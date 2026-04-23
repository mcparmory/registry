"""
Pagerduty MCP Server - Pydantic Models

Generated: 2026-04-23 21:34:30 UTC
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
    "AssociateServiceToIncidentWorkflowTriggerRequest",
    "CancelIncidentResponderRequest",
    "CreateAutomationActionInvocationRequest",
    "CreateAutomationActionRequest",
    "CreateAutomationActionServiceAssocationRequest",
    "CreateAutomationActionsRunnerRequest",
    "CreateAutomationActionsRunnerTeamAssociationRequest",
    "CreateAutomationActionTeamAssociationRequest",
    "CreateBusinessServiceAccountSubscriptionRequest",
    "CreateBusinessServiceNotificationSubscribersRequest",
    "CreateBusinessServiceRequest",
    "CreateCacheVarOnGlobalOrchRequest",
    "CreateCacheVarOnServiceOrchRequest",
    "CreateChangeEventRequest",
    "CreateCustomShiftsRequest",
    "CreateEntityTypeByIdChangeTagsRequest",
    "CreateEscalationPolicyRequest",
    "CreateEventRequest",
    "CreateExtensionRequest",
    "CreateIncidentNoteRequest",
    "CreateIncidentNotificationSubscribersRequest",
    "CreateIncidentRequest",
    "CreateIncidentResponderRequest",
    "CreateIncidentSnoozeRequest",
    "CreateIncidentStatusUpdateRequest",
    "CreateIncidentTypeCustomFieldFieldOptionsRequest",
    "CreateIncidentTypeCustomFieldRequest",
    "CreateIncidentTypeRequest",
    "CreateIncidentWorkflowInstanceRequest",
    "CreateMaintenanceWindowRequest",
    "CreateOverridesRequest",
    "CreateRotationRequest",
    "CreateSchedulePreviewRequest",
    "CreateScheduleV3Request",
    "CreateServiceCustomFieldOptionRequest",
    "CreateServiceDependencyRequest",
    "CreateServiceIntegrationRequest",
    "CreateServiceRequest",
    "CreateStatusPagePostmortemRequest",
    "CreateStatusPagePostRequest",
    "CreateStatusPagePostUpdateRequest",
    "CreateStatusPageSubscriptionRequest",
    "CreateTagsRequest",
    "CreateTeamRequest",
    "CreateTemplateRequest",
    "CreateUserContactMethodRequest",
    "CreateUserNotificationSubscriptionsRequest",
    "CreateUserRequest",
    "CreateWorkflowIntegrationConnectionRequest",
    "DeleteAutomationActionRequest",
    "DeleteAutomationActionServiceAssociationRequest",
    "DeleteAutomationActionsRunnerRequest",
    "DeleteAutomationActionsRunnerTeamAssociationRequest",
    "DeleteAutomationActionTeamAssociationRequest",
    "DeleteBusinessServiceRequest",
    "DeleteCacheVarOnGlobalOrchRequest",
    "DeleteCacheVarOnServiceOrchRequest",
    "DeleteCustomShiftRequest",
    "DeleteEscalationPolicyRequest",
    "DeleteEventRequest",
    "DeleteExtensionRequest",
    "DeleteExternalDataCacheVarDataOnGlobalOrchRequest",
    "DeleteExternalDataCacheVarDataOnServiceOrchRequest",
    "DeleteIncidentNoteRequest",
    "DeleteIncidentTypeCustomFieldFieldOptionRequest",
    "DeleteIncidentTypeCustomFieldRequest",
    "DeleteIncidentWorkflowRequest",
    "DeleteIncidentWorkflowTriggerRequest",
    "DeleteMaintenanceWindowRequest",
    "DeleteOauthDelegationsRequest",
    "DeleteOrchestrationIntegrationRequest",
    "DeleteOrchestrationRequest",
    "DeleteOverrideRequest",
    "DeleteRotationRequest",
    "DeleteRulesetEventRuleRequest",
    "DeleteScheduleV3Request",
    "DeleteServiceCustomFieldOptionRequest",
    "DeleteServiceCustomFieldRequest",
    "DeleteServiceDependencyRequest",
    "DeleteServiceEventRuleRequest",
    "DeleteServiceFromIncidentWorkflowTriggerRequest",
    "DeleteServiceRequest",
    "DeleteSreMemoryRequest",
    "DeleteStatusPagePostmortemRequest",
    "DeleteStatusPagePostRequest",
    "DeleteStatusPagePostUpdateRequest",
    "DeleteStatusPageSubscriptionRequest",
    "DeleteTagRequest",
    "DeleteTeamEscalationPolicyRequest",
    "DeleteTeamRequest",
    "DeleteTeamUserRequest",
    "DeleteTemplateRequest",
    "DeleteUserContactMethodRequest",
    "DeleteUserHandoffNotificationRuleRequest",
    "DeleteUserNotificationRuleRequest",
    "DeleteUserRequest",
    "DeleteUserStatusUpdateNotificationRuleRequest",
    "DeleteWorkflowIntegrationConnectionRequest",
    "EnableExtensionRequest",
    "EnableWebhookSubscriptionRequest",
    "GetAbilityRequest",
    "GetAddonRequest",
    "GetAlertGroupingSettingRequest",
    "GetAllAutomationActionsRequest",
    "GetAnalyticsIncidentResponsesByIdRequest",
    "GetAnalyticsIncidentsByIdRequest",
    "GetAnalyticsIncidentsRequest",
    "GetAnalyticsMetricsIncidentsAllRequest",
    "GetAnalyticsMetricsIncidentsEscalationPolicyAllRequest",
    "GetAnalyticsMetricsIncidentsEscalationPolicyRequest",
    "GetAnalyticsMetricsIncidentsServiceAllRequest",
    "GetAnalyticsMetricsIncidentsServiceRequest",
    "GetAnalyticsMetricsIncidentsTeamAllRequest",
    "GetAnalyticsMetricsIncidentsTeamRequest",
    "GetAnalyticsMetricsPdAdvanceUsageFeaturesRequest",
    "GetAnalyticsMetricsRespondersAllRequest",
    "GetAnalyticsMetricsRespondersTeamRequest",
    "GetAnalyticsMetricsUsersAllRequest",
    "GetAnalyticsResponderIncidentsRequest",
    "GetAnalyticsUsersRequest",
    "GetAutomationActionRequest",
    "GetAutomationActionsActionServiceAssociationRequest",
    "GetAutomationActionsActionServiceAssociationsRequest",
    "GetAutomationActionsActionTeamAssociationRequest",
    "GetAutomationActionsActionTeamAssociationsRequest",
    "GetAutomationActionsInvocationRequest",
    "GetAutomationActionsRunnerRequest",
    "GetAutomationActionsRunnersRequest",
    "GetAutomationActionsRunnerTeamAssociationRequest",
    "GetAutomationActionsRunnerTeamAssociationsRequest",
    "GetBusinessServiceImpactsRequest",
    "GetBusinessServicePriorityThresholdsRequest",
    "GetBusinessServiceRequest",
    "GetBusinessServiceServiceDependenciesRequest",
    "GetBusinessServiceSubscribersRequest",
    "GetBusinessServiceSupportingServiceImpactsRequest",
    "GetBusinessServiceTopLevelImpactorsRequest",
    "GetCacheVarOnGlobalOrchRequest",
    "GetCacheVarOnServiceOrchRequest",
    "GetChangeEventRequest",
    "GetCurrentUserRequest",
    "GetCustomShiftRequest",
    "GetEntityTypeByIdTagsRequest",
    "GetEscalationPolicyRequest",
    "GetEventRequest",
    "GetExtensionRequest",
    "GetExtensionSchemaRequest",
    "GetExternalDataCacheVarDataOnGlobalOrchRequest",
    "GetExternalDataCacheVarDataOnServiceOrchRequest",
    "GetIncidentAlertRequest",
    "GetIncidentFieldValuesRequest",
    "GetIncidentImpactedBusinessServicesRequest",
    "GetIncidentNotificationSubscribersRequest",
    "GetIncidentRequest",
    "GetIncidentTypeCustomFieldFieldOptionsRequest",
    "GetIncidentTypeCustomFieldRequest",
    "GetIncidentTypeRequest",
    "GetIncidentWorkflowActionRequest",
    "GetLogEntryRequest",
    "GetMaintenanceWindowRequest",
    "GetOrchActiveStatusRequest",
    "GetOrchestrationIntegrationRequest",
    "GetOrchestrationRequest",
    "GetOrchPathGlobalRequest",
    "GetOrchPathRouterRequest",
    "GetOrchPathServiceRequest",
    "GetOrchPathUnroutedRequest",
    "GetOutlierIncidentRequest",
    "GetOverrideRequest",
    "GetPastIncidentsRequest",
    "GetPausedIncidentReportAlertsRequest",
    "GetPausedIncidentReportCountsRequest",
    "GetPostmortemRequest",
    "GetPostUpdateRequest",
    "GetRelatedIncidentsRequest",
    "GetRotationRequest",
    "GetScheduleV3Request",
    "GetServiceCustomFieldOptionRequest",
    "GetServiceCustomFieldRequest",
    "GetServiceCustomFieldValuesRequest",
    "GetServiceIntegrationRequest",
    "GetServiceRequest",
    "GetStatusDashboardByIdRequest",
    "GetStatusDashboardByUrlSlugRequest",
    "GetStatusDashboardServiceImpactsByIdRequest",
    "GetStatusDashboardServiceImpactsByUrlSlugRequest",
    "GetStatusPageImpactRequest",
    "GetStatusPagePostRequest",
    "GetStatusPageServiceRequest",
    "GetStatusPageSeverityRequest",
    "GetStatusPageStatusRequest",
    "GetStatusPageSubscriptionRequest",
    "GetTagRequest",
    "GetTagsByEntityTypeRequest",
    "GetTeamNotificationSubscriptionsRequest",
    "GetTeamRequest",
    "GetTechnicalServiceServiceDependenciesRequest",
    "GetTemplateFieldsRequest",
    "GetTemplateRequest",
    "GetTemplatesRequest",
    "GetUserContactMethodRequest",
    "GetUserContactMethodsRequest",
    "GetUserDelegationRequest",
    "GetUserHandoffNotifiactionRuleRequest",
    "GetUserLicenseRequest",
    "GetUserNotificationRuleRequest",
    "GetUserNotificationRulesRequest",
    "GetUserNotificationSubscriptionsRequest",
    "GetUserRequest",
    "GetVendorRequest",
    "GetWebhookSubscriptionRequest",
    "GetWorkflowIntegrationConnectionRequest",
    "GetWorkflowIntegrationRequest",
    "ListAbilitiesRequest",
    "ListAuditRecordsRequest",
    "ListAutomationActionInvocationsRequest",
    "ListBusinessServicesRequest",
    "ListCacheVarOnGlobalOrchRequest",
    "ListCacheVarOnServiceOrchRequest",
    "ListChangeEventsRequest",
    "ListCustomShiftsRequest",
    "ListEscalationPoliciesRequest",
    "ListEscalationPolicyAuditRecordsRequest",
    "ListEventOrchestrationFeatureEnablementsRequest",
    "ListEventOrchestrationsRequest",
    "ListEventsRequest",
    "ListExtensionSchemasRequest",
    "ListExtensionsRequest",
    "ListIncidentAlertsRequest",
    "ListIncidentLogEntriesRequest",
    "ListIncidentNotesRequest",
    "ListIncidentRelatedChangeEventsRequest",
    "ListIncidentsRequest",
    "ListIncidentTypeCustomFieldRequest",
    "ListIncidentTypeCustomFieldsRequest",
    "ListIncidentTypesRequest",
    "ListIncidentWorkflowActionsRequest",
    "ListIncidentWorkflowTriggersRequest",
    "ListLicenseAllocationsRequest",
    "ListLicensesRequest",
    "ListLogEntriesRequest",
    "ListMaintenanceWindowsRequest",
    "ListNotificationsRequest",
    "ListOnCallsRequest",
    "ListOrchestrationIntegrationsRequest",
    "ListOverridesRequest",
    "ListPrioritiesRequest",
    "ListResourceStandardsManyServicesRequest",
    "ListResourceStandardsRequest",
    "ListRotationsRequest",
    "ListSchedulesAuditRecordsRequest",
    "ListSchedulesV3Request",
    "ListScheduleUsersRequest",
    "ListServiceAuditRecordsRequest",
    "ListServiceChangeEventsRequest",
    "ListServiceCustomFieldOptionsRequest",
    "ListServiceCustomFieldsRequest",
    "ListServiceEventRulesRequest",
    "ListServiceFeatureEnablementsRequest",
    "ListServicesRequest",
    "ListSreMemoriesRequest",
    "ListStandardsRequest",
    "ListStatusDashboardsRequest",
    "ListStatusPageImpactsRequest",
    "ListStatusPagePostsRequest",
    "ListStatusPagePostUpdatesRequest",
    "ListStatusPageServicesRequest",
    "ListStatusPageSeveritiesRequest",
    "ListStatusPagesRequest",
    "ListStatusPageStatusesRequest",
    "ListStatusPageSubscriptionsRequest",
    "ListTagsRequest",
    "ListTeamsAuditRecordsRequest",
    "ListTeamsRequest",
    "ListTeamUsersRequest",
    "ListUserDelegationsRequest",
    "ListUsersAuditRecordsRequest",
    "ListUsersRequest",
    "ListVendorsRequest",
    "ListWebhookSubscriptionsRequest",
    "ListWorkflowIntegrationConnectionsByIntegrationRequest",
    "ListWorkflowIntegrationConnectionsRequest",
    "ListWorkflowIntegrationsRequest",
    "MergeIncidentsRequest",
    "MigrateOrchestrationIntegrationRequest",
    "PostOrchestrationIntegrationRequest",
    "PostOrchestrationRequest",
    "PutIncidentManualBusinessServiceAssociationRequest",
    "RemoveBusinessServiceAccountSubscriptionRequest",
    "RemoveBusinessServiceNotificationSubscriberRequest",
    "RemoveIncidentNotificationSubscribersRequest",
    "RemoveTeamNotificationSubscriptionsRequest",
    "RenderTemplateRequest",
    "SetIncidentFieldValuesRequest",
    "TestWebhookSubscriptionRequest",
    "UnsubscribeUserNotificationSubscriptionsRequest",
    "UpdateAutomationActionRequest",
    "UpdateAutomationActionsRunnerRequest",
    "UpdateBusinessServiceRequest",
    "UpdateCacheVarOnGlobalOrchRequest",
    "UpdateCacheVarOnServiceOrchRequest",
    "UpdateChangeEventRequest",
    "UpdateCustomShiftRequest",
    "UpdateEscalationPolicyRequest",
    "UpdateEventOrchestrationFeatureEnablementsRequest",
    "UpdateEventRequest",
    "UpdateExtensionRequest",
    "UpdateExternalDataCacheVarDataOnGlobalOrchRequest",
    "UpdateExternalDataCacheVarDataOnServiceOrchRequest",
    "UpdateIncidentAlertRequest",
    "UpdateIncidentAlertsRequest",
    "UpdateIncidentNoteRequest",
    "UpdateIncidentRequest",
    "UpdateIncidentsRequest",
    "UpdateIncidentTypeCustomFieldFieldOptionRequest",
    "UpdateIncidentTypeCustomFieldRequest",
    "UpdateIncidentTypeRequest",
    "UpdateLogEntryChannelRequest",
    "UpdateMaintenanceWindowRequest",
    "UpdateOrchActiveStatusRequest",
    "UpdateOrchestrationIntegrationRequest",
    "UpdateOverrideRequest",
    "UpdateScheduleV3Request",
    "UpdateServiceCustomFieldRequest",
    "UpdateServiceCustomFieldValuesRequest",
    "UpdateServiceFeatureEnablementRequest",
    "UpdateServiceIntegrationRequest",
    "UpdateServiceRequest",
    "UpdateSreMemoryRequest",
    "UpdateStandardRequest",
    "UpdateStatusPagePostmortemRequest",
    "UpdateStatusPagePostRequest",
    "UpdateStatusPagePostUpdateRequest",
    "UpdateTeamEscalationPolicyRequest",
    "UpdateTeamRequest",
    "UpdateTeamUserRequest",
    "UpdateTemplateRequest",
    "UpdateUserContactMethodRequest",
    "UpdateUserNotificationRuleRequest",
    "UpdateUserRequest",
    "UpdateWebhookSubscriptionRequest",
    "UpdateWorkflowIntegrationConnectionRequest",
    "AlertUpdate",
    "AutomationActionsProcessAutomationJobActionPostBody",
    "AutomationActionsProcessAutomationJobActionPutBody",
    "AutomationActionsRunnerRunbookBody",
    "AutomationActionsRunnerRunbookPostBody",
    "AutomationActionsRunnerSidecarBody",
    "AutomationActionsRunnerSidecarPostBody",
    "AutomationActionsScriptActionPostBody",
    "AutomationActionsScriptActionPutBody",
    "CancelIncidentResponderRequestBodyResponderRequestTargetsItem",
    "ChangeEvent",
    "CreateCustomShiftsBodyCustomShiftsItem",
    "CreateEntityTypeByIdChangeTagsBodyAddItem",
    "CreateEntityTypeByIdChangeTagsBodyRemoveItem",
    "CreateIncidentBodyIncidentAssignmentsItem",
    "CreateOverridesBodyOverridesItem",
    "CreateScheduleV3BodyScheduleTeamsItem",
    "CreateServiceDependencyBodyRelationshipsItem",
    "CreateStatusPagePostUpdateBodyPostUpdateImpactedServicesItem",
    "CreateUserBodyUser",
    "CreateWorkflowIntegrationConnectionBodyAppsItem",
    "CreateWorkflowIntegrationConnectionBodyTeamsItem",
    "CustomFieldsEditableFieldValue",
    "CustomFieldsFieldOption",
    "DeleteServiceDependencyBodyRelationshipsItem",
    "EmailContactMethod",
    "EscalationPolicy",
    "EscalationPolicyReference",
    "Extension",
    "IncidentReference",
    "Integration",
    "MaintenanceWindow",
    "NotificationRule",
    "NotificationSubscribable",
    "NotificationSubscriber",
    "OrchestrationCacheVariableExternalData",
    "OrchestrationCacheVariableRecentValue",
    "OrchestrationCacheVariableTriggerEventCount",
    "PhoneContactMethod",
    "PriorityReference",
    "PushContactMethod",
    "Schedule",
    "Service",
    "ServiceCustomFieldsFieldValueUpdateModel",
    "ServiceReference",
    "ShiftMember",
    "StatusPagePostUpdateRequest",
    "StatusUpdateTemplateInput",
    "Tag",
    "Team",
    "TeamReference",
    "UpdateCustomShiftBodyCustomShiftAssignmentsItem",
    "UpdateIncidentBodyIncidentAssignmentsItem",
    "UpdateIncidentBodyIncidentPriority",
    "UpdateIncidentsBodyIncidentsItem",
    "UpdateServiceCustomFieldBodyFieldFieldOptionsItem",
    "UpdateStandardBody",
    "UpdateStatusPagePostUpdateBodyPostUpdateImpactedServicesItem",
    "UpdateUserBodyUser",
    "UpdateWorkflowIntegrationConnectionBodyAppsItem",
    "UpdateWorkflowIntegrationConnectionBodyTeamsItem",
    "WhatsAppContactMethod",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: add_and_remove_tags_for_entity
class CreateEntityTypeByIdChangeTagsRequestPath(StrictModel):
    entity_type: Literal["users", "teams", "escalation_policies"] = Field(default=..., description="The type of entity to tag: users, teams, or escalation policies.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the entity to modify tags for.")
class CreateEntityTypeByIdChangeTagsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API version header. Use the default value for PagerDuty API v2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be application/json.")
class CreateEntityTypeByIdChangeTagsRequestBody(StrictModel):
    add: list[CreateEntityTypeByIdChangeTagsBodyAddItem] | None = Field(default=None, description="Array of tags to add to the entity. Each item can be a tag reference (using an existing tag's ID) or a new tag definition (by label). If a label matches an existing tag, that tag is added; otherwise, a new tag is created if you have permission.")
    remove: list[CreateEntityTypeByIdChangeTagsBodyRemoveItem] | None = Field(default=None, description="Array of tag references (by ID) to remove from the entity.")
class CreateEntityTypeByIdChangeTagsRequest(StrictModel):
    """Add or remove tags from a user, team, or escalation policy. Tags can be existing tags or newly created ones, and are used to organize and filter entities."""
    path: CreateEntityTypeByIdChangeTagsRequestPath
    header: CreateEntityTypeByIdChangeTagsRequestHeader
    body: CreateEntityTypeByIdChangeTagsRequestBody | None = None

# Operation: list_tags_for_entity
class GetEntityTypeByIdTagsRequestPath(StrictModel):
    entity_type: Literal["users", "teams", "escalation_policies"] = Field(default=..., description="The type of entity to retrieve tags for. Must be one of: users, teams, or escalation_policies.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the entity (user, team, or escalation policy) to retrieve tags for.")
class GetEntityTypeByIdTagsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Defaults to application/vnd.pagerduty+json;version=2 to specify the response format and API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type for the request body. Must be application/json.")
class GetEntityTypeByIdTagsRequest(StrictModel):
    """Retrieve all tags associated with a specific user, team, or escalation policy. Tags are used to organize and filter these entities within PagerDuty."""
    path: GetEntityTypeByIdTagsRequestPath
    header: GetEntityTypeByIdTagsRequestHeader

# Operation: list_abilities
class ListAbilitiesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to the PagerDuty JSON API version 2 format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request content type. Must be application/json.")
class ListAbilitiesRequest(StrictModel):
    """Retrieve all capabilities available to your account based on your pricing plan and account state. Abilities are feature names (e.g., 'teams') that indicate what functionality your account can access."""
    header: ListAbilitiesRequestHeader

# Operation: check_account_ability
class GetAbilityRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the ability to check (e.g., 'teams'). This determines which account capability is being tested.")
class GetAbilityRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default value to request the current API version (version 2).")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request. Must be set to application/json.")
class GetAbilityRequest(StrictModel):
    """Check whether your account has a specific capability or feature enabled. Abilities represent account features (such as 'teams') that may be available based on your pricing plan or account state."""
    path: GetAbilityRequestPath
    header: GetAbilityRequestHeader

# Operation: get_addon
class GetAddonRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Add-on to retrieve.")
class GetAddonRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request content type as JSON.")
class GetAddonRequest(StrictModel):
    """Retrieve details about a specific Add-on, which is a piece of functionality that extends PagerDuty's UI with custom features."""
    path: GetAddonRequestPath
    header: GetAddonRequestHeader

# Operation: get_alert_grouping_setting
class GetAlertGroupingSettingRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Alert Grouping Setting to retrieve.")
class GetAlertGroupingSettingRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty JSON API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to application/json.")
class GetAlertGroupingSettingRequest(StrictModel):
    """Retrieve a specific Alert Grouping Setting by ID. Alert Grouping Settings define the configurations used by the Alert Grouper service to organize and group alerts."""
    path: GetAlertGroupingSettingRequestPath
    header: GetAlertGroupingSettingRequestHeader

# Operation: get_incident_analytics_aggregated
class GetAnalyticsMetricsIncidentsAllRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be application/json.")
class GetAnalyticsMetricsIncidentsAllRequestBodyFilters(StrictModel):
    created_at_start: str | None = Field(default=None, validation_alias="created_at_start", serialization_alias="created_at_start", description="ISO 8601 datetime string marking the start of the query window (inclusive). Incidents created before this time are excluded. Maximum supported time range is one year when used with created_at_end.")
    created_at_end: str | None = Field(default=None, validation_alias="created_at_end", serialization_alias="created_at_end", description="ISO 8601 datetime string marking the end of the query window (exclusive). Incidents created at or after this time are excluded. Maximum supported time range is one year when used with created_at_start.")
    urgency: Literal["high", "low"] | None = Field(default=None, validation_alias="urgency", serialization_alias="urgency", description="Filter results to incidents matching a specific urgency level: high or low. Omit to include all urgency levels.")
    major: bool | None = Field(default=None, validation_alias="major", serialization_alias="major", description="Filter to include only major incidents (true), exclude major incidents (false), or include all incidents (omit parameter). Major incidents are those flagged in operational reviews.")
    min_ackowledgements: int | None = Field(default=None, validation_alias="min_ackowledgements", serialization_alias="min_ackowledgements", description="Minimum number of acknowledgements required. Only incidents with at least this many acknowledgements are included. Omit to include all incidents regardless of acknowledgement count.")
    min_timeout_escalations: int | None = Field(default=None, validation_alias="min_timeout_escalations", serialization_alias="min_timeout_escalations", description="Minimum number of timeout escalations required. Only incidents with at least this many timeout escalations are included. Omit to include all incidents regardless of timeout escalation count.")
    min_manual_escalations: int | None = Field(default=None, validation_alias="min_manual_escalations", serialization_alias="min_manual_escalations", description="Minimum number of manual escalations required. Only incidents with at least this many manual escalations are included. Omit to include all incidents regardless of manual escalation count.")
    team_ids: list[str] | None = Field(default=None, validation_alias="team_ids", serialization_alias="team_ids", description="Array of team IDs to filter results. Only incidents associated with these teams are included. Required for user-level API keys or OAuth-generated keys; optional for account-level keys. Omit to include all accessible teams.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="Array of service IDs to filter results. Only incidents associated with these services are included. Required for user-level API keys or OAuth-generated keys; optional for account-level keys. Omit to include all accessible services.")
    escalation_policy_ids: list[str] | None = Field(default=None, validation_alias="escalation_policy_ids", serialization_alias="escalation_policy_ids", description="Array of escalation policy IDs to filter results. Only incidents associated with these escalation policies are included. Omit to include all accessible escalation policies.")
class GetAnalyticsMetricsIncidentsAllRequestBody(StrictModel):
    """Parameters and filters to apply to the dataset."""
    time_zone: str | None = Field(default=None, description="Time zone for result grouping and display, specified in tzdata format (e.g., America/New_York, Europe/London, Etc/UTC). Defaults to UTC if omitted.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for results: asc for ascending or desc for descending. Used in conjunction with order_by parameter.")
    order_by: str | None = Field(default=None, description="Column name to sort results by (e.g., created_at). Used in conjunction with order parameter.")
    aggregate_unit: Literal["day", "week", "month"] | None = Field(default=None, description="Time unit for aggregating metrics: day, week, or month. Omit to aggregate metrics across the entire queried period without time-based grouping.")
    filters: GetAnalyticsMetricsIncidentsAllRequestBodyFilters | None = None
class GetAnalyticsMetricsIncidentsAllRequest(StrictModel):
    """Retrieve aggregated incident metrics with optional time-based grouping (daily, weekly, monthly). Metrics are enriched and can be filtered by date range, urgency, team, service, and escalation characteristics. Note: Analytics data updates periodically with up to 24-hour latency for new incidents."""
    header: GetAnalyticsMetricsIncidentsAllRequestHeader
    body: GetAnalyticsMetricsIncidentsAllRequestBody | None = None

# Operation: get_escalation_policy_incident_metrics
class GetAnalyticsMetricsIncidentsEscalationPolicyRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header specifying the response format and version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request body content type; must be JSON.")
class GetAnalyticsMetricsIncidentsEscalationPolicyRequestBodyFilters(StrictModel):
    created_at_start: str | None = Field(default=None, validation_alias="created_at_start", serialization_alias="created_at_start", description="Filter incidents by creation date (inclusive start). Accepts ISO 8601 datetime format. Combined with created_at_end, the maximum supported range is one year.")
    created_at_end: str | None = Field(default=None, validation_alias="created_at_end", serialization_alias="created_at_end", description="Filter incidents by creation date (exclusive end). Accepts ISO 8601 datetime format. Combined with created_at_start, the maximum supported range is one year.")
    urgency: Literal["high", "low"] | None = Field(default=None, validation_alias="urgency", serialization_alias="urgency", description="Filter incidents by urgency level. Specify 'high' or 'low' to include only incidents matching that urgency.")
    major: bool | None = Field(default=None, validation_alias="major", serialization_alias="major", description="Filter to include only major incidents (true), exclude major incidents (false), or include all incidents (omit parameter).")
    min_ackowledgements: int | None = Field(default=None, validation_alias="min_ackowledgements", serialization_alias="min_ackowledgements", description="Filter to include only incidents with at least the specified number of acknowledgements. Omit to include all incidents regardless of acknowledgement count.")
    min_timeout_escalations: int | None = Field(default=None, validation_alias="min_timeout_escalations", serialization_alias="min_timeout_escalations", description="Filter to include only incidents with at least the specified number of timeout-triggered escalations. Omit to include all incidents regardless of timeout escalation count.")
    min_manual_escalations: int | None = Field(default=None, validation_alias="min_manual_escalations", serialization_alias="min_manual_escalations", description="Filter to include only incidents with at least the specified number of manually-triggered escalations. Omit to include all incidents regardless of manual escalation count.")
    team_ids: list[str] | None = Field(default=None, validation_alias="team_ids", serialization_alias="team_ids", description="Restrict results to incidents associated with specific teams. Provide an array of team IDs. Omit to include all teams accessible to the requestor.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="Restrict results to incidents associated with specific services. Provide an array of service IDs. Omit to include all services accessible to the requestor.")
    escalation_policy_ids: list[str] | None = Field(default=None, validation_alias="escalation_policy_ids", serialization_alias="escalation_policy_ids", description="Restrict results to specific escalation policies. Provide an array of escalation policy IDs. Omit to include all escalation policies accessible to the requestor.")
class GetAnalyticsMetricsIncidentsEscalationPolicyRequestBody(StrictModel):
    """Parameters and filters to apply to the dataset."""
    time_zone: str | None = Field(default=None, description="Time zone for result grouping and display. Must be in tzdata format (e.g., 'America/New_York', 'Etc/UTC'). Defaults to UTC if omitted.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results: 'asc' for ascending or 'desc' for descending. Use with order_by to specify the sort column.")
    order_by: str | None = Field(default=None, description="Column name to sort results by (e.g., 'created_at'). Use with order to specify ascending or descending direction.")
    aggregate_unit: Literal["day", "week", "month"] | None = Field(default=None, description="Time unit for aggregating metrics: 'day', 'week', or 'month'. Omit to aggregate metrics across the entire specified period without time-based grouping.")
    filters: GetAnalyticsMetricsIncidentsEscalationPolicyRequestBodyFilters | None = None
class GetAnalyticsMetricsIncidentsEscalationPolicyRequest(StrictModel):
    """Retrieve aggregated incident metrics grouped by escalation policy over a specified time period. Returns metrics such as resolution time, engagement time, and sleep interruptions to analyze escalation policy performance."""
    header: GetAnalyticsMetricsIncidentsEscalationPolicyRequestHeader
    body: GetAnalyticsMetricsIncidentsEscalationPolicyRequestBody | None = None

# Operation: get_escalation_policy_incident_metrics_aggregated
class GetAnalyticsMetricsIncidentsEscalationPolicyAllRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header; must be set to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type; must be application/json.")
class GetAnalyticsMetricsIncidentsEscalationPolicyAllRequestBodyFilters(StrictModel):
    created_at_start: str | None = Field(default=None, validation_alias="created_at_start", serialization_alias="created_at_start", description="Filter results to incidents created on or after this ISO 8601 datetime. When combined with created_at_end, the maximum supported time range is one year.")
    created_at_end: str | None = Field(default=None, validation_alias="created_at_end", serialization_alias="created_at_end", description="Filter results to incidents created before this ISO 8601 datetime. When combined with created_at_start, the maximum supported time range is one year.")
    urgency: Literal["high", "low"] | None = Field(default=None, validation_alias="urgency", serialization_alias="urgency", description="Filter results by incident urgency; use 'high' for high-urgency incidents or 'low' for low-urgency incidents. Omit to include all urgency levels.")
    major: bool | None = Field(default=None, validation_alias="major", serialization_alias="major", description="Filter to include only major incidents (true), exclude major incidents (false), or include all incidents (omit parameter).")
    min_ackowledgements: int | None = Field(default=None, validation_alias="min_ackowledgements", serialization_alias="min_ackowledgements", description="Filter to incidents with at least this many acknowledgements. For example, set to 1 to return only acknowledged incidents. Omit to include all incidents regardless of acknowledgement count.")
    min_timeout_escalations: int | None = Field(default=None, validation_alias="min_timeout_escalations", serialization_alias="min_timeout_escalations", description="Filter to incidents with at least this many timeout-triggered escalations. For example, set to 1 to return only incidents that escalated due to timeout. Omit to include all incidents regardless of timeout escalation count.")
    min_manual_escalations: int | None = Field(default=None, validation_alias="min_manual_escalations", serialization_alias="min_manual_escalations", description="Filter to incidents with at least this many manual escalations. For example, set to 1 to return only manually escalated incidents. Omit to include all incidents regardless of manual escalation count.")
    team_ids: list[str] | None = Field(default=None, validation_alias="team_ids", serialization_alias="team_ids", description="Comma-separated list of team IDs to include in results. Only incidents assigned to these teams will be returned. Omit to include all teams the requestor has access to.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="Comma-separated list of service IDs to include in results. Only incidents related to these services will be returned. Omit to include all services the requestor has access to.")
    escalation_policy_ids: list[str] | None = Field(default=None, validation_alias="escalation_policy_ids", serialization_alias="escalation_policy_ids", description="Comma-separated list of escalation policy IDs to include in results. Only incidents using these escalation policies will be returned. Omit to include all escalation policies the requestor has access to.")
class GetAnalyticsMetricsIncidentsEscalationPolicyAllRequestBody(StrictModel):
    """Parameters and filters to apply to the dataset."""
    time_zone: str | None = Field(default=None, description="Time zone for result timestamps and metric aggregation grouping; must be in IANA tzdata format (e.g., 'America/New_York', 'Etc/UTC'). Defaults to UTC if omitted.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results: 'asc' for ascending or 'desc' for descending. Use with order_by to specify the sort column.")
    order_by: str | None = Field(default=None, description="Column name to sort results by (e.g., 'created_at'). Use with order to specify ascending or descending direction.")
    aggregate_unit: Literal["day", "week", "month"] | None = Field(default=None, description="Time unit for metric aggregation: 'day', 'week', or 'month'. Omit to aggregate metrics across the entire requested period without time-based grouping.")
    filters: GetAnalyticsMetricsIncidentsEscalationPolicyAllRequestBodyFilters | None = None
class GetAnalyticsMetricsIncidentsEscalationPolicyAllRequest(StrictModel):
    """Retrieve aggregated incident metrics across all escalation policies, including resolution time, engagement time, and sleep interruptions. Supports filtering by date range, urgency, teams, services, and escalation policies, with optional time-based aggregation."""
    header: GetAnalyticsMetricsIncidentsEscalationPolicyAllRequestHeader
    body: GetAnalyticsMetricsIncidentsEscalationPolicyAllRequestBody | None = None

# Operation: get_service_incident_analytics
class GetAnalyticsMetricsIncidentsServiceRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header; use application/vnd.pagerduty+json;version=2 for this operation.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request body content type; must be application/json.")
class GetAnalyticsMetricsIncidentsServiceRequestBodyFilters(StrictModel):
    created_at_start: str | None = Field(default=None, validation_alias="created_at_start", serialization_alias="created_at_start", description="Filter results to incidents created on or after this ISO 8601 datetime. Combined with created_at_end, the maximum supported time range is one year.")
    created_at_end: str | None = Field(default=None, validation_alias="created_at_end", serialization_alias="created_at_end", description="Filter results to incidents created before this ISO 8601 datetime. Combined with created_at_start, the maximum supported time range is one year.")
    urgency: Literal["high", "low"] | None = Field(default=None, validation_alias="urgency", serialization_alias="urgency", description="Filter results by incident urgency level: either 'high' or 'low'. Omit to include all urgency levels.")
    major: bool | None = Field(default=None, validation_alias="major", serialization_alias="major", description="Filter to include only major incidents (true), exclude major incidents (false), or include all incidents (omit parameter).")
    min_ackowledgements: int | None = Field(default=None, validation_alias="min_ackowledgements", serialization_alias="min_ackowledgements", description="Filter to incidents with at least this many acknowledgements. Omit to include incidents regardless of acknowledgement count.")
    min_timeout_escalations: int | None = Field(default=None, validation_alias="min_timeout_escalations", serialization_alias="min_timeout_escalations", description="Filter to incidents with at least this many timeout escalations. Omit to include incidents regardless of timeout escalation count.")
    min_manual_escalations: int | None = Field(default=None, validation_alias="min_manual_escalations", serialization_alias="min_manual_escalations", description="Filter to incidents with at least this many manual escalations. Omit to include incidents regardless of manual escalation count.")
    team_ids: list[str] | None = Field(default=None, validation_alias="team_ids", serialization_alias="team_ids", description="Restrict results to incidents associated with these team IDs. Provide as an array of team identifiers. Omit to include all teams you have access to.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="Restrict results to incidents associated with these service IDs. Provide as an array of service identifiers. Omit to include all services you have access to.")
    escalation_policy_ids: list[str] | None = Field(default=None, validation_alias="escalation_policy_ids", serialization_alias="escalation_policy_ids", description="Restrict results to incidents associated with these escalation policy IDs. Provide as an array of escalation policy identifiers. Omit to include all escalation policies you have access to.")
class GetAnalyticsMetricsIncidentsServiceRequestBody(StrictModel):
    """Parameters and filters to apply to the dataset."""
    time_zone: str | None = Field(default=None, description="Time zone for aggregating and displaying results; must be in tzdata format (e.g., 'America/New_York', 'Etc/UTC'). Defaults to UTC if omitted.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results: 'asc' for ascending or 'desc' for descending. Use with order_by to specify the sort column.")
    order_by: str | None = Field(default=None, description="Column name to sort results by (e.g., 'created_at'). Use with order to specify ascending or descending direction.")
    aggregate_unit: Literal["day", "week", "month"] | None = Field(default=None, description="Time unit for aggregating metrics: 'day', 'week', or 'month'. Omit to aggregate metrics across the entire specified period without time-based grouping.")
    filters: GetAnalyticsMetricsIncidentsServiceRequestBodyFilters | None = None
class GetAnalyticsMetricsIncidentsServiceRequest(StrictModel):
    """Retrieve aggregated incident metrics by service over a specified time period. Metrics include resolution time, engagement time, and sleep interruptions, with optional grouping by day, week, or month."""
    header: GetAnalyticsMetricsIncidentsServiceRequestHeader
    body: GetAnalyticsMetricsIncidentsServiceRequestBody | None = None

# Operation: get_aggregated_incident_metrics_across_services
class GetAnalyticsMetricsIncidentsServiceAllRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to ensure compatibility with this endpoint.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request body content type. Must be application/json.")
class GetAnalyticsMetricsIncidentsServiceAllRequestBodyFilters(StrictModel):
    created_at_start: str | None = Field(default=None, validation_alias="created_at_start", serialization_alias="created_at_start", description="Filter results to incidents created on or after this date and time. Accepts ISO 8601 format. Maximum supported time range is one year when used with created_at_end.")
    created_at_end: str | None = Field(default=None, validation_alias="created_at_end", serialization_alias="created_at_end", description="Filter results to incidents created before this date and time. Accepts ISO 8601 format. Maximum supported time range is one year when used with created_at_start.")
    urgency: Literal["high", "low"] | None = Field(default=None, validation_alias="urgency", serialization_alias="urgency", description="Filter results by incident urgency level. Use 'high' for high-urgency incidents or 'low' for low-urgency incidents. Omit to include all urgency levels.")
    major: bool | None = Field(default=None, validation_alias="major", serialization_alias="major", description="Filter to include only major incidents (true) or exclude major incidents (false). Omit to include all incidents regardless of major status.")
    min_ackowledgements: int | None = Field(default=None, validation_alias="min_ackowledgements", serialization_alias="min_ackowledgements", description="Filter to incidents with at least this many acknowledgements. For example, set to 1 to return only incidents that were acknowledged. Omit to include all incidents.")
    min_timeout_escalations: int | None = Field(default=None, validation_alias="min_timeout_escalations", serialization_alias="min_timeout_escalations", description="Filter to incidents with at least this many timeout-based escalations. For example, set to 1 to return only incidents that escalated due to timeout. Omit to include all incidents.")
    min_manual_escalations: int | None = Field(default=None, validation_alias="min_manual_escalations", serialization_alias="min_manual_escalations", description="Filter to incidents with at least this many manual escalations. For example, set to 1 to return only incidents that were manually escalated. Omit to include all incidents.")
    team_ids: list[str] | None = Field(default=None, validation_alias="team_ids", serialization_alias="team_ids", description="Restrict results to incidents associated with specific teams. Provide as an array of team IDs. Required for user-level API keys; optional for account-level keys. Omit to include all accessible teams.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="Restrict results to incidents associated with specific services. Provide as an array of service IDs. Required for user-level API keys; optional for account-level keys. Omit to include all accessible services.")
    escalation_policy_ids: list[str] | None = Field(default=None, validation_alias="escalation_policy_ids", serialization_alias="escalation_policy_ids", description="Restrict results to incidents routed through specific escalation policies. Provide as an array of escalation policy IDs. Omit to include all accessible escalation policies.")
class GetAnalyticsMetricsIncidentsServiceAllRequestBody(StrictModel):
    """Parameters and filters to apply to the dataset."""
    time_zone: str | None = Field(default=None, description="Time zone for interpreting date ranges and grouping results. Use tzdata format (e.g., 'America/New_York', 'Etc/UTC'). Defaults to UTC if omitted.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for results. Use 'asc' for ascending or 'desc' for descending order. Only applies when order_by is specified.")
    order_by: str | None = Field(default=None, description="Column name to sort results by (e.g., 'created_at'). Pair with order parameter to control sort direction.")
    aggregate_unit: Literal["day", "week", "month"] | None = Field(default=None, description="Time unit for aggregating metrics. Use 'day', 'week', or 'month' to group metrics by that period. Omit to aggregate metrics across the entire time range.")
    filters: GetAnalyticsMetricsIncidentsServiceAllRequestBodyFilters | None = None
class GetAnalyticsMetricsIncidentsServiceAllRequest(StrictModel):
    """Retrieve aggregated incident metrics across all services, including resolution time, engagement time, and sleep interruptions. Supports filtering by time range, urgency, escalation activity, and organizational units (teams, services, escalation policies)."""
    header: GetAnalyticsMetricsIncidentsServiceAllRequestHeader
    body: GetAnalyticsMetricsIncidentsServiceAllRequestBody | None = None

# Operation: get_team_incident_analytics
class GetAnalyticsMetricsIncidentsTeamRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header; must be set to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request body content type; must be application/json.")
class GetAnalyticsMetricsIncidentsTeamRequestBodyFilters(StrictModel):
    created_at_start: str | None = Field(default=None, validation_alias="created_at_start", serialization_alias="created_at_start", description="Filter results to incidents created on or after this ISO 8601 datetime. When combined with created_at_end, the maximum supported time range is one year.")
    created_at_end: str | None = Field(default=None, validation_alias="created_at_end", serialization_alias="created_at_end", description="Filter results to incidents created before this ISO 8601 datetime. When combined with created_at_start, the maximum supported time range is one year.")
    urgency: Literal["high", "low"] | None = Field(default=None, validation_alias="urgency", serialization_alias="urgency", description="Filter results by incident urgency; include only high or low urgency incidents. If omitted, all urgency levels are included.")
    major: bool | None = Field(default=None, validation_alias="major", serialization_alias="major", description="Filter to include only major incidents (true), exclude major incidents (false), or include all incidents (omitted).")
    min_ackowledgements: int | None = Field(default=None, validation_alias="min_ackowledgements", serialization_alias="min_ackowledgements", description="Filter to include only incidents with at least this many acknowledgements. If omitted, all incidents are included regardless of acknowledgement count.")
    min_timeout_escalations: int | None = Field(default=None, validation_alias="min_timeout_escalations", serialization_alias="min_timeout_escalations", description="Filter to include only incidents with at least this many timeout escalations. If omitted, all incidents are included regardless of timeout escalation count.")
    min_manual_escalations: int | None = Field(default=None, validation_alias="min_manual_escalations", serialization_alias="min_manual_escalations", description="Filter to include only incidents with at least this many manual escalations. If omitted, all incidents are included regardless of manual escalation count.")
    team_ids: list[str] | None = Field(default=None, validation_alias="team_ids", serialization_alias="team_ids", description="Restrict results to incidents associated with these team IDs. Required for user-level and OAuth API keys; optional for account-level keys. Provide as an array of team ID strings.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="Restrict results to incidents associated with these service IDs. Optional for all key types. Provide as an array of service ID strings.")
    escalation_policy_ids: list[str] | None = Field(default=None, validation_alias="escalation_policy_ids", serialization_alias="escalation_policy_ids", description="Restrict results to incidents associated with these escalation policy IDs. Optional for all key types. Provide as an array of escalation policy ID strings.")
class GetAnalyticsMetricsIncidentsTeamRequestBody(StrictModel):
    """Parameters and filters to apply to the dataset."""
    time_zone: str | None = Field(default=None, description="Time zone for aggregation and result timestamps; must be in tzdata format (e.g., America/New_York, Etc/UTC). Defaults to UTC if omitted.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results: ascending (asc) or descending (desc). Used in conjunction with order_by.")
    order_by: str | None = Field(default=None, description="Column name to sort results by (e.g., created_at). Used in conjunction with order.")
    aggregate_unit: Literal["day", "week", "month"] | None = Field(default=None, description="Time unit for metric aggregation: day, week, or month. If omitted, metrics are aggregated across the entire period without time-based grouping.")
    filters: GetAnalyticsMetricsIncidentsTeamRequestBodyFilters | None = None
class GetAnalyticsMetricsIncidentsTeamRequest(StrictModel):
    """Retrieve aggregated incident metrics for teams, including resolution time, engagement time, and sleep interruptions. Metrics can be grouped by day, week, or month, or aggregated across the entire period."""
    header: GetAnalyticsMetricsIncidentsTeamRequestHeader
    body: GetAnalyticsMetricsIncidentsTeamRequestBody | None = None

# Operation: get_analytics_metrics_incidents_for_all_teams
class GetAnalyticsMetricsIncidentsTeamAllRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be application/json.")
class GetAnalyticsMetricsIncidentsTeamAllRequestBodyFilters(StrictModel):
    created_at_start: str | None = Field(default=None, validation_alias="created_at_start", serialization_alias="created_at_start", description="Filter results to incidents created on or after this ISO 8601 datetime. When combined with created_at_end, the maximum supported time range is one year.")
    created_at_end: str | None = Field(default=None, validation_alias="created_at_end", serialization_alias="created_at_end", description="Filter results to incidents created before this ISO 8601 datetime. When combined with created_at_start, the maximum supported time range is one year.")
    urgency: Literal["high", "low"] | None = Field(default=None, validation_alias="urgency", serialization_alias="urgency", description="Filter results by incident urgency. Specify 'high' or 'low' to include only incidents matching that urgency level.")
    major: bool | None = Field(default=None, validation_alias="major", serialization_alias="major", description="Filter to include only major incidents (true) or exclude them (false). If not specified, all incidents are included regardless of major incident status.")
    min_ackowledgements: int | None = Field(default=None, validation_alias="min_ackowledgements", serialization_alias="min_ackowledgements", description="Filter to include only incidents with at least this many acknowledgements. For example, set to 1 to return only acknowledged incidents.")
    min_timeout_escalations: int | None = Field(default=None, validation_alias="min_timeout_escalations", serialization_alias="min_timeout_escalations", description="Filter to include only incidents with at least this many timeout escalations.")
    min_manual_escalations: int | None = Field(default=None, validation_alias="min_manual_escalations", serialization_alias="min_manual_escalations", description="Filter to include only incidents with at least this many manual escalations.")
    team_ids: list[str] | None = Field(default=None, validation_alias="team_ids", serialization_alias="team_ids", description="Restrict results to incidents associated with these team IDs. Required for user-level API keys or OAuth-generated keys. Omit to include all teams the requestor has access to.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="Restrict results to incidents associated with these service IDs. Required for user-level API keys or OAuth-generated keys. Omit to include all services the requestor has access to.")
    escalation_policy_ids: list[str] | None = Field(default=None, validation_alias="escalation_policy_ids", serialization_alias="escalation_policy_ids", description="Restrict results to incidents associated with these escalation policy IDs. Omit to include all escalation policies the requestor has access to.")
class GetAnalyticsMetricsIncidentsTeamAllRequestBody(StrictModel):
    """Parameters and filters to apply to the dataset."""
    time_zone: str | None = Field(default=None, description="Time zone for results and grouping, specified in tzdata format (e.g., America/New_York, Etc/UTC). Defaults to UTC if not provided.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results: 'asc' for ascending or 'desc' for descending. Use with order_by to specify the sort column.")
    order_by: str | None = Field(default=None, description="Column name to sort results by (e.g., 'created_at'). Use with order to specify ascending or descending.")
    aggregate_unit: Literal["day", "week", "month"] | None = Field(default=None, description="Time unit for aggregating metrics: 'day', 'week', or 'month'. If not specified, metrics are aggregated across the entire requested period.")
    filters: GetAnalyticsMetricsIncidentsTeamAllRequestBodyFilters | None = None
class GetAnalyticsMetricsIncidentsTeamAllRequest(StrictModel):
    """Retrieve aggregated incident metrics across all teams, including resolution time, engagement time, and sleep interruptions. Supports filtering by date range, urgency, escalations, and other incident characteristics."""
    header: GetAnalyticsMetricsIncidentsTeamAllRequestHeader
    body: GetAnalyticsMetricsIncidentsTeamAllRequestBody | None = None

# Operation: get_pd_advance_usage_metrics
class GetAnalyticsMetricsPdAdvanceUsageFeaturesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header specifying the response format and schema version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request body content type; must be JSON.")
class GetAnalyticsMetricsPdAdvanceUsageFeaturesRequestBodyFilters(StrictModel):
    created_at_start: str | None = Field(default=None, validation_alias="created_at_start", serialization_alias="created_at_start", description="ISO 8601 datetime marking the start of the PD Advance usage creation window (inclusive). Combined with created_at_end, the time range cannot exceed one year.")
    created_at_end: str | None = Field(default=None, validation_alias="created_at_end", serialization_alias="created_at_end", description="ISO 8601 datetime marking the end of the PD Advance usage creation window (exclusive). Combined with created_at_start, the time range cannot exceed one year.")
    incident_created_at_start: str | None = Field(default=None, validation_alias="incident_created_at_start", serialization_alias="incident_created_at_start", description="ISO 8601 datetime marking the start of the incident creation window (inclusive). Combined with incident_created_at_end, the time range cannot exceed one year.")
    incident_created_at_end: str | None = Field(default=None, validation_alias="incident_created_at_end", serialization_alias="incident_created_at_end", description="ISO 8601 datetime marking the end of the incident creation window (exclusive). Combined with incident_created_at_start, the time range cannot exceed one year.")
    urgency: Literal["high", "low"] | None = Field(default=None, validation_alias="urgency", serialization_alias="urgency", description="Filter results to incidents with a specific urgency level: high or low.")
    major: bool | None = Field(default=None, validation_alias="major", serialization_alias="major", description="When true, include only major incidents; when false, exclude major incidents. Omit to include all incidents regardless of major status.")
    min_ackowledgements: int | None = Field(default=None, validation_alias="min_ackowledgements", serialization_alias="min_ackowledgements", description="Minimum number of acknowledgements required on an incident for inclusion in results. Omit to include all incidents.")
    min_timeout_escalations: int | None = Field(default=None, validation_alias="min_timeout_escalations", serialization_alias="min_timeout_escalations", description="Minimum number of timeout escalations required on an incident for inclusion in results. Omit to include all incidents.")
    min_manual_escalations: int | None = Field(default=None, validation_alias="min_manual_escalations", serialization_alias="min_manual_escalations", description="Minimum number of manual escalations required on an incident for inclusion in results. Omit to include all incidents.")
    team_ids: list[str] | None = Field(default=None, validation_alias="team_ids", serialization_alias="team_ids", description="Array of team IDs to filter incidents by team membership. Omit to include incidents from all teams accessible to the requestor.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="Array of service IDs to filter incidents by service association. Omit to include incidents from all services accessible to the requestor.")
    escalation_policy_ids: list[str] | None = Field(default=None, validation_alias="escalation_policy_ids", serialization_alias="escalation_policy_ids", description="Array of escalation policy IDs to filter incidents by escalation policy. Omit to include incidents from all escalation policies accessible to the requestor.")
class GetAnalyticsMetricsPdAdvanceUsageFeaturesRequestBody(StrictModel):
    """Parameters and filters to apply to the dataset."""
    time_zone: str | None = Field(default=None, description="Time zone for result grouping and display, specified in tzdata format (e.g., America/New_York, Europe/London). Defaults to UTC if omitted.")
    filters: GetAnalyticsMetricsPdAdvanceUsageFeaturesRequestBodyFilters | None = None
class GetAnalyticsMetricsPdAdvanceUsageFeaturesRequest(StrictModel):
    """Retrieve aggregated PD Advance usage metrics filtered by time range, incident properties, and organizational resources. Analytics data updates periodically with up to 24-hour latency for new incidents."""
    header: GetAnalyticsMetricsPdAdvanceUsageFeaturesRequestHeader
    body: GetAnalyticsMetricsPdAdvanceUsageFeaturesRequestBody | None = None

# Operation: get_analytics_metrics_for_all_responders
class GetAnalyticsMetricsRespondersAllRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header; must be set to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type; must be application/json.")
class GetAnalyticsMetricsRespondersAllRequestBodyFilters(StrictModel):
    date_range_start: str | None = Field(default=None, validation_alias="date_range_start", serialization_alias="date_range_start", description="Start of the date range as an ISO 8601 datetime string (inclusive). Incidents created before this time are excluded. Maximum supported range is one year when used with date_range_end.")
    date_range_end: str | None = Field(default=None, validation_alias="date_range_end", serialization_alias="date_range_end", description="End of the date range as an ISO 8601 datetime string (exclusive). Incidents created at or after this time are excluded. Maximum supported range is one year when used with date_range_start.")
    urgency: Literal["high", "low"] | None = Field(default=None, validation_alias="urgency", serialization_alias="urgency", description="Filter results by incident urgency: either 'high' or 'low'. Incidents not matching the specified urgency are excluded.")
    team_ids: list[str] | None = Field(default=None, validation_alias="team_ids", serialization_alias="team_ids", description="Array of team IDs to include in results. Only incidents associated with these teams are returned. If omitted, all teams accessible to the requestor are included.")
    responder_ids: list[str] | None = Field(default=None, validation_alias="responder_ids", serialization_alias="responder_ids", description="Array of responder IDs to include in results. Only incidents involving these responders are returned. If omitted, all responders accessible to the requestor are included.")
class GetAnalyticsMetricsRespondersAllRequestBody(StrictModel):
    """Parameters and filters to apply to the dataset."""
    time_zone: str | None = Field(default=None, description="Time zone for interpreting date ranges and grouping results (e.g., 'Etc/UTC'). Affects how dates are processed and displayed.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for results: 'asc' for ascending or 'desc' for descending order.")
    order_by: str | None = Field(default=None, description="Column name to sort results by (e.g., 'user_id'). Used in conjunction with the order parameter.")
    filters: GetAnalyticsMetricsRespondersAllRequestBodyFilters | None = None
class GetAnalyticsMetricsRespondersAllRequest(StrictModel):
    """Retrieve aggregated incident metrics across all responders, including resolution time, engagement time, and sleep interruptions. Results can be filtered by date range, urgency, teams, and responders, with data updated periodically (up to 24 hours for new incidents)."""
    header: GetAnalyticsMetricsRespondersAllRequestHeader
    body: GetAnalyticsMetricsRespondersAllRequestBody | None = None

# Operation: get_analytics_metrics_responders_by_team
class GetAnalyticsMetricsRespondersTeamRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header; must be set to application/vnd.pagerduty+json;version=2")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type; must be application/json")
class GetAnalyticsMetricsRespondersTeamRequestBodyFilters(StrictModel):
    date_range_start: str | None = Field(default=None, validation_alias="date_range_start", serialization_alias="date_range_start", description="Filter results to incidents created on or after this ISO 8601 datetime. Combined with date_range_end, the maximum supported time range is one year.")
    date_range_end: str | None = Field(default=None, validation_alias="date_range_end", serialization_alias="date_range_end", description="Filter results to incidents created before this ISO 8601 datetime. Combined with date_range_start, the maximum supported time range is one year.")
    urgency: Literal["high", "low"] | None = Field(default=None, validation_alias="urgency", serialization_alias="urgency", description="Filter results by incident urgency; use 'high' for high-urgency incidents or 'low' for low-urgency incidents. Omit to include all urgency levels.")
    team_ids: list[str] | None = Field(default=None, validation_alias="team_ids", serialization_alias="team_ids", description="Array of team IDs to include in results. If omitted, all teams accessible to the requestor are included. Order does not affect results.")
    responder_ids: list[str] | None = Field(default=None, validation_alias="responder_ids", serialization_alias="responder_ids", description="Array of responder IDs to include in results. If omitted, all responders accessible to the requestor are included. Order does not affect results.")
class GetAnalyticsMetricsRespondersTeamRequestBody(StrictModel):
    """Parameters and filters to apply to the dataset."""
    time_zone: str | None = Field(default=None, description="IANA timezone identifier (e.g., Etc/UTC, America/New_York) used for interpreting date ranges and grouping results.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for results; use 'asc' for ascending or 'desc' for descending order.")
    order_by: str | None = Field(default=None, description="Column name to sort results by (e.g., user_id, seconds_to_resolve). Must be used with the order parameter.")
    filters: GetAnalyticsMetricsRespondersTeamRequestBodyFilters | None = None
class GetAnalyticsMetricsRespondersTeamRequest(StrictModel):
    """Retrieve incident response metrics aggregated by team, including resolution time, engagement time, and sleep interruptions. Analytics data updates periodically with up to 24-hour latency for new incidents."""
    header: GetAnalyticsMetricsRespondersTeamRequestHeader
    body: GetAnalyticsMetricsRespondersTeamRequestBody | None = None

# Operation: get_analytics_metrics_for_all_users
class GetAnalyticsMetricsUsersAllRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to specify the response format and API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be application/json.")
class GetAnalyticsMetricsUsersAllRequestBodyFilters(StrictModel):
    created_at_start: str | None = Field(default=None, validation_alias="created_at_start", serialization_alias="created_at_start", description="Start of the date range for metrics (ISO 8601 format). If omitted, metrics begin from the earliest available data.", json_schema_extra={'format': 'date-time'})
    created_at_end: str | None = Field(default=None, validation_alias="created_at_end", serialization_alias="created_at_end", description="End of the date range for metrics (ISO 8601 format). If omitted, metrics extend to the most recent available data.", json_schema_extra={'format': 'date-time'})
    team_ids: list[str] | None = Field(default=None, validation_alias="team_ids", serialization_alias="team_ids", description="Filter results to include only users belonging to specified teams. Provide as an array of team IDs.")
    user_ids: list[str] | None = Field(default=None, validation_alias="user_ids", serialization_alias="user_ids", description="Filter results to include only specified users. Provide as an array of user IDs.")
    role_ids: list[str] | None = Field(default=None, validation_alias="role_ids", serialization_alias="role_ids", description="Filter results to include only users with specified roles. Provide as an array of role IDs.")
class GetAnalyticsMetricsUsersAllRequestBody(StrictModel):
    """Parameters and filters to apply to the dataset."""
    time_zone: str | None = Field(default=None, description="Time zone for result timestamps and time-based grouping. Must be in tzdata format (e.g., Etc/UTC, America/New_York). Defaults to Etc/UTC if not specified.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for results: ascending (asc) or descending (desc). Defaults to descending.")
    order_by: str | None = Field(default=None, description="Column to sort results by. Defaults to user_id. Common values include user_id and other metric fields.")
    aggregate_unit: Literal["day", "week", "month"] | None = Field(default=None, description="Time unit for aggregating metrics: day, week, or month. If omitted, metrics are aggregated across the entire specified period.")
    filters: GetAnalyticsMetricsUsersAllRequestBodyFilters | None = None
class GetAnalyticsMetricsUsersAllRequest(StrictModel):
    """Retrieve aggregated analytics metrics across all users in your account, including activity and performance statistics. Note: Analytics data updates periodically with up to 24 hours latency for new incidents."""
    header: GetAnalyticsMetricsUsersAllRequestHeader
    body: GetAnalyticsMetricsUsersAllRequestBody | None = None

# Operation: list_analytics_incidents
class GetAnalyticsIncidentsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be application/json.")
class GetAnalyticsIncidentsRequestBodyFilters(StrictModel):
    created_at_start: str | None = Field(default=None, validation_alias="created_at_start", serialization_alias="created_at_start", description="Filter incidents by creation timestamp (inclusive). Use ISO 8601 format. Only incidents created on or after this time are returned.")
    created_at_end: str | None = Field(default=None, validation_alias="created_at_end", serialization_alias="created_at_end", description="Filter incidents by creation timestamp (exclusive). Use ISO 8601 format. Only incidents created before this time are returned.")
    updated_after: str | None = Field(default=None, validation_alias="updated_after", serialization_alias="updated_after", description="Filter incidents by last update time. Use ISO 8601 format. Only incidents updated after this timestamp are returned.")
    urgency: str | None = Field(default=None, validation_alias="urgency", serialization_alias="urgency", description="Filter incidents by urgency level. Valid values are 'high' and 'low'.")
    major: bool | None = Field(default=None, validation_alias="major", serialization_alias="major", description="Filter to show only major incidents. Major incidents have one of the two highest priorities or multiple acknowledged responders.")
    team_ids: list[str] | None = Field(default=None, validation_alias="team_ids", serialization_alias="team_ids", description="Filter by team IDs. Provide an array of team IDs to return only incidents assigned to members of those teams. Required for user-level API keys or OAuth-generated keys.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="Filter by service IDs. Provide an array of service IDs to return only incidents related to those services.")
    incident_type_ids: list[str] | None = Field(default=None, validation_alias="incident_type_ids", serialization_alias="incident_type_ids", description="Filter by incident type IDs. Provide an array of incident type IDs to return only incidents matching those types.")
class GetAnalyticsIncidentsRequestBody(StrictModel):
    """Parameters and filters to apply to the dataset."""
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results. Use 'asc' for ascending or 'desc' for descending. Defaults to 'desc'.")
    order_by: Literal["created_at", "seconds_to_resolve"] | None = Field(default=None, description="Column to sort by. Options are 'created_at' (default) or 'seconds_to_resolve'.")
    time_zone: str | None = Field(default=None, description="Time zone for result timestamps. Use IANA time zone format (e.g., 'Etc/UTC', 'America/New_York'). Defaults to account time zone.")
    filters: GetAnalyticsIncidentsRequestBodyFilters | None = None
class GetAnalyticsIncidentsRequest(StrictModel):
    """Retrieve enriched incident data and metrics for multiple incidents, including resolution time, engagement time, and sleep interruptions. Analytics data updates periodically with up to 24-hour latency for new incidents."""
    header: GetAnalyticsIncidentsRequestHeader
    body: GetAnalyticsIncidentsRequestBody | None = None

# Operation: get_incident_analytics
class GetAnalyticsIncidentsByIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to retrieve analytics for.")
class GetAnalyticsIncidentsByIdRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body. Must be JSON format.")
class GetAnalyticsIncidentsByIdRequest(StrictModel):
    """Retrieve enriched analytics data and metrics for a single incident, including resolution time, engagement time, and sleep interruption metrics. Note: Analytics data updates periodically with up to 24 hours latency for new incidents."""
    path: GetAnalyticsIncidentsByIdRequestPath
    header: GetAnalyticsIncidentsByIdRequestHeader

# Operation: get_incident_response_analytics
class GetAnalyticsIncidentResponsesByIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident for which to retrieve response analytics.")
class GetAnalyticsIncidentResponsesByIdRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header; use application/vnd.pagerduty+json;version=2 for current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request; must be application/json.")
class GetAnalyticsIncidentResponsesByIdRequestBody(StrictModel):
    """Parameters to apply to the dataset."""
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results: ascending (asc) or descending (desc). Defaults to descending.")
    order_by: Literal["requested_at"] | None = Field(default=None, description="Field to sort by; currently supports requested_at (the timestamp when the response was requested).")
    time_zone: str | None = Field(default=None, description="Time zone for interpreting and displaying timestamps in results (e.g., Etc/UTC). Defaults to UTC if not specified.")
class GetAnalyticsIncidentResponsesByIdRequest(StrictModel):
    """Retrieve enriched responder analytics for a specific incident, including metrics like time to respond, responder type, and response status. Note: Analytics data updates daily with up to 24-hour latency for new incident responses."""
    path: GetAnalyticsIncidentResponsesByIdRequestPath
    header: GetAnalyticsIncidentResponsesByIdRequestHeader
    body: GetAnalyticsIncidentResponsesByIdRequestBody | None = None

# Operation: list_responder_incidents
class GetAnalyticsResponderIncidentsRequestPath(StrictModel):
    responder_id: str = Field(default=..., description="The unique identifier of the responder whose incidents you want to retrieve.")
class GetAnalyticsResponderIncidentsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be application/json.")
class GetAnalyticsResponderIncidentsRequestBodyFilters(StrictModel):
    created_at_start: str | None = Field(default=None, validation_alias="created_at_start", serialization_alias="created_at_start", description="Filter results to incidents created on or after this timestamp (ISO 8601 format, e.g., 2023-05-01T00:00:00-04:00).")
    created_at_end: str | None = Field(default=None, validation_alias="created_at_end", serialization_alias="created_at_end", description="Filter results to incidents created before this timestamp (ISO 8601 format, e.g., 2023-06-01T00:00:00-04:00).")
    urgency: str | None = Field(default=None, validation_alias="urgency", serialization_alias="urgency", description="Filter results by incident urgency level (e.g., 'high' or 'low').")
    major: bool | None = Field(default=None, validation_alias="major", serialization_alias="major", description="Filter to only major incidents, which are classified as such when they have one of the two highest priorities or involve multiple acknowledged responders.")
    team_ids: list[str] | None = Field(default=None, validation_alias="team_ids", serialization_alias="team_ids", description="Filter results to incidents assigned to members of specific teams. Provide an array of team IDs. Requires teams ability on your account.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids", serialization_alias="service_ids", description="Filter results to incidents related to specific services. Provide an array of service IDs.")
    incident_type_ids: list[str] | None = Field(default=None, validation_alias="incident_type_ids", serialization_alias="incident_type_ids", description="Filter results to incidents matching specific incident type IDs. Provide an array of incident type IDs.")
class GetAnalyticsResponderIncidentsRequestBody(StrictModel):
    """Parameters and filters to apply to the dataset."""
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results: 'asc' for ascending or 'desc' for descending. Defaults to descending.")
    order_by: Literal["incident_created_at"] | None = Field(default=None, description="Column to sort by. Currently supports 'incident_created_at' (default).")
    time_zone: str | None = Field(default=None, description="Time zone for interpreting timestamps in results (e.g., 'Etc/UTC'). Use IANA time zone identifiers.")
    filters: GetAnalyticsResponderIncidentsRequestBodyFilters | None = None
class GetAnalyticsResponderIncidentsRequest(StrictModel):
    """Retrieve enriched incident data and performance metrics for a specific responder, including resolution times, engagement times, and sleep interruptions. Note: Analytics data updates periodically and may take up to 24 hours to reflect new incidents."""
    path: GetAnalyticsResponderIncidentsRequestPath
    header: GetAnalyticsResponderIncidentsRequestHeader
    body: GetAnalyticsResponderIncidentsRequestBody | None = None

# Operation: list_analytics_users
class GetAnalyticsUsersRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to specify the response format and API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be application/json.")
class GetAnalyticsUsersRequestBodyFilters(StrictModel):
    created_at_start: str | None = Field(default=None, validation_alias="created_at_start", serialization_alias="created_at_start", description="Filter results to users created on or after this date. Specify as an ISO 8601 datetime string.", json_schema_extra={'format': 'date-time'})
    created_at_end: str | None = Field(default=None, validation_alias="created_at_end", serialization_alias="created_at_end", description="Filter results to users created on or before this date. Specify as an ISO 8601 datetime string.", json_schema_extra={'format': 'date-time'})
    team_ids: list[str] | None = Field(default=None, validation_alias="team_ids", serialization_alias="team_ids", description="Filter results to include only users belonging to the specified teams. Provide as an array of team IDs.")
    user_ids: list[str] | None = Field(default=None, validation_alias="user_ids", serialization_alias="user_ids", description="Filter results to include only the specified users. Provide as an array of user IDs.")
    role_ids: list[str] | None = Field(default=None, validation_alias="role_ids", serialization_alias="role_ids", description="Filter results to include only users with the specified roles. Provide as an array of role IDs.")
class GetAnalyticsUsersRequestBody(StrictModel):
    """Parameters and filters to apply to the dataset."""
    time_zone: str | None = Field(default=None, description="Time zone for result timestamps and time-based grouping. Must be a valid tzdata format (e.g., Etc/UTC, America/New_York).")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for results: ascending (asc) or descending (desc). Defaults to descending.")
    order_by: str | None = Field(default=None, description="Column to sort results by. Defaults to user_id. Common values include user_id and creation date fields.")
    aggregate_unit: Literal["day", "week", "month"] | None = Field(default=None, description="Time unit for aggregating metrics. Choose day, week, or month for time-bucketed results. If omitted, metrics are aggregated across the entire period.")
    filters: GetAnalyticsUsersRequestBodyFilters | None = None
class GetAnalyticsUsersRequest(StrictModel):
    """Retrieve raw user analytics data for your account, including detailed user activity and configuration metrics. Note that analytics data updates periodically with up to 24 hours latency for new user data."""
    header: GetAnalyticsUsersRequestHeader
    body: GetAnalyticsUsersRequestBody | None = None

# Operation: list_audit_records
class ListAuditRecordsRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="Start of the date range to search (ISO 8601 format). Defaults to 24 hours ago if not specified.", json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="End of the date range to search (ISO 8601 format). Defaults to now if not specified. Cannot be more than 31 days after the `since` parameter.", json_schema_extra={'format': 'date-time'})
    root_resource_types: Literal["users", "teams", "schedules", "escalation_policies", "services"] | None = Field(default=None, validation_alias="root_resource_types[]", serialization_alias="root_resource_types[]", description="Filter records by the type of resource affected. Accepts one or more values: users, teams, schedules, escalation_policies, or services.")
    actor_type: Literal["user_reference", "api_key_reference", "app_reference"] | None = Field(default=None, description="Filter records by who performed the action: a user, API key, or application.")
    actor_id: str | None = Field(default=None, description="Filter records by a specific actor's ID. Requires `actor_type` to be specified.")
    method_type: Literal["browser", "oauth", "api_token", "identity_provider", "other"] | None = Field(default=None, description="Filter records by the method used to perform the action: browser session, OAuth, API token, identity provider, or other.")
    method_truncated_token: str | None = Field(default=None, description="Filter records by a truncated authentication token. Requires `method_type` to be specified.")
    actions: Literal["create", "update", "delete"] | None = Field(default=None, validation_alias="actions[]", serialization_alias="actions[]", description="Filter records by the type of action performed: create, update, or delete. Accepts one or more values.")
class ListAuditRecordsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="HTTP Accept header for API versioning. Must be set to the PagerDuty v2 JSON media type.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="HTTP Content-Type header specifying the request body format as JSON.")
class ListAuditRecordsRequest(StrictModel):
    """Retrieve audit trail records for your PagerDuty account, filtered by date range and optional criteria like resource type, actor, or action. Results are sorted by execution time from newest to oldest and support cursor-based pagination."""
    query: ListAuditRecordsRequestQuery | None = None
    header: ListAuditRecordsRequestHeader

# Operation: list_automation_actions
class GetAllAutomationActionsRequestQuery(StrictModel):
    runner_id: str | None = Field(default=None, description="Filter results to automation actions linked to a specific runner by ID. Use the special value `any` to include only actions linked to runners, excluding unlinked actions.")
    classification: Literal["diagnostic", "remediation"] | None = Field(default=None, description="Filter results by action classification: either `diagnostic` for diagnostic actions or `remediation` for remediation actions.")
    team_id: str | None = Field(default=None, description="Filter results to include only automation actions associated with the specified team ID.")
    service_id: str | None = Field(default=None, description="Filter results to include only automation actions associated with the specified service ID.")
    action_type: Literal["script", "process_automation"] | None = Field(default=None, description="Filter results by action type: either `script` for script-based actions or `process_automation` for process automation actions.")
class GetAllAutomationActionsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to `application/vnd.pagerduty+json;version=2` to request the correct API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request content type. Must be `application/json`.")
class GetAllAutomationActionsRequest(StrictModel):
    """Retrieves a list of automation actions filtered by optional criteria such as runner, classification, team, service, or action type. Results are sorted alphabetically by action name and support cursor-based pagination."""
    query: GetAllAutomationActionsRequestQuery | None = None
    header: GetAllAutomationActionsRequestHeader

# Operation: create_automation_action
class CreateAutomationActionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version. Must be set to application/vnd.pagerduty+json;version=2 to use the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format. Must be application/json for this operation.")
class CreateAutomationActionRequestBody(StrictModel):
    action: AutomationActionsScriptActionPostBody | AutomationActionsProcessAutomationJobActionPostBody = Field(default=..., description="The automation action configuration object defining the action type (Script, Process Automation, or Runbook Automation) and its properties.")
class CreateAutomationActionRequest(StrictModel):
    """Create a new automation action (Script, Process Automation, or Runbook Automation) to define automated workflows and tasks within PagerDuty."""
    header: CreateAutomationActionRequestHeader
    body: CreateAutomationActionRequestBody

# Operation: get_automation_action
class GetAutomationActionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the automation action to retrieve.")
class GetAutomationActionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body. Must be set to application/json.")
class GetAutomationActionRequest(StrictModel):
    """Retrieve a specific automation action by its ID. Returns the full details of the automation action resource."""
    path: GetAutomationActionRequestPath
    header: GetAutomationActionRequestHeader

# Operation: update_automation_action
class UpdateAutomationActionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Automation Action to update.")
class UpdateAutomationActionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON.")
class UpdateAutomationActionRequestBody(StrictModel):
    action: AutomationActionsScriptActionPutBody | AutomationActionsProcessAutomationJobActionPutBody = Field(default=..., description="The Automation Action object containing the updated configuration details.")
class UpdateAutomationActionRequest(StrictModel):
    """Updates an existing Automation Action with new configuration. Specify the action ID and provide the updated action details in the request body."""
    path: UpdateAutomationActionRequestPath
    header: UpdateAutomationActionRequestHeader
    body: UpdateAutomationActionRequestBody

# Operation: delete_automation_action
class DeleteAutomationActionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Automation Action to delete.")
class DeleteAutomationActionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to JSON format.")
class DeleteAutomationActionRequest(StrictModel):
    """Permanently delete an Automation Action by its ID. This operation removes the automation action and cannot be undone."""
    path: DeleteAutomationActionRequestPath
    header: DeleteAutomationActionRequestHeader

# Operation: invoke_automation_action
class CreateAutomationActionInvocationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the automation action to invoke.")
class CreateAutomationActionInvocationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be application/json.")
class CreateAutomationActionInvocationRequestBodyInvocationMetadata(StrictModel):
    incident_id: str = Field(default=..., validation_alias="incident_id", serialization_alias="incident_id", description="The unique identifier of the incident associated with this invocation. Required to scope the action execution to a specific incident.")
    alert_id: str | None = Field(default=None, validation_alias="alert_id", serialization_alias="alert_id", description="The unique identifier of the alert associated with this invocation. Optional; use to further scope the action to a specific alert within an incident.")
class CreateAutomationActionInvocationRequestBodyInvocation(StrictModel):
    metadata: CreateAutomationActionInvocationRequestBodyInvocationMetadata
class CreateAutomationActionInvocationRequestBody(StrictModel):
    invocation: CreateAutomationActionInvocationRequestBodyInvocation
class CreateAutomationActionInvocationRequest(StrictModel):
    """Triggers an invocation of an automation action, optionally scoped to a specific incident or alert. This executes the action's defined workflow or automation logic."""
    path: CreateAutomationActionInvocationRequestPath
    header: CreateAutomationActionInvocationRequestHeader
    body: CreateAutomationActionInvocationRequestBody

# Operation: list_automation_action_service_associations
class GetAutomationActionsActionServiceAssociationsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Automation Action resource whose service associations you want to retrieve.")
class GetAutomationActionsActionServiceAssociationsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version. Defaults to PagerDuty API version 2 with JSON content type.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body. Must be set to JSON format.")
class GetAutomationActionsActionServiceAssociationsRequest(StrictModel):
    """Retrieve all service references associated with a specific Automation Action. This returns the complete list of services linked to the automation action for management and visibility purposes."""
    path: GetAutomationActionsActionServiceAssociationsRequestPath
    header: GetAutomationActionsActionServiceAssociationsRequestHeader

# Operation: associate_automation_action_with_service
class CreateAutomationActionServiceAssocationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Automation Action resource to associate with a service.")
class CreateAutomationActionServiceAssocationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be application/json.")
class CreateAutomationActionServiceAssocationRequestBody(StrictModel):
    service: ServiceReference = Field(default=..., description="The service object to associate with the Automation Action. This should contain the service identifier and any required service details.")
class CreateAutomationActionServiceAssocationRequest(StrictModel):
    """Associate an Automation Action with a service to enable the action to be triggered by or applied to that service. This establishes the relationship between an automation action and a specific service in your PagerDuty account."""
    path: CreateAutomationActionServiceAssocationRequestPath
    header: CreateAutomationActionServiceAssocationRequestHeader
    body: CreateAutomationActionServiceAssocationRequestBody

# Operation: get_automation_action_service_association
class GetAutomationActionsActionServiceAssociationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Automation Action resource.")
    service_id: str = Field(default=..., description="The unique identifier of the service associated with the Automation Action.")
class GetAutomationActionsActionServiceAssociationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version. Defaults to PagerDuty JSON API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body. Must be JSON format.")
class GetAutomationActionsActionServiceAssociationRequest(StrictModel):
    """Retrieve the details of the relationship between a specific Automation Action and a service. This shows how an automation action is associated with and configured for a particular service."""
    path: GetAutomationActionsActionServiceAssociationRequestPath
    header: GetAutomationActionsActionServiceAssociationRequestHeader

# Operation: remove_automation_action_service_association
class DeleteAutomationActionServiceAssociationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Automation Action to disassociate.")
    service_id: str = Field(default=..., description="The unique identifier of the service from which the Automation Action should be removed.")
class DeleteAutomationActionServiceAssociationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be JSON format.")
class DeleteAutomationActionServiceAssociationRequest(StrictModel):
    """Remove the association between an Automation Action and a service, effectively disabling that action for the specified service."""
    path: DeleteAutomationActionServiceAssociationRequestPath
    header: DeleteAutomationActionServiceAssociationRequestHeader

# Operation: list_automation_action_team_associations
class GetAutomationActionsActionTeamAssociationsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Automation Action resource.")
class GetAutomationActionsActionTeamAssociationsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to application/json.")
class GetAutomationActionsActionTeamAssociationsRequest(StrictModel):
    """Retrieve all teams associated with a specific Automation Action. Use this to view which teams are linked to an automation action for access control and assignment purposes."""
    path: GetAutomationActionsActionTeamAssociationsRequestPath
    header: GetAutomationActionsActionTeamAssociationsRequestHeader

# Operation: add_automation_action_team
class CreateAutomationActionTeamAssociationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Automation Action to associate with a team.")
class CreateAutomationActionTeamAssociationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version. Use the default PagerDuty JSON format version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON.")
class CreateAutomationActionTeamAssociationRequestBody(StrictModel):
    team: TeamReference = Field(default=..., description="The team object containing the team identifier and details to associate with this Automation Action.")
class CreateAutomationActionTeamAssociationRequest(StrictModel):
    """Associate an Automation Action with a team, enabling the team to access and manage the automation action."""
    path: CreateAutomationActionTeamAssociationRequestPath
    header: CreateAutomationActionTeamAssociationRequestHeader
    body: CreateAutomationActionTeamAssociationRequestBody

# Operation: get_automation_action_team_association
class GetAutomationActionsActionTeamAssociationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Automation Action resource.")
    team_id: str = Field(default=..., description="The unique identifier of the team associated with the Automation Action.")
class GetAutomationActionsActionTeamAssociationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and schema version. Defaults to PagerDuty JSON API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body. Must be application/json.")
class GetAutomationActionsActionTeamAssociationRequest(StrictModel):
    """Retrieve the association details between a specific Automation Action and a team, including their relationship configuration and metadata."""
    path: GetAutomationActionsActionTeamAssociationRequestPath
    header: GetAutomationActionsActionTeamAssociationRequestHeader

# Operation: remove_automation_action_team_association
class DeleteAutomationActionTeamAssociationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Automation Action resource to disassociate.")
    team_id: str = Field(default=..., description="The unique identifier of the team to disassociate from the Automation Action.")
class DeleteAutomationActionTeamAssociationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version (defaults to PagerDuty JSON API v2).")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body, must be JSON format.")
class DeleteAutomationActionTeamAssociationRequest(StrictModel):
    """Remove the association between an Automation Action and a specific team, effectively disassociating them from each other."""
    path: DeleteAutomationActionTeamAssociationRequestPath
    header: DeleteAutomationActionTeamAssociationRequestHeader

# Operation: list_automation_action_invocations
class ListAutomationActionInvocationsRequestQuery(StrictModel):
    invocation_state: Literal["prepared", "created", "sent", "queued", "running", "aborted", "completed", "error", "unknown"] | None = Field(default=None, description="Filter invocations by their current state in the execution lifecycle, such as prepared, running, completed, or error.")
    incident_id: str | None = Field(default=None, description="Filter invocations to those associated with a specific incident by its ID.")
    action_id: str | None = Field(default=None, description="Filter invocations to those triggered by a specific automation action by its ID.")
class ListAutomationActionInvocationsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and schema version. Use the default value for standard JSON responses.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body content type as JSON.")
class ListAutomationActionInvocationsRequest(StrictModel):
    """Retrieve a list of automation action invocations, optionally filtered by invocation state, incident, or action. Use this to track the execution history and status of automated actions."""
    query: ListAutomationActionInvocationsRequestQuery | None = None
    header: ListAutomationActionInvocationsRequestHeader

# Operation: get_automation_action_invocation
class GetAutomationActionsInvocationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Automation Action Invocation to retrieve.")
class GetAutomationActionsInvocationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body. Must be set to application/json.")
class GetAutomationActionsInvocationRequest(StrictModel):
    """Retrieve details about a specific Automation Action Invocation by its ID. This returns the current state and metadata of an invocation execution."""
    path: GetAutomationActionsInvocationRequestPath
    header: GetAutomationActionsInvocationRequestHeader

# Operation: list_automation_action_runners
class GetAutomationActionsRunnersRequestQuery(StrictModel):
    include: Annotated[list[Literal["associated_actions"]], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array of additional data elements to include in the response payload, expanding the default response structure.")
class GetAutomationActionsRunnersRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request content type. Must be set to JSON format.")
class GetAutomationActionsRunnersRequest(StrictModel):
    """Retrieve a list of Automation Action runners filtered by query parameters. Results are sorted alphabetically by runner name and support cursor-based pagination."""
    query: GetAutomationActionsRunnersRequestQuery | None = None
    header: GetAutomationActionsRunnersRequestHeader

# Operation: create_automation_runner
class CreateAutomationActionsRunnerRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version. Must be set to application/vnd.pagerduty+json;version=2 to use the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format. Must be application/json.")
class CreateAutomationActionsRunnerRequestBody(StrictModel):
    runner: AutomationActionsRunnerSidecarPostBody | AutomationActionsRunnerRunbookPostBody = Field(default=..., description="The automation runner configuration object containing the runner type (Process Automation or Runbook Automation) and associated settings.")
class CreateAutomationActionsRunnerRequest(StrictModel):
    """Create a new automation runner for Process Automation or Runbook Automation workflows. The runner executes automation actions within your PagerDuty environment."""
    header: CreateAutomationActionsRunnerRequestHeader
    body: CreateAutomationActionsRunnerRequestBody

# Operation: get_automation_actions_runner
class GetAutomationActionsRunnerRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Automation Action runner to retrieve.")
class GetAutomationActionsRunnerRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON.")
class GetAutomationActionsRunnerRequest(StrictModel):
    """Retrieve a specific Automation Action runner by its ID. Use this to fetch details about a configured runner instance."""
    path: GetAutomationActionsRunnerRequestPath
    header: GetAutomationActionsRunnerRequestHeader

# Operation: update_automation_actions_runner
class UpdateAutomationActionsRunnerRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Automation Action runner to update.")
class UpdateAutomationActionsRunnerRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API version header for response formatting. Defaults to PagerDuty API version 2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON.")
class UpdateAutomationActionsRunnerRequestBody(StrictModel):
    runner: AutomationActionsRunnerSidecarBody | AutomationActionsRunnerRunbookBody = Field(default=..., description="The runner configuration object containing the properties to update. Refer to the API documentation for the complete schema of updatable runner fields.")
class UpdateAutomationActionsRunnerRequest(StrictModel):
    """Update the configuration and settings of an existing Automation Action runner. This operation allows you to modify runner properties such as name, status, or other operational parameters."""
    path: UpdateAutomationActionsRunnerRequestPath
    header: UpdateAutomationActionsRunnerRequestHeader
    body: UpdateAutomationActionsRunnerRequestBody

# Operation: delete_automation_actions_runner
class DeleteAutomationActionsRunnerRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Automation Action runner to delete.")
class DeleteAutomationActionsRunnerRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to JSON format.")
class DeleteAutomationActionsRunnerRequest(StrictModel):
    """Permanently delete an Automation Action runner by its ID. This operation removes the runner and cannot be undone."""
    path: DeleteAutomationActionsRunnerRequestPath
    header: DeleteAutomationActionsRunnerRequestHeader

# Operation: list_runner_team_associations
class GetAutomationActionsRunnerTeamAssociationsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the automation action runner.")
class GetAutomationActionsRunnerTeamAssociationsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body. Must be set to application/json.")
class GetAutomationActionsRunnerTeamAssociationsRequest(StrictModel):
    """Retrieve all teams associated with an automation action runner. Use this to view which teams have access to or are linked with a specific runner."""
    path: GetAutomationActionsRunnerTeamAssociationsRequestPath
    header: GetAutomationActionsRunnerTeamAssociationsRequestHeader

# Operation: associate_runner_with_team
class CreateAutomationActionsRunnerTeamAssociationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the automation actions runner to associate with a team.")
class CreateAutomationActionsRunnerTeamAssociationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version. Use the default PagerDuty JSON format version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be application/json.")
class CreateAutomationActionsRunnerTeamAssociationRequestBody(StrictModel):
    team: TeamReference = Field(default=..., description="The team object containing the team details to associate with the runner. Typically includes the team's unique identifier.")
class CreateAutomationActionsRunnerTeamAssociationRequest(StrictModel):
    """Associate an automation actions runner with a team to enable the team to use that runner for executing automations."""
    path: CreateAutomationActionsRunnerTeamAssociationRequestPath
    header: CreateAutomationActionsRunnerTeamAssociationRequestHeader
    body: CreateAutomationActionsRunnerTeamAssociationRequestBody

# Operation: get_runner_team_association
class GetAutomationActionsRunnerTeamAssociationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the automation action runner resource.")
    team_id: str = Field(default=..., description="The unique identifier of the team associated with the runner.")
class GetAutomationActionsRunnerTeamAssociationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and schema version. Defaults to PagerDuty JSON API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body. Must be JSON format.")
class GetAutomationActionsRunnerTeamAssociationRequest(StrictModel):
    """Retrieve the association details between a specific automation action runner and a team, including their relationship configuration and status."""
    path: GetAutomationActionsRunnerTeamAssociationRequestPath
    header: GetAutomationActionsRunnerTeamAssociationRequestHeader

# Operation: remove_runner_from_team
class DeleteAutomationActionsRunnerTeamAssociationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the automation action runner to disassociate.")
    team_id: str = Field(default=..., description="The unique identifier of the team to disassociate from the runner.")
class DeleteAutomationActionsRunnerTeamAssociationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version (defaults to PagerDuty JSON v2).")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body (must be application/json).")
class DeleteAutomationActionsRunnerTeamAssociationRequest(StrictModel):
    """Removes the association between an automation action runner and a team, preventing the runner from executing actions for that team."""
    path: DeleteAutomationActionsRunnerTeamAssociationRequestPath
    header: DeleteAutomationActionsRunnerTeamAssociationRequestHeader

# Operation: list_business_services
class ListBusinessServicesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and schema version. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON. This is the only supported content type for this operation.")
class ListBusinessServicesRequest(StrictModel):
    """Retrieve a list of existing business services that span multiple technical services and may be owned by different teams. Use this to discover available business services in your PagerDuty instance."""
    header: ListBusinessServicesRequestHeader

# Operation: create_business_service
class CreateBusinessServiceRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to specify the API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request body content type. Must be application/json.")
class CreateBusinessServiceRequestBodyBusinessServiceTeam(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The Team ID that will own this Business Service.")
class CreateBusinessServiceRequestBodyBusinessService(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A human-readable description of the Business Service's purpose and scope.")
    point_of_contact: str | None = Field(default=None, validation_alias="point_of_contact", serialization_alias="point_of_contact", description="The identifier or reference of the team or person responsible for owning and managing this Business Service.")
    team: CreateBusinessServiceRequestBodyBusinessServiceTeam | None = None
class CreateBusinessServiceRequestBody(StrictModel):
    business_service: CreateBusinessServiceRequestBodyBusinessService | None = None
class CreateBusinessServiceRequest(StrictModel):
    """Create a new Business Service that models capabilities spanning multiple technical services and owned by different teams. Each account is limited to 5,000 business services."""
    header: CreateBusinessServiceRequestHeader
    body: CreateBusinessServiceRequestBody | None = None

# Operation: get_business_service
class GetBusinessServiceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Business Service to retrieve.")
class GetBusinessServiceRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and schema version. Defaults to PagerDuty JSON API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body. Must be set to application/json.")
class GetBusinessServiceRequest(StrictModel):
    """Retrieve details about a specific Business Service, which represents a capability spanning multiple technical services and potentially owned by several teams."""
    path: GetBusinessServiceRequestPath
    header: GetBusinessServiceRequestHeader

# Operation: update_business_service
class UpdateBusinessServiceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Business Service to update.")
class UpdateBusinessServiceRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be JSON format.")
class UpdateBusinessServiceRequestBodyBusinessServiceTeam(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The ID of the team that owns or is associated with this Business Service.")
class UpdateBusinessServiceRequestBodyBusinessService(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A text description of the Business Service's purpose, scope, or other relevant details.")
    point_of_contact: str | None = Field(default=None, validation_alias="point_of_contact", serialization_alias="point_of_contact", description="The name or identifier of the person or team responsible for owning and managing this Business Service.")
    team: UpdateBusinessServiceRequestBodyBusinessServiceTeam | None = None
class UpdateBusinessServiceRequestBody(StrictModel):
    business_service: UpdateBusinessServiceRequestBodyBusinessService | None = None
class UpdateBusinessServiceRequest(StrictModel):
    """Update an existing Business Service that spans multiple technical services and may be owned by several teams. Supports both PUT and PATCH HTTP methods."""
    path: UpdateBusinessServiceRequestPath
    header: UpdateBusinessServiceRequestHeader
    body: UpdateBusinessServiceRequestBody | None = None

# Operation: delete_business_service
class DeleteBusinessServiceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the business service to delete.")
class DeleteBusinessServiceRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to application/json.")
class DeleteBusinessServiceRequest(StrictModel):
    """Permanently delete a business service by its ID. Once deleted, the service will no longer be accessible in the web UI and cannot be associated with new incidents."""
    path: DeleteBusinessServiceRequestPath
    header: DeleteBusinessServiceRequestHeader

# Operation: subscribe_account_to_business_service
class CreateBusinessServiceAccountSubscriptionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Business Service to subscribe to.")
class CreateBusinessServiceAccountSubscriptionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default PagerDuty JSON format version 2.")
class CreateBusinessServiceAccountSubscriptionRequest(StrictModel):
    """Subscribe your account to a Business Service, enabling access to its features and capabilities. Requires the `subscribers.write` OAuth scope."""
    path: CreateBusinessServiceAccountSubscriptionRequestPath
    header: CreateBusinessServiceAccountSubscriptionRequestHeader

# Operation: remove_business_service_account_subscription
class RemoveBusinessServiceAccountSubscriptionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Business Service from which to remove the account subscription.")
class RemoveBusinessServiceAccountSubscriptionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="The API version to use for this request, specified via the Accept header. Defaults to PagerDuty API version 2 if not provided.")
class RemoveBusinessServiceAccountSubscriptionRequest(StrictModel):
    """Unsubscribe your account from a Business Service. This operation removes the subscription relationship between your account and the specified Business Service."""
    path: RemoveBusinessServiceAccountSubscriptionRequestPath
    header: RemoveBusinessServiceAccountSubscriptionRequestHeader

# Operation: list_business_service_subscribers
class GetBusinessServiceSubscribersRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Business Service for which to retrieve subscribers.")
class GetBusinessServiceSubscribersRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="The API version to use for this request, specified as a media type. Defaults to PagerDuty API v2 JSON format.")
class GetBusinessServiceSubscribersRequest(StrictModel):
    """Retrieve all notification subscribers configured for a specific Business Service. Only subscribers that have been explicitly added through the subscriber creation endpoint will be returned."""
    path: GetBusinessServiceSubscribersRequestPath
    header: GetBusinessServiceSubscribersRequestHeader

# Operation: add_subscribers_to_business_service
class CreateBusinessServiceNotificationSubscribersRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Business Service to which subscribers will be added.")
class CreateBusinessServiceNotificationSubscribersRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default PagerDuty JSON format version 2.")
class CreateBusinessServiceNotificationSubscribersRequestBody(StrictModel):
    """The entities to subscribe."""
    subscribers: Annotated[list[NotificationSubscriber], AfterValidator(_check_unique_items)] = Field(default=..., description="Array of subscriber objects to add to the Business Service. Must contain at least one subscriber. Each subscriber should specify the entity type and ID.", min_length=1)
class CreateBusinessServiceNotificationSubscribersRequest(StrictModel):
    """Subscribe one or more entities (users, teams, or schedules) to a Business Service to receive notifications related to that service."""
    path: CreateBusinessServiceNotificationSubscribersRequestPath
    header: CreateBusinessServiceNotificationSubscribersRequestHeader
    body: CreateBusinessServiceNotificationSubscribersRequestBody

# Operation: list_supporting_service_impacts
class GetBusinessServiceSupportingServiceImpactsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Business Service for which to retrieve supporting service impacts.")
class GetBusinessServiceSupportingServiceImpactsRequestQuery(StrictModel):
    additional_fields: Literal["services.highest_impacting_priority", "total_impacted_count"] | None = Field(default=None, validation_alias="additional_fields[]", serialization_alias="additional_fields[]", description="Optional fields to include in the response. Choose from: `services.highest_impacting_priority` to get the highest priority per business service, or `total_impacted_count` to get the total impacted count.")
    ids: str | None = Field(default=None, validation_alias="ids[]", serialization_alias="ids[]", description="Filter results to only include supporting services with the specified IDs. Provide as a list of resource identifiers.")
class GetBusinessServiceSupportingServiceImpactsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default value `application/vnd.pagerduty+json;version=2` unless a different API version is required.")
class GetBusinessServiceSupportingServiceImpactsRequest(StrictModel):
    """Retrieve the supporting Business Services for a given Business Service, sorted by impact level and recency. Returns up to 200 most impacted supporting services with their impact status."""
    path: GetBusinessServiceSupportingServiceImpactsRequestPath
    query: GetBusinessServiceSupportingServiceImpactsRequestQuery | None = None
    header: GetBusinessServiceSupportingServiceImpactsRequestHeader

# Operation: remove_business_service_notification_subscribers
class RemoveBusinessServiceNotificationSubscriberRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Business Service from which subscribers will be unsubscribed.")
class RemoveBusinessServiceNotificationSubscriberRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="The API version header for request/response formatting. Defaults to PagerDuty API v2 JSON format.")
class RemoveBusinessServiceNotificationSubscriberRequestBody(StrictModel):
    """The entities to unsubscribe."""
    subscribers: Annotated[list[NotificationSubscriber], AfterValidator(_check_unique_items)] = Field(default=..., description="An array of subscriber identifiers to unsubscribe from the Business Service. Must contain at least one subscriber ID.", min_length=1)
class RemoveBusinessServiceNotificationSubscriberRequest(StrictModel):
    """Unsubscribe one or more subscribers from receiving notifications for a specific Business Service. This operation removes the notification subscriptions for the provided subscriber IDs."""
    path: RemoveBusinessServiceNotificationSubscriberRequestPath
    header: RemoveBusinessServiceNotificationSubscriberRequestHeader
    body: RemoveBusinessServiceNotificationSubscriberRequestBody

# Operation: list_business_service_impactors
class GetBusinessServiceTopLevelImpactorsRequestQuery(StrictModel):
    ids: str | None = Field(default=None, validation_alias="ids[]", serialization_alias="ids[]", description="Filter results to specific Business Services by their IDs. Provide one or more IDs to retrieve Impactors for only those services; omit to retrieve Impactors for all top-level Business Services.")
class GetBusinessServiceTopLevelImpactorsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and schema version. Use the default value unless you require a different API version.")
class GetBusinessServiceTopLevelImpactorsRequest(StrictModel):
    """Retrieve the highest-priority Impactors (currently limited to Incidents) affecting top-level Business Services on your account, sorted by priority and creation date. Returns up to 200 results; use the ids[] parameter to filter for specific Business Services."""
    query: GetBusinessServiceTopLevelImpactorsRequestQuery | None = None
    header: GetBusinessServiceTopLevelImpactorsRequestHeader

# Operation: list_business_services_by_impact
class GetBusinessServiceImpactsRequestQuery(StrictModel):
    additional_fields: Literal["services.highest_impacting_priority", "total_impacted_count"] | None = Field(default=None, validation_alias="additional_fields[]", serialization_alias="additional_fields[]", description="Optional additional fields to include in the response: use 'services.highest_impacting_priority' to get the highest priority incident per service, or 'total_impacted_count' to get the total count of impacted resources per service.")
    ids: str | None = Field(default=None, validation_alias="ids[]", serialization_alias="ids[]", description="Optional list of specific Business Service IDs to retrieve impact information for. When provided, returns impact data for only these services regardless of impact level.")
class GetBusinessServiceImpactsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default value 'application/vnd.pagerduty+json;version=2' to request the current API version.")
class GetBusinessServiceImpactsRequest(StrictModel):
    """Retrieve the most impacted Business Services sorted by impact level, recency, and name. Without filtering by IDs, returns up to 200 of the highest-impact services; use the `ids[]` parameter to get impact data for a specific set of Business Services."""
    query: GetBusinessServiceImpactsRequestQuery | None = None
    header: GetBusinessServiceImpactsRequestHeader

# Operation: get_business_service_priority_thresholds
class GetBusinessServicePriorityThresholdsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="Content type and API version specification. Use the PagerDuty JSON media type with version 2 to ensure compatibility with the current API specification.")
class GetBusinessServicePriorityThresholdsRequest(StrictModel):
    """Retrieve the global priority threshold that determines when an Incident is considered to impact a Business Service. This threshold applies account-wide, affecting any Business Service that depends on the Service to which an Incident belongs."""
    header: GetBusinessServicePriorityThresholdsRequestHeader

# Operation: list_change_events
class ListChangeEventsRequestQuery(StrictModel):
    team_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="team_ids[]", serialization_alias="team_ids[]", description="Filter results to only include change events from specific teams. Provide an array of team IDs. Requires the `teams` ability on your account.")
    integration_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="integration_ids[]", serialization_alias="integration_ids[]", description="Filter results to only include change events from specific integrations. Provide an array of integration IDs.")
    since: str | None = Field(default=None, description="Start of the date range to search, specified as a UTC ISO 8601 datetime string (format: YYYY-MM-DDThh:mm:ssZ). Non-UTC datetimes will return an HTTP 400 error.", pattern='YYYY-MM-DDThh:mm:ssZ', json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="End of the date range to search, specified as a UTC ISO 8601 datetime string (format: YYYY-MM-DDThh:mm:ssZ). Non-UTC datetimes will return an HTTP 400 error.", pattern='YYYY-MM-DDThh:mm:ssZ', json_schema_extra={'format': 'date-time'})
class ListChangeEventsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Defaults to `application/vnd.pagerduty+json;version=2`.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request. Must be `application/json`.")
class ListChangeEventsRequest(StrictModel):
    """Retrieve all change events, optionally filtered by teams, integrations, or date range. Change events track modifications across your PagerDuty account."""
    query: ListChangeEventsRequestQuery | None = None
    header: ListChangeEventsRequestHeader

# Operation: send_change_event
class CreateChangeEventRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version. Must be set to the PagerDuty V2 JSON media type.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format. Must be JSON.")
class CreateChangeEventRequest(StrictModel):
    """Send a change event to PagerDuty to notify about infrastructure or application changes. This operation integrates with the V2 Events API for change event tracking."""
    header: CreateChangeEventRequestHeader

# Operation: get_change_event
class GetChangeEventRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Change Event to retrieve.")
class GetChangeEventRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body. Must be set to application/json.")
class GetChangeEventRequest(StrictModel):
    """Retrieve detailed information about a specific Change Event by its ID. Returns the full Change Event resource with all associated metadata."""
    path: GetChangeEventRequestPath
    header: GetChangeEventRequestHeader

# Operation: update_change_event
class UpdateChangeEventRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Change Event to update.")
class UpdateChangeEventRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default value to request PagerDuty API v2 response format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON.")
class UpdateChangeEventRequestBody(StrictModel):
    """The Change Event to be updated."""
    change_event: ChangeEvent = Field(default=..., description="The Change Event object containing the fields to update. Provide the properties you want to modify for the Change Event.")
class UpdateChangeEventRequest(StrictModel):
    """Update an existing Change Event in PagerDuty. Modify the properties of a specific Change Event using its ID."""
    path: UpdateChangeEventRequestPath
    header: UpdateChangeEventRequestHeader
    body: UpdateChangeEventRequestBody

# Operation: list_escalation_policies
class ListEscalationPoliciesRequestQuery(StrictModel):
    user_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="user_ids[]", serialization_alias="user_ids[]", description="Filter results to show only escalation policies where any of the specified users are targets. Provide as an array of user IDs.")
    team_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="team_ids[]", serialization_alias="team_ids[]", description="Filter results to only escalation policies related to the specified teams. Requires the account to have the teams ability. Provide as an array of team IDs.")
    include: Annotated[Literal["services", "teams", "targets"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Include additional related data in the response. Choose from services (related services), teams (team details), or targets (escalation targets).")
    sort_by: Literal["name", "name:asc", "name:desc"] | None = Field(default=None, description="Sort results by the specified field. Options are name (default, ascending), name:asc (ascending), or name:desc (descending).")
class ListEscalationPoliciesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to specify the API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request. Must be application/json.")
class ListEscalationPoliciesRequest(StrictModel):
    """Retrieve all escalation policies that define which users should be alerted and when. Optionally filter by users, teams, or include related service and target details."""
    query: ListEscalationPoliciesRequestQuery | None = None
    header: ListEscalationPoliciesRequestHeader

# Operation: create_escalation_policy
class CreateEscalationPolicyRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty v2 JSON format for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request body content type. Must be JSON format.")
    from_: str | None = Field(default=None, validation_alias="From", serialization_alias="From", description="Email address of the user making the request. Optional and used only for change tracking purposes. Must be a valid email address associated with your account.", json_schema_extra={'format': 'email'})
class CreateEscalationPolicyRequestBody(StrictModel):
    """The escalation policy to be created."""
    escalation_policy: EscalationPolicy = Field(default=..., description="The escalation policy configuration object. Must include at least one escalation rule that specifies which users to alert and at what intervals.")
class CreateEscalationPolicyRequest(StrictModel):
    """Creates a new escalation policy that defines which users should be alerted and when. At least one escalation rule must be provided in the request."""
    header: CreateEscalationPolicyRequestHeader
    body: CreateEscalationPolicyRequestBody

# Operation: get_escalation_policy
class GetEscalationPolicyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the escalation policy to retrieve.")
class GetEscalationPolicyRequestQuery(StrictModel):
    include: Annotated[Literal["services", "teams", "targets"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array of related resources to include in the response. Valid options are services, teams, or targets. Specify multiple values to include multiple resource types.")
class GetEscalationPolicyRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2 for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be application/json.")
class GetEscalationPolicyRequest(StrictModel):
    """Retrieve details about an escalation policy, including its rules that define which users should be alerted and when. Optionally include related services, teams, or escalation targets in the response."""
    path: GetEscalationPolicyRequestPath
    query: GetEscalationPolicyRequestQuery | None = None
    header: GetEscalationPolicyRequestHeader

# Operation: update_escalation_policy
class UpdateEscalationPolicyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the escalation policy to update.")
class UpdateEscalationPolicyRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be application/json.")
class UpdateEscalationPolicyRequestBody(StrictModel):
    """The escalation policy to be updated."""
    escalation_policy: EscalationPolicy = Field(default=..., description="The escalation policy object containing the updated configuration, including escalation rules and notification settings.")
class UpdateEscalationPolicyRequest(StrictModel):
    """Update an existing escalation policy to modify alert routing rules and user notification timing. Escalation policies define the sequence and timing of which users should be alerted during an incident."""
    path: UpdateEscalationPolicyRequestPath
    header: UpdateEscalationPolicyRequestHeader
    body: UpdateEscalationPolicyRequestBody

# Operation: delete_escalation_policy
class DeleteEscalationPolicyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the escalation policy to delete.")
class DeleteEscalationPolicyRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to JSON format.")
class DeleteEscalationPolicyRequest(StrictModel):
    """Permanently delete an escalation policy and its associated rules. The escalation policy must not be actively used by any services before deletion."""
    path: DeleteEscalationPolicyRequestPath
    header: DeleteEscalationPolicyRequestHeader

# Operation: list_escalation_policy_audit_records
class ListEscalationPolicyAuditRecordsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the escalation policy to retrieve audit records for.")
class ListEscalationPolicyAuditRecordsRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="The start of the date range for the audit search in ISO 8601 format. Defaults to 24 hours before the current time if not specified.", json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="The end of the date range for the audit search in ISO 8601 format. Defaults to the current time if not specified. Cannot be more than 31 days after the `since` parameter.", json_schema_extra={'format': 'date-time'})
class ListEscalationPolicyAuditRecordsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to `application/vnd.pagerduty+json;version=2` to specify the API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request. Must be `application/json`.")
class ListEscalationPolicyAuditRecordsRequest(StrictModel):
    """Retrieve audit records for a specific escalation policy, sorted by execution time from newest to oldest. Use cursor-based pagination to navigate through results."""
    path: ListEscalationPolicyAuditRecordsRequestPath
    query: ListEscalationPolicyAuditRecordsRequestQuery | None = None
    header: ListEscalationPolicyAuditRecordsRequestHeader

# Operation: list_event_orchestrations
class ListEventOrchestrationsRequestQuery(StrictModel):
    sort_by: Literal["name:asc", "name:desc", "routes:asc", "routes:desc", "created_at:asc", "created_at:desc"] | None = Field(default=None, description="Sort results by a specific field in ascending or descending order. Options include orchestration name, number of routes, or creation timestamp. Defaults to sorting by name in ascending order.")
class ListEventOrchestrationsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to the PagerDuty JSON API version 2 format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON.")
class ListEventOrchestrationsRequest(StrictModel):
    """Retrieve all Global Event Orchestrations configured on your account. Global Event Orchestrations enable you to define rules that automatically process and route incoming events to the appropriate services based on event content."""
    query: ListEventOrchestrationsRequestQuery | None = None
    header: ListEventOrchestrationsRequestHeader

# Operation: create_event_orchestration
class PostOrchestrationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to use the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request body content type. Must be application/json.")
class PostOrchestrationRequestBodyOrchestrationTeam(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the team that owns this orchestration. Optional; if not specified, the orchestration will not be assigned to a team.")
class PostOrchestrationRequestBodyOrchestration(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A human-readable description explaining the purpose and function of this orchestration. Optional; helps document the orchestration's role in your event processing workflow.")
    team: PostOrchestrationRequestBodyOrchestrationTeam | None = None
class PostOrchestrationRequestBody(StrictModel):
    orchestration: PostOrchestrationRequestBodyOrchestration | None = None
class PostOrchestrationRequest(StrictModel):
    """Create a Global Event Orchestration to define rules and routing logic for incoming events. Events ingested using the orchestration's routing key will be processed through Global Rules and then routed to the appropriate Service based on Router Rules."""
    header: PostOrchestrationRequestHeader
    body: PostOrchestrationRequestBody | None = None

# Operation: get_orchestration
class GetOrchestrationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Event Orchestration to retrieve.")
class GetOrchestrationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty JSON API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be application/json.")
class GetOrchestrationRequest(StrictModel):
    """Retrieve a Global Event Orchestration by ID. Global Event Orchestrations define Global Rules and Router Rules that process and route incoming events to the appropriate Service based on event content."""
    path: GetOrchestrationRequestPath
    header: GetOrchestrationRequestHeader

# Operation: delete_orchestration
class DeleteOrchestrationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Event Orchestration to delete.")
class DeleteOrchestrationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty API version 2 format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request content type as JSON.")
class DeleteOrchestrationRequest(StrictModel):
    """Delete a Global Event Orchestration. Once deleted, the orchestration's Routing Key can no longer be used to ingest events into PagerDuty."""
    path: DeleteOrchestrationRequestPath
    header: DeleteOrchestrationRequestHeader

# Operation: list_integrations_for_event_orchestration
class ListOrchestrationIntegrationsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Event Orchestration whose integrations you want to list.")
class ListOrchestrationIntegrationsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type for the request body. Must be application/json.")
class ListOrchestrationIntegrationsRequest(StrictModel):
    """Retrieve all integrations associated with a specific Event Orchestration. Use the routing keys from these integrations to send events to PagerDuty."""
    path: ListOrchestrationIntegrationsRequestPath
    header: ListOrchestrationIntegrationsRequestHeader

# Operation: create_integration_for_event_orchestration
class PostOrchestrationIntegrationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Event Orchestration to associate this integration with.")
class PostOrchestrationIntegrationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to application/vnd.pagerduty+json;version=2 to use the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format. Must be application/json.")
class PostOrchestrationIntegrationRequestBodyIntegration(StrictModel):
    label: str = Field(default=..., validation_alias="label", serialization_alias="label", description="A human-readable name for this integration. This label helps identify the integration's purpose within the Event Orchestration.")
class PostOrchestrationIntegrationRequestBody(StrictModel):
    integration: PostOrchestrationIntegrationRequestBodyIntegration
class PostOrchestrationIntegrationRequest(StrictModel):
    """Create a new integration for an Event Orchestration to generate a routing key for sending events to PagerDuty. Each integration provides a unique routing key that can be used to route events through the orchestration's rules."""
    path: PostOrchestrationIntegrationRequestPath
    header: PostOrchestrationIntegrationRequestHeader
    body: PostOrchestrationIntegrationRequestBody

# Operation: get_integration_for_orchestration
class GetOrchestrationIntegrationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the event orchestration.")
    integration_id: str = Field(default=..., description="The unique identifier of the integration to retrieve.")
class GetOrchestrationIntegrationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to specify the API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be application/json.")
class GetOrchestrationIntegrationRequest(StrictModel):
    """Retrieve a specific integration associated with an event orchestration. Use the routing key from the returned integration to send events to PagerDuty."""
    path: GetOrchestrationIntegrationRequestPath
    header: GetOrchestrationIntegrationRequestHeader

# Operation: update_event_orchestration_integration
class UpdateOrchestrationIntegrationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Event Orchestration to update.")
    integration_id: str = Field(default=..., description="The unique identifier of the Integration within the Event Orchestration.")
class UpdateOrchestrationIntegrationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to specify the API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be application/json.")
class UpdateOrchestrationIntegrationRequestBodyIntegration(StrictModel):
    label: str = Field(default=..., validation_alias="label", serialization_alias="label", description="A human-readable name for the Integration.")
class UpdateOrchestrationIntegrationRequestBody(StrictModel):
    integration: UpdateOrchestrationIntegrationRequestBodyIntegration
class UpdateOrchestrationIntegrationRequest(StrictModel):
    """Update an integration associated with an Event Orchestration. The integration's routing key can be used to send events to PagerDuty."""
    path: UpdateOrchestrationIntegrationRequestPath
    header: UpdateOrchestrationIntegrationRequestHeader
    body: UpdateOrchestrationIntegrationRequestBody

# Operation: delete_orchestration_integration
class DeleteOrchestrationIntegrationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Event Orchestration containing the integration to delete.")
    integration_id: str = Field(default=..., description="The unique identifier of the Integration to delete from the Event Orchestration.")
class DeleteOrchestrationIntegrationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be application/json.")
class DeleteOrchestrationIntegrationRequest(StrictModel):
    """Delete an integration from an Event Orchestration, which stops PagerDuty from accepting events sent to the associated Routing Key. Once deleted, all future events using that Routing Key will be dropped."""
    path: DeleteOrchestrationIntegrationRequestPath
    header: DeleteOrchestrationIntegrationRequestHeader

# Operation: move_integration_between_orchestrations
class MigrateOrchestrationIntegrationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the target Event Orchestration that will receive and process the Integration.")
class MigrateOrchestrationIntegrationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class MigrateOrchestrationIntegrationRequestBody(StrictModel):
    source_id: str = Field(default=..., description="The ID of the source Event Orchestration from which the Integration will be moved.")
    source_type: Literal["orchestration"] = Field(default=..., description="The type of the source object. Must be 'orchestration'.")
    integration_id: str = Field(default=..., description="The ID of the Integration to be moved to the target Event Orchestration.")
class MigrateOrchestrationIntegrationRequest(StrictModel):
    """Relocate an Integration and its Routing Key from a source Event Orchestration to a target Event Orchestration. Future events sent to the Integration's Routing Key will be processed by the target orchestration's rules."""
    path: MigrateOrchestrationIntegrationRequestPath
    header: MigrateOrchestrationIntegrationRequestHeader
    body: MigrateOrchestrationIntegrationRequestBody

# Operation: get_event_orchestration_global
class GetOrchPathGlobalRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Event Orchestration to retrieve global rules for.")
class GetOrchPathGlobalRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty JSON API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type for the request body. Must be application/json.")
class GetOrchPathGlobalRequest(StrictModel):
    """Retrieve the Global Orchestration rules for an Event Orchestration. Global rules evaluate all incoming events and can modify, enhance, and route events for further processing within the orchestration."""
    path: GetOrchPathGlobalRequestPath
    header: GetOrchPathGlobalRequestHeader

# Operation: get_event_orchestration_router
class GetOrchPathRouterRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Event Orchestration whose router configuration you want to retrieve.")
class GetOrchPathRouterRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty JSON API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to application/json.")
class GetOrchPathRouterRequest(StrictModel):
    """Retrieve the routing rules for an Event Orchestration. The router evaluates incoming events against a set of rules and directs them to the appropriate Service based on the first matching rule, or to a catch-all service if no rules match."""
    path: GetOrchPathRouterRequestPath
    header: GetOrchPathRouterRequestHeader

# Operation: get_unrouted_orchestration
class GetOrchPathUnroutedRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Event Orchestration to retrieve unrouted rules for.")
class GetOrchPathUnroutedRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be application/json.")
class GetOrchPathUnroutedRequest(StrictModel):
    """Retrieve the Unrouted Orchestration rules for an Event Orchestration, which processes events that don't match any rules in the Global Orchestration's Router. The Unrouted Orchestration evaluates these events against its rule sets and can modify, enhance, or route them for further processing."""
    path: GetOrchPathUnroutedRequestPath
    header: GetOrchPathUnroutedRequestHeader

# Operation: get_service_orchestration
class GetOrchPathServiceRequestPath(StrictModel):
    service_id: str = Field(default=..., description="The unique identifier of the service whose orchestration configuration should be retrieved.")
class GetOrchPathServiceRequestQuery(StrictModel):
    include: Annotated[Literal["migrated_metadata"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array of additional data models to include in the response. Specify 'migrated_metadata' to include migration-related metadata in the response.")
class GetOrchPathServiceRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to application/json.")
class GetOrchPathServiceRequest(StrictModel):
    """Retrieve the Event Orchestration configuration for a specific service. The orchestration defines a set of event rules that process and route incoming events through multiple rule sets for enhancement and conditional handling."""
    path: GetOrchPathServiceRequestPath
    query: GetOrchPathServiceRequestQuery | None = None
    header: GetOrchPathServiceRequestHeader

# Operation: get_service_orchestration_active_status
class GetOrchActiveStatusRequestPath(StrictModel):
    service_id: str = Field(default=..., description="The unique identifier of the service for which to retrieve the orchestration active status.")
class GetOrchActiveStatusRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to application/json.")
class GetOrchActiveStatusRequest(StrictModel):
    """Retrieve whether a Service Orchestration is active for a given service. When active (true), events are evaluated against the service orchestration path; when inactive (false), events are evaluated against the service ruleset instead."""
    path: GetOrchActiveStatusRequestPath
    header: GetOrchActiveStatusRequestHeader

# Operation: update_service_orchestration_active_status
class UpdateOrchActiveStatusRequestPath(StrictModel):
    service_id: str = Field(default=..., description="The unique identifier of the service whose orchestration active status should be updated.")
class UpdateOrchActiveStatusRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default value to request the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON.")
class UpdateOrchActiveStatusRequestBody(StrictModel):
    """Update Service Orchestration's active status."""
    active: bool | None = Field(default=None, description="Boolean flag indicating whether the service orchestration should be active (true) or inactive (false). When true, events are evaluated against the orchestration path; when false, they use the service ruleset instead.")
class UpdateOrchActiveStatusRequest(StrictModel):
    """Enable or disable event evaluation against a service orchestration path for a specific service. When active, events are evaluated using the orchestration path; when inactive, they fall back to the service ruleset."""
    path: UpdateOrchActiveStatusRequestPath
    header: UpdateOrchActiveStatusRequestHeader
    body: UpdateOrchActiveStatusRequestBody | None = None

# Operation: list_cache_variables_for_global_orchestration
class ListCacheVarOnGlobalOrchRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the event orchestration.")
class ListCacheVarOnGlobalOrchRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class ListCacheVarOnGlobalOrchRequest(StrictModel):
    """Retrieve all cache variables stored on a global event orchestration. Cache variables store event data that can be referenced in orchestration rules for conditions and actions."""
    path: ListCacheVarOnGlobalOrchRequestPath
    header: ListCacheVarOnGlobalOrchRequestHeader

# Operation: create_cache_variable_for_global_orchestration
class CreateCacheVarOnGlobalOrchRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the event orchestration where the cache variable will be created.")
class CreateCacheVarOnGlobalOrchRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format. Must be application/json.")
class CreateCacheVarOnGlobalOrchRequestBody(StrictModel):
    cache_variable: OrchestrationCacheVariableRecentValue | OrchestrationCacheVariableTriggerEventCount | OrchestrationCacheVariableExternalData = Field(default=..., description="The cache variable object containing the variable name, initial value, and other configuration properties.")
class CreateCacheVarOnGlobalOrchRequest(StrictModel):
    """Create a cache variable on a global event orchestration to store event data for use in orchestration rules, conditions, and actions."""
    path: CreateCacheVarOnGlobalOrchRequestPath
    header: CreateCacheVarOnGlobalOrchRequestHeader
    body: CreateCacheVarOnGlobalOrchRequestBody

# Operation: get_cache_variable_for_global_orchestration
class GetCacheVarOnGlobalOrchRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the event orchestration containing the cache variable.")
    cache_variable_id: str = Field(default=..., description="The unique identifier of the cache variable to retrieve.")
class GetCacheVarOnGlobalOrchRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be JSON format.")
class GetCacheVarOnGlobalOrchRequest(StrictModel):
    """Retrieve a specific cache variable from a global event orchestration. Cache variables store event data that can be referenced in orchestration rules for conditions and actions."""
    path: GetCacheVarOnGlobalOrchRequestPath
    header: GetCacheVarOnGlobalOrchRequestHeader

# Operation: update_cache_variable_for_global_orchestration
class UpdateCacheVarOnGlobalOrchRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the event orchestration containing the cache variable.")
    cache_variable_id: str = Field(default=..., description="The unique identifier of the cache variable to update.")
class UpdateCacheVarOnGlobalOrchRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API version header. Must be set to application/vnd.pagerduty+json;version=2 to specify the API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type of the request body. Must be application/json.")
class UpdateCacheVarOnGlobalOrchRequestBody(StrictModel):
    cache_variable: OrchestrationCacheVariableRecentValue | OrchestrationCacheVariableTriggerEventCount | OrchestrationCacheVariableExternalData = Field(default=..., description="The cache variable object containing the updated configuration and values.")
class UpdateCacheVarOnGlobalOrchRequest(StrictModel):
    """Update a cache variable on a global event orchestration. Cache variables store event data that can be referenced in orchestration rules for conditions and actions."""
    path: UpdateCacheVarOnGlobalOrchRequestPath
    header: UpdateCacheVarOnGlobalOrchRequestHeader
    body: UpdateCacheVarOnGlobalOrchRequestBody

# Operation: delete_cache_variable_from_global_orchestration
class DeleteCacheVarOnGlobalOrchRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the event orchestration containing the cache variable to delete.")
    cache_variable_id: str = Field(default=..., description="The unique identifier of the cache variable to remove from the orchestration.")
class DeleteCacheVarOnGlobalOrchRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to specify the API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON.")
class DeleteCacheVarOnGlobalOrchRequest(StrictModel):
    """Remove a cache variable from a global event orchestration. Cache variables store event data that can be referenced in orchestration rules for conditions and actions."""
    path: DeleteCacheVarOnGlobalOrchRequestPath
    header: DeleteCacheVarOnGlobalOrchRequestHeader

# Operation: get_external_data_cache_variable_data
class GetExternalDataCacheVarDataOnGlobalOrchRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Event Orchestration containing the Cache Variable.")
    cache_variable_id: str = Field(default=..., description="The unique identifier of the Cache Variable to retrieve data from.")
class GetExternalDataCacheVarDataOnGlobalOrchRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2 for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type for the request body. Must be application/json.")
class GetExternalDataCacheVarDataOnGlobalOrchRequest(StrictModel):
    """Retrieve the stored data for an external data type Cache Variable on a Global Event Orchestration. External data Cache Variables store string, number, or boolean values that can be referenced in Event Orchestration rules and conditions."""
    path: GetExternalDataCacheVarDataOnGlobalOrchRequestPath
    header: GetExternalDataCacheVarDataOnGlobalOrchRequestHeader

# Operation: update_cache_variable_external_data
class UpdateExternalDataCacheVarDataOnGlobalOrchRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the event orchestration containing the cache variable.")
    cache_variable_id: str = Field(default=..., description="The unique identifier of the cache variable to update.")
class UpdateExternalDataCacheVarDataOnGlobalOrchRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default value of application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be application/json.")
class UpdateExternalDataCacheVarDataOnGlobalOrchRequestBody(StrictModel):
    """The updated data for an `external_data` type Cache Variable for this Event Orchestration."""
    cache_variable_data: str = Field(default=..., description="The string value to store in the cache variable. Use this parameter when the cache variable is configured with data_type of string.")
class UpdateExternalDataCacheVarDataOnGlobalOrchRequest(StrictModel):
    """Update the data value stored in an external data type cache variable on a global event orchestration. The updated value can then be referenced in event orchestration rules and conditions."""
    path: UpdateExternalDataCacheVarDataOnGlobalOrchRequestPath
    header: UpdateExternalDataCacheVarDataOnGlobalOrchRequestHeader
    body: UpdateExternalDataCacheVarDataOnGlobalOrchRequestBody

# Operation: delete_external_data_cache_variable_data
class DeleteExternalDataCacheVarDataOnGlobalOrchRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Event Orchestration containing the Cache Variable.")
    cache_variable_id: str = Field(default=..., description="The unique identifier of the Cache Variable whose data should be deleted.")
class DeleteExternalDataCacheVarDataOnGlobalOrchRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be application/json.")
class DeleteExternalDataCacheVarDataOnGlobalOrchRequest(StrictModel):
    """Delete stored data for an external data type Cache Variable on a Global Event Orchestration. This removes the cached values that were previously set via the dedicated API endpoint."""
    path: DeleteExternalDataCacheVarDataOnGlobalOrchRequestPath
    header: DeleteExternalDataCacheVarDataOnGlobalOrchRequestHeader

# Operation: list_cache_variables_for_service_orchestration
class ListCacheVarOnServiceOrchRequestPath(StrictModel):
    service_id: str = Field(default=..., description="The unique identifier of the service whose cache variables you want to list.")
class ListCacheVarOnServiceOrchRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request content type. Must be set to JSON format.")
class ListCacheVarOnServiceOrchRequest(StrictModel):
    """Retrieve all cache variables configured for a service's event orchestration. Cache variables store event data that can be referenced in orchestration rules for conditions and actions."""
    path: ListCacheVarOnServiceOrchRequestPath
    header: ListCacheVarOnServiceOrchRequestHeader

# Operation: create_cache_variable_for_service_orchestration
class CreateCacheVarOnServiceOrchRequestPath(StrictModel):
    service_id: str = Field(default=..., description="The unique identifier of the service for which to create the cache variable.")
class CreateCacheVarOnServiceOrchRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2 for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type of the request body. Must be application/json.")
class CreateCacheVarOnServiceOrchRequestBody(StrictModel):
    cache_variable: OrchestrationCacheVariableRecentValue | OrchestrationCacheVariableTriggerEventCount | OrchestrationCacheVariableExternalData = Field(default=..., description="The cache variable configuration object containing the variable definition and settings.")
class CreateCacheVarOnServiceOrchRequest(StrictModel):
    """Create a cache variable for a service event orchestration to store event data that can be referenced in orchestration rules for conditions and actions."""
    path: CreateCacheVarOnServiceOrchRequestPath
    header: CreateCacheVarOnServiceOrchRequestHeader
    body: CreateCacheVarOnServiceOrchRequestBody

# Operation: get_cache_variable_for_service_orchestration
class GetCacheVarOnServiceOrchRequestPath(StrictModel):
    service_id: str = Field(default=..., description="The unique identifier of the service containing the event orchestration.")
    cache_variable_id: str = Field(default=..., description="The unique identifier of the cache variable to retrieve.")
class GetCacheVarOnServiceOrchRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use application/vnd.pagerduty+json;version=2 for the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type for the request body. Must be application/json.")
class GetCacheVarOnServiceOrchRequest(StrictModel):
    """Retrieve a specific cache variable from a service's event orchestration. Cache variables store event data that can be referenced in orchestration rules for conditions and actions."""
    path: GetCacheVarOnServiceOrchRequestPath
    header: GetCacheVarOnServiceOrchRequestHeader

# Operation: update_cache_variable_for_service_orchestration
class UpdateCacheVarOnServiceOrchRequestPath(StrictModel):
    service_id: str = Field(default=..., description="The unique identifier of the service containing the event orchestration.")
    cache_variable_id: str = Field(default=..., description="The unique identifier of the cache variable to update.")
class UpdateCacheVarOnServiceOrchRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type of the request body. Must be application/json.")
class UpdateCacheVarOnServiceOrchRequestBody(StrictModel):
    cache_variable: OrchestrationCacheVariableRecentValue | OrchestrationCacheVariableTriggerEventCount | OrchestrationCacheVariableExternalData = Field(default=..., description="The cache variable object containing the updated configuration and values.")
class UpdateCacheVarOnServiceOrchRequest(StrictModel):
    """Update a cache variable on a service event orchestration. Cache variables store event data that can be referenced in orchestration rules for conditions and actions."""
    path: UpdateCacheVarOnServiceOrchRequestPath
    header: UpdateCacheVarOnServiceOrchRequestHeader
    body: UpdateCacheVarOnServiceOrchRequestBody

# Operation: delete_cache_variable_for_service_orchestration
class DeleteCacheVarOnServiceOrchRequestPath(StrictModel):
    service_id: str = Field(default=..., description="The unique identifier of the service whose event orchestration contains the cache variable to delete.")
    cache_variable_id: str = Field(default=..., description="The unique identifier of the cache variable to delete from the service's event orchestration.")
class DeleteCacheVarOnServiceOrchRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to use the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON.")
class DeleteCacheVarOnServiceOrchRequest(StrictModel):
    """Remove a cache variable from a service's event orchestration. Cache variables store event data that can be referenced in orchestration rules for conditions and actions."""
    path: DeleteCacheVarOnServiceOrchRequestPath
    header: DeleteCacheVarOnServiceOrchRequestHeader

# Operation: get_cache_variable_data_on_service_orchestration
class GetExternalDataCacheVarDataOnServiceOrchRequestPath(StrictModel):
    service_id: str = Field(default=..., description="The unique identifier of the service containing the cache variable.")
    cache_variable_id: str = Field(default=..., description="The unique identifier of the cache variable to retrieve data for.")
class GetExternalDataCacheVarDataOnServiceOrchRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type for the request body. Must be application/json.")
class GetExternalDataCacheVarDataOnServiceOrchRequest(StrictModel):
    """Retrieve the stored data for an external data type cache variable on a service event orchestration. External data cache variables store string, number, or boolean values that can be referenced in event orchestration rules and conditions."""
    path: GetExternalDataCacheVarDataOnServiceOrchRequestPath
    header: GetExternalDataCacheVarDataOnServiceOrchRequestHeader

# Operation: update_cache_variable_data
class UpdateExternalDataCacheVarDataOnServiceOrchRequestPath(StrictModel):
    service_id: str = Field(default=..., description="The unique identifier of the service containing the cache variable.")
    cache_variable_id: str = Field(default=..., description="The unique identifier of the cache variable to update.")
class UpdateExternalDataCacheVarDataOnServiceOrchRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be JSON format.")
class UpdateExternalDataCacheVarDataOnServiceOrchRequestBody(StrictModel):
    """The updated data for an `external_data` type Cache Variable for this Event Orchestration."""
    cache_variable_data: str = Field(default=..., description="The string value to store in the external data cache variable. Can be any string value used by Event Orchestration rules.")
class UpdateExternalDataCacheVarDataOnServiceOrchRequest(StrictModel):
    """Update the data value for an external data type cache variable on a service event orchestration. The stored value can be used in conditions and actions within Event Orchestration rules."""
    path: UpdateExternalDataCacheVarDataOnServiceOrchRequestPath
    header: UpdateExternalDataCacheVarDataOnServiceOrchRequestHeader
    body: UpdateExternalDataCacheVarDataOnServiceOrchRequestBody

# Operation: delete_cache_variable_data_on_service_orchestration
class DeleteExternalDataCacheVarDataOnServiceOrchRequestPath(StrictModel):
    service_id: str = Field(default=..., description="The unique identifier of the service containing the cache variable.")
    cache_variable_id: str = Field(default=..., description="The unique identifier of the cache variable whose data should be deleted.")
class DeleteExternalDataCacheVarDataOnServiceOrchRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class DeleteExternalDataCacheVarDataOnServiceOrchRequest(StrictModel):
    """Delete stored data for an external data type cache variable on a service event orchestration. This removes the cached string, number, or boolean value that was previously stored via the cache variable API."""
    path: DeleteExternalDataCacheVarDataOnServiceOrchRequestPath
    header: DeleteExternalDataCacheVarDataOnServiceOrchRequestHeader

# Operation: list_event_orchestration_enablements
class ListEventOrchestrationFeatureEnablementsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Event Orchestration for which to list feature enablements.")
class ListEventOrchestrationFeatureEnablementsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and structure. Defaults to PagerDuty API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to JSON format.")
class ListEventOrchestrationFeatureEnablementsRequest(StrictModel):
    """Retrieve all feature enablement settings for a specific Event Orchestration. Currently supports the `aiops` enablement, which is enabled by default for accounts with the AIOps product addon. A warning will be returned if the account lacks AIOps entitlement."""
    path: ListEventOrchestrationFeatureEnablementsRequestPath
    header: ListEventOrchestrationFeatureEnablementsRequestHeader

# Operation: update_event_orchestration_feature_enablement
class UpdateEventOrchestrationFeatureEnablementsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Event Orchestration to update.")
    feature_name: Literal["aiops"] = Field(default=..., description="The feature addon to enable or disable. Currently only 'aiops' is supported.")
class UpdateEventOrchestrationFeatureEnablementsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default value for standard PagerDuty API v2 responses.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be JSON.")
class UpdateEventOrchestrationFeatureEnablementsRequestBodyEnablement(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Set to true to enable the feature addon, or false to disable it.")
class UpdateEventOrchestrationFeatureEnablementsRequestBody(StrictModel):
    """The feature enablement setting to apply."""
    enablement: UpdateEventOrchestrationFeatureEnablementsRequestBodyEnablement
class UpdateEventOrchestrationFeatureEnablementsRequest(StrictModel):
    """Enable or disable a feature addon for an Event Orchestration. Currently supports the AIOps addon. Note: if your account lacks AIOps entitlement, the setting will update but return a warning."""
    path: UpdateEventOrchestrationFeatureEnablementsRequestPath
    header: UpdateEventOrchestrationFeatureEnablementsRequestHeader
    body: UpdateEventOrchestrationFeatureEnablementsRequestBody

# Operation: list_extension_schemas
class ListExtensionSchemasRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version. Must be set to application/vnd.pagerduty+json;version=2 to request the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request content type. Must be application/json.")
class ListExtensionSchemasRequest(StrictModel):
    """Retrieve all available extension schemas that define outbound extension types (such as Generic Webhook, Slack, ServiceNow) supported by PagerDuty."""
    header: ListExtensionSchemasRequestHeader

# Operation: get_extension_schema
class GetExtensionSchemaRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the extension schema to retrieve.")
class GetExtensionSchemaRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type for the request body. Must be application/json.")
class GetExtensionSchemaRequest(StrictModel):
    """Retrieve details about a specific PagerDuty extension vendor (such as Generic Webhook, Slack, or ServiceNow). Extension schemas define the structure and capabilities of outbound extensions."""
    path: GetExtensionSchemaRequestPath
    header: GetExtensionSchemaRequestHeader

# Operation: list_extensions
class ListExtensionsRequestQuery(StrictModel):
    extension_object_id: str | None = Field(default=None, description="Filter results to extensions associated with a specific extension object by its ID.")
    extension_schema_id: str | None = Field(default=None, description="Filter results to extensions using a specific extension schema (vendor) by its ID.")
    include: Annotated[Literal["extension_objects", "extension_schemas"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Array of related resources to include in the response. Specify 'extension_objects' to include extension object details or 'extension_schemas' to include schema definitions.")
class ListExtensionsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Defaults to version 2 of the PagerDuty JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class ListExtensionsRequest(StrictModel):
    """Retrieve a list of extensions attached to services. Extensions are representations of Extension Schema objects that extend service functionality. Use optional filters to narrow results by extension object or schema, and include related details as needed."""
    query: ListExtensionsRequestQuery | None = None
    header: ListExtensionsRequestHeader

# Operation: create_extension
class CreateExtensionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to application/vnd.pagerduty+json;version=2 to use the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format. Must be application/json.")
class CreateExtensionRequestBody(StrictModel):
    """The extension to be created"""
    extension: Extension = Field(default=..., description="The Extension object to create, containing the configuration and schema details for the new extension.")
class CreateExtensionRequest(StrictModel):
    """Create a new Extension that can be attached to a Service. Extensions are representations of Extension Schema objects used to extend Service functionality."""
    header: CreateExtensionRequestHeader
    body: CreateExtensionRequestBody

# Operation: get_extension
class GetExtensionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the extension to retrieve.")
class GetExtensionRequestQuery(StrictModel):
    include: Annotated[Literal["extension_schemas", "extension_objects", "temporarily_disabled"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array of related resources to include in the response. Choose from: extension_schemas (the schema definition), extension_objects (associated objects), or temporarily_disabled (disabled status information).")
class GetExtensionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use application/vnd.pagerduty+json;version=2 to specify the API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class GetExtensionRequest(StrictModel):
    """Retrieve details about a specific extension attached to a service. Extensions are representations of Extension Schema objects that define how services integrate with external systems."""
    path: GetExtensionRequestPath
    query: GetExtensionRequestQuery | None = None
    header: GetExtensionRequestHeader

# Operation: update_extension
class UpdateExtensionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the extension to update.")
class UpdateExtensionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default value to request API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON.")
class UpdateExtensionRequestBody(StrictModel):
    """The extension to be updated."""
    extension: Extension = Field(default=..., description="The extension object containing the fields to update.")
class UpdateExtensionRequest(StrictModel):
    """Update an existing extension attached to a service. Extensions are representations of Extension Schema objects that customize service behavior."""
    path: UpdateExtensionRequestPath
    header: UpdateExtensionRequestHeader
    body: UpdateExtensionRequestBody

# Operation: delete_extension
class DeleteExtensionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the extension to delete.")
class DeleteExtensionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default value to request the current API version (version 2).")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request content type. Must be set to application/json.")
class DeleteExtensionRequest(StrictModel):
    """Permanently delete an extension by ID. Once deleted, the extension will no longer be accessible in the web UI and cannot be used for creating new incidents."""
    path: DeleteExtensionRequestPath
    header: DeleteExtensionRequestHeader

# Operation: enable_extension
class EnableExtensionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the extension to enable.")
class EnableExtensionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to application/json.")
class EnableExtensionRequest(StrictModel):
    """Enable a temporarily disabled extension attached to a service. The extension will become active and functional again."""
    path: EnableExtensionRequestPath
    header: EnableExtensionRequestHeader

# Operation: delete_incident_workflow
class DeleteIncidentWorkflowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Incident Workflow to delete.")
class DeleteIncidentWorkflowRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to JSON format.")
class DeleteIncidentWorkflowRequest(StrictModel):
    """Permanently delete an Incident Workflow by its ID. This removes the workflow and all its associated Steps, Triggers, and automated Actions."""
    path: DeleteIncidentWorkflowRequestPath
    header: DeleteIncidentWorkflowRequestHeader

# Operation: create_incident_workflow_instance
class CreateIncidentWorkflowInstanceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident workflow to execute.")
class CreateIncidentWorkflowInstanceRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="The API version header for response formatting. Defaults to version 2 of the PagerDuty JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The request body content type. Must be JSON format.")
class CreateIncidentWorkflowInstanceRequestBodyIncidentWorkflowInstanceIncident(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident on which to execute the workflow.")
class CreateIncidentWorkflowInstanceRequestBodyIncidentWorkflowInstance(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="An optional identifier to distinguish between multiple executions of the same workflow, useful for tracking and auditing purposes.")
    incident: CreateIncidentWorkflowInstanceRequestBodyIncidentWorkflowInstanceIncident
class CreateIncidentWorkflowInstanceRequestBody(StrictModel):
    incident_workflow_instance: CreateIncidentWorkflowInstanceRequestBodyIncidentWorkflowInstance
class CreateIncidentWorkflowInstanceRequest(StrictModel):
    """Trigger an instance of an incident workflow to execute its configured steps and automated actions on a specific incident. This starts a new workflow execution sequence for the given incident."""
    path: CreateIncidentWorkflowInstanceRequestPath
    header: CreateIncidentWorkflowInstanceRequestHeader
    body: CreateIncidentWorkflowInstanceRequestBody

# Operation: list_incident_workflow_actions
class ListIncidentWorkflowActionsRequestQuery(StrictModel):
    keyword: str | None = Field(default=None, description="Filter actions by a specific keyword tag (e.g., 'slack'). When provided, only actions tagged with this keyword are returned.")
class ListIncidentWorkflowActionsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and schema version. Must be set to the PagerDuty API v2 content type.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON. Required for API compatibility.")
class ListIncidentWorkflowActionsRequest(StrictModel):
    """Retrieve a list of available incident workflow actions. Optionally filter actions by keyword tag to find specific action types."""
    query: ListIncidentWorkflowActionsRequestQuery | None = None
    header: ListIncidentWorkflowActionsRequestHeader

# Operation: get_incident_workflow_action
class GetIncidentWorkflowActionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Incident Workflow Action to retrieve.")
class GetIncidentWorkflowActionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to application/json.")
class GetIncidentWorkflowActionRequest(StrictModel):
    """Retrieve a specific Incident Workflow Action by its ID. Returns the action details including its configuration and properties within an incident workflow."""
    path: GetIncidentWorkflowActionRequestPath
    header: GetIncidentWorkflowActionRequestHeader

# Operation: list_incident_workflow_triggers
class ListIncidentWorkflowTriggersRequestQuery(StrictModel):
    workflow_id: str | None = Field(default=None, description="Filter to show only triggers configured to start a specific workflow. Useful for discovering all services and incidents associated with a given workflow.")
    incident_id: str | None = Field(default=None, description="Filter to show only triggers configured on the service of a specific incident. Useful for finding manual triggers available for that incident. Cannot be used together with `service_id`.")
    service_id: str | None = Field(default=None, description="Filter to show only triggers configured for a specific service. Useful for discovering all workflows that can be triggered for incidents in that service. Cannot be used together with `incident_id`.")
    trigger_type: Literal["manual", "conditional", "incident_type"] | None = Field(default=None, description="Filter to show only triggers of a specific type: 'manual' for user-initiated triggers, 'conditional' for automatically triggered workflows, or 'incident_type' for type-based triggers.")
    workflow_name_contains: str | None = Field(default=None, description="Filter to show only triggers configured to start workflows whose names contain the provided text. Matching is case-sensitive substring search.")
    sort_by: Literal["workflow_id", "workflow_id asc", "workflow_id desc", "workflow_name", "workflow_name asc", "workflow_name desc"] | None = Field(default=None, description="Sort results by workflow ID or workflow name in ascending or descending order. If not specified, results are returned in default order.")
class ListIncidentWorkflowTriggersRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="HTTP header specifying the API version. Must be set to 'application/vnd.pagerduty+json;version=2' for this operation.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="HTTP header specifying the request body format. Must be 'application/json'.")
class ListIncidentWorkflowTriggersRequest(StrictModel):
    """Retrieve a list of incident workflow triggers, optionally filtered by workflow, service, incident, trigger type, or workflow name. Use this to discover which workflows are configured to start automatically or manually for specific services or incidents."""
    query: ListIncidentWorkflowTriggersRequestQuery | None = None
    header: ListIncidentWorkflowTriggersRequestHeader

# Operation: delete_incident_workflow_trigger
class DeleteIncidentWorkflowTriggerRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Incident Workflow Trigger to delete.")
class DeleteIncidentWorkflowTriggerRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON.")
class DeleteIncidentWorkflowTriggerRequest(StrictModel):
    """Permanently delete an existing Incident Workflow Trigger by its ID. This action cannot be undone."""
    path: DeleteIncidentWorkflowTriggerRequestPath
    header: DeleteIncidentWorkflowTriggerRequestHeader

# Operation: add_service_to_incident_workflow_trigger
class AssociateServiceToIncidentWorkflowTriggerRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Incident Workflow Trigger to associate the service with.")
class AssociateServiceToIncidentWorkflowTriggerRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API version header for response formatting. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request body content type. Must be JSON format.")
class AssociateServiceToIncidentWorkflowTriggerRequestBodyService(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the Service to associate with the trigger.")
class AssociateServiceToIncidentWorkflowTriggerRequestBody(StrictModel):
    service: AssociateServiceToIncidentWorkflowTriggerRequestBodyService | None = None
class AssociateServiceToIncidentWorkflowTriggerRequest(StrictModel):
    """Associate a Service with an existing Incident Workflow Trigger to enable the trigger to act on incidents for that service."""
    path: AssociateServiceToIncidentWorkflowTriggerRequestPath
    header: AssociateServiceToIncidentWorkflowTriggerRequestHeader
    body: AssociateServiceToIncidentWorkflowTriggerRequestBody | None = None

# Operation: remove_service_from_incident_workflow_trigger
class DeleteServiceFromIncidentWorkflowTriggerRequestPath(StrictModel):
    trigger_id: str = Field(default=..., description="The unique identifier of the incident workflow trigger from which the service will be removed.")
    service_id: str = Field(default=..., description="The unique identifier of the service to be dissociated from the trigger.")
class DeleteServiceFromIncidentWorkflowTriggerRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to application/vnd.pagerduty+json;version=2 to use the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON.")
class DeleteServiceFromIncidentWorkflowTriggerRequest(StrictModel):
    """Remove a service from an incident workflow trigger, effectively dissociating them. This operation requires write access to incident workflows."""
    path: DeleteServiceFromIncidentWorkflowTriggerRequestPath
    header: DeleteServiceFromIncidentWorkflowTriggerRequestHeader

# Operation: list_incidents
class ListIncidentsRequestQuery(StrictModel):
    date_range: Literal["all"] | None = Field(default=None, description="When set to 'all', ignores the since and until date range parameters and their defaults to retrieve all incidents without time constraints.")
    incident_key: str | None = Field(default=None, description="Filter by incident de-duplication key. For incidents with child alerts, this matches against the alert_key of associated alerts rather than a direct incident key.")
    service_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="service_ids[]", serialization_alias="service_ids[]", description="Filter results to incidents associated with one or more specific services. Accepts an array of service IDs.")
    team_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="team_ids[]", serialization_alias="team_ids[]", description="Filter results to incidents related to one or more teams. Requires the account to have the teams ability. Accepts an array of team IDs.")
    user_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="user_ids[]", serialization_alias="user_ids[]", description="Filter to incidents currently assigned to one or more users. Accepts an array of user IDs. Note: Only returns incidents with triggered or acknowledged status, as resolved incidents are not assigned to users.")
    urgencies: Annotated[Literal["high", "low"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="urgencies[]", serialization_alias="urgencies[]", description="Filter by incident urgency level. Valid values are 'high' or 'low'. Defaults to all urgencies. Requires the account to have the urgencies ability.")
    time_zone: str | None = Field(default=None, description="Specify the time zone for rendering date/time results in responses. Defaults to the account's configured time zone. Use IANA time zone format (tzinfo).", json_schema_extra={'format': 'tzinfo'})
    statuses: Annotated[Literal["triggered", "acknowledged", "resolved"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="statuses[]", serialization_alias="statuses[]", description="Filter by incident status. Valid values are 'triggered', 'acknowledged', or 'resolved'. Pass multiple times to filter by multiple statuses.")
    sort_by: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, description="Sort results by one or two fields with direction. Format each field as 'field:direction' (e.g., 'incident_number:asc'). Valid fields are incident_number, created_at, resolved_at, or urgency. Separate multiple sorts with commas. Defaults to ascending order. Sorting by urgency requires the urgencies ability.", max_length=2)
    include: Annotated[Literal["acknowledgers", "agents", "assignees", "conference_bridge", "escalation_policies", "first_trigger_log_entries", "priorities", "services", "teams", "users"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Include additional related data in the response. Valid options include acknowledgers, agents, assignees, conference_bridge, escalation_policies, first_trigger_log_entries, priorities, services, teams, and users.")
    since: str | None = Field(default=None, description="Start of the date range for searching incidents. Maximum searchable range is 6 months; defaults to 1 month if not specified. Use ISO 8601 format.")
    until: str | None = Field(default=None, description="End of the date range for searching incidents. Maximum searchable range is 6 months; defaults to 1 month if not specified. Use ISO 8601 format.")
class ListIncidentsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="HTTP Accept header for API versioning. Must be set to 'application/vnd.pagerduty+json;version=2'.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="HTTP Content-Type header specifying request body format. Must be 'application/json'.")
class ListIncidentsRequest(StrictModel):
    """Retrieve a list of incidents with optional filtering by service, team, user assignment, status, and urgency. Incidents represent problems or issues requiring resolution and can be filtered across various dimensions and sorted by multiple fields."""
    query: ListIncidentsRequestQuery | None = None
    header: ListIncidentsRequestHeader

# Operation: create_incident
class CreateIncidentRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to specify the API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request body content type. Must be application/json.")
    from_: str = Field(default=..., validation_alias="From", serialization_alias="From", description="Email address of a valid user associated with the account making the request. Used to identify the incident creator.", json_schema_extra={'format': 'email'})
class CreateIncidentRequestBodyIncidentBody(StrictModel):
    details: dict[str, Any] | None = Field(default=None, validation_alias="details", serialization_alias="details", description="Additional structured data providing context or metadata about the incident. Useful for storing custom fields or supplementary information.")
class CreateIncidentRequestBodyIncidentConferenceBridge(StrictModel):
    conference_number: str | None = Field(default=None, validation_alias="conference_number", serialization_alias="conference_number", description="The phone number for the conference bridge, formatted with commas representing one-second waits and pound sign (#) completing access code input (e.g., +1 415-555-1212,,,,1234#).")
    conference_url: str | None = Field(default=None, validation_alias="conference_url", serialization_alias="conference_url", description="A URL for the conference bridge, such as a web conference link or Slack channel. Must be a valid URL format.", json_schema_extra={'format': 'url'})
class CreateIncidentRequestBodyIncident(StrictModel):
    type_: Literal["incident"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'incident'.")
    title: str = Field(default=..., validation_alias="title", serialization_alias="title", description="A concise description of the incident's nature, symptoms, cause, or effect. This is the primary human-readable summary of the problem.")
    service: ServiceReference = Field(default=..., validation_alias="service", serialization_alias="service", description="The service associated with this incident. This determines which service the incident belongs to and affects escalation routing.")
    priority: PriorityReference | None = Field(default=None, validation_alias="priority", serialization_alias="priority", description="The priority level of the incident. Helps determine urgency and response requirements.")
    urgency: Literal["high", "low"] | None = Field(default=None, validation_alias="urgency", serialization_alias="urgency", description="The urgency level of the incident. Must be either 'high' or 'low', affecting notification and escalation behavior.")
    incident_key: str | None = Field(default=None, validation_alias="incident_key", serialization_alias="incident_key", description="A unique identifier for the incident within its service. Subsequent requests with the same service and incident_key will be rejected if an open incident already exists with that key, preventing duplicate incidents.")
    assignments: list[CreateIncidentBodyIncidentAssignmentsItem] | None = Field(default=None, validation_alias="assignments", serialization_alias="assignments", description="List of users to assign the incident to. Cannot be used together with an escalation policy. Assignments determine who is initially responsible for the incident.")
    escalation_policy: EscalationPolicyReference | None = Field(default=None, validation_alias="escalation_policy", serialization_alias="escalation_policy", description="The escalation policy to apply to the incident. Determines the chain of escalation if the incident is not acknowledged. Cannot be specified if assignments are provided.")
    body: CreateIncidentRequestBodyIncidentBody | None = None
    conference_bridge: CreateIncidentRequestBodyIncidentConferenceBridge | None = None
class CreateIncidentRequestBody(StrictModel):
    incident: CreateIncidentRequestBodyIncident
class CreateIncidentRequest(StrictModel):
    """Create an incident synchronously to represent a problem or issue that needs to be addressed, without requiring a corresponding event from a monitoring service. Requires a valid user email and service association."""
    header: CreateIncidentRequestHeader
    body: CreateIncidentRequestBody

# Operation: update_incidents
class UpdateIncidentsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version. Must be set to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type of the request body. Must be application/json.")
    from_: str = Field(default=..., validation_alias="From", serialization_alias="From", description="Email address of a valid user associated with the account making the request. This identifies who is performing the incident updates.", json_schema_extra={'format': 'email'})
class UpdateIncidentsRequestBody(StrictModel):
    incidents: list[UpdateIncidentsBodyIncidentsItem] = Field(default=..., description="Array of incident objects to update, each containing the incident ID and the parameters to modify (status, assignee, escalation policy, etc.). Maximum of 250 incidents per request; exceeding this limit will return a 413 error.")
class UpdateIncidentsRequest(StrictModel):
    """Update the status of one or more incidents by acknowledging, resolving, escalating, or reassigning them. Supports batch operations on up to 250 incidents per request."""
    header: UpdateIncidentsRequestHeader
    body: UpdateIncidentsRequestBody

# Operation: get_incident
class GetIncidentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to retrieve.")
class GetIncidentRequestQuery(StrictModel):
    include: Annotated[Literal["acknowledgers", "agents", "assignees", "conference_bridge", "custom_fields", "escalation_policies", "first_trigger_log_entries", "priorities", "services", "teams", "users"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array of related resources to include in the response. Choose from: acknowledgers, agents, assignees, conference_bridge, custom_fields, escalation_policies, first_trigger_log_entries, priorities, services, teams, or users.")
class GetIncidentRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Defaults to PagerDuty API version 2 (application/vnd.pagerduty+json;version=2).")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class GetIncidentRequest(StrictModel):
    """Retrieve detailed information about a specific incident by its ID or incident number. An incident represents a problem or issue that requires resolution."""
    path: GetIncidentRequestPath
    query: GetIncidentRequestQuery | None = None
    header: GetIncidentRequestHeader

# Operation: update_incident
class UpdateIncidentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to update.")
class UpdateIncidentRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API version header. Use the default PagerDuty v2 JSON format for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
    from_: str = Field(default=..., validation_alias="From", serialization_alias="From", description="Email address of the authenticated user making this request. Must be a valid user associated with your account.", json_schema_extra={'format': 'email'})
class UpdateIncidentRequestBodyIncidentService(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the service associated with this incident.")
    type_: Literal["service_reference"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of service reference. Must be 'service_reference'.")
class UpdateIncidentRequestBodyIncidentConferenceBridge(StrictModel):
    conference_number: str | None = Field(default=None, validation_alias="conference_number", serialization_alias="conference_number", description="Phone number for the incident's conference bridge. Format as +1 415-555-1212,,,,1234# where commas represent one-second waits and # completes access code entry.")
    conference_url: str | None = Field(default=None, validation_alias="conference_url", serialization_alias="conference_url", description="URL for the incident's conference bridge, such as a web conference link or Slack channel. Must be a valid URL.", json_schema_extra={'format': 'url'})
class UpdateIncidentRequestBodyIncident(StrictModel):
    type_: Literal["incident", "incident_reference"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The incident type. Use 'incident' for standard incidents or 'incident_reference' for references.")
    status: Literal["resolved", "acknowledged", "triggered"] | None = Field(default=None, validation_alias="status", serialization_alias="status", description="The new incident status. Use 'resolved' to close the incident, 'acknowledged' to mark as in-progress, or 'triggered' to reopen. Reopening to 'triggered' reassigns based on escalation policy; reopening to 'acknowledged' assigns to the current user.")
    priority: UpdateIncidentBodyIncidentPriority | None = Field(default=None, validation_alias="priority", serialization_alias="priority", description="The priority level for the incident. Can be provided as an object or scalar value.")
    resolution: str | None = Field(default=None, validation_alias="resolution", serialization_alias="resolution", description="Resolution reason or notes. Only used when setting status to 'resolved'. Appears in the incident's resolution log entry.")
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="A new title for the incident.")
    escalation_level: int | None = Field(default=None, validation_alias="escalation_level", serialization_alias="escalation_level", description="Escalate the incident to a specific level in the escalation policy. Must be a positive integer representing the escalation level.")
    assignments: list[UpdateIncidentBodyIncidentAssignmentsItem] | None = Field(default=None, validation_alias="assignments", serialization_alias="assignments", description="Array of users or schedules to assign this incident to. Order may affect assignment priority.")
    escalation_policy: EscalationPolicyReference | None = Field(default=None, validation_alias="escalation_policy", serialization_alias="escalation_policy", description="The escalation policy to apply to this incident.")
    urgency: Literal["high", "low"] | None = Field(default=None, validation_alias="urgency", serialization_alias="urgency", description="The urgency level of the incident. Use 'high' for critical issues or 'low' for non-critical ones.")
    service: UpdateIncidentRequestBodyIncidentService
    conference_bridge: UpdateIncidentRequestBodyIncidentConferenceBridge | None = None
class UpdateIncidentRequestBody(StrictModel):
    incident: UpdateIncidentRequestBodyIncident
class UpdateIncidentRequest(StrictModel):
    """Update an incident's status, priority, assignments, or other details. Use this to acknowledge, resolve, escalate, or reassign incidents, and optionally add resolution notes or conference details."""
    path: UpdateIncidentRequestPath
    header: UpdateIncidentRequestHeader
    body: UpdateIncidentRequestBody

# Operation: list_incident_alerts
class ListIncidentAlertsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident for which to retrieve alerts.")
class ListIncidentAlertsRequestQuery(StrictModel):
    alert_key: str | None = Field(default=None, description="Filter alerts by their de-duplication key to find specific alert instances.")
    statuses: Annotated[Literal["triggered", "resolved"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="statuses[]", serialization_alias="statuses[]", description="Filter results to only include alerts with specific statuses: triggered (active/unresolved) or resolved (closed). Multiple statuses can be specified.")
    sort_by: Annotated[Literal["created_at", "resolved_at", "created_at:asc", "created_at:desc", "resolved_at:asc", "resolved_at:desc"], AfterValidator(_check_unique_items)] | None = Field(default=None, description="Sort results by creation time or resolution time in ascending or descending order. Specify as field:direction (e.g., created_at:desc). Up to two sort fields can be combined with commas; direction defaults to ascending if omitted.", max_length=2)
    include: Annotated[Literal["services", "first_trigger_log_entries", "incidents"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Include additional related data in the response: services (associated service details), first_trigger_log_entries (initial trigger event logs), or incidents (parent incident information). Multiple inclusions can be specified.")
class ListIncidentAlertsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to request the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class ListIncidentAlertsRequest(StrictModel):
    """Retrieve all alerts associated with a specific incident. Alerts can be filtered by status, deduplicated by key, sorted by creation or resolution time, and enriched with related service, log entry, or incident details."""
    path: ListIncidentAlertsRequestPath
    query: ListIncidentAlertsRequestQuery | None = None
    header: ListIncidentAlertsRequestHeader

# Operation: update_incident_alerts
class UpdateIncidentAlertsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to update alerts for.")
class UpdateIncidentAlertsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty v2 JSON format for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request body content type. Must be JSON format.")
    from_: str = Field(default=..., validation_alias="From", serialization_alias="From", description="Email address of the authenticated user making the request. Must be a valid user associated with the PagerDuty account.", json_schema_extra={'format': 'email'})
class UpdateIncidentAlertsRequestBody(StrictModel):
    alerts: list[AlertUpdate] = Field(default=..., description="Array of alert objects to update, each containing the alert ID and parameters to modify (such as status or target incident). Maximum 250 alerts per request; exceeding this limit will return a 413 error.")
class UpdateIncidentAlertsRequest(StrictModel):
    """Update the status of multiple alerts or reassign them to different incidents. Supports resolving alerts or moving them between incidents, with a maximum of 250 alerts per request."""
    path: UpdateIncidentAlertsRequestPath
    header: UpdateIncidentAlertsRequestHeader
    body: UpdateIncidentAlertsRequestBody

# Operation: get_incident_alert
class GetIncidentAlertRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident containing the alert.")
    alert_id: str = Field(default=..., description="The unique identifier of the alert to retrieve.")
class GetIncidentAlertRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2 for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type for the request body. Must be JSON format.")
class GetIncidentAlertRequest(StrictModel):
    """Retrieve detailed information about a specific alert within an incident. Alerts are triggered when a service sends an event to PagerDuty and represent the individual notifications associated with an incident."""
    path: GetIncidentAlertRequestPath
    header: GetIncidentAlertRequestHeader

# Operation: update_incident_alert
class UpdateIncidentAlertRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident containing the alert to update.")
    alert_id: str = Field(default=..., description="The unique identifier of the alert to update.")
class UpdateIncidentAlertRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API version header. Must be set to 'application/vnd.pagerduty+json;version=2' to specify the PagerDuty API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type of the request body. Must be 'application/json'.")
    from_: str = Field(default=..., validation_alias="From", serialization_alias="From", description="The email address of a valid user associated with your PagerDuty account. This identifies who is making the request.", json_schema_extra={'format': 'email'})
class UpdateIncidentAlertRequestBodyAlertIncident(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the parent incident to associate this alert with. Use this to reassign the alert to a different incident.")
class UpdateIncidentAlertRequestBodyAlert(StrictModel):
    status: Literal["resolved", "triggered"] | None = Field(default=None, validation_alias="status", serialization_alias="status", description="The new status for the alert. Set to 'resolved' to close the alert or 'triggered' to reopen it.")
    incident: UpdateIncidentAlertRequestBodyAlertIncident
class UpdateIncidentAlertRequestBody(StrictModel):
    """The parameters of the alert to update."""
    alert: UpdateIncidentAlertRequestBodyAlert
class UpdateIncidentAlertRequest(StrictModel):
    """Update an alert by resolving it or reassigning it to a different parent incident. This operation allows you to change an alert's status or move it between incidents."""
    path: UpdateIncidentAlertRequestPath
    header: UpdateIncidentAlertRequestHeader
    body: UpdateIncidentAlertRequestBody

# Operation: update_incident_business_service_impact
class PutIncidentManualBusinessServiceAssociationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to modify.")
    business_service_id: str = Field(default=..., description="The unique identifier of the business service whose impact status should be updated.")
class PutIncidentManualBusinessServiceAssociationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default value to request PagerDuty API version 2.")
class PutIncidentManualBusinessServiceAssociationRequestBody(StrictModel):
    """The `impacted` relation will cause the Business Service and any Services that it supports to become impacted by this incident.

The `not_impacted` relation will remove the Incident's Impact from the specified Business Service.

The effect of adding or removing Impact to a Business Service in this way will also change the propagation of Impact to other Services supported by that Business Service."""
    relation: Literal["impacted", "not_impacted"] = Field(default=..., description="The impact relationship status. Set to 'impacted' if the incident affects this business service, or 'not_impacted' if it does not.")
class PutIncidentManualBusinessServiceAssociationRequest(StrictModel):
    """Manually update whether an incident impacts a specific business service. Use this to change the impact relationship between an incident and a business service."""
    path: PutIncidentManualBusinessServiceAssociationRequestPath
    header: PutIncidentManualBusinessServiceAssociationRequestHeader
    body: PutIncidentManualBusinessServiceAssociationRequestBody

# Operation: list_business_services_impacted_by_incident
class GetIncidentImpactedBusinessServicesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident for which to retrieve impacted business services.")
class GetIncidentImpactedBusinessServicesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and schema version. Defaults to PagerDuty JSON API version 2.")
class GetIncidentImpactedBusinessServicesRequest(StrictModel):
    """Retrieve all Business Services currently being impacted by a specific incident. Use this to understand the scope of service degradation caused by an incident."""
    path: GetIncidentImpactedBusinessServicesRequestPath
    header: GetIncidentImpactedBusinessServicesRequestHeader

# Operation: get_incident_custom_field_values
class GetIncidentFieldValuesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident whose custom field values you want to retrieve.")
class GetIncidentFieldValuesRequest(StrictModel):
    """Retrieve all custom field values associated with a specific incident. Returns the current values for any custom fields configured for that incident."""
    path: GetIncidentFieldValuesRequestPath

# Operation: update_incident_custom_field_values
class SetIncidentFieldValuesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to update.")
class SetIncidentFieldValuesRequestBody(StrictModel):
    custom_fields: list[CustomFieldsEditableFieldValue] = Field(default=..., description="An array of custom field assignments to set for the incident. Each item in the array should specify the field and its value.")
class SetIncidentFieldValuesRequest(StrictModel):
    """Update custom field values for a specific incident. Allows setting or modifying one or more custom field values associated with the incident."""
    path: SetIncidentFieldValuesRequestPath
    body: SetIncidentFieldValuesRequestBody

# Operation: list_incident_log_entries
class ListIncidentLogEntriesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident for which to retrieve log entries.")
class ListIncidentLogEntriesRequestQuery(StrictModel):
    time_zone: str | None = Field(default=None, description="Time zone for rendering timestamps in results. Defaults to your account's configured time zone. Specify as a valid IANA time zone identifier (e.g., America/New_York).", json_schema_extra={'format': 'tzinfo'})
    since: str | None = Field(default=None, description="Filter log entries to those on or after this date and time. Specify in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="Filter log entries to those on or before this date and time. Specify in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    is_overview: bool | None = Field(default=None, description="When true, returns only the most significant log entries highlighting major incident changes. When false (default), returns all log entries.")
    include: Annotated[Literal["incidents", "services", "channels", "teams"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Comma-separated list of related resources to include in the response. Valid options are incidents, services, channels, and teams. Omit to return only log entry data.")
class ListIncidentLogEntriesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to use this operation.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class ListIncidentLogEntriesRequest(StrictModel):
    """Retrieve a chronological list of log entries documenting all events and changes for a specific incident. Optionally filter by date range and retrieve only critical updates."""
    path: ListIncidentLogEntriesRequestPath
    query: ListIncidentLogEntriesRequestQuery | None = None
    header: ListIncidentLogEntriesRequestHeader

# Operation: merge_incidents
class MergeIncidentsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the target incident that will receive the merged incidents and their alerts.")
class MergeIncidentsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty API v2 format for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be JSON format.")
    from_: str = Field(default=..., validation_alias="From", serialization_alias="From", description="Email address of the authenticated user making the request. Must be a valid user associated with the account.", json_schema_extra={'format': 'email'})
class MergeIncidentsRequestBody(StrictModel):
    source_incidents: list[IncidentReference] = Field(default=..., description="Array of incident IDs to merge into the target incident. Only incidents with alerts or manually created incidents are eligible. Open incidents cannot be merged into resolved incidents.")
class MergeIncidentsRequest(StrictModel):
    """Merge multiple source incidents into a target incident, consolidating their alerts and resolving the source incidents. The target incident will inherit all alerts from source incidents, with a maximum combined alert limit of 1000."""
    path: MergeIncidentsRequestPath
    header: MergeIncidentsRequestHeader
    body: MergeIncidentsRequestBody

# Operation: list_incident_notes
class ListIncidentNotesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident for which to retrieve notes.")
class ListIncidentNotesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body. Must be set to JSON format.")
class ListIncidentNotesRequest(StrictModel):
    """Retrieve all notes associated with a specific incident. Notes provide additional context and updates about the incident's status and resolution efforts."""
    path: ListIncidentNotesRequestPath
    header: ListIncidentNotesRequestHeader

# Operation: add_note_to_incident
class CreateIncidentNoteRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to which the note will be added.")
class CreateIncidentNoteRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API version header for response formatting. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type, must be JSON.")
    from_: str = Field(default=..., validation_alias="From", serialization_alias="From", description="Email address of the user account making this request. Must be a valid, active user associated with your PagerDuty account.", json_schema_extra={'format': 'email'})
class CreateIncidentNoteRequestBodyNote(StrictModel):
    content: str = Field(default=..., validation_alias="content", serialization_alias="content", description="The text content of the note. Can be up to 2000 characters to document incident details, actions taken, or resolution information.")
class CreateIncidentNoteRequestBody(StrictModel):
    note: CreateIncidentNoteRequestBodyNote
class CreateIncidentNoteRequest(StrictModel):
    """Add a new note to an incident to document updates, context, or resolution steps. Each incident supports up to 2000 notes."""
    path: CreateIncidentNoteRequestPath
    header: CreateIncidentNoteRequestHeader
    body: CreateIncidentNoteRequestBody

# Operation: update_incident_note
class UpdateIncidentNoteRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident containing the note to update.")
    note_id: str = Field(default=..., description="The unique identifier of the note to update.")
class UpdateIncidentNoteRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API version header for response formatting. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be JSON format.")
    from_: str = Field(default=..., validation_alias="From", serialization_alias="From", description="The email address of a valid user account associated with your PagerDuty instance. This identifies who is making the request.", json_schema_extra={'format': 'email'})
class UpdateIncidentNoteRequestBodyNote(StrictModel):
    content: str = Field(default=..., validation_alias="content", serialization_alias="content", description="The updated text content for the note.")
class UpdateIncidentNoteRequestBody(StrictModel):
    note: UpdateIncidentNoteRequestBodyNote
class UpdateIncidentNoteRequest(StrictModel):
    """Update the content of an existing note attached to an incident. This allows you to modify note text after it has been created."""
    path: UpdateIncidentNoteRequestPath
    header: UpdateIncidentNoteRequestHeader
    body: UpdateIncidentNoteRequestBody

# Operation: delete_incident_note
class DeleteIncidentNoteRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident containing the note to delete.")
    note_id: str = Field(default=..., description="The unique identifier of the note to delete.")
class DeleteIncidentNoteRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API version header for response formatting. Defaults to PagerDuty API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class DeleteIncidentNoteRequest(StrictModel):
    """Permanently delete a note attached to an incident. This action cannot be undone."""
    path: DeleteIncidentNoteRequestPath
    header: DeleteIncidentNoteRequestHeader

# Operation: get_outlier_incident
class GetOutlierIncidentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident resource to retrieve outlier information for.")
class GetOutlierIncidentRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="The start of the date range for analyzing incident patterns. Specify as an ISO 8601 formatted date-time string.", json_schema_extra={'format': 'date-time'})
    additional_details: Annotated[Literal["incident"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="additional_details[]", serialization_alias="additional_details[]", description="Array of additional attributes to include in the response for related incidents. Currently supports 'incident' to include full incident details.")
class GetOutlierIncidentRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty JSON API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class GetOutlierIncidentRequest(StrictModel):
    """Retrieves outlier incident information for a specific incident on its associated service. Outlier incidents are identified based on statistical deviation from normal incident patterns."""
    path: GetOutlierIncidentRequestPath
    query: GetOutlierIncidentRequestQuery | None = None
    header: GetOutlierIncidentRequestHeader

# Operation: list_past_incidents
class GetPastIncidentsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident for which to retrieve related past incidents.")
class GetPastIncidentsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body. Must be set to application/json.")
class GetPastIncidentsRequest(StrictModel):
    """Retrieve incidents from the past 6 months that share similar metadata and were generated on the same service as a specified incident. Returns up to 5 past incidents by default. This feature requires the Event Intelligence package or Digital Operations plan."""
    path: GetPastIncidentsRequestPath
    header: GetPastIncidentsRequestHeader

# Operation: list_incident_related_change_events
class ListIncidentRelatedChangeEventsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident for which to retrieve related change events.")
class ListIncidentRelatedChangeEventsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and structure. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to JSON format.")
class ListIncidentRelatedChangeEventsRequest(StrictModel):
    """Retrieve change events correlated with a specific incident, including the correlation reasons (time proximity, related service, or machine learning intelligence). This helps incident responders understand what service changes may have triggered or contributed to the incident."""
    path: ListIncidentRelatedChangeEventsRequestPath
    header: ListIncidentRelatedChangeEventsRequestHeader

# Operation: get_related_incidents
class GetRelatedIncidentsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident for which to retrieve related incidents.")
class GetRelatedIncidentsRequestQuery(StrictModel):
    additional_details: Annotated[Literal["incident"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="additional_details[]", serialization_alias="additional_details[]", description="Optional array to include additional details about returned incidents. Currently supports the 'incident' attribute to expand incident information.")
class GetRelatedIncidentsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to JSON format.")
class GetRelatedIncidentsRequest(StrictModel):
    """Retrieve the 20 most recent incidents that are impacting other responders and services in relation to a specific incident. This feature requires the Event Intelligence package or Digital Operations plan."""
    path: GetRelatedIncidentsRequestPath
    query: GetRelatedIncidentsRequestQuery | None = None
    header: GetRelatedIncidentsRequestHeader

# Operation: send_responder_request_for_incident
class CreateIncidentResponderRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to request responders for.")
class CreateIncidentResponderRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty v2 JSON format for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be JSON format.")
class CreateIncidentResponderRequestBody(StrictModel):
    requester_id: str = Field(default=..., description="The user ID of the person making the responder request.")
    message: str = Field(default=..., description="A message to include with the responder request explaining the need for additional responders.")
    responder_request_targets: Any = Field(default=..., description="An array of responder targets (users or escalation policies) to notify. Each target will receive high urgency notifications until they respond to the request.")
class CreateIncidentResponderRequest(StrictModel):
    """Request additional responders for an incident by notifying a user or escalation policy. The responder targets will be notified via high urgency notification rules until they accept or decline the request. Requires the account to have the `coordinated_responding` ability."""
    path: CreateIncidentResponderRequestPath
    header: CreateIncidentResponderRequestHeader
    body: CreateIncidentResponderRequestBody

# Operation: cancel_incident_responder_requests
class CancelIncidentResponderRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident for which responder requests should be cancelled.")
class CancelIncidentResponderRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty v2 JSON format for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be application/json.")
class CancelIncidentResponderRequestBody(StrictModel):
    requester_id: str = Field(default=..., description="The user ID of the person making the cancellation request. This user must have permission to modify the incident.")
    responder_request_targets: list[CancelIncidentResponderRequestBodyResponderRequestTargetsItem] = Field(default=..., description="Array of responder targets to cancel. Each target can be a user or escalation policy. Only targets in pending state will be cancelled; those already joined or declined are unaffected.")
class CancelIncidentResponderRequest(StrictModel):
    """Cancel pending responder requests for an incident. Stops notifications and updates state to cancelled for responders who have not yet joined or declined. Requires the coordinated_responding account ability."""
    path: CancelIncidentResponderRequestPath
    header: CancelIncidentResponderRequestHeader
    body: CancelIncidentResponderRequestBody

# Operation: snooze_incident
class CreateIncidentSnoozeRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to snooze.")
class CreateIncidentSnoozeRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty v2 JSON format for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be JSON format.")
    from_: str = Field(default=..., validation_alias="From", serialization_alias="From", description="Email address of the authenticated user making this request. Must be a valid user associated with your PagerDuty account.", json_schema_extra={'format': 'email'})
class CreateIncidentSnoozeRequestBody(StrictModel):
    duration: int = Field(default=..., description="Duration to snooze the incident in seconds. Must be between 1 second and 7 days (604800 seconds).", ge=1, le=604800)
class CreateIncidentSnoozeRequest(StrictModel):
    """Temporarily snooze an incident to suppress notifications and defer its resolution. The incident will automatically return to triggered state after the specified duration expires."""
    path: CreateIncidentSnoozeRequestPath
    header: CreateIncidentSnoozeRequestHeader
    body: CreateIncidentSnoozeRequestBody

# Operation: create_incident_status_update
class CreateIncidentStatusUpdateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to update.")
class CreateIncidentStatusUpdateRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API version header to specify the response format. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be JSON.")
    from_: str = Field(default=..., validation_alias="From", serialization_alias="From", description="The email address of an active user account associated with your organization. This user is credited as the author of the status update.", json_schema_extra={'format': 'email'})
class CreateIncidentStatusUpdateRequestBody(StrictModel):
    message: str = Field(default=..., description="The status update message to post. This text will be visible in the incident timeline.")
    subject: str | None = Field(default=None, description="The subject line for the email notification sent to stakeholders. Only used if html_message is also provided for a custom email.")
    html_message: str | None = Field(default=None, description="The HTML content for the email notification sent to stakeholders. Only used if subject is also provided for a custom email.")
class CreateIncidentStatusUpdateRequest(StrictModel):
    """Post a status update to an incident to communicate progress or changes. Optionally customize the email notification sent to stakeholders by providing a custom subject and HTML message."""
    path: CreateIncidentStatusUpdateRequestPath
    header: CreateIncidentStatusUpdateRequestHeader
    body: CreateIncidentStatusUpdateRequestBody

# Operation: list_incident_notification_subscribers
class GetIncidentNotificationSubscribersRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident for which to retrieve notification subscribers.")
class GetIncidentNotificationSubscribersRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="The API version header for response formatting. Defaults to PagerDuty API v2 JSON format.")
class GetIncidentNotificationSubscribersRequest(StrictModel):
    """Retrieve the list of users subscribed to receive status update notifications for a specific incident. Only users explicitly added via the subscribe endpoint will be returned."""
    path: GetIncidentNotificationSubscribersRequestPath
    header: GetIncidentNotificationSubscribersRequestHeader

# Operation: add_incident_status_update_subscribers
class CreateIncidentNotificationSubscribersRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident to subscribe entities to for status update notifications.")
class CreateIncidentNotificationSubscribersRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default PagerDuty JSON v2 format.")
class CreateIncidentNotificationSubscribersRequestBody(StrictModel):
    """The entities to subscribe."""
    subscribers: Annotated[list[NotificationSubscriber], AfterValidator(_check_unique_items)] = Field(default=..., description="Array of subscriber entities to add to the incident's notification list. Must contain at least one subscriber. Each subscriber should specify the entity type (user, team, or schedule) and its ID.", min_length=1)
class CreateIncidentNotificationSubscribersRequest(StrictModel):
    """Subscribe entities (users, teams, or schedules) to receive notifications when an incident's status is updated. This allows stakeholders to stay informed of incident progress."""
    path: CreateIncidentNotificationSubscribersRequestPath
    header: CreateIncidentNotificationSubscribersRequestHeader
    body: CreateIncidentNotificationSubscribersRequestBody

# Operation: remove_incident_notification_subscribers
class RemoveIncidentNotificationSubscribersRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the incident from which to remove subscribers.")
class RemoveIncidentNotificationSubscribersRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="The API version header for request/response formatting. Defaults to PagerDuty API v2 JSON format.")
class RemoveIncidentNotificationSubscribersRequestBody(StrictModel):
    """The entities to unsubscribe."""
    subscribers: Annotated[list[NotificationSubscriber], AfterValidator(_check_unique_items)] = Field(default=..., description="An array of subscriber identifiers to unsubscribe from incident notifications. Must contain at least one subscriber.", min_length=1)
class RemoveIncidentNotificationSubscribersRequest(StrictModel):
    """Unsubscribes one or more subscribers from receiving status update notifications for a specific incident."""
    path: RemoveIncidentNotificationSubscribersRequestPath
    header: RemoveIncidentNotificationSubscribersRequestHeader
    body: RemoveIncidentNotificationSubscribersRequestBody

# Operation: list_incident_types
class ListIncidentTypesRequestQuery(StrictModel):
    filter_: Literal["enabled", "disabled", "all"] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by the enabled state of incident types. Use 'enabled' to show only active types, 'disabled' to show only inactive types, or 'all' to show both. Defaults to 'enabled'.")
class ListIncidentTypesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to the PagerDuty JSON media type with version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON.")
class ListIncidentTypesRequest(StrictModel):
    """Retrieve the list of available incident types that can be used to categorize incidents (such as security, major, or fraud incidents). Results can be filtered by enabled or disabled status."""
    query: ListIncidentTypesRequestQuery | None = None
    header: ListIncidentTypesRequestHeader

# Operation: create_incident_type
class CreateIncidentTypeRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request body content type. Must be JSON.")
class CreateIncidentTypeRequestBodyIncidentType(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The incident type identifier (up to 50 characters). Cannot be changed after creation and cannot end with `_default`.", max_length=50)
    display_name: str = Field(default=..., validation_alias="display_name", serialization_alias="display_name", description="The human-readable display name (up to 50 characters). Cannot start with `PD`, `PagerDuty`, or `Default`.", max_length=50)
    parent_type: str = Field(default=..., validation_alias="parent_type", serialization_alias="parent_type", description="The parent incident type that this type inherits from. Specify either the parent type's name or ID.")
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Whether this incident type is active and available for use. Defaults to true if not specified.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Optional description of the incident type's purpose and usage (up to 1000 characters).", max_length=1000)
class CreateIncidentTypeRequestBody(StrictModel):
    incident_type: CreateIncidentTypeRequestBodyIncidentType
class CreateIncidentTypeRequest(StrictModel):
    """Create a new incident type to categorize incidents (e.g., security, major, fraud). Incident types help organize and manage different incident categories within your organization."""
    header: CreateIncidentTypeRequestHeader
    body: CreateIncidentTypeRequestBody

# Operation: get_incident_type
class GetIncidentTypeRequestPath(StrictModel):
    type_id_or_name: str = Field(default=..., description="The unique identifier or display name of the incident type to retrieve.")
class GetIncidentTypeRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty JSON API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body. Must be application/json.")
class GetIncidentTypeRequest(StrictModel):
    """Retrieve detailed information about a single incident type by its ID or name. Incident types categorize incidents (e.g., security, major, fraud) for organizational purposes."""
    path: GetIncidentTypeRequestPath
    header: GetIncidentTypeRequestHeader

# Operation: update_incident_type
class UpdateIncidentTypeRequestPath(StrictModel):
    type_id_or_name: str = Field(default=..., description="The unique identifier or name of the Incident Type to update.")
class UpdateIncidentTypeRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type of the request body. Must be application/json.")
class UpdateIncidentTypeRequestBodyIncidentType(StrictModel):
    display_name: str | None = Field(default=None, validation_alias="display_name", serialization_alias="display_name", description="The display name for the Incident Type. Maximum 50 characters.", max_length=50)
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Whether the Incident Type is active and available for use. Defaults to true if not specified.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A detailed description of the Incident Type's purpose or usage. Maximum 1000 characters.", max_length=1000)
class UpdateIncidentTypeRequestBody(StrictModel):
    incident_type: UpdateIncidentTypeRequestBodyIncidentType | None = None
class UpdateIncidentTypeRequest(StrictModel):
    """Update an existing Incident Type to modify its display name, description, or enabled status. Incident Types allow customers to categorize incidents such as security, major, or fraud incidents."""
    path: UpdateIncidentTypeRequestPath
    header: UpdateIncidentTypeRequestHeader
    body: UpdateIncidentTypeRequestBody | None = None

# Operation: list_incident_type_custom_fields
class ListIncidentTypeCustomFieldsRequestPath(StrictModel):
    type_id_or_name: str = Field(default=..., description="The unique identifier or display name of the incident type whose custom fields you want to retrieve.")
class ListIncidentTypeCustomFieldsRequestQuery(StrictModel):
    include: Annotated[Literal["field_options"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array to include additional details about custom fields. Specify 'field_options' to retrieve the available options for fields that support predefined choices.")
class ListIncidentTypeCustomFieldsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Defaults to PagerDuty API version 2 (application/vnd.pagerduty+json;version=2).")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be set to application/json.")
class ListIncidentTypeCustomFieldsRequest(StrictModel):
    """Retrieve all custom fields configured for a specific incident type. Custom fields extend incidents with additional context and enable customized filtering, search, and analytics capabilities."""
    path: ListIncidentTypeCustomFieldsRequestPath
    query: ListIncidentTypeCustomFieldsRequestQuery | None = None
    header: ListIncidentTypeCustomFieldsRequestHeader

# Operation: create_incident_type_custom_field
class CreateIncidentTypeCustomFieldRequestPath(StrictModel):
    type_id_or_name: str = Field(default=..., description="The incident type identifier or name to which the custom field will be added.")
class CreateIncidentTypeCustomFieldRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be application/json.")
class CreateIncidentTypeCustomFieldRequestBodyField(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The internal name of the custom field. Limited to 50 characters.", max_length=50)
    display_name: str = Field(default=..., validation_alias="display_name", serialization_alias="display_name", description="The user-facing display name for the custom field. Limited to 50 characters.", max_length=50)
    data_type: str = Field(default=..., validation_alias="data_type", serialization_alias="data_type", description="The data type that the custom field will store (e.g., string, integer, boolean).")
    field_type: Literal["single_value", "single_value_fixed", "multi_value", "multi_value_fixed"] = Field(default=..., validation_alias="field_type", serialization_alias="field_type", description="The field interaction type. Use 'single_value' or 'multi_value' for open-ended fields, or 'single_value_fixed' or 'multi_value_fixed' for predefined options.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Optional description of the custom field's purpose and usage. Limited to 1000 characters.", max_length=1000)
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Whether the custom field is active and available for use on incidents.")
    default_value: str | None = Field(default=None, validation_alias="default_value", serialization_alias="default_value", description="The initial value assigned to this custom field when creating new incidents.")
    field_options: list[CustomFieldsFieldOption] | None = Field(default=None, validation_alias="field_options", serialization_alias="field_options", description="Predefined options for fixed-value fields. Required when field_type is 'single_value_fixed' or 'multi_value_fixed'. Must include at least one option.")
class CreateIncidentTypeCustomFieldRequestBody(StrictModel):
    field: CreateIncidentTypeCustomFieldRequestBodyField
class CreateIncidentTypeCustomFieldRequest(StrictModel):
    """Create a custom field for a specific incident type to extend incidents with additional context. Custom fields support customized filtering, search, and analytics across incident data."""
    path: CreateIncidentTypeCustomFieldRequestPath
    header: CreateIncidentTypeCustomFieldRequestHeader
    body: CreateIncidentTypeCustomFieldRequestBody

# Operation: get_incident_type_custom_field
class GetIncidentTypeCustomFieldRequestPath(StrictModel):
    type_id_or_name: str = Field(default=..., description="The unique identifier or display name of the incident type to which the custom field belongs.")
    field_id: str = Field(default=..., description="The unique identifier of the custom field to retrieve.")
class GetIncidentTypeCustomFieldRequestQuery(StrictModel):
    include: Annotated[Literal["field_options"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array of related data to include in the response. Specify 'field_options' to include the available options for this custom field.")
class GetIncidentTypeCustomFieldRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty JSON API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to JSON format.")
class GetIncidentTypeCustomFieldRequest(StrictModel):
    """Retrieve a specific custom field associated with an incident type. Custom fields extend incidents with additional context and enable customized filtering, search, and analytics capabilities."""
    path: GetIncidentTypeCustomFieldRequestPath
    query: GetIncidentTypeCustomFieldRequestQuery | None = None
    header: GetIncidentTypeCustomFieldRequestHeader

# Operation: update_incident_type_custom_field
class UpdateIncidentTypeCustomFieldRequestPath(StrictModel):
    type_id_or_name: str = Field(default=..., description="The ID or name of the incident type to which the custom field belongs.")
    field_id: str = Field(default=..., description="The ID of the custom field to update.")
class UpdateIncidentTypeCustomFieldRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default value to request the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be JSON format.")
class UpdateIncidentTypeCustomFieldRequestBodyField(StrictModel):
    display_name: str | None = Field(default=None, validation_alias="display_name", serialization_alias="display_name", description="The display name of the custom field, up to 50 characters.", max_length=50)
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Whether the custom field is active and available for use on incidents.")
    default_value: str | None = Field(default=None, validation_alias="default_value", serialization_alias="default_value", description="The default value assigned to this custom field when creating new incidents.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A description of the custom field's purpose and usage, up to 1000 characters.", max_length=1000)
    field_options: list[CustomFieldsFieldOption] | None = Field(default=None, validation_alias="field_options", serialization_alias="field_options", description="List of field options to add or update. Only applicable to fixed-value fields (single or multi-select). Include an `id` property to update an existing option, or omit it to add a new option. Options not included in this list will be deleted unless they are referenced by the current default value.")
class UpdateIncidentTypeCustomFieldRequestBody(StrictModel):
    field: UpdateIncidentTypeCustomFieldRequestBodyField | None = None
class UpdateIncidentTypeCustomFieldRequest(StrictModel):
    """Update a custom field definition for an incident type, including its display properties and field options. Custom fields extend incidents with additional context to support filtering, search, and analytics."""
    path: UpdateIncidentTypeCustomFieldRequestPath
    header: UpdateIncidentTypeCustomFieldRequestHeader
    body: UpdateIncidentTypeCustomFieldRequestBody | None = None

# Operation: delete_incident_type_custom_field
class DeleteIncidentTypeCustomFieldRequestPath(StrictModel):
    type_id_or_name: str = Field(default=..., description="The incident type identifier or name to which the custom field is attached.")
    field_id: str = Field(default=..., description="The unique identifier of the custom field to delete.")
class DeleteIncidentTypeCustomFieldRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be JSON format.")
class DeleteIncidentTypeCustomFieldRequest(StrictModel):
    """Remove a custom field from an incident type. Custom fields extend incidents with additional context and enable customized filtering, search, and analytics capabilities."""
    path: DeleteIncidentTypeCustomFieldRequestPath
    header: DeleteIncidentTypeCustomFieldRequestHeader

# Operation: list_incident_type_custom_field_options
class ListIncidentTypeCustomFieldRequestPath(StrictModel):
    type_id_or_name: str = Field(default=..., description="The incident type identifier or name to which the custom field is attached.")
    field_id: str = Field(default=..., description="The unique identifier of the custom field whose options you want to list.")
class ListIncidentTypeCustomFieldRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty JSON API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type for the request body. Must be application/json.")
class ListIncidentTypeCustomFieldRequest(StrictModel):
    """Retrieve all available field options for a custom field attached to a specific incident type. Custom fields extend incidents with additional context and enable customized filtering, search, and analytics capabilities."""
    path: ListIncidentTypeCustomFieldRequestPath
    header: ListIncidentTypeCustomFieldRequestHeader

# Operation: create_incident_type_custom_field_option
class CreateIncidentTypeCustomFieldFieldOptionsRequestPath(StrictModel):
    type_id_or_name: str = Field(default=..., description="The incident type identifier or name to which the custom field belongs.")
    field_id: str = Field(default=..., description="The unique identifier of the custom field within the incident type.")
class CreateIncidentTypeCustomFieldFieldOptionsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use application/vnd.pagerduty+json;version=2 for current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be application/json.")
class CreateIncidentTypeCustomFieldFieldOptionsRequestBodyFieldOptionData(StrictModel):
    data_type: str = Field(default=..., validation_alias="data_type", serialization_alias="data_type", description="The data type classification for this field option (e.g., string, number, boolean).")
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The actual value of the field option that will be available for selection when creating or updating incidents.")
class CreateIncidentTypeCustomFieldFieldOptionsRequestBodyFieldOption(StrictModel):
    data: CreateIncidentTypeCustomFieldFieldOptionsRequestBodyFieldOptionData
class CreateIncidentTypeCustomFieldFieldOptionsRequestBody(StrictModel):
    field_option: CreateIncidentTypeCustomFieldFieldOptionsRequestBodyFieldOption
class CreateIncidentTypeCustomFieldFieldOptionsRequest(StrictModel):
    """Create a field option for a custom field on a specific incident type. Field options define the available choices for custom fields, enabling structured data collection and filtering across incidents."""
    path: CreateIncidentTypeCustomFieldFieldOptionsRequestPath
    header: CreateIncidentTypeCustomFieldFieldOptionsRequestHeader
    body: CreateIncidentTypeCustomFieldFieldOptionsRequestBody

# Operation: get_incident_type_custom_field_option
class GetIncidentTypeCustomFieldFieldOptionsRequestPath(StrictModel):
    type_id_or_name: str = Field(default=..., description="The incident type identifier or name to which the custom field is applied.")
    field_option_id: str = Field(default=..., description="The unique identifier of the field option to retrieve.")
    field_id: str = Field(default=..., description="The unique identifier of the custom field containing the field option.")
class GetIncidentTypeCustomFieldFieldOptionsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default value to request the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body and response. Must be JSON format.")
class GetIncidentTypeCustomFieldFieldOptionsRequest(StrictModel):
    """Retrieve a specific field option from a custom field associated with an incident type. Field options define the available choices for custom fields applied to incidents."""
    path: GetIncidentTypeCustomFieldFieldOptionsRequestPath
    header: GetIncidentTypeCustomFieldFieldOptionsRequestHeader

# Operation: update_incident_type_custom_field_option
class UpdateIncidentTypeCustomFieldFieldOptionRequestPath(StrictModel):
    type_id_or_name: str = Field(default=..., description="The incident type identifier or name to which the custom field belongs.")
    field_option_id: str = Field(default=..., description="The unique identifier of the field option to update.")
    field_id: str = Field(default=..., description="The unique identifier of the custom field containing the field option.")
class UpdateIncidentTypeCustomFieldFieldOptionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2 for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be application/json.")
class UpdateIncidentTypeCustomFieldFieldOptionRequestBodyFieldOptionData(StrictModel):
    data_type: str = Field(default=..., validation_alias="data_type", serialization_alias="data_type", description="The data type classification for this field option (e.g., string, number, boolean).")
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The display value or label for this field option that users will see when selecting it.")
class UpdateIncidentTypeCustomFieldFieldOptionRequestBodyFieldOption(StrictModel):
    data: UpdateIncidentTypeCustomFieldFieldOptionRequestBodyFieldOptionData
class UpdateIncidentTypeCustomFieldFieldOptionRequestBody(StrictModel):
    field_option: UpdateIncidentTypeCustomFieldFieldOptionRequestBodyFieldOption
class UpdateIncidentTypeCustomFieldFieldOptionRequest(StrictModel):
    """Update a specific field option within a custom field attached to an incident type. Field options define the available choices for custom fields, allowing you to modify their values and data types."""
    path: UpdateIncidentTypeCustomFieldFieldOptionRequestPath
    header: UpdateIncidentTypeCustomFieldFieldOptionRequestHeader
    body: UpdateIncidentTypeCustomFieldFieldOptionRequestBody

# Operation: delete_incident_type_custom_field_option
class DeleteIncidentTypeCustomFieldFieldOptionRequestPath(StrictModel):
    type_id_or_name: str = Field(default=..., description="The incident type identifier or name to which the custom field belongs. Can be either the unique ID or the human-readable name of the incident type.")
    field_option_id: str = Field(default=..., description="The unique identifier of the field option to delete. This is the specific choice or value being removed from the custom field.")
    field_id: str = Field(default=..., description="The unique identifier of the custom field that contains the field option being deleted.")
class DeleteIncidentTypeCustomFieldFieldOptionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON. Only application/json is supported.")
class DeleteIncidentTypeCustomFieldFieldOptionRequest(StrictModel):
    """Remove a specific field option from a custom field associated with an incident type. This allows you to delete predefined choices or values that were previously available for selection in that custom field."""
    path: DeleteIncidentTypeCustomFieldFieldOptionRequestPath
    header: DeleteIncidentTypeCustomFieldFieldOptionRequestHeader

# Operation: list_license_allocations
class ListLicenseAllocationsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default PagerDuty JSON API version 2 format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON. This is the only supported content type for this operation.")
class ListLicenseAllocationsRequest(StrictModel):
    """Retrieve all licenses allocated to users within your PagerDuty account. This operation returns a list of license assignments showing which users have been granted specific license types."""
    header: ListLicenseAllocationsRequestHeader

# Operation: list_licenses
class ListLicensesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to the PagerDuty JSON API version 2 format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request content type. Must be JSON format.")
class ListLicensesRequest(StrictModel):
    """Retrieve all licenses associated with your PagerDuty account. Returns a collection of license objects with their current status and details."""
    header: ListLicensesRequestHeader

# Operation: list_incident_log_entries_account
class ListLogEntriesRequestQuery(StrictModel):
    time_zone: str | None = Field(default=None, description="Time zone for rendering timestamps in results. Defaults to your account's configured time zone. Specify as a valid IANA time zone identifier.", json_schema_extra={'format': 'tzinfo'})
    since: str | None = Field(default=None, description="Start of the date range to search, specified in ISO 8601 date-time format. Only log entries on or after this time will be included.", json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="End of the date range to search, specified in ISO 8601 date-time format. Only log entries on or before this time will be included.", json_schema_extra={'format': 'date-time'})
    is_overview: bool | None = Field(default=None, description="When true, returns only the most important log entries that represent significant changes to incidents. Defaults to false, which returns all entries.")
    include: Annotated[Literal["incidents", "services", "channels", "teams"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Array of related resource types to include in the response. Valid options are incidents, services, channels, and teams. Helps provide context for log entries.")
    team_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="team_ids[]", serialization_alias="team_ids[]", description="Array of team IDs to filter results. Only log entries related to the specified teams will be returned. Requires your account to have the teams ability enabled.")
class ListLogEntriesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="HTTP header specifying the API version. Must be set to application/vnd.pagerduty+json;version=2 for this operation.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="HTTP header specifying the request content type. Must be application/json.")
class ListLogEntriesRequest(StrictModel):
    """Retrieve all incident log entries across your account, showing events and changes that occur to incidents. Optionally filter by date range, teams, and incident details to find specific activity."""
    query: ListLogEntriesRequestQuery | None = None
    header: ListLogEntriesRequestHeader

# Operation: get_log_entry
class GetLogEntryRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the log entry to retrieve.")
class GetLogEntryRequestQuery(StrictModel):
    time_zone: str | None = Field(default=None, description="Time zone for rendering timestamps in the response, specified in IANA tzinfo format (e.g., America/New_York). Defaults to the account's configured time zone if not provided.", json_schema_extra={'format': 'tzinfo'})
    include: Annotated[Literal["incidents", "services", "channels", "teams"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Array of related resource types to include in the response. Valid options are incidents, services, channels, and teams. Omit this parameter to return only the log entry itself.")
class GetLogEntryRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to application/vnd.pagerduty+json;version=2 to use this operation.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class GetLogEntryRequest(StrictModel):
    """Retrieve detailed information about a specific incident log entry, including raw event data and related resources. Log entries represent all events that occur during an incident's lifecycle."""
    path: GetLogEntryRequestPath
    query: GetLogEntryRequestQuery | None = None
    header: GetLogEntryRequestHeader

# Operation: update_log_entry_channel
class UpdateLogEntryChannelRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the log entry resource to update.")
class UpdateLogEntryChannelRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2 for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be JSON format.")
    from_: str = Field(default=..., validation_alias="From", serialization_alias="From", description="Email address of a valid user account associated with your PagerDuty instance. Required to authenticate the request.", json_schema_extra={'format': 'email'})
class UpdateLogEntryChannelRequestBodyChannel(StrictModel):
    details: str = Field(default=..., validation_alias="details", serialization_alias="details", description="The updated channel details. Provide the new information for the channel being modified.")
    type_: Literal["web_trigger", "mobile"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The channel type (web_trigger or mobile). This value cannot be changed and must match the existing channel type on the log entry.")
class UpdateLogEntryChannelRequestBody(StrictModel):
    """The log entry channel to be updated."""
    channel: UpdateLogEntryChannelRequestBodyChannel
class UpdateLogEntryChannelRequest(StrictModel):
    """Update the channel information for an existing incident log entry. Modify channel details while preserving the channel type, which cannot be changed."""
    path: UpdateLogEntryChannelRequestPath
    header: UpdateLogEntryChannelRequestHeader
    body: UpdateLogEntryChannelRequestBody

# Operation: list_maintenance_windows
class ListMaintenanceWindowsRequestQuery(StrictModel):
    team_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="team_ids[]", serialization_alias="team_ids[]", description="Filter results to maintenance windows associated with specific teams. Requires account to have the teams ability. Provide as an array of team identifiers.")
    service_ids: list[str] | None = Field(default=None, validation_alias="service_ids[]", serialization_alias="service_ids[]", description="Filter results to maintenance windows associated with specific services. Provide as an array of service identifiers.")
    include: Annotated[Literal["teams", "services", "users"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Include additional related data in the response. Choose from teams, services, or users to expand the response with full object details.")
    filter_: Literal["past", "future", "ongoing", "open", "all"] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter maintenance windows by temporal state: past (completed), future (scheduled), ongoing (currently active), open (not yet started or currently active), or all (no filtering).")
class ListMaintenanceWindowsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to specify the API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request content type. Must be application/json.")
class ListMaintenanceWindowsRequest(StrictModel):
    """Retrieve maintenance windows with optional filtering by service, team, or temporal state (past, present, future). Maintenance windows temporarily disable services during scheduled maintenance periods."""
    query: ListMaintenanceWindowsRequestQuery | None = None
    header: ListMaintenanceWindowsRequestHeader

# Operation: create_maintenance_window
class CreateMaintenanceWindowRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API version header. Use the default PagerDuty v2 JSON format for request and response serialization.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request body content type. Must be JSON format.")
    from_: str = Field(default=..., validation_alias="From", serialization_alias="From", description="Email address of a valid user account associated with your PagerDuty account. This user will be recorded as the creator of the maintenance window.", json_schema_extra={'format': 'email'})
class CreateMaintenanceWindowRequestBody(StrictModel):
    """The maintenance window object."""
    maintenance_window: MaintenanceWindow = Field(default=..., description="Maintenance window configuration object containing service IDs, start time, and end time. Refer to the API Concepts Document for the required schema and field specifications.")
class CreateMaintenanceWindowRequest(StrictModel):
    """Create a new maintenance window to temporarily disable one or more services for a specified period. Services in maintenance will not generate new incidents."""
    header: CreateMaintenanceWindowRequestHeader
    body: CreateMaintenanceWindowRequestBody

# Operation: get_maintenance_window
class GetMaintenanceWindowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the maintenance window to retrieve.")
class GetMaintenanceWindowRequestQuery(StrictModel):
    include: Annotated[Literal["teams", "services", "users"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array of related resources to include in the response. Supported values are teams, services, and users. Specify multiple values to include multiple resource types.")
class GetMaintenanceWindowRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to request the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type of the request body. Must be application/json.")
class GetMaintenanceWindowRequest(StrictModel):
    """Retrieve a specific maintenance window by ID. A maintenance window temporarily disables one or more services for a scheduled period of time."""
    path: GetMaintenanceWindowRequestPath
    query: GetMaintenanceWindowRequestQuery | None = None
    header: GetMaintenanceWindowRequestHeader

# Operation: update_maintenance_window
class UpdateMaintenanceWindowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the maintenance window to update.")
class UpdateMaintenanceWindowRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be JSON.")
class UpdateMaintenanceWindowRequestBody(StrictModel):
    """The maintenance window to be updated."""
    maintenance_window: MaintenanceWindow = Field(default=..., description="The maintenance window object containing the fields to update, such as the affected services and the start/end times for the maintenance period.")
class UpdateMaintenanceWindowRequest(StrictModel):
    """Update an existing maintenance window to modify the services affected or the time period during which they are temporarily disabled."""
    path: UpdateMaintenanceWindowRequestPath
    header: UpdateMaintenanceWindowRequestHeader
    body: UpdateMaintenanceWindowRequestBody

# Operation: delete_maintenance_window
class DeleteMaintenanceWindowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the maintenance window to delete or end.")
class DeleteMaintenanceWindowRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and schema version (defaults to PagerDuty API v2).")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body, must be JSON.")
class DeleteMaintenanceWindowRequest(StrictModel):
    """Delete a future maintenance window or end an ongoing one. Maintenance windows that have already ended cannot be deleted."""
    path: DeleteMaintenanceWindowRequestPath
    header: DeleteMaintenanceWindowRequestHeader

# Operation: list_notifications
class ListNotificationsRequestQuery(StrictModel):
    time_zone: str | None = Field(default=None, description="Time zone for rendering results in IANA tzinfo format (e.g., America/New_York). Defaults to the account's configured time zone if not specified.", json_schema_extra={'format': 'tzinfo'})
    since: str = Field(default=..., description="Start of the search date range in ISO 8601 format (date-time). The time component is optional; if omitted, defaults to the start of the day.", json_schema_extra={'format': 'date-time'})
    until: str = Field(default=..., description="End of the search date range in ISO 8601 format (date-time), matching the format of the since parameter. The date range span must not exceed 3 months.", json_schema_extra={'format': 'date-time'})
    filter_: Literal["sms_notification", "email_notification", "phone_notification", "push_notification"] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results to a single notification type: sms_notification, email_notification, phone_notification, or push_notification. Omit to return all notification types.")
    include: Annotated[Literal["users"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Array of additional related resources to include in the response. Currently supports 'users' to include user details associated with notifications.")
class ListNotificationsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="HTTP Accept header for API versioning. Must be set to application/vnd.pagerduty+json;version=2 to request the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="HTTP Content-Type header specifying the request body format. Must be application/json.")
class ListNotificationsRequest(StrictModel):
    """Retrieve notifications triggered by incidents within a specified time range, with optional filtering by notification type (SMS, email, phone, or push). Results can be rendered in a specific time zone and include related user details."""
    query: ListNotificationsRequestQuery
    header: ListNotificationsRequestHeader

# Operation: revoke_user_oauth_delegations
class DeleteOauthDelegationsRequestQuery(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user whose OAuth delegations should be revoked.")
    type_: Literal["mobile", "web"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The delegation type(s) to revoke: 'mobile' to sign out of the mobile app, 'web' to sign out of the web app, or both types separated by commas (e.g., 'web,mobile').")
class DeleteOauthDelegationsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Defaults to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be application/json.")
class DeleteOauthDelegationsRequest(StrictModel):
    """Revoke OAuth delegations for a user by type, effectively signing them out of the specified app(s). This synchronous operation revokes access for mobile app, web app, or both delegation types."""
    query: DeleteOauthDelegationsRequestQuery
    header: DeleteOauthDelegationsRequestHeader

# Operation: list_oncalls
class ListOnCallsRequestQuery(StrictModel):
    time_zone: str | None = Field(default=None, description="Time zone for rendering results (e.g., America/New_York, Europe/London). Defaults to the account's configured time zone. Must be a valid IANA time zone identifier.", json_schema_extra={'format': 'tzinfo'})
    include: Annotated[Literal["escalation_policies", "users", "schedules"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Include additional related resource details in the response. Specify any combination of escalation policies, users, or schedules to expand the response with full resource objects.")
    user_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="user_ids[]", serialization_alias="user_ids[]", description="Filter results to show on-calls only for the specified user IDs. Provide as a comma-separated list or array of user identifiers.")
    escalation_policy_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="escalation_policy_ids[]", serialization_alias="escalation_policy_ids[]", description="Filter results to show on-calls only for the specified escalation policy IDs. Provide as a comma-separated list or array of escalation policy identifiers.")
    schedule_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="schedule_ids[]", serialization_alias="schedule_ids[]", description="Filter results to show on-calls only for the specified schedule IDs. Provide as a comma-separated list or array of schedule identifiers. Include `null` in the array to also return permanent on-calls from direct user escalation targets.")
    since: str | None = Field(default=None, description="Start of the time range to search (ISO 8601 format). On-call periods overlapping this range are included. Defaults to the current time. On-call shifts are limited to 90 days in the future.", json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="End of the time range to search (ISO 8601 format). On-call periods overlapping this range are included. Defaults to the current time. Must be at or after the `since` time, and on-call shifts are limited to 90 days in the future.", json_schema_extra={'format': 'date-time'})
    earliest: bool | None = Field(default=None, description="When enabled, returns only the earliest on-call for each unique combination of escalation policy, escalation level, and user. Useful for identifying the next upcoming on-calls.")
class ListOnCallsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="HTTP Accept header for API versioning. Must be set to the PagerDuty API version 2 media type.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="HTTP Content-Type header specifying the request body format. Must be application/json.")
class ListOnCallsRequest(StrictModel):
    """Retrieve all on-call entries within a specified time range. An on-call represents a contiguous period during which a user is assigned to an escalation policy. Results can be filtered by user, escalation policy, or schedule, and optionally enriched with related resource details."""
    query: ListOnCallsRequestQuery | None = None
    header: ListOnCallsRequestHeader

# Operation: list_paused_incident_report_alerts
class GetPausedIncidentReportAlertsRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="Start of the date range for the report in ISO 8601 date-time format (e.g., 2024-01-15T10:30:00Z). If omitted, defaults to 6 months before the until date.", json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="End of the date range for the report in ISO 8601 date-time format (e.g., 2024-01-15T10:30:00Z). If omitted, defaults to the current time.", json_schema_extra={'format': 'date-time'})
    service_id: str | None = Field(default=None, description="Limit results to alerts for a specific service by providing the service ID (e.g., P123456). Omit to include all services.")
    suspended_by: Literal["auto_pause", "rules"] | None = Field(default=None, description="Filter alerts by suspension source: 'auto_pause' for alerts suspended by automatic pause rules, or 'rules' for alerts suspended by event rules. Omit to include both sources.")
class GetPausedIncidentReportAlertsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to 'application/vnd.pagerduty+json;version=2' to request the correct response format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be 'application/json'.")
class GetPausedIncidentReportAlertsRequest(StrictModel):
    """Retrieve the 5 most recent alerts triggered after being paused and the 5 most recent alerts resolved after being paused within a specified reporting period (up to 6 months lookback). Available only with Event Intelligence package or Digital Operations plan."""
    query: GetPausedIncidentReportAlertsRequestQuery | None = None
    header: GetPausedIncidentReportAlertsRequestHeader

# Operation: list_paused_incident_report_counts
class GetPausedIncidentReportCountsRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="Start of the reporting period as an ISO 8601 datetime. If omitted, defaults to 6 months before the until date.", json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="End of the reporting period as an ISO 8601 datetime. If omitted, defaults to the current time.", json_schema_extra={'format': 'date-time'})
    service_id: str | None = Field(default=None, description="Filter results to a specific service by its ID (e.g., P123456). Omit to include all services.")
    suspended_by: Literal["auto_pause", "rules"] | None = Field(default=None, description="Filter results by the source of the pause: auto_pause for automatically paused incidents, or rules for incidents paused by Event Rules.")
class GetPausedIncidentReportCountsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class GetPausedIncidentReportCountsRequest(StrictModel):
    """Retrieve reporting counts for paused incidents over a specified period (up to 6 months lookback). Available only with Event Intelligence package or Digital Operations plan."""
    query: GetPausedIncidentReportCountsRequestQuery | None = None
    header: GetPausedIncidentReportCountsRequestHeader

# Operation: list_priorities
class ListPrioritiesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to the PagerDuty JSON API version 2 format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request content type. Must be application/json.")
class ListPrioritiesRequest(StrictModel):
    """Retrieve all priorities ordered by severity from most to least severe. Priorities are labels that represent the importance and impact of incidents in PagerDuty."""
    header: ListPrioritiesRequestHeader

# Operation: delete_ruleset_event_rule
class DeleteRulesetEventRuleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the ruleset containing the event rule to delete.")
    rule_id: str = Field(default=..., description="The unique identifier of the event rule to delete.")
class DeleteRulesetEventRuleRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request. Must be application/json.")
class DeleteRulesetEventRuleRequest(StrictModel):
    """Delete an Event Rule from a ruleset. Note: Rulesets and Event Rules are end-of-life; migrate to Event Orchestration for improved functionality and ongoing support."""
    path: DeleteRulesetEventRuleRequestPath
    header: DeleteRulesetEventRuleRequestHeader

# Operation: list_schedules_audit_records
class ListSchedulesAuditRecordsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule for which to retrieve audit records.")
class ListSchedulesAuditRecordsRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="The start of the date range for the audit search (ISO 8601 format). Defaults to 24 hours before the current time if not specified.", json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="The end of the date range for the audit search (ISO 8601 format). Defaults to the current time if not specified. Cannot be more than 31 days after the `since` parameter.", json_schema_extra={'format': 'date-time'})
class ListSchedulesAuditRecordsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to `application/vnd.pagerduty+json;version=2` to specify the PagerDuty API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be `application/json`.")
class ListSchedulesAuditRecordsRequest(StrictModel):
    """Retrieve audit records for a specific schedule, sorted by execution time from newest to oldest. Supports date range filtering and cursor-based pagination."""
    path: ListSchedulesAuditRecordsRequestPath
    query: ListSchedulesAuditRecordsRequestQuery | None = None
    header: ListSchedulesAuditRecordsRequestHeader

# Operation: list_schedule_users
class ListScheduleUsersRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule to query for on-call users.")
class ListScheduleUsersRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="The start of the time range to search, specified as an ISO 8601 date-time. If omitted, defaults to the current time.", json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="The end of the time range to search, specified as an ISO 8601 date-time. If omitted, defaults to the current time.", json_schema_extra={'format': 'date-time'})
class ListScheduleUsersRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to `application/vnd.pagerduty+json;version=2` to use the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the response content type. Must be `application/json`.")
class ListScheduleUsersRequest(StrictModel):
    """Retrieve all users currently on call for a specific schedule within an optional time range. Use this to see who is responsible for on-call duties during a given period."""
    path: ListScheduleUsersRequestPath
    query: ListScheduleUsersRequestQuery | None = None
    header: ListScheduleUsersRequestHeader

# Operation: preview_schedule
class CreateSchedulePreviewRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="The start of the date range for the preview, specified in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="The end of the date range for the preview, specified in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    overflow: bool | None = Field(default=None, description="When true, schedule entries that span beyond the date range bounds are returned in full; when false (default), entries are truncated at the range boundaries.")
class CreateSchedulePreviewRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="HTTP header specifying the API version. Must be set to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="HTTP header specifying the request body format. Must be application/json.")
class CreateSchedulePreviewRequestBody(StrictModel):
    """The schedule to be previewed."""
    schedule: Schedule = Field(default=..., description="The schedule configuration object to preview, containing rotation rules and user assignments.")
class CreateSchedulePreviewRequest(StrictModel):
    """Generate a preview of an on-call schedule without persisting it, showing what user coverage would look like across a specified time range."""
    query: CreateSchedulePreviewRequestQuery | None = None
    header: CreateSchedulePreviewRequestHeader
    body: CreateSchedulePreviewRequestBody

# Operation: associate_service_dependencies
class CreateServiceDependencyRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to the PagerDuty JSON media type version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format. Must be JSON.")
class CreateServiceDependencyRequestBody(StrictModel):
    relationships: list[CreateServiceDependencyBodyRelationshipsItem] | None = Field(default=None, description="Array of service dependency objects to create. Each object defines a relationship between two services. Order is preserved as provided.")
class CreateServiceDependencyRequest(StrictModel):
    """Create dependencies between two services within a business service model. Each service can have up to 2,000 dependencies with a maximum depth of 100; the API will return an error if either limit is exceeded."""
    header: CreateServiceDependencyRequestHeader
    body: CreateServiceDependencyRequestBody | None = None

# Operation: get_business_service_dependencies
class GetBusinessServiceServiceDependenciesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Business Service resource.")
class GetBusinessServiceServiceDependenciesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty JSON API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type for the request body. Must be application/json.")
class GetBusinessServiceServiceDependenciesRequest(StrictModel):
    """Retrieve all immediate dependencies of a Business Service, which may span multiple technical services and teams. Use this to understand what services a Business Service depends on."""
    path: GetBusinessServiceServiceDependenciesRequestPath
    header: GetBusinessServiceServiceDependenciesRequestHeader

# Operation: remove_service_dependencies
class DeleteServiceDependencyRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to specify the API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be application/json.")
class DeleteServiceDependencyRequestBody(StrictModel):
    relationships: list[DeleteServiceDependencyBodyRelationshipsItem] | None = Field(default=None, description="Array of service dependency relationships to remove. Each entry specifies a dependency pair to disassociate. Order is not significant.")
class DeleteServiceDependencyRequest(StrictModel):
    """Remove dependencies between services in a business service model. This operation disassociates technical service relationships that may span multiple teams."""
    header: DeleteServiceDependencyRequestHeader
    body: DeleteServiceDependencyRequestBody | None = None

# Operation: get_technical_service_dependencies
class GetTechnicalServiceServiceDependenciesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the technical service for which to retrieve dependencies.")
class GetTechnicalServiceServiceDependenciesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty JSON API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type for the request body. Must be application/json.")
class GetTechnicalServiceServiceDependenciesRequest(StrictModel):
    """Retrieve all immediate dependencies for a specified technical service. This returns the services that the given service directly depends on to function."""
    path: GetTechnicalServiceServiceDependenciesRequestPath
    header: GetTechnicalServiceServiceDependenciesRequestHeader

# Operation: list_services
class ListServicesRequestQuery(StrictModel):
    team_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="team_ids[]", serialization_alias="team_ids[]", description="Filter results to only include services associated with specific teams. Requires the `teams` ability on your account. Provide an array of team IDs.")
    time_zone: str | None = Field(default=None, description="Specify the time zone for rendering results in the response. Defaults to your account's configured time zone. Use standard time zone identifiers (tzinfo format).", json_schema_extra={'format': 'tzinfo'})
    sort_by: Literal["name", "name:asc", "name:desc"] | None = Field(default=None, description="Sort results by the specified field. Defaults to sorting by service name in ascending order. Supports sorting by name in ascending or descending order.")
    include: Annotated[Literal["escalation_policies", "teams", "integrations", "auto_pause_notifications_parameters"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Include additional related data in the response. Specify an array of resource types to expand: escalation policies, teams, integrations, or auto-pause notification parameters.")
class ListServicesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="HTTP header specifying the API version. Required for all requests. Must be set to `application/vnd.pagerduty+json;version=2`.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="HTTP header specifying the request content type. Must be `application/json`.")
class ListServicesRequest(StrictModel):
    """Retrieve a list of services in your PagerDuty account. Services represent applications, components, or teams that can have incidents opened against them."""
    query: ListServicesRequestQuery | None = None
    header: ListServicesRequestHeader

# Operation: create_service
class CreateServiceRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to 'application/vnd.pagerduty+json;version=2'.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request body content type. Must be 'application/json'.")
class CreateServiceRequestBody(StrictModel):
    """The service to be created"""
    service: Service = Field(default=..., description="Service object containing the service configuration. Required fields and structure depend on the service definition schema. Note: accounts are limited to 25,000 services; if this limit is reached, the API will return an error. Services are also limited to 100,000 open incidents; if exceeded and auto-resolution is disabled, the auto_resolve_timeout will automatically be set to 1 day (84600 seconds).")
class CreateServiceRequest(StrictModel):
    """Create a new service to represent an application, component, or team for incident management. If a status is provided, it must be set to 'active'; use a separate update request to change the status later."""
    header: CreateServiceRequestHeader
    body: CreateServiceRequestBody

# Operation: get_service
class GetServiceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the service to retrieve.")
class GetServiceRequestQuery(StrictModel):
    include: Annotated[Literal["escalation_policies", "teams", "auto_pause_notifications_parameters", "integrations"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array of related resources to include in the response. Valid options are escalation_policies, teams, auto_pause_notifications_parameters, and integrations. Specify multiple values to include multiple resource types.")
class GetServiceRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class GetServiceRequest(StrictModel):
    """Retrieve detailed information about a service, which represents an application, component, or team for incident management. Optionally include related resources such as escalation policies, teams, auto-pause settings, or integrations."""
    path: GetServiceRequestPath
    query: GetServiceRequestQuery | None = None
    header: GetServiceRequestHeader

# Operation: update_service
class UpdateServiceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the service to update.")
class UpdateServiceRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty API v2 format for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be JSON format.")
class UpdateServiceRequestBody(StrictModel):
    """The service to be updated."""
    service: Service = Field(default=..., description="The service object containing the fields to update. Refer to the service schema for available properties and validation rules.")
class UpdateServiceRequest(StrictModel):
    """Update an existing service's configuration. Services represent applications, components, or teams for incident management. Note: Services are limited to 100,000 open incidents; disabling auto_resolve_timeout when at capacity will result in an error."""
    path: UpdateServiceRequestPath
    header: UpdateServiceRequestHeader
    body: UpdateServiceRequestBody

# Operation: delete_service
class DeleteServiceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the service to delete.")
class DeleteServiceRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be application/json.")
class DeleteServiceRequest(StrictModel):
    """Permanently delete a service, making it inaccessible in the web UI and preventing new incidents from being created against it. Services represent applications, components, or teams for incident management."""
    path: DeleteServiceRequestPath
    header: DeleteServiceRequestHeader

# Operation: list_service_audit_records
class ListServiceAuditRecordsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the service for which to retrieve audit records.")
class ListServiceAuditRecordsRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="The start of the date range for the search in ISO 8601 format. Defaults to 24 hours before the current time if not specified.", json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="The end of the date range for the search in ISO 8601 format. Defaults to the current time if not specified. Cannot be more than 31 days after the `since` parameter.", json_schema_extra={'format': 'date-time'})
class ListServiceAuditRecordsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="HTTP header specifying the API version. Must be set to `application/vnd.pagerduty+json;version=2` for this operation.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="HTTP header specifying the request content type. Must be `application/json`.")
class ListServiceAuditRecordsRequest(StrictModel):
    """Retrieve audit records for a specific service, sorted by execution time from newest to oldest. Results support cursor-based pagination for efficient browsing of large datasets."""
    path: ListServiceAuditRecordsRequestPath
    query: ListServiceAuditRecordsRequestQuery | None = None
    header: ListServiceAuditRecordsRequestHeader

# Operation: list_service_change_events
class ListServiceChangeEventsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the service for which to retrieve change events.")
class ListServiceChangeEventsRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="Filter results to changes occurring on or after this date. Specify as a UTC ISO 8601 datetime string (format: YYYY-MM-DDThh:mm:ssZ). Non-UTC datetimes will return an error.", pattern='YYYY-MM-DDThh:mm:ssZ', json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="Filter results to changes occurring on or before this date. Specify as a UTC ISO 8601 datetime string (format: YYYY-MM-DDThh:mm:ssZ). Non-UTC datetimes will return an error.", pattern='YYYY-MM-DDThh:mm:ssZ', json_schema_extra={'format': 'date-time'})
    team_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="team_ids[]", serialization_alias="team_ids[]", description="Restrict results to change events associated with specific teams. Provide an array of team IDs. Requires the account to have the `teams` ability.")
    integration_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="integration_ids[]", serialization_alias="integration_ids[]", description="Restrict results to change events associated with specific integrations. Provide an array of integration IDs.")
class ListServiceChangeEventsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Defaults to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class ListServiceChangeEventsRequest(StrictModel):
    """Retrieve all change events for a specific service, with optional filtering by date range, team, or integration. Change events track modifications and updates to the service over time."""
    path: ListServiceChangeEventsRequestPath
    query: ListServiceChangeEventsRequestQuery | None = None
    header: ListServiceChangeEventsRequestHeader

# Operation: create_service_integration
class CreateServiceIntegrationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the service to which the integration will be added.")
class CreateServiceIntegrationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2 for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class CreateServiceIntegrationRequestBody(StrictModel):
    """The integration to be created"""
    integration: Integration = Field(default=..., description="The integration configuration object containing the details of the integration to be created.")
class CreateServiceIntegrationRequest(StrictModel):
    """Create a new integration for a service. Integrations allow you to connect external applications, components, or tools to a service for incident management."""
    path: CreateServiceIntegrationRequestPath
    header: CreateServiceIntegrationRequestHeader
    body: CreateServiceIntegrationRequestBody

# Operation: get_service_integration
class GetServiceIntegrationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the service resource.")
    integration_id: str = Field(default=..., description="The unique identifier of the integration attached to the service.")
class GetServiceIntegrationRequestQuery(StrictModel):
    include: Annotated[Literal["services", "vendors"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array of related resources to include in the response. Specify 'services' to include parent service details or 'vendors' to include vendor information.")
class GetServiceIntegrationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class GetServiceIntegrationRequest(StrictModel):
    """Retrieve detailed information about a specific integration configured for a service. Use this to view integration settings, status, and configuration details for a service that represents an application, component, or team."""
    path: GetServiceIntegrationRequestPath
    query: GetServiceIntegrationRequestQuery | None = None
    header: GetServiceIntegrationRequestHeader

# Operation: update_service_integration
class UpdateServiceIntegrationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the service containing the integration to update.")
    integration_id: str = Field(default=..., description="The unique identifier of the integration within the service to update.")
class UpdateServiceIntegrationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to use the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type of the request body. Must be application/json.")
class UpdateServiceIntegrationRequestBody(StrictModel):
    """The integration to be updated"""
    integration: Integration = Field(default=..., description="The integration object containing the fields to update. Refer to the API documentation for the complete schema of updatable fields.")
class UpdateServiceIntegrationRequest(StrictModel):
    """Update an existing integration for a service. Services represent applications, components, or teams against which you can open incidents."""
    path: UpdateServiceIntegrationRequestPath
    header: UpdateServiceIntegrationRequestHeader
    body: UpdateServiceIntegrationRequestBody

# Operation: list_service_event_rules
class ListServiceEventRulesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the service whose event rules you want to list.")
class ListServiceEventRulesRequestQuery(StrictModel):
    include: Annotated[Literal["migrated_metadata"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array to include additional metadata in the response, such as migrated_metadata to show migration status information.")
class ListServiceEventRulesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class ListServiceEventRulesRequest(StrictModel):
    """Retrieve all Event Rules configured for a specific service. Note: Event Rules are deprecated; migrate to Event Orchestration for improved functionality and ongoing support."""
    path: ListServiceEventRulesRequestPath
    query: ListServiceEventRulesRequestQuery | None = None
    header: ListServiceEventRulesRequestHeader

# Operation: delete_service_event_rule
class DeleteServiceEventRuleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Service from which the Event Rule will be deleted.")
    rule_id: str = Field(default=..., description="The unique identifier of the Event Rule to be deleted.")
class DeleteServiceEventRuleRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to specify the API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be application/json.")
class DeleteServiceEventRuleRequest(StrictModel):
    """Remove an Event Rule from a Service. Note: Event Rules are end-of-life; migrate to Event Orchestration for improved functionality and ongoing support."""
    path: DeleteServiceEventRuleRequestPath
    header: DeleteServiceEventRuleRequestHeader

# Operation: list_service_custom_fields
class ListServiceCustomFieldsRequestQuery(StrictModel):
    include: Annotated[Literal["field_options"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array of additional details to include in the response. Specify 'field_options' to include the available options for each custom field.")
class ListServiceCustomFieldsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be set to JSON format.")
class ListServiceCustomFieldsRequest(StrictModel):
    """Retrieve all custom fields available for Services in PagerDuty. Optionally include additional details such as field options."""
    query: ListServiceCustomFieldsRequestQuery | None = None
    header: ListServiceCustomFieldsRequestHeader

# Operation: get_service_custom_field
class GetServiceCustomFieldRequestPath(StrictModel):
    field_id: str = Field(default=..., description="The unique identifier of the custom field to retrieve.")
class GetServiceCustomFieldRequestQuery(StrictModel):
    include: Annotated[Literal["field_options"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array of related data to include in the response. Specify 'field_options' to include the list of available options for this field.")
class GetServiceCustomFieldRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty API v2 format for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be JSON format.")
class GetServiceCustomFieldRequest(StrictModel):
    """Retrieve detailed information about a custom field for PagerDuty Services, including its configuration and available options."""
    path: GetServiceCustomFieldRequestPath
    query: GetServiceCustomFieldRequestQuery | None = None
    header: GetServiceCustomFieldRequestHeader

# Operation: update_service_custom_field
class UpdateServiceCustomFieldRequestPath(StrictModel):
    field_id: str = Field(default=..., description="The unique identifier of the custom field to update.")
class UpdateServiceCustomFieldRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be JSON format.")
class UpdateServiceCustomFieldRequestBodyField(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A description explaining what data this field contains. Limited to 1000 characters.", max_length=1000)
    display_name: str | None = Field(default=None, validation_alias="display_name", serialization_alias="display_name", description="The human-readable name displayed for this field. Must be unique within the account and limited to 50 characters.", max_length=50)
    enabled: Literal[True, False] | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Whether this field is active and available for use.")
    field_options: list[UpdateServiceCustomFieldBodyFieldFieldOptionsItem] | None = Field(default=None, validation_alias="field_options", serialization_alias="field_options", description="List of field options to manage. An empty array deletes all options; omitting this field preserves existing options; unlisted existing options are deleted unless they are the current default value.")
class UpdateServiceCustomFieldRequestBody(StrictModel):
    field: UpdateServiceCustomFieldRequestBodyField | None = None
class UpdateServiceCustomFieldRequest(StrictModel):
    """Update a custom field for services, including its display name, description, enabled status, and field options. Changes to field options support selective updates, deletions, or complete replacement."""
    path: UpdateServiceCustomFieldRequestPath
    header: UpdateServiceCustomFieldRequestHeader
    body: UpdateServiceCustomFieldRequestBody | None = None

# Operation: delete_service_custom_field
class DeleteServiceCustomFieldRequestPath(StrictModel):
    field_id: str = Field(default=..., description="The unique identifier of the custom field to delete.")
class DeleteServiceCustomFieldRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to JSON format.")
class DeleteServiceCustomFieldRequest(StrictModel):
    """Permanently delete a custom field from Services. This operation requires write access to custom fields and cannot be undone."""
    path: DeleteServiceCustomFieldRequestPath
    header: DeleteServiceCustomFieldRequestHeader

# Operation: list_custom_field_options
class ListServiceCustomFieldOptionsRequestPath(StrictModel):
    field_id: str = Field(default=..., description="The unique identifier of the custom field whose options you want to list.")
class ListServiceCustomFieldOptionsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type for the request body. Must be JSON format.")
class ListServiceCustomFieldOptionsRequest(StrictModel):
    """Retrieve all available options for a specific custom field in PagerDuty services. Use this to populate dropdowns or validate field option values."""
    path: ListServiceCustomFieldOptionsRequestPath
    header: ListServiceCustomFieldOptionsRequestHeader

# Operation: create_service_custom_field_option
class CreateServiceCustomFieldOptionRequestPath(StrictModel):
    field_id: str = Field(default=..., description="The unique identifier of the custom field to which this option will be added.")
class CreateServiceCustomFieldOptionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version to use.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body, must be JSON.")
class CreateServiceCustomFieldOptionRequestBodyFieldOptionData(StrictModel):
    data_type: Literal["string"] = Field(default=..., validation_alias="data_type", serialization_alias="data_type", description="The data type of this option, which must match the parent field's data type. Currently supports string values.")
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The value for this field option. Must be unique among all options within the same field and cannot exceed 200 characters.", max_length=200)
class CreateServiceCustomFieldOptionRequestBodyFieldOption(StrictModel):
    data: CreateServiceCustomFieldOptionRequestBodyFieldOptionData
class CreateServiceCustomFieldOptionRequestBody(StrictModel):
    field_option: CreateServiceCustomFieldOptionRequestBodyFieldOption
class CreateServiceCustomFieldOptionRequest(StrictModel):
    """Create a new option for a custom field in a service. The option value must be unique within the field and match the field's data type."""
    path: CreateServiceCustomFieldOptionRequestPath
    header: CreateServiceCustomFieldOptionRequestHeader
    body: CreateServiceCustomFieldOptionRequestBody

# Operation: get_service_custom_field_option
class GetServiceCustomFieldOptionRequestPath(StrictModel):
    field_id: str = Field(default=..., description="The unique identifier of the custom field that contains the field option.")
    field_option_id: str = Field(default=..., description="The unique identifier of the specific field option to retrieve.")
class GetServiceCustomFieldOptionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty JSON API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body. Must be set to application/json.")
class GetServiceCustomFieldOptionRequest(StrictModel):
    """Retrieve a specific field option for a custom field in a service. This operation requires read access to custom fields and returns the configuration details of the requested field option."""
    path: GetServiceCustomFieldOptionRequestPath
    header: GetServiceCustomFieldOptionRequestHeader

# Operation: delete_service_custom_field_option
class DeleteServiceCustomFieldOptionRequestPath(StrictModel):
    field_id: str = Field(default=..., description="The unique identifier of the custom field containing the option to delete.")
    field_option_id: str = Field(default=..., description="The unique identifier of the field option to delete.")
class DeleteServiceCustomFieldOptionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to the PagerDuty JSON API version 2 format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be JSON format.")
class DeleteServiceCustomFieldOptionRequest(StrictModel):
    """Remove a specific field option from a custom field in a service. This permanently deletes the option and cannot be undone."""
    path: DeleteServiceCustomFieldOptionRequestPath
    header: DeleteServiceCustomFieldOptionRequestHeader

# Operation: get_service_custom_field_values
class GetServiceCustomFieldValuesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the service for which to retrieve custom field values.")
class GetServiceCustomFieldValuesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and API version. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to application/json.")
class GetServiceCustomFieldValuesRequest(StrictModel):
    """Retrieve all custom field values associated with a specific service. Returns the current values of custom fields configured for the service."""
    path: GetServiceCustomFieldValuesRequestPath
    header: GetServiceCustomFieldValuesRequestHeader

# Operation: update_service_custom_field_values
class UpdateServiceCustomFieldValuesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the service resource to update.")
class UpdateServiceCustomFieldValuesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to the PagerDuty API version 2 media type.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be JSON format.")
class UpdateServiceCustomFieldValuesRequestBody(StrictModel):
    custom_fields: list[ServiceCustomFieldsFieldValueUpdateModel] = Field(default=..., description="An array of custom field objects to set for the service. Each object should contain the field identifier and its corresponding value.")
class UpdateServiceCustomFieldValuesRequest(StrictModel):
    """Update custom field values for a specific service. This operation allows you to set or modify custom field data associated with a service resource."""
    path: UpdateServiceCustomFieldValuesRequestPath
    header: UpdateServiceCustomFieldValuesRequestHeader
    body: UpdateServiceCustomFieldValuesRequestBody

# Operation: list_service_feature_enablements
class ListServiceFeatureEnablementsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the service for which to retrieve feature enablements.")
class ListServiceFeatureEnablementsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body. Must be set to JSON format.")
class ListServiceFeatureEnablementsRequest(StrictModel):
    """Retrieve all feature enablement settings for a service, including AIOps features. Services with the AIOps product addon have AIOps enabled by default, and a warning is returned if the account lacks AIOps entitlement."""
    path: ListServiceFeatureEnablementsRequestPath
    header: ListServiceFeatureEnablementsRequestHeader

# Operation: update_service_feature_enablement
class UpdateServiceFeatureEnablementRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the service resource to update.")
    feature_name: Literal["aiops"] = Field(default=..., description="The feature addon identifier to enable or disable. Currently only 'aiops' is supported.")
class UpdateServiceFeatureEnablementRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default value for PagerDuty API v2 compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be JSON format.")
class UpdateServiceFeatureEnablementRequestBodyEnablement(StrictModel):
    enabled: bool = Field(default=..., validation_alias="enabled", serialization_alias="enabled", description="Boolean flag to enable (true) or disable (false) the specified product addon feature.")
class UpdateServiceFeatureEnablementRequestBody(StrictModel):
    """The feature enablement setting to apply."""
    enablement: UpdateServiceFeatureEnablementRequestBodyEnablement
class UpdateServiceFeatureEnablementRequest(StrictModel):
    """Enable or disable a product addon feature for a service. Currently supports the AIOps feature enablement. Note: if the account lacks entitlement for the feature, the setting will still update but return a warning."""
    path: UpdateServiceFeatureEnablementRequestPath
    header: UpdateServiceFeatureEnablementRequestHeader
    body: UpdateServiceFeatureEnablementRequestBody

# Operation: list_standards
class ListStandardsRequestQuery(StrictModel):
    active: bool | None = Field(default=None, description="Filter standards to only include active or inactive standards. Omit to retrieve all standards regardless of status.")
    resource_type: Literal["technical_service"] | None = Field(default=None, description="Filter standards by resource type. Currently supports 'technical_service' to retrieve standards associated with technical services.")
class ListStandardsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to 'application/vnd.pagerduty+json;version=2' to request the current API version.")
class ListStandardsRequest(StrictModel):
    """Retrieve all standards configured for your account, with optional filtering by active status and resource type."""
    query: ListStandardsRequestQuery | None = None
    header: ListStandardsRequestHeader

# Operation: update_standard
class UpdateStandardRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the standard to update.")
class UpdateStandardRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be JSON format.")
class UpdateStandardRequestBody(StrictModel):
    body: UpdateStandardBody | None = Field(default=None, description="The standard properties to update. Supports properties like active status to enable or disable the standard.", examples=[{'active': False}])
class UpdateStandardRequest(StrictModel):
    """Update an existing standard by ID. Modify standard properties such as active status to manage its state."""
    path: UpdateStandardRequestPath
    header: UpdateStandardRequestHeader
    body: UpdateStandardRequestBody | None = None

# Operation: list_standards_scores_for_services
class ListResourceStandardsManyServicesRequestPath(StrictModel):
    resource_type: Literal["technical_services"] = Field(default=..., description="The type of resource to retrieve standards for. Currently supports technical services only.")
class ListResourceStandardsManyServicesRequestQuery(StrictModel):
    ids: list[str] = Field(default=..., description="A list of resource identifiers to fetch standards scores for. Accepts up to 100 IDs per request.")
class ListResourceStandardsManyServicesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Defaults to PagerDuty JSON format version 2.")
class ListResourceStandardsManyServicesRequest(StrictModel):
    """Retrieve standards compliance scores for multiple technical services. Returns the standards applied to each specified resource along with their scores."""
    path: ListResourceStandardsManyServicesRequestPath
    query: ListResourceStandardsManyServicesRequestQuery
    header: ListResourceStandardsManyServicesRequestHeader

# Operation: list_resource_standards_scores
class ListResourceStandardsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the resource to retrieve standards scores for.")
    resource_type: Literal["technical_services"] = Field(default=..., description="The type of resource being evaluated. Currently supports technical services resources.")
class ListResourceStandardsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty JSON API version 2.")
class ListResourceStandardsRequest(StrictModel):
    """Retrieve all standards scores applied to a specific resource. Returns a collection of standards evaluations for the given resource."""
    path: ListResourceStandardsRequestPath
    header: ListResourceStandardsRequestHeader

# Operation: list_status_dashboards
class ListStatusDashboardsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and schema version. Use the default PagerDuty JSON v2 format.")
class ListStatusDashboardsRequest(StrictModel):
    """Retrieve all custom Status Dashboard views configured for your PagerDuty account. Use this to discover available dashboards for monitoring and status tracking."""
    header: ListStatusDashboardsRequestHeader

# Operation: get_status_dashboard
class GetStatusDashboardByIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique PagerDuty identifier for the Status Dashboard resource.")
class GetStatusDashboardByIdRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default application/vnd.pagerduty+json;version=2 to ensure compatibility with the current API version.")
class GetStatusDashboardByIdRequest(StrictModel):
    """Retrieve a single Status Dashboard by its PagerDuty ID. Returns the complete dashboard configuration and current status information."""
    path: GetStatusDashboardByIdRequestPath
    header: GetStatusDashboardByIdRequestHeader

# Operation: get_service_impacts_for_status_dashboard
class GetStatusDashboardServiceImpactsByIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Status Dashboard to retrieve service impacts for.")
class GetStatusDashboardServiceImpactsByIdRequestQuery(StrictModel):
    additional_fields: Literal["services.highest_impacting_priority", "total_impacted_count"] | None = Field(default=None, validation_alias="additional_fields[]", serialization_alias="additional_fields[]", description="Optional fields to include in the response: 'services.highest_impacting_priority' returns the highest priority incident per service, and 'total_impacted_count' returns the total number of impacted services. Specify as a comma-separated list or multiple array parameters.")
class GetStatusDashboardServiceImpactsByIdRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 JSON format.")
class GetStatusDashboardServiceImpactsByIdRequest(StrictModel):
    """Retrieve the most impacted Business Services for a specific Status Dashboard, sorted by impact severity and recency. Returns up to 200 services; use the Business Services impacts endpoint with specific IDs to query services not included in this impact-sorted list."""
    path: GetStatusDashboardServiceImpactsByIdRequestPath
    query: GetStatusDashboardServiceImpactsByIdRequestQuery | None = None
    header: GetStatusDashboardServiceImpactsByIdRequestHeader

# Operation: get_status_dashboard_by_url_slug
class GetStatusDashboardByUrlSlugRequestPath(StrictModel):
    url_slug: str = Field(default=..., description="The human-readable URL slug that uniquely identifies the status dashboard (e.g., 'my-status-page' or 'incident-tracking')")
class GetStatusDashboardByUrlSlugRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and schema version. Defaults to PagerDuty API v2 JSON format.")
class GetStatusDashboardByUrlSlugRequest(StrictModel):
    """Retrieve a single Status Dashboard using its human-readable URL slug identifier. The URL slug is a dash-separated string that uniquely identifies a custom Status Dashboard in PagerDuty."""
    path: GetStatusDashboardByUrlSlugRequestPath
    header: GetStatusDashboardByUrlSlugRequestHeader

# Operation: get_service_impacts_for_status_dashboard_by_url_slug
class GetStatusDashboardServiceImpactsByUrlSlugRequestPath(StrictModel):
    url_slug: str = Field(default=..., description="The URL slug identifier for the Status Dashboard (typically a dash-separated string like 'my-dashboard-name')")
class GetStatusDashboardServiceImpactsByUrlSlugRequestQuery(StrictModel):
    additional_fields: Literal["services.highest_impacting_priority", "total_impacted_count"] | None = Field(default=None, validation_alias="additional_fields[]", serialization_alias="additional_fields[]", description="Optional fields to include in the response: 'services.highest_impacting_priority' returns the highest priority incident per service, and 'total_impacted_count' returns the total number of impacted services")
class GetStatusDashboardServiceImpactsByUrlSlugRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header; defaults to PagerDuty JSON API version 2")
class GetStatusDashboardServiceImpactsByUrlSlugRequest(StrictModel):
    """Retrieve the most impacted Business Services displayed on a Status Dashboard, identified by its URL slug. Results are sorted by impact severity, recency, and name, with a maximum of 200 services returned."""
    path: GetStatusDashboardServiceImpactsByUrlSlugRequestPath
    query: GetStatusDashboardServiceImpactsByUrlSlugRequestQuery | None = None
    header: GetStatusDashboardServiceImpactsByUrlSlugRequestHeader

# Operation: list_status_pages
class ListStatusPagesRequestQuery(StrictModel):
    status_page_type: Literal["public", "private"] | None = Field(default=None, description="Filter status pages by visibility type: 'public' for publicly accessible pages or 'private' for restricted access. Omit to retrieve all status pages regardless of type.")
class ListStatusPagesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default PagerDuty JSON v2 format for compatibility.")
class ListStatusPagesRequest(StrictModel):
    """Retrieve a list of status pages, optionally filtered by type (public or private). Requires status_pages.read OAuth scope."""
    query: ListStatusPagesRequestQuery | None = None
    header: ListStatusPagesRequestHeader

# Operation: list_status_page_impacts
class ListStatusPageImpactsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page for which to retrieve impacts.")
class ListStatusPageImpactsRequestQuery(StrictModel):
    post_type: Literal["incident", "maintenance"] | None = Field(default=None, description="Filter impacts by post type: either 'incident' for unplanned service disruptions or 'maintenance' for scheduled maintenance events. Omit to retrieve all impact types.")
class ListStatusPageImpactsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default value to ensure compatibility with the current API version.")
class ListStatusPageImpactsRequest(StrictModel):
    """Retrieve all impacts associated with a specific status page. Impacts represent incidents or maintenance events that affect services tracked on the status page."""
    path: ListStatusPageImpactsRequestPath
    query: ListStatusPageImpactsRequestQuery | None = None
    header: ListStatusPageImpactsRequestHeader

# Operation: get_status_page_impact
class GetStatusPageImpactRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page resource.")
    impact_id: str = Field(default=..., description="The unique identifier of the impact record within the status page.")
class GetStatusPageImpactRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default PagerDuty JSON format version 2.")
class GetStatusPageImpactRequest(StrictModel):
    """Retrieve a specific impact associated with a status page. Returns detailed information about how an incident or maintenance event affects the status page's components and services."""
    path: GetStatusPageImpactRequestPath
    header: GetStatusPageImpactRequestHeader

# Operation: list_status_page_services
class ListStatusPageServicesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page for which to retrieve associated services.")
class ListStatusPageServicesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and schema version. Defaults to PagerDuty API v2 JSON format.")
class ListStatusPageServicesRequest(StrictModel):
    """Retrieve all services associated with a specific status page. This returns the complete list of services monitored and displayed on the given status page."""
    path: ListStatusPageServicesRequestPath
    header: ListStatusPageServicesRequestHeader

# Operation: get_status_page_service
class GetStatusPageServiceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page resource.")
    service_id: str = Field(default=..., description="The unique identifier of the service within the status page.")
class GetStatusPageServiceRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty JSON API version 2.")
class GetStatusPageServiceRequest(StrictModel):
    """Retrieve a specific service associated with a status page. Use this to fetch details about an individual service tracked on a status page by providing both the status page ID and the service ID."""
    path: GetStatusPageServiceRequestPath
    header: GetStatusPageServiceRequestHeader

# Operation: list_status_page_severities
class ListStatusPageSeveritiesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page for which to retrieve severities.")
class ListStatusPageSeveritiesRequestQuery(StrictModel):
    post_type: Literal["incident", "maintenance"] | None = Field(default=None, description="Optional filter to return severities associated only with specific post types: either 'incident' for incident-related severities or 'maintenance' for maintenance-related severities.")
class ListStatusPageSeveritiesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 JSON format.")
class ListStatusPageSeveritiesRequest(StrictModel):
    """Retrieve the list of severity levels configured for a specific status page. Severities define the impact classification for incidents and maintenance events displayed on the status page."""
    path: ListStatusPageSeveritiesRequestPath
    query: ListStatusPageSeveritiesRequestQuery | None = None
    header: ListStatusPageSeveritiesRequestHeader

# Operation: get_status_page_severity
class GetStatusPageSeverityRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page resource.")
    severity_id: str = Field(default=..., description="The unique identifier of the severity level within the status page.")
class GetStatusPageSeverityRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty JSON API version 2.")
class GetStatusPageSeverityRequest(StrictModel):
    """Retrieve a specific severity level associated with a status page. Use this to fetch details about how a particular severity is configured for a given status page."""
    path: GetStatusPageSeverityRequestPath
    header: GetStatusPageSeverityRequestHeader

# Operation: list_status_page_statuses
class ListStatusPageStatusesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page whose statuses you want to retrieve.")
class ListStatusPageStatusesRequestQuery(StrictModel):
    post_type: Literal["incident", "maintenance"] | None = Field(default=None, description="Filter results to show only posts of a specific type: either incidents or maintenance updates. Omit to retrieve all post types.")
class ListStatusPageStatusesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default PagerDuty JSON format version 2.")
class ListStatusPageStatusesRequest(StrictModel):
    """Retrieve all statuses (incidents and maintenance updates) for a specific status page. Optionally filter results by post type to show only incidents or maintenance notifications."""
    path: ListStatusPageStatusesRequestPath
    query: ListStatusPageStatusesRequestQuery | None = None
    header: ListStatusPageStatusesRequestHeader

# Operation: get_status_page_status
class GetStatusPageStatusRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page resource.")
    status_id: str = Field(default=..., description="The unique identifier of the status entry within the status page.")
class GetStatusPageStatusRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default PagerDuty JSON format version 2.")
class GetStatusPageStatusRequest(StrictModel):
    """Retrieve a specific status entry from a status page using the status page ID and status ID. This allows you to fetch detailed information about an individual status update."""
    path: GetStatusPageStatusRequestPath
    header: GetStatusPageStatusRequestHeader

# Operation: list_status_page_posts
class ListStatusPagePostsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page for which to retrieve posts.")
class ListStatusPagePostsRequestQuery(StrictModel):
    post_type: Literal["incident", "maintenance"] | None = Field(default=None, description="Filter posts by type: either 'incident' for incident reports or 'maintenance' for maintenance notifications.")
    reviewed_status: Literal["approved", "not_reviewed"] | None = Field(default=None, description="Filter posts by their review status: 'approved' for reviewed posts or 'not_reviewed' for posts pending review.")
    status: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="status[]", serialization_alias="status[]", description="Filter posts by one or more status identifiers. Provide as an array of status IDs to return only posts associated with those statuses.")
class ListStatusPagePostsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default value 'application/vnd.pagerduty+json;version=2' to request the current API version.")
class ListStatusPagePostsRequest(StrictModel):
    """Retrieve all posts for a specific status page, with optional filtering by post type, review status, and status identifiers. Posts can represent incidents or maintenance events."""
    path: ListStatusPagePostsRequestPath
    query: ListStatusPagePostsRequestQuery | None = None
    header: ListStatusPagePostsRequestHeader

# Operation: create_status_page_post
class CreateStatusPagePostRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page where the post will be created.")
class CreateStatusPagePostRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default PagerDuty JSON format version 2.")
class CreateStatusPagePostRequestBodyPostStatusPage(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page to associate with this post (must match the status page ID in the path).")
class CreateStatusPagePostRequestBodyPost(StrictModel):
    type_: Literal["status_page_post"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier for this object. Must be set to 'status_page_post'.")
    title: str = Field(default=..., validation_alias="title", serialization_alias="title", description="A descriptive title for the post between 1 and 128 characters that summarizes the incident or maintenance event.", min_length=1, max_length=128)
    post_type: Literal["incident", "maintenance"] = Field(default=..., validation_alias="post_type", serialization_alias="post_type", description="Classifies the post as either an 'incident' (unplanned event) or 'maintenance' (scheduled downtime).")
    starts_at: str | None = Field(default=..., validation_alias="starts_at", serialization_alias="starts_at", description="The date and time when the maintenance event begins, specified in ISO 8601 format. Required for maintenance post types.", json_schema_extra={'format': 'date-time'})
    ends_at: str | None = Field(default=..., validation_alias="ends_at", serialization_alias="ends_at", description="The date and time when the maintenance event concludes, specified in ISO 8601 format. Required for maintenance post types.", json_schema_extra={'format': 'date-time'})
    updates: list[StatusPagePostUpdateRequest] = Field(default=..., validation_alias="updates", serialization_alias="updates", description="An array of 1 to 50 post updates providing detailed information about the event. Updates are displayed in the order provided.", min_length=1, max_length=50)
    status_page: CreateStatusPagePostRequestBodyPostStatusPage
class CreateStatusPagePostRequestBody(StrictModel):
    post: CreateStatusPagePostRequestBodyPost
class CreateStatusPagePostRequest(StrictModel):
    """Create a new post on a status page to communicate incidents or scheduled maintenance to subscribers. Posts can be associated with multiple updates to provide detailed information about the event."""
    path: CreateStatusPagePostRequestPath
    header: CreateStatusPagePostRequestHeader
    body: CreateStatusPagePostRequestBody

# Operation: get_status_page_post
class GetStatusPagePostRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page containing the post.")
    post_id: str = Field(default=..., description="The unique identifier of the post to retrieve from the status page.")
class GetStatusPagePostRequestQuery(StrictModel):
    include: list[Literal["status_page_post_update"]] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array of related models to include in the response for richer context (e.g., author details, attachments). Specify model names as array elements.")
class GetStatusPagePostRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and schema version. Defaults to PagerDuty JSON API version 2.")
class GetStatusPagePostRequest(StrictModel):
    """Retrieve a specific post from a status page using the status page ID and post ID. Returns detailed information about the post including its content and metadata."""
    path: GetStatusPagePostRequestPath
    query: GetStatusPagePostRequestQuery | None = None
    header: GetStatusPagePostRequestHeader

# Operation: update_status_page_post
class UpdateStatusPagePostRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page containing the post to update.")
    post_id: str = Field(default=..., description="The unique identifier of the specific post within the status page to update.")
class UpdateStatusPagePostRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header; use the default value to ensure compatibility with the current API version.")
class UpdateStatusPagePostRequestBodyPostStatusPage(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page that owns this post; must match the status page specified in the path.")
class UpdateStatusPagePostRequestBodyPost(StrictModel):
    type_: Literal["status_page_post"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'status_page_post' to indicate this is a status page post object.")
    title: str = Field(default=..., validation_alias="title", serialization_alias="title", description="A descriptive title for the post, between 1 and 128 characters in length.", min_length=1, max_length=128)
    post_type: Literal["incident", "maintenance"] = Field(default=..., validation_alias="post_type", serialization_alias="post_type", description="Classifies the post as either an 'incident' (unplanned event) or 'maintenance' (scheduled event).")
    starts_at: str | None = Field(default=..., validation_alias="starts_at", serialization_alias="starts_at", description="The date and time when the post's event becomes effective, specified in ISO 8601 format; required for maintenance post types.", json_schema_extra={'format': 'date-time'})
    ends_at: str | None = Field(default=..., validation_alias="ends_at", serialization_alias="ends_at", description="The date and time when the post's event concludes, specified in ISO 8601 format; required for maintenance post types.", json_schema_extra={'format': 'date-time'})
    status_page: UpdateStatusPagePostRequestBodyPostStatusPage
class UpdateStatusPagePostRequestBody(StrictModel):
    post: UpdateStatusPagePostRequestBodyPost
class UpdateStatusPagePostRequest(StrictModel):
    """Update an existing post on a status page, allowing you to modify incident or maintenance event details including title, type, and timing information."""
    path: UpdateStatusPagePostRequestPath
    header: UpdateStatusPagePostRequestHeader
    body: UpdateStatusPagePostRequestBody

# Operation: delete_status_page_post
class DeleteStatusPagePostRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page containing the post to delete.")
    post_id: str = Field(default=..., description="The unique identifier of the post to delete from the status page.")
class DeleteStatusPagePostRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default value for PagerDuty API v2 responses.")
class DeleteStatusPagePostRequest(StrictModel):
    """Permanently delete a specific post from a status page. Requires the status page ID and the post ID to identify which post to remove."""
    path: DeleteStatusPagePostRequestPath
    header: DeleteStatusPagePostRequestHeader

# Operation: list_status_page_post_updates
class ListStatusPagePostUpdatesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page containing the post.")
    post_id: str = Field(default=..., description="The unique identifier of the post within the status page.")
class ListStatusPagePostUpdatesRequestQuery(StrictModel):
    reviewed_status: Literal["approved", "not_reviewed"] | None = Field(default=None, description="Filter results by review status. Use 'approved' to show only reviewed updates or 'not_reviewed' to show updates pending review.")
class ListStatusPagePostUpdatesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Specifies the response format and API version (defaults to application/vnd.pagerduty+json;version=2).")
class ListStatusPagePostUpdatesRequest(StrictModel):
    """Retrieve all updates for a specific post within a status page. Use this to track the history of changes and status communications for a particular post."""
    path: ListStatusPagePostUpdatesRequestPath
    query: ListStatusPagePostUpdatesRequestQuery | None = None
    header: ListStatusPagePostUpdatesRequestHeader

# Operation: create_post_update_for_status_page_post
class CreateStatusPagePostUpdateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page resource.")
    post_id2: str = Field(default=..., description="The unique identifier of the severity level for this post update.")
class CreateStatusPagePostUpdateRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="The HTTP Accept header for API versioning. Use the default application/vnd.pagerduty+json;version=2 unless a different API version is required.")
class CreateStatusPagePostUpdateRequestBodyPostUpdatePost(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page post to which this update belongs.")
class CreateStatusPagePostUpdateRequestBodyPostUpdateStatus(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page post being updated.")
class CreateStatusPagePostUpdateRequestBodyPostUpdateSeverity(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status to assign to this post update.")
class CreateStatusPagePostUpdateRequestBodyPostUpdate(StrictModel):
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to indicate this is a Status Page Post Update object.")
    message: str = Field(default=..., validation_alias="message", serialization_alias="message", description="The update message communicating the status change or additional information to subscribers.")
    impacted_services: list[CreateStatusPagePostUpdateBodyPostUpdateImpactedServicesItem] = Field(default=..., validation_alias="impacted_services", serialization_alias="impacted_services", description="An array of services affected by this post update and their impact levels. Can be empty if no specific services are impacted.", min_length=0)
    update_frequency_ms: int | None = Field(default=..., validation_alias="update_frequency_ms", serialization_alias="update_frequency_ms", description="The interval in milliseconds before the next post update is expected. Helps set expectations for update frequency.")
    notify_subscribers: bool = Field(default=..., validation_alias="notify_subscribers", serialization_alias="notify_subscribers", description="Whether to send notifications to status page subscribers about this post update.")
    reported_at: str | None = Field(default=None, validation_alias="reported_at", serialization_alias="reported_at", description="The date and time when the post update was initially reported, formatted as an ISO 8601 datetime string. If omitted, the current time is used.", json_schema_extra={'format': 'date-time'})
    post: CreateStatusPagePostUpdateRequestBodyPostUpdatePost
    status: CreateStatusPagePostUpdateRequestBodyPostUpdateStatus
    severity: CreateStatusPagePostUpdateRequestBodyPostUpdateSeverity
class CreateStatusPagePostUpdateRequestBody(StrictModel):
    post_update: CreateStatusPagePostUpdateRequestBodyPostUpdate
class CreateStatusPagePostUpdateRequest(StrictModel):
    """Create a new update for an existing status page post, allowing you to add messages, impact information, and subscriber notifications to communicate status changes."""
    path: CreateStatusPagePostUpdateRequestPath
    header: CreateStatusPagePostUpdateRequestHeader
    body: CreateStatusPagePostUpdateRequestBody

# Operation: get_post_update
class GetPostUpdateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page resource.")
    post_id: str = Field(default=..., description="The unique identifier of the status page post containing the update.")
    post_update_id: str = Field(default=..., description="The unique identifier of the specific post update to retrieve.")
class GetPostUpdateRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="HTTP header specifying the response format and API version. Use the default PagerDuty JSON format version 2.")
class GetPostUpdateRequest(StrictModel):
    """Retrieve a specific update for a status page post. Use this to fetch details about a particular post update by providing the status page ID, post ID, and post update ID."""
    path: GetPostUpdateRequestPath
    header: GetPostUpdateRequestHeader

# Operation: update_status_page_post_update
class UpdateStatusPagePostUpdateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page resource.")
    post_id2: str = Field(default=..., description="The unique identifier of the status page post being updated.")
    post_update_id: str = Field(default=..., description="The unique identifier of the status page status to associate with this update.")
class UpdateStatusPagePostUpdateRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="The unique identifier of the severity level for this update.")
class UpdateStatusPagePostUpdateRequestBodyPostUpdatePost(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page post that contains this update.")
class UpdateStatusPagePostUpdateRequestBodyPostUpdateStatus(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the post update to modify.")
class UpdateStatusPagePostUpdateRequestBodyPostUpdateSeverity(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The API version header. Use application/vnd.pagerduty+json;version=2 for this operation.")
class UpdateStatusPagePostUpdateRequestBodyPostUpdate(StrictModel):
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The object type identifier. Must be set to the Status Page Post Update type.")
    message: str = Field(default=..., validation_alias="message", serialization_alias="message", description="The message content describing the post update. This is the primary communication to subscribers.")
    impacted_services: list[UpdateStatusPagePostUpdateBodyPostUpdateImpactedServicesItem] = Field(default=..., validation_alias="impacted_services", serialization_alias="impacted_services", description="An array of services affected by this post update and their impact levels. Can be empty if no specific services are impacted.", min_length=0)
    update_frequency_ms: int | None = Field(default=..., validation_alias="update_frequency_ms", serialization_alias="update_frequency_ms", description="The interval in milliseconds before the next post update is expected. Helps set subscriber expectations for update frequency.")
    notify_subscribers: bool = Field(default=..., validation_alias="notify_subscribers", serialization_alias="notify_subscribers", description="Whether to send notifications to subscribers about this post update.")
    reported_at: str | None = Field(default=None, validation_alias="reported_at", serialization_alias="reported_at", description="The date and time when this post update was initially reported, in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    post: UpdateStatusPagePostUpdateRequestBodyPostUpdatePost
    status: UpdateStatusPagePostUpdateRequestBodyPostUpdateStatus
    severity: UpdateStatusPagePostUpdateRequestBodyPostUpdateSeverity
class UpdateStatusPagePostUpdateRequestBody(StrictModel):
    post_update: UpdateStatusPagePostUpdateRequestBodyPostUpdate
class UpdateStatusPagePostUpdateRequest(StrictModel):
    """Update an existing post update within a status page post. Modify the message, impacted services, notification settings, and other details of a specific post update."""
    path: UpdateStatusPagePostUpdateRequestPath
    header: UpdateStatusPagePostUpdateRequestHeader
    body: UpdateStatusPagePostUpdateRequestBody

# Operation: delete_post_update
class DeleteStatusPagePostUpdateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page containing the post.")
    post_id: str = Field(default=..., description="The unique identifier of the post within the status page.")
    post_update_id: str = Field(default=..., description="The unique identifier of the post update to delete.")
class DeleteStatusPagePostUpdateRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2 for compatibility.")
class DeleteStatusPagePostUpdateRequest(StrictModel):
    """Delete a specific update from a status page post. Requires the status page ID, post ID, and post update ID to identify the exact update to remove."""
    path: DeleteStatusPagePostUpdateRequestPath
    header: DeleteStatusPagePostUpdateRequestHeader

# Operation: get_postmortem_for_post
class GetPostmortemRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page resource.")
    post_id: str = Field(default=..., description="The unique identifier of the status page post for which to retrieve the postmortem.")
class GetPostmortemRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default PagerDuty JSON format version 2.")
class GetPostmortemRequest(StrictModel):
    """Retrieve the postmortem details for a specific post on a status page. Postmortems provide analysis and context for incidents or events documented in status page posts."""
    path: GetPostmortemRequestPath
    header: GetPostmortemRequestHeader

# Operation: create_postmortem_for_status_page_post
class CreateStatusPagePostmortemRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page resource.")
    post_id2: str = Field(default=..., description="The unique identifier of the status page post (path parameter).")
class CreateStatusPagePostmortemRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default value to request the current API version.")
class CreateStatusPagePostmortemRequestBodyPostmortemPost(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page post for which the postmortem is being created.")
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the postmortem object. Typically used for API versioning and object type identification.")
class CreateStatusPagePostmortemRequestBodyPostmortem(StrictModel):
    message: str = Field(default=..., validation_alias="message", serialization_alias="message", description="The postmortem message content, which supports rich-text formatting. Maximum length is 10,000 characters.", max_length=10000)
    notify_subscribers: bool = Field(default=..., validation_alias="notify_subscribers", serialization_alias="notify_subscribers", description="Whether to notify all subscribers of the status page about this postmortem. Set to true to send notifications, false to skip.")
    post: CreateStatusPagePostmortemRequestBodyPostmortemPost
class CreateStatusPagePostmortemRequestBody(StrictModel):
    postmortem: CreateStatusPagePostmortemRequestBodyPostmortem
class CreateStatusPagePostmortemRequest(StrictModel):
    """Create a postmortem for a specific status page post. The postmortem message supports rich-text formatting and can optionally notify all subscribers of the status page."""
    path: CreateStatusPagePostmortemRequestPath
    header: CreateStatusPagePostmortemRequestHeader
    body: CreateStatusPagePostmortemRequestBody

# Operation: update_status_page_post_postmortem
class UpdateStatusPagePostmortemRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page resource.")
    post_id2: str = Field(default=..., description="The unique identifier of the status page post being updated.")
class UpdateStatusPagePostmortemRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use application/vnd.pagerduty+json;version=2 for the current API version.")
class UpdateStatusPagePostmortemRequestBodyPostmortemPost(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page post associated with this postmortem.")
class UpdateStatusPagePostmortemRequestBodyPostmortem(StrictModel):
    message: str = Field(default=..., validation_alias="message", serialization_alias="message", description="The postmortem message content supporting rich-text formatting. Maximum length is 10,000 characters.", max_length=10000)
    notify_subscribers: bool = Field(default=..., validation_alias="notify_subscribers", serialization_alias="notify_subscribers", description="Whether to notify all subscribers of the status page about this postmortem update.")
    post: UpdateStatusPagePostmortemRequestBodyPostmortemPost
class UpdateStatusPagePostmortemRequestBody(StrictModel):
    postmortem: UpdateStatusPagePostmortemRequestBodyPostmortem
class UpdateStatusPagePostmortemRequest(StrictModel):
    """Update the postmortem for a specific status page post, including the postmortem message and subscriber notification settings. Requires write access to status pages."""
    path: UpdateStatusPagePostmortemRequestPath
    header: UpdateStatusPagePostmortemRequestHeader
    body: UpdateStatusPagePostmortemRequestBody

# Operation: delete_postmortem_for_status_page_post
class DeleteStatusPagePostmortemRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page resource.")
    post_id: str = Field(default=..., description="The unique identifier of the status page post from which to delete the postmortem.")
class DeleteStatusPagePostmortemRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default PagerDuty JSON format version 2.")
class DeleteStatusPagePostmortemRequest(StrictModel):
    """Remove a postmortem document from a status page post. This permanently deletes the postmortem analysis associated with the specified post."""
    path: DeleteStatusPagePostmortemRequestPath
    header: DeleteStatusPagePostmortemRequestHeader

# Operation: list_status_page_subscriptions
class ListStatusPageSubscriptionsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page whose subscriptions you want to list.")
class ListStatusPageSubscriptionsRequestQuery(StrictModel):
    status: Literal["active", "pending"] | None = Field(default=None, description="Filter subscriptions by their current state: either active subscriptions or those pending activation.")
    channel: Literal["webhook", "email", "slack"] | None = Field(default=None, description="Filter subscriptions by their notification delivery method: webhook, email, or Slack.")
class ListStatusPageSubscriptionsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default application/vnd.pagerduty+json;version=2 for standard responses.")
class ListStatusPageSubscriptionsRequest(StrictModel):
    """Retrieve all subscriptions for a specific status page, with optional filtering by subscription status or notification channel."""
    path: ListStatusPageSubscriptionsRequestPath
    query: ListStatusPageSubscriptionsRequestQuery | None = None
    header: ListStatusPageSubscriptionsRequestHeader

# Operation: create_status_page_subscription
class CreateStatusPageSubscriptionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page to subscribe to.")
class CreateStatusPageSubscriptionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API version header for response formatting. Must be set to application/vnd.pagerduty+json;version=2.")
class CreateStatusPageSubscriptionRequestBodySubscriptionStatusPage(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page being subscribed to (must match the status page ID in the path).")
class CreateStatusPageSubscriptionRequestBodySubscriptionSubscribableObject(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="Optional identifier of a specific entity (component, service, etc.) within the status page to subscribe to. If omitted, subscribes to all updates for the status page.")
class CreateStatusPageSubscriptionRequestBodySubscription(StrictModel):
    channel: Literal["webhook", "email"] = Field(default=..., validation_alias="channel", serialization_alias="channel", description="The delivery method for subscription notifications. Choose 'email' to receive updates via email or 'webhook' to receive JSON payloads at a specified URL.")
    contact: str = Field(default=..., validation_alias="contact", serialization_alias="contact", description="The recipient contact information. Provide an email address for email subscriptions or a webhook URL for webhook subscriptions.")
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The subscription object type identifier. This determines the schema and structure of the subscription being created.")
    status_page: CreateStatusPageSubscriptionRequestBodySubscriptionStatusPage
    subscribable_object: CreateStatusPageSubscriptionRequestBodySubscriptionSubscribableObject | None = None
class CreateStatusPageSubscriptionRequestBody(StrictModel):
    subscription: CreateStatusPageSubscriptionRequestBodySubscription
class CreateStatusPageSubscriptionRequest(StrictModel):
    """Subscribe to status page updates via email or webhook. Creates a new subscription that will deliver notifications about status page changes through your specified contact channel."""
    path: CreateStatusPageSubscriptionRequestPath
    header: CreateStatusPageSubscriptionRequestHeader
    body: CreateStatusPageSubscriptionRequestBody

# Operation: get_status_page_subscription
class GetStatusPageSubscriptionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the status page resource.")
    subscription_id: str = Field(default=..., description="The unique identifier of the subscription within the status page.")
class GetStatusPageSubscriptionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and schema version. Use the default PagerDuty JSON format version 2.")
class GetStatusPageSubscriptionRequest(StrictModel):
    """Retrieve a specific subscription for a status page by providing both the status page ID and subscription ID. This operation returns the subscription details including notification preferences and contact information."""
    path: GetStatusPageSubscriptionRequestPath
    header: GetStatusPageSubscriptionRequestHeader

# Operation: delete_status_page_subscription
class DeleteStatusPageSubscriptionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Status Page from which the subscription will be removed.")
    subscription_id: str = Field(default=..., description="The unique identifier of the subscription to be deleted from the Status Page.")
class DeleteStatusPageSubscriptionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default PagerDuty JSON format version 2.")
class DeleteStatusPageSubscriptionRequest(StrictModel):
    """Remove a subscription from a Status Page by providing the Status Page ID and Subscription ID. This operation requires write access to status pages."""
    path: DeleteStatusPageSubscriptionRequestPath
    header: DeleteStatusPageSubscriptionRequestHeader

# Operation: list_sre_memories
class ListSreMemoriesRequestQuery(StrictModel):
    service_id: str | None = Field(default=None, description="Filter memories to a specific service by its ID.")
    incident_id: str | None = Field(default=None, description="Filter memories to a specific incident by its ID.")
class ListSreMemoriesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API version header. Use the default PagerDuty JSON format version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be JSON.")
class ListSreMemoriesRequest(StrictModel):
    """Retrieve SRE Agent memories for your account, including service runbooks, profiles, incident playbooks, and summaries. Filter by service or incident to find relevant knowledge."""
    query: ListSreMemoriesRequestQuery | None = None
    header: ListSreMemoriesRequestHeader

# Operation: update_sre_memory
class UpdateSreMemoryRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SRE Agent memory to update.")
class UpdateSreMemoryRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty JSON API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be JSON format.")
class UpdateSreMemoryRequestBodyMemory(StrictModel):
    content: str = Field(default=..., validation_alias="content", serialization_alias="content", description="The updated content for the SRE memory. This is the primary data being modified in the memory record.")
class UpdateSreMemoryRequestBody(StrictModel):
    """The SRE Agent memory to be updated."""
    memory: UpdateSreMemoryRequestBodyMemory
class UpdateSreMemoryRequest(StrictModel):
    """Update the content of an existing SRE Agent memory by ID. Requires write access to SRE Agent memories."""
    path: UpdateSreMemoryRequestPath
    header: UpdateSreMemoryRequestHeader
    body: UpdateSreMemoryRequestBody

# Operation: delete_sre_memory
class DeleteSreMemoryRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SRE Agent memory to delete.")
class DeleteSreMemoryRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be JSON format.")
class DeleteSreMemoryRequest(StrictModel):
    """Permanently delete an SRE Agent memory by its ID. This action cannot be undone."""
    path: DeleteSreMemoryRequestPath
    header: DeleteSreMemoryRequestHeader

# Operation: list_tags
class ListTagsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to the PagerDuty JSON API version 2 format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request content type. Must be application/json.")
class ListTagsRequest(StrictModel):
    """Retrieve all tags in your PagerDuty account. Tags can be applied to Escalation Policies, Teams, or Users for filtering and organization purposes."""
    header: ListTagsRequestHeader

# Operation: create_tag
class CreateTagsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to application/vnd.pagerduty+json;version=2 to use the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format. Must be application/json.")
class CreateTagsRequestBody(StrictModel):
    tag: Tag = Field(default=..., description="The tag object containing the tag configuration to be created. Refer to the API Concepts Document for the required and optional fields.")
class CreateTagsRequest(StrictModel):
    """Create a new tag that can be applied to Escalation Policies, Teams, or Users for filtering and organization purposes."""
    header: CreateTagsRequestHeader
    body: CreateTagsRequestBody

# Operation: get_tag
class GetTagRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag to retrieve.")
class GetTagRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be set to application/json.")
class GetTagRequest(StrictModel):
    """Retrieve details about a specific tag by ID. Tags are used to organize and filter Escalation Policies, Teams, and Users."""
    path: GetTagRequestPath
    header: GetTagRequestHeader

# Operation: delete_tag
class DeleteTagRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag to delete.")
class DeleteTagRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON.")
class DeleteTagRequest(StrictModel):
    """Permanently remove a tag from the PagerDuty system. Tags are used to organize and filter Escalation Policies, Teams, and Users."""
    path: DeleteTagRequestPath
    header: DeleteTagRequestHeader

# Operation: list_entities_by_tag
class GetTagsByEntityTypeRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag resource.")
    entity_type: Literal["users", "teams", "escalation_policies"] = Field(default=..., description="The type of entity to retrieve. Must be one of: users, teams, or escalation_policies.")
class GetTagsByEntityTypeRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Defaults to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request. Must be application/json.")
class GetTagsByEntityTypeRequest(StrictModel):
    """Retrieve all entities (users, teams, or escalation policies) associated with a specific tag. Tags are used to organize and filter PagerDuty resources across your account."""
    path: GetTagsByEntityTypeRequestPath
    header: GetTagsByEntityTypeRequestHeader

# Operation: list_teams
class ListTeamsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and schema version. Must be set to the PagerDuty JSON API version 2 format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request content type. Must be application/json.")
class ListTeamsRequest(StrictModel):
    """Retrieve a list of teams in your PagerDuty account, optionally filtered by search query. Teams are collections of users and escalation policies that represent groups within your organization."""
    header: ListTeamsRequestHeader

# Operation: create_team
class CreateTeamRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to the PagerDuty JSON API version 2 format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format. Must be JSON.")
class CreateTeamRequestBody(StrictModel):
    """The team to be created."""
    team: Team = Field(default=..., description="The team object containing the team configuration. Include required fields such as name and any optional fields like description or default escalation policy.")
class CreateTeamRequest(StrictModel):
    """Create a new team representing a collection of users and escalation policies within your organization. Teams are used to group people and define escalation behavior for incident management."""
    header: CreateTeamRequestHeader
    body: CreateTeamRequestBody

# Operation: get_team
class GetTeamRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the team to retrieve.")
class GetTeamRequestQuery(StrictModel):
    include: Annotated[Literal["privileges"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array to include additional data in the response. Specify 'privileges' to include team member privileges.")
class GetTeamRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be JSON format.")
class GetTeamRequest(StrictModel):
    """Retrieve detailed information about a specific team, including its users and escalation policies. Teams represent groups of people within an organization."""
    path: GetTeamRequestPath
    query: GetTeamRequestQuery | None = None
    header: GetTeamRequestHeader

# Operation: update_team
class UpdateTeamRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the team to update.")
class UpdateTeamRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2 for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be JSON format.")
class UpdateTeamRequestBody(StrictModel):
    """The team to be updated."""
    team: Team = Field(default=..., description="The team object containing the properties to update (e.g., name, description).")
class UpdateTeamRequest(StrictModel):
    """Update an existing team's properties. A team is a collection of users and escalation policies representing a group within an organization."""
    path: UpdateTeamRequestPath
    header: UpdateTeamRequestHeader
    body: UpdateTeamRequestBody

# Operation: delete_team
class DeleteTeamRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the team to delete.")
class DeleteTeamRequestQuery(StrictModel):
    reassignment_team: str | None = Field(default=None, description="Optional team ID to receive unresolved incidents from the deleted team. If omitted, incidents become account-level and lose team association. Duplicate incidents are not created if they already exist on the reassignment team.")
class DeleteTeamRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be application/json.")
class DeleteTeamRequest(StrictModel):
    """Permanently remove a team from the account. The team must have no associated Escalation Policies, Services, Schedules, or Subteams. Any unresolved incidents will be asynchronously reassigned to another team or converted to account-level incidents."""
    path: DeleteTeamRequestPath
    query: DeleteTeamRequestQuery | None = None
    header: DeleteTeamRequestHeader

# Operation: list_teams_audit_records
class ListTeamsAuditRecordsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the team for which to retrieve audit records.")
class ListTeamsAuditRecordsRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="The start of the date range for the audit search in ISO 8601 format. Defaults to 24 hours before the current time if not specified.", json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="The end of the date range for the audit search in ISO 8601 format. Defaults to the current time if not specified. Cannot be more than 31 days after the start date.", json_schema_extra={'format': 'date-time'})
class ListTeamsAuditRecordsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to the PagerDuty API v2 content type.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type for the request body, must be JSON.")
class ListTeamsAuditRecordsRequest(StrictModel):
    """Retrieve audit records for a team, sorted by execution time from newest to oldest. Records default to the past 24 hours if no date range is specified."""
    path: ListTeamsAuditRecordsRequestPath
    query: ListTeamsAuditRecordsRequestQuery | None = None
    header: ListTeamsAuditRecordsRequestHeader

# Operation: add_escalation_policy_to_team
class UpdateTeamEscalationPolicyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the team resource to which the escalation policy will be added.")
    escalation_policy_id: str = Field(default=..., description="The unique identifier of the escalation policy to associate with the team.")
class UpdateTeamEscalationPolicyRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to application/vnd.pagerduty+json;version=2 to use the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be application/json.")
class UpdateTeamEscalationPolicyRequest(StrictModel):
    """Associate an escalation policy with a team to define how incidents are escalated within that team. This enables the team to use the specified escalation policy for incident routing and notification."""
    path: UpdateTeamEscalationPolicyRequestPath
    header: UpdateTeamEscalationPolicyRequestHeader

# Operation: remove_escalation_policy_from_team
class DeleteTeamEscalationPolicyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the team from which the escalation policy will be removed.")
    escalation_policy_id: str = Field(default=..., description="The unique identifier of the escalation policy to remove from the team.")
class DeleteTeamEscalationPolicyRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to application/vnd.pagerduty+json;version=2 to use the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be application/json.")
class DeleteTeamEscalationPolicyRequest(StrictModel):
    """Remove an escalation policy from a team. This operation disassociates the specified escalation policy from the team, affecting how incidents are routed and escalated within that team."""
    path: DeleteTeamEscalationPolicyRequestPath
    header: DeleteTeamEscalationPolicyRequestHeader

# Operation: list_team_members
class ListTeamUsersRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the team whose members you want to list.")
class ListTeamUsersRequestQuery(StrictModel):
    include: Annotated[Literal["users"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array of additional data models to include in the response. Specify 'users' to include detailed user information for team members.")
class ListTeamUsersRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2 for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be set to JSON format.")
class ListTeamUsersRequest(StrictModel):
    """Retrieve all members of a team, including users and escalation policies. Optionally include additional related data in the response."""
    path: ListTeamUsersRequestPath
    query: ListTeamUsersRequestQuery | None = None
    header: ListTeamUsersRequestHeader

# Operation: list_team_notification_subscriptions
class GetTeamNotificationSubscriptionsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the team whose notification subscriptions you want to retrieve.")
class GetTeamNotificationSubscriptionsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API version header to specify the response format. Defaults to PagerDuty API v2 JSON format.")
class GetTeamNotificationSubscriptionsRequest(StrictModel):
    """Retrieve all notification subscriptions for a specific team. Only subscriptions that were explicitly added through the create endpoint will be returned."""
    path: GetTeamNotificationSubscriptionsRequestPath
    header: GetTeamNotificationSubscriptionsRequestHeader

# Operation: remove_team_notification_subscriptions
class RemoveTeamNotificationSubscriptionsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the team resource to unsubscribe from notifications.")
class RemoveTeamNotificationSubscriptionsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="The API version header for request/response formatting. Defaults to PagerDuty API v2 JSON format.")
class RemoveTeamNotificationSubscriptionsRequestBody(StrictModel):
    """The entities to unsubscribe from."""
    subscribables: Annotated[list[NotificationSubscribable], AfterValidator(_check_unique_items)] = Field(default=..., description="An array of subscribable entity identifiers to unsubscribe the team from. Must contain at least one item.", min_length=1)
class RemoveTeamNotificationSubscriptionsRequest(StrictModel):
    """Unsubscribe a team from notifications on specified subscribable entities. This operation removes the team's notification subscriptions for the given resources."""
    path: RemoveTeamNotificationSubscriptionsRequestPath
    header: RemoveTeamNotificationSubscriptionsRequestHeader
    body: RemoveTeamNotificationSubscriptionsRequestBody

# Operation: add_user_to_team
class UpdateTeamUserRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the team to which the user will be added.")
    user_id: str = Field(default=..., description="The unique identifier of the user to add to the team.")
class UpdateTeamUserRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use application/vnd.pagerduty+json;version=2 for the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be application/json.")
class UpdateTeamUserRequestBody(StrictModel):
    """The role of the user on the team."""
    role: Literal["observer", "responder", "manager"] | None = Field(default=None, description="The role to assign the user on the team. Valid roles are observer (read-only access), responder (can respond to incidents), or manager (full team management access).")
class UpdateTeamUserRequest(StrictModel):
    """Add a user to a team with a specified role. Note that users with the read_only_user role cannot be added and will result in a 400 error."""
    path: UpdateTeamUserRequestPath
    header: UpdateTeamUserRequestHeader
    body: UpdateTeamUserRequestBody | None = None

# Operation: remove_user_from_team
class DeleteTeamUserRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the team from which the user will be removed.")
    user_id: str = Field(default=..., description="The unique identifier of the user to be removed from the team.")
class DeleteTeamUserRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty JSON format version 2 for compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request payload. Must be application/json.")
class DeleteTeamUserRequest(StrictModel):
    """Remove a user from a team. This operation deletes the membership relationship between a user and a team, effectively removing the user from that team's roster."""
    path: DeleteTeamUserRequestPath
    header: DeleteTeamUserRequestHeader

# Operation: list_templates
class GetTemplatesRequestQuery(StrictModel):
    template_type: str | None = Field(default=None, description="Filter templates by their type. Defaults to 'status_update' if not specified.")
    sort_by: Literal["name", "name:asc", "name:desc", "created_at", "created_at:asc", "created_at:desc"] | None = Field(default=None, description="Sort results by a specified field (name or created_at) in ascending or descending order. Use the format 'field:direction' (e.g., 'name:desc'). Defaults to sorting by creation date in ascending order.")
class GetTemplatesRequest(StrictModel):
    """Retrieve all templates on an account, with optional filtering by type and sorting capabilities."""
    query: GetTemplatesRequestQuery | None = None

# Operation: create_status_update_template
class CreateTemplateRequestBodyTemplateTemplatedFields(StrictModel):
    email_subject: str | None = Field(default=None, validation_alias="email_subject", serialization_alias="email_subject", description="The subject line for email communications using this template.")
    email_body: str | None = Field(default=None, validation_alias="email_body", serialization_alias="email_body", description="The HTML-formatted body content for email messages sent using this template.")
    message: str | None = Field(default=None, validation_alias="message", serialization_alias="message", description="A concise message for use in SMS, push notifications, Slack, and other short-form communication channels.")
class CreateTemplateRequestBodyTemplate(StrictModel):
    template_type: Literal["status_update"] | None = Field(default=None, validation_alias="template_type", serialization_alias="template_type", description="The category of template being created. Currently, only `status_update` templates are supported.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A brief description explaining the purpose or use case of this template.")
    templated_fields: CreateTemplateRequestBodyTemplateTemplatedFields | None = None
class CreateTemplateRequestBody(StrictModel):
    template: CreateTemplateRequestBodyTemplate | None = None
class CreateTemplateRequest(StrictModel):
    """Create a new status update template with optional email and messaging content. Templates can be used to standardize communications across email, SMS, push notifications, and Slack."""
    body: CreateTemplateRequestBody | None = None

# Operation: get_template
class GetTemplateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the template to retrieve.")
class GetTemplateRequest(StrictModel):
    """Retrieve a single template from your account by its ID. Returns the complete template details including configuration and metadata."""
    path: GetTemplateRequestPath

# Operation: update_template
class UpdateTemplateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the template to update.")
class UpdateTemplateRequestBodyTemplateTemplatedFields(StrictModel):
    email_subject: str | None = Field(default=None, validation_alias="email_subject", serialization_alias="email_subject", description="The subject line for email notifications sent using this template.")
    email_body: str | None = Field(default=None, validation_alias="email_body", serialization_alias="email_body", description="The HTML-formatted body content for email notifications sent using this template.")
    message: str | None = Field(default=None, validation_alias="message", serialization_alias="message", description="The concise message text for SMS, push notifications, Slack, and other short-form channels.")
class UpdateTemplateRequestBodyTemplate(StrictModel):
    template_type: Literal["status_update"] | None = Field(default=None, validation_alias="template_type", serialization_alias="template_type", description="The category of template. Currently, only `status_update` templates are supported for notifications across email, SMS, push, and Slack channels.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A human-readable description of the template's purpose and usage.")
    templated_fields: UpdateTemplateRequestBodyTemplateTemplatedFields | None = None
class UpdateTemplateRequestBody(StrictModel):
    template: UpdateTemplateRequestBodyTemplate | None = None
class UpdateTemplateRequest(StrictModel):
    """Update an existing template with new content and configuration. Modify template type, description, email subject/body, or message content for status update notifications."""
    path: UpdateTemplateRequestPath
    body: UpdateTemplateRequestBody | None = None

# Operation: delete_template
class DeleteTemplateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the template to delete.")
class DeleteTemplateRequest(StrictModel):
    """Permanently delete a template from the account. This action cannot be undone."""
    path: DeleteTemplateRequestPath

# Operation: render_template
class RenderTemplateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the template to render.")
class RenderTemplateRequestBody(StrictModel):
    body: StatusUpdateTemplateInput = Field(default=..., description="Template-specific payload containing the data needed to render the template. For status_update templates, include incident_id (string) and status_update object with a message field.", examples=[{'incident_id': 'QT4KHLK034QWE34', 'status_update': {'message': 'Status update message'}}])
class RenderTemplateRequest(StrictModel):
    """Render a template by providing template-specific data. The request body structure varies based on template type; for status_update templates, provide the incident ID and status message."""
    path: RenderTemplateRequestPath
    body: RenderTemplateRequestBody

# Operation: list_template_fields
class GetTemplateFieldsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to the PagerDuty JSON API version 2 format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request and response content type. Must be JSON format.")
class GetTemplateFieldsRequest(StrictModel):
    """Retrieve all available fields that can be used when creating or configuring account templates. This operation returns the complete set of supported template field definitions."""
    header: GetTemplateFieldsRequestHeader

# Operation: list_users
class ListUsersRequestQuery(StrictModel):
    team_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="team_ids[]", serialization_alias="team_ids[]", description="Filter results to only include users belonging to the specified teams. Requires the account to have the teams ability enabled. Provide as an array of team IDs.")
    include: Annotated[Literal["contact_methods", "notification_rules", "teams", "subdomains"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Expand the response to include additional related data such as contact methods, notification rules, team associations, or subdomains for each user.")
class ListUsersRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="HTTP header specifying the API version. Must be set to application/vnd.pagerduty+json;version=2 for this operation.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="HTTP header specifying the request body format. Must be application/json.")
class ListUsersRequest(StrictModel):
    """Retrieve a list of users in your PagerDuty account with optional filtering by team membership and additional related data. Users are account members with the ability to interact with incidents and other account data."""
    query: ListUsersRequestQuery | None = None
    header: ListUsersRequestHeader

# Operation: create_user
class CreateUserRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the PagerDuty v2 JSON format for request and response serialization.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request body content type. Must be JSON format.")
    from_: str = Field(default=..., validation_alias="From", serialization_alias="From", description="Email address of a valid user associated with the PagerDuty account making this request. Used to identify the requester for audit purposes.", json_schema_extra={'format': 'email'})
class CreateUserRequestBody(StrictModel):
    """The user to be created."""
    user: CreateUserBodyUser = Field(default=..., description="User object containing the details for the new user account to be created.")
class CreateUserRequest(StrictModel):
    """Create a new user account in PagerDuty. Users are account members with the ability to interact with incidents and other account data. Requires the `users.write` OAuth scope."""
    header: CreateUserRequestHeader
    body: CreateUserRequestBody

# Operation: get_user
class GetUserRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user to retrieve.")
class GetUserRequestQuery(StrictModel):
    include: Annotated[Literal["contact_methods", "notification_rules", "teams", "subdomains"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array of related data models to include in the response. Valid options are contact methods, notification rules, team memberships, and subdomains associated with the user.")
class GetUserRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be JSON format.")
class GetUserRequest(StrictModel):
    """Retrieve detailed information about a specific user in the PagerDuty account. Users are account members with the ability to interact with incidents and other account data."""
    path: GetUserRequestPath
    query: GetUserRequestQuery | None = None
    header: GetUserRequestHeader

# Operation: update_user
class UpdateUserRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user to update.")
class UpdateUserRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to `application/vnd.pagerduty+json;version=2` to specify the API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type of the request body. Must be `application/json`.")
class UpdateUserRequestBody(StrictModel):
    """The user to be updated."""
    user: UpdateUserBodyUser = Field(default=..., description="User object containing the fields to update. Refer to the API Concepts Document for the complete user schema and available fields.")
class UpdateUserRequest(StrictModel):
    """Update an existing user in a PagerDuty account. Users are members with the ability to interact with incidents and other account data. Requires `users.write` OAuth scope."""
    path: UpdateUserRequestPath
    header: UpdateUserRequestHeader
    body: UpdateUserRequestBody

# Operation: delete_user
class DeleteUserRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user to delete.")
class DeleteUserRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be application/json.")
class DeleteUserRequest(StrictModel):
    """Permanently remove a user from the PagerDuty account. Deletion may fail if the user has assigned incidents unless your pricing plan includes the offboarding feature and your account is configured for it. Note that incident reassignment is asynchronous and may not complete before the API call returns."""
    path: DeleteUserRequestPath
    header: DeleteUserRequestHeader

# Operation: list_user_audit_records
class ListUsersAuditRecordsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose audit records you want to retrieve.")
class ListUsersAuditRecordsRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="The start of the date range for the audit search in ISO 8601 format. Defaults to 24 hours before the current time if not specified.", json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="The end of the date range for the audit search in ISO 8601 format. Defaults to the current time if not specified. Cannot be more than 31 days after the `since` parameter.", json_schema_extra={'format': 'date-time'})
class ListUsersAuditRecordsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to `application/vnd.pagerduty+json;version=2` to specify the API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be `application/json`.")
class ListUsersAuditRecordsRequest(StrictModel):
    """Retrieve audit records showing changes made to a specific user. Records are sorted by execution time from newest to oldest and support cursor-based pagination."""
    path: ListUsersAuditRecordsRequestPath
    query: ListUsersAuditRecordsRequestQuery | None = None
    header: ListUsersAuditRecordsRequestHeader

# Operation: list_user_contact_methods
class GetUserContactMethodsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose contact methods you want to retrieve.")
class GetUserContactMethodsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request content type. Must be set to application/json.")
class GetUserContactMethodsRequest(StrictModel):
    """Retrieve all contact methods configured for a PagerDuty user. Contact methods define how a user can be reached during incidents and alerts."""
    path: GetUserContactMethodsRequestPath
    header: GetUserContactMethodsRequestHeader

# Operation: create_user_contact_method
class CreateUserContactMethodRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user for whom the contact method is being created.")
class CreateUserContactMethodRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format. Must be application/json.")
class CreateUserContactMethodRequestBody(StrictModel):
    """The contact method to be created."""
    contact_method: PhoneContactMethod | PushContactMethod | EmailContactMethod | WhatsAppContactMethod = Field(default=..., description="The contact method object containing details such as type (email, phone, SMS, etc.) and address. Refer to API documentation for required and optional fields.")
class CreateUserContactMethodRequest(StrictModel):
    """Create a new contact method for a PagerDuty user, enabling them to receive notifications through additional channels. Requires users:contact_methods.write OAuth scope."""
    path: CreateUserContactMethodRequestPath
    header: CreateUserContactMethodRequestHeader
    body: CreateUserContactMethodRequestBody

# Operation: get_user_contact_method
class GetUserContactMethodRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose contact method you want to retrieve.")
    contact_method_id: str = Field(default=..., description="The unique identifier of the contact method belonging to the specified user.")
class GetUserContactMethodRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type for the request body. Must be JSON format.")
class GetUserContactMethodRequest(StrictModel):
    """Retrieve details about a specific contact method for a PagerDuty user. Contact methods define how users can be reached for incident notifications."""
    path: GetUserContactMethodRequestPath
    header: GetUserContactMethodRequestHeader

# Operation: update_user_contact_method
class UpdateUserContactMethodRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose contact method is being updated.")
    contact_method_id: str = Field(default=..., description="The unique identifier of the contact method to update on the user.")
class UpdateUserContactMethodRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to use the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type of the request body. Must be application/json.")
class UpdateUserContactMethodRequestBody(StrictModel):
    """The user's contact method to be updated."""
    contact_method: PhoneContactMethod | PushContactMethod | EmailContactMethod | WhatsAppContactMethod = Field(default=..., description="The contact method object containing the updated configuration details for the user's contact method.")
class UpdateUserContactMethodRequest(StrictModel):
    """Update a specific contact method for a PagerDuty user. This allows modification of how a user can be reached for incident notifications and communications."""
    path: UpdateUserContactMethodRequestPath
    header: UpdateUserContactMethodRequestHeader
    body: UpdateUserContactMethodRequestBody

# Operation: delete_user_contact_method
class DeleteUserContactMethodRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose contact method will be deleted.")
    contact_method_id: str = Field(default=..., description="The unique identifier of the contact method to be removed from the user.")
class DeleteUserContactMethodRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to the PagerDuty API version 2 content type.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body. Must be JSON format.")
class DeleteUserContactMethodRequest(StrictModel):
    """Remove a contact method from a PagerDuty user account. This operation permanently deletes the specified contact method, preventing further notifications through that channel."""
    path: DeleteUserContactMethodRequestPath
    header: DeleteUserContactMethodRequestHeader

# Operation: list_user_oauth_delegations
class ListUserDelegationsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose delegations you want to retrieve.")
class ListUserDelegationsRequestQuery(StrictModel):
    delegation_type: Literal["mobile", "web", "integration"] | None = Field(default=None, description="Filter delegations by type. Accepts one or more values (mobile, web, or integration) separated by commas to return delegations matching any of the specified types.")
    status: Literal["issued", "revoked"] | None = Field(default=None, description="Filter delegations by status. Accepts one or more values (issued or revoked) separated by commas to return delegations matching any of the specified statuses.")
class ListUserDelegationsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request content type as JSON.")
class ListUserDelegationsRequest(StrictModel):
    """Retrieve a list of OAuth delegations for a specific user, with optional filtering by delegation type and status. This endpoint replaces the deprecated sessions endpoint."""
    path: ListUserDelegationsRequestPath
    query: ListUserDelegationsRequestQuery | None = None
    header: ListUserDelegationsRequestHeader

# Operation: get_user_oauth_delegation
class GetUserDelegationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose delegation you want to retrieve.")
    delegation_id: str = Field(default=..., description="The unique identifier of the OAuth delegation to retrieve.")
class GetUserDelegationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The content type for the request body. Must be JSON format.")
class GetUserDelegationRequest(StrictModel):
    """Retrieve details about a specific OAuth delegation for a user. This endpoint replaces the deprecated session-based endpoint and requires the `oauth_delegations.read` OAuth scope."""
    path: GetUserDelegationRequestPath
    header: GetUserDelegationRequestHeader

# Operation: get_user_license
class GetUserLicenseRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose license allocation you want to retrieve.")
class GetUserLicenseRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body. Must be set to application/json.")
class GetUserLicenseRequest(StrictModel):
    """Retrieve the license currently allocated to a specific user. Returns the license details associated with the user's account."""
    path: GetUserLicenseRequestPath
    header: GetUserLicenseRequestHeader

# Operation: list_user_notification_rules
class GetUserNotificationRulesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose notification rules you want to retrieve.")
class GetUserNotificationRulesRequestQuery(StrictModel):
    include: Annotated[Literal["contact_methods"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array to include additional related data in the response. Specify 'contact_methods' to include the user's contact methods associated with each notification rule.")
    urgency: Annotated[Literal["high", "low", "all"], AfterValidator(_check_unique_items)] | None = Field(default=None, description="Filter notification rules by incident urgency level. Use 'high' for high-urgency incidents, 'low' for low-urgency incidents, or 'all' to retrieve rules for all urgency levels. Defaults to 'high' if not specified.")
class GetUserNotificationRulesRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="HTTP header specifying the API version. Must be set to 'application/vnd.pagerduty+json;version=2' to use the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="HTTP header specifying the request content type. Must be 'application/json'.")
class GetUserNotificationRulesRequest(StrictModel):
    """Retrieve notification rules configured for a PagerDuty user. Notification rules determine how and when the user receives alerts based on incident urgency."""
    path: GetUserNotificationRulesRequestPath
    query: GetUserNotificationRulesRequestQuery | None = None
    header: GetUserNotificationRulesRequestHeader

# Operation: get_user_notification_rule
class GetUserNotificationRuleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose notification rule you want to retrieve.")
    notification_rule_id: str = Field(default=..., description="The unique identifier of the notification rule to retrieve.")
class GetUserNotificationRuleRequestQuery(StrictModel):
    include: Annotated[Literal["contact_methods"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array to include additional related data. Specify 'contact_methods' to include the contact methods associated with this notification rule.")
class GetUserNotificationRuleRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use the default PagerDuty API version 2 format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be JSON format.")
class GetUserNotificationRuleRequest(StrictModel):
    """Retrieve details about a specific notification rule for a PagerDuty user. Notification rules define how and when users receive alerts for incidents."""
    path: GetUserNotificationRuleRequestPath
    query: GetUserNotificationRuleRequestQuery | None = None
    header: GetUserNotificationRuleRequestHeader

# Operation: update_user_notification_rule
class UpdateUserNotificationRuleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose notification rule is being updated.")
    notification_rule_id: str = Field(default=..., description="The unique identifier of the notification rule to update.")
class UpdateUserNotificationRuleRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to use the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type of the request body. Must be application/json.")
class UpdateUserNotificationRuleRequestBody(StrictModel):
    """The user's notification rule to be updated."""
    notification_rule: NotificationRule = Field(default=..., description="The notification rule object containing the updated configuration for the notification rule.")
class UpdateUserNotificationRuleRequest(StrictModel):
    """Update a specific notification rule for a PagerDuty user. Notification rules control how and when users receive alerts for incidents."""
    path: UpdateUserNotificationRuleRequestPath
    header: UpdateUserNotificationRuleRequestHeader
    body: UpdateUserNotificationRuleRequestBody

# Operation: delete_user_notification_rule
class DeleteUserNotificationRuleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose notification rule will be deleted.")
    notification_rule_id: str = Field(default=..., description="The unique identifier of the notification rule to be removed from the user.")
class DeleteUserNotificationRuleRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to use the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request body format as JSON.")
class DeleteUserNotificationRuleRequest(StrictModel):
    """Remove a specific notification rule from a PagerDuty user. This permanently deletes the user's notification rule configuration."""
    path: DeleteUserNotificationRuleRequestPath
    header: DeleteUserNotificationRuleRequestHeader

# Operation: list_user_notification_subscriptions
class GetUserNotificationSubscriptionsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose notification subscriptions you want to retrieve.")
class GetUserNotificationSubscriptionsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API version header for response formatting. Defaults to PagerDuty API v2 JSON format if not specified.")
class GetUserNotificationSubscriptionsRequest(StrictModel):
    """Retrieve all notification subscriptions for a specific user. Only subscriptions that were explicitly added through the create endpoint will be returned."""
    path: GetUserNotificationSubscriptionsRequestPath
    header: GetUserNotificationSubscriptionsRequestHeader

# Operation: create_user_notification_subscriptions
class CreateUserNotificationSubscriptionsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user for whom to create notification subscriptions.")
class CreateUserNotificationSubscriptionsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default PagerDuty JSON format version 2.")
class CreateUserNotificationSubscriptionsRequestBody(StrictModel):
    """The entities to subscribe to."""
    subscribables: Annotated[list[NotificationSubscribable], AfterValidator(_check_unique_items)] = Field(default=..., description="Array of subscribable resources to create subscriptions for. Must contain at least one item. Each item specifies a resource the user wants to receive notifications about.", min_length=1)
class CreateUserNotificationSubscriptionsRequest(StrictModel):
    """Create one or more notification subscriptions for a user to receive alerts about specific resources or events. Requires the `subscribers.write` OAuth scope."""
    path: CreateUserNotificationSubscriptionsRequestPath
    header: CreateUserNotificationSubscriptionsRequestHeader
    body: CreateUserNotificationSubscriptionsRequestBody

# Operation: remove_user_notification_subscriptions
class UnsubscribeUserNotificationSubscriptionsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user to unsubscribe from notifications.")
class UnsubscribeUserNotificationSubscriptionsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Use application/vnd.pagerduty+json;version=2 to specify the response format and API version.")
class UnsubscribeUserNotificationSubscriptionsRequestBody(StrictModel):
    """The entities to unsubscribe from."""
    subscribables: Annotated[list[NotificationSubscribable], AfterValidator(_check_unique_items)] = Field(default=..., description="Array of subscribable entity identifiers to unsubscribe from. Must contain at least one entity ID. Order is not significant.", min_length=1)
class UnsubscribeUserNotificationSubscriptionsRequest(StrictModel):
    """Unsubscribe a user from notifications on specified subscribable entities. Requires the subscribers.write OAuth scope."""
    path: UnsubscribeUserNotificationSubscriptionsRequestPath
    header: UnsubscribeUserNotificationSubscriptionsRequestHeader
    body: UnsubscribeUserNotificationSubscriptionsRequestBody

# Operation: get_user_oncall_handoff_notification_rule
class GetUserHandoffNotifiactionRuleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user resource.")
    oncall_handoff_notification_rule_id: str = Field(default=..., description="The unique identifier of the on-call handoff notification rule associated with the user.")
class GetUserHandoffNotifiactionRuleRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to use the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be application/json.")
class GetUserHandoffNotifiactionRuleRequest(StrictModel):
    """Retrieve a specific on-call handoff notification rule for a user. This returns the configuration details for how a user is notified when on-call responsibilities are handed off."""
    path: GetUserHandoffNotifiactionRuleRequestPath
    header: GetUserHandoffNotifiactionRuleRequestHeader

# Operation: delete_user_oncall_handoff_notification_rule
class DeleteUserHandoffNotificationRuleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose handoff notification rule should be deleted.")
    oncall_handoff_notification_rule_id: str = Field(default=..., description="The unique identifier of the specific handoff notification rule to delete from the user's account.")
class DeleteUserHandoffNotificationRuleRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Must be set to application/vnd.pagerduty+json;version=2 to use the current API version.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class DeleteUserHandoffNotificationRuleRequest(StrictModel):
    """Remove a specific handoff notification rule from a user's on-call settings. This operation permanently deletes the rule, preventing further notifications based on that rule's configuration."""
    path: DeleteUserHandoffNotificationRuleRequestPath
    header: DeleteUserHandoffNotificationRuleRequestHeader

# Operation: delete_user_status_update_notification_rule
class DeleteUserStatusUpdateNotificationRuleRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose notification rule will be deleted.")
    status_update_notification_rule_id: str = Field(default=..., description="The unique identifier of the status update notification rule to be removed from the user.")
class DeleteUserStatusUpdateNotificationRuleRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request content type. Must be application/json.")
class DeleteUserStatusUpdateNotificationRuleRequest(StrictModel):
    """Remove a specific status update notification rule from a user's account. This operation permanently deletes the notification rule, preventing further status update notifications according to that rule's configuration."""
    path: DeleteUserStatusUpdateNotificationRuleRequestPath
    header: DeleteUserStatusUpdateNotificationRuleRequestHeader

# Operation: get_current_user
class GetCurrentUserRequestQuery(StrictModel):
    include: Annotated[Literal["contact_methods", "notification_rules", "teams", "subdomains"], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Optional array of related resources to include in the response. Valid options are contact_methods, notification_rules, teams, and subdomains.")
class GetCurrentUserRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Content type for the request body. Must be application/json.")
class GetCurrentUserRequest(StrictModel):
    """Retrieve details about the authenticated user. This operation requires a user-level API key or OAuth token and cannot be used with account-level access tokens."""
    query: GetCurrentUserRequestQuery | None = None
    header: GetCurrentUserRequestHeader

# Operation: list_vendors
class ListVendorsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to the PagerDuty JSON API version 2 format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Specifies the request content type. Must be set to application/json.")
class ListVendorsRequest(StrictModel):
    """Retrieve a list of all available PagerDuty vendors, which represent specific types of integrations such as AWS Cloudwatch, Splunk, and Datadog. Use this to discover supported integration types for your account."""
    header: ListVendorsRequestHeader

# Operation: list_schedules
class ListSchedulesV3RequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required header indicating acceptance of the Early Access API contract. This endpoint is under active development and may change without notice—do not use in production. Must be set to the fixed value `flexible-schedules-early-access`.")
class ListSchedulesV3Request(StrictModel):
    """Retrieve a paginated list of schedule references with lightweight objects. Results are automatically filtered by your read permissions; schedules you cannot access are excluded."""
    header: ListSchedulesV3RequestHeader

# Operation: create_schedule
class CreateScheduleV3RequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Early access header required to use this API. Must be set to the fixed value `flexible-schedules-early-access`. This endpoint is under active development and may change without notice.")
class CreateScheduleV3RequestBodySchedule(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The name of the schedule. Must be between 1 and 255 characters.", min_length=1, max_length=255)
    time_zone: str = Field(default=..., validation_alias="time_zone", serialization_alias="time_zone", description="IANA timezone identifier (e.g., America/New_York, Europe/London) that determines the timezone context for all schedule operations.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Optional description of the schedule's purpose or scope. Maximum 1024 characters.", max_length=1024)
    teams: list[CreateScheduleV3BodyScheduleTeamsItem] | None = Field(default=None, validation_alias="teams", serialization_alias="teams", description="Optional list of teams to associate with this schedule. Teams will have access to and visibility of this schedule.")
class CreateScheduleV3RequestBody(StrictModel):
    schedule: CreateScheduleV3RequestBodySchedule
class CreateScheduleV3Request(StrictModel):
    """Create a new on-call schedule with basic metadata. Rotations and events must be added separately after creation using dedicated API endpoints."""
    header: CreateScheduleV3RequestHeader
    body: CreateScheduleV3RequestBody

# Operation: get_schedule_with_final_assignments
class GetScheduleV3RequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule to retrieve.")
class GetScheduleV3RequestQuery(StrictModel):
    since: str | None = Field(default=None, description="Start of the time range for computing final schedule assignments, specified in ISO 8601 date-time format (e.g., 2025-01-01T00:00:00Z). Only used when final_schedule is included.", json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="End of the time range for computing final schedule assignments, specified in ISO 8601 date-time format (e.g., 2025-01-31T23:59:59Z). Only used when final_schedule is included.", json_schema_extra={'format': 'date-time'})
    time_zone: str | None = Field(default=None, description="IANA timezone identifier for rendering shift times in the response (e.g., America/New_York). If not specified, defaults to the schedule's configured timezone.")
    overflow: bool | None = Field(default=None, description="When true, includes shifts that extend beyond the requested time range boundaries. Defaults to false.")
    include: list[Literal["final_schedule"]] | None = Field(default=None, validation_alias="include[]", serialization_alias="include[]", description="Array of additional data to include in the response. Use 'final_schedule' to compute on-call assignments for the specified time range.")
class GetScheduleV3RequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required header indicating acceptance of the Early Access API terms. Must be set to 'flexible-schedules-early-access'. This endpoint is under construction and may change without notice.")
class GetScheduleV3Request(StrictModel):
    """Retrieve a schedule by ID with its rotations and events. Optionally compute on-call assignments for a specified time range by including the final schedule in the response."""
    path: GetScheduleV3RequestPath
    query: GetScheduleV3RequestQuery | None = None
    header: GetScheduleV3RequestHeader

# Operation: update_schedule
class UpdateScheduleV3RequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule to update.")
class UpdateScheduleV3RequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required early access header to indicate acceptance of potential API changes. Must be set to the fixed value 'flexible-schedules-early-access'. Do not use this endpoint in production.")
class UpdateScheduleV3RequestBodySchedule(StrictModel):
    time_zone: str | None = Field(default=None, validation_alias="time_zone", serialization_alias="time_zone", description="The time zone for the schedule (e.g., 'America/Los_Angeles'). Optional; only provided values are updated.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A description of the schedule, up to 1024 characters. Optional; only provided values are updated.", max_length=1024)
class UpdateScheduleV3RequestBody(StrictModel):
    schedule: UpdateScheduleV3RequestBodySchedule | None = None
class UpdateScheduleV3Request(StrictModel):
    """Update schedule metadata including name, description, and time zone. This is an early access endpoint that only modifies schedule properties; use dedicated endpoints to modify rotations or events."""
    path: UpdateScheduleV3RequestPath
    header: UpdateScheduleV3RequestHeader
    body: UpdateScheduleV3RequestBody | None = None

# Operation: delete_schedule
class DeleteScheduleV3RequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule to delete.")
class DeleteScheduleV3RequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required header to access this early-access API endpoint. Must be set to `flexible-schedules-early-access`. This API is under active development and may change without notice—do not use in production.")
class DeleteScheduleV3Request(StrictModel):
    """Permanently delete a schedule along with all its associated rotations and events. The operation will fail if the schedule is currently referenced by an active escalation policy."""
    path: DeleteScheduleV3RequestPath
    header: DeleteScheduleV3RequestHeader

# Operation: list_custom_shifts
class ListCustomShiftsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule to retrieve custom shifts for.")
class ListCustomShiftsRequestQuery(StrictModel):
    since: str = Field(default=..., description="Start of the time range for retrieving shifts, specified in ISO 8601 date-time format (e.g., 2025-01-01T00:00:00Z). Required parameter.", json_schema_extra={'format': 'date-time'})
    until: str = Field(default=..., description="End of the time range for retrieving shifts, specified in ISO 8601 date-time format (e.g., 2025-01-31T23:59:59Z). Required parameter.", json_schema_extra={'format': 'date-time'})
    time_zone: str | None = Field(default=None, description="IANA timezone identifier used to render shift times in the response. If not provided, defaults to the schedule's configured timezone (e.g., America/New_York).")
    overflow: bool | None = Field(default=None, description="When enabled, includes shifts that extend beyond the requested time range boundaries. Defaults to false, returning only shifts fully contained within the range.")
class ListCustomShiftsRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required header indicating acceptance of Early Access API terms. Must be set to the value 'flexible-schedules-early-access'. This endpoint is under construction and may change without notice.")
class ListCustomShiftsRequest(StrictModel):
    """Retrieve custom shifts for a schedule within a specified time range. This endpoint is in Early Access and requires the X-EARLY-ACCESS header on every request."""
    path: ListCustomShiftsRequestPath
    query: ListCustomShiftsRequestQuery
    header: ListCustomShiftsRequestHeader

# Operation: create_custom_shifts
class CreateCustomShiftsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule where custom shifts will be created.")
class CreateCustomShiftsRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required header indicating acceptance of Early Access API terms. Must be set to the fixed value 'flexible-schedules-early-access'. Do not use this endpoint in production as it may change without notice.")
class CreateCustomShiftsRequestBody(StrictModel):
    custom_shifts: list[CreateCustomShiftsBodyCustomShiftsItem] = Field(default=..., description="Array of custom shift objects to create. At least one custom shift is required per request. Each shift must include exactly one assignment.", min_length=1)
class CreateCustomShiftsRequest(StrictModel):
    """Create one or more ad-hoc custom shifts for a schedule that exist outside of rotation events. Each custom shift requires exactly one assignment. This endpoint is in Early Access and may change at any time."""
    path: CreateCustomShiftsRequestPath
    header: CreateCustomShiftsRequestHeader
    body: CreateCustomShiftsRequestBody

# Operation: get_custom_shift
class GetCustomShiftRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule containing the custom shift.")
    custom_shift_id: str = Field(default=..., description="The unique identifier of the custom shift to retrieve.")
class GetCustomShiftRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required early access header to indicate acceptance of the API's early access status and potential changes. Must be set to the fixed value `flexible-schedules-early-access`. Do not use this endpoint in production.")
class GetCustomShiftRequest(StrictModel):
    """Retrieve a single custom shift by its ID from a schedule. This endpoint is in early access and requires the early access header to be passed with every request."""
    path: GetCustomShiftRequestPath
    header: GetCustomShiftRequestHeader

# Operation: update_custom_shift
class UpdateCustomShiftRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule containing the custom shift.")
    custom_shift_id: str = Field(default=..., description="The unique identifier of the custom shift to update.")
class UpdateCustomShiftRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required header indicating acceptance of Early Access API terms. Must be set to 'flexible-schedules-early-access'. This API is under construction and may change without notice—do not use in production.")
class UpdateCustomShiftRequestBodyCustomShift(StrictModel):
    start_time: str | None = Field(default=None, validation_alias="start_time", serialization_alias="start_time", description="The start time for the custom shift in ISO 8601 date-time format. Cannot be modified if the shift has already started.", json_schema_extra={'format': 'date-time'})
    end_time: str | None = Field(default=None, validation_alias="end_time", serialization_alias="end_time", description="The end time for the custom shift in ISO 8601 date-time format. This is the only field that can be modified after a shift has started.", json_schema_extra={'format': 'date-time'})
    assignments: list[UpdateCustomShiftBodyCustomShiftAssignmentsItem] | None = Field(default=None, validation_alias="assignments", serialization_alias="assignments", description="Array of shift assignments. Must contain exactly one assignment. Order and format follow the API's assignment schema.", min_length=1, max_length=1)
class UpdateCustomShiftRequestBody(StrictModel):
    custom_shift: UpdateCustomShiftRequestBodyCustomShift | None = None
class UpdateCustomShiftRequest(StrictModel):
    """Update an existing custom shift in a schedule. If the shift has already started, only the end time can be modified. This endpoint is in Early Access and requires the X-EARLY-ACCESS header."""
    path: UpdateCustomShiftRequestPath
    header: UpdateCustomShiftRequestHeader
    body: UpdateCustomShiftRequestBody | None = None

# Operation: delete_custom_shift
class DeleteCustomShiftRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule containing the custom shift.")
    custom_shift_id: str = Field(default=..., description="The unique identifier of the custom shift to delete.")
class DeleteCustomShiftRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required early access header to use this API endpoint. Must be set to `flexible-schedules-early-access`. This endpoint is under active development and may change without notice—do not use in production.")
class DeleteCustomShiftRequest(StrictModel):
    """Delete a custom shift from a schedule. If the shift hasn't started, it removes the shift entirely; if already in progress, it ends the shift immediately. Returns an error if the shift has already ended."""
    path: DeleteCustomShiftRequestPath
    header: DeleteCustomShiftRequestHeader

# Operation: list_schedule_overrides
class ListOverridesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule to retrieve overrides for.")
class ListOverridesRequestQuery(StrictModel):
    since: str = Field(default=..., description="Start of the time range for retrieving overrides, specified in ISO 8601 date-time format (e.g., 2025-01-01T00:00:00Z).", json_schema_extra={'format': 'date-time'})
    until: str = Field(default=..., description="End of the time range for retrieving overrides, specified in ISO 8601 date-time format (e.g., 2025-01-31T23:59:59Z). Must be after the since parameter.", json_schema_extra={'format': 'date-time'})
    time_zone: str | None = Field(default=None, description="IANA timezone identifier used to render shift times in the response. If not provided, defaults to the schedule's configured timezone (e.g., America/New_York).")
    overflow: bool | None = Field(default=None, description="When enabled, includes shifts that extend beyond the requested time range boundaries. Defaults to false.")
class ListOverridesRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required Early Access header that must be set to 'flexible-schedules-early-access' to use this endpoint. This API is under construction and may change without notice.")
class ListOverridesRequest(StrictModel):
    """Retrieve all schedule overrides within a specified time range. This endpoint requires the Early Access header and both start and end times in ISO 8601 format."""
    path: ListOverridesRequestPath
    query: ListOverridesRequestQuery
    header: ListOverridesRequestHeader

# Operation: create_schedule_overrides
class CreateOverridesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule for which to create overrides.")
class CreateOverridesRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required Early Access header that must be set to 'flexible-schedules-early-access' to use this endpoint. This API is under construction and may change at any time.")
class CreateOverridesRequestBody(StrictModel):
    overrides: list[CreateOverridesBodyOverridesItem] = Field(default=..., description="Array of one or more override objects to create. Each override must reference either a rotation_id or custom_shift_id (not both), and the overriding member must belong to the account.", min_length=1)
class CreateOverridesRequest(StrictModel):
    """Create one or more overrides for a schedule to temporarily replace scheduled on-call members with different members for specific time periods. This endpoint is in Early Access and requires the X-EARLY-ACCESS header."""
    path: CreateOverridesRequestPath
    header: CreateOverridesRequestHeader
    body: CreateOverridesRequestBody

# Operation: get_override
class GetOverrideRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule containing the override.")
    override_id: str = Field(default=..., description="The unique identifier of the override to retrieve.")
class GetOverrideRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required early access header to use this endpoint. Must be set to `flexible-schedules-early-access`. This API is under construction and may change at any time; do not use in production.")
class GetOverrideRequest(StrictModel):
    """Retrieve a single schedule override by its ID. This endpoint is in early access and requires the early access header on every request."""
    path: GetOverrideRequestPath
    header: GetOverrideRequestHeader

# Operation: update_schedule_override
class UpdateOverrideRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule containing the override to update.")
    override_id: str = Field(default=..., description="The unique identifier of the override to update.")
class UpdateOverrideRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required early access header that must be set to `flexible-schedules-early-access` to use this endpoint. This API is under construction and may change without notice.")
class UpdateOverrideRequestBodyOverrideOverridingMember(StrictModel):
    type_: Literal["user_member", "empty_member"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of override assignment: `user_member` to assign a specific user, or `empty_member` to intentionally leave the slot unassigned.")
    user_id: str | None = Field(default=None, validation_alias="user_id", serialization_alias="user_id", description="The ID of the user to assign to this override. Required when type is set to `user_member`.")
class UpdateOverrideRequestBodyOverride(StrictModel):
    start_time: str | None = Field(default=None, validation_alias="start_time", serialization_alias="start_time", description="The start time for the override in ISO 8601 date-time format. Defines when the override begins.", json_schema_extra={'format': 'date-time'})
    end_time: str | None = Field(default=None, validation_alias="end_time", serialization_alias="end_time", description="The end time for the override in ISO 8601 date-time format. Defines when the override ends.", json_schema_extra={'format': 'date-time'})
    overriding_member: UpdateOverrideRequestBodyOverrideOverridingMember
class UpdateOverrideRequestBody(StrictModel):
    override: UpdateOverrideRequestBodyOverride
class UpdateOverrideRequest(StrictModel):
    """Update an existing override for a schedule, allowing you to modify the time window and assignment (either to a specific user or leave the slot intentionally unassigned). This endpoint is in early access and requires the early access header."""
    path: UpdateOverrideRequestPath
    header: UpdateOverrideRequestHeader
    body: UpdateOverrideRequestBody

# Operation: delete_schedule_override
class DeleteOverrideRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule containing the override to delete.")
    override_id: str = Field(default=..., description="The unique identifier of the override to delete.")
class DeleteOverrideRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required early access header to acknowledge this API is under construction and subject to change. Must be set to the fixed value `flexible-schedules-early-access`.")
class DeleteOverrideRequest(StrictModel):
    """Remove a specific override from a schedule. This endpoint is in early access and may change; include the required early access header with every request."""
    path: DeleteOverrideRequestPath
    header: DeleteOverrideRequestHeader

# Operation: list_rotations
class ListRotationsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule for which to retrieve rotations.")
class ListRotationsRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required early access header to acknowledge this API is under construction and may change. Must be set to the fixed value `flexible-schedules-early-access`.")
class ListRotationsRequest(StrictModel):
    """Retrieve all rotations configured for a specific schedule. This endpoint is in early access and requires the early access header on every request."""
    path: ListRotationsRequestPath
    header: ListRotationsRequestHeader

# Operation: create_rotation_for_schedule
class CreateRotationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule to which the rotation will be added.")
class CreateRotationRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required header indicating acceptance of Early Access API terms. Must be set to the specified value to proceed with the request.")
class CreateRotationRequestBody(StrictModel):
    body: dict[str, Any] | None = Field(default=None, description="Request body must be empty or an empty object. Rotations carry no configuration at creation time; all scheduling logic is defined through events added after creation.")
class CreateRotationRequest(StrictModel):
    """Create a new empty rotation within a schedule. After creation, add events to define the on-call pattern and scheduling logic. Note: This API is in Early Access and may change at any time."""
    path: CreateRotationRequestPath
    header: CreateRotationRequestHeader
    body: CreateRotationRequestBody | None = None

# Operation: get_rotation
class GetRotationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule containing the rotation.")
    rotation_id: str = Field(default=..., description="The unique identifier of the rotation to retrieve.")
class GetRotationRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="Optional start of the time range for filtering events, specified in ISO 8601 format (e.g., 2025-01-01T00:00:00Z).", json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="Optional end of the time range for filtering events, specified in ISO 8601 format (e.g., 2025-01-31T23:59:59Z).", json_schema_extra={'format': 'date-time'})
class GetRotationRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required header indicating acceptance of the Early Access API status. Must be set to `flexible-schedules-early-access`. This endpoint is under construction and may change without notice—do not use in production.")
class GetRotationRequest(StrictModel):
    """Retrieve a specific rotation by ID, including all its scheduled events. Optionally filter events by a time range using ISO 8601 timestamps."""
    path: GetRotationRequestPath
    query: GetRotationRequestQuery | None = None
    header: GetRotationRequestHeader

# Operation: delete_rotation
class DeleteRotationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule containing the rotation to delete.")
    rotation_id: str = Field(default=..., description="The unique identifier of the rotation to delete.")
class DeleteRotationRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required header indicating acceptance of the Early Access API terms. This endpoint is under active development and may change without notice. Must be set to the fixed value `flexible-schedules-early-access`. Do not use in production environments.")
class DeleteRotationRequest(StrictModel):
    """Permanently delete a rotation and all its associated events from a schedule. Past events are preserved in audit history, the current active event is truncated to the deletion time, and all future events are removed."""
    path: DeleteRotationRequestPath
    header: DeleteRotationRequestHeader

# Operation: list_rotation_events
class ListEventsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule containing the rotation.")
    rotation_id: str = Field(default=..., description="The unique identifier of the rotation within the schedule.")
class ListEventsRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required early access header to use this endpoint. Must be set to `flexible-schedules-early-access`. This API is under construction and may change at any time; do not use in production.")
class ListEventsRequest(StrictModel):
    """Retrieve all events for a rotation within a schedule, ordered by start time. This endpoint is in early access and requires the early access header."""
    path: ListEventsRequestPath
    header: ListEventsRequestHeader

# Operation: create_rotation_event
class CreateEventRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule containing the rotation.")
    rotation_id: str = Field(default=..., description="The unique identifier of the rotation within the schedule.")
class CreateEventRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required header indicating acceptance of the Early Access API. Must be set to `flexible-schedules-early-access`. This endpoint is under construction and may change without notice—do not use in production.")
class CreateEventRequestBodyEventStartTime(StrictModel):
    date_time: str = Field(default=..., validation_alias="date_time", serialization_alias="date_time", description="The start date and time for the event in ISO 8601 format (e.g., 2025-03-03T09:00:00Z).", json_schema_extra={'format': 'date-time'})
    time_zone: str = Field(default=..., validation_alias="time_zone", serialization_alias="time_zone", description="IANA timezone identifier for the event start time (e.g., America/New_York). Used to interpret the start_time in local context.")
class CreateEventRequestBodyEventEndTime(StrictModel):
    date_time: str = Field(default=..., validation_alias="date_time", serialization_alias="date_time", description="The end date and time for the event in ISO 8601 format (e.g., 2025-03-03T09:00:00Z). Must be after the start time.", json_schema_extra={'format': 'date-time'})
    time_zone: str = Field(default=..., validation_alias="time_zone", serialization_alias="time_zone", description="IANA timezone identifier for the event end time (e.g., America/New_York). Used to interpret the end_time in local context.")
class CreateEventRequestBodyEventAssignmentStrategy(StrictModel):
    type_: Literal["rotating_member_assignment_strategy", "every_member_assignment_strategy"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The assignment strategy type: `rotating_member_assignment_strategy` rotates members through shifts sequentially, while `every_member_assignment_strategy` assigns all members to each shift.")
    shifts_per_member: int | None = Field(default=None, validation_alias="shifts_per_member", serialization_alias="shifts_per_member", description="Required only for `rotating_member_assignment_strategy`. Specifies how many consecutive shift occurrences each member covers before the next member takes over. Must be at least 1.", ge=1)
    members: list[ShiftMember] = Field(default=..., validation_alias="members", serialization_alias="members", description="An array of user IDs to include in the rotation, between 1 and 20 members. All users must exist and belong to the account.", min_length=1, max_length=20)
class CreateEventRequestBodyEvent(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="A descriptive name for the event, up to 255 characters.", max_length=255)
    effective_since: str = Field(default=..., validation_alias="effective_since", serialization_alias="effective_since", description="The date and time when this event begins generating shifts, in ISO 8601 format. Past values are automatically adjusted to the current time.", json_schema_extra={'format': 'date-time'})
    effective_until: str | None = Field(default=None, validation_alias="effective_until", serialization_alias="effective_until", description="The date and time when this event stops generating shifts, in ISO 8601 format. Omit or set to null for indefinite duration.", json_schema_extra={'format': 'date-time'})
    recurrence: list[str] = Field(default=..., validation_alias="recurrence", serialization_alias="recurrence", description="An array of RFC 5545 recurrence rules that define how often the event repeats (e.g., daily, weekly, monthly patterns).")
    start_time: CreateEventRequestBodyEventStartTime
    end_time: CreateEventRequestBodyEventEndTime
    assignment_strategy: CreateEventRequestBodyEventAssignmentStrategy
class CreateEventRequestBody(StrictModel):
    event: CreateEventRequestBodyEvent
class CreateEventRequest(StrictModel):
    """Create a new event that defines when and how users are on-call within a rotation. Events specify time periods, recurrence patterns, and member assignment strategies, with a maximum of 5 non-overlapping events per rotation."""
    path: CreateEventRequestPath
    header: CreateEventRequestHeader
    body: CreateEventRequestBody

# Operation: get_event_in_rotation
class GetEventRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule containing the rotation.")
    rotation_id: str = Field(default=..., description="The unique identifier of the rotation containing the event.")
    event_id: str = Field(default=..., description="The unique identifier of the event to retrieve.")
class GetEventRequestQuery(StrictModel):
    since: str | None = Field(default=None, description="Optional start of the time range for filtering results, specified in ISO 8601 format (e.g., 2025-01-01T00:00:00Z).", json_schema_extra={'format': 'date-time'})
    until: str | None = Field(default=None, description="Optional end of the time range for filtering results, specified in ISO 8601 format (e.g., 2025-01-31T23:59:59Z).", json_schema_extra={'format': 'date-time'})
class GetEventRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required early access header that must be set to `flexible-schedules-early-access` to use this endpoint. This API is under construction and may change at any time; do not use in production.")
class GetEventRequest(StrictModel):
    """Retrieve a specific event from a schedule rotation by its ID. This endpoint is in early access and requires the early access header on every request."""
    path: GetEventRequestPath
    query: GetEventRequestQuery | None = None
    header: GetEventRequestHeader

# Operation: update_rotation_event
class UpdateEventRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule containing the rotation.")
    rotation_id: str = Field(default=..., description="The unique identifier of the rotation containing the event to update.")
    event_id: str = Field(default=..., description="The unique identifier of the event to update.")
class UpdateEventRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required Early Access header to acknowledge this API is under construction and may change. Must be set to the fixed value 'flexible-schedules-early-access'.")
class UpdateEventRequestBodyEventStartTime(StrictModel):
    date_time: str = Field(default=..., validation_alias="date_time", serialization_alias="date_time", description="The start date and time for the event in ISO 8601 format (e.g., 2025-03-03T09:00:00Z).", json_schema_extra={'format': 'date-time'})
    time_zone: str = Field(default=..., validation_alias="time_zone", serialization_alias="time_zone", description="IANA timezone identifier for the event start time (e.g., America/New_York). Determines how the start_time.date_time is interpreted.")
class UpdateEventRequestBodyEventEndTime(StrictModel):
    date_time: str = Field(default=..., validation_alias="date_time", serialization_alias="date_time", description="The end date and time for the event in ISO 8601 format (e.g., 2025-03-03T09:00:00Z).", json_schema_extra={'format': 'date-time'})
    time_zone: str = Field(default=..., validation_alias="time_zone", serialization_alias="time_zone", description="IANA timezone identifier for the event end time (e.g., America/New_York). Determines how the end_time.date_time is interpreted.")
class UpdateEventRequestBodyEventAssignmentStrategy(StrictModel):
    type_: Literal["rotating_member_assignment_strategy", "every_member_assignment_strategy"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The assignment strategy type for the event. Choose 'rotating_member_assignment_strategy' to rotate members through shifts, or 'every_member_assignment_strategy' to assign all members to each shift.")
    shifts_per_member: int | None = Field(default=None, validation_alias="shifts_per_member", serialization_alias="shifts_per_member", description="Required when using 'rotating_member_assignment_strategy'. Specifies how many consecutive shift occurrences each member covers before the next member takes over. Must be at least 1.", ge=1)
    members: list[ShiftMember] = Field(default=..., validation_alias="members", serialization_alias="members", description="Array of members assigned to this event. Must contain between 1 and 20 members. Order may be significant depending on the assignment strategy.", min_length=1, max_length=20)
class UpdateEventRequestBodyEvent(StrictModel):
    effective_since: str | None = Field(default=None, validation_alias="effective_since", serialization_alias="effective_since", description="Optional date-time in ISO 8601 format marking when this event becomes effective. Only modifiable for future events.", json_schema_extra={'format': 'date-time'})
    effective_until: str | None = Field(default=None, validation_alias="effective_until", serialization_alias="effective_until", description="Optional date-time in ISO 8601 format marking when this event expires. Can be updated for active events even if other fields cannot be modified.", json_schema_extra={'format': 'date-time'})
    recurrence: list[str] | None = Field(default=None, validation_alias="recurrence", serialization_alias="recurrence", description="Optional array defining recurrence rules for the event. Specify recurrence pattern details if the event should repeat.")
    start_time: UpdateEventRequestBodyEventStartTime
    end_time: UpdateEventRequestBodyEventEndTime
    assignment_strategy: UpdateEventRequestBodyEventAssignmentStrategy
class UpdateEventRequestBody(StrictModel):
    event: UpdateEventRequestBodyEvent
class UpdateEventRequest(StrictModel):
    """Update an existing event in a rotation schedule. Modification capabilities depend on event timing: past events cannot be modified, active events can only update the effective_until date, and future events support full updates. Requires the Early Access header as this API is under construction."""
    path: UpdateEventRequestPath
    header: UpdateEventRequestHeader
    body: UpdateEventRequestBody

# Operation: delete_rotation_event
class DeleteEventRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the schedule containing the rotation.")
    rotation_id: str = Field(default=..., description="The unique identifier of the rotation containing the event to delete.")
    event_id: str = Field(default=..., description="The unique identifier of the event to delete from the rotation.")
class DeleteEventRequestHeader(StrictModel):
    x_early_access: Literal["flexible-schedules-early-access"] = Field(default=..., validation_alias="X-EARLY-ACCESS", serialization_alias="X-EARLY-ACCESS", description="Required early access header to acknowledge this API is under construction and subject to change. Must be set to `flexible-schedules-early-access`.")
class DeleteEventRequest(StrictModel):
    """Remove an event from a rotation within a schedule. This endpoint is in early access and may change; include the required early access header with every request."""
    path: DeleteEventRequestPath
    header: DeleteEventRequestHeader

# Operation: get_vendor
class GetVendorRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the vendor to retrieve.")
class GetVendorRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API version 2 in JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type for the request body. Must be application/json.")
class GetVendorRequest(StrictModel):
    """Retrieve details about a specific vendor integration type. Vendors represent integration sources like AWS Cloudwatch, Splunk, or Datadog that can be configured in PagerDuty."""
    path: GetVendorRequestPath
    header: GetVendorRequestHeader

# Operation: list_webhook_subscriptions
class ListWebhookSubscriptionsRequestQuery(StrictModel):
    filter_type: Literal["account", "service", "team"] | None = Field(default=None, description="Filter subscriptions by resource type. When set to 'service' or 'team', the filter_id parameter becomes required to specify which resource to filter by.")
    filter_id: str | None = Field(default=None, description="The ID of the resource to filter subscriptions by. Required when filter_type is 'service' or 'team'; ignored for 'account' filter type.")
class ListWebhookSubscriptionsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and schema version.")
class ListWebhookSubscriptionsRequest(StrictModel):
    """Retrieve all webhook subscriptions, optionally filtered by resource type (account, service, or team). Use filter parameters to narrow results to subscriptions for a specific service or team."""
    query: ListWebhookSubscriptionsRequestQuery | None = None
    header: ListWebhookSubscriptionsRequestHeader

# Operation: get_webhook_subscription
class GetWebhookSubscriptionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook subscription to retrieve.")
class GetWebhookSubscriptionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default PagerDuty JSON format version 2.")
class GetWebhookSubscriptionRequest(StrictModel):
    """Retrieve detailed information about a specific webhook subscription by its ID. Returns the subscription's configuration, URL, event filters, and status."""
    path: GetWebhookSubscriptionRequestPath
    header: GetWebhookSubscriptionRequestHeader

# Operation: update_webhook_subscription
class UpdateWebhookSubscriptionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook subscription to update.")
class UpdateWebhookSubscriptionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header. Defaults to application/vnd.pagerduty+json;version=2.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request content type. Must be application/json.")
class UpdateWebhookSubscriptionRequestBodyWebhookSubscriptionFilter(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The ID of the object being filtered on. Required for all filter types except account_reference filters.")
class UpdateWebhookSubscriptionRequestBodyWebhookSubscription(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A brief description of the webhook subscription's purpose.")
    events: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, validation_alias="events", serialization_alias="events", description="The outbound event types this subscription will receive. At least one event type must be specified.", min_length=1)
    active: bool | None = Field(default=None, validation_alias="active", serialization_alias="active", description="Whether the webhook is active and will send events. Defaults to true when not specified.")
    oauth_client_id: str | None = Field(default=None, validation_alias="oauth_client_id", serialization_alias="oauth_client_id", description="The OAuth client ID to use for authenticating outbound webhook requests. Optional; if not provided, webhook requests will use default authentication.")
    filter_: UpdateWebhookSubscriptionRequestBodyWebhookSubscriptionFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter")
class UpdateWebhookSubscriptionRequestBody(StrictModel):
    webhook_subscription: UpdateWebhookSubscriptionRequestBodyWebhookSubscription | None = None
class UpdateWebhookSubscriptionRequest(StrictModel):
    """Update an existing webhook subscription's configuration. Only specified fields will be updated; the delivery method cannot be changed through this operation."""
    path: UpdateWebhookSubscriptionRequestPath
    header: UpdateWebhookSubscriptionRequestHeader
    body: UpdateWebhookSubscriptionRequestBody | None = None

# Operation: enable_webhook_subscription
class EnableWebhookSubscriptionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook subscription to enable.")
class EnableWebhookSubscriptionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty API v2 JSON format.")
class EnableWebhookSubscriptionRequest(StrictModel):
    """Re-enable a webhook subscription that has been temporarily disabled due to repeated delivery failures. Use this operation to restore a subscription's functionality after the underlying delivery issue has been resolved."""
    path: EnableWebhookSubscriptionRequestPath
    header: EnableWebhookSubscriptionRequestHeader

# Operation: send_webhook_subscription_test_ping
class TestWebhookSubscriptionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook subscription to test.")
class TestWebhookSubscriptionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API version header for response formatting. Defaults to PagerDuty API v2 JSON format.")
class TestWebhookSubscriptionRequest(StrictModel):
    """Send a test event to a webhook subscription to verify it's properly configured. This fires a `pagey.ping` event to the webhook's destination endpoint."""
    path: TestWebhookSubscriptionRequestPath
    header: TestWebhookSubscriptionRequestHeader

# Operation: list_workflow_integrations
class ListWorkflowIntegrationsRequestQuery(StrictModel):
    include_deprecated: bool | None = Field(default=None, description="Set to true to include integrations that have been deprecated and are no longer actively maintained. By default, only active integrations are returned.")
class ListWorkflowIntegrationsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="Specifies the API version for the response format. Use the default application/vnd.pagerduty+json;version=2 for standard responses.")
class ListWorkflowIntegrationsRequest(StrictModel):
    """Retrieve a list of available workflow integrations that can be used to connect external services and tools to your workflows."""
    query: ListWorkflowIntegrationsRequestQuery | None = None
    header: ListWorkflowIntegrationsRequestHeader

# Operation: get_workflow_integration
class GetWorkflowIntegrationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Workflow Integration resource to retrieve.")
class GetWorkflowIntegrationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default PagerDuty JSON format version 2 for compatibility.")
class GetWorkflowIntegrationRequest(StrictModel):
    """Retrieve detailed information about a specific Workflow Integration by its ID. Returns the configuration and status of the integration."""
    path: GetWorkflowIntegrationRequestPath
    header: GetWorkflowIntegrationRequestHeader

# Operation: list_workflow_integration_connections
class ListWorkflowIntegrationConnectionsRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format and schema version. Use the default PagerDuty JSON format version 2.")
class ListWorkflowIntegrationConnectionsRequest(StrictModel):
    """Retrieve all configured workflow integration connections. Returns a list of all active connections between workflows and external integrations."""
    header: ListWorkflowIntegrationConnectionsRequestHeader

# Operation: list_workflow_integration_connections_for_integration
class ListWorkflowIntegrationConnectionsByIntegrationRequestPath(StrictModel):
    integration_id: str = Field(default=..., description="The unique identifier of the workflow integration whose connections you want to list.")
class ListWorkflowIntegrationConnectionsByIntegrationRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Defaults to PagerDuty JSON API version 2.")
class ListWorkflowIntegrationConnectionsByIntegrationRequest(StrictModel):
    """Retrieve all connections associated with a specific workflow integration. Use this to view all configured connections for a given integration."""
    path: ListWorkflowIntegrationConnectionsByIntegrationRequestPath
    header: ListWorkflowIntegrationConnectionsByIntegrationRequestHeader

# Operation: create_workflow_integration_connection
class CreateWorkflowIntegrationConnectionRequestPath(StrictModel):
    integration_id: str = Field(default=..., description="The unique identifier of the Workflow Integration for which this connection is being created.")
class CreateWorkflowIntegrationConnectionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Must be set to application/vnd.pagerduty+json;version=2 to ensure compatibility.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body. Must be application/json.")
class CreateWorkflowIntegrationConnectionRequestBody(StrictModel):
    name: str = Field(default=..., description="A human-readable name for this connection to identify it within the integration.")
    service_url: str | None = Field(default=None, description="The base URL of the external service this connection communicates with.")
    external_id: str | None = Field(default=None, description="The identifier used by the external system to reference this connection.")
    external_id_label: str | None = Field(default=None, description="A display label for the external system, used to identify the external_id in user interfaces.")
    scopes: list[str] | None = Field(default=None, description="An array of permission scopes or capabilities granted to this connection for the external system.")
    is_default: bool | None = Field(default=None, description="If true, designates this connection as the default for this integration when multiple connections exist.")
    configuration: dict[str, Any] | None = Field(default=None, description="An object containing integration-specific configuration settings. The structure and required fields are defined by the Workflow Integration's configuration_schema property.")
    secrets: dict[str, Any] = Field(default=..., description="An object containing sensitive authentication credentials required for this connection. The structure and required fields are defined by the Workflow Integration's secrets_schema property. This field is write-only and will not be returned in responses to prevent credential exposure.")
    teams: list[CreateWorkflowIntegrationConnectionBodyTeamsItem] | None = Field(default=None, description="An array of team identifiers whose managers are permitted to use or modify this connection.")
    apps: list[CreateWorkflowIntegrationConnectionBodyAppsItem] | None = Field(default=None, description="An array of application identifiers that are associated with and can use this connection.")
class CreateWorkflowIntegrationConnectionRequest(StrictModel):
    """Create a new connection for a Workflow Integration to enable external system communication. The connection stores authentication credentials, configuration, and metadata needed to establish and manage the integration."""
    path: CreateWorkflowIntegrationConnectionRequestPath
    header: CreateWorkflowIntegrationConnectionRequestHeader
    body: CreateWorkflowIntegrationConnectionRequestBody

# Operation: get_workflow_integration_connection
class GetWorkflowIntegrationConnectionRequestPath(StrictModel):
    integration_id: str = Field(default=..., description="The unique identifier of the workflow integration that contains the connection.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the workflow integration connection to retrieve.")
class GetWorkflowIntegrationConnectionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default PagerDuty JSON format version 2.")
class GetWorkflowIntegrationConnectionRequest(StrictModel):
    """Retrieve detailed information about a specific connection within a workflow integration. This operation returns the configuration and status of a single integration connection."""
    path: GetWorkflowIntegrationConnectionRequestPath
    header: GetWorkflowIntegrationConnectionRequestHeader

# Operation: update_workflow_integration_connection
class UpdateWorkflowIntegrationConnectionRequestPath(StrictModel):
    integration_id: str = Field(default=..., description="The unique identifier of the workflow integration that owns this connection.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the connection resource to update.")
class UpdateWorkflowIntegrationConnectionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API version header for response formatting. Defaults to PagerDuty API v2 JSON format.")
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="Request body content type. Must be JSON.")
class UpdateWorkflowIntegrationConnectionRequestBody(StrictModel):
    name: str = Field(default=..., description="A human-readable name for this connection.")
    service_url: str | None = Field(default=None, description="The URL endpoint of the external service this connection integrates with.")
    external_id: str | None = Field(default=None, description="The identifier used by the external system to reference this connection.")
    external_id_label: str | None = Field(default=None, description="A display label for the external system identifier.")
    scopes: list[str] | None = Field(default=None, description="An array of permission scopes or capabilities granted to this connection.")
    is_default: bool | None = Field(default=None, description="Set to true to designate this as the default connection for this integration type.")
    configuration: dict[str, Any] | None = Field(default=None, description="A JSON object containing connection-specific configuration parameters. The schema is defined by the workflow integration's configuration_schema property and varies by integration type.")
    secrets: dict[str, Any] = Field(default=..., description="A JSON object containing sensitive credentials or API keys required for authentication. The schema is defined by the workflow integration's secrets_schema property. This field is write-only and always returns null in responses to prevent secret exposure.")
    teams: list[UpdateWorkflowIntegrationConnectionBodyTeamsItem] | None = Field(default=None, description="An array of team identifiers whose managers are permitted to use or modify this connection.")
    apps: list[UpdateWorkflowIntegrationConnectionBodyAppsItem] | None = Field(default=None, description="An array of application identifiers that can use this connection.")
class UpdateWorkflowIntegrationConnectionRequest(StrictModel):
    """Update an existing workflow integration connection with new configuration, secrets, or metadata. Requires write access to workflow integration connections."""
    path: UpdateWorkflowIntegrationConnectionRequestPath
    header: UpdateWorkflowIntegrationConnectionRequestHeader
    body: UpdateWorkflowIntegrationConnectionRequestBody

# Operation: delete_workflow_integration_connection
class DeleteWorkflowIntegrationConnectionRequestPath(StrictModel):
    integration_id: str = Field(default=..., description="The unique identifier of the workflow integration that contains the connection to be deleted.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the connection resource to delete.")
class DeleteWorkflowIntegrationConnectionRequestHeader(StrictModel):
    accept: str = Field(default=..., validation_alias="Accept", serialization_alias="Accept", description="API versioning header that specifies the response format. Use the default PagerDuty JSON format version 2.")
class DeleteWorkflowIntegrationConnectionRequest(StrictModel):
    """Permanently delete a specific connection within a workflow integration. This operation removes the connection and cannot be undone."""
    path: DeleteWorkflowIntegrationConnectionRequestPath
    header: DeleteWorkflowIntegrationConnectionRequestHeader

# ============================================================================
# Component Models
# ============================================================================

class AlertCount(PermissiveModel):
    triggered: int | None = Field(None, description="The count of triggered alerts grouped into this incident")
    resolved: int | None = Field(None, description="The count of resolved alerts grouped into this incident")
    all_: int | None = Field(None, validation_alias="all", serialization_alias="all", description="The total count of alerts grouped into this incident")

class AlertUpdateIncidentReference(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    type_: Literal["incident_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class AlertUpdate(PermissiveModel):
    status: Literal["resolved", "triggered"] | None = None
    incident: AlertUpdateIncidentReference | None = None

class AlertV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})

class AutoPauseNotificationsParameters(PermissiveModel):
    """Defines how alerts on this service are automatically suspended for a period of time before triggering, when identified as likely being transient. Note that automatically pausing notifications is only available on certain plans."""
    enabled: bool | None = Field(False, description="Indicates whether alerts should be automatically suspended when identified as transient")
    timeout: Literal[0, 120, 180, 300, 600, 900] | None = Field(None, description="Indicates in seconds how long alerts should be suspended before triggering. To automatically select the recommended timeout for a service, set this value to `0`.")
    recommended_timeout: Literal[120, 180, 300, 600, 900] | None = Field(None, description="The recommended timeout setting for this service based on prior alert patterns.")

class AutomationActionsAbstractActionPutBody(PermissiveModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=1024)
    action_classification: Literal["diagnostic", "remediation"] | None = None
    action_type: Literal["script", "process_automation"] | None = None
    runner: str | None = Field(None, max_length=36)
    only_invocable_on_unresolved_incidents: bool | None = Field(False, description="If true, the action can only be invoked against an unresolved incident.")
    allow_invocation_manually: bool | None = Field(True, description="If true, the action can only be invoked manually by a user.")
    allow_invocation_from_event_orchestration: bool | None = Field(True, description="If true, the action can only be invoked automatically by an Event Orchestration.")
    map_to_all_services: bool | None = Field(False, description="If true, the action will be associated with every service.")

class AutomationActionsProcessAutomationJobActionDataReference(PermissiveModel):
    process_automation_job_id: str = Field(..., max_length=36)
    process_automation_job_arguments: str | None = Field(None, description="Arguments to pass to the Process Automation job. The maxLength value is specified in bytes.", max_length=1024)
    process_automation_node_filter: str | None = Field(None, description="Node filter for the Process Automation job. The maxLength value is specified in bytes. Filter syntax: https://docs.rundeck.com/docs/manual/11-node-filters.html#node-filter-syntax", max_length=1024)

class AutomationActionsProcessAutomationJobActionPutBody(PermissiveModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=1024)
    action_classification: Literal["diagnostic", "remediation"] | None = None
    action_type: Literal["script", "process_automation"] | None = None
    runner: str | None = Field(None, max_length=36)
    only_invocable_on_unresolved_incidents: bool | None = Field(False, description="If true, the action can only be invoked against an unresolved incident.")
    allow_invocation_manually: bool | None = Field(True, description="If true, the action can only be invoked manually by a user.")
    allow_invocation_from_event_orchestration: bool | None = Field(True, description="If true, the action can only be invoked automatically by an Event Orchestration.")
    map_to_all_services: bool | None = Field(False, description="If true, the action will be associated with every service.")
    action_data_reference: AutomationActionsProcessAutomationJobActionDataReference | None = None

class AutomationActionsRunnerRunbookBody(PermissiveModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=1024)
    runbook_base_uri: str | None = None
    runbook_api_key: str | None = Field(None, description="The API key to connect to the Runbook server with. If omitted, the previously stored value will remain unchanged", max_length=64)

class AutomationActionsRunnerSidecarBody(PermissiveModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=1024)

class AutomationActionsScriptActionDataReference(PermissiveModel):
    script: str = Field(..., description="Body of the script to be executed on the Runner. To execute it, the Runner will write the content of the property into a temp file, make the file executable and execute it. It is assumed that the Runner has a properly configured environment to run the script as an executable file. This behaviour can be altered by providing the `invocation_command` property. The maxLength value is specified in bytes.", max_length=16777215)
    invocation_command: str | None = Field(None, description="The command to executed a script with. With the body of the script written into a temp file, the Runner will execute the `<invocation_command> <temp_file>` command. The maxLength value is specified in bytes.", max_length=65535)

class AutomationActionsScriptActionPutBody(PermissiveModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=1024)
    action_classification: Literal["diagnostic", "remediation"] | None = None
    action_type: Literal["script", "process_automation"] | None = None
    runner: str | None = Field(None, max_length=36)
    only_invocable_on_unresolved_incidents: bool | None = Field(False, description="If true, the action can only be invoked against an unresolved incident.")
    allow_invocation_manually: bool | None = Field(True, description="If true, the action can only be invoked manually by a user.")
    allow_invocation_from_event_orchestration: bool | None = Field(True, description="If true, the action can only be invoked automatically by an Event Orchestration.")
    map_to_all_services: bool | None = Field(False, description="If true, the action will be associated with every service.")
    action_data_reference: AutomationActionsScriptActionDataReference | None = None

class CancelIncidentResponderRequestBodyResponderRequestTargetsItem(PermissiveModel):
    type_: Literal["user_reference", "escalation_policy_reference"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of target (either a user or an escalation policy)")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The id of the user or escalation policy")

class ChangeEventImagesItem(PermissiveModel):
    src: str | None = None
    href: str | None = None
    alt: str | None = None

class ChangeEventLinksItem(PermissiveModel):
    href: str | None = None
    text: str | None = None

class ChangeEventV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})

class ChangeEventV1ImagesItem(PermissiveModel):
    src: str | None = None
    href: str | None = None
    alt: str | None = None

class ChangeEventV1LinksItem(PermissiveModel):
    href: str | None = None
    text: str | None = None

class ChannelChangesetApplicationFieldsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None
    value: str | int | list[str] | None = None
    namespace: str | None = None
    old_value: str | None = None

class ChannelChangesetCustomerFieldsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None
    value: int | list[str] | None = None
    namespace: str | None = None
    old_value: str | None = None

class ChannelChangesetCustomerSchema(PermissiveModel):
    old_value: str | None = None

class ChannelChangeset(PermissiveModel):
    """Changeset present in CustomFieldsValueChange and FieldValueChange log entries."""
    customer_fields: list[ChannelChangesetCustomerFieldsItem] | None = Field(None, description="Customer Fields present in CustomFieldsValueChange and FieldValueChange log entries.")
    application_fields: list[ChannelChangesetApplicationFieldsItem] | None = Field(None, description="Application Fields present in CustomFieldsValueChange and FieldValueChange log entries.")
    custom_attributes: dict[str, str] | None = Field(None, description="Custom attributes for the changeset.")
    customer_schema: ChannelChangesetCustomerSchema | None = None

class ChannelV0(PermissiveModel):
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="Will be `nagios`")
    summary: str | None = Field(None, description="Same as `host`")
    host: str | None = Field(None, description="Nagios host")
    service: str | None = Field(None, description="Nagios service that created the event, if applicable")
    state: str | None = Field(None, description="State that caused the event")
    details: dict[str, Any] | None = Field(None, description="Additional details of the incident")

class ChannelV1(PermissiveModel):
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="Will be `api`")
    summary: str | None = Field(None, description="Same as `description`")
    service_key: str | None = Field(None, description="API service key")
    description: str | None = Field(None, description="Description of the event")
    incident_key: str | None = Field(None, description="Incident deduping string")
    details: dict[str, Any] | None = Field(None, description="Additional details of the incident")

class ChannelV2(PermissiveModel):
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="Will be `email`")
    summary: str | None = Field(None, description="Same as `subject`")
    to: str | None = Field(None, description="To address of the email")
    from_: str | None = Field(None, validation_alias="from", serialization_alias="from", description="From address of the email")
    subject: str | None = Field(None, description="Subject of the email")
    body: str | None = Field(None, description="Body of the email")
    body_content_type: str | None = Field(None, description="Content type of the email body. Will be `text/plain` or `text/html`")
    raw_url: str | None = Field(None, description="URL for raw text of email")
    html_url: str | None = Field(None, description="URL for html rendered version of the email. Only present if `content_type` is `text/html`")

class ChannelV3(PermissiveModel):
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="Will be `web_trigger`")
    summary: str | None = Field(None, description="Same as `subject`")
    subject: str | None = Field(None, description="Subject of the web trigger")
    details: str | None = Field(None, description="Details about the web trigger")

class ChannelV4(PermissiveModel):
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="Will be `website`")
    duration: int | None = Field(None, description="For `snooze` log entries, this is the number of seconds that the incident was snoozed for.")

class ConferenceBridge(PermissiveModel):
    conference_number: str | None = Field(None, description="The phone number of the conference call for the conference bridge. Phone numbers should be formatted like +1 415-555-1212,,,,1234#, where a comma (,) represents a one-second wait and pound (#) completes access code input.")
    conference_url: str | None = Field(None, description="An URL for the conference bridge. This could be a link to a web conference or Slack channel.", json_schema_extra={'format': 'url'})

class ContactMethod(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: Literal["email_contact_method", "phone_contact_method", "push_notification_contact_method", "sms_contact_method", "whatsapp_contact_method"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of contact method being created.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})
    label: str = Field(..., description="The label (e.g., \"Work\", \"Mobile\", etc.).")
    address: str = Field(..., description="The \"address\" to deliver to: email, phone number, etc., depending on the type.")

class ContactMethodV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})

class ContentBasedAlertGroupingConfiguration(PermissiveModel):
    """The configuration for Content Based Alert Grouping"""
    aggregate: Literal["all, any"] | None = Field(None, description="Whether Alerts should be grouped if `all` or `any` specified fields match. If `all` is selected, an exact match on every specified field name must occur for Alerts to be grouped. If `any` is selected, Alerts will be grouped when there is an exact match on at least one of the specified fields.")
    fields: list[str] | None = Field(None, description="An array of strings which represent the fields with which to group against. Depending on the aggregate, Alerts will group if some or all the fields match.")
    time_window: int | None = Field(None, description="The maximum amount of time allowed between Alerts. Any Alerts arriving greater than `time_window` seconds apart will not be grouped together. This is a rolling time window up to 24 hours and is counted from the most recently grouped alert. The window is extended every time a new alert is added to the group, up to 24 hours (24 hours only applies to single-service settings). To use the \"recommended_time_window,\" set the value to 0, otherwise the value must be between 300 <= time_window <= 3600 or 86400(i.e. 24 hours).", ge=300, le=86400)
    recommended_time_window: int | None = Field(None, description="In order to ensure your Service has the optimal grouping window, we use data science to calculate your Service's average Alert inter-arrival time. We encourage customer's to use this value, please set `time_window` to 0 to use the `recommended_time_window`.")

class Context(PermissiveModel):
    type_: Literal["link", "image"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of context being attached to the incident.")
    href: str | None = Field(None, description="The link's target url")
    src: str | None = Field(None, description="The image's source url")
    text: str | None = Field(None, description="The alternate display for an image")

class AlertBody(PermissiveModel):
    """A JSON object containing data describing the alert."""
    type_: Literal["alert_body"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the body.")
    contexts: list[Context] | None = Field(None, description="Contexts to be included with the body such as links to graphs or images.")
    details: dict[str, Any] | None = Field(None, description="An arbitrary JSON object or string containing any data explaining the nature of the alert.")

class AlertV1Body(PermissiveModel):
    """A JSON object containing data describing the alert."""
    type_: Literal["alert_body"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the body.")
    contexts: list[Context] | None = Field(None, description="Contexts to be included with the body such as links to graphs or images.")
    details: dict[str, Any] | None = Field(None, description="An arbitrary JSON object or string containing any data explaining the nature of the alert.")

class CreateCustomShiftsBodyCustomShiftsItemAssignmentsItemMember(PermissiveModel):
    """A member (user) assigned to a shift or rotation slot"""
    type_: Literal["user_member", "empty_member"] = Field(..., validation_alias="type", serialization_alias="type", description="`user_member` — a specific user is assigned.\n`empty_member` — the slot is intentionally unassigned.\n")
    user_id: str | None = Field(None, description="The ID of the user. Required when type is `user_member`.")

class CreateCustomShiftsBodyCustomShiftsItemAssignmentsItem(PermissiveModel):
    type_: Literal["shift_assignment"] = Field(..., validation_alias="type", serialization_alias="type")
    member: CreateCustomShiftsBodyCustomShiftsItemAssignmentsItemMember = Field(..., description="A member (user) assigned to a shift or rotation slot")

class CreateCustomShiftsBodyCustomShiftsItem(PermissiveModel):
    type_: Literal["custom_shift"] = Field(..., validation_alias="type", serialization_alias="type")
    start_time: str = Field(..., json_schema_extra={'format': 'date-time'})
    end_time: str = Field(..., json_schema_extra={'format': 'date-time'})
    assignments: list[CreateCustomShiftsBodyCustomShiftsItemAssignmentsItem] = Field(..., min_length=1, max_length=1)

class CreateEntityTypeByIdChangeTagsBodyAddItem(PermissiveModel):
    type_: Literal["tag", "tag_reference"] = Field(..., validation_alias="type", serialization_alias="type")
    label: str | None = Field(None, description="The label of the tag. Should be used when type is \"tag\".", max_length=191)
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The id of the tag. Should be used when type is \"tag_reference\".")

class CreateEntityTypeByIdChangeTagsBodyRemoveItem(PermissiveModel):
    type_: Literal["tag_reference"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The id of the tag")

class CreateOverridesBodyOverridesItemOverriddenMember(PermissiveModel):
    """A member (user) assigned to a shift or rotation slot"""
    type_: Literal["user_member", "empty_member"] = Field(..., validation_alias="type", serialization_alias="type", description="`user_member` — a specific user is assigned.\n`empty_member` — the slot is intentionally unassigned.\n")
    user_id: str | None = Field(None, description="The ID of the user. Required when type is `user_member`.")

class CreateOverridesBodyOverridesItemOverridingMember(PermissiveModel):
    """A member (user) assigned to a shift or rotation slot"""
    type_: Literal["user_member", "empty_member"] = Field(..., validation_alias="type", serialization_alias="type", description="`user_member` — a specific user is assigned.\n`empty_member` — the slot is intentionally unassigned.\n")
    user_id: str | None = Field(None, description="The ID of the user. Required when type is `user_member`.")

class CreateOverridesBodyOverridesItem(PermissiveModel):
    type_: Literal["override_shift"] = Field(..., validation_alias="type", serialization_alias="type")
    rotation_id: str | None = Field(None, description="Mutually exclusive with custom_shift_id")
    custom_shift_id: str | None = Field(None, description="Mutually exclusive with rotation_id")
    start_time: str = Field(..., json_schema_extra={'format': 'date-time'})
    end_time: str = Field(..., json_schema_extra={'format': 'date-time'})
    overridden_member: CreateOverridesBodyOverridesItemOverriddenMember = Field(..., description="A member (user) assigned to a shift or rotation slot")
    overriding_member: CreateOverridesBodyOverridesItemOverridingMember = Field(..., description="A member (user) assigned to a shift or rotation slot")

class CreateScheduleV3BodyScheduleTeamsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    type_: Literal["team_reference"] = Field(..., validation_alias="type", serialization_alias="type")

class CreateServiceDependencyBodyRelationshipsItemDependentService(PermissiveModel):
    """The reference to the service that is dependent on the supporting service."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateServiceDependencyBodyRelationshipsItemSupportingService(PermissiveModel):
    """The reference to the service that supports the dependent service."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateServiceDependencyBodyRelationshipsItem(PermissiveModel):
    supporting_service: CreateServiceDependencyBodyRelationshipsItemSupportingService | None = Field(None, description="The reference to the service that supports the dependent service.")
    dependent_service: CreateServiceDependencyBodyRelationshipsItemDependentService | None = Field(None, description="The reference to the service that is dependent on the supporting service.")

class CreateStatusPagePostUpdateBodyPostUpdateImpactedServicesItemImpact(PermissiveModel):
    """Status Page Impact"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="An unique identifier within Status Page scope that defines a Status Page Impact entry.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the object returned by the API - in this case, a Status Page Impact.")

class CreateStatusPagePostUpdateBodyPostUpdateImpactedServicesItemService(PermissiveModel):
    """Status Page Service"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="An unique identifier within Status Page scope that defines a Service entry.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the object returned by the API - in this case, a Status Page Service.")

class CreateStatusPagePostUpdateBodyPostUpdateImpactedServicesItem(PermissiveModel):
    """Status Page Post Update Impact"""
    service: CreateStatusPagePostUpdateBodyPostUpdateImpactedServicesItemService | None = Field(None, description="Status Page Service")
    impact: CreateStatusPagePostUpdateBodyPostUpdateImpactedServicesItemImpact | None = Field(None, description="Status Page Impact")

class CreateWorkflowIntegrationConnectionBodyAppsItem(PermissiveModel):
    app_id: str | None = Field(None, description="The ID of the app")
    type_: Literal["pd_app_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateWorkflowIntegrationConnectionBodyTeamsItem(PermissiveModel):
    team_id: str | None = Field(None, description="The ID of the team")
    type_: Literal["team_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class CustomFieldsEditableFieldOptionDataV0(PermissiveModel):
    data_type: Literal["string"] = Field(..., description="The kind of data represented by this option. Must match the Field's `data_type`.")
    value: str = Field(..., max_length=200)

class CustomFieldsEditableFieldOption(PermissiveModel):
    data: Annotated[CustomFieldsEditableFieldOptionDataV0, Field(discriminator="data_type")] | None = None
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the resource.")
    type_: Literal["field_option"] = Field(..., validation_alias="type", serialization_alias="type")
    updated_at: str = Field(..., description="The date/time the object was last updated.", json_schema_extra={'format': 'date-time'})
    created_at: str = Field(..., description="The date/time the object was created at.", json_schema_extra={'format': 'date-time'})

class CustomFieldsEditableFieldValueV0ValueV0(PermissiveModel):
    value: bool | None = None

class CustomFieldsEditableFieldValueV0ValueV1(PermissiveModel):
    value: float | None = None

class CustomFieldsEditableFieldValueV0ValueV2(PermissiveModel):
    value: int | None = None

class CustomFieldsEditableFieldValueV0ValueV3(PermissiveModel):
    value: str | None | list[str] | None = None

class CustomFieldsEditableFieldValueV0ValueV4(PermissiveModel):
    value: str | None = Field(None, json_schema_extra={'format': 'date-time'})

class CustomFieldsEditableFieldValueV0ValueV5(PermissiveModel):
    value: str | None = Field(None, max_length=200, json_schema_extra={'format': 'uri'})

class CustomFieldsEditableFieldValueV0(PermissiveModel):
    name: str | None = None
    value: CustomFieldsEditableFieldValueV0ValueV0 | CustomFieldsEditableFieldValueV0ValueV1 | CustomFieldsEditableFieldValueV0ValueV2 | CustomFieldsEditableFieldValueV0ValueV3 | CustomFieldsEditableFieldValueV0ValueV4 | CustomFieldsEditableFieldValueV0ValueV5 | None = None

class CustomFieldsEditableFieldValueV1ValueV0(PermissiveModel):
    value: bool | None = None

class CustomFieldsEditableFieldValueV1ValueV1(PermissiveModel):
    value: float | None = None

class CustomFieldsEditableFieldValueV1ValueV2(PermissiveModel):
    value: int | None = None

class CustomFieldsEditableFieldValueV1ValueV3(PermissiveModel):
    value: str | None | list[str] | None = None

class CustomFieldsEditableFieldValueV1ValueV4(PermissiveModel):
    value: str | None = Field(None, json_schema_extra={'format': 'date-time'})

class CustomFieldsEditableFieldValueV1ValueV5(PermissiveModel):
    value: str | None = Field(None, max_length=200, json_schema_extra={'format': 'uri'})

class CustomFieldsEditableFieldValueV1(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the Field.")
    value: CustomFieldsEditableFieldValueV1ValueV0 | CustomFieldsEditableFieldValueV1ValueV1 | CustomFieldsEditableFieldValueV1ValueV2 | CustomFieldsEditableFieldValueV1ValueV3 | CustomFieldsEditableFieldValueV1ValueV4 | CustomFieldsEditableFieldValueV1ValueV5 | None = None

class CustomFieldsEditableFieldValue(PermissiveModel):
    custom_fields_editable_field_value: CustomFieldsEditableFieldValueV0 | CustomFieldsEditableFieldValueV1

class CustomFieldsFieldOptionDataV0(PermissiveModel):
    data_type: Literal["string"] = Field(..., description="The kind of data represented by this option. Must match the Field's `data_type`.")
    value: str = Field(..., max_length=200)

class CustomFieldsFieldOption(PermissiveModel):
    data: Annotated[CustomFieldsFieldOptionDataV0, Field(discriminator="data_type")]
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the resource.")
    type_: Literal["field_option"] = Field(..., validation_alias="type", serialization_alias="type")
    updated_at: str = Field(..., description="The date/time the object was last updated.", json_schema_extra={'format': 'date-time'})
    created_at: str = Field(..., description="The date/time the object was created at.", json_schema_extra={'format': 'date-time'})

class DeleteServiceDependencyBodyRelationshipsItemDependentService(PermissiveModel):
    """The reference to the service that is dependent on the supporting service."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type")

class DeleteServiceDependencyBodyRelationshipsItemSupportingService(PermissiveModel):
    """The reference to the service that supports the dependent service."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type")

class DeleteServiceDependencyBodyRelationshipsItem(PermissiveModel):
    supporting_service: DeleteServiceDependencyBodyRelationshipsItemSupportingService | None = Field(None, description="The reference to the service that supports the dependent service.")
    dependent_service: DeleteServiceDependencyBodyRelationshipsItemDependentService | None = Field(None, description="The reference to the service that is dependent on the supporting service.")

class EditableTemplateTemplatedFields(PermissiveModel):
    email_subject: str | None = Field(None, description="The subject of the e-mail")
    email_body: str | None = Field(None, description="The HTML body of the e-mail message")
    message: str | None = Field(None, description="The short-message of the template (SMS, Push notification, Slack,\netc)")

class EditableTemplate(PermissiveModel):
    template_type: Literal["status_update"] | None = Field(None, description="The type of template (`status_update` is the only supported template at this time)")
    name: str | None = Field(None, description="The name of the template")
    description: str | None = Field(None, description="Description of the template")
    templated_fields: EditableTemplateTemplatedFields | None = None

class EmailContactMethod(PermissiveModel):
    """The Email Contact Method of the User."""
    type_: Literal["email_contact_method"] | None = Field(None, validation_alias="type", serialization_alias="type")
    send_short_email: bool | None = Field(False, description="Send an abbreviated email message instead of the standard email output. Useful for email-to-SMS gateways and email based pagers.")

class EmailParserValueExtractorsItem(PermissiveModel):
    type_: Literal["entire", "regex", "between"] = Field(..., validation_alias="type", serialization_alias="type")
    part: Literal["body", "subject", "from_addresses"]
    value_name: str = Field(..., description="The field name to set in the Incident object. Exactly one must use the `value_name` of `incident_key`", min_length=1)
    regex: str | None = None
    starts_after: str | None = None
    ends_with: str | None = None

class EscalationPolicyV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})

class ExtensionV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})

class FlexibleTimeWindowIntelligentAlertGroupingConfig(PermissiveModel):
    """The configuration for Intelligent Alert Grouping. Note that this configuration is only available for certain plans."""
    time_window: int | None = Field(None, description="The maximum amount of time allowed between Alerts. Any Alerts arriving greater than `time_window` seconds apart will not be grouped together. This is a rolling time window and is counted from the most recently grouped alert. The window is extended every time a new alert is added to the group, up to 24 hours. To use the \"recommended_time_window,\" set the value to 0, otherwise the value must be between 300 and 3600.", ge=300, le=3600)
    recommended_time_window: int | None = Field(None, description="In order to ensure your Service has the optimal grouping window, we use data science to calculate your Service`s average Alert inter-arrival time. We encourage customer`s to use this value, please set `time_window` to 0 to use the `recommended_time_window`.")

class ImpactAdditionalFieldsHighestImpactingPriority(PermissiveModel):
    """Priority information for the highest priority level that is affecting the impacted object."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    order: int | None = None

class ImpactAdditionalFields(PermissiveModel):
    highest_impacting_priority: ImpactAdditionalFieldsHighestImpactingPriority | None = Field(None, description="Priority information for the highest priority level that is affecting the impacted object.")

class Impact(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None
    type_: Literal["business_service"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The kind of object that has been impacted")
    status: Literal["impacted", "not_impacted"] | None = Field(None, description="The current impact status of the object")
    additional_fields: ImpactAdditionalFields | None = None

class IncidentAction(PermissiveModel):
    """An incident action is a pending change to an incident that will automatically happen at some future time."""
    type_: Literal["unacknowledge", "escalate", "resolve", "urgency_change"] = Field(..., validation_alias="type", serialization_alias="type")
    at: str = Field(..., json_schema_extra={'format': 'date-time'})
    to: Literal["high"] | None = Field(None, description="The urgency that the incident will change to. This field is only present when the type is `urgency_change`.")

class IncidentAlertGrouping(PermissiveModel):
    """Describes the alert grouping state of this incident. Will be null if the incident has no alerts."""
    grouping_type: Literal["basic", "advanced", "rules"] | None = None
    started_at: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    ended_at: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    alert_grouping_active: bool | None = None

class IncidentBody(PermissiveModel):
    details: dict[str, Any] | None = Field(None, description="Additional incident details.")

class IncidentIncidentType(PermissiveModel):
    """The incident type of the incident."""
    name: str | None = Field(None, description="The name of the Incident Type.")

class IncidentTypeReference(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = Field(None, description="The name of the Incident Type.")

class IncidentUrgencyType(PermissiveModel):
    type_: Literal["constant", "use_support_hours"] | None = Field('constant', validation_alias="type", serialization_alias="type", description="The type of incident urgency: whether it's constant, or it's dependent on the support hours.")
    urgency: Literal["low", "high", "severity_based"] | None = Field('high', description="The incidents' urgency, if type is constant.")

class IncidentUrgencyRule(PermissiveModel):
    type_: Literal["constant", "use_support_hours"] | None = Field('constant', validation_alias="type", serialization_alias="type", description="The type of incident urgency: whether it's constant, or it's dependent on the support hours.")
    urgency: Literal["low", "high", "severity_based"] | None = Field('high', description="The incidents' urgency, if type is constant.")
    during_support_hours: IncidentUrgencyType | None = None
    outside_support_hours: IncidentUrgencyType | None = None

class IncidentV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})

class IncidentV1AlertGrouping(PermissiveModel):
    """Describes the alert grouping state of this incident. Will be null if the incident has no alerts."""
    grouping_type: Literal["basic", "advanced", "rules"] | None = None
    started_at: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    ended_at: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    alert_grouping_active: bool | None = None

class IncidentV1IncidentType(PermissiveModel):
    """The incident type of the incident."""
    name: str | None = Field(None, description="The name of the Incident Type.")

class IntegrationEmailFiltersItem(PermissiveModel):
    subject_mode: Literal["match", "no-match", "always"]
    subject_regex: str | None = Field(None, description="Specify if subject_mode is set to match or no-match")
    body_mode: Literal["match", "no-match", "always"]
    body_regex: str | None = Field(None, description="Specify if body_mode is set to match or no-match")
    from_email_mode: Literal["match", "no-match", "always"]
    from_email_regex: str | None = Field(None, description="Specify if from_email_mode is set to match or no-match")

class IntegrationV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})

class IntegrationV1EmailFiltersItem(PermissiveModel):
    subject_mode: Literal["match", "no-match", "always"]
    subject_regex: str | None = Field(None, description="Specify if subject_mode is set to match or no-match")
    body_mode: Literal["match", "no-match", "always"]
    body_regex: str | None = Field(None, description="Specify if body_mode is set to match or no-match")
    from_email_mode: Literal["match", "no-match", "always"]
    from_email_regex: str | None = Field(None, description="Specify if from_email_mode is set to match or no-match")

class LogEntryEventDetails(PermissiveModel):
    description: str | None = Field(None, description="Additional details about the event.")

class LogEntryV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})

class LogEntryV1EventDetails(PermissiveModel):
    description: str | None = Field(None, description="Additional details about the event.")

class MaintenanceWindowV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})

class NotificationRuleV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})

class NotificationSubscribable(PermissiveModel):
    """A reference of a subscribable entity."""
    subscribable_id: str | None = Field(None, description="The ID of the entity to subscribe to")
    subscribable_type: Literal["incident", "business_service"] | None = Field(None, description="The type of the entity being subscribed to")

class NotificationSubscriber(PermissiveModel):
    """A reference of a subscriber entity."""
    subscriber_id: str | None = Field(None, description="The ID of the entity being subscribed")
    subscriber_type: Literal["user", "team"] | None = Field(None, description="The type of the entity being subscribed")

class OrchestrationCacheVariableExternalDataConfiguration(PermissiveModel):
    type_: Literal["external_data"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The Cache Variable value will be set via a PUT API request to a dedicated endpoint that is made available after the creation of the cache variable.\n")
    data_type: Literal["string", "number", "boolean"] | None = Field(None, description="The type of data that will eventually be set for this cache variable via an API request.\n")
    ttl_seconds: int | None = Field(None, description="The time to live (in seconds) for how long data sent to endpoint is persisted. After the TTL passes the data is deleted.\n")

class OrchestrationCacheVariableExternalDataCreatedBy(PermissiveModel):
    """Reference to the user that created the object."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="The API show URL at which the object is accessible", json_schema_extra={'format': 'url'})

class OrchestrationCacheVariableExternalDataUpdatedBy(PermissiveModel):
    """Reference to the user that last updated the object."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="The API show URL at which the object is accessible", json_schema_extra={'format': 'url'})

class OrchestrationCacheVariableExternalData(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str = Field(..., description="The name of the Cache Variable")
    disabled: bool | None = Field(None, description="Indicates whether the Cache Variable is disabled and would therefore not be evaluated.")
    created_at: str | None = Field(None, description="The date/time the object was created.", json_schema_extra={'format': 'date-time'})
    created_by: OrchestrationCacheVariableExternalDataCreatedBy | None = Field(None, description="Reference to the user that created the object.")
    updated_at: str | None = Field(None, description="The date/time the object was last updated.", json_schema_extra={'format': 'date-time'})
    updated_by: OrchestrationCacheVariableExternalDataUpdatedBy | None = Field(None, description="Reference to the user that last updated the object.")
    configuration: OrchestrationCacheVariableExternalDataConfiguration
    data_endpoint: str | None = Field(None, description="The endpoint that can be used to manage the data for an `external_data` type cache variable", json_schema_extra={'format': 'uri'})

class OrchestrationCacheVariableExternalDataV0CreatedBy(PermissiveModel):
    """Reference to the user that created the object."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="The API show URL at which the object is accessible", json_schema_extra={'format': 'url'})

class OrchestrationCacheVariableExternalDataV0UpdatedBy(PermissiveModel):
    """Reference to the user that last updated the object."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="The API show URL at which the object is accessible", json_schema_extra={'format': 'url'})

class OrchestrationCacheVariableExternalDataV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str = Field(..., description="The name of the Cache Variable")
    disabled: bool | None = Field(None, description="Indicates whether the Cache Variable is disabled and would therefore not be evaluated.")
    created_at: str | None = Field(None, description="The date/time the object was created.", json_schema_extra={'format': 'date-time'})
    created_by: OrchestrationCacheVariableExternalDataV0CreatedBy | None = Field(None, description="Reference to the user that created the object.")
    updated_at: str | None = Field(None, description="The date/time the object was last updated.", json_schema_extra={'format': 'date-time'})
    updated_by: OrchestrationCacheVariableExternalDataV0UpdatedBy | None = Field(None, description="Reference to the user that last updated the object.")

class OrchestrationCacheVariableExternalDataV1Configuration(PermissiveModel):
    type_: Literal["external_data"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The Cache Variable value will be set via a PUT API request to a dedicated endpoint that is made available after the creation of the cache variable.\n")
    data_type: Literal["string", "number", "boolean"] | None = Field(None, description="The type of data that will eventually be set for this cache variable via an API request.\n")
    ttl_seconds: int | None = Field(None, description="The time to live (in seconds) for how long data sent to endpoint is persisted. After the TTL passes the data is deleted.\n")

class OrchestrationCacheVariableRecentValueConditionsItem(PermissiveModel):
    expression: str | None = Field(None, description="A PCL condition string.\n\nNote: The `trigger_count` and `resetting_trigger_count` operators are unsupported for Cache Variables\n")

class OrchestrationCacheVariableRecentValueConfiguration(PermissiveModel):
    type_: Literal["recent_value"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Cache Variable will be set to the most recent value seen, based on the source event field and the extraction regex specified\n")
    source: str | None = Field(None, description="The path to the event field where the regex will be applied to extract a value.")
    regex: str | None = Field(None, description="A RE2 regular expression. If it contains one or more capture groups, their values will be extracted and appended together. If it contains no capture groups, the whole match is used.\n")

class OrchestrationCacheVariableRecentValueCreatedBy(PermissiveModel):
    """Reference to the user that created the object."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="The API show URL at which the object is accessible", json_schema_extra={'format': 'url'})

class OrchestrationCacheVariableRecentValueUpdatedBy(PermissiveModel):
    """Reference to the user that last updated the object."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="The API show URL at which the object is accessible", json_schema_extra={'format': 'url'})

class OrchestrationCacheVariableRecentValue(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str = Field(..., description="The name of the Cache Variable")
    disabled: bool | None = Field(None, description="Indicates whether the Cache Variable is disabled and would therefore not be evaluated.")
    created_at: str | None = Field(None, description="The date/time the object was created.", json_schema_extra={'format': 'date-time'})
    created_by: OrchestrationCacheVariableRecentValueCreatedBy | None = Field(None, description="Reference to the user that created the object.")
    updated_at: str | None = Field(None, description="The date/time the object was last updated.", json_schema_extra={'format': 'date-time'})
    updated_by: OrchestrationCacheVariableRecentValueUpdatedBy | None = Field(None, description="Reference to the user that last updated the object.")
    configuration: OrchestrationCacheVariableRecentValueConfiguration
    conditions: list[OrchestrationCacheVariableRecentValueConditionsItem] | None = Field(None, description="Each of these conditions is evaluated to check if an event matches this rule.\nThe rule is considered a match if **any** of these conditions match.\n")

class OrchestrationCacheVariableRecentValueV0CreatedBy(PermissiveModel):
    """Reference to the user that created the object."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="The API show URL at which the object is accessible", json_schema_extra={'format': 'url'})

class OrchestrationCacheVariableRecentValueV0UpdatedBy(PermissiveModel):
    """Reference to the user that last updated the object."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="The API show URL at which the object is accessible", json_schema_extra={'format': 'url'})

class OrchestrationCacheVariableRecentValueV1ConditionsItem(PermissiveModel):
    expression: str | None = Field(None, description="A PCL condition string.\n\nNote: The `trigger_count` and `resetting_trigger_count` operators are unsupported for Cache Variables\n")

class OrchestrationCacheVariableRecentValueV1Configuration(PermissiveModel):
    type_: Literal["recent_value"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Cache Variable will be set to the most recent value seen, based on the source event field and the extraction regex specified\n")
    source: str | None = Field(None, description="The path to the event field where the regex will be applied to extract a value.")
    regex: str | None = Field(None, description="A RE2 regular expression. If it contains one or more capture groups, their values will be extracted and appended together. If it contains no capture groups, the whole match is used.\n")

class OrchestrationCacheVariableTriggerEventCountConditionsItem(PermissiveModel):
    expression: str | None = Field(None, description="A PCL condition string.\n\nNote: The `trigger_count` and `resetting_trigger_count` operators are unsupported for Cache Variables\n")

class OrchestrationCacheVariableTriggerEventCountConfiguration(PermissiveModel):
    type_: Literal["trigger_event_count"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Cache Variable will be set to the number of trigger events that have been seen within the TTL range\n")
    ttl_seconds: int | None = Field(None, description="The time to live (in seconds) for how long to count trigger events before resetting back to 0.\n")

class OrchestrationCacheVariableTriggerEventCountCreatedBy(PermissiveModel):
    """Reference to the user that created the object."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="The API show URL at which the object is accessible", json_schema_extra={'format': 'url'})

class OrchestrationCacheVariableTriggerEventCountUpdatedBy(PermissiveModel):
    """Reference to the user that last updated the object."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="The API show URL at which the object is accessible", json_schema_extra={'format': 'url'})

class OrchestrationCacheVariableTriggerEventCount(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str = Field(..., description="The name of the Cache Variable")
    disabled: bool | None = Field(None, description="Indicates whether the Cache Variable is disabled and would therefore not be evaluated.")
    created_at: str | None = Field(None, description="The date/time the object was created.", json_schema_extra={'format': 'date-time'})
    created_by: OrchestrationCacheVariableTriggerEventCountCreatedBy | None = Field(None, description="Reference to the user that created the object.")
    updated_at: str | None = Field(None, description="The date/time the object was last updated.", json_schema_extra={'format': 'date-time'})
    updated_by: OrchestrationCacheVariableTriggerEventCountUpdatedBy | None = Field(None, description="Reference to the user that last updated the object.")
    configuration: OrchestrationCacheVariableTriggerEventCountConfiguration
    conditions: list[OrchestrationCacheVariableTriggerEventCountConditionsItem] | None = Field(None, description="Each of these conditions is evaluated to check if an event matches this rule.\nThe rule is considered a match if **any** of these conditions match.\n")

class OrchestrationCacheVariableTriggerEventCountV0CreatedBy(PermissiveModel):
    """Reference to the user that created the object."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="The API show URL at which the object is accessible", json_schema_extra={'format': 'url'})

class OrchestrationCacheVariableTriggerEventCountV0UpdatedBy(PermissiveModel):
    """Reference to the user that last updated the object."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="The API show URL at which the object is accessible", json_schema_extra={'format': 'url'})

class OrchestrationCacheVariableTriggerEventCountV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str = Field(..., description="The name of the Cache Variable")
    disabled: bool | None = Field(None, description="Indicates whether the Cache Variable is disabled and would therefore not be evaluated.")
    created_at: str | None = Field(None, description="The date/time the object was created.", json_schema_extra={'format': 'date-time'})
    created_by: OrchestrationCacheVariableTriggerEventCountV0CreatedBy | None = Field(None, description="Reference to the user that created the object.")
    updated_at: str | None = Field(None, description="The date/time the object was last updated.", json_schema_extra={'format': 'date-time'})
    updated_by: OrchestrationCacheVariableTriggerEventCountV0UpdatedBy | None = Field(None, description="Reference to the user that last updated the object.")

class OrchestrationCacheVariableTriggerEventCountV1ConditionsItem(PermissiveModel):
    expression: str | None = Field(None, description="A PCL condition string.\n\nNote: The `trigger_count` and `resetting_trigger_count` operators are unsupported for Cache Variables\n")

class OrchestrationCacheVariableTriggerEventCountV1Configuration(PermissiveModel):
    type_: Literal["trigger_event_count"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Cache Variable will be set to the number of trigger events that have been seen within the TTL range\n")
    ttl_seconds: int | None = Field(None, description="The time to live (in seconds) for how long to count trigger events before resetting back to 0.\n")

class OrchestrationCreatedBy(PermissiveModel):
    """Reference to the user that has created the Orchestration."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object")
    self: str | None = Field(None, description="The API show URL at which the object is accessible", json_schema_extra={'format': 'url'})

class OrchestrationIntegrationParameters(PermissiveModel):
    routing_key: str | None = Field(None, description="Routing Key used to send Events to this Orchestration")
    type_: str | None = Field('global', validation_alias="type", serialization_alias="type")

class OrchestrationIntegration(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="ID of the Integration.")
    label: str | None = Field(None, description="Name of the Integration.")
    parameters: OrchestrationIntegrationParameters | None = None

class OrchestrationTeam(PermissiveModel):
    """Reference to the team that owns the Orchestration. If none is specified, only admins have access."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object")
    self: str | None = Field(None, description="The API show URL at which the object is accessible", json_schema_extra={'format': 'url'})

class OrchestrationUpdatedBy(PermissiveModel):
    """Reference to the user that has updated the Orchestration last."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object")
    self: str | None = Field(None, description="The API show URL at which the object is accessible", json_schema_extra={'format': 'url'})

class Orchestration(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="ID of the Orchestration.")
    self: str | None = Field(None, description="The API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    name: str | None = Field(None, description="Name of the Orchestration.")
    description: str | None = Field(None, description="A description of this Orchestration's purpose.")
    team: OrchestrationTeam | None = Field(None, description="Reference to the team that owns the Orchestration. If none is specified, only admins have access.")
    integrations: list[OrchestrationIntegration] | None = None
    routes: int | None = Field(None, description="Number of different Service Orchestration being routed to")
    created_at: str | None = Field(None, description="The date the Orchestration was created at.", json_schema_extra={'format': 'date-time'})
    created_by: OrchestrationCreatedBy | None = Field(None, description="Reference to the user that has created the Orchestration.")
    updated_at: str | None = Field(None, description="The date the Orchestration was last updated.", json_schema_extra={'format': 'date-time'})
    updated_by: OrchestrationUpdatedBy | None = Field(None, description="Reference to the user that has updated the Orchestration last.")
    version: str | None = Field(None, description="Version of the Orchestration.")

class PhoneContactMethod(PermissiveModel):
    """The Phone Contact Method of the User, used for Voice or SMS."""
    type_: Literal["phone_contact_method", "sms_contact_method"] | None = Field(None, validation_alias="type", serialization_alias="type")
    country_code: int = Field(..., description="The 1-to-3 digit country calling code.", ge=1, le=1999)
    enabled: bool | None = Field(None, description="If true, this phone is capable of receiving SMS messages.")
    blacklisted: bool | None = Field(None, description="If true, this phone has been blacklisted by PagerDuty and no messages will be sent to it.")

class Priority(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})
    name: str | None = Field(None, description="The user-provided short name of the priority.")
    description: str | None = Field(None, description="The user-provided description of the priority.")

class PriorityV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})

class PushContactMethodSound(PermissiveModel):
    type_: Literal["alert_high_urgency", "alert_low_urgency"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of sound.")
    file_: str | None = Field(None, validation_alias="file", serialization_alias="file", description="The sound file name.")

class PushContactMethod(PermissiveModel):
    """The Push Contact Method of the User."""
    type_: Literal["push_notification_contact_method"] | None = Field(None, validation_alias="type", serialization_alias="type")
    device_type: Literal["android", "ios"] = Field(..., description="The type of device.")
    sounds: list[PushContactMethodSound] | None = None
    created_at: str | None = Field(None, description="Time at which the contact method was created.", json_schema_extra={'format': 'date-time'})
    blacklisted: bool | None = Field(None, description="If true, this phone has been blacklisted by PagerDuty and no messages will be sent to it.")

class Reference(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})

class AcknowledgerReference(PermissiveModel):
    type_: Literal["user_reference", "service_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class AddonReference(PermissiveModel):
    src: str | None = Field(None, description="The URL source of the Addon", json_schema_extra={'format': 'url'})
    name: str | None = Field(None, description="The user entered name of the Addon.")
    type_: Literal["full_page_addon_reference", "incident_show_addon_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class AgentReference(PermissiveModel):
    type_: Literal["user_reference", "service_reference", "integration_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class ContactMethodReference(PermissiveModel):
    type_: Literal["email_contact_method_reference", "phone_contact_method_reference", "push_notification_contact_method_reference", "sms_contact_method_reference", "whatsapp_contact_method_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class EscalationPolicyReference(PermissiveModel):
    type_: Literal["escalation_policy_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class EscalationTargetReference(PermissiveModel):
    type_: Literal["user", "schedule", "user_reference", "schedule_reference", "schedule_v3_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class EscalationRule(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    escalation_delay_in_minutes: int = Field(..., description="The number of minutes before an unacknowledged incident escalates away from this rule.")
    targets: list[EscalationTargetReference] = Field(..., description="The targets an incident should be assigned to upon reaching this rule.", min_length=1, max_length=10)
    escalation_rule_assignment_strategy: Literal["round_robin", "assign_to_everyone"] | None = Field(None, description="The strategy used to assign the escalation rule to an incident.")

class ExtensionSchemaReference(PermissiveModel):
    type_: Literal["extension_schema_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class IncidentReference(PermissiveModel):
    type_: Literal["incident_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class IntegrationReference(PermissiveModel):
    type_: Literal["aws_cloudwatch_inbound_integration_reference", "cloudkick_inbound_integration_reference", "event_transformer_api_inbound_integration_reference", "generic_email_inbound_integration_reference", "generic_events_api_inbound_integration_reference", "keynote_inbound_integration_reference", "nagios_inbound_integration_reference", "pingdom_inbound_integration_reference", "sql_monitor_inbound_integration_reference", "events_api_v2_inbound_integration_reference", "inbound_integration_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class LicenseReference(PermissiveModel):
    type_: Literal["license_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class LogEntryReference(PermissiveModel):
    type_: Literal["acknowledge_log_entry_reference", "annotate_log_entry_reference", "assign_log_entry_reference", "escalate_log_entry_reference", "exhaust_escalation_path_log_entry_reference", "notify_log_entry_reference", "reach_trigger_limit_log_entry_reference", "repeat_escalation_path_log_entry_reference", "resolve_log_entry_reference", "snooze_log_entry_reference", "trigger_log_entry_reference", "unacknowledge_log_entry_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class NotificationRule(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: Literal["assignment_notification_rule"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of object being created.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})
    start_delay_in_minutes: int = Field(..., description="The delay before firing the rule, in minutes.", ge=0)
    contact_method: ContactMethodReference
    urgency: Literal["high", "low"] = Field(..., description="Which incident urgency this rule is used for. Account must have the `urgencies` ability to have a low urgency notification rule.")

class NotificationRuleReference(PermissiveModel):
    type_: Literal["assignment_notification_rule_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class OutboundIntegrationReference(PermissiveModel):
    type_: Literal["outbound_integration_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PriorityReference(PermissiveModel):
    type_: Literal["priority_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class ReferenceV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})

class ResolveReason(PermissiveModel):
    type_: Literal["merge_resolve_reason"] | None = Field('merge_resolve_reason', validation_alias="type", serialization_alias="type", description="The reason the incident was resolved. The only reason currently supported is merge.")
    incident: IncidentReference | None = None

class Restriction(PermissiveModel):
    type_: Literal["daily_restriction", "weekly_restriction"] = Field(..., validation_alias="type", serialization_alias="type", description="Specify the types of `restriction`.")
    duration_seconds: int = Field(..., description="The duration of the restriction in seconds.")
    start_time_of_day: str = Field(..., description="The start time in HH:mm:ss format.", json_schema_extra={'format': 'partial-time'})
    start_day_of_week: int | None = Field(None, description="Only required for use with a `weekly_restriction` restriction type. The first day of the weekly rotation schedule as [ISO 8601 day](https://en.wikipedia.org/wiki/ISO_week_date) (1 is Monday, etc.)", ge=1, le=7)

class ScheduleNextOncallForUser(PermissiveModel):
    start: str | None = Field(None, description="The start date for the User shift")
    end: str | None = Field(None, description="The end date for the User shift")
    user: Reference | None = None

class ScheduleV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})

class ScheduleV1NextOncallForUser(PermissiveModel):
    start: str | None = Field(None, description="The start date for the User shift")
    end: str | None = Field(None, description="The end date for the User shift")
    user: Reference | None = None

class ScheduledActionAt(PermissiveModel):
    """Represents when scheduled action will occur."""
    type_: Literal["named_time"] = Field(..., validation_alias="type", serialization_alias="type", description="Must be set to named_time.")
    name: Literal["support_hours_start", "support_hours_end"] = Field(..., description="Designates either the start or the end of support hours.")

class ScheduledAction(PermissiveModel):
    type_: Literal["urgency_change"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of schedule action. Must be set to urgency_change.")
    at: ScheduledActionAt = Field(..., description="Represents when scheduled action will occur.")
    to_urgency: Literal["high"] = Field(..., description="Urgency level. Must be set to high.")

class ServiceAlertGroupingParametersV1(PermissiveModel):
    """When a service uses alert grouping configuration that is unsupported via the services api, and can only be configured via the [Alert Grouping Settings API](https://developer.pagerduty.com/api-reference/587edbc8ff416-create-an-alert-grouping-setting). The reference object includes the new location details for the service's Alert Grouping Setting. When an `alert_grouping_settings_reference` is included in a create or update request it will be ignored and no changes are applied to the service."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="id of the related alert grouping setting")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="type of reference eg. alert_grouping_setting_reference")
    summary: str | None = Field(None, description="an explanation of this reference")
    self: str | None = Field(None, description="link to api endpoint for this setting")
    html_url: str | None = Field(None, description="link to the ui page to edit the setting")

class ServiceCustomFieldsFieldValueUpdateModelV0ValueV0(PermissiveModel):
    value: bool | None = None

class ServiceCustomFieldsFieldValueUpdateModelV0ValueV1(PermissiveModel):
    value: str | None = Field(None, json_schema_extra={'format': 'date-time'})

class ServiceCustomFieldsFieldValueUpdateModelV0ValueV2(PermissiveModel):
    value: float | None = None

class ServiceCustomFieldsFieldValueUpdateModelV0ValueV3(PermissiveModel):
    value: int | None = None

class ServiceCustomFieldsFieldValueUpdateModelV0ValueV4(PermissiveModel):
    value: str | None | list[str] | None = None

class ServiceCustomFieldsFieldValueUpdateModelV0ValueV5(PermissiveModel):
    value: str | None = Field(None, max_length=200, json_schema_extra={'format': 'uri'})

class ServiceCustomFieldsFieldValueUpdateModelV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    value: ServiceCustomFieldsFieldValueUpdateModelV0ValueV0 | ServiceCustomFieldsFieldValueUpdateModelV0ValueV1 | ServiceCustomFieldsFieldValueUpdateModelV0ValueV2 | ServiceCustomFieldsFieldValueUpdateModelV0ValueV3 | ServiceCustomFieldsFieldValueUpdateModelV0ValueV4 | ServiceCustomFieldsFieldValueUpdateModelV0ValueV5

class ServiceCustomFieldsFieldValueUpdateModelV1ValueV0(PermissiveModel):
    value: bool | None = None

class ServiceCustomFieldsFieldValueUpdateModelV1ValueV1(PermissiveModel):
    value: str | None = Field(None, json_schema_extra={'format': 'date-time'})

class ServiceCustomFieldsFieldValueUpdateModelV1ValueV2(PermissiveModel):
    value: float | None = None

class ServiceCustomFieldsFieldValueUpdateModelV1ValueV3(PermissiveModel):
    value: int | None = None

class ServiceCustomFieldsFieldValueUpdateModelV1ValueV4(PermissiveModel):
    value: str | None | list[str] | None = None

class ServiceCustomFieldsFieldValueUpdateModelV1ValueV5(PermissiveModel):
    value: str | None = Field(None, max_length=200, json_schema_extra={'format': 'uri'})

class ServiceCustomFieldsFieldValueUpdateModelV1(PermissiveModel):
    name: str
    value: ServiceCustomFieldsFieldValueUpdateModelV1ValueV0 | ServiceCustomFieldsFieldValueUpdateModelV1ValueV1 | ServiceCustomFieldsFieldValueUpdateModelV1ValueV2 | ServiceCustomFieldsFieldValueUpdateModelV1ValueV3 | ServiceCustomFieldsFieldValueUpdateModelV1ValueV4 | ServiceCustomFieldsFieldValueUpdateModelV1ValueV5

class ServiceCustomFieldsFieldValueUpdateModel(PermissiveModel):
    """During updates:
- Omitted fields remain unchanged
- Null values reset fields
- Provided values update fields

Note: All updates succeed or none are applied.
"""
    service_custom_fields_field_value_update_model: ServiceCustomFieldsFieldValueUpdateModelV0 | ServiceCustomFieldsFieldValueUpdateModelV1

class ServiceReference(PermissiveModel):
    type_: Literal["service_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class Alert(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: Literal["alert"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of object being created.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})
    created_at: str | None = Field(None, description="The date/time the alert was first triggered.", json_schema_extra={'format': 'date-time'})
    status: Literal["triggered", "resolved"] | None = Field(None, description="The current status of the alert.")
    alert_key: str | None = Field(None, description="The alert's de-duplication key.")
    service: ServiceReference | None = None
    first_trigger_log_entry: LogEntryReference | None = None
    incident: IncidentReference | None = None
    suppressed: bool | None = Field(False, description="Whether or not an alert is suppressed. Suppressed alerts are not created with a parent incident.")
    severity: Literal["info", "warning", "error", "critical"] | None = Field(None, description="The magnitude of the problem as reported by the monitoring tool.")
    integration: IntegrationReference | None = None
    body: AlertBody | None = Field(None, description="A JSON object containing data describing the alert.")

class ChangeEvent(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A brief text summary of the event. Displayed in PagerDuty to provide information about the change. The maximum permitted length of this property is 1024 characters.")
    type_: Literal["change_event"] | None = Field('change_event', validation_alias="type", serialization_alias="type", description="The type of object being created.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})
    timestamp: str | None = Field(None, description="The time at which the emitting tool detected or generated the event.", json_schema_extra={'format': 'date-time'})
    services: list[ServiceReference] | None = Field(None, description="An array containing Service objects that this change event is associated with.")
    integration: IntegrationReference | None = None
    routing_key: str | None = Field(None, description="This is the 32 character Integration Key for an Integration on a Service. The same Integration Key can be used for both alert and change events.")
    source: str | None = Field(None, description="The unique name of the location where the Change Event occurred.")
    links: list[ChangeEventLinksItem] | None = Field(None, description="List of links to include.")
    images: list[ChangeEventImagesItem] | None = None
    custom_details: dict[str, Any] | None = Field(None, description="Additional details about the change event.")

class Extension(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: Literal["extension"] | None = Field('extension', validation_alias="type", serialization_alias="type", description="The type of object being created.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})
    name: str = Field(..., description="The name of the extension.")
    endpoint_url: str | None = Field(None, description="The url of the extension.", json_schema_extra={'format': 'url'})
    extension_objects: list[ServiceReference] = Field(..., description="The objects for which the extension applies")
    extension_schema: ExtensionSchemaReference
    temporarily_disabled: bool | None = Field(False, description="Whether or not this extension is temporarily disabled; for example, a webhook extension that is repeatedly rejected by the server.")
    config: dict[str, Any] | None = Field(None, description="The object that contains extension configuration values depending on the extension schema specification.")

class ServiceV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})

class ServiceV1AlertGroupingParametersV1(PermissiveModel):
    """When a service uses alert grouping configuration that is unsupported via the services api, and can only be configured via the [Alert Grouping Settings API](https://developer.pagerduty.com/api-reference/587edbc8ff416-create-an-alert-grouping-setting). The reference object includes the new location details for the service's Alert Grouping Setting. When an `alert_grouping_settings_reference` is included in a create or update request it will be ignored and no changes are applied to the service."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="id of the related alert grouping setting")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="type of reference eg. alert_grouping_setting_reference")
    summary: str | None = Field(None, description="an explanation of this reference")
    self: str | None = Field(None, description="link to api endpoint for this setting")
    html_url: str | None = Field(None, description="link to the ui page to edit the setting")

class ShiftMember(PermissiveModel):
    """A member (user) assigned to a shift or rotation slot"""
    type_: Literal["user_member", "empty_member"] = Field(..., validation_alias="type", serialization_alias="type", description="`user_member` — a specific user is assigned.\n`empty_member` — the slot is intentionally unassigned.\n")
    user_id: str | None = Field(None, description="The ID of the user. Required when type is `user_member`.")

class CreateCustomShiftsRequestCustomShiftsItemAssignmentsItem(PermissiveModel):
    type_: Literal["shift_assignment"] = Field(..., validation_alias="type", serialization_alias="type")
    member: ShiftMember

class CreateCustomShiftsRequestCustomShiftsItem(PermissiveModel):
    type_: Literal["custom_shift"] = Field(..., validation_alias="type", serialization_alias="type")
    start_time: str = Field(..., json_schema_extra={'format': 'date-time'})
    end_time: str = Field(..., json_schema_extra={'format': 'date-time'})
    assignments: list[CreateCustomShiftsRequestCustomShiftsItemAssignmentsItem] = Field(..., min_length=1, max_length=1)

class CreateOverridesRequestOverridesItem(PermissiveModel):
    type_: Literal["override_shift"] = Field(..., validation_alias="type", serialization_alias="type")
    rotation_id: str | None = Field(None, description="Mutually exclusive with custom_shift_id")
    custom_shift_id: str | None = Field(None, description="Mutually exclusive with rotation_id")
    start_time: str = Field(..., json_schema_extra={'format': 'date-time'})
    end_time: str = Field(..., json_schema_extra={'format': 'date-time'})
    overridden_member: ShiftMember
    overriding_member: ShiftMember

class EventAssignmentStrategy(PermissiveModel):
    """Defines how users are assigned on-call within an event's time window.

- `rotating_member_assignment_strategy`: users rotate in sequence.
  `shifts_per_member` controls how many consecutive shift periods each
  member covers before rotating.
- `every_member_assignment_strategy`: all listed members are on-call
  simultaneously for every occurrence.
"""
    type_: Literal["rotating_member_assignment_strategy", "every_member_assignment_strategy"] = Field(..., validation_alias="type", serialization_alias="type")
    shifts_per_member: int | None = Field(None, description="Required for `rotating_member_assignment_strategy`. Number of\nconsecutive shift occurrences each member covers before the\nnext member takes over.\n", ge=1)
    members: list[ShiftMember] = Field(..., min_length=1, max_length=20)

class StandardInclusionExclusion(PermissiveModel):
    type_: Literal["technical_service_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")

class StatusPagePostUpdateRequestImpactedServicesItemImpact(PermissiveModel):
    """Status Page Impact"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="An unique identifier within Status Page scope that defines a Status Page Impact entry.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the object returned by the API - in this case, a Status Page Impact.")

class StatusPagePostUpdateRequestImpactedServicesItemService(PermissiveModel):
    """Status Page Service"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="An unique identifier within Status Page scope that defines a Service entry.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the object returned by the API - in this case, a Status Page Service.")

class StatusPagePostUpdateRequestImpactedServicesItem(PermissiveModel):
    """Status Page Post Update Impact"""
    service: StatusPagePostUpdateRequestImpactedServicesItemService | None = Field(None, description="Status Page Service")
    impact: StatusPagePostUpdateRequestImpactedServicesItemImpact | None = Field(None, description="Status Page Impact")

class StatusPagePostUpdateRequestPost(PermissiveModel):
    """Status Page Post"""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Status page post unique identifier")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object.")

class StatusPagePostUpdateRequestSeverity(PermissiveModel):
    """Status Page Severity"""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Status page Severity unique identifier")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object.")

class StatusPagePostUpdateRequestStatus(PermissiveModel):
    """Status Page Status"""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Status page Status unique identifier")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object.")

class StatusPagePostUpdateRequest(PermissiveModel):
    """Attributes for Post Update creation/update"""
    self: str | None = Field(None, description="The path to which the Post Update resource is accessible.")
    post: StatusPagePostUpdateRequestPost = Field(..., description="Status Page Post")
    message: str = Field(..., description="The message of the Post Update.")
    status: StatusPagePostUpdateRequestStatus = Field(..., description="Status Page Status")
    severity: StatusPagePostUpdateRequestSeverity = Field(..., description="Status Page Severity")
    impacted_services: list[StatusPagePostUpdateRequestImpactedServicesItem] = Field(..., description="Impacted services represent the status page services affected by a post update, and its impact.", min_length=0)
    update_frequency_ms: int | None = Field(..., description="The frequency of the next Post Update in milliseconds.")
    notify_subscribers: bool = Field(..., description="Determines if the subscribers should be notified of the Post Update.")
    reported_at: str | None = Field(None, description="The date and time the Post Update was reported.", json_schema_extra={'format': 'date-time'})
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="The type of the object returned by the API - in this case, a Status Page Post Update.")

class StatusUpdateTemplateInputStatusUpdate(PermissiveModel):
    message: str | None = Field(None, description="An optional status update message that will be sent to the template")

class StatusUpdateTemplateInput(PermissiveModel):
    incident_id: str | None = Field(None, description="The incident id to render the template for")
    status_update: StatusUpdateTemplateInputStatusUpdate | None = None
    external: Any | None = Field(None, description="An optional object collection that can be referenced in the template.")

class SupportHours(PermissiveModel):
    type_: Literal["fixed_time_per_day"] | None = Field('fixed_time_per_day', validation_alias="type", serialization_alias="type", description="The type of support hours")
    time_zone: str | None = Field(None, description="The time zone for the support hours", json_schema_extra={'format': 'activesupport-time-zone'})
    days_of_week: list[int] | None = None
    start_time: str | None = Field(None, description="The support hours' starting time of day (date portion is ignored)", json_schema_extra={'format': 'time'})
    end_time: str | None = Field(None, description="The support hours' ending time of day (date portion is ignored)", json_schema_extra={'format': 'time'})

class Tag(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: Literal["tag"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of object being created.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})
    label: str = Field(..., description="The label of the tag.", max_length=191)

class Team(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: Literal["team"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of object being created.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})
    name: str = Field(..., description="The name of the team.", max_length=100)
    description: str | None = Field(None, description="The description of the team.", max_length=1024)
    default_role: Literal["manager", "none"] | None = Field('manager', description="The team is private if the value is \"none\", or public if it is \"manager\" (the default permissions for a non-member of the team are either \"none\", or their base role up until \"manager\").")

class TeamReference(PermissiveModel):
    type_: Literal["team_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class AutomationActionsAbstractActionPostBody(PermissiveModel):
    name: str = Field(..., max_length=255)
    description: str = Field(..., max_length=1024)
    action_classification: Literal["diagnostic", "remediation"] | None = None
    action_type: Literal["script", "process_automation"]
    runner: str | None = Field(None, max_length=36)
    services: list[ServiceReference] | None = None
    teams: list[TeamReference] | None = None
    only_invocable_on_unresolved_incidents: bool | None = Field(False, description="If true, the action can only be invoked against an unresolved incident.")
    allow_invocation_manually: bool | None = Field(True, description="If true, the action can only be invoked manually by a user.")
    allow_invocation_from_event_orchestration: bool | None = Field(True, description="If true, the action can only be invoked automatically by an Event Orchestration.")
    map_to_all_services: bool | None = Field(False, description="If true, the action will be associated with every service.")

class AutomationActionsProcessAutomationJobActionPostBody(PermissiveModel):
    name: str = Field(..., max_length=255)
    description: str = Field(..., max_length=1024)
    action_classification: Literal["diagnostic", "remediation"] | None = None
    action_type: Literal["script", "process_automation"]
    runner: str | None = Field(None, max_length=36)
    services: list[ServiceReference] | None = None
    teams: list[TeamReference] | None = None
    only_invocable_on_unresolved_incidents: bool | None = Field(False, description="If true, the action can only be invoked against an unresolved incident.")
    allow_invocation_manually: bool | None = Field(True, description="If true, the action can only be invoked manually by a user.")
    allow_invocation_from_event_orchestration: bool | None = Field(True, description="If true, the action can only be invoked automatically by an Event Orchestration.")
    map_to_all_services: bool | None = Field(False, description="If true, the action will be associated with every service.")
    action_data_reference: AutomationActionsProcessAutomationJobActionDataReference

class AutomationActionsRunnerRunbookPostBody(PermissiveModel):
    runner_type: Literal["sidecar", "runbook"]
    name: str = Field(..., max_length=255)
    description: str = Field(..., max_length=1024)
    runbook_base_uri: str
    runbook_api_key: str = Field(..., description="The API key to connect to the Runbook server with. If omitted, the previously stored value will remain unchanged", max_length=64)
    teams: list[TeamReference] | None = Field(None, description="The list of teams associated with the Runner")

class AutomationActionsRunnerSidecarPostBody(PermissiveModel):
    runner_type: Literal["sidecar", "runbook"]
    name: str = Field(..., max_length=255)
    description: str = Field(..., max_length=1024)
    teams: list[TeamReference] | None = Field(None, description="The list of teams associated with the Runner")

class AutomationActionsScriptActionPostBody(PermissiveModel):
    name: str = Field(..., max_length=255)
    description: str = Field(..., max_length=1024)
    action_classification: Literal["diagnostic", "remediation"] | None = None
    action_type: Literal["script", "process_automation"]
    runner: str | None = Field(None, max_length=36)
    services: list[ServiceReference] | None = None
    teams: list[TeamReference] | None = None
    only_invocable_on_unresolved_incidents: bool | None = Field(False, description="If true, the action can only be invoked against an unresolved incident.")
    allow_invocation_manually: bool | None = Field(True, description="If true, the action can only be invoked manually by a user.")
    allow_invocation_from_event_orchestration: bool | None = Field(True, description="If true, the action can only be invoked automatically by an Event Orchestration.")
    map_to_all_services: bool | None = Field(False, description="If true, the action will be associated with every service.")
    action_data_reference: AutomationActionsScriptActionDataReference

class EscalationPolicy(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: Literal["escalation_policy"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of object being created.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})
    name: str = Field(..., description="The name of the escalation policy.")
    description: str | None = Field(None, description="Escalation policy description.")
    num_loops: int | None = Field(0, description="The number of times the escalation policy will repeat after reaching the end of its escalation.", ge=0)
    on_call_handoff_notifications: Literal["if_has_services", "always"] | None = Field(None, description="Determines how on call handoff notifications will be sent for users on the escalation policy. Defaults to \"if_has_services\".")
    escalation_rules: list[EscalationRule]
    services: list[ServiceReference] | None = Field(None, min_length=0)
    teams: list[TeamReference] | None = Field(None, description="Team associated with the policy. Account must have the `teams` ability to use this parameter. Only one team may be associated with the policy.", min_length=0)

class TeamV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})

class TemplateCreatedByV1(PermissiveModel):
    type_: Literal["account_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class TemplateTemplatedFields(PermissiveModel):
    email_subject: str | None = Field(None, description="The subject of the e-mail")
    email_body: str | None = Field(None, description="The HTML body of the e-mail message")
    message: str | None = Field(None, description="The short-message of the template (SMS, Push notification, Slack,\netc)")

class TemplateUpdatedByV1(PermissiveModel):
    type_: Literal["account_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class TemplateV1CreatedByV1(PermissiveModel):
    type_: Literal["account_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class TemplateV1UpdatedByV1(PermissiveModel):
    type_: Literal["account_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class TimeBasedAlertGroupingConfiguration(PermissiveModel):
    """The configuration for Time Based Alert Grouping"""
    timeout: int | None = Field(None, description="The duration in minutes within which to automatically group incoming Alerts. To continue grouping Alerts until the Incident is resolved, set this value to 0.", ge=1, le=1440)

class AlertGroupingParameters(PermissiveModel):
    """Defines how alerts on this service will be automatically grouped into incidents. Note that the alert grouping features are available only on certain plans. To turn grouping off set the type to null.
This attribute has been deprecated and configuration via [Alert Grouping Settings](https://developer.pagerduty.com/api-reference/587edbc8ff416-create-an-alert-grouping-setting) resource is encouraged.
"""
    type_: Literal["time", "intelligent", "content_based"] | None = Field(None, validation_alias="type", serialization_alias="type")
    config: FlexibleTimeWindowIntelligentAlertGroupingConfig | TimeBasedAlertGroupingConfiguration | ContentBasedAlertGroupingConfiguration | None = None

class Service(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: Literal["service"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of object being created.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})
    name: str | None = Field(None, description="The name of the service.")
    description: str | None = Field(None, description="The user-provided description of the service.")
    auto_resolve_timeout: int | None = Field(14400, description="Time in seconds that an incident is automatically resolved if left open for that long. Value is `null` if the feature is disabled. Value must not be negative. Setting this field to `0`, `null` (or unset in POST request) will disable the feature.")
    acknowledgement_timeout: int | None = Field(1800, description="Time in seconds that an incident changes to the Triggered State after being Acknowledged. Value is `null` if the feature is disabled. Value must not be negative. Setting this field to `0`, `null` (or unset in POST request) will disable the feature.")
    created_at: str | None = Field(None, description="The date/time when this service was created", json_schema_extra={'format': 'date-time'})
    status: Literal["active", "warning", "critical", "maintenance", "disabled"] | None = Field('active', description="The current state of the Service. Valid statuses are:\n\n\n- `active`: The service is enabled and has no open incidents. This is the only status a service can be created with.\n- `warning`: The service is enabled and has one or more acknowledged incidents.\n- `critical`: The service is enabled and has one or more triggered incidents.\n- `maintenance`: The service is under maintenance, no new incidents will be triggered during maintenance mode.\n- `disabled`: The service is disabled and will not have any new triggered incidents.\n")
    last_incident_timestamp: str | None = Field(None, description="The date/time when the most recent incident was created for this service.", json_schema_extra={'format': 'date-time'})
    escalation_policy: EscalationPolicyReference
    response_play: Any | None = Field(None, description="Response plays associated with this service.")
    teams: list[TeamReference] | None = Field(None, description="The set of teams associated with this service.")
    integrations: list[IntegrationReference] | None = Field(None, description="An array containing Integration objects that belong to this service. If `integrations` is passed as an argument, these are full objects - otherwise, these are references.")
    incident_urgency_rule: IncidentUrgencyRule | None = None
    support_hours: SupportHours | None = None
    scheduled_actions: list[ScheduledAction] | None = Field(None, description="An array containing scheduled actions for the service.")
    addons: list[AddonReference] | None = Field(None, description="The array of Add-ons associated with this service.")
    alert_creation: Literal["create_incidents", "create_alerts_and_incidents"] | None = Field('create_alerts_and_incidents', description="Whether a service creates only incidents, or both alerts and incidents. A service must create alerts in order to enable incident merging.\n* \"create_incidents\" - The service will create one incident and zero alerts for each incoming event.\n* \"create_alerts_and_incidents\" - The service will create one incident and one associated alert for each incoming event.\nThis attribute has been deprecated as all services will be migrated to use alerts and incidents. Afterward, the incident only service setting will no longer be available. For details, please refer to the knowledge base: https://support.pagerduty.com/docs/alerts#enable-and-disable-alerts-on-a-service.\n")
    alert_grouping_parameters: AlertGroupingParameters | ServiceAlertGroupingParametersV1 | None = Field(None, description="Alert Grouping Parameters")
    alert_grouping: Literal["time", "intelligent"] | None = Field(None, description="Defines how alerts on this service will be automatically grouped into incidents. Note that the alert grouping features are available only on certain plans. There are three available options:\n* null - No alert grouping on the service. Each alert will create a separate incident;\n* \"time\" - All alerts within a specified duration will be grouped into the same incident. This duration is set in the `alert_grouping_timeout` setting (described below). Available on Standard, Enterprise, and Event Intelligence plans;\n* \"intelligent\" - Alerts will be intelligently grouped based on a machine learning model that looks at the alert summary, timing, and the history of grouped alerts. Available on Enterprise and Event Intelligence plans\n\nThis attribute has been deprecated and configuration via [Alert Grouping Settings](https://developer.pagerduty.com/api-reference/587edbc8ff416-create-an-alert-grouping-setting) resource is encouraged.\n")
    alert_grouping_timeout: int | None = Field(None, description="The duration in minutes within which to automatically group incoming alerts. This setting applies only when `alert_grouping` is set to `time`. To continue grouping alerts until the Incident is resolved, set this value to `0`.\n\nThis attribute has been deprecated and configuration via [Alert Grouping Settings](https://developer.pagerduty.com/api-reference/587edbc8ff416-create-an-alert-grouping-setting) resource is encouraged.\n")
    auto_pause_notifications_parameters: AutoPauseNotificationsParameters | None = None

class UpdateCustomShiftBodyCustomShiftAssignmentsItemMember(PermissiveModel):
    """A member (user) assigned to a shift or rotation slot"""
    type_: Literal["user_member", "empty_member"] = Field(..., validation_alias="type", serialization_alias="type", description="`user_member` — a specific user is assigned.\n`empty_member` — the slot is intentionally unassigned.\n")
    user_id: str | None = Field(None, description="The ID of the user. Required when type is `user_member`.")

class UpdateCustomShiftBodyCustomShiftAssignmentsItem(PermissiveModel):
    type_: Literal["shift_assignment"] = Field(..., validation_alias="type", serialization_alias="type")
    member: UpdateCustomShiftBodyCustomShiftAssignmentsItemMember = Field(..., description="A member (user) assigned to a shift or rotation slot")

class UpdateCustomShiftRequestCustomShiftAssignmentsItem(PermissiveModel):
    type_: Literal["shift_assignment"] = Field(..., validation_alias="type", serialization_alias="type")
    member: ShiftMember

class UpdateCustomShiftRequestCustomShift(PermissiveModel):
    """If the shift has already started,
only `end_time` can be modified.
"""
    start_time: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    end_time: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    assignments: list[UpdateCustomShiftRequestCustomShiftAssignmentsItem] | None = Field(None, min_length=1, max_length=1)

class UpdateIncidentBodyIncidentPriority(PermissiveModel):
    """Also accepts scalar shorthand."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the priority.")
    name: str | None = Field(None, description="The user-provided short name of the priority.")
    type_: Literal["priority", "priority_reference"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the reference.")

class UpdateIncidentsBodyIncidentsItemPriorityV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the priority.")
    name: str | None = Field(None, description="The user-provided short name of the priority.")
    type_: Literal["priority", "priority_reference"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the reference.")

class UpdateOverrideRequestOverride(PermissiveModel):
    start_time: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    end_time: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    overriding_member: ShiftMember | None = None

class UpdateServiceCustomFieldBodyFieldFieldOptionsItemData(PermissiveModel):
    """The data content of the field option."""
    data_type: Literal["string"] = Field(..., description="The kind of data represented by this option. Must match the Field's `data_type`.")
    value: str = Field(..., description="The value of the field option. Must be unique within the field.", max_length=200)

class UpdateServiceCustomFieldBodyFieldFieldOptionsItem(PermissiveModel):
    data: UpdateServiceCustomFieldBodyFieldFieldOptionsItemData = Field(..., description="The data content of the field option.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The unique identifier of the field option. How this field is used determines the behavior:\n  - When included with a valid `id`: Updates the corresponding existing field option\n  - When omitted or null: Creates a new field option\n")

class UpdateStandardBodyValues(PermissiveModel):
    regex: str | None = None

class UpdateStandardBody(PermissiveModel):
    active: bool | None = None
    values: UpdateStandardBodyValues | None = None
    description: str | None = None
    inclusions: list[StandardInclusionExclusion] | None = None
    exclusions: list[StandardInclusionExclusion] | None = None

class UpdateStatusPagePostUpdateBodyPostUpdateImpactedServicesItemImpact(PermissiveModel):
    """Status Page Impact"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="An unique identifier within Status Page scope that defines a Status Page Impact entry.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the object returned by the API - in this case, a Status Page Impact.")

class UpdateStatusPagePostUpdateBodyPostUpdateImpactedServicesItemService(PermissiveModel):
    """Status Page Service"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="An unique identifier within Status Page scope that defines a Service entry.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the object returned by the API - in this case, a Status Page Service.")

class UpdateStatusPagePostUpdateBodyPostUpdateImpactedServicesItem(PermissiveModel):
    """Status Page Post Update Impact"""
    service: UpdateStatusPagePostUpdateBodyPostUpdateImpactedServicesItemService | None = Field(None, description="Status Page Service")
    impact: UpdateStatusPagePostUpdateBodyPostUpdateImpactedServicesItemImpact | None = Field(None, description="Status Page Impact")

class UpdateWorkflowIntegrationConnectionBodyAppsItem(PermissiveModel):
    app_id: str | None = Field(None, description="The ID of the app")
    type_: Literal["pd_app_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class UpdateWorkflowIntegrationConnectionBodyTeamsItem(PermissiveModel):
    team_id: str | None = Field(None, description="The ID of the team")
    type_: Literal["team_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class User(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: Literal["user"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of object being created.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})
    name: str = Field(..., description="The name of the user.", max_length=100)
    email: str = Field(..., description="The user's email address.", min_length=6, max_length=100, json_schema_extra={'format': 'email'})
    time_zone: str | None = Field(None, description="The preferred time zone name. If null, the account's time zone will be used.", json_schema_extra={'format': 'tzinfo'})
    color: str | None = Field(None, description="The schedule color.")
    role: Literal["admin", "limited_user", "observer", "owner", "read_only_user", "restricted_access", "read_only_limited_user", "user"] | None = Field(None, description="The user role. Account must have the `read_only_users` ability to set a user as a `read_only_user` or a `read_only_limited_user`, and must have advanced permissions abilities to set a user as `observer` or `restricted_access`.")
    avatar_url: str | None = Field(None, description="The URL of the user's avatar.", json_schema_extra={'format': 'url'})
    description: str | None = Field(None, description="The user's bio.")
    invitation_sent: bool | None = Field(None, description="If true, the user has an outstanding invitation.")
    job_title: str | None = Field(None, description="The user's title.", max_length=100)
    created_via_sso: bool | None = Field(None, description="If true, the user was created via Single Sign-On (SSO).")
    teams: list[TeamReference] | None = Field(None, description="The list of teams to which the user belongs. Account must have the `teams` ability to set this.")
    contact_methods: list[ContactMethodReference] | None = Field(None, description="The list of contact methods for the user.")
    notification_rules: list[NotificationRuleReference] | None = Field(None, description="The list of notification rules for the user.")

class Acknowledgement(PermissiveModel):
    at: str = Field(..., description="Time at which the acknowledgement was created.", json_schema_extra={'format': 'date-time'})
    acknowledger: AcknowledgerReference | User | Service

class CreateUserBodyUser(PermissiveModel):
    license_: LicenseReference | None = Field(None, validation_alias="license", serialization_alias="license")

class UpdateUserBodyUser(PermissiveModel):
    license_: LicenseReference | None = Field(None, validation_alias="license", serialization_alias="license")

class UserReference(PermissiveModel):
    type_: Literal["user_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class Assignment(PermissiveModel):
    at: str = Field(..., description="Time at which the assignment was created.", json_schema_extra={'format': 'date-time'})
    assignee: UserReference | User

class CreateIncidentBodyIncidentAssignmentsItem(PermissiveModel):
    assignee: UserReference | None = None

class IncidentsRespondersReference(PermissiveModel):
    state: Literal["pending", "joined", "declined", "user_cancelled"] | None = Field(None, description="The status of the responder being added to the incident")
    user: UserReference | None = None
    incident: IncidentReference | None = None
    updated_at: str | None = None
    message: str | None = Field(None, description="The message sent with the responder request")
    requester: UserReference | None = None
    requested_at: str | None = None
    escalation_policy_requests: list[str] | None = Field(None, description="Names of escalation policies that this responder was requested through, if applicable")

class MaintenanceWindow(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: Literal["maintenance_window"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of object being created.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})
    sequence_number: int | None = Field(None, description="The order in which the maintenance window was created.")
    start_time: str = Field(..., description="This maintenance window's start time. This is when the services will stop creating incidents. If this date is in the past, it will be updated to be the current time.", json_schema_extra={'format': 'date-time'})
    end_time: str = Field(..., description="This maintenance window's end time. This is when the services will start creating incidents again. This date must be in the future and after the `start_time`.", json_schema_extra={'format': 'date-time'})
    description: str | None = Field(None, description="A description for this maintenance window.")
    created_by: UserReference | None = None
    services: list[ServiceReference]
    teams: list[TeamReference] | None = None

class Notification(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: Literal["sms_notification", "email_notification", "phone_notification", "push_notification"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of notification.")
    started_at: str | None = Field(None, description="The time at which the notification was sent", json_schema_extra={'format': 'date-time'})
    address: str | None = Field(None, description="The address where the notification was sent. This will be null for notification type `push_notification`.")
    user: UserReference | None = None
    conference_address: str | None = Field(None, validation_alias="conferenceAddress", serialization_alias="conferenceAddress", description="The address of the conference bridge")
    status: str | None = None
    field: str | None = None

class Channel(PermissiveModel):
    """Polymorphic object representation of the means by which the action was channeled. Has different formats depending on type, indicated by channel[type]. Will be one of `auto`, `email`, `api`, `nagios`, or `timeout` if `agent[type]` is `service`. Will be one of `email`, `sms`, `website`, `web_trigger`, or `note` if `agent[type]` is `user`."""
    channel: ChannelV0 | ChannelV1 | ChannelV2 | ChannelV3 | ChannelV4

class LogEntry(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: Literal["acknowledge_log_entry", "annotate_log_entry", "assign_log_entry", "delegate_log_entry", "escalate_log_entry", "exhaust_escalation_path_log_entry", "notify_log_entry", "reach_ack_limit_log_entry", "reach_trigger_limit_log_entry", "repeat_escalation_path_log_entry", "resolve_log_entry", "snooze_log_entry", "trigger_log_entry", "unacknowledge_log_entry", "urgency_change_log_entry", "field_value_change_log_entry", "custom_field_value_change_log_entry"] | None = Field(None, validation_alias="type", serialization_alias="type")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})
    created_at: str | None = Field(None, description="Time at which the log entry was created.", json_schema_extra={'format': 'date-time'})
    channel: Channel | None = None
    agent: AgentReference | None = None
    note: str | None = Field(None, description="Optional field containing a note, if one was included with the log entry.")
    contexts: list[Context] | None = Field(None, description="Contexts to be included with the trigger such as links to graphs or images.")
    service: ServiceReference | None = None
    incident: IncidentReference | None = None
    teams: list[TeamReference] | None = Field(None, description="Will consist of references unless included")
    event_details: LogEntryEventDetails | None = None
    changeset: list[str] | None = Field(None, description="String record of custom field updates")

class ResponderRequestTargetReference(PermissiveModel):
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of target (either a user or an escalation policy)")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The id of the user or escalation policy")
    summary: str | None = None
    incident_responders: list[IncidentsRespondersReference] | None = Field(None, description="An array of responders associated with the specified incident")

class ResponderRequest(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the responder request")
    incident: IncidentReference | None = None
    requester: UserReference | None = None
    requested_at: str | None = Field(None, description="The time the request was made")
    message: str | None = Field(None, description="The message sent with the responder request")
    responder_request_targets: list[ResponderRequestTargetReference] | None = Field(None, description="The array of targets the responder request is being sent to")

class ScheduleLayerEntry(PermissiveModel):
    user: UserReference | None = None
    start: str = Field(..., description="The start time of this entry.", json_schema_extra={'format': 'date-time'})
    end: str = Field(..., description="The end time of this entry. If null, the entry does not end.", json_schema_extra={'format': 'date-time'})

class ScheduleLayerUser(PermissiveModel):
    user: UserReference

class ScheduleLayer(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    start: str = Field(..., description="The start time of this layer.", json_schema_extra={'format': 'date-time'})
    end: str | None = Field(None, description="The end time of this layer. If `null`, the layer does not end.", json_schema_extra={'format': 'date-time'})
    users: list[ScheduleLayerUser] = Field(..., description="The ordered list of users on this layer. The position of the user on the list determines their order in the layer.")
    restrictions: list[Restriction] | None = Field(None, description="An array of restrictions for the layer. A restriction is a limit on which period of the day or week the schedule layer can accept assignments. Restrictions respect the `time_zone` parameter of the request.")
    rotation_virtual_start: str = Field(..., description="The effective start time of the layer. This can be before the start time of the schedule.", json_schema_extra={'format': 'date-time'})
    rotation_turn_length_seconds: int = Field(..., description="The duration of each on-call shift in seconds.")
    name: str | None = Field(None, description="The name of the schedule layer.")
    rendered_schedule_entries: list[ScheduleLayerEntry] | None = Field(None, description="This is a list of entries on the computed layer for the current time range. Since or until must be set in order for this field to be populated.")
    rendered_coverage_percentage: float | None = Field(None, description="The percentage of the time range covered by this layer. Returns null unless since or until are set.")

class Template(PermissiveModel):
    template_type: Literal["status_update"] | None = Field(None, description="The type of template (`status_update` is the only supported template at this time)")
    name: str | None = Field(None, description="The name of the template")
    description: str | None = Field(None, description="Description of the template")
    templated_fields: TemplateTemplatedFields | None = None
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})
    type_: Literal["template"] | None = Field(None, validation_alias="type", serialization_alias="type")
    created_by: UserReference | TemplateCreatedByV1 | None = Field(None, description="User/Account object reference of the creator")
    updated_by: UserReference | TemplateUpdatedByV1 | None = Field(None, description="User/Account object reference of the updator")

class TriggerLogEntry(PermissiveModel):
    type_: Literal["trigger_log_entry"] | None = Field(None, validation_alias="type", serialization_alias="type")

class Incident(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})
    incident_number: int | None = Field(None, description="The number of the incident. This is unique across your account.")
    title: str | None = Field(None, description="A succinct description of the nature, symptoms, cause, or effect of the incident.")
    created_at: str | None = Field(None, description="The time the incident was first triggered.", json_schema_extra={'format': 'date-time'})
    updated_at: str | None = Field(None, description="The time the incident was last modified.", json_schema_extra={'format': 'date-time'})
    status: Literal["triggered", "acknowledged", "resolved"] | None = Field(None, description="The current status of the incident.")
    incident_key: str | None = Field(None, description="The incident's de-duplication key.")
    service: ServiceReference | Service | None = Field(None, description="The service the incident is on. If the `include[]=services` query parameter is provided, the full service definition will be returned.")
    assignments: list[Assignment] | None = Field(None, description="List of all assignments for this incident. This list will be empty if the `Incident.status` is `resolved`. Returns a user reference for each assignment. Full user definitions will be returned if the `include[]=assignees` query parameter is provided.")
    assigned_via: Literal["escalation_policy", "direct_assignment"] | None = Field(None, description="How the current incident assignments were decided.  Note that `direct_assignment` incidents will not escalate up the attached `escalation_policy`")
    last_status_change_at: str | None = Field(None, description="The time the status of the incident last changed. If the incident is not currently acknowledged or resolved, this will be the incident's `updated_at`.", json_schema_extra={'format': 'date-time'})
    resolved_at: str | None = Field(None, description="The time the incident became \"resolved\" or `null` if the incident is not resolved.", json_schema_extra={'format': 'date-time'})
    first_trigger_log_entry: LogEntryReference | TriggerLogEntry | None = Field(None, description="The first log entry on the incident. The log entry will be of type `TriggerLogEntry` and will represent information about how the incident was triggered. If the `include[]=first_trigger_log_entries` query parameter is provided, the full log entry definition will be returned.")
    alert_counts: AlertCount | None = None
    is_mergeable: bool | None = Field(None, description="Whether the incident is mergeable. Only incidents that have alerts, or that are manually created can be merged.")
    incident_type: IncidentIncidentType | None = Field(None, description="The incident type of the incident.")
    escalation_policy: EscalationPolicyReference | EscalationPolicy | None = Field(None, description="The escalation policy attached to the service that the incident is on. If the `include[]=escalation_policies` query parameter is provided, the full escalation policy definition will be returned.")
    teams: list[TeamReference | Team] | None = Field(None, description="The teams involved in the incident’s lifecycle. If the `include[]=teams` query parameter is provided, the full team definitions will be returned.")
    pending_actions: list[IncidentAction] | None = Field(None, description="The list of pending_actions on the incident. A pending_action object contains a type of action which can be escalate, unacknowledge, resolve or urgency_change. A pending_action object contains at, the time at which the action will take place. An urgency_change pending_action will contain to, the urgency that the incident will change to.")
    acknowledgements: list[Acknowledgement] | None = Field(None, description="List of all acknowledgements for this incident. This list will be empty if the `Incident.status` is `resolved` or `triggered`. If the `include[]=acknowledgers` query parameter is provided, the full user or service definitions will be returned for each acknowledgement entry.")
    alert_grouping: IncidentAlertGrouping | None = Field(None, description="Describes the alert grouping state of this incident. Will be null if the incident has no alerts.")
    last_status_change_by: AgentReference | User | Service | None = Field(None, description="The entity that last changed the status of the incident. If the `include[]=agents` query parameter is provided, the full user/service/integration definition will be returned.")
    priority: Priority | None = None
    resolve_reason: ResolveReason | None = None
    conference_bridge: ConferenceBridge | None = Field(None, description="The conference bridge information attached to the incident. Only returned if the `include[]=conference_bridge` query parameter is provided.")
    incidents_responders: list[IncidentsRespondersReference] | None = Field(None, description="The responders on the incident. Only returned if the account has access to the [responder requests](https://support.pagerduty.com/docs/add-responders) feature.")
    responder_requests: list[ResponderRequest] | None = Field(None, description="Previous responder requests made on this incident. Only returned if the account has access to the [responder requests](https://support.pagerduty.com/docs/add-responders) feature.")
    urgency: Literal["high", "low"] | None = Field(None, description="The current urgency of the incident.")
    body: IncidentBody | None = Field(None, description="The additional incident body details. Only returned if the `include[]=body` query parameter is provided.")

class UpdateIncidentBodyIncidentAssignmentsItem(PermissiveModel):
    assignee: UserReference | None = None

class UpdateIncidentsBodyIncidentsItemAssignmentsItem(PermissiveModel):
    assignee: UserReference | None = None

class UpdateIncidentsBodyIncidentsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The id of the incident to update.")
    type_: Literal["incident", "incident_reference"] = Field(..., validation_alias="type", serialization_alias="type", description="The incident type.")
    status: Literal["resolved", "acknowledged", "triggered"] | None = Field(None, description="The new status of the incident. If the incident is currently resolved, setting the status to \"triggered\" or \"acknowledged\" will reopen it. When reopening an incident to the \"triggered\" status, it will be assigned based on the assignees or escalation_policy fields in the request, otherwise it will be assigned to the current Escalation Policy. When reopening an incident to the \"acknowledged\" status, it will be assigned to the current user.")
    resolution: str | None = Field(None, description="The resolution for this incident. This field is used only when setting the incident status to resolved.\nThe value provided here is added to the incident’s 'Resolve' log entry as a note and will not be displayed directly in the UI.\n")
    title: str | None = Field(None, description="A succinct description of the nature, symptoms, cause, or effect of the incident.")
    priority: UpdateIncidentsBodyIncidentsItemPriorityV0 | str | None = Field(None, description="The priority of the incident. Can be provided as a priority object or a string matching a priority name. If a string is provided, the highest priority with a matching name will be used.")
    escalation_level: int | None = Field(None, description="Escalate the incident to this level in the escalation policy.")
    assignments: list[UpdateIncidentsBodyIncidentsItemAssignmentsItem] | None = Field(None, description="Assign the incident to these assignees.")
    incident_type: IncidentTypeReference | None = None
    escalation_policy: EscalationPolicyReference | None = None
    urgency: Literal["high", "low"] | None = Field(None, description="The urgency of the incident.")
    conference_bridge: ConferenceBridge | None = None

class UserV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A string that determines the schema of the object. This must be the standard name for the entity, suffixed by `_reference` if the object is a reference.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})

class VendorReference(PermissiveModel):
    type_: Literal["vendor_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class WebhookObject(PermissiveModel):
    type_: Literal["service", "service_reference"] | None = Field(None, validation_alias="type", serialization_alias="type")

class Webhook(PermissiveModel):
    """Information about the configured webhook."""
    endpoint_url: str | None = Field(None, description="The url endpoint the webhook payload is sent to.", json_schema_extra={'format': 'url'})
    name: str | None = Field(None, description="The name of the webhook.")
    webhook_object: WebhookObject | None = None
    config: dict[str, Any] | None = Field(None, description="The object that contains webhook configuration values depending on the webhook type specification.")
    outbound_integration: OutboundIntegrationReference | None = None

class Action(PermissiveModel):
    """A message containing information about a single PagerDuty action."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Uniquely identifies this outgoing webhook message; can be used for idempotency when processing the messages.", json_schema_extra={'format': 'uuid'})
    triggered_at: str | None = Field(None, description="The date/time when this message was was sent.", json_schema_extra={'format': 'date-time'})
    webhook: Webhook | None = None

class WhatsAppContactMethod(PermissiveModel):
    """The WhatsApp Contact Method of the User.

**Availability Note:** WhatsApp contact methods are available in select regions and require account-level access. For information about regional availability and how to enable WhatsApp for your account, please refer to the [PagerDuty Knowledge Base](https://support.pagerduty.com/).
"""
    type_: Literal["whatsapp_contact_method"] | None = Field(None, validation_alias="type", serialization_alias="type")
    country_code: int = Field(..., description="The 1-to-3 digit country calling code.", ge=1, le=1999)
    enabled: bool | None = Field(None, description="If true, this phone is capable of receiving WhatsApp messages.")
    blacklisted: bool | None = Field(None, description="If true, this phone has been blacklisted by PagerDuty and no messages will be sent to it.")

class ZonedDateTime(PermissiveModel):
    """A time-of-day value with an explicit time zone. Used for event
`start_time` and `end_time` to define the recurring window of coverage
(e.g., 9 AM–5 PM every Monday in New York).
"""
    date_time: str = Field(..., description="The date and time", json_schema_extra={'format': 'date-time'})
    time_zone: str = Field(..., description="IANA timezone identifier")

class CreateEventRequestEvent(PermissiveModel):
    name: str = Field(..., max_length=255)
    start_time: ZonedDateTime
    end_time: ZonedDateTime
    effective_since: str = Field(..., description="When this event starts producing shifts. Values in the past are\nclamped to the current time.\n", json_schema_extra={'format': 'date-time'})
    effective_until: str | None = Field(None, description="When this event stops producing shifts. Omit or null for indefinite.", json_schema_extra={'format': 'date-time'})
    recurrence: list[str] = Field(..., description="RFC 5545 recurrence rules")
    assignment_strategy: EventAssignmentStrategy

class Event(PermissiveModel):
    """An event defines when and how users are on-call within a rotation.
It combines a recurring time window (`start_time`, `end_time`,
`recurrence`) with an assignment strategy and an effective date range
(`effective_since`, `effective_until`).
"""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    type_: Literal["schedule_event"] = Field(..., validation_alias="type", serialization_alias="type")
    name: str = Field(..., description="Display name for this event")
    start_time: ZonedDateTime
    end_time: ZonedDateTime
    effective_since: str = Field(..., description="When this event starts producing shifts (UTC)", json_schema_extra={'format': 'date-time'})
    effective_until: str | None = Field(None, description="When this event stops producing shifts (UTC). Null means indefinite.", json_schema_extra={'format': 'date-time'})
    recurrence: list[str] = Field(..., description="RFC 5545 recurrence rules defining the repeating pattern. This must be an array containing:  <br> - Exactly one <b>RRULE</b> <br>- Zero or more <b>EXDATE</b> <br>- Zero or more <b>RDATE</b>")
    assignment_strategy: EventAssignmentStrategy
    self: str | None = Field(None, json_schema_extra={'format': 'uri'})
    html_url: str | None = Field(None, json_schema_extra={'format': 'uri'})

class UpdateEventRequestEvent(PermissiveModel):
    name: str | None = Field(None, max_length=255)
    start_time: ZonedDateTime | None = None
    end_time: ZonedDateTime | None = None
    effective_since: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    effective_until: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    recurrence: list[str] | None = None
    assignment_strategy: EventAssignmentStrategy | None = None

class EmailParser(PermissiveModel):
    action: Literal["trigger", "resolve"]
    match_predicate: MatchPredicate
    value_extractors: Annotated[list[EmailParserValueExtractorsItem], AfterValidator(_check_unique_items)] | None = Field(None, description="Additional values that will be pulled in to the Incident object. Exactly one value extractor must have a `value_name` of `incident_key`.", min_length=1)

class Integration(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: Literal["aws_cloudwatch_inbound_integration", "cloudkick_inbound_integration", "event_transformer_api_inbound_integration", "generic_email_inbound_integration", "generic_events_api_inbound_integration", "keynote_inbound_integration", "nagios_inbound_integration", "pingdom_inbound_integration", "sql_monitor_inbound_integration", "events_api_v2_inbound_integration"] | None = Field(None, validation_alias="type", serialization_alias="type")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})
    name: str | None = Field(None, description="The name of this integration.")
    service: ServiceReference | None = None
    created_at: str | None = Field(None, description="The date/time when this integration was created.", json_schema_extra={'format': 'date-time'})
    vendor: VendorReference | None = None
    integration_email: str | None = Field(None, description="Specify for generic_email_inbound_integration. Must be set to an email address @your-subdomain.pagerduty.com")
    email_incident_creation: Literal["on_new_email", "on_new_email_subject", "only_if_no_open_incidents", "use_rules"] | None = Field(None, description="Specify for generic_email_inbound_integration")
    email_filter_mode: Literal["all-email", "or-rules-email", "and-rules-email"] | None = Field(None, description="Specify for generic_email_inbound_integration. May override email_incident_creation")
    email_parsers: Annotated[list[EmailParser], AfterValidator(_check_unique_items)] | None = Field(None, description="Specify for generic_email_inbound_integration.", min_length=1)
    email_parsing_fallback: Literal["open_new_incident", "discard"] | None = Field(None, description="Specify for generic_email_inbound_integration.")
    email_filters: Annotated[list[IntegrationEmailFiltersItem], AfterValidator(_check_unique_items)] | None = Field(None, description="Specify for generic_email_inbound_integration.", min_length=1)

class MatchPredicate(PermissiveModel):
    type_: Literal["all", "any", "not", "contains", "exactly", "regex"] = Field(..., validation_alias="type", serialization_alias="type")
    matcher: str | None = Field(None, description="Required if the type is `contains`, `exactly` or `regex`.", min_length=1)
    part: Literal["body", "subject", "from_addresses"] = Field(..., description="The email field that will attempt to use the matcher expression. Required if the type is `contains`, `exactly` or `regex`.")
    children: list[MatchPredicate] = Field(..., description="Additional matchers to be run. Must be not empty if the type is `all`, `any`, or `not`.")

class Schedule(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    summary: str | None = Field(None, description="A short-form, server-generated string that provides succinct, important information about an object suitable for primary labeling of an entity in a client. In many cases, this will be identical to `name`, though it is not intended to be an identifier.")
    type_: Literal["schedule"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of object being created.")
    self: str | None = Field(None, description="the API show URL at which the object is accessible", json_schema_extra={'format': 'url'})
    html_url: str | None = Field(None, description="a URL at which the entity is uniquely displayed in the Web app", json_schema_extra={'format': 'url'})
    schedule_layers: list[ScheduleLayer] | None = Field(None, description="A list of schedule layers.")
    time_zone: str = Field(..., description="The time zone of the schedule.", json_schema_extra={'format': 'activesupport-time-zone'})
    name: str | None = Field(None, description="The name of the schedule")
    description: str | None = Field(None, description="The description of the schedule")
    final_schedule: SubSchedule | None = None
    overrides_subschedule: SubSchedule | None = None
    escalation_policies: list[EscalationPolicyReference] | None = Field(None, description="An array of all of the escalation policies that uses this schedule.")
    users: list[UserReference] | None = Field(None, description="An array of all of the users on the schedule.")
    teams: list[TeamReference] | None = Field(None, description="An array of all of the teams on the schedule.")
    next_oncall_for_user: ScheduleNextOncallForUser | None = None

class SubSchedule(PermissiveModel):
    name: Literal["Final Schedule", "Overrides"] = Field(..., description="The name of the subschedule")
    rendered_schedule_entries: list[ScheduleLayerEntry] | None = Field(None, description="This is a list of entries on the computed layer for the current time range. Since or until must be set in order for this field to be populated.")
    rendered_coverage_percentage: float | None = Field(None, description="The percentage of the time range covered by this layer. Returns null unless since or until are set.")


# Rebuild models to resolve forward references (required for circular refs)
Acknowledgement.model_rebuild()
AcknowledgerReference.model_rebuild()
Action.model_rebuild()
AddonReference.model_rebuild()
AgentReference.model_rebuild()
Alert.model_rebuild()
AlertBody.model_rebuild()
AlertCount.model_rebuild()
AlertGroupingParameters.model_rebuild()
AlertUpdate.model_rebuild()
AlertUpdateIncidentReference.model_rebuild()
AlertV0.model_rebuild()
AlertV1Body.model_rebuild()
Assignment.model_rebuild()
AutomationActionsAbstractActionPostBody.model_rebuild()
AutomationActionsAbstractActionPutBody.model_rebuild()
AutomationActionsProcessAutomationJobActionDataReference.model_rebuild()
AutomationActionsProcessAutomationJobActionPostBody.model_rebuild()
AutomationActionsProcessAutomationJobActionPutBody.model_rebuild()
AutomationActionsRunnerRunbookBody.model_rebuild()
AutomationActionsRunnerRunbookPostBody.model_rebuild()
AutomationActionsRunnerSidecarBody.model_rebuild()
AutomationActionsRunnerSidecarPostBody.model_rebuild()
AutomationActionsScriptActionDataReference.model_rebuild()
AutomationActionsScriptActionPostBody.model_rebuild()
AutomationActionsScriptActionPutBody.model_rebuild()
AutoPauseNotificationsParameters.model_rebuild()
CancelIncidentResponderRequestBodyResponderRequestTargetsItem.model_rebuild()
ChangeEvent.model_rebuild()
ChangeEventImagesItem.model_rebuild()
ChangeEventLinksItem.model_rebuild()
ChangeEventV0.model_rebuild()
ChangeEventV1ImagesItem.model_rebuild()
ChangeEventV1LinksItem.model_rebuild()
Channel.model_rebuild()
ChannelChangeset.model_rebuild()
ChannelChangesetApplicationFieldsItem.model_rebuild()
ChannelChangesetCustomerFieldsItem.model_rebuild()
ChannelChangesetCustomerSchema.model_rebuild()
ChannelV0.model_rebuild()
ChannelV1.model_rebuild()
ChannelV2.model_rebuild()
ChannelV3.model_rebuild()
ChannelV4.model_rebuild()
ConferenceBridge.model_rebuild()
ContactMethod.model_rebuild()
ContactMethodReference.model_rebuild()
ContactMethodV0.model_rebuild()
ContentBasedAlertGroupingConfiguration.model_rebuild()
Context.model_rebuild()
CreateCustomShiftsBodyCustomShiftsItem.model_rebuild()
CreateCustomShiftsBodyCustomShiftsItemAssignmentsItem.model_rebuild()
CreateCustomShiftsBodyCustomShiftsItemAssignmentsItemMember.model_rebuild()
CreateCustomShiftsRequestCustomShiftsItem.model_rebuild()
CreateCustomShiftsRequestCustomShiftsItemAssignmentsItem.model_rebuild()
CreateEntityTypeByIdChangeTagsBodyAddItem.model_rebuild()
CreateEntityTypeByIdChangeTagsBodyRemoveItem.model_rebuild()
CreateEventRequestEvent.model_rebuild()
CreateIncidentBodyIncidentAssignmentsItem.model_rebuild()
CreateOverridesBodyOverridesItem.model_rebuild()
CreateOverridesBodyOverridesItemOverriddenMember.model_rebuild()
CreateOverridesBodyOverridesItemOverridingMember.model_rebuild()
CreateOverridesRequestOverridesItem.model_rebuild()
CreateScheduleV3BodyScheduleTeamsItem.model_rebuild()
CreateServiceDependencyBodyRelationshipsItem.model_rebuild()
CreateServiceDependencyBodyRelationshipsItemDependentService.model_rebuild()
CreateServiceDependencyBodyRelationshipsItemSupportingService.model_rebuild()
CreateStatusPagePostUpdateBodyPostUpdateImpactedServicesItem.model_rebuild()
CreateStatusPagePostUpdateBodyPostUpdateImpactedServicesItemImpact.model_rebuild()
CreateStatusPagePostUpdateBodyPostUpdateImpactedServicesItemService.model_rebuild()
CreateUserBodyUser.model_rebuild()
CreateWorkflowIntegrationConnectionBodyAppsItem.model_rebuild()
CreateWorkflowIntegrationConnectionBodyTeamsItem.model_rebuild()
CustomFieldsEditableFieldOption.model_rebuild()
CustomFieldsEditableFieldOptionDataV0.model_rebuild()
CustomFieldsEditableFieldValue.model_rebuild()
CustomFieldsEditableFieldValueV0.model_rebuild()
CustomFieldsEditableFieldValueV0ValueV0.model_rebuild()
CustomFieldsEditableFieldValueV0ValueV1.model_rebuild()
CustomFieldsEditableFieldValueV0ValueV2.model_rebuild()
CustomFieldsEditableFieldValueV0ValueV3.model_rebuild()
CustomFieldsEditableFieldValueV0ValueV4.model_rebuild()
CustomFieldsEditableFieldValueV0ValueV5.model_rebuild()
CustomFieldsEditableFieldValueV1.model_rebuild()
CustomFieldsEditableFieldValueV1ValueV0.model_rebuild()
CustomFieldsEditableFieldValueV1ValueV1.model_rebuild()
CustomFieldsEditableFieldValueV1ValueV2.model_rebuild()
CustomFieldsEditableFieldValueV1ValueV3.model_rebuild()
CustomFieldsEditableFieldValueV1ValueV4.model_rebuild()
CustomFieldsEditableFieldValueV1ValueV5.model_rebuild()
CustomFieldsFieldOption.model_rebuild()
CustomFieldsFieldOptionDataV0.model_rebuild()
DeleteServiceDependencyBodyRelationshipsItem.model_rebuild()
DeleteServiceDependencyBodyRelationshipsItemDependentService.model_rebuild()
DeleteServiceDependencyBodyRelationshipsItemSupportingService.model_rebuild()
EditableTemplate.model_rebuild()
EditableTemplateTemplatedFields.model_rebuild()
EmailContactMethod.model_rebuild()
EmailParser.model_rebuild()
EmailParserValueExtractorsItem.model_rebuild()
EscalationPolicy.model_rebuild()
EscalationPolicyReference.model_rebuild()
EscalationPolicyV0.model_rebuild()
EscalationRule.model_rebuild()
EscalationTargetReference.model_rebuild()
Event.model_rebuild()
EventAssignmentStrategy.model_rebuild()
Extension.model_rebuild()
ExtensionSchemaReference.model_rebuild()
ExtensionV0.model_rebuild()
FlexibleTimeWindowIntelligentAlertGroupingConfig.model_rebuild()
Impact.model_rebuild()
ImpactAdditionalFields.model_rebuild()
ImpactAdditionalFieldsHighestImpactingPriority.model_rebuild()
Incident.model_rebuild()
IncidentAction.model_rebuild()
IncidentAlertGrouping.model_rebuild()
IncidentBody.model_rebuild()
IncidentIncidentType.model_rebuild()
IncidentReference.model_rebuild()
IncidentsRespondersReference.model_rebuild()
IncidentTypeReference.model_rebuild()
IncidentUrgencyRule.model_rebuild()
IncidentUrgencyType.model_rebuild()
IncidentV0.model_rebuild()
IncidentV1AlertGrouping.model_rebuild()
IncidentV1IncidentType.model_rebuild()
Integration.model_rebuild()
IntegrationEmailFiltersItem.model_rebuild()
IntegrationReference.model_rebuild()
IntegrationV0.model_rebuild()
IntegrationV1EmailFiltersItem.model_rebuild()
LicenseReference.model_rebuild()
LogEntry.model_rebuild()
LogEntryEventDetails.model_rebuild()
LogEntryReference.model_rebuild()
LogEntryV0.model_rebuild()
LogEntryV1EventDetails.model_rebuild()
MaintenanceWindow.model_rebuild()
MaintenanceWindowV0.model_rebuild()
MatchPredicate.model_rebuild()
Notification.model_rebuild()
NotificationRule.model_rebuild()
NotificationRuleReference.model_rebuild()
NotificationRuleV0.model_rebuild()
NotificationSubscribable.model_rebuild()
NotificationSubscriber.model_rebuild()
Orchestration.model_rebuild()
OrchestrationCacheVariableExternalData.model_rebuild()
OrchestrationCacheVariableExternalDataConfiguration.model_rebuild()
OrchestrationCacheVariableExternalDataCreatedBy.model_rebuild()
OrchestrationCacheVariableExternalDataUpdatedBy.model_rebuild()
OrchestrationCacheVariableExternalDataV0.model_rebuild()
OrchestrationCacheVariableExternalDataV0CreatedBy.model_rebuild()
OrchestrationCacheVariableExternalDataV0UpdatedBy.model_rebuild()
OrchestrationCacheVariableExternalDataV1Configuration.model_rebuild()
OrchestrationCacheVariableRecentValue.model_rebuild()
OrchestrationCacheVariableRecentValueConditionsItem.model_rebuild()
OrchestrationCacheVariableRecentValueConfiguration.model_rebuild()
OrchestrationCacheVariableRecentValueCreatedBy.model_rebuild()
OrchestrationCacheVariableRecentValueUpdatedBy.model_rebuild()
OrchestrationCacheVariableRecentValueV0CreatedBy.model_rebuild()
OrchestrationCacheVariableRecentValueV0UpdatedBy.model_rebuild()
OrchestrationCacheVariableRecentValueV1ConditionsItem.model_rebuild()
OrchestrationCacheVariableRecentValueV1Configuration.model_rebuild()
OrchestrationCacheVariableTriggerEventCount.model_rebuild()
OrchestrationCacheVariableTriggerEventCountConditionsItem.model_rebuild()
OrchestrationCacheVariableTriggerEventCountConfiguration.model_rebuild()
OrchestrationCacheVariableTriggerEventCountCreatedBy.model_rebuild()
OrchestrationCacheVariableTriggerEventCountUpdatedBy.model_rebuild()
OrchestrationCacheVariableTriggerEventCountV0.model_rebuild()
OrchestrationCacheVariableTriggerEventCountV0CreatedBy.model_rebuild()
OrchestrationCacheVariableTriggerEventCountV0UpdatedBy.model_rebuild()
OrchestrationCacheVariableTriggerEventCountV1ConditionsItem.model_rebuild()
OrchestrationCacheVariableTriggerEventCountV1Configuration.model_rebuild()
OrchestrationCreatedBy.model_rebuild()
OrchestrationIntegration.model_rebuild()
OrchestrationIntegrationParameters.model_rebuild()
OrchestrationTeam.model_rebuild()
OrchestrationUpdatedBy.model_rebuild()
OutboundIntegrationReference.model_rebuild()
PhoneContactMethod.model_rebuild()
Priority.model_rebuild()
PriorityReference.model_rebuild()
PriorityV0.model_rebuild()
PushContactMethod.model_rebuild()
PushContactMethodSound.model_rebuild()
Reference.model_rebuild()
ReferenceV0.model_rebuild()
ResolveReason.model_rebuild()
ResponderRequest.model_rebuild()
ResponderRequestTargetReference.model_rebuild()
Restriction.model_rebuild()
Schedule.model_rebuild()
ScheduledAction.model_rebuild()
ScheduledActionAt.model_rebuild()
ScheduleLayer.model_rebuild()
ScheduleLayerEntry.model_rebuild()
ScheduleLayerUser.model_rebuild()
ScheduleNextOncallForUser.model_rebuild()
ScheduleV0.model_rebuild()
ScheduleV1NextOncallForUser.model_rebuild()
Service.model_rebuild()
ServiceAlertGroupingParametersV1.model_rebuild()
ServiceCustomFieldsFieldValueUpdateModel.model_rebuild()
ServiceCustomFieldsFieldValueUpdateModelV0.model_rebuild()
ServiceCustomFieldsFieldValueUpdateModelV0ValueV0.model_rebuild()
ServiceCustomFieldsFieldValueUpdateModelV0ValueV1.model_rebuild()
ServiceCustomFieldsFieldValueUpdateModelV0ValueV2.model_rebuild()
ServiceCustomFieldsFieldValueUpdateModelV0ValueV3.model_rebuild()
ServiceCustomFieldsFieldValueUpdateModelV0ValueV4.model_rebuild()
ServiceCustomFieldsFieldValueUpdateModelV0ValueV5.model_rebuild()
ServiceCustomFieldsFieldValueUpdateModelV1.model_rebuild()
ServiceCustomFieldsFieldValueUpdateModelV1ValueV0.model_rebuild()
ServiceCustomFieldsFieldValueUpdateModelV1ValueV1.model_rebuild()
ServiceCustomFieldsFieldValueUpdateModelV1ValueV2.model_rebuild()
ServiceCustomFieldsFieldValueUpdateModelV1ValueV3.model_rebuild()
ServiceCustomFieldsFieldValueUpdateModelV1ValueV4.model_rebuild()
ServiceCustomFieldsFieldValueUpdateModelV1ValueV5.model_rebuild()
ServiceReference.model_rebuild()
ServiceV0.model_rebuild()
ServiceV1AlertGroupingParametersV1.model_rebuild()
ShiftMember.model_rebuild()
StandardInclusionExclusion.model_rebuild()
StatusPagePostUpdateRequest.model_rebuild()
StatusPagePostUpdateRequestImpactedServicesItem.model_rebuild()
StatusPagePostUpdateRequestImpactedServicesItemImpact.model_rebuild()
StatusPagePostUpdateRequestImpactedServicesItemService.model_rebuild()
StatusPagePostUpdateRequestPost.model_rebuild()
StatusPagePostUpdateRequestSeverity.model_rebuild()
StatusPagePostUpdateRequestStatus.model_rebuild()
StatusUpdateTemplateInput.model_rebuild()
StatusUpdateTemplateInputStatusUpdate.model_rebuild()
SubSchedule.model_rebuild()
SupportHours.model_rebuild()
Tag.model_rebuild()
Team.model_rebuild()
TeamReference.model_rebuild()
TeamV0.model_rebuild()
Template.model_rebuild()
TemplateCreatedByV1.model_rebuild()
TemplateTemplatedFields.model_rebuild()
TemplateUpdatedByV1.model_rebuild()
TemplateV1CreatedByV1.model_rebuild()
TemplateV1UpdatedByV1.model_rebuild()
TimeBasedAlertGroupingConfiguration.model_rebuild()
TriggerLogEntry.model_rebuild()
UpdateCustomShiftBodyCustomShiftAssignmentsItem.model_rebuild()
UpdateCustomShiftBodyCustomShiftAssignmentsItemMember.model_rebuild()
UpdateCustomShiftRequestCustomShift.model_rebuild()
UpdateCustomShiftRequestCustomShiftAssignmentsItem.model_rebuild()
UpdateEventRequestEvent.model_rebuild()
UpdateIncidentBodyIncidentAssignmentsItem.model_rebuild()
UpdateIncidentBodyIncidentPriority.model_rebuild()
UpdateIncidentsBodyIncidentsItem.model_rebuild()
UpdateIncidentsBodyIncidentsItemAssignmentsItem.model_rebuild()
UpdateIncidentsBodyIncidentsItemPriorityV0.model_rebuild()
UpdateOverrideRequestOverride.model_rebuild()
UpdateServiceCustomFieldBodyFieldFieldOptionsItem.model_rebuild()
UpdateServiceCustomFieldBodyFieldFieldOptionsItemData.model_rebuild()
UpdateStandardBody.model_rebuild()
UpdateStandardBodyValues.model_rebuild()
UpdateStatusPagePostUpdateBodyPostUpdateImpactedServicesItem.model_rebuild()
UpdateStatusPagePostUpdateBodyPostUpdateImpactedServicesItemImpact.model_rebuild()
UpdateStatusPagePostUpdateBodyPostUpdateImpactedServicesItemService.model_rebuild()
UpdateUserBodyUser.model_rebuild()
UpdateWorkflowIntegrationConnectionBodyAppsItem.model_rebuild()
UpdateWorkflowIntegrationConnectionBodyTeamsItem.model_rebuild()
User.model_rebuild()
UserReference.model_rebuild()
UserV0.model_rebuild()
VendorReference.model_rebuild()
Webhook.model_rebuild()
WebhookObject.model_rebuild()
WhatsAppContactMethod.model_rebuild()
ZonedDateTime.model_rebuild()

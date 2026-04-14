"""
Bamboohr MCP Server - Pydantic Models

Generated: 2026-04-14 18:15:45 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "AddCompanyFileCategoryRequest",
    "AddEmployeeFileCategoryRequest",
    "AdjustTimeOffBalanceRequest",
    "AssignEmployeesToBreakPolicyRequest",
    "AssignTimeOffPoliciesRequest",
    "AssignTimeOffPoliciesV11Request",
    "CloseGoalRequest",
    "CreateApplicationCommentRequest",
    "CreateBreakPolicyRequest",
    "CreateBreakRequest",
    "CreateCandidateRequest",
    "CreateEmployeeDependentRequest",
    "CreateEmployeeRequest",
    "CreateEmployeeTrainingRecordRequest",
    "CreateGoalCommentRequest",
    "CreateGoalRequest",
    "CreateJobOpeningRequest",
    "CreateOrUpdateTimesheetClockEntriesRequest",
    "CreateOrUpdateTimesheetHourEntriesRequest",
    "CreateOrUpdateTimeTrackingHourRecordsRequest",
    "CreateTableRowRequest",
    "CreateTableRowV11Request",
    "CreateTimeOffHistoryRequest",
    "CreateTimeOffRequest",
    "CreateTimesheetClockInEntryRequest",
    "CreateTimesheetClockOutEntryRequest",
    "CreateTimeTrackingHourRecordRequest",
    "CreateTimeTrackingProjectRequest",
    "CreateTrainingCategoryRequest",
    "CreateTrainingTypeRequest",
    "DeleteBreakPolicyRequest",
    "DeleteBreakRequest",
    "DeleteCompanyFileRequest",
    "DeleteEmployeeFileRequest",
    "DeleteEmployeeTableRowRequest",
    "DeleteEmployeeTrainingRecordRequest",
    "DeleteGoalCommentRequest",
    "DeleteGoalRequest",
    "DeleteTimesheetClockEntriesViaPostRequest",
    "DeleteTimesheetHourEntriesViaPostRequest",
    "DeleteTimeTrackingHourRecordRequest",
    "DeleteTrainingCategoryRequest",
    "DeleteTrainingTypeRequest",
    "DeleteWebhookRequest",
    "GetAlignableGoalOptionsRequest",
    "GetApplicationDetailsRequest",
    "GetApplicationsRequest",
    "GetBreakPolicyRequest",
    "GetBreakRequest",
    "GetByReportIdRequest",
    "GetChangedEmployeeIdsRequest",
    "GetChangedEmployeeTableDataRequest",
    "GetCompanyFileRequest",
    "GetDataFromDatasetRequest",
    "GetEmployeeDependentRequest",
    "GetEmployeeFileRequest",
    "GetEmployeePhotoRequest",
    "GetEmployeeRequest",
    "GetEmployeesDirectoryRequest",
    "GetEmployeeTableDataRequest",
    "GetFieldOptionsRequest",
    "GetFieldOptionsV12Request",
    "GetFieldsFromDatasetRequest",
    "GetFieldsFromDatasetV12Request",
    "GetGoalAggregateRequest",
    "GetGoalsAggregateV12Request",
    "GetGoalsFiltersV12Request",
    "GetJobSummariesRequest",
    "GetMemberBenefitsRequest",
    "GetStatesByCountryIdRequest",
    "GetTimeOffBalanceRequest",
    "GetTimeTrackingRecordRequest",
    "GetWebhookLogsRequest",
    "GetWebhookRequest",
    "ListBreakAssessmentsRequest",
    "ListBreakPoliciesRequest",
    "ListBreakPolicyBreaksRequest",
    "ListBreakPolicyEmployeesRequest",
    "ListEmployeeBenefitsRequest",
    "ListEmployeeBreakAvailabilitiesRequest",
    "ListEmployeeBreakPoliciesRequest",
    "ListEmployeeDependentsRequest",
    "ListEmployeeFilesRequest",
    "ListEmployeesRequest",
    "ListEmployeeTimeOffPoliciesRequest",
    "ListEmployeeTimeOffPoliciesV11Request",
    "ListEmployeeTrainingsRequest",
    "ListGoalCommentsRequest",
    "ListGoalShareOptionsRequest",
    "ListGoalsRequest",
    "ListListFieldsRequest",
    "ListReportsRequest",
    "ListTimeOffRequestsRequest",
    "ListTimeOffTypesRequest",
    "ListTimesheetEntriesRequest",
    "ListUsersRequest",
    "ListWhosOutRequest",
    "Op5c5fb0f1211ae1c9451753f92f1053b6Request",
    "ReopenGoalRequest",
    "ReplaceBreaksForBreakPolicyRequest",
    "SetBreakPolicyEmployeesRequest",
    "SyncBreakPolicyRequest",
    "UnassignEmployeesFromBreakPolicyRequest",
    "UpdateApplicantStatusRequest",
    "UpdateBreakPolicyRequest",
    "UpdateBreakRequest",
    "UpdateCompanyFileRequest",
    "UpdateEmployeeDependentRequest",
    "UpdateEmployeeFileRequest",
    "UpdateEmployeeRequest",
    "UpdateEmployeeTrainingRecordRequest",
    "UpdateGoalCommentRequest",
    "UpdateGoalMilestoneProgressRequest",
    "UpdateGoalProgressRequest",
    "UpdateGoalSharingRequest",
    "UpdateGoalV11Request",
    "UpdateListFieldValuesRequest",
    "UpdateTableRowRequest",
    "UpdateTableRowV11Request",
    "UpdateTimeOffRequestStatusRequest",
    "UpdateTimeTrackingRecordRequest",
    "UpdateTrainingCategoryRequest",
    "UpdateTrainingTypeRequest",
    "UploadCompanyFileRequest",
    "UploadEmployeeFileRequest",
    "UploadEmployeePhotoRequest",
    "AssignTimeOffPoliciesBodyItem",
    "AssignTimeOffPoliciesV11BodyItem",
    "ClockEntrySchema",
    "CreateGoalBodyMilestonesItem",
    "CreateTimeOffRequestBodyDatesItem",
    "CreateTimeOffRequestBodyNotesItem",
    "CursorPaginationQueryObject",
    "GetDataFromDatasetBodyAggregationsItem",
    "GetDataFromDatasetBodyFiltersFiltersItem",
    "GetDataFromDatasetBodySortByItem",
    "GetEmployeesFilterRequestObject",
    "GetFieldOptionsBodyDependentFieldsValueItem",
    "GetFieldOptionsV12BodyDependentFieldsValueItem",
    "HourEntrySchema",
    "TaskCreateSchema",
    "TimeTrackingCreateOrUpdateTimeTrackingBreakWithoutPolicyV1",
    "TimeTrackingRecord",
    "UpdateGoalV11BodyMilestonesItem",
    "UpdateListFieldValuesBodyOptionsItem",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: create_project
class CreateTimeTrackingProjectRequestBody(StrictModel):
    name: str = Field(default=..., description="Unique display name for the project, no more than 50 characters.", max_length=50)
    billable: bool | None = Field(default=None, description="Whether time logged to this project is billable. Defaults to true if omitted.")
    allow_all_employees: bool | None = Field(default=None, validation_alias="allowAllEmployees", serialization_alias="allowAllEmployees", description="Whether all employees are permitted to log time to this project. Set to false and provide employeeIds to restrict access to specific employees. Defaults to true if omitted.")
    employee_ids: list[int] | None = Field(default=None, validation_alias="employeeIds", serialization_alias="employeeIds", description="List of employee IDs permitted to log time to this project. Only applied when allowAllEmployees is false; ignored otherwise.")
    has_tasks: bool | None = Field(default=None, validation_alias="hasTasks", serialization_alias="hasTasks", description="Whether the project supports task-level time tracking. When true, at least one task must be provided in the tasks array. Defaults to false if omitted.")
    tasks: list[TaskCreateSchema] | None = Field(default=None, description="Tasks to create and associate with the project. Required when hasTasks is true; each task name must be unique within the project and no more than 50 characters. Order is not significant.")
class CreateTimeTrackingProjectRequest(StrictModel):
    """Creates a new time tracking project with optional task-level tracking and employee access controls. Returns the created project including its ID, tasks, and employee access list when access is restricted."""
    body: CreateTimeTrackingProjectRequestBody

# Operation: list_break_assessments
class ListBreakAssessmentsRequestQuery(StrictModel):
    offset: int | None = Field(default=None, description="Number of records to skip before returning results, used for paginating through large result sets. Must be zero or greater; defaults to 0.", ge=0)
    limit: int | None = Field(default=None, description="Maximum number of break assessment records to return in a single response. Accepts values from 0 to 500; defaults to 100.", ge=0, le=500)
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="OData v4 filter expression to narrow results by specific fields. Filterable fields include: `id`, `breakId`, `employeeId`, `employeeTimesheetId`, `date`, `result`, `availableYmdt`, `unavailableYmdt`, `createdAt`, `updatedAt`, `expectedDuration`, `recordedDuration`, and `durationDifference`.")
class ListBreakAssessmentsRequest(StrictModel):
    """Retrieves a paginated list of break assessments, each recording whether an employee complied with their assigned break policy for a given day along with any violations. Use the filter parameter to scope results by employee, date, compliance result, or other fields."""
    query: ListBreakAssessmentsRequestQuery | None = None

# Operation: get_break
class GetBreakRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the time tracking break to retrieve, provided as a UUID.", json_schema_extra={'format': 'uuid'})
class GetBreakRequest(StrictModel):
    """Retrieves the full details of a specific time tracking break by its unique identifier, including its name, duration, paid status, and availability configuration."""
    path: GetBreakRequestPath

# Operation: update_break
class UpdateBreakRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the break to update.", json_schema_extra={'format': 'uuid'})
class UpdateBreakRequestBody(StrictModel):
    name: str | None = Field(default=None, description="Human-readable label for the break, used to identify it in schedules and reports.")
    policy_id: str | None = Field(default=None, validation_alias="policyId", serialization_alias="policyId", description="The UUID of the break policy this break belongs to, linking it to a set of organizational rules.", json_schema_extra={'format': 'uuid'})
    paid: bool | None = Field(default=None, description="Indicates whether employees are compensated during this break; true means the break counts toward paid work time.")
    duration: int | None = Field(default=None, description="The length of the break in whole minutes.")
    availability_type: Literal["anytime", "hours_worked", "time_of_day"] | None = Field(default=None, validation_alias="availabilityType", serialization_alias="availabilityType", description="Determines when the break becomes available: 'anytime' imposes no restriction, 'hours_worked' gates availability on hours worked thresholds, and 'time_of_day' restricts the break to a specific time window.")
    availability_min_hours_worked: float | None = Field(default=None, validation_alias="availabilityMinHoursWorked", serialization_alias="availabilityMinHoursWorked", description="The minimum number of hours an employee must have worked before this break becomes available; applicable when availabilityType is 'hours_worked'.", json_schema_extra={'format': 'float'})
    availability_max_hours_worked: float | None = Field(default=None, validation_alias="availabilityMaxHoursWorked", serialization_alias="availabilityMaxHoursWorked", description="The maximum number of hours an employee can work before this break must be taken; applicable when availabilityType is 'hours_worked'.", json_schema_extra={'format': 'float'})
    availability_start_time: str | None = Field(default=None, validation_alias="availabilityStartTime", serialization_alias="availabilityStartTime", description="The earliest clock time at which the break may be started, in HH:MM 24-hour format; applicable when availabilityType is 'time_of_day'.", json_schema_extra={'format': 'time'})
    availability_end_time: str | None = Field(default=None, validation_alias="availabilityEndTime", serialization_alias="availabilityEndTime", description="The latest clock time by which the break must be started, in HH:MM 24-hour format; applicable when availabilityType is 'time_of_day'.", json_schema_extra={'format': 'time'})
class UpdateBreakRequest(StrictModel):
    """Partially updates an existing time tracking break by its UUID, modifying only the fields provided in the request body. Returns the full updated break record on success."""
    path: UpdateBreakRequestPath
    body: UpdateBreakRequestBody | None = None

# Operation: delete_break
class DeleteBreakRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the break to delete, provided as a UUID.", json_schema_extra={'format': 'uuid'})
class DeleteBreakRequest(StrictModel):
    """Soft-deletes a time tracking break by its unique identifier, permanently removing it from any associated break policies."""
    path: DeleteBreakRequestPath

# Operation: list_break_policy_breaks
class ListBreakPolicyBreaksRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the break policy whose breaks you want to retrieve.", json_schema_extra={'format': 'uuid'})
class ListBreakPolicyBreaksRequestQuery(StrictModel):
    offset: int | None = Field(default=None, description="The number of records to skip before returning results, used for paginating through large result sets.")
    limit: int | None = Field(default=None, description="The maximum number of breaks to return in a single response, up to a limit of 500.", le=500)
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="An OData v4 filter expression used to query breaks by specific field values or conditions.")
class ListBreakPolicyBreaksRequest(StrictModel):
    """Retrieves a paginated list of breaks associated with a specific break policy. Supports OData v4 filtering to narrow results by break attributes."""
    path: ListBreakPolicyBreaksRequestPath
    query: ListBreakPolicyBreaksRequestQuery | None = None

# Operation: create_break
class CreateBreakRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the break policy to associate the new break with.", json_schema_extra={'format': 'uuid'})
class CreateBreakRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A descriptive label for the break, used to identify it within the policy.")
    paid: bool | None = Field(default=None, description="Indicates whether employees are compensated during this break.")
    duration: int | None = Field(default=None, description="How long the break lasts, expressed in whole minutes.")
    availability_type: Literal["anytime", "hours_worked", "time_of_day"] | None = Field(default=None, validation_alias="availabilityType", serialization_alias="availabilityType", description="Controls when the break becomes available: 'anytime' allows it at any point, 'hours_worked' gates it on hours worked thresholds, and 'time_of_day' restricts it to a specific time window.")
    availability_min_hours_worked: float | None = Field(default=None, validation_alias="availabilityMinHoursWorked", serialization_alias="availabilityMinHoursWorked", description="The minimum number of hours an employee must have worked before this break becomes available; applicable when availabilityType is 'hours_worked'.", json_schema_extra={'format': 'float'})
    availability_max_hours_worked: float | None = Field(default=None, validation_alias="availabilityMaxHoursWorked", serialization_alias="availabilityMaxHoursWorked", description="The maximum number of hours an employee can work before this break must be taken; applicable when availabilityType is 'hours_worked'.", json_schema_extra={'format': 'float'})
    availability_start_time: str | None = Field(default=None, validation_alias="availabilityStartTime", serialization_alias="availabilityStartTime", description="The earliest clock time at which the break can be taken, in HH:MM 24-hour format; applicable when availabilityType is 'time_of_day'.", json_schema_extra={'format': 'time'})
    availability_end_time: str | None = Field(default=None, validation_alias="availabilityEndTime", serialization_alias="availabilityEndTime", description="The latest clock time by which the break must be taken, in HH:MM 24-hour format; applicable when availabilityType is 'time_of_day'.", json_schema_extra={'format': 'time'})
class CreateBreakRequest(StrictModel):
    """Creates a new break and associates it with the specified break policy. Configure the break's name, pay status, duration, and availability rules to control when employees can take it."""
    path: CreateBreakRequestPath
    body: CreateBreakRequestBody | None = None

# Operation: replace_break_policy_breaks
class ReplaceBreaksForBreakPolicyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the break policy whose breaks will be replaced.", json_schema_extra={'format': 'uuid'})
class ReplaceBreaksForBreakPolicyRequestBody(StrictModel):
    body: list[TimeTrackingCreateOrUpdateTimeTrackingBreakWithoutPolicyV1] | None = Field(default=None, description="The full desired collection of breaks for the policy. Each item with an ID will be updated, items without an ID will be created, and any existing breaks not included will be soft-deleted. Order is not significant.")
class ReplaceBreaksForBreakPolicyRequest(StrictModel):
    """Replaces the complete set of breaks for a specified break policy. Breaks with an ID are updated, breaks without an ID are created, and any existing breaks omitted from the request are soft-deleted."""
    path: ReplaceBreaksForBreakPolicyRequestPath
    body: ReplaceBreaksForBreakPolicyRequestBody | None = None

# Operation: assign_employees_to_break_policy
class AssignEmployeesToBreakPolicyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the break policy to which employees will be assigned.", json_schema_extra={'format': 'uuid'})
class AssignEmployeesToBreakPolicyRequestBody(StrictModel):
    employee_ids: list[int] = Field(default=..., validation_alias="employeeIds", serialization_alias="employeeIds", description="List of employee IDs to add to the break policy. Must contain at least one ID; order is not significant.", min_length=1)
class AssignEmployeesToBreakPolicyRequest(StrictModel):
    """Assigns one or more employees to an existing break policy, adding them to the policy's membership without affecting any previously assigned employees."""
    path: AssignEmployeesToBreakPolicyRequestPath
    body: AssignEmployeesToBreakPolicyRequestBody

# Operation: assign_break_policy_employees
class SetBreakPolicyEmployeesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the break policy whose employee assignments will be replaced.", json_schema_extra={'format': 'uuid'})
class SetBreakPolicyEmployeesRequestBody(StrictModel):
    employee_ids: list[int] = Field(default=..., validation_alias="employeeIds", serialization_alias="employeeIds", description="Complete list of employee IDs to assign to the break policy. This fully replaces all current assignments — any employee not included will be unassigned. Order is not significant.")
class SetBreakPolicyEmployeesRequest(StrictModel):
    """Assigns a specific set of employees to a break policy, fully replacing all existing employee assignments with the provided list."""
    path: SetBreakPolicyEmployeesRequestPath
    body: SetBreakPolicyEmployeesRequestBody

# Operation: unassign_employees_from_break_policy
class UnassignEmployeesFromBreakPolicyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="Unique identifier of the break policy from which employees will be unassigned.", json_schema_extra={'format': 'uuid'})
class UnassignEmployeesFromBreakPolicyRequestBody(StrictModel):
    employee_ids: list[int] = Field(default=..., validation_alias="employeeIds", serialization_alias="employeeIds", description="List of one or more employee IDs to remove from the break policy; order is not significant and each entry should be a valid employee identifier.", min_length=1)
class UnassignEmployeesFromBreakPolicyRequest(StrictModel):
    """Removes specific employees from a break policy assignment without affecting the policy itself or other assigned employees. Only applicable to policies that are not configured to apply to all employees."""
    path: UnassignEmployeesFromBreakPolicyRequestPath
    body: UnassignEmployeesFromBreakPolicyRequestBody

# Operation: get_break_policy
class GetBreakPolicyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the break policy to retrieve.", json_schema_extra={'format': 'uuid'})
class GetBreakPolicyRequestQuery(StrictModel):
    include_counts: bool | None = Field(default=None, validation_alias="includeCounts", serialization_alias="includeCounts", description="When set to true, the response includes the total number of employees and breaks associated with this policy.")
class GetBreakPolicyRequest(StrictModel):
    """Retrieves a single break policy by its unique identifier. Optionally includes counts of associated employees and breaks for summary reporting."""
    path: GetBreakPolicyRequestPath
    query: GetBreakPolicyRequestQuery | None = None

# Operation: update_break_policy
class UpdateBreakPolicyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the break policy to update.", json_schema_extra={'format': 'uuid'})
class UpdateBreakPolicyRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name for the break policy, typically reflecting a geographic region or compliance context.")
    description: str | None = Field(default=None, description="An optional human-readable description providing additional context about the break policy's purpose or scope.")
    all_employees_assigned: bool | None = Field(default=None, validation_alias="allEmployeesAssigned", serialization_alias="allEmployeesAssigned", description="When set to true, this break policy is automatically assigned to all employees rather than a specific subset.")
class UpdateBreakPolicyRequest(StrictModel):
    """Partially updates an existing break policy by its UUID, modifying only the fields provided in the request body. Returns the full updated break policy on success."""
    path: UpdateBreakPolicyRequestPath
    body: UpdateBreakPolicyRequestBody | None = None

# Operation: delete_break_policy
class DeleteBreakPolicyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the break policy to delete, provided as a UUID.", json_schema_extra={'format': 'uuid'})
class DeleteBreakPolicyRequest(StrictModel):
    """Permanently deletes a break policy by its unique identifier. All associated breaks and employee assignments linked to the policy are also removed."""
    path: DeleteBreakPolicyRequestPath

# Operation: list_break_policies
class ListBreakPoliciesRequestQuery(StrictModel):
    offset: int | None = Field(default=None, description="Number of records to skip before returning results, used for paginating through large result sets.")
    limit: int | None = Field(default=None, description="Maximum number of break policies to return in a single response, up to 500 per request.", le=500)
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="OData v4 filter expression to narrow results by policy attributes such as name or status.")
    include_counts: bool | None = Field(default=None, validation_alias="includeCounts", serialization_alias="includeCounts", description="When enabled, each policy in the response will include the count of assigned employees and associated breaks.")
class ListBreakPoliciesRequest(StrictModel):
    """Retrieves a paginated list of all break policies configured in the time-tracking system. Optionally includes employee and break counts per policy for summary reporting."""
    query: ListBreakPoliciesRequestQuery | None = None

# Operation: create_break_policy
class CreateBreakPolicyRequestBody(StrictModel):
    name: str = Field(default=..., description="Display name for the break policy, typically reflecting the jurisdiction or compliance context it applies to.")
    description: str | None = Field(default=None, description="Optional human-readable description providing additional context about the policy's purpose or compliance requirements.")
    all_employees_assigned: bool | None = Field(default=None, validation_alias="allEmployeesAssigned", serialization_alias="allEmployeesAssigned", description="When set to true, automatically assigns this break policy to all employees, superseding any individual employee assignments.")
    breaks: list[TimeTrackingCreateOrUpdateTimeTrackingBreakWithoutPolicyV1] | None = Field(default=None, description="List of break definitions to create and associate with this policy simultaneously. Each item defines a break's rules and timing configuration.")
    employee_ids: list[int] | None = Field(default=None, validation_alias="employeeIds", serialization_alias="employeeIds", description="List of employee IDs to assign to this policy. Ignored if allEmployeesAssigned is true. Order is not significant.")
class CreateBreakPolicyRequest(StrictModel):
    """Creates a new break policy for time tracking compliance, optionally including break definitions and employee assignments in a single request."""
    body: CreateBreakPolicyRequestBody

# Operation: list_employee_break_availabilities
class ListEmployeeBreakAvailabilitiesRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the employee whose break availabilities are being retrieved.")
class ListEmployeeBreakAvailabilitiesRequestQuery(StrictModel):
    effective: str | None = Field(default=None, description="The employee's local datetime used to calculate which breaks are currently available, defaulting to the current time if omitted. Must be provided in ISO 8601 local datetime format (no timezone offset).", pattern='^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}$')
class ListEmployeeBreakAvailabilitiesRequest(StrictModel):
    """Retrieves the available break options for a specific employee at a given point in time. Requires permission to view the target employee and time-tracking-break access."""
    path: ListEmployeeBreakAvailabilitiesRequestPath
    query: ListEmployeeBreakAvailabilitiesRequestQuery | None = None

# Operation: list_employee_break_policies
class ListEmployeeBreakPoliciesRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the employee whose break policies are being retrieved.")
class ListEmployeeBreakPoliciesRequestQuery(StrictModel):
    offset: int | None = Field(default=None, description="The number of records to skip before returning results, used for paginating through large result sets. Must be 0 or greater.", ge=0)
    limit: int | None = Field(default=None, description="The maximum number of break policies to return in a single response. Accepts values between 0 and 500.", ge=0, le=500)
class ListEmployeeBreakPoliciesRequest(StrictModel):
    """Retrieves all break policies assigned to a specific employee. Requires permission to view the target employee's records."""
    path: ListEmployeeBreakPoliciesRequestPath
    query: ListEmployeeBreakPoliciesRequestQuery | None = None

# Operation: list_break_policy_employees
class ListBreakPolicyEmployeesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the break policy whose assigned employees you want to retrieve.", json_schema_extra={'format': 'uuid'})
class ListBreakPolicyEmployeesRequestQuery(StrictModel):
    offset: int | None = Field(default=None, description="The number of records to skip before returning results, used for paginating through large result sets.")
    limit: int | None = Field(default=None, description="The maximum number of employee records to return in a single response, up to a limit of 500.", le=500)
class ListBreakPolicyEmployeesRequest(StrictModel):
    """Retrieves the list of employees assigned to a specific break policy. Returns an empty list if no employees are currently assigned to the policy."""
    path: ListBreakPolicyEmployeesRequestPath
    query: ListBreakPolicyEmployeesRequestQuery | None = None

# Operation: replace_break_policy
class SyncBreakPolicyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="Unique identifier of the break policy to fully replace.", json_schema_extra={'format': 'uuid'})
class SyncBreakPolicyRequestBody(StrictModel):
    name: str | None = Field(default=None, description="Display name for the break policy, typically reflecting the region or compliance context it applies to.")
    description: str | None = Field(default=None, description="Optional human-readable description providing additional context about the break policy's purpose or compliance scope.")
    all_employees_assigned: bool | None = Field(default=None, validation_alias="allEmployeesAssigned", serialization_alias="allEmployeesAssigned", description="When set to true, this policy applies to all employees in the organization, superseding individual employee assignments.")
    breaks: list[TimeTrackingCreateOrUpdateTimeTrackingBreakWithoutPolicyV1] | None = Field(default=None, description="Complete list of break definitions to associate with this policy; any breaks previously on the policy that are omitted here will be deleted. Each item should represent a full break configuration.")
    employee_ids: list[int] | None = Field(default=None, validation_alias="employeeIds", serialization_alias="employeeIds", description="Complete list of employee IDs to assign to this policy; any employees previously assigned who are omitted here will be unassigned. Ignored if allEmployeesAssigned is true.")
class SyncBreakPolicyRequest(StrictModel):
    """Performs a full replacement of a break policy and all its associated data, including breaks and employee assignments. Any breaks or assignments not included in the request payload will be removed from the policy."""
    path: SyncBreakPolicyRequestPath
    body: SyncBreakPolicyRequestBody | None = None

# Operation: delete_clock_entries
class DeleteTimesheetClockEntriesViaPostRequestBody(StrictModel):
    clock_entry_ids: list[int] = Field(default=..., validation_alias="clockEntryIds", serialization_alias="clockEntryIds", description="List of one or more clock entry IDs to delete. At least one ID must be provided; order does not matter.", min_length=1)
class DeleteTimesheetClockEntriesViaPostRequest(StrictModel):
    """Permanently deletes one or more timesheet clock entries by their unique IDs. This operation is idempotent, so submitting IDs for already-deleted entries will not cause errors or require retries."""
    body: DeleteTimesheetClockEntriesViaPostRequestBody

# Operation: delete_hour_entries
class DeleteTimesheetHourEntriesViaPostRequestBody(StrictModel):
    hour_entry_ids: list[int] = Field(default=..., validation_alias="hourEntryIds", serialization_alias="hourEntryIds", description="List of one or more timesheet hour entry IDs to delete. At least one ID must be provided; order does not affect the outcome.", min_length=1)
class DeleteTimesheetHourEntriesViaPostRequest(StrictModel):
    """Permanently deletes one or more timesheet hour entries by their unique IDs. This operation is idempotent, so submitting IDs for already-deleted entries will not cause errors or require retries."""
    body: DeleteTimesheetHourEntriesViaPostRequestBody

# Operation: list_timesheet_entries
class ListTimesheetEntriesRequestQuery(StrictModel):
    start: str = Field(default=..., description="The start of the date range to filter timesheet entries, inclusive. Must be a date within the last 365 days, in ISO 8601 date format.", json_schema_extra={'format': 'date'})
    end: str = Field(default=..., description="The end of the date range to filter timesheet entries, inclusive. Must be a date within the last 365 days, in ISO 8601 date format.", json_schema_extra={'format': 'date'})
    employee_ids: str | None = Field(default=None, validation_alias="employeeIds", serialization_alias="employeeIds", description="Comma-separated list of employee IDs used to restrict results to specific employees. When omitted, entries for all accessible employees are returned.", pattern='^\\d+(,\\d+)*$')
class ListTimesheetEntriesRequest(StrictModel):
    """Retrieves timesheet entries (clock and hour types) for all employees or a filtered subset within a specified date range. Both dates must fall within the last 365 days and are interpreted in the company timezone."""
    query: ListTimesheetEntriesRequestQuery

# Operation: clock_in_employee
class CreateTimesheetClockInEntryRequestPath(StrictModel):
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="Unique identifier of the employee to clock in.")
class CreateTimesheetClockInEntryRequestBody(StrictModel):
    project_id: int | None = Field(default=None, validation_alias="projectId", serialization_alias="projectId", description="Associates the timesheet entry with a specific time tracking project. Required when specifying a task.")
    task_id: int | None = Field(default=None, validation_alias="taskId", serialization_alias="taskId", description="Associates the timesheet entry with a specific task within the given project. Requires projectId to be provided.")
    note: str | None = Field(default=None, description="Free-text note to attach to the timesheet entry for additional context.")
    date: str | None = Field(default=None, description="The calendar date of the clock-in entry for historical records. Must follow YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    start: str | None = Field(default=None, description="The clock-in time for historical entries in 24-hour HH:MM format, ranging from 00:00 to 23:59.", pattern='^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    timezone_: str | None = Field(default=None, validation_alias="timezone", serialization_alias="timezone", description="IANA timezone name used to interpret the date and start time for historical clock-in entries.")
    break_id: str | None = Field(default=None, validation_alias="breakId", serialization_alias="breakId", description="UUID of the break type to associate with this timesheet entry.", json_schema_extra={'format': 'uuid'})
    offline: bool | None = Field(default=None, description="Marks the entry as an offline punch, bypassing shift schedule restrictions. Intended for devices that buffer punches locally and sync them later.")
class CreateTimesheetClockInEntryRequest(StrictModel):
    """Records a clock-in entry for an employee, defaulting to the current server time. To log a historical entry, supply a date, start time, and timezone, and optionally associate the entry with a project, task, break, or note."""
    path: CreateTimesheetClockInEntryRequestPath
    body: CreateTimesheetClockInEntryRequestBody | None = None

# Operation: clock_out_employee
class CreateTimesheetClockOutEntryRequestPath(StrictModel):
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee to clock out.")
class CreateTimesheetClockOutEntryRequestBody(StrictModel):
    date: str | None = Field(default=None, description="The calendar date of the clock-out entry, required when recording a historical entry rather than clocking out at the current server time. Must follow YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    end: str | None = Field(default=None, description="The clock-out time for a historical entry, expressed in 24-hour HH:MM format where hours range from 00–23 and minutes from 00–59.", pattern='^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
    timezone_: str | None = Field(default=None, validation_alias="timezone", serialization_alias="timezone", description="The IANA timezone name associated with the clock-out time, required when recording a historical entry to ensure the end time is interpreted correctly.")
class CreateTimesheetClockOutEntryRequest(StrictModel):
    """Records a clock-out entry for a currently clocked-in employee, defaulting to the current server time. To log a historical clock-out, supply a date, end time, and timezone."""
    path: CreateTimesheetClockOutEntryRequestPath
    body: CreateTimesheetClockOutEntryRequestBody | None = None

# Operation: bulk_upsert_clock_entries
class CreateOrUpdateTimesheetClockEntriesRequestBody(StrictModel):
    entries: list[ClockEntrySchema] = Field(default=..., description="Array of one or more clock entry objects to create or update. Each entry without an ID will be created as a new record; each entry with an existing ID will update the matching record. Must contain at least one entry.", min_length=1)
class CreateOrUpdateTimesheetClockEntriesRequest(StrictModel):
    """Creates new timesheet clock entries or updates existing ones in a single bulk operation. Entries containing an existing ID are updated; entries without an ID are created as new records."""
    body: CreateOrUpdateTimesheetClockEntriesRequestBody

# Operation: bulk_upsert_timesheet_entries
class CreateOrUpdateTimesheetHourEntriesRequestBody(StrictModel):
    hours: list[HourEntrySchema] = Field(default=..., description="Array of hour entry objects to create or update. Each entry without an ID will be created as a new record; each entry with an existing ID will update the matching record. Order is not significant.")
class CreateOrUpdateTimesheetHourEntriesRequest(StrictModel):
    """Creates new timesheet hour entries or updates existing ones in a single bulk operation. Entries containing an existing ID are updated; entries without an ID are created as new records."""
    body: CreateOrUpdateTimesheetHourEntriesRequestBody

# Operation: get_webhook
class GetWebhookRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique numeric identifier of the webhook to retrieve.")
class GetWebhookRequest(StrictModel):
    """Retrieves the full configuration of a single webhook owned by the authenticated user, including its name, URL, format, monitored fields, events, and activity timestamps. Returns 403 if the webhook belongs to a different user and 404 if it does not exist."""
    path: GetWebhookRequestPath

# Operation: delete_webhook
class DeleteWebhookRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique numeric identifier of the webhook to delete. Must correspond to a webhook owned by the authenticated API key.")
class DeleteWebhookRequest(StrictModel):
    """Permanently deletes a webhook associated with the authenticated user's API key. Returns 403 if the webhook belongs to a different API key, or 404 if the webhook does not exist."""
    path: DeleteWebhookRequestPath

# Operation: list_webhook_logs
class GetWebhookLogsRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique numeric identifier of the webhook whose delivery logs should be retrieved.")
class GetWebhookLogsRequest(StrictModel):
    """Retrieves recent delivery log entries for a specific webhook, covering the last 14 days and up to 200 entries. Each entry includes the webhook URL, last attempt and success timestamps (UTC datetime or status string), HTTP response code, payload format, and employee IDs in the payload. Note: when the rate limit is exceeded the server returns HTTP 200 with an error object instead of the log array — callers must check for an `error.code` of 429 in the response body before processing results."""
    path: GetWebhookLogsRequestPath

# Operation: query_dataset
class GetDataFromDatasetRequestPath(StrictModel):
    dataset_name: str = Field(default=..., validation_alias="datasetName", serialization_alias="datasetName", description="The unique name of the dataset to query. Use GET /api/v1/datasets to discover available dataset names.")
class GetDataFromDatasetRequestQuery(StrictModel):
    page: int | None = Field(default=None, description="The page number to retrieve when paginating through results. Must be 1 or greater; defaults to 1.", ge=1)
    page_size: int | None = Field(default=None, description="The number of records to return per page. Must be between 1 and 1000; defaults to 500.", ge=1, le=1000)
class GetDataFromDatasetRequestBodyFilters(StrictModel):
    match: str | None = Field(default=None, validation_alias="match", serialization_alias="match", description="A full-text search string used to match records across the dataset.")
    filters: list[GetDataFromDatasetBodyFiltersFiltersItem] | None = Field(default=None, validation_alias="filters", serialization_alias="filters", description="An array of filter conditions to apply to the query. Each filter references a field, an operator, and a value; the filtered field does not need to be included in the fields list. Supported operators vary by field type — for example, options fields use includes or does_not_include with values enclosed in square brackets, and date fields support range and last/next with structured value objects. Use GET /api/v1/datasets/{datasetName}/field-options to retrieve valid filter values.")
class GetDataFromDatasetRequestBody(StrictModel):
    fields: list[str] = Field(default=..., description="The list of field names to include in the response. Use GET /api/v1/datasets/{datasetName}/fields to discover valid field names for the target dataset.")
    aggregations: list[GetDataFromDatasetBodyAggregationsItem] | None = Field(default=None, description="One or more aggregation operations to apply to the result set, each specifying a field and an aggregation function. Supported functions vary by field type: text/bool/options/govIdText support count; date supports count, min, max; int supports count, min, max, sum, avg.")
    sort_by: list[GetDataFromDatasetBodySortByItem] | None = Field(default=None, validation_alias="sortBy", serialization_alias="sortBy", description="An ordered array of sort directives, each specifying a field name and direction. Sort priority follows the order of items in the array, with the first item having the highest priority.")
    group_by: list[str] | None = Field(default=None, validation_alias="groupBy", serialization_alias="groupBy", description="An array containing a single field name by which to group results. Only one field is supported for grouping at a time.")
    show_history: list[str] | None = Field(default=None, validation_alias="showHistory", serialization_alias="showHistory", description="An array of entity names corresponding to historical table fields whose full history should be included in the response. Use the entity name values returned by GET /api/v1/datasets/{datasetName}/fields.")
    filters: GetDataFromDatasetRequestBodyFilters | None = None
class GetDataFromDatasetRequest(StrictModel):
    """Retrieve paginated records from a specified dataset by providing a list of fields to return, with optional filtering, sorting, grouping, and aggregation. Use GET /api/v1/datasets/{datasetName}/fields to discover available field names before calling this endpoint."""
    path: GetDataFromDatasetRequestPath
    query: GetDataFromDatasetRequestQuery | None = None
    body: GetDataFromDatasetRequestBody

# Operation: get_custom_report
class GetByReportIdRequestPath(StrictModel):
    report_id: int = Field(default=..., validation_alias="reportId", serialization_alias="reportId", description="The unique identifier of the saved custom report to retrieve data for.")
class GetByReportIdRequestQuery(StrictModel):
    page: int | None = Field(default=None, description="The page number to retrieve when paginating through results. Must be 1 or greater.", ge=1)
    page_size: int | None = Field(default=None, description="The number of records to return per page. Must be between 1 and 1000 inclusive; defaults to 500.", ge=1, le=1000)
class GetByReportIdRequest(StrictModel):
    """Retrieve paginated data for a specific saved custom report by its ID, using the report's stored field list and filter configuration. Use list_custom_reports to discover available report IDs."""
    path: GetByReportIdRequestPath
    query: GetByReportIdRequestQuery | None = None

# Operation: list_dataset_fields
class GetFieldsFromDatasetRequestPath(StrictModel):
    dataset_name: str = Field(default=..., validation_alias="datasetName", serialization_alias="datasetName", description="The unique machine-readable name of the dataset whose fields you want to retrieve.")
class GetFieldsFromDatasetRequestQuery(StrictModel):
    page: int | None = Field(default=None, description="The page number to retrieve when navigating paginated results; must be 1 or greater.", ge=1)
    page_size: int | None = Field(default=None, description="The number of field records to return per page; must be between 1 and 1000 inclusive.", ge=1, le=1000)
class GetFieldsFromDatasetRequest(StrictModel):
    """Retrieves the available fields for a specified dataset, returning paginated field descriptors that include each field's machine-readable name, human-readable label, parent section type and name, and entity name. Use the returned field `name` values when constructing field selections in POST /api/v1/datasets/{datasetName} queries. Note: this endpoint is deprecated — prefer GET /api/v1_2/datasets/{datasetName}/fields."""
    path: GetFieldsFromDatasetRequestPath
    query: GetFieldsFromDatasetRequestQuery | None = None

# Operation: list_custom_reports
class ListReportsRequestQuery(StrictModel):
    page: int | None = Field(default=None, description="The page number to retrieve when paginating through results, starting at page 1.", ge=1)
    page_size: int | None = Field(default=None, description="The number of records to return per page, between 1 and 1000. Defaults to 500 if not specified.", ge=1, le=1000)
class ListReportsRequest(StrictModel):
    """Retrieve a paginated list of saved custom reports available in the account, returning each report's ID and name. Use the returned report ID with the get_custom_report operation to fetch full report data."""
    query: ListReportsRequestQuery | None = None

# Operation: get_field_options
class GetFieldOptionsRequestPath(StrictModel):
    dataset_name: str = Field(default=..., validation_alias="datasetName", serialization_alias="datasetName", description="The name of the dataset whose field options you want to retrieve.")
class GetFieldOptionsRequestBody(StrictModel):
    fields: list[str] = Field(default=..., description="One or more field names whose possible values should be returned; order is not significant and each entry should be a valid field name within the dataset.")
    dependent_fields: dict[str, list[GetFieldOptionsBodyDependentFieldsValueItem]] | None = Field(default=None, validation_alias="dependentFields", serialization_alias="dependentFields", description="A map of field names to dependent field-value pairs that constrain the options returned for those fields, used when one field's valid options depend on the selected value of another field.")
    filters: dict[str, Any] | None = Field(default=None, description="An optional filter object that scopes the returned options to only those that exist for records matching the specified conditions, such as limiting options to those applicable to active employees.")
class GetFieldOptionsRequest(StrictModel):
    """Retrieve the available filter values for one or more fields in a dataset, returning an object keyed by field name where each value is an array of id/value pairs. Use the returned id values when constructing filters for dataset queries."""
    path: GetFieldOptionsRequestPath
    body: GetFieldOptionsRequestBody

# Operation: list_dataset_fields_v1_2
class GetFieldsFromDatasetV12RequestPath(StrictModel):
    dataset_name: str = Field(default=..., validation_alias="datasetName", serialization_alias="datasetName", description="The machine-readable name of the dataset whose fields you want to retrieve.")
class GetFieldsFromDatasetV12RequestQuery(StrictModel):
    page: int | None = Field(default=None, description="The page number to retrieve for paginated results; must be 1 or greater.", ge=1)
    page_size: int | None = Field(default=None, description="The number of field records to return per page; must be between 1 and 1000 inclusive.", ge=1, le=1000)
class GetFieldsFromDatasetV12Request(StrictModel):
    """Retrieve the available fields for a specified dataset, returning paginated field descriptors that include each field's machine-readable name, human-readable label, parent section, and entity name. Use the returned field `name` values when constructing data queries against the dataset."""
    path: GetFieldsFromDatasetV12RequestPath
    query: GetFieldsFromDatasetV12RequestQuery | None = None

# Operation: get_field_options_rfc7807
class GetFieldOptionsV12RequestPath(StrictModel):
    dataset_name: str = Field(default=..., validation_alias="datasetName", serialization_alias="datasetName", description="The name of the dataset whose field options you want to retrieve.")
class GetFieldOptionsV12RequestBody(StrictModel):
    fields: list[str] = Field(default=..., description="One or more field names whose possible values should be returned; order is not significant and each entry should be a valid field name within the dataset.")
    dependent_fields: dict[str, list[GetFieldOptionsV12BodyDependentFieldsValueItem]] | None = Field(default=None, validation_alias="dependentFields", serialization_alias="dependentFields", description="A map of field names to dependent field/value pairs that constrain the options returned for those fields, used when one field's valid options depend on the selected value of another field.")
    filters: dict[str, Any] | None = Field(default=None, description="An optional filter object that scopes the returned options to only those consistent with the specified field conditions, using match mode and a list of field/operator/value filter rules.")
class GetFieldOptionsV12Request(StrictModel):
    """Retrieve the available filter values for one or more fields in a dataset, returning an object keyed by field name where each value is an array of id/value pairs. Use the returned id values when constructing filters for dataset queries."""
    path: GetFieldOptionsV12RequestPath
    body: GetFieldOptionsV12RequestBody

# Operation: list_applications
class GetApplicationsRequestQuery(StrictModel):
    page: int | None = Field(default=None, description="The page number to retrieve for paginated results.")
    job_id: int | None = Field(default=None, validation_alias="jobId", serialization_alias="jobId", description="Filters results to only applications associated with the specified job ID.")
    application_status_id: str | None = Field(default=None, validation_alias="applicationStatusId", serialization_alias="applicationStatusId", description="Filters results to applications matching one or more specific application status IDs, provided as a comma-separated list of numeric IDs.")
    application_status: str | None = Field(default=None, validation_alias="applicationStatus", serialization_alias="applicationStatus", description="Filters results by one or more high-level application status group codes, provided as a comma-separated list. Use ALL to return all statuses, ALL_ACTIVE for any active state, or specific codes such as NEW, ACTIVE, INACTIVE, or HIRED.")
    job_status_groups: str | None = Field(default=None, validation_alias="jobStatusGroups", serialization_alias="jobStatusGroups", description="Filters results by one or more job position status groups, provided as a comma-separated list. Use ALL to include every status, or target specific states such as Open, Filled, Draft, Deleted, On Hold, or Canceled.")
    search_string: str | None = Field(default=None, validation_alias="searchString", serialization_alias="searchString", description="A general keyword or search string used to find matching applications across relevant fields such as applicant name or job title.")
    sort_by: Literal["first_name", "job_title", "rating", "phone", "status", "last_updated", "created_date"] | None = Field(default=None, validation_alias="sortBy", serialization_alias="sortBy", description="The field by which to sort the returned applications.")
    sort_order: Literal["ASC", "DESC"] | None = Field(default=None, validation_alias="sortOrder", serialization_alias="sortOrder", description="The direction in which to sort results — ascending (ASC) or descending (DESC).")
    new_since: str | None = Field(default=None, validation_alias="newSince", serialization_alias="newSince", description="Restricts results to applications submitted after the specified UTC timestamp. Must follow the format Y-m-d H:i:s.")
class GetApplicationsRequest(StrictModel):
    """Retrieve a paginated list of job applications from the Applicant Tracking System (ATS). Supports filtering by job, application status, position status, and submission date, with flexible sorting options."""
    query: GetApplicationsRequestQuery | None = None

# Operation: create_candidate
class CreateCandidateRequestBody(StrictModel):
    first_name: str = Field(default=..., validation_alias="firstName", serialization_alias="firstName", description="The candidate's first name.")
    last_name: str = Field(default=..., validation_alias="lastName", serialization_alias="lastName", description="The candidate's last name.")
    email: str | None = Field(default=None, description="The candidate's email address, used for communication and deduplication.", json_schema_extra={'format': 'email'})
    phone_number: str | None = Field(default=None, validation_alias="phoneNumber", serialization_alias="phoneNumber", description="The candidate's phone number, including country code if applicable.")
    source: str | None = Field(default=None, description="The channel or platform through which the candidate was sourced, such as a job board or professional network.")
    job_id: int = Field(default=..., validation_alias="jobId", serialization_alias="jobId", description="The unique identifier of the job opening this application is being submitted for.")
    address: str | None = Field(default=None, description="The candidate's street address.")
    city: str | None = Field(default=None, description="The city of the candidate's address.")
    state: str | None = Field(default=None, description="The state or province of the candidate's address; accepts full name, abbreviation, or ISO code.")
    zip_: str | None = Field(default=None, validation_alias="zip", serialization_alias="zip", description="The zip or postal code of the candidate's address.")
    country: str | None = Field(default=None, description="The country of the candidate's address; accepts full country name or ISO country code.")
    linkedin_url: str | None = Field(default=None, validation_alias="linkedinUrl", serialization_alias="linkedinUrl", description="The candidate's LinkedIn profile URL; must be a valid LinkedIn URL matching the required domain pattern.", json_schema_extra={'format': 'uri'})
    date_available: str | None = Field(default=None, validation_alias="dateAvailable", serialization_alias="dateAvailable", description="The date the candidate is available to start, in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    desired_salary: str | None = Field(default=None, validation_alias="desiredSalary", serialization_alias="desiredSalary", description="The candidate's desired compensation or salary expectation.")
    referred_by: str | None = Field(default=None, validation_alias="referredBy", serialization_alias="referredBy", description="The name of the person or organization that referred the candidate.")
    website_url: str | None = Field(default=None, validation_alias="websiteUrl", serialization_alias="websiteUrl", description="The URL of the candidate's personal website, blog, or online portfolio; must be a valid URL.", json_schema_extra={'format': 'uri'})
    highest_education: Literal["GED or Equivalent", "High School", "Some College", "College - Associates", "College - Bachelor of Arts", "College - Bachelor of Fine Arts", "College - Bachelor of Science", "College - Master of Arts", "College - Master of Fine Arts", "College - Master of Science", "College - Master of Business Administration", "College - Doctorate", "Medical Doctor", "Other"] | None = Field(default=None, validation_alias="highestEducation", serialization_alias="highestEducation", description="The highest level of education the candidate has completed; must match one of the predefined education level values.")
    college_name: str | None = Field(default=None, validation_alias="collegeName", serialization_alias="collegeName", description="The name of the college or university the candidate attended.")
    references: str | None = Field(default=None, description="Professional or personal references provided by the candidate.")
    resume: str | None = Field(default=None, description="The candidate's resume file; accepted formats include PDF, Word documents, plain text, RTF, and common image types.", json_schema_extra={'format': 'binary'})
    cover_letter: str | None = Field(default=None, validation_alias="coverLetter", serialization_alias="coverLetter", description="The candidate's cover letter file; accepted formats include PDF, Word documents, plain text, RTF, and common image types.", json_schema_extra={'format': 'binary'})
class CreateCandidateRequest(StrictModel):
    """Submit a new candidate application for a specific job opening in the Applicant Tracking System. Requires ATS settings access; only fields mandated by the target job's standard questions need to be provided beyond the three required fields."""
    body: CreateCandidateRequestBody

# Operation: create_job_opening
class CreateJobOpeningRequestBody(StrictModel):
    posting_title: str = Field(default=..., validation_alias="postingTitle", serialization_alias="postingTitle", description="The public-facing title of the job opening as it will appear in postings.")
    job_status: Literal["Draft", "Open", "On Hold", "Filled", "Canceled"] = Field(default=..., validation_alias="jobStatus", serialization_alias="jobStatus", description="The current workflow status of the job opening, controlling its visibility and availability in the hiring pipeline.")
    hiring_lead: int = Field(default=..., validation_alias="hiringLead", serialization_alias="hiringLead", description="The employee ID of the person responsible for leading the hiring process, obtained from the list_hiring_leads endpoint.")
    department: str | None = Field(default=None, description="The name of the department this job opening belongs to within the organization.")
    employment_type: str = Field(default=..., validation_alias="employmentType", serialization_alias="employmentType", description="The employment arrangement type for the role, such as full-time, part-time, or contractor.")
    minimum_experience: Literal["Entry-level", "Mid-level", "Experienced", "Manager/Supervisor", "Senior Manager/Supervisor'", "Executive", "Senior Executive"] | None = Field(default=None, validation_alias="minimumExperience", serialization_alias="minimumExperience", description="The minimum career experience level required for a candidate to qualify for this role.")
    compensation: str | None = Field(default=None, description="The pay rate or compensation package details for the job opening, such as salary range or hourly rate.")
    job_location: int | None = Field(default=None, validation_alias="jobLocation", serialization_alias="jobLocation", description="The location ID for the job's physical workplace, obtained from the list_company_locations endpoint. Omit for fully remote positions; required when locationType is 0 (on-site) or 2 (hybrid).")
    job_description: str = Field(default=..., validation_alias="jobDescription", serialization_alias="jobDescription", description="The full descriptive text of the job opening, including responsibilities, qualifications, and any other relevant details presented to applicants.")
    application_question_resume: Literal["true", "false", "Required"] | None = Field(default=None, validation_alias="applicationQuestionResume", serialization_alias="applicationQuestionResume", description="Controls whether the resume upload field appears on the application form: hidden, optional, or mandatory.")
    application_question_address: Literal["true", "false", "Required"] | None = Field(default=None, validation_alias="applicationQuestionAddress", serialization_alias="applicationQuestionAddress", description="Controls whether the address field appears on the application form: hidden, optional, or mandatory.")
    application_question_linkedin_url: Literal["true", "false", "Required"] | None = Field(default=None, validation_alias="applicationQuestionLinkedinUrl", serialization_alias="applicationQuestionLinkedinUrl", description="Controls whether the LinkedIn profile URL field appears on the application form: hidden, optional, or mandatory.")
    application_question_date_available: Literal["true", "false", "Required"] | None = Field(default=None, validation_alias="applicationQuestionDateAvailable", serialization_alias="applicationQuestionDateAvailable", description="Controls whether the availability start date field appears on the application form: hidden, optional, or mandatory.")
    application_question_desired_salary: Literal["true", "false", "Required"] | None = Field(default=None, validation_alias="applicationQuestionDesiredSalary", serialization_alias="applicationQuestionDesiredSalary", description="Controls whether the desired salary field appears on the application form: hidden, optional, or mandatory.")
    application_question_cover_letter: Literal["true", "false", "Required"] | None = Field(default=None, validation_alias="applicationQuestionCoverLetter", serialization_alias="applicationQuestionCoverLetter", description="Controls whether the cover letter upload field appears on the application form: hidden, optional, or mandatory.")
    application_question_referred_by: Literal["true", "false", "Required"] | None = Field(default=None, validation_alias="applicationQuestionReferredBy", serialization_alias="applicationQuestionReferredBy", description="Controls whether the referral source field appears on the application form: hidden, optional, or mandatory.")
    application_question_website_url: Literal["true", "false", "Required"] | None = Field(default=None, validation_alias="applicationQuestionWebsiteUrl", serialization_alias="applicationQuestionWebsiteUrl", description="Controls whether the personal or portfolio website URL field appears on the application form: hidden, optional, or mandatory.")
    application_question_highest_education: Literal["true", "false", "Required"] | None = Field(default=None, validation_alias="applicationQuestionHighestEducation", serialization_alias="applicationQuestionHighestEducation", description="Controls whether the highest education level field appears on the application form: hidden, optional, or mandatory.")
    application_question_college: Literal["true", "false", "Required"] | None = Field(default=None, validation_alias="applicationQuestionCollege", serialization_alias="applicationQuestionCollege", description="Controls whether the college or university attended field appears on the application form: hidden, optional, or mandatory.")
    application_question_references: Literal["true", "false", "Required"] | None = Field(default=None, validation_alias="applicationQuestionReferences", serialization_alias="applicationQuestionReferences", description="Controls whether the professional references field appears on the application form: hidden, optional, or mandatory.")
    internal_job_code: str | None = Field(default=None, validation_alias="internalJobCode", serialization_alias="internalJobCode", description="An internal identifier or code used by your organization to track or categorize this job opening.")
    location_type: Literal[0, 1, 2] | None = Field(default=None, validation_alias="locationType", serialization_alias="locationType", description="Specifies the work arrangement type: 0 = on-site (requires jobLocation), 1 = fully remote (no jobLocation), 2 = hybrid (requires jobLocation). Defaults to 1 when no jobLocation is provided, or 0 when jobLocation is provided.")
class CreateJobOpeningRequest(StrictModel):
    """Creates a new job opening in the Applicant Tracking System (ATS). Requires ATS settings access; use the list_company_locations and list_hiring_leads endpoints to retrieve valid IDs for location and hiring lead fields. Returns the new job opening ID on success."""
    body: CreateJobOpeningRequestBody

# Operation: list_employee_benefits
class ListEmployeeBenefitsRequestBodyFilters(StrictModel):
    employee_id: int | None = Field(default=None, validation_alias="employeeId", serialization_alias="employeeId", description="Filters results to benefit enrollments belonging to a specific employee, identified by their unique numeric ID.")
    company_benefit_id: int | None = Field(default=None, validation_alias="companyBenefitId", serialization_alias="companyBenefitId", description="Filters results to enrollments associated with a specific company benefit plan, identified by its unique numeric ID.")
    enrollment_status_effective_date: str | None = Field(default=None, validation_alias="enrollmentStatusEffectiveDate", serialization_alias="enrollmentStatusEffectiveDate", description="Filters results to enrollments whose status became effective on the specified date, provided in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
class ListEmployeeBenefitsRequestBody(StrictModel):
    """Filters to scope the results. The filters object is required and must include at least one filter field."""
    filters: ListEmployeeBenefitsRequestBodyFilters | None = None
class ListEmployeeBenefitsRequest(StrictModel):
    """Retrieves current and future benefit enrollment records for one or more employees, grouped by employee, including plan details, enrollment status, deduction amounts, and cost-sharing information. At least one filter — employee ID, company benefit plan ID, or enrollment status effective date — must be provided."""
    body: ListEmployeeBenefitsRequestBody | None = None

# Operation: list_member_benefits
class GetMemberBenefitsRequestQuery(StrictModel):
    calendar_year: str = Field(default=..., validation_alias="calendarYear", serialization_alias="calendarYear", description="The four-digit calendar year for which to retrieve benefit enrollment data, in YYYY format.", pattern='^\\d{4}$')
    page: str | None = Field(default=None, description="The 1-based page number to retrieve; values that resolve to zero or below are rejected with a 400. Defaults to 1.")
    page_size: str | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="The number of benefit records to return per page; must resolve to an integer between 1 and 99 inclusive, otherwise a 400 is returned. Defaults to 25.")
class GetMemberBenefitsRequest(StrictModel):
    """Retrieves a paginated list of benefit enrollment records for all members (employees and dependents) in the company for a specified calendar year, including each member's plans and enrollment status date ranges. Requires benefit admin privileges; non-admin callers receive a 403."""
    query: GetMemberBenefitsRequestQuery

# Operation: list_employees
class ListEmployeesRequestQuery(StrictModel):
    filter_: GetEmployeesFilterRequestObject | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Narrows results to employees matching the specified field criteria, encoded as a deepObject. Employees for which the caller lacks permission to view the filtered field are excluded entirely from results.")
    sort: str | None = Field(default=None, description="Comma-separated list of fields to sort by, where a leading hyphen indicates descending order; sortable fields are limited to the core default set. Employees for which the caller lacks permission to view the sort field are excluded from results, and nulls sort first ascending and last descending.")
    fields: str | None = Field(default=None, description="Comma-separated list of additional contact or social fields to include beyond the default set, up to 14 supported values. Unrecognized field names are silently ignored, and fields the caller lacks permission to view will be null or omitted with the field name listed in the record's `_restrictedFields` array.")
    page: CursorPaginationQueryObject | None = Field(default=None, description="Cursor-based pagination control accepting `limit`, `after`, and `before` parameters to navigate through result pages.")
class ListEmployeesRequest(StrictModel):
    """Retrieves a paginated list of employees, each including core identity and job fields by default, with optional filtering, sorting, and additional contact or social fields. Use the Get Employee endpoint or Datasets API for more comprehensive field coverage."""
    query: ListEmployeesRequestQuery | None = None

# Operation: create_employee
class CreateEmployeeRequestBody(StrictModel):
    first_name: str = Field(default=..., validation_alias="firstName", serialization_alias="firstName", description="Employee's legal first name as it should appear on official records and payroll documents.")
    last_name: str = Field(default=..., validation_alias="lastName", serialization_alias="lastName", description="Employee's legal last name as it should appear on official records and payroll documents.")
    work_email: str | None = Field(default=None, validation_alias="workEmail", serialization_alias="workEmail", description="Employee's work email address used for company communications and system access.")
    job_title: str | None = Field(default=None, validation_alias="jobTitle", serialization_alias="jobTitle", description="Employee's job title reflecting their role or position within the organization.")
    department: str | None = Field(default=None, description="Name of the department the employee belongs to; must match an existing department name in the system.")
    hire_date: str | None = Field(default=None, validation_alias="hireDate", serialization_alias="hireDate", description="The date the employee was officially hired, formatted as a calendar date in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
class CreateEmployeeRequest(StrictModel):
    """Creates a new employee record with at minimum a first and last name; additional fields such as payroll, contact, and job details can be included using any valid employee field name discoverable via the list-fields endpoint. Employees added to a Trax Payroll-synced pay schedule require a full set of payroll-related fields including SSN/EIN, compensation, and location details."""
    body: CreateEmployeeRequestBody

# Operation: update_employee_table_row
class UpdateTableRowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the employee whose table row will be updated.")
    table: str = Field(default=..., description="The name of the employee table containing the row to update, such as job information or compensation tables.")
    row_id: str = Field(default=..., validation_alias="rowId", serialization_alias="rowId", description="The unique identifier of the specific row within the table to be updated.")
class UpdateTableRowRequestBody(StrictModel):
    date: str | None = Field(default=None, description="The effective date for the row update in YYYY-MM-DD format, determining when the change takes effect.", json_schema_extra={'format': 'date'})
    location: str | None = Field(default=None, description="The office or work location value to assign to this row.")
    division: str | None = Field(default=None, description="The organizational division value to assign to this row.")
    department: str | None = Field(default=None, description="The department value to assign to this row.")
    job_title: str | None = Field(default=None, validation_alias="jobTitle", serialization_alias="jobTitle", description="The job title value to assign to this row.")
    reports_to: str | None = Field(default=None, validation_alias="reportsTo", serialization_alias="reportsTo", description="The identifier of the manager or supervisor this employee reports to for this row.")
    teams: list[str] | None = Field(default=None, description="A list of team identifiers or names associated with this row; order is not significant and each item represents a single team assignment.")
class UpdateTableRowRequest(StrictModel):
    """Updates an existing row in a specified employee table by submitting one or more field name/value pairs to modify. Targets a specific row by ID within tables such as job information or compensation history."""
    path: UpdateTableRowRequestPath
    body: UpdateTableRowRequestBody | None = None

# Operation: delete_employee_table_row
class DeleteEmployeeTableRowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the employee whose tabular data is being modified.")
    table: str = Field(default=..., description="The name of the tabular dataset from which the row will be deleted, such as job history, compensation records, or a custom tabular field.")
    row_id: str = Field(default=..., validation_alias="rowId", serialization_alias="rowId", description="The unique identifier of the specific row to delete within the targeted table.")
class DeleteEmployeeTableRowRequest(StrictModel):
    """Permanently removes a specific row from a named tabular dataset associated with an employee. Deletion will fail if the row has pending approval changes (409) or is tied to an active pay schedule (412)."""
    path: DeleteEmployeeTableRowRequestPath

# Operation: download_company_file
class GetCompanyFileRequestPath(StrictModel):
    file_id: int = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the company file to download.")
class GetCompanyFileRequest(StrictModel):
    """Downloads the raw content of a company file by its ID, with the response including the appropriate MIME type and original filename as an attachment. Access is granted if the file or its category is shared with employees, shared directly with the requesting user, or the user holds view permission on the file section."""
    path: GetCompanyFileRequestPath

# Operation: update_company_file
class UpdateCompanyFileRequestPath(StrictModel):
    file_id: int = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the company file to update.")
class UpdateCompanyFileRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new display name to assign to the file.")
    category_id: str | None = Field(default=None, validation_alias="categoryId", serialization_alias="categoryId", description="The identifier of the category (file section) to move the file into.")
    share_with_employee: Literal["yes", "no"] | None = Field(default=None, validation_alias="shareWithEmployee", serialization_alias="shareWithEmployee", description="Controls whether the file is visible and accessible to employees; set to 'yes' to share or 'no' to restrict access.")
class UpdateCompanyFileRequest(StrictModel):
    """Updates metadata for an existing company file, including its display name, category, and employee visibility. Only fields included in the request body are modified; omitted fields remain unchanged."""
    path: UpdateCompanyFileRequestPath
    body: UpdateCompanyFileRequestBody | None = None

# Operation: delete_company_file
class DeleteCompanyFileRequestPath(StrictModel):
    file_id: int = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique numeric identifier of the company file to delete. Must correspond to an existing file the caller has write access to.")
class DeleteCompanyFileRequest(StrictModel):
    """Permanently deletes a company file by its unique identifier. Requires write access to company files; returns 404 if the file is not found or 403 if the caller lacks sufficient permissions."""
    path: DeleteCompanyFileRequestPath

# Operation: download_employee_file
class GetEmployeeFileRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The numeric ID of the employee whose file is being downloaded. Pass 0 to automatically resolve to the employee associated with the API key.")
    file_id: int = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The numeric ID of the specific file to download from the employee's record.")
class GetEmployeeFileRequest(StrictModel):
    """Downloads the binary content of a specific file attached to an employee record, returning it as an attachment with the appropriate MIME type. Returns 403 if access to the employee or file section is denied, and 404 if the file does not exist or is archived."""
    path: GetEmployeeFileRequestPath

# Operation: update_employee_file
class UpdateEmployeeFileRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the employee whose file is being updated.")
    file_id: int = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the employee file to update.")
class UpdateEmployeeFileRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new display name to assign to the file. Omit this field to leave the current name unchanged.")
    category_id: int | None = Field(default=None, validation_alias="categoryId", serialization_alias="categoryId", description="The ID of the file category (section) to move the file into. Omit this field to leave the file in its current category.")
    share_with_employee: Literal["yes", "no"] | None = Field(default=None, validation_alias="shareWithEmployee", serialization_alias="shareWithEmployee", description="Controls whether the file is visible to the employee. Accepts 'yes' to share or 'no' to hide; also accepted as 'shareWithEmployees'.")
class UpdateEmployeeFileRequest(StrictModel):
    """Updates metadata for an existing employee file, supporting renaming, category reassignment, and toggling employee visibility. Only fields included in the request body are modified; omitted fields remain unchanged."""
    path: UpdateEmployeeFileRequestPath
    body: UpdateEmployeeFileRequestBody | None = None

# Operation: delete_employee_file
class DeleteEmployeeFileRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The numeric ID of the employee whose file will be deleted. Pass 0 to automatically resolve to the employee associated with the API key.")
    file_id: int = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The numeric ID of the specific file to delete from the employee's record.")
class DeleteEmployeeFileRequest(StrictModel):
    """Permanently deletes a specific file associated with an employee record. Returns 200 even if the file was already deleted (idempotent), 404 if the file is not linked to the specified employee, and 403 if the caller lacks permission or the file is managed by BambooPayroll."""
    path: DeleteEmployeeFileRequestPath

# Operation: list_employee_goals
class ListGoalsRequestPath(StrictModel):
    employee_id: str = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee whose goals should be retrieved.")
class ListGoalsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Restricts results to goals matching the specified status. Accepted values are `status-inProgress`, `status-completed`, and `status-closed`; if omitted, all goals are returned regardless of status. Unrecognized values may be silently ignored.")
class ListGoalsRequest(StrictModel):
    """Retrieves the list of goals assigned to a specific employee, optionally filtered by goal status. Returns up to 50 goals in a `goals` array."""
    path: ListGoalsRequestPath
    query: ListGoalsRequestQuery | None = None

# Operation: create_employee_goal
class CreateGoalRequestPath(StrictModel):
    employee_id: str = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee for whom the goal is being created.")
class CreateGoalRequestBody(StrictModel):
    title: str = Field(default=..., description="A short, descriptive title for the goal.")
    description: str | None = Field(default=None, description="A detailed explanation of the goal's purpose, expectations, or scope.")
    due_date: str = Field(default=..., validation_alias="dueDate", serialization_alias="dueDate", description="The target completion date for the goal in YYYY-MM-DD format (ISO 8601).", json_schema_extra={'format': 'date'})
    percent_complete: int | None = Field(default=None, validation_alias="percentComplete", serialization_alias="percentComplete", description="How far along the goal is, expressed as a whole number between 0 and 100. Defaults to 0 if not provided. A value of 100 indicates the goal is fully complete and requires a completionDate.", ge=0, le=100)
    completion_date: str | None = Field(default=None, validation_alias="completionDate", serialization_alias="completionDate", description="The date the goal was completed in YYYY-MM-DD format (ISO 8601). Must be provided when percentComplete is set to 100.", json_schema_extra={'format': 'date'})
    shared_with_employee_ids: list[int] = Field(default=..., validation_alias="sharedWithEmployeeIds", serialization_alias="sharedWithEmployeeIds", description="An unordered list of employee IDs who can view this goal. Must include the goal owner's employee ID.")
    aligns_with_option_id: int | None = Field(default=None, validation_alias="alignsWithOptionId", serialization_alias="alignsWithOptionId", description="The identifier of a predefined alignment option that this goal supports, used to link the goal to broader organizational objectives.")
    milestones: list[CreateGoalBodyMilestonesItem] | None = Field(default=None, description="An ordered list of milestone objects that break the goal into smaller steps. Each milestone requires a title field and is tracked independently.")
class CreateGoalRequest(StrictModel):
    """Creates a new performance goal for a specified employee, including due dates, completion tracking, milestones, and sharing with other employees."""
    path: CreateGoalRequestPath
    body: CreateGoalRequestBody

# Operation: delete_employee_goal
class DeleteGoalRequestPath(StrictModel):
    employee_id: str = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee whose goal is being deleted.")
    goal_id: str = Field(default=..., validation_alias="goalId", serialization_alias="goalId", description="The unique identifier of the goal to permanently delete, which must belong to the specified employee.")
class DeleteGoalRequest(StrictModel):
    """Permanently deletes a specific goal associated with an employee. The goal must belong to the specified employee; returns 204 with no response body on success."""
    path: DeleteGoalRequestPath

# Operation: update_goal_progress
class UpdateGoalProgressRequestPath(StrictModel):
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee whose goal progress is being updated.")
    goal_id: int = Field(default=..., validation_alias="goalId", serialization_alias="goalId", description="The unique identifier of the goal to update for the specified employee.")
class UpdateGoalProgressRequestBody(StrictModel):
    """The updated progress for the goal. Provide percentComplete (0-100) and optionally a completionDate when percentComplete is 100."""
    percent_complete: int = Field(default=..., validation_alias="percentComplete", serialization_alias="percentComplete", description="The current completion percentage of the goal, expressed as a whole number between 0 (not started) and 100 (fully complete).", ge=0, le=100)
    completion_date: str | None = Field(default=None, validation_alias="completionDate", serialization_alias="completionDate", description="The date the goal was completed in YYYY-MM-DD format. Must be provided when percentComplete is 100.", json_schema_extra={'format': 'date'})
class UpdateGoalProgressRequest(StrictModel):
    """Updates the completion percentage of a specific employee goal, optionally recording the completion date when the goal is fully achieved."""
    path: UpdateGoalProgressRequestPath
    body: UpdateGoalProgressRequestBody

# Operation: update_milestone_progress
class UpdateGoalMilestoneProgressRequestPath(StrictModel):
    employee_id: str = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee whose goal milestone is being updated.")
    goal_id: str = Field(default=..., validation_alias="goalId", serialization_alias="goalId", description="The unique identifier of the goal that contains the milestone to be updated.")
    milestone_id: str = Field(default=..., validation_alias="milestoneId", serialization_alias="milestoneId", description="The unique identifier of the milestone whose progress is being updated.")
class UpdateGoalMilestoneProgressRequestBody(StrictModel):
    complete: bool = Field(default=..., description="Indicates whether the milestone has been completed. Set to true to mark the milestone as complete, or false to mark it as incomplete.")
class UpdateGoalMilestoneProgressRequest(StrictModel):
    """Updates the completion status of a specific milestone within an employee's goal. Use this to mark a milestone as complete or incomplete as part of tracking goal progress."""
    path: UpdateGoalMilestoneProgressRequestPath
    body: UpdateGoalMilestoneProgressRequestBody

# Operation: set_goal_sharing
class UpdateGoalSharingRequestPath(StrictModel):
    employee_id: str = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee who owns the goal.")
    goal_id: str = Field(default=..., validation_alias="goalId", serialization_alias="goalId", description="The unique identifier of the goal whose sharing list will be replaced.")
class UpdateGoalSharingRequestBody(StrictModel):
    """Employee IDs of employees with whom the goal is shared. All goal owners are considered "shared with"."""
    shared_with_employee_ids: list[int] | None = Field(default=None, validation_alias="sharedWithEmployeeIds", serialization_alias="sharedWithEmployeeIds", description="The complete, replacement list of employee IDs with whom the goal should be shared. Must include the goal owner's employee ID; order is not significant.")
class UpdateGoalSharingRequest(StrictModel):
    """Replaces the complete list of employees a goal is shared with, overwriting any previous sharing configuration. The goal owner's employee ID must be included in the updated list."""
    path: UpdateGoalSharingRequestPath
    body: UpdateGoalSharingRequestBody | None = None

# Operation: list_goal_share_options
class ListGoalShareOptionsRequestPath(StrictModel):
    employee_id: str = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee whose goal sharing options are being retrieved.")
class ListGoalShareOptionsRequestQuery(StrictModel):
    search: str = Field(default=..., description="A search term to filter the returned employees by name, employee ID, or email address. Must be provided to return results.")
    limit: int | None = Field(default=None, description="Maximum number of employees to include in the response. Accepts values between 1 and 100, defaulting to 10 if not specified.", ge=1, le=100)
class ListGoalShareOptionsRequest(StrictModel):
    """Retrieves a list of employees with whom the specified employee's goals can be shared. Results are filtered by a search term matching name, employee ID, or email."""
    path: ListGoalShareOptionsRequestPath
    query: ListGoalShareOptionsRequestQuery

# Operation: list_goal_comments
class ListGoalCommentsRequestPath(StrictModel):
    employee_id: str = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee whose goal comments are being retrieved.")
    goal_id: str = Field(default=..., validation_alias="goalId", serialization_alias="goalId", description="The unique identifier of the goal for which comments are being listed, scoped to the specified employee.")
class ListGoalCommentsRequest(StrictModel):
    """Retrieves all comments associated with a specific goal for a given employee. Useful for reviewing feedback, progress notes, and discussion threads tied to a performance goal."""
    path: ListGoalCommentsRequestPath

# Operation: add_goal_comment
class CreateGoalCommentRequestPath(StrictModel):
    employee_id: str = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee who owns the goal.")
    goal_id: str = Field(default=..., validation_alias="goalId", serialization_alias="goalId", description="The unique identifier of the goal on which the comment will be created.")
class CreateGoalCommentRequestBody(StrictModel):
    text: str = Field(default=..., description="The text content of the comment to be added to the goal.")
class CreateGoalCommentRequest(StrictModel):
    """Adds a new comment to a specific goal belonging to the given employee. Returns the newly created comment object, including its assigned ID."""
    path: CreateGoalCommentRequestPath
    body: CreateGoalCommentRequestBody

# Operation: update_goal_comment
class UpdateGoalCommentRequestPath(StrictModel):
    employee_id: str = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="Unique identifier of the employee whose goal contains the comment to be updated.")
    goal_id: str = Field(default=..., validation_alias="goalId", serialization_alias="goalId", description="Unique identifier of the goal associated with the specified employee that contains the comment.")
    comment_id: str = Field(default=..., validation_alias="commentId", serialization_alias="commentId", description="Unique identifier of the comment to be updated, which must belong to the specified goal.")
class UpdateGoalCommentRequestBody(StrictModel):
    text: str = Field(default=..., description="The new text content to replace the existing comment body.")
class UpdateGoalCommentRequest(StrictModel):
    """Updates the text of an existing comment on a specific employee goal. The comment, goal, and employee must all be correctly associated for the update to succeed."""
    path: UpdateGoalCommentRequestPath
    body: UpdateGoalCommentRequestBody

# Operation: delete_goal_comment
class DeleteGoalCommentRequestPath(StrictModel):
    employee_id: str = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="Unique identifier of the employee whose goal contains the comment to be deleted.")
    goal_id: str = Field(default=..., validation_alias="goalId", serialization_alias="goalId", description="Unique identifier of the goal associated with the specified employee that contains the target comment.")
    comment_id: str = Field(default=..., validation_alias="commentId", serialization_alias="commentId", description="Unique identifier of the comment to delete from the specified goal.")
class DeleteGoalCommentRequest(StrictModel):
    """Permanently deletes a specific comment from an employee's goal. The comment must belong to the specified goal, which must be associated with the specified employee. Returns 204 with no response body on success."""
    path: DeleteGoalCommentRequestPath

# Operation: get_goal_aggregate
class GetGoalAggregateRequestPath(StrictModel):
    employee_id: str = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee whose goal is being retrieved.")
    goal_id: str = Field(default=..., validation_alias="goalId", serialization_alias="goalId", description="The unique identifier of the goal for which aggregate information is being fetched.")
class GetGoalAggregateRequest(StrictModel):
    """Retrieves a comprehensive goal detail view for a specific employee, including the goal's comments, alignment options, and a consolidated list of all persons who are shared on or have commented on the goal. Designed to populate a full goal detail view in a single request."""
    path: GetGoalAggregateRequestPath

# Operation: list_goal_alignment_options
class GetAlignableGoalOptionsRequestPath(StrictModel):
    employee_id: str = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee whose alignable goal options are being retrieved.")
class GetAlignableGoalOptionsRequestQuery(StrictModel):
    goal_id: int | None = Field(default=None, validation_alias="goalId", serialization_alias="goalId", description="The ID of the employee's existing goal for which alignment options are being explored. When provided, the goal currently aligned to this goal is included in the results; when omitted, alignment options are returned for the API user.")
class GetAlignableGoalOptionsRequest(StrictModel):
    """Retrieves the list of goals that a specified employee's goal can be aligned with. When a goal ID is provided, the currently aligned goal is included in the results even if it would otherwise be filtered out."""
    path: GetAlignableGoalOptionsRequestPath
    query: GetAlignableGoalOptionsRequestQuery | None = None

# Operation: close_goal
class CloseGoalRequestPath(StrictModel):
    employee_id: str = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee whose goal is being closed.")
    goal_id: str = Field(default=..., validation_alias="goalId", serialization_alias="goalId", description="The unique identifier of the goal to be closed, associated with the specified employee.")
class CloseGoalRequestBody(StrictModel):
    """An optional comment to record when closing the goal."""
    comment: str | None = Field(default=None, description="An optional note to record alongside the goal closure, useful for documenting the reason or context for closing.")
class CloseGoalRequest(StrictModel):
    """Closes an employee's goal by transitioning it to closed status, optionally recording a comment at the time of closure. Note: cascading goals that have visible child goals cannot be closed."""
    path: CloseGoalRequestPath
    body: CloseGoalRequestBody | None = None

# Operation: reopen_goal
class ReopenGoalRequestPath(StrictModel):
    employee_id: str = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee whose goal is being reopened.")
    goal_id: str = Field(default=..., validation_alias="goalId", serialization_alias="goalId", description="The unique identifier of the closed goal to be reopened for the specified employee.")
class ReopenGoalRequest(StrictModel):
    """Reopens a previously closed goal for the specified employee, returning it to in-progress status. Returns the updated goal object reflecting the new status."""
    path: ReopenGoalRequestPath

# Operation: update_goal_with_milestones
class UpdateGoalV11RequestPath(StrictModel):
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee who owns the goal being updated.")
    goal_id: int = Field(default=..., validation_alias="goalId", serialization_alias="goalId", description="The unique identifier of the goal to update, scoped to the specified employee.")
class UpdateGoalV11RequestBody(StrictModel):
    """Required fields: title, sharedWithEmployeeIds, dueDate. Omitted optional fields overwrite existing values using the endpoint's default behavior; see individual field descriptions for details."""
    title: str = Field(default=..., description="The display title of the goal.")
    description: str | None = Field(default=None, description="A detailed narrative description providing additional context or specifics about the goal.")
    due_date: str = Field(default=..., validation_alias="dueDate", serialization_alias="dueDate", description="The target completion date for the goal, provided in YYYY-MM-DD format (ISO 8601 date).", json_schema_extra={'format': 'date'})
    percent_complete: int | None = Field(default=None, validation_alias="percentComplete", serialization_alias="percentComplete", description="The current completion percentage of the goal, expressed as a whole number between 0 and 100. Required when milestones are not enabled for this goal.", ge=0, le=100)
    completion_date: str | None = Field(default=None, validation_alias="completionDate", serialization_alias="completionDate", description="The date the goal was fully completed, provided in YYYY-MM-DD format (ISO 8601 date). Required when percentComplete is set to 100.", json_schema_extra={'format': 'date'})
    shared_with_employee_ids: list[int] = Field(default=..., validation_alias="sharedWithEmployeeIds", serialization_alias="sharedWithEmployeeIds", description="The list of employee IDs who have visibility into this goal. Must include the goal owner's employee ID; order is not significant.")
    aligns_with_option_id: int | None = Field(default=None, validation_alias="alignsWithOptionId", serialization_alias="alignsWithOptionId", description="The identifier of the strategic option or objective this goal is aligned with, linking it to a broader organizational priority.")
    milestones_enabled: bool | None = Field(default=None, validation_alias="milestonesEnabled", serialization_alias="milestonesEnabled", description="When set to true, enables milestone tracking for this goal, allowing progress to be measured through individual milestones rather than a single percent-complete value.")
    deleted_milestone_ids: list[int] | None = Field(default=None, validation_alias="deletedMilestoneIds", serialization_alias="deletedMilestoneIds", description="A list of milestone IDs to permanently remove from this goal. Order is not significant.")
    milestones: list[UpdateGoalV11BodyMilestonesItem] | None = Field(default=None, description="A list of milestone objects to add to this goal. Each item should represent a discrete, trackable step toward goal completion.")
class UpdateGoalV11Request(StrictModel):
    """Updates an existing performance goal for a specified employee, including support for adding, modifying, or deleting milestones within the goal. Use this version (v1.1) instead of v1 when milestone management is required."""
    path: UpdateGoalV11RequestPath
    body: UpdateGoalV11RequestBody

# Operation: get_goal_filters
class GetGoalsFiltersV12RequestPath(StrictModel):
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee whose goal filter counts should be retrieved.")
class GetGoalsFiltersV12Request(StrictModel):
    """Retrieves the count of goals grouped by status for a specific employee, including goals that contain milestones. Use this to understand an employee's goal distribution across statuses before fetching detailed goal data."""
    path: GetGoalsFiltersV12RequestPath

# Operation: get_employee_goals_aggregate
class GetGoalsAggregateV12RequestPath(StrictModel):
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique numeric identifier of the employee whose goals aggregate data should be retrieved.")
class GetGoalsAggregateV12RequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filters the returned goals by status using a filter ID from the filters endpoint. If omitted or an unrecognized value is provided, the API defaults to the first available filter.")
class GetGoalsAggregateV12Request(StrictModel):
    """Retrieves a comprehensive aggregate of all goals for a given employee, including milestone-containing goals, type counts, filter actions, comment counts, and shared employee details. This version extends v1.1 by including goals that contain milestones."""
    path: GetGoalsAggregateV12RequestPath
    query: GetGoalsAggregateV12RequestQuery | None = None

# Operation: get_time_tracking_record
class GetTimeTrackingRecordRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the time tracking record to retrieve, as assigned when the record was originally created.")
class GetTimeTrackingRecordRequest(StrictModel):
    """Retrieves a single time tracking record by its unique ID, returning full details including hours, date, employee, project, task, and shift differential information. Note that project and shiftDifferential fields may be null when not applicable, and missing records may return an empty or null payload rather than a not-found error."""
    path: GetTimeTrackingRecordRequestPath

# Operation: create_time_entry
class CreateTimeTrackingHourRecordRequestBody(StrictModel):
    time_tracking_id: str = Field(default=..., validation_alias="timeTrackingId", serialization_alias="timeTrackingId", description="A caller-supplied unique identifier for this time entry, used to reference the record for future updates or deletions. Accepts any string up to 36 characters, such as a UUID.")
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The numeric ID of the employee for whom hours are being recorded.")
    division_id: int | None = Field(default=None, validation_alias="divisionId", serialization_alias="divisionId", description="The numeric ID of the division to associate with this time entry. Required only when your payroll configuration tracks hours at the division level.")
    department_id: int | None = Field(default=None, validation_alias="departmentId", serialization_alias="departmentId", description="The numeric ID of the department to associate with this time entry. Required only when your payroll configuration tracks hours at the department level.")
    job_title_id: int | None = Field(default=None, validation_alias="jobTitleId", serialization_alias="jobTitleId", description="The numeric ID of the job title to associate with this time entry. Required only when your payroll configuration tracks hours by job title.")
    pay_code: str | None = Field(default=None, validation_alias="payCode", serialization_alias="payCode", description="The payroll provider-specific pay code to classify this time entry. Required only when your payroll provider mandates a pay code.")
    date_hours_worked: str = Field(default=..., validation_alias="dateHoursWorked", serialization_alias="dateHoursWorked", description="The calendar date on which the hours were worked, in ISO 8601 full-date format.")
    pay_rate: float | None = Field(default=None, validation_alias="payRate", serialization_alias="payRate", description="The hourly rate of pay for this entry, expressed as a decimal number. Required only when your payroll provider mandates a pay rate.")
    rate_type: str = Field(default=..., validation_alias="rateType", serialization_alias="rateType", description="Classifies the hours as regular, overtime, or double-time. Must be one of the accepted rate type codes.")
    hours_worked: float = Field(default=..., validation_alias="hoursWorked", serialization_alias="hoursWorked", description="The total number of hours worked for this entry, expressed as a decimal number.")
    job_code: int | None = Field(default=None, validation_alias="jobCode", serialization_alias="jobCode", description="An optional numeric job code to associate with this time entry for payroll or reporting purposes.")
    job_data: str | None = Field(default=None, validation_alias="jobData", serialization_alias="jobData", description="An ordered, comma-delimited list of up to four job numbers (each up to 20 characters, no spaces) to associate with this time entry.")
class CreateTimeTrackingHourRecordRequest(StrictModel):
    """Creates a single time tracking hour record for an employee. Use this endpoint for one-off entries; for bulk imports use the batch upsert endpoint."""
    body: CreateTimeTrackingHourRecordRequestBody

# Operation: upsert_hour_records
class CreateOrUpdateTimeTrackingHourRecordsRequestBody(StrictModel):
    body: list[TimeTrackingRecord] | None = Field(default=None, description="Array of hour record objects to create or update; each item should include the relevant time tracking fields. Order is not significant, but each item's result is returned individually so partial failures can be identified per record.")
class CreateOrUpdateTimeTrackingHourRecordsRequest(StrictModel):
    """Bulk create or update time tracking hour records in a single request. Note that HTTP 201 may be returned even when individual records fail validation — always inspect each item's `success` flag and `response.message` for partial failures."""
    body: CreateOrUpdateTimeTrackingHourRecordsRequestBody | None = None

# Operation: update_time_entry
class UpdateTimeTrackingRecordRequestBody(StrictModel):
    time_tracking_id: str = Field(default=..., validation_alias="timeTrackingId", serialization_alias="timeTrackingId", description="The unique identifier of the time tracking entry to update, up to 36 characters in length (e.g., a UUID).")
    hours_worked: float = Field(default=..., validation_alias="hoursWorked", serialization_alias="hoursWorked", description="The corrected total number of hours worked for this entry. Always provide the full intended value, not a delta — for example, if correcting from 8.0 to 6.0 hours, send 6.0.")
    project_id: int | None = Field(default=None, validation_alias="projectId", serialization_alias="projectId", description="The ID of the project to associate with this time entry. Omit if the project association should remain unchanged or is not applicable.")
    task_id: int | None = Field(default=None, validation_alias="taskId", serialization_alias="taskId", description="The ID of the task to associate with this time entry. Omit if the task association should remain unchanged or is not applicable.")
    shift_differential_id: int | None = Field(default=None, validation_alias="shiftDifferentialId", serialization_alias="shiftDifferentialId", description="The ID of the shift differential to associate with this time entry, used when the entry qualifies for differential pay. Omit if not applicable.")
    holiday_id: int | None = Field(default=None, validation_alias="holidayId", serialization_alias="holidayId", description="The ID of the holiday to associate with this time entry, used when the hours were worked on a recognized holiday. Omit if not applicable.")
class UpdateTimeTrackingRecordRequest(StrictModel):
    """Updates an existing time tracking entry identified by its unique ID. Use this to correct hours worked or reassign the entry to a different project, task, shift differential, or holiday."""
    body: UpdateTimeTrackingRecordRequestBody

# Operation: delete_time_tracking_record
class DeleteTimeTrackingHourRecordRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the time tracking record to delete, up to 36 characters in length (e.g., a UUID). Both not-found and malformed ID values will return a 400 error.")
class DeleteTimeTrackingHourRecordRequest(StrictModel):
    """Permanently deletes a time tracking record and all of its associated revisions by ID. Note that both not-found and invalid ID cases return a 400 invalid-argument response for backward compatibility."""
    path: DeleteTimeTrackingHourRecordRequestPath

# Operation: list_country_states
class GetStatesByCountryIdRequestPath(StrictModel):
    country_id: int = Field(default=..., validation_alias="countryId", serialization_alias="countryId", description="The numeric ID of the country whose states or provinces to retrieve. Obtain valid country IDs from the list_countries operation.")
class GetStatesByCountryIdRequest(StrictModel):
    """Retrieves the list of states or provinces for a given country, sorted alphabetically by abbreviation. Each result includes a numeric ID, abbreviation label, ISO 3166-2 code, and full name."""
    path: GetStatesByCountryIdRequestPath

# Operation: list_timezones
class Op5c5fb0f1211ae1c9451753f92f1053b6RequestQuery(StrictModel):
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="The number of timezone records to return per page. Controls the size of each paginated response.")
    page: int | None = Field(default=None, description="The page number to retrieve within the paginated result set, starting at page 1.")
    sort: str | None = Field(default=None, description="Specifies the sort order of results using OData v4 syntax, allowing ordering by one or more timezone fields in ascending or descending direction.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filters the timezone list using OData v4 filter syntax, enabling conditional expressions on timezone fields to narrow results.")
class Op5c5fb0f1211ae1c9451753f92f1053b6Request(StrictModel):
    """Retrieves a paginated list of available timezones. Supports pagination, filtering, sorting, and field projection via OData v4 query parameters."""
    query: Op5c5fb0f1211ae1c9451753f92f1053b6RequestQuery | None = None

# Operation: list_users
class ListUsersRequestQuery(StrictModel):
    status: str | None = Field(default=None, description="Comma-separated list of account statuses to filter results by; only users matching at least one of the provided statuses are returned. Omitting this parameter or providing no recognized values returns users of all statuses.")
class ListUsersRequest(StrictModel):
    """Retrieves all users for the company, with each record including user ID, employee ID, name, email, account status, and last login time. Support admin accounts are always excluded; results can be filtered by status and returned as JSON or XML based on the Accept header."""
    query: ListUsersRequestQuery | None = None

# Operation: get_employee
class GetEmployeeRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the employee to retrieve. Use the special value 0 to automatically resolve to the employee associated with the current API key.")
class GetEmployeeRequestQuery(StrictModel):
    fields: str | None = Field(default=None, description="Comma-separated list of field names specifying which employee fields to include in the response. Use the List Fields endpoint (list-fields) to discover all valid field names. Maximum of 400 fields per request.")
    only_current: bool | None = Field(default=None, validation_alias="onlyCurrent", serialization_alias="onlyCurrent", description="Controls whether historical table fields (such as job title or compensation) return only the current value or also include future-dated entries. Set to false to include future-dated values.")
class GetEmployeeRequest(StrictModel):
    """Retrieves profile and field data for a specific employee by ID. Supports selective field retrieval and optionally includes future-dated values from historical tables such as job title or compensation."""
    path: GetEmployeeRequestPath
    query: GetEmployeeRequestQuery | None = None

# Operation: update_employee
class UpdateEmployeeRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="Unique identifier of the employee record to update.")
class UpdateEmployeeRequestBody(StrictModel):
    first_name: str | None = Field(default=None, validation_alias="firstName", serialization_alias="firstName", description="Employee's legal first name.")
    last_name: str | None = Field(default=None, validation_alias="lastName", serialization_alias="lastName", description="Employee's legal last name.")
    work_email: str | None = Field(default=None, validation_alias="workEmail", serialization_alias="workEmail", description="Employee's work email address.")
    job_title: str | None = Field(default=None, validation_alias="jobTitle", serialization_alias="jobTitle", description="Employee's job title.")
    department: str | None = Field(default=None, description="Name of the department the employee belongs to.")
    division: str | None = Field(default=None, description="Name of the division the employee belongs to.")
    location: str | None = Field(default=None, description="Name of the work location assigned to the employee.")
    hire_date: str | None = Field(default=None, validation_alias="hireDate", serialization_alias="hireDate", description="Date the employee was hired, in YYYY-MM-DD format (ISO 8601 full date).", json_schema_extra={'format': 'date'})
    mobile_phone: str | None = Field(default=None, validation_alias="mobilePhone", serialization_alias="mobilePhone", description="Employee's mobile phone number.")
    home_phone: str | None = Field(default=None, validation_alias="homePhone", serialization_alias="homePhone", description="Employee's home phone number.")
    work_phone: str | None = Field(default=None, validation_alias="workPhone", serialization_alias="workPhone", description="Employee's work phone number.")
    address1: str | None = Field(default=None, description="First line of the employee's street address.")
    city: str | None = Field(default=None, description="City component of the employee's address.")
    state: str | None = Field(default=None, description="State or province component of the employee's address; values are normalized to standard abbreviations (e.g., full state names are converted to their two-letter code).")
    zipcode: str | None = Field(default=None, description="ZIP or postal code component of the employee's address.")
    country: str | None = Field(default=None, description="Country component of the employee's address.")
class UpdateEmployeeRequest(StrictModel):
    """Update one or more fields for an existing employee by submitting a JSON object or XML document with field name/value pairs. To discover all available field names beyond those listed here, call the list_fields operation (GET /api/v1/meta/fields). Note: if the employee is on a Trax Payroll pay schedule, a comprehensive set of required payroll fields must be included in the request."""
    path: UpdateEmployeeRequestPath
    body: UpdateEmployeeRequestBody | None = None

# Operation: list_changed_employee_table_rows
class GetChangedEmployeeTableDataRequestPath(StrictModel):
    table: str = Field(default=..., description="The name of the employee data table to retrieve changed rows for, such as job information or compensation details.")
class GetChangedEmployeeTableDataRequestQuery(StrictModel):
    since: str = Field(default=..., description="An ISO 8601 datetime timestamp indicating the cutoff point; only rows belonging to employees whose records were modified after this timestamp will be returned. Must be URL-encoded when included in the request.", json_schema_extra={'format': 'date-time'})
class GetChangedEmployeeTableDataRequest(StrictModel):
    """Retrieves table rows for all employees whose records have changed since a specified timestamp, grouped by employee ID. Any change to an employee record causes all of that employee's rows in the specified table to be returned, making this an efficient alternative to fetching full table data for all employees."""
    path: GetChangedEmployeeTableDataRequestPath
    query: GetChangedEmployeeTableDataRequestQuery

# Operation: list_employee_table_rows
class GetEmployeeTableDataRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the employee whose table data should be retrieved. Use the special value \"all\" to retrieve table data across all employees the API user has access to.")
    table: str = Field(default=..., description="The name of the table to retrieve rows from, such as job information, compensation, or employment status tables.")
class GetEmployeeTableDataRequest(StrictModel):
    """Retrieves all rows from a specified table for one or all employees, returning only the fields the caller has permission to access. Results are unordered and field visibility is subject to field-level permission checks."""
    path: GetEmployeeTableDataRequestPath

# Operation: create_employee_table_row
class CreateTableRowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the employee whose table will receive the new row.")
    table: str = Field(default=..., description="The name of the employee table to append a row to, such as job information or compensation history.")
class CreateTableRowRequestBody(StrictModel):
    date: str | None = Field(default=None, description="The effective date for the new row, indicating when the record becomes active. Must follow YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    location: str | None = Field(default=None, description="The office or work location associated with this row entry.")
    division: str | None = Field(default=None, description="The organizational division associated with this row entry.")
    department: str | None = Field(default=None, description="The department associated with this row entry.")
    job_title: str | None = Field(default=None, validation_alias="jobTitle", serialization_alias="jobTitle", description="The job title assigned to the employee for this row entry.")
    reports_to: str | None = Field(default=None, validation_alias="reportsTo", serialization_alias="reportsTo", description="The identifier of the manager or supervisor this employee reports to for this row entry.")
    teams: list[str] | None = Field(default=None, description="A list of team identifiers or names associated with this row entry. Order is not significant; each item represents a single team affiliation.")
class CreateTableRowRequest(StrictModel):
    """Appends a new row to a specified tabular data section of an employee record, such as job information or compensation history. Submit field name/value pairs in JSON or XML to record a new entry with an effective date and relevant attributes."""
    path: CreateTableRowRequestPath
    body: CreateTableRowRequestBody | None = None

# Operation: update_employee_table_row_v1_1
class UpdateTableRowV11RequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the employee whose table row is being updated.")
    table: str = Field(default=..., description="The name of the employee table containing the row to update, such as job information or compensation tables.")
    row_id: str = Field(default=..., validation_alias="rowId", serialization_alias="rowId", description="The unique identifier of the specific row within the table to update.")
class UpdateTableRowV11RequestBody(StrictModel):
    date: str | None = Field(default=None, description="The effective date for the row update in ISO 8601 full-date format (YYYY-MM-DD), determining when the change takes effect.", json_schema_extra={'format': 'date'})
    location: str | None = Field(default=None, description="The physical or organizational location value to assign to the employee for this row.")
    division: str | None = Field(default=None, description="The division value to assign to the employee for this row, representing a high-level organizational grouping.")
    department: str | None = Field(default=None, description="The department value to assign to the employee for this row, representing the employee's organizational unit.")
    job_title: str | None = Field(default=None, validation_alias="jobTitle", serialization_alias="jobTitle", description="The job title value to assign to the employee for this row, reflecting their role or position.")
    reports_to: str | None = Field(default=None, validation_alias="reportsTo", serialization_alias="reportsTo", description="The identifier of the manager or supervisor this employee reports to for this row.")
    teams: list[str] | None = Field(default=None, description="A list of team identifiers or names associated with the employee for this row; order is not significant.")
class UpdateTableRowV11Request(StrictModel):
    """Updates an existing row in a specified employee table, such as job information or compensation history. Submit field changes to modify the row's effective date, location, department, job title, reporting structure, or team assignments."""
    path: UpdateTableRowV11RequestPath
    body: UpdateTableRowV11RequestBody | None = None

# Operation: create_employee_table_row_v1_1
class CreateTableRowV11RequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the employee whose table will receive the new row.")
    table: str = Field(default=..., description="The name of the employee table to add a row to, such as job information or compensation tables.")
class CreateTableRowV11RequestBody(StrictModel):
    date: str | None = Field(default=None, description="The date on which the new row becomes effective, in YYYY-MM-DD format following ISO 8601.", json_schema_extra={'format': 'date'})
    location: str | None = Field(default=None, description="The office or work location associated with this row entry.")
    division: str | None = Field(default=None, description="The organizational division associated with this row entry.")
    department: str | None = Field(default=None, description="The department associated with this row entry.")
    job_title: str | None = Field(default=None, validation_alias="jobTitle", serialization_alias="jobTitle", description="The job title associated with this row entry.")
    reports_to: str | None = Field(default=None, validation_alias="reportsTo", serialization_alias="reportsTo", description="The identifier of the manager or supervisor this employee reports to for this row entry.")
    teams: list[str] | None = Field(default=None, description="A list of team identifiers associated with this row entry; order is not significant and each item represents a single team value.")
class CreateTableRowV11Request(StrictModel):
    """Adds a new row to a specified table in an employee's record, such as job information or compensation history. Accepts row data in JSON or XML format with an optional effective date and relevant field values."""
    path: CreateTableRowV11RequestPath
    body: CreateTableRowV11RequestBody | None = None

# Operation: list_changed_employees
class GetChangedEmployeeIdsRequestQuery(StrictModel):
    since: str = Field(default=..., description="The cutoff timestamp in ISO 8601 format; only employees whose records changed after this point will be returned. Must be URL-encoded when included in the request.", json_schema_extra={'format': 'date-time'})
    type_: Literal["inserted", "updated", "deleted", "all"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Filters results to a specific type of change; when omitted, employees of all change types are returned. Accepted values are 'inserted', 'updated', 'deleted', or 'all'.")
class GetChangedEmployeeIdsRequest(StrictModel):
    """Retrieves a list of employee IDs that have changed since a specified timestamp, enabling efficient incremental sync without downloading all employee records. Each result includes the employee ID, change type (inserted, updated, or deleted), and the timestamp of the last change."""
    query: GetChangedEmployeeIdsRequestQuery

# Operation: get_employee_photo
class GetEmployeePhotoRequestPath(StrictModel):
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique numeric identifier of the employee whose photo is being requested.")
    size: Literal["original", "large", "medium", "small", "xs", "tiny"] = Field(default=..., description="The predefined size tier for the returned photo. Available options are: original (full resolution), large (340×340), medium (170×170), small (150×150), xs (50×50), and tiny (20×20).")
class GetEmployeePhotoRequestQuery(StrictModel):
    width: int | None = Field(default=None, description="Scales the returned image to this pixel width, capped at the natural width of the requested size tier. Only applies when size is small or tiny.")
    height: int | None = Field(default=None, description="Scales the returned image to this pixel height, capped at the natural height of the requested size tier. Only applies when size is small or tiny.")
class GetEmployeePhotoRequest(StrictModel):
    """Retrieves a JPEG photo of the specified employee at a predefined size. The response Content-Type is always image/jpeg, though the underlying byte payload may reflect the original upload format."""
    path: GetEmployeePhotoRequestPath
    query: GetEmployeePhotoRequestQuery | None = None

# Operation: create_employee_file_categories
class AddEmployeeFileCategoryRequestBody(StrictModel):
    body: list[str] | None = Field(default=None, description="A list of category name strings to create. Each name must be non-empty and must not already exist. Order is not significant.")
class AddEmployeeFileCategoryRequest(StrictModel):
    """Creates one or more employee file categories by accepting a list of category names. An empty payload succeeds without creating anything; duplicate or empty names return an error."""
    body: AddEmployeeFileCategoryRequestBody | None = None

# Operation: create_file_categories
class AddCompanyFileCategoryRequestBody(StrictModel):
    body: list[str] | None = Field(default=None, description="An array of category name strings to create. Each entry must be a non-empty, unique name that is not reserved. Order is not significant.")
class AddCompanyFileCategoryRequest(StrictModel):
    """Creates one or more company file categories in a single request. Returns 400 if any name is empty or already exists, 403 if the caller lacks permission or a name is reserved, and 200 with no changes if the payload is empty."""
    body: AddCompanyFileCategoryRequestBody | None = None

# Operation: upload_employee_file
class UploadEmployeeFileRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the employee whose file folder will receive the upload. Pass 0 to target the employee associated with the API key.")
class UploadEmployeeFileRequestBody(StrictModel):
    file_name: str = Field(default=..., validation_alias="fileName", serialization_alias="fileName", description="The display name assigned to the uploaded file as it will appear in the employee's document folder.")
    category: int = Field(default=..., description="The numeric ID of the employee file section (category) into which the file will be uploaded.")
    share: Literal["yes", "no"] | None = Field(default=None, description="Controls whether the uploaded file is shared with the employee and made visible to them. Defaults to no if omitted.")
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="The binary file content to upload, submitted as part of the multipart/form-data request body.", json_schema_extra={'format': 'binary'})
class UploadEmployeeFileRequest(StrictModel):
    """Uploads a file to a specific section of an employee's document folder via multipart/form-data. Files must be under 20MB and use a supported extension; on success, the response includes a Location header pointing to the newly created file resource."""
    path: UploadEmployeeFileRequestPath
    body: UploadEmployeeFileRequestBody

# Operation: upload_file
class UploadCompanyFileRequestBody(StrictModel):
    file_name: str = Field(default=..., validation_alias="fileName", serialization_alias="fileName", description="The display name for the file as it will appear in the company file system.")
    category: int = Field(default=..., description="The numeric ID of the file category (section) into which the file will be uploaded. Read-only categories and implementation categories (for completed implementations) are not permitted.")
    share: Literal["yes", "no"] | None = Field(default=None, description="Controls whether the uploaded file is shared with all employees. Accepts 'yes' to share or 'no' to keep private; defaults to 'no' if omitted.")
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="The binary file content to upload. Must be under 20MB and use a supported file extension.", json_schema_extra={'format': 'binary'})
class UploadCompanyFileRequest(StrictModel):
    """Uploads a file to a specified company file category using a multipart/form-data request. Files must be under 20MB, use a supported extension, and cannot be uploaded to read-only categories or implementation categories on companies that have completed implementation."""
    body: UploadCompanyFileRequestBody

# Operation: list_employee_time_off_policies
class ListEmployeeTimeOffPoliciesRequestPath(StrictModel):
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee whose assigned time off policies should be retrieved.")
class ListEmployeeTimeOffPoliciesRequest(StrictModel):
    """Retrieves all time off policies currently assigned to a specified employee, including each policy's ID, time off type, and accrual start date."""
    path: ListEmployeeTimeOffPoliciesRequestPath

# Operation: assign_employee_time_off_policies
class AssignTimeOffPoliciesRequestPath(StrictModel):
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee to whom time off policies will be assigned.")
class AssignTimeOffPoliciesRequestBody(StrictModel):
    body: list[AssignTimeOffPoliciesBodyItem] | None = Field(default=None, description="List of policy assignment objects, each specifying a time off policy and the date on which accruals should begin for that policy. Order is not significant. Set accrualStartDate to null to remove an existing policy assignment rather than add or update one.")
class AssignTimeOffPoliciesRequest(StrictModel):
    """Assigns one or more time off policies to an employee, with accruals beginning on the specified start date for each policy. Passing a null accrual start date for a policy removes that existing assignment; returns the full updated list of assigned policies on success."""
    path: AssignTimeOffPoliciesRequestPath
    body: AssignTimeOffPoliciesRequestBody | None = None

# Operation: list_employee_time_off_policies_extended
class ListEmployeeTimeOffPoliciesV11RequestPath(StrictModel):
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee whose time off policies should be retrieved.")
class ListEmployeeTimeOffPoliciesV11Request(StrictModel):
    """Retrieves all time off policies currently assigned to a specified employee, including manual and unlimited policy types not available in the v1 endpoint."""
    path: ListEmployeeTimeOffPoliciesV11RequestPath

# Operation: assign_time_off_policies
class AssignTimeOffPoliciesV11RequestPath(StrictModel):
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee to whom the time off policies will be assigned.")
class AssignTimeOffPoliciesV11RequestBody(StrictModel):
    body: list[AssignTimeOffPoliciesV11BodyItem] | None = Field(default=None, description="A list of policy assignment objects, each specifying a time off policy and the date on which accruals should begin for that policy. Order is not significant. Set accrual start date to null for policies that do not use accrual-based tracking.")
class AssignTimeOffPoliciesV11Request(StrictModel):
    """Assigns one or more time off policies to an employee, with accruals beginning on the specified start date for each policy. Returns the employee's full current list of assigned policies, including manual and unlimited policy types."""
    path: AssignTimeOffPoliciesV11RequestPath
    body: AssignTimeOffPoliciesV11RequestBody | None = None

# Operation: get_application
class GetApplicationDetailsRequestPath(StrictModel):
    application_id: int = Field(default=..., validation_alias="applicationId", serialization_alias="applicationId", description="The unique identifier of the job application to retrieve.")
class GetApplicationDetailsRequest(StrictModel):
    """Retrieves full details for a single job application, including applicant information, job details, screening questions and answers, and status history. Requires the API key owner to have access to ATS settings."""
    path: GetApplicationDetailsRequestPath

# Operation: add_application_comment
class CreateApplicationCommentRequestPath(StrictModel):
    application_id: int = Field(default=..., validation_alias="applicationId", serialization_alias="applicationId", description="The unique identifier of the job application to which the comment will be added.")
class CreateApplicationCommentRequestBody(StrictModel):
    """Comment object to post"""
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The category of the comment being posted. Accepts predefined comment type values; defaults to 'comment' if not provided.")
    comment: str = Field(default=..., description="The text content of the comment to post on the application.")
class CreateApplicationCommentRequest(StrictModel):
    """Adds a comment to a specific job application in the Applicant Tracking System. Requires the API key owner to have access to ATS settings."""
    path: CreateApplicationCommentRequestPath
    body: CreateApplicationCommentRequestBody

# Operation: list_jobs
class GetJobSummariesRequestQuery(StrictModel):
    status_groups: str | None = Field(default=None, validation_alias="statusGroups", serialization_alias="statusGroups", description="One or more status group names to filter job openings by, provided as a comma-separated string. Defaults to all non-deleted positions when omitted.")
    status_ids: str | None = Field(default=None, description="One or more specific job opening status IDs to filter by, provided as a comma-separated string of integers. When combined with statusGroups, both filters are applied together.")
    sort_by: Literal["count", "title", "lead", "created", "status"] | None = Field(default=None, validation_alias="sortBy", serialization_alias="sortBy", description="The field by which to sort the returned job openings. Applies to the full result set before pagination.")
    sort_order: Literal["ASC", "DESC"] | None = Field(default=None, validation_alias="sortOrder", serialization_alias="sortOrder", description="The direction in which to sort results, either ascending or descending.")
class GetJobSummariesRequest(StrictModel):
    """Retrieves a list of job opening summaries from the Applicant Tracking System. Supports filtering by status group or specific status IDs, with configurable sorting. Requires ATS settings access."""
    query: GetJobSummariesRequestQuery | None = None

# Operation: update_application_status
class UpdateApplicantStatusRequestPath(StrictModel):
    application_id: int = Field(default=..., validation_alias="applicationId", serialization_alias="applicationId", description="The unique identifier of the application whose status will be updated.")
class UpdateApplicantStatusRequestBody(StrictModel):
    """The new status to assign to the application."""
    status: int = Field(default=..., description="The unique identifier of the status to assign to the application. Retrieve valid status IDs using the Get Applicant Statuses endpoint.")
class UpdateApplicantStatusRequest(StrictModel):
    """Updates the status of a specific applicant tracking application. The API key owner must have ATS settings access, and valid status IDs can be retrieved via the Get Applicant Statuses endpoint."""
    path: UpdateApplicantStatusRequestPath
    body: UpdateApplicantStatusRequestBody

# Operation: get_employee_dependent
class GetEmployeeDependentRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique numeric identifier of the employee dependent record to retrieve.")
class GetEmployeeDependentRequest(StrictModel):
    """Retrieves the full details of a single employee dependent by their unique dependent ID, including masked SSN/SIN values and full state and country names. Requires Benefits Administration permissions and returns data as a JSON or XML object containing a single-element array under the 'Employee Dependents' key."""
    path: GetEmployeeDependentRequestPath

# Operation: update_dependent
class UpdateEmployeeDependentRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The numeric ID of the employee dependent record to update.")
class UpdateEmployeeDependentRequestBody(StrictModel):
    employee_id: str = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The ID of the employee this dependent is associated with. Must reference an existing, valid employee.")
    first_name: str | None = Field(default=None, validation_alias="firstName", serialization_alias="firstName", description="The dependent's first name.")
    middle_name: str | None = Field(default=None, validation_alias="middleName", serialization_alias="middleName", description="The dependent's middle name.")
    last_name: str | None = Field(default=None, validation_alias="lastName", serialization_alias="lastName", description="The dependent's last name.")
    relationship: str | None = Field(default=None, description="The dependent's relationship to the employee. Must be a valid relationship type recognized by the system.")
    gender: str | None = Field(default=None, description="The dependent's gender. Must be a valid gender value recognized by the system.")
    ssn: str | None = Field(default=None, description="The dependent's Social Security Number, submitted as plain text and stored encrypted. Read responses return a masked value.")
    sin: str | None = Field(default=None, description="The dependent's Social Insurance Number (Canadian equivalent of SSN), submitted as plain text and stored encrypted. Read responses return a masked value.")
    date_of_birth: str | None = Field(default=None, validation_alias="dateOfBirth", serialization_alias="dateOfBirth", description="The dependent's date of birth. Must be provided in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    address_line1: str | None = Field(default=None, validation_alias="addressLine1", serialization_alias="addressLine1", description="The first line of the dependent's street address.")
    address_line2: str | None = Field(default=None, validation_alias="addressLine2", serialization_alias="addressLine2", description="The second line of the dependent's street address, such as an apartment or suite number.")
    city: str | None = Field(default=None, description="The city component of the dependent's address.")
    state: str | None = Field(default=None, description="The dependent's state, provided as a two-letter state code. Read responses return the full state name.")
    zip_code: str | None = Field(default=None, validation_alias="zipCode", serialization_alias="zipCode", description="The dependent's ZIP or postal code.")
    home_phone: str | None = Field(default=None, validation_alias="homePhone", serialization_alias="homePhone", description="The dependent's home phone number.")
    country: str | None = Field(default=None, description="The dependent's country, provided as an ISO 3166-1 alpha-2 two-letter country code. Read responses return the full country name.")
    is_us_citizen: Literal["yes", "no"] | None = Field(default=None, validation_alias="isUsCitizen", serialization_alias="isUsCitizen", description="Indicates whether the dependent is a US citizen. Accepted values are \"yes\" or \"no\".")
    is_student: Literal["yes", "no"] | None = Field(default=None, validation_alias="isStudent", serialization_alias="isStudent", description="Indicates whether the dependent is currently enrolled as a student. Accepted values are \"yes\" or \"no\".")
class UpdateEmployeeDependentRequest(StrictModel):
    """Fully replaces an existing employee dependent record with the provided data. This is a full-replacement operation — all fields must be supplied, as omitted fields will be cleared rather than preserved."""
    path: UpdateEmployeeDependentRequestPath
    body: UpdateEmployeeDependentRequestBody

# Operation: list_employee_dependents
class ListEmployeeDependentsRequestQuery(StrictModel):
    employeeid: int | None = Field(default=None, description="Filters the results to dependents belonging to a specific employee. When omitted, dependents for all employees in the company are returned.")
class ListEmployeeDependentsRequest(StrictModel):
    """Retrieves dependent records for one or all employees in the company, requiring Benefits Administration permissions. When an employee ID is provided the response is scoped to that employee; otherwise all dependents across the company are returned, with SSN/SIN values masked and state/country fields returned as full names."""
    query: ListEmployeeDependentsRequestQuery | None = None

# Operation: create_employee_dependent
class CreateEmployeeDependentRequestBody(StrictModel):
    employee_id: str = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee to whom this dependent belongs. Must reference an existing employee record.")
    first_name: str | None = Field(default=None, validation_alias="firstName", serialization_alias="firstName", description="The dependent's first name.")
    middle_name: str | None = Field(default=None, validation_alias="middleName", serialization_alias="middleName", description="The dependent's middle name.")
    last_name: str | None = Field(default=None, validation_alias="lastName", serialization_alias="lastName", description="The dependent's last name.")
    relationship: str | None = Field(default=None, description="The dependent's relationship to the employee. Must be a valid relationship type such as spouse, child, or domestic partner.")
    gender: str | None = Field(default=None, description="The dependent's gender. Must be a valid gender value as recognized by the API.")
    ssn: str | None = Field(default=None, description="The dependent's Social Security Number, submitted as plain text and stored encrypted. When retrieved, the value is returned in masked form showing only the last four digits.")
    sin: str | None = Field(default=None, description="The dependent's Social Insurance Number (Canadian equivalent of SSN), submitted as plain text and stored encrypted. When retrieved, the value is returned in masked form.")
    date_of_birth: str | None = Field(default=None, validation_alias="dateOfBirth", serialization_alias="dateOfBirth", description="The dependent's date of birth, formatted as a calendar date in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    address_line1: str | None = Field(default=None, validation_alias="addressLine1", serialization_alias="addressLine1", description="The first line of the dependent's street address, typically including street number and name.")
    address_line2: str | None = Field(default=None, validation_alias="addressLine2", serialization_alias="addressLine2", description="The second line of the dependent's address, used for suite, apartment, or unit information.")
    city: str | None = Field(default=None, description="The city portion of the dependent's address.")
    state: str | None = Field(default=None, description="The dependent's state, provided as a two-letter state code. When retrieved, the API returns the full state name.")
    zip_code: str | None = Field(default=None, validation_alias="zipCode", serialization_alias="zipCode", description="The dependent's ZIP or postal code corresponding to their address.")
    home_phone: str | None = Field(default=None, validation_alias="homePhone", serialization_alias="homePhone", description="The dependent's home phone number.")
    country: str | None = Field(default=None, description="The dependent's country, provided as an ISO 3166-1 alpha-2 two-letter country code. When retrieved, the API returns the full country name.")
    is_us_citizen: Literal["yes", "no"] | None = Field(default=None, validation_alias="isUsCitizen", serialization_alias="isUsCitizen", description="Indicates whether the dependent is a US citizen. Accepted values are yes or no.")
    is_student: Literal["yes", "no"] | None = Field(default=None, validation_alias="isStudent", serialization_alias="isStudent", description="Indicates whether the dependent is currently enrolled as a student. Accepted values are yes or no.")
class CreateEmployeeDependentRequest(StrictModel):
    """Creates a new dependent record associated with a specific employee, capturing personal, demographic, and address details. The employee must exist, and sensitive fields like SSN and SIN are accepted as plain text and stored encrypted."""
    body: CreateEmployeeDependentRequestBody

# Operation: get_employee_directory
class GetEmployeesDirectoryRequestQuery(StrictModel):
    only_current: bool | None = Field(default=None, validation_alias="onlyCurrent", serialization_alias="onlyCurrent", description="Controls whether only active employees are returned. Set to false to include terminated employees alongside active ones.")
class GetEmployeesDirectoryRequest(StrictModel):
    """Retrieves the company employee directory, including a fieldset definition and employee records. Access level determines the returned fieldset; directory sharing or org-chart access must be enabled for the company."""
    query: GetEmployeesDirectoryRequestQuery | None = None

# Operation: list_employee_files
class ListEmployeeFilesRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the employee whose files are being listed. Only files and categories the caller is permitted to view will be returned.")
class ListEmployeeFilesRequest(StrictModel):
    """Retrieves the file categories and associated files visible to the caller for a specified employee. Results are permission-filtered; employees viewing their own profile also see files shared with them. Response format is determined by the Accept header (application/json for JSON, XML otherwise)."""
    path: ListEmployeeFilesRequestPath

# Operation: list_list_fields
class ListListFieldsRequestQuery(StrictModel):
    format_: Literal["json"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="Specifies the response format as JSON, serving as an alternative to setting the Accept header on the request.")
class ListListFieldsRequest(StrictModel):
    """Retrieves all list fields defined in the account, including each field's ID, alias, options, manageability, and multi-value support. Archived options are included in responses to support historical data references but should not be presented as active selections."""
    query: ListListFieldsRequestQuery | None = None

# Operation: update_list_field_options
class UpdateListFieldValuesRequestPath(StrictModel):
    list_field_id: str = Field(default=..., validation_alias="listFieldId", serialization_alias="listFieldId", description="The unique identifier of the list field whose options are being managed.")
class UpdateListFieldValuesRequestBody(StrictModel):
    options: list[UpdateListFieldValuesBodyOptionsItem] | None = Field(default=None, description="Array of option objects to create, update, or archive on the list field. To create a new option omit its ID, to update an existing option include its ID, and to archive an option include its ID with the archived attribute set to yes. Order is not significant.")
class UpdateListFieldValuesRequest(StrictModel):
    """Create, update, or archive options for a specific list field by its ID. Omit an option's ID to create it, include an ID to update it, or set archived to yes to hide it from future use while preserving historical data."""
    path: UpdateListFieldValuesRequestPath
    body: UpdateListFieldValuesRequestBody | None = None

# Operation: get_employee_time_off_balance
class GetTimeOffBalanceRequestPath(StrictModel):
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee whose time off balances should be retrieved.")
class GetTimeOffBalanceRequestQuery(StrictModel):
    end: str | None = Field(default=None, description="The date through which time off balances are calculated, in YYYY-MM-DD format. Defaults to the company's current date if omitted; supply a future date to project balances.", json_schema_extra={'format': 'date'})
    precision: int | None = Field(default=None, description="Number of decimal places applied to balance and year-to-date usage values. Accepts values from 0 (whole numbers) to 4 (four decimal places), defaulting to 2.", ge=0, le=4)
class GetTimeOffBalanceRequest(StrictModel):
    """Retrieves time off balances for an employee across all assigned categories as of a specified date, incorporating accruals, adjustments, usage, and carry-over events. Pass today's date for current balances or a future date to project balances forward."""
    path: GetTimeOffBalanceRequestPath
    query: GetTimeOffBalanceRequestQuery | None = None

# Operation: create_time_off_history_entry
class CreateTimeOffHistoryRequestPath(StrictModel):
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee for whom the time off history entry is being created.")
class CreateTimeOffHistoryRequestBody(StrictModel):
    date: str = Field(default=..., description="The calendar date the history entry applies to, provided in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    event_type: Literal["used", "override"] | None = Field(default=None, validation_alias="eventType", serialization_alias="eventType", description="Specifies whether the entry records actual time off usage against an approved request or a manual balance override adjustment. Defaults to 'used' when omitted on this endpoint.")
    time_off_request_id: int | None = Field(default=None, validation_alias="timeOffRequestId", serialization_alias="timeOffRequestId", description="The unique identifier of the approved time off request this entry is linked to. Must be provided when eventType is 'used'.")
    time_off_type_id: int | None = Field(default=None, validation_alias="timeOffTypeId", serialization_alias="timeOffTypeId", description="The unique identifier of the time off type (e.g., vacation, sick leave) to apply the balance adjustment to. Must be provided when eventType is 'override'.")
    amount: float | None = Field(default=None, description="The quantity of hours or days to record for this history entry. Must be provided when eventType is 'override'; positive values increase the balance and negative values decrease it.")
    note: str | None = Field(default=None, description="An optional free-text note that will be displayed alongside this entry in the employee's time off history.")
class CreateTimeOffHistoryRequest(StrictModel):
    """Records a time off history entry for an employee, either logging usage against an approved time off request or applying a manual balance adjustment. The entry type determines which additional fields are required."""
    path: CreateTimeOffHistoryRequestPath
    body: CreateTimeOffHistoryRequestBody

# Operation: adjust_time_off_balance
class AdjustTimeOffBalanceRequestPath(StrictModel):
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="Unique identifier of the employee whose time off balance is being adjusted.")
class AdjustTimeOffBalanceRequestBody(StrictModel):
    date: str = Field(default=..., description="The effective date of the balance adjustment as it will appear in history, in ISO 8601 format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    time_off_type_id: int = Field(default=..., validation_alias="timeOffTypeId", serialization_alias="timeOffTypeId", description="Unique identifier of the time off type to adjust; must be a non-discretionary (limited) time off type.")
    amount: float = Field(default=..., description="The number of hours or days to adjust the balance by; use a positive value to add time or a negative value to deduct time.")
    note: str | None = Field(default=None, description="Optional note providing context or reason for the adjustment, visible in the employee's time off history.")
class AdjustTimeOffBalanceRequest(StrictModel):
    """Creates a balance adjustment for a specific time off type on an employee's account, recorded as an override history entry. Not applicable to discretionary (unlimited) time off types."""
    path: AdjustTimeOffBalanceRequestPath
    body: AdjustTimeOffBalanceRequestBody

# Operation: create_time_off_request
class CreateTimeOffRequestPath(StrictModel):
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee for whom the time off request is being created.")
class CreateTimeOffRequestBody(StrictModel):
    status: Literal["approved", "denied", "declined", "requested"] = Field(default=..., description="The initial status of the time off request. Use 'requested' to submit for approval; use 'approved' or 'denied' to record a decision directly without triggering approval notifications; 'declined' indicates the employee withdrew the request.")
    start: str = Field(default=..., description="The first day of the time off period in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    end: str = Field(default=..., description="The last day of the time off period in YYYY-MM-DD format. Must be the same as or later than the start date.", json_schema_extra={'format': 'date'})
    time_off_type_id: int = Field(default=..., validation_alias="timeOffTypeId", serialization_alias="timeOffTypeId", description="The unique identifier of the time off type (e.g., vacation, sick leave) to apply to this request.")
    amount: float | None = Field(default=None, description="The total number of hours or days being requested. This value is ignored when a dates array is provided, in which case the sum of the daily amounts is used instead.")
    previous_request: int | None = Field(default=None, validation_alias="previousRequest", serialization_alias="previousRequest", description="The unique identifier of an existing time off request that this request supersedes. The referenced request will be cancelled and replaced by this new request.")
    notes: list[CreateTimeOffRequestBodyNotesItem] | None = Field(default=None, description="An optional list of notes from the employee or manager providing context or comments about the time off request. Order is not significant.")
    dates: list[CreateTimeOffRequestBodyDatesItem] | None = Field(default=None, description="An optional per-day breakdown of the time off request, where each item specifies the date and amount for that day. When provided, the top-level amount field is ignored and the sum of daily amounts is used as the total.")
class CreateTimeOffRequest(StrictModel):
    """Creates a time off request for an employee with an initial status of approved, denied, or requested. Approved and denied requests are recorded directly without triggering approval notifications; supplying a previousRequest ID cancels the original request and replaces it with this one."""
    path: CreateTimeOffRequestPath
    body: CreateTimeOffRequestBody

# Operation: update_time_off_request_status
class UpdateTimeOffRequestStatusRequestPath(StrictModel):
    request_id: int = Field(default=..., validation_alias="requestId", serialization_alias="requestId", description="The unique identifier of the time off request whose status is being updated.")
class UpdateTimeOffRequestStatusRequestBody(StrictModel):
    status: Literal["approved", "denied", "declined", "canceled", "cancelled"] = Field(default=..., description="The new status to apply to the time off request. Use 'approved' to grant the request, 'denied' or 'declined' to reject it, and 'canceled' or 'cancelled' to withdraw it.")
    note: str | None = Field(default=None, description="An optional note to attach to the status change, such as a reason for denial or approval context.")
class UpdateTimeOffRequestStatusRequest(StrictModel):
    """Approves, denies, or cancels an existing time off request by updating its status. Owners and admins can complete all workflow approval steps at once, while standard approvers advance only their current step."""
    path: UpdateTimeOffRequestStatusRequestPath
    body: UpdateTimeOffRequestStatusRequestBody

# Operation: list_time_off_requests
class ListTimeOffRequestsRequestQuery(StrictModel):
    id_: int | None = Field(default=None, validation_alias="id", serialization_alias="id", description="Filters the response to a single time off request matching this ID.")
    action: Literal["view", "approve", "myRequests"] | None = Field(default=None, description="Scopes the response based on the caller's relationship to the requests: all viewable requests, only those the caller can approve, or only the caller's own requests. Defaults to view if omitted.")
    employee_id: int | None = Field(default=None, validation_alias="employeeId", serialization_alias="employeeId", description="Filters the response to requests belonging to a single employee matching this ID.")
    start: str = Field(default=..., description="The beginning of the query window in YYYY-MM-DD format; requests that end on or after this date are included. Must be provided alongside the end parameter.", json_schema_extra={'format': 'date'})
    end: str = Field(default=..., description="The end of the query window in YYYY-MM-DD format; requests that start on or before this date are included. Must be provided alongside the start parameter.", json_schema_extra={'format': 'date'})
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Comma-separated list of time off type IDs to filter results by. When omitted, requests of all time off types are returned.")
    status: str | None = Field(default=None, description="Comma-separated list of statuses to filter results by; accepted values are approved, denied, superceded, requested, and canceled. When omitted, requests of all statuses are returned.")
    exclude_note: str | None = Field(default=None, validation_alias="excludeNote", serialization_alias="excludeNote", description="When set to a truthy value, the notes object is omitted from each request in the response, reducing payload size.")
class ListTimeOffRequestsRequest(StrictModel):
    """Retrieves time off requests that overlap a specified date range, requiring both a start and end date. Results can be filtered by request ID, employee, time off type, status, or scoped to requests the caller is authorized to approve."""
    query: ListTimeOffRequestsRequestQuery

# Operation: list_time_off_types
class ListTimeOffTypesRequestQuery(StrictModel):
    mode: Literal["request"] | None = Field(default=None, description="Controls filtering of returned time off types. When set to 'request', results are limited to only the types the authenticated employee has permission to request.")
class ListTimeOffTypesRequest(StrictModel):
    """Retrieves all active time off types for the company, along with the company's default hours-per-day schedule. Optionally filter to only the types the authenticated employee has permission to request."""
    query: ListTimeOffTypesRequestQuery | None = None

# Operation: create_training_type
class CreateTrainingTypeRequestBodyCategory(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The name of the category to associate with this training type, used to group related trainings together.")
    id_: int | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of an existing category to associate with this training type.")
class CreateTrainingTypeRequestBody(StrictModel):
    """Training object to post"""
    name: str = Field(default=..., description="The display name for the new training type.")
    frequency: int | None = Field(default=None, description="The number of months between required renewals for this training type. Must be provided when renewable is true; ignored otherwise.")
    renewable: bool | None = Field(default=None, description="Indicates whether this training type must be periodically renewed. When set to true, frequency must also be provided to define the renewal interval in months.")
    required: bool | None = Field(default=None, description="Indicates whether this training type is mandatory for employees. When true, dueFromHireDate may also be specified.")
    due_from_hire_date: int | None = Field(default=None, validation_alias="dueFromHireDate", serialization_alias="dueFromHireDate", description="The number of days after an employee's hire date by which this training must be completed. Only valid when required is true.")
    link_url: str | None = Field(default=None, validation_alias="linkUrl", serialization_alias="linkUrl", description="An optional URL to attach to this training type, such as a link to course materials or an external training resource.")
    description: str | None = Field(default=None, description="A detailed description of the training type, providing employees and administrators with context about its purpose or content.")
    allow_employees_to_mark_complete: bool | None = Field(default=None, validation_alias="allowEmployeesToMarkComplete", serialization_alias="allowEmployeesToMarkComplete", description="When true, any employee who can view this training type is also permitted to mark it as complete on their own record.")
    category: CreateTrainingTypeRequestBodyCategory | None = None
class CreateTrainingTypeRequest(StrictModel):
    """Creates a new training type with the specified configuration, including optional renewal schedules, hiring requirements, and completion permissions. Requires training settings access; when renewable is true, frequency must be provided, and dueFromHireDate is only applicable when required is true."""
    body: CreateTrainingTypeRequestBody

# Operation: update_training_type
class UpdateTrainingTypeRequestPath(StrictModel):
    training_type_id: int = Field(default=..., validation_alias="trainingTypeId", serialization_alias="trainingTypeId", description="The unique identifier of the training type to update.")
class UpdateTrainingTypeRequestBodyCategory(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The name of the category to assign to this training type. Pass an empty string or null to remove the existing category.")
    id_: int | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the category to assign to this training type.")
class UpdateTrainingTypeRequestBody(StrictModel):
    """Training type object to update to"""
    name: str | None = Field(default=None, description="The display name of the training type.")
    frequency: int | None = Field(default=None, description="The interval in months at which this training must be renewed. Only applicable when the training type is set to renewable.")
    renewable: bool | None = Field(default=None, description="Indicates whether this training type can be renewed on a recurring basis. If set to true, a frequency value must also be provided.")
    required: bool | None = Field(default=None, description="Indicates whether completion of this training type is mandatory for employees.")
    due_from_hire_date: int | None = Field(default=None, validation_alias="dueFromHireDate", serialization_alias="dueFromHireDate", description="The number of days after an employee's hire date by which this training must be completed. Only applicable when the training type is marked as required.")
    link_url: str | None = Field(default=None, validation_alias="linkUrl", serialization_alias="linkUrl", description="An optional URL to associate with this training type, such as a link to training materials or an external resource.")
    description: str | None = Field(default=None, description="A detailed description of the training type, providing context or instructions for employees.")
    allow_employees_to_mark_complete: bool | None = Field(default=None, validation_alias="allowEmployeesToMarkComplete", serialization_alias="allowEmployeesToMarkComplete", description="When enabled, allows any employee who can view this training type to mark it as complete without manager or admin intervention.")
    category: UpdateTrainingTypeRequestBodyCategory | None = None
class UpdateTrainingTypeRequest(StrictModel):
    """Updates an existing training type by modifying only the fields provided in the request. Requires training settings access; pass an empty string or null for the category field to remove a category assignment."""
    path: UpdateTrainingTypeRequestPath
    body: UpdateTrainingTypeRequestBody | None = None

# Operation: delete_training_type
class DeleteTrainingTypeRequestPath(StrictModel):
    training_type_id: int = Field(default=..., validation_alias="trainingTypeId", serialization_alias="trainingTypeId", description="The unique numeric identifier of the training type to delete. All associated employee trainings must be removed before this operation can succeed.")
class DeleteTrainingTypeRequest(StrictModel):
    """Permanently deletes an existing training type by its ID, requiring training settings access. All employee trainings associated with this type must be removed before this deletion will succeed."""
    path: DeleteTrainingTypeRequestPath

# Operation: create_training_category
class CreateTrainingCategoryRequestBody(StrictModel):
    """Training category to post"""
    name: str = Field(default=..., description="The display name for the new training category, used to identify and organize training content.")
class CreateTrainingCategoryRequest(StrictModel):
    """Creates a new training category to organize training content. Requires training settings access and returns the newly created TrainingCategory on success."""
    body: CreateTrainingCategoryRequestBody

# Operation: update_training_category
class UpdateTrainingCategoryRequestPath(StrictModel):
    training_category_id: int = Field(default=..., validation_alias="trainingCategoryId", serialization_alias="trainingCategoryId", description="The unique numeric identifier of the training category to update.")
class UpdateTrainingCategoryRequestBody(StrictModel):
    """Training category to update"""
    name: str = Field(default=..., description="The new name to assign to the training category; must be unique across all existing training categories.")
class UpdateTrainingCategoryRequest(StrictModel):
    """Updates the name of an existing training category identified by its ID. Requires training settings access; returns a 409 conflict if a category with the new name already exists."""
    path: UpdateTrainingCategoryRequestPath
    body: UpdateTrainingCategoryRequestBody

# Operation: delete_training_category
class DeleteTrainingCategoryRequestPath(StrictModel):
    training_category_id: int = Field(default=..., validation_alias="trainingCategoryId", serialization_alias="trainingCategoryId", description="The unique identifier of the training category to delete.")
class DeleteTrainingCategoryRequest(StrictModel):
    """Permanently deletes an existing training category by its unique identifier. The API key owner must have access to training settings to perform this action."""
    path: DeleteTrainingCategoryRequestPath

# Operation: list_employee_training_records
class ListEmployeeTrainingsRequestPath(StrictModel):
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee whose training records should be retrieved. The API key owner must have permission to view this employee.")
class ListEmployeeTrainingsRequestQuery(StrictModel):
    type_: int | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The unique identifier of a training type used to filter results to only records of that type. Omit this parameter to return all training records regardless of type.")
class ListEmployeeTrainingsRequest(StrictModel):
    """Retrieves all training records for a specified employee, returned as an object keyed by training record ID. Optionally filter by training type; note that fields like instructor, credits, hours, and cost are only present when enabled in the company's training settings."""
    path: ListEmployeeTrainingsRequestPath
    query: ListEmployeeTrainingsRequestQuery | None = None

# Operation: create_employee_training_record
class CreateEmployeeTrainingRecordRequestPath(StrictModel):
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique identifier of the employee for whom the training record is being created.")
class CreateEmployeeTrainingRecordRequestBodyCost(StrictModel):
    currency: str | None = Field(default=None, validation_alias="currency", serialization_alias="currency", description="The currency associated with the training cost, specified as an ISO 4217 three-letter currency code.")
    amount: str | None = Field(default=None, validation_alias="amount", serialization_alias="amount", description="The monetary cost of the training expressed as a decimal string, used alongside the currency field.")
class CreateEmployeeTrainingRecordRequestBody(StrictModel):
    """Training object to post"""
    completed: str = Field(default=..., description="The date the training was completed, formatted as ISO 8601 calendar date (yyyy-mm-dd).")
    instructor: str | None = Field(default=None, description="The full name of the instructor who delivered the training.")
    hours: float | None = Field(default=None, description="The total duration of the training expressed in hours.")
    credits_: float | None = Field(default=None, validation_alias="credits", serialization_alias="credits", description="The number of credits the employee earned upon completing the training.")
    notes: str | None = Field(default=None, description="Free-text notes providing additional context or details about the training record.")
    type_: int = Field(default=..., validation_alias="type", serialization_alias="type", description="The identifier of the training type to categorize this record; must correspond to an existing training type ID in the system.")
    cost: CreateEmployeeTrainingRecordRequestBodyCost | None = None
class CreateEmployeeTrainingRecordRequest(StrictModel):
    """Creates a new training record for a specified employee, logging completion date, training type, and optional details such as instructor, hours, credits, cost, and notes. The API key owner must have permission to add training records for the target employee."""
    path: CreateEmployeeTrainingRecordRequestPath
    body: CreateEmployeeTrainingRecordRequestBody

# Operation: update_training_record
class UpdateEmployeeTrainingRecordRequestPath(StrictModel):
    employee_training_record_id: int = Field(default=..., validation_alias="employeeTrainingRecordId", serialization_alias="employeeTrainingRecordId", description="The unique identifier of the employee training record to update.")
class UpdateEmployeeTrainingRecordRequestBodyCost(StrictModel):
    currency: str | None = Field(default=None, validation_alias="currency", serialization_alias="currency", description="The ISO 4217 three-letter currency code representing the currency of the training cost.")
    amount: str | None = Field(default=None, validation_alias="amount", serialization_alias="amount", description="The monetary cost of the training expressed as a decimal string, corresponding to the specified currency.")
class UpdateEmployeeTrainingRecordRequestBody(StrictModel):
    """Training object to update"""
    completed: str = Field(default=..., description="The date the training was completed, required for every update. Must follow the yyyy-mm-dd format.")
    instructor: str | None = Field(default=None, description="The full name of the person who delivered or facilitated the training.")
    hours: float | None = Field(default=None, description="The total duration of the training expressed in hours.")
    credits_: float | None = Field(default=None, validation_alias="credits", serialization_alias="credits", description="The number of credits the employee earned upon completing the training.")
    notes: str | None = Field(default=None, description="Free-text notes providing any additional context or details about the training record.")
    cost: UpdateEmployeeTrainingRecordRequestBodyCost | None = None
class UpdateEmployeeTrainingRecordRequest(StrictModel):
    """Updates an existing employee training record by its ID. The completion date is required; all other fields such as cost, instructor, hours, credits, and notes are optional."""
    path: UpdateEmployeeTrainingRecordRequestPath
    body: UpdateEmployeeTrainingRecordRequestBody

# Operation: delete_training_record
class DeleteEmployeeTrainingRecordRequestPath(StrictModel):
    employee_training_record_id: int = Field(default=..., validation_alias="employeeTrainingRecordId", serialization_alias="employeeTrainingRecordId", description="The unique identifier of the employee training record to delete.")
class DeleteEmployeeTrainingRecordRequest(StrictModel):
    """Permanently deletes an existing employee training record by its unique ID. The API key owner must have view and edit permissions for both the associated employee and training type."""
    path: DeleteEmployeeTrainingRecordRequestPath

# Operation: upload_employee_photo
class UploadEmployeePhotoRequestPath(StrictModel):
    employee_id: int = Field(default=..., validation_alias="employeeId", serialization_alias="employeeId", description="The unique numeric identifier of the employee whose photo is being uploaded.")
class UploadEmployeePhotoRequestBody(StrictModel):
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="The image file to set as the employee's photo. Must be a square image (width and height within one pixel of each other), at least 150×150 pixels, no larger than 20MB, and in JPEG, PNG, or BMP format; other formats such as HEIC, SVG, AVIF, and TIFF are not reliably supported.", json_schema_extra={'format': 'binary'})
class UploadEmployeePhotoRequest(StrictModel):
    """Uploads and replaces the photo for a specified employee, updating all size variants. The image must be a square JPEG, PNG, or BMP file of at least 150×150 pixels and no larger than 20MB; employees may upload their own photo if the company has self-photo uploads enabled."""
    path: UploadEmployeePhotoRequestPath
    body: UploadEmployeePhotoRequestBody

# Operation: list_whos_out
class ListWhosOutRequestQuery(StrictModel):
    start: str | None = Field(default=None, description="The first day of the date range to query, in YYYY-MM-DD format. Defaults to today when omitted.", json_schema_extra={'format': 'date'})
    end: str | None = Field(default=None, description="The last day of the date range to query, in YYYY-MM-DD format. Defaults to 14 days after the start date when omitted.", json_schema_extra={'format': 'date'})
    filter_: Literal["off"] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Controls visibility filtering on the results. Set to 'off' to bypass the Who's Out visibility filter and return the full unfiltered feed; omitting this parameter leaves filtering enabled.")
class ListWhosOutRequest(StrictModel):
    """Returns a date-sorted list of employees who are out and company holidays for a specified date range. Includes both time off entries and holidays, each identified by type, defaulting to today through the next 14 days when no dates are provided."""
    query: ListWhosOutRequestQuery | None = None

# ============================================================================
# Component Models
# ============================================================================

class AssignTimeOffPoliciesBodyItem(PermissiveModel):
    time_off_policy_id: int = Field(..., validation_alias="timeOffPolicyId", serialization_alias="timeOffPolicyId", description="The ID of the time off policy to assign.")
    accrual_start_date: str | None = Field(..., validation_alias="accrualStartDate", serialization_alias="accrualStartDate", description="The date accruals should start in YYYY-MM-DD format. Set to null to remove an existing assignment.", json_schema_extra={'format': 'date'})

class AssignTimeOffPoliciesV11BodyItem(PermissiveModel):
    time_off_policy_id: int = Field(..., validation_alias="timeOffPolicyId", serialization_alias="timeOffPolicyId", description="The ID of the time off policy to assign.")
    accrual_start_date: str | None = Field(..., validation_alias="accrualStartDate", serialization_alias="accrualStartDate", description="The date accruals should start in YYYY-MM-DD format. Set to null to remove an existing assignment.", json_schema_extra={'format': 'date'})

class ClockEntrySchema(PermissiveModel):
    """Schema for a single clock entry"""
    employee_id: int = Field(..., validation_alias="employeeId", serialization_alias="employeeId", description="Unique identifier for the employee.")
    date: str = Field(..., description="Date for the timesheet entry. Must be in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    start: str = Field(..., description="Start time for the timesheet entry. Local time for the employee. Must be in hh:mm 24 hour format.", pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    end: str = Field(..., description="End time for the timesheet entry. Local time for the employee. Must be in hh:mm 24 hour format.", pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of an existing timesheet entry. This can be specified to edit an existing entry.")
    project_id: int | None = Field(None, validation_alias="projectId", serialization_alias="projectId", description="The ID of the project to associate with the timesheet entry.")
    task_id: int | None = Field(None, validation_alias="taskId", serialization_alias="taskId", description="The ID of the task to associate with the timesheet entry.")
    note: str | None = Field(None, description="Optional note to associate with the timesheet entry.")
    break_id: str | None = Field(None, validation_alias="breakId", serialization_alias="breakId", description="Optional break id to associate with the timesheet entry.", json_schema_extra={'format': 'uuid'})

class Country(PermissiveModel):
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the country")
    name: str | None = Field(None, description="The name of the country")
    iso_code: str | None = Field(None, description="The ISO standard code of the country")

class CreateGoalBodyMilestonesItem(PermissiveModel):
    title: str | None = Field(None, description="The title of the milestone")

class CreateTimeOffRequestBodyDatesItem(PermissiveModel):
    ymd: str | None = Field(None, description="Date in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    amount: float | None = Field(None, description="Hours or days for this date.")

class CreateTimeOffRequestBodyNotesItem(PermissiveModel):
    from_: Literal["employee", "manager"] | None = Field(None, validation_alias="from", serialization_alias="from", description="Who the note is from.")
    note: str | None = Field(None, description="The note text.")

class CursorPaginationQueryObject(PermissiveModel):
    before: str | None = Field(None, description="Cursor pointing to the start of the previous page. Use the `prevCursor` value from the last response to paginate backward.")
    after: str | None = Field(None, description="Cursor pointing to the start of the next page. Use the `nextCursor` value from the last response to paginate forward.")
    limit: int | None = Field(50, description="Maximum number of items to return. This can be at most 100.", ge=1, le=100)

class Employee(PermissiveModel):
    """A dictionary of employee field names and their new values. The properties listed below are commonly used fields, but any valid employee field name can be used as a key. To discover all available field names, call the list-fields endpoint (operationId: list-fields, GET /api/v1/meta/fields). Only the fields you include will be updated; omitted fields are left unchanged. Some string-valued fields are backed by lists or lookups, so callers should use valid option values from BambooHR metadata rather than assuming any free-text string will persist as entered."""
    first_name: str | None = Field(None, validation_alias="firstName", serialization_alias="firstName", description="Legal first name.")
    last_name: str | None = Field(None, validation_alias="lastName", serialization_alias="lastName", description="Legal last name.")
    work_email: str | None = Field(None, validation_alias="workEmail", serialization_alias="workEmail", description="Work email address.")
    job_title: str | None = Field(None, validation_alias="jobTitle", serialization_alias="jobTitle", description="Job title.")
    department: str | None = Field(None, description="Department name.")
    division: str | None = Field(None, description="Division name.")
    location: str | None = Field(None, description="Location name.")
    hire_date: str | None = Field(None, validation_alias="hireDate", serialization_alias="hireDate", description="Hire date in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    mobile_phone: str | None = Field(None, validation_alias="mobilePhone", serialization_alias="mobilePhone", description="Mobile phone number.")
    home_phone: str | None = Field(None, validation_alias="homePhone", serialization_alias="homePhone", description="Home phone number.")
    work_phone: str | None = Field(None, validation_alias="workPhone", serialization_alias="workPhone", description="Work phone number.")
    address1: str | None = Field(None, description="Street address line 1.")
    city: str | None = Field(None, description="City.")
    state: str | None = Field(None, description="State or province. Values are normalized to standard abbreviations (e.g., \"Pennsylvania\" becomes \"PA\").")
    zipcode: str | None = Field(None, description="ZIP or postal code.")
    country: str | None = Field(None, description="Country name.")

class GetDataFromDatasetBodyAggregationsItem(PermissiveModel):
    field: str | None = None
    aggregation: Literal["count", "sum", "avg", "min", "max"] | None = None

class GetDataFromDatasetBodyFiltersFiltersItem(PermissiveModel):
    field: str | None = None
    operator: Literal["contains", "does_not_contain", "equal", "not_equal", "empty", "not_empty", "lt", "lte", "gt", "gte", "last", "next", "range", "checked", "not_checked", "includes", "does_not_include"] | None = None
    value: Any | None = None

class GetDataFromDatasetBodySortByItem(PermissiveModel):
    field: str | None = None
    sort: Literal["asc", "desc"] | None = None

class GetEmployeesFilterRequestObject(PermissiveModel):
    """Filter criteria for the employee list endpoint. All filter fields are optional. Multiple fields are combined with AND logic."""
    first_name: str | None = Field(None, validation_alias="firstName", serialization_alias="firstName", description="This will match any employees whose first name contains this string (case insensitive)")
    last_name: str | None = Field(None, validation_alias="lastName", serialization_alias="lastName", description="This will match any employees whose last name contains this string (case insensitive)")
    job_title_name: str | None = Field(None, validation_alias="jobTitleName", serialization_alias="jobTitleName", description="This will match any employees whose current job title descriptor contains this string (case insensitive)")
    status: Literal["active", "inactive"] | None = Field(None, description="Employee status")
    ids: str | list[int] | None = Field(None, description="List of employee IDs for batch fetch. Accepts repeated keys (filter[ids][]=123&filter[ids][]=124) or a single comma-separated string (filter[ids]=123,124).")

class GetFieldOptionsBodyDependentFieldsValueItem(PermissiveModel):
    field: str | None = None
    value: str | None = None

class GetFieldOptionsV12BodyDependentFieldsValueItem(PermissiveModel):
    field: str | None = None
    value: str | None = None

class HourEntrySchema(PermissiveModel):
    """Schema for a single timesheet hour entry"""
    employee_id: int | None = Field(None, validation_alias="employeeId", serialization_alias="employeeId", description="Unique identifier for the employee")
    date: str | None = Field(None, description="Date for the timesheet entry. Must be in YYYY-MM-DD format", json_schema_extra={'format': 'date'})
    hours: float | None = Field(None, description="Hours worked for this timesheet entry", json_schema_extra={'format': 'float'})
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of an existing timesheet entry. This can be specified to edit an existing entry")
    project_id: int | None = Field(None, validation_alias="projectId", serialization_alias="projectId", description="The ID of the project to associate with the timesheet entry")
    task_id: int | None = Field(None, validation_alias="taskId", serialization_alias="taskId", description="The ID of the task to associate with the timesheet entry")
    note: str | None = Field(None, description="Optional note to associate with the timesheet entry")

class State(PermissiveModel):
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the state")
    name: str | None = Field(None, description="The name of the state")
    abbrev: str | None = Field(None, description="The abbreviation of the state")
    iso_code: str | None = Field(None, description="The ISO standard code of the state")

class Location(PermissiveModel):
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the location")
    name: str | None = Field(None, description="Name of the location")
    description: str | None = Field(None, description="Description of the location")
    city: str | None = Field(None, description="City of the location")
    state: State | None = None
    country: Country | None = None
    zipcode: str | None = Field(None, description="The ZIP or postal code of the location")
    address_line1: str | None = Field(None, validation_alias="addressLine1", serialization_alias="addressLine1", description="The first address line of the location")
    address_line2: str | None = Field(None, validation_alias="addressLine2", serialization_alias="addressLine2", description="The second address line of the location")
    phone: str | None = Field(None, description="The phone number of the location")

class TaskCreateSchema(PermissiveModel):
    """Schema for creating a new task for a time tracking project"""
    name: str = Field(..., description="Name of the task.")
    billable: bool | None = Field(None, description="Indicates if the task is billable. Defaults to true if not provided.")

class TimeTrackingCreateOrUpdateTimeTrackingBreakWithoutPolicyV1(PermissiveModel):
    """Data contract for creating or updating a break"""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The unique identifier of the break. If not included, a new break will be created.", json_schema_extra={'format': 'uuid'})
    name: str | None = Field(None, description="The name of the break")
    paid: bool | None = Field(None, description="Whether the break is paid")
    duration: int | None = Field(None, description="Duration of the break in minutes")
    availability_type: Literal["anytime", "hours_worked", "time_of_day"] | None = Field(None, validation_alias="availabilityType", serialization_alias="availabilityType", description="When the break is available to be taken")
    availability_min_hours_worked: float | None = Field(None, validation_alias="availabilityMinHoursWorked", serialization_alias="availabilityMinHoursWorked", description="Minimum hours that must be worked before the break can be taken", json_schema_extra={'format': 'float'})
    availability_max_hours_worked: float | None = Field(None, validation_alias="availabilityMaxHoursWorked", serialization_alias="availabilityMaxHoursWorked", description="Maximum hours that can be worked before the break must be taken", json_schema_extra={'format': 'float'})
    availability_start_time: str | None = Field(None, validation_alias="availabilityStartTime", serialization_alias="availabilityStartTime", description="Earliest time the break can be taken (HH:MM format)", json_schema_extra={'format': 'time'})
    availability_end_time: str | None = Field(None, validation_alias="availabilityEndTime", serialization_alias="availabilityEndTime", description="Latest time the break can be taken (HH:MM format)", json_schema_extra={'format': 'time'})

class TimeTrackingRecord(PermissiveModel):
    time_tracking_id: str = Field(..., validation_alias="timeTrackingId", serialization_alias="timeTrackingId", description="A unique identifier for the record. Use this ID to adjust or delete these hours. It can be any ID you use to track the record up to 36 characters in length. (i.e. UUID).")
    employee_id: int = Field(..., validation_alias="employeeId", serialization_alias="employeeId", description="The ID of the employee.")
    division_id: int | None = Field(None, validation_alias="divisionId", serialization_alias="divisionId", description="[Optional] The ID of the division for the employee.")
    department_id: int | None = Field(None, validation_alias="departmentId", serialization_alias="departmentId", description="[Optional] The ID of the department for the employee.")
    job_title_id: int | None = Field(None, validation_alias="jobTitleId", serialization_alias="jobTitleId", description="[Optional] The ID of the job title for the employee.")
    pay_code: str | None = Field(None, validation_alias="payCode", serialization_alias="payCode", description="[Optional] Only necessary if the payroll provider requires a pay code")
    date_hours_worked: str = Field(..., validation_alias="dateHoursWorked", serialization_alias="dateHoursWorked", description="The date the hours were worked. Please use the ISO-8601 date format YYYY-MM-DD.")
    pay_rate: float | None = Field(None, validation_alias="payRate", serialization_alias="payRate", description="[Optional] The rate of pay. e.g. $15.00/hour should use 15.00 here. Only necessary if the payroll provider requires a pay rate.")
    rate_type: str = Field(..., validation_alias="rateType", serialization_alias="rateType", description="The type of hours - regular or overtime. Please use either \"REG\", \"OT\", or \"DT\" here.")
    hours_worked: float = Field(..., validation_alias="hoursWorked", serialization_alias="hoursWorked", description="The number of hours worked.")
    job_code: int | None = Field(None, validation_alias="jobCode", serialization_alias="jobCode", description="[Optional] A job code.")
    job_data: str | None = Field(None, validation_alias="jobData", serialization_alias="jobData", description="[Optional] A list of up to four 20 characters max job numbers in comma delimited format with no spaces.")

class TrainingCategory(PermissiveModel):
    """The category ID and name"""
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the training category.")
    name: str | None = Field(None, description="The name of the training category.")

class UpdateGoalV11BodyMilestonesItem(PermissiveModel):
    title: str | None = Field(None, description="The title of the milestone")

class UpdateListFieldValuesBodyOptionsItem(PermissiveModel):
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="The existing option ID. Omit this field to create a new option.")
    value: str | None = Field(None, description="The display value for the option.")
    archived: Literal["yes", "no"] | None = Field(None, description="Whether the option should be archived. Use `yes` to archive an option or `no` to keep it active.")
    adp_code: str | None = Field(None, validation_alias="adpCode", serialization_alias="adpCode", description="Optional payroll-mapping code associated with the option.")


# Rebuild models to resolve forward references (required for circular refs)
AssignTimeOffPoliciesBodyItem.model_rebuild()
AssignTimeOffPoliciesV11BodyItem.model_rebuild()
ClockEntrySchema.model_rebuild()
Country.model_rebuild()
CreateGoalBodyMilestonesItem.model_rebuild()
CreateTimeOffRequestBodyDatesItem.model_rebuild()
CreateTimeOffRequestBodyNotesItem.model_rebuild()
CursorPaginationQueryObject.model_rebuild()
Employee.model_rebuild()
GetDataFromDatasetBodyAggregationsItem.model_rebuild()
GetDataFromDatasetBodyFiltersFiltersItem.model_rebuild()
GetDataFromDatasetBodySortByItem.model_rebuild()
GetEmployeesFilterRequestObject.model_rebuild()
GetFieldOptionsBodyDependentFieldsValueItem.model_rebuild()
GetFieldOptionsV12BodyDependentFieldsValueItem.model_rebuild()
HourEntrySchema.model_rebuild()
Location.model_rebuild()
State.model_rebuild()
TaskCreateSchema.model_rebuild()
TimeTrackingCreateOrUpdateTimeTrackingBreakWithoutPolicyV1.model_rebuild()
TimeTrackingRecord.model_rebuild()
TrainingCategory.model_rebuild()
UpdateGoalV11BodyMilestonesItem.model_rebuild()
UpdateListFieldValuesBodyOptionsItem.model_rebuild()

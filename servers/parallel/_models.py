"""
Parallel Api MCP Server - Pydantic Models

Generated: 2026-04-23 21:35:26 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field


def _check_property_names_298fdb3a(v: dict) -> dict:
    """Validate all dict keys satisfy: key in ('queued', 'action_required', 'running', 'completed', 'failed', 'cancelling', 'cancelled')."""
    for _key in v:
        if _key not in ('queued', 'action_required', 'running', 'completed', 'failed', 'cancelling', 'cancelled'):
            raise ValueError(f"key '{_key}' does not satisfy: key in ('queued', 'action_required', 'running', 'completed', 'failed', 'cancelling', 'cancelled')")
    return v



__all__ = [
    "BetaExtractV1betaExtractPostRequest",
    "CreateMonitorV1alphaMonitorsPostRequest",
    "DeleteMonitorV1alphaMonitorsMonitorIdDeleteRequest",
    "FindallRunsV1V1betaFindallRunsPostRequest",
    "IngestFindallRunV1betaFindallIngestPostRequest",
    "ListMonitorEventsV1alphaMonitorsMonitorIdEventsGetRequest",
    "ListMonitorsPaginatedV1alphaMonitorsListGetRequest",
    "ListMonitorsV1alphaMonitorsGetRequest",
    "RetrieveEventGroupV1alphaMonitorsMonitorIdEventGroupsEventGroupIdGetRequest",
    "RetrieveMonitorV1alphaMonitorsMonitorIdGetRequest",
    "SimulateEventV1alphaMonitorsMonitorIdSimulateEventPostRequest",
    "TasksRunsEventsGetV1betaTasksRunsRunIdEventsGetRequest",
    "TasksRunsGetV1TasksRunsRunIdGetRequest",
    "TasksRunsInputGetV1TasksRunsRunIdInputGetRequest",
    "TasksRunsPostV1TasksRunsPostRequest",
    "TasksRunsResultGetV1TasksRunsRunIdResultGetRequest",
    "TasksSessionsEventsGetV1betaTasksGroupsTaskgroupIdEventsGetRequest",
    "TasksTaskgroupsGetV1betaTasksGroupsTaskgroupIdGetRequest",
    "TasksTaskgroupsPostV1betaTasksGroupsPostRequest",
    "TasksTaskgroupsRunsGetV1betaTasksGroupsTaskgroupIdRunsGetRequest",
    "TasksTaskgroupsRunsIdGetV1betaTasksGroupsTaskgroupIdRunsRunIdGetRequest",
    "TasksTaskgroupsRunsPostV1betaTasksGroupsTaskgroupIdRunsPostRequest",
    "UpdateMonitorV1alphaMonitorsMonitorIdPostRequest",
    "WebSearchV1betaSearchPostRequest",
    "AutoSchema",
    "BetaTaskRunInput",
    "ExcerptSettings",
    "ExcludeCandidate",
    "FullContentSettings",
    "MatchCondition",
    "McpServer",
    "MonitorWebhook",
    "TextSchema",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: search_web
class WebSearchV1betaSearchPostRequestBodyExcerpts(StrictModel):
    max_chars_per_result: int | None = Field(default=None, validation_alias="max_chars_per_result", serialization_alias="max_chars_per_result", description="Maximum characters to include per URL in excerpts. Values below 1000 are automatically increased to 1000. Excerpts may be shorter to prioritize relevance and token efficiency.")
    max_chars_total: int | None = Field(default=None, validation_alias="max_chars_total", serialization_alias="max_chars_total", description="Maximum total characters across all results combined. Values below 1000 are automatically increased to 1000. This limit applies in addition to the per-result limit to maximize relevance and token efficiency.")
class WebSearchV1betaSearchPostRequestBodySourcePolicy(StrictModel):
    include_domains: list[str] | None = Field(default=None, validation_alias="include_domains", serialization_alias="include_domains", description="List of domains to restrict results to. Accepts full domains (e.g., example.com, subdomain.example.gov) or domain extensions with leading period (e.g., .gov, .edu). Only sources from specified domains will be included.", examples=[['wikipedia.org', 'usa.gov', '.edu']])
    exclude_domains: list[str] | None = Field(default=None, validation_alias="exclude_domains", serialization_alias="exclude_domains", description="List of domains to exclude from results. Accepts full domains (e.g., example.com, subdomain.example.gov) or domain extensions with leading period (e.g., .gov, .edu). Sources from specified domains will be filtered out.", examples=[['reddit.com', 'x.com', '.ai']])
    after_date: str | None = Field(default=None, validation_alias="after_date", serialization_alias="after_date", description="Start date for filtering results, provided as an RFC 3339 date string. Only content published on or after this date will be included.", json_schema_extra={'format': 'date'}, examples=['2024-01-01'])
class WebSearchV1betaSearchPostRequestBody(StrictModel):
    mode: Literal["one-shot", "agentic", "fast"] | None = Field(default=None, description="Execution mode that presets parameter defaults for different use cases: 'one-shot' for comprehensive single-response answers, 'agentic' for token-efficient results in multi-step workflows, or 'fast' for lower-latency results with concise queries. Defaults to 'one-shot'.")
    objective: str | None = Field(default=None, description="Natural language description of the search objective, including any preferences about source types or content freshness. Either this or search_queries must be provided.")
    search_queries: list[str] | None = Field(default=None, description="List of traditional keyword search queries to guide the search, optionally including search operators. Either this or objective must be provided.")
    max_results: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 10 if not specified.")
    excerpts: WebSearchV1betaSearchPostRequestBodyExcerpts | None = None
    source_policy: WebSearchV1betaSearchPostRequestBodySourcePolicy | None = None
class WebSearchV1betaSearchPostRequest(StrictModel):
    """Search the web for information based on natural language objectives or keyword queries. Returns relevant results with excerpts optimized for the specified use case."""
    body: WebSearchV1betaSearchPostRequestBody | None = None

# Operation: extract_content_from_urls
class BetaExtractV1betaExtractPostRequestBody(StrictModel):
    urls: list[str] = Field(default=..., description="List of web URLs to extract content from. Each URL should be a valid HTTP or HTTPS address.")
    objective: str | None = Field(default=None, description="Optional search objective to focus extraction on specific topics or themes. When provided, helps filter extracted content to relevant sections.")
    search_queries: list[str] | None = Field(default=None, description="Optional list of keyword search queries to focus extraction. When provided, extracted content will prioritize sections matching these queries.")
    excerpts: bool | ExcerptSettings | None = Field(default=None, description="Whether to include excerpts from each URL relevant to the search objective and queries. Enabled by default. Most useful when objective or search_queries are specified; redundant if neither is provided.")
    full_content: bool | FullContentSettings | None = Field(default=None, description="Whether to include the complete content from each URL. Disabled by default. Enable to retrieve full page content; useful when objective and search_queries are not specified.")
class BetaExtractV1betaExtractPostRequest(StrictModel):
    """Extracts relevant content from specified web URLs, optionally focused on a search objective or keyword queries."""
    body: BetaExtractV1betaExtractPostRequestBody

# Operation: create_task_run
class TasksRunsPostV1TasksRunsPostRequestBodySourcePolicy(StrictModel):
    include_domains: list[str] | None = Field(default=None, validation_alias="include_domains", serialization_alias="include_domains", description="Restrict results to specific domains. Accepts full domains (e.g., example.com, subdomain.example.gov) or domain extensions with leading period (e.g., .gov, .edu, .co.uk). Only sources matching these domains will be included.", examples=[['wikipedia.org', 'usa.gov', '.edu']])
    exclude_domains: list[str] | None = Field(default=None, validation_alias="exclude_domains", serialization_alias="exclude_domains", description="Exclude results from specific domains. Accepts full domains (e.g., example.com, subdomain.example.gov) or domain extensions with leading period (e.g., .gov, .edu, .co.uk). Sources matching these domains will be filtered out.", examples=[['reddit.com', 'x.com', '.ai']])
    after_date: str | None = Field(default=None, validation_alias="after_date", serialization_alias="after_date", description="Filter results to content published on or after this date. Provide as an RFC 3339 date string in YYYY-MM-DD format.", json_schema_extra={'format': 'date'}, examples=['2024-01-01'])
class TasksRunsPostV1TasksRunsPostRequestBodyTaskSpec(StrictModel):
    output_schema: Any | TextSchema | AutoSchema | str = Field(default=..., validation_alias="output_schema", serialization_alias="output_schema", description="JSON schema or text description defining the desired output structure and content. Field descriptions determine the form and content of the response. A plain string is treated as a text schema.")
    input_schema: str | Any | TextSchema | None = Field(default=None, validation_alias="input_schema", serialization_alias="input_schema", description="Optional JSON schema or text description of the expected input format. A plain string is treated as a text schema with that description.")
class TasksRunsPostV1TasksRunsPostRequestBodyWebhook(StrictModel):
    url: str = Field(default=..., validation_alias="url", serialization_alias="url", description="Webhook URL where task run notifications will be sent.")
    event_types: list[Literal["task_run.status"]] | None = Field(default=None, validation_alias="event_types", serialization_alias="event_types", description="List of event types that trigger webhook notifications. Defaults to empty array (no notifications sent).")
class TasksRunsPostV1TasksRunsPostRequestBody(StrictModel):
    processor: str = Field(default=..., description="The processor type to execute the task. Use 'base' for standard processing.", examples=['base'])
    metadata: dict[str, str | int | float | bool] | None = Field(default=None, description="Custom key-value metadata to attach to the run. Keys and values must be strings, with keys limited to 16 characters and values to 512 characters.")
    input_: str | dict[str, Any] = Field(default=..., validation_alias="input", serialization_alias="input", description="The input data for the task, provided as either plain text or a JSON object matching the input schema.", examples=['What was the GDP of France in 2023?', '{"country": "France", "year": 2023}'])
    previous_interaction_id: str | None = Field(default=None, description="Reference to a previous interaction to use as context for this task run, enabling multi-turn workflows.")
    mcp_servers: list[McpServer] | None = Field(default=None, description="Optional list of MCP servers to use for this run. Requires 'mcp-server-2025-07-17' in the parallel-beta header to enable.")
    enable_events: bool | None = Field(default=None, description="Enable or disable progress event tracking for this run. When true, execution progress events are recorded and accessible via the Task Run events endpoint. Defaults to true for premium processors. Requires 'events-sse-2025-07-24' in the parallel-beta header to enable.")
    source_policy: TasksRunsPostV1TasksRunsPostRequestBodySourcePolicy | None = None
    task_spec: TasksRunsPostV1TasksRunsPostRequestBodyTaskSpec
    webhook: TasksRunsPostV1TasksRunsPostRequestBodyWebhook
class TasksRunsPostV1TasksRunsPostRequest(StrictModel):
    """Initiates a new task run that processes input according to a specified processor and output schema. Returns immediately with a run object in 'queued' status. Supports optional filtering by domain, date range, and webhook notifications."""
    body: TasksRunsPostV1TasksRunsPostRequestBody

# Operation: get_task_run
class TasksRunsGetV1TasksRunsRunIdGetRequestPath(StrictModel):
    run_id: str = Field(default=..., description="The unique identifier of the task run to retrieve.")
class TasksRunsGetV1TasksRunsRunIdGetRequest(StrictModel):
    """Retrieve the status and details of a specific task run by its ID. Use the `/result` endpoint to access the run's output results."""
    path: TasksRunsGetV1TasksRunsRunIdGetRequestPath

# Operation: get_task_run_input
class TasksRunsInputGetV1TasksRunsRunIdInputGetRequestPath(StrictModel):
    run_id: str = Field(default=..., description="The unique identifier of the task run whose input you want to retrieve.")
class TasksRunsInputGetV1TasksRunsRunIdInputGetRequest(StrictModel):
    """Retrieves the input data that was provided to a specific task run. Use this to inspect what parameters or data were passed when the task run was executed."""
    path: TasksRunsInputGetV1TasksRunsRunIdInputGetRequestPath

# Operation: get_task_run_result
class TasksRunsResultGetV1TasksRunsRunIdResultGetRequestPath(StrictModel):
    run_id: str = Field(default=..., description="The unique identifier of the task run whose result you want to retrieve.")
class TasksRunsResultGetV1TasksRunsRunIdResultGetRequest(StrictModel):
    """Retrieves the result of a completed task run by its ID. This operation blocks until the task run finishes executing, then returns the final result."""
    path: TasksRunsResultGetV1TasksRunsRunIdResultGetRequestPath

# Operation: stream_task_run_events
class TasksRunsEventsGetV1betaTasksRunsRunIdEventsGetRequestPath(StrictModel):
    run_id: str = Field(default=..., description="The unique identifier of the task run for which to retrieve events.")
class TasksRunsEventsGetV1betaTasksRunsRunIdEventsGetRequest(StrictModel):
    """Stream events for a specific task run, including progress updates and state changes. Event frequency is reduced for task runs created without event streaming enabled."""
    path: TasksRunsEventsGetV1betaTasksRunsRunIdEventsGetRequestPath

# Operation: create_task_group
class TasksTaskgroupsPostV1betaTasksGroupsPostRequestBody(StrictModel):
    metadata: dict[str, str | int | float | bool] | None = Field(default=None, description="Optional custom metadata to attach to the task group for organizational or tracking purposes. This metadata is stored with the group and can be used to add context or labels relevant to your use case.")
class TasksTaskgroupsPostV1betaTasksGroupsPostRequest(StrictModel):
    """Creates a new TaskGroup to organize and monitor multiple task runs together. Use this to establish a logical grouping for related tasks that should be tracked as a unit."""
    body: TasksTaskgroupsPostV1betaTasksGroupsPostRequestBody | None = None

# Operation: get_taskgroup
class TasksTaskgroupsGetV1betaTasksGroupsTaskgroupIdGetRequestPath(StrictModel):
    taskgroup_id: str = Field(default=..., description="The unique identifier of the TaskGroup to retrieve.")
class TasksTaskgroupsGetV1betaTasksGroupsTaskgroupIdGetRequest(StrictModel):
    """Retrieves a TaskGroup and its aggregated status across all runs, providing a summary view of the group's execution state."""
    path: TasksTaskgroupsGetV1betaTasksGroupsTaskgroupIdGetRequestPath

# Operation: stream_task_group_events
class TasksSessionsEventsGetV1betaTasksGroupsTaskgroupIdEventsGetRequestPath(StrictModel):
    taskgroup_id: str = Field(default=..., description="The unique identifier of the TaskGroup whose events should be streamed.")
class TasksSessionsEventsGetV1betaTasksGroupsTaskgroupIdEventsGetRequestQuery(StrictModel):
    last_event_id: str | None = Field(default=None, description="Optional event ID to resume streaming from a specific point, useful for recovering from connection interruptions without missing events.")
class TasksSessionsEventsGetV1betaTasksGroupsTaskgroupIdEventsGetRequest(StrictModel):
    """Streams real-time events from a TaskGroup, including status updates and run completions. The connection remains open for up to one hour while at least one run in the group is active."""
    path: TasksSessionsEventsGetV1betaTasksGroupsTaskgroupIdEventsGetRequestPath
    query: TasksSessionsEventsGetV1betaTasksGroupsTaskgroupIdEventsGetRequestQuery | None = None

# Operation: list_task_group_runs
class TasksTaskgroupsRunsGetV1betaTasksGroupsTaskgroupIdRunsGetRequestPath(StrictModel):
    taskgroup_id: str = Field(default=..., description="The unique identifier of the TaskGroup whose runs should be retrieved.")
class TasksTaskgroupsRunsGetV1betaTasksGroupsTaskgroupIdRunsGetRequestQuery(StrictModel):
    last_event_id: str | None = Field(default=None, description="Resume a stream from a specific point by providing the event_id of the last received event. The stream will continue from the next event after this cursor.")
    status: Literal["queued", "action_required", "running", "completed", "failed", "cancelling", "cancelled"] | None = Field(default=None, description="Filter runs by their current status: queued (waiting to start), action_required (awaiting user input), running (in progress), completed (finished successfully), failed (encountered an error), cancelling (cancellation in progress), or cancelled (cancellation completed).")
    include_input: bool | None = Field(default=None, description="Include the input data for each run in the stream response. Defaults to false.")
    include_output: bool | None = Field(default=None, description="Include the output data for each run in the stream response. Defaults to false.")
class TasksTaskgroupsRunsGetV1betaTasksGroupsTaskgroupIdRunsGetRequest(StrictModel):
    """Retrieves all task runs within a TaskGroup as a resumable stream, with optional inclusion of run inputs and outputs."""
    path: TasksTaskgroupsRunsGetV1betaTasksGroupsTaskgroupIdRunsGetRequestPath
    query: TasksTaskgroupsRunsGetV1betaTasksGroupsTaskgroupIdRunsGetRequestQuery | None = None

# Operation: add_runs_to_task_group
class TasksTaskgroupsRunsPostV1betaTasksGroupsTaskgroupIdRunsPostRequestPath(StrictModel):
    taskgroup_id: str = Field(default=..., description="The unique identifier of the TaskGroup to which runs will be added.")
class TasksTaskgroupsRunsPostV1betaTasksGroupsTaskgroupIdRunsPostRequestBodyDefaultTaskSpec(StrictModel):
    output_schema: Any | TextSchema | AutoSchema | str = Field(default=..., validation_alias="output_schema", serialization_alias="output_schema", description="JSON schema or text description defining the desired output structure from each task. Field descriptions in the schema will determine the form and content of task responses. A plain string is treated as a text schema with that description.")
    input_schema: str | Any | TextSchema | None = Field(default=None, validation_alias="input_schema", serialization_alias="input_schema", description="Optional JSON schema or text description specifying the expected input structure for tasks. A plain string is treated as a text schema with that description.")
class TasksTaskgroupsRunsPostV1betaTasksGroupsTaskgroupIdRunsPostRequestBody(StrictModel):
    inputs: list[BetaTaskRunInput] = Field(default=..., description="Array of task run configurations to execute. Each item represents a single task run with its input parameters. Up to 1,000 runs can be added per request; for larger batches, split across multiple requests.")
    default_task_spec: TasksTaskgroupsRunsPostV1betaTasksGroupsTaskgroupIdRunsPostRequestBodyDefaultTaskSpec
class TasksTaskgroupsRunsPostV1betaTasksGroupsTaskgroupIdRunsPostRequest(StrictModel):
    """Initiates multiple task runs within a TaskGroup, allowing batch execution of tasks with specified inputs and output requirements."""
    path: TasksTaskgroupsRunsPostV1betaTasksGroupsTaskgroupIdRunsPostRequestPath
    body: TasksTaskgroupsRunsPostV1betaTasksGroupsTaskgroupIdRunsPostRequestBody

# Operation: get_task_group_run
class TasksTaskgroupsRunsIdGetV1betaTasksGroupsTaskgroupIdRunsRunIdGetRequestPath(StrictModel):
    taskgroup_id: str = Field(default=..., description="The unique identifier of the task group containing the run.")
    run_id: str = Field(default=..., description="The unique identifier of the run whose status and details should be retrieved.")
class TasksTaskgroupsRunsIdGetV1betaTasksGroupsTaskgroupIdRunsRunIdGetRequest(StrictModel):
    """Retrieves the status and details of a specific task group run by its run ID. The run result data is available separately via the `/result` endpoint."""
    path: TasksTaskgroupsRunsIdGetV1betaTasksGroupsTaskgroupIdRunsRunIdGetRequestPath

# Operation: create_findall_spec_from_objective
class IngestFindallRunV1betaFindallIngestPostRequestBody(StrictModel):
    objective: str = Field(default=..., description="A natural language description of what you want to find. Describe your search goal in plain English, such as company characteristics, funding criteria, or other business attributes you're looking for.", examples=['Find all AI companies that raised Series A funding in 2024'])
class IngestFindallRunV1betaFindallIngestPostRequest(StrictModel):
    """Converts a natural language search objective into a structured FindAll specification that can be used to execute targeted searches. The generated spec serves as a customizable starting point and can be further refined by the user."""
    body: IngestFindallRunV1betaFindallIngestPostRequestBody

# Operation: create_findall_run
class FindallRunsV1V1betaFindallRunsPostRequestBody(StrictModel):
    objective: str = Field(default=..., description="The goal or search objective described in natural language for the FindAll run.")
    entity_type: str = Field(default=..., description="The category or type of entity to search for (e.g., company, person, product).")
    match_conditions: list[MatchCondition] = Field(default=..., description="Array of conditions that entities must satisfy to be included in results. Order and format depend on the entity type and generator used.")
    generator: Literal["base", "core", "pro", "preview"] = Field(default=..., description="The search algorithm tier to use: 'base' for basic matching, 'core' for standard accuracy, 'pro' for advanced matching, or 'preview' for experimental features.")
    match_limit: int = Field(default=..., description="Maximum number of matching entities to return, between 5 and 1000 inclusive.")
    exclude_list: list[ExcludeCandidate] | None = Field(default=None, description="Optional list of entity names or IDs to exclude from the search results.")
    metadata: dict[str, str | int | float | bool] | None = Field(default=None, description="Optional custom metadata object to attach to the FindAll run for tracking or reference purposes.")
class FindallRunsV1V1betaFindallRunsPostRequest(StrictModel):
    """Initiates a FindAll run to search for entities matching specified criteria. Returns immediately with a queued run object; use the returned run ID to poll status, stream events, or receive webhook notifications as the search progresses."""
    body: FindallRunsV1V1betaFindallRunsPostRequestBody

# Operation: list_monitors
class ListMonitorsV1alphaMonitorsGetRequestQuery(StrictModel):
    monitor_id: str | None = Field(default=None, description="Cursor for pagination—specify a monitor ID to start listing after that point in lexicographic order. Useful for fetching subsequent pages of results.")
    limit: int | None = Field(default=None, description="Maximum number of monitors to return per request, between 1 and 10,000. Omit to retrieve all monitors at once.", ge=1, le=10000)
class ListMonitorsV1alphaMonitorsGetRequest(StrictModel):
    """Retrieve all active monitors for the user with their current configuration and status. Supports cursor-based pagination to efficiently browse large monitor lists."""
    query: ListMonitorsV1alphaMonitorsGetRequestQuery | None = None

# Operation: create_monitor
class CreateMonitorV1alphaMonitorsPostRequestBody(StrictModel):
    query: str = Field(default=..., description="The search query to monitor for material changes. This query will be executed periodically according to the monitor's frequency.", examples=['Extract recent news about AI'])
    webhook: MonitorWebhook | None = Field(default=None, description="Optional webhook URL that will receive notifications whenever the monitor executes, including execution results and any detected changes.")
    metadata: dict[str, str] | None = Field(default=None, description="Optional custom metadata object to store application-specific context with the monitor. This metadata is returned in webhook notifications and GET requests, allowing you to correlate monitor responses with your application's internal objects (e.g., storing a Slack thread ID to route notifications to the correct conversation).", examples=[{'slack_thread_id': '1234567890.123456', 'user_id': 'U123ABC'}])
    output_schema: Any | None = Field(default=None, description="Optional schema definition for structuring the monitor's output events. Defines how results should be formatted in webhook notifications.")
    frequency: str | None = Field(default=None, description="How often the monitor should execute, specified as a number followed by a time unit: 'h' for hours, 'd' for days, or 'w' for weeks (e.g., '1h', '2d', '1w'). Must be between 1 hour and 30 days inclusive.", examples=['1d', '1w', '1h', '2w'])
    cadence: Literal["daily", "every_two_weeks", "hourly", "weekly"] | None = Field(default=None, description="Deprecated: use the 'frequency' field instead. Predefined execution cadence options: hourly, daily, weekly, or every two weeks.", examples=['daily', 'weekly', 'hourly', 'every_two_weeks'])
class CreateMonitorV1alphaMonitorsPostRequest(StrictModel):
    """Create a web monitor that periodically executes a search query at a specified frequency and sends updates to an optional webhook. The monitor runs immediately upon creation and then continues according to the configured schedule."""
    body: CreateMonitorV1alphaMonitorsPostRequestBody

# Operation: list_monitors_paginated
class ListMonitorsPaginatedV1alphaMonitorsListGetRequestQuery(StrictModel):
    cursor: str | None = Field(default=None, description="Opaque token for cursor-based pagination. Omit this parameter to start from the most recently created monitor, or provide the `next_cursor` value from a previous response to fetch the next page of results.")
    limit: int | None = Field(default=None, description="Maximum number of monitors to return per page. Must be between 1 and 10,000, defaults to 100 if not specified.", ge=1, le=10000)
class ListMonitorsPaginatedV1alphaMonitorsListGetRequest(StrictModel):
    """Retrieve a paginated list of active monitors ordered by creation time, newest first. Use cursor-based pagination to navigate through results."""
    query: ListMonitorsPaginatedV1alphaMonitorsListGetRequestQuery | None = None

# Operation: get_monitor
class RetrieveMonitorV1alphaMonitorsMonitorIdGetRequestPath(StrictModel):
    monitor_id: str = Field(default=..., description="The unique identifier of the monitor to retrieve.")
class RetrieveMonitorV1alphaMonitorsMonitorIdGetRequest(StrictModel):
    """Retrieve a specific monitor by its ID. Returns the complete monitor configuration including status, cadence, input settings, and webhook configuration."""
    path: RetrieveMonitorV1alphaMonitorsMonitorIdGetRequestPath

# Operation: update_monitor
class UpdateMonitorV1alphaMonitorsMonitorIdPostRequestPath(StrictModel):
    monitor_id: str = Field(default=..., description="The unique identifier of the monitor to update.")
class UpdateMonitorV1alphaMonitorsMonitorIdPostRequestBodyWebhook(StrictModel):
    url: str = Field(default=..., validation_alias="url", serialization_alias="url", description="The webhook URL where monitor notifications will be sent. Must be a valid HTTPS or HTTP endpoint.", examples=['https://example.com/webhook'])
    event_types: list[Literal["monitor.event.detected", "monitor.execution.completed", "monitor.execution.failed"]] | None = Field(default=None, validation_alias="event_types", serialization_alias="event_types", description="Event types that should trigger webhook notifications. Specify as an array of event type identifiers.")
class UpdateMonitorV1alphaMonitorsMonitorIdPostRequestBody(StrictModel):
    query: str | None = Field(default=None, description="Updated search query for the monitor. Use for minor prompt and instruction refinements only; major query changes may affect change detection accuracy since the monitor compares new results against previously cached results.", examples=['Extract recent news about AI'])
    frequency: str | None = Field(default=None, description="Updated check frequency for the monitor. Specify as a number followed by a unit: 'h' for hours, 'd' for days, or 'w' for weeks. Must be between 1 hour and 30 days inclusive.", examples=['1d', '1w', '1h', '2w'])
    metadata: dict[str, str] | None = Field(default=None, description="Custom metadata object to associate with the monitor. This metadata is included in all webhook notifications, allowing you to correlate monitor events with corresponding objects in your application.", examples=[{'slack_thread_id': '1234567890.123456', 'user_id': 'U123ABC'}])
    webhook: UpdateMonitorV1alphaMonitorsMonitorIdPostRequestBodyWebhook
class UpdateMonitorV1alphaMonitorsMonitorIdPostRequest(StrictModel):
    """Update an existing monitor's configuration, including its search query, check frequency, webhook URL, and associated metadata. At least one field must be provided to apply changes."""
    path: UpdateMonitorV1alphaMonitorsMonitorIdPostRequestPath
    body: UpdateMonitorV1alphaMonitorsMonitorIdPostRequestBody

# Operation: delete_monitor
class DeleteMonitorV1alphaMonitorsMonitorIdDeleteRequestPath(StrictModel):
    monitor_id: str = Field(default=..., description="The unique identifier of the monitor to delete.")
class DeleteMonitorV1alphaMonitorsMonitorIdDeleteRequest(StrictModel):
    """Permanently delete a monitor and stop all its future executions. Deleted monitors cannot be updated or retrieved."""
    path: DeleteMonitorV1alphaMonitorsMonitorIdDeleteRequestPath

# Operation: get_event_group
class RetrieveEventGroupV1alphaMonitorsMonitorIdEventGroupsEventGroupIdGetRequestPath(StrictModel):
    monitor_id: str = Field(default=..., description="The unique identifier of the monitor that contains the event group.")
    event_group_id: str = Field(default=..., description="The unique identifier of the event group to retrieve.")
class RetrieveEventGroupV1alphaMonitorsMonitorIdEventGroupsEventGroupIdGetRequest(StrictModel):
    """Retrieve a specific event group associated with a monitor. The response contains event items that represent individual events within the group."""
    path: RetrieveEventGroupV1alphaMonitorsMonitorIdEventGroupsEventGroupIdGetRequestPath

# Operation: list_monitor_events
class ListMonitorEventsV1alphaMonitorsMonitorIdEventsGetRequestPath(StrictModel):
    monitor_id: str = Field(default=..., description="The unique identifier of the monitor for which to retrieve events.")
class ListMonitorEventsV1alphaMonitorsMonitorIdEventsGetRequestQuery(StrictModel):
    lookback_period: str | None = Field(default=None, description="The time window to search for events, specified as a duration (e.g., '10d' for 10 days, '1w' for 1 week). Supports day and week increments with a minimum of 1 day. Defaults to 10 days if not specified.")
class ListMonitorEventsV1alphaMonitorsMonitorIdEventsGetRequest(StrictModel):
    """Retrieve events for a specific monitor, including errors and material changes from up to the last 300 event groups. Events are returned in reverse chronological order with the most recent first."""
    path: ListMonitorEventsV1alphaMonitorsMonitorIdEventsGetRequestPath
    query: ListMonitorEventsV1alphaMonitorsMonitorIdEventsGetRequestQuery | None = None

# Operation: simulate_monitor_event
class SimulateEventV1alphaMonitorsMonitorIdSimulateEventPostRequestPath(StrictModel):
    monitor_id: str = Field(default=..., description="The unique identifier of the monitor to simulate an event for.")
class SimulateEventV1alphaMonitorsMonitorIdSimulateEventPostRequestQuery(StrictModel):
    event_type: Literal["monitor.event.detected", "monitor.execution.completed", "monitor.execution.failed"] | None = Field(default=None, description="The type of event to simulate. Defaults to `monitor.event.detected` if not specified. Valid options are: `monitor.event.detected` (standard event detection), `monitor.execution.completed` (successful execution), or `monitor.execution.failed` (execution failure).", examples=['monitor.event.detected', 'monitor.execution.completed', 'monitor.execution.failed'])
class SimulateEventV1alphaMonitorsMonitorIdSimulateEventPostRequestBody(StrictModel):
    body: str | None = Field(default=None, description="Optional binary payload data to include with the simulated event.", json_schema_extra={'format': 'binary'})
class SimulateEventV1alphaMonitorsMonitorIdSimulateEventPostRequest(StrictModel):
    """Simulate sending an event to a monitor to test its event handling and triggering behavior. Useful for validating monitor configurations without waiting for real events."""
    path: SimulateEventV1alphaMonitorsMonitorIdSimulateEventPostRequestPath
    query: SimulateEventV1alphaMonitorsMonitorIdSimulateEventPostRequestQuery | None = None
    body: SimulateEventV1alphaMonitorsMonitorIdSimulateEventPostRequestBody | None = None

# ============================================================================
# Component Models
# ============================================================================

class AutoSchema(PermissiveModel):
    """Auto schema for a task input or output."""
    type_: Literal["auto"] | None = Field('auto', validation_alias="type", serialization_alias="type", description="The type of schema being defined. Always `auto`.")

class ExcerptSettings(PermissiveModel):
    """Optional settings for returning relevant excerpts."""
    max_chars_per_result: int | None = Field(None, description="Optional upper bound on the total number of characters to include per url. Excerpts may contain fewer characters than this limit to maximize relevance and token efficiency. Values below 1000 will be automatically set to 1000.")
    max_chars_total: int | None = Field(None, description="Optional upper bound on the total number of characters to include across all urls. Results may contain fewer characters than this limit to maximize relevance and token efficiency. Values below 1000 will be automatically set to 1000. This overall limit applies in addition to max_chars_per_result.")

class ExcludeCandidate(PermissiveModel):
    """Exclude candidate input model for FindAll run."""
    name: str = Field(..., description="Name of the entity to exclude from results.")
    url: str = Field(..., description="URL of the entity to exclude from results.")

class FullContentSettings(PermissiveModel):
    """Optional settings for returning full content."""
    max_chars_per_result: int | None = Field(None, description="Optional limit on the number of characters to include in the full content for each url. Full content always starts at the beginning of the page and is truncated at the limit if necessary.")

class MatchCondition(PermissiveModel):
    """Match condition model for FindAll ingest."""
    name: str = Field(..., description="Name of the match condition.")
    description: str = Field(..., description="Detailed description of the match condition. Include as much specific information as possible to help improve the quality and accuracy of Find All run results.")

class McpServer(PermissiveModel):
    """MCP server configuration."""
    type_: Literal["url"] | None = Field('url', validation_alias="type", serialization_alias="type", description="Type of MCP server being configured. Always `url`.")
    url: str = Field(..., description="URL of the MCP server.")
    headers: dict[str, str] | None = Field(None, description="Headers for the MCP server.")
    name: str = Field(..., description="Name of the MCP server.")
    allowed_tools: list[str] | None = Field(None, description="List of allowed tools for the MCP server.")

class MonitorWebhook(PermissiveModel):
    """Webhook configuration for a monitor."""
    url: str = Field(..., description="URL for the webhook.")
    event_types: list[Literal["monitor.event.detected", "monitor.execution.completed", "monitor.execution.failed"]] | None = Field(None, description="Event types to send the webhook notifications for.")

class SourcePolicy(PermissiveModel):
    """Source policy for web search results.

This policy governs which sources are allowed/disallowed in results."""
    include_domains: list[str] | None = Field(None, description="List of domains to restrict the results to. If specified, only sources from these domains will be included. Accepts plain domains (e.g., example.com, subdomain.example.gov) or bare domain extension starting with a period (e.g., .gov, .edu, .co.uk).")
    exclude_domains: list[str] | None = Field(None, description="List of domains to exclude from results. If specified, sources from these domains will be excluded. Accepts plain domains (e.g., example.com, subdomain.example.gov) or bare domain extension starting with a period (e.g., .gov, .edu, .co.uk).")
    after_date: str | None = Field(None, description="Optional start date for filtering search results. Results will be limited to content published on or after this date. Provided as an RFC 3339 date string (YYYY-MM-DD).", json_schema_extra={'format': 'date'})

class TaskSpecInputSchemaV1(PermissiveModel):
    """JSON schema for a task input or output."""
    json_schema: dict[str, Any] = Field(..., description="A JSON Schema object. Only a subset of JSON Schema is supported.")
    type_: Literal["json"] | None = Field('json', validation_alias="type", serialization_alias="type", description="The type of schema being defined. Always `json`.")

class TaskSpecOutputSchemaV0(PermissiveModel):
    """JSON schema for a task input or output."""
    json_schema: dict[str, Any] = Field(..., description="A JSON Schema object. Only a subset of JSON Schema is supported.")
    type_: Literal["json"] | None = Field('json', validation_alias="type", serialization_alias="type", description="The type of schema being defined. Always `json`.")

class TextSchema(PermissiveModel):
    """Text description for a task input or output."""
    description: str | None = Field(None, description="A text description of the desired output from the task.")
    type_: Literal["text"] | None = Field('text', validation_alias="type", serialization_alias="type", description="The type of schema being defined. Always `text`.")

class TaskSpec(PermissiveModel):
    """Specification for a task.

Auto output schemas can be specified by setting `output_schema={"type":"auto"}`. Not
specifying a TaskSpec is the same as setting an auto output schema.

For convenience bare strings are also accepted as input or output schemas."""
    output_schema: Any | TextSchema | AutoSchema | str = Field(..., description="JSON schema or text fully describing the desired output from the task. Descriptions of output fields will determine the form and content of the response. A bare string is equivalent to a text schema with the same description.")
    input_schema: str | Any | TextSchema | None = Field(None, description="Optional JSON schema or text description of expected input to the task. A bare string is equivalent to a text schema with the same description.")

class Webhook(PermissiveModel):
    """Webhooks for Task Runs."""
    url: str = Field(..., description="URL for the webhook.")
    event_types: list[Literal["task_run.status"]] | None = Field(None, description="Event types to send the webhook notifications for.")

class BetaTaskRunInput(PermissiveModel):
    """Task run input with additional beta fields."""
    processor: str = Field(..., description="Processor to use for the task.")
    metadata: dict[str, str | int | float | bool] | None = Field(None, description="User-provided metadata stored with the run. Keys and values must be strings with a maximum length of 16 and 512 characters respectively.")
    source_policy: SourcePolicy | None = Field(None, description="Optional source policy governing preferred and disallowed domains in web search results.")
    task_spec: TaskSpec | None = Field(None, description="Task specification. If unspecified, defaults to auto output schema.")
    input_: str | dict[str, Any] = Field(..., validation_alias="input", serialization_alias="input", description="Input to the task, either text or a JSON object.")
    previous_interaction_id: str | None = Field(None, description="Interaction ID to use as context for this request.")
    mcp_servers: list[McpServer] | None = Field(None, description="Optional list of MCP servers to use for the run.\nTo enable this feature in your requests, specify `mcp-server-2025-07-17` as one of the values in `parallel-beta` header (for API calls) or `betas` param (for the SDKs).")
    enable_events: bool | None = Field(None, description="Controls tracking of task run execution progress. When set to true, progress events are recorded and can be accessed via the [Task Run events](https://platform.parallel.ai/api-reference) endpoint. When false, no progress events are tracked. Note that progress tracking cannot be enabled after a run has been created. The flag is set to true by default for premium processors (pro and above).\nTo enable this feature in your requests, specify `events-sse-2025-07-24` as one of the values in `parallel-beta` header (for API calls) or `betas` param (for the SDKs).")
    webhook: Webhook | None = Field(None, description="Callback URL (webhook endpoint) that will receive an HTTP POST when the run completes. \nThis feature is not available via the Python SDK. To enable this feature in your API requests, specify the `parallel-beta` header with `webhook-2025-08-12` value.")


# Rebuild models to resolve forward references (required for circular refs)
AutoSchema.model_rebuild()
BetaTaskRunInput.model_rebuild()
ExcerptSettings.model_rebuild()
ExcludeCandidate.model_rebuild()
FullContentSettings.model_rebuild()
MatchCondition.model_rebuild()
McpServer.model_rebuild()
MonitorWebhook.model_rebuild()
SourcePolicy.model_rebuild()
TaskSpec.model_rebuild()
TaskSpecInputSchemaV1.model_rebuild()
TaskSpecOutputSchemaV0.model_rebuild()
TextSchema.model_rebuild()
Webhook.model_rebuild()

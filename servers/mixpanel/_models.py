"""
Mixpanel MCP Server - Pydantic Models

Generated: 2026-05-12 11:56:14 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import StrictModel
from pydantic import Field

__all__ = [
    "ActivityStreamQueryRequest",
    "CohortsListRequest",
    "EngageQueryRequest",
    "FunnelsListSavedRequest",
    "FunnelsQueryRequest",
    "InsightsQueryRequest",
    "ListRecentEventsRequest",
    "QueryEventPropertiesRequest",
    "QueryEventsTopPropertiesRequest",
    "QueryEventsTopPropertyValuesRequest",
    "QueryJqlRequest",
    "QueryMonthsTopEventNamesRequest",
    "QueryTopEventsRequest",
    "RetentionFrequencyQueryRequest",
    "RetentionQueryRequest",
    "SegmentationNumericQueryRequest",
    "SegmentationQueryAverageRequest",
    "SegmentationQueryRequest",
    "SegmentationSumQueryRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: get_insights_report
class InsightsQueryRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The Mixpanel project ID associated with your account.")
    bookmark_id: int = Field(default=..., description="The unique identifier of your Insights report, found in the Mixpanel URL path after 'report-' in the editor-card-id parameter.")
class InsightsQueryRequest(StrictModel):
    """Retrieve data from a saved Insights report in your Mixpanel project. Subject to a rate limit of 60 queries per hour with a maximum of 5 concurrent queries."""
    query: InsightsQueryRequestQuery

# Operation: get_funnel_data
class FunnelsQueryRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The Mixpanel project ID that contains the funnel.")
    funnel_id: int = Field(default=..., description="The ID of the funnel to retrieve data for.")
    from_date: str = Field(default=..., description="The start date for the query in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    to_date: str = Field(default=..., description="The end date for the query in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    length: int | None = Field(default=None, description="The time window for users to complete the funnel from when they trigger the first step. Maximum allowed is 90 days. If not specified, uses the value saved in the UI for this funnel.")
    length_unit: Literal["day", "hour", "minute", "second"] | None = Field(default=None, description="The unit of time for the length parameter: day, hour, minute, or second. If not specified, uses the value saved in the UI for this funnel.")
    on: str | None = Field(default=None, description="A property expression to segment funnel results by. When specified, results are grouped by the values of this property.")
    where: str | None = Field(default=None, description="An expression to filter which events are included in the funnel analysis. Only events matching this filter are considered.")
    limit: int | None = Field(default=None, description="The maximum number of top property values to return when segmenting. Defaults to 255 if not specified; maximum allowed is 10,000. This parameter has no effect if the 'on' parameter is not used.")
class FunnelsQueryRequest(StrictModel):
    """Retrieve funnel conversion data for a specified date range and funnel. Results can be segmented by user properties and filtered by event criteria. Subject to a rate limit of 60 queries per hour with a maximum of 5 concurrent queries."""
    query: FunnelsQueryRequestQuery

# Operation: list_saved_funnels
class FunnelsListSavedRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The Mixpanel project ID associated with the funnels you want to retrieve.")
class FunnelsListSavedRequest(StrictModel):
    """Retrieve a list of all saved funnels in your Mixpanel project, including their names and unique funnel identifiers."""
    query: FunnelsListSavedRequestQuery

# Operation: get_retention_report
class RetentionQueryRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The Mixpanel project ID to query retention data for.")
    from_date: str = Field(default=..., description="Start date for the retention analysis period in YYYY-MM-DD format (e.g., 2024-01-15).", json_schema_extra={'format': 'date'})
    to_date: str = Field(default=..., description="End date for the retention analysis period in YYYY-MM-DD format (e.g., 2024-01-31).", json_schema_extra={'format': 'date'})
    retention_type: Literal["birth", "compounded"] | None = Field(default=None, description="Retention measurement type: 'birth' tracks first-time user retention, while 'compounded' tracks recurring retention. Defaults to 'birth' if not specified.")
    event: str | None = Field(default=None, description="Optional event name to analyze retention for (e.g., 'Viewed report'). If omitted, retention is calculated across all events.")
    where: str | None = Field(default=None, description="Optional filter expression to segment the initial cohort by user properties (e.g., properties[\"$os\"]==\"Linux\"). Uses Mixpanel expression syntax.")
    interval_count: int | None = Field(default=None, description="Number of time intervals to return in the retention analysis; defaults to 1. The report includes a '0th' interval for events occurring within the first interval period.")
    unbounded_retention: bool | None = Field(default=None, description="When enabled, retention values accumulate from right to left, so each interval includes users retained on that day and all subsequent days. Defaults to false for standard interval-by-interval counting.")
    on: str | None = Field(default=None, description="Optional property expression to segment the returning event by (e.g., properties[\"plan_type\"]). Only applies when segmenting retention results.")
    limit: int | None = Field(default=None, description="Maximum number of segmentation values to return in results. Only used when the 'on' parameter is specified for property-based segmentation.")
class RetentionQueryRequest(StrictModel):
    """Retrieve a retention analysis report for a Mixpanel project, measuring how users return to your product over time. Supports both first-time user retention (birth) and recurring user retention (compounded) with optional event and property filtering."""
    query: RetentionQueryRequestQuery

# Operation: get_retention_frequency_report
class RetentionFrequencyQueryRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The Mixpanel project ID to query against.")
    from_date: str = Field(default=..., description="Start date for the analysis period in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    to_date: str = Field(default=..., description="End date for the analysis period in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    unit: Literal["day", "week", "month"] = Field(default=..., description="The time period granularity for the overall report: day, week, or month.")
    addiction_unit: Literal["hour", "day"] = Field(default=..., description="The granularity at which to measure action frequency: hour or day.")
    event: str | None = Field(default=None, description="The specific event name to analyze for returning user counts. If omitted, analyzes all events.")
    where: str | None = Field(default=None, description="A filter expression to narrow the returning events analyzed. Supports property-based conditions and logical operators as documented in segmentation expressions.")
    on: str | None = Field(default=None, description="A property expression to segment results by. When specified, the report breaks down metrics by distinct values of this property. Supports nested properties as documented in segmentation expressions.")
    limit: int | None = Field(default=None, description="Maximum number of segmentation values to return when segmenting by the 'on' property. Has no effect if 'on' is not specified.")
class RetentionFrequencyQueryRequest(StrictModel):
    """Retrieve a frequency report analyzing user retention and addiction patterns over a specified date range. Returns the distribution of returning user actions segmented by time unit and optional properties."""
    query: RetentionFrequencyQueryRequestQuery

# Operation: get_segmented_event_data
class SegmentationQueryRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="Your Mixpanel project identifier (numeric ID).")
    event: str = Field(default=..., description="The name of the event to query. Specify a single event name, not multiple events.")
    from_date: str = Field(default=..., description="Query start date in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    to_date: str = Field(default=..., description="Query end date in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    on: str | None = Field(default=None, description="Optional property expression to segment results by. Omit to get aggregate counts without segmentation. See segmentation expressions documentation for syntax.")
    where: str | None = Field(default=None, description="Optional filter expression to narrow events by property values. See segmentation expressions documentation for syntax.")
    limit: int | None = Field(default=None, description="Maximum number of top property values to return (defaults to 60, maximum 10,000). Only applies when segmenting with the 'on' parameter.")
    format_: Literal["csv"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="Optional output format. Set to 'csv' for comma-separated values; omit for default JSON format.")
class SegmentationQueryRequest(StrictModel):
    """Retrieve event data segmented and filtered by properties from your Mixpanel project. Results can be broken down by a specific property dimension and filtered by event criteria."""
    query: SegmentationQueryRequestQuery

# Operation: get_event_segmentation_by_numeric_buckets
class SegmentationNumericQueryRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The Mixpanel project ID to query.")
    event: str = Field(default=..., description="The name of the event to analyze. Specify a single event name, not multiple events.")
    from_date: str = Field(default=..., description="The start date for the query range in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    to_date: str = Field(default=..., description="The end date for the query range in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    on: str = Field(default=..., description="A numeric property expression to segment the event data into buckets. The property must contain numeric values.")
    where: str | None = Field(default=None, description="An optional property expression to filter which events are included in the results. Only events matching this filter will be segmented.")
class SegmentationNumericQueryRequest(StrictModel):
    """Retrieve event data segmented into numeric buckets based on a numeric property value. Results are filtered by the specified date range and optional event properties."""
    query: SegmentationNumericQueryRequestQuery

# Operation: get_event_sum_by_time
class SegmentationSumQueryRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The Mixpanel project ID to query.")
    event: str = Field(default=..., description="The name of the event to analyze. Provide a single event name, not multiple events.")
    from_date: str = Field(default=..., description="The start date for the query in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    to_date: str = Field(default=..., description="The end date for the query in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    on: str = Field(default=..., description="A numeric expression to sum for each time unit. Non-numeric expression results are treated as 0.0. Use Mixpanel expression syntax to reference event properties and perform calculations.")
    where: str | None = Field(default=None, description="Optional filter expression to narrow results to specific events. Use Mixpanel expression syntax to define conditions on event properties.")
class SegmentationSumQueryRequest(StrictModel):
    """Calculate the sum of a numeric expression for a specified event aggregated over time. Results are broken down by unit time periods within the requested date range."""
    query: SegmentationSumQueryRequestQuery

# Operation: get_event_average
class SegmentationQueryAverageRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The Mixpanel project ID to query.")
    event: str = Field(default=..., description="The name of the event to analyze. Provide a single event name, not multiple events.")
    from_date: str = Field(default=..., description="The start date for the query range in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    to_date: str = Field(default=..., description="The end date for the query range in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    on: str = Field(default=..., description="A numeric expression to average per unit time. Non-numeric expression results are treated as 0.0. Refer to the expressions documentation for valid syntax.")
    where: str | None = Field(default=None, description="Optional filter expression to narrow events by specific criteria. Refer to the expressions documentation for valid syntax.")
class SegmentationQueryAverageRequest(StrictModel):
    """Calculate the average value of a numeric expression across events within a specified date range. Results are aggregated per unit time for trend analysis."""
    query: SegmentationQueryAverageRequestQuery

# Operation: get_activity_stream_for_users
class ActivityStreamQueryRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The Mixpanel project ID that identifies which project to query.")
    distinct_ids: str = Field(default=..., description="A JSON array (as a string) of distinct user IDs for which to return activity feeds. Each ID should be a valid distinct_id from your Mixpanel project.")
    from_date: str = Field(default=..., description="The start date for the activity query in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    to_date: str = Field(default=..., description="The end date for the activity query in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
class ActivityStreamQueryRequest(StrictModel):
    """Retrieve the activity feed for specified users within a date range. Subject to a rate limit of 60 queries per hour with a maximum of 5 concurrent queries."""
    query: ActivityStreamQueryRequestQuery

# Operation: list_cohorts
class CohortsListRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The numeric identifier for your Mixpanel project.")
class CohortsListRequest(StrictModel):
    """Retrieve all saved cohorts in a Mixpanel project, including metadata such as name, ID, user count, description, creation date, and visibility settings. Use the /engage endpoint with filter_by_cohort to retrieve the actual users within a cohort."""
    query: CohortsListRequestQuery

# Operation: query_profiles
class EngageQueryRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The Mixpanel project ID to query profiles from. Required to identify which project's data to access.")
class EngageQueryRequestBody(StrictModel):
    distinct_ids: str | None = Field(default=None, description="A JSON array of distinct IDs to retrieve profiles for. When provided, limits results to only these specific user or group identifiers.")
    data_group_id: str | None = Field(default=None, description="The group key ID for querying group profiles instead of user profiles. Required when analyzing group-level analytics data rather than individual users.")
    where: str | None = Field(default=None, description="A filter expression to narrow results by profile properties or attributes. Supports complex conditions to target specific user or group segments.")
    output_properties: list[str] | None = Field(default=None, description="A JSON array of property names to include in the response. Restricting to needed properties significantly reduces data transfer and improves query performance.")
    as_of_timestamp: int | None = Field(default=None, description="A Unix timestamp specifying the point-in-time snapshot for profile data. Required when exporting more than 1,000 profiles with behavior filters to avoid caching errors.")
    filter_by_cohort: str | None = Field(default=None, description="A JSON object with an `id` key containing a cohort ID to filter profiles by cohort membership. Mutually exclusive with behavior-based filtering.")
    include_all_users: bool | None = Field(default=None, description="When using cohort filtering, set to `true` (default) to include all distinct IDs even without profiles, or `false` to return only IDs with existing profiles.")
class EngageQueryRequest(StrictModel):
    """Query user or group profiles from a Mixpanel project with optional filtering, property selection, and cohort-based retrieval to retrieve detailed profile data."""
    query: EngageQueryRequestQuery
    body: EngageQueryRequestBody | None = None

# Operation: get_event_aggregates
class ListRecentEventsRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The Mixpanel project ID to query.")
    event: str = Field(default=..., description="One or more event names to analyze, provided as a JSON array of strings (e.g., [\"play song\", \"log in\"]).")
    type_: Literal["general", "unique", "average"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of aggregation to perform: 'general' for total event counts, 'unique' for distinct user counts, or 'average' for mean values per time unit.")
    unit: Literal["minute", "hour", "day", "week", "month"] = Field(default=..., description="The time granularity for bucketing results: 'minute', 'hour', 'day', 'week', or 'month'. Note that hourly granularity is not available for unique user counts.")
    from_date: str = Field(default=..., description="The start date for the query range in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    to_date: str = Field(default=..., description="The end date for the query range in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    format_: Literal["json", "csv"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="The response format: 'json' (default) or 'csv'. Subject to rate limits of 60 queries per hour and 5 concurrent queries.")
class ListRecentEventsRequest(StrictModel):
    """Retrieve aggregated event data (counts, unique users, or averages) for specified events over a time period. Results can be broken down by minute, hour, day, week, or month granularity."""
    query: ListRecentEventsRequestQuery

# Operation: list_top_events
class QueryTopEventsRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The Mixpanel project ID to query events for.")
    type_: Literal["general", "unique", "average"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of event analysis to perform: 'general' for event frequency, 'unique' for unique user counts, or 'average' for average event values.")
    limit: int | None = Field(default=None, description="Maximum number of events to return in the results. Defaults to 100 if not specified.")
class QueryTopEventsRequest(StrictModel):
    """Retrieve today's top events ranked by frequency, including event counts and normalized percent change compared to yesterday."""
    query: QueryTopEventsRequestQuery

# Operation: list_top_event_names
class QueryMonthsTopEventNamesRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The Mixpanel project ID that identifies which project's event data to query.")
    type_: Literal["general", "unique", "average"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of event analysis to perform: 'general' for event frequency, 'unique' for distinct user counts, or 'average' for per-user averages.")
    limit: int | None = Field(default=None, description="Maximum number of top events to return in the results, up to 255. Defaults to 255 if not specified.")
class QueryMonthsTopEventNamesRequest(StrictModel):
    """Retrieve the most frequently occurring events from the past 31 days, analyzed by the specified metric type. Useful for understanding user behavior patterns and identifying key interactions in your product."""
    query: QueryMonthsTopEventNamesRequestQuery

# Operation: get_event_property_aggregates
class QueryEventPropertiesRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The Mixpanel project ID to query.")
    event: str = Field(default=..., description="The name of the event to analyze. Provide a single event name, not multiple events.")
    name: str = Field(default=..., description="The property name within the event whose values you want to aggregate.")
    values: list[str] | None = Field(default=None, description="Optional filter to analyze only specific property values. Provide as a JSON array of strings (e.g., [\"value1\", \"value2\"]). If omitted, all values are included.")
    type_: Literal["general", "unique", "average"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of aggregation to perform: 'general' for total event counts, 'unique' for distinct value counts, or 'average' for mean values.")
    unit: Literal["minute", "hour", "day", "week", "month"] = Field(default=..., description="The time bucket granularity for results: 'minute', 'hour', 'day', 'week', or 'month'. Note that hourly granularity is not available for unique analysis.")
    from_date: str = Field(default=..., description="The start date for the analysis period in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    to_date: str = Field(default=..., description="The end date for the analysis period in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    format_: Literal["json", "csv"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="The response format: 'json' (default) or 'csv'.")
    limit: int | None = Field(default=None, description="Maximum number of property values to return in results. Defaults to 255 if not specified.")
class QueryEventPropertiesRequest(StrictModel):
    """Retrieve aggregated metrics for a specific event property over a time period, supporting analysis types like total counts, unique values, or averages at various time granularities (minute through month)."""
    query: QueryEventPropertiesRequestQuery

# Operation: list_top_event_properties
class QueryEventsTopPropertiesRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The Mixpanel project ID that contains the event you want to analyze.")
    event: str = Field(default=..., description="The name of the event to retrieve properties for. Provide a single event name, not multiple events.")
    limit: int | None = Field(default=None, description="The maximum number of top properties to return in the results. Defaults to 10 if not specified.")
class QueryEventsTopPropertiesRequest(StrictModel):
    """Retrieve the most frequently used property names for a specified event in your Mixpanel project. Useful for understanding which properties are most relevant to an event's analysis."""
    query: QueryEventsTopPropertiesRequestQuery

# Operation: list_event_property_top_values
class QueryEventsTopPropertyValuesRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The Mixpanel project ID that contains the event data you want to query.")
    event: str = Field(default=..., description="The name of the event to analyze. Provide a single event name (not multiple events).")
    name: str = Field(default=..., description="The property name within the event whose top values you want to retrieve.")
    limit: int | None = Field(default=None, description="The maximum number of top values to return in the response. Defaults to 255 if not specified.")
class QueryEventsTopPropertyValuesRequest(StrictModel):
    """Retrieve the most frequently occurring values for a specific event property in Mixpanel. Useful for understanding the distribution and cardinality of property values within an event."""
    query: QueryEventsTopPropertyValuesRequestQuery

# Operation: execute_jql_script
class QueryJqlRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The numeric identifier for the Mixpanel project where the script will execute.")
class QueryJqlRequestBody(StrictModel):
    script: str = Field(default=..., description="A JavaScript function that processes events using the Mixpanel JQL API. The function receives a params object and must return aggregated event data. Typically groups events by specified dimensions and applies reducers (e.g., count, sum, average).")
    params: str | None = Field(default=None, description="A JSON object containing custom variables and configuration values made available to the script as the global params variable. Allows parameterization of script logic without modifying the script itself.", json_schema_extra={'format': 'blob'})
class QueryJqlRequest(StrictModel):
    """Execute a custom JQL script against a Mixpanel project to query and aggregate event data. The script receives optional parameters and returns results based on the defined aggregation logic."""
    query: QueryJqlRequestQuery
    body: QueryJqlRequestBody

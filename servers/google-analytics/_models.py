"""
Google Analytics MCP Server - Pydantic Models

Generated: 2026-04-09 17:22:55 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field, RootModel

__all__ = [
    "AudienceExportsCreateRequest",
    "AudienceExportsGetRequest",
    "AudienceExportsListRequest",
    "AudienceExportsQueryRequest",
    "BatchRunPivotReportsRequest",
    "BatchRunReportsRequest",
    "CheckCompatibilityRequest",
    "RunPivotReportRequest",
    "RunRealtimeReportRequest",
    "RunReportRequest",
    "Cohort",
    "Comparison",
    "DateRange",
    "Dimension",
    "FilterExpression",
    "Metric",
    "MinuteRange",
    "OrderBy",
    "Pivot",
    "RunPivotReportRequest",
    "RunReportRequest",
    "V1betaAudienceDimension",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: run_pivot_reports_batch
class BatchRunPivotReportsRequestPath(StrictModel):
    property_: str = Field(default=..., validation_alias="property", serialization_alias="property", description="The Google Analytics property identifier whose events are tracked. Specified in the URL path. This property applies to all reports in the batch, though individual requests may omit or match this value.")
class BatchRunPivotReportsRequestBody(StrictModel):
    requests: list[RunPivotReportRequest] | None = Field(default=None, description="Array of individual pivot report requests to execute. Each request generates a separate pivot report response. Maximum of 5 requests allowed per batch.")
class BatchRunPivotReportsRequest(StrictModel):
    """Execute multiple pivot reports in a single batch request for a Google Analytics property. All reports must belong to the same property, with support for up to 5 requests per batch."""
    path: BatchRunPivotReportsRequestPath
    body: BatchRunPivotReportsRequestBody | None = None

# Operation: run_reports_batch
class BatchRunReportsRequestPath(StrictModel):
    property_: str = Field(default=..., validation_alias="property", serialization_alias="property", description="The Google Analytics property identifier whose events are tracked. Specified in the URL path. The property must be consistent across all batch requests.")
class BatchRunReportsRequestBody(StrictModel):
    requests: list[RunReportRequest] | None = Field(default=None, description="Array of individual report requests to execute. Each request generates a separate report response. Order is preserved in the response. Maximum of 5 requests allowed per batch.")
class BatchRunReportsRequest(StrictModel):
    """Execute multiple analytics reports in a single batch request for a Google Analytics property. All reports must belong to the same property, with support for up to 5 requests per batch."""
    path: BatchRunReportsRequestPath
    body: BatchRunReportsRequestBody | None = None

# Operation: validate_report_compatibility
class CheckCompatibilityRequestPath(StrictModel):
    property_: str = Field(default=..., validation_alias="property", serialization_alias="property", description="The Google Analytics property identifier (format: properties/PROPERTY_ID) whose events are tracked. Must match the property used in your runReport request.")
class CheckCompatibilityRequestBodyDimensionFilterOrGroup(StrictModel):
    expressions: list[FilterExpression] | None = Field(default=None, validation_alias="expressions", serialization_alias="expressions", description="A list of dimension filter expressions combined with OR logic. All expressions in this list are evaluated and combined.")
class CheckCompatibilityRequestBodyDimensionFilterFilterBetweenFilter(StrictModel):
    to_value: dict[str, Any] | None = Field(default=None, validation_alias="toValue", serialization_alias="toValue", description="The upper bound (inclusive) for a between filter on dimensions. Accepts numeric or date values.")
class CheckCompatibilityRequestBodyDimensionFilterFilterStringFilter(StrictModel):
    case_sensitive: bool | None = Field(default=None, validation_alias="caseSensitive", serialization_alias="caseSensitive", description="If true, string matching for dimension filters is case-sensitive.")
    value: str | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The string value to match against dimension values.")
    match_type: Literal["MATCH_TYPE_UNSPECIFIED", "EXACT", "BEGINS_WITH", "ENDS_WITH", "CONTAINS", "FULL_REGEXP", "PARTIAL_REGEXP"] | None = Field(default=None, validation_alias="matchType", serialization_alias="matchType", description="The string matching type for dimension filters (e.g., exact match, contains, regex).")
class CheckCompatibilityRequestBodyDimensionFilterFilterInListFilter(StrictModel):
    values: list[str] | None = Field(default=None, validation_alias="values", serialization_alias="values", description="A non-empty list of string values to match against dimension values using the in-list filter.")
class CheckCompatibilityRequestBodyDimensionFilterFilterNumericFilter(StrictModel):
    operation: Literal["OPERATION_UNSPECIFIED", "EQUAL", "LESS_THAN", "LESS_THAN_OR_EQUAL", "GREATER_THAN", "GREATER_THAN_OR_EQUAL"] | None = Field(default=None, validation_alias="operation", serialization_alias="operation", description="The comparison operation to apply for numeric dimension filtering.")
    value: dict[str, Any] | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The numeric or date value to compare against for dimension filtering.")
class CheckCompatibilityRequestBodyDimensionFilterFilter(StrictModel):
    empty_filter: dict[str, Any] | None = Field(default=None, validation_alias="emptyFilter", serialization_alias="emptyFilter", description="Filters dimension values that are empty, such as \"(not set)\" or empty strings.")
    between_filter: CheckCompatibilityRequestBodyDimensionFilterFilterBetweenFilter | None = Field(default=None, validation_alias="betweenFilter", serialization_alias="betweenFilter")
    string_filter: CheckCompatibilityRequestBodyDimensionFilterFilterStringFilter | None = Field(default=None, validation_alias="stringFilter", serialization_alias="stringFilter")
    in_list_filter: CheckCompatibilityRequestBodyDimensionFilterFilterInListFilter | None = Field(default=None, validation_alias="inListFilter", serialization_alias="inListFilter")
    numeric_filter: CheckCompatibilityRequestBodyDimensionFilterFilterNumericFilter | None = Field(default=None, validation_alias="numericFilter", serialization_alias="numericFilter")
class CheckCompatibilityRequestBodyDimensionFilter(StrictModel):
    not_expression: FilterExpression | None = Field(default=None, validation_alias="notExpression", serialization_alias="notExpression", description="A NOT expression that inverts the logic of the dimension filter.")
    or_group: CheckCompatibilityRequestBodyDimensionFilterOrGroup | None = Field(default=None, validation_alias="orGroup", serialization_alias="orGroup")
    filter_: CheckCompatibilityRequestBodyDimensionFilterFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter")
class CheckCompatibilityRequestBodyMetricFilterAndGroup(StrictModel):
    expressions: list[FilterExpression] | None = Field(default=None, validation_alias="expressions", serialization_alias="expressions", description="A list of metric filter expressions combined with AND logic. All expressions in this list must be satisfied.")
class CheckCompatibilityRequestBodyMetricFilterOrGroup(StrictModel):
    expressions: list[FilterExpression] | None = Field(default=None, validation_alias="expressions", serialization_alias="expressions", description="A list of metric filter expressions combined with OR logic. All expressions in this list are evaluated and combined.")
class CheckCompatibilityRequestBodyMetricFilterFilterBetweenFilter(StrictModel):
    from_value: dict[str, Any] | None = Field(default=None, validation_alias="fromValue", serialization_alias="fromValue", description="The lower bound (inclusive) for a between filter on metrics. Accepts numeric or date values.")
    to_value: dict[str, Any] | None = Field(default=None, validation_alias="toValue", serialization_alias="toValue", description="The upper bound (inclusive) for a between filter on metrics. Accepts numeric or date values.")
class CheckCompatibilityRequestBodyMetricFilterFilterInListFilter(StrictModel):
    case_sensitive: bool | None = Field(default=None, validation_alias="caseSensitive", serialization_alias="caseSensitive", description="If true, string matching for metric in-list filters is case-sensitive.")
    values: list[str] | None = Field(default=None, validation_alias="values", serialization_alias="values", description="A non-empty list of string values to match against metric values using the in-list filter.")
class CheckCompatibilityRequestBodyMetricFilterFilterStringFilter(StrictModel):
    case_sensitive: bool | None = Field(default=None, validation_alias="caseSensitive", serialization_alias="caseSensitive", description="If true, string matching for metric filters is case-sensitive.")
    value: str | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The string value to match against metric values.")
    match_type: Literal["MATCH_TYPE_UNSPECIFIED", "EXACT", "BEGINS_WITH", "ENDS_WITH", "CONTAINS", "FULL_REGEXP", "PARTIAL_REGEXP"] | None = Field(default=None, validation_alias="matchType", serialization_alias="matchType", description="The string matching type for metric filters (e.g., exact match, contains, regex).")
class CheckCompatibilityRequestBodyMetricFilterFilterNumericFilter(StrictModel):
    operation: Literal["OPERATION_UNSPECIFIED", "EQUAL", "LESS_THAN", "LESS_THAN_OR_EQUAL", "GREATER_THAN", "GREATER_THAN_OR_EQUAL"] | None = Field(default=None, validation_alias="operation", serialization_alias="operation", description="The comparison operation to apply for numeric metric filtering.")
    value: dict[str, Any] | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The numeric or date value to compare against for metric filtering.")
class CheckCompatibilityRequestBodyMetricFilterFilter(StrictModel):
    empty_filter: dict[str, Any] | None = Field(default=None, validation_alias="emptyFilter", serialization_alias="emptyFilter", description="Filters metric values that are empty, such as \"(not set)\" or empty strings.")
    field_name: str | None = Field(default=None, validation_alias="fieldName", serialization_alias="fieldName", description="The dimension or metric name to filter on. In pivot reports, this field must also be specified in the dimensions or metrics array.")
    between_filter: CheckCompatibilityRequestBodyMetricFilterFilterBetweenFilter | None = Field(default=None, validation_alias="betweenFilter", serialization_alias="betweenFilter")
    in_list_filter: CheckCompatibilityRequestBodyMetricFilterFilterInListFilter | None = Field(default=None, validation_alias="inListFilter", serialization_alias="inListFilter")
    string_filter: CheckCompatibilityRequestBodyMetricFilterFilterStringFilter | None = Field(default=None, validation_alias="stringFilter", serialization_alias="stringFilter")
    numeric_filter: CheckCompatibilityRequestBodyMetricFilterFilterNumericFilter | None = Field(default=None, validation_alias="numericFilter", serialization_alias="numericFilter")
class CheckCompatibilityRequestBodyMetricFilter(StrictModel):
    not_expression: FilterExpression | None = Field(default=None, validation_alias="notExpression", serialization_alias="notExpression", description="A NOT expression that inverts the logic of the metric filter.")
    and_group: CheckCompatibilityRequestBodyMetricFilterAndGroup | None = Field(default=None, validation_alias="andGroup", serialization_alias="andGroup")
    or_group: CheckCompatibilityRequestBodyMetricFilterOrGroup | None = Field(default=None, validation_alias="orGroup", serialization_alias="orGroup")
    filter_: CheckCompatibilityRequestBodyMetricFilterFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter")
class CheckCompatibilityRequestBody(StrictModel):
    compatibility_filter: Literal["COMPATIBILITY_UNSPECIFIED", "COMPATIBLE", "INCOMPATIBLE"] | None = Field(default=None, validation_alias="compatibilityFilter", serialization_alias="compatibilityFilter", description="Filters the response to return only dimensions and metrics matching this compatibility status.")
    dimensions: list[Dimension] | None = Field(default=None, description="The list of dimension names to validate for compatibility. Must match the dimensions used in your runReport request.")
    metrics: list[Metric] | None = Field(default=None, description="The list of metric names to validate for compatibility. Must match the metrics used in your runReport request.")
    dimension_filter: CheckCompatibilityRequestBodyDimensionFilter | None = Field(default=None, validation_alias="dimensionFilter", serialization_alias="dimensionFilter")
    metric_filter: CheckCompatibilityRequestBodyMetricFilter | None = Field(default=None, validation_alias="metricFilter", serialization_alias="metricFilter")
class CheckCompatibilityRequest(StrictModel):
    """Validates whether a set of dimensions and metrics can be used together in a Core report, and returns compatible or incompatible dimensions and metrics. Use this to identify which dimensions and metrics need to be removed to create a valid report."""
    path: CheckCompatibilityRequestPath
    body: CheckCompatibilityRequestBody | None = None

# Operation: get_audience_export
class AudienceExportsGetRequestPath(StrictModel):
    name: str = Field(default=..., description="The resource identifier for the audience export in the format properties/{property}/audienceExports/{audience_export}, where property is your Google Analytics property ID and audience_export is the unique export identifier.")
class AudienceExportsGetRequest(StrictModel):
    """Retrieves configuration metadata for a specific audience export, including its status and settings. Use this to inspect an audience export after creation or to monitor its progress."""
    path: AudienceExportsGetRequestPath

# Operation: generate_pivot_report
class RunPivotReportRequestPath(StrictModel):
    property_: str = Field(default=..., validation_alias="property", serialization_alias="property", description="The Google Analytics property identifier whose events are tracked. Found in your Google Analytics account settings.")
class RunPivotReportRequestBodyCohortSpecCohortReportSettings(StrictModel):
    accumulate: bool | None = Field(default=None, validation_alias="accumulate", serialization_alias="accumulate", description="If true, accumulates results from the first touch day through the end date. Not supported for standard reports.")
class RunPivotReportRequestBodyCohortSpecCohortsRange(StrictModel):
    end_offset: int | None = Field(default=None, validation_alias="endOffset", serialization_alias="endOffset", description="The end offset for the extended reporting date range in a cohort report, specified as a positive integer. The actual end date is calculated by multiplying this offset by the granularity unit (days, weeks, or months).", json_schema_extra={'format': 'int32'})
    granularity: Literal["GRANULARITY_UNSPECIFIED", "DAILY", "WEEKLY", "MONTHLY"] | None = Field(default=None, validation_alias="granularity", serialization_alias="granularity", description="The time unit granularity used to interpret start and end offsets in cohort reports (daily, weekly, or monthly).")
    start_offset: int | None = Field(default=None, validation_alias="startOffset", serialization_alias="startOffset", description="The start offset for the extended reporting date range in a cohort report, specified as a positive integer. Commonly set to 0 to include data from cohort acquisition forward. The actual start date is calculated by multiplying this offset by the granularity unit.", json_schema_extra={'format': 'int32'})
class RunPivotReportRequestBodyCohortSpec(StrictModel):
    cohorts: list[Cohort] | None = Field(default=None, validation_alias="cohorts", serialization_alias="cohorts", description="Defines selection criteria to group users into cohorts for cohort analysis. Most cohort reports use a single cohort; multiple cohorts are distinguished by their assigned names.")
    cohort_report_settings: RunPivotReportRequestBodyCohortSpecCohortReportSettings | None = Field(default=None, validation_alias="cohortReportSettings", serialization_alias="cohortReportSettings")
    cohorts_range: RunPivotReportRequestBodyCohortSpecCohortsRange | None = Field(default=None, validation_alias="cohortsRange", serialization_alias="cohortsRange")
class RunPivotReportRequestBodyDimensionFilterAndGroup(StrictModel):
    expressions: list[FilterExpression] | None = Field(default=None, validation_alias="expressions", serialization_alias="expressions", description="Dimension filter expressions combined with AND logic. All expressions must be satisfied for a row to be included.")
class RunPivotReportRequestBodyDimensionFilterOrGroup(StrictModel):
    expressions: list[FilterExpression] | None = Field(default=None, validation_alias="expressions", serialization_alias="expressions", description="Dimension filter expressions combined with OR logic. At least one expression must be satisfied for a row to be included.")
class RunPivotReportRequestBodyDimensionFilterFilterBetweenFilter(StrictModel):
    from_value: dict[str, Any] | None = Field(default=None, validation_alias="fromValue", serialization_alias="fromValue", description="The lower bound (inclusive) for a between filter on dimensions. Specifies where the range begins.")
    to_value: dict[str, Any] | None = Field(default=None, validation_alias="toValue", serialization_alias="toValue", description="The upper bound (inclusive) for a between filter on dimensions. Specifies where the range ends.")
class RunPivotReportRequestBodyDimensionFilterFilterInListFilter(StrictModel):
    case_sensitive: bool | None = Field(default=None, validation_alias="caseSensitive", serialization_alias="caseSensitive", description="If true, dimension filter string matching is case-sensitive. If false, matching is case-insensitive.")
    values: list[str] | None = Field(default=None, validation_alias="values", serialization_alias="values", description="List of string values for dimension in-list filtering. At least one value must be provided.")
class RunPivotReportRequestBodyDimensionFilterFilterStringFilter(StrictModel):
    case_sensitive: bool | None = Field(default=None, validation_alias="caseSensitive", serialization_alias="caseSensitive", description="If true, dimension filter string matching is case-sensitive. If false, matching is case-insensitive.")
    value: str | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The string value to match in dimension filters.")
    match_type: Literal["MATCH_TYPE_UNSPECIFIED", "EXACT", "BEGINS_WITH", "ENDS_WITH", "CONTAINS", "FULL_REGEXP", "PARTIAL_REGEXP"] | None = Field(default=None, validation_alias="matchType", serialization_alias="matchType", description="The string matching strategy for dimension filters (exact match, begins with, contains, regex, etc.).")
class RunPivotReportRequestBodyDimensionFilterFilterNumericFilter(StrictModel):
    operation: Literal["OPERATION_UNSPECIFIED", "EQUAL", "LESS_THAN", "LESS_THAN_OR_EQUAL", "GREATER_THAN", "GREATER_THAN_OR_EQUAL"] | None = Field(default=None, validation_alias="operation", serialization_alias="operation", description="The comparison operation for numeric dimension filtering (equal, less than, greater than, etc.).")
    value: dict[str, Any] | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The numeric or date value to compare against in dimension filters.")
class RunPivotReportRequestBodyDimensionFilterFilter(StrictModel):
    empty_filter: dict[str, Any] | None = Field(default=None, validation_alias="emptyFilter", serialization_alias="emptyFilter", description="Filters dimension values that are empty, such as '(not set)' or blank strings.")
    field_name: str | None = Field(default=None, validation_alias="fieldName", serialization_alias="fieldName", description="The dimension or metric name to filter. In pivot reports, this field must also be explicitly included in the dimensions or metrics array.")
    between_filter: RunPivotReportRequestBodyDimensionFilterFilterBetweenFilter | None = Field(default=None, validation_alias="betweenFilter", serialization_alias="betweenFilter")
    in_list_filter: RunPivotReportRequestBodyDimensionFilterFilterInListFilter | None = Field(default=None, validation_alias="inListFilter", serialization_alias="inListFilter")
    string_filter: RunPivotReportRequestBodyDimensionFilterFilterStringFilter | None = Field(default=None, validation_alias="stringFilter", serialization_alias="stringFilter")
    numeric_filter: RunPivotReportRequestBodyDimensionFilterFilterNumericFilter | None = Field(default=None, validation_alias="numericFilter", serialization_alias="numericFilter")
class RunPivotReportRequestBodyDimensionFilter(StrictModel):
    not_expression: FilterExpression | None = Field(default=None, validation_alias="notExpression", serialization_alias="notExpression", description="Negates the dimension filter expression. The filter matches rows where the expression is false.")
    and_group: RunPivotReportRequestBodyDimensionFilterAndGroup | None = Field(default=None, validation_alias="andGroup", serialization_alias="andGroup")
    or_group: RunPivotReportRequestBodyDimensionFilterOrGroup | None = Field(default=None, validation_alias="orGroup", serialization_alias="orGroup")
    filter_: RunPivotReportRequestBodyDimensionFilterFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter")
class RunPivotReportRequestBodyMetricFilterAndGroup(StrictModel):
    expressions: list[FilterExpression] | None = Field(default=None, validation_alias="expressions", serialization_alias="expressions", description="Metric filter expressions combined with AND logic. All expressions must be satisfied for a row to be included.")
class RunPivotReportRequestBodyMetricFilterOrGroup(StrictModel):
    expressions: list[FilterExpression] | None = Field(default=None, validation_alias="expressions", serialization_alias="expressions", description="Metric filter expressions combined with OR logic. At least one expression must be satisfied for a row to be included.")
class RunPivotReportRequestBodyMetricFilterFilterBetweenFilter(StrictModel):
    from_value: dict[str, Any] | None = Field(default=None, validation_alias="fromValue", serialization_alias="fromValue", description="The lower bound (inclusive) for a between filter on metrics. Specifies where the range begins.")
    to_value: dict[str, Any] | None = Field(default=None, validation_alias="toValue", serialization_alias="toValue", description="The upper bound (inclusive) for a between filter on metrics. Specifies where the range ends.")
class RunPivotReportRequestBodyMetricFilterFilterInListFilter(StrictModel):
    case_sensitive: bool | None = Field(default=None, validation_alias="caseSensitive", serialization_alias="caseSensitive", description="If true, metric filter string matching is case-sensitive. If false, matching is case-insensitive.")
    values: list[str] | None = Field(default=None, validation_alias="values", serialization_alias="values", description="List of string values for metric in-list filtering. At least one value must be provided.")
class RunPivotReportRequestBodyMetricFilterFilterStringFilter(StrictModel):
    case_sensitive: bool | None = Field(default=None, validation_alias="caseSensitive", serialization_alias="caseSensitive", description="If true, metric filter string matching is case-sensitive. If false, matching is case-insensitive.")
    value: str | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The string value to match in metric filters.")
    match_type: Literal["MATCH_TYPE_UNSPECIFIED", "EXACT", "BEGINS_WITH", "ENDS_WITH", "CONTAINS", "FULL_REGEXP", "PARTIAL_REGEXP"] | None = Field(default=None, validation_alias="matchType", serialization_alias="matchType", description="The string matching strategy for metric filters (exact match, begins with, contains, regex, etc.).")
class RunPivotReportRequestBodyMetricFilterFilterNumericFilter(StrictModel):
    operation: Literal["OPERATION_UNSPECIFIED", "EQUAL", "LESS_THAN", "LESS_THAN_OR_EQUAL", "GREATER_THAN", "GREATER_THAN_OR_EQUAL"] | None = Field(default=None, validation_alias="operation", serialization_alias="operation", description="The comparison operation for numeric metric filtering (equal, less than, greater than, etc.).")
    value: dict[str, Any] | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The numeric or date value to compare against in metric filters.")
class RunPivotReportRequestBodyMetricFilterFilter(StrictModel):
    empty_filter: dict[str, Any] | None = Field(default=None, validation_alias="emptyFilter", serialization_alias="emptyFilter", description="Filters metric values that are empty, such as '(not set)' or blank strings.")
    field_name: str | None = Field(default=None, validation_alias="fieldName", serialization_alias="fieldName", description="The dimension or metric name to filter. In pivot reports, this field must also be explicitly included in the dimensions or metrics array.")
    between_filter: RunPivotReportRequestBodyMetricFilterFilterBetweenFilter | None = Field(default=None, validation_alias="betweenFilter", serialization_alias="betweenFilter")
    in_list_filter: RunPivotReportRequestBodyMetricFilterFilterInListFilter | None = Field(default=None, validation_alias="inListFilter", serialization_alias="inListFilter")
    string_filter: RunPivotReportRequestBodyMetricFilterFilterStringFilter | None = Field(default=None, validation_alias="stringFilter", serialization_alias="stringFilter")
    numeric_filter: RunPivotReportRequestBodyMetricFilterFilterNumericFilter | None = Field(default=None, validation_alias="numericFilter", serialization_alias="numericFilter")
class RunPivotReportRequestBodyMetricFilter(StrictModel):
    not_expression: FilterExpression | None = Field(default=None, validation_alias="notExpression", serialization_alias="notExpression", description="Negates the metric filter expression. The filter matches rows where the expression is false.")
    and_group: RunPivotReportRequestBodyMetricFilterAndGroup | None = Field(default=None, validation_alias="andGroup", serialization_alias="andGroup")
    or_group: RunPivotReportRequestBodyMetricFilterOrGroup | None = Field(default=None, validation_alias="orGroup", serialization_alias="orGroup")
    filter_: RunPivotReportRequestBodyMetricFilterFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter")
class RunPivotReportRequestBody(StrictModel):
    comparisons: list[Comparison] | None = Field(default=None, description="Configuration for comparison columns in the report. Requires both this field and a comparisons dimension to display comparison data.")
    currency_code: str | None = Field(default=None, validation_alias="currencyCode", serialization_alias="currencyCode", description="ISO 4217 currency code for monetary values in the report. If unspecified, uses the property's default currency.")
    date_ranges: list[DateRange] | None = Field(default=None, validation_alias="dateRanges", serialization_alias="dateRanges", description="Date ranges for retrieving event data. Multiple ranges can be specified to compare data across periods. Include the special 'dateRange' dimension in pivots to compare between ranges. Omit for cohort requests.")
    dimensions: list[Dimension] | None = Field(default=None, description="The dimensions to include in the report. All specified dimensions must be used in at least one pivot, dimension filter, or order by clause.")
    keep_empty_rows: bool | None = Field(default=None, validation_alias="keepEmptyRows", serialization_alias="keepEmptyRows", description="If false, rows with all metrics equal to zero are excluded from results. If true, zero-value rows are included unless removed by filters. Only data actually recorded by the property appears in the report.")
    metrics: list[Metric] | None = Field(default=None, description="The metrics to include in the report. At least one metric is required. All specified metrics must be used in a metric filter, order by clause, or metric expression.")
    pivots: list[Pivot] | None = Field(default=None, description="Defines how dimensions are organized visually as rows or columns in the pivot report. All dimension names in pivots must be declared in the dimensions array. Each dimension can appear in only one pivot.")
    return_property_quota: bool | None = Field(default=None, validation_alias="returnPropertyQuota", serialization_alias="returnPropertyQuota", description="If true, returns the current quota status for this Google Analytics property, including usage and limits.")
    cohort_spec: RunPivotReportRequestBodyCohortSpec | None = Field(default=None, validation_alias="cohortSpec", serialization_alias="cohortSpec")
    dimension_filter: RunPivotReportRequestBodyDimensionFilter | None = Field(default=None, validation_alias="dimensionFilter", serialization_alias="dimensionFilter")
    metric_filter: RunPivotReportRequestBodyMetricFilter | None = Field(default=None, validation_alias="metricFilter", serialization_alias="metricFilter")
class RunPivotReportRequest(StrictModel):
    """Generate a customized pivot report of Google Analytics event data with advanced dimensional analysis. Pivot reports allow dimensions to be organized in rows or columns, with support for multiple pivots to further segment and analyze your data."""
    path: RunPivotReportRequestPath
    body: RunPivotReportRequestBody | None = None

# Operation: get_realtime_report
class RunRealtimeReportRequestPath(StrictModel):
    property_: str = Field(default=..., validation_alias="property", serialization_alias="property", description="The Google Analytics property identifier whose events are tracked. Format: properties/{propertyId}. Find your Property ID in your Google Analytics account settings.")
class RunRealtimeReportRequestBodyDimensionFilterOrGroup(StrictModel):
    expressions: list[FilterExpression] | None = Field(default=None, validation_alias="expressions", serialization_alias="expressions", description="Filter expressions to apply to dimensions. Multiple expressions are combined with OR logic.")
class RunRealtimeReportRequestBodyDimensionFilter(StrictModel):
    or_group: RunRealtimeReportRequestBodyDimensionFilterOrGroup | None = Field(default=None, validation_alias="orGroup", serialization_alias="orGroup")
class RunRealtimeReportRequestBodyMetricFilterAndGroup(StrictModel):
    expressions: list[FilterExpression] | None = Field(default=None, validation_alias="expressions", serialization_alias="expressions", description="Filter expressions to apply to metrics. Multiple expressions are combined with AND logic.")
class RunRealtimeReportRequestBodyMetricFilterOrGroup(StrictModel):
    expressions: list[FilterExpression] | None = Field(default=None, validation_alias="expressions", serialization_alias="expressions", description="Filter expressions to apply to metrics. Multiple expressions are combined with OR logic.")
class RunRealtimeReportRequestBodyMetricFilterFilterBetweenFilter(StrictModel):
    from_value: dict[str, Any] | None = Field(default=None, validation_alias="fromValue", serialization_alias="fromValue", description="The lower bound (inclusive) for a numeric range filter on metrics.")
    to_value: dict[str, Any] | None = Field(default=None, validation_alias="toValue", serialization_alias="toValue", description="The upper bound (inclusive) for a numeric range filter on metrics.")
class RunRealtimeReportRequestBodyMetricFilterFilterInListFilter(StrictModel):
    case_sensitive: bool | None = Field(default=None, validation_alias="caseSensitive", serialization_alias="caseSensitive", description="Whether string matching in the in-list filter is case-sensitive. Defaults to false.")
    values: list[str] | None = Field(default=None, validation_alias="values", serialization_alias="values", description="A list of string values to match against. At least one value is required.")
class RunRealtimeReportRequestBodyMetricFilterFilterStringFilter(StrictModel):
    case_sensitive: bool | None = Field(default=None, validation_alias="caseSensitive", serialization_alias="caseSensitive", description="Whether string matching in the string filter is case-sensitive. Defaults to false.")
    value: str | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The string value to match against in the filter.")
    match_type: Literal["MATCH_TYPE_UNSPECIFIED", "EXACT", "BEGINS_WITH", "ENDS_WITH", "CONTAINS", "FULL_REGEXP", "PARTIAL_REGEXP"] | None = Field(default=None, validation_alias="matchType", serialization_alias="matchType", description="The matching strategy for the string filter.")
class RunRealtimeReportRequestBodyMetricFilterFilterNumericFilter(StrictModel):
    operation: Literal["OPERATION_UNSPECIFIED", "EQUAL", "LESS_THAN", "LESS_THAN_OR_EQUAL", "GREATER_THAN", "GREATER_THAN_OR_EQUAL"] | None = Field(default=None, validation_alias="operation", serialization_alias="operation", description="The comparison operation to apply for numeric filtering.")
    value: dict[str, Any] | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The numeric or date value to compare against in the filter operation.")
class RunRealtimeReportRequestBodyMetricFilterFilter(StrictModel):
    empty_filter: dict[str, Any] | None = Field(default=None, validation_alias="emptyFilter", serialization_alias="emptyFilter", description="Filter to match empty or unset values in a dimension or metric.")
    field_name: str | None = Field(default=None, validation_alias="fieldName", serialization_alias="fieldName", description="The name of the dimension or metric to filter on. Must be a valid Google Analytics dimension or metric name.")
    between_filter: RunRealtimeReportRequestBodyMetricFilterFilterBetweenFilter | None = Field(default=None, validation_alias="betweenFilter", serialization_alias="betweenFilter")
    in_list_filter: RunRealtimeReportRequestBodyMetricFilterFilterInListFilter | None = Field(default=None, validation_alias="inListFilter", serialization_alias="inListFilter")
    string_filter: RunRealtimeReportRequestBodyMetricFilterFilterStringFilter | None = Field(default=None, validation_alias="stringFilter", serialization_alias="stringFilter")
    numeric_filter: RunRealtimeReportRequestBodyMetricFilterFilterNumericFilter | None = Field(default=None, validation_alias="numericFilter", serialization_alias="numericFilter")
class RunRealtimeReportRequestBodyMetricFilter(StrictModel):
    not_expression: FilterExpression | None = Field(default=None, validation_alias="notExpression", serialization_alias="notExpression", description="Logical NOT expression to negate the filter condition.")
    and_group: RunRealtimeReportRequestBodyMetricFilterAndGroup | None = Field(default=None, validation_alias="andGroup", serialization_alias="andGroup")
    or_group: RunRealtimeReportRequestBodyMetricFilterOrGroup | None = Field(default=None, validation_alias="orGroup", serialization_alias="orGroup")
    filter_: RunRealtimeReportRequestBodyMetricFilterFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter")
class RunRealtimeReportRequestBody(StrictModel):
    dimensions: list[Dimension] | None = Field(default=None, description="The dimensions to include in the report. Dimensions break down metrics by categorical values (e.g., country, device type, page path).")
    limit: str | None = Field(default=None, description="Maximum number of rows to return. Defaults to 10,000 if unspecified. API maximum is 250,000 rows per request. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    metric_aggregations: list[Literal["METRIC_AGGREGATION_UNSPECIFIED", "TOTAL", "MINIMUM", "MAXIMUM", "COUNT"]] | None = Field(default=None, validation_alias="metricAggregations", serialization_alias="metricAggregations", description="Aggregation methods for metrics. Aggregated values appear in rows with dimension values set to the aggregation type (e.g., RESERVED_TOTAL).")
    metrics: list[Metric] | None = Field(default=None, description="The metrics to include in the report. Metrics are quantitative measurements (e.g., activeUsers, eventCount, screenPageViews).")
    minute_ranges: list[MinuteRange] | None = Field(default=None, validation_alias="minuteRanges", serialization_alias="minuteRanges", description="Time ranges in minutes to retrieve data from. If unspecified, defaults to the last 30 minutes. Multiple ranges can be requested; overlapping minutes appear in results for each range.")
    order_bys: list[OrderBy] | None = Field(default=None, validation_alias="orderBys", serialization_alias="orderBys", description="Specifies the sort order for report rows. Can sort by dimension values or metric values in ascending or descending order.")
    return_property_quota: bool | None = Field(default=None, validation_alias="returnPropertyQuota", serialization_alias="returnPropertyQuota", description="Whether to include the current quota status for this property in the response. Useful for monitoring API quota consumption.")
    dimension_filter: RunRealtimeReportRequestBodyDimensionFilter | None = Field(default=None, validation_alias="dimensionFilter", serialization_alias="dimensionFilter")
    metric_filter: RunRealtimeReportRequestBodyMetricFilter | None = Field(default=None, validation_alias="metricFilter", serialization_alias="metricFilter")
class RunRealtimeReportRequest(StrictModel):
    """Retrieve a customized report of real-time event data for a Google Analytics property, showing events and usage from the present moment up to 30 minutes ago (60 minutes for GA360). Data appears in reports within seconds of being sent to Google Analytics."""
    path: RunRealtimeReportRequestPath
    body: RunRealtimeReportRequestBody | None = None

# Operation: run_report
class RunReportRequestPath(StrictModel):
    property_: str = Field(default=..., validation_alias="property", serialization_alias="property", description="A Google Analytics property identifier whose events are tracked. Specified in the URL path and not the body. To learn more, see [where to find your Property ID](https://developers.google.com/analytics/devguides/reporting/data/v1/property-id). Within a batch request, this property should either be unspecified or consistent with the batch-level property. Example: properties/1234")
class RunReportRequestBodyCohortSpecCohortReportSettings(StrictModel):
    accumulate: bool | None = Field(default=None, validation_alias="accumulate", serialization_alias="accumulate", description="If true, accumulates the result from first touch day to the end day. Not supported in `RunReportRequest`.")
class RunReportRequestBodyCohortSpecCohortsRange(StrictModel):
    end_offset: int | None = Field(default=None, validation_alias="endOffset", serialization_alias="endOffset", description="Required. `endOffset` specifies the end date of the extended reporting date range for a cohort report. `endOffset` can be any positive integer but is commonly set to 5 to 10 so that reports contain data on the cohort for the next several granularity time periods. If `granularity` is `DAILY`, the `endDate` of the extended reporting date range is `endDate` of the cohort plus `endOffset` days. If `granularity` is `WEEKLY`, the `endDate` of the extended reporting date range is `endDate` of the cohort plus `endOffset * 7` days. If `granularity` is `MONTHLY`, the `endDate` of the extended reporting date range is `endDate` of the cohort plus `endOffset * 30` days.", json_schema_extra={'format': 'int32'})
    granularity: Literal["GRANULARITY_UNSPECIFIED", "DAILY", "WEEKLY", "MONTHLY"] | None = Field(default=None, validation_alias="granularity", serialization_alias="granularity", description="Required. The granularity used to interpret the `startOffset` and `endOffset` for the extended reporting date range for a cohort report.")
    start_offset: int | None = Field(default=None, validation_alias="startOffset", serialization_alias="startOffset", description="`startOffset` specifies the start date of the extended reporting date range for a cohort report. `startOffset` is commonly set to 0 so that reports contain data from the acquisition of the cohort forward. If `granularity` is `DAILY`, the `startDate` of the extended reporting date range is `startDate` of the cohort plus `startOffset` days. If `granularity` is `WEEKLY`, the `startDate` of the extended reporting date range is `startDate` of the cohort plus `startOffset * 7` days. If `granularity` is `MONTHLY`, the `startDate` of the extended reporting date range is `startDate` of the cohort plus `startOffset * 30` days.", json_schema_extra={'format': 'int32'})
class RunReportRequestBodyCohortSpec(StrictModel):
    cohorts: list[Cohort] | None = Field(default=None, validation_alias="cohorts", serialization_alias="cohorts", description="Defines the selection criteria to group users into cohorts. Most cohort reports define only a single cohort. If multiple cohorts are specified, each cohort can be recognized in the report by their name.")
    cohort_report_settings: RunReportRequestBodyCohortSpecCohortReportSettings | None = Field(default=None, validation_alias="cohortReportSettings", serialization_alias="cohortReportSettings")
    cohorts_range: RunReportRequestBodyCohortSpecCohortsRange | None = Field(default=None, validation_alias="cohortsRange", serialization_alias="cohortsRange")
class RunReportRequestBodyDimensionFilterFilterBetweenFilter(StrictModel):
    from_value: dict[str, Any] | None = Field(default=None, validation_alias="fromValue", serialization_alias="fromValue", description="Begins with this number.")
    to_value: dict[str, Any] | None = Field(default=None, validation_alias="toValue", serialization_alias="toValue", description="Ends with this number.")
class RunReportRequestBodyDimensionFilterFilterInListFilter(StrictModel):
    case_sensitive: bool | None = Field(default=None, validation_alias="caseSensitive", serialization_alias="caseSensitive", description="If true, the string value is case sensitive.")
    values: list[str] | None = Field(default=None, validation_alias="values", serialization_alias="values", description="The list of string values. Must be non-empty.")
class RunReportRequestBodyDimensionFilterFilterStringFilter(StrictModel):
    case_sensitive: bool | None = Field(default=None, validation_alias="caseSensitive", serialization_alias="caseSensitive", description="If true, the string value is case sensitive.")
    value: str | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The string value used for the matching.")
    match_type: Literal["MATCH_TYPE_UNSPECIFIED", "EXACT", "BEGINS_WITH", "ENDS_WITH", "CONTAINS", "FULL_REGEXP", "PARTIAL_REGEXP"] | None = Field(default=None, validation_alias="matchType", serialization_alias="matchType", description="The match type for this filter.")
class RunReportRequestBodyDimensionFilterFilterNumericFilter(StrictModel):
    operation: Literal["OPERATION_UNSPECIFIED", "EQUAL", "LESS_THAN", "LESS_THAN_OR_EQUAL", "GREATER_THAN", "GREATER_THAN_OR_EQUAL"] | None = Field(default=None, validation_alias="operation", serialization_alias="operation", description="The operation type for this filter.")
    value: dict[str, Any] | None = Field(default=None, validation_alias="value", serialization_alias="value", description="A numeric value or a date value.")
class RunReportRequestBodyDimensionFilterFilter(StrictModel):
    empty_filter: dict[str, Any] | None = Field(default=None, validation_alias="emptyFilter", serialization_alias="emptyFilter", description="A filter for empty values such as \"(not set)\" and \"\" values.")
    field_name: str | None = Field(default=None, validation_alias="fieldName", serialization_alias="fieldName", description="The dimension name or metric name. In most methods, dimensions & metrics can be used for the first time in this field. However in a RunPivotReportRequest, this field must be additionally specified by name in the RunPivotReportRequest's dimensions or metrics.")
    between_filter: RunReportRequestBodyDimensionFilterFilterBetweenFilter | None = Field(default=None, validation_alias="betweenFilter", serialization_alias="betweenFilter")
    in_list_filter: RunReportRequestBodyDimensionFilterFilterInListFilter | None = Field(default=None, validation_alias="inListFilter", serialization_alias="inListFilter")
    string_filter: RunReportRequestBodyDimensionFilterFilterStringFilter | None = Field(default=None, validation_alias="stringFilter", serialization_alias="stringFilter")
    numeric_filter: RunReportRequestBodyDimensionFilterFilterNumericFilter | None = Field(default=None, validation_alias="numericFilter", serialization_alias="numericFilter")
class RunReportRequestBodyDimensionFilter(StrictModel):
    not_expression: FilterExpression | None = Field(default=None, validation_alias="notExpression", serialization_alias="notExpression")
    filter_: RunReportRequestBodyDimensionFilterFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter")
class RunReportRequestBodyMetricFilterFilterBetweenFilter(StrictModel):
    from_value: dict[str, Any] | None = Field(default=None, validation_alias="fromValue", serialization_alias="fromValue", description="Begins with this number.")
    to_value: dict[str, Any] | None = Field(default=None, validation_alias="toValue", serialization_alias="toValue", description="Ends with this number.")
class RunReportRequestBodyMetricFilterFilterInListFilter(StrictModel):
    case_sensitive: bool | None = Field(default=None, validation_alias="caseSensitive", serialization_alias="caseSensitive", description="If true, the string value is case sensitive.")
    values: list[str] | None = Field(default=None, validation_alias="values", serialization_alias="values", description="The list of string values. Must be non-empty.")
class RunReportRequestBodyMetricFilterFilterStringFilter(StrictModel):
    case_sensitive: bool | None = Field(default=None, validation_alias="caseSensitive", serialization_alias="caseSensitive", description="If true, the string value is case sensitive.")
    value: str | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The string value used for the matching.")
    match_type: Literal["MATCH_TYPE_UNSPECIFIED", "EXACT", "BEGINS_WITH", "ENDS_WITH", "CONTAINS", "FULL_REGEXP", "PARTIAL_REGEXP"] | None = Field(default=None, validation_alias="matchType", serialization_alias="matchType", description="The match type for this filter.")
class RunReportRequestBodyMetricFilterFilterNumericFilter(StrictModel):
    operation: Literal["OPERATION_UNSPECIFIED", "EQUAL", "LESS_THAN", "LESS_THAN_OR_EQUAL", "GREATER_THAN", "GREATER_THAN_OR_EQUAL"] | None = Field(default=None, validation_alias="operation", serialization_alias="operation", description="The operation type for this filter.")
    value: dict[str, Any] | None = Field(default=None, validation_alias="value", serialization_alias="value", description="A numeric value or a date value.")
class RunReportRequestBodyMetricFilterFilter(StrictModel):
    empty_filter: dict[str, Any] | None = Field(default=None, validation_alias="emptyFilter", serialization_alias="emptyFilter", description="A filter for empty values such as \"(not set)\" and \"\" values.")
    field_name: str | None = Field(default=None, validation_alias="fieldName", serialization_alias="fieldName", description="The dimension name or metric name. In most methods, dimensions & metrics can be used for the first time in this field. However in a RunPivotReportRequest, this field must be additionally specified by name in the RunPivotReportRequest's dimensions or metrics.")
    between_filter: RunReportRequestBodyMetricFilterFilterBetweenFilter | None = Field(default=None, validation_alias="betweenFilter", serialization_alias="betweenFilter")
    in_list_filter: RunReportRequestBodyMetricFilterFilterInListFilter | None = Field(default=None, validation_alias="inListFilter", serialization_alias="inListFilter")
    string_filter: RunReportRequestBodyMetricFilterFilterStringFilter | None = Field(default=None, validation_alias="stringFilter", serialization_alias="stringFilter")
    numeric_filter: RunReportRequestBodyMetricFilterFilterNumericFilter | None = Field(default=None, validation_alias="numericFilter", serialization_alias="numericFilter")
class RunReportRequestBodyMetricFilter(StrictModel):
    not_expression: FilterExpression | None = Field(default=None, validation_alias="notExpression", serialization_alias="notExpression")
    filter_: RunReportRequestBodyMetricFilterFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter")
class RunReportRequestBody(StrictModel):
    comparisons: list[Comparison] | None = Field(default=None, description="Optional. The configuration of comparisons requested and displayed. The request only requires a comparisons field in order to receive a comparison column in the response.")
    currency_code: str | None = Field(default=None, validation_alias="currencyCode", serialization_alias="currencyCode", description="A currency code in ISO4217 format, such as \"AED\", \"USD\", \"JPY\". If the field is empty, the report uses the property's default currency.")
    date_ranges: list[DateRange] | None = Field(default=None, validation_alias="dateRanges", serialization_alias="dateRanges", description="Date ranges of data to read. If multiple date ranges are requested, each response row will contain a zero based date range index. If two date ranges overlap, the event data for the overlapping days is included in the response rows for both date ranges. In a cohort request, this `dateRanges` must be unspecified.")
    dimensions: list[Dimension] | None = Field(default=None, description="The dimensions requested and displayed.")
    keep_empty_rows: bool | None = Field(default=None, validation_alias="keepEmptyRows", serialization_alias="keepEmptyRows", description="If false or unspecified, each row with all metrics equal to 0 will not be returned. If true, these rows will be returned if they are not separately removed by a filter. Regardless of this `keep_empty_rows` setting, only data recorded by the Google Analytics property can be displayed in a report. For example if a property never logs a `purchase` event, then a query for the `eventName` dimension and `eventCount` metric will not have a row eventName: \"purchase\" and eventCount: 0.")
    limit: str | None = Field(default=None, description="The number of rows to return. If unspecified, 10,000 rows are returned. The API returns a maximum of 250,000 rows per request, no matter how many you ask for. `limit` must be positive. The API can also return fewer rows than the requested `limit`, if there aren't as many dimension values as the `limit`. For instance, there are fewer than 300 possible values for the dimension `country`, so when reporting on only `country`, you can't get more than 300 rows, even if you set `limit` to a higher value. To learn more about this pagination parameter, see [Pagination](https://developers.google.com/analytics/devguides/reporting/data/v1/basics#pagination).", json_schema_extra={'format': 'int64'})
    metric_aggregations: list[Literal["METRIC_AGGREGATION_UNSPECIFIED", "TOTAL", "MINIMUM", "MAXIMUM", "COUNT"]] | None = Field(default=None, validation_alias="metricAggregations", serialization_alias="metricAggregations", description="Aggregation of metrics. Aggregated metric values will be shown in rows where the dimension_values are set to \"RESERVED_(MetricAggregation)\". Aggregates including both comparisons and multiple date ranges will be aggregated based on the date ranges.")
    metrics: list[Metric] | None = Field(default=None, description="The metrics requested and displayed.")
    offset: str | None = Field(default=None, description="The row count of the start row. The first row is counted as row 0. When paging, the first request does not specify offset; or equivalently, sets offset to 0; the first request returns the first `limit` of rows. The second request sets offset to the `limit` of the first request; the second request returns the second `limit` of rows. To learn more about this pagination parameter, see [Pagination](https://developers.google.com/analytics/devguides/reporting/data/v1/basics#pagination).", json_schema_extra={'format': 'int64'})
    order_bys: list[OrderBy] | None = Field(default=None, validation_alias="orderBys", serialization_alias="orderBys", description="Specifies how rows are ordered in the response. Requests including both comparisons and multiple date ranges will have order bys applied on the comparisons.")
    return_property_quota: bool | None = Field(default=None, validation_alias="returnPropertyQuota", serialization_alias="returnPropertyQuota", description="Toggles whether to return the current state of this Google Analytics property's quota. Quota is returned in [PropertyQuota](#PropertyQuota).")
    cohort_spec: RunReportRequestBodyCohortSpec | None = Field(default=None, validation_alias="cohortSpec", serialization_alias="cohortSpec")
    dimension_filter: RunReportRequestBodyDimensionFilter | None = Field(default=None, validation_alias="dimensionFilter", serialization_alias="dimensionFilter")
    metric_filter: RunReportRequestBodyMetricFilter | None = Field(default=None, validation_alias="metricFilter", serialization_alias="metricFilter")
class RunReportRequest(StrictModel):
    """Returns a customized report of your Google Analytics event data. Reports contain statistics derived from data collected by the Google Analytics tracking code. The data returned from the API is as a table with columns for the requested dimensions and metrics. Metrics are individual measurements of user activity on your property, such as active users or event count. Dimensions break down metrics across some common criteria, such as country or event name. For a guide to constructing requests & understanding responses, see [Creating a Report](https://developers.google.com/analytics/devguides/reporting/data/v1/basics)."""
    path: RunReportRequestPath
    body: RunReportRequestBody | None = None

# Operation: list_audience_exports
class AudienceExportsListRequestPath(StrictModel):
    parent: str = Field(default=..., description="The property for which to list audience exports. Format: properties/{property}")
class AudienceExportsListRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="Maximum number of audience exports to return per page. The service may return fewer than specified. Higher values are coerced to the maximum allowed.")
    page_token: str | None = Field(default=None, validation_alias="pageToken", serialization_alias="pageToken", description="Page token from a previous ListAudienceExports call to retrieve the next page of results. When paginating, all other parameters must match the original request.")
class AudienceExportsListRequest(StrictModel):
    """Lists all audience exports for a property, allowing you to find and reuse existing exports rather than creating duplicates. The same audience can have multiple exports representing user snapshots from different dates."""
    path: AudienceExportsListRequestPath
    query: AudienceExportsListRequestQuery | None = None

# Operation: create_audience_export
class AudienceExportsCreateRequestPath(StrictModel):
    parent: str = Field(default=..., description="The parent property resource where this audience export will be created. Format: properties/{property}")
class AudienceExportsCreateRequestBody(StrictModel):
    audience: str | None = Field(default=None, description="The audience resource to export. This identifies which audience's users will be included in the export. Format: properties/{property}/audiences/{audience}")
    dimensions: list[V1betaAudienceDimension] | None = Field(default=None, description="The dimensions to include in the audience export response. Specifies which user attributes or characteristics will be returned in the exported data.")
class AudienceExportsCreateRequest(StrictModel):
    """Creates a snapshot of users currently in an audience and initiates an asynchronous export process. Use QueryAudienceExport to retrieve the exported audience data after creation."""
    path: AudienceExportsCreateRequestPath
    body: AudienceExportsCreateRequestBody | None = None

# Operation: query_audience_export
class AudienceExportsQueryRequestPath(StrictModel):
    name: str = Field(default=..., description="The resource name of the audience export to query. Format: properties/{property}/audienceExports/{audience_export}")
class AudienceExportsQueryRequestBody(StrictModel):
    limit: str | None = Field(default=None, description="Maximum number of rows to return per request. Defaults to 10,000 if unspecified. The API returns a maximum of 250,000 rows regardless of the requested limit. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    offset: str | None = Field(default=None, description="The zero-indexed row number to start from for pagination. Omit or set to 0 for the first request. For subsequent requests, set to the limit value from the previous response to retrieve the next batch of rows.", json_schema_extra={'format': 'int64'})
class AudienceExportsQueryRequest(StrictModel):
    """Retrieves user data from a previously created audience export. Users must first be exported via CreateAudienceExport before they can be queried using this method."""
    path: AudienceExportsQueryRequestPath
    body: AudienceExportsQueryRequestBody | None = None

# ============================================================================
# Component Models
# ============================================================================

class CaseExpression(PermissiveModel):
    """Used to convert a dimension value to a single case."""
    dimension_name: str | None = Field(None, validation_alias="dimensionName", serialization_alias="dimensionName", description="Name of a dimension. The name must refer back to a name in dimensions field of the request.")

class CohortReportSettings(PermissiveModel):
    """Optional settings of a cohort report."""
    accumulate: bool | None = Field(None, description="If true, accumulates the result from first touch day to the end day. Not supported in `RunReportRequest`.")

class CohortsRange(PermissiveModel):
    """Configures the extended reporting date range for a cohort report. Specifies an offset duration to follow the cohorts over."""
    end_offset: int | None = Field(None, validation_alias="endOffset", serialization_alias="endOffset", description="Required. `endOffset` specifies the end date of the extended reporting date range for a cohort report. `endOffset` can be any positive integer but is commonly set to 5 to 10 so that reports contain data on the cohort for the next several granularity time periods. If `granularity` is `DAILY`, the `endDate` of the extended reporting date range is `endDate` of the cohort plus `endOffset` days. If `granularity` is `WEEKLY`, the `endDate` of the extended reporting date range is `endDate` of the cohort plus `endOffset * 7` days. If `granularity` is `MONTHLY`, the `endDate` of the extended reporting date range is `endDate` of the cohort plus `endOffset * 30` days.", json_schema_extra={'format': 'int32'})
    granularity: Literal["GRANULARITY_UNSPECIFIED", "DAILY", "WEEKLY", "MONTHLY"] | None = Field(None, description="Required. The granularity used to interpret the `startOffset` and `endOffset` for the extended reporting date range for a cohort report.")
    start_offset: int | None = Field(None, validation_alias="startOffset", serialization_alias="startOffset", description="`startOffset` specifies the start date of the extended reporting date range for a cohort report. `startOffset` is commonly set to 0 so that reports contain data from the acquisition of the cohort forward. If `granularity` is `DAILY`, the `startDate` of the extended reporting date range is `startDate` of the cohort plus `startOffset` days. If `granularity` is `WEEKLY`, the `startDate` of the extended reporting date range is `startDate` of the cohort plus `startOffset * 7` days. If `granularity` is `MONTHLY`, the `startDate` of the extended reporting date range is `startDate` of the cohort plus `startOffset * 30` days.", json_schema_extra={'format': 'int32'})

class ConcatenateExpression(PermissiveModel):
    """Used to combine dimension values to a single dimension."""
    delimiter: str | None = Field(None, description="The delimiter placed between dimension names. Delimiters are often single characters such as \"|\" or \",\" but can be longer strings. If a dimension value contains the delimiter, both will be present in response with no distinction. For example if dimension 1 value = \"US,FR\", dimension 2 value = \"JP\", and delimiter = \",\", then the response will contain \"US,FR,JP\".")
    dimension_names: list[str] | None = Field(None, validation_alias="dimensionNames", serialization_alias="dimensionNames", description="Names of dimensions. The names must refer back to names in the dimensions field of the request.")

class DateRange(PermissiveModel):
    """A contiguous set of days: `startDate`, `startDate + 1`, ..., `endDate`. Requests are allowed up to 4 date ranges."""
    end_date: str | None = Field(None, validation_alias="endDate", serialization_alias="endDate", description="The inclusive end date for the query in the format `YYYY-MM-DD`. Cannot be before `start_date`. The format `NdaysAgo`, `yesterday`, or `today` is also accepted, and in that case, the date is inferred based on the property's reporting time zone.")
    name: str | None = Field(None, description="Assigns a name to this date range. The dimension `dateRange` is valued to this name in a report response. If set, cannot begin with `date_range_` or `RESERVED_`. If not set, date ranges are named by their zero based index in the request: `date_range_0`, `date_range_1`, etc.")
    start_date: str | None = Field(None, validation_alias="startDate", serialization_alias="startDate", description="The inclusive start date for the query in the format `YYYY-MM-DD`. Cannot be after `end_date`. The format `NdaysAgo`, `yesterday`, or `today` is also accepted, and in that case, the date is inferred based on the property's reporting time zone.")

class Cohort(PermissiveModel):
    """Defines a cohort selection criteria. A cohort is a group of users who share a common characteristic. For example, users with the same `firstSessionDate` belong to the same cohort."""
    date_range: DateRange | None = Field(None, validation_alias="dateRange", serialization_alias="dateRange", description="The cohort selects users whose first touch date is between start date and end date defined in the `dateRange`. This `dateRange` does not specify the full date range of event data that is present in a cohort report. In a cohort report, this `dateRange` is extended by the granularity and offset present in the `cohortsRange`; event data for the extended reporting date range is present in a cohort report. In a cohort request, this `dateRange` is required and the `dateRanges` in the `RunReportRequest` or `RunPivotReportRequest` must be unspecified. This `dateRange` should generally be aligned with the cohort's granularity. If `CohortsRange` uses daily granularity, this `dateRange` can be a single day. If `CohortsRange` uses weekly granularity, this `dateRange` can be aligned to a week boundary, starting at Sunday and ending Saturday. If `CohortsRange` uses monthly granularity, this `dateRange` can be aligned to a month, starting at the first and ending on the last day of the month.")
    dimension: str | None = Field(None, description="Dimension used by the cohort. Required and only supports `firstSessionDate`.")
    name: str | None = Field(None, description="Assigns a name to this cohort. The dimension `cohort` is valued to this name in a report response. If set, cannot begin with `cohort_` or `RESERVED_`. If not set, cohorts are named by their zero based index `cohort_0`, `cohort_1`, etc.")

class CohortSpec(PermissiveModel):
    """The specification of cohorts for a cohort report. Cohort reports create a time series of user retention for the cohort. For example, you could select the cohort of users that were acquired in the first week of September and follow that cohort for the next six weeks. Selecting the users acquired in the first week of September cohort is specified in the `cohort` object. Following that cohort for the next six weeks is specified in the `cohortsRange` object. For examples, see [Cohort Report Examples](https://developers.google.com/analytics/devguides/reporting/data/v1/advanced#cohort_report_examples). The report response could show a weekly time series where say your app has retained 60% of this cohort after three weeks and 25% of this cohort after six weeks. These two percentages can be calculated by the metric `cohortActiveUsers/cohortTotalUsers` and will be separate rows in the report."""
    cohort_report_settings: CohortReportSettings | None = Field(None, validation_alias="cohortReportSettings", serialization_alias="cohortReportSettings", description="Optional settings for a cohort report.")
    cohorts: list[Cohort] | None = Field(None, description="Defines the selection criteria to group users into cohorts. Most cohort reports define only a single cohort. If multiple cohorts are specified, each cohort can be recognized in the report by their name.")
    cohorts_range: CohortsRange | None = Field(None, validation_alias="cohortsRange", serialization_alias="cohortsRange", description="Cohort reports follow cohorts over an extended reporting date range. This range specifies an offset duration to follow the cohorts over.")

class DimensionExpression(PermissiveModel):
    """Used to express a dimension which is the result of a formula of multiple dimensions. Example usages: 1) lower_case(dimension) 2) concatenate(dimension1, symbol, dimension2)."""
    concatenate: ConcatenateExpression | None = Field(None, description="Used to combine dimension values to a single dimension. For example, dimension \"country, city\": concatenate(country, \", \", city).")
    lower_case: CaseExpression | None = Field(None, validation_alias="lowerCase", serialization_alias="lowerCase", description="Used to convert a dimension value to lower case.")
    upper_case: CaseExpression | None = Field(None, validation_alias="upperCase", serialization_alias="upperCase", description="Used to convert a dimension value to upper case.")

class Dimension(PermissiveModel):
    """Dimensions are attributes of your data. For example, the dimension city indicates the city from which an event originates. Dimension values in report responses are strings; for example, the city could be "Paris" or "New York". Requests are allowed up to 9 dimensions."""
    dimension_expression: DimensionExpression | None = Field(None, validation_alias="dimensionExpression", serialization_alias="dimensionExpression", description="One dimension can be the result of an expression of multiple dimensions. For example, dimension \"country, city\": concatenate(country, \", \", city).")
    name: str | None = Field(None, description="The name of the dimension. See the [API Dimensions](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema#dimensions) for the list of dimension names supported by core reporting methods such as `runReport` and `batchRunReports`. See [Realtime Dimensions](https://developers.google.com/analytics/devguides/reporting/data/v1/realtime-api-schema#dimensions) for the list of dimension names supported by the `runRealtimeReport` method. See [Funnel Dimensions](https://developers.google.com/analytics/devguides/reporting/data/v1/exploration-api-schema#dimensions) for the list of dimension names supported by the `runFunnelReport` method. If `dimensionExpression` is specified, `name` can be any string that you would like within the allowed character set. For example if a `dimensionExpression` concatenates `country` and `city`, you could call that dimension `countryAndCity`. Dimension names that you choose must match the regular expression `^[a-zA-Z0-9_]$`. Dimensions are referenced by `name` in...")

class DimensionOrderBy(PermissiveModel):
    """Sorts by dimension values."""
    dimension_name: str | None = Field(None, validation_alias="dimensionName", serialization_alias="dimensionName", description="A dimension name in the request to order by.")
    order_type: Literal["ORDER_TYPE_UNSPECIFIED", "ALPHANUMERIC", "CASE_INSENSITIVE_ALPHANUMERIC", "NUMERIC"] | None = Field(None, validation_alias="orderType", serialization_alias="orderType", description="Controls the rule for dimension value ordering.")

class EmptyFilter(RootModel[dict[str, Any]]):
    pass

class InListFilter(PermissiveModel):
    """The result needs to be in a list of string values."""
    case_sensitive: bool | None = Field(None, validation_alias="caseSensitive", serialization_alias="caseSensitive", description="If true, the string value is case sensitive.")
    values: list[str] | None = Field(None, description="The list of string values. Must be non-empty.")

class Metric(PermissiveModel):
    """The quantitative measurements of a report. For example, the metric `eventCount` is the total number of events. Requests are allowed up to 10 metrics."""
    expression: str | None = Field(None, description="A mathematical expression for derived metrics. For example, the metric Event count per user is `eventCount/totalUsers`.")
    invisible: bool | None = Field(None, description="Indicates if a metric is invisible in the report response. If a metric is invisible, the metric will not produce a column in the response, but can be used in `metricFilter`, `orderBys`, or a metric `expression`.")
    name: str | None = Field(None, description="The name of the metric. See the [API Metrics](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema#metrics) for the list of metric names supported by core reporting methods such as `runReport` and `batchRunReports`. See [Realtime Metrics](https://developers.google.com/analytics/devguides/reporting/data/v1/realtime-api-schema#metrics) for the list of metric names supported by the `runRealtimeReport` method. See [Funnel Metrics](https://developers.google.com/analytics/devguides/reporting/data/v1/exploration-api-schema#metrics) for the list of metric names supported by the `runFunnelReport` method. If `expression` is specified, `name` can be any string that you would like within the allowed character set. For example if `expression` is `screenPageViews/sessions`, you could call that metric's name = `viewsPerSession`. Metric names that you choose must match the regular expression `^[a-zA-Z0-9_]$`. Metrics are referenced by `name` in `metricFilter`, `orderBys`, and metric `expression`.")

class MetricOrderBy(PermissiveModel):
    """Sorts by metric values."""
    metric_name: str | None = Field(None, validation_alias="metricName", serialization_alias="metricName", description="A metric name in the request to order by.")

class MinuteRange(PermissiveModel):
    """A contiguous set of minutes: `startMinutesAgo`, `startMinutesAgo + 1`, ..., `endMinutesAgo`. Requests are allowed up to 2 minute ranges."""
    end_minutes_ago: int | None = Field(None, validation_alias="endMinutesAgo", serialization_alias="endMinutesAgo", description="The inclusive end minute for the query as a number of minutes before now. Cannot be before `startMinutesAgo`. For example, `\"endMinutesAgo\": 15` specifies the report should include event data from prior to 15 minutes ago. If unspecified, `endMinutesAgo` is defaulted to 0. Standard Analytics properties can request any minute in the last 30 minutes of event data (`endMinutesAgo <= 29`), and 360 Analytics properties can request any minute in the last 60 minutes of event data (`endMinutesAgo <= 59`).", json_schema_extra={'format': 'int32'})
    name: str | None = Field(None, description="Assigns a name to this minute range. The dimension `dateRange` is valued to this name in a report response. If set, cannot begin with `date_range_` or `RESERVED_`. If not set, minute ranges are named by their zero based index in the request: `date_range_0`, `date_range_1`, etc.")
    start_minutes_ago: int | None = Field(None, validation_alias="startMinutesAgo", serialization_alias="startMinutesAgo", description="The inclusive start minute for the query as a number of minutes before now. For example, `\"startMinutesAgo\": 29` specifies the report should include event data from 29 minutes ago and after. Cannot be after `endMinutesAgo`. If unspecified, `startMinutesAgo` is defaulted to 29. Standard Analytics properties can request up to the last 30 minutes of event data (`startMinutesAgo <= 29`), and 360 Analytics properties can request up to the last 60 minutes of event data (`startMinutesAgo <= 59`).", json_schema_extra={'format': 'int32'})

class NumericValue(PermissiveModel):
    """To represent a number."""
    double_value: float | None = Field(None, validation_alias="doubleValue", serialization_alias="doubleValue", description="Double value", json_schema_extra={'format': 'double'})
    int64_value: str | None = Field(None, validation_alias="int64Value", serialization_alias="int64Value", description="Integer value", json_schema_extra={'format': 'int64'})

class BetweenFilter(PermissiveModel):
    """To express that the result needs to be between two numbers (inclusive)."""
    from_value: NumericValue | None = Field(None, validation_alias="fromValue", serialization_alias="fromValue", description="Begins with this number.")
    to_value: NumericValue | None = Field(None, validation_alias="toValue", serialization_alias="toValue", description="Ends with this number.")

class NumericFilter(PermissiveModel):
    """Filters for numeric or date values."""
    operation: Literal["OPERATION_UNSPECIFIED", "EQUAL", "LESS_THAN", "LESS_THAN_OR_EQUAL", "GREATER_THAN", "GREATER_THAN_OR_EQUAL"] | None = Field(None, description="The operation type for this filter.")
    value: NumericValue | None = Field(None, description="A numeric value or a date value.")

class PivotSelection(PermissiveModel):
    """A pair of dimension names and values. Rows with this dimension pivot pair are ordered by the metric's value. For example if pivots = {{"browser", "Chrome"}} and metric_name = "Sessions", then the rows will be sorted based on Sessions in Chrome. ---------|----------|----------------|----------|---------------- | Chrome | Chrome | Safari | Safari ---------|----------|----------------|----------|---------------- Country | Sessions | Pages/Sessions | Sessions | Pages/Sessions ---------|----------|----------------|----------|---------------- US | 2 | 2 | 3 | 1 ---------|----------|----------------|----------|---------------- Canada | 3 | 1 | 4 | 1 ---------|----------|----------------|----------|----------------"""
    dimension_name: str | None = Field(None, validation_alias="dimensionName", serialization_alias="dimensionName", description="Must be a dimension name from the request.")
    dimension_value: str | None = Field(None, validation_alias="dimensionValue", serialization_alias="dimensionValue", description="Order by only when the named dimension is this value.")

class PivotOrderBy(PermissiveModel):
    """Sorts by a pivot column group."""
    metric_name: str | None = Field(None, validation_alias="metricName", serialization_alias="metricName", description="In the response to order by, order rows by this column. Must be a metric name from the request.")
    pivot_selections: list[PivotSelection] | None = Field(None, validation_alias="pivotSelections", serialization_alias="pivotSelections", description="Used to select a dimension name and value pivot. If multiple pivot selections are given, the sort occurs on rows where all pivot selection dimension name and value pairs match the row's dimension name and value pair.")

class OrderBy(PermissiveModel):
    """Order bys define how rows will be sorted in the response. For example, ordering rows by descending event count is one ordering, and ordering rows by the event name string is a different ordering."""
    desc: bool | None = Field(None, description="If true, sorts by descending order.")
    dimension: DimensionOrderBy | None = Field(None, description="Sorts results by a dimension's values.")
    metric: MetricOrderBy | None = Field(None, description="Sorts results by a metric's values.")
    pivot: PivotOrderBy | None = Field(None, description="Sorts results by a metric's values within a pivot column group.")

class Pivot(PermissiveModel):
    """Describes the visible dimension columns and rows in the report response."""
    field_names: list[str] | None = Field(None, validation_alias="fieldNames", serialization_alias="fieldNames", description="Dimension names for visible columns in the report response. Including \"dateRange\" produces a date range column; for each row in the response, dimension values in the date range column will indicate the corresponding date range from the request.")
    limit: str | None = Field(None, description="The number of unique combinations of dimension values to return in this pivot. The `limit` parameter is required. A `limit` of 10,000 is common for single pivot requests. The product of the `limit` for each `pivot` in a `RunPivotReportRequest` must not exceed 250,000. For example, a two pivot request with `limit: 1000` in each pivot will fail because the product is `1,000,000`.", json_schema_extra={'format': 'int64'})
    metric_aggregations: list[Literal["METRIC_AGGREGATION_UNSPECIFIED", "TOTAL", "MINIMUM", "MAXIMUM", "COUNT"]] | None = Field(None, validation_alias="metricAggregations", serialization_alias="metricAggregations", description="Aggregate the metrics by dimensions in this pivot using the specified metric_aggregations.")
    offset: str | None = Field(None, description="The row count of the start row. The first row is counted as row 0.", json_schema_extra={'format': 'int64'})
    order_bys: list[OrderBy] | None = Field(None, validation_alias="orderBys", serialization_alias="orderBys", description="Specifies how dimensions are ordered in the pivot. In the first Pivot, the OrderBys determine Row and PivotDimensionHeader ordering; in subsequent Pivots, the OrderBys determine only PivotDimensionHeader ordering. Dimensions specified in these OrderBys must be a subset of Pivot.field_names.")

class QuotaStatus(PermissiveModel):
    """Current state for a particular quota group."""
    consumed: int | None = Field(None, description="Quota consumed by this request.", json_schema_extra={'format': 'int32'})
    remaining: int | None = Field(None, description="Quota remaining after this request.", json_schema_extra={'format': 'int32'})

class PropertyQuota(PermissiveModel):
    """Current state of all quotas for this Analytics Property. If any quota for a property is exhausted, all requests to that property will return Resource Exhausted errors."""
    concurrent_requests: QuotaStatus | None = Field(None, validation_alias="concurrentRequests", serialization_alias="concurrentRequests", description="Standard Analytics Properties can send up to 10 concurrent requests; Analytics 360 Properties can use up to 50 concurrent requests.")
    potentially_thresholded_requests_per_hour: QuotaStatus | None = Field(None, validation_alias="potentiallyThresholdedRequestsPerHour", serialization_alias="potentiallyThresholdedRequestsPerHour", description="Analytics Properties can send up to 120 requests with potentially thresholded dimensions per hour. In a batch request, each report request is individually counted for this quota if the request contains potentially thresholded dimensions.")
    server_errors_per_project_per_hour: QuotaStatus | None = Field(None, validation_alias="serverErrorsPerProjectPerHour", serialization_alias="serverErrorsPerProjectPerHour", description="Standard Analytics Properties and cloud project pairs can have up to 10 server errors per hour; Analytics 360 Properties and cloud project pairs can have up to 50 server errors per hour.")
    tokens_per_day: QuotaStatus | None = Field(None, validation_alias="tokensPerDay", serialization_alias="tokensPerDay", description="Standard Analytics Properties can use up to 200,000 tokens per day; Analytics 360 Properties can use 2,000,000 tokens per day. Most requests consume fewer than 10 tokens.")
    tokens_per_hour: QuotaStatus | None = Field(None, validation_alias="tokensPerHour", serialization_alias="tokensPerHour", description="Standard Analytics Properties can use up to 40,000 tokens per hour; Analytics 360 Properties can use 400,000 tokens per hour. An API request consumes a single number of tokens, and that number is deducted from all of the hourly, daily, and per project hourly quotas.")
    tokens_per_project_per_hour: QuotaStatus | None = Field(None, validation_alias="tokensPerProjectPerHour", serialization_alias="tokensPerProjectPerHour", description="Analytics Properties can use up to 35% of their tokens per project per hour. This amounts to standard Analytics Properties can use up to 14,000 tokens per project per hour, and Analytics 360 Properties can use 140,000 tokens per project per hour. An API request consumes a single number of tokens, and that number is deducted from all of the hourly, daily, and per project hourly quotas.")

class StringFilter(PermissiveModel):
    """The filter for string"""
    case_sensitive: bool | None = Field(None, validation_alias="caseSensitive", serialization_alias="caseSensitive", description="If true, the string value is case sensitive.")
    match_type: Literal["MATCH_TYPE_UNSPECIFIED", "EXACT", "BEGINS_WITH", "ENDS_WITH", "CONTAINS", "FULL_REGEXP", "PARTIAL_REGEXP"] | None = Field(None, validation_alias="matchType", serialization_alias="matchType", description="The match type for this filter.")
    value: str | None = Field(None, description="The string value used for the matching.")

class FilterModel(PermissiveModel):
    """An expression to filter dimension or metric values."""
    between_filter: BetweenFilter | None = Field(None, validation_alias="betweenFilter", serialization_alias="betweenFilter", description="A filter for two values.")
    empty_filter: EmptyFilter | None = Field(None, validation_alias="emptyFilter", serialization_alias="emptyFilter", description="A filter for empty values such as \"(not set)\" and \"\" values.")
    field_name: str | None = Field(None, validation_alias="fieldName", serialization_alias="fieldName", description="The dimension name or metric name. In most methods, dimensions & metrics can be used for the first time in this field. However in a RunPivotReportRequest, this field must be additionally specified by name in the RunPivotReportRequest's dimensions or metrics.")
    in_list_filter: InListFilter | None = Field(None, validation_alias="inListFilter", serialization_alias="inListFilter", description="A filter for in list values.")
    numeric_filter: NumericFilter | None = Field(None, validation_alias="numericFilter", serialization_alias="numericFilter", description="A filter for numeric or date values.")
    string_filter: StringFilter | None = Field(None, validation_alias="stringFilter", serialization_alias="stringFilter", description="Strings related filter.")

class V1betaAudienceDimension(PermissiveModel):
    """An audience dimension is a user attribute. Specific user attributed are requested and then later returned in the `QueryAudienceExportResponse`."""
    dimension_name: str | None = Field(None, validation_alias="dimensionName", serialization_alias="dimensionName", description="Optional. The API name of the dimension. See the [API Dimensions](https://developers.google.com/analytics/devguides/reporting/data/v1/audience-list-api-schema#dimensions) for the list of dimension names.")

class Comparison(PermissiveModel):
    """Defines an individual comparison. Most requests will include multiple comparisons so that the report compares between the comparisons."""
    comparison: str | None = Field(None, description="A saved comparison identified by the comparison's resource name. For example, 'comparisons/1234'.")
    dimension_filter: FilterExpression | None = Field(None, validation_alias="dimensionFilter", serialization_alias="dimensionFilter", description="A basic comparison.")
    name: str | None = Field(None, description="Each comparison produces separate rows in the response. In the response, this comparison is identified by this name. If name is unspecified, we will use the saved comparisons display name.")

class FilterExpression(PermissiveModel):
    """To express dimension or metric filters. The fields in the same FilterExpression need to be either all dimensions or all metrics."""
    and_group: FilterExpressionList | None = Field(None, validation_alias="andGroup", serialization_alias="andGroup", description="The FilterExpressions in and_group have an AND relationship.")
    filter_: FilterModel | None = Field(None, validation_alias="filter", serialization_alias="filter", description="A primitive filter. In the same FilterExpression, all of the filter's field names need to be either all dimensions or all metrics.")
    not_expression: FilterExpression | None = Field(None, validation_alias="notExpression", serialization_alias="notExpression", description="The FilterExpression is NOT of not_expression.")
    or_group: FilterExpressionList | None = Field(None, validation_alias="orGroup", serialization_alias="orGroup", description="The FilterExpressions in or_group have an OR relationship.")

class FilterExpressionList(PermissiveModel):
    """A list of filter expressions."""
    expressions: list[FilterExpression] | None = Field(None, description="A list of filter expressions.")


# Rebuild models to resolve forward references (required for circular refs)
BetweenFilter.model_rebuild()
CaseExpression.model_rebuild()
Cohort.model_rebuild()
CohortReportSettings.model_rebuild()
CohortSpec.model_rebuild()
CohortsRange.model_rebuild()
Comparison.model_rebuild()
ConcatenateExpression.model_rebuild()
DateRange.model_rebuild()
Dimension.model_rebuild()
DimensionExpression.model_rebuild()
DimensionOrderBy.model_rebuild()
EmptyFilter.model_rebuild()
FilterExpression.model_rebuild()
FilterExpressionList.model_rebuild()
FilterModel.model_rebuild()
InListFilter.model_rebuild()
Metric.model_rebuild()
MetricOrderBy.model_rebuild()
MinuteRange.model_rebuild()
NumericFilter.model_rebuild()
NumericValue.model_rebuild()
OrderBy.model_rebuild()
Pivot.model_rebuild()
PivotOrderBy.model_rebuild()
PivotSelection.model_rebuild()
PropertyQuota.model_rebuild()
QuotaStatus.model_rebuild()
StringFilter.model_rebuild()
V1betaAudienceDimension.model_rebuild()

"""
Google Sheets Api MCP Server - Pydantic Models

Generated: 2026-04-09 17:24:32 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "BatchUpdateRequest",
    "CreateRequest",
    "DeveloperMetadataGetRequest",
    "DeveloperMetadataSearchRequest",
    "GetByDataFilterRequest",
    "GetRequest",
    "SheetsCopyToRequest",
    "ValuesAppendRequest",
    "ValuesBatchClearByDataFilterRequest",
    "ValuesBatchClearRequest",
    "ValuesBatchGetByDataFilterRequest",
    "ValuesBatchGetRequest",
    "ValuesBatchUpdateByDataFilterRequest",
    "ValuesBatchUpdateRequest",
    "ValuesClearRequest",
    "ValuesGetRequest",
    "ValuesUpdateRequest",
    "DataFilter",
    "DataFilterValueRange",
    "DataSource",
    "DeveloperMetadata",
    "NamedRange",
    "Request",
    "Sheet",
    "ThemeColorPair",
    "ValueRange",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: apply_spreadsheet_updates
class BatchUpdateRequestPath(StrictModel):
    spreadsheet_id: str = Field(default=..., validation_alias="spreadsheetId", serialization_alias="spreadsheetId", description="The unique identifier of the spreadsheet to update.")
class BatchUpdateRequestBody(StrictModel):
    include_spreadsheet_in_response: bool | None = Field(default=None, validation_alias="includeSpreadsheetInResponse", serialization_alias="includeSpreadsheetInResponse", description="When true, includes the complete spreadsheet resource in the response after updates are applied.")
    requests: list[Request] | None = Field(default=None, description="An ordered list of update requests to apply to the spreadsheet. Requests are processed sequentially in the order specified. If any request fails validation, no updates will be applied.")
    response_ranges: list[str] | None = Field(default=None, validation_alias="responseRanges", serialization_alias="responseRanges", description="Restricts which ranges are included in the response spreadsheet. Only meaningful when the spreadsheet is included in the response.")
class BatchUpdateRequest(StrictModel):
    """Applies one or more updates to a spreadsheet atomically. All requests are validated before being applied; if any request is invalid, the entire batch fails and no changes are made. Responses mirror the structure of requests, with replies provided only for updates that generate them."""
    path: BatchUpdateRequestPath
    body: BatchUpdateRequestBody | None = None

# Operation: create_spreadsheet
class CreateRequestBodyPropertiesDefaultFormatBackgroundColorStyle(StrictModel):
    rgb_color: dict[str, Any] | None = Field(default=None, validation_alias="rgbColor", serialization_alias="rgbColor", description="RGB color object for styling. Note that the alpha (transparency) channel is not generally supported by the API.")
    theme_color: Literal["THEME_COLOR_TYPE_UNSPECIFIED", "TEXT", "BACKGROUND", "ACCENT1", "ACCENT2", "ACCENT3", "ACCENT4", "ACCENT5", "ACCENT6", "LINK"] | None = Field(default=None, validation_alias="themeColor", serialization_alias="themeColor", description="Theme color selection from the spreadsheet's color palette, such as text, background, accent colors, or link color.")
class CreateRequestBodyPropertiesDefaultFormatBorders(StrictModel):
    bottom: dict[str, Any] | None = Field(default=None, validation_alias="bottom", serialization_alias="bottom", description="Bottom border styling for cells in the default format.")
    left: dict[str, Any] | None = Field(default=None, validation_alias="left", serialization_alias="left", description="Left border styling for cells in the default format.")
    right: dict[str, Any] | None = Field(default=None, validation_alias="right", serialization_alias="right", description="Right border styling for cells in the default format.")
    top: dict[str, Any] | None = Field(default=None, validation_alias="top", serialization_alias="top", description="Top border styling for cells in the default format.")
class CreateRequestBodyPropertiesDefaultFormatPadding(StrictModel):
    bottom: int | None = Field(default=None, validation_alias="bottom", serialization_alias="bottom", description="Bottom padding in pixels for cells in the default format. Must be a 32-bit integer.", json_schema_extra={'format': 'int32'})
    left: int | None = Field(default=None, validation_alias="left", serialization_alias="left", description="Left padding in pixels for cells in the default format. Must be a 32-bit integer.", json_schema_extra={'format': 'int32'})
    right: int | None = Field(default=None, validation_alias="right", serialization_alias="right", description="Right padding in pixels for cells in the default format. Must be a 32-bit integer.", json_schema_extra={'format': 'int32'})
    top: int | None = Field(default=None, validation_alias="top", serialization_alias="top", description="Top padding in pixels for cells in the default format. Must be a 32-bit integer.", json_schema_extra={'format': 'int32'})
class CreateRequestBodyPropertiesDefaultFormatNumberFormat(StrictModel):
    pattern: str | None = Field(default=None, validation_alias="pattern", serialization_alias="pattern", description="Number format pattern string (e.g., for dates, currency, decimals). If not specified, a default pattern based on spreadsheet locale will be used.")
    type_: Literal["NUMBER_FORMAT_TYPE_UNSPECIFIED", "TEXT", "NUMBER", "PERCENT", "CURRENCY", "DATE", "TIME", "DATE_TIME", "SCIENTIFIC"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Number format type such as text, number, percent, currency, date, time, date-time, or scientific notation. Required when setting number formats.")
class CreateRequestBodyPropertiesDefaultFormatTextFormat(StrictModel):
    bold: bool | None = Field(default=None, validation_alias="bold", serialization_alias="bold", description="Whether text in cells should be displayed in bold.")
    font_family: str | None = Field(default=None, validation_alias="fontFamily", serialization_alias="fontFamily", description="Font family name for text styling (e.g., Arial, Times New Roman).")
    font_size: int | None = Field(default=None, validation_alias="fontSize", serialization_alias="fontSize", description="Font size in points. Must be a 32-bit integer.", json_schema_extra={'format': 'int32'})
    foreground_color_style: dict[str, Any] | None = Field(default=None, validation_alias="foregroundColorStyle", serialization_alias="foregroundColorStyle", description="Foreground color styling for text. Takes precedence over the foreground_color field if both are set.")
    italic: bool | None = Field(default=None, validation_alias="italic", serialization_alias="italic", description="Whether text in cells should be displayed in italics.")
    link: dict[str, Any] | None = Field(default=None, validation_alias="link", serialization_alias="link", description="Hyperlink destination URL for text. Setting this clears any existing cell-level links. Link color and underline formatting are applied automatically unless overridden.")
    strikethrough: bool | None = Field(default=None, validation_alias="strikethrough", serialization_alias="strikethrough", description="Whether text in cells should have a strikethrough line.")
    underline: bool | None = Field(default=None, validation_alias="underline", serialization_alias="underline", description="Whether text in cells should be underlined.")
class CreateRequestBodyPropertiesDefaultFormatTextRotation(StrictModel):
    angle: int | None = Field(default=None, validation_alias="angle", serialization_alias="angle", description="Text rotation angle in degrees, ranging from -90 to 90. Positive angles rotate counterclockwise (LTR) or clockwise (RTL), negative angles rotate the opposite direction.", json_schema_extra={'format': 'int32'})
    vertical: bool | None = Field(default=None, validation_alias="vertical", serialization_alias="vertical", description="If true, text reads vertically from top to bottom while individual characters maintain their standard orientation.")
class CreateRequestBodyPropertiesDefaultFormat(StrictModel):
    horizontal_alignment: Literal["HORIZONTAL_ALIGN_UNSPECIFIED", "LEFT", "CENTER", "RIGHT"] | None = Field(default=None, validation_alias="horizontalAlignment", serialization_alias="horizontalAlignment", description="Horizontal alignment for cell values: left, center, or right alignment.")
    hyperlink_display_type: Literal["HYPERLINK_DISPLAY_TYPE_UNSPECIFIED", "LINKED", "PLAIN_TEXT"] | None = Field(default=None, validation_alias="hyperlinkDisplayType", serialization_alias="hyperlinkDisplayType", description="How hyperlinks should display in cells: as clickable links or as plain text.")
    text_direction: Literal["TEXT_DIRECTION_UNSPECIFIED", "LEFT_TO_RIGHT", "RIGHT_TO_LEFT"] | None = Field(default=None, validation_alias="textDirection", serialization_alias="textDirection", description="Text direction for cell content: left-to-right or right-to-left for language support.")
    vertical_alignment: Literal["VERTICAL_ALIGN_UNSPECIFIED", "TOP", "MIDDLE", "BOTTOM"] | None = Field(default=None, validation_alias="verticalAlignment", serialization_alias="verticalAlignment", description="Vertical alignment for cell values: top, middle, or bottom alignment.")
    wrap_strategy: Literal["WRAP_STRATEGY_UNSPECIFIED", "OVERFLOW_CELL", "LEGACY_WRAP", "CLIP", "WRAP"] | None = Field(default=None, validation_alias="wrapStrategy", serialization_alias="wrapStrategy", description="Text wrapping strategy: overflow into adjacent cells, legacy wrap, clip excess text, or wrap to multiple lines.")
    background_color_style: CreateRequestBodyPropertiesDefaultFormatBackgroundColorStyle | None = Field(default=None, validation_alias="backgroundColorStyle", serialization_alias="backgroundColorStyle")
    borders: CreateRequestBodyPropertiesDefaultFormatBorders | None = None
    padding: CreateRequestBodyPropertiesDefaultFormatPadding | None = None
    number_format: CreateRequestBodyPropertiesDefaultFormatNumberFormat | None = Field(default=None, validation_alias="numberFormat", serialization_alias="numberFormat")
    text_format: CreateRequestBodyPropertiesDefaultFormatTextFormat | None = Field(default=None, validation_alias="textFormat", serialization_alias="textFormat")
    text_rotation: CreateRequestBodyPropertiesDefaultFormatTextRotation | None = Field(default=None, validation_alias="textRotation", serialization_alias="textRotation")
class CreateRequestBodyPropertiesIterativeCalculationSettings(StrictModel):
    convergence_threshold: float | None = Field(default=None, validation_alias="convergenceThreshold", serialization_alias="convergenceThreshold", description="Convergence threshold for iterative calculations. When successive calculation results differ by less than this value, iteration stops. Must be a double-precision number.", json_schema_extra={'format': 'double'})
    max_iterations: int | None = Field(default=None, validation_alias="maxIterations", serialization_alias="maxIterations", description="Maximum number of calculation rounds to perform when iterative calculation is enabled. Must be a 32-bit integer.", json_schema_extra={'format': 'int32'})
class CreateRequestBodyPropertiesSpreadsheetTheme(StrictModel):
    primary_font_family: str | None = Field(default=None, validation_alias="primaryFontFamily", serialization_alias="primaryFontFamily", description="Primary font family name used as the default for the spreadsheet.")
    theme_colors: list[ThemeColorPair] | None = Field(default=None, validation_alias="themeColors", serialization_alias="themeColors", description="Complete set of theme color pairs for the spreadsheet. All theme color pairs must be provided together when updating.")
class CreateRequestBodyProperties(StrictModel):
    auto_recalc: Literal["RECALCULATION_INTERVAL_UNSPECIFIED", "ON_CHANGE", "MINUTE", "HOUR"] | None = Field(default=None, validation_alias="autoRecalc", serialization_alias="autoRecalc", description="Recalculation frequency for volatile functions. Options include: on change, every minute, or every hour. Defaults to unspecified behavior.")
    import_functions_external_url_access_allowed: bool | None = Field(default=None, validation_alias="importFunctionsExternalUrlAccessAllowed", serialization_alias="importFunctionsExternalUrlAccessAllowed", description="Whether to allow external URL access for image and import functions. Read-only when true. May be overridden by admin URL allowlist settings.")
    locale: str | None = Field(default=None, validation_alias="locale", serialization_alias="locale", description="Spreadsheet locale in ISO 639-1 format (e.g., 'en'), ISO 639-2 format (e.g., 'fil'), or combined language-country format (e.g., 'en_US'). Not all locales are supported for updates.")
    time_zone: str | None = Field(default=None, validation_alias="timeZone", serialization_alias="timeZone", description="Spreadsheet time zone in CLDR format (e.g., 'America/New_York'). Custom time zones like 'GMT-07:00' are supported if the standard zone isn't recognized.")
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="Title or name of the spreadsheet.")
    default_format: CreateRequestBodyPropertiesDefaultFormat | None = Field(default=None, validation_alias="defaultFormat", serialization_alias="defaultFormat")
    iterative_calculation_settings: CreateRequestBodyPropertiesIterativeCalculationSettings | None = Field(default=None, validation_alias="iterativeCalculationSettings", serialization_alias="iterativeCalculationSettings")
    spreadsheet_theme: CreateRequestBodyPropertiesSpreadsheetTheme | None = Field(default=None, validation_alias="spreadsheetTheme", serialization_alias="spreadsheetTheme")
class CreateRequestBody(StrictModel):
    data_sources: list[DataSource] | None = Field(default=None, validation_alias="dataSources", serialization_alias="dataSources", description="List of external data sources to connect with the spreadsheet, such as BigQuery or database connections.")
    developer_metadata: list[DeveloperMetadata] | None = Field(default=None, validation_alias="developerMetadata", serialization_alias="developerMetadata", description="Developer metadata key-value pairs to associate with the spreadsheet for custom tracking or integration purposes.")
    named_ranges: list[NamedRange] | None = Field(default=None, validation_alias="namedRanges", serialization_alias="namedRanges", description="Named ranges to define in the spreadsheet, allowing cells or ranges to be referenced by custom names instead of cell coordinates.")
    sheets: list[Sheet] | None = Field(default=None, description="Array of sheet objects that define the individual sheets within the spreadsheet.")
    properties: CreateRequestBodyProperties | None = None
class CreateRequest(StrictModel):
    """Creates a new spreadsheet with optional configuration for sheets, properties, formatting defaults, and external data sources. Returns the newly created spreadsheet object."""
    body: CreateRequestBody | None = None

# Operation: get_spreadsheet
class GetRequestPath(StrictModel):
    spreadsheet_id: str = Field(default=..., validation_alias="spreadsheetId", serialization_alias="spreadsheetId", description="The unique identifier of the spreadsheet to retrieve. This ID is required to access the correct spreadsheet.")
class GetRequestQuery(StrictModel):
    ranges: list[str] | None = Field(default=None, description="Optional cell ranges to retrieve from the spreadsheet, specified using A1 notation (e.g., A1, A1:D5, or Sheet2!A1:C4). Multiple ranges can be specified to retrieve data from different areas or sheets. When specified, only data intersecting these ranges is returned.")
class GetRequest(StrictModel):
    """Retrieves a spreadsheet by its ID with optional support for specific cell ranges and grid data. By default, grid data is excluded; use field masks or the includeGridData parameter to include it."""
    path: GetRequestPath
    query: GetRequestQuery | None = None

# Operation: retrieve_spreadsheet_by_data_filter
class GetByDataFilterRequestPath(StrictModel):
    spreadsheet_id: str = Field(default=..., validation_alias="spreadsheetId", serialization_alias="spreadsheetId", description="The unique identifier of the spreadsheet to retrieve.")
class GetByDataFilterRequestBody(StrictModel):
    data_filters: list[DataFilter] | None = Field(default=None, validation_alias="dataFilters", serialization_alias="dataFilters", description="One or more data filters that specify which ranges to return from the spreadsheet. When multiple filters are provided, the response includes data from all matching ranges. If omitted, only spreadsheet metadata is returned without grid data.")
class GetByDataFilterRequest(StrictModel):
    """Retrieves a spreadsheet by ID with the ability to filter which data ranges are returned. Use data filters to selectively fetch specific portions of the spreadsheet, optionally including grid data."""
    path: GetByDataFilterRequestPath
    body: GetByDataFilterRequestBody | None = None

# Operation: get_developer_metadata
class DeveloperMetadataGetRequestPath(StrictModel):
    spreadsheet_id: str = Field(default=..., validation_alias="spreadsheetId", serialization_alias="spreadsheetId", description="The unique identifier of the spreadsheet containing the developer metadata you want to retrieve.")
    metadata_id: int = Field(default=..., validation_alias="metadataId", serialization_alias="metadataId", description="The unique identifier of the developer metadata entry to retrieve. This is a numeric ID assigned when the metadata was created.")
class DeveloperMetadataGetRequest(StrictModel):
    """Retrieves a specific developer metadata entry from a spreadsheet by its unique metadata ID. Use this to access custom metadata properties attached to spreadsheet resources."""
    path: DeveloperMetadataGetRequestPath

# Operation: search_developer_metadata
class DeveloperMetadataSearchRequestPath(StrictModel):
    spreadsheet_id: str = Field(default=..., validation_alias="spreadsheetId", serialization_alias="spreadsheetId", description="The unique identifier of the spreadsheet to search for developer metadata.")
class DeveloperMetadataSearchRequestBody(StrictModel):
    data_filters: list[DataFilter] | None = Field(default=None, validation_alias="dataFilters", serialization_alias="dataFilters", description="One or more data filters that define the search criteria. Metadata matching any of the specified filters will be included in the results. Filters can target specific metadata lookups or location regions within the spreadsheet.")
class DeveloperMetadataSearchRequest(StrictModel):
    """Search for developer metadata entries in a spreadsheet that match specified criteria. Returns all metadata matching the provided data filters, which can target specific metadata lookups or location-based regions."""
    path: DeveloperMetadataSearchRequestPath
    body: DeveloperMetadataSearchRequestBody | None = None

# Operation: copy_sheet
class SheetsCopyToRequestPath(StrictModel):
    spreadsheet_id: str = Field(default=..., validation_alias="spreadsheetId", serialization_alias="spreadsheetId", description="The unique identifier of the spreadsheet that contains the sheet you want to copy.")
    sheet_id: int = Field(default=..., validation_alias="sheetId", serialization_alias="sheetId", description="The unique identifier of the sheet to copy. This must be a valid sheet ID within the source spreadsheet.")
class SheetsCopyToRequestBody(StrictModel):
    destination_spreadsheet_id: str | None = Field(default=None, validation_alias="destinationSpreadsheetId", serialization_alias="destinationSpreadsheetId", description="The unique identifier of the spreadsheet where the sheet should be copied to. If omitted, the sheet will be copied within the same spreadsheet.")
class SheetsCopyToRequest(StrictModel):
    """Copies a sheet from one spreadsheet to another and returns the properties of the newly created sheet. If no destination spreadsheet is specified, the sheet is copied within the same spreadsheet."""
    path: SheetsCopyToRequestPath
    body: SheetsCopyToRequestBody | None = None

# Operation: append_sheet_values
class ValuesAppendRequestPath(StrictModel):
    spreadsheet_id: str = Field(default=..., validation_alias="spreadsheetId", serialization_alias="spreadsheetId", description="The unique identifier of the spreadsheet to update.")
    range_: str = Field(default=..., validation_alias="range", serialization_alias="range", description="The range in A1 notation where the operation should search for an existing data table. New values will be appended to the row immediately following the last row of the detected table.")
class ValuesAppendRequestQuery(StrictModel):
    include_values_in_response: bool | None = Field(default=None, validation_alias="includeValuesInResponse", serialization_alias="includeValuesInResponse", description="When enabled, the response will include the actual values that were appended to the spreadsheet. By default, the response omits the appended values.")
    insert_data_option: Literal["OVERWRITE", "INSERT_ROWS"] | None = Field(default=None, validation_alias="insertDataOption", serialization_alias="insertDataOption", description="Specifies how new data should be inserted: OVERWRITE replaces existing data, while INSERT_ROWS creates new rows for the appended data.")
    value_input_option: Literal["INPUT_VALUE_OPTION_UNSPECIFIED", "RAW", "USER_ENTERED"] | None = Field(default=None, validation_alias="valueInputOption", serialization_alias="valueInputOption", description="Specifies how the input data should be interpreted: RAW treats values as-is, while USER_ENTERED applies the same parsing as if entered through the Sheets UI (e.g., formulas, dates).")
class ValuesAppendRequestBody(StrictModel):
    major_dimension: Literal["DIMENSION_UNSPECIFIED", "ROWS", "COLUMNS"] | None = Field(default=None, validation_alias="majorDimension", serialization_alias="majorDimension", description="Specifies whether the input array is organized by rows or columns. Defaults to ROWS, where each inner array represents a single row. Use COLUMNS if each inner array represents a single column.")
    values: list[list[Any]] | None = Field(default=None, description="A two-dimensional array of values to append, where each inner array represents either a row or column depending on majorDimension. Supported types are boolean, string, and number. Null values are ignored; use empty strings to set cells to empty values.")
class ValuesAppendRequest(StrictModel):
    """Appends values to the next row of a detected data table in a spreadsheet. The operation automatically locates the table within the specified range and adds new rows starting from the first column of that table."""
    path: ValuesAppendRequestPath
    query: ValuesAppendRequestQuery | None = None
    body: ValuesAppendRequestBody | None = None

# Operation: clear_spreadsheet_values
class ValuesBatchClearRequestPath(StrictModel):
    spreadsheet_id: str = Field(default=..., validation_alias="spreadsheetId", serialization_alias="spreadsheetId", description="The unique identifier of the spreadsheet to update. This ID can be found in the spreadsheet URL.")
class ValuesBatchClearRequestBody(StrictModel):
    ranges: list[str] | None = Field(default=None, description="One or more cell ranges to clear, specified using A1 notation (e.g., Sheet1!A1:B2) or R1C1 notation. If omitted, no ranges will be cleared. Order of ranges does not affect the operation.")
class ValuesBatchClearRequest(StrictModel):
    """Clears all values from one or more specified ranges in a spreadsheet while preserving cell formatting, data validation, and other properties. Useful for resetting data while maintaining spreadsheet structure."""
    path: ValuesBatchClearRequestPath
    body: ValuesBatchClearRequestBody | None = None

# Operation: clear_spreadsheet_values_by_filter
class ValuesBatchClearByDataFilterRequestPath(StrictModel):
    spreadsheet_id: str = Field(default=..., validation_alias="spreadsheetId", serialization_alias="spreadsheetId", description="The unique identifier of the spreadsheet to update. This ID is typically found in the spreadsheet's URL.")
class ValuesBatchClearByDataFilterRequestBody(StrictModel):
    data_filters: list[DataFilter] | None = Field(default=None, validation_alias="dataFilters", serialization_alias="dataFilters", description="One or more data filters that define which ranges to clear. Each filter is evaluated independently, and all ranges matching any filter will have their values cleared. If not specified, no ranges will be cleared.")
class ValuesBatchClearByDataFilterRequest(StrictModel):
    """Clears cell values from a spreadsheet based on one or more data filters, while preserving all formatting, validation rules, and other cell properties. Use this to selectively remove data from ranges matching your specified filter criteria."""
    path: ValuesBatchClearByDataFilterRequestPath
    body: ValuesBatchClearByDataFilterRequestBody | None = None

# Operation: get_spreadsheet_values_batch
class ValuesBatchGetRequestPath(StrictModel):
    spreadsheet_id: str = Field(default=..., validation_alias="spreadsheetId", serialization_alias="spreadsheetId", description="The unique identifier of the spreadsheet to retrieve data from.")
class ValuesBatchGetRequestQuery(StrictModel):
    date_time_render_option: Literal["SERIAL_NUMBER", "FORMATTED_STRING"] | None = Field(default=None, validation_alias="dateTimeRenderOption", serialization_alias="dateTimeRenderOption", description="Controls how dates, times, and durations are represented in the output. Choose between serial number format (numeric representation) or formatted string. This setting is ignored if values are returned in formatted value mode. Defaults to serial number format.")
    major_dimension: Literal["DIMENSION_UNSPECIFIED", "ROWS", "COLUMNS"] | None = Field(default=None, validation_alias="majorDimension", serialization_alias="majorDimension", description="Determines the orientation of returned data. Use ROWS to return data organized by rows (each inner array is a row), COLUMNS to return data organized by columns (each inner array is a column), or DIMENSION_UNSPECIFIED for default behavior. Defaults to ROWS.")
    ranges: list[str] | None = Field(default=None, description="The cell ranges to retrieve, specified in A1 notation or R1C1 notation. Provide as an array of range strings (e.g., ['A1:B10', 'D5:E20']). If omitted, the entire sheet is retrieved.")
    value_render_option: Literal["FORMATTED_VALUE", "UNFORMATTED_VALUE", "FORMULA"] | None = Field(default=None, validation_alias="valueRenderOption", serialization_alias="valueRenderOption", description="Controls how cell values are represented in the output. Choose FORMATTED_VALUE to return values as displayed in the spreadsheet, UNFORMATTED_VALUE for raw values, or FORMULA to return formulas as text. Defaults to formatted value mode.")
class ValuesBatchGetRequest(StrictModel):
    """Retrieves one or more ranges of values from a spreadsheet. Specify the spreadsheet ID and one or more ranges to fetch, with options to control how values and dates are formatted in the response."""
    path: ValuesBatchGetRequestPath
    query: ValuesBatchGetRequestQuery | None = None

# Operation: get_spreadsheet_values_by_filter
class ValuesBatchGetByDataFilterRequestPath(StrictModel):
    spreadsheet_id: str = Field(default=..., validation_alias="spreadsheetId", serialization_alias="spreadsheetId", description="The unique identifier of the spreadsheet to retrieve data from.")
class ValuesBatchGetByDataFilterRequestBody(StrictModel):
    data_filters: list[DataFilter] | None = Field(default=None, validation_alias="dataFilters", serialization_alias="dataFilters", description="One or more data filters that define which ranges to retrieve. Any ranges matching at least one filter will be included in the response.")
    date_time_render_option: Literal["SERIAL_NUMBER", "FORMATTED_STRING"] | None = Field(default=None, validation_alias="dateTimeRenderOption", serialization_alias="dateTimeRenderOption", description="Controls how dates, times, and durations are formatted in the output. Choose SERIAL_NUMBER for numeric representation or FORMATTED_STRING for human-readable text. This setting is ignored when valueRenderOption is set to FORMATTED_VALUE. Defaults to SERIAL_NUMBER.")
    major_dimension: Literal["DIMENSION_UNSPECIFIED", "ROWS", "COLUMNS"] | None = Field(default=None, validation_alias="majorDimension", serialization_alias="majorDimension", description="Specifies whether results should be organized by rows or columns. ROWS returns data as nested arrays where each inner array is a row; COLUMNS returns data where each inner array is a column. Defaults to ROWS.")
    value_render_option: Literal["FORMATTED_VALUE", "UNFORMATTED_VALUE", "FORMULA"] | None = Field(default=None, validation_alias="valueRenderOption", serialization_alias="valueRenderOption", description="Controls how cell values are represented in the output. FORMATTED_VALUE shows values as displayed in the spreadsheet, UNFORMATTED_VALUE shows raw values, and FORMULA shows the actual formulas. Defaults to FORMATTED_VALUE.")
class ValuesBatchGetByDataFilterRequest(StrictModel):
    """Retrieves one or more ranges of values from a spreadsheet that match specified data filters. Multiple ranges matching any of the provided filters are returned in a single response."""
    path: ValuesBatchGetByDataFilterRequestPath
    body: ValuesBatchGetByDataFilterRequestBody | None = None

# Operation: update_sheet_values_batch
class ValuesBatchUpdateRequestPath(StrictModel):
    spreadsheet_id: str = Field(default=..., validation_alias="spreadsheetId", serialization_alias="spreadsheetId", description="The unique identifier of the spreadsheet to update.")
class ValuesBatchUpdateRequestBody(StrictModel):
    data: list[ValueRange] | None = Field(default=None, description="An array of value ranges to update, where each range specifies the target cells and the values to write. Order matters as ranges are processed sequentially.")
    include_values_in_response: bool | None = Field(default=None, validation_alias="includeValuesInResponse", serialization_alias="includeValuesInResponse", description="When enabled, the response includes the actual values written to the cells, including all values in the requested range (excluding trailing empty rows and columns). Disabled by default.")
    value_input_option: Literal["INPUT_VALUE_OPTION_UNSPECIFIED", "RAW", "USER_ENTERED"] | None = Field(default=None, validation_alias="valueInputOption", serialization_alias="valueInputOption", description="Specifies how the input data should be interpreted: RAW treats values as-is without formula parsing, USER_ENTERED parses formulas and formats like a user entering data manually, or UNSPECIFIED uses the default behavior.")
class ValuesBatchUpdateRequest(StrictModel):
    """Updates multiple ranges of cells in a spreadsheet with new values. Specify which ranges to update, how to interpret the input data, and optionally request the updated values in the response."""
    path: ValuesBatchUpdateRequestPath
    body: ValuesBatchUpdateRequestBody | None = None

# Operation: update_spreadsheet_values_by_filter
class ValuesBatchUpdateByDataFilterRequestPath(StrictModel):
    spreadsheet_id: str = Field(default=..., validation_alias="spreadsheetId", serialization_alias="spreadsheetId", description="The unique identifier of the spreadsheet to update.")
class ValuesBatchUpdateByDataFilterRequestBody(StrictModel):
    data: list[DataFilterValueRange] | None = Field(default=None, description="Array of data filter value ranges specifying which cells to update and what values to apply. When multiple ranges match a filter, the same values are applied to all matched ranges.")
    include_values_in_response: bool | None = Field(default=None, validation_alias="includeValuesInResponse", serialization_alias="includeValuesInResponse", description="If true, the response will include the actual values that were written to the cells. By default, responses omit updated values. When enabled, the response includes all values in the requested range, excluding trailing empty rows and columns.")
    value_input_option: Literal["INPUT_VALUE_OPTION_UNSPECIFIED", "RAW", "USER_ENTERED"] | None = Field(default=None, validation_alias="valueInputOption", serialization_alias="valueInputOption", description="Specifies how the input data should be interpreted: RAW treats values as-is without parsing, USER_ENTERED applies the same parsing as if entered through the Sheets UI (formulas, dates, etc.), or INPUT_VALUE_OPTION_UNSPECIFIED uses the default behavior.")
class ValuesBatchUpdateByDataFilterRequest(StrictModel):
    """Updates cell values in one or more ranges of a spreadsheet using data filters to target specific cells. Allows you to set values across multiple matched ranges simultaneously and optionally retrieve the updated values in the response."""
    path: ValuesBatchUpdateByDataFilterRequestPath
    body: ValuesBatchUpdateByDataFilterRequestBody | None = None

# Operation: clear_spreadsheet_values_range
class ValuesClearRequestPath(StrictModel):
    spreadsheet_id: str = Field(default=..., validation_alias="spreadsheetId", serialization_alias="spreadsheetId", description="The unique identifier of the spreadsheet to update. This ID is typically found in the spreadsheet's URL.")
    range_: str = Field(default=..., validation_alias="range", serialization_alias="range", description="The cells to clear, specified using A1 notation (e.g., Sheet1!A1:B10) or R1C1 notation. Supports single cells, ranges, and multiple ranges.")
class ValuesClearRequest(StrictModel):
    """Clears all values from specified cells in a spreadsheet while preserving formatting, data validation, and other cell properties. Specify the spreadsheet and target range using A1 or R1C1 notation."""
    path: ValuesClearRequestPath

# Operation: read_spreadsheet_range
class ValuesGetRequestPath(StrictModel):
    spreadsheet_id: str = Field(default=..., validation_alias="spreadsheetId", serialization_alias="spreadsheetId", description="The unique identifier of the spreadsheet to read from.")
    range_: str = Field(default=..., validation_alias="range", serialization_alias="range", description="The cell range to retrieve, specified using A1 notation (e.g., Sheet1!A1:B10) or R1C1 notation.")
class ValuesGetRequestQuery(StrictModel):
    date_time_render_option: Literal["SERIAL_NUMBER", "FORMATTED_STRING"] | None = Field(default=None, validation_alias="dateTimeRenderOption", serialization_alias="dateTimeRenderOption", description="Controls how dates, times, and durations are formatted in the response. Choose SERIAL_NUMBER for numeric representation or FORMATTED_STRING for human-readable text. Ignored when valueRenderOption is set to FORMATTED_VALUE. Defaults to SERIAL_NUMBER.")
    major_dimension: Literal["DIMENSION_UNSPECIFIED", "ROWS", "COLUMNS"] | None = Field(default=None, validation_alias="majorDimension", serialization_alias="majorDimension", description="Determines the structure of the returned data. ROWS returns data organized by rows (default behavior), COLUMNS returns data organized by columns. This affects how nested arrays are structured in the response.")
    value_render_option: Literal["FORMATTED_VALUE", "UNFORMATTED_VALUE", "FORMULA"] | None = Field(default=None, validation_alias="valueRenderOption", serialization_alias="valueRenderOption", description="Specifies how cell values should be represented. FORMATTED_VALUE returns values as displayed in the spreadsheet, UNFORMATTED_VALUE returns raw values, and FORMULA returns the actual formulas. Defaults to FORMATTED_VALUE.")
class ValuesGetRequest(StrictModel):
    """Retrieves cell values from a specified range in a spreadsheet. Supports flexible formatting options for dates, times, and formulas, with configurable output structure."""
    path: ValuesGetRequestPath
    query: ValuesGetRequestQuery | None = None

# Operation: update_sheet_values
class ValuesUpdateRequestPath(StrictModel):
    spreadsheet_id: str = Field(default=..., validation_alias="spreadsheetId", serialization_alias="spreadsheetId", description="The unique identifier of the spreadsheet to update.")
    range_: str = Field(default=..., validation_alias="range", serialization_alias="range", description="The target range in A1 notation (e.g., 'Sheet1!A1:B10') where values will be written.")
class ValuesUpdateRequestQuery(StrictModel):
    include_values_in_response: bool | None = Field(default=None, validation_alias="includeValuesInResponse", serialization_alias="includeValuesInResponse", description="When enabled, the response includes the actual values written to the cells. By default, responses omit updated values.")
    value_input_option: Literal["INPUT_VALUE_OPTION_UNSPECIFIED", "RAW", "USER_ENTERED"] | None = Field(default=None, validation_alias="valueInputOption", serialization_alias="valueInputOption", description="Specifies how input data should be interpreted: RAW treats values as-is, USER_ENTERED evaluates formulas and formats. Defaults to RAW if unspecified.")
class ValuesUpdateRequestBody(StrictModel):
    major_dimension: Literal["DIMENSION_UNSPECIFIED", "ROWS", "COLUMNS"] | None = Field(default=None, validation_alias="majorDimension", serialization_alias="majorDimension", description="Determines how the values array is organized: ROWS means each inner array represents a row, COLUMNS means each inner array represents a column. Defaults to ROWS if unspecified.")
    values: list[list[Any]] | None = Field(default=None, description="A 2D array of values to write, where each inner array represents either a row or column depending on majorDimension. Supported types are boolean, string, and number; null values are ignored, and empty strings clear cells.")
class ValuesUpdateRequest(StrictModel):
    """Updates cell values in a spreadsheet within a specified range using A1 notation. Specify how input data should be interpreted (raw or user-entered formulas) and optionally retrieve the updated values in the response."""
    path: ValuesUpdateRequestPath
    query: ValuesUpdateRequestQuery | None = None
    body: ValuesUpdateRequestBody | None = None

# ============================================================================
# Component Models
# ============================================================================

class AppendDimensionRequest(PermissiveModel):
    """Appends rows or columns to the end of a sheet."""
    dimension: Literal["DIMENSION_UNSPECIFIED", "ROWS", "COLUMNS"] | None = Field(None, description="Whether rows or columns should be appended.")
    length: int | None = Field(None, description="The number of rows or columns to append.", json_schema_extra={'format': 'int32'})
    sheet_id: int | None = Field(None, validation_alias="sheetId", serialization_alias="sheetId", description="The sheet to append rows or columns to.", json_schema_extra={'format': 'int32'})

class BigQueryQuerySpec(PermissiveModel):
    """Specifies a custom BigQuery query."""
    raw_query: str | None = Field(None, validation_alias="rawQuery", serialization_alias="rawQuery", description="The raw query string.")

class BigQueryTableSpec(PermissiveModel):
    """Specifies a BigQuery table definition. Only [native tables](https://cloud.google.com/bigquery/docs/tables-intro) are allowed."""
    dataset_id: str | None = Field(None, validation_alias="datasetId", serialization_alias="datasetId", description="The BigQuery dataset id.")
    table_id: str | None = Field(None, validation_alias="tableId", serialization_alias="tableId", description="The BigQuery table id.")
    table_project_id: str | None = Field(None, validation_alias="tableProjectId", serialization_alias="tableProjectId", description="The ID of a BigQuery project the table belongs to. If not specified, the project_id is assumed.")

class BigQueryDataSourceSpec(PermissiveModel):
    """The specification of a BigQuery data source that's connected to a sheet."""
    project_id: str | None = Field(None, validation_alias="projectId", serialization_alias="projectId", description="The ID of a BigQuery enabled Google Cloud project with a billing account attached. For any queries executed against the data source, the project is charged.")
    query_spec: BigQueryQuerySpec | None = Field(None, validation_alias="querySpec", serialization_alias="querySpec", description="A BigQueryQuerySpec.")
    table_spec: BigQueryTableSpec | None = Field(None, validation_alias="tableSpec", serialization_alias="tableSpec", description="A BigQueryTableSpec.")

class ChartAxisViewWindowOptions(PermissiveModel):
    """The options that define a "view window" for a chart (such as the visible values in an axis)."""
    view_window_max: float | None = Field(None, validation_alias="viewWindowMax", serialization_alias="viewWindowMax", description="The maximum numeric value to be shown in this view window. If unset, will automatically determine a maximum value that looks good for the data.", json_schema_extra={'format': 'double'})
    view_window_min: float | None = Field(None, validation_alias="viewWindowMin", serialization_alias="viewWindowMin", description="The minimum numeric value to be shown in this view window. If unset, will automatically determine a minimum value that looks good for the data.", json_schema_extra={'format': 'double'})
    view_window_mode: Literal["DEFAULT_VIEW_WINDOW_MODE", "VIEW_WINDOW_MODE_UNSUPPORTED", "EXPLICIT", "PRETTY"] | None = Field(None, validation_alias="viewWindowMode", serialization_alias="viewWindowMode", description="The view window's mode.")

class ChartCustomNumberFormatOptions(PermissiveModel):
    """Custom number formatting options for chart attributes."""
    prefix: str | None = Field(None, description="Custom prefix to be prepended to the chart attribute. This field is optional.")
    suffix: str | None = Field(None, description="Custom suffix to be appended to the chart attribute. This field is optional.")

class ChartDateTimeRule(PermissiveModel):
    """Allows you to organize the date-time values in a source data column into buckets based on selected parts of their date or time values."""
    type_: Literal["CHART_DATE_TIME_RULE_TYPE_UNSPECIFIED", "SECOND", "MINUTE", "HOUR", "HOUR_MINUTE", "HOUR_MINUTE_AMPM", "DAY_OF_WEEK", "DAY_OF_YEAR", "DAY_OF_MONTH", "DAY_MONTH", "MONTH", "QUARTER", "YEAR", "YEAR_MONTH", "YEAR_QUARTER", "YEAR_MONTH_DAY"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of date-time grouping to apply.")

class ChartHistogramRule(PermissiveModel):
    """Allows you to organize numeric values in a source data column into buckets of constant size."""
    interval_size: float | None = Field(None, validation_alias="intervalSize", serialization_alias="intervalSize", description="The size of the buckets that are created. Must be positive.", json_schema_extra={'format': 'double'})
    max_value: float | None = Field(None, validation_alias="maxValue", serialization_alias="maxValue", description="The maximum value at which items are placed into buckets. Values greater than the maximum are grouped into a single bucket. If omitted, it is determined by the maximum item value.", json_schema_extra={'format': 'double'})
    min_value: float | None = Field(None, validation_alias="minValue", serialization_alias="minValue", description="The minimum value at which items are placed into buckets. Values that are less than the minimum are grouped into a single bucket. If omitted, it is determined by the minimum item value.", json_schema_extra={'format': 'double'})

class ChartGroupRule(PermissiveModel):
    """An optional setting on the ChartData of the domain of a data source chart that defines buckets for the values in the domain rather than breaking out each individual value. For example, when plotting a data source chart, you can specify a histogram rule on the domain (it should only contain numeric values), grouping its values into buckets. Any values of a chart series that fall into the same bucket are aggregated based on the aggregate_type."""
    date_time_rule: ChartDateTimeRule | None = Field(None, validation_alias="dateTimeRule", serialization_alias="dateTimeRule", description="A ChartDateTimeRule.")
    histogram_rule: ChartHistogramRule | None = Field(None, validation_alias="histogramRule", serialization_alias="histogramRule", description="A ChartHistogramRule")

class ClearBasicFilterRequest(PermissiveModel):
    """Clears the basic filter, if any exists on the sheet."""
    sheet_id: int | None = Field(None, validation_alias="sheetId", serialization_alias="sheetId", description="The sheet ID on which the basic filter should be cleared.", json_schema_extra={'format': 'int32'})

class Color(PermissiveModel):
    """Represents a color in the RGBA color space. This representation is designed for simplicity of conversion to and from color representations in various languages over compactness. For example, the fields of this representation can be trivially provided to the constructor of `java.awt.Color` in Java; it can also be trivially provided to UIColor's `+colorWithRed:green:blue:alpha` method in iOS; and, with just a little work, it can be easily formatted into a CSS `rgba()` string in JavaScript. This reference page doesn't have information about the absolute color space that should be used to interpret the RGB value—for example, sRGB, Adobe RGB, DCI-P3, and BT.2020. By default, applications should assume the sRGB color space. When color equality needs to be decided, implementations, unless documented otherwise, treat two colors as equal if all their red, green, blue, and alpha values each differ by at most `1e-5`. Example (Java): import com.google.type.Color; // ... public static java.awt.Color fromProto(Color protocolor) { float alpha = protocolor.hasAlpha() ? protocolor.getAlpha().getValue() : 1.0; return new java.awt.Color( protocolor.getRed(), protocolor.getGreen(), protocolor.getBlue(), alpha); } public static Color toProto(java.awt.Color color) { float red = (float) color.getRed(); float green = (float) color.getGreen(); float blue = (float) color.getBlue(); float denominator = 255.0; Color.Builder resultBuilder = Color .newBuilder() .setRed(red / denominator) .setGreen(green / denominator) .setBlue(blue / denominator); int alpha = color.getAlpha(); if (alpha != 255) { result.setAlpha( FloatValue .newBuilder() .setValue(((float) alpha) / denominator) .build()); } return resultBuilder.build(); } // ... Example (iOS / Obj-C): // ... static UIColor* fromProto(Color* protocolor) { float red = [protocolor red]; float green = [protocolor green]; float blue = [protocolor blue]; FloatValue* alpha_wrapper = [protocolor alpha]; float alpha = 1.0; if (alpha_wrapper != nil) { alpha = [alpha_wrapper value]; } return [UIColor colorWithRed:red green:green blue:blue alpha:alpha]; } static Color* toProto(UIColor* color) { CGFloat red, green, blue, alpha; if (![color getRed:&red green:&green blue:&blue alpha:&alpha]) { return nil; } Color* result = [[Color alloc] init]; [result setRed:red]; [result setGreen:green]; [result setBlue:blue]; if (alpha <= 0.9999) { [result setAlpha:floatWrapperWithValue(alpha)]; } [result autorelease]; return result; } // ... Example (JavaScript): // ... var protoToCssColor = function(rgb_color) { var redFrac = rgb_color.red || 0.0; var greenFrac = rgb_color.green || 0.0; var blueFrac = rgb_color.blue || 0.0; var red = Math.floor(redFrac * 255); var green = Math.floor(greenFrac * 255); var blue = Math.floor(blueFrac * 255); if (!('alpha' in rgb_color)) { return rgbToCssColor(red, green, blue); } var alphaFrac = rgb_color.alpha.value || 0.0; var rgbParams = [red, green, blue].join(','); return ['rgba(', rgbParams, ',', alphaFrac, ')'].join(''); }; var rgbToCssColor = function(red, green, blue) { var rgbNumber = new Number((red << 16) | (green << 8) | blue); var hexString = rgbNumber.toString(16); var missingZeros = 6 - hexString.length; var resultBuilder = ['#']; for (var i = 0; i < missingZeros; i++) { resultBuilder.push('0'); } resultBuilder.push(hexString); return resultBuilder.join(''); }; // ..."""
    alpha: float | None = Field(None, description="The fraction of this color that should be applied to the pixel. That is, the final pixel color is defined by the equation: `pixel color = alpha * (this color) + (1.0 - alpha) * (background color)` This means that a value of 1.0 corresponds to a solid color, whereas a value of 0.0 corresponds to a completely transparent color. This uses a wrapper message rather than a simple float scalar so that it is possible to distinguish between a default value and the value being unset. If omitted, this color object is rendered as a solid color (as if the alpha value had been explicitly given a value of 1.0).", json_schema_extra={'format': 'float'})
    blue: float | None = Field(None, description="The amount of blue in the color as a value in the interval [0, 1].", json_schema_extra={'format': 'float'})
    green: float | None = Field(None, description="The amount of green in the color as a value in the interval [0, 1].", json_schema_extra={'format': 'float'})
    red: float | None = Field(None, description="The amount of red in the color as a value in the interval [0, 1].", json_schema_extra={'format': 'float'})

class ColorStyle(PermissiveModel):
    """A color value."""
    rgb_color: Color | None = Field(None, validation_alias="rgbColor", serialization_alias="rgbColor", description="RGB color. The [`alpha`](https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/other#Color.FIELDS.alpha) value in the [`Color`](https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/other#color) object isn't generally supported.")
    theme_color: Literal["THEME_COLOR_TYPE_UNSPECIFIED", "TEXT", "BACKGROUND", "ACCENT1", "ACCENT2", "ACCENT3", "ACCENT4", "ACCENT5", "ACCENT6", "LINK"] | None = Field(None, validation_alias="themeColor", serialization_alias="themeColor", description="Theme color.")

class BandingProperties(PermissiveModel):
    """Properties referring a single dimension (either row or column). If both BandedRange.row_properties and BandedRange.column_properties are set, the fill colors are applied to cells according to the following rules: * header_color and footer_color take priority over band colors. * first_band_color takes priority over second_band_color. * row_properties takes priority over column_properties. For example, the first row color takes priority over the first column color, but the first column color takes priority over the second row color. Similarly, the row header takes priority over the column header in the top left cell, but the column header takes priority over the first row color if the row header is not set."""
    first_band_color: Color | None = Field(None, validation_alias="firstBandColor", serialization_alias="firstBandColor", description="The first color that is alternating. (Required) Deprecated: Use first_band_color_style.")
    first_band_color_style: ColorStyle | None = Field(None, validation_alias="firstBandColorStyle", serialization_alias="firstBandColorStyle", description="The first color that is alternating. (Required) If first_band_color is also set, this field takes precedence.")
    footer_color: Color | None = Field(None, validation_alias="footerColor", serialization_alias="footerColor", description="The color of the last row or column. If this field is not set, the last row or column is filled with either first_band_color or second_band_color, depending on the color of the previous row or column. Deprecated: Use footer_color_style.")
    footer_color_style: ColorStyle | None = Field(None, validation_alias="footerColorStyle", serialization_alias="footerColorStyle", description="The color of the last row or column. If this field is not set, the last row or column is filled with either first_band_color or second_band_color, depending on the color of the previous row or column. If footer_color is also set, this field takes precedence.")
    header_color: Color | None = Field(None, validation_alias="headerColor", serialization_alias="headerColor", description="The color of the first row or column. If this field is set, the first row or column is filled with this color and the colors alternate between first_band_color and second_band_color starting from the second row or column. Otherwise, the first row or column is filled with first_band_color and the colors proceed to alternate as they normally would. Deprecated: Use header_color_style.")
    header_color_style: ColorStyle | None = Field(None, validation_alias="headerColorStyle", serialization_alias="headerColorStyle", description="The color of the first row or column. If this field is set, the first row or column is filled with this color and the colors alternate between first_band_color and second_band_color starting from the second row or column. Otherwise, the first row or column is filled with first_band_color and the colors proceed to alternate as they normally would. If header_color is also set, this field takes precedence.")
    second_band_color: Color | None = Field(None, validation_alias="secondBandColor", serialization_alias="secondBandColor", description="The second color that is alternating. (Required) Deprecated: Use second_band_color_style.")
    second_band_color_style: ColorStyle | None = Field(None, validation_alias="secondBandColorStyle", serialization_alias="secondBandColorStyle", description="The second color that is alternating. (Required) If second_band_color is also set, this field takes precedence.")

class Border(PermissiveModel):
    """A border along a cell."""
    color: Color | None = Field(None, description="The color of the border. Deprecated: Use color_style.")
    color_style: ColorStyle | None = Field(None, validation_alias="colorStyle", serialization_alias="colorStyle", description="The color of the border. If color is also set, this field takes precedence.")
    style: Literal["STYLE_UNSPECIFIED", "DOTTED", "DASHED", "SOLID", "SOLID_MEDIUM", "SOLID_THICK", "NONE", "DOUBLE"] | None = Field(None, description="The style of the border.")
    width: int | None = Field(None, description="The width of the border, in pixels. Deprecated; the width is determined by the \"style\" field.", json_schema_extra={'format': 'int32'})

class Borders(PermissiveModel):
    """The borders of the cell."""
    bottom: Border | None = Field(None, description="The bottom border of the cell.")
    left: Border | None = Field(None, description="The left border of the cell.")
    right: Border | None = Field(None, description="The right border of the cell.")
    top: Border | None = Field(None, description="The top border of the cell.")

class ConditionValue(PermissiveModel):
    """The value of the condition."""
    relative_date: Literal["RELATIVE_DATE_UNSPECIFIED", "PAST_YEAR", "PAST_MONTH", "PAST_WEEK", "YESTERDAY", "TODAY", "TOMORROW"] | None = Field(None, validation_alias="relativeDate", serialization_alias="relativeDate", description="A relative date (based on the current date). Valid only if the type is DATE_BEFORE, DATE_AFTER, DATE_ON_OR_BEFORE or DATE_ON_OR_AFTER. Relative dates are not supported in data validation. They are supported only in conditional formatting and conditional filters.")
    user_entered_value: str | None = Field(None, validation_alias="userEnteredValue", serialization_alias="userEnteredValue", description="A value the condition is based on. The value is parsed as if the user typed into a cell. Formulas are supported (and must begin with an `=` or a '+').")

class BooleanCondition(PermissiveModel):
    """A condition that can evaluate to true or false. BooleanConditions are used by conditional formatting, data validation, and the criteria in filters."""
    type_: Literal["CONDITION_TYPE_UNSPECIFIED", "NUMBER_GREATER", "NUMBER_GREATER_THAN_EQ", "NUMBER_LESS", "NUMBER_LESS_THAN_EQ", "NUMBER_EQ", "NUMBER_NOT_EQ", "NUMBER_BETWEEN", "NUMBER_NOT_BETWEEN", "TEXT_CONTAINS", "TEXT_NOT_CONTAINS", "TEXT_STARTS_WITH", "TEXT_ENDS_WITH", "TEXT_EQ", "TEXT_IS_EMAIL", "TEXT_IS_URL", "DATE_EQ", "DATE_BEFORE", "DATE_AFTER", "DATE_ON_OR_BEFORE", "DATE_ON_OR_AFTER", "DATE_BETWEEN", "DATE_NOT_BETWEEN", "DATE_IS_VALID", "ONE_OF_RANGE", "ONE_OF_LIST", "BLANK", "NOT_BLANK", "CUSTOM_FORMULA", "BOOLEAN", "TEXT_NOT_EQ", "DATE_NOT_EQ", "FILTER_EXPRESSION"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of condition.")
    values: list[ConditionValue] | None = Field(None, description="The values of the condition. The number of supported values depends on the condition type. Some support zero values, others one or two values, and ConditionType.ONE_OF_LIST supports an arbitrary number of values.")

class DataExecutionStatus(PermissiveModel):
    """The data execution status. A data execution is created to sync a data source object with the latest data from a DataSource. It is usually scheduled to run at background, you can check its state to tell if an execution completes There are several scenarios where a data execution is triggered to run: * Adding a data source creates an associated data source sheet as well as a data execution to sync the data from the data source to the sheet. * Updating a data source creates a data execution to refresh the associated data source sheet similarly. * You can send refresh request to explicitly refresh one or multiple data source objects."""
    error_code: Literal["DATA_EXECUTION_ERROR_CODE_UNSPECIFIED", "TIMED_OUT", "TOO_MANY_ROWS", "TOO_MANY_COLUMNS", "TOO_MANY_CELLS", "ENGINE", "PARAMETER_INVALID", "UNSUPPORTED_DATA_TYPE", "DUPLICATE_COLUMN_NAMES", "INTERRUPTED", "CONCURRENT_QUERY", "OTHER", "TOO_MANY_CHARS_PER_CELL", "DATA_NOT_FOUND", "PERMISSION_DENIED", "MISSING_COLUMN_ALIAS", "OBJECT_NOT_FOUND", "OBJECT_IN_ERROR_STATE", "OBJECT_SPEC_INVALID", "DATA_EXECUTION_CANCELLED"] | None = Field(None, validation_alias="errorCode", serialization_alias="errorCode", description="The error code.")
    error_message: str | None = Field(None, validation_alias="errorMessage", serialization_alias="errorMessage", description="The error message, which may be empty.")
    last_refresh_time: str | None = Field(None, validation_alias="lastRefreshTime", serialization_alias="lastRefreshTime", description="Gets the time the data last successfully refreshed.", json_schema_extra={'format': 'google-datetime'})
    state: Literal["DATA_EXECUTION_STATE_UNSPECIFIED", "NOT_STARTED", "RUNNING", "CANCELLING", "SUCCEEDED", "FAILED"] | None = Field(None, description="The state of the data execution.")

class DataSourceChartProperties(PermissiveModel):
    """Properties of a data source chart."""
    data_execution_status: DataExecutionStatus | None = Field(None, validation_alias="dataExecutionStatus", serialization_alias="dataExecutionStatus", description="Output only. The data execution status.")
    data_source_id: str | None = Field(None, validation_alias="dataSourceId", serialization_alias="dataSourceId", description="ID of the data source that the chart is associated with.")

class DataSourceColumnReference(PermissiveModel):
    """An unique identifier that references a data source column."""
    name: str | None = Field(None, description="The display name of the column. It should be unique within a data source.")

class DataSourceColumn(PermissiveModel):
    """A column in a data source."""
    formula: str | None = Field(None, description="The formula of the calculated column.")
    reference: DataSourceColumnReference | None = Field(None, description="The column reference.")

class DataSourceFormula(PermissiveModel):
    """A data source formula."""
    data_execution_status: DataExecutionStatus | None = Field(None, validation_alias="dataExecutionStatus", serialization_alias="dataExecutionStatus", description="Output only. The data execution status.")
    data_source_id: str | None = Field(None, validation_alias="dataSourceId", serialization_alias="dataSourceId", description="The ID of the data source the formula is associated with.")

class DataSourceSheetDimensionRange(PermissiveModel):
    """A range along a single dimension on a DATA_SOURCE sheet."""
    column_references: list[DataSourceColumnReference] | None = Field(None, validation_alias="columnReferences", serialization_alias="columnReferences", description="The columns on the data source sheet.")
    sheet_id: int | None = Field(None, validation_alias="sheetId", serialization_alias="sheetId", description="The ID of the data source sheet the range is on.", json_schema_extra={'format': 'int32'})

class DataSourceSheetProperties(PermissiveModel):
    """Additional properties of a DATA_SOURCE sheet."""
    columns: list[DataSourceColumn] | None = Field(None, description="The columns displayed on the sheet, corresponding to the values in RowData.")
    data_execution_status: DataExecutionStatus | None = Field(None, validation_alias="dataExecutionStatus", serialization_alias="dataExecutionStatus", description="The data execution status.")
    data_source_id: str | None = Field(None, validation_alias="dataSourceId", serialization_alias="dataSourceId", description="ID of the DataSource the sheet is connected to.")

class DataValidationRule(PermissiveModel):
    """A data validation rule."""
    condition: BooleanCondition | None = Field(None, description="The condition that data in the cell must match.")
    input_message: str | None = Field(None, validation_alias="inputMessage", serialization_alias="inputMessage", description="A message to show the user when adding data to the cell.")
    show_custom_ui: bool | None = Field(None, validation_alias="showCustomUi", serialization_alias="showCustomUi", description="True if the UI should be customized based on the kind of condition. If true, \"List\" conditions will show a dropdown.")
    strict: bool | None = Field(None, description="True if invalid data should be rejected.")

class DateTimeRule(PermissiveModel):
    """Allows you to organize the date-time values in a source data column into buckets based on selected parts of their date or time values. For example, consider a pivot table showing sales transactions by date: +----------+--------------+ | Date | SUM of Sales | +----------+--------------+ | 1/1/2017 | $621.14 | | 2/3/2017 | $708.84 | | 5/8/2017 | $326.84 | ... +----------+--------------+ Applying a date-time group rule with a DateTimeRuleType of YEAR_MONTH results in the following pivot table. +--------------+--------------+ | Grouped Date | SUM of Sales | +--------------+--------------+ | 2017-Jan | $53,731.78 | | 2017-Feb | $83,475.32 | | 2017-Mar | $94,385.05 | ... +--------------+--------------+"""
    type_: Literal["DATE_TIME_RULE_TYPE_UNSPECIFIED", "SECOND", "MINUTE", "HOUR", "HOUR_MINUTE", "HOUR_MINUTE_AMPM", "DAY_OF_WEEK", "DAY_OF_YEAR", "DAY_OF_MONTH", "DAY_MONTH", "MONTH", "QUARTER", "YEAR", "YEAR_MONTH", "YEAR_QUARTER", "YEAR_MONTH_DAY"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of date-time grouping to apply.")

class DeleteBandingRequest(PermissiveModel):
    """Removes the banded range with the given ID from the spreadsheet."""
    banded_range_id: int | None = Field(None, validation_alias="bandedRangeId", serialization_alias="bandedRangeId", description="The ID of the banded range to delete.", json_schema_extra={'format': 'int32'})

class DeleteConditionalFormatRuleRequest(PermissiveModel):
    """Deletes a conditional format rule at the given index. All subsequent rules' indexes are decremented."""
    index: int | None = Field(None, description="The zero-based index of the rule to be deleted.", json_schema_extra={'format': 'int32'})
    sheet_id: int | None = Field(None, validation_alias="sheetId", serialization_alias="sheetId", description="The sheet the rule is being deleted from.", json_schema_extra={'format': 'int32'})

class DeleteDataSourceRequest(PermissiveModel):
    """Deletes a data source. The request also deletes the associated data source sheet, and unlinks all associated data source objects."""
    data_source_id: str | None = Field(None, validation_alias="dataSourceId", serialization_alias="dataSourceId", description="The ID of the data source to delete.")

class DeleteEmbeddedObjectRequest(PermissiveModel):
    """Deletes the embedded object with the given ID."""
    object_id: int | None = Field(None, validation_alias="objectId", serialization_alias="objectId", description="The ID of the embedded object to delete.", json_schema_extra={'format': 'int32'})

class DeleteFilterViewRequest(PermissiveModel):
    """Deletes a particular filter view."""
    filter_id: int | None = Field(None, validation_alias="filterId", serialization_alias="filterId", description="The ID of the filter to delete.", json_schema_extra={'format': 'int32'})

class DeleteNamedRangeRequest(PermissiveModel):
    """Removes the named range with the given ID from the spreadsheet."""
    named_range_id: str | None = Field(None, validation_alias="namedRangeId", serialization_alias="namedRangeId", description="The ID of the named range to delete.")

class DeleteProtectedRangeRequest(PermissiveModel):
    """Deletes the protected range with the given ID."""
    protected_range_id: int | None = Field(None, validation_alias="protectedRangeId", serialization_alias="protectedRangeId", description="The ID of the protected range to delete.", json_schema_extra={'format': 'int32'})

class DeleteSheetRequest(PermissiveModel):
    """Deletes the requested sheet."""
    sheet_id: int | None = Field(None, validation_alias="sheetId", serialization_alias="sheetId", description="The ID of the sheet to delete. If the sheet is of DATA_SOURCE type, the associated DataSource is also deleted.", json_schema_extra={'format': 'int32'})

class DeleteTableRequest(PermissiveModel):
    """Removes the table with the given ID from the spreadsheet."""
    table_id: str | None = Field(None, validation_alias="tableId", serialization_alias="tableId", description="The ID of the table to delete.")

class DimensionRange(PermissiveModel):
    """A range along a single dimension on a sheet. All indexes are zero-based. Indexes are half open: the start index is inclusive and the end index is exclusive. Missing indexes indicate the range is unbounded on that side."""
    dimension: Literal["DIMENSION_UNSPECIFIED", "ROWS", "COLUMNS"] | None = Field(None, description="The dimension of the span.")
    end_index: int | None = Field(None, validation_alias="endIndex", serialization_alias="endIndex", description="The end (exclusive) of the span, or not set if unbounded.", json_schema_extra={'format': 'int32'})
    sheet_id: int | None = Field(None, validation_alias="sheetId", serialization_alias="sheetId", description="The sheet this span is on.", json_schema_extra={'format': 'int32'})
    start_index: int | None = Field(None, validation_alias="startIndex", serialization_alias="startIndex", description="The start (inclusive) of the span, or not set if unbounded.", json_schema_extra={'format': 'int32'})

class AddDimensionGroupRequest(PermissiveModel):
    """Creates a group over the specified range. If the requested range is a superset of the range of an existing group G, then the depth of G is incremented and this new group G' has the depth of that group. For example, a group [C:D, depth 1] + [B:E] results in groups [B:E, depth 1] and [C:D, depth 2]. If the requested range is a subset of the range of an existing group G, then the depth of the new group G' becomes one greater than the depth of G. For example, a group [B:E, depth 1] + [C:D] results in groups [B:E, depth 1] and [C:D, depth 2]. If the requested range starts before and ends within, or starts within and ends after, the range of an existing group G, then the range of the existing group G becomes the union of the ranges, and the new group G' has depth one greater than the depth of G and range as the intersection of the ranges. For example, a group [B:D, depth 1] + [C:E] results in groups [B:E, depth 1] and [C:D, depth 2]."""
    range_: DimensionRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range over which to create a group.")

class AutoResizeDimensionsRequest(PermissiveModel):
    """Automatically resizes one or more dimensions based on the contents of the cells in that dimension."""
    data_source_sheet_dimensions: DataSourceSheetDimensionRange | None = Field(None, validation_alias="dataSourceSheetDimensions", serialization_alias="dataSourceSheetDimensions", description="The dimensions on a data source sheet to automatically resize.")
    dimensions: DimensionRange | None = Field(None, description="The dimensions to automatically resize.")

class DeleteDimensionGroupRequest(PermissiveModel):
    """Deletes a group over the specified range by decrementing the depth of the dimensions in the range. For example, assume the sheet has a depth-1 group over B:E and a depth-2 group over C:D. Deleting a group over D:E leaves the sheet with a depth-1 group over B:D and a depth-2 group over C:C."""
    range_: DimensionRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range of the group to be deleted.")

class DeleteDimensionRequest(PermissiveModel):
    """ Deletes the dimensions from the sheet."""
    range_: DimensionRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The dimensions to delete from the sheet.")

class DeveloperMetadataLocation(PermissiveModel):
    """A location where metadata may be associated in a spreadsheet."""
    dimension_range: DimensionRange | None = Field(None, validation_alias="dimensionRange", serialization_alias="dimensionRange", description="Represents the row or column when metadata is associated with a dimension. The specified DimensionRange must represent a single row or column. It cannot be unbounded or span multiple rows or columns.")
    location_type: Literal["DEVELOPER_METADATA_LOCATION_TYPE_UNSPECIFIED", "ROW", "COLUMN", "SHEET", "SPREADSHEET"] | None = Field(None, validation_alias="locationType", serialization_alias="locationType", description="The type of location this object represents. This field is read-only.")
    sheet_id: int | None = Field(None, validation_alias="sheetId", serialization_alias="sheetId", description="The ID of the sheet when metadata is associated with an entire sheet.", json_schema_extra={'format': 'int32'})
    spreadsheet: bool | None = Field(None, description="True when metadata is associated with an entire spreadsheet.")

class DeveloperMetadata(PermissiveModel):
    """Developer metadata associated with a location or object in a spreadsheet. For more information, see [Read, write, and search metadata](https://developers.google.com/workspace/sheets/api/guides/metadata). Developer metadata may be used to associate arbitrary data with various parts of a spreadsheet and it will remain associated at those locations as they move around and the spreadsheet is edited. For example, if developer metadata is associated with row 5 and another row is then subsequently inserted above row 5, that original metadata is still associated with the row it was first associated with (what is now row 6). If the associated object is deleted then its metadata is deleted too."""
    location: DeveloperMetadataLocation | None = Field(None, description="The location where the metadata is associated.")
    metadata_id: int | None = Field(None, validation_alias="metadataId", serialization_alias="metadataId", description="The spreadsheet-scoped unique ID that identifies the metadata. IDs may be specified when metadata is created, otherwise one will be randomly generated and assigned. Must be positive.", json_schema_extra={'format': 'int32'})
    metadata_key: str | None = Field(None, validation_alias="metadataKey", serialization_alias="metadataKey", description="The metadata key. There may be multiple metadata in a spreadsheet with the same key. Developer metadata must always have a key specified.")
    metadata_value: str | None = Field(None, validation_alias="metadataValue", serialization_alias="metadataValue", description="Data associated with the metadata's key.")
    visibility: Literal["DEVELOPER_METADATA_VISIBILITY_UNSPECIFIED", "DOCUMENT", "PROJECT"] | None = Field(None, description="The metadata visibility. Developer metadata must always have visibility specified.")

class CreateDeveloperMetadataRequest(PermissiveModel):
    """A request to create developer metadata."""
    developer_metadata: DeveloperMetadata | None = Field(None, validation_alias="developerMetadata", serialization_alias="developerMetadata", description="The developer metadata to create.")

class DeveloperMetadataLookup(PermissiveModel):
    """Selects DeveloperMetadata that matches all of the specified fields. For example, if only a metadata ID is specified this considers the DeveloperMetadata with that particular unique ID. If a metadata key is specified, this considers all developer metadata with that key. If a key, visibility, and location type are all specified, this considers all developer metadata with that key and visibility that are associated with a location of that type. In general, this selects all DeveloperMetadata that match the intersection of all the specified fields; any field or combination of fields may be specified."""
    location_matching_strategy: Literal["DEVELOPER_METADATA_LOCATION_MATCHING_STRATEGY_UNSPECIFIED", "EXACT_LOCATION", "INTERSECTING_LOCATION"] | None = Field(None, validation_alias="locationMatchingStrategy", serialization_alias="locationMatchingStrategy", description="Determines how this lookup matches the location. If this field is specified as EXACT, only developer metadata associated on the exact location specified is matched. If this field is specified to INTERSECTING, developer metadata associated on intersecting locations is also matched. If left unspecified, this field assumes a default value of INTERSECTING. If this field is specified, a metadataLocation must also be specified.")
    location_type: Literal["DEVELOPER_METADATA_LOCATION_TYPE_UNSPECIFIED", "ROW", "COLUMN", "SHEET", "SPREADSHEET"] | None = Field(None, validation_alias="locationType", serialization_alias="locationType", description="Limits the selected developer metadata to those entries which are associated with locations of the specified type. For example, when this field is specified as ROW this lookup only considers developer metadata associated on rows. If the field is left unspecified, all location types are considered. This field cannot be specified as SPREADSHEET when the locationMatchingStrategy is specified as INTERSECTING or when the metadataLocation is specified as a non-spreadsheet location. Spreadsheet metadata cannot intersect any other developer metadata location. This field also must be left unspecified when the locationMatchingStrategy is specified as EXACT.")
    metadata_id: int | None = Field(None, validation_alias="metadataId", serialization_alias="metadataId", description="Limits the selected developer metadata to that which has a matching DeveloperMetadata.metadata_id.", json_schema_extra={'format': 'int32'})
    metadata_key: str | None = Field(None, validation_alias="metadataKey", serialization_alias="metadataKey", description="Limits the selected developer metadata to that which has a matching DeveloperMetadata.metadata_key.")
    metadata_location: DeveloperMetadataLocation | None = Field(None, validation_alias="metadataLocation", serialization_alias="metadataLocation", description="Limits the selected developer metadata to those entries associated with the specified location. This field either matches exact locations or all intersecting locations according the specified locationMatchingStrategy.")
    metadata_value: str | None = Field(None, validation_alias="metadataValue", serialization_alias="metadataValue", description="Limits the selected developer metadata to that which has a matching DeveloperMetadata.metadata_value.")
    visibility: Literal["DEVELOPER_METADATA_VISIBILITY_UNSPECIFIED", "DOCUMENT", "PROJECT"] | None = Field(None, description="Limits the selected developer metadata to that which has a matching DeveloperMetadata.visibility. If left unspecified, all developer metadata visible to the requesting project is considered.")

class DimensionGroup(PermissiveModel):
    """A group over an interval of rows or columns on a sheet, which can contain or be contained within other groups. A group can be collapsed or expanded as a unit on the sheet."""
    collapsed: bool | None = Field(None, description="This field is true if this group is collapsed. A collapsed group remains collapsed if an overlapping group at a shallower depth is expanded. A true value does not imply that all dimensions within the group are hidden, since a dimension's visibility can change independently from this group property. However, when this property is updated, all dimensions within it are set to hidden if this field is true, or set to visible if this field is false.")
    depth: int | None = Field(None, description="The depth of the group, representing how many groups have a range that wholly contains the range of this group.", json_schema_extra={'format': 'int32'})
    range_: DimensionRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range over which this group exists.")

class DimensionProperties(PermissiveModel):
    """Properties about a dimension."""
    data_source_column_reference: DataSourceColumnReference | None = Field(None, validation_alias="dataSourceColumnReference", serialization_alias="dataSourceColumnReference", description="Output only. If set, this is a column in a data source sheet.")
    developer_metadata: list[DeveloperMetadata] | None = Field(None, validation_alias="developerMetadata", serialization_alias="developerMetadata", description="The developer metadata associated with a single row or column.")
    hidden_by_filter: bool | None = Field(None, validation_alias="hiddenByFilter", serialization_alias="hiddenByFilter", description="True if this dimension is being filtered. This field is read-only.")
    hidden_by_user: bool | None = Field(None, validation_alias="hiddenByUser", serialization_alias="hiddenByUser", description="True if this dimension is explicitly hidden.")
    pixel_size: int | None = Field(None, validation_alias="pixelSize", serialization_alias="pixelSize", description="The height (if a row) or width (if a column) of the dimension in pixels.", json_schema_extra={'format': 'int32'})

class DuplicateFilterViewRequest(PermissiveModel):
    """Duplicates a particular filter view."""
    filter_id: int | None = Field(None, validation_alias="filterId", serialization_alias="filterId", description="The ID of the filter being duplicated.", json_schema_extra={'format': 'int32'})

class DuplicateSheetRequest(PermissiveModel):
    """Duplicates the contents of a sheet."""
    insert_sheet_index: int | None = Field(None, validation_alias="insertSheetIndex", serialization_alias="insertSheetIndex", description="The zero-based index where the new sheet should be inserted. The index of all sheets after this are incremented.", json_schema_extra={'format': 'int32'})
    new_sheet_id: int | None = Field(None, validation_alias="newSheetId", serialization_alias="newSheetId", description="If set, the ID of the new sheet. If not set, an ID is chosen. If set, the ID must not conflict with any existing sheet ID. If set, it must be non-negative.", json_schema_extra={'format': 'int32'})
    new_sheet_name: str | None = Field(None, validation_alias="newSheetName", serialization_alias="newSheetName", description="The name of the new sheet. If empty, a new name is chosen for you.")
    source_sheet_id: int | None = Field(None, validation_alias="sourceSheetId", serialization_alias="sourceSheetId", description="The sheet to duplicate. If the source sheet is of DATA_SOURCE type, its backing DataSource is also duplicated and associated with the new copy of the sheet. No data execution is triggered, the grid data of this sheet is also copied over but only available after the batch request completes.", json_schema_extra={'format': 'int32'})

class Editors(PermissiveModel):
    """The editors of a protected range."""
    domain_users_can_edit: bool | None = Field(None, validation_alias="domainUsersCanEdit", serialization_alias="domainUsersCanEdit", description="True if anyone in the document's domain has edit access to the protected range. Domain protection is only supported on documents within a domain.")
    groups: list[str] | None = Field(None, description="The email addresses of groups with edit access to the protected range.")
    users: list[str] | None = Field(None, description="The email addresses of users with edit access to the protected range.")

class EmbeddedObjectBorder(PermissiveModel):
    """A border along an embedded object."""
    color: Color | None = Field(None, description="The color of the border. Deprecated: Use color_style.")
    color_style: ColorStyle | None = Field(None, validation_alias="colorStyle", serialization_alias="colorStyle", description="The color of the border. If color is also set, this field takes precedence.")

class ErrorValue(PermissiveModel):
    """An error in a cell."""
    message: str | None = Field(None, description="A message with more information about the error (in the spreadsheet's locale).")
    type_: Literal["ERROR_TYPE_UNSPECIFIED", "ERROR", "NULL_VALUE", "DIVIDE_BY_ZERO", "VALUE", "REF", "NAME", "NUM", "N_A", "LOADING"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of error.")

class ExtendedValue(PermissiveModel):
    """The kinds of value that a cell in a spreadsheet can have."""
    bool_value: bool | None = Field(None, validation_alias="boolValue", serialization_alias="boolValue", description="Represents a boolean value.")
    error_value: ErrorValue | None = Field(None, validation_alias="errorValue", serialization_alias="errorValue", description="Represents an error. This field is read-only.")
    formula_value: str | None = Field(None, validation_alias="formulaValue", serialization_alias="formulaValue", description="Represents a formula.")
    number_value: float | None = Field(None, validation_alias="numberValue", serialization_alias="numberValue", description="Represents a double value. Note: Dates, Times and DateTimes are represented as doubles in SERIAL_NUMBER format.", json_schema_extra={'format': 'double'})
    string_value: str | None = Field(None, validation_alias="stringValue", serialization_alias="stringValue", description="Represents a string value. Leading single quotes are not included. For example, if the user typed `'123` into the UI, this would be represented as a `stringValue` of `\"123\"`.")

class FilterCriteria(PermissiveModel):
    """Criteria for showing or hiding rows in a filter or filter view."""
    condition: BooleanCondition | None = Field(None, description="A condition that must be `true` for values to be shown. (This does not override hidden_values -- if a value is listed there, it will still be hidden.)")
    hidden_values: list[str] | None = Field(None, validation_alias="hiddenValues", serialization_alias="hiddenValues", description="Values that should be hidden.")
    visible_background_color: Color | None = Field(None, validation_alias="visibleBackgroundColor", serialization_alias="visibleBackgroundColor", description="The background fill color to filter by; only cells with this fill color are shown. Mutually exclusive with visible_foreground_color. Deprecated: Use visible_background_color_style.")
    visible_background_color_style: ColorStyle | None = Field(None, validation_alias="visibleBackgroundColorStyle", serialization_alias="visibleBackgroundColorStyle", description="The background fill color to filter by; only cells with this fill color are shown. This field is mutually exclusive with visible_foreground_color, and must be set to an RGB-type color. If visible_background_color is also set, this field takes precedence.")
    visible_foreground_color: Color | None = Field(None, validation_alias="visibleForegroundColor", serialization_alias="visibleForegroundColor", description="The foreground color to filter by; only cells with this foreground color are shown. Mutually exclusive with visible_background_color. Deprecated: Use visible_foreground_color_style.")
    visible_foreground_color_style: ColorStyle | None = Field(None, validation_alias="visibleForegroundColorStyle", serialization_alias="visibleForegroundColorStyle", description="The foreground color to filter by; only cells with this foreground color are shown. This field is mutually exclusive with visible_background_color, and must be set to an RGB-type color. If visible_foreground_color is also set, this field takes precedence.")

class FilterSpec(PermissiveModel):
    """The filter criteria associated with a specific column."""
    column_index: int | None = Field(None, validation_alias="columnIndex", serialization_alias="columnIndex", description="The zero-based column index.", json_schema_extra={'format': 'int32'})
    data_source_column_reference: DataSourceColumnReference | None = Field(None, validation_alias="dataSourceColumnReference", serialization_alias="dataSourceColumnReference", description="Reference to a data source column.")
    filter_criteria: FilterCriteria | None = Field(None, validation_alias="filterCriteria", serialization_alias="filterCriteria", description="The criteria for the column.")

class GridCoordinate(PermissiveModel):
    """A coordinate in a sheet. All indexes are zero-based."""
    column_index: int | None = Field(None, validation_alias="columnIndex", serialization_alias="columnIndex", description="The column index of the coordinate.", json_schema_extra={'format': 'int32'})
    row_index: int | None = Field(None, validation_alias="rowIndex", serialization_alias="rowIndex", description="The row index of the coordinate.", json_schema_extra={'format': 'int32'})
    sheet_id: int | None = Field(None, validation_alias="sheetId", serialization_alias="sheetId", description="The sheet this coordinate is on.", json_schema_extra={'format': 'int32'})

class DataSourceObjectReference(PermissiveModel):
    """Reference to a data source object."""
    chart_id: int | None = Field(None, validation_alias="chartId", serialization_alias="chartId", description="References to a data source chart.", json_schema_extra={'format': 'int32'})
    data_source_formula_cell: GridCoordinate | None = Field(None, validation_alias="dataSourceFormulaCell", serialization_alias="dataSourceFormulaCell", description="References to a cell containing DataSourceFormula.")
    data_source_pivot_table_anchor_cell: GridCoordinate | None = Field(None, validation_alias="dataSourcePivotTableAnchorCell", serialization_alias="dataSourcePivotTableAnchorCell", description="References to a data source PivotTable anchored at the cell.")
    data_source_table_anchor_cell: GridCoordinate | None = Field(None, validation_alias="dataSourceTableAnchorCell", serialization_alias="dataSourceTableAnchorCell", description="References to a DataSourceTable anchored at the cell.")
    sheet_id: str | None = Field(None, validation_alias="sheetId", serialization_alias="sheetId", description="References to a DATA_SOURCE sheet.")

class DataSourceObjectReferences(PermissiveModel):
    """A list of references to data source objects."""
    references: list[DataSourceObjectReference] | None = Field(None, description="The references.")

class CancelDataSourceRefreshRequest(PermissiveModel):
    """Cancels one or multiple refreshes of data source objects in the spreadsheet by the specified references. The request requires an additional `bigquery.readonly` OAuth scope if you are cancelling a refresh on a BigQuery data source."""
    data_source_id: str | None = Field(None, validation_alias="dataSourceId", serialization_alias="dataSourceId", description="Reference to a DataSource. If specified, cancels all associated data source object refreshes for this data source.")
    is_all: bool | None = Field(None, validation_alias="isAll", serialization_alias="isAll", description="Cancels all existing data source object refreshes for all data sources in the spreadsheet.")
    references: DataSourceObjectReferences | None = Field(None, description="References to data source objects whose refreshes are to be cancelled.")

class GridProperties(PermissiveModel):
    """Properties of a grid."""
    column_count: int | None = Field(None, validation_alias="columnCount", serialization_alias="columnCount", description="The number of columns in the grid.", json_schema_extra={'format': 'int32'})
    column_group_control_after: bool | None = Field(None, validation_alias="columnGroupControlAfter", serialization_alias="columnGroupControlAfter", description="True if the column grouping control toggle is shown after the group.")
    frozen_column_count: int | None = Field(None, validation_alias="frozenColumnCount", serialization_alias="frozenColumnCount", description="The number of columns that are frozen in the grid.", json_schema_extra={'format': 'int32'})
    frozen_row_count: int | None = Field(None, validation_alias="frozenRowCount", serialization_alias="frozenRowCount", description="The number of rows that are frozen in the grid.", json_schema_extra={'format': 'int32'})
    hide_gridlines: bool | None = Field(None, validation_alias="hideGridlines", serialization_alias="hideGridlines", description="True if the grid isn't showing gridlines in the UI.")
    row_count: int | None = Field(None, validation_alias="rowCount", serialization_alias="rowCount", description="The number of rows in the grid.", json_schema_extra={'format': 'int32'})
    row_group_control_after: bool | None = Field(None, validation_alias="rowGroupControlAfter", serialization_alias="rowGroupControlAfter", description="True if the row grouping control toggle is shown after the group.")

class GridRange(PermissiveModel):
    """A range on a sheet. All indexes are zero-based. Indexes are half open, i.e. the start index is inclusive and the end index is exclusive -- [start_index, end_index). Missing indexes indicate the range is unbounded on that side. For example, if `"Sheet1"` is sheet ID 123456, then: `Sheet1!A1:A1 == sheet_id: 123456, start_row_index: 0, end_row_index: 1, start_column_index: 0, end_column_index: 1` `Sheet1!A3:B4 == sheet_id: 123456, start_row_index: 2, end_row_index: 4, start_column_index: 0, end_column_index: 2` `Sheet1!A:B == sheet_id: 123456, start_column_index: 0, end_column_index: 2` `Sheet1!A5:B == sheet_id: 123456, start_row_index: 4, start_column_index: 0, end_column_index: 2` `Sheet1 == sheet_id: 123456` The start index must always be less than or equal to the end index. If the start index equals the end index, then the range is empty. Empty ranges are typically not meaningful and are usually rendered in the UI as `#REF!`."""
    end_column_index: int | None = Field(None, validation_alias="endColumnIndex", serialization_alias="endColumnIndex", description="The end column (exclusive) of the range, or not set if unbounded.", json_schema_extra={'format': 'int32'})
    end_row_index: int | None = Field(None, validation_alias="endRowIndex", serialization_alias="endRowIndex", description="The end row (exclusive) of the range, or not set if unbounded.", json_schema_extra={'format': 'int32'})
    sheet_id: int | None = Field(None, validation_alias="sheetId", serialization_alias="sheetId", description="The sheet this range is on.", json_schema_extra={'format': 'int32'})
    start_column_index: int | None = Field(None, validation_alias="startColumnIndex", serialization_alias="startColumnIndex", description="The start column (inclusive) of the range, or not set if unbounded.", json_schema_extra={'format': 'int32'})
    start_row_index: int | None = Field(None, validation_alias="startRowIndex", serialization_alias="startRowIndex", description="The start row (inclusive) of the range, or not set if unbounded.", json_schema_extra={'format': 'int32'})

class BandedRange(PermissiveModel):
    """A banded (alternating colors) range in a sheet."""
    banded_range_id: int | None = Field(None, validation_alias="bandedRangeId", serialization_alias="bandedRangeId", description="The ID of the banded range. If unset, refer to banded_range_reference.", json_schema_extra={'format': 'int32'})
    banded_range_reference: str | None = Field(None, validation_alias="bandedRangeReference", serialization_alias="bandedRangeReference", description="Output only. The reference of the banded range, used to identify the ID that is not supported by the banded_range_id.")
    column_properties: BandingProperties | None = Field(None, validation_alias="columnProperties", serialization_alias="columnProperties", description="Properties for column bands. These properties are applied on a column- by-column basis throughout all the columns in the range. At least one of row_properties or column_properties must be specified.")
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range over which these properties are applied.")
    row_properties: BandingProperties | None = Field(None, validation_alias="rowProperties", serialization_alias="rowProperties", description="Properties for row bands. These properties are applied on a row-by-row basis throughout all the rows in the range. At least one of row_properties or column_properties must be specified.")

class AddBandingRequest(PermissiveModel):
    """Adds a new banded range to the spreadsheet."""
    banded_range: BandedRange | None = Field(None, validation_alias="bandedRange", serialization_alias="bandedRange", description="The banded range to add. The bandedRangeId field is optional; if one is not set, an id will be randomly generated. (It is an error to specify the ID of a range that already exists.)")

class ChartSourceRange(PermissiveModel):
    """Source ranges for a chart."""
    sources: list[GridRange] | None = Field(None, description="The ranges of data for a series or domain. Exactly one dimension must have a length of 1, and all sources in the list must have the same dimension with length 1. The domain (if it exists) & all series must have the same number of source ranges. If using more than one source range, then the source range at a given offset must be in order and contiguous across the domain and series. For example, these are valid configurations: domain sources: A1:A5 series1 sources: B1:B5 series2 sources: D6:D10 domain sources: A1:A5, C10:C12 series1 sources: B1:B5, D10:D12 series2 sources: C1:C5, E10:E12")

class ChartData(PermissiveModel):
    """The data included in a domain or series."""
    aggregate_type: Literal["CHART_AGGREGATE_TYPE_UNSPECIFIED", "AVERAGE", "COUNT", "MAX", "MEDIAN", "MIN", "SUM"] | None = Field(None, validation_alias="aggregateType", serialization_alias="aggregateType", description="The aggregation type for the series of a data source chart. Only supported for data source charts.")
    column_reference: DataSourceColumnReference | None = Field(None, validation_alias="columnReference", serialization_alias="columnReference", description="The reference to the data source column that the data reads from.")
    group_rule: ChartGroupRule | None = Field(None, validation_alias="groupRule", serialization_alias="groupRule", description="The rule to group the data by if the ChartData backs the domain of a data source chart. Only supported for data source charts.")
    source_range: ChartSourceRange | None = Field(None, validation_alias="sourceRange", serialization_alias="sourceRange", description="The source ranges of the data.")

class BasicChartDomain(PermissiveModel):
    """The domain of a chart. For example, if charting stock prices over time, this would be the date."""
    domain: ChartData | None = Field(None, description="The data of the domain. For example, if charting stock prices over time, this is the data representing the dates.")
    reversed_: bool | None = Field(None, validation_alias="reversed", serialization_alias="reversed", description="True to reverse the order of the domain values (horizontal axis).")

class CandlestickDomain(PermissiveModel):
    """The domain of a CandlestickChart."""
    data: ChartData | None = Field(None, description="The data of the CandlestickDomain.")
    reversed_: bool | None = Field(None, validation_alias="reversed", serialization_alias="reversed", description="True to reverse the order of the domain values (horizontal axis).")

class CandlestickSeries(PermissiveModel):
    """The series of a CandlestickData."""
    data: ChartData | None = Field(None, description="The data of the CandlestickSeries.")

class CandlestickData(PermissiveModel):
    """The Candlestick chart data, each containing the low, open, close, and high values for a series."""
    close_series: CandlestickSeries | None = Field(None, validation_alias="closeSeries", serialization_alias="closeSeries", description="The range data (vertical axis) for the close/final value for each candle. This is the top of the candle body. If greater than the open value the candle will be filled. Otherwise the candle will be hollow.")
    high_series: CandlestickSeries | None = Field(None, validation_alias="highSeries", serialization_alias="highSeries", description="The range data (vertical axis) for the high/maximum value for each candle. This is the top of the candle's center line.")
    low_series: CandlestickSeries | None = Field(None, validation_alias="lowSeries", serialization_alias="lowSeries", description="The range data (vertical axis) for the low/minimum value for each candle. This is the bottom of the candle's center line.")
    open_series: CandlestickSeries | None = Field(None, validation_alias="openSeries", serialization_alias="openSeries", description="The range data (vertical axis) for the open/initial value for each candle. This is the bottom of the candle body. If less than the close value the candle will be filled. Otherwise the candle will be hollow.")

class CandlestickChartSpec(PermissiveModel):
    """A candlestick chart."""
    data: list[CandlestickData] | None = Field(None, description="The Candlestick chart data. Only one CandlestickData is supported.")
    domain: CandlestickDomain | None = Field(None, description="The domain data (horizontal axis) for the candlestick chart. String data will be treated as discrete labels, other data will be treated as continuous values.")

class CopyPasteRequest(PermissiveModel):
    """Copies data from the source to the destination."""
    destination: GridRange | None = Field(None, description="The location to paste to. If the range covers a span that's a multiple of the source's height or width, then the data will be repeated to fill in the destination range. If the range is smaller than the source range, the entire source data will still be copied (beyond the end of the destination range).")
    paste_orientation: Literal["NORMAL", "TRANSPOSE"] | None = Field(None, validation_alias="pasteOrientation", serialization_alias="pasteOrientation", description="How that data should be oriented when pasting.")
    paste_type: Literal["PASTE_NORMAL", "PASTE_VALUES", "PASTE_FORMAT", "PASTE_NO_BORDERS", "PASTE_FORMULA", "PASTE_DATA_VALIDATION", "PASTE_CONDITIONAL_FORMATTING"] | None = Field(None, validation_alias="pasteType", serialization_alias="pasteType", description="What kind of data to paste.")
    source: GridRange | None = Field(None, description="The source range to copy.")

class CutPasteRequest(PermissiveModel):
    """Moves data from the source to the destination."""
    destination: GridCoordinate | None = Field(None, description="The top-left coordinate where the data should be pasted.")
    paste_type: Literal["PASTE_NORMAL", "PASTE_VALUES", "PASTE_FORMAT", "PASTE_NO_BORDERS", "PASTE_FORMULA", "PASTE_DATA_VALIDATION", "PASTE_CONDITIONAL_FORMATTING"] | None = Field(None, validation_alias="pasteType", serialization_alias="pasteType", description="What kind of data to paste. All the source data will be cut, regardless of what is pasted.")
    source: GridRange | None = Field(None, description="The source data to cut.")

class DataFilter(PermissiveModel):
    """Filter that describes what data should be selected or returned from a request. For more information, see [Read, write, and search metadata](https://developers.google.com/workspace/sheets/api/guides/metadata)."""
    a1_range: str | None = Field(None, validation_alias="a1Range", serialization_alias="a1Range", description="Selects data that matches the specified A1 range.")
    developer_metadata_lookup: DeveloperMetadataLookup | None = Field(None, validation_alias="developerMetadataLookup", serialization_alias="developerMetadataLookup", description="Selects data associated with the developer metadata matching the criteria described by this DeveloperMetadataLookup.")
    grid_range: GridRange | None = Field(None, validation_alias="gridRange", serialization_alias="gridRange", description="Selects data that matches the range described by the GridRange.")

class DataFilterValueRange(PermissiveModel):
    """A range of values whose location is specified by a DataFilter."""
    data_filter: DataFilter | None = Field(None, validation_alias="dataFilter", serialization_alias="dataFilter", description="The data filter describing the location of the values in the spreadsheet.")
    major_dimension: Literal["DIMENSION_UNSPECIFIED", "ROWS", "COLUMNS"] | None = Field(None, validation_alias="majorDimension", serialization_alias="majorDimension", description="The major dimension of the values.")
    values: list[list[Any]] | None = Field(None, description="The data to be written. If the provided values exceed any of the ranges matched by the data filter then the request fails. If the provided values are less than the matched ranges only the specified values are written, existing values in the matched ranges remain unaffected.")

class DataSourceParameter(PermissiveModel):
    """A parameter in a data source's query. The parameter allows the user to pass in values from the spreadsheet into a query."""
    name: str | None = Field(None, description="Named parameter. Must be a legitimate identifier for the DataSource that supports it. For example, [BigQuery identifier](https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical#identifiers).")
    named_range_id: str | None = Field(None, validation_alias="namedRangeId", serialization_alias="namedRangeId", description="ID of a NamedRange. Its size must be 1x1.")
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="A range that contains the value of the parameter. Its size must be 1x1.")

class DeleteDeveloperMetadataRequest(PermissiveModel):
    """A request to delete developer metadata."""
    data_filter: DataFilter | None = Field(None, validation_alias="dataFilter", serialization_alias="dataFilter", description="The data filter describing the criteria used to select which developer metadata entry to delete.")

class DeleteDuplicatesRequest(PermissiveModel):
    """Removes rows within this range that contain values in the specified columns that are duplicates of values in any previous row. Rows with identical values but different letter cases, formatting, or formulas are considered to be duplicates. This request also removes duplicate rows hidden from view (for example, due to a filter). When removing duplicates, the first instance of each duplicate row scanning from the top downwards is kept in the resulting range. Content outside of the specified range isn't removed, and rows considered duplicates do not have to be adjacent to each other in the range."""
    comparison_columns: list[DimensionRange] | None = Field(None, validation_alias="comparisonColumns", serialization_alias="comparisonColumns", description="The columns in the range to analyze for duplicate values. If no columns are selected then all columns are analyzed for duplicates.")
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range to remove duplicates rows from.")

class DeleteRangeRequest(PermissiveModel):
    """Deletes a range of cells, shifting other cells into the deleted area."""
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range of cells to delete.")
    shift_dimension: Literal["DIMENSION_UNSPECIFIED", "ROWS", "COLUMNS"] | None = Field(None, validation_alias="shiftDimension", serialization_alias="shiftDimension", description="The dimension from which deleted cells will be replaced with. If ROWS, existing cells will be shifted upward to replace the deleted cells. If COLUMNS, existing cells will be shifted left to replace the deleted cells.")

class FindReplaceRequest(PermissiveModel):
    """Finds and replaces data in cells over a range, sheet, or all sheets."""
    all_sheets: bool | None = Field(None, validation_alias="allSheets", serialization_alias="allSheets", description="True to find/replace over all sheets.")
    find: str | None = Field(None, description="The value to search.")
    include_formulas: bool | None = Field(None, validation_alias="includeFormulas", serialization_alias="includeFormulas", description="True if the search should include cells with formulas. False to skip cells with formulas.")
    match_case: bool | None = Field(None, validation_alias="matchCase", serialization_alias="matchCase", description="True if the search is case sensitive.")
    match_entire_cell: bool | None = Field(None, validation_alias="matchEntireCell", serialization_alias="matchEntireCell", description="True if the find value should match the entire cell.")
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range to find/replace over.")
    replacement: str | None = Field(None, description="The value to use as the replacement.")
    search_by_regex: bool | None = Field(None, validation_alias="searchByRegex", serialization_alias="searchByRegex", description="True if the find value is a regex. The regular expression and replacement should follow Java regex rules at https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html. The replacement string is allowed to refer to capturing groups. For example, if one cell has the contents `\"Google Sheets\"` and another has `\"Google Docs\"`, then searching for `\"o.* (.*)\"` with a replacement of `\"$1 Rocks\"` would change the contents of the cells to `\"GSheets Rocks\"` and `\"GDocs Rocks\"` respectively.")
    sheet_id: int | None = Field(None, validation_alias="sheetId", serialization_alias="sheetId", description="The sheet to find/replace over.", json_schema_extra={'format': 'int32'})

class HistogramRule(PermissiveModel):
    """Allows you to organize the numeric values in a source data column into buckets of a constant size. All values from HistogramRule.start to HistogramRule.end are placed into groups of size HistogramRule.interval. In addition, all values below HistogramRule.start are placed in one group, and all values above HistogramRule.end are placed in another. Only HistogramRule.interval is required, though if HistogramRule.start and HistogramRule.end are both provided, HistogramRule.start must be less than HistogramRule.end. For example, a pivot table showing average purchase amount by age that has 50+ rows: +-----+-------------------+ | Age | AVERAGE of Amount | +-----+-------------------+ | 16 | $27.13 | | 17 | $5.24 | | 18 | $20.15 | ... +-----+-------------------+ could be turned into a pivot table that looks like the one below by applying a histogram group rule with a HistogramRule.start of 25, an HistogramRule.interval of 20, and an HistogramRule.end of 65. +-------------+-------------------+ | Grouped Age | AVERAGE of Amount | +-------------+-------------------+ | < 25 | $19.34 | | 25-45 | $31.43 | | 45-65 | $35.87 | | > 65 | $27.55 | +-------------+-------------------+ | Grand Total | $29.12 | +-------------+-------------------+"""
    end: float | None = Field(None, description="The maximum value at which items are placed into buckets of constant size. Values above end are lumped into a single bucket. This field is optional.", json_schema_extra={'format': 'double'})
    interval: float | None = Field(None, description="The size of the buckets that are created. Must be positive.", json_schema_extra={'format': 'double'})
    start: float | None = Field(None, description="The minimum value at which items are placed into buckets of constant size. Values below start are lumped into a single bucket. This field is optional.", json_schema_extra={'format': 'double'})

class HistogramSeries(PermissiveModel):
    """A histogram series containing the series color and data."""
    bar_color: Color | None = Field(None, validation_alias="barColor", serialization_alias="barColor", description="The color of the column representing this series in each bucket. This field is optional. Deprecated: Use bar_color_style.")
    bar_color_style: ColorStyle | None = Field(None, validation_alias="barColorStyle", serialization_alias="barColorStyle", description="The color of the column representing this series in each bucket. This field is optional. If bar_color is also set, this field takes precedence.")
    data: ChartData | None = Field(None, description="The data for this histogram series.")

class HistogramChartSpec(PermissiveModel):
    """A histogram chart. A histogram chart groups data items into bins, displaying each bin as a column of stacked items. Histograms are used to display the distribution of a dataset. Each column of items represents a range into which those items fall. The number of bins can be chosen automatically or specified explicitly."""
    bucket_size: float | None = Field(None, validation_alias="bucketSize", serialization_alias="bucketSize", description="By default the bucket size (the range of values stacked in a single column) is chosen automatically, but it may be overridden here. E.g., A bucket size of 1.5 results in buckets from 0 - 1.5, 1.5 - 3.0, etc. Cannot be negative. This field is optional.", json_schema_extra={'format': 'double'})
    legend_position: Literal["HISTOGRAM_CHART_LEGEND_POSITION_UNSPECIFIED", "BOTTOM_LEGEND", "LEFT_LEGEND", "RIGHT_LEGEND", "TOP_LEGEND", "NO_LEGEND", "INSIDE_LEGEND"] | None = Field(None, validation_alias="legendPosition", serialization_alias="legendPosition", description="The position of the chart legend.")
    outlier_percentile: float | None = Field(None, validation_alias="outlierPercentile", serialization_alias="outlierPercentile", description="The outlier percentile is used to ensure that outliers do not adversely affect the calculation of bucket sizes. For example, setting an outlier percentile of 0.05 indicates that the top and bottom 5% of values when calculating buckets. The values are still included in the chart, they will be added to the first or last buckets instead of their own buckets. Must be between 0.0 and 0.5.", json_schema_extra={'format': 'double'})
    series: list[HistogramSeries] | None = Field(None, description="The series for a histogram may be either a single series of values to be bucketed or multiple series, each of the same length, containing the name of the series followed by the values to be bucketed for that series.")
    show_item_dividers: bool | None = Field(None, validation_alias="showItemDividers", serialization_alias="showItemDividers", description="Whether horizontal divider lines should be displayed between items in each column.")

class InsertDimensionRequest(PermissiveModel):
    """Inserts rows or columns in a sheet at a particular index."""
    inherit_from_before: bool | None = Field(None, validation_alias="inheritFromBefore", serialization_alias="inheritFromBefore", description="Whether dimension properties should be extended from the dimensions before or after the newly inserted dimensions. True to inherit from the dimensions before (in which case the start index must be greater than 0), and false to inherit from the dimensions after. For example, if row index 0 has red background and row index 1 has a green background, then inserting 2 rows at index 1 can inherit either the green or red background. If `inheritFromBefore` is true, the two new rows will be red (because the row before the insertion point was red), whereas if `inheritFromBefore` is false, the two new rows will be green (because the row after the insertion point was green).")
    range_: DimensionRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The dimensions to insert. Both the start and end indexes must be bounded.")

class InsertRangeRequest(PermissiveModel):
    """Inserts cells into a range, shifting the existing cells over or down."""
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range to insert new cells into. The range is constrained to the current sheet boundaries.")
    shift_dimension: Literal["DIMENSION_UNSPECIFIED", "ROWS", "COLUMNS"] | None = Field(None, validation_alias="shiftDimension", serialization_alias="shiftDimension", description="The dimension which will be shifted when inserting cells. If ROWS, existing cells will be shifted down. If COLUMNS, existing cells will be shifted right.")

class InterpolationPoint(PermissiveModel):
    """A single interpolation point on a gradient conditional format. These pin the gradient color scale according to the color, type and value chosen."""
    color: Color | None = Field(None, description="The color this interpolation point should use. Deprecated: Use color_style.")
    color_style: ColorStyle | None = Field(None, validation_alias="colorStyle", serialization_alias="colorStyle", description="The color this interpolation point should use. If color is also set, this field takes precedence.")
    type_: Literal["INTERPOLATION_POINT_TYPE_UNSPECIFIED", "MIN", "MAX", "NUMBER", "PERCENT", "PERCENTILE"] | None = Field(None, validation_alias="type", serialization_alias="type", description="How the value should be interpreted.")
    value: str | None = Field(None, description="The value this interpolation point uses. May be a formula. Unused if type is MIN or MAX.")

class GradientRule(PermissiveModel):
    """A rule that applies a gradient color scale format, based on the interpolation points listed. The format of a cell will vary based on its contents as compared to the values of the interpolation points."""
    maxpoint: InterpolationPoint | None = Field(None, description="The final interpolation point.")
    midpoint: InterpolationPoint | None = Field(None, description="An optional midway interpolation point.")
    minpoint: InterpolationPoint | None = Field(None, description="The starting interpolation point.")

class Interval(PermissiveModel):
    """Represents a time interval, encoded as a Timestamp start (inclusive) and a Timestamp end (exclusive). The start must be less than or equal to the end. When the start equals the end, the interval is empty (matches no time). When both start and end are unspecified, the interval matches any time."""
    end_time: str | None = Field(None, validation_alias="endTime", serialization_alias="endTime", description="Optional. Exclusive end of the interval. If specified, a Timestamp matching this interval will have to be before the end.", json_schema_extra={'format': 'google-datetime'})
    start_time: str | None = Field(None, validation_alias="startTime", serialization_alias="startTime", description="Optional. Inclusive start of the interval. If specified, a Timestamp matching this interval will have to be the same or after the start.", json_schema_extra={'format': 'google-datetime'})

class IterativeCalculationSettings(PermissiveModel):
    """Settings to control how circular dependencies are resolved with iterative calculation."""
    convergence_threshold: float | None = Field(None, validation_alias="convergenceThreshold", serialization_alias="convergenceThreshold", description="When iterative calculation is enabled and successive results differ by less than this threshold value, the calculation rounds stop.", json_schema_extra={'format': 'double'})
    max_iterations: int | None = Field(None, validation_alias="maxIterations", serialization_alias="maxIterations", description="When iterative calculation is enabled, the maximum number of calculation rounds to perform.", json_schema_extra={'format': 'int32'})

class LineStyle(PermissiveModel):
    """Properties that describe the style of a line."""
    type_: Literal["LINE_DASH_TYPE_UNSPECIFIED", "INVISIBLE", "CUSTOM", "SOLID", "DOTTED", "MEDIUM_DASHED", "MEDIUM_DASHED_DOTTED", "LONG_DASHED", "LONG_DASHED_DOTTED"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The dash type of the line.")
    width: int | None = Field(None, description="The thickness of the line, in px.", json_schema_extra={'format': 'int32'})

class Link(PermissiveModel):
    """An external or local reference."""
    uri: str | None = Field(None, description="The link identifier.")

class LookerDataSourceSpec(PermissiveModel):
    """The specification of a Looker data source."""
    explore: str | None = Field(None, description="Name of a Looker model explore.")
    instance_uri: str | None = Field(None, validation_alias="instanceUri", serialization_alias="instanceUri", description="A Looker instance URL.")
    model: str | None = Field(None, description="Name of a Looker model.")

class DataSourceSpec(PermissiveModel):
    """This specifies the details of the data source. For example, for BigQuery, this specifies information about the BigQuery source."""
    big_query: BigQueryDataSourceSpec | None = Field(None, validation_alias="bigQuery", serialization_alias="bigQuery", description="A BigQueryDataSourceSpec.")
    looker: LookerDataSourceSpec | None = Field(None, description="A LookerDatasourceSpec.")
    parameters: list[DataSourceParameter] | None = Field(None, description="The parameters of the data source, used when querying the data source.")

class DataSource(PermissiveModel):
    """Information about an external data source in the spreadsheet."""
    calculated_columns: list[DataSourceColumn] | None = Field(None, validation_alias="calculatedColumns", serialization_alias="calculatedColumns", description="All calculated columns in the data source.")
    data_source_id: str | None = Field(None, validation_alias="dataSourceId", serialization_alias="dataSourceId", description="The spreadsheet-scoped unique ID that identifies the data source. Example: 1080547365.")
    sheet_id: int | None = Field(None, validation_alias="sheetId", serialization_alias="sheetId", description="The ID of the Sheet connected with the data source. The field cannot be changed once set. When creating a data source, an associated DATA_SOURCE sheet is also created, if the field is not specified, the ID of the created sheet will be randomly generated.", json_schema_extra={'format': 'int32'})
    spec: DataSourceSpec | None = Field(None, description="The DataSourceSpec for the data source connected with this spreadsheet.")

class AddDataSourceRequest(PermissiveModel):
    """Adds a data source. After the data source is added successfully, an associated DATA_SOURCE sheet is created and an execution is triggered to refresh the sheet to read data from the data source. The request requires an additional `bigquery.readonly` OAuth scope if you are adding a BigQuery data source."""
    data_source: DataSource | None = Field(None, validation_alias="dataSource", serialization_alias="dataSource", description="The data source to add.")

class ManualRuleGroup(PermissiveModel):
    """A group name and a list of items from the source data that should be placed in the group with this name."""
    group_name: ExtendedValue | None = Field(None, validation_alias="groupName", serialization_alias="groupName", description="The group name, which must be a string. Each group in a given ManualRule must have a unique group name.")
    items: list[ExtendedValue] | None = Field(None, description="The items in the source data that should be placed into this group. Each item may be a string, number, or boolean. Items may appear in at most one group within a given ManualRule. Items that do not appear in any group will appear on their own.")

class ManualRule(PermissiveModel):
    """Allows you to manually organize the values in a source data column into buckets with names of your choosing. For example, a pivot table that aggregates population by state: +-------+-------------------+ | State | SUM of Population | +-------+-------------------+ | AK | 0.7 | | AL | 4.8 | | AR | 2.9 | ... +-------+-------------------+ could be turned into a pivot table that aggregates population by time zone by providing a list of groups (for example, groupName = 'Central', items = ['AL', 'AR', 'IA', ...]) to a manual group rule. Note that a similar effect could be achieved by adding a time zone column to the source data and adjusting the pivot table. +-----------+-------------------+ | Time Zone | SUM of Population | +-----------+-------------------+ | Central | 106.3 | | Eastern | 151.9 | | Mountain | 17.4 | ... +-----------+-------------------+"""
    groups: list[ManualRuleGroup] | None = Field(None, description="The list of group names and the corresponding items from the source data that map to each group name.")

class MergeCellsRequest(PermissiveModel):
    """Merges all cells in the range."""
    merge_type: Literal["MERGE_ALL", "MERGE_COLUMNS", "MERGE_ROWS"] | None = Field(None, validation_alias="mergeType", serialization_alias="mergeType", description="How the cells should be merged.")
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range of cells to merge.")

class MoveDimensionRequest(PermissiveModel):
    """Moves one or more rows or columns."""
    destination_index: int | None = Field(None, validation_alias="destinationIndex", serialization_alias="destinationIndex", description="The zero-based start index of where to move the source data to, based on the coordinates *before* the source data is removed from the grid. Existing data will be shifted down or right (depending on the dimension) to make room for the moved dimensions. The source dimensions are removed from the grid, so the the data may end up in a different index than specified. For example, given `A1..A5` of `0, 1, 2, 3, 4` and wanting to move `\"1\"` and `\"2\"` to between `\"3\"` and `\"4\"`, the source would be `ROWS [1..3)`,and the destination index would be `\"4\"` (the zero-based index of row 5). The end result would be `A1..A5` of `0, 3, 1, 2, 4`.", json_schema_extra={'format': 'int32'})
    source: DimensionRange | None = Field(None, description="The source dimensions to move.")

class NamedRange(PermissiveModel):
    """A named range."""
    name: str | None = Field(None, description="The name of the named range.")
    named_range_id: str | None = Field(None, validation_alias="namedRangeId", serialization_alias="namedRangeId", description="The ID of the named range.")
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range this represents.")

class AddNamedRangeRequest(PermissiveModel):
    """Adds a named range to the spreadsheet."""
    named_range: NamedRange | None = Field(None, validation_alias="namedRange", serialization_alias="namedRange", description="The named range to add. The namedRangeId field is optional; if one is not set, an id will be randomly generated. (It is an error to specify the ID of a range that already exists.)")

class NumberFormat(PermissiveModel):
    """The number format of a cell."""
    pattern: str | None = Field(None, description="Pattern string used for formatting. If not set, a default pattern based on the spreadsheet's locale will be used if necessary for the given type. See the [Date and Number Formats guide](https://developers.google.com/workspace/sheets/api/guides/formats) for more information about the supported patterns.")
    type_: Literal["NUMBER_FORMAT_TYPE_UNSPECIFIED", "TEXT", "NUMBER", "PERCENT", "CURRENCY", "DATE", "TIME", "DATE_TIME", "SCIENTIFIC"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the number format. When writing, this field must be set.")

class OrgChartSpec(PermissiveModel):
    """An org chart. Org charts require a unique set of labels in labels and may optionally include parent_labels and tooltips. parent_labels contain, for each node, the label identifying the parent node. tooltips contain, for each node, an optional tooltip. For example, to describe an OrgChart with Alice as the CEO, Bob as the President (reporting to Alice) and Cathy as VP of Sales (also reporting to Alice), have labels contain "Alice", "Bob", "Cathy", parent_labels contain "", "Alice", "Alice" and tooltips contain "CEO", "President", "VP Sales"."""
    labels: ChartData | None = Field(None, description="The data containing the labels for all the nodes in the chart. Labels must be unique.")
    node_color: Color | None = Field(None, validation_alias="nodeColor", serialization_alias="nodeColor", description="The color of the org chart nodes. Deprecated: Use node_color_style.")
    node_color_style: ColorStyle | None = Field(None, validation_alias="nodeColorStyle", serialization_alias="nodeColorStyle", description="The color of the org chart nodes. If node_color is also set, this field takes precedence.")
    node_size: Literal["ORG_CHART_LABEL_SIZE_UNSPECIFIED", "SMALL", "MEDIUM", "LARGE"] | None = Field(None, validation_alias="nodeSize", serialization_alias="nodeSize", description="The size of the org chart nodes.")
    parent_labels: ChartData | None = Field(None, validation_alias="parentLabels", serialization_alias="parentLabels", description="The data containing the label of the parent for the corresponding node. A blank value indicates that the node has no parent and is a top-level node. This field is optional.")
    selected_node_color: Color | None = Field(None, validation_alias="selectedNodeColor", serialization_alias="selectedNodeColor", description="The color of the selected org chart nodes. Deprecated: Use selected_node_color_style.")
    selected_node_color_style: ColorStyle | None = Field(None, validation_alias="selectedNodeColorStyle", serialization_alias="selectedNodeColorStyle", description="The color of the selected org chart nodes. If selected_node_color is also set, this field takes precedence.")
    tooltips: ChartData | None = Field(None, description="The data containing the tooltip for the corresponding node. A blank value results in no tooltip being displayed for the node. This field is optional.")

class OverlayPosition(PermissiveModel):
    """The location an object is overlaid on top of a grid."""
    anchor_cell: GridCoordinate | None = Field(None, validation_alias="anchorCell", serialization_alias="anchorCell", description="The cell the object is anchored to.")
    height_pixels: int | None = Field(None, validation_alias="heightPixels", serialization_alias="heightPixels", description="The height of the object, in pixels. Defaults to 371.", json_schema_extra={'format': 'int32'})
    offset_x_pixels: int | None = Field(None, validation_alias="offsetXPixels", serialization_alias="offsetXPixels", description="The horizontal offset, in pixels, that the object is offset from the anchor cell.", json_schema_extra={'format': 'int32'})
    offset_y_pixels: int | None = Field(None, validation_alias="offsetYPixels", serialization_alias="offsetYPixels", description="The vertical offset, in pixels, that the object is offset from the anchor cell.", json_schema_extra={'format': 'int32'})
    width_pixels: int | None = Field(None, validation_alias="widthPixels", serialization_alias="widthPixels", description="The width of the object, in pixels. Defaults to 600.", json_schema_extra={'format': 'int32'})

class EmbeddedObjectPosition(PermissiveModel):
    """The position of an embedded object such as a chart."""
    new_sheet: bool | None = Field(None, validation_alias="newSheet", serialization_alias="newSheet", description="If true, the embedded object is put on a new sheet whose ID is chosen for you. Used only when writing.")
    overlay_position: OverlayPosition | None = Field(None, validation_alias="overlayPosition", serialization_alias="overlayPosition", description="The position at which the object is overlaid on top of a grid.")
    sheet_id: int | None = Field(None, validation_alias="sheetId", serialization_alias="sheetId", description="The sheet this is on. Set only if the embedded object is on its own sheet. Must be non-negative.", json_schema_extra={'format': 'int32'})

class Padding(PermissiveModel):
    """The amount of padding around the cell, in pixels. When updating padding, every field must be specified."""
    bottom: int | None = Field(None, description="The bottom padding of the cell.", json_schema_extra={'format': 'int32'})
    left: int | None = Field(None, description="The left padding of the cell.", json_schema_extra={'format': 'int32'})
    right: int | None = Field(None, description="The right padding of the cell.", json_schema_extra={'format': 'int32'})
    top: int | None = Field(None, description="The top padding of the cell.", json_schema_extra={'format': 'int32'})

class PasteDataRequest(PermissiveModel):
    """Inserts data into the spreadsheet starting at the specified coordinate."""
    coordinate: GridCoordinate | None = Field(None, description="The coordinate at which the data should start being inserted.")
    data: str | None = Field(None, description="The data to insert.")
    delimiter: str | None = Field(None, description="The delimiter in the data.")
    html: bool | None = Field(None, description="True if the data is HTML.")
    type_: Literal["PASTE_NORMAL", "PASTE_VALUES", "PASTE_FORMAT", "PASTE_NO_BORDERS", "PASTE_FORMULA", "PASTE_DATA_VALIDATION", "PASTE_CONDITIONAL_FORMATTING"] | None = Field(None, validation_alias="type", serialization_alias="type", description="How the data should be pasted.")

class PersonProperties(PermissiveModel):
    """Properties specific to a linked person."""
    display_format: Literal["DISPLAY_FORMAT_UNSPECIFIED", "DEFAULT", "LAST_NAME_COMMA_FIRST_NAME", "EMAIL"] | None = Field(None, validation_alias="displayFormat", serialization_alias="displayFormat", description="Optional. The display format of the person chip. If not set, the default display format is used.")
    email: str | None = Field(None, description="Required. The email address linked to this person. This field is always present.")

class PieChartSpec(PermissiveModel):
    """A pie chart."""
    domain: ChartData | None = Field(None, description="The data that covers the domain of the pie chart.")
    legend_position: Literal["PIE_CHART_LEGEND_POSITION_UNSPECIFIED", "BOTTOM_LEGEND", "LEFT_LEGEND", "RIGHT_LEGEND", "TOP_LEGEND", "NO_LEGEND", "LABELED_LEGEND"] | None = Field(None, validation_alias="legendPosition", serialization_alias="legendPosition", description="Where the legend of the pie chart should be drawn.")
    pie_hole: float | None = Field(None, validation_alias="pieHole", serialization_alias="pieHole", description="The size of the hole in the pie chart.", json_schema_extra={'format': 'double'})
    series: ChartData | None = Field(None, description="The data that covers the one and only series of the pie chart.")
    three_dimensional: bool | None = Field(None, validation_alias="threeDimensional", serialization_alias="threeDimensional", description="True if the pie is three dimensional.")

class PivotFilterCriteria(PermissiveModel):
    """Criteria for showing/hiding rows in a pivot table."""
    condition: BooleanCondition | None = Field(None, description="A condition that must be true for values to be shown. (`visibleValues` does not override this -- even if a value is listed there, it is still hidden if it does not meet the condition.) Condition values that refer to ranges in A1-notation are evaluated relative to the pivot table sheet. References are treated absolutely, so are not filled down the pivot table. For example, a condition value of `=A1` on \"Pivot Table 1\" is treated as `'Pivot Table 1'!$A$1`. The source data of the pivot table can be referenced by column header name. For example, if the source data has columns named \"Revenue\" and \"Cost\" and a condition is applied to the \"Revenue\" column with type `NUMBER_GREATER` and value `=Cost`, then only columns where \"Revenue\" > \"Cost\" are included.")
    visible_by_default: bool | None = Field(None, validation_alias="visibleByDefault", serialization_alias="visibleByDefault", description="Whether values are visible by default. If true, the visible_values are ignored, all values that meet condition (if specified) are shown. If false, values that are both in visible_values and meet condition are shown.")
    visible_values: list[str] | None = Field(None, validation_alias="visibleValues", serialization_alias="visibleValues", description="Values that should be included. Values not listed here are excluded.")

class PivotFilterSpec(PermissiveModel):
    """The pivot table filter criteria associated with a specific source column offset."""
    column_offset_index: int | None = Field(None, validation_alias="columnOffsetIndex", serialization_alias="columnOffsetIndex", description="The zero-based column offset of the source range.", json_schema_extra={'format': 'int32'})
    data_source_column_reference: DataSourceColumnReference | None = Field(None, validation_alias="dataSourceColumnReference", serialization_alias="dataSourceColumnReference", description="The reference to the data source column.")
    filter_criteria: PivotFilterCriteria | None = Field(None, validation_alias="filterCriteria", serialization_alias="filterCriteria", description="The criteria for the column.")

class PivotGroupLimit(PermissiveModel):
    """The count limit on rows or columns in the pivot group."""
    apply_order: int | None = Field(None, validation_alias="applyOrder", serialization_alias="applyOrder", description="The order in which the group limit is applied to the pivot table. Pivot group limits are applied from lower to higher order number. Order numbers are normalized to consecutive integers from 0. For write request, to fully customize the applying orders, all pivot group limits should have this field set with an unique number. Otherwise, the order is determined by the index in the PivotTable.rows list and then the PivotTable.columns list.", json_schema_extra={'format': 'int32'})
    count_limit: int | None = Field(None, validation_alias="countLimit", serialization_alias="countLimit", description="The count limit.", json_schema_extra={'format': 'int32'})

class PivotGroupRule(PermissiveModel):
    """An optional setting on a PivotGroup that defines buckets for the values in the source data column rather than breaking out each individual value. Only one PivotGroup with a group rule may be added for each column in the source data, though on any given column you may add both a PivotGroup that has a rule and a PivotGroup that does not."""
    date_time_rule: DateTimeRule | None = Field(None, validation_alias="dateTimeRule", serialization_alias="dateTimeRule", description="A DateTimeRule.")
    histogram_rule: HistogramRule | None = Field(None, validation_alias="histogramRule", serialization_alias="histogramRule", description="A HistogramRule.")
    manual_rule: ManualRule | None = Field(None, validation_alias="manualRule", serialization_alias="manualRule", description="A ManualRule.")

class PivotGroupSortValueBucket(PermissiveModel):
    """Information about which values in a pivot group should be used for sorting."""
    buckets: list[ExtendedValue] | None = Field(None, description="Determines the bucket from which values are chosen to sort. For example, in a pivot table with one row group & two column groups, the row group can list up to two values. The first value corresponds to a value within the first column group, and the second value corresponds to a value in the second column group. If no values are listed, this would indicate that the row should be sorted according to the \"Grand Total\" over the column groups. If a single value is listed, this would correspond to using the \"Total\" of that bucket.")
    values_index: int | None = Field(None, validation_alias="valuesIndex", serialization_alias="valuesIndex", description="The offset in the PivotTable.values list which the values in this grouping should be sorted by.", json_schema_extra={'format': 'int32'})

class PivotGroupValueMetadata(PermissiveModel):
    """Metadata about a value in a pivot grouping."""
    collapsed: bool | None = Field(None, description="True if the data corresponding to the value is collapsed.")
    value: ExtendedValue | None = Field(None, description="The calculated value the metadata corresponds to. (Note that formulaValue is not valid, because the values will be calculated.)")

class PivotGroup(PermissiveModel):
    """A single grouping (either row or column) in a pivot table."""
    data_source_column_reference: DataSourceColumnReference | None = Field(None, validation_alias="dataSourceColumnReference", serialization_alias="dataSourceColumnReference", description="The reference to the data source column this grouping is based on.")
    group_limit: PivotGroupLimit | None = Field(None, validation_alias="groupLimit", serialization_alias="groupLimit", description="The count limit on rows or columns to apply to this pivot group.")
    group_rule: PivotGroupRule | None = Field(None, validation_alias="groupRule", serialization_alias="groupRule", description="The group rule to apply to this row/column group.")
    label: str | None = Field(None, description="The labels to use for the row/column groups which can be customized. For example, in the following pivot table, the row label is `Region` (which could be renamed to `State`) and the column label is `Product` (which could be renamed `Item`). Pivot tables created before December 2017 do not have header labels. If you'd like to add header labels to an existing pivot table, please delete the existing pivot table and then create a new pivot table with same parameters. +--------------+---------+-------+ | SUM of Units | Product | | | Region | Pen | Paper | +--------------+---------+-------+ | New York | 345 | 98 | | Oregon | 234 | 123 | | Tennessee | 531 | 415 | +--------------+---------+-------+ | Grand Total | 1110 | 636 | +--------------+---------+-------+")
    repeat_headings: bool | None = Field(None, validation_alias="repeatHeadings", serialization_alias="repeatHeadings", description="True if the headings in this pivot group should be repeated. This is only valid for row groupings and is ignored by columns. By default, we minimize repetition of headings by not showing higher level headings where they are the same. For example, even though the third row below corresponds to \"Q1 Mar\", \"Q1\" is not shown because it is redundant with previous rows. Setting repeat_headings to true would cause \"Q1\" to be repeated for \"Feb\" and \"Mar\". +--------------+ | Q1 | Jan | | | Feb | | | Mar | +--------+-----+ | Q1 Total | +--------------+")
    show_totals: bool | None = Field(None, validation_alias="showTotals", serialization_alias="showTotals", description="True if the pivot table should include the totals for this grouping.")
    sort_order: Literal["SORT_ORDER_UNSPECIFIED", "ASCENDING", "DESCENDING"] | None = Field(None, validation_alias="sortOrder", serialization_alias="sortOrder", description="The order the values in this group should be sorted.")
    source_column_offset: int | None = Field(None, validation_alias="sourceColumnOffset", serialization_alias="sourceColumnOffset", description="The column offset of the source range that this grouping is based on. For example, if the source was `C10:E15`, a `sourceColumnOffset` of `0` means this group refers to column `C`, whereas the offset `1` would refer to column `D`.", json_schema_extra={'format': 'int32'})
    value_bucket: PivotGroupSortValueBucket | None = Field(None, validation_alias="valueBucket", serialization_alias="valueBucket", description="The bucket of the opposite pivot group to sort by. If not specified, sorting is alphabetical by this group's values.")
    value_metadata: list[PivotGroupValueMetadata] | None = Field(None, validation_alias="valueMetadata", serialization_alias="valueMetadata", description="Metadata about values in the grouping.")

class PivotValue(PermissiveModel):
    """The definition of how a value in a pivot table should be calculated."""
    calculated_display_type: Literal["PIVOT_VALUE_CALCULATED_DISPLAY_TYPE_UNSPECIFIED", "PERCENT_OF_ROW_TOTAL", "PERCENT_OF_COLUMN_TOTAL", "PERCENT_OF_GRAND_TOTAL"] | None = Field(None, validation_alias="calculatedDisplayType", serialization_alias="calculatedDisplayType", description="If specified, indicates that pivot values should be displayed as the result of a calculation with another pivot value. For example, if calculated_display_type is specified as PERCENT_OF_GRAND_TOTAL, all the pivot values are displayed as the percentage of the grand total. In the Sheets editor, this is referred to as \"Show As\" in the value section of a pivot table.")
    data_source_column_reference: DataSourceColumnReference | None = Field(None, validation_alias="dataSourceColumnReference", serialization_alias="dataSourceColumnReference", description="The reference to the data source column that this value reads from.")
    formula: str | None = Field(None, description="A custom formula to calculate the value. The formula must start with an `=` character.")
    name: str | None = Field(None, description="A name to use for the value.")
    source_column_offset: int | None = Field(None, validation_alias="sourceColumnOffset", serialization_alias="sourceColumnOffset", description="The column offset of the source range that this value reads from. For example, if the source was `C10:E15`, a `sourceColumnOffset` of `0` means this value refers to column `C`, whereas the offset `1` would refer to column `D`.", json_schema_extra={'format': 'int32'})
    summarize_function: Literal["PIVOT_STANDARD_VALUE_FUNCTION_UNSPECIFIED", "SUM", "COUNTA", "COUNT", "COUNTUNIQUE", "AVERAGE", "MAX", "MIN", "MEDIAN", "PRODUCT", "STDEV", "STDEVP", "VAR", "VARP", "CUSTOM", "NONE"] | None = Field(None, validation_alias="summarizeFunction", serialization_alias="summarizeFunction", description="A function to summarize the value. If formula is set, the only supported values are SUM and CUSTOM. If sourceColumnOffset is set, then `CUSTOM` is not supported.")

class PivotTable(PermissiveModel):
    """A pivot table."""
    columns: list[PivotGroup] | None = Field(None, description="Each column grouping in the pivot table.")
    criteria: dict[str, PivotFilterCriteria] | None = Field(None, description="An optional mapping of filters per source column offset. The filters are applied before aggregating data into the pivot table. The map's key is the column offset of the source range that you want to filter, and the value is the criteria for that column. For example, if the source was `C10:E15`, a key of `0` will have the filter for column `C`, whereas the key `1` is for column `D`. This field is deprecated in favor of filter_specs.")
    data_execution_status: DataExecutionStatus | None = Field(None, validation_alias="dataExecutionStatus", serialization_alias="dataExecutionStatus", description="Output only. The data execution status for data source pivot tables.")
    data_source_id: str | None = Field(None, validation_alias="dataSourceId", serialization_alias="dataSourceId", description="The ID of the data source the pivot table is reading data from.")
    filter_specs: list[PivotFilterSpec] | None = Field(None, validation_alias="filterSpecs", serialization_alias="filterSpecs", description="The filters applied to the source columns before aggregating data for the pivot table. Both criteria and filter_specs are populated in responses. If both fields are specified in an update request, this field takes precedence.")
    rows: list[PivotGroup] | None = Field(None, description="Each row grouping in the pivot table.")
    source: GridRange | None = Field(None, description="The range the pivot table is reading data from.")
    value_layout: Literal["HORIZONTAL", "VERTICAL"] | None = Field(None, validation_alias="valueLayout", serialization_alias="valueLayout", description="Whether values should be listed horizontally (as columns) or vertically (as rows).")
    values: list[PivotValue] | None = Field(None, description="A list of values to include in the pivot table.")

class PointStyle(PermissiveModel):
    """The style of a point on the chart."""
    shape: Literal["POINT_SHAPE_UNSPECIFIED", "CIRCLE", "DIAMOND", "HEXAGON", "PENTAGON", "SQUARE", "STAR", "TRIANGLE", "X_MARK"] | None = Field(None, description="The point shape. If empty or unspecified, a default shape is used.")
    size: float | None = Field(None, description="The point size. If empty, a default size is used.", json_schema_extra={'format': 'double'})

class BasicSeriesDataPointStyleOverride(PermissiveModel):
    """Style override settings for a single series data point."""
    color: Color | None = Field(None, description="Color of the series data point. If empty, the series default is used. Deprecated: Use color_style.")
    color_style: ColorStyle | None = Field(None, validation_alias="colorStyle", serialization_alias="colorStyle", description="Color of the series data point. If empty, the series default is used. If color is also set, this field takes precedence.")
    index: int | None = Field(None, description="The zero-based index of the series data point.", json_schema_extra={'format': 'int32'})
    point_style: PointStyle | None = Field(None, validation_alias="pointStyle", serialization_alias="pointStyle", description="Point style of the series data point. Valid only if the chartType is AREA, LINE, or SCATTER. COMBO charts are also supported if the series chart type is AREA, LINE, or SCATTER. If empty, the series default is used.")

class ProtectedRange(PermissiveModel):
    """A protected range."""
    description: str | None = Field(None, description="The description of this protected range.")
    editors: Editors | None = Field(None, description="The users and groups with edit access to the protected range. This field is only visible to users with edit access to the protected range and the document. Editors are not supported with warning_only protection.")
    named_range_id: str | None = Field(None, validation_alias="namedRangeId", serialization_alias="namedRangeId", description="The named range this protected range is backed by, if any. When writing, only one of range or named_range_id or table_id may be set.")
    protected_range_id: int | None = Field(None, validation_alias="protectedRangeId", serialization_alias="protectedRangeId", description="The ID of the protected range. This field is read-only.", json_schema_extra={'format': 'int32'})
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range that is being protected. The range may be fully unbounded, in which case this is considered a protected sheet. When writing, only one of range or named_range_id or table_id may be set.")
    requesting_user_can_edit: bool | None = Field(None, validation_alias="requestingUserCanEdit", serialization_alias="requestingUserCanEdit", description="True if the user who requested this protected range can edit the protected area. This field is read-only.")
    table_id: str | None = Field(None, validation_alias="tableId", serialization_alias="tableId", description="The table this protected range is backed by, if any. When writing, only one of range or named_range_id or table_id may be set.")
    unprotected_ranges: list[GridRange] | None = Field(None, validation_alias="unprotectedRanges", serialization_alias="unprotectedRanges", description="The list of unprotected ranges within a protected sheet. Unprotected ranges are only supported on protected sheets.")
    warning_only: bool | None = Field(None, validation_alias="warningOnly", serialization_alias="warningOnly", description="True if this protected range will show a warning when editing. Warning-based protection means that every user can edit data in the protected range, except editing will prompt a warning asking the user to confirm the edit. When writing: if this field is true, then editors are ignored. Additionally, if this field is changed from true to false and the `editors` field is not set (nor included in the field mask), then the editors will be set to all the editors in the document.")

class AddProtectedRangeRequest(PermissiveModel):
    """Adds a new protected range."""
    protected_range: ProtectedRange | None = Field(None, validation_alias="protectedRange", serialization_alias="protectedRange", description="The protected range to be added. The protectedRangeId field is optional; if one is not set, an id will be randomly generated. (It is an error to specify the ID of a range that already exists.)")

class RandomizeRangeRequest(PermissiveModel):
    """Randomizes the order of the rows in a range."""
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range to randomize.")

class RefreshDataSourceRequest(PermissiveModel):
    """Refreshes one or multiple data source objects in the spreadsheet by the specified references. The request requires an additional `bigquery.readonly` OAuth scope if you are refreshing a BigQuery data source. If there are multiple refresh requests referencing the same data source objects in one batch, only the last refresh request is processed, and all those requests will have the same response accordingly."""
    data_source_id: str | None = Field(None, validation_alias="dataSourceId", serialization_alias="dataSourceId", description="Reference to a DataSource. If specified, refreshes all associated data source objects for the data source.")
    force: bool | None = Field(None, description="Refreshes the data source objects regardless of the current state. If not set and a referenced data source object was in error state, the refresh will fail immediately.")
    is_all: bool | None = Field(None, validation_alias="isAll", serialization_alias="isAll", description="Refreshes all existing data source objects in the spreadsheet.")
    references: DataSourceObjectReferences | None = Field(None, description="References to data source objects to refresh.")

class RichLinkProperties(PermissiveModel):
    """Properties of a link to a Google resource (such as a file in Drive, a YouTube video, a Maps address, or a Calendar event). Only Drive files can be written as chips. All other rich link types are read only. URIs cannot exceed 2000 bytes when writing. NOTE: Writing Drive file chips requires at least one of the `drive.file`, `drive.readonly`, or `drive` OAuth scopes."""
    mime_type: str | None = Field(None, validation_alias="mimeType", serialization_alias="mimeType", description="Output only. The [MIME type](https://developers.google.com/drive/api/v3/mime-types) of the link, if there's one (for example, when it's a file in Drive).")
    uri: str | None = Field(None, description="Required. The URI to the link. This is always present.")

class Chip(PermissiveModel):
    """The Smart Chip."""
    person_properties: PersonProperties | None = Field(None, validation_alias="personProperties", serialization_alias="personProperties", description="Properties of a linked person.")
    rich_link_properties: RichLinkProperties | None = Field(None, validation_alias="richLinkProperties", serialization_alias="richLinkProperties", description="Properties of a rich link.")

class ChipRun(PermissiveModel):
    """The run of a chip. The chip continues until the start index of the next run."""
    chip: Chip | None = Field(None, description="Optional. The chip of this run.")
    start_index: int | None = Field(None, validation_alias="startIndex", serialization_alias="startIndex", description="Required. The zero-based character index where this run starts, in UTF-16 code units.", json_schema_extra={'format': 'int32'})

class SetDataValidationRequest(PermissiveModel):
    """Sets a data validation rule to every cell in the range. To clear validation in a range, call this with no rule specified."""
    filtered_rows_included: bool | None = Field(None, validation_alias="filteredRowsIncluded", serialization_alias="filteredRowsIncluded", description="Optional. If true, the data validation rule will be applied to the filtered rows as well.")
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range the data validation rule should apply to.")
    rule: DataValidationRule | None = Field(None, description="The data validation rule to set on each cell in the range, or empty to clear the data validation in the range.")

class SheetProperties(PermissiveModel):
    """Properties of a sheet."""
    data_source_sheet_properties: DataSourceSheetProperties | None = Field(None, validation_alias="dataSourceSheetProperties", serialization_alias="dataSourceSheetProperties", description="Output only. If present, the field contains DATA_SOURCE sheet specific properties.")
    grid_properties: GridProperties | None = Field(None, validation_alias="gridProperties", serialization_alias="gridProperties", description="Additional properties of the sheet if this sheet is a grid. (If the sheet is an object sheet, containing a chart or image, then this field will be absent.) When writing it is an error to set any grid properties on non-grid sheets. If this sheet is a DATA_SOURCE sheet, this field is output only but contains the properties that reflect how a data source sheet is rendered in the UI, e.g. row_count.")
    hidden: bool | None = Field(None, description="True if the sheet is hidden in the UI, false if it's visible.")
    index: int | None = Field(None, description="The index of the sheet within the spreadsheet. When adding or updating sheet properties, if this field is excluded then the sheet is added or moved to the end of the sheet list. When updating sheet indices or inserting sheets, movement is considered in \"before the move\" indexes. For example, if there were three sheets (S1, S2, S3) in order to move S1 ahead of S2 the index would have to be set to 2. A sheet index update request is ignored if the requested index is identical to the sheets current index or if the requested new index is equal to the current sheet index + 1.", json_schema_extra={'format': 'int32'})
    right_to_left: bool | None = Field(None, validation_alias="rightToLeft", serialization_alias="rightToLeft", description="True if the sheet is an RTL sheet instead of an LTR sheet.")
    sheet_id: int | None = Field(None, validation_alias="sheetId", serialization_alias="sheetId", description="The ID of the sheet. Must be non-negative. This field cannot be changed once set.", json_schema_extra={'format': 'int32'})
    sheet_type: Literal["SHEET_TYPE_UNSPECIFIED", "GRID", "OBJECT", "DATA_SOURCE"] | None = Field(None, validation_alias="sheetType", serialization_alias="sheetType", description="The type of sheet. Defaults to GRID. This field cannot be changed once set.")
    tab_color: Color | None = Field(None, validation_alias="tabColor", serialization_alias="tabColor", description="The color of the tab in the UI. Deprecated: Use tab_color_style.")
    tab_color_style: ColorStyle | None = Field(None, validation_alias="tabColorStyle", serialization_alias="tabColorStyle", description="The color of the tab in the UI. If tab_color is also set, this field takes precedence.")
    title: str | None = Field(None, description="The name of the sheet.")

class AddSheetRequest(PermissiveModel):
    """Adds a new sheet. When a sheet is added at a given index, all subsequent sheets' indexes are incremented. To add an object sheet, use AddChartRequest instead and specify EmbeddedObjectPosition.sheetId or EmbeddedObjectPosition.newSheet."""
    properties: SheetProperties | None = Field(None, description="The properties the new sheet should have. All properties are optional. The sheetId field is optional; if one is not set, an id will be randomly generated. (It is an error to specify the ID of a sheet that already exists.)")

class SortSpec(PermissiveModel):
    """A sort order associated with a specific column or row."""
    background_color: Color | None = Field(None, validation_alias="backgroundColor", serialization_alias="backgroundColor", description="The background fill color to sort by; cells with this fill color are sorted to the top. Mutually exclusive with foreground_color. Deprecated: Use background_color_style.")
    background_color_style: ColorStyle | None = Field(None, validation_alias="backgroundColorStyle", serialization_alias="backgroundColorStyle", description="The background fill color to sort by; cells with this fill color are sorted to the top. Mutually exclusive with foreground_color, and must be an RGB-type color. If background_color is also set, this field takes precedence.")
    data_source_column_reference: DataSourceColumnReference | None = Field(None, validation_alias="dataSourceColumnReference", serialization_alias="dataSourceColumnReference", description="Reference to a data source column.")
    dimension_index: int | None = Field(None, validation_alias="dimensionIndex", serialization_alias="dimensionIndex", description="The dimension the sort should be applied to.", json_schema_extra={'format': 'int32'})
    foreground_color: Color | None = Field(None, validation_alias="foregroundColor", serialization_alias="foregroundColor", description="The foreground color to sort by; cells with this foreground color are sorted to the top. Mutually exclusive with background_color. Deprecated: Use foreground_color_style.")
    foreground_color_style: ColorStyle | None = Field(None, validation_alias="foregroundColorStyle", serialization_alias="foregroundColorStyle", description="The foreground color to sort by; cells with this foreground color are sorted to the top. Mutually exclusive with background_color, and must be an RGB-type color. If foreground_color is also set, this field takes precedence.")
    sort_order: Literal["SORT_ORDER_UNSPECIFIED", "ASCENDING", "DESCENDING"] | None = Field(None, validation_alias="sortOrder", serialization_alias="sortOrder", description="The order data should be sorted.")

class BasicFilter(PermissiveModel):
    """The default filter associated with a sheet. For more information, see [Manage data visibility with filters](https://developers.google.com/workspace/sheets/api/guides/filters)."""
    criteria: dict[str, FilterCriteria] | None = Field(None, description="The criteria for showing/hiding values per column. The map's key is the column index, and the value is the criteria for that column. This field is deprecated in favor of filter_specs.")
    filter_specs: list[FilterSpec] | None = Field(None, validation_alias="filterSpecs", serialization_alias="filterSpecs", description="The filter criteria per column. Both criteria and filter_specs are populated in responses. If both fields are specified in an update request, this field takes precedence.")
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range the filter covers.")
    sort_specs: list[SortSpec] | None = Field(None, validation_alias="sortSpecs", serialization_alias="sortSpecs", description="The sort order per column. Later specifications are used when values are equal in the earlier specifications.")
    table_id: str | None = Field(None, validation_alias="tableId", serialization_alias="tableId", description="The table this filter is backed by, if any. When writing, only one of range or table_id may be set.")

class DataSourceTable(PermissiveModel):
    """A data source table, which allows the user to import a static table of data from the DataSource into Sheets. This is also known as "Extract" in the Sheets editor."""
    columns: list[DataSourceColumnReference] | None = Field(None, description="Columns selected for the data source table. The column_selection_type must be SELECTED.")
    column_selection_type: Literal["DATA_SOURCE_TABLE_COLUMN_SELECTION_TYPE_UNSPECIFIED", "SELECTED", "SYNC_ALL"] | None = Field(None, validation_alias="columnSelectionType", serialization_alias="columnSelectionType", description="The type to select columns for the data source table. Defaults to SELECTED.")
    data_execution_status: DataExecutionStatus | None = Field(None, validation_alias="dataExecutionStatus", serialization_alias="dataExecutionStatus", description="Output only. The data execution status.")
    data_source_id: str | None = Field(None, validation_alias="dataSourceId", serialization_alias="dataSourceId", description="The ID of the data source the data source table is associated with.")
    filter_specs: list[FilterSpec] | None = Field(None, validation_alias="filterSpecs", serialization_alias="filterSpecs", description="Filter specifications in the data source table.")
    row_limit: int | None = Field(None, validation_alias="rowLimit", serialization_alias="rowLimit", description="The limit of rows to return. If not set, a default limit is applied. Please refer to the Sheets editor for the default and max limit.", json_schema_extra={'format': 'int32'})
    sort_specs: list[SortSpec] | None = Field(None, validation_alias="sortSpecs", serialization_alias="sortSpecs", description="Sort specifications in the data source table. The result of the data source table is sorted based on the sort specifications in order.")

class FilterView(PermissiveModel):
    """A filter view. For more information, see [Manage data visibility with filters](https://developers.google.com/workspace/sheets/api/guides/filters)."""
    criteria: dict[str, FilterCriteria] | None = Field(None, description="The criteria for showing/hiding values per column. The map's key is the column index, and the value is the criteria for that column. This field is deprecated in favor of filter_specs.")
    filter_specs: list[FilterSpec] | None = Field(None, validation_alias="filterSpecs", serialization_alias="filterSpecs", description="The filter criteria for showing or hiding values per column. Both criteria and filter_specs are populated in responses. If both fields are specified in an update request, this field takes precedence.")
    filter_view_id: int | None = Field(None, validation_alias="filterViewId", serialization_alias="filterViewId", description="The ID of the filter view.", json_schema_extra={'format': 'int32'})
    named_range_id: str | None = Field(None, validation_alias="namedRangeId", serialization_alias="namedRangeId", description="The named range this filter view is backed by, if any. When writing, only one of range, named_range_id, or table_id may be set.")
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range this filter view covers. When writing, only one of range, named_range_id, or table_id may be set.")
    sort_specs: list[SortSpec] | None = Field(None, validation_alias="sortSpecs", serialization_alias="sortSpecs", description="The sort order per column. Later specifications are used when values are equal in the earlier specifications.")
    table_id: str | None = Field(None, validation_alias="tableId", serialization_alias="tableId", description="The table this filter view is backed by, if any. When writing, only one of range, named_range_id, or table_id may be set.")
    title: str | None = Field(None, description="The name of the filter view.")

class AddFilterViewRequest(PermissiveModel):
    """Adds a filter view."""
    filter_: FilterView | None = Field(None, validation_alias="filter", serialization_alias="filter", description="The filter to add. The filterViewId field is optional. If one is not set, an ID will be randomly generated. (It is an error to specify the ID of a filter that already exists.)")

class SetBasicFilterRequest(PermissiveModel):
    """Sets the basic filter associated with a sheet."""
    filter_: BasicFilter | None = Field(None, validation_alias="filter", serialization_alias="filter", description="The filter to set.")

class SortRangeRequest(PermissiveModel):
    """Sorts data in rows based on a sort order per column."""
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range to sort.")
    sort_specs: list[SortSpec] | None = Field(None, validation_alias="sortSpecs", serialization_alias="sortSpecs", description="The sort order per column. Later specifications are used when values are equal in the earlier specifications.")

class SourceAndDestination(PermissiveModel):
    """A combination of a source range and how to extend that source."""
    dimension: Literal["DIMENSION_UNSPECIFIED", "ROWS", "COLUMNS"] | None = Field(None, description="The dimension that data should be filled into.")
    fill_length: int | None = Field(None, validation_alias="fillLength", serialization_alias="fillLength", description="The number of rows or columns that data should be filled into. Positive numbers expand beyond the last row or last column of the source. Negative numbers expand before the first row or first column of the source.", json_schema_extra={'format': 'int32'})
    source: GridRange | None = Field(None, description="The location of the data to use as the source of the autofill.")

class AutoFillRequest(PermissiveModel):
    """Fills in more data based on existing data."""
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range to autofill. This will examine the range and detect the location that has data and automatically fill that data in to the rest of the range.")
    source_and_destination: SourceAndDestination | None = Field(None, validation_alias="sourceAndDestination", serialization_alias="sourceAndDestination", description="The source and destination areas to autofill. This explicitly lists the source of the autofill and where to extend that data.")
    use_alternate_series: bool | None = Field(None, validation_alias="useAlternateSeries", serialization_alias="useAlternateSeries", description="True if we should generate data with the \"alternate\" series. This differs based on the type and amount of source data.")

class TableColumnDataValidationRule(PermissiveModel):
    """A data validation rule for a column in a table."""
    condition: BooleanCondition | None = Field(None, description="The condition that data in the cell must match. Valid only if the [BooleanCondition.type] is ONE_OF_LIST.")

class TableColumnProperties(PermissiveModel):
    """The table column."""
    column_index: int | None = Field(None, validation_alias="columnIndex", serialization_alias="columnIndex", description="The 0-based column index. This index is relative to its position in the table and is not necessarily the same as the column index in the sheet.", json_schema_extra={'format': 'int32'})
    column_name: str | None = Field(None, validation_alias="columnName", serialization_alias="columnName", description="The column name.")
    column_type: Literal["COLUMN_TYPE_UNSPECIFIED", "DOUBLE", "CURRENCY", "PERCENT", "DATE", "TIME", "DATE_TIME", "TEXT", "BOOLEAN", "DROPDOWN", "FILES_CHIP", "PEOPLE_CHIP", "FINANCE_CHIP", "PLACE_CHIP", "RATINGS_CHIP"] | None = Field(None, validation_alias="columnType", serialization_alias="columnType", description="The column type.")
    data_validation_rule: TableColumnDataValidationRule | None = Field(None, validation_alias="dataValidationRule", serialization_alias="dataValidationRule", description="The column data validation rule. Only set for dropdown column type.")

class TableRowsProperties(PermissiveModel):
    """The table row properties."""
    first_band_color_style: ColorStyle | None = Field(None, validation_alias="firstBandColorStyle", serialization_alias="firstBandColorStyle", description="The first color that is alternating. If this field is set, the first banded row is filled with the specified color. Otherwise, the first banded row is filled with a default color.")
    footer_color_style: ColorStyle | None = Field(None, validation_alias="footerColorStyle", serialization_alias="footerColorStyle", description="The color of the last row. If this field is not set a footer is not added, the last row is filled with either first_band_color_style or second_band_color_style, depending on the color of the previous row. If updating an existing table without a footer to have a footer, the range will be expanded by 1 row. If updating an existing table with a footer and removing a footer, the range will be shrunk by 1 row.")
    header_color_style: ColorStyle | None = Field(None, validation_alias="headerColorStyle", serialization_alias="headerColorStyle", description="The color of the header row. If this field is set, the header row is filled with the specified color. Otherwise, the header row is filled with a default color.")
    second_band_color_style: ColorStyle | None = Field(None, validation_alias="secondBandColorStyle", serialization_alias="secondBandColorStyle", description="The second color that is alternating. If this field is set, the second banded row is filled with the specified color. Otherwise, the second banded row is filled with a default color.")

class Table(PermissiveModel):
    """A table."""
    column_properties: list[TableColumnProperties] | None = Field(None, validation_alias="columnProperties", serialization_alias="columnProperties", description="The table column properties.")
    name: str | None = Field(None, description="The table name. This is unique to all tables in the same spreadsheet.")
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The table range.")
    rows_properties: TableRowsProperties | None = Field(None, validation_alias="rowsProperties", serialization_alias="rowsProperties", description="The table rows properties.")
    table_id: str | None = Field(None, validation_alias="tableId", serialization_alias="tableId", description="The id of the table.")

class AddTableRequest(PermissiveModel):
    """Adds a new table to the spreadsheet."""
    table: Table | None = Field(None, description="Required. The table to add.")

class TextFormat(PermissiveModel):
    """The format of a run of text in a cell. Absent values indicate that the field isn't specified."""
    bold: bool | None = Field(None, description="True if the text is bold.")
    font_family: str | None = Field(None, validation_alias="fontFamily", serialization_alias="fontFamily", description="The font family.")
    font_size: int | None = Field(None, validation_alias="fontSize", serialization_alias="fontSize", description="The size of the font.", json_schema_extra={'format': 'int32'})
    foreground_color: Color | None = Field(None, validation_alias="foregroundColor", serialization_alias="foregroundColor", description="The foreground color of the text. Deprecated: Use foreground_color_style.")
    foreground_color_style: ColorStyle | None = Field(None, validation_alias="foregroundColorStyle", serialization_alias="foregroundColorStyle", description="The foreground color of the text. If foreground_color is also set, this field takes precedence.")
    italic: bool | None = Field(None, description="True if the text is italicized.")
    link: Link | None = Field(None, description="The link destination of the text, if any. Setting the link field in a TextFormatRun will clear the cell's existing links or a cell-level link set in the same request. When a link is set, the text foreground color will be set to the default link color and the text will be underlined. If these fields are modified in the same request, those values will be used instead of the link defaults.")
    strikethrough: bool | None = Field(None, description="True if the text has a strikethrough.")
    underline: bool | None = Field(None, description="True if the text is underlined.")

class BubbleChartSpec(PermissiveModel):
    """A bubble chart."""
    bubble_border_color: Color | None = Field(None, validation_alias="bubbleBorderColor", serialization_alias="bubbleBorderColor", description="The bubble border color. Deprecated: Use bubble_border_color_style.")
    bubble_border_color_style: ColorStyle | None = Field(None, validation_alias="bubbleBorderColorStyle", serialization_alias="bubbleBorderColorStyle", description="The bubble border color. If bubble_border_color is also set, this field takes precedence.")
    bubble_labels: ChartData | None = Field(None, validation_alias="bubbleLabels", serialization_alias="bubbleLabels", description="The data containing the bubble labels. These do not need to be unique.")
    bubble_max_radius_size: int | None = Field(None, validation_alias="bubbleMaxRadiusSize", serialization_alias="bubbleMaxRadiusSize", description="The max radius size of the bubbles, in pixels. If specified, the field must be a positive value.", json_schema_extra={'format': 'int32'})
    bubble_min_radius_size: int | None = Field(None, validation_alias="bubbleMinRadiusSize", serialization_alias="bubbleMinRadiusSize", description="The minimum radius size of the bubbles, in pixels. If specific, the field must be a positive value.", json_schema_extra={'format': 'int32'})
    bubble_opacity: float | None = Field(None, validation_alias="bubbleOpacity", serialization_alias="bubbleOpacity", description="The opacity of the bubbles between 0 and 1.0. 0 is fully transparent and 1 is fully opaque.", json_schema_extra={'format': 'float'})
    bubble_sizes: ChartData | None = Field(None, validation_alias="bubbleSizes", serialization_alias="bubbleSizes", description="The data containing the bubble sizes. Bubble sizes are used to draw the bubbles at different sizes relative to each other. If specified, group_ids must also be specified. This field is optional.")
    bubble_text_style: TextFormat | None = Field(None, validation_alias="bubbleTextStyle", serialization_alias="bubbleTextStyle", description="The format of the text inside the bubbles. Strikethrough, underline, and link are not supported.")
    domain: ChartData | None = Field(None, description="The data containing the bubble x-values. These values locate the bubbles in the chart horizontally.")
    group_ids: ChartData | None = Field(None, validation_alias="groupIds", serialization_alias="groupIds", description="The data containing the bubble group IDs. All bubbles with the same group ID are drawn in the same color. If bubble_sizes is specified then this field must also be specified but may contain blank values. This field is optional.")
    legend_position: Literal["BUBBLE_CHART_LEGEND_POSITION_UNSPECIFIED", "BOTTOM_LEGEND", "LEFT_LEGEND", "RIGHT_LEGEND", "TOP_LEGEND", "NO_LEGEND", "INSIDE_LEGEND"] | None = Field(None, validation_alias="legendPosition", serialization_alias="legendPosition", description="Where the legend of the chart should be drawn.")
    series: ChartData | None = Field(None, description="The data containing the bubble y-values. These values locate the bubbles in the chart vertically.")

class DataLabel(PermissiveModel):
    """Settings for one set of data labels. Data labels are annotations that appear next to a set of data, such as the points on a line chart, and provide additional information about what the data represents, such as a text representation of the value behind that point on the graph."""
    custom_label_data: ChartData | None = Field(None, validation_alias="customLabelData", serialization_alias="customLabelData", description="Data to use for custom labels. Only used if type is set to CUSTOM. This data must be the same length as the series or other element this data label is applied to. In addition, if the series is split into multiple source ranges, this source data must come from the next column in the source data. For example, if the series is B2:B4,E6:E8 then this data must come from C2:C4,F6:F8.")
    placement: Literal["DATA_LABEL_PLACEMENT_UNSPECIFIED", "CENTER", "LEFT", "RIGHT", "ABOVE", "BELOW", "INSIDE_END", "INSIDE_BASE", "OUTSIDE_END"] | None = Field(None, description="The placement of the data label relative to the labeled data.")
    text_format: TextFormat | None = Field(None, validation_alias="textFormat", serialization_alias="textFormat", description="The text format used for the data label. The link field is not supported.")
    type_: Literal["DATA_LABEL_TYPE_UNSPECIFIED", "NONE", "DATA", "CUSTOM"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the data label.")

class BasicChartSeries(PermissiveModel):
    """A single series of data in a chart. For example, if charting stock prices over time, multiple series may exist, one for the "Open Price", "High Price", "Low Price" and "Close Price"."""
    color: Color | None = Field(None, description="The color for elements (such as bars, lines, and points) associated with this series. If empty, a default color is used. Deprecated: Use color_style.")
    color_style: ColorStyle | None = Field(None, validation_alias="colorStyle", serialization_alias="colorStyle", description="The color for elements (such as bars, lines, and points) associated with this series. If empty, a default color is used. If color is also set, this field takes precedence.")
    data_label: DataLabel | None = Field(None, validation_alias="dataLabel", serialization_alias="dataLabel", description="Information about the data labels for this series.")
    line_style: LineStyle | None = Field(None, validation_alias="lineStyle", serialization_alias="lineStyle", description="The line style of this series. Valid only if the chartType is AREA, LINE, or SCATTER. COMBO charts are also supported if the series chart type is AREA or LINE.")
    point_style: PointStyle | None = Field(None, validation_alias="pointStyle", serialization_alias="pointStyle", description="The style for points associated with this series. Valid only if the chartType is AREA, LINE, or SCATTER. COMBO charts are also supported if the series chart type is AREA, LINE, or SCATTER. If empty, a default point style is used.")
    series: ChartData | None = Field(None, description="The data being visualized in this chart series.")
    style_overrides: list[BasicSeriesDataPointStyleOverride] | None = Field(None, validation_alias="styleOverrides", serialization_alias="styleOverrides", description="Style override settings for series data points.")
    target_axis: Literal["BASIC_CHART_AXIS_POSITION_UNSPECIFIED", "BOTTOM_AXIS", "LEFT_AXIS", "RIGHT_AXIS"] | None = Field(None, validation_alias="targetAxis", serialization_alias="targetAxis", description="The minor axis that will specify the range of values for this series. For example, if charting stocks over time, the \"Volume\" series may want to be pinned to the right with the prices pinned to the left, because the scale of trading volume is different than the scale of prices. It is an error to specify an axis that isn't a valid minor axis for the chart's type.")
    type_: Literal["BASIC_CHART_TYPE_UNSPECIFIED", "BAR", "LINE", "AREA", "COLUMN", "SCATTER", "COMBO", "STEPPED_AREA"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of this series. Valid only if the chartType is COMBO. Different types will change the way the series is visualized. Only LINE, AREA, and COLUMN are supported.")

class SlicerSpec(PermissiveModel):
    """The specifications of a slicer."""
    apply_to_pivot_tables: bool | None = Field(None, validation_alias="applyToPivotTables", serialization_alias="applyToPivotTables", description="True if the filter should apply to pivot tables. If not set, default to `True`.")
    background_color: Color | None = Field(None, validation_alias="backgroundColor", serialization_alias="backgroundColor", description="The background color of the slicer. Deprecated: Use background_color_style.")
    background_color_style: ColorStyle | None = Field(None, validation_alias="backgroundColorStyle", serialization_alias="backgroundColorStyle", description="The background color of the slicer. If background_color is also set, this field takes precedence.")
    column_index: int | None = Field(None, validation_alias="columnIndex", serialization_alias="columnIndex", description="The zero-based column index in the data table on which the filter is applied to.", json_schema_extra={'format': 'int32'})
    data_range: GridRange | None = Field(None, validation_alias="dataRange", serialization_alias="dataRange", description="The data range of the slicer.")
    filter_criteria: FilterCriteria | None = Field(None, validation_alias="filterCriteria", serialization_alias="filterCriteria", description="The filtering criteria of the slicer.")
    horizontal_alignment: Literal["HORIZONTAL_ALIGN_UNSPECIFIED", "LEFT", "CENTER", "RIGHT"] | None = Field(None, validation_alias="horizontalAlignment", serialization_alias="horizontalAlignment", description="The horizontal alignment of title in the slicer. If unspecified, defaults to `LEFT`")
    text_format: TextFormat | None = Field(None, validation_alias="textFormat", serialization_alias="textFormat", description="The text format of title in the slicer. The link field is not supported.")
    title: str | None = Field(None, description="The title of the slicer.")

class Slicer(PermissiveModel):
    """A slicer in a sheet."""
    position: EmbeddedObjectPosition | None = Field(None, description="The position of the slicer. Note that slicer can be positioned only on existing sheet. Also, width and height of slicer can be automatically adjusted to keep it within permitted limits.")
    slicer_id: int | None = Field(None, validation_alias="slicerId", serialization_alias="slicerId", description="The ID of the slicer.", json_schema_extra={'format': 'int32'})
    spec: SlicerSpec | None = Field(None, description="The specification of the slicer.")

class AddSlicerRequest(PermissiveModel):
    """Adds a slicer to a sheet in the spreadsheet."""
    slicer: Slicer | None = Field(None, description="The slicer that should be added to the spreadsheet, including the position where it should be placed. The slicerId field is optional; if one is not set, an id will be randomly generated. (It is an error to specify the ID of a slicer that already exists.)")

class TextFormatRun(PermissiveModel):
    """A run of a text format. The format of this run continues until the start index of the next run. When updating, all fields must be set."""
    format_: TextFormat | None = Field(None, validation_alias="format", serialization_alias="format", description="The format of this run. Absent values inherit the cell's format.")
    start_index: int | None = Field(None, validation_alias="startIndex", serialization_alias="startIndex", description="The zero-based character index where this run starts, in UTF-16 code units.", json_schema_extra={'format': 'int32'})

class TextPosition(PermissiveModel):
    """Position settings for text."""
    horizontal_alignment: Literal["HORIZONTAL_ALIGN_UNSPECIFIED", "LEFT", "CENTER", "RIGHT"] | None = Field(None, validation_alias="horizontalAlignment", serialization_alias="horizontalAlignment", description="Horizontal alignment setting for the piece of text.")

class BaselineValueFormat(PermissiveModel):
    """Formatting options for baseline value."""
    comparison_type: Literal["COMPARISON_TYPE_UNDEFINED", "ABSOLUTE_DIFFERENCE", "PERCENTAGE_DIFFERENCE"] | None = Field(None, validation_alias="comparisonType", serialization_alias="comparisonType", description="The comparison type of key value with baseline value.")
    description: str | None = Field(None, description="Description which is appended after the baseline value. This field is optional.")
    negative_color: Color | None = Field(None, validation_alias="negativeColor", serialization_alias="negativeColor", description="Color to be used, in case baseline value represents a negative change for key value. This field is optional. Deprecated: Use negative_color_style.")
    negative_color_style: ColorStyle | None = Field(None, validation_alias="negativeColorStyle", serialization_alias="negativeColorStyle", description="Color to be used, in case baseline value represents a negative change for key value. This field is optional. If negative_color is also set, this field takes precedence.")
    position: TextPosition | None = Field(None, description="Specifies the horizontal text positioning of baseline value. This field is optional. If not specified, default positioning is used.")
    positive_color: Color | None = Field(None, validation_alias="positiveColor", serialization_alias="positiveColor", description="Color to be used, in case baseline value represents a positive change for key value. This field is optional. Deprecated: Use positive_color_style.")
    positive_color_style: ColorStyle | None = Field(None, validation_alias="positiveColorStyle", serialization_alias="positiveColorStyle", description="Color to be used, in case baseline value represents a positive change for key value. This field is optional. If positive_color is also set, this field takes precedence.")
    text_format: TextFormat | None = Field(None, validation_alias="textFormat", serialization_alias="textFormat", description="Text formatting options for baseline value. The link field is not supported.")

class BasicChartAxis(PermissiveModel):
    """An axis of the chart. A chart may not have more than one axis per axis position."""
    format_: TextFormat | None = Field(None, validation_alias="format", serialization_alias="format", description="The format of the title. Only valid if the axis is not associated with the domain. The link field is not supported.")
    position: Literal["BASIC_CHART_AXIS_POSITION_UNSPECIFIED", "BOTTOM_AXIS", "LEFT_AXIS", "RIGHT_AXIS"] | None = Field(None, description="The position of this axis.")
    title: str | None = Field(None, description="The title of this axis. If set, this overrides any title inferred from headers of the data.")
    title_text_position: TextPosition | None = Field(None, validation_alias="titleTextPosition", serialization_alias="titleTextPosition", description="The axis title text position.")
    view_window_options: ChartAxisViewWindowOptions | None = Field(None, validation_alias="viewWindowOptions", serialization_alias="viewWindowOptions", description="The view window options for this axis.")

class BasicChartSpec(PermissiveModel):
    """The specification for a basic chart. See BasicChartType for the list of charts this supports."""
    axis: list[BasicChartAxis] | None = Field(None, description="The axis on the chart.")
    chart_type: Literal["BASIC_CHART_TYPE_UNSPECIFIED", "BAR", "LINE", "AREA", "COLUMN", "SCATTER", "COMBO", "STEPPED_AREA"] | None = Field(None, validation_alias="chartType", serialization_alias="chartType", description="The type of the chart.")
    compare_mode: Literal["BASIC_CHART_COMPARE_MODE_UNSPECIFIED", "DATUM", "CATEGORY"] | None = Field(None, validation_alias="compareMode", serialization_alias="compareMode", description="The behavior of tooltips and data highlighting when hovering on data and chart area.")
    domains: list[BasicChartDomain] | None = Field(None, description="The domain of data this is charting. Only a single domain is supported.")
    header_count: int | None = Field(None, validation_alias="headerCount", serialization_alias="headerCount", description="The number of rows or columns in the data that are \"headers\". If not set, Google Sheets will guess how many rows are headers based on the data. (Note that BasicChartAxis.title may override the axis title inferred from the header values.)", json_schema_extra={'format': 'int32'})
    interpolate_nulls: bool | None = Field(None, validation_alias="interpolateNulls", serialization_alias="interpolateNulls", description="If some values in a series are missing, gaps may appear in the chart (e.g, segments of lines in a line chart will be missing). To eliminate these gaps set this to true. Applies to Line, Area, and Combo charts.")
    legend_position: Literal["BASIC_CHART_LEGEND_POSITION_UNSPECIFIED", "BOTTOM_LEGEND", "LEFT_LEGEND", "RIGHT_LEGEND", "TOP_LEGEND", "NO_LEGEND"] | None = Field(None, validation_alias="legendPosition", serialization_alias="legendPosition", description="The position of the chart legend.")
    line_smoothing: bool | None = Field(None, validation_alias="lineSmoothing", serialization_alias="lineSmoothing", description="Gets whether all lines should be rendered smooth or straight by default. Applies to Line charts.")
    series: list[BasicChartSeries] | None = Field(None, description="The data this chart is visualizing.")
    stacked_type: Literal["BASIC_CHART_STACKED_TYPE_UNSPECIFIED", "NOT_STACKED", "STACKED", "PERCENT_STACKED"] | None = Field(None, validation_alias="stackedType", serialization_alias="stackedType", description="The stacked type for charts that support vertical stacking. Applies to Area, Bar, Column, Combo, and Stepped Area charts.")
    three_dimensional: bool | None = Field(None, validation_alias="threeDimensional", serialization_alias="threeDimensional", description="True to make the chart 3D. Applies to Bar and Column charts.")
    total_data_label: DataLabel | None = Field(None, validation_alias="totalDataLabel", serialization_alias="totalDataLabel", description="Controls whether to display additional data labels on stacked charts which sum the total value of all stacked values at each value along the domain axis. These data labels can only be set when chart_type is one of AREA, BAR, COLUMN, COMBO or STEPPED_AREA and stacked_type is either STACKED or PERCENT_STACKED. In addition, for COMBO, this will only be supported if there is only one type of stackable series type or one type has more series than the others and each of the other types have no more than one series. For example, if a chart has two stacked bar series and one area series, the total data labels will be supported. If it has three bar series and two area series, total data labels are not allowed. Neither CUSTOM nor placement can be set on the total_data_label.")

class KeyValueFormat(PermissiveModel):
    """Formatting options for key value."""
    position: TextPosition | None = Field(None, description="Specifies the horizontal text positioning of key value. This field is optional. If not specified, default positioning is used.")
    text_format: TextFormat | None = Field(None, validation_alias="textFormat", serialization_alias="textFormat", description="Text formatting options for key value. The link field is not supported.")

class ScorecardChartSpec(PermissiveModel):
    """A scorecard chart. Scorecard charts are used to highlight key performance indicators, known as KPIs, on the spreadsheet. A scorecard chart can represent things like total sales, average cost, or a top selling item. You can specify a single data value, or aggregate over a range of data. Percentage or absolute difference from a baseline value can be highlighted, like changes over time."""
    aggregate_type: Literal["CHART_AGGREGATE_TYPE_UNSPECIFIED", "AVERAGE", "COUNT", "MAX", "MEDIAN", "MIN", "SUM"] | None = Field(None, validation_alias="aggregateType", serialization_alias="aggregateType", description="The aggregation type for key and baseline chart data in scorecard chart. This field is not supported for data source charts. Use the ChartData.aggregateType field of the key_value_data or baseline_value_data instead for data source charts. This field is optional.")
    baseline_value_data: ChartData | None = Field(None, validation_alias="baselineValueData", serialization_alias="baselineValueData", description="The data for scorecard baseline value. This field is optional.")
    baseline_value_format: BaselineValueFormat | None = Field(None, validation_alias="baselineValueFormat", serialization_alias="baselineValueFormat", description="Formatting options for baseline value. This field is needed only if baseline_value_data is specified.")
    custom_format_options: ChartCustomNumberFormatOptions | None = Field(None, validation_alias="customFormatOptions", serialization_alias="customFormatOptions", description="Custom formatting options for numeric key/baseline values in scorecard chart. This field is used only when number_format_source is set to CUSTOM. This field is optional.")
    key_value_data: ChartData | None = Field(None, validation_alias="keyValueData", serialization_alias="keyValueData", description="The data for scorecard key value.")
    key_value_format: KeyValueFormat | None = Field(None, validation_alias="keyValueFormat", serialization_alias="keyValueFormat", description="Formatting options for key value.")
    number_format_source: Literal["CHART_NUMBER_FORMAT_SOURCE_UNDEFINED", "FROM_DATA", "CUSTOM"] | None = Field(None, validation_alias="numberFormatSource", serialization_alias="numberFormatSource", description="The number format source used in the scorecard chart. This field is optional.")
    scale_factor: float | None = Field(None, validation_alias="scaleFactor", serialization_alias="scaleFactor", description="Value to scale scorecard key and baseline value. For example, a factor of 10 can be used to divide all values in the chart by 10. This field is optional.", json_schema_extra={'format': 'double'})

class TextRotation(PermissiveModel):
    """The rotation applied to text in a cell."""
    angle: int | None = Field(None, description="The angle between the standard orientation and the desired orientation. Measured in degrees. Valid values are between -90 and 90. Positive angles are angled upwards, negative are angled downwards. Note: For LTR text direction positive angles are in the counterclockwise direction, whereas for RTL they are in the clockwise direction", json_schema_extra={'format': 'int32'})
    vertical: bool | None = Field(None, description="If true, text reads top to bottom, but the orientation of individual characters is unchanged. For example: | V | | e | | r | | t | | i | | c | | a | | l |")

class CellFormat(PermissiveModel):
    """The format of a cell."""
    background_color: Color | None = Field(None, validation_alias="backgroundColor", serialization_alias="backgroundColor", description="The background color of the cell. Deprecated: Use background_color_style.")
    background_color_style: ColorStyle | None = Field(None, validation_alias="backgroundColorStyle", serialization_alias="backgroundColorStyle", description="The background color of the cell. If background_color is also set, this field takes precedence.")
    borders: Borders | None = Field(None, description="The borders of the cell.")
    horizontal_alignment: Literal["HORIZONTAL_ALIGN_UNSPECIFIED", "LEFT", "CENTER", "RIGHT"] | None = Field(None, validation_alias="horizontalAlignment", serialization_alias="horizontalAlignment", description="The horizontal alignment of the value in the cell.")
    hyperlink_display_type: Literal["HYPERLINK_DISPLAY_TYPE_UNSPECIFIED", "LINKED", "PLAIN_TEXT"] | None = Field(None, validation_alias="hyperlinkDisplayType", serialization_alias="hyperlinkDisplayType", description="If one exists, how a hyperlink should be displayed in the cell.")
    number_format: NumberFormat | None = Field(None, validation_alias="numberFormat", serialization_alias="numberFormat", description="A format describing how number values should be represented to the user.")
    padding: Padding | None = Field(None, description="The padding of the cell.")
    text_direction: Literal["TEXT_DIRECTION_UNSPECIFIED", "LEFT_TO_RIGHT", "RIGHT_TO_LEFT"] | None = Field(None, validation_alias="textDirection", serialization_alias="textDirection", description="The direction of the text in the cell.")
    text_format: TextFormat | None = Field(None, validation_alias="textFormat", serialization_alias="textFormat", description="The format of the text in the cell (unless overridden by a format run). Setting a cell-level link here clears the cell's existing links. Setting the link field in a TextFormatRun takes precedence over the cell-level link.")
    text_rotation: TextRotation | None = Field(None, validation_alias="textRotation", serialization_alias="textRotation", description="The rotation applied to text in the cell.")
    vertical_alignment: Literal["VERTICAL_ALIGN_UNSPECIFIED", "TOP", "MIDDLE", "BOTTOM"] | None = Field(None, validation_alias="verticalAlignment", serialization_alias="verticalAlignment", description="The vertical alignment of the value in the cell.")
    wrap_strategy: Literal["WRAP_STRATEGY_UNSPECIFIED", "OVERFLOW_CELL", "LEGACY_WRAP", "CLIP", "WRAP"] | None = Field(None, validation_alias="wrapStrategy", serialization_alias="wrapStrategy", description="The wrap strategy for the value in the cell.")

class BooleanRule(PermissiveModel):
    """A rule that may or may not match, depending on the condition."""
    condition: BooleanCondition | None = Field(None, description="The condition of the rule. If the condition evaluates to true, the format is applied.")
    format_: CellFormat | None = Field(None, validation_alias="format", serialization_alias="format", description="The format to apply. Conditional formatting can only apply a subset of formatting: bold, italic, strikethrough, foreground color and, background color.")

class CellData(PermissiveModel):
    """Data about a specific cell."""
    chip_runs: list[ChipRun] | None = Field(None, validation_alias="chipRuns", serialization_alias="chipRuns", description="Optional. Runs of chips applied to subsections of the cell. Properties of a run start at a specific index in the text and continue until the next run. When reading, all chipped and non-chipped runs are included. Non-chipped runs will have an empty Chip. When writing, only runs with chips are included. Runs containing chips are of length 1 and are represented in the user-entered text by an “@” placeholder symbol. New runs will overwrite any prior runs. Writing a new user_entered_value will erase previous runs.")
    data_source_formula: DataSourceFormula | None = Field(None, validation_alias="dataSourceFormula", serialization_alias="dataSourceFormula", description="Output only. Information about a data source formula on the cell. The field is set if user_entered_value is a formula referencing some DATA_SOURCE sheet, e.g. `=SUM(DataSheet!Column)`.")
    data_source_table: DataSourceTable | None = Field(None, validation_alias="dataSourceTable", serialization_alias="dataSourceTable", description="A data source table anchored at this cell. The size of data source table itself is computed dynamically based on its configuration. Only the first cell of the data source table contains the data source table definition. The other cells will contain the display values of the data source table result in their effective_value fields.")
    data_validation: DataValidationRule | None = Field(None, validation_alias="dataValidation", serialization_alias="dataValidation", description="A data validation rule on the cell, if any. When writing, the new data validation rule will overwrite any prior rule.")
    effective_format: CellFormat | None = Field(None, validation_alias="effectiveFormat", serialization_alias="effectiveFormat", description="The effective format being used by the cell. This includes the results of applying any conditional formatting and, if the cell contains a formula, the computed number format. If the effective format is the default format, effective format will not be written. This field is read-only.")
    effective_value: ExtendedValue | None = Field(None, validation_alias="effectiveValue", serialization_alias="effectiveValue", description="The effective value of the cell. For cells with formulas, this is the calculated value. For cells with literals, this is the same as the user_entered_value. This field is read-only.")
    formatted_value: str | None = Field(None, validation_alias="formattedValue", serialization_alias="formattedValue", description="The formatted value of the cell. This is the value as it's shown to the user. This field is read-only.")
    hyperlink: str | None = Field(None, description="A hyperlink this cell points to, if any. If the cell contains multiple hyperlinks, this field will be empty. This field is read-only. To set it, use a `=HYPERLINK` formula in the userEnteredValue.formulaValue field. A cell-level link can also be set from the userEnteredFormat.textFormat field. Alternatively, set a hyperlink in the textFormatRun.format.link field that spans the entire cell.")
    note: str | None = Field(None, description="Any note on the cell.")
    pivot_table: PivotTable | None = Field(None, validation_alias="pivotTable", serialization_alias="pivotTable", description="A pivot table anchored at this cell. The size of pivot table itself is computed dynamically based on its data, grouping, filters, values, etc. Only the top-left cell of the pivot table contains the pivot table definition. The other cells will contain the calculated values of the results of the pivot in their effective_value fields.")
    text_format_runs: list[TextFormatRun] | None = Field(None, validation_alias="textFormatRuns", serialization_alias="textFormatRuns", description="Runs of rich text applied to subsections of the cell. Runs are only valid on user entered strings, not formulas, bools, or numbers. Properties of a run start at a specific index in the text and continue until the next run. Runs will inherit the properties of the cell unless explicitly changed. When writing, the new runs will overwrite any prior runs. When writing a new user_entered_value, previous runs are erased.")
    user_entered_format: CellFormat | None = Field(None, validation_alias="userEnteredFormat", serialization_alias="userEnteredFormat", description="The format the user entered for the cell. When writing, the new format will be merged with the existing format.")
    user_entered_value: ExtendedValue | None = Field(None, validation_alias="userEnteredValue", serialization_alias="userEnteredValue", description="The value the user entered in the cell. e.g., `1234`, `'Hello'`, or `=NOW()` Note: Dates, Times and DateTimes are represented as doubles in serial number format.")

class ConditionalFormatRule(PermissiveModel):
    """A rule describing a conditional format."""
    boolean_rule: BooleanRule | None = Field(None, validation_alias="booleanRule", serialization_alias="booleanRule", description="The formatting is either \"on\" or \"off\" according to the rule.")
    gradient_rule: GradientRule | None = Field(None, validation_alias="gradientRule", serialization_alias="gradientRule", description="The formatting will vary based on the gradients in the rule.")
    ranges: list[GridRange] | None = Field(None, description="The ranges that are formatted if the condition is true. All the ranges must be on the same grid.")

class AddConditionalFormatRuleRequest(PermissiveModel):
    """Adds a new conditional format rule at the given index. All subsequent rules' indexes are incremented."""
    index: int | None = Field(None, description="The zero-based index where the rule should be inserted.", json_schema_extra={'format': 'int32'})
    rule: ConditionalFormatRule | None = Field(None, description="The rule to add.")

class RepeatCellRequest(PermissiveModel):
    """Updates all cells in the range to the values in the given Cell object. Only the fields listed in the fields field are updated; others are unchanged. If writing a cell with a formula, the formula's ranges will automatically increment for each field in the range. For example, if writing a cell with formula `=A1` into range B2:C4, B2 would be `=A1`, B3 would be `=A2`, B4 would be `=A3`, C2 would be `=B1`, C3 would be `=B2`, C4 would be `=B3`. To keep the formula's ranges static, use the `$` indicator. For example, use the formula `=$A$1` to prevent both the row and the column from incrementing."""
    cell: CellData | None = Field(None, description="The data to write.")
    fields: str | None = Field(None, description="The fields that should be updated. At least one field must be specified. The root `cell` is implied and should not be specified. A single `\"*\"` can be used as short-hand for listing every field.", json_schema_extra={'format': 'google-fieldmask'})
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range to repeat the cell in.")

class RowData(PermissiveModel):
    """Data about each cell in a row."""
    values: list[CellData] | None = Field(None, description="The values in the row, one per column.")

class AppendCellsRequest(PermissiveModel):
    """Adds new cells after the last row with data in a sheet, inserting new rows into the sheet if necessary."""
    fields: str | None = Field(None, description="The fields of CellData that should be updated. At least one field must be specified. The root is the CellData; 'row.values.' should not be specified. A single `\"*\"` can be used as short-hand for listing every field.", json_schema_extra={'format': 'google-fieldmask'})
    rows: list[RowData] | None = Field(None, description="The data to append.")
    sheet_id: int | None = Field(None, validation_alias="sheetId", serialization_alias="sheetId", description="The sheet ID to append the data to.", json_schema_extra={'format': 'int32'})
    table_id: str | None = Field(None, validation_alias="tableId", serialization_alias="tableId", description="The ID of the table to append data to. The data will be only appended to the table body. This field also takes precedence over the `sheet_id` field.")

class GridData(PermissiveModel):
    """Data in the grid, as well as metadata about the dimensions."""
    column_metadata: list[DimensionProperties] | None = Field(None, validation_alias="columnMetadata", serialization_alias="columnMetadata", description="Metadata about the requested columns in the grid, starting with the column in start_column.")
    row_data: list[RowData] | None = Field(None, validation_alias="rowData", serialization_alias="rowData", description="The data in the grid, one entry per row, starting with the row in startRow. The values in RowData will correspond to columns starting at start_column.")
    row_metadata: list[DimensionProperties] | None = Field(None, validation_alias="rowMetadata", serialization_alias="rowMetadata", description="Metadata about the requested rows in the grid, starting with the row in start_row.")
    start_column: int | None = Field(None, validation_alias="startColumn", serialization_alias="startColumn", description="The first column this GridData refers to, zero-based.", json_schema_extra={'format': 'int32'})
    start_row: int | None = Field(None, validation_alias="startRow", serialization_alias="startRow", description="The first row this GridData refers to, zero-based.", json_schema_extra={'format': 'int32'})

class TextToColumnsRequest(PermissiveModel):
    """Splits a column of text into multiple columns, based on a delimiter in each cell."""
    delimiter: str | None = Field(None, description="The delimiter to use. Used only if delimiterType is CUSTOM.")
    delimiter_type: Literal["DELIMITER_TYPE_UNSPECIFIED", "COMMA", "SEMICOLON", "PERIOD", "SPACE", "CUSTOM", "AUTODETECT"] | None = Field(None, validation_alias="delimiterType", serialization_alias="delimiterType", description="The delimiter type to use.")
    source: GridRange | None = Field(None, description="The source data range. This must span exactly one column.")

class ThemeColorPair(PermissiveModel):
    """A pair mapping a spreadsheet theme color type to the concrete color it represents."""
    color: ColorStyle | None = Field(None, description="The concrete color corresponding to the theme color type.")
    color_type: Literal["THEME_COLOR_TYPE_UNSPECIFIED", "TEXT", "BACKGROUND", "ACCENT1", "ACCENT2", "ACCENT3", "ACCENT4", "ACCENT5", "ACCENT6", "LINK"] | None = Field(None, validation_alias="colorType", serialization_alias="colorType", description="The type of the spreadsheet theme color.")

class SpreadsheetTheme(PermissiveModel):
    """Represents spreadsheet theme"""
    primary_font_family: str | None = Field(None, validation_alias="primaryFontFamily", serialization_alias="primaryFontFamily", description="Name of the primary font family.")
    theme_colors: list[ThemeColorPair] | None = Field(None, validation_alias="themeColors", serialization_alias="themeColors", description="The spreadsheet theme color pairs. To update you must provide all theme color pairs.")

class SpreadsheetProperties(PermissiveModel):
    """Properties of a spreadsheet."""
    auto_recalc: Literal["RECALCULATION_INTERVAL_UNSPECIFIED", "ON_CHANGE", "MINUTE", "HOUR"] | None = Field(None, validation_alias="autoRecalc", serialization_alias="autoRecalc", description="The amount of time to wait before volatile functions are recalculated.")
    default_format: CellFormat | None = Field(None, validation_alias="defaultFormat", serialization_alias="defaultFormat", description="The default format of all cells in the spreadsheet. CellData.effectiveFormat will not be set if the cell's format is equal to this default format. This field is read-only.")
    import_functions_external_url_access_allowed: bool | None = Field(None, validation_alias="importFunctionsExternalUrlAccessAllowed", serialization_alias="importFunctionsExternalUrlAccessAllowed", description="Whether to allow external URL access for image and import functions. Read only when true. When false, you can set to true. This value will be bypassed and always return true if the admin has enabled the [allowlisting feature](https://support.google.com/a?p=url_allowlist).")
    iterative_calculation_settings: IterativeCalculationSettings | None = Field(None, validation_alias="iterativeCalculationSettings", serialization_alias="iterativeCalculationSettings", description="Determines whether and how circular references are resolved with iterative calculation. Absence of this field means that circular references result in calculation errors.")
    locale: str | None = Field(None, description="The locale of the spreadsheet in one of the following formats: * an ISO 639-1 language code such as `en` * an ISO 639-2 language code such as `fil`, if no 639-1 code exists * a combination of the ISO language code and country code, such as `en_US` Note: when updating this field, not all locales/languages are supported.")
    spreadsheet_theme: SpreadsheetTheme | None = Field(None, validation_alias="spreadsheetTheme", serialization_alias="spreadsheetTheme", description="Theme applied to the spreadsheet.")
    time_zone: str | None = Field(None, validation_alias="timeZone", serialization_alias="timeZone", description="The time zone of the spreadsheet, in CLDR format such as `America/New_York`. If the time zone isn't recognized, this may be a custom time zone such as `GMT-07:00`.")
    title: str | None = Field(None, description="The title of the spreadsheet.")

class TimeOfDay(PermissiveModel):
    """Represents a time of day. The date and time zone are either not significant or are specified elsewhere. An API may choose to allow leap seconds. Related types are google.type.Date and `google.protobuf.Timestamp`."""
    hours: int | None = Field(None, description="Hours of a day in 24 hour format. Must be greater than or equal to 0 and typically must be less than or equal to 23. An API may choose to allow the value \"24:00:00\" for scenarios like business closing time.", json_schema_extra={'format': 'int32'})
    minutes: int | None = Field(None, description="Minutes of an hour. Must be greater than or equal to 0 and less than or equal to 59.", json_schema_extra={'format': 'int32'})
    nanos: int | None = Field(None, description="Fractions of seconds, in nanoseconds. Must be greater than or equal to 0 and less than or equal to 999,999,999.", json_schema_extra={'format': 'int32'})
    seconds: int | None = Field(None, description="Seconds of a minute. Must be greater than or equal to 0 and typically must be less than or equal to 59. An API may allow the value 60 if it allows leap-seconds.", json_schema_extra={'format': 'int32'})

class DataSourceRefreshDailySchedule(PermissiveModel):
    """A schedule for data to refresh every day in a given time interval."""
    start_time: TimeOfDay | None = Field(None, validation_alias="startTime", serialization_alias="startTime", description="The start time of a time interval in which a data source refresh is scheduled. Only `hours` part is used. The time interval size defaults to that in the Sheets editor.")

class DataSourceRefreshMonthlySchedule(PermissiveModel):
    """A monthly schedule for data to refresh on specific days in the month in a given time interval."""
    days_of_month: list[int] | None = Field(None, validation_alias="daysOfMonth", serialization_alias="daysOfMonth", description="Days of the month to refresh. Only 1-28 are supported, mapping to the 1st to the 28th day. At least one day must be specified.")
    start_time: TimeOfDay | None = Field(None, validation_alias="startTime", serialization_alias="startTime", description="The start time of a time interval in which a data source refresh is scheduled. Only `hours` part is used. The time interval size defaults to that in the Sheets editor.")

class DataSourceRefreshWeeklySchedule(PermissiveModel):
    """A weekly schedule for data to refresh on specific days in a given time interval."""
    days_of_week: list[Literal["DAY_OF_WEEK_UNSPECIFIED", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]] | None = Field(None, validation_alias="daysOfWeek", serialization_alias="daysOfWeek", description="Days of the week to refresh. At least one day must be specified.")
    start_time: TimeOfDay | None = Field(None, validation_alias="startTime", serialization_alias="startTime", description="The start time of a time interval in which a data source refresh is scheduled. Only `hours` part is used. The time interval size defaults to that in the Sheets editor.")

class DataSourceRefreshSchedule(PermissiveModel):
    """Schedule for refreshing the data source. Data sources in the spreadsheet are refreshed within a time interval. You can specify the start time by clicking the Scheduled Refresh button in the Sheets editor, but the interval is fixed at 4 hours. For example, if you specify a start time of 8 AM , the refresh will take place between 8 AM and 12 PM every day."""
    daily_schedule: DataSourceRefreshDailySchedule | None = Field(None, validation_alias="dailySchedule", serialization_alias="dailySchedule", description="Daily refresh schedule.")
    enabled: bool | None = Field(None, description="True if the refresh schedule is enabled, or false otherwise.")
    monthly_schedule: DataSourceRefreshMonthlySchedule | None = Field(None, validation_alias="monthlySchedule", serialization_alias="monthlySchedule", description="Monthly refresh schedule.")
    next_run: Interval | None = Field(None, validation_alias="nextRun", serialization_alias="nextRun", description="Output only. The time interval of the next run.")
    refresh_scope: Literal["DATA_SOURCE_REFRESH_SCOPE_UNSPECIFIED", "ALL_DATA_SOURCES"] | None = Field(None, validation_alias="refreshScope", serialization_alias="refreshScope", description="The scope of the refresh. Must be ALL_DATA_SOURCES.")
    weekly_schedule: DataSourceRefreshWeeklySchedule | None = Field(None, validation_alias="weeklySchedule", serialization_alias="weeklySchedule", description="Weekly refresh schedule.")

class TreemapChartColorScale(PermissiveModel):
    """A color scale for a treemap chart."""
    max_value_color: Color | None = Field(None, validation_alias="maxValueColor", serialization_alias="maxValueColor", description="The background color for cells with a color value greater than or equal to maxValue. Defaults to #109618 if not specified. Deprecated: Use max_value_color_style.")
    max_value_color_style: ColorStyle | None = Field(None, validation_alias="maxValueColorStyle", serialization_alias="maxValueColorStyle", description="The background color for cells with a color value greater than or equal to maxValue. Defaults to #109618 if not specified. If max_value_color is also set, this field takes precedence.")
    mid_value_color: Color | None = Field(None, validation_alias="midValueColor", serialization_alias="midValueColor", description="The background color for cells with a color value at the midpoint between minValue and maxValue. Defaults to #efe6dc if not specified. Deprecated: Use mid_value_color_style.")
    mid_value_color_style: ColorStyle | None = Field(None, validation_alias="midValueColorStyle", serialization_alias="midValueColorStyle", description="The background color for cells with a color value at the midpoint between minValue and maxValue. Defaults to #efe6dc if not specified. If mid_value_color is also set, this field takes precedence.")
    min_value_color: Color | None = Field(None, validation_alias="minValueColor", serialization_alias="minValueColor", description="The background color for cells with a color value less than or equal to minValue. Defaults to #dc3912 if not specified. Deprecated: Use min_value_color_style.")
    min_value_color_style: ColorStyle | None = Field(None, validation_alias="minValueColorStyle", serialization_alias="minValueColorStyle", description="The background color for cells with a color value less than or equal to minValue. Defaults to #dc3912 if not specified. If min_value_color is also set, this field takes precedence.")
    no_data_color: Color | None = Field(None, validation_alias="noDataColor", serialization_alias="noDataColor", description="The background color for cells that have no color data associated with them. Defaults to #000000 if not specified. Deprecated: Use no_data_color_style.")
    no_data_color_style: ColorStyle | None = Field(None, validation_alias="noDataColorStyle", serialization_alias="noDataColorStyle", description="The background color for cells that have no color data associated with them. Defaults to #000000 if not specified. If no_data_color is also set, this field takes precedence.")

class TreemapChartSpec(PermissiveModel):
    """A Treemap chart."""
    color_data: ChartData | None = Field(None, validation_alias="colorData", serialization_alias="colorData", description="The data that determines the background color of each treemap data cell. This field is optional. If not specified, size_data is used to determine background colors. If specified, the data is expected to be numeric. color_scale will determine how the values in this data map to data cell background colors.")
    color_scale: TreemapChartColorScale | None = Field(None, validation_alias="colorScale", serialization_alias="colorScale", description="The color scale for data cells in the treemap chart. Data cells are assigned colors based on their color values. These color values come from color_data, or from size_data if color_data is not specified. Cells with color values less than or equal to min_value will have minValueColor as their background color. Cells with color values greater than or equal to max_value will have maxValueColor as their background color. Cells with color values between min_value and max_value will have background colors on a gradient between minValueColor and maxValueColor, the midpoint of the gradient being midValueColor. Cells with missing or non-numeric color values will have noDataColor as their background color.")
    header_color: Color | None = Field(None, validation_alias="headerColor", serialization_alias="headerColor", description="The background color for header cells. Deprecated: Use header_color_style.")
    header_color_style: ColorStyle | None = Field(None, validation_alias="headerColorStyle", serialization_alias="headerColorStyle", description="The background color for header cells. If header_color is also set, this field takes precedence.")
    hide_tooltips: bool | None = Field(None, validation_alias="hideTooltips", serialization_alias="hideTooltips", description="True to hide tooltips.")
    hinted_levels: int | None = Field(None, validation_alias="hintedLevels", serialization_alias="hintedLevels", description="The number of additional data levels beyond the labeled levels to be shown on the treemap chart. These levels are not interactive and are shown without their labels. Defaults to 0 if not specified.", json_schema_extra={'format': 'int32'})
    labels: ChartData | None = Field(None, description="The data that contains the treemap cell labels.")
    levels: int | None = Field(None, description="The number of data levels to show on the treemap chart. These levels are interactive and are shown with their labels. Defaults to 2 if not specified.", json_schema_extra={'format': 'int32'})
    max_value: float | None = Field(None, validation_alias="maxValue", serialization_alias="maxValue", description="The maximum possible data value. Cells with values greater than this will have the same color as cells with this value. If not specified, defaults to the actual maximum value from color_data, or the maximum value from size_data if color_data is not specified.", json_schema_extra={'format': 'double'})
    min_value: float | None = Field(None, validation_alias="minValue", serialization_alias="minValue", description="The minimum possible data value. Cells with values less than this will have the same color as cells with this value. If not specified, defaults to the actual minimum value from color_data, or the minimum value from size_data if color_data is not specified.", json_schema_extra={'format': 'double'})
    parent_labels: ChartData | None = Field(None, validation_alias="parentLabels", serialization_alias="parentLabels", description="The data the contains the treemap cells' parent labels.")
    size_data: ChartData | None = Field(None, validation_alias="sizeData", serialization_alias="sizeData", description="The data that determines the size of each treemap data cell. This data is expected to be numeric. The cells corresponding to non-numeric or missing data will not be rendered. If color_data is not specified, this data is used to determine data cell background colors as well.")
    text_format: TextFormat | None = Field(None, validation_alias="textFormat", serialization_alias="textFormat", description="The text format for all labels on the chart. The link field is not supported.")

class TrimWhitespaceRequest(PermissiveModel):
    """Trims the whitespace (such as spaces, tabs, or new lines) in every cell in the specified range. This request removes all whitespace from the start and end of each cell's text, and reduces any subsequence of remaining whitespace characters to a single space. If the resulting trimmed text starts with a '+' or '=' character, the text remains as a string value and isn't interpreted as a formula."""
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range whose cells to trim.")

class UnmergeCellsRequest(PermissiveModel):
    """Unmerges cells in the given range."""
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range within which all cells should be unmerged. If the range spans multiple merges, all will be unmerged. The range must not partially span any merge.")

class UpdateBandingRequest(PermissiveModel):
    """Updates properties of the supplied banded range."""
    banded_range: BandedRange | None = Field(None, validation_alias="bandedRange", serialization_alias="bandedRange", description="The banded range to update with the new properties.")
    fields: str | None = Field(None, description="The fields that should be updated. At least one field must be specified. The root `bandedRange` is implied and should not be specified. A single `\"*\"` can be used as short-hand for listing every field.", json_schema_extra={'format': 'google-fieldmask'})

class UpdateBordersRequest(PermissiveModel):
    """Updates the borders of a range. If a field is not set in the request, that means the border remains as-is. For example, with two subsequent UpdateBordersRequest: 1. range: A1:A5 `{ top: RED, bottom: WHITE }` 2. range: A1:A5 `{ left: BLUE }` That would result in A1:A5 having a borders of `{ top: RED, bottom: WHITE, left: BLUE }`. If you want to clear a border, explicitly set the style to NONE."""
    bottom: Border | None = Field(None, description="The border to put at the bottom of the range.")
    inner_horizontal: Border | None = Field(None, validation_alias="innerHorizontal", serialization_alias="innerHorizontal", description="The horizontal border to put within the range.")
    inner_vertical: Border | None = Field(None, validation_alias="innerVertical", serialization_alias="innerVertical", description="The vertical border to put within the range.")
    left: Border | None = Field(None, description="The border to put at the left of the range.")
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range whose borders should be updated.")
    right: Border | None = Field(None, description="The border to put at the right of the range.")
    top: Border | None = Field(None, description="The border to put at the top of the range.")

class UpdateCellsRequest(PermissiveModel):
    """Updates all cells in a range with new data."""
    fields: str | None = Field(None, description="The fields of CellData that should be updated. At least one field must be specified. The root is the CellData; 'row.values.' should not be specified. A single `\"*\"` can be used as short-hand for listing every field.", json_schema_extra={'format': 'google-fieldmask'})
    range_: GridRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The range to write data to. If the data in rows does not cover the entire requested range, the fields matching those set in fields will be cleared.")
    rows: list[RowData] | None = Field(None, description="The data to write.")
    start: GridCoordinate | None = Field(None, description="The coordinate to start writing data at. Any number of rows and columns (including a different number of columns per row) may be written.")

class UpdateConditionalFormatRuleRequest(PermissiveModel):
    """Updates a conditional format rule at the given index, or moves a conditional format rule to another index."""
    index: int | None = Field(None, description="The zero-based index of the rule that should be replaced or moved.", json_schema_extra={'format': 'int32'})
    new_index: int | None = Field(None, validation_alias="newIndex", serialization_alias="newIndex", description="The zero-based new index the rule should end up at.", json_schema_extra={'format': 'int32'})
    rule: ConditionalFormatRule | None = Field(None, description="The rule that should replace the rule at the given index.")
    sheet_id: int | None = Field(None, validation_alias="sheetId", serialization_alias="sheetId", description="The sheet of the rule to move. Required if new_index is set, unused otherwise.", json_schema_extra={'format': 'int32'})

class UpdateDataSourceRequest(PermissiveModel):
    """Updates a data source. After the data source is updated successfully, an execution is triggered to refresh the associated DATA_SOURCE sheet to read data from the updated data source. The request requires an additional `bigquery.readonly` OAuth scope if you are updating a BigQuery data source."""
    data_source: DataSource | None = Field(None, validation_alias="dataSource", serialization_alias="dataSource", description="The data source to update.")
    fields: str | None = Field(None, description="The fields that should be updated. At least one field must be specified. The root `dataSource` is implied and should not be specified. A single `\"*\"` can be used as short-hand for listing every field.", json_schema_extra={'format': 'google-fieldmask'})

class UpdateDeveloperMetadataRequest(PermissiveModel):
    """A request to update properties of developer metadata. Updates the properties of the developer metadata selected by the filters to the values provided in the DeveloperMetadata resource. Callers must specify the properties they wish to update in the fields parameter, as well as specify at least one DataFilter matching the metadata they wish to update."""
    data_filters: list[DataFilter] | None = Field(None, validation_alias="dataFilters", serialization_alias="dataFilters", description="The filters matching the developer metadata entries to update.")
    developer_metadata: DeveloperMetadata | None = Field(None, validation_alias="developerMetadata", serialization_alias="developerMetadata", description="The value that all metadata matched by the data filters will be updated to.")
    fields: str | None = Field(None, description="The fields that should be updated. At least one field must be specified. The root `developerMetadata` is implied and should not be specified. A single `\"*\"` can be used as short-hand for listing every field.", json_schema_extra={'format': 'google-fieldmask'})

class UpdateDimensionGroupRequest(PermissiveModel):
    """Updates the state of the specified group."""
    dimension_group: DimensionGroup | None = Field(None, validation_alias="dimensionGroup", serialization_alias="dimensionGroup", description="The group whose state should be updated. The range and depth of the group should specify a valid group on the sheet, and all other fields updated.")
    fields: str | None = Field(None, description="The fields that should be updated. At least one field must be specified. The root `dimensionGroup` is implied and should not be specified. A single `\"*\"` can be used as short-hand for listing every field.", json_schema_extra={'format': 'google-fieldmask'})

class UpdateDimensionPropertiesRequest(PermissiveModel):
    """Updates properties of dimensions within the specified range."""
    data_source_sheet_range: DataSourceSheetDimensionRange | None = Field(None, validation_alias="dataSourceSheetRange", serialization_alias="dataSourceSheetRange", description="The columns on a data source sheet to update.")
    fields: str | None = Field(None, description="The fields that should be updated. At least one field must be specified. The root `properties` is implied and should not be specified. A single `\"*\"` can be used as short-hand for listing every field.", json_schema_extra={'format': 'google-fieldmask'})
    properties: DimensionProperties | None = Field(None, description="Properties to update.")
    range_: DimensionRange | None = Field(None, validation_alias="range", serialization_alias="range", description="The rows or columns to update.")

class UpdateEmbeddedObjectBorderRequest(PermissiveModel):
    """Updates an embedded object's border property."""
    border: EmbeddedObjectBorder | None = Field(None, description="The border that applies to the embedded object.")
    fields: str | None = Field(None, description="The fields that should be updated. At least one field must be specified. The root `border` is implied and should not be specified. A single `\"*\"` can be used as short-hand for listing every field.", json_schema_extra={'format': 'google-fieldmask'})
    object_id: int | None = Field(None, validation_alias="objectId", serialization_alias="objectId", description="The ID of the embedded object to update.", json_schema_extra={'format': 'int32'})

class UpdateEmbeddedObjectPositionRequest(PermissiveModel):
    """Update an embedded object's position (such as a moving or resizing a chart or image)."""
    fields: str | None = Field(None, description="The fields of OverlayPosition that should be updated when setting a new position. Used only if newPosition.overlayPosition is set, in which case at least one field must be specified. The root `newPosition.overlayPosition` is implied and should not be specified. A single `\"*\"` can be used as short-hand for listing every field.", json_schema_extra={'format': 'google-fieldmask'})
    new_position: EmbeddedObjectPosition | None = Field(None, validation_alias="newPosition", serialization_alias="newPosition", description="An explicit position to move the embedded object to. If newPosition.sheetId is set, a new sheet with that ID will be created. If newPosition.newSheet is set to true, a new sheet will be created with an ID that will be chosen for you.")
    object_id: int | None = Field(None, validation_alias="objectId", serialization_alias="objectId", description="The ID of the object to moved.", json_schema_extra={'format': 'int32'})

class UpdateFilterViewRequest(PermissiveModel):
    """Updates properties of the filter view."""
    fields: str | None = Field(None, description="The fields that should be updated. At least one field must be specified. The root `filter` is implied and should not be specified. A single `\"*\"` can be used as short-hand for listing every field.", json_schema_extra={'format': 'google-fieldmask'})
    filter_: FilterView | None = Field(None, validation_alias="filter", serialization_alias="filter", description="The new properties of the filter view.")

class UpdateNamedRangeRequest(PermissiveModel):
    """Updates properties of the named range with the specified namedRangeId."""
    fields: str | None = Field(None, description="The fields that should be updated. At least one field must be specified. The root `namedRange` is implied and should not be specified. A single `\"*\"` can be used as short-hand for listing every field.", json_schema_extra={'format': 'google-fieldmask'})
    named_range: NamedRange | None = Field(None, validation_alias="namedRange", serialization_alias="namedRange", description="The named range to update with the new properties.")

class UpdateProtectedRangeRequest(PermissiveModel):
    """Updates an existing protected range with the specified protectedRangeId."""
    fields: str | None = Field(None, description="The fields that should be updated. At least one field must be specified. The root `protectedRange` is implied and should not be specified. A single `\"*\"` can be used as short-hand for listing every field.", json_schema_extra={'format': 'google-fieldmask'})
    protected_range: ProtectedRange | None = Field(None, validation_alias="protectedRange", serialization_alias="protectedRange", description="The protected range to update with the new properties.")

class UpdateSheetPropertiesRequest(PermissiveModel):
    """Updates properties of the sheet with the specified sheetId."""
    fields: str | None = Field(None, description="The fields that should be updated. At least one field must be specified. The root `properties` is implied and should not be specified. A single `\"*\"` can be used as short-hand for listing every field.", json_schema_extra={'format': 'google-fieldmask'})
    properties: SheetProperties | None = Field(None, description="The properties to update.")

class UpdateSlicerSpecRequest(PermissiveModel):
    """Updates a slicer's specifications. (This does not move or resize a slicer. To move or resize a slicer use UpdateEmbeddedObjectPositionRequest."""
    fields: str | None = Field(None, description="The fields that should be updated. At least one field must be specified. The root `SlicerSpec` is implied and should not be specified. A single \"*\"` can be used as short-hand for listing every field.", json_schema_extra={'format': 'google-fieldmask'})
    slicer_id: int | None = Field(None, validation_alias="slicerId", serialization_alias="slicerId", description="The id of the slicer to update.", json_schema_extra={'format': 'int32'})
    spec: SlicerSpec | None = Field(None, description="The specification to apply to the slicer.")

class UpdateSpreadsheetPropertiesRequest(PermissiveModel):
    """Updates properties of a spreadsheet."""
    fields: str | None = Field(None, description="The fields that should be updated. At least one field must be specified. The root 'properties' is implied and should not be specified. A single `\"*\"` can be used as short-hand for listing every field.", json_schema_extra={'format': 'google-fieldmask'})
    properties: SpreadsheetProperties | None = Field(None, description="The properties to update.")

class UpdateTableRequest(PermissiveModel):
    """Updates a table in the spreadsheet."""
    fields: str | None = Field(None, description="Required. The fields that should be updated. At least one field must be specified. The root `table` is implied and should not be specified. A single `\"*\"` can be used as short-hand for listing every field.", json_schema_extra={'format': 'google-fieldmask'})
    table: Table | None = Field(None, description="Required. The table to update.")

class ValueRange(PermissiveModel):
    """Data within a range of the spreadsheet."""
    major_dimension: Literal["DIMENSION_UNSPECIFIED", "ROWS", "COLUMNS"] | None = Field(None, validation_alias="majorDimension", serialization_alias="majorDimension", description="The major dimension of the values. For output, if the spreadsheet data is: `A1=1,B1=2,A2=3,B2=4`, then requesting `range=A1:B2,majorDimension=ROWS` will return `[[1,2],[3,4]]`, whereas requesting `range=A1:B2,majorDimension=COLUMNS` will return `[[1,3],[2,4]]`. For input, with `range=A1:B2,majorDimension=ROWS` then `[[1,2],[3,4]]` will set `A1=1,B1=2,A2=3,B2=4`. With `range=A1:B2,majorDimension=COLUMNS` then `[[1,2],[3,4]]` will set `A1=1,B1=3,A2=2,B2=4`. When writing, if this field is not set, it defaults to ROWS.")
    range_: str | None = Field(None, validation_alias="range", serialization_alias="range", description="The range the values cover, in [A1 notation](https://developers.google.com/workspace/sheets/api/guides/concepts#cell). For output, this range indicates the entire requested range, even though the values will exclude trailing rows and columns. When appending values, this field represents the range to search for a table, after which values will be appended.")
    values: list[list[Any]] | None = Field(None, description="The data that was read or to be written. This is an array of arrays, the outer array representing all the data and each inner array representing a major dimension. Each item in the inner array corresponds with one cell. For output, empty trailing rows and columns will not be included. For input, supported value types are: bool, string, and double. Null values will be skipped. To set a cell to an empty value, set the string value to an empty string.")

class WaterfallChartColumnStyle(PermissiveModel):
    """Styles for a waterfall chart column."""
    color: Color | None = Field(None, description="The color of the column. Deprecated: Use color_style.")
    color_style: ColorStyle | None = Field(None, validation_alias="colorStyle", serialization_alias="colorStyle", description="The color of the column. If color is also set, this field takes precedence.")
    label: str | None = Field(None, description="The label of the column's legend.")

class WaterfallChartCustomSubtotal(PermissiveModel):
    """A custom subtotal column for a waterfall chart series."""
    data_is_subtotal: bool | None = Field(None, validation_alias="dataIsSubtotal", serialization_alias="dataIsSubtotal", description="True if the data point at subtotal_index is the subtotal. If false, the subtotal will be computed and appear after the data point.")
    label: str | None = Field(None, description="A label for the subtotal column.")
    subtotal_index: int | None = Field(None, validation_alias="subtotalIndex", serialization_alias="subtotalIndex", description="The zero-based index of a data point within the series. If data_is_subtotal is true, the data point at this index is the subtotal. Otherwise, the subtotal appears after the data point with this index. A series can have multiple subtotals at arbitrary indices, but subtotals do not affect the indices of the data points. For example, if a series has three data points, their indices will always be 0, 1, and 2, regardless of how many subtotals exist on the series or what data points they are associated with.", json_schema_extra={'format': 'int32'})

class WaterfallChartDomain(PermissiveModel):
    """The domain of a waterfall chart."""
    data: ChartData | None = Field(None, description="The data of the WaterfallChartDomain.")
    reversed_: bool | None = Field(None, validation_alias="reversed", serialization_alias="reversed", description="True to reverse the order of the domain values (horizontal axis).")

class WaterfallChartSeries(PermissiveModel):
    """A single series of data for a waterfall chart."""
    custom_subtotals: list[WaterfallChartCustomSubtotal] | None = Field(None, validation_alias="customSubtotals", serialization_alias="customSubtotals", description="Custom subtotal columns appearing in this series. The order in which subtotals are defined is not significant. Only one subtotal may be defined for each data point.")
    data: ChartData | None = Field(None, description="The data being visualized in this series.")
    data_label: DataLabel | None = Field(None, validation_alias="dataLabel", serialization_alias="dataLabel", description="Information about the data labels for this series.")
    hide_trailing_subtotal: bool | None = Field(None, validation_alias="hideTrailingSubtotal", serialization_alias="hideTrailingSubtotal", description="True to hide the subtotal column from the end of the series. By default, a subtotal column will appear at the end of each series. Setting this field to true will hide that subtotal column for this series.")
    negative_columns_style: WaterfallChartColumnStyle | None = Field(None, validation_alias="negativeColumnsStyle", serialization_alias="negativeColumnsStyle", description="Styles for all columns in this series with negative values.")
    positive_columns_style: WaterfallChartColumnStyle | None = Field(None, validation_alias="positiveColumnsStyle", serialization_alias="positiveColumnsStyle", description="Styles for all columns in this series with positive values.")
    subtotal_columns_style: WaterfallChartColumnStyle | None = Field(None, validation_alias="subtotalColumnsStyle", serialization_alias="subtotalColumnsStyle", description="Styles for all subtotal columns in this series.")

class WaterfallChartSpec(PermissiveModel):
    """A waterfall chart."""
    connector_line_style: LineStyle | None = Field(None, validation_alias="connectorLineStyle", serialization_alias="connectorLineStyle", description="The line style for the connector lines.")
    domain: WaterfallChartDomain | None = Field(None, description="The domain data (horizontal axis) for the waterfall chart.")
    first_value_is_total: bool | None = Field(None, validation_alias="firstValueIsTotal", serialization_alias="firstValueIsTotal", description="True to interpret the first value as a total.")
    hide_connector_lines: bool | None = Field(None, validation_alias="hideConnectorLines", serialization_alias="hideConnectorLines", description="True to hide connector lines between columns.")
    series: list[WaterfallChartSeries] | None = Field(None, description="The data this waterfall chart is visualizing.")
    stacked_type: Literal["WATERFALL_STACKED_TYPE_UNSPECIFIED", "STACKED", "SEQUENTIAL"] | None = Field(None, validation_alias="stackedType", serialization_alias="stackedType", description="The stacked type.")
    total_data_label: DataLabel | None = Field(None, validation_alias="totalDataLabel", serialization_alias="totalDataLabel", description="Controls whether to display additional data labels on stacked charts which sum the total value of all stacked values at each value along the domain axis. stacked_type must be STACKED and neither CUSTOM nor placement can be set on the total_data_label.")

class ChartSpec(PermissiveModel):
    """The specifications of a chart."""
    alt_text: str | None = Field(None, validation_alias="altText", serialization_alias="altText", description="The alternative text that describes the chart. This is often used for accessibility.")
    background_color: Color | None = Field(None, validation_alias="backgroundColor", serialization_alias="backgroundColor", description="The background color of the entire chart. Not applicable to Org charts. Deprecated: Use background_color_style.")
    background_color_style: ColorStyle | None = Field(None, validation_alias="backgroundColorStyle", serialization_alias="backgroundColorStyle", description="The background color of the entire chart. Not applicable to Org charts. If background_color is also set, this field takes precedence.")
    basic_chart: BasicChartSpec | None = Field(None, validation_alias="basicChart", serialization_alias="basicChart", description="A basic chart specification, can be one of many kinds of charts. See BasicChartType for the list of all charts this supports.")
    bubble_chart: BubbleChartSpec | None = Field(None, validation_alias="bubbleChart", serialization_alias="bubbleChart", description="A bubble chart specification.")
    candlestick_chart: CandlestickChartSpec | None = Field(None, validation_alias="candlestickChart", serialization_alias="candlestickChart", description="A candlestick chart specification.")
    data_source_chart_properties: DataSourceChartProperties | None = Field(None, validation_alias="dataSourceChartProperties", serialization_alias="dataSourceChartProperties", description="If present, the field contains data source chart specific properties.")
    filter_specs: list[FilterSpec] | None = Field(None, validation_alias="filterSpecs", serialization_alias="filterSpecs", description="The filters applied to the source data of the chart. Only supported for data source charts.")
    font_name: str | None = Field(None, validation_alias="fontName", serialization_alias="fontName", description="The name of the font to use by default for all chart text (e.g. title, axis labels, legend). If a font is specified for a specific part of the chart it will override this font name.")
    hidden_dimension_strategy: Literal["CHART_HIDDEN_DIMENSION_STRATEGY_UNSPECIFIED", "SKIP_HIDDEN_ROWS_AND_COLUMNS", "SKIP_HIDDEN_ROWS", "SKIP_HIDDEN_COLUMNS", "SHOW_ALL"] | None = Field(None, validation_alias="hiddenDimensionStrategy", serialization_alias="hiddenDimensionStrategy", description="Determines how the charts will use hidden rows or columns.")
    histogram_chart: HistogramChartSpec | None = Field(None, validation_alias="histogramChart", serialization_alias="histogramChart", description="A histogram chart specification.")
    maximized: bool | None = Field(None, description="True to make a chart fill the entire space in which it's rendered with minimum padding. False to use the default padding. (Not applicable to Geo and Org charts.)")
    org_chart: OrgChartSpec | None = Field(None, validation_alias="orgChart", serialization_alias="orgChart", description="An org chart specification.")
    pie_chart: PieChartSpec | None = Field(None, validation_alias="pieChart", serialization_alias="pieChart", description="A pie chart specification.")
    scorecard_chart: ScorecardChartSpec | None = Field(None, validation_alias="scorecardChart", serialization_alias="scorecardChart", description="A scorecard chart specification.")
    sort_specs: list[SortSpec] | None = Field(None, validation_alias="sortSpecs", serialization_alias="sortSpecs", description="The order to sort the chart data by. Only a single sort spec is supported. Only supported for data source charts.")
    subtitle: str | None = Field(None, description="The subtitle of the chart.")
    subtitle_text_format: TextFormat | None = Field(None, validation_alias="subtitleTextFormat", serialization_alias="subtitleTextFormat", description="The subtitle text format. Strikethrough, underline, and link are not supported.")
    subtitle_text_position: TextPosition | None = Field(None, validation_alias="subtitleTextPosition", serialization_alias="subtitleTextPosition", description="The subtitle text position. This field is optional.")
    title: str | None = Field(None, description="The title of the chart.")
    title_text_format: TextFormat | None = Field(None, validation_alias="titleTextFormat", serialization_alias="titleTextFormat", description="The title text format. Strikethrough, underline, and link are not supported.")
    title_text_position: TextPosition | None = Field(None, validation_alias="titleTextPosition", serialization_alias="titleTextPosition", description="The title text position. This field is optional.")
    treemap_chart: TreemapChartSpec | None = Field(None, validation_alias="treemapChart", serialization_alias="treemapChart", description="A treemap chart specification.")
    waterfall_chart: WaterfallChartSpec | None = Field(None, validation_alias="waterfallChart", serialization_alias="waterfallChart", description="A waterfall chart specification.")

class EmbeddedChart(PermissiveModel):
    """A chart embedded in a sheet."""
    border: EmbeddedObjectBorder | None = Field(None, description="The border of the chart.")
    chart_id: int | None = Field(None, validation_alias="chartId", serialization_alias="chartId", description="The ID of the chart.", json_schema_extra={'format': 'int32'})
    position: EmbeddedObjectPosition | None = Field(None, description="The position of the chart.")
    spec: ChartSpec | None = Field(None, description="The specification of the chart.")

class AddChartRequest(PermissiveModel):
    """Adds a chart to a sheet in the spreadsheet."""
    chart: EmbeddedChart | None = Field(None, description="The chart that should be added to the spreadsheet, including the position where it should be placed. The chartId field is optional; if one is not set, an id will be randomly generated. (It is an error to specify the ID of an embedded object that already exists.)")

class Sheet(PermissiveModel):
    """A sheet in a spreadsheet."""
    banded_ranges: list[BandedRange] | None = Field(None, validation_alias="bandedRanges", serialization_alias="bandedRanges", description="The banded (alternating colors) ranges on this sheet.")
    basic_filter: BasicFilter | None = Field(None, validation_alias="basicFilter", serialization_alias="basicFilter", description="The filter on this sheet, if any.")
    charts: list[EmbeddedChart] | None = Field(None, description="The specifications of every chart on this sheet.")
    column_groups: list[DimensionGroup] | None = Field(None, validation_alias="columnGroups", serialization_alias="columnGroups", description="All column groups on this sheet, ordered by increasing range start index, then by group depth.")
    conditional_formats: list[ConditionalFormatRule] | None = Field(None, validation_alias="conditionalFormats", serialization_alias="conditionalFormats", description="The conditional format rules in this sheet.")
    data: list[GridData] | None = Field(None, description="Data in the grid, if this is a grid sheet. The number of GridData objects returned is dependent on the number of ranges requested on this sheet. For example, if this is representing `Sheet1`, and the spreadsheet was requested with ranges `Sheet1!A1:C10` and `Sheet1!D15:E20`, then the first GridData will have a startRow/startColumn of `0`, while the second one will have `startRow 14` (zero-based row 15), and `startColumn 3` (zero-based column D). For a DATA_SOURCE sheet, you can not request a specific range, the GridData contains all the values.")
    developer_metadata: list[DeveloperMetadata] | None = Field(None, validation_alias="developerMetadata", serialization_alias="developerMetadata", description="The developer metadata associated with a sheet.")
    filter_views: list[FilterView] | None = Field(None, validation_alias="filterViews", serialization_alias="filterViews", description="The filter views in this sheet.")
    merges: list[GridRange] | None = Field(None, description="The ranges that are merged together.")
    properties: SheetProperties | None = Field(None, description="The properties of the sheet.")
    protected_ranges: list[ProtectedRange] | None = Field(None, validation_alias="protectedRanges", serialization_alias="protectedRanges", description="The protected ranges in this sheet.")
    row_groups: list[DimensionGroup] | None = Field(None, validation_alias="rowGroups", serialization_alias="rowGroups", description="All row groups on this sheet, ordered by increasing range start index, then by group depth.")
    slicers: list[Slicer] | None = Field(None, description="The slicers on this sheet.")
    tables: list[Table] | None = Field(None, description="The tables on this sheet.")

class Spreadsheet(PermissiveModel):
    """Resource that represents a spreadsheet."""
    data_sources: list[DataSource] | None = Field(None, validation_alias="dataSources", serialization_alias="dataSources", description="A list of external data sources connected with the spreadsheet.")
    data_source_schedules: list[DataSourceRefreshSchedule] | None = Field(None, validation_alias="dataSourceSchedules", serialization_alias="dataSourceSchedules", description="Output only. A list of data source refresh schedules.")
    developer_metadata: list[DeveloperMetadata] | None = Field(None, validation_alias="developerMetadata", serialization_alias="developerMetadata", description="The developer metadata associated with a spreadsheet.")
    named_ranges: list[NamedRange] | None = Field(None, validation_alias="namedRanges", serialization_alias="namedRanges", description="The named ranges defined in a spreadsheet.")
    properties: SpreadsheetProperties | None = Field(None, description="Overall properties of a spreadsheet.")
    sheets: list[Sheet] | None = Field(None, description="The sheets that are part of a spreadsheet.")
    spreadsheet_id: str | None = Field(None, validation_alias="spreadsheetId", serialization_alias="spreadsheetId", description="The ID of the spreadsheet. This field is read-only.")
    spreadsheet_url: str | None = Field(None, validation_alias="spreadsheetUrl", serialization_alias="spreadsheetUrl", description="The url of the spreadsheet. This field is read-only.")

class UpdateChartSpecRequest(PermissiveModel):
    """Updates a chart's specifications. (This does not move or resize a chart. To move or resize a chart, use UpdateEmbeddedObjectPositionRequest.)"""
    chart_id: int | None = Field(None, validation_alias="chartId", serialization_alias="chartId", description="The ID of the chart to update.", json_schema_extra={'format': 'int32'})
    spec: ChartSpec | None = Field(None, description="The specification to apply to the chart.")

class Request(PermissiveModel):
    """A single kind of update to apply to a spreadsheet."""
    add_banding: AddBandingRequest | None = Field(None, validation_alias="addBanding", serialization_alias="addBanding", description="Adds a new banded range")
    add_chart: AddChartRequest | None = Field(None, validation_alias="addChart", serialization_alias="addChart", description="Adds a chart.")
    add_conditional_format_rule: AddConditionalFormatRuleRequest | None = Field(None, validation_alias="addConditionalFormatRule", serialization_alias="addConditionalFormatRule", description="Adds a new conditional format rule.")
    add_data_source: AddDataSourceRequest | None = Field(None, validation_alias="addDataSource", serialization_alias="addDataSource", description="Adds a data source.")
    add_dimension_group: AddDimensionGroupRequest | None = Field(None, validation_alias="addDimensionGroup", serialization_alias="addDimensionGroup", description="Creates a group over the specified range.")
    add_filter_view: AddFilterViewRequest | None = Field(None, validation_alias="addFilterView", serialization_alias="addFilterView", description="Adds a filter view.")
    add_named_range: AddNamedRangeRequest | None = Field(None, validation_alias="addNamedRange", serialization_alias="addNamedRange", description="Adds a named range.")
    add_protected_range: AddProtectedRangeRequest | None = Field(None, validation_alias="addProtectedRange", serialization_alias="addProtectedRange", description="Adds a protected range.")
    add_sheet: AddSheetRequest | None = Field(None, validation_alias="addSheet", serialization_alias="addSheet", description="Adds a sheet.")
    add_slicer: AddSlicerRequest | None = Field(None, validation_alias="addSlicer", serialization_alias="addSlicer", description="Adds a slicer.")
    add_table: AddTableRequest | None = Field(None, validation_alias="addTable", serialization_alias="addTable", description="Adds a table.")
    append_cells: AppendCellsRequest | None = Field(None, validation_alias="appendCells", serialization_alias="appendCells", description="Appends cells after the last row with data in a sheet.")
    append_dimension: AppendDimensionRequest | None = Field(None, validation_alias="appendDimension", serialization_alias="appendDimension", description="Appends dimensions to the end of a sheet.")
    auto_fill: AutoFillRequest | None = Field(None, validation_alias="autoFill", serialization_alias="autoFill", description="Automatically fills in more data based on existing data.")
    auto_resize_dimensions: AutoResizeDimensionsRequest | None = Field(None, validation_alias="autoResizeDimensions", serialization_alias="autoResizeDimensions", description="Automatically resizes one or more dimensions based on the contents of the cells in that dimension.")
    cancel_data_source_refresh: CancelDataSourceRefreshRequest | None = Field(None, validation_alias="cancelDataSourceRefresh", serialization_alias="cancelDataSourceRefresh", description="Cancels refreshes of one or multiple data sources and associated dbobjects.")
    clear_basic_filter: ClearBasicFilterRequest | None = Field(None, validation_alias="clearBasicFilter", serialization_alias="clearBasicFilter", description="Clears the basic filter on a sheet.")
    copy_paste: CopyPasteRequest | None = Field(None, validation_alias="copyPaste", serialization_alias="copyPaste", description="Copies data from one area and pastes it to another.")
    create_developer_metadata: CreateDeveloperMetadataRequest | None = Field(None, validation_alias="createDeveloperMetadata", serialization_alias="createDeveloperMetadata", description="Creates new developer metadata")
    cut_paste: CutPasteRequest | None = Field(None, validation_alias="cutPaste", serialization_alias="cutPaste", description="Cuts data from one area and pastes it to another.")
    delete_banding: DeleteBandingRequest | None = Field(None, validation_alias="deleteBanding", serialization_alias="deleteBanding", description="Removes a banded range")
    delete_conditional_format_rule: DeleteConditionalFormatRuleRequest | None = Field(None, validation_alias="deleteConditionalFormatRule", serialization_alias="deleteConditionalFormatRule", description="Deletes an existing conditional format rule.")
    delete_data_source: DeleteDataSourceRequest | None = Field(None, validation_alias="deleteDataSource", serialization_alias="deleteDataSource", description="Deletes a data source.")
    delete_developer_metadata: DeleteDeveloperMetadataRequest | None = Field(None, validation_alias="deleteDeveloperMetadata", serialization_alias="deleteDeveloperMetadata", description="Deletes developer metadata")
    delete_dimension: DeleteDimensionRequest | None = Field(None, validation_alias="deleteDimension", serialization_alias="deleteDimension", description="Deletes rows or columns in a sheet.")
    delete_dimension_group: DeleteDimensionGroupRequest | None = Field(None, validation_alias="deleteDimensionGroup", serialization_alias="deleteDimensionGroup", description="Deletes a group over the specified range.")
    delete_duplicates: DeleteDuplicatesRequest | None = Field(None, validation_alias="deleteDuplicates", serialization_alias="deleteDuplicates", description="Removes rows containing duplicate values in specified columns of a cell range.")
    delete_embedded_object: DeleteEmbeddedObjectRequest | None = Field(None, validation_alias="deleteEmbeddedObject", serialization_alias="deleteEmbeddedObject", description="Deletes an embedded object (e.g, chart, image) in a sheet.")
    delete_filter_view: DeleteFilterViewRequest | None = Field(None, validation_alias="deleteFilterView", serialization_alias="deleteFilterView", description="Deletes a filter view from a sheet.")
    delete_named_range: DeleteNamedRangeRequest | None = Field(None, validation_alias="deleteNamedRange", serialization_alias="deleteNamedRange", description="Deletes a named range.")
    delete_protected_range: DeleteProtectedRangeRequest | None = Field(None, validation_alias="deleteProtectedRange", serialization_alias="deleteProtectedRange", description="Deletes a protected range.")
    delete_range: DeleteRangeRequest | None = Field(None, validation_alias="deleteRange", serialization_alias="deleteRange", description="Deletes a range of cells from a sheet, shifting the remaining cells.")
    delete_sheet: DeleteSheetRequest | None = Field(None, validation_alias="deleteSheet", serialization_alias="deleteSheet", description="Deletes a sheet.")
    delete_table: DeleteTableRequest | None = Field(None, validation_alias="deleteTable", serialization_alias="deleteTable", description="A request for deleting a table.")
    duplicate_filter_view: DuplicateFilterViewRequest | None = Field(None, validation_alias="duplicateFilterView", serialization_alias="duplicateFilterView", description="Duplicates a filter view.")
    duplicate_sheet: DuplicateSheetRequest | None = Field(None, validation_alias="duplicateSheet", serialization_alias="duplicateSheet", description="Duplicates a sheet.")
    find_replace: FindReplaceRequest | None = Field(None, validation_alias="findReplace", serialization_alias="findReplace", description="Finds and replaces occurrences of some text with other text.")
    insert_dimension: InsertDimensionRequest | None = Field(None, validation_alias="insertDimension", serialization_alias="insertDimension", description="Inserts new rows or columns in a sheet.")
    insert_range: InsertRangeRequest | None = Field(None, validation_alias="insertRange", serialization_alias="insertRange", description="Inserts new cells in a sheet, shifting the existing cells.")
    merge_cells: MergeCellsRequest | None = Field(None, validation_alias="mergeCells", serialization_alias="mergeCells", description="Merges cells together.")
    move_dimension: MoveDimensionRequest | None = Field(None, validation_alias="moveDimension", serialization_alias="moveDimension", description="Moves rows or columns to another location in a sheet.")
    paste_data: PasteDataRequest | None = Field(None, validation_alias="pasteData", serialization_alias="pasteData", description="Pastes data (HTML or delimited) into a sheet.")
    randomize_range: RandomizeRangeRequest | None = Field(None, validation_alias="randomizeRange", serialization_alias="randomizeRange", description="Randomizes the order of the rows in a range.")
    refresh_data_source: RefreshDataSourceRequest | None = Field(None, validation_alias="refreshDataSource", serialization_alias="refreshDataSource", description="Refreshes one or multiple data sources and associated dbobjects.")
    repeat_cell: RepeatCellRequest | None = Field(None, validation_alias="repeatCell", serialization_alias="repeatCell", description="Repeats a single cell across a range.")
    set_basic_filter: SetBasicFilterRequest | None = Field(None, validation_alias="setBasicFilter", serialization_alias="setBasicFilter", description="Sets the basic filter on a sheet.")
    set_data_validation: SetDataValidationRequest | None = Field(None, validation_alias="setDataValidation", serialization_alias="setDataValidation", description="Sets data validation for one or more cells.")
    sort_range: SortRangeRequest | None = Field(None, validation_alias="sortRange", serialization_alias="sortRange", description="Sorts data in a range.")
    text_to_columns: TextToColumnsRequest | None = Field(None, validation_alias="textToColumns", serialization_alias="textToColumns", description="Converts a column of text into many columns of text.")
    trim_whitespace: TrimWhitespaceRequest | None = Field(None, validation_alias="trimWhitespace", serialization_alias="trimWhitespace", description="Trims cells of whitespace (such as spaces, tabs, or new lines).")
    unmerge_cells: UnmergeCellsRequest | None = Field(None, validation_alias="unmergeCells", serialization_alias="unmergeCells", description="Unmerges merged cells.")
    update_banding: UpdateBandingRequest | None = Field(None, validation_alias="updateBanding", serialization_alias="updateBanding", description="Updates a banded range")
    update_borders: UpdateBordersRequest | None = Field(None, validation_alias="updateBorders", serialization_alias="updateBorders", description="Updates the borders in a range of cells.")
    update_cells: UpdateCellsRequest | None = Field(None, validation_alias="updateCells", serialization_alias="updateCells", description="Updates many cells at once.")
    update_chart_spec: UpdateChartSpecRequest | None = Field(None, validation_alias="updateChartSpec", serialization_alias="updateChartSpec", description="Updates a chart's specifications.")
    update_conditional_format_rule: UpdateConditionalFormatRuleRequest | None = Field(None, validation_alias="updateConditionalFormatRule", serialization_alias="updateConditionalFormatRule", description="Updates an existing conditional format rule.")
    update_data_source: UpdateDataSourceRequest | None = Field(None, validation_alias="updateDataSource", serialization_alias="updateDataSource", description="Updates a data source.")
    update_developer_metadata: UpdateDeveloperMetadataRequest | None = Field(None, validation_alias="updateDeveloperMetadata", serialization_alias="updateDeveloperMetadata", description="Updates an existing developer metadata entry")
    update_dimension_group: UpdateDimensionGroupRequest | None = Field(None, validation_alias="updateDimensionGroup", serialization_alias="updateDimensionGroup", description="Updates the state of the specified group.")
    update_dimension_properties: UpdateDimensionPropertiesRequest | None = Field(None, validation_alias="updateDimensionProperties", serialization_alias="updateDimensionProperties", description="Updates dimensions' properties.")
    update_embedded_object_border: UpdateEmbeddedObjectBorderRequest | None = Field(None, validation_alias="updateEmbeddedObjectBorder", serialization_alias="updateEmbeddedObjectBorder", description="Updates an embedded object's border.")
    update_embedded_object_position: UpdateEmbeddedObjectPositionRequest | None = Field(None, validation_alias="updateEmbeddedObjectPosition", serialization_alias="updateEmbeddedObjectPosition", description="Updates an embedded object's (e.g. chart, image) position.")
    update_filter_view: UpdateFilterViewRequest | None = Field(None, validation_alias="updateFilterView", serialization_alias="updateFilterView", description="Updates the properties of a filter view.")
    update_named_range: UpdateNamedRangeRequest | None = Field(None, validation_alias="updateNamedRange", serialization_alias="updateNamedRange", description="Updates a named range.")
    update_protected_range: UpdateProtectedRangeRequest | None = Field(None, validation_alias="updateProtectedRange", serialization_alias="updateProtectedRange", description="Updates a protected range.")
    update_sheet_properties: UpdateSheetPropertiesRequest | None = Field(None, validation_alias="updateSheetProperties", serialization_alias="updateSheetProperties", description="Updates a sheet's properties.")
    update_slicer_spec: UpdateSlicerSpecRequest | None = Field(None, validation_alias="updateSlicerSpec", serialization_alias="updateSlicerSpec", description="Updates a slicer's specifications.")
    update_spreadsheet_properties: UpdateSpreadsheetPropertiesRequest | None = Field(None, validation_alias="updateSpreadsheetProperties", serialization_alias="updateSpreadsheetProperties", description="Updates the spreadsheet's properties.")
    update_table: UpdateTableRequest | None = Field(None, validation_alias="updateTable", serialization_alias="updateTable", description="Updates a table.")


# Rebuild models to resolve forward references (required for circular refs)
AddBandingRequest.model_rebuild()
AddChartRequest.model_rebuild()
AddConditionalFormatRuleRequest.model_rebuild()
AddDataSourceRequest.model_rebuild()
AddDimensionGroupRequest.model_rebuild()
AddFilterViewRequest.model_rebuild()
AddNamedRangeRequest.model_rebuild()
AddProtectedRangeRequest.model_rebuild()
AddSheetRequest.model_rebuild()
AddSlicerRequest.model_rebuild()
AddTableRequest.model_rebuild()
AppendCellsRequest.model_rebuild()
AppendDimensionRequest.model_rebuild()
AutoFillRequest.model_rebuild()
AutoResizeDimensionsRequest.model_rebuild()
BandedRange.model_rebuild()
BandingProperties.model_rebuild()
BaselineValueFormat.model_rebuild()
BasicChartAxis.model_rebuild()
BasicChartDomain.model_rebuild()
BasicChartSeries.model_rebuild()
BasicChartSpec.model_rebuild()
BasicFilter.model_rebuild()
BasicSeriesDataPointStyleOverride.model_rebuild()
BigQueryDataSourceSpec.model_rebuild()
BigQueryQuerySpec.model_rebuild()
BigQueryTableSpec.model_rebuild()
BooleanCondition.model_rebuild()
BooleanRule.model_rebuild()
Border.model_rebuild()
Borders.model_rebuild()
BubbleChartSpec.model_rebuild()
CancelDataSourceRefreshRequest.model_rebuild()
CandlestickChartSpec.model_rebuild()
CandlestickData.model_rebuild()
CandlestickDomain.model_rebuild()
CandlestickSeries.model_rebuild()
CellData.model_rebuild()
CellFormat.model_rebuild()
ChartAxisViewWindowOptions.model_rebuild()
ChartCustomNumberFormatOptions.model_rebuild()
ChartData.model_rebuild()
ChartDateTimeRule.model_rebuild()
ChartGroupRule.model_rebuild()
ChartHistogramRule.model_rebuild()
ChartSourceRange.model_rebuild()
ChartSpec.model_rebuild()
Chip.model_rebuild()
ChipRun.model_rebuild()
ClearBasicFilterRequest.model_rebuild()
Color.model_rebuild()
ColorStyle.model_rebuild()
ConditionalFormatRule.model_rebuild()
ConditionValue.model_rebuild()
CopyPasteRequest.model_rebuild()
CreateDeveloperMetadataRequest.model_rebuild()
CutPasteRequest.model_rebuild()
DataExecutionStatus.model_rebuild()
DataFilter.model_rebuild()
DataFilterValueRange.model_rebuild()
DataLabel.model_rebuild()
DataSource.model_rebuild()
DataSourceChartProperties.model_rebuild()
DataSourceColumn.model_rebuild()
DataSourceColumnReference.model_rebuild()
DataSourceFormula.model_rebuild()
DataSourceObjectReference.model_rebuild()
DataSourceObjectReferences.model_rebuild()
DataSourceParameter.model_rebuild()
DataSourceRefreshDailySchedule.model_rebuild()
DataSourceRefreshMonthlySchedule.model_rebuild()
DataSourceRefreshSchedule.model_rebuild()
DataSourceRefreshWeeklySchedule.model_rebuild()
DataSourceSheetDimensionRange.model_rebuild()
DataSourceSheetProperties.model_rebuild()
DataSourceSpec.model_rebuild()
DataSourceTable.model_rebuild()
DataValidationRule.model_rebuild()
DateTimeRule.model_rebuild()
DeleteBandingRequest.model_rebuild()
DeleteConditionalFormatRuleRequest.model_rebuild()
DeleteDataSourceRequest.model_rebuild()
DeleteDeveloperMetadataRequest.model_rebuild()
DeleteDimensionGroupRequest.model_rebuild()
DeleteDimensionRequest.model_rebuild()
DeleteDuplicatesRequest.model_rebuild()
DeleteEmbeddedObjectRequest.model_rebuild()
DeleteFilterViewRequest.model_rebuild()
DeleteNamedRangeRequest.model_rebuild()
DeleteProtectedRangeRequest.model_rebuild()
DeleteRangeRequest.model_rebuild()
DeleteSheetRequest.model_rebuild()
DeleteTableRequest.model_rebuild()
DeveloperMetadata.model_rebuild()
DeveloperMetadataLocation.model_rebuild()
DeveloperMetadataLookup.model_rebuild()
DimensionGroup.model_rebuild()
DimensionProperties.model_rebuild()
DimensionRange.model_rebuild()
DuplicateFilterViewRequest.model_rebuild()
DuplicateSheetRequest.model_rebuild()
Editors.model_rebuild()
EmbeddedChart.model_rebuild()
EmbeddedObjectBorder.model_rebuild()
EmbeddedObjectPosition.model_rebuild()
ErrorValue.model_rebuild()
ExtendedValue.model_rebuild()
FilterCriteria.model_rebuild()
FilterSpec.model_rebuild()
FilterView.model_rebuild()
FindReplaceRequest.model_rebuild()
GradientRule.model_rebuild()
GridCoordinate.model_rebuild()
GridData.model_rebuild()
GridProperties.model_rebuild()
GridRange.model_rebuild()
HistogramChartSpec.model_rebuild()
HistogramRule.model_rebuild()
HistogramSeries.model_rebuild()
InsertDimensionRequest.model_rebuild()
InsertRangeRequest.model_rebuild()
InterpolationPoint.model_rebuild()
Interval.model_rebuild()
IterativeCalculationSettings.model_rebuild()
KeyValueFormat.model_rebuild()
LineStyle.model_rebuild()
Link.model_rebuild()
LookerDataSourceSpec.model_rebuild()
ManualRule.model_rebuild()
ManualRuleGroup.model_rebuild()
MergeCellsRequest.model_rebuild()
MoveDimensionRequest.model_rebuild()
NamedRange.model_rebuild()
NumberFormat.model_rebuild()
OrgChartSpec.model_rebuild()
OverlayPosition.model_rebuild()
Padding.model_rebuild()
PasteDataRequest.model_rebuild()
PersonProperties.model_rebuild()
PieChartSpec.model_rebuild()
PivotFilterCriteria.model_rebuild()
PivotFilterSpec.model_rebuild()
PivotGroup.model_rebuild()
PivotGroupLimit.model_rebuild()
PivotGroupRule.model_rebuild()
PivotGroupSortValueBucket.model_rebuild()
PivotGroupValueMetadata.model_rebuild()
PivotTable.model_rebuild()
PivotValue.model_rebuild()
PointStyle.model_rebuild()
ProtectedRange.model_rebuild()
RandomizeRangeRequest.model_rebuild()
RefreshDataSourceRequest.model_rebuild()
RepeatCellRequest.model_rebuild()
Request.model_rebuild()
RichLinkProperties.model_rebuild()
RowData.model_rebuild()
ScorecardChartSpec.model_rebuild()
SetBasicFilterRequest.model_rebuild()
SetDataValidationRequest.model_rebuild()
Sheet.model_rebuild()
SheetProperties.model_rebuild()
Slicer.model_rebuild()
SlicerSpec.model_rebuild()
SortRangeRequest.model_rebuild()
SortSpec.model_rebuild()
SourceAndDestination.model_rebuild()
Spreadsheet.model_rebuild()
SpreadsheetProperties.model_rebuild()
SpreadsheetTheme.model_rebuild()
Table.model_rebuild()
TableColumnDataValidationRule.model_rebuild()
TableColumnProperties.model_rebuild()
TableRowsProperties.model_rebuild()
TextFormat.model_rebuild()
TextFormatRun.model_rebuild()
TextPosition.model_rebuild()
TextRotation.model_rebuild()
TextToColumnsRequest.model_rebuild()
ThemeColorPair.model_rebuild()
TimeOfDay.model_rebuild()
TreemapChartColorScale.model_rebuild()
TreemapChartSpec.model_rebuild()
TrimWhitespaceRequest.model_rebuild()
UnmergeCellsRequest.model_rebuild()
UpdateBandingRequest.model_rebuild()
UpdateBordersRequest.model_rebuild()
UpdateCellsRequest.model_rebuild()
UpdateChartSpecRequest.model_rebuild()
UpdateConditionalFormatRuleRequest.model_rebuild()
UpdateDataSourceRequest.model_rebuild()
UpdateDeveloperMetadataRequest.model_rebuild()
UpdateDimensionGroupRequest.model_rebuild()
UpdateDimensionPropertiesRequest.model_rebuild()
UpdateEmbeddedObjectBorderRequest.model_rebuild()
UpdateEmbeddedObjectPositionRequest.model_rebuild()
UpdateFilterViewRequest.model_rebuild()
UpdateNamedRangeRequest.model_rebuild()
UpdateProtectedRangeRequest.model_rebuild()
UpdateSheetPropertiesRequest.model_rebuild()
UpdateSlicerSpecRequest.model_rebuild()
UpdateSpreadsheetPropertiesRequest.model_rebuild()
UpdateTableRequest.model_rebuild()
ValueRange.model_rebuild()
WaterfallChartColumnStyle.model_rebuild()
WaterfallChartCustomSubtotal.model_rebuild()
WaterfallChartDomain.model_rebuild()
WaterfallChartSeries.model_rebuild()
WaterfallChartSpec.model_rebuild()

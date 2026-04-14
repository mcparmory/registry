"""
Airtable MCP Server - Pydantic Models

Generated: 2026-04-14 18:13:17 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "DeleteV0BaseidTableidornameRecordidRequest",
    "DeleteV0BaseidTableidornameRequest",
    "GetV0BaseidTableidornameRecordidRequest",
    "GetV0BaseidTableidornameRequest",
    "PatchV0BaseidTableidornameRecordidRequest",
    "PatchV0BaseidTableidornameRequest",
    "PostV0BaseidRecordidAttachmentfieldidornameUploadattachmentRequest",
    "PostV0BaseidTableidornameRequest",
    "PostV0BaseidTableidornameSyncApiendpointsyncidRequest",
    "PutV0BaseidTableidornameRecordidRequest",
    "PutV0BaseidTableidornameRequest",
    "PatchV0BaseidTableidornameBodyRecordsItem",
    "PostV0BaseidTableidornameBodyRecordsItem",
    "PutV0BaseidTableidornameBodyRecordsItem",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_table_records
class GetV0BaseidTableidornameRequestPath(StrictModel):
    base_id: str = Field(default=..., validation_alias="baseId", serialization_alias="baseId", description="The unique identifier for the base containing the table.")
    table_id_or_name: str = Field(default=..., validation_alias="tableIdOrName", serialization_alias="tableIdOrName", description="The table identifier or name to query records from.")
class GetV0BaseidTableidornameRequestQuery(StrictModel):
    time_zone: str | None = Field(default=None, validation_alias="timeZone", serialization_alias="timeZone", description="The time zone for formatting dates when using string cell format (required if cellFormat is 'string'). Use standard time zone identifiers.")
    user_locale: str | None = Field(default=None, validation_alias="userLocale", serialization_alias="userLocale", description="The user locale for formatting dates when using string cell format (required if cellFormat is 'string'). Use standard locale codes.")
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="Number of records to return per page. Must be between 1 and 100 (defaults to 100).", ge=1, le=100)
    max_records: int | None = Field(default=None, validation_alias="maxRecords", serialization_alias="maxRecords", description="The maximum total number of records to return across all paginated requests. Must be at least 1.", ge=1)
    offset: str | None = Field(default=None, description="Pagination token from a previous response. Include this to fetch the next page of records.")
    view: str | None = Field(default=None, description="Filter results to a specific view by its name or ID. Only records visible in that view will be returned.")
    filter_by_formula: str | None = Field(default=None, validation_alias="filterByFormula", serialization_alias="filterByFormula", description="A formula to filter records. Records are included if the formula evaluates to a truthy value (excluding 0, false, empty string, NaN, empty array, or #Error!).")
    cell_format: Literal["json", "string"] | None = Field(default=None, validation_alias="cellFormat", serialization_alias="cellFormat", description="Format for cell values: 'json' returns type-specific JSON representations, 'string' returns user-facing formatted strings. When using 'string', timeZone and userLocale are required.")
    record_metadata: list[Literal["commentCount"]] | None = Field(default=None, validation_alias="recordMetadata", serialization_alias="recordMetadata", description="Optional metadata to include with each record. When specified, adds commentCount to the record metadata.")
    sort: list[dict] | None = Field(default=None, description="A list of sort objects that specifies how the records will be ordered. Each sort object must have a 'field' key and an optional 'direction' key ('asc' or 'desc', default 'asc').")
class GetV0BaseidTableidornameRequest(StrictModel):
    """Retrieve paginated records from a table with optional filtering, formatting, and view selection. Results are returned one page at a time (up to 100 records per page by default), with pagination support via offset tokens."""
    path: GetV0BaseidTableidornameRequestPath
    query: GetV0BaseidTableidornameRequestQuery | None = None

# Operation: create_records
class PostV0BaseidTableidornameRequestPath(StrictModel):
    base_id: str = Field(default=..., validation_alias="baseId", serialization_alias="baseId", description="The unique identifier for the base containing the target table.")
    table_id_or_name: str = Field(default=..., validation_alias="tableIdOrName", serialization_alias="tableIdOrName", description="The table identifier or name. Table IDs are recommended to avoid needing request updates when table names change.")
class PostV0BaseidTableidornameRequestBody(StrictModel):
    records: list[PostV0BaseidTableidornameBodyRecordsItem] | None = Field(default=None, description="Array of up to 10 record objects to create. Each record object should contain a single key with an inner object of cell values, keyed by field name or field ID.")
    typecast: bool | None = Field(default=None, description="Enable automatic type conversion from string values to appropriate field types. Disabled by default to preserve data integrity; enable when integrating with third-party data sources that may require conversion.")
class PostV0BaseidTableidornameRequest(StrictModel):
    """Create multiple records in a table. Submit up to 10 record objects in a single request, with cell values keyed by field name or field ID. Returns an array of newly created record IDs."""
    path: PostV0BaseidTableidornameRequestPath
    body: PostV0BaseidTableidornameRequestBody | None = None

# Operation: replace_records
class PutV0BaseidTableidornameRequestPath(StrictModel):
    base_id: str = Field(default=..., validation_alias="baseId", serialization_alias="baseId", description="The unique identifier of the base containing the table.")
    table_id_or_name: str = Field(default=..., validation_alias="tableIdOrName", serialization_alias="tableIdOrName", description="The unique identifier or name of the table to update.")
class PutV0BaseidTableidornameRequestBodyPerformUpsert(StrictModel):
    fields_to_merge_on: list[str] = Field(default=..., validation_alias="fieldsToMergeOn", serialization_alias="fieldsToMergeOn", description="One to three field names or IDs used to match and identify records for replacement. Field IDs must uniquely identify a single record.")
class PutV0BaseidTableidornameRequestBody(StrictModel):
    typecast: bool | None = Field(default=None, description="When enabled, Airtable will attempt to convert string values to appropriate cell types (e.g., numbers, dates). Defaults to false.")
    records: list[PutV0BaseidTableidornameBodyRecordsItem] = Field(default=..., description="Array of up to 10 records to replace or upsert, with each record containing field values to apply.")
    perform_upsert: PutV0BaseidTableidornameRequestBodyPerformUpsert = Field(default=..., validation_alias="performUpsert", serialization_alias="performUpsert")
class PutV0BaseidTableidornameRequest(StrictModel):
    """Replace multiple records in a table with a destructive update that clears all unincluded cell values. Supports upserting up to 10 records by matching on specified field(s)."""
    path: PutV0BaseidTableidornameRequestPath
    body: PutV0BaseidTableidornameRequestBody

# Operation: update_records
class PatchV0BaseidTableidornameRequestPath(StrictModel):
    base_id: str = Field(default=..., validation_alias="baseId", serialization_alias="baseId", description="The unique identifier of the base containing the table.")
    table_id_or_name: str = Field(default=..., validation_alias="tableIdOrName", serialization_alias="tableIdOrName", description="The unique identifier or name of the table to update records in.")
class PatchV0BaseidTableidornameRequestBodyPerformUpsert(StrictModel):
    fields_to_merge_on: list[str] = Field(default=..., validation_alias="fieldsToMergeOn", serialization_alias="fieldsToMergeOn", description="One to three field names or IDs used to identify which records to update or upsert. Field IDs must uniquely identify a single record. When multiple fields are specified, all must match for a record to be identified.")
class PatchV0BaseidTableidornameRequestBody(StrictModel):
    typecast: bool | None = Field(default=None, description="When enabled, Airtable will automatically convert string values to appropriate cell types (e.g., '123' to number, 'true' to checkbox). Defaults to false.")
    records: list[PatchV0BaseidTableidornameBodyRecordsItem] = Field(default=..., description="Array of record objects to update or upsert, with a maximum of 10 records per request. Each record should include the merge-on fields and any fields to be updated.")
    perform_upsert: PatchV0BaseidTableidornameRequestBodyPerformUpsert = Field(default=..., validation_alias="performUpsert", serialization_alias="performUpsert")
class PatchV0BaseidTableidornameRequest(StrictModel):
    """Update or upsert up to 10 records in a table. When performUpsert is enabled, records matching the specified merge fields are updated; non-matching records are created. Only fields included in the request are modified; all other fields remain unchanged."""
    path: PatchV0BaseidTableidornameRequestPath
    body: PatchV0BaseidTableidornameRequestBody

# Operation: delete_records
class DeleteV0BaseidTableidornameRequestPath(StrictModel):
    base_id: str = Field(default=..., validation_alias="baseId", serialization_alias="baseId", description="The unique identifier for the base containing the table.")
    table_id_or_name: str = Field(default=..., validation_alias="tableIdOrName", serialization_alias="tableIdOrName", description="The table identifier or name where records will be deleted.")
class DeleteV0BaseidTableidornameRequestQuery(StrictModel):
    records: list[str] | None = Field(default=None, description="Array of record IDs to delete. Accepts up to 10 record IDs per request. Each ID should be a valid record identifier string.")
class DeleteV0BaseidTableidornameRequest(StrictModel):
    """Delete multiple records from a table by their record IDs. Supports batch deletion of up to 10 records in a single request."""
    path: DeleteV0BaseidTableidornameRequestPath
    query: DeleteV0BaseidTableidornameRequestQuery | None = None

# Operation: get_record
class GetV0BaseidTableidornameRecordidRequestPath(StrictModel):
    base_id: str = Field(default=..., validation_alias="baseId", serialization_alias="baseId", description="The unique identifier of the base containing the record.")
    table_id_or_name: str = Field(default=..., validation_alias="tableIdOrName", serialization_alias="tableIdOrName", description="The table identifier or name where the record is located.")
    record_id: str = Field(default=..., validation_alias="recordId", serialization_alias="recordId", description="The unique identifier of the record to retrieve.")
class GetV0BaseidTableidornameRecordidRequestQuery(StrictModel):
    cell_format: Literal["json", "string"] | None = Field(default=None, validation_alias="cellFormat", serialization_alias="cellFormat", description="The format for cell values in the response. Use 'json' to format cells according to their field type, or 'string' to format all cells as user-facing strings (requires timeZone and userLocale parameters). Defaults to 'json'.")
class GetV0BaseidTableidornameRecordidRequest(StrictModel):
    """Retrieve a single record by its ID from a specified table. If the record is not found in the table, the system automatically searches across the entire base and returns the record if located."""
    path: GetV0BaseidTableidornameRecordidRequestPath
    query: GetV0BaseidTableidornameRecordidRequestQuery | None = None

# Operation: replace_record
class PutV0BaseidTableidornameRecordidRequestPath(StrictModel):
    base_id: str = Field(default=..., validation_alias="baseId", serialization_alias="baseId", description="The unique identifier for the base containing the table and record to update.")
    table_id_or_name: str = Field(default=..., validation_alias="tableIdOrName", serialization_alias="tableIdOrName", description="The table identifier or name. Both formats are accepted interchangeably.")
    record_id: str = Field(default=..., validation_alias="recordId", serialization_alias="recordId", description="The unique identifier of the record to update.")
class PutV0BaseidTableidornameRecordidRequestBody(StrictModel):
    typecast: bool | None = Field(default=None, description="Enable automatic data type conversion from string values when integrating with third-party data sources. Disabled by default to maintain data integrity.")
    fields: dict[str, Any] = Field(default=..., description="An object containing the cell values for the record, keyed by field name or field ID. Any fields omitted from this object will be cleared during the update.")
class PutV0BaseidTableidornameRecordidRequest(StrictModel):
    """Destructively update a single record in a table, clearing all unspecified cell values. Use this operation when you want to replace the entire record content with new values."""
    path: PutV0BaseidTableidornameRecordidRequestPath
    body: PutV0BaseidTableidornameRecordidRequestBody

# Operation: update_record
class PatchV0BaseidTableidornameRecordidRequestPath(StrictModel):
    base_id: str = Field(default=..., validation_alias="baseId", serialization_alias="baseId", description="The unique identifier for the base containing the record.")
    table_id_or_name: str = Field(default=..., validation_alias="tableIdOrName", serialization_alias="tableIdOrName", description="The table identifier or name where the record is located. Both table IDs and table names are accepted.")
    record_id: str = Field(default=..., validation_alias="recordId", serialization_alias="recordId", description="The unique identifier of the record to update.")
class PatchV0BaseidTableidornameRecordidRequestBody(StrictModel):
    typecast: bool | None = Field(default=None, description="Enable automatic data type conversion from string values when updating fields. Disabled by default to preserve data integrity, but useful when integrating with third-party data sources.")
    fields: dict[str, Any] = Field(default=..., description="An object containing the field values to update, keyed by field name or field ID. Only specified fields will be updated; all other fields remain unchanged.")
class PatchV0BaseidTableidornameRecordidRequest(StrictModel):
    """Partially update a single record in a table by specifying only the fields you want to change. Unspecified fields remain unchanged. Table names and IDs can be used interchangeably."""
    path: PatchV0BaseidTableidornameRecordidRequestPath
    body: PatchV0BaseidTableidornameRecordidRequestBody

# Operation: delete_record
class DeleteV0BaseidTableidornameRecordidRequestPath(StrictModel):
    base_id: str = Field(default=..., validation_alias="baseId", serialization_alias="baseId", description="The unique identifier of the base containing the table and record to delete.")
    table_id_or_name: str = Field(default=..., validation_alias="tableIdOrName", serialization_alias="tableIdOrName", description="The table identifier or name where the record is located. Can be specified by either the table's unique ID or its display name.")
    record_id: str = Field(default=..., validation_alias="recordId", serialization_alias="recordId", description="The unique identifier of the record to delete.")
class DeleteV0BaseidTableidornameRecordidRequest(StrictModel):
    """Permanently deletes a single record from a table. This action cannot be undone."""
    path: DeleteV0BaseidTableidornameRecordidRequestPath

# Operation: sync_table_data
class PostV0BaseidTableidornameSyncApiendpointsyncidRequestPath(StrictModel):
    base_id: str = Field(default=..., validation_alias="baseId", serialization_alias="baseId", description="The unique identifier for the base containing the table to sync.")
    table_id_or_name: str = Field(default=..., validation_alias="tableIdOrName", serialization_alias="tableIdOrName", description="The table identifier or name where the CSV data will be synced.")
    api_endpoint_sync_id: str = Field(default=..., validation_alias="apiEndpointSyncId", serialization_alias="apiEndpointSyncId", description="The API endpoint sync identifier, obtained from the Sync API table setup flow or the synced table settings.")
class PostV0BaseidTableidornameSyncApiendpointsyncidRequestBody(StrictModel):
    body: str = Field(default=..., description="Raw CSV data to sync into the table. Supports up to 10,000 rows and 500 columns, with a total request size not exceeding 2 MB.")
class PostV0BaseidTableidornameSyncApiendpointsyncidRequest(StrictModel):
    """Syncs CSV data into a Sync API table. The CSV can contain up to 10,000 rows and 500 columns, with a maximum HTTP request size of 2 MB per sync run."""
    path: PostV0BaseidTableidornameSyncApiendpointsyncidRequestPath
    body: PostV0BaseidTableidornameSyncApiendpointsyncidRequestBody

# Operation: upload_attachment
class PostV0BaseidRecordidAttachmentfieldidornameUploadattachmentRequestPath(StrictModel):
    base_id: str = Field(default=..., validation_alias="baseId", serialization_alias="baseId", description="The unique identifier of the base containing the record.")
    record_id: str = Field(default=..., validation_alias="recordId", serialization_alias="recordId", description="The unique identifier of the record where the attachment will be added.")
    attachment_field_id_or_name: str = Field(default=..., validation_alias="attachmentFieldIdOrName", serialization_alias="attachmentFieldIdOrName", description="The ID or name of the attachment field where the file will be uploaded.")
class PostV0BaseidRecordidAttachmentfieldidornameUploadattachmentRequestBody(StrictModel):
    content_type: str = Field(default=..., validation_alias="contentType", serialization_alias="contentType", description="The MIME type of the file being uploaded (e.g., image/jpeg, application/pdf, text/plain).")
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="The file content encoded as a base64 string. The decoded file size must not exceed 5 MB.")
    filename: str = Field(default=..., description="The name of the file including its extension (e.g., document.pdf, photo.jpg).")
class PostV0BaseidRecordidAttachmentfieldidornameUploadattachmentRequest(StrictModel):
    """Upload a file attachment (up to 5 MB) directly to an attachment field in a record. The file must be provided as base64-encoded bytes along with its content type and filename."""
    path: PostV0BaseidRecordidAttachmentfieldidornameUploadattachmentRequestPath
    body: PostV0BaseidRecordidAttachmentfieldidornameUploadattachmentRequestBody

# ============================================================================
# Component Models
# ============================================================================

class PatchV0BaseidTableidornameBodyRecordsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the record to update. Required when performUpsert is undefined.")
    fields: dict[str, Any] = Field(..., description="Object with field names or IDs as keys and cell values")

class PostV0BaseidTableidornameBodyRecordsItem(PermissiveModel):
    fields: dict[str, Any] = Field(..., description="Cell values keyed by field name or field id")

class PutV0BaseidTableidornameBodyRecordsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the record to update. Required when performUpsert is undefined.")
    fields: dict[str, Any] = Field(..., description="Object with field names or IDs as keys and cell values")


# Rebuild models to resolve forward references (required for circular refs)
PatchV0BaseidTableidornameBodyRecordsItem.model_rebuild()
PostV0BaseidTableidornameBodyRecordsItem.model_rebuild()
PutV0BaseidTableidornameBodyRecordsItem.model_rebuild()

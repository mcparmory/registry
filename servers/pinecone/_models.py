"""
Pinecone Control Plane Api MCP Server - Pydantic Models

Generated: 2026-04-10 13:58:24 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any

from _validators import PermissiveModel, StrictModel
from pydantic import Field, RootModel

__all__ = [
    "ConfigureIndexRequest",
    "CreateBackupRequest",
    "CreateCollectionRequest",
    "CreateIndexForModelRequest",
    "CreateIndexFromBackupOperationRequest",
    "CreateIndexRequest",
    "DeleteBackupRequest",
    "DeleteCollectionRequest",
    "DeleteIndexRequest",
    "DescribeBackupRequest",
    "DescribeCollectionRequest",
    "DescribeIndexRequest",
    "DescribeRestoreJobRequest",
    "ListCollectionsRequest",
    "ListIndexBackupsRequest",
    "ListIndexesRequest",
    "ListProjectBackupsRequest",
    "ListRestoreJobsRequest",
    "ConfigureIndexBodySpecV0",
    "ConfigureIndexBodySpecV1",
    "ConfigureIndexBodySpecV2",
    "CreateIndexBodySpecV0",
    "CreateIndexBodySpecV1",
    "CreateIndexBodySpecV2",
    "CreateIndexForModelBodySchemaFieldsValue",
    "ReadCapacityDedicatedSpec",
    "ReadCapacityOnDemandSpec",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_indexes
class ListIndexesRequestHeader(StrictModel):
    x_pinecone_api_version: str = Field(default=..., validation_alias="X-Pinecone-Api-Version", serialization_alias="X-Pinecone-Api-Version", description="API version specified as a date string in YYYY-MM format. Required for request routing and response formatting. Defaults to 2026-04 if not provided.")
class ListIndexesRequest(StrictModel):
    """Retrieve all indexes in the current project. Returns a list of index configurations and metadata."""
    header: ListIndexesRequestHeader

# Operation: create_index
class CreateIndexRequestHeader(StrictModel):
    x_pinecone_api_version: str = Field(default=..., validation_alias="X-Pinecone-Api-Version", serialization_alias="X-Pinecone-Api-Version", description="API version identifier in date format (e.g., 2026-04). Required for all requests to ensure compatibility.")
class CreateIndexRequestBody(StrictModel):
    """The desired configuration for the index."""
    name: str = Field(default=..., description="Unique name for the index (1-45 characters). Must start and end with an alphanumeric character and contain only lowercase letters, numbers, or hyphens.", min_length=1, max_length=45)
    dimension: int | None = Field(default=None, description="Number of dimensions for vectors stored in this index (1-20,000). Required for dense vector types. Omit for sparse vectors.", json_schema_extra={'format': 'int32'})
    metric: str | None = Field(default=None, description="Distance metric for similarity calculations: 'cosine' (default for dense vectors), 'euclidean', or 'dotproduct' (required for sparse vectors).")
    deletion_protection: str | None = Field(default=None, description="Enable or disable deletion protection for the index. When enabled, prevents accidental index removal. Defaults to disabled.")
    tags: dict[str, str] | None = Field(default=None, description="Optional custom metadata tags for organizing and identifying the index. Keys up to 80 characters (alphanumeric, underscore, hyphen); values up to 120 characters (alphanumeric, semicolon, at-sign, underscore, hyphen, period, plus, space). Set value to empty string to remove a tag.")
    spec: CreateIndexBodySpecV0 | CreateIndexBodySpecV1 | CreateIndexBodySpecV2 = Field(default=..., description="Deployment configuration specifying where and how the index runs. For serverless indexes, provide cloud provider and region. For pod-based indexes, specify environment, pod type, and pod size.")
    vector_type: str | None = Field(default=None, description="Vector type for the index: 'dense' (default, requires dimension specification) or 'sparse' (omit dimension specification).")
class CreateIndexRequest(StrictModel):
    """Create a new Pinecone index by specifying vector dimensions, similarity metric, deployment configuration, and optional metadata. This establishes the foundation for storing and searching vectors."""
    header: CreateIndexRequestHeader
    body: CreateIndexRequestBody

# Operation: get_index
class DescribeIndexRequestPath(StrictModel):
    index_name: str = Field(default=..., description="The name of the index to retrieve. Use the exact index name as it appears in your Pinecone project (e.g., 'test-index').")
class DescribeIndexRequestHeader(StrictModel):
    x_pinecone_api_version: str = Field(default=..., validation_alias="X-Pinecone-Api-Version", serialization_alias="X-Pinecone-Api-Version", description="API version specified as a date in YYYY-MM format. Defaults to 2026-04 if not provided; include this header to ensure compatibility with a specific API version.")
class DescribeIndexRequest(StrictModel):
    """Retrieve detailed metadata and configuration information about a specific index, including its dimensions, metric type, and current status."""
    path: DescribeIndexRequestPath
    header: DescribeIndexRequestHeader

# Operation: update_index
class ConfigureIndexRequestPath(StrictModel):
    index_name: str = Field(default=..., description="The name of the index to configure (e.g., 'test-index').")
class ConfigureIndexRequestHeader(StrictModel):
    x_pinecone_api_version: str = Field(default=..., validation_alias="X-Pinecone-Api-Version", serialization_alias="X-Pinecone-Api-Version", description="Required API version header in date-based format (defaults to 2026-04).")
class ConfigureIndexRequestBody(StrictModel):
    """The desired pod size and replica configuration for the index."""
    spec: ConfigureIndexBodySpecV0 | ConfigureIndexBodySpecV1 | ConfigureIndexBodySpecV2 | None = Field(default=None, description="The deployment specification for the index. Defines how the index is scaled and configured. Only modifiable attributes related to scaling and configuration are supported; cloud provider and region are immutable.")
    deletion_protection: str | None = Field(default=None, description="Enable or disable deletion protection for the index to prevent accidental removal. Defaults to disabled.")
    tags: dict[str, str] | None = Field(default=None, description="Custom key-value tags for organizing and labeling the index. Keys must be 80 characters or fewer and contain only alphanumeric characters, underscores, or hyphens. Values must be 120 characters or fewer and contain only alphanumeric characters, semicolons, at signs, underscores, hyphens, periods, plus signs, or spaces. Set a value to an empty string to remove a tag.")
class ConfigureIndexRequest(StrictModel):
    """Update configuration settings for an existing index, including scaling parameters, deletion protection, and custom tags. Only scaling and configuration attributes can be modified; the index's cloud provider and region cannot be changed."""
    path: ConfigureIndexRequestPath
    header: ConfigureIndexRequestHeader
    body: ConfigureIndexRequestBody | None = None

# Operation: delete_index
class DeleteIndexRequestPath(StrictModel):
    index_name: str = Field(default=..., description="The name of the index to delete (e.g., 'test-index'). Must match an existing index exactly.")
class DeleteIndexRequestHeader(StrictModel):
    x_pinecone_api_version: str = Field(default=..., validation_alias="X-Pinecone-Api-Version", serialization_alias="X-Pinecone-Api-Version", description="API version specified as a date string in YYYY-MM format (defaults to 2026-04). Required header for request routing.")
class DeleteIndexRequest(StrictModel):
    """Permanently delete an existing index and all its data. This operation cannot be undone."""
    path: DeleteIndexRequestPath
    header: DeleteIndexRequestHeader

# Operation: list_index_backups
class ListIndexBackupsRequestPath(StrictModel):
    index_name: str = Field(default=..., description="The name of the index for which to list backups.")
class ListIndexBackupsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of backup results to return per page. Must be between 1 and 100 (defaults to 10).", ge=1, le=100)
    pagination_token: str | None = Field(default=None, validation_alias="paginationToken", serialization_alias="paginationToken", description="Pagination token from a previous response to retrieve the next page of results.")
class ListIndexBackupsRequestHeader(StrictModel):
    x_pinecone_api_version: str = Field(default=..., validation_alias="X-Pinecone-Api-Version", serialization_alias="X-Pinecone-Api-Version", description="API version specified as a date string in YYYY-MM format (defaults to 2026-04). Required for request routing.")
class ListIndexBackupsRequest(StrictModel):
    """Retrieve all backups for a specified index with pagination support. Use pagination tokens to navigate through large result sets."""
    path: ListIndexBackupsRequestPath
    query: ListIndexBackupsRequestQuery | None = None
    header: ListIndexBackupsRequestHeader

# Operation: create_backup
class CreateBackupRequestPath(StrictModel):
    index_name: str = Field(default=..., description="The name of the index to back up. This identifies which index will be backed up.")
class CreateBackupRequestHeader(StrictModel):
    x_pinecone_api_version: str = Field(default=..., validation_alias="X-Pinecone-Api-Version", serialization_alias="X-Pinecone-Api-Version", description="The API version specified as a date-based header (required for all requests). Use the default version 2026-04 unless you need a specific earlier version.")
class CreateBackupRequestBody(StrictModel):
    """The desired configuration for the backup."""
    name: str | None = Field(default=None, description="An optional name for the backup. If provided, this will be used to identify the backup in your backup list.")
    description: str | None = Field(default=None, description="An optional description of the backup. Use this to document the purpose or context of the backup for future reference.")
class CreateBackupRequest(StrictModel):
    """Create a backup of a Pinecone index to preserve its current state. Backups can be named and described for easy identification and management."""
    path: CreateBackupRequestPath
    header: CreateBackupRequestHeader
    body: CreateBackupRequestBody | None = None

# Operation: list_collections
class ListCollectionsRequestHeader(StrictModel):
    x_pinecone_api_version: str = Field(default=..., validation_alias="X-Pinecone-Api-Version", serialization_alias="X-Pinecone-Api-Version", description="API version specified as a date string in YYYY-MM format. Required for all requests to ensure compatibility with the API specification.")
class ListCollectionsRequest(StrictModel):
    """Retrieve all collections in a project. Note that serverless indexes do not support collections."""
    header: ListCollectionsRequestHeader

# Operation: create_collection
class CreateCollectionRequestHeader(StrictModel):
    x_pinecone_api_version: str = Field(default=..., validation_alias="X-Pinecone-Api-Version", serialization_alias="X-Pinecone-Api-Version", description="API version specified as a date-based header in YYYY-MM format. Defaults to 2026-04 if not provided.")
class CreateCollectionRequestBody(StrictModel):
    """The desired configuration for the collection."""
    name: str = Field(default=..., description="The name for the new collection. Must be 1-45 characters long, start and end with an alphanumeric character, and contain only lowercase alphanumeric characters or hyphens.", min_length=1, max_length=45)
    source: str = Field(default=..., description="The name of an existing index to use as the source for this collection. The source index will provide the data and configuration for the collection.")
class CreateCollectionRequest(StrictModel):
    """Create a new collection in Pinecone by specifying a name and source index. Collections allow you to organize and manage data within an index (note: serverless indexes do not support collections)."""
    header: CreateCollectionRequestHeader
    body: CreateCollectionRequestBody

# Operation: create_index_for_model
class CreateIndexForModelRequestHeader(StrictModel):
    x_pinecone_api_version: str = Field(default=..., validation_alias="X-Pinecone-Api-Version", serialization_alias="X-Pinecone-Api-Version", description="API version identifier in date format (required header for all requests).")
class CreateIndexForModelRequestBodySchema(StrictModel):
    fields: dict[str, CreateIndexForModelBodySchemaFieldsValue] = Field(default=..., validation_alias="fields", serialization_alias="fields", description="Configuration map defining metadata field names and their types. Each field name must be unique and follow valid metadata field naming conventions.")
class CreateIndexForModelRequestBodyEmbed(StrictModel):
    model: str = Field(default=..., validation_alias="model", serialization_alias="model", description="Name of the hosted embedding model to use for automatic text vectorization (e.g., multilingual-e5-large). The model determines default vector dimensions and distance metrics.")
    metric: str | None = Field(default=None, validation_alias="metric", serialization_alias="metric", description="Distance metric for similarity search operations: cosine, euclidean, or dotproduct. If omitted, defaults based on the selected embedding model. Cannot be changed after index creation.")
    field_map: dict[str, Any] = Field(default=..., validation_alias="field_map", serialization_alias="field_map", description="Mapping that identifies which text field from your documents will be embedded. Specify the source field name that contains the text to vectorize.")
    dimension: int | None = Field(default=None, validation_alias="dimension", serialization_alias="dimension", description="Optional vector dimension size for embeddings. If not specified, the dimension is automatically determined by the selected embedding model.")
class CreateIndexForModelRequestBody(StrictModel):
    """The desired configuration for the index and associated embedding model."""
    name: str = Field(default=..., description="Unique name for the index. Must be 1-45 characters, start and end with alphanumeric characters, and contain only lowercase letters, numbers, or hyphens.", min_length=1, max_length=45)
    cloud: str = Field(default=..., description="Cloud provider where the index will be hosted: AWS, Google Cloud, or Azure.")
    region: str = Field(default=..., description="Geographic region for index deployment (e.g., us-east-1, europe-west1). Must be a valid region for your chosen cloud provider.")
    deletion_protection: str | None = Field(default=None, description="Enable or disable deletion protection to prevent accidental index removal. Defaults to disabled if not specified.")
    tags: dict[str, str] | None = Field(default=None, description="Optional custom key-value tags for organizing and identifying the index. Keys up to 80 characters, values up to 120 characters. Keys must be alphanumeric with underscores or hyphens; values support alphanumeric characters plus ';@_-.+' and spaces.")
    read_capacity: ReadCapacityOnDemandSpec | ReadCapacityDedicatedSpec | None = Field(default=None, description="Optional capacity configuration for read operations. Defaults to OnDemand mode; specify Dedicated mode with node_type and scaling parameters for predictable, reserved throughput.")
    schema_: CreateIndexForModelRequestBodySchema = Field(default=..., validation_alias="schema", serialization_alias="schema")
    embed: CreateIndexForModelRequestBodyEmbed
class CreateIndexForModelRequest(StrictModel):
    """Create a vector search index with integrated embedding capabilities. Pinecone automatically converts your source text using the specified hosted embedding model during data operations, eliminating the need for separate embedding infrastructure."""
    header: CreateIndexForModelRequestHeader
    body: CreateIndexForModelRequestBody

# Operation: list_project_backups
class ListProjectBackupsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of backups to return per page, between 1 and 100. Defaults to 10 results per page.", ge=1, le=100)
    pagination_token: str | None = Field(default=None, validation_alias="paginationToken", serialization_alias="paginationToken", description="Pagination token from a previous response to retrieve the next page of results.")
class ListProjectBackupsRequestHeader(StrictModel):
    x_pinecone_api_version: str = Field(default=..., validation_alias="X-Pinecone-Api-Version", serialization_alias="X-Pinecone-Api-Version", description="API version specified as a date-based string (defaults to 2026-04). Required header for API compatibility.")
class ListProjectBackupsRequest(StrictModel):
    """Retrieve all backups for indexes in a project with optional pagination. Use pagination tokens to navigate through large result sets."""
    query: ListProjectBackupsRequestQuery | None = None
    header: ListProjectBackupsRequestHeader

# Operation: get_backup
class DescribeBackupRequestPath(StrictModel):
    backup_id: str = Field(default=..., description="The unique identifier of the backup to retrieve, formatted as a UUID (e.g., 670e8400-e29b-41d4-a716-446655440000).")
class DescribeBackupRequestHeader(StrictModel):
    x_pinecone_api_version: str = Field(default=..., validation_alias="X-Pinecone-Api-Version", serialization_alias="X-Pinecone-Api-Version", description="API version specified as a date-based header to ensure compatibility with the Pinecone API. Defaults to 2026-04 if not provided.")
class DescribeBackupRequest(StrictModel):
    """Retrieve detailed information about a specific backup by its ID. Returns the backup's metadata and configuration."""
    path: DescribeBackupRequestPath
    header: DescribeBackupRequestHeader

# Operation: delete_backup
class DeleteBackupRequestPath(StrictModel):
    backup_id: str = Field(default=..., description="The unique identifier of the backup to delete, formatted as a UUID.")
class DeleteBackupRequestHeader(StrictModel):
    x_pinecone_api_version: str = Field(default=..., validation_alias="X-Pinecone-Api-Version", serialization_alias="X-Pinecone-Api-Version", description="API version specified as a date string in YYYY-MM format (defaults to 2026-04 if not provided).")
class DeleteBackupRequest(StrictModel):
    """Permanently delete a backup by its ID. This operation removes the backup and cannot be undone."""
    path: DeleteBackupRequestPath
    header: DeleteBackupRequestHeader

# Operation: create_index_from_backup
class CreateIndexFromBackupOperationRequestPath(StrictModel):
    backup_id: str = Field(default=..., description="The unique identifier of the backup to restore from, formatted as a UUID.")
class CreateIndexFromBackupOperationRequestHeader(StrictModel):
    x_pinecone_api_version: str = Field(default=..., validation_alias="X-Pinecone-Api-Version", serialization_alias="X-Pinecone-Api-Version", description="API version specified as a date string in YYYY-MM format (e.g., 2026-04). This header is required to ensure compatibility with the API version.")
class CreateIndexFromBackupOperationRequestBody(StrictModel):
    """The desired configuration for the index created from a backup."""
    name: str = Field(default=..., description="The name for the new index. Must be 1-45 characters long, start and end with an alphanumeric character, and contain only lowercase letters, numbers, or hyphens.", min_length=1, max_length=45)
    tags: dict[str, str] | None = Field(default=None, description="Optional custom metadata tags for organizing and identifying the index. Tag keys can be up to 80 characters and must contain only alphanumeric characters, underscores, or hyphens. Tag values can be up to 120 characters and may include alphanumeric characters, semicolons, at signs, underscores, hyphens, periods, plus signs, or spaces. Set a value to an empty string to remove a tag.")
    deletion_protection: str | None = Field(default=None, description="Optional setting to prevent accidental deletion of the index. Set to 'enabled' to protect the index or 'disabled' (default) to allow deletion.")
class CreateIndexFromBackupOperationRequest(StrictModel):
    """Create a new index by restoring data from an existing backup. The new index will be initialized with the backup's configuration and data."""
    path: CreateIndexFromBackupOperationRequestPath
    header: CreateIndexFromBackupOperationRequestHeader
    body: CreateIndexFromBackupOperationRequestBody

# Operation: list_restore_jobs
class ListRestoreJobsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of restore jobs to return per page, between 1 and 100 results. Defaults to 10 if not specified.", ge=1, le=100)
    pagination_token: str | None = Field(default=None, validation_alias="paginationToken", serialization_alias="paginationToken", description="Pagination token from a previous response to retrieve the next page of restore jobs. Omit for the first page.")
class ListRestoreJobsRequestHeader(StrictModel):
    x_pinecone_api_version: str = Field(default=..., validation_alias="X-Pinecone-Api-Version", serialization_alias="X-Pinecone-Api-Version", description="API version specified as a date string in YYYY-MM format. Required for all requests. Defaults to 2026-04.")
class ListRestoreJobsRequest(StrictModel):
    """Retrieve a paginated list of all restore jobs for the project. Use pagination tokens to navigate through results."""
    query: ListRestoreJobsRequestQuery | None = None
    header: ListRestoreJobsRequestHeader

# Operation: get_restore_job
class DescribeRestoreJobRequestPath(StrictModel):
    job_id: str = Field(default=..., description="The unique identifier of the restore job to retrieve, formatted as a UUID (e.g., 670e8400-e29b-41d4-a716-446655440000).")
class DescribeRestoreJobRequestHeader(StrictModel):
    x_pinecone_api_version: str = Field(default=..., validation_alias="X-Pinecone-Api-Version", serialization_alias="X-Pinecone-Api-Version", description="API version specified as a date-based header to ensure compatibility with the Pinecone API. Defaults to 2026-04 if not provided.")
class DescribeRestoreJobRequest(StrictModel):
    """Retrieve detailed information about a specific restore job, including its status, progress, and configuration."""
    path: DescribeRestoreJobRequestPath
    header: DescribeRestoreJobRequestHeader

# Operation: get_collection
class DescribeCollectionRequestPath(StrictModel):
    collection_name: str = Field(default=..., description="The name of the collection to retrieve information about (e.g., 'tiny-collection').")
class DescribeCollectionRequestHeader(StrictModel):
    x_pinecone_api_version: str = Field(default=..., validation_alias="X-Pinecone-Api-Version", serialization_alias="X-Pinecone-Api-Version", description="API version specified as a date-based header in YYYY-MM format (defaults to 2026-04 if not provided).")
class DescribeCollectionRequest(StrictModel):
    """Retrieve detailed metadata and configuration information about a specific collection. Note that serverless indexes do not support collections."""
    path: DescribeCollectionRequestPath
    header: DescribeCollectionRequestHeader

# Operation: delete_collection
class DeleteCollectionRequestPath(StrictModel):
    collection_name: str = Field(default=..., description="The name of the collection to delete (e.g., 'test-collection'). This is a required identifier that specifies which collection will be removed.")
class DeleteCollectionRequestHeader(StrictModel):
    x_pinecone_api_version: str = Field(default=..., validation_alias="X-Pinecone-Api-Version", serialization_alias="X-Pinecone-Api-Version", description="Required API version header in date-based format (defaults to 2026-04). This ensures the request is processed with the correct API specification.")
class DeleteCollectionRequest(StrictModel):
    """Permanently delete an existing collection and all its data. Note that serverless indexes do not support collections."""
    path: DeleteCollectionRequestPath
    header: DeleteCollectionRequestHeader

# ============================================================================
# Component Models
# ============================================================================

class ConfigureIndexBodySpecV1Pod(PermissiveModel):
    """Updated configuration for pod-based indexes"""
    replicas: int | None = Field(1, description="The number of replicas. Replicas duplicate your index. They provide higher availability and throughput. Replicas can be scaled up or down as your needs change.", ge=1, json_schema_extra={'format': 'int32'})
    pod_type: str | None = Field('p1.x1', description="The type of pod to use. One of `s1`, `p1`, or `p2` appended with `.` and one of `x1`, `x2`, `x4`, or `x8`.")

class ConfigureIndexBodySpecV1(StrictModel):
    pod: ConfigureIndexBodySpecV1Pod = Field(..., description="Updated configuration for pod-based indexes")

class ConfigureIndexRequestEmbed(PermissiveModel):
    """Configure the integrated inference embedding settings for this index.

You can convert an existing index to an integrated index by specifying the embedding model and field_map. The index vector type and dimension must match the model vector type and dimension, and the index similarity metric must be supported by the model. Refer to the [model guide](https://docs.pinecone.io/guides/index-data/create-an-index#embedding-models) for available models and model details.

You can later change the embedding configuration to update the field map, read parameters, or write parameters. Once set, the model cannot be changed."""
    model: str | None = Field(None, description="The name of the embedding model to use with the index. The index dimension and model dimension must match, and the index similarity metric must be supported by the model. The index embedding model cannot be changed once set.")
    field_map: dict[str, Any] | None = Field(None, description="Identifies the name of the text field from your document model that will be embedded.")
    read_parameters: dict[str, Any] | None = Field(None, description="The read parameters for the embedding model.")
    write_parameters: dict[str, Any] | None = Field(None, description="The write parameters for the embedding model.")

class ConfigureIndexRequestSpecV1Pod(PermissiveModel):
    """Updated configuration for pod-based indexes"""
    replicas: int | None = Field(1, description="The number of replicas. Replicas duplicate your index. They provide higher availability and throughput. Replicas can be scaled up or down as your needs change.", ge=1, json_schema_extra={'format': 'int32'})
    pod_type: str | None = Field('p1.x1', description="The type of pod to use. One of `s1`, `p1`, or `p2` appended with `.` and one of `x1`, `x2`, `x4`, or `x8`.")

class ConfigureIndexRequestSpecV1(StrictModel):
    pod: ConfigureIndexRequestSpecV1Pod = Field(..., description="Updated configuration for pod-based indexes")

class CreateIndexBodySpecV0ServerlessSchemaFieldsValue(PermissiveModel):
    filterable: bool | None = Field(None, description="Whether the field is filterable. If true, the field is indexed and can be used in filters. Only true values are allowed.")

class CreateIndexBodySpecV0ServerlessSchema(PermissiveModel):
    """Schema for the behavior of Pinecone's internal metadata index. By default, all metadata is indexed; when `schema` is present, only fields which are present in the `fields` object with a `filterable: true` are indexed. Note that `filterable: false` is not currently supported."""
    fields: dict[str, CreateIndexBodySpecV0ServerlessSchemaFieldsValue] = Field(..., description="A map of metadata field names to their configuration. The field name must be a valid metadata field name. The field name must be unique.")

class CreateIndexBodySpecV1PodMetadataConfig(PermissiveModel):
    """Configuration for the behavior of Pinecone's internal metadata index. By default, all metadata is indexed; when `metadata_config` is present, only specified metadata fields are indexed. These configurations are only valid for use with pod-based indexes."""
    indexed: list[str] | None = Field(None, description="By default, all metadata is indexed; to change this behavior, use this property to specify an array of metadata fields that should be indexed.")

class CreateIndexBodySpecV1Pod(PermissiveModel):
    """Configuration needed to deploy a pod-based index."""
    environment: str = Field(..., description="The environment where the index is hosted.")
    replicas: int | None = Field(1, description="The number of replicas. Replicas duplicate your index. They provide higher availability and throughput. Replicas can be scaled up or down as your needs change.", ge=1, json_schema_extra={'format': 'int32'})
    shards: int | None = Field(1, description="The number of shards. Shards split your data across multiple pods so you can fit more data into an index.", ge=1, json_schema_extra={'format': 'int32'})
    pod_type: str = Field(..., description="The type of pod to use. One of `s1`, `p1`, or `p2` appended with `.` and one of `x1`, `x2`, `x4`, or `x8`.")
    pods: int | None = Field(1, description="The number of pods to be used in the index. This should be equal to `shards` x `replicas`.'", ge=1)
    metadata_config: CreateIndexBodySpecV1PodMetadataConfig | None = Field(None, description="Configuration for the behavior of Pinecone's internal metadata index. By default, all metadata is indexed; when `metadata_config` is present, only specified metadata fields are indexed. These configurations are only valid for use with pod-based indexes.")
    source_collection: str | None = Field(None, description="The name of the collection to be used as the source for the index.")

class CreateIndexBodySpecV1(StrictModel):
    pod: CreateIndexBodySpecV1Pod = Field(..., description="Configuration needed to deploy a pod-based index.")

class CreateIndexBodySpecV2ByocSchemaFieldsValue(PermissiveModel):
    filterable: bool | None = Field(None, description="Whether the field is filterable. If true, the field is indexed and can be used in filters. Only true values are allowed.")

class CreateIndexBodySpecV2ByocSchema(PermissiveModel):
    """Schema for the behavior of Pinecone's internal metadata index. By default, all metadata is indexed; when `schema` is present, only fields which are present in the `fields` object with a `filterable: true` are indexed. Note that `filterable: false` is not currently supported."""
    fields: dict[str, CreateIndexBodySpecV2ByocSchemaFieldsValue] = Field(..., description="A map of metadata field names to their configuration. The field name must be a valid metadata field name. The field name must be unique.")

class CreateIndexForModelBodySchemaFieldsValue(PermissiveModel):
    filterable: bool | None = Field(None, description="Whether the field is filterable. If true, the field is indexed and can be used in filters. Only true values are allowed.")

class CreateIndexForModelRequestEmbed(PermissiveModel):
    """Specify the integrated inference embedding configuration for the index.

Once set the model cannot be changed, but you can later update the embedding configuration for an integrated inference index including field map, read parameters, or write parameters.

Refer to the [model guide](https://docs.pinecone.io/guides/index-data/create-an-index#embedding-models) for available models and model details."""
    model: str = Field(..., description="The name of the embedding model to use for the index.")
    metric: str | None = Field(None, description="The distance metric to be used for similarity search. You can use 'euclidean', 'cosine', or 'dotproduct'. If not specified, the metric will be defaulted according to the model. Cannot be updated once set.\nPossible values: `cosine`, `euclidean`, or `dotproduct`.")
    field_map: dict[str, Any] = Field(..., description="Identifies the name of the text field from your document model that will be embedded.")
    dimension: int | None = Field(None, description="The dimension of embedding vectors produced for the index.")
    read_parameters: dict[str, Any] | None = Field(None, description="The read parameters for the embedding model.")
    write_parameters: dict[str, Any] | None = Field(None, description="The write parameters for the embedding model.")

class IndexTags(RootModel[dict[str, str]]):
    pass

class MetadataSchemaFieldsValue(PermissiveModel):
    filterable: bool | None = Field(None, description="Whether the field is filterable. If true, the field is indexed and can be used in filters. Only true values are allowed.")

class MetadataSchema(PermissiveModel):
    """Schema for the behavior of Pinecone's internal metadata index. By default, all metadata is indexed; when `schema` is present, only fields which are present in the `fields` object with a `filterable: true` are indexed. Note that `filterable: false` is not currently supported."""
    fields: dict[str, MetadataSchemaFieldsValue] = Field(..., description="A map of metadata field names to their configuration. The field name must be a valid metadata field name. The field name must be unique.")

class PodSpecMetadataConfig(PermissiveModel):
    """Configuration for the behavior of Pinecone's internal metadata index. By default, all metadata is indexed; when `metadata_config` is present, only specified metadata fields are indexed. These configurations are only valid for use with pod-based indexes."""
    indexed: list[str] | None = Field(None, description="By default, all metadata is indexed; to change this behavior, use this property to specify an array of metadata fields that should be indexed.")

class PodSpec(PermissiveModel):
    """Configuration needed to deploy a pod-based index."""
    environment: str = Field(..., description="The environment where the index is hosted.")
    replicas: int | None = Field(1, description="The number of replicas. Replicas duplicate your index. They provide higher availability and throughput. Replicas can be scaled up or down as your needs change.", ge=1, json_schema_extra={'format': 'int32'})
    shards: int | None = Field(1, description="The number of shards. Shards split your data across multiple pods so you can fit more data into an index.", ge=1, json_schema_extra={'format': 'int32'})
    pod_type: str = Field(..., description="The type of pod to use. One of `s1`, `p1`, or `p2` appended with `.` and one of `x1`, `x2`, `x4`, or `x8`.")
    pods: int | None = Field(1, description="The number of pods to be used in the index. This should be equal to `shards` x `replicas`.'", ge=1)
    metadata_config: PodSpecMetadataConfig | None = Field(None, description="Configuration for the behavior of Pinecone's internal metadata index. By default, all metadata is indexed; when `metadata_config` is present, only specified metadata fields are indexed. These configurations are only valid for use with pod-based indexes.")
    source_collection: str | None = Field(None, description="The name of the collection to be used as the source for the index.")

class IndexSpecV1(StrictModel):
    pod: PodSpec

class ReadCapacityOnDemandSpec(StrictModel):
    mode: str = Field(..., description="The mode of the index. Possible values: `OnDemand` or `Dedicated`. Defaults to `OnDemand`. If set to `Dedicated`, `dedicated.node_type`, and `dedicated.scaling` must be specified.")

class ScalingConfigManual(PermissiveModel):
    """The config to use for manual read capacity scaling."""
    replicas: int | None = Field(None, description="The number of replicas to use. Replicas duplicate the compute resources and data of an index, allowing higher query throughput and availability. Setting replicas to 0 disables the index but can be used to reduce costs while usage is paused.", ge=0, json_schema_extra={'format': 'int32'})
    shards: int | None = Field(None, description="The number of shards to use. Shards determine the storage capacity of an index, with each shard providing 250 GB of storage.", ge=1, json_schema_extra={'format': 'int32'})

class ReadCapacityDedicatedConfig(PermissiveModel):
    """Configuration for dedicated read capacity. See  [this guide](https://docs.pinecone.io/guides/index-data/dedicated-read-nodes) for more details on  how to configure dedicated read capacity."""
    node_type: str | None = Field(None, description="The type of machines to use. Available options: `b1` and `t1`. `t1` includes increased processing power and memory.")
    scaling: str | None = Field(None, description="The type of scaling strategy to use.")
    manual: ScalingConfigManual | None = None

class ReadCapacityDedicatedSpec(PermissiveModel):
    mode: str = Field(..., description="The mode of the index. Possible values: `OnDemand` or `Dedicated`. Defaults to `OnDemand`. If set to `Dedicated`, `dedicated.node_type`, and `dedicated.scaling` must be specified.")
    dedicated: ReadCapacityDedicatedConfig

class ConfigureIndexBodySpecV0Serverless(PermissiveModel):
    """Updated configuration for serverless indexes"""
    read_capacity: ReadCapacityOnDemandSpec | ReadCapacityDedicatedSpec | None = Field(None, description="By default the index will be created with read capacity  mode `OnDemand`. If you prefer to allocate dedicated read  nodes for your workload, you must specify mode `Dedicated` and additional configurations for `node_type` and `scaling`.")

class ConfigureIndexBodySpecV0(StrictModel):
    serverless: ConfigureIndexBodySpecV0Serverless = Field(..., description="Updated configuration for serverless indexes")

class ConfigureIndexBodySpecV2Byoc(PermissiveModel):
    """Updated configuration for a BYOC index"""
    read_capacity: ReadCapacityOnDemandSpec | ReadCapacityDedicatedSpec | None = Field(None, description="By default the index will be created with read capacity  mode `OnDemand`. If you prefer to allocate dedicated read  nodes for your workload, you must specify mode `Dedicated` and additional configurations for `node_type` and `scaling`.")

class ConfigureIndexBodySpecV2(StrictModel):
    byoc: ConfigureIndexBodySpecV2Byoc = Field(..., description="Updated configuration for a BYOC index")

class CreateIndexBodySpecV0Serverless(PermissiveModel):
    """Configuration needed to deploy a serverless index."""
    cloud: str = Field(..., description="The public cloud where you would like your index hosted.\nPossible values: `gcp`, `aws`, or `azure`.")
    region: str = Field(..., description="The region where you would like your index to be created.")
    read_capacity: ReadCapacityOnDemandSpec | ReadCapacityDedicatedSpec | None = Field(None, description="By default the index will be created with read capacity  mode `OnDemand`. If you prefer to allocate dedicated read  nodes for your workload, you must specify mode `Dedicated` and additional configurations for `node_type` and `scaling`.")
    source_collection: str | None = Field(None, description="The name of the collection to be used as the source for the index.")
    schema_: CreateIndexBodySpecV0ServerlessSchema | None = Field(None, validation_alias="schema", serialization_alias="schema", description="Schema for the behavior of Pinecone's internal metadata index. By default, all metadata is indexed; when `schema` is present, only fields which are present in the `fields` object with a `filterable: true` are indexed. Note that `filterable: false` is not currently supported.")

class CreateIndexBodySpecV0(StrictModel):
    serverless: CreateIndexBodySpecV0Serverless = Field(..., description="Configuration needed to deploy a serverless index.")

class CreateIndexBodySpecV2Byoc(PermissiveModel):
    """Configuration needed to deploy an index in a BYOC environment."""
    environment: str = Field(..., description="The environment where the index is hosted.")
    read_capacity: ReadCapacityOnDemandSpec | ReadCapacityDedicatedSpec | None = Field(None, description="By default the index will be created with read capacity  mode `OnDemand`. If you prefer to allocate dedicated read  nodes for your workload, you must specify mode `Dedicated` and additional configurations for `node_type` and `scaling`.")
    schema_: CreateIndexBodySpecV2ByocSchema | None = Field(None, validation_alias="schema", serialization_alias="schema", description="Schema for the behavior of Pinecone's internal metadata index. By default, all metadata is indexed; when `schema` is present, only fields which are present in the `fields` object with a `filterable: true` are indexed. Note that `filterable: false` is not currently supported.")

class CreateIndexBodySpecV2(StrictModel):
    byoc: CreateIndexBodySpecV2Byoc = Field(..., description="Configuration needed to deploy an index in a BYOC environment.")

class ReadCapacity(PermissiveModel):
    """By default the index will be created with read capacity  mode `OnDemand`. If you prefer to allocate dedicated read  nodes for your workload, you must specify mode `Dedicated` and additional configurations for `node_type` and `scaling`."""
    read_capacity: ReadCapacityOnDemandSpec | ReadCapacityDedicatedSpec

class ByocSpec(PermissiveModel):
    """Configuration needed to deploy an index in a BYOC environment."""
    environment: str = Field(..., description="The environment where the index is hosted.")
    read_capacity: ReadCapacity | None = None
    schema_: MetadataSchema | None = Field(None, validation_alias="schema", serialization_alias="schema")

class ConfigureIndexRequestSpecV0Serverless(PermissiveModel):
    """Updated configuration for serverless indexes"""
    read_capacity: ReadCapacity | None = None

class ConfigureIndexRequestSpecV0(StrictModel):
    serverless: ConfigureIndexRequestSpecV0Serverless = Field(..., description="Updated configuration for serverless indexes")

class ConfigureIndexRequestSpecV2Byoc(PermissiveModel):
    """Updated configuration for a BYOC index"""
    read_capacity: ReadCapacity | None = None

class ConfigureIndexRequestSpecV2(StrictModel):
    byoc: ConfigureIndexRequestSpecV2Byoc = Field(..., description="Updated configuration for a BYOC index")

class IndexSpecV2(StrictModel):
    byoc: ByocSpec

class ServerlessSpec(PermissiveModel):
    """Configuration needed to deploy a serverless index."""
    cloud: str = Field(..., description="The public cloud where you would like your index hosted.\nPossible values: `gcp`, `aws`, or `azure`.")
    region: str = Field(..., description="The region where you would like your index to be created.")
    read_capacity: ReadCapacity | None = None
    source_collection: str | None = Field(None, description="The name of the collection to be used as the source for the index.")
    schema_: MetadataSchema | None = Field(None, validation_alias="schema", serialization_alias="schema")

class IndexSpecV0(StrictModel):
    serverless: ServerlessSpec

class IndexSpec(PermissiveModel):
    """The spec object defines how the index should be deployed.

For serverless indexes, you define only the [cloud and region](http://docs.pinecone.io/guides/index-data/create-an-index#cloud-regions) where the index should be hosted. For pod-based indexes, you define the [environment](http://docs.pinecone.io/guides/indexes/pods/understanding-pod-based-indexes#pod-environments) where the index should be hosted, the [pod type and size](http://docs.pinecone.io/guides/indexes/pods/understanding-pod-based-indexes#pod-types) to use, and other index characteristics.
"""
    index_spec: IndexSpecV0 | IndexSpecV1 | IndexSpecV2


# Rebuild models to resolve forward references (required for circular refs)
ByocSpec.model_rebuild()
ConfigureIndexBodySpecV0.model_rebuild()
ConfigureIndexBodySpecV0Serverless.model_rebuild()
ConfigureIndexBodySpecV1.model_rebuild()
ConfigureIndexBodySpecV1Pod.model_rebuild()
ConfigureIndexBodySpecV2.model_rebuild()
ConfigureIndexBodySpecV2Byoc.model_rebuild()
ConfigureIndexRequestEmbed.model_rebuild()
ConfigureIndexRequestSpecV0.model_rebuild()
ConfigureIndexRequestSpecV0Serverless.model_rebuild()
ConfigureIndexRequestSpecV1.model_rebuild()
ConfigureIndexRequestSpecV1Pod.model_rebuild()
ConfigureIndexRequestSpecV2.model_rebuild()
ConfigureIndexRequestSpecV2Byoc.model_rebuild()
CreateIndexBodySpecV0.model_rebuild()
CreateIndexBodySpecV0Serverless.model_rebuild()
CreateIndexBodySpecV0ServerlessSchema.model_rebuild()
CreateIndexBodySpecV0ServerlessSchemaFieldsValue.model_rebuild()
CreateIndexBodySpecV1.model_rebuild()
CreateIndexBodySpecV1Pod.model_rebuild()
CreateIndexBodySpecV1PodMetadataConfig.model_rebuild()
CreateIndexBodySpecV2.model_rebuild()
CreateIndexBodySpecV2Byoc.model_rebuild()
CreateIndexBodySpecV2ByocSchema.model_rebuild()
CreateIndexBodySpecV2ByocSchemaFieldsValue.model_rebuild()
CreateIndexForModelBodySchemaFieldsValue.model_rebuild()
CreateIndexForModelRequestEmbed.model_rebuild()
IndexSpec.model_rebuild()
IndexSpecV0.model_rebuild()
IndexSpecV1.model_rebuild()
IndexSpecV2.model_rebuild()
IndexTags.model_rebuild()
MetadataSchema.model_rebuild()
MetadataSchemaFieldsValue.model_rebuild()
PodSpec.model_rebuild()
PodSpecMetadataConfig.model_rebuild()
ReadCapacity.model_rebuild()
ReadCapacityDedicatedConfig.model_rebuild()
ReadCapacityDedicatedSpec.model_rebuild()
ReadCapacityOnDemandSpec.model_rebuild()
ScalingConfigManual.model_rebuild()
ServerlessSpec.model_rebuild()

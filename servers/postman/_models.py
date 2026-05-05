"""
Postman MCP Server - Pydantic Models

Generated: 2026-05-05 16:01:50 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "CreateAForkRequest",
    "CreateApiRequest",
    "CreateApiVersionRequest",
    "CreateCollectionFromSchemaRequest",
    "CreateCollectionRequest",
    "CreateEnvironmentRequest",
    "CreateMockRequest",
    "CreateMonitorRequest",
    "CreateRelationsRequest",
    "CreateSchemaRequest",
    "CreateWebhookRequest",
    "CreateWorkspaceRequest",
    "DeleteAnApiRequest",
    "DeleteAnApiVersionRequest",
    "DeleteCollectionRequest",
    "DeleteEnvironmentRequest",
    "DeleteMockRequest",
    "DeleteMonitorRequest",
    "DeleteWorkspaceRequest",
    "GetAllApIsRequest",
    "GetAllApiVersionsRequest",
    "GetAnApiVersionRequest",
    "GetContractTestRelationsRequest",
    "GetDocumentationRelationsRequest",
    "GetEnvironmentRelationsRequest",
    "GetIntegrationTestRelationsRequest",
    "GetLinkedRelationsRequest",
    "GetMonitorRelationsRequest",
    "GetSchemaRequest",
    "GetTestSuiteRelationsRequest",
    "MergeAForkRequest",
    "PublishMockRequest",
    "RunAMonitorRequest",
    "SingleApiRequest",
    "SingleCollectionRequest",
    "SingleEnvironmentRequest",
    "SingleMockRequest",
    "SingleMonitorRequest",
    "SingleWorkspaceRequest",
    "SyncRelationsWithSchemaRequest",
    "UnpublishMockRequest",
    "UpdateAnApiRequest",
    "UpdateAnApiVersionRequest",
    "UpdateCollectionRequest",
    "UpdateEnvironmentRequest",
    "UpdateMockRequest",
    "UpdateMonitorRequest",
    "UpdateSchemaRequest",
    "UpdateWorkspaceRequest",
    "CreateCollectionBodyCollectionItemItem",
    "CreateCollectionFromSchemaBodyRelationsItem",
    "CreateEnvironmentBodyEnvironmentValuesItem",
    "CreateWorkspaceBodyWorkspaceCollectionsItem",
    "CreateWorkspaceBodyWorkspaceEnvironmentsItem",
    "CreateWorkspaceBodyWorkspaceMocksItem",
    "CreateWorkspaceBodyWorkspaceMonitorsItem",
    "UpdateCollectionBodyCollectionItemItem",
    "UpdateEnvironmentBodyEnvironmentValuesItem",
    "UpdateWorkspaceBodyWorkspaceCollectionsItem",
    "UpdateWorkspaceBodyWorkspaceEnvironmentsItem",
    "UpdateWorkspaceBodyWorkspaceMocksItem",
    "UpdateWorkspaceBodyWorkspaceMonitorsItem",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_apis
class GetAllApIsRequestQuery(StrictModel):
    workspace: str | None = Field(default=None, description="Filter results to APIs within a specific workspace. Provide the workspace ID to scope the query.")
    since: str | None = Field(default=None, description="Filter results to APIs updated on or after this timestamp. Use ISO 8601 date-time format.")
    until: str | None = Field(default=None, description="Filter results to APIs updated on or before this timestamp. Use ISO 8601 date-time format.")
    created_by: str | None = Field(default=None, validation_alias="createdBy", serialization_alias="createdBy", description="Filter results to APIs created by a specific user. Provide the user ID.")
    updated_by: str | None = Field(default=None, validation_alias="updatedBy", serialization_alias="updatedBy", description="Filter results to APIs last updated by a specific user. Provide the user ID.")
    is_public: str | None = Field(default=None, validation_alias="isPublic", serialization_alias="isPublic", description="Filter results by privacy state: use true for public APIs or false for private APIs.")
    name: str | None = Field(default=None, description="Filter results to APIs whose name contains this value. Matching is case-insensitive.")
    summary: str | None = Field(default=None, description="Filter results to APIs whose summary contains this value. Matching is case-insensitive.")
    description: str | None = Field(default=None, description="Filter results to APIs whose description contains this value. Matching is case-insensitive.")
    sort: str | None = Field(default=None, description="Sort results by a specific field name from the response. Combine with direction parameter to control sort order.")
    direction: str | None = Field(default=None, description="Set sort order to ascending (asc) or descending (desc). Defaults to descending for timestamps and numeric fields, ascending otherwise.")
class GetAllApIsRequest(StrictModel):
    """Retrieve all APIs in a workspace with optional filtering by metadata, timestamps, privacy state, and text search. Results can be sorted by any response field in ascending or descending order."""
    query: GetAllApIsRequestQuery | None = None

# Operation: create_api
class CreateApiRequestQuery(StrictModel):
    workspace: str | None = Field(default=None, description="The workspace ID where the API will be created. If not specified, the API is created in the default workspace.")
class CreateApiRequestBodyApi(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A detailed description of the API's purpose and functionality.")
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The name of the API. This is a required field and must be provided in the request body.")
    summary: str | None = Field(default=None, validation_alias="summary", serialization_alias="summary", description="A short summary of the API's purpose. Should be concise and suitable for display in API listings.")
class CreateApiRequestBody(StrictModel):
    api: CreateApiRequestBodyApi | None = None
class CreateApiRequest(StrictModel):
    """Creates a new API with a default API Version. The request must include an `api` object with at least a `name` property, and returns the created API with full details including id, name, summary, and description."""
    query: CreateApiRequestQuery | None = None
    body: CreateApiRequestBody | None = None

# Operation: get_api
class SingleApiRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API to retrieve.")
class SingleApiRequest(StrictModel):
    """Retrieve detailed information about a specific API by its ID, including metadata such as name, summary, and description."""
    path: SingleApiRequestPath

# Operation: update_api
class UpdateAnApiRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API to update.")
class UpdateAnApiRequestBodyApi(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="The updated description for the API. Provide a clear, concise explanation of what the API does.")
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The updated name for the API. Use a descriptive title that identifies the API's purpose.")
class UpdateAnApiRequestBody(StrictModel):
    api: UpdateAnApiRequestBodyApi | None = None
class UpdateAnApiRequest(StrictModel):
    """Update an existing API by modifying its name, summary, or description. Returns the complete updated API object with all current details."""
    path: UpdateAnApiRequestPath
    body: UpdateAnApiRequestBody | None = None

# Operation: delete_api
class DeleteAnApiRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API to delete.")
class DeleteAnApiRequest(StrictModel):
    """Permanently deletes an API by its ID. Returns the deleted API object with its ID for confirmation."""
    path: DeleteAnApiRequestPath

# Operation: list_api_versions
class GetAllApiVersionsRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API for which to retrieve all versions.")
class GetAllApiVersionsRequest(StrictModel):
    """Retrieve all versions of a specified API, including detailed metadata for each version."""
    path: GetAllApiVersionsRequestPath

# Operation: create_api_version
class CreateApiVersionRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API in which to create the new version.")
class CreateApiVersionRequestBodyVersionSourceRelations(StrictModel):
    documentation: bool | None = Field(default=None, validation_alias="documentation", serialization_alias="documentation", description="When true, copies the API schema (specification/definition) from the source API version to the new version.")
    mock: bool | None = Field(default=None, validation_alias="mock", serialization_alias="mock", description="When true, copies mock server configurations from the source API version to the new version.")
    monitor: bool | None = Field(default=None, validation_alias="monitor", serialization_alias="monitor", description="When true, copies monitoring configurations from the source API version to the new version.")
class CreateApiVersionRequestBodyVersionSource(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of an existing API version to copy configuration and resources from. When specified, the new version will inherit selected schema and relations from this source version.")
    relations: CreateApiVersionRequestBodyVersionSourceRelations | None = None
class CreateApiVersionRequestBodyVersion(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The name for the new API version (e.g., '1.0', '2.0-beta'). Required when creating a version from scratch.")
    source: CreateApiVersionRequestBodyVersionSource | None = None
class CreateApiVersionRequestBody(StrictModel):
    version: CreateApiVersionRequestBodyVersion | None = None
class CreateApiVersionRequest(StrictModel):
    """Creates a new API version within the specified API. Optionally copies schema and related resources (mocks, monitors, documentation, tests, etc.) from an existing API version."""
    path: CreateApiVersionRequestPath
    body: CreateApiVersionRequestBody | None = None

# Operation: get_api_version
class GetAnApiVersionRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API containing the version to retrieve.")
    api_version_id: str = Field(default=..., validation_alias="apiVersionId", serialization_alias="apiVersionId", description="The unique identifier of the specific API version to fetch.")
class GetAnApiVersionRequest(StrictModel):
    """Retrieve detailed information about a specific API version, including its configuration and metadata."""
    path: GetAnApiVersionRequestPath

# Operation: update_api_version
class UpdateAnApiVersionRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API containing the version to update.")
    api_version_id: str = Field(default=..., validation_alias="apiVersionId", serialization_alias="apiVersionId", description="The unique identifier of the API version to update.")
class UpdateAnApiVersionRequestBodyVersion(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The new name for the API version (e.g., '2.0'). This is the only field that can be updated.")
class UpdateAnApiVersionRequestBody(StrictModel):
    version: UpdateAnApiVersionRequestBodyVersion | None = None
class UpdateAnApiVersionRequest(StrictModel):
    """Update the name of an existing API version. Provide the API ID and version ID, along with the new name in the request body."""
    path: UpdateAnApiVersionRequestPath
    body: UpdateAnApiVersionRequestBody | None = None

# Operation: delete_api_version
class DeleteAnApiVersionRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API containing the version to delete.")
    api_version_id: str = Field(default=..., validation_alias="apiVersionId", serialization_alias="apiVersionId", description="The unique identifier of the API version to delete.")
class DeleteAnApiVersionRequest(StrictModel):
    """Permanently deletes a specific API version. Returns the id of the deleted API version."""
    path: DeleteAnApiVersionRequestPath

# Operation: list_contract_test_relations
class GetContractTestRelationsRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API for which to fetch contract test relations.")
    api_version_id: str = Field(default=..., validation_alias="apiVersionId", serialization_alias="apiVersionId", description="The unique identifier of the specific API version for which to fetch contract test relations.")
class GetContractTestRelationsRequest(StrictModel):
    """Retrieves all contract test relations linked to a specific API version, organized by relation type with complete details for each relation."""
    path: GetContractTestRelationsRequestPath

# Operation: get_documentation_relations
class GetDocumentationRelationsRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API for which to fetch documentation relations.")
    api_version_id: str = Field(default=..., validation_alias="apiVersionId", serialization_alias="apiVersionId", description="The unique identifier of the API version for which to fetch documentation relations.")
class GetDocumentationRelationsRequest(StrictModel):
    """Retrieves all documentation relations linked to a specific API version, organized by relation type with complete details for each relation."""
    path: GetDocumentationRelationsRequestPath

# Operation: get_environment_relations_for_api_version
class GetEnvironmentRelationsRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API for which to retrieve environment relations.")
    api_version_id: str = Field(default=..., validation_alias="apiVersionId", serialization_alias="apiVersionId", description="The unique identifier of the specific API version for which to retrieve environment relations.")
class GetEnvironmentRelationsRequest(StrictModel):
    """Retrieves all environment relations linked to a specific API version, organized by relation type with complete details for each relation."""
    path: GetEnvironmentRelationsRequestPath

# Operation: list_integration_test_relations
class GetIntegrationTestRelationsRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API for which to fetch integration test relations.")
    api_version_id: str = Field(default=..., validation_alias="apiVersionId", serialization_alias="apiVersionId", description="The unique identifier of the API version for which to fetch integration test relations.")
class GetIntegrationTestRelationsRequest(StrictModel):
    """Retrieves all integration test relations linked to a specific API version, organized by relation type with complete details for each relation."""
    path: GetIntegrationTestRelationsRequestPath

# Operation: list_monitor_relations
class GetMonitorRelationsRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API.")
    api_version_id: str = Field(default=..., validation_alias="apiVersionId", serialization_alias="apiVersionId", description="The unique identifier of the API version for which to fetch monitor relations.")
class GetMonitorRelationsRequest(StrictModel):
    """Retrieves all monitor relations linked to a specific API version, organized by relation type with complete details for each relation."""
    path: GetMonitorRelationsRequestPath

# Operation: list_linked_relations
class GetLinkedRelationsRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API for which to retrieve linked relations.")
    api_version_id: str = Field(default=..., validation_alias="apiVersionId", serialization_alias="apiVersionId", description="The unique identifier of the API version for which to retrieve linked relations.")
class GetLinkedRelationsRequest(StrictModel):
    """Retrieve all relations linked to a specific API version, including detailed information about each relation type and its associated relations."""
    path: GetLinkedRelationsRequestPath

# Operation: add_relations_to_api_version
class CreateRelationsRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API to which relations will be added.")
    api_version_id: str = Field(default=..., validation_alias="apiVersionId", serialization_alias="apiVersionId", description="The unique identifier of the API version to which relations will be added.")
class CreateRelationsRequestBody(StrictModel):
    contracttest: list[str] | None = Field(default=None, description="Array of Collection UIDs to associate as contract tests with this API version.")
    documentation: list[str] | None = Field(default=None, description="Array of Collection UIDs to associate as documentation with this API version.")
    mock: list[str] | None = Field(default=None, description="Array of Mock IDs to associate with this API version.")
    testsuite: list[str] | None = Field(default=None, description="Array of Collection UIDs to associate as test suites with this API version.")
class CreateRelationsRequest(StrictModel):
    """Link existing Postman entities (collections, environments, mocks, monitors) to an API version as relations. Specify which entity types to associate by providing their corresponding UIDs or IDs in the request body."""
    path: CreateRelationsRequestPath
    body: CreateRelationsRequestBody | None = None

# Operation: create_schema
class CreateSchemaRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API to which the schema will be added.")
    api_version_id: str = Field(default=..., validation_alias="apiVersionId", serialization_alias="apiVersionId", description="The unique identifier of the API version under which the schema will be created.")
class CreateSchemaRequestBodySchema(StrictModel):
    language: str | None = Field(default=None, validation_alias="language", serialization_alias="language", description="The schema language format. Use 'json' or 'yaml' for OpenAPI and RAML schemas; use 'graphql' exclusively for GraphQL schemas.")
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The schema type specification. Supported types are 'openapi3', 'openapi2', 'openapi1', 'raml', and 'graphql'.")
class CreateSchemaRequestBody(StrictModel):
    schema_: CreateSchemaRequestBodySchema | None = Field(default=None, validation_alias="schema", serialization_alias="schema")
class CreateSchemaRequest(StrictModel):
    """Creates a new schema for an API version. The schema can be defined in OpenAPI (v1, v2, v3), RAML, or GraphQL format with corresponding language specification."""
    path: CreateSchemaRequestPath
    body: CreateSchemaRequestBody | None = None

# Operation: get_schema
class GetSchemaRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API containing the schema.")
    api_version_id: str = Field(default=..., validation_alias="apiVersionId", serialization_alias="apiVersionId", description="The unique identifier of the API version containing the schema.")
    schema_id: str = Field(default=..., validation_alias="schemaId", serialization_alias="schemaId", description="The unique identifier of the schema to retrieve.")
class GetSchemaRequest(StrictModel):
    """Retrieves a single schema by its ID. Returns a schema object containing metadata including id, language, type, and schema definition."""
    path: GetSchemaRequestPath

# Operation: update_schema
class UpdateSchemaRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API containing the schema to update.")
    api_version_id: str = Field(default=..., validation_alias="apiVersionId", serialization_alias="apiVersionId", description="The unique identifier of the API version containing the schema to update.")
    schema_id: str = Field(default=..., validation_alias="schemaId", serialization_alias="schemaId", description="The unique identifier of the schema to update.")
class UpdateSchemaRequestBodySchema(StrictModel):
    language: str | None = Field(default=None, validation_alias="language", serialization_alias="language", description="The schema language format. Use `json` or `yaml` for OpenAPI and RAML schemas; use `graphql` for GraphQL schemas.")
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The schema type being updated. Allowed values are `openapi3`, `openapi2`, `openapi1`, `raml`, or `graphql`.")
class UpdateSchemaRequestBody(StrictModel):
    schema_: UpdateSchemaRequestBodySchema | None = Field(default=None, validation_alias="schema", serialization_alias="schema")
class UpdateSchemaRequest(StrictModel):
    """Update an existing API schema by replacing its content and metadata. Supports OpenAPI (v1, v2, v3), RAML, and GraphQL schema types in their respective formats."""
    path: UpdateSchemaRequestPath
    body: UpdateSchemaRequestBody | None = None

# Operation: create_collection_from_schema
class CreateCollectionFromSchemaRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API to which the collection will be linked.")
    api_version_id: str = Field(default=..., validation_alias="apiVersionId", serialization_alias="apiVersionId", description="The unique identifier of the API version to which the collection will be linked.")
    schema_id: str = Field(default=..., validation_alias="schemaId", serialization_alias="schemaId", description="The unique identifier of the schema from which the collection will be created.")
class CreateCollectionFromSchemaRequestQuery(StrictModel):
    workspace: str | None = Field(default=None, description="The workspace ID where the collection will be created. Use the workspace identifier to scope the collection to a specific workspace context.")
class CreateCollectionFromSchemaRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name for the new collection. This is a human-readable identifier for organizing and referencing the collection.")
    relations: list[CreateCollectionFromSchemaBodyRelationsItem] | None = Field(default=None, description="An array of relation types to associate with the collection. Valid relation types are: contracttest, integrationtest, testsuite, and documentation. At least one relation type should be specified to define the collection's purpose.")
class CreateCollectionFromSchemaRequest(StrictModel):
    """Create a new collection linked to an API schema with one or more relation types (contract test, integration test, test suite, or documentation). The collection serves as an organizational container for API-related artifacts."""
    path: CreateCollectionFromSchemaRequestPath
    query: CreateCollectionFromSchemaRequestQuery | None = None
    body: CreateCollectionFromSchemaRequestBody | None = None

# Operation: list_test_suite_relations
class GetTestSuiteRelationsRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API for which to retrieve test suite relations.")
    api_version_id: str = Field(default=..., validation_alias="apiVersionId", serialization_alias="apiVersionId", description="The unique identifier of the API version for which to retrieve test suite relations.")
class GetTestSuiteRelationsRequest(StrictModel):
    """Retrieves all test suite relations linked to a specific API version, organized by relation type with complete details for each relation."""
    path: GetTestSuiteRelationsRequestPath

# Operation: sync_relation_with_schema
class SyncRelationsWithSchemaRequestPath(StrictModel):
    api_id: str = Field(default=..., validation_alias="apiId", serialization_alias="apiId", description="The unique identifier of the API containing the relation to synchronize.")
    api_version_id: str = Field(default=..., validation_alias="apiVersionId", serialization_alias="apiVersionId", description="The unique identifier of the specific API version whose schema will be used for synchronization.")
    entity_type: str = Field(default=..., validation_alias="entityType", serialization_alias="entityType", description="The type of relation to sync, such as documentation, contracttest, integrationtest, testsuite, mock, or monitor.")
    entity_id: str = Field(default=..., validation_alias="entityId", serialization_alias="entityId", description="The unique identifier of the specific relation instance to synchronize with the schema.")
class SyncRelationsWithSchemaRequest(StrictModel):
    """Synchronize a relation (such as documentation, contract test, or monitor) with the current API schema to ensure consistency and alignment with schema changes."""
    path: SyncRelationsWithSchemaRequestPath

# Operation: create_collection
class CreateCollectionRequestBodyCollectionInfo(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A descriptive label for the collection (e.g., 'This is just a sample collection.'). Helps identify the collection's purpose.")
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The name of the collection. Supports dynamic variables like {{$randomInt}} for generating unique names.")
    schema_: str | None = Field(default=None, validation_alias="schema", serialization_alias="schema")
class CreateCollectionRequestBodyCollection(StrictModel):
    item: list[CreateCollectionBodyCollectionItemItem] | None = Field(default=None, validation_alias="item", serialization_alias="item", description="An array of request items to include in the collection. Items define the API requests and folder structure within the collection.")
    info: CreateCollectionRequestBodyCollectionInfo | None = None
class CreateCollectionRequestBody(StrictModel):
    collection: CreateCollectionRequestBodyCollection | None = None
class CreateCollectionRequest(StrictModel):
    """Create a new Postman collection in Postman Collection v2 format. Returns the created collection's name, ID, and UID. Optionally specify a workspace via query parameter to create the collection in a specific workspace."""
    body: CreateCollectionRequestBody | None = None

# Operation: create_fork_of_collection
class CreateAForkRequestPath(StrictModel):
    collection_uid: str = Field(default=..., description="The unique identifier of the collection to fork.")
class CreateAForkRequestQuery(StrictModel):
    workspace: str | None = Field(default=None, description="The ID of the workspace where the forked collection should be created. If not specified, the fork will be created in the default workspace.")
class CreateAForkRequest(StrictModel):
    """Create a fork of an existing collection. The response includes the forked collection's name, ID, UID, and fork metadata. You can optionally specify a target workspace for the fork. Note: The fork is created with a default label 'Forked Collection' (Postman v10 API requires 'label', and the schema-declared 'name' field is rejected)."""
    path: CreateAForkRequestPath
    query: CreateAForkRequestQuery | None = None

# Operation: merge_fork_to_collection
class MergeAForkRequestBody(StrictModel):
    destination: str | None = Field(default=None, description="The UID of the destination collection where the fork will be merged into. Required for the merge operation.")
    source: str | None = Field(default=None, description="The UID of the forked collection to merge. This is the source collection that will be merged into the destination.")
    strategy: str | None = Field(default=None, description="The merge strategy to apply: `deleteSource` removes the forked collection after merging, or `updateSourceWithDestination` syncs the forked collection with any changes made to the destination. Defaults to standard merge behavior if not specified.")
class MergeAForkRequest(StrictModel):
    """Merge a forked collection back into its destination collection. Optionally specify a merge strategy to control whether the source fork is deleted or updated with destination changes after the merge."""
    body: MergeAForkRequestBody | None = None

# Operation: get_collection
class SingleCollectionRequestPath(StrictModel):
    collection_uid: str = Field(default=..., description="The unique identifier (uid) of the collection to retrieve. This is a required string value that uniquely identifies the collection within the system.")
class SingleCollectionRequest(StrictModel):
    """Retrieve the full contents of a specific collection by its unique identifier. You must have access permissions to the collection to retrieve it."""
    path: SingleCollectionRequestPath

# Operation: update_collection
class UpdateCollectionRequestPath(StrictModel):
    collection_uid: str = Field(default=..., description="The unique identifier of the collection to update. This is a required path parameter that specifies which collection will be replaced.")
class UpdateCollectionRequestBodyCollectionInfo(StrictModel):
    postman_id: str | None = Field(default=None, validation_alias="_postman_id", serialization_alias="_postman_id", description="The Postman internal identifier for the collection, typically a UUID format. Used to maintain collection identity across systems.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A text description of the collection's purpose and contents. Supports dynamic variables in the format.")
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The display name of the collection. Supports dynamic variables (e.g., {{$randomInt}}) for generating unique names.")
    schema_: str | None = Field(default=None, validation_alias="schema", serialization_alias="schema")
class UpdateCollectionRequestBodyCollection(StrictModel):
    item: list[UpdateCollectionBodyCollectionItemItem] | None = Field(default=None, validation_alias="item", serialization_alias="item", description="An array of request items and folders that comprise the collection. Items are processed in the order provided and define the collection's structure and endpoints.")
    info: UpdateCollectionRequestBodyCollectionInfo | None = None
class UpdateCollectionRequestBody(StrictModel):
    collection: UpdateCollectionRequestBodyCollection | None = None
class UpdateCollectionRequest(StrictModel):
    """Replace an existing collection with updated content in Postman Collection v2 format. Returns the updated collection's name, id, and uid. Requires API Key authentication."""
    path: UpdateCollectionRequestPath
    body: UpdateCollectionRequestBody | None = None

# Operation: delete_collection
class DeleteCollectionRequestPath(StrictModel):
    collection_uid: str = Field(default=..., description="The unique identifier of the collection to delete. This identifier is required to specify which collection should be removed.")
class DeleteCollectionRequest(StrictModel):
    """Permanently delete a collection by its unique identifier. Returns the deleted collection's id and uid upon successful deletion."""
    path: DeleteCollectionRequestPath

# Operation: create_environment
class CreateEnvironmentRequestBodyEnvironment(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The name of the environment to create. Must be between 1 and 254 characters long.")
    values: list[CreateEnvironmentBodyEnvironmentValuesItem] | None = Field(default=None, validation_alias="values", serialization_alias="values", description="An array of environment variables to initialize with the environment. Each variable must have a key and value; the enabled flag is optional. Up to 100 variables can be specified per environment.")
class CreateEnvironmentRequestBody(StrictModel):
    environment: CreateEnvironmentRequestBodyEnvironment | None = None
class CreateEnvironmentRequest(StrictModel):
    """Create a new environment with configuration variables. Optionally specify a workspace context via query parameter. Returns the created environment's name and unique identifier."""
    body: CreateEnvironmentRequestBody | None = None

# Operation: get_environment
class SingleEnvironmentRequestPath(StrictModel):
    environment_uid: str = Field(default=..., description="The unique identifier of the environment to retrieve. This is a required string value that identifies which environment's contents to access.")
class SingleEnvironmentRequest(StrictModel):
    """Retrieve the full contents of a specific environment by its unique identifier. This operation requires authentication via API Key."""
    path: SingleEnvironmentRequestPath

# Operation: update_environment
class UpdateEnvironmentRequestPath(StrictModel):
    environment_uid: str = Field(default=..., description="The unique identifier of the environment to update.")
class UpdateEnvironmentRequestBodyEnvironment(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The new name for the environment. Must be between 1 and 254 characters.")
    values: list[UpdateEnvironmentBodyEnvironmentValuesItem] | None = Field(default=None, validation_alias="values", serialization_alias="values", description="An array of environment variables (up to 100 items). Each variable must have a key and value (both 1-254 characters), and may optionally include a type and enabled status. Variables are applied in the order provided.")
class UpdateEnvironmentRequestBody(StrictModel):
    environment: UpdateEnvironmentRequestBodyEnvironment | None = None
class UpdateEnvironmentRequest(StrictModel):
    """Replace an existing environment with updated configuration. Specify the environment to modify by its unique identifier and provide the new environment name and variable values."""
    path: UpdateEnvironmentRequestPath
    body: UpdateEnvironmentRequestBody | None = None

# Operation: delete_environment
class DeleteEnvironmentRequestPath(StrictModel):
    environment_uid: str = Field(default=..., description="The unique identifier of the environment to delete. This is a required string value that uniquely identifies the environment within the system.")
class DeleteEnvironmentRequest(StrictModel):
    """Permanently delete a single environment by its unique identifier. This action cannot be undone."""
    path: DeleteEnvironmentRequestPath

# Operation: create_mock
class CreateMockRequestBodyMock(StrictModel):
    collection: str | None = Field(default=None, validation_alias="collection", serialization_alias="collection", description="The unique identifier of the collection for which to create the mock. Format is a UUID string.")
    environment: str | None = Field(default=None, validation_alias="environment", serialization_alias="environment", description="The unique identifier of an environment to use for resolving variables within the collection. Format is a UUID string. If provided, environment variables will be substituted in the mock.")
class CreateMockRequestBody(StrictModel):
    mock: CreateMockRequestBodyMock | None = None
class CreateMockRequest(StrictModel):
    """Create a mock server for a collection, optionally resolving environment variables. You can specify a workspace context via query parameter to determine where the mock is created."""
    body: CreateMockRequestBody | None = None

# Operation: get_mock
class SingleMockRequestPath(StrictModel):
    mock_uid: str = Field(default=..., description="The unique identifier of the mock to retrieve. This is a required string value that uniquely identifies the mock resource.")
class SingleMockRequest(StrictModel):
    """Retrieve detailed information about a specific mock by its unique identifier. Requires API Key authentication via X-Api-Key header or apikey query parameter."""
    path: SingleMockRequestPath

# Operation: update_mock
class UpdateMockRequestPath(StrictModel):
    mock_uid: str = Field(default=..., description="The unique identifier of the mock server to update.")
class UpdateMockRequestBodyMock(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A descriptive text explaining the purpose or details of the mock server.")
    environment: str | None = Field(default=None, validation_alias="environment", serialization_alias="environment", description="The unique identifier of the environment where this mock server operates.")
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="A human-readable name for the mock server.")
    private: bool | None = Field(default=None, validation_alias="private", serialization_alias="private", description="Whether the mock server is private (true) or publicly accessible (false).")
    version_tag: str | None = Field(default=None, validation_alias="versionTag", serialization_alias="versionTag", description="The unique identifier of the version tag associated with this mock server.")
class UpdateMockRequestBody(StrictModel):
    mock: UpdateMockRequestBodyMock | None = None
class UpdateMockRequest(StrictModel):
    """Update an existing mock server by its unique identifier. Modify properties such as name, description, environment, privacy settings, and version tag."""
    path: UpdateMockRequestPath
    body: UpdateMockRequestBody | None = None

# Operation: delete_mock
class DeleteMockRequestPath(StrictModel):
    mock_uid: str = Field(default=..., description="The unique identifier of the mock to delete. This is a required string value that identifies which mock should be removed.")
class DeleteMockRequest(StrictModel):
    """Permanently delete an existing mock by its unique identifier. This operation removes the mock and all associated data."""
    path: DeleteMockRequestPath

# Operation: publish_mock
class PublishMockRequestPath(StrictModel):
    mock_uid: str = Field(default=..., description="The unique identifier of the mock to publish. This is the uid assigned to the mock when it was created.")
class PublishMockRequest(StrictModel):
    """Publishes a mock that you have created, making it available for use. Requires the mock's unique identifier (uid) and API key authentication."""
    path: PublishMockRequestPath

# Operation: delete_mock_publication
class UnpublishMockRequestPath(StrictModel):
    mock_uid: str = Field(default=..., description="The unique identifier of the mock to unpublish. This is a required string value that identifies which mock should be removed from published state.")
class UnpublishMockRequest(StrictModel):
    """Unpublish a mock by its unique identifier. This removes the mock from published state, making it unavailable for use."""
    path: UnpublishMockRequestPath

# Operation: create_monitor
class CreateMonitorRequestBodyMonitorSchedule(StrictModel):
    cron: str | None = Field(default=None, validation_alias="cron", serialization_alias="cron", description="A cron expression defining the monitor's execution schedule (e.g., '*/5 * * * *' for every 5 minutes, '0 17 * * *' for daily at 5pm). Only limited schedules are supported; check Postman Monitors for allowed values.")
    timezone_: str | None = Field(default=None, validation_alias="timezone", serialization_alias="timezone", description="The timezone for interpreting the cron schedule (e.g., 'Asia/Kolkata', 'America/New_York'). Use IANA timezone database format. Defaults to UTC if not specified.")
class CreateMonitorRequestBodyMonitor(StrictModel):
    collection: str | None = Field(default=None, validation_alias="collection", serialization_alias="collection", description="The unique identifier of the Postman collection to monitor. This collection contains the API tests that will be executed on schedule.")
    environment: str | None = Field(default=None, validation_alias="environment", serialization_alias="environment", description="The unique identifier of the Postman environment to use when running the monitor. This provides variables and configuration for the collection execution.")
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="A descriptive name for the monitor to help identify it in your workspace.")
    schedule: CreateMonitorRequestBodyMonitorSchedule | None = None
class CreateMonitorRequestBody(StrictModel):
    monitor: CreateMonitorRequestBodyMonitor | None = None
class CreateMonitorRequest(StrictModel):
    """Create a new monitor that runs API tests on a specified schedule. The monitor will execute a Postman collection in a given environment at intervals defined by a cron expression and timezone."""
    body: CreateMonitorRequestBody | None = None

# Operation: get_monitor
class SingleMonitorRequestPath(StrictModel):
    monitor_uid: str = Field(default=..., description="The unique identifier of the monitor to retrieve. This is a required string value that uniquely identifies the monitor in the system.")
class SingleMonitorRequest(StrictModel):
    """Retrieve detailed information about a specific monitor using its unique identifier. This operation requires authentication via API key."""
    path: SingleMonitorRequestPath

# Operation: update_monitor
class UpdateMonitorRequestPath(StrictModel):
    monitor_uid: str = Field(default=..., description="The unique identifier of the monitor to update. This is a required path parameter that specifies which monitor will be modified.")
class UpdateMonitorRequestBodyMonitorSchedule(StrictModel):
    cron: str | None = Field(default=None, validation_alias="cron", serialization_alias="cron", description="A cron expression defining the monitor's execution schedule (e.g., `*/5 * * * *` for every 5 minutes, `0 17 * * *` for daily at 5pm). Only certain predefined schedules are supported—verify your desired frequency is available in Postman Monitors before use.")
    timezone_: str | None = Field(default=None, validation_alias="timezone", serialization_alias="timezone", description="The timezone for interpreting the cron schedule (e.g., `America/Chicago`). Use IANA timezone database identifiers to ensure the monitor runs at the intended local time.")
class UpdateMonitorRequestBodyMonitor(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The new display name for the monitor. Use this to give the monitor a more descriptive or updated label.")
    schedule: UpdateMonitorRequestBodyMonitorSchedule | None = None
class UpdateMonitorRequestBody(StrictModel):
    monitor: UpdateMonitorRequestBodyMonitor | None = None
class UpdateMonitorRequest(StrictModel):
    """Update an existing monitor's name and execution schedule. Modify the monitor identified by its unique identifier to change its display name and/or cron-based execution frequency and timezone."""
    path: UpdateMonitorRequestPath
    body: UpdateMonitorRequestBody | None = None

# Operation: delete_monitor
class DeleteMonitorRequestPath(StrictModel):
    monitor_uid: str = Field(default=..., description="The unique identifier of the monitor to delete. This is a required string value that identifies which monitor to remove.")
class DeleteMonitorRequest(StrictModel):
    """Permanently delete an existing monitor by its unique identifier. This operation removes the monitor and all associated data."""
    path: DeleteMonitorRequestPath

# Operation: run_monitor
class RunAMonitorRequestPath(StrictModel):
    monitor_uid: str = Field(default=..., description="The unique identifier of the monitor to execute.")
class RunAMonitorRequest(StrictModel):
    """Executes a monitor immediately and waits for completion, returning the run results. This is a synchronous operation that blocks until the monitor finishes executing."""
    path: RunAMonitorRequestPath

# Operation: create_webhook
class CreateWebhookRequestQuery(StrictModel):
    workspace: str | None = Field(default=None, description="The workspace ID where the webhook will be created. Required to scope the webhook to the correct workspace context.")
class CreateWebhookRequestBodyWebhook(StrictModel):
    collection: str | None = Field(default=None, validation_alias="collection", serialization_alias="collection", description="The ID of the collection that will be triggered when this webhook is invoked. This determines which collection executes when the webhook URL is called.")
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="A descriptive name for the webhook to help identify its purpose and distinguish it from other webhooks in your workspace.")
class CreateWebhookRequestBody(StrictModel):
    webhook: CreateWebhookRequestBodyWebhook | None = None
class CreateWebhookRequest(StrictModel):
    """Create a webhook that automatically triggers a specified collection when the webhook URL is called. The webhook URL is returned in the response for use in external systems."""
    query: CreateWebhookRequestQuery | None = None
    body: CreateWebhookRequestBody | None = None

# Operation: create_workspace
class CreateWorkspaceRequestBodyWorkspace(StrictModel):
    collections_: list[CreateWorkspaceBodyWorkspaceCollectionsItem] | None = Field(default=None, validation_alias="collections", serialization_alias="collections", description="Array of collection UIDs to include in the workspace. Order is preserved as provided.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A descriptive text for the workspace to explain its purpose or contents.")
    environments: list[CreateWorkspaceBodyWorkspaceEnvironmentsItem] | None = Field(default=None, validation_alias="environments", serialization_alias="environments", description="Array of environment UIDs to include in the workspace. Order is preserved as provided.")
    mocks: list[CreateWorkspaceBodyWorkspaceMocksItem] | None = Field(default=None, validation_alias="mocks", serialization_alias="mocks", description="Array of mock server UIDs to include in the workspace. Order is preserved as provided.")
    monitors: list[CreateWorkspaceBodyWorkspaceMonitorsItem] | None = Field(default=None, validation_alias="monitors", serialization_alias="monitors", description="Array of monitor UIDs to include in the workspace. Order is preserved as provided.")
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The display name for the workspace. Use a descriptive name that identifies the workspace purpose or project.")
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The workspace type, such as 'personal' for individual workspaces or other organizational types.")
class CreateWorkspaceRequestBody(StrictModel):
    workspace: CreateWorkspaceRequestBodyWorkspace | None = None
class CreateWorkspaceRequest(StrictModel):
    """Create a new workspace and optionally populate it with collections, environments, mocks, and monitors by their unique identifiers. Returns the created workspace name and ID."""
    body: CreateWorkspaceRequestBody | None = None

# Operation: get_workspace
class SingleWorkspaceRequestPath(StrictModel):
    workspace_id: str = Field(default=..., description="The unique identifier of the workspace to retrieve. Must be a valid workspace ID that you have access to.")
class SingleWorkspaceRequest(StrictModel):
    """Retrieve a workspace by its ID, including all associated collections, environments, mocks, and monitors that you have access to."""
    path: SingleWorkspaceRequestPath

# Operation: update_workspace
class UpdateWorkspaceRequestPath(StrictModel):
    workspace_id: str = Field(default=..., description="The unique identifier of the workspace to update.")
class UpdateWorkspaceRequestBodyWorkspace(StrictModel):
    collections_: list[UpdateWorkspaceBodyWorkspaceCollectionsItem] | None = Field(default=None, validation_alias="collections", serialization_alias="collections", description="Array of collection UIDs to associate with this workspace. Replaces all existing collections—only specified collections will remain associated after the update.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A text description for the workspace to help identify its purpose or contents.")
    environments: list[UpdateWorkspaceBodyWorkspaceEnvironmentsItem] | None = Field(default=None, validation_alias="environments", serialization_alias="environments", description="Array of environment UIDs to associate with this workspace. Replaces all existing environments—only specified environments will remain associated after the update.")
    mocks: list[UpdateWorkspaceBodyWorkspaceMocksItem] | None = Field(default=None, validation_alias="mocks", serialization_alias="mocks", description="Array of mock UIDs to associate with this workspace. Replaces all existing mocks—only specified mocks will remain associated after the update.")
    monitors: list[UpdateWorkspaceBodyWorkspaceMonitorsItem] | None = Field(default=None, validation_alias="monitors", serialization_alias="monitors", description="Array of monitor UIDs to associate with this workspace. Replaces all existing monitors—only specified monitors will remain associated after the update.")
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The display name for the workspace.")
class UpdateWorkspaceRequestBody(StrictModel):
    workspace: UpdateWorkspaceRequestBodyWorkspace | None = None
class UpdateWorkspaceRequest(StrictModel):
    """Update a workspace's properties and manage its associations with collections, environments, mocks, and monitors. The endpoint replaces all associated entities with those specified in the request, so omitted entities will be removed from the workspace."""
    path: UpdateWorkspaceRequestPath
    body: UpdateWorkspaceRequestBody | None = None

# Operation: delete_workspace
class DeleteWorkspaceRequestPath(StrictModel):
    workspace_id: str = Field(default=..., description="The unique identifier of the workspace to delete. This ID is required to specify which workspace should be removed.")
class DeleteWorkspaceRequest(StrictModel):
    """Permanently delete an existing workspace by its ID. Returns the ID of the deleted workspace upon successful completion."""
    path: DeleteWorkspaceRequestPath

# ============================================================================
# Component Models
# ============================================================================

class CreateCollectionBodyCollectionItemItemItemItemRequestBody(PermissiveModel):
    mode: str | None = None
    raw: str | None = None

class CreateCollectionBodyCollectionItemItemItemItemRequestHeaderItem(PermissiveModel):
    key: str | None = None
    value: str | None = None

class CreateCollectionBodyCollectionItemItemItemItemRequest(PermissiveModel):
    body: CreateCollectionBodyCollectionItemItemItemItemRequestBody | None = None
    description: str | None = None
    header: list[CreateCollectionBodyCollectionItemItemItemItemRequestHeaderItem] | None = None
    method: str | None = None
    url: str | None = None

class CreateCollectionBodyCollectionItemItemItemItem(PermissiveModel):
    name: str | None = None
    request: CreateCollectionBodyCollectionItemItemItemItemRequest | None = None

class CreateCollectionBodyCollectionItemItem(PermissiveModel):
    item: list[CreateCollectionBodyCollectionItemItemItemItem] | None = None
    name: str | None = None

class CreateCollectionFromSchemaBodyRelationsItem(PermissiveModel):
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type")

class CreateEnvironmentBodyEnvironmentValuesItem(PermissiveModel):
    key: str | None = None
    value: str | None = None

class CreateWorkspaceBodyWorkspaceCollectionsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None
    uid: str | None = None

class CreateWorkspaceBodyWorkspaceEnvironmentsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None
    uid: str | None = None

class CreateWorkspaceBodyWorkspaceMocksItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")

class CreateWorkspaceBodyWorkspaceMonitorsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")

class UpdateCollectionBodyCollectionItemItemItemItemRequestBody(PermissiveModel):
    mode: str | None = None
    raw: str | None = None

class UpdateCollectionBodyCollectionItemItemItemItemRequestHeaderItem(PermissiveModel):
    key: str | None = None
    value: str | None = None

class UpdateCollectionBodyCollectionItemItemItemItemRequest(PermissiveModel):
    body: UpdateCollectionBodyCollectionItemItemItemItemRequestBody | None = None
    description: str | None = None
    header: list[UpdateCollectionBodyCollectionItemItemItemItemRequestHeaderItem] | None = None
    method: str | None = None
    url: str | None = None

class UpdateCollectionBodyCollectionItemItemItemItem(PermissiveModel):
    name: str | None = None
    request: UpdateCollectionBodyCollectionItemItemItemItemRequest | None = None

class UpdateCollectionBodyCollectionItemItem(PermissiveModel):
    item: list[UpdateCollectionBodyCollectionItemItemItemItem] | None = None
    name: str | None = None

class UpdateEnvironmentBodyEnvironmentValuesItem(PermissiveModel):
    key: str | None = None
    value: str | None = None

class UpdateWorkspaceBodyWorkspaceCollectionsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None
    uid: str | None = None

class UpdateWorkspaceBodyWorkspaceEnvironmentsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None
    uid: str | None = None

class UpdateWorkspaceBodyWorkspaceMocksItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")

class UpdateWorkspaceBodyWorkspaceMonitorsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")


# Rebuild models to resolve forward references (required for circular refs)
CreateCollectionBodyCollectionItemItem.model_rebuild()
CreateCollectionBodyCollectionItemItemItemItem.model_rebuild()
CreateCollectionBodyCollectionItemItemItemItemRequest.model_rebuild()
CreateCollectionBodyCollectionItemItemItemItemRequestBody.model_rebuild()
CreateCollectionBodyCollectionItemItemItemItemRequestHeaderItem.model_rebuild()
CreateCollectionFromSchemaBodyRelationsItem.model_rebuild()
CreateEnvironmentBodyEnvironmentValuesItem.model_rebuild()
CreateWorkspaceBodyWorkspaceCollectionsItem.model_rebuild()
CreateWorkspaceBodyWorkspaceEnvironmentsItem.model_rebuild()
CreateWorkspaceBodyWorkspaceMocksItem.model_rebuild()
CreateWorkspaceBodyWorkspaceMonitorsItem.model_rebuild()
UpdateCollectionBodyCollectionItemItem.model_rebuild()
UpdateCollectionBodyCollectionItemItemItemItem.model_rebuild()
UpdateCollectionBodyCollectionItemItemItemItemRequest.model_rebuild()
UpdateCollectionBodyCollectionItemItemItemItemRequestBody.model_rebuild()
UpdateCollectionBodyCollectionItemItemItemItemRequestHeaderItem.model_rebuild()
UpdateEnvironmentBodyEnvironmentValuesItem.model_rebuild()
UpdateWorkspaceBodyWorkspaceCollectionsItem.model_rebuild()
UpdateWorkspaceBodyWorkspaceEnvironmentsItem.model_rebuild()
UpdateWorkspaceBodyWorkspaceMocksItem.model_rebuild()
UpdateWorkspaceBodyWorkspaceMonitorsItem.model_rebuild()

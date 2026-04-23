"""
Contentful Management MCP Server - Pydantic Models

Generated: 2026-04-23 21:10:05 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from _validators import StrictModel
from pydantic import Field

__all__ = [
    "DeleteOrganizationsAppDefinitionsKeysRequest",
    "DeleteOrganizationsAppDefinitionsRequest",
    "DeleteOrganizationsAppDefinitionsSigningSecretRequest",
    "DeleteSpacesApiKeysRequest",
    "DeleteSpacesEnvironmentAliasesRequest",
    "DeleteSpacesEnvironmentReleasesPublishedRequest",
    "DeleteSpacesEnvironmentReleasesRequest",
    "DeleteSpacesEnvironmentsAppInstallationsRequest",
    "DeleteSpacesEnvironmentsAssetsArchivedRequest",
    "DeleteSpacesEnvironmentsAssetsPublishedRequest",
    "DeleteSpacesEnvironmentsAssetsRequest",
    "DeleteSpacesEnvironmentsContentTypesPublishedRequest",
    "DeleteSpacesEnvironmentsContentTypesRequest",
    "DeleteSpacesEnvironmentsEntriesArchivedRequest",
    "DeleteSpacesEnvironmentsEntriesPublishedRequest",
    "DeleteSpacesEnvironmentsEntriesRequest",
    "DeleteSpacesEnvironmentsEntriesTasksRequest",
    "DeleteSpacesEnvironmentsExtensionsRequest",
    "DeleteSpacesEnvironmentsLocalesRequest",
    "DeleteSpacesEnvironmentsRequest",
    "DeleteSpacesEnvironmentsTagsRequest",
    "DeleteSpacesRequest",
    "DeleteSpacesRolesRequest",
    "DeleteSpacesScheduledActionsRequest",
    "DeleteSpacesSpaceMembershipsRequest",
    "DeleteSpacesUploadsRequest",
    "GetOrganizationsAppDefinitionsSigningSecretRequest",
    "GetOrganizationsByOrganizationIdAppDefinitionsByAppDefinitionIdKeysRequest",
    "GetOrganizationsByOrganizationIdAppDefinitionsRequest",
    "GetOrganizationsOrganizationPeriodicUsagesRequest",
    "GetOrganizationsSpacePeriodicUsagesRequest",
    "GetSpacesBySpaceIdApiKeysByApiKeyIdRequest",
    "GetSpacesBySpaceIdApiKeysRequest",
    "GetSpacesBySpaceIdEnvironmentAliasesByEnvironmentAliasIdRequest",
    "GetSpacesBySpaceIdEnvironmentAliasesRequest",
    "GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesByReleasesIdActionsByReleaseActionIdRequest",
    "GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesByReleasesIdActionsRequest",
    "GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesByReleasesIdRequest",
    "GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesRequest",
    "GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAppInstallationsRequest",
    "GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAssetsByAssetIdRequest",
    "GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAssetsRequest",
    "GetSpacesBySpaceIdEnvironmentsByEnvironmentIdContentTypesByContentTypeIdRequest",
    "GetSpacesBySpaceIdEnvironmentsByEnvironmentIdContentTypesRequest",
    "GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesByEntryIdRequest",
    "GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesByEntryIdTasksByTaskIdRequest",
    "GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesByEntryIdTasksRequest",
    "GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesRequest",
    "GetSpacesBySpaceIdEnvironmentsByEnvironmentIdExtensionsByExtensionIdRequest",
    "GetSpacesBySpaceIdEnvironmentsByEnvironmentIdExtensionsRequest",
    "GetSpacesBySpaceIdEnvironmentsByEnvironmentIdLocalesByLocaleIdRequest",
    "GetSpacesBySpaceIdEnvironmentsByEnvironmentIdLocalesRequest",
    "GetSpacesBySpaceIdEnvironmentsByEnvironmentIdRequest",
    "GetSpacesBySpaceIdEnvironmentsByEnvironmentIdTagsByTagIdRequest",
    "GetSpacesBySpaceIdEnvironmentsByEnvironmentIdTagsRequest",
    "GetSpacesBySpaceIdEnvironmentsMasterContentTypesByContentTypeIdSnapshotsBySnapshotIdRequest",
    "GetSpacesBySpaceIdEnvironmentsMasterContentTypesByContentTypeIdSnapshotsRequest",
    "GetSpacesBySpaceIdEnvironmentsMasterEntriesByEntryIdSnapshotsBySnapshotIdRequest",
    "GetSpacesBySpaceIdEnvironmentsMasterEntriesByEntryIdSnapshotsRequest",
    "GetSpacesBySpaceIdEnvironmentsRequest",
    "GetSpacesBySpaceIdPreviewApiKeysByPreviewApiKeyIdRequest",
    "GetSpacesBySpaceIdPreviewApiKeysRequest",
    "GetSpacesBySpaceIdRequest",
    "GetSpacesBySpaceIdSpaceMembershipsBySpaceMembershipIdRequest",
    "GetSpacesBySpaceIdSpaceMembershipsRequest",
    "GetSpacesBySpaceIdWebhookDefinitionsByWebhookDefinitionIdRequest",
    "GetSpacesBySpaceIdWebhookDefinitionsRequest",
    "GetSpacesBySpaceIdWebhooksByWebhookIdCallsByCallIdRequest",
    "GetSpacesBySpaceIdWebhooksByWebhookIdCallsRequest",
    "GetSpacesEnvironmentBulkActionsActionsRequest",
    "GetSpacesEnvironmentsEntriesReferencesRequest",
    "GetSpacesEnvironmentsPublicAssetsRequest",
    "GetSpacesEnvironmentsPublicContentTypesRequest",
    "GetSpacesScheduledActionsRequest",
    "GetSpacesTeamsRequest",
    "GetSpacesUploadsRequest",
    "GetSpacesWebhooksHealthRequest",
    "GetUsersMeAccessTokensByTokenIdRequest",
    "PatchSpacesEnvironmentsEntriesRequest",
    "PostSpacesApiKeysRequest",
    "PostSpacesEnvironmentBulkActionsPublishRequest",
    "PostSpacesEnvironmentBulkActionsUnpublishRequest",
    "PostSpacesEnvironmentBulkActionsValidateRequest",
    "PostSpacesEnvironmentReleasesRequest",
    "PostSpacesEnvironmentReleasesValidateRequest",
    "PostSpacesEnvironmentsAppInstallationsAccessTokensRequest",
    "PostSpacesEnvironmentsAssetKeysRequest",
    "PostSpacesEnvironmentsAssetsRequest",
    "PostSpacesEnvironmentsContentTypesRequest",
    "PostSpacesEnvironmentsEntriesRequest",
    "PostSpacesEnvironmentsEntriesTasksRequest",
    "PostSpacesEnvironmentsLocalesRequest",
    "PostSpacesEnvironmentsRequest",
    "PostSpacesEnvironmentsTagsRequest",
    "PostSpacesRequest",
    "PostSpacesScheduledActionsRequest",
    "PostSpacesSpaceMembershipsRequest",
    "PostSpacesUploadsRequest",
    "PutOrganizationsAppDefinitionsSigningSecretRequest",
    "PutSpacesApiKeysRequest",
    "PutSpacesEnvironmentAliasesRequest",
    "PutSpacesEnvironmentReleasesPublishedRequest",
    "PutSpacesEnvironmentReleasesRequest",
    "PutSpacesEnvironmentsAssetsArchivedRequest",
    "PutSpacesEnvironmentsAssetsFilesProcessRequest",
    "PutSpacesEnvironmentsAssetsPublishedRequest",
    "PutSpacesEnvironmentsAssetsRequest",
    "PutSpacesEnvironmentsContentTypesPublishedRequest",
    "PutSpacesEnvironmentsContentTypesRequest",
    "PutSpacesEnvironmentsEntriesArchivedRequest",
    "PutSpacesEnvironmentsEntriesPublishedRequest",
    "PutSpacesEnvironmentsEntriesRequest",
    "PutSpacesEnvironmentsEntriesTasksRequest",
    "PutSpacesEnvironmentsExtensionsRequest",
    "PutSpacesEnvironmentsLocalesRequest",
    "PutSpacesEnvironmentsRequest",
    "PutSpacesEnvironmentsTagsRequest",
    "PutSpacesScheduledActionsRequest",
    "PutSpacesSpaceMembershipsRequest",
    "PutUsersMeAccessTokensRevokedRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: create_space
class PostSpacesRequestHeader(StrictModel):
    x_contentful_organization: str | None = Field(default=None, validation_alias="X-Contentful-Organization", serialization_alias="X-Contentful-Organization", description="The ID of the Contentful organization where the space will be created. Required to route the request to the correct organization context.")
class PostSpacesRequest(StrictModel):
    """Create a new space in Contentful by specifying its name and default locale. A space is a container for content types, entries, and assets within your Contentful organization."""
    header: PostSpacesRequestHeader | None = None

# Operation: get_space
class GetSpacesBySpaceIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space to retrieve. This is a required string that identifies which Contentful space you want to access.")
class GetSpacesBySpaceIdRequest(StrictModel):
    """Retrieve detailed information about a specific Contentful space by its ID. This returns the space's configuration, settings, and metadata."""
    path: GetSpacesBySpaceIdRequestPath

# Operation: delete_space
class DeleteSpacesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space to delete.")
class DeleteSpacesRequest(StrictModel):
    """Permanently delete a space and all its associated content. This action cannot be undone."""
    path: DeleteSpacesRequestPath

# Operation: list_environments
class GetSpacesBySpaceIdEnvironmentsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the environments you want to retrieve.")
class GetSpacesBySpaceIdEnvironmentsRequest(StrictModel):
    """Retrieve all environments within a Contentful space. Environments allow you to manage different versions of your content (e.g., staging, production)."""
    path: GetSpacesBySpaceIdEnvironmentsRequestPath

# Operation: create_environment
class PostSpacesEnvironmentsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space where the environment will be created.")
class PostSpacesEnvironmentsRequestHeader(StrictModel):
    x_contentful_source_environment: str | None = Field(default=None, validation_alias="X-Contentful-Source-Environment", serialization_alias="X-Contentful-Source-Environment", description="Optional identifier of an existing environment to clone as the source for the new environment's content and structure.")
class PostSpacesEnvironmentsRequest(StrictModel):
    """Create a new environment within a Contentful space. Optionally clone content from an existing source environment."""
    path: PostSpacesEnvironmentsRequestPath
    header: PostSpacesEnvironmentsRequestHeader | None = None

# Operation: get_environment
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the environment.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment to retrieve.")
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdRequest(StrictModel):
    """Retrieve a single environment within a Contentful space. Environments allow you to manage different versions of your content independently."""
    path: GetSpacesBySpaceIdEnvironmentsByEnvironmentIdRequestPath

# Operation: update_environment
class PutSpacesEnvironmentsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the environment to update.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment to update.")
class PutSpacesEnvironmentsRequest(StrictModel):
    """Update the configuration and settings of an environment within a Contentful space. This allows you to modify environment properties after creation."""
    path: PutSpacesEnvironmentsRequestPath

# Operation: delete_environment
class DeleteSpacesEnvironmentsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the environment to delete.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment to delete. Common examples include 'master' for the default environment.")
class DeleteSpacesEnvironmentsRequest(StrictModel):
    """Permanently delete an environment within a Contentful space. This action cannot be undone and will remove all content and configuration associated with the environment."""
    path: DeleteSpacesEnvironmentsRequestPath

# Operation: list_environment_aliases
class GetSpacesBySpaceIdEnvironmentAliasesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the environment aliases you want to retrieve.")
class GetSpacesBySpaceIdEnvironmentAliasesRequest(StrictModel):
    """Retrieve all environment aliases configured for a specific space in Contentful. Environment aliases allow you to reference environments by custom names in addition to their IDs."""
    path: GetSpacesBySpaceIdEnvironmentAliasesRequestPath

# Operation: get_environment_alias
class GetSpacesBySpaceIdEnvironmentAliasesByEnvironmentAliasIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the environment alias.")
    environment_alias_id: str = Field(default=..., description="The unique identifier of the environment alias to retrieve.")
class GetSpacesBySpaceIdEnvironmentAliasesByEnvironmentAliasIdRequest(StrictModel):
    """Retrieve a specific environment alias within a space. Environment aliases provide alternative identifiers for accessing environments in the Content Management API."""
    path: GetSpacesBySpaceIdEnvironmentAliasesByEnvironmentAliasIdRequestPath

# Operation: create_or_update_environment_alias
class PutSpacesEnvironmentAliasesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the environment alias.")
    environment_alias_id: str = Field(default=..., description="The unique identifier of the environment alias to create or update.")
class PutSpacesEnvironmentAliasesRequest(StrictModel):
    """Create a new environment alias or update an existing one within a Contentful space. Environment aliases provide stable references to environments that can be updated without changing client configurations."""
    path: PutSpacesEnvironmentAliasesRequestPath

# Operation: delete_environment_alias
class DeleteSpacesEnvironmentAliasesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the environment alias to delete.")
    environment_alias_id: str = Field(default=..., description="The unique identifier of the environment alias to delete.")
class DeleteSpacesEnvironmentAliasesRequest(StrictModel):
    """Delete an environment alias from a space. This removes the alias mapping, making it no longer available for accessing the associated environment."""
    path: DeleteSpacesEnvironmentAliasesRequestPath

# Operation: list_content_types
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdContentTypesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the environment and content types.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space from which to retrieve content types.")
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdContentTypesRequest(StrictModel):
    """Retrieve all content types defined for a specific environment within a space. Content types define the structure and fields for entries in Contentful."""
    path: GetSpacesBySpaceIdEnvironmentsByEnvironmentIdContentTypesRequestPath

# Operation: create_content_type
class PostSpacesEnvironmentsContentTypesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space where the content type will be created.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the content type will be created.")
class PostSpacesEnvironmentsContentTypesRequest(StrictModel):
    """Create a new content type within a specific environment. Content types define the structure and fields for entries in Contentful."""
    path: PostSpacesEnvironmentsContentTypesRequestPath

# Operation: get_content_type
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdContentTypesByContentTypeIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the content type. Example format: alphanumeric string like '5nvk6q4s3ttw'.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space. Typically 'master' for the default environment, but can be any environment name.")
    content_type_id: str = Field(default=..., description="The unique identifier of the content type to retrieve. Example format: alphanumeric string like 'testValid'.")
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdContentTypesByContentTypeIdRequest(StrictModel):
    """Retrieve a single content type definition from a specific environment within a space. Content types define the structure and fields for entries in Contentful."""
    path: GetSpacesBySpaceIdEnvironmentsByEnvironmentIdContentTypesByContentTypeIdRequestPath

# Operation: create_or_update_content_type
class PutSpacesEnvironmentsContentTypesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the content type.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the content type will be created or updated.")
    content_type_id: str = Field(default=..., description="The unique identifier for the content type being created or updated.")
class PutSpacesEnvironmentsContentTypesRequest(StrictModel):
    """Create a new content type or update an existing one within a specific space and environment. This operation allows you to define the structure and fields for content entries."""
    path: PutSpacesEnvironmentsContentTypesRequestPath

# Operation: delete_content_type
class DeleteSpacesEnvironmentsContentTypesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the content type to delete.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the content type is located.")
    content_type_id: str = Field(default=..., description="The unique identifier of the content type to delete.")
class DeleteSpacesEnvironmentsContentTypesRequest(StrictModel):
    """Permanently delete a content type from a specific environment within a space. This action cannot be undone and will remove the content type definition."""
    path: DeleteSpacesEnvironmentsContentTypesRequestPath

# Operation: publish_content_type
class PutSpacesEnvironmentsContentTypesPublishedRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the content type.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the content type will be published.")
    content_type_id: str = Field(default=..., description="The unique identifier of the content type to be published and activated.")
class PutSpacesEnvironmentsContentTypesPublishedRequest(StrictModel):
    """Activate a content type to make it available for use in a Contentful space. Once published, the content type can be used to create and manage content entries."""
    path: PutSpacesEnvironmentsContentTypesPublishedRequestPath

# Operation: deactivate_content_type
class DeleteSpacesEnvironmentsContentTypesPublishedRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the content type.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment where the content type is published.")
    content_type_id: str = Field(default=..., description="The unique identifier of the content type to deactivate.")
class DeleteSpacesEnvironmentsContentTypesPublishedRequest(StrictModel):
    """Deactivate a published content type in a specific environment, making it unavailable for use in new content entries."""
    path: DeleteSpacesEnvironmentsContentTypesPublishedRequestPath

# Operation: list_content_types_published
class GetSpacesEnvironmentsPublicContentTypesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the content types you want to retrieve.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space from which to fetch activated content types.")
class GetSpacesEnvironmentsPublicContentTypesRequest(StrictModel):
    """Retrieve all activated content types for a specific space and environment. Content types define the structure and fields available for entries in your space."""
    path: GetSpacesEnvironmentsPublicContentTypesRequestPath

# Operation: list_extensions
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdExtensionsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the environment and extensions.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment from which to retrieve extensions.")
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdExtensionsRequest(StrictModel):
    """Retrieve all UI extensions configured for a specific environment within a space. Extensions allow customization of the Contentful UI for content editors."""
    path: GetSpacesBySpaceIdEnvironmentsByEnvironmentIdExtensionsRequestPath

# Operation: get_extension
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdExtensionsByExtensionIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the extension.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the extension is configured.")
    extension_id: str = Field(default=..., description="The unique identifier of the extension to retrieve.")
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdExtensionsByExtensionIdRequest(StrictModel):
    """Retrieve a single UI extension configuration from a specific environment within a space. This returns the extension's definition and settings."""
    path: GetSpacesBySpaceIdEnvironmentsByEnvironmentIdExtensionsByExtensionIdRequestPath

# Operation: create_or_update_extension
class PutSpacesEnvironmentsExtensionsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space where the extension will be created or updated.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the extension will be created or updated.")
    extension_id: str = Field(default=..., description="The unique identifier for the extension being created or updated.")
class PutSpacesEnvironmentsExtensionsRequest(StrictModel):
    """Create a new UI extension or update an existing one in a Contentful space environment. This operation allows you to define custom UI components for the Contentful editor."""
    path: PutSpacesEnvironmentsExtensionsRequestPath

# Operation: delete_extension
class DeleteSpacesEnvironmentsExtensionsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the extension to delete.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the extension is located.")
    extension_id: str = Field(default=..., description="The unique identifier of the extension to delete.")
class DeleteSpacesEnvironmentsExtensionsRequest(StrictModel):
    """Permanently delete a UI extension from a specific environment within a space. This action cannot be undone."""
    path: DeleteSpacesEnvironmentsExtensionsRequestPath

# Operation: list_entries
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the entries to retrieve.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space from which to fetch entries.")
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesRequestQuery(StrictModel):
    tag_key: str | None = Field(default=None, validation_alias="TAG_KEY", serialization_alias="TAG_KEY", description="Optional tag key to filter entries by a specific tag value. Use this to retrieve only entries associated with a particular tag.")
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesRequest(StrictModel):
    """Retrieve all entries from a specific environment within a space. Entries represent content items managed in Contentful and can be filtered by tags."""
    path: GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesRequestPath
    query: GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesRequestQuery | None = None

# Operation: create_entry
class PostSpacesEnvironmentsEntriesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space where the entry will be created.")
    environment_id: str = Field(default=..., description="The environment within the space where the entry will be created. Defaults to 'master' for the main environment.")
class PostSpacesEnvironmentsEntriesRequestHeader(StrictModel):
    x_contentful_content_type: str | None = Field(default=None, validation_alias="X-Contentful-Content-Type", serialization_alias="X-Contentful-Content-Type", description="The content type ID that defines the structure and fields for this entry. This determines what fields are available and required for the entry.")
class PostSpacesEnvironmentsEntriesRequest(StrictModel):
    """Create a new entry in a Contentful space environment. Entries are the primary content objects that hold your data according to a defined content model."""
    path: PostSpacesEnvironmentsEntriesRequestPath
    header: PostSpacesEnvironmentsEntriesRequestHeader | None = None

# Operation: get_entry
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesByEntryIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space (e.g., '5nvk6q4s3ttw'). This identifies which space contains the entry.")
    environment_id: str = Field(default=..., description="The environment identifier within the space, typically 'master' for the main environment. Specifies which environment version of the entry to retrieve.")
    entry_id: str = Field(default=..., description="The unique identifier of the entry to retrieve (e.g., '4Mxj1aVYccLOCunUzsNcNL'). This identifies the specific entry within the environment.")
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesByEntryIdRequest(StrictModel):
    """Retrieve a single entry from a Contentful space and environment. Returns the complete entry object with all its fields and metadata."""
    path: GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesByEntryIdRequestPath

# Operation: upsert_entry
class PutSpacesEnvironmentsEntriesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the entry. This is the workspace where your content is organized.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space. Environments allow you to manage different versions of your content (e.g., draft, published).")
    entry_id: str = Field(default=..., description="The unique identifier of the entry to create or update. If the entry doesn't exist, it will be created; otherwise, the existing entry will be updated.")
class PutSpacesEnvironmentsEntriesRequestHeader(StrictModel):
    x_contentful_content_type: str | None = Field(default=None, validation_alias="X-Contentful-Content-Type", serialization_alias="X-Contentful-Content-Type", description="The content type ID that defines the structure and fields for this entry. This determines what fields are available and their validation rules.")
class PutSpacesEnvironmentsEntriesRequest(StrictModel):
    """Create a new entry or update an existing entry within a specific environment and space. This operation allows you to define or modify content entries in your Contentful workspace."""
    path: PutSpacesEnvironmentsEntriesRequestPath
    header: PutSpacesEnvironmentsEntriesRequestHeader | None = None

# Operation: update_entry
class PatchSpacesEnvironmentsEntriesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the entry to update.")
    environment_id: str = Field(default=..., description="The environment identifier where the entry resides. Typically 'master' for the default environment.")
    entry_id: str = Field(default=..., description="The unique identifier of the entry to update.")
class PatchSpacesEnvironmentsEntriesRequestHeader(StrictModel):
    x_contentful_content_type: str | None = Field(default=None, validation_alias="X-Contentful-Content-Type", serialization_alias="X-Contentful-Content-Type", description="The content type ID that defines the structure of the entry being updated.")
class PatchSpacesEnvironmentsEntriesRequest(StrictModel):
    """Partially update an entry within a Contentful space and environment. Use this operation to modify specific fields of an existing entry without replacing the entire entry."""
    path: PatchSpacesEnvironmentsEntriesRequestPath
    header: PatchSpacesEnvironmentsEntriesRequestHeader | None = None

# Operation: delete_entry
class DeleteSpacesEnvironmentsEntriesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the entry to delete.")
    environment_id: str = Field(default=..., description="The environment within the space where the entry exists. Typically 'master' for the main environment.")
    entry_id: str = Field(default=..., description="The unique identifier of the entry to delete.")
class DeleteSpacesEnvironmentsEntriesRequest(StrictModel):
    """Permanently delete an entry from a Contentful space environment. This action cannot be undone."""
    path: DeleteSpacesEnvironmentsEntriesRequestPath

# Operation: list_entry_references
class GetSpacesEnvironmentsEntriesReferencesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the entry (e.g., '5nvk6q4s3ttw').")
    environment_id: str = Field(default=..., description="The environment identifier within the space, typically 'master' for the default environment.")
    entry_id: str = Field(default=..., description="The unique identifier of the entry for which to retrieve references (e.g., '4Mxj1aVYccLOCunUzsNcNL').")
class GetSpacesEnvironmentsEntriesReferencesRequest(StrictModel):
    """Retrieve all entries that reference a specific entry within a Contentful space and environment. This helps identify content dependencies and relationships."""
    path: GetSpacesEnvironmentsEntriesReferencesRequestPath

# Operation: publish_entry
class PutSpacesEnvironmentsEntriesPublishedRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the entry to publish.")
    environment_id: str = Field(default=..., description="The environment where the entry will be published. Typically 'master' for the main environment.")
    entry_id: str = Field(default=..., description="The unique identifier of the entry to publish.")
class PutSpacesEnvironmentsEntriesPublishedRequest(StrictModel):
    """Publish an entry to make it publicly available. This operation marks the entry as published in the specified environment."""
    path: PutSpacesEnvironmentsEntriesPublishedRequestPath

# Operation: unpublish_entry
class DeleteSpacesEnvironmentsEntriesPublishedRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the entry to unpublish.")
    environment_id: str = Field(default=..., description="The environment identifier where the entry exists. Typically 'master' for the default environment.")
    entry_id: str = Field(default=..., description="The unique identifier of the entry to unpublish.")
class DeleteSpacesEnvironmentsEntriesPublishedRequest(StrictModel):
    """Unpublish an entry, removing it from the published state while keeping the draft version intact. This operation reverses a previous publish action."""
    path: DeleteSpacesEnvironmentsEntriesPublishedRequestPath

# Operation: archive_entry
class PutSpacesEnvironmentsEntriesArchivedRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the entry to archive.")
    environment_id: str = Field(default=..., description="The environment identifier where the entry resides. Typically 'master' for the default environment.")
    entry_id: str = Field(default=..., description="The unique identifier of the entry to archive.")
class PutSpacesEnvironmentsEntriesArchivedRequest(StrictModel):
    """Archive an entry in a Contentful space environment. Archived entries are hidden from published content but retained for historical reference."""
    path: PutSpacesEnvironmentsEntriesArchivedRequestPath

# Operation: unarchive_entry
class DeleteSpacesEnvironmentsEntriesArchivedRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the entry.")
    environment_id: str = Field(default=..., description="The environment identifier where the entry is stored. Typically 'master' for the default environment.")
    entry_id: str = Field(default=..., description="The unique identifier of the entry to unarchive.")
class DeleteSpacesEnvironmentsEntriesArchivedRequest(StrictModel):
    """Restore an archived entry to active status in a Contentful space. This operation reverses the archival of an entry, making it available for use again."""
    path: DeleteSpacesEnvironmentsEntriesArchivedRequestPath

# Operation: upload_file
class PostSpacesUploadsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space where the file will be uploaded.")
class PostSpacesUploadsRequest(StrictModel):
    """Upload a file to a Contentful space. The uploaded file can then be used as an asset within the space."""
    path: PostSpacesUploadsRequestPath

# Operation: get_upload
class GetSpacesUploadsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the upload.")
    upload_id: str = Field(default=..., description="The unique identifier of the upload to retrieve.")
class GetSpacesUploadsRequest(StrictModel):
    """Retrieve details about a specific upload in a space. Use this to check the status and metadata of a previously created upload."""
    path: GetSpacesUploadsRequestPath

# Operation: delete_upload
class DeleteSpacesUploadsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the upload to delete.")
    upload_id: str = Field(default=..., description="The unique identifier of the upload to delete.")
class DeleteSpacesUploadsRequest(StrictModel):
    """Permanently delete an upload from a Contentful space. Once deleted, the upload cannot be recovered."""
    path: DeleteSpacesUploadsRequestPath

# Operation: list_assets
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAssetsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the assets you want to retrieve.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space from which to fetch assets.")
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAssetsRequest(StrictModel):
    """Retrieve all assets in a specific environment within a space. Assets are media files and other resources managed in Contentful."""
    path: GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAssetsRequestPath

# Operation: create_asset
class PostSpacesEnvironmentsAssetsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space where the asset will be created.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the asset will be created.")
class PostSpacesEnvironmentsAssetsRequest(StrictModel):
    """Create a new asset in a specified Contentful space and environment. Assets are files and media that can be referenced by content entries."""
    path: PostSpacesEnvironmentsAssetsRequestPath

# Operation: list_published_assets
class GetSpacesEnvironmentsPublicAssetsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the assets.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space from which to retrieve published assets.")
class GetSpacesEnvironmentsPublicAssetsRequest(StrictModel):
    """Retrieve all published assets for a specific space and environment. This returns assets that have been explicitly published and are available for use."""
    path: GetSpacesEnvironmentsPublicAssetsRequestPath

# Operation: get_asset
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAssetsByAssetIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the asset.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the asset is located.")
    asset_id: str = Field(default=..., description="The unique identifier of the asset to retrieve (e.g., B1fZbskHLWGKIVuZySN5P).")
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAssetsByAssetIdRequest(StrictModel):
    """Retrieve a single asset from a specific environment within a space. Assets are media files and other resources managed in Contentful."""
    path: GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAssetsByAssetIdRequestPath

# Operation: create_or_update_asset
class PutSpacesEnvironmentsAssetsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the asset.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the asset is located.")
    asset_id: str = Field(default=..., description="The unique identifier of the asset to create or update. If the asset does not exist, it will be created with this ID.")
class PutSpacesEnvironmentsAssetsRequest(StrictModel):
    """Create a new asset or update an existing asset in a Contentful space environment. Use this operation to manage media files and other assets within your content management system."""
    path: PutSpacesEnvironmentsAssetsRequestPath

# Operation: delete_asset
class DeleteSpacesEnvironmentsAssetsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the asset to delete.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the asset is located.")
    asset_id: str = Field(default=..., description="The unique identifier of the asset to delete.")
class DeleteSpacesEnvironmentsAssetsRequest(StrictModel):
    """Permanently delete an asset from a specific environment within a space. This action cannot be undone."""
    path: DeleteSpacesEnvironmentsAssetsRequestPath

# Operation: process_asset_file
class PutSpacesEnvironmentsAssetsFilesProcessRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the asset.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the asset is located.")
    asset_id: str = Field(default=..., description="The unique identifier of the asset file to process.")
    locale_code: str = Field(default=..., description="The locale code for the asset file variant to process, specified in language-region format (e.g., en-us for US English).")
class PutSpacesEnvironmentsAssetsFilesProcessRequest(StrictModel):
    """Trigger processing of an asset file in a specific locale within a Contentful space and environment. This initiates any necessary transformations or optimizations for the uploaded asset."""
    path: PutSpacesEnvironmentsAssetsFilesProcessRequestPath

# Operation: publish_asset
class PutSpacesEnvironmentsAssetsPublishedRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the asset to publish.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment where the asset will be published.")
    asset_id: str = Field(default=..., description="The unique identifier of the asset to publish.")
class PutSpacesEnvironmentsAssetsPublishedRequest(StrictModel):
    """Publish an asset to make it available in the specified environment. Publishing an asset marks it as ready for use in your content delivery pipeline."""
    path: PutSpacesEnvironmentsAssetsPublishedRequestPath

# Operation: unpublish_asset
class DeleteSpacesEnvironmentsAssetsPublishedRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the asset.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment from which to unpublish the asset.")
    asset_id: str = Field(default=..., description="The unique identifier of the asset to unpublish.")
class DeleteSpacesEnvironmentsAssetsPublishedRequest(StrictModel):
    """Unpublish an asset from a specific environment, making it unavailable to content consumers while retaining the asset in the space."""
    path: DeleteSpacesEnvironmentsAssetsPublishedRequestPath

# Operation: archive_asset
class PutSpacesEnvironmentsAssetsArchivedRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the asset.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the asset is located.")
    asset_id: str = Field(default=..., description="The unique identifier of the asset to archive.")
class PutSpacesEnvironmentsAssetsArchivedRequest(StrictModel):
    """Archive an asset in a Contentful space environment. Archived assets are hidden from delivery but retained for historical purposes."""
    path: PutSpacesEnvironmentsAssetsArchivedRequestPath

# Operation: unarchive_asset
class DeleteSpacesEnvironmentsAssetsArchivedRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the asset.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the asset is located.")
    asset_id: str = Field(default=..., description="The unique identifier of the asset to unarchive.")
class DeleteSpacesEnvironmentsAssetsArchivedRequest(StrictModel):
    """Restore an archived asset in a specific environment, making it available for use again. This operation removes the archived status from the asset."""
    path: DeleteSpacesEnvironmentsAssetsArchivedRequestPath

# Operation: create_asset_key
class PostSpacesEnvironmentsAssetKeysRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space where the asset key will be created.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the asset key will be created.")
class PostSpacesEnvironmentsAssetKeysRequest(StrictModel):
    """Create a new asset key within a specific environment. Asset keys are used to manage and organize digital assets in your content space."""
    path: PostSpacesEnvironmentsAssetKeysRequestPath

# Operation: list_locales
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdLocalesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the environment and locales to retrieve.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space from which to fetch locales.")
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdLocalesRequest(StrictModel):
    """Retrieve all locales configured for a specific environment within a space. Locales define the languages and regional variants available for content in that environment."""
    path: GetSpacesBySpaceIdEnvironmentsByEnvironmentIdLocalesRequestPath

# Operation: create_locale
class PostSpacesEnvironmentsLocalesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space where the locale will be created (e.g., 'r0926rqjrebl').")
    environment_id: str = Field(default=..., description="The environment identifier within the space where the locale will be added (e.g., 'master' for the default environment).")
class PostSpacesEnvironmentsLocalesRequest(StrictModel):
    """Create a new locale within a specific environment of a Contentful space. Locales define the languages and regional variants available for content in your space."""
    path: PostSpacesEnvironmentsLocalesRequestPath

# Operation: get_locale
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdLocalesByLocaleIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the locale.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space.")
    locale_id: str = Field(default=..., description="The unique identifier of the locale to retrieve.")
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdLocalesByLocaleIdRequest(StrictModel):
    """Retrieve a specific locale configuration for a given space and environment. Locales define language and regional settings for content management."""
    path: GetSpacesBySpaceIdEnvironmentsByEnvironmentIdLocalesByLocaleIdRequestPath

# Operation: update_locale
class PutSpacesEnvironmentsLocalesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the locale to update.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the locale resides.")
    locale_id: str = Field(default=..., description="The unique identifier of the locale to update.")
class PutSpacesEnvironmentsLocalesRequest(StrictModel):
    """Update the configuration of a specific locale within a Contentful environment, such as display name or other locale settings."""
    path: PutSpacesEnvironmentsLocalesRequestPath

# Operation: delete_locale
class DeleteSpacesEnvironmentsLocalesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the locale to delete.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the locale exists.")
    locale_id: str = Field(default=..., description="The unique identifier of the locale to delete.")
class DeleteSpacesEnvironmentsLocalesRequest(StrictModel):
    """Permanently delete a locale from a specific environment within a space. This action removes the locale configuration and cannot be undone."""
    path: DeleteSpacesEnvironmentsLocalesRequestPath

# Operation: list_environment_tags
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdTagsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the environment. This is required to scope the request to the correct workspace.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space. This specifies which environment's tags should be retrieved.")
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdTagsRequest(StrictModel):
    """Retrieve all tags configured for a specific environment within a space. Tags are used to organize and categorize content management UI extensions."""
    path: GetSpacesBySpaceIdEnvironmentsByEnvironmentIdTagsRequestPath

# Operation: get_tag
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdTagsByTagIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the tag.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the tag is located.")
    tag_id: str = Field(default=..., description="The unique identifier of the tag to retrieve.")
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdTagsByTagIdRequest(StrictModel):
    """Retrieve a single tag from a specific environment within a space. Tags are used to organize and categorize content in Contentful."""
    path: GetSpacesBySpaceIdEnvironmentsByEnvironmentIdTagsByTagIdRequestPath

# Operation: create_tag
class PostSpacesEnvironmentsTagsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the environment where the tag will be created.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the tag will be created.")
    tag_id: str = Field(default=..., description="The unique identifier for the tag being created.")
class PostSpacesEnvironmentsTagsRequest(StrictModel):
    """Create a new tag within a specific environment in Contentful. Tags are used to organize and categorize content for better management and filtering."""
    path: PostSpacesEnvironmentsTagsRequestPath

# Operation: update_tag
class PutSpacesEnvironmentsTagsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the tag to be updated.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the tag is located.")
    tag_id: str = Field(default=..., description="The unique identifier of the tag to be updated.")
class PutSpacesEnvironmentsTagsRequest(StrictModel):
    """Update an existing tag within a specific environment and space. This operation allows you to modify tag properties and settings."""
    path: PutSpacesEnvironmentsTagsRequestPath

# Operation: delete_tag
class DeleteSpacesEnvironmentsTagsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the environment and tag to be deleted.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space that contains the tag to be deleted.")
    tag_id: str = Field(default=..., description="The unique identifier of the tag to be deleted.")
class DeleteSpacesEnvironmentsTagsRequest(StrictModel):
    """Remove a tag from a specific environment within a space. This permanently deletes the tag and its associations."""
    path: DeleteSpacesEnvironmentsTagsRequestPath

# Operation: list_webhooks
class GetSpacesBySpaceIdWebhookDefinitionsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the webhooks you want to retrieve (e.g., '5nvk6q4s3ttw').")
class GetSpacesBySpaceIdWebhookDefinitionsRequest(StrictModel):
    """Retrieve all webhook definitions configured for a specific space. Webhooks allow you to receive HTTP notifications when content changes occur in your space."""
    path: GetSpacesBySpaceIdWebhookDefinitionsRequestPath

# Operation: list_webhook_calls
class GetSpacesBySpaceIdWebhooksByWebhookIdCallsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the webhook. This is required to scope the webhook calls to the correct environment.")
    webhook_id: str = Field(default=..., description="The unique identifier of the webhook whose call history you want to retrieve. This specifies which webhook's execution log to fetch.")
class GetSpacesBySpaceIdWebhooksByWebhookIdCallsRequest(StrictModel):
    """Retrieve a list of recent webhook call attempts for a specific webhook, including their status and execution details. This helps monitor webhook delivery and troubleshoot integration issues."""
    path: GetSpacesBySpaceIdWebhooksByWebhookIdCallsRequestPath

# Operation: get_webhook_call
class GetSpacesBySpaceIdWebhooksByWebhookIdCallsByCallIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the webhook.")
    webhook_id: str = Field(default=..., description="The unique identifier of the webhook for which to retrieve call details.")
    call_id: str = Field(default=..., description="The unique identifier of the specific webhook call to retrieve.")
class GetSpacesBySpaceIdWebhooksByWebhookIdCallsByCallIdRequest(StrictModel):
    """Retrieve detailed information about a specific webhook call, including its request, response, and execution status."""
    path: GetSpacesBySpaceIdWebhooksByWebhookIdCallsByCallIdRequestPath

# Operation: check_webhook_health
class GetSpacesWebhooksHealthRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the webhook.")
    webhook_id: str = Field(default=..., description="The unique identifier of the webhook whose health status should be retrieved.")
class GetSpacesWebhooksHealthRequest(StrictModel):
    """Retrieve the health status and diagnostic information for a specific webhook in a space, including recent delivery attempts and error details."""
    path: GetSpacesWebhooksHealthRequestPath

# Operation: get_webhook_definition
class GetSpacesBySpaceIdWebhookDefinitionsByWebhookDefinitionIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the webhook definition.")
    webhook_definition_id: str = Field(default=..., description="The unique identifier of the webhook definition to retrieve.")
class GetSpacesBySpaceIdWebhookDefinitionsByWebhookDefinitionIdRequest(StrictModel):
    """Retrieve a single webhook definition by its ID. Returns the complete configuration and metadata for the specified webhook in a Contentful space."""
    path: GetSpacesBySpaceIdWebhookDefinitionsByWebhookDefinitionIdRequestPath

# Operation: delete_role
class DeleteSpacesRolesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the role to delete.")
    role_id: str = Field(default=..., description="The unique identifier of the role to delete.")
class DeleteSpacesRolesRequest(StrictModel):
    """Permanently delete a role from a space. This action removes the role and all associated permissions, affecting any users or API tokens assigned to this role."""
    path: DeleteSpacesRolesRequestPath

# Operation: list_entry_snapshots
class GetSpacesBySpaceIdEnvironmentsMasterEntriesByEntryIdSnapshotsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the entry. This is a required alphanumeric identifier that specifies which workspace to query.")
    entry_id: str = Field(default=..., description="The unique identifier of the entry for which to retrieve snapshots. This is a required alphanumeric identifier that specifies which entry's version history to fetch.")
class GetSpacesBySpaceIdEnvironmentsMasterEntriesByEntryIdSnapshotsRequest(StrictModel):
    """Retrieve all snapshots for a specific entry in the master environment. Snapshots capture the state of an entry at different points in time, allowing you to view historical versions and changes."""
    path: GetSpacesBySpaceIdEnvironmentsMasterEntriesByEntryIdSnapshotsRequestPath

# Operation: list_content_type_snapshots
class GetSpacesBySpaceIdEnvironmentsMasterContentTypesByContentTypeIdSnapshotsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the content type.")
    content_type_id: str = Field(default=..., description="The unique identifier of the content type for which to retrieve snapshots.")
class GetSpacesBySpaceIdEnvironmentsMasterContentTypesByContentTypeIdSnapshotsRequest(StrictModel):
    """Retrieve all snapshots for a specific content type in the master environment. Snapshots capture the state of a content type at different points in time, allowing you to track changes and restore previous versions."""
    path: GetSpacesBySpaceIdEnvironmentsMasterContentTypesByContentTypeIdSnapshotsRequestPath

# Operation: get_content_type_snapshot
class GetSpacesBySpaceIdEnvironmentsMasterContentTypesByContentTypeIdSnapshotsBySnapshotIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the content type.")
    content_type_id: str = Field(default=..., description="The unique identifier of the content type for which to retrieve the snapshot.")
    snapshot_id: str = Field(default=..., description="The unique identifier of the snapshot to retrieve.")
class GetSpacesBySpaceIdEnvironmentsMasterContentTypesByContentTypeIdSnapshotsBySnapshotIdRequest(StrictModel):
    """Retrieve a specific snapshot of a content type, allowing you to view the content type definition at a particular point in time."""
    path: GetSpacesBySpaceIdEnvironmentsMasterContentTypesByContentTypeIdSnapshotsBySnapshotIdRequestPath

# Operation: get_entry_snapshot
class GetSpacesBySpaceIdEnvironmentsMasterEntriesByEntryIdSnapshotsBySnapshotIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the entry.")
    entry_id: str = Field(default=..., description="The unique identifier of the entry for which you want to retrieve the snapshot.")
    snapshot_id: str = Field(default=..., description="The unique identifier of the snapshot to retrieve.")
class GetSpacesBySpaceIdEnvironmentsMasterEntriesByEntryIdSnapshotsBySnapshotIdRequest(StrictModel):
    """Retrieve a specific snapshot of an entry, allowing you to view the entry's state at a particular point in time."""
    path: GetSpacesBySpaceIdEnvironmentsMasterEntriesByEntryIdSnapshotsBySnapshotIdRequestPath

# Operation: list_space_memberships
class GetSpacesBySpaceIdSpaceMembershipsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space. Use the space ID to target a specific workspace (e.g., '5nvk6q4s3ttw').")
class GetSpacesBySpaceIdSpaceMembershipsRequest(StrictModel):
    """Retrieve all space memberships for a given space. Returns a collection of all users and their roles within the specified space."""
    path: GetSpacesBySpaceIdSpaceMembershipsRequestPath

# Operation: create_space_membership
class PostSpacesSpaceMembershipsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space where the membership will be created.")
class PostSpacesSpaceMembershipsRequest(StrictModel):
    """Add a new member to a space with specified roles and permissions. This operation creates a space membership record that grants a user or team access to the space."""
    path: PostSpacesSpaceMembershipsRequestPath

# Operation: get_space_membership
class GetSpacesBySpaceIdSpaceMembershipsBySpaceMembershipIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the membership.")
    space_membership_id: str = Field(default=..., description="The unique identifier of the space membership to retrieve.")
class GetSpacesBySpaceIdSpaceMembershipsBySpaceMembershipIdRequest(StrictModel):
    """Retrieve a specific space membership by its ID. Returns detailed information about a user's membership and role within a Contentful space."""
    path: GetSpacesBySpaceIdSpaceMembershipsBySpaceMembershipIdRequestPath

# Operation: update_space_membership
class PutSpacesSpaceMembershipsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the membership to update.")
    space_membership_id: str = Field(default=..., description="The unique identifier of the space membership record to update.")
class PutSpacesSpaceMembershipsRequest(StrictModel):
    """Update a space membership to modify user roles and permissions within a specific space. This operation allows you to change access levels and membership details for a user in the space."""
    path: PutSpacesSpaceMembershipsRequestPath

# Operation: remove_space_member
class DeleteSpacesSpaceMembershipsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space from which the member will be removed.")
    space_membership_id: str = Field(default=..., description="The unique identifier of the space membership record to delete.")
class DeleteSpacesSpaceMembershipsRequest(StrictModel):
    """Remove a member from a space by deleting their space membership. This revokes their access to the specified space."""
    path: DeleteSpacesSpaceMembershipsRequestPath

# Operation: list_teams
class GetSpacesTeamsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space for which to retrieve teams.")
class GetSpacesTeamsRequest(StrictModel):
    """Retrieve all teams associated with a specific space. Teams are organizational units within a space that can be assigned permissions and manage content collaboratively."""
    path: GetSpacesTeamsRequestPath

# Operation: get_delivery_api_key
class GetSpacesBySpaceIdApiKeysByApiKeyIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the API key.")
    api_key_id: str = Field(default=..., description="The unique identifier of the Delivery API key to retrieve.")
class GetSpacesBySpaceIdApiKeysByApiKeyIdRequest(StrictModel):
    """Retrieve a specific Delivery API key for a space. Use this to view details of an existing API key used for content delivery."""
    path: GetSpacesBySpaceIdApiKeysByApiKeyIdRequestPath

# Operation: update_delivery_api_key
class PutSpacesApiKeysRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the API key to update.")
    api_key_id: str = Field(default=..., description="The unique identifier of the Delivery API key to update.")
class PutSpacesApiKeysRequest(StrictModel):
    """Update the configuration of a Delivery API key within a space. This allows you to modify settings for an existing API key used for content delivery."""
    path: PutSpacesApiKeysRequestPath

# Operation: delete_delivery_api_key
class DeleteSpacesApiKeysRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the API key to delete.")
    api_key_id: str = Field(default=..., description="The unique identifier of the Delivery API key to delete.")
class DeleteSpacesApiKeysRequest(StrictModel):
    """Permanently delete a Delivery API key from a space. This action cannot be undone and will immediately revoke access for any applications using this key."""
    path: DeleteSpacesApiKeysRequestPath

# Operation: list_delivery_api_keys
class GetSpacesBySpaceIdApiKeysRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the API keys to retrieve.")
class GetSpacesBySpaceIdApiKeysRequest(StrictModel):
    """Retrieve all Delivery API keys configured for a specific space. These keys are used to access published content through the Contentful Delivery API."""
    path: GetSpacesBySpaceIdApiKeysRequestPath

# Operation: create_delivery_api_key
class PostSpacesApiKeysRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space where the API key will be created.")
class PostSpacesApiKeysRequest(StrictModel):
    """Create a new Delivery API key for a Contentful space to enable read-only access to published content via the Delivery API."""
    path: PostSpacesApiKeysRequestPath

# Operation: list_preview_api_keys
class GetSpacesBySpaceIdPreviewApiKeysRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the Preview API keys to retrieve.")
class GetSpacesBySpaceIdPreviewApiKeysRequest(StrictModel):
    """Retrieve all Preview API keys for a specific space. Preview API keys are used to access published content in a read-only manner."""
    path: GetSpacesBySpaceIdPreviewApiKeysRequestPath

# Operation: get_preview_api_key
class GetSpacesBySpaceIdPreviewApiKeysByPreviewApiKeyIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the Preview API key.")
    preview_api_key_id: str = Field(default=..., description="The unique identifier of the Preview API key to retrieve.")
class GetSpacesBySpaceIdPreviewApiKeysByPreviewApiKeyIdRequest(StrictModel):
    """Retrieve a single Preview API key for a specific space. Preview API keys are used to access published content in a read-only manner."""
    path: GetSpacesBySpaceIdPreviewApiKeysByPreviewApiKeyIdRequestPath

# Operation: get_access_token
class GetUsersMeAccessTokensByTokenIdRequestPath(StrictModel):
    token_id: str = Field(default=..., description="The unique identifier of the personal access token to retrieve.")
class GetUsersMeAccessTokensByTokenIdRequest(StrictModel):
    """Retrieve a specific personal access token by its ID. This allows you to view details about an individual access token associated with your account."""
    path: GetUsersMeAccessTokensByTokenIdRequestPath

# Operation: revoke_access_token
class PutUsersMeAccessTokensRevokedRequestPath(StrictModel):
    token_id: str = Field(default=..., description="The unique identifier of the personal access token to revoke.")
class PutUsersMeAccessTokensRevokedRequest(StrictModel):
    """Revoke a personal access token to immediately invalidate it and prevent further API access using that token."""
    path: PutUsersMeAccessTokensRevokedRequestPath

# Operation: list_entry_tasks
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesByEntryIdTasksRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the entry.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the entry resides.")
    entry_id: str = Field(default=..., description="The unique identifier of the entry for which to retrieve associated tasks.")
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesByEntryIdTasksRequest(StrictModel):
    """Retrieve all tasks associated with a specific entry within a Contentful environment. Tasks represent workflow actions or assignments related to the entry."""
    path: GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesByEntryIdTasksRequestPath

# Operation: create_entry_task
class PostSpacesEnvironmentsEntriesTasksRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the entry.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the entry resides.")
    entry_id: str = Field(default=..., description="The unique identifier of the entry for which the task is being created.")
class PostSpacesEnvironmentsEntriesTasksRequest(StrictModel):
    """Create a task for a specific entry within a Contentful space and environment. Tasks are used to track workflows and actions associated with content entries."""
    path: PostSpacesEnvironmentsEntriesTasksRequestPath

# Operation: get_task
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesByEntryIdTasksByTaskIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the task.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space.")
    entry_id: str = Field(default=..., description="The unique identifier of the entry that contains the task.")
    task_id: str = Field(default=..., description="The unique identifier of the task to retrieve.")
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesByEntryIdTasksByTaskIdRequest(StrictModel):
    """Retrieve a specific task associated with an entry. Tasks are used to track workflows and approvals within Contentful entries."""
    path: GetSpacesBySpaceIdEnvironmentsByEnvironmentIdEntriesByEntryIdTasksByTaskIdRequestPath

# Operation: update_task
class PutSpacesEnvironmentsEntriesTasksRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the entry and task to update.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the task exists.")
    entry_id: str = Field(default=..., description="The unique identifier of the entry that the task is associated with.")
    task_id: str = Field(default=..., description="The unique identifier of the task to update.")
class PutSpacesEnvironmentsEntriesTasksRequest(StrictModel):
    """Update an existing task associated with a specific entry in a Contentful environment. This allows you to modify task details such as status, assignees, or other task-related metadata."""
    path: PutSpacesEnvironmentsEntriesTasksRequestPath

# Operation: delete_task
class DeleteSpacesEnvironmentsEntriesTasksRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the entry and task to be deleted.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the entry and task reside.")
    entry_id: str = Field(default=..., description="The unique identifier of the entry that contains the task to be deleted.")
    task_id: str = Field(default=..., description="The unique identifier of the task to be deleted.")
class DeleteSpacesEnvironmentsEntriesTasksRequest(StrictModel):
    """Permanently delete a specific task associated with an entry. This removes the task and all its related data from the entry."""
    path: DeleteSpacesEnvironmentsEntriesTasksRequestPath

# Operation: list_scheduled_actions
class GetSpacesScheduledActionsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the scheduled actions you want to retrieve.")
class GetSpacesScheduledActionsRequest(StrictModel):
    """Retrieve all scheduled actions for a specific space. Scheduled actions allow you to automate content management tasks at predetermined times."""
    path: GetSpacesScheduledActionsRequestPath

# Operation: create_scheduled_action
class PostSpacesScheduledActionsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space where the scheduled action will be created.")
class PostSpacesScheduledActionsRequest(StrictModel):
    """Create a new scheduled action within a space. Scheduled actions allow you to automate content management tasks at specified times."""
    path: PostSpacesScheduledActionsRequestPath

# Operation: update_scheduled_action
class PutSpacesScheduledActionsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the scheduled action to update.")
    scheduled_action_id: str = Field(default=..., description="The unique identifier of the scheduled action to update.")
class PutSpacesScheduledActionsRequest(StrictModel):
    """Update an existing scheduled action in a space. Modify the configuration and settings of a scheduled action that has been previously created."""
    path: PutSpacesScheduledActionsRequestPath

# Operation: cancel_scheduled_action
class DeleteSpacesScheduledActionsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the scheduled action to cancel.")
    scheduled_action_id: str = Field(default=..., description="The unique identifier of the scheduled action to cancel.")
class DeleteSpacesScheduledActionsRequest(StrictModel):
    """Cancel a scheduled action in a space. This prevents the scheduled action from executing at its designated time."""
    path: DeleteSpacesScheduledActionsRequestPath

# Operation: list_releases
class GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the environment and releases.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space from which to retrieve releases.")
class GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesRequest(StrictModel):
    """Retrieve all scheduled releases for a specific environment within a space. This allows you to query and manage content publication schedules."""
    path: GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesRequestPath

# Operation: create_environment_release
class PostSpacesEnvironmentReleasesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the environment where the release will be created.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the release will be created.")
class PostSpacesEnvironmentReleasesRequest(StrictModel):
    """Create a new release for a specific environment within a space. Releases allow you to schedule and manage content deployments across your Contentful workspace."""
    path: PostSpacesEnvironmentReleasesRequestPath

# Operation: validate_release
class PostSpacesEnvironmentReleasesValidateRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the release.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment where the release will be validated.")
    releases_id: str = Field(default=..., description="The unique identifier of the release to validate.")
class PostSpacesEnvironmentReleasesValidateRequest(StrictModel):
    """Create a validation action for a scheduled release in a specific environment. This initiates validation of the release's contents before it can be published."""
    path: PostSpacesEnvironmentReleasesValidateRequestPath

# Operation: list_release_actions
class GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesByReleasesIdActionsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the release.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the release exists.")
    releases_id: str = Field(default=..., description="The unique identifier of the release for which to retrieve associated actions.")
class GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesByReleasesIdActionsRequest(StrictModel):
    """Retrieve all scheduled actions associated with a specific release in a Contentful environment. This allows you to query and monitor the actions planned for a release."""
    path: GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesByReleasesIdActionsRequestPath

# Operation: get_release_action
class GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesByReleasesIdActionsByReleaseActionIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the release and action.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the release action is defined.")
    releases_id: str = Field(default=..., description="The unique identifier of the release that contains the action.")
    release_action_id: str = Field(default=..., description="The unique identifier of the specific release action to retrieve.")
class GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesByReleasesIdActionsByReleaseActionIdRequest(StrictModel):
    """Retrieve a specific scheduled action within a release. Use this to fetch details about a single release action, such as its status, timing, and associated content changes."""
    path: GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesByReleasesIdActionsByReleaseActionIdRequestPath

# Operation: publish_release
class PutSpacesEnvironmentReleasesPublishedRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the release to be published.")
    releases_id: str = Field(default=..., description="The unique identifier of the release to publish.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment where the release will be published.")
class PutSpacesEnvironmentReleasesPublishedRequest(StrictModel):
    """Publish a release to make its scheduled changes live in the specified environment. This marks the release as published and applies all contained entries and assets to the target environment."""
    path: PutSpacesEnvironmentReleasesPublishedRequestPath

# Operation: unpublish_release
class DeleteSpacesEnvironmentReleasesPublishedRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the release.")
    releases_id: str = Field(default=..., description="The unique identifier of the release to unpublish.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment where the release is published.")
class DeleteSpacesEnvironmentReleasesPublishedRequest(StrictModel):
    """Unpublish a scheduled release, removing it from the published state and preventing its scheduled actions from executing."""
    path: DeleteSpacesEnvironmentReleasesPublishedRequestPath

# Operation: get_release
class GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesByReleasesIdRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the release.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the release is located.")
    releases_id: str = Field(default=..., description="The unique identifier of the release to retrieve.")
class GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesByReleasesIdRequest(StrictModel):
    """Retrieve a single scheduled release by its ID within a specific space and environment. This operation fetches detailed information about a release, including its scheduled actions and metadata."""
    path: GetSpacesBySpaceIdEnvironmentByEnvironmentIdReleasesByReleasesIdRequestPath

# Operation: update_release
class PutSpacesEnvironmentReleasesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the Contentful space containing the release to update.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the release exists.")
    releases_id: str = Field(default=..., description="The unique identifier of the release to update.")
class PutSpacesEnvironmentReleasesRequest(StrictModel):
    """Update an existing release in a Contentful space environment. This operation allows you to modify release details such as scheduling, metadata, or other release properties."""
    path: PutSpacesEnvironmentReleasesRequestPath

# Operation: delete_release
class DeleteSpacesEnvironmentReleasesRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the release to be deleted.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the release exists.")
    releases_id: str = Field(default=..., description="The unique identifier of the release to be permanently removed.")
class DeleteSpacesEnvironmentReleasesRequest(StrictModel):
    """Permanently remove a scheduled release from a specific environment within a space. This action cannot be undone."""
    path: DeleteSpacesEnvironmentReleasesRequestPath

# Operation: get_bulk_action
class GetSpacesEnvironmentBulkActionsActionsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the bulk action.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the bulk action is located.")
    bulk_action_id: str = Field(default=..., description="The unique identifier of the bulk action to retrieve.")
class GetSpacesEnvironmentBulkActionsActionsRequest(StrictModel):
    """Retrieve details of a specific bulk action by its ID within a given space and environment. Use this to check the status and results of scheduled bulk operations."""
    path: GetSpacesEnvironmentBulkActionsActionsRequestPath

# Operation: publish_scheduled_actions
class PostSpacesEnvironmentBulkActionsPublishRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the environment where scheduled actions will be published.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the scheduled bulk actions will be published.")
class PostSpacesEnvironmentBulkActionsPublishRequest(StrictModel):
    """Publish scheduled bulk actions for a specific environment, making them active and executable. This operation processes pending scheduled actions that have been queued for publication."""
    path: PostSpacesEnvironmentBulkActionsPublishRequestPath

# Operation: unpublish_scheduled_actions
class PostSpacesEnvironmentBulkActionsUnpublishRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the environment where scheduled actions will be unpublished.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where scheduled actions will be unpublished.")
class PostSpacesEnvironmentBulkActionsUnpublishRequest(StrictModel):
    """Unpublish scheduled actions in bulk for a specific environment. This operation reverts previously scheduled publish actions, preventing them from being executed."""
    path: PostSpacesEnvironmentBulkActionsUnpublishRequestPath

# Operation: validate_scheduled_bulk_action
class PostSpacesEnvironmentBulkActionsValidateRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the environment where the bulk action will be validated.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment where the bulk action will be executed and validated.")
class PostSpacesEnvironmentBulkActionsValidateRequest(StrictModel):
    """Validate a bulk action before execution in a specific environment. This operation checks the bulk action configuration for errors and ensures it can be safely scheduled."""
    path: PostSpacesEnvironmentBulkActionsValidateRequestPath

# Operation: list_app_definitions
class GetOrganizationsByOrganizationIdAppDefinitionsRequestPath(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier of the organization for which to retrieve app definitions.")
class GetOrganizationsByOrganizationIdAppDefinitionsRequest(StrictModel):
    """Retrieve all app definitions for a specific organization. App definitions describe the configuration and capabilities of apps available within the organization."""
    path: GetOrganizationsByOrganizationIdAppDefinitionsRequestPath

# Operation: delete_app_definition
class DeleteOrganizationsAppDefinitionsRequestPath(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier of the organization that contains the app definition to be deleted.")
    app_definition_id: str = Field(default=..., description="The unique identifier of the app definition to be deleted.")
class DeleteOrganizationsAppDefinitionsRequest(StrictModel):
    """Permanently delete an app definition from an organization. This action cannot be undone and will remove the app definition and all associated configurations."""
    path: DeleteOrganizationsAppDefinitionsRequestPath

# Operation: get_app_signing_secret
class GetOrganizationsAppDefinitionsSigningSecretRequestPath(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier of the organization that owns the app definition.")
    app_definition_id: str = Field(default=..., description="The unique identifier of the app definition for which to retrieve the signing secret.")
class GetOrganizationsAppDefinitionsSigningSecretRequest(StrictModel):
    """Retrieve the current cryptographic signing secret for an app definition. This secret is used to verify the authenticity of requests from Contentful to your app."""
    path: GetOrganizationsAppDefinitionsSigningSecretRequestPath

# Operation: set_app_signing_secret
class PutOrganizationsAppDefinitionsSigningSecretRequestPath(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier of the organization that owns the app definition.")
    app_definition_id: str = Field(default=..., description="The unique identifier of the app definition for which to set the signing secret.")
class PutOrganizationsAppDefinitionsSigningSecretRequest(StrictModel):
    """Create or overwrite the signing secret for an app definition. This secret is used to verify the authenticity of requests from Contentful to your app."""
    path: PutOrganizationsAppDefinitionsSigningSecretRequestPath

# Operation: revoke_app_signing_secret
class DeleteOrganizationsAppDefinitionsSigningSecretRequestPath(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier of the organization that owns the app definition.")
    app_definition_id: str = Field(default=..., description="The unique identifier of the app definition whose signing secret should be revoked.")
class DeleteOrganizationsAppDefinitionsSigningSecretRequest(StrictModel):
    """Revoke and remove the current signing secret for an app definition. This invalidates the existing secret, requiring a new one to be generated for future app authentications."""
    path: DeleteOrganizationsAppDefinitionsSigningSecretRequestPath

# Operation: list_app_keys
class GetOrganizationsByOrganizationIdAppDefinitionsByAppDefinitionIdKeysRequestPath(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier of the organization that contains the app definition.")
    app_definition_id: str = Field(default=..., description="The unique identifier of the app definition for which to retrieve all associated API keys.")
class GetOrganizationsByOrganizationIdAppDefinitionsByAppDefinitionIdKeysRequest(StrictModel):
    """Retrieve all API keys associated with a specific app definition within an organization. This allows you to manage and view the credentials used for app authentication."""
    path: GetOrganizationsByOrganizationIdAppDefinitionsByAppDefinitionIdKeysRequestPath

# Operation: delete_app_key
class DeleteOrganizationsAppDefinitionsKeysRequestPath(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier of the organization that owns the app definition.")
    app_definition_id: str = Field(default=..., description="The unique identifier of the app definition containing the key to be deleted.")
    key_kid: str = Field(default=..., description="The unique identifier (kid) of the specific key to delete from the app definition.")
class DeleteOrganizationsAppDefinitionsKeysRequest(StrictModel):
    """Delete a specific cryptographic key associated with an app definition. This removes the key from the app definition, preventing it from being used for authentication or signing operations."""
    path: DeleteOrganizationsAppDefinitionsKeysRequestPath

# Operation: list_app_installations
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAppInstallationsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the environment and app installations.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space for which to retrieve app installations.")
class GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAppInstallationsRequest(StrictModel):
    """Retrieve all app installations configured for a specific environment within a space. This returns the complete list of installed applications and their configurations."""
    path: GetSpacesBySpaceIdEnvironmentsByEnvironmentIdAppInstallationsRequestPath

# Operation: uninstall_app
class DeleteSpacesEnvironmentsAppInstallationsRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the environment where the app is installed.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment from which the app will be uninstalled.")
    app_definition_id: str = Field(default=..., description="The unique identifier of the app definition to uninstall.")
class DeleteSpacesEnvironmentsAppInstallationsRequest(StrictModel):
    """Remove an installed app from a specific environment within a space. This operation permanently uninstalls the app and removes its access to the environment."""
    path: DeleteSpacesEnvironmentsAppInstallationsRequestPath

# Operation: issue_app_installation_access_token
class PostSpacesEnvironmentsAppInstallationsAccessTokensRequestPath(StrictModel):
    space_id: str = Field(default=..., description="The unique identifier of the space containing the app installation.")
    environment_id: str = Field(default=..., description="The unique identifier of the environment within the space where the app is installed.")
    app_definition_id: str = Field(default=..., description="The unique identifier of the app definition for which to issue an access token.")
class PostSpacesEnvironmentsAppInstallationsAccessTokensRequest(StrictModel):
    """Generate an access token for an app installation within a specific space environment. This token enables the app to authenticate and interact with Contentful APIs on behalf of the installation."""
    path: PostSpacesEnvironmentsAppInstallationsAccessTokensRequestPath

# Operation: list_organization_usage_metrics
class GetOrganizationsOrganizationPeriodicUsagesRequestPath(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier of the organization for which to retrieve usage data.")
class GetOrganizationsOrganizationPeriodicUsagesRequestQuery(StrictModel):
    order: str | None = Field(default=None, description="Field to sort results by, such as usage metrics. Determines the order of returned usage records.")
    metric_in: str | None = Field(default=None, validation_alias="metric[in]", serialization_alias="metric[in]", description="Comma-separated list of metric types to include in the results, such as Content Management API (cma), Content Preview API (cpa), or GraphQL (gql) usage.")
    date_range_start_at: str | None = Field(default=None, validation_alias="dateRange.startAt", serialization_alias="dateRange.startAt", description="Start date for the usage period in ISO 8601 format (YYYY-MM-DD). Defines the beginning of the date range for usage data retrieval.")
    date_range_end_at: str | None = Field(default=None, validation_alias="dateRange.endAt", serialization_alias="dateRange.endAt", description="End date for the usage period in ISO 8601 format (YYYY-MM-DD). Defines the end of the date range for usage data retrieval.")
class GetOrganizationsOrganizationPeriodicUsagesRequest(StrictModel):
    """Retrieve periodic usage metrics for an organization, including API calls and resource consumption across specified time periods and metric types."""
    path: GetOrganizationsOrganizationPeriodicUsagesRequestPath
    query: GetOrganizationsOrganizationPeriodicUsagesRequestQuery | None = None

# Operation: list_space_periodic_usages
class GetOrganizationsSpacePeriodicUsagesRequestPath(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier of the organization for which to retrieve space usage data.")
class GetOrganizationsSpacePeriodicUsagesRequestQuery(StrictModel):
    order: str | None = Field(default=None, description="Field to sort results by, such as usage metrics. Determines the order in which usage records are returned.")
    metric_in: str | None = Field(default=None, validation_alias="metric[in]", serialization_alias="metric[in]", description="Comma-separated list of metrics to include in the response, such as Content Management API (cma), Content Preview API (cpa), or GraphQL (gql) usage.")
    date_range_start_at: str | None = Field(default=None, validation_alias="dateRange.startAt", serialization_alias="dateRange.startAt", description="Start date for the usage period in ISO 8601 format (YYYY-MM-DD). Usage data will be retrieved from this date onwards.")
    date_range_end_at: str | None = Field(default=None, validation_alias="dateRange.endAt", serialization_alias="dateRange.endAt", description="End date for the usage period in ISO 8601 format (YYYY-MM-DD). Usage data will be retrieved up to and including this date.")
class GetOrganizationsSpacePeriodicUsagesRequest(StrictModel):
    """Retrieve periodic space usage metrics for an organization, allowing you to track content delivery and API consumption patterns over a specified time range."""
    path: GetOrganizationsSpacePeriodicUsagesRequestPath
    query: GetOrganizationsSpacePeriodicUsagesRequestQuery | None = None

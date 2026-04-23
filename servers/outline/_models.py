"""
Outline MCP Server - Pydantic Models

Generated: 2026-04-23 21:33:28 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "AttachmentsCreateRequest",
    "AttachmentsDeleteRequest",
    "AttachmentsRedirectRequest",
    "CollectionsAddGroupRequest",
    "CollectionsAddUserRequest",
    "CollectionsCreateRequest",
    "CollectionsDeleteRequest",
    "CollectionsDocumentsRequest",
    "CollectionsExportAllRequest",
    "CollectionsExportRequest",
    "CollectionsGroupMembershipsRequest",
    "CollectionsInfoRequest",
    "CollectionsListRequest",
    "CollectionsMembershipsRequest",
    "CollectionsRemoveGroupRequest",
    "CollectionsRemoveUserRequest",
    "CollectionsUpdateRequest",
    "CommentsCreateRequest",
    "CommentsDeleteRequest",
    "CommentsInfoRequest",
    "CommentsListRequest",
    "CommentsUpdateRequest",
    "DataAttributesDeleteRequest",
    "DataAttributesInfoRequest",
    "DataAttributesListRequest",
    "DataAttributesUpdateRequest",
    "DocumentsAddGroupRequest",
    "DocumentsAddUserRequest",
    "DocumentsAnswerQuestionRequest",
    "DocumentsArchivedRequest",
    "DocumentsArchiveRequest",
    "DocumentsCreateRequest",
    "DocumentsDeletedRequest",
    "DocumentsDeleteRequest",
    "DocumentsDocumentsRequest",
    "DocumentsDraftsRequest",
    "DocumentsDuplicateRequest",
    "DocumentsExportRequest",
    "DocumentsGroupMembershipsRequest",
    "DocumentsImportRequest",
    "DocumentsInfoRequest",
    "DocumentsListRequest",
    "DocumentsMembershipsRequest",
    "DocumentsMoveRequest",
    "DocumentsRemoveGroupRequest",
    "DocumentsRemoveUserRequest",
    "DocumentsRestoreRequest",
    "DocumentsSearchRequest",
    "DocumentsSearchTitlesRequest",
    "DocumentsTemplatizeRequest",
    "DocumentsUnpublishRequest",
    "DocumentsUpdateRequest",
    "DocumentsUsersRequest",
    "DocumentsViewedRequest",
    "EventsListRequest",
    "FileOperationsDeleteRequest",
    "FileOperationsInfoRequest",
    "FileOperationsListRequest",
    "FileOperationsRedirectRequest",
    "GroupsAddUserRequest",
    "GroupsCreateRequest",
    "GroupsDeleteRequest",
    "GroupsInfoRequest",
    "GroupsListRequest",
    "GroupsMembershipsRequest",
    "GroupsRemoveUserRequest",
    "GroupsUpdateRequest",
    "OauthAuthenticationsDeleteRequest",
    "OauthAuthenticationsListRequest",
    "OauthClientsDeleteRequest",
    "OauthClientsListRequest",
    "OauthClientsRotateSecretRequest",
    "OauthClientsUpdateRequest",
    "RevisionsInfoRequest",
    "RevisionsListRequest",
    "SharesCreateRequest",
    "SharesInfoRequest",
    "SharesListRequest",
    "SharesRevokeRequest",
    "SharesUpdateRequest",
    "StarsCreateRequest",
    "StarsDeleteRequest",
    "StarsListRequest",
    "StarsUpdateRequest",
    "TemplatesCreateRequest",
    "TemplatesDeleteRequest",
    "TemplatesDuplicateRequest",
    "TemplatesInfoRequest",
    "TemplatesListRequest",
    "TemplatesRestoreRequest",
    "TemplatesUpdateRequest",
    "UsersActivateRequest",
    "UsersDeleteRequest",
    "UsersInfoRequest",
    "UsersInviteRequest",
    "UsersListRequest",
    "UsersSuspendRequest",
    "UsersUpdateRequest",
    "UsersUpdateRoleRequest",
    "ViewsCreateRequest",
    "ViewsListRequest",
    "CollectionsGroupMembershipsBody",
    "CollectionsListBody",
    "CollectionsMembershipsBody",
    "CommentsListBody",
    "DataAttributesListBody",
    "DataAttributesUpdateBodyOptionsOptionsItem",
    "DocumentsAnswerQuestionBody",
    "DocumentsArchivedBody",
    "DocumentsCreateBodyDataAttributesItem",
    "DocumentsDeletedBody",
    "DocumentsDraftsBody",
    "DocumentsGroupMembershipsBody",
    "DocumentsListBody",
    "DocumentsSearchBody",
    "DocumentsSearchTitlesBody",
    "DocumentsUpdateBodyDataAttributesItem",
    "DocumentsViewedBody",
    "EventsListBody",
    "FileOperationsListBody",
    "GroupsListBody",
    "GroupsMembershipsBody",
    "Invite",
    "RevisionsListBody",
    "SharesListBody",
    "TemplatesListBody",
    "UsersListBody",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: create_attachment
class AttachmentsCreateRequestBody(StrictModel):
    name: str = Field(default=..., description="The filename of the attachment, including the file extension (e.g., image.png, document.pdf).")
    document_id: str | None = Field(default=None, validation_alias="documentId", serialization_alias="documentId", description="Optional UUID identifier of the document this attachment is associated with. Omit if the attachment is not linked to a specific document.", json_schema_extra={'format': 'uuid'})
    content_type: str = Field(default=..., validation_alias="contentType", serialization_alias="contentType", description="The MIME type of the file being attached (e.g., image/png, application/pdf, text/plain). Must match the actual file format.")
    size: float = Field(default=..., description="The size of the file in bytes. Must be a positive number representing the exact file size before upload.")
class AttachmentsCreateRequest(StrictModel):
    """Create an attachment record in the database and obtain the necessary credentials to upload the file to cloud storage from the client. Returns upload configuration details for completing the file transfer."""
    body: AttachmentsCreateRequestBody

# Operation: get_attachment
class AttachmentsRedirectRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the attachment, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class AttachmentsRedirectRequest(StrictModel):
    """Retrieve an attachment by its unique identifier. For private attachments, a temporary signed URL with embedded credentials is generated automatically."""
    body: AttachmentsRedirectRequestBody

# Operation: delete_attachment
class AttachmentsDeleteRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID) of the attachment to delete.", json_schema_extra={'format': 'uuid'})
class AttachmentsDeleteRequest(StrictModel):
    """Permanently delete an attachment by its unique identifier. Note that this action does not remove any references or links to the attachment that may exist in documents."""
    body: AttachmentsDeleteRequestBody

# Operation: get_collection
class CollectionsInfoRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The UUID that uniquely identifies the collection to retrieve.", json_schema_extra={'format': 'uuid'})
class CollectionsInfoRequest(StrictModel):
    """Retrieve detailed information about a specific collection using its unique identifier."""
    body: CollectionsInfoRequestBody

# Operation: get_collection_document_structure
class CollectionsDocumentsRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the collection, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class CollectionsDocumentsRequest(StrictModel):
    """Retrieve the document structure of a collection as a hierarchical tree of navigation nodes, showing how documents are organized within the collection."""
    body: CollectionsDocumentsRequestBody

# Operation: list_collections
class CollectionsListRequestBody(StrictModel):
    body: CollectionsListBody | None = Field(default=None, description="Optional request body for filtering or configuring the list operation. Consult API documentation for supported query parameters or filter options.")
class CollectionsListRequest(StrictModel):
    """Retrieve all collections that the authenticated user has access to. Returns a list of collections with their metadata and details."""
    body: CollectionsListRequestBody | None = None

# Operation: create_collection
class CollectionsCreateRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the collection (e.g., 'Human Resources'). Used as the primary identifier for the collection.")
    description: str | None = Field(default=None, description="A brief description of the collection's purpose and contents. Markdown formatting is supported for rich text.")
    permission: Literal["read", "read_write"] | None = Field(default=None, description="The access level for the collection. Choose 'read' for view-only access or 'read_write' for full editing permissions.")
    color: str | None = Field(default=None, description="A hex color code (e.g., '#123123') to customize the visual appearance of the collection icon.")
    sharing: bool | None = Field(default=None, description="Whether documents in this collection can be shared publicly. Set to true to enable public sharing, false to restrict sharing.")
class CollectionsCreateRequest(StrictModel):
    """Create a new collection to organize and manage documents. Specify the collection's name, description, visual styling, and access permissions."""
    body: CollectionsCreateRequestBody

# Operation: update_collection
class CollectionsUpdateRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the collection to update, provided as a UUID.", json_schema_extra={'format': 'uuid'})
    name: str | None = Field(default=None, description="The new name for the collection. Use a clear, descriptive title that reflects the collection's purpose.")
    description: str | None = Field(default=None, description="A brief description of the collection's contents and purpose. Markdown formatting is supported for rich text styling.")
    permission: Literal["read", "read_write"] | None = Field(default=None, description="The access level for users who can access this collection. Choose 'read' for view-only access or 'read_write' to allow modifications.")
    color: str | None = Field(default=None, description="A hex color code (e.g., #123456) to customize the collection's icon color for visual organization and identification.")
    sharing: bool | None = Field(default=None, description="Whether to allow public sharing of documents within this collection. Set to true to enable sharing, false to restrict to authenticated users only.")
class CollectionsUpdateRequest(StrictModel):
    """Update an existing collection's properties including name, description, icon color, sharing settings, and access permissions. Changes apply immediately to the collection and affect how it appears and behaves for all users with access."""
    body: CollectionsUpdateRequestBody

# Operation: add_user_to_collection
class CollectionsAddUserRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID) of the collection to which the user will be added.", json_schema_extra={'format': 'uuid'})
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The unique identifier (UUID) of the user to add as a member to the collection.", json_schema_extra={'format': 'uuid'})
    permission: Literal["read", "read_write"] | None = Field(default=None, description="The access permission level for the user in this collection. Choose 'read' for view-only access or 'read_write' for full read and write access. Defaults to 'read' if not specified.")
class CollectionsAddUserRequest(StrictModel):
    """Add a user as a member to a collection with specified access permissions. The user will gain access to the collection based on the permission level assigned."""
    body: CollectionsAddUserRequestBody

# Operation: remove_user_from_collection
class CollectionsRemoveUserRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID) of the collection from which the user will be removed.", json_schema_extra={'format': 'uuid'})
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The unique identifier (UUID) of the user to remove from the collection.", json_schema_extra={'format': 'uuid'})
class CollectionsRemoveUserRequest(StrictModel):
    """Remove a user from a collection. This operation revokes the specified user's access to the collection."""
    body: CollectionsRemoveUserRequestBody

# Operation: list_collection_memberships
class CollectionsMembershipsRequestBody(StrictModel):
    body: CollectionsMembershipsBody | None = Field(default=None, description="Request body containing the collection identifier and optional filtering criteria for the membership query.")
class CollectionsMembershipsRequest(StrictModel):
    """Retrieve all individual memberships for a specific collection. Note that this endpoint returns only direct memberships and does not include group-based memberships."""
    body: CollectionsMembershipsRequestBody | None = None

# Operation: add_group_to_collection
class CollectionsAddGroupRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID) of the collection to which the group will be granted access.", json_schema_extra={'format': 'uuid'})
    group_id: str = Field(default=..., validation_alias="groupId", serialization_alias="groupId", description="The unique identifier (UUID) of the group whose members will receive access to the collection.", json_schema_extra={'format': 'uuid'})
    permission: Literal["read", "read_write"] | None = Field(default=None, description="The access level to grant the group members. Choose 'read' for view-only access or 'read_write' for full read and write permissions. Defaults to 'read' if not specified.")
class CollectionsAddGroupRequest(StrictModel):
    """Grant all members of a group access to a collection with a specified permission level. This enables group-based access control for collaborative collection management."""
    body: CollectionsAddGroupRequestBody

# Operation: remove_group_from_collection
class CollectionsRemoveGroupRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID) of the collection from which the group will be removed.", json_schema_extra={'format': 'uuid'})
    group_id: str = Field(default=..., validation_alias="groupId", serialization_alias="groupId", description="The unique identifier (UUID) of the group whose members will lose access to the collection.", json_schema_extra={'format': 'uuid'})
class CollectionsRemoveGroupRequest(StrictModel):
    """Revoke all members of a group from accessing a collection. Note that group members may retain access through other group memberships or individual collection access."""
    body: CollectionsRemoveGroupRequestBody

# Operation: list_collection_group_memberships
class CollectionsGroupMembershipsRequestBody(StrictModel):
    body: CollectionsGroupMembershipsBody | None = Field(default=None, description="Request body containing the collection identifier and optional filtering criteria for the group memberships query.")
class CollectionsGroupMembershipsRequest(StrictModel):
    """Retrieve all groups that have been granted access to a specific collection. This lists the group memberships associated with the collection."""
    body: CollectionsGroupMembershipsRequestBody | None = None

# Operation: delete_collection
class CollectionsDeleteRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID) of the collection to delete.", json_schema_extra={'format': 'uuid'})
class CollectionsDeleteRequest(StrictModel):
    """Permanently delete a collection and all of its documents. This action cannot be undone, so exercise caution before proceeding."""
    body: CollectionsDeleteRequestBody

# Operation: export_collection
class CollectionsExportRequestBody(StrictModel):
    format_: Literal["outline-markdown", "json", "html"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="Export format for the collection. Choose from outline-markdown (default), json, or html. Determines the structure and format of exported documents.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID) of the collection to export. Required to specify which collection should be exported.", json_schema_extra={'format': 'uuid'})
class CollectionsExportRequest(StrictModel):
    """Triggers a bulk export of a collection in your preferred format (markdown, JSON, or HTML) along with all attachments. Nested documents are preserved as folders in the resulting zip file. Returns a FileOperation object to track export progress and retrieve the download URL."""
    body: CollectionsExportRequestBody

# Operation: export_all_collections
class CollectionsExportAllRequestBody(StrictModel):
    format_: Literal["outline-markdown", "json", "html"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="Output format for the exported collections. Choose from outline-markdown for structured text, json for machine-readable data, or html for web-viewable content.")
    include_attachments: bool | None = Field(default=None, validation_alias="includeAttachments", serialization_alias="includeAttachments", description="Whether to include file attachments and media in the export. Enabled by default.")
    include_private: bool | None = Field(default=None, validation_alias="includePrivate", serialization_alias="includePrivate", description="Whether to include private collections in the export. Enabled by default.")
class CollectionsExportAllRequest(StrictModel):
    """Initiates a bulk export of all collections and their documents in your specified format. Returns a FileOperation object that you can poll to track export progress and retrieve the download URL when complete."""
    body: CollectionsExportAllRequestBody | None = None

# Operation: create_comment_on_document
class CommentsCreateRequestBody(StrictModel):
    document_id: str = Field(default=..., validation_alias="documentId", serialization_alias="documentId", description="The unique identifier (UUID format) of the document to which the comment will be added.", json_schema_extra={'format': 'uuid'})
    parent_comment_id: str | None = Field(default=None, validation_alias="parentCommentId", serialization_alias="parentCommentId", description="The unique identifier (UUID format) of the parent comment if this is a reply; omit to create a top-level comment.", json_schema_extra={'format': 'uuid'})
    data: dict[str, Any] | None = Field(default=None, description="The body of the comment.")
    text: str | None = Field(default=None, description="The body of the comment in markdown.")
class CommentsCreateRequest(StrictModel):
    """Add a new comment or reply to a document. Use parentCommentId to create a reply to an existing comment, or omit it to create a top-level comment."""
    body: CommentsCreateRequestBody

# Operation: get_comment
class CommentsInfoRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the comment to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
    include_anchor_text: bool | None = Field(default=None, validation_alias="includeAnchorText", serialization_alias="includeAnchorText", description="When enabled, includes the document text that the comment is anchored to in the response, if available.")
class CommentsInfoRequest(StrictModel):
    """Retrieve a specific comment by its unique identifier, with optional inclusion of the anchored document text."""
    body: CommentsInfoRequestBody

# Operation: update_comment
class CommentsUpdateRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the comment to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
    data: dict[str, Any] = Field(default=..., description="An object containing the comment fields to update. Specify the properties you want to modify in this object.")
class CommentsUpdateRequest(StrictModel):
    """Update an existing comment by its unique identifier. Modify comment content and properties using the provided data object."""
    body: CommentsUpdateRequestBody

# Operation: delete_comment
class CommentsDeleteRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the comment to delete, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class CommentsDeleteRequest(StrictModel):
    """Deletes a comment by its unique identifier. If the comment is a top-level comment, all of its child replies will be automatically deleted as well."""
    body: CommentsDeleteRequestBody

# Operation: list_comments
class CommentsListRequestBody(StrictModel):
    body: CommentsListBody | None = Field(default=None, description="Request body containing filter properties to match comments against. Structure and supported fields depend on the API's comment schema and filtering capabilities.")
class CommentsListRequest(StrictModel):
    """Retrieve all comments matching the specified filter criteria. Use the request body to define which comments to return based on properties like author, date range, or associated resources."""
    body: CommentsListRequestBody | None = None

# Operation: get_data_attribute
class DataAttributesInfoRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID format) of the data attribute to retrieve.", json_schema_extra={'format': 'uuid'})
class DataAttributesInfoRequest(StrictModel):
    """Retrieve a specific data attribute by its unique identifier. Use this operation to fetch detailed information about a single data attribute."""
    body: DataAttributesInfoRequestBody

# Operation: list_data_attributes
class DataAttributesListRequestBody(StrictModel):
    body: DataAttributesListBody | None = Field(default=None, description="Optional request body for filtering or configuring the list operation. Consult API documentation for supported query parameters or filter options.")
class DataAttributesListRequest(StrictModel):
    """Retrieve a complete list of all available data attributes in the system. Use this operation to discover and enumerate data attributes for reference or integration purposes."""
    body: DataAttributesListRequestBody | None = None

# Operation: update_data_attribute
class DataAttributesUpdateRequestBodyOptions(StrictModel):
    options: list[DataAttributesUpdateBodyOptionsOptionsItem] | None = Field(default=None, validation_alias="options", serialization_alias="options", description="An optional list of valid options for list-type data attributes. Each item represents a selectable value for this attribute.")
class DataAttributesUpdateRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the data attribute to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
    name: str = Field(default=..., description="The name of the data attribute (e.g., 'Status'). Used to identify the attribute in the system.")
    description: str | None = Field(default=None, description="An optional description providing additional context or details about the data attribute's purpose.")
    pinned: bool | None = Field(default=None, description="An optional boolean flag indicating whether this data attribute should be pinned to the top of documents for quick access.")
    options: DataAttributesUpdateRequestBodyOptions | None = None
class DataAttributesUpdateRequest(StrictModel):
    """Update an existing data attribute with new metadata. Only administrators can perform this operation. Note that the data type cannot be changed after the attribute is created."""
    body: DataAttributesUpdateRequestBody

# Operation: delete_data_attribute
class DataAttributesDeleteRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID) of the data attribute to delete.", json_schema_extra={'format': 'uuid'})
class DataAttributesDeleteRequest(StrictModel):
    """Permanently delete a data attribute from the system. Only administrators have permission to perform this operation."""
    body: DataAttributesDeleteRequestBody

# Operation: get_document
class DocumentsInfoRequestBody(StrictModel):
    share_id: str | None = Field(default=None, validation_alias="shareId", serialization_alias="shareId", description="The unique identifier for a shared document, formatted as a UUID. This shareId allows access to documents shared with you without requiring the original document UUID.", json_schema_extra={'format': 'uuid'})
class DocumentsInfoRequest(StrictModel):
    """Retrieve a document by its share identifier. Use this operation to access a document that has been shared with you via a shareId."""
    body: DocumentsInfoRequestBody | None = None

# Operation: create_document_from_file
class DocumentsImportRequestBody(StrictModel):
    file_: dict[str, Any] = Field(default=..., validation_alias="file", serialization_alias="file", description="The file to import as a document. Supported formats include plain text, markdown, docx, csv, tsv, and html.")
    publish: bool | None = Field(default=None, description="Whether to automatically publish the imported document upon creation. Defaults to unpublished if not specified.")
class DocumentsImportRequest(StrictModel):
    """Create a new document by importing a file. The document is placed at the collection root by default, or as a child document if a parent document ID is specified."""
    body: DocumentsImportRequestBody

# Operation: export_document
class DocumentsExportRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The document to export, specified by either its UUID or URL-friendly identifier.")
    paper_size: str | None = Field(default=None, validation_alias="paperSize", serialization_alias="paperSize", description="Paper size for PDF exports, such as A4 or Letter. Only applicable when exporting to PDF format.")
    signed_urls: float | None = Field(default=None, validation_alias="signedUrls", serialization_alias="signedUrls", description="Duration in seconds that signed URLs for attachment links should remain valid. Determines how long generated attachment links can be accessed.")
    include_child_documents: bool | None = Field(default=None, validation_alias="includeChildDocuments", serialization_alias="includeChildDocuments", description="Include all child documents in the export. When enabled, the response will always be returned as a zip file regardless of other parameters. Defaults to false.")
class DocumentsExportRequest(StrictModel):
    """Export a document in Markdown, HTML, or PDF format, with optional inclusion of child documents as a zip file. The response format is determined by the Accept header."""
    body: DocumentsExportRequestBody

# Operation: list_documents
class DocumentsListRequestBody(StrictModel):
    body: DocumentsListBody | None = Field(default=None, description="Optional request body for filtering or configuring the document list retrieval.")
class DocumentsListRequest(StrictModel):
    """Retrieve all documents accessible to the current user, including both published and draft documents."""
    body: DocumentsListRequestBody | None = None

# Operation: get_document_children
class DocumentsDocumentsRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the document, provided as either a UUID or URL-friendly ID.")
class DocumentsDocumentsRequest(StrictModel):
    """Retrieve the nested child structure (tree) of a document. Returns all immediate children and their hierarchical relationships for the specified document."""
    body: DocumentsDocumentsRequestBody

# Operation: list_draft_documents
class DocumentsDraftsRequestBody(StrictModel):
    body: DocumentsDraftsBody | None = Field(default=None, description="Optional request body for filtering or pagination options. Refer to API documentation for supported query parameters.")
class DocumentsDraftsRequest(StrictModel):
    """Retrieve all draft documents belonging to the current user. Returns a collection of documents that have not yet been finalized or published."""
    body: DocumentsDraftsRequestBody | None = None

# Operation: list_viewed_documents
class DocumentsViewedRequestBody(StrictModel):
    body: DocumentsViewedBody | None = Field(default=None, description="Optional request body for filtering or pagination options. If provided, structure should follow the API's standard filtering conventions.")
class DocumentsViewedRequest(StrictModel):
    """Retrieve a list of all documents recently viewed by the current user, ordered by most recent view first."""
    body: DocumentsViewedRequestBody | None = None

# Operation: search_documents_with_question
class DocumentsAnswerQuestionRequestBody(StrictModel):
    body: DocumentsAnswerQuestionBody | None = Field(default=None, description="Request payload containing the question and optional search parameters to query against your documents.")
class DocumentsAnswerQuestionRequest(StrictModel):
    """Query documents using natural language questions to retrieve direct answers. Results are filtered to documents accessible by your current credentials, and requires AI answers to be enabled in your workspace."""
    body: DocumentsAnswerQuestionRequestBody | None = None

# Operation: search_document_titles
class DocumentsSearchTitlesRequestBody(StrictModel):
    body: DocumentsSearchTitlesBody | None = Field(default=None, description="Request body containing search parameters such as keywords and optional filters for refining title search results.")
class DocumentsSearchTitlesRequest(StrictModel):
    """Search document titles using keywords for fast, title-only matching. This operation is optimized for title searches and returns results faster than the full documents.search method."""
    body: DocumentsSearchTitlesRequestBody | None = None

# Operation: search_documents
class DocumentsSearchRequestBody(StrictModel):
    body: DocumentsSearchBody | None = Field(default=None, description="Request body containing search parameters such as keywords, filters, and pagination options. Refer to the API documentation for the expected structure and available search filters.")
class DocumentsSearchRequest(StrictModel):
    """Search across all documents in your workspace using keywords. Results are automatically filtered to only include documents accessible with your current credentials."""
    body: DocumentsSearchRequestBody | None = None

# Operation: create_document
class DocumentsCreateRequestBody(StrictModel):
    title: str | None = Field(default=None, description="The title of the document (e.g., 'Welcome to Acme Inc'). If not provided, the document will be created without a title.")
    color: str | None = Field(default=None, description="The color for the document icon in hexadecimal format (e.g., '#FF5733'). Helps visually distinguish documents in the workspace.")
    template_id: str | None = Field(default=None, validation_alias="templateId", serialization_alias="templateId", description="The UUID of a template to use when creating the document. If provided, the document will be initialized with the template's structure and content.", json_schema_extra={'format': 'uuid'})
    publish: bool | None = Field(default=None, description="Whether to immediately publish the document and make it visible to other workspace members. If false or omitted, the document will be created in draft state.")
    full_width: bool | None = Field(default=None, validation_alias="fullWidth", serialization_alias="fullWidth", description="Whether the document should be displayed in full width mode. If true, the document will span the full available width; otherwise, it uses standard width constraints.")
    data_attributes: list[DocumentsCreateBodyDataAttributesItem] | None = Field(default=None, validation_alias="dataAttributes", serialization_alias="dataAttributes", description="An array of data attributes to attach to the document. Each attribute is a key-value pair that can be used for custom metadata or integration purposes.")
    collection_id: str | None = Field(default=None, validation_alias="collectionId", serialization_alias="collectionId", description="Identifier for the collection. Required to publish unless parentDocumentId is provided", json_schema_extra={'format': 'uuid'})
    parent_document_id: str | None = Field(default=None, validation_alias="parentDocumentId", serialization_alias="parentDocumentId", description="Identifier for the parent document. Required to publish unless collectionId is provided", json_schema_extra={'format': 'uuid'})
    text: str | None = Field(default=None, description="The body of the document in markdown")
class DocumentsCreateRequest(StrictModel):
    """Create a new document in the workspace, optionally as a child of an existing document. The document can be immediately published and configured with display preferences."""
    body: DocumentsCreateRequestBody | None = None

# Operation: update_document
class DocumentsUpdateRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The document identifier, accepting either a UUID or URL-friendly ID (e.g., 'hDYep1TPAM'). Required to specify which document to update.")
    title: str | None = Field(default=None, description="The new title for the document. Updates the document's display name.")
    color: str | None = Field(default=None, description="The icon color for the document in hexadecimal format (e.g., '#FF5733'). Controls the visual appearance in document lists.")
    full_width: bool | None = Field(default=None, validation_alias="fullWidth", serialization_alias="fullWidth", description="Whether the document should render using the full available width. When enabled, removes side margins for expanded viewing.")
    template_id: str | None = Field(default=None, validation_alias="templateId", serialization_alias="templateId", description="The UUID of a template to base this document on. Applies template structure and formatting to the document.", json_schema_extra={'format': 'uuid'})
    insights_enabled: bool | None = Field(default=None, validation_alias="insightsEnabled", serialization_alias="insightsEnabled", description="Whether to enable insights visibility on the document. When enabled, displays analytics and insights panels.")
    edit_mode: Literal["append", "prepend", "replace"] | None = Field(default=None, validation_alias="editMode", serialization_alias="editMode", description="The text update strategy: 'append' adds content to the end, 'prepend' adds to the beginning, or 'replace' overwrites existing content. Determines how text modifications are applied.")
    publish: bool | None = Field(default=None, description="Whether to publish the document and make it visible to other workspace members. Only applies if the document is currently in draft status.")
    data_attributes: list[DocumentsUpdateBodyDataAttributesItem] | None = Field(default=None, validation_alias="dataAttributes", serialization_alias="dataAttributes", description="An array of data attributes to update on the document. Any attributes not included in this array will be removed from the document. Specify as an array of attribute objects.")
    text: str | None = Field(default=None, description="The body of the document in markdown.")
    collection_id: str | None = Field(default=None, validation_alias="collectionId", serialization_alias="collectionId", description="Identifier for the collection to move the document to", json_schema_extra={'format': 'uuid'})
class DocumentsUpdateRequest(StrictModel):
    """Modify an existing document's properties, including metadata, display settings, and content attributes. Accepts either the document's UUID or URL ID for identification."""
    body: DocumentsUpdateRequestBody

# Operation: create_template_from_document
class DocumentsTemplatizeRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID) of the document to use as the template basis.", json_schema_extra={'format': 'uuid'})
    publish: bool = Field(default=..., description="Whether to publish the newly created template immediately. If true, the template becomes available for use; if false, it remains in draft state.")
class DocumentsTemplatizeRequest(StrictModel):
    """Create a new template based on an existing document. The document content and structure become the foundation for the template, which can optionally be published immediately upon creation."""
    body: DocumentsTemplatizeRequestBody

# Operation: unpublish_document
class DocumentsUnpublishRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The document identifier, which can be either a UUID or URL-friendly ID (urlId).")
    detach_: bool | None = Field(default=None, validation_alias="detach", serialization_alias="detach", description="Whether to detach the document from its collection when unpublishing. Defaults to false, keeping the document in the collection as a draft.")
class DocumentsUnpublishRequest(StrictModel):
    """Unpublish a document to revert it from published status back to draft, optionally removing it from its collection."""
    body: DocumentsUnpublishRequestBody

# Operation: move_document
class DocumentsMoveRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the document to move, accepting either a UUID or URL-friendly ID format.")
    index: float | None = Field(default=None, description="The position index where the document should be placed within its new parent collection. Lower indices position the document earlier in the collection structure.")
    collection_id: str | None = Field(default=None, validation_alias="collectionId", serialization_alias="collectionId", json_schema_extra={'format': 'uuid'})
    parent_document_id: str | None = Field(default=None, validation_alias="parentDocumentId", serialization_alias="parentDocumentId", json_schema_extra={'format': 'uuid'})
class DocumentsMoveRequest(StrictModel):
    """Move a document to a new location within the collection hierarchy. If no parent document is specified, the document will be relocated to the collection root."""
    body: DocumentsMoveRequestBody

# Operation: archive_document
class DocumentsArchiveRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The document identifier, which can be either the UUID or the URL-friendly ID (urlId). Both formats are accepted interchangeably.")
class DocumentsArchiveRequest(StrictModel):
    """Move a document to archived status, removing it from active view while preserving it for future search and restoration. Archived documents remain accessible but are hidden from standard document listings."""
    body: DocumentsArchiveRequestBody

# Operation: restore_document
class DocumentsRestoreRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The document identifier, which can be either a UUID or URL-friendly ID (e.g., 'hDYep1TPAM').")
    revision_id: str | None = Field(default=None, validation_alias="revisionId", serialization_alias="revisionId", description="Optional UUID of a specific revision to restore the document to. If not provided, the document is restored to its most recent state.", json_schema_extra={'format': 'uuid'})
class DocumentsRestoreRequest(StrictModel):
    """Restore a previously archived or deleted document. Optionally restore to a specific revision to recover the document at a previous point in time."""
    body: DocumentsRestoreRequestBody

# Operation: delete_document
class DocumentsDeleteRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The document identifier, either as a UUID or URL-friendly ID (e.g., 'hDYep1TPAM').")
    permanent: bool | None = Field(default=None, description="When true, permanently destroys the document with no recovery option instead of moving it to trash. Defaults to false (moves to trash).")
class DocumentsDeleteRequest(StrictModel):
    """Delete a document by moving it to trash, where it remains recoverable for 30 days before permanent deletion. Optionally bypass trash and permanently destroy the document immediately."""
    body: DocumentsDeleteRequestBody

# Operation: list_document_users
class DocumentsUsersRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The document identifier, either as a UUID or URL-friendly ID (e.g., 'hDYep1TPAM').")
    query: str | None = Field(default=None, description="Optional filter to search users by name. When provided, results are filtered to users matching this query string.")
    user_id: str | None = Field(default=None, validation_alias="userId", serialization_alias="userId", description="Optional filter to retrieve a specific user by their UUID. When provided, results are limited to this single user if they have access to the document.", json_schema_extra={'format': 'uuid'})
class DocumentsUsersRequest(StrictModel):
    """Retrieve all users with access to a document, including both direct members and inherited access. Use `list_document_memberships` to filter for only direct document members."""
    body: DocumentsUsersRequestBody

# Operation: list_document_memberships
class DocumentsMembershipsRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The document identifier, either as a UUID or URL-friendly ID (e.g., 'hDYep1TPAM').")
    query: str | None = Field(default=None, description="Optional filter to search memberships by user name. When provided, results are filtered to users matching this query.")
    permission: Literal["read", "read_write"] | None = Field(default=None, description="Optional filter to return only memberships with a specific permission level: 'read' for view-only access or 'read_write' for edit access.")
class DocumentsMembershipsRequest(StrictModel):
    """Retrieve users with direct membership to a document. This lists only users explicitly granted access to the document; use `documents.users` to see all users with any level of access."""
    body: DocumentsMembershipsRequestBody

# Operation: add_user_to_document
class DocumentsAddUserRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The document identifier, which can be either a UUID or a URL-friendly ID (urlId).")
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The unique identifier (UUID format) of the user to add to the document.", json_schema_extra={'format': 'uuid'})
    permission: Literal["read", "read_write"] | None = Field(default=None, description="The access level for the user: 'read' for view-only access or 'read_write' for editing permissions. Defaults to 'read' if not specified.")
class DocumentsAddUserRequest(StrictModel):
    """Grant a user access to a document by adding them as a member with specified permissions. The user will be able to interact with the document according to their assigned permission level."""
    body: DocumentsAddUserRequestBody

# Operation: remove_user_from_document
class DocumentsRemoveUserRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The document identifier, which can be either a UUID or a URL-friendly ID (urlId).")
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The UUID of the user to remove from the document.", json_schema_extra={'format': 'uuid'})
class DocumentsRemoveUserRequest(StrictModel):
    """Remove a user's membership and access from a specified document. The user will no longer be able to view or interact with the document."""
    body: DocumentsRemoveUserRequestBody

# Operation: list_archived_documents
class DocumentsArchivedRequestBody(StrictModel):
    body: DocumentsArchivedBody | None = Field(default=None, description="Optional request body for filtering or pagination options. Refer to API documentation for supported filter and pagination parameters.")
class DocumentsArchivedRequest(StrictModel):
    """Retrieve all archived documents in the workspace that the current user has access to. Returns a list of archived document records with their metadata."""
    body: DocumentsArchivedRequestBody | None = None

# Operation: list_deleted_documents
class DocumentsDeletedRequestBody(StrictModel):
    body: DocumentsDeletedBody | None = Field(default=None, description="Optional request body for filtering or pagination options. Refer to API documentation for supported query parameters.")
class DocumentsDeletedRequest(StrictModel):
    """Retrieve a list of all deleted documents in the workspace that the current user has access to. This allows users to view and potentially recover deleted documents."""
    body: DocumentsDeletedRequestBody | None = None

# Operation: duplicate_document
class DocumentsDuplicateRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The document to duplicate, specified as either its UUID or URL-friendly identifier.")
    title: str | None = Field(default=None, description="Optional custom title for the duplicated document. If not provided, the original title will be used.")
    recursive: bool | None = Field(default=None, description="When enabled, all child documents nested under the original document will also be duplicated, preserving the document hierarchy.")
    publish: bool | None = Field(default=None, description="When enabled, the newly created document will be published immediately. If disabled, it will be created in draft state.")
class DocumentsDuplicateRequest(StrictModel):
    """Creates a copy of an existing document with an optional new title, and optionally duplicates all child documents in the hierarchy."""
    body: DocumentsDuplicateRequestBody

# Operation: add_group_to_document
class DocumentsAddGroupRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The document identifier, which can be either a UUID or URL-friendly ID.")
    group_id: str = Field(default=..., validation_alias="groupId", serialization_alias="groupId", description="The unique identifier (UUID format) of the group to grant access to the document.", json_schema_extra={'format': 'uuid'})
    permission: Literal["read", "read_write"] | None = Field(default=None, description="The access level for group members: 'read' for view-only access or 'read_write' for editing permissions. Defaults to 'read' if not specified.")
class DocumentsAddGroupRequest(StrictModel):
    """Grant all members of a group access to a document by adding the group and specifying their permission level."""
    body: DocumentsAddGroupRequestBody

# Operation: remove_group_from_document
class DocumentsRemoveGroupRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The document identifier, which can be either a UUID or URL-friendly ID (urlId).")
    group_id: str = Field(default=..., validation_alias="groupId", serialization_alias="groupId", description="The unique identifier (UUID format) of the group whose access should be revoked from the document.", json_schema_extra={'format': 'uuid'})
class DocumentsRemoveGroupRequest(StrictModel):
    """Revoke all members of a group from accessing a document. This operation removes the group's collective access permissions to the specified document."""
    body: DocumentsRemoveGroupRequestBody

# Operation: list_document_group_memberships
class DocumentsGroupMembershipsRequestBody(StrictModel):
    body: DocumentsGroupMembershipsBody | None = Field(default=None, description="Request body containing the document identifier and optional filtering criteria for group memberships.")
class DocumentsGroupMembershipsRequest(StrictModel):
    """Retrieve all group memberships associated with a specific document. This allows you to see which groups have access to or are linked with the document."""
    body: DocumentsGroupMembershipsRequestBody | None = None

# Operation: list_events
class EventsListRequestBody(StrictModel):
    body: EventsListBody | None = Field(default=None, description="Optional request body for filtering or configuring the events list query. Specify any desired filters or parameters to narrow down the results.")
class EventsListRequest(StrictModel):
    """Retrieve a list of all events from the knowledge base audit trail. Events represent important activities and changes that have occurred within the system."""
    body: EventsListRequestBody | None = None

# Operation: get_file_operation
class FileOperationsInfoRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID) of the file operation to retrieve.", json_schema_extra={'format': 'uuid'})
class FileOperationsInfoRequest(StrictModel):
    """Retrieve the details and current status of a file operation by its unique identifier. Use this to monitor long-running import or export tasks."""
    body: FileOperationsInfoRequestBody

# Operation: delete_file_operation
class FileOperationsDeleteRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID) of the file operation to delete.", json_schema_extra={'format': 'uuid'})
class FileOperationsDeleteRequest(StrictModel):
    """Delete a file operation and permanently remove its associated files. Use this to clean up completed, failed, or unwanted import/export operations."""
    body: FileOperationsDeleteRequestBody

# Operation: get_file_redirect
class FileOperationsRedirectRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID format) of the file operation to retrieve.", json_schema_extra={'format': 'uuid'})
class FileOperationsRedirectRequest(StrictModel):
    """Retrieve a file by generating a temporary, signed URL with embedded credentials that redirects to the file's storage location."""
    body: FileOperationsRedirectRequestBody

# Operation: list_file_operations
class FileOperationsListRequestBody(StrictModel):
    body: FileOperationsListBody | None = Field(default=None, description="Request body containing optional filter criteria such as operation type (import or export) to narrow results. Omit to retrieve all file operations.")
class FileOperationsListRequest(StrictModel):
    """Retrieve all file operations (imports and exports) for the current workspace. Results can be filtered by operation type to show only imports, exports, or all operations."""
    body: FileOperationsListRequestBody | None = None

# Operation: get_group
class GroupsInfoRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID) of the group to retrieve.", json_schema_extra={'format': 'uuid'})
class GroupsInfoRequest(StrictModel):
    """Retrieve detailed information about a specific group, including its name and member count, using its unique identifier."""
    body: GroupsInfoRequestBody

# Operation: list_groups
class GroupsListRequestBody(StrictModel):
    body: GroupsListBody | None = Field(default=None, description="Optional request body for filtering or configuring the list operation. Refer to API documentation for supported query parameters.")
class GroupsListRequest(StrictModel):
    """Retrieve all groups in the workspace. Groups organize users and control access permissions for collections."""
    body: GroupsListRequestBody | None = None

# Operation: create_group
class GroupsCreateRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the group (e.g., 'Designers'). Used to identify and reference the group in permission assignments and user management.")
class GroupsCreateRequest(StrictModel):
    """Create a new group with a specified name. Groups organize users and enable efficient permission management by allowing collection access to be assigned to multiple users simultaneously."""
    body: GroupsCreateRequestBody

# Operation: update_group
class GroupsUpdateRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the group to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
    name: str = Field(default=..., description="The new name for the group. Use a descriptive name that reflects the group's purpose or membership.")
class GroupsUpdateRequest(StrictModel):
    """Update an existing group's name by providing its unique identifier and the new name."""
    body: GroupsUpdateRequestBody

# Operation: delete_group
class GroupsDeleteRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID) of the group to delete.", json_schema_extra={'format': 'uuid'})
class GroupsDeleteRequest(StrictModel):
    """Permanently delete a group and revoke all member access to collections the group was added to. This action cannot be undone."""
    body: GroupsDeleteRequestBody

# Operation: list_group_memberships
class GroupsMembershipsRequestBody(StrictModel):
    body: GroupsMembershipsBody | None = Field(default=None, description="Request body containing filter criteria, sorting options, and pagination parameters to customize the membership list results.")
class GroupsMembershipsRequest(StrictModel):
    """Retrieve and filter all members belonging to a specific group. Use the request body to specify filtering criteria and pagination options."""
    body: GroupsMembershipsRequestBody | None = None

# Operation: add_user_to_group
class GroupsAddUserRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the group to which the user will be added. Must be a valid UUID.", json_schema_extra={'format': 'uuid'})
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The unique identifier of the user to add to the group. Must be a valid UUID.", json_schema_extra={'format': 'uuid'})
class GroupsAddUserRequest(StrictModel):
    """Add a user to a group. The user will become a member of the specified group and gain access to group resources."""
    body: GroupsAddUserRequestBody

# Operation: remove_user_from_group
class GroupsRemoveUserRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID) of the group from which the user will be removed.", json_schema_extra={'format': 'uuid'})
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The unique identifier (UUID) of the user to remove from the group.", json_schema_extra={'format': 'uuid'})
class GroupsRemoveUserRequest(StrictModel):
    """Remove a user from a group. This operation deletes the membership relationship between the specified user and group."""
    body: GroupsRemoveUserRequestBody

# Operation: list_oauth_clients
class OauthClientsListRequestBody(StrictModel):
    offset: float | None = Field(default=None, description="The number of results to skip before returning items, used for pagination. Defaults to 0 to start from the beginning.")
    limit: float | None = Field(default=None, description="The maximum number of OAuth clients to return in a single response, used for pagination. Defaults to 25 items per page.")
class OauthClientsListRequest(StrictModel):
    """Retrieve a paginated list of OAuth clients accessible to the authenticated user, including both user-created clients and published clients available to the workspace."""
    body: OauthClientsListRequestBody | None = None

# Operation: update_oauth_client
class OauthClientsUpdateRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the OAuth client to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
    name: str | None = Field(default=None, description="The display name for the OAuth client.")
    description: str | None = Field(default=None, description="A brief description explaining the purpose or functionality of the OAuth client.")
    developer_name: str | None = Field(default=None, validation_alias="developerName", serialization_alias="developerName", description="The name of the developer or organization that created this OAuth client.")
    developer_url: str | None = Field(default=None, validation_alias="developerUrl", serialization_alias="developerUrl", description="A URL pointing to the developer's or organization's website.")
    avatar_url: str | None = Field(default=None, validation_alias="avatarUrl", serialization_alias="avatarUrl", description="A URL pointing to an image that represents the OAuth client visually.")
    redirect_uris: list[str] | None = Field(default=None, validation_alias="redirectUris", serialization_alias="redirectUris", description="A list of valid redirect URIs where the OAuth client can redirect users after authentication. Each URI should be a complete, valid URL.")
    published: bool | None = Field(default=None, description="Whether this OAuth client is published and available for use by other workspaces.")
class OauthClientsUpdateRequest(StrictModel):
    """Update an existing OAuth client's configuration, including its name, description, developer information, redirect URIs, and publication status."""
    body: OauthClientsUpdateRequestBody

# Operation: rotate_oauth_client_secret
class OauthClientsRotateSecretRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the OAuth client, provided as a UUID.", json_schema_extra={'format': 'uuid'})
class OauthClientsRotateSecretRequest(StrictModel):
    """Generate a new client secret for an OAuth client, immediately invalidating the previous secret. Update your application to use the new secret before the old one expires to avoid authentication failures."""
    body: OauthClientsRotateSecretRequestBody

# Operation: delete_oauth_client
class OauthClientsDeleteRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID) of the OAuth client to delete.", json_schema_extra={'format': 'uuid'})
class OauthClientsDeleteRequest(StrictModel):
    """Permanently delete an OAuth client and revoke all associated access tokens. This action cannot be undone and will immediately invalidate all active sessions using this client."""
    body: OauthClientsDeleteRequestBody

# Operation: list_oauth_authentications
class OauthAuthenticationsListRequestBody(StrictModel):
    offset: float | None = Field(default=None, description="The number of results to skip before returning items, used for pagination. Defaults to 0 to start from the beginning.")
    limit: float | None = Field(default=None, description="The maximum number of OAuth authentications to return in a single response, used for pagination. Defaults to 25 items per page.")
class OauthAuthenticationsListRequest(StrictModel):
    """Retrieve a list of all OAuth authentications accessible to the current user, representing third-party applications that have been authorized to access their account."""
    body: OauthAuthenticationsListRequestBody | None = None

# Operation: revoke_oauth_authentication
class OauthAuthenticationsDeleteRequestBody(StrictModel):
    oauth_client_id: str = Field(default=..., validation_alias="oauthClientId", serialization_alias="oauthClientId", description="The unique identifier (UUID format) of the OAuth client application whose access should be revoked.", json_schema_extra={'format': 'uuid'})
    scope: list[str] | None = Field(default=None, description="Optional list of specific permission scopes to revoke. If omitted, all scopes for the OAuth client will be revoked.")
class OauthAuthenticationsDeleteRequest(StrictModel):
    """Revoke an OAuth authentication to remove a third-party application's access to the user's account. This operation permanently disconnects the authorized application."""
    body: OauthAuthenticationsDeleteRequestBody

# Operation: get_revision
class RevisionsInfoRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the revision to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class RevisionsInfoRequest(StrictModel):
    """Retrieve a specific revision of a document by its unique identifier. A revision represents a snapshot of the document at a particular point in time."""
    body: RevisionsInfoRequestBody

# Operation: list_revisions
class RevisionsListRequestBody(StrictModel):
    body: RevisionsListBody | None = Field(default=None, description="Request body containing the document identifier and optional filtering criteria for revisions to retrieve.")
class RevisionsListRequest(StrictModel):
    """Retrieve all revisions for a specific document. Revisions represent historical snapshots of document content and enable tracking of changes over time."""
    body: RevisionsListRequestBody | None = None

# Operation: get_share_by_document
class SharesInfoRequestBody(StrictModel):
    document_id: str | None = Field(default=None, validation_alias="documentId", serialization_alias="documentId", description="The unique identifier of the document whose share information should be retrieved. Must be a valid UUID format.", json_schema_extra={'format': 'uuid'})
class SharesInfoRequest(StrictModel):
    """Retrieve detailed information about a share link using its associated document ID. This operation returns the share object containing access permissions and sharing configuration for the specified document."""
    body: SharesInfoRequestBody | None = None

# Operation: list_shares
class SharesListRequestBody(StrictModel):
    body: SharesListBody | None = Field(default=None, description="Optional request body for filtering or configuring the share list retrieval. Consult the API documentation for supported query parameters or filter options.")
class SharesListRequest(StrictModel):
    """Retrieve all share links available in the workspace. This operation returns a complete list of shares that have been created for collaborative access."""
    body: SharesListRequestBody | None = None

# Operation: create_share
class SharesCreateRequestBody(StrictModel):
    document_id: str = Field(default=..., validation_alias="documentId", serialization_alias="documentId", description="The unique identifier (UUID) of the document to create a share link for.", json_schema_extra={'format': 'uuid'})
class SharesCreateRequest(StrictModel):
    """Creates a new share link for accessing a document. If multiple shares are requested for the same document using the same API key, the existing share object is returned. Shares are unpublished by default."""
    body: SharesCreateRequestBody

# Operation: update_share_published_status
class SharesUpdateRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the share to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
    published: bool = Field(default=..., description="Whether the share should be published (true) and publicly accessible, or unpublished (false) and require authentication.")
class SharesUpdateRequest(StrictModel):
    """Update a share's published status to control access. When published is set to true, the share becomes publicly accessible via its link without requiring authentication."""
    body: SharesUpdateRequestBody

# Operation: revoke_share
class SharesRevokeRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the share to revoke, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class SharesRevokeRequest(StrictModel):
    """Deactivate a share link to prevent further access to the shared document. Once revoked, the share link becomes inactive and can no longer be used."""
    body: SharesRevokeRequestBody

# Operation: add_star
class StarsCreateRequestBody(StrictModel):
    document_id: str | None = Field(default=None, validation_alias="documentId", serialization_alias="documentId", description="The UUID of the document to star. Either this or collectionId must be provided.", json_schema_extra={'format': 'uuid'})
    index: str | None = Field(default=None, description="The position in the starred items list where this star should appear. If not specified, the star will be added at the end.")
class StarsCreateRequest(StrictModel):
    """Add a document or collection to the user's starred items, making it appear in their sidebar for quick access. Either a document ID or collection ID must be provided."""
    body: StarsCreateRequestBody | None = None

# Operation: list_starred_documents
class StarsListRequestBody(StrictModel):
    offset: float | None = Field(default=None, description="Number of documents to skip from the beginning of the list, useful for pagination. Defaults to 0 to start from the first document.")
    limit: float | None = Field(default=None, description="Maximum number of documents to return per request, useful for controlling response size and pagination. Defaults to 25 documents.")
class StarsListRequest(StrictModel):
    """Retrieve all starred documents for the authenticated user. Stars serve as bookmarks for quick access to important documents in the sidebar."""
    body: StarsListRequestBody | None = None

# Operation: update_star
class StarsUpdateRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the starred document to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
    index: str = Field(default=..., description="The new display position for this starred document in the sidebar order. Lower indices appear higher in the list.")
class StarsUpdateRequest(StrictModel):
    """Reorder a starred document in the sidebar by updating its display position relative to other starred items."""
    body: StarsUpdateRequestBody

# Operation: remove_star
class StarsDeleteRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the starred document to remove, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class StarsDeleteRequest(StrictModel):
    """Remove a star from a document, deleting it from the user's starred documents list in the sidebar."""
    body: StarsDeleteRequestBody

# Operation: send_user_invites
class UsersInviteRequestBody(StrictModel):
    invites: list[Invite] = Field(default=..., description="Array of user invitations to send. Each invitation specifies the recipient and any relevant details for account creation. Order is preserved as submitted.")
class UsersInviteRequest(StrictModel):
    """Send email invitations to one or more users to join the workspace. Each invitation includes a personalized link that allows recipients to create an account and access the workspace."""
    body: UsersInviteRequestBody

# Operation: get_user
class UsersInfoRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID) of the user to retrieve.", json_schema_extra={'format': 'uuid'})
class UsersInfoRequest(StrictModel):
    """Retrieve detailed information about a specific user, including their name, email, avatar, and workspace role."""
    body: UsersInfoRequestBody

# Operation: list_users
class UsersListRequestBody(StrictModel):
    body: UsersListBody | None = Field(default=None, description="Optional request body containing filter criteria and pagination options to customize the user list results.")
class UsersListRequest(StrictModel):
    """Retrieve and filter all users in the workspace. Supports optional filtering and pagination parameters to narrow results."""
    body: UsersListRequestBody | None = None

# Operation: update_user
class UsersUpdateRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The user's display name. Can be any string value.")
    language: str | None = Field(default=None, description="The user's preferred language, specified as a BCP 47 language tag (e.g., en, en-US, fr-CA).", json_schema_extra={'format': 'BCP47'})
    avatar_url: str | None = Field(default=None, validation_alias="avatarUrl", serialization_alias="avatarUrl", description="A URI pointing to the user's avatar image. Must be a valid URL format.", json_schema_extra={'format': 'uri'})
class UsersUpdateRequest(StrictModel):
    """Update the authenticated user's profile information, including their display name and avatar. Optionally specify a user ID to update a different user's profile."""
    body: UsersUpdateRequestBody | None = None

# Operation: update_user_role
class UsersUpdateRoleRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose role should be updated, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
    role: Literal["admin", "member", "viewer", "guest"] = Field(default=..., description="The new role to assign to the user. Must be one of: admin, member, viewer, or guest.")
class UsersUpdateRoleRequest(StrictModel):
    """Update a user's role within the system. This operation requires admin authorization and allows changing a user's access level to one of the predefined role types."""
    body: UsersUpdateRoleRequestBody

# Operation: suspend_user
class UsersSuspendRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID) of the user to suspend.", json_schema_extra={'format': 'uuid'})
class UsersSuspendRequest(StrictModel):
    """Suspend a user account to prevent sign-in and exclude them from billing calculations. Suspended users retain their data but cannot access the system."""
    body: UsersSuspendRequestBody

# Operation: activate_user
class UsersActivateRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The UUID of the user to activate.", json_schema_extra={'format': 'uuid'})
class UsersActivateRequest(StrictModel):
    """Reactivate a suspended user to restore their signin access. Activation triggers billing recalculation in hosted environments."""
    body: UsersActivateRequestBody

# Operation: delete_user
class UsersDeleteRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID) of the user to delete.", json_schema_extra={'format': 'uuid'})
class UsersDeleteRequest(StrictModel):
    """Permanently delete a user account. Note: Deleted users can be recreated if they sign in via SSO again. Consider suspending the user instead in most cases to preserve data integrity."""
    body: UsersDeleteRequestBody

# Operation: list_document_views
class ViewsListRequestBody(StrictModel):
    document_id: str = Field(default=..., validation_alias="documentId", serialization_alias="documentId", description="The unique identifier of the document to retrieve views for, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
    include_suspended: bool | None = Field(default=None, validation_alias="includeSuspended", serialization_alias="includeSuspended", description="Whether to include view records from users with suspended accounts. Defaults to false, excluding suspended user views.")
class ViewsListRequest(StrictModel):
    """Retrieve a list of all users who have viewed a specific document along with the total view count. Optionally include views from suspended users."""
    body: ViewsListRequestBody

# Operation: create_view_for_document
class ViewsCreateRequestBody(StrictModel):
    document_id: str = Field(default=..., validation_alias="documentId", serialization_alias="documentId", description="The unique identifier (UUID) of the document for which to create the view.", json_schema_extra={'format': 'uuid'})
class ViewsCreateRequest(StrictModel):
    """Creates a new view for a document. Note: This operation is provided for completeness, but it is recommended to create views through the Outline UI instead of programmatically."""
    body: ViewsCreateRequestBody

# Operation: create_template
class TemplatesCreateRequestBody(StrictModel):
    title: str = Field(default=..., description="The display name for the template. Must be between 1 and 255 characters.", min_length=1, max_length=255)
    data: dict[str, Any] = Field(default=..., description="The template content structured as a ProseMirror document object, defining the default body and formatting for documents created from this template.")
    color: str | None = Field(default=None, description="Optional hex color code for the template icon (e.g., #FF5733). Must be a valid 6-digit hexadecimal color.", pattern='^#[0-9A-Fa-f]{6}$')
class TemplatesCreateRequest(StrictModel):
    """Create a new template that serves as a reusable starting point for documents. Templates can be customized with content and styling, and optionally scoped to a specific collection."""
    body: TemplatesCreateRequestBody

# Operation: list_templates
class TemplatesListRequestBody(StrictModel):
    body: TemplatesListBody | None = Field(default=None, description="Optional request body to filter templates by collection or apply other query criteria.")
class TemplatesListRequest(StrictModel):
    """Retrieve all templates available to the current user, with optional filtering by collection. Templates without an associated collection are accessible workspace-wide."""
    body: TemplatesListRequestBody | None = None

# Operation: get_template
class TemplatesInfoRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the template, provided as either a UUID or a URL-friendly ID string.")
class TemplatesInfoRequest(StrictModel):
    """Retrieve a specific template by its unique identifier. Accepts either the UUID or URL-friendly ID format."""
    body: TemplatesInfoRequestBody

# Operation: update_template
class TemplatesUpdateRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the template, accepting either a UUID or URL-friendly ID.")
    title: str | None = Field(default=None, description="The display name for the template.")
    color: str | None = Field(default=None, description="The color of the template icon specified in hexadecimal format (e.g., #FF5733).", pattern='^#[0-9A-Fa-f]{6}$')
    full_width: bool | None = Field(default=None, validation_alias="fullWidth", serialization_alias="fullWidth", description="Whether the template should render at full width in the user interface.")
class TemplatesUpdateRequest(StrictModel):
    """Update an existing template's properties such as title, icon color, and display width by providing its unique identifier."""
    body: TemplatesUpdateRequestBody

# Operation: delete_template
class TemplatesDeleteRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the template, accepting either the UUID or the URL-friendly ID.")
class TemplatesDeleteRequest(StrictModel):
    """Soft-delete a template by its unique identifier. The template can be restored later if needed."""
    body: TemplatesDeleteRequestBody

# Operation: restore_template
class TemplatesRestoreRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the template to restore. Accept either the UUID or the URL-friendly ID (urlId) format.")
class TemplatesRestoreRequest(StrictModel):
    """Restore a previously deleted template using its unique identifier. This operation recovers a soft-deleted template and makes it available for use again."""
    body: TemplatesRestoreRequestBody

# Operation: duplicate_template
class TemplatesDuplicateRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the template to duplicate. Accepts either the UUID or the URL-friendly ID (urlId) of the template.")
    title: str | None = Field(default=None, description="Optional custom title for the duplicated template. If not provided, the original template's title will be used for the copy.")
class TemplatesDuplicateRequest(StrictModel):
    """Create a copy of an existing template with optional customization. You can override the duplicated template's title and specify the target collection for the copy."""
    body: TemplatesDuplicateRequestBody

# ============================================================================
# Component Models
# ============================================================================

class CollectionSort(PermissiveModel):
    """The sort of documents in the collection. Note that not all API responses respect this and it is left as a frontend concern to implement."""
    field: str | None = None
    direction: Literal["asc", "desc"] | None = None

class CollectionsGroupMembershipsBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Identifier for the collection", json_schema_extra={'format': 'uuid'})
    query: str | None = Field(None, description="Filter memberships by group names")
    permission: Literal["read", "read_write"] | None = None

class CollectionsListBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    sort: str | None = None
    direction: Literal["ASC", "DESC"] | None = None
    query: str | None = Field(None, description="If set, will filter the results by collection name.")
    status_filter: list[Literal["archived"]] | None = Field(None, validation_alias="statusFilter", serialization_alias="statusFilter", description="An optional array of statuses to filter by.")

class CollectionsMembershipsBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Identifier for the collection", json_schema_extra={'format': 'uuid'})
    query: str | None = Field(None, description="Filter memberships by user names")
    permission: Literal["read", "read_write"] | None = None

class CommentsListBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    sort: str | None = None
    direction: Literal["ASC", "DESC"] | None = None
    document_id: str | None = Field(None, validation_alias="documentId", serialization_alias="documentId", description="Filter to a specific document", json_schema_extra={'format': 'uuid'})
    collection_id: str | None = Field(None, validation_alias="collectionId", serialization_alias="collectionId", description="Filter to a specific collection", json_schema_extra={'format': 'uuid'})
    include_anchor_text: bool | None = Field(None, validation_alias="includeAnchorText", serialization_alias="includeAnchorText", description="Include the document text that the comment is anchored to, if any, in the response.")

class DataAttributesListBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    sort: str | None = None
    direction: Literal["ASC", "DESC"] | None = None

class DataAttributesUpdateBodyOptionsOptionsItem(PermissiveModel):
    value: str | None = Field(None, description="The label/value of the option.")
    color: str | None = Field(None, description="Optional color for the option.")

class DocumentsAnswerQuestionBody(PermissiveModel):
    query: str | None = None
    user_id: str | None = Field(None, validation_alias="userId", serialization_alias="userId", description="Any documents that have not been edited by the user identifier will be filtered out", json_schema_extra={'format': 'uuid'})
    collection_id: str | None = Field(None, validation_alias="collectionId", serialization_alias="collectionId", description="A collection to search within", json_schema_extra={'format': 'uuid'})
    document_id: str | None = Field(None, validation_alias="documentId", serialization_alias="documentId", description="A document to search within", json_schema_extra={'format': 'uuid'})
    status_filter: Literal["draft", "archived", "published"] | None = Field(None, validation_alias="statusFilter", serialization_alias="statusFilter", description="Any documents that are not in the specified status will be filtered out")
    date_filter: Literal["day", "week", "month", "year"] | None = Field(None, validation_alias="dateFilter", serialization_alias="dateFilter", description="Any documents that have not been updated within the specified period will be filtered out")

class DocumentsArchivedBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    sort: str | None = None
    direction: Literal["ASC", "DESC"] | None = None
    collection_id: str | None = Field(None, validation_alias="collectionId", serialization_alias="collectionId", description="Optionally filter to a specific collection", json_schema_extra={'format': 'uuid'})

class DocumentsCreateBodyDataAttributesItem(PermissiveModel):
    data_attribute_id: str = Field(..., validation_alias="dataAttributeId", serialization_alias="dataAttributeId", description="Unique identifier for the data attribute.", json_schema_extra={'format': 'uuid'})
    value: str | bool | float = Field(..., description="The value of the data attribute. Can be a string, boolean, or number depending on the data attribute type.")

class DocumentsDeletedBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    sort: str | None = None
    direction: Literal["ASC", "DESC"] | None = None

class DocumentsDraftsBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    sort: str | None = None
    direction: Literal["ASC", "DESC"] | None = None
    collection_id: str | None = Field(None, validation_alias="collectionId", serialization_alias="collectionId", description="A collection to search within", json_schema_extra={'format': 'uuid'})
    date_filter: Literal["day", "week", "month", "year"] | None = Field(None, validation_alias="dateFilter", serialization_alias="dateFilter", description="Any documents that have not been updated within the specified period will be filtered out")

class DocumentsGroupMembershipsBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier for the document. Either the UUID or the urlId is acceptable.")
    query: str | None = Field(None, description="Filter memberships by group names")
    permission: Literal["read", "read_write"] | None = None

class DocumentsListBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    sort: str | None = None
    direction: Literal["ASC", "DESC"] | None = None
    collection_id: str | None = Field(None, validation_alias="collectionId", serialization_alias="collectionId", description="Optionally filter to a specific collection", json_schema_extra={'format': 'uuid'})
    user_id: str | None = Field(None, validation_alias="userId", serialization_alias="userId", description="Optionally filter to documents created by a specific user", json_schema_extra={'format': 'uuid'})
    backlink_document_id: str | None = Field(None, validation_alias="backlinkDocumentId", serialization_alias="backlinkDocumentId", json_schema_extra={'format': 'uuid'})
    parent_document_id: str | None = Field(None, validation_alias="parentDocumentId", serialization_alias="parentDocumentId", json_schema_extra={'format': 'uuid'})
    status_filter: list[Literal["draft", "archived", "published"]] | None = Field(None, validation_alias="statusFilter", serialization_alias="statusFilter", description="Document statuses to include in results")

class DocumentsSearchBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    query: str | None = None
    user_id: str | None = Field(None, validation_alias="userId", serialization_alias="userId", description="Any documents that have not been edited by the user identifier will be filtered out", json_schema_extra={'format': 'uuid'})
    collection_id: str | None = Field(None, validation_alias="collectionId", serialization_alias="collectionId", description="A collection to search within", json_schema_extra={'format': 'uuid'})
    document_id: str | None = Field(None, validation_alias="documentId", serialization_alias="documentId", description="A document to search within", json_schema_extra={'format': 'uuid'})
    status_filter: list[Literal["draft", "archived", "published"]] | None = Field(None, validation_alias="statusFilter", serialization_alias="statusFilter", description="Document statuses to include in results")
    date_filter: Literal["day", "week", "month", "year"] | None = Field(None, validation_alias="dateFilter", serialization_alias="dateFilter", description="Any documents that have not been updated within the specified period will be filtered out")
    share_id: str | None = Field(None, validation_alias="shareId", serialization_alias="shareId", description="Filter results to the collection or document referenced by the shareId")
    snippet_min_words: float | None = Field(20, validation_alias="snippetMinWords", serialization_alias="snippetMinWords", description="Minimum number of words to show in search result snippets")
    snippet_max_words: float | None = Field(30, validation_alias="snippetMaxWords", serialization_alias="snippetMaxWords", description="Maximum number of words to show in search result snippets")
    sort: Literal["relevance", "createdAt", "updatedAt", "title"] | None = Field(None, description="Specifies the attributes by which search results will be sorted")
    direction: Literal["ASC", "DESC"] | None = Field(None, description="Specifies the sort order with respect to sort field")

class DocumentsSearchTitlesBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    query: str = Field(..., description="Search query to match against document titles")
    collection_id: str | None = Field(None, validation_alias="collectionId", serialization_alias="collectionId", description="Filter to a specific collection", json_schema_extra={'format': 'uuid'})
    user_id: str | None = Field(None, validation_alias="userId", serialization_alias="userId", description="Filter results based on user", json_schema_extra={'format': 'uuid'})
    document_id: str | None = Field(None, validation_alias="documentId", serialization_alias="documentId", description="Filter results based on content within a document and its children", json_schema_extra={'format': 'uuid'})
    status_filter: list[Literal["draft", "archived", "published"]] | None = Field(None, validation_alias="statusFilter", serialization_alias="statusFilter", description="Document statuses to include in results")
    date_filter: Literal["day", "week", "month", "year"] | None = Field(None, validation_alias="dateFilter", serialization_alias="dateFilter", description="Any documents that have not been updated within the specified period will be filtered out")
    share_id: str | None = Field(None, validation_alias="shareId", serialization_alias="shareId", description="Filter results for the collection or document referenced by the shareId")
    sort: Literal["relevance", "createdAt", "updatedAt", "title"] | None = Field(None, description="Specifies the attributes by which search results will be sorted")
    direction: Literal["ASC", "DESC"] | None = Field(None, description="Specifies the sort order with respect to sort field")

class DocumentsUpdateBodyDataAttributesItem(PermissiveModel):
    data_attribute_id: str = Field(..., validation_alias="dataAttributeId", serialization_alias="dataAttributeId", description="Unique identifier for the data attribute.", json_schema_extra={'format': 'uuid'})
    value: str | bool | float = Field(..., description="The value of the data attribute. Can be a string, boolean, or number depending on the data attribute type.")

class DocumentsViewedBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    sort: str | None = None
    direction: Literal["ASC", "DESC"] | None = None

class EventsListBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    sort: str | None = None
    direction: Literal["ASC", "DESC"] | None = None
    name: str | None = Field(None, description="Filter to a specific event, e.g. \"collections.create\". Event names are in the format \"objects.verb\"")
    actor_id: str | None = Field(None, validation_alias="actorId", serialization_alias="actorId", description="Filter to events performed by the selected user", json_schema_extra={'format': 'uuid'})
    document_id: str | None = Field(None, validation_alias="documentId", serialization_alias="documentId", description="Filter to events performed in the selected document", json_schema_extra={'format': 'uuid'})
    collection_id: str | None = Field(None, validation_alias="collectionId", serialization_alias="collectionId", description="Filter to events performed in the selected collection", json_schema_extra={'format': 'uuid'})
    audit_log: bool | None = Field(None, validation_alias="auditLog", serialization_alias="auditLog", description="Whether to return detailed events suitable for an audit log. Without this flag less detailed event types will be returned.")

class FileOperationsListBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    sort: str | None = None
    direction: Literal["ASC", "DESC"] | None = None
    type_: Literal["export", "import"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of fileOperation")

class GroupsListBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    sort: str | None = None
    direction: Literal["ASC", "DESC"] | None = None
    user_id: str | None = Field(None, validation_alias="userId", serialization_alias="userId", description="Filter to groups including a specific user", json_schema_extra={'format': 'uuid'})
    external_id: str | None = Field(None, validation_alias="externalId", serialization_alias="externalId", description="Filter to groups matching an external ID", json_schema_extra={'format': 'uuid'})
    query: str | None = Field(None, description="Filter to groups matching a search query", json_schema_extra={'format': 'uuid'})

class GroupsMembershipsBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Group id")
    query: str | None = Field(None, description="Filter memberships by user names")

class Invite(PermissiveModel):
    name: str | None = Field(None, description="The full name of the user being invited")
    email: str | None = Field(None, description="The email address to invite")
    role: Literal["admin", "member", "viewer", "guest"] | None = None

class RevisionsListBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    sort: str | None = None
    direction: Literal["ASC", "DESC"] | None = None
    document_id: str | None = Field(None, validation_alias="documentId", serialization_alias="documentId", description="The document ID to retrieve revisions for", json_schema_extra={'format': 'uuid'})

class SharesListBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    sort: str | None = None
    direction: Literal["ASC", "DESC"] | None = None
    query: str | None = Field(None, description="Filter to shared documents matching a search query")

class TemplatesListBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    sort: str | None = None
    direction: Literal["ASC", "DESC"] | None = None
    collection_id: str | None = Field(None, validation_alias="collectionId", serialization_alias="collectionId", description="Optionally filter to a specific collection", json_schema_extra={'format': 'uuid'})

class User(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Unique identifier for the object.", json_schema_extra={'format': 'uuid'})
    name: str | None = Field(None, description="The name of this user, it is migrated from Slack or Google Workspace when the SSO connection is made but can be changed if necessary.")
    avatar_url: str | None = Field(None, validation_alias="avatarUrl", serialization_alias="avatarUrl", description="The URL for the image associated with this user, it will be displayed in the application UI and email notifications.", json_schema_extra={'format': 'uri'})
    email: str | None = Field(None, description="The email associated with this user, it is migrated from Slack or Google Workspace when the SSO connection is made but can be changed if necessary.", json_schema_extra={'format': 'email'})
    role: Literal["admin", "member", "viewer", "guest"] | None = None
    is_suspended: bool | None = Field(None, validation_alias="isSuspended", serialization_alias="isSuspended", description="Whether this user has been suspended.")
    last_active_at: str | None = Field(None, validation_alias="lastActiveAt", serialization_alias="lastActiveAt", description="The last time this user made an API request, this value is updated at most every 5 minutes.", json_schema_extra={'format': 'date-time'})
    created_at: str | None = Field(None, validation_alias="createdAt", serialization_alias="createdAt", description="The date and time that this user first signed in or was invited as a guest.", json_schema_extra={'format': 'date-time'})

class Collection(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Unique identifier for the object.", json_schema_extra={'format': 'uuid'})
    url_id: str | None = Field(None, validation_alias="urlId", serialization_alias="urlId", description="A short unique identifier that can be used to identify the collection instead of the UUID.")
    name: str | None = Field(None, description="The name of the collection.")
    description: str | None = Field(None, description="A description of the collection, may contain markdown formatting")
    sort: CollectionSort | None = Field(None, description="The sort of documents in the collection. Note that not all API responses respect this and it is left as a frontend concern to implement.")
    index: str | None = Field(None, description="The position of the collection in the sidebar")
    color: str | None = Field(None, description="A color representing the collection, this is used to help make collections more identifiable in the UI. It should be in HEX format including the #")
    icon: str | None = Field(None, description="A string that represents an icon in the outline-icons package or an emoji")
    permission: Literal["read", "read_write"] | None = None
    sharing: bool | None = Field(False, description="Whether public document sharing is enabled in this collection")
    created_at: str | None = Field(None, validation_alias="createdAt", serialization_alias="createdAt", description="The date and time that this object was created", json_schema_extra={'format': 'date-time'})
    updated_at: str | None = Field(None, validation_alias="updatedAt", serialization_alias="updatedAt", description="The date and time that this object was last changed", json_schema_extra={'format': 'date-time'})
    deleted_at: str | None = Field(None, validation_alias="deletedAt", serialization_alias="deletedAt", description="The date and time that this object was deleted", json_schema_extra={'format': 'date-time'})
    archived_at: str | None = Field(None, validation_alias="archivedAt", serialization_alias="archivedAt", description="The date and time that this object was archived", json_schema_extra={'format': 'date-time'})
    archived_by: User | None = Field(None, validation_alias="archivedBy", serialization_alias="archivedBy")

class FileOperation(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Unique identifier for the object.", json_schema_extra={'format': 'uuid'})
    type_: Literal["import", "export"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of file operation.")
    state: Literal["creating", "uploading", "complete", "error", "expired"] | None = Field(None, description="The state of the file operation.")
    collection: Any | Collection | None = None
    user: User | None = None
    size: float | None = Field(None, description="The size of the resulting file in bytes")
    created_at: str | None = Field(None, validation_alias="createdAt", serialization_alias="createdAt", description="The date and time that this object was created", json_schema_extra={'format': 'date-time'})

class UsersListBody(PermissiveModel):
    offset: float | None = None
    limit: float | None = None
    sort: str | None = None
    direction: Literal["ASC", "DESC"] | None = None
    query: str | None = None
    emails: list[str] | None = Field(None, description="Array of emails")
    filter_: Literal["all", "invited", "active", "suspended"] | None = Field(None, validation_alias="filter", serialization_alias="filter", description="The status to filter by")
    role: Literal["admin", "member", "viewer", "guest"] | None = None


# Rebuild models to resolve forward references (required for circular refs)
Collection.model_rebuild()
CollectionsGroupMembershipsBody.model_rebuild()
CollectionsListBody.model_rebuild()
CollectionsMembershipsBody.model_rebuild()
CollectionSort.model_rebuild()
CommentsListBody.model_rebuild()
DataAttributesListBody.model_rebuild()
DataAttributesUpdateBodyOptionsOptionsItem.model_rebuild()
DocumentsAnswerQuestionBody.model_rebuild()
DocumentsArchivedBody.model_rebuild()
DocumentsCreateBodyDataAttributesItem.model_rebuild()
DocumentsDeletedBody.model_rebuild()
DocumentsDraftsBody.model_rebuild()
DocumentsGroupMembershipsBody.model_rebuild()
DocumentsListBody.model_rebuild()
DocumentsSearchBody.model_rebuild()
DocumentsSearchTitlesBody.model_rebuild()
DocumentsUpdateBodyDataAttributesItem.model_rebuild()
DocumentsViewedBody.model_rebuild()
EventsListBody.model_rebuild()
FileOperation.model_rebuild()
FileOperationsListBody.model_rebuild()
GroupsListBody.model_rebuild()
GroupsMembershipsBody.model_rebuild()
Invite.model_rebuild()
RevisionsListBody.model_rebuild()
SharesListBody.model_rebuild()
TemplatesListBody.model_rebuild()
User.model_rebuild()
UsersListBody.model_rebuild()

"""
Shortcut MCP Server - Pydantic Models

Generated: 2026-04-25 15:35:28 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from _validators import StrictModel
from pydantic import AfterValidator, Field


def _check_unique_items(v: list) -> list:
    """Validate that array items are unique (OAS uniqueItems: true)."""
    seen = []
    for item in v:
        if item in seen:
            raise ValueError("array items must be unique")
        seen.append(item)
    return v


__all__ = [
    "CreateCategoryRequest",
    "CreateDocRequest",
    "CreateEpicCommentCommentRequest",
    "CreateEpicCommentRequest",
    "CreateEpicHealthRequest",
    "CreateEpicRequest",
    "CreateGroupRequest",
    "CreateIterationRequest",
    "CreateLabelRequest",
    "CreateLinkedFileRequest",
    "CreateMilestoneRequest",
    "CreateMultipleStoriesRequest",
    "CreateObjectiveRequest",
    "CreateProjectRequest",
    "CreateStoryCommentRequest",
    "CreateStoryFromTemplateRequest",
    "CreateStoryLinkRequest",
    "CreateStoryReactionRequest",
    "CreateStoryRequest",
    "CreateTaskRequest",
    "DeleteCategoryRequest",
    "DeleteCustomFieldRequest",
    "DeleteDocRequest",
    "DeleteEpicCommentRequest",
    "DeleteEpicRequest",
    "DeleteFileRequest",
    "DeleteGenericIntegrationRequest",
    "DeleteIterationRequest",
    "DeleteLabelRequest",
    "DeleteLinkedFileRequest",
    "DeleteMilestoneRequest",
    "DeleteMultipleStoriesRequest",
    "DeleteObjectiveRequest",
    "DeleteProjectRequest",
    "DeleteStoryCommentRequest",
    "DeleteStoryLinkRequest",
    "DeleteStoryReactionRequest",
    "DeleteStoryRequest",
    "DeleteTaskRequest",
    "GetCategoryRequest",
    "GetCustomFieldRequest",
    "GetDocRequest",
    "GetEntityTemplateRequest",
    "GetEpicCommentRequest",
    "GetEpicHealthRequest",
    "GetEpicRequest",
    "GetExternalLinkStoriesRequest",
    "GetFileRequest",
    "GetGenericIntegrationRequest",
    "GetGroupRequest",
    "GetIterationRequest",
    "GetKeyResultRequest",
    "GetLabelRequest",
    "GetLinkedFileRequest",
    "GetMemberRequest",
    "GetMilestoneRequest",
    "GetObjectiveRequest",
    "GetProjectRequest",
    "GetRepositoryRequest",
    "GetStoryCommentRequest",
    "GetStoryLinkRequest",
    "GetStoryRequest",
    "GetTaskRequest",
    "GetWorkflowRequest",
    "LinkDocumentToEpicRequest",
    "ListCategoryMilestonesRequest",
    "ListCategoryObjectivesRequest",
    "ListDocumentEpicsRequest",
    "ListEpicCommentsRequest",
    "ListEpicDocumentsRequest",
    "ListEpicHealthsRequest",
    "ListEpicsPaginatedRequest",
    "ListEpicsRequest",
    "ListEpicStoriesRequest",
    "ListGroupsRequest",
    "ListGroupStoriesRequest",
    "ListIterationStoriesRequest",
    "ListLabelEpicsRequest",
    "ListLabelsRequest",
    "ListLabelStoriesRequest",
    "ListMembersRequest",
    "ListMilestoneEpicsRequest",
    "ListObjectiveEpicsRequest",
    "ListStoriesRequest",
    "ListStoryCommentRequest",
    "ListStorySubTasksRequest",
    "QueryStoriesRequest",
    "SearchDocumentsRequest",
    "SearchEpicsRequest",
    "SearchIterationsRequest",
    "SearchMilestonesRequest",
    "SearchObjectivesRequest",
    "SearchRequest",
    "SearchStoriesRequest",
    "StoryHistoryRequest",
    "UnlinkCommentThreadFromSlackRequest",
    "UnlinkDocumentFromEpicRequest",
    "UnlinkProductboardFromEpicRequest",
    "UpdateCategoryRequest",
    "UpdateCustomFieldRequest",
    "UpdateDocRequest",
    "UpdateEpicCommentRequest",
    "UpdateEpicRequest",
    "UpdateFileRequest",
    "UpdateGroupRequest",
    "UpdateHealthRequest",
    "UpdateIterationRequest",
    "UpdateKeyResultRequest",
    "UpdateLabelRequest",
    "UpdateLinkedFileRequest",
    "UpdateMilestoneRequest",
    "UpdateMultipleStoriesRequest",
    "UpdateObjectiveRequest",
    "UpdateProjectRequest",
    "UpdateStoryCommentRequest",
    "UpdateStoryLinkRequest",
    "UpdateStoryRequest",
    "UpdateTaskRequest",
    "UploadFilesRequest",
    "CreateCategoryParams",
    "CreateLabelParams",
    "CreateStoryCommentParams",
    "CreateStoryLinkParams",
    "CreateStoryParams",
    "CreateSubTaskParams",
    "CreateTaskParams",
    "CustomFieldValueParams",
    "LinkSubTaskParams",
    "RemoveCustomFieldParams",
    "RemoveLabelParams",
    "UpdateCustomFieldEnumValue",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: create_category
class CreateCategoryRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the new Category. Must be between 1 and 128 characters.", min_length=1, max_length=128)
    external_id: str | None = Field(default=None, description="An optional external identifier for this Category, useful when importing from another tool. Must be between 1 and 128 characters if provided.", min_length=1, max_length=128)
    type_: Any | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The entity type this Category is associated with. Currently supports Milestone or Objective types.")
class CreateCategoryRequest(StrictModel):
    """Create a new Category in Shortcut for organizing Milestones or Objectives. Categories help structure and group related work items by type."""
    body: CreateCategoryRequestBody

# Operation: get_category
class GetCategoryRequestPath(StrictModel):
    category_public_id: int = Field(default=..., validation_alias="category-public-id", serialization_alias="category-public-id", description="The unique identifier for the category as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetCategoryRequest(StrictModel):
    """Retrieve detailed information about a specific category using its unique identifier. Returns the category's properties and metadata."""
    path: GetCategoryRequestPath

# Operation: update_category
class UpdateCategoryRequestPath(StrictModel):
    category_public_id: int = Field(default=..., validation_alias="category-public-id", serialization_alias="category-public-id", description="The unique identifier of the Category to update. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class UpdateCategoryRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the Category. Must be at least 1 character long and unique across all Categories.", min_length=1)
    archived: bool | None = Field(default=None, description="Whether the Category should be archived. Set to true to archive or false to unarchive.")
class UpdateCategoryRequest(StrictModel):
    """Update a Category's name and/or archived status. Category names must be unique; attempting to use a name that already exists will result in an error."""
    path: UpdateCategoryRequestPath
    body: UpdateCategoryRequestBody | None = None

# Operation: delete_category
class DeleteCategoryRequestPath(StrictModel):
    category_public_id: int = Field(default=..., validation_alias="category-public-id", serialization_alias="category-public-id", description="The unique identifier of the category to delete, provided as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class DeleteCategoryRequest(StrictModel):
    """Permanently delete a category by its unique identifier. This operation removes the category and cannot be undone."""
    path: DeleteCategoryRequestPath

# Operation: list_milestones_for_category
class ListCategoryMilestonesRequestPath(StrictModel):
    category_public_id: int = Field(default=..., validation_alias="category-public-id", serialization_alias="category-public-id", description="The unique identifier of the category. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class ListCategoryMilestonesRequest(StrictModel):
    """Retrieve all milestones associated with a specific category. Returns a complete list of milestones within the given category."""
    path: ListCategoryMilestonesRequestPath

# Operation: list_objectives_for_category
class ListCategoryObjectivesRequestPath(StrictModel):
    category_public_id: int = Field(default=..., validation_alias="category-public-id", serialization_alias="category-public-id", description="The unique identifier of the Category. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class ListCategoryObjectivesRequest(StrictModel):
    """Retrieves all Objectives associated with a specific Category. Use this to view the complete list of objectives within a category."""
    path: ListCategoryObjectivesRequestPath

# Operation: get_custom_field
class GetCustomFieldRequestPath(StrictModel):
    custom_field_public_id: str = Field(default=..., validation_alias="custom-field-public-id", serialization_alias="custom-field-public-id", description="The unique identifier of the custom field to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetCustomFieldRequest(StrictModel):
    """Retrieve a specific custom field by its unique identifier. Returns the complete configuration and metadata for the custom field."""
    path: GetCustomFieldRequestPath

# Operation: update_custom_field
class UpdateCustomFieldRequestPath(StrictModel):
    custom_field_public_id: str = Field(default=..., validation_alias="custom-field-public-id", serialization_alias="custom-field-public-id", description="The unique identifier of the custom field to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class UpdateCustomFieldRequestBody(StrictModel):
    enabled: bool | None = Field(default=None, description="Whether this field is enabled for use in the workspace. Only enabled fields can be applied to stories.")
    name: str | None = Field(default=None, description="The display name of the custom field. Must be between 1 and 63 characters.", min_length=1, max_length=63)
    values: list[UpdateCustomFieldEnumValue] | None = Field(default=None, description="An ordered collection of enum values defining the field's domain. The order in this collection determines the sort order of values. Omit existing values to delete them; include new values as objects with a 'value' property and optional 'color_key' to create them inline.")
    icon_set_identifier: str | None = Field(default=None, description="A frontend-controlled identifier for the icon associated with this custom field. Must be between 1 and 63 characters.", min_length=1, max_length=63)
    description: str | None = Field(default=None, description="A description explaining the purpose and use of this custom field.")
class UpdateCustomFieldRequest(StrictModel):
    """Update the definition of a custom field, including its name, description, enabled status, enum values, and icon. Enum values are ordered by their position in the collection; omit values to delete them, or include new values with only a 'value' property to create them inline."""
    path: UpdateCustomFieldRequestPath
    body: UpdateCustomFieldRequestBody | None = None

# Operation: delete_custom_field
class DeleteCustomFieldRequestPath(StrictModel):
    custom_field_public_id: str = Field(default=..., validation_alias="custom-field-public-id", serialization_alias="custom-field-public-id", description="The unique UUID identifier of the custom field to delete.", json_schema_extra={'format': 'uuid'})
class DeleteCustomFieldRequest(StrictModel):
    """Permanently delete a custom field by its unique identifier. This operation removes the custom field and all associated data."""
    path: DeleteCustomFieldRequestPath

# Operation: create_document
class CreateDocRequestBody(StrictModel):
    title: str = Field(default=..., description="The document title. Must be between 1 and 256 characters long.", min_length=1, max_length=256)
    content: str = Field(default=..., description="The document content. Can be formatted as markdown or HTML depending on the content_format parameter.")
class CreateDocRequest(StrictModel):
    """Creates a new document with the specified title and content. Supports both markdown and HTML content formats via the content_format parameter."""
    body: CreateDocRequestBody

# Operation: get_doc
class GetDocRequestPath(StrictModel):
    doc_public_id: str = Field(default=..., validation_alias="doc-public-id", serialization_alias="doc-public-id", description="The unique identifier of the Doc to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetDocRequest(StrictModel):
    """Retrieve a Doc by its public ID, including its full content. Optionally request HTML-formatted content using the content_format query parameter."""
    path: GetDocRequestPath

# Operation: update_document
class UpdateDocRequestPath(StrictModel):
    doc_public_id: str = Field(default=..., validation_alias="doc-public-id", serialization_alias="doc-public-id", description="The unique public identifier for the document being updated, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class UpdateDocRequestBody(StrictModel):
    title: str | None = Field(default=None, description="The new title for the document. Must be between 1 and 256 characters long.", min_length=1, max_length=256)
    content: str | None = Field(default=None, description="The new content for the document. Supports markdown or HTML format as specified by the content_format parameter.")
class UpdateDocRequest(StrictModel):
    """Update a document's title and/or content. Supports markdown or HTML input. Connected users receive real-time SSE notifications to refresh their view, while disconnected sessions trigger cache invalidation to ensure fresh content."""
    path: UpdateDocRequestPath
    body: UpdateDocRequestBody | None = None

# Operation: delete_doc
class DeleteDocRequestPath(StrictModel):
    doc_public_id: str = Field(default=..., validation_alias="doc-public-id", serialization_alias="doc-public-id", description="The unique public identifier of the Doc to delete, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class DeleteDocRequest(StrictModel):
    """Permanently deletes a Doc and all its associated data. Requires admin access to the document. Connected clients will be notified of the deletion via SSE events."""
    path: DeleteDocRequestPath

# Operation: list_document_epics
class ListDocumentEpicsRequestPath(StrictModel):
    doc_public_id: str = Field(default=..., validation_alias="doc-public-id", serialization_alias="doc-public-id", description="The unique public identifier of the Document, provided as a UUID.", json_schema_extra={'format': 'uuid'})
class ListDocumentEpicsRequest(StrictModel):
    """Retrieve all Epics associated with a specific Document. Returns a collection of Epics linked to the Document identified by its public ID."""
    path: ListDocumentEpicsRequestPath

# Operation: link_document_to_epic
class LinkDocumentToEpicRequestPath(StrictModel):
    doc_public_id: str = Field(default=..., validation_alias="doc-public-id", serialization_alias="doc-public-id", description="The unique identifier of the Document to link, provided as a UUID.", json_schema_extra={'format': 'uuid'})
    epic_public_id: int = Field(default=..., validation_alias="epic-public-id", serialization_alias="epic-public-id", description="The unique identifier of the Epic to link the document to, provided as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class LinkDocumentToEpicRequest(StrictModel):
    """Create a relationship between a Document and an Epic, associating the document with the specified epic for organizational and tracking purposes."""
    path: LinkDocumentToEpicRequestPath

# Operation: remove_document_from_epic
class UnlinkDocumentFromEpicRequestPath(StrictModel):
    doc_public_id: str = Field(default=..., validation_alias="doc-public-id", serialization_alias="doc-public-id", description="The unique identifier of the Document to unlink, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
    epic_public_id: int = Field(default=..., validation_alias="epic-public-id", serialization_alias="epic-public-id", description="The unique identifier of the Epic to unlink, formatted as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class UnlinkDocumentFromEpicRequest(StrictModel):
    """Remove the relationship between a Document and an Epic, unlinking them from each other."""
    path: UnlinkDocumentFromEpicRequestPath

# Operation: get_entity_template
class GetEntityTemplateRequestPath(StrictModel):
    entity_template_public_id: str = Field(default=..., validation_alias="entity-template-public-id", serialization_alias="entity-template-public-id", description="The unique identifier of the entity template, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetEntityTemplateRequest(StrictModel):
    """Retrieve detailed information about a specific entity template using its unique identifier. This operation returns the complete configuration and metadata for the requested entity template."""
    path: GetEntityTemplateRequestPath

# Operation: list_epics
class ListEpicsRequestQuery(StrictModel):
    includes_description: bool | None = Field(default=None, description="Set to true to include the full description text for each Epic in the response; omit or set to false to return only basic Epic metadata.")
class ListEpicsRequest(StrictModel):
    """Retrieve a list of all Epics with their core attributes. Optionally include full descriptions for each Epic."""
    query: ListEpicsRequestQuery | None = None

# Operation: create_epic
class CreateEpicRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A detailed explanation of the Epic's purpose and scope. Limited to 100,000 characters.", max_length=100000)
    objective_ids: list[int] | None = Field(default=None, description="An array of Objective IDs to associate with this Epic. Objectives provide strategic alignment for the Epic.")
    name: str = Field(default=..., description="The Epic's title or name. Required field, must be between 1 and 256 characters.", min_length=1, max_length=256)
    planned_start_date: str | None = Field(default=None, description="The date when work on this Epic is planned to begin. Specify as an ISO 8601 formatted date-time string.", json_schema_extra={'format': 'date-time'})
    requested_by_id: str | None = Field(default=None, description="The UUID of the team member who requested this Epic. Used to track Epic ownership and accountability.", json_schema_extra={'format': 'uuid'})
    epic_state_id: int | None = Field(default=None, description="The numeric ID of the Epic State that defines the Epic's workflow status (e.g., Backlog, In Progress, Done).", json_schema_extra={'format': 'int64'})
    group_ids: list[str] | None = Field(default=None, description="An array of Group UUIDs to associate with this Epic. Groups help organize and categorize Epics within your workspace.")
    converted_from_story_id: int | None = Field(default=None, description="The numeric ID of a Story that was converted into this Epic. Use this when promoting an existing Story to Epic status.", json_schema_extra={'format': 'int64'})
    external_id: str | None = Field(default=None, description="An external identifier for this Epic, useful when importing from other tools or systems. Limited to 128 characters and should be unique within your workspace.", max_length=128)
    deadline: str | None = Field(default=None, description="The date by which this Epic must be completed. Specify as an ISO 8601 formatted date-time string.", json_schema_extra={'format': 'date-time'})
class CreateEpicRequest(StrictModel):
    """Create a new Epic in Shortcut. An Epic is a large body of work that can be broken down into Stories and related to Objectives and Groups."""
    body: CreateEpicRequestBody

# Operation: list_epics_paginated
class ListEpicsPaginatedRequestQuery(StrictModel):
    includes_description: bool | None = Field(default=None, description="Include the full description text for each Epic in the response. When false or omitted, descriptions are excluded from the results.")
    page: int | None = Field(default=None, description="The page number to retrieve, starting from 1. Defaults to the first page if not specified.", json_schema_extra={'format': 'int64'})
    page_size: int | None = Field(default=None, description="The number of Epics to return per page, between 1 and 250 items. Defaults to 10 if not specified.", json_schema_extra={'format': 'int64'})
class ListEpicsPaginatedRequest(StrictModel):
    """Retrieve a paginated list of Epics with optional descriptions. Use pagination parameters to control which results are returned and how many per page."""
    query: ListEpicsPaginatedRequestQuery | None = None

# Operation: get_epic
class GetEpicRequestPath(StrictModel):
    epic_public_id: int = Field(default=..., validation_alias="epic-public-id", serialization_alias="epic-public-id", description="The unique identifier of the Epic to retrieve. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetEpicRequest(StrictModel):
    """Retrieve detailed information about a specific Epic by its unique identifier. Returns the Epic's properties and metadata."""
    path: GetEpicRequestPath

# Operation: update_epic
class UpdateEpicRequestPath(StrictModel):
    epic_public_id: int = Field(default=..., validation_alias="epic-public-id", serialization_alias="epic-public-id", description="The unique identifier of the Epic to update. This is a 64-bit integer value found in the Shortcut UI.", json_schema_extra={'format': 'int64'})
class UpdateEpicRequestBody(StrictModel):
    description: str | None = Field(default=None, description="The Epic's description text. Can be up to 100,000 characters long.", max_length=100000)
    archived: bool | None = Field(default=None, description="Whether the Epic is archived. Set to true to archive or false to unarchive.")
    objective_ids: list[int] | None = Field(default=None, description="An array of Objective IDs to associate with this Epic. Order is not significant.")
    name: str | None = Field(default=None, description="The Epic's display name. Must be between 1 and 256 characters long.", min_length=1, max_length=256)
    planned_start_date: str | None = Field(default=None, description="The Epic's planned start date in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    requested_by_id: str | None = Field(default=None, description="The UUID of the team member who requested this Epic.", json_schema_extra={'format': 'uuid'})
    epic_state_id: int | None = Field(default=None, description="The 64-bit integer ID of the Epic State (e.g., Backlog, In Progress, Done) to assign to this Epic.", json_schema_extra={'format': 'int64'})
    group_ids: list[str] | None = Field(default=None, description="An array of Group UUIDs to associate with this Epic. Order is not significant.")
    external_id: str | None = Field(default=None, description="An external identifier for this Epic, useful when importing from other tools. Maximum 128 characters.", max_length=128)
    deadline: str | None = Field(default=None, description="The Epic's deadline in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
class UpdateEpicRequest(StrictModel):
    """Update an Epic's properties including name, description, dates, state, and relationships. Only the Epic ID is required; all other fields are optional and will only be updated if provided."""
    path: UpdateEpicRequestPath
    body: UpdateEpicRequestBody | None = None

# Operation: delete_epic
class DeleteEpicRequestPath(StrictModel):
    epic_public_id: int = Field(default=..., validation_alias="epic-public-id", serialization_alias="epic-public-id", description="The unique identifier of the Epic to delete, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class DeleteEpicRequest(StrictModel):
    """Permanently delete an Epic by its unique identifier. This operation removes the Epic and cannot be undone."""
    path: DeleteEpicRequestPath

# Operation: list_epic_comments
class ListEpicCommentsRequestPath(StrictModel):
    epic_public_id: int = Field(default=..., validation_alias="epic-public-id", serialization_alias="epic-public-id", description="The unique identifier of the Epic. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class ListEpicCommentsRequest(StrictModel):
    """Retrieve all comments associated with a specific Epic. Returns a list of comment objects ordered by creation date."""
    path: ListEpicCommentsRequestPath

# Operation: create_epic_comment
class CreateEpicCommentRequestPath(StrictModel):
    epic_public_id: int = Field(default=..., validation_alias="epic-public-id", serialization_alias="epic-public-id", description="The unique identifier of the Epic where the comment will be posted.", json_schema_extra={'format': 'int64'})
class CreateEpicCommentRequestBody(StrictModel):
    text: str = Field(default=..., description="The comment text content. Must be between 1 and 100,000 characters.", min_length=1, max_length=100000)
    author_id: str | None = Field(default=None, description="The UUID of the team member who authored this comment. If not provided, defaults to the user associated with the API token.", json_schema_extra={'format': 'uuid'})
    external_id: str | None = Field(default=None, description="An optional external identifier for this comment, useful when importing comments from other tools. Maximum length is 128 characters.", max_length=128)
class CreateEpicCommentRequest(StrictModel):
    """Add a threaded comment to an Epic. The comment can be authored by the API token holder or another team member, and optionally linked to an external system via an external ID."""
    path: CreateEpicCommentRequestPath
    body: CreateEpicCommentRequestBody

# Operation: get_epic_comment
class GetEpicCommentRequestPath(StrictModel):
    epic_public_id: int = Field(default=..., validation_alias="epic-public-id", serialization_alias="epic-public-id", description="The unique identifier of the Epic that contains the comment. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    comment_public_id: int = Field(default=..., validation_alias="comment-public-id", serialization_alias="comment-public-id", description="The unique identifier of the specific comment to retrieve. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class GetEpicCommentRequest(StrictModel):
    """Retrieves detailed information about a specific comment on an Epic. Use this to fetch comment content, metadata, and other details by providing both the Epic ID and the Comment ID."""
    path: GetEpicCommentRequestPath

# Operation: create_reply_to_epic_comment
class CreateEpicCommentCommentRequestPath(StrictModel):
    epic_public_id: int = Field(default=..., validation_alias="epic-public-id", serialization_alias="epic-public-id", description="The unique identifier of the Epic containing the parent comment. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    comment_public_id: int = Field(default=..., validation_alias="comment-public-id", serialization_alias="comment-public-id", description="The unique identifier of the parent Epic Comment to which you are replying. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class CreateEpicCommentCommentRequestBody(StrictModel):
    text: str = Field(default=..., description="The text content of the reply. Must be between 1 and 100,000 characters.", min_length=1, max_length=100000)
    author_id: str | None = Field(default=None, description="The UUID of the team member who authored this reply. If not provided, defaults to the user associated with the API token making the request.", json_schema_extra={'format': 'uuid'})
    external_id: str | None = Field(default=None, description="An optional external identifier for this comment, useful when importing comments from other tools. Maximum length is 128 characters.", max_length=128)
class CreateEpicCommentCommentRequest(StrictModel):
    """Create a nested reply to an existing Epic Comment. This allows you to add threaded discussion to Epic Comments within an Epic."""
    path: CreateEpicCommentCommentRequestPath
    body: CreateEpicCommentCommentRequestBody

# Operation: update_epic_comment
class UpdateEpicCommentRequestPath(StrictModel):
    epic_public_id: int = Field(default=..., validation_alias="epic-public-id", serialization_alias="epic-public-id", description="The unique identifier of the Epic containing the comment. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    comment_public_id: int = Field(default=..., validation_alias="comment-public-id", serialization_alias="comment-public-id", description="The unique identifier of the Comment to update. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class UpdateEpicCommentRequestBody(StrictModel):
    text: str = Field(default=..., description="The new text content for the comment. Replaces the existing comment text.")
class UpdateEpicCommentRequest(StrictModel):
    """Update the text content of an existing threaded comment on an Epic. Allows modification of comment text while preserving the comment's identity and thread context."""
    path: UpdateEpicCommentRequestPath
    body: UpdateEpicCommentRequestBody

# Operation: delete_epic_comment
class DeleteEpicCommentRequestPath(StrictModel):
    epic_public_id: int = Field(default=..., validation_alias="epic-public-id", serialization_alias="epic-public-id", description="The unique identifier of the epic containing the comment. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    comment_public_id: int = Field(default=..., validation_alias="comment-public-id", serialization_alias="comment-public-id", description="The unique identifier of the comment to delete. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class DeleteEpicCommentRequest(StrictModel):
    """Permanently delete a comment from an epic. This action cannot be undone."""
    path: DeleteEpicCommentRequestPath

# Operation: list_epic_documents
class ListEpicDocumentsRequestPath(StrictModel):
    epic_public_id: int = Field(default=..., validation_alias="epic-public-id", serialization_alias="epic-public-id", description="The unique identifier of the Epic. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class ListEpicDocumentsRequest(StrictModel):
    """Retrieve all documents associated with a specific Epic. Returns a collection of documents linked to the Epic for reference and collaboration."""
    path: ListEpicDocumentsRequestPath

# Operation: get_epic_health
class GetEpicHealthRequestPath(StrictModel):
    epic_public_id: int = Field(default=..., validation_alias="epic-public-id", serialization_alias="epic-public-id", description="The unique identifier of the Epic. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetEpicHealthRequest(StrictModel):
    """Retrieve the current health status of a specified Epic. This provides insights into the Epic's overall condition and progress."""
    path: GetEpicHealthRequestPath

# Operation: create_epic_health
class CreateEpicHealthRequestPath(StrictModel):
    epic_public_id: int = Field(default=..., validation_alias="epic-public-id", serialization_alias="epic-public-id", description="The unique identifier of the Epic for which you're creating a health status. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class CreateEpicHealthRequestBody(StrictModel):
    status: Literal["At Risk", "On Track", "Off Track", "No Health"] = Field(default=..., description="The health status level for the Epic. Must be one of: 'At Risk', 'On Track', 'Off Track', or 'No Health'.")
    text: str | None = Field(default=None, description="An optional detailed explanation or context for the health status being recorded.")
class CreateEpicHealthRequest(StrictModel):
    """Create a new health status record for an Epic to track its current state. This allows you to document whether the Epic is progressing as planned, facing risks, or has encountered issues."""
    path: CreateEpicHealthRequestPath
    body: CreateEpicHealthRequestBody

# Operation: list_epic_health_history
class ListEpicHealthsRequestPath(StrictModel):
    epic_public_id: int = Field(default=..., validation_alias="epic-public-id", serialization_alias="epic-public-id", description="The unique identifier of the Epic whose health history you want to retrieve. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class ListEpicHealthsRequest(StrictModel):
    """Retrieve the complete health status history for a specified Epic, ordered from most recent to oldest. Use this to track how an Epic's health has evolved over time."""
    path: ListEpicHealthsRequestPath

# Operation: list_epic_stories
class ListEpicStoriesRequestPath(StrictModel):
    epic_public_id: int = Field(default=..., validation_alias="epic-public-id", serialization_alias="epic-public-id", description="The unique identifier of the epic. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class ListEpicStoriesRequestQuery(StrictModel):
    includes_description: bool | None = Field(default=None, description="Set to true to include story descriptions in the response; false or omit to exclude them.")
class ListEpicStoriesRequest(StrictModel):
    """Retrieve all stories associated with a specific epic. Optionally include story descriptions in the response."""
    path: ListEpicStoriesRequestPath
    query: ListEpicStoriesRequestQuery | None = None

# Operation: remove_productboard_from_epic
class UnlinkProductboardFromEpicRequestPath(StrictModel):
    epic_public_id: int = Field(default=..., validation_alias="epic-public-id", serialization_alias="epic-public-id", description="The unique identifier of the Epic to unlink from Productboard. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class UnlinkProductboardFromEpicRequest(StrictModel):
    """Unlink a Productboard epic from an Epic, removing the association between the two resources."""
    path: UnlinkProductboardFromEpicRequestPath

# Operation: list_stories_by_external_link
class GetExternalLinkStoriesRequestQuery(StrictModel):
    external_link: str = Field(default=..., description="A valid HTTP or HTTPS URL (must start with http:// or https://) that is associated with one or more stories. Maximum length is 2048 characters.", max_length=2048, pattern='^https?://.+$')
class GetExternalLinkStoriesRequest(StrictModel):
    """Retrieve all stories associated with a given external link. Use this to find stories that reference or are linked to a specific URL."""
    query: GetExternalLinkStoriesRequestQuery

# Operation: upload_files
class UploadFilesRequestBody(StrictModel):
    story_id: int | None = Field(default=None, description="The ID of the story to associate these uploaded files with. If omitted, files are uploaded without story association.", json_schema_extra={'format': 'int64'})
    file0: str = Field(default=..., description="The primary file to upload. This parameter is required; at least one file must be provided in the request.", json_schema_extra={'format': 'binary'})
    file1: str | None = Field(default=None, description="An optional additional file to upload alongside file0.", json_schema_extra={'format': 'binary'})
    file2: str | None = Field(default=None, description="An optional additional file to upload alongside file0 and file1.", json_schema_extra={'format': 'binary'})
    file3: str | None = Field(default=None, description="An optional additional file to upload alongside file0, file1, and file2.", json_schema_extra={'format': 'binary'})
class UploadFilesRequest(StrictModel):
    """Upload one or more files to the system, optionally associating them with a specific story. Files are submitted using multipart/form-data encoding with each file assigned to a separate form field."""
    body: UploadFilesRequestBody

# Operation: get_file
class GetFileRequestPath(StrictModel):
    file_public_id: int = Field(default=..., validation_alias="file-public-id", serialization_alias="file-public-id", description="The unique identifier for the file, provided as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetFileRequest(StrictModel):
    """Retrieve detailed information about a specific uploaded file using its unique public identifier."""
    path: GetFileRequestPath

# Operation: update_file
class UpdateFileRequestPath(StrictModel):
    file_public_id: int = Field(default=..., validation_alias="file-public-id", serialization_alias="file-public-id", description="The unique identifier of the file in Shortcut (64-bit integer).", json_schema_extra={'format': 'int64'})
class UpdateFileRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A descriptive text for the file, up to 4096 characters.", max_length=4096)
    name: str | None = Field(default=None, description="The display name of the file, between 1 and 1024 characters.", min_length=1, max_length=1024)
    external_id: str | None = Field(default=None, description="An optional external identifier you can assign to the file for tracking purposes, up to 128 characters.", max_length=128)
class UpdateFileRequest(StrictModel):
    """Update the metadata properties of an uploaded file, including its name, description, and external identifier. The file content itself cannot be modified through this operation."""
    path: UpdateFileRequestPath
    body: UpdateFileRequestBody | None = None

# Operation: delete_file
class DeleteFileRequestPath(StrictModel):
    file_public_id: int = Field(default=..., validation_alias="file-public-id", serialization_alias="file-public-id", description="The unique identifier of the file to delete, provided as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class DeleteFileRequest(StrictModel):
    """Permanently delete a previously uploaded file by its unique identifier. This action cannot be undone."""
    path: DeleteFileRequestPath

# Operation: list_groups
class ListGroupsRequestQuery(StrictModel):
    archived: bool | None = Field(default=None, description="Filter groups by their archived state. Set to true to return only archived groups, false to return only active groups, or omit to return all groups regardless of status.")
class ListGroupsRequest(StrictModel):
    """Retrieve a list of groups (teams) in Shortcut. Groups represent collections of users that can be associated with stories, epics, and iterations. Optionally filter by archived status."""
    query: ListGroupsRequestQuery | None = None

# Operation: create_group
class CreateGroupRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A detailed description of the group's purpose and scope, up to 4096 characters.", max_length=4096)
    member_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, description="Array of member IDs to add to the group upon creation. Members can be added or modified after creation.")
    workflow_ids: list[int] | None = Field(default=None, description="Array of workflow IDs to associate with the group. Workflows define the processes and automations available to group members.")
    name: str = Field(default=..., description="The display name of the group, between 1 and 63 characters. This is the human-readable identifier shown in the UI.", min_length=1, max_length=63)
    mention_name: str = Field(default=..., description="The mention handle for the group, between 1 and 63 characters. Used for @-mentions and programmatic references (e.g., @engineering-team).", min_length=1, max_length=63)
    display_icon_id: str | None = Field(default=None, description="A UUID-formatted icon ID to use as the group's avatar. If not provided, a default icon will be assigned.", json_schema_extra={'format': 'uuid'})
class CreateGroupRequest(StrictModel):
    """Create a new group with members and workflows. Groups can be used to organize and manage collections of members and their associated workflows."""
    body: CreateGroupRequestBody

# Operation: get_group
class GetGroupRequestPath(StrictModel):
    group_public_id: str = Field(default=..., validation_alias="group-public-id", serialization_alias="group-public-id", description="The unique identifier of the group, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetGroupRequest(StrictModel):
    """Retrieve detailed information about a specific group using its unique public identifier. Returns the group's metadata and configuration."""
    path: GetGroupRequestPath

# Operation: update_group
class UpdateGroupRequestPath(StrictModel):
    group_public_id: str = Field(default=..., validation_alias="group-public-id", serialization_alias="group-public-id", description="The unique identifier of the group to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class UpdateGroupRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A text description of the group, up to 4096 characters.", max_length=4096)
    archived: bool | None = Field(default=None, description="Whether the group is archived. Archived groups are typically hidden from active use but retain their data.")
    display_icon_id: str | None = Field(default=None, description="The UUID of an icon to use as the group's avatar.", json_schema_extra={'format': 'uuid'})
    mention_name: str | None = Field(default=None, description="The mention name for the group, used in @mentions. Must be 1-63 characters long.", min_length=1, max_length=63)
    name: str | None = Field(default=None, description="The display name of the group, 1-63 characters long.", min_length=1, max_length=63)
    default_workflow_id: int | None = Field(default=None, description="The numeric ID of the workflow to set as the default for stories created in this group.", json_schema_extra={'format': 'int64'})
    member_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, description="An array of member IDs to add to the group. Each ID should be a valid member identifier.")
    workflow_ids: list[int] | None = Field(default=None, description="An array of workflow IDs to associate with the group, enabling these workflows for story creation.")
class UpdateGroupRequest(StrictModel):
    """Update an existing group's properties including name, description, icon, workflow settings, and membership. Allows archiving groups and modifying their configuration."""
    path: UpdateGroupRequestPath
    body: UpdateGroupRequestBody | None = None

# Operation: list_group_stories
class ListGroupStoriesRequestPath(StrictModel):
    group_public_id: str = Field(default=..., validation_alias="group-public-id", serialization_alias="group-public-id", description="The unique identifier of the Group, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class ListGroupStoriesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return per request. Defaults to 1,000 and cannot exceed 1,000.", json_schema_extra={'format': 'int64'})
    offset: int | None = Field(default=None, description="Number of results to skip before returning data, enabling pagination through large result sets. Defaults to 0.", json_schema_extra={'format': 'int64'})
class ListGroupStoriesRequest(StrictModel):
    """Retrieve all Stories assigned to a specific Group with pagination support. Results are limited to a maximum of 1,000 stories by default."""
    path: ListGroupStoriesRequestPath
    query: ListGroupStoriesRequestQuery | None = None

# Operation: update_health
class UpdateHealthRequestPath(StrictModel):
    health_public_id: str = Field(default=..., validation_alias="health-public-id", serialization_alias="health-public-id", description="The unique identifier of the Health record to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class UpdateHealthRequestBody(StrictModel):
    status: Literal["At Risk", "On Track", "Off Track", "No Health"] | None = Field(default=None, description="The health status level for the Epic. Must be one of: At Risk, On Track, Off Track, or No Health.")
    text: str | None = Field(default=None, description="A text description providing context or details about the health status.")
class UpdateHealthRequest(StrictModel):
    """Update the health status and description of an Epic. Modify the current health state and optional status text to reflect the Epic's current condition."""
    path: UpdateHealthRequestPath
    body: UpdateHealthRequestBody | None = None

# Operation: get_webhook_integration
class GetGenericIntegrationRequestPath(StrictModel):
    integration_public_id: int = Field(default=..., validation_alias="integration-public-id", serialization_alias="integration-public-id", description="The unique public identifier of the webhook integration to retrieve. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetGenericIntegrationRequest(StrictModel):
    """Retrieve a specific webhook integration by its public identifier. Use this to fetch configuration and details for a webhook integration."""
    path: GetGenericIntegrationRequestPath

# Operation: delete_webhook_integration
class DeleteGenericIntegrationRequestPath(StrictModel):
    integration_public_id: int = Field(default=..., validation_alias="integration-public-id", serialization_alias="integration-public-id", description="The unique public identifier of the webhook integration to delete, provided as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class DeleteGenericIntegrationRequest(StrictModel):
    """Permanently delete a webhook integration by its public identifier. This action cannot be undone and will remove all associated webhook configurations."""
    path: DeleteGenericIntegrationRequestPath

# Operation: create_iteration
class CreateIterationRequestBody(StrictModel):
    group_ids: list[str] | None = Field(default=None, description="An array of group UUIDs to add as followers to this iteration. Currently, the web UI supports only one group association at a time.")
    description: str | None = Field(default=None, description="A detailed description of the iteration's purpose or scope. Limited to 100,000 characters.", max_length=100000)
    name: str = Field(default=..., description="The name of the iteration. Must be between 1 and 256 characters.", min_length=1, max_length=256)
    start_date: str = Field(default=..., description="The start date of the iteration in ISO 8601 format (e.g., 2019-07-01). Required and must be a valid date string.", min_length=1)
    end_date: str = Field(default=..., description="The end date of the iteration in ISO 8601 format (e.g., 2019-07-01). Required and must be a valid date string.", min_length=1)
class CreateIterationRequest(StrictModel):
    """Create a new iteration (sprint or planning cycle) with a specified name, date range, and optional description. Optionally add groups as followers to the iteration."""
    body: CreateIterationRequestBody

# Operation: get_iteration
class GetIterationRequestPath(StrictModel):
    iteration_public_id: int = Field(default=..., validation_alias="iteration-public-id", serialization_alias="iteration-public-id", description="The unique identifier for the iteration as a 64-bit integer. This ID is used to look up and retrieve the specific iteration's details.", json_schema_extra={'format': 'int64'})
class GetIterationRequest(StrictModel):
    """Retrieve detailed information about a specific iteration by its public ID. Use this to fetch iteration metadata, status, and associated data."""
    path: GetIterationRequestPath

# Operation: update_iteration
class UpdateIterationRequestPath(StrictModel):
    iteration_public_id: int = Field(default=..., validation_alias="iteration-public-id", serialization_alias="iteration-public-id", description="The unique identifier of the iteration to update. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class UpdateIterationRequestBody(StrictModel):
    group_ids: list[str] | None = Field(default=None, description="An array of group UUIDs to add as followers to this iteration. Currently, the web UI supports one group association at a time.")
    description: str | None = Field(default=None, description="A detailed description of the iteration. Maximum length is 100,000 characters.", max_length=100000)
    name: str | None = Field(default=None, description="The display name of the iteration. Must be between 1 and 256 characters.", min_length=1, max_length=256)
    start_date: str | None = Field(default=None, description="The start date of the iteration in ISO 8601 format (e.g., YYYY-MM-DD). Must be a non-empty string.", min_length=1)
    end_date: str | None = Field(default=None, description="The end date of the iteration in ISO 8601 format (e.g., YYYY-MM-DD). Must be a non-empty string.", min_length=1)
class UpdateIterationRequest(StrictModel):
    """Update an existing iteration with new metadata such as name, description, dates, and group followers. Allows partial updates—only provided fields are modified."""
    path: UpdateIterationRequestPath
    body: UpdateIterationRequestBody | None = None

# Operation: delete_iteration
class DeleteIterationRequestPath(StrictModel):
    iteration_public_id: int = Field(default=..., validation_alias="iteration-public-id", serialization_alias="iteration-public-id", description="The unique public identifier of the iteration to delete, provided as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class DeleteIterationRequest(StrictModel):
    """Permanently delete an iteration by its public ID. This action cannot be undone and will remove the iteration and all associated data."""
    path: DeleteIterationRequestPath

# Operation: list_iteration_stories
class ListIterationStoriesRequestPath(StrictModel):
    iteration_public_id: int = Field(default=..., validation_alias="iteration-public-id", serialization_alias="iteration-public-id", description="The unique identifier of the iteration. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class ListIterationStoriesRequestQuery(StrictModel):
    includes_description: bool | None = Field(default=None, description="Set to true to include story descriptions in the response; false or omit to exclude them.")
class ListIterationStoriesRequest(StrictModel):
    """Retrieve all stories associated with a specific iteration. Optionally include story descriptions in the response."""
    path: ListIterationStoriesRequestPath
    query: ListIterationStoriesRequestQuery | None = None

# Operation: get_key_result
class GetKeyResultRequestPath(StrictModel):
    key_result_public_id: str = Field(default=..., validation_alias="key-result-public-id", serialization_alias="key-result-public-id", description="The unique identifier of the Key Result to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetKeyResultRequest(StrictModel):
    """Retrieve detailed information about a specific Key Result by its unique identifier. Returns the Key Result's properties and current state."""
    path: GetKeyResultRequestPath

# Operation: update_key_result
class UpdateKeyResultRequestPath(StrictModel):
    key_result_public_id: str = Field(default=..., validation_alias="key-result-public-id", serialization_alias="key-result-public-id", description="The unique identifier of the Key Result to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class UpdateKeyResultRequestBodyObservedValue(StrictModel):
    numeric_value: str | None = Field(default=None, validation_alias="numeric_value", serialization_alias="numeric_value", description="The observed numeric value as a decimal string, limited to a maximum of two decimal places.")
    boolean_value: bool | None = Field(default=None, validation_alias="boolean_value", serialization_alias="boolean_value", description="The observed boolean value (true or false).")
class UpdateKeyResultRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The updated name for the Key Result. Maximum length is 1024 characters.", max_length=1024)
    observed_value: UpdateKeyResultRequestBodyObservedValue | None = None
class UpdateKeyResultRequest(StrictModel):
    """Update a Key Result's name, initial value, observed value, or target value. Supports numeric values (up to 2 decimal places) or boolean values for the observed metric."""
    path: UpdateKeyResultRequestPath
    body: UpdateKeyResultRequestBody | None = None

# Operation: list_labels
class ListLabelsRequestQuery(StrictModel):
    slim: bool | None = Field(default=None, description="When true, returns a lightweight version of each label with minimal attributes; when false or omitted, returns complete label details.")
class ListLabelsRequest(StrictModel):
    """Retrieve all labels available in the system with their complete attributes. Optionally request slim versions containing only essential label information."""
    query: ListLabelsRequestQuery | None = None

# Operation: create_label
class CreateLabelRequestBody(StrictModel):
    """Request parameters for creating a Label on a Shortcut Story."""
    name: str = Field(default=..., description="The display name for the label. Must be between 1 and 128 characters.", min_length=1, max_length=128)
    description: str | None = Field(default=None, description="Optional descriptive text explaining the label's purpose or usage. Limited to 1024 characters.", max_length=1024)
    external_id: str | None = Field(default=None, description="Optional external identifier for labels imported from other tools. Use this to maintain references to the original tool's ID. Must be between 1 and 128 characters if provided.", min_length=1, max_length=128)
class CreateLabelRequest(StrictModel):
    """Create a new label in Shortcut to organize and categorize work items. Labels help teams tag and filter issues, stories, and other work across projects."""
    body: CreateLabelRequestBody

# Operation: get_label
class GetLabelRequestPath(StrictModel):
    label_public_id: int = Field(default=..., validation_alias="label-public-id", serialization_alias="label-public-id", description="The unique identifier of the label to retrieve, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetLabelRequest(StrictModel):
    """Retrieve detailed information about a specific label by its unique identifier. Returns the label's properties and metadata."""
    path: GetLabelRequestPath

# Operation: update_label
class UpdateLabelRequestPath(StrictModel):
    label_public_id: int = Field(default=..., validation_alias="label-public-id", serialization_alias="label-public-id", description="The unique identifier of the label to update. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class UpdateLabelRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the label. Must be between 1 and 128 characters long.", min_length=1, max_length=128)
    description: str | None = Field(default=None, description="The new description for the label. Must not exceed 1024 characters.", max_length=1024)
    archived: bool | None = Field(default=None, description="Whether the label should be archived. Set to true to archive the label, or false to unarchive it.")
class UpdateLabelRequest(StrictModel):
    """Update a label's name, description, or archived status. The label name must be unique within the system; attempting to use a name that already exists will result in an error."""
    path: UpdateLabelRequestPath
    body: UpdateLabelRequestBody | None = None

# Operation: delete_label
class DeleteLabelRequestPath(StrictModel):
    label_public_id: int = Field(default=..., validation_alias="label-public-id", serialization_alias="label-public-id", description="The unique identifier of the label to delete, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class DeleteLabelRequest(StrictModel):
    """Permanently delete a label by its unique identifier. This operation removes the label and cannot be undone."""
    path: DeleteLabelRequestPath

# Operation: list_epics_for_label
class ListLabelEpicsRequestPath(StrictModel):
    label_public_id: int = Field(default=..., validation_alias="label-public-id", serialization_alias="label-public-id", description="The unique identifier of the Label. Must be a positive integer value.", json_schema_extra={'format': 'int64'})
class ListLabelEpicsRequest(StrictModel):
    """Retrieve all Epics associated with a specific Label. Use this to view Epic-level work items grouped by a particular label."""
    path: ListLabelEpicsRequestPath

# Operation: list_stories_by_label
class ListLabelStoriesRequestPath(StrictModel):
    label_public_id: int = Field(default=..., validation_alias="label-public-id", serialization_alias="label-public-id", description="The unique identifier of the label. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class ListLabelStoriesRequestQuery(StrictModel):
    includes_description: bool | None = Field(default=None, description="Set to true to include story descriptions in the response; false or omit to exclude them.")
class ListLabelStoriesRequest(StrictModel):
    """Retrieve all stories associated with a specific label. Optionally include story descriptions in the response."""
    path: ListLabelStoriesRequestPath
    query: ListLabelStoriesRequestQuery | None = None

# Operation: create_linked_file
class CreateLinkedFileRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A brief explanation of the file's purpose or contents. Limited to 512 characters.", max_length=512)
    story_id: int | None = Field(default=None, description="The numeric ID of the story to associate this linked file with. If omitted, the file is created without a story association.", json_schema_extra={'format': 'int64'})
    name: str = Field(default=..., description="The display name for the linked file. Must be between 1 and 256 characters.", min_length=1, max_length=256)
    type_: Literal["google", "url", "dropbox", "box", "onedrive"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The source service or integration type for the file. Must be one of: google (Google Drive), url (direct link), dropbox (Dropbox), box (Box), or onedrive (OneDrive).")
    content_type: str | None = Field(default=None, description="The MIME type describing the file's format (e.g., text/plain, application/pdf). Limited to 128 characters.", max_length=128)
    url: str = Field(default=..., description="The full URL pointing to the linked file. Must be a valid HTTP or HTTPS URL and cannot exceed 2048 characters.", max_length=2048, pattern='^https?://.+$')
class CreateLinkedFileRequest(StrictModel):
    """Create a new linked file in Shortcut that references an external file from an integrated service like Google Drive, Dropbox, Box, OneDrive, or a direct URL. Optionally associate the file with a specific story."""
    body: CreateLinkedFileRequestBody

# Operation: get_linked_file
class GetLinkedFileRequestPath(StrictModel):
    linked_file_public_id: int = Field(default=..., validation_alias="linked-file-public-id", serialization_alias="linked-file-public-id", description="The unique public identifier of the linked file to retrieve. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetLinkedFileRequest(StrictModel):
    """Retrieve detailed information about a specific linked file using its unique public identifier."""
    path: GetLinkedFileRequestPath

# Operation: update_linked_file
class UpdateLinkedFileRequestPath(StrictModel):
    linked_file_public_id: int = Field(default=..., validation_alias="linked-file-public-id", serialization_alias="linked-file-public-id", description="The unique identifier of the linked file to update. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class UpdateLinkedFileRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A brief description of the file's purpose or content. Limited to 512 characters.", max_length=512)
    story_id: int | None = Field(default=None, description="The ID of the story to associate with this linked file. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
    name: str | None = Field(default=None, description="The display name of the file. Must be at least 1 character long.", min_length=1)
    type_: Literal["google", "url", "dropbox", "box", "onedrive"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The source integration type for the file. Valid options are: google (Google Drive), url (direct link), dropbox (Dropbox), box (Box), or onedrive (OneDrive).")
    url: str | None = Field(default=None, description="The web address of the linked file. Must be a valid HTTP or HTTPS URL and cannot exceed 2048 characters.", max_length=2048, pattern='^https?://.+$')
class UpdateLinkedFileRequest(StrictModel):
    """Update properties of a previously attached linked file, such as its name, description, associated story, or source URL. Supports files from multiple integration types including Google Drive, Dropbox, Box, OneDrive, and direct URLs."""
    path: UpdateLinkedFileRequestPath
    body: UpdateLinkedFileRequestBody | None = None

# Operation: delete_linked_file
class DeleteLinkedFileRequestPath(StrictModel):
    linked_file_public_id: int = Field(default=..., validation_alias="linked-file-public-id", serialization_alias="linked-file-public-id", description="The unique identifier of the linked file to delete. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class DeleteLinkedFileRequest(StrictModel):
    """Permanently delete a previously attached linked file by its unique identifier. This operation removes the file association and cannot be undone."""
    path: DeleteLinkedFileRequestPath

# Operation: list_workspace_members
class ListMembersRequestQuery(StrictModel):
    org_public_id: str | None = Field(default=None, validation_alias="org-public-id", serialization_alias="org-public-id", description="Filter results to members belonging to a specific Organization by providing its unique identifier (UUID format).", json_schema_extra={'format': 'uuid'})
    disabled: bool | None = Field(default=None, description="Filter members by their account status: true returns only disabled members, false returns only enabled members. Omit to include all members regardless of status.")
class ListMembersRequest(StrictModel):
    """Retrieve a list of members in the Workspace, with optional filtering by Organization and member status."""
    query: ListMembersRequestQuery | None = None

# Operation: get_member
class GetMemberRequestPath(StrictModel):
    member_public_id: str = Field(default=..., validation_alias="member-public-id", serialization_alias="member-public-id", description="The unique identifier of the member to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetMemberRequestQuery(StrictModel):
    org_public_id: str | None = Field(default=None, validation_alias="org-public-id", serialization_alias="org-public-id", description="Optional organization identifier (UUID format) to scope the member lookup to a specific organization.", json_schema_extra={'format': 'uuid'})
class GetMemberRequest(StrictModel):
    """Retrieve detailed information about a specific member by their unique identifier. Optionally scope the lookup to a particular organization."""
    path: GetMemberRequestPath
    query: GetMemberRequestQuery | None = None

# Operation: create_milestone
class CreateMilestoneRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the Milestone. Must be between 1 and 256 characters.", min_length=1, max_length=256)
    description: str | None = Field(default=None, description="Optional description of the Milestone. Can be up to 100,000 characters.", max_length=100000)
    categories: list[CreateCategoryParams] | None = Field(default=None, description="Optional array of Category IDs to attach to the Milestone. Provide as a list of numeric identifiers.")
class CreateMilestoneRequest(StrictModel):
    """Create a new Milestone in Shortcut. Note: This operation is deprecated; use create_objective for new implementations."""
    body: CreateMilestoneRequestBody

# Operation: get_milestone
class GetMilestoneRequestPath(StrictModel):
    milestone_public_id: int = Field(default=..., validation_alias="milestone-public-id", serialization_alias="milestone-public-id", description="The unique identifier of the milestone to retrieve, provided as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetMilestoneRequest(StrictModel):
    """Retrieve detailed information about a specific milestone by its public ID. Note: This operation is deprecated; use get_objective instead for new implementations."""
    path: GetMilestoneRequestPath

# Operation: update_milestone
class UpdateMilestoneRequestPath(StrictModel):
    milestone_public_id: int = Field(default=..., validation_alias="milestone-public-id", serialization_alias="milestone-public-id", description="The unique identifier of the milestone to update. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class UpdateMilestoneRequestBody(StrictModel):
    description: str | None = Field(default=None, description="The milestone's description text. Can be up to 100,000 characters long.", max_length=100000)
    archived: bool | None = Field(default=None, description="Whether the milestone is archived. Set to true to archive or false to unarchive.")
    name: str | None = Field(default=None, description="The display name for the milestone. Must be between 1 and 256 characters.", min_length=1, max_length=256)
    categories: list[CreateCategoryParams] | None = Field(default=None, description="An array of category IDs to attach to the milestone. Each element should be a category identifier.")
class UpdateMilestoneRequest(StrictModel):
    """Update properties of an existing milestone, including its name, description, archived status, and associated categories. Note: This operation is deprecated; use update_objective for new implementations."""
    path: UpdateMilestoneRequestPath
    body: UpdateMilestoneRequestBody | None = None

# Operation: delete_milestone
class DeleteMilestoneRequestPath(StrictModel):
    milestone_public_id: int = Field(default=..., validation_alias="milestone-public-id", serialization_alias="milestone-public-id", description="The unique identifier of the milestone to delete, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class DeleteMilestoneRequest(StrictModel):
    """Delete a milestone by its public ID. Note: This operation is deprecated; use delete_objective instead for new implementations."""
    path: DeleteMilestoneRequestPath

# Operation: list_epics_for_milestone
class ListMilestoneEpicsRequestPath(StrictModel):
    milestone_public_id: int = Field(default=..., validation_alias="milestone-public-id", serialization_alias="milestone-public-id", description="The unique identifier of the milestone. Must be a positive integer value.", json_schema_extra={'format': 'int64'})
class ListMilestoneEpicsRequest(StrictModel):
    """Retrieve all epics associated with a specific milestone. This operation is deprecated; use list_objective_epics instead for new implementations."""
    path: ListMilestoneEpicsRequestPath

# Operation: create_objective
class CreateObjectiveRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the Objective. Must be between 1 and 256 characters.", min_length=1, max_length=256)
    description: str | None = Field(default=None, description="A detailed description of the Objective. Can be up to 100,000 characters to provide comprehensive context and guidance.", max_length=100000)
    categories: list[CreateCategoryParams] | None = Field(default=None, description="An array of Category IDs to associate with this Objective for organizational purposes. Each ID should reference an existing Category.")
class CreateObjectiveRequest(StrictModel):
    """Create a new Objective in Shortcut to define goals and track progress. Objectives can be organized with categories and include detailed descriptions."""
    body: CreateObjectiveRequestBody

# Operation: get_objective
class GetObjectiveRequestPath(StrictModel):
    objective_public_id: int = Field(default=..., validation_alias="objective-public-id", serialization_alias="objective-public-id", description="The unique public identifier for the Objective. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetObjectiveRequest(StrictModel):
    """Retrieve detailed information about a specific Objective by its public ID. Use this to fetch the full details of an Objective you want to inspect or reference."""
    path: GetObjectiveRequestPath

# Operation: update_objective
class UpdateObjectiveRequestPath(StrictModel):
    objective_public_id: int = Field(default=..., validation_alias="objective-public-id", serialization_alias="objective-public-id", description="The unique identifier of the Objective to update. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class UpdateObjectiveRequestBody(StrictModel):
    description: str | None = Field(default=None, description="The Objective's description text. Can be up to 100,000 characters long.", max_length=100000)
    archived: bool | None = Field(default=None, description="A boolean flag to archive or unarchive the Objective. Set to true to archive, false to unarchive.")
    name: str | None = Field(default=None, description="The name of the Objective. Must be between 1 and 256 characters long.", min_length=1, max_length=256)
    categories: list[CreateCategoryParams] | None = Field(default=None, description="An array of Category IDs to attach to the Objective. Provide as a list of numeric identifiers.")
class UpdateObjectiveRequest(StrictModel):
    """Update an Objective's properties including its name, description, archived status, and associated categories. Use this operation to modify any aspect of an existing Objective."""
    path: UpdateObjectiveRequestPath
    body: UpdateObjectiveRequestBody | None = None

# Operation: delete_objective
class DeleteObjectiveRequestPath(StrictModel):
    objective_public_id: int = Field(default=..., validation_alias="objective-public-id", serialization_alias="objective-public-id", description="The unique public identifier of the Objective to delete, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class DeleteObjectiveRequest(StrictModel):
    """Permanently delete an Objective by its public ID. This action cannot be undone."""
    path: DeleteObjectiveRequestPath

# Operation: list_epics_for_objective
class ListObjectiveEpicsRequestPath(StrictModel):
    objective_public_id: int = Field(default=..., validation_alias="objective-public-id", serialization_alias="objective-public-id", description="The unique identifier of the objective. Must be a positive integer value.", json_schema_extra={'format': 'int64'})
class ListObjectiveEpicsRequest(StrictModel):
    """Retrieve all epics associated with a specific objective. Epics are returned as a collection within the objective."""
    path: ListObjectiveEpicsRequestPath

# Operation: create_project
class CreateProjectRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A detailed description of the project's purpose and scope. Limited to 100,000 characters.", max_length=100000)
    name: str = Field(default=..., description="The display name for the project. Must be between 1 and 128 characters long.", min_length=1, max_length=128)
    start_time: str | None = Field(default=None, description="The project's start date in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    external_id: str | None = Field(default=None, description="An external identifier for the project, useful when migrating from another tool. Limited to 128 characters.", max_length=128)
    team_id: int = Field(default=..., description="The numeric ID of the team that will own this project.", json_schema_extra={'format': 'int64'})
    iteration_length: int | None = Field(default=None, description="The duration of each iteration cycle in this project, specified in weeks.", json_schema_extra={'format': 'int64'})
    abbreviation: str | None = Field(default=None, description="A short abbreviation for the project, typically 3 characters or fewer, used in story summaries. Limited to 63 characters.", max_length=63)
class CreateProjectRequest(StrictModel):
    """Creates a new Shortcut project within a specified team. The project name is required, and you can optionally configure iteration length, description, start date, abbreviation, and external identifiers."""
    body: CreateProjectRequestBody

# Operation: get_project
class GetProjectRequestPath(StrictModel):
    project_public_id: int = Field(default=..., validation_alias="project-public-id", serialization_alias="project-public-id", description="The unique public identifier for the project. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetProjectRequest(StrictModel):
    """Retrieve detailed information about a specific project using its unique public identifier. Returns comprehensive project metadata and configuration."""
    path: GetProjectRequestPath

# Operation: update_project
class UpdateProjectRequestPath(StrictModel):
    project_public_id: int = Field(default=..., validation_alias="project-public-id", serialization_alias="project-public-id", description="The unique identifier of the project to update. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class UpdateProjectRequestBody(StrictModel):
    description: str | None = Field(default=None, description="The project's description text. Can be up to 100,000 characters long.", max_length=100000)
    archived: bool | None = Field(default=None, description="Whether the project is archived. Set to true to archive the project or false to unarchive it.")
    days_to_thermometer: int | None = Field(default=None, description="The number of days before the thermometer indicator appears in story summaries. Must be a non-negative 64-bit integer.", json_schema_extra={'format': 'int64'})
    name: str | None = Field(default=None, description="The project's display name. Must be between 1 and 128 characters long.", min_length=1, max_length=128)
    show_thermometer: bool | None = Field(default=None, description="Enable or disable thermometer indicators in story summaries. Set to true to show thermometers or false to hide them.")
    team_id: int | None = Field(default=None, description="The 64-bit integer ID of the team this project belongs to. Use this to reassign the project to a different team.", json_schema_extra={'format': 'int64'})
    abbreviation: str | None = Field(default=None, description="A short abbreviation for the project used in story summaries. Recommended to keep to 3 characters or fewer.")
class UpdateProjectRequest(StrictModel):
    """Update project properties such as name, description, team assignment, and thermometer settings. Changes are applied immediately to the specified project."""
    path: UpdateProjectRequestPath
    body: UpdateProjectRequestBody | None = None

# Operation: delete_project
class DeleteProjectRequestPath(StrictModel):
    project_public_id: int = Field(default=..., validation_alias="project-public-id", serialization_alias="project-public-id", description="The unique identifier of the project to delete, provided as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class DeleteProjectRequest(StrictModel):
    """Permanently delete a project. Projects can only be deleted if all associated stories have been moved or deleted; attempting to delete a project with remaining stories will result in a 422 error."""
    path: DeleteProjectRequestPath

# Operation: list_stories
class ListStoriesRequestPath(StrictModel):
    project_public_id: int = Field(default=..., validation_alias="project-public-id", serialization_alias="project-public-id", description="The unique identifier of the project. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class ListStoriesRequestQuery(StrictModel):
    includes_description: bool | None = Field(default=None, description="Set to true to include story descriptions in the response; omit or set to false to exclude them.")
class ListStoriesRequest(StrictModel):
    """Retrieve all stories in a project with their core attributes. Optionally include story descriptions in the response."""
    path: ListStoriesRequestPath
    query: ListStoriesRequestQuery | None = None

# Operation: get_repository
class GetRepositoryRequestPath(StrictModel):
    repo_public_id: int = Field(default=..., validation_alias="repo-public-id", serialization_alias="repo-public-id", description="The unique public identifier of the repository as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetRepositoryRequest(StrictModel):
    """Retrieve detailed information about a specific repository using its unique public identifier."""
    path: GetRepositoryRequestPath

# Operation: search_epics_and_stories
class SearchRequestQuery(StrictModel):
    query: str = Field(default=..., description="Search query using supported search operators (see help documentation). Must be at least 1 character long.", min_length=1)
    page_size: int | None = Field(default=None, description="Number of results per page, between 1 and 250 inclusive. Defaults to a standard page size if not specified.", json_schema_extra={'format': 'int64'})
    detail: Literal["full", "slim"] | None = Field(default=None, description="Level of detail in results: 'full' includes all descriptions, comments, and related item details (pull requests, branches, tasks); 'slim' omits large text fields and references related items by ID only. Defaults to 'full'.")
    entity_types: list[Literal["story", "milestone", "epic", "iteration", "objective"]] | None = Field(default=None, description="Entity types to include in search results. Supports: epic, iteration, objective, story. Defaults to story and epic if not specified. Provide as an array of entity type strings.")
class SearchRequest(StrictModel):
    """Search for Epics and Stories using search operators and filters. Results are ranked and paginated; use the `next` value from previous responses to maintain stable ordering across pages."""
    query: SearchRequestQuery

# Operation: search_documents
class SearchDocumentsRequestQuery(StrictModel):
    title: str = Field(default=..., description="Search text to match against document titles using fuzzy matching. Must be at least 1 character long.", min_length=1)
    archived: bool | None = Field(default=None, description="Filter by archive status: true returns archived documents, false returns non-archived documents.")
    created_by_me: bool | None = Field(default=None, description="Filter by document ownership: true returns documents created by the current user, false returns documents created by others.")
    followed_by_me: bool | None = Field(default=None, description="Filter by follow status: true returns documents the current user is following, false returns documents not followed.")
    page_size: int | None = Field(default=None, description="Number of results to return per page. Must be between 1 and 250.", json_schema_extra={'format': 'int64'})
class SearchDocumentsRequest(StrictModel):
    """Search for documents by title with optional filtering by archive status, ownership, and follow status. Supports fuzzy matching on document titles and pagination of results."""
    query: SearchDocumentsRequestQuery

# Operation: search_epics
class SearchEpicsRequestQuery(StrictModel):
    query: str = Field(default=..., description="Search query using supported operators (see search operators documentation). Must be at least 1 character long.", min_length=1)
    page_size: int | None = Field(default=None, description="Number of results per page, between 1 and 250 inclusive. Defaults to a standard page size if not specified.", json_schema_extra={'format': 'int64'})
    detail: Literal["full", "slim"] | None = Field(default=None, description="Level of detail in results: 'full' includes all descriptions, comments, and related item details (pull requests, branches, tasks); 'slim' omits large text fields and references related items by ID only. Defaults to 'full'.")
    entity_types: list[Literal["story", "milestone", "epic", "iteration", "objective"]] | None = Field(default=None, description="Entity types to include in search results. Supports: epic, iteration, objective, story. Defaults to story and epic if not specified.")
class SearchEpicsRequest(StrictModel):
    """Search for epics using query operators and optional filters. Results support pagination via the `next` cursor to maintain stable ordering as the search index evolves."""
    query: SearchEpicsRequestQuery

# Operation: search_iterations
class SearchIterationsRequestQuery(StrictModel):
    query: str = Field(default=..., description="Search query using supported search operators. Must be at least 1 character long. See search operators documentation for syntax and available filters.", min_length=1)
    page_size: int | None = Field(default=None, description="Number of results to return per page, between 1 and 250 results. Defaults to a standard page size if not specified.", json_schema_extra={'format': 'int64'})
    detail: Literal["full", "slim"] | None = Field(default=None, description="Level of detail in results. Use 'full' for complete data including descriptions, comments, and related item details, or 'slim' to omit large text fields and reference related items by ID only. Defaults to 'full'.")
    entity_types: list[Literal["story", "milestone", "epic", "iteration", "objective"]] | None = Field(default=None, description="Entity types to include in search results. Accepts multiple types: epic, iteration, objective, or story. Defaults to story and epic if not specified.")
class SearchIterationsRequest(StrictModel):
    """Search for iterations using query operators and filters. Results are ordered by search ranking and can be paginated using the next cursor from previous responses to maintain stable ordering."""
    query: SearchIterationsRequestQuery

# Operation: search_milestones
class SearchMilestonesRequestQuery(StrictModel):
    query: str = Field(default=..., description="Search query using supported search operators. Must be at least 1 character long.", min_length=1)
    page_size: int | None = Field(default=None, description="Number of results per page, between 1 and 250 inclusive. Defaults to a standard page size if not specified.", json_schema_extra={'format': 'int64'})
    detail: Literal["full", "slim"] | None = Field(default=None, description="Level of detail in results: 'full' includes all descriptions, comments, and related item details; 'slim' omits large text fields and references related items by ID only. Defaults to 'full'.")
    entity_types: list[Literal["story", "milestone", "epic", "iteration", "objective"]] | None = Field(default=None, description="Entity types to include in search results. Supports: epic, iteration, objective, story. Defaults to story and epic if not specified. Provide as an array of entity type strings.")
class SearchMilestonesRequest(StrictModel):
    """Search for milestones using query operators and filters. Results are paginated and support stable ordering through cursor-based navigation."""
    query: SearchMilestonesRequestQuery

# Operation: search_objectives
class SearchObjectivesRequestQuery(StrictModel):
    query: str = Field(default=..., description="Search query using supported search operators. Must be at least 1 character long. See search operators documentation for syntax details.", min_length=1)
    page_size: int | None = Field(default=None, description="Number of results to return per page, between 1 and 250 results.", json_schema_extra={'format': 'int64'})
    detail: Literal["full", "slim"] | None = Field(default=None, description="Level of detail in results. Use 'full' for complete data including descriptions, comments, and related item details, or 'slim' to omit large text fields and reference related items by ID only. Defaults to 'full'.")
    entity_types: list[Literal["story", "milestone", "epic", "iteration", "objective"]] | None = Field(default=None, description="Entity types to include in search results. Accepts any combination of: epic, iteration, objective, story. Defaults to story and epic if not specified.")
class SearchObjectivesRequest(StrictModel):
    """Search for Objectives using query operators and filters. Results are ranked by relevance and can be paginated using the `next` value from previous responses to maintain stable ordering."""
    query: SearchObjectivesRequestQuery

# Operation: search_stories
class SearchStoriesRequestQuery(StrictModel):
    query: str = Field(default=..., description="Search query using supported operators (see search operators documentation). Must be at least 1 character long.", min_length=1)
    page_size: int | None = Field(default=None, description="Number of results per page, between 1 and 250 inclusive. Defaults to a standard page size if not specified.", json_schema_extra={'format': 'int64'})
    detail: Literal["full", "slim"] | None = Field(default=None, description="Level of detail in results: 'full' includes all descriptions, comments, and related item details; 'slim' omits large text fields and references related items by ID only. Defaults to 'full'.")
    entity_types: list[Literal["story", "milestone", "epic", "iteration", "objective"]] | None = Field(default=None, description="Entity types to include in search results. Supports: epic, iteration, objective, story. Defaults to story and epic if not specified. Provide as an array of entity type strings.")
class SearchStoriesRequest(StrictModel):
    """Search for stories and related entities using query operators and filters. Results support pagination via the `next` cursor to maintain stable ordering as the search index evolves."""
    query: SearchStoriesRequestQuery

# Operation: create_story
class CreateStoryRequestBody(StrictModel):
    """Request parameters for creating a story."""
    description: str | None = Field(default=None, description="The story's description text. Supports up to 100,000 characters.", max_length=100000)
    archived: bool | None = Field(default=None, description="Whether the story should be archived upon creation.")
    story_links: list[CreateStoryLinkParams] | None = Field(default=None, description="An array of story links to attach to this story. Each link establishes a relationship between stories.")
    story_type: Literal["feature", "chore", "bug"] | None = Field(default=None, description="Categorizes the story as a feature, bug, or chore.")
    name: str = Field(default=..., description="The story's title. Must be between 1 and 512 characters.", min_length=1, max_length=512)
    comments: list[CreateStoryCommentParams] | None = Field(default=None, description="An array of comments to add to the story immediately upon creation.")
    story_template_id: str | None = Field(default=None, description="Associates this story with a story template by its UUID. No template content is automatically inherited.", json_schema_extra={'format': 'uuid'})
    sub_tasks: list[LinkSubTaskParams | CreateSubTaskParams] | None = Field(default=None, description="An array of sub-tasks to create or link. Each entry can reference an existing story or define a new sub-task. Only applicable when the Sub-task feature is enabled.")
    requested_by_id: str | None = Field(default=None, description="The UUID of the team member who requested this story.", json_schema_extra={'format': 'uuid'})
    iteration_id: int | None = Field(default=None, description="The numeric ID of the iteration this story belongs to.", json_schema_extra={'format': 'int64'})
    tasks: list[CreateTaskParams] | None = Field(default=None, description="An array of tasks to associate with this story.")
    workflow_state_id: int | None = Field(default=None, description="The numeric ID of the workflow state for this story. Either this or project_id must be provided, but not both.", json_schema_extra={'format': 'int64'})
    external_id: str | None = Field(default=None, description="An external identifier for this story, useful when importing from other tools. Supports up to 1,024 characters.", max_length=1024)
    parent_story_id: int | None = Field(default=None, description="The numeric ID of the parent story, making this story a sub-task. Only applicable when the Sub-task feature is enabled.", json_schema_extra={'format': 'int64'})
    estimate: int | None = Field(default=None, description="The point estimate for this story's complexity. Can be null to leave unestimated.", json_schema_extra={'format': 'int64'})
    deadline: str | None = Field(default=None, description="The story's due date in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class CreateStoryRequest(StrictModel):
    """Create a new story in your Shortcut workspace. You must specify either a workflow_state_id or project_id (but not both); workflow_state_id is recommended as projects are being sunset."""
    body: CreateStoryRequestBody

# Operation: create_stories
class CreateMultipleStoriesRequestBody(StrictModel):
    stories: list[CreateStoryParams] = Field(default=..., description="An array of story objects to create. Each story object uses the same schema as individual story creation. Order is preserved in processing.")
class CreateMultipleStoriesRequest(StrictModel):
    """Create multiple stories in a single batch request. Each story is created with the same configuration options available in individual story creation."""
    body: CreateMultipleStoriesRequestBody

# Operation: update_multiple_stories
class UpdateMultipleStoriesRequestBody(StrictModel):
    archived: bool | None = Field(default=None, description="Archive or unarchive the selected stories.")
    story_ids: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(default=..., description="The unique identifiers of the stories to update. Required to specify which stories are affected by this bulk operation.")
    story_type: Literal["feature", "chore", "bug"] | None = Field(default=None, description="Classify the story as a feature request, bug fix, or chore. Must be one of: feature, chore, or bug.")
    follower_ids_add: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, description="UUIDs of team members to add as followers to the stories. Followers receive notifications about story updates.")
    follower_ids_remove: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, description="UUIDs of team members to remove from the stories' followers list.")
    requested_by_id: str | None = Field(default=None, description="UUID of the team member who requested the story.", json_schema_extra={'format': 'uuid'})
    iteration_id: int | None = Field(default=None, description="The iteration or sprint ID to assign the stories to.", json_schema_extra={'format': 'int64'})
    custom_fields_remove: list[CustomFieldValueParams] | None = Field(default=None, description="Custom field values to remove from the stories. Specify as a map of CustomField ID to CustomFieldEnumValue ID.")
    labels_add: list[CreateLabelParams] | None = Field(default=None, description="Labels to add to the stories. Provide as an array of label identifiers or names.")
    workflow_state_id: int | None = Field(default=None, description="The workflow state ID representing the status to move the stories to (e.g., backlog, in progress, done).", json_schema_extra={'format': 'int64'})
    estimate: int | None = Field(default=None, description="Point estimate for story complexity and effort. Use null to mark stories as unestimated.", json_schema_extra={'format': 'int64'})
    owner_ids_remove: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, description="UUIDs of team members to remove as owners from the stories.")
    custom_fields_add: list[CustomFieldValueParams] | None = Field(default=None, description="Custom field values to add to the stories. Specify as a map of CustomField ID to CustomFieldEnumValue ID.")
    labels_remove: list[CreateLabelParams] | None = Field(default=None, description="Labels to remove from the stories. Provide as an array of label identifiers or names.")
    deadline: str | None = Field(default=None, description="The due date for the stories in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    owner_ids_add: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, description="UUIDs of team members to add as owners to the stories. Owners are responsible for completing the work.")
class UpdateMultipleStoriesRequest(StrictModel):
    """Bulk update multiple stories with changes to properties like status, assignments, estimates, and metadata. Apply changes across numerous stories simultaneously to streamline project management workflows."""
    body: UpdateMultipleStoriesRequestBody

# Operation: delete_stories_bulk
class DeleteMultipleStoriesRequestBody(StrictModel):
    story_ids: Annotated[list[int], AfterValidator(_check_unique_items)] = Field(default=..., description="A list of story IDs to delete. Provide the IDs as an array of strings or numbers representing the stories you want to remove. All stories must be archived before deletion.")
class DeleteMultipleStoriesRequest(StrictModel):
    """Permanently delete multiple archived stories in a single operation. This bulk deletion operation allows you to remove several stories at once by providing their IDs."""
    body: DeleteMultipleStoriesRequestBody

# Operation: create_story_from_template
class CreateStoryFromTemplateRequestBody(StrictModel):
    """Request parameters for creating a story from a story template. These parameters are merged with the values derived from the template."""
    description: str | None = Field(default=None, description="The story's description text. Limited to 100,000 characters.", max_length=100000)
    archived: bool | None = Field(default=None, description="Whether the story should be archived. Defaults to false if not specified.")
    story_links: list[CreateStoryLinkParams] | None = Field(default=None, description="An array of story links to attach to this story, establishing relationships with other stories.")
    external_links_add: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, description="An array of external links to add to the story in addition to any provided by the template. Cannot be combined with external_links_remove.")
    story_type: Literal["feature", "chore", "bug"] | None = Field(default=None, description="The story's type classification. Must be one of: feature, chore, or bug.")
    name: str | None = Field(default=None, description="The story's title. Required if the template does not provide a name. Must be between 1 and 512 characters.", min_length=1, max_length=512)
    file_ids_add: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(default=None, description="An array of file IDs to attach to the story in addition to files from the template. Cannot be combined with file_ids_remove.")
    file_ids_remove: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(default=None, description="An array of file IDs to remove from the template's attached files. Cannot be combined with file_ids_add.")
    comments: list[CreateStoryCommentParams] | None = Field(default=None, description="An array of comment objects to add to the story upon creation.")
    follower_ids_add: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, description="An array of member UUIDs to add as followers in addition to followers from the template. Cannot be combined with follower_ids_remove.")
    story_template_id: str = Field(default=..., description="The UUID of the story template to use as the basis for this story. Required.", json_schema_extra={'format': 'uuid'})
    follower_ids_remove: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, description="An array of member UUIDs to remove from the template's followers. Cannot be combined with follower_ids_add.")
    sub_tasks: list[LinkSubTaskParams | CreateSubTaskParams] | None = Field(default=None, description="An array of sub-task definitions to associate with the story. Each entry can link to an existing story or create a new sub-task. Only applicable when the Sub-task feature is enabled.")
    linked_file_ids_remove: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(default=None, description="An array of linked file IDs to remove from the template's linked files. Cannot be combined with linked_file_ids_add.")
    requested_by_id: str | None = Field(default=None, description="The UUID of the workspace member who requested this story.", json_schema_extra={'format': 'uuid'})
    iteration_id: int | None = Field(default=None, description="The numeric ID of the iteration (sprint) this story belongs to.", json_schema_extra={'format': 'int64'})
    custom_fields_remove: Annotated[list[RemoveCustomFieldParams], AfterValidator(_check_unique_items)] | None = Field(default=None, description="An array of custom field IDs to remove from the template's custom field values. Cannot be combined with custom_fields_add.")
    tasks: list[CreateTaskParams] | None = Field(default=None, description="An array of task objects to create and associate with the story.")
    labels_add: Annotated[list[CreateLabelParams], AfterValidator(_check_unique_items)] | None = Field(default=None, description="An array of label names or IDs to add to the story in addition to labels from the template. Cannot be combined with labels_remove.")
    workflow_state_id: int | None = Field(default=None, description="The numeric ID of the workflow state this story should be placed in.", json_schema_extra={'format': 'int64'})
    external_id: str | None = Field(default=None, description="An external identifier for this story, useful when importing from other tools. Limited to 1,024 characters.", max_length=1024)
    parent_story_id: int | None = Field(default=None, description="The numeric ID of the parent story, making this story a sub-task. Only applicable when the Sub-task feature is enabled.", json_schema_extra={'format': 'int64'})
    estimate: int | None = Field(default=None, description="The numeric point estimate for story complexity. Can be null to leave unestimated.", json_schema_extra={'format': 'int64'})
    owner_ids_remove: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, description="An array of member UUIDs to remove from the template's owners. Cannot be combined with owner_ids_add.")
    custom_fields_add: Annotated[list[CustomFieldValueParams], AfterValidator(_check_unique_items)] | None = Field(default=None, description="An array of custom field assignments, each specifying a custom field ID and its enum value. These are added to template values. Cannot be combined with custom_fields_remove.")
    linked_file_ids_add: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(default=None, description="An array of linked file IDs to attach to the story in addition to files from the template. Cannot be combined with linked_file_ids_remove.")
    labels_remove: Annotated[list[RemoveLabelParams], AfterValidator(_check_unique_items)] | None = Field(default=None, description="An array of label names or IDs to remove from the template's labels. Cannot be combined with labels_add.")
    deadline: str | None = Field(default=None, description="The story's due date in ISO 8601 format (e.g., 2024-12-31T23:59:59Z).", json_schema_extra={'format': 'date-time'})
    owner_ids_add: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, description="An array of member UUIDs to add as owners in addition to owners from the template. Cannot be combined with owner_ids_remove.")
    external_links_remove: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, description="An array of external links to remove from the template's external links. Cannot be combined with external_links_add.")
class CreateStoryFromTemplateRequest(StrictModel):
    """Create a new story in your Shortcut workspace based on a story template, with the ability to customize or override template values for all story attributes."""
    body: CreateStoryFromTemplateRequestBody

# Operation: search_stories_advanced
class QueryStoriesRequestBody(StrictModel):
    archived: bool | None = Field(default=None, description="Filter to include or exclude archived Stories.")
    story_type: Literal["feature", "chore", "bug"] | None = Field(default=None, description="Filter Stories by type: feature, chore, or bug.")
    epic_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(default=None, description="Filter Stories associated with one or more Epics by their IDs.")
    project_ids: Annotated[list[int | None], AfterValidator(_check_unique_items)] | None = Field(default=None, description="Filter Stories assigned to one or more Projects by their IDs.")
    updated_at_end: str | None = Field(default=None, description="Filter Stories updated on or before this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    completed_at_end: str | None = Field(default=None, description="Filter Stories completed on or before this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    workflow_state_types: list[Literal["started", "backlog", "unstarted", "done"]] | None = Field(default=None, description="Filter Stories by Workflow State type (e.g., started, completed, unstarted).")
    deadline_end: str | None = Field(default=None, description="Filter Stories with a deadline on or before this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    created_at_start: str | None = Field(default=None, description="Filter Stories created on or after this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    label_name: str | None = Field(default=None, description="Filter Stories by associated Label name (minimum 1 character).", min_length=1)
    requested_by_id: str | None = Field(default=None, description="Filter Stories requested by a specific User (UUID format).", json_schema_extra={'format': 'uuid'})
    iteration_id: int | None = Field(default=None, description="Filter Stories associated with a specific Iteration by its ID.", json_schema_extra={'format': 'int64'})
    label_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(default=None, description="Filter Stories associated with one or more Labels by their IDs.")
    workflow_state_id: int | None = Field(default=None, description="Filter Stories in a specific Workflow State by its unique ID.", json_schema_extra={'format': 'int64'})
    iteration_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(default=None, description="Filter Stories associated with one or more Iterations by their IDs.")
    created_at_end: str | None = Field(default=None, description="Filter Stories created on or before this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    deadline_start: str | None = Field(default=None, description="Filter Stories with a deadline on or after this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    group_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(default=None, description="Filter Stories associated with one or more Groups by their IDs.")
    external_id: str | None = Field(default=None, description="Filter Stories by external resource reference ID or URL (up to 1024 characters), useful for tracking imported items.", max_length=1024)
    includes_description: bool | None = Field(default=None, description="Include the full story description text in the response when true.")
    estimate: int | None = Field(default=None, description="Filter Stories by estimate points (whole number).", json_schema_extra={'format': 'int64'})
    completed_at_start: str | None = Field(default=None, description="Filter Stories completed on or after this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    updated_at_start: str | None = Field(default=None, description="Filter Stories updated on or after this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
class QueryStoriesRequest(StrictModel):
    """Search and filter Stories across projects using flexible criteria including type, status, dates, assignments, and metadata. Returns matching Stories with optional description content."""
    body: QueryStoriesRequestBody | None = None

# Operation: get_story
class GetStoryRequestPath(StrictModel):
    story_public_id: int = Field(default=..., validation_alias="story-public-id", serialization_alias="story-public-id", description="The unique public identifier for the story. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetStoryRequest(StrictModel):
    """Retrieve detailed information about a specific story by its public ID. Returns the story's metadata and content."""
    path: GetStoryRequestPath

# Operation: update_story
class UpdateStoryRequestPath(StrictModel):
    story_public_id: int = Field(default=..., validation_alias="story-public-id", serialization_alias="story-public-id", description="The unique identifier of the story to update. This is a 64-bit integer that uniquely identifies the story within the system.", json_schema_extra={'format': 'int64'})
class UpdateStoryRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A detailed description of the story, up to 100,000 characters in length.", max_length=100000)
    archived: bool | None = Field(default=None, description="Whether the story is archived. Set to true to archive the story or false to unarchive it.")
    pull_request_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(default=None, description="An array of pull or merge request IDs to attach to this story. The order and specific format depend on your version control system integration.")
    story_type: Literal["feature", "chore", "bug"] | None = Field(default=None, description="The category of work this story represents: 'feature' for new functionality, 'bug' for defects, or 'chore' for maintenance tasks.")
    name: str | None = Field(default=None, description="The title of the story, between 1 and 512 characters in length.", min_length=1, max_length=512)
    branch_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(default=None, description="An array of branch IDs to attach to this story. The order and specific format depend on your version control system integration.")
    commit_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(default=None, description="An array of commit IDs to attach to this story. The order and specific format depend on your version control system integration.")
    sub_tasks: list[LinkSubTaskParams] | None = Field(default=None, description="An array of story IDs to set as sub-tasks of this story. This represents the complete final state—stories not in this list will be unlinked, new stories will be linked, and the array order determines sub-task positions.")
    requested_by_id: str | None = Field(default=None, description="The UUID of the team member who requested this story.", json_schema_extra={'format': 'uuid'})
    iteration_id: int | None = Field(default=None, description="The 64-bit integer ID of the iteration (sprint or planning cycle) this story belongs to.", json_schema_extra={'format': 'int64'})
    workflow_state_id: int | None = Field(default=None, description="The 64-bit integer ID of the workflow state to move this story into (e.g., 'To Do', 'In Progress', 'Done').", json_schema_extra={'format': 'int64'})
    parent_story_id: int | None = Field(default=None, description="The 64-bit integer ID of the parent story, making this story a sub-task. Set to null to remove the parent relationship and make this story independent.", json_schema_extra={'format': 'int64'})
    estimate: int | None = Field(default=None, description="The point estimate for this story as a 64-bit integer, or null to mark the story as unestimated.", json_schema_extra={'format': 'int64'})
    deadline: str | None = Field(default=None, description="The due date for this story in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
class UpdateStoryRequest(StrictModel):
    """Update one or more properties of an existing story, including its metadata, relationships, and workflow state. Changes are applied immediately and replace the current values for any fields provided."""
    path: UpdateStoryRequestPath
    body: UpdateStoryRequestBody | None = None

# Operation: delete_story
class DeleteStoryRequestPath(StrictModel):
    story_public_id: int = Field(default=..., validation_alias="story-public-id", serialization_alias="story-public-id", description="The unique public identifier of the story to delete. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class DeleteStoryRequest(StrictModel):
    """Permanently delete a story by its public ID. This action cannot be undone."""
    path: DeleteStoryRequestPath

# Operation: list_story_comments
class ListStoryCommentRequestPath(StrictModel):
    story_public_id: int = Field(default=..., validation_alias="story-public-id", serialization_alias="story-public-id", description="The unique identifier of the story. Must be a positive integer value.", json_schema_extra={'format': 'int64'})
class ListStoryCommentRequest(StrictModel):
    """Retrieves all comments associated with a specific story. Use this to fetch the complete list of comments for a given story."""
    path: ListStoryCommentRequestPath

# Operation: create_story_comment
class CreateStoryCommentRequestPath(StrictModel):
    story_public_id: int = Field(default=..., validation_alias="story-public-id", serialization_alias="story-public-id", description="The unique identifier of the story where the comment will be posted. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class CreateStoryCommentRequestBody(StrictModel):
    text: str = Field(default=..., description="The comment text content. Supports up to 100,000 characters.", max_length=100000)
    author_id: str | None = Field(default=None, description="The UUID of the team member authoring the comment. If not provided, defaults to the user associated with the API token.", json_schema_extra={'format': 'uuid'})
    external_id: str | None = Field(default=None, description="An external identifier for the comment, useful when migrating comments from other tools. Maximum length is 1,024 characters.", max_length=1024)
    parent_id: int | None = Field(default=None, description="The ID of the parent comment to thread this comment under as a reply. If omitted, the comment will be a top-level comment on the story.", json_schema_extra={'format': 'int64'})
class CreateStoryCommentRequest(StrictModel):
    """Add a comment to a story. Comments can be standalone or threaded as replies to existing comments."""
    path: CreateStoryCommentRequestPath
    body: CreateStoryCommentRequestBody

# Operation: get_story_comment
class GetStoryCommentRequestPath(StrictModel):
    story_public_id: int = Field(default=..., validation_alias="story-public-id", serialization_alias="story-public-id", description="The unique identifier of the story containing the comment. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    comment_public_id: int = Field(default=..., validation_alias="comment-public-id", serialization_alias="comment-public-id", description="The unique identifier of the comment to retrieve. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class GetStoryCommentRequest(StrictModel):
    """Retrieve detailed information about a specific comment within a story. Use this to fetch comment data by providing both the story and comment identifiers."""
    path: GetStoryCommentRequestPath

# Operation: update_story_comment
class UpdateStoryCommentRequestPath(StrictModel):
    story_public_id: int = Field(default=..., validation_alias="story-public-id", serialization_alias="story-public-id", description="The unique identifier of the story containing the comment to update.", json_schema_extra={'format': 'int64'})
    comment_public_id: int = Field(default=..., validation_alias="comment-public-id", serialization_alias="comment-public-id", description="The unique identifier of the comment to update.", json_schema_extra={'format': 'int64'})
class UpdateStoryCommentRequestBody(StrictModel):
    text: str = Field(default=..., description="The new comment text content, up to 100,000 characters in length.", max_length=100000)
class UpdateStoryCommentRequest(StrictModel):
    """Update the text content of an existing comment within a story. The comment text can be up to 100,000 characters."""
    path: UpdateStoryCommentRequestPath
    body: UpdateStoryCommentRequestBody

# Operation: delete_story_comment
class DeleteStoryCommentRequestPath(StrictModel):
    story_public_id: int = Field(default=..., validation_alias="story-public-id", serialization_alias="story-public-id", description="The unique identifier of the story containing the comment to delete. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    comment_public_id: int = Field(default=..., validation_alias="comment-public-id", serialization_alias="comment-public-id", description="The unique identifier of the comment to delete. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class DeleteStoryCommentRequest(StrictModel):
    """Remove a comment from a story. This permanently deletes the specified comment and cannot be undone."""
    path: DeleteStoryCommentRequestPath

# Operation: add_reaction_to_story_comment
class CreateStoryReactionRequestPath(StrictModel):
    story_public_id: int = Field(default=..., validation_alias="story-public-id", serialization_alias="story-public-id", description="The unique identifier of the story containing the comment. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    comment_public_id: int = Field(default=..., validation_alias="comment-public-id", serialization_alias="comment-public-id", description="The unique identifier of the comment to react to. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class CreateStoryReactionRequestBody(StrictModel):
    emoji: str = Field(default=..., description="The emoji short-code to add or remove as a reaction (e.g., `:thumbsup::skin-tone-4:`, `:heart:`, `:laughing:`). Use standard emoji short-code format with colons.")
class CreateStoryReactionRequest(StrictModel):
    """Add an emoji reaction to a comment on a story. Use emoji short-codes (e.g., `:thumbsup::skin-tone-4:`) to express reactions."""
    path: CreateStoryReactionRequestPath
    body: CreateStoryReactionRequestBody

# Operation: remove_reaction_from_story_comment
class DeleteStoryReactionRequestPath(StrictModel):
    story_public_id: int = Field(default=..., validation_alias="story-public-id", serialization_alias="story-public-id", description="The unique identifier of the story containing the comment. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    comment_public_id: int = Field(default=..., validation_alias="comment-public-id", serialization_alias="comment-public-id", description="The unique identifier of the comment from which to remove the reaction. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class DeleteStoryReactionRequestBody(StrictModel):
    emoji: str = Field(default=..., description="The emoji short-code to remove, formatted as a colon-delimited code (e.g., `:thumbsup:` or `:thumbsup::skin-tone-4:` for variants with modifiers).")
class DeleteStoryReactionRequest(StrictModel):
    """Remove a reaction (emoji) from a comment on a story. Specify the story, comment, and emoji to delete the reaction."""
    path: DeleteStoryReactionRequestPath
    body: DeleteStoryReactionRequestBody

# Operation: remove_comment_slack_link
class UnlinkCommentThreadFromSlackRequestPath(StrictModel):
    story_public_id: int = Field(default=..., validation_alias="story-public-id", serialization_alias="story-public-id", description="The unique identifier of the Story containing the comment to unlink. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    comment_public_id: int = Field(default=..., validation_alias="comment-public-id", serialization_alias="comment-public-id", description="The unique identifier of the Comment to unlink from Slack. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class UnlinkCommentThreadFromSlackRequest(StrictModel):
    """Unlinks a comment from its associated Slack thread, stopping synchronization of replies between the comment thread and Slack."""
    path: UnlinkCommentThreadFromSlackRequestPath

# Operation: get_story_history
class StoryHistoryRequestPath(StrictModel):
    story_public_id: int = Field(default=..., validation_alias="story-public-id", serialization_alias="story-public-id", description="The unique identifier of the story. Must be a valid 64-bit integer representing the story's public ID.", json_schema_extra={'format': 'int64'})
class StoryHistoryRequest(StrictModel):
    """Retrieve the complete history of changes for a specific story, including all revisions and modifications over time."""
    path: StoryHistoryRequestPath

# Operation: list_story_sub_tasks
class ListStorySubTasksRequestPath(StrictModel):
    story_public_id: int = Field(default=..., validation_alias="story-public-id", serialization_alias="story-public-id", description="The unique identifier of the parent story. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class ListStorySubTasksRequest(StrictModel):
    """Retrieve all sub-task stories associated with a parent story. Returns a complete list of child tasks for the specified story."""
    path: ListStorySubTasksRequestPath

# Operation: create_task_in_story
class CreateTaskRequestPath(StrictModel):
    story_public_id: int = Field(default=..., validation_alias="story-public-id", serialization_alias="story-public-id", description="The unique identifier of the Story where the task will be created. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class CreateTaskRequestBody(StrictModel):
    description: str = Field(default=..., description="A text description of the task. Must be between 1 and 2048 characters.", min_length=1, max_length=2048)
    complete: bool | None = Field(default=None, description="Optional boolean flag to set the task's completion status. Defaults to false (incomplete) if not provided.")
    external_id: str | None = Field(default=None, description="Optional identifier for linking this task to an external system or tool. Useful when importing tasks from other platforms. Maximum length is 128 characters.", max_length=128)
class CreateTaskRequest(StrictModel):
    """Create a new task within a Story. Tasks are actionable items that can be marked complete and optionally linked to external systems via an external ID."""
    path: CreateTaskRequestPath
    body: CreateTaskRequestBody

# Operation: get_task
class GetTaskRequestPath(StrictModel):
    story_public_id: int = Field(default=..., validation_alias="story-public-id", serialization_alias="story-public-id", description="The unique identifier of the Story that contains the Task. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    task_public_id: int = Field(default=..., validation_alias="task-public-id", serialization_alias="task-public-id", description="The unique identifier of the Task to retrieve. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class GetTaskRequest(StrictModel):
    """Retrieve detailed information about a specific Task within a Story. Returns the Task's properties and metadata."""
    path: GetTaskRequestPath

# Operation: update_task
class UpdateTaskRequestPath(StrictModel):
    story_public_id: int = Field(default=..., validation_alias="story-public-id", serialization_alias="story-public-id", description="The unique identifier of the parent story containing the task. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    task_public_id: int = Field(default=..., validation_alias="task-public-id", serialization_alias="task-public-id", description="The unique identifier of the task to update. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class UpdateTaskRequestBody(StrictModel):
    description: str | None = Field(default=None, description="The task's description text. Must be between 1 and 2048 characters long.", min_length=1, max_length=2048)
    complete: bool | None = Field(default=None, description="Whether the task is complete. Set to true to mark the task as done, or false to mark it as incomplete.")
class UpdateTaskRequest(StrictModel):
    """Update properties of a specific task within a story, such as its description or completion status."""
    path: UpdateTaskRequestPath
    body: UpdateTaskRequestBody | None = None

# Operation: delete_task
class DeleteTaskRequestPath(StrictModel):
    story_public_id: int = Field(default=..., validation_alias="story-public-id", serialization_alias="story-public-id", description="The unique identifier of the Story containing the Task to delete. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    task_public_id: int = Field(default=..., validation_alias="task-public-id", serialization_alias="task-public-id", description="The unique identifier of the Task to delete. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class DeleteTaskRequest(StrictModel):
    """Permanently delete a Task from a Story. This operation removes the Task and all associated data."""
    path: DeleteTaskRequestPath

# Operation: create_story_link
class CreateStoryLinkRequestBody(StrictModel):
    verb: Literal["blocks", "duplicates", "relates to"] = Field(default=..., description="The relationship type expressed as an active voice verb. Must be one of: 'blocks' (subject prevents object from progressing), 'duplicates' (subject and object represent identical work), or 'relates to' (subject has a general association with object).")
    subject_id: int = Field(default=..., description="The numeric ID of the story performing the action (the subject of the relationship).", json_schema_extra={'format': 'int64'})
    object_id: int = Field(default=..., description="The numeric ID of the story being acted upon (the object of the relationship).", json_schema_extra={'format': 'int64'})
class CreateStoryLinkRequest(StrictModel):
    """Create a semantic relationship between two stories by specifying how one story acts upon another. The subject story performs an action (blocks, duplicates, or relates to) on the object story, establishing a directional dependency or association."""
    body: CreateStoryLinkRequestBody

# Operation: get_story_link
class GetStoryLinkRequestPath(StrictModel):
    story_link_public_id: int = Field(default=..., validation_alias="story-link-public-id", serialization_alias="story-link-public-id", description="The unique identifier of the story link to retrieve. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class GetStoryLinkRequest(StrictModel):
    """Retrieves a specific story link and the stories it connects, along with their relationship details. Use this to understand how stories are related to each other."""
    path: GetStoryLinkRequestPath

# Operation: update_story_link
class UpdateStoryLinkRequestPath(StrictModel):
    story_link_public_id: int = Field(default=..., validation_alias="story-link-public-id", serialization_alias="story-link-public-id", description="The unique identifier of the story link to update. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class UpdateStoryLinkRequestBody(StrictModel):
    verb: Literal["blocks", "duplicates", "relates to"] | None = Field(default=None, description="The type of relationship between the stories. Choose from: blocks (one story blocks another), duplicates (stories are duplicates), or relates to (general relationship).")
    subject_id: int | None = Field(default=None, description="The ID of the subject story in the relationship. Must be a positive integer if provided.", json_schema_extra={'format': 'int64'})
    object_id: int | None = Field(default=None, description="The ID of the object story in the relationship. Must be a positive integer if provided.", json_schema_extra={'format': 'int64'})
class UpdateStoryLinkRequest(StrictModel):
    """Updates the relationship type and/or the connected stories for an existing story link. Modify how two stories are related or change which stories are linked together."""
    path: UpdateStoryLinkRequestPath
    body: UpdateStoryLinkRequestBody | None = None

# Operation: delete_story_link
class DeleteStoryLinkRequestPath(StrictModel):
    story_link_public_id: int = Field(default=..., validation_alias="story-link-public-id", serialization_alias="story-link-public-id", description="The unique identifier of the Story Link to delete. This is a 64-bit integer that uniquely identifies the relationship between stories.", json_schema_extra={'format': 'int64'})
class DeleteStoryLinkRequest(StrictModel):
    """Removes the relationship between two stories by deleting the specified Story Link. This operation severs the connection without affecting the individual stories themselves."""
    path: DeleteStoryLinkRequestPath

# Operation: get_workflow
class GetWorkflowRequestPath(StrictModel):
    workflow_public_id: int = Field(default=..., validation_alias="workflow-public-id", serialization_alias="workflow-public-id", description="The unique identifier of the workflow to retrieve, provided as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetWorkflowRequest(StrictModel):
    """Retrieve detailed information about a specific workflow by its public ID. Returns the workflow's configuration, status, and metadata."""
    path: GetWorkflowRequestPath

# ============================================================================
# Component Models
# ============================================================================

class Category(StrictModel):
    """A Category can be used to associate Objectives."""
    archived: bool = Field(..., description="A true/false boolean indicating if the Category has been archived.")
    entity_type: str = Field(..., description="A string description of this resource.")
    color: str | None = Field(..., description="The hex color to be displayed with the Category (for example, \"#ff0000\").", min_length=1, pattern="^#[a-fA-F0-9]{6}$", json_schema_extra={'format': 'css-color'})
    name: str = Field(..., description="The name of the Category.")
    global_id: str = Field(..., description="The Global ID of the Category.")
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="The type of entity this Category is associated with; currently Milestone or Objective is the only type of Category.")
    updated_at: str = Field(..., description="The time/date that the Category was updated.", json_schema_extra={'format': 'date-time'})
    external_id: str | None = Field(..., description="This field can be set to another unique ID. In the case that the Category has been imported from another tool, the ID in the other tool can be indicated here.")
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID of the Category.", json_schema_extra={'format': 'int64'})
    created_at: str = Field(..., description="The time/date that the Category was created.", json_schema_extra={'format': 'date-time'})

class CreateCategoryParams(StrictModel):
    """Request parameters for creating a Category with a Objective."""
    name: str = Field(..., description="The name of the new Category.", min_length=1, max_length=128)
    color: str | None = Field(None, description="The hex color to be displayed with the Category (for example, \"#ff0000\").", min_length=1, pattern="^#[a-fA-F0-9]{6}$", json_schema_extra={'format': 'css-color'})
    external_id: str | None = Field(None, description="This field can be set to another unique ID. In the case that the Category has been imported from another tool, the ID in the other tool can be indicated here.", min_length=1, max_length=128)

class CreateLabelParams(StrictModel):
    """Request parameters for creating a Label on a Shortcut Story."""
    name: str = Field(..., description="The name of the new Label.", min_length=1, max_length=128)
    description: str | None = Field(None, description="The description of the new Label.", max_length=1024)
    color: str | None = Field(None, description="The hex color to be displayed with the Label (for example, \"#ff0000\").", min_length=1, pattern="^#[a-fA-F0-9]{6}$", json_schema_extra={'format': 'css-color'})
    external_id: str | None = Field(None, description="This field can be set to another unique ID. In the case that the Label has been imported from another tool, the ID in the other tool can be indicated here.", min_length=1, max_length=128)

class CreateStoryCommentParams(StrictModel):
    """Request parameters for creating a Comment on a Shortcut Story."""
    text: str = Field(..., description="The comment text.", max_length=100000)
    author_id: str | None = Field(None, description="The Member ID of the Comment's author. Defaults to the user identified by the API token.", json_schema_extra={'format': 'uuid'})
    created_at: str | None = Field(None, description="Defaults to the time/date the comment is created, but can be set to reflect another date.", json_schema_extra={'format': 'date-time'})
    updated_at: str | None = Field(None, description="Defaults to the time/date the comment is last updated, but can be set to reflect another date.", json_schema_extra={'format': 'date-time'})
    external_id: str | None = Field(None, description="This field can be set to another unique ID. In the case that the comment has been imported from another tool, the ID in the other tool can be indicated here.", max_length=1024)
    parent_id: int | None = Field(None, description="The ID of the Comment that this comment is threaded under.", json_schema_extra={'format': 'int64'})

class CreateStoryLinkParams(StrictModel):
    """Request parameters for creating a Story Link within a Story."""
    subject_id: int | None = Field(None, description="The unique ID of the Story defined as subject.", json_schema_extra={'format': 'int64'})
    verb: Literal["blocks", "duplicates", "relates to"] = Field(..., description="How the subject Story acts on the object Story. This can be \"blocks\", \"duplicates\", or \"relates to\".")
    object_id: int | None = Field(None, description="The unique ID of the Story defined as object.", json_schema_extra={'format': 'int64'})

class CreateSubTaskParams(StrictModel):
    name: str = Field(..., description="The name of the SubTask.", min_length=1, max_length=512)
    owner_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of UUIDs of the owners of this story.")
    workflow_state_id: int | None = Field(None, description="The ID of the workflow state the story will be in.", json_schema_extra={'format': 'int64'})

class CreateTaskParams(StrictModel):
    """Request parameters for creating a Task on a Story."""
    description: str = Field(..., description="The Task description.", min_length=1, max_length=2048)
    complete: bool | None = Field(None, description="True/false boolean indicating whether the Task is completed. Defaults to false.")
    owner_ids: list[str] | None = Field(None, description="An array of UUIDs for any members you want to add as Owners on this new Task.")
    external_id: str | None = Field(None, description="This field can be set to another unique ID. In the case that the Task has been imported from another tool, the ID in the other tool can be indicated here.", max_length=128)
    created_at: str | None = Field(None, description="Defaults to the time/date the Task is created but can be set to reflect another creation time/date.", json_schema_extra={'format': 'date-time'})
    updated_at: str | None = Field(None, description="Defaults to the time/date the Task is created in Shortcut but can be set to reflect another time/date.", json_schema_extra={'format': 'date-time'})

class CustomFieldEnumValue(StrictModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The unique public ID for the Custom Field.", json_schema_extra={'format': 'uuid'})
    value: str = Field(..., description="A string value within the domain of this Custom Field.", min_length=1, max_length=63)
    position: int = Field(..., description="An integer indicating the position of this Value with respect to the other CustomFieldEnumValues in the enumeration.", json_schema_extra={'format': 'int64'})
    color_key: str | None = Field(..., description="A color key associated with this CustomFieldEnumValue.")
    entity_type: Literal["custom-field-enum-value"] = Field(..., description="A string description of this resource.")
    enabled: bool = Field(..., description="When true, the CustomFieldEnumValue can be selected for the CustomField.")

class CustomField(StrictModel):
    description: str | None = Field(None, description="A string description of the CustomField", min_length=1, max_length=512)
    icon_set_identifier: str | None = Field(None, description="A string that represents the icon that corresponds to this custom field.", min_length=1, max_length=63)
    entity_type: Literal["custom-field"] = Field(..., description="A string description of this resource.")
    story_types: list[str] | None = Field(None, description="The types of stories this CustomField is scoped to.")
    name: str = Field(..., description="The name of the Custom Field.", min_length=1, max_length=63)
    fixed_position: bool | None = Field(None, description="When true, the CustomFieldEnumValues may not be reordered.")
    updated_at: str = Field(..., description="The instant when this CustomField was last updated.", json_schema_extra={'format': 'date-time'})
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The unique public ID for the CustomField.", json_schema_extra={'format': 'uuid'})
    values: list[CustomFieldEnumValue] | None = Field(None, description="A collection of legal values for a CustomField.")
    field_type: Literal["enum"] = Field(..., description="The type of Custom Field, eg. 'enum'.")
    position: int = Field(..., description="An integer indicating the position of this Custom Field with respect to the other CustomField", json_schema_extra={'format': 'int64'})
    canonical_name: str | None = Field(None, description="The canonical name for a Shortcut-defined field.")
    enabled: bool = Field(..., description="When true, the CustomField can be applied to entities in the Workspace.")
    created_at: str = Field(..., description="The instant when this CustomField was created.", json_schema_extra={'format': 'date-time'})

class CustomFieldValueParams(StrictModel):
    field_id: str = Field(..., description="The unique public ID for the CustomField.", json_schema_extra={'format': 'uuid'})
    value_id: str = Field(..., description="The unique public ID for the CustomFieldEnumValue.", json_schema_extra={'format': 'uuid'})
    value: str | None = Field(None, description="A literal value for the CustomField. Currently ignored.")

class Doc(StrictModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The public id of the Doc", json_schema_extra={'format': 'uuid'})
    title: str | None = Field(..., description="The Doc's title")
    content_markdown: str | None = Field(..., description="The Doc's content in Markdown format (converted from HTML storage).")
    content_html: str | None = Field(None, description="The Doc's content in HTML format (as stored in S3). Only included when include_html=true query parameter is provided.")
    app_url: str = Field(..., description="The Shortcut application url for the Doc")
    created_at: str = Field(..., description="The time/date the Doc was created", json_schema_extra={'format': 'date-time'})
    updated_at: str = Field(..., description="The time/date the Doc was last updated", json_schema_extra={'format': 'date-time'})
    archived: bool = Field(..., description="Whether the Doc is archived")

class EpicAssociatedGroup(StrictModel):
    group_id: str = Field(..., description="The Group ID of the associated group.", json_schema_extra={'format': 'uuid'})
    associated_stories_count: int | None = Field(None, description="The number of stories this Group owns in the Epic.", json_schema_extra={'format': 'int64'})

class EpicStats(StrictModel):
    """A group of calculated values for this Epic."""
    num_points_done: int = Field(..., description="The total number of completed points in this Epic.", json_schema_extra={'format': 'int64'})
    num_related_documents: int = Field(..., description="The total number of documents associated with this Epic.", json_schema_extra={'format': 'int64'})
    num_stories_unstarted: int = Field(..., description="The total number of unstarted Stories in this Epic.", json_schema_extra={'format': 'int64'})
    num_stories_total: int = Field(..., description="The total number of Stories in this Epic.", json_schema_extra={'format': 'int64'})
    last_story_update: str | None = Field(..., description="The date of the last update of a Story in this Epic.", json_schema_extra={'format': 'date-time'})
    num_points_started: int = Field(..., description="The total number of started points in this Epic.", json_schema_extra={'format': 'int64'})
    num_points_unstarted: int = Field(..., description="The total number of unstarted points in this Epic.", json_schema_extra={'format': 'int64'})
    num_stories_started: int = Field(..., description="The total number of started Stories in this Epic.", json_schema_extra={'format': 'int64'})
    num_stories_unestimated: int = Field(..., description="The total number of Stories with no point estimate.", json_schema_extra={'format': 'int64'})
    num_stories_backlog: int = Field(..., description="The total number of backlog Stories in this Epic.", json_schema_extra={'format': 'int64'})
    num_points_backlog: int = Field(..., description="The total number of backlog points in this Epic.", json_schema_extra={'format': 'int64'})
    num_points: int = Field(..., description="The total number of points in this Epic.", json_schema_extra={'format': 'int64'})
    num_stories_done: int = Field(..., description="The total number of done Stories in this Epic.", json_schema_extra={'format': 'int64'})

class Icon(StrictModel):
    """Icons are used to attach images to Groups, Workspaces, Members, and Loading screens in the Shortcut web application."""
    entity_type: str = Field(..., description="A string description of this resource.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID of the Icon.", json_schema_extra={'format': 'uuid'})
    created_at: str = Field(..., description="The time/date that the Icon was created.", json_schema_extra={'format': 'date-time'})
    updated_at: str = Field(..., description="The time/date that the Icon was updated.", json_schema_extra={'format': 'date-time'})
    url: str = Field(..., description="The URL of the Icon.")

class Group(StrictModel):
    """A Group."""
    app_url: str = Field(..., description="The Shortcut application url for the Group.")
    description: str = Field(..., description="The description of the Group.")
    archived: bool = Field(..., description="Whether or not the Group is archived.")
    entity_type: str = Field(..., description="A string description of this resource.")
    color: str | None = Field(..., description="The hex color to be displayed with the Group (for example, \"#ff0000\").", min_length=1, pattern="^#[a-fA-F0-9]{6}$", json_schema_extra={'format': 'css-color'})
    num_stories_started: int = Field(..., description="The number of stories assigned to the group which are in a started workflow state.", json_schema_extra={'format': 'int64'})
    mention_name: str = Field(..., description="The mention name of the Group.", min_length=1, pattern="^[a-z0-9\\-\\_\\.]+$")
    name: str = Field(..., description="The name of the Group.")
    global_id: str
    color_key: Literal["blue", "purple", "midnight-blue", "orange", "yellow-green", "brass", "gray", "fuchsia", "yellow", "pink", "sky-blue", "green", "red", "black", "slate", "turquoise"] | None = Field(..., description="The color key to be displayed with the Group.")
    num_stories: int = Field(..., description="The total number of stories assigned to the group.", json_schema_extra={'format': 'int64'})
    num_epics_started: int = Field(..., description="The number of epics assigned to the group which are in the started workflow state.", json_schema_extra={'format': 'int64'})
    updated_at: str = Field(..., description="The last instant when this group was updated.", json_schema_extra={'format': 'date-time'})
    num_stories_backlog: int = Field(..., description="The number of stories assigned to the group which are in a backlog workflow state.", json_schema_extra={'format': 'int64'})
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The id of the Group.", json_schema_extra={'format': 'uuid'})
    display_icon: Icon
    default_workflow_id: int | None = Field(None, description="The ID of the default workflow for stories created in this group.", json_schema_extra={'format': 'int64'})
    member_ids: list[str] = Field(..., description="The Member IDs contain within the Group.")
    workflow_ids: list[int] = Field(..., description="The Workflow IDs contained within the Group.")
    created_at: str = Field(..., description="The instant when this group was created.", json_schema_extra={'format': 'date-time'})

class Identity(StrictModel):
    """The Identity of the VCS user that authored the Commit."""
    entity_type: str = Field(..., description="A string description of this resource.")
    name: str | None = Field(..., description="This is your login in VCS.")
    type_: Literal["slack", "github", "gitlab", "bitbucket"] | None = Field(..., validation_alias="type", serialization_alias="type", description="The service this Identity is for.")

class Commit(StrictModel):
    """Commit refers to a VCS commit and all associated details."""
    entity_type: str = Field(..., description="A string description of this resource.")
    author_id: str | None = Field(..., description="The ID of the Member that authored the Commit, if known.", json_schema_extra={'format': 'uuid'})
    hash_: str = Field(..., validation_alias="hash", serialization_alias="hash", description="The Commit hash.")
    updated_at: str | None = Field(..., description="The time/date the Commit was updated.", json_schema_extra={'format': 'date-time'})
    id_: int | None = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID of the Commit.", json_schema_extra={'format': 'int64'})
    url: str = Field(..., description="The URL of the Commit.")
    author_email: str = Field(..., description="The email address of the VCS user that authored the Commit.")
    timestamp: str = Field(..., description="The time/date the Commit was pushed.", json_schema_extra={'format': 'date-time'})
    author_identity: Identity
    repository_id: int | None = Field(..., description="The ID of the Repository that contains the Commit.", json_schema_extra={'format': 'int64'})
    created_at: str = Field(..., description="The time/date the Commit was created.", json_schema_extra={'format': 'date-time'})
    message: str = Field(..., description="The Commit message.")

class IterationAssociatedGroup(StrictModel):
    group_id: str = Field(..., description="The Group ID of the associated group.", json_schema_extra={'format': 'uuid'})
    associated_stories_count: int | None = Field(None, description="The number of stories this Group owns in the Iteration.", json_schema_extra={'format': 'int64'})

class IterationStats(StrictModel):
    """A group of calculated values for this Iteration."""
    num_points_done: int = Field(..., description="The total number of completed points in this Iteration.", json_schema_extra={'format': 'int64'})
    num_related_documents: int = Field(..., description="The total number of documents related to an Iteration", json_schema_extra={'format': 'int64'})
    average_cycle_time: int | None = Field(None, description="The average cycle time (in seconds) of completed stories in this Iteration.", json_schema_extra={'format': 'int64'})
    num_stories_unstarted: int = Field(..., description="The total number of unstarted Stories in this Iteration.", json_schema_extra={'format': 'int64'})
    num_points_started: int = Field(..., description="The total number of started points in this Iteration.", json_schema_extra={'format': 'int64'})
    num_points_unstarted: int = Field(..., description="The total number of unstarted points in this Iteration.", json_schema_extra={'format': 'int64'})
    num_stories_started: int = Field(..., description="The total number of started Stories in this Iteration.", json_schema_extra={'format': 'int64'})
    num_stories_unestimated: int = Field(..., description="The total number of Stories with no point estimate.", json_schema_extra={'format': 'int64'})
    num_stories_backlog: int = Field(..., description="The total number of backlog Stories in this Iteration.", json_schema_extra={'format': 'int64'})
    average_lead_time: int | None = Field(None, description="The average lead time (in seconds) of completed stories in this Iteration.", json_schema_extra={'format': 'int64'})
    num_points_backlog: int = Field(..., description="The total number of backlog points in this Iteration.", json_schema_extra={'format': 'int64'})
    num_points: int = Field(..., description="The total number of points in this Iteration.", json_schema_extra={'format': 'int64'})
    num_stories_done: int = Field(..., description="The total number of done Stories in this Iteration.", json_schema_extra={'format': 'int64'})

class LabelSlim(StrictModel):
    """A Label can be used to associate and filter Stories and Epics, and also create new Workspaces. A slim Label does not include aggregate stats. Fetch the Label using the labels endpoint to retrieve them."""
    app_url: str = Field(..., description="The Shortcut application url for the Label.")
    description: str | None = Field(..., description="The description of the Label.")
    archived: bool = Field(..., description="A true/false boolean indicating if the Label has been archived.")
    entity_type: str = Field(..., description="A string description of this resource.")
    color: str | None = Field(..., description="The hex color to be displayed with the Label (for example, \"#ff0000\").", min_length=1, pattern="^#[a-fA-F0-9]{6}$", json_schema_extra={'format': 'css-color'})
    name: str = Field(..., description="The name of the Label.")
    global_id: str
    updated_at: str | None = Field(..., description="The time/date that the Label was updated.", json_schema_extra={'format': 'date-time'})
    external_id: str | None = Field(..., description="This field can be set to another unique ID. In the case that the Label has been imported from another tool, the ID in the other tool can be indicated here.")
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID of the Label.", json_schema_extra={'format': 'int64'})
    created_at: str | None = Field(..., description="The time/date that the Label was created.", json_schema_extra={'format': 'date-time'})

class LabelStats(StrictModel):
    """A group of calculated values for this Label. This is not included if the slim? flag is set to true for the List Labels endpoint."""
    num_related_documents: int = Field(..., description="The total number of Documents associated this Label.", json_schema_extra={'format': 'int64'})
    num_epics: int = Field(..., description="The total number of Epics with this Label.", json_schema_extra={'format': 'int64'})
    num_stories_unstarted: int = Field(..., description="The total number of stories unstarted Stories with this Label.", json_schema_extra={'format': 'int64'})
    num_stories_total: int = Field(..., description="The total number of Stories with this Label.", json_schema_extra={'format': 'int64'})
    num_epics_unstarted: int = Field(..., description="The number of unstarted epics associated with this label.", json_schema_extra={'format': 'int64'})
    num_epics_in_progress: int = Field(..., description="The number of in progress epics associated with this label.", json_schema_extra={'format': 'int64'})
    num_points_unstarted: int = Field(..., description="The total number of unstarted points with this Label.", json_schema_extra={'format': 'int64'})
    num_stories_unestimated: int = Field(..., description="The total number of Stories with no point estimate with this Label.", json_schema_extra={'format': 'int64'})
    num_points_in_progress: int = Field(..., description="The total number of in-progress points with this Label.", json_schema_extra={'format': 'int64'})
    num_epics_total: int = Field(..., description="The total number of Epics associated with this Label.", json_schema_extra={'format': 'int64'})
    num_stories_completed: int = Field(..., description="The total number of completed Stories with this Label.", json_schema_extra={'format': 'int64'})
    num_points_completed: int = Field(..., description="The total number of completed points with this Label.", json_schema_extra={'format': 'int64'})
    num_stories_backlog: int = Field(..., description="The total number of stories backlog Stories with this Label.", json_schema_extra={'format': 'int64'})
    num_points_total: int = Field(..., description="The total number of points with this Label.", json_schema_extra={'format': 'int64'})
    num_stories_in_progress: int = Field(..., description="The total number of in-progress Stories with this Label.", json_schema_extra={'format': 'int64'})
    num_points_backlog: int = Field(..., description="The total number of backlog points with this Label.", json_schema_extra={'format': 'int64'})
    num_epics_completed: int = Field(..., description="The number of completed Epics associated with this Label.", json_schema_extra={'format': 'int64'})

class Label(StrictModel):
    """A Label can be used to associate and filter Stories and Epics, and also create new Workspaces."""
    app_url: str = Field(..., description="The Shortcut application url for the Label.")
    description: str | None = Field(..., description="The description of the Label.")
    archived: bool = Field(..., description="A true/false boolean indicating if the Label has been archived.")
    entity_type: str = Field(..., description="A string description of this resource.")
    color: str | None = Field(..., description="The hex color to be displayed with the Label (for example, \"#ff0000\").", min_length=1, pattern="^#[a-fA-F0-9]{6}$", json_schema_extra={'format': 'css-color'})
    name: str = Field(..., description="The name of the Label.")
    global_id: str
    updated_at: str | None = Field(..., description="The time/date that the Label was updated.", json_schema_extra={'format': 'date-time'})
    external_id: str | None = Field(..., description="This field can be set to another unique ID. In the case that the Label has been imported from another tool, the ID in the other tool can be indicated here.")
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID of the Label.", json_schema_extra={'format': 'int64'})
    stats: LabelStats | None = None
    created_at: str | None = Field(..., description="The time/date that the Label was created.", json_schema_extra={'format': 'date-time'})

class Iteration(StrictModel):
    """An Iteration is a defined, time-boxed period of development for a collection of Stories. See https://help.shortcut.com/hc/en-us/articles/360028953452-Iterations-Overview for more information."""
    app_url: str = Field(..., description="The Shortcut application url for the Iteration.")
    description: str = Field(..., description="The description of the iteration.")
    entity_type: str = Field(..., description="A string description of this resource")
    labels: list[Label] = Field(..., description="An array of labels attached to the iteration.")
    mention_ids: list[str] = Field(..., description="`Deprecated:` use `member_mention_ids`.")
    member_mention_ids: list[str] = Field(..., description="An array of Member IDs that have been mentioned in the Story description.")
    associated_groups: list[IterationAssociatedGroup] = Field(..., description="An array containing Group IDs and Group-owned story counts for the Iteration's associated groups.")
    name: str = Field(..., description="The name of the iteration.")
    global_id: str
    label_ids: list[int] = Field(..., description="An array of label ids attached to the iteration.")
    updated_at: str = Field(..., description="The instant when this iteration was last updated.", json_schema_extra={'format': 'date-time'})
    group_mention_ids: list[str] = Field(..., description="An array of Group IDs that have been mentioned in the Story description.")
    end_date: str = Field(..., description="The date this iteration ends.", json_schema_extra={'format': 'date-time'})
    follower_ids: list[str] = Field(..., description="An array of UUIDs for any Members listed as Followers.")
    group_ids: list[str] = Field(..., description="An array of UUIDs for any Groups you want to add as Followers. Currently, only one Group association is presented in our web UI.")
    start_date: str = Field(..., description="The date this iteration begins.", json_schema_extra={'format': 'date-time'})
    status: str = Field(..., description="The status of the iteration. Values are either \"unstarted\", \"started\", or \"done\".")
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the iteration.", json_schema_extra={'format': 'int64'})
    stats: IterationStats
    created_at: str = Field(..., description="The instant when this iteration was created.", json_schema_extra={'format': 'date-time'})

class LinkSubTaskParams(StrictModel):
    story_id: int = Field(..., description="The ID of the story to link as a sub-task of the parent story", json_schema_extra={'format': 'int64'})

class CreateStoryParams(StrictModel):
    """Request parameters for creating a story."""
    description: str | None = Field(None, description="The description of the story.", max_length=100000)
    archived: bool | None = Field(None, description="Controls the story's archived state.")
    story_links: list[CreateStoryLinkParams] | None = Field(None, description="An array of story links attached to the story.")
    labels: list[CreateLabelParams] | None = Field(None, description="An array of labels attached to the story.")
    story_type: Literal["feature", "chore", "bug"] | None = Field(None, description="The type of story (feature, bug, chore).")
    custom_fields: list[CustomFieldValueParams] | None = Field(None, description="A map specifying a CustomField ID and CustomFieldEnumValue ID that represents an assertion of some value for a CustomField.")
    move_to: Literal["last", "first"] | None = Field(None, description="One of \"first\" or \"last\". This can be used to move the given story to the first or last position in the workflow state.")
    file_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of IDs of files attached to the story.")
    source_task_id: int | None = Field(None, description="Given this story was converted from a task in another story, this is the original task ID that was converted to this story.", json_schema_extra={'format': 'int64'})
    completed_at_override: str | None = Field(None, description="A manual override for the time/date the Story was completed.", json_schema_extra={'format': 'date-time'})
    name: str = Field(..., description="The name of the story.", min_length=1, max_length=512)
    comments: list[CreateStoryCommentParams] | None = Field(None, description="An array of comments to add to the story.")
    epic_id: int | None = Field(None, description="The ID of the epic the story belongs to.", json_schema_extra={'format': 'int64'})
    story_template_id: str | None = Field(None, description="The id of the story template used to create this story, if applicable. This is just an association; no content from the story template is inherited by the story simply by setting this field.", json_schema_extra={'format': 'uuid'})
    external_links: list[str] | None = Field(None, description="An array of External Links associated with this story.")
    sub_tasks: list[LinkSubTaskParams | CreateSubTaskParams] | None = Field(None, description="An array of maps specifying sub-tasks to be associated with the created story. Each map can either link to an existing story or create a new sub-task story to be linked to the created story.\nField only applicable when Sub-task feature is enabled.")
    requested_by_id: str | None = Field(None, description="The ID of the member that requested the story.", json_schema_extra={'format': 'uuid'})
    iteration_id: int | None = Field(None, description="The ID of the iteration the story belongs to.", json_schema_extra={'format': 'int64'})
    tasks: list[CreateTaskParams] | None = Field(None, description="An array of tasks connected to the story.")
    started_at_override: str | None = Field(None, description="A manual override for the time/date the Story was started.", json_schema_extra={'format': 'date-time'})
    group_id: str | None = Field(None, description="The id of the group to associate with this story.", json_schema_extra={'format': 'uuid'})
    workflow_state_id: int | None = Field(None, description="The ID of the workflow state the story will be in.", json_schema_extra={'format': 'int64'})
    updated_at: str | None = Field(None, description="The time/date the Story was updated.", json_schema_extra={'format': 'date-time'})
    follower_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of UUIDs of the followers of this story.")
    owner_ids: Annotated[list[str], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of UUIDs of the owners of this story.")
    external_id: str | None = Field(None, description="This field can be set to another unique ID. In the case that the Story has been imported from another tool, the ID in the other tool can be indicated here.", max_length=1024)
    parent_story_id: int | None = Field(None, description="The ID of the parent story to associate with this story (making the created story a sub-task).\nField only applicable when Sub-task feature is enabled.", json_schema_extra={'format': 'int64'})
    estimate: int | None = Field(None, description="The numeric point estimate of the story. Can also be null, which means unestimated.", json_schema_extra={'format': 'int64'})
    project_id: int | None = Field(None, description="The ID of the project the story belongs to.", json_schema_extra={'format': 'int64'})
    linked_file_ids: Annotated[list[int], AfterValidator(_check_unique_items)] | None = Field(None, description="An array of IDs of linked files attached to the story.")
    deadline: str | None = Field(None, description="The due date of the story.", json_schema_extra={'format': 'date-time'})
    created_at: str | None = Field(None, description="The time/date the Story was created.", json_schema_extra={'format': 'date-time'})

class LinkedFile(StrictModel):
    """Linked files are stored on a third-party website and linked to one or more Stories. Shortcut currently supports linking files from Google Drive, Dropbox, Box, and by URL."""
    description: str | None = Field(..., description="The description of the file.")
    entity_type: str = Field(..., description="A string description of this resource.")
    story_ids: list[int] = Field(..., description="The IDs of the stories this file is attached to.")
    mention_ids: list[str] = Field(..., description="`Deprecated:` use `member_mention_ids`.")
    member_mention_ids: list[str] = Field(..., description="The members that are mentioned in the description of the file.")
    name: str = Field(..., description="The name of the linked file.")
    thumbnail_url: str | None = Field(..., description="The URL of the file thumbnail, if the integration provided it.")
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="The integration type (e.g. google, dropbox, box).")
    size: int | None = Field(..., description="The filesize, if the integration provided it.", json_schema_extra={'format': 'int64'})
    uploader_id: str = Field(..., description="The UUID of the member that uploaded the file.", json_schema_extra={'format': 'uuid'})
    content_type: str | None = Field(..., description="The content type of the image (e.g. txt/plain).")
    updated_at: str = Field(..., description="The time/date the LinkedFile was updated.", json_schema_extra={'format': 'date-time'})
    group_mention_ids: list[str] = Field(..., description="The groups that are mentioned in the description of the file.")
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The unique identifier for the file.", json_schema_extra={'format': 'int64'})
    url: str = Field(..., description="The URL of the file.")
    created_at: str = Field(..., description="The time/date the LinkedFile was created.", json_schema_extra={'format': 'date-time'})

class MilestoneStats(StrictModel):
    """A group of calculated values for this Milestone."""
    average_cycle_time: int | None = Field(None, description="The average cycle time (in seconds) of completed stories in this Milestone.", json_schema_extra={'format': 'int64'})
    average_lead_time: int | None = Field(None, description="The average lead time (in seconds) of completed stories in this Milestone.", json_schema_extra={'format': 'int64'})
    num_related_documents: int = Field(..., description="The number of related documents to this Milestone.", json_schema_extra={'format': 'int64'})

class Milestone(StrictModel):
    """(Deprecated) A Milestone is a collection of Epics that represent a release or some other large initiative that you are working on. Milestones have become Objectives, so you should use Objective-related API resources instead of Milestone ones."""
    app_url: str = Field(..., description="The Shortcut application url for the Milestone.")
    description: str = Field(..., description="The Milestone's description.")
    archived: bool = Field(..., description="A boolean indicating whether the Milestone has been archived or not.")
    started: bool = Field(..., description="A true/false boolean indicating if the Milestone has been started.")
    entity_type: str = Field(..., description="A string description of this resource.")
    completed_at_override: str | None = Field(..., description="A manual override for the time/date the Milestone was completed.", json_schema_extra={'format': 'date-time'})
    started_at: str | None = Field(..., description="The time/date the Milestone was started.", json_schema_extra={'format': 'date-time'})
    completed_at: str | None = Field(..., description="The time/date the Milestone was completed.", json_schema_extra={'format': 'date-time'})
    name: str = Field(..., description="The name of the Milestone.")
    global_id: str
    completed: bool = Field(..., description="A true/false boolean indicating if the Milestone has been completed.")
    state: str = Field(..., description="The workflow state that the Milestone is in.")
    started_at_override: str | None = Field(..., description="A manual override for the time/date the Milestone was started.", json_schema_extra={'format': 'date-time'})
    updated_at: str = Field(..., description="The time/date the Milestone was updated.", json_schema_extra={'format': 'date-time'})
    categories: list[Category] = Field(..., description="An array of Categories attached to the Milestone.")
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID of the Milestone.", json_schema_extra={'format': 'int64'})
    key_result_ids: list[str] = Field(..., description="The IDs of the Key Results associated with the Objective.")
    position: int = Field(..., description="A number representing the position of the Milestone in relation to every other Milestone within the Workspace.", json_schema_extra={'format': 'int64'})
    stats: MilestoneStats
    created_at: str = Field(..., description="The time/date the Milestone was created.", json_schema_extra={'format': 'date-time'})

class ObjectiveStats(StrictModel):
    """A group of calculated values for this Objective."""
    average_cycle_time: int | None = Field(None, description="The average cycle time (in seconds) of completed stories in this Objective.", json_schema_extra={'format': 'int64'})
    average_lead_time: int | None = Field(None, description="The average lead time (in seconds) of completed stories in this Objective.", json_schema_extra={'format': 'int64'})
    num_related_documents: int = Field(..., description="The number of related documents to this Objective.", json_schema_extra={'format': 'int64'})

class Objective(StrictModel):
    """An Objective is a collection of Epics that represent a release or some other large initiative that you are working on."""
    app_url: str = Field(..., description="The Shortcut application url for the Objective.")
    description: str = Field(..., description="The Objective's description.")
    archived: bool = Field(..., description="A boolean indicating whether the Objective has been archived or not.")
    started: bool = Field(..., description="A true/false boolean indicating if the Objective has been started.")
    entity_type: str = Field(..., description="A string description of this resource.")
    completed_at_override: str | None = Field(..., description="A manual override for the time/date the Objective was completed.", json_schema_extra={'format': 'date-time'})
    started_at: str | None = Field(..., description="The time/date the Objective was started.", json_schema_extra={'format': 'date-time'})
    completed_at: str | None = Field(..., description="The time/date the Objective was completed.", json_schema_extra={'format': 'date-time'})
    name: str = Field(..., description="The name of the Objective.")
    global_id: str
    completed: bool = Field(..., description="A true/false boolean indicating if the Objectivehas been completed.")
    state: str = Field(..., description="The workflow state that the Objective is in.")
    started_at_override: str | None = Field(..., description="A manual override for the time/date the Objective was started.", json_schema_extra={'format': 'date-time'})
    updated_at: str = Field(..., description="The time/date the Objective was updated.", json_schema_extra={'format': 'date-time'})
    categories: list[Category] = Field(..., description="An array of Categories attached to the Objective.")
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID of the Objective.", json_schema_extra={'format': 'int64'})
    key_result_ids: list[str] = Field(..., description="The IDs of the Key Results associated with the Objective.")
    position: int = Field(..., description="A number representing the position of the Objective in relation to every other Objective within the Workspace.", json_schema_extra={'format': 'int64'})
    stats: ObjectiveStats
    created_at: str = Field(..., description="The time/date the Objective was created.", json_schema_extra={'format': 'date-time'})

class PullRequestLabel(StrictModel):
    """Corresponds to a VCS Label associated with a Pull Request."""
    entity_type: str = Field(..., description="A string description of this resource.")
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID of the VCS Label.", json_schema_extra={'format': 'int64'})
    color: str = Field(..., description="The color of the VCS label.", min_length=1, pattern="^#[a-fA-F0-9]{6}$", json_schema_extra={'format': 'css-color'})
    description: str | None = Field(None, description="The description of the VCS label.")
    name: str = Field(..., description="The name of the VCS label.")

class PullRequest(StrictModel):
    """Corresponds to a VCS Pull Request attached to a Shortcut story."""
    entity_type: str = Field(..., description="A string description of this resource.")
    closed: bool = Field(..., description="True/False boolean indicating whether the VCS pull request has been closed.")
    merged: bool = Field(..., description="True/False boolean indicating whether the VCS pull request has been merged.")
    num_added: int = Field(..., description="Number of lines added in the pull request, according to VCS.", json_schema_extra={'format': 'int64'})
    branch_id: int = Field(..., description="The ID of the branch for the particular pull request.", json_schema_extra={'format': 'int64'})
    overlapping_stories: list[int] | None = Field(None, description="An array of Story ids that have Pull Requests that change at least one of the same lines this Pull Request changes.")
    number: int = Field(..., description="The pull request's unique number ID in VCS.", json_schema_extra={'format': 'int64'})
    branch_name: str = Field(..., description="The name of the branch for the particular pull request.")
    target_branch_name: str = Field(..., description="The name of the target branch for the particular pull request.")
    num_commits: int | None = Field(..., description="The number of commits on the pull request.", json_schema_extra={'format': 'int64'})
    title: str = Field(..., description="The title of the pull request.")
    updated_at: str = Field(..., description="The time/date the pull request was created.", json_schema_extra={'format': 'date-time'})
    has_overlapping_stories: bool = Field(..., description="Boolean indicating that the Pull Request has Stories that have Pull Requests that change at least one of the same lines this Pull Request changes.")
    draft: bool = Field(..., description="True/False boolean indicating whether the VCS pull request is in the draft state.")
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID associated with the pull request in Shortcut.", json_schema_extra={'format': 'int64'})
    vcs_labels: list[PullRequestLabel] | None = Field(None, description="An array of PullRequestLabels attached to the PullRequest.")
    url: str = Field(..., description="The URL for the pull request.")
    num_removed: int = Field(..., description="Number of lines removed in the pull request, according to VCS.", json_schema_extra={'format': 'int64'})
    review_status: str | None = Field(None, description="The status of the review for the pull request.")
    num_modified: int | None = Field(..., description="Number of lines modified in the pull request, according to VCS.", json_schema_extra={'format': 'int64'})
    build_status: str | None = Field(None, description="The status of the Continuous Integration workflow for the pull request.")
    target_branch_id: int = Field(..., description="The ID of the target branch for the particular pull request.", json_schema_extra={'format': 'int64'})
    repository_id: int = Field(..., description="The ID of the repository for the particular pull request.", json_schema_extra={'format': 'int64'})
    created_at: str = Field(..., description="The time/date the pull request was created.", json_schema_extra={'format': 'date-time'})

class Branch(StrictModel):
    """Branch refers to a VCS branch. Branches are feature branches associated with Shortcut Stories."""
    entity_type: str = Field(..., description="A string description of this resource.")
    deleted: bool = Field(..., description="A true/false boolean indicating if the Branch has been deleted.")
    name: str = Field(..., description="The name of the Branch.")
    persistent: bool = Field(..., description="This field is deprecated, and will always be false.")
    updated_at: str | None = Field(..., description="The time/date the Branch was updated.", json_schema_extra={'format': 'date-time'})
    pull_requests: list[PullRequest] = Field(..., description="An array of PullRequests attached to the Branch (there is usually only one).")
    merged_branch_ids: list[int] = Field(..., description="The IDs of the Branches the Branch has been merged into.")
    id_: int | None = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID of the Branch.", json_schema_extra={'format': 'int64'})
    url: str = Field(..., description="The URL of the Branch.")
    repository_id: int = Field(..., description="The ID of the Repository that contains the Branch.", json_schema_extra={'format': 'int64'})
    created_at: str | None = Field(..., description="The time/date the Branch was created.", json_schema_extra={'format': 'date-time'})

class RemoveCustomFieldParams(StrictModel):
    field_id: str = Field(..., description="The unique public ID for the CustomField.", json_schema_extra={'format': 'uuid'})

class RemoveLabelParams(StrictModel):
    """Request parameters for removing a Label from a Shortcut Story."""
    name: str = Field(..., description="The name of the new Label to remove.", min_length=1, max_length=128)

class StoryCustomField(StrictModel):
    field_id: str = Field(..., description="The unique public ID for a CustomField.", json_schema_extra={'format': 'uuid'})
    value_id: str = Field(..., description="The unique public ID for a CustomFieldEnumValue.", json_schema_extra={'format': 'uuid'})
    value: str = Field(..., description="A string representation of the value, if applicable.")

class StoryReaction(StrictModel):
    """Emoji reaction on a comment."""
    emoji: str = Field(..., description="Emoji text of the reaction.")
    permission_ids: list[str] = Field(..., description="Permissions who have reacted with this.")

class StoryComment(StrictModel):
    """A Comment is any note added within the Comment field of a Story."""
    app_url: str = Field(..., description="The Shortcut application url for the Comment.")
    entity_type: str = Field(..., description="A string description of this resource.")
    deleted: bool = Field(..., description="True/false boolean indicating whether the Comment has been deleted.")
    story_id: int = Field(..., description="The ID of the Story on which the Comment appears.", json_schema_extra={'format': 'int64'})
    mention_ids: list[str] = Field(..., description="`Deprecated:` use `member_mention_ids`.")
    author_id: str | None = Field(..., description="The unique ID of the Member who is the Comment's author.", json_schema_extra={'format': 'uuid'})
    member_mention_ids: list[str] = Field(..., description="The unique IDs of the Member who are mentioned in the Comment.")
    blocker: bool | None = Field(None, description="Marks the comment as a blocker that can be surfaced to permissions or teams mentioned in the comment. Can only be used on a top-level comment.")
    linked_to_slack: bool = Field(..., description="Whether the Comment is currently the root of a thread that is linked to Slack.")
    updated_at: str | None = Field(..., description="The time/date when the Comment was updated.", json_schema_extra={'format': 'date-time'})
    group_mention_ids: list[str] = Field(..., description="The unique IDs of the Group who are mentioned in the Comment.")
    external_id: str | None = Field(..., description="This field can be set to another unique ID. In the case that the Comment has been imported from another tool, the ID in the other tool can be indicated here.")
    parent_id: int | None = Field(None, description="The ID of the parent Comment this Comment is threaded under.", json_schema_extra={'format': 'int64'})
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID of the Comment.", json_schema_extra={'format': 'int64'})
    position: int = Field(..., description="The Comments numerical position in the list from oldest to newest.", json_schema_extra={'format': 'int64'})
    unblocks_parent: bool | None = Field(None, description="Marks the comment as an unblocker to its  blocker parent. Can only be set on a threaded comment who has a parent with `blocker` set.")
    reactions: list[StoryReaction] = Field(..., description="A set of Reactions to this Comment.")
    created_at: str = Field(..., description="The time/date when the Comment was created.", json_schema_extra={'format': 'date-time'})
    text: str | None = Field(..., description="The text of the Comment. In the case that the Comment has been deleted, this field can be set to nil.")

class StoryStats(StrictModel):
    """The stats object for Stories"""
    num_related_documents: int = Field(..., description="The number of documents related to this Story.", json_schema_extra={'format': 'int64'})

class SyncedItem(StrictModel):
    """The synced item for the story."""
    external_id: str = Field(..., description="The id used to reference an external entity.")
    url: str = Field(..., description="The url to the external entity.")

class Task(StrictModel):
    """A Task on a Story."""
    description: str = Field(..., description="Full text of the Task.")
    entity_type: str = Field(..., description="A string description of this resource.")
    story_id: int = Field(..., description="The unique identifier of the parent Story.", json_schema_extra={'format': 'int64'})
    mention_ids: list[str] = Field(..., description="`Deprecated:` use `member_mention_ids`.")
    member_mention_ids: list[str] = Field(..., description="An array of UUIDs of Members mentioned in this Task.")
    completed_at: str | None = Field(..., description="The time/date the Task was completed.", json_schema_extra={'format': 'date-time'})
    global_id: str
    updated_at: str | None = Field(..., description="The time/date the Task was updated.", json_schema_extra={'format': 'date-time'})
    group_mention_ids: list[str] = Field(..., description="An array of UUIDs of Groups mentioned in this Task.")
    owner_ids: list[str] = Field(..., description="An array of UUIDs of the Owners of this Task.")
    external_id: str | None = Field(..., description="This field can be set to another unique ID. In the case that the Task has been imported from another tool, the ID in the other tool can be indicated here.")
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID of the Task.", json_schema_extra={'format': 'int64'})
    position: int = Field(..., description="The number corresponding to the Task's position within a list of Tasks on a Story.", json_schema_extra={'format': 'int64'})
    complete: bool = Field(..., description="True/false boolean indicating whether the Task has been completed.")
    created_at: str = Field(..., description="The time/date the Task was created.", json_schema_extra={'format': 'date-time'})

class TypedStoryLink(StrictModel):
    """The type of Story Link. The string can be subject or object."""
    entity_type: str = Field(..., description="A string description of this resource.")
    object_id: int = Field(..., description="The ID of the object Story.", json_schema_extra={'format': 'int64'})
    verb: str = Field(..., description="How the subject Story acts on the object Story. This can be \"blocks\", \"duplicates\", or \"relates to\".")
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="This indicates whether the Story is the subject or object in the Story Link.")
    updated_at: str = Field(..., description="The time/date when the Story Link was last updated.", json_schema_extra={'format': 'date-time'})
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Story Link.", json_schema_extra={'format': 'int64'})
    subject_id: int = Field(..., description="The ID of the subject Story.", json_schema_extra={'format': 'int64'})
    subject_workflow_state_id: int = Field(..., description="The workflow state of the \"subject\" story.", json_schema_extra={'format': 'int64'})
    created_at: str = Field(..., description="The time/date when the Story Link was created.", json_schema_extra={'format': 'date-time'})

class UpdateCustomFieldEnumValue(StrictModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The unique ID of an existing EnumValue within the CustomField's domain.", json_schema_extra={'format': 'uuid'})
    value: str | None = Field(None, description="A string value within the domain of this Custom Field.", min_length=1, max_length=63)
    color_key: str | None = Field(None, description="A color key associated with this EnumValue within the CustomField's domain.")
    enabled: bool | None = Field(None, description="Whether this EnumValue is enabled for its CustomField or not. Leaving this key out of the request leaves the current enabled state untouched.")

class UploadedFile(StrictModel):
    """An UploadedFile is any document uploaded to your Shortcut Workspace. Files attached from a third-party service are different: see the Linked Files endpoint."""
    description: str | None = Field(..., description="The description of the file.")
    entity_type: str = Field(..., description="A string description of this resource.")
    story_ids: list[int] = Field(..., description="The unique IDs of the Stories associated with this file.")
    mention_ids: list[str] = Field(..., description="`Deprecated:` use `member_mention_ids`.")
    member_mention_ids: list[str] = Field(..., description="The unique IDs of the Members who are mentioned in the file description.")
    name: str = Field(..., description="The optional User-specified name of the file.")
    thumbnail_url: str | None = Field(..., description="The url where the thumbnail of the file can be found in Shortcut.")
    size: int = Field(..., description="The size of the file.", json_schema_extra={'format': 'int64'})
    uploader_id: str = Field(..., description="The unique ID of the Member who uploaded the file.", json_schema_extra={'format': 'uuid'})
    content_type: str = Field(..., description="Free form string corresponding to a text or image file.")
    updated_at: str | None = Field(..., description="The time/date that the file was updated.", json_schema_extra={'format': 'date-time'})
    filename: str = Field(..., description="The name assigned to the file in Shortcut upon upload.")
    group_mention_ids: list[str] = Field(..., description="The unique IDs of the Groups who are mentioned in the file description.")
    external_id: str | None = Field(..., description="This field can be set to another unique ID. In the case that the File has been imported from another tool, the ID in the other tool can be indicated here.")
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID for the file.", json_schema_extra={'format': 'int64'})
    url: str | None = Field(..., description="The URL for the file.")
    created_at: str = Field(..., description="The time/date that the file was created.", json_schema_extra={'format': 'date-time'})

class Story(StrictModel):
    """Stories are the standard unit of work in Shortcut and represent individual features, bugs, and chores."""
    app_url: str = Field(..., description="The Shortcut application url for the Story.")
    description: str = Field(..., description="The description of the story.")
    archived: bool = Field(..., description="True if the story has been archived or not.")
    started: bool = Field(..., description="A true/false boolean indicating if the Story has been started.")
    story_links: list[TypedStoryLink] = Field(..., description="An array of story links attached to the Story.")
    entity_type: str = Field(..., description="A string description of this resource.")
    labels: list[LabelSlim] = Field(..., description="An array of labels attached to the story.")
    mention_ids: list[str] = Field(..., description="`Deprecated:` use `member_mention_ids`.")
    synced_item: SyncedItem | None = None
    member_mention_ids: list[str] = Field(..., description="An array of Member IDs that have been mentioned in the Story description.")
    story_type: str = Field(..., description="The type of story (feature, bug, chore).")
    custom_fields: list[StoryCustomField] | None = Field(None, description="An array of CustomField value assertions for the story.")
    linked_files: list[LinkedFile] = Field(..., description="An array of linked files attached to the story.")
    workflow_id: int = Field(..., description="The ID of the workflow the story belongs to.", json_schema_extra={'format': 'int64'})
    completed_at_override: str | None = Field(..., description="A manual override for the time/date the Story was completed.", json_schema_extra={'format': 'date-time'})
    started_at: str | None = Field(..., description="The time/date the Story was started.", json_schema_extra={'format': 'date-time'})
    completed_at: str | None = Field(..., description="The time/date the Story was completed.", json_schema_extra={'format': 'date-time'})
    name: str = Field(..., description="The name of the story.")
    global_id: str
    completed: bool = Field(..., description="A true/false boolean indicating if the Story has been completed.")
    comments: list[StoryComment] = Field(..., description="An array of comments attached to the story.")
    blocker: bool = Field(..., description="A true/false boolean indicating if the Story is currently a blocker of another story.")
    branches: list[Branch] = Field(..., description="An array of Git branches attached to the story.")
    epic_id: int | None = Field(..., description="The ID of the epic the story belongs to.", json_schema_extra={'format': 'int64'})
    story_template_id: str | None = Field(..., description="The ID of the story template used to create this story, or null if not created using a template.", json_schema_extra={'format': 'uuid'})
    external_links: list[str] = Field(..., description="An array of external links (strings) associated with a Story")
    previous_iteration_ids: list[int] = Field(..., description="The IDs of the iteration the story belongs to.")
    requested_by_id: str = Field(..., description="The ID of the Member that requested the story.", json_schema_extra={'format': 'uuid'})
    iteration_id: int | None = Field(..., description="The ID of the iteration the story belongs to.", json_schema_extra={'format': 'int64'})
    sub_task_story_ids: list[int] | None = Field(None, description="The Story IDs of Sub-tasks attached to the Story\nField only applicable when Sub-task feature is enabled.")
    tasks: list[Task] = Field(..., description="An array of tasks connected to the story.")
    formatted_vcs_branch_name: str | None = Field(None, description="The formatted branch name for this story.")
    label_ids: list[int] = Field(..., description="An array of label ids attached to the story.")
    started_at_override: str | None = Field(..., description="A manual override for the time/date the Story was started.", json_schema_extra={'format': 'date-time'})
    group_id: str | None = Field(..., description="The ID of the group associated with the story.", json_schema_extra={'format': 'uuid'})
    workflow_state_id: int = Field(..., description="The ID of the workflow state the story is currently in.", json_schema_extra={'format': 'int64'})
    updated_at: str | None = Field(..., description="The time/date the Story was updated.", json_schema_extra={'format': 'date-time'})
    pull_requests: list[PullRequest] = Field(..., description="An array of Pull/Merge Requests attached to the story.")
    group_mention_ids: list[str] = Field(..., description="An array of Group IDs that have been mentioned in the Story description.")
    follower_ids: list[str] = Field(..., description="An array of UUIDs for any Members listed as Followers.")
    owner_ids: list[str] = Field(..., description="An array of UUIDs of the owners of this story.")
    external_id: str | None = Field(..., description="This field can be set to another unique ID. In the case that the Story has been imported from another tool, the ID in the other tool can be indicated here.")
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID of the Story.", json_schema_extra={'format': 'int64'})
    lead_time: int | None = Field(None, description="The lead time (in seconds) of this story when complete.", json_schema_extra={'format': 'int64'})
    parent_story_id: int | None = Field(None, description="The ID of the parent story to this story (making this story a sub-task).\nField only applicable when Sub-task feature is enabled.", json_schema_extra={'format': 'int64'})
    estimate: int | None = Field(..., description="The numeric point estimate of the story. Can also be null, which means unestimated.", json_schema_extra={'format': 'int64'})
    commits: list[Commit] = Field(..., description="An array of commits attached to the story.")
    files: list[UploadedFile] = Field(..., description="An array of files attached to the story.")
    position: int = Field(..., description="A number representing the position of the story in relation to every other story in the current project.", json_schema_extra={'format': 'int64'})
    blocked: bool = Field(..., description="A true/false boolean indicating if the Story is currently blocked.")
    project_id: int | None = Field(..., description="The ID of the project the story belongs to.", json_schema_extra={'format': 'int64'})
    deadline: str | None = Field(..., description="The due date of the story.", json_schema_extra={'format': 'date-time'})
    stats: StoryStats
    cycle_time: int | None = Field(None, description="The cycle time (in seconds) of this story when complete.", json_schema_extra={'format': 'int64'})
    created_at: str = Field(..., description="The time/date the Story was created.", json_schema_extra={'format': 'date-time'})
    moved_at: str | None = Field(..., description="The time/date the Story was last changed workflow-state.", json_schema_extra={'format': 'date-time'})

class WorkflowState(StrictModel):
    """Workflow State is any of the at least 3 columns. Workflow States correspond to one of 3 types: Unstarted, Started, or Done."""
    description: str = Field(..., description="The description of what sort of Stories belong in that Workflow state.")
    entity_type: str = Field(..., description="A string description of this resource.")
    color: str | None = Field(None, description="The hex color for this Workflow State.", min_length=1, pattern="^#[a-fA-F0-9]{6}$", json_schema_extra={'format': 'css-color'})
    verb: str | None = Field(..., description="The verb that triggers a move to that Workflow State when making VCS commits.")
    name: str = Field(..., description="The Workflow State's name.")
    global_id: str
    num_stories: int = Field(..., description="The number of Stories currently in that Workflow State.", json_schema_extra={'format': 'int64'})
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="The type of Workflow State (Unstarted, Started, or Finished)")
    updated_at: str = Field(..., description="When the Workflow State was last updated.", json_schema_extra={'format': 'date-time'})
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID of the Workflow State.", json_schema_extra={'format': 'int64'})
    num_story_templates: int = Field(..., description="The number of Story Templates associated with that Workflow State.", json_schema_extra={'format': 'int64'})
    position: int = Field(..., description="The position that the Workflow State is in, starting with 0 at the left.", json_schema_extra={'format': 'int64'})
    created_at: str = Field(..., description="The time/date the Workflow State was created.", json_schema_extra={'format': 'date-time'})

class Workflow(StrictModel):
    """Workflow is the array of defined Workflow States. Workflow can be queried using the API but must be updated in the Shortcut UI."""
    description: str = Field(..., description="A description of the workflow.")
    entity_type: str = Field(..., description="A string description of this resource.")
    project_ids: list[float] = Field(..., description="An array of IDs of projects within the Workflow.")
    states: list[WorkflowState] = Field(..., description="A map of the states in this Workflow.")
    name: str = Field(..., description="The name of the workflow.")
    updated_at: str = Field(..., description="The date the Workflow was updated.", json_schema_extra={'format': 'date-time'})
    auto_assign_owner: bool = Field(..., description="Indicates if an owner is automatically assigned when an unowned story is started.")
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID of the Workflow.", json_schema_extra={'format': 'int64'})
    team_id: int = Field(..., description="The ID of the team the workflow belongs to.", json_schema_extra={'format': 'int64'})
    created_at: str = Field(..., description="The date the Workflow was created.", json_schema_extra={'format': 'date-time'})
    default_state_id: int = Field(..., description="The unique ID of the default state that new Stories are entered into.", json_schema_extra={'format': 'int64'})

class Epic(StrictModel):
    """An Epic is a collection of stories that together might make up a release, a objective, or some other large initiative that you are working on."""
    app_url: str = Field(..., description="The Shortcut application url for the Epic.")
    description: str = Field(..., description="The Epic's description.")
    archived: bool = Field(..., description="True/false boolean that indicates whether the Epic is archived or not.")
    started: bool = Field(..., description="A true/false boolean indicating if the Epic has been started.")
    entity_type: str = Field(..., description="A string description of this resource.")
    labels: list[LabelSlim] = Field(..., description="An array of Labels attached to the Epic.")
    mention_ids: list[str] = Field(..., description="`Deprecated:` use `member_mention_ids`.")
    member_mention_ids: list[str] = Field(..., description="An array of Member IDs that have been mentioned in the Epic description.")
    associated_groups: list[EpicAssociatedGroup] = Field(..., description="An array containing Group IDs and Group-owned story counts for the Epic's associated groups.")
    project_ids: list[int] = Field(..., description="The IDs of Projects related to this Epic.")
    stories_without_projects: int = Field(..., description="The number of stories in this epic which are not associated with a project.", json_schema_extra={'format': 'int64'})
    completed_at_override: str | None = Field(..., description="A manual override for the time/date the Epic was completed.", json_schema_extra={'format': 'date-time'})
    productboard_plugin_id: str | None = Field(..., description="The ID of the associated productboard integration.", json_schema_extra={'format': 'uuid'})
    started_at: str | None = Field(..., description="The time/date the Epic was started.", json_schema_extra={'format': 'date-time'})
    completed_at: str | None = Field(..., description="The time/date the Epic was completed.", json_schema_extra={'format': 'date-time'})
    objective_ids: list[int] = Field(..., description="An array of IDs for Objectives to which this epic is related.")
    name: str = Field(..., description="The name of the Epic.")
    global_id: str
    completed: bool = Field(..., description="A true/false boolean indicating if the Epic has been completed.")
    comments: list[ThreadedComment] = Field(..., description="A nested array of threaded comments.")
    productboard_url: str | None = Field(..., description="The URL of the associated productboard feature.")
    planned_start_date: str | None = Field(..., description="The Epic's planned start date.", json_schema_extra={'format': 'date-time'})
    state: str = Field(..., description="`Deprecated` The workflow state that the Epic is in.")
    milestone_id: int | None = Field(..., description="`Deprecated` The ID of the Objective this Epic is related to. Use `objective_ids`.", json_schema_extra={'format': 'int64'})
    requested_by_id: str = Field(..., description="The ID of the Member that requested the epic.", json_schema_extra={'format': 'uuid'})
    epic_state_id: int = Field(..., description="The ID of the Epic State.", json_schema_extra={'format': 'int64'})
    label_ids: list[int] = Field(..., description="An array of Label ids attached to the Epic.")
    started_at_override: str | None = Field(..., description="A manual override for the time/date the Epic was started.", json_schema_extra={'format': 'date-time'})
    group_id: str | None = Field(..., description="`Deprecated` The ID of the group to associate with the epic. Use `group_ids`.", json_schema_extra={'format': 'uuid'})
    updated_at: str | None = Field(..., description="The time/date the Epic was updated.", json_schema_extra={'format': 'date-time'})
    group_mention_ids: list[str] = Field(..., description="An array of Group IDs that have been mentioned in the Epic description.")
    productboard_id: str | None = Field(..., description="The ID of the associated productboard feature.", json_schema_extra={'format': 'uuid'})
    follower_ids: list[str] = Field(..., description="An array of UUIDs for any Members you want to add as Followers on this Epic.")
    group_ids: list[str] = Field(..., description="An array of UUIDS for Groups to which this Epic is related.")
    owner_ids: list[str] = Field(..., description="An array of UUIDs for any members you want to add as Owners on this new Epic.")
    external_id: str | None = Field(..., description="This field can be set to another unique ID. In the case that the Epic has been imported from another tool, the ID in the other tool can be indicated here.")
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID of the Epic.", json_schema_extra={'format': 'int64'})
    health: Health | None = None
    position: int = Field(..., description="The Epic's relative position in the Epic workflow state.", json_schema_extra={'format': 'int64'})
    productboard_name: str | None = Field(..., description="The name of the associated productboard feature.")
    deadline: str | None = Field(..., description="The Epic's deadline.", json_schema_extra={'format': 'date-time'})
    stats: EpicStats
    created_at: str | None = Field(..., description="The time/date the Epic was created.", json_schema_extra={'format': 'date-time'})

class Health(StrictModel):
    """The current health status of the Epic."""
    entity_type: str = Field(..., description="A string description of this resource.")
    author_id: str | None = Field(None, description="The ID of the permission who created or updated the Health record.", json_schema_extra={'format': 'uuid'})
    epic_id: int | None = Field(None, description="The ID of the Epic associated with this Health record.", json_schema_extra={'format': 'int64'})
    objective_id: int | None = Field(None, description="The ID of the Objective associated with this Health record.", json_schema_extra={'format': 'int64'})
    updated_at: str | None = Field(None, description="The time that the Health record was updated.", json_schema_extra={'format': 'date-time'})
    status: Literal["At Risk", "On Track", "Off Track", "No Health"] = Field(..., description="The health status of the Epic or Objective.")
    id_: str | None = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID of the Health record.", json_schema_extra={'format': 'uuid'})
    created_at: str | None = Field(None, description="The time that the Health record was created.", json_schema_extra={'format': 'date-time'})
    text: str | None = Field(None, description="The text of the Health record.")

class ThreadedComment(StrictModel):
    """Comments associated with Epic Discussions."""
    app_url: str = Field(..., description="The Shortcut application url for the Comment.")
    entity_type: str = Field(..., description="A string description of this resource.")
    deleted: bool = Field(..., description="True/false boolean indicating whether the Comment is deleted.")
    mention_ids: list[str] = Field(..., description="`Deprecated:` use `member_mention_ids`.")
    author_id: str = Field(..., description="The unique ID of the Member that authored the Comment.", json_schema_extra={'format': 'uuid'})
    member_mention_ids: list[str] = Field(..., description="An array of Member IDs that have been mentioned in this Comment.")
    comments: list[ThreadedComment] = Field(..., description="A nested array of threaded comments.")
    updated_at: str = Field(..., description="The time/date the Comment was updated.", json_schema_extra={'format': 'date-time'})
    group_mention_ids: list[str] = Field(..., description="An array of Group IDs that have been mentioned in this Comment.")
    external_id: str | None = Field(..., description="This field can be set to another unique ID. In the case that the Comment has been imported from another tool, the ID in the other tool can be indicated here.")
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The unique ID of the Comment.", json_schema_extra={'format': 'int64'})
    created_at: str = Field(..., description="The time/date the Comment was created.", json_schema_extra={'format': 'date-time'})
    text: str = Field(..., description="The text of the Comment.")


# Rebuild models to resolve forward references (required for circular refs)
Branch.model_rebuild()
Category.model_rebuild()
Commit.model_rebuild()
CreateCategoryParams.model_rebuild()
CreateLabelParams.model_rebuild()
CreateStoryCommentParams.model_rebuild()
CreateStoryLinkParams.model_rebuild()
CreateStoryParams.model_rebuild()
CreateSubTaskParams.model_rebuild()
CreateTaskParams.model_rebuild()
CustomField.model_rebuild()
CustomFieldEnumValue.model_rebuild()
CustomFieldValueParams.model_rebuild()
Doc.model_rebuild()
Epic.model_rebuild()
EpicAssociatedGroup.model_rebuild()
EpicStats.model_rebuild()
Group.model_rebuild()
Health.model_rebuild()
Icon.model_rebuild()
Identity.model_rebuild()
Iteration.model_rebuild()
IterationAssociatedGroup.model_rebuild()
IterationStats.model_rebuild()
Label.model_rebuild()
LabelSlim.model_rebuild()
LabelStats.model_rebuild()
LinkedFile.model_rebuild()
LinkSubTaskParams.model_rebuild()
Milestone.model_rebuild()
MilestoneStats.model_rebuild()
Objective.model_rebuild()
ObjectiveStats.model_rebuild()
PullRequest.model_rebuild()
PullRequestLabel.model_rebuild()
RemoveCustomFieldParams.model_rebuild()
RemoveLabelParams.model_rebuild()
Story.model_rebuild()
StoryComment.model_rebuild()
StoryCustomField.model_rebuild()
StoryReaction.model_rebuild()
StoryStats.model_rebuild()
SyncedItem.model_rebuild()
Task.model_rebuild()
ThreadedComment.model_rebuild()
TypedStoryLink.model_rebuild()
UpdateCustomFieldEnumValue.model_rebuild()
UploadedFile.model_rebuild()
Workflow.model_rebuild()
WorkflowState.model_rebuild()

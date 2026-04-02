"""
Google Gmail MCP Server - Pydantic Models

Generated: 2026-04-02 11:32:27 UTC
Generator: MCP Blacksmith v1.0.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "DraftsCreateRequest",
    "DraftsDeleteRequest",
    "DraftsGetRequest",
    "DraftsListRequest",
    "DraftsSendRequest",
    "DraftsUpdateRequest",
    "GetProfileRequest",
    "HistoryListRequest",
    "LabelsCreateRequest",
    "LabelsDeleteRequest",
    "LabelsGetRequest",
    "LabelsListRequest",
    "LabelsPatchRequest",
    "LabelsUpdateRequest",
    "MessagesAttachmentsGetRequest",
    "MessagesBatchDeleteRequest",
    "MessagesBatchModifyRequest",
    "MessagesDeleteRequest",
    "MessagesGetRequest",
    "MessagesImportRequest",
    "MessagesInsertRequest",
    "MessagesListRequest",
    "MessagesModifyRequest",
    "MessagesSendRequest",
    "MessagesTrashRequest",
    "MessagesUntrashRequest",
    "SettingsCseIdentitiesCreateRequest",
    "SettingsCseIdentitiesDeleteRequest",
    "SettingsCseIdentitiesGetRequest",
    "SettingsCseIdentitiesListRequest",
    "SettingsCseIdentitiesPatchRequest",
    "SettingsCseKeypairsCreateRequest",
    "SettingsCseKeypairsDisableRequest",
    "SettingsCseKeypairsEnableRequest",
    "SettingsCseKeypairsGetRequest",
    "SettingsCseKeypairsListRequest",
    "SettingsCseKeypairsObliterateRequest",
    "SettingsDelegatesCreateRequest",
    "SettingsDelegatesDeleteRequest",
    "SettingsDelegatesGetRequest",
    "SettingsDelegatesListRequest",
    "SettingsFiltersCreateRequest",
    "SettingsFiltersDeleteRequest",
    "SettingsFiltersGetRequest",
    "SettingsFiltersListRequest",
    "SettingsForwardingAddressesCreateRequest",
    "SettingsForwardingAddressesDeleteRequest",
    "SettingsForwardingAddressesGetRequest",
    "SettingsForwardingAddressesListRequest",
    "SettingsGetAutoForwardingRequest",
    "SettingsGetImapRequest",
    "SettingsGetLanguageRequest",
    "SettingsGetPopRequest",
    "SettingsGetVacationRequest",
    "SettingsSendAsCreateRequest",
    "SettingsSendAsDeleteRequest",
    "SettingsSendAsGetRequest",
    "SettingsSendAsListRequest",
    "SettingsSendAsPatchRequest",
    "SettingsSendAsSmimeInfoDeleteRequest",
    "SettingsSendAsSmimeInfoGetRequest",
    "SettingsSendAsSmimeInfoInsertRequest",
    "SettingsSendAsSmimeInfoListRequest",
    "SettingsSendAsSmimeInfoSetDefaultRequest",
    "SettingsSendAsUpdateRequest",
    "SettingsSendAsVerifyRequest",
    "SettingsUpdateAutoForwardingRequest",
    "SettingsUpdateImapRequest",
    "SettingsUpdateLanguageRequest",
    "SettingsUpdatePopRequest",
    "SettingsUpdateVacationRequest",
    "StopRequest",
    "ThreadsDeleteRequest",
    "ThreadsGetRequest",
    "ThreadsListRequest",
    "ThreadsModifyRequest",
    "ThreadsTrashRequest",
    "ThreadsUntrashRequest",
    "WatchRequest",
    "ClassificationLabelValue",
    "CsePrivateKeyMetadata",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: get_profile
class GetProfileRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address or the special value `me` to refer to the authenticated user.")
class GetProfileRequest(StrictModel):
    """Retrieves the Gmail profile information for the authenticated user or a specified user, including account details and settings."""
    path: GetProfileRequestPath

# Operation: stop_push_notifications
class StopRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address or the special value `me` to refer to the authenticated user.")
class StopRequest(StrictModel):
    """Stop receiving push notifications for the specified user's Gmail mailbox. This disables all push notification delivery to the configured endpoint."""
    path: StopRequestPath

# Operation: enable_mailbox_watch
class WatchRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The email address of the user whose mailbox to watch. Use the special value 'me' to refer to the authenticated user.")
class WatchRequestBody(StrictModel):
    label_filter_behavior: Literal["include", "exclude"] | None = Field(default=None, validation_alias="labelFilterBehavior", serialization_alias="labelFilterBehavior", description="Determines how the labelIds list is applied: 'include' to only notify on changes to specified labels, or 'exclude' to notify on all changes except those to specified labels.")
    label_ids: list[str] | None = Field(default=None, validation_alias="labelIds", serialization_alias="labelIds", description="List of label IDs to filter notifications. When combined with labelFilterBehavior, controls which mailbox changes trigger push notifications. If omitted, all changes are included by default.")
    topic_name: str | None = Field(default=None, validation_alias="topicName", serialization_alias="topicName", description="The fully qualified Cloud Pub/Sub topic name where notifications will be published. The topic must already exist and Gmail must have publish permissions on it. Use the Cloud Pub/Sub v1 naming format: projects/{project-id}/topics/{topic-name}.")
class WatchRequest(StrictModel):
    """Enable or update push notifications for a Gmail mailbox by subscribing to a Cloud Pub/Sub topic. Changes matching the specified criteria will be published to the configured topic."""
    path: WatchRequestPath
    body: WatchRequestBody | None = None

# Operation: list_drafts
class DraftsListRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user.")
class DraftsListRequestQuery(StrictModel):
    include_spam_trash: bool | None = Field(default=None, validation_alias="includeSpamTrash", serialization_alias="includeSpamTrash", description="Whether to include draft messages from the SPAM and TRASH folders in the results.")
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="Maximum number of drafts to return. The default is 100 and the maximum allowed value is 500.", le=500)
    q: str | None = Field(default=None, description="Filter draft messages using Gmail search query syntax. Supports the same query operators as the Gmail search box (e.g., from:, rfc822msgid:, is:unread).")
class DraftsListRequest(StrictModel):
    """Retrieves a list of draft messages from the user's mailbox. Supports filtering by search query and optional inclusion of drafts from spam and trash folders."""
    path: DraftsListRequestPath
    query: DraftsListRequestQuery | None = None

# Operation: create_draft
class DraftsCreateRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address or the special value 'me' to indicate the authenticated user.")
class DraftsCreateRequestBodyMessage(StrictModel):
    classification_label_values: list[ClassificationLabelValue] | None = Field(default=None, validation_alias="classificationLabelValues", serialization_alias="classificationLabelValues", description="Classification label values to apply to the draft message. Each classification label ID must be unique; duplicate IDs will be deduplicated arbitrarily. Only available for Google Workspace accounts.")
    label_ids: list[str] | None = Field(default=None, validation_alias="labelIds", serialization_alias="labelIds", description="List of label IDs to apply to the draft message. Labels are applied in the order provided.")
    raw: str | None = Field(default=None, validation_alias="raw", serialization_alias="raw", description="The entire email message in an RFC 2822 formatted and base64url encoded string. Returned in `messages.get` and `drafts.get` responses when the `format=RAW` parameter is supplied.", json_schema_extra={'format': 'byte'})
class DraftsCreateRequestBody(StrictModel):
    message: DraftsCreateRequestBodyMessage | None = None
class DraftsCreateRequest(StrictModel):
    """Creates a new email draft with the DRAFT label in Gmail. The draft can optionally include classification labels and custom label IDs."""
    path: DraftsCreateRequestPath
    body: DraftsCreateRequestBody | None = None

# Operation: get_draft
class DraftsGetRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address or the special value 'me' to refer to the authenticated user.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the draft message to retrieve.")
class DraftsGetRequestQuery(StrictModel):
    format_: Literal["minimal", "full", "raw", "metadata"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="The format in which to return the draft message content and metadata.")
class DraftsGetRequest(StrictModel):
    """Retrieves a specific draft message by ID. Returns the draft in the requested format for viewing or further editing."""
    path: DraftsGetRequestPath
    query: DraftsGetRequestQuery | None = None

# Operation: update_draft
class DraftsUpdateRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the draft message to update.")
class DraftsUpdateRequestBodyMessage(StrictModel):
    classification_label_values: list[ClassificationLabelValue] | None = Field(default=None, validation_alias="classificationLabelValues", serialization_alias="classificationLabelValues", description="Classification label values to apply to the message. Each classification label ID must be unique; duplicate IDs will be deduplicated arbitrarily. Only available for Google Workspace accounts. Classification label schemas can be queried using the Google Drive Labels API.")
    label_ids: list[str] | None = Field(default=None, validation_alias="labelIds", serialization_alias="labelIds", description="List of label IDs to apply to this message. Labels are used to organize and categorize messages in Gmail.")
    raw: str | None = Field(default=None, validation_alias="raw", serialization_alias="raw", description="The entire email message in an RFC 2822 formatted and base64url encoded string. Returned in `messages.get` and `drafts.get` responses when the `format=RAW` parameter is supplied.", json_schema_extra={'format': 'byte'})
class DraftsUpdateRequestBody(StrictModel):
    message: DraftsUpdateRequestBodyMessage | None = None
class DraftsUpdateRequest(StrictModel):
    """Updates the content of an existing draft message. Replaces the draft's message body and metadata with the provided values."""
    path: DraftsUpdateRequestPath
    body: DraftsUpdateRequestBody | None = None

# Operation: delete_draft
class DraftsDeleteRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The email address of the user whose draft should be deleted. Use the special value `me` to refer to the authenticated user.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the draft message to delete.")
class DraftsDeleteRequest(StrictModel):
    """Permanently deletes a draft message without moving it to trash. This action is immediate and irreversible."""
    path: DraftsDeleteRequestPath

# Operation: send_draft
class DraftsSendRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address or the special value `me` to indicate the authenticated user.")
class DraftsSendRequestBodyMessage(StrictModel):
    classification_label_values: list[ClassificationLabelValue] | None = Field(default=None, validation_alias="classificationLabelValues", serialization_alias="classificationLabelValues", description="Classification label values to apply to the message. Each classification label ID must be unique; duplicate IDs will be deduplicated arbitrarily. Only available for Google Workspace accounts.")
    label_ids: list[str] | None = Field(default=None, validation_alias="labelIds", serialization_alias="labelIds", description="List of label IDs to apply to this message. Labels are applied in the order provided.")
    raw: str | None = Field(default=None, validation_alias="raw", serialization_alias="raw", description="The entire email message in an RFC 2822 formatted and base64url encoded string. Returned in `messages.get` and `drafts.get` responses when the `format=RAW` parameter is supplied.", json_schema_extra={'format': 'byte'})
class DraftsSendRequestBody(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The immutable ID of the draft.")
    message: DraftsSendRequestBodyMessage | None = None
class DraftsSendRequest(StrictModel):
    """Sends an existing draft message to recipients specified in the To, Cc, and Bcc headers. The draft must already exist and contain valid recipient information."""
    path: DraftsSendRequestPath
    body: DraftsSendRequestBody | None = None

# Operation: list_mailbox_history
class HistoryListRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user.")
class HistoryListRequestQuery(StrictModel):
    history_types: list[Literal["messageAdded", "messageDeleted", "labelAdded", "labelRemoved"]] | None = Field(default=None, validation_alias="historyTypes", serialization_alias="historyTypes", description="Types of history events to include in results. When specified, only changes matching these types are returned.")
    label_id: str | None = Field(default=None, validation_alias="labelId", serialization_alias="labelId", description="Filter results to only include messages with a specific label ID.")
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="Maximum number of history records to return per request. Defaults to 100 if not specified.", le=500)
    start_history_id: str | None = Field(default=None, validation_alias="startHistoryId", serialization_alias="startHistoryId", description="Starting point for retrieving history records. Provide a historyId from a previous response or message to retrieve all changes after that point. History IDs are valid for at least a week but may expire sooner in rare cases. If an HTTP 404 error occurs, perform a full sync. Omit this parameter for the initial sync request.")
class HistoryListRequest(StrictModel):
    """Retrieves the chronological history of all changes to a mailbox, including message additions, deletions, and label modifications. Results are returned in chronological order by historyId and support pagination for efficient sync operations."""
    path: HistoryListRequestPath
    query: HistoryListRequestQuery | None = None

# Operation: list_labels
class LabelsListRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address or the special value `me` to refer to the authenticated user.")
class LabelsListRequest(StrictModel):
    """Retrieves all labels in the user's mailbox. Labels are used to organize and categorize emails in Gmail."""
    path: LabelsListRequestPath

# Operation: create_label
class LabelsCreateRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address or the special value `me` to indicate the authenticated user.")
class LabelsCreateRequestBody(StrictModel):
    label_list_visibility: Literal["labelShow", "labelShowIfUnread", "labelHide"] | None = Field(default=None, validation_alias="labelListVisibility", serialization_alias="labelListVisibility", description="Controls whether this label appears in the label list in Gmail's web interface.")
    message_list_visibility: Literal["show", "hide"] | None = Field(default=None, validation_alias="messageListVisibility", serialization_alias="messageListVisibility", description="Controls whether messages with this label are visible in the message list in Gmail's web interface.")
    name: str | None = Field(default=None, description="The display name for the label as it appears in Gmail.")
    type_: Literal["system", "user"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The owner type for the label. User labels are created and managed by the user and can be applied to any message or thread. System labels are internally created and cannot be modified or deleted by users.")
class LabelsCreateRequest(StrictModel):
    """Creates a new custom label in Gmail for organizing messages and threads. Labels can be configured with specific visibility settings in the Gmail web interface."""
    path: LabelsCreateRequestPath
    body: LabelsCreateRequestBody | None = None

# Operation: get_label
class LabelsGetRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address or the special value `me` to refer to the authenticated user.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the label to retrieve.")
class LabelsGetRequest(StrictModel):
    """Retrieves a specific Gmail label by its ID. Use this to fetch detailed information about a label, such as its name, visibility settings, and other metadata."""
    path: LabelsGetRequestPath

# Operation: update_label
class LabelsUpdateRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the label to update.")
class LabelsUpdateRequestBody(StrictModel):
    label_list_visibility: Literal["labelShow", "labelShowIfUnread", "labelHide"] | None = Field(default=None, validation_alias="labelListVisibility", serialization_alias="labelListVisibility", description="Controls whether the label appears in the label list in Gmail's web interface.")
    message_list_visibility: Literal["show", "hide"] | None = Field(default=None, validation_alias="messageListVisibility", serialization_alias="messageListVisibility", description="Controls whether messages with this label are visible in the message list in Gmail's web interface.")
    name: str | None = Field(default=None, description="The display name of the label as shown to the user in Gmail.")
    type_: Literal["system", "user"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The owner type of the label. User labels can be modified and deleted; system labels are managed by Gmail and cannot be altered.")
class LabelsUpdateRequest(StrictModel):
    """Updates an existing Gmail label with new properties such as display name and visibility settings. Only user-created labels can be modified; system labels cannot be changed."""
    path: LabelsUpdateRequestPath
    body: LabelsUpdateRequestBody | None = None

# Operation: update_label_partial
class LabelsPatchRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the label to update.")
class LabelsPatchRequestBody(StrictModel):
    label_list_visibility: Literal["labelShow", "labelShowIfUnread", "labelHide"] | None = Field(default=None, validation_alias="labelListVisibility", serialization_alias="labelListVisibility", description="Controls whether this label appears in the label list within Gmail's web interface.")
    message_list_visibility: Literal["show", "hide"] | None = Field(default=None, validation_alias="messageListVisibility", serialization_alias="messageListVisibility", description="Controls whether messages with this label are visible in the message list within Gmail's web interface.")
    name: str | None = Field(default=None, description="The human-readable name displayed for this label in the Gmail interface.")
    type_: Literal["system", "user"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Indicates whether this is a system label (created and managed by Gmail) or a user label (created and managed by the user). System labels cannot be modified or deleted, while user labels can be fully customized.")
class LabelsPatchRequest(StrictModel):
    """Update properties of a Gmail label using partial update semantics. Modify visibility settings, display name, or other label attributes without replacing the entire label configuration."""
    path: LabelsPatchRequestPath
    body: LabelsPatchRequestBody | None = None

# Operation: delete_label
class LabelsDeleteRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the label to delete.")
class LabelsDeleteRequest(StrictModel):
    """Permanently deletes a label and removes it from all messages and threads it is applied to. This action cannot be undone."""
    path: LabelsDeleteRequestPath

# Operation: delete_messages
class MessagesBatchDeleteRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address or the special value `me` to indicate the authenticated user.")
class MessagesBatchDeleteRequestBody(StrictModel):
    ids: list[str] | None = Field(default=None, description="An array of message IDs to delete. The order of IDs is not significant.")
class MessagesBatchDeleteRequest(StrictModel):
    """Permanently deletes multiple messages by their IDs. Note that this operation provides no guarantees about message existence or prior deletion status."""
    path: MessagesBatchDeleteRequestPath
    body: MessagesBatchDeleteRequestBody | None = None

# Operation: modify_message_labels
class MessagesBatchModifyRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user.")
class MessagesBatchModifyRequestBody(StrictModel):
    add_label_ids: list[str] | None = Field(default=None, validation_alias="addLabelIds", serialization_alias="addLabelIds", description="Label IDs to add to the specified messages. Order is not significant.")
    ids: list[str] | None = Field(default=None, description="The message IDs to modify. Maximum of 1000 IDs per request.")
    remove_label_ids: list[str] | None = Field(default=None, validation_alias="removeLabelIds", serialization_alias="removeLabelIds", description="Label IDs to remove from the specified messages. Order is not significant.")
class MessagesBatchModifyRequest(StrictModel):
    """Modifies labels on specified messages by adding and/or removing label IDs. Supports batch operations on up to 1000 messages per request."""
    path: MessagesBatchModifyRequestPath
    body: MessagesBatchModifyRequestBody | None = None

# Operation: get_message
class MessagesGetRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address or the special value `me` to indicate the authenticated user.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the message to retrieve, typically obtained from messages.list, messages.insert, or messages.import operations.")
class MessagesGetRequestQuery(StrictModel):
    format_: Literal["minimal", "full", "raw", "metadata"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="The format in which to return the message content and structure.")
    metadata_headers: list[str] | None = Field(default=None, validation_alias="metadataHeaders", serialization_alias="metadataHeaders", description="When format is set to `metadata`, specify which message headers to include in the response. Headers should be provided as an array of header names.")
class MessagesGetRequest(StrictModel):
    """Retrieves a specific message by ID from the user's mailbox. Supports multiple output formats including full message content, headers only, or raw RFC 2822 format."""
    path: MessagesGetRequestPath
    query: MessagesGetRequestQuery | None = None

# Operation: delete_message
class MessagesDeleteRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The email address of the user whose message will be deleted. Use the special value `me` to refer to the authenticated user.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the message to delete.")
class MessagesDeleteRequest(StrictModel):
    """Permanently and immediately deletes a specified message. This action cannot be undone; consider using trash_message for recoverable deletion instead."""
    path: MessagesDeleteRequestPath

# Operation: import_message
class MessagesImportRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value 'me' to reference the authenticated user.")
class MessagesImportRequestQuery(StrictModel):
    deleted: bool | None = Field(default=None, description="Mark the message as permanently deleted and only visible to Google Vault administrators. Only applicable for Google Workspace accounts.")
    internal_date_source: Literal["receivedTime", "dateHeader"] | None = Field(default=None, validation_alias="internalDateSource", serialization_alias="internalDateSource", description="Determines the source for Gmail's internal date assignment to the message.")
    never_mark_spam: bool | None = Field(default=None, validation_alias="neverMarkSpam", serialization_alias="neverMarkSpam", description="Prevent Gmail's spam classifier from marking this message as SPAM, regardless of its classification decision.")
    process_for_calendar: bool | None = Field(default=None, validation_alias="processForCalendar", serialization_alias="processForCalendar", description="Automatically process calendar invitations in the message and add any extracted meetings to the user's Google Calendar.")
class MessagesImportRequestBody(StrictModel):
    classification_label_values: list[ClassificationLabelValue] | None = Field(default=None, validation_alias="classificationLabelValues", serialization_alias="classificationLabelValues", description="Classification label values to apply to the message. Each classification label ID must be unique; duplicate IDs will be deduplicated arbitrarily. Only applicable for Google Workspace accounts. Available schemas can be queried using the Google Drive Labels API.")
    label_ids: list[str] | None = Field(default=None, validation_alias="labelIds", serialization_alias="labelIds", description="List of label IDs to apply to the imported message. Labels are applied in the order provided.")
    raw: str | None = Field(default=None, description="The entire email message in an RFC 2822 formatted and base64url encoded string. Returned in `messages.get` and `drafts.get` responses when the `format=RAW` parameter is supplied.", json_schema_extra={'format': 'byte'})
class MessagesImportRequest(StrictModel):
    """Imports a message into the user's mailbox with standard email delivery scanning and classification. The message is processed similarly to SMTP delivery, with a maximum size limit of 150MB."""
    path: MessagesImportRequestPath
    query: MessagesImportRequestQuery | None = None
    body: MessagesImportRequestBody | None = None

# Operation: list_messages
class MessagesListRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user.")
class MessagesListRequestQuery(StrictModel):
    include_spam_trash: bool | None = Field(default=None, validation_alias="includeSpamTrash", serialization_alias="includeSpamTrash", description="Include messages from SPAM and TRASH folders in the results. Defaults to false if not specified.")
    label_ids: list[str] | None = Field(default=None, validation_alias="labelIds", serialization_alias="labelIds", description="Filter results to only include messages with labels matching all specified label IDs. Messages within the same thread may have different labels. Provide as an array of label ID strings.")
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="Maximum number of messages to return per request. Defaults to 100 if not specified.", le=500)
    q: str | None = Field(default=None, description="Only return messages matching the specified query. Supports the same query format as the Gmail search box. For example, `\"from:someuser@example.com rfc822msgid: is:unread\"`. Parameter cannot be used when accessing the api using the gmail.metadata scope.")
class MessagesListRequest(StrictModel):
    """Retrieves a list of messages from the user's mailbox, with optional filtering by labels and inclusion of spam/trash folders. Supports pagination through the maxResults parameter."""
    path: MessagesListRequestPath
    query: MessagesListRequestQuery | None = None

# Operation: insert_message
class MessagesInsertRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value 'me' to refer to the authenticated user.")
class MessagesInsertRequestQuery(StrictModel):
    deleted: bool | None = Field(default=None, description="Mark the message as permanently deleted and only visible to Google Vault administrators. Only applicable for Google Workspace accounts.")
    internal_date_source: Literal["receivedTime", "dateHeader"] | None = Field(default=None, validation_alias="internalDateSource", serialization_alias="internalDateSource", description="Determines the source for Gmail's internal date assigned to the message.")
class MessagesInsertRequestBody(StrictModel):
    classification_label_values: list[ClassificationLabelValue] | None = Field(default=None, validation_alias="classificationLabelValues", serialization_alias="classificationLabelValues", description="Classification label values to apply to the message. Each classification label ID must be unique; duplicate IDs will be deduplicated arbitrarily. Only applicable for Google Workspace accounts. Available schemas can be queried via the Google Drive Labels API.")
    label_ids: list[str] | None = Field(default=None, validation_alias="labelIds", serialization_alias="labelIds", description="List of label IDs to apply to this message. Labels are applied in the order provided.")
    raw: str | None = Field(default=None, description="The entire email message in an RFC 2822 formatted and base64url encoded string. Returned in `messages.get` and `drafts.get` responses when the `format=RAW` parameter is supplied.", json_schema_extra={'format': 'byte'})
class MessagesInsertRequest(StrictModel):
    """Inserts a message directly into the user's mailbox, bypassing scanning and classification, similar to IMAP APPEND. This operation does not send a message but adds it to the mailbox with optional metadata."""
    path: MessagesInsertRequestPath
    query: MessagesInsertRequestQuery | None = None
    body: MessagesInsertRequestBody | None = None

# Operation: update_message_labels
class MessagesModifyRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The email address of the user whose message will be modified. Use the special value `me` to refer to the authenticated user.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the message to modify.")
class MessagesModifyRequestBody(StrictModel):
    add_label_ids: list[str] | None = Field(default=None, validation_alias="addLabelIds", serialization_alias="addLabelIds", description="A list of label IDs to add to the message. Maximum of 100 labels can be added in a single request.")
    remove_label_ids: list[str] | None = Field(default=None, validation_alias="removeLabelIds", serialization_alias="removeLabelIds", description="A list of label IDs to remove from the message. Maximum of 100 labels can be removed in a single request.")
class MessagesModifyRequest(StrictModel):
    """Updates the labels applied to a specific message by adding and/or removing label IDs. You can modify up to 100 labels per request."""
    path: MessagesModifyRequestPath
    body: MessagesModifyRequestBody | None = None

# Operation: send_message
class MessagesSendRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The email address of the user sending the message. Use the special value `me` to refer to the authenticated user.")
class MessagesSendRequestBody(StrictModel):
    classification_label_values: list[ClassificationLabelValue] | None = Field(default=None, validation_alias="classificationLabelValues", serialization_alias="classificationLabelValues", description="Classification labels to apply to the message for organizational purposes. Each classification label ID must be unique; duplicate IDs will be deduplicated arbitrarily. Only available for Google Workspace accounts.")
    label_ids: list[str] | None = Field(default=None, validation_alias="labelIds", serialization_alias="labelIds", description="IDs of labels to apply to the message. Labels help organize and categorize messages in Gmail.")
    raw: str | None = Field(default=None, description="The entire email message in an RFC 2822 formatted and base64url encoded string. Returned in `messages.get` and `drafts.get` responses when the `format=RAW` parameter is supplied.", json_schema_extra={'format': 'byte'})
class MessagesSendRequest(StrictModel):
    """Sends an email message to recipients specified in the To, Cc, and Bcc headers. The message is delivered immediately to all specified recipients."""
    path: MessagesSendRequestPath
    body: MessagesSendRequestBody | None = None

# Operation: trash_message
class MessagesTrashRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address or the special value `me` to reference the authenticated user.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the message to move to trash.")
class MessagesTrashRequest(StrictModel):
    """Moves a specified message to the trash folder. The message can be restored from trash before permanent deletion."""
    path: MessagesTrashRequestPath

# Operation: restore_message
class MessagesUntrashRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The email address of the user whose message should be restored. Use the special value `me` to refer to the authenticated user.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the message to restore from trash.")
class MessagesUntrashRequest(StrictModel):
    """Restores a message from the trash by removing it from the trash folder. The message will be returned to its previous labels or inbox."""
    path: MessagesUntrashRequestPath

# Operation: get_attachment
class MessagesAttachmentsGetRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The email address of the account owner. Use the special value `me` to refer to the authenticated user's account.")
    message_id: str = Field(default=..., validation_alias="messageId", serialization_alias="messageId", description="The unique identifier of the message containing the attachment.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the attachment to retrieve.")
class MessagesAttachmentsGetRequest(StrictModel):
    """Retrieves a specific attachment from a Gmail message. Use this to download or access attachment metadata by providing the message ID and attachment ID."""
    path: MessagesAttachmentsGetRequestPath

# Operation: get_auto_forwarding
class SettingsGetAutoForwardingRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The Gmail account identifier. Use the email address associated with the account, or use the special value \"me\" to refer to the authenticated user's account.")
class SettingsGetAutoForwardingRequest(StrictModel):
    """Retrieves the auto-forwarding configuration for the specified Gmail account. This includes the forwarding address and whether auto-forwarding is enabled."""
    path: SettingsGetAutoForwardingRequestPath

# Operation: update_auto_forwarding
class SettingsUpdateAutoForwardingRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address or 'me' to reference the authenticated user.")
class SettingsUpdateAutoForwardingRequestBody(StrictModel):
    disposition: Literal["dispositionUnspecified", "leaveInInbox", "archive", "trash", "markRead"] | None = Field(default=None, description="The action to take on messages after forwarding them to the target address.")
    email_address: str | None = Field(default=None, validation_alias="emailAddress", serialization_alias="emailAddress", description="The email address where incoming messages will be forwarded. This address must be verified in the account's forwarding addresses list.")
    enabled: bool | None = Field(default=None, description="Whether to enable automatic forwarding of all incoming mail to the specified email address.")
class SettingsUpdateAutoForwardingRequest(StrictModel):
    """Updates the auto-forwarding configuration for a Gmail account, allowing incoming messages to be automatically forwarded to a verified address. Requires domain-wide delegation authority for service account access."""
    path: SettingsUpdateAutoForwardingRequestPath
    body: SettingsUpdateAutoForwardingRequestBody | None = None

# Operation: get_imap_settings
class SettingsGetImapRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The Gmail account identifier. Use the special value 'me' to refer to the authenticated user, or provide the user's email address.")
class SettingsGetImapRequest(StrictModel):
    """Retrieves the IMAP settings for a Gmail account. This includes configuration details needed to connect to the account via IMAP protocol."""
    path: SettingsGetImapRequestPath

# Operation: update_imap_settings
class SettingsUpdateImapRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The Gmail user account identifier. Use 'me' to refer to the authenticated user, or provide the user's email address.")
class SettingsUpdateImapRequestBody(StrictModel):
    auto_expunge: bool | None = Field(default=None, validation_alias="autoExpunge", serialization_alias="autoExpunge", description="When enabled, Gmail will immediately expunge messages marked as deleted in IMAP. When disabled, Gmail waits for client confirmation before expunging.")
    enabled: bool | None = Field(default=None, description="Controls whether IMAP access is enabled for this Gmail account.")
    expunge_behavior: Literal["expungeBehaviorUnspecified", "archive", "trash", "deleteForever"] | None = Field(default=None, validation_alias="expungeBehavior", serialization_alias="expungeBehavior", description="Specifies the action to perform on messages when they are marked as deleted and expunged from the last visible IMAP folder.")
    max_folder_size: int | None = Field(default=None, validation_alias="maxFolderSize", serialization_alias="maxFolderSize", description="Optional limit on the maximum number of messages an IMAP folder can contain. Valid values are 0 (no limit), 1000, 2000, 5000, or 10000.", json_schema_extra={'format': 'int32'})
class SettingsUpdateImapRequest(StrictModel):
    """Updates IMAP configuration settings for a Gmail account, including enablement status, auto-expunge behavior, and folder size limits."""
    path: SettingsUpdateImapRequestPath
    body: SettingsUpdateImapRequestBody | None = None

# Operation: get_language_settings
class SettingsGetLanguageRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The Gmail user's email address, or use the special value \"me\" to refer to the authenticated user making the request.")
class SettingsGetLanguageRequest(StrictModel):
    """Retrieves the language settings for a Gmail user account. Returns the preferred language configuration for the specified user."""
    path: SettingsGetLanguageRequestPath

# Operation: update_language_setting
class SettingsUpdateLanguageRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address or 'me' to reference the authenticated user.")
class SettingsUpdateLanguageRequestBody(StrictModel):
    display_language: str | None = Field(default=None, validation_alias="displayLanguage", serialization_alias="displayLanguage", description="The language to display Gmail in, formatted as an RFC 3066 Language Tag. Gmail automatically selects the closest supported variant if the requested language is unavailable on the client.")
class SettingsUpdateLanguageRequest(StrictModel):
    """Updates the display language for Gmail. The saved language may differ from the requested value if Gmail automatically substitutes a supported variant."""
    path: SettingsUpdateLanguageRequestPath
    body: SettingsUpdateLanguageRequestBody | None = None

# Operation: get_pop_settings
class SettingsGetPopRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The Gmail user account identifier. Use the special value \"me\" to refer to the authenticated user, or provide a specific email address.")
class SettingsGetPopRequest(StrictModel):
    """Retrieves POP (Post Office Protocol) settings for a Gmail account. Returns the current POP configuration including whether POP is enabled and related preferences."""
    path: SettingsGetPopRequestPath

# Operation: update_pop_settings
class SettingsUpdatePopRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value \"me\" to refer to the authenticated user.")
class SettingsUpdatePopRequestBody(StrictModel):
    access_window: Literal["accessWindowUnspecified", "disabled", "fromNowOn", "allMail"] | None = Field(default=None, validation_alias="accessWindow", serialization_alias="accessWindow", description="The range of messages accessible via POP, controlling which messages can be retrieved.")
    disposition: Literal["dispositionUnspecified", "leaveInInbox", "archive", "trash", "markRead"] | None = Field(default=None, description="The action to perform on a message after it has been fetched via POP.")
class SettingsUpdatePopRequest(StrictModel):
    """Updates POP (Post Office Protocol) settings for a Gmail account, including message accessibility range and post-fetch actions."""
    path: SettingsUpdatePopRequestPath
    body: SettingsUpdatePopRequestBody | None = None

# Operation: get_vacation_settings
class SettingsGetVacationRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The Gmail user account identifier. Use 'me' to refer to the authenticated user, or provide a specific email address.")
class SettingsGetVacationRequest(StrictModel):
    """Retrieves the vacation responder settings for a Gmail account, including whether auto-reply is enabled and the message content."""
    path: SettingsGetVacationRequestPath

# Operation: update_vacation_responder
class SettingsUpdateVacationRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address or 'me' to refer to the authenticated user.")
class SettingsUpdateVacationRequestBody(StrictModel):
    enable_auto_reply: bool | None = Field(default=None, validation_alias="enableAutoReply", serialization_alias="enableAutoReply", description="Enable or disable automatic vacation replies to incoming messages.")
    end_time: str | None = Field(default=None, validation_alias="endTime", serialization_alias="endTime", description="End time for sending auto-replies as milliseconds since epoch. Auto-replies will only be sent to messages received before this time. Must be after startTime if both are specified.", json_schema_extra={'format': 'int64'})
    response_body_html: str | None = Field(default=None, validation_alias="responseBodyHtml", serialization_alias="responseBodyHtml", description="Vacation response message in HTML format. Gmail will sanitize the HTML before storing. Takes precedence over plain text if both are provided.")
    response_subject: str | None = Field(default=None, validation_alias="responseSubject", serialization_alias="responseSubject", description="Optional subject line prefix for vacation responses. Either this or responseBodyHtml must be non-empty to enable auto-replies.")
    restrict_to_contacts: bool | None = Field(default=None, validation_alias="restrictToContacts", serialization_alias="restrictToContacts", description="Restrict vacation replies to contacts in the user's contact list only.")
    restrict_to_domain: bool | None = Field(default=None, validation_alias="restrictToDomain", serialization_alias="restrictToDomain", description="Restrict vacation replies to recipients within the user's domain. Only available for Google Workspace users.")
    start_time: str | None = Field(default=None, validation_alias="startTime", serialization_alias="startTime", description="Start time for sending auto-replies as milliseconds since epoch. Auto-replies will only be sent to messages received after this time. Must be before endTime if both are specified.", json_schema_extra={'format': 'int64'})
class SettingsUpdateVacationRequest(StrictModel):
    """Configure Gmail's vacation auto-reply settings, including response message, timing window, and recipient restrictions. At least one of responseSubject or responseBodyHtml must be provided to enable auto-replies."""
    path: SettingsUpdateVacationRequestPath
    body: SettingsUpdateVacationRequestBody | None = None

# Operation: list_cse_identities
class SettingsCseIdentitiesListRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's primary email address. Use the special value `me` to refer to the authenticated user.")
class SettingsCseIdentitiesListRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="Maximum number of identities to return per page. If not specified, defaults to 20 entries.")
class SettingsCseIdentitiesListRequest(StrictModel):
    """Retrieves all client-side encrypted identities for an authenticated user. Administrators with domain-wide delegation can manage identities for their organization, while users managing their own identities require hardware key encryption to be enabled."""
    path: SettingsCseIdentitiesListRequestPath
    query: SettingsCseIdentitiesListRequestQuery | None = None

# Operation: create_cse_identity
class SettingsCseIdentitiesCreateRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The requester's primary email address. Use the special value `me` to indicate the authenticated user.")
class SettingsCseIdentitiesCreateRequestBody(StrictModel):
    email_address: str | None = Field(default=None, validation_alias="emailAddress", serialization_alias="emailAddress", description="The email address for the sending identity. Must be the primary email address of the authenticated user.")
class SettingsCseIdentitiesCreateRequest(StrictModel):
    """Creates and configures a client-side encryption identity for sending encrypted mail from a user account. The S/MIME certificate is published to a shared domain-wide directory, enabling secure communication within a Google Workspace organization."""
    path: SettingsCseIdentitiesCreateRequestPath
    body: SettingsCseIdentitiesCreateRequestBody | None = None

# Operation: get_cse_identity
class SettingsCseIdentitiesGetRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The requester's primary email address. Use the special value `me` to refer to the authenticated user.")
    cse_email_address: str = Field(default=..., validation_alias="cseEmailAddress", serialization_alias="cseEmailAddress", description="The primary email address associated with the client-side encryption identity configuration to retrieve.")
class SettingsCseIdentitiesGetRequest(StrictModel):
    """Retrieves a client-side encryption identity configuration for a specified email address. Administrators require service account with domain-wide delegation authority, while users require hardware key encryption to be enabled."""
    path: SettingsCseIdentitiesGetRequestPath

# Operation: delete_cse_identity
class SettingsCseIdentitiesDeleteRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's primary email address. Use the special value `me` to refer to the authenticated user.")
    cse_email_address: str = Field(default=..., validation_alias="cseEmailAddress", serialization_alias="cseEmailAddress", description="The primary email address associated with the client-side encryption identity to be deleted.")
class SettingsCseIdentitiesDeleteRequest(StrictModel):
    """Permanently deletes a client-side encryption identity, preventing further use for sending encrypted messages. The identity cannot be restored; create a new identity with the same configuration if needed."""
    path: SettingsCseIdentitiesDeleteRequestPath

# Operation: update_cse_identity_keypair
class SettingsCseIdentitiesPatchRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user identifier. Use the special value `me` to refer to the authenticated user, or provide the user's primary email address.")
    email_address: str = Field(default=..., validation_alias="emailAddress", serialization_alias="emailAddress", description="The email address of the client-side encryption identity to update.")
class SettingsCseIdentitiesPatchRequestBody(StrictModel):
    email_address2: str | None = Field(default=None, validation_alias="emailAddress", serialization_alias="emailAddress", description="The email address for the sending identity. Must be the primary email address of the authenticated user.")
class SettingsCseIdentitiesPatchRequest(StrictModel):
    """Associates a new key pair with an existing client-side encryption identity. The updated key pair must validate against Google's S/MIME certificate profiles. Requires either domain-wide delegation authority for administrators or hardware key encryption enabled for individual users."""
    path: SettingsCseIdentitiesPatchRequestPath
    body: SettingsCseIdentitiesPatchRequestBody | None = None

# Operation: list_encryption_keypairs
class SettingsCseKeypairsListRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's primary email address. Use the special value `me` to refer to the authenticated user.")
class SettingsCseKeypairsListRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="Maximum number of key pairs to return per page. If not specified, defaults to 20 entries.")
class SettingsCseKeypairsListRequest(StrictModel):
    """Retrieves all client-side encryption key pairs for a user. Administrators with domain-wide delegation can manage keypairs for users in their organization, while individual users require hardware key encryption to be enabled."""
    path: SettingsCseKeypairsListRequestPath
    query: SettingsCseKeypairsListRequestQuery | None = None

# Operation: create_cse_keypair
class SettingsCseKeypairsCreateRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's primary email address. Use the special value `me` to refer to the authenticated user.")
class SettingsCseKeypairsCreateRequestBody(StrictModel):
    pkcs7: str | None = Field(default=None, description="The public key and its certificate chain in PKCS#7 format with PEM encoding and ASCII armor.")
    private_key_metadata: list[CsePrivateKeyMetadata] | None = Field(default=None, validation_alias="privateKeyMetadata", serialization_alias="privateKeyMetadata", description="An ordered array of metadata objects for instances of this key pair's private key. Order significance and item structure should follow the API specification.")
class SettingsCseKeypairsCreateRequest(StrictModel):
    """Creates and uploads a client-side encryption S/MIME public key certificate chain and private key metadata for Gmail. Requires either domain-wide delegation authority for administrators or hardware key encryption enabled for individual users."""
    path: SettingsCseKeypairsCreateRequestPath
    body: SettingsCseKeypairsCreateRequestBody | None = None

# Operation: disable_cse_keypair
class SettingsCseKeypairsDisableRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's primary email address. Use the special value 'me' to refer to the authenticated user.")
    key_pair_id: str = Field(default=..., validation_alias="keyPairId", serialization_alias="keyPairId", description="The unique identifier of the key pair to disable.")
class SettingsCseKeypairsDisableRequest(StrictModel):
    """Disables a client-side encryption key pair, preventing the user from decrypting incoming CSE messages or signing outgoing CSE mail. The key pair can be re-enabled later using enable_cse_keypair, or permanently deleted after 30 days using obliterate_cse_keypair."""
    path: SettingsCseKeypairsDisableRequestPath

# Operation: enable_encryption_keypair
class SettingsCseKeypairsEnableRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's primary email address. Use the special value `me` to refer to the authenticated user.")
    key_pair_id: str = Field(default=..., validation_alias="keyPairId", serialization_alias="keyPairId", description="The unique identifier of the key pair to reactivate.")
class SettingsCseKeypairsEnableRequest(StrictModel):
    """Reactivates a previously disabled client-side encryption key pair for use with associated encryption identities. Administrators require service account with domain-wide delegation authority; end users require hardware key encryption to be enabled."""
    path: SettingsCseKeypairsEnableRequestPath

# Operation: get_encryption_keypair
class SettingsCseKeypairsGetRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The email address of the user whose key pair is being retrieved. Use the special value `me` to refer to the authenticated user.")
    key_pair_id: str = Field(default=..., validation_alias="keyPairId", serialization_alias="keyPairId", description="The unique identifier of the encryption key pair to retrieve.")
class SettingsCseKeypairsGetRequest(StrictModel):
    """Retrieves a client-side encryption key pair for Gmail. Administrators require service account authorization with domain-wide delegation, while users must have hardware key encryption enabled."""
    path: SettingsCseKeypairsGetRequestPath

# Operation: obliterate_cse_keypair
class SettingsCseKeypairsObliterateRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The email address of the user whose key pair will be obliterated. Use the special value `me` to refer to the authenticated user.")
    key_pair_id: str = Field(default=..., validation_alias="keyPairId", serialization_alias="keyPairId", description="The unique identifier of the key pair to permanently delete.")
class SettingsCseKeypairsObliterateRequest(StrictModel):
    """Permanently and immediately deletes a client-side encryption key pair. The key pair must be disabled for at least 30 days before obliteration. Once obliterated, all messages encrypted with this key become permanently inaccessible to all users."""
    path: SettingsCseKeypairsObliterateRequestPath

# Operation: list_delegates
class SettingsDelegatesListRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The Gmail user account identifier. Use the special value 'me' to refer to the authenticated user, or provide the user's full email address.")
class SettingsDelegatesListRequest(StrictModel):
    """Retrieves the list of delegates for the specified Gmail account. This operation requires service account credentials with domain-wide delegation authority."""
    path: SettingsDelegatesListRequestPath

# Operation: add_delegate
class SettingsDelegatesCreateRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The email address of the user whose delegates are being managed. Use the special value 'me' to refer to the authenticated user.")
class SettingsDelegatesCreateRequestBody(StrictModel):
    delegate_email: str | None = Field(default=None, validation_alias="delegateEmail", serialization_alias="delegateEmail", description="The primary email address of the delegate to add. The delegate must be a member of the same Google Workspace organization as the delegator.")
class SettingsDelegatesCreateRequest(StrictModel):
    """Adds a delegate to a user's Gmail account with immediate acceptance status, bypassing email verification. The delegate must be a member of the same Google Workspace organization and referred to by their primary email address."""
    path: SettingsDelegatesCreateRequestPath
    body: SettingsDelegatesCreateRequestBody | None = None

# Operation: get_delegate
class SettingsDelegatesGetRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The email address of the user whose delegates are being queried. Use the special value 'me' to refer to the authenticated user.")
    delegate_email: str = Field(default=..., validation_alias="delegateEmail", serialization_alias="delegateEmail", description="The primary email address of the delegate whose relationship details should be retrieved. Email aliases cannot be used; the primary email address is required.")
class SettingsDelegatesGetRequest(StrictModel):
    """Retrieves the delegate relationship for a specified email address. This operation requires service account clients with domain-wide authority and uses the delegate's primary email address (not aliases)."""
    path: SettingsDelegatesGetRequestPath

# Operation: remove_delegate
class SettingsDelegatesDeleteRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The email address of the Gmail account owner. Use the special value 'me' to refer to the authenticated user.")
    delegate_email: str = Field(default=..., validation_alias="delegateEmail", serialization_alias="delegateEmail", description="The primary email address of the delegate to be removed from the account.")
class SettingsDelegatesDeleteRequest(StrictModel):
    """Removes a delegate from the user's Gmail account and revokes any associated verification. This operation requires domain-wide authority and uses the delegate's primary email address."""
    path: SettingsDelegatesDeleteRequestPath

# Operation: list_filters
class SettingsFiltersListRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The Gmail user account identifier. Use the special value 'me' to refer to the authenticated user, or provide a specific email address.")
class SettingsFiltersListRequest(StrictModel):
    """Retrieves all message filters configured for a Gmail account. Filters define rules for automatically organizing, labeling, or processing incoming messages."""
    path: SettingsFiltersListRequestPath

# Operation: create_filter
class SettingsFiltersCreateRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address or 'me' to refer to the authenticated user.")
class SettingsFiltersCreateRequestBodyAction(StrictModel):
    add_label_ids: list[str] | None = Field(default=None, validation_alias="addLabelIds", serialization_alias="addLabelIds", description="List of label IDs to automatically add to messages matching this filter.")
    forward: str | None = Field(default=None, validation_alias="forward", serialization_alias="forward", description="Email address to automatically forward matching messages to.")
    remove_label_ids: list[str] | None = Field(default=None, validation_alias="removeLabelIds", serialization_alias="removeLabelIds", description="List of label IDs to automatically remove from messages matching this filter.")
class SettingsFiltersCreateRequestBodyCriteria(StrictModel):
    exclude_chats: bool | None = Field(default=None, validation_alias="excludeChats", serialization_alias="excludeChats", description="Whether to exclude chat messages from this filter.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="The sender's display name or email address to match against. Matching is case-insensitive.")
    has_attachment: bool | None = Field(default=None, validation_alias="hasAttachment", serialization_alias="hasAttachment", description="Whether the message must have one or more attachments to match this filter.")
    size_comparison: Literal["unspecified", "smaller", "larger"] | None = Field(default=None, validation_alias="sizeComparison", serialization_alias="sizeComparison", description="The comparison operator for message size in bytes relative to the size field.")
    subject: str | None = Field(default=None, validation_alias="subject", serialization_alias="subject", description="Case-insensitive phrase to match in the message subject line. Leading and trailing whitespace is trimmed, and consecutive spaces are collapsed.")
    to: str | None = Field(default=None, validation_alias="to", serialization_alias="to", description="The recipient's display name or email address to match against. Matches recipients in 'to', 'cc', and 'bcc' fields. The local part of an email address (before @) is sufficient for matching. Matching is case-insensitive.")
class SettingsFiltersCreateRequestBody(StrictModel):
    action: SettingsFiltersCreateRequestBodyAction | None = None
    criteria: SettingsFiltersCreateRequestBodyCriteria | None = None
class SettingsFiltersCreateRequest(StrictModel):
    """Creates an email filter to automatically organize, forward, or modify messages based on specified criteria. Note: A maximum of 1,000 filters can be created per user."""
    path: SettingsFiltersCreateRequestPath
    body: SettingsFiltersCreateRequestBody | None = None

# Operation: get_filter
class SettingsFiltersGetRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The Gmail account identifier. Use 'me' to refer to the authenticated user, or provide the user's email address.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the filter to retrieve.")
class SettingsFiltersGetRequest(StrictModel):
    """Retrieves a specific Gmail filter by its ID. Use this to fetch the configuration and rules of an existing filter."""
    path: SettingsFiltersGetRequestPath

# Operation: delete_filter
class SettingsFiltersDeleteRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The email address of the user whose filter will be deleted. Use the special value \"me\" to refer to the authenticated user.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the filter to be deleted.")
class SettingsFiltersDeleteRequest(StrictModel):
    """Permanently deletes a specified Gmail filter. This action is immediate and cannot be undone."""
    path: SettingsFiltersDeleteRequestPath

# Operation: list_forwarding_addresses
class SettingsForwardingAddressesListRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The Gmail account identifier. Use the authenticated user's email address, or specify 'me' to refer to the currently authenticated user.")
class SettingsForwardingAddressesListRequest(StrictModel):
    """Retrieves all forwarding addresses configured for the specified Gmail account. Forwarding addresses are alternative email addresses where incoming messages can be automatically sent."""
    path: SettingsForwardingAddressesListRequestPath

# Operation: create_forwarding_address
class SettingsForwardingAddressesCreateRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The Gmail user account identifier. Use the user's email address or the special value 'me' to refer to the authenticated user.")
class SettingsForwardingAddressesCreateRequestBody(StrictModel):
    forwarding_email: str | None = Field(default=None, validation_alias="forwardingEmail", serialization_alias="forwardingEmail", description="The email address to which messages will be forwarded. This address will receive a verification message if ownership confirmation is required.")
class SettingsForwardingAddressesCreateRequest(StrictModel):
    """Creates a forwarding address for a Gmail account to automatically redirect incoming messages. If ownership verification is required, a verification message will be sent to the recipient; otherwise, the address is immediately accepted. This operation requires service account credentials with domain-wide delegation authority."""
    path: SettingsForwardingAddressesCreateRequestPath
    body: SettingsForwardingAddressesCreateRequestBody | None = None

# Operation: get_forwarding_address
class SettingsForwardingAddressesGetRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The Gmail account identifier. Use the special value 'me' to refer to the authenticated user's account, or provide the user's full email address.")
    forwarding_email: str = Field(default=..., validation_alias="forwardingEmail", serialization_alias="forwardingEmail", description="The email address for which forwarding configuration should be retrieved.")
class SettingsForwardingAddressesGetRequest(StrictModel):
    """Retrieves the configuration details for a specified forwarding address associated with a Gmail account. Use this to view forwarding settings for a particular email address."""
    path: SettingsForwardingAddressesGetRequestPath

# Operation: delete_forwarding_address
class SettingsForwardingAddressesDeleteRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address or 'me' to reference the authenticated user.")
    forwarding_email: str = Field(default=..., validation_alias="forwardingEmail", serialization_alias="forwardingEmail", description="The forwarding email address to delete.")
class SettingsForwardingAddressesDeleteRequest(StrictModel):
    """Deletes a forwarding address and revokes any associated verification. This operation requires service account credentials with domain-wide delegation authority."""
    path: SettingsForwardingAddressesDeleteRequestPath

# Operation: list_send_as_aliases
class SettingsSendAsListRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The Gmail account identifier. Use 'me' to reference the authenticated user's account.")
class SettingsSendAsListRequest(StrictModel):
    """Retrieves all send-as aliases configured for the specified Gmail account, including the primary email address and any custom 'from' aliases."""
    path: SettingsSendAsListRequestPath

# Operation: create_send_as_alias
class SettingsSendAsCreateRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The Gmail user's email address or 'me' to reference the authenticated user.")
class SettingsSendAsCreateRequestBodySmtpMsa(StrictModel):
    host: str | None = Field(default=None, validation_alias="host", serialization_alias="host", description="The SMTP server hostname for outgoing mail validation and delivery. Required if configuring SMTP MSA settings.")
    password: str | None = Field(default=None, validation_alias="password", serialization_alias="password", description="The password for SMTP authentication. This write-only field is never returned in responses.")
    port: int | None = Field(default=None, validation_alias="port", serialization_alias="port", description="The SMTP server port number for outgoing mail. Required if configuring SMTP MSA settings.", json_schema_extra={'format': 'int32'})
    security_mode: Literal["securityModeUnspecified", "none", "ssl", "starttls"] | None = Field(default=None, validation_alias="securityMode", serialization_alias="securityMode", description="The security protocol for SMTP communication. Required if configuring SMTP MSA settings.")
    username: str | None = Field(default=None, validation_alias="username", serialization_alias="username", description="The username for SMTP authentication. This write-only field is never returned in responses.")
class SettingsSendAsCreateRequestBody(StrictModel):
    is_default: bool | None = Field(default=None, validation_alias="isDefault", serialization_alias="isDefault", description="Whether to set this address as the default 'From:' address for new messages and auto-replies. Only 'true' can be written; setting this to 'true' automatically sets the previous default address to 'false'.")
    reply_to_address: str | None = Field(default=None, validation_alias="replyToAddress", serialization_alias="replyToAddress", description="Optional email address to include in the 'Reply-To:' header for messages sent using this alias. Leave empty to omit the 'Reply-To:' header.")
    signature: str | None = Field(default=None, description="Optional HTML signature to append to new emails composed with this alias in Gmail's web interface. Gmail will sanitize the HTML before saving.")
    treat_as_alias: bool | None = Field(default=None, validation_alias="treatAsAlias", serialization_alias="treatAsAlias", description="Whether Gmail should treat this address as an alias for the user's primary email address. This setting applies only to custom 'from' aliases.")
    display_name: dict | None = Field(default=None, validation_alias="displayName", serialization_alias="displayName", description="A name that appears in the \"From:\" header for mail sent using this alias. For custom \"from\" addresses, when this is empty, Gmail will populate the \"From:\" header with the name that is used for the primary address associated with the account. If the admin has disabled the ability for users to update their name format, requests to update this field for the primary login will silently fail.")
    send_as_email: str | None = Field(default=None, validation_alias="sendAsEmail", serialization_alias="sendAsEmail", description="The email address that appears in the \"From:\" header for mail sent using this alias. This is read-only for all operations except create.")
    smtp_msa: SettingsSendAsCreateRequestBodySmtpMsa | None = Field(default=None, validation_alias="smtpMsa", serialization_alias="smtpMsa")
class SettingsSendAsCreateRequest(StrictModel):
    """Creates a custom 'from' send-as alias for a Gmail account, with optional SMTP configuration validation and ownership verification. This operation is restricted to service accounts with domain-wide delegation authority."""
    path: SettingsSendAsCreateRequestPath
    body: SettingsSendAsCreateRequestBody | None = None

# Operation: get_send_as_alias
class SettingsSendAsGetRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value 'me' to refer to the authenticated user.")
    send_as_email: str = Field(default=..., validation_alias="sendAsEmail", serialization_alias="sendAsEmail", description="The email address of the send-as alias to retrieve.")
class SettingsSendAsGetRequest(StrictModel):
    """Retrieves a specific send-as alias configuration for a user. Returns an HTTP 404 error if the specified email address is not configured as a send-as alias."""
    path: SettingsSendAsGetRequestPath

# Operation: update_send_as_alias
class SettingsSendAsUpdateRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The Gmail user's email address. Use the special value 'me' to refer to the authenticated user.")
    send_as_email: str = Field(default=..., validation_alias="sendAsEmail", serialization_alias="sendAsEmail", description="The email address of the send-as alias to be updated.")
class SettingsSendAsUpdateRequestBodySmtpMsa(StrictModel):
    host: str | None = Field(default=None, validation_alias="host", serialization_alias="host", description="The hostname of the SMTP server used for sending mail through this alias.")
    password: str | None = Field(default=None, validation_alias="password", serialization_alias="password", description="The password for SMTP authentication. This write-only field is used only during creation or updates and is never returned in responses.")
    port: int | None = Field(default=None, validation_alias="port", serialization_alias="port", description="The port number of the SMTP server.", json_schema_extra={'format': 'int32'})
    security_mode: Literal["securityModeUnspecified", "none", "ssl", "starttls"] | None = Field(default=None, validation_alias="securityMode", serialization_alias="securityMode", description="The security protocol for SMTP communication.")
    username: str | None = Field(default=None, validation_alias="username", serialization_alias="username", description="The username for SMTP authentication. This write-only field is used only during creation or updates and is never returned in responses.")
class SettingsSendAsUpdateRequestBody(StrictModel):
    send_as_email: str | None = Field(default=None, validation_alias="sendAsEmail", serialization_alias="sendAsEmail", description="The email address displayed in the 'From:' header for messages sent using this alias. This field is read-only and cannot be modified after creation.")
    display_name: str | None = Field(default=None, validation_alias="displayName", serialization_alias="displayName", description="The display name shown in the 'From:' header for messages sent using this alias. If empty for custom addresses, Gmail will use the primary account's name. Updates to this field may be silently ignored if the admin has restricted name format changes.")
    is_default: bool | None = Field(default=None, validation_alias="isDefault", serialization_alias="isDefault", description="Whether this alias is the default 'From:' address for new messages and auto-replies. Only 'true' can be written; setting this to true automatically sets the previous default address to false. Every Gmail account must have exactly one default send-as address.")
    reply_to_address: str | None = Field(default=None, validation_alias="replyToAddress", serialization_alias="replyToAddress", description="An optional email address to include in the 'Reply-To:' header for messages sent using this alias. Leave empty to omit the 'Reply-To:' header.")
    signature: str | None = Field(default=None, description="An optional HTML signature appended to new emails composed with this alias in Gmail's web interface. Gmail will sanitize the HTML before saving.")
    treat_as_alias: bool | None = Field(default=None, validation_alias="treatAsAlias", serialization_alias="treatAsAlias", description="Whether Gmail should treat this address as an alias for the user's primary email address. This setting applies only to custom 'from' aliases.")
    smtp_msa: SettingsSendAsUpdateRequestBodySmtpMsa | None = Field(default=None, validation_alias="smtpMsa", serialization_alias="smtpMsa")
class SettingsSendAsUpdateRequest(StrictModel):
    """Updates a send-as alias configuration for a Gmail account, including display name, reply-to address, and optional HTML signature. Service accounts with domain-wide delegation can update non-primary addresses; standard users can only modify their own aliases."""
    path: SettingsSendAsUpdateRequestPath
    body: SettingsSendAsUpdateRequestBody | None = None

# Operation: update_send_as_alias_partial
class SettingsSendAsPatchRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The Gmail account identifier. Use 'me' to refer to the authenticated user, or provide a specific email address.")
    send_as_email: str = Field(default=..., validation_alias="sendAsEmail", serialization_alias="sendAsEmail", description="The email address of the send-as alias to update.")
class SettingsSendAsPatchRequestBodySmtpMsa(StrictModel):
    host: str | None = Field(default=None, validation_alias="host", serialization_alias="host", description="The hostname of the SMTP server used to send mail through this alias.")
    password: str | None = Field(default=None, validation_alias="password", serialization_alias="password", description="The password for SMTP authentication. This write-only field is never returned in responses and must be provided when configuring SMTP settings.")
    port: int | None = Field(default=None, validation_alias="port", serialization_alias="port", description="The port number of the SMTP server. Common values are 25, 465, or 587 depending on the security mode.", json_schema_extra={'format': 'int32'})
    security_mode: Literal["securityModeUnspecified", "none", "ssl", "starttls"] | None = Field(default=None, validation_alias="securityMode", serialization_alias="securityMode", description="The security protocol for SMTP communication. Determines how the connection to the SMTP server is encrypted or secured.")
    username: str | None = Field(default=None, validation_alias="username", serialization_alias="username", description="The username for SMTP authentication. This write-only field is never returned in responses and must be provided when configuring SMTP settings.")
class SettingsSendAsPatchRequestBody(StrictModel):
    send_as_email: str | None = Field(default=None, validation_alias="sendAsEmail", serialization_alias="sendAsEmail", description="The email address displayed in the 'From:' header for messages sent using this alias. This field is read-only for updates and can only be set during alias creation.")
    display_name: str | None = Field(default=None, validation_alias="displayName", serialization_alias="displayName", description="The display name shown in the 'From:' header for messages sent using this alias. If empty, Gmail uses the primary account's name. Updates may be silently ignored if the admin has restricted name format changes.")
    is_default: bool | None = Field(default=None, validation_alias="isDefault", serialization_alias="isDefault", description="Set to true to make this the default 'From:' address for new messages and auto-replies. Only true is a valid value for updates; setting this true automatically sets the previous default to false.")
    reply_to_address: str | None = Field(default=None, validation_alias="replyToAddress", serialization_alias="replyToAddress", description="An optional email address to include in the 'Reply-To:' header for messages sent using this alias. Leave empty to omit the Reply-To header.")
    signature: str | None = Field(default=None, description="An optional HTML signature appended to new emails composed with this alias in Gmail's web interface. This signature is not added to replies or forwarded messages.")
    treat_as_alias: bool | None = Field(default=None, validation_alias="treatAsAlias", serialization_alias="treatAsAlias", description="Whether Gmail should treat this address as an alias for the user's primary email address. This setting only applies to custom 'from' aliases and affects how Gmail handles replies and threading.")
    smtp_msa: SettingsSendAsPatchRequestBodySmtpMsa | None = Field(default=None, validation_alias="smtpMsa", serialization_alias="smtpMsa")
class SettingsSendAsPatchRequest(StrictModel):
    """Partially update a send-as alias configuration for a Gmail account. Use this to modify display name, default status, reply-to address, signature, SMTP settings, or alias treatment without replacing the entire resource."""
    path: SettingsSendAsPatchRequestPath
    body: SettingsSendAsPatchRequestBody | None = None

# Operation: delete_send_as_alias
class SettingsSendAsDeleteRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The Gmail user account identifier. Use the special value 'me' to reference the authenticated user, or provide the user's email address.")
    send_as_email: str = Field(default=..., validation_alias="sendAsEmail", serialization_alias="sendAsEmail", description="The email address of the send-as alias to be deleted.")
class SettingsSendAsDeleteRequest(StrictModel):
    """Deletes a send-as alias for a Gmail account and revokes any associated verification. This operation requires service account credentials with domain-wide delegation authority."""
    path: SettingsSendAsDeleteRequestPath

# Operation: verify_send_as_alias
class SettingsSendAsVerifyRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value 'me' to refer to the authenticated user.")
    send_as_email: str = Field(default=..., validation_alias="sendAsEmail", serialization_alias="sendAsEmail", description="The send-as alias email address that requires verification.")
class SettingsSendAsVerifyRequest(StrictModel):
    """Sends a verification email to a send-as alias address to confirm ownership. The alias must have a pending verification status and requires service account with domain-wide delegation authority."""
    path: SettingsSendAsVerifyRequestPath

# Operation: get_smime_info
class SettingsSendAsSmimeInfoGetRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user.")
    send_as_email: str = Field(default=..., validation_alias="sendAsEmail", serialization_alias="sendAsEmail", description="The email address that appears in the From header for messages sent using this send-as alias.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The immutable identifier for the S/MIME configuration.")
class SettingsSendAsSmimeInfoGetRequest(StrictModel):
    """Retrieves the S/MIME configuration for a specified send-as alias. This allows you to access the details of a specific S/MIME certificate associated with an email alias."""
    path: SettingsSendAsSmimeInfoGetRequestPath

# Operation: delete_smime_config
class SettingsSendAsSmimeInfoDeleteRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user.")
    send_as_email: str = Field(default=..., validation_alias="sendAsEmail", serialization_alias="sendAsEmail", description="The email address that appears in the From header for messages sent using this send-as alias.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The immutable identifier for the S/MIME configuration to delete.")
class SettingsSendAsSmimeInfoDeleteRequest(StrictModel):
    """Deletes the S/MIME configuration for a specified send-as alias. This removes the security certificate associated with the alias used for signing and encrypting outgoing emails."""
    path: SettingsSendAsSmimeInfoDeleteRequestPath

# Operation: list_smime_configs
class SettingsSendAsSmimeInfoListRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user.")
    send_as_email: str = Field(default=..., validation_alias="sendAsEmail", serialization_alias="sendAsEmail", description="The email address configured as a send-as alias. This is the address that appears in the From header for emails sent using this alias.")
class SettingsSendAsSmimeInfoListRequest(StrictModel):
    """Lists all S/MIME configurations for a specified send-as alias. S/MIME configs define the certificates and encryption settings used when sending emails from this alias."""
    path: SettingsSendAsSmimeInfoListRequestPath

# Operation: upload_smime_certificate
class SettingsSendAsSmimeInfoInsertRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user.")
    send_as_email: str = Field(default=..., validation_alias="sendAsEmail", serialization_alias="sendAsEmail", description="The email address that will appear in the From header for messages sent using this S/MIME alias.")
class SettingsSendAsSmimeInfoInsertRequestBody(StrictModel):
    encrypted_key_password: str | None = Field(default=None, validation_alias="encryptedKeyPassword", serialization_alias="encryptedKeyPassword", description="Password for the encrypted private key, required if the PKCS#12 certificate is password-protected.")
    expiration: str | None = Field(default=None, description="Certificate expiration timestamp in milliseconds since epoch (Unix time).", json_schema_extra={'format': 'int64'})
    is_default: bool | None = Field(default=None, validation_alias="isDefault", serialization_alias="isDefault", description="Whether to set this S/MIME certificate as the default for this send-as address.")
    pkcs12: str | None = Field(default=None, description="The S/MIME certificate in PKCS#12 format. Must contain a single private/public key pair and certificate chain. The private key may be encrypted; if so, provide the password in encryptedKeyPassword.", json_schema_extra={'format': 'byte'})
class SettingsSendAsSmimeInfoInsertRequest(StrictModel):
    """Upload and configure an S/MIME certificate for a send-as alias. The certificate must be provided in PKCS#12 format containing a private/public key pair and certificate chain."""
    path: SettingsSendAsSmimeInfoInsertRequestPath
    body: SettingsSendAsSmimeInfoInsertRequestBody | None = None

# Operation: set_default_smime_config
class SettingsSendAsSmimeInfoSetDefaultRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user.")
    send_as_email: str = Field(default=..., validation_alias="sendAsEmail", serialization_alias="sendAsEmail", description="The email address that appears in the From header for mail sent using this send-as alias.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The immutable identifier for the S/MIME configuration to set as default.")
class SettingsSendAsSmimeInfoSetDefaultRequest(StrictModel):
    """Sets the default S/MIME configuration for the specified send-as alias. This determines which S/MIME certificate will be used by default when sending emails from this alias."""
    path: SettingsSendAsSmimeInfoSetDefaultRequestPath

# Operation: get_thread
class ThreadsGetRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The email address of the user whose thread should be retrieved. Use the special value `me` to refer to the authenticated user.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the thread to retrieve.")
class ThreadsGetRequestQuery(StrictModel):
    format_: Literal["full", "metadata", "minimal"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="The format in which to return thread messages. Controls the level of detail included in the response.")
    metadata_headers: list[str] | None = Field(default=None, validation_alias="metadataHeaders", serialization_alias="metadataHeaders", description="When format is set to metadata, specify which email headers to include in the response. Headers should be provided as an array of header names.")
class ThreadsGetRequest(StrictModel):
    """Retrieves a specific email thread by ID. Returns thread messages in the requested format with optional filtering of metadata headers."""
    path: ThreadsGetRequestPath
    query: ThreadsGetRequestQuery | None = None

# Operation: delete_thread
class ThreadsDeleteRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The email address of the user whose thread will be deleted. Use the special value `me` to refer to the authenticated user.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the thread to delete.")
class ThreadsDeleteRequest(StrictModel):
    """Permanently deletes a thread and all messages within it. This action cannot be undone; consider using trash_thread as a safer alternative."""
    path: ThreadsDeleteRequestPath

# Operation: list_threads
class ThreadsListRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user.")
class ThreadsListRequestQuery(StrictModel):
    include_spam_trash: bool | None = Field(default=None, validation_alias="includeSpamTrash", serialization_alias="includeSpamTrash", description="Include threads from the SPAM and TRASH folders in the results.")
    label_ids: list[str] | None = Field(default=None, validation_alias="labelIds", serialization_alias="labelIds", description="Filter results to only return threads that have all of the specified label IDs. Provide as an array of label ID strings.")
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="Maximum number of threads to return in the response.", le=500)
    q: str | None = Field(default=None, description="Filter results using Gmail search query syntax (e.g., sender, subject, date filters, read status). Not supported when using the gmail.metadata scope.")
class ThreadsListRequest(StrictModel):
    """Retrieves a list of message threads from the user's mailbox, with optional filtering by labels, search query, and inclusion of spam/trash folders."""
    path: ThreadsListRequestPath
    query: ThreadsListRequestQuery | None = None

# Operation: update_thread_labels
class ThreadsModifyRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the thread to modify.")
class ThreadsModifyRequestBody(StrictModel):
    add_label_ids: list[str] | None = Field(default=None, validation_alias="addLabelIds", serialization_alias="addLabelIds", description="A list of label IDs to add to this thread. Up to 100 labels can be added per request.")
    remove_label_ids: list[str] | None = Field(default=None, validation_alias="removeLabelIds", serialization_alias="removeLabelIds", description="A list of label IDs to remove from this thread. Up to 100 labels can be removed per request.")
class ThreadsModifyRequest(StrictModel):
    """Modifies the labels applied to a thread, affecting all messages within it. Supports adding and removing labels in a single operation."""
    path: ThreadsModifyRequestPath
    body: ThreadsModifyRequestBody | None = None

# Operation: trash_thread
class ThreadsTrashRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address or the special value 'me' to reference the authenticated user.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the thread to move to trash.")
class ThreadsTrashRequest(StrictModel):
    """Moves a thread and all its associated messages to the trash. The thread and its messages can be permanently deleted or recovered from trash."""
    path: ThreadsTrashRequestPath

# Operation: restore_thread
class ThreadsUntrashRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the thread to restore from trash.")
class ThreadsUntrashRequest(StrictModel):
    """Restores a thread from trash by removing it and all its associated messages from the trash folder."""
    path: ThreadsUntrashRequestPath

# ============================================================================
# Component Models
# ============================================================================

class ClassificationLabelFieldValue(PermissiveModel):
    """Field values for a classification label."""
    field_id: str | None = Field(None, validation_alias="fieldId", serialization_alias="fieldId", description="Required. The field ID for the Classification Label Value. Maps to the ID field of the Google Drive `Label.Field` object.")
    selection: str | None = Field(None, description="Selection choice ID for the selection option. Should only be set if the field type is `SELECTION` in the Google Drive `Label.Field` object. Maps to the id field of the Google Drive `Label.Field.Sel...")

class ClassificationLabelValue(PermissiveModel):
    """Classification Labels applied to the email message. Classification Labels are different from Gmail inbox labels. Only used for Google Workspace accounts. [Learn more about classification labels](https://support.google.com/a/answer/9292382)."""
    fields: list[ClassificationLabelFieldValue] | None = Field(None, description="Field values for the given classification label ID.")
    label_id: str | None = Field(None, validation_alias="labelId", serialization_alias="labelId", description="Required. The canonical or raw alphanumeric classification label ID. Maps to the ID field of the Google Drive Label resource.")

class HardwareKeyMetadata(PermissiveModel):
    """Metadata for hardware keys. If [hardware key encryption](https://support.google.com/a/answer/14153163) is set up for the Google Workspace organization, users can optionally store their private key on their smart card and use it to sign and decrypt email messages in Gmail by inserting their smart card into a reader attached to their Windows device."""
    description: str | None = Field(None, description="Description about the hardware key.")

class KaclsKeyMetadata(PermissiveModel):
    """Metadata for private keys managed by an external key access control list service. For details about managing key access, see [Google Workspace CSE API Reference](https://developers.google.com/workspace/cse/reference)."""
    kacls_data: str | None = Field(None, validation_alias="kaclsData", serialization_alias="kaclsData", description="Opaque data generated and used by the key access control list service. Maximum size: 8 KiB.")
    kacls_uri: str | None = Field(None, validation_alias="kaclsUri", serialization_alias="kaclsUri", description="The URI of the key access control list service that manages the private key.")

class CsePrivateKeyMetadata(PermissiveModel):
    """Metadata for a private key instance."""
    hardware_key_metadata: HardwareKeyMetadata | None = Field(None, validation_alias="hardwareKeyMetadata", serialization_alias="hardwareKeyMetadata", description="Metadata for hardware keys.")
    kacls_key_metadata: KaclsKeyMetadata | None = Field(None, validation_alias="kaclsKeyMetadata", serialization_alias="kaclsKeyMetadata", description="Metadata for a private key instance managed by an external key access control list service.")
    private_key_metadata_id: str | None = Field(None, validation_alias="privateKeyMetadataId", serialization_alias="privateKeyMetadataId", description="Output only. The immutable ID for the private key metadata instance.")

class LabelColor(PermissiveModel):
    background_color: str | None = Field(None, validation_alias="backgroundColor", serialization_alias="backgroundColor", description="The background color represented as hex string #RRGGBB (ex #000000). This field is required in order to set the color of a label. Only the following predefined set of color values are allowed: \\#0...")
    text_color: str | None = Field(None, validation_alias="textColor", serialization_alias="textColor", description="The text color of the label, represented as hex string. This field is required in order to set the color of a label. Only the following predefined set of color values are allowed: \\#000000, #43434...")

class Label(PermissiveModel):
    """Labels are used to categorize messages and threads within the user's mailbox. The maximum number of labels supported for a user's mailbox is 10,000."""
    color: LabelColor | None = Field(None, description="The color to assign to the label. Color is only available for labels that have their `type` set to `user`.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The immutable ID of the label.")
    label_list_visibility: Literal["labelShow", "labelShowIfUnread", "labelHide"] | None = Field(None, validation_alias="labelListVisibility", serialization_alias="labelListVisibility", description="The visibility of the label in the label list in the Gmail web interface.")
    message_list_visibility: Literal["show", "hide"] | None = Field(None, validation_alias="messageListVisibility", serialization_alias="messageListVisibility", description="The visibility of messages with this label in the message list in the Gmail web interface.")
    messages_total: int | None = Field(None, validation_alias="messagesTotal", serialization_alias="messagesTotal", description="The total number of messages with the label.", json_schema_extra={'format': 'int32'})
    messages_unread: int | None = Field(None, validation_alias="messagesUnread", serialization_alias="messagesUnread", description="The number of unread messages with the label.", json_schema_extra={'format': 'int32'})
    name: str | None = Field(None, description="The display name of the label.")
    threads_total: int | None = Field(None, validation_alias="threadsTotal", serialization_alias="threadsTotal", description="The total number of threads with the label.", json_schema_extra={'format': 'int32'})
    threads_unread: int | None = Field(None, validation_alias="threadsUnread", serialization_alias="threadsUnread", description="The number of unread threads with the label.", json_schema_extra={'format': 'int32'})
    type_: Literal["system", "user"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The owner type for the label. User labels are created by the user and can be modified and deleted by the user and can be applied to any message or thread. System labels are internally created and c...")

class MessagePartBody(PermissiveModel):
    """The body of a single MIME message part."""
    attachment_id: str | None = Field(None, validation_alias="attachmentId", serialization_alias="attachmentId", description="When present, contains the ID of an external attachment that can be retrieved in a separate `messages.attachments.get` request. When not present, the entire content of the message part body is cont...")
    data: str | None = Field(None, description="The body data of a MIME message part as a base64url encoded string. May be empty for MIME container types that have no message body or when the body data is sent as a separate attachment. An attach...", json_schema_extra={'format': 'byte'})
    size: int | None = Field(None, description="Number of bytes for the message part data (encoding notwithstanding).", json_schema_extra={'format': 'int32'})

class MessagePartHeader(PermissiveModel):
    name: str | None = Field(None, description="The name of the header before the `:` separator. For example, `To`.")
    value: str | None = Field(None, description="The value of the header after the `:` separator. For example, `someuser@example.com`.")

class History(PermissiveModel):
    """A record of a change to the user's mailbox. Each history change may affect multiple messages in multiple ways."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The mailbox sequence ID.", json_schema_extra={'format': 'uint64'})
    labels_added: list[HistoryLabelAdded] | None = Field(None, validation_alias="labelsAdded", serialization_alias="labelsAdded", description="Labels added to messages in this history record.")
    labels_removed: list[HistoryLabelRemoved] | None = Field(None, validation_alias="labelsRemoved", serialization_alias="labelsRemoved", description="Labels removed from messages in this history record.")
    messages: list[Message] | None = Field(None, description="List of messages changed in this history record. The fields for specific change types, such as `messagesAdded` may duplicate messages in this field. We recommend using the specific change-type fiel...")
    messages_added: list[HistoryMessageAdded] | None = Field(None, validation_alias="messagesAdded", serialization_alias="messagesAdded", description="Messages added to the mailbox in this history record.")
    messages_deleted: list[HistoryMessageDeleted] | None = Field(None, validation_alias="messagesDeleted", serialization_alias="messagesDeleted", description="Messages deleted (not Trashed) from the mailbox in this history record.")

class HistoryLabelAdded(PermissiveModel):
    label_ids: list[str] | None = Field(None, validation_alias="labelIds", serialization_alias="labelIds", description="Label IDs added to the message.")
    message: Message | None = None

class HistoryLabelRemoved(PermissiveModel):
    label_ids: list[str] | None = Field(None, validation_alias="labelIds", serialization_alias="labelIds", description="Label IDs removed from the message.")
    message: Message | None = None

class HistoryMessageAdded(PermissiveModel):
    message: Message | None = None

class HistoryMessageDeleted(PermissiveModel):
    message: Message | None = None

class Message(PermissiveModel):
    """An email message."""
    classification_label_values: list[ClassificationLabelValue] | None = Field(None, validation_alias="classificationLabelValues", serialization_alias="classificationLabelValues", description="Classification Label values on the message. Available Classification Label schemas can be queried using the Google Drive Labels API. Each classification label ID must be unique. If duplicate IDs ar...")
    history_id: str | None = Field(None, validation_alias="historyId", serialization_alias="historyId", description="The ID of the last history record that modified this message.", json_schema_extra={'format': 'uint64'})
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The immutable ID of the message.")
    internal_date: str | None = Field(None, validation_alias="internalDate", serialization_alias="internalDate", description="The internal message creation timestamp (epoch ms), which determines ordering in the inbox. For normal SMTP-received email, this represents the time the message was originally accepted by Google, w...", json_schema_extra={'format': 'int64'})
    label_ids: list[str] | None = Field(None, validation_alias="labelIds", serialization_alias="labelIds", description="List of IDs of labels applied to this message.")
    payload: MessagePart | None = Field(None, description="The parsed email structure in the message parts.")
    raw: str | None = Field(None, description="The entire email message in an RFC 2822 formatted and base64url encoded string. Returned in `messages.get` and `drafts.get` responses when the `format=RAW` parameter is supplied.", json_schema_extra={'format': 'byte'})
    size_estimate: int | None = Field(None, validation_alias="sizeEstimate", serialization_alias="sizeEstimate", description="Estimated size in bytes of the message.", json_schema_extra={'format': 'int32'})
    snippet: str | None = Field(None, description="A short part of the message text.")
    thread_id: str | None = Field(None, validation_alias="threadId", serialization_alias="threadId", description="The ID of the thread the message belongs to. To add a message or draft to a thread, the following criteria must be met: 1. The requested `threadId` must be specified on the `Message` or `Draft.Mess...")

class MessagePart(PermissiveModel):
    """A single MIME message part."""
    body: MessagePartBody | None = Field(None, description="The message part body for this part, which may be empty for container MIME message parts.")
    filename: str | None = Field(None, description="The filename of the attachment. Only present if this message part represents an attachment.")
    headers: list[MessagePartHeader] | None = Field(None, description="List of headers on this message part. For the top-level message part, representing the entire message payload, it will contain the standard RFC 2822 email headers such as `To`, `From`, and `Subject`.")
    mime_type: str | None = Field(None, validation_alias="mimeType", serialization_alias="mimeType", description="The MIME type of the message part.")
    part_id: str | None = Field(None, validation_alias="partId", serialization_alias="partId", description="The immutable ID of the message part.")
    parts: list[MessagePart] | None = Field(None, description="The child MIME message parts of this part. This only applies to container MIME message parts, for example `multipart/*`. For non- container MIME message part types, such as `text/plain`, this field...")


# Rebuild models to resolve forward references (required for circular refs)
ClassificationLabelFieldValue.model_rebuild()
ClassificationLabelValue.model_rebuild()
CsePrivateKeyMetadata.model_rebuild()
HardwareKeyMetadata.model_rebuild()
History.model_rebuild()
HistoryLabelAdded.model_rebuild()
HistoryLabelRemoved.model_rebuild()
HistoryMessageAdded.model_rebuild()
HistoryMessageDeleted.model_rebuild()
KaclsKeyMetadata.model_rebuild()
Label.model_rebuild()
LabelColor.model_rebuild()
Message.model_rebuild()
MessagePart.model_rebuild()
MessagePartBody.model_rebuild()
MessagePartHeader.model_rebuild()

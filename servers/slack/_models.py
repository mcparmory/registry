"""
Slack MCP Server - Pydantic Models

Generated: 2026-05-08 19:05:30 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from _validators import StrictModel
from pydantic import Field

__all__ = [
    "BotsInfoRequest",
    "CallsUpdateRequest",
    "ChatDeleteRequest",
    "ChatDeleteScheduledMessageRequest",
    "ChatGetPermalinkRequest",
    "ChatMeMessageRequest",
    "ChatPostEphemeralRequest",
    "ChatPostMessageRequest",
    "ChatScheduledMessagesListRequest",
    "ChatScheduleMessageRequest",
    "ChatUpdateRequest",
    "ConversationsArchiveRequest",
    "ConversationsCloseRequest",
    "ConversationsCreateRequest",
    "ConversationsHistoryRequest",
    "ConversationsInfoRequest",
    "ConversationsInviteRequest",
    "ConversationsJoinRequest",
    "ConversationsKickRequest",
    "ConversationsLeaveRequest",
    "ConversationsListRequest",
    "ConversationsMarkRequest",
    "ConversationsMembersRequest",
    "ConversationsOpenRequest",
    "ConversationsRenameRequest",
    "ConversationsRepliesRequest",
    "ConversationsSetPurposeRequest",
    "ConversationsSetTopicRequest",
    "ConversationsUnarchiveRequest",
    "DndInfoRequest",
    "DndSetSnoozeRequest",
    "DndTeamInfoRequest",
    "FilesCommentsDeleteRequest",
    "FilesDeleteRequest",
    "FilesInfoRequest",
    "FilesListRequest",
    "FilesRevokePublicUrlRequest",
    "FilesSharedPublicUrlRequest",
    "PinsAddRequest",
    "PinsListRequest",
    "PinsRemoveRequest",
    "ReactionsAddRequest",
    "ReactionsGetRequest",
    "ReactionsListRequest",
    "ReactionsRemoveRequest",
    "RemindersAddRequest",
    "SearchMessagesRequest",
    "StarsAddRequest",
    "StarsListRequest",
    "StarsRemoveRequest",
    "TeamInfoRequest",
    "TeamProfileGetRequest",
    "UsergroupsCreateRequest",
    "UsergroupsDisableRequest",
    "UsergroupsEnableRequest",
    "UsergroupsListRequest",
    "UsergroupsUpdateRequest",
    "UsergroupsUsersListRequest",
    "UsergroupsUsersUpdateRequest",
    "UsersConversationsRequest",
    "UsersGetPresenceRequest",
    "UsersInfoRequest",
    "UsersListRequest",
    "UsersLookupByEmailRequest",
    "UsersProfileGetRequest",
    "UsersSetPhotoRequest",
    "UsersSetPresenceRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: get_bot_info
class BotsInfoRequestQuery(StrictModel):
    bot: str | None = Field(default=None, description="The bot user identifier to retrieve information for. If not provided, returns information about the authenticated bot making the request.")
class BotsInfoRequest(StrictModel):
    """Retrieves detailed information about a specific bot user. Requires authentication with users:read scope."""
    query: BotsInfoRequestQuery | None = None

# Operation: update_call
class CallsUpdateRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Call to update, as returned by the calls.add method.")
    join_url: str | None = Field(default=None, description="The URL that clients use to join the Call. This is the primary join link for the call.")
    desktop_app_join_url: str | None = Field(default=None, description="A direct launch URL for the 3rd-party Call application on desktop clients. When provided, Slack clients will attempt to open the call directly using this URL instead of the standard join_url.")
class CallsUpdateRequest(StrictModel):
    """Updates the join URLs and other metadata for an existing Call, allowing you to modify how clients access the call."""
    body: CallsUpdateRequestBody

# Operation: delete_message
class ChatDeleteRequestBody(StrictModel):
    ts: float | None = Field(default=None, description="The timestamp of the message to delete. This uniquely identifies the message within its channel.")
    as_user: bool | None = Field(default=None, description="When true, deletes the message as the authenticated user using the `chat:write:user` scope (applies to bot users as well). When false or omitted, deletes the message using the `chat:write:bot` scope.")
    channel: str | None = Field(default=None, description="Channel containing the message to be deleted.")
class ChatDeleteRequest(StrictModel):
    """Deletes a message from a channel. The message is identified by its timestamp, and deletion can be performed either as the authenticated user or as a bot, depending on the scope and parameters provided."""
    body: ChatDeleteRequestBody | None = None

# Operation: delete_scheduled_message
class ChatDeleteScheduledMessageRequestBody(StrictModel):
    as_user: bool | None = Field(default=None, description="When true, deletes the message as the authenticated user with `chat:write:user` scope (applies to bot users as well). When false or omitted, uses `chat:write:bot` scope instead.")
    channel: str = Field(default=..., description="The channel ID where the scheduled message is queued to be posted.")
    scheduled_message_id: str = Field(default=..., description="The unique identifier of the scheduled message to delete, as returned from the chat.scheduleMessage operation.")
class ChatDeleteScheduledMessageRequest(StrictModel):
    """Removes a pending scheduled message from the queue before it is posted to a channel."""
    body: ChatDeleteScheduledMessageRequestBody

# Operation: get_message_permalink
class ChatGetPermalinkRequestQuery(StrictModel):
    channel: str = Field(default=..., description="The unique identifier of the channel or conversation containing the target message.")
    message_ts: str = Field(default=..., description="The timestamp value (`ts`) of the message, which uniquely identifies it within the channel.")
class ChatGetPermalinkRequest(StrictModel):
    """Generate a shareable permalink URL for a specific message in a channel or conversation. This allows you to create direct links to individual messages that persist even if the original message is edited."""
    query: ChatGetPermalinkRequestQuery

# Operation: send_me_message
class ChatMeMessageRequestBody(StrictModel):
    text: str | None = Field(default=None, description="The text content of the me message to send to the channel.")
    channel: str | None = Field(default=None, description="Channel to send message to. Can be a public channel, private group or IM channel. Can be an encoded ID, or a name.")
class ChatMeMessageRequest(StrictModel):
    """Send a me message (action message) to a channel. Me messages are typically used to share actions or emotes in a conversational context."""
    body: ChatMeMessageRequestBody | None = None

# Operation: send_ephemeral_message
class ChatPostEphemeralRequestBody(StrictModel):
    as_user: bool | None = Field(default=None, description="When true, posts the message as the authenticated user; when false, posts as the bot. Defaults based on available scopes.")
    channel: str = Field(default=..., description="Target channel, private group, or direct message channel. Accepts encoded channel ID or channel name.")
    parse: str | None = Field(default=None, description="Controls message formatting interpretation. Set to `none` by default to treat text literally, or use other values to enable special formatting.")
    text: str | None = Field(default=None, description="Message content. Required unless using block-based formatting. Supports text, mentions, and links depending on the `parse` setting.")
    thread_ts: str | None = Field(default=None, description="Parent message timestamp to post this message as a reply in a thread. Use the parent message's `ts` value, not a reply's timestamp. Only visible if the thread is already active.")
    user: str = Field(default=..., description="User ID of the recipient. The user must be a member of the specified channel to receive the ephemeral message.")
    username: str | None = Field(default=None, description="Custom display name for the bot. Only applies when `as_user` is false; ignored otherwise.")
class ChatPostEphemeralRequest(StrictModel):
    """Sends an ephemeral message visible only to a specific user in a channel. Ephemeral messages disappear after the user refreshes and are useful for temporary notifications or interactive responses."""
    body: ChatPostEphemeralRequestBody

# Operation: send_message_to_channel
class ChatPostMessageRequestBody(StrictModel):
    as_user: str | None = Field(default=None, description="When true, posts the message as the authenticated user instead of as a bot. Defaults to false.")
    channel: str = Field(default=..., description="Target destination for the message: a channel name, private group name, or encoded channel/user ID.")
    mrkdwn: bool | None = Field(default=None, description="When false, disables Slack markup parsing. Enabled by default to allow formatting.")
    parse: str | None = Field(default=None, description="Controls message formatting behavior. Defaults to `none`; see API documentation for available options.")
    reply_broadcast: bool | None = Field(default=None, description="When true and used with `thread_ts`, makes the threaded reply visible to all channel members instead of just the thread participants.")
    text: str | None = Field(default=None, description="Message content. Required unless using blocks or other content fields. Supports text and Slack markup when `mrkdwn` is enabled.")
    thread_ts: str | None = Field(default=None, description="Timestamp of the parent message to create a threaded reply. Use the parent message's timestamp, not a reply's timestamp.")
    unfurl_links: bool | None = Field(default=None, description="When true, enables automatic unfurling of text-based content links in the message.")
    unfurl_media: bool | None = Field(default=None, description="When false, prevents automatic unfurling of media content (images, videos, etc.) in the message.")
    username: str | None = Field(default=None, description="Custom display name for the bot. Only used when `as_user` is false; ignored otherwise.")
class ChatPostMessageRequest(StrictModel):
    """Sends a message to a Slack channel, private group, or direct message. Supports threaded replies, formatting options, and customizable authorship."""
    body: ChatPostMessageRequestBody

# Operation: schedule_message
class ChatScheduleMessageRequestBody(StrictModel):
    text: str | None = Field(default=None, description="The message content to send. Required unless using blocks or other content structures. See formatting documentation for supported syntax options.")
    post_at: str | None = Field(default=None, description="Unix EPOCH timestamp indicating when the message should be sent. Must be a future time.")
    parse: str | None = Field(default=None, description="Controls how the message text is processed. Defaults to 'none'. Options include 'full' for markdown-style formatting and 'mrkdwn' for Slack's markup syntax.")
    as_user: bool | None = Field(default=None, description="When true, posts the message as the authenticated user instead of as a bot. Defaults to false.")
    unfurl_links: bool | None = Field(default=None, description="When true, enables automatic expansion of text-based links (URLs, articles, etc.) into rich previews.")
    unfurl_media: bool | None = Field(default=None, description="When false, prevents automatic expansion of media content (images, videos, etc.) in the message.")
    thread_ts: float | None = Field(default=None, description="The timestamp of a parent message to make this message a threaded reply. Use the parent message's timestamp, not a reply's timestamp.")
    reply_broadcast: bool | None = Field(default=None, description="When true, makes a threaded reply visible to all channel members. Only applies when thread_ts is provided. Defaults to false.")
    channel: str | None = Field(default=None, description="Channel, private group, or DM channel to send message to. Can be an encoded ID, or a name. See [below](#channels) for more details.")
class ChatScheduleMessageRequest(StrictModel):
    """Schedules a message to be delivered to a channel at a specified future time. The message content and formatting can be customized with optional parameters for parsing, unfurling, and threading."""
    body: ChatScheduleMessageRequestBody | None = None

# Operation: list_scheduled_messages
class ChatScheduledMessagesListRequestQuery(StrictModel):
    latest: float | None = Field(default=None, description="A UNIX timestamp marking the most recent message to include in the results. Messages scheduled at or before this time will be returned.")
    oldest: float | None = Field(default=None, description="A UNIX timestamp marking the oldest message to include in the results. Messages scheduled at or after this time will be returned.")
    limit: int | None = Field(default=None, description="The maximum number of scheduled messages to return in a single response. Useful for pagination and controlling response size.")
class ChatScheduledMessagesListRequest(StrictModel):
    """Retrieves a list of scheduled messages, optionally filtered by a time range. Use the oldest and latest parameters to narrow results to a specific period."""
    query: ChatScheduledMessagesListRequestQuery | None = None

# Operation: update_message
class ChatUpdateRequestBody(StrictModel):
    as_user: str | None = Field(default=None, description="Set to `true` to update the message as the authenticated user (applies to bot users as well). Defaults to `false` if not specified.")
    channel: str = Field(default=..., description="The channel ID containing the message to be updated.")
    parse: str | None = Field(default=None, description="Controls how the message content is parsed. Use `none` to disable formatting or `full` to enable all formatting rules. Defaults to `client` if not specified; omitting this parameter will reset to the default value.")
    text: str | None = Field(default=None, description="The new message text using standard formatting rules. Not required if `blocks` or `attachments` are being provided instead.")
    ts: str = Field(default=..., description="The timestamp (ts) of the message to be updated, used to uniquely identify the message within the channel.")
class ChatUpdateRequest(StrictModel):
    """Updates the text and formatting of an existing message in a channel. Requires the message timestamp and channel ID to identify which message to update."""
    body: ChatUpdateRequestBody

# Operation: archive_conversation
class ConversationsArchiveRequestBody(StrictModel):
    channel: str | None = Field(default=None, description="ID of conversation to archive")
class ConversationsArchiveRequest(StrictModel):
    """Archives a conversation, removing it from the active conversation list while preserving its history for future reference."""
    body: ConversationsArchiveRequestBody | None = None

# Operation: close_conversation
class ConversationsCloseRequestBody(StrictModel):
    channel: str | None = Field(default=None, description="Conversation to close.")
class ConversationsCloseRequest(StrictModel):
    """Closes an active direct message conversation, either between two users or among multiple participants. This action archives the conversation and prevents further messages in that thread."""
    body: ConversationsCloseRequestBody | None = None

# Operation: create_conversation
class ConversationsCreateRequestBody(StrictModel):
    is_private: bool | None = Field(default=None, description="Set to true to create a private channel with restricted access, or false (default) to create a public channel visible to all users.")
    name: str | None = Field(default=None, description="Name of the public or private channel to create")
class ConversationsCreateRequest(StrictModel):
    """Creates a new conversation channel that can be either public or private. Public channels are visible to all users, while private channels restrict access to invited members only."""
    body: ConversationsCreateRequestBody | None = None

# Operation: get_conversation_history
class ConversationsHistoryRequestQuery(StrictModel):
    latest: float | None = Field(default=None, description="Unix timestamp marking the end of the time range; only messages up to this point are included in results.")
    oldest: float | None = Field(default=None, description="Unix timestamp marking the start of the time range; only messages from this point forward are included in results.")
    inclusive: bool | None = Field(default=None, description="When true, includes messages with timestamps exactly matching the latest or oldest values; when false, excludes them. Only applies when at least one timestamp boundary is specified.")
    limit: int | None = Field(default=None, description="Maximum number of messages to return per request. The actual number returned may be less than requested, even if additional messages exist.")
    channel: str | None = Field(default=None, description="Conversation ID to fetch history for.")
class ConversationsHistoryRequest(StrictModel):
    """Retrieves the message and event history for a conversation within an optional time range. Results can be paginated and filtered by timestamp boundaries."""
    query: ConversationsHistoryRequestQuery | None = None

# Operation: get_conversation_info
class ConversationsInfoRequestQuery(StrictModel):
    include_locale: bool | None = Field(default=None, description="Include the locale language and region information for the conversation in the response.")
    include_num_members: bool | None = Field(default=None, description="Include the total number of members in the conversation in the response.")
    channel: str | None = Field(default=None, description="Conversation ID to learn more about")
class ConversationsInfoRequest(StrictModel):
    """Retrieve detailed information about a specific conversation, optionally including locale and member count metadata."""
    query: ConversationsInfoRequestQuery | None = None

# Operation: add_users_to_conversation
class ConversationsInviteRequestBody(StrictModel):
    users: str | None = Field(default=None, description="A comma-separated list of user IDs to invite to the conversation. Up to 1000 users can be added in a single request.")
    channel: str | None = Field(default=None, description="The ID of the public or private channel to invite user(s) to.")
class ConversationsInviteRequest(StrictModel):
    """Adds one or more users to a conversation channel. Specify users by their IDs in a comma-separated list."""
    body: ConversationsInviteRequestBody | None = None

# Operation: join_conversation
class ConversationsJoinRequestBody(StrictModel):
    channel: str | None = Field(default=None, description="ID of conversation to join")
class ConversationsJoinRequest(StrictModel):
    """Joins the authenticated user to an existing conversation, enabling participation in the conversation's messages and interactions."""
    body: ConversationsJoinRequestBody | None = None

# Operation: remove_user_from_conversation
class ConversationsKickRequestBody(StrictModel):
    user: str | None = Field(default=None, description="The unique identifier of the user to be removed from the conversation.")
    channel: str | None = Field(default=None, description="ID of conversation to remove user from.")
class ConversationsKickRequest(StrictModel):
    """Removes a specified user from a conversation, effectively ending their participation in that conversation thread."""
    body: ConversationsKickRequestBody | None = None

# Operation: leave_conversation
class ConversationsLeaveRequestBody(StrictModel):
    channel: str | None = Field(default=None, description="Conversation to leave")
class ConversationsLeaveRequest(StrictModel):
    """Removes the authenticated user from a conversation, ending their participation and access to that conversation."""
    body: ConversationsLeaveRequestBody | None = None

# Operation: list_conversations
class ConversationsListRequestQuery(StrictModel):
    exclude_archived: bool | None = Field(default=None, description="When set to true, archived channels are excluded from the results. Useful for focusing on active conversations only.")
    types: str | None = Field(default=None, description="Filters conversations by type using a comma-separated list. Supported types are public_channel, private_channel, mpim (multi-person direct messages), and im (direct messages). Omit to include all types.")
    limit: int | None = Field(default=None, description="Maximum number of conversations to return per request, up to 1000. The API may return fewer items than requested even if more results are available.")
class ConversationsListRequest(StrictModel):
    """Retrieves a list of all conversations (channels and direct messages) in a Slack workspace, with options to filter by type and archive status."""
    query: ConversationsListRequestQuery | None = None

# Operation: mark_conversation_read
class ConversationsMarkRequestBody(StrictModel):
    ts: float = Field(default=..., description="The message timestamp to mark as read. If provided, sets your read cursor to this message; if omitted, marks the entire conversation as read up to the current time.")
    channel: str | None = Field(default=None, description="Channel or conversation to set the read cursor for.")
class ConversationsMarkRequest(StrictModel):
    """Mark a conversation as read by setting the read cursor to a specific message timestamp. This updates your read position in the channel."""
    body: ConversationsMarkRequestBody

# Operation: list_conversation_members
class ConversationsMembersRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of members to return in a single request. The API may return fewer members than requested if the end of the list is reached.")
    channel: str | None = Field(default=None, description="ID of the conversation to retrieve members for")
class ConversationsMembersRequest(StrictModel):
    """Retrieve a paginated list of members in a conversation. Use the limit parameter to control the number of results returned per request."""
    query: ConversationsMembersRequestQuery | None = None

# Operation: open_direct_message
class ConversationsOpenRequestBody(StrictModel):
    users: str | None = Field(default=None, description="Comma-separated list of user identifiers to include in the direct message. Provide a single user for a 1:1 DM, or multiple users for a group DM. The order of users is preserved in the returned conversation. Either this parameter or a channel must be supplied.")
    return_im: bool | None = Field(default=None, description="When true, returns the complete direct message channel definition in the response, including all channel metadata and settings.")
class ConversationsOpenRequest(StrictModel):
    """Opens or resumes a direct message conversation, either a 1:1 DM with a single user or a multi-person DM with multiple users. The conversation is created if it doesn't exist, or resumed if it already does."""
    body: ConversationsOpenRequestBody | None = None

# Operation: update_conversation
class ConversationsRenameRequestBody(StrictModel):
    channel: str | None = Field(default=None, description="ID of conversation to rename")
    name: str | None = Field(default=None, description="New name for conversation.")
class ConversationsRenameRequest(StrictModel):
    """Updates the name of an existing conversation. This operation allows you to rename a conversation to better organize or identify it."""
    body: ConversationsRenameRequestBody | None = None

# Operation: get_conversation_thread
class ConversationsRepliesRequestQuery(StrictModel):
    ts: float | None = Field(default=None, description="The timestamp of the parent message whose thread you want to retrieve. This message must exist and can have zero or more replies; if there are no replies, only the parent message itself is returned.")
    latest: float | None = Field(default=None, description="The end of the time range for filtering messages, specified as a Unix timestamp. Only messages up to this time will be included in results.")
    oldest: float | None = Field(default=None, description="The start of the time range for filtering messages, specified as a Unix timestamp. Only messages from this time onward will be included in results.")
    inclusive: bool | None = Field(default=None, description="When true, includes messages that match the exact latest or oldest timestamp in results. Only applies when at least one of those timestamps is specified.")
    limit: int | None = Field(default=None, description="The maximum number of messages to return in a single response. The actual number returned may be less if the thread contains fewer messages than requested.")
    channel: str | None = Field(default=None, description="Conversation ID to fetch thread from.")
class ConversationsRepliesRequest(StrictModel):
    """Retrieve a thread of messages from a conversation, including a parent message and all its replies within an optional time range."""
    query: ConversationsRepliesRequestQuery | None = None

# Operation: update_conversation_purpose
class ConversationsSetPurposeRequestBody(StrictModel):
    purpose: str | None = Field(default=None, description="The new purpose or topic description for the conversation. Provide a clear, concise statement that describes the conversation's intent or focus.")
    channel: str | None = Field(default=None, description="Conversation to set the purpose of")
class ConversationsSetPurposeRequest(StrictModel):
    """Updates the purpose or topic description for a conversation. This helps organize and clarify the conversation's intent."""
    body: ConversationsSetPurposeRequestBody | None = None

# Operation: update_conversation_topic
class ConversationsSetTopicRequestBody(StrictModel):
    topic: str | None = Field(default=None, description="The new topic string for the conversation. Plain text only; formatting and linkification are not supported.")
    channel: str | None = Field(default=None, description="Conversation to set the topic of")
class ConversationsSetTopicRequest(StrictModel):
    """Updates the topic for a conversation. The topic is a plain text string used to label or describe the conversation's subject matter."""
    body: ConversationsSetTopicRequestBody | None = None

# Operation: unarchive_conversation
class ConversationsUnarchiveRequestBody(StrictModel):
    channel: str | None = Field(default=None, description="ID of conversation to unarchive")
class ConversationsUnarchiveRequest(StrictModel):
    """Restores an archived conversation to active status, reversing the archival action and making it accessible again."""
    body: ConversationsUnarchiveRequestBody | None = None

# Operation: get_dnd_status
class DndInfoRequestQuery(StrictModel):
    user: str | None = Field(default=None, description="The user ID or username to fetch the Do Not Disturb status for. If not provided, returns the status for the authenticated user making the request.")
class DndInfoRequest(StrictModel):
    """Retrieves the current Do Not Disturb status for a user, indicating whether they have notifications muted or disabled."""
    query: DndInfoRequestQuery | None = None

# Operation: enable_do_not_disturb
class DndSetSnoozeRequestBody(StrictModel):
    num_minutes: str = Field(default=..., description="Duration in minutes from the current time until Do Not Disturb mode should automatically turn off. Must be a positive integer.")
class DndSetSnoozeRequest(StrictModel):
    """Activates Do Not Disturb mode for the current user with a specified duration. If Do Not Disturb is already active, this updates the snooze duration."""
    body: DndSetSnoozeRequestBody

# Operation: get_team_dnd_status
class DndTeamInfoRequestQuery(StrictModel):
    users: str = Field(default=..., description="Comma-separated list of user identifiers to retrieve Do Not Disturb status for. Supports up to 50 users per request.")
class DndTeamInfoRequest(StrictModel):
    """Retrieves the Do Not Disturb status for specified users on a team, allowing you to check up to 50 users at once."""
    query: DndTeamInfoRequestQuery

# Operation: delete_file_comment
class FilesCommentsDeleteRequestBody(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the comment to delete.")
    file_: str | None = Field(default=None, validation_alias="file", serialization_alias="file", description="File to delete a comment from.")
class FilesCommentsDeleteRequest(StrictModel):
    """Deletes an existing comment on a file. Requires the comment ID to identify which comment to remove."""
    body: FilesCommentsDeleteRequestBody | None = None

# Operation: delete_file
class FilesDeleteRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="file", serialization_alias="file", description="ID of file to delete.")
class FilesDeleteRequest(StrictModel):
    """Permanently deletes a file from the system. This action cannot be undone."""
    body: FilesDeleteRequestBody | None = None

# Operation: get_file_info
class FilesInfoRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of file records to return in the response. The API may return fewer items than requested if the end of the list is reached.")
    file_: str | None = Field(default=None, validation_alias="file", serialization_alias="file", description="Specify a file by providing its ID.")
class FilesInfoRequest(StrictModel):
    """Retrieves metadata and information about a specific file, including details such as size, type, timestamps, and other file attributes."""
    query: FilesInfoRequestQuery | None = None

# Operation: list_files
class FilesListRequestQuery(StrictModel):
    user: str | None = Field(default=None, description="Filter results to files created by a specific user. Provide the user identifier.")
    ts_from: float | None = Field(default=None, description="Filter results to files created on or after this timestamp (inclusive). Use Unix timestamp format.")
    ts_to: float | None = Field(default=None, description="Filter results to files created on or before this timestamp (inclusive). Use Unix timestamp format.")
    types: str | None = Field(default=None, description="Filter results by file type. Accepts multiple comma-separated values (e.g., spaces,snippets). Defaults to all types if not specified.")
    show_files_hidden_by_limit: bool | None = Field(default=None, description="When enabled, includes truncated file information for files hidden due to age or the team exceeding file storage limits. Defaults to false.")
class FilesListRequest(StrictModel):
    """Retrieve a list of files with optional filtering by user, date range, file type, and visibility. Supports showing truncated information for files hidden due to age or team file limits."""
    query: FilesListRequestQuery | None = None

# Operation: revoke_file_public_url
class FilesRevokePublicUrlRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="file", serialization_alias="file", description="File to revoke")
class FilesRevokePublicUrlRequest(StrictModel):
    """Revokes public and external sharing access for a file, preventing further access via public URLs."""
    body: FilesRevokePublicUrlRequestBody | None = None

# Operation: enable_file_public_sharing
class FilesSharedPublicUrlRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="file", serialization_alias="file", description="File to share")
class FilesSharedPublicUrlRequest(StrictModel):
    """Enables public sharing for a file by generating a shareable public URL that allows external users to access the file without authentication."""
    body: FilesSharedPublicUrlRequestBody | None = None

# Operation: add_pin_to_channel
class PinsAddRequestBody(StrictModel):
    channel: str = Field(default=..., description="The channel where the item will be pinned. Specify the channel ID or name.")
    timestamp: str | None = Field(default=None, description="The timestamp of the message to pin. Use the message's timestamp identifier to specify which message should be pinned.")
class PinsAddRequest(StrictModel):
    """Pins a message to a channel, making it easily accessible to channel members. Requires authentication with pins:write scope."""
    body: PinsAddRequestBody

# Operation: list_channel_pins
class PinsListRequestQuery(StrictModel):
    channel: str = Field(default=..., description="The channel ID or name to retrieve pinned items from.")
class PinsListRequest(StrictModel):
    """Retrieves all items pinned to a specified channel. Pinned items are messages or files that have been marked for easy reference within the channel."""
    query: PinsListRequestQuery

# Operation: remove_pin_from_channel
class PinsRemoveRequestBody(StrictModel):
    channel: str = Field(default=..., description="The channel ID or name where the pinned item is located.")
    timestamp: str | None = Field(default=None, description="The timestamp of the specific message to un-pin. If omitted, the most recently pinned message in the channel will be removed.")
class PinsRemoveRequest(StrictModel):
    """Removes a pinned message from a channel. Specify the channel and optionally the message timestamp to un-pin."""
    body: PinsRemoveRequestBody

# Operation: add_reaction_to_message
class ReactionsAddRequestBody(StrictModel):
    channel: str = Field(default=..., description="The channel ID where the message to react to is located.")
    name: str = Field(default=..., description="The emoji name to add as a reaction (e.g., 'thumbsup', 'heart'). Use the emoji name without colons or special characters.")
    timestamp: str = Field(default=..., description="The message timestamp (in seconds or milliseconds since epoch) identifying which message to add the reaction to.")
class ReactionsAddRequest(StrictModel):
    """Adds an emoji reaction to a message in a channel. Requires authentication with reactions:write scope."""
    body: ReactionsAddRequestBody

# Operation: get_reactions
class ReactionsGetRequestQuery(StrictModel):
    file_comment: str | None = Field(default=None, description="The file comment to retrieve reactions for. Specify either this parameter, timestamp, or neither to get reactions for the item context.")
    full: bool | None = Field(default=None, description="When true, returns the complete list of all reactions. When false or omitted, may return a truncated list.")
    timestamp: str | None = Field(default=None, description="The timestamp of the message to retrieve reactions for, typically in Unix epoch format. Specify either this parameter, file_comment, or neither to get reactions for the item context.")
    channel: str | None = Field(default=None, description="Channel where the message to get reactions for was posted.")
    file_: str | None = Field(default=None, validation_alias="file", serialization_alias="file", description="File to get reactions for.")
class ReactionsGetRequest(StrictModel):
    """Retrieves all reactions added to a specific message, file comment, or other item. Use this to see what emoji reactions users have added to content."""
    query: ReactionsGetRequestQuery | None = None

# Operation: list_user_reactions
class ReactionsListRequestQuery(StrictModel):
    user: str | None = Field(default=None, description="The user whose reactions to retrieve. If not specified, defaults to the authenticated user.")
    full: bool | None = Field(default=None, description="When enabled, returns the complete list of all reactions without pagination limits.")
    limit: int | None = Field(default=None, description="Maximum number of reactions to return per request. The actual number returned may be less than requested if fewer items remain.")
class ReactionsListRequest(StrictModel):
    """Retrieves a list of emoji reactions made by a user. By default, returns reactions from the authenticated user, but can be filtered to show reactions from a specific user."""
    query: ReactionsListRequestQuery | None = None

# Operation: remove_reaction
class ReactionsRemoveRequestBody(StrictModel):
    name: str = Field(default=..., description="The emoji name of the reaction to remove (e.g., 'thumbsup', 'heart'). Must match the exact reaction name.")
    file_comment: str | None = Field(default=None, description="The file comment ID from which to remove the reaction. Use this when removing a reaction from a file comment instead of a message.")
    timestamp: str | None = Field(default=None, description="The message timestamp identifying which message to remove the reaction from. Use this when removing a reaction from a message instead of a file comment.")
    channel: str | None = Field(default=None, description="Channel where the message to remove reaction from was posted.")
    file_: str | None = Field(default=None, validation_alias="file", serialization_alias="file", description="File to remove reaction from.")
class ReactionsRemoveRequest(StrictModel):
    """Removes an emoji reaction from a message or file comment. Specify either a message timestamp or file comment ID to identify the target item."""
    body: ReactionsRemoveRequestBody

# Operation: create_reminder
class RemindersAddRequestBody(StrictModel):
    text: str = Field(default=..., description="The reminder message content that will be displayed to the recipient.")
    time_: str = Field(default=..., validation_alias="time", serialization_alias="time", description="When the reminder should trigger: a Unix timestamp (up to five years in the future), seconds from now (for reminders within 24 hours), or natural language phrasing like 'in 15 minutes' or 'every Thursday'.")
    user: str | None = Field(default=None, description="The user who will receive the reminder. If omitted, the reminder is assigned to the user who created it.")
class RemindersAddRequest(StrictModel):
    """Creates a reminder that will be delivered at a specified time. The reminder can be scheduled for a specific Unix timestamp, a relative time within 24 hours, or using natural language descriptions."""
    body: RemindersAddRequestBody

# Operation: search_messages
class SearchMessagesRequestQuery(StrictModel):
    highlight: bool | None = Field(default=None, description="Enable query highlight markers in results to visually distinguish matched terms within message content.")
    query: str = Field(default=..., description="Search query string to match against message content. Supports the platform's standard search syntax.")
    sort: str | None = Field(default=None, description="Sort results by relevance score or message timestamp. Defaults to score-based sorting if not specified.")
    sort_dir: str | None = Field(default=None, description="Sort direction for results: ascending (`asc`) for oldest/lowest first, or descending (`desc`) for newest/highest first.")
class SearchMessagesRequest(StrictModel):
    """Searches for messages matching a query string, with optional result highlighting and sorting capabilities. Returns matching messages from the workspace."""
    query: SearchMessagesRequestQuery

# Operation: add_star
class StarsAddRequestBody(StrictModel):
    file_comment: str | None = Field(default=None, description="The file comment identifier to star. Specify either this or timestamp, but not both.")
    timestamp: str | None = Field(default=None, description="The timestamp of the message to star. Specify either this or file_comment, but not both.")
    channel: str | None = Field(default=None, description="Channel to add star to, or channel where the message to add star to was posted (used with `timestamp`).")
class StarsAddRequest(StrictModel):
    """Adds a star to a specific item, such as a file comment or message. Requires authentication with stars:write scope."""
    body: StarsAddRequestBody | None = None

# Operation: list_stars
class StarsListRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of items to return per request. The API may return fewer items than requested if the end of the list is reached.")
class StarsListRequest(StrictModel):
    """Retrieves a list of stars for the authenticated user, with optional pagination control."""
    query: StarsListRequestQuery | None = None

# Operation: remove_star
class StarsRemoveRequestBody(StrictModel):
    file_comment: str | None = Field(default=None, description="The file comment to remove the star from. Either this or timestamp must be provided.")
    timestamp: str | None = Field(default=None, description="The timestamp of the message to remove the star from. Either this or file_comment must be provided.")
    channel: str | None = Field(default=None, description="Channel to remove star from, or channel where the message to remove star from was posted (used with `timestamp`).")
class StarsRemoveRequest(StrictModel):
    """Removes a star from a specific item, such as a file comment or message. Requires authentication with stars:write scope."""
    body: StarsRemoveRequestBody | None = None

# Operation: get_team_info
class TeamInfoRequestQuery(StrictModel):
    team: str | None = Field(default=None, description="Optional team identifier to retrieve information for a specific team. If omitted, returns the current team. Only returns teams accessible to the authenticated token through external shared channels.")
class TeamInfoRequest(StrictModel):
    """Retrieves information about a team. If no team is specified, returns information about the authenticated user's current team. The authenticated token must have the `team:read` scope."""
    query: TeamInfoRequestQuery | None = None

# Operation: get_team_profile
class TeamProfileGetRequestQuery(StrictModel):
    visibility: str | None = Field(default=None, description="Optional filter to retrieve only team profiles matching a specific visibility level.")
class TeamProfileGetRequest(StrictModel):
    """Retrieve detailed profile information for a team, with optional filtering by visibility settings."""
    query: TeamProfileGetRequestQuery | None = None

# Operation: create_usergroup
class UsergroupsCreateRequestBody(StrictModel):
    channels: str | None = Field(default=None, description="Comma-separated list of encoded channel IDs to set as defaults for this User Group.")
    description: str | None = Field(default=None, description="A brief description of the User Group's purpose or membership.")
    handle: str | None = Field(default=None, description="A unique mention handle for the User Group. Must not conflict with existing channel names, user handles, or other User Group handles.")
    include_count: bool | None = Field(default=None, description="When enabled, the response will include the count of users currently in the User Group.")
    name: str = Field(default=..., description="A unique name for the User Group. Must not duplicate any existing User Group names.")
class UsergroupsCreateRequest(StrictModel):
    """Create a new User Group with a unique name and optional configuration for channels, description, and mention handle."""
    body: UsergroupsCreateRequestBody

# Operation: disable_usergroup
class UsergroupsDisableRequestBody(StrictModel):
    include_count: bool | None = Field(default=None, description="When enabled, the response will include a count of users currently in the User Group.")
    usergroup: str = Field(default=..., description="The encoded ID of the User Group to disable. This identifier uniquely identifies the target group.")
class UsergroupsDisableRequest(StrictModel):
    """Disable an existing User Group, preventing its use while preserving its configuration and membership data."""
    body: UsergroupsDisableRequestBody

# Operation: enable_usergroup
class UsergroupsEnableRequestBody(StrictModel):
    include_count: bool | None = Field(default=None, description="When true, the response includes the total number of users currently in the User Group.")
    usergroup: str = Field(default=..., description="The encoded ID of the User Group to enable. This identifier uniquely identifies the target User Group.")
class UsergroupsEnableRequest(StrictModel):
    """Activate a disabled User Group, making it available for use. Optionally retrieve the current member count."""
    body: UsergroupsEnableRequestBody

# Operation: list_usergroups
class UsergroupsListRequestQuery(StrictModel):
    include_users: bool | None = Field(default=None, description="Include the complete list of users belonging to each User Group in the response.")
    include_count: bool | None = Field(default=None, description="Include the total count of users in each User Group without listing individual members.")
    include_disabled: bool | None = Field(default=None, description="Include User Groups that have been disabled in addition to active groups.")
class UsergroupsListRequest(StrictModel):
    """Retrieve all User Groups configured for a team, with optional details about group membership and status."""
    query: UsergroupsListRequestQuery | None = None

# Operation: update_usergroup
class UsergroupsUpdateRequestBody(StrictModel):
    handle: str | None = Field(default=None, description="A unique mention handle for the User Group. Must be distinct across all channels, users, and other User Groups in the workspace.")
    description: str | None = Field(default=None, description="A brief description of the User Group's purpose or membership.")
    channels: str | None = Field(default=None, description="A comma-separated list of encoded channel IDs to set as defaults for this User Group.")
    include_count: bool | None = Field(default=None, description="When enabled, the response will include the total count of users currently in the User Group.")
    usergroup: str = Field(default=..., description="The encoded ID of the User Group to update. This identifier is required to target the correct group.")
class UsergroupsUpdateRequest(StrictModel):
    """Update an existing User Group's properties such as handle, description, and associated channels. Requires usergroups:write scope."""
    body: UsergroupsUpdateRequestBody

# Operation: list_usergroup_members
class UsergroupsUsersListRequestQuery(StrictModel):
    include_disabled: bool | None = Field(default=None, description="When enabled, includes results from User Groups that are currently disabled. By default, only active User Groups are included.")
    usergroup: str = Field(default=..., description="The encoded ID of the User Group whose members you want to list.")
class UsergroupsUsersListRequest(StrictModel):
    """Retrieve all users who are members of a specified User Group. Optionally include users from disabled User Groups in the results."""
    query: UsergroupsUsersListRequestQuery

# Operation: update_usergroup_users
class UsergroupsUsersUpdateRequestBody(StrictModel):
    include_count: bool | None = Field(default=None, description="When true, the response will include a count of the total number of users in the User Group.")
    usergroup: str = Field(default=..., description="The encoded ID of the User Group to update. This identifies which group's membership will be replaced.")
    users: str = Field(default=..., description="A comma-separated list of encoded user IDs that defines the complete new membership for the User Group. All previous members not in this list will be removed.")
class UsergroupsUsersUpdateRequest(StrictModel):
    """Update the complete membership of a User Group by replacing all users with a new list of user IDs."""
    body: UsergroupsUsersUpdateRequestBody

# Operation: list_user_conversations
class UsersConversationsRequestQuery(StrictModel):
    user: str | None = Field(default=None, description="Filter conversations to only those where a specific user is a member. Non-public channels are only included if the calling user shares membership in them.")
    types: str | None = Field(default=None, description="Filter by conversation type using a comma-separated list. Supported types are: public_channel, private_channel, mpim (multi-person direct message), and im (direct message).")
    exclude_archived: bool | None = Field(default=None, description="Set to true to exclude archived conversations from the results.")
    limit: int | None = Field(default=None, description="Maximum number of conversations to return per request. Must be between 1 and 1000; the API may return fewer items than requested even if more results are available.")
class UsersConversationsRequest(StrictModel):
    """Retrieve a list of conversations (channels and direct messages) that the calling user has access to, with optional filtering by user membership, conversation type, and archive status."""
    query: UsersConversationsRequestQuery | None = None

# Operation: get_user_presence
class UsersGetPresenceRequestQuery(StrictModel):
    user: str | None = Field(default=None, description="The user whose presence information should be retrieved. If omitted, defaults to the authenticated user making the request.")
class UsersGetPresenceRequest(StrictModel):
    """Retrieves the presence status of a user. If no user is specified, returns the presence information for the authenticated user."""
    query: UsersGetPresenceRequestQuery | None = None

# Operation: get_user_info
class UsersInfoRequestQuery(StrictModel):
    include_locale: bool | None = Field(default=None, description="Set to `true` to include the user's locale in the response; defaults to `false` if omitted.")
    user: str | None = Field(default=None, description="The user identifier to retrieve information for. If omitted, returns information for the authenticated user.")
class UsersInfoRequest(StrictModel):
    """Retrieves detailed information about a specific user, optionally including their locale preference."""
    query: UsersInfoRequestQuery | None = None

# Operation: list_users
class UsersListRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of users to return per request. Omitting this parameter attempts to return the entire user list, which may fail if the workspace is large; include a limit to ensure reliable pagination.")
    include_locale: bool | None = Field(default=None, description="Include the locale setting for each user in the response. Defaults to false; set to true only if locale information is needed, as it may increase response size.")
class UsersListRequest(StrictModel):
    """Retrieves all users in a Slack workspace. Results can be paginated and optionally include user locale information."""
    query: UsersListRequestQuery | None = None

# Operation: get_user_by_email
class UsersLookupByEmailRequestQuery(StrictModel):
    email: str = Field(default=..., description="The email address of the user to look up. Must be a valid email address associated with a user in the workspace.")
class UsersLookupByEmailRequest(StrictModel):
    """Retrieve a user account by their email address. Returns the user object if found in the workspace."""
    query: UsersLookupByEmailRequestQuery

# Operation: get_user_profile
class UsersProfileGetRequestQuery(StrictModel):
    include_labels: bool | None = Field(default=None, description="When enabled, includes human-readable labels for each identifier in custom profile fields, making the response more interpretable.")
    user: str | None = Field(default=None, description="The user identifier to retrieve profile information for. If omitted, returns the profile of the authenticated user making the request.")
class UsersProfileGetRequest(StrictModel):
    """Retrieves detailed profile information for a specified user or the authenticated user. Requires authentication with users.profile:read scope."""
    query: UsersProfileGetRequestQuery | None = None

# Operation: update_user_presence
class UsersSetPresenceRequestBody(StrictModel):
    presence: str = Field(default=..., description="Presence status to set for the user. Must be either 'auto' for active presence or 'away' for away status.")
class UsersSetPresenceRequest(StrictModel):
    """Manually set a user's presence status to either active (auto) or away. Requires authentication with users:write scope."""
    body: UsersSetPresenceRequestBody

# Operation: users_set_photo
class UsersSetPhotoRequestBody(StrictModel):
    crop_w: str | None = Field(default=None, description="Width/height of crop box (always square)")
    crop_x: str | None = Field(default=None, description="X coordinate of top-left corner of crop box")
    crop_y: str | None = Field(default=None, description="Y coordinate of top-left corner of crop box")
    image: str | None = Field(default=None, description="Base64-encoded file content for upload. File contents via `multipart/form-data`.", json_schema_extra={'format': 'byte'})
class UsersSetPhotoRequest(StrictModel):
    """Set the user profile photo"""
    body: UsersSetPhotoRequestBody | None = None

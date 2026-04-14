"""
Files.com MCP Server - Pydantic Models

Generated: 2026-04-14 18:21:17 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "BehaviorListForPathRequest",
    "DeleteApiKeysIdRequest",
    "DeleteAs2PartnersIdRequest",
    "DeleteAs2StationsIdRequest",
    "DeleteAutomationsIdRequest",
    "DeleteBehaviorsIdRequest",
    "DeleteBundleNotificationsIdRequest",
    "DeleteBundlesIdRequest",
    "DeleteClickwrapsIdRequest",
    "DeleteFileCommentReactionsIdRequest",
    "DeleteFileCommentsIdRequest",
    "DeleteFilesPathRequest",
    "DeleteFormFieldSetsIdRequest",
    "DeleteGroupsGroupIdMembershipsUserIdRequest",
    "DeleteGroupsIdRequest",
    "DeleteGroupUsersIdRequest",
    "DeleteLocksPathRequest",
    "DeleteMessageCommentReactionsIdRequest",
    "DeleteMessageCommentsIdRequest",
    "DeleteMessageReactionsIdRequest",
    "DeleteMessagesIdRequest",
    "DeleteNotificationsIdRequest",
    "DeletePermissionsIdRequest",
    "DeleteProjectsIdRequest",
    "DeletePublicKeysIdRequest",
    "DeleteRemoteServersIdRequest",
    "DeleteRequestsIdRequest",
    "DeleteSftpHostKeysIdRequest",
    "DeleteStylesPathRequest",
    "DeleteUserRequestsIdRequest",
    "DeleteUsersIdRequest",
    "FileActionBeginUploadRequest",
    "FileActionCopyRequest",
    "FileActionFindRequest",
    "FileActionMoveRequest",
    "FileDownloadRequest",
    "FolderListForPathRequest",
    "GetActionNotificationExportResultsRequest",
    "GetActionNotificationExportsIdRequest",
    "GetApiKeysIdRequest",
    "GetApiKeysRequest",
    "GetAppsRequest",
    "GetAs2IncomingMessagesRequest",
    "GetAs2OutgoingMessagesRequest",
    "GetAs2PartnersIdRequest",
    "GetAs2PartnersRequest",
    "GetAs2StationsIdRequest",
    "GetAs2StationsRequest",
    "GetAutomationRunsIdRequest",
    "GetAutomationRunsRequest",
    "GetAutomationsIdRequest",
    "GetAutomationsRequest",
    "GetBandwidthSnapshotsRequest",
    "GetBehaviorsIdRequest",
    "GetBundleDownloadsRequest",
    "GetBundleNotificationsIdRequest",
    "GetBundleNotificationsRequest",
    "GetBundleRecipientsRequest",
    "GetBundleRegistrationsRequest",
    "GetBundlesIdRequest",
    "GetBundlesRequest",
    "GetClickwrapsIdRequest",
    "GetClickwrapsRequest",
    "GetDnsRecordsRequest",
    "GetExternalEventsIdRequest",
    "GetExternalEventsRequest",
    "GetFileMigrationsIdRequest",
    "GetFormFieldSetsIdRequest",
    "GetFormFieldSetsRequest",
    "GetGroupsGroupIdPermissionsRequest",
    "GetGroupsGroupIdUsersRequest",
    "GetGroupsIdRequest",
    "GetGroupsRequest",
    "GetGroupUsersRequest",
    "GetHistoryExportResultsRequest",
    "GetHistoryExportsIdRequest",
    "GetInboxRecipientsRequest",
    "GetInboxRegistrationsRequest",
    "GetInboxUploadsRequest",
    "GetInvoicesIdRequest",
    "GetInvoicesRequest",
    "GetIpAddressesExavaultReservedRequest",
    "GetIpAddressesRequest",
    "GetIpAddressesReservedRequest",
    "GetMessageCommentReactionsIdRequest",
    "GetMessageCommentReactionsRequest",
    "GetMessageCommentsIdRequest",
    "GetMessageCommentsRequest",
    "GetMessageReactionsIdRequest",
    "GetMessageReactionsRequest",
    "GetMessagesIdRequest",
    "GetMessagesRequest",
    "GetNotificationsIdRequest",
    "GetNotificationsRequest",
    "GetPaymentsIdRequest",
    "GetPaymentsRequest",
    "GetPermissionsRequest",
    "GetProjectsIdRequest",
    "GetPublicKeysIdRequest",
    "GetPublicKeysRequest",
    "GetRemoteBandwidthSnapshotsRequest",
    "GetRemoteServersIdConfigurationFileRequest",
    "GetRemoteServersIdRequest",
    "GetRemoteServersRequest",
    "GetRequestsFoldersPathRequest",
    "GetRequestsRequest",
    "GetSftpHostKeysIdRequest",
    "GetSftpHostKeysRequest",
    "GetSiteApiKeysRequest",
    "GetSiteDnsRecordsRequest",
    "GetSiteIpAddressesRequest",
    "GetSsoStrategiesIdRequest",
    "GetUsageDailySnapshotsRequest",
    "GetUsageSnapshotsRequest",
    "GetUserApiKeysRequest",
    "GetUserCipherUsesRequest",
    "GetUserGroupsRequest",
    "GetUserPublicKeysRequest",
    "GetUserRequestsIdRequest",
    "GetUserRequestsRequest",
    "GetUsersIdRequest",
    "GetUsersRequest",
    "GetUsersUserIdApiKeysRequest",
    "GetUsersUserIdCipherUsesRequest",
    "GetUsersUserIdGroupsRequest",
    "GetUsersUserIdPermissionsRequest",
    "GetUsersUserIdPublicKeysRequest",
    "HistoryListForFileRequest",
    "HistoryListForFolderRequest",
    "HistoryListForUserRequest",
    "HistoryListLoginsRequest",
    "HistoryListRequest",
    "LockListForPathRequest",
    "PatchApiKeysIdRequest",
    "PatchAs2PartnersIdRequest",
    "PatchAs2StationsIdRequest",
    "PatchAutomationsIdRequest",
    "PatchBundleNotificationsIdRequest",
    "PatchBundlesIdRequest",
    "PatchClickwrapsIdRequest",
    "PatchFileCommentsIdRequest",
    "PatchFilesPathRequest",
    "PatchFormFieldSetsIdRequest",
    "PatchGroupsGroupIdMembershipsUserIdRequest",
    "PatchGroupsIdRequest",
    "PatchGroupUsersIdRequest",
    "PatchMessageCommentsIdRequest",
    "PatchMessagesIdRequest",
    "PatchNotificationsIdRequest",
    "PatchPublicKeysIdRequest",
    "PatchRemoteServersIdRequest",
    "PatchSftpHostKeysIdRequest",
    "PatchStylesPathRequest",
    "PatchUserRequest",
    "PatchUsersIdRequest",
    "PostActionNotificationExportsRequest",
    "PostActionWebhookFailuresIdRetryRequest",
    "PostApiKeysRequest",
    "PostAs2PartnersRequest",
    "PostAs2StationsRequest",
    "PostBundleRecipientsRequest",
    "PostBundlesIdShareRequest",
    "PostBundlesRequest",
    "PostClickwrapsRequest",
    "PostExternalEventsRequest",
    "PostFileCommentReactionsRequest",
    "PostFilesPathRequest",
    "PostFoldersPathRequest",
    "PostFormFieldSetsRequest",
    "PostGroupsGroupIdUsersRequest",
    "PostGroupsRequest",
    "PostGroupUsersRequest",
    "PostHistoryExportsRequest",
    "PostInboxRecipientsRequest",
    "PostMessagesRequest",
    "PostNotificationsRequest",
    "PostPermissionsRequest",
    "PostProjectsRequest",
    "PostPublicKeysRequest",
    "PostRemoteServersIdConfigurationFileRequest",
    "PostRemoteServersRequest",
    "PostRequestsRequest",
    "PostSftpHostKeysRequest",
    "PostSiteApiKeysRequest",
    "PostSsoStrategiesIdSyncRequest",
    "PostUserApiKeysRequest",
    "PostUserPublicKeysRequest",
    "PostUserRequestsRequest",
    "PostUsersId2faResetRequest",
    "PostUsersIdResendWelcomeEmailRequest",
    "PostUsersIdUnlockRequest",
    "PostUsersRequest",
    "PostUsersUserIdApiKeysRequest",
    "PostUsersUserIdPublicKeysRequest",
    "PostWebhookTestsRequest",
    "PatchFormFieldSetsIdBodyFormFieldsItem",
    "PatchRemoteServersIdBodyAws",
    "PatchRemoteServersIdBodyAzureBlobStorage",
    "PatchRemoteServersIdBodyAzureFilesStorage",
    "PatchRemoteServersIdBodyBackblazeB2",
    "PatchRemoteServersIdBodyFilebase",
    "PatchRemoteServersIdBodyGoogleCloudStorage",
    "PatchRemoteServersIdBodyRackspace",
    "PatchRemoteServersIdBodyS3Compatible",
    "PatchRemoteServersIdBodyWasabi",
    "PostFormFieldSetsBodyFormFieldsItem",
    "PostRemoteServersBodyAws",
    "PostRemoteServersBodyAzureBlobStorage",
    "PostRemoteServersBodyAzureFilesStorage",
    "PostRemoteServersBodyBackblazeB2",
    "PostRemoteServersBodyFilebase",
    "PostRemoteServersBodyGoogleCloudStorage",
    "PostRemoteServersBodyRackspace",
    "PostRemoteServersBodyS3Compatible",
    "PostRemoteServersBodyWasabi",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_action_notification_export_results
class GetActionNotificationExportResultsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Maximum number of records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    action_notification_export_id: int = Field(default=..., description="The unique identifier of the action notification export whose results you want to retrieve.", json_schema_extra={'format': 'int32'})
class GetActionNotificationExportResultsRequest(StrictModel):
    """Retrieve a paginated list of results from a specific action notification export. Use the export ID to filter results and control pagination with per_page."""
    query: GetActionNotificationExportResultsRequestQuery

# Operation: export_action_notifications
class PostActionNotificationExportsRequestBody(StrictModel):
    end_at: str | None = Field(default=None, description="End date and time for the export range (inclusive). Notifications triggered after this timestamp will be excluded.", json_schema_extra={'format': 'date-time'})
    query_folder: str | None = Field(default=None, description="Filter to notifications triggered by actions within a specific folder. Useful for isolating notifications from a particular directory.")
    query_message: str | None = Field(default=None, description="Filter to notifications with a specific error message. Helps identify notifications that failed with particular error conditions.")
    query_path: str | None = Field(default=None, description="Filter to notifications triggered by actions on a specific file or resource path. Use to track notifications for a particular file.")
    query_request_method: str | None = Field(default=None, description="Filter by the HTTP method used in the webhook request (e.g., GET, POST, PUT). Narrows results to notifications sent with a specific request method.")
    query_request_url: str | None = Field(default=None, description="Filter by the target webhook URL. Use to isolate notifications sent to a specific endpoint.")
    query_status: str | None = Field(default=None, description="Filter by the HTTP status code returned from the webhook server. Helps identify notifications that received specific response codes.")
    query_success: bool | None = Field(default=None, description="Filter by webhook delivery success. Set to true for successful deliveries (HTTP 200 or 204 responses) or false for failed deliveries.")
    start_at: str | None = Field(default=None, description="Start date and time for the export range (inclusive). Notifications triggered before this timestamp will be excluded.", json_schema_extra={'format': 'date-time'})
class PostActionNotificationExportsRequest(StrictModel):
    """Generate an export of action notification records filtered by date range, folder, file path, webhook configuration, and delivery status. Use this to audit webhook delivery history and troubleshoot notification failures."""
    body: PostActionNotificationExportsRequestBody | None = None

# Operation: get_action_notification_export
class GetActionNotificationExportsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the action notification export to retrieve.", json_schema_extra={'format': 'int32'})
class GetActionNotificationExportsIdRequest(StrictModel):
    """Retrieve details of a specific action notification export by its ID. Use this to view the status, configuration, and results of a previously created notification export."""
    path: GetActionNotificationExportsIdRequestPath

# Operation: retry_webhook_failure
class PostActionWebhookFailuresIdRetryRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the action webhook failure to retry.", json_schema_extra={'format': 'int32'})
class PostActionWebhookFailuresIdRetryRequest(StrictModel):
    """Retry a failed action webhook by its failure ID. This operation allows you to re-attempt delivery of a webhook that previously failed."""
    path: PostActionWebhookFailuresIdRetryRequestPath

# Operation: list_api_keys
class GetApiKeysRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of API keys to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort the results by a specified field in ascending or descending order. Supports sorting by expiration date.")
class GetApiKeysRequest(StrictModel):
    """Retrieve a paginated list of API keys with optional sorting by expiration date. Use this to view all API keys associated with your account."""
    query: GetApiKeysRequestQuery | None = None

# Operation: create_api_key
class PostApiKeysRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A user-supplied description to help identify the purpose or context of this API key.")
    expires_at: str | None = Field(default=None, description="The date and time when this API key will automatically expire and become invalid. Specify in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    name: str | None = Field(default=None, description="An internal name for this API key for your own reference and organization.")
    permission_set: Literal["none", "full", "desktop_app", "sync_app", "office_integration", "mobile_app"] | None = Field(default=None, description="The permission level for this API key. `full` grants complete API access, `desktop_app` restricts to file and share link operations, `sync_app` for sync functionality, `office_integration` for office tools, and `mobile_app` for mobile access. `none` grants no permissions.")
class PostApiKeysRequest(StrictModel):
    """Create a new API key for programmatic access to the API. Configure the key's name, expiration date, description, and permission level to control its capabilities."""
    body: PostApiKeysRequestBody | None = None

# Operation: get_api_key
class GetApiKeysIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the API key to retrieve.", json_schema_extra={'format': 'int32'})
class GetApiKeysIdRequest(StrictModel):
    """Retrieve a specific API key by its ID. Use this to view details of an existing API key in your account."""
    path: GetApiKeysIdRequestPath

# Operation: update_api_key_by_id
class PatchApiKeysIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the API key to update.", json_schema_extra={'format': 'int32'})
class PatchApiKeysIdRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A user-supplied description to help identify the purpose or context of this API key.")
    expires_at: str | None = Field(default=None, description="The date and time when this API key will expire and become invalid.", json_schema_extra={'format': 'date-time'})
    name: str | None = Field(default=None, description="An internal name for the API key to help you organize and identify it.")
    permission_set: Literal["none", "full", "desktop_app", "sync_app", "office_integration", "mobile_app"] | None = Field(default=None, description="The permission set determines what operations this API key can perform. Desktop app keys are limited to file and share link operations, while full keys have unrestricted access.")
class PatchApiKeysIdRequest(StrictModel):
    """Update an existing API key's configuration including name, description, expiration date, and permission set."""
    path: PatchApiKeysIdRequestPath
    body: PatchApiKeysIdRequestBody | None = None

# Operation: delete_api_key
class DeleteApiKeysIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the API key to delete.", json_schema_extra={'format': 'int32'})
class DeleteApiKeysIdRequest(StrictModel):
    """Permanently delete an API key by its ID. This action cannot be undone and will immediately revoke access for any integrations using this key."""
    path: DeleteApiKeysIdRequestPath

# Operation: list_apps
class GetAppsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, though the API supports up to 10,000 records per page.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Valid sortable fields are `name` and `app_type`. Specify the field name as the key and the direction (asc or desc) as the value.")
class GetAppsRequest(StrictModel):
    """Retrieve a paginated list of all apps with optional sorting capabilities. Use pagination parameters to control result size and sorting to organize results by name or app type."""
    query: GetAppsRequestQuery | None = None

# Operation: list_as2_incoming_messages
class GetAs2IncomingMessagesRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Valid fields are `created_at` and `as2_partner_id`.")
    as2_partner_id: int | None = Field(default=None, description="Filter messages by a specific AS2 partner ID. When provided, only messages from that partner will be returned.", json_schema_extra={'format': 'int32'})
class GetAs2IncomingMessagesRequest(StrictModel):
    """Retrieve a list of incoming AS2 messages, optionally filtered by AS2 partner and sorted by specified fields. Supports pagination for managing large result sets."""
    query: GetAs2IncomingMessagesRequestQuery | None = None

# Operation: list_as2_outgoing_messages
class GetAs2OutgoingMessagesRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Supported fields are `created_at` and `as2_partner_id`.")
    as2_partner_id: int | None = Field(default=None, description="Filter results to messages associated with a specific AS2 partner. If omitted, returns messages from all partners.", json_schema_extra={'format': 'int32'})
class GetAs2OutgoingMessagesRequest(StrictModel):
    """Retrieve a list of outgoing AS2 messages, optionally filtered by AS2 partner and sorted by specified fields. Useful for monitoring message delivery status and history."""
    query: GetAs2OutgoingMessagesRequestQuery | None = None

# Operation: list_as2_partners
class GetAs2PartnersRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.", json_schema_extra={'format': 'int32'})
class GetAs2PartnersRequest(StrictModel):
    """Retrieve a paginated list of AS2 partners configured in the system. Use the per_page parameter to control result set size."""
    query: GetAs2PartnersRequestQuery | None = None

# Operation: create_as2_partner
class PostAs2PartnersRequestBody(StrictModel):
    as2_station_id: int = Field(default=..., description="The ID of the AS2 station that this partner will be associated with.", json_schema_extra={'format': 'int32'})
    name: str = Field(default=..., description="The AS2 identifier name for this partner, used in AS2 message headers for partner identification.")
    public_certificate: str = Field(default=..., description="The public certificate in PEM format used to verify signatures and encrypt messages from this partner.")
    server_certificate: str | None = Field(default=None, description="The remote server's certificate for validating secure connections to the partner's AS2 endpoint.")
    uri: str = Field(default=..., description="The base URL where AS2 responses and acknowledgments will be sent to this partner.")
class PostAs2PartnersRequest(StrictModel):
    """Create a new AS2 partner configuration for secure EDI communication. Requires an associated AS2 station and partner identification details including certificates and response URI."""
    body: PostAs2PartnersRequestBody

# Operation: get_as2_partner
class GetAs2PartnersIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the AS2 partner to retrieve.", json_schema_extra={'format': 'int32'})
class GetAs2PartnersIdRequest(StrictModel):
    """Retrieve details for a specific AS2 partner by ID. Returns the partner's configuration and connection information."""
    path: GetAs2PartnersIdRequestPath

# Operation: update_as2_partner
class PatchAs2PartnersIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the AS2 partner to update.", json_schema_extra={'format': 'int32'})
class PatchAs2PartnersIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The AS2 partner's display name or identifier.")
    public_certificate: str | None = Field(default=None, description="The public certificate used for verifying signatures and encrypting messages from this AS2 partner.")
    server_certificate: str | None = Field(default=None, description="The remote server's certificate for establishing secure connections and validating the AS2 partner's identity.")
    uri: str | None = Field(default=None, description="The base URL where AS2 responses and acknowledgments should be sent to this partner.")
class PatchAs2PartnersIdRequest(StrictModel):
    """Update an AS2 partner's configuration including name, certificates, and response URI. Allows modification of existing AS2 partner settings for secure EDI communication."""
    path: PatchAs2PartnersIdRequestPath
    body: PatchAs2PartnersIdRequestBody | None = None

# Operation: delete_as2_partner
class DeleteAs2PartnersIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the AS2 partner to delete.", json_schema_extra={'format': 'int32'})
class DeleteAs2PartnersIdRequest(StrictModel):
    """Delete an AS2 partner configuration. This operation permanently removes the specified AS2 partner from the system."""
    path: DeleteAs2PartnersIdRequestPath

# Operation: list_as2_stations
class GetAs2StationsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.", json_schema_extra={'format': 'int32'})
class GetAs2StationsRequest(StrictModel):
    """Retrieve a paginated list of AS2 stations. Use the per_page parameter to control the number of records returned per page."""
    query: GetAs2StationsRequestQuery | None = None

# Operation: create_as2_station
class PostAs2StationsRequestBody(StrictModel):
    name: str = Field(default=..., description="The name identifier for the AS2 station. Used to reference this station in AS2 communications and configurations.")
    private_key: str = Field(default=..., description="The private key used for signing outbound AS2 messages and decrypting inbound messages. Must be in PEM format.")
    private_key_password: str | None = Field(default=None, description="Optional password protecting the private key. Required if the private key is encrypted.")
    public_certificate: str = Field(default=..., description="The public certificate corresponding to the private key, used for message authentication and encryption verification. Must be in PEM or DER format.")
class PostAs2StationsRequest(StrictModel):
    """Create a new AS2 station for secure EDI communication. Requires cryptographic credentials including a private key and public certificate for message signing and encryption."""
    body: PostAs2StationsRequestBody

# Operation: get_as2_station
class GetAs2StationsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the AS2 station to retrieve.", json_schema_extra={'format': 'int32'})
class GetAs2StationsIdRequest(StrictModel):
    """Retrieve details for a specific AS2 station by its ID. Returns the configuration and status information for the AS2 station."""
    path: GetAs2StationsIdRequestPath

# Operation: update_as2_station
class PatchAs2StationsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the AS2 station to update.", json_schema_extra={'format': 'int32'})
class PatchAs2StationsIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The AS2 station name or identifier.")
    private_key: str | None = Field(default=None, description="The private key used for signing AS2 messages.")
    private_key_password: str | None = Field(default=None, description="The password protecting the private key.")
    public_certificate: str | None = Field(default=None, description="The public certificate used for verifying AS2 message signatures.")
class PatchAs2StationsIdRequest(StrictModel):
    """Update an AS2 station configuration including its name, private key, and public certificate credentials."""
    path: PatchAs2StationsIdRequestPath
    body: PatchAs2StationsIdRequestBody | None = None

# Operation: delete_as2_station
class DeleteAs2StationsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the AS2 station to delete.", json_schema_extra={'format': 'int32'})
class DeleteAs2StationsIdRequest(StrictModel):
    """Delete an AS2 station by its ID. This operation permanently removes the AS2 station configuration and cannot be undone."""
    path: DeleteAs2StationsIdRequestPath

# Operation: list_automation_runs
class GetAutomationRunsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Maximum number of records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Supported fields are `created_at` and `status`.")
    automation_id: int = Field(default=..., description="The ID of the automation whose runs you want to list.", json_schema_extra={'format': 'int32'})
class GetAutomationRunsRequest(StrictModel):
    """Retrieve a paginated list of automation runs for a specific automation. Filter, sort, and control pagination to find the runs you need."""
    query: GetAutomationRunsRequestQuery

# Operation: get_automation_run
class GetAutomationRunsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the automation run to retrieve.", json_schema_extra={'format': 'int32'})
class GetAutomationRunsIdRequest(StrictModel):
    """Retrieve details of a specific automation run by its ID. Returns the current state, execution history, and results of the automation run."""
    path: GetAutomationRunsIdRequestPath

# Operation: list_automations
class GetAutomationsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of automation records to return per page. Recommended to use 1,000 or less for optimal performance, though up to 10,000 is supported.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Valid sortable fields are: automation, disabled, last_modified_at, or name.")
    with_deleted: bool | None = Field(default=None, description="Include deleted automations in the results. Set to true to show all automations including those that have been deleted.")
class GetAutomationsRequest(StrictModel):
    """Retrieve a paginated list of automations with optional filtering and sorting. Use this to view all automations in your account, including deleted ones if needed."""
    query: GetAutomationsRequestQuery | None = None

# Operation: get_automation
class GetAutomationsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the automation to retrieve.", json_schema_extra={'format': 'int32'})
class GetAutomationsIdRequest(StrictModel):
    """Retrieve details for a specific automation by its ID. Returns the automation configuration and current state."""
    path: GetAutomationsIdRequestPath

# Operation: update_automation
class PatchAutomationsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the automation to update.", json_schema_extra={'format': 'int32'})
class PatchAutomationsIdRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A descriptive label for this automation.")
    disabled: bool | None = Field(default=None, description="When true, prevents this automation from executing.")
    interval: str | None = Field(default=None, description="The execution frequency for this automation. Determines how often the automation runs based on calendar intervals.")
    name: str | None = Field(default=None, description="A human-readable name for this automation.")
    source: str | None = Field(default=None, description="The source path associated with this automation.")
    sync_ids: str | None = Field(default=None, description="Comma-separated list of sync IDs this automation is associated with.")
    trigger: Literal["realtime", "daily", "custom_schedule", "webhook", "email", "action"] | None = Field(default=None, description="The mechanism that initiates automation execution. Determines whether the automation runs on a schedule, in response to events, or via external triggers.")
    trigger_actions: list[str] | None = Field(default=None, description="When trigger is set to 'action', specifies which action types activate the automation. Valid actions include create, read, update, destroy, move, and copy operations.")
    user_ids: str | None = Field(default=None, description="Comma-separated list of user IDs this automation is associated with.")
    value: dict[str, Any] | None = Field(default=None, description="A structured object containing automation type-specific configuration parameters and settings.")
    destinations: list | None = Field(default=None, description="A list of String destination paths or Hash of folder_path and optional file_path.")
    schedule: dict | None = Field(default=None, description="Custom schedule for running this automation.")
class PatchAutomationsIdRequest(StrictModel):
    """Update an existing automation configuration. Modify automation properties such as schedule, trigger type, associated syncs/users, and behavior settings."""
    path: PatchAutomationsIdRequestPath
    body: PatchAutomationsIdRequestBody | None = None

# Operation: delete_automation
class DeleteAutomationsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the automation to delete.", json_schema_extra={'format': 'int32'})
class DeleteAutomationsIdRequest(StrictModel):
    """Permanently delete an automation by its ID. This action cannot be undone."""
    path: DeleteAutomationsIdRequestPath

# Operation: list_bandwidth_snapshots
class GetBandwidthSnapshotsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Use the field name as the key and 'asc' or 'desc' as the value. Valid sortable field is 'logged_at'.")
class GetBandwidthSnapshotsRequest(StrictModel):
    """Retrieve a paginated list of bandwidth snapshots. Results can be sorted by the logged timestamp in ascending or descending order."""
    query: GetBandwidthSnapshotsRequestQuery | None = None

# Operation: list_behaviors_by_path
class BehaviorListForPathRequestPath(StrictModel):
    path: str = Field(default=..., description="The folder path where behaviors are located. This path determines the starting point for the behavior listing.")
class BehaviorListForPathRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Maximum number of behavior records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by the behavior field in ascending or descending order. Specify as an object with the field name as key and sort direction as value.")
    recursive: str | None = Field(default=None, description="Include behaviors from parent directories above the specified path when enabled. Controls whether the listing is limited to the exact path or includes the hierarchy above it.")
class BehaviorListForPathRequest(StrictModel):
    """Retrieve a list of behaviors from a specified folder path, with optional filtering, sorting, and recursive traversal capabilities."""
    path: BehaviorListForPathRequestPath
    query: BehaviorListForPathRequestQuery | None = None

# Operation: get_behavior
class GetBehaviorsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the behavior to retrieve.", json_schema_extra={'format': 'int32'})
class GetBehaviorsIdRequest(StrictModel):
    """Retrieve detailed information about a specific behavior by its ID."""
    path: GetBehaviorsIdRequestPath

# Operation: delete_behavior
class DeleteBehaviorsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the behavior to delete.", json_schema_extra={'format': 'int32'})
class DeleteBehaviorsIdRequest(StrictModel):
    """Permanently delete a behavior by its ID. This action cannot be undone."""
    path: DeleteBehaviorsIdRequestPath

# Operation: list_bundle_downloads
class GetBundleDownloadsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000 records per page.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Only `created_at` is supported as a valid sort field.")
    bundle_id: int | None = Field(default=None, description="Filter results to downloads associated with a specific bundle by its ID.", json_schema_extra={'format': 'int32'})
    bundle_registration_id: int | None = Field(default=None, description="Filter results to downloads associated with a specific bundle registration by its ID.", json_schema_extra={'format': 'int32'})
class GetBundleDownloadsRequest(StrictModel):
    """Retrieve a paginated list of bundle downloads with optional filtering by bundle or bundle registration ID, and sorting capabilities."""
    query: GetBundleDownloadsRequestQuery | None = None

# Operation: list_bundle_notifications
class GetBundleNotificationsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Maximum number of records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    bundle_id: int | None = Field(default=None, description="Filter notifications by a specific bundle ID. Omit to retrieve notifications for all bundles.", json_schema_extra={'format': 'int32'})
class GetBundleNotificationsRequest(StrictModel):
    """Retrieve a paginated list of notifications for a specific bundle or all bundles. Use pagination parameters to control result size and retrieval."""
    query: GetBundleNotificationsRequestQuery | None = None

# Operation: get_bundle_notification
class GetBundleNotificationsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bundle notification to retrieve.", json_schema_extra={'format': 'int32'})
class GetBundleNotificationsIdRequest(StrictModel):
    """Retrieve details for a specific bundle notification by its ID. Use this to fetch the full notification record including its content and metadata."""
    path: GetBundleNotificationsIdRequestPath

# Operation: update_bundle_notification
class PatchBundleNotificationsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bundle notification to update.", json_schema_extra={'format': 'int32'})
class PatchBundleNotificationsIdRequestBody(StrictModel):
    notify_on_registration: bool | None = Field(default=None, description="Enable or disable notifications when a registration action occurs for this bundle.")
    notify_on_upload: bool | None = Field(default=None, description="Enable or disable notifications when an upload action occurs for this bundle.")
class PatchBundleNotificationsIdRequest(StrictModel):
    """Update notification settings for a bundle, controlling when notifications are triggered for registration and upload actions."""
    path: PatchBundleNotificationsIdRequestPath
    body: PatchBundleNotificationsIdRequestBody | None = None

# Operation: delete_bundle_notification
class DeleteBundleNotificationsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bundle notification to delete.", json_schema_extra={'format': 'int32'})
class DeleteBundleNotificationsIdRequest(StrictModel):
    """Delete a specific bundle notification by its ID. This operation permanently removes the bundle notification from the system."""
    path: DeleteBundleNotificationsIdRequestPath

# Operation: list_bundle_recipients
class GetBundleRecipientsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Valid field is `has_registrations`.")
    bundle_id: int = Field(default=..., description="The ID of the bundle for which to list recipients.", json_schema_extra={'format': 'int32'})
class GetBundleRecipientsRequest(StrictModel):
    """Retrieve a list of recipients associated with a specific bundle. Supports pagination and sorting by registration status."""
    query: GetBundleRecipientsRequestQuery

# Operation: share_bundle_with_recipient
class PostBundleRecipientsRequestBody(StrictModel):
    bundle_id: int = Field(default=..., description="The ID of the bundle to share with the recipient.", json_schema_extra={'format': 'int32'})
    company: str | None = Field(default=None, description="The company name associated with the recipient.")
    name: str | None = Field(default=None, description="The full name of the recipient.")
    note: str | None = Field(default=None, description="An optional message to include in the share notification email sent to the recipient.")
    recipient: str = Field(default=..., description="The email address of the recipient to share the bundle with.")
    share_after_create: bool | None = Field(default=None, description="When true, automatically sends a share notification email to the recipient upon creation. When false, the recipient is added without sending an email.")
class PostBundleRecipientsRequest(StrictModel):
    """Share a bundle with a recipient by creating a bundle recipient record. Optionally send a share notification email immediately upon creation."""
    body: PostBundleRecipientsRequestBody

# Operation: list_bundle_registrations
class GetBundleRegistrationsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    bundle_id: int | None = Field(default=None, description="Filter results to registrations associated with a specific bundle by its ID.", json_schema_extra={'format': 'int32'})
class GetBundleRegistrationsRequest(StrictModel):
    """Retrieve a paginated list of bundle registrations, optionally filtered by a specific bundle ID."""
    query: GetBundleRegistrationsRequestQuery | None = None

# Operation: list_bundles
class GetBundlesRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of bundle records to return per page. Recommended to use 1,000 or less for optimal performance, though up to 10,000 is supported.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Supports sorting by `created_at` or `code` fields.")
class GetBundlesRequest(StrictModel):
    """Retrieve a paginated list of bundles with optional sorting. Use pagination parameters to control result size and sorting to organize bundles by creation date or code."""
    query: GetBundlesRequestQuery | None = None

# Operation: create_bundle
class PostBundlesRequestBody(StrictModel):
    clickwrap_id: int | None = Field(default=None, description="ID of the clickwrap agreement to display to bundle recipients before access is granted.", json_schema_extra={'format': 'int32'})
    code: str | None = Field(default=None, description="Custom code that forms the public-facing URL slug for this bundle. Must be unique and URL-safe.")
    description: str | None = Field(default=None, description="Public-facing description displayed to bundle recipients explaining the bundle's contents and purpose.")
    dont_separate_submissions_by_folder: bool | None = Field(default=None, description="When enabled, prevents automatic creation of subfolders for uploads from different users. Use with caution due to security implications when accepting anonymous uploads from multiple sources.")
    expires_at: str | None = Field(default=None, description="Date and time when the bundle automatically expires and becomes inaccessible. Specified in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    form_field_set_id: int | None = Field(default=None, description="ID of the form field set to associate with this bundle. Captured data from form submissions will be stored with uploads.", json_schema_extra={'format': 'int32'})
    inbox_id: int | None = Field(default=None, description="ID of the inbox where bundle submissions will be delivered. If not specified, submissions go to the default location.", json_schema_extra={'format': 'int32'})
    max_uses: int | None = Field(default=None, description="Maximum number of times the bundle can be accessed before it becomes unavailable. Unlimited if not specified.", json_schema_extra={'format': 'int32'})
    note: str | None = Field(default=None, description="Internal note for bundle management purposes. Not visible to bundle recipients.")
    path_template: str | None = Field(default=None, description="Template for organizing submission subfolders using uploader metadata. Supports placeholders for name, email, IP address, company, and custom form fields using double-brace syntax.")
    paths: list[str] = Field(default=..., description="List of file and folder paths to include in this bundle. Paths are processed in the order specified.")
    permissions: Literal["read", "write", "read_write", "full", "none", "preview_only"] | None = Field(default=None, description="Access level granted to recipients for folders within this bundle. Controls whether recipients can view, download, upload, or modify contents.")
    require_registration: bool | None = Field(default=None, description="When enabled, recipients must provide their name and email address before accessing the bundle.")
    require_share_recipient: bool | None = Field(default=None, description="When enabled, only recipients who received an invitation email through the Files.com interface can access the bundle.")
    send_email_receipt_to_uploader: bool | None = Field(default=None, description="When enabled, an email receipt confirming successful upload is sent to the uploader. Only applicable for bundles with write permissions.")
    watermark_attachment_file: str | None = Field(default=None, description="Image file to apply as a watermark overlay on all bundle item previews. Uploaded as binary file data.", json_schema_extra={'format': 'binary'})
class PostBundlesRequest(StrictModel):
    """Create a shareable bundle that packages files and folders with configurable access controls, expiration, and submission handling. Bundles can require registration, limit access to specific recipients, and apply watermarks to previewed items."""
    body: PostBundlesRequestBody

# Operation: get_bundle
class GetBundlesIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bundle to retrieve.", json_schema_extra={'format': 'int32'})
class GetBundlesIdRequest(StrictModel):
    """Retrieve detailed information about a specific bundle by its ID."""
    path: GetBundlesIdRequestPath

# Operation: update_bundle
class PatchBundlesIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bundle to update.", json_schema_extra={'format': 'int32'})
class PatchBundlesIdRequestBody(StrictModel):
    clickwrap_id: int | None = Field(default=None, description="The clickwrap agreement to associate with this bundle for user acceptance.", json_schema_extra={'format': 'int32'})
    code: str | None = Field(default=None, description="A unique code that forms the final segment of the bundle's public URL.")
    description: str | None = Field(default=None, description="A public-facing description displayed to bundle users.")
    dont_separate_submissions_by_folder: bool | None = Field(default=None, description="When enabled, prevents automatic creation of subfolders for uploads from different users. Use with caution due to potential security implications with anonymous multi-user uploads.")
    expires_at: str | None = Field(default=None, description="The date and time when the bundle expires and becomes inaccessible. Use ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    form_field_set_id: int | None = Field(default=None, description="The form field set to associate with this bundle for collecting uploader information.", json_schema_extra={'format': 'int32'})
    inbox_id: int | None = Field(default=None, description="The inbox to associate with this bundle for organizing submissions.", json_schema_extra={'format': 'int32'})
    max_uses: int | None = Field(default=None, description="The maximum number of times the bundle can be accessed before becoming unavailable.", json_schema_extra={'format': 'int32'})
    note: str | None = Field(default=None, description="An internal note for bundle administrators, not visible to users.")
    path_template: str | None = Field(default=None, description="A template for organizing submission subfolders using uploader metadata. Supports placeholders for name, email, IP address, company, and custom form fields.")
    paths: list[str] | None = Field(default=None, description="A list of file and folder paths to include in the bundle. Order is preserved as specified.")
    permissions: Literal["read", "write", "read_write", "full", "none", "preview_only"] | None = Field(default=None, description="The permission level for accessing folders within this bundle.")
    require_registration: bool | None = Field(default=None, description="When enabled, displays a registration form to capture the downloader's name and email address.")
    require_share_recipient: bool | None = Field(default=None, description="When enabled, restricts access to only recipients who have been explicitly invited via email through the Files.com interface.")
    send_email_receipt_to_uploader: bool | None = Field(default=None, description="When enabled, sends a delivery receipt to the uploader upon bundle access. Only applicable for writable bundles.")
    watermark_attachment_file: str | None = Field(default=None, description="A watermark image file to overlay on all bundle item previews for branding or security purposes.", json_schema_extra={'format': 'binary'})
class PatchBundlesIdRequest(StrictModel):
    """Update an existing bundle's configuration, including access controls, expiration, paths, and metadata. Allows modification of sharing permissions, recipient requirements, and submission handling."""
    path: PatchBundlesIdRequestPath
    body: PatchBundlesIdRequestBody | None = None

# Operation: delete_bundle
class DeleteBundlesIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bundle to delete.", json_schema_extra={'format': 'int32'})
class DeleteBundlesIdRequest(StrictModel):
    """Permanently delete a bundle by its ID. This action cannot be undone."""
    path: DeleteBundlesIdRequestPath

# Operation: share_bundle
class PostBundlesIdShareRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bundle to share.", json_schema_extra={'format': 'int32'})
class PostBundlesIdShareRequestBody(StrictModel):
    note: str | None = Field(default=None, description="Optional custom message to include in the share email.")
class PostBundlesIdShareRequest(StrictModel):
    """Send email(s) with a shareable link to a bundle. Optionally include a custom note in the email message."""
    path: PostBundlesIdShareRequestPath
    body: PostBundlesIdShareRequestBody | None = None

# Operation: list_clickwraps
class GetClickwrapsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of clickwrap records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
class GetClickwrapsRequest(StrictModel):
    """Retrieve a paginated list of clickwraps. Use the per_page parameter to control the number of records returned in each page."""
    query: GetClickwrapsRequestQuery | None = None

# Operation: create_clickwrap
class PostClickwrapsRequestBody(StrictModel):
    name: str | None = Field(default=None, description="Display name for this clickwrap agreement, used when presenting multiple clickwrap options to users.")
    use_with_bundles: Literal["none", "available", "require"] | None = Field(default=None, description="Determines how this clickwrap applies to bundle operations: 'none' disables it, 'available' makes it optional, 'require' makes acceptance mandatory.")
    use_with_inboxes: Literal["none", "available", "require"] | None = Field(default=None, description="Determines how this clickwrap applies to inbox operations: 'none' disables it, 'available' makes it optional, 'require' makes acceptance mandatory.")
    use_with_users: Literal["none", "require"] | None = Field(default=None, description="Determines how this clickwrap applies to user registration via email invitation: 'none' disables it, 'require' makes acceptance mandatory during password setup.")
    body: str | None = Field(default=None, description="Body text of Clickwrap (supports Markdown formatting).")
class PostClickwrapsRequest(StrictModel):
    """Create a new clickwrap agreement that users must accept. Clickwraps can be configured for use with bundles, inboxes, and user registrations."""
    body: PostClickwrapsRequestBody | None = None

# Operation: get_clickwrap
class GetClickwrapsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the clickwrap agreement to retrieve.", json_schema_extra={'format': 'int32'})
class GetClickwrapsIdRequest(StrictModel):
    """Retrieve a specific clickwrap agreement by its ID. Returns the clickwrap details including its configuration and status."""
    path: GetClickwrapsIdRequestPath

# Operation: update_clickwrap
class PatchClickwrapsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Clickwrap agreement to update.", json_schema_extra={'format': 'int32'})
class PatchClickwrapsIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="Display name for the Clickwrap agreement, used when presenting multiple agreements to users for selection.")
    use_with_bundles: Literal["none", "available", "require"] | None = Field(default=None, description="Controls whether this Clickwrap is available for Bundle operations. Set to 'require' to mandate acceptance, 'available' to offer optionally, or 'none' to disable.")
    use_with_inboxes: Literal["none", "available", "require"] | None = Field(default=None, description="Controls whether this Clickwrap is available for Inbox operations. Set to 'require' to mandate acceptance, 'available' to offer optionally, or 'none' to disable.")
    use_with_users: Literal["none", "require"] | None = Field(default=None, description="Controls whether this Clickwrap is required for user registrations via email invitation. Applies only when users are invited to set their own password. Set to 'require' to mandate acceptance or 'none' to disable.")
class PatchClickwrapsIdRequest(StrictModel):
    """Update an existing Clickwrap agreement configuration, including its name and usage settings across bundles, inboxes, and user registrations."""
    path: PatchClickwrapsIdRequestPath
    body: PatchClickwrapsIdRequestBody | None = None

# Operation: delete_clickwrap
class DeleteClickwrapsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the clickwrap to delete.", json_schema_extra={'format': 'int32'})
class DeleteClickwrapsIdRequest(StrictModel):
    """Permanently delete a clickwrap by its ID. This action cannot be undone."""
    path: DeleteClickwrapsIdRequestPath

# Operation: list_dns_records
class GetDnsRecordsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of DNS records to return per page. Recommended to use 1,000 or less for optimal performance, though up to 10,000 records can be retrieved in a single request.", json_schema_extra={'format': 'int32'})
class GetDnsRecordsRequest(StrictModel):
    """Retrieve the DNS records configured for a site. Results can be paginated to manage large record sets."""
    query: GetDnsRecordsRequestQuery | None = None

# Operation: list_external_events
class GetExternalEventsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, though up to 10,000 is supported.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Valid sortable fields are: remote_server_type, site_id, folder_behavior_id, event_type, created_at, or status.")
class GetExternalEventsRequest(StrictModel):
    """Retrieve a paginated list of external events with optional sorting. Use this to monitor and track events from remote servers across your file management system."""
    query: GetExternalEventsRequestQuery | None = None

# Operation: create_external_event
class PostExternalEventsRequestBody(StrictModel):
    body: str = Field(default=..., description="The content or payload of the event being created.")
    status: Literal["success", "failure", "partial_failure", "in_progress", "skipped"] = Field(default=..., description="The current processing state of the event.")
class PostExternalEventsRequest(StrictModel):
    """Create a new external event with a specified status. This operation allows you to log events from external systems with their current processing state."""
    body: PostExternalEventsRequestBody

# Operation: get_external_event
class GetExternalEventsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the external event to retrieve.", json_schema_extra={'format': 'int32'})
class GetExternalEventsIdRequest(StrictModel):
    """Retrieve details for a specific external event by its ID. Returns the complete event information including metadata and configuration."""
    path: GetExternalEventsIdRequestPath

# Operation: initiate_file_upload
class FileActionBeginUploadRequestPath(StrictModel):
    path: str = Field(default=..., description="The file path where the upload will be stored. Can be a new file or an existing file for append/restart operations.")
class FileActionBeginUploadRequestBody(StrictModel):
    mkdir_parents: bool | None = Field(default=None, description="Whether to automatically create any missing parent directories in the path hierarchy.")
    parts: int | None = Field(default=None, description="The number of parts to divide the file into for multipart upload. Determines parallelization strategy for the upload.", json_schema_extra={'format': 'int32'})
    size: int | None = Field(default=None, description="The total file size in bytes, including any existing bytes if appending to or restarting an existing file.", json_schema_extra={'format': 'int32'})
class FileActionBeginUploadRequest(StrictModel):
    """Initiate a file upload by specifying the target path, total file size, and number of parts. Optionally create parent directories and configure multipart upload parameters."""
    path: FileActionBeginUploadRequestPath
    body: FileActionBeginUploadRequestBody | None = None

# Operation: copy_file
class FileActionCopyRequestPath(StrictModel):
    path: str = Field(default=..., description="The file or folder path to copy from.")
class FileActionCopyRequestBody(StrictModel):
    destination: str = Field(default=..., description="The destination path where the file or folder will be copied to.")
    structure: bool | None = Field(default=None, description="If true, copy only the directory structure without copying file contents.")
class FileActionCopyRequest(StrictModel):
    """Copy a file or folder to a specified destination. Optionally copy only the directory structure without file contents."""
    path: FileActionCopyRequestPath
    body: FileActionCopyRequestBody

# Operation: get_file_metadata
class FileActionFindRequestPath(StrictModel):
    path: str = Field(default=..., description="The file system path to the target file or folder.")
class FileActionFindRequestQuery(StrictModel):
    preview_size: str | None = Field(default=None, description="The size of the file preview to include in the response. Determines the resolution and detail level of preview data.")
    with_previews: bool | None = Field(default=None, description="Whether to include preview information in the response metadata.")
    with_priority_color: bool | None = Field(default=None, description="Whether to include priority color information in the response metadata.")
class FileActionFindRequest(StrictModel):
    """Retrieve metadata for a file or folder at the specified path, optionally including preview and priority information."""
    path: FileActionFindRequestPath
    query: FileActionFindRequestQuery | None = None

# Operation: move_file
class FileActionMoveRequestPath(StrictModel):
    path: str = Field(default=..., description="The current path of the file or folder to be moved.")
class FileActionMoveRequestBody(StrictModel):
    destination: str = Field(default=..., description="The destination path where the file or folder should be moved to.")
class FileActionMoveRequest(StrictModel):
    """Move a file or folder to a new location. The source path and destination path must both be valid within the file system."""
    path: FileActionMoveRequestPath
    body: FileActionMoveRequestBody

# Operation: add_file_comment_reaction
class PostFileCommentReactionsRequestBody(StrictModel):
    emoji: str = Field(default=..., description="The emoji character or emoji code to use as the reaction on the file comment.")
    file_comment_id: int = Field(default=..., description="The unique identifier of the file comment to attach the reaction to.", json_schema_extra={'format': 'int32'})
class PostFileCommentReactionsRequest(StrictModel):
    """Add an emoji reaction to a file comment. This allows users to express feedback or acknowledgment on specific comments within a file."""
    body: PostFileCommentReactionsRequestBody

# Operation: remove_file_comment_reaction
class DeleteFileCommentReactionsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the file comment reaction to delete.", json_schema_extra={'format': 'int32'})
class DeleteFileCommentReactionsIdRequest(StrictModel):
    """Remove a reaction from a file comment. Deletes the specified file comment reaction by its ID."""
    path: DeleteFileCommentReactionsIdRequestPath

# Operation: update_file_comment
class PatchFileCommentsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the file comment to update.", json_schema_extra={'format': 'int32'})
class PatchFileCommentsIdRequestBody(StrictModel):
    body: str = Field(default=..., description="The new comment text content to replace the existing body.")
class PatchFileCommentsIdRequest(StrictModel):
    """Update the body text of an existing file comment. Allows modification of comment content after initial creation."""
    path: PatchFileCommentsIdRequestPath
    body: PatchFileCommentsIdRequestBody

# Operation: delete_file_comment
class DeleteFileCommentsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the file comment to delete.", json_schema_extra={'format': 'int32'})
class DeleteFileCommentsIdRequest(StrictModel):
    """Delete a specific file comment by its ID. This operation permanently removes the comment from the file."""
    path: DeleteFileCommentsIdRequestPath

# Operation: get_file_migration
class GetFileMigrationsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the file migration to retrieve.", json_schema_extra={'format': 'int32'})
class GetFileMigrationsIdRequest(StrictModel):
    """Retrieve details of a specific file migration by its ID. Use this to check the status and information of a file migration operation."""
    path: GetFileMigrationsIdRequestPath

# Operation: download_file
class FileDownloadRequestPath(StrictModel):
    path: str = Field(default=..., description="The file path to download or retrieve information for.")
class FileDownloadRequestQuery(StrictModel):
    action: str | None = Field(default=None, description="Controls the response behavior: leave blank for standard download, use 'stat' to retrieve file metadata without a download URL, or use 'redirect' to receive a 302 redirect directly to the file.")
    preview_size: str | None = Field(default=None, description="The size of the preview image to generate. Larger sizes provide higher resolution previews.")
    with_previews: bool | None = Field(default=None, description="Include preview image data in the response when available.")
    with_priority_color: bool | None = Field(default=None, description="Include priority color metadata in the response when available.")
class FileDownloadRequest(StrictModel):
    """Download a file from the specified path with optional preview generation, metadata retrieval, or redirect handling. Supports stat mode to retrieve file information without initiating a download."""
    path: FileDownloadRequestPath
    query: FileDownloadRequestQuery | None = None

# Operation: upload_file
class PostFilesPathRequestPath(StrictModel):
    path: str = Field(default=..., description="The file system path where the file will be uploaded or operated on.")
class PostFilesPathRequestBody(StrictModel):
    action: str | None = Field(default=None, description="The type of upload action to perform: `upload` for standard file upload, `append` to append to existing file, `attachment` for attachment handling, `put` for direct replacement, `end` to finalize multipart upload, or omit for default behavior.")
    etags_etag: list[str] = Field(default=..., validation_alias="etags[etag]", serialization_alias="etags[etag]", description="Array of etag identifiers for multipart upload validation, used to verify part integrity. Order corresponds to part numbers.")
    etags_part: list[int] = Field(default=..., validation_alias="etags[part]", serialization_alias="etags[part]", description="Array of part numbers corresponding to each etag, indicating the sequence of multipart upload segments. Order must match the etags array.")
    length: int | None = Field(default=None, description="The length of the file being uploaded in bytes.", json_schema_extra={'format': 'int32'})
    mkdir_parents: bool | None = Field(default=None, description="Whether to automatically create parent directories in the path if they do not already exist.")
    parts: int | None = Field(default=None, description="The number of parts to fetch or process for multipart uploads.", json_schema_extra={'format': 'int32'})
    provided_mtime: str | None = Field(default=None, description="User-provided modification timestamp for the uploaded file in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    size: int | None = Field(default=None, description="The total size of the file in bytes.", json_schema_extra={'format': 'int32'})
    structure: str | None = Field(default=None, description="When copying a folder, set to `true` to copy only the directory structure without file contents.")
class PostFilesPathRequest(StrictModel):
    """Upload a file to the specified path, supporting multipart uploads, append operations, and optional parent directory creation. Supports various upload actions including standard upload, append, and multipart completion."""
    path: PostFilesPathRequestPath
    body: PostFilesPathRequestBody

# Operation: update_file_metadata
class PatchFilesPathRequestPath(StrictModel):
    path: str = Field(default=..., description="The file or folder path to update.")
class PatchFilesPathRequestBody(StrictModel):
    priority_color: str | None = Field(default=None, description="Priority or bookmark color to assign to the file or folder.")
    provided_mtime: str | None = Field(default=None, description="The modification timestamp to set for the file or folder in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class PatchFilesPathRequest(StrictModel):
    """Update metadata for a file or folder, including priority color and modification timestamp."""
    path: PatchFilesPathRequestPath
    body: PatchFilesPathRequestBody | None = None

# Operation: delete_file
class DeleteFilesPathRequestPath(StrictModel):
    path: str = Field(default=..., description="The file system path to the file or folder to delete.")
class DeleteFilesPathRequestQuery(StrictModel):
    recursive: bool | None = Field(default=None, description="When true, recursively deletes folders and their contents. When false, deletion fails if the target folder is not empty.")
class DeleteFilesPathRequest(StrictModel):
    """Delete a file or folder at the specified path. Use the recursive parameter to delete non-empty folders; otherwise, deletion will fail if the folder contains items."""
    path: DeleteFilesPathRequestPath
    query: DeleteFilesPathRequestQuery | None = None

# Operation: list_folders
class FolderListForPathRequestPath(StrictModel):
    path: str = Field(default=..., description="The folder path to list contents from.")
class FolderListForPathRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    preview_size: str | None = Field(default=None, description="Size of file previews to include in the response.")
    search_all: bool | None = Field(default=None, description="When enabled, searches the entire site and ignores the specified folder path. Use only for ad-hoc human searches, not automated processes, as results are best-effort and not real-time guaranteed.")
    with_previews: bool | None = Field(default=None, description="Include file preview data in the response.")
    with_priority_color: bool | None = Field(default=None, description="Include file priority color metadata in the response.")
class FolderListForPathRequest(StrictModel):
    """List folders at a specified path with optional filtering, previews, and metadata. Supports site-wide search when enabled."""
    path: FolderListForPathRequestPath
    query: FolderListForPathRequestQuery | None = None

# Operation: create_folder
class PostFoldersPathRequestPath(StrictModel):
    path: str = Field(default=..., description="The file system path where the folder should be created.")
class PostFoldersPathRequestBody(StrictModel):
    mkdir_parents: bool | None = Field(default=None, description="Whether to automatically create any missing parent directories in the path.")
    provided_mtime: str | None = Field(default=None, description="Custom modification timestamp for the created folder in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
class PostFoldersPathRequest(StrictModel):
    """Create a new folder at the specified path. Optionally create parent directories and set a custom modification time."""
    path: PostFoldersPathRequestPath
    body: PostFoldersPathRequestBody | None = None

# Operation: list_form_field_sets
class GetFormFieldSetsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.", json_schema_extra={'format': 'int32'})
class GetFormFieldSetsRequest(StrictModel):
    """Retrieve a paginated list of form field sets. Use pagination to control the number of records returned per page."""
    query: GetFormFieldSetsRequestQuery | None = None

# Operation: create_form_field_set
class PostFormFieldSetsRequestBody(StrictModel):
    form_fields: list[PostFormFieldSetsBodyFormFieldsItem] | None = Field(default=None, description="Array of form fields to include in this set. Order is preserved and determines field display sequence. Each item should represent a field configuration.")
    title: str | None = Field(default=None, description="Display title for the form field set. Used to identify and label the set in user interfaces.")
class PostFormFieldSetsRequest(StrictModel):
    """Create a new form field set with a title and optional collection of form fields. Form field sets organize related fields for structured data collection."""
    body: PostFormFieldSetsRequestBody | None = None

# Operation: get_form_field_set
class GetFormFieldSetsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form field set to retrieve.", json_schema_extra={'format': 'int32'})
class GetFormFieldSetsIdRequest(StrictModel):
    """Retrieve a specific form field set by its ID. Returns the complete configuration and structure of the requested form field set."""
    path: GetFormFieldSetsIdRequestPath

# Operation: update_form_field_set
class PatchFormFieldSetsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form field set to update.", json_schema_extra={'format': 'int32'})
class PatchFormFieldSetsIdRequestBody(StrictModel):
    form_fields: list[PatchFormFieldSetsIdBodyFormFieldsItem] | None = Field(default=None, description="Array of form fields to associate with this field set. Order may be significant for display purposes.")
    title: str | None = Field(default=None, description="The display title for this form field set.")
class PatchFormFieldSetsIdRequest(StrictModel):
    """Update an existing form field set by modifying its title and/or associated form fields. Changes are applied to the specified form field set."""
    path: PatchFormFieldSetsIdRequestPath
    body: PatchFormFieldSetsIdRequestBody | None = None

# Operation: delete_form_field_set
class DeleteFormFieldSetsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form field set to delete.", json_schema_extra={'format': 'int32'})
class DeleteFormFieldSetsIdRequest(StrictModel):
    """Delete a form field set by its ID. This operation permanently removes the specified form field set and cannot be undone."""
    path: DeleteFormFieldSetsIdRequestPath

# Operation: list_group_users
class GetGroupUsersRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.", json_schema_extra={'format': 'int32'})
    group_id: int | None = Field(default=None, description="Group ID.  If provided, will return group_users of this group.", json_schema_extra={'format': 'int32'})
    user_id: int | None = Field(default=None, description="User ID.  If provided, will return group_users of this user.", json_schema_extra={'format': 'int32'})
class GetGroupUsersRequest(StrictModel):
    """Retrieve a paginated list of users belonging to a group. Use the per_page parameter to control result set size."""
    query: GetGroupUsersRequestQuery | None = None

# Operation: add_user_to_group
class PostGroupUsersRequestBody(StrictModel):
    admin: bool | None = Field(default=None, description="Grant group administrator privileges to the user, allowing them to manage group membership and settings.")
    group_id: int = Field(default=..., description="The ID of the group to which the user will be added.", json_schema_extra={'format': 'int32'})
    user_id: int = Field(default=..., description="The ID of the user to add to the group.", json_schema_extra={'format': 'int32'})
class PostGroupUsersRequest(StrictModel):
    """Add a user to a group with optional administrator privileges. The user will gain access to all group resources based on their assigned role."""
    body: PostGroupUsersRequestBody

# Operation: update_group_user
class PatchGroupUsersIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the group user membership record to update.", json_schema_extra={'format': 'int32'})
class PatchGroupUsersIdRequestBody(StrictModel):
    admin: bool | None = Field(default=None, description="Whether the user should have administrator privileges within the group.")
    group_id: int = Field(default=..., description="The group to which the user belongs or should be associated.", json_schema_extra={'format': 'int32'})
    user_id: int = Field(default=..., description="The user to be added or updated in the group membership.", json_schema_extra={'format': 'int32'})
class PatchGroupUsersIdRequest(StrictModel):
    """Update a user's membership in a group, including their administrator status. Modify group user associations and permissions."""
    path: PatchGroupUsersIdRequestPath
    body: PatchGroupUsersIdRequestBody

# Operation: remove_user_from_group
class DeleteGroupUsersIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the group user membership record to delete.", json_schema_extra={'format': 'int32'})
class DeleteGroupUsersIdRequestQuery(StrictModel):
    group_id: int = Field(default=..., description="The unique identifier of the group from which the user will be removed.", json_schema_extra={'format': 'int32'})
    user_id: int = Field(default=..., description="The unique identifier of the user to remove from the group.", json_schema_extra={'format': 'int32'})
class DeleteGroupUsersIdRequest(StrictModel):
    """Remove a user from a group by deleting the group membership record. This operation requires the group user ID along with the group and user IDs for verification."""
    path: DeleteGroupUsersIdRequestPath
    query: DeleteGroupUsersIdRequestQuery

# Operation: list_groups
class GetGroupsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Maximum number of group records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. The `name` field is supported for sorting.")
    ids: str | None = Field(default=None, description="Filter results to include only groups with the specified IDs. Provide as a comma-separated list of group identifiers.")
class GetGroupsRequest(StrictModel):
    """Retrieve a paginated list of groups with optional filtering by IDs and sorting capabilities. Use this operation to browse available groups in your system."""
    query: GetGroupsRequestQuery | None = None

# Operation: create_group
class PostGroupsRequestBody(StrictModel):
    admin_ids: str | None = Field(default=None, description="Comma-delimited list of user IDs to designate as group administrators. Administrators have elevated permissions within the group.")
    name: str | None = Field(default=None, description="The name of the group. Used for identification and display purposes.")
    notes: str | None = Field(default=None, description="Optional notes or description for the group. Useful for documenting the group's purpose or additional context.")
    user_ids: str | None = Field(default=None, description="Comma-delimited list of user IDs to add as members of the group. Order is not significant.")
class PostGroupsRequest(StrictModel):
    """Create a new group with specified members and administrators. Optionally include group name, notes, and assign users and admins during creation."""
    body: PostGroupsRequestBody | None = None

# Operation: update_group_membership
class PatchGroupsGroupIdMembershipsUserIdRequestPath(StrictModel):
    group_id: int = Field(default=..., description="The unique identifier of the group containing the membership to update.", json_schema_extra={'format': 'int32'})
    user_id: int = Field(default=..., description="The unique identifier of the user whose group membership should be updated.", json_schema_extra={'format': 'int32'})
class PatchGroupsGroupIdMembershipsUserIdRequestBody(StrictModel):
    admin: bool | None = Field(default=None, description="Whether the user should have administrator privileges within the group.")
class PatchGroupsGroupIdMembershipsUserIdRequest(StrictModel):
    """Update a user's membership status in a group, including their administrator privileges. Allows modification of a user's role within the specified group."""
    path: PatchGroupsGroupIdMembershipsUserIdRequestPath
    body: PatchGroupsGroupIdMembershipsUserIdRequestBody | None = None

# Operation: remove_group_member
class DeleteGroupsGroupIdMembershipsUserIdRequestPath(StrictModel):
    group_id: int = Field(default=..., description="The unique identifier of the group from which the user will be removed.", json_schema_extra={'format': 'int32'})
    user_id: int = Field(default=..., description="The unique identifier of the user to be removed from the group.", json_schema_extra={'format': 'int32'})
class DeleteGroupsGroupIdMembershipsUserIdRequest(StrictModel):
    """Remove a user from a group by deleting their membership. This operation revokes the user's access to the group."""
    path: DeleteGroupsGroupIdMembershipsUserIdRequestPath

# Operation: list_group_permissions
class GetGroupsGroupIdPermissionsRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The ID of the group for which to list permissions. Note: This parameter is deprecated; use the `filter[group_id]` query parameter for filtering instead.")
class GetGroupsGroupIdPermissionsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of permission records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort the results by a specified field in ascending or descending order. Valid sortable fields are `group_id`, `path`, `user_id`, or `permission`.")
    include_groups: bool | None = Field(default=None, description="When enabled, includes permissions inherited from the group's parent groups in addition to directly assigned permissions.")
class GetGroupsGroupIdPermissionsRequest(StrictModel):
    """Retrieve a paginated list of permissions for a specific group. Supports filtering, sorting, and optionally including inherited permissions from parent groups."""
    path: GetGroupsGroupIdPermissionsRequestPath
    query: GetGroupsGroupIdPermissionsRequestQuery | None = None

# Operation: list_group_members
class GetGroupsGroupIdUsersRequestPath(StrictModel):
    group_id: int = Field(default=..., description="The unique identifier of the group whose members you want to retrieve.", json_schema_extra={'format': 'int32'})
class GetGroupsGroupIdUsersRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of user records to return per page. Recommended to use 1,000 or less for optimal performance; maximum allowed is 10,000.", json_schema_extra={'format': 'int32'})
class GetGroupsGroupIdUsersRequest(StrictModel):
    """Retrieve a paginated list of users who are members of a specific group. Use pagination parameters to control result size and navigate through large member lists."""
    path: GetGroupsGroupIdUsersRequestPath
    query: GetGroupsGroupIdUsersRequestQuery | None = None

# Operation: create_group_user
class PostGroupsGroupIdUsersRequestPath(StrictModel):
    group_id: int = Field(default=..., description="The group ID to associate with the new user.", json_schema_extra={'format': 'int32'})
class PostGroupsGroupIdUsersRequestBody(StrictModel):
    allowed_ips: str | None = Field(default=None, description="Newline-delimited list of IP addresses permitted to access this user's account.")
    announcements_read: bool | None = Field(default=None, description="Whether the user has read all announcements displayed in the UI.")
    authenticate_until: str | None = Field(default=None, description="Date and time at which the user account will be automatically deactivated.", json_schema_extra={'format': 'date-time'})
    authentication_method: Literal["password", "unused_former_ldap", "sso", "none", "email_signup", "password_with_imported_hash"] | None = Field(default=None, description="The authentication method used for this user's login credentials.")
    billing_permission: bool | None = Field(default=None, description="Whether this user can perform operations on account settings, payments, and invoices.")
    bypass_inactive_disable: bool | None = Field(default=None, description="Whether this user is exempt from automatic deactivation due to inactivity.")
    bypass_site_allowed_ips: bool | None = Field(default=None, description="Whether this user can bypass site-wide IP blacklist restrictions.")
    company: str | None = Field(default=None, description="The user's company or organization name.")
    dav_permission: bool | None = Field(default=None, description="Whether the user can connect and authenticate via WebDAV protocol.")
    disabled: bool | None = Field(default=None, description="Whether the user account is disabled. Disabled users cannot log in and do not consume billing seats.")
    email: str | None = Field(default=None, description="The user's email address.")
    ftp_permission: bool | None = Field(default=None, description="Whether the user can access files and folders via FTP or FTPS protocols.")
    grant_permission: str | None = Field(default=None, description="Permission level to grant on the user's root folder. Options include full access, read-only, write, list, or history.")
    header_text: str | None = Field(default=None, description="Custom text message displayed to the user in the UI header.")
    language: str | None = Field(default=None, description="The user's preferred language for the UI.")
    name: str | None = Field(default=None, description="The user's full name.")
    notes: str | None = Field(default=None, description="Internal notes or comments about the user for administrative reference.")
    notification_daily_send_time: int | None = Field(default=None, description="The hour of the day (0-23) when daily notifications should be sent to the user.", json_schema_extra={'format': 'int32'})
    office_integration_enabled: bool | None = Field(default=None, description="Whether to enable integration with Microsoft Office for the web applications.")
    password_validity_days: int | None = Field(default=None, description="Number of days a user can use the same password before being required to change it.", json_schema_extra={'format': 'int32'})
    receive_admin_alerts: bool | None = Field(default=None, description="Whether the user receives administrative alerts such as certificate expiration and usage overages.")
    require_2fa: Literal["use_system_setting", "always_require", "never_require"] | None = Field(default=None, description="Whether two-factor authentication is required for this user's login.")
    require_password_change: bool | None = Field(default=None, description="Whether the user must change their password on the next login.")
    restapi_permission: bool | None = Field(default=None, description="Whether the user can authenticate and access the REST API.")
    self_managed: bool | None = Field(default=None, description="Whether this user manages their own credentials or is a shared/bot account with managed credentials.")
    sftp_permission: bool | None = Field(default=None, description="Whether the user can access files and folders via SFTP protocol.")
    site_admin: bool | None = Field(default=None, description="Whether the user has administrator privileges for this site.")
    skip_welcome_screen: bool | None = Field(default=None, description="Whether to skip displaying the welcome screen to the user on first login.")
    ssl_required: Literal["use_system_setting", "always_require", "never_require"] | None = Field(default=None, description="Whether SSL/TLS encryption is required for this user's connections.")
    sso_strategy_id: int | None = Field(default=None, description="The ID of the SSO (Single Sign On) strategy to use for this user's authentication.", json_schema_extra={'format': 'int32'})
    subscribe_to_newsletter: bool | None = Field(default=None, description="Whether the user is subscribed to receive newsletter communications.")
    time_zone: str | None = Field(default=None, description="The user's time zone for scheduling and time-based operations.")
    user_root: str | None = Field(default=None, description="Root folder path for FTP access and optionally SFTP if configured site-wide. Not used for API, desktop, or web interface access.")
    username: str | None = Field(default=None, description="User's username")
class PostGroupsGroupIdUsersRequest(StrictModel):
    """Create a new user within a specified group with configurable authentication, permissions, and access settings."""
    path: PostGroupsGroupIdUsersRequestPath
    body: PostGroupsGroupIdUsersRequestBody | None = None

# Operation: get_group
class GetGroupsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the group to retrieve.", json_schema_extra={'format': 'int32'})
class GetGroupsIdRequest(StrictModel):
    """Retrieve detailed information about a specific group by its ID."""
    path: GetGroupsIdRequestPath

# Operation: update_group
class PatchGroupsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the group to update.", json_schema_extra={'format': 'int32'})
class PatchGroupsIdRequestBody(StrictModel):
    admin_ids: str | None = Field(default=None, description="Comma-separated list of user IDs to designate as group administrators.")
    name: str | None = Field(default=None, description="The name of the group.")
    notes: str | None = Field(default=None, description="Additional notes or description for the group.")
    user_ids: str | None = Field(default=None, description="Comma-separated list of user IDs to add as members of the group.")
class PatchGroupsIdRequest(StrictModel):
    """Update an existing group's properties including name, notes, members, and administrators. Provide only the fields you want to modify."""
    path: PatchGroupsIdRequestPath
    body: PatchGroupsIdRequestBody | None = None

# Operation: delete_group
class DeleteGroupsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the group to delete.", json_schema_extra={'format': 'int32'})
class DeleteGroupsIdRequest(StrictModel):
    """Permanently delete a group by its ID. This action cannot be undone."""
    path: DeleteGroupsIdRequestPath

# Operation: list_history
class HistoryListRequestQuery(StrictModel):
    start_at: str | None = Field(default=None, description="Filter to exclude history entries before this date and time. Leave blank to include all earlier entries.", json_schema_extra={'format': 'date-time'})
    end_at: str | None = Field(default=None, description="Filter to exclude history entries after this date and time. Leave blank to include all later entries.", json_schema_extra={'format': 'date-time'})
    display: str | None = Field(default=None, description="Control the detail level of returned history entries. Use `full` for complete details or `parent` for parent-only view. Leave blank for default format.")
    per_page: int | None = Field(default=None, description="Number of history records to return per page. Maximum allowed is 10,000, though 1,000 or fewer is recommended for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict | None = Field(default=None, description="If set, sort records by the specified field in either `asc` or `desc` direction (e.g. `sort_by[path]=desc`). Valid fields are `path`, `folder`, `user_id` or `created_at`.")
class HistoryListRequest(StrictModel):
    """Retrieve the complete action history for the site with optional filtering by date range and customizable display format."""
    query: HistoryListRequestQuery | None = None

# Operation: list_file_history
class HistoryListForFileRequestPath(StrictModel):
    path: str = Field(default=..., description="The file path to retrieve history for.")
class HistoryListForFileRequestQuery(StrictModel):
    start_at: str | None = Field(default=None, description="Filter to only include history entries created on or after this date and time.", json_schema_extra={'format': 'date-time'})
    end_at: str | None = Field(default=None, description="Filter to only include history entries created on or before this date and time.", json_schema_extra={'format': 'date-time'})
    display: str | None = Field(default=None, description="Control the detail level of returned records. Use `full` for complete details or `parent` for parent-only information.")
    per_page: int | None = Field(default=None, description="Number of records to return per page. Maximum is 10,000; 1,000 or less is recommended.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Use object notation (e.g., `sort_by[user_id]=desc`). Valid fields are `user_id` and `created_at`.")
class HistoryListForFileRequest(StrictModel):
    """Retrieve the change history for a specific file, with optional filtering by date range and customizable sorting and pagination."""
    path: HistoryListForFileRequestPath
    query: HistoryListForFileRequestQuery | None = None

# Operation: list_folder_history
class HistoryListForFolderRequestPath(StrictModel):
    path: str = Field(default=..., description="The folder path for which to retrieve history.")
class HistoryListForFolderRequestQuery(StrictModel):
    start_at: str | None = Field(default=None, description="Filter to exclude history entries created before this date and time.", json_schema_extra={'format': 'date-time'})
    end_at: str | None = Field(default=None, description="Filter to exclude history entries created after this date and time.", json_schema_extra={'format': 'date-time'})
    display: str | None = Field(default=None, description="Control the detail level of returned records: `full` for complete details or `parent` for parent-only information.")
    per_page: int | None = Field(default=None, description="Number of history records to return per page. Recommended maximum is 1,000 for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Supported fields are `user_id` and `created_at`.")
class HistoryListForFolderRequest(StrictModel):
    """Retrieve the change history for a specific folder, with optional filtering by date range and customizable sorting and pagination."""
    path: HistoryListForFolderRequestPath
    query: HistoryListForFolderRequestQuery | None = None

# Operation: list_logins
class HistoryListLoginsRequestQuery(StrictModel):
    start_at: str | None = Field(default=None, description="Filter to exclude login records before this date and time. Leave blank to include all earlier entries.", json_schema_extra={'format': 'date-time'})
    end_at: str | None = Field(default=None, description="Filter to exclude login records after this date and time. Leave blank to include all later entries.", json_schema_extra={'format': 'date-time'})
    display: str | None = Field(default=None, description="Control the response format. Use `full` for complete details or `parent` for parent-level information only.")
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended maximum is 1,000 for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Use format `sort_by[field_name]=direction` where field_name is `user_id` or `created_at` and direction is `asc` or `desc`.")
class HistoryListLoginsRequest(StrictModel):
    """Retrieve a paginated list of site login history with optional filtering by date range and sorting capabilities."""
    query: HistoryListLoginsRequestQuery | None = None

# Operation: list_user_history
class HistoryListForUserRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user whose history records should be retrieved.", json_schema_extra={'format': 'int32'})
class HistoryListForUserRequestQuery(StrictModel):
    start_at: str | None = Field(default=None, description="Filter to exclude history entries created before this date and time. Leave blank to include all earlier entries.", json_schema_extra={'format': 'date-time'})
    end_at: str | None = Field(default=None, description="Filter to exclude history entries created after this date and time. Leave blank to include all later entries.", json_schema_extra={'format': 'date-time'})
    display: str | None = Field(default=None, description="Control the detail level of returned records. Use `full` for complete details or `parent` for parent-only information.")
    per_page: int | None = Field(default=None, description="Maximum number of records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Use field names `user_id` or `created_at` with direction indicators.")
class HistoryListForUserRequest(StrictModel):
    """Retrieve a paginated list of history records for a specific user, with optional filtering by date range and customizable sorting and display format."""
    path: HistoryListForUserRequestPath
    query: HistoryListForUserRequestQuery | None = None

# Operation: list_history_export_results
class GetHistoryExportResultsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of results to return per page. Recommended to use 1,000 or less for optimal performance, though up to 10,000 is supported.", json_schema_extra={'format': 'int32'})
    history_export_id: int = Field(default=..., description="The unique identifier of the history export whose results you want to retrieve.", json_schema_extra={'format': 'int32'})
class GetHistoryExportResultsRequest(StrictModel):
    """Retrieve a paginated list of results from a completed history export. Use the history export ID to fetch the exported records with configurable page size."""
    query: GetHistoryExportResultsRequestQuery

# Operation: create_history_export
class PostHistoryExportsRequestBody(StrictModel):
    end_at: str | None = Field(default=None, description="End date and time for the export range (inclusive). Use ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    query_action: str | None = Field(default=None, description="Filter exported history records by action type performed (e.g., file operations, user management, authentication events).")
    query_destination: str | None = Field(default=None, description="Filter results to include only file move operations with this destination path.")
    query_failure_type: str | None = Field(default=None, description="When filtering for login failures, restrict results to failures of this specific type.")
    query_file_id: str | None = Field(default=None, description="Filter results to include only actions related to the specified file ID.")
    query_folder: str | None = Field(default=None, description="Filter results to include only actions on files or folders within this folder path.")
    query_interface: str | None = Field(default=None, description="Filter exported history records by the interface or protocol used to perform the action.")
    query_ip: str | None = Field(default=None, description="Filter results to include only actions originating from this IP address.")
    query_parent_id: str | None = Field(default=None, description="Filter results to include only actions within the parent folder specified by this folder ID.")
    query_path: str | None = Field(default=None, description="Filter results to include only actions related to this file or folder path.")
    query_src: str | None = Field(default=None, description="Filter results to include only file move operations originating from this source path.")
    query_target_id: str | None = Field(default=None, description="Filter results to include only actions on objects (users, API keys, etc.) matching this target object ID.")
    query_target_name: str | None = Field(default=None, description="Filter results to include only actions on objects (users, groups, etc.) matching this name or username.")
    query_target_permission: str | None = Field(default=None, description="When filtering for permission-related actions, restrict results to permissions at this access level.")
    query_target_permission_set: str | None = Field(default=None, description="When filtering for API key actions, restrict results to API keys with this permission set.")
    query_target_platform: str | None = Field(default=None, description="When filtering for API key actions, restrict results to API keys associated with this platform.")
    query_user_id: str | None = Field(default=None, description="Filter results to include only actions performed by the user with this user ID.")
    query_username: str | None = Field(default=None, description="Filter results to include only actions performed by this username.")
    start_at: str | None = Field(default=None, description="Start date and time for the export range (inclusive). Use ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class PostHistoryExportsRequest(StrictModel):
    """Initiate a history export with optional filtering by date range, user, action type, interface, and target object. Returns an export job that can be monitored for completion."""
    body: PostHistoryExportsRequestBody | None = None

# Operation: get_history_export
class GetHistoryExportsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the history export to retrieve.", json_schema_extra={'format': 'int32'})
class GetHistoryExportsIdRequest(StrictModel):
    """Retrieve details of a specific history export by its ID. Use this to check the status, metadata, and information about a previously created history export."""
    path: GetHistoryExportsIdRequestPath

# Operation: list_inbox_recipients
class GetInboxRecipientsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Maximum number of records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Only `has_registrations` is supported as a sortable field.")
    inbox_id: int = Field(default=..., description="The unique identifier of the inbox for which to list recipients.", json_schema_extra={'format': 'int32'})
class GetInboxRecipientsRequest(StrictModel):
    """Retrieve a list of recipients associated with a specific inbox. Use sorting and pagination to manage large result sets."""
    query: GetInboxRecipientsRequestQuery

# Operation: share_inbox_with_recipient
class PostInboxRecipientsRequestBody(StrictModel):
    company: str | None = Field(default=None, description="Company name associated with the recipient for organizational context.")
    inbox_id: int = Field(default=..., description="The ID of the inbox to be shared with the recipient.", json_schema_extra={'format': 'int32'})
    name: str | None = Field(default=None, description="Full name of the recipient for identification purposes.")
    note: str | None = Field(default=None, description="Optional message to include in the notification email sent to the recipient.")
    recipient: str = Field(default=..., description="Email address of the recipient who will receive access to the inbox.")
    share_after_create: bool | None = Field(default=None, description="When true, automatically sends a sharing notification email to the recipient upon creation.")
class PostInboxRecipientsRequest(StrictModel):
    """Grant a recipient access to an inbox by sharing it with their email address. Optionally send them a notification email upon creation."""
    body: PostInboxRecipientsRequestBody

# Operation: list_inbox_registrations
class GetInboxRegistrationsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.", json_schema_extra={'format': 'int32'})
    folder_behavior_id: int | None = Field(default=None, description="Filter results by the ID of the associated inbox. When provided, only registrations for that specific inbox are returned.", json_schema_extra={'format': 'int32'})
class GetInboxRegistrationsRequest(StrictModel):
    """Retrieve a paginated list of inbox registrations, optionally filtered by a specific inbox. Use pagination parameters to control result set size."""
    query: GetInboxRegistrationsRequestQuery | None = None

# Operation: list_inbox_uploads
class GetInboxUploadsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Only `created_at` is supported as a valid sort field.")
    inbox_registration_id: int | None = Field(default=None, description="Filter uploads by the associated inbox registration ID.", json_schema_extra={'format': 'int32'})
    inbox_id: int | None = Field(default=None, description="Filter uploads by the associated inbox ID.", json_schema_extra={'format': 'int32'})
class GetInboxUploadsRequest(StrictModel):
    """Retrieve a paginated list of uploads associated with inboxes. Filter by specific inbox or inbox registration, and optionally sort results by creation date."""
    query: GetInboxUploadsRequestQuery | None = None

# Operation: list_invoices
class GetInvoicesRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of invoice records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
class GetInvoicesRequest(StrictModel):
    """Retrieve a paginated list of invoices. Use the per_page parameter to control the number of results returned per page."""
    query: GetInvoicesRequestQuery | None = None

# Operation: get_invoice
class GetInvoicesIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the invoice to retrieve.", json_schema_extra={'format': 'int32'})
class GetInvoicesIdRequest(StrictModel):
    """Retrieve a specific invoice by its ID. Returns detailed invoice information including amounts, dates, and line items."""
    path: GetInvoicesIdRequestPath

# Operation: list_ip_addresses
class GetIpAddressesRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, though the API supports up to 10,000 records per page.", json_schema_extra={'format': 'int32'})
class GetIpAddressesRequest(StrictModel):
    """Retrieve a paginated list of IP addresses associated with the current site. Use the per_page parameter to control result set size."""
    query: GetIpAddressesRequestQuery | None = None

# Operation: list_exavault_reserved_ip_addresses
class GetIpAddressesExavaultReservedRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000 records per page.", json_schema_extra={'format': 'int32'})
class GetIpAddressesExavaultReservedRequest(StrictModel):
    """Retrieve a paginated list of all public IP addresses reserved and used by ExaVault for its services. Use this to configure firewall rules or IP allowlists for ExaVault connectivity."""
    query: GetIpAddressesExavaultReservedRequestQuery | None = None

# Operation: list_reserved_ip_addresses
class GetIpAddressesReservedRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000 records per page.", json_schema_extra={'format': 'int32'})
class GetIpAddressesReservedRequest(StrictModel):
    """Retrieve a paginated list of all reserved public IP addresses available in the system."""
    query: GetIpAddressesReservedRequestQuery | None = None

# Operation: list_locks
class LockListForPathRequestPath(StrictModel):
    path: str = Field(default=..., description="The resource path for which to retrieve locks.")
class LockListForPathRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.", json_schema_extra={'format': 'int32'})
    include_children: bool | None = Field(default=None, description="Whether to include locks from child objects in addition to the specified path.")
class LockListForPathRequest(StrictModel):
    """Retrieve all locks for a specified path, with optional support for including locks from child objects and pagination control."""
    path: LockListForPathRequestPath
    query: LockListForPathRequestQuery | None = None

# Operation: release_lock
class DeleteLocksPathRequestPath(StrictModel):
    path: str = Field(default=..., description="The resource path for which the lock should be released.")
class DeleteLocksPathRequestQuery(StrictModel):
    token: str = Field(default=..., description="The unique token that identifies and authorizes the release of this specific lock.")
class DeleteLocksPathRequest(StrictModel):
    """Release a lock on a resource by providing its path and token. This removes the lock, allowing other operations to proceed."""
    path: DeleteLocksPathRequestPath
    query: DeleteLocksPathRequestQuery

# Operation: list_message_comment_reactions
class GetMessageCommentReactionsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Maximum number of reactions to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    message_comment_id: int = Field(default=..., description="The ID of the message comment for which to retrieve reactions.", json_schema_extra={'format': 'int32'})
class GetMessageCommentReactionsRequest(StrictModel):
    """Retrieve all reactions added to a specific message comment. Results are paginated and can be controlled via the per_page parameter."""
    query: GetMessageCommentReactionsRequestQuery

# Operation: get_message_comment_reaction
class GetMessageCommentReactionsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the message comment reaction to retrieve.", json_schema_extra={'format': 'int32'})
class GetMessageCommentReactionsIdRequest(StrictModel):
    """Retrieve details of a specific message comment reaction by its ID. Use this to fetch information about a user's reaction to a message comment."""
    path: GetMessageCommentReactionsIdRequestPath

# Operation: remove_message_comment_reaction
class DeleteMessageCommentReactionsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the message comment reaction to delete.", json_schema_extra={'format': 'int32'})
class DeleteMessageCommentReactionsIdRequest(StrictModel):
    """Remove a reaction from a message comment. Deletes the specified reaction by its ID."""
    path: DeleteMessageCommentReactionsIdRequestPath

# Operation: list_message_comments
class GetMessageCommentsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Maximum number of comments to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    message_id: int = Field(default=..., description="The ID of the message for which to retrieve comments.", json_schema_extra={'format': 'int32'})
class GetMessageCommentsRequest(StrictModel):
    """Retrieve all comments associated with a specific message. Results are paginated and can be controlled via the per_page parameter."""
    query: GetMessageCommentsRequestQuery

# Operation: get_message_comment
class GetMessageCommentsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the message comment to retrieve.", json_schema_extra={'format': 'int32'})
class GetMessageCommentsIdRequest(StrictModel):
    """Retrieve a specific message comment by its ID. Returns the full details of the requested comment."""
    path: GetMessageCommentsIdRequestPath

# Operation: update_message_comment
class PatchMessageCommentsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the message comment to update.", json_schema_extra={'format': 'int32'})
class PatchMessageCommentsIdRequestBody(StrictModel):
    body: str = Field(default=..., description="The updated text content for the message comment.")
class PatchMessageCommentsIdRequest(StrictModel):
    """Update the body text of an existing message comment. Allows modification of comment content after initial creation."""
    path: PatchMessageCommentsIdRequestPath
    body: PatchMessageCommentsIdRequestBody

# Operation: delete_message_comment
class DeleteMessageCommentsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the message comment to delete.", json_schema_extra={'format': 'int32'})
class DeleteMessageCommentsIdRequest(StrictModel):
    """Delete a specific message comment by its ID. This operation permanently removes the comment from the message thread."""
    path: DeleteMessageCommentsIdRequestPath

# Operation: list_message_reactions
class GetMessageReactionsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Maximum number of reactions to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    message_id: int = Field(default=..., description="The ID of the message to retrieve reactions for.", json_schema_extra={'format': 'int32'})
class GetMessageReactionsRequest(StrictModel):
    """Retrieve all reactions added to a specific message. Supports pagination to control the number of results returned per page."""
    query: GetMessageReactionsRequestQuery

# Operation: get_message_reaction
class GetMessageReactionsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the message reaction to retrieve.", json_schema_extra={'format': 'int32'})
class GetMessageReactionsIdRequest(StrictModel):
    """Retrieve details of a specific message reaction by its ID. Use this to fetch information about a single reaction to a message."""
    path: GetMessageReactionsIdRequestPath

# Operation: remove_message_reaction
class DeleteMessageReactionsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the message reaction to delete.", json_schema_extra={'format': 'int32'})
class DeleteMessageReactionsIdRequest(StrictModel):
    """Remove a reaction from a message by its reaction ID. This deletes the association between the user and the message reaction."""
    path: DeleteMessageReactionsIdRequestPath

# Operation: list_messages
class GetMessagesRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of messages to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    project_id: int = Field(default=..., description="The project ID for which to retrieve messages. Required to scope results to a specific project.", json_schema_extra={'format': 'int32'})
class GetMessagesRequest(StrictModel):
    """Retrieve a paginated list of messages for a specific project. Use pagination parameters to control the number of results returned per page."""
    query: GetMessagesRequestQuery

# Operation: create_message
class PostMessagesRequestBody(StrictModel):
    body: str = Field(default=..., description="The content of the message to be created.")
    project_id: int = Field(default=..., description="The unique identifier of the project to which this message should be attached.", json_schema_extra={'format': 'int32'})
    subject: str = Field(default=..., description="The subject line or title for the message.")
class PostMessagesRequest(StrictModel):
    """Create a new message attached to a specific project. Messages can be used for project communication and collaboration."""
    body: PostMessagesRequestBody

# Operation: get_message
class GetMessagesIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the message to retrieve.", json_schema_extra={'format': 'int32'})
class GetMessagesIdRequest(StrictModel):
    """Retrieve a specific message by its ID. Returns the full message details including content, metadata, and timestamps."""
    path: GetMessagesIdRequestPath

# Operation: update_message
class PatchMessagesIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the message to update.", json_schema_extra={'format': 'int32'})
class PatchMessagesIdRequestBody(StrictModel):
    body: str = Field(default=..., description="The new content body for the message.")
    project_id: int = Field(default=..., description="The project ID to which this message should be attached or reassigned.", json_schema_extra={'format': 'int32'})
    subject: str = Field(default=..., description="The new subject line for the message.")
class PatchMessagesIdRequest(StrictModel):
    """Update an existing message with new subject and body content. The message will be associated with the specified project."""
    path: PatchMessagesIdRequestPath
    body: PatchMessagesIdRequestBody

# Operation: delete_message
class DeleteMessagesIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the message to delete.", json_schema_extra={'format': 'int32'})
class DeleteMessagesIdRequest(StrictModel):
    """Permanently delete a message by its ID. This action cannot be undone."""
    path: DeleteMessagesIdRequestPath

# Operation: list_notifications
class GetNotificationsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Maximum number of notification records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Valid sortable fields are `path`, `user_id`, or `group_id`.")
    include_ancestors: bool | None = Field(default=None, description="When enabled and a `path` filter is applied, include notifications from all parent paths in addition to the specified path. Has no effect if `path` is not specified.")
class GetNotificationsRequest(StrictModel):
    """Retrieve a paginated list of notifications with optional sorting and ancestor path inclusion. Use this to display notification feeds or audit logs with flexible filtering options."""
    query: GetNotificationsRequestQuery | None = None

# Operation: create_notification
class PostNotificationsRequestBody(StrictModel):
    message: str | None = Field(default=None, description="Custom message to include in notification emails sent when the rule is triggered.")
    notify_on_copy: bool | None = Field(default=None, description="When enabled, copying or moving resources into this path will trigger a notification in addition to upload events.")
    notify_on_delete: bool | None = Field(default=None, description="When enabled, deleting files from this path will trigger a notification.")
    notify_on_download: bool | None = Field(default=None, description="When enabled, downloading files from this path will trigger a notification.")
    notify_on_move: bool | None = Field(default=None, description="When enabled, moving files to this path will trigger a notification.")
    notify_on_upload: bool | None = Field(default=None, description="When enabled, uploading new files to this path will trigger a notification.")
    notify_user_actions: bool | None = Field(default=None, description="When enabled, actions initiated by the user account itself will still result in a notification.")
    recursive: bool | None = Field(default=None, description="When enabled, notifications will be triggered for actions in all subfolders under this path.")
    send_interval: str | None = Field(default=None, description="The time interval over which notifications are aggregated before being sent. Longer intervals batch multiple events into a single notification.")
    trigger_by_share_recipients: bool | None = Field(default=None, description="When enabled, notifications will be triggered for actions performed by users who have access through a share link or shared folder.")
    triggering_filenames: list[str] | None = Field(default=None, description="Array of filename patterns to match against the action path. Supports wildcards to filter which files trigger notifications. Patterns are evaluated in order.")
    triggering_group_ids: list[int] | None = Field(default=None, description="Array of group IDs. When specified, only actions performed by members of these groups will trigger notifications.")
    triggering_user_ids: list[int] | None = Field(default=None, description="Array of user IDs. When specified, only actions performed by these users will trigger notifications.")
    path: str | None = Field(default=None, description="Path")
    user_id: int | None = Field(default=None, description="The id of the user to notify. Provide `user_id`, `username` or `group_id`.", json_schema_extra={'format': 'int32'})
    group_id: int | None = Field(default=None, description="The ID of the group to notify.  Provide `user_id`, `username` or `group_id`.", json_schema_extra={'format': 'int32'})
class PostNotificationsRequest(StrictModel):
    """Create a notification rule that triggers on specified file system actions within a path. Configure which actions trigger notifications, who performs them, and how notifications are aggregated."""
    body: PostNotificationsRequestBody | None = None

# Operation: get_notification
class GetNotificationsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the notification to retrieve.", json_schema_extra={'format': 'int32'})
class GetNotificationsIdRequest(StrictModel):
    """Retrieve a specific notification by its ID. Returns the full details of the requested notification."""
    path: GetNotificationsIdRequestPath

# Operation: update_notification
class PatchNotificationsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the notification rule to update.", json_schema_extra={'format': 'int32'})
class PatchNotificationsIdRequestBody(StrictModel):
    message: str | None = Field(default=None, description="Custom message text to include in notification emails sent for this rule.")
    notify_on_copy: bool | None = Field(default=None, description="When enabled, copying or moving resources into the monitored path will trigger notifications in addition to upload events.")
    notify_on_delete: bool | None = Field(default=None, description="When enabled, file deletions from the monitored path will trigger notifications.")
    notify_on_download: bool | None = Field(default=None, description="When enabled, file downloads from the monitored path will trigger notifications.")
    notify_on_move: bool | None = Field(default=None, description="When enabled, file moves to the monitored path will trigger notifications.")
    notify_on_upload: bool | None = Field(default=None, description="When enabled, file uploads to the monitored path will trigger notifications.")
    notify_user_actions: bool | None = Field(default=None, description="When enabled, notifications will be sent for actions initiated by the user account itself, not just external actions.")
    recursive: bool | None = Field(default=None, description="When enabled, notifications will apply to all subfolders within the monitored path.")
    send_interval: str | None = Field(default=None, description="The time interval over which notifications are aggregated before sending. Valid values are five_minutes, fifteen_minutes, hourly, or daily.")
    trigger_by_share_recipients: bool | None = Field(default=None, description="When enabled, actions performed by share recipients will trigger notifications.")
    triggering_filenames: list[str] | None = Field(default=None, description="Array of filename patterns (supporting wildcards) to match against action paths. Only actions on matching files will trigger notifications.")
    triggering_group_ids: list[int] | None = Field(default=None, description="Array of group IDs. When specified, only actions performed by members of these groups will trigger notifications.")
    triggering_user_ids: list[int] | None = Field(default=None, description="Array of user IDs. When specified, only actions performed by these users will trigger notifications.")
class PatchNotificationsIdRequest(StrictModel):
    """Update notification settings for a specific notification rule, including trigger conditions, aggregation intervals, and recipient filters."""
    path: PatchNotificationsIdRequestPath
    body: PatchNotificationsIdRequestBody | None = None

# Operation: delete_notification
class DeleteNotificationsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the notification to delete.", json_schema_extra={'format': 'int32'})
class DeleteNotificationsIdRequest(StrictModel):
    """Permanently delete a notification by its ID. This action cannot be undone."""
    path: DeleteNotificationsIdRequestPath

# Operation: list_payments
class GetPaymentsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of payment records to return per page. Recommended to use 1,000 or less for optimal performance, though up to 10,000 is supported.", json_schema_extra={'format': 'int32'})
class GetPaymentsRequest(StrictModel):
    """Retrieve a paginated list of payments. Use the per_page parameter to control the number of records returned per page."""
    query: GetPaymentsRequestQuery | None = None

# Operation: get_payment
class GetPaymentsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the payment to retrieve.", json_schema_extra={'format': 'int32'})
class GetPaymentsIdRequest(StrictModel):
    """Retrieve details for a specific payment by its ID. Returns the payment information including amount, status, and transaction details."""
    path: GetPaymentsIdRequestPath

# Operation: list_permissions
class GetPermissionsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, though up to 10,000 is supported.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Valid sortable fields are: group_id, path, user_id, or permission.")
    include_groups: bool | None = Field(default=None, description="When filtering by user or group, include permissions inherited from the user's group memberships in addition to directly assigned permissions.")
class GetPermissionsRequest(StrictModel):
    """Retrieve a paginated list of permissions with optional sorting and group inheritance filtering. Use this to view all permissions in the system, optionally including permissions inherited from group memberships."""
    query: GetPermissionsRequestQuery | None = None

# Operation: create_permission
class PostPermissionsRequestBody(StrictModel):
    permission: str | None = Field(default=None, description="The access level type to assign. Determines what actions are permitted.")
    recursive: bool | None = Field(default=None, description="Whether to apply this permission to all subfolders in addition to the target folder.")
    path: str | None = Field(default=None, description="Folder path")
    user_id: int | None = Field(default=None, description="User ID.  Provide `username` or `user_id`", json_schema_extra={'format': 'int32'})
    group_id: int | None = Field(default=None, description="Group ID", json_schema_extra={'format': 'int32'})
class PostPermissionsRequest(StrictModel):
    """Create a new permission with specified access level and optional recursive application to subfolders."""
    body: PostPermissionsRequestBody | None = None

# Operation: delete_permission
class DeletePermissionsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the permission to delete.", json_schema_extra={'format': 'int32'})
class DeletePermissionsIdRequest(StrictModel):
    """Delete a permission by its ID. This operation permanently removes the specified permission from the system."""
    path: DeletePermissionsIdRequestPath

# Operation: create_project
class PostProjectsRequestBody(StrictModel):
    global_access: str = Field(default=..., description="Sets the global access level for the project, controlling visibility and permissions for all users in the organization.")
class PostProjectsRequest(StrictModel):
    """Create a new project with specified global access permissions. Global access determines who can view or modify the project across your organization."""
    body: PostProjectsRequestBody

# Operation: get_project
class GetProjectsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the project to retrieve.", json_schema_extra={'format': 'int32'})
class GetProjectsIdRequest(StrictModel):
    """Retrieve detailed information about a specific project by its ID."""
    path: GetProjectsIdRequestPath

# Operation: delete_project
class DeleteProjectsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the project to delete.", json_schema_extra={'format': 'int32'})
class DeleteProjectsIdRequest(StrictModel):
    """Permanently delete a project by its ID. This action cannot be undone."""
    path: DeleteProjectsIdRequestPath

# Operation: list_public_keys
class GetPublicKeysRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.", json_schema_extra={'format': 'int32'})
class GetPublicKeysRequest(StrictModel):
    """Retrieve a paginated list of public keys. Use the per_page parameter to control the number of results returned per page."""
    query: GetPublicKeysRequestQuery | None = None

# Operation: create_public_key
class PostPublicKeysRequestBody(StrictModel):
    public_key: str = Field(default=..., description="The complete SSH public key content in standard format (typically starting with ssh-rsa, ssh-ed25519, or similar).")
    title: str = Field(default=..., description="A descriptive name or label for this public key to help identify it among multiple keys.")
class PostPublicKeysRequest(StrictModel):
    """Create a new SSH public key for authentication. The key is stored with an internal reference title for easy identification."""
    body: PostPublicKeysRequestBody

# Operation: get_public_key
class GetPublicKeysIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the public key to retrieve.", json_schema_extra={'format': 'int32'})
class GetPublicKeysIdRequest(StrictModel):
    """Retrieve a specific public key by its ID. Use this to fetch details of a previously created or stored public key."""
    path: GetPublicKeysIdRequestPath

# Operation: update_public_key
class PatchPublicKeysIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the public key to update.", json_schema_extra={'format': 'int32'})
class PatchPublicKeysIdRequestBody(StrictModel):
    title: str = Field(default=..., description="A descriptive name or label for the public key used for internal reference and identification.")
class PatchPublicKeysIdRequest(StrictModel):
    """Update the title or metadata of an existing public key. This allows you to change the internal reference name for a key that has already been created."""
    path: PatchPublicKeysIdRequestPath
    body: PatchPublicKeysIdRequestBody

# Operation: delete_public_key
class DeletePublicKeysIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the public key to delete.", json_schema_extra={'format': 'int32'})
class DeletePublicKeysIdRequest(StrictModel):
    """Permanently delete a public key by its ID. This action cannot be undone."""
    path: DeletePublicKeysIdRequestPath

# Operation: list_bandwidth_snapshots_remote
class GetRemoteBandwidthSnapshotsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Use the field name as the key and 'asc' or 'desc' as the value. Valid sortable field is 'logged_at'.")
class GetRemoteBandwidthSnapshotsRequest(StrictModel):
    """Retrieve a paginated list of remote bandwidth snapshots. Results can be sorted by the logged timestamp in ascending or descending order."""
    query: GetRemoteBandwidthSnapshotsRequestQuery | None = None

# Operation: list_remote_servers
class GetRemoteServersRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.", json_schema_extra={'format': 'int32'})
class GetRemoteServersRequest(StrictModel):
    """Retrieve a paginated list of remote servers. Use the per_page parameter to control the number of results returned per page."""
    query: GetRemoteServersRequestQuery | None = None

# Operation: create_remote_server
class PostRemoteServersRequestBody(StrictModel):
    enable_dedicated_ips: bool | None = Field(default=None, description="When enabled, restricts remote server connections to dedicated IP addresses only.")
    files_agent_permission_set: Literal["read_write", "read_only", "write_only"] | None = Field(default=None, description="File permissions level for the files agent: read_only allows downloads only, write_only allows uploads only, read_write allows both operations.")
    files_agent_root: str | None = Field(default=None, description="Local root directory path where the files agent will access files.")
    max_connections: int | None = Field(default=None, description="Maximum number of parallel connections to the remote server. Ignored for S3 connections which parallelize automatically.", json_schema_extra={'format': 'int32'})
    name: str | None = Field(default=None, description="Internal display name for this remote server configuration.")
    one_drive_account_type: Literal["personal", "business_other"] | None = Field(default=None, description="OneDrive account type: personal for individual accounts or business_other for business/organizational accounts.")
    pin_to_site_region: bool | None = Field(default=None, description="When enabled, all communications with this remote server route through the primary region of the site. Can be overridden by site-wide settings.")
    private_key: str | None = Field(default=None, description="Private key for SFTP or other key-based authentication methods.")
    private_key_passphrase: str | None = Field(default=None, description="Passphrase to decrypt the private key if it is encrypted.")
    s3_bucket: str | None = Field(default=None, description="AWS S3 bucket name where files will be stored.")
    s3_region: str | None = Field(default=None, description="AWS region code where the S3 bucket is located.")
    server_certificate: Literal["require_match", "allow_any"] | None = Field(default=None, description="SSL certificate validation mode: require_match enforces exact certificate matching, allow_any accepts any valid certificate.")
    server_host_key: str | None = Field(default=None, description="Remote server SSH host key in OpenSSH format (as would appear in ~/.ssh/known_hosts). When provided, the server's host key must match exactly.")
    server_type: Literal["ftp", "sftp", "s3", "google_cloud_storage", "webdav", "wasabi", "backblaze_b2", "one_drive", "rackspace", "box", "dropbox", "google_drive", "azure", "sharepoint", "s3_compatible", "azure_files", "files_agent", "filebase"] | None = Field(default=None, description="Type of remote server to configure. Determines which authentication credentials and configuration parameters are required.")
    ssl: Literal["if_available", "require", "require_implicit", "never"] | None = Field(default=None, description="SSL/TLS requirement level: if_available uses SSL when supported, require enforces SSL, require_implicit uses implicit SSL, never disables SSL.")
    ssl_certificate: str | None = Field(default=None, description="SSL client certificate for mutual TLS authentication with the remote server.")
    aws: PostRemoteServersBodyAws | None = Field(default=None, description="AWS S3 connection settings (access key, secret key)")
    azure_blob_storage: PostRemoteServersBodyAzureBlobStorage | None = Field(default=None, description="Azure Blob Storage connection settings")
    azure_files_storage: PostRemoteServersBodyAzureFilesStorage | None = Field(default=None, description="Azure File Storage connection settings")
    backblaze_b2: PostRemoteServersBodyBackblazeB2 | None = Field(default=None, description="Backblaze B2 connection settings")
    filebase: PostRemoteServersBodyFilebase | None = Field(default=None, description="Filebase connection settings")
    google_cloud_storage: PostRemoteServersBodyGoogleCloudStorage | None = Field(default=None, description="Google Cloud Storage connection settings")
    rackspace: PostRemoteServersBodyRackspace | None = Field(default=None, description="Rackspace Cloud Files connection settings")
    s3_compatible: PostRemoteServersBodyS3Compatible | None = Field(default=None, description="S3-compatible storage connection settings")
    wasabi: PostRemoteServersBodyWasabi | None = Field(default=None, description="Wasabi storage connection settings")
    hostname: str | None = Field(default=None, description="Hostname or IP address")
    port: int | None = Field(default=None, description="Port for remote server.  Not needed for S3.", json_schema_extra={'format': 'int32'})
class PostRemoteServersRequest(StrictModel):
    """Create a remote server configuration for cloud storage or file transfer integration. Supports multiple storage backends including AWS S3, Azure, Google Cloud Storage, and various other cloud providers."""
    body: PostRemoteServersRequestBody | None = None

# Operation: get_remote_server
class GetRemoteServersIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the remote server to retrieve.", json_schema_extra={'format': 'int32'})
class GetRemoteServersIdRequest(StrictModel):
    """Retrieve details for a specific remote server by its ID. Returns the configuration and status information for the requested remote server."""
    path: GetRemoteServersIdRequestPath

# Operation: update_remote_server
class PatchRemoteServersIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the remote server to update.", json_schema_extra={'format': 'int32'})
class PatchRemoteServersIdRequestBody(StrictModel):
    enable_dedicated_ips: bool | None = Field(default=None, description="Restrict remote server connections to dedicated IP addresses only.")
    files_agent_permission_set: Literal["read_write", "read_only", "write_only"] | None = Field(default=None, description="Permission level for the files agent to access local files.")
    files_agent_root: str | None = Field(default=None, description="Local root directory path for the files agent.")
    hostname: str | None = Field(default=None, description="Hostname or IP address of the remote server.")
    max_connections: int | None = Field(default=None, description="Maximum number of parallel connections to the remote server. Ignored for S3 connections which parallelize automatically.", json_schema_extra={'format': 'int32'})
    name: str | None = Field(default=None, description="Internal name for the remote server for reference and identification.")
    one_drive_account_type: Literal["personal", "business_other"] | None = Field(default=None, description="OneDrive account type: personal for individual accounts or business_other for organizational accounts.")
    pin_to_site_region: bool | None = Field(default=None, description="Force all communications with this remote server through the primary region of the site. Can be overridden by site-wide settings.")
    port: int | None = Field(default=None, description="Port number for the remote server connection. Not required for S3 or cloud storage providers.", json_schema_extra={'format': 'int32'})
    private_key: str | None = Field(default=None, description="Private key for SSH or certificate-based authentication.")
    private_key_passphrase: str | None = Field(default=None, description="Passphrase to decrypt the private key if it is encrypted.")
    s3_bucket: str | None = Field(default=None, description="S3 bucket name for file storage.")
    s3_region: str | None = Field(default=None, description="AWS region code for S3 bucket location.")
    server_certificate: Literal["require_match", "allow_any"] | None = Field(default=None, description="SSL certificate validation mode: require_match to validate against server certificate, or allow_any to accept any certificate.")
    server_host_key: str | None = Field(default=None, description="SSH host key in OpenSSH format (as would appear in ~/.ssh/known_hosts). If provided, the server host key must match exactly.")
    server_type: Literal["ftp", "sftp", "s3", "google_cloud_storage", "webdav", "wasabi", "backblaze_b2", "one_drive", "rackspace", "box", "dropbox", "google_drive", "azure", "sharepoint", "s3_compatible", "azure_files", "files_agent", "filebase"] | None = Field(default=None, description="Type of remote server connection.")
    ssl: Literal["if_available", "require", "require_implicit", "never"] | None = Field(default=None, description="SSL/TLS requirement for the connection: if_available to use when supported, require to mandate SSL, require_implicit for implicit SSL, or never to disable.")
    ssl_certificate: str | None = Field(default=None, description="SSL client certificate for mutual TLS authentication.")
    aws: PatchRemoteServersIdBodyAws | None = Field(default=None, description="AWS S3 connection settings (access key, secret key)")
    azure_blob_storage: PatchRemoteServersIdBodyAzureBlobStorage | None = Field(default=None, description="Azure Blob Storage connection settings")
    azure_files_storage: PatchRemoteServersIdBodyAzureFilesStorage | None = Field(default=None, description="Azure File Storage connection settings")
    backblaze_b2: PatchRemoteServersIdBodyBackblazeB2 | None = Field(default=None, description="Backblaze B2 connection settings")
    filebase: PatchRemoteServersIdBodyFilebase | None = Field(default=None, description="Filebase connection settings")
    google_cloud_storage: PatchRemoteServersIdBodyGoogleCloudStorage | None = Field(default=None, description="Google Cloud Storage connection settings")
    rackspace: PatchRemoteServersIdBodyRackspace | None = Field(default=None, description="Rackspace Cloud Files connection settings")
    s3_compatible: PatchRemoteServersIdBodyS3Compatible | None = Field(default=None, description="S3-compatible storage connection settings")
    wasabi: PatchRemoteServersIdBodyWasabi | None = Field(default=None, description="Wasabi storage connection settings")
class PatchRemoteServersIdRequest(StrictModel):
    """Update configuration for a remote server connection. Modify authentication credentials, connection settings, storage bucket details, and security parameters for cloud storage providers (S3, Azure, Google Cloud, etc.) or traditional servers (FTP, SFTP, WebDAV)."""
    path: PatchRemoteServersIdRequestPath
    body: PatchRemoteServersIdRequestBody | None = None

# Operation: delete_remote_server
class DeleteRemoteServersIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the remote server to delete.", json_schema_extra={'format': 'int32'})
class DeleteRemoteServersIdRequest(StrictModel):
    """Permanently delete a remote server by its ID. This action cannot be undone."""
    path: DeleteRemoteServersIdRequestPath

# Operation: download_remote_server_configuration
class GetRemoteServersIdConfigurationFileRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Remote Server for which to download the configuration file.", json_schema_extra={'format': 'int32'})
class GetRemoteServersIdConfigurationFileRequest(StrictModel):
    """Download the configuration file for a Remote Server. This file is required for integrating certain Remote Server types, such as the Files.com Agent."""
    path: GetRemoteServersIdConfigurationFileRequestPath

# Operation: update_remote_server_configuration
class PostRemoteServersIdConfigurationFileRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the remote server to update.", json_schema_extra={'format': 'int32'})
class PostRemoteServersIdConfigurationFileRequestBody(StrictModel):
    config_version: str | None = Field(default=None, description="The version identifier of the agent configuration being submitted.")
    hostname: str | None = Field(default=None, description="The hostname or IP address of the remote server.")
    permission_set: str | None = Field(default=None, description="The permission level for the agent, controlling access scope.")
    port: int | None = Field(default=None, description="The network port on which the agent listens for incoming connections.", json_schema_extra={'format': 'int32'})
    private_key: str | None = Field(default=None, description="The private key used for secure authentication and encryption.")
    public_key: str | None = Field(default=None, description="The public key corresponding to the private key for secure communication.")
    root: str | None = Field(default=None, description="The local filesystem root path where the agent operates and stores files.")
    server_host_key: str | None = Field(default=None, description="The server's host key used for SSH-based authentication and verification.")
    status: str | None = Field(default=None, description="The current operational state of the agent, either running or shutdown.")
    subdomain: str | None = Field(default=None, description="The subdomain identifier for the remote server configuration.")
class PostRemoteServersIdConfigurationFileRequest(StrictModel):
    """Submit local configuration changes, commit them, and retrieve the updated configuration file for a remote server. This operation is used by Remote Server integrations such as the Files.com Agent to synchronize agent configuration state."""
    path: PostRemoteServersIdConfigurationFileRequestPath
    body: PostRemoteServersIdConfigurationFileRequestBody | None = None

# Operation: list_requests
class GetRequestsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Only the `destination` field is supported for sorting.")
    mine: bool | None = Field(default=None, description="Filter to show only requests belonging to the current user. Defaults to true for non-admin users.")
class GetRequestsRequest(StrictModel):
    """Retrieve a paginated list of requests with optional filtering and sorting. By default, shows only the current user's requests unless the user is a site admin."""
    query: GetRequestsRequestQuery | None = None

# Operation: request_file
class PostRequestsRequestBody(StrictModel):
    destination: str = Field(default=..., description="The destination filename (without file extension) being requested.")
    path: str = Field(default=..., description="The folder path where the requested file is located.")
    user_ids: str | None = Field(default=None, description="List of user IDs to request the file from. Provide as comma-separated values when sent as a string.")
class PostRequestsRequest(StrictModel):
    """Request a file from specified users by destination filename and folder path. Optionally target specific users; if no users are specified, the request is sent broadly."""
    body: PostRequestsRequestBody

# Operation: list_requests_folder
class GetRequestsFoldersPathRequestPath(StrictModel):
    path: str = Field(default=..., description="The folder path to filter requests. Use `/` to represent the root directory. Required parameter.")
class GetRequestsFoldersPathRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Maximum allowed is 10,000, though 1,000 or less is recommended for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Valid field is `destination`.")
    mine: bool | None = Field(default=None, description="Filter to show only requests created by the current user. Defaults to true for non-admin users.")
class GetRequestsFoldersPathRequest(StrictModel):
    """Retrieve a list of requests, optionally filtered by folder path and user ownership. Results can be paginated and sorted by destination."""
    path: GetRequestsFoldersPathRequestPath
    query: GetRequestsFoldersPathRequestQuery | None = None

# Operation: delete_request
class DeleteRequestsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the request to delete.", json_schema_extra={'format': 'int32'})
class DeleteRequestsIdRequest(StrictModel):
    """Delete a specific request by its ID. This operation permanently removes the request from the system."""
    path: DeleteRequestsIdRequestPath

# Operation: list_sftp_host_keys
class GetSftpHostKeysRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.", json_schema_extra={'format': 'int32'})
class GetSftpHostKeysRequest(StrictModel):
    """Retrieve a paginated list of SFTP host keys. Use pagination to manage large result sets efficiently."""
    query: GetSftpHostKeysRequestQuery | None = None

# Operation: create_sftp_host_key
class PostSftpHostKeysRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A user-friendly name to identify this SFTP host key for reference and management purposes.")
    private_key: str | None = Field(default=None, description="The private key data in PEM format used for SFTP host authentication. This should be the complete private key content.")
class PostSftpHostKeysRequest(StrictModel):
    """Create a new SFTP host key for secure file transfer authentication. The host key consists of a friendly name and the associated private key data."""
    body: PostSftpHostKeysRequestBody | None = None

# Operation: get_sftp_host_key
class GetSftpHostKeysIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SFTP host key to retrieve.", json_schema_extra={'format': 'int32'})
class GetSftpHostKeysIdRequest(StrictModel):
    """Retrieve details for a specific SFTP host key by its ID. Use this to view the configuration and properties of an existing host key."""
    path: GetSftpHostKeysIdRequestPath

# Operation: update_sftp_host_key
class PatchSftpHostKeysIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SFTP host key to update.", json_schema_extra={'format': 'int32'})
class PatchSftpHostKeysIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A user-friendly name to identify this SFTP host key.")
    private_key: str | None = Field(default=None, description="The private key data in PEM format or other standard key format.")
class PatchSftpHostKeysIdRequest(StrictModel):
    """Update an SFTP host key's friendly name and/or private key data. Specify the host key ID and provide the fields you want to modify."""
    path: PatchSftpHostKeysIdRequestPath
    body: PatchSftpHostKeysIdRequestBody | None = None

# Operation: delete_sftp_host_key
class DeleteSftpHostKeysIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SFTP host key to delete.", json_schema_extra={'format': 'int32'})
class DeleteSftpHostKeysIdRequest(StrictModel):
    """Delete an SFTP host key by its ID. This operation permanently removes the specified host key from the system."""
    path: DeleteSftpHostKeysIdRequestPath

# Operation: list_api_keys_site
class GetSiteApiKeysRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Supports sorting by expiration date.")
class GetSiteApiKeysRequest(StrictModel):
    """Retrieve a paginated list of API keys for your site. Optionally sort and filter results to manage your API credentials."""
    query: GetSiteApiKeysRequestQuery | None = None

# Operation: create_api_key_site
class PostSiteApiKeysRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A user-supplied description to help identify the purpose or context of this API key.")
    expires_at: str | None = Field(default=None, description="The date and time when this API key will automatically expire and become invalid. Specified in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    name: str | None = Field(default=None, description="An internal name for this API key to help you identify and manage it.")
    permission_set: Literal["none", "full", "desktop_app", "sync_app", "office_integration", "mobile_app"] | None = Field(default=None, description="The permission level for this API key, controlling which operations it can perform. Desktop app keys are limited to file and share link operations, while full keys have unrestricted access.")
class PostSiteApiKeysRequest(StrictModel):
    """Create a new API key for authenticating requests to the Files.com. Configure the key's name, expiration date, description, and permission level to control its access scope."""
    body: PostSiteApiKeysRequestBody | None = None

# Operation: list_dns_records_site
class GetSiteDnsRecordsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of DNS records to return per page. Recommended to use 1,000 or less for optimal performance, though up to 10,000 records can be retrieved in a single request.", json_schema_extra={'format': 'int32'})
class GetSiteDnsRecordsRequest(StrictModel):
    """Retrieve the DNS records configured for a site. Results can be paginated to manage large record sets."""
    query: GetSiteDnsRecordsRequestQuery | None = None

# Operation: list_site_ip_addresses
class GetSiteIpAddressesRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.", json_schema_extra={'format': 'int32'})
class GetSiteIpAddressesRequest(StrictModel):
    """Retrieve a paginated list of IP addresses associated with the current site. Use the per_page parameter to control result set size."""
    query: GetSiteIpAddressesRequestQuery | None = None

# Operation: get_sso_strategy
class GetSsoStrategiesIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SSO strategy to retrieve.", json_schema_extra={'format': 'int32'})
class GetSsoStrategiesIdRequest(StrictModel):
    """Retrieve a specific SSO (Single Sign-On) strategy by its ID. Use this to view the configuration and details of an existing SSO strategy."""
    path: GetSsoStrategiesIdRequestPath

# Operation: sync_sso_strategy
class PostSsoStrategiesIdSyncRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SSO strategy to synchronize.", json_schema_extra={'format': 'int32'})
class PostSsoStrategiesIdSyncRequest(StrictModel):
    """Synchronize provisioning data between the local system and the remote SSO server for the specified strategy. This operation ensures user and group data are up-to-date across both systems."""
    path: PostSsoStrategiesIdSyncRequestPath

# Operation: update_style
class PatchStylesPathRequestPath(StrictModel):
    path: str = Field(default=..., description="The path identifier for the style to update.")
class PatchStylesPathRequestBody(StrictModel):
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="Binary file containing the logo or branding assets for custom styling.", json_schema_extra={'format': 'binary'})
class PatchStylesPathRequest(StrictModel):
    """Update a style configuration by uploading a new branding file. Specify the style path and provide the binary file for custom branding."""
    path: PatchStylesPathRequestPath
    body: PatchStylesPathRequestBody

# Operation: delete_style
class DeleteStylesPathRequestPath(StrictModel):
    path: str = Field(default=..., description="The path identifier of the style to delete. This uniquely identifies which style resource to remove.")
class DeleteStylesPathRequest(StrictModel):
    """Delete a style by its path. This operation permanently removes the style from the system."""
    path: DeleteStylesPathRequestPath

# Operation: list_usage_snapshots_daily
class GetUsageDailySnapshotsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000 records per page.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Supported fields are `date` and `usage_snapshot_id`. Specify as an object with field name as key and sort direction as value.")
class GetUsageDailySnapshotsRequest(StrictModel):
    """Retrieve a paginated list of daily usage snapshots. Results can be sorted by date or snapshot ID to track usage patterns over time."""
    query: GetUsageDailySnapshotsRequestQuery | None = None

# Operation: list_usage_snapshots
class GetUsageSnapshotsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
class GetUsageSnapshotsRequest(StrictModel):
    """Retrieve a paginated list of usage snapshots. Use the per_page parameter to control the number of records returned per page."""
    query: GetUsageSnapshotsRequestQuery | None = None

# Operation: update_user
class PatchUserRequestBody(StrictModel):
    allowed_ips: str | None = Field(default=None, description="Comma-separated or newline-delimited list of IP addresses permitted to access this user account. Leave empty to allow all IPs.")
    announcements_read: bool | None = Field(default=None, description="Mark whether the user has acknowledged all announcements displayed in the UI.")
    authenticate_until: str | None = Field(default=None, description="Scheduled date and time when this user account will be automatically deactivated.", json_schema_extra={'format': 'date-time'})
    authentication_method: Literal["password", "unused_former_ldap", "sso", "none", "email_signup", "password_with_imported_hash"] | None = Field(default=None, description="Authentication method used for this user account.")
    billing_permission: bool | None = Field(default=None, description="Grant this user permission to manage account settings, process payments, and view invoices.")
    bypass_inactive_disable: bool | None = Field(default=None, description="Prevent this user from being automatically disabled due to inactivity, overriding site-wide settings.")
    bypass_site_allowed_ips: bool | None = Field(default=None, description="Allow this user to bypass site-wide IP address restrictions and blacklists.")
    company: str | None = Field(default=None, description="User's organization or company name.")
    dav_permission: bool | None = Field(default=None, description="Enable or disable WebDAV protocol access for this user.")
    disabled: bool | None = Field(default=None, description="Disable or enable the user account. Disabled users cannot log in and do not consume billing seats. Users may be automatically disabled after prolonged inactivity based on site configuration.")
    email: str | None = Field(default=None, description="User's email address.")
    ftp_permission: bool | None = Field(default=None, description="Enable or disable FTP and FTPS protocol access for this user.")
    grant_permission: str | None = Field(default=None, description="Permission level to grant on the user's root folder. Options include full access, read-only, write, list directory contents, or history access.")
    header_text: str | None = Field(default=None, description="Custom message text displayed to this user in the UI header.")
    language: str | None = Field(default=None, description="User's preferred language for the UI.")
    name: str | None = Field(default=None, description="User's full name.")
    notes: str | None = Field(default=None, description="Internal notes or comments about this user for administrative reference.")
    notification_daily_send_time: int | None = Field(default=None, description="Hour of the day (0-23) when daily notifications should be sent to this user.", json_schema_extra={'format': 'int32'})
    office_integration_enabled: bool | None = Field(default=None, description="Enable integration with Microsoft Office for the web applications.")
    password_validity_days: int | None = Field(default=None, description="Number of days a user can use the same password before being required to change it.", json_schema_extra={'format': 'int32'})
    receive_admin_alerts: bool | None = Field(default=None, description="Enable or disable receipt of administrative alerts such as certificate expiration warnings and account overages.")
    require_2fa: Literal["use_system_setting", "always_require", "never_require"] | None = Field(default=None, description="Two-factor authentication requirement setting for this user.")
    require_password_change: bool | None = Field(default=None, description="Require this user to change their password on the next login.")
    restapi_permission: bool | None = Field(default=None, description="Enable or disable REST API access for this user.")
    self_managed: bool | None = Field(default=None, description="Indicate whether this user manages their own credentials or is a shared/bot account with managed credentials.")
    sftp_permission: bool | None = Field(default=None, description="Enable or disable SFTP protocol access for this user.")
    site_admin: bool | None = Field(default=None, description="Grant or revoke site administrator privileges for this user.")
    skip_welcome_screen: bool | None = Field(default=None, description="Skip the welcome screen when this user first logs into the UI.")
    ssl_required: Literal["use_system_setting", "always_require", "never_require"] | None = Field(default=None, description="SSL/TLS encryption requirement setting for this user's connections.")
    sso_strategy_id: int | None = Field(default=None, description="SSO (Single Sign On) strategy ID associated with this user for federated authentication.", json_schema_extra={'format': 'int32'})
    subscribe_to_newsletter: bool | None = Field(default=None, description="Subscribe or unsubscribe this user from the newsletter.")
    time_zone: str | None = Field(default=None, description="User's time zone for scheduling and time-based operations.")
    user_root: str | None = Field(default=None, description="Root folder path for FTP access and optionally SFTP if configured site-wide. Not used for API, desktop, or web interface access.")
class PatchUserRequest(StrictModel):
    """Update user account settings, permissions, and authentication configuration. Allows modification of user profile, access controls, security settings, and notification preferences."""
    body: PatchUserRequestBody | None = None

# Operation: list_api_keys_current_user
class GetUserApiKeysRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of API keys to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Supports sorting by expiration date (e.g., sort_by[expires_at]=desc).")
class GetUserApiKeysRequest(StrictModel):
    """Retrieve a paginated list of API keys for the authenticated user. Supports sorting by expiration date and customizable page size."""
    query: GetUserApiKeysRequestQuery | None = None

# Operation: create_api_key_user
class PostUserApiKeysRequestBody(StrictModel):
    description: str | None = Field(default=None, description="Optional user-supplied description to help identify the purpose or context of this API key.")
    expires_at: str | None = Field(default=None, description="Optional expiration date and time for this API key in ISO 8601 format. After this date, the key will no longer be valid for authentication.", json_schema_extra={'format': 'date-time'})
    name: str | None = Field(default=None, description="Optional internal name for this API key to help you identify and manage it.")
    permission_set: Literal["none", "full", "desktop_app", "sync_app", "office_integration", "mobile_app"] | None = Field(default=None, description="Permission level for this API key. Controls which operations and resources the key can access. Desktop app keys are limited to file and share link operations, while full keys have unrestricted access.")
class PostUserApiKeysRequest(StrictModel):
    """Create a new API key for programmatic access to your account. Configure the key's name, permissions, expiration date, and optional description."""
    body: PostUserApiKeysRequestBody | None = None

# Operation: list_user_groups
class GetUserGroupsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, though the API supports up to 10,000 records per page.", json_schema_extra={'format': 'int32'})
class GetUserGroupsRequest(StrictModel):
    """Retrieve a paginated list of users belonging to groups. Use the per_page parameter to control result set size for optimal performance."""
    query: GetUserGroupsRequestQuery | None = None

# Operation: list_public_keys_current_user
class GetUserPublicKeysRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, though the API supports up to 10,000 records per page.", json_schema_extra={'format': 'int32'})
class GetUserPublicKeysRequest(StrictModel):
    """Retrieve a paginated list of public keys associated with the user account. Use the per_page parameter to control pagination size."""
    query: GetUserPublicKeysRequestQuery | None = None

# Operation: add_public_key
class PostUserPublicKeysRequestBody(StrictModel):
    public_key: str = Field(default=..., description="The complete SSH public key content (typically starts with 'ssh-rsa', 'ssh-ed25519', or similar algorithm identifier).")
    title: str = Field(default=..., description="A descriptive label to identify this key within your account.")
class PostUserPublicKeysRequest(StrictModel):
    """Add a new SSH public key to your account for authentication purposes. Each key requires a descriptive title for easy identification."""
    body: PostUserPublicKeysRequestBody

# Operation: list_cipher_uses
class GetUserCipherUsesRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, though up to 10,000 is supported.", json_schema_extra={'format': 'int32'})
class GetUserCipherUsesRequest(StrictModel):
    """Retrieve a paginated list of cipher uses associated with the authenticated user. Use the per_page parameter to control result set size."""
    query: GetUserCipherUsesRequestQuery | None = None

# Operation: list_requests_user
class GetUserRequestsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance, with a maximum of 10,000.", json_schema_extra={'format': 'int32'})
class GetUserRequestsRequest(StrictModel):
    """Retrieve a paginated list of user requests. Use the per_page parameter to control result set size for optimal performance."""
    query: GetUserRequestsRequestQuery | None = None

# Operation: create_user_request
class PostUserRequestsRequestBody(StrictModel):
    details: str = Field(default=..., description="Detailed description or content of the user request, providing context about what is being requested.")
    email: str = Field(default=..., description="Email address of the user associated with this request. Used for identification and communication purposes.")
    name: str = Field(default=..., description="Full name of the user associated with this request.")
class PostUserRequestsRequest(StrictModel):
    """Create a new user request with details about a specific user. This operation registers a request associated with the provided user's email and name."""
    body: PostUserRequestsRequestBody

# Operation: get_user_request
class GetUserRequestsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user request to retrieve.", json_schema_extra={'format': 'int32'})
class GetUserRequestsIdRequest(StrictModel):
    """Retrieve details for a specific user request by its ID. Returns the complete request information including status, content, and metadata."""
    path: GetUserRequestsIdRequestPath

# Operation: delete_user_request
class DeleteUserRequestsIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user request to delete.", json_schema_extra={'format': 'int32'})
class DeleteUserRequestsIdRequest(StrictModel):
    """Delete a specific user request by its ID. This operation permanently removes the user request from the system."""
    path: DeleteUserRequestsIdRequestPath

# Operation: list_users
class GetUsersRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    ids: str | None = Field(default=None, description="Filter results by one or more user IDs using comma-separated values.")
    q_username: str | None = Field(default=None, validation_alias="q[username]", serialization_alias="q[username]", description="Filter results to users whose username matches the provided value.")
    q_email: str | None = Field(default=None, validation_alias="q[email]", serialization_alias="q[email]", description="Filter results to users whose email address matches the provided value.")
    q_notes: str | None = Field(default=None, validation_alias="q[notes]", serialization_alias="q[notes]", description="Filter results to users whose notes field matches the provided value.")
    q_admin: str | None = Field(default=None, validation_alias="q[admin]", serialization_alias="q[admin]", description="Filter results to include only administrative users when set to true.")
    q_allowed_ips: str | None = Field(default=None, validation_alias="q[allowed_ips]", serialization_alias="q[allowed_ips]", description="Filter results to include only users with custom allowed IP address restrictions configured.")
    q_password_validity_days: str | None = Field(default=None, validation_alias="q[password_validity_days]", serialization_alias="q[password_validity_days]", description="Filter results to include only users with custom password validity days settings configured.")
    q_ssl_required: str | None = Field(default=None, validation_alias="q[ssl_required]", serialization_alias="q[ssl_required]", description="Filter results to include only users with custom SSL requirement settings configured.")
    sort_by: dict | None = Field(default=None, description="If set, sort records by the specified field in either `asc` or `desc` direction (e.g. `sort_by[authenticate_until]=desc`). Valid fields are `authenticate_until`, `active`, `email`, `last_desktop_login_at`, `last_login_at`, `username`, `company`, `name`, `site_admin`, `receive_admin_alerts`, `password_validity_days`, `ssl_required` or `not_site_admin`.")
class GetUsersRequest(StrictModel):
    """Retrieve a paginated list of users with optional filtering by ID, username, email, notes, or administrative and security settings."""
    query: GetUsersRequestQuery | None = None

# Operation: create_user
class PostUsersRequestBody(StrictModel):
    allowed_ips: str | None = Field(default=None, description="Comma-separated or newline-delimited list of IP addresses permitted to access this user account. Leave empty to allow all IPs.")
    announcements_read: bool | None = Field(default=None, description="Indicates whether the user has acknowledged all announcements displayed in the UI.")
    authenticate_until: str | None = Field(default=None, description="Date and time after which the user account will be automatically deactivated. Useful for temporary or contract-based access.", json_schema_extra={'format': 'date-time'})
    authentication_method: Literal["password", "unused_former_ldap", "sso", "none", "email_signup", "password_with_imported_hash"] | None = Field(default=None, description="Authentication mechanism used for this user. Determines how credentials are validated and managed.")
    billing_permission: bool | None = Field(default=None, description="Grant permission to manage account operations, payments, and invoices. Restricted to trusted users only.")
    bypass_inactive_disable: bool | None = Field(default=None, description="Prevent this user from being automatically disabled due to inactivity, overriding site-wide inactivity policies.")
    bypass_site_allowed_ips: bool | None = Field(default=None, description="Allow this user to bypass site-wide IP address blacklists and restrictions.")
    company: str | None = Field(default=None, description="User's organization or company name for identification and organizational purposes.")
    dav_permission: bool | None = Field(default=None, description="Enable WebDAV protocol access for this user.")
    disabled: bool | None = Field(default=None, description="Disable user account. Disabled users cannot log in and do not consume billing seats. Can be automatically applied after inactivity.")
    email: str | None = Field(default=None, description="User's email address used for login, notifications, and account recovery.")
    ftp_permission: bool | None = Field(default=None, description="Enable FTP/FTPS protocol access for this user.")
    grant_permission: str | None = Field(default=None, description="Default permission level for the user's root folder. Options include full access, read-only, write, list, or history viewing.")
    header_text: str | None = Field(default=None, description="Custom message displayed in the UI header for this user. Useful for notifications or instructions.")
    language: str | None = Field(default=None, description="User's preferred language for the UI interface.")
    name: str | None = Field(default=None, description="User's full name for display and identification purposes.")
    notes: str | None = Field(default=None, description="Internal notes or comments about the user for administrative reference. Not visible to the user.")
    notification_daily_send_time: int | None = Field(default=None, description="Hour of day (0-23) when daily notification digests should be sent to this user.", json_schema_extra={'format': 'int32'})
    office_integration_enabled: bool | None = Field(default=None, description="Enable integration with Microsoft Office for the web applications.")
    password_validity_days: int | None = Field(default=None, description="Number of days before the user must change their password. Enforces periodic password rotation.", json_schema_extra={'format': 'int32'})
    receive_admin_alerts: bool | None = Field(default=None, description="Send administrative alerts to this user, including certificate expiration warnings and account overages.")
    require_2fa: Literal["use_system_setting", "always_require", "never_require"] | None = Field(default=None, description="Two-factor authentication requirement for this user. Can override system-wide settings.")
    require_password_change: bool | None = Field(default=None, description="Require the user to change their password on the next login attempt.")
    restapi_permission: bool | None = Field(default=None, description="Enable REST API access for this user.")
    self_managed: bool | None = Field(default=None, description="Indicate whether the user manages their own credentials or is a shared/bot account with managed credentials.")
    sftp_permission: bool | None = Field(default=None, description="Enable SFTP protocol access for this user.")
    site_admin: bool | None = Field(default=None, description="Grant site administrator privileges to this user, allowing management of other users and system settings.")
    skip_welcome_screen: bool | None = Field(default=None, description="Skip the welcome/onboarding screen on first login to the UI.")
    ssl_required: Literal["use_system_setting", "always_require", "never_require"] | None = Field(default=None, description="SSL/TLS encryption requirement for this user's connections. Can override system-wide settings.")
    sso_strategy_id: int | None = Field(default=None, description="ID of the SSO (Single Sign On) strategy to use for this user's authentication.", json_schema_extra={'format': 'int32'})
    subscribe_to_newsletter: bool | None = Field(default=None, description="Subscribe this user to the system newsletter for updates and announcements.")
    time_zone: str | None = Field(default=None, description="User's time zone for scheduling notifications and displaying timestamps in the UI.")
    user_root: str | None = Field(default=None, description="Root folder path for FTP access and optionally SFTP (if configured site-wide). Does not apply to API, desktop, or web interface access.")
    username: str | None = Field(default=None, description="User's username")
class PostUsersRequest(StrictModel):
    """Create a new user account with configurable authentication, permissions, and security settings. Supports multiple authentication methods and granular access control across protocols (FTP, SFTP, WebDAV, REST API)."""
    body: PostUsersRequestBody | None = None

# Operation: get_user
class GetUsersIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user to retrieve.", json_schema_extra={'format': 'int32'})
class GetUsersIdRequest(StrictModel):
    """Retrieve detailed information for a specific user by their ID."""
    path: GetUsersIdRequestPath

# Operation: update_user_account
class PatchUsersIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user to update.", json_schema_extra={'format': 'int32'})
class PatchUsersIdRequestBody(StrictModel):
    allowed_ips: str | None = Field(default=None, description="Comma-separated or newline-delimited list of IP addresses permitted to access this user account.")
    announcements_read: bool | None = Field(default=None, description="Whether the user has read all announcements displayed in the UI.")
    authenticate_until: str | None = Field(default=None, description="Date and time when the user account will be automatically deactivated.", json_schema_extra={'format': 'date-time'})
    authentication_method: Literal["password", "unused_former_ldap", "sso", "none", "email_signup", "password_with_imported_hash"] | None = Field(default=None, description="The authentication method used for this user account.")
    billing_permission: bool | None = Field(default=None, description="Whether the user can perform operations on account settings, payments, and invoices.")
    bypass_inactive_disable: bool | None = Field(default=None, description="Whether the user is exempt from automatic deactivation due to inactivity.")
    bypass_site_allowed_ips: bool | None = Field(default=None, description="Whether the user can bypass site-wide IP blacklist restrictions.")
    company: str | None = Field(default=None, description="The user's company or organization name.")
    dav_permission: bool | None = Field(default=None, description="Whether the user can connect and access files via WebDAV protocol.")
    disabled: bool | None = Field(default=None, description="Whether the user account is disabled. Disabled users cannot log in and do not count toward billing. Users may be automatically disabled after an inactivity period based on site settings.")
    email: str | None = Field(default=None, description="The user's email address.")
    ftp_permission: bool | None = Field(default=None, description="Whether the user can access files and accounts via FTP or FTPS protocols.")
    grant_permission: str | None = Field(default=None, description="Permission level to grant on the user's root folder. Options include full access, read-only, write, list, or history access.")
    header_text: str | None = Field(default=None, description="Custom text message displayed to the user in the UI header for notifications or announcements.")
    language: str | None = Field(default=None, description="The user's preferred language for the UI.")
    name: str | None = Field(default=None, description="The user's full name.")
    notes: str | None = Field(default=None, description="Internal notes or comments about the user for administrative reference.")
    notification_daily_send_time: int | None = Field(default=None, description="The hour of the day (0-23) when daily notifications should be sent to the user.", json_schema_extra={'format': 'int32'})
    office_integration_enabled: bool | None = Field(default=None, description="Whether to enable integration with Microsoft Office for the web applications.")
    password_validity_days: int | None = Field(default=None, description="Number of days a user can use the same password before being required to change it.", json_schema_extra={'format': 'int32'})
    receive_admin_alerts: bool | None = Field(default=None, description="Whether the user receives administrative alerts such as certificate expiration warnings and account overages.")
    require_2fa: Literal["use_system_setting", "always_require", "never_require"] | None = Field(default=None, description="Two-factor authentication requirement setting for this user.")
    require_password_change: bool | None = Field(default=None, description="Whether the user must change their password on the next login.")
    restapi_permission: bool | None = Field(default=None, description="Whether the user can access and use the REST API.")
    self_managed: bool | None = Field(default=None, description="Whether the user manages their own credentials or is a shared/bot account with managed credentials.")
    sftp_permission: bool | None = Field(default=None, description="Whether the user can access files and accounts via SFTP protocol.")
    site_admin: bool | None = Field(default=None, description="Whether the user has administrator privileges for this site.")
    skip_welcome_screen: bool | None = Field(default=None, description="Whether to skip the welcome screen when the user first logs into the UI.")
    ssl_required: Literal["use_system_setting", "always_require", "never_require"] | None = Field(default=None, description="SSL/TLS encryption requirement setting for this user's connections.")
    sso_strategy_id: int | None = Field(default=None, description="The ID of the SSO (Single Sign On) strategy assigned to this user, if applicable.", json_schema_extra={'format': 'int32'})
    subscribe_to_newsletter: bool | None = Field(default=None, description="Whether the user is subscribed to receive newsletter communications.")
    time_zone: str | None = Field(default=None, description="The user's time zone for scheduling and time-based operations.")
    user_root: str | None = Field(default=None, description="Root folder path for FTP access and optionally SFTP if configured at the site level. Not used for API, desktop, or web interface access.")
class PatchUsersIdRequest(StrictModel):
    """Update user account settings, permissions, and authentication configuration. Allows modification of user profile, access controls, security settings, and notification preferences."""
    path: PatchUsersIdRequestPath
    body: PatchUsersIdRequestBody | None = None

# Operation: delete_user
class DeleteUsersIdRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user to delete.", json_schema_extra={'format': 'int32'})
class DeleteUsersIdRequest(StrictModel):
    """Permanently delete a user account by ID. This action cannot be undone."""
    path: DeleteUsersIdRequestPath

# Operation: reset_user_2fa
class PostUsersId2faResetRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose 2FA needs to be reset.", json_schema_extra={'format': 'int32'})
class PostUsersId2faResetRequest(StrictModel):
    """Initiate a two-factor authentication reset for a user who has lost access to their existing 2FA methods. This process allows the user to regain account access and reconfigure their authentication."""
    path: PostUsersId2faResetRequestPath

# Operation: resend_welcome_email
class PostUsersIdResendWelcomeEmailRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user who should receive the welcome email.", json_schema_extra={'format': 'int32'})
class PostUsersIdResendWelcomeEmailRequest(StrictModel):
    """Resend the welcome email to a user. This operation is useful when the initial welcome email was not received or needs to be sent again."""
    path: PostUsersIdResendWelcomeEmailRequestPath

# Operation: unlock_user
class PostUsersIdUnlockRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user account to unlock.", json_schema_extra={'format': 'int32'})
class PostUsersIdUnlockRequest(StrictModel):
    """Unlock a user account that has been locked due to failed login attempts. This restores the user's ability to authenticate."""
    path: PostUsersIdUnlockRequestPath

# Operation: list_api_keys_for_user
class GetUsersUserIdApiKeysRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The user ID whose API keys to retrieve. Use `0` to operate on the current session's user.", json_schema_extra={'format': 'int32'})
class GetUsersUserIdApiKeysRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Maximum 10,000; 1,000 or less is recommended.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort results by a specified field in ascending or descending order. Valid field: `expires_at`.")
class GetUsersUserIdApiKeysRequest(StrictModel):
    """Retrieve a paginated list of API keys for a user. Use user_id `0` to list keys for the current session's user."""
    path: GetUsersUserIdApiKeysRequestPath
    query: GetUsersUserIdApiKeysRequestQuery | None = None

# Operation: create_api_key_admin
class PostUsersUserIdApiKeysRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The user ID for which to create the API key. Use `0` to create a key for the current authenticated user.", json_schema_extra={'format': 'int32'})
class PostUsersUserIdApiKeysRequestBody(StrictModel):
    description: str | None = Field(default=None, description="Optional user-supplied description to help identify the purpose or context of this API key.")
    expires_at: str | None = Field(default=None, description="Optional expiration date and time for the API key in ISO 8601 format. After this date, the key will no longer be valid.", json_schema_extra={'format': 'date-time'})
    name: str | None = Field(default=None, description="Optional internal name for the API key for your own reference and organization.")
    permission_set: Literal["none", "full", "desktop_app", "sync_app", "office_integration", "mobile_app"] | None = Field(default=None, description="Permission level for this API key. `full` grants all permissions, `desktop_app` restricts to file and share link operations, and other sets provide specialized access for specific applications.")
class PostUsersUserIdApiKeysRequest(StrictModel):
    """Create a new API key for the specified user with configurable permissions and optional expiration. Use user_id `0` to create a key for the current session's user."""
    path: PostUsersUserIdApiKeysRequestPath
    body: PostUsersUserIdApiKeysRequestBody | None = None

# Operation: list_cipher_uses_by_user
class GetUsersUserIdCipherUsesRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user whose cipher uses should be retrieved. Use 0 to refer to the current session's authenticated user.", json_schema_extra={'format': 'int32'})
class GetUsersUserIdCipherUsesRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of cipher use records to return per page. Maximum allowed is 10,000, though 1,000 or fewer is recommended for optimal performance.", json_schema_extra={'format': 'int32'})
class GetUsersUserIdCipherUsesRequest(StrictModel):
    """Retrieve a paginated list of cipher uses for a specific user. Use user_id value of 0 to retrieve cipher uses for the current authenticated session's user."""
    path: GetUsersUserIdCipherUsesRequestPath
    query: GetUsersUserIdCipherUsesRequestQuery | None = None

# Operation: list_user_groups_2
class GetUsersUserIdGroupsRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user whose group memberships should be retrieved.", json_schema_extra={'format': 'int32'})
class GetUsersUserIdGroupsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of records to return per page. Recommended to use 1,000 or less for optimal performance; maximum allowed is 10,000.", json_schema_extra={'format': 'int32'})
class GetUsersUserIdGroupsRequest(StrictModel):
    """Retrieve all groups that a specific user belongs to. Supports pagination to handle large result sets."""
    path: GetUsersUserIdGroupsRequestPath
    query: GetUsersUserIdGroupsRequestQuery | None = None

# Operation: list_user_permissions
class GetUsersUserIdPermissionsRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The user ID to retrieve permissions for. Note: This parameter is deprecated; use the filter[user_id] query parameter instead for new implementations.")
class GetUsersUserIdPermissionsRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of permission records to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
    sort_by: dict[str, Any] | None = Field(default=None, description="Sort the results by a specified field in ascending or descending order. Valid sortable fields are group_id, path, user_id, or permission.")
    include_groups: bool | None = Field(default=None, description="When enabled, includes permissions inherited from the user's group memberships in addition to directly assigned permissions.")
class GetUsersUserIdPermissionsRequest(StrictModel):
    """Retrieve a list of permissions for a specific user, with optional filtering by group inheritance and sorting capabilities."""
    path: GetUsersUserIdPermissionsRequestPath
    query: GetUsersUserIdPermissionsRequestQuery | None = None

# Operation: list_public_keys_by_user
class GetUsersUserIdPublicKeysRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user whose public keys should be retrieved. Use `0` to refer to the current authenticated user.", json_schema_extra={'format': 'int32'})
class GetUsersUserIdPublicKeysRequestQuery(StrictModel):
    per_page: int | None = Field(default=None, description="Number of public keys to return per page. Recommended to use 1,000 or less for optimal performance.", json_schema_extra={'format': 'int32'})
class GetUsersUserIdPublicKeysRequest(StrictModel):
    """Retrieve a paginated list of public keys for a specified user. Use user ID `0` to retrieve keys for the current authenticated session."""
    path: GetUsersUserIdPublicKeysRequestPath
    query: GetUsersUserIdPublicKeysRequestQuery | None = None

# Operation: create_public_key_for_user
class PostUsersUserIdPublicKeysRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The ID of the user to create the public key for. Use 0 to create a key for the current session's authenticated user.", json_schema_extra={'format': 'int32'})
class PostUsersUserIdPublicKeysRequestBody(StrictModel):
    public_key: str = Field(default=..., description="The complete SSH public key content (typically starting with ssh-rsa, ssh-ed25519, or similar).")
    title: str = Field(default=..., description="A descriptive label for this public key to help identify it among multiple keys.")
class PostUsersUserIdPublicKeysRequest(StrictModel):
    """Create a new SSH public key for a user account. The key can be associated with the current session's user by providing a user_id of 0."""
    path: PostUsersUserIdPublicKeysRequestPath
    body: PostUsersUserIdPublicKeysRequestBody

# Operation: test_webhook
class PostWebhookTestsRequestBody(StrictModel):
    action: str | None = Field(default=None, description="Action identifier to include in the test request body.")
    encoding: str | None = Field(default=None, description="HTTP encoding format for the request body: JSON, XML, or RAW (form data).")
    file_as_body: bool | None = Field(default=None, description="Whether to send file data as the raw request body instead of as a form field.")
    file_form_field: str | None = Field(default=None, description="Form field name to use when sending file data as a named parameter in the POST body.")
    headers: dict[str, Any] | None = Field(default=None, description="Custom HTTP headers to include in the test request as key-value pairs.")
    method: str | None = Field(default=None, description="HTTP method for the test request: GET or POST.")
    url: str = Field(default=..., description="The webhook URL endpoint to test. Must be a valid HTTP or HTTPS URL.")
class PostWebhookTestsRequest(StrictModel):
    """Execute a test request to a webhook URL to validate connectivity and configuration. Supports custom headers, multiple encoding formats, and optional file payload."""
    body: PostWebhookTestsRequestBody

# ============================================================================
# Component Models
# ============================================================================

class PatchFormFieldSetsIdBodyFormFieldsItem(PermissiveModel):
    default_option: str | None = Field(None, description="Default option to be preselected in the dropdown or radio.")
    field_type: str | None = Field(None, description="Type of field: text, text_area, dropdown, or radio")
    help_text: str | None = Field(None, description="Help text of field")
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="Id of existing Form Field", json_schema_extra={'format': 'int32'})
    label: str | None = Field(None, description="Label of Field")
    options_for_select: str | None = Field(None, description="List of options for dropdown or radio")
    required: bool | None = Field(None, description="Is this a required field? (default true)")

class PatchRemoteServersIdBodyAws(PermissiveModel):
    """AWS S3 connection settings (access key, secret key)"""
    aws_access_key: str | None = Field(None, description="AWS Access Key.")
    aws_secret_key: str | None = Field(None, description="AWS secret key.")

class PatchRemoteServersIdBodyAzureBlobStorage(PermissiveModel):
    """Azure Blob Storage connection settings"""
    azure_blob_storage_access_key: str | None = Field(None, description="Azure Blob Storage secret key.")
    azure_blob_storage_account: str | None = Field(None, description="Azure Blob Storage Account name")
    azure_blob_storage_container: str | None = Field(None, description="Azure Blob Storage Container name")

class PatchRemoteServersIdBodyAzureFilesStorage(PermissiveModel):
    """Azure File Storage connection settings"""
    azure_files_storage_access_key: str | None = Field(None, description="Azure File Storage access key.")
    azure_files_storage_account: str | None = Field(None, description="Azure File Storage Account name")
    azure_files_storage_share_name: str | None = Field(None, description="Azure File Storage Share name")

class PatchRemoteServersIdBodyBackblazeB2(PermissiveModel):
    """Backblaze B2 connection settings"""
    backblaze_b2_application_key: str | None = Field(None, description="Backblaze B2 Cloud Storage applicationKey.")
    backblaze_b2_bucket: str | None = Field(None, description="Backblaze B2 Cloud Storage Bucket name")
    backblaze_b2_key_id: str | None = Field(None, description="Backblaze B2 Cloud Storage keyID.")
    backblaze_b2_s3_endpoint: str | None = Field(None, description="Backblaze B2 Cloud Storage S3 Endpoint")

class PatchRemoteServersIdBodyFilebase(PermissiveModel):
    """Filebase connection settings"""
    filebase_access_key: str | None = Field(None, description="Filebase Access Key.")
    filebase_bucket: str | None = Field(None, description="Filebase Bucket name")
    filebase_secret_key: str | None = Field(None, description="Filebase secret key")

class PatchRemoteServersIdBodyGoogleCloudStorage(PermissiveModel):
    """Google Cloud Storage connection settings"""
    google_cloud_storage_bucket: str | None = Field(None, description="Google Cloud Storage bucket name")
    google_cloud_storage_credentials_json: str | None = Field(None, description="A JSON file that contains the private key. To generate see https://cloud.google.com/storage/docs/json_api/v1/how-tos/authorizing#APIKey")
    google_cloud_storage_project_id: str | None = Field(None, description="Google Cloud Project ID")

class PatchRemoteServersIdBodyRackspace(PermissiveModel):
    """Rackspace Cloud Files connection settings"""
    rackspace_api_key: str | None = Field(None, description="Rackspace API key from the Rackspace Cloud Control Panel.")
    rackspace_container: str | None = Field(None, description="The name of the container (top level directory) where files will sync.")
    rackspace_region: str | None = Field(None, description="Three letter airport code for Rackspace region. See https://support.rackspace.com/how-to/about-regions/")
    rackspace_username: str | None = Field(None, description="Rackspace username used to login to the Rackspace Cloud Control Panel.")

class PatchRemoteServersIdBodyS3Compatible(PermissiveModel):
    """S3-compatible storage connection settings"""
    s3_compatible_access_key: str | None = Field(None, description="S3-compatible Access Key.")
    s3_compatible_bucket: str | None = Field(None, description="S3-compatible Bucket name")
    s3_compatible_endpoint: str | None = Field(None, description="S3-compatible endpoint")
    s3_compatible_secret_key: str | None = Field(None, description="S3-compatible secret key")

class PatchRemoteServersIdBodyWasabi(PermissiveModel):
    """Wasabi storage connection settings"""
    wasabi_access_key: str | None = Field(None, description="Wasabi access key.")
    wasabi_bucket: str | None = Field(None, description="Wasabi Bucket name")
    wasabi_region: str | None = Field(None, description="Wasabi region")
    wasabi_secret_key: str | None = Field(None, description="Wasabi secret key.")

class PostFormFieldSetsBodyFormFieldsItem(PermissiveModel):
    default_option: str | None = Field(None, description="Default option to be preselected in the dropdown or radio.")
    field_type: str | None = Field(None, description="Type of field: text, text_area, dropdown, or radio")
    help_text: str | None = Field(None, description="Help text of field")
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="Id of existing Form Field", json_schema_extra={'format': 'int32'})
    label: str | None = Field(None, description="Label of Field")
    options_for_select: str | None = Field(None, description="List of options for dropdown or radio")
    required: bool | None = Field(None, description="Is this a required field? (default true)")

class PostRemoteServersBodyAws(PermissiveModel):
    """AWS S3 connection settings (access key, secret key)"""
    aws_access_key: str | None = Field(None, description="AWS Access Key.")
    aws_secret_key: str | None = Field(None, description="AWS secret key.")

class PostRemoteServersBodyAzureBlobStorage(PermissiveModel):
    """Azure Blob Storage connection settings"""
    azure_blob_storage_access_key: str | None = Field(None, description="Azure Blob Storage secret key.")
    azure_blob_storage_account: str | None = Field(None, description="Azure Blob Storage Account name")
    azure_blob_storage_container: str | None = Field(None, description="Azure Blob Storage Container name")

class PostRemoteServersBodyAzureFilesStorage(PermissiveModel):
    """Azure File Storage connection settings"""
    azure_files_storage_access_key: str | None = Field(None, description="Azure File Storage access key.")
    azure_files_storage_account: str | None = Field(None, description="Azure File Storage Account name")
    azure_files_storage_share_name: str | None = Field(None, description="Azure File Storage Share name")

class PostRemoteServersBodyBackblazeB2(PermissiveModel):
    """Backblaze B2 connection settings"""
    backblaze_b2_application_key: str | None = Field(None, description="Backblaze B2 Cloud Storage applicationKey.")
    backblaze_b2_bucket: str | None = Field(None, description="Backblaze B2 Cloud Storage Bucket name")
    backblaze_b2_key_id: str | None = Field(None, description="Backblaze B2 Cloud Storage keyID.")
    backblaze_b2_s3_endpoint: str | None = Field(None, description="Backblaze B2 Cloud Storage S3 Endpoint")

class PostRemoteServersBodyFilebase(PermissiveModel):
    """Filebase connection settings"""
    filebase_access_key: str | None = Field(None, description="Filebase Access Key.")
    filebase_bucket: str | None = Field(None, description="Filebase Bucket name")
    filebase_secret_key: str | None = Field(None, description="Filebase secret key")

class PostRemoteServersBodyGoogleCloudStorage(PermissiveModel):
    """Google Cloud Storage connection settings"""
    google_cloud_storage_bucket: str | None = Field(None, description="Google Cloud Storage bucket name")
    google_cloud_storage_credentials_json: str | None = Field(None, description="A JSON file that contains the private key. To generate see https://cloud.google.com/storage/docs/json_api/v1/how-tos/authorizing#APIKey")
    google_cloud_storage_project_id: str | None = Field(None, description="Google Cloud Project ID")

class PostRemoteServersBodyRackspace(PermissiveModel):
    """Rackspace Cloud Files connection settings"""
    rackspace_api_key: str | None = Field(None, description="Rackspace API key from the Rackspace Cloud Control Panel.")
    rackspace_container: str | None = Field(None, description="The name of the container (top level directory) where files will sync.")
    rackspace_region: str | None = Field(None, description="Three letter airport code for Rackspace region. See https://support.rackspace.com/how-to/about-regions/")
    rackspace_username: str | None = Field(None, description="Rackspace username used to login to the Rackspace Cloud Control Panel.")

class PostRemoteServersBodyS3Compatible(PermissiveModel):
    """S3-compatible storage connection settings"""
    s3_compatible_access_key: str | None = Field(None, description="S3-compatible Access Key.")
    s3_compatible_bucket: str | None = Field(None, description="S3-compatible Bucket name")
    s3_compatible_endpoint: str | None = Field(None, description="S3-compatible endpoint")
    s3_compatible_secret_key: str | None = Field(None, description="S3-compatible secret key")

class PostRemoteServersBodyWasabi(PermissiveModel):
    """Wasabi storage connection settings"""
    wasabi_access_key: str | None = Field(None, description="Wasabi access key.")
    wasabi_bucket: str | None = Field(None, description="Wasabi Bucket name")
    wasabi_region: str | None = Field(None, description="Wasabi region")
    wasabi_secret_key: str | None = Field(None, description="Wasabi secret key.")


# Rebuild models to resolve forward references (required for circular refs)
PatchFormFieldSetsIdBodyFormFieldsItem.model_rebuild()
PatchRemoteServersIdBodyAws.model_rebuild()
PatchRemoteServersIdBodyAzureBlobStorage.model_rebuild()
PatchRemoteServersIdBodyAzureFilesStorage.model_rebuild()
PatchRemoteServersIdBodyBackblazeB2.model_rebuild()
PatchRemoteServersIdBodyFilebase.model_rebuild()
PatchRemoteServersIdBodyGoogleCloudStorage.model_rebuild()
PatchRemoteServersIdBodyRackspace.model_rebuild()
PatchRemoteServersIdBodyS3Compatible.model_rebuild()
PatchRemoteServersIdBodyWasabi.model_rebuild()
PostFormFieldSetsBodyFormFieldsItem.model_rebuild()
PostRemoteServersBodyAws.model_rebuild()
PostRemoteServersBodyAzureBlobStorage.model_rebuild()
PostRemoteServersBodyAzureFilesStorage.model_rebuild()
PostRemoteServersBodyBackblazeB2.model_rebuild()
PostRemoteServersBodyFilebase.model_rebuild()
PostRemoteServersBodyGoogleCloudStorage.model_rebuild()
PostRemoteServersBodyRackspace.model_rebuild()
PostRemoteServersBodyS3Compatible.model_rebuild()
PostRemoteServersBodyWasabi.model_rebuild()

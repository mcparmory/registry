"""
Grafana MCP Server - Pydantic Models

Generated: 2026-04-09 11:49:20 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field, RootModel

__all__ = [
    "AddDataSourceRequest",
    "AddOrgInviteRequest",
    "AddOrgUserRequest",
    "AddOrgUserToCurrentOrgRequest",
    "AddTeamGroupApiRequest",
    "AddTeamMemberRequest",
    "AddTeamRoleRequest",
    "AdminCreateUserRequest",
    "AdminDeleteUserRequest",
    "AdminDisableUserRequest",
    "AdminEnableUserRequest",
    "AdminGetUserAuthTokensRequest",
    "AdminLogoutUserRequest",
    "AdminRevokeUserAuthTokenRequest",
    "AdminUpdateUserPasswordRequest",
    "CallDatasourceResourceWithUidRequest",
    "CancelSnapshotRequest",
    "CheckDatasourceHealthWithUidRequest",
    "CreateCorrelationRequest",
    "CreateDashboardSnapshotRequest",
    "CreateLibraryElementRequest",
    "CreatePublicDashboardRequest",
    "CreateQueryRequest",
    "CreateRecordingRuleRequest",
    "CreateRecordingRuleWriteTargetRequest",
    "CreateReportRequest",
    "CreateServiceAccountRequest",
    "CreateSnapshotRequest",
    "CreateTeamRequest",
    "CreateTokenRequest",
    "DeleteAnnotationByIdRequest",
    "DeleteCloudMigrationTokenRequest",
    "DeleteCorrelationRequest",
    "DeleteDashboardSnapshotByDeleteKeyRequest",
    "DeleteDashboardSnapshotRequest",
    "DeleteDataSourceByUidRequest",
    "DeleteLibraryElementByUidRequest",
    "DeleteLicenseTokenRequest",
    "DeleteOrgByIdRequest",
    "DeletePublicDashboardRequest",
    "DeleteQueryRequest",
    "DeleteRecordingRuleRequest",
    "DeleteServiceAccountRequest",
    "DeleteSessionRequest",
    "DeleteTeamByIdRequest",
    "DeleteTokenRequest",
    "DisableDataSourceCacheRequest",
    "EnableDataSourceCacheRequest",
    "GetAnnotationByIdRequest",
    "GetAnnotationsRequest",
    "GetAnnotationTagsRequest",
    "GetCorrelationRequest",
    "GetCorrelationsBySourceUidRequest",
    "GetCorrelationsRequest",
    "GetDashboardSnapshotRequest",
    "GetDataSourceByUidRequest",
    "GetDataSourceCacheConfigRequest",
    "GetGroupRolesRequest",
    "GetLibraryElementByNameRequest",
    "GetLibraryElementByUidRequest",
    "GetLibraryElementConnectionsRequest",
    "GetLibraryElementsRequest",
    "GetOrgByIdRequest",
    "GetOrgByNameRequest",
    "GetOrgQuotaRequest",
    "GetOrgUsersForCurrentOrgLookupRequest",
    "GetOrgUsersForCurrentOrgRequest",
    "GetOrgUsersRequest",
    "GetPublicAnnotationsRequest",
    "GetPublicDashboardRequest",
    "GetReportsByDashboardUidRequest",
    "GetRoleAssignmentsRequest",
    "GetRoleRequest",
    "GetSessionRequest",
    "GetSettingsImageRequest",
    "GetShapshotListRequest",
    "GetSnapshotRequest",
    "GetTeamByIdRequest",
    "GetTeamGroupsApiRequest",
    "GetTeamMembersRequest",
    "GetTeamPreferencesRequest",
    "GetUserByIdRequest",
    "GetUserByLoginOrEmailRequest",
    "GetUserFromLdapRequest",
    "GetUserOrgListRequest",
    "GetUserQuotaRequest",
    "GetUserTeamsRequest",
    "ImportDashboardRequest",
    "ListRolesRequest",
    "ListTeamRolesRequest",
    "ListTeamsRolesRequest",
    "ListTokensRequest",
    "ListUserRolesRequest",
    "ListUsersRolesRequest",
    "MassDeleteAnnotationsRequest",
    "PatchAnnotationRequest",
    "PatchQueryCommentRequest",
    "PatchUserPreferencesRequest",
    "PostAnnotationRequest",
    "PostGraphiteAnnotationRequest",
    "PostLicenseTokenRequest",
    "PostSyncUserWithLdapRequest",
    "QueryMetricsWithExpressionsRequest",
    "QueryPublicDashboardRequest",
    "RemoveOrgUserForCurrentOrgRequest",
    "RemoveOrgUserRequest",
    "RemoveTeamGroupApiQueryRequest",
    "RemoveTeamMemberRequest",
    "RemoveTeamRoleRequest",
    "RemoveUserRoleRequest",
    "RenderReportCsVsRequest",
    "RenderReportPdFsRequest",
    "RetrieveServiceAccountRequest",
    "RevokeInviteRequest",
    "RouteConvertPrometheusCortexDeleteNamespaceRequest",
    "RouteConvertPrometheusCortexDeleteRuleGroupRequest",
    "RouteConvertPrometheusCortexGetNamespaceRequest",
    "RouteConvertPrometheusCortexGetRuleGroupRequest",
    "RouteConvertPrometheusCortexPostRuleGroupRequest",
    "RouteConvertPrometheusDeleteNamespaceRequest",
    "RouteConvertPrometheusDeleteRuleGroupRequest",
    "RouteConvertPrometheusGetNamespaceRequest",
    "RouteConvertPrometheusGetRuleGroupRequest",
    "RouteConvertPrometheusPostRuleGroupRequest",
    "RouteDeleteContactpointsRequest",
    "RouteDeleteMuteTimingRequest",
    "RouteDeleteTemplateRequest",
    "RouteExportMuteTimingRequest",
    "RouteExportMuteTimingsRequest",
    "RouteGetAlertRuleExportRequest",
    "RouteGetAlertRuleGroupExportRequest",
    "RouteGetAlertRulesExportRequest",
    "RouteGetContactpointsExportRequest",
    "RouteGetMuteTimingRequest",
    "RouteGetTemplateRequest",
    "RoutePostContactpointsRequest",
    "RoutePutContactpointRequest",
    "RoutePutMuteTimingRequest",
    "RoutePutTemplateRequest",
    "SearchDashboardSnapshotsRequest",
    "SearchOrgServiceAccountsWithPagingRequest",
    "SearchOrgsRequest",
    "SearchOrgUsersRequest",
    "SearchQueriesRequest",
    "SearchRequest",
    "SearchTeamGroupsRequest",
    "SearchTeamsRequest",
    "SearchUsersRequest",
    "SendReportRequest",
    "SendTestEmailRequest",
    "SetDataSourceCacheConfigRequest",
    "SetHelpFlagRequest",
    "SetResourcePermissionsForTeamRequest",
    "SetResourcePermissionsForUserRequest",
    "SetResourcePermissionsRequest",
    "SetTeamMembershipsRequest",
    "SetTeamRolesRequest",
    "StarDashboardByUidRequest",
    "StarQueryRequest",
    "TestCreateRecordingRuleRequest",
    "UnstarDashboardByUidRequest",
    "UnstarQueryRequest",
    "UpdateAnnotationRequest",
    "UpdateCorrelationRequest",
    "UpdateCurrentOrgAddressRequest",
    "UpdateDataSourceByUidRequest",
    "UpdateFolderPermissionsRequest",
    "UpdateLibraryElementRequest",
    "UpdateOrgAddressRequest",
    "UpdateOrgQuotaRequest",
    "UpdateOrgRequest",
    "UpdateOrgUserForCurrentOrgRequest",
    "UpdateOrgUserRequest",
    "UpdatePublicDashboardRequest",
    "UpdateRecordingRuleRequest",
    "UpdateServiceAccountRequest",
    "UpdateSignedInUserRequest",
    "UpdateTeamMemberRequest",
    "UpdateTeamRequest",
    "UpdateUserQuotaRequest",
    "UpdateUserRequest",
    "UploadSnapshotRequest",
    "UserSetUsingOrgRequest",
    "ViewPublicDashboardRequest",
    "DashboardAclUpdateItem",
    "ImportDashboardInput",
    "Json",
    "PrometheusRule",
    "ReportDashboard",
    "SetResourcePermissionCommand",
    "TimeInterval",
    "Transformation",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_roles
class ListRolesRequestQuery(StrictModel):
    delegatable: bool | None = Field(default=None, description="When enabled, filters the results to only include roles that the signed-in user has permission to assign to others.")
    include_hidden: bool | None = Field(default=None, validation_alias="includeHidden", serialization_alias="includeHidden", description="When enabled, includes roles that are marked as hidden from the standard role list.")
    target_org_id: int | None = Field(default=None, validation_alias="targetOrgId", serialization_alias="targetOrgId", description="The numeric identifier of the target organization. When specified, retrieves roles for that organization instead of the signed-in user's current organization.", json_schema_extra={'format': 'int64'})
class ListRolesRequest(StrictModel):
    """Retrieve all available roles for the signed-in user's organization, including both global and organization-local roles. Requires the `roles:read` permission with `roles:*` scope."""
    query: ListRolesRequestQuery | None = None

# Operation: get_role
class GetRoleRequestPath(StrictModel):
    role_uid: str = Field(default=..., validation_alias="roleUID", serialization_alias="roleUID", description="The unique identifier of the role to retrieve.")
class GetRoleRequest(StrictModel):
    """Retrieve a specific role by its unique identifier. Requires `roles:read` permission with `roles:*` scope."""
    path: GetRoleRequestPath

# Operation: list_role_assignments
class GetRoleAssignmentsRequestPath(StrictModel):
    role_uid: str = Field(default=..., validation_alias="roleUID", serialization_alias="roleUID", description="The unique identifier of the role for which to retrieve assignments.")
class GetRoleAssignmentsRequest(StrictModel):
    """Retrieve all user and team assignments for a specific role. This returns direct role assignments only and excludes assignments inherited through group attribute synchronization."""
    path: GetRoleAssignmentsRequestPath

# Operation: list_team_roles_search
class ListTeamsRolesRequestBody(StrictModel):
    include_hidden: bool | None = Field(default=None, validation_alias="includeHidden", serialization_alias="includeHidden", description="Whether to include hidden roles in the results. Set to true to show roles that are normally hidden from view.")
    team_ids: list[int] | None = Field(default=None, validation_alias="teamIds", serialization_alias="teamIds", description="Array of team identifiers to retrieve roles for. If provided, only roles assigned to these teams will be returned.")
    user_ids: list[int] | None = Field(default=None, validation_alias="userIds", serialization_alias="userIds", description="Array of user identifiers to filter results. If provided, only roles assigned to users within the specified teams will be included.")
class ListTeamsRolesRequest(StrictModel):
    """Retrieve all roles that have been directly assigned to specified teams. Requires `teams.roles:read` permission with `teams:id:*` scope."""
    body: ListTeamsRolesRequestBody | None = None

# Operation: list_team_roles
class ListTeamRolesRequestPath(StrictModel):
    team_id: int = Field(default=..., validation_alias="teamId", serialization_alias="teamId", description="The unique identifier of the team whose roles you want to retrieve. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class ListTeamRolesRequestQuery(StrictModel):
    target_org_id: int | None = Field(default=None, validation_alias="targetOrgId", serialization_alias="targetOrgId", description="Optional organization ID to scope the role listing to a specific organization context. Must be a positive integer if provided.", json_schema_extra={'format': 'int64'})
class ListTeamRolesRequest(StrictModel):
    """Retrieve all roles assigned to a team. Requires `teams.roles:read` permission scoped to the specified team."""
    path: ListTeamRolesRequestPath
    query: ListTeamRolesRequestQuery | None = None

# Operation: assign_team_role
class AddTeamRoleRequestPath(StrictModel):
    team_id: int = Field(default=..., validation_alias="teamId", serialization_alias="teamId", description="The unique identifier of the team to which the role will be assigned. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class AddTeamRoleRequestBody(StrictModel):
    role_uid: str | None = Field(default=None, validation_alias="roleUid", serialization_alias="roleUid", description="The unique identifier of the role to assign to the team. Identifies which role permissions and capabilities the team will receive.")
class AddTeamRoleRequest(StrictModel):
    """Assign a role to a team. Requires permission to delegate team roles within your organization."""
    path: AddTeamRoleRequestPath
    body: AddTeamRoleRequestBody | None = None

# Operation: update_team_roles
class SetTeamRolesRequestPath(StrictModel):
    team_id: int = Field(default=..., validation_alias="teamId", serialization_alias="teamId", description="The unique identifier of the team whose roles are being updated. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class SetTeamRolesRequestQuery(StrictModel):
    target_org_id: int | None = Field(default=None, validation_alias="targetOrgId", serialization_alias="targetOrgId", description="The organization ID to scope the role update to. Optional; if provided, must be a positive integer.", json_schema_extra={'format': 'int64'})
class SetTeamRolesRequestBody(StrictModel):
    include_hidden: bool | None = Field(default=None, validation_alias="includeHidden", serialization_alias="includeHidden", description="Whether to include hidden roles in the operation. Optional boolean flag.")
    role_uids: list[str] | None = Field(default=None, validation_alias="roleUids", serialization_alias="roleUids", description="Array of role unique identifiers to assign to the team. Order may be significant for role precedence or application sequence.")
class SetTeamRolesRequest(StrictModel):
    """Update the roles assigned to a team. Requires permissions to both add and remove team roles with delegation scope."""
    path: SetTeamRolesRequestPath
    query: SetTeamRolesRequestQuery | None = None
    body: SetTeamRolesRequestBody | None = None

# Operation: remove_team_role
class RemoveTeamRoleRequestPath(StrictModel):
    role_uid: str = Field(default=..., validation_alias="roleUID", serialization_alias="roleUID", description="The unique identifier of the role to remove from the team.")
    team_id: int = Field(default=..., validation_alias="teamId", serialization_alias="teamId", description="The unique identifier of the team from which the role will be removed. Must be a valid positive integer.", json_schema_extra={'format': 'int64'})
class RemoveTeamRoleRequest(StrictModel):
    """Remove a role assignment from a team. Requires permission to delegate team roles."""
    path: RemoveTeamRoleRequestPath

# Operation: search_user_roles
class ListUsersRolesRequestBody(StrictModel):
    include_hidden: bool | None = Field(default=None, validation_alias="includeHidden", serialization_alias="includeHidden", description="Include hidden roles in the search results. When enabled, returns roles that are marked as hidden in addition to visible roles.")
    team_ids: list[int] | None = Field(default=None, validation_alias="teamIds", serialization_alias="teamIds", description="Filter results by team identifiers. Specify as an array of team IDs to limit role search to users belonging to these teams.")
    user_ids: list[int] | None = Field(default=None, validation_alias="userIds", serialization_alias="userIds", description="Filter results by user identifiers. Specify as an array of user IDs to search for roles assigned to these specific users.")
class ListUsersRolesRequest(StrictModel):
    """Search for roles directly assigned to specified users. Returns custom roles only, excluding built-in roles (Viewer, Editor, Admin, Grafana Admin) and team-inherited roles. Requires `users.roles:read` permission with `users:id:*` scope."""
    body: ListUsersRolesRequestBody | None = None

# Operation: list_user_roles
class ListUserRolesRequestPath(StrictModel):
    user_id: int = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The unique identifier of the user whose roles should be listed. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class ListUserRolesRequestQuery(StrictModel):
    include_hidden: bool | None = Field(default=None, validation_alias="includeHidden", serialization_alias="includeHidden", description="Whether to include hidden roles in the response. When enabled, returns roles that are normally hidden from the user interface.")
    target_org_id: int | None = Field(default=None, validation_alias="targetOrgId", serialization_alias="targetOrgId", description="The organization ID to scope the role query to. When specified, returns roles within that organization context. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class ListUserRolesRequest(StrictModel):
    """Retrieve all directly assigned roles for a specific user. This returns only explicitly assigned roles and excludes built-in roles (Viewer, Editor, Admin, Grafana Admin) and roles inherited from team membership."""
    path: ListUserRolesRequestPath
    query: ListUserRolesRequestQuery | None = None

# Operation: revoke_user_role
class RemoveUserRoleRequestPath(StrictModel):
    role_uid: str = Field(default=..., validation_alias="roleUID", serialization_alias="roleUID", description="The unique identifier of the role to revoke from the user.")
    user_id: int = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The numeric identifier of the user from whom the role will be removed. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class RemoveUserRoleRequestQuery(StrictModel):
    global_: bool | None = Field(default=None, validation_alias="global", serialization_alias="global", description="Whether the role assignment is global or organization-scoped. When false, the authenticated user's default organization will be used for the removal.")
class RemoveUserRoleRequest(StrictModel):
    """Revoke a role assignment from a user. Requires permission to remove user roles with delegate scope to prevent privilege escalation. For bulk role updates, use the set user role assignments operation instead."""
    path: RemoveUserRoleRequestPath
    query: RemoveUserRoleRequestQuery | None = None

# Operation: assign_resource_permissions
class SetResourcePermissionsRequestPath(StrictModel):
    resource: str = Field(default=..., description="The type of resource to assign permissions for. Must be one of: datasources, teams, dashboards, folders, or serviceaccounts.")
    resource_id: str = Field(default=..., validation_alias="resourceID", serialization_alias="resourceID", description="The unique identifier of the specific resource instance for which permissions are being assigned.")
class SetResourcePermissionsRequestBody(StrictModel):
    permissions: list[SetResourcePermissionCommand] | None = Field(default=None, description="An array of permission assignment objects that define who has access and what actions they can perform. Refer to the resource description endpoint to see valid permission types for the specified resource.")
class SetResourcePermissionsRequest(StrictModel):
    """Assign or update permissions for a resource (datasource, team, dashboard, folder, or service account) by specifying the resource type and ID along with the desired permission assignments."""
    path: SetResourcePermissionsRequestPath
    body: SetResourcePermissionsRequestBody | None = None

# Operation: grant_team_resource_permissions
class SetResourcePermissionsForTeamRequestPath(StrictModel):
    resource: str = Field(default=..., description="The type of resource to grant permissions for. Must be one of: datasources, teams, dashboards, folders, or serviceaccounts.")
    resource_id: str = Field(default=..., validation_alias="resourceID", serialization_alias="resourceID", description="The unique identifier of the resource for which permissions are being granted.")
    team_id: int = Field(default=..., validation_alias="teamID", serialization_alias="teamID", description="The unique identifier of the team receiving the permissions. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class SetResourcePermissionsForTeamRequestBody(StrictModel):
    permission: str | None = Field(default=None, description="The permission level or role to assign to the team. Refer to the resource-specific permissions endpoint for valid values.")
class SetResourcePermissionsForTeamRequest(StrictModel):
    """Grants or updates permissions for a team to access a specific resource. Supports permissions on datasources, teams, dashboards, folders, and service accounts."""
    path: SetResourcePermissionsForTeamRequestPath
    body: SetResourcePermissionsForTeamRequestBody | None = None

# Operation: grant_resource_permission
class SetResourcePermissionsForUserRequestPath(StrictModel):
    resource: str = Field(default=..., description="The type of resource to grant permissions for. Must be one of: datasources, teams, dashboards, folders, or serviceaccounts.")
    resource_id: str = Field(default=..., validation_alias="resourceID", serialization_alias="resourceID", description="The unique identifier of the resource instance for which permissions are being granted.")
    user_id: int = Field(default=..., validation_alias="userID", serialization_alias="userID", description="The numeric ID of the user or service account to grant permissions to. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class SetResourcePermissionsForUserRequestBody(StrictModel):
    permission: str | None = Field(default=None, description="The permission level to assign. Refer to the resource-specific permissions endpoint for valid permission values for the chosen resource type.")
class SetResourcePermissionsForUserRequest(StrictModel):
    """Grant or update a user's permissions for a specific resource. Supports datasources, teams, dashboards, folders, and service accounts."""
    path: SetResourcePermissionsForUserRequestPath
    body: SetResourcePermissionsForUserRequestBody | None = None

# Operation: sync_ldap_user
class PostSyncUserWithLdapRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the Grafana user to synchronize with LDAP, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class PostSyncUserWithLdapRequest(StrictModel):
    """Synchronize a single Grafana user's account with LDAP directory. Requires the `ldap.user:sync` permission in Grafana Enterprise with Fine-grained access control enabled."""
    path: PostSyncUserWithLdapRequestPath

# Operation: lookup_ldap_user
class GetUserFromLdapRequestPath(StrictModel):
    user_name: str = Field(default=..., description="The LDAP username to look up. This is the unique identifier used in your LDAP directory to retrieve the user's attributes and preview their Grafana mapping.")
class GetUserFromLdapRequest(StrictModel):
    """Retrieves LDAP user details by username to preview how the user will be mapped and synchronized in Grafana. Requires the `ldap.user:read` permission when Fine-grained access control is enabled in Grafana Enterprise."""
    path: GetUserFromLdapRequestPath

# Operation: create_user
class AdminCreateUserRequestBody(StrictModel):
    email: str | None = Field(default=None, description="Email address for the new user. Used for user identification and communication.")
    login: str | None = Field(default=None, description="Login username for the new user. Used for authentication and user identification within Grafana.")
    password: str | None = Field(default=None, description="Initial password for the new user account. Should meet Grafana's password security requirements.")
class AdminCreateUserRequest(StrictModel):
    """Create a new user in Grafana. Requires the `users:create` permission in Grafana Enterprise with Fine-grained access control enabled. Optionally assign the user to a different organization using the OrgId parameter when `auto_assign_org` is enabled."""
    body: AdminCreateUserRequestBody | None = None

# Operation: delete_user
class AdminDeleteUserRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user to delete, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class AdminDeleteUserRequest(StrictModel):
    """Permanently delete a global user from Grafana. Requires the `users:delete` permission with `global.users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""
    path: AdminDeleteUserRequestPath

# Operation: list_user_auth_tokens
class AdminGetUserAuthTokensRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user whose authentication tokens should be retrieved. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class AdminGetUserAuthTokensRequest(StrictModel):
    """Retrieve all active authentication tokens (devices) for a specific user. Requires Fine-grained access control permission `users.authtoken:list` with `global.users:*` scope in Grafana Enterprise."""
    path: AdminGetUserAuthTokensRequestPath

# Operation: disable_user
class AdminDisableUserRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user to disable, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class AdminDisableUserRequest(StrictModel):
    """Disable a user account in Grafana. Requires the `users:disable` permission with `global.users:1` scope in Grafana Enterprise with Fine-grained access control enabled."""
    path: AdminDisableUserRequestPath

# Operation: enable_user
class AdminEnableUserRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user to enable, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class AdminEnableUserRequest(StrictModel):
    """Activate a disabled user account in Grafana. Requires the `users:enable` permission with `global.users:1` scope in Grafana Enterprise with Fine-grained access control enabled."""
    path: AdminEnableUserRequestPath

# Operation: revoke_user_sessions
class AdminLogoutUserRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user whose sessions should be revoked. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class AdminLogoutUserRequest(StrictModel):
    """Revokes all active authentication tokens and sessions for a user across all devices. The user will be logged out immediately and must re-authenticate on next access. Requires the `users.logout` permission with `global.users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""
    path: AdminLogoutUserRequestPath

# Operation: set_user_password
class AdminUpdateUserPasswordRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user whose password will be updated. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class AdminUpdateUserPasswordRequestBody(StrictModel):
    password: str | None = Field(default=None, description="The new password to set for the user. If not provided, the password will not be changed.")
class AdminUpdateUserPasswordRequest(StrictModel):
    """Set or reset a user's password. Requires the `users.password:update` permission with `global.users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""
    path: AdminUpdateUserPasswordRequestPath
    body: AdminUpdateUserPasswordRequestBody | None = None

# Operation: get_user_quota
class GetUserQuotaRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user whose quota information should be retrieved. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class GetUserQuotaRequest(StrictModel):
    """Retrieve quota information for a specific user. Requires Fine-grained access control with `users.quotas:list` permission and `global.users:1` scope in Grafana Enterprise."""
    path: GetUserQuotaRequestPath

# Operation: update_user_quota
class UpdateUserQuotaRequestPath(StrictModel):
    quota_target: str = Field(default=..., description="The quota target type to update (e.g., 'dashboard', 'api_calls', 'storage'). Identifies which quota category to modify for the user.")
    user_id: int = Field(default=..., description="The unique identifier of the user whose quota is being updated. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class UpdateUserQuotaRequestBody(StrictModel):
    limit: int | None = Field(default=None, description="The new quota limit value as a positive integer. Specifies the maximum allowed usage for the quota target.", json_schema_extra={'format': 'int64'})
class UpdateUserQuotaRequest(StrictModel):
    """Update a user's quota limit for a specific quota target. Requires the `users.quotas:update` permission with global user scope in Grafana Enterprise with Fine-grained access control enabled."""
    path: UpdateUserQuotaRequestPath
    body: UpdateUserQuotaRequestBody | None = None

# Operation: revoke_user_auth_token
class AdminRevokeUserAuthTokenRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user whose authentication token should be revoked. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class AdminRevokeUserAuthTokenRequestBody(StrictModel):
    auth_token_id: int | None = Field(default=None, validation_alias="authTokenId", serialization_alias="authTokenId", description="The unique identifier of the specific authentication token (device session) to revoke. If not provided, a default token may be revoked. Must be a positive integer if specified.", json_schema_extra={'format': 'int64'})
class AdminRevokeUserAuthTokenRequest(StrictModel):
    """Revoke an authentication token for a user, forcing them to re-authenticate on their next activity. This invalidates the specified device session and logs out the user from that device."""
    path: AdminRevokeUserAuthTokenRequestPath
    body: AdminRevokeUserAuthTokenRequestBody | None = None

# Operation: list_annotations
class GetAnnotationsRequestQuery(StrictModel):
    alert_uid: str | None = Field(default=None, validation_alias="alertUID", serialization_alias="alertUID", description="Filter annotations by a specific alert rule using its unique identifier (UID).")
    dashboard_uid: str | None = Field(default=None, validation_alias="dashboardUID", serialization_alias="dashboardUID", description="Filter annotations to those associated with a specific dashboard using its unique identifier (UID).")
    limit: int | None = Field(default=None, description="Maximum number of annotation results to return in the response.", json_schema_extra={'format': 'int64'})
    tags: list[str] | None = Field(default=None, description="Filter organization-level annotations by one or more tags. Organization annotations come from annotation data sources and are not tied to a specific dashboard or panel. Provide tags as an array of strings.")
    match_any: bool | None = Field(default=None, validation_alias="matchAny", serialization_alias="matchAny", description="When filtering by tags, set to true to match annotations with any of the specified tags, or false to match only annotations with all specified tags.")
class GetAnnotationsRequest(StrictModel):
    """Retrieve annotations from your Grafana instance, optionally filtered by alert rule, dashboard, tags, or other criteria. Annotations can be scoped to specific dashboards or be organization-wide from annotation data sources."""
    query: GetAnnotationsRequestQuery | None = None

# Operation: create_annotation
class PostAnnotationRequestBody(StrictModel):
    dashboard_uid: str | None = Field(default=None, validation_alias="dashboardUID", serialization_alias="dashboardUID", description="The unique identifier of the dashboard where this annotation will be created. If omitted, the annotation is created at the organization level and can be queried from any dashboard using the Grafana annotations data source.")
    tags: list[str] | None = Field(default=None, description="An array of tag strings to categorize and organize the annotation for easier filtering and discovery.")
    text: str = Field(default=..., description="The annotation text content that will be displayed. This is the primary descriptive information for the annotation.")
    time_: int | None = Field(default=None, validation_alias="time", serialization_alias="time", description="The start time of the annotation as an epoch timestamp in millisecond resolution. Required for all annotations; use timeEnd to create a region annotation spanning a time period.", json_schema_extra={'format': 'int64'})
    time_end: int | None = Field(default=None, validation_alias="timeEnd", serialization_alias="timeEnd", description="The end time for a region annotation as an epoch timestamp in millisecond resolution. When specified, creates a region annotation spanning from time to timeEnd instead of a point-in-time annotation.", json_schema_extra={'format': 'int64'})
class PostAnnotationRequest(StrictModel):
    """Creates an annotation in Grafana that can be scoped to a specific dashboard and panel, or created as an organization-wide annotation. For region annotations spanning a time period, include both time and timeEnd properties."""
    body: PostAnnotationRequestBody

# Operation: create_graphite_annotation
class PostGraphiteAnnotationRequestBody(StrictModel):
    tags: Any | None = Field(default=None, description="Space-separated list of tags to associate with the annotation. Supports both modern and legacy Graphite tag formats (pre-0.10.0).")
    what: str | None = Field(default=None, description="Human-readable description or title of the annotation event.")
    when: int | None = Field(default=None, description="Unix timestamp (in seconds) indicating when the annotation occurred. If omitted, the current server time will be used.", json_schema_extra={'format': 'int64'})
class PostGraphiteAnnotationRequest(StrictModel):
    """Creates an annotation using Graphite-compatible event format. The annotation timestamp defaults to the current time if not specified, and tags can use either modern or pre-0.10.0 Graphite formats."""
    body: PostGraphiteAnnotationRequestBody | None = None

# Operation: delete_annotations
class MassDeleteAnnotationsRequestBody(StrictModel):
    annotation_id: int | None = Field(default=None, validation_alias="annotationId", serialization_alias="annotationId", description="The unique identifier of a specific annotation to delete. Provide one or more annotation IDs to target specific annotations across dashboards.", json_schema_extra={'format': 'int64'})
    dashboard_uid: str | None = Field(default=None, validation_alias="dashboardUID", serialization_alias="dashboardUID", description="The unique identifier of a dashboard. When provided, all annotations associated with this dashboard will be deleted.")
class MassDeleteAnnotationsRequest(StrictModel):
    """Delete one or more annotations from dashboards. Specify either annotation IDs or a dashboard UID to remove annotations in bulk."""
    body: MassDeleteAnnotationsRequestBody | None = None

# Operation: list_annotation_tags
class GetAnnotationTagsRequestQuery(StrictModel):
    tag: str | None = Field(default=None, description="Filter tags by a specific string value to narrow results to matching tags.")
    limit: str | None = Field(default=None, description="Maximum number of results to return in the response, defaulting to 100 if not specified.")
class GetAnnotationTagsRequest(StrictModel):
    """Retrieve all event tags that have been created in annotations, with optional filtering and pagination support."""
    query: GetAnnotationTagsRequestQuery | None = None

# Operation: get_annotation
class GetAnnotationByIdRequestPath(StrictModel):
    annotation_id: str = Field(default=..., description="The unique identifier of the annotation to retrieve.")
class GetAnnotationByIdRequest(StrictModel):
    """Retrieve a specific annotation by its unique identifier. Returns the full annotation details including metadata and content."""
    path: GetAnnotationByIdRequestPath

# Operation: update_annotation
class UpdateAnnotationRequestPath(StrictModel):
    annotation_id: str = Field(default=..., description="The unique identifier of the annotation to update.")
class UpdateAnnotationRequestBody(StrictModel):
    tags: list[str] | None = Field(default=None, description="An array of tags to associate with the annotation for categorization and filtering.")
    text: str | None = Field(default=None, description="The text content of the annotation.")
    time_: int | None = Field(default=None, validation_alias="time", serialization_alias="time", description="The start time of the annotation as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64'})
    time_end: int | None = Field(default=None, validation_alias="timeEnd", serialization_alias="timeEnd", description="The end time of the annotation as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64'})
class UpdateAnnotationRequest(StrictModel):
    """Update all properties of an annotation by its ID. Use this operation to replace the entire annotation; for partial updates, use the patch annotation operation instead."""
    path: UpdateAnnotationRequestPath
    body: UpdateAnnotationRequestBody | None = None

# Operation: update_annotation_partial
class PatchAnnotationRequestPath(StrictModel):
    annotation_id: str = Field(default=..., description="The unique identifier of the annotation to update.")
class PatchAnnotationRequestBody(StrictModel):
    tags: list[str] | None = Field(default=None, description="Array of tag strings to associate with the annotation. Tags are used for organizing and filtering annotations.")
    text: str | None = Field(default=None, description="The text content or description of the annotation.")
    time_: int | None = Field(default=None, validation_alias="time", serialization_alias="time", description="The start time of the annotation as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64'})
    time_end: int | None = Field(default=None, validation_alias="timeEnd", serialization_alias="timeEnd", description="The end time of the annotation as a Unix timestamp in milliseconds.", json_schema_extra={'format': 'int64'})
class PatchAnnotationRequest(StrictModel):
    """Update one or more properties of an annotation by its ID. Supports modifying text content, tags, start time, and end time. Available in Grafana 6.0.0-beta2 and later."""
    path: PatchAnnotationRequestPath
    body: PatchAnnotationRequestBody | None = None

# Operation: delete_annotation
class DeleteAnnotationByIdRequestPath(StrictModel):
    annotation_id: str = Field(default=..., description="The unique identifier of the annotation to delete.")
class DeleteAnnotationByIdRequest(StrictModel):
    """Permanently deletes an annotation by its unique identifier. This action cannot be undone."""
    path: DeleteAnnotationByIdRequestPath

# Operation: get_migration_session
class GetSessionRequestPath(StrictModel):
    uid: str = Field(default=..., description="The unique identifier of the migration session to retrieve.")
class GetSessionRequest(StrictModel):
    """Retrieve details of a cloud migration session by its unique identifier. Use this to check the status, configuration, and progress of a specific migration."""
    path: GetSessionRequestPath

# Operation: delete_migration_session
class DeleteSessionRequestPath(StrictModel):
    uid: str = Field(default=..., description="The unique identifier of the migration session to delete.")
class DeleteSessionRequest(StrictModel):
    """Permanently delete a cloud migration session by its unique identifier. This action removes the migration session and its associated data."""
    path: DeleteSessionRequestPath

# Operation: create_migration_snapshot
class CreateSnapshotRequestPath(StrictModel):
    uid: str = Field(default=..., description="The unique identifier of the migration session for which to create a snapshot.")
class CreateSnapshotRequestBody(StrictModel):
    resource_types: list[Literal["DASHBOARD", "DATASOURCE", "FOLDER", "LIBRARY_ELEMENT", "ALERT_RULE", "ALERT_RULE_GROUP", "CONTACT_POINT", "NOTIFICATION_POLICY", "NOTIFICATION_TEMPLATE", "MUTE_TIMING", "PLUGIN"]] | None = Field(default=None, validation_alias="resourceTypes", serialization_alias="resourceTypes", description="Optional list of resource types to include in the snapshot. Specifies which resource categories should be captured.")
class CreateSnapshotRequest(StrictModel):
    """Initiates the creation of an instance snapshot for a cloud migration session. Returns the snapshot UID upon successful initialization."""
    path: CreateSnapshotRequestPath
    body: CreateSnapshotRequestBody | None = None

# Operation: get_snapshot
class GetSnapshotRequestPath(StrictModel):
    uid: str = Field(default=..., description="The unique identifier of the migration session containing the snapshot.")
    snapshot_uid: str = Field(default=..., validation_alias="snapshotUid", serialization_alias="snapshotUid", description="The unique identifier of the snapshot to retrieve metadata for.")
class GetSnapshotRequestQuery(StrictModel):
    result_page: int | None = Field(default=None, validation_alias="resultPage", serialization_alias="resultPage", description="Page number for paginating through snapshot results, starting from page 1. Use with resultLimit to control result sets.", json_schema_extra={'format': 'int64'})
    result_limit: int | None = Field(default=None, validation_alias="resultLimit", serialization_alias="resultLimit", description="Maximum number of snapshot results to return per page, up to 100 results. Defaults to 100 if not specified.", json_schema_extra={'format': 'int64'})
    result_sort_column: str | None = Field(default=None, validation_alias="resultSortColumn", serialization_alias="resultSortColumn", description="Column to sort results by. Valid options are 'name' (resource name), 'resource_type' (type of resource), or 'status' (processing status). Defaults to system-defined sorting if not specified.")
    result_sort_order: str | None = Field(default=None, validation_alias="resultSortOrder", serialization_alias="resultSortOrder", description="Sort direction for results: 'ASC' for ascending or 'DESC' for descending order. Defaults to ascending.")
    errors_only: bool | None = Field(default=None, validation_alias="errorsOnly", serialization_alias="errorsOnly", description="When enabled, returns only resources with error statuses, filtering out successful results. Defaults to false (all results returned).")
class GetSnapshotRequest(StrictModel):
    """Retrieve detailed metadata about a migration snapshot, including its processing status and results. Use pagination and filtering options to navigate large result sets."""
    path: GetSnapshotRequestPath
    query: GetSnapshotRequestQuery | None = None

# Operation: cancel_snapshot
class CancelSnapshotRequestPath(StrictModel):
    uid: str = Field(default=..., description="The unique identifier of the cloud migration session containing the snapshot to be cancelled.")
    snapshot_uid: str = Field(default=..., validation_alias="snapshotUid", serialization_alias="snapshotUid", description="The unique identifier of the snapshot to cancel.")
class CancelSnapshotRequest(StrictModel):
    """Cancel an in-progress snapshot within a cloud migration session. This operation will halt the snapshot processing at any stage of its execution pipeline."""
    path: CancelSnapshotRequestPath

# Operation: upload_snapshot
class UploadSnapshotRequestPath(StrictModel):
    uid: str = Field(default=..., description="The unique identifier of the migration session to which this snapshot belongs.")
    snapshot_uid: str = Field(default=..., validation_alias="snapshotUid", serialization_alias="snapshotUid", description="The unique identifier of the snapshot being uploaded for processing.")
class UploadSnapshotRequest(StrictModel):
    """Upload a snapshot to the Grafana Migration Service for processing. This operation ingests snapshot data associated with a migration session for analysis and migration preparation."""
    path: UploadSnapshotRequestPath

# Operation: list_snapshots
class GetShapshotListRequestPath(StrictModel):
    uid: str = Field(default=..., description="The unique identifier of the migration session for which to retrieve snapshots.")
class GetShapshotListRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of snapshots to return in the response. Defaults to 100 if not specified.", json_schema_extra={'format': 'int64'})
    sort: str | None = Field(default=None, description="Sort order for results. Set to 'latest' to return snapshots in descending order by creation date.")
class GetShapshotListRequest(StrictModel):
    """Retrieve a list of snapshots for a cloud migration session. Results can be paginated and sorted by creation date."""
    path: GetShapshotListRequestPath
    query: GetShapshotListRequestQuery | None = None

# Operation: revoke_cloud_migration_token
class DeleteCloudMigrationTokenRequestPath(StrictModel):
    uid: str = Field(default=..., description="The unique identifier of the cloud migration token to revoke.")
class DeleteCloudMigrationTokenRequest(StrictModel):
    """Revokes and removes a cloud migration token, preventing further use for cloud migration operations. This action is permanent and cannot be undone."""
    path: DeleteCloudMigrationTokenRequestPath

# Operation: list_prometheus_alert_rules_by_namespace
class RouteConvertPrometheusCortexGetNamespaceRequestPath(StrictModel):
    namespace_title: str = Field(default=..., validation_alias="NamespaceTitle", serialization_alias="NamespaceTitle", description="The name of the namespace (folder) containing the alert rules to retrieve. This identifies which rule group to query.")
class RouteConvertPrometheusCortexGetNamespaceRequest(StrictModel):
    """Retrieves Grafana-managed alert rules that were imported from Prometheus-compatible sources for a specified namespace. This operation allows you to view rules organized within a particular folder or namespace."""
    path: RouteConvertPrometheusCortexGetNamespaceRequestPath

# Operation: convert_prometheus_rule_group
class RouteConvertPrometheusCortexPostRuleGroupRequestPath(StrictModel):
    namespace_title: str = Field(default=..., validation_alias="NamespaceTitle", serialization_alias="NamespaceTitle", description="The name of the namespace where the rule group will be created or updated.")
class RouteConvertPrometheusCortexPostRuleGroupRequestHeader(StrictModel):
    x_grafana_alerting_datasource_uid: str | None = Field(default=None, validation_alias="x-grafana-alerting-datasource-uid", serialization_alias="x-grafana-alerting-datasource-uid", description="The unique identifier of the Grafana datasource to use for alerting rules.")
    x_grafana_alerting_recording_rules_paused: bool | None = Field(default=None, validation_alias="x-grafana-alerting-recording-rules-paused", serialization_alias="x-grafana-alerting-recording-rules-paused", description="Whether to pause all recording rules in the converted rule group.")
    x_grafana_alerting_alert_rules_paused: bool | None = Field(default=None, validation_alias="x-grafana-alerting-alert-rules-paused", serialization_alias="x-grafana-alerting-alert-rules-paused", description="Whether to pause all alert rules in the converted rule group.")
    x_grafana_alerting_target_datasource_uid: str | None = Field(default=None, validation_alias="x-grafana-alerting-target-datasource-uid", serialization_alias="x-grafana-alerting-target-datasource-uid", description="The unique identifier of the target datasource for rule evaluation.")
    x_grafana_alerting_folder_uid: str | None = Field(default=None, validation_alias="x-grafana-alerting-folder-uid", serialization_alias="x-grafana-alerting-folder-uid", description="The unique identifier of the Grafana folder where the rule group will be stored.")
    x_grafana_alerting_notification_settings: str | None = Field(default=None, validation_alias="x-grafana-alerting-notification-settings", serialization_alias="x-grafana-alerting-notification-settings", description="Configuration for notification settings applied to the rule group, specified as a JSON string.")
class RouteConvertPrometheusCortexPostRuleGroupRequestBody(StrictModel):
    interval: int | None = Field(default=None, description="The evaluation interval for the rule group, specified in nanoseconds as a 64-bit integer. Represents the elapsed time between rule evaluations.", json_schema_extra={'format': 'int64'})
    labels: dict[str, str] | None = Field(default=None, description="Custom labels to attach to all rules in the group, specified as key-value pairs.")
    limit: int | None = Field(default=None, description="Maximum number of rules to process from the Prometheus rule group, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
    query_offset: str | None = Field(default=None, description="Time offset for query evaluation, specified as a duration string (e.g., ISO 8601 format).")
    rules: list[PrometheusRule] | None = Field(default=None, description="Array of Prometheus rules to convert. Each rule is converted to Grafana's rule format and included in the group.")
class RouteConvertPrometheusCortexPostRuleGroupRequest(StrictModel):
    """Converts a Prometheus rule group into a Grafana-compatible rule group and creates or updates it within the specified namespace. Existing groups that were not originally imported from a Prometheus source will not be replaced and will return an error."""
    path: RouteConvertPrometheusCortexPostRuleGroupRequestPath
    header: RouteConvertPrometheusCortexPostRuleGroupRequestHeader | None = None
    body: RouteConvertPrometheusCortexPostRuleGroupRequestBody | None = None

# Operation: delete_prometheus_rules_by_namespace
class RouteConvertPrometheusCortexDeleteNamespaceRequestPath(StrictModel):
    namespace_title: str = Field(default=..., validation_alias="NamespaceTitle", serialization_alias="NamespaceTitle", description="The name of the namespace containing the Prometheus-compatible rule groups to delete. This identifier specifies which namespace's rules will be removed.")
class RouteConvertPrometheusCortexDeleteNamespaceRequest(StrictModel):
    """Permanently deletes all rule groups that were imported from Prometheus-compatible sources within a specified namespace. This operation removes the entire namespace and its associated rules."""
    path: RouteConvertPrometheusCortexDeleteNamespaceRequestPath

# Operation: get_prometheus_rule_group
class RouteConvertPrometheusCortexGetRuleGroupRequestPath(StrictModel):
    namespace_title: str = Field(default=..., validation_alias="NamespaceTitle", serialization_alias="NamespaceTitle", description="The name of the namespace containing the rule group. This identifies the organizational container where the rule group is stored.")
    group: str = Field(default=..., validation_alias="Group", serialization_alias="Group", description="The name of the rule group to retrieve. This identifies the specific group of Prometheus rules within the namespace.")
class RouteConvertPrometheusCortexGetRuleGroupRequest(StrictModel):
    """Retrieves a single rule group in Prometheus-compatible format from a namespace. This operation is available only for rule groups that were imported from a Prometheus-compatible source."""
    path: RouteConvertPrometheusCortexGetRuleGroupRequestPath

# Operation: delete_prometheus_rule_group
class RouteConvertPrometheusCortexDeleteRuleGroupRequestPath(StrictModel):
    namespace_title: str = Field(default=..., validation_alias="NamespaceTitle", serialization_alias="NamespaceTitle", description="The namespace title that contains the rule group to delete. This identifies the logical grouping or project under which the rules are organized.")
    group: str = Field(default=..., validation_alias="Group", serialization_alias="Group", description="The name of the rule group to delete. This identifies the specific group of alert rules within the namespace.")
class RouteConvertPrometheusCortexDeleteRuleGroupRequest(StrictModel):
    """Deletes a specific rule group from Prometheus-compatible alerting rules. This operation only succeeds if the rule group was originally imported from a Prometheus-compatible source."""
    path: RouteConvertPrometheusCortexDeleteRuleGroupRequestPath

# Operation: get_prometheus_alert_rules
class RouteConvertPrometheusGetNamespaceRequestPath(StrictModel):
    namespace_title: str = Field(default=..., validation_alias="NamespaceTitle", serialization_alias="NamespaceTitle", description="The name of the namespace (folder) containing the Prometheus-imported alert rules to retrieve.")
class RouteConvertPrometheusGetNamespaceRequest(StrictModel):
    """Retrieves Grafana-managed alert rules that were imported from Prometheus-compatible sources for a specified namespace (folder)."""
    path: RouteConvertPrometheusGetNamespaceRequestPath

# Operation: convert_prometheus_rule_group_config
class RouteConvertPrometheusPostRuleGroupRequestPath(StrictModel):
    namespace_title: str = Field(default=..., validation_alias="NamespaceTitle", serialization_alias="NamespaceTitle", description="The title of the namespace where the rule group will be created or updated.")
class RouteConvertPrometheusPostRuleGroupRequestHeader(StrictModel):
    x_grafana_alerting_datasource_uid: str | None = Field(default=None, validation_alias="x-grafana-alerting-datasource-uid", serialization_alias="x-grafana-alerting-datasource-uid", description="The unique identifier of the Grafana datasource to use for alerting rules.")
    x_grafana_alerting_recording_rules_paused: bool | None = Field(default=None, validation_alias="x-grafana-alerting-recording-rules-paused", serialization_alias="x-grafana-alerting-recording-rules-paused", description="Whether to pause all recording rules in the converted rule group.")
    x_grafana_alerting_alert_rules_paused: bool | None = Field(default=None, validation_alias="x-grafana-alerting-alert-rules-paused", serialization_alias="x-grafana-alerting-alert-rules-paused", description="Whether to pause all alert rules in the converted rule group.")
    x_grafana_alerting_target_datasource_uid: str | None = Field(default=None, validation_alias="x-grafana-alerting-target-datasource-uid", serialization_alias="x-grafana-alerting-target-datasource-uid", description="The unique identifier of the target datasource for rule evaluation.")
    x_grafana_alerting_folder_uid: str | None = Field(default=None, validation_alias="x-grafana-alerting-folder-uid", serialization_alias="x-grafana-alerting-folder-uid", description="The unique identifier of the Grafana folder where the rule group will be stored.")
    x_grafana_alerting_notification_settings: str | None = Field(default=None, validation_alias="x-grafana-alerting-notification-settings", serialization_alias="x-grafana-alerting-notification-settings", description="Configuration for notification settings applied to the rule group, specified as a JSON string.")
class RouteConvertPrometheusPostRuleGroupRequestBody(StrictModel):
    interval: int | None = Field(default=None, description="The evaluation interval for the rule group, specified in nanoseconds as a 64-bit integer. Represents the elapsed time between rule evaluations.", json_schema_extra={'format': 'int64'})
    labels: dict[str, str] | None = Field(default=None, description="Custom labels to attach to all rules in the group as key-value pairs.")
    limit: int | None = Field(default=None, description="Maximum number of rules to process from the Prometheus rule group, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
    query_offset: str | None = Field(default=None, description="Time offset for query evaluation, specified as a duration string (e.g., ISO 8601 format).")
    rules: list[PrometheusRule] | None = Field(default=None, description="Array of Prometheus rules to convert. Each rule is converted to Grafana's rule format and included in the group.")
class RouteConvertPrometheusPostRuleGroupRequest(StrictModel):
    """Converts a Prometheus rule group into a Grafana-compatible rule group and creates or updates it in the specified namespace. Existing groups that were not originally imported from Prometheus sources will not be replaced and will return an error."""
    path: RouteConvertPrometheusPostRuleGroupRequestPath
    header: RouteConvertPrometheusPostRuleGroupRequestHeader | None = None
    body: RouteConvertPrometheusPostRuleGroupRequestBody | None = None

# Operation: delete_prometheus_rules_namespace
class RouteConvertPrometheusDeleteNamespaceRequestPath(StrictModel):
    namespace_title: str = Field(default=..., validation_alias="NamespaceTitle", serialization_alias="NamespaceTitle", description="The name of the namespace containing the Prometheus-imported rule groups to delete. This identifier specifies which namespace's rules will be removed.")
class RouteConvertPrometheusDeleteNamespaceRequest(StrictModel):
    """Deletes all rule groups that were imported from Prometheus-compatible sources within a specified namespace. This operation removes the entire namespace and its associated rules."""
    path: RouteConvertPrometheusDeleteNamespaceRequestPath

# Operation: get_prometheus_rule_group_config
class RouteConvertPrometheusGetRuleGroupRequestPath(StrictModel):
    namespace_title: str = Field(default=..., validation_alias="NamespaceTitle", serialization_alias="NamespaceTitle", description="The title or identifier of the namespace containing the rule group.")
    group: str = Field(default=..., validation_alias="Group", serialization_alias="Group", description="The name of the rule group to retrieve.")
class RouteConvertPrometheusGetRuleGroupRequest(StrictModel):
    """Retrieves a single rule group in Prometheus-compatible format from a previously imported Prometheus-compatible source configuration."""
    path: RouteConvertPrometheusGetRuleGroupRequestPath

# Operation: delete_prometheus_rule_group_config
class RouteConvertPrometheusDeleteRuleGroupRequestPath(StrictModel):
    namespace_title: str = Field(default=..., validation_alias="NamespaceTitle", serialization_alias="NamespaceTitle", description="The namespace title that contains the rule group to be deleted.")
    group: str = Field(default=..., validation_alias="Group", serialization_alias="Group", description="The name of the rule group to delete within the specified namespace.")
class RouteConvertPrometheusDeleteRuleGroupRequest(StrictModel):
    """Deletes a specific rule group from a Prometheus-compatible source. This operation only succeeds if the rule group was originally imported from Prometheus."""
    path: RouteConvertPrometheusDeleteRuleGroupRequestPath

# Operation: list_dashboard_snapshots
class SearchDashboardSnapshotsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of snapshots to return in the response. Defaults to 1000 if not specified.", json_schema_extra={'format': 'int64'})
class SearchDashboardSnapshotsRequest(StrictModel):
    """Retrieve a list of dashboard snapshots. Use the limit parameter to control the number of results returned."""
    query: SearchDashboardSnapshotsRequestQuery | None = None

# Operation: import_dashboard
class ImportDashboardRequestBody(StrictModel):
    dashboard: dict[str, Any] | None = Field(default=None, description="The dashboard configuration object containing the dashboard definition, settings, and panels to be imported.")
    folder_uid: str | None = Field(default=None, validation_alias="folderUid", serialization_alias="folderUid", description="The unique identifier of the folder where the imported dashboard will be stored. If not specified, the dashboard will be placed in the default location.")
    inputs: list[ImportDashboardInput] | None = Field(default=None, description="An array of input variables used for template substitution within the dashboard configuration. Each input provides values for dashboard variables or placeholders.")
    overwrite: bool | None = Field(default=None, description="Whether to overwrite an existing dashboard with the same name or UID. When true, the import will replace any conflicting dashboard; when false, the import will fail if a conflict exists.")
    path: str | None = Field(default=None, description="The file path or location identifier for the dashboard being imported. Used to identify the source of the dashboard configuration.")
    plugin_id: str | None = Field(default=None, validation_alias="pluginId", serialization_alias="pluginId", description="The plugin identifier associated with the dashboard, if the dashboard depends on or is specific to a particular Grafana plugin.")
class ImportDashboardRequest(StrictModel):
    """Import a dashboard configuration into Grafana, optionally overwriting existing dashboards and placing them in a specified folder. Supports variable substitution through inputs for dynamic dashboard provisioning."""
    body: ImportDashboardRequestBody | None = None

# Operation: get_public_dashboard
class GetPublicDashboardRequestPath(StrictModel):
    dashboard_uid: str = Field(default=..., validation_alias="dashboardUid", serialization_alias="dashboardUid", description="The unique identifier of the dashboard to retrieve. This is the dashboard's UID that has been configured for public access.")
class GetPublicDashboardRequest(StrictModel):
    """Retrieve a publicly shared dashboard by its unique identifier. This endpoint allows access to dashboards that have been configured for public sharing."""
    path: GetPublicDashboardRequestPath

# Operation: create_public_dashboard
class CreatePublicDashboardRequestPath(StrictModel):
    dashboard_uid: str = Field(default=..., validation_alias="dashboardUid", serialization_alias="dashboardUid", description="The unique identifier of the dashboard to make public.")
class CreatePublicDashboardRequestBody(StrictModel):
    annotations_enabled: bool | None = Field(default=None, validation_alias="annotationsEnabled", serialization_alias="annotationsEnabled", description="Enable or disable annotations visibility in the public dashboard.")
    is_enabled: bool | None = Field(default=None, validation_alias="isEnabled", serialization_alias="isEnabled", description="Enable or disable the public dashboard link.")
    share: str | None = Field(default=None, description="Access level or sharing mode for the public dashboard (e.g., view-only, edit permissions).")
    time_selection_enabled: bool | None = Field(default=None, validation_alias="timeSelectionEnabled", serialization_alias="timeSelectionEnabled", description="Enable or disable time range selection controls in the public dashboard.")
class CreatePublicDashboardRequest(StrictModel):
    """Create a public dashboard link for an existing dashboard, enabling external sharing with configurable access controls and features."""
    path: CreatePublicDashboardRequestPath
    body: CreatePublicDashboardRequestBody | None = None

# Operation: update_public_dashboard
class UpdatePublicDashboardRequestPath(StrictModel):
    dashboard_uid: str = Field(default=..., validation_alias="dashboardUid", serialization_alias="dashboardUid", description="The unique identifier of the dashboard that contains the public dashboard configuration to be updated.")
    uid: str = Field(default=..., description="The unique identifier of the public dashboard instance to update.")
class UpdatePublicDashboardRequestBody(StrictModel):
    uid2: str | None = Field(default=None, description="The unique identifier for the public dashboard (optional override if different from the path parameter).")
    annotations_enabled: bool | None = Field(default=None, validation_alias="annotationsEnabled", serialization_alias="annotationsEnabled", description="Enable or disable annotations display on the public dashboard.")
    is_enabled: bool | None = Field(default=None, validation_alias="isEnabled", serialization_alias="isEnabled", description="Enable or disable the public dashboard, controlling whether it is accessible to viewers.")
    share: str | None = Field(default=None, description="The sharing access level or mode for the public dashboard (e.g., public, restricted, or specific user/team access).")
    time_selection_enabled: bool | None = Field(default=None, validation_alias="timeSelectionEnabled", serialization_alias="timeSelectionEnabled", description="Enable or disable the time range selection controls, allowing viewers to modify the dashboard's time window.")
class UpdatePublicDashboardRequest(StrictModel):
    """Update the configuration and sharing settings of a public dashboard, including visibility, annotation display, time selection controls, and access permissions."""
    path: UpdatePublicDashboardRequestPath
    body: UpdatePublicDashboardRequestBody | None = None

# Operation: delete_public_dashboard
class DeletePublicDashboardRequestPath(StrictModel):
    dashboard_uid: str = Field(default=..., validation_alias="dashboardUid", serialization_alias="dashboardUid", description="The unique identifier of the dashboard that contains the public dashboard link to be deleted.")
    uid: str = Field(default=..., description="The unique identifier of the public dashboard link to be removed.")
class DeletePublicDashboardRequest(StrictModel):
    """Remove a public dashboard link from a dashboard, preventing public access to the dashboard's shared view."""
    path: DeletePublicDashboardRequestPath

# Operation: create_datasource
class AddDataSourceRequestBody(StrictModel):
    access: str | None = Field(default=None, description="Access mode for the data source, determining how Grafana communicates with it (e.g., direct browser access or server-side proxy).")
    database: str | None = Field(default=None, description="Database name or identifier for the data source connection.")
    is_default: bool | None = Field(default=None, validation_alias="isDefault", serialization_alias="isDefault", description="Whether this data source should be the default for new panels and queries.")
    json_data: dict[str, Any] | None = Field(default=None, validation_alias="jsonData", serialization_alias="jsonData", description="Additional JSON configuration specific to the data source type, such as timeout settings, SSL options, or type-specific parameters.")
    secure_json_data: dict[str, str] | None = Field(default=None, validation_alias="secureJsonData", serialization_alias="secureJsonData", description="Sensitive credentials stored as encrypted JSON, such as `password` and `basicAuthPassword`. These fields are encrypted at rest and returned as `secureJsonFields` in the response.")
    url: str | None = Field(default=None, description="Connection URL or endpoint for the data source (e.g., database host, API endpoint).")
    user: str | None = Field(default=None, description="Username for authenticating with the data source.")
    with_credentials: bool | None = Field(default=None, validation_alias="withCredentials", serialization_alias="withCredentials", description="Whether to send credentials (cookies, authorization headers) with cross-origin requests to the data source.")
class AddDataSourceRequest(StrictModel):
    """Create a new data source in Grafana. Sensitive credentials like passwords are automatically encrypted and stored securely in the database. Requires `datasources:create` permission in Grafana Enterprise with Fine-grained access control enabled."""
    body: AddDataSourceRequestBody | None = None

# Operation: list_correlations
class GetCorrelationsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of correlations to return per page, up to 1000. Defaults to 100 if not specified.", le=1000, json_schema_extra={'format': 'int64'})
    source_uid: list[str] | None = Field(default=None, validation_alias="sourceUID", serialization_alias="sourceUID", description="Filter correlations by one or more source datasource UIDs. Only correlations involving the specified sources will be returned.")
class GetCorrelationsRequest(StrictModel):
    """Retrieves all correlations across datasources, with optional filtering and pagination. Use this to discover relationships between data sources."""
    query: GetCorrelationsRequestQuery | None = None

# Operation: list_correlations_by_source
class GetCorrelationsBySourceUidRequestPath(StrictModel):
    source_uid: str = Field(default=..., validation_alias="sourceUID", serialization_alias="sourceUID", description="The unique identifier of the data source for which to retrieve correlations.")
class GetCorrelationsBySourceUidRequest(StrictModel):
    """Retrieves all correlations that originate from a specified data source. Use this to discover relationships and dependencies associated with a particular data source."""
    path: GetCorrelationsBySourceUidRequestPath

# Operation: create_correlation
class CreateCorrelationRequestPath(StrictModel):
    source_uid: str = Field(default=..., validation_alias="sourceUID", serialization_alias="sourceUID", description="The unique identifier of the source data source where the correlation will be attached.")
class CreateCorrelationRequestBodyConfig(StrictModel):
    field: str = Field(default=..., validation_alias="field", serialization_alias="field", description="The field name in the source data that will serve as the attachment point for the correlation link (e.g., 'message').")
    target: dict[str, Any] = Field(default=..., validation_alias="target", serialization_alias="target", description="The target data query definition as a key-value object that specifies what data to correlate to.")
    transformations: list[Transformation] | None = Field(default=None, validation_alias="transformations", serialization_alias="transformations", description="Optional array of transformations to apply to the correlation data before display or processing.")
class CreateCorrelationRequestBody(StrictModel):
    description: str | None = Field(default=None, description="Optional human-readable description of the correlation's purpose (e.g., 'Logs to Traces').")
    label: str | None = Field(default=None, description="Optional label to identify and organize the correlation within the data source.")
    target_uid: str | None = Field(default=None, validation_alias="targetUID", serialization_alias="targetUID", description="The unique identifier of the target data source for the correlation. Required when the correlation type is a query.")
    config: CreateCorrelationRequestBodyConfig
class CreateCorrelationRequest(StrictModel):
    """Create a correlation link between two data sources, enabling navigation from a field in the source to related data in a target source or query."""
    path: CreateCorrelationRequestPath
    body: CreateCorrelationRequestBody

# Operation: get_correlation
class GetCorrelationRequestPath(StrictModel):
    source_uid: str = Field(default=..., validation_alias="sourceUID", serialization_alias="sourceUID", description="The unique identifier of the data source containing the correlation.")
    correlation_uid: str = Field(default=..., validation_alias="correlationUID", serialization_alias="correlationUID", description="The unique identifier of the correlation to retrieve.")
class GetCorrelationRequest(StrictModel):
    """Retrieves a specific correlation by its unique identifier from a data source. Use this to fetch detailed information about a correlation relationship between data elements."""
    path: GetCorrelationRequestPath

# Operation: update_correlation
class UpdateCorrelationRequestPath(StrictModel):
    source_uid: str = Field(default=..., validation_alias="sourceUID", serialization_alias="sourceUID", description="The unique identifier of the data source containing the correlation to update.")
    correlation_uid: str = Field(default=..., validation_alias="correlationUID", serialization_alias="correlationUID", description="The unique identifier of the correlation to update.")
class UpdateCorrelationRequestBodyConfig(StrictModel):
    field: str | None = Field(default=None, validation_alias="field", serialization_alias="field", description="The field name where the correlation link will be attached (e.g., 'message'). This determines which field in the source data carries the correlation reference.")
    transformations: list[Transformation] | None = Field(default=None, validation_alias="transformations", serialization_alias="transformations", description="An ordered array of transformation operations to apply to source data before correlation. Each transformation is an object specifying a type (such as 'logfmt' for log format parsing or 'regex' for pattern matching) and relevant parameters like 'expression' and 'variable' for regex transformations.")
class UpdateCorrelationRequestBody(StrictModel):
    description: str | None = Field(default=None, description="An optional human-readable description explaining the purpose or context of this correlation (e.g., 'Logs to Traces').")
    label: str | None = Field(default=None, description="An optional label to identify and organize the correlation within your data source.")
    config: UpdateCorrelationRequestBodyConfig | None = None
class UpdateCorrelationRequest(StrictModel):
    """Updates an existing correlation configuration for a data source, allowing you to modify the field attachment point, data transformations, description, and label."""
    path: UpdateCorrelationRequestPath
    body: UpdateCorrelationRequestBody | None = None

# Operation: get_datasource
class GetDataSourceByUidRequestPath(StrictModel):
    uid: str = Field(default=..., description="The unique identifier of the data source to retrieve.")
class GetDataSourceByUidRequest(StrictModel):
    """Retrieve a single data source by its unique identifier. Requires datasources:read permission with appropriate scopes in Grafana Enterprise with Fine-grained access control enabled."""
    path: GetDataSourceByUidRequestPath

# Operation: update_datasource
class UpdateDataSourceByUidRequestPath(StrictModel):
    uid: str = Field(default=..., description="The unique identifier of the data source to update.")
class UpdateDataSourceByUidRequestBody(StrictModel):
    access: str | None = Field(default=None, description="The access mode for the data source, determining how Grafana communicates with it (e.g., direct or proxy).")
    database: str | None = Field(default=None, description="The default database name to use for queries against this data source.")
    is_default: bool | None = Field(default=None, validation_alias="isDefault", serialization_alias="isDefault", description="Whether this data source should be the default for its type in Grafana.")
    json_data: dict[str, Any] | None = Field(default=None, validation_alias="jsonData", serialization_alias="jsonData", description="Additional JSON configuration data specific to the data source type, such as authentication details or connection parameters.")
    secure_json_data: dict[str, str] | None = Field(default=None, validation_alias="secureJsonData", serialization_alias="secureJsonData", description="Sensitive configuration data that will be encrypted before storage, such as passwords and basic authentication credentials. These fields should not be included in jsonData.")
    url: str | None = Field(default=None, description="The URL endpoint or connection string for the data source.")
    user: str | None = Field(default=None, description="The username for authenticating with the data source.")
    with_credentials: bool | None = Field(default=None, validation_alias="withCredentials", serialization_alias="withCredentials", description="Whether to send credentials (cookies, authorization headers) when making cross-origin requests to the data source.")
class UpdateDataSourceByUidRequest(StrictModel):
    """Update an existing data source configuration. Sensitive credentials like passwords should be provided in secureJsonData to ensure they are encrypted and stored securely in the database."""
    path: UpdateDataSourceByUidRequestPath
    body: UpdateDataSourceByUidRequestBody | None = None

# Operation: delete_datasource
class DeleteDataSourceByUidRequestPath(StrictModel):
    uid: str = Field(default=..., description="The unique identifier of the data source to delete.")
class DeleteDataSourceByUidRequest(StrictModel):
    """Permanently delete a data source by its unique identifier. Requires datasources:delete permission with appropriate scopes in Grafana Enterprise with Fine-grained access control enabled."""
    path: DeleteDataSourceByUidRequestPath

# Operation: delete_correlation
class DeleteCorrelationRequestPath(StrictModel):
    uid: str = Field(default=..., description="The unique identifier of the datasource containing the correlation to delete.")
    correlation_uid: str = Field(default=..., validation_alias="correlationUID", serialization_alias="correlationUID", description="The unique identifier of the correlation to delete.")
class DeleteCorrelationRequest(StrictModel):
    """Remove a correlation from a datasource. This permanently deletes the specified correlation relationship."""
    path: DeleteCorrelationRequestPath

# Operation: check_datasource_health
class CheckDatasourceHealthWithUidRequestPath(StrictModel):
    uid: str = Field(default=..., description="The unique identifier of the datasource to check. This UID is used to locate and verify the health status of the specific plugin datasource.")
class CheckDatasourceHealthWithUidRequest(StrictModel):
    """Performs a health check on a plugin datasource to verify its connectivity and operational status. Returns the health status of the datasource identified by the provided UID."""
    path: CheckDatasourceHealthWithUidRequestPath

# Operation: fetch_datasource_resource
class CallDatasourceResourceWithUidRequestPath(StrictModel):
    datasource_proxy_route: str = Field(default=..., description="The unique identifier of the data source to query.")
    uid: str = Field(default=..., description="The proxy route path that specifies which resource endpoint within the data source to access.")
class CallDatasourceResourceWithUidRequest(StrictModel):
    """Retrieve data from a specific data source resource by its unique identifier and proxy route. This operation allows you to access data source resources through their configured proxy endpoints."""
    path: CallDatasourceResourceWithUidRequestPath

# Operation: get_datasource_cache_config
class GetDataSourceCacheConfigRequestPath(StrictModel):
    data_source_uid: str = Field(default=..., validation_alias="dataSourceUID", serialization_alias="dataSourceUID", description="The unique identifier of the data source for which to retrieve cache configuration.")
class GetDataSourceCacheConfigRequestQuery(StrictModel):
    data_source_type: str | None = Field(default=None, validation_alias="dataSourceType", serialization_alias="dataSourceType", description="Optional type identifier for the data source, used to filter or validate the cache configuration retrieval.")
class GetDataSourceCacheConfigRequest(StrictModel):
    """Retrieve the cache configuration settings for a specific data source. Returns caching policies and parameters that control how data from this source is cached."""
    path: GetDataSourceCacheConfigRequestPath
    query: GetDataSourceCacheConfigRequestQuery | None = None

# Operation: configure_datasource_cache
class SetDataSourceCacheConfigRequestPath(StrictModel):
    data_source_uid: str = Field(default=..., validation_alias="dataSourceUID", serialization_alias="dataSourceUID", description="The unique identifier of the data source to configure caching for.")
class SetDataSourceCacheConfigRequestQuery(StrictModel):
    data_source_type: str | None = Field(default=None, validation_alias="dataSourceType", serialization_alias="dataSourceType", description="The type of data source (e.g., Prometheus, Graphite, InfluxDB). Used to identify the data source category.")
class SetDataSourceCacheConfigRequestBody(StrictModel):
    data_source_id: int | None = Field(default=None, validation_alias="dataSourceID", serialization_alias="dataSourceID", description="The numeric identifier of the data source. Used as an alternative or supplementary identifier for the data source.", json_schema_extra={'format': 'int64'})
    enabled: bool | None = Field(default=None, description="Enable or disable caching for this data source. When disabled, cached data will not be used or stored.")
    ttl_queries_ms: int | None = Field(default=None, validation_alias="ttlQueriesMs", serialization_alias="ttlQueriesMs", description="Time-to-live for cached queries in milliseconds. Specifies how long query results remain in the cache before expiration. Only used if UseDefaultTTL is disabled.", json_schema_extra={'format': 'int64'})
    ttl_resources_ms: int | None = Field(default=None, validation_alias="ttlResourcesMs", serialization_alias="ttlResourcesMs", description="Time-to-live for cached resources in milliseconds. Specifies how long resource data remains in the cache before expiration. Only used if UseDefaultTTL is disabled.", json_schema_extra={'format': 'int64'})
    use_default_ttl: bool | None = Field(default=None, validation_alias="useDefaultTTL", serialization_alias="useDefaultTTL", description="When enabled, ignores the TTLQueriesMs and TTLResourcesMs values and uses the default TTL settings from the Grafana configuration file instead.")
class SetDataSourceCacheConfigRequest(StrictModel):
    """Configure caching behavior for a specific data source, including TTL settings for queries and resources. Use this to optimize performance by controlling how long cached data persists."""
    path: SetDataSourceCacheConfigRequestPath
    query: SetDataSourceCacheConfigRequestQuery | None = None
    body: SetDataSourceCacheConfigRequestBody | None = None

# Operation: disable_datasource_cache
class DisableDataSourceCacheRequestPath(StrictModel):
    data_source_uid: str = Field(default=..., validation_alias="dataSourceUID", serialization_alias="dataSourceUID", description="The unique identifier of the data source for which caching should be disabled.")
class DisableDataSourceCacheRequestQuery(StrictModel):
    data_source_type: str | None = Field(default=None, validation_alias="dataSourceType", serialization_alias="dataSourceType", description="The type or category of the data source, used to provide additional context for the cache disabling operation.")
class DisableDataSourceCacheRequest(StrictModel):
    """Disable caching for a specific data source to ensure fresh data is fetched on subsequent queries. This operation clears the cache configuration for the specified data source."""
    path: DisableDataSourceCacheRequestPath
    query: DisableDataSourceCacheRequestQuery | None = None

# Operation: enable_datasource_cache
class EnableDataSourceCacheRequestPath(StrictModel):
    data_source_uid: str = Field(default=..., validation_alias="dataSourceUID", serialization_alias="dataSourceUID", description="The unique identifier of the data source for which caching should be enabled.")
class EnableDataSourceCacheRequestQuery(StrictModel):
    data_source_type: str | None = Field(default=None, validation_alias="dataSourceType", serialization_alias="dataSourceType", description="The type of data source (e.g., Prometheus, Graphite, Elasticsearch). Used to apply type-specific cache configuration if needed.")
class EnableDataSourceCacheRequest(StrictModel):
    """Enable caching for a data source to improve query performance and reduce load on the underlying data source."""
    path: EnableDataSourceCacheRequestPath
    query: EnableDataSourceCacheRequestQuery | None = None

# Operation: query_metrics
class QueryMetricsWithExpressionsRequestBody(StrictModel):
    from_: str = Field(default=..., validation_alias="from", serialization_alias="from", description="Start time for the query range as an epoch timestamp in milliseconds or a relative Grafana time unit (e.g., 'now-1h', 'now-24h'). Relative units are calculated from the current time.")
    queries: list[Json] = Field(default=..., description="Array of query objects to execute. Each query must specify a unique datasourceId and can optionally include a refId identifier (defaults to 'A'), maxDataPoints for rendering limits (defaults to 100), and intervalMs for time series granularity in milliseconds (defaults to 1000). Query objects support datasource-specific fields like rawSql for SQL queries and format specification (e.g., 'table').")
    to: str = Field(default=..., description="End time for the query range as an epoch timestamp in milliseconds or a relative Grafana time unit (e.g., 'now'). Relative units are calculated from the current time.")
class QueryMetricsWithExpressionsRequest(StrictModel):
    """Execute metric queries against a data source with support for expressions and custom time ranges. Requires datasources:query permission in Grafana Enterprise with Fine-grained access control enabled."""
    body: QueryMetricsWithExpressionsRequestBody

# Operation: set_folder_permissions
class UpdateFolderPermissionsRequestPath(StrictModel):
    folder_uid: str = Field(default=..., description="The unique identifier of the folder whose permissions should be updated.")
class UpdateFolderPermissionsRequestBody(StrictModel):
    items: list[DashboardAclUpdateItem] | None = Field(default=None, description="An array of permission objects defining who has access to the folder and what level of access they have. Permissions not included in this list will be removed from the folder.")
class UpdateFolderPermissionsRequest(StrictModel):
    """Sets permissions for a folder by replacing all existing permissions with the ones specified in the request. Any permissions not included will be removed."""
    path: UpdateFolderPermissionsRequestPath
    body: UpdateFolderPermissionsRequestBody | None = None

# Operation: list_group_roles
class GetGroupRolesRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the group for which to retrieve mapped roles.")
class GetGroupRolesRequest(StrictModel):
    """Retrieve all roles mapped to a specific group. This endpoint is experimental and requires the `groupAttributeSync` feature flag to be enabled."""
    path: GetGroupRolesRequestPath

# Operation: list_library_elements
class GetLibraryElementsRequestQuery(StrictModel):
    search_string: str | None = Field(default=None, validation_alias="searchString", serialization_alias="searchString", description="Search for library elements by matching text against their name or description fields.")
    sort_direction: Literal["alpha-asc", "alpha-desc"] | None = Field(default=None, validation_alias="sortDirection", serialization_alias="sortDirection", description="Sort the returned elements alphabetically in ascending or descending order.")
    type_filter: str | None = Field(default=None, validation_alias="typeFilter", serialization_alias="typeFilter", description="Filter results to include only elements of specified types. Provide multiple types as a comma-separated list.")
    exclude_uid: str | None = Field(default=None, validation_alias="excludeUid", serialization_alias="excludeUid", description="Exclude a specific element from the search results by providing its unique identifier (UID).")
    folder_filter_ui_ds: str | None = Field(default=None, validation_alias="folderFilterUIDs", serialization_alias="folderFilterUIDs", description="Filter results to include only elements located in specified folders. Provide multiple folder UIDs as a comma-separated list.")
    per_page: int | None = Field(default=None, validation_alias="perPage", serialization_alias="perPage", description="Set the maximum number of elements to return per page. Defaults to 100 results per page.", json_schema_extra={'format': 'int64'})
class GetLibraryElementsRequest(StrictModel):
    """Retrieve a paginated list of all library elements that the authenticated user has permission to view. Results can be filtered, searched, and sorted to find specific elements."""
    query: GetLibraryElementsRequestQuery | None = None

# Operation: create_library_element
class CreateLibraryElementRequestBody(StrictModel):
    folder_uid: str | None = Field(default=None, validation_alias="folderUid", serialization_alias="folderUid", description="The unique identifier of the folder where this library element will be stored. If not provided, the element will be created in the default location.")
    model: dict[str, Any] | None = Field(default=None, description="The JSON configuration object defining the library element's properties, type, and settings. This object structure depends on the type of library element being created.")
class CreateLibraryElementRequest(StrictModel):
    """Creates a new library element that can be reused across dashboards and other resources. Optionally specify a folder location and provide the element configuration as a JSON model."""
    body: CreateLibraryElementRequestBody | None = None

# Operation: get_library_element_by_name
class GetLibraryElementByNameRequestPath(StrictModel):
    library_element_name: str = Field(default=..., description="The name of the library element to retrieve. This is the unique identifier used to look up the library element.")
class GetLibraryElementByNameRequest(StrictModel):
    """Retrieve a library element by its name. Returns the library element matching the specified name."""
    path: GetLibraryElementByNameRequestPath

# Operation: get_library_element
class GetLibraryElementByUidRequestPath(StrictModel):
    library_element_uid: str = Field(default=..., description="The unique identifier of the library element to retrieve.")
class GetLibraryElementByUidRequest(StrictModel):
    """Retrieve a specific library element by its unique identifier. Returns the complete library element details for the given UID."""
    path: GetLibraryElementByUidRequestPath

# Operation: update_library_element
class UpdateLibraryElementRequestPath(StrictModel):
    library_element_uid: str = Field(default=..., description="The unique identifier of the library element to update.")
class UpdateLibraryElementRequestBody(StrictModel):
    folder_uid: str | None = Field(default=None, validation_alias="folderUid", serialization_alias="folderUid", description="The unique identifier of the folder where the library element should be stored or moved to.")
    model: dict[str, Any] | None = Field(default=None, description="The JSON model containing the library element's properties and configuration to be updated.")
class UpdateLibraryElementRequest(StrictModel):
    """Update an existing library element by modifying its properties, folder location, or model configuration. Specify the library element by its unique identifier and provide the fields you want to change."""
    path: UpdateLibraryElementRequestPath
    body: UpdateLibraryElementRequestBody | None = None

# Operation: delete_library_element
class DeleteLibraryElementByUidRequestPath(StrictModel):
    library_element_uid: str = Field(default=..., description="The unique identifier of the library element to delete. Must reference an unconnected library element.")
class DeleteLibraryElementByUidRequest(StrictModel):
    """Permanently delete a library element by its unique identifier. This action cannot be undone and will fail if the library element is currently connected to other resources."""
    path: DeleteLibraryElementByUidRequestPath

# Operation: list_library_element_connections
class GetLibraryElementConnectionsRequestPath(StrictModel):
    library_element_uid: str = Field(default=..., description="The unique identifier of the library element for which to retrieve connections.")
class GetLibraryElementConnectionsRequest(StrictModel):
    """Retrieve all connections associated with a specific library element. Returns a list of dashboards, panels, or other resources that reference the library element."""
    path: GetLibraryElementConnectionsRequestPath

# Operation: create_license_token
class PostLicenseTokenRequestBody(StrictModel):
    instance: str | None = Field(default=None, description="The instance identifier for which to create the license token. If not specified, the token is created for the default instance.")
class PostLicenseTokenRequest(StrictModel):
    """Generate a new license token for the specified instance. Requires licensing:write permission to perform this operation."""
    body: PostLicenseTokenRequestBody | None = None

# Operation: remove_license_token
class DeleteLicenseTokenRequestBody(StrictModel):
    instance: str | None = Field(default=None, description="The Grafana instance identifier or URL where the license token should be removed.")
class DeleteLicenseTokenRequest(StrictModel):
    """Remove the license token from the Grafana database. This operation permanently deletes the stored license and requires the `licensing:delete` permission. Available in Grafana Enterprise v7.4+."""
    body: DeleteLicenseTokenRequestBody | None = None

# Operation: update_organization_address
class UpdateCurrentOrgAddressRequestBody(StrictModel):
    address1: str | None = Field(default=None, description="The primary street address line for the organization's location.")
    address2: str | None = Field(default=None, description="The secondary street address line (e.g., suite, apartment, or unit number) for the organization's location.")
    city: str | None = Field(default=None, description="The city where the organization is located.")
    country: str | None = Field(default=None, description="The country where the organization is located.")
    state: str | None = Field(default=None, description="The state or province where the organization is located.")
    zipcode: str | None = Field(default=None, description="The postal or ZIP code for the organization's location.")
class UpdateCurrentOrgAddressRequest(StrictModel):
    """Update the address information for the current organization. Provide any address fields that need to be changed; omitted fields will remain unchanged."""
    body: UpdateCurrentOrgAddressRequestBody | None = None

# Operation: invite_organization_member
class AddOrgInviteRequestBody(StrictModel):
    login_or_email: str | None = Field(default=None, validation_alias="loginOrEmail", serialization_alias="loginOrEmail", description="The login username or email address of the person to invite to the organization.")
    role: Literal["None", "Viewer", "Editor", "Admin"] | None = Field(default=None, description="The role to assign to the invited member. Must be one of: None, Viewer, Editor, or Admin. Determines the member's permissions within the organization.")
    send_email: bool | None = Field(default=None, validation_alias="sendEmail", serialization_alias="sendEmail", description="Whether to send a notification email to the invitee. If true, an invitation email will be delivered; if false, the invite is created silently.")
class AddOrgInviteRequest(StrictModel):
    """Send an invitation to join an organization with a specified role. The invitee can be identified by their login or email address, and an optional notification email can be sent to them."""
    body: AddOrgInviteRequestBody | None = None

# Operation: revoke_invitation
class RevokeInviteRequestPath(StrictModel):
    invitation_code: str = Field(default=..., description="The unique code identifying the invitation to revoke. This code was provided when the invitation was created.")
class RevokeInviteRequest(StrictModel):
    """Revoke a pending organization invitation, preventing the recipient from accepting it. This operation invalidates the invitation code immediately."""
    path: RevokeInviteRequestPath

# Operation: list_organization_users
class GetOrgUsersForCurrentOrgRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of users to return in the response. Specify as a positive integer to limit result set size.", json_schema_extra={'format': 'int64'})
class GetOrgUsersForCurrentOrgRequest(StrictModel):
    """Retrieve all users in the current organization. Requires org admin role or the `org.users:read` permission in Grafana Enterprise with Fine-grained access control enabled."""
    query: GetOrgUsersForCurrentOrgRequestQuery | None = None

# Operation: add_user_to_organization
class AddOrgUserToCurrentOrgRequestBody(StrictModel):
    login_or_email: str | None = Field(default=None, validation_alias="loginOrEmail", serialization_alias="loginOrEmail", description="The login username or email address of the global user to add to the organization.")
    role: Literal["None", "Viewer", "Editor", "Admin"] | None = Field(default=None, description="The role to assign to the user within the organization. Must be one of: None, Viewer, Editor, or Admin.")
class AddOrgUserToCurrentOrgRequest(StrictModel):
    """Adds an existing global user to the current organization with a specified role. Requires the `org.users:add` permission with `users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""
    body: AddOrgUserToCurrentOrgRequestBody | None = None

# Operation: list_organization_users_lookup
class GetOrgUsersForCurrentOrgLookupRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of users to return in the response. Specify as a positive integer to limit the result set size.", json_schema_extra={'format': 'int64'})
class GetOrgUsersForCurrentOrgLookupRequest(StrictModel):
    """Retrieve a list of all users in the current organization with basic information. This lightweight endpoint is designed for UI operations like team member selection and permission management, and requires org admin role or admin privileges in any folder or team."""
    query: GetOrgUsersForCurrentOrgLookupRequestQuery | None = None

# Operation: update_org_user_role
class UpdateOrgUserForCurrentOrgRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user to update, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class UpdateOrgUserForCurrentOrgRequestBody(StrictModel):
    role: Literal["None", "Viewer", "Editor", "Admin"] | None = Field(default=None, description="The new role to assign to the user. Must be one of: None, Viewer, Editor, or Admin.")
class UpdateOrgUserForCurrentOrgRequest(StrictModel):
    """Updates a user's role within the current organization. Requires the `org.users.role:update` permission with `users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""
    path: UpdateOrgUserForCurrentOrgRequestPath
    body: UpdateOrgUserForCurrentOrgRequestBody | None = None

# Operation: remove_organization_user
class RemoveOrgUserForCurrentOrgRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user to remove from the organization. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class RemoveOrgUserForCurrentOrgRequest(StrictModel):
    """Remove a user from the current organization. Requires the `org.users:remove` permission with `users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""
    path: RemoveOrgUserForCurrentOrgRequestPath

# Operation: list_organizations
class SearchOrgsRequestQuery(StrictModel):
    perpage: int | None = Field(default=None, description="Number of organizations to return per page. Defaults to 1000 items per page; use this with the totalCount response field to navigate through all results.", json_schema_extra={'format': 'int64'})
class SearchOrgsRequest(StrictModel):
    """Retrieve a paginated list of all organizations. Use the totalCount field in the response to determine pagination, where each page contains up to the specified number of items."""
    query: SearchOrgsRequestQuery | None = None

# Operation: get_organization_by_name
class GetOrgByNameRequestPath(StrictModel):
    org_name: str = Field(default=..., description="The name of the organization to retrieve. This should be the exact organization name as it exists in the system.")
class GetOrgByNameRequest(StrictModel):
    """Retrieve a specific organization by its name. Use this operation to look up organization details when you know the organization's name."""
    path: GetOrgByNameRequestPath

# Operation: get_organization_by_id
class GetOrgByIdRequestPath(StrictModel):
    org_id: int = Field(default=..., description="The unique identifier of the organization to retrieve, provided as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetOrgByIdRequest(StrictModel):
    """Retrieve a specific organization by its unique identifier. Returns detailed organization information including metadata and configuration."""
    path: GetOrgByIdRequestPath

# Operation: update_organization
class UpdateOrgRequestPath(StrictModel):
    org_id: int = Field(default=..., description="The unique identifier of the organization to update, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class UpdateOrgRequest(StrictModel):
    """Update an existing organization's details and configuration. Requires the organization ID to identify which organization to modify."""
    path: UpdateOrgRequestPath

# Operation: delete_organization
class DeleteOrgByIdRequestPath(StrictModel):
    org_id: int = Field(default=..., description="The unique identifier of the organization to delete, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class DeleteOrgByIdRequest(StrictModel):
    """Permanently delete an organization and all associated data. This action cannot be undone."""
    path: DeleteOrgByIdRequestPath

# Operation: update_organization_address_by_id
class UpdateOrgAddressRequestPath(StrictModel):
    org_id: int = Field(default=..., description="The unique identifier of the organization whose address will be updated. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class UpdateOrgAddressRequestBody(StrictModel):
    address1: str | None = Field(default=None, description="The primary street address line (e.g., street number and name).")
    address2: str | None = Field(default=None, description="The secondary street address line for additional address details (e.g., suite, apartment, or unit number).")
    city: str | None = Field(default=None, description="The city or municipality name.")
    country: str | None = Field(default=None, description="The country name or code.")
    state: str | None = Field(default=None, description="The state, province, or region name or code.")
    zipcode: str | None = Field(default=None, description="The postal or ZIP code for the address.")
class UpdateOrgAddressRequest(StrictModel):
    """Update the physical address information for an organization. Provide any combination of address fields to update the organization's location details."""
    path: UpdateOrgAddressRequestPath
    body: UpdateOrgAddressRequestBody | None = None

# Operation: get_organization_quota_by_id
class GetOrgQuotaRequestPath(StrictModel):
    org_id: int = Field(default=..., description="The unique identifier of the organization whose quota information should be retrieved. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class GetOrgQuotaRequest(StrictModel):
    """Retrieve the quota limits and usage for a specific organization. Requires the `orgs.quotas:read` permission with the appropriate organization scope in Grafana Enterprise with Fine-grained access control enabled."""
    path: GetOrgQuotaRequestPath

# Operation: update_org_quota
class UpdateOrgQuotaRequestPath(StrictModel):
    quota_target: str = Field(default=..., description="The quota target type to update (e.g., users, dashboards, data sources). Identifies which resource quota to modify.")
    org_id: int = Field(default=..., description="The organization ID as a 64-bit integer. Identifies which organization's quota to update.", json_schema_extra={'format': 'int64'})
class UpdateOrgQuotaRequestBody(StrictModel):
    limit: int | None = Field(default=None, description="The new quota limit as a 64-bit integer. Specifies the maximum number of resources allowed for the quota target.", json_schema_extra={'format': 'int64'})
class UpdateOrgQuotaRequest(StrictModel):
    """Update the quota limit for a specific target within an organization. Requires the `orgs.quotas:write` permission in Grafana Enterprise with Fine-grained access control enabled."""
    path: UpdateOrgQuotaRequestPath
    body: UpdateOrgQuotaRequestBody | None = None

# Operation: list_organization_users_by_id
class GetOrgUsersRequestPath(StrictModel):
    org_id: int = Field(default=..., description="The unique identifier of the organization. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class GetOrgUsersRequest(StrictModel):
    """Retrieve all users in a Grafana organization. Requires the `org.users:read` permission with `users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""
    path: GetOrgUsersRequestPath

# Operation: add_organization_user
class AddOrgUserRequestPath(StrictModel):
    org_id: int = Field(default=..., description="The unique identifier of the organization to which the user will be added. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class AddOrgUserRequestBody(StrictModel):
    login_or_email: str | None = Field(default=None, validation_alias="loginOrEmail", serialization_alias="loginOrEmail", description="The login username or email address of the global user to add to the organization.")
    role: Literal["None", "Viewer", "Editor", "Admin"] | None = Field(default=None, description="The role to assign to the user within the organization. Valid options are: None, Viewer, Editor, or Admin. If not specified, defaults to None.")
class AddOrgUserRequest(StrictModel):
    """Add an existing global user to the current organization with an optional role assignment. Requires the `org.users:add` permission with `users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""
    path: AddOrgUserRequestPath
    body: AddOrgUserRequestBody | None = None

# Operation: search_organization_users
class SearchOrgUsersRequestPath(StrictModel):
    org_id: int = Field(default=..., description="The unique identifier of the organization to search users in. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class SearchOrgUsersRequest(StrictModel):
    """Search for users within a specific organization. Requires the `org.users:read` permission with `users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""
    path: SearchOrgUsersRequestPath

# Operation: update_organization_user_role
class UpdateOrgUserRequestPath(StrictModel):
    org_id: int = Field(default=..., description="The unique identifier of the organization containing the user. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    user_id: int = Field(default=..., description="The unique identifier of the user to update. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class UpdateOrgUserRequestBody(StrictModel):
    role: Literal["None", "Viewer", "Editor", "Admin"] | None = Field(default=None, description="The new role to assign to the user. Valid options are: None, Viewer, Editor, or Admin. If not specified, the user's current role remains unchanged.")
class UpdateOrgUserRequest(StrictModel):
    """Update a user's role within an organization. Requires the `org.users.role:update` permission with `users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""
    path: UpdateOrgUserRequestPath
    body: UpdateOrgUserRequestBody | None = None

# Operation: remove_organization_user_by_id
class RemoveOrgUserRequestPath(StrictModel):
    org_id: int = Field(default=..., description="The unique identifier of the organization from which the user will be removed. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    user_id: int = Field(default=..., description="The unique identifier of the user to be removed from the organization. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class RemoveOrgUserRequest(StrictModel):
    """Remove a user from the current organization. Requires the `org.users:remove` permission with `users:*` scope in Grafana Enterprise with Fine-grained access control enabled."""
    path: RemoveOrgUserRequestPath

# Operation: get_public_dashboard_access
class ViewPublicDashboardRequestPath(StrictModel):
    access_token: str = Field(default=..., validation_alias="accessToken", serialization_alias="accessToken", description="The unique access token that grants permission to view the public dashboard. This token is provided when a dashboard is shared publicly.")
class ViewPublicDashboardRequest(StrictModel):
    """Retrieve a publicly shared dashboard using its access token. This allows viewing dashboards that have been made publicly available without requiring authentication."""
    path: ViewPublicDashboardRequestPath

# Operation: list_dashboard_annotations
class GetPublicAnnotationsRequestPath(StrictModel):
    access_token: str = Field(default=..., validation_alias="accessToken", serialization_alias="accessToken", description="The unique access token that grants permission to view the public dashboard and its associated annotations.")
class GetPublicAnnotationsRequest(StrictModel):
    """Retrieve all annotations for a public dashboard using its access token. Annotations provide contextual notes and markers associated with dashboard visualizations."""
    path: GetPublicAnnotationsRequestPath

# Operation: query_dashboard_panel
class QueryPublicDashboardRequestPath(StrictModel):
    access_token: str = Field(default=..., validation_alias="accessToken", serialization_alias="accessToken", description="The access token that grants permission to query this public dashboard. This token authenticates your request and determines which dashboard you can access.")
    panel_id: int = Field(default=..., validation_alias="panelId", serialization_alias="panelId", description="The unique identifier of the panel within the dashboard whose data you want to query. This is a numeric ID that specifies which panel's results to retrieve.", json_schema_extra={'format': 'int64'})
class QueryPublicDashboardRequest(StrictModel):
    """Execute a query against a specific panel on a public dashboard and retrieve the results. Use the dashboard's access token and panel identifier to fetch panel data."""
    path: QueryPublicDashboardRequestPath

# Operation: list_queries
class SearchQueriesRequestQuery(StrictModel):
    datasource_uid: list[str] | None = Field(default=None, validation_alias="datasourceUid", serialization_alias="datasourceUid", description="Filter results to include only queries from specific data sources by their unique identifiers.")
    search_string: str | None = Field(default=None, validation_alias="searchString", serialization_alias="searchString", description="Search for queries containing specific text in the query content or associated comments.")
    only_starred: bool | None = Field(default=None, validation_alias="onlyStarred", serialization_alias="onlyStarred", description="When enabled, return only queries that have been marked as starred or favorited.")
    sort: Literal["time-desc", "time-asc"] | None = Field(default=None, description="Order results by timestamp in descending order (newest first) or ascending order (oldest first). Defaults to newest first.")
    limit: int | None = Field(default=None, description="Maximum number of queries to return in a single response. Defaults to 100 if not specified.", json_schema_extra={'format': 'int64'})
class SearchQueriesRequest(StrictModel):
    """Retrieve queries from history filtered by data source, search terms, or starred status. Results are paginated with a default limit of 100 queries per page."""
    query: SearchQueriesRequestQuery | None = None

# Operation: save_query
class CreateQueryRequestBody(StrictModel):
    datasource_uid: str | None = Field(default=None, validation_alias="datasourceUid", serialization_alias="datasourceUid", description="The unique identifier of the data source where queries will be stored. Use the data source UID (e.g., PE1C5CBDA0504A6A3) to target a specific data source.")
    queries: dict[str, Any] = Field(default=..., description="One or more query objects to add to the history. Each query object contains the query details to be persisted.")
class CreateQueryRequest(StrictModel):
    """Save one or more queries to the query history for a specified data source. This allows you to persist and track queries for later retrieval and analysis."""
    body: CreateQueryRequestBody

# Operation: star_query_history
class StarQueryRequestPath(StrictModel):
    query_history_uid: str = Field(default=..., description="The unique identifier of the query history entry to star.")
class StarQueryRequest(StrictModel):
    """Mark a query in your history as starred for quick access and organization. This helps you keep track of frequently used or important queries."""
    path: StarQueryRequestPath

# Operation: remove_query_star
class UnstarQueryRequestPath(StrictModel):
    query_history_uid: str = Field(default=..., description="The unique identifier of the query history entry to unstar.")
class UnstarQueryRequest(StrictModel):
    """Remove a star from a saved query in your query history. This operation unmarks a previously starred query, making it easier to manage your frequently used queries."""
    path: UnstarQueryRequestPath

# Operation: update_query_comment
class PatchQueryCommentRequestPath(StrictModel):
    query_history_uid: str = Field(default=..., description="The unique identifier of the query history record to update.")
class PatchQueryCommentRequestBody(StrictModel):
    comment: str | None = Field(default=None, description="The new comment text to associate with the query. Provide the complete comment as it should appear in the query history.")
class PatchQueryCommentRequest(StrictModel):
    """Updates the comment associated with a specific query in the query history. Use this to add, modify, or replace notes for a previously executed query."""
    path: PatchQueryCommentRequestPath
    body: PatchQueryCommentRequestBody | None = None

# Operation: delete_query_history
class DeleteQueryRequestPath(StrictModel):
    query_history_uid: str = Field(default=..., description="The unique identifier of the query history entry to delete.")
class DeleteQueryRequest(StrictModel):
    """Permanently removes a query from the query history by its unique identifier. This action cannot be undone."""
    path: DeleteQueryRequestPath

# Operation: create_recording_rule
class CreateRecordingRuleRequestBody(StrictModel):
    active: bool | None = Field(default=None, description="Whether the recording rule is enabled and actively collecting metrics upon creation.")
    count: bool | None = Field(default=None, description="Whether to return the count of matching time series instead of the series data itself.")
    description: str | None = Field(default=None, description="A human-readable description of the recording rule's purpose and behavior.")
    dest_data_source_uid: str | None = Field(default=None, description="The unique identifier of the destination data source where recorded metrics will be stored.")
    interval: int | None = Field(default=None, description="The evaluation interval in milliseconds at which the recording rule queries will be executed.", json_schema_extra={'format': 'int64'})
    prom_name: str | None = Field(default=None, description="The name to assign to the recorded metric in the Prometheus data source.")
    queries: list[dict[str, Any]] | None = Field(default=None, description="An array of metric queries to execute for this recording rule. Order matters and determines query execution sequence.")
    range_: int | None = Field(default=None, validation_alias="range", serialization_alias="range", description="The time range in milliseconds over which each query will look back when evaluating the recording rule.", json_schema_extra={'format': 'int64'})
    target_ref_id: str | None = Field(default=None, description="The reference identifier of the target query within the queries array that produces the final recorded metric.")
class CreateRecordingRuleRequest(StrictModel):
    """Create and register a new recording rule that automatically starts collecting metrics according to the specified query and interval configuration."""
    body: CreateRecordingRuleRequestBody | None = None

# Operation: update_recording_rule
class UpdateRecordingRuleRequestBody(StrictModel):
    active: bool | None = Field(default=None, description="Enable or disable the recording rule. When active, the rule will be evaluated according to its schedule; when inactive, evaluations are skipped.")
    count: bool | None = Field(default=None, description="Whether to count results from the recording rule evaluation. When enabled, the rule tracks the number of matching records.")
    description: str | None = Field(default=None, description="A human-readable description of the recording rule's purpose and behavior.")
    dest_data_source_uid: str | None = Field(default=None, description="The unique identifier of the destination data source where recorded metrics will be stored.")
    interval: int | None = Field(default=None, description="The evaluation interval in milliseconds. Defines how frequently the recording rule is executed.", json_schema_extra={'format': 'int64'})
    prom_name: str | None = Field(default=None, description="The Prometheus metric name for the recorded data. This is the name used to reference the recorded metric in queries.")
    queries: list[dict[str, Any]] | None = Field(default=None, description="An array of query objects that define what data to record. Each query specifies the metrics or logs to capture.")
    range_: int | None = Field(default=None, validation_alias="range", serialization_alias="range", description="The time range in milliseconds for each evaluation. Defines the lookback window of data considered during rule execution.", json_schema_extra={'format': 'int64'})
    target_ref_id: str | None = Field(default=None, description="The reference identifier for the target query or panel. Used to link the recording rule to a specific query definition.")
class UpdateRecordingRuleRequest(StrictModel):
    """Update an existing recording rule's configuration, including its active status, query parameters, and data source settings. This operation allows modification of rule behavior such as evaluation interval, range, and target data source."""
    body: UpdateRecordingRuleRequestBody | None = None

# Operation: test_recording_rule
class TestCreateRecordingRuleRequestBody(StrictModel):
    active: bool | None = Field(default=None, description="Whether the recording rule is enabled and should be actively processed.")
    count: bool | None = Field(default=None, description="Whether to return the count of matching results instead of the full dataset.")
    description: str | None = Field(default=None, description="A human-readable description of the recording rule's purpose and behavior.")
    dest_data_source_uid: str | None = Field(default=None, description="The unique identifier of the destination data source where recorded metrics will be stored.")
    interval: int | None = Field(default=None, description="The evaluation interval in milliseconds at which the recording rule will be executed.", json_schema_extra={'format': 'int64'})
    prom_name: str | None = Field(default=None, description="The name of the metric as it will be recorded in the destination data source.")
    queries: list[dict[str, Any]] | None = Field(default=None, description="An array of query objects that define the data to be recorded. Order matters as queries are evaluated sequentially.")
    range_: int | None = Field(default=None, validation_alias="range", serialization_alias="range", description="The time range in milliseconds over which the recording rule will evaluate data during the test.", json_schema_extra={'format': 'int64'})
    target_ref_id: str | None = Field(default=None, description="The reference identifier of the target query or data source to use as the recording source.")
class TestCreateRecordingRuleRequest(StrictModel):
    """Validate a recording rule configuration by testing it against the specified data source and queries. This operation allows you to verify the rule's behavior before applying it to production."""
    body: TestCreateRecordingRuleRequestBody | None = None

# Operation: create_remote_write_target
class CreateRecordingRuleWriteTargetRequestBody(StrictModel):
    data_source_uid: str | None = Field(default=None, description="The unique identifier of the Prometheus data source to associate with this remote write target.")
    remote_write_path: str | None = Field(default=None, description="The endpoint path where Prometheus will send remote write requests for this target.")
class CreateRecordingRuleWriteTargetRequest(StrictModel):
    """Create a remote write target for Prometheus recording rules. Requires an existing Prometheus data source to be configured, otherwise returns a 422 error."""
    body: CreateRecordingRuleWriteTargetRequestBody | None = None

# Operation: delete_recording_rule
class DeleteRecordingRuleRequestPath(StrictModel):
    recording_rule_id: int = Field(default=..., validation_alias="recordingRuleID", serialization_alias="recordingRuleID", description="The unique identifier of the recording rule to delete. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class DeleteRecordingRuleRequest(StrictModel):
    """Permanently delete a recording rule from the registry and stop its execution. The rule will no longer be active after deletion."""
    path: DeleteRecordingRuleRequestPath

# Operation: create_report
class CreateReportRequestBodyOptions(StrictModel):
    layout: str | None = Field(default=None, validation_alias="layout", serialization_alias="layout", description="Page layout for PDF rendering (e.g., portrait, landscape, grid).")
    orientation: str | None = Field(default=None, validation_alias="orientation", serialization_alias="orientation", description="Page orientation for PDF output (portrait or landscape).")
    pdf_combine_one_file: bool | None = Field(default=None, validation_alias="pdfCombineOneFile", serialization_alias="pdfCombineOneFile", description="Combine all PDF pages into a single file instead of separate files per dashboard.")
    pdf_show_template_variables: bool | None = Field(default=None, validation_alias="pdfShowTemplateVariables", serialization_alias="pdfShowTemplateVariables", description="Include template variable definitions and values in the PDF output for reference.")
class CreateReportRequestBodySchedule(StrictModel):
    day_of_month: str | None = Field(default=None, validation_alias="dayOfMonth", serialization_alias="dayOfMonth", description="Day of the month for monthly recurring reports (1-31). Only applicable when frequency is set to monthly.")
    end_date: str | None = Field(default=None, validation_alias="endDate", serialization_alias="endDate", description="End date for the report schedule in ISO 8601 format. Report will stop being generated after this date.", json_schema_extra={'format': 'date-time'})
    frequency: str | None = Field(default=None, validation_alias="frequency", serialization_alias="frequency", description="Frequency of report generation (e.g., once, daily, weekly, monthly, yearly).")
    interval_amount: int | None = Field(default=None, validation_alias="intervalAmount", serialization_alias="intervalAmount", description="Number of intervals between report generations. Used with intervalFrequency to define custom schedules.", json_schema_extra={'format': 'int64'})
    interval_frequency: str | None = Field(default=None, validation_alias="intervalFrequency", serialization_alias="intervalFrequency", description="Time unit for the interval (e.g., hours, days, weeks, months). Defines the period between recurring reports.")
    start_date: str | None = Field(default=None, validation_alias="startDate", serialization_alias="startDate", description="Start date for the report schedule in ISO 8601 format. Report generation begins on this date.", json_schema_extra={'format': 'date-time'})
    time_zone: str | None = Field(default=None, validation_alias="timeZone", serialization_alias="timeZone", description="Time zone for scheduling report generation and delivery (e.g., UTC, America/New_York). Affects when scheduled reports run.")
    workdays_only: bool | None = Field(default=None, validation_alias="workdaysOnly", serialization_alias="workdaysOnly", description="Generate reports only on business days, excluding weekends and holidays.")
class CreateReportRequestBody(StrictModel):
    dashboards: list[ReportDashboard] | None = Field(default=None, description="Array of dashboard IDs to include in the report. Dashboards will be rendered in the order specified.")
    enable_csv: bool | None = Field(default=None, validation_alias="enableCsv", serialization_alias="enableCsv", description="Enable CSV export format for the report output.")
    enable_dashboard_url: bool | None = Field(default=None, validation_alias="enableDashboardUrl", serialization_alias="enableDashboardUrl", description="Include direct URLs to dashboards in the report for easy navigation.")
    formats: list[str] | None = Field(default=None, description="Array of output formats for the report (e.g., PDF, PNG, CSV). Specifies which file formats to generate.")
    message: str | None = Field(default=None, description="Custom message to include in the report body or email delivery.")
    recipients: str | None = Field(default=None, description="Comma-separated list of email addresses to receive the report.")
    reply_to: str | None = Field(default=None, validation_alias="replyTo", serialization_alias="replyTo", description="Reply-to email address for report delivery notifications.")
    scale_factor: int | None = Field(default=None, validation_alias="scaleFactor", serialization_alias="scaleFactor", description="Scale factor for rendering dashboard content in the report. Specified as an integer representing the scaling percentage.", json_schema_extra={'format': 'int64'})
    state: str | None = Field(default=None, description="Current state of the report (e.g., draft, active, paused, archived). Controls whether the report is actively generated.")
    subject: str | None = Field(default=None, description="Subject line for report email delivery.")
    options: CreateReportRequestBodyOptions | None = None
    schedule: CreateReportRequestBodySchedule | None = None
class CreateReportRequest(StrictModel):
    """Create a scheduled or on-demand report with customizable formatting, delivery options, and distribution settings. Requires organization admin privileges and a valid license with the `reports.admin:create` permission."""
    body: CreateReportRequestBody | None = None

# Operation: list_reports_by_dashboard
class GetReportsByDashboardUidRequestPath(StrictModel):
    uid: str = Field(default=..., description="The unique identifier of the dashboard for which to retrieve associated reports.")
class GetReportsByDashboardUidRequest(StrictModel):
    """Retrieve all reports associated with a specific dashboard. Requires org admin privileges and a valid or expired license, with `reports:read` permission."""
    path: GetReportsByDashboardUidRequestPath

# Operation: send_report
class SendReportRequestBody(StrictModel):
    emails: str | None = Field(default=None, description="Comma-separated list of email addresses to receive the report. If not provided, the report will be sent to default recipients based on your organization settings.")
class SendReportRequest(StrictModel):
    """Generate and send a report via email. This operation waits for report generation to complete before returning, so allow at least 60 seconds for the request to finish. Requires Grafana Enterprise v7.0+ with admin privileges and a valid license."""
    body: SendReportRequestBody | None = None

# Operation: retrieve_branding_image
class GetSettingsImageRequestPath(StrictModel):
    image: str = Field(default=..., description="Image filename to retrieve")
class GetSettingsImageRequest(StrictModel):
    """Retrieve a custom branding report image for your organization. Requires admin access and a valid or expired license."""
    path: GetSettingsImageRequestPath

# Operation: download_csv_report
class RenderReportCsVsRequestQuery(StrictModel):
    dashboards: str | None = Field(default=None, description="Comma-separated list of dashboard identifiers to include in the report. If omitted, the report includes all available dashboards.")
    title: str | None = Field(default=None, description="Custom title for the generated CSV report. If omitted, a default title is used.")
class RenderReportCsVsRequest(StrictModel):
    """Download a CSV-formatted report. Available to all users with a valid license."""
    query: RenderReportCsVsRequestQuery | None = None

# Operation: render_report_pdfs
class RenderReportPdFsRequestQuery(StrictModel):
    dashboards: str | None = Field(default=None, description="Comma-separated list of dashboard identifiers to include in the report. Specifies which dashboards will be rendered into the PDF output.")
    orientation: str | None = Field(default=None, description="Page orientation for the PDF output. Controls whether the report renders in portrait or landscape format.")
    layout: str | None = Field(default=None, description="Layout configuration for dashboard arrangement. Determines how multiple dashboards are positioned and sized within the PDF pages.")
    title: str | None = Field(default=None, description="Custom title text to display at the top of the generated PDF report.")
    scale_factor: str | None = Field(default=None, validation_alias="scaleFactor", serialization_alias="scaleFactor", description="Scaling factor to adjust the size of rendered content. Controls zoom level of dashboards in the final PDF output.")
    include_tables: str | None = Field(default=None, validation_alias="includeTables", serialization_alias="includeTables", description="Flag to include or exclude data tables associated with the dashboards in the PDF report.")
class RenderReportPdFsRequest(StrictModel):
    """Generate a PDF report rendering multiple dashboards with customizable layout, orientation, and styling options. Available to all licensed users."""
    query: RenderReportPdFsRequestQuery | None = None

# Operation: send_test_report_email
class SendTestEmailRequestBodyOptions(StrictModel):
    layout: str | None = Field(default=None, validation_alias="layout", serialization_alias="layout", description="Page layout for rendered reports (e.g., portrait, landscape).")
    orientation: str | None = Field(default=None, validation_alias="orientation", serialization_alias="orientation", description="Page orientation for PDF output (portrait or landscape).")
    pdf_combine_one_file: bool | None = Field(default=None, validation_alias="pdfCombineOneFile", serialization_alias="pdfCombineOneFile", description="Combine multiple pages into a single PDF file.")
    pdf_show_template_variables: bool | None = Field(default=None, validation_alias="pdfShowTemplateVariables", serialization_alias="pdfShowTemplateVariables", description="Include template variable definitions in the PDF output.")
class SendTestEmailRequestBodySchedule(StrictModel):
    day_of_month: str | None = Field(default=None, validation_alias="dayOfMonth", serialization_alias="dayOfMonth", description="Day of month for recurring reports (1-31).")
    end_date: str | None = Field(default=None, validation_alias="endDate", serialization_alias="endDate", description="End date for the report schedule in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    frequency: str | None = Field(default=None, validation_alias="frequency", serialization_alias="frequency", description="Frequency of report delivery (e.g., daily, weekly, monthly).")
    interval_amount: int | None = Field(default=None, validation_alias="intervalAmount", serialization_alias="intervalAmount", description="Number of intervals between report deliveries.", json_schema_extra={'format': 'int64'})
    interval_frequency: str | None = Field(default=None, validation_alias="intervalFrequency", serialization_alias="intervalFrequency", description="Unit of time for the interval (e.g., days, weeks, months).")
    start_date: str | None = Field(default=None, validation_alias="startDate", serialization_alias="startDate", description="Start date for the report schedule in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    time_zone: str | None = Field(default=None, validation_alias="timeZone", serialization_alias="timeZone", description="Timezone for scheduling report delivery (e.g., UTC, America/New_York).")
    workdays_only: bool | None = Field(default=None, validation_alias="workdaysOnly", serialization_alias="workdaysOnly", description="Deliver reports only on business days (Monday-Friday).")
class SendTestEmailRequestBody(StrictModel):
    dashboards: list[ReportDashboard] | None = Field(default=None, description="List of dashboard IDs to include in the report.")
    enable_csv: bool | None = Field(default=None, validation_alias="enableCsv", serialization_alias="enableCsv", description="Include CSV format export in the email.")
    enable_dashboard_url: bool | None = Field(default=None, validation_alias="enableDashboardUrl", serialization_alias="enableDashboardUrl", description="Include a direct URL link to the dashboard in the email.")
    formats: list[str] | None = Field(default=None, description="Array of output formats for the report (e.g., PDF, PNG, CSV).")
    message: str | None = Field(default=None, description="Custom message body to include in the email.")
    recipients: str | None = Field(default=None, description="Email address or comma-separated list of recipient email addresses.")
    reply_to: str | None = Field(default=None, validation_alias="replyTo", serialization_alias="replyTo", description="Reply-to email address for responses.")
    scale_factor: int | None = Field(default=None, validation_alias="scaleFactor", serialization_alias="scaleFactor", description="Scale factor for rendering, specified as an integer value.", json_schema_extra={'format': 'int64'})
    state: str | None = Field(default=None, description="Current state of the report schedule (e.g., active, paused, draft).")
    subject: str | None = Field(default=None, description="Email subject line for the report.")
    options: SendTestEmailRequestBodyOptions | None = None
    schedule: SendTestEmailRequestBodySchedule | None = None
class SendTestEmailRequest(StrictModel):
    """Send a test report via email to verify configuration before scheduling. Requires organization admin privileges and a valid license with the `reports:send` permission."""
    body: SendTestEmailRequestBody | None = None

# Operation: search_dashboards
class SearchRequestQuery(StrictModel):
    tag: list[str] | None = Field(default=None, description="Filter results by one or more tags. Only dashboards matching all specified tags will be returned.")
    dashboard_ui_ds: list[str] | None = Field(default=None, validation_alias="dashboardUIDs", serialization_alias="dashboardUIDs", description="Filter results to specific dashboards by their unique identifiers (UIDs).")
    folder_ui_ds: list[str] | None = Field(default=None, validation_alias="folderUIDs", serialization_alias="folderUIDs", description="Limit search scope to dashboards within specific folders by their UIDs. Use an empty string to search only top-level folders.")
    starred: bool | None = Field(default=None, description="When enabled, return only dashboards that have been marked as starred by the user.")
    limit: int | None = Field(default=None, description="Maximum number of results to return, up to 5000 results per request.", json_schema_extra={'format': 'int64'})
    permission: Literal["Edit", "View"] | None = Field(default=None, description="Filter by user permissions: 'View' returns dashboards the user can view, 'Edit' returns only dashboards the user can edit. Defaults to 'View'.")
    sort: Literal["alpha-asc", "alpha-desc"] | None = Field(default=None, description="Sort results by dashboard name in ascending or descending alphabetical order. Defaults to ascending alphabetical order.")
    deleted: bool | None = Field(default=None, description="When enabled, return only dashboards that have been soft deleted (not permanently removed).")
class SearchRequest(StrictModel):
    """Search for dashboards and folders by tags, UIDs, starred status, and other criteria. Returns matching dashboards with optional filtering by permissions and deletion status."""
    query: SearchRequestQuery | None = None

# Operation: create_service_account
class CreateServiceAccountRequestBody(StrictModel):
    is_disabled: bool | None = Field(default=None, validation_alias="isDisabled", serialization_alias="isDisabled", description="Whether the service account should be created in a disabled state. Defaults to false (enabled).")
    role: Literal["None", "Viewer", "Editor", "Admin"] | None = Field(default=None, description="The role to assign to the service account. Must be one of: None, Viewer, Editor, or Admin. Defaults to None if not specified.")
    name: str | None = None
class CreateServiceAccountRequest(StrictModel):
    """Create a new service account in Grafana for programmatic access. Requires Grafana Admin privileges and basic authentication."""
    body: CreateServiceAccountRequestBody | None = None

# Operation: list_service_accounts
class SearchOrgServiceAccountsWithPagingRequestQuery(StrictModel):
    disabled: bool | None = Field(default=None, validation_alias="Disabled", serialization_alias="Disabled", description="Filter to include only disabled service accounts when set to true, or only active accounts when false.")
    expired_tokens: bool | None = Field(default=None, validation_alias="expiredTokens", serialization_alias="expiredTokens", description="Filter to include only service accounts with expired tokens when set to true.")
    perpage: int | None = Field(default=None, description="Number of service accounts to return per page. Defaults to 1000 if not specified.", json_schema_extra={'format': 'int64'})
class SearchOrgServiceAccountsWithPagingRequest(StrictModel):
    """Search and retrieve service accounts with pagination support. Requires `serviceaccounts:read` permission with `serviceaccounts:*` scope."""
    query: SearchOrgServiceAccountsWithPagingRequestQuery | None = None

# Operation: get_service_account
class RetrieveServiceAccountRequestPath(StrictModel):
    service_account_id: int = Field(default=..., validation_alias="serviceAccountId", serialization_alias="serviceAccountId", description="The unique identifier of the service account to retrieve. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class RetrieveServiceAccountRequest(StrictModel):
    """Retrieve a specific service account by its ID. Requires serviceaccounts:read permission with scope limited to the requested service account."""
    path: RetrieveServiceAccountRequestPath

# Operation: update_service_account
class UpdateServiceAccountRequestPath(StrictModel):
    service_account_id: int = Field(default=..., validation_alias="serviceAccountId", serialization_alias="serviceAccountId", description="The unique identifier of the service account to update. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class UpdateServiceAccountRequestBody(StrictModel):
    is_disabled: bool | None = Field(default=None, validation_alias="isDisabled", serialization_alias="isDisabled", description="Whether the service account is disabled. Set to true to deactivate the account or false to enable it.")
    role: Literal["None", "Viewer", "Editor", "Admin"] | None = Field(default=None, description="The role to assign to the service account. Must be one of: None, Viewer, Editor, or Admin.")
class UpdateServiceAccountRequest(StrictModel):
    """Modify an existing service account's configuration, including its enabled status and role assignment. Requires serviceaccounts:write permission for the specific service account."""
    path: UpdateServiceAccountRequestPath
    body: UpdateServiceAccountRequestBody | None = None

# Operation: delete_service_account
class DeleteServiceAccountRequestPath(StrictModel):
    service_account_id: int = Field(default=..., validation_alias="serviceAccountId", serialization_alias="serviceAccountId", description="The unique identifier of the service account to delete. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class DeleteServiceAccountRequest(StrictModel):
    """Permanently delete a service account by its ID. Requires serviceaccounts:delete permission and serviceaccounts:id:{serviceAccountId} scope."""
    path: DeleteServiceAccountRequestPath

# Operation: list_service_account_tokens
class ListTokensRequestPath(StrictModel):
    service_account_id: int = Field(default=..., validation_alias="serviceAccountId", serialization_alias="serviceAccountId", description="The unique identifier of the service account. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class ListTokensRequest(StrictModel):
    """Retrieve all API tokens associated with a specific service account. Requires Grafana Admin privileges and the serviceaccounts:read permission for the target service account."""
    path: ListTokensRequestPath

# Operation: create_service_account_token
class CreateTokenRequestPath(StrictModel):
    service_account_id: int = Field(default=..., validation_alias="serviceAccountId", serialization_alias="serviceAccountId", description="The unique identifier of the service account for which to create the token. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class CreateTokenRequestBody(StrictModel):
    seconds_to_live: int | None = Field(default=None, validation_alias="secondsToLive", serialization_alias="secondsToLive", description="Optional token lifetime in seconds. If specified, the token will automatically expire after this duration. If omitted, the token will not expire.", json_schema_extra={'format': 'int64'})
    name: str | None = None
class CreateTokenRequest(StrictModel):
    """Generate a new authentication token for a service account. The token can be configured with an optional expiration time in seconds."""
    path: CreateTokenRequestPath
    body: CreateTokenRequestBody | None = None

# Operation: revoke_service_account_token
class DeleteTokenRequestPath(StrictModel):
    token_id: int = Field(default=..., validation_alias="tokenId", serialization_alias="tokenId", description="The unique identifier of the service account token to revoke. Must be a positive integer.", json_schema_extra={'format': 'int64'})
    service_account_id: int = Field(default=..., validation_alias="serviceAccountId", serialization_alias="serviceAccountId", description="The unique identifier of the service account that owns the token. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class DeleteTokenRequest(StrictModel):
    """Revoke and delete a specific token for a service account. Requires Grafana Admin privileges and the serviceaccounts:write permission for the target service account."""
    path: DeleteTokenRequestPath

# Operation: create_snapshot
class CreateDashboardSnapshotRequestBody(StrictModel):
    delete_key: str | None = Field(default=None, validation_alias="deleteKey", serialization_alias="deleteKey", description="A unique key that grants deletion permissions for this snapshot. Required when storing the snapshot externally. Only the snapshot creator should have access to this key.")
    expires: int | None = Field(default=None, description="The number of seconds before the snapshot automatically expires and becomes unavailable. Omit or set to 0 to keep the snapshot indefinitely.", json_schema_extra={'format': 'int64'})
    external: bool | None = Field(default=None, description="When enabled, stores the snapshot on an external server instead of locally. Requires both `key` and `deleteKey` to be provided.")
    key: str | None = Field(default=None, description="A unique identifier for this snapshot. Required when storing the snapshot externally. Used to reference and retrieve the snapshot.")
    dashboard: dict[str, Any] = Field(default=..., description="The complete dashboard model object to snapshot.")
class CreateDashboardSnapshotRequest(StrictModel):
    """Create a snapshot of a dashboard for sharing or archival. Requires either public snapshot mode to be enabled or valid authentication credentials."""
    body: CreateDashboardSnapshotRequestBody

# Operation: delete_snapshot_by_delete_key
class DeleteDashboardSnapshotByDeleteKeyRequestPath(StrictModel):
    delete_key: str = Field(default=..., validation_alias="deleteKey", serialization_alias="deleteKey", description="The unique delete key that identifies the snapshot to be deleted. This key is typically provided when the snapshot is created or shared.")
class DeleteDashboardSnapshotByDeleteKeyRequest(StrictModel):
    """Delete a snapshot using its unique delete key. Requires either public snapshot mode to be enabled or valid authentication credentials."""
    path: DeleteDashboardSnapshotByDeleteKeyRequestPath

# Operation: get_snapshot_by_key
class GetDashboardSnapshotRequestPath(StrictModel):
    key: str = Field(default=..., description="The unique identifier of the snapshot to retrieve.")
class GetDashboardSnapshotRequest(StrictModel):
    """Retrieve a dashboard snapshot by its unique identifier. Returns the snapshot data associated with the provided key."""
    path: GetDashboardSnapshotRequestPath

# Operation: delete_snapshot
class DeleteDashboardSnapshotRequestPath(StrictModel):
    key: str = Field(default=..., description="The unique identifier of the snapshot to delete.")
class DeleteDashboardSnapshotRequest(StrictModel):
    """Permanently delete a dashboard snapshot by its unique key. This action cannot be undone."""
    path: DeleteDashboardSnapshotRequestPath

# Operation: create_team
class CreateTeamRequestBody(StrictModel):
    email: str | None = Field(default=None, description="Email address associated with the team for contact and notifications purposes.")
    name: str = Field(default=..., description="The name of the team. This is a required identifier used to distinguish the team from others.")
class CreateTeamRequest(StrictModel):
    """Create a new team with a required name and optional email contact. This establishes a new team entity that can be used to organize users and resources."""
    body: CreateTeamRequestBody

# Operation: list_teams
class SearchTeamsRequestQuery(StrictModel):
    perpage: int | None = Field(default=None, description="Number of teams to return per page for pagination. Defaults to 1000 items per page. Use this with totalCount from the response to navigate through all results.", json_schema_extra={'format': 'int64'})
    sort: str | None = Field(default=None, description="Field to sort results by. Specify the team attribute name to order the returned teams.")
class SearchTeamsRequest(StrictModel):
    """Search and retrieve teams with pagination support. Use the totalCount field in the response to determine the number of pages available."""
    query: SearchTeamsRequestQuery | None = None

# Operation: list_team_groups
class GetTeamGroupsApiRequestPath(StrictModel):
    team_id: str = Field(default=..., validation_alias="teamId", serialization_alias="teamId", description="The unique identifier of the team for which to retrieve associated external groups.")
class GetTeamGroupsApiRequest(StrictModel):
    """Retrieve all external groups associated with a specific team. This returns a list of groups that have been configured for the team."""
    path: GetTeamGroupsApiRequestPath

# Operation: add_group_to_team
class AddTeamGroupApiRequestPath(StrictModel):
    team_id: str = Field(default=..., validation_alias="teamId", serialization_alias="teamId", description="The unique identifier of the team to which the group will be added.")
class AddTeamGroupApiRequestBody(StrictModel):
    group_id: str | None = Field(default=None, validation_alias="groupId", serialization_alias="groupId", description="The unique identifier of the external group to add to the team.")
class AddTeamGroupApiRequest(StrictModel):
    """Add an external group to a team, enabling group-level access and collaboration within the team."""
    path: AddTeamGroupApiRequestPath
    body: AddTeamGroupApiRequestBody | None = None

# Operation: remove_team_group
class RemoveTeamGroupApiQueryRequestPath(StrictModel):
    team_id: str = Field(default=..., validation_alias="teamId", serialization_alias="teamId", description="The unique identifier of the team from which the group will be removed.")
class RemoveTeamGroupApiQueryRequestQuery(StrictModel):
    group_id: str | None = Field(default=None, validation_alias="groupId", serialization_alias="groupId", description="The unique identifier of the external group to remove from the team.")
class RemoveTeamGroupApiQueryRequest(StrictModel):
    """Remove an external group from a team. This operation deletes the association between a specific group and the team."""
    path: RemoveTeamGroupApiQueryRequestPath
    query: RemoveTeamGroupApiQueryRequestQuery | None = None

# Operation: search_groups
class SearchTeamGroupsRequestPath(StrictModel):
    team_id: int = Field(default=..., validation_alias="teamId", serialization_alias="teamId", description="The unique identifier of the team to search groups within. Required to scope the search to a specific team.", json_schema_extra={'format': 'int64'})
class SearchTeamGroupsRequestQuery(StrictModel):
    perpage: int | None = Field(default=None, description="Maximum number of results to return per page. Defaults to 1000 items if not specified.", json_schema_extra={'format': 'int64'})
class SearchTeamGroupsRequest(StrictModel):
    """Search for groups within a team with optional filtering and pagination support. Returns matching groups based on search criteria with configurable result limits."""
    path: SearchTeamGroupsRequestPath
    query: SearchTeamGroupsRequestQuery | None = None

# Operation: get_team
class GetTeamByIdRequestPath(StrictModel):
    team_id: str = Field(default=..., description="The unique identifier of the team to retrieve.")
class GetTeamByIdRequest(StrictModel):
    """Retrieve a specific team by its unique identifier. Returns the team's details including name, members, and configuration."""
    path: GetTeamByIdRequestPath

# Operation: update_team
class UpdateTeamRequestPath(StrictModel):
    team_id: str = Field(default=..., description="The unique identifier of the team to update.")
class UpdateTeamRequestBody(StrictModel):
    email: str | None = Field(default=None, description="The email address to associate with the team.")
class UpdateTeamRequest(StrictModel):
    """Update an existing team's information, such as the associated email address. Provide the team ID and any fields you want to modify."""
    path: UpdateTeamRequestPath
    body: UpdateTeamRequestBody | None = None

# Operation: delete_team
class DeleteTeamByIdRequestPath(StrictModel):
    team_id: str = Field(default=..., description="The unique identifier of the team to delete.")
class DeleteTeamByIdRequest(StrictModel):
    """Permanently delete a team by its ID. This action removes the team and all associated data."""
    path: DeleteTeamByIdRequestPath

# Operation: list_team_members
class GetTeamMembersRequestPath(StrictModel):
    team_id: str = Field(default=..., description="The unique identifier of the team whose members you want to retrieve.")
class GetTeamMembersRequest(StrictModel):
    """Retrieve all members belonging to a specific team. Returns a list of team members with their associated details and roles."""
    path: GetTeamMembersRequestPath

# Operation: add_team_member
class AddTeamMemberRequestPath(StrictModel):
    team_id: str = Field(default=..., description="The unique identifier of the team to which the member will be added.")
class AddTeamMemberRequestBody(StrictModel):
    user_id: int = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The unique identifier of the user to add to the team, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class AddTeamMemberRequest(StrictModel):
    """Add a user to a team by their user ID. The user will gain access to the team's resources and collaboration features."""
    path: AddTeamMemberRequestPath
    body: AddTeamMemberRequestBody

# Operation: update_team_members
class SetTeamMembershipsRequestPath(StrictModel):
    team_id: str = Field(default=..., description="The unique identifier of the team to update.")
class SetTeamMembershipsRequestBody(StrictModel):
    admins: list[str] | None = Field(default=None, description="List of user email addresses to set as team admins. Users should be specified by their email addresses. Omit or provide an empty list to remove all admins.")
    members: list[str] | None = Field(default=None, description="List of user email addresses to set as team members. Users should be specified by their email addresses. Omit or provide an empty list to remove all members.")
class SetTeamMembershipsRequest(StrictModel):
    """Update team membership by replacing the current members and admins with the provided lists. Any existing members or admins not included in the new lists will be removed from the team."""
    path: SetTeamMembershipsRequestPath
    body: SetTeamMembershipsRequestBody | None = None

# Operation: update_team_member
class UpdateTeamMemberRequestPath(StrictModel):
    team_id: str = Field(default=..., description="The unique identifier of the team containing the member to be updated.")
    user_id: int = Field(default=..., description="The unique identifier of the user whose team membership and permissions should be updated. This is a 64-bit integer value.", json_schema_extra={'format': 'int64'})
class UpdateTeamMemberRequestBody(StrictModel):
    permission: int | None = Field(default=None, description="The permission level to assign to the team member, specified as a 64-bit integer. This determines the member's access rights and capabilities within the team.", json_schema_extra={'format': 'int64'})
class UpdateTeamMemberRequest(StrictModel):
    """Update a team member's information and permissions within a specific team. Modify the member's role or access level by specifying their permission level."""
    path: UpdateTeamMemberRequestPath
    body: UpdateTeamMemberRequestBody | None = None

# Operation: remove_team_member
class RemoveTeamMemberRequestPath(StrictModel):
    team_id: str = Field(default=..., description="The unique identifier of the team from which the member will be removed.")
    user_id: int = Field(default=..., description="The unique identifier of the user to be removed from the team. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class RemoveTeamMemberRequest(StrictModel):
    """Remove a user from a team, revoking their access and team membership. The user will no longer have permissions to view or interact with team resources."""
    path: RemoveTeamMemberRequestPath

# Operation: get_team_preferences
class GetTeamPreferencesRequestPath(StrictModel):
    team_id: str = Field(default=..., description="The unique identifier of the team whose preferences you want to retrieve.")
class GetTeamPreferencesRequest(StrictModel):
    """Retrieve the preferences and settings configured for a specific team, including notification defaults, display options, and other team-level configurations."""
    path: GetTeamPreferencesRequestPath

# Operation: update_user_profile
class UpdateSignedInUserRequestBody(StrictModel):
    """To change the email, name, login, theme, provide another one."""
    email: str | None = Field(default=None, description="The new email address for the user account. Must be a valid email format.")
    login: str | None = Field(default=None, description="The new login username for the user account. Used for authentication and account identification.")
    theme: str | None = Field(default=None, description="The preferred display theme for the user interface (e.g., light, dark, auto).")
class UpdateSignedInUserRequest(StrictModel):
    """Update the profile information for the currently signed-in user, including email address, login username, and display theme preference."""
    body: UpdateSignedInUserRequestBody | None = None

# Operation: enable_help_flag
class SetHelpFlagRequestPath(StrictModel):
    flag_id: str = Field(default=..., description="The unique identifier of the help flag to enable.")
class SetHelpFlagRequest(StrictModel):
    """Enable a specific help flag for the user to control which help features or guidance are displayed."""
    path: SetHelpFlagRequestPath

# Operation: update_user_preferences_partial
class PatchUserPreferencesRequestBody(StrictModel):
    home_dashboard_uid: str | None = Field(default=None, validation_alias="homeDashboardUID", serialization_alias="homeDashboardUID", description="The unique identifier of the dashboard to set as the user's home dashboard.")
    language: str | None = Field(default=None, description="The user's preferred language for the interface.")
    regional_format: str | None = Field(default=None, validation_alias="regionalFormat", serialization_alias="regionalFormat", description="The user's preferred regional format for displaying dates, numbers, and currency.")
    theme: Literal["light", "dark"] | None = Field(default=None, description="The user's preferred color theme. Choose between light mode or dark mode.")
    timezone_: str | None = Field(default=None, validation_alias="timezone", serialization_alias="timezone", description="The user's timezone for displaying times and scheduling. Accepts any IANA timezone identifier (e.g., America/New_York), 'utc' for UTC, 'browser' to use the browser's timezone, or an empty string for no preference.")
    week_start: str | None = Field(default=None, validation_alias="weekStart", serialization_alias="weekStart", description="The day of the week to display as the first day in calendar views.")
class PatchUserPreferencesRequest(StrictModel):
    """Update user preferences for dashboard, display, and localization settings. Allows customization of theme, timezone, language, and other UI preferences."""
    body: PatchUserPreferencesRequestBody | None = None

# Operation: star_dashboard
class StarDashboardByUidRequestPath(StrictModel):
    dashboard_uid: str = Field(default=..., description="The unique identifier of the dashboard to star.")
class StarDashboardByUidRequest(StrictModel):
    """Add a dashboard to the current user's starred dashboards. Starred dashboards appear in the user's favorites for quick access."""
    path: StarDashboardByUidRequestPath

# Operation: remove_dashboard_star
class UnstarDashboardByUidRequestPath(StrictModel):
    dashboard_uid: str = Field(default=..., description="The unique identifier of the dashboard to unstar. This is the dashboard's UID that was previously starred by the user.")
class UnstarDashboardByUidRequest(StrictModel):
    """Remove a dashboard from the current user's starred list. This action deletes the star marking for the specified dashboard."""
    path: UnstarDashboardByUidRequestPath

# Operation: switch_organization
class UserSetUsingOrgRequestPath(StrictModel):
    org_id: int = Field(default=..., description="The unique identifier of the organization to switch to. Must be a valid 64-bit integer representing an existing organization the user has access to.", json_schema_extra={'format': 'int64'})
class UserSetUsingOrgRequest(StrictModel):
    """Switch the authenticated user's active organization context to the specified organization. This changes which organization's data and resources the user will access in subsequent operations."""
    path: UserSetUsingOrgRequestPath

# Operation: list_users
class SearchUsersRequestQuery(StrictModel):
    perpage: int | None = Field(default=None, description="Maximum number of users to return per page. Defaults to 1000 if not specified.", json_schema_extra={'format': 'int64'})
class SearchUsersRequest(StrictModel):
    """Retrieve all users that the authenticated user has permission to view. Requires admin permission to access this operation."""
    query: SearchUsersRequestQuery | None = None

# Operation: lookup_user
class GetUserByLoginOrEmailRequestQuery(StrictModel):
    login_or_email: str = Field(default=..., validation_alias="loginOrEmail", serialization_alias="loginOrEmail", description="The user's login name or email address to search for. Accepts either format to locate the user account.")
class GetUserByLoginOrEmailRequest(StrictModel):
    """Retrieve a user account by their login name or email address. Use this to find user details when you have either identifier available."""
    query: GetUserByLoginOrEmailRequestQuery

# Operation: get_user
class GetUserByIdRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user to retrieve, specified as a 64-bit integer.", json_schema_extra={'format': 'int64'})
class GetUserByIdRequest(StrictModel):
    """Retrieve a specific user by their unique identifier. Returns the user's profile information and details."""
    path: GetUserByIdRequestPath

# Operation: update_user
class UpdateUserRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user to update. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class UpdateUserRequestBody(StrictModel):
    """To change the email, name, login, theme, provide another one."""
    email: str | None = Field(default=None, description="The user's email address. Optional field for updating contact information.")
    login: str | None = Field(default=None, description="The user's login username or identifier. Optional field for updating authentication credentials.")
    theme: str | None = Field(default=None, description="The user's preferred display theme or UI preference. Optional field for customizing the user experience.")
class UpdateUserRequest(StrictModel):
    """Update user account details including email, login credentials, and display preferences. Modifies the user record identified by the provided user ID."""
    path: UpdateUserRequestPath
    body: UpdateUserRequestBody | None = None

# Operation: list_user_organizations_by_id
class GetUserOrgListRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user. Must be a positive integer value.", json_schema_extra={'format': 'int64'})
class GetUserOrgListRequest(StrictModel):
    """Retrieve all organizations associated with a specific user. Returns a list of organizations where the user is a member or has access."""
    path: GetUserOrgListRequestPath

# Operation: list_user_teams_by_id
class GetUserTeamsRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class GetUserTeamsRequest(StrictModel):
    """Retrieve all teams that a user is a member of. Returns a list of teams associated with the specified user."""
    path: GetUserTeamsRequestPath

# Operation: export_alert_rules
class RouteGetAlertRulesExportRequestQuery(StrictModel):
    format_: Literal["yaml", "json", "hcl"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="File format for the exported rules. Choose from YAML, JSON, or HCL. Defaults to YAML if not specified. The query parameter takes precedence over the Accept header.")
    folder_uid: list[str] | None = Field(default=None, validation_alias="folderUid", serialization_alias="folderUid", description="Filter export to specific folders by their UIDs. Provide one or more folder UIDs to limit the rules exported to those folders only.")
    group: str | None = Field(default=None, description="Filter export to a specific rule group by name. Can only be used together with a single folder UID. Ignored if multiple folders or no folder is specified.")
    rule_uid: str | None = Field(default=None, validation_alias="ruleUid", serialization_alias="ruleUid", description="Export a single alert rule by its UID. When specified, folderUid and group parameters must be empty. Takes precedence over folder and group filters.")
class RouteGetAlertRulesExportRequest(StrictModel):
    """Export all alert rules or a filtered subset in provisioning file format (YAML, JSON, or HCL). Useful for backing up, version controlling, or migrating alert rule configurations."""
    query: RouteGetAlertRulesExportRequestQuery | None = None

# Operation: export_alert_rule
class RouteGetAlertRuleExportRequestPath(StrictModel):
    uid: str = Field(default=..., validation_alias="UID", serialization_alias="UID", description="The unique identifier of the alert rule to export.")
class RouteGetAlertRuleExportRequestQuery(StrictModel):
    format_: Literal["yaml", "json", "hcl"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="The file format for the exported alert rule. Choose from YAML, JSON, or HCL. Defaults to YAML if not specified.")
class RouteGetAlertRuleExportRequest(StrictModel):
    """Export an alert rule in provisioning file format (YAML, JSON, or HCL) for use in infrastructure-as-code workflows."""
    path: RouteGetAlertRuleExportRequestPath
    query: RouteGetAlertRuleExportRequestQuery | None = None

# Operation: create_contact_point
class RoutePostContactpointsRequestBody(StrictModel):
    disable_resolve_message: bool | None = Field(default=None, validation_alias="disableResolveMessage", serialization_alias="disableResolveMessage", description="Whether to disable the resolve message when alerts are resolved. Defaults to false, meaning resolve messages are sent.")
    settings: dict[str, Any] = Field(default=..., description="Configuration settings for the contact point. The structure and required fields depend on the selected type (e.g., webhook URL, email address, API credentials).")
    type_: Literal["alertmanager", "dingding", "discord", "email", "googlechat", "kafka", "line", "opsgenie", "pagerduty", "pushover", "sensugo", "slack", "teams", "telegram", "threema", "victorops", "webhook", "wecom"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of contact point to create. Choose from supported integrations including alertmanager, dingding, discord, email, googlechat, kafka, line, opsgenie, pagerduty, pushover, sensugo, slack, teams, telegram, threema, victorops, webhook, or wecom.")
    name: str | None = Field(default=None, description="Name is used as grouping key in the UI. Contact points with the same name will be grouped in the UI.")
class RoutePostContactpointsRequest(StrictModel):
    """Create a new contact point for alert notifications. Specify the contact point type and configure its settings to enable routing of alerts to external services."""
    body: RoutePostContactpointsRequestBody

# Operation: export_contact_points
class RouteGetContactpointsExportRequestQuery(StrictModel):
    format_: Literal["yaml", "json", "hcl"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="File format for the exported contact points. Choose from YAML, JSON, or HCL. Defaults to YAML if not specified.")
    decrypt: bool | None = Field(default=None, description="Whether to decrypt sensitive settings in the export. When false (default), secure settings are redacted. Only org admins can view decrypted values.")
class RouteGetContactpointsExportRequest(StrictModel):
    """Export all provisioned contact points in your preferred format (YAML, JSON, or HCL). Optionally decrypt secure settings if you have org admin permissions."""
    query: RouteGetContactpointsExportRequestQuery | None = None

# Operation: update_contact_point
class RoutePutContactpointRequestPath(StrictModel):
    uid: str = Field(default=..., validation_alias="UID", serialization_alias="UID", description="The unique identifier of the contact point to update.")
class RoutePutContactpointRequestBody(StrictModel):
    disable_resolve_message: bool | None = Field(default=None, validation_alias="disableResolveMessage", serialization_alias="disableResolveMessage", description="Whether to disable message resolution notifications. Defaults to false, meaning resolution messages are sent by default.")
    settings: dict[str, Any] = Field(default=..., description="Configuration settings specific to the contact point type. Structure and required fields vary based on the notification channel type selected.")
    type_: Literal["alertmanager", "dingding", "discord", "email", "googlechat", "kafka", "line", "opsgenie", "pagerduty", "pushover", "sensugo", "slack", "teams", "telegram", "threema", "victorops", "webhook", "wecom"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The notification channel type for this contact point. Supported types include webhook, email, Slack, PagerDuty, Telegram, Discord, and other integration platforms.")
class RoutePutContactpointRequest(StrictModel):
    """Update an existing contact point configuration with new settings and notification type. Allows modification of contact point details such as notification channel type and delivery preferences."""
    path: RoutePutContactpointRequestPath
    body: RoutePutContactpointRequestBody

# Operation: delete_contact_point
class RouteDeleteContactpointsRequestPath(StrictModel):
    uid: str = Field(default=..., validation_alias="UID", serialization_alias="UID", description="The unique identifier of the contact point to delete.")
class RouteDeleteContactpointsRequest(StrictModel):
    """Permanently delete a contact point by its unique identifier. This action cannot be undone."""
    path: RouteDeleteContactpointsRequestPath

# Operation: export_alert_rule_group
class RouteGetAlertRuleGroupExportRequestPath(StrictModel):
    folder_uid: str = Field(default=..., validation_alias="FolderUID", serialization_alias="FolderUID", description="The unique identifier of the folder containing the alert rule group to export.")
    group: str = Field(default=..., validation_alias="Group", serialization_alias="Group", description="The name or identifier of the alert rule group to export.")
class RouteGetAlertRuleGroupExportRequestQuery(StrictModel):
    format_: Literal["yaml", "json", "hcl"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="The file format for the exported provisioning file. Supports YAML, JSON, or HCL formats. Defaults to YAML if not specified.")
class RouteGetAlertRuleGroupExportRequest(StrictModel):
    """Export an alert rule group in provisioning file format (YAML, JSON, or HCL) for backup, version control, or migration purposes."""
    path: RouteGetAlertRuleGroupExportRequestPath
    query: RouteGetAlertRuleGroupExportRequestQuery | None = None

# Operation: export_mute_timings
class RouteExportMuteTimingsRequestQuery(StrictModel):
    format_: Literal["yaml", "json", "hcl"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="File format for the exported mute timings. Choose from YAML, JSON, or HCL formats. Defaults to YAML if not specified.")
class RouteExportMuteTimingsRequest(StrictModel):
    """Export all configured mute timings in provisioning format. Returns mute timing definitions that can be used for infrastructure-as-code deployment."""
    query: RouteExportMuteTimingsRequestQuery | None = None

# Operation: get_mute_timing
class RouteGetMuteTimingRequestPath(StrictModel):
    name: str = Field(default=..., description="The unique identifier of the mute timing to retrieve.")
class RouteGetMuteTimingRequest(StrictModel):
    """Retrieve a specific mute timing configuration by name. Mute timings define periods when alerts and notifications are suppressed."""
    path: RouteGetMuteTimingRequestPath

# Operation: update_mute_timing
class RoutePutMuteTimingRequestPath(StrictModel):
    name: str = Field(default=..., description="The unique identifier of the mute timing to replace. Must match an existing mute timing name in the system.")
class RoutePutMuteTimingRequestBody(StrictModel):
    time_intervals: list[TimeInterval] | None = Field(default=None, description="Array of time intervals during which alerts should be muted. Each interval defines a period when muting is active. The order of intervals may affect evaluation logic.")
class RoutePutMuteTimingRequest(StrictModel):
    """Replace an existing mute timing configuration with new time intervals. This operation completely overwrites the mute timing identified by name with the provided settings."""
    path: RoutePutMuteTimingRequestPath
    body: RoutePutMuteTimingRequestBody | None = None

# Operation: delete_mute_timing
class RouteDeleteMuteTimingRequestPath(StrictModel):
    name: str = Field(default=..., description="The name of the mute timing to delete. Must match an existing mute timing configuration.")
class RouteDeleteMuteTimingRequest(StrictModel):
    """Delete a mute timing configuration by name. This removes the specified mute timing rule from the provisioning system."""
    path: RouteDeleteMuteTimingRequestPath

# Operation: export_mute_timing
class RouteExportMuteTimingRequestPath(StrictModel):
    name: str = Field(default=..., description="The name of the mute timing to export.")
class RouteExportMuteTimingRequestQuery(StrictModel):
    format_: Literal["yaml", "json", "hcl"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="The format for the exported file. Choose from YAML, JSON, or HCL. Defaults to YAML if not specified.")
class RouteExportMuteTimingRequest(StrictModel):
    """Export a mute timing configuration in the specified provisioning format (YAML, JSON, or HCL) for use in infrastructure-as-code workflows."""
    path: RouteExportMuteTimingRequestPath
    query: RouteExportMuteTimingRequestQuery | None = None

# Operation: get_notification_template
class RouteGetTemplateRequestPath(StrictModel):
    name: str = Field(default=..., description="The name of the notification template group to retrieve.")
class RouteGetTemplateRequest(StrictModel):
    """Retrieve a notification template group by name. Returns the template configuration for the specified template group."""
    path: RouteGetTemplateRequestPath

# Operation: update_notification_template
class RoutePutTemplateRequestPath(StrictModel):
    name: str = Field(default=..., description="The unique identifier of the notification template group to update. Used to locate and modify the specific template configuration.")
class RoutePutTemplateRequestBody(StrictModel):
    template: str | None = Field(default=None, description="The updated template content or configuration for the notification template group. Defines the structure and content of notifications sent through this template.")
class RoutePutTemplateRequest(StrictModel):
    """Updates an existing notification template group with new configuration. Allows modification of template settings for the specified template group name."""
    path: RoutePutTemplateRequestPath
    body: RoutePutTemplateRequestBody | None = None

# Operation: delete_notification_template
class RouteDeleteTemplateRequestPath(StrictModel):
    name: str = Field(default=..., description="The name of the notification template group to delete. Must be an exact match to an existing template group.")
class RouteDeleteTemplateRequest(StrictModel):
    """Delete a notification template group by name. This operation permanently removes the template group and all associated configurations."""
    path: RouteDeleteTemplateRequestPath

# ============================================================================
# Component Models
# ============================================================================

class DashboardAclUpdateItem(PermissiveModel):
    permission: int | None = None
    role: Literal["None", "Viewer", "Editor", "Admin"] | None = None
    team_id: int | None = Field(None, validation_alias="teamId", serialization_alias="teamId", json_schema_extra={'format': 'int64'})
    user_id: int | None = Field(None, validation_alias="userId", serialization_alias="userId", json_schema_extra={'format': 'int64'})

class Group(PermissiveModel):
    group_id: str | None = Field(None, validation_alias="groupID", serialization_alias="groupID")
    mappings: Any | None = None

class ImportDashboardInput(PermissiveModel):
    name: str | None = None
    plugin_id: str | None = Field(None, validation_alias="pluginId", serialization_alias="pluginId")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type")
    value: str | None = None

class Json(RootModel[dict[str, Any]]):
    pass

class ObjectIdentifier(RootModel[list[int]]):
    pass

class AttributeTypeAndValue(PermissiveModel):
    """AttributeTypeAndValue mirrors the ASN.1 structure of the same name in
RFC 5280, Section 4.1.2.4."""
    type_: ObjectIdentifier | None = Field(None, validation_alias="Type", serialization_alias="Type")
    value: Any | None = Field(None, validation_alias="Value", serialization_alias="Value")

class Name(PermissiveModel):
    """Name represents an X.509 distinguished name. This only includes the common
elements of a DN. Note that Name is only an approximation of the X.509
structure. If an accurate representation is needed, asn1.Unmarshal the raw
subject or issuer as an [RDNSequence]."""
    country: list[str] | None = Field(None, validation_alias="Country", serialization_alias="Country")
    extra_names: list[AttributeTypeAndValue] | None = Field(None, validation_alias="ExtraNames", serialization_alias="ExtraNames", description="ExtraNames contains attributes to be copied, raw, into any marshaled\ndistinguished names. Values override any attributes with the same OID.\nThe ExtraNames field is not populated when parsing, see Names.")
    locality: list[str] | None = Field(None, validation_alias="Locality", serialization_alias="Locality")
    names: list[AttributeTypeAndValue] | None = Field(None, validation_alias="Names", serialization_alias="Names", description="Names contains all parsed attributes. When parsing distinguished names,\nthis can be used to extract non-standard attributes that are not parsed\nby this package. When marshaling to RDNSequences, the Names field is\nignored, see ExtraNames.")
    serial_number: str | None = Field(None, validation_alias="SerialNumber", serialization_alias="SerialNumber")
    street_address: list[str] | None = Field(None, validation_alias="StreetAddress", serialization_alias="StreetAddress")

class PrometheusRule(PermissiveModel):
    alert: str | None = None
    annotations_: dict[str, str] | None = Field(None, validation_alias="annotations", serialization_alias="annotations")
    expr: str | None = None
    for_: str | None = Field(None, validation_alias="for", serialization_alias="for")
    keep_firing_for: str | None = None
    labels: dict[str, str] | None = None
    record: str | None = None

class ReportDashboardId(PermissiveModel):
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    name: str | None = None
    uid: str | None = None

class ReportSchedule(PermissiveModel):
    day_of_month: str | None = Field(None, validation_alias="dayOfMonth", serialization_alias="dayOfMonth")
    end_date: str | None = Field(None, validation_alias="endDate", serialization_alias="endDate", json_schema_extra={'format': 'date-time'})
    frequency: str | None = None
    interval_amount: int | None = Field(None, validation_alias="intervalAmount", serialization_alias="intervalAmount", json_schema_extra={'format': 'int64'})
    interval_frequency: str | None = Field(None, validation_alias="intervalFrequency", serialization_alias="intervalFrequency")
    start_date: str | None = Field(None, validation_alias="startDate", serialization_alias="startDate", json_schema_extra={'format': 'date-time'})
    time_zone: str | None = Field(None, validation_alias="timeZone", serialization_alias="timeZone")
    workdays_only: bool | None = Field(None, validation_alias="workdaysOnly", serialization_alias="workdaysOnly")

class ReportTimeRange(PermissiveModel):
    from_: str | None = Field(None, validation_alias="from", serialization_alias="from")
    to: str | None = None

class ReportDashboard(PermissiveModel):
    dashboard: ReportDashboardId | None = None
    report_variables: dict[str, Any] | None = Field(None, validation_alias="reportVariables", serialization_alias="reportVariables")
    time_range: ReportTimeRange | None = Field(None, validation_alias="timeRange", serialization_alias="timeRange")

class ReportOptions(PermissiveModel):
    csv_encoding: str | None = Field(None, validation_alias="csvEncoding", serialization_alias="csvEncoding")
    layout: str | None = None
    orientation: str | None = None
    pdf_combine_one_file: bool | None = Field(None, validation_alias="pdfCombineOneFile", serialization_alias="pdfCombineOneFile")
    pdf_show_template_variables: bool | None = Field(None, validation_alias="pdfShowTemplateVariables", serialization_alias="pdfShowTemplateVariables")
    time_range: ReportTimeRange | None = Field(None, validation_alias="timeRange", serialization_alias="timeRange")

class Report(PermissiveModel):
    created: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    dashboards: list[ReportDashboard] | None = None
    enable_csv: bool | None = Field(None, validation_alias="enableCsv", serialization_alias="enableCsv")
    enable_dashboard_url: bool | None = Field(None, validation_alias="enableDashboardUrl", serialization_alias="enableDashboardUrl")
    formats: list[str] | None = None
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    message: str | None = None
    name: str | None = None
    options: ReportOptions | None = None
    org_id: int | None = Field(None, validation_alias="orgId", serialization_alias="orgId", json_schema_extra={'format': 'int64'})
    recipients: str | None = None
    reply_to: str | None = Field(None, validation_alias="replyTo", serialization_alias="replyTo")
    scale_factor: int | None = Field(None, validation_alias="scaleFactor", serialization_alias="scaleFactor", json_schema_extra={'format': 'int64'})
    schedule: ReportSchedule | None = None
    state: str | None = None
    subject: str | None = None
    uid: str | None = None
    updated: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    user_id: int | None = Field(None, validation_alias="userId", serialization_alias="userId", json_schema_extra={'format': 'int64'})

class SetResourcePermissionCommand(PermissiveModel):
    built_in_role: str | None = Field(None, validation_alias="builtInRole", serialization_alias="builtInRole")
    permission: str | None = None
    team_id: int | None = Field(None, validation_alias="teamId", serialization_alias="teamId", json_schema_extra={'format': 'int64'})
    user_id: int | None = Field(None, validation_alias="userId", serialization_alias="userId", json_schema_extra={'format': 'int64'})

class Transformation(PermissiveModel):
    expression: str | None = None
    field: str | None = None
    map_value: str | None = Field(None, validation_alias="mapValue", serialization_alias="mapValue")
    type_: Literal["regex", "logfmt"] | None = Field(None, validation_alias="type", serialization_alias="type")

class TimeInterval(PermissiveModel):
    name: str | None = None
    time_intervals: list[TimeInterval] | None = None


# Rebuild models to resolve forward references (required for circular refs)
AttributeTypeAndValue.model_rebuild()
DashboardAclUpdateItem.model_rebuild()
Group.model_rebuild()
ImportDashboardInput.model_rebuild()
Json.model_rebuild()
Name.model_rebuild()
ObjectIdentifier.model_rebuild()
PrometheusRule.model_rebuild()
Report.model_rebuild()
ReportDashboard.model_rebuild()
ReportDashboardId.model_rebuild()
ReportOptions.model_rebuild()
ReportSchedule.model_rebuild()
ReportTimeRange.model_rebuild()
SetResourcePermissionCommand.model_rebuild()
TimeInterval.model_rebuild()
Transformation.model_rebuild()

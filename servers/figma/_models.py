"""
Figma MCP Server - Pydantic Models

Generated: 2026-04-09 17:20:26 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Annotated, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field, RootModel

__all__ = [
    "DeleteCommentReactionRequest",
    "DeleteCommentRequest",
    "DeleteDevResourceRequest",
    "GetActivityLogsRequest",
    "GetCommentReactionsRequest",
    "GetCommentsRequest",
    "GetComponentRequest",
    "GetComponentSetRequest",
    "GetDevResourcesRequest",
    "GetFileComponentSetsRequest",
    "GetFileComponentsRequest",
    "GetFileMetaRequest",
    "GetFileNodesRequest",
    "GetFileRequest",
    "GetFileStylesRequest",
    "GetFileVersionsRequest",
    "GetImageFillsRequest",
    "GetImagesRequest",
    "GetLibraryAnalyticsComponentActionsRequest",
    "GetLibraryAnalyticsComponentUsagesRequest",
    "GetLibraryAnalyticsStyleActionsRequest",
    "GetLibraryAnalyticsStyleUsagesRequest",
    "GetLibraryAnalyticsVariableActionsRequest",
    "GetLibraryAnalyticsVariableUsagesRequest",
    "GetLocalVariablesRequest",
    "GetPaymentsRequest",
    "GetProjectFilesRequest",
    "GetPublishedVariablesRequest",
    "GetStyleRequest",
    "GetTeamComponentSetsRequest",
    "GetTeamComponentsRequest",
    "GetTeamProjectsRequest",
    "GetTeamStylesRequest",
    "GetWebhookRequest",
    "GetWebhooksRequest",
    "PostCommentReactionRequest",
    "PostCommentRequest",
    "PostDevResourcesRequest",
    "PostVariablesRequest",
    "PutDevResourcesRequest",
    "FrameOffset",
    "FrameOffsetRegion",
    "PostDevResourcesBodyDevResourcesItem",
    "PutDevResourcesBodyDevResourcesItem",
    "Region",
    "VariableChange",
    "VariableCollectionChange",
    "VariableModeChange",
    "VariableModeValue",
    "Vector",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: export_file_json
class GetFileRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The unique identifier of the file to export. Can be extracted from the Figma file URL (https://www.figma.com/file/{file_key}/{title}) or obtained as a branch key using the branch_data parameter.")
class GetFileRequestQuery(StrictModel):
    ids: str | None = Field(default=None, description="Comma-separated list of node IDs to include in the export. When specified, returns only the requested nodes, their children, and ancestor chains. Top-level canvas nodes are always included regardless of this parameter.")
    depth: float | None = Field(default=None, description="Controls traversal depth into the document tree. A value of 1 returns only pages; 2 returns pages and top-level objects; omitting returns the entire tree.")
    geometry: str | None = Field(default=None, description="Set to include vector path data in the export for shape and vector nodes.")
    plugin_data: str | None = Field(default=None, description="Comma-separated list of plugin IDs and/or the string 'shared' to include plugin data written to the document. Plugin data will appear in pluginData and sharedPluginData properties.")
    branch_data: bool | None = Field(default=None, description="Include branch metadata in the response, showing the main file key if this is a branch, or branch metadata if the file has branches.")
class GetFileRequest(StrictModel):
    """Export a Figma file as JSON, including document structure, components, and optional metadata. Supports partial exports by node ID and configurable depth traversal."""
    path: GetFileRequestPath
    query: GetFileRequestQuery | None = None

# Operation: get_file_nodes
class GetFileNodesRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The Figma file identifier to query. Can be either a file key or branch key (obtain branch key via GET /v1/files/:key with branch_data parameter).")
class GetFileNodesRequestQuery(StrictModel):
    ids: str = Field(default=..., description="Comma-separated list of node IDs to retrieve. The API will return data for each specified node, though some values may be null if a node ID does not exist in the file.")
    depth: float | None = Field(default=None, description="How many levels deep to traverse the node tree from each specified node. A value of 1 returns only direct children; omitting this parameter returns the entire subtree.")
    geometry: str | None = Field(default=None, description="Include vector path data in the response. Set to 'paths' to export vector geometry; omit to exclude vector data.")
    plugin_data: str | None = Field(default=None, description="Comma-separated list of plugin IDs and/or the string 'shared' to include plugin data written to the document. Plugin data will be returned in pluginData and sharedPluginData properties.")
class GetFileNodesRequest(StrictModel):
    """Retrieve specific nodes from a Figma file as JSON objects. Extract node data by providing node IDs, with optional support for vector geometry, nested traversal depth, and plugin data."""
    path: GetFileNodesRequestPath
    query: GetFileNodesRequestQuery

# Operation: render_node_images
class GetImagesRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The file to export images from. Accepts either a file key or branch key. Use GET /v1/files/:key with the branch_data query parameter to retrieve a branch key.")
class GetImagesRequestQuery(StrictModel):
    ids: str = Field(default=..., description="Comma-separated list of node IDs to render. Multiple node IDs can be specified to render multiple images from the same file.")
    scale: float | None = Field(default=None, description="Scaling factor for the rendered image. Values between 0.01 and 4 are supported, where 1.0 represents the original size.", ge=0.01, le=4)
    format_: Literal["jpg", "png", "svg", "pdf"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="Output format for the rendered image.")
    svg_include_id: bool | None = Field(default=None, description="Whether to include id attributes for all SVG elements. When enabled, adds the layer name to the id attribute of each SVG element.")
class GetImagesRequest(StrictModel):
    """Render images from specified nodes in a file. Returns a map of node IDs to image URLs, with null values indicating failed renders. Rendered images expire after 30 days."""
    path: GetImagesRequestPath
    query: GetImagesRequestQuery

# Operation: list_image_fills
class GetImageFillsRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The Figma file identifier to retrieve images from. Accepts either a file key or branch key; use GET /v1/files/:key with branch_data query parameter to obtain a branch key.")
class GetImageFillsRequest(StrictModel):
    """Retrieve download URLs for all images used in image fills within a Figma document. Image URLs are valid for up to 14 days and can be located by their imageRef attribute in Paint objects from the file endpoint."""
    path: GetImageFillsRequestPath

# Operation: get_file_metadata
class GetFileMetaRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The unique identifier for the file or branch. Use a file key for standard file metadata or a branch key for branch-specific metadata.")
class GetFileMetaRequest(StrictModel):
    """Retrieve metadata for a file or branch. Provide either a file key or branch key to access file information."""
    path: GetFileMetaRequestPath

# Operation: list_team_projects
class GetTeamProjectsRequestPath(StrictModel):
    team_id: str = Field(default=..., description="The unique identifier of the team. You can find the team ID in the URL of your team page, positioned after 'team' and before your team name.")
class GetTeamProjectsRequest(StrictModel):
    """Retrieve all projects within a specified team that are visible to the authenticated user. Only projects accessible to the token owner or authenticated user will be returned."""
    path: GetTeamProjectsRequestPath

# Operation: list_project_files
class GetProjectFilesRequestPath(StrictModel):
    project_id: str = Field(default=..., description="The unique identifier of the project from which to retrieve files.")
class GetProjectFilesRequestQuery(StrictModel):
    branch_data: bool | None = Field(default=None, description="Include branch metadata in the response for each main file that contains branches within the project.")
class GetProjectFilesRequest(StrictModel):
    """Retrieve all files within a specified project. Optionally include branch metadata for files that contain branches."""
    path: GetProjectFilesRequestPath
    query: GetProjectFilesRequestQuery | None = None

# Operation: list_file_versions
class GetFileVersionsRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The file or branch key identifying which file's version history to retrieve. Obtain the branch key using GET /v1/files/:key with the branch_data query parameter.")
class GetFileVersionsRequestQuery(StrictModel):
    page_size: float | None = Field(default=None, description="Number of version records to return per page. Defaults to 30 if not specified.", le=50)
class GetFileVersionsRequest(StrictModel):
    """Retrieve the version history of a file to see how it has evolved over time. Use the returned version information to render a specific version via another endpoint."""
    path: GetFileVersionsRequestPath
    query: GetFileVersionsRequestQuery | None = None

# Operation: list_file_comments
class GetCommentsRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The file or branch identifier to retrieve comments from. Use the file key for the main file, or obtain a branch key via GET /v1/files/:key with the branch_data query parameter to access comments on a specific branch.")
class GetCommentsRequestQuery(StrictModel):
    as_md: bool | None = Field(default=None, description="When enabled, converts comments to their markdown equivalents where applicable for better formatting compatibility.")
class GetCommentsRequest(StrictModel):
    """Retrieves all comments left on a file. Supports both file keys and branch keys for accessing comments across different file versions."""
    path: GetCommentsRequestPath
    query: GetCommentsRequestQuery | None = None

# Operation: add_file_comment
class PostCommentRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The file identifier to add the comment to. Can be a file key or branch key; use GET /v1/files/:key with the branch_data query parameter to retrieve a branch key.")
class PostCommentRequestBody(StrictModel):
    """Comment to post."""
    message: str = Field(default=..., description="The text content of the comment to post.")
    comment_id: str | None = Field(default=None, description="The ID of the root comment to reply to. Replies to replies are not supported; only root-level comments can be replied to.")
    client_meta: Vector | FrameOffset | Region | FrameOffsetRegion | None = Field(default=None, description="Metadata specifying the position or location where the comment should be placed within the file.")
class PostCommentRequest(StrictModel):
    """Posts a new comment on a file or replies to an existing root comment. Use the comment_id parameter to reply to a specific comment."""
    path: PostCommentRequestPath
    body: PostCommentRequestBody

# Operation: delete_comment
class DeleteCommentRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The file or branch key identifying the file containing the comment. Retrieve the branch key using GET /v1/files/:key with the branch_data query parameter.")
    comment_id: str = Field(default=..., description="The unique identifier of the comment to delete.")
class DeleteCommentRequest(StrictModel):
    """Deletes a specific comment from a file. Only the comment author is permitted to delete their own comments."""
    path: DeleteCommentRequestPath

# Operation: list_comment_reactions
class GetCommentReactionsRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The file identifier to retrieve the comment from. Can be either a file key or branch key; use `GET /v1/files/:key` with the `branch_data` query parameter to obtain a branch key if needed.")
    comment_id: str = Field(default=..., description="The unique identifier of the comment to retrieve reactions from.")
class GetCommentReactionsRequest(StrictModel):
    """Retrieves a paginated list of reactions left on a specific comment. Use this to see all emoji reactions and their authors for a given comment."""
    path: GetCommentReactionsRequestPath

# Operation: add_comment_reaction
class PostCommentReactionRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The file identifier to add the reaction to. Can be a file key or branch key; use GET /v1/files/:key with the branch_data query parameter to retrieve a branch key.")
    comment_id: str = Field(default=..., description="The unique identifier of the comment to react to.")
class PostCommentReactionRequestBody(StrictModel):
    """Reaction to post."""
    emoji: str = Field(default=..., description="The emoji reaction as a shortcode format. Supports optional skin tone modifiers for applicable emoji. Valid shortcodes are defined in the emoji-mart native set.")
class PostCommentReactionRequest(StrictModel):
    """Add an emoji reaction to a file comment. Reactions allow users to quickly respond to comments with emoji expressions."""
    path: PostCommentReactionRequestPath
    body: PostCommentReactionRequestBody

# Operation: remove_comment_reaction
class DeleteCommentReactionRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The file or branch key containing the comment. Retrieve the branch key using GET /v1/files/:key with the branch_data query parameter.")
    comment_id: str = Field(default=..., description="The unique identifier of the comment from which to remove the reaction.")
class DeleteCommentReactionRequestQuery(StrictModel):
    emoji: str = Field(default=..., description="The emoji reaction to remove, specified as a shortcode format. Skin tone modifiers are supported where applicable.")
class DeleteCommentReactionRequest(StrictModel):
    """Remove a reaction from a comment. Only the user who added the reaction can delete it."""
    path: DeleteCommentReactionRequestPath
    query: DeleteCommentReactionRequestQuery

# Operation: list_team_components
class GetTeamComponentsRequestPath(StrictModel):
    team_id: str = Field(default=..., description="The unique identifier of the team whose components you want to list.")
class GetTeamComponentsRequestQuery(StrictModel):
    page_size: float | None = Field(default=None, description="The number of components to return per page. Specify a value between 1 and 1000 to control result set size.")
class GetTeamComponentsRequest(StrictModel):
    """Retrieve a paginated list of published components available in a team's component library. Use pagination to manage large result sets efficiently."""
    path: GetTeamComponentsRequestPath
    query: GetTeamComponentsRequestQuery | None = None

# Operation: list_file_components
class GetFileComponentsRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The main file key identifying the file library to retrieve components from. Branch keys are not supported for this operation.")
class GetFileComponentsRequest(StrictModel):
    """Retrieve a list of published components available in a file library. Only main file keys are supported, as components cannot be published from branch files."""
    path: GetFileComponentsRequestPath

# Operation: get_component
class GetComponentRequestPath(StrictModel):
    key: str = Field(default=..., description="The unique identifier that uniquely identifies the component within the system.")
class GetComponentRequest(StrictModel):
    """Retrieve detailed metadata for a specific component using its unique identifier. This operation returns comprehensive information about the component's configuration and properties."""
    path: GetComponentRequestPath

# Operation: list_component_sets
class GetTeamComponentSetsRequestPath(StrictModel):
    team_id: str = Field(default=..., description="The unique identifier of the team whose component sets you want to retrieve.")
class GetTeamComponentSetsRequestQuery(StrictModel):
    page_size: float | None = Field(default=None, description="The number of component sets to return per page. Useful for controlling response size and implementing pagination.")
class GetTeamComponentSetsRequest(StrictModel):
    """Retrieve a paginated list of published component sets available in a team's library. Use pagination to manage large result sets efficiently."""
    path: GetTeamComponentSetsRequestPath
    query: GetTeamComponentSetsRequestQuery | None = None

# Operation: list_component_sets_file
class GetFileComponentSetsRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The main file key identifying the library file. Branch keys are not supported as component sets can only be published from main files.")
class GetFileComponentSetsRequest(StrictModel):
    """Retrieve all published component sets available in a file library. This operation requires a main file key and cannot be used with branch keys."""
    path: GetFileComponentSetsRequestPath

# Operation: get_component_set
class GetComponentSetRequestPath(StrictModel):
    key: str = Field(default=..., description="The unique identifier that uniquely identifies the component set to retrieve.")
class GetComponentSetRequest(StrictModel):
    """Retrieve metadata for a published component set using its unique identifier. Returns detailed information about the component set configuration and properties."""
    path: GetComponentSetRequestPath

# Operation: list_team_styles
class GetTeamStylesRequestPath(StrictModel):
    team_id: str = Field(default=..., description="The unique identifier of the team whose styles you want to retrieve.")
class GetTeamStylesRequestQuery(StrictModel):
    page_size: float | None = Field(default=None, description="The number of styles to return per page. Adjust this value to control result set size.")
class GetTeamStylesRequest(StrictModel):
    """Retrieve a paginated list of published styles from a team's design library. Use pagination to control the number of results returned per request."""
    path: GetTeamStylesRequestPath
    query: GetTeamStylesRequestQuery | None = None

# Operation: list_file_styles
class GetFileStylesRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The main file key containing the styles to retrieve. Branch keys are not supported since style publishing is only available for main files.")
class GetFileStylesRequest(StrictModel):
    """Retrieve a list of published styles available in a file library. Styles can only be published from main files, not from branches."""
    path: GetFileStylesRequestPath

# Operation: get_style
class GetStyleRequestPath(StrictModel):
    key: str = Field(default=..., description="The unique identifier that references the specific style to retrieve.")
class GetStyleRequest(StrictModel):
    """Retrieve detailed metadata for a specific style using its unique identifier. Use this to fetch style configuration and properties."""
    path: GetStyleRequestPath

# Operation: list_webhooks
class GetWebhooksRequestQuery(StrictModel):
    context_id: str | None = Field(default=None, description="The unique identifier of the context to retrieve webhooks for. Cannot be used together with plan_api_id.")
    plan_api_id: str | None = Field(default=None, description="The unique identifier of your plan to retrieve all webhooks across all accessible contexts. Cannot be used together with context_id. Results are paginated when using this parameter.")
class GetWebhooksRequest(StrictModel):
    """Retrieve webhooks filtered by context or plan. Use context_id to get webhooks for a specific context, or plan_api_id to retrieve all webhooks across all accessible contexts with pagination support."""
    query: GetWebhooksRequestQuery | None = None

# Operation: get_webhook
class GetWebhookRequestPath(StrictModel):
    webhook_id: str = Field(default=..., description="The unique identifier of the webhook to retrieve.")
class GetWebhookRequest(StrictModel):
    """Retrieve a webhook configuration by its ID. Use this to fetch details about a specific webhook including its URL, events, and status."""
    path: GetWebhookRequestPath

# Operation: list_activity_logs
class GetActivityLogsRequestQuery(StrictModel):
    events: str | None = Field(default=None, description="Filter results to include only specified event types. Accepts comma-separated values to include multiple event types; all events are returned if unspecified.")
    start_time: float | None = Field(default=None, description="Unix timestamp marking the start of the time range (inclusive). Defaults to one year ago if unspecified.")
    end_time: float | None = Field(default=None, description="Unix timestamp marking the end of the time range (inclusive). Defaults to the current timestamp if unspecified.")
    limit: float | None = Field(default=None, description="Maximum number of events to return in the response. Defaults to 1000 if unspecified.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for events by timestamp. Use ascending order to show oldest events first, or descending order to show newest events first.")
class GetActivityLogsRequest(StrictModel):
    """Retrieve a list of activity log events filtered by type, time range, and ordering. Useful for auditing, monitoring system changes, and tracking user actions."""
    query: GetActivityLogsRequestQuery | None = None

# Operation: list_payments
class GetPaymentsRequestQuery(StrictModel):
    user_id: str | None = Field(default=None, description="The ID of the user whose payment information you want to retrieve. Obtain this by having the user authenticate via OAuth2 to the Figma REST API.")
    community_file_id: str | None = Field(default=None, description="The ID of the Community file to query. Find this in the file's Community page URL (the number after 'file/'). Provide exactly one of: community_file_id, plugin_id, or widget_id.")
    plugin_id: str | None = Field(default=None, description="The ID of the plugin to query. Find this in the plugin's manifest or Community page URL (the number after 'plugin/'). Provide exactly one of: community_file_id, plugin_id, or widget_id.")
    widget_id: str | None = Field(default=None, description="The ID of the widget to query. Find this in the widget's manifest or Community page URL (the number after 'widget/'). Provide exactly one of: community_file_id, plugin_id, or widget_id.")
class GetPaymentsRequest(StrictModel):
    """Retrieve payment information for a user on a specific Community file, plugin, or widget. You can only query resources that you own."""
    query: GetPaymentsRequestQuery | None = None

# Operation: list_local_variables
class GetLocalVariablesRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The file or branch identifier to retrieve variables from. Use the branch key obtained from GET /v1/files/:key with the branch_data query parameter to access branch-specific variables.")
class GetLocalVariablesRequest(StrictModel):
    """Retrieve all local variables created in a file and remote variables referenced within it. This operation is restricted to full members of Enterprise organizations and supports examining variable modes and bound variable details."""
    path: GetLocalVariablesRequestPath

# Operation: list_published_variables
class GetPublishedVariablesRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The main file key to retrieve published variables from. Branch keys are not supported as variables cannot be published from branches.")
class GetPublishedVariablesRequest(StrictModel):
    """Retrieve all variables published from a file, including their subscription IDs and last published timestamps. Available only to full members of Enterprise organizations."""
    path: GetPublishedVariablesRequestPath

# Operation: bulk_modify_variables
class PostVariablesRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The file to modify variables in. Can be a file key or branch key obtained from GET /v1/files/:key with the branch_data query parameter.")
class PostVariablesRequestBody(StrictModel):
    variable_collections: list[VariableCollectionChange] | None = Field(default=None, validation_alias="variableCollections", serialization_alias="variableCollections", description="Array of variable collection objects to create, update, or delete. Each object must include an action property (create, update, or delete). Processed first in the request.")
    variable_modes: list[VariableModeChange] | None = Field(default=None, validation_alias="variableModes", serialization_alias="variableModes", description="Array of variable mode objects to create, update, or delete within collections. Each collection supports a maximum of 40 modes with names up to 40 characters. Processed second in the request.")
    variables: list[VariableChange] | None = Field(default=None, description="Array of variable objects to create, update, or delete. Each collection supports a maximum of 5000 variables. Variable names must be unique within a collection and cannot contain special characters such as . { }. Processed third in the request.")
    variable_mode_values: list[VariableModeValue] | None = Field(default=None, validation_alias="variableModeValues", serialization_alias="variableModeValues", description="Array of variable mode value assignments to set specific values for variables under particular modes. Variables cannot be aliased to themselves or form alias cycles. Processed last in the request.")
class PostVariablesRequest(StrictModel):
    """Bulk create, update, and delete variables, variable collections, modes, and mode values in a file. Changes are applied atomically in a defined order: collections, then modes, then variables, then mode values."""
    path: PostVariablesRequestPath
    body: PostVariablesRequestBody | None = None

# Operation: list_dev_resources
class GetDevResourcesRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The main file key to retrieve dev resources from. Branch keys are not supported.")
class GetDevResourcesRequestQuery(StrictModel):
    node_ids: str | None = Field(default=None, description="Comma-separated list of node identifiers to filter results. When specified, only dev resources attached to these nodes are returned. Omit to retrieve all dev resources in the file.")
class GetDevResourcesRequest(StrictModel):
    """Retrieve development resources associated with a file. Optionally filter results to specific nodes within the file."""
    path: GetDevResourcesRequestPath
    query: GetDevResourcesRequestQuery | None = None

# Operation: create_dev_resources
class PostDevResourcesRequestBody(StrictModel):
    """A list of dev resources that you want to create."""
    dev_resources: list[PostDevResourcesBodyDevResourcesItem] = Field(default=..., description="An array of dev resource objects to create. Each resource must reference a valid file_key, have a unique URL per node, and not exceed the 10 dev resource limit per node.")
class PostDevResourcesRequest(StrictModel):
    """Bulk create dev resources across multiple files. Successfully created resources are returned in the links_created array, while any resources that fail validation appear in the errors array with failure reasons."""
    body: PostDevResourcesRequestBody

# Operation: update_dev_resources
class PutDevResourcesRequestBody(StrictModel):
    """A list of dev resources that you want to update."""
    dev_resources: list[PutDevResourcesBodyDevResourcesItem] = Field(default=..., description="An array of dev resource objects to update. Each resource in the array will be processed, and results will be returned indicating which resources were successfully updated and which encountered errors.")
class PutDevResourcesRequest(StrictModel):
    """Bulk update dev resources across multiple files. Successfully updated resource IDs are returned in the response, while any resources that fail to update are included in an errors array."""
    body: PutDevResourcesRequestBody

# Operation: remove_dev_resource
class DeleteDevResourceRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The main file key containing the dev resource to delete. Must be a main file key, not a branch key.")
    dev_resource_id: str = Field(default=..., description="The unique identifier of the dev resource to delete.")
class DeleteDevResourceRequest(StrictModel):
    """Remove a dev resource from a file. This operation permanently deletes the specified dev resource and cannot be undone."""
    path: DeleteDevResourceRequestPath

# Operation: list_library_component_actions
class GetLibraryAnalyticsComponentActionsRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The unique identifier of the library file for which to retrieve analytics data.")
class GetLibraryAnalyticsComponentActionsRequestQuery(StrictModel):
    group_by: Literal["component", "team"] = Field(default=..., description="The dimension by which to aggregate the returned analytics data.")
    start_date: str | None = Field(default=None, description="The earliest week to include in the analytics results, specified as an ISO 8601 date. The date will be rounded back to the nearest start of a week. Defaults to one year prior to the end date.")
    end_date: str | None = Field(default=None, description="The latest week to include in the analytics results, specified as an ISO 8601 date. The date will be rounded forward to the nearest end of a week. Defaults to the most recently computed week.")
class GetLibraryAnalyticsComponentActionsRequest(StrictModel):
    """Retrieve analytics data for component actions within a library, aggregated by the specified dimension (component or team). Use this to analyze usage patterns and activity metrics across your design library."""
    path: GetLibraryAnalyticsComponentActionsRequestPath
    query: GetLibraryAnalyticsComponentActionsRequestQuery

# Operation: list_library_component_usages
class GetLibraryAnalyticsComponentUsagesRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The unique identifier of the library file for which to retrieve component usage analytics.")
class GetLibraryAnalyticsComponentUsagesRequestQuery(StrictModel):
    group_by: Literal["component", "file"] = Field(default=..., description="The dimension by which to group the returned usage analytics data.")
class GetLibraryAnalyticsComponentUsagesRequest(StrictModel):
    """Retrieves analytics data on how components from a library are being used, with results grouped by the specified dimension (component or file)."""
    path: GetLibraryAnalyticsComponentUsagesRequestPath
    query: GetLibraryAnalyticsComponentUsagesRequestQuery

# Operation: list_library_style_actions
class GetLibraryAnalyticsStyleActionsRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The unique identifier of the library for which to fetch style action analytics.")
class GetLibraryAnalyticsStyleActionsRequestQuery(StrictModel):
    group_by: Literal["style", "team"] = Field(default=..., description="The dimension to group analytics results by. Choose 'style' to aggregate by individual styles or 'team' to aggregate by team.")
    start_date: str | None = Field(default=None, description="The earliest week to include in results, specified as an ISO 8601 date. The date will be rounded back to the nearest week start. Defaults to one year prior to the end date.")
    end_date: str | None = Field(default=None, description="The latest week to include in results, specified as an ISO 8601 date. The date will be rounded forward to the nearest week end. Defaults to the most recently computed week.")
class GetLibraryAnalyticsStyleActionsRequest(StrictModel):
    """Retrieve analytics data for style actions in a library, aggregated by the specified dimension (style or team). Use date parameters to filter results to a specific time range."""
    path: GetLibraryAnalyticsStyleActionsRequestPath
    query: GetLibraryAnalyticsStyleActionsRequestQuery

# Operation: list_library_style_usages
class GetLibraryAnalyticsStyleUsagesRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The unique identifier of the library file for which to retrieve style usage analytics.")
class GetLibraryAnalyticsStyleUsagesRequestQuery(StrictModel):
    group_by: Literal["style", "file"] = Field(default=..., description="The dimension by which to group the returned analytics data. Choose 'style' to see usage broken down by individual styles, or 'file' to see usage broken down by the files that consume those styles.")
class GetLibraryAnalyticsStyleUsagesRequest(StrictModel):
    """Retrieves analytics data on how styles are used within a library, aggregated by the specified dimension (style or file). Use this to understand style adoption and usage patterns across your design library."""
    path: GetLibraryAnalyticsStyleUsagesRequestPath
    query: GetLibraryAnalyticsStyleUsagesRequestQuery

# Operation: list_library_variable_actions
class GetLibraryAnalyticsVariableActionsRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The unique identifier of the library for which to fetch variable action analytics.")
class GetLibraryAnalyticsVariableActionsRequestQuery(StrictModel):
    group_by: Literal["variable", "team"] = Field(default=..., description="The dimension by which to group the returned analytics data.")
    start_date: str | None = Field(default=None, description="ISO 8601 date marking the start of the analytics period. Dates are rounded back to the nearest week start. Defaults to one year prior to the end date.")
    end_date: str | None = Field(default=None, description="ISO 8601 date marking the end of the analytics period. Dates are rounded forward to the nearest week end. Defaults to the latest computed week.")
class GetLibraryAnalyticsVariableActionsRequest(StrictModel):
    """Retrieve analytics data for variable actions within a library, aggregated by the specified dimension (variable or team). Use date parameters to filter results to a specific time range."""
    path: GetLibraryAnalyticsVariableActionsRequestPath
    query: GetLibraryAnalyticsVariableActionsRequestQuery

# Operation: list_library_variable_usages
class GetLibraryAnalyticsVariableUsagesRequestPath(StrictModel):
    file_key: str = Field(default=..., description="The unique identifier of the library file for which to retrieve variable usage analytics.")
class GetLibraryAnalyticsVariableUsagesRequestQuery(StrictModel):
    group_by: Literal["variable", "file"] = Field(default=..., description="The dimension by which to aggregate the returned variable usage data. Choose 'variable' to group by individual variables, or 'file' to group by source files.")
class GetLibraryAnalyticsVariableUsagesRequest(StrictModel):
    """Retrieves analytics data on how variables are used within a library, aggregated by the specified dimension (variable or file). Use this to understand variable usage patterns and dependencies."""
    path: GetLibraryAnalyticsVariableUsagesRequestPath
    query: GetLibraryAnalyticsVariableUsagesRequestQuery

# ============================================================================
# Component Models
# ============================================================================

class BasePaint(PermissiveModel):
    visible: bool | None = Field(True, description="Is the paint enabled?")
    opacity: float | None = Field(1, description="Overall opacity of paint (colors within the paint can also have opacity values which would blend with this)", ge=0, le=1)
    blend_mode: Literal["PASS_THROUGH", "NORMAL", "DARKEN", "MULTIPLY", "LINEAR_BURN", "COLOR_BURN", "LIGHTEN", "SCREEN", "LINEAR_DODGE", "COLOR_DODGE", "OVERLAY", "SOFT_LIGHT", "HARD_LIGHT", "DIFFERENCE", "EXCLUSION", "HUE", "SATURATION", "COLOR", "LUMINOSITY"] = Field(..., validation_alias="blendMode", serialization_alias="blendMode", description="How this node blends with nodes behind it in the scene")

class ImageFilters(PermissiveModel):
    """Image filters to apply to the node."""
    exposure: float | None = 0
    contrast: float | None = 0
    saturation: float | None = 0
    temperature: float | None = 0
    tint: float | None = 0
    highlights: float | None = 0
    shadows: float | None = 0

class PostDevResourcesBodyDevResourcesItem(PermissiveModel):
    name: str = Field(..., description="The name of the dev resource.")
    url: str = Field(..., description="The URL of the dev resource.")
    file_key: str = Field(..., description="The file key where the dev resource belongs.")
    node_id: str = Field(..., description="The target node to attach the dev resource to.")

class PutDevResourcesBodyDevResourcesItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier of the dev resource")
    name: str | None = Field(None, description="The name of the dev resource.")
    url: str | None = Field(None, description="The URL of the dev resource.")

class Region(PermissiveModel):
    """Position of a region comment on the canvas."""
    x: float = Field(..., description="X coordinate of the position.")
    y: float = Field(..., description="Y coordinate of the position.")
    region_height: float = Field(..., description="The height of the comment region. Must be greater than 0.")
    region_width: float = Field(..., description="The width of the comment region. Must be greater than 0.")
    comment_pin_corner: Literal["top-left", "top-right", "bottom-left", "bottom-right"] | None = Field('bottom-right', description="The corner of the comment region to pin to the node's corner as a string enum.")

class Rgb(PermissiveModel):
    """An RGB color"""
    r: float = Field(..., description="Red channel value, between 0 and 1.", ge=0, le=1)
    g: float = Field(..., description="Green channel value, between 0 and 1.", ge=0, le=1)
    b: float = Field(..., description="Blue channel value, between 0 and 1.", ge=0, le=1)

class Rgba(PermissiveModel):
    """An RGBA color"""
    r: float = Field(..., description="Red channel value, between 0 and 1.", ge=0, le=1)
    g: float = Field(..., description="Green channel value, between 0 and 1.", ge=0, le=1)
    b: float = Field(..., description="Blue channel value, between 0 and 1.", ge=0, le=1)
    a: float = Field(..., description="Alpha channel value, between 0 and 1.", ge=0, le=1)

class Transform(RootModel[list[list[float]]]):
    pass

class ImagePaint(PermissiveModel):
    type_: Literal["IMAGE"] = Field(..., validation_alias="type", serialization_alias="type", description="The string literal \"IMAGE\" representing the paint's type. Always check the `type` before reading other properties.")
    scale_mode: Literal["FILL", "FIT", "TILE", "STRETCH"] = Field(..., validation_alias="scaleMode", serialization_alias="scaleMode", description="Image scaling mode.")
    image_ref: str = Field(..., validation_alias="imageRef", serialization_alias="imageRef", description="A reference to an image embedded in this node. To download the image using this reference, use the `GET file images` endpoint to retrieve the mapping from image references to image URLs.")
    image_transform: Transform | None = Field(None, validation_alias="imageTransform", serialization_alias="imageTransform", description="Affine transform applied to the image, only present if `scaleMode` is `STRETCH`")
    scaling_factor: float | None = Field(None, validation_alias="scalingFactor", serialization_alias="scalingFactor", description="Amount image is scaled by in tiling, only present if scaleMode is `TILE`.")
    filters: ImageFilters | None = Field(None, description="Defines what image filters have been applied to this paint, if any. If this property is not defined, no filters have been applied.")
    rotation: float | None = Field(0, description="Image rotation, in degrees.")
    gif_ref: str | None = Field(None, validation_alias="gifRef", serialization_alias="gifRef", description="A reference to an animated GIF embedded in this node. To download the image using this reference, use the `GET file images` endpoint to retrieve the mapping from image references to image URLs.")
    visible: bool | None = Field(True, description="Is the paint enabled?")
    opacity: float | None = Field(1, description="Overall opacity of paint (colors within the paint can also have opacity values which would blend with this)", ge=0, le=1)
    blend_mode: Literal["PASS_THROUGH", "NORMAL", "DARKEN", "MULTIPLY", "LINEAR_BURN", "COLOR_BURN", "LIGHTEN", "SCREEN", "LINEAR_DODGE", "COLOR_DODGE", "OVERLAY", "SOFT_LIGHT", "HARD_LIGHT", "DIFFERENCE", "EXCLUSION", "HUE", "SATURATION", "COLOR", "LUMINOSITY"] = Field(..., validation_alias="blendMode", serialization_alias="blendMode", description="How this node blends with nodes behind it in the scene")

class User(PermissiveModel):
    """A description of a user."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique stable id of the user.")
    handle: str = Field(..., description="Name of the user.")
    img_url: str = Field(..., description="URL link to the user's profile image.")

class Reaction(PermissiveModel):
    """A reaction left by a user."""
    user: User = Field(..., description="The user who left the reaction.")
    emoji: str
    created_at: str = Field(..., description="The UTC ISO 8601 time at which the reaction was left.", json_schema_extra={'format': 'date-time'})

class VariableAlias(PermissiveModel):
    """Contains a variable alias"""
    type_: Literal["VARIABLE_ALIAS"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The id of the variable that the current variable is aliased to. This variable can be a local or remote variable, and both can be retrieved via the GET /v1/files/:file_key/variables/local endpoint.")

class ColorStopBoundVariables(PermissiveModel):
    """The variables bound to a particular gradient stop"""
    color: VariableAlias | None = None

class ColorStop(PermissiveModel):
    """A single color stop with its position along the gradient axis, color, and bound variables if any"""
    position: float = Field(..., description="Value between 0 and 1 representing position along gradient axis.")
    color: Rgba = Field(..., description="Color attached to corresponding position.")
    bound_variables: ColorStopBoundVariables | None = Field(None, validation_alias="boundVariables", serialization_alias="boundVariables", description="The variables bound to a particular gradient stop")

class SolidPaintBoundVariables(PermissiveModel):
    """The variables bound to a particular field on this paint"""
    color: VariableAlias | None = None

class SolidPaint(PermissiveModel):
    type_: Literal["SOLID"] = Field(..., validation_alias="type", serialization_alias="type", description="The string literal \"SOLID\" representing the paint's type. Always check the `type` before reading other properties.")
    color: Rgba = Field(..., description="Solid color of the paint")
    bound_variables: SolidPaintBoundVariables | None = Field(None, validation_alias="boundVariables", serialization_alias="boundVariables", description="The variables bound to a particular field on this paint")
    visible: bool | None = Field(True, description="Is the paint enabled?")
    opacity: float | None = Field(1, description="Overall opacity of paint (colors within the paint can also have opacity values which would blend with this)", ge=0, le=1)
    blend_mode: Literal["PASS_THROUGH", "NORMAL", "DARKEN", "MULTIPLY", "LINEAR_BURN", "COLOR_BURN", "LIGHTEN", "SCREEN", "LINEAR_DODGE", "COLOR_DODGE", "OVERLAY", "SOFT_LIGHT", "HARD_LIGHT", "DIFFERENCE", "EXCLUSION", "HUE", "SATURATION", "COLOR", "LUMINOSITY"] = Field(..., validation_alias="blendMode", serialization_alias="blendMode", description="How this node blends with nodes behind it in the scene")

class SolidPaintV0BoundVariables(PermissiveModel):
    """The variables bound to a particular field on this paint"""
    color: VariableAlias | None = None

class VariableCodeSyntax(PermissiveModel):
    """An object containing platform-specific code syntax definitions for a variable. All platforms are optional."""
    web: str | None = Field(None, validation_alias="WEB", serialization_alias="WEB")
    android: str | None = Field(None, validation_alias="ANDROID", serialization_alias="ANDROID")
    i_os: str | None = Field(None, validation_alias="iOS", serialization_alias="iOS")

class VariableCollectionCreate(PermissiveModel):
    """An object that contains details about creating a `VariableCollection`."""
    action: Literal["CREATE"] = Field(..., description="The action to perform for the variable collection.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="A temporary id for this variable collection.")
    name: str = Field(..., description="The name of this variable collection.")
    initial_mode_id: str | None = Field(None, validation_alias="initialModeId", serialization_alias="initialModeId", description="The initial mode refers to the mode that is created by default. You can set a temporary id here, in order to reference this mode later in this request.")
    hidden_from_publishing: bool | None = Field(False, validation_alias="hiddenFromPublishing", serialization_alias="hiddenFromPublishing", description="Whether this variable collection is hidden when publishing the current file as a library.")
    parent_variable_collection_id: str | None = Field(None, validation_alias="parentVariableCollectionId", serialization_alias="parentVariableCollectionId", description="The id of the parent variable collection that this variable collection is extending from.")
    initial_mode_id_to_parent_mode_id_mapping: dict[str, str] | None = Field(None, validation_alias="initialModeIdToParentModeIdMapping", serialization_alias="initialModeIdToParentModeIdMapping", description="Maps inherited modes from the parent variable collection to the initial mode ids on the extended variable collection.")

class VariableCollectionDelete(PermissiveModel):
    """An object that contains details about deleting a `VariableCollection`."""
    action: Literal["DELETE"] = Field(..., description="The action to perform for the variable collection.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The id of the variable collection to delete.")

class VariableCollectionUpdate(PermissiveModel):
    """An object that contains details about updating a `VariableCollection`."""
    action: Literal["UPDATE"] = Field(..., description="The action to perform for the variable collection.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The id of the variable collection to update.")
    name: str | None = Field(None, description="The name of this variable collection.")
    hidden_from_publishing: bool | None = Field(False, validation_alias="hiddenFromPublishing", serialization_alias="hiddenFromPublishing", description="Whether this variable collection is hidden when publishing the current file as a library.")

class VariableCollectionChange(RootModel[Annotated[
    VariableCollectionCreate
    | VariableCollectionUpdate
    | VariableCollectionDelete,
    Field(discriminator="action")
]]):
    pass

class VariableCreate(PermissiveModel):
    """An object that contains details about creating a `Variable`."""
    action: Literal["CREATE"] = Field(..., description="The action to perform for the variable.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="A temporary id for this variable.")
    name: str = Field(..., description="The name of this variable.")
    variable_collection_id: str = Field(..., validation_alias="variableCollectionId", serialization_alias="variableCollectionId", description="The variable collection that will contain the variable. You can use the temporary id of a variable collection.")
    resolved_type: Literal["BOOLEAN", "FLOAT", "STRING", "COLOR"] = Field(..., validation_alias="resolvedType", serialization_alias="resolvedType", description="The resolved type of the variable.")
    description: str | None = Field(None, description="The description of this variable.")
    hidden_from_publishing: bool | None = Field(False, validation_alias="hiddenFromPublishing", serialization_alias="hiddenFromPublishing", description="Whether this variable is hidden when publishing the current file as a library.")
    scopes: list[Literal["ALL_SCOPES", "TEXT_CONTENT", "CORNER_RADIUS", "WIDTH_HEIGHT", "GAP", "ALL_FILLS", "FRAME_FILL", "SHAPE_FILL", "TEXT_FILL", "STROKE_COLOR", "STROKE_FLOAT", "EFFECT_FLOAT", "EFFECT_COLOR", "OPACITY", "FONT_FAMILY", "FONT_STYLE", "FONT_WEIGHT", "FONT_SIZE", "LINE_HEIGHT", "LETTER_SPACING", "PARAGRAPH_SPACING", "PARAGRAPH_INDENT", "FONT_VARIATIONS"]] | None = Field(None, description="An array of scopes in the UI where this variable is shown. Setting this property will show/hide this variable in the variable picker UI for different fields.")
    code_syntax: VariableCodeSyntax | None = Field(None, validation_alias="codeSyntax", serialization_alias="codeSyntax")

class VariableDelete(PermissiveModel):
    """An object that contains details about deleting a `Variable`."""
    action: Literal["DELETE"] = Field(..., description="The action to perform for the variable.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The id of the variable to delete.")

class VariableModeCreate(PermissiveModel):
    """An object that contains details about creating a `VariableMode`."""
    action: Literal["CREATE"] = Field(..., description="The action to perform for the variable mode.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="A temporary id for this variable mode.")
    name: str = Field(..., description="The name of this variable mode.")
    variable_collection_id: str = Field(..., validation_alias="variableCollectionId", serialization_alias="variableCollectionId", description="The variable collection that will contain the mode. You can use the temporary id of a variable collection. New modes cannot be created on extended collections.")

class VariableModeDelete(PermissiveModel):
    """An object that contains details about deleting a `VariableMode`."""
    action: Literal["DELETE"] = Field(..., description="The action to perform for the variable mode.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The id of the variable mode to delete. Modes cannot be deleted on extended collections unless its parent mode has been deleted.")

class VariableModeUpdate(PermissiveModel):
    """An object that contains details about updating a `VariableMode`."""
    action: Literal["UPDATE"] = Field(..., description="The action to perform for the variable mode.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The id of the variable mode to update.")
    name: str | None = Field(None, description="The name of this variable mode.")
    variable_collection_id: str = Field(..., validation_alias="variableCollectionId", serialization_alias="variableCollectionId", description="The variable collection that contains the mode. Modes cannot be updated on extended collections.")

class VariableModeChange(RootModel[Annotated[
    VariableModeCreate
    | VariableModeUpdate
    | VariableModeDelete,
    Field(discriminator="action")
]]):
    pass

class VariableModeValue(PermissiveModel):
    """An object that represents a value for a given mode of a variable. All properties are required."""
    variable_id: str = Field(..., validation_alias="variableId", serialization_alias="variableId", description="The target variable. You can use the temporary id of a variable.")
    mode_id: str = Field(..., validation_alias="modeId", serialization_alias="modeId", description="Must correspond to a mode in the variable collection that contains the target variable.")
    value: bool | float | str | Rgb | Rgba | VariableAlias

class VariableUpdate(PermissiveModel):
    """An object that contains details about updating a `Variable`."""
    action: Literal["UPDATE"] = Field(..., description="The action to perform for the variable.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The id of the variable to update.")
    name: str | None = Field(None, description="The name of this variable.")
    description: str | None = Field(None, description="The description of this variable.")
    hidden_from_publishing: bool | None = Field(False, validation_alias="hiddenFromPublishing", serialization_alias="hiddenFromPublishing", description="Whether this variable is hidden when publishing the current file as a library.")
    scopes: list[Literal["ALL_SCOPES", "TEXT_CONTENT", "CORNER_RADIUS", "WIDTH_HEIGHT", "GAP", "ALL_FILLS", "FRAME_FILL", "SHAPE_FILL", "TEXT_FILL", "STROKE_COLOR", "STROKE_FLOAT", "EFFECT_FLOAT", "EFFECT_COLOR", "OPACITY", "FONT_FAMILY", "FONT_STYLE", "FONT_WEIGHT", "FONT_SIZE", "LINE_HEIGHT", "LETTER_SPACING", "PARAGRAPH_SPACING", "PARAGRAPH_INDENT", "FONT_VARIATIONS"]] | None = Field(None, description="An array of scopes in the UI where this variable is shown. Setting this property will show/hide this variable in the variable picker UI for different fields.")
    code_syntax: VariableCodeSyntax | None = Field(None, validation_alias="codeSyntax", serialization_alias="codeSyntax")

class VariableChange(RootModel[Annotated[
    VariableCreate
    | VariableUpdate
    | VariableDelete,
    Field(discriminator="action")
]]):
    pass

class Vector(PermissiveModel):
    """A 2d vector."""
    x: float = Field(..., description="X coordinate of the vector.")
    y: float = Field(..., description="Y coordinate of the vector.")

class FrameOffset(PermissiveModel):
    """Position of a comment relative to the frame to which it is attached."""
    node_id: str = Field(..., description="Unique id specifying the frame.")
    node_offset: Vector = Field(..., description="2D vector offset within the frame from the top-left corner.")

class FrameOffsetRegion(PermissiveModel):
    """Position of a region comment relative to the frame to which it is attached."""
    node_id: str = Field(..., description="Unique id specifying the frame.")
    node_offset: Vector = Field(..., description="2D vector offset within the frame from the top-left corner.")
    region_height: float = Field(..., description="The height of the comment region. Must be greater than 0.")
    region_width: float = Field(..., description="The width of the comment region. Must be greater than 0.")
    comment_pin_corner: Literal["top-left", "top-right", "bottom-left", "bottom-right"] | None = Field('bottom-right', description="The corner of the comment region to pin to the node's corner as a string enum.")

class Comment(PermissiveModel):
    """A comment or reply left by a user."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier for comment.")
    client_meta: Vector | FrameOffset | Region | FrameOffsetRegion = Field(..., description="Positioning information of the comment. Includes information on the location of the comment pin, which is either the absolute coordinates on the canvas or a relative offset within a frame. If the comment is a region, it will also contain the region height, width, and position of the anchor in regards to the region.")
    file_key: str = Field(..., description="The file in which the comment lives")
    parent_id: str | None = Field(None, description="If present, the id of the comment to which this is the reply")
    user: User = Field(..., description="The user who left the comment")
    created_at: str = Field(..., description="The UTC ISO 8601 time at which the comment was left", json_schema_extra={'format': 'date-time'})
    resolved_at: str | None = Field(None, description="If set, the UTC ISO 8601 time the comment was resolved", json_schema_extra={'format': 'date-time'})
    message: str = Field(..., description="The content of the comment")
    order_id: str | None = Field(..., description="Only set for top level comments. The number displayed with the comment in the UI")
    reactions: list[Reaction] = Field(..., description="An array of reactions to the comment")

class GradientPaint(PermissiveModel):
    type_: Literal["GRADIENT_LINEAR", "GRADIENT_RADIAL", "GRADIENT_ANGULAR", "GRADIENT_DIAMOND"] = Field(..., validation_alias="type", serialization_alias="type", description="The string literal representing the paint's type. Always check the `type` before reading other properties.")
    gradient_handle_positions: list[Vector] = Field(..., validation_alias="gradientHandlePositions", serialization_alias="gradientHandlePositions", description="This field contains three vectors, each of which are a position in normalized object space (normalized object space is if the top left corner of the bounding box of the object is (0, 0) and the bottom right is (1,1)). The first position corresponds to the start of the gradient (value 0 for the purposes of calculating gradient stops), the second position is the end of the gradient (value 1), and the third handle position determines the width of the gradient.")
    gradient_stops: list[ColorStop] = Field(..., validation_alias="gradientStops", serialization_alias="gradientStops", description="Positions of key points along the gradient axis with the colors anchored there. Colors along the gradient are interpolated smoothly between neighboring gradient stops.")
    visible: bool | None = Field(True, description="Is the paint enabled?")
    opacity: float | None = Field(1, description="Overall opacity of paint (colors within the paint can also have opacity values which would blend with this)", ge=0, le=1)
    blend_mode: Literal["PASS_THROUGH", "NORMAL", "DARKEN", "MULTIPLY", "LINEAR_BURN", "COLOR_BURN", "LIGHTEN", "SCREEN", "LINEAR_DODGE", "COLOR_DODGE", "OVERLAY", "SOFT_LIGHT", "HARD_LIGHT", "DIFFERENCE", "EXCLUSION", "HUE", "SATURATION", "COLOR", "LUMINOSITY"] = Field(..., validation_alias="blendMode", serialization_alias="blendMode", description="How this node blends with nodes behind it in the scene")

class PatternPaint(PermissiveModel):
    type_: Literal["PATTERN"] = Field(..., validation_alias="type", serialization_alias="type", description="The string literal \"PATTERN\" representing the paint's type. Always check the `type` before reading other properties.")
    source_node_id: str = Field(..., validation_alias="sourceNodeId", serialization_alias="sourceNodeId", description="The node id of the source node for the pattern")
    tile_type: Literal["RECTANGULAR", "HORIZONTAL_HEXAGONAL", "VERTICAL_HEXAGONAL"] = Field(..., validation_alias="tileType", serialization_alias="tileType", description="The tile type for the pattern")
    scaling_factor: float = Field(..., validation_alias="scalingFactor", serialization_alias="scalingFactor", description="The scaling factor for the pattern")
    spacing: Vector = Field(..., description="The spacing for the pattern")
    horizontal_alignment: Literal["START", "CENTER", "END"] = Field(..., validation_alias="horizontalAlignment", serialization_alias="horizontalAlignment", description="The horizontal alignment for the pattern")
    vertical_alignment: Literal["START", "CENTER", "END"] = Field(..., validation_alias="verticalAlignment", serialization_alias="verticalAlignment", description="The vertical alignment for the pattern")
    visible: bool | None = Field(True, description="Is the paint enabled?")
    opacity: float | None = Field(1, description="Overall opacity of paint (colors within the paint can also have opacity values which would blend with this)", ge=0, le=1)
    blend_mode: Literal["PASS_THROUGH", "NORMAL", "DARKEN", "MULTIPLY", "LINEAR_BURN", "COLOR_BURN", "LIGHTEN", "SCREEN", "LINEAR_DODGE", "COLOR_DODGE", "OVERLAY", "SOFT_LIGHT", "HARD_LIGHT", "DIFFERENCE", "EXCLUSION", "HUE", "SATURATION", "COLOR", "LUMINOSITY"] = Field(..., validation_alias="blendMode", serialization_alias="blendMode", description="How this node blends with nodes behind it in the scene")

class Paint(PermissiveModel):
    paint: SolidPaint | GradientPaint | ImagePaint | PatternPaint


# Rebuild models to resolve forward references (required for circular refs)
BasePaint.model_rebuild()
ColorStop.model_rebuild()
ColorStopBoundVariables.model_rebuild()
Comment.model_rebuild()
FrameOffset.model_rebuild()
FrameOffsetRegion.model_rebuild()
GradientPaint.model_rebuild()
ImageFilters.model_rebuild()
ImagePaint.model_rebuild()
Paint.model_rebuild()
PatternPaint.model_rebuild()
PostDevResourcesBodyDevResourcesItem.model_rebuild()
PutDevResourcesBodyDevResourcesItem.model_rebuild()
Reaction.model_rebuild()
Region.model_rebuild()
Rgb.model_rebuild()
Rgba.model_rebuild()
SolidPaint.model_rebuild()
SolidPaintBoundVariables.model_rebuild()
SolidPaintV0BoundVariables.model_rebuild()
Transform.model_rebuild()
User.model_rebuild()
VariableAlias.model_rebuild()
VariableChange.model_rebuild()
VariableCodeSyntax.model_rebuild()
VariableCollectionChange.model_rebuild()
VariableCollectionCreate.model_rebuild()
VariableCollectionDelete.model_rebuild()
VariableCollectionUpdate.model_rebuild()
VariableCreate.model_rebuild()
VariableDelete.model_rebuild()
VariableModeChange.model_rebuild()
VariableModeCreate.model_rebuild()
VariableModeDelete.model_rebuild()
VariableModeUpdate.model_rebuild()
VariableModeValue.model_rebuild()
VariableUpdate.model_rebuild()
Vector.model_rebuild()

"""
Apify MCP Server - Pydantic Models

Generated: 2026-04-14 18:14:06 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field, RootModel

__all__ = [
    "ActBuildDefaultGetRequest",
    "ActBuildsGetRequest",
    "ActBuildsPostRequest",
    "ActDeleteRequest",
    "ActGetRequest",
    "ActorBuildAbortPostRequest",
    "ActorBuildDeleteRequest",
    "ActorBuildGetRequest",
    "ActorBuildLogGetRequest",
    "ActorBuildsGetRequest",
    "ActorRunAbortPostRequest",
    "ActorRunDeleteRequest",
    "ActorRunGetRequest",
    "ActorRunMetamorphPostRequest",
    "ActorRunPutRequest",
    "ActorRunRebootPostRequest",
    "ActorRunsGetRequest",
    "ActorTaskDeleteRequest",
    "ActorTaskGetRequest",
    "ActorTaskInputGetRequest",
    "ActorTaskInputPutRequest",
    "ActorTaskPutRequest",
    "ActorTaskRunsGetRequest",
    "ActorTaskRunsLastGetRequest",
    "ActorTaskRunsPostRequest",
    "ActorTaskRunSyncGetDatasetItemsGetRequest",
    "ActorTaskRunSyncGetDatasetItemsPostRequest",
    "ActorTaskRunSyncGetRequest",
    "ActorTaskRunSyncPostRequest",
    "ActorTasksGetRequest",
    "ActorTasksPostRequest",
    "ActorTaskWebhooksGetRequest",
    "ActPutRequest",
    "ActRunResurrectPostRequest",
    "ActRunsGetRequest",
    "ActRunsLastGetRequest",
    "ActRunsPostRequest",
    "ActRunSyncGetDatasetItemsGetRequest",
    "ActRunSyncGetDatasetItemsPostRequest",
    "ActRunSyncGetRequest",
    "ActRunSyncPostRequest",
    "ActsGetRequest",
    "ActsPostRequest",
    "ActVersionDeleteRequest",
    "ActVersionEnvVarDeleteRequest",
    "ActVersionEnvVarGetRequest",
    "ActVersionEnvVarPutRequest",
    "ActVersionEnvVarsGetRequest",
    "ActVersionEnvVarsPostRequest",
    "ActVersionGetRequest",
    "ActVersionPutRequest",
    "ActVersionsGetRequest",
    "ActVersionsPostRequest",
    "ActWebhooksGetRequest",
    "DatasetDeleteRequest",
    "DatasetGetRequest",
    "DatasetItemsGetRequest",
    "DatasetItemsPostRequest",
    "DatasetPutRequest",
    "DatasetsGetRequest",
    "DatasetsPostRequest",
    "DatasetStatisticsGetRequest",
    "KeyValueStoreDeleteRequest",
    "KeyValueStoreGetRequest",
    "KeyValueStoreKeysGetRequest",
    "KeyValueStorePutRequest",
    "KeyValueStoreRecordDeleteRequest",
    "KeyValueStoreRecordGetRequest",
    "KeyValueStoreRecordHeadRequest",
    "KeyValueStoreRecordPutRequest",
    "KeyValueStoresGetRequest",
    "KeyValueStoresPostRequest",
    "LogGetRequest",
    "PostChargeRunRequest",
    "PostResurrectRunRequest",
    "RequestQueueDeleteRequest",
    "RequestQueueGetRequest",
    "RequestQueueHeadGetRequest",
    "RequestQueueHeadLockPostRequest",
    "RequestQueuePutRequest",
    "RequestQueueRequestDeleteRequest",
    "RequestQueueRequestGetRequest",
    "RequestQueueRequestLockDeleteRequest",
    "RequestQueueRequestLockPutRequest",
    "RequestQueueRequestPutRequest",
    "RequestQueueRequestsBatchDeleteRequest",
    "RequestQueueRequestsBatchPostRequest",
    "RequestQueueRequestsGetRequest",
    "RequestQueueRequestsPostRequest",
    "RequestQueueRequestsUnlockPostRequest",
    "RequestQueuesGetRequest",
    "RequestQueuesPostRequest",
    "ScheduleDeleteRequest",
    "ScheduleGetRequest",
    "ScheduleLogGetRequest",
    "SchedulePutRequest",
    "SchedulesGetRequest",
    "SchedulesPostRequest",
    "StoreGetRequest",
    "UserGetRequest",
    "UsersMeUsageMonthlyGetRequest",
    "WebhookDeleteRequest",
    "WebhookDispatchesGetRequest",
    "WebhookDispatchGetRequest",
    "WebhookGetRequest",
    "WebhookPutRequest",
    "WebhooksGetRequest",
    "WebhooksPostRequest",
    "WebhookTestPostRequest",
    "WebhookWebhookDispatchesGetRequest",
    "ActorRunPutBody",
    "ActorTasksPostBody",
    "BuildTag",
    "CreateOrUpdateVersionRequest",
    "EnvVar",
    "FlatPricePerMonthActorPricingInfo",
    "FreeActorPricingInfo",
    "PayPerEventActorPricingInfo",
    "PricePerDatasetItemActorPricingInfo",
    "PutItemsRequest",
    "RequestDraft",
    "RequestDraftDelete",
    "RequestQueuePutBody",
    "ScheduleCreateActions",
    "SourceCodeFile",
    "SourceCodeFolder",
    "Version",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_actors
class ActsGetRequestQuery(StrictModel):
    my: bool | None = Field(default=None, description="When set to true, restricts the results to only Actors owned by the authenticated user, excluding Actors they have used but not created.")
    offset: float | None = Field(default=None, description="Number of records to skip from the beginning of the result set, used for paginating through large lists. Defaults to 0.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of Actors to return in a single response. Accepts values between 1 and 1000, with 1000 being both the default and the upper limit.", json_schema_extra={'format': 'double'})
    desc: bool | None = Field(default=None, description="When set to true, reverses the sort order so that the most recently created (or most recently run, if sorting by last run) Actors appear first.")
    sort_by: Literal["createdAt", "stats.lastRunStartedAt"] | None = Field(default=None, validation_alias="sortBy", serialization_alias="sortBy", description="Determines the field used to order results. Use 'createdAt' to sort by when the Actor was created, or 'stats.lastRunStartedAt' to sort by the most recent run start time.")
class ActsGetRequest(StrictModel):
    """Retrieves a paginated list of Actors the user has created or used, with options to filter to owned Actors only and sort by creation date or last run time. Returns up to 1000 records per request."""
    query: ActsGetRequestQuery | None = None

# Operation: create_actor
class ActsPostRequestBodyDefaultRunOptions(StrictModel):
    restart_on_error: bool | None = Field(default=None, validation_alias="restartOnError", serialization_alias="restartOnError", description="Whether the Actor run should automatically restart if it encounters an error during execution.", examples=[False])
    build: str | None = Field(default=None, validation_alias="build", serialization_alias="build", description="The default build tag or version to use when starting a run, such as a semantic version tag or 'latest'.", examples=['latest'])
    timeout_secs: int | None = Field(default=None, validation_alias="timeoutSecs", serialization_alias="timeoutSecs", description="Default maximum run duration in seconds; the run is terminated if it exceeds this limit.", examples=[3600])
    memory_mbytes: int | None = Field(default=None, validation_alias="memoryMbytes", serialization_alias="memoryMbytes", description="Default memory allocation in megabytes for each Actor run; must be a power of 2.", examples=[2048])
    max_items: int | None = Field(default=None, validation_alias="maxItems", serialization_alias="maxItems", description="Maximum number of output items the Actor is allowed to produce per run; used for pay-per-result pricing enforcement.")
    force_permission_level: Literal["LIMITED_PERMISSIONS", "FULL_PERMISSIONS"] | None = Field(default=None, validation_alias="forcePermissionLevel", serialization_alias="forcePermissionLevel", description="Specifies the permission level the Actor requires at runtime; use LIMITED_PERMISSIONS to restrict access or FULL_PERMISSIONS for unrestricted access. See Actor permissions documentation for details.", examples=['LIMITED_PERMISSIONS'])
class ActsPostRequestBodyActorStandby(StrictModel):
    build: str | None = Field(default=None, validation_alias="build", serialization_alias="build", description="The build tag or version to use when starting the Actor in Standby mode.")
    memory_mbytes: int | None = Field(default=None, validation_alias="memoryMbytes", serialization_alias="memoryMbytes", description="Memory allocation in megabytes for the Actor when running in Standby mode.")
    is_enabled: bool | None = Field(default=None, validation_alias="isEnabled", serialization_alias="isEnabled", description="Whether the Actor is enabled and available to be run; set to false to disable the Actor without deleting it.")
    desired_requests_per_actor_run: int | None = Field(default=None, validation_alias="desiredRequestsPerActorRun", serialization_alias="desiredRequestsPerActorRun", description="Target number of requests to be processed per Actor run in Standby mode, used for autoscaling decisions.")
    max_requests_per_actor_run: int | None = Field(default=None, validation_alias="maxRequestsPerActorRun", serialization_alias="maxRequestsPerActorRun", description="Hard upper limit on the number of requests processed per Actor run in Standby mode.")
    idle_timeout_secs: int | None = Field(default=None, validation_alias="idleTimeoutSecs", serialization_alias="idleTimeoutSecs", description="Duration in seconds after which an idle Standby Actor instance is terminated to free resources.")
    disable_standby_fields_override: bool | None = Field(default=None, validation_alias="disableStandbyFieldsOverride", serialization_alias="disableStandbyFieldsOverride", description="When true, prevents automatic overriding of Standby-related fields by the platform during Actor configuration updates.")
    should_pass_actor_input: bool | None = Field(default=None, validation_alias="shouldPassActorInput", serialization_alias="shouldPassActorInput", description="Whether the Actor's input should be forwarded to Standby mode instances when they are activated.")
class ActsPostRequestBodyExampleRunInput(StrictModel):
    body: str | None = Field(default=None, validation_alias="body", serialization_alias="body", description="Raw JSON string representing the default input body passed to the Actor run.")
    content_type: str | None = Field(default=None, validation_alias="contentType", serialization_alias="contentType", description="MIME content type of the input body, specifying encoding and format for correct parsing.", examples=['application/json; charset=utf-8'])
class ActsPostRequestBody(StrictModel):
    name: str | None = Field(default=None, description="Unique identifier name for the Actor, used in URLs and API references.", examples=['MyActor'])
    description: str | None = Field(default=None, description="Short human-readable description of what the Actor does, displayed in Apify Store and the Actor detail page.", examples=['My favourite actor!'])
    title: str | None = Field(default=None, description="Display title for the Actor shown in Apify Store; required when making the Actor public.", examples=['My actor'])
    is_public: bool | None = Field(default=None, validation_alias="isPublic", serialization_alias="isPublic", description="Whether the Actor is publicly listed in Apify Store; requires title and categories to be set when true.", examples=[False])
    seo_title: str | None = Field(default=None, validation_alias="seoTitle", serialization_alias="seoTitle", description="SEO-optimized title for the Actor's store page, used for search engine indexing.", examples=['My actor'])
    seo_description: str | None = Field(default=None, validation_alias="seoDescription", serialization_alias="seoDescription", description="SEO-optimized description for the Actor's store page, used for search engine indexing.", examples=['My actor is the best'])
    versions: list[Version] | None = Field(default=None, description="List of source code version objects defining the Actor's versioned implementations; at least one version is required. Each item follows the Version object schema.")
    pricing_infos: list[PayPerEventActorPricingInfo | PricePerDatasetItemActorPricingInfo | FlatPricePerMonthActorPricingInfo | FreeActorPricingInfo] | None = Field(default=None, validation_alias="pricingInfos", serialization_alias="pricingInfos", description="List of pricing information objects associated with the Actor, defining monetization tiers or pay-per-result configurations.")
    categories: list[str] | None = Field(default=None, description="List of Apify Store category identifiers under which the Actor is classified; required when isPublic is true. Use constants from the apify-shared-js package.")
    default_run_options: ActsPostRequestBodyDefaultRunOptions | None = Field(default=None, validation_alias="defaultRunOptions", serialization_alias="defaultRunOptions")
    actor_standby: ActsPostRequestBodyActorStandby | None = Field(default=None, validation_alias="actorStandby", serialization_alias="actorStandby")
    example_run_input: ActsPostRequestBodyExampleRunInput | None = Field(default=None, validation_alias="exampleRunInput", serialization_alias="exampleRunInput")
class ActsPostRequest(StrictModel):
    """Creates a new Actor on the Apify platform with the specified configuration, including source code versions, run options, and publishing settings. At least one version of the source code must be defined; set isPublic to true along with a title and categories to list the Actor in Apify Store."""
    body: ActsPostRequestBody | None = None

# Operation: get_actor
class ActGetRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique identifier of the Actor to retrieve, either as an Actor ID or a tilde-separated combination of the owner's username and Actor name.")
class ActGetRequest(StrictModel):
    """Retrieves full details for a specific Actor, including its configuration, settings, and metadata. Use this to inspect an Actor before running it or to verify its current state."""
    path: ActGetRequestPath

# Operation: update_actor
class ActPutRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique ID of the Actor, or a tilde-separated string combining the owner's username and Actor name.")
class ActPutRequestBodyDefaultRunOptions(StrictModel):
    restart_on_error: bool | None = Field(default=None, validation_alias="restartOnError", serialization_alias="restartOnError", description="Whether the Actor should automatically restart if it encounters an error during a run.", examples=[False])
    build: str | None = Field(default=None, validation_alias="build", serialization_alias="build", description="The default build tag or version to use when starting a run, such as a version tag.", examples=['latest'])
    timeout_secs: int | None = Field(default=None, validation_alias="timeoutSecs", serialization_alias="timeoutSecs", description="The default maximum run duration in seconds before the run is forcefully stopped.", examples=[3600])
    memory_mbytes: int | None = Field(default=None, validation_alias="memoryMbytes", serialization_alias="memoryMbytes", description="The default amount of memory in megabytes allocated to each Actor run.", examples=[2048])
    max_items: int | None = Field(default=None, validation_alias="maxItems", serialization_alias="maxItems", description="The maximum number of items the Actor is allowed to return in a single run.")
    force_permission_level: Literal["LIMITED_PERMISSIONS", "FULL_PERMISSIONS"] | None = Field(default=None, validation_alias="forcePermissionLevel", serialization_alias="forcePermissionLevel", description="Overrides the permission level the Actor is forced to run with, regardless of the actorPermissionLevel setting.", examples=['LIMITED_PERMISSIONS'])
class ActPutRequestBodyActorStandby(StrictModel):
    build: str | None = Field(default=None, validation_alias="build", serialization_alias="build", description="The build tag or version to use when starting the Actor in Standby mode.")
    memory_mbytes: int | None = Field(default=None, validation_alias="memoryMbytes", serialization_alias="memoryMbytes", description="The amount of memory in megabytes allocated when the Actor runs in Standby mode.")
    is_enabled: bool | None = Field(default=None, validation_alias="isEnabled", serialization_alias="isEnabled", description="Whether the Actor Standby mode is enabled, allowing the Actor to remain warm and handle requests without cold-start delays.")
    desired_requests_per_actor_run: int | None = Field(default=None, validation_alias="desiredRequestsPerActorRun", serialization_alias="desiredRequestsPerActorRun", description="The target number of concurrent requests the Actor Standby should aim to handle per active Actor run.")
    max_requests_per_actor_run: int | None = Field(default=None, validation_alias="maxRequestsPerActorRun", serialization_alias="maxRequestsPerActorRun", description="The maximum number of concurrent requests allowed per Actor run when operating in Standby mode.")
    idle_timeout_secs: int | None = Field(default=None, validation_alias="idleTimeoutSecs", serialization_alias="idleTimeoutSecs", description="The number of seconds a Standby Actor run may remain idle without receiving requests before it is shut down.")
    disable_standby_fields_override: bool | None = Field(default=None, validation_alias="disableStandbyFieldsOverride", serialization_alias="disableStandbyFieldsOverride", description="When true, prevents automatic overriding of Standby-related fields by the platform.")
    should_pass_actor_input: bool | None = Field(default=None, validation_alias="shouldPassActorInput", serialization_alias="shouldPassActorInput", description="Whether the Actor's input schema should be forwarded to the Standby Actor run when it is initialized.")
class ActPutRequestBodyExampleRunInput(StrictModel):
    body: str | None = Field(default=None, validation_alias="body", serialization_alias="body", description="The raw JSON request body payload containing the Actor settings to update, serialized as a string.")
    content_type: str | None = Field(default=None, validation_alias="contentType", serialization_alias="contentType", description="The MIME content type of the request body, which must be set to application/json.", examples=['application/json; charset=utf-8'])
class ActPutRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The internal name identifier for the Actor.", examples=['MyActor'])
    description: str | None = Field(default=None, description="A short human-readable description of what the Actor does.", examples=['My favourite actor!'])
    is_public: bool | None = Field(default=None, validation_alias="isPublic", serialization_alias="isPublic", description="Whether the Actor is publicly visible in Apify Store. Setting this to true also requires providing a title and categories.", examples=[False])
    actor_permission_level: Literal["LIMITED_PERMISSIONS", "FULL_PERMISSIONS"] | None = Field(default=None, validation_alias="actorPermissionLevel", serialization_alias="actorPermissionLevel", description="Specifies the permission level the Actor requires at runtime. Use LIMITED_PERMISSIONS for restricted access or FULL_PERMISSIONS for unrestricted platform access.", examples=['LIMITED_PERMISSIONS'])
    seo_title: str | None = Field(default=None, validation_alias="seoTitle", serialization_alias="seoTitle", description="The SEO-optimized title used for the Actor's page in Apify Store search results.", examples=['My actor'])
    seo_description: str | None = Field(default=None, validation_alias="seoDescription", serialization_alias="seoDescription", description="The SEO-optimized description used for the Actor's page in Apify Store search results.", examples=['My actor is the best'])
    title: str | None = Field(default=None, description="The display title shown for the Actor in Apify Store. Required when making the Actor public.", examples=['My Actor'])
    versions: list[CreateOrUpdateVersionRequest] | None = Field(default=None, description="An array of version objects defining the Actor's available versions and their source configurations. Order is not significant.")
    pricing_infos: list[PayPerEventActorPricingInfo | PricePerDatasetItemActorPricingInfo | FlatPricePerMonthActorPricingInfo | FreeActorPricingInfo] | None = Field(default=None, validation_alias="pricingInfos", serialization_alias="pricingInfos", description="An array of pricing information objects associated with the Actor. Order is not significant.")
    categories: list[str] | None = Field(default=None, description="An array of category identifiers under which the Actor is classified in Apify Store. Required when making the Actor public. Use constants from the apify-shared-js package.")
    tagged_builds: dict[str, BuildTag] | None = Field(default=None, validation_alias="taggedBuilds", serialization_alias="taggedBuilds", description="An object for managing build tags using a patch strategy — existing tags not included are preserved. Assign a tag by providing a buildId, or remove a tag by setting its value to null.")
    is_deprecated: bool | None = Field(default=None, validation_alias="isDeprecated", serialization_alias="isDeprecated", description="Whether the Actor is marked as deprecated, signaling to users that it should no longer be used.")
    default_run_options: ActPutRequestBodyDefaultRunOptions | None = Field(default=None, validation_alias="defaultRunOptions", serialization_alias="defaultRunOptions")
    actor_standby: ActPutRequestBodyActorStandby | None = Field(default=None, validation_alias="actorStandby", serialization_alias="actorStandby")
    example_run_input: ActPutRequestBodyExampleRunInput | None = Field(default=None, validation_alias="exampleRunInput", serialization_alias="exampleRunInput")
class ActPutRequest(StrictModel):
    """Updates the settings and configuration of an existing Actor by applying only the properties provided in the JSON request body. Returns the full updated Actor object after the changes are applied."""
    path: ActPutRequestPath
    body: ActPutRequestBody | None = None

# Operation: delete_actor
class ActDeleteRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique identifier of the Actor to delete, either as a standalone Actor ID or as a tilde-separated combination of the owner's username and Actor name.")
class ActDeleteRequest(StrictModel):
    """Permanently deletes the specified Actor and all associated data. This action is irreversible."""
    path: ActDeleteRequestPath

# Operation: list_actor_versions
class ActVersionsGetRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique identifier of the Actor, either as a standalone Actor ID or as a tilde-separated combination of the owner's username and Actor name.")
class ActVersionsGetRequest(StrictModel):
    """Retrieves all versions of a specific Actor, returning a list of Version objects with basic information about each version."""
    path: ActVersionsGetRequestPath

# Operation: create_actor_version
class ActVersionsPostRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique identifier of the Actor, either as an Actor ID or a tilde-separated combination of the owner's username and Actor name.")
class ActVersionsPostRequestBody(StrictModel):
    version_number: str | None = Field(default=None, validation_alias="versionNumber", serialization_alias="versionNumber", description="The semantic version number to assign to this Actor version, following a major.minor format.", examples=['0.0'])
    source_type: Literal["SOURCE_FILES", "GIT_REPO", "TARBALL", "GITHUB_GIST"] | None = Field(default=None, validation_alias="sourceType", serialization_alias="sourceType", description="Defines where the Actor's source code is hosted; must be one of the supported source types. Each value requires its own additional properties: SOURCE_FILES uses sourceFiles, GIT_REPO uses gitRepoUrl, TARBALL uses tarballUrl, and GITHUB_GIST uses gitHubGistUrl.")
    env_vars: list[EnvVar] | None = Field(default=None, validation_alias="envVars", serialization_alias="envVars", description="A list of environment variables to make available to the Actor at runtime and optionally during builds. Each item should specify the variable name and value.")
    apply_env_vars_to_build: bool | None = Field(default=None, validation_alias="applyEnvVarsToBuild", serialization_alias="applyEnvVarsToBuild", description="When set to true, the defined environment variables are also injected into the build process, not just runtime execution.", examples=[False])
    build_tag: str | None = Field(default=None, validation_alias="buildTag", serialization_alias="buildTag", description="A tag label applied to builds created from this version, used to reference or promote specific builds (e.g., marking a build as the latest stable release).", examples=['latest'])
    source_files: list[SourceCodeFile | SourceCodeFolder] | None = Field(default=None, validation_alias="sourceFiles", serialization_alias="sourceFiles", description="An array of source file objects representing the Actor's code when sourceType is SOURCE_FILES. Each item defines a file's name, content, and format.")
    git_repo_url: str | None = Field(default=None, validation_alias="gitRepoUrl", serialization_alias="gitRepoUrl", description="The URL of the Git repository containing the Actor's source code; required when sourceType is GIT_REPO.")
    tarball_url: str | None = Field(default=None, validation_alias="tarballUrl", serialization_alias="tarballUrl", description="The URL of a tarball archive containing the Actor's source code; required when sourceType is TARBALL.")
    git_hub_gist_url: str | None = Field(default=None, validation_alias="gitHubGistUrl", serialization_alias="gitHubGistUrl", description="The URL of a GitHub Gist containing the Actor's source code; required when sourceType is GITHUB_GIST.")
class ActVersionsPostRequest(StrictModel):
    """Creates a new version of an Actor by specifying a version number and source type along with the corresponding source details. The source type determines which additional properties are required (e.g., a Git repository URL for GIT_REPO, a tarball URL for TARBALL)."""
    path: ActVersionsPostRequestPath
    body: ActVersionsPostRequestBody | None = None

# Operation: get_actor_version
class ActVersionGetRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique identifier of the Actor, either as a standalone Actor ID or as a tilde-separated combination of the owner's username and Actor name.")
    version_number: str = Field(default=..., validation_alias="versionNumber", serialization_alias="versionNumber", description="The version number of the Actor to retrieve, following a major.minor versioning format.")
class ActVersionGetRequest(StrictModel):
    """Retrieves detailed information about a specific version of an Actor, including its configuration and metadata. Useful for inspecting the exact state of a particular Actor version."""
    path: ActVersionGetRequestPath

# Operation: update_actor_version
class ActVersionPutRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The Actor's unique ID or a tilde-separated combination of the owner's username and Actor name identifying which Actor to update.")
    version_number: str = Field(default=..., validation_alias="versionNumber", serialization_alias="versionNumber", description="The version number of the Actor to update, following major.minor versioning format.")
class ActVersionPutRequestBody(StrictModel):
    source_type: Literal["SOURCE_FILES", "GIT_REPO", "TARBALL", "GITHUB_GIST"] | None = Field(default=None, validation_alias="sourceType", serialization_alias="sourceType", description="Defines where the Actor's source code originates, which determines which of the source URL fields are required.")
    env_vars: list[EnvVar] | None = Field(default=None, validation_alias="envVars", serialization_alias="envVars", description="List of environment variables to make available to the Actor during execution and optionally during builds.")
    apply_env_vars_to_build: bool | None = Field(default=None, validation_alias="applyEnvVarsToBuild", serialization_alias="applyEnvVarsToBuild", description="When set to true, the defined environment variables are also injected into the build process, not just runtime execution.", examples=[False])
    build_tag: str | None = Field(default=None, validation_alias="buildTag", serialization_alias="buildTag", description="Tag label assigned to builds created from this version, used to reference the build when running the Actor.", examples=['latest'])
    source_files: list[SourceCodeFile | SourceCodeFolder] | None = Field(default=None, validation_alias="sourceFiles", serialization_alias="sourceFiles", description="Array of source file objects representing the Actor's code when sourceType is SOURCE_FILES; each item defines a file path and its content.")
    git_repo_url: str | None = Field(default=None, validation_alias="gitRepoUrl", serialization_alias="gitRepoUrl", description="The URL of the Git repository containing the Actor's source code; required when sourceType is GIT_REPO.")
    tarball_url: str | None = Field(default=None, validation_alias="tarballUrl", serialization_alias="tarballUrl", description="The URL of the tarball archive containing the Actor's source code; required when sourceType is TARBALL.")
    git_hub_gist_url: str | None = Field(default=None, validation_alias="gitHubGistUrl", serialization_alias="gitHubGistUrl", description="The URL of the GitHub Gist containing the Actor's source code; required when sourceType is GITHUB_GIST.")
class ActVersionPutRequest(StrictModel):
    """Updates a specific version of an Actor with the provided fields, leaving unspecified properties unchanged. Send a JSON payload with only the fields you want to modify."""
    path: ActVersionPutRequestPath
    body: ActVersionPutRequestBody | None = None

# Operation: delete_actor_version
class ActVersionDeleteRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique identifier of the Actor, either as a standalone Actor ID or as a tilde-separated combination of the owner's username and Actor name.")
    version_number: str = Field(default=..., validation_alias="versionNumber", serialization_alias="versionNumber", description="The version number of the Actor to delete, following major.minor versioning format.")
class ActVersionDeleteRequest(StrictModel):
    """Permanently deletes a specific version of an Actor's source code. This action is irreversible and removes the version along with its associated configuration."""
    path: ActVersionDeleteRequestPath

# Operation: list_actor_version_env_vars
class ActVersionEnvVarsGetRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique identifier of the Actor, either as an Actor ID or a tilde-separated combination of the owner's username and Actor name.")
    version_number: str = Field(default=..., validation_alias="versionNumber", serialization_alias="versionNumber", description="The version number of the Actor whose environment variables should be retrieved, following major.minor versioning format.")
class ActVersionEnvVarsGetRequest(StrictModel):
    """Retrieves all environment variables configured for a specific version of an Actor. Returns a list of environment variable objects, each containing the variable's key, value, and related metadata."""
    path: ActVersionEnvVarsGetRequestPath

# Operation: create_actor_env_var
class ActVersionEnvVarsPostRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique identifier of the Actor, either as an Actor ID or a tilde-separated combination of the owner's username and Actor name.")
    version_number: str = Field(default=..., validation_alias="versionNumber", serialization_alias="versionNumber", description="The version number of the Actor to which the environment variable will be added.")
class ActVersionEnvVarsPostRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the environment variable, typically uppercase with underscores following standard environment variable naming conventions.", examples=['MY_ENV_VAR'])
    value: str = Field(default=..., description="The value assigned to the environment variable.", examples=['my-value'])
    is_secret: bool | None = Field(default=None, validation_alias="isSecret", serialization_alias="isSecret", description="Indicates whether the environment variable should be treated as a secret, hiding its value from logs and the UI.", examples=[False])
class ActVersionEnvVarsPostRequest(StrictModel):
    """Creates a new environment variable for a specific version of an Actor. Requires a name and value, with an optional flag to mark the variable as secret."""
    path: ActVersionEnvVarsPostRequestPath
    body: ActVersionEnvVarsPostRequestBody

# Operation: get_actor_env_var
class ActVersionEnvVarGetRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique ID of the Actor, or a tilde-separated combination of the owner's username and Actor name.")
    version_number: str = Field(default=..., validation_alias="versionNumber", serialization_alias="versionNumber", description="The version number of the Actor to retrieve the environment variable from, following major.minor versioning format.")
    env_var_name: str = Field(default=..., validation_alias="envVarName", serialization_alias="envVarName", description="The exact name of the environment variable to retrieve, typically uppercase with underscores.")
class ActVersionEnvVarGetRequest(StrictModel):
    """Retrieves details of a specific environment variable for a given Actor version. If the variable is marked as secret, its value will be omitted from the response."""
    path: ActVersionEnvVarGetRequestPath

# Operation: update_actor_env_var
class ActVersionEnvVarPutRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique identifier of the Actor, either as an Actor ID or a tilde-separated combination of the owner's username and Actor name.")
    version_number: str = Field(default=..., validation_alias="versionNumber", serialization_alias="versionNumber", description="The version number of the Actor whose environment variable you want to update, in major.minor format.")
    env_var_name: str = Field(default=..., validation_alias="envVarName", serialization_alias="envVarName", description="The exact name of the environment variable to update, as it appears in the Actor version's configuration.")
class ActVersionEnvVarPutRequestBody(StrictModel):
    name: str = Field(default=..., description="The updated name for the environment variable, typically uppercase with underscores following standard environment variable naming conventions.", examples=['MY_ENV_VAR'])
    value: str = Field(default=..., description="The updated value to assign to the environment variable.", examples=['my-value'])
    is_secret: bool | None = Field(default=None, validation_alias="isSecret", serialization_alias="isSecret", description="Indicates whether the environment variable should be treated as a secret. Secret variables are encrypted at rest and masked in logs.", examples=[False])
class ActVersionEnvVarPutRequest(StrictModel):
    """Updates an existing environment variable for a specific Actor version. Only the properties included in the request body will be modified; omitted properties retain their current values."""
    path: ActVersionEnvVarPutRequestPath
    body: ActVersionEnvVarPutRequestBody

# Operation: delete_actor_version_env_var
class ActVersionEnvVarDeleteRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique identifier of the Actor, either as an Actor ID or a tilde-separated combination of the owner's username and Actor name.")
    version_number: str = Field(default=..., validation_alias="versionNumber", serialization_alias="versionNumber", description="The version number of the Actor from which the environment variable will be deleted, following major.minor versioning format.")
    env_var_name: str = Field(default=..., validation_alias="envVarName", serialization_alias="envVarName", description="The exact name of the environment variable to delete, typically uppercase with underscores as separators.")
class ActVersionEnvVarDeleteRequest(StrictModel):
    """Permanently deletes a specific environment variable from a given Actor version. This action cannot be undone."""
    path: ActVersionEnvVarDeleteRequestPath

# Operation: list_actor_webhooks
class ActWebhooksGetRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique identifier of the Actor, either as a standalone Actor ID or as a tilde-separated combination of the owner's username and Actor name.")
class ActWebhooksGetRequestQuery(StrictModel):
    offset: float | None = Field(default=None, description="Number of webhooks to skip from the beginning of the result set, used for paginating through records. Defaults to 0.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of webhooks to return in a single response. Accepts values between 1 and 1000, defaulting to 1000.", json_schema_extra={'format': 'double'})
    desc: bool | None = Field(default=None, description="When set to true, reverses the sort order so that the most recently created webhooks appear first instead of last.")
class ActWebhooksGetRequest(StrictModel):
    """Retrieves a paginated list of webhooks associated with a specific Actor, returning basic information about each webhook. Results are sorted by creation date ascending by default, with a maximum of 1000 records per request."""
    path: ActWebhooksGetRequestPath
    query: ActWebhooksGetRequestQuery | None = None

# Operation: list_actor_builds
class ActBuildsGetRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique identifier of the Actor, either as a plain Actor ID or in tilde-separated format combining the owner's username and Actor name.")
class ActBuildsGetRequestQuery(StrictModel):
    offset: float | None = Field(default=None, description="Number of build records to skip from the beginning of the result set, used for paginating through results. Defaults to 0.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of build records to return in a single response. Accepts values up to 1000, which is also the default.", json_schema_extra={'format': 'double'})
    desc: bool | None = Field(default=None, description="When set to true, sorts the returned builds by their start time in descending order (newest first). Defaults to ascending order.")
class ActBuildsGetRequest(StrictModel):
    """Retrieves a paginated list of builds for a specific Actor, with each record containing basic build information. Results are sorted by start time in ascending order by default, supporting incremental fetching as new builds are created."""
    path: ActBuildsGetRequestPath
    query: ActBuildsGetRequestQuery | None = None

# Operation: build_actor
class ActBuildsPostRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique ID of the Actor, or a tilde-separated string combining the owner's username and Actor name.")
class ActBuildsPostRequestQuery(StrictModel):
    version: str = Field(default=..., description="The Actor version number to build, corresponding to a version defined in the Actor's configuration.")
    use_cache: bool | None = Field(default=None, validation_alias="useCache", serialization_alias="useCache", description="When enabled, the build system reuses cached layers to speed up the build process; cache is disabled by default.")
    beta_packages: bool | None = Field(default=None, validation_alias="betaPackages", serialization_alias="betaPackages", description="When enabled, the Actor is built using beta versions of Apify NPM packages instead of the default latest stable versions.")
    tag: str | None = Field(default=None, description="A label applied to the build upon successful completion; if omitted, the tag defaults to the value set in the Actor version's buildTag property.")
    wait_for_finish: float | None = Field(default=None, validation_alias="waitForFinish", serialization_alias="waitForFinish", description="Number of seconds the server will wait for the build to complete before returning a response; must be between 0 and 60, where 0 returns immediately with a transitional status and higher values may return a terminal status if the build finishes in time.", json_schema_extra={'format': 'double'})
class ActBuildsPostRequest(StrictModel):
    """Triggers a new build for a specified Actor version, compiling its source code and dependencies into a runnable image. Returns the resulting build object, which may reflect a terminal or transitional status depending on wait time."""
    path: ActBuildsPostRequestPath
    query: ActBuildsPostRequestQuery

# Operation: get_default_actor_build
class ActBuildDefaultGetRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique identifier of the Actor, either as a standalone Actor ID or as a tilde-separated combination of the owner's username and Actor name.")
class ActBuildDefaultGetRequestQuery(StrictModel):
    wait_for_finish: float | None = Field(default=None, validation_alias="waitForFinish", serialization_alias="waitForFinish", description="Maximum number of seconds the server will wait for the build to finish before returning; if the build completes within this window the response will reflect a terminal status (e.g. SUCCEEDED), otherwise a transitional status (e.g. RUNNING) is returned. Accepts values from 0 (default, no wait) up to 60.", json_schema_extra={'format': 'double'})
class ActBuildDefaultGetRequest(StrictModel):
    """Retrieves the default build for a specified Actor, optionally waiting synchronously for the build to reach a terminal state. No authentication token is required, though unauthenticated requests will have certain usage cost fields omitted from the response."""
    path: ActBuildDefaultGetRequestPath
    query: ActBuildDefaultGetRequestQuery | None = None

# Operation: list_actor_runs_by_actor
class ActRunsGetRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique identifier of the Actor, either as an Actor ID or a tilde-separated combination of the owner's username and Actor name.")
class ActRunsGetRequestQuery(StrictModel):
    offset: float | None = Field(default=None, description="Number of runs to skip from the beginning of the result set, used for paginating through results.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of runs to return in a single response; cannot exceed 1000.", json_schema_extra={'format': 'double'})
    desc: bool | None = Field(default=None, description="When set to true, sorts runs by their start time in descending order (newest first); defaults to ascending order.")
    status: str | None = Field(default=None, description="Filters results to only include runs matching the specified status or comma-separated list of statuses (e.g., SUCCEEDED, FAILED, RUNNING).")
    started_after: str | None = Field(default=None, validation_alias="startedAfter", serialization_alias="startedAfter", description="Filters results to only include runs that started at or after this point in time, specified as an ISO 8601 datetime string in UTC.", json_schema_extra={'format': 'date-time'})
    started_before: str | None = Field(default=None, validation_alias="startedBefore", serialization_alias="startedBefore", description="Filters results to only include runs that started at or before this point in time, specified as an ISO 8601 datetime string in UTC.", json_schema_extra={'format': 'date-time'})
class ActRunsGetRequest(StrictModel):
    """Retrieves a paginated list of runs for a specific Actor, with each item containing basic run metadata. Supports filtering by status and start time, and sorting in ascending or descending order."""
    path: ActRunsGetRequestPath
    query: ActRunsGetRequestQuery | None = None

# Operation: run_actor
class ActRunsPostRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique ID of the Actor, or a tilde-separated combination of the owner's username and Actor name.")
class ActRunsPostRequestQuery(StrictModel):
    timeout: float | None = Field(default=None, description="Maximum duration the run is allowed to execute before being stopped, in seconds. Overrides the timeout configured in the Actor's settings.", json_schema_extra={'format': 'double'})
    memory: float | None = Field(default=None, description="Maximum RAM allocated to the run, in megabytes. Must be a power of 2 and at least 128 MB. Overrides the memory limit configured in the Actor's settings.", json_schema_extra={'format': 'double'})
    max_items: float | None = Field(default=None, validation_alias="maxItems", serialization_alias="maxItems", description="Maximum number of dataset items that will be billed for pay-per-result Actors. Does not cap the number of items returned — only limits charges. Accessible inside the Actor via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable.", json_schema_extra={'format': 'double'})
    max_total_charge_usd: float | None = Field(default=None, validation_alias="maxTotalChargeUsd", serialization_alias="maxTotalChargeUsd", description="Maximum total cost in USD allowed for the run, intended for pay-per-event Actors to cap charges. Accessible inside the Actor via the ACTOR_MAX_TOTAL_CHARGE_USD environment variable.", json_schema_extra={'format': 'double'})
    restart_on_error: bool | None = Field(default=None, validation_alias="restartOnError", serialization_alias="restartOnError", description="Whether the run should automatically restart if it encounters a failure.")
    build: str | None = Field(default=None, description="The specific Actor build to execute, specified as either a build tag or a build number. Defaults to the build defined in the Actor's configuration, typically the latest tag.")
    wait_for_finish: float | None = Field(default=None, validation_alias="waitForFinish", serialization_alias="waitForFinish", description="Number of seconds the server will wait for the run to finish before returning a response, between 0 and 60. If the run completes within this window, the response will reflect a terminal status such as SUCCEEDED; otherwise it will reflect a transitional status such as RUNNING.", json_schema_extra={'format': 'double'})
    force_permission_level: Literal["LIMITED_PERMISSIONS", "FULL_PERMISSIONS"] | None = Field(default=None, validation_alias="forcePermissionLevel", serialization_alias="forcePermissionLevel", description="Overrides the Actor's default permission level for this run only, useful for testing restricted or elevated access scenarios without permanently changing the Actor's configuration.")
    webhooks: str | None = Field(default=None, description="Specifies optional webhooks associated with the Actor run, which can be used to receive a notification\ne.g. when the Actor finished or failed. The value is a Base64-encoded\nJSON array of objects defining the webhooks. For more information, see\n[Webhooks documentation](https://docs.apify.com/platform/integrations/webhooks).\n")
class ActRunsPostRequestBody(StrictModel):
    body: dict[str, Any] | None = Field(default=None, description="The input payload passed to the Actor as INPUT, typically a JSON object. The Content-Type header of the request is forwarded alongside this body.", examples=[{'foo': 'bar'}])
class ActRunsPostRequest(StrictModel):
    """Starts an Actor run asynchronously and immediately returns a Run object without waiting for completion. Pass input data as the request body and use the returned run ID or defaultDatasetId to retrieve results later."""
    path: ActRunsPostRequestPath
    query: ActRunsPostRequestQuery | None = None
    body: ActRunsPostRequestBody | None = None

# Operation: run_actor_sync_no_input
class ActRunSyncGetRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique identifier of the Actor to run, either as an Actor ID or a tilde-separated combination of the owner's username and Actor name.")
class ActRunSyncGetRequestQuery(StrictModel):
    output_record_key: str | None = Field(default=None, validation_alias="outputRecordKey", serialization_alias="outputRecordKey", description="The key of the record from the run's default key-value store to return in the response. Defaults to OUTPUT if not specified.")
    timeout: float | None = Field(default=None, description="Maximum duration the run is allowed to execute, in seconds. If omitted, the timeout defined in the Actor's saved configuration is used.", json_schema_extra={'format': 'double'})
    memory: float | None = Field(default=None, description="Memory allocated for the run in megabytes; must be a power of 2 with a minimum of 128. If omitted, the memory limit from the Actor's saved configuration is used.", json_schema_extra={'format': 'double'})
    max_items: float | None = Field(default=None, validation_alias="maxItems", serialization_alias="maxItems", description="Maximum number of dataset items that will be charged for pay-per-result Actors; does not cap the actual items returned, only the billing ceiling. Accessible inside the Actor via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable.", json_schema_extra={'format': 'double'})
    max_total_charge_usd: float | None = Field(default=None, validation_alias="maxTotalChargeUsd", serialization_alias="maxTotalChargeUsd", description="Maximum total cost in USD allowed for the run, useful for capping charges on pay-per-event Actors. Accessible inside the Actor via the ACTOR_MAX_TOTAL_CHARGE_USD environment variable.", json_schema_extra={'format': 'double'})
    restart_on_error: bool | None = Field(default=None, validation_alias="restartOnError", serialization_alias="restartOnError", description="When set to true, the run will automatically restart if it encounters a failure. Defaults to false if not specified.")
    build: str | None = Field(default=None, description="Specifies which build of the Actor to execute, provided as either a build tag or a build number. Defaults to the build defined in the Actor's configuration, typically the latest tag.")
    webhooks: str | None = Field(default=None, description="Specifies optional webhooks associated with the Actor run, which can be used to receive a notification\ne.g. when the Actor finished or failed. The value is a Base64-encoded\nJSON array of objects defining the webhooks. For more information, see\n[Webhooks documentation](https://docs.apify.com/platform/integrations/webhooks).\n")
class ActRunSyncGetRequest(StrictModel):
    """Runs a specific Actor synchronously without input and returns its output directly in the response. The run must complete within 300 seconds; if it exceeds this limit or the connection breaks, a timeout error is returned."""
    path: ActRunSyncGetRequestPath
    query: ActRunSyncGetRequestQuery | None = None

# Operation: run_actor_sync
class ActRunSyncPostRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique identifier of the Actor to run, either as an Actor ID or a tilde-separated owner username and Actor name combination.")
class ActRunSyncPostRequestQuery(StrictModel):
    output_record_key: str | None = Field(default=None, validation_alias="outputRecordKey", serialization_alias="outputRecordKey", description="The key of the record from the run's default key-value store to return in the response. Defaults to OUTPUT if not specified.")
    timeout: float | None = Field(default=None, description="Maximum duration the Actor run is allowed to execute, in seconds. Overrides the timeout defined in the Actor's configuration.", json_schema_extra={'format': 'double'})
    memory: float | None = Field(default=None, description="Memory allocated for the Actor run, in megabytes. Must be a power of 2 with a minimum of 128 MB. Overrides the memory limit defined in the Actor's configuration.", json_schema_extra={'format': 'double'})
    max_items: float | None = Field(default=None, validation_alias="maxItems", serialization_alias="maxItems", description="Maximum number of dataset items that will be charged for pay-per-result Actors. Does not cap the number of items returned, only the number billed. Accessible inside the Actor via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable.", json_schema_extra={'format': 'double'})
    max_total_charge_usd: float | None = Field(default=None, validation_alias="maxTotalChargeUsd", serialization_alias="maxTotalChargeUsd", description="Maximum total cost in USD allowed for the run, useful for limiting charges on pay-per-event Actors. Accessible inside the Actor via the ACTOR_MAX_TOTAL_CHARGE_USD environment variable.", json_schema_extra={'format': 'double'})
    restart_on_error: bool | None = Field(default=None, validation_alias="restartOnError", serialization_alias="restartOnError", description="Whether the Actor run should automatically restart if it encounters a failure.")
    build: str | None = Field(default=None, description="The specific Actor build to execute, specified as either a build tag or build number. Defaults to the build defined in the Actor's configuration, typically the latest tag.")
    webhooks: str | None = Field(default=None, description="Specifies optional webhooks associated with the Actor run, which can be used to receive a notification\ne.g. when the Actor finished or failed. The value is a Base64-encoded\nJSON array of objects defining the webhooks. For more information, see\n[Webhooks documentation](https://docs.apify.com/platform/integrations/webhooks).\n")
class ActRunSyncPostRequestBody(StrictModel):
    body: dict[str, Any] | None = Field(default=None, description="The input payload passed to the Actor as its INPUT record. The Content-Type header of the request is forwarded alongside this body, typically as application/json.", examples=[{'foo': 'bar'}])
class ActRunSyncPostRequest(StrictModel):
    """Runs a specific Actor synchronously, passing the request body as INPUT, and returns the Actor's OUTPUT from its default key-value store. If the Actor run exceeds 300 seconds, the response will return a 408 timeout status."""
    path: ActRunSyncPostRequestPath
    query: ActRunSyncPostRequestQuery | None = None
    body: ActRunSyncPostRequestBody | None = None

# Operation: run_actor_sync_get_dataset_items
class ActRunSyncGetDatasetItemsGetRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique identifier of the Actor to run, either as an internal Actor ID or as a tilde-separated combination of the owner's username and Actor name.")
class ActRunSyncGetDatasetItemsGetRequestQuery(StrictModel):
    timeout: float | None = Field(default=None, description="Maximum duration the Actor run is allowed to execute before being forcibly stopped, in seconds. Overrides the timeout defined in the Actor's saved configuration.", json_schema_extra={'format': 'double'})
    memory: float | None = Field(default=None, description="Maximum RAM the Actor run may use, in megabytes. Must be a power of 2 and at least 128 MB. Overrides the memory limit defined in the Actor's saved configuration.", json_schema_extra={'format': 'double'})
    max_items: float | None = Field(default=None, validation_alias="maxItems", serialization_alias="maxItems", description="Maximum number of dataset items that will be billed for pay-per-result Actors. Does not cap the number of items returned — only limits charges. Accessible inside the Actor via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable.", json_schema_extra={'format': 'double'})
    max_total_charge_usd: float | None = Field(default=None, validation_alias="maxTotalChargeUsd", serialization_alias="maxTotalChargeUsd", description="Maximum total cost in USD that may be charged for this run, intended for pay-per-event Actors. Accessible inside the Actor via the ACTOR_MAX_TOTAL_CHARGE_USD environment variable.", json_schema_extra={'format': 'double'})
    restart_on_error: bool | None = Field(default=None, validation_alias="restartOnError", serialization_alias="restartOnError", description="When enabled, the Actor run will automatically restart if it encounters a failure, rather than terminating in an error state.")
    build: str | None = Field(default=None, description="Specifies which build of the Actor to execute, either by build tag or build number. Overrides the build defined in the Actor's saved configuration, which defaults to the latest tag.")
    format_: str | None = Field(default=None, validation_alias="format", serialization_alias="format", description="Output format for the returned dataset items. Supported values are json, jsonl, csv, html, xlsx, xml, and rss.")
    offset: float | None = Field(default=None, description="Number of dataset items to skip from the beginning of the result set before returning data. Useful for pagination.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of dataset items to include in the response. When omitted, all available items are returned.", json_schema_extra={'format': 'double'})
    fields: str | None = Field(default=None, description="Comma-separated list of field names to include in each returned item, excluding all other fields. Output fields are ordered to match the order specified in this list.")
    omit: str | None = Field(default=None, description="Comma-separated list of field names to exclude from each returned item. All other fields are retained.")
    unwind: str | None = Field(default=None, description="Comma-separated list of fields to unwind, processed in the specified order. Array fields produce one record per element merged with the parent; object fields are merged directly into the parent. Items with missing or non-unwindable fields are preserved as-is. Unwound items are not affected by the desc parameter.")
    flatten: str | None = Field(default=None, description="Comma-separated list of fields whose nested object values should be flattened into dot-notation keys on the parent object. The original nested object is replaced by its flattened representation.")
    desc: bool | None = Field(default=None, description="When set to true, reverses the order of returned items so the most recently stored items appear first. By default, items are returned in insertion order.")
    attachment: bool | None = Field(default=None, description="When set to true, adds a Content-Disposition: attachment header to the response, prompting browsers to download the result as a file rather than render it inline.")
    delimiter: str | None = Field(default=None, description="Single character used as the field delimiter in CSV output. Only applies when format is csv. Special characters should be URL-encoded (e.g., %09 for tab, %3B for semicolon). Defaults to a comma.")
    bom: bool | None = Field(default=None, description="Controls whether a UTF-8 Byte Order Mark (BOM) is prepended to the response. By default, BOM is included for CSV and omitted for json, jsonl, xml, html, and rss. Set to true to force inclusion or false to force omission.")
    xml_root: str | None = Field(default=None, validation_alias="xmlRoot", serialization_alias="xmlRoot", description="Overrides the name of the root XML element in xml-formatted output. Only applies when format is xml.")
    xml_row: str | None = Field(default=None, validation_alias="xmlRow", serialization_alias="xmlRow", description="Overrides the name of the element wrapping each individual record in xml-formatted output. Only applies when format is xml.")
    skip_header_row: bool | None = Field(default=None, validation_alias="skipHeaderRow", serialization_alias="skipHeaderRow", description="When set to true, omits the header row from csv-formatted output. Only applies when format is csv.")
    skip_hidden: bool | None = Field(default=None, validation_alias="skipHidden", serialization_alias="skipHidden", description="When set to true, excludes fields whose names begin with the # character from the output.")
    skip_empty: bool | None = Field(default=None, validation_alias="skipEmpty", serialization_alias="skipEmpty", description="When set to true, items with no fields or all-null values are excluded from the output. Note that the total number of returned items may be less than the specified limit when this is enabled.")
    simplified: bool | None = Field(default=None, description="When set to true, applies preset query parameters fields=url,pageFunctionResult,errorInfo and unwind=pageFunctionResult to emulate the simplified output format of the legacy Apify Crawler. Not recommended for new integrations.")
    skip_failed_pages: bool | None = Field(default=None, validation_alias="skipFailedPages", serialization_alias="skipFailedPages", description="When set to true, excludes all items that contain an errorInfo property from the output. Provided for compatibility with legacy Apify Crawler API v1 behavior. Not recommended for new integrations.")
    webhooks: str | None = Field(default=None, description="Specifies optional webhooks associated with the Actor run, which can be used to receive a notification\ne.g. when the Actor finished or failed. The value is a Base64-encoded\nJSON array of objects defining the webhooks. For more information, see\n[Webhooks documentation](https://docs.apify.com/platform/integrations/webhooks).\n")
class ActRunSyncGetDatasetItemsGetRequest(StrictModel):
    """Runs a specific Actor synchronously without input and returns its dataset items directly in the response. The Actor must complete within 300 seconds; if it exceeds this limit or the connection breaks, a timeout error is returned."""
    path: ActRunSyncGetDatasetItemsGetRequestPath
    query: ActRunSyncGetDatasetItemsGetRequestQuery | None = None

# Operation: run_actor_sync_get_dataset_items_with_input
class ActRunSyncGetDatasetItemsPostRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique ID of the Actor, or a tilde-separated combination of the owner's username and Actor name.")
class ActRunSyncGetDatasetItemsPostRequestQuery(StrictModel):
    timeout: float | None = Field(default=None, description="Maximum duration the Actor run is allowed to execute before being terminated, in seconds. Defaults to the timeout configured on the Actor itself.", json_schema_extra={'format': 'double'})
    memory: float | None = Field(default=None, description="Memory allocated to the Actor run in megabytes. Must be a power of 2 with a minimum of 128 MB. Defaults to the memory limit configured on the Actor.", json_schema_extra={'format': 'double'})
    max_items: float | None = Field(default=None, validation_alias="maxItems", serialization_alias="maxItems", description="Maximum number of dataset items that will be charged for pay-per-result Actors. Does not cap the number of items returned — only limits billing. Accessible inside the Actor via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable.", json_schema_extra={'format': 'double'})
    max_total_charge_usd: float | None = Field(default=None, validation_alias="maxTotalChargeUsd", serialization_alias="maxTotalChargeUsd", description="Maximum total cost in USD allowed for the run, intended for pay-per-event Actors to cap charges. Accessible inside the Actor via the ACTOR_MAX_TOTAL_CHARGE_USD environment variable.", json_schema_extra={'format': 'double'})
    restart_on_error: bool | None = Field(default=None, validation_alias="restartOnError", serialization_alias="restartOnError", description="When set to true, the Actor run will automatically restart if it encounters a failure.")
    build: str | None = Field(default=None, description="The specific Actor build to execute, specified as either a build tag or a build number. Defaults to the build configured on the Actor, typically the latest tag.")
    format_: str | None = Field(default=None, validation_alias="format", serialization_alias="format", description="Output format for the returned dataset items. Accepted values are json, jsonl, csv, html, xlsx, xml, and rss. Defaults to json.")
    offset: float | None = Field(default=None, description="Number of dataset items to skip from the beginning of the result set before returning data. Defaults to 0.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of dataset items to include in the response. When omitted, all available items are returned.", json_schema_extra={'format': 'double'})
    fields: str | None = Field(default=None, description="Comma-separated list of field names to include in each output record, excluding all other fields. Output fields are ordered according to the order specified in this list.")
    omit: str | None = Field(default=None, description="Comma-separated list of field names to exclude from each output record. All other fields are retained.")
    unwind: str | None = Field(default=None, description="Comma-separated list of fields to unwind, processed in the specified order. Array fields produce one record per element merged with the parent; object fields are merged directly into the parent. Items with missing or non-unwindable fields are preserved as-is.")
    flatten: str | None = Field(default=None, description="Comma-separated list of fields whose nested object values should be flattened into dot-notation keys on the parent object. The original nested object is replaced by its flattened representation.")
    desc: bool | None = Field(default=None, description="When set to true, reverses the order of returned items. By default, items are returned in the order they were stored.")
    delimiter: str | None = Field(default=None, description="Single character used as the field delimiter in CSV output; only applicable when format is csv. URL-encode special characters as needed. Defaults to a comma.")
    xml_root: str | None = Field(default=None, validation_alias="xmlRoot", serialization_alias="xmlRoot", description="Overrides the name of the root XML element in xml-formatted output. Defaults to items.")
    xml_row: str | None = Field(default=None, validation_alias="xmlRow", serialization_alias="xmlRow", description="Overrides the name of the element wrapping each individual record in xml-formatted output. Defaults to item.")
    skip_header_row: bool | None = Field(default=None, validation_alias="skipHeaderRow", serialization_alias="skipHeaderRow", description="When set to true, omits the header row from csv-formatted output.")
    skip_hidden: bool | None = Field(default=None, validation_alias="skipHidden", serialization_alias="skipHidden", description="When set to true, fields whose names begin with the # character are excluded from the output.")
    skip_empty: bool | None = Field(default=None, validation_alias="skipEmpty", serialization_alias="skipEmpty", description="When set to true, items with no fields or all-null values are excluded from the output. Note that the total number of returned items may be less than the specified limit when this option is active.")
    webhooks: str | None = Field(default=None, description="Specifies optional webhooks associated with the Actor run, which can be used to receive a notification\ne.g. when the Actor finished or failed. The value is a Base64-encoded\nJSON array of objects defining the webhooks. For more information, see\n[Webhooks documentation](https://docs.apify.com/platform/integrations/webhooks).\n")
class ActRunSyncGetDatasetItemsPostRequestBody(StrictModel):
    body: dict[str, Any] | None = Field(default=None, description="The input payload passed to the Actor as its INPUT, with the request's Content-Type header forwarded alongside it. Typically a JSON object.", examples=[{'foo': 'bar'}])
class ActRunSyncGetDatasetItemsPostRequest(StrictModel):
    """Runs a specific Actor synchronously with the provided input payload and returns the resulting dataset items directly in the response. Supports the same output formatting and filtering options as the Get Dataset Items endpoint; times out with HTTP 408 if the Actor run exceeds 300 seconds."""
    path: ActRunSyncGetDatasetItemsPostRequestPath
    query: ActRunSyncGetDatasetItemsPostRequestQuery | None = None
    body: ActRunSyncGetDatasetItemsPostRequestBody | None = None

# Operation: resurrect_actor_run
class ActRunResurrectPostRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The Actor's unique ID or a tilde-separated combination of the owner's username and Actor name identifying which Actor the run belongs to.")
    run_id: str = Field(default=..., validation_alias="runId", serialization_alias="runId", description="The unique ID of the finished Actor run to resurrect.")
class ActRunResurrectPostRequestQuery(StrictModel):
    build: str | None = Field(default=None, description="The Actor build to use for the resurrected run, specified as a build tag or build number. Defaults to the exact build version used when the run originally started, not the current resolution of any tag.")
    timeout: float | None = Field(default=None, description="Maximum duration the resurrected run is allowed to execute, in seconds. Defaults to the timeout value from the original run.", json_schema_extra={'format': 'double'})
    memory: float | None = Field(default=None, description="Memory allocated to the resurrected run in megabytes; must be a power of 2 and at least 128 MB. Defaults to the memory limit from the original run.", json_schema_extra={'format': 'double'})
    restart_on_error: bool | None = Field(default=None, validation_alias="restartOnError", serialization_alias="restartOnError", description="Whether the resurrected run should automatically restart if it encounters a failure. Defaults to the same setting used in the original run.")
class ActRunResurrectPostRequest(StrictModel):
    """Restarts a finished Actor run (with status FINISHED, FAILED, ABORTED, or TIMED-OUT), resuming execution with the same storages and updating its status back to RUNNING. Optionally override the build, timeout, memory, or error-restart behavior from the original run."""
    path: ActRunResurrectPostRequestPath
    query: ActRunResurrectPostRequestQuery | None = None

# Operation: get_last_actor_run
class ActRunsLastGetRequestPath(StrictModel):
    actor_id: str = Field(default=..., validation_alias="actorId", serialization_alias="actorId", description="The unique ID of the Actor, or a tilde-separated combination of the owner's username and Actor name.")
class ActRunsLastGetRequestQuery(StrictModel):
    status: str | None = Field(default=None, description="Filters the result to only return the last run matching the specified status, ensuring you retrieve a run in a particular state (e.g. only succeeded runs).")
class ActRunsLastGetRequest(StrictModel):
    """Retrieves the most recent run of a specified Actor, with optional filtering by run status. Also serves as the base path for accessing the last run's default storages (log, key-value store, dataset, and request queue) via sub-endpoints."""
    path: ActRunsLastGetRequestPath
    query: ActRunsLastGetRequestQuery | None = None

# Operation: list_tasks
class ActorTasksGetRequestQuery(StrictModel):
    offset: float | None = Field(default=None, description="Number of tasks to skip from the beginning of the result set, used for paginating through large lists.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of tasks to return in a single response, up to a maximum of 1000.", json_schema_extra={'format': 'double'})
    desc: bool | None = Field(default=None, description="When set to true, sorts tasks by creation date in descending order (newest first); defaults to ascending order (oldest first).")
class ActorTasksGetRequest(StrictModel):
    """Retrieves a paginated list of all actor tasks created or used by the authenticated user. Results are sorted by creation date and capped at 1000 records per request."""
    query: ActorTasksGetRequestQuery | None = None

# Operation: create_task
class ActorTasksPostRequestBody(StrictModel):
    body: ActorTasksPostBody | None = Field(default=None, description="JSON object defining the new task's configuration, including the actor to run, the task name, and execution options such as build version, timeout, and memory allocation.", examples=[{'actId': 'asADASadYvn4mBZmm', 'name': 'my-task', 'options': {'build': 'latest', 'timeoutSecs': 300, 'memoryMbytes': 128}}])
class ActorTasksPostRequest(StrictModel):
    """Creates a new actor task with the specified configuration, including the target actor, build version, timeout, and memory settings. Returns the full task object upon successful creation."""
    body: ActorTasksPostRequestBody | None = None

# Operation: get_task
class ActorTaskGetRequestPath(StrictModel):
    actor_task_id: str = Field(default=..., validation_alias="actorTaskId", serialization_alias="actorTaskId", description="The unique identifier of the task to retrieve, either as a standalone task ID or as a tilde-separated combination of the owner's username and the task's name.")
class ActorTaskGetRequest(StrictModel):
    """Retrieve full details of a specific actor task, including its configuration, settings, and metadata. Use this to inspect an existing task before running or modifying it."""
    path: ActorTaskGetRequestPath

# Operation: update_task
class ActorTaskPutRequestPath(StrictModel):
    actor_task_id: str = Field(default=..., validation_alias="actorTaskId", serialization_alias="actorTaskId", description="The unique identifier of the task to update, either as a task ID or a tilde-separated combination of the owner's username and task name.")
class ActorTaskPutRequestBodyOptions(StrictModel):
    build: str | None = Field(default=None, validation_alias="build", serialization_alias="build", description="The Actor build tag or version to use when running the task, such as a version tag or 'latest'.", examples=['latest'])
    timeout_secs: int | None = Field(default=None, validation_alias="timeoutSecs", serialization_alias="timeoutSecs", description="Maximum duration in seconds the task run is allowed to execute before it is forcefully stopped.", examples=[300])
    memory_mbytes: int | None = Field(default=None, validation_alias="memoryMbytes", serialization_alias="memoryMbytes", description="Amount of memory in megabytes allocated to each task run; must be a power of 2.", examples=[128])
    restart_on_error: bool | None = Field(default=None, validation_alias="restartOnError", serialization_alias="restartOnError", description="Whether the task run should automatically restart if it encounters an error during execution.", examples=[False])
    max_items: int | None = Field(default=None, validation_alias="maxItems", serialization_alias="maxItems", description="Maximum number of output dataset items the task is allowed to produce before the run is stopped.")
class ActorTaskPutRequestBodyActorStandby(StrictModel):
    build: str | None = Field(default=None, validation_alias="build", serialization_alias="build", description="The Actor build tag or version to use when the task is running in Standby mode.")
    memory_mbytes: int | None = Field(default=None, validation_alias="memoryMbytes", serialization_alias="memoryMbytes", description="Amount of memory in megabytes allocated to each task run when operating in Standby mode; must be a power of 2.")
    is_enabled: bool | None = Field(default=None, validation_alias="isEnabled", serialization_alias="isEnabled", description="Whether the task is enabled and available to be run; disabled tasks cannot be triggered.")
    desired_requests_per_actor_run: int | None = Field(default=None, validation_alias="desiredRequestsPerActorRun", serialization_alias="desiredRequestsPerActorRun", description="The target number of requests to process per Actor run when the task is operating in Standby mode.")
    max_requests_per_actor_run: int | None = Field(default=None, validation_alias="maxRequestsPerActorRun", serialization_alias="maxRequestsPerActorRun", description="The upper limit on the number of requests that can be processed per Actor run in Standby mode.")
    idle_timeout_secs: int | None = Field(default=None, validation_alias="idleTimeoutSecs", serialization_alias="idleTimeoutSecs", description="Duration in seconds the Standby Actor is allowed to remain idle before it is considered inactive and shut down.")
    disable_standby_fields_override: bool | None = Field(default=None, validation_alias="disableStandbyFieldsOverride", serialization_alias="disableStandbyFieldsOverride", description="When true, prevents task-level Standby field values from overriding the Actor's default Standby configuration.")
    should_pass_actor_input: bool | None = Field(default=None, validation_alias="shouldPassActorInput", serialization_alias="shouldPassActorInput", description="When true, the Actor's own input is passed through to the task run in addition to the task's configured input.")
class ActorTaskPutRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The URL-friendly name of the task, used to identify it within the owner's account.", examples=['my-task'])
    input_: dict[str, Any] | None = Field(default=None, validation_alias="input", serialization_alias="input", description="The user-defined JSON input configuration passed to the Actor when the task is executed; structure depends on the specific Actor's input schema.")
    title: str | None = Field(default=None, description="A human-readable display title for the task, distinct from its URL-friendly name.")
    options: ActorTaskPutRequestBodyOptions | None = None
    actor_standby: ActorTaskPutRequestBodyActorStandby | None = Field(default=None, validation_alias="actorStandby", serialization_alias="actorStandby")
class ActorTaskPutRequest(StrictModel):
    """Update the settings, input configuration, and runtime options of an existing Actor task. Only properties included in the request body are modified; omitted properties retain their current values."""
    path: ActorTaskPutRequestPath
    body: ActorTaskPutRequestBody | None = None

# Operation: delete_task
class ActorTaskDeleteRequestPath(StrictModel):
    actor_task_id: str = Field(default=..., validation_alias="actorTaskId", serialization_alias="actorTaskId", description="The unique identifier of the task to delete, either as a standalone task ID or as a tilde-separated combination of the owner's username and task name.")
class ActorTaskDeleteRequest(StrictModel):
    """Permanently deletes the specified actor task and all associated configuration. This action is irreversible and removes the task from the account."""
    path: ActorTaskDeleteRequestPath

# Operation: get_task_input
class ActorTaskInputGetRequestPath(StrictModel):
    actor_task_id: str = Field(default=..., validation_alias="actorTaskId", serialization_alias="actorTaskId", description="The unique identifier of the actor task, either as a standalone task ID or as a tilde-separated combination of the owner's username and the task's name.")
class ActorTaskInputGetRequest(StrictModel):
    """Retrieves the input configuration for a specified actor task. Returns the input object that defines the parameters passed to the actor when the task runs."""
    path: ActorTaskInputGetRequestPath

# Operation: update_task_input
class ActorTaskInputPutRequestPath(StrictModel):
    actor_task_id: str = Field(default=..., validation_alias="actorTaskId", serialization_alias="actorTaskId", description="The unique identifier of the actor task to update, either as a standalone task ID or as a tilde-separated combination of the owner's username and the task's name.")
class ActorTaskInputPutRequestBody(StrictModel):
    body: dict[str, Any] | None = Field(default=None, description="A JSON object containing the input fields to update on the task. Only the specified properties will be modified; any properties not included will remain unchanged.", examples=[{'myField2': 'updated-value'}])
class ActorTaskInputPutRequest(StrictModel):
    """Updates the input configuration of a specific actor task by merging the provided JSON object with the existing input. Only the properties included in the request body are updated; omitted properties retain their current values."""
    path: ActorTaskInputPutRequestPath
    body: ActorTaskInputPutRequestBody | None = None

# Operation: list_task_webhooks
class ActorTaskWebhooksGetRequestPath(StrictModel):
    actor_task_id: str = Field(default=..., validation_alias="actorTaskId", serialization_alias="actorTaskId", description="The unique identifier of the Actor task, either as a plain task ID or in tilde-separated format combining the owner's username and task name.")
class ActorTaskWebhooksGetRequestQuery(StrictModel):
    offset: float | None = Field(default=None, description="Number of webhooks to skip from the beginning of the result set, used for paginating through records. Defaults to 0.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of webhooks to return in a single response. Accepts values between 1 and 1000, with 1000 as both the default and upper limit.", json_schema_extra={'format': 'double'})
    desc: bool | None = Field(default=None, description="When set to true, reverses the sort order so that the most recently created webhooks appear first. By default, results are sorted by creation date in ascending order.")
class ActorTaskWebhooksGetRequest(StrictModel):
    """Retrieves a paginated list of webhooks associated with a specific Actor task. Results are sorted by creation date and capped at 1000 records per request."""
    path: ActorTaskWebhooksGetRequestPath
    query: ActorTaskWebhooksGetRequestQuery | None = None

# Operation: list_task_runs
class ActorTaskRunsGetRequestPath(StrictModel):
    actor_task_id: str = Field(default=..., validation_alias="actorTaskId", serialization_alias="actorTaskId", description="The unique identifier of the actor task, either as a task ID or a tilde-separated combination of the owner's username and task name.")
class ActorTaskRunsGetRequestQuery(StrictModel):
    offset: float | None = Field(default=None, description="Number of runs to skip from the beginning of the result set, used for paginating through results. Defaults to 0.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of runs to return in a single response. Accepts values between 1 and 1000, defaulting to 1000.", json_schema_extra={'format': 'double'})
    desc: bool | None = Field(default=None, description="When set to true, sorts runs by their start time in descending order (newest first). By default, runs are returned in ascending order.")
    status: str | None = Field(default=None, description="Filters results to only runs matching the specified status or comma-separated list of statuses. Valid statuses follow the Apify actor run lifecycle (e.g., SUCCEEDED, FAILED, RUNNING).")
class ActorTaskRunsGetRequest(StrictModel):
    """Retrieve a paginated list of runs for a specific actor task, including essential metadata for each run. Results can be filtered by status and sorted ascending or descending by start time."""
    path: ActorTaskRunsGetRequestPath
    query: ActorTaskRunsGetRequestQuery | None = None

# Operation: run_task
class ActorTaskRunsPostRequestPath(StrictModel):
    actor_task_id: str = Field(default=..., validation_alias="actorTaskId", serialization_alias="actorTaskId", description="The unique identifier of the task to run, either as a task ID or a tilde-separated string combining the owner's username and task name.")
class ActorTaskRunsPostRequestQuery(StrictModel):
    timeout: float | None = Field(default=None, description="Maximum duration the run is allowed to execute before being terminated, in seconds. Overrides the timeout defined in the task's configuration.", json_schema_extra={'format': 'double'})
    memory: float | None = Field(default=None, description="Maximum RAM allocated to the run, in megabytes. Must be a power of 2 with a minimum of 128. Overrides the memory limit defined in the task's configuration.", json_schema_extra={'format': 'double'})
    max_items: float | None = Field(default=None, validation_alias="maxItems", serialization_alias="maxItems", description="Maximum number of dataset items that will be billed for pay-per-result Actors. Does not cap the number of items returned — only limits charges. Accessible inside the Actor via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable.", json_schema_extra={'format': 'double'})
    max_total_charge_usd: float | None = Field(default=None, validation_alias="maxTotalChargeUsd", serialization_alias="maxTotalChargeUsd", description="Maximum total cost in USD allowed for the run, useful for capping charges on pay-per-event Actors. Accessible inside the Actor via the ACTOR_MAX_TOTAL_CHARGE_USD environment variable.", json_schema_extra={'format': 'double'})
    restart_on_error: bool | None = Field(default=None, validation_alias="restartOnError", serialization_alias="restartOnError", description="Whether the run should automatically restart if it encounters a failure. Defaults to false.")
    build: str | None = Field(default=None, description="The specific Actor build to execute, specified as either a build tag or a build number. Overrides the build defined in the task's configuration, which defaults to latest.")
    wait_for_finish: float | None = Field(default=None, validation_alias="waitForFinish", serialization_alias="waitForFinish", description="Number of seconds the server will wait for the run to finish before returning a response. Accepts values from 0 to 60; if the run completes within this window the response will reflect a terminal status, otherwise a transitional status such as RUNNING is returned.", json_schema_extra={'format': 'double'})
    webhooks: str | None = Field(default=None, description="Specifies optional webhooks associated with the Actor run, which can be used to receive a notification\ne.g. when the Actor finished or failed. The value is a Base64-encoded\nJSON array of objects defining the webhooks. For more information, see\n[Webhooks documentation](https://docs.apify.com/platform/integrations/webhooks).\n")
class ActorTaskRunsPostRequestBody(StrictModel):
    body: dict[str, Any] | None = Field(default=None, description="JSON object containing input properties to override the task's default input configuration. Any properties not included here will fall back to the task's or Actor's default values.", examples=[{'foo': 'bar'}])
class ActorTaskRunsPostRequest(StrictModel):
    """Starts an Actor task run asynchronously and immediately returns a run object without waiting for completion. Optionally override the task's input configuration via the request body, and use the returned run ID to poll for results or fetch dataset output."""
    path: ActorTaskRunsPostRequestPath
    query: ActorTaskRunsPostRequestQuery | None = None
    body: ActorTaskRunsPostRequestBody | None = None

# Operation: run_task_sync_get
class ActorTaskRunSyncGetRequestPath(StrictModel):
    actor_task_id: str = Field(default=..., validation_alias="actorTaskId", serialization_alias="actorTaskId", description="The unique identifier of the task to run, either as a task ID or a tilde-separated combination of the owner's username and task name.")
class ActorTaskRunSyncGetRequestQuery(StrictModel):
    timeout: float | None = Field(default=None, description="Maximum duration in seconds the run is allowed to execute before being timed out. If omitted, the timeout defined in the task's saved configuration is used.", json_schema_extra={'format': 'double'})
    memory: float | None = Field(default=None, description="Memory allocated to the run in megabytes; must be a power of 2 and at least 128 MB. If omitted, the memory limit from the task's saved configuration is used.", json_schema_extra={'format': 'double'})
    max_items: float | None = Field(default=None, validation_alias="maxItems", serialization_alias="maxItems", description="Maximum number of dataset items that will be billed for pay-per-result Actors; does not cap the actual items returned, only the charge. Applies exclusively to pay-per-result Actors and is exposed inside the run via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable.", json_schema_extra={'format': 'double'})
    build: str | None = Field(default=None, description="The Actor build to execute, specified as either a build tag or a build number. If omitted, the build defined in the task's saved configuration (typically 'latest') is used.")
    output_record_key: str | None = Field(default=None, validation_alias="outputRecordKey", serialization_alias="outputRecordKey", description="The key of the record in the run's default key-value store whose value will be returned as the response body. Defaults to 'OUTPUT' if not specified.")
    webhooks: str | None = Field(default=None, description="Specifies optional webhooks associated with the Actor run, which can be used to receive a notification\ne.g. when the Actor finished or failed. The value is a Base64-encoded\nJSON array of objects defining the webhooks. For more information, see\n[Webhooks documentation](https://docs.apify.com/platform/integrations/webhooks).\n")
class ActorTaskRunSyncGetRequest(StrictModel):
    """Runs a specific actor task synchronously and returns its output directly in the response. The task must complete within 300 seconds; if it exceeds this limit or the connection drops, the request fails but the underlying run continues."""
    path: ActorTaskRunSyncGetRequestPath
    query: ActorTaskRunSyncGetRequestQuery | None = None

# Operation: run_task_sync
class ActorTaskRunSyncPostRequestPath(StrictModel):
    actor_task_id: str = Field(default=..., validation_alias="actorTaskId", serialization_alias="actorTaskId", description="The unique identifier of the Actor task to run, either as a task ID or a tilde-separated combination of the owner's username and task name.")
class ActorTaskRunSyncPostRequestQuery(StrictModel):
    timeout: float | None = Field(default=None, description="Maximum duration the run is allowed to execute before being timed out, in seconds. Overrides the timeout defined in the task's configuration.", json_schema_extra={'format': 'double'})
    memory: float | None = Field(default=None, description="Memory allocated to the run, in megabytes. Must be a power of 2 with a minimum of 128 MB. Overrides the memory limit defined in the task's configuration.", json_schema_extra={'format': 'double'})
    max_items: float | None = Field(default=None, validation_alias="maxItems", serialization_alias="maxItems", description="Maximum number of dataset items that will be billed for pay-per-result Actors. Does not cap the number of items returned, only the number charged. Accessible inside the Actor via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable.", json_schema_extra={'format': 'double'})
    max_total_charge_usd: float | None = Field(default=None, validation_alias="maxTotalChargeUsd", serialization_alias="maxTotalChargeUsd", description="Maximum total cost in USD allowed for the run, intended for pay-per-event Actors to cap charges. Accessible inside the Actor via the ACTOR_MAX_TOTAL_CHARGE_USD environment variable.", json_schema_extra={'format': 'double'})
    restart_on_error: bool | None = Field(default=None, validation_alias="restartOnError", serialization_alias="restartOnError", description="Whether the run should automatically restart if it encounters a failure. Defaults to false.")
    build: str | None = Field(default=None, description="The specific Actor build to execute, specified as either a build tag or a build number. Defaults to the build defined in the task's configuration, typically the latest tag.")
    output_record_key: str | None = Field(default=None, validation_alias="outputRecordKey", serialization_alias="outputRecordKey", description="The key of the record in the run's default key-value store to return in the response body. Defaults to OUTPUT if not specified.")
    webhooks: str | None = Field(default=None, description="Specifies optional webhooks associated with the Actor run, which can be used to receive a notification\ne.g. when the Actor finished or failed. The value is a Base64-encoded\nJSON array of objects defining the webhooks. For more information, see\n[Webhooks documentation](https://docs.apify.com/platform/integrations/webhooks).\n")
class ActorTaskRunSyncPostRequestBody(StrictModel):
    body: dict[str, Any] | None = Field(default=None, description="A JSON object used to override specific input fields defined in the Actor task configuration. Any fields not included here will fall back to the task's default values. Requires the Content-Type header to be set to application/json.", examples=[{'foo': 'bar'}])
class ActorTaskRunSyncPostRequest(StrictModel):
    """Runs an Actor task synchronously and returns its output directly in the response. The task must complete within 300 seconds; optionally, you can override the task's default input by providing a JSON payload."""
    path: ActorTaskRunSyncPostRequestPath
    query: ActorTaskRunSyncPostRequestQuery | None = None
    body: ActorTaskRunSyncPostRequestBody | None = None

# Operation: run_task_sync_and_get_dataset_items
class ActorTaskRunSyncGetDatasetItemsGetRequestPath(StrictModel):
    actor_task_id: str = Field(default=..., validation_alias="actorTaskId", serialization_alias="actorTaskId", description="The unique identifier of the actor task to run, either as a task ID or a tilde-separated combination of the owner's username and task name.")
class ActorTaskRunSyncGetDatasetItemsGetRequestQuery(StrictModel):
    timeout: float | None = Field(default=None, description="Maximum duration in seconds the run is allowed to execute before being timed out. If omitted, the timeout defined in the task's saved configuration is used.", json_schema_extra={'format': 'double'})
    memory: float | None = Field(default=None, description="Memory allocated to the run in megabytes. Must be a power of 2 and at least 128 MB. If omitted, the memory limit from the task's saved configuration is used.", json_schema_extra={'format': 'double'})
    max_items: float | None = Field(default=None, validation_alias="maxItems", serialization_alias="maxItems", description="Maximum number of dataset items that will be charged for pay-per-result actors. Does not cap the number of items returned — only limits billing. Accessible inside the actor run via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable.", json_schema_extra={'format': 'double'})
    build: str | None = Field(default=None, description="The actor build to execute, specified as either a build tag or a build number. If omitted, the build defined in the task's saved configuration (typically 'latest') is used.")
    format_: str | None = Field(default=None, validation_alias="format", serialization_alias="format", description="Output format for the returned dataset items. Supported values are: json, jsonl, csv, html, xlsx, xml, and rss. Defaults to json if not specified.")
    offset: float | None = Field(default=None, description="Number of items to skip from the beginning of the dataset before returning results. Useful for pagination. Defaults to 0.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of items to include in the response. When omitted, all available items are returned without a cap.", json_schema_extra={'format': 'double'})
    fields: str | None = Field(default=None, description="Comma-separated list of field names to include in each returned item, excluding all other fields. Output fields are ordered to match the order specified in this list.")
    omit: str | None = Field(default=None, description="Comma-separated list of field names to exclude from each returned item. All other fields are retained in the output.")
    unwind: str | None = Field(default=None, description="Comma-separated list of fields to unwind, processed in the order specified. Array fields produce one record per element merged with the parent; object fields are merged directly into the parent. Items with missing or non-unwindable fields are preserved as-is. Unwound items are not affected by the desc parameter.")
    flatten: str | None = Field(default=None, description="Comma-separated list of fields whose nested object values should be flattened into dot-notation keys on the parent object. The original nested object is replaced by its flattened representation.")
    desc: bool | None = Field(default=None, description="When set to true, reverses the order of returned items so the most recently stored items appear first. By default items are returned in insertion order.")
    attachment: bool | None = Field(default=None, description="When set to true, adds a Content-Disposition: attachment header to the response, prompting browsers to download the result as a file rather than render it inline.")
    delimiter: str | None = Field(default=None, description="Field delimiter character used when format is csv. Special characters should be URL-encoded (e.g., %09 for tab, %3B for semicolon). Defaults to a comma.")
    bom: bool | None = Field(default=None, description="Controls inclusion of the UTF-8 Byte Order Mark (BOM) in the response. CSV files include the BOM by default; json, jsonl, xml, html, and rss do not. Set to true to force inclusion or false to force exclusion regardless of format.")
    xml_root: str | None = Field(default=None, validation_alias="xmlRoot", serialization_alias="xmlRoot", description="Overrides the name of the root XML element when format is xml. Defaults to 'items'.")
    xml_row: str | None = Field(default=None, validation_alias="xmlRow", serialization_alias="xmlRow", description="Overrides the name of the element wrapping each individual record when format is xml. Defaults to 'item'.")
    skip_header_row: bool | None = Field(default=None, validation_alias="skipHeaderRow", serialization_alias="skipHeaderRow", description="When set to true, omits the header row from csv output. Only applies when format is csv.")
    skip_hidden: bool | None = Field(default=None, validation_alias="skipHidden", serialization_alias="skipHidden", description="When set to true, excludes fields whose names begin with the '#' character from the output.")
    skip_empty: bool | None = Field(default=None, validation_alias="skipEmpty", serialization_alias="skipEmpty", description="When set to true, items with no fields or empty values are excluded from the output. Note that the total number of returned items may be less than the specified limit when this is enabled.")
    simplified: bool | None = Field(default=None, description="When set to true, automatically applies fields=url,pageFunctionResult,errorInfo and unwind=pageFunctionResult to emulate the legacy Apify Crawler simplified output format. Not recommended for new integrations.")
    skip_failed_pages: bool | None = Field(default=None, validation_alias="skipFailedPages", serialization_alias="skipFailedPages", description="When set to true, items containing an errorInfo property are excluded from the output. Provided for backward compatibility with legacy Apify Crawler integrations and not recommended for new integrations.")
    webhooks: str | None = Field(default=None, description="Specifies optional webhooks associated with the Actor run, which can be used to receive a notification\ne.g. when the Actor finished or failed. The value is a Base64-encoded\nJSON array of objects defining the webhooks. For more information, see\n[Webhooks documentation](https://docs.apify.com/platform/integrations/webhooks).\n")
class ActorTaskRunSyncGetDatasetItemsGetRequest(StrictModel):
    """Synchronously runs a specific actor task and returns its dataset items directly in the response. The task must complete within 300 seconds; if it exceeds this limit the request times out, though the underlying run continues executing."""
    path: ActorTaskRunSyncGetDatasetItemsGetRequestPath
    query: ActorTaskRunSyncGetDatasetItemsGetRequestQuery | None = None

# Operation: run_task_sync_get_dataset_items
class ActorTaskRunSyncGetDatasetItemsPostRequestPath(StrictModel):
    actor_task_id: str = Field(default=..., validation_alias="actorTaskId", serialization_alias="actorTaskId", description="The unique identifier of the Actor task to run, either as a task ID or a tilde-separated string combining the owner's username and task name.")
class ActorTaskRunSyncGetDatasetItemsPostRequestQuery(StrictModel):
    timeout: float | None = Field(default=None, description="Maximum duration in seconds the run is allowed to execute before being timed out. If not provided, the timeout defined in the task configuration is used.", json_schema_extra={'format': 'double'})
    memory: float | None = Field(default=None, description="Memory allocated to the run in megabytes. Must be a power of 2 and at least 128 MB. Defaults to the memory limit set in the task configuration.", json_schema_extra={'format': 'double'})
    max_items: float | None = Field(default=None, validation_alias="maxItems", serialization_alias="maxItems", description="Maximum number of dataset items that will be charged for pay-per-result Actors. Does not cap the number of items returned — only limits billing. Accessible inside the Actor via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable.", json_schema_extra={'format': 'double'})
    max_total_charge_usd: float | None = Field(default=None, validation_alias="maxTotalChargeUsd", serialization_alias="maxTotalChargeUsd", description="Maximum total cost in USD allowed for the run, intended for pay-per-event Actors to cap charges. Accessible inside the Actor via the ACTOR_MAX_TOTAL_CHARGE_USD environment variable.", json_schema_extra={'format': 'double'})
    restart_on_error: bool | None = Field(default=None, validation_alias="restartOnError", serialization_alias="restartOnError", description="When set to true, the run will automatically restart if it encounters a failure.")
    build: str | None = Field(default=None, description="Specifies which Actor build version to execute, provided as a build tag or build number. Defaults to the build defined in the task configuration, typically the latest tag.")
    format_: str | None = Field(default=None, validation_alias="format", serialization_alias="format", description="Output format for the returned dataset items. Supported values are json, jsonl, csv, html, xlsx, xml, and rss. Defaults to json.")
    offset: float | None = Field(default=None, description="Number of items to skip from the beginning of the dataset before returning results. Useful for pagination. Defaults to 0.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of items to include in the response. When omitted, all available items are returned.", json_schema_extra={'format': 'double'})
    fields: str | None = Field(default=None, description="Comma-separated list of field names to include in each returned item, excluding all other fields. Output fields are ordered according to the order specified in this list.")
    omit: str | None = Field(default=None, description="Comma-separated list of field names to exclude from each returned item. All other fields are retained.")
    unwind: str | None = Field(default=None, description="Comma-separated list of fields to unwind, processed in the specified order. Array fields produce one record per element merged with the parent; object fields are merged directly into the parent. Items with missing or non-unwindable fields are preserved as-is. Unwound items are not affected by the desc parameter.")
    flatten: str | None = Field(default=None, description="Comma-separated list of fields whose nested object values should be flattened into dot-notation keys on the parent object. The original nested object is replaced by the flattened representation.")
    desc: bool | None = Field(default=None, description="When set to true, results are returned in reverse order from how they were stored. Defaults to ascending (insertion) order.")
    delimiter: str | None = Field(default=None, description="Single character used as the field delimiter in CSV output. Only applicable when format is csv. URL-encode special characters as needed. Defaults to a comma.")
    xml_root: str | None = Field(default=None, validation_alias="xmlRoot", serialization_alias="xmlRoot", description="Overrides the name of the root XML element in xml format output. Defaults to items.")
    xml_row: str | None = Field(default=None, validation_alias="xmlRow", serialization_alias="xmlRow", description="Overrides the name of the element wrapping each individual record in xml format output. Defaults to item.")
    skip_header_row: bool | None = Field(default=None, validation_alias="skipHeaderRow", serialization_alias="skipHeaderRow", description="When set to true, omits the header row from csv format output.")
    skip_hidden: bool | None = Field(default=None, validation_alias="skipHidden", serialization_alias="skipHidden", description="When set to true, fields whose names begin with the # character are excluded from the output.")
    skip_empty: bool | None = Field(default=None, validation_alias="skipEmpty", serialization_alias="skipEmpty", description="When set to true, items with no fields or all-null values are excluded from the output. Note that the total number of returned items may be less than the specified limit when this option is active.")
class ActorTaskRunSyncGetDatasetItemsPostRequestBody(StrictModel):
    body: dict[str, Any] | None = Field(default=None, description="Optional JSON object to override specific input fields defined in the Actor task configuration. Fields not included in this payload retain their default values from the task or Actor input schema. Must be sent with Content-Type: application/json.", examples=[{'foo': 'bar'}])
class ActorTaskRunSyncGetDatasetItemsPostRequest(StrictModel):
    """Runs an Actor task synchronously and returns the resulting dataset items directly in the response. Optionally override task input via the POST body and control output format, pagination, and field selection through query parameters."""
    path: ActorTaskRunSyncGetDatasetItemsPostRequestPath
    query: ActorTaskRunSyncGetDatasetItemsPostRequestQuery | None = None
    body: ActorTaskRunSyncGetDatasetItemsPostRequestBody | None = None

# Operation: get_last_task_run
class ActorTaskRunsLastGetRequestPath(StrictModel):
    actor_task_id: str = Field(default=..., validation_alias="actorTaskId", serialization_alias="actorTaskId", description="The unique identifier of the actor task, either as a task ID or a tilde-separated combination of the owner's username and task name.")
class ActorTaskRunsLastGetRequestQuery(StrictModel):
    status: str | None = Field(default=None, description="Restricts the result to the last run matching the specified status, ensuring runs in other states are ignored.")
class ActorTaskRunsLastGetRequest(StrictModel):
    """Retrieves the most recent run of a specified actor task, with optional filtering by run status. Also serves as the base path for accessing the last run's default storages (log, key-value store, dataset, request queue) via sub-endpoints."""
    path: ActorTaskRunsLastGetRequestPath
    query: ActorTaskRunsLastGetRequestQuery | None = None

# Operation: list_actor_runs
class ActorRunsGetRequestQuery(StrictModel):
    offset: float | None = Field(default=None, description="Number of runs to skip from the beginning of the result set, used for pagination.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of runs to return per request; cannot exceed 1000.", json_schema_extra={'format': 'double'})
    desc: bool | None = Field(default=None, description="When set to true, sorts runs by their start time in descending order (newest first); defaults to ascending order.")
    status: str | None = Field(default=None, description="Filters results to only runs matching the given status or statuses; accepts a single status value or a comma-separated list of status values (e.g., SUCCEEDED, FAILED, RUNNING).")
    started_after: str | None = Field(default=None, validation_alias="startedAfter", serialization_alias="startedAfter", description="Filters results to only runs that started at or after this point in time; must be a valid ISO 8601 datetime string in UTC.", json_schema_extra={'format': 'date-time'})
    started_before: str | None = Field(default=None, validation_alias="startedBefore", serialization_alias="startedBefore", description="Filters results to only runs that started at or before this point in time; must be a valid ISO 8601 datetime string in UTC.", json_schema_extra={'format': 'date-time'})
class ActorRunsGetRequest(StrictModel):
    """Retrieves a paginated list of all Actor runs for the authenticated user, with each item containing basic run metadata. Supports filtering by status and start time, and sorting in ascending or descending order."""
    query: ActorRunsGetRequestQuery | None = None

# Operation: get_actor_run
class ActorRunGetRequestPath(StrictModel):
    run_id: str = Field(default=..., validation_alias="runId", serialization_alias="runId", description="The unique identifier of the Actor run to retrieve.")
class ActorRunGetRequestQuery(StrictModel):
    wait_for_finish: float | None = Field(default=None, validation_alias="waitForFinish", serialization_alias="waitForFinish", description="Maximum number of seconds the server will wait for the run to reach a terminal status before responding. Accepts values from 0 to 60; if the run finishes within the specified time the response will reflect its final status, otherwise it will reflect the current transitional status.", json_schema_extra={'format': 'double'})
class ActorRunGetRequest(StrictModel):
    """Retrieves all details about a specific Actor run, including its status, timing, and usage statistics. Optionally waits synchronously for the run to finish, eliminating the need for repeated polling."""
    path: ActorRunGetRequestPath
    query: ActorRunGetRequestQuery | None = None

# Operation: update_run
class ActorRunPutRequestPath(StrictModel):
    run_id: str = Field(default=..., validation_alias="runId", serialization_alias="runId", description="The unique identifier of the Actor run to update.")
class ActorRunPutRequestBody(StrictModel):
    body: ActorRunPutBody | None = Field(default=None, description="Request body containing the fields to update on the run. Supports setting a status message (with an optional terminal flag indicating it is the final message) and/or the general resource access level, which controls anonymous or restricted visibility of the run and its default storages and logs. Allowed access values are: FOLLOW_USER_SETTING, ANYONE_WITH_ID_CAN_READ, or RESTRICTED.", examples=[{'runId': '3KH8gEpp4d8uQSe8T', 'statusMessage': 'Actor has finished', 'isStatusMessageTerminal': True}])
class ActorRunPutRequest(StrictModel):
    """Updates an Actor run's status message and/or general resource access level. Use this to communicate progress to users via the Apify Console UI or to control who can view the run and its associated storages and logs."""
    path: ActorRunPutRequestPath
    body: ActorRunPutRequestBody | None = None

# Operation: delete_actor_run
class ActorRunDeleteRequestPath(StrictModel):
    run_id: str = Field(default=..., validation_alias="runId", serialization_alias="runId", description="The unique identifier of the actor run to delete. The run must be in a finished state before it can be deleted.")
class ActorRunDeleteRequest(StrictModel):
    """Permanently deletes a finished actor run. Only completed runs can be deleted, and only by the user or organization that initiated the run."""
    path: ActorRunDeleteRequestPath

# Operation: abort_run
class ActorRunAbortPostRequestPath(StrictModel):
    run_id: str = Field(default=..., validation_alias="runId", serialization_alias="runId", description="The unique identifier of the Actor run to abort.")
class ActorRunAbortPostRequestQuery(StrictModel):
    gracefully: bool | None = Field(default=None, description="When true, the run is aborted gracefully by sending 'aborting' and 'persistState' events before force-stopping after 30 seconds, which is useful if you intend to resurrect the run later.")
class ActorRunAbortPostRequest(StrictModel):
    """Aborts a currently starting or running Actor run, returning full run details. Runs already in a terminal state (FINISHED, FAILED, ABORTING, TIMED-OUT) are unaffected."""
    path: ActorRunAbortPostRequestPath
    query: ActorRunAbortPostRequestQuery | None = None

# Operation: metamorph_run
class ActorRunMetamorphPostRequestPath(StrictModel):
    run_id: str = Field(default=..., validation_alias="runId", serialization_alias="runId", description="The unique identifier of the Actor run to be transformed.")
class ActorRunMetamorphPostRequestQuery(StrictModel):
    target_actor_id: str = Field(default=..., validation_alias="targetActorId", serialization_alias="targetActorId", description="The unique identifier of the target Actor that this run should be transformed into.")
    build: str | None = Field(default=None, description="Specifies which build of the target Actor to use, either as a build tag or build number. Defaults to the build defined in the target Actor's default run configuration (typically `latest`).")
class ActorRunMetamorphPostRequest(StrictModel):
    """Transforms an active Actor run into a run of a different Actor with new input, seamlessly handing off work without creating a new run. The original run's default storages are preserved and the new input is stored in the same key-value store."""
    path: ActorRunMetamorphPostRequestPath
    query: ActorRunMetamorphPostRequestQuery

# Operation: reboot_actor_run
class ActorRunRebootPostRequestPath(StrictModel):
    run_id: str = Field(default=..., validation_alias="runId", serialization_alias="runId", description="The unique identifier of the Actor run to reboot. The run must currently have a RUNNING status.")
class ActorRunRebootPostRequest(StrictModel):
    """Reboots a currently running Actor run by restarting its container, returning the updated run details. Only runs with a RUNNING status can be rebooted; any data not persisted to a key-value store, dataset, or request queue will be lost."""
    path: ActorRunRebootPostRequestPath

# Operation: resurrect_run
class PostResurrectRunRequestPath(StrictModel):
    run_id: str = Field(default=..., validation_alias="runId", serialization_alias="runId", description="The unique identifier of the Actor run to resurrect.")
class PostResurrectRunRequestQuery(StrictModel):
    build: str | None = Field(default=None, description="The Actor build to use for the resurrected run, specified as a build tag (e.g. 'latest') or a build number. If omitted, the run restarts with the exact build version it originally executed, even if a tag like 'latest' now points to a newer build.")
    timeout: float | None = Field(default=None, description="Maximum duration the resurrected run is allowed to execute, in seconds. If omitted, the timeout from the original run is used.", json_schema_extra={'format': 'double'})
    memory: float | None = Field(default=None, description="Memory allocated to the resurrected run in megabytes; must be a power of 2 and at least 128 MB. If omitted, the memory limit from the original run is used.", json_schema_extra={'format': 'double'})
    max_items: float | None = Field(default=None, validation_alias="maxItems", serialization_alias="maxItems", description="Maximum number of dataset items that will be charged for pay-per-result Actors; does not cap the actual items returned, only the billable count. Accessible inside the Actor via the ACTOR_MAX_PAID_DATASET_ITEMS environment variable.", json_schema_extra={'format': 'double'})
    max_total_charge_usd: float | None = Field(default=None, validation_alias="maxTotalChargeUsd", serialization_alias="maxTotalChargeUsd", description="Maximum total cost in USD allowed for the resurrected run, intended for pay-per-event Actors to cap charges to your subscription. Accessible inside the Actor via the ACTOR_MAX_TOTAL_CHARGE_USD environment variable.", json_schema_extra={'format': 'double'})
    restart_on_error: bool | None = Field(default=None, validation_alias="restartOnError", serialization_alias="restartOnError", description="Whether the resurrected run should automatically restart if it encounters a failure. If omitted, the setting from the original run is preserved.")
class PostResurrectRunRequest(StrictModel):
    """Restarts a finished Actor run (with status FINISHED, FAILED, ABORTED, or TIMED-OUT) by restarting its container with the same storages, updating its status back to RUNNING. Optionally override the build, timeout, memory, and cost limits used for the resurrected run."""
    path: PostResurrectRunRequestPath
    query: PostResurrectRunRequestQuery | None = None

# Operation: charge_run_event
class PostChargeRunRequestPath(StrictModel):
    run_id: str = Field(default=..., validation_alias="runId", serialization_alias="runId", description="The unique identifier of the Actor run to charge events against.")
class PostChargeRunRequestBody(StrictModel):
    """Define which event, and how many times, you want to charge for."""
    event_name: str = Field(default=..., validation_alias="eventName", serialization_alias="eventName", description="The name of the billing event to charge for, which must exactly match one of the events configured in the Actor's pay-per-event settings.", examples=['ANALYZE_PAGE'])
    count: int = Field(default=..., description="The number of event occurrences to charge for in this request; must be a positive integer.", examples=[1])
class PostChargeRunRequest(StrictModel):
    """Charge for one or more occurrences of a configured pay-per-event (PPE) billing event within a specific Actor run. Must be called from within the Actor run using the same API token that started the run."""
    path: PostChargeRunRequestPath
    body: PostChargeRunRequestBody

# Operation: list_builds
class ActorBuildsGetRequestQuery(StrictModel):
    offset: float | None = Field(default=None, description="Number of builds to skip from the beginning of the result set, used for paginating through large result sets.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of builds to return in a single response, capped at 1000 records.", json_schema_extra={'format': 'double'})
    desc: bool | None = Field(default=None, description="When set to true, sorts builds by their start time in descending order (newest first); defaults to ascending order (oldest first).")
class ActorBuildsGetRequest(StrictModel):
    """Retrieves a paginated list of all builds for the authenticated user, with each entry containing basic build information. Records are sorted by start time and the endpoint returns a maximum of 1000 records per request."""
    query: ActorBuildsGetRequestQuery | None = None

# Operation: get_actor_build
class ActorBuildGetRequestPath(StrictModel):
    build_id: str = Field(default=..., validation_alias="buildId", serialization_alias="buildId", description="The unique identifier of the Actor build to retrieve.")
class ActorBuildGetRequestQuery(StrictModel):
    wait_for_finish: float | None = Field(default=None, validation_alias="waitForFinish", serialization_alias="waitForFinish", description="Maximum number of seconds the server will wait for the build to reach a terminal status before responding. Accepts values from 0 (default, return immediately) to 60. If the build finishes within the timeout, the response will reflect a terminal status such as SUCCEEDED; otherwise a transitional status such as RUNNING is returned.", json_schema_extra={'format': 'double'})
class ActorBuildGetRequest(StrictModel):
    """Retrieves full details about a specific Actor build, including its status, timing, and resource usage. Supports synchronous waiting via an optional timeout parameter to avoid polling when monitoring build completion."""
    path: ActorBuildGetRequestPath
    query: ActorBuildGetRequestQuery | None = None

# Operation: delete_build
class ActorBuildDeleteRequestPath(StrictModel):
    build_id: str = Field(default=..., validation_alias="buildId", serialization_alias="buildId", description="The unique identifier of the Actor build to delete, found in the build's Info tab.")
class ActorBuildDeleteRequest(StrictModel):
    """Permanently deletes a specific Actor build by its ID. The current default build for an Actor cannot be deleted; only users with build permissions for the Actor may perform this action."""
    path: ActorBuildDeleteRequestPath

# Operation: abort_build
class ActorBuildAbortPostRequestPath(StrictModel):
    build_id: str = Field(default=..., validation_alias="buildId", serialization_alias="buildId", description="The unique identifier of the Actor build to abort, available in the build's Info tab.")
class ActorBuildAbortPostRequest(StrictModel):
    """Aborts a running or starting Actor build, immediately halting execution and returning the build's full details. Builds already in a terminal state (FINISHED, FAILED, ABORTING, TIMED-OUT) are unaffected by this call."""
    path: ActorBuildAbortPostRequestPath

# Operation: get_build_log
class ActorBuildLogGetRequestPath(StrictModel):
    build_id: str = Field(default=..., validation_alias="buildId", serialization_alias="buildId", description="The unique identifier of the actor build whose log you want to retrieve.")
class ActorBuildLogGetRequestQuery(StrictModel):
    stream: bool | None = Field(default=None, description="When set to true, the response will stream log output continuously as long as the build is still running, rather than returning a static snapshot.")
class ActorBuildLogGetRequest(StrictModel):
    """Retrieves the log output for a specific actor build. Supports real-time log streaming while the build is in progress."""
    path: ActorBuildLogGetRequestPath
    query: ActorBuildLogGetRequestQuery | None = None

# Operation: list_key_value_stores
class KeyValueStoresGetRequestQuery(StrictModel):
    offset: float | None = Field(default=None, description="Number of stores to skip from the beginning of the result set, used for paginating through results.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of stores to return in a single response. Accepts values up to 1000.", json_schema_extra={'format': 'double'})
    desc: bool | None = Field(default=None, description="When set to true, reverses the sort order so that the most recently created stores appear first.")
    unnamed: bool | None = Field(default=None, description="When set to true, returns both named and unnamed stores. By default, only named stores are included in the response.")
    ownership: Literal["ownedByMe", "sharedWithMe"] | None = Field(default=None, description="Filters results by ownership relationship. Omitting this parameter returns all accessible stores regardless of ownership.", examples=['ownedByMe'])
class KeyValueStoresGetRequest(StrictModel):
    """Retrieves a paginated list of key-value stores accessible to the user, including basic metadata for each store. Results are sorted by creation date ascending by default, supporting incremental pagination as new stores are created."""
    query: KeyValueStoresGetRequestQuery | None = None

# Operation: create_key_value_store
class KeyValueStoresPostRequestQuery(StrictModel):
    name: str | None = Field(default=None, description="Optional unique name for the store, making it easy to identify and retrieve later. If omitted, an unnamed store is created and subject to the platform's data retention policy.")
class KeyValueStoresPostRequest(StrictModel):
    """Creates a new key-value store and returns its store object. If a store with the specified name already exists, the existing store is returned instead of creating a duplicate."""
    query: KeyValueStoresPostRequestQuery | None = None

# Operation: get_key_value_store
class KeyValueStoreGetRequestPath(StrictModel):
    store_id: str = Field(default=..., validation_alias="storeId", serialization_alias="storeId", description="The unique identifier of the key-value store to retrieve, either as a store ID or in the format username~store-name.")
class KeyValueStoreGetRequest(StrictModel):
    """Retrieves full details about a specific key-value store, including its configuration and metadata. Use this to inspect store properties before reading or writing data."""
    path: KeyValueStoreGetRequestPath

# Operation: update_key_value_store
class KeyValueStorePutRequestPath(StrictModel):
    store_id: str = Field(default=..., validation_alias="storeId", serialization_alias="storeId", description="The unique identifier of the key-value store to update, either as a store ID or in the format username~store-name.")
class KeyValueStorePutRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name to assign to the key-value store.")
    general_access: Literal["ANYONE_WITH_ID_CAN_READ", "ANYONE_WITH_NAME_CAN_READ", "FOLLOW_USER_SETTING", "RESTRICTED"] | None = Field(default=None, validation_alias="generalAccess", serialization_alias="generalAccess", description="The general access level for the key-value store, controlling who can read or interact with it. Use RESTRICTED to limit access, ANYONE_WITH_ID_CAN_READ or ANYONE_WITH_NAME_CAN_READ for broader read access, or FOLLOW_USER_SETTING to inherit the owner's default setting.", examples=['RESTRICTED'])
class KeyValueStorePutRequest(StrictModel):
    """Updates a key-value store's name and general access level using the provided JSON payload. Returns the updated store object reflecting the applied changes."""
    path: KeyValueStorePutRequestPath
    body: KeyValueStorePutRequestBody | None = None

# Operation: delete_key_value_store
class KeyValueStoreDeleteRequestPath(StrictModel):
    store_id: str = Field(default=..., validation_alias="storeId", serialization_alias="storeId", description="The unique identifier of the key-value store to delete, either as a store ID or in the format username~store-name.")
class KeyValueStoreDeleteRequest(StrictModel):
    """Permanently deletes a key-value store and all of its contents. This action is irreversible and removes the store along with all stored key-value pairs."""
    path: KeyValueStoreDeleteRequestPath

# Operation: list_key_value_store_keys
class KeyValueStoreKeysGetRequestPath(StrictModel):
    store_id: str = Field(default=..., validation_alias="storeId", serialization_alias="storeId", description="The unique identifier of the key-value store, either as a store ID or in the format username~store-name.")
class KeyValueStoreKeysGetRequestQuery(StrictModel):
    exclusive_start_key: str | None = Field(default=None, validation_alias="exclusiveStartKey", serialization_alias="exclusiveStartKey", description="Pagination cursor — all keys up to and including this key are excluded from the results, allowing you to retrieve the next page of keys.")
    limit: float | None = Field(default=None, description="Maximum number of keys to return in a single response. Must be between 1 and 1000.", json_schema_extra={'format': 'double'})
    collection: str | None = Field(default=None, description="Restricts results to keys belonging to a specific collection defined in the key-value store's schema. Requires the store to have a schema configured.")
    prefix: str | None = Field(default=None, description="Restricts results to keys that begin with the specified string prefix, useful for filtering logically grouped keys.")
class KeyValueStoreKeysGetRequest(StrictModel):
    """Retrieves a paginated list of keys from a specified key-value store, including metadata about each key's associated value such as size. Supports filtering by collection or key prefix."""
    path: KeyValueStoreKeysGetRequestPath
    query: KeyValueStoreKeysGetRequestQuery | None = None

# Operation: get_key_value_store_record
class KeyValueStoreRecordGetRequestPath(StrictModel):
    store_id: str = Field(default=..., validation_alias="storeId", serialization_alias="storeId", description="The unique identifier of the key-value store, either as a store ID or in the format username~store-name.")
    record_key: str = Field(default=..., validation_alias="recordKey", serialization_alias="recordKey", description="The key under which the record is stored in the key-value store.")
class KeyValueStoreRecordGetRequestQuery(StrictModel):
    attachment: bool | None = Field(default=None, description="When set to true, the response is served with a Content-Disposition: attachment header, prompting browsers to download the file rather than render it, and bypasses Apify's HTML security modifications to return raw content.")
class KeyValueStoreRecordGetRequest(StrictModel):
    """Retrieves the value stored under a specific key in a key-value store, returning the record with its original content type and encoding. Use the attachment parameter to fetch raw HTML content without Apify's security modifications."""
    path: KeyValueStoreRecordGetRequestPath
    query: KeyValueStoreRecordGetRequestQuery | None = None

# Operation: put_store_record
class KeyValueStoreRecordPutRequestPath(StrictModel):
    store_id: str = Field(default=..., validation_alias="storeId", serialization_alias="storeId", description="The unique identifier of the key-value store, either as a store ID or in the format username~store-name.")
    record_key: str = Field(default=..., validation_alias="recordKey", serialization_alias="recordKey", description="The key under which the value will be stored; must be unique within the store and is used to retrieve the record later.")
class KeyValueStoreRecordPutRequestBody(StrictModel):
    body: dict[str, Any] | None = Field(default=None, description="The value to store in the record; any data type or structure is supported, with the content type specified via the Content-Type request header.")
class KeyValueStoreRecordPutRequest(StrictModel):
    """Stores a value under a specific key in a key-value store, with the content type defined by the Content-Type header. Supports Gzip, Deflate, and Brotli compression via the Content-Encoding header to reduce payload size and improve upload speed."""
    path: KeyValueStoreRecordPutRequestPath
    body: KeyValueStoreRecordPutRequestBody | None = None

# Operation: delete_key_value_store_record
class KeyValueStoreRecordDeleteRequestPath(StrictModel):
    store_id: str = Field(default=..., validation_alias="storeId", serialization_alias="storeId", description="The unique identifier of the key-value store, either as a store ID or in the format username~store-name.")
    record_key: str = Field(default=..., validation_alias="recordKey", serialization_alias="recordKey", description="The key identifying the specific record to delete within the store.")
class KeyValueStoreRecordDeleteRequest(StrictModel):
    """Permanently removes a single record from a key-value store by its key. The store itself and all other records remain unaffected."""
    path: KeyValueStoreRecordDeleteRequestPath

# Operation: check_key_value_store_record_exists
class KeyValueStoreRecordHeadRequestPath(StrictModel):
    store_id: str = Field(default=..., validation_alias="storeId", serialization_alias="storeId", description="The unique identifier of the key-value store, either as a store ID or in the format username~store-name.")
    record_key: str = Field(default=..., validation_alias="recordKey", serialization_alias="recordKey", description="The key identifying the record to check for existence within the key-value store.")
class KeyValueStoreRecordHeadRequest(StrictModel):
    """Checks whether a record exists in a key-value store under a specific key without retrieving its value. Useful for lightweight existence checks before performing read or write operations."""
    path: KeyValueStoreRecordHeadRequestPath

# Operation: list_datasets
class DatasetsGetRequestQuery(StrictModel):
    offset: float | None = Field(default=None, description="Number of datasets to skip from the beginning of the result set, used for pagination. Defaults to 0.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of datasets to return in a single response. Accepts values up to 1000, which is also the default.", json_schema_extra={'format': 'double'})
    desc: bool | None = Field(default=None, description="When set to true, results are sorted by creation date in descending order (newest first). By default, results are sorted in ascending order.")
    unnamed: bool | None = Field(default=None, description="When set to true, both named and unnamed datasets are returned. By default, only named datasets are included in the response.")
    ownership: Literal["ownedByMe", "sharedWithMe"] | None = Field(default=None, description="Filters results by ownership relationship. Use 'ownedByMe' to return only datasets you own, or 'sharedWithMe' to return only datasets shared with you by others. Omit to return all accessible datasets.", examples=['ownedByMe'])
class DatasetsGetRequest(StrictModel):
    """Retrieves a paginated list of datasets accessible to the user, including basic metadata for each. Supports sorting, filtering by ownership, and optionally including unnamed datasets."""
    query: DatasetsGetRequestQuery | None = None

# Operation: create_dataset
class DatasetsPostRequestQuery(StrictModel):
    name: str | None = Field(default=None, description="Optional unique human-readable name for the dataset, allowing easy identification and retrieval in the future. If omitted, the dataset is unnamed and subject to the platform's data retention policy.")
class DatasetsPostRequest(StrictModel):
    """Creates a new dataset for storing structured data and returns its object. If a name is provided and a dataset with that name already exists, the existing dataset object is returned instead."""
    query: DatasetsPostRequestQuery | None = None

# Operation: get_dataset
class DatasetGetRequestPath(StrictModel):
    dataset_id: str = Field(default=..., validation_alias="datasetId", serialization_alias="datasetId", description="The unique identifier of the dataset, either as a standalone dataset ID or in the combined username~dataset-name format.")
class DatasetGetRequest(StrictModel):
    """Retrieves metadata and storage information for a specific dataset by its ID. Note that item count fields may lag up to 5 seconds behind actual data; use the list dataset items endpoint to retrieve the dataset's contents."""
    path: DatasetGetRequestPath

# Operation: update_dataset
class DatasetPutRequestPath(StrictModel):
    dataset_id: str = Field(default=..., validation_alias="datasetId", serialization_alias="datasetId", description="The unique identifier of the dataset to update, either as a standalone dataset ID or in the format username~dataset-name.")
class DatasetPutRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new display name to assign to the dataset.")
    general_access: Literal["ANYONE_WITH_ID_CAN_READ", "ANYONE_WITH_NAME_CAN_READ", "FOLLOW_USER_SETTING", "RESTRICTED"] | None = Field(default=None, validation_alias="generalAccess", serialization_alias="generalAccess", description="Controls who can access the dataset: restrict to specific users, allow anyone with the ID or name to read, or inherit from the user's default sharing setting.", examples=['RESTRICTED'])
class DatasetPutRequest(StrictModel):
    """Updates a dataset's name and general access level by dataset ID or username-scoped name. Returns the full updated dataset object."""
    path: DatasetPutRequestPath
    body: DatasetPutRequestBody | None = None

# Operation: delete_dataset
class DatasetDeleteRequestPath(StrictModel):
    dataset_id: str = Field(default=..., validation_alias="datasetId", serialization_alias="datasetId", description="The unique identifier of the dataset to delete, accepted either as a standalone dataset ID or as a combined username and dataset name in the format `username~dataset-name`.")
class DatasetDeleteRequest(StrictModel):
    """Permanently deletes a specific dataset and its associated data. This action is irreversible and removes the dataset from the account."""
    path: DatasetDeleteRequestPath

# Operation: list_dataset_items
class DatasetItemsGetRequestPath(StrictModel):
    dataset_id: str = Field(default=..., validation_alias="datasetId", serialization_alias="datasetId", description="The unique identifier of the dataset, either as a dataset ID or in the format `username~dataset-name`.")
class DatasetItemsGetRequestQuery(StrictModel):
    format_: str | None = Field(default=None, validation_alias="format", serialization_alias="format", description="Output format for the response. Structured formats (`json`, `jsonl`, `xml`) return raw item objects; tabular formats (`html`, `csv`, `xlsx`) return rows and columns limited to 2000 columns with column names up to 200 characters; `rss` returns an RSS feed. Defaults to `json`.")
    offset: float | None = Field(default=None, description="Number of items to skip from the beginning of the result set, used for pagination. Defaults to `0`.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of items to include in the response. When omitted, all available items are returned. Note that using `skipEmpty` may cause fewer items to be returned than this limit.", json_schema_extra={'format': 'double'})
    fields: str | None = Field(default=None, description="Comma-separated list of top-level field names to include in each output item; all other fields are dropped. The order of fields in the output matches the order specified here, which can be used to enforce a consistent output schema.")
    omit: str | None = Field(default=None, description="Comma-separated list of top-level field names to exclude from each output item; all other fields are retained.")
    unwind: str | None = Field(default=None, description="Comma-separated list of fields to unwind, processed in the specified order. Array fields are expanded so each element becomes a separate item merged with the parent object; object fields are merged directly into the parent. Items whose unwind field is missing or not an array/object are preserved unchanged. Unwound items are not affected by the `desc` ordering parameter.")
    flatten: str | None = Field(default=None, description="Comma-separated list of fields whose nested object values should be flattened into dot-notation keys on the parent object (e.g., `foo.bar`). The original nested object is replaced by the flattened representation.")
    desc: bool | None = Field(default=None, description="When set to `true` or `1`, reverses the sort order so items are returned from newest to oldest. By default items are returned in insertion order (oldest first). Note that this does not reverse the order of elements within unwound arrays.")
    delimiter: str | None = Field(default=None, description="Single character used as the field delimiter in CSV output; only applicable when `format=csv`. URL-encode special characters as needed (e.g., `%09` for tab, `%3B` for semicolon). Defaults to a comma.")
    xml_root: str | None = Field(default=None, validation_alias="xmlRoot", serialization_alias="xmlRoot", description="Overrides the name of the root XML element wrapping all results in XML output. Only applicable when `format=xml`. Defaults to `items`.")
    xml_row: str | None = Field(default=None, validation_alias="xmlRow", serialization_alias="xmlRow", description="Overrides the name of the XML element wrapping each individual item in XML output. Only applicable when `format=xml`. Defaults to `item`.")
    skip_header_row: bool | None = Field(default=None, validation_alias="skipHeaderRow", serialization_alias="skipHeaderRow", description="When set to `true` or `1`, omits the header row from CSV output. Only applicable when `format=csv`.")
    skip_hidden: bool | None = Field(default=None, validation_alias="skipHidden", serialization_alias="skipHidden", description="When set to `true` or `1`, excludes hidden fields (top-level fields whose names begin with `#`) from the output. Equivalent to enabling `clean`.")
    skip_empty: bool | None = Field(default=None, validation_alias="skipEmpty", serialization_alias="skipEmpty", description="When set to `true` or `1`, excludes empty items from the output. Be aware that the number of returned items may be less than the specified `limit` when this option is active.")
    view: str | None = Field(default=None, description="Name of a predefined view configuration defined in the dataset's schema, which controls how items are filtered and presented. Refer to the dataset schema documentation for how views are defined.")
class DatasetItemsGetRequest(StrictModel):
    """Retrieves items stored in a dataset, supporting multiple output formats (JSON, JSONL, XML, HTML, CSV, XLSX, RSS) with options for pagination, field filtering, sorting, and data transformation. Use this to export or inspect dataset contents produced by an Actor run."""
    path: DatasetItemsGetRequestPath
    query: DatasetItemsGetRequestQuery | None = None

# Operation: append_dataset_items
class DatasetItemsPostRequestPath(StrictModel):
    dataset_id: str = Field(default=..., validation_alias="datasetId", serialization_alias="datasetId", description="The unique identifier of the target dataset, either as a dataset ID or in the format username~dataset-name.")
class DatasetItemsPostRequestBody(StrictModel):
    body: list[PutItemsRequest] | None = Field(default=None, description="A single JSON object or an array of JSON objects to append to the dataset in order; total payload must not exceed 5 MB, so split larger arrays into smaller batches.")
class DatasetItemsPostRequest(StrictModel):
    """Appends one or more JSON objects to the end of the specified dataset. The entire request is rejected with a 400 error if any item fails schema validation; payloads must not exceed 5 MB."""
    path: DatasetItemsPostRequestPath
    body: DatasetItemsPostRequestBody | None = None

# Operation: get_dataset_statistics
class DatasetStatisticsGetRequestPath(StrictModel):
    dataset_id: str = Field(default=..., validation_alias="datasetId", serialization_alias="datasetId", description="The unique identifier of the dataset, either as a dataset ID or in the format username~dataset-name.")
class DatasetStatisticsGetRequest(StrictModel):
    """Retrieves field-level statistics for a specified dataset. Returns aggregated metrics such as value counts, null rates, and type distributions for each field in the dataset."""
    path: DatasetStatisticsGetRequestPath

# Operation: list_request_queues
class RequestQueuesGetRequestQuery(StrictModel):
    offset: float | None = Field(default=None, description="Number of queues to skip from the beginning of the result set, used for pagination. Defaults to 0.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of queues to return in a single response. Accepts values up to 1000, which is also the default.", json_schema_extra={'format': 'double'})
    desc: bool | None = Field(default=None, description="When set to true, reverses the sort order so queues are returned with the most recently created first instead of oldest first.")
    unnamed: bool | None = Field(default=None, description="When set to true, returns both named and unnamed queues. By default, only named queues are included in the results.")
    ownership: Literal["ownedByMe", "sharedWithMe"] | None = Field(default=None, description="Filters results by ownership relationship. Omitting this parameter returns all accessible queues, while specifying a value limits results to queues owned by the user or shared with them by others.", examples=['ownedByMe'])
class RequestQueuesGetRequest(StrictModel):
    """Retrieves a paginated list of the user's request queues, returning basic metadata for each. Results are sorted by creation date ascending by default, supporting incremental fetching as new queues are created."""
    query: RequestQueuesGetRequestQuery | None = None

# Operation: create_request_queue
class RequestQueuesPostRequestQuery(StrictModel):
    name: str | None = Field(default=None, description="Optional unique name for the request queue, allowing easy identification and retrieval in the future. If omitted, an unnamed queue is created and subject to data retention limits.")
class RequestQueuesPostRequest(StrictModel):
    """Creates a new request queue and returns its object, or returns the existing queue object if a queue with the given name already exists. Unnamed queues are subject to the platform's data retention policy."""
    query: RequestQueuesPostRequestQuery | None = None

# Operation: get_request_queue
class RequestQueueGetRequestPath(StrictModel):
    queue_id: str = Field(default=..., validation_alias="queueId", serialization_alias="queueId", description="The unique identifier of the request queue to retrieve. Accepts either the queue's ID or a combined username and queue name in the format username~queue-name.")
class RequestQueueGetRequest(StrictModel):
    """Retrieves metadata and configuration details for a specific request queue. Returns the full queue object including its properties and current state."""
    path: RequestQueueGetRequestPath

# Operation: update_request_queue
class RequestQueuePutRequestPath(StrictModel):
    queue_id: str = Field(default=..., validation_alias="queueId", serialization_alias="queueId", description="The unique identifier of the request queue to update, either as a queue ID or in the format username~queue-name.")
class RequestQueuePutRequestBody(StrictModel):
    body: RequestQueuePutBody | None = Field(default=None, description="JSON object containing the fields to update on the request queue, such as its name or general resource access level.", examples=[{'name': 'new-request-queue-name'}])
class RequestQueuePutRequest(StrictModel):
    """Updates a request queue's name and resource access level by submitting a JSON payload with the desired changes. Returns the full updated request queue object upon success."""
    path: RequestQueuePutRequestPath
    body: RequestQueuePutRequestBody | None = None

# Operation: delete_request_queue
class RequestQueueDeleteRequestPath(StrictModel):
    queue_id: str = Field(default=..., validation_alias="queueId", serialization_alias="queueId", description="The unique identifier of the request queue to delete, either as a queue ID or in the format username~queue-name.")
class RequestQueueDeleteRequest(StrictModel):
    """Permanently deletes a request queue and all its associated data. This action is irreversible and removes the queue identified by its ID or name."""
    path: RequestQueueDeleteRequestPath

# Operation: batch_add_requests
class RequestQueueRequestsBatchPostRequestPath(StrictModel):
    queue_id: str = Field(default=..., validation_alias="queueId", serialization_alias="queueId", description="The unique identifier of the target request queue, either as a queue ID or in the format username~queue-name.")
class RequestQueueRequestsBatchPostRequestQuery(StrictModel):
    client_key: str | None = Field(default=None, validation_alias="clientKey", serialization_alias="clientKey", description="A unique string identifier (1–32 characters) representing the calling client, used to detect whether the queue is being accessed by multiple clients simultaneously. Omitting this value causes the system to treat the call as originating from a new client.")
    forefront: str | None = Field(default=None, description="Controls whether each request in the batch is inserted at the front (head) or back (end) of the queue. Accepts a boolean string value; defaults to false, placing requests at the end.")
class RequestQueueRequestsBatchPostRequestBody(StrictModel):
    body: list[RequestDraft] | None = Field(default=None, description="An array of request objects to add to the queue, with a maximum of 25 items per batch. Each item should include the request details such as URL and uniqueKey; order within the array does not affect queue priority.")
class RequestQueueRequestsBatchPostRequest(StrictModel):
    """Adds up to 25 requests to a specified request queue in a single batch operation. Returns arrays of successfully processed and unprocessed requests, with unprocessed entries recommended for retry using exponential backoff."""
    path: RequestQueueRequestsBatchPostRequestPath
    query: RequestQueueRequestsBatchPostRequestQuery | None = None
    body: RequestQueueRequestsBatchPostRequestBody | None = None

# Operation: batch_delete_queue_requests
class RequestQueueRequestsBatchDeleteRequestPath(StrictModel):
    queue_id: str = Field(default=..., validation_alias="queueId", serialization_alias="queueId", description="The unique identifier of the request queue, either as a queue ID or in the format username~queue-name.")
class RequestQueueRequestsBatchDeleteRequestQuery(StrictModel):
    client_key: str | None = Field(default=None, validation_alias="clientKey", serialization_alias="clientKey", description="A unique string identifier (1–32 characters) representing the client accessing the queue, used to detect whether the queue has been accessed by multiple clients. If omitted, the system treats this call as originating from a new client.")
class RequestQueueRequestsBatchDeleteRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body, which must be set to application/json.")
class RequestQueueRequestsBatchDeleteRequestBody(StrictModel):
    body: list[RequestDraftDelete] | None = Field(default=None, description="An array of request objects to delete, each identified by either an ID or uniqueKey field. The batch is limited to 25 requests; order is not significant.")
class RequestQueueRequestsBatchDeleteRequest(StrictModel):
    """Batch-deletes up to 25 requests from a specified request queue, identified by their ID or uniqueKey. Any requests that fail due to rate limiting or internal errors are returned in the response for retry, with exponential backoff recommended."""
    path: RequestQueueRequestsBatchDeleteRequestPath
    query: RequestQueueRequestsBatchDeleteRequestQuery | None = None
    header: RequestQueueRequestsBatchDeleteRequestHeader
    body: RequestQueueRequestsBatchDeleteRequestBody | None = None

# Operation: unlock_queue_requests
class RequestQueueRequestsUnlockPostRequestPath(StrictModel):
    queue_id: str = Field(default=..., validation_alias="queueId", serialization_alias="queueId", description="The unique identifier of the request queue, either as a queue ID or in the format username~queue-name.")
class RequestQueueRequestsUnlockPostRequestQuery(StrictModel):
    client_key: str | None = Field(default=None, validation_alias="clientKey", serialization_alias="clientKey", description="A unique string identifier (1–32 characters) representing the client accessing the queue, used to track whether multiple clients have accessed the same queue. If omitted, the system treats the request as originating from a new client.")
class RequestQueueRequestsUnlockPostRequest(StrictModel):
    """Unlocks all currently locked requests in the specified request queue that are held by the calling client. Within an Actor run, this releases locks held by both the current run and the same clientKey; outside a run, it releases all locks associated with the provided clientKey."""
    path: RequestQueueRequestsUnlockPostRequestPath
    query: RequestQueueRequestsUnlockPostRequestQuery | None = None

# Operation: list_queue_requests
class RequestQueueRequestsGetRequestPath(StrictModel):
    queue_id: str = Field(default=..., validation_alias="queueId", serialization_alias="queueId", description="The unique identifier of the request queue, either as a queue ID or in the format username~queue-name.")
class RequestQueueRequestsGetRequestQuery(StrictModel):
    exclusive_start_id: str | None = Field(default=None, validation_alias="exclusiveStartId", serialization_alias="exclusiveStartId", description="Cursor for pagination — all requests up to and including this request ID are excluded from the results, returning only subsequent requests.")
    limit: float | None = Field(default=None, description="Maximum number of requests to return in a single response. Must be between 1 and 10000.", json_schema_extra={'format': 'double'})
class RequestQueueRequestsGetRequest(StrictModel):
    """Retrieves a paginated list of requests from a specified request queue. Use exclusiveStartId and limit to page through large queues efficiently."""
    path: RequestQueueRequestsGetRequestPath
    query: RequestQueueRequestsGetRequestQuery | None = None

# Operation: add_queue_request
class RequestQueueRequestsPostRequestPath(StrictModel):
    queue_id: str = Field(default=..., validation_alias="queueId", serialization_alias="queueId", description="The ID of the target request queue, or a combined identifier in the format username~queue-name.")
class RequestQueueRequestsPostRequestQuery(StrictModel):
    client_key: str | None = Field(default=None, validation_alias="clientKey", serialization_alias="clientKey", description="A unique string identifier (1–32 characters) representing the client making this request, used to detect whether the queue has been accessed by multiple clients.")
    forefront: str | None = Field(default=None, description="Controls where the request is inserted in the queue. Set to true to add at the front (head) of the queue, or false to append at the end. Defaults to false.")
class RequestQueueRequestsPostRequestBody(StrictModel):
    unique_key: str = Field(default=..., validation_alias="uniqueKey", serialization_alias="uniqueKey", description="A unique key used to deduplicate requests — requests sharing the same uniqueKey are treated as identical and will not be added twice.", examples=['GET|60d83e70|e3b0c442|https://apify.com'])
    url: str = Field(default=..., description="The fully qualified URL to be fetched or processed by this request, must be a valid URI.", json_schema_extra={'format': 'uri'}, examples=['https://apify.com'])
    method: str = Field(default=..., description="The HTTP method to use when executing this request (e.g., GET, POST, PUT, DELETE).", examples=['GET'])
class RequestQueueRequestsPostRequest(StrictModel):
    """Adds a new URL request to a specified request queue for processing. If a request with the same uniqueKey already exists in the queue, returns the ID of the existing request instead of creating a duplicate."""
    path: RequestQueueRequestsPostRequestPath
    query: RequestQueueRequestsPostRequestQuery | None = None
    body: RequestQueueRequestsPostRequestBody

# Operation: get_queue_request
class RequestQueueRequestGetRequestPath(StrictModel):
    queue_id: str = Field(default=..., validation_alias="queueId", serialization_alias="queueId", description="The unique identifier of the request queue, either as a queue ID or in the format username~queue-name.")
    request_id: str = Field(default=..., validation_alias="requestId", serialization_alias="requestId", description="The unique identifier of the request to retrieve from the specified queue.")
class RequestQueueRequestGetRequest(StrictModel):
    """Retrieves a specific request from a request queue by its ID. Returns the full request details including URL, metadata, and processing status."""
    path: RequestQueueRequestGetRequestPath

# Operation: update_queue_request
class RequestQueueRequestPutRequestPath(StrictModel):
    queue_id: str = Field(default=..., validation_alias="queueId", serialization_alias="queueId", description="The ID of the request queue, either as a direct queue ID or in the format `username~queue-name`.")
    request_id: str = Field(default=..., validation_alias="requestId", serialization_alias="requestId", description="The unique ID of the request to update within the queue.")
class RequestQueueRequestPutRequestQuery(StrictModel):
    forefront: str | None = Field(default=None, description="Controls whether the updated request is repositioned to the front of the queue (`true`) or remains at the end (`false`). Defaults to `false`.")
    client_key: str | None = Field(default=None, validation_alias="clientKey", serialization_alias="clientKey", description="A unique string identifier (1–32 characters) representing the client making this call, used to detect whether the queue is being accessed by multiple clients simultaneously.")
class RequestQueueRequestPutRequestBodyUserData(StrictModel):
    label: str | None = Field(default=None, validation_alias="label", serialization_alias="label", description="An optional label for categorizing or routing the request during processing.", examples=['DETAIL'])
    image: str | None = Field(default=None, validation_alias="image", serialization_alias="image", description="An optional URI pointing to an image associated with this request, must be a valid URI.", json_schema_extra={'format': 'uri'}, examples=['https://picserver1.eu'])
class RequestQueueRequestPutRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier assigned to this request object, used to reference it within the queue.", examples=['dnjkDMKLmdlkmlkmld'])
    unique_key: str = Field(default=..., validation_alias="uniqueKey", serialization_alias="uniqueKey", description="A unique key used to deduplicate requests; requests sharing the same key are treated as identical and will not be added more than once.", examples=['GET|60d83e70|e3b0c442|https://apify.com/career'])
    url: str = Field(default=..., description="The target URL for this request, must be a valid URI.", json_schema_extra={'format': 'uri'}, examples=['https://apify.com/career'])
    method: str | None = Field(default=None, description="The HTTP method to use when executing this request (e.g., GET, POST, PUT, DELETE).", examples=['GET'])
    payload: dict[str, Any] | None = Field(default=None, description="The body payload to send with the request, typically used for POST or PUT requests.")
    headers: dict[str, Any] | None = Field(default=None, description="A key-value map of HTTP headers to include when executing this request.")
    no_retry: bool | None = Field(default=None, validation_alias="noRetry", serialization_alias="noRetry", description="When set to `true`, prevents the request from being retried automatically if its processing fails.", examples=[False])
    user_data: RequestQueueRequestPutRequestBodyUserData | None = Field(default=None, validation_alias="userData", serialization_alias="userData")
class RequestQueueRequestPutRequest(StrictModel):
    """Updates an existing request in a queue, allowing you to modify its properties or mark it as handled. Setting `handledAt` to the current time removes the request from the head of the queue and releases any lock on it."""
    path: RequestQueueRequestPutRequestPath
    query: RequestQueueRequestPutRequestQuery | None = None
    body: RequestQueueRequestPutRequestBody

# Operation: delete_queue_request
class RequestQueueRequestDeleteRequestPath(StrictModel):
    queue_id: str = Field(default=..., validation_alias="queueId", serialization_alias="queueId", description="The unique identifier of the request queue, either as a queue ID or in the format username~queue-name.")
    request_id: str = Field(default=..., validation_alias="requestId", serialization_alias="requestId", description="The unique identifier of the request to delete from the queue.")
class RequestQueueRequestDeleteRequestQuery(StrictModel):
    client_key: str | None = Field(default=None, validation_alias="clientKey", serialization_alias="clientKey", description="A unique string (1–32 characters) identifying the client making this call, used to track whether the queue has been accessed by multiple clients. If omitted, the system treats this call as originating from a new client.")
class RequestQueueRequestDeleteRequest(StrictModel):
    """Permanently removes a specific request from a request queue by its ID. Use this to discard requests that are no longer needed for processing."""
    path: RequestQueueRequestDeleteRequestPath
    query: RequestQueueRequestDeleteRequestQuery | None = None

# Operation: get_request_queue_head
class RequestQueueHeadGetRequestPath(StrictModel):
    queue_id: str = Field(default=..., validation_alias="queueId", serialization_alias="queueId", description="The unique ID of the request queue, or a combined identifier in the format `username~queue-name`.")
class RequestQueueHeadGetRequestQuery(StrictModel):
    limit: float | None = Field(default=None, description="The maximum number of requests to return from the head of the queue. If omitted, a default limit is applied.", json_schema_extra={'format': 'double'})
    client_key: str | None = Field(default=None, validation_alias="clientKey", serialization_alias="clientKey", description="A unique string identifier (1–32 characters) representing the calling client, used to track whether the queue is being accessed by multiple clients. Omitting this value causes the system to treat the call as originating from a new, distinct client.")
class RequestQueueHeadGetRequest(StrictModel):
    """Retrieves the first N requests from the head of a request queue. Returns a `hadMultipleClients` flag indicating whether the queue has been accessed by more than one client, which helps SDKs determine local cache consistency."""
    path: RequestQueueHeadGetRequestPath
    query: RequestQueueHeadGetRequestQuery | None = None

# Operation: lock_queue_head_requests
class RequestQueueHeadLockPostRequestPath(StrictModel):
    queue_id: str = Field(default=..., validation_alias="queueId", serialization_alias="queueId", description="The unique identifier of the request queue, either as a queue ID or in the format username~queue-name.")
class RequestQueueHeadLockPostRequestQuery(StrictModel):
    lock_secs: float = Field(default=..., validation_alias="lockSecs", serialization_alias="lockSecs", description="The duration in seconds for which the retrieved requests will be locked and unavailable to other clients or runs.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="The maximum number of requests to retrieve from the head of the queue, between 1 and 25.", le=25, json_schema_extra={'format': 'double'})
    client_key: str | None = Field(default=None, validation_alias="clientKey", serialization_alias="clientKey", description="A unique string identifier (1–32 characters) representing the calling client, used to detect whether the queue is being accessed by multiple distinct clients. Omitting this value causes the system to treat the call as originating from a new client.")
class RequestQueueHeadLockPostRequest(StrictModel):
    """Retrieves and locks a specified number of requests from the head of a request queue, preventing other clients or runs from accessing them for the duration of the lock period. Returns a flag indicating whether the queue has been accessed by multiple clients."""
    path: RequestQueueHeadLockPostRequestPath
    query: RequestQueueHeadLockPostRequestQuery

# Operation: prolong_request_lock
class RequestQueueRequestLockPutRequestPath(StrictModel):
    queue_id: str = Field(default=..., validation_alias="queueId", serialization_alias="queueId", description="The unique identifier of the request queue, either as a queue ID or in the format username~queue-name.")
    request_id: str = Field(default=..., validation_alias="requestId", serialization_alias="requestId", description="The unique identifier of the request whose lock you want to prolong.")
class RequestQueueRequestLockPutRequestQuery(StrictModel):
    lock_secs: float = Field(default=..., validation_alias="lockSecs", serialization_alias="lockSecs", description="The number of seconds to extend the lock duration from the current time. Must be a positive value.", json_schema_extra={'format': 'double'})
    client_key: str | None = Field(default=None, validation_alias="clientKey", serialization_alias="clientKey", description="A unique string identifier (1–32 characters) representing the client accessing the queue. Must match the client key used when the request was originally locked in order to prolong or delete the lock.")
    forefront: str | None = Field(default=None, description="Controls where the request is placed in the queue after its lock expires — set to true to move it to the front of the queue, or false to place it at the end.")
class RequestQueueRequestLockPutRequest(StrictModel):
    """Extends the lock duration on a specific request in a queue, preventing other clients from acquiring it. Only the client that originally locked the request can prolong its lock."""
    path: RequestQueueRequestLockPutRequestPath
    query: RequestQueueRequestLockPutRequestQuery

# Operation: delete_request_lock
class RequestQueueRequestLockDeleteRequestPath(StrictModel):
    queue_id: str = Field(default=..., validation_alias="queueId", serialization_alias="queueId", description="The unique identifier of the request queue, either as a queue ID or in the format username~queue-name.")
    request_id: str = Field(default=..., validation_alias="requestId", serialization_alias="requestId", description="The unique identifier of the request whose lock should be deleted.")
class RequestQueueRequestLockDeleteRequestQuery(StrictModel):
    client_key: str | None = Field(default=None, validation_alias="clientKey", serialization_alias="clientKey", description="A unique string identifier (1–32 characters) representing the client releasing the lock. Must match the client key used when the lock was originally acquired.")
    forefront: str | None = Field(default=None, description="Controls where the request is re-inserted in the queue after the lock is removed — set to true to place it at the front of the queue, or false to append it to the end.")
class RequestQueueRequestLockDeleteRequestHeader(StrictModel):
    content_type: Literal["application/json"] = Field(default=..., validation_alias="Content-Type", serialization_alias="Content-Type", description="The media type of the request body, which must be application/json.")
class RequestQueueRequestLockDeleteRequest(StrictModel):
    """Releases a lock on a specific request in a queue, making it available for other clients to process. Only the client that originally locked the request (via the lock head operation) can delete its lock."""
    path: RequestQueueRequestLockDeleteRequestPath
    query: RequestQueueRequestLockDeleteRequestQuery | None = None
    header: RequestQueueRequestLockDeleteRequestHeader

# Operation: list_webhooks
class WebhooksGetRequestQuery(StrictModel):
    offset: float | None = Field(default=None, description="Number of records to skip from the beginning of the result set, used for paginating through results.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of webhook records to return in a single request, with an upper bound of 1000.", json_schema_extra={'format': 'double'})
    desc: bool | None = Field(default=None, description="When set to true, results are sorted by creation date in descending order (newest first); defaults to ascending order (oldest first).")
class WebhooksGetRequest(StrictModel):
    """Retrieves a paginated list of webhooks created by the authenticated user. Results are sorted by creation date and capped at 1000 records per request."""
    query: WebhooksGetRequestQuery | None = None

# Operation: create_webhook
class WebhooksPostRequestBodyCondition(StrictModel):
    actor_id: str | None = Field(default=None, validation_alias="actorId", serialization_alias="actorId", description="ID of the Actor to assign this webhook to. Provide inside the condition object along with optionally actorTaskId to scope the webhook to a specific Actor.", examples=['hksJZtadYvn4mBuin'])
    actor_task_id: str | None = Field(default=None, validation_alias="actorTaskId", serialization_alias="actorTaskId", description="ID of the Actor task to assign this webhook to. Provide inside the condition object to scope the webhook to a specific task run.", examples=['asdLZtadYvn4mBZmm'])
    actor_run_id: str | None = Field(default=None, validation_alias="actorRunId", serialization_alias="actorRunId", description="ID of a specific Actor run to associate with this webhook, used to scope the webhook to a particular run instance.", examples=['hgdKZtadYvn4mBpoi'])
class WebhooksPostRequestBody(StrictModel):
    is_ad_hoc: bool | None = Field(default=None, validation_alias="isAdHoc", serialization_alias="isAdHoc", description="When true, marks the webhook as ad-hoc (not permanently assigned to an Actor or task). Defaults to false for standard persistent webhooks.", examples=[False])
    event_types: list[Literal["ACTOR.BUILD.ABORTED", "ACTOR.BUILD.CREATED", "ACTOR.BUILD.FAILED", "ACTOR.BUILD.SUCCEEDED", "ACTOR.BUILD.TIMED_OUT", "ACTOR.RUN.ABORTED", "ACTOR.RUN.CREATED", "ACTOR.RUN.FAILED", "ACTOR.RUN.RESURRECTED", "ACTOR.RUN.SUCCEEDED", "ACTOR.RUN.TIMED_OUT", "TEST"]] = Field(default=..., validation_alias="eventTypes", serialization_alias="eventTypes", description="List of event types that will trigger this webhook. Each item must be a valid Apify event string (e.g., ACTOR.RUN.SUCCEEDED, ACTOR.RUN.FAILED, ACTOR.RUN.ABORTED). Order is not significant.", examples=[['ACTOR.RUN.SUCCEEDED']])
    idempotency_key: str | None = Field(default=None, validation_alias="idempotencyKey", serialization_alias="idempotencyKey", description="Unique key used to prevent duplicate webhook creation. Multiple requests with the same key will only create the webhook once and return the existing webhook on subsequent calls. Use a UUID or sufficiently random string.", examples=['fdSJmdP3nfs7sfk3y'])
    ignore_ssl_errors: bool | None = Field(default=None, validation_alias="ignoreSslErrors", serialization_alias="ignoreSslErrors", description="When true, SSL certificate errors on the target requestUrl will be ignored during webhook dispatch. Defaults to false.", examples=[False])
    do_not_retry: bool | None = Field(default=None, validation_alias="doNotRetry", serialization_alias="doNotRetry", description="When true, failed webhook dispatch attempts will not be retried. Defaults to false, meaning Apify will retry on failure.", examples=[False])
    request_url: str = Field(default=..., validation_alias="requestUrl", serialization_alias="requestUrl", description="The target URL to which webhook event data is sent as an HTTP POST request with a JSON payload. Must be a valid absolute URI.", json_schema_extra={'format': 'uri'}, examples=['http://example.com/'])
    payload_template: str | None = Field(default=None, validation_alias="payloadTemplate", serialization_alias="payloadTemplate", description="A JSON-like template string defining the payload sent to the requestUrl. Supports Apify template variables (e.g., {{userId}}, {{resource}}). If shouldInterpolateStrings is true, variables inside string values are also interpolated.", examples=['{\\n "userId": {{userId}}...'])
    headers_template: str | None = Field(default=None, validation_alias="headersTemplate", serialization_alias="headersTemplate", description="A JSON-like template string defining custom HTTP headers sent with the webhook request. Supports Apify template variables. Note: host, Content-Type, X-Apify-Webhook, X-Apify-Webhook-Dispatch-Id, and X-Apify-Request-Origin are always overwritten with defaults.", examples=['{\\n "Authorization": "Bearer ..."}'])
    description: str | None = Field(default=None, description="Optional human-readable label for the webhook to help identify its purpose.", examples=['this is webhook description'])
    should_interpolate_strings: bool | None = Field(default=None, validation_alias="shouldInterpolateStrings", serialization_alias="shouldInterpolateStrings", description="When true, Apify template variables found inside string values within the payloadTemplate are interpolated. When false, only top-level variable placeholders are replaced.", examples=[False])
    condition: WebhooksPostRequestBodyCondition | None = None
class WebhooksPostRequest(StrictModel):
    """Creates a new webhook that triggers HTTP POST requests to a target URL when specified Actor or task events occur. Use an idempotency key to safely retry creation without duplicating webhooks."""
    body: WebhooksPostRequestBody

# Operation: get_webhook
class WebhookGetRequestPath(StrictModel):
    webhook_id: str = Field(default=..., validation_alias="webhookId", serialization_alias="webhookId", description="The unique identifier of the webhook to retrieve.")
class WebhookGetRequest(StrictModel):
    """Retrieves full details of a specific webhook by its unique identifier. Returns all webhook configuration and metadata."""
    path: WebhookGetRequestPath

# Operation: update_webhook
class WebhookPutRequestPath(StrictModel):
    webhook_id: str = Field(default=..., validation_alias="webhookId", serialization_alias="webhookId", description="The unique identifier of the webhook to update.")
class WebhookPutRequestBodyCondition(StrictModel):
    actor_id: str | None = Field(default=None, validation_alias="actorId", serialization_alias="actorId", description="The ID of the Actor whose events should trigger this webhook. Scopes the webhook to a specific Actor.", examples=['hksJZtadYvn4mBuin'])
    actor_task_id: str | None = Field(default=None, validation_alias="actorTaskId", serialization_alias="actorTaskId", description="The ID of the Actor task whose events should trigger this webhook. Scopes the webhook to a specific task.", examples=['asdLZtadYvn4mBZmm'])
    actor_run_id: str | None = Field(default=None, validation_alias="actorRunId", serialization_alias="actorRunId", description="The ID of the Actor run whose events should trigger this webhook. Scopes the webhook to a specific run.", examples=['hgdKZtadYvn4mBpoi'])
class WebhookPutRequestBody(StrictModel):
    is_ad_hoc: bool | None = Field(default=None, validation_alias="isAdHoc", serialization_alias="isAdHoc", description="Indicates whether the webhook is ad hoc (created for a single run) rather than a persistent webhook.", examples=[False])
    event_types: list[Literal["ACTOR.BUILD.ABORTED", "ACTOR.BUILD.CREATED", "ACTOR.BUILD.FAILED", "ACTOR.BUILD.SUCCEEDED", "ACTOR.BUILD.TIMED_OUT", "ACTOR.RUN.ABORTED", "ACTOR.RUN.CREATED", "ACTOR.RUN.FAILED", "ACTOR.RUN.RESURRECTED", "ACTOR.RUN.SUCCEEDED", "ACTOR.RUN.TIMED_OUT", "TEST"]] | None = Field(default=None, validation_alias="eventTypes", serialization_alias="eventTypes", description="List of event types that trigger this webhook, such as actor run lifecycle events. Order is not significant; each item must be a valid event type string.", examples=[['ACTOR.RUN.SUCCEEDED']])
    ignore_ssl_errors: bool | None = Field(default=None, validation_alias="ignoreSslErrors", serialization_alias="ignoreSslErrors", description="When true, SSL certificate errors on the target request URL are ignored. Use with caution in production environments.", examples=[False])
    do_not_retry: bool | None = Field(default=None, validation_alias="doNotRetry", serialization_alias="doNotRetry", description="When true, failed webhook delivery attempts will not be retried automatically.", examples=[False])
    request_url: str | None = Field(default=None, validation_alias="requestUrl", serialization_alias="requestUrl", description="The destination URL to which the webhook will send HTTP POST requests when triggered. Must be a valid URI.", json_schema_extra={'format': 'uri'}, examples=['http://example.com/'])
    payload_template: str | None = Field(default=None, validation_alias="payloadTemplate", serialization_alias="payloadTemplate", description="A template string defining the JSON payload sent with each webhook request. Supports variable interpolation using double curly brace syntax.", examples=['{\\n "userId": {{userId}}...'])
    headers_template: str | None = Field(default=None, validation_alias="headersTemplate", serialization_alias="headersTemplate", description="A template string defining custom HTTP headers included with each webhook request. Supports variable interpolation using double curly brace syntax.", examples=['{\\n "Authorization": "Bearer ..."}'])
    description: str | None = Field(default=None, description="A human-readable description of the webhook's purpose or configuration for identification.", examples=['this is webhook description'])
    should_interpolate_strings: bool | None = Field(default=None, validation_alias="shouldInterpolateStrings", serialization_alias="shouldInterpolateStrings", description="When true, string values within the payload and headers templates will have variable placeholders interpolated before the request is sent.", examples=[False])
    condition: WebhookPutRequestBodyCondition | None = None
class WebhookPutRequest(StrictModel):
    """Updates an existing webhook's configuration by its ID, applying only the properties provided in the JSON request body. Returns the full updated webhook object."""
    path: WebhookPutRequestPath
    body: WebhookPutRequestBody | None = None

# Operation: delete_webhook
class WebhookDeleteRequestPath(StrictModel):
    webhook_id: str = Field(default=..., validation_alias="webhookId", serialization_alias="webhookId", description="The unique identifier of the webhook to delete.")
class WebhookDeleteRequest(StrictModel):
    """Permanently deletes a webhook by its unique identifier. This action is irreversible and will stop all event notifications associated with the webhook."""
    path: WebhookDeleteRequestPath

# Operation: test_webhook
class WebhookTestPostRequestPath(StrictModel):
    webhook_id: str = Field(default=..., validation_alias="webhookId", serialization_alias="webhookId", description="The unique identifier of the webhook to test.")
class WebhookTestPostRequest(StrictModel):
    """Sends a test dispatch to the specified webhook using a dummy payload. Useful for verifying that the webhook endpoint is correctly configured and reachable."""
    path: WebhookTestPostRequestPath

# Operation: list_webhook_dispatches_by_webhook
class WebhookWebhookDispatchesGetRequestPath(StrictModel):
    webhook_id: str = Field(default=..., validation_alias="webhookId", serialization_alias="webhookId", description="The unique identifier of the webhook whose dispatch history you want to retrieve.")
class WebhookWebhookDispatchesGetRequest(StrictModel):
    """Retrieves the list of dispatch records for a specific webhook, showing its delivery history and execution events."""
    path: WebhookWebhookDispatchesGetRequestPath

# Operation: list_webhook_dispatches
class WebhookDispatchesGetRequestQuery(StrictModel):
    offset: float | None = Field(default=None, description="Number of records to skip from the beginning of the result set, used for paginating through results. Defaults to 0.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of webhook dispatch records to return in a single response. Accepts values up to 1000, which is also the default.", json_schema_extra={'format': 'double'})
    desc: bool | None = Field(default=None, description="When set to true, sorts the returned records by the createdAt field in descending order (newest first). Defaults to ascending order.")
class WebhookDispatchesGetRequest(StrictModel):
    """Retrieves a paginated list of webhook dispatches associated with the authenticated user. Results are sorted by creation date and capped at 1000 records per request."""
    query: WebhookDispatchesGetRequestQuery | None = None

# Operation: get_webhook_dispatch
class WebhookDispatchGetRequestPath(StrictModel):
    dispatch_id: str = Field(default=..., validation_alias="dispatchId", serialization_alias="dispatchId", description="The unique identifier of the webhook dispatch record to retrieve.")
class WebhookDispatchGetRequest(StrictModel):
    """Retrieves a webhook dispatch record by its unique ID, returning full details about the dispatch event, status, and payload."""
    path: WebhookDispatchGetRequestPath

# Operation: list_schedules
class SchedulesGetRequestQuery(StrictModel):
    offset: float | None = Field(default=None, description="Number of schedules to skip from the beginning of the result set, used for paginating through records.", json_schema_extra={'format': 'double'})
    limit: float | None = Field(default=None, description="Maximum number of schedules to return in a single request, capped at 1000.", json_schema_extra={'format': 'double'})
    desc: bool | None = Field(default=None, description="When set to true, sorts the returned schedules by creation date in descending order instead of the default ascending order.")
class SchedulesGetRequest(StrictModel):
    """Retrieves a paginated list of schedules created by the user. Results are sorted by creation date ascending by default, with a maximum of 1000 records per request."""
    query: SchedulesGetRequestQuery | None = None

# Operation: create_schedule
class SchedulesPostRequestBody(StrictModel):
    name: str | None = Field(default=None, description="Unique identifier name for the schedule, used to reference it programmatically.", examples=['my-schedule'])
    is_enabled: bool | None = Field(default=None, validation_alias="isEnabled", serialization_alias="isEnabled", description="Controls whether the schedule is active and will trigger at its configured times. Set to false to create the schedule in a paused state.", examples=[True])
    is_exclusive: bool | None = Field(default=None, validation_alias="isExclusive", serialization_alias="isExclusive", description="When true, ensures only one run of this schedule executes at a time, preventing overlapping executions if a previous run is still in progress.", examples=[True])
    cron_expression: str | None = Field(default=None, validation_alias="cronExpression", serialization_alias="cronExpression", description="Defines the schedule's timing using standard cron syntax (minute, hour, day-of-month, month, day-of-week).", examples=['* * * * *'])
    timezone_: str | None = Field(default=None, validation_alias="timezone", serialization_alias="timezone", description="IANA timezone name used to interpret the cron expression, ensuring the schedule fires at the correct local time.", examples=['UTC'])
    description: str | None = Field(default=None, description="Human-readable explanation of the schedule's purpose, useful for documentation and identifying what the schedule does.", examples=['Schedule of actor ...'])
    title: str | None = Field(default=None, description="Display-friendly label for the schedule shown in the UI, distinct from the programmatic name.")
    actions: list[ScheduleCreateActions] | None = Field(default=None, description="List of actions to execute when the schedule triggers. Each item defines an action type and its configuration; order determines execution sequence.")
class SchedulesPostRequest(StrictModel):
    """Creates a new schedule with the specified configuration, including timing, timezone, and associated actions. Returns the fully created schedule object upon success."""
    body: SchedulesPostRequestBody | None = None

# Operation: get_schedule
class ScheduleGetRequestPath(StrictModel):
    schedule_id: str = Field(default=..., validation_alias="scheduleId", serialization_alias="scheduleId", description="The unique identifier of the schedule to retrieve.")
class ScheduleGetRequest(StrictModel):
    """Retrieves a schedule object with all associated details by its unique identifier. Use this to inspect scheduling configuration, timing, and related metadata for a specific schedule."""
    path: ScheduleGetRequestPath

# Operation: update_schedule
class SchedulePutRequestPath(StrictModel):
    schedule_id: str = Field(default=..., validation_alias="scheduleId", serialization_alias="scheduleId", description="The unique identifier of the schedule to update.")
class SchedulePutRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A short machine-friendly identifier for the schedule, typically used for referencing it programmatically.", examples=['my-schedule'])
    is_enabled: bool | None = Field(default=None, validation_alias="isEnabled", serialization_alias="isEnabled", description="Whether the schedule is active and will trigger its actions at the defined times. Set to false to pause the schedule without deleting it.", examples=[True])
    is_exclusive: bool | None = Field(default=None, validation_alias="isExclusive", serialization_alias="isExclusive", description="Whether the schedule runs exclusively, preventing overlapping executions if a previous run is still in progress when the next trigger fires.", examples=[True])
    cron_expression: str | None = Field(default=None, validation_alias="cronExpression", serialization_alias="cronExpression", description="The cron expression defining when the schedule triggers, using standard five-field cron syntax (minute, hour, day-of-month, month, day-of-week).", examples=['* * * * *'])
    timezone_: str | None = Field(default=None, validation_alias="timezone", serialization_alias="timezone", description="The IANA timezone name used to interpret the cron expression, ensuring triggers fire at the correct local time.", examples=['UTC'])
    description: str | None = Field(default=None, description="A human-readable explanation of the schedule's purpose or context, useful for documentation and identification.", examples=['Schedule of actor ...'])
    title: str | None = Field(default=None, description="A human-friendly display name for the schedule, intended for presentation in UIs or dashboards.")
    actions: list[ScheduleCreateActions] | None = Field(default=None, description="An ordered list of action objects that the schedule will execute when triggered. Each item defines the type and configuration of an action to perform.")
class SchedulePutRequest(StrictModel):
    """Updates an existing schedule by its ID, applying only the properties provided in the request body while leaving unspecified properties unchanged. Returns the full updated schedule object."""
    path: SchedulePutRequestPath
    body: SchedulePutRequestBody | None = None

# Operation: delete_schedule
class ScheduleDeleteRequestPath(StrictModel):
    schedule_id: str = Field(default=..., validation_alias="scheduleId", serialization_alias="scheduleId", description="The unique identifier of the schedule to delete.")
class ScheduleDeleteRequest(StrictModel):
    """Permanently deletes a schedule by its unique identifier. This action cannot be undone."""
    path: ScheduleDeleteRequestPath

# Operation: get_schedule_log
class ScheduleLogGetRequestPath(StrictModel):
    schedule_id: str = Field(default=..., validation_alias="scheduleId", serialization_alias="scheduleId", description="The unique identifier of the schedule whose invocation log you want to retrieve.")
class ScheduleLogGetRequest(StrictModel):
    """Retrieves the execution log for a specific schedule, returning a JSON array of up to 1000 recent invocation records. Useful for auditing schedule activity and diagnosing execution history."""
    path: ScheduleLogGetRequestPath

# Operation: list_store_actors
class StoreGetRequestQuery(StrictModel):
    limit: float | None = Field(default=None, description="Maximum number of Actors to return in a single response. Accepts values up to 1,000.", json_schema_extra={'format': 'double'})
    offset: float | None = Field(default=None, description="Number of Actors to skip from the beginning of the result set, used for paginating through results.", json_schema_extra={'format': 'double'})
    search: str | None = Field(default=None, description="Keyword or phrase used to search Actors across their title, name, description, username, and readme fields.")
    sort_by: str | None = Field(default=None, validation_alias="sortBy", serialization_alias="sortBy", description="Field by which to sort the returned Actors. Supported values are relevance (default), popularity, newest, and lastUpdate.")
    category: str | None = Field(default=None, description="Filters results to only include Actors belonging to the specified category.")
    username: str | None = Field(default=None, description="Filters results to only include Actors published by the specified username.")
    pricing_model: Literal["FREE", "FLAT_PRICE_PER_MONTH", "PRICE_PER_DATASET_ITEM", "PAY_PER_EVENT"] | None = Field(default=None, validation_alias="pricingModel", serialization_alias="pricingModel", description="Filters results to only include Actors with the specified pricing model. Must be one of the supported pricing model values.")
    allows_agentic_users: bool | None = Field(default=None, validation_alias="allowsAgenticUsers", serialization_alias="allowsAgenticUsers", description="When true, restricts results to Actors that permit agentic users; when false, restricts results to Actors that do not permit agentic users.")
class StoreGetRequest(StrictModel):
    """Retrieves the list of publicly available Actors from the Apify Store, with support for keyword search, filtering, and sorting. Returns up to 1,000 results and supports pagination."""
    query: StoreGetRequestQuery | None = None

# Operation: get_run_log
class LogGetRequestPath(StrictModel):
    build_or_run_id: str = Field(default=..., validation_alias="buildOrRunId", serialization_alias="buildOrRunId", description="The unique identifier of the Actor build or run whose logs you want to retrieve.")
class LogGetRequestQuery(StrictModel):
    stream: bool | None = Field(default=None, description="When set to true, the response streams log output continuously while the build or run is still active, rather than returning a static snapshot.")
    raw: bool | None = Field(default=None, description="When set to true, logs are returned verbatim including ANSI escape codes. By default, ANSI escape codes are stripped and only printable characters are returned.")
class LogGetRequest(StrictModel):
    """Retrieves the log output for a specific Actor build or run. Supports real-time streaming for active runs and optional preservation of raw ANSI escape codes."""
    path: LogGetRequestPath
    query: LogGetRequestQuery | None = None

# Operation: get_user
class UserGetRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The unique identifier or username of the user whose public profile data should be retrieved.")
class UserGetRequest(StrictModel):
    """Retrieves public profile information for a specific user account, equivalent to what is visible on their public profile page. No authentication is required to call this endpoint."""
    path: UserGetRequestPath

# Operation: get_monthly_usage
class UsersMeUsageMonthlyGetRequestQuery(StrictModel):
    date: str | None = Field(default=None, description="The date within the billing cycle you want to retrieve usage for, in YYYY-MM-DD format. If omitted, the current billing cycle is returned.")
class UsersMeUsageMonthlyGetRequest(StrictModel):
    """Retrieves a complete summary of your usage for the current or a specified billing cycle, including storage, data transfer, and request queue usage with both an overall total and a daily breakdown."""
    query: UsersMeUsageMonthlyGetRequestQuery | None = None

# ============================================================================
# Component Models
# ============================================================================

class ActorChargeEvent(PermissiveModel):
    event_price_usd: float = Field(..., validation_alias="eventPriceUsd", serialization_alias="eventPriceUsd")
    event_title: str = Field(..., validation_alias="eventTitle", serialization_alias="eventTitle")
    event_description: str = Field(..., validation_alias="eventDescription", serialization_alias="eventDescription")

class ActorRunPutBody(PermissiveModel):
    run_id: str | None = Field(None, validation_alias="runId", serialization_alias="runId")
    status_message: str | None = Field(None, validation_alias="statusMessage", serialization_alias="statusMessage")
    is_status_message_terminal: bool | None = Field(None, validation_alias="isStatusMessageTerminal", serialization_alias="isStatusMessageTerminal")
    general_access: Literal["ANYONE_WITH_ID_CAN_READ", "ANYONE_WITH_NAME_CAN_READ", "FOLLOW_USER_SETTING", "RESTRICTED"] | None = Field(None, validation_alias="generalAccess", serialization_alias="generalAccess", description="Defines the general access level for the resource.")

class ActorStandby(PermissiveModel):
    is_enabled: bool | None = Field(None, validation_alias="isEnabled", serialization_alias="isEnabled")
    desired_requests_per_actor_run: int | None = Field(None, validation_alias="desiredRequestsPerActorRun", serialization_alias="desiredRequestsPerActorRun")
    max_requests_per_actor_run: int | None = Field(None, validation_alias="maxRequestsPerActorRun", serialization_alias="maxRequestsPerActorRun")
    idle_timeout_secs: int | None = Field(None, validation_alias="idleTimeoutSecs", serialization_alias="idleTimeoutSecs")
    build: str | None = None
    memory_mbytes: int | None = Field(None, validation_alias="memoryMbytes", serialization_alias="memoryMbytes")
    disable_standby_fields_override: bool | None = Field(None, validation_alias="disableStandbyFieldsOverride", serialization_alias="disableStandbyFieldsOverride")
    should_pass_actor_input: bool | None = Field(None, validation_alias="shouldPassActorInput", serialization_alias="shouldPassActorInput")

class ActorStats(PermissiveModel):
    total_builds: int | None = Field(None, validation_alias="totalBuilds", serialization_alias="totalBuilds")
    total_runs: int | None = Field(None, validation_alias="totalRuns", serialization_alias="totalRuns")
    total_users: int | None = Field(None, validation_alias="totalUsers", serialization_alias="totalUsers")
    total_users7_days: int | None = Field(None, validation_alias="totalUsers7Days", serialization_alias="totalUsers7Days")
    total_users30_days: int | None = Field(None, validation_alias="totalUsers30Days", serialization_alias="totalUsers30Days")
    total_users90_days: int | None = Field(None, validation_alias="totalUsers90Days", serialization_alias="totalUsers90Days")
    total_metamorphs: int | None = Field(None, validation_alias="totalMetamorphs", serialization_alias="totalMetamorphs")
    last_run_started_at: str | None = Field(None, validation_alias="lastRunStartedAt", serialization_alias="lastRunStartedAt", json_schema_extra={'format': 'date-time'})

class ActorTasksPostBodyActorStandby(PermissiveModel):
    is_enabled: bool | None = Field(None, validation_alias="isEnabled", serialization_alias="isEnabled")
    desired_requests_per_actor_run: int | None = Field(None, validation_alias="desiredRequestsPerActorRun", serialization_alias="desiredRequestsPerActorRun")
    max_requests_per_actor_run: int | None = Field(None, validation_alias="maxRequestsPerActorRun", serialization_alias="maxRequestsPerActorRun")
    idle_timeout_secs: int | None = Field(None, validation_alias="idleTimeoutSecs", serialization_alias="idleTimeoutSecs")
    build: str | None = None
    memory_mbytes: int | None = Field(None, validation_alias="memoryMbytes", serialization_alias="memoryMbytes")
    disable_standby_fields_override: bool | None = Field(None, validation_alias="disableStandbyFieldsOverride", serialization_alias="disableStandbyFieldsOverride")
    should_pass_actor_input: bool | None = Field(None, validation_alias="shouldPassActorInput", serialization_alias="shouldPassActorInput")

class ActorTasksPostBodyOptions(PermissiveModel):
    build: str | None = None
    timeout_secs: int | None = Field(None, validation_alias="timeoutSecs", serialization_alias="timeoutSecs")
    memory_mbytes: int | None = Field(None, validation_alias="memoryMbytes", serialization_alias="memoryMbytes")
    restart_on_error: bool | None = Field(None, validation_alias="restartOnError", serialization_alias="restartOnError")
    max_items: int | None = Field(None, validation_alias="maxItems", serialization_alias="maxItems")

class ActorTasksPostBody(PermissiveModel):
    act_id: str = Field(..., validation_alias="actId", serialization_alias="actId")
    name: str
    options: ActorTasksPostBodyOptions | None = None
    input_: dict[str, Any] | None = Field(None, validation_alias="input", serialization_alias="input", description="The input configuration for the Actor task. This is a user-defined JSON object\nthat will be passed to the Actor when the task is run.\n")
    title: str | None = None
    actor_standby: ActorTasksPostBodyActorStandby | None = Field(None, validation_alias="actorStandby", serialization_alias="actorStandby")

class BuildTag(PermissiveModel):
    build_id: str = Field(..., validation_alias="buildId", serialization_alias="buildId")

class CommonActorPricingInfo(PermissiveModel):
    apify_margin_percentage: float = Field(..., validation_alias="apifyMarginPercentage", serialization_alias="apifyMarginPercentage", description="In [0, 1], fraction of pricePerUnitUsd that goes to Apify")
    created_at: str = Field(..., validation_alias="createdAt", serialization_alias="createdAt", description="When this pricing info record has been created", json_schema_extra={'format': 'date-time'})
    started_at: str = Field(..., validation_alias="startedAt", serialization_alias="startedAt", description="Since when is this pricing info record effective for a given Actor", json_schema_extra={'format': 'date-time'})
    notified_about_future_change_at: str | None = Field(None, validation_alias="notifiedAboutFutureChangeAt", serialization_alias="notifiedAboutFutureChangeAt", json_schema_extra={'format': 'date-time'})
    notified_about_change_at: str | None = Field(None, validation_alias="notifiedAboutChangeAt", serialization_alias="notifiedAboutChangeAt", json_schema_extra={'format': 'date-time'})
    reason_for_change: str | None = Field(None, validation_alias="reasonForChange", serialization_alias="reasonForChange")

class DatasetStats(PermissiveModel):
    read_count: int = Field(..., validation_alias="readCount", serialization_alias="readCount")
    write_count: int = Field(..., validation_alias="writeCount", serialization_alias="writeCount")
    storage_bytes: int = Field(..., validation_alias="storageBytes", serialization_alias="storageBytes")

class Dataset(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str | None = None
    user_id: str = Field(..., validation_alias="userId", serialization_alias="userId")
    created_at: str = Field(..., validation_alias="createdAt", serialization_alias="createdAt", json_schema_extra={'format': 'date-time'})
    modified_at: str = Field(..., validation_alias="modifiedAt", serialization_alias="modifiedAt", json_schema_extra={'format': 'date-time'})
    accessed_at: str = Field(..., validation_alias="accessedAt", serialization_alias="accessedAt", json_schema_extra={'format': 'date-time'})
    item_count: int = Field(..., validation_alias="itemCount", serialization_alias="itemCount", ge=0)
    clean_item_count: int = Field(..., validation_alias="cleanItemCount", serialization_alias="cleanItemCount", ge=0)
    act_id: str | None = Field(None, validation_alias="actId", serialization_alias="actId")
    act_run_id: str | None = Field(None, validation_alias="actRunId", serialization_alias="actRunId")
    fields: list[str] | None = None
    schema_: dict[str, Any] | None = Field(None, validation_alias="schema", serialization_alias="schema", description="Defines the schema of items in your dataset, the full specification can be found in [Apify docs](/platform/actors/development/actor-definition/dataset-schema)")
    console_url: str = Field(..., validation_alias="consoleUrl", serialization_alias="consoleUrl", json_schema_extra={'format': 'uri'})
    items_public_url: str | None = Field(None, validation_alias="itemsPublicUrl", serialization_alias="itemsPublicUrl", description="A public link to access the dataset items directly.", json_schema_extra={'format': 'uri'})
    url_signing_secret_key: str | None = Field(None, validation_alias="urlSigningSecretKey", serialization_alias="urlSigningSecretKey", description="A secret key for generating signed public URLs. It is only provided to clients with WRITE permission for the dataset.")
    general_access: Literal["ANYONE_WITH_ID_CAN_READ", "ANYONE_WITH_NAME_CAN_READ", "FOLLOW_USER_SETTING", "RESTRICTED"] | None = Field(None, validation_alias="generalAccess", serialization_alias="generalAccess")
    stats: DatasetStats | None = None

class DefaultRunOptions(PermissiveModel):
    build: str | None = None
    timeout_secs: int | None = Field(None, validation_alias="timeoutSecs", serialization_alias="timeoutSecs")
    memory_mbytes: int | None = Field(None, validation_alias="memoryMbytes", serialization_alias="memoryMbytes")
    restart_on_error: bool | None = Field(None, validation_alias="restartOnError", serialization_alias="restartOnError")
    max_items: int | None = Field(None, validation_alias="maxItems", serialization_alias="maxItems")
    force_permission_level: Literal["LIMITED_PERMISSIONS", "FULL_PERMISSIONS"] | None = Field(None, validation_alias="forcePermissionLevel", serialization_alias="forcePermissionLevel")

class EnvVar(PermissiveModel):
    name: str
    value: str
    is_secret: bool | None = Field(None, validation_alias="isSecret", serialization_alias="isSecret")

class ExampleRunInput(PermissiveModel):
    body: str | None = None
    content_type: str | None = Field(None, validation_alias="contentType", serialization_alias="contentType")

class ExampleWebhookDispatch(PermissiveModel):
    status: Literal["ACTIVE", "SUCCEEDED", "FAILED"]
    finished_at: str | None = Field(None, validation_alias="finishedAt", serialization_alias="finishedAt", json_schema_extra={'format': 'date-time'})

class FlatPricePerMonthActorPricingInfo(PermissiveModel):
    apify_margin_percentage: float = Field(..., validation_alias="apifyMarginPercentage", serialization_alias="apifyMarginPercentage", description="In [0, 1], fraction of pricePerUnitUsd that goes to Apify")
    created_at: str = Field(..., validation_alias="createdAt", serialization_alias="createdAt", description="When this pricing info record has been created", json_schema_extra={'format': 'date-time'})
    started_at: str = Field(..., validation_alias="startedAt", serialization_alias="startedAt", description="Since when is this pricing info record effective for a given Actor", json_schema_extra={'format': 'date-time'})
    notified_about_future_change_at: str | None = Field(None, validation_alias="notifiedAboutFutureChangeAt", serialization_alias="notifiedAboutFutureChangeAt", json_schema_extra={'format': 'date-time'})
    notified_about_change_at: str | None = Field(None, validation_alias="notifiedAboutChangeAt", serialization_alias="notifiedAboutChangeAt", json_schema_extra={'format': 'date-time'})
    reason_for_change: str | None = Field(None, validation_alias="reasonForChange", serialization_alias="reasonForChange")
    pricing_model: Literal["PAY_PER_EVENT", "PRICE_PER_DATASET_ITEM", "FLAT_PRICE_PER_MONTH", "FREE"] = Field(..., validation_alias="pricingModel", serialization_alias="pricingModel")
    trial_minutes: int = Field(..., validation_alias="trialMinutes", serialization_alias="trialMinutes", description="For how long this Actor can be used for free in trial period")
    price_per_unit_usd: float = Field(..., validation_alias="pricePerUnitUsd", serialization_alias="pricePerUnitUsd", description="Monthly flat price in USD")

class FreeActorPricingInfo(PermissiveModel):
    apify_margin_percentage: float = Field(..., validation_alias="apifyMarginPercentage", serialization_alias="apifyMarginPercentage", description="In [0, 1], fraction of pricePerUnitUsd that goes to Apify")
    created_at: str = Field(..., validation_alias="createdAt", serialization_alias="createdAt", description="When this pricing info record has been created", json_schema_extra={'format': 'date-time'})
    started_at: str = Field(..., validation_alias="startedAt", serialization_alias="startedAt", description="Since when is this pricing info record effective for a given Actor", json_schema_extra={'format': 'date-time'})
    notified_about_future_change_at: str | None = Field(None, validation_alias="notifiedAboutFutureChangeAt", serialization_alias="notifiedAboutFutureChangeAt", json_schema_extra={'format': 'date-time'})
    notified_about_change_at: str | None = Field(None, validation_alias="notifiedAboutChangeAt", serialization_alias="notifiedAboutChangeAt", json_schema_extra={'format': 'date-time'})
    reason_for_change: str | None = Field(None, validation_alias="reasonForChange", serialization_alias="reasonForChange")
    pricing_model: Literal["PAY_PER_EVENT", "PRICE_PER_DATASET_ITEM", "FLAT_PRICE_PER_MONTH", "FREE"] = Field(..., validation_alias="pricingModel", serialization_alias="pricingModel")

class Limits(PermissiveModel):
    max_monthly_usage_usd: float = Field(..., validation_alias="maxMonthlyUsageUsd", serialization_alias="maxMonthlyUsageUsd")
    max_monthly_actor_compute_units: float = Field(..., validation_alias="maxMonthlyActorComputeUnits", serialization_alias="maxMonthlyActorComputeUnits")
    max_monthly_external_data_transfer_gbytes: float = Field(..., validation_alias="maxMonthlyExternalDataTransferGbytes", serialization_alias="maxMonthlyExternalDataTransferGbytes")
    max_monthly_proxy_serps: int = Field(..., validation_alias="maxMonthlyProxySerps", serialization_alias="maxMonthlyProxySerps")
    max_monthly_residential_proxy_gbytes: float = Field(..., validation_alias="maxMonthlyResidentialProxyGbytes", serialization_alias="maxMonthlyResidentialProxyGbytes")
    max_actor_memory_gbytes: float = Field(..., validation_alias="maxActorMemoryGbytes", serialization_alias="maxActorMemoryGbytes")
    max_actor_count: int = Field(..., validation_alias="maxActorCount", serialization_alias="maxActorCount")
    max_actor_task_count: int = Field(..., validation_alias="maxActorTaskCount", serialization_alias="maxActorTaskCount")
    max_concurrent_actor_jobs: int = Field(..., validation_alias="maxConcurrentActorJobs", serialization_alias="maxConcurrentActorJobs")
    max_team_account_seat_count: int = Field(..., validation_alias="maxTeamAccountSeatCount", serialization_alias="maxTeamAccountSeatCount")
    data_retention_days: int = Field(..., validation_alias="dataRetentionDays", serialization_alias="dataRetentionDays")

class Metamorph(PermissiveModel):
    """Information about a metamorph event that occurred during the run."""
    created_at: str = Field(..., validation_alias="createdAt", serialization_alias="createdAt", description="Time when the metamorph occurred.", json_schema_extra={'format': 'date-time'})
    actor_id: str = Field(..., validation_alias="actorId", serialization_alias="actorId", description="ID of the Actor that the run was metamorphed to.")
    build_id: str = Field(..., validation_alias="buildId", serialization_alias="buildId", description="ID of the build used for the metamorphed Actor.")
    input_key: str | None = Field(None, validation_alias="inputKey", serialization_alias="inputKey", description="Key of the input record in the key-value store.")

class PayPerEventActorPricingInfoPricingPerEvent(PermissiveModel):
    actor_charge_events: dict[str, ActorChargeEvent] | None = Field(None, validation_alias="actorChargeEvents", serialization_alias="actorChargeEvents")

class PayPerEventActorPricingInfo(PermissiveModel):
    apify_margin_percentage: float = Field(..., validation_alias="apifyMarginPercentage", serialization_alias="apifyMarginPercentage", description="In [0, 1], fraction of pricePerUnitUsd that goes to Apify")
    created_at: str = Field(..., validation_alias="createdAt", serialization_alias="createdAt", description="When this pricing info record has been created", json_schema_extra={'format': 'date-time'})
    started_at: str = Field(..., validation_alias="startedAt", serialization_alias="startedAt", description="Since when is this pricing info record effective for a given Actor", json_schema_extra={'format': 'date-time'})
    notified_about_future_change_at: str | None = Field(None, validation_alias="notifiedAboutFutureChangeAt", serialization_alias="notifiedAboutFutureChangeAt", json_schema_extra={'format': 'date-time'})
    notified_about_change_at: str | None = Field(None, validation_alias="notifiedAboutChangeAt", serialization_alias="notifiedAboutChangeAt", json_schema_extra={'format': 'date-time'})
    reason_for_change: str | None = Field(None, validation_alias="reasonForChange", serialization_alias="reasonForChange")
    pricing_model: Literal["PAY_PER_EVENT", "PRICE_PER_DATASET_ITEM", "FLAT_PRICE_PER_MONTH", "FREE"] = Field(..., validation_alias="pricingModel", serialization_alias="pricingModel")
    pricing_per_event: PayPerEventActorPricingInfoPricingPerEvent = Field(..., validation_alias="pricingPerEvent", serialization_alias="pricingPerEvent")
    minimal_max_total_charge_usd: float | None = Field(None, validation_alias="minimalMaxTotalChargeUsd", serialization_alias="minimalMaxTotalChargeUsd")

class PayPerEventActorPricingInfoV1PricingPerEvent(PermissiveModel):
    actor_charge_events: dict[str, ActorChargeEvent] | None = Field(None, validation_alias="actorChargeEvents", serialization_alias="actorChargeEvents")

class PricePerDatasetItemActorPricingInfo(PermissiveModel):
    apify_margin_percentage: float = Field(..., validation_alias="apifyMarginPercentage", serialization_alias="apifyMarginPercentage", description="In [0, 1], fraction of pricePerUnitUsd that goes to Apify")
    created_at: str = Field(..., validation_alias="createdAt", serialization_alias="createdAt", description="When this pricing info record has been created", json_schema_extra={'format': 'date-time'})
    started_at: str = Field(..., validation_alias="startedAt", serialization_alias="startedAt", description="Since when is this pricing info record effective for a given Actor", json_schema_extra={'format': 'date-time'})
    notified_about_future_change_at: str | None = Field(None, validation_alias="notifiedAboutFutureChangeAt", serialization_alias="notifiedAboutFutureChangeAt", json_schema_extra={'format': 'date-time'})
    notified_about_change_at: str | None = Field(None, validation_alias="notifiedAboutChangeAt", serialization_alias="notifiedAboutChangeAt", json_schema_extra={'format': 'date-time'})
    reason_for_change: str | None = Field(None, validation_alias="reasonForChange", serialization_alias="reasonForChange")
    pricing_model: Literal["PAY_PER_EVENT", "PRICE_PER_DATASET_ITEM", "FLAT_PRICE_PER_MONTH", "FREE"] = Field(..., validation_alias="pricingModel", serialization_alias="pricingModel")
    unit_name: str = Field(..., validation_alias="unitName", serialization_alias="unitName", description="Name of the unit that is being charged")
    price_per_unit_usd: float = Field(..., validation_alias="pricePerUnitUsd", serialization_alias="pricePerUnitUsd")

class PutItemsRequest(RootModel[dict[str, Any]]):
    pass

class RequestDraft(PermissiveModel):
    """A request that failed to be processed during a request queue operation and can be retried."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="A unique identifier assigned to the request.")
    unique_key: str = Field(..., validation_alias="uniqueKey", serialization_alias="uniqueKey", description="A unique key used for request de-duplication. Requests with the same unique key are considered identical.")
    url: str = Field(..., description="The URL of the request.", json_schema_extra={'format': 'uri'})
    method: str = Field(..., description="The HTTP method of the request.")

class RequestDraftDelete(PermissiveModel):
    """A request that should be deleted."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="A unique identifier assigned to the request.")
    unique_key: str | None = Field(None, validation_alias="uniqueKey", serialization_alias="uniqueKey", description="A unique key used for request de-duplication. Requests with the same unique key are considered identical.")

class RequestQueuePutBody(PermissiveModel):
    name: str | None = Field(None, description="The new name for the request queue.")
    general_access: Literal["ANYONE_WITH_ID_CAN_READ", "ANYONE_WITH_NAME_CAN_READ", "FOLLOW_USER_SETTING", "RESTRICTED"] | None = Field(None, validation_alias="generalAccess", serialization_alias="generalAccess", description="Defines the general access level for the resource.")

class RequestUserData(PermissiveModel):
    """Custom user data attached to the request. Can contain arbitrary fields."""
    label: str | None = Field(None, description="Optional label for categorizing the request.")
    image: str | None = Field(None, description="Optional image URL associated with the request.", json_schema_extra={'format': 'uri'})

class Request(PermissiveModel):
    """A request stored in the request queue, including its metadata and processing state."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A unique identifier assigned to the request.")
    unique_key: str = Field(..., validation_alias="uniqueKey", serialization_alias="uniqueKey", description="A unique key used for request de-duplication. Requests with the same unique key are considered identical.")
    url: str = Field(..., description="The URL of the request.", json_schema_extra={'format': 'uri'})
    method: str | None = Field(None, description="The HTTP method of the request.")
    retry_count: int | None = Field(None, validation_alias="retryCount", serialization_alias="retryCount", description="The number of times this request has been retried.")
    loaded_url: str | None = Field(None, validation_alias="loadedUrl", serialization_alias="loadedUrl", description="The final URL that was loaded, after redirects (if any).", json_schema_extra={'format': 'uri'})
    payload: dict[str, Any] | None = Field(None, description="The request payload, typically used with POST or PUT requests.")
    headers: dict[str, Any] | None = Field(None, description="HTTP headers sent with the request.")
    user_data: RequestUserData | None = Field(None, validation_alias="userData", serialization_alias="userData")
    no_retry: bool | None = Field(None, validation_alias="noRetry", serialization_alias="noRetry", description="Indicates whether the request should not be retried if processing fails.")
    error_messages: list[str] | None = Field(None, validation_alias="errorMessages", serialization_alias="errorMessages", description="Error messages recorded from failed processing attempts.")
    handled_at: str | None = Field(None, validation_alias="handledAt", serialization_alias="handledAt", description="The timestamp when the request was marked as handled, if applicable.", json_schema_extra={'format': 'date-time'})

class RunMeta(PermissiveModel):
    origin: Literal["DEVELOPMENT", "WEB", "API", "SCHEDULER", "TEST", "WEBHOOK", "ACTOR", "CLI", "STANDBY"]
    client_ip: str | None = Field(None, validation_alias="clientIp", serialization_alias="clientIp", description="IP address of the client that started the run.")
    user_agent: str | None = Field(None, validation_alias="userAgent", serialization_alias="userAgent", description="User agent of the client that started the run.")
    schedule_id: str | None = Field(None, validation_alias="scheduleId", serialization_alias="scheduleId", description="ID of the schedule that triggered the run.")
    scheduled_at: str | None = Field(None, validation_alias="scheduledAt", serialization_alias="scheduledAt", description="Time when the run was scheduled.", json_schema_extra={'format': 'date-time'})

class RunOptions(PermissiveModel):
    build: str
    timeout_secs: int = Field(..., validation_alias="timeoutSecs", serialization_alias="timeoutSecs", ge=0)
    memory_mbytes: int = Field(..., validation_alias="memoryMbytes", serialization_alias="memoryMbytes", ge=128, le=32768)
    disk_mbytes: int = Field(..., validation_alias="diskMbytes", serialization_alias="diskMbytes", ge=0)
    max_items: int | None = Field(None, validation_alias="maxItems", serialization_alias="maxItems", ge=1)
    max_total_charge_usd: float | None = Field(None, validation_alias="maxTotalChargeUsd", serialization_alias="maxTotalChargeUsd", ge=0)

class RunStats(PermissiveModel):
    input_body_len: int | None = Field(None, validation_alias="inputBodyLen", serialization_alias="inputBodyLen", ge=0)
    migration_count: int | None = Field(None, validation_alias="migrationCount", serialization_alias="migrationCount", ge=0)
    reboot_count: int | None = Field(None, validation_alias="rebootCount", serialization_alias="rebootCount", ge=0)
    restart_count: int = Field(..., validation_alias="restartCount", serialization_alias="restartCount", ge=0)
    resurrect_count: int = Field(..., validation_alias="resurrectCount", serialization_alias="resurrectCount", ge=0)
    mem_avg_bytes: float | None = Field(None, validation_alias="memAvgBytes", serialization_alias="memAvgBytes")
    mem_max_bytes: int | None = Field(None, validation_alias="memMaxBytes", serialization_alias="memMaxBytes", ge=0)
    mem_current_bytes: int | None = Field(None, validation_alias="memCurrentBytes", serialization_alias="memCurrentBytes", ge=0)
    cpu_avg_usage: float | None = Field(None, validation_alias="cpuAvgUsage", serialization_alias="cpuAvgUsage")
    cpu_max_usage: float | None = Field(None, validation_alias="cpuMaxUsage", serialization_alias="cpuMaxUsage")
    cpu_current_usage: float | None = Field(None, validation_alias="cpuCurrentUsage", serialization_alias="cpuCurrentUsage")
    net_rx_bytes: int | None = Field(None, validation_alias="netRxBytes", serialization_alias="netRxBytes", ge=0)
    net_tx_bytes: int | None = Field(None, validation_alias="netTxBytes", serialization_alias="netTxBytes", ge=0)
    duration_millis: int | None = Field(None, validation_alias="durationMillis", serialization_alias="durationMillis", ge=0)
    run_time_secs: float | None = Field(None, validation_alias="runTimeSecs", serialization_alias="runTimeSecs", ge=0)
    metamorph: int | None = Field(None, ge=0)
    compute_units: float = Field(..., validation_alias="computeUnits", serialization_alias="computeUnits", ge=0)

class RunStorageIds(PermissiveModel):
    """A map of aliased storage IDs associated with this run, grouped by storage type."""
    datasets: dict[str, str] | None = Field(None, description="Aliased dataset IDs for this run.")
    key_value_stores: dict[str, str] | None = Field(None, validation_alias="keyValueStores", serialization_alias="keyValueStores", description="Aliased key-value store IDs for this run.")
    request_queues: dict[str, str] | None = Field(None, validation_alias="requestQueues", serialization_alias="requestQueues", description="Aliased request queue IDs for this run.")

class RunStorageIdsDatasets(PermissiveModel):
    """Aliased dataset IDs for this run."""
    default: str | None = Field(None, description="ID of the default dataset for this run.")

class RunStorageIdsKeyValueStores(PermissiveModel):
    """Aliased key-value store IDs for this run."""
    default: str | None = Field(None, description="ID of the default key-value store for this run.")

class RunStorageIdsRequestQueues(PermissiveModel):
    """Aliased request queue IDs for this run."""
    default: str | None = Field(None, description="ID of the default request queue for this run.")

class RunUsage(PermissiveModel):
    actor_compute_units: float | None = Field(None, validation_alias="ACTOR_COMPUTE_UNITS", serialization_alias="ACTOR_COMPUTE_UNITS")
    dataset_reads: int | None = Field(None, validation_alias="DATASET_READS", serialization_alias="DATASET_READS")
    dataset_writes: int | None = Field(None, validation_alias="DATASET_WRITES", serialization_alias="DATASET_WRITES")
    key_value_store_reads: int | None = Field(None, validation_alias="KEY_VALUE_STORE_READS", serialization_alias="KEY_VALUE_STORE_READS")
    key_value_store_writes: int | None = Field(None, validation_alias="KEY_VALUE_STORE_WRITES", serialization_alias="KEY_VALUE_STORE_WRITES")
    key_value_store_lists: int | None = Field(None, validation_alias="KEY_VALUE_STORE_LISTS", serialization_alias="KEY_VALUE_STORE_LISTS")
    request_queue_reads: int | None = Field(None, validation_alias="REQUEST_QUEUE_READS", serialization_alias="REQUEST_QUEUE_READS")
    request_queue_writes: int | None = Field(None, validation_alias="REQUEST_QUEUE_WRITES", serialization_alias="REQUEST_QUEUE_WRITES")
    data_transfer_internal_gbytes: float | None = Field(None, validation_alias="DATA_TRANSFER_INTERNAL_GBYTES", serialization_alias="DATA_TRANSFER_INTERNAL_GBYTES")
    data_transfer_external_gbytes: float | None = Field(None, validation_alias="DATA_TRANSFER_EXTERNAL_GBYTES", serialization_alias="DATA_TRANSFER_EXTERNAL_GBYTES")
    proxy_residential_transfer_gbytes: float | None = Field(None, validation_alias="PROXY_RESIDENTIAL_TRANSFER_GBYTES", serialization_alias="PROXY_RESIDENTIAL_TRANSFER_GBYTES")
    proxy_serps: int | None = Field(None, validation_alias="PROXY_SERPS", serialization_alias="PROXY_SERPS")

class RunUsageUsd(PermissiveModel):
    """Resource usage costs in USD. All values are monetary amounts in US dollars."""
    actor_compute_units: float | None = Field(None, validation_alias="ACTOR_COMPUTE_UNITS", serialization_alias="ACTOR_COMPUTE_UNITS")
    dataset_reads: float | None = Field(None, validation_alias="DATASET_READS", serialization_alias="DATASET_READS")
    dataset_writes: float | None = Field(None, validation_alias="DATASET_WRITES", serialization_alias="DATASET_WRITES")
    key_value_store_reads: float | None = Field(None, validation_alias="KEY_VALUE_STORE_READS", serialization_alias="KEY_VALUE_STORE_READS")
    key_value_store_writes: float | None = Field(None, validation_alias="KEY_VALUE_STORE_WRITES", serialization_alias="KEY_VALUE_STORE_WRITES")
    key_value_store_lists: float | None = Field(None, validation_alias="KEY_VALUE_STORE_LISTS", serialization_alias="KEY_VALUE_STORE_LISTS")
    request_queue_reads: float | None = Field(None, validation_alias="REQUEST_QUEUE_READS", serialization_alias="REQUEST_QUEUE_READS")
    request_queue_writes: float | None = Field(None, validation_alias="REQUEST_QUEUE_WRITES", serialization_alias="REQUEST_QUEUE_WRITES")
    data_transfer_internal_gbytes: float | None = Field(None, validation_alias="DATA_TRANSFER_INTERNAL_GBYTES", serialization_alias="DATA_TRANSFER_INTERNAL_GBYTES")
    data_transfer_external_gbytes: float | None = Field(None, validation_alias="DATA_TRANSFER_EXTERNAL_GBYTES", serialization_alias="DATA_TRANSFER_EXTERNAL_GBYTES")
    proxy_residential_transfer_gbytes: float | None = Field(None, validation_alias="PROXY_RESIDENTIAL_TRANSFER_GBYTES", serialization_alias="PROXY_RESIDENTIAL_TRANSFER_GBYTES")
    proxy_serps: float | None = Field(None, validation_alias="PROXY_SERPS", serialization_alias="PROXY_SERPS")

class Run(PermissiveModel):
    """Represents an Actor run and its associated data."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier of the Actor run.")
    act_id: str = Field(..., validation_alias="actId", serialization_alias="actId", description="ID of the Actor that was run.")
    user_id: str = Field(..., validation_alias="userId", serialization_alias="userId", description="ID of the user who started the run.")
    actor_task_id: str | None = Field(None, validation_alias="actorTaskId", serialization_alias="actorTaskId", description="ID of the Actor task, if the run was started from a task.")
    started_at: str = Field(..., validation_alias="startedAt", serialization_alias="startedAt", description="Time when the Actor run started.", json_schema_extra={'format': 'date-time'})
    finished_at: str | None = Field(None, validation_alias="finishedAt", serialization_alias="finishedAt", description="Time when the Actor run finished.", json_schema_extra={'format': 'date-time'})
    status: Literal["READY", "RUNNING", "SUCCEEDED", "FAILED", "TIMING-OUT", "TIMED-OUT", "ABORTING", "ABORTED"] = Field(..., description="Current status of the Actor run.")
    status_message: str | None = Field(None, validation_alias="statusMessage", serialization_alias="statusMessage", description="Detailed message about the run status.")
    is_status_message_terminal: bool | None = Field(None, validation_alias="isStatusMessageTerminal", serialization_alias="isStatusMessageTerminal", description="Whether the status message is terminal (final).")
    meta: RunMeta = Field(..., description="Metadata about the Actor run.")
    pricing_info: PayPerEventActorPricingInfo | PricePerDatasetItemActorPricingInfo | FlatPricePerMonthActorPricingInfo | FreeActorPricingInfo | None = Field(None, validation_alias="pricingInfo", serialization_alias="pricingInfo", description="Pricing information for the Actor.")
    stats: RunStats = Field(..., description="Statistics of the Actor run.")
    charged_event_counts: dict[str, int] | None = Field(None, validation_alias="chargedEventCounts", serialization_alias="chargedEventCounts", description="A map of charged event types to their counts. The keys are event type identifiers defined by the Actor's pricing model (pay-per-event), and the values are the number of times each event was charged during this run.")
    options: RunOptions = Field(..., description="Configuration options for the Actor run.")
    build_id: str = Field(..., validation_alias="buildId", serialization_alias="buildId", description="ID of the Actor build used for this run.")
    exit_code: int | None = Field(None, validation_alias="exitCode", serialization_alias="exitCode", description="Exit code of the Actor run process.")
    general_access: Literal["ANYONE_WITH_ID_CAN_READ", "ANYONE_WITH_NAME_CAN_READ", "FOLLOW_USER_SETTING", "RESTRICTED"] = Field(..., validation_alias="generalAccess", serialization_alias="generalAccess", description="General access level for the Actor run.")
    default_key_value_store_id: str = Field(..., validation_alias="defaultKeyValueStoreId", serialization_alias="defaultKeyValueStoreId", description="ID of the default key-value store for this run.")
    default_dataset_id: str = Field(..., validation_alias="defaultDatasetId", serialization_alias="defaultDatasetId", description="ID of the default dataset for this run.")
    default_request_queue_id: str = Field(..., validation_alias="defaultRequestQueueId", serialization_alias="defaultRequestQueueId", description="ID of the default request queue for this run.")
    storage_ids: RunStorageIds | None = Field(None, validation_alias="storageIds", serialization_alias="storageIds", description="A map of aliased storage IDs associated with this run, grouped by storage type.")
    build_number: str | None = Field(None, validation_alias="buildNumber", serialization_alias="buildNumber", description="Build number of the Actor build used for this run.")
    container_url: str | None = Field(None, validation_alias="containerUrl", serialization_alias="containerUrl", description="URL of the container running the Actor.", json_schema_extra={'format': 'uri'})
    is_container_server_ready: bool | None = Field(None, validation_alias="isContainerServerReady", serialization_alias="isContainerServerReady", description="Whether the container's HTTP server is ready to accept requests.")
    git_branch_name: str | None = Field(None, validation_alias="gitBranchName", serialization_alias="gitBranchName", description="Name of the git branch used for the Actor build.")
    usage: RunUsage | None = Field(None, description="Resource usage statistics for the run.")
    usage_total_usd: float | None = Field(None, validation_alias="usageTotalUsd", serialization_alias="usageTotalUsd", description="Total cost in USD for this run. Represents what you actually pay. For run owners: includes platform usage (compute units) and/or event costs depending on the Actor's pricing model. For run non-owners: only available for Pay-Per-Event Actors (event costs only). Not available for Pay-Per-Result Actors when you're not the Actor owner.")
    usage_usd: RunUsageUsd | None = Field(None, validation_alias="usageUsd", serialization_alias="usageUsd", description="Platform usage costs breakdown in USD. Only present if you own the run AND are paying for platform usage (Pay-Per-Usage, Rental, or Pay-Per-Event with usage costs like standby Actors). Not available for standard Pay-Per-Event Actors or Pay-Per-Result Actors owned by others.")
    metamorphs: list[Metamorph] | None = Field(None, description="List of metamorph events that occurred during the run.")

class ScheduleActionsRunInput(PermissiveModel):
    body: str | None = None
    content_type: str | None = Field(None, validation_alias="contentType", serialization_alias="contentType")

class ScheduleActionsRunOptions(PermissiveModel):
    build: str | None = None
    timeout_secs: int | None = Field(None, validation_alias="timeoutSecs", serialization_alias="timeoutSecs")
    memory_mbytes: int | None = Field(None, validation_alias="memoryMbytes", serialization_alias="memoryMbytes")
    restart_on_error: bool | None = Field(None, validation_alias="restartOnError", serialization_alias="restartOnError")

class ScheduleActions(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    type_: Literal["RUN_ACTOR", "RUN_ACTOR_TASK"] = Field(..., validation_alias="type", serialization_alias="type")
    actor_id: str = Field(..., validation_alias="actorId", serialization_alias="actorId")
    run_input: ScheduleActionsRunInput | None = Field(None, validation_alias="runInput", serialization_alias="runInput")
    run_options: ScheduleActionsRunOptions | None = Field(None, validation_alias="runOptions", serialization_alias="runOptions")

class Schedule(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    user_id: str = Field(..., validation_alias="userId", serialization_alias="userId")
    name: str
    cron_expression: str = Field(..., validation_alias="cronExpression", serialization_alias="cronExpression")
    timezone_: str = Field(..., validation_alias="timezone", serialization_alias="timezone")
    is_enabled: bool = Field(..., validation_alias="isEnabled", serialization_alias="isEnabled")
    is_exclusive: bool = Field(..., validation_alias="isExclusive", serialization_alias="isExclusive")
    description: str | None = None
    created_at: str = Field(..., validation_alias="createdAt", serialization_alias="createdAt", json_schema_extra={'format': 'date-time'})
    modified_at: str = Field(..., validation_alias="modifiedAt", serialization_alias="modifiedAt", json_schema_extra={'format': 'date-time'})
    next_run_at: str | None = Field(None, validation_alias="nextRunAt", serialization_alias="nextRunAt", json_schema_extra={'format': 'date-time'})
    last_run_at: str | None = Field(None, validation_alias="lastRunAt", serialization_alias="lastRunAt", json_schema_extra={'format': 'date-time'})
    title: str | None = None
    actions: list[ScheduleActions]

class ScheduleCreateActions(PermissiveModel):
    type_: Literal["RUN_ACTOR", "RUN_ACTOR_TASK"] = Field(..., validation_alias="type", serialization_alias="type")
    actor_id: str = Field(..., validation_alias="actorId", serialization_alias="actorId")
    run_input: ScheduleActionsRunInput | None = Field(None, validation_alias="runInput", serialization_alias="runInput")
    run_options: ScheduleActionsRunOptions | None = Field(None, validation_alias="runOptions", serialization_alias="runOptions")

class SourceCodeFile(PermissiveModel):
    format_: Literal["BASE64", "TEXT"] = Field(..., validation_alias="format", serialization_alias="format")
    content: str
    name: str

class SourceCodeFolder(PermissiveModel):
    """Represents a folder in the Actor's source code structure. Distinguished from
SourceCodeFile by the presence of the `folder` property set to `true`.
"""
    name: str = Field(..., description="The folder path relative to the Actor's root directory.")
    folder: bool = Field(..., description="Always `true` for folders. Used to distinguish folders from files.")

class TaggedBuildInfo(PermissiveModel):
    """Information about a tagged build."""
    build_id: str | None = Field(None, validation_alias="buildId", serialization_alias="buildId", description="The ID of the build associated with this tag.")
    build_number: str | None = Field(None, validation_alias="buildNumber", serialization_alias="buildNumber", description="The build number/version string.")
    finished_at: str | None = Field(None, validation_alias="finishedAt", serialization_alias="finishedAt", description="The timestamp when the build finished.", json_schema_extra={'format': 'date-time'})

class TaggedBuilds(RootModel[dict[str, TaggedBuildInfo]]):
    pass

class VersionSourceFiles(RootModel[list[SourceCodeFile | SourceCodeFolder]]):
    pass

class CreateOrUpdateVersionRequest(PermissiveModel):
    version_number: str | None = Field(None, validation_alias="versionNumber", serialization_alias="versionNumber")
    source_type: Literal["SOURCE_FILES", "GIT_REPO", "TARBALL", "GITHUB_GIST"] | None = Field(None, validation_alias="sourceType", serialization_alias="sourceType")
    env_vars: list[EnvVar] | None = Field(None, validation_alias="envVars", serialization_alias="envVars")
    apply_env_vars_to_build: bool | None = Field(None, validation_alias="applyEnvVarsToBuild", serialization_alias="applyEnvVarsToBuild")
    build_tag: str | None = Field(None, validation_alias="buildTag", serialization_alias="buildTag")
    source_files: VersionSourceFiles | None = Field(None, validation_alias="sourceFiles", serialization_alias="sourceFiles")
    git_repo_url: str | None = Field(None, validation_alias="gitRepoUrl", serialization_alias="gitRepoUrl", description="URL of the Git repository when sourceType is GIT_REPO.")
    tarball_url: str | None = Field(None, validation_alias="tarballUrl", serialization_alias="tarballUrl", description="URL of the tarball when sourceType is TARBALL.")
    git_hub_gist_url: str | None = Field(None, validation_alias="gitHubGistUrl", serialization_alias="gitHubGistUrl", description="URL of the GitHub Gist when sourceType is GITHUB_GIST.")

class Version(PermissiveModel):
    version_number: str = Field(..., validation_alias="versionNumber", serialization_alias="versionNumber")
    source_type: Literal["SOURCE_FILES", "GIT_REPO", "TARBALL", "GITHUB_GIST"] | None = Field(..., validation_alias="sourceType", serialization_alias="sourceType")
    env_vars: list[EnvVar] | None = Field(None, validation_alias="envVars", serialization_alias="envVars")
    apply_env_vars_to_build: bool | None = Field(None, validation_alias="applyEnvVarsToBuild", serialization_alias="applyEnvVarsToBuild")
    build_tag: str | None = Field(None, validation_alias="buildTag", serialization_alias="buildTag")
    source_files: VersionSourceFiles | None = Field(None, validation_alias="sourceFiles", serialization_alias="sourceFiles")
    git_repo_url: str | None = Field(None, validation_alias="gitRepoUrl", serialization_alias="gitRepoUrl", description="URL of the Git repository when sourceType is GIT_REPO.")
    tarball_url: str | None = Field(None, validation_alias="tarballUrl", serialization_alias="tarballUrl", description="URL of the tarball when sourceType is TARBALL.")
    git_hub_gist_url: str | None = Field(None, validation_alias="gitHubGistUrl", serialization_alias="gitHubGistUrl", description="URL of the GitHub Gist when sourceType is GITHUB_GIST.")

class Actor(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    user_id: str = Field(..., validation_alias="userId", serialization_alias="userId")
    name: str
    username: str
    description: str | None = None
    restart_on_error: bool | None = Field(None, validation_alias="restartOnError", serialization_alias="restartOnError")
    is_public: bool = Field(..., validation_alias="isPublic", serialization_alias="isPublic")
    actor_permission_level: Literal["LIMITED_PERMISSIONS", "FULL_PERMISSIONS"] | None = Field(None, validation_alias="actorPermissionLevel", serialization_alias="actorPermissionLevel")
    created_at: str = Field(..., validation_alias="createdAt", serialization_alias="createdAt", json_schema_extra={'format': 'date-time'})
    modified_at: str = Field(..., validation_alias="modifiedAt", serialization_alias="modifiedAt", json_schema_extra={'format': 'date-time'})
    stats: ActorStats
    versions: list[Version]
    pricing_infos: list[PayPerEventActorPricingInfo | PricePerDatasetItemActorPricingInfo | FlatPricePerMonthActorPricingInfo | FreeActorPricingInfo] | None = Field(None, validation_alias="pricingInfos", serialization_alias="pricingInfos")
    default_run_options: DefaultRunOptions = Field(..., validation_alias="defaultRunOptions", serialization_alias="defaultRunOptions")
    example_run_input: ExampleRunInput | None = Field(None, validation_alias="exampleRunInput", serialization_alias="exampleRunInput")
    is_deprecated: bool | None = Field(None, validation_alias="isDeprecated", serialization_alias="isDeprecated")
    deployment_key: str | None = Field(None, validation_alias="deploymentKey", serialization_alias="deploymentKey")
    title: str | None = None
    tagged_builds: TaggedBuilds | None = Field(None, validation_alias="taggedBuilds", serialization_alias="taggedBuilds")
    actor_standby: ActorStandby | None = Field(None, validation_alias="actorStandby", serialization_alias="actorStandby")
    readme_summary: str | None = Field(None, validation_alias="readmeSummary", serialization_alias="readmeSummary", description="A brief, LLM-generated readme summary")

class WebhookCondition(PermissiveModel):
    actor_id: str | None = Field(None, validation_alias="actorId", serialization_alias="actorId")
    actor_task_id: str | None = Field(None, validation_alias="actorTaskId", serialization_alias="actorTaskId")
    actor_run_id: str | None = Field(None, validation_alias="actorRunId", serialization_alias="actorRunId")

class WebhookStats(PermissiveModel):
    total_dispatches: int = Field(..., validation_alias="totalDispatches", serialization_alias="totalDispatches")

class Webhook(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    created_at: str = Field(..., validation_alias="createdAt", serialization_alias="createdAt", json_schema_extra={'format': 'date-time'})
    modified_at: str = Field(..., validation_alias="modifiedAt", serialization_alias="modifiedAt", json_schema_extra={'format': 'date-time'})
    user_id: str = Field(..., validation_alias="userId", serialization_alias="userId")
    is_ad_hoc: bool | None = Field(None, validation_alias="isAdHoc", serialization_alias="isAdHoc")
    should_interpolate_strings: bool | None = Field(None, validation_alias="shouldInterpolateStrings", serialization_alias="shouldInterpolateStrings")
    event_types: list[Literal["ACTOR.BUILD.ABORTED", "ACTOR.BUILD.CREATED", "ACTOR.BUILD.FAILED", "ACTOR.BUILD.SUCCEEDED", "ACTOR.BUILD.TIMED_OUT", "ACTOR.RUN.ABORTED", "ACTOR.RUN.CREATED", "ACTOR.RUN.FAILED", "ACTOR.RUN.RESURRECTED", "ACTOR.RUN.SUCCEEDED", "ACTOR.RUN.TIMED_OUT", "TEST"]] = Field(..., validation_alias="eventTypes", serialization_alias="eventTypes")
    condition: WebhookCondition
    ignore_ssl_errors: bool = Field(..., validation_alias="ignoreSslErrors", serialization_alias="ignoreSslErrors")
    do_not_retry: bool | None = Field(None, validation_alias="doNotRetry", serialization_alias="doNotRetry")
    request_url: str = Field(..., validation_alias="requestUrl", serialization_alias="requestUrl", json_schema_extra={'format': 'uri'})
    payload_template: str | None = Field(None, validation_alias="payloadTemplate", serialization_alias="payloadTemplate")
    headers_template: str | None = Field(None, validation_alias="headersTemplate", serialization_alias="headersTemplate")
    description: str | None = None
    last_dispatch: ExampleWebhookDispatch | None = Field(None, validation_alias="lastDispatch", serialization_alias="lastDispatch")
    stats: WebhookStats | None = None


# Rebuild models to resolve forward references (required for circular refs)
Actor.model_rebuild()
ActorChargeEvent.model_rebuild()
ActorRunPutBody.model_rebuild()
ActorStandby.model_rebuild()
ActorStats.model_rebuild()
ActorTasksPostBody.model_rebuild()
ActorTasksPostBodyActorStandby.model_rebuild()
ActorTasksPostBodyOptions.model_rebuild()
BuildTag.model_rebuild()
CommonActorPricingInfo.model_rebuild()
CreateOrUpdateVersionRequest.model_rebuild()
Dataset.model_rebuild()
DatasetStats.model_rebuild()
DefaultRunOptions.model_rebuild()
EnvVar.model_rebuild()
ExampleRunInput.model_rebuild()
ExampleWebhookDispatch.model_rebuild()
FlatPricePerMonthActorPricingInfo.model_rebuild()
FreeActorPricingInfo.model_rebuild()
Limits.model_rebuild()
Metamorph.model_rebuild()
PayPerEventActorPricingInfo.model_rebuild()
PayPerEventActorPricingInfoPricingPerEvent.model_rebuild()
PayPerEventActorPricingInfoV1PricingPerEvent.model_rebuild()
PricePerDatasetItemActorPricingInfo.model_rebuild()
PutItemsRequest.model_rebuild()
Request.model_rebuild()
RequestDraft.model_rebuild()
RequestDraftDelete.model_rebuild()
RequestQueuePutBody.model_rebuild()
RequestUserData.model_rebuild()
Run.model_rebuild()
RunMeta.model_rebuild()
RunOptions.model_rebuild()
RunStats.model_rebuild()
RunStorageIds.model_rebuild()
RunStorageIdsDatasets.model_rebuild()
RunStorageIdsKeyValueStores.model_rebuild()
RunStorageIdsRequestQueues.model_rebuild()
RunUsage.model_rebuild()
RunUsageUsd.model_rebuild()
Schedule.model_rebuild()
ScheduleActions.model_rebuild()
ScheduleActionsRunInput.model_rebuild()
ScheduleActionsRunOptions.model_rebuild()
ScheduleCreateActions.model_rebuild()
SourceCodeFile.model_rebuild()
SourceCodeFolder.model_rebuild()
TaggedBuildInfo.model_rebuild()
TaggedBuilds.model_rebuild()
Version.model_rebuild()
VersionSourceFiles.model_rebuild()
Webhook.model_rebuild()
WebhookCondition.model_rebuild()
WebhookStats.model_rebuild()

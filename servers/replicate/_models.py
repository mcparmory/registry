"""
Replicate MCP Server - Pydantic Models

Generated: 2026-05-12 12:24:35 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import StrictModel
from pydantic import Field

__all__ = [
    "CollectionsGetRequest",
    "DeploymentsCreateRequest",
    "DeploymentsDeleteRequest",
    "DeploymentsGetRequest",
    "DeploymentsPredictionsCreateRequest",
    "DeploymentsUpdateRequest",
    "FilesCreateRequest",
    "FilesDeleteRequest",
    "FilesDownloadRequest",
    "FilesGetRequest",
    "ModelsCreateRequest",
    "ModelsDeleteRequest",
    "ModelsExamplesListRequest",
    "ModelsGetRequest",
    "ModelsListRequest",
    "ModelsPredictionsCreateRequest",
    "ModelsReadmeGetRequest",
    "ModelsSearchRequest",
    "ModelsUpdateRequest",
    "ModelsVersionsDeleteRequest",
    "ModelsVersionsGetRequest",
    "ModelsVersionsListRequest",
    "PredictionsCancelRequest",
    "PredictionsCreateRequest",
    "PredictionsGetRequest",
    "PredictionsListRequest",
    "SearchRequest",
    "TrainingsCancelRequest",
    "TrainingsCreateRequest",
    "TrainingsGetRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: get_collection
class CollectionsGetRequestPath(StrictModel):
    collection_slug: str = Field(default=..., description="The unique identifier slug for the collection (e.g., 'super-resolution', 'image-restoration'). Find available collections at replicate.com/collections.")
class CollectionsGetRequest(StrictModel):
    """Retrieve a collection of models by its slug, including the collection metadata and all models within it."""
    path: CollectionsGetRequestPath

# Operation: create_deployment
class DeploymentsCreateRequestBody(StrictModel):
    hardware: str = Field(default=..., description="The hardware SKU to run the model on. Available SKUs can be retrieved from the hardware list endpoint (e.g., gpu-t4, gpu-a40).")
    max_instances: int = Field(default=..., description="The maximum number of instances for auto-scaling. Must be between 0 and 20, and should be greater than or equal to min_instances.", ge=0, le=20)
    min_instances: int = Field(default=..., description="The minimum number of instances to keep running. Must be between 0 and 5, and should be less than or equal to max_instances.", ge=0, le=5)
    model: str = Field(default=..., description="The full model identifier in the format owner/model-name (e.g., stability-ai/sdxl).")
    name: str = Field(default=..., description="A unique name for this deployment within your organization. Used to identify and manage the deployment.")
    version: str = Field(default=..., description="The 64-character version ID of the model to deploy. This specifies the exact model version and weights to use.")
class DeploymentsCreateRequest(StrictModel):
    """Create a new deployment to run a specific model version on designated hardware with auto-scaling configuration. The deployment will be immediately available for inference requests."""
    body: DeploymentsCreateRequestBody

# Operation: get_deployment
class DeploymentsGetRequestPath(StrictModel):
    deployment_owner: str = Field(default=..., description="The username or organization name that owns the deployment.")
    deployment_name: str = Field(default=..., description="The name of the deployment to retrieve.")
class DeploymentsGetRequest(StrictModel):
    """Retrieve detailed information about a specific deployment, including its current release configuration, hardware settings, and scaling parameters."""
    path: DeploymentsGetRequestPath

# Operation: update_deployment
class DeploymentsUpdateRequestPath(StrictModel):
    deployment_owner: str = Field(default=..., description="The username or organization name that owns the deployment.")
    deployment_name: str = Field(default=..., description="The name of the deployment to update.")
class DeploymentsUpdateRequestBody(StrictModel):
    hardware: str | None = Field(default=None, description="The hardware SKU to run the model on (e.g., gpu-t4). Available options can be retrieved from the hardware list endpoint.")
    max_instances: int | None = Field(default=None, description="The maximum number of instances for autoscaling, ranging from 0 to 20.", ge=0, le=20)
    min_instances: int | None = Field(default=None, description="The minimum number of instances to maintain, ranging from 0 to 5.", ge=0, le=5)
    version: str | None = Field(default=None, description="The model version ID to deploy. Use this to update the deployment to a different version of the model.")
class DeploymentsUpdateRequest(StrictModel):
    """Modify an existing deployment's configuration, including hardware SKU, scaling limits, and model version. Each update increments the deployment's release number."""
    path: DeploymentsUpdateRequestPath
    body: DeploymentsUpdateRequestBody | None = None

# Operation: delete_deployment
class DeploymentsDeleteRequestPath(StrictModel):
    deployment_owner: str = Field(default=..., description="The username or organization name that owns the deployment being deleted.")
    deployment_name: str = Field(default=..., description="The name of the deployment to delete.")
class DeploymentsDeleteRequest(StrictModel):
    """Delete a deployment that has been offline and unused for at least 15 minutes. The operation returns a 204 status code on successful deletion."""
    path: DeploymentsDeleteRequestPath

# Operation: create_deployment_prediction
class DeploymentsPredictionsCreateRequestPath(StrictModel):
    deployment_owner: str = Field(default=..., description="The username or organization name that owns the deployment.")
    deployment_name: str = Field(default=..., description="The name of the deployment to run the prediction against.")
class DeploymentsPredictionsCreateRequestHeader(StrictModel):
    prefer: str | None = Field(default=None, validation_alias="Prefer", serialization_alias="Prefer", description="Set to `wait` or `wait=n` (where n is 1-60 seconds) to hold the request open and wait for the model to complete. Without this header, the prediction starts asynchronously and returns immediately.", pattern='^wait(=([1-9]|[1-9][0-9]|60))?$')
    cancel_after: str | None = Field(default=None, validation_alias="Cancel-After", serialization_alias="Cancel-After", description="Maximum duration the prediction can run before automatic cancellation, measured from creation time. Specify with optional unit suffix: `s` for seconds, `m` for minutes, `h` for hours (e.g., `5m`, `1h30m45s`). Minimum is 5 seconds; defaults to seconds if no unit is provided.")
class DeploymentsPredictionsCreateRequestBody(StrictModel):
    input_: dict[str, Any] = Field(default=..., validation_alias="input", serialization_alias="input", description="A JSON object containing the model's input parameters. The required fields depend on the specific model running on the deployment. Files should be passed as HTTP URLs (for files >256KB or reusable files) or data URLs (for small files ≤256KB).")
    webhook: str | None = Field(default=None, description="An HTTPS URL that receives a POST webhook notification when the prediction updates or completes. The request body will contain the full prediction object. Replicate retries on network failures, so the endpoint must be idempotent.")
    webhook_events_filter: list[Literal["start", "output", "logs", "completed"]] | None = Field(default=None, description="An array of event types that trigger webhook requests: `start` (immediately), `output` (each new output), `logs` (each log line), or `completed` (terminal state). If omitted, defaults to sending on output and completion. Output and log events are throttled to at most once per 500ms.")
class DeploymentsPredictionsCreateRequest(StrictModel):
    """Create a prediction by running a model on a deployment with specified inputs. The request can optionally wait synchronously for results (up to 60 seconds) or return immediately with a prediction ID for asynchronous polling."""
    path: DeploymentsPredictionsCreateRequestPath
    header: DeploymentsPredictionsCreateRequestHeader | None = None
    body: DeploymentsPredictionsCreateRequestBody

# Operation: create_file
class FilesCreateRequestBody(StrictModel):
    content: str = Field(default=..., description="Base64-encoded file content for upload. The raw file content to upload. Provide the binary data of the file you want to store.", json_schema_extra={'format': 'byte'})
    filename: str | None = Field(default=None, description="The name of the file being uploaded. Must be valid UTF-8 and not exceed 255 bytes in length.", max_length=255)
    metadata: dict[str, Any] | None = Field(default=None, description="Optional custom metadata to associate with the file as a JSON object. Defaults to an empty object if not provided.")
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The MIME type of the file content (e.g., application/zip, application/json, image/png). Defaults to application/octet-stream if not specified.")
class FilesCreateRequest(StrictModel):
    """Upload a file with its content and optional metadata. The file is stored and can be referenced by its returned ID for use in other operations."""
    body: FilesCreateRequestBody

# Operation: get_file
class FilesGetRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file to retrieve.")
class FilesGetRequest(StrictModel):
    """Retrieve detailed metadata and information about a specific file by its ID."""
    path: FilesGetRequestPath

# Operation: delete_file
class FilesDeleteRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file to delete. This ID must correspond to an existing file in the system.")
class FilesDeleteRequest(StrictModel):
    """Permanently delete a file by its ID. Once deleted, the file resource will no longer be accessible and subsequent requests will return a 404 Not Found error."""
    path: FilesDeleteRequestPath

# Operation: get_file_download
class FilesDownloadRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file to download.")
class FilesDownloadRequestQuery(StrictModel):
    owner: str = Field(default=..., description="The username of the user or organization that owns and uploaded the file.")
    expiry: int = Field(default=..., description="Unix timestamp (seconds since epoch) indicating when this download URL expires and becomes invalid.", json_schema_extra={'format': 'int64'})
    signature: str = Field(default=..., description="Base64-encoded HMAC-SHA256 signature authenticating the download request. Generated by hashing the string '{owner} {id} {expiry}' with your Files API signing secret.")
class FilesDownloadRequest(StrictModel):
    """Download a file using authenticated access credentials. Requires the file ID, owner information, and a cryptographically signed URL that includes an expiration timestamp."""
    path: FilesDownloadRequestPath
    query: FilesDownloadRequestQuery

# Operation: list_models
class ModelsListRequestQuery(StrictModel):
    sort_by: Literal["model_created_at", "latest_version_created_at"] | None = Field(default=None, description="Field to sort results by: either model creation date or the date of the model's latest version. Defaults to sorting by latest version creation date.")
    sort_direction: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for results: ascending (oldest first) or descending (newest first). Defaults to descending.")
class ModelsListRequest(StrictModel):
    """Retrieve a paginated list of publicly available models, optionally sorted by creation date or latest version update."""
    query: ModelsListRequestQuery | None = None

# Operation: create_model
class ModelsCreateRequestBody(StrictModel):
    cover_image_url: str | None = Field(default=None, description="A URL pointing to an image file to use as the model's cover image on the Replicate platform.")
    description: str | None = Field(default=None, description="A brief description explaining what the model does and its primary use case.")
    github_url: str | None = Field(default=None, description="A URL to the model's source code repository on GitHub.")
    hardware: str = Field(default=..., description="The hardware SKU required to run this model. Valid values can be retrieved from the hardware.list endpoint (e.g., 'cpu', 'gpu-t4').")
    license_url: str | None = Field(default=None, description="A URL to the license governing the model's use and distribution.")
    name: str = Field(default=..., description="The model's name, which must be unique within your user or organization account. Use lowercase alphanumeric characters and hyphens.")
    owner: str = Field(default=..., description="The username or organization name that will own this model. Must match the account associated with your API token.")
    paper_url: str | None = Field(default=None, description="A URL to the academic paper or research publication describing the model's methodology.")
    visibility: Literal["public", "private"] = Field(default=..., description="Controls model visibility: 'public' allows anyone to view and run the model, while 'private' restricts access to account members only.")
class ModelsCreateRequest(StrictModel):
    """Create a new model in your account. Each account is limited to 1,000 models; for iterative improvements, create new versions of an existing model instead."""
    body: ModelsCreateRequestBody

# Operation: search_models
class ModelsSearchRequestBody(StrictModel):
    body: str = Field(default=..., description="The search query string to find matching models. Can include model names, descriptions, or keywords.")
class ModelsSearchRequest(StrictModel):
    """Search for public models on Replicate using a text query. Returns a paginated list of models matching your search criteria."""
    body: ModelsSearchRequestBody

# Operation: get_model
class ModelsGetRequestPath(StrictModel):
    model_owner: str = Field(default=..., description="The username or organization name that owns the model.")
    model_name: str = Field(default=..., description="The unique identifier of the model within the owner's namespace.")
class ModelsGetRequest(StrictModel):
    """Retrieve detailed metadata for a specific model, including its latest version, input/output schemas, and example prediction. Returns comprehensive information about the model's configuration, visibility, and usage statistics."""
    path: ModelsGetRequestPath

# Operation: update_model_metadata
class ModelsUpdateRequestPath(StrictModel):
    model_owner: str = Field(default=..., description="The username or organization name that owns the model.")
    model_name: str = Field(default=..., description="The name of the model to update.")
class ModelsUpdateRequestBody(StrictModel):
    description: str | None = Field(default=None, description="A brief description of the model's purpose and functionality.")
    github_url: str | None = Field(default=None, description="A URL pointing to the model's source code repository on GitHub.")
    license_url: str | None = Field(default=None, description="A URL pointing to the model's license document or license page.")
    paper_url: str | None = Field(default=None, description="A URL pointing to the research paper or academic publication associated with the model.")
    readme: str | None = Field(default=None, description="The README content in Markdown format, typically including usage instructions, examples, and documentation.")
    weights_url: str | None = Field(default=None, description="A URL pointing to the pre-trained model weights or model artifacts, such as on Hugging Face or similar hosting platforms.")
class ModelsUpdateRequest(StrictModel):
    """Update metadata properties for an existing model, including description, documentation, and resource links. Only specified properties are updated; omitted properties remain unchanged."""
    path: ModelsUpdateRequestPath
    body: ModelsUpdateRequestBody | None = None

# Operation: delete_model
class ModelsDeleteRequestPath(StrictModel):
    model_owner: str = Field(default=..., description="The username or organization name that owns the model. You can only delete models you own.")
    model_name: str = Field(default=..., description="The name of the model to delete. The model must be private and have no versions remaining.")
class ModelsDeleteRequest(StrictModel):
    """Permanently delete a private model you own. The model must have no versions associated with it—delete all versions before attempting to delete the model itself."""
    path: ModelsDeleteRequestPath

# Operation: list_model_examples
class ModelsExamplesListRequestPath(StrictModel):
    model_owner: str = Field(default=..., description="The username or organization name that owns the model.")
    model_name: str = Field(default=..., description="The name of the model.")
class ModelsExamplesListRequest(StrictModel):
    """Retrieve all example predictions that were saved by the model author to demonstrate the model's capabilities. Use this to browse illustrative examples; for just the default example, use the get_model operation instead."""
    path: ModelsExamplesListRequestPath

# Operation: create_prediction_for_official_model
class ModelsPredictionsCreateRequestPath(StrictModel):
    model_owner: str = Field(default=..., description="The username or organization name that owns the official model.")
    model_name: str = Field(default=..., description="The name of the official model to run.")
class ModelsPredictionsCreateRequestHeader(StrictModel):
    prefer: str | None = Field(default=None, validation_alias="Prefer", serialization_alias="Prefer", description="Enable synchronous mode by setting to `wait` or `wait=n` where n is the number of seconds (1-60) to wait for the model to finish. If omitted, the request returns immediately.", pattern='^wait(=([1-9]|[1-9][0-9]|60))?$')
    cancel_after: str | None = Field(default=None, validation_alias="Cancel-After", serialization_alias="Cancel-After", description="Maximum duration the prediction can run before automatic cancellation, measured from creation time. Specify as a number with optional unit suffix: `s` for seconds, `m` for minutes, `h` for hours (e.g., `5m`, `1h30m45s`). Minimum is 5 seconds; defaults to seconds if no unit is provided.")
class ModelsPredictionsCreateRequestBody(StrictModel):
    input_: dict[str, Any] = Field(default=..., validation_alias="input", serialization_alias="input", description="The model's input parameters as a JSON object. Structure depends on the specific model being run. Files should be passed as HTTP URLs (for files >256KB or reusable files) or data URLs (for files ≤256KB or one-time use).")
    webhook: str | None = Field(default=None, description="An HTTPS URL that receives a POST webhook notification when the prediction updates or completes. The request body matches the prediction's full state. Replicate retries on network failures, so the endpoint must be idempotent.")
    webhook_events_filter: list[Literal["start", "output", "logs", "completed"]] | None = Field(default=None, description="Filter which events trigger webhook requests: `start` (immediately), `output` (each generation), `logs` (each log line), or `completed` (terminal state). Output and logs events are throttled to at most once per 500ms; start and completed events are always sent.")
class ModelsPredictionsCreateRequest(StrictModel):
    """Create a prediction by running an official model. The request can optionally wait synchronously for up to 60 seconds for the model to complete, or return immediately with a starting status for asynchronous polling."""
    path: ModelsPredictionsCreateRequestPath
    header: ModelsPredictionsCreateRequestHeader | None = None
    body: ModelsPredictionsCreateRequestBody

# Operation: get_model_readme
class ModelsReadmeGetRequestPath(StrictModel):
    model_owner: str = Field(default=..., description="The username or organization name that owns the model.")
    model_name: str = Field(default=..., description="The name of the model to retrieve documentation for.")
class ModelsReadmeGetRequest(StrictModel):
    """Retrieve the README documentation for a specific model. Returns the README content as plain text in Markdown format."""
    path: ModelsReadmeGetRequestPath

# Operation: list_model_versions
class ModelsVersionsListRequestPath(StrictModel):
    model_owner: str = Field(default=..., description="The username or organization name that owns the model. This identifies the model's owner in the Replicate registry.")
    model_name: str = Field(default=..., description="The name of the model. Combined with the model owner, this uniquely identifies which model's versions to retrieve.")
class ModelsVersionsListRequest(StrictModel):
    """Retrieve all versions of a model owned by a specific user or organization, sorted with the most recent version first. Returns paginated results including version metadata and OpenAPI schemas."""
    path: ModelsVersionsListRequestPath

# Operation: get_model_version
class ModelsVersionsGetRequestPath(StrictModel):
    model_owner: str = Field(default=..., description="The username or organization name that owns the model.")
    model_name: str = Field(default=..., description="The name of the model to retrieve version information for.")
    version_id: str = Field(default=..., description="The unique identifier of the specific model version to retrieve.")
class ModelsVersionsGetRequest(StrictModel):
    """Retrieve detailed metadata and schema information for a specific version of a model, including its OpenAPI schema that describes the model's inputs and outputs."""
    path: ModelsVersionsGetRequestPath

# Operation: delete_model_version
class ModelsVersionsDeleteRequestPath(StrictModel):
    model_owner: str = Field(default=..., description="The username or organization name that owns the model. You must be the owner to delete versions.")
    model_name: str = Field(default=..., description="The name of the model containing the version to delete.")
    version_id: str = Field(default=..., description="The unique identifier of the model version to delete. The version cannot be deleted if it's in use by deployments, fine-tuning jobs, other model versions, or has predictions run by other users.")
class ModelsVersionsDeleteRequest(StrictModel):
    """Permanently delete a specific model version and all associated predictions and output files. Deletion is asynchronous and may take several minutes to complete."""
    path: ModelsVersionsDeleteRequestPath

# Operation: create_training
class TrainingsCreateRequestPath(StrictModel):
    model_owner: str = Field(default=..., description="The username or organization name that owns the model being trained.")
    model_name: str = Field(default=..., description="The name of the model to train.")
    version_id: str = Field(default=..., description="The unique identifier of the model version to use as the base for training.")
class TrainingsCreateRequestBody(StrictModel):
    destination: str = Field(default=..., description="The target model location in format `owner/name`. Must be an existing model owned by the requesting user or organization.")
    input_: dict[str, Any] = Field(default=..., validation_alias="input", serialization_alias="input", description="An object containing input parameters for the model's training function. Structure depends on the specific model's training requirements.")
    webhook: str | None = Field(default=None, description="An HTTPS URL that will receive a POST request when the training completes. The request body will contain the final training status. Replicate will retry on network failures, so the endpoint should be idempotent.")
    webhook_events_filter: list[Literal["start", "output", "logs", "completed"]] | None = Field(default=None, description="An array of event types that trigger webhook requests. Valid events are `start` (immediately when training begins), `output` (when training generates outputs), `logs` (when log output is generated), and `completed` (when training reaches a terminal state). If omitted, defaults to sending on outputs and completion.")
class TrainingsCreateRequest(StrictModel):
    """Start a new training job for a model version. The training will create a new version of the model at the specified destination when complete. Since training can take several minutes or longer, use webhooks or polling to track completion."""
    path: TrainingsCreateRequestPath
    body: TrainingsCreateRequestBody

# Operation: list_predictions
class PredictionsListRequestQuery(StrictModel):
    created_after: str | None = Field(default=None, description="Filter to include only predictions created at or after this date-time. Specify in ISO 8601 format (e.g., 2025-01-01T00:00:00Z).", json_schema_extra={'format': 'date-time'})
    created_before: str | None = Field(default=None, description="Filter to include only predictions created before this date-time. Specify in ISO 8601 format (e.g., 2025-02-01T00:00:00Z).", json_schema_extra={'format': 'date-time'})
    source: Literal["web"] | None = Field(default=None, description="Filter predictions by creation source. Use 'web' to show only web-created predictions (limited to the last 14 days). Omit this parameter to include predictions from both API and web sources.")
class PredictionsListRequest(StrictModel):
    """Retrieve a paginated list of all predictions created by your user or organization, including those from both API and web sources. Results are sorted with the most recent prediction first, returning up to 100 records per page."""
    query: PredictionsListRequestQuery | None = None

# Operation: create_prediction
class PredictionsCreateRequestHeader(StrictModel):
    prefer: str | None = Field(default=None, validation_alias="Prefer", serialization_alias="Prefer", description="Enable synchronous mode by setting to `wait` or `wait=n` where n is 1-60 seconds. When set, the request will block and wait for the model to complete within the specified timeout before returning results.", pattern='^wait(=([1-9]|[1-9][0-9]|60))?$')
    cancel_after: str | None = Field(default=None, validation_alias="Cancel-After", serialization_alias="Cancel-After", description="Set a maximum runtime duration for the prediction before automatic cancellation. Accepts durations with optional unit suffixes: seconds (s), minutes (m), or hours (h). Combine units for precision (e.g., `1h30m45s`). Minimum allowed duration is 5 seconds.")
class PredictionsCreateRequestBody(StrictModel):
    input_: dict[str, Any] = Field(default=..., validation_alias="input", serialization_alias="input", description="Required JSON object containing the model's input parameters. Structure depends on the specific model version being run. Files should be passed as HTTP URLs (for files >256KB or reusable files) or data URLs (for small files ≤256KB).")
    version: str = Field(default=..., description="Required identifier for the model or version to execute. Accepts three formats: `owner/model` for official models, `owner/model:version_id` for specific versions, or just the 64-character `version_id` alone.")
    webhook: str | None = Field(default=None, description="HTTPS URL for receiving webhook notifications when the prediction updates or completes. Replicate will POST the prediction state to this URL and may retry on network failures, so the endpoint should be idempotent.")
    webhook_events_filter: list[Literal["start", "output", "logs", "completed"]] | None = Field(default=None, description="Array of event types that trigger webhook requests: `start` (immediately), `output` (each generation), `logs` (log output), or `completed` (terminal state). Omit to receive all events. Output and logs events are throttled to at most once per 500ms.")
class PredictionsCreateRequest(StrictModel):
    """Submit a prediction request to run a model with specified inputs. The request can optionally wait synchronously for results (up to 60 seconds) or return immediately with a prediction ID for asynchronous polling."""
    header: PredictionsCreateRequestHeader | None = None
    body: PredictionsCreateRequestBody

# Operation: get_prediction
class PredictionsGetRequestPath(StrictModel):
    prediction_id: str = Field(default=..., description="The unique identifier of the prediction to retrieve. This ID is returned when a prediction is created and can be used to poll for results or access the prediction details.")
class PredictionsGetRequest(StrictModel):
    """Retrieve the current state and results of a prediction, including its status, output, logs, and performance metrics."""
    path: PredictionsGetRequestPath

# Operation: cancel_prediction
class PredictionsCancelRequestPath(StrictModel):
    prediction_id: str = Field(default=..., description="The unique identifier of the prediction to cancel. This must be a valid prediction ID that is currently in a running or queued state.")
class PredictionsCancelRequest(StrictModel):
    """Cancel an in-progress prediction. This stops the model execution and prevents further processing of the prediction."""
    path: PredictionsCancelRequestPath

# Operation: search_models_collections_and_docs
class SearchRequestQuery(StrictModel):
    query: str = Field(default=..., description="The text query to search for models, collections, and docs. Use keywords or phrases relevant to your search intent (e.g., 'nano banana').")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Must be between 1 and 50; defaults to 20 if not specified.", ge=1, le=50)
class SearchRequest(StrictModel):
    """Search across public models, collections, and documentation using a text query. Results include detailed metadata such as AI-generated descriptions, tags, and relevance scores to help identify the most suitable resources."""
    query: SearchRequestQuery

# Operation: get_training
class TrainingsGetRequestPath(StrictModel):
    training_id: str = Field(default=..., description="The unique identifier of the training job to retrieve.")
class TrainingsGetRequest(StrictModel):
    """Retrieve the current state and results of a training job, including status, metrics, logs, and output artifacts."""
    path: TrainingsGetRequestPath

# Operation: cancel_training
class TrainingsCancelRequestPath(StrictModel):
    training_id: str = Field(default=..., description="The unique identifier of the training session to cancel.")
class TrainingsCancelRequest(StrictModel):
    """Cancel an active or scheduled training session. Once cancelled, the training will no longer be available and participants will be notified of the cancellation."""
    path: TrainingsCancelRequestPath

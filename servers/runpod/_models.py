"""
Runpod Api MCP Server - Pydantic Models

Generated: 2026-05-05 16:14:05 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field, RootModel

__all__ = [
    "CreateContainerRegistryAuthRequest",
    "CreateEndpointRequest",
    "CreateNetworkVolumeRequest",
    "CreatePodRequest",
    "CreateTemplateRequest",
    "DeleteContainerRegistryAuthRequest",
    "DeleteEndpointRequest",
    "DeleteNetworkVolumeRequest",
    "DeletePodRequest",
    "DeleteTemplateRequest",
    "EndpointBillingRequest",
    "GetContainerRegistryAuthRequest",
    "GetEndpointRequest",
    "GetNetworkVolumeRequest",
    "GetPodRequest",
    "GetTemplateRequest",
    "ListEndpointsRequest",
    "ListPodsRequest",
    "ListTemplatesRequest",
    "NetworkVolumeBillingRequest",
    "PodBillingRequest",
    "ResetPodRequest",
    "RestartPodRequest",
    "StartPodRequest",
    "StopPodRequest",
    "UpdateEndpoint2Request",
    "UpdateEndpointRequest",
    "UpdateNetworkVolume2Request",
    "UpdateNetworkVolumeRequest",
    "UpdatePod2Request",
    "UpdatePodRequest",
    "UpdateTemplate2Request",
    "UpdateTemplateRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_pods
class ListPodsRequestQuery(StrictModel):
    compute_type: Literal["GPU", "CPU"] | None = Field(default=None, validation_alias="computeType", serialization_alias="computeType", description="Filter results to only GPU-based or CPU-based Pods.")
    cpu_flavor_id: list[str] | None = Field(default=None, validation_alias="cpuFlavorId", serialization_alias="cpuFlavorId", description="Filter to CPU Pods matching any of the specified CPU flavor identifiers (e.g., cpu3c, cpu5g).")
    data_center_id: list[str] | None = Field(default=None, validation_alias="dataCenterId", serialization_alias="dataCenterId", description="Filter to Pods located in any of the specified RunPod data center regions (e.g., EU-RO-1).")
    desired_status: Literal["RUNNING", "EXITED", "TERMINATED"] | None = Field(default=None, validation_alias="desiredStatus", serialization_alias="desiredStatus", description="Filter to Pods currently in a specific operational state: RUNNING, EXITED, or TERMINATED.")
    endpoint_id: str | None = Field(default=None, validation_alias="endpointId", serialization_alias="endpointId", description="Filter to worker Pods associated with a specific Serverless endpoint ID. Worker Pods are excluded from results by default unless includeWorkers is enabled.", max_length=191)
    gpu_type_id: list[str] | None = Field(default=None, validation_alias="gpuTypeId", serialization_alias="gpuTypeId", description="Filter to Pods with any of the specified GPU types attached (e.g., NVIDIA GeForce RTX 4090, NVIDIA RTX A5000).")
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="Filter to a specific Pod by its unique identifier.")
    image_name: str | None = Field(default=None, validation_alias="imageName", serialization_alias="imageName", description="Filter to Pods created with a specific container image.")
    include_machine: bool | None = Field(default=None, validation_alias="includeMachine", serialization_alias="includeMachine", description="Include detailed information about the physical machine or node the Pod is running on.")
    include_network_volume: bool | None = Field(default=None, validation_alias="includeNetworkVolume", serialization_alias="includeNetworkVolume", description="Include detailed information about any network volume attached to the Pod.")
    include_savings_plans: bool | None = Field(default=None, validation_alias="includeSavingsPlans", serialization_alias="includeSavingsPlans", description="Include information about active savings plans or discounts applied to the Pod.")
    include_template: bool | None = Field(default=None, validation_alias="includeTemplate", serialization_alias="includeTemplate", description="Include information about the Pod template used during creation, if applicable.")
    include_workers: bool | None = Field(default=None, validation_alias="includeWorkers", serialization_alias="includeWorkers", description="Include Serverless worker Pods in the results. By default, only standard Pods are returned.")
    name: str | None = Field(default=None, description="Filter to Pods with a specific name.", max_length=191)
    template_id: str | None = Field(default=None, validation_alias="templateId", serialization_alias="templateId", description="Filter to Pods created from a specific template ID.")
class ListPodsRequest(StrictModel):
    """Retrieve a list of Pods with optional filtering by compute type, hardware specifications, location, status, and other attributes. Supports inclusion of related metadata such as machine details, network volumes, savings plans, and templates."""
    query: ListPodsRequestQuery | None = None

# Operation: create_pod
class CreatePodRequestBody(StrictModel):
    """Input for Pod creation."""
    cloud_type: Literal["SECURE", "COMMUNITY"] | None = Field(default=None, validation_alias="cloudType", serialization_alias="cloudType", description="Cloud environment for the Pod. SECURE provides dedicated infrastructure with guaranteed availability; COMMUNITY offers lower-cost shared resources. Defaults to SECURE.")
    compute_type: Literal["GPU", "CPU"] | None = Field(default=None, validation_alias="computeType", serialization_alias="computeType", description="Compute type for the Pod. GPU Pods include graphics processors and ignore CPU-related settings; CPU Pods are GPU-less and ignore GPU-related settings. Defaults to GPU.")
    country_codes: list[str] | None = Field(default=None, validation_alias="countryCodes", serialization_alias="countryCodes", description="List of ISO 3166-1 alpha-2 country codes where the Pod can be located. If omitted, the Pod can be placed in any country.")
    cpu_flavor_ids: list[Literal["cpu3c", "cpu3g", "cpu3m", "cpu5c", "cpu5g", "cpu5m"]] | None = Field(default=None, validation_alias="cpuFlavorIds", serialization_alias="cpuFlavorIds", description="Ordered list of CPU flavor IDs for CPU Pods. The order determines rental priority; earlier entries are attempted first. Ignored for GPU Pods.")
    data_center_ids: list[Literal["EU-RO-1", "CA-MTL-1", "EU-SE-1", "US-IL-1", "EUR-IS-1", "EU-CZ-1", "US-TX-3", "EUR-IS-2", "US-KS-2", "US-GA-2", "US-WA-1", "US-TX-1", "CA-MTL-3", "EU-NL-1", "US-TX-4", "US-CA-2", "US-NC-1", "OC-AU-1", "US-DE-1", "EUR-IS-3", "CA-MTL-2", "AP-JP-1", "EUR-NO-1", "EU-FR-1", "US-KS-3", "US-GA-1"]] | None = Field(default=None, validation_alias="dataCenterIds", serialization_alias="dataCenterIds", description="Ordered list of data center IDs where the Pod can be located. The order determines rental priority; earlier entries are attempted first. Defaults to a global list of 26 data centers.")
    docker_entrypoint: list[str] | None = Field(default=None, validation_alias="dockerEntrypoint", serialization_alias="dockerEntrypoint", description="Docker ENTRYPOINT override for the container. Pass an empty array to use the image's default ENTRYPOINT. Defaults to empty array.")
    docker_start_cmd: list[str] | None = Field(default=None, validation_alias="dockerStartCmd", serialization_alias="dockerStartCmd", description="Docker CMD override for the container startup. Pass an empty array to use the image's default CMD. Defaults to empty array.")
    env: dict[str, Any] | None = Field(default=None, description="Environment variables to inject into the Pod container as key-value pairs. Defaults to empty object.")
    global_networking: bool | None = Field(default=None, validation_alias="globalNetworking", serialization_alias="globalNetworking", description="Enable global networking for the Pod. Currently available only for On-Demand GPU Pods on select Secure Cloud data centers. Defaults to false.")
    gpu_count: int | None = Field(default=None, validation_alias="gpuCount", serialization_alias="gpuCount", description="Number of GPUs to attach to the Pod. Only applies to GPU Pods. Must be at least 1. Defaults to 1.", ge=1)
    gpu_type_ids: list[Literal["NVIDIA GeForce RTX 4090", "NVIDIA A40", "NVIDIA RTX A5000", "NVIDIA GeForce RTX 5090", "NVIDIA H100 80GB HBM3", "NVIDIA GeForce RTX 3090", "NVIDIA RTX A4500", "NVIDIA L40S", "NVIDIA H200", "NVIDIA L4", "NVIDIA RTX 6000 Ada Generation", "NVIDIA A100-SXM4-80GB", "NVIDIA RTX 4000 Ada Generation", "NVIDIA RTX A6000", "NVIDIA A100 80GB PCIe", "NVIDIA RTX 2000 Ada Generation", "NVIDIA RTX A4000", "NVIDIA RTX PRO 6000 Blackwell Server Edition", "NVIDIA H100 PCIe", "NVIDIA H100 NVL", "NVIDIA L40", "NVIDIA B200", "NVIDIA GeForce RTX 3080 Ti", "NVIDIA RTX PRO 6000 Blackwell Workstation Edition", "NVIDIA GeForce RTX 3080", "NVIDIA GeForce RTX 3070", "AMD Instinct MI300X OAM", "NVIDIA GeForce RTX 4080 SUPER", "Tesla V100-PCIE-16GB", "Tesla V100-SXM2-32GB", "NVIDIA RTX 5000 Ada Generation", "NVIDIA GeForce RTX 4070 Ti", "NVIDIA RTX 4000 SFF Ada Generation", "NVIDIA GeForce RTX 3090 Ti", "NVIDIA RTX A2000", "NVIDIA GeForce RTX 4080", "NVIDIA A30", "NVIDIA GeForce RTX 5080", "Tesla V100-FHHL-16GB", "NVIDIA H200 NVL", "Tesla V100-SXM2-16GB", "NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition", "NVIDIA A5000 Ada", "Tesla V100-PCIE-32GB", "NVIDIA  RTX A4500", "NVIDIA  A30", "NVIDIA GeForce RTX 3080TI", "Tesla T4", "NVIDIA RTX A30"]] | None = Field(default=None, validation_alias="gpuTypeIds", serialization_alias="gpuTypeIds", description="Ordered list of GPU type IDs for GPU Pods. The order determines rental priority; earlier entries are attempted first. Ignored for CPU Pods.")
    image_name: str | None = Field(default=None, validation_alias="imageName", serialization_alias="imageName", description="Container image tag to run on the Pod (e.g., runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04).")
    interruptible: bool | None = Field(default=None, description="Create an interruptible (spot) Pod instead of reserved. Interruptible Pods cost less but can be stopped anytime to free resources. Defaults to false (reserved).")
    locked: bool | None = Field(default=None, description="Lock the Pod to prevent stopping or resetting. Defaults to false (unlocked).")
    min_disk_bandwidth_m_bps: float | None = Field(default=None, validation_alias="minDiskBandwidthMBps", serialization_alias="minDiskBandwidthMBps", description="Minimum disk bandwidth in megabytes per second (MBps) required for the Pod.")
    min_download_mbps: float | None = Field(default=None, validation_alias="minDownloadMbps", serialization_alias="minDownloadMbps", description="Minimum download speed in megabits per second (Mbps) required for the Pod.")
    min_ram_per_gpu: int | None = Field(default=None, validation_alias="minRAMPerGPU", serialization_alias="minRAMPerGPU", description="Minimum RAM in gigabytes (GB) per GPU for GPU Pods. Defaults to 8 GB per GPU.")
    min_upload_mbps: float | None = Field(default=None, validation_alias="minUploadMbps", serialization_alias="minUploadMbps", description="Minimum upload speed in megabits per second (Mbps) required for the Pod.")
    min_vcpu_per_gpu: int | None = Field(default=None, validation_alias="minVCPUPerGPU", serialization_alias="minVCPUPerGPU", description="Minimum virtual CPUs per GPU for GPU Pods. Defaults to 2 vCPUs per GPU.")
    name: str | None = Field(default=None, description="User-defined name for the Pod. Does not need to be unique. Maximum 191 characters. Defaults to 'my pod'.", max_length=191)
    ports: list[str] | None = Field(default=None, description="List of exposed ports in format [port_number]/[protocol], where protocol is either 'http' or 'tcp' (e.g., ['8888/http', '22/tcp']).")
    support_public_ip: bool | None = Field(default=None, validation_alias="supportPublicIp", serialization_alias="supportPublicIp", description="For Community Cloud Pods, set to true to request a public IP address. On Secure Cloud, Pods always have public IPs. Defaults to null (may not have public IP on Community Cloud).")
    template_id: str | None = Field(default=None, validation_alias="templateId", serialization_alias="templateId", description="Unique identifier of a Pod template to use for creation. If provided, the Pod is created from this template.")
    vcpu_count: int | None = Field(default=None, validation_alias="vcpuCount", serialization_alias="vcpuCount", description="Number of virtual CPUs to allocate to the Pod. Only applies to CPU Pods. Defaults to 2 vCPUs.")
class CreatePodRequest(StrictModel):
    """Create and optionally deploy a new Pod with configurable compute resources, networking, and deployment settings. Supports both GPU and CPU Pods across Secure Cloud and Community Cloud environments."""
    body: CreatePodRequestBody | None = None

# Operation: get_pod
class GetPodRequestPath(StrictModel):
    pod_id: str = Field(default=..., validation_alias="podId", serialization_alias="podId", description="The unique identifier of the Pod to retrieve.")
class GetPodRequestQuery(StrictModel):
    include_machine: bool | None = Field(default=None, validation_alias="includeMachine", serialization_alias="includeMachine", description="When enabled, includes details about the machine the Pod is running on. Defaults to false.")
    include_network_volume: bool | None = Field(default=None, validation_alias="includeNetworkVolume", serialization_alias="includeNetworkVolume", description="When enabled, includes information about any network volume attached to the Pod. Defaults to false.")
    include_savings_plans: bool | None = Field(default=None, validation_alias="includeSavingsPlans", serialization_alias="includeSavingsPlans", description="When enabled, includes details about savings plans applied to the Pod. Defaults to false.")
    include_template: bool | None = Field(default=None, validation_alias="includeTemplate", serialization_alias="includeTemplate", description="When enabled, includes information about the template used by the Pod, if one exists. Defaults to false.")
    include_workers: bool | None = Field(default=None, validation_alias="includeWorkers", serialization_alias="includeWorkers", description="When enabled, includes Pods that are Serverless workers in the results. Defaults to false.")
class GetPodRequest(StrictModel):
    """Retrieve a single Pod by its ID with optional related resource information. Use include parameters to expand the response with machine, network volume, savings plans, template, or worker details."""
    path: GetPodRequestPath
    query: GetPodRequestQuery | None = None

# Operation: update_pod
class UpdatePodRequestPath(StrictModel):
    pod_id: str = Field(default=..., validation_alias="podId", serialization_alias="podId", description="The unique identifier of the Pod to update.")
class UpdatePodRequestBody(StrictModel):
    """Form data to update a Pod."""
    docker_entrypoint: list[str] | None = Field(default=None, validation_alias="dockerEntrypoint", serialization_alias="dockerEntrypoint", description="Override the Docker image's ENTRYPOINT instruction. Provide as an array of command segments (e.g., ['python', '-m', 'server']). An empty array uses the image's default ENTRYPOINT.")
    docker_start_cmd: list[str] | None = Field(default=None, validation_alias="dockerStartCmd", serialization_alias="dockerStartCmd", description="Override the Docker image's CMD instruction. Provide as an array of command segments (e.g., ['--port', '8080']). An empty array uses the image's default CMD.")
    env: dict[str, Any] | None = Field(default=None, description="Environment variables to set in the Pod runtime, provided as key-value pairs (e.g., {'ENV_VAR': 'value'}).")
    global_networking: bool | None = Field(default=None, validation_alias="globalNetworking", serialization_alias="globalNetworking", description="Enable global networking for the Pod. Currently available only for On-Demand GPU Pods on select Secure Cloud data centers.")
    image_name: str | None = Field(default=None, validation_alias="imageName", serialization_alias="imageName", description="The container image tag to run on the Pod (e.g., 'runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04').")
    locked: bool | None = Field(default=None, description="Lock the Pod to prevent stopping or resetting. Useful for protecting long-running workloads from accidental interruption.")
    name: str | None = Field(default=None, description="A user-defined name for the Pod. Names do not need to be unique and are limited to 191 characters.", max_length=191)
    ports: list[str] | None = Field(default=None, description="List of ports to expose on the Pod. Each port is specified as 'port_number/protocol' where protocol is either 'http' or 'tcp' (e.g., ['8888/http', '22/tcp']).")
class UpdatePodRequest(StrictModel):
    """Update Pod configuration settings such as Docker image, environment variables, networking, and port mappings. Changes may trigger a Pod reset depending on the parameters modified."""
    path: UpdatePodRequestPath
    body: UpdatePodRequestBody | None = None

# Operation: delete_pod
class DeletePodRequestPath(StrictModel):
    pod_id: str = Field(default=..., validation_alias="podId", serialization_alias="podId", description="The unique identifier of the Pod to delete.")
class DeletePodRequest(StrictModel):
    """Permanently delete a Pod by its ID. This operation removes the Pod and cannot be undone."""
    path: DeletePodRequestPath

# Operation: update_pod_request
class UpdatePod2RequestPath(StrictModel):
    pod_id: str = Field(default=..., validation_alias="podId", serialization_alias="podId", description="The unique identifier of the Pod to update.")
class UpdatePod2RequestBody(StrictModel):
    """Form data to update a Pod."""
    docker_entrypoint: list[str] | None = Field(default=None, validation_alias="dockerEntrypoint", serialization_alias="dockerEntrypoint", description="Override the Docker image's ENTRYPOINT instruction. Provide as an array of command arguments, or use an empty array to use the image's default ENTRYPOINT.")
    docker_start_cmd: list[str] | None = Field(default=None, validation_alias="dockerStartCmd", serialization_alias="dockerStartCmd", description="Override the Docker image's CMD instruction. Provide as an array of command arguments, or use an empty array to use the image's default CMD.")
    env: dict[str, Any] | None = Field(default=None, description="Environment variables to set in the Pod container, provided as key-value pairs (e.g., {'ENV_VAR': 'value'}).")
    global_networking: bool | None = Field(default=None, validation_alias="globalNetworking", serialization_alias="globalNetworking", description="Enable global networking for the Pod. Currently supported only for On-Demand GPU Pods on select Secure Cloud data centers.")
    image_name: str | None = Field(default=None, validation_alias="imageName", serialization_alias="imageName", description="The container image tag to run on the Pod (e.g., 'runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04').")
    locked: bool | None = Field(default=None, description="Lock the Pod to prevent stopping or resetting. Useful for protecting long-running workloads from accidental interruption.")
    name: str | None = Field(default=None, description="A user-defined name for the Pod. Names do not need to be unique and are limited to 191 characters.", max_length=191)
    ports: list[str] | None = Field(default=None, description="List of ports to expose on the Pod. Each port is specified as 'port_number/protocol' where protocol is either 'http' or 'tcp' (e.g., ['8888/http', '22/tcp']).")
class UpdatePod2Request(StrictModel):
    """Update configuration settings for an existing Pod, including container image, environment variables, networking, and exposed ports."""
    path: UpdatePod2RequestPath
    body: UpdatePod2RequestBody | None = None

# Operation: start_pod
class StartPodRequestPath(StrictModel):
    pod_id: str = Field(default=..., validation_alias="podId", serialization_alias="podId", description="The unique identifier of the Pod to start or resume.")
class StartPodRequest(StrictModel):
    """Start or resume a Pod that is currently stopped or paused. This operation transitions the Pod to a running state."""
    path: StartPodRequestPath

# Operation: stop_pod
class StopPodRequestPath(StrictModel):
    pod_id: str = Field(default=..., validation_alias="podId", serialization_alias="podId", description="The unique identifier of the Pod to stop.")
class StopPodRequest(StrictModel):
    """Stop a running Pod, halting its execution and resources. This operation gracefully terminates the Pod identified by the provided ID."""
    path: StopPodRequestPath

# Operation: reset_pod
class ResetPodRequestPath(StrictModel):
    pod_id: str = Field(default=..., validation_alias="podId", serialization_alias="podId", description="The unique identifier of the Pod to reset.")
class ResetPodRequest(StrictModel):
    """Reset a Pod to its initial state, clearing any runtime state or configuration changes. This operation restarts the Pod and restores it to a clean state."""
    path: ResetPodRequestPath

# Operation: restart_pod
class RestartPodRequestPath(StrictModel):
    pod_id: str = Field(default=..., validation_alias="podId", serialization_alias="podId", description="The unique identifier of the Pod to restart.")
class RestartPodRequest(StrictModel):
    """Restart a running Pod, causing it to stop and start again. This operation is useful for refreshing a Pod's state or recovering from transient issues."""
    path: RestartPodRequestPath

# Operation: list_endpoints
class ListEndpointsRequestQuery(StrictModel):
    include_template: bool | None = Field(default=None, validation_alias="includeTemplate", serialization_alias="includeTemplate", description="When enabled, includes template information for each endpoint. Defaults to false.")
    include_workers: bool | None = Field(default=None, validation_alias="includeWorkers", serialization_alias="includeWorkers", description="When enabled, includes details about workers currently running on each endpoint. Defaults to false.")
class ListEndpointsRequest(StrictModel):
    """Retrieves a list of all available endpoints. Optionally include details about the templates used to create endpoints and the workers currently running on them."""
    query: ListEndpointsRequestQuery | None = None

# Operation: create_serverless_endpoint
class CreateEndpointRequestBody(StrictModel):
    """Create a new endpoint."""
    compute_type: Literal["GPU", "CPU"] | None = Field(default=None, validation_alias="computeType", serialization_alias="computeType", description="Compute resource type for workers: GPU for GPU-accelerated inference, or CPU for CPU-only workloads. GPU-related properties are ignored for CPU endpoints and vice versa. Defaults to GPU.")
    cpu_flavor_ids: list[Literal["cpu3c", "cpu3g", "cpu5c", "cpu5g"]] | None = Field(default=None, validation_alias="cpuFlavorIds", serialization_alias="cpuFlavorIds", description="List of RunPod CPU flavor IDs available for CPU endpoints. Order determines rental preference priority when scaling workers.")
    data_center_ids: list[Literal["EU-RO-1", "CA-MTL-1", "EU-SE-1", "US-IL-1", "EUR-IS-1", "EU-CZ-1", "US-TX-3", "EUR-IS-2", "US-KS-2", "US-GA-2", "US-WA-1", "US-TX-1", "CA-MTL-3", "EU-NL-1", "US-TX-4", "US-CA-2", "US-NC-1", "OC-AU-1", "US-DE-1", "EUR-IS-3", "CA-MTL-2", "AP-JP-1", "EUR-NO-1", "EU-FR-1", "US-KS-3", "US-GA-1"]] | None = Field(default=None, validation_alias="dataCenterIds", serialization_alias="dataCenterIds", description="List of RunPod data center IDs where workers can be deployed. Order determines preference priority. Defaults to all available global data centers.")
    gpu_count: int | None = Field(default=None, validation_alias="gpuCount", serialization_alias="gpuCount", description="Number of GPUs per worker for GPU endpoints. Must be at least 1. Defaults to 1.", ge=1)
    gpu_type_ids: list[Literal["NVIDIA GeForce RTX 4090", "NVIDIA A40", "NVIDIA RTX A5000", "NVIDIA GeForce RTX 5090", "NVIDIA H100 80GB HBM3", "NVIDIA GeForce RTX 3090", "NVIDIA RTX A4500", "NVIDIA L40S", "NVIDIA H200", "NVIDIA L4", "NVIDIA RTX 6000 Ada Generation", "NVIDIA A100-SXM4-80GB", "NVIDIA RTX 4000 Ada Generation", "NVIDIA RTX A6000", "NVIDIA A100 80GB PCIe", "NVIDIA RTX 2000 Ada Generation", "NVIDIA RTX A4000", "NVIDIA RTX PRO 6000 Blackwell Server Edition", "NVIDIA H100 PCIe", "NVIDIA H100 NVL", "NVIDIA L40", "NVIDIA B200", "NVIDIA GeForce RTX 3080 Ti", "NVIDIA RTX PRO 6000 Blackwell Workstation Edition", "NVIDIA GeForce RTX 3080", "NVIDIA GeForce RTX 3070", "AMD Instinct MI300X OAM", "NVIDIA GeForce RTX 4080 SUPER", "Tesla V100-PCIE-16GB", "Tesla V100-SXM2-32GB", "NVIDIA RTX 5000 Ada Generation", "NVIDIA GeForce RTX 4070 Ti", "NVIDIA RTX 4000 SFF Ada Generation", "NVIDIA GeForce RTX 3090 Ti", "NVIDIA RTX A2000", "NVIDIA GeForce RTX 4080", "NVIDIA A30", "NVIDIA GeForce RTX 5080", "Tesla V100-FHHL-16GB", "NVIDIA H200 NVL", "Tesla V100-SXM2-16GB", "NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition", "NVIDIA A5000 Ada", "Tesla V100-PCIE-32GB", "NVIDIA  RTX A4500", "NVIDIA  A30", "NVIDIA GeForce RTX 3080TI", "Tesla T4", "NVIDIA RTX A30"]] | None = Field(default=None, validation_alias="gpuTypeIds", serialization_alias="gpuTypeIds", description="List of RunPod GPU type IDs available for GPU endpoints. Order determines rental preference priority when scaling workers.")
    name: str | None = Field(default=None, description="User-defined name for the endpoint. Does not need to be unique. Maximum 191 characters.", max_length=191)
    network_volume_ids: list[str] | None = Field(default=None, validation_alias="networkVolumeIds", serialization_alias="networkVolumeIds", description="List of network volume IDs to attach to the endpoint. Enables multi-region endpoints to access shared storage across data centers.")
    scaler_type: Literal["QUEUE_DELAY", "REQUEST_COUNT"] | None = Field(default=None, validation_alias="scalerType", serialization_alias="scalerType", description="Scaling strategy: QUEUE_DELAY scales workers when requests exceed maximum latency tolerance, REQUEST_COUNT scales based on request queue depth. Defaults to QUEUE_DELAY.")
    scaler_value: int | None = Field(default=None, validation_alias="scalerValue", serialization_alias="scalerValue", description="Scaling threshold: for QUEUE_DELAY, maximum seconds a request waits before scaling up; for REQUEST_COUNT, requests per worker ratio. Must be at least 1. Defaults to 4.", ge=1)
    template_id: str = Field(default=..., validation_alias="templateId", serialization_alias="templateId", description="Unique identifier of the template defining the container image and runtime configuration for workers.")
    vcpu_count: int | None = Field(default=None, validation_alias="vcpuCount", serialization_alias="vcpuCount", description="Number of vCPUs allocated per worker for CPU endpoints. Defaults to 2.")
    workers_max: int | None = Field(default=None, validation_alias="workersMax", serialization_alias="workersMax", description="Maximum number of concurrent workers. Must be 0 or greater. Set to 0 for unlimited scaling.", ge=0)
    workers_min: int | None = Field(default=None, validation_alias="workersMin", serialization_alias="workersMin", description="Minimum number of always-running workers. Must be 0 or greater. These workers run continuously at reduced cost even with no active requests.", ge=0)
class CreateEndpointRequest(StrictModel):
    """Create a new Serverless endpoint for running containerized workloads. Configure compute resources (GPU or CPU), scaling behavior, worker limits, and data center preferences to match your inference workload requirements."""
    body: CreateEndpointRequestBody

# Operation: get_endpoint
class GetEndpointRequestPath(StrictModel):
    endpoint_id: str = Field(default=..., validation_alias="endpointId", serialization_alias="endpointId", description="The unique identifier of the endpoint to retrieve.")
class GetEndpointRequestQuery(StrictModel):
    include_template: bool | None = Field(default=None, validation_alias="includeTemplate", serialization_alias="includeTemplate", description="When enabled, includes detailed information about the template that was used to create this endpoint. Defaults to false.")
    include_workers: bool | None = Field(default=None, validation_alias="includeWorkers", serialization_alias="includeWorkers", description="When enabled, includes information about all workers currently running on this endpoint. Defaults to false.")
class GetEndpointRequest(StrictModel):
    """Retrieve a single endpoint by its ID. Optionally include details about the template used to create it and the workers currently running on it."""
    path: GetEndpointRequestPath
    query: GetEndpointRequestQuery | None = None

# Operation: update_endpoint
class UpdateEndpointRequestPath(StrictModel):
    endpoint_id: str = Field(default=..., validation_alias="endpointId", serialization_alias="endpointId", description="The unique identifier of the endpoint to update.")
class UpdateEndpointRequestBody(StrictModel):
    """Update an endpoint."""
    cpu_flavor_ids: list[Literal["cpu3c", "cpu3g", "cpu5c", "cpu5g"]] | None = Field(default=None, validation_alias="cpuFlavorIds", serialization_alias="cpuFlavorIds", description="For CPU endpoints, an ordered list of RunPod CPU flavor IDs to attach to workers. The list order determines rental priority.")
    data_center_ids: list[Literal["EU-RO-1", "CA-MTL-1", "EU-SE-1", "US-IL-1", "EUR-IS-1", "EU-CZ-1", "US-TX-3", "EUR-IS-2", "US-KS-2", "US-GA-2", "US-WA-1", "US-TX-1", "CA-MTL-3", "EU-NL-1", "US-TX-4", "US-CA-2", "US-NC-1", "OC-AU-1", "US-DE-1", "EUR-IS-3", "CA-MTL-2", "AP-JP-1", "EUR-NO-1", "EU-FR-1", "US-KS-3", "US-GA-1"]] | None = Field(default=None, validation_alias="dataCenterIds", serialization_alias="dataCenterIds", description="An ordered list of RunPod data center IDs where workers can be deployed. Defaults to all available global data centers if not specified.")
    gpu_count: int | None = Field(default=None, validation_alias="gpuCount", serialization_alias="gpuCount", description="For GPU endpoints, the number of GPUs to attach to each worker. Must be at least 1.", ge=1)
    gpu_type_ids: list[Literal["NVIDIA GeForce RTX 4090", "NVIDIA A40", "NVIDIA RTX A5000", "NVIDIA GeForce RTX 5090", "NVIDIA H100 80GB HBM3", "NVIDIA GeForce RTX 3090", "NVIDIA RTX A4500", "NVIDIA L40S", "NVIDIA H200", "NVIDIA L4", "NVIDIA RTX 6000 Ada Generation", "NVIDIA A100-SXM4-80GB", "NVIDIA RTX 4000 Ada Generation", "NVIDIA RTX A6000", "NVIDIA A100 80GB PCIe", "NVIDIA RTX 2000 Ada Generation", "NVIDIA RTX A4000", "NVIDIA RTX PRO 6000 Blackwell Server Edition", "NVIDIA H100 PCIe", "NVIDIA H100 NVL", "NVIDIA L40", "NVIDIA B200", "NVIDIA GeForce RTX 3080 Ti", "NVIDIA RTX PRO 6000 Blackwell Workstation Edition", "NVIDIA GeForce RTX 3080", "NVIDIA GeForce RTX 3070", "AMD Instinct MI300X OAM", "NVIDIA GeForce RTX 4080 SUPER", "Tesla V100-PCIE-16GB", "Tesla V100-SXM2-32GB", "NVIDIA RTX 5000 Ada Generation", "NVIDIA GeForce RTX 4070 Ti", "NVIDIA RTX 4000 SFF Ada Generation", "NVIDIA GeForce RTX 3090 Ti", "NVIDIA RTX A2000", "NVIDIA GeForce RTX 4080", "NVIDIA A30", "NVIDIA GeForce RTX 5080", "Tesla V100-FHHL-16GB", "NVIDIA H200 NVL", "Tesla V100-SXM2-16GB", "NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition", "NVIDIA A5000 Ada", "Tesla V100-PCIE-32GB", "NVIDIA  RTX A4500", "NVIDIA  A30", "NVIDIA GeForce RTX 3080TI", "Tesla T4", "NVIDIA RTX A30"]] | None = Field(default=None, validation_alias="gpuTypeIds", serialization_alias="gpuTypeIds", description="For GPU endpoints, an ordered list of RunPod GPU type IDs to attach to workers. The list order determines rental priority.")
    name: str | None = Field(default=None, description="A user-friendly name for the endpoint. Names do not need to be unique and can be up to 191 characters.", max_length=191)
    network_volume_ids: list[str] | None = Field(default=None, validation_alias="networkVolumeIds", serialization_alias="networkVolumeIds", description="A list of network volume IDs to attach to the endpoint, enabling multi-region storage access.")
    scaler_type: Literal["QUEUE_DELAY", "REQUEST_COUNT"] | None = Field(default=None, validation_alias="scalerType", serialization_alias="scalerType", description="The autoscaling strategy: QUEUE_DELAY scales workers when requests exceed a latency threshold, while REQUEST_COUNT scales based on queue depth divided by a target ratio.")
    scaler_value: int | None = Field(default=None, validation_alias="scalerValue", serialization_alias="scalerValue", description="For QUEUE_DELAY scaling, the maximum seconds a request can wait before triggering a new worker. For REQUEST_COUNT scaling, the target number of requests per worker. Must be at least 1.", ge=1)
    template_id: str | None = Field(default=None, validation_alias="templateId", serialization_alias="templateId", description="The template ID used to configure the endpoint's runtime environment and dependencies.")
    vcpu_count: int | None = Field(default=None, validation_alias="vcpuCount", serialization_alias="vcpuCount", description="For CPU endpoints, the number of vCPUs allocated to each worker. Defaults to 2.")
    workers_max: int | None = Field(default=None, validation_alias="workersMax", serialization_alias="workersMax", description="The maximum number of workers that can run simultaneously. Must be 0 or greater.", ge=0)
    workers_min: int | None = Field(default=None, validation_alias="workersMin", serialization_alias="workersMin", description="The minimum number of workers that always run, even with no active requests. These are charged at a lower rate. Must be 0 or greater.", ge=0)
class UpdateEndpointRequest(StrictModel):
    """Modify configuration settings for a Serverless endpoint, including scaling behavior, resource allocation, worker limits, and attached volumes."""
    path: UpdateEndpointRequestPath
    body: UpdateEndpointRequestBody | None = None

# Operation: delete_endpoint
class DeleteEndpointRequestPath(StrictModel):
    endpoint_id: str = Field(default=..., validation_alias="endpointId", serialization_alias="endpointId", description="The unique identifier of the endpoint to delete.")
class DeleteEndpointRequest(StrictModel):
    """Permanently delete an endpoint by its ID. This action cannot be undone and will remove the endpoint from the system."""
    path: DeleteEndpointRequestPath

# Operation: update_endpoint_async
class UpdateEndpoint2RequestPath(StrictModel):
    endpoint_id: str = Field(default=..., validation_alias="endpointId", serialization_alias="endpointId", description="The unique identifier of the endpoint to update.")
class UpdateEndpoint2RequestBody(StrictModel):
    """Update an endpoint."""
    cpu_flavor_ids: list[Literal["cpu3c", "cpu3g", "cpu5c", "cpu5g"]] | None = Field(default=None, validation_alias="cpuFlavorIds", serialization_alias="cpuFlavorIds", description="For CPU endpoints, an ordered list of RunPod CPU flavor IDs available for worker allocation. Earlier flavors in the list are prioritized for rental.")
    data_center_ids: list[Literal["EU-RO-1", "CA-MTL-1", "EU-SE-1", "US-IL-1", "EUR-IS-1", "EU-CZ-1", "US-TX-3", "EUR-IS-2", "US-KS-2", "US-GA-2", "US-WA-1", "US-TX-1", "CA-MTL-3", "EU-NL-1", "US-TX-4", "US-CA-2", "US-NC-1", "OC-AU-1", "US-DE-1", "EUR-IS-3", "CA-MTL-2", "AP-JP-1", "EUR-NO-1", "EU-FR-1", "US-KS-3", "US-GA-1"]] | None = Field(default=None, validation_alias="dataCenterIds", serialization_alias="dataCenterIds", description="An ordered list of RunPod data center IDs where workers can be deployed. Earlier data centers are prioritized. Defaults to a global set of 26 data centers across multiple regions.")
    gpu_count: int | None = Field(default=None, validation_alias="gpuCount", serialization_alias="gpuCount", description="For GPU endpoints, the number of GPUs to attach to each worker. Must be at least 1. Defaults to 1 GPU per worker.", ge=1)
    gpu_type_ids: list[Literal["NVIDIA GeForce RTX 4090", "NVIDIA A40", "NVIDIA RTX A5000", "NVIDIA GeForce RTX 5090", "NVIDIA H100 80GB HBM3", "NVIDIA GeForce RTX 3090", "NVIDIA RTX A4500", "NVIDIA L40S", "NVIDIA H200", "NVIDIA L4", "NVIDIA RTX 6000 Ada Generation", "NVIDIA A100-SXM4-80GB", "NVIDIA RTX 4000 Ada Generation", "NVIDIA RTX A6000", "NVIDIA A100 80GB PCIe", "NVIDIA RTX 2000 Ada Generation", "NVIDIA RTX A4000", "NVIDIA RTX PRO 6000 Blackwell Server Edition", "NVIDIA H100 PCIe", "NVIDIA H100 NVL", "NVIDIA L40", "NVIDIA B200", "NVIDIA GeForce RTX 3080 Ti", "NVIDIA RTX PRO 6000 Blackwell Workstation Edition", "NVIDIA GeForce RTX 3080", "NVIDIA GeForce RTX 3070", "AMD Instinct MI300X OAM", "NVIDIA GeForce RTX 4080 SUPER", "Tesla V100-PCIE-16GB", "Tesla V100-SXM2-32GB", "NVIDIA RTX 5000 Ada Generation", "NVIDIA GeForce RTX 4070 Ti", "NVIDIA RTX 4000 SFF Ada Generation", "NVIDIA GeForce RTX 3090 Ti", "NVIDIA RTX A2000", "NVIDIA GeForce RTX 4080", "NVIDIA A30", "NVIDIA GeForce RTX 5080", "Tesla V100-FHHL-16GB", "NVIDIA H200 NVL", "Tesla V100-SXM2-16GB", "NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition", "NVIDIA A5000 Ada", "Tesla V100-PCIE-32GB", "NVIDIA  RTX A4500", "NVIDIA  A30", "NVIDIA GeForce RTX 3080TI", "Tesla T4", "NVIDIA RTX A30"]] | None = Field(default=None, validation_alias="gpuTypeIds", serialization_alias="gpuTypeIds", description="For GPU endpoints, an ordered list of RunPod GPU type IDs available for worker allocation. Earlier types in the list are prioritized for rental.")
    name: str | None = Field(default=None, description="A user-friendly name for the endpoint. Names do not need to be unique and can be up to 191 characters.", max_length=191)
    network_volume_ids: list[str] | None = Field(default=None, validation_alias="networkVolumeIds", serialization_alias="networkVolumeIds", description="A list of network volume IDs to attach to the endpoint. Supports multiple volumes for multi-region deployments.")
    scaler_type: Literal["QUEUE_DELAY", "REQUEST_COUNT"] | None = Field(default=None, validation_alias="scalerType", serialization_alias="scalerType", description="The autoscaling strategy: QUEUE_DELAY scales workers when requests exceed a latency threshold, while REQUEST_COUNT scales based on queue depth divided by a target ratio. Defaults to QUEUE_DELAY.")
    scaler_value: int | None = Field(default=None, validation_alias="scalerValue", serialization_alias="scalerValue", description="For QUEUE_DELAY scaling, the maximum seconds a request can wait before triggering a new worker. For REQUEST_COUNT scaling, the target number of requests per worker. Must be at least 1. Defaults to 4.", ge=1)
    template_id: str | None = Field(default=None, validation_alias="templateId", serialization_alias="templateId", description="The template ID used to configure the endpoint's runtime environment and dependencies.")
    vcpu_count: int | None = Field(default=None, validation_alias="vcpuCount", serialization_alias="vcpuCount", description="For CPU endpoints, the number of vCPUs allocated to each worker. Defaults to 2 vCPUs per worker.")
    workers_max: int | None = Field(default=None, validation_alias="workersMax", serialization_alias="workersMax", description="The maximum number of workers that can run simultaneously. Must be 0 or greater. Set to 0 for unlimited scaling.", ge=0)
    workers_min: int | None = Field(default=None, validation_alias="workersMin", serialization_alias="workersMin", description="The minimum number of workers that always run, even with no active requests. These workers are charged at a lower rate. Must be 0 or greater.", ge=0)
class UpdateEndpoint2Request(StrictModel):
    """Update configuration for a Serverless endpoint, including scaling behavior, resource allocation, and deployment settings. Changes apply to all future workers spawned on this endpoint."""
    path: UpdateEndpoint2RequestPath
    body: UpdateEndpoint2RequestBody | None = None

# Operation: list_templates
class ListTemplatesRequestQuery(StrictModel):
    include_endpoint_bound_templates: bool | None = Field(default=None, validation_alias="includeEndpointBoundTemplates", serialization_alias="includeEndpointBoundTemplates", description="Include templates that are bound to Serverless endpoints in the response. Disabled by default.")
    include_public_templates: bool | None = Field(default=None, validation_alias="includePublicTemplates", serialization_alias="includePublicTemplates", description="Include community-made public templates in the response. Disabled by default.")
    include_runpod_templates: bool | None = Field(default=None, validation_alias="includeRunpodTemplates", serialization_alias="includeRunpodTemplates", description="Include official Runpod templates in the response. Disabled by default.")
class ListTemplatesRequest(StrictModel):
    """Retrieve available templates with optional filtering to include endpoint-bound, community, and official Runpod templates. By default, returns only your personal templates."""
    query: ListTemplatesRequestQuery | None = None

# Operation: create_template
class CreateTemplateRequestBody(StrictModel):
    """Create a new template."""
    category: Literal["NVIDIA", "AMD", "CPU"] | None = Field(default=None, description="The compute hardware category for this template. Choose NVIDIA for GPU acceleration, AMD for AMD GPUs, or CPU for CPU-only workloads. Defaults to NVIDIA.")
    docker_entrypoint: list[str] | None = Field(default=None, validation_alias="dockerEntrypoint", serialization_alias="dockerEntrypoint", description="Override the Docker image's ENTRYPOINT instruction. Provide as an array of command segments (e.g., ['/bin/bash', '-c']). Leave empty to use the image's default ENTRYPOINT.")
    docker_start_cmd: list[str] | None = Field(default=None, validation_alias="dockerStartCmd", serialization_alias="dockerStartCmd", description="Override the Docker image's CMD instruction. Provide as an array of command segments. Leave empty to use the image's default CMD.")
    env: dict[str, Any] | None = Field(default=None, description="Environment variables to inject into the container at runtime. Provide as key-value pairs (e.g., {'ENV_VAR': 'value'}).")
    image_name: str = Field(default=..., validation_alias="imageName", serialization_alias="imageName", description="The Docker image to use for this template, specified as a registry path (e.g., 'nvidia/cuda:12.0' or 'myregistry.com/myimage:latest'). Required.")
    is_public: bool | None = Field(default=None, validation_alias="isPublic", serialization_alias="isPublic", description="Make this template visible to other RunPod users. Only applies to Pod templates. Defaults to private (false).")
    is_serverless: bool | None = Field(default=None, validation_alias="isServerless", serialization_alias="isServerless", description="Specify whether this template is for a Serverless worker (true) or a standard Pod (false). Defaults to Pod (false).")
    name: str = Field(default=..., description="A human-readable name for this template. Used for identification in the RunPod UI and API. Required.")
    ports: list[str] | None = Field(default=None, description="List of network ports to expose on the Pod. Each port is specified as 'port_number/protocol' where protocol is either 'http' or 'tcp' (e.g., ['8888/http', '22/tcp']).")
    readme: str | None = Field(default=None, description="Documentation for this template in Markdown format. Displayed to users who select this template. Defaults to empty.")
class CreateTemplateRequest(StrictModel):
    """Create a new Docker-based template for RunPod Pods or Serverless workers. Templates define the compute environment, Docker image, runtime configuration, and exposed ports for containerized workloads."""
    body: CreateTemplateRequestBody

# Operation: get_template
class GetTemplateRequestPath(StrictModel):
    template_id: str = Field(default=..., validation_alias="templateId", serialization_alias="templateId", description="The unique identifier of the template to retrieve.")
class GetTemplateRequestQuery(StrictModel):
    include_endpoint_bound_templates: bool | None = Field(default=None, validation_alias="includeEndpointBoundTemplates", serialization_alias="includeEndpointBoundTemplates", description="Whether to include templates that are bound to Serverless endpoints in the response. Defaults to false.")
    include_public_templates: bool | None = Field(default=None, validation_alias="includePublicTemplates", serialization_alias="includePublicTemplates", description="Whether to include community-made public templates in the response. Defaults to false.")
    include_runpod_templates: bool | None = Field(default=None, validation_alias="includeRunpodTemplates", serialization_alias="includeRunpodTemplates", description="Whether to include official Runpod templates in the response. Defaults to false.")
class GetTemplateRequest(StrictModel):
    """Retrieve a single template by its ID. Optionally include templates from Serverless endpoints, community-made public templates, or official Runpod templates in the response."""
    path: GetTemplateRequestPath
    query: GetTemplateRequestQuery | None = None

# Operation: update_template
class UpdateTemplateRequestPath(StrictModel):
    template_id: str = Field(default=..., validation_alias="templateId", serialization_alias="templateId", description="The unique identifier of the template to update.")
class UpdateTemplateRequestBody(StrictModel):
    """Update a template."""
    docker_entrypoint: list[str] | None = Field(default=None, validation_alias="dockerEntrypoint", serialization_alias="dockerEntrypoint", description="Override the Docker image's ENTRYPOINT instruction. Provide as an array of command segments (e.g., ['python', '-m', 'server']). Leave empty to use the ENTRYPOINT defined in the Dockerfile.")
    docker_start_cmd: list[str] | None = Field(default=None, validation_alias="dockerStartCmd", serialization_alias="dockerStartCmd", description="Override the Docker image's start command (CMD instruction). Provide as an array of command segments. Leave empty to use the CMD defined in the Dockerfile.")
    env: dict[str, Any] | None = Field(default=None, description="Environment variables to inject into Pods created from this template, specified as key-value pairs (e.g., ENV_VAR: value).")
    image_name: str | None = Field(default=None, validation_alias="imageName", serialization_alias="imageName", description="The Docker image name and optional tag to use for Pods created from this template (e.g., 'myregistry/myimage:latest').")
    is_public: bool | None = Field(default=None, validation_alias="isPublic", serialization_alias="isPublic", description="If true, makes this Pod template visible to other Runpod users. If false, the template is private to your account.")
    name: str | None = Field(default=None, description="A human-readable name for the template.")
    ports: list[str] | None = Field(default=None, description="List of network ports to expose on Pods created from this template. Each port is specified as 'port_number/protocol' where protocol is either 'http' or 'tcp' (e.g., '8888/http', '22/tcp').")
    readme: str | None = Field(default=None, description="Template documentation in Markdown format, displayed to users when viewing or selecting this template.")
class UpdateTemplateRequest(StrictModel):
    """Update an existing template's configuration, including Docker image settings, environment variables, exposed ports, and metadata. Changes apply to all Pods created from this template going forward."""
    path: UpdateTemplateRequestPath
    body: UpdateTemplateRequestBody | None = None

# Operation: delete_template
class DeleteTemplateRequestPath(StrictModel):
    template_id: str = Field(default=..., validation_alias="templateId", serialization_alias="templateId", description="The unique identifier of the template to delete.")
class DeleteTemplateRequest(StrictModel):
    """Permanently delete a template by its ID. This action cannot be undone."""
    path: DeleteTemplateRequestPath

# Operation: update_template_alternate
class UpdateTemplate2RequestPath(StrictModel):
    template_id: str = Field(default=..., validation_alias="templateId", serialization_alias="templateId", description="The unique identifier of the template to update.")
class UpdateTemplate2RequestBody(StrictModel):
    """Update a template."""
    docker_entrypoint: list[str] | None = Field(default=None, validation_alias="dockerEntrypoint", serialization_alias="dockerEntrypoint", description="Docker ENTRYPOINT override for Pods using this template. Provide as an array of command segments; pass an empty array to use the ENTRYPOINT defined in the Dockerfile.")
    docker_start_cmd: list[str] | None = Field(default=None, validation_alias="dockerStartCmd", serialization_alias="dockerStartCmd", description="Docker CMD override for Pods using this template. Provide as an array of command segments; pass an empty array to use the CMD defined in the Dockerfile.")
    env: dict[str, Any] | None = Field(default=None, description="Environment variables to inject into Pods using this template, specified as key-value pairs (e.g., ENV_VAR: value).")
    image_name: str | None = Field(default=None, validation_alias="imageName", serialization_alias="imageName", description="The Docker image name and tag to use for Pods created from this template.")
    is_public: bool | None = Field(default=None, validation_alias="isPublic", serialization_alias="isPublic", description="Whether this Pod template is visible to other Runpod users. Defaults to private (not visible).")
    name: str | None = Field(default=None, description="A human-readable name for the template.")
    ports: list[str] | None = Field(default=None, description="Network ports exposed by Pods using this template. Each port is specified as [port_number]/[protocol], where protocol is either 'http' or 'tcp'.")
    readme: str | None = Field(default=None, description="Template documentation in Markdown format, displayed to users viewing or using this template.")
class UpdateTemplate2Request(StrictModel):
    """Update an existing Pod template's configuration, including Docker image settings, environment variables, exposed ports, and metadata. Changes apply to all Pods created from this template going forward."""
    path: UpdateTemplate2RequestPath
    body: UpdateTemplate2RequestBody | None = None

# Operation: create_network_volume
class CreateNetworkVolumeRequestBody(StrictModel):
    """Create a new network volume."""
    data_center_id: str = Field(default=..., validation_alias="dataCenterId", serialization_alias="dataCenterId", description="The Runpod data center where the network volume will be created (e.g., EU-RO-1).")
    name: str = Field(default=..., description="A user-defined name for the network volume. Names do not need to be unique and can be any descriptive label.")
    size: int = Field(default=..., description="The storage capacity to allocate for the network volume, specified in gigabytes. Must be between 0 and 4000 GB.", ge=0, le=4000)
class CreateNetworkVolumeRequest(StrictModel):
    """Create a new network volume in a specified Runpod data center. The volume will be allocated with the specified storage capacity and can be referenced by its user-defined name."""
    body: CreateNetworkVolumeRequestBody

# Operation: get_network_volume
class GetNetworkVolumeRequestPath(StrictModel):
    network_volume_id: str = Field(default=..., validation_alias="networkVolumeId", serialization_alias="networkVolumeId", description="The unique identifier of the network volume to retrieve.")
class GetNetworkVolumeRequest(StrictModel):
    """Retrieve a specific network volume by its unique identifier. Returns detailed information about the requested network volume."""
    path: GetNetworkVolumeRequestPath

# Operation: update_network_volume
class UpdateNetworkVolumeRequestPath(StrictModel):
    network_volume_id: str = Field(default=..., validation_alias="networkVolumeId", serialization_alias="networkVolumeId", description="The unique identifier of the network volume to be updated.")
class UpdateNetworkVolumeRequestBody(StrictModel):
    """Update a network volume."""
    name: str | None = Field(default=None, description="A user-defined name for the network volume. Names do not need to be unique and can be changed at any time.")
    size: int | None = Field(default=None, description="The new disk space allocation in gigabytes (GB) for the network volume. Must be greater than the current size and cannot exceed 4000 GB.", ge=0, le=4000)
class UpdateNetworkVolumeRequest(StrictModel):
    """Update the name and/or storage capacity of an existing network volume. Changes take effect immediately after the update is processed."""
    path: UpdateNetworkVolumeRequestPath
    body: UpdateNetworkVolumeRequestBody | None = None

# Operation: delete_network_volume
class DeleteNetworkVolumeRequestPath(StrictModel):
    network_volume_id: str = Field(default=..., validation_alias="networkVolumeId", serialization_alias="networkVolumeId", description="The unique identifier of the network volume to delete.")
class DeleteNetworkVolumeRequest(StrictModel):
    """Permanently delete a network volume by its ID. This operation removes the network volume and its associated resources from the system."""
    path: DeleteNetworkVolumeRequestPath

# Operation: update_network_volume_action
class UpdateNetworkVolume2RequestPath(StrictModel):
    network_volume_id: str = Field(default=..., validation_alias="networkVolumeId", serialization_alias="networkVolumeId", description="The unique identifier of the network volume to update.")
class UpdateNetworkVolume2RequestBody(StrictModel):
    """Update a network volume."""
    name: str | None = Field(default=None, description="A user-defined name for the network volume. Names do not need to be unique across volumes.")
    size: int | None = Field(default=None, description="The new disk space allocation in gigabytes. Must be between 0 and 4000 GB, and must exceed the current volume size.", ge=0, le=4000)
class UpdateNetworkVolume2Request(StrictModel):
    """Update the name and/or storage capacity of an existing network volume. The new size must be larger than the current allocated size."""
    path: UpdateNetworkVolume2RequestPath
    body: UpdateNetworkVolume2RequestBody | None = None

# Operation: create_container_registry_auth
class CreateContainerRegistryAuthRequestBody(StrictModel):
    """Create a new container registry auth."""
    name: str = Field(default=..., description="A unique identifier for this container registry credential. Choose a descriptive name that helps you identify which registry or account this credential is for.")
    password: str = Field(default=..., description="The password or authentication token for accessing the container registry. This is stored securely and used when authenticating registry operations.")
    username: str = Field(default=..., description="The username or account identifier for accessing the container registry. This is paired with the password to authenticate registry operations.")
class CreateContainerRegistryAuthRequest(StrictModel):
    """Create a new container registry authentication credential with a unique name. This stores the username and password needed to authenticate with a container registry."""
    body: CreateContainerRegistryAuthRequestBody

# Operation: get_container_registry_auth
class GetContainerRegistryAuthRequestPath(StrictModel):
    container_registry_auth_id: str = Field(default=..., validation_alias="containerRegistryAuthId", serialization_alias="containerRegistryAuthId", description="The unique identifier of the container registry authentication configuration to retrieve.")
class GetContainerRegistryAuthRequest(StrictModel):
    """Retrieve a specific container registry authentication configuration by its unique identifier. Returns the complete details of the requested registry auth."""
    path: GetContainerRegistryAuthRequestPath

# Operation: delete_container_registry_auth
class DeleteContainerRegistryAuthRequestPath(StrictModel):
    container_registry_auth_id: str = Field(default=..., validation_alias="containerRegistryAuthId", serialization_alias="containerRegistryAuthId", description="The unique identifier of the container registry authentication configuration to delete.")
class DeleteContainerRegistryAuthRequest(StrictModel):
    """Permanently delete a container registry authentication configuration. This removes the stored credentials and access settings for the specified registry."""
    path: DeleteContainerRegistryAuthRequestPath

# Operation: list_pod_billing_history
class PodBillingRequestQuery(StrictModel):
    bucket_size: Literal["hour", "day", "week", "month", "year"] | None = Field(default=None, validation_alias="bucketSize", serialization_alias="bucketSize", description="Time granularity for aggregating billing records. Choose from hourly, daily, weekly, monthly, or yearly buckets. Defaults to daily aggregation.")
    end_time: str | None = Field(default=None, validation_alias="endTime", serialization_alias="endTime", description="End of the billing period to retrieve, specified as an ISO 8601 datetime (e.g., 2023-01-31T23:59:59Z). If omitted, defaults to the current time.", json_schema_extra={'format': 'date-time'})
    gpu_type_id: Literal["NVIDIA GeForce RTX 4090", "NVIDIA A40", "NVIDIA RTX A5000", "NVIDIA GeForce RTX 5090", "NVIDIA H100 80GB HBM3", "NVIDIA GeForce RTX 3090", "NVIDIA RTX A4500", "NVIDIA L40S", "NVIDIA H200", "NVIDIA L4", "NVIDIA RTX 6000 Ada Generation", "NVIDIA A100-SXM4-80GB", "NVIDIA RTX 4000 Ada Generation", "NVIDIA RTX A6000", "NVIDIA A100 80GB PCIe", "NVIDIA RTX 2000 Ada Generation", "NVIDIA RTX A4000", "NVIDIA RTX PRO 6000 Blackwell Server Edition", "NVIDIA H100 PCIe", "NVIDIA H100 NVL", "NVIDIA L40", "NVIDIA B200", "NVIDIA GeForce RTX 3080 Ti", "NVIDIA RTX PRO 6000 Blackwell Workstation Edition", "NVIDIA GeForce RTX 3080", "NVIDIA GeForce RTX 3070", "AMD Instinct MI300X OAM", "NVIDIA GeForce RTX 4080 SUPER", "Tesla V100-PCIE-16GB", "Tesla V100-SXM2-32GB", "NVIDIA RTX 5000 Ada Generation", "NVIDIA GeForce RTX 4070 Ti", "NVIDIA RTX 4000 SFF Ada Generation", "NVIDIA GeForce RTX 3090 Ti", "NVIDIA RTX A2000", "NVIDIA GeForce RTX 4080", "NVIDIA A30", "NVIDIA GeForce RTX 5080", "Tesla V100-FHHL-16GB", "NVIDIA H200 NVL", "Tesla V100-SXM2-16GB", "NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition", "NVIDIA A5000 Ada", "Tesla V100-PCIE-32GB", "NVIDIA  RTX A4500", "NVIDIA  A30", "NVIDIA GeForce RTX 3080TI", "Tesla T4", "NVIDIA RTX A30"] | None = Field(default=None, validation_alias="gpuTypeId", serialization_alias="gpuTypeId", description="Filter results to Pods equipped with a specific GPU type. Accepts the full GPU model name (e.g., 'NVIDIA GeForce RTX 4090'). Omit to include all GPU types.")
    grouping: Literal["podId", "gpuTypeId"] | None = Field(default=None, description="Organize billing records by Pod ID or GPU type. Defaults to grouping by GPU type. Use 'podId' to see per-Pod breakdowns.")
    pod_id: str | None = Field(default=None, validation_alias="podId", serialization_alias="podId", description="Filter results to a single Pod by its ID. Omit to include all Pods.")
    start_time: str | None = Field(default=None, validation_alias="startTime", serialization_alias="startTime", description="Start of the billing period to retrieve, specified as an ISO 8601 datetime (e.g., 2023-01-01T00:00:00Z). If omitted, defaults to 30 days before the end time.", json_schema_extra={'format': 'date-time'})
class PodBillingRequest(StrictModel):
    """Retrieve aggregated billing records for your Pods over a specified time period. Results can be grouped by individual Pod or GPU type, with flexible time bucket granularity."""
    query: PodBillingRequestQuery | None = None

# Operation: list_endpoint_billing_history
class EndpointBillingRequestQuery(StrictModel):
    bucket_size: Literal["hour", "day", "week", "month", "year"] | None = Field(default=None, validation_alias="bucketSize", serialization_alias="bucketSize", description="Time bucket size for aggregating billing records. Choose from hourly, daily, weekly, monthly, or yearly aggregation. Defaults to daily.")
    data_center_id: list[Literal["EU-RO-1", "CA-MTL-1", "EU-SE-1", "US-IL-1", "EUR-IS-1", "EU-CZ-1", "US-TX-3", "EUR-IS-2", "US-KS-2", "US-GA-2", "US-WA-1", "US-TX-1", "CA-MTL-3", "EU-NL-1", "US-TX-4", "US-CA-2", "US-NC-1", "OC-AU-1", "US-DE-1", "EUR-IS-3", "CA-MTL-2", "AP-JP-1", "EUR-NO-1", "EU-FR-1", "US-KS-3", "US-GA-1"]] | None = Field(default=None, validation_alias="dataCenterId", serialization_alias="dataCenterId", description="Filter results to endpoints in specific Runpod data centers. Provide an array of data center IDs (e.g., EU-RO-1, US-TX-3). Defaults to all available data centers.")
    endpoint_id: str | None = Field(default=None, validation_alias="endpointId", serialization_alias="endpointId", description="Filter results to a single endpoint by its ID.")
    end_time: str | None = Field(default=None, validation_alias="endTime", serialization_alias="endTime", description="End date for the billing period in ISO 8601 format (e.g., 2023-01-31T23:59:59Z).", json_schema_extra={'format': 'date-time'})
    gpu_type_id: list[Literal["NVIDIA GeForce RTX 4090", "NVIDIA A40", "NVIDIA RTX A5000", "NVIDIA GeForce RTX 5090", "NVIDIA H100 80GB HBM3", "NVIDIA GeForce RTX 3090", "NVIDIA RTX A4500", "NVIDIA L40S", "NVIDIA H200", "NVIDIA L4", "NVIDIA RTX 6000 Ada Generation", "NVIDIA A100-SXM4-80GB", "NVIDIA RTX 4000 Ada Generation", "NVIDIA RTX A6000", "NVIDIA A100 80GB PCIe", "NVIDIA RTX 2000 Ada Generation", "NVIDIA RTX A4000", "NVIDIA RTX PRO 6000 Blackwell Server Edition", "NVIDIA H100 PCIe", "NVIDIA H100 NVL", "NVIDIA L40", "NVIDIA B200", "NVIDIA GeForce RTX 3080 Ti", "NVIDIA RTX PRO 6000 Blackwell Workstation Edition", "NVIDIA GeForce RTX 3080", "NVIDIA GeForce RTX 3070", "AMD Instinct MI300X OAM", "NVIDIA GeForce RTX 4080 SUPER", "Tesla V100-PCIE-16GB", "Tesla V100-SXM2-32GB", "NVIDIA RTX 5000 Ada Generation", "NVIDIA GeForce RTX 4070 Ti", "NVIDIA RTX 4000 SFF Ada Generation", "NVIDIA GeForce RTX 3090 Ti", "NVIDIA RTX A2000", "NVIDIA GeForce RTX 4080", "NVIDIA A30", "NVIDIA GeForce RTX 5080", "Tesla V100-FHHL-16GB", "NVIDIA H200 NVL", "Tesla V100-SXM2-16GB", "NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition", "NVIDIA A5000 Ada", "Tesla V100-PCIE-32GB", "NVIDIA  RTX A4500", "NVIDIA  A30", "NVIDIA GeForce RTX 3080TI", "Tesla T4", "NVIDIA RTX A30"]] | None = Field(default=None, validation_alias="gpuTypeId", serialization_alias="gpuTypeId", description="Filter results to endpoints with specific GPU types attached. Provide an array of GPU type names (e.g., NVIDIA GeForce RTX 4090).")
    grouping: Literal["endpointId", "podId", "gpuTypeId"] | None = Field(default=None, description="Group billing records by endpoint ID, pod ID, or GPU type. Defaults to grouping by endpoint ID.")
    image_name: str | None = Field(default=None, validation_alias="imageName", serialization_alias="imageName", description="Filter results to endpoints created with a specific container image.")
    start_time: str | None = Field(default=None, validation_alias="startTime", serialization_alias="startTime", description="Start date for the billing period in ISO 8601 format (e.g., 2023-01-01T00:00:00Z).", json_schema_extra={'format': 'date-time'})
    template_id: str | None = Field(default=None, validation_alias="templateId", serialization_alias="templateId", description="Filter results to endpoints created from a specific template by its ID.")
class EndpointBillingRequest(StrictModel):
    """Retrieve aggregated billing records for your Serverless endpoints, with flexible filtering by location, GPU type, endpoint, and time range. Results can be grouped by endpoint, pod, or GPU type."""
    query: EndpointBillingRequestQuery | None = None

# Operation: list_network_volume_billing
class NetworkVolumeBillingRequestQuery(StrictModel):
    bucket_size: Literal["hour", "day", "week", "month", "year"] | None = Field(default=None, validation_alias="bucketSize", serialization_alias="bucketSize", description="The time granularity for aggregating billing data. Defaults to daily buckets if not specified. Valid options are hour, day, week, month, or year.")
    end_time: str | None = Field(default=None, validation_alias="endTime", serialization_alias="endTime", description="The end of the billing period to retrieve, specified as an ISO 8601 datetime string (e.g., 2023-01-31T23:59:59Z). If omitted, defaults to the current time.", json_schema_extra={'format': 'date-time'})
    start_time: str | None = Field(default=None, validation_alias="startTime", serialization_alias="startTime", description="The start of the billing period to retrieve, specified as an ISO 8601 datetime string (e.g., 2023-01-01T00:00:00Z). If omitted, defaults to a reasonable historical starting point.", json_schema_extra={'format': 'date-time'})
class NetworkVolumeBillingRequest(StrictModel):
    """Retrieve aggregated billing records for your network volumes over a specified time period. Results can be grouped by hour, day, week, month, or year."""
    query: NetworkVolumeBillingRequestQuery | None = None

# ============================================================================
# Component Models
# ============================================================================

class PodGpu(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    count: int | None = Field(None, description="The number of GPUs attached to a Pod.")
    display_name: str | None = Field(None, validation_alias="displayName", serialization_alias="displayName")
    secure_price: float | None = Field(None, validation_alias="securePrice", serialization_alias="securePrice")
    community_price: float | None = Field(None, validation_alias="communityPrice", serialization_alias="communityPrice")
    one_month_price: float | None = Field(None, validation_alias="oneMonthPrice", serialization_alias="oneMonthPrice")
    three_month_price: float | None = Field(None, validation_alias="threeMonthPrice", serialization_alias="threeMonthPrice")
    six_month_price: float | None = Field(None, validation_alias="sixMonthPrice", serialization_alias="sixMonthPrice")
    one_week_price: float | None = Field(None, validation_alias="oneWeekPrice", serialization_alias="oneWeekPrice")
    community_spot_price: float | None = Field(None, validation_alias="communitySpotPrice", serialization_alias="communitySpotPrice")
    secure_spot_price: float | None = Field(None, validation_alias="secureSpotPrice", serialization_alias="secureSpotPrice")

class PodMachineCpuType(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    display_name: str | None = Field(None, validation_alias="displayName", serialization_alias="displayName")
    cores: float | None = None
    threads_per_core: float | None = Field(None, validation_alias="threadsPerCore", serialization_alias="threadsPerCore")
    group_id: str | None = Field(None, validation_alias="groupId", serialization_alias="groupId")

class PodMachineGpuType(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    count: int | None = Field(None, description="The number of GPUs attached to a Pod.")
    display_name: str | None = Field(None, validation_alias="displayName", serialization_alias="displayName")
    secure_price: float | None = Field(None, validation_alias="securePrice", serialization_alias="securePrice")
    community_price: float | None = Field(None, validation_alias="communityPrice", serialization_alias="communityPrice")
    one_month_price: float | None = Field(None, validation_alias="oneMonthPrice", serialization_alias="oneMonthPrice")
    three_month_price: float | None = Field(None, validation_alias="threeMonthPrice", serialization_alias="threeMonthPrice")
    six_month_price: float | None = Field(None, validation_alias="sixMonthPrice", serialization_alias="sixMonthPrice")
    one_week_price: float | None = Field(None, validation_alias="oneWeekPrice", serialization_alias="oneWeekPrice")
    community_spot_price: float | None = Field(None, validation_alias="communitySpotPrice", serialization_alias="communitySpotPrice")
    secure_spot_price: float | None = Field(None, validation_alias="secureSpotPrice", serialization_alias="secureSpotPrice")

class PodMachine(PermissiveModel):
    """Information about the machine a Pod is running on (see [Machine](#/components/schemas/Machine))."""
    min_pod_gpu_count: int | None = Field(None, validation_alias="minPodGpuCount", serialization_alias="minPodGpuCount")
    gpu_type_id: str | None = Field(None, validation_alias="gpuTypeId", serialization_alias="gpuTypeId")
    gpu_type: PodMachineGpuType | None = Field(None, validation_alias="gpuType", serialization_alias="gpuType")
    cpu_count: int | None = Field(None, validation_alias="cpuCount", serialization_alias="cpuCount")
    cpu_type_id: str | None = Field(None, validation_alias="cpuTypeId", serialization_alias="cpuTypeId")
    cpu_type: PodMachineCpuType | None = Field(None, validation_alias="cpuType", serialization_alias="cpuType")
    location: str | None = None
    data_center_id: str | None = Field(None, validation_alias="dataCenterId", serialization_alias="dataCenterId")
    disk_throughput_m_bps: int | None = Field(None, validation_alias="diskThroughputMBps", serialization_alias="diskThroughputMBps")
    max_download_speed_mbps: int | None = Field(None, validation_alias="maxDownloadSpeedMbps", serialization_alias="maxDownloadSpeedMbps")
    max_upload_speed_mbps: int | None = Field(None, validation_alias="maxUploadSpeedMbps", serialization_alias="maxUploadSpeedMbps")
    support_public_ip: bool | None = Field(None, validation_alias="supportPublicIp", serialization_alias="supportPublicIp")
    secure_cloud: bool | None = Field(None, validation_alias="secureCloud", serialization_alias="secureCloud")
    maintenance_start: str | None = Field(None, validation_alias="maintenanceStart", serialization_alias="maintenanceStart")
    maintenance_end: str | None = Field(None, validation_alias="maintenanceEnd", serialization_alias="maintenanceEnd")
    maintenance_note: str | None = Field(None, validation_alias="maintenanceNote", serialization_alias="maintenanceNote")
    note: str | None = None
    cost_per_hr: float | None = Field(None, validation_alias="costPerHr", serialization_alias="costPerHr")
    current_price_per_gpu: float | None = Field(None, validation_alias="currentPricePerGpu", serialization_alias="currentPricePerGpu")
    gpu_available: int | None = Field(None, validation_alias="gpuAvailable", serialization_alias="gpuAvailable")
    gpu_display_name: str | None = Field(None, validation_alias="gpuDisplayName", serialization_alias="gpuDisplayName")

class PodNetworkVolume(PermissiveModel):
    """If a network volume is attached to a Pod, information about the network volume (see [network volume schema](#/components/schemas/NetworkVolume))."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="A unique string identifying a network volume.")
    name: str | None = Field(None, description="A user-defined name for a network volume. The name does not need to be unique.")
    size: int | None = Field(None, description="The amount of disk space, in gigabytes (GB), allocated to a network volume.")
    data_center_id: str | None = Field(None, validation_alias="dataCenterId", serialization_alias="dataCenterId", description="The Runpod data center ID where a network volume is located.")

class SavingsPlan(PermissiveModel):
    cost_per_hr: float | None = Field(None, validation_alias="costPerHr", serialization_alias="costPerHr")
    end_time: str | None = Field(None, validation_alias="endTime", serialization_alias="endTime")
    gpu_type_id: str | None = Field(None, validation_alias="gpuTypeId", serialization_alias="gpuTypeId")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    pod_id: str | None = Field(None, validation_alias="podId", serialization_alias="podId")
    start_time: str | None = Field(None, validation_alias="startTime", serialization_alias="startTime")

class Pod(PermissiveModel):
    adjusted_cost_per_hr: float | None = Field(None, validation_alias="adjustedCostPerHr", serialization_alias="adjustedCostPerHr", description="The effective cost in Runpod credits per hour of running a Pod, adjusted by active Savings Plans.")
    ai_api_id: str | None = Field(None, validation_alias="aiApiId", serialization_alias="aiApiId", description="Synonym for endpointId (legacy name).")
    consumer_user_id: str | None = Field(None, validation_alias="consumerUserId", serialization_alias="consumerUserId", description="A unique string identifying the Runpod user who rents a Pod.")
    container_disk_in_gb: int | None = Field(None, validation_alias="containerDiskInGb", serialization_alias="containerDiskInGb", description="The amount of disk space, in gigabytes (GB), to allocate on the container disk for a Pod. The data on the container disk is wiped when the Pod restarts. To persist data across Pod restarts, set volumeInGb to configure the Pod network volume.")
    container_registry_auth_id: str | None = Field(None, validation_alias="containerRegistryAuthId", serialization_alias="containerRegistryAuthId", description="If a Pod is created with a container registry auth, the unique string identifying that container registry auth.")
    cost_per_hr: float | None = Field(None, validation_alias="costPerHr", serialization_alias="costPerHr", description="The cost in Runpod credits per hour of running a Pod. Note that the actual cost may be lower if Savings Plans are applied.", json_schema_extra={'format': 'currency'})
    cpu_flavor_id: str | None = Field(None, validation_alias="cpuFlavorId", serialization_alias="cpuFlavorId", description="If the Pod is a CPU Pod, the unique string identifying the CPU flavor the Pod is running on.")
    desired_status: Literal["RUNNING", "EXITED", "TERMINATED"] | None = Field(None, validation_alias="desiredStatus", serialization_alias="desiredStatus", description="The current expected status of a Pod.")
    docker_entrypoint: list[str] | None = Field(None, validation_alias="dockerEntrypoint", serialization_alias="dockerEntrypoint", description="If specified, overrides the ENTRYPOINT for the Docker image run on the created Pod. If [], uses the ENTRYPOINT defined in the image.")
    docker_start_cmd: list[str] | None = Field(None, validation_alias="dockerStartCmd", serialization_alias="dockerStartCmd", description="If specified, overrides the start CMD for the Docker image run on the created Pod. If [], uses the start CMD defined in the image.")
    endpoint_id: str | None = Field(None, validation_alias="endpointId", serialization_alias="endpointId", description="If the Pod is a Serverless worker, a unique string identifying the associated endpoint.")
    env: dict[str, Any] | None = {}
    gpu: PodGpu | None = None
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="A unique string identifying a [Pod](#/components/schema/Pod).")
    image: str | None = Field(None, description="The image tag for the container run on a Pod.")
    interruptible: bool | None = Field(None, description="Describes how a Pod is rented. An interruptible Pod can be rented at a lower cost but can be stopped at any time to free up resources for another Pod. A reserved Pod is rented at a higher cost but runs until it exits or is manually stopped.")
    last_started_at: str | None = Field(None, validation_alias="lastStartedAt", serialization_alias="lastStartedAt", description="The UTC timestamp when a Pod was last started.")
    last_status_change: str | None = Field(None, validation_alias="lastStatusChange", serialization_alias="lastStatusChange", description="A string describing the last lifecycle event on a Pod.")
    locked: bool | None = Field(None, description="Set to true to lock a Pod. Locking a Pod disables stopping or resetting the Pod.")
    machine: PodMachine | None = Field(None, description="Information about the machine a Pod is running on (see [Machine](#/components/schemas/Machine)).")
    machine_id: str | None = Field(None, validation_alias="machineId", serialization_alias="machineId", description="A unique string identifying the host machine a Pod is running on.")
    memory_in_gb: float | None = Field(None, validation_alias="memoryInGb", serialization_alias="memoryInGb", description="The amount of RAM, in gigabytes (GB), attached to a Pod.")
    name: str | None = Field(None, description="A user-defined name for the created Pod. The name does not need to be unique.", max_length=191)
    network_volume: PodNetworkVolume | None = Field(None, validation_alias="networkVolume", serialization_alias="networkVolume", description="If a network volume is attached to a Pod, information about the network volume (see [network volume schema](#/components/schemas/NetworkVolume)).")
    port_mappings: dict[str, Any] | None = Field(None, validation_alias="portMappings", serialization_alias="portMappings", description="A mapping of internal ports to public ports on a Pod. For example, { \"22\": 10341 } means that port 22 on the Pod is mapped to port 10341 and is publicly accessible at [public ip]:10341. If the Pod is still initializing, this mapping is not yet determined and will be empty.")
    ports: list[str] | None = Field(None, description="A list of ports exposed on a Pod. Each port is formatted as [port number]/[protocol]. Protocol can be either http or tcp.")
    public_ip: str | None = Field(None, validation_alias="publicIp", serialization_alias="publicIp", description="The public IP address of a Pod. If the Pod is still initializing, this IP is not yet determined and will be empty.", json_schema_extra={'format': 'ipv4'})
    savings_plans: list[SavingsPlan] | None = Field(None, validation_alias="savingsPlans", serialization_alias="savingsPlans", description="The list of active Savings Plans applied to a Pod (see [Savings Plans](#/components/schemas/SavingsPlan)). If none are applied, the list is empty.")
    sls_version: int | None = Field(None, validation_alias="slsVersion", serialization_alias="slsVersion", description="If the Pod is a Serverless worker, the version of the associated endpoint (see [Endpoint Version](#/components/schemas/Endpoint/version)).")
    template_id: str | None = Field(None, validation_alias="templateId", serialization_alias="templateId", description="If a Pod is created with a template, the unique string identifying that template.")
    vcpu_count: float | None = Field(None, validation_alias="vcpuCount", serialization_alias="vcpuCount", description="The number of virtual CPUs attached to a Pod.")
    volume_encrypted: bool | None = Field(None, validation_alias="volumeEncrypted", serialization_alias="volumeEncrypted", description="Set to true if the local network volume of a Pod is encrypted. Can only be set when creating a Pod.")
    volume_in_gb: int | None = Field(None, validation_alias="volumeInGb", serialization_alias="volumeInGb", description="The amount of disk space, in gigabytes (GB), to allocate on the Pod volume for a Pod. The data on the Pod volume is persisted across Pod restarts. To persist data so that future Pods can access it, create a network volume and set networkVolumeId to attach it to the Pod.")
    volume_mount_path: str | None = Field(None, validation_alias="volumeMountPath", serialization_alias="volumeMountPath", description="If either a Pod volume or a network volume is attached to a Pod, the absolute path where the network volume is mounted in the filesystem.")

class Pods(RootModel[list[Pod]]):
    pass

class Template(PermissiveModel):
    category: str | None = Field(None, description="The category of the template. The category can be used to filter templates in the Runpod UI. Current categories are NVIDIA, AMD, and CPU.")
    container_disk_in_gb: int | None = Field(None, validation_alias="containerDiskInGb", serialization_alias="containerDiskInGb", description="The amount of disk space, in gigabytes (GB), to allocate on the container disk for a Pod or worker. The data on the container disk is wiped when the Pod or worker restarts. To persist data across restarts, set volumeInGb to configure the local network volume.")
    container_registry_auth_id: str | None = Field(None, validation_alias="containerRegistryAuthId", serialization_alias="containerRegistryAuthId")
    docker_entrypoint: list[str] | None = Field(None, validation_alias="dockerEntrypoint", serialization_alias="dockerEntrypoint", description="If specified, overrides the ENTRYPOINT for the Docker image run on a Pod or worker. If [], uses the ENTRYPOINT defined in the image.")
    docker_start_cmd: list[str] | None = Field(None, validation_alias="dockerStartCmd", serialization_alias="dockerStartCmd", description="If specified, overrides the start CMD for the Docker image run on a Pod or worker. If [], uses the start CMD defined in the image.")
    earned: float | None = Field(None, description="The amount of Runpod credits earned by the creator of a template by all Pods or workers created from the template.")
    env: dict[str, Any] | None = {}
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="A unique string identifying a template.")
    image_name: str | None = Field(None, validation_alias="imageName", serialization_alias="imageName", description="The image tag for the container run on Pods or workers created from a template.")
    is_public: bool | None = Field(None, validation_alias="isPublic", serialization_alias="isPublic", description="Set to true if a template is public and can be used by any Runpod user. Set to false if a template is private and can only be used by the creator.")
    is_runpod: bool | None = Field(None, validation_alias="isRunpod", serialization_alias="isRunpod", description="If true, a template is an official template managed by Runpod.")
    is_serverless: bool | None = Field(None, validation_alias="isServerless", serialization_alias="isServerless", description="If true, instances created from a template are Serverless workers. If false, instances created from a template are Pods.")
    name: str | None = Field(None, description="A user-defined name for a template. The name needs to be unique.")
    ports: list[str] | None = Field(None, description="A list of ports exposed on a Pod or worker. Each port is formatted as [port number]/[protocol]. Protocol can be either http or tcp.")
    readme: str | None = Field(None, description="A string of markdown-formatted text that describes a template. The readme is displayed in the Runpod UI when a user selects the template.")
    runtime_in_min: int | None = Field(None, validation_alias="runtimeInMin", serialization_alias="runtimeInMin")
    volume_in_gb: int | None = Field(None, validation_alias="volumeInGb", serialization_alias="volumeInGb", description="The amount of disk space, in gigabytes (GB), to allocate on the local network volume for a Pod or worker. The data on the local network volume is persisted across restarts. To persist data so that future Pods and workers can access it, create a network volume and set networkVolumeId to attach it to the Pod or worker.")
    volume_mount_path: str | None = Field(None, validation_alias="volumeMountPath", serialization_alias="volumeMountPath", description="If a local network volume or network volume is attached to a Pod or worker, the absolute path where the network volume is mounted in the filesystem.")

class Templates(RootModel[list[Template]]):
    pass


# Rebuild models to resolve forward references (required for circular refs)
Pod.model_rebuild()
PodGpu.model_rebuild()
PodMachine.model_rebuild()
PodMachineCpuType.model_rebuild()
PodMachineGpuType.model_rebuild()
PodNetworkVolume.model_rebuild()
Pods.model_rebuild()
SavingsPlan.model_rebuild()
Template.model_rebuild()
Templates.model_rebuild()

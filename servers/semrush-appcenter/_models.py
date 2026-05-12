"""
Semrush Appcenter MCP Server - Pydantic Models

Generated: 2026-05-12 12:44:24 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "GetApisV4HermesV0EventRequest",
    "GetApisV4HermesV0UserSubscriptionRequest",
    "PostApisV4AppCenterV2PartnerViewerStatusRequest",
    "PostApisV4HermesV0EventRequest",
    "EventAttachment",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: get_viewer_status
class PostApisV4AppCenterV2PartnerViewerStatusRequestBody(StrictModel):
    user_id: int | None = Field(default=None, description="The Semrush user ID to retrieve status for. If not provided, returns status for the authenticated user making the request.")
class PostApisV4AppCenterV2PartnerViewerStatusRequest(StrictModel):
    """Retrieves the current user's account status within the app, including information about purchases and active subscriptions."""
    body: PostApisV4AppCenterV2PartnerViewerStatusRequestBody | None = None

# Operation: get_user_subscription
class GetApisV4HermesV0UserSubscriptionRequestPath(StrictModel):
    user_id: int = Field(default=..., description="The unique identifier of the user whose subscription status you want to retrieve. Must be a positive integer.")
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the subscription to retrieve. Must be a positive integer corresponding to an existing subscription for the user.")
class GetApisV4HermesV0UserSubscriptionRequest(StrictModel):
    """Retrieve the current subscription status for a specific user. Returns detailed information about the user's subscription including its active state and configuration."""
    path: GetApisV4HermesV0UserSubscriptionRequestPath

# Operation: send_event_notification
class PostApisV4HermesV0EventRequestBody(StrictModel):
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The category or type of event being sent (e.g., 'alert', 'update', 'reminder'). Helps classify the notification for routing and filtering.")
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="A unique identifier for this event using UUID v4 format. Serves as an idempotency key to prevent duplicate notifications if the request is retried.", json_schema_extra={'format': 'uuid'})
    user_id: int | None = Field(default=None, description="The Semrush user ID who should receive this notification. Must be a valid integer representing an existing user account.")
    data: str | None = Field(default=None, description="Custom event payload as a base64-encoded byte string. Decode to access the JSON data structure containing event-specific information.", json_schema_extra={'format': 'byte'})
    attachments: list[EventAttachment] | None = Field(default=None, description="Array of file attachments to include with the notification. Each attachment is processed in the order provided.")
class PostApisV4HermesV0EventRequest(StrictModel):
    """Send a notification event to Semrush users. Use this to trigger server-to-server notifications with optional attachments and custom event data."""
    body: PostApisV4HermesV0EventRequestBody | None = None

# Operation: get_event_status
class GetApisV4HermesV0EventRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier (UUID format) of the subscription event whose status you want to retrieve.", json_schema_extra={'format': 'uuid'})
class GetApisV4HermesV0EventRequest(StrictModel):
    """Retrieve the current status of a notification event subscription. Use this to check the delivery status and details of a specific event."""
    path: GetApisV4HermesV0EventRequestPath

# ============================================================================
# Component Models
# ============================================================================

class EventAttachment(PermissiveModel):
    """Event additional files"""
    name: str | None = Field(None, description="File name")
    mime: str | None = Field(None, description="File content mime type")
    content: str | None = Field(None, description="File content in Base64", json_schema_extra={'format': 'byte'})


# Rebuild models to resolve forward references (required for circular refs)
EventAttachment.model_rebuild()

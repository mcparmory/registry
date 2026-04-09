"""
Customer.io Journeys Track MCP Server - Pydantic Models

Generated: 2026-04-09 17:19:09 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field, RootModel

__all__ = [
    "AddDeviceRequest",
    "AddToSegmentRequest",
    "BatchRequest",
    "DeleteDeviceRequest",
    "DeleteRequest",
    "EntityRequest",
    "IdentifyRequest",
    "MergeRequest",
    "MetricsRequest",
    "RemoveFromSegmentRequest",
    "SubmitFormRequest",
    "SuppressRequest",
    "TrackAnonymousRequest",
    "TrackRequest",
    "UnsubscribeRequest",
    "UnsuppressRequest",
    "DeliveryOperations",
    "DeviceObject",
    "EntityBodyDevice",
    "EntityBodyIdentifiersV0",
    "EntityBodyIdentifiersV1",
    "EntityBodyIdentifiersV2",
    "EntityBodyPrimaryV0",
    "EntityBodyPrimaryV1",
    "EntityBodyPrimaryV2",
    "EntityBodySecondaryV0",
    "EntityBodySecondaryV1",
    "EntityBodySecondaryV2",
    "IdentifyBodyCioRelationshipsRelationshipsItem",
    "IdentifyPerson",
    "MergeBodyPrimaryV0",
    "MergeBodyPrimaryV1",
    "MergeBodyPrimaryV2",
    "MergeBodySecondaryV0",
    "MergeBodySecondaryV1",
    "MergeBodySecondaryV2",
    "ObjectAddRelationships",
    "ObjectDelete",
    "ObjectDeleteRelationships",
    "ObjectIdentify",
    "ObjectIdentifyAnonymous",
    "ObjectRelationships",
    "PersonAddDevice",
    "PersonAddRelationships",
    "PersonDelete",
    "PersonDeleteDevice",
    "PersonDeleteRelationships",
    "PersonEvent",
    "PersonMerge",
    "PersonPage",
    "PersonScreen",
    "PersonSuppress",
    "PersonUnsuppress",
    "SubmitFormBodyDataV0",
    "SubmitFormBodyDataV1",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: upsert_customer
class IdentifyRequestPath(StrictModel):
    identifier: str = Field(default=..., description="The unique identifier for the customer in the path. Can be a customer ID, email address, or `cio_id` (prefixed with `cio_`). For workspaces using email as an identifier, this is case-insensitive.")
class IdentifyRequestBodyCioRelationships(StrictModel):
    action: Literal["add_relationships", "delete_relationships"] | None = Field(default=None, validation_alias="action", serialization_alias="action", description="Specifies whether to add relationships to or remove relationships from the customer.")
    relationships: list[IdentifyBodyCioRelationshipsRelationshipsItem] | None = Field(default=None, validation_alias="relationships", serialization_alias="relationships", description="An array of relationship objects to add to or remove from the customer, based on the `action` parameter. Each object represents a single relationship.")
class IdentifyRequestBodyCioSubscriptionPreferences(StrictModel):
    topics: dict[str, bool] | None = Field(default=None, validation_alias="topics", serialization_alias="topics", description="An object containing active topics in your workspace, with keys in the format `topic_<id>` and boolean values indicating topic subscription status.")
class IdentifyRequestBody(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="A customer's unique ID. Can be set when identifying by email; can be updated when identifying by `cio_id`.")
    email: str | None = Field(default=None, description="The email address of the customer. Case-insensitive for workspaces using email as an identifier.", json_schema_extra={'format': 'email'})
    anonymous_id: str | None = Field(default=None, description="An anonymous identifier (such as a cookie value) that associates anonymous events with this customer. Must be unique and cannot be reused across different customers.")
    update: bool | None = Field(default=None, validation_alias="_update", serialization_alias="_update", description="Set to true to update an existing customer profile instead of creating a new one when the identifier is not found. Prevents duplicate profile creation during rapid successive requests.")
    unsubscribed: bool | None = Field(default=None, description="Subscription status for the customer. When true, the customer is unsubscribed from all messages. When false or absent, the customer is eligible to receive messages based on their subscription preferences. Automatically updated when a customer clicks an unsubscribe link.")
    cio_relationships: IdentifyRequestBodyCioRelationships | None = None
    cio_subscription_preferences: IdentifyRequestBodyCioSubscriptionPreferences | None = None
class IdentifyRequest(StrictModel):
    """Add a new customer or update an existing customer's profile. This operation handles identifier merging, profile creation, and attribute updates based on the identifiers provided in the path and request body."""
    path: IdentifyRequestPath
    body: IdentifyRequestBody | None = None

# Operation: delete_customer
class DeleteRequestPath(StrictModel):
    identifier: str = Field(default=..., description="The unique identifier for the customer to delete. This can be a customer ID, email address, or cio_id (prefixed with 'cio_') depending on your workspace configuration.")
class DeleteRequest(StrictModel):
    """Permanently remove a customer and all associated information from Customer.io. Note that customers recreated through other integration methods (such as the Javascript snippet) after deletion may need to be deleted again."""
    path: DeleteRequestPath

# Operation: register_device
class AddDeviceRequestPath(StrictModel):
    identifier: str = Field(default=..., description="The unique identifier for the customer. Can be an `id`, `email` address, or `cio_id` (prefixed with `cio_`) depending on workspace configuration.")
class AddDeviceRequestBody(StrictModel):
    device: DeviceObject = Field(default=..., description="An object containing device properties such as platform type, device token, and attributes. Properties are automatically collected by SDKs unless `autoTrackDeviceAttributes` is disabled. Device properties can be referenced in segments and Liquid templates.")
class AddDeviceRequest(StrictModel):
    """Register or update a device for a customer. Customers can maintain multiple devices (iOS and Android) on their profile."""
    path: AddDeviceRequestPath
    body: AddDeviceRequestBody

# Operation: remove_device
class DeleteDeviceRequestPath(StrictModel):
    identifier: str = Field(default=..., description="The unique identifier for the customer. This can be an `id`, `email` address, or `cio_id` (prefixed with `cio_`) depending on your workspace configuration.")
    device_id: str = Field(default=..., description="The unique identifier of the device to remove from the customer profile.")
class DeleteDeviceRequest(StrictModel):
    """Remove a device from a customer profile. Ensure you stop sending device data to Customer.io to prevent the device from being automatically re-added."""
    path: DeleteDeviceRequestPath

# Operation: suppress_customer
class SuppressRequestPath(StrictModel):
    identifier: str = Field(default=..., description="The unique identifier for the customer to suppress. This can be an email address, customer ID, or CIO ID (prefixed with `cio_`) depending on your workspace configuration. When using CIO ID, the value must be prefixed with `cio_`.")
class SuppressRequest(StrictModel):
    """Permanently delete a customer profile and suppress their identifier(s) to prevent re-addition to the workspace. All future API calls referencing the suppressed identifier are ignored. This action cannot be undone and should be used primarily for GDPR/CCPA compliance requests."""
    path: SuppressRequestPath

# Operation: unsuppress_customer
class UnsuppressRequestPath(StrictModel):
    identifier: str = Field(default=..., description="The unique identifier for the customer, which can be their ID, email address, or cio_id (prefixed with 'cio_'). The identifier type depends on your workspace configuration.")
class UnsuppressRequest(StrictModel):
    """Reactivate a suppressed customer profile to make their identifier available for new profile creation. Unsuppressing does not restore the previous profile history; it only makes the identifier usable again."""
    path: UnsuppressRequestPath

# Operation: mark_delivery_unsubscribed
class UnsubscribeRequestPath(StrictModel):
    delivery_id: str = Field(default=..., description="The unique identifier of the email delivery associated with the unsubscribe request.")
class UnsubscribeRequestBody(StrictModel):
    unsubscribe: bool | None = Field(default=None, description="Set to true to mark the person as unsubscribed and attribute the unsubscribe action to this delivery.")
class UnsubscribeRequest(StrictModel):
    """Mark a person as unsubscribed from a specific email delivery. Use this endpoint with custom unsubscribe pages to record unsubscribe requests and trigger email_unsubscribed events for audience segmentation."""
    path: UnsubscribeRequestPath
    body: UnsubscribeRequestBody | None = None

# Operation: track_customer_event
class TrackRequestPath(StrictModel):
    identifier: str = Field(default=..., description="The unique identifier for the customer. Can be their user ID, email address, or CIO ID depending on workspace configuration.")
class TrackRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the event used to reference it in campaigns and segments. Leading and trailing spaces are automatically trimmed.")
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="A unique identifier for deduplicating events. If an event with this ID was previously received, it will not be processed again.", json_schema_extra={'format': 'ulid'})
    type_: Literal["event", "page", "screen"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Categorizes the event as a page view, mobile screen view, or custom event. Defaults to 'event' if not specified.")
    timestamp: int | None = Field(default=None, description="The Unix timestamp indicating when the event occurred. If omitted, the server timestamp at receipt is used. Only events from the past 72 hours can trigger campaigns.", json_schema_extra={'format': 'unix timestamp'})
    data: dict[str, Any] | None = Field(default=None, description="Custom properties associated with the event for use in campaign personalization via liquid templating or for setting customer attributes. Reserved properties (from_address, recipient, reply_to) override campaign settings when present.")
    anonymous_id: str | None = Field(default=None, description="An identifier for anonymous events (such as a cookie value). When set as a customer attribute, all events with this identifier are associated with that customer. Must be unique and non-reusable.")
class TrackRequest(StrictModel):
    """Record a behavioral event (page view, screen view, or custom event) for a customer to enable campaign triggering and audience segmentation. Events with timestamps within the past 72 hours can activate campaigns."""
    path: TrackRequestPath
    body: TrackRequestBody

# Operation: log_anonymous_event
class TrackAnonymousRequestBody(StrictModel):
    anonymous_id: str | None = Field(default=None, description="A unique identifier for the anonymous person, such as a cookie or device ID. When this identifier is later set as an attribute on a person, all events with matching anonymous_id are associated with that person.")
    name: str = Field(default=..., description="The name of the event used to reference it in campaigns and segments. Avoid leading or trailing spaces as they cannot be referenced in campaign logic.")
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="A unique identifier for deduplicating this event. If an event with the same ID was previously received, it will not be processed again.", json_schema_extra={'format': 'ulid'})
    type_: Literal["event", "page", "screen"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The category of event being tracked. Use 'page' for website page views, 'screen' for mobile app screen views, or 'event' for all other event types.")
    timestamp: int | None = Field(default=None, description="The Unix timestamp indicating when the event occurred. If not provided, the server timestamp at receipt time is used.", json_schema_extra={'format': 'unix timestamp'})
    data: dict[str, Any] | None = Field(default=None, description="Additional event metadata as key-value pairs. Can include custom attributes to set on the person, or special fields like 'from_address' and 'reply_to' for campaign triggering.")
class TrackAnonymousRequest(StrictModel):
    """Log an event for an unidentified person using an anonymous identifier. Events can be associated with a person later when their identity is confirmed, enabling campaign triggers within 72 hours of the event timestamp."""
    body: TrackAnonymousRequestBody

# Operation: submit_form
class SubmitFormRequestPath(StrictModel):
    form_id: str = Field(default=..., description="The unique identifier for the form. Use a value that is meaningful to your system and traceable to your backend. If Customer.io does not recognize this identifier, a new form connection will be created automatically.")
class SubmitFormRequestBody(StrictModel):
    data: SubmitFormBodyDataV0 | SubmitFormBodyDataV1 = Field(default=..., description="An object containing form field data and respondent identifiers. Must include at least one identifier field (id, email, or a field mapped to these identifiers) to identify or create the form respondent. All additional keys represent form fields submitted by the respondent; field values must be formatted as strings. Reserved keys (form_id, form_name, form_type, form_url, form_url_param) are ignored if included.")
class SubmitFormRequest(StrictModel):
    """Submit a form response and create or update the respondent in Customer.io. Form submissions are associated with a form connection; if the form_id is unrecognized, a new form connection is automatically created."""
    path: SubmitFormRequestPath
    body: SubmitFormRequestBody

# Operation: merge_customers
class MergeRequestBody(StrictModel):
    primary: MergeBodyPrimaryV0 | MergeBodyPrimaryV1 | MergeBodyPrimaryV2 = Field(default=..., description="The customer profile that will remain after the merge. Identified by `id`, `email`, or `cio_id`. This profile receives merged data from the secondary profile. Must already exist in Customer.io at the time of the merge request.")
    secondary: MergeBodySecondaryV0 | MergeBodySecondaryV1 | MergeBodySecondaryV2 = Field(default=..., description="The customer profile that will be deleted after the merge. Identified by `id`, `email`, or `cio_id`. This profile's attributes, event history, segments, and campaign journeys are merged into the primary profile before deletion.")
class MergeRequest(StrictModel):
    """Merge two customer profiles by consolidating the secondary profile into the primary profile, then deleting the secondary. This operation is irreversible and requires the primary profile to already exist in Customer.io."""
    body: MergeRequestBody

# Operation: report_metric
class MetricsRequestBody(StrictModel):
    delivery_id: str = Field(default=..., description="The CIO-Delivery-ID header value from the notification you want to associate this metric with. This ID links the reported event back to the original message delivery.")
    timestamp: int | None = Field(default=None, description="The Unix timestamp indicating when the event occurred. If omitted, the current time is used.", json_schema_extra={'format': 'unix timestamp'})
    metric: Literal["bounced", "clicked", "converted", "deferred", "delivered", "dropped", "opened", "spammed"] = Field(default=..., description="The type of email metric being reported. Choose the value that best describes the event that occurred.")
    recipient: str | None = Field(default=None, description="The email address of the recipient who received the message and triggered this metric event.")
    reason: str | None = Field(default=None, description="The reason for failure-related metrics such as bounces or drops. Provide context about why the metric occurred.")
    href: str | None = Field(default=None, description="For clicked metrics, the URL or link that the recipient clicked. Include the full link destination.")
class MetricsRequest(StrictModel):
    """Report email metrics from external channels or non-SDK integrations by associating events with a delivery ID from a Customer.io message. Use the CIO-Delivery-ID header value as the delivery_id to track opens, clicks, conversions, bounces, and other email events."""
    body: MetricsRequestBody

# Operation: add_customers_to_segment
class AddToSegmentRequestPath(StrictModel):
    segment_id: int = Field(default=..., description="The unique identifier of the manual segment. Find this ID in the segment's dashboard page under Usage, or retrieve it using the segments API.", json_schema_extra={'format': 'int32'})
class AddToSegmentRequestQuery(StrictModel):
    id_type: Literal["id", "email", "cio_id"] | None = Field(default=None, description="The identifier type for all values in the ids array. All customer identifiers must be of the same type. Defaults to customer ID if not specified.")
class AddToSegmentRequestBody(StrictModel):
    ids: list[str] = Field(default=..., description="Array of customer identifiers to add to the segment. All values must match the id_type parameter. Unmatched entries are ignored. Accepts 1 to 1000 identifiers per request.", min_length=1, max_length=1000)
class AddToSegmentRequest(StrictModel):
    """Add customers to a manual segment by their identifiers. You can add up to 1000 customers per request using their ID, email, or CIO ID."""
    path: AddToSegmentRequestPath
    query: AddToSegmentRequestQuery | None = None
    body: AddToSegmentRequestBody

# Operation: remove_customers_from_segment
class RemoveFromSegmentRequestPath(StrictModel):
    segment_id: int = Field(default=..., description="The unique identifier of the segment from which to remove customers. You can find this ID in the Segments dashboard under Usage, or retrieve it via the Segments API.", json_schema_extra={'format': 'int32'})
class RemoveFromSegmentRequestQuery(StrictModel):
    id_type: Literal["id", "email", "cio_id"] | None = Field(default=None, description="The identifier type for the customers being removed. All values in the ids array must match this type. Defaults to id if not specified.")
class RemoveFromSegmentRequestBody(StrictModel):
    ids: list[str] = Field(default=..., description="Array of customer identifiers to remove from the segment. Must contain between 1 and 1000 identifiers, all matching the type specified in id_type.", min_length=1, max_length=1000)
class RemoveFromSegmentRequest(StrictModel):
    """Remove customers from a manual segment by their identifiers. This operation supports up to 1000 customer IDs per request and requires customers to have id attributes in your workspace."""
    path: RemoveFromSegmentRequestPath
    query: RemoveFromSegmentRequestQuery | None = None
    body: RemoveFromSegmentRequestBody

# Operation: manage_entity
class EntityRequestBody(StrictModel):
    type_: Literal["delivery", "object", "person"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The entity type being modified: a person, object, or delivery record.")
    identifiers: EntityBodyIdentifiersV0 | EntityBodyIdentifiersV1 | EntityBodyIdentifiersV2 | None = Field(default=None, description="The identifier for the person or object being modified. Provide exactly one of: `id` (ULID), `email`, or `cio_id`. Cannot pass multiple identifiers.")
    action: Literal["add_device", "add_relationships", "delete", "delete_device", "delete_relationships", "event", "identify", "identify_anonymous", "merge", "page", "screen", "suppress", "unsuppress"] = Field(default=..., description="The operation to perform on the specified entity type, such as identifying a profile, tracking an event, managing devices, or merging records.")
    timestamp: int | None = Field(default=None, description="Unix timestamp indicating when the attribute update occurred. Use this to control the order of updates when multiple requests are sent in rapid succession.")
    attributes: dict[str, Any] | None = Field(default=None, description="Custom and reserved attributes to add or update for the entity. You can pass custom properties beyond the reserved ones defined in the Track API.")
    cio_relationships: ObjectRelationships | None = Field(default=None, description="Relationship data to associate with the entity, defining connections between people and objects.")
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="A unique ULID used to deduplicate events and prevent duplicate processing.", json_schema_extra={'format': 'ULID'})
    name: Literal["converted", "delivered", "opened"] | None = Field(default=None, description="The name of the event being tracked. Used to identify and trigger campaigns in Customer.io.")
    device: EntityBodyDevice | None = Field(default=None, description="Properties representing an individual device, such as device type, OS, and app version. SDKs automatically gather these properties unless disabled.")
    primary: EntityBodyPrimaryV0 | EntityBodyPrimaryV1 | EntityBodyPrimaryV2 | None = Field(default=None, description="The person to retain after a merge operation, identified by `id`, `email`, or `cio_id`. This person receives attributes from the secondary person. Required when action is `merge`.")
    secondary: EntityBodySecondaryV0 | EntityBodySecondaryV1 | EntityBodySecondaryV2 | None = Field(default=None, description="The person to delete after a merge operation, identified by `id`, `email`, or `cio_id`. This person's information is merged into the primary person and then deleted. Required when action is `merge`.")
class EntityRequest(StrictModel):
    """Create, update, delete, or manage relationships for a person or object (such as a company or product) in Customer.io. Supports operations like identifying profiles, tracking events, managing devices, and merging duplicate person records."""
    body: EntityRequestBody

# Operation: batch_entities
class BatchRequestBody(StrictModel):
    batch: list[Annotated[IdentifyPerson | PersonDelete | PersonEvent | PersonScreen | PersonPage | PersonAddRelationships | PersonDeleteRelationships | PersonAddDevice | PersonDeleteDevice | PersonMerge | PersonSuppress | PersonUnsuppress, Field(discriminator="action")] | Annotated[ObjectIdentify | ObjectIdentifyAnonymous | ObjectDelete | ObjectAddRelationships | ObjectDeleteRelationships, Field(discriminator="action")] | DeliveryOperations] | None = Field(default=None, description="Array of entity payloads representing individual operations. Each object modifies a single person or object. The batch request must not exceed 500kb total, and each individual entity operation must not exceed 32kb.")
class BatchRequest(StrictModel):
    """Submit multiple entity operations in a single request to create or modify people and objects. Combine different entity types (people, objects, deliveries) in one batch for efficient bulk processing."""
    body: BatchRequestBody | None = None

# ============================================================================
# Component Models
# ============================================================================

class CioSubscriptionPreferences(PermissiveModel):
    """Stores your audience's subscription preferences if you enable our [subscription center](/subscription-center/) feature. These items are set automatically when people use the unsubscribe link in your messages, but you can set preferences outside the subscription flow. To update select topic preferences while preserving those set for other topics, use JSON dot notation `"cio_subscription_preferences.topics.topic_<topic ID>":<boolean>`."""
    topics: dict[str, bool] | None = Field(None, description="Contains active topics in your workspace, named `topic_<id>`.")

class DeliveryOperationsAttributes(PermissiveModel):
    """Contains information about the delivery and the individual who received the message."""
    device_token: str = Field(..., description="The device that received the message.")

class DeliveryOperationsIdentifiers(PermissiveModel):
    """Contains identifiers for the delivery itself."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The `delivery_id` for the delivery that you want to attribute metrics to.")

class DeliveryOperations(PermissiveModel):
    """The "delivery" type lets you attribute metrics to messages that don't self-report back to Customer.io, like push and in-app notifications."""
    type_: Literal["delivery"] = Field(..., validation_alias="type", serialization_alias="type", description="The \"delivery\" type lets you attribute metrics to messages that don't self-report back to Customer.io, like push and in-app notifications.")
    action: Literal["event"] = Field(..., description="An `event` action indicates a delivery event. Use the `name` to determine the specific metric that you want to attribute to this delivery.")
    identifiers: DeliveryOperationsIdentifiers = Field(..., description="Contains identifiers for the delivery itself.")
    name: Literal["opened", "converted", "delivered"] = Field(..., description="The name of the metric you want to attribute to this \"delivery\".")
    attributes: DeliveryOperationsAttributes = Field(..., description="Contains information about the delivery and the individual who received the message.")

class DeviceObjectAttributes(PermissiveModel):
    """Attributes that you can reference to segment your audience—like a person's attributes, but specific to a device. These can be either the attributes defined below or custom key-value attributes."""
    device_os: str | None = Field(None, description="The operating system, including the version, on the device.")
    device_model: str | None = Field(None, description="The model of the device a person uses.")
    app_version: str | None = Field(None, description="The version of your app that a customer uses. You might target app versions to let people know when they need to update, or expose them to new features when they do.")
    cio_sdk_version: str | None = Field(None, description="The version of the Customer.io SDK in the app.")
    last_status: Literal["", "bounced", "sent", "suppressed"] | None = Field(None, validation_alias="_last_status", serialization_alias="_last_status", description="The delivery status of the last message sent to the device—sent, bounced, or suppressed. An empty string indicates that that the device hasn't received a push yet.")
    device_locale: str | None = Field(None, description="The four-letter [IETF language code](/localization/#supported-languages) for the device. For example, `en-MX` (indicating an app in Spanish formatted for a user in Mexico) or `es-ES` (indicating an app in Spanish formatted for a user in Spain).")
    push_enabled: Literal["true", "false"] | None = Field(None, description="If `\"true\"`, the device is opted-in and can receive push notifications.")

class DeviceObjectCommon(PermissiveModel):
    """Device information common to the v1 and v2 APIs."""
    last_used: int | None = Field(None, description="The `timestamp` when you last identified this device. If you don't pass a timestamp when you add or update a device, we use the time of the request itself. Our SDKs identify a device when a person launches their app.", json_schema_extra={'format': 'unix timestamp'})
    platform: Literal["ios", "android"] = Field(..., description="The device/messaging platform.")
    attributes: dict[str, str] | None = Field(None, description="Attributes that you can reference to segment your audience—like a person's attributes, but specific to a device. These can be either the attributes defined below or custom key-value attributes.")

class DeviceObject(PermissiveModel):
    """The properties representing an individual device. [Our SDK's](/integrations/sdk/) gather all the properties defined below automatically, unless you disable the `autoTrackDeviceAttributes` setting. You can reference the properties outside the `attributes` object in segments or in Liquid."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The device token.")
    last_used: int | None = Field(None, description="The `timestamp` when you last identified this device. If you don't pass a timestamp when you add or update a device, we use the time of the request itself. Our SDKs identify a device when a person launches their app.", json_schema_extra={'format': 'unix timestamp'})
    platform: Literal["ios", "android"] = Field(..., description="The device/messaging platform.")
    attributes: dict[str, str] | None = Field(None, description="Attributes that you can reference to segment your audience—like a person's attributes, but specific to a device. These can be either the attributes defined below or custom key-value attributes.")

class DeviceObjectCommonAttributes(PermissiveModel):
    """Attributes that you can reference to segment your audience—like a person's attributes, but specific to a device. These can be either the attributes defined below or custom key-value attributes."""
    device_os: str | None = Field(None, description="The operating system, including the version, on the device.")
    device_model: str | None = Field(None, description="The model of the device a person uses.")
    app_version: str | None = Field(None, description="The version of your app that a customer uses. You might target app versions to let people know when they need to update, or expose them to new features when they do.")
    cio_sdk_version: str | None = Field(None, description="The version of the Customer.io SDK in the app.")
    last_status: Literal["", "bounced", "sent", "suppressed"] | None = Field(None, validation_alias="_last_status", serialization_alias="_last_status", description="The delivery status of the last message sent to the device—sent, bounced, or suppressed. An empty string indicates that that the device hasn't received a push yet.")
    device_locale: str | None = Field(None, description="The four-letter [IETF language code](/localization/#supported-languages) for the device. For example, `en-MX` (indicating an app in Spanish formatted for a user in Mexico) or `es-ES` (indicating an app in Spanish formatted for a user in Spain).")
    push_enabled: Literal["true", "false"] | None = Field(None, description="If `\"true\"`, the device is opted-in and can receive push notifications.")

class EntityBodyDevice(PermissiveModel):
    """The properties representing an individual device. [Our SDK's](/integrations/sdk/) gather all the properties defined below automatically, unless you disable the `autoTrackDeviceAttributes` setting. You can reference the properties outside the `attributes` object in segments."""
    token: str = Field(..., description="The device token.")
    last_used: int | None = Field(None, description="The `timestamp` when you last identified this device. If you don't pass a timestamp when you add or update a device, we use the time of the request itself. Our SDKs identify a device when a person launches their app.", json_schema_extra={'format': 'unix timestamp'})
    platform: Literal["ios", "android"] = Field(..., description="The device/messaging platform.")
    attributes: dict[str, str] | None = Field(None, description="Attributes that you can reference to segment your audience—like a person's attributes, but specific to a device. These can be either the attributes defined below or custom key-value attributes.")

class EntityBodyIdentifiersV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class EntityBodyIdentifiersV1(PermissiveModel):
    email: str

class EntityBodyIdentifiersV2(PermissiveModel):
    cio_id: str

class EntityBodyPrimaryV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class EntityBodyPrimaryV1(PermissiveModel):
    email: str

class EntityBodyPrimaryV2(PermissiveModel):
    cio_id: str

class EntityBodySecondaryV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class EntityBodySecondaryV1(PermissiveModel):
    email: str

class EntityBodySecondaryV2(PermissiveModel):
    cio_id: str

class IdentifyBodyCioRelationshipsRelationshipsItemIdentifiersV0(PermissiveModel):
    object_type_id: str = Field(..., description="The object type an object belongs to—like \"Companies\" or \"Accounts\". Object type IDs are string-formatted integers that begin at `1` and increment for each new type.")
    object_id: str = Field(..., description="The unique identifier for an object. If you use an `object_id` that already exists, we'll update the object accordingly.")

class IdentifyBodyCioRelationshipsRelationshipsItemIdentifiersV1(PermissiveModel):
    cio_object_id: str = Field(..., description="A unique value that Customer.io sets for an object when you create it. This ID is immutable.")

class IdentifyBodyCioRelationshipsRelationshipsItem(PermissiveModel):
    identifiers: IdentifyBodyCioRelationshipsRelationshipsItemIdentifiersV0 | IdentifyBodyCioRelationshipsRelationshipsItemIdentifiersV1 | None = Field(None, description="The identifiers for a particular object. You can use either the `object_type_id` and `object_id` (where `object_type_id` represents the type of object and the `object_id` is the individual identifier for the object) or the `cio_object_id`.")
    relationship_attributes: dict[str, Any] | None = Field(None, description="The attributes associated with a relationship. Passing null or an empty string removes the attribute from the relationship.\n")

class IdentifyPersonAttributes(PermissiveModel):
    """Attributes that you want to add or update for this person. You can pass properties that aren't defined below to set custom attributes; the defined properties are reserved in the Customer.io Track API."""
    cio_subscription_preferences: CioSubscriptionPreferences | None = None
    update: bool | None = Field(False, validation_alias="_update", serialization_alias="_update", description="By default, an `identify` request creates a new person if they don't already exist. If you perform multiple requests in rapid succession, there's a danger that you could create multiple profiles. If you know that a profile already exists and you want to update it, set this value to `true`, and Customer.io will _not_ create a new profile, even if the person doesn't exist.\n\nIf the identifiers in your request don't belong to an existing person, the request does nothing.\n")

class IdentifyPersonIdentifiersV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class IdentifyPersonIdentifiersV1(PermissiveModel):
    email: str

class IdentifyPersonIdentifiersV2(PermissiveModel):
    cio_id: str

class IdentifyPersonV1Attributes(PermissiveModel):
    """Attributes that you want to add or update for this person. You can pass properties that aren't defined below to set custom attributes; the defined properties are reserved in the Customer.io Track API."""
    cio_subscription_preferences: CioSubscriptionPreferences | None = None
    update: bool | None = Field(False, validation_alias="_update", serialization_alias="_update", description="By default, an `identify` request creates a new person if they don't already exist. If you perform multiple requests in rapid succession, there's a danger that you could create multiple profiles. If you know that a profile already exists and you want to update it, set this value to `true`, and Customer.io will _not_ create a new profile, even if the person doesn't exist.\n\nIf the identifiers in your request don't belong to an existing person, the request does nothing.\n")

class MergeBodyPrimaryV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")

class MergeBodyPrimaryV1(PermissiveModel):
    email: str | None = None

class MergeBodyPrimaryV2(PermissiveModel):
    cio_id: str | None = None

class MergeBodySecondaryV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")

class MergeBodySecondaryV1(PermissiveModel):
    email: str | None = None

class MergeBodySecondaryV2(PermissiveModel):
    cio_id: str | None = None

class ObjectAttributes(RootModel[dict[str, Any]]):
    pass

class ObjectCommonIdentifiersV0(PermissiveModel):
    object_type_id: str
    object_id: str = Field(..., description="The unique identifier for an object. If you use an `object_id` that already exists, we'll update the object accordingly.")

class ObjectCommonIdentifiersV1(PermissiveModel):
    cio_object_id: str = Field(..., description="A unique value that Customer.io sets for an object when you create it. This ID is immutable.")

class ObjectCommonIdentifyIdentifiersV0(PermissiveModel):
    object_type_id: str
    object_id: str = Field(..., description="The unique identifier for an object. If you use an `object_id` that already exists, we'll update the object accordingly.")

class ObjectCommonIdentifyIdentifiersV1(PermissiveModel):
    cio_object_id: str = Field(..., description="A unique value that Customer.io sets for an object when you create it. This ID is immutable.")

class ObjectCommonIdentify(PermissiveModel):
    identifiers: ObjectCommonIdentifyIdentifiersV0 | ObjectCommonIdentifyIdentifiersV1 = Field(..., description="The identifiers for a custom object. When identifying a new object, you *must* use both the `object_type_id` and `object_id` (where `object_type_id` is an integer representing the type of object and the `object_id` is the individual identifier for the object).\n\nIf you're updating an existing object, you can use either the `object_type_id` and `object_id` or the `cio_object_id` (where `cio_object_id` is an immutable unique value that Customer.io sets for an object when you create it).\n")
    type_: Literal["object"] = Field(..., validation_alias="type", serialization_alias="type", description="The operation modifies a single object—non person data.")

class ObjectIdentifiersIdentifiersV0(PermissiveModel):
    object_type_id: str
    object_id: str = Field(..., description="The unique identifier for an object. If you use an `object_id` that already exists, we'll update the object accordingly.")

class ObjectIdentifiersIdentifiersV1(PermissiveModel):
    cio_object_id: str = Field(..., description="A unique value that Customer.io sets for an object when you create it. This ID is immutable.")

class ObjectIdentifiers(PermissiveModel):
    identifiers: ObjectIdentifiersIdentifiersV0 | ObjectIdentifiersIdentifiersV1 | None = Field(None, description="The identifiers for a particular object. You can use either the `object_type_id` and `object_id` (where `object_type_id` represents the type of object and the `object_id` is the individual identifier for the object) or the `cio_object_id`.")

class ObjectCommon(PermissiveModel):
    identifiers: ObjectCommonIdentifiersV0 | ObjectCommonIdentifiersV1 | None = Field(None, description="The identifiers for a particular object. You can use either the `object_type_id` and `object_id` (where `object_type_id` represents the type of object and the `object_id` is the individual identifier for the object) or the `cio_object_id`.")
    type_: Literal["object"] = Field(..., validation_alias="type", serialization_alias="type", description="The operation modifies a single object—non person data.")

class ObjectDelete(PermissiveModel):
    """Delete an object. This also removes relationships from people.
"""
    action: Literal["delete"] = Field(..., description="Indicates that the operation will `delete` the the item of the specified `type`.")

class ObjectIdentifyAnonymousCioRelationshipsItemIdentifiers(PermissiveModel):
    anonymous_id: str | None = None

class ObjectIdentifyAnonymousCioRelationshipsItem(PermissiveModel):
    identifiers: ObjectIdentifyAnonymousCioRelationshipsItemIdentifiers | None = None
    relationship_attributes: dict[str, Any] | None = Field(None, description="Coming October 2023 - The attributes associated with a relationship. Passing null or an empty string removes the attribute from the relationship.")

class ObjectIdentifyAnonymousIdentifiersV0(PermissiveModel):
    object_type_id: str
    object_id: str = Field(..., description="The unique identifier for an object. If you use an `object_id` that already exists, we'll update the object accordingly.")

class ObjectIdentifyAnonymousIdentifiersV1(PermissiveModel):
    cio_object_id: str = Field(..., description="A unique value that Customer.io sets for an object when you create it. This ID is immutable.")

class ObjectIdentifyAnonymous(PermissiveModel):
    """The `identify_anonymous` action lets you relate an object to a person who hasn't yet identified themselves by anonymous_id. When you identify the person, their anonymous relationship will carry over to the identified profile."""
    identifiers: ObjectIdentifyAnonymousIdentifiersV0 | ObjectIdentifyAnonymousIdentifiersV1 = Field(..., description="The identifiers for a custom object. When identifying a new object, you *must* use both the `object_type_id` and `object_id` (where `object_type_id` is an integer representing the type of object and the `object_id` is the individual identifier for the object).\n\nIf you're updating an existing object, you can use either the `object_type_id` and `object_id` or the `cio_object_id` (where `cio_object_id` is an immutable unique value that Customer.io sets for an object when you create it).\n")
    type_: Literal["object"] = Field(..., validation_alias="type", serialization_alias="type", description="The operation modifies a single object—non person data.")
    action: Literal["identify_anonymous"] = Field(..., description="Indicates that the operation will `identify` the item of the specified `type` and relate it to an `anonymous_id`.")
    attributes: ObjectAttributes | None = None
    cio_relationships: list[ObjectIdentifyAnonymousCioRelationshipsItem] | None = Field(None, description="The anonymous people you want to associate with an object. Each object in the array contains an `anonymous_id` representing a person you haven't yet identified by `id` or `email`.")

class ObjectIdentifyAnonymousV1CioRelationshipsItemIdentifiers(PermissiveModel):
    anonymous_id: str | None = None

class ObjectIdentifyAnonymousV1CioRelationshipsItem(PermissiveModel):
    identifiers: ObjectIdentifyAnonymousV1CioRelationshipsItemIdentifiers | None = None
    relationship_attributes: dict[str, Any] | None = Field(None, description="Coming October 2023 - The attributes associated with a relationship. Passing null or an empty string removes the attribute from the relationship.")

class ObjectIdentifyIdentifiersV0(PermissiveModel):
    object_type_id: str
    object_id: str = Field(..., description="The unique identifier for an object. If you use an `object_id` that already exists, we'll update the object accordingly.")

class ObjectIdentifyIdentifiersV1(PermissiveModel):
    cio_object_id: str = Field(..., description="A unique value that Customer.io sets for an object when you create it. This ID is immutable.")

class ObjectRelationshipsItemIdentifiersV0(PermissiveModel):
    object_type_id: str
    object_id: str = Field(..., description="The unique identifier for an object. If you use an `object_id` that already exists, we'll update the object accordingly.")

class ObjectRelationshipsItemIdentifiersV1(PermissiveModel):
    cio_object_id: str = Field(..., description="A unique value that Customer.io sets for an object when you create it. This ID is immutable.")

class PersonAddDeviceDevice(PermissiveModel):
    """The properties representing an individual device. [Our SDK's](/integrations/sdk/) gather all the properties defined below automatically, unless you disable the `autoTrackDeviceAttributes` setting. You can reference the properties outside the `attributes` object in segments."""
    token: str = Field(..., description="The device token.")
    last_used: int | None = Field(None, description="The `timestamp` when you last identified this device. If you don't pass a timestamp when you add or update a device, we use the time of the request itself. Our SDKs identify a device when a person launches their app.", json_schema_extra={'format': 'unix timestamp'})
    platform: Literal["ios", "android"] = Field(..., description="The device/messaging platform.")
    attributes: dict[str, str] | None = Field(None, description="Attributes that you can reference to segment your audience—like a person's attributes, but specific to a device. These can be either the attributes defined below or custom key-value attributes.")

class PersonAddDeviceDeviceAttributes(PermissiveModel):
    """Attributes that you can reference to segment your audience—like a person's attributes, but specific to a device. These can be either the attributes defined below or custom key-value attributes."""
    device_os: str | None = Field(None, description="The operating system, including the version, on the device.")
    device_model: str | None = Field(None, description="The model of the device a person uses.")
    app_version: str | None = Field(None, description="The version of your app that a customer uses. You might target app versions to let people know when they need to update, or expose them to new features when they do.")
    cio_sdk_version: str | None = Field(None, description="The version of the Customer.io SDK in the app.")
    last_status: Literal["", "bounced", "sent", "suppressed"] | None = Field(None, validation_alias="_last_status", serialization_alias="_last_status", description="The delivery status of the last message sent to the device—sent, bounced, or suppressed. An empty string indicates that that the device hasn't received a push yet.")
    device_locale: str | None = Field(None, description="The four-letter [IETF language code](/localization/#supported-languages) for the device. For example, `en-MX` (indicating an app in Spanish formatted for a user in Mexico) or `es-ES` (indicating an app in Spanish formatted for a user in Spain).")
    push_enabled: Literal["true", "false"] | None = Field(None, description="If `\"true\"`, the device is opted-in and can receive push notifications.")

class PersonAddDeviceIdentifiersV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class PersonAddDeviceIdentifiersV1(PermissiveModel):
    email: str

class PersonAddDeviceIdentifiersV2(PermissiveModel):
    cio_id: str

class PersonAddDeviceV1Device(PermissiveModel):
    """The properties representing an individual device. [Our SDK's](/integrations/sdk/) gather all the properties defined below automatically, unless you disable the `autoTrackDeviceAttributes` setting. You can reference the properties outside the `attributes` object in segments."""
    token: str = Field(..., description="The device token.")
    last_used: int | None = Field(None, description="The `timestamp` when you last identified this device. If you don't pass a timestamp when you add or update a device, we use the time of the request itself. Our SDKs identify a device when a person launches their app.", json_schema_extra={'format': 'unix timestamp'})
    platform: Literal["ios", "android"] = Field(..., description="The device/messaging platform.")
    attributes: dict[str, str] | None = Field(None, description="Attributes that you can reference to segment your audience—like a person's attributes, but specific to a device. These can be either the attributes defined below or custom key-value attributes.")

class PersonAddDeviceV1DeviceAttributes(PermissiveModel):
    """Attributes that you can reference to segment your audience—like a person's attributes, but specific to a device. These can be either the attributes defined below or custom key-value attributes."""
    device_os: str | None = Field(None, description="The operating system, including the version, on the device.")
    device_model: str | None = Field(None, description="The model of the device a person uses.")
    app_version: str | None = Field(None, description="The version of your app that a customer uses. You might target app versions to let people know when they need to update, or expose them to new features when they do.")
    cio_sdk_version: str | None = Field(None, description="The version of the Customer.io SDK in the app.")
    last_status: Literal["", "bounced", "sent", "suppressed"] | None = Field(None, validation_alias="_last_status", serialization_alias="_last_status", description="The delivery status of the last message sent to the device—sent, bounced, or suppressed. An empty string indicates that that the device hasn't received a push yet.")
    device_locale: str | None = Field(None, description="The four-letter [IETF language code](/localization/#supported-languages) for the device. For example, `en-MX` (indicating an app in Spanish formatted for a user in Mexico) or `es-ES` (indicating an app in Spanish formatted for a user in Spain).")
    push_enabled: Literal["true", "false"] | None = Field(None, description="If `\"true\"`, the device is opted-in and can receive push notifications.")

class PersonAddRelationshipsIdentifiersV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class PersonAddRelationshipsIdentifiersV1(PermissiveModel):
    email: str

class PersonAddRelationshipsIdentifiersV2(PermissiveModel):
    cio_id: str

class PersonCommonIdentifiersV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class PersonCommonIdentifiersV1(PermissiveModel):
    email: str

class PersonCommonIdentifiersV2(PermissiveModel):
    cio_id: str

class PersonCommon(PermissiveModel):
    type_: Literal["person"] = Field(..., validation_alias="type", serialization_alias="type", description="The operation modifies a person in Customer.io")
    identifiers: PersonCommonIdentifiersV0 | PersonCommonIdentifiersV1 | PersonCommonIdentifiersV2 = Field(..., description="The person you want to perform an action for—one of either `id`, `email`, or `cio_id`. You cannot pass multiple identifiers.")

class PersonAddDevice(PermissiveModel):
    """Assign devices to a person."""
    type_: Literal["person"] = Field(..., validation_alias="type", serialization_alias="type", description="The operation modifies a person in Customer.io")
    identifiers: PersonAddDeviceIdentifiersV0 | PersonAddDeviceIdentifiersV1 | PersonAddDeviceIdentifiersV2 = Field(..., description="The person you want to perform an action for—one of either `id`, `email`, or `cio_id`. You cannot pass multiple identifiers.")
    action: Literal["add_device"] = Field(..., description="Add a mobile device to a person's profile.")
    device: PersonAddDeviceDevice = Field(..., description="The properties representing an individual device. [Our SDK's](/integrations/sdk/) gather all the properties defined below automatically, unless you disable the `autoTrackDeviceAttributes` setting. You can reference the properties outside the `attributes` object in segments.")

class PersonDeleteDeviceDevice(PermissiveModel):
    """The device you want to remove."""
    token: str = Field(..., description="The token of the device you want to remove.")

class PersonDeleteDeviceIdentifiersV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class PersonDeleteDeviceIdentifiersV1(PermissiveModel):
    email: str

class PersonDeleteDeviceIdentifiersV2(PermissiveModel):
    cio_id: str

class PersonDeleteDevice(PermissiveModel):
    """Delete devices that belong to a person."""
    type_: Literal["person"] = Field(..., validation_alias="type", serialization_alias="type", description="The operation modifies a person in Customer.io")
    identifiers: PersonDeleteDeviceIdentifiersV0 | PersonDeleteDeviceIdentifiersV1 | PersonDeleteDeviceIdentifiersV2 = Field(..., description="The person you want to perform an action for—one of either `id`, `email`, or `cio_id`. You cannot pass multiple identifiers.")
    action: Literal["delete_device"] = Field(..., description="Delete a device from a person's profile.")
    device: PersonDeleteDeviceDevice = Field(..., description="The device you want to remove.")

class PersonDeleteDeviceV1Device(PermissiveModel):
    """The device you want to remove."""
    token: str = Field(..., description="The token of the device you want to remove.")

class PersonDeleteIdentifiersV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class PersonDeleteIdentifiersV1(PermissiveModel):
    email: str

class PersonDeleteIdentifiersV2(PermissiveModel):
    cio_id: str

class PersonDelete(PermissiveModel):
    """Delete a person from your workspace."""
    type_: Literal["person"] = Field(..., validation_alias="type", serialization_alias="type", description="The operation modifies a person in Customer.io")
    identifiers: PersonDeleteIdentifiersV0 | PersonDeleteIdentifiersV1 | PersonDeleteIdentifiersV2 = Field(..., description="The person you want to perform an action for—one of either `id`, `email`, or `cio_id`. You cannot pass multiple identifiers.")
    action: Literal["delete"] = Field(..., description="Indicates that the operation will `delete` the the item of the specified `type`.")

class PersonDeleteRelationshipsIdentifiersV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class PersonDeleteRelationshipsIdentifiersV1(PermissiveModel):
    email: str

class PersonDeleteRelationshipsIdentifiersV2(PermissiveModel):
    cio_id: str

class PersonEventAttributes(PermissiveModel):
    """Additional information that you might want to reference in a message using liquid or use to set attributes on the identified person.
"""
    recipient: str | None = Field(None, description="The email address of the person associated with the event, overriding the `to` field in emails triggered by the event.", json_schema_extra={'format': 'email'})
    from_address: str | None = Field(None, description="The address you want to trigger messages from, overriding the `from` field in emails triggered by the event.", json_schema_extra={'format': 'email'})
    reply_to: str | None = Field(None, description="The address you want to receive replies to, overriding the `reply to` field for emails triggered by the event.", json_schema_extra={'format': 'email'})

class PersonEventIdentifiersV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class PersonEventIdentifiersV1(PermissiveModel):
    email: str

class PersonEventIdentifiersV2(PermissiveModel):
    cio_id: str

class PersonEvent(PermissiveModel):
    """A custom event attributed to a person. You can use events to trigger campaigns, or reference event information using liquid in your messages."""
    type_: Literal["person"] = Field(..., validation_alias="type", serialization_alias="type", description="The operation modifies a person in Customer.io")
    identifiers: PersonEventIdentifiersV0 | PersonEventIdentifiersV1 | PersonEventIdentifiersV2 = Field(..., description="The person you want to perform an action for—one of either `id`, `email`, or `cio_id`. You cannot pass multiple identifiers.")
    action: Literal["event"] = Field(..., description="A custom event attributed to the specified person.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="A valid ULID used to deduplicate events. Note - our Python and Ruby libraries do not pass this id.", json_schema_extra={'format': 'ULID'})
    name: str = Field(..., description="The name of the event. This is how you'll find your event in Customer.io or select it when using events as campaign triggers.")
    timestamp: int | None = Field(None, description="The Unix timestamp when the event happened.")
    attributes: dict[str, Any] | None = Field(None, description="Additional information that you might want to reference in a message using liquid or use to set attributes on the identified person.\n")

class PersonEventV1Attributes(PermissiveModel):
    """Additional information that you might want to reference in a message using liquid or use to set attributes on the identified person.
"""
    recipient: str | None = Field(None, description="The email address of the person associated with the event, overriding the `to` field in emails triggered by the event.", json_schema_extra={'format': 'email'})
    from_address: str | None = Field(None, description="The address you want to trigger messages from, overriding the `from` field in emails triggered by the event.", json_schema_extra={'format': 'email'})
    reply_to: str | None = Field(None, description="The address you want to receive replies to, overriding the `reply to` field for emails triggered by the event.", json_schema_extra={'format': 'email'})

class PersonMergePrimaryV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class PersonMergePrimaryV1(PermissiveModel):
    email: str

class PersonMergePrimaryV2(PermissiveModel):
    cio_id: str

class PersonMergeSecondaryV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class PersonMergeSecondaryV1(PermissiveModel):
    email: str

class PersonMergeSecondaryV2(PermissiveModel):
    cio_id: str

class PersonMerge(PermissiveModel):
    """Merge two people. You'll merge the `secondary` person into the `primary`. The primary profile remains after the merge and the secondary is deleted. This operation is _not_ reversible.

**Important:** The primary profile must already exist in Customer.io for the merge operation to work. If the primary profile doesn't exist, the merge request will not perform any action. This can lead to race conditions if you have concurrent requests that create a profile and merge profiles with the same primary ID.

See our page on [merging duplicate people](/merge-people/) for more information.
"""
    type_: Literal["person"] = Field(..., validation_alias="type", serialization_alias="type", description="The operation modifies a person in Customer.io")
    action: Literal["merge"] = Field(..., description="Merge two people. You'll merge the `secondary` person into the `primary`. The primary profile remains after the merge and the secondary is deleted. This operation is _not_ reversible. See our page on [merging duplicate people](/merge-people/) for more information.\n")
    primary: PersonMergePrimaryV0 | PersonMergePrimaryV1 | PersonMergePrimaryV2 = Field(..., description="The person that you want to remain after the merge, identified by one of `id`, `email`, or `cio_id`. This person receives information from the secondary person in the merge. \n        \nIf email is disabled as an identifier in your [workspace settings](https://fly.customer.io/workspaces/last/settings/edit), then you must reference people by `id` or `cio_id`. Under How to Modify, `id` must be set to \"Reference people by cio_id\" for a successful merge. \n")
    secondary: PersonMergeSecondaryV0 | PersonMergeSecondaryV1 | PersonMergeSecondaryV2 = Field(..., description="The person that you want to delete after the merge, identified by one of `id`, `email`, or `cio_id`. This person's information is merged into the primary person's profile and then it is deleted.\n      \nIf email is disabled as an identifier in your [workspace settings](https://fly.customer.io/workspaces/last/settings/edit), then you must reference people by `id` or `cio_id`. Under How to Modify, `id` must be set to \"Reference people by cio_id\" for a successful merge.\n")

class PersonPageAttributes(PermissiveModel):
    """Additional information that you might want to reference in a message using liquid or use to set attributes on the identified person."""
    path: str | None = Field(None, description="The path portion of the page's URL. Equivalent to the canonical `path` which defaults to `location.pathname` from the DOM API.")
    referrer: str | None = Field(None, description="The previous page's full URL. Equivalent to `document.referrer` from the DOM API.")
    search: str | None = Field(None, description="The query string portion of the page's URL. Equivalent to `location.search` from the DOM API.")
    title: str | None = Field(None, description="The page's title. Equivalent to `document.title` from the DOM API.")
    url: str | None = Field(None, description="A page's full URL. We first look for the canonical URL. If the canonical URL is not provided, we'll use `location.href` from the DOM API.")
    keywords: list[str] | None = Field(None, description="A list/array of keywords describing the page's content. The keywords are likely the same as, or similar to, the keywords you would find in an HTML `meta` tag for SEO purposes. This property is mainly used by content publishers that rely heavily on pageview tracking. This isn't automatically collected.")

class PersonPageIdentifiersV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class PersonPageIdentifiersV1(PermissiveModel):
    email: str

class PersonPageIdentifiersV2(PermissiveModel):
    cio_id: str

class PersonPage(PermissiveModel):
    """A web "pageview" event attributed to a person. Our `screen` and `page` event types are more specific than our standard `event`, and help you track and target people based on the pages people visit in your mobile app or website."""
    type_: Literal["person"] = Field(..., validation_alias="type", serialization_alias="type", description="The operation modifies a person in Customer.io")
    identifiers: PersonPageIdentifiersV0 | PersonPageIdentifiersV1 | PersonPageIdentifiersV2 = Field(..., description="The person you want to perform an action for—one of either `id`, `email`, or `cio_id`. You cannot pass multiple identifiers.")
    action: Literal["page"] = Field(..., description="A web \"pageview\" event attributed to a person. Our `screen` and `page` event types are more specific than our standard `event`, and help you track and target people based on the pages people visit in your mobile app or website.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="A valid ULID used to deduplicate events. Note - our Python and Ruby libraries do not pass this id.", json_schema_extra={'format': 'ULID'})
    name: str = Field(..., description="The name of the page or page path that a person visited. This is how you'll find and select page view events in Customer.io.")
    timestamp: int | None = Field(None, description="The Unix timestamp when the event happened.")
    attributes: dict[str, Any] | None = Field(None, description="Additional information that you might want to reference in a message using liquid or use to set attributes on the identified person.")

class PersonPageV1Attributes(PermissiveModel):
    """Additional information that you might want to reference in a message using liquid or use to set attributes on the identified person."""
    path: str | None = Field(None, description="The path portion of the page's URL. Equivalent to the canonical `path` which defaults to `location.pathname` from the DOM API.")
    referrer: str | None = Field(None, description="The previous page's full URL. Equivalent to `document.referrer` from the DOM API.")
    search: str | None = Field(None, description="The query string portion of the page's URL. Equivalent to `location.search` from the DOM API.")
    title: str | None = Field(None, description="The page's title. Equivalent to `document.title` from the DOM API.")
    url: str | None = Field(None, description="A page's full URL. We first look for the canonical URL. If the canonical URL is not provided, we'll use `location.href` from the DOM API.")
    keywords: list[str] | None = Field(None, description="A list/array of keywords describing the page's content. The keywords are likely the same as, or similar to, the keywords you would find in an HTML `meta` tag for SEO purposes. This property is mainly used by content publishers that rely heavily on pageview tracking. This isn't automatically collected.")

class PersonScreenIdentifiersV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class PersonScreenIdentifiersV1(PermissiveModel):
    email: str

class PersonScreenIdentifiersV2(PermissiveModel):
    cio_id: str

class PersonScreen(PermissiveModel):
    """A mobile "screenview" event attributed to a person. Our `screen` and `page` event types are more specific than our standard `event`, and help you track and target people based on the pages people visit in your mobile app or website."""
    type_: Literal["person"] = Field(..., validation_alias="type", serialization_alias="type", description="The operation modifies a person in Customer.io")
    identifiers: PersonScreenIdentifiersV0 | PersonScreenIdentifiersV1 | PersonScreenIdentifiersV2 = Field(..., description="The person you want to perform an action for—one of either `id`, `email`, or `cio_id`. You cannot pass multiple identifiers.")
    action: Literal["screen"] = Field(..., description="A mobile \"screenview\" event attributed to a person. Our `screen` and `page` event types are more specific than our standard `event`, and help you track and target people based on the pages people visit in your mobile app or website.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="A valid ULID used to deduplicate events. Note - our Python and Ruby libraries do not pass this id.", json_schema_extra={'format': 'ULID'})
    name: str = Field(..., description="The name of the screen a person visited. This is how you'll find and select screen view events in Customer.io.")
    timestamp: int | None = Field(None, description="The Unix timestamp when the event happened.")
    attributes: dict[str, Any] | None = Field(None, description="Additional information that you might want to reference in a message using liquid or use to set attributes on the identified person.")

class PersonSuppressIdentifiersV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class PersonSuppressIdentifiersV1(PermissiveModel):
    email: str

class PersonSuppressIdentifiersV2(PermissiveModel):
    cio_id: str

class PersonSuppress(PermissiveModel):
    """Suppress a person's identifier(s) in Customer.io, so that you can't message a person or add their identifiers back to your workspace. This is separate from suppressions performed by your email provider."""
    type_: Literal["person"] = Field(..., validation_alias="type", serialization_alias="type", description="The operation modifies a person in Customer.io")
    identifiers: PersonSuppressIdentifiersV0 | PersonSuppressIdentifiersV1 | PersonSuppressIdentifiersV2 = Field(..., description="The person you want to perform an action for—one of either `id`, `email`, or `cio_id`. You cannot pass multiple identifiers.")
    action: Literal["suppress"] = Field(..., description="Suppress a person's identifier(s) in Customer.io, so that you can't message a person or add their identifiers back to your workspace. This is separate from suppressions performed by your email provider.")

class PersonUnsuppressIdentifiersV0(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class PersonUnsuppressIdentifiersV1(PermissiveModel):
    email: str

class PersonUnsuppressIdentifiersV2(PermissiveModel):
    cio_id: str

class PersonUnsuppress(PermissiveModel):
    """Unsuppress a person's identifier(s) in Customer.io, so that you can message a person or add their identifiers back to your workspace. This does not unsuppress addresses that were previously suppressed by your email provider."""
    type_: Literal["person"] = Field(..., validation_alias="type", serialization_alias="type", description="The operation modifies a person in Customer.io")
    identifiers: PersonUnsuppressIdentifiersV0 | PersonUnsuppressIdentifiersV1 | PersonUnsuppressIdentifiersV2 = Field(..., description="The person you want to perform an action for—one of either `id`, `email`, or `cio_id`. You cannot pass multiple identifiers.")
    action: Literal["unsuppress"] = Field(..., description="Unsuppress a person's identifier(s) in Customer.io, so that you can message a person or add their identifiers back to your workspace. This does not unsuppress addresses that were previously suppressed by your email provider.")

class RelationshipAttributes(RootModel[dict[str, Any]]):
    pass

class ObjectRelationshipsItem(PermissiveModel):
    identifiers: ObjectRelationshipsItemIdentifiersV0 | ObjectRelationshipsItemIdentifiersV1 | None = Field(None, description="The identifiers for a particular object. You can use either the `object_type_id` and `object_id` (where `object_type_id` represents the type of object and the `object_id` is the individual identifier for the object) or the `cio_object_id`.")
    relationship_attributes: RelationshipAttributes | None = None

class ObjectRelationships(RootModel[list[ObjectRelationshipsItem]]):
    pass

class IdentifyPerson(PermissiveModel):
    """Add or update a person."""
    type_: Literal["person"] = Field(..., validation_alias="type", serialization_alias="type", description="The operation modifies a person in Customer.io")
    identifiers: IdentifyPersonIdentifiersV0 | IdentifyPersonIdentifiersV1 | IdentifyPersonIdentifiersV2 = Field(..., description="The person you want to perform an action for—one of either `id`, `email`, or `cio_id`. You cannot pass multiple identifiers.")
    action: Literal["identify"] = Field(..., description="Indicates that the operation will `identify` the the item of the specified `type`.")
    timestamp: int | None = Field(None, description="The Unix timestamp for when the attribute update occurred. This can be used to control the order of attribute updates when multiple requests are sent in rapid succession.")
    attributes: dict[str, Any] | None = Field(None, description="Attributes that you want to add or update for this person. You can pass properties that aren't defined below to set custom attributes; the defined properties are reserved in the Customer.io Track API.")
    cio_relationships: ObjectRelationships | None = None

class PersonAddRelationships(PermissiveModel):
    """Associate multiple objects with a person."""
    type_: Literal["person"] = Field(..., validation_alias="type", serialization_alias="type", description="The operation modifies a person in Customer.io")
    identifiers: PersonAddRelationshipsIdentifiersV0 | PersonAddRelationshipsIdentifiersV1 | PersonAddRelationshipsIdentifiersV2 = Field(..., description="The person you want to perform an action for—one of either `id`, `email`, or `cio_id`. You cannot pass multiple identifiers.")
    action: Literal["add_relationships"] = Field(..., description="This operation associates a person with one or more objects.")
    cio_relationships: ObjectRelationships

class PersonDeleteRelationships(PermissiveModel):
    """Remove multiple object relationships from a person."""
    type_: Literal["person"] = Field(..., validation_alias="type", serialization_alias="type", description="The operation modifies a person in Customer.io")
    identifiers: PersonDeleteRelationshipsIdentifiersV0 | PersonDeleteRelationshipsIdentifiersV1 | PersonDeleteRelationshipsIdentifiersV2 = Field(..., description="The person you want to perform an action for—one of either `id`, `email`, or `cio_id`. You cannot pass multiple identifiers.")
    action: Literal["delete_relationships"] = Field(..., description="This operation deletes an object relationship from one or more people.")
    cio_relationships: ObjectRelationships

class SubmitFormBodyDataV0(PermissiveModel):
    """Identify the person who submitted your form by email."""
    email: str

class SubmitFormBodyDataV1(PermissiveModel):
    """Identify the person who submitted your form by ID."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class V2CioRelationshipsItemIdentifiersV0(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")

class V2CioRelationshipsItemIdentifiersV1(PermissiveModel):
    email: str | None = None

class V2CioRelationshipsItemIdentifiersV2(PermissiveModel):
    cio_id: str | None = None

class V2CioRelationshipsItem(PermissiveModel):
    identifiers: V2CioRelationshipsItemIdentifiersV0 | V2CioRelationshipsItemIdentifiersV1 | V2CioRelationshipsItemIdentifiersV2 | None = None
    relationship_attributes: dict[str, Any] | None = Field(None, description="The attributes associated with a relationship. Passing null or an empty string removes the attribute from the relationship.\n")

class V2CioRelationships(RootModel[list[V2CioRelationshipsItem]]):
    pass

class ObjectAddRelationships(PermissiveModel):
    """Add relationships between an object and one or more people."""
    action: Literal["add_relationships"] = Field(..., description="This operation associates an object with one or more people.")
    cio_relationships: V2CioRelationships

class ObjectDeleteRelationships(PermissiveModel):
    """Delete relationships between an object and one or more people."""
    action: Literal["delete_relationships"] = Field(..., description="This operation deletes an object relationship from one or more people.")
    cio_relationships: V2CioRelationships

class ObjectIdentify(PermissiveModel):
    """The `action` determines the type of operation you want to perform with an object. If `identifiers.object_id` does not exist, we'll create a new object; if it exists, we'll update the object accordingly.
"""
    identifiers: ObjectIdentifyIdentifiersV0 | ObjectIdentifyIdentifiersV1 = Field(..., description="The identifiers for a custom object. When identifying a new object, you *must* use both the `object_type_id` and `object_id` (where `object_type_id` is an integer representing the type of object and the `object_id` is the individual identifier for the object).\n\nIf you're updating an existing object, you can use either the `object_type_id` and `object_id` or the `cio_object_id` (where `cio_object_id` is an immutable unique value that Customer.io sets for an object when you create it).\n")
    type_: Literal["object"] = Field(..., validation_alias="type", serialization_alias="type", description="The operation modifies a single object—non person data.")
    action: Literal["identify"] = Field(..., description="Indicates that the operation will `identify` the the item of the specified `type`.")
    attributes: ObjectAttributes | None = None
    cio_relationships: V2CioRelationships | None = None


# Rebuild models to resolve forward references (required for circular refs)
CioSubscriptionPreferences.model_rebuild()
DeliveryOperations.model_rebuild()
DeliveryOperationsAttributes.model_rebuild()
DeliveryOperationsIdentifiers.model_rebuild()
DeviceObject.model_rebuild()
DeviceObjectAttributes.model_rebuild()
DeviceObjectCommon.model_rebuild()
DeviceObjectCommonAttributes.model_rebuild()
EntityBodyDevice.model_rebuild()
EntityBodyIdentifiersV0.model_rebuild()
EntityBodyIdentifiersV1.model_rebuild()
EntityBodyIdentifiersV2.model_rebuild()
EntityBodyPrimaryV0.model_rebuild()
EntityBodyPrimaryV1.model_rebuild()
EntityBodyPrimaryV2.model_rebuild()
EntityBodySecondaryV0.model_rebuild()
EntityBodySecondaryV1.model_rebuild()
EntityBodySecondaryV2.model_rebuild()
IdentifyBodyCioRelationshipsRelationshipsItem.model_rebuild()
IdentifyBodyCioRelationshipsRelationshipsItemIdentifiersV0.model_rebuild()
IdentifyBodyCioRelationshipsRelationshipsItemIdentifiersV1.model_rebuild()
IdentifyPerson.model_rebuild()
IdentifyPersonAttributes.model_rebuild()
IdentifyPersonIdentifiersV0.model_rebuild()
IdentifyPersonIdentifiersV1.model_rebuild()
IdentifyPersonIdentifiersV2.model_rebuild()
IdentifyPersonV1Attributes.model_rebuild()
MergeBodyPrimaryV0.model_rebuild()
MergeBodyPrimaryV1.model_rebuild()
MergeBodyPrimaryV2.model_rebuild()
MergeBodySecondaryV0.model_rebuild()
MergeBodySecondaryV1.model_rebuild()
MergeBodySecondaryV2.model_rebuild()
ObjectAddRelationships.model_rebuild()
ObjectAttributes.model_rebuild()
ObjectCommon.model_rebuild()
ObjectCommonIdentifiersV0.model_rebuild()
ObjectCommonIdentifiersV1.model_rebuild()
ObjectCommonIdentify.model_rebuild()
ObjectCommonIdentifyIdentifiersV0.model_rebuild()
ObjectCommonIdentifyIdentifiersV1.model_rebuild()
ObjectDelete.model_rebuild()
ObjectDeleteRelationships.model_rebuild()
ObjectIdentifiers.model_rebuild()
ObjectIdentifiersIdentifiersV0.model_rebuild()
ObjectIdentifiersIdentifiersV1.model_rebuild()
ObjectIdentify.model_rebuild()
ObjectIdentifyAnonymous.model_rebuild()
ObjectIdentifyAnonymousCioRelationshipsItem.model_rebuild()
ObjectIdentifyAnonymousCioRelationshipsItemIdentifiers.model_rebuild()
ObjectIdentifyAnonymousIdentifiersV0.model_rebuild()
ObjectIdentifyAnonymousIdentifiersV1.model_rebuild()
ObjectIdentifyAnonymousV1CioRelationshipsItem.model_rebuild()
ObjectIdentifyAnonymousV1CioRelationshipsItemIdentifiers.model_rebuild()
ObjectIdentifyIdentifiersV0.model_rebuild()
ObjectIdentifyIdentifiersV1.model_rebuild()
ObjectRelationships.model_rebuild()
ObjectRelationshipsItem.model_rebuild()
ObjectRelationshipsItemIdentifiersV0.model_rebuild()
ObjectRelationshipsItemIdentifiersV1.model_rebuild()
PersonAddDevice.model_rebuild()
PersonAddDeviceDevice.model_rebuild()
PersonAddDeviceDeviceAttributes.model_rebuild()
PersonAddDeviceIdentifiersV0.model_rebuild()
PersonAddDeviceIdentifiersV1.model_rebuild()
PersonAddDeviceIdentifiersV2.model_rebuild()
PersonAddDeviceV1Device.model_rebuild()
PersonAddDeviceV1DeviceAttributes.model_rebuild()
PersonAddRelationships.model_rebuild()
PersonAddRelationshipsIdentifiersV0.model_rebuild()
PersonAddRelationshipsIdentifiersV1.model_rebuild()
PersonAddRelationshipsIdentifiersV2.model_rebuild()
PersonCommon.model_rebuild()
PersonCommonIdentifiersV0.model_rebuild()
PersonCommonIdentifiersV1.model_rebuild()
PersonCommonIdentifiersV2.model_rebuild()
PersonDelete.model_rebuild()
PersonDeleteDevice.model_rebuild()
PersonDeleteDeviceDevice.model_rebuild()
PersonDeleteDeviceIdentifiersV0.model_rebuild()
PersonDeleteDeviceIdentifiersV1.model_rebuild()
PersonDeleteDeviceIdentifiersV2.model_rebuild()
PersonDeleteDeviceV1Device.model_rebuild()
PersonDeleteIdentifiersV0.model_rebuild()
PersonDeleteIdentifiersV1.model_rebuild()
PersonDeleteIdentifiersV2.model_rebuild()
PersonDeleteRelationships.model_rebuild()
PersonDeleteRelationshipsIdentifiersV0.model_rebuild()
PersonDeleteRelationshipsIdentifiersV1.model_rebuild()
PersonDeleteRelationshipsIdentifiersV2.model_rebuild()
PersonEvent.model_rebuild()
PersonEventAttributes.model_rebuild()
PersonEventIdentifiersV0.model_rebuild()
PersonEventIdentifiersV1.model_rebuild()
PersonEventIdentifiersV2.model_rebuild()
PersonEventV1Attributes.model_rebuild()
PersonMerge.model_rebuild()
PersonMergePrimaryV0.model_rebuild()
PersonMergePrimaryV1.model_rebuild()
PersonMergePrimaryV2.model_rebuild()
PersonMergeSecondaryV0.model_rebuild()
PersonMergeSecondaryV1.model_rebuild()
PersonMergeSecondaryV2.model_rebuild()
PersonPage.model_rebuild()
PersonPageAttributes.model_rebuild()
PersonPageIdentifiersV0.model_rebuild()
PersonPageIdentifiersV1.model_rebuild()
PersonPageIdentifiersV2.model_rebuild()
PersonPageV1Attributes.model_rebuild()
PersonScreen.model_rebuild()
PersonScreenIdentifiersV0.model_rebuild()
PersonScreenIdentifiersV1.model_rebuild()
PersonScreenIdentifiersV2.model_rebuild()
PersonSuppress.model_rebuild()
PersonSuppressIdentifiersV0.model_rebuild()
PersonSuppressIdentifiersV1.model_rebuild()
PersonSuppressIdentifiersV2.model_rebuild()
PersonUnsuppress.model_rebuild()
PersonUnsuppressIdentifiersV0.model_rebuild()
PersonUnsuppressIdentifiersV1.model_rebuild()
PersonUnsuppressIdentifiersV2.model_rebuild()
RelationshipAttributes.model_rebuild()
SubmitFormBodyDataV0.model_rebuild()
SubmitFormBodyDataV1.model_rebuild()
V2CioRelationships.model_rebuild()
V2CioRelationshipsItem.model_rebuild()
V2CioRelationshipsItemIdentifiersV0.model_rebuild()
V2CioRelationshipsItemIdentifiersV1.model_rebuild()
V2CioRelationshipsItemIdentifiersV2.model_rebuild()

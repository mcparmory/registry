"""
Netlicensing MCP Server - Pydantic Models

Generated: 2026-04-14 18:26:21 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "CreateLicenseeRequest",
    "CreateLicenseRequest",
    "CreateLicenseTemplateRequest",
    "CreateProductModuleRequest",
    "CreateProductRequest",
    "CreateTokenRequest",
    "CreateTransactionRequest",
    "DeleteLicenseeRequest",
    "DeleteLicenseRequest",
    "DeleteLicenseTemplateRequest",
    "DeleteProductModuleRequest",
    "DeleteProductRequest",
    "DeleteTokenRequest",
    "GetLicenseeRequest",
    "GetLicenseRequest",
    "GetLicenseTemplateRequest",
    "GetPaymentMethodRequest",
    "GetProductModuleRequest",
    "GetTokenRequest",
    "GetTransactionRequest",
    "ProductNumberRequest",
    "TransferLicensesRequest",
    "UpdateLicenseeRequest",
    "UpdateLicenseRequest",
    "UpdateLicenseTemplateRequest",
    "UpdatePaymentMethodRequest",
    "UpdateProductModuleRequest",
    "UpdateProductRequest",
    "UpdateTransactionRequest",
    "ValidateLicenseeRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: create_product
class CreateProductRequestBody(StrictModel):
    active: bool = Field(default=..., description="Activation status of the product. When set to false, the product is disabled and prevents new licensee registrations and license issuance to existing licensees.")
    name: str = Field(default=..., description="The product name, which together with the version uniquely identifies the product for end customers.")
    version: str = Field(default=..., description="The product version, which together with the name uniquely identifies the product for end customers.")
    licensee_auto_create: bool | None = Field(default=None, validation_alias="licenseeAutoCreate", serialization_alias="licenseeAutoCreate", description="When enabled, non-existing licensees are automatically created upon their first license validation attempt.")
    description: str | None = Field(default=None, description="A descriptive text providing additional information about the product.")
    licensing_info: str | None = Field(default=None, validation_alias="licensingInfo", serialization_alias="licensingInfo", description="Licensing-related information or terms associated with the product.")
    vat_mode: Literal["GROSS", "NET"] | None = Field(default=None, validation_alias="vatMode", serialization_alias="vatMode", description="Tax calculation mode for the product. Choose GROSS for prices including tax or NET for prices excluding tax.")
class CreateProductRequest(StrictModel):
    """Creates a new product with licensing configuration. The product is identified by its name and version combination and can be immediately activated or disabled for new licensee registrations."""
    body: CreateProductRequestBody

# Operation: get_product
class ProductNumberRequestPath(StrictModel):
    product_number: str = Field(default=..., validation_alias="productNumber", serialization_alias="productNumber", description="The unique identifier for the product. This value must exactly match the product number in the system.")
class ProductNumberRequest(StrictModel):
    """Retrieve a specific product by its unique product number. Use this operation to fetch detailed information about a single product."""
    path: ProductNumberRequestPath

# Operation: update_product
class UpdateProductRequestPath(StrictModel):
    product_number: str = Field(default=..., validation_alias="productNumber", serialization_alias="productNumber", description="The unique identifier for the product to update.")
class UpdateProductRequestBody(StrictModel):
    active: bool | None = Field(default=None, description="Enable or disable the product. When disabled, new licensees cannot be registered and existing licensees cannot obtain new licenses.")
    name: str | None = Field(default=None, description="The product name, typically displayed to end customers alongside the version.")
    version: str | None = Field(default=None, description="The product version, used alongside the name to identify the product to end customers.")
    licensee_auto_create: bool | None = Field(default=None, validation_alias="licenseeAutoCreate", serialization_alias="licenseeAutoCreate", description="When enabled, licensees that do not exist will be automatically created during their first license validation attempt.")
    description: str | None = Field(default=None, description="A description of the product for internal or customer-facing documentation.")
    licensing_info: str | None = Field(default=None, validation_alias="licensingInfo", serialization_alias="licensingInfo", description="Licensing terms and conditions information associated with the product.")
    vat_mode: Literal["GROSS", "NET"] | None = Field(default=None, validation_alias="vatMode", serialization_alias="vatMode", description="The VAT calculation mode for the product: GROSS (price includes VAT) or NET (price excludes VAT).")
class UpdateProductRequest(StrictModel):
    """Update product properties such as name, version, licensing settings, and VAT configuration. Returns the updated product with all applied changes."""
    path: UpdateProductRequestPath
    body: UpdateProductRequestBody | None = None

# Operation: delete_product
class DeleteProductRequestPath(StrictModel):
    product_number: str = Field(default=..., validation_alias="productNumber", serialization_alias="productNumber", description="The unique identifier for the product to delete.")
class DeleteProductRequestQuery(StrictModel):
    force_cascade: bool | None = Field(default=None, validation_alias="forceCascade", serialization_alias="forceCascade", description="When enabled, forces deletion of the product and all its dependent objects. Use with caution as this operation cannot be undone.")
class DeleteProductRequest(StrictModel):
    """Permanently delete a product by its unique product number. Optionally cascade the deletion to remove all dependent objects."""
    path: DeleteProductRequestPath
    query: DeleteProductRequestQuery | None = None

# Operation: create_product_module
class CreateProductModuleRequestBody(StrictModel):
    product_number: str = Field(default=..., validation_alias="productNumber", serialization_alias="productNumber", description="Unique identifier for the Product Module within the Vendor's Product catalog. Can be assigned by the Vendor or auto-generated by NetLicensing. Becomes read-only once the first Licensee is created for this Product Module.")
    active: bool = Field(default=..., description="Activation status of the Product Module. When set to false, the module is disabled and Licensees cannot obtain new Licenses for it.")
    name: str = Field(default=..., description="Display name for the Product Module shown to end customers in the NetLicensing Shop.")
    licensing_model: str = Field(default=..., validation_alias="licensingModel", serialization_alias="licensingModel", description="The licensing model that governs how this Product Module's licenses are configured and validated. The selected model determines which License Templates can be used and validation behavior.")
    max_checkout_validity: int | None = Field(default=None, validation_alias="maxCheckoutValidity", serialization_alias="maxCheckoutValidity", description="Maximum number of days a License can remain checked out offline. Required when using the Floating licensing model.", json_schema_extra={'format': 'int32'})
    yellow_threshold: int | None = Field(default=None, validation_alias="yellowThreshold", serialization_alias="yellowThreshold", description="Remaining time volume threshold (in days) that triggers yellow status alerts. Required when using the Rental licensing model.", json_schema_extra={'format': 'int32'})
    red_threshold: int | None = Field(default=None, validation_alias="redThreshold", serialization_alias="redThreshold", description="Remaining time volume threshold (in days) that triggers red status alerts. Required when using the Rental licensing model.", json_schema_extra={'format': 'int32'})
    node_secret_mode: list[Literal["PREDEFINED", "CLIENT"]] | None = Field(default=None, validation_alias="nodeSecretMode", serialization_alias="nodeSecretMode", description="Secret Mode configuration for node-locked licensing. Required when using the Node-Locked licensing model. Specify as an array of mode values.")
    license_template: list[Literal["TIMEVOLUME", "FEATURE"]] | None = Field(default=None, validation_alias="licenseTemplate", serialization_alias="licenseTemplate", description="License Template configuration defining license types and rules. Required when using the Try & Buy licensing model. Specify as an array of template objects.")
class CreateProductModuleRequest(StrictModel):
    """Creates a new Product Module within a Product, establishing the licensing model and configuration for how licenses are managed and validated for end customers."""
    body: CreateProductModuleRequestBody

# Operation: get_product_module
class GetProductModuleRequestPath(StrictModel):
    product_module_number: str = Field(default=..., validation_alias="productModuleNumber", serialization_alias="productModuleNumber", description="The unique identifier for the Product Module, assigned by the Vendor or auto-generated by NetLicensing. This value becomes read-only once the first Licensee is created for the Product.")
class GetProductModuleRequest(StrictModel):
    """Retrieve a specific Product Module by its unique identifier. Returns the complete Product Module details for the given productModuleNumber."""
    path: GetProductModuleRequestPath

# Operation: update_product_module
class UpdateProductModuleRequestPath(StrictModel):
    product_module_number: str = Field(default=..., validation_alias="productModuleNumber", serialization_alias="productModuleNumber", description="Unique identifier for the Product Module within the Vendor's product catalog. This value becomes read-only once the first Licensee is created for the Product.")
class UpdateProductModuleRequestBody(StrictModel):
    active: bool | None = Field(default=None, description="Enable or disable the Product Module. When disabled, Licensees cannot obtain new Licenses for this module.")
    name: str | None = Field(default=None, description="Display name for the Product Module shown to end customers in NetLicensing Shop.")
    licensing_model: str | None = Field(default=None, validation_alias="licensingModel", serialization_alias="licensingModel", description="Licensing model that governs how this Product Module's licenses are configured and validated. The selected model determines which additional properties are required.")
    max_checkout_validity: int | None = Field(default=None, validation_alias="maxCheckoutValidity", serialization_alias="maxCheckoutValidity", description="Maximum number of days a license can remain checked out. Required when using the Floating licensing model.", json_schema_extra={'format': 'int32'})
    yellow_threshold: int | None = Field(default=None, validation_alias="yellowThreshold", serialization_alias="yellowThreshold", description="Remaining time volume threshold (in days) that triggers yellow status. Required when using the Rental licensing model.", json_schema_extra={'format': 'int32'})
    red_threshold: int | None = Field(default=None, validation_alias="redThreshold", serialization_alias="redThreshold", description="Remaining time volume threshold (in days) that triggers red status. Required when using the Rental licensing model.", json_schema_extra={'format': 'int32'})
    license_template: list[Literal["TIMEVOLUME", "FEATURE"]] | None = Field(default=None, validation_alias="licenseTemplate", serialization_alias="licenseTemplate", description="License Template configuration for this Product Module. Required when using the Try & Buy licensing model.")
    node_secret_mode: list[Literal["PREDEFINED", "CLIENT"]] | None = Field(default=None, validation_alias="nodeSecretMode", serialization_alias="nodeSecretMode", description="Secret Mode configuration for node-locked licensing. Required when using the Node-Locked licensing model.")
class UpdateProductModuleRequest(StrictModel):
    """Update properties of an existing Product Module. Modifies the specified Product Module configuration and returns the updated module details."""
    path: UpdateProductModuleRequestPath
    body: UpdateProductModuleRequestBody | None = None

# Operation: delete_product_module
class DeleteProductModuleRequestPath(StrictModel):
    product_module_number: str = Field(default=..., validation_alias="productModuleNumber", serialization_alias="productModuleNumber", description="The unique identifier for the Product Module within a Vendor's product catalog. This number must exactly match an existing Product Module.")
class DeleteProductModuleRequestQuery(StrictModel):
    force_cascade: bool | None = Field(default=None, validation_alias="forceCascade", serialization_alias="forceCascade", description="When enabled, forces deletion of the Product Module and all its child objects in the hierarchy. Use with caution as this operation cannot be undone.")
class DeleteProductModuleRequest(StrictModel):
    """Permanently delete a Product Module by its unique number. Optionally cascade the deletion to all descendant objects."""
    path: DeleteProductModuleRequestPath
    query: DeleteProductModuleRequestQuery | None = None

# Operation: create_license_template
class CreateLicenseTemplateRequestBody(StrictModel):
    product_module_number: str = Field(default=..., validation_alias="productModuleNumber", serialization_alias="productModuleNumber", description="The unique identifier of the Product Module under which this License Template will be created.")
    name: str = Field(default=..., description="A descriptive name for the License Template that identifies its purpose and licensing model.")
    active: bool = Field(default=..., description="Controls whether the License Template is active; when disabled, licensees cannot obtain new licenses from this template.")
    license_type: str = Field(default=..., validation_alias="licenseType", serialization_alias="licenseType", description="Specifies the licensing model for licenses created from this template. Choose from: FEATURE (feature-based licensing), TIMEVOLUME (time-limited volume licensing), FLOATING (concurrent user licensing), or QUANTITY (fixed quantity licensing).")
    time_volume_period: str | None = Field(default=None, validation_alias="timeVolumePeriod", serialization_alias="timeVolumePeriod", description="Required when licenseType is set to TIMEVOLUME; specifies the duration period for time-volume licenses (e.g., monthly, yearly).")
    automatic: bool | None = Field(default=None, description="When enabled, new licensees automatically receive one license from this template upon creation. Automatic licenses must have a price of zero.")
    hidden: bool | None = Field(default=None, description="When enabled, this License Template is hidden from the NetLicensing Shop and not offered for direct purchase by customers.")
    hide_licenses: bool | None = Field(default=None, validation_alias="hideLicenses", serialization_alias="hideLicenses", description="When enabled, licenses created from this template are hidden from end customers but still participate in license validation checks.")
    quota: str | None = Field(default=None, description="Required for quota-based licensing models; defines the maximum quota allocation for licenses created from this template.")
class CreateLicenseTemplateRequest(StrictModel):
    """Creates a new License Template for a specified Product Module, defining the licensing model and availability rules for licensees."""
    body: CreateLicenseTemplateRequestBody

# Operation: get_license_template
class GetLicenseTemplateRequestPath(StrictModel):
    license_template_number: str = Field(default=..., validation_alias="licenseTemplateNumber", serialization_alias="licenseTemplateNumber", description="The unique identifier for the License Template, assigned by the vendor during creation or auto-generated by NetLicensing. This value becomes read-only once the first License is created from this template.")
class GetLicenseTemplateRequest(StrictModel):
    """Retrieve a specific License Template by its unique identifier. This template defines the licensing model and terms for products from a vendor."""
    path: GetLicenseTemplateRequestPath

# Operation: update_license_template
class UpdateLicenseTemplateRequestPath(StrictModel):
    license_template_number: str = Field(default=..., validation_alias="licenseTemplateNumber", serialization_alias="licenseTemplateNumber", description="The unique identifier for the License Template within the Vendor's product portfolio. This value is immutable once the first License is created from this template.")
class UpdateLicenseTemplateRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A human-readable name for the License Template to identify it in the system.")
    active: bool | None = Field(default=None, description="Enable or disable the License Template. When disabled, new Licensees cannot obtain Licenses from this template, though existing Licenses remain valid.")
    license_type: str | None = Field(default=None, validation_alias="licenseType", serialization_alias="licenseType", description="Specifies the licensing model for Licenses created from this template. Choose from: FEATURE (feature-based licensing), TIMEVOLUME (time and volume-based), FLOATING (concurrent usage), or QUANTITY (fixed quantity).")
    time_volume_period: str | None = Field(default=None, validation_alias="timeVolumePeriod", serialization_alias="timeVolumePeriod", description="Required for TIMEVOLUME License Type. Defines the time period over which volume is measured (e.g., monthly, yearly).")
    automatic: bool | None = Field(default=None, description="When enabled, each newly created Licensee automatically receives one License from this template at no cost. Automatic Licenses must have a price of zero.")
    hidden: bool | None = Field(default=None, description="When enabled, this License Template is excluded from the NetLicensing Shop and is not available for direct purchase by customers.")
    hide_licenses: bool | None = Field(default=None, validation_alias="hideLicenses", serialization_alias="hideLicenses", description="When enabled, Licenses created from this template are hidden from end-customer visibility but still participate in license validation checks.")
    quota: str | None = Field(default=None, description="Required when using the Quota License Model. Specifies the quota limit for Licenses created from this template.")
class UpdateLicenseTemplateRequest(StrictModel):
    """Update properties of an existing License Template. Changes apply to the template itself and affect how new Licenses are created from it."""
    path: UpdateLicenseTemplateRequestPath
    body: UpdateLicenseTemplateRequestBody | None = None

# Operation: delete_license_template
class DeleteLicenseTemplateRequestPath(StrictModel):
    license_template_number: str = Field(default=..., validation_alias="licenseTemplateNumber", serialization_alias="licenseTemplateNumber", description="The unique identifier for the License Template to delete, assigned across all Products within a Vendor.")
class DeleteLicenseTemplateRequestQuery(StrictModel):
    force_cascade: bool | None = Field(default=None, validation_alias="forceCascade", serialization_alias="forceCascade", description="When enabled, forces deletion of the License Template and all its descendant objects. Use with caution as this operation cannot be undone.")
class DeleteLicenseTemplateRequest(StrictModel):
    """Permanently delete a License Template by its unique number. Optionally cascade the deletion to remove all dependent objects."""
    path: DeleteLicenseTemplateRequestPath
    query: DeleteLicenseTemplateRequestQuery | None = None

# Operation: create_licensee
class CreateLicenseeRequestBody(StrictModel):
    product_number: str = Field(default=..., validation_alias="productNumber", serialization_alias="productNumber", description="The product number to assign to the new Licensee. This identifier links the licensee to a specific product.")
    name: str | None = Field(default=None, description="The display name for the Licensee. Used to identify the licensee in the system.")
    active: bool = Field(default=..., description="Determines whether the Licensee is active. When set to false, the Licensee is disabled and cannot obtain new licenses or participate in validation.")
    marked_for_transfer: bool | None = Field(default=None, validation_alias="markedForTransfer", serialization_alias="markedForTransfer", description="Indicates whether this Licensee is marked for transfer to another entity. Used to flag licensees pending transfer operations.")
class CreateLicenseeRequest(StrictModel):
    """Creates a new Licensee entity that can obtain licenses and be validated. The licensee's active status determines whether it can acquire new licenses and participate in validation processes."""
    body: CreateLicenseeRequestBody

# Operation: get_licensee
class GetLicenseeRequestPath(StrictModel):
    licensee_number: str = Field(default=..., validation_alias="licenseeNumber", serialization_alias="licenseeNumber", description="The unique identifier assigned to the licensee within the vendor's product ecosystem. This value is either vendor-assigned during licensee creation or auto-generated by NetLicensing, and becomes read-only once the first license is issued.")
class GetLicenseeRequest(StrictModel):
    """Retrieve a specific licensee by their unique identifier. Returns complete licensee details including licensing status and associated metadata."""
    path: GetLicenseeRequestPath

# Operation: update_licensee
class UpdateLicenseeRequestPath(StrictModel):
    licensee_number: str = Field(default=..., validation_alias="licenseeNumber", serialization_alias="licenseeNumber", description="The unique identifier for the Licensee within the Vendor's product ecosystem. This value is assigned by the Vendor during creation or auto-generated by NetLicensing, and becomes read-only once the first License is created for this Licensee.")
class UpdateLicenseeRequestBody(StrictModel):
    active: bool | None = Field(default=None, description="Enable or disable the Licensee. When set to false, the Licensee cannot obtain new Licenses and validation checks are disabled.")
    name: str | None = Field(default=None, description="Display name or label for the Licensee.")
    marked_for_transfer: bool | None = Field(default=None, validation_alias="markedForTransfer", serialization_alias="markedForTransfer", description="Flag indicating whether this Licensee is eligible for transfer to another Vendor or account.")
class UpdateLicenseeRequest(StrictModel):
    """Update properties of an existing Licensee. Modify activation status, name, or transfer eligibility and receive the updated Licensee object."""
    path: UpdateLicenseeRequestPath
    body: UpdateLicenseeRequestBody | None = None

# Operation: delete_licensee
class DeleteLicenseeRequestPath(StrictModel):
    licensee_number: str = Field(default=..., validation_alias="licenseeNumber", serialization_alias="licenseeNumber", description="The unique identifier for the licensee to delete. This number is unique across all products for a given vendor.")
class DeleteLicenseeRequestQuery(StrictModel):
    force_cascade: bool | None = Field(default=None, validation_alias="forceCascade", serialization_alias="forceCascade", description="When enabled, forces deletion of the licensee and all its dependent objects and descendants. Use with caution as this operation cannot be undone.")
class DeleteLicenseeRequest(StrictModel):
    """Permanently delete a licensee by its unique number. Optionally cascade the deletion to remove all dependent objects and descendants."""
    path: DeleteLicenseeRequestPath
    query: DeleteLicenseeRequestQuery | None = None

# Operation: validate_licensee
class ValidateLicenseeRequestPath(StrictModel):
    licensee_number: str = Field(default=..., validation_alias="licenseeNumber", serialization_alias="licenseeNumber", description="The unique identifier for the licensee to validate. Maximum length is 1000 characters.")
class ValidateLicenseeRequestBody(StrictModel):
    licensee_name: str | None = Field(default=None, validation_alias="licenseeName", serialization_alias="licenseeName", description="Human-readable name for the licensee. Used as a custom property if the licensee is auto-created during validation.")
    product_number: str | None = Field(default=None, validation_alias="productNumber", serialization_alias="productNumber", description="The product identifier associated with the licensee. Required when licensee auto-creation is enabled to specify which product the new licensee should be added to.")
    product_module_number: str | None = Field(default=None, validation_alias="productModuleNumber", serialization_alias="productModuleNumber", description="The product module identifier for node-locked licensing models. Specifies which module within the product is being validated.")
    node_secret: str | None = Field(default=None, validation_alias="nodeSecret", serialization_alias="nodeSecret", description="A unique secret value for node-locked licensing models. Used to identify and validate the specific node.")
    session_id: str | None = Field(default=None, validation_alias="sessionId", serialization_alias="sessionId", description="A unique session identifier for floating licensing models. Used to track and manage the session within the available pool.")
    action: Literal["checkOut", "checkIn"] | None = Field(default=None, description="The session action for floating licensing models. Use 'checkOut' to allocate a session from the pool or 'checkIn' to return a session to the pool.")
class ValidateLicenseeRequest(StrictModel):
    """Validates the active licenses for a specific licensee, supporting both node-locked and floating licensing models. Use this to verify license status and manage session allocation for floating licenses."""
    path: ValidateLicenseeRequestPath
    body: ValidateLicenseeRequestBody | None = None

# Operation: transfer_licenses_between_licensees
class TransferLicensesRequestPath(StrictModel):
    licensee_number: str = Field(default=..., validation_alias="licenseeNumber", serialization_alias="licenseeNumber", description="The destination licensee number that will receive the transferred licenses. Must be a valid licensee identifier with a maximum length of 1000 characters.")
class TransferLicensesRequestBody(StrictModel):
    source_licensee_number: str = Field(default=..., validation_alias="sourceLicenseeNumber", serialization_alias="sourceLicenseeNumber", description="The source licensee number from which licenses will be transferred. Must be a valid licensee identifier with a maximum length of 1000 characters.")
class TransferLicensesRequest(StrictModel):
    """Transfer licenses from a source licensee to a destination licensee. This operation moves all or specified licenses between two licensee accounts."""
    path: TransferLicensesRequestPath
    body: TransferLicensesRequestBody

# Operation: create_license
class CreateLicenseRequestBody(StrictModel):
    licensee_number: str = Field(default=..., validation_alias="licenseeNumber", serialization_alias="licenseeNumber", description="The unique identifier of the licensee to whom this license will be assigned.")
    license_template_number: str = Field(default=..., validation_alias="licenseTemplateNumber", serialization_alias="licenseTemplateNumber", description="The unique identifier of the license template that defines the license type, model, and default properties.")
    active: bool = Field(default=..., description="Whether the license is active and available for use immediately upon creation.")
    name: str | None = Field(default=None, description="A display name for the licensed item. If not provided, the name from the license template will be used automatically.")
    parentfeature: str | None = Field(default=None, description="Required when the license template uses the 'TIMEVOLUME' type or 'RENTAL' licensing model. Identifies the parent feature or product this license applies to.")
    time_volume_period: str | None = Field(default=None, validation_alias="timeVolumePeriod", serialization_alias="timeVolumePeriod", description="The time period unit for time-volume based licenses (e.g., 'MONTH', 'YEAR'). Only applicable for 'TIMEVOLUME' license type.")
    start_date: str | None = Field(default=None, validation_alias="startDate", serialization_alias="startDate", description="The date and time when the license becomes effective. Required for 'TIMEVOLUME' license type. Must be provided in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    hidden: bool | None = Field(default=None, description="If set to true, this license will not be displayed in the NetLicensing Shop as a purchased license. If not specified, the value from the license template will be used.")
    used_quantity: str | None = Field(default=None, validation_alias="usedQuantity", serialization_alias="usedQuantity", description="The quantity of the licensed resource already consumed. Required for 'Pay-per-Use' licensing model to track usage.")
class CreateLicenseRequest(StrictModel):
    """Creates a new license by associating a licensee with a license template. The license inherits default properties from the template unless explicitly overridden."""
    body: CreateLicenseRequestBody

# Operation: get_license
class GetLicenseRequestPath(StrictModel):
    license_number: str = Field(default=..., validation_alias="licenseNumber", serialization_alias="licenseNumber", description="The unique license identifier assigned by the vendor or auto-generated by NetLicensing. This value is immutable after the associated creation transaction is closed.")
class GetLicenseRequest(StrictModel):
    """Retrieve a specific license by its unique identifier. Returns complete license details including status, product information, and licensee data."""
    path: GetLicenseRequestPath

# Operation: update_license
class UpdateLicenseRequestPath(StrictModel):
    license_number: str = Field(default=..., validation_alias="licenseNumber", serialization_alias="licenseNumber", description="The unique identifier for the license to update. This number is assigned by the vendor or auto-generated by NetLicensing and cannot be changed after the creation transaction is closed.")
class UpdateLicenseRequestBody(StrictModel):
    active: bool | None = Field(default=None, description="Enable or disable the license. When disabled, the license becomes inactive.")
    name: str | None = Field(default=None, description="A human-readable name for the licensed item. If not provided during update, the existing name from the License Template is retained.")
    start_date: str | None = Field(default=None, validation_alias="startDate", serialization_alias="startDate", description="The start date and time for the license validity period. Required for TIMEVOLUME license types. Must be provided in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    parentfeature: str | None = Field(default=None, description="The parent feature that this license is associated with or depends on.")
    time_volume_period: str | None = Field(default=None, validation_alias="timeVolumePeriod", serialization_alias="timeVolumePeriod", description="The time period duration for TIMEVOLUME license types (e.g., monthly, yearly, or custom interval).")
    hidden: bool | None = Field(default=None, description="When set to true, this license will not be displayed in the NetLicensing Shop as a purchased license. If not specified, the setting from the License Template is used.")
    used_quantity: str | None = Field(default=None, validation_alias="usedQuantity", serialization_alias="usedQuantity", description="The quantity of the licensed resource that has been consumed or used. Required and must be tracked for Pay-per-Use license models.")
class UpdateLicenseRequest(StrictModel):
    """Update an existing license by its unique license number. Modify license properties such as activation status, name, validity period, and usage tracking."""
    path: UpdateLicenseRequestPath
    body: UpdateLicenseRequestBody | None = None

# Operation: delete_license
class DeleteLicenseRequestPath(StrictModel):
    license_number: str = Field(default=..., validation_alias="licenseNumber", serialization_alias="licenseNumber", description="The unique license identifier assigned by the vendor or generated by NetLicensing. This value is immutable after the associated creation transaction is closed.")
class DeleteLicenseRequest(StrictModel):
    """Permanently delete a license by its unique identifier. Once deleted, the license cannot be recovered."""
    path: DeleteLicenseRequestPath

# Operation: create_transaction
class CreateTransactionRequestBody(StrictModel):
    licensee_number: str | None = Field(default=None, validation_alias="licenseeNumber", serialization_alias="licenseeNumber", description="Optional identifier for the licensee associated with this transaction.")
    active: bool = Field(default=..., description="Activation status of the transaction. Must always be set to true when creating a transaction.")
    status: Literal["CANCELLED", "CLOSED", "PENDING"] = Field(default=..., description="The current state of the transaction. Must be one of: PENDING (awaiting processing), CLOSED (completed), or CANCELLED (voided).")
    source: Literal["SHOP"] = Field(default=..., description="The origin system for this transaction. Must be set to SHOP, indicating this is a point-of-sale transaction for internal use.")
    payment_method: str | None = Field(default=None, validation_alias="paymentMethod", serialization_alias="paymentMethod", description="Optional payment method used for this transaction (e.g., credit card, cash, digital wallet).")
class CreateTransactionRequest(StrictModel):
    """Creates a new transaction in the system. Transactions are always initialized in an active state and require a status and source to be specified."""
    body: CreateTransactionRequestBody

# Operation: get_transaction
class GetTransactionRequestPath(StrictModel):
    transaction_number: str = Field(default=..., validation_alias="transactionNumber", serialization_alias="transactionNumber", description="The unique transaction identifier assigned by the vendor. This number is globally unique across all products within the vendor's system and is used to retrieve the specific transaction record.")
class GetTransactionRequest(StrictModel):
    """Retrieve a specific transaction by its unique identifier. Returns complete transaction details including all associated metadata and status information."""
    path: GetTransactionRequestPath

# Operation: update_transaction
class UpdateTransactionRequestPath(StrictModel):
    transaction_number: str = Field(default=..., validation_alias="transactionNumber", serialization_alias="transactionNumber", description="The unique identifier for the transaction to update. This number is unique across all products for a given vendor.")
class UpdateTransactionRequestBody(StrictModel):
    active: bool | None = Field(default=None, description="Flag indicating whether the transaction is active. This field should always be set to true for transactions.")
    status: Literal["CANCELLED", "CLOSED", "PENDING"] | None = Field(default=None, description="The current state of the transaction. Valid states are: PENDING (awaiting processing), CLOSED (completed), or CANCELLED (voided).")
    source: Literal["SHOP"] | None = Field(default=None, description="The origin system for the transaction. Currently only SHOP is supported; AUTO transactions are reserved for internal system use only.")
    payment_method: str | None = Field(default=None, validation_alias="paymentMethod", serialization_alias="paymentMethod", description="The payment method used for the transaction (e.g., credit card, debit card, digital wallet).")
class UpdateTransactionRequest(StrictModel):
    """Update specific properties of an existing transaction identified by its transaction number. Returns the updated transaction with all changes applied."""
    path: UpdateTransactionRequestPath
    body: UpdateTransactionRequestBody | None = None

# Operation: create_token
class CreateTokenRequestBody(StrictModel):
    token_type: Literal["DEFAULT", "SHOP", "APIKEY"] = Field(default=..., validation_alias="tokenType", serialization_alias="tokenType", description="The category of token to generate. Choose DEFAULT for licensee login actions, SHOP for customer checkout flows, or APIKEY for programmatic API access.")
    api_key_role: Literal["ROLE_APIKEY_LICENSEE", "ROLE_APIKEY_ANALYTICS", "ROLE_APIKEY_OPERATION", "ROLE_APIKEY_MAINTENANCE", "ROLE_APIKEY_ADMIN"] | None = Field(default=None, validation_alias="apiKeyRole", serialization_alias="apiKeyRole", description="The permission level for APIKEY tokens only. Defaults to ROLE_APIKEY_LICENSEE if not specified. Select from licensee, analytics, operation, maintenance, or admin roles.")
    type_: Literal["ACTION"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The token behavior for DEFAULT tokens only. Currently supports ACTION type for performing specific licensee login operations.")
    action: Literal["licenseeLogin"] | None = Field(default=None, description="The specific operation for DEFAULT tokens with type=ACTION only. Currently supports licenseeLogin action.")
    licensee_number: str | None = Field(default=None, validation_alias="licenseeNumber", serialization_alias="licenseeNumber", description="The licensee identifier required for SHOP tokens or DEFAULT tokens with type=ACTION. Identifies which licensee owns or is associated with the token.")
    private_key: str | None = Field(default=None, validation_alias="privateKey", serialization_alias="privateKey", description="The private key for APIKEY tokens only, used for token validation. Must be provided as a single line without spaces.")
    product_number: str | None = Field(default=None, validation_alias="productNumber", serialization_alias="productNumber", description="The product identifier required for SHOP tokens. Specifies which product the customer can purchase through the generated shop token.")
    license_template_number: str | None = Field(default=None, validation_alias="licenseTemplateNumber", serialization_alias="licenseTemplateNumber", description="The license template identifier for SHOP tokens only. Determines the licensing terms applied to purchases made with this token.")
    predefined_shopping_item: str | None = Field(default=None, validation_alias="predefinedShoppingItem", serialization_alias="predefinedShoppingItem", description="The shopping item name for SHOP tokens only. Displayed to the customer during the checkout process.")
    success_url_title: str | None = Field(default=None, validation_alias="successURLTitle", serialization_alias="successURLTitle", description="The link title for SHOP tokens only, displayed to the customer after successful checkout completion.")
    cancel_url_title: str | None = Field(default=None, validation_alias="cancelURLTitle", serialization_alias="cancelURLTitle", description="The link title for SHOP tokens only, displayed to the customer if they cancel the checkout process.")
class CreateTokenRequest(StrictModel):
    """Generate authentication or shop tokens for different use cases. The token type determines which additional parameters are required: APIKEY tokens for programmatic access, SHOP tokens for customer checkout flows, or DEFAULT tokens for licensee login actions."""
    body: CreateTokenRequestBody

# Operation: get_token
class GetTokenRequestPath(StrictModel):
    token_number: str = Field(default=..., validation_alias="tokenNumber", serialization_alias="tokenNumber", description="The unique identifier of the token to retrieve, provided as a string value.")
class GetTokenRequest(StrictModel):
    """Retrieve a specific token by its token number. Use this operation to fetch details about an individual token in the system."""
    path: GetTokenRequestPath

# Operation: delete_token
class DeleteTokenRequestPath(StrictModel):
    token_number: str = Field(default=..., validation_alias="tokenNumber", serialization_alias="tokenNumber", description="The unique identifier of the token to delete, provided as a string.")
class DeleteTokenRequest(StrictModel):
    """Permanently delete a token by its number. This operation removes the token from the system and cannot be undone."""
    path: DeleteTokenRequestPath

# Operation: get_payment_method
class GetPaymentMethodRequestPath(StrictModel):
    payment_method_number: str = Field(default=..., validation_alias="paymentMethodNumber", serialization_alias="paymentMethodNumber", description="The unique identifier for the payment method to retrieve.")
class GetPaymentMethodRequest(StrictModel):
    """Retrieve detailed information about a specific payment method using its unique payment method number."""
    path: GetPaymentMethodRequestPath

# Operation: update_payment_method
class UpdatePaymentMethodRequestPath(StrictModel):
    payment_method_number: str = Field(default=..., validation_alias="paymentMethodNumber", serialization_alias="paymentMethodNumber", description="The unique identifier of the payment method to update.")
class UpdatePaymentMethodRequestBody(StrictModel):
    active: bool | None = Field(default=None, description="Set to false to disable the payment method, or true to enable it. If not provided, the current active status is preserved.")
    paypal_subject: str | None = Field(default=None, validation_alias="paypal.subject", serialization_alias="paypal.subject", description="The email address associated with the PayPal account. Required only when updating PayPal-based payment methods.")
class UpdatePaymentMethodRequest(StrictModel):
    """Update properties of an existing payment method, such as enabling/disabling it or modifying PayPal account details. Returns the updated payment method."""
    path: UpdatePaymentMethodRequestPath
    body: UpdatePaymentMethodRequestBody | None = None

# ============================================================================
# Component Models
# ============================================================================

class Licensee(PermissiveModel):
    number: str | None = Field(None, description="Unique number (across all Products of a Vendor) that identifies the Licensee. Vendor can assign this number when creating a Licensee or let NetLicensing generate one. Read-only after creation of the first License for the Licensee.")
    active: bool | None = Field(None, description="If set to 'false', the Licensee is disabled. Licensee can not obtain new Licenses, and validation is disabled.")

class Product(PermissiveModel):
    number: str | None = Field(None, description="Unique number that identifies the Product. Vendor can assign this number when creating a Product or let NetLicensing generate one. Read-only after creation of the first Licensee for the Product.")
    active: bool | None = Field(None, description="If set to 'false', the Product is disabled. No new Licensees can be registered for the Product, existing Licensees can not obtain new Licenses")
    name: str | None = Field(None, description="Product name. Together with the version identifies the Product for the end customer")
    version: str | None = Field(None, description="Product version. Convenience parameter, additional to the Product name.")
    licensee_auto_create: bool | None = Field(None, validation_alias="licenseeAutoCreate", serialization_alias="licenseeAutoCreate", description="If set to 'true', non-existing Licensees will be created at first validation attempt.")


# Rebuild models to resolve forward references (required for circular refs)
Licensee.model_rebuild()
Product.model_rebuild()

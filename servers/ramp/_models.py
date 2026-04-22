"""
Ramp Developer Api MCP Server - Pydantic Models

Generated: 2026-04-22 21:31:11 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "DeleteAccountingVendorResourceRequest",
    "DeleteBillResourceRequest",
    "DeleteCustomFieldOptionResourceRequest",
    "DeleteCustomFieldResourceRequest",
    "DeleteDevApiCustomRowRequest",
    "DeleteDevApiDeleteMatrixRowRequest",
    "DeleteGlAccountResourceRequest",
    "DeleteInventoryItemFieldOptionResourceRequest",
    "DeleteItemReceiptSingleResourceRequest",
    "DeleteOutboundWebhookSubscriptionDetailResourceRequest",
    "DeletePurchaseOrderLineItemSingleResourceRequest",
    "DeleteReceiptIntegrationOptedOutEmailsDeleteResourceRequest",
    "DeleteSpendAllocationDeleteUsersRequest",
    "DeleteTaxCodeFieldOptionResourceRequest",
    "DeleteTaxRateDetailResourceRequest",
    "DeleteVendorResourceRequest",
    "GetAccountingConnectionDetailResourceRequest",
    "GetAccountingVendorListResourceRequest",
    "GetAccountingVendorResourceRequest",
    "GetAllVendorCreditsListRequest",
    "GetAuditLogEventsListResourceRequest",
    "GetBankAccountListWithPaginationRequest",
    "GetBankAccountResourceRequest",
    "GetBillListWithPaginationRequest",
    "GetBillResourceRequest",
    "GetCardDeferredTaskResourceRequest",
    "GetCardListWithPaginationRequest",
    "GetCardResourceRequest",
    "GetCardVaultResourceRequest",
    "GetCashbackListWithPaginationRequest",
    "GetCashbackResourceRequest",
    "GetCustomFieldListResourceRequest",
    "GetCustomFieldOptionListResourceRequest",
    "GetCustomFieldOptionResourceRequest",
    "GetCustomFieldResourceRequest",
    "GetDepartmentListWithPaginationRequest",
    "GetDepartmentResourceRequest",
    "GetDevApiCustomRowRequest",
    "GetDevApiCustomTableColumnRequest",
    "GetDevApiNativeRowRequest",
    "GetDevApiNativeTableColumnRequest",
    "GetDraftBillListWithPaginationRequest",
    "GetDraftBillResourceRequest",
    "GetEntityListWithPaginationRequest",
    "GetEntityResourceRequest",
    "GetGlAccountListResourceRequest",
    "GetGlAccountResourceRequest",
    "GetInventoryItemFieldOptionsListResourceRequest",
    "GetItemReceiptSingleResourceRequest",
    "GetItemReceiptsResourceRequest",
    "GetLocationListResourceRequest",
    "GetLocationSingleResourceRequest",
    "GetMemoListWithPaginationRequest",
    "GetMemoSingleResourceRequest",
    "GetMerchantListWithPaginationRequest",
    "GetOutboundWebhookSubscriptionDetailResourceRequest",
    "GetPurchaseOrderSingleResourceRequest",
    "GetPurchaseOrdersResourceRequest",
    "GetReceiptIntegrationOptedOutEmailsListResourceRequest",
    "GetReceiptListRequest",
    "GetReceiptSingleResourceRequest",
    "GetReimbursementListWithPaginationRequest",
    "GetReimbursementResourceRequest",
    "GetSpendLimitDeferredTaskStatusRequest",
    "GetSpendLimitListWithPaginationRequest",
    "GetSpendLimitResourceRequest",
    "GetSpendProgramResourceRequest",
    "GetSpendProgramSingleResourceRequest",
    "GetStatementListWithPaginationRequest",
    "GetStatementResourceRequest",
    "GetTaxCodeFieldOptionsListResourceRequest",
    "GetTaxCodeRatesListResourceRequest",
    "GetTransactionCanonicalResourceRequest",
    "GetTransactionsCanonicalListWithPaginationRequest",
    "GetTransferListWithPaginationRequest",
    "GetTransferResourceRequest",
    "GetTripListResourceRequest",
    "GetTripSingleResourceRequest",
    "GetUserDeferredTaskResourceRequest",
    "GetUserListWithPaginationRequest",
    "GetUserResourceRequest",
    "GetVendorBankAccountListResourceRequest",
    "GetVendorBankAccountResourceRequest",
    "GetVendorContactListResourceRequest",
    "GetVendorContactResourceRequest",
    "GetVendorCreditDetailRequest",
    "GetVendorCreditsListRequest",
    "GetVendorListResourceRequest",
    "GetVendorResourceRequest",
    "PatchAccountingConnectionDetailResourceRequest",
    "PatchAccountingVendorResourceRequest",
    "PatchBillResourceRequest",
    "PatchCardResourceRequest",
    "PatchCustomFieldOptionResourceRequest",
    "PatchCustomFieldResourceRequest",
    "PatchDepartmentResourceRequest",
    "PatchDevApiChangeCustomRowExternalKeyRequest",
    "PatchDevApiRenameMatrixColumnRequest",
    "PatchDraftBillResourceRequest",
    "PatchGlAccountResourceRequest",
    "PatchInventoryItemFieldListResourceRequest",
    "PatchInventoryItemFieldOptionResourceRequest",
    "PatchLocationSingleResourceRequest",
    "PatchPurchaseOrderLineItemSingleResourceRequest",
    "PatchPurchaseOrderSingleResourceRequest",
    "PatchSpendLimitResourceRequest",
    "PatchTaxCodeFieldOptionResourceRequest",
    "PatchTaxCodeFieldResourceRequest",
    "PatchTaxRateDetailResourceRequest",
    "PatchUserDeactivationResourceRequest",
    "PatchUserReactivationResourceRequest",
    "PatchUserResourceRequest",
    "PatchVendorResourceRequest",
    "PostAccountingConnectionResourceRequest",
    "PostAccountingVendorListResourceRequest",
    "PostApplicationResourceRequest",
    "PostBillAttachmentUploadResourceRequest",
    "PostBillListWithPaginationRequest",
    "PostCardSuspensionResourceRequest",
    "PostCardTerminationResourceRequest",
    "PostCardUnsuspensionResourceRequest",
    "PostCardVaultCreationRequest",
    "PostCustomFieldListResourceRequest",
    "PostCustomFieldOptionListResourceRequest",
    "PostDepartmentListWithPaginationRequest",
    "PostDevApiAddMatrixResultColumnRequest",
    "PostDevApiAppendCustomRowCellsRequest",
    "PostDevApiAppendNativeRowCellsRequest",
    "PostDevApiMatrixAppendCellsRequest",
    "PostDevApiMatrixListRowsRequest",
    "PostDevApiMatrixRemoveCellsRequest",
    "PostDevApiMatrixTablesRequest",
    "PostDevApiRemoveCustomRowCellsRequest",
    "PostDevApiRemoveNativeRowCellsRequest",
    "PostDevApiRenameMatrixTableRequest",
    "PostDraftBillAttachmentUploadResourceRequest",
    "PostDraftBillListWithPaginationRequest",
    "PostGlAccountListResourceRequest",
    "PostInventoryItemFieldListResourceRequest",
    "PostInventoryItemFieldOptionsListResourceRequest",
    "PostItemReceiptsResourceRequest",
    "PostLocationListResourceRequest",
    "PostMemoCreateSingleResourceRequest",
    "PostMileageReimbursementResourceRequest",
    "PostPhysicalCardRequest",
    "PostPurchaseOrderArchiveResourceRequest",
    "PostPurchaseOrderLineItemsResourceRequest",
    "PostPurchaseOrdersResourceRequest",
    "PostRampEmbeddedCardResourceRequest",
    "PostReactivateConnectionResourceRequest",
    "PostReadyToSyncResourceRequest",
    "PostReceiptUploadRequest",
    "PostReimbursementReceiptUploadRequest",
    "PostSpendLimitCreationRequest",
    "PostSpendLimitSuspensionResourceRequest",
    "PostSpendLimitTerminationResourceRequest",
    "PostSpendLimitUnsuspensionResourceRequest",
    "PostSpendProgramResourceRequest",
    "PostSyncListResourceRequest",
    "PostTaxCodeFieldOptionsListResourceRequest",
    "PostTaxCodeFieldResourceRequest",
    "PostTaxCodeRatesListResourceRequest",
    "PostUserCreationDeferredTaskRequest",
    "PostVendorAgreementListResourceRequest",
    "PostVendorBankAccountArchiveResourceRequest",
    "PostVendorBankAccountUpdateResourceRequest",
    "PostVendorListResourceRequest",
    "PostVirtualCardRequest",
    "PutCustomFieldOptionResourceRequest",
    "PutDevApiCustomRowRequest",
    "PutDevApiMatrixPutRowsRequest",
    "PutDevApiNativeRowRequest",
    "PutSpendAllocationAddUsersRequest",
    "PutSpendLimitResourceRequest",
    "AccountingVendor",
    "ApiAccountingFailedSyncRequestBody",
    "ApiAccountingSuccessfulSyncRequestBody",
    "ApiApplicationPersonParamsRequestBody",
    "ApiCreateAccountingFieldParamsRequestBody",
    "ApiCreateBankAccountPaymentParamsRequestBody",
    "ApiCreateBillInventoryLineItemParamsRequestBody",
    "ApiCreateBillLineItemParamsRequestBody",
    "ApiCreateBillVendorPaymentParamsRequestBody",
    "ApiCreateCardBillPaymentParamsRequestBody",
    "ApiCreateManualBillPaymentParamsRequestBody",
    "ApiItemReceiptLineItemCreateParamsRequestBody",
    "ApiPurchaseOrderLineItemCreateParamsRequestBody",
    "CustomRowColumnContentsByColumnNameRequestBody",
    "CustomRowExternalKeyRequestBody",
    "DeveloperApiMatrixColumnFilterRequestBody",
    "DeveloperApiMatrixInputColumnDefRequestBody",
    "DeveloperApiMatrixResultColumnDefRequestBody",
    "FieldOption",
    "GlAccount",
    "InventoryItemOption",
    "MatrixRowInputByNameRequestBody",
    "NativeRowColumnContentsByColumnNameRequestBody",
    "PatchAccountingConnectionDetailResourceBodySettings",
    "PatchCardResourceBodySpendingRestrictions",
    "PatchSpendLimitResourceBodyPermittedSpendTypes",
    "PatchSpendLimitResourceBodySpendingRestrictions",
    "PatchVendorResourceBodyAddress",
    "PostAccountingConnectionResourceBodySettings",
    "PostApplicationResourceBodyApplicant",
    "PostApplicationResourceBodyBusiness",
    "PostApplicationResourceBodyControllingOfficer",
    "PostApplicationResourceBodyFinancialDetails",
    "PostApplicationResourceBodyOauthAuthorizeParams",
    "PostCardVaultCreationBodySpendingRestrictions",
    "PostDevApiAddMatrixResultColumnBodyNativeTable",
    "PostPhysicalCardBodyFulfillment",
    "PostPhysicalCardBodySpendingRestrictions",
    "PostSpendLimitCreationBodyPermittedSpendTypes",
    "PostSpendLimitCreationBodySpendingRestrictions",
    "PostSpendProgramResourceBodyIssuanceRules",
    "PostSpendProgramResourceBodyPermittedSpendTypes",
    "PostSpendProgramResourceBodySpendingRestrictions",
    "PostVendorAgreementListResourceBodyAgreementCustomRecords",
    "PostVendorAgreementListResourceBodyEndDateRange",
    "PostVendorAgreementListResourceBodyLastDateToTerminateRange",
    "PostVendorAgreementListResourceBodyStartDateRange",
    "PostVendorBankAccountUpdateResourceBodyAchDetails",
    "PostVendorBankAccountUpdateResourceBodyWireDetails",
    "PostVendorListResourceBodyAddress",
    "PostVendorListResourceBodyBusinessVendorContacts",
    "PostVirtualCardBodySpendingRestrictions",
    "PutSpendLimitResourceBodyPermittedSpendTypes",
    "PutSpendLimitResourceBodySpendingRestrictions",
    "SpendLimitAccountingRulesDataRequestBody",
    "TaxCodeOption",
    "TaxRate",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_gl_accounts
class GetGlAccountListResourceRequestQuery(StrictModel):
    remote_id: str | None = Field(default=None, description="Filter results to accounts matching this external or remote system identifier.")
    is_active: bool | None = Field(default=None, description="Filter by account active status: true returns only active accounts, false returns only inactive accounts, omitting this parameter returns all accounts regardless of status.")
    code: str | None = Field(default=None, description="Filter results to accounts matching this account code.")
    page_size: int | None = Field(default=None, description="Number of results per page, between 2 and 100 inclusive. Defaults to 20 if not specified.")
class GetGlAccountListResourceRequest(StrictModel):
    """Retrieve a paginated list of general ledger accounts with optional filtering by remote ID, active status, or account code."""
    query: GetGlAccountListResourceRequestQuery | None = None

# Operation: create_gl_accounts
class PostGlAccountListResourceRequestBody(StrictModel):
    gl_accounts: list[GlAccount] = Field(default=..., description="A list of general ledger accounts to upload for transaction classification. Accepts between 1 and 500 accounts per request. All accounts in the batch must be valid; a single malformed account will cause the entire batch to be rejected.", min_length=1, max_length=500)
class PostGlAccountListResourceRequest(StrictModel):
    """Batch upload general ledger accounts to classify Ramp transactions. Uploads are all-or-nothing: if any account in the batch is malformed or violates constraints, the entire batch is rejected. Ensure accounts don't already exist on Ramp; use the PATCH endpoint to update existing accounts instead."""
    body: PostGlAccountListResourceRequestBody

# Operation: get_gl_account
class GetGlAccountResourceRequestPath(StrictModel):
    gl_account_id: str = Field(default=..., description="The unique identifier (UUID) of the general ledger account to retrieve.", json_schema_extra={'format': 'uuid'})
class GetGlAccountResourceRequest(StrictModel):
    """Retrieve a specific general ledger account by its unique identifier. Returns the account details for accounting and financial reporting purposes."""
    path: GetGlAccountResourceRequestPath

# Operation: update_gl_account
class PatchGlAccountResourceRequestPath(StrictModel):
    gl_account_id: str = Field(default=..., description="The unique identifier (UUID) of the general ledger account to update.", json_schema_extra={'format': 'uuid'})
class PatchGlAccountResourceRequestBody(StrictModel):
    code: str | None = Field(default=None, description="The new code for the general ledger account. Provide an empty string to clear the existing code.")
    name: str | None = Field(default=None, description="The new name for the general ledger account.")
    reactivate: Literal[True] | None = Field(default=None, description="Set to true to reactivate a deleted general ledger account.")
class PatchGlAccountResourceRequest(StrictModel):
    """Update a general ledger account's name or code, or reactivate a previously deleted account."""
    path: PatchGlAccountResourceRequestPath
    body: PatchGlAccountResourceRequestBody | None = None

# Operation: delete_gl_account
class DeleteGlAccountResourceRequestPath(StrictModel):
    gl_account_id: str = Field(default=..., description="The unique identifier of the general ledger account to delete, provided as a UUID.", json_schema_extra={'format': 'uuid'})
class DeleteGlAccountResourceRequest(StrictModel):
    """Permanently delete a general ledger account from the accounting system. This operation removes the account and cannot be undone."""
    path: DeleteGlAccountResourceRequestPath

# Operation: create_accounting_connection
class PostAccountingConnectionResourceRequestBody(StrictModel):
    remote_provider_name: str = Field(default=..., description="The name of the accounting provider (e.g., QuickBooks, Xero, NetSuite). This identifies which accounting system to connect.")
    settings: PostAccountingConnectionResourceBodySettings | None = Field(default=None, description="Optional configuration settings specific to the accounting provider's API connection. Settings vary by provider and are only applicable to API-based connections.")
class PostAccountingConnectionResourceRequest(StrictModel):
    """Register a new API-based accounting connection to enable accounting API functionality. If a Universal CSV connection already exists for the provider, it will be automatically upgraded to an API-based connection."""
    body: PostAccountingConnectionResourceRequestBody

# Operation: get_accounting_connection
class GetAccountingConnectionDetailResourceRequestPath(StrictModel):
    connection_id: str = Field(default=..., description="The unique identifier of the accounting connection to retrieve. This ID is used to look up the specific connection record in the system.")
class GetAccountingConnectionDetailResourceRequest(StrictModel):
    """Retrieve detailed information about a specific accounting connection by its unique identifier. Use this to fetch connection settings, status, and configuration details."""
    path: GetAccountingConnectionDetailResourceRequestPath

# Operation: update_accounting_connection
class PatchAccountingConnectionDetailResourceRequestPath(StrictModel):
    connection_id: str = Field(default=..., description="The unique identifier of the accounting connection to update.")
class PatchAccountingConnectionDetailResourceRequestBody(StrictModel):
    settings: PatchAccountingConnectionDetailResourceBodySettings | None = Field(default=None, description="Configuration settings for the accounting connection. Only applicable to API-based connections; settings vary depending on the connection type and provider requirements.")
class PatchAccountingConnectionDetailResourceRequest(StrictModel):
    """Update the configuration settings for an accounting connection. This operation is restricted to API-based accounting connections and allows you to modify connection-specific settings."""
    path: PatchAccountingConnectionDetailResourceRequestPath
    body: PatchAccountingConnectionDetailResourceRequestBody | None = None

# Operation: reactivate_accounting_connection
class PostReactivateConnectionResourceRequestPath(StrictModel):
    connection_id: str = Field(default=..., description="The unique identifier (UUID) of the accounting connection to reactivate.", json_schema_extra={'format': 'uuid'})
class PostReactivateConnectionResourceRequest(StrictModel):
    """Reactivate a previously disconnected accounting connection, restoring it to active status while preserving all previous field configurations and settings. The business must not have any other active accounting connections at the time of reactivation."""
    path: PostReactivateConnectionResourceRequestPath

# Operation: list_custom_field_options
class GetCustomFieldOptionListResourceRequestQuery(StrictModel):
    remote_id: str | None = Field(default=None, description="Filter results by the external ID of custom accounting field options as they appear in the ERP system.")
    is_active: bool | None = Field(default=None, description="Filter by active status: true returns only active options, false returns only inactive options, and omitting this parameter returns all options regardless of status.")
    code: str | None = Field(default=None, description="Filter results by the code identifier of custom accounting field options.")
    visibility: Literal["HIDDEN", "VISIBLE"] | None = Field(default=None, description="Filter by visibility setting: either HIDDEN or VISIBLE. Omitting this parameter returns options with any visibility level.")
    field_id: str = Field(default=..., description="The unique identifier (ramp_id) of the custom accounting field whose options you want to retrieve. This is a UUID that must be obtained from custom field endpoints.", json_schema_extra={'format': 'uuid'})
    page_size: int | None = Field(default=None, description="The number of results to return per page, between 2 and 100 inclusive. Defaults to 20 if not specified.")
class GetCustomFieldOptionListResourceRequest(StrictModel):
    """Retrieve a paginated list of options available for a specific custom accounting field, with optional filtering by remote ID, active status, code, or visibility."""
    query: GetCustomFieldOptionListResourceRequestQuery

# Operation: create_custom_field_options
class PostCustomFieldOptionListResourceRequestBody(StrictModel):
    field_id: str = Field(default=..., description="The UUID of the custom accounting field to which these options belong. This is the ramp_id returned from custom field endpoints.", json_schema_extra={'format': 'uuid'})
    options: list[FieldOption] = Field(default=..., description="A list of field options to upload for the specified custom accounting field. Must contain between 1 and 500 options. All options in the batch are processed together; if any option is invalid, the entire batch is rejected.", min_length=1, max_length=500)
class PostCustomFieldOptionListResourceRequest(StrictModel):
    """Batch upload new options for a custom accounting field. Up to 500 options can be uploaded at once in an all-or-nothing transaction—if any option is malformed or violates constraints, the entire batch is rejected. Ensure options don't already exist on Ramp; use the PATCH endpoint to update existing options instead."""
    body: PostCustomFieldOptionListResourceRequestBody

# Operation: get_custom_field_option
class GetCustomFieldOptionResourceRequestPath(StrictModel):
    field_option_id: str = Field(default=..., description="The unique identifier (UUID) of the custom field option to retrieve.", json_schema_extra={'format': 'uuid'})
class GetCustomFieldOptionResourceRequest(StrictModel):
    """Retrieve a specific custom accounting field option by its unique identifier. Use this to fetch details about a predefined option value for a custom accounting field."""
    path: GetCustomFieldOptionResourceRequestPath

# Operation: update_custom_field_option
class PutCustomFieldOptionResourceRequestPath(StrictModel):
    field_option_id: str = Field(default=..., description="The unique identifier (UUID format) of the custom field option to update.", json_schema_extra={'format': 'uuid'})
class PutCustomFieldOptionResourceRequestBody(StrictModel):
    code: str | None = Field(default=None, description="The code identifier for this custom field option. You can provide an empty string to clear the code. Only available for non-ERP integrated systems.")
    reactivate: Literal[True] | None = Field(default=None, description="Set to true to reactivate a previously deleted custom field option. Only available for non-ERP integrated systems.")
    value: str | None = Field(default=None, description="The display name of the custom field option. Only available for non-ERP integrated systems.")
    visibility: Literal["HIDDEN", "VISIBLE"] | None = Field(default=None, description="Controls whether this option is visible or hidden in the UI. Must be either VISIBLE or HIDDEN.")
class PutCustomFieldOptionResourceRequest(StrictModel):
    """Update a custom accounting field option by modifying its code, name, visibility, or reactivation status. Only available for non-ERP integrated systems."""
    path: PutCustomFieldOptionResourceRequestPath
    body: PutCustomFieldOptionResourceRequestBody | None = None

# Operation: update_custom_field_option_partial
class PatchCustomFieldOptionResourceRequestPath(StrictModel):
    field_option_id: str = Field(default=..., description="The unique identifier (UUID format) of the custom field option to update.", json_schema_extra={'format': 'uuid'})
class PatchCustomFieldOptionResourceRequestBody(StrictModel):
    code: str | None = Field(default=None, description="The code identifier for this custom field option. You can provide an empty string to clear the code. Only available for non-ERP integrated systems.")
    reactivate: Literal[True] | None = Field(default=None, description="Set to true to reactivate a previously deleted custom field option. Only available for non-ERP integrated systems.")
    value: str | None = Field(default=None, description="The display name of the custom field option. Only available for non-ERP integrated systems.")
    visibility: Literal["HIDDEN", "VISIBLE"] | None = Field(default=None, description="Controls whether this option is visible or hidden in the UI. Must be either VISIBLE or HIDDEN.")
class PatchCustomFieldOptionResourceRequest(StrictModel):
    """Update a custom accounting field option by modifying its code, value, visibility, or reactivation status. Only available for non-ERP integrated systems."""
    path: PatchCustomFieldOptionResourceRequestPath
    body: PatchCustomFieldOptionResourceRequestBody | None = None

# Operation: delete_custom_field_option
class DeleteCustomFieldOptionResourceRequestPath(StrictModel):
    field_option_id: str = Field(default=..., description="The unique identifier (UUID) of the custom field option to delete.", json_schema_extra={'format': 'uuid'})
class DeleteCustomFieldOptionResourceRequest(StrictModel):
    """Delete a custom accounting field option by its unique identifier. This operation permanently removes the field option from the accounting system."""
    path: DeleteCustomFieldOptionResourceRequestPath

# Operation: list_custom_accounting_fields
class GetCustomFieldListResourceRequestQuery(StrictModel):
    remote_id: str | None = Field(default=None, description="Filter results to custom accounting fields matching a specific remote or external ID in your ERP system.")
    is_active: bool | None = Field(default=None, description="Filter by field status: omit to return all fields, true for active fields only, or false for inactive fields only.")
    page_size: int | None = Field(default=None, description="Number of results per page, between 2 and 100 (defaults to 20 if not specified).")
class GetCustomFieldListResourceRequest(StrictModel):
    """Retrieve a paginated list of custom accounting fields from your ERP system, with optional filtering by remote ID and active status."""
    query: GetCustomFieldListResourceRequestQuery | None = None

# Operation: create_accounting_custom_field
class PostCustomFieldListResourceRequestBody(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for this custom field in your ERP system. This ID is used to match and prevent duplicate fields.")
    input_type: Literal["BOOLEAN", "FREE_FORM_TEXT", "SINGLE_CHOICE"] = Field(default=..., description="The data type for user input: BOOLEAN for true/false values, FREE_FORM_TEXT for open-ended text, or SINGLE_CHOICE for predefined options.")
    is_required_for: list[Literal["BILL", "BILL_PAYMENT", "INVOICE", "PURCHASE_ORDER", "REIMBURSEMENT", "TRANSACTION", "VENDOR_CREDIT"]] | None = Field(default=None, description="An optional list of object types that must have this field populated before they can be marked as ready to sync (e.g., expenses, invoices).")
    is_splittable: bool | None = Field(default=None, description="Optional flag to allow this field to annotate individual split line items within a transaction. Defaults to false if not specified.")
    name: str = Field(default=..., description="The display name for this custom accounting field as it will appear in the UI.")
class PostCustomFieldListResourceRequest(StrictModel):
    """Create a new custom accounting field for your ERP system integration. If a field with the same ID already exists, the existing field will be returned; inactive fields will be reactivated. To modify an existing field, use the update endpoint instead."""
    body: PostCustomFieldListResourceRequestBody

# Operation: get_custom_field
class GetCustomFieldResourceRequestPath(StrictModel):
    field_id: str = Field(default=..., description="The unique identifier (UUID) of the custom accounting field to retrieve.", json_schema_extra={'format': 'uuid'})
class GetCustomFieldResourceRequest(StrictModel):
    """Retrieve a custom accounting field by its unique identifier. Use this to fetch detailed information about a specific custom field configured in your accounting system."""
    path: GetCustomFieldResourceRequestPath

# Operation: update_custom_accounting_field
class PatchCustomFieldResourceRequestPath(StrictModel):
    field_id: str = Field(default=..., description="The unique identifier (UUID) of the custom accounting field to update.", json_schema_extra={'format': 'uuid'})
class PatchCustomFieldResourceRequestBody(StrictModel):
    is_splittable: bool | None = Field(default=None, description="Whether this custom field can be split across multiple line items or cost centers.")
    name: str | None = Field(default=None, description="The display name for the custom accounting field.")
class PatchCustomFieldResourceRequest(StrictModel):
    """Update properties of a custom accounting field in Ramp, such as its name or splittability configuration. Specify the field by its UUID and provide the properties you want to modify."""
    path: PatchCustomFieldResourceRequestPath
    body: PatchCustomFieldResourceRequestBody | None = None

# Operation: delete_custom_field
class DeleteCustomFieldResourceRequestPath(StrictModel):
    field_id: str = Field(default=..., description="The unique identifier (UUID) of the custom accounting field to delete.", json_schema_extra={'format': 'uuid'})
class DeleteCustomFieldResourceRequest(StrictModel):
    """Permanently delete a custom accounting field by its unique identifier. This operation removes the field and its associated data from the accounting system."""
    path: DeleteCustomFieldResourceRequestPath

# Operation: create_inventory_item_accounting_field
class PostInventoryItemFieldListResourceRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the inventory item tracking category. This identifies the type of inventory metric or attribute being tracked (e.g., 'Warehouse Location', 'Serial Number', 'Batch ID').")
class PostInventoryItemFieldListResourceRequest(StrictModel):
    """Create a new inventory item accounting field to track a specific category for inventory items within an accounting connection. Only one active field can exist per accounting connection."""
    body: PostInventoryItemFieldListResourceRequestBody

# Operation: update_inventory_item_field
class PatchInventoryItemFieldListResourceRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The name of the inventory item field to update. Specify which accounting field should be modified.")
class PatchInventoryItemFieldListResourceRequest(StrictModel):
    """Update a specific accounting field for an inventory item. Use this to modify individual field values within an inventory item's accounting configuration."""
    body: PatchInventoryItemFieldListResourceRequestBody | None = None

# Operation: list_inventory_item_options
class GetInventoryItemFieldOptionsListResourceRequestQuery(StrictModel):
    remote_id: str | None = Field(default=None, description="Filter results to inventory items matching this external or remote system identifier.")
    is_active: bool | None = Field(default=None, description="Filter by active status: true returns only active items, false returns only inactive items, and omitting this parameter returns all items regardless of status.")
    code: str | None = Field(default=None, description="Filter results to inventory items matching this code value.")
    page_size: int | None = Field(default=None, description="Number of results per page, between 2 and 100 inclusive. Defaults to 20 if not specified.")
class GetInventoryItemFieldOptionsListResourceRequest(StrictModel):
    """Retrieve a paginated list of inventory item field options with optional filtering by remote ID, active status, or code."""
    query: GetInventoryItemFieldOptionsListResourceRequestQuery | None = None

# Operation: add_inventory_item_options
class PostInventoryItemFieldOptionsListResourceRequestBody(StrictModel):
    options: list[InventoryItemOption] = Field(default=..., description="A list of inventory item options to upload. Must contain between 1 and 500 options. Order is preserved as submitted.", min_length=1, max_length=500)
class PostInventoryItemFieldOptionsListResourceRequest(StrictModel):
    """Upload a batch of inventory item options to an active accounting field. Requires an active inventory item accounting field configured for the accounting connection."""
    body: PostInventoryItemFieldOptionsListResourceRequestBody

# Operation: update_inventory_item_option
class PatchInventoryItemFieldOptionResourceRequestPath(StrictModel):
    option_id: str = Field(default=..., description="The unique identifier of the inventory item option to update.")
class PatchInventoryItemFieldOptionResourceRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the inventory item option.")
    reactivate: Literal[True] | None = Field(default=None, description="Reactivate a deleted inventory item option. When provided, this parameter must be set to true; false is not a valid value.")
class PatchInventoryItemFieldOptionResourceRequest(StrictModel):
    """Update an inventory item option by modifying its name or reactivating a previously deleted option."""
    path: PatchInventoryItemFieldOptionResourceRequestPath
    body: PatchInventoryItemFieldOptionResourceRequestBody | None = None

# Operation: delete_inventory_item_option
class DeleteInventoryItemFieldOptionResourceRequestPath(StrictModel):
    option_id: str = Field(default=..., description="The unique identifier of the inventory item option to delete.")
class DeleteInventoryItemFieldOptionResourceRequest(StrictModel):
    """Delete a specific inventory item option by its ID. This operation removes the option from the system permanently."""
    path: DeleteInventoryItemFieldOptionResourceRequestPath

# Operation: mark_transactions_ready_to_sync
class PostReadyToSyncResourceRequestBody(StrictModel):
    object_ids: list[str] = Field(default=..., description="A list of transaction IDs to mark as ready for sync. Provide between 1 and 500 object IDs per request.", min_length=1, max_length=500)
    object_type: Literal["TRANSACTION"] = Field(default=..., description="The type of object being marked for sync. Currently supports TRANSACTION objects only.")
class PostReadyToSyncResourceRequest(StrictModel):
    """Mark one or more accounting transactions as ready to sync. This notifies the system that the specified transactions are prepared for synchronization."""
    body: PostReadyToSyncResourceRequestBody

# Operation: report_sync_results
class PostSyncListResourceRequestBody(StrictModel):
    failed_syncs: list[ApiAccountingFailedSyncRequestBody] | None = Field(default=None, description="A list of objects that failed to sync, containing between 1 and 5000 items. Include this when reporting sync failures.", min_length=1, max_length=5000)
    idempotency_key: str = Field(default=..., description="A unique identifier for this request, typically a randomly generated UUID. The server uses this to recognize and deduplicate retries of the same request.")
    successful_syncs: list[ApiAccountingSuccessfulSyncRequestBody] | None = Field(default=None, description="A list of objects that were successfully synced, containing between 1 and 5000 items. Include this when reporting sync successes.", min_length=1, max_length=5000)
    sync_type: Literal["BILL_PAYMENT_SYNC", "BILL_SYNC", "BROKERAGE_ORDER_SYNC", "REIMBURSEMENT_SYNC", "STATEMENT_CREDIT_SYNC", "TRANSACTION_SYNC", "TRANSFER_SYNC", "WALLET_TRANSFER_SYNC"] = Field(default=..., description="The category of objects being synced. Must be one of: BILL_PAYMENT_SYNC, BILL_SYNC, BROKERAGE_ORDER_SYNC, REIMBURSEMENT_SYNC, STATEMENT_CREDIT_SYNC, TRANSACTION_SYNC, TRANSFER_SYNC, or WALLET_TRANSFER_SYNC.")
class PostSyncListResourceRequest(StrictModel):
    """Report the results of a batch sync operation to Ramp, specifying which objects succeeded and which failed. An idempotency key ensures safe retry handling."""
    body: PostSyncListResourceRequestBody

# Operation: create_tax_code_field
class PostTaxCodeFieldResourceRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the tax code accounting field. This name identifies the field within the accounting system.")
class PostTaxCodeFieldResourceRequest(StrictModel):
    """Create a new tax code accounting field for an accounting connection. Only one active tax code field can exist per connection, so creating a new one will replace any existing field."""
    body: PostTaxCodeFieldResourceRequestBody

# Operation: update_tax_code_field
class PatchTaxCodeFieldResourceRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the tax code field. This identifier is used to reference the tax code in accounting operations.")
class PatchTaxCodeFieldResourceRequest(StrictModel):
    """Update the name or other properties of a tax code accounting field. Use this operation to modify an existing tax code field's configuration."""
    body: PatchTaxCodeFieldResourceRequestBody | None = None

# Operation: list_tax_code_options
class GetTaxCodeFieldOptionsListResourceRequestQuery(StrictModel):
    remote_id: str | None = Field(default=None, description="Filter results to tax codes matching this remote or external identifier from your source system.")
    is_active: bool | None = Field(default=None, description="Filter by active status: omit to return all tax codes, true for active only, or false for inactive only.")
    code: str | None = Field(default=None, description="Filter results to tax codes matching this code value exactly.")
    page_size: int | None = Field(default=None, description="Number of results per page, between 2 and 100 (defaults to 20 if not specified).")
class GetTaxCodeFieldOptionsListResourceRequest(StrictModel):
    """Retrieve a paginated list of available tax code options, with optional filtering by remote ID, active status, or code value. Use this to populate dropdowns or validate tax code selections in accounting workflows."""
    query: GetTaxCodeFieldOptionsListResourceRequestQuery | None = None

# Operation: add_tax_code_options
class PostTaxCodeFieldOptionsListResourceRequestBody(StrictModel):
    options: list[TaxCodeOption] = Field(default=..., description="A list of tax code options to upload. Must contain between 1 and 500 options.", min_length=1, max_length=500)
class PostTaxCodeFieldOptionsListResourceRequest(StrictModel):
    """Upload tax code options to an active tax code accounting field. Requires an active tax code accounting field to be configured for the accounting connection."""
    body: PostTaxCodeFieldOptionsListResourceRequestBody

# Operation: update_tax_code_option
class PatchTaxCodeFieldOptionResourceRequestPath(StrictModel):
    option_id: str = Field(default=..., description="The unique identifier of the tax code option to update.")
class PatchTaxCodeFieldOptionResourceRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name for this tax code option.")
    tax_rate_ids: list[str] | None = Field(default=None, description="A list of external tax rate IDs (remote_id values) to associate with this tax code option. Providing this value will replace all existing tax rate associations. Order is not significant.")
class PatchTaxCodeFieldOptionResourceRequest(StrictModel):
    """Update the name and associated tax rates for a specific tax code option. Changes to tax rate associations will replace all existing associations for this option."""
    path: PatchTaxCodeFieldOptionResourceRequestPath
    body: PatchTaxCodeFieldOptionResourceRequestBody | None = None

# Operation: delete_tax_code_option
class DeleteTaxCodeFieldOptionResourceRequestPath(StrictModel):
    option_id: str = Field(default=..., description="The unique identifier of the tax code option to delete.")
class DeleteTaxCodeFieldOptionResourceRequest(StrictModel):
    """Permanently delete a tax code option from the accounting system. This action cannot be undone."""
    path: DeleteTaxCodeFieldOptionResourceRequestPath

# Operation: list_tax_rates
class GetTaxCodeRatesListResourceRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Number of tax rates to return per page. Must be between 2 and 100 results; defaults to 20 if not specified.")
class GetTaxCodeRatesListResourceRequest(StrictModel):
    """Retrieve a paginated list of tax rates configured in the accounting system. Use the page_size parameter to control how many results are returned per page."""
    query: GetTaxCodeRatesListResourceRequestQuery | None = None

# Operation: upload_tax_rates
class PostTaxCodeRatesListResourceRequestBody(StrictModel):
    tax_rates: list[TaxRate] = Field(default=..., description="A list of tax rates to upload, containing between 1 and 500 rates. Each rate must be properly formatted and not already exist in your Ramp account.", min_length=1, max_length=500)
class PostTaxCodeRatesListResourceRequest(StrictModel):
    """Upload a batch of tax rates to your Ramp account. All rates in the batch are processed together—if any rate is malformed or violates constraints, the entire upload is rejected. Ensure rates are properly formatted and don't already exist in your system."""
    body: PostTaxCodeRatesListResourceRequestBody

# Operation: update_tax_rate
class PatchTaxRateDetailResourceRequestPath(StrictModel):
    tax_rate_id: str = Field(default=..., description="The unique identifier of the tax rate to update.")
class PatchTaxRateDetailResourceRequestBody(StrictModel):
    accounting_gl_account_id: str | None = Field(default=None, description="The Ramp ID of the GL account to associate with this tax rate. Must be a valid UUID format.", json_schema_extra={'format': 'uuid'})
    name: str | None = Field(default=None, description="The display name for the tax rate.")
    rate: str | None = Field(default=None, description="The tax rate percentage expressed as a decimal value (e.g., 0.10 for 10%).")
class PatchTaxRateDetailResourceRequest(StrictModel):
    """Update an existing tax rate's configuration, including its name, rate percentage, and associated GL account."""
    path: PatchTaxRateDetailResourceRequestPath
    body: PatchTaxRateDetailResourceRequestBody | None = None

# Operation: delete_tax_rate
class DeleteTaxRateDetailResourceRequestPath(StrictModel):
    tax_rate_id: str = Field(default=..., description="The unique identifier of the tax rate to delete.")
class DeleteTaxRateDetailResourceRequest(StrictModel):
    """Permanently delete a tax rate from the accounting system. This action cannot be undone."""
    path: DeleteTaxRateDetailResourceRequestPath

# Operation: list_vendors_accounting
class GetAccountingVendorListResourceRequestQuery(StrictModel):
    remote_id: str | None = Field(default=None, description="Filter results to vendors matching this remote or external identifier.")
    is_active: bool | None = Field(default=None, description="Filter by vendor active status: true returns only active vendors, false returns only inactive vendors, and omitting this parameter returns all vendors regardless of status.")
    code: str | None = Field(default=None, description="Filter results to vendors matching this code.")
    page_size: int | None = Field(default=None, description="Number of results per page, between 2 and 100 inclusive. Defaults to 20 if not specified.")
class GetAccountingVendorListResourceRequest(StrictModel):
    """Retrieve a paginated list of accounting vendors with optional filtering by remote ID, active status, or vendor code."""
    query: GetAccountingVendorListResourceRequestQuery | None = None

# Operation: create_vendors
class PostAccountingVendorListResourceRequestBody(StrictModel):
    vendors: list[AccountingVendor] = Field(default=..., description="A list of vendor objects to upload for transaction classification. Between 1 and 500 vendors can be submitted per request. Each vendor must be properly formatted and not already exist in Ramp.", min_length=1, max_length=500)
class PostAccountingVendorListResourceRequest(StrictModel):
    """Batch upload vendors to classify Ramp transactions. Uploads are all-or-nothing: if any vendor in the batch is malformed or violates constraints, the entire batch is rejected. Ensure vendors are sanitized and don't already exist in Ramp; use the update endpoint instead for modifying existing vendors."""
    body: PostAccountingVendorListResourceRequestBody

# Operation: get_vendor_accounting
class GetAccountingVendorResourceRequestPath(StrictModel):
    vendor_id: str = Field(default=..., description="The unique identifier (UUID) of the vendor to retrieve.", json_schema_extra={'format': 'uuid'})
class GetAccountingVendorResourceRequest(StrictModel):
    """Retrieve detailed information about a specific accounting vendor by its unique identifier."""
    path: GetAccountingVendorResourceRequestPath

# Operation: update_vendor_accounting
class PatchAccountingVendorResourceRequestPath(StrictModel):
    vendor_id: str = Field(default=..., description="The unique identifier of the vendor to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class PatchAccountingVendorResourceRequestBody(StrictModel):
    code: str | None = Field(default=None, description="The vendor's code identifier. Provide an empty string to clear the existing code.")
    name: str | None = Field(default=None, description="The display name of the vendor.")
    reactivate: Literal[True] | None = Field(default=None, description="Set to true to restore a vendor that was previously deleted.")
class PatchAccountingVendorResourceRequest(StrictModel):
    """Update vendor details including name and code, or reactivate a previously deleted vendor. Provide only the fields you want to modify."""
    path: PatchAccountingVendorResourceRequestPath
    body: PatchAccountingVendorResourceRequestBody | None = None

# Operation: delete_vendor_accounting
class DeleteAccountingVendorResourceRequestPath(StrictModel):
    vendor_id: str = Field(default=..., description="The unique identifier (UUID) of the vendor to delete.", json_schema_extra={'format': 'uuid'})
class DeleteAccountingVendorResourceRequest(StrictModel):
    """Permanently delete an accounting vendor by its unique identifier. This action cannot be undone."""
    path: DeleteAccountingVendorResourceRequestPath

# Operation: create_financing_application
class PostApplicationResourceRequestBody(StrictModel):
    applicant: PostApplicationResourceBodyApplicant = Field(default=..., description="Required information about the applicant, including their contact details and identification.")
    beneficial_owners: list[ApiApplicationPersonParamsRequestBody] | None = Field(default=None, description="Optional list of individuals who have beneficial ownership in the business. Order may indicate ownership hierarchy or priority.")
    business: PostApplicationResourceBodyBusiness | None = Field(default=None, description="Optional business details such as legal name, industry, and operational information.")
    controlling_officer: PostApplicationResourceBodyControllingOfficer | None = Field(default=None, description="Optional information about the individual with primary control over the business operations and decision-making.")
    financial_details: PostApplicationResourceBodyFinancialDetails | None = Field(default=None, description="Optional financial information required for underwriting assessment, such as revenue, expenses, and credit metrics.")
    oauth_authorize_params: PostApplicationResourceBodyOauthAuthorizeParams | None = Field(default=None, description="Optional OAuth parameters that, when provided, will redirect the applicant to an OAuth consent screen after they accept the invitation email.")
class PostApplicationResourceRequest(StrictModel):
    """Create a new financing application for a business applicant. The applicant will receive an email with instructions to complete their signup and application. If the applicant email already exists, an invitation will be resent for applications in progress, or the operation will have no effect if the business is already approved."""
    body: PostApplicationResourceRequestBody

# Operation: list_audit_log_events
class GetAuditLogEventsListResourceRequestQuery(StrictModel):
    user_ids: list[str] | None = Field(default=None, description="Filter results to only include events attributed to specific users. Provide an array of user IDs to narrow the results.")
    event_actor_types: list[Literal["policy_agent", "ramp", "user"]] | None = Field(default=None, description="Filter results to only include events from specific actor types (e.g., user, system, service). Provide an array of actor type values.")
    event_types: list[Literal["ABK agent blocked on user", "ABK agent review requested", "ABK agent started", "AI custom field config executed", "Accounting ai auto mark ready", "Activated card", "Added bill field", "Added card acceptance policy", "Added procurement field", "Added user to funds", "Added vendor field", "Admin changed email", "Admin changed phone", "Agent access request resolved", "Agent access requested", "Agent created", "Agent current version changed", "Agent permissions updated", "Agent version created", "Agent version published", "Approval chain updated", "Approval step added", "Approval step approved", "Approval step rejected", "Approval step skipped", "Approval step terminated", "Approved by manager", "Approved card edit request with modifications", "Approved card edit request", "Approved funds edit request with modifications", "Approved funds edit request", "Approved new card request with modifications", "Approved new card request", "Approved procurement change request", "Approved request for new funds with modifications", "Approved request for new funds", "Attendee split", "Bank account updated", "Bill linked to PO", "Bill linked", "Bill pay accepted sync for bank account from vendor network", "Bill pay accepted sync for vendor card acceptance policy from vendor network", "Bill pay accepted sync for vendor check mailing address from vendor network", "Bill pay accepted sync for vendor information from vendor network", "Bill pay accepted sync for vendor tax info from vendor network", "Bill pay accounting manual user action", "Bill pay accounting sync triggered", "Bill pay approval policy updated", "Bill pay automatic card payment no longer eligible", "Bill pay automatic card payment", "Bill pay bank account updated", "Bill pay batch payment initiated", "Bill pay business vendor unlinked from vendor network", "Bill pay card delivery", "Bill pay check address update", "Bill pay check tracking update", "Bill pay deleted bill", "Bill pay delivered payment", "Bill pay dismissed fraud alert", "Bill pay edited payee address", "Bill pay edited payment method", "Bill pay initiated payment refund", "Bill pay mailed check payment", "Bill pay marked as paid", "Bill pay matched transaction to bill", "Bill pay payment failed", "Bill pay payment posted", "Bill pay recurrence info changed for recurring series", "Bill pay rejected sync for bank account from vendor network", "Bill pay rejected sync for vendor card acceptance policy from vendor network", "Bill pay rejected sync for vendor check mailing address from vendor network", "Bill pay rejected sync for vendor information from vendor network", "Bill pay rejected sync for vendor tax info from vendor network", "Bill pay retried payment", "Bill pay returned funds", "Bill unlinked from PO", "Bill unlinked", "Billing config updated", "Blank canvas workflow execution updated", "Blank canvas workflow pause status updated", "Booking request approval policy updated", "Brokerage order updated", "Cancel revision request", "Cancelled by customer", "Cancelled by ramp", "Card delivered", "Card payment initiated", "Cash agent recommendation updated", "Changed bank account on bill", "Changed card holder", "Changed funds user", "Combined contracts with this contract", "Communication sent", "Complete revision", "Created accounting split line item", "Created card", "Created fund from purchase order", "Created merchant error", "Created unrecognized charge", "Created", "Deleted bill field", "Deleted card acceptance policy", "Deleted procurement field", "Deleted vendor field", "Deleted", "Demoted co-owner to member", "Detached funds from spend program", "Document labeled", "Document updated", "Docusign envelope updated", "Draft vendor created", "Draft vendor deleted", "Draft vendor published", "Edited bill field", "Edited card acceptance policy", "Edited contract tracking setting", "Edited procurement field", "Edited spend intent", "Edited tin", "Edited vendor field", "Edited wallet automation", "Email updated", "Emailed purchase order", "Exception given from dispute resolution", "Exception given from repayment", "Exception request approved", "Exception request cancelled", "Exception request denied", "Exception requested", "External ticket created asana", "External ticket created jira", "External ticket created linear", "External ticket created zendesk", "Funds activated from reissued virtual card", "Generated renewal brief for contract", "Ironclad workflow updated", "Issued funds", "Linked funds to spend program", "Locked access to funds", "Locked card", "Managed portfolio transfer updated", "Manager updated", "Mark as accidental", "Matched purchase order to transaction", "Matched transaction to purchase order", "Memo updated", "Merged vendors", "Name updated hris", "Name updated", "New virtual card issued for currency migration", "Notification sent due to purchase order request modification", "Password reset required", "Password reset user", "Password updated user", "Payback cancelled", "Payback payment failed", "Payback payment manually paid", "Payback payment retried", "Payback payment succeeded", "Payback request approved by user", "Payback request cancelled by manager", "Payback request rejected by user", "Payback requested by manager", "Payback triggered by user", "Payee linked to accounting", "Payment run updated", "Payment updated", "Phone updated", "Policy agent suggestion feedback submitted", "Post spend approval policy updated", "Procurement  unmatched purchase order from transaction", "Procurement  unmatched transaction from purchase order", "Procurement agent run completed", "Procurement change request approval policy updated", "Procurement send global form", "Procurement submit global form response", "Procurement vendor onboarding submitted", "Procurement vendor onboarding triggered", "Promoted member to co-owner", "Purchase order accounting sync created vendor", "Purchase order accounting sync failed", "Purchase order accounting sync success", "RFX clarification answered", "RFX clarification question submitted", "RFX closed", "RFX created", "RFX graded", "RFX published", "RFX response redacted", "RFX response submitted", "RFX vendor accepted", "RFX vendor added", "RFX vendor declined", "RFX vendor removed", "Receipt created", "Receipt deleted", "Receipt matched", "Refund cleared", "Refund paid", "Reimbursement bank account updated", "Reimbursement from user", "Reimbursement policy agent suggestion feedback submitted", "Reimbursement submitted", "Reimbursement to user", "Reimbursements disabled", "Reimbursements enabled", "Reissued card", "Rejected card edit request", "Rejected funds edit request", "Rejected new card request", "Rejected procurement change request", "Rejected request for new funds", "Reminded to approve items", "Reminded to upload missing items", "Removed user from funds", "Request revision", "Requested an edit to these funds", "Requested new card", "Requested new funds", "Resolved by ramp", "Review needed", "Reviewed by ramp", "Role updated", "SFTP Authentication Failed", "SFTP Authentication IP and Username Matched", "SFTP Configuration Changed", "Separation of duties disabled", "Separation of duties enabled", "Set member limit on shared fund", "Sourcing event created", "Sourcing event status changed", "Spend allocation change request approval policy updated", "Spend approved", "Spend rejected", "Spend request approval policy updated", "Status updated", "Submitted procurement change request", "Temporarily unlocked access to funds", "Terminated card", "Terminated funds", "Test", "Third party risk management vendor review updated", "This contract was combined with another contract", "Ticket assignee updated", "Ticket status updated", "Totp authenticator created", "Totp authenticator deleted", "Totp authenticator updated", "Transaction approval policy updated", "Transaction cleared", "Transaction entity changed", "Transaction missing item reminder event", "Transaction paid", "Transaction receipt updated", "Transaction submission policy exemption event", "Transferred ownership of funds", "Travel policy selection updated", "Undid marking transaction as accidental", "Unlocked access to funds", "Unlocked card temporarily", "Unlocked card", "Unmark as accidental", "Updated card program", "Updated card", "Updated funds", "Updated spend program", "User accepted invite", "User assigned by external firm", "User assigned through external firm merge", "User created", "User deactivated", "User deleted", "User invited", "User locked", "User login", "User previewed", "User reactivated", "User undeleted", "User unlocked", "Vendor Network updates enabled", "Vendor awarded", "Vendor credit action", "Vendor imported from erp", "Vendor management  vendor added to managed list", "Vendor management  vendor removed from managed list", "Vendor management agreement deleted document", "Vendor management agreement deleted", "Vendor management agreement linked document", "Vendor management agreement linked purchase order", "Vendor management agreement notification type switched", "Vendor management agreement status changed", "Vendor management agreement unlinked document", "Vendor management agreement unlinked purchase order", "Vendor management agreement uploaded document", "Vendor management edited agreement field", "Vendor management expansion request status changed", "Vendor payment approval policy updated", "Vendor profile access created", "Vendor profile access denied", "Vendor profile access edited", "Vendor profile access email sent", "Vendor profile access requested", "Vendor profile access revoked", "Vendor profile all documents downloaded", "Vendor profile document downloaded", "Vendor sync failure", "Viewed sensitive card details", "Violation from manager", "Violation from rule", "Violation from user", "Virtual card reissued", "Workflow restarted due to purchase order request modification"]] | None = Field(default=None, description="Filter results to only include specific event types (e.g., login, create, delete, update). Provide an array of event type values.")
    page_size: int | None = Field(default=None, description="Number of results to return per page. Must be between 2 and 100 results; defaults to 20 if not specified.")
class GetAuditLogEventsListResourceRequest(StrictModel):
    """Retrieve a paginated list of audit log events with optional filtering by user, actor type, and event type. Use this to track system activities and changes across your organization."""
    query: GetAuditLogEventsListResourceRequestQuery | None = None

# Operation: list_bank_accounts
class GetBankAccountListWithPaginationRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Number of bank accounts to return per page. Must be between 2 and 100 results; defaults to 20 if not specified.")
class GetBankAccountListWithPaginationRequest(StrictModel):
    """Retrieve a paginated list of bank accounts associated with the authenticated user or organization. Results are returned in pages with configurable size."""
    query: GetBankAccountListWithPaginationRequestQuery | None = None

# Operation: get_bank_account
class GetBankAccountResourceRequestPath(StrictModel):
    bank_account_id: str = Field(default=..., description="The unique identifier (UUID) of the bank account to retrieve.", json_schema_extra={'format': 'uuid'})
class GetBankAccountResourceRequest(StrictModel):
    """Retrieve detailed information for a specific bank account by its unique identifier. Returns the complete bank account resource including account details and metadata."""
    path: GetBankAccountResourceRequestPath

# Operation: list_bills_with_pagination
class GetBillListWithPaginationRequestQuery(StrictModel):
    entity_id: str | None = Field(default=None, description="Filter results to bills associated with a specific entity (UUID format).", json_schema_extra={'format': 'uuid'})
    customer_friendly_payment_id: str | None = Field(default=None, description="Filter by exact customer-friendly payment ID to retrieve all bills in the same payment or batch payment group.")
    draft_bill_id: str | None = Field(default=None, description="Filter by exact draft bill ID (UUID format).", json_schema_extra={'format': 'uuid'})
    invoice_number: str | None = Field(default=None, description="Filter by exact invoice number.")
    remote_id: str | None = Field(default=None, description="Filter by exact remote ID from an external system.")
    accounting_field_selection_id: str | None = Field(default=None, description="Filter to bills coded with a specific accounting field selection (UUID format).", json_schema_extra={'format': 'uuid'})
    status_summaries: list[Literal["APPROVAL_PENDING", "APPROVAL_REJECTED", "ARCHIVED", "AWAITING_RELEASE", "BLOCKED", "HELD_BY_PROVIDER", "ON_HOLD", "PAYMENT_COMPLETED", "PAYMENT_DETAILS_MISSING", "PAYMENT_ERROR", "PAYMENT_NOT_INSTRUCTED", "PAYMENT_PROCESSING", "PAYMENT_READY", "PAYMENT_SCHEDULED", "PENDING_VENDOR_APPROVAL", "WAITING_FOR_TRANSACTION_MATCH", "WAITING_FOR_VENDOR"]] | None = Field(default=None, description="Filter by one or more bill status summaries. Provide as a comma-separated list of status values.")
    payment_id: str | None = Field(default=None, description="Filter by payment ID (UUID format) to retrieve all bills belonging to the same payment.", json_schema_extra={'format': 'uuid'})
    vendor_id: str | None = Field(default=None, description="Filter results to bills from a specific vendor (UUID format).", json_schema_extra={'format': 'uuid'})
    is_accounting_sync_enabled: bool | None = Field(default=None, description="Filter by ERP sync configuration: true returns only bills configured to sync to the ERP, false returns only bills excluded from sync.")
    approval_status: Literal["APPROVED", "INITIALIZED", "PENDING", "REJECTED", "TERMINATED"] | None = Field(default=None, description="Filter by bill approval status. Valid values are: APPROVED, INITIALIZED, PENDING, REJECTED, or TERMINATED. This is distinct from payment release approval status.")
    payment_status: Literal["OPEN", "PAID"] | None = Field(default=None, description="Filter by payment status. Valid values are: OPEN (unpaid) or PAID.")
    sync_status: Literal["BILL_AND_PAYMENT_SYNCED", "BILL_SYNCED", "NOT_SYNCED"] | None = Field(default=None, description="Filter by ERP sync status. Valid values are: BILL_AND_PAYMENT_SYNCED, BILL_SYNCED, or NOT_SYNCED.")
    is_archived: bool | None = Field(default=None, description="Include archived (deleted) bills in results instead of active bills. Defaults to false.")
    from_due_date: str | None = Field(default=None, description="Return only bills with a due date on or after this date. Provide as an ISO 8601 datetime string.", json_schema_extra={'format': 'date-time'})
    to_due_date: str | None = Field(default=None, description="Return only bills with a due date on or before this date. Provide as an ISO 8601 datetime string.", json_schema_extra={'format': 'date-time'})
    from_issued_date: str | None = Field(default=None, description="Return only bills with an issue date on or after this date. Provide as an ISO 8601 datetime string.", json_schema_extra={'format': 'date-time'})
    to_issued_date: str | None = Field(default=None, description="Return only bills with an issue date on or before this date. Provide as an ISO 8601 datetime string.", json_schema_extra={'format': 'date-time'})
    from_paid_at: str | None = Field(default=None, description="Return only bills with a payment date on or after this date. Provide as an ISO 8601 datetime string.", json_schema_extra={'format': 'date-time'})
    to_paid_at: str | None = Field(default=None, description="Return only bills with a payment date on or before this date. Provide as an ISO 8601 datetime string.", json_schema_extra={'format': 'date-time'})
    min_amount: str | None = Field(default=None, description="Return only bills with an amount greater than or equal to this value. Accepts numeric values.")
    max_amount: str | None = Field(default=None, description="Return only bills with an amount less than or equal to this value. Accepts numeric values.")
    page_size: int | None = Field(default=None, description="Number of results per page. Must be between 2 and 100. Defaults to 20 if not specified.")
class GetBillListWithPaginationRequest(StrictModel):
    """Retrieve a paginated list of bills with flexible filtering by entity, vendor, payment status, approval status, dates, amounts, and accounting sync configuration. Supports searching by identifiers and status summaries."""
    query: GetBillListWithPaginationRequestQuery | None = None

# Operation: create_bill
class PostBillListWithPaginationRequestBody(StrictModel):
    accounting_field_selections: list[ApiCreateAccountingFieldParamsRequestBody] | None = Field(default=None, description="List of accounting field selections to code the bill for ERP synchronization. Specify which accounting fields and their selected values should be applied.")
    attachment_id: str | None = Field(default=None, description="UUID of a previously uploaded file to attach to this bill for reference or documentation purposes.", json_schema_extra={'format': 'uuid'})
    due_at: str = Field(default=..., description="Due date for payment of the bill in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    enable_accounting_sync: bool | None = Field(default=None, description="Set to false to prevent this bill from syncing to your ERP system. Must remain true if a remote_id is provided.")
    entity_id: str = Field(default=..., description="UUID of the business entity associated with this bill.", json_schema_extra={'format': 'uuid'})
    inventory_line_items: list[ApiCreateBillInventoryLineItemParamsRequestBody] | None = Field(default=None, description="List of inventory line items to include on the bill. Each item should specify quantity, unit cost, and inventory details.")
    invoice_currency: Literal["AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN", "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BOV", "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHE", "CHF", "CHW", "CLF", "CLP", "CNH", "CNY", "COP", "COU", "CRC", "CUC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ERN", "ETB", "EUR", "EURC", "FJD", "FKP", "GBP", "GEL", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "INR", "IQD", "IRR", "ISK", "JMD", "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KPW", "KRW", "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MXV", "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL", "SOS", "SRD", "SSP", "STN", "SVC", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY", "TTD", "TWD", "TZS", "UAH", "UGX", "USD", "USDB", "USDC", "USN", "UYI", "UYU", "UYW", "UZS", "VED", "VES", "VND", "VUV", "WST", "XAD", "XAF", "XAG", "XAU", "XBA", "XBB", "XBC", "XBD", "XCD", "XCG", "XDR", "XOF", "XPD", "XPF", "XPT", "XSU", "XTS", "XUA", "XXX", "YER", "ZAR", "ZMW", "ZWG", "ZWL"] = Field(default=..., description="Three-letter ISO 4217 currency code for the bill amount (e.g., USD, EUR, GBP). Must be a valid currency code.")
    invoice_number: str = Field(default=..., description="The invoice number displayed on the bill. Maximum 20 characters; must be unique or match your vendor's numbering system.", max_length=20)
    issued_at: str = Field(default=..., description="Date the bill was issued by the vendor in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    line_items: list[ApiCreateBillLineItemParamsRequestBody] | None = Field(default=None, description="List of line items detailing charges on the bill. Each item should include description, quantity, unit price, and optional account coding.")
    memo: str | None = Field(default=None, description="Internal memo or notes about the bill. Maximum 1000 characters.", max_length=1000)
    payment_details: ApiCreateBankAccountPaymentParamsRequestBody | ApiCreateBillVendorPaymentParamsRequestBody | ApiCreateCardBillPaymentParamsRequestBody | ApiCreateManualBillPaymentParamsRequestBody | None = Field(default=None, description="Payment method details for the bill. Schema varies based on the payment method selected (e.g., bank transfer, check, credit card).")
    posting_date: str | None = Field(default=None, description="Date the bill is posted to the accounting system in ISO 8601 date format (YYYY-MM-DD). If not provided, defaults to the issued date.", json_schema_extra={'format': 'date'})
    purchase_order_ids: list[str] | None = Field(default=None, description="List of purchase order UUIDs to match and reconcile against this bill for three-way matching.")
    remote_id: str | None = Field(default=None, description="External identifier for this bill from your system or ERP. When provided, enable_accounting_sync must be set to true.")
    vendor_contact_id: str | None = Field(default=None, description="UUID of the vendor contact to receive this bill. Must be associated with the specified vendor unless use_default_vendor_contact is enabled.", json_schema_extra={'format': 'uuid'})
    vendor_id: str = Field(default=..., description="UUID of the vendor issuing this bill.", json_schema_extra={'format': 'uuid'})
    vendor_memo: str | None = Field(default=None, description="Message or memo to include for the vendor. Maximum 400 characters.", max_length=400)
class PostBillListWithPaginationRequest(StrictModel):
    """Create a new bill for a vendor. Batch payments cannot be created through this API; use this operation for individual bill creation with line items, attachments, and accounting synchronization options."""
    body: PostBillListWithPaginationRequestBody

# Operation: list_draft_bills
class GetDraftBillListWithPaginationRequestQuery(StrictModel):
    entity_id: str | None = Field(default=None, description="Filter results to draft bills associated with a specific entity, specified as a UUID.", json_schema_extra={'format': 'uuid'})
    invoice_number: str | None = Field(default=None, description="Filter results to draft bills matching an exact invoice number.")
    remote_id: str | None = Field(default=None, description="Filter results to draft bills matching an exact remote ID.")
    vendor_id: str | None = Field(default=None, description="Filter results to draft bills from a specific vendor, specified as a UUID.", json_schema_extra={'format': 'uuid'})
    from_due_date: str | None = Field(default=None, description="Show only draft bills with a due date on or after this date. Provide as an ISO 8601 datetime string.", json_schema_extra={'format': 'date-time'})
    to_due_date: str | None = Field(default=None, description="Show only draft bills with a due date on or before this date. Provide as an ISO 8601 datetime string.", json_schema_extra={'format': 'date-time'})
    from_issued_date: str | None = Field(default=None, description="Show only draft bills with an issued date on or after this date. Provide as an ISO 8601 datetime string.", json_schema_extra={'format': 'date-time'})
    to_issued_date: str | None = Field(default=None, description="Show only draft bills with an issued date on or before this date. Provide as an ISO 8601 datetime string.", json_schema_extra={'format': 'date-time'})
    page_size: int | None = Field(default=None, description="Number of results per page. Must be between 2 and 100; defaults to 20 if not specified.")
class GetDraftBillListWithPaginationRequest(StrictModel):
    """Retrieve a paginated list of draft bills with optional filtering by entity, vendor, invoice details, and date ranges. Useful for finding bills in draft status that match specific criteria."""
    query: GetDraftBillListWithPaginationRequestQuery | None = None

# Operation: create_draft_bill
class PostDraftBillListWithPaginationRequestBody(StrictModel):
    accounting_field_selections: list[ApiCreateAccountingFieldParamsRequestBody] | None = Field(default=None, description="List of accounting field selections to code the bill for accounting purposes.")
    due_at: str | None = Field(default=None, description="Due date for payment of the bill in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    enable_accounting_sync: bool | None = Field(default=None, description="Set to false to prevent this bill from syncing to your connected ERP system; defaults to true for automatic sync.")
    entity_id: str | None = Field(default=None, description="UUID of the business entity associated with this bill.", json_schema_extra={'format': 'uuid'})
    inventory_line_items: list[ApiCreateBillInventoryLineItemParamsRequestBody] | None = Field(default=None, description="List of inventory line items to attach to the bill. Providing this replaces all existing inventory line items.")
    invoice_currency: Literal["AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN", "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BOV", "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHE", "CHF", "CHW", "CLF", "CLP", "CNH", "CNY", "COP", "COU", "CRC", "CUC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ERN", "ETB", "EUR", "EURC", "FJD", "FKP", "GBP", "GEL", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "INR", "IQD", "IRR", "ISK", "JMD", "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KPW", "KRW", "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MXV", "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL", "SOS", "SRD", "SSP", "STN", "SVC", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY", "TTD", "TWD", "TZS", "UAH", "UGX", "USD", "USDB", "USDC", "USN", "UYI", "UYU", "UYW", "UZS", "VED", "VES", "VND", "VUV", "WST", "XAD", "XAF", "XAG", "XAU", "XBA", "XBB", "XBC", "XBD", "XCD", "XCG", "XDR", "XOF", "XPD", "XPF", "XPT", "XSU", "XTS", "XUA", "XXX", "YER", "ZAR", "ZMW", "ZWG", "ZWL"] | None = Field(default=None, description="Three-letter ISO 4217 currency code for the invoice (e.g., USD, EUR, GBP). Supports major world currencies and crypto assets.")
    invoice_number: str | None = Field(default=None, description="The invoice number or reference from the vendor, up to 20 characters.", max_length=20)
    issued_at: str | None = Field(default=None, description="Date the bill was issued by the vendor in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    line_items: list[ApiCreateBillLineItemParamsRequestBody] | None = Field(default=None, description="List of line items detailing charges on the bill. Providing this replaces all existing line items.")
    memo: str | None = Field(default=None, description="Internal notes or memo about the bill, up to 1000 characters.", max_length=1000)
    posting_date: str | None = Field(default=None, description="Date the bill is posted to the accounting system in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    purchase_order_ids: list[str] | None = Field(default=None, description="List of purchase order UUIDs to match and link to this bill. Providing this replaces all existing linked purchase orders.")
    remote_id: str | None = Field(default=None, description="External identifier for this bill from your system, useful for tracking and reconciliation.")
    vendor_contact_id: str | None = Field(default=None, description="UUID of the vendor contact person associated with this bill; the contact must belong to the specified vendor.", json_schema_extra={'format': 'uuid'})
    vendor_id: str = Field(default=..., description="UUID of the vendor who issued this bill. Required to create the draft.", json_schema_extra={'format': 'uuid'})
class PostDraftBillListWithPaginationRequest(StrictModel):
    """Create a draft bill for a vendor with optional line items, accounting details, and purchase order matching. Draft bills can be configured for ERP synchronization and support multiple currencies."""
    body: PostDraftBillListWithPaginationRequestBody

# Operation: get_draft_bill
class GetDraftBillResourceRequestPath(StrictModel):
    draft_bill_id: str = Field(default=..., description="The unique identifier of the draft bill to retrieve.")
class GetDraftBillResourceRequest(StrictModel):
    """Retrieve a specific draft bill by its unique identifier. Use this to view the current state and details of a bill in draft status."""
    path: GetDraftBillResourceRequestPath

# Operation: update_draft_bill
class PatchDraftBillResourceRequestPath(StrictModel):
    draft_bill_id: str = Field(default=..., description="The unique identifier of the draft bill to update.")
class PatchDraftBillResourceRequestBody(StrictModel):
    accounting_field_selections: list[ApiCreateAccountingFieldParamsRequestBody] | None = Field(default=None, description="List of accounting field options selected to categorize and code the bill for accounting purposes.")
    due_at: str | None = Field(default=None, description="The due date for payment of the bill, specified as a calendar date.", json_schema_extra={'format': 'date'})
    enable_accounting_sync: bool | None = Field(default=None, description="Set to false to prevent this bill from automatically syncing to your connected ERP system; defaults to true.")
    entity_id: str | None = Field(default=None, description="The UUID of the business entity associated with this bill.", json_schema_extra={'format': 'uuid'})
    inventory_line_items: list[ApiCreateBillInventoryLineItemParamsRequestBody] | None = Field(default=None, description="List of inventory line items to attach to the bill. Providing this list replaces all previously existing inventory line items.")
    invoice_currency: Literal["AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN", "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BOV", "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHE", "CHF", "CHW", "CLF", "CLP", "CNH", "CNY", "COP", "COU", "CRC", "CUC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ERN", "ETB", "EUR", "EURC", "FJD", "FKP", "GBP", "GEL", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "INR", "IQD", "IRR", "ISK", "JMD", "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KPW", "KRW", "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MXV", "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL", "SOS", "SRD", "SSP", "STN", "SVC", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY", "TTD", "TWD", "TZS", "UAH", "UGX", "USD", "USDB", "USDC", "USN", "UYI", "UYU", "UYW", "UZS", "VED", "VES", "VND", "VUV", "WST", "XAD", "XAF", "XAG", "XAU", "XBA", "XBB", "XBC", "XBD", "XCD", "XCG", "XDR", "XOF", "XPD", "XPF", "XPT", "XSU", "XTS", "XUA", "XXX", "YER", "ZAR", "ZMW", "ZWG", "ZWL"] | None = Field(default=None, description="The currency code for the invoice amount, selected from the ISO 4217 standard currency list.")
    invoice_number: str | None = Field(default=None, description="The vendor's invoice number or reference identifier, up to 20 characters.", max_length=20)
    issued_at: str | None = Field(default=None, description="The date the bill was issued by the vendor, specified as a calendar date.", json_schema_extra={'format': 'date'})
    line_items: list[ApiCreateBillLineItemParamsRequestBody] | None = Field(default=None, description="List of line items detailing charges, quantities, and amounts on the bill. Providing this list replaces all previously existing line items.")
    memo: str | None = Field(default=None, description="Internal notes or comments about the bill, up to 1000 characters.", max_length=1000)
    posting_date: str | None = Field(default=None, description="The date the bill is posted or recorded in the accounting system, specified as a calendar date.", json_schema_extra={'format': 'date'})
    purchase_order_ids: list[str] | None = Field(default=None, description="List of purchase order identifiers to match and link with this bill. Providing this list replaces all previously linked purchase orders.")
    remote_id: str | None = Field(default=None, description="An external identifier or reference number for this bill from your internal system or vendor portal.")
    vendor_contact_id: str | None = Field(default=None, description="The UUID of the vendor contact person associated with this bill; the contact must belong to the specified vendor.", json_schema_extra={'format': 'uuid'})
    vendor_id: str | None = Field(default=None, description="The UUID of the vendor issuing this bill.", json_schema_extra={'format': 'uuid'})
class PatchDraftBillResourceRequest(StrictModel):
    """Update an existing draft bill with new details such as vendor information, line items, dates, and accounting settings. Changes are applied to the draft without posting to the accounting system."""
    path: PatchDraftBillResourceRequestPath
    body: PatchDraftBillResourceRequestBody | None = None

# Operation: add_draft_bill_attachment
class PostDraftBillAttachmentUploadResourceRequestPath(StrictModel):
    draft_bill_id: str = Field(default=..., description="The unique identifier of the draft bill to which the attachment will be uploaded.")
class PostDraftBillAttachmentUploadResourceRequestBody(StrictModel):
    attachment_type: Literal["EMAIL", "FILE", "INVOICE", "VENDOR_CREDIT"] = Field(default=..., description="The classification of the attachment. Use 'INVOICE' to designate the actual invoice document for the bill; only one INVOICE attachment is permitted per draft bill.")
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="The file to upload as a binary attachment. The file should be included in the multipart/form-data request with the part name 'file' and Content-Disposition header set to 'attachment'.", json_schema_extra={'format': 'binary'})
class PostDraftBillAttachmentUploadResourceRequest(StrictModel):
    """Upload a file attachment to a draft bill. Only one INVOICE type attachment is allowed per draft bill."""
    path: PostDraftBillAttachmentUploadResourceRequestPath
    body: PostDraftBillAttachmentUploadResourceRequestBody

# Operation: get_bill
class GetBillResourceRequestPath(StrictModel):
    bill_id: str = Field(default=..., description="The unique identifier of the bill to retrieve. This is a required string value that identifies which bill to fetch.")
class GetBillResourceRequest(StrictModel):
    """Retrieve a specific bill by its unique identifier. Returns the complete bill details including charges, dates, and payment information."""
    path: GetBillResourceRequestPath

# Operation: update_bill
class PatchBillResourceRequestPath(StrictModel):
    bill_id: str = Field(default=..., description="The unique identifier of the bill to update.")
class PatchBillResourceRequestBody(StrictModel):
    accounting_field_selections: list[ApiCreateAccountingFieldParamsRequestBody] | None = Field(default=None, description="List of accounting field selections used to code the bill for accounting purposes.")
    due_at: str | None = Field(default=None, description="The due date for payment, specified as a date in ISO 8601 format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    entity_id: str | None = Field(default=None, description="The UUID of the business entity associated with this bill.", json_schema_extra={'format': 'uuid'})
    inventory_line_items: list[ApiCreateBillInventoryLineItemParamsRequestBody] | None = Field(default=None, description="List of inventory line items to attach to the bill. Providing this replaces all existing inventory line items.")
    invoice_number: str | None = Field(default=None, description="The vendor's invoice number, up to 20 characters.", max_length=20)
    issued_at: str | None = Field(default=None, description="The date the bill was issued, specified as a date in ISO 8601 format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    line_items: list[ApiCreateBillLineItemParamsRequestBody] | None = Field(default=None, description="List of line items detailing charges on the bill. Providing this replaces all existing line items.")
    memo: str | None = Field(default=None, description="Internal memo or notes about the bill, up to 1000 characters.", max_length=1000)
    posting_date: str | None = Field(default=None, description="The date the bill is posted to the accounting system, specified as a date in ISO 8601 format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    purchase_order_ids: list[str] | None = Field(default=None, description="List of purchase order identifiers to match against this bill. Providing this replaces all existing linked purchase orders.")
    remote_id: str | None = Field(default=None, description="An external identifier that uniquely identifies this bill in the client's system.")
    vendor_contact_id: str | None = Field(default=None, description="The UUID of the vendor contact associated with this bill. The contact must belong to the specified vendor.", json_schema_extra={'format': 'uuid'})
    vendor_id: str | None = Field(default=None, description="The UUID of the vendor who issued this bill.", json_schema_extra={'format': 'uuid'})
    vendor_memo: str | None = Field(default=None, description="Memo or message to include for the vendor, up to 400 characters.", max_length=400)
class PatchBillResourceRequest(StrictModel):
    """Update an approved bill with new financial details, line items, dates, or vendor information. Only bills with approved status can be modified."""
    path: PatchBillResourceRequestPath
    body: PatchBillResourceRequestBody | None = None

# Operation: archive_bill
class DeleteBillResourceRequestPath(StrictModel):
    bill_id: str = Field(default=..., description="The unique identifier of the bill to archive. Paid bills and bills belonging to a batch payment cannot be deleted.")
class DeleteBillResourceRequest(StrictModel):
    """Archive a bill and cancel associated inflight payments or terminate attached one-time cards. This is a destructive action that cannot be reversed for paid bills or bills in batch payments."""
    path: DeleteBillResourceRequestPath

# Operation: add_bill_attachment
class PostBillAttachmentUploadResourceRequestPath(StrictModel):
    bill_id: str = Field(default=..., description="The unique identifier of the bill to attach the file to, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class PostBillAttachmentUploadResourceRequestBody(StrictModel):
    attachment_type: Literal["EMAIL", "FILE", "INVOICE", "VENDOR_CREDIT"] = Field(default=..., description="The classification of the attachment. Use 'INVOICE' to designate the actual invoice document for the bill; only one INVOICE attachment is permitted per bill.")
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="The binary file content to upload as the attachment.", json_schema_extra={'format': 'binary'})
class PostBillAttachmentUploadResourceRequest(StrictModel):
    """Upload a file attachment to an existing bill. Note that only one INVOICE type attachment is allowed per bill."""
    path: PostBillAttachmentUploadResourceRequestPath
    body: PostBillAttachmentUploadResourceRequestBody

# Operation: list_cards
class GetCardListWithPaginationRequestQuery(StrictModel):
    entity_id: str | None = Field(default=None, description="Filter results to cards belonging to a specific business entity, specified as a UUID.", json_schema_extra={'format': 'uuid'})
    user_id: str | None = Field(default=None, description="Filter results to cards owned by a specific user, specified as a UUID.", json_schema_extra={'format': 'uuid'})
    is_activated: bool | None = Field(default=None, description="Filter to show only activated cards. Defaults to true if not specified.")
    is_terminated: bool | None = Field(default=None, description="Filter to show only terminated cards. Defaults to false if not specified.")
    page_size: int | None = Field(default=None, description="Number of results per page, between 2 and 100 inclusive. Defaults to 20 if not specified.")
class GetCardListWithPaginationRequest(StrictModel):
    """Retrieve a paginated list of cards with optional filtering by entity, user, activation status, and termination status."""
    query: GetCardListWithPaginationRequestQuery | None = None

# Operation: create_physical_card
class PostPhysicalCardRequestBody(StrictModel):
    entity_id: str | None = Field(default=None, description="UUID of the business entity to associate with the card. If omitted, the card will be linked to the entity associated with the user's location.", json_schema_extra={'format': 'uuid'})
    fulfillment: PostPhysicalCardBodyFulfillment | None = Field(default=None, description="Fulfillment configuration for the physical card, including delivery address and shipping preferences.")
    idempotency_key: str = Field(default=..., description="A unique identifier (typically a UUID) generated by the client to ensure idempotent requests. The server uses this to recognize and deduplicate retries of the same request.")
    is_temporary: bool | None = Field(default=None, description="Set to true to create a temporary card with limited validity. Defaults to false for standard permanent cards.")
    spending_restrictions: PostPhysicalCardBodySpendingRestrictions | None = Field(default=None, description="Spending limits and restrictions to apply to the card. Either this or card_program_id must be provided to define card behavior.")
    user_id: str = Field(default=..., description="UUID of the user who will own and use the card.", json_schema_extra={'format': 'uuid'})
class PostPhysicalCardRequest(StrictModel):
    """Initiates an asynchronous request to create a new physical Ramp card for a specified user. The operation returns immediately with a task ID for tracking the card creation process."""
    body: PostPhysicalCardRequestBody

# Operation: get_card_deferred_task_status
class GetCardDeferredTaskResourceRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the deferred task, provided as a UUID.", json_schema_extra={'format': 'uuid'})
class GetCardDeferredTaskResourceRequest(StrictModel):
    """Retrieve the current status of a deferred card processing task. Use this to poll for completion of asynchronous card operations."""
    path: GetCardDeferredTaskResourceRequestPath

# Operation: create_virtual_card
class PostVirtualCardRequestBody(StrictModel):
    entity_id: str | None = Field(default=None, description="UUID of the business entity to associate with the card. If omitted, the card will be linked to the entity associated with the user's location.", json_schema_extra={'format': 'uuid'})
    idempotency_key: str = Field(default=..., description="A unique identifier (typically a UUID) generated by the client to prevent duplicate card creation if the request is retried. The server uses this to recognize and deduplicate subsequent attempts of the same request.")
    is_temporary: bool | None = Field(default=None, description="Set to true to create a temporary card with limited validity; defaults to false for standard permanent cards.")
    spending_restrictions: PostVirtualCardBodySpendingRestrictions | None = Field(default=None, description="Defines spending limits and restrictions for the card. Either this parameter or card_program_id must be provided to configure card behavior.")
    user_id: str = Field(default=..., description="UUID of the user who will own and use the card. This is required to identify the cardholder.", json_schema_extra={'format': 'uuid'})
class PostVirtualCardRequest(StrictModel):
    """Initiates an asynchronous request to create a new virtual card for a specified user. Returns a task identifier that can be used to track the card creation status."""
    body: PostVirtualCardRequestBody

# Operation: get_card
class GetCardResourceRequestPath(StrictModel):
    card_id: str = Field(default=..., description="The unique identifier of the card to retrieve.")
class GetCardResourceRequest(StrictModel):
    """Retrieve detailed information about a specific card by its unique identifier."""
    path: GetCardResourceRequestPath

# Operation: update_card
class PatchCardResourceRequestPath(StrictModel):
    card_id: str = Field(default=..., description="The unique identifier of the card to update.")
class PatchCardResourceRequestBody(StrictModel):
    entity_id: str | None = Field(default=None, description="The UUID of the business entity to associate with this card. Use this to reassign the card to a different entity.", json_schema_extra={'format': 'uuid'})
    has_notifications_enabled: bool | None = Field(default=None, description="Enable or disable notifications for this card.")
    new_user_id: str | None = Field(default=None, description="The UUID of the user who will become the new owner of this card.", json_schema_extra={'format': 'uuid'})
    spending_restrictions: PatchCardResourceBodySpendingRestrictions | None = Field(default=None, description="Spending restrictions to apply to the card. Only include fields that need to be modified; unchanged restrictions do not need to be specified.")
class PatchCardResourceRequest(StrictModel):
    """Update card properties including owner, display name, and spending restrictions. Allows modification of the associated business entity and notification settings."""
    path: PatchCardResourceRequestPath
    body: PatchCardResourceRequestBody | None = None

# Operation: suspend_card
class PostCardSuspensionResourceRequestPath(StrictModel):
    card_id: str = Field(default=..., description="The unique identifier of the card to suspend.")
class PostCardSuspensionResourceRequestBody(StrictModel):
    idempotency_key: str = Field(default=..., description="A unique identifier generated by the client (typically a UUID) to ensure idempotent behavior. The server uses this to recognize and deduplicate retried requests, preventing duplicate suspensions if the request is sent multiple times.")
class PostCardSuspensionResourceRequest(StrictModel):
    """Suspend a card to lock it from use. This creates an asynchronous task that prevents further transactions on the card; the suspension can be reverted later."""
    path: PostCardSuspensionResourceRequestPath
    body: PostCardSuspensionResourceRequestBody

# Operation: delete_card
class PostCardTerminationResourceRequestPath(StrictModel):
    card_id: str = Field(default=..., description="The unique identifier of the card to terminate.")
class PostCardTerminationResourceRequestBody(StrictModel):
    idempotency_key: str = Field(default=..., description="A unique value generated by the client (typically a UUID) to ensure idempotent behavior. The server uses this key to recognize and deduplicate retried requests, preventing duplicate terminations if the request is sent multiple times.")
class PostCardTerminationResourceRequest(StrictModel):
    """Permanently terminate a card by creating an asynchronous task. This action is irreversible and cannot be undone."""
    path: PostCardTerminationResourceRequestPath
    body: PostCardTerminationResourceRequestBody

# Operation: unsuspend_card
class PostCardUnsuspensionResourceRequestPath(StrictModel):
    card_id: str = Field(default=..., description="The unique identifier of the card to unsuspend.")
class PostCardUnsuspensionResourceRequestBody(StrictModel):
    idempotency_key: str = Field(default=..., description="A unique identifier (typically a UUID) generated by the client to ensure idempotent request handling. The server uses this to recognize and deduplicate retries of the same request.")
class PostCardUnsuspensionResourceRequest(StrictModel):
    """Initiates an asynchronous task to remove a card's suspension status, allowing it to be used for transactions again."""
    path: PostCardUnsuspensionResourceRequestPath
    body: PostCardUnsuspensionResourceRequestBody

# Operation: list_cashbacks
class GetCashbackListWithPaginationRequestQuery(StrictModel):
    sync_status: Literal["NOT_SYNC_READY", "SYNCED", "SYNC_READY"] | None = Field(default=None, description="Filter results by synchronization status. Use NOT_SYNC_READY for cashbacks pending sync, SYNC_READY for those ready to sync, or SYNCED for already synchronized cashbacks. When provided, this filter takes precedence over other sync-related filters.")
    entity_id: str | None = Field(default=None, description="Filter cashbacks to those associated with a specific business entity, specified as a UUID.", json_schema_extra={'format': 'uuid'})
    statement_id: str | None = Field(default=None, description="Filter cashbacks to only those included in a specific statement, specified as a UUID.", json_schema_extra={'format': 'uuid'})
    page_size: int | None = Field(default=None, description="Number of results per page, between 2 and 100 inclusive. Defaults to 20 if not specified.")
class GetCashbackListWithPaginationRequest(StrictModel):
    """Retrieve a paginated list of cashback payments with optional filtering by sync status, business entity, or statement inclusion."""
    query: GetCashbackListWithPaginationRequestQuery | None = None

# Operation: get_cashback
class GetCashbackResourceRequestPath(StrictModel):
    cashback_id: str = Field(default=..., description="The unique identifier of the cashback payment to retrieve.")
class GetCashbackResourceRequest(StrictModel):
    """Retrieve details for a specific cashback payment by its unique identifier."""
    path: GetCashbackResourceRequestPath

# Operation: list_custom_table_columns
class GetDevApiCustomTableColumnRequestPath(StrictModel):
    custom_table_name: str = Field(default=..., description="The name of the custom table for which to list columns. This is the identifier of the custom table resource.")
class GetDevApiCustomTableColumnRequest(StrictModel):
    """Retrieve all columns defined for a specific custom table. Returns the column metadata including names, types, and configurations for the specified custom table."""
    path: GetDevApiCustomTableColumnRequestPath

# Operation: list_custom_table_rows
class GetDevApiCustomRowRequestPath(StrictModel):
    custom_table_name: str = Field(default=..., description="The name of the custom table to query for rows.")
class GetDevApiCustomRowRequestQuery(StrictModel):
    external_key: list[str] | None = Field(default=None, description="Filter results by the external key of custom rows. Accepts one or more external key values to match against.")
    include_all_referenced_rows: bool | None = Field(default=None, description="When enabled, includes all referenced rows in each cell instead of a limited subset. Defaults to false for performance.")
    page_size: int | None = Field(default=None, description="Number of rows to return per request, up to a maximum of 100. Defaults to 50 rows.")
class GetDevApiCustomRowRequest(StrictModel):
    """Retrieve rows from a custom table, with optional filtering by external key and control over referenced row inclusion and pagination."""
    path: GetDevApiCustomRowRequestPath
    query: GetDevApiCustomRowRequestQuery | None = None

# Operation: update_custom_table_rows
class PutDevApiCustomRowRequestPath(StrictModel):
    custom_table_name: str = Field(default=..., description="The name of the custom table where rows will be inserted or updated.")
class PutDevApiCustomRowRequestBody(StrictModel):
    data: list[CustomRowColumnContentsByColumnNameRequestBody] = Field(default=..., description="An array of row objects to insert or update. All objects must have identical column names; use null to omit setting a value for a specific column in a row.")
class PutDevApiCustomRowRequest(StrictModel):
    """Insert or update multiple rows in a custom table. Rows are identified by their existing keys, and all entries must contain the same set of column names with null values for columns that should not be modified."""
    path: PutDevApiCustomRowRequestPath
    body: PutDevApiCustomRowRequestBody

# Operation: delete_custom_table_rows
class DeleteDevApiCustomRowRequestPath(StrictModel):
    custom_table_name: str = Field(default=..., description="The name of the custom table from which rows will be deleted.")
class DeleteDevApiCustomRowRequestBody(StrictModel):
    data: list[CustomRowExternalKeyRequestBody] = Field(default=..., description="An array of external keys identifying the rows to delete. Each key must correspond to an existing row in the specified custom table.")
class DeleteDevApiCustomRowRequest(StrictModel):
    """Delete one or more rows from a custom table by their external keys. Specify the custom table and provide a list of row identifiers to remove."""
    path: DeleteDevApiCustomRowRequestPath
    body: DeleteDevApiCustomRowRequestBody

# Operation: update_custom_table_row_external_key
class PatchDevApiChangeCustomRowExternalKeyRequestPath(StrictModel):
    custom_table_name: str = Field(default=..., description="The name of the custom table containing the row to be updated.")
    row_id: str = Field(default=..., description="The unique identifier of the row whose external key should be changed.")
class PatchDevApiChangeCustomRowExternalKeyRequestBody(StrictModel):
    new_external_key: str = Field(default=..., description="The new external key value to assign to the row. This becomes the new external identifier for the row.")
class PatchDevApiChangeCustomRowExternalKeyRequest(StrictModel):
    """Updates the external key identifier for a specific row in a custom table. This operation allows you to change how the row is referenced externally."""
    path: PatchDevApiChangeCustomRowExternalKeyRequestPath
    body: PatchDevApiChangeCustomRowExternalKeyRequestBody

# Operation: append_custom_table_rows
class PostDevApiAppendCustomRowCellsRequestPath(StrictModel):
    table_name: str = Field(default=..., description="The name of the custom table where rows will be appended or updated.")
class PostDevApiAppendCustomRowCellsRequestBody(StrictModel):
    data: list[CustomRowColumnContentsByColumnNameRequestBody] = Field(default=..., description="An array of row objects to insert or update. All objects in the array must have identical column names; use null for any columns where a value should not be set.")
class PostDevApiAppendCustomRowCellsRequest(StrictModel):
    """Append or update multiple rows in a custom table by providing cell data. Each row entry must contain the same set of column names, with null values used to indicate cells that should not be modified."""
    path: PostDevApiAppendCustomRowCellsRequestPath
    body: PostDevApiAppendCustomRowCellsRequestBody

# Operation: remove_custom_table_row_cells
class PostDevApiRemoveCustomRowCellsRequestPath(StrictModel):
    table_name: str = Field(default=..., description="The name of the custom table from which cells will be removed. This identifies the target table for the operation.")
class PostDevApiRemoveCustomRowCellsRequestBody(StrictModel):
    data: list[CustomRowColumnContentsByColumnNameRequestBody] = Field(default=..., description="An array of row specifications indicating which cells to remove. Each row entry must specify the row identifier and list the column names whose cells should be cleared. All entries must use consistent column naming.")
class PostDevApiRemoveCustomRowCellsRequest(StrictModel):
    """Remove specific cells from rows in a custom table. Specify which cells to clear by providing row identifiers and column names."""
    path: PostDevApiRemoveCustomRowCellsRequestPath
    body: PostDevApiRemoveCustomRowCellsRequestBody

# Operation: create_matrix_table
class PostDevApiMatrixTablesRequestBody(StrictModel):
    input_columns: list[DeveloperApiMatrixInputColumnDefRequestBody] = Field(default=..., description="Array of input columns that define the matrix dimensions. Each column can reference existing fields or accept numeric values. The order of columns defines the lookup hierarchy.")
    label: str = Field(default=..., description="Human-readable display name for the matrix table, shown in the user interface.")
    name: str | None = Field(default=None, description="API identifier for the matrix table used in programmatic references. If not provided, a default name will be generated automatically.")
    result_columns: list[DeveloperApiMatrixResultColumnDefRequestBody] = Field(default=..., description="Array of result columns that store the output values computed from the input column combinations. The order corresponds to the sequence of results returned.")
class PostDevApiMatrixTablesRequest(StrictModel):
    """Create a matrix table that maps unique combinations of input values to result values, enabling efficient lookup operations across multiple dimensions."""
    body: PostDevApiMatrixTablesRequestBody

# Operation: add_result_column_to_matrix_table
class PostDevApiAddMatrixResultColumnRequestPath(StrictModel):
    table_name: str = Field(default=..., description="The name of the matrix table to which the result column will be added.")
class PostDevApiAddMatrixResultColumnRequestBody(StrictModel):
    cardinality: Literal["many_to_many", "many_to_one"] = Field(default=..., description="The relationship cardinality for the result column: either many_to_one or many_to_many, defining how the result data relates to the matrix rows.")
    label: str = Field(default=..., description="The display name for the result column as it will appear in the user interface.")
    name: str | None = Field(default=None, description="The API name for the result column used in programmatic access. If not provided, a default name will be generated.")
    native_table: PostDevApiAddMatrixResultColumnBodyNativeTable = Field(default=..., description="The native table that the result column references. Only users and accounting_field_options are supported as valid native tables.")
class PostDevApiAddMatrixResultColumnRequest(StrictModel):
    """Add a result column to an existing matrix table, enabling aggregation of user or accounting field data without modifying the table's input columns. Result columns can only reference users or accounting_field_options native tables."""
    path: PostDevApiAddMatrixResultColumnRequestPath
    body: PostDevApiAddMatrixResultColumnRequestBody

# Operation: rename_matrix_column
class PatchDevApiRenameMatrixColumnRequestPath(StrictModel):
    column_name: str = Field(default=..., description="The current API name of the column to rename within the matrix table.")
    table_name: str = Field(default=..., description="The name of the matrix table containing the column to rename.")
class PatchDevApiRenameMatrixColumnRequestBody(StrictModel):
    new_name: str = Field(default=..., description="The new API name to assign to the column. This becomes the identifier used in API requests and responses.")
class PatchDevApiRenameMatrixColumnRequest(StrictModel):
    """Rename the API identifier for a matrix table column while keeping its human-readable label unchanged. This operation works for both input and result columns in custom matrix records."""
    path: PatchDevApiRenameMatrixColumnRequestPath
    body: PatchDevApiRenameMatrixColumnRequestBody

# Operation: list_matrix_table_rows
class PostDevApiMatrixListRowsRequestPath(StrictModel):
    table_name: str = Field(default=..., description="The name of the matrix table to query.")
class PostDevApiMatrixListRowsRequestBody(StrictModel):
    external_keys: list[str] | None = Field(default=None, description="Optional list of external keys to filter results to specific rows. Only rows matching one of the provided keys are returned.")
    filters: list[DeveloperApiMatrixColumnFilterRequestBody] | None = Field(default=None, description="Optional list of filters to apply against input column values. Only rows matching ALL specified filters are included in results.")
    page_size: int | None = Field(default=None, description="Maximum number of rows to return per page. Defaults to 100 rows.")
class PostDevApiMatrixListRowsRequest(StrictModel):
    """Retrieve rows from a matrix table with inputs and results separated. Input columns are always complete, while result columns contain only values that have been explicitly set."""
    path: PostDevApiMatrixListRowsRequestPath
    body: PostDevApiMatrixListRowsRequestBody | None = None

# Operation: rename_matrix_table
class PostDevApiRenameMatrixTableRequestPath(StrictModel):
    table_name: str = Field(default=..., description="The current API name of the Matrix table to be renamed. This is the identifier used to reference the table in API operations.")
class PostDevApiRenameMatrixTableRequestBody(StrictModel):
    new_name: str = Field(default=..., description="The new API name for the Matrix table. This will become the identifier used to reference the table in subsequent API operations.")
class PostDevApiRenameMatrixTableRequest(StrictModel):
    """Updates the API name of an existing Matrix table. This operation allows you to change how the table is referenced in API calls without affecting its underlying data or structure."""
    path: PostDevApiRenameMatrixTableRequestPath
    body: PostDevApiRenameMatrixTableRequestBody

# Operation: upsert_matrix_table_rows
class PutDevApiMatrixPutRowsRequestPath(StrictModel):
    table_name: str = Field(default=..., description="The name of the matrix table to upsert rows into.")
class PutDevApiMatrixPutRowsRequestBody(StrictModel):
    data: list[MatrixRowInputByNameRequestBody] = Field(default=..., description="Array of row objects to create or update. Each row must include an external_key field to identify whether it should be created or updated. Order is not significant.")
class PutDevApiMatrixPutRowsRequest(StrictModel):
    """Creates new rows or updates existing rows in a matrix table. Rows are identified by their external_key; matching keys update existing rows while new keys create new rows. Result values can be partially updated."""
    path: PutDevApiMatrixPutRowsRequestPath
    body: PutDevApiMatrixPutRowsRequestBody

# Operation: append_matrix_table_cells
class PostDevApiMatrixAppendCellsRequestPath(StrictModel):
    table_name: str = Field(default=..., description="The name of the matrix table where cells will be appended. This identifies which custom record table to update.")
class PostDevApiMatrixAppendCellsRequestBody(StrictModel):
    data: list[MatrixRowInputByNameRequestBody] = Field(default=..., description="An array of row objects, each containing cells to append to many-to-many result columns. Order is preserved as provided. Each row should specify the target row and the cell values to add.")
class PostDevApiMatrixAppendCellsRequest(StrictModel):
    """Append values to many-to-many result columns in a matrix table without replacing existing data. This operation only works with many-to-many relationship columns."""
    path: PostDevApiMatrixAppendCellsRequestPath
    body: PostDevApiMatrixAppendCellsRequestBody

# Operation: remove_matrix_table_cells
class PostDevApiMatrixRemoveCellsRequestPath(StrictModel):
    table_name: str = Field(default=..., description="The name of the matrix table from which cells will be removed.")
class PostDevApiMatrixRemoveCellsRequestBody(StrictModel):
    data: list[MatrixRowInputByNameRequestBody] = Field(default=..., description="An array of row objects specifying which cells to remove from many-to-many result columns. Each row entry identifies the target row and the specific cell values to delete.")
class PostDevApiMatrixRemoveCellsRequest(StrictModel):
    """Remove specific cell values from many-to-many result columns in a matrix table without affecting other data in those rows."""
    path: PostDevApiMatrixRemoveCellsRequestPath
    body: PostDevApiMatrixRemoveCellsRequestBody

# Operation: delete_matrix_row
class DeleteDevApiDeleteMatrixRowRequestPath(StrictModel):
    row_id: str = Field(default=..., description="The unique identifier of the matrix table row to delete.")
    table_name: str = Field(default=..., description="The name of the matrix table containing the row to delete.")
class DeleteDevApiDeleteMatrixRowRequest(StrictModel):
    """Permanently removes a single row from a matrix table by its ID. This operation deletes the specified row and cannot be undone."""
    path: DeleteDevApiDeleteMatrixRowRequestPath

# Operation: list_native_table_columns
class GetDevApiNativeTableColumnRequestPath(StrictModel):
    native_table_name: str = Field(default=..., description="The name of the native Ramp table for which to retrieve custom columns. This identifies the specific table whose column definitions should be listed.")
class GetDevApiNativeTableColumnRequest(StrictModel):
    """Retrieve all custom columns defined for a specified native Ramp table. This operation returns the column metadata and configuration for the given native table."""
    path: GetDevApiNativeTableColumnRequestPath

# Operation: list_native_table_rows
class GetDevApiNativeRowRequestPath(StrictModel):
    native_table_name: str = Field(default=..., description="The name of the Native Ramp table to query for rows.")
class GetDevApiNativeRowRequestQuery(StrictModel):
    include_all_referenced_rows: bool | None = Field(default=None, description="When enabled, includes all referenced rows within each cell instead of a limited subset. Defaults to false.")
    page_size: int | None = Field(default=None, description="Number of rows to return per request, up to a maximum of 100. Defaults to 50.")
    ramp_id: list[str] | None = Field(default=None, description="Filter results to include only rows associated with the specified Ramp object IDs. Provide as an array of IDs.")
class GetDevApiNativeRowRequest(StrictModel):
    """Retrieve rows and their custom column values from a Native Ramp table, with optional filtering by Ramp object IDs and configurable pagination."""
    path: GetDevApiNativeRowRequestPath
    query: GetDevApiNativeRowRequestQuery | None = None

# Operation: update_native_table_rows
class PutDevApiNativeRowRequestPath(StrictModel):
    native_table_name: str = Field(default=..., description="The name of the Native Ramp table where rows will be inserted or updated.")
class PutDevApiNativeRowRequestBody(StrictModel):
    data: list[NativeRowColumnContentsByColumnNameRequestBody] = Field(default=..., description="An array of row objects to insert or update. All objects must contain the same set of column names; use `null` values for columns that should not be set on specific rows.")
class PutDevApiNativeRowRequest(StrictModel):
    """Insert or update rows in a Native Ramp table. Specify the table by name and provide row data with consistent column sets across all entries."""
    path: PutDevApiNativeRowRequestPath
    body: PutDevApiNativeRowRequestBody

# Operation: append_native_table_rows
class PostDevApiAppendNativeRowCellsRequestPath(StrictModel):
    native_table_name: str = Field(default=..., description="The name of the Native Ramp table where rows will be appended or updated.")
class PostDevApiAppendNativeRowCellsRequestBody(StrictModel):
    data: list[NativeRowColumnContentsByColumnNameRequestBody] = Field(default=..., description="An array of row objects to insert or update. Each row must contain the same set of column names. Use null for any column value that should not be set, allowing partial row updates.")
class PostDevApiAppendNativeRowCellsRequest(StrictModel):
    """Append or update rows in a Native Ramp table by providing cell data. Use null values to indicate cells that should not be modified."""
    path: PostDevApiAppendNativeRowCellsRequestPath
    body: PostDevApiAppendNativeRowCellsRequestBody

# Operation: remove_native_table_row_cells
class PostDevApiRemoveNativeRowCellsRequestPath(StrictModel):
    native_table_name: str = Field(default=..., description="The name of the native table from which cells will be removed. This identifies the specific Native Ramp table to modify.")
class PostDevApiRemoveNativeRowCellsRequestBody(StrictModel):
    data: list[NativeRowColumnContentsByColumnNameRequestBody] = Field(default=..., description="Array of row specifications indicating which cells to remove. Each row entry must specify the row identifier and the column names whose cells should be cleared. All entries must use consistent column naming.")
class PostDevApiRemoveNativeRowCellsRequest(StrictModel):
    """Remove specific cells from rows in a Native Ramp table. Specify which cells to clear by providing row identifiers and column names."""
    path: PostDevApiRemoveNativeRowCellsRequestPath
    body: PostDevApiRemoveNativeRowCellsRequestBody

# Operation: list_departments
class GetDepartmentListWithPaginationRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Number of departments to return per page. Must be between 2 and 100 items; defaults to 20 if not specified.")
class GetDepartmentListWithPaginationRequest(StrictModel):
    """Retrieve a paginated list of all departments. Results are returned in pages with a configurable size to support efficient browsing of large department collections."""
    query: GetDepartmentListWithPaginationRequestQuery | None = None

# Operation: create_department
class PostDepartmentListWithPaginationRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the department. This identifier is used to reference the department throughout the system.")
class PostDepartmentListWithPaginationRequest(StrictModel):
    """Create a new department with the specified name. The department will be added to the organization and made available for use in resource allocation and team management."""
    body: PostDepartmentListWithPaginationRequestBody

# Operation: get_department
class GetDepartmentResourceRequestPath(StrictModel):
    department_id: str = Field(default=..., description="The unique identifier of the department to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetDepartmentResourceRequest(StrictModel):
    """Retrieve detailed information about a specific department by its unique identifier."""
    path: GetDepartmentResourceRequestPath

# Operation: update_department
class PatchDepartmentResourceRequestPath(StrictModel):
    department_id: str = Field(default=..., description="The unique identifier of the department to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class PatchDepartmentResourceRequestBody(StrictModel):
    name: str = Field(default=..., description="The new name for the department.")
class PatchDepartmentResourceRequest(StrictModel):
    """Update an existing department's information by its unique identifier. Allows modification of department details such as name."""
    path: PatchDepartmentResourceRequestPath
    body: PatchDepartmentResourceRequestBody

# Operation: create_card_embed_token
class PostRampEmbeddedCardResourceRequestPath(StrictModel):
    card_id: str = Field(default=..., description="The unique identifier of the card for which to create an embed token.")
class PostRampEmbeddedCardResourceRequestBody(StrictModel):
    parent_origin: str = Field(default=..., description="The origin URL where the card will be embedded, specified as a valid HTTP or HTTPS URL with hostname (e.g., https://app.example.com/). Localhost origins are not permitted in production environments.", json_schema_extra={'format': 'url'})
class PostRampEmbeddedCardResourceRequest(StrictModel):
    """Generate an embed initialization token for an activated card, enabling secure embedded card functionality on a specified origin. The card must be in an active state to create the token."""
    path: PostRampEmbeddedCardResourceRequestPath
    body: PostRampEmbeddedCardResourceRequestBody

# Operation: list_entities_with_pagination
class GetEntityListWithPaginationRequestQuery(StrictModel):
    currency: Literal["AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN", "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BOV", "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHE", "CHF", "CHW", "CLF", "CLP", "CNH", "CNY", "COP", "COU", "CRC", "CUC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ERN", "ETB", "EUR", "EURC", "FJD", "FKP", "GBP", "GEL", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "INR", "IQD", "IRR", "ISK", "JMD", "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KPW", "KRW", "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MXV", "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL", "SOS", "SRD", "SSP", "STN", "SVC", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY", "TTD", "TWD", "TZS", "UAH", "UGX", "USD", "USDB", "USDC", "USN", "UYI", "UYU", "UYW", "UZS", "VED", "VES", "VND", "VUV", "WST", "XAD", "XAF", "XAG", "XAU", "XBA", "XBB", "XBC", "XBD", "XCD", "XCG", "XDR", "XOF", "XPD", "XPF", "XPT", "XSU", "XTS", "XUA", "XXX", "YER", "ZAR", "ZMW", "ZWG", "ZWL"] | None = Field(default=None, description="Filter results to entities using a specific currency code (e.g., USD, EUR, GBP). Accepts ISO 4217 currency codes and cryptocurrency variants.")
    entity_name: str | None = Field(default=None, description="Filter results to entities matching a specific name or partial name.")
    is_primary: bool | None = Field(default=None, description="Filter to return only primary entities (true) or only non-primary entities (false).")
    hide_inactive: bool | None = Field(default=None, description="Exclude inactive entities from results. Defaults to false, which includes both active and inactive entities.")
    page_size: int | None = Field(default=None, description="Number of results per page. Must be between 2 and 100 inclusive. Defaults to 20 if not specified.")
    include_deleted_accounts: Any | None = Field(default=None, description="Include deleted accounts in the results.")
class GetEntityListWithPaginationRequest(StrictModel):
    """Retrieve a paginated list of business entities with optional filtering by currency, name, primary status, and active state."""
    query: GetEntityListWithPaginationRequestQuery | None = None

# Operation: get_entity
class GetEntityResourceRequestPath(StrictModel):
    entity_id: str = Field(default=..., description="The unique identifier of the business entity to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetEntityResourceRequestQuery(StrictModel):
    hide_inactive: bool | None = Field(default=None, description="When enabled, excludes inactive entities from the results. Defaults to false, returning all entities regardless of active status.")
class GetEntityResourceRequest(StrictModel):
    """Retrieve a specific business entity by its unique identifier. Optionally filter out inactive entities from the response."""
    path: GetEntityResourceRequestPath
    query: GetEntityResourceRequestQuery | None = None

# Operation: list_item_receipts
class GetItemReceiptsResourceRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Number of results per page, between 2 and 100. Defaults to 20 if not specified.")
    entity_id: str | None = Field(default=None, description="Filter results to a specific business entity using its unique identifier (UUID format).", json_schema_extra={'format': 'uuid'})
    purchase_order_line_item_id: str | None = Field(default=None, description="Filter results to a specific purchase order line item using its unique identifier (UUID format).", json_schema_extra={'format': 'uuid'})
    purchase_order_id: str | None = Field(default=None, description="Filter results to a specific purchase order using its unique identifier (UUID format).", json_schema_extra={'format': 'uuid'})
    include_archived: bool | None = Field(default=None, description="Include archived item receipts in the results. By default, only active receipts are returned.")
class GetItemReceiptsResourceRequest(StrictModel):
    """Retrieve a paginated list of item receipts, optionally filtered by entity, purchase order, or line item. Archived receipts are excluded by default."""
    query: GetItemReceiptsResourceRequestQuery | None = None

# Operation: create_item_receipt
class PostItemReceiptsResourceRequestBody(StrictModel):
    item_receipt_line_items: list[ApiItemReceiptLineItemCreateParamsRequestBody] = Field(default=..., description="Array of line items included in this receipt, each specifying the items received. Order of items in the array is preserved as submitted.")
    item_receipt_number: str = Field(default=..., description="Unique identifier for this item receipt, used to reference and track the receipt in your system.")
    memo: str | None = Field(default=None, description="Optional internal note or comment associated with this item receipt for reference purposes.")
    purchase_order_id: str = Field(default=..., description="The unique identifier (UUID format) of the purchase order this receipt is associated with. The receipt must be linked to an existing purchase order.", json_schema_extra={'format': 'uuid'})
    received_at: str = Field(default=..., description="The date when the vendor delivered or will deliver the goods or services, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
class PostItemReceiptsResourceRequest(StrictModel):
    """Create a new item receipt to record goods or services received from a vendor against a purchase order. This documents the receipt of items and their delivery date."""
    body: PostItemReceiptsResourceRequestBody

# Operation: get_item_receipt
class GetItemReceiptSingleResourceRequestPath(StrictModel):
    item_receipt_id: str = Field(default=..., description="The unique identifier of the item receipt to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetItemReceiptSingleResourceRequest(StrictModel):
    """Retrieve a single item receipt by its unique identifier. Returns the complete receipt details for the specified item receipt."""
    path: GetItemReceiptSingleResourceRequestPath

# Operation: delete_item_receipt
class DeleteItemReceiptSingleResourceRequestPath(StrictModel):
    item_receipt_id: str = Field(default=..., description="The unique identifier (UUID) of the item receipt to delete.", json_schema_extra={'format': 'uuid'})
class DeleteItemReceiptSingleResourceRequest(StrictModel):
    """Permanently delete a specific item receipt by its unique identifier. This action cannot be undone."""
    path: DeleteItemReceiptSingleResourceRequestPath

# Operation: list_spend_limits
class GetSpendLimitListWithPaginationRequestQuery(StrictModel):
    entity_id: str | None = Field(default=None, description="Filter results to limits associated with a specific business entity, specified as a UUID.", json_schema_extra={'format': 'uuid'})
    spend_program_id: str | None = Field(default=None, description="Filter results to limits linked to a specific spend program, specified as a UUID.", json_schema_extra={'format': 'uuid'})
    card_id: str | None = Field(default=None, description="Filter results to limits associated with a specific card, specified as a UUID.", json_schema_extra={'format': 'uuid'})
    user_id: str | None = Field(default=None, description="Filter results to limits owned by a specific user, specified as a UUID.", json_schema_extra={'format': 'uuid'})
    is_terminated: bool | None = Field(default=None, description="When true, return only terminated spend limits; when false or omitted, return active limits.")
    user_access_roles: list[Literal["COORDINATOR", "COOWNER", "MEMBER", "OWNER"]] | None = Field(default=None, description="Filter by user access roles. Accepts one or more values from: OWNER, COOWNER, MEMBER. Can be provided as repeated parameters or comma-separated values. Only limits with matching access types are returned.")
    page_size: int | None = Field(default=None, description="Number of results per page, between 2 and 100 inclusive. Defaults to 20 if not specified.")
class GetSpendLimitListWithPaginationRequest(StrictModel):
    """Retrieve a paginated list of spend limits with optional filtering by entity, program, card, user, termination status, and access roles."""
    query: GetSpendLimitListWithPaginationRequestQuery | None = None

# Operation: create_spend_limit
class PostSpendLimitCreationRequestBody(StrictModel):
    accounting_rules: list[SpendLimitAccountingRulesDataRequestBody] | None = Field(default=None, description="Array of accounting rules to apply to this spend limit. Rules define how spending is categorized and tracked for accounting purposes.")
    idempotency_key: str = Field(default=..., description="A unique identifier (UUID) generated by the client to prevent duplicate limit creation if the request is retried. The server uses this to recognize and deduplicate subsequent attempts of the same request.")
    is_shareable: bool | None = Field(default=None, description="Boolean flag indicating whether this spend limit can be shared and used by multiple users, or is restricted to the owner only.")
    permitted_spend_types: PostSpendLimitCreationBodyPermittedSpendTypes | None = Field(default=None, description="Specifies which types of spending are allowed under this limit. Required when creating a limit without a spend program; ignored if spend_program_id is provided.")
    spend_program_id: str | None = Field(default=None, description="UUID of an existing spend program to associate with this limit. When provided, the limit inherits the program's spending restrictions and cannot override permitted spend types.", json_schema_extra={'format': 'uuid'})
    spending_restrictions: PostSpendLimitCreationBodySpendingRestrictions | None = Field(default=None, description="Custom spending restrictions that define limits, categories, and rules for this limit. Ignored if spend_program_id is provided, as the limit will inherit the program's restrictions instead.")
    user_id: str = Field(default=..., description="UUID of the user who owns and is the primary user of this spend limit.", json_schema_extra={'format': 'uuid'})
class PostSpendLimitCreationRequest(StrictModel):
    """Create a new spend limit for a user. The limit can be associated with an existing spend program (inheriting its restrictions) or created independently with custom spending restrictions and permitted spend types."""
    body: PostSpendLimitCreationRequestBody

# Operation: get_spend_limit_deferred_task_status
class GetSpendLimitDeferredTaskStatusRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the deferred task, provided as a UUID.", json_schema_extra={'format': 'uuid'})
class GetSpendLimitDeferredTaskStatusRequest(StrictModel):
    """Retrieve the current status of a deferred spend limit task. Use this to check the progress and outcome of asynchronous spend limit operations."""
    path: GetSpendLimitDeferredTaskStatusRequestPath

# Operation: get_spend_limit
class GetSpendLimitResourceRequestPath(StrictModel):
    spend_limit_id: str = Field(default=..., description="The unique identifier of the spending limit to retrieve.")
class GetSpendLimitResourceRequest(StrictModel):
    """Retrieve details for a specific spending limit by its ID. Use this to fetch current limit configuration and status."""
    path: GetSpendLimitResourceRequestPath

# Operation: update_spend_limit
class PutSpendLimitResourceRequestPath(StrictModel):
    spend_limit_id: str = Field(default=..., description="The unique identifier of the spend limit to update.")
class PutSpendLimitResourceRequestBody(StrictModel):
    accounting_rules: list[SpendLimitAccountingRulesDataRequestBody] | None = Field(default=None, description="Set or modify accounting rules that apply to all card transactions and reimbursements under this spend limit.")
    existing_expense_policy_agent_exemption_application_rules: Literal["APPLY_TO_ALL", "APPLY_TO_NONE"] | None = Field(default=None, description="Controls how policy agent exemptions apply to existing transactions when is_exempt_from_policy_agent is enabled. Use APPLY_TO_ALL to retroactively exempt all existing transactions, or APPLY_TO_NONE to exempt only future transactions.")
    is_exempt_from_policy_agent: bool | None = Field(default=None, description="When enabled, exempts this spend limit from policy agent review, preventing the policy agent from evaluating transactions against this limit.")
    is_shareable: bool | None = Field(default=None, description="When enabled, allows this spend limit to be shared among multiple users.")
    new_user_id: str | None = Field(default=None, description="Transfer ownership of this spend limit to a different user by providing their user ID.", json_schema_extra={'format': 'uuid'})
    permitted_spend_types: PutSpendLimitResourceBodyPermittedSpendTypes | None = Field(default=None, description="Modify the types of spending permitted under this limit. When provided, all fields of permitted_spend_types must be included; partial updates are not supported.")
    spend_program_id: str | None = Field(default=None, description="Link this spend limit to a spend program, which will override the limit's spending restrictions and permitted spend types with those defined in the program. Pass null to detach the current spend program. This field cannot be combined with other update fields.", json_schema_extra={'format': 'uuid'})
    spending_restrictions: PutSpendLimitResourceBodySpendingRestrictions | None = Field(default=None, description="Modify spending restrictions for this limit. When provided, the entire set of new restrictions must be specified, as they will completely replace all existing restrictions.")
class PutSpendLimitResourceRequest(StrictModel):
    """Update an existing spend limit's configuration, including accounting rules, policy agent exemptions, sharing settings, spending restrictions, and program associations."""
    path: PutSpendLimitResourceRequestPath
    body: PutSpendLimitResourceRequestBody | None = None

# Operation: update_spend_limit_partial
class PatchSpendLimitResourceRequestPath(StrictModel):
    spend_limit_id: str = Field(default=..., description="The unique identifier of the spend limit to update.")
class PatchSpendLimitResourceRequestBody(StrictModel):
    accounting_rules: list[SpendLimitAccountingRulesDataRequestBody] | None = Field(default=None, description="Set or modify accounting rules that apply to all card transactions and reimbursements under this spend limit.")
    existing_expense_policy_agent_exemption_application_rules: Literal["APPLY_TO_ALL", "APPLY_TO_NONE"] | None = Field(default=None, description="Controls how policy agent exemptions apply to existing transactions when is_exempt_from_policy_agent is enabled. Use APPLY_TO_ALL to retroactively exempt all existing transactions, or APPLY_TO_NONE to exempt only future transactions.")
    is_exempt_from_policy_agent: bool | None = Field(default=None, description="When enabled, exempts this spend limit from policy agent review, preventing the policy agent from evaluating transactions against this limit.")
    is_shareable: bool | None = Field(default=None, description="When enabled, allows this spend limit to be shared among multiple users.")
    new_user_id: str | None = Field(default=None, description="Transfer ownership of this spend limit to a different user by providing their user ID.", json_schema_extra={'format': 'uuid'})
    permitted_spend_types: PatchSpendLimitResourceBodyPermittedSpendTypes | None = Field(default=None, description="Modify the types of spending permitted under this limit. When provided, all fields of permitted_spend_types must be included; partial updates are not supported.")
    spend_program_id: str | None = Field(default=None, description="Link this spend limit to a spend program, which will override the limit's spending restrictions and permitted spend types with those defined in the program. Pass null to detach the current spend program. This field cannot be combined with other update fields.", json_schema_extra={'format': 'uuid'})
    spending_restrictions: PatchSpendLimitResourceBodySpendingRestrictions | None = Field(default=None, description="Replace all spending restrictions for this limit with a new set. When provided, the entire set of restrictions must be specified; existing restrictions will be completely overridden.")
class PatchSpendLimitResourceRequest(StrictModel):
    """Update configuration for a spend limit, including accounting rules, policy agent exemptions, sharing settings, spending restrictions, and program associations."""
    path: PatchSpendLimitResourceRequestPath
    body: PatchSpendLimitResourceRequestBody | None = None

# Operation: add_users_to_spend_limit
class PutSpendAllocationAddUsersRequestPath(StrictModel):
    spend_limit_id: str = Field(default=..., description="The unique identifier (UUID) of the spend limit to which users will be added.", json_schema_extra={'format': 'uuid'})
class PutSpendAllocationAddUsersRequestBody(StrictModel):
    user_ids: list[str] | None = Field(default=None, description="Array of user identifiers to add to the shared spend limit. Each entry should be a valid user ID in the system.")
class PutSpendAllocationAddUsersRequest(StrictModel):
    """Add one or more users to a shared spend limit, allowing them to access and manage the allocation together."""
    path: PutSpendAllocationAddUsersRequestPath
    body: PutSpendAllocationAddUsersRequestBody | None = None

# Operation: terminate_spend_limit
class PostSpendLimitTerminationResourceRequestPath(StrictModel):
    spend_limit_id: str = Field(default=..., description="The unique identifier of the spend limit to terminate.")
class PostSpendLimitTerminationResourceRequestBody(StrictModel):
    idempotency_key: str = Field(default=..., description="A unique value (typically a UUID) generated by the client to ensure idempotent request handling. The server uses this to recognize and deduplicate retries of the same request.")
class PostSpendLimitTerminationResourceRequest(StrictModel):
    """Permanently terminate a spend limit by creating an asynchronous task. The operation is idempotent and can be safely retried."""
    path: PostSpendLimitTerminationResourceRequestPath
    body: PostSpendLimitTerminationResourceRequestBody

# Operation: remove_users_from_spend_limit
class DeleteSpendAllocationDeleteUsersRequestPath(StrictModel):
    spend_limit_id: str = Field(default=..., description="The unique identifier (UUID) of the spend limit from which users will be removed.", json_schema_extra={'format': 'uuid'})
class DeleteSpendAllocationDeleteUsersRequestBody(StrictModel):
    user_ids: list[str] | None = Field(default=None, description="Array of user identifiers to remove from the spend limit. If omitted, no users are removed.")
class DeleteSpendAllocationDeleteUsersRequest(StrictModel):
    """Remove one or more users from a shared spend limit, revoking their access to that limit's budget allocation."""
    path: DeleteSpendAllocationDeleteUsersRequestPath
    body: DeleteSpendAllocationDeleteUsersRequestBody | None = None

# Operation: suspend_spend_limit
class PostSpendLimitSuspensionResourceRequestPath(StrictModel):
    spend_limit_id: str = Field(default=..., description="The unique identifier of the spend limit to suspend.")
class PostSpendLimitSuspensionResourceRequest(StrictModel):
    """Suspend an active spend limit to temporarily halt enforcement of spending restrictions without deleting the limit configuration."""
    path: PostSpendLimitSuspensionResourceRequestPath

# Operation: unsuspend_spend_limit
class PostSpendLimitUnsuspensionResourceRequestPath(StrictModel):
    spend_limit_id: str = Field(default=..., description="The unique identifier of the spend limit to unsuspend.")
class PostSpendLimitUnsuspensionResourceRequest(StrictModel):
    """Reactivate a suspended spending limit, allowing it to enforce restrictions again."""
    path: PostSpendLimitUnsuspensionResourceRequestPath

# Operation: list_locations
class GetLocationListResourceRequestQuery(StrictModel):
    entity_id: str | None = Field(default=None, description="Filter results to locations associated with a specific business entity, specified as a UUID.", json_schema_extra={'format': 'uuid'})
    page_size: int | None = Field(default=None, description="Number of results per page, between 2 and 100 inclusive. Defaults to 20 if not specified.")
class GetLocationListResourceRequest(StrictModel):
    """Retrieve a paginated list of business locations, optionally filtered by a specific business entity."""
    query: GetLocationListResourceRequestQuery | None = None

# Operation: create_location
class PostLocationListResourceRequestBody(StrictModel):
    entity_id: str | None = Field(default=None, description="UUID identifier of the business entity this location belongs to. If not provided, the location may be created under a default or current entity context.", json_schema_extra={'format': 'uuid'})
    name: str = Field(default=..., description="The display name for the location. This is a required field that uniquely identifies the location within its entity.")
class PostLocationListResourceRequest(StrictModel):
    """Create a new location for a business entity. The location will be associated with the specified entity and identified by the provided name."""
    body: PostLocationListResourceRequestBody

# Operation: get_location
class GetLocationSingleResourceRequestPath(StrictModel):
    location_id: str = Field(default=..., description="The unique identifier of the location to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetLocationSingleResourceRequest(StrictModel):
    """Retrieve a specific location by its unique identifier. Returns detailed information about the requested location."""
    path: GetLocationSingleResourceRequestPath

# Operation: update_location
class PatchLocationSingleResourceRequestPath(StrictModel):
    location_id: str = Field(default=..., description="The unique identifier of the location to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class PatchLocationSingleResourceRequestBody(StrictModel):
    entity_id: str | None = Field(default=None, description="The UUID of the business entity this location belongs to. Provide this to reassign the location to a different entity.", json_schema_extra={'format': 'uuid'})
    name: str = Field(default=..., description="The updated name for the location.")
class PatchLocationSingleResourceRequest(StrictModel):
    """Update an existing location's details, including its name and associated business entity. Provide the location ID and the fields you want to update."""
    path: PatchLocationSingleResourceRequestPath
    body: PatchLocationSingleResourceRequestBody

# Operation: list_memos
class GetMemoListWithPaginationRequestQuery(StrictModel):
    card_id: str | None = Field(default=None, description="Filter results to memos associated with a specific card. Provide the card's UUID.", json_schema_extra={'format': 'uuid'})
    department_id: str | None = Field(default=None, description="Filter results to memos associated with a specific department. Provide the department's UUID.", json_schema_extra={'format': 'uuid'})
    location_id: str | None = Field(default=None, description="Filter results to memos associated with a specific location. Provide the location's UUID.", json_schema_extra={'format': 'uuid'})
    merchant_id: str | None = Field(default=None, description="Filter results to memos associated with a specific merchant. Provide the merchant's UUID.", json_schema_extra={'format': 'uuid'})
    user_id: str | None = Field(default=None, description="Filter results to memos associated with a specific user. Provide the user's UUID.", json_schema_extra={'format': 'uuid'})
    page_size: int | None = Field(default=None, description="Number of memos to return per page. Must be between 2 and 100 inclusive. Defaults to 20 if not specified.")
class GetMemoListWithPaginationRequest(StrictModel):
    """Retrieve a paginated list of memos with optional filtering by card, department, location, merchant, or user. Results are returned in pages with configurable size."""
    query: GetMemoListWithPaginationRequestQuery | None = None

# Operation: get_memo
class GetMemoSingleResourceRequestPath(StrictModel):
    transaction_id: str = Field(default=..., description="The unique identifier of the transaction in UUID format.", json_schema_extra={'format': 'uuid'})
class GetMemoSingleResourceRequest(StrictModel):
    """Retrieve a transaction memo by its unique identifier. Returns the memo details associated with the specified transaction."""
    path: GetMemoSingleResourceRequestPath

# Operation: create_memo_for_transaction
class PostMemoCreateSingleResourceRequestPath(StrictModel):
    transaction_id: str = Field(default=..., description="The unique identifier of the transaction to which the memo will be attached. Must be a valid UUID format.", json_schema_extra={'format': 'uuid'})
class PostMemoCreateSingleResourceRequestBody(StrictModel):
    memo: str = Field(default=..., description="The text content of the memo. Limited to a maximum of 255 characters.", max_length=255)
class PostMemoCreateSingleResourceRequest(StrictModel):
    """Create and attach a new memo to a specific transaction. The memo text is limited to 255 characters and serves as a note or annotation for the transaction record."""
    path: PostMemoCreateSingleResourceRequestPath
    body: PostMemoCreateSingleResourceRequestBody

# Operation: list_merchants
class GetMerchantListWithPaginationRequestQuery(StrictModel):
    transaction_from_date: str | None = Field(default=None, description="Filter results to include only merchants with transactions on or after this date. Specify as an ISO 8601 datetime string.", json_schema_extra={'format': 'date-time'})
    transaction_to_date: str | None = Field(default=None, description="Filter results to include only merchants with transactions on or before this date. Specify as an ISO 8601 datetime string.", json_schema_extra={'format': 'date-time'})
    page_size: int | None = Field(default=None, description="Number of merchants to return per page. Must be between 2 and 100 inclusive; defaults to 20 if not specified.")
class GetMerchantListWithPaginationRequest(StrictModel):
    """Retrieve a paginated list of merchants, optionally filtered by transaction date range. Use pagination parameters to control result set size."""
    query: GetMerchantListWithPaginationRequestQuery | None = None

# Operation: list_purchase_orders
class GetPurchaseOrdersResourceRequestQuery(StrictModel):
    creation_source: Literal["ACCOUNTING_PROVIDER", "DEVELOPER_API", "RAMP"] | None = Field(default=None, description="Filter purchase orders by their creation source: ACCOUNTING_PROVIDER (imported from accounting software), DEVELOPER_API (created via API), or RAMP (created through Ramp platform).")
    receipt_status: Literal["FULLY_RECEIVED", "NOT_RECEIVED", "OVER_RECEIVED", "PARTIALLY_RECEIVED"] | None = Field(default=None, description="Filter purchase orders by receipt status: NOT_RECEIVED (no items received), PARTIALLY_RECEIVED (some items received), FULLY_RECEIVED (all items received), or OVER_RECEIVED (more items received than ordered).")
    page_size: int | None = Field(default=None, description="Number of results per page, between 2 and 100. Defaults to 20 if not specified.")
    entity_id: str | None = Field(default=None, description="Filter results to purchase orders associated with a specific business entity using its unique identifier.", json_schema_extra={'format': 'uuid'})
    spend_request_id: str | None = Field(default=None, description="Filter results to purchase orders linked to a specific spend request using its unique identifier.", json_schema_extra={'format': 'uuid'})
    three_way_match_enabled: bool | None = Field(default=None, description="Filter to include only purchase orders where three-way match (PO, receipt, and invoice reconciliation) is enabled. Defaults to false.")
    include_archived: bool | None = Field(default=None, description="Include archived purchase orders in results. By default, only active purchase orders are returned.")
class GetPurchaseOrdersResourceRequest(StrictModel):
    """Retrieve a paginated list of purchase orders with optional filtering by creation source, receipt status, entity, spend request, and three-way match configuration. Supports inclusion of archived purchase orders."""
    query: GetPurchaseOrdersResourceRequestQuery | None = None

# Operation: create_purchase_order
class PostPurchaseOrdersResourceRequestBody(StrictModel):
    accounting_field_selections: list[ApiCreateAccountingFieldParamsRequestBody] | None = Field(default=None, description="List of accounting field selections to code the purchase order for financial tracking. Typically only one vendor accounting field is applied per purchase order.")
    currency: Literal["AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN", "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BOV", "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHE", "CHF", "CHW", "CLF", "CLP", "CNH", "CNY", "COP", "COU", "CRC", "CUC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ERN", "ETB", "EUR", "EURC", "FJD", "FKP", "GBP", "GEL", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "INR", "IQD", "IRR", "ISK", "JMD", "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KPW", "KRW", "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MXV", "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL", "SOS", "SRD", "SSP", "STN", "SVC", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY", "TTD", "TWD", "TZS", "UAH", "UGX", "USD", "USDB", "USDC", "USN", "UYI", "UYU", "UYW", "UZS", "VED", "VES", "VND", "VUV", "WST", "XAD", "XAF", "XAG", "XAU", "XBA", "XBB", "XBC", "XBD", "XCD", "XCG", "XDR", "XOF", "XPD", "XPF", "XPT", "XSU", "XTS", "XUA", "XXX", "YER", "ZAR", "ZMW", "ZWG", "ZWL"] = Field(default=..., description="The currency code for the purchase order amount. Must be a valid ISO 4217 currency code (e.g., USD, EUR, GBP).")
    entity_id: str = Field(default=..., description="The UUID of the business entity associated with this purchase order.", json_schema_extra={'format': 'uuid'})
    line_items: list[ApiPurchaseOrderLineItemCreateParamsRequestBody] = Field(default=..., description="Array of line items detailing the goods or services being purchased. Each item should include quantity, description, and unit price information.")
    memo: str | None = Field(default=None, description="Optional internal memo or notes for the purchase order.")
    net_payment_terms: int | None = Field(default=None, description="Number of days after invoice receipt within which payment must be made to the vendor.")
    promise_date: str | None = Field(default=None, description="The expected delivery date for goods or services from the vendor, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    purchase_order_number: str | None = Field(default=None, description="Unique purchase order identifier with format prefix-number. Prefixes may contain only numbers, uppercase letters, and dashes; invalid characters are automatically removed. If omitted, a number is auto-generated using the procurement settings prefix.")
    spend_end_date: str | None = Field(default=None, description="The end date for authorized spending under this purchase order, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    spend_start_date: str | None = Field(default=None, description="The start date for authorized spending under this purchase order, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    three_way_match_enabled: bool = Field(default=..., description="Whether three-way matching is required for this purchase order. When enabled, an item receipt must be attached to confirm goods were received before payment.")
    vendor_id: str | None = Field(default=None, description="The UUID of the vendor supplying the goods or services for this purchase order.", json_schema_extra={'format': 'uuid'})
class PostPurchaseOrdersResourceRequest(StrictModel):
    """Create a new purchase order for a business entity with specified line items, vendor, and payment terms. Supports optional three-way matching for receipt verification and accounting field coding."""
    body: PostPurchaseOrdersResourceRequestBody

# Operation: get_purchase_order
class GetPurchaseOrderSingleResourceRequestPath(StrictModel):
    purchase_order_id: str = Field(default=..., description="The unique identifier of the purchase order to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetPurchaseOrderSingleResourceRequest(StrictModel):
    """Retrieve a single purchase order by its unique identifier. Returns the complete purchase order details including line items, pricing, and status information."""
    path: GetPurchaseOrderSingleResourceRequestPath

# Operation: update_purchase_order
class PatchPurchaseOrderSingleResourceRequestPath(StrictModel):
    purchase_order_id: str = Field(default=..., description="The unique identifier of the purchase order to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class PatchPurchaseOrderSingleResourceRequestBody(StrictModel):
    accounting_field_selections: list[ApiCreateAccountingFieldParamsRequestBody] | None = Field(default=None, description="List of accounting field options to assign for coding the purchase order at the body level. Updates are applied in an all-or-nothing manner; typically only a single vendor accounting field is supported per purchase order.")
    spend_end_date: str | None = Field(default=None, description="The end date for spending on this purchase order, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    spend_start_date: str | None = Field(default=None, description="The start date for spending on this purchase order, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
class PatchPurchaseOrderSingleResourceRequest(StrictModel):
    """Update an approved purchase order's spending dates and accounting field selections. Changes to accounting fields are applied atomically—all selections must be valid or the entire update will be rejected."""
    path: PatchPurchaseOrderSingleResourceRequestPath
    body: PatchPurchaseOrderSingleResourceRequestBody | None = None

# Operation: archive_purchase_order
class PostPurchaseOrderArchiveResourceRequestPath(StrictModel):
    purchase_order_id: str = Field(default=..., description="The unique identifier (UUID) of the purchase order to archive.", json_schema_extra={'format': 'uuid'})
class PostPurchaseOrderArchiveResourceRequestBody(StrictModel):
    archived_reason: str | None = Field(default=None, description="Optional reason documenting why the purchase order is being archived.")
class PostPurchaseOrderArchiveResourceRequest(StrictModel):
    """Archive a purchase order by its ID, optionally recording the reason for archival. Archived purchase orders are removed from active workflows but retained for historical records."""
    path: PostPurchaseOrderArchiveResourceRequestPath
    body: PostPurchaseOrderArchiveResourceRequestBody | None = None

# Operation: add_line_items_to_purchase_order
class PostPurchaseOrderLineItemsResourceRequestPath(StrictModel):
    purchase_order_id: str = Field(default=..., description="The unique identifier of the purchase order to which line items will be added.")
class PostPurchaseOrderLineItemsResourceRequestBody(StrictModel):
    line_items: list[ApiPurchaseOrderLineItemCreateParamsRequestBody] = Field(default=..., description="An array of line item objects to add to the purchase order. Each item represents a product or service to be included in the order. The order of items in the array is preserved.")
class PostPurchaseOrderLineItemsResourceRequest(StrictModel):
    """Add one or more line items to an existing purchase order. Existing line items remain unchanged; only new items are appended."""
    path: PostPurchaseOrderLineItemsResourceRequestPath
    body: PostPurchaseOrderLineItemsResourceRequestBody

# Operation: update_purchase_order_line_item
class PatchPurchaseOrderLineItemSingleResourceRequestPath(StrictModel):
    line_item_id: str = Field(default=..., description="The unique identifier of the line item to update.")
    purchase_order_id: str = Field(default=..., description="The unique identifier of the purchase order containing the line item.")
class PatchPurchaseOrderLineItemSingleResourceRequestBody(StrictModel):
    accounting_field_selections: list[ApiCreateAccountingFieldParamsRequestBody] | None = Field(default=None, description="List of accounting field options to assign to this line item for coding purposes. Updates are applied atomically—all selections must be valid or the entire operation fails.")
    description: str | None = Field(default=None, description="Text description of the line item contents or purpose.")
    unit_price: str | None = Field(default=None, description="Unit price for the line item. Accepts numeric values or numeric strings.")
    unit_quantity: int | None = Field(default=None, description="Quantity of units for the line item. Must be a positive integer.")
class PatchPurchaseOrderLineItemSingleResourceRequest(StrictModel):
    """Update a single line item on an approved purchase order. Modify pricing, quantity, description, or accounting field assignments for the line item."""
    path: PatchPurchaseOrderLineItemSingleResourceRequestPath
    body: PatchPurchaseOrderLineItemSingleResourceRequestBody | None = None

# Operation: delete_purchase_order_line_item
class DeletePurchaseOrderLineItemSingleResourceRequestPath(StrictModel):
    line_item_id: str = Field(default=..., description="The unique identifier of the line item to be deleted from the purchase order.")
    purchase_order_id: str = Field(default=..., description="The unique identifier of the purchase order containing the line item to be deleted.")
class DeletePurchaseOrderLineItemSingleResourceRequest(StrictModel):
    """Remove a single line item from an approved purchase order. The purchase order must be in an approved state before line items can be deleted."""
    path: DeletePurchaseOrderLineItemSingleResourceRequestPath

# Operation: list_receipt_integration_opted_out_emails
class GetReceiptIntegrationOptedOutEmailsListResourceRequestBody(StrictModel):
    email: str | None = Field(default=None, description="Filter results to a specific email address. Must be a valid email format.", json_schema_extra={'format': 'email'})
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="Filter results to a specific receipt integration by its unique identifier (UUID format).", json_schema_extra={'format': 'uuid'})
class GetReceiptIntegrationOptedOutEmailsListResourceRequest(StrictModel):
    """Retrieve a list of email addresses that have opted out of receipt integrations. Optionally filter results by a specific email address or integration ID."""
    body: GetReceiptIntegrationOptedOutEmailsListResourceRequestBody | None = None

# Operation: remove_opted_out_email_from_receipt_integration
class DeleteReceiptIntegrationOptedOutEmailsDeleteResourceRequestPath(StrictModel):
    mailbox_opted_out_email_uuid: str = Field(default=..., description="The unique identifier (UUID) of the opted-out email record to remove from the opt-out list.")
class DeleteReceiptIntegrationOptedOutEmailsDeleteResourceRequest(StrictModel):
    """Remove an email address from the receipt integration opt-out list, allowing it to receive receipt integrations again."""
    path: DeleteReceiptIntegrationOptedOutEmailsDeleteResourceRequestPath

# Operation: list_receipts
class GetReceiptListRequestQuery(StrictModel):
    reimbursement_id: str | None = Field(default=None, description="Filter results to receipts associated with a specific reimbursement using its unique identifier.", json_schema_extra={'format': 'uuid'})
    transaction_id: str | None = Field(default=None, description="Filter results to receipts associated with a specific transaction using its unique identifier.", json_schema_extra={'format': 'uuid'})
    page_size: int | None = Field(default=None, description="Number of receipts to return per page. Must be between 2 and 100 results; defaults to 20 if not specified.")
class GetReceiptListRequest(StrictModel):
    """Retrieve a paginated list of receipts, optionally filtered by reimbursement or transaction. Use pagination to control result set size."""
    query: GetReceiptListRequestQuery | None = None

# Operation: upload_receipt
class PostReceiptUploadRequestBody(StrictModel):
    idempotency_key: str = Field(default=..., description="A unique identifier (UUID) that prevents duplicate uploads. Use a UUID to ensure idempotency across retries.")
    transaction_id: str | None = Field(default=None, description="Optional UUID of the transaction to attach this receipt to. If omitted, Ramp will attempt to automatically match the receipt to the most relevant transaction.", json_schema_extra={'format': 'uuid'})
    user_id: str = Field(default=..., description="UUID of the user associated with this receipt. This affects the priority and accuracy of automatic transaction matching.", json_schema_extra={'format': 'uuid'})
class PostReceiptUploadRequest(StrictModel):
    """Upload a receipt image and optionally link it to a transaction. If a transaction ID is provided, the receipt attaches directly to that transaction; otherwise, Ramp automatically matches the receipt to the most relevant transaction based on context."""
    body: PostReceiptUploadRequestBody

# Operation: get_receipt
class GetReceiptSingleResourceRequestPath(StrictModel):
    receipt_id: str = Field(default=..., description="The unique identifier of the receipt to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetReceiptSingleResourceRequest(StrictModel):
    """Retrieve a single receipt by its unique identifier. Returns the complete receipt details for the specified receipt ID."""
    path: GetReceiptSingleResourceRequestPath

# Operation: list_reimbursements
class GetReimbursementListWithPaginationRequestQuery(StrictModel):
    direction: Literal["BUSINESS_TO_USER", "USER_TO_BUSINESS"] | None = Field(default=None, description="Filter reimbursements by direction: BUSINESS_TO_USER for standard reimbursements (default) or USER_TO_BUSINESS for repayments from users back to the business.")
    sync_status: Literal["NOT_SYNC_READY", "SYNCED", "SYNC_READY"] | None = Field(default=None, description="Filter by synchronization status: NOT_SYNC_READY (not ready for sync), SYNC_READY (ready to sync), or SYNCED (already synchronized).")
    from_transaction_date: str | None = Field(default=None, description="Filter reimbursements by the underlying transaction date, returning only those on or after this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    to_transaction_date: str | None = Field(default=None, description="Filter reimbursements by the underlying transaction date, returning only those on or before this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    awaiting_approval_by_user_id: str | None = Field(default=None, description="Filter for reimbursements awaiting approval from a specific user, identified by their UUID.", json_schema_extra={'format': 'uuid'})
    has_been_approved: bool | None = Field(default=None, description="Filter reimbursements by approval status: true for approved reimbursements, false for unapproved. Omit to return all reimbursements regardless of approval status.")
    trip_id: str | None = Field(default=None, description="Filter reimbursements associated with a specific trip, identified by its UUID.", json_schema_extra={'format': 'uuid'})
    accounting_field_selection_id: str | None = Field(default=None, description="Filter reimbursements by accounting field selection, identified by its UUID. This uniquely identifies an accounting field selection configuration on Ramp.", json_schema_extra={'format': 'uuid'})
    entity_id: str | None = Field(default=None, description="Filter reimbursements by business entity, identified by its UUID.", json_schema_extra={'format': 'uuid'})
    from_submitted_at: str | None = Field(default=None, description="Filter reimbursements by submission date, returning only those submitted on or after this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    to_submitted_at: str | None = Field(default=None, description="Filter reimbursements by submission date, returning only those submitted on or before this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    synced_after: str | None = Field(default=None, description="Filter reimbursements by sync date, returning only those synchronized on or after this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    updated_after: str | None = Field(default=None, description="Filter reimbursements by last update date, returning only those updated on or after this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    page_size: int | None = Field(default=None, description="Number of results per page; must be between 2 and 100. Defaults to 20 if not specified.")
    user_id: str | None = Field(default=None, description="Filter reimbursements by user, identified by their UUID.", json_schema_extra={'format': 'uuid'})
class GetReimbursementListWithPaginationRequest(StrictModel):
    """Retrieve a paginated list of reimbursements with flexible filtering by direction, approval status, dates, and associated entities. Supports filtering by transaction dates, submission dates, sync status, and approval workflows."""
    query: GetReimbursementListWithPaginationRequestQuery | None = None

# Operation: create_mileage_reimbursement
class PostMileageReimbursementResourceRequestBody(StrictModel):
    distance: str = Field(default=..., description="The distance traveled, provided as a numeric value or string. Use distance_units to specify whether this is in kilometers or miles.")
    distance_units: Literal["KILOMETERS", "MILES"] | None = Field(default=None, description="The unit of measurement for the distance: either kilometers or miles. Defaults to miles if not specified.")
    end_location: str | None = Field(default=None, description="The destination location or address where the trip ended.")
    memo: str | None = Field(default=None, description="An optional note or description for the reimbursement request.")
    reimbursee_id: str = Field(default=..., description="The unique identifier (UUID) of the employee requesting reimbursement.", json_schema_extra={'format': 'uuid'})
    start_location: str | None = Field(default=None, description="The starting location or address where the trip began.")
    trip_date: str = Field(default=..., description="The date the trip occurred, formatted as a calendar date (ISO 8601 format).", json_schema_extra={'format': 'date'})
    waypoints: list[str] | None = Field(default=None, description="An optional array of intermediate locations visited during the trip, in order of travel.")
class PostMileageReimbursementResourceRequest(StrictModel):
    """Create a mileage reimbursement request for an employee. Specify the distance traveled, trip date, and reimbursee to generate a reimbursement record."""
    body: PostMileageReimbursementResourceRequestBody

# Operation: upload_receipt_for_reimbursement
class PostReimbursementReceiptUploadRequestBody(StrictModel):
    idempotency_key: str = Field(default=..., description="A unique identifier (UUID) that prevents duplicate receipt uploads. Generate a new UUID for each upload request to ensure idempotency.")
    reimbursee_id: str = Field(default=..., description="The UUID of the employee or user who will be reimbursed for this receipt.", json_schema_extra={'format': 'uuid'})
    reimbursement_id: str | None = Field(default=None, description="The UUID of an existing reimbursement to attach this receipt to. If omitted, Ramp will automatically create a new draft reimbursement by extracting receipt data via OCR.", json_schema_extra={'format': 'uuid'})
class PostReimbursementReceiptUploadRequest(StrictModel):
    """Upload a receipt image for reimbursement processing. The receipt can be linked to an existing reimbursement or used to automatically create a new draft reimbursement via OCR analysis."""
    body: PostReimbursementReceiptUploadRequestBody

# Operation: get_reimbursement
class GetReimbursementResourceRequestPath(StrictModel):
    reimbursement_id: str = Field(default=..., description="The unique identifier of the reimbursement to retrieve.")
class GetReimbursementResourceRequest(StrictModel):
    """Retrieve detailed information about a specific reimbursement by its unique identifier."""
    path: GetReimbursementResourceRequestPath

# Operation: list_spend_programs
class GetSpendProgramResourceRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Number of spend programs to return per page. Must be between 2 and 100 results; defaults to 20 if not specified.")
class GetSpendProgramResourceRequest(StrictModel):
    """Retrieve a paginated list of spend programs. Use the page_size parameter to control how many results are returned per page."""
    query: GetSpendProgramResourceRequestQuery | None = None

# Operation: create_spend_program
class PostSpendProgramResourceRequestBody(StrictModel):
    description: str = Field(default=..., description="A brief explanation of the spend program's purpose and use case.")
    display_name: str = Field(default=..., description="The user-facing name of the spend program that will be displayed in interfaces.")
    icon: Literal["AccountingServicesIcon", "AdvertisingIcon", "CONTRACTORS_AND_PROFESSIONAL_SERVICES", "CUSTOM", "CardIcon", "EducationStipendIcon", "EmployeeRewardsIcon", "GroundTransportationIcon", "LegalFeesIcon", "LodgingIcon", "LunchOrderingIcon", "OnboardingIcon", "PerDiemCardIcon", "SOFTWARE", "SaasSubscriptionIcon", "SoftwareTrialIcon", "SuppliesIcon", "TeamSocialIcon", "TravelExpensesIcon", "VirtualEventIcon", "WellnessIcon", "WorkFromHomeIcon", "advertising", "airlines", "bills", "business", "car_services", "contractor", "education", "entertainment", "event_balloons", "event_virtual", "food", "fuel_and_gas", "general_expense", "general_merchandise", "gift", "government_services", "internet_and_phone", "legal", "lodging", "lodging_room", "newspaper", "office", "physical_card", "procurement_checklist", "procurement_intake", "professional_services", "restaurants", "reward", "saas_software", "shipping", "travel_misc", "wellness"] = Field(default=..., description="A visual icon identifier for the spend program. Choose from predefined category icons (e.g., 'SaasSubscriptionIcon', 'TravelExpensesIcon', 'WellnessIcon') or use 'CUSTOM' for a custom icon. Icons help users quickly identify the program's purpose.")
    is_shareable: bool | None = Field(default=None, description="Whether the spend program can be shared and accessed by multiple users. Defaults to false (single-user only).")
    issuance_rules: PostSpendProgramResourceBodyIssuanceRules | None = Field(default=None, description="Optional rules that control how limits are issued from this program. Define which users or user groups (by department, location, or custom attributes) can request limits or receive them automatically. Set `applies_to_all` to true to grant permissions to all employees, or leave unset if no custom issuance logic is needed.")
    issue_physical_card_if_needed: bool | None = Field(default=None, description="Whether to automatically issue a physical card to users who don't already have one when they join this spend program. Defaults to false.")
    permitted_spend_types: PostSpendProgramResourceBodyPermittedSpendTypes = Field(default=..., description="The types of spending allowed under this program (e.g., software subscriptions, travel, meals). This defines what purchases users can make with funds from this program.")
    spending_restrictions: PostSpendProgramResourceBodySpendingRestrictions = Field(default=..., description="Spending limits and restrictions applied to this program, such as daily/monthly caps, merchant category restrictions, or geographic limitations.")
class PostSpendProgramResourceRequest(StrictModel):
    """Create a new spend program that defines spending policies, restrictions, and issuance rules for a group of users. Spend programs control how funds are allocated, what types of spending are permitted, and whether physical cards should be issued."""
    body: PostSpendProgramResourceRequestBody

# Operation: get_spend_program
class GetSpendProgramSingleResourceRequestPath(StrictModel):
    spend_program_id: str = Field(default=..., description="The unique identifier of the spend program to retrieve.")
class GetSpendProgramSingleResourceRequest(StrictModel):
    """Retrieve detailed information about a specific spend program by its unique identifier."""
    path: GetSpendProgramSingleResourceRequestPath

# Operation: list_statements
class GetStatementListWithPaginationRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Number of statements to return per page. Must be between 2 and 100 results; defaults to 20 if not specified.")
class GetStatementListWithPaginationRequest(StrictModel):
    """Retrieve a paginated list of statements. Use the page_size parameter to control how many results are returned per page."""
    query: GetStatementListWithPaginationRequestQuery | None = None

# Operation: get_statement
class GetStatementResourceRequestPath(StrictModel):
    statement_id: str = Field(default=..., description="The unique identifier of the statement to retrieve. This ID is typically provided when a statement is created or can be obtained from a list of statements.")
class GetStatementResourceRequest(StrictModel):
    """Retrieve a specific statement by its unique identifier. Use this to fetch detailed information about a previously created or stored statement."""
    path: GetStatementResourceRequestPath

# Operation: list_transactions
class GetTransactionsCanonicalListWithPaginationRequestQuery(StrictModel):
    sk_category_id: Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9] | None = Field(default=None, description="Filter transactions by Ramp expense category code. Valid codes range from 1 to 44.")
    department_id: str | None = Field(default=None, description="Filter transactions by department using its unique identifier.", json_schema_extra={'format': 'uuid'})
    limit_id: str | None = Field(default=None, description="Filter transactions by spending limit using its unique identifier.", json_schema_extra={'format': 'uuid'})
    location_id: str | None = Field(default=None, description="Filter transactions by merchant location using its unique identifier.", json_schema_extra={'format': 'uuid'})
    merchant_id: str | None = Field(default=None, description="Filter transactions by merchant using its unique identifier.", json_schema_extra={'format': 'uuid'})
    card_id: str | None = Field(default=None, description="Filter transactions by physical card using its unique identifier.", json_schema_extra={'format': 'uuid'})
    spend_program_id: str | None = Field(default=None, description="Filter transactions by spend program using its unique identifier.", json_schema_extra={'format': 'uuid'})
    statement_id: str | None = Field(default=None, description="Filter transactions by statement using its unique identifier.", json_schema_extra={'format': 'uuid'})
    approval_status: Literal["AWAITING_EMPLOYEE", "AWAITING_EMPLOYEE_CHANGES_REQUESTED", "AWAITING_EMPLOYEE_MISSING_ITEMS", "AWAITING_EMPLOYEE_REPAYMENT_FAILED", "AWAITING_EMPLOYEE_REPAYMENT_REQUESTED", "AWAITING_REVIEWER", "FULLY_APPROVED"] | None = Field(default=None, description="Filter transactions by approval status. Valid statuses include awaiting employee action, awaiting reviewer, or fully approved.")
    user_id: str | None = Field(default=None, description="Filter transactions by cardholder user using their unique identifier.", json_schema_extra={'format': 'uuid'})
    awaiting_approval_by_user_id: str | None = Field(default=None, description="Filter transactions awaiting approval from a specific user using their unique identifier.", json_schema_extra={'format': 'uuid'})
    sync_status: Literal["NOT_SYNC_READY", "SYNCED", "SYNC_READY"] | None = Field(default=None, description="Filter transactions by synchronization status: not ready to sync, already synced, or ready to sync. When set, this supersedes other sync-related filters.")
    has_been_approved: bool | None = Field(default=None, description="Filter to include only transactions that have been approved, or only those that have not been approved. If not specified, returns all transactions regardless of approval status.")
    all_requirements_met_and_approved: bool | None = Field(default=None, description="Filter to include only transactions that are fully approved with all cardholder requirements met (receipts, memos, tracking categories). If not specified, returns all transactions.")
    has_statement: bool | None = Field(default=None, description="Filter to include only transactions with a statement, or only those without a statement. If not specified, returns all transactions.")
    synced_after: str | None = Field(default=None, description="Filter for transactions synced after a specific date and time in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    min_amount: str | None = Field(default=None, description="Filter for transactions with an amount greater than or equal to the specified USD dollar amount. Accepts numeric values.")
    max_amount: str | None = Field(default=None, description="Filter for transactions with an amount less than or equal to the specified USD dollar amount. Accepts numeric values.")
    trip_id: str | None = Field(default=None, description="Filter transactions by trip using its unique identifier.", json_schema_extra={'format': 'uuid'})
    accounting_field_selection_id: str | None = Field(default=None, description="Filter transactions by accounting field selection using its unique identifier.", json_schema_extra={'format': 'uuid'})
    entity_id: str | None = Field(default=None, description="Filter transactions by business entity using its unique identifier.", json_schema_extra={'format': 'uuid'})
    requires_memo: bool | None = Field(default=None, description="When set to true, returns only transactions that require a memo but do not have one. Cannot be set to false.")
    include_merchant_data: bool | None = Field(default=None, description="When set to true, includes all purchase data provided by the merchant in the response.")
    order_by_date_desc: bool | None = Field(default=None, description="When set to true, sorts transactions by user transaction date in descending order (newest first). Note that multiple ordering parameters cannot be used together.")
    order_by_amount_desc: bool | None = Field(default=None, description="When set to true, sorts transactions by amount in descending order (highest first). Note that multiple ordering parameters cannot be used together.")
    page_size: int | None = Field(default=None, description="Number of results to return per page. Must be between 2 and 100; defaults to 20 if not specified.")
class GetTransactionsCanonicalListWithPaginationRequest(StrictModel):
    """Retrieve a paginated list of transactions with support for filtering by various attributes (category, department, user, approval status, etc.) and ordering by date or amount. By default, all transactions except declined ones are returned."""
    query: GetTransactionsCanonicalListWithPaginationRequestQuery | None = None

# Operation: get_transaction
class GetTransactionCanonicalResourceRequestPath(StrictModel):
    transaction_id: str = Field(default=..., description="The unique identifier of the transaction to retrieve.")
class GetTransactionCanonicalResourceRequestQuery(StrictModel):
    include_merchant_data: bool | None = Field(default=None, description="When enabled, includes all purchase data provided by the merchant, such as item details, categories, and merchant-specific metadata.")
class GetTransactionCanonicalResourceRequest(StrictModel):
    """Retrieve detailed information about a specific transaction by its ID. Optionally include merchant-provided purchase data for comprehensive transaction context."""
    path: GetTransactionCanonicalResourceRequestPath
    query: GetTransactionCanonicalResourceRequestQuery | None = None

# Operation: list_transfers_with_pagination
class GetTransferListWithPaginationRequestQuery(StrictModel):
    sync_status: Literal["NOT_SYNC_READY", "SYNCED", "SYNC_READY"] | None = Field(default=None, description="Filter transfers by their synchronization readiness state. Use NOT_SYNC_READY for transfers not yet ready to sync, SYNC_READY for transfers prepared for synchronization, or SYNCED for transfers already synchronized. This parameter takes precedence over has_no_sync_commits if both are provided.")
    status: Literal["ACH_CONFIRMED", "CANCELED", "COMPLETED", "ERROR", "INITIATED", "NOT_ACKED", "NOT_ENOUGH_FUNDS", "PROCESSING_BY_ODFI", "REJECTED_BY_ODFI", "RETURNED_BY_RDFI", "SUBMITTED_TO_FED", "SUBMITTED_TO_RDFI", "UNNECESSARY", "UPLOADED"] | None = Field(default=None, description="Filter transfers by their current processing status in the ACH workflow. Refer to the Transfers Guide for detailed definitions of each status value, which range from initial states like INITIATED through final states like COMPLETED or REJECTED_BY_ODFI.")
    entity_id: str | None = Field(default=None, description="Filter transfers to only those associated with a specific business entity, identified by its UUID.", json_schema_extra={'format': 'uuid'})
    statement_id: str | None = Field(default=None, description="Filter transfers to only those included in a specific statement, identified by its UUID.", json_schema_extra={'format': 'uuid'})
    page_size: int | None = Field(default=None, description="Set the number of transfer records returned per page. Must be between 2 and 100 results per page. Defaults to 20 if not specified.")
class GetTransferListWithPaginationRequest(StrictModel):
    """Retrieve a paginated list of transfer payments with optional filtering by sync status, transfer status, business entity, or statement. Use this to view transfer history and monitor payment processing status."""
    query: GetTransferListWithPaginationRequestQuery | None = None

# Operation: get_transfer
class GetTransferResourceRequestPath(StrictModel):
    transfer_id: str = Field(default=..., description="The unique identifier of the transfer payment to retrieve.")
class GetTransferResourceRequest(StrictModel):
    """Retrieve details of a specific transfer payment by its unique identifier. Use this to check the status, amount, and other metadata of a completed or pending transfer."""
    path: GetTransferResourceRequestPath

# Operation: list_trips
class GetTripListResourceRequestQuery(StrictModel):
    user_ids: list[str] | None = Field(default=None, description="Filter results to include only trips assigned to specific users. Provide an array of user IDs.")
    status: Literal["cancelled", "completed", "ongoing", "upcoming"] | None = Field(default=None, description="Filter trips by their current status: cancelled, completed, ongoing, or upcoming.")
    min_amount: str | None = Field(default=None, description="Show only trips with a total amount greater than or equal to this value. Accepts numeric values.")
    max_amount: str | None = Field(default=None, description="Show only trips with a total amount less than or equal to this value. Accepts numeric values.")
    trip_name: str | None = Field(default=None, description="Filter trips by exact name match.")
    page_size: int | None = Field(default=None, description="Number of results to return per page. Must be between 2 and 100; defaults to 20 if not specified.")
class GetTripListResourceRequest(StrictModel):
    """Retrieve all trips for the business with optional filtering by user, status, amount range, and name. Results are paginated with a configurable page size."""
    query: GetTripListResourceRequestQuery | None = None

# Operation: get_trip
class GetTripSingleResourceRequestPath(StrictModel):
    trip_id: str = Field(default=..., description="The unique identifier of the trip to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetTripSingleResourceRequest(StrictModel):
    """Retrieve detailed information about a specific trip using its unique identifier."""
    path: GetTripSingleResourceRequestPath

# Operation: list_users
class GetUserListWithPaginationRequestQuery(StrictModel):
    employee_id: str | None = Field(default=None, description="Filter results to users with a specific employee ID.")
    role: Literal["AUDITOR", "BUSINESS_ADMIN", "BUSINESS_BOOKKEEPER", "BUSINESS_OWNER", "BUSINESS_USER", "GUEST_USER", "IT_ADMIN"] | None = Field(default=None, description="Filter results to users with a specific role: AUDITOR, BUSINESS_ADMIN, BUSINESS_BOOKKEEPER, BUSINESS_OWNER, BUSINESS_USER, GUEST_USER, or IT_ADMIN.")
    status: Literal["USER_ACTIVE", "USER_INACTIVE", "USER_SUSPENDED"] | None = Field(default=None, description="Filter results by user status: USER_ACTIVE, USER_INACTIVE, or USER_SUSPENDED. If not specified, returns all active and inactive users but excludes suspended users.")
    page_size: int | None = Field(default=None, description="Number of results per page, between 2 and 100. Defaults to 20 if not specified.")
    entity_id: str | None = Field(default=None, description="Filter results to users belonging to a specific business entity, specified as a UUID.", json_schema_extra={'format': 'uuid'})
    department_id: str | None = Field(default=None, description="Filter results to users in a specific department, specified as a UUID.", json_schema_extra={'format': 'uuid'})
    email: str | None = Field(default=None, description="Filter results to users with a specific email address.", json_schema_extra={'format': 'email'})
    location_id: str | None = Field(default=None, description="Filter results to users at a specific location, specified as a UUID.", json_schema_extra={'format': 'uuid'})
class GetUserListWithPaginationRequest(StrictModel):
    """Retrieve a paginated list of users with optional filtering by employee ID, role, status, entity, department, email, or location. Defaults to returning all active and inactive users, excluding suspended users."""
    query: GetUserListWithPaginationRequestQuery | None = None

# Operation: send_user_invite
class PostUserCreationDeferredTaskRequestBody(StrictModel):
    department_id: str | None = Field(default=None, description="UUID of the department to which the employee belongs.", json_schema_extra={'format': 'uuid'})
    direct_manager_id: str | None = Field(default=None, description="UUID of the employee's direct manager.", json_schema_extra={'format': 'uuid'})
    email: str = Field(default=..., description="The employee's email address used for sending the invite and account access.", json_schema_extra={'format': 'email'})
    first_name: str = Field(default=..., description="The employee's first name; limited to 255 characters.", max_length=255)
    idempotency_key: str = Field(default=..., description="A unique identifier generated by the client (preferably a UUID) to ensure idempotent request handling. The server uses this to recognize and deduplicate retries of the same request.")
    is_manager: bool | None = Field(default=None, description="Whether the employee has managerial responsibilities and permissions.")
    last_name: str = Field(default=..., description="The employee's last name; limited to 255 characters.", max_length=255)
    location_id: str | None = Field(default=None, description="UUID of the location to which the employee is assigned. Locations are mapped to entities in a many-to-one relationship.", json_schema_extra={'format': 'uuid'})
    role: Literal["AUDITOR", "BUSINESS_ADMIN", "BUSINESS_BOOKKEEPER", "BUSINESS_OWNER", "BUSINESS_USER", "GUEST_USER", "IT_ADMIN"] = Field(default=..., description="The employee's role within the system. Valid roles are: AUDITOR, BUSINESS_ADMIN, BUSINESS_BOOKKEEPER, BUSINESS_OWNER, BUSINESS_USER, GUEST_USER, or IT_ADMIN. Note that BUSINESS_OWNER cannot be assigned via invite.")
    scheduled_deactivation_date: str | None = Field(default=None, description="The date (in ISO 8601 format) when the user account will be automatically deactivated. For guest users, this defaults to 6 months from invite creation unless explicitly set to null. Cannot be set for admins or owners.", json_schema_extra={'format': 'date'})
class PostUserCreationDeferredTaskRequest(StrictModel):
    """Trigger an asynchronous task to send a user invite via email. The invited user must accept the invite to complete onboarding and gain access to the system."""
    body: PostUserCreationDeferredTaskRequestBody

# Operation: get_deferred_task_status
class GetUserDeferredTaskResourceRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier (UUID) of the deferred task whose status you want to retrieve.", json_schema_extra={'format': 'uuid'})
class GetUserDeferredTaskResourceRequest(StrictModel):
    """Retrieve the current status of a deferred task by its unique identifier. Use this to poll for completion or check the progress of asynchronous operations."""
    path: GetUserDeferredTaskResourceRequestPath

# Operation: get_user
class GetUserResourceRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetUserResourceRequest(StrictModel):
    """Retrieve a specific user's profile and details by their unique identifier."""
    path: GetUserResourceRequestPath

# Operation: update_user
class PatchUserResourceRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class PatchUserResourceRequestBody(StrictModel):
    auto_promote: bool | None = Field(default=None, description="Automatically promote the user's manager to a manager role if they are not already one.")
    department_id: str | None = Field(default=None, description="The unique identifier (UUID) of the department the employee belongs to.", json_schema_extra={'format': 'uuid'})
    direct_manager_id: str | None = Field(default=None, description="The unique identifier (UUID) of the employee's direct manager.", json_schema_extra={'format': 'uuid'})
    first_name: str | None = Field(default=None, description="The employee's first name. Must be at least 1 character long.", min_length=1)
    is_manager: bool | None = Field(default=None, description="Whether the employee has manager-level permissions and responsibilities.")
    last_name: str | None = Field(default=None, description="The employee's last name. Must be at least 1 character long.", min_length=1)
    location_id: str | None = Field(default=None, description="The unique identifier (UUID) of the physical location where the employee is based.", json_schema_extra={'format': 'uuid'})
    role: Literal["AUDITOR", "BUSINESS_ADMIN", "BUSINESS_BOOKKEEPER", "BUSINESS_OWNER", "BUSINESS_USER", "GUEST_USER", "IT_ADMIN"] | None = Field(default=None, description="The employee's role within the organization. Valid roles include: AUDITOR, BUSINESS_ADMIN, BUSINESS_BOOKKEEPER, BUSINESS_OWNER, BUSINESS_USER, GUEST_USER, or IT_ADMIN.")
    scheduled_deactivation_date: str | None = Field(default=None, description="The date (in ISO 8601 format) when the user account will be automatically deactivated. Set to null to remove a scheduled deactivation. Cannot be set for admin or owner roles.", json_schema_extra={'format': 'date'})
class PatchUserResourceRequest(StrictModel):
    """Update user profile information including name, organizational hierarchy, role, and deactivation schedule. Supports partial updates of employee details."""
    path: PatchUserResourceRequestPath
    body: PatchUserResourceRequestBody | None = None

# Operation: deactivate_user
class PatchUserDeactivationResourceRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user to deactivate, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class PatchUserDeactivationResourceRequest(StrictModel):
    """Deactivate a user account, preventing them from logging in, making card purchases, or receiving notifications from Ramp."""
    path: PatchUserDeactivationResourceRequestPath

# Operation: reactivate_user
class PatchUserReactivationResourceRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user to reactivate, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class PatchUserReactivationResourceRequest(StrictModel):
    """Reactivate a deactivated user account, restoring their ability to log in, use their issued cards, and receive Ramp notifications."""
    path: PatchUserReactivationResourceRequestPath

# Operation: create_card_vault
class PostCardVaultCreationRequestBody(StrictModel):
    accounting_rules: list[SpendLimitAccountingRulesDataRequestBody] | None = Field(default=None, description="Array of accounting rules to apply to this card and its spend limit. Rules are applied in the order specified.")
    allowed_overage_percent_override: str | None = Field(default=None, description="Optional override for the maximum overage percentage allowed on this card's spend limit. Must be a decimal value between 0 and 100 (e.g., 10 for 10%). If not provided, the card inherits the overage setting from its spend program or business default.")
    spend_program_id: str | None = Field(default=None, description="UUID of the spend program to associate with this card. When provided, the card automatically inherits the spending restrictions and limits from the program, and any spending_restrictions parameter is ignored.", json_schema_extra={'format': 'uuid'})
    spending_restrictions: PostCardVaultCreationBodySpendingRestrictions | None = Field(default=None, description="Spending restrictions that define where and how this card can be used. Ignored if spend_program_id is provided, as restrictions are inherited from the spend program instead.")
    user_id: str = Field(default=..., description="UUID of the user who will own and use this card. Required to identify the cardholder.", json_schema_extra={'format': 'uuid'})
class PostCardVaultCreationRequest(StrictModel):
    """Create a virtual card with optional spend limits and accounting rules. Requires Vault API access and returns sensitive card details for the specified user."""
    body: PostCardVaultCreationRequestBody

# Operation: get_card_vault_details
class GetCardVaultResourceRequestPath(StrictModel):
    card_id: str = Field(default=..., description="The unique identifier of the card whose sensitive details should be retrieved from the vault.")
class GetCardVaultResourceRequest(StrictModel):
    """Retrieve sensitive details for a stored card from the vault. Requires Vault API access permissions to execute."""
    path: GetCardVaultResourceRequestPath

# Operation: list_vendors
class GetVendorListResourceRequestQuery(StrictModel):
    external_vendor_id: str | None = Field(default=None, description="Filter results to vendors matching this customer-defined external vendor identifier, independent of any accounting system remote IDs.")
    merchant_id: str | None = Field(default=None, description="Filter results to vendors associated with this specific card merchant, identified by UUID.", json_schema_extra={'format': 'uuid'})
    accounting_vendor_remote_ids: list[str] | None = Field(default=None, description="Filter results to vendors whose accounting system remote IDs match any in this comma-separated list of strings.")
    vendor_tracking_category_option_ids: list[str] | None = Field(default=None, description="Filter results to vendors whose accounting field selection IDs match any in this comma-separated list of UUIDs.")
    sk_category_ids: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = Field(default=None, description="Filter results to vendors whose Ramp category codes match any in this comma-separated list of integers.")
    page_size: int | None = Field(default=None, description="Number of vendors to return per page; must be between 2 and 100. Defaults to 20 if not specified.")
    vendor_owner_id: str | None = Field(default=None, description="Filter results to vendors owned by this specific user, identified by UUID.", json_schema_extra={'format': 'uuid'})
    include_subsidiary: bool | None = Field(default=None, description="When enabled, include ERP subsidiary identifiers associated with each vendor in the response, if available. Defaults to false.")
    is_active: bool | None = Field(default=None, description="Filter results to vendors with this active status (true for active vendors, false for inactive).")
    name: str | None = Field(default=None, description="Filter results to vendors whose name matches or contains this value.")
class GetVendorListResourceRequest(StrictModel):
    """Retrieve a paginated list of vendors with optional filtering by external ID, merchant, accounting system mappings, categories, and ownership. Use filters to narrow results to specific vendors matching your business criteria."""
    query: GetVendorListResourceRequestQuery | None = None

# Operation: create_vendor
class PostVendorListResourceRequestBody(StrictModel):
    accounting_vendor_remote_id: str | None = Field(default=None, description="The accounting system remote ID for the vendor. Provide either this or vendor_tracking_category_option_id, but not both.")
    address: PostVendorListResourceBodyAddress | None = Field(default=None, description="The vendor's physical address, including street, city, state, postal code, and country details.")
    business_vendor_contacts: PostVendorListResourceBodyBusinessVendorContacts = Field(default=..., description="Contact information for the vendor, including name, email, phone, and other relevant details. This is required to create the vendor.")
    country: str = Field(default=..., description="The country where the vendor is located. Required field that determines tax and regulatory context.")
    external_vendor_id: str | None = Field(default=None, description="A customer-defined external identifier for the vendor, independent of any accounting system IDs. Useful for tracking vendors across multiple systems.")
    name: str | None = Field(default=None, description="The vendor's business name. Must be at least 1 character long.", min_length=1)
    request_payment_details: bool | None = Field(default=None, description="Whether to request payment details (ACH bank account, international wire transfer, check mailing address) from the vendor. Requires a valid contact email address.")
    request_tax_details: bool | None = Field(default=None, description="Whether to request tax information (Tax Identification Number, federal tax classification, tax address) from the vendor. Requires a valid contact email address.")
    vendor_owner_id: str | None = Field(default=None, description="The UUID of the user who will own and manage this vendor. If not provided, the vendor will be created without an assigned owner.", json_schema_extra={'format': 'uuid'})
    vendor_tracking_category_option_id: str | None = Field(default=None, description="The Ramp unique identifier of an existing accounting vendor to link with this vendor. Provide either this or accounting_vendor_remote_id, but not both.", json_schema_extra={'format': 'uuid'})
class PostVendorListResourceRequest(StrictModel):
    """Create a new vendor that is automatically approved and not subject to existing approval policies. Optionally request payment or tax details from the vendor contact."""
    body: PostVendorListResourceRequestBody

# Operation: list_vendor_agreements
class PostVendorAgreementListResourceRequestBody(StrictModel):
    agreement_custom_records: PostVendorAgreementListResourceBodyAgreementCustomRecords | None = Field(default=None, description="JSON object containing custom record field filters to match against agreement custom records.")
    auto_renews: bool | None = Field(default=None, description="Filter to include only agreements that automatically renew, or exclude them if false.")
    contract_owner_ids: list[str] | None = Field(default=None, description="Filter by one or more contract owner IDs to return only agreements owned by specified users.")
    department_ids: list[str] | None = Field(default=None, description="Filter by one or more department IDs to return only agreements associated with specified departments.")
    end_date_range: PostVendorAgreementListResourceBodyEndDateRange | None = Field(default=None, description="JSON object specifying a relative date range filter for agreement end dates (e.g., within next 30 days).")
    exclude_snoozed: bool | None = Field(default=None, description="When true, exclude agreements that have been snoozed from the results.")
    has_end_date: bool | None = Field(default=None, description="Filter to include only agreements with a defined end date, or exclude them if false.")
    has_pending_expansion_requests: bool | None = Field(default=None, description="Filter to include only agreements with pending expansion requests, or exclude them if false.")
    has_reminders: bool | None = Field(default=None, description="Filter to include only agreements with configured reminders, or exclude them if false.")
    include_archived: bool | None = Field(default=None, description="When true, include archived agreements in results; defaults to false to show only active agreements.")
    is_active: bool | None = Field(default=None, description="Filter to include only currently active agreements, or exclude them if false.")
    is_up_for_renewal: bool | None = Field(default=None, description="Filter to include only agreements that are up for renewal, or exclude them if false.")
    last_date_to_terminate_range: PostVendorAgreementListResourceBodyLastDateToTerminateRange | None = Field(default=None, description="JSON object specifying a relative date range filter for the last date to terminate an agreement (e.g., within next 60 days).")
    max_days_remaining: int | None = Field(default=None, description="Filter to include only agreements with days remaining less than or equal to this value.")
    max_total_value: str | None = Field(default=None, description="Filter to include only agreements with total contract value less than or equal to this amount. Accepts numeric string or number format.")
    min_days_remaining: int | None = Field(default=None, description="Filter to include only agreements with days remaining greater than or equal to this value.")
    min_total_value: str | None = Field(default=None, description="Filter to include only agreements with total contract value greater than or equal to this amount. Accepts numeric string or number format.")
    page_size: int | None = Field(default=None, description="Number of results per page; must be between 2 and 100, defaults to 20 if not specified.")
    payee_agreement_ids: list[str] | None = Field(default=None, description="Filter by one or more agreement IDs to return only specified agreements.")
    payee_ids: list[str] | None = Field(default=None, description="Filter by one or more vendor (payee) IDs to return only agreements with specified vendors.")
    payee_owner_ids: list[str] | None = Field(default=None, description="Filter by one or more vendor owner IDs to return only agreements owned by specified vendor contacts.")
    renewal_status: list[Literal["CANCELLED", "EXPIRED", "INITIATED", "NOT_STARTED", "REJECTED", "RENEWED"]] | None = Field(default=None, description="Filter by one or more renewal status values to include only agreements with matching renewal statuses.")
    renewal_status_exclude: list[Literal["CANCELLED", "EXPIRED", "INITIATED", "NOT_STARTED", "REJECTED", "RENEWED"]] | None = Field(default=None, description="Exclude agreements with any of the specified renewal statuses from results.")
    start_date_range: PostVendorAgreementListResourceBodyStartDateRange | None = Field(default=None, description="JSON object specifying a relative date range filter for agreement start dates (e.g., within last 90 days).")
class PostVendorAgreementListResourceRequest(StrictModel):
    """Retrieve a paginated list of vendor agreements with flexible filtering by dates, financial values, renewal status, ownership, and custom metadata. Supports inclusion of archived agreements and exclusion of snoozed items."""
    body: PostVendorAgreementListResourceRequestBody | None = None

# Operation: list_vendor_credits
class GetAllVendorCreditsListRequestQuery(StrictModel):
    from_accounting_date: str | None = Field(default=None, description="Filter results to include only vendor credits with an accounting date on or after this date (inclusive). Use ISO 8601 date format.", json_schema_extra={'format': 'date'})
    to_accounting_date: str | None = Field(default=None, description="Filter results to include only vendor credits with an accounting date on or before this date (inclusive). Use ISO 8601 date format.", json_schema_extra={'format': 'date'})
    include_fully_used: bool | None = Field(default=None, description="When false (default), excludes vendor credits marked as fully used from results. Set to true to include them.")
    page_size: int | None = Field(default=None, description="Number of results per page, between 2 and 100. Defaults to 20 if not specified.")
class GetAllVendorCreditsListRequest(StrictModel):
    """Retrieve all vendor credits across all vendors for a business, with optional filtering by accounting date range and credit status."""
    query: GetAllVendorCreditsListRequestQuery | None = None

# Operation: get_vendor_credit
class GetVendorCreditDetailRequestPath(StrictModel):
    vendor_credit_id: str = Field(default=..., description="The unique identifier (UUID) of the vendor credit to retrieve.", json_schema_extra={'format': 'uuid'})
class GetVendorCreditDetailRequest(StrictModel):
    """Retrieve detailed information about a specific vendor credit by its unique identifier."""
    path: GetVendorCreditDetailRequestPath

# Operation: get_vendor
class GetVendorResourceRequestPath(StrictModel):
    vendor_id: str = Field(default=..., description="The unique identifier of the vendor, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetVendorResourceRequest(StrictModel):
    """Retrieve detailed information about a specific vendor by its unique identifier."""
    path: GetVendorResourceRequestPath

# Operation: update_vendor
class PatchVendorResourceRequestPath(StrictModel):
    vendor_id: str = Field(default=..., description="The unique identifier of the vendor to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class PatchVendorResourceRequestBody(StrictModel):
    accounting_vendor_remote_id: str | None = Field(default=None, description="The remote identifier for this vendor in your accounting system. Provide either this or vendor_tracking_category_option_id, but not both.")
    address: PatchVendorResourceBodyAddress | None = Field(default=None, description="The vendor's physical address details.")
    country: str | None = Field(default=None, description="The country where the vendor is located.")
    description: str | None = Field(default=None, description="A descriptive name or label for the vendor.")
    external_vendor_id: str | None = Field(default=None, description="A custom external identifier for the vendor that you define, independent of any accounting system identifiers.")
    is_active: bool | None = Field(default=None, description="Set to true to mark the vendor as active, or false to deactivate it.")
    vendor_tracking_category_option_id: str | None = Field(default=None, description="The unique identifier of the vendor tracking category option, formatted as a UUID. Provide either this or accounting_vendor_remote_id, but not both.", json_schema_extra={'format': 'uuid'})
class PatchVendorResourceRequest(StrictModel):
    """Update vendor details including contact information, identifiers, and active status. Use this to modify an existing vendor's attributes in the system."""
    path: PatchVendorResourceRequestPath
    body: PatchVendorResourceRequestBody | None = None

# Operation: delete_vendor
class DeleteVendorResourceRequestPath(StrictModel):
    vendor_id: str = Field(default=..., description="The unique identifier of the vendor to delete, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class DeleteVendorResourceRequest(StrictModel):
    """Delete a vendor from the system. The vendor must have no associated transactions, bills, contracts, or spend requests to be successfully deleted."""
    path: DeleteVendorResourceRequestPath

# Operation: list_vendor_bank_accounts
class GetVendorBankAccountListResourceRequestPath(StrictModel):
    vendor_id: str = Field(default=..., description="The unique identifier (UUID) of the vendor whose bank accounts you want to retrieve.", json_schema_extra={'format': 'uuid'})
class GetVendorBankAccountListResourceRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="The number of bank accounts to return per page. Must be between 2 and 100 results; defaults to 20 if not specified.")
class GetVendorBankAccountListResourceRequest(StrictModel):
    """Retrieve a paginated list of bank accounts associated with a specific vendor. Use pagination parameters to control result set size."""
    path: GetVendorBankAccountListResourceRequestPath
    query: GetVendorBankAccountListResourceRequestQuery | None = None

# Operation: get_vendor_bank_account
class GetVendorBankAccountResourceRequestPath(StrictModel):
    bank_account_id: str = Field(default=..., description="The unique identifier (UUID) of the vendor whose bank account you want to retrieve.", json_schema_extra={'format': 'uuid'})
    vendor_id: str = Field(default=..., description="The unique identifier (UUID) of the specific bank account to fetch.", json_schema_extra={'format': 'uuid'})
class GetVendorBankAccountResourceRequest(StrictModel):
    """Retrieve detailed information about a specific bank account associated with a vendor. Use this to access bank account details for payment processing or vendor management purposes."""
    path: GetVendorBankAccountResourceRequestPath

# Operation: archive_vendor_bank_account
class PostVendorBankAccountArchiveResourceRequestPath(StrictModel):
    bank_account_id: str = Field(default=..., description="The unique identifier (UUID) of the bank account to archive.", json_schema_extra={'format': 'uuid'})
    vendor_id: str = Field(default=..., description="The unique identifier (UUID) of the vendor that owns the bank account.", json_schema_extra={'format': 'uuid'})
class PostVendorBankAccountArchiveResourceRequestBody(StrictModel):
    replacement_bank_account_id: str | None = Field(default=None, description="The unique identifier (UUID) of the replacement bank account to transfer any associated bills, drafts, or recurring templates to. Required if the account being archived has existing associations.", json_schema_extra={'format': 'uuid'})
class PostVendorBankAccountArchiveResourceRequest(StrictModel):
    """Archive a vendor's bank account. If the account has associated bills, drafts, or recurring templates, you must specify a replacement bank account to transfer them to."""
    path: PostVendorBankAccountArchiveResourceRequestPath
    body: PostVendorBankAccountArchiveResourceRequestBody | None = None

# Operation: list_vendor_contacts
class GetVendorContactListResourceRequestPath(StrictModel):
    vendor_id: str = Field(default=..., description="The unique identifier (UUID) of the vendor whose contacts you want to retrieve.", json_schema_extra={'format': 'uuid'})
class GetVendorContactListResourceRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="The number of contacts to return per page, between 2 and 100. Defaults to 20 if not specified.")
class GetVendorContactListResourceRequest(StrictModel):
    """Retrieve a paginated list of contacts associated with a specific vendor. Use pagination to control the number of results returned per page."""
    path: GetVendorContactListResourceRequestPath
    query: GetVendorContactListResourceRequestQuery | None = None

# Operation: get_vendor_contact
class GetVendorContactResourceRequestPath(StrictModel):
    vendor_contact_id: str = Field(default=..., description="The unique identifier of the vendor contact to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
    vendor_id: str = Field(default=..., description="The unique identifier of the vendor that owns the contact, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetVendorContactResourceRequest(StrictModel):
    """Retrieve a specific contact person associated with a vendor. Requires both the vendor ID and the contact ID to identify the exact contact record."""
    path: GetVendorContactResourceRequestPath

# Operation: list_vendor_credits_by_vendor
class GetVendorCreditsListRequestPath(StrictModel):
    vendor_id: str = Field(default=..., description="The unique identifier (UUID) of the vendor whose credits should be retrieved.", json_schema_extra={'format': 'uuid'})
class GetVendorCreditsListRequestQuery(StrictModel):
    from_accounting_date: str | None = Field(default=None, description="Filter results to include only vendor credits with an accounting date on or after this date (ISO 8601 format). Optional.", json_schema_extra={'format': 'date'})
    to_accounting_date: str | None = Field(default=None, description="Filter results to include only vendor credits with an accounting date on or before this date (ISO 8601 format). Optional.", json_schema_extra={'format': 'date'})
    include_fully_used: bool | None = Field(default=None, description="When true, includes vendor credits marked as fully used in the results. Defaults to false, excluding fully used credits.")
    page_size: int | None = Field(default=None, description="Number of results per page, between 2 and 100. Defaults to 20 if not specified.")
class GetVendorCreditsListRequest(StrictModel):
    """Retrieve a paginated list of vendor credits for a specific vendor, with optional filtering by accounting date range and inclusion of fully used credits."""
    path: GetVendorCreditsListRequestPath
    query: GetVendorCreditsListRequestQuery | None = None

# Operation: add_vendor_bank_account
class PostVendorBankAccountUpdateResourceRequestPath(StrictModel):
    vendor_id: str = Field(default=..., description="The unique identifier of the vendor to add the bank account for. Must be a valid UUID.", json_schema_extra={'format': 'uuid'})
class PostVendorBankAccountUpdateResourceRequestBody(StrictModel):
    account_nickname: str | None = Field(default=None, description="An optional human-readable label for this bank account to help identify it among multiple payment methods.")
    ach_details: PostVendorBankAccountUpdateResourceBodyAchDetails | None = Field(default=None, description="ACH payment details for US bank transfers, including routing and account numbers. Provide this for ACH transfers or wire_details for wire transfers.")
    is_default: bool | None = Field(default=None, description="Set to true to make this the vendor's default payment method. Defaults to false if not specified.")
    wire_details: PostVendorBankAccountUpdateResourceBodyWireDetails | None = Field(default=None, description="Wire transfer payment details for US wire transfers, including routing and account numbers. Provide this for wire transfers or ach_details for ACH transfers.")
class PostVendorBankAccountUpdateResourceRequest(StrictModel):
    """Add or update a bank account for a vendor's payment processing. The account addition may require approval based on your business's configured approval policies."""
    path: PostVendorBankAccountUpdateResourceRequestPath
    body: PostVendorBankAccountUpdateResourceRequestBody | None = None

# Operation: get_webhook_subscription
class GetOutboundWebhookSubscriptionDetailResourceRequestPath(StrictModel):
    webhook_id: str = Field(default=..., description="The unique identifier (UUID) of the webhook subscription to retrieve.", json_schema_extra={'format': 'uuid'})
class GetOutboundWebhookSubscriptionDetailResourceRequest(StrictModel):
    """Retrieve a specific outbound webhook subscription by its unique identifier. Use this to inspect the configuration and status of a webhook."""
    path: GetOutboundWebhookSubscriptionDetailResourceRequestPath

# Operation: delete_webhook
class DeleteOutboundWebhookSubscriptionDetailResourceRequestPath(StrictModel):
    webhook_id: str = Field(default=..., description="The unique identifier of the webhook subscription to delete, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class DeleteOutboundWebhookSubscriptionDetailResourceRequest(StrictModel):
    """Delete a webhook subscription by its unique identifier. This permanently removes the webhook and stops it from receiving events."""
    path: DeleteOutboundWebhookSubscriptionDetailResourceRequestPath

# ============================================================================
# Component Models
# ============================================================================

class AccountingVendor(PermissiveModel):
    code: str | None = Field(None, description="Code of the vendor.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Remote/external ID of accounting vendor in ERP system.")
    name: str = Field(..., description="name of the vendor")

class ApiAccountingCategory(PermissiveModel):
    category_id: str | None = Field(None, description="User-selected category id for transaction.")
    category_name: str | None = Field(None, description="User-selected category name for transaction.")
    tracking_category_remote_id: str | None = None
    tracking_category_remote_name: str | None = None
    tracking_category_remote_type: str | None = None

class ApiAccountingField(PermissiveModel):
    external_id: str = Field(..., description="external id of accounting field; It should uniquely identify an accounting field on the client end.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="ID that uniquely identifies an accounting field within Ramp")
    name: str = Field(..., description="name of accounting field")
    type_: Literal["AMORTIZATION_TEMPLATE", "BILLABLE", "COST_CENTER", "CUSTOMERS_JOBS", "DEFERRAL_CODE", "EXPENSE_ENTITY", "GL_ACCOUNT", "INVENTORY_ITEM", "JOURNAL", "MERCHANT", "NON_ERP", "OTHER", "PROJECT", "REPORTING_TAG", "SUBSIDIARY", "TAX_CODE"] = Field(..., validation_alias="type", serialization_alias="type", description="accounting field type")

class ApiAccountingFieldSelection(PermissiveModel):
    category_info: ApiAccountingField = Field(..., description="information about the accounting category (or accounting field).")
    external_code: str | None = Field(None, description="external code of accounting field option; Code field displayed on the ERP.")
    external_id: str = Field(..., description="external id of accounting field option; It should uniquely identify an accounting field option on the client end.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="ID that uniquely identifies an accounting field option within Ramp")
    name: str = Field(..., description="name of accounting field option")
    provider_name: str | None = Field(..., description="Name of the accounting provider")

class ApiAccountingFieldSelectionSource(PermissiveModel):
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="Describes the type of source that added this selection.")

class ApiAccountingSuccessfulSyncRequestBody(PermissiveModel):
    deep_link_url: str | None = Field(None, description="URL that links to the object in the remote ERP system. Only applicable for bills.", json_schema_extra={'format': 'url'})
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="ID that uniquely identifies the object to sync in Ramp systems.", json_schema_extra={'format': 'uuid'})
    reference_id: str = Field(..., description="ID that uniquely identifies the object to sync in remote ERP systems.")

class ApiAccountingSyncErrorRequestBody(PermissiveModel):
    message: str = Field(..., description="an error message that explains the reason of the sync failure.")

class ApiAccountingFailedSyncRequestBody(PermissiveModel):
    error: ApiAccountingSyncErrorRequestBody = Field(..., description="describes the reason why the sync object failed to sync.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="ID that uniquely identifies a transaction/reimbursement in Ramp systems.", json_schema_extra={'format': 'uuid'})

class ApiAddressResource(PermissiveModel):
    address_line_1: str
    address_line_2: str | None = None
    city: str
    country: str
    postal_code: str
    state: str | None = None

class ApiApplicationPersonAddressParamsRequestBody(PermissiveModel):
    apt_suite: str | None = Field(None, description="Apartment or suite number.")
    city: str | None = Field(None, description="City.")
    country: str | None = Field(None, description="Two-letter country code (e.g. US).", min_length=2, max_length=2)
    postal_code: str | None = Field(None, description="Postal code.")
    state: str | None = Field(None, description="Two-letter state code (e.g. CA).", min_length=2, max_length=2)
    street_address: str | None = Field(None, description="Street address.")

class ApiApplicationPersonParamsRequestBody(PermissiveModel):
    address: ApiApplicationPersonAddressParamsRequestBody | None = Field(None, description="Residential address.")
    birth_date: str | None = Field(None, description="Date of birth in YYYY-MM-DD format.")
    email: str | None = Field(None, description="Email address.", json_schema_extra={'format': 'email'})
    first_name: str | None = Field(None, description="First name.")
    last_name: str | None = Field(None, description="Last name.")
    passport_last_4: str | None = Field(None, description="Last 4 digits of passport number.", min_length=4, max_length=4)
    phone: str | None = Field(None, description="Phone number in E.164 format.")
    ssn_last_4: str | None = Field(None, description="Last 4 digits of SSN.", min_length=4, max_length=4)
    title: str | None = Field(None, description="Job title or role.")

class ApiBillOwner(PermissiveModel):
    first_name: str | None = Field(None, description="Bill owner's first name.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Bill owner's ID.", json_schema_extra={'format': 'uuid'})
    last_name: str | None = Field(None, description="Bill owner's last name.")

class ApiBillTraceId(PermissiveModel):
    descriptor: str | None = Field(None, description="Human-readable description of the trace ID. For example, 'Check Number' or 'ACH Trace ID'.")
    trace_id: str | None = Field(None, description="The unique reference ID to the payment for this bill.")

class ApiBillVendor(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier of the vendor.", json_schema_extra={'format': 'uuid'})
    name: str = Field(..., description="Name of the vendor.")
    remote_code: str | None = Field(None, description="Code of the vendor; usually it is a unique identifier for the vendor in the remote ERP system.")
    remote_id: str | None = Field(None, description="External ID that uniquely identifies the vendor on the client's side.")
    remote_name: str | None = Field(None, description="Name of the vendor.")
    type_: Literal["BUSINESS", "INDIVIDUAL"] | None = Field(None, validation_alias="type", serialization_alias="type")

class ApiCardAccountingRulesDataRequestBody(PermissiveModel):
    tracking_category_id: str = Field(..., json_schema_extra={'format': 'uuid'})
    tracking_category_option_id: str = Field(..., json_schema_extra={'format': 'uuid'})
    tracking_category_option_remote_name: str

class ApiCardPaymentDetailsResource(PermissiveModel):
    spend_limit_id: str | None = Field(None, description="Unique identifier of the spend limit associated with this bill payment.", json_schema_extra={'format': 'uuid'})
    transaction_ids: list[str] | None = Field(None, description="Array of unique identifiers of transactions associated with this bill payment.")

class ApiCardSpendingRestrictionsDump(PermissiveModel):
    amount: float | None = Field(None, description="Amount limit total per interval.")
    auto_lock_date: str | None = Field(..., description="Date to automatically lock the card. Note that this is different from the actual card expiration date. It conforms to ISO8601 format", json_schema_extra={'format': 'date-time'})
    blocked_categories: list[int] | None = Field(None, description="List of [Ramp Category Codes](/developer-api/v1/overview/conventions#ramp-category-codes) blocked for this card.")
    categories: list[int] | None = Field(None, description="List of [Ramp Category Codes](/developer-api/v1/overview/conventions#ramp-category-codes) this card is restricted to.")
    interval: Literal["ANNUAL", "DAILY", "MONTHLY", "QUARTERLY", "TERTIARY", "TOTAL", "WEEKLY", "YEARLY"] | None = Field(None, description="Time interval to apply limit to.")
    suspended: bool | None = Field(None, description="Whether the card has been locked.")
    transaction_amount_limit: float | None = Field(None, description="Max amount limit per transaction.")

class ApiCreateAccountingFieldParamsRequestBody(PermissiveModel):
    field_external_id: str = Field(..., description="Remote ID of accounting field. This is the external ID, likely from ERP system.")
    field_option_external_id: str | None = Field(None, description="Remote ID of accounting field option. This is the external ID, likely from ERP system. Required if free_form_text is not provided.")
    free_form_text: str | None = Field(None, description="Free form text for the accounting field selection. For DATE-type fields, use ISO format (YYYY-MM-DD). Required if field_option_external_id is not provided.", min_length=1)

class ApiCreateBankAccountPaymentParamsRequestBody(PermissiveModel):
    is_same_day: bool | None = Field(False, description="\nEnables same-day delivery for eligible payments. Currently, this functionality is available only for ACH payments.\nSame-day delivery may incur an additional fee. For more details, see the [Ramp Help Center](https://support.ramp.com/hc/en-us/articles/4417836454419-Bill-payment-methods-and-timelines#h_01GYSNEJWEJ1G133138FQZTMVK).\nTo use same-day delivery via the API, your account must first be enabled for this feature. Please contact developer-support@ramp.com to request access before implementing.\n")
    payment_arrival_date: str = Field(..., description="\nThe expected date the payment will arrive in the vendor's bank account.\n\nThe required time and fee to process the payment depends on the payment method. See the [Ramp Help Center](https://support.ramp.com/hc/en-us/articles/4417836454419-Bill-payment-methods-and-timelines) for more information on payment speeds. An error will be thrown if selected date is invalid.\n", json_schema_extra={'format': 'date'})
    source_bank_account_id: str = Field(..., description="Unique identifier of the bank account to pay the bill from. Must be associated with the passed business entity and have usage_type=BILL_PAY_BANK_ACCOUNT.", json_schema_extra={'format': 'uuid'})
    vendor_account_id: str = Field(..., description="Unique identifier of the vendor account to pay the bill to.", json_schema_extra={'format': 'uuid'})

class ApiCreateBillInventoryLineItemParamsRequestBody(PermissiveModel):
    accounting_field_selections: list[ApiCreateAccountingFieldParamsRequestBody] | None = None
    memo: str | None = None
    quantity: str | float = Field(..., ge=0)
    unit_price: str | float = Field(..., ge=0)

class ApiCreateBillLineItemParamsRequestBody(PermissiveModel):
    accounting_field_selections: list[ApiCreateAccountingFieldParamsRequestBody] | None = None
    amount: str | float
    memo: str | None = None

class ApiCreateBillVendorPaymentParamsRequestBody(PermissiveModel):
    is_same_day: bool | None = Field(False, description="\nEnables same-day delivery for eligible payments. Currently, this functionality is available only for ACH payments.\nSame-day delivery may incur an additional fee. For more details, see the [Ramp Help Center](https://support.ramp.com/hc/en-us/articles/4417836454419-Bill-payment-methods-and-timelines#h_01GYSNEJWEJ1G133138FQZTMVK).\nTo use same-day delivery via the API, your account must first be enabled for this feature. Please contact developer-support@ramp.com to request access before implementing.\n")
    payment_arrival_date: str = Field(..., description="\nThe expected date the payment will arrive in the vendor's bank account.\n\nThe required time and fee to process the payment depends on the payment method. See the [Ramp Help Center](https://support.ramp.com/hc/en-us/articles/4417836454419-Bill-payment-methods-and-timelines) for more information on payment speeds. An error will be thrown if selected date is invalid.\n", json_schema_extra={'format': 'date'})
    source_bank_account_id: str = Field(..., description="Unique identifier of the bank account to pay the bill from. Must be associated with the passed business entity and have usage_type=BILL_PAY_BANK_ACCOUNT.", json_schema_extra={'format': 'uuid'})

class ApiCreateCardBillPaymentParamsRequestBody(PermissiveModel):
    spend_limit_id: str = Field(..., description="Unique identifier of the spend limit associated with the matched transaction.", json_schema_extra={'format': 'uuid'})
    transaction_id: str | None = Field(None, description="If already paid, the unique identifier of the bill payment transaction. The bill will be marked as paid with this transaction once approved.", json_schema_extra={'format': 'uuid'})

class ApiCreateManualBillPaymentParamsRequestBody(PermissiveModel):
    manual_payment_method: Literal["CASH", "CHECK", "CROSS_BORDER_PAYMENT", "CRYPTO_WALLET_TRANSFER", "DIRECT_DEBIT", "DOMESTIC_WIRE_TRANSFER", "NON_RAMP_CREDIT_CARD", "OTHER", "PAID_IN_ERP"] = Field(..., description="Manual payment method of the bill. If passed, payment_date must also be passed and the bill will be marked as paid.")
    payment_date: str = Field(..., description="The date the bill is paid. This field is not relevant for one-time card delivery, as limits are created immediately and sent out to the vendor on the due date.", json_schema_extra={'format': 'date'})

class ApiItemReceiptLineItemCreateParamsRequestBody(PermissiveModel):
    purchase_order_line_item_id: str = Field(..., description="Unique identifier of the purchase order line item being received.", json_schema_extra={'format': 'uuid'})
    unit_quantity: int | None = Field(None, description="The number of units of an item received; required for purchase order line items with inventory item accounting field selections.")

class ApiManualPaymentDetailsResource(PermissiveModel):
    manual_payment_method: Literal["CASH", "CHECK", "CROSS_BORDER_PAYMENT", "CRYPTO_WALLET_TRANSFER", "DIRECT_DEBIT", "DOMESTIC_WIRE_TRANSFER", "NON_RAMP_CREDIT_CARD", "OTHER", "PAID_IN_ERP"] = Field(..., description="Manual payment method used for this bill payment.")

class ApiMerchantLocation(PermissiveModel):
    city: str | None = Field(...)
    country: str | None = Field(...)
    postal_code: str | None = Field(...)
    state: str | None = Field(...)

class ApiPurchaseOrderLineItemCreateParamsRequestBody(PermissiveModel):
    accounting_field_selections: list[ApiCreateAccountingFieldParamsRequestBody] | None = Field(None, description="List of accounting field options selected to code the line item.")
    description: str | None = Field(None, description="Description of the line item.")
    unit_price: str | float = Field(..., description="Unit price of the line item.")
    unit_quantity: int = Field(..., description="Quantity of the line item.")

class ApiReimbursementAccountingCategoryInfo(PermissiveModel):
    external_id: str | None = Field(..., description="External ID that uniquely identifies this field in the ERP.")
    id_: str | None = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier for this accounting field within Ramp.")
    name: str | None = Field(..., description="Name of the accounting field.")
    type_: Literal["AMORTIZATION_TEMPLATE", "BILLABLE", "COST_CENTER", "CUSTOMERS_JOBS", "DEFERRAL_CODE", "EXPENSE_ENTITY", "GL_ACCOUNT", "INVENTORY_ITEM", "JOURNAL", "MERCHANT", "NON_ERP", "OTHER", "PROJECT", "REPORTING_TAG", "SUBSIDIARY", "TAX_CODE"] | None = Field(..., validation_alias="type", serialization_alias="type", description="Type of accounting field.")

class ApiReimbursementAccountingFieldSelection(PermissiveModel):
    category_info: ApiReimbursementAccountingCategoryInfo | None = Field(..., description="Information about the parent accounting category.")
    external_code: str | None = Field(..., description="External code displayed in the ERP for this option.")
    external_id: str | None = Field(..., description="External ID that uniquely identifies this option in the ERP.")
    id_: str | None = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier for this option within Ramp.")
    name: str | None = Field(..., description="Name of the accounting field option.")
    provider_name: str | None = Field(..., description="Name of accounting field provider")
    source: ApiAccountingFieldSelectionSource | None = Field(..., description="Source of this accounting coding selection.")
    type_: Literal["AMORTIZATION_TEMPLATE", "BILLABLE", "COST_CENTER", "CUSTOMERS_JOBS", "DEFERRAL_CODE", "EXPENSE_ENTITY", "GL_ACCOUNT", "INVENTORY_ITEM", "JOURNAL", "MERCHANT", "NON_ERP", "OTHER", "PROJECT", "REPORTING_TAG", "SUBSIDIARY", "TAX_CODE"] | None = Field(..., validation_alias="type", serialization_alias="type", description="Type of accounting field.")

class ApiReimbursementAttendee(PermissiveModel):
    name: str = Field(..., description="Full name of the attendee")
    user_id: str | None = Field(..., description="User ID of the attendee, if linked to a Ramp user. Missing if the attendee is not a Ramp user", json_schema_extra={'format': 'uuid'})

class ApiTransactionAccountingCategoryInfo(PermissiveModel):
    external_id: str | None = Field(None, description="External ID of accounting field; It should uniquely identify an accounting field on the ERP.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="ID that uniquely identifies an accounting field within Ramp", json_schema_extra={'format': 'uuid'})
    name: str | None = Field(None, description="Name of accounting field")
    type_: Literal["AMORTIZATION_TEMPLATE", "BILLABLE", "COST_CENTER", "CUSTOMERS_JOBS", "DEFERRAL_CODE", "EXPENSE_ENTITY", "GL_ACCOUNT", "INVENTORY_ITEM", "JOURNAL", "MERCHANT", "NON_ERP", "OTHER", "PROJECT", "REPORTING_TAG", "SUBSIDIARY", "TAX_CODE"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Accounting field type")

class ApiTransactionAccountingFieldSelection(PermissiveModel):
    category_info: ApiTransactionAccountingCategoryInfo | None = Field(None, description="Information about the accounting category (or accounting field).")
    external_code: str | None = Field(None, description="External code of accounting field option; Code field displayed on the ERP.")
    external_id: str | None = Field(None, description="External ID of accounting field option; It should uniquely identify an accounting field option on the ERP.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="ID that uniquely identifies an accounting field option within Ramp", json_schema_extra={'format': 'uuid'})
    name: str | None = Field(None, description="Name of accounting field option")
    provider_name: str = Field(..., description="Name of accounting field provider")
    source: ApiAccountingFieldSelectionSource | None = Field(None, description="Describes the source of the accounting coding selection.")
    type_: Literal["AMORTIZATION_TEMPLATE", "BILLABLE", "COST_CENTER", "CUSTOMERS_JOBS", "DEFERRAL_CODE", "EXPENSE_ENTITY", "GL_ACCOUNT", "INVENTORY_ITEM", "JOURNAL", "MERCHANT", "NON_ERP", "OTHER", "PROJECT", "REPORTING_TAG", "SUBSIDIARY", "TAX_CODE"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Accounting field type")

class ApiTransactionAttendee(PermissiveModel):
    name: str = Field(..., description="Full name of the attendee")
    user_id: str | None = Field(..., description="User ID of the attendee, if linked to a Ramp user. Missing if the attendee is not a Ramp user", json_schema_extra={'format': 'uuid'})

class ApiTransactionCardHolder(PermissiveModel):
    department_id: str | None = Field(None, description="ID of the card holder's department.", json_schema_extra={'format': 'uuid'})
    department_name: str | None = Field(None, description="Name of the card holder's deparment.")
    employee_id: str | None = Field(None, description="User-defined employee ID of the card holder.")
    first_name: str | None = Field(None, description="Card holder's first name.")
    last_name: str | None = Field(None, description="Card holder's last name.")
    location_id: str | None = Field(None, description="ID of the card holder's location.", json_schema_extra={'format': 'uuid'})
    location_name: str | None = Field(None, description="Name of the card holder's location.")
    user_id: str | None = Field(None, description="Card holder's ID.", json_schema_extra={'format': 'uuid'})

class ApiTransactionDeclineDetails(PermissiveModel):
    amount: float | None = None
    reason: Literal["AUTHORIZER", "AUTHORIZER_AP_CARD_VELOCITY_LIMIT", "AUTHORIZER_BUSINESS_LIMIT", "AUTHORIZER_BUSINESS_SUSPENDED", "AUTHORIZER_BUSINESS_VENDOR_BLACKLIST", "AUTHORIZER_CARD_AUTO_LOCK_DATE", "AUTHORIZER_CARD_CATEGORY_BLACKLIST", "AUTHORIZER_CARD_CATEGORY_WHITELIST", "AUTHORIZER_CARD_LIMIT", "AUTHORIZER_CARD_MCC_BLACKLIST", "AUTHORIZER_CARD_MISSING_POLICY_ITEMS", "AUTHORIZER_CARD_NOT_ACTIVATED", "AUTHORIZER_CARD_PARTIALLY_ACTIVATED", "AUTHORIZER_CARD_START_DATE", "AUTHORIZER_CARD_SUSPENDED", "AUTHORIZER_CARD_TASK_SANCTION", "AUTHORIZER_CARD_TOTAL_ACTIVATION_REQUIRED", "AUTHORIZER_CARD_VENDOR_BLACKLIST", "AUTHORIZER_CARD_VENDOR_WHITELIST", "AUTHORIZER_COMMANDO_MODE", "AUTHORIZER_FRAUD", "AUTHORIZER_FREEZE_TRANSACTIONS_RISK", "AUTHORIZER_GLOBAL_MCC_BLACKLIST", "AUTHORIZER_MEMBER_LIMIT", "AUTHORIZER_NON_AP_CARD_VELOCITY_LIMIT", "AUTHORIZER_OOB_BLOCKED_MERCHANT", "AUTHORIZER_OOB_DAILY_BUSINESS_BALANCE", "AUTHORIZER_OOB_DAILY_CARD_SPEND", "AUTHORIZER_RAMP_AUTHORIZATION_METHODS", "AUTHORIZER_RAMP_TRANSACTION_AMOUNT_LIMIT", "AUTHORIZER_RAMP_VENDOR_RESTRICTIONS", "AUTHORIZER_SPEND_ALLOCATION_ARCHIVED_FUNDS", "AUTHORIZER_SPEND_ALLOCATION_MEMBER_SUSPENDED", "AUTHORIZER_SPEND_ALLOCATION_SUSPENDED", "AUTHORIZER_TRANSACTION_AMOUNT_LIMIT", "AUTHORIZER_UNAUTHORIZED_USER", "AUTHORIZER_USER_LIMIT", "AUTHORIZER_USER_SUSPENDED", "BLOCKED_COUNTRY", "CARD_EXPIRED", "CARD_LOST_OR_STOLEN", "CARD_TERMINATED", "CHIP_FAILURE", "FORBIDDEN_CATEGORY", "INSECURE_AUTHORIZATION_METHOD", "INSUFFICIENT_FUNDS", "INVALID_PIN", "MISSING_CVV", "MISSING_EXPIRATION", "MOBILE_WALLET_FAILURE", "MOBILE_WALLET_TOKEN_NOT_FOUND", "MOBILE_WALLET_TOKEN_TERMINATED", "NETWORK_DECLINE_ACCOUNT_VERIFICATION", "NETWORK_DECLINE_ADVICE", "NETWORK_DECLINE_ADVICE_ACQUIRER_ISSUE", "NETWORK_DECLINE_ADVICE_ADDITIONAL_AUTHENTICATION_REQUIRED", "NETWORK_DECLINE_ADVICE_FORCED_STIP_BY_ISSUER", "NETWORK_DECLINE_ADVICE_ISSUER_LOGGED_OFF", "NETWORK_DECLINE_ADVICE_ISSUER_TIMEOUT", "NETWORK_DECLINE_ADVICE_ISSUER_UNAVAILABLE", "NETWORK_DECLINE_ADVICE_PIN_ERROR", "NETWORK_DECLINE_ADVICE_RECURRING_PAYMENT", "NETWORK_DECLINE_ADVICE_SELECTIVE_ACCEPTANCE_SERVICE", "NETWORK_DECLINE_ADVICE_SUSPECTED_FRAUD_TRANSACTION", "NETWORK_DECLINE_ADVICE_TOKEN_PROVISIONING_SERVICE", "NETWORK_DECLINE_ADVICE_VISA_PAYMENT_CONTROLS_RULE", "NOT_ACTIVE", "NOT_ALLOWED", "NO_AUTO_ROUTED_LIMITS_AVAILABLE", "NO_LINKED_SPEND_ALLOCATION", "OFAC_VERIFICATION_NEEDED", "OPEN_TO_BUY_LIMIT", "OTHER", "PIN_BLOCKED", "PIN_TRY_LIMIT_EXCEEDED", "PROCESSOR_CAP", "QUASI_CASH", "ROUTED_TO_TERMINATED_SPEND_ALLOCATION", "STRIPE_WEBHOOK_TIMEOUT", "SUSPECTED_BIN_ATTACK", "SUSPECTED_FRAUD", "THREE_D_SECURE_REQUIRED", "USER_BLOCKED", "USER_TERMINATED", "WRONG_ADDRESS", "WRONG_CVV", "WRONG_EXPIRATION", "WRONG_POSTAL_CODE"] | None = None

class ApiTransactionDispute(PermissiveModel):
    created_at: str | None = Field(None, description="Time at which the dispute is created, presented in ISO8601 format.", json_schema_extra={'format': 'date-time'})
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Uniquely identifies a transaction dispute.", json_schema_extra={'format': 'uuid'})
    memo: str | None = Field(None, description="Free form text regarding the dispute.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="The dispute type; It could be one of the following values: RESOLVED_BY_RAMP, CANCELLED_BY_CUSTOMER, CANCELLED_BY_RAMP, CREATED_MERCHANT_ERROR and CREATED_UNRECOGNIZED_CHARGE.")

class ApiTransactionPolicyViolation(PermissiveModel):
    created_at: str | None = Field(None, description="Time at which the policy violation is created, presented in ISO8601 format.", json_schema_extra={'format': 'date-time'})
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Uniquely identifies a policy violation.", json_schema_extra={'format': 'uuid'})
    memo: str | None = Field(None, description="Free form text regarding the policy violation.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="Type of the policy violation.")

class ApiTransactionPurchaseAutoRental(PermissiveModel):
    check_out: str | None = None
    days: int | None = None

class ApiTransactionPurchaseFlightSegment(PermissiveModel):
    arrival_airport_code: str | None = None
    carrier: str | None = None
    departure_airport_code: str | None = None
    flight_number: str | None = None
    service_class: str | None = None
    stopover_allowed: bool | None = None

class ApiTransactionPurchaseFlightData(PermissiveModel):
    departure_date: str | None = Field(...)
    passenger_name: str | None = None
    segments: list[ApiTransactionPurchaseFlightSegment] | None = Field(...)

class ApiTransactionPurchaseLodging(PermissiveModel):
    check_in: str | None = None
    nights: int | None = Field(...)

class ApiTransactionPurchaseReceiptLineItem(PermissiveModel):
    commodity_code: str | None = Field(...)
    description: str | None = None
    discount: float | None = Field(...)
    quantity: float | None = None
    tax: float | None = Field(...)
    total: float | None = None
    unit_cost: float | None = None

class ApiTransactionPurchaseReceipt(PermissiveModel):
    items: list[ApiTransactionPurchaseReceiptLineItem] | None = None

class ApiTransactionPurchaseData(PermissiveModel):
    auto_rental: ApiTransactionPurchaseAutoRental | None = Field(..., description="Auto rental purchase data provided by the merchant")
    flight: ApiTransactionPurchaseFlightData | None = Field(..., description="Flight purchase data provided by the merchant")
    lodging: ApiTransactionPurchaseLodging | None = Field(..., description="Lodging purchase data provided by the merchant")
    receipt: ApiTransactionPurchaseReceipt | None = Field(..., description="Receipt purchase data provided by the merchant")
    reference: str | None = Field(..., description="Purchase data reference ID provided by the merchant")

class ApiUserCustomField(PermissiveModel):
    name: str = Field(..., description="Name of the custom field")
    value: str = Field(..., description="Value of the custom field")

class ApiVendorBankAccountResource(PermissiveModel):
    account_nickname: str | None = Field(None, description="Nickname of the vendor bank account.")
    currency: Literal["AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN", "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BOV", "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHE", "CHF", "CHW", "CLF", "CLP", "CNH", "CNY", "COP", "COU", "CRC", "CUC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ERN", "ETB", "EUR", "EURC", "FJD", "FKP", "GBP", "GEL", "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "INR", "IQD", "IRR", "ISK", "JMD", "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KPW", "KRW", "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MXV", "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL", "SOS", "SRD", "SSP", "STN", "SVC", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY", "TTD", "TWD", "TZS", "UAH", "UGX", "USD", "USDB", "USDC", "USN", "UYI", "UYU", "UYW", "UZS", "VED", "VES", "VND", "VUV", "WST", "XAD", "XAF", "XAG", "XAU", "XBA", "XBB", "XBC", "XBD", "XCD", "XCG", "XDR", "XOF", "XPD", "XPF", "XPT", "XSU", "XTS", "XUA", "XXX", "YER", "ZAR", "ZMW", "ZWG", "ZWL"] = Field(..., description="Currency of the vendor bank account.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier of the vendor bank account.", json_schema_extra={'format': 'uuid'})
    is_default: bool | None = Field(None, description="Whether this is the payee's default bank account.")
    payment_method: Literal["ACH", "AUTOMATIC_CARD_PAYMENT", "CARD", "CHECK", "CRYPTO_WALLET_TRANSFER", "DOMESTIC_WIRE", "INTERNATIONAL", "LOCAL_BANK_TRANSFER", "ONE_TIME_CARD", "ONE_TIME_CARD_DELIVERY", "PAID_MANUALLY", "RTP", "SWIFT", "UNSPECIFIED", "VENDOR_CREDIT"] = Field(..., description="Supported payment method for the vendor bank account.")

class ApiVendorPaymentDetailsResource(PermissiveModel):
    approval_status: Literal["APPROVED", "INITIALIZED", "PENDING", "REJECTED", "TERMINATED"] | None = Field(..., description="Approval status of the payment, if payment-step approvals are used.")
    is_same_day: bool = Field(..., description="Specifies whether the payment is configured for same-day delivery.")
    source_bank_account_id: str | None = Field(..., description="Unique identifier of the bank account associated with this bill payment, if it exists.", json_schema_extra={'format': 'uuid'})
    vendor_account_id: str | None = Field(..., description="Unique identifier of the vendor account associated with this bill payment, if it exists.", json_schema_extra={'format': 'uuid'})

class CardPersonalizationNameLine(PermissiveModel):
    value: str | None = None

class CardPersonalizationText(PermissiveModel):
    name_line_1: CardPersonalizationNameLine | None = None
    name_line_2: CardPersonalizationNameLine | None = None

class CardPersonalization(PermissiveModel):
    text: CardPersonalizationText | None = None

class CardShippingAddress(PermissiveModel):
    address1: str = Field(..., min_length=1, max_length=50)
    address2: str | None = Field(None, min_length=0, max_length=50)
    city: str
    country: str
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    phone: str | None = None
    postal_code: str
    state: str | None = None

class CardShipping(PermissiveModel):
    method: str | None = None
    recipient_address: CardShippingAddress | None = None
    recipient_address_verification_state: Literal["NOT_VERIFIED", "OVERRIDEN", "VERIFIED"] | None = None
    return_address: CardShippingAddress | None = None

class ApiCardFulfillment(PermissiveModel):
    card_personalization: CardPersonalization | None = None
    cardholder_uuid: str | None = Field(None, json_schema_extra={'format': 'uuid'})
    fulfillment_status: Literal["DELIVERED", "DIGITALLY_PRESENTED", "ISSUED", "ORDERED", "REJECTED", "SHIPPED"] | None = Field(None, description="Fulfillment status of the card")
    shipping: CardShipping | None = None
    shipping_date: str | None = Field(None, description="Date on which the card is shipped out, presented in ISO8601 format", json_schema_extra={'format': 'date-time'})
    shipping_eta: str | None = Field(None, description="Estimated arrival time, presented in ISO8601 format", json_schema_extra={'format': 'date-time'})
    shipping_tracking_url: str | None = Field(None, description="Tracking url")

class Card(PermissiveModel):
    card_program_id: str | None = Field(..., description="Unique identifier of the card program.", json_schema_extra={'format': 'uuid'})
    cardholder_id: str | None = Field(None, description="Unique identifier of the card holder.", json_schema_extra={'format': 'uuid'})
    cardholder_name: str | None = Field(None, description="Card holder's full name.")
    created_at: str | None = Field(None, description="Date time at which the card is created. It conforms to ISO8601 format", json_schema_extra={'format': 'date-time'})
    display_name: str = Field(..., description="Cosmetic display name of the card.")
    entity_id: str | None = Field(None, description="Unique identifier of the associated business entity.", json_schema_extra={'format': 'uuid'})
    expiration: str = Field(..., description="Expiration date in the format of MMYY.")
    fulfillment: ApiCardFulfillment | None = Field(..., description="Fulfillment details of a Ramp card. For physical cards only.")
    has_program_overridden: bool = Field(..., description="Whether the card has overridden the default settings from its card program.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Unique identifier of the card.", json_schema_extra={'format': 'uuid'})
    is_physical: bool | None = None
    last_four: str = Field(..., description="Last four digits of the card number.")
    spending_restrictions: ApiCardSpendingRestrictionsDump | None = Field(..., description="Specifies the spend restrictions on a Ramp card.")
    state: Literal["ACTIVE", "CHIP_LOCKED", "SUSPENDED", "TERMINATED", "UNACTIVATED"] | None = Field(None, description="State of the card")

class CurrencyAmount(PermissiveModel):
    amount: int = Field(..., description="the amount of money represented in the smallest denomination of the currency. For example, when the currency is USD, then the amount is expressed in cents.")
    currency_code: str = Field(..., description="The type of currency, in ISO 4217 format. e.g. USD for US dollars")
    minor_unit_conversion_rate: int | None = Field(..., description="The conversion factor to convert from the integer amount to the actual currency value. Divide amount by this value to get the real currency amount. For USD, this is 100 (e.g., 12034 / 100 = 120.34 USD). See https://docs.ramp.com/developer-api/v1/monetary-values for more information.")

class ApiBillInventoryLineItem(PermissiveModel):
    accounting_field_selections: list[ApiAccountingFieldSelection] = Field(..., description="List of accounting field options selected to code the line item.")
    amount: CurrencyAmount = Field(..., description="Amount of the line item, equal to the product of unit quantity and unit price, represented in the lowest denomination of the currency (e.g., cents for USD).")
    item_receipt_line_item_ids: list[str] = Field(..., description="List of unique identifiers for item receipt line items associated with this bill inventory line item through the purchase order line item")
    memo: str | None = Field(None, description="Memo of the line item")
    purchase_order_line_item_id: str | None = Field(..., description="Unique identifier of the matched purchase order line item, if any", json_schema_extra={'format': 'uuid'})
    quantity: float = Field(..., description="Quantity of the line item")
    unit_price: CurrencyAmount = Field(..., description="Unit price of the line item, represented in the lowest denomination of the currency (e.g., cents for USD).")

class ApiBillLineItem(PermissiveModel):
    accounting_field_selections: list[ApiAccountingFieldSelection] = Field(..., description="List of accounting field options selected to code the line item.")
    amount: CurrencyAmount = Field(..., description="Amount of the line item, represented in the lowest denomination of the currency (e.g., cents for USD).")
    item_receipt_line_item_ids: list[str] = Field(..., description="List of unique identifiers for item receipt line items associated with this bill line item through the purchase order line item")
    memo: str | None = Field(None, description="Memo of the line item")
    purchase_order_line_item_id: str | None = Field(..., description="Unique identifier of the matched purchase order line item, if any", json_schema_extra={'format': 'uuid'})

class ApiBillPayment(PermissiveModel):
    amount: CurrencyAmount = Field(..., description="Paid amount of the bill.")
    customer_friendly_payment_id: str | None = Field(..., description="Customer-friendly payment identifier for non-card payment methods, if available. Bills sharing the same value belong to the same payment or batch payment.")
    details: ApiCardPaymentDetailsResource | ApiManualPaymentDetailsResource | ApiVendorPaymentDetailsResource = Field(..., description="Additional payment details specific to payment method.")
    effective_date: str | None = Field(..., description="For non-card payment methods only, the date the payment is actually initiated.", json_schema_extra={'format': 'date-time'})
    id_: str | None = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier of the payment. Bills sharing the same payment ID belong to the same batch payment.")
    payment_date: str | None = Field(..., description="For non-card payment methods, the date the payment is scheduled to be initiated. For card methods, the settlement date of the latest transaction on card. Additional information about transactions should be accessed through the transactions API.", json_schema_extra={'format': 'date-time'})
    payment_method: Literal["ACH", "AUTOMATIC_CARD_PAYMENT", "CARD", "CHECK", "CRYPTO_WALLET_TRANSFER", "DOMESTIC_WIRE", "INTERNATIONAL", "LOCAL_BANK_TRANSFER", "ONE_TIME_CARD", "ONE_TIME_CARD_DELIVERY", "PAID_MANUALLY", "RTP", "SWIFT", "UNSPECIFIED", "VENDOR_CREDIT"] | None = Field(...)
    trace_id: ApiBillTraceId | None = Field(..., description="For non-card payment methods only, the trace ID for this bill. This field is only returned in the GET /bills/{bill_id} response body (not in the GET /bills paginated query).")

class ApiReimbursementLineItem(PermissiveModel):
    accounting_field_selections: list[ApiReimbursementAccountingFieldSelection] = Field(..., description="Accounting field selections used to code this line item.")
    amount: CurrencyAmount | None = Field(..., description="Amount of the line item.")
    memo: str | None = Field(..., description="Memo text for this line item.")

class ApiTransactionLineItem(PermissiveModel):
    accounting_field_selections: list[ApiTransactionAccountingFieldSelection] | None = Field(None, description="List of accounting field options selected to code the line item.")
    amount: CurrencyAmount | None = Field(..., description="Amount of the line item, denominated in the currency that the transaction was settled in.")
    converted_amount: CurrencyAmount | None = Field(..., description="Amount of the split line item, converted to the currency of the card on which the transaction occurred.")
    memo: str | None = Field(None, description="Memo associated with the line item.")

class BillAppliedVendorCredit(PermissiveModel):
    amount: CurrencyAmount = Field(..., description="Amount of the Vendor Credit applied to this specific bill. This is not necessarily the entire amount of the Vendor Credit itself. Currently only USD is supported for Vendor Credits.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier for the vendor credit")

class Bill(PermissiveModel):
    accounting_date: str = Field(..., description="The date for the bill for accounting purposes. If not specified, falls back to the bill issue date.", json_schema_extra={'format': 'date-time'})
    accounting_field_selections: list[ApiAccountingFieldSelection] = Field(..., description="List of accounting field options selected to code the bill.")
    amount: CurrencyAmount = Field(..., description="Amount of the bill, represented in the lowest denomination of the currency (e.g., cents for USD).")
    applied_vendor_credits: list[BillAppliedVendorCredit] = Field(..., description="Vendor Credits that have been applied to this Bill")
    approval_status: Literal["APPROVED", "INITIALIZED", "PENDING", "REJECTED", "TERMINATED"] | None = Field(..., description="Approval status of the bill. Note that this is separate from the approval status for payment release.")
    archived_at: str | None = Field(..., description="The datetime the bill was archived.", json_schema_extra={'format': 'date-time'})
    bill_owner: ApiBillOwner = Field(..., description="Information about the bill owner.")
    created_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    deep_link_url: str | None = Field(None, description="Link to bill in ERP, if exists.")
    draft_bill_created_at: str | None = Field(..., description="The date the draft bill was created if this bill was created from a draft bill, otherwise None.", json_schema_extra={'format': 'date-time'})
    draft_bill_id: str | None = Field(..., description="Unique identifier of the draft bill this bill was created from, if one exists.", json_schema_extra={'format': 'uuid'})
    due_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    enable_accounting_sync: bool | None = Field(None, description="Flag specifying whether the bill should sync to the ERP")
    entity_id: str = Field(..., description="Associated business entity.", json_schema_extra={'format': 'uuid'})
    fx_conversion_rate: str = Field(..., description="FX conversion rate from bill invoice currency to payer currency.", json_schema_extra={'format': 'decimal'})
    id_: str = Field(..., validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'uuid'})
    inventory_line_items: list[ApiBillInventoryLineItem] = Field(..., description="List of inventory line items related to the bill.")
    invoice_number: str | None = Field(None, description="The invoice number on the bill.")
    invoice_urls: list[str] = Field(..., description="Pre-signed urls to download invoice files.")
    issued_at: str = Field(..., description="The date the bill was issued on invoice.", json_schema_extra={'format': 'date-time'})
    item_receipt_ids: list[str] = Field(..., description="List of unique identifiers for item receipts associated with this bill through matched purchase orders.")
    line_items: list[ApiBillLineItem] = Field(..., description="List of line items related to the bill.")
    memo: str | None = Field(None, description="Memo of the bill.")
    paid_at: str | None = Field(None, description="The datetime the bill's payment status is set to PAID. None if the bill's payment status is OPEN", json_schema_extra={'format': 'date-time'})
    payment: ApiBillPayment | None = Field(..., description="Payment information of the bill.")
    posting_date: str | None = Field(None, description="The date the bill was posted to the ERP. Alternatively known as accounting date, accounting sync date.", json_schema_extra={'format': 'date-time'})
    purchase_order_id: str | None = Field(None, description="Unique identifier of matched purchase order, if one exists.", json_schema_extra={'format': 'uuid'})
    remote_id: str | None = Field(None, description="The external ID that identifies the bill on client's side.")
    status: Literal["OPEN", "PAID"]
    status_summary: Literal["APPROVAL_PENDING", "APPROVAL_REJECTED", "ARCHIVED", "AWAITING_RELEASE", "BLOCKED", "HELD_BY_PROVIDER", "ON_HOLD", "PAYMENT_COMPLETED", "PAYMENT_DETAILS_MISSING", "PAYMENT_ERROR", "PAYMENT_NOT_INSTRUCTED", "PAYMENT_PROCESSING", "PAYMENT_READY", "PAYMENT_SCHEDULED", "PENDING_VENDOR_APPROVAL", "WAITING_FOR_TRANSACTION_MATCH", "WAITING_FOR_VENDOR"] = Field(..., description="Status summary of the bill.")
    sync_status: Literal["BILL_AND_PAYMENT_SYNCED", "BILL_SYNCED", "NOT_SYNCED"] = Field(..., description="Sync status of the bill.")
    vendor: ApiBillVendor = Field(..., description="Vendor information of the bill.")
    vendor_contact_id: str | None = Field(..., description="Unique identifier of associated vendor contact.", json_schema_extra={'format': 'uuid'})
    vendor_memo: str | None = Field(None, description="Memo to the vendor.")

class CustomRowExternalKeyRequestBody(PermissiveModel):
    external_key: str

class DefaultPaymentMethodAddressPolicy(PermissiveModel):
    data: ApiAddressResource
    kind: Literal["ADDRESS", "BANK_ACCOUNT", "CARD", "MANUAL"]

class DefaultPaymentMethodBankAccountPolicy(PermissiveModel):
    data: ApiVendorBankAccountResource
    kind: Literal["ADDRESS", "BANK_ACCOUNT", "CARD", "MANUAL"]

class DefaultPaymentMethodCardPolicy(PermissiveModel):
    card_payment_method: Literal["ACH", "AUTOMATIC_CARD_PAYMENT", "CARD", "CHECK", "CRYPTO_WALLET_TRANSFER", "DOMESTIC_WIRE", "INTERNATIONAL", "LOCAL_BANK_TRANSFER", "ONE_TIME_CARD", "ONE_TIME_CARD_DELIVERY", "PAID_MANUALLY", "RTP", "SWIFT", "UNSPECIFIED", "VENDOR_CREDIT"]
    kind: Literal["ADDRESS", "BANK_ACCOUNT", "CARD", "MANUAL"]

class DefaultPaymentMethodResource(PermissiveModel):
    policy: DefaultPaymentMethodAddressPolicy | DefaultPaymentMethodBankAccountPolicy | DefaultPaymentMethodCardPolicy | None = None
    update_source: Literal["AUTO", "MANUAL"] | None = None

class DeveloperApiMatrixColumnFilterRequestBody(PermissiveModel):
    """Filter for a specific Matrix input column."""
    column_name: str = Field(..., description="API name of the input column to filter on")
    one_of: list[str] = Field(..., description="List of ramp object UUIDs to filter by (matches any)")

class DeveloperApiNativeRowIdentifierRequestBody(PermissiveModel):
    """Identifier for a native Ramp object (e.g., user, department)."""
    column_name: str = Field(..., description="Column name to identify by (e.g., 'id', 'email')")
    value: str = Field(..., description="Value for identification")

class DeveloperApiNativeTableReferenceRequestBody(PermissiveModel):
    """Native table reference for Developer API input columns.

Allows: users, locations, departments, business_entities, and accounting_field_options."""
    accounting_field_ramp_id: str | None = Field(None, description="The accounting field's ramp_id (UUID), only set for accounting_field_options")
    table_name: Literal["accounting_field_options", "business_entities", "departments", "locations", "users"] = Field(..., description="The native table name for input columns: users, locations, departments, business_entities, accounting_field_options.")
    type_: Literal["native_table"] | None = Field('native_table', validation_alias="type", serialization_alias="type")

class DeveloperApiNumberColumnTypeRequestBody(PermissiveModel):
    """Number column type for Developer API input columns."""
    type_: Literal["number"] | None = Field('number', validation_alias="type", serialization_alias="type", description="Column type discriminator")

class DeveloperApiMatrixInputColumnDefRequestBody(PermissiveModel):
    """Schema for defining a Matrix input column (Developer API)."""
    column_type: DeveloperApiNativeTableReferenceRequestBody | DeveloperApiNumberColumnTypeRequestBody = Field(..., description="Defines the type of input field used by the matrix")
    label: str = Field(..., description="Display name for the input column")
    name: str | None = Field(None, description="API name for the column")

class DeveloperApiResultNativeTableReferenceRequestBody(PermissiveModel):
    """Native table reference for Developer API result columns.

Only allows: users and accounting_field_options."""
    accounting_field_ramp_id: str | None = Field(None, description="The accounting field's ramp_id (UUID), only set for accounting_field_options")
    table_name: Literal["accounting_field_options", "users"] = Field(..., description="The native table name for result columns: users or accounting_field_options only.")
    type_: Literal["native_table"] | None = Field('native_table', validation_alias="type", serialization_alias="type")

class DeveloperApiMatrixResultColumnDefRequestBody(PermissiveModel):
    """Schema for defining a Matrix result column (Developer API)."""
    cardinality: Literal["many_to_many", "many_to_one"] = Field(..., description="many_to_one or many_to_many for the result column")
    label: str = Field(..., description="Display name for the result column")
    name: str | None = Field(None, description="API name for the column")
    native_table: DeveloperApiResultNativeTableReferenceRequestBody = Field(..., description="The native table this result references (only users and accounting_field_options supported)")

class FieldOption(PermissiveModel):
    code: str | None = Field(None, description="Code of the custom accounting field option; e.g. 400-100.")
    display_name: str | None = Field(None, description="Set an optional user-facing display name of the custom field option.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Remote/external ID of custom accounting field option from ERP system.")
    value: str = Field(..., description="e.g. Employees:Salaries & Wages")

class GlAccount(PermissiveModel):
    classification: Literal["ANY", "ASSET", "CREDCARD", "EQUITY", "EXPENSE", "LIABILITY", "REVENUE", "UNKNOWN"]
    code: str | None = Field(None, description="e.g. 400-100.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Remote/external ID of GL account in ERP system.")
    name: str = Field(..., description="e.g. Travel : Travel - Lodging.")

class InventoryItemOption(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The external ID of the inventory item option. This is the ID in your ERP system.")
    name: str = Field(..., description="The name of the inventory item option.")

class Location(PermissiveModel):
    entity_id: str = Field(..., description="Identifier of the business entity this location belongs to.", json_schema_extra={'format': 'uuid'})
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier for the location.", json_schema_extra={'format': 'uuid'})
    name: str = Field(..., description="Name of the location.")

class MatrixInputCellByNameRequestBody(PermissiveModel):
    """A Matrix input cell with column name and identifier."""
    column_name: str = Field(..., description="API name of the input column")
    identifier: DeveloperApiNativeRowIdentifierRequestBody | None = Field(None, description="Identifier for the referenced native object (use for native_table columns)")
    number_identifier: float | str | None = Field(None, description="Number value identifier (use for number columns)")

class MatrixResultCellByNameRequestBody(PermissiveModel):
    """A Matrix result cell with column name and identifier (for input requests)."""
    column_name: str = Field(..., description="API name of the result column")
    identifier: DeveloperApiNativeRowIdentifierRequestBody | None = Field(..., description="Identifier for the referenced object (None to clear)")

class MatrixRowInputByNameRequestBody(PermissiveModel):
    """Input for writing a single Matrix row."""
    inputs: list[MatrixInputCellByNameRequestBody] = Field(..., description="Input column values (must include ALL input columns)")
    results: list[MatrixResultCellByNameRequestBody] = Field(..., description="Result column values (can be partial subset)")

class Memo(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Unique identifier for the transaction associated with this memo.", json_schema_extra={'format': 'uuid'})
    memo: str | None = Field(None, description="Text content of the memo.")

class NativeRowIdentifierRequestBody(PermissiveModel):
    column_name: str
    value: str

class ColumnNameAndContentsRequestBody(PermissiveModel):
    contents: NativeRowIdentifierRequestBody | str | bool | float | None = Field(...)
    name: str

class CustomRowColumnContentsByColumnNameRequestBody(PermissiveModel):
    cells: list[ColumnNameAndContentsRequestBody] = Field(..., description="The contents of the cells in the row. The column name should be the name of the column, and the contents should be the value to insert into the cell. When setting a cell to reference many rows, each reference must be a separate entry in the list.")
    external_key: str = Field(..., description="The external key of the row.")

class NativeRowColumnContentsByColumnNameRequestBody(PermissiveModel):
    cells: list[ColumnNameAndContentsRequestBody] = Field(..., description="The contents of the cells in the row. The column name should be the name of the column, and the contents should be the value to insert into the cell. When setting a cell to reference many rows, each reference must be a separate entry in the list.")
    row: NativeRowIdentifierRequestBody = Field(..., description="An identifier for the Ramp object")

class PatchAccountingConnectionDetailResourceBodySettings(PermissiveModel):
    """Settings for the accounting connection. Only applies to API-based connections."""
    reimbursement_sync_button_enabled: bool | None = Field(None, description="Whether the reimbursement sync button is enabled for this accounting connection. Only applies to API-based connections.")
    transaction_accounting_vendor_creation_on_sync_enabled: bool | None = Field(None, description="Whether card transactions missing a mapped accounting vendor should require vendor creation before sync. Only applies to API-based connections.")
    transaction_sync_button_enabled: bool | None = Field(None, description="Whether the transaction sync button is enabled for this accounting connection. Only applies to API-based connections.")
    vendor_credits_enabled: bool | None = Field(None, description="Whether vendor credits are enabled for this accounting connection. Only applies to API-based connections.")

class PatchCardResourceBodySpendingRestrictions(PermissiveModel):
    """Modify spending restrictions. Only the fields to be modified need to be passed (so fields that will stay the same do not have to be passed)."""
    amount: str | float | None = Field(None, description="Amount limit total per interval.", ge=0)
    blocked_mcc_codes: list[str] | None = None
    categories: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = Field(None, description="List of Ramp category codes that this card is restricted to.")
    categories_blacklist: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = None
    categories_whitelist: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = None
    currency: str | None = Field(None, description="Currency in which the amount is specified.")
    interval: Literal["ANNUAL", "DAILY", "MONTHLY", "QUARTERLY", "TERTIARY", "TOTAL", "WEEKLY", "YEARLY"] | None = Field(None, description="Time interval to apply limit to.")
    lock_date: str | None = Field(None, description="Date to automatically lock the card. If `lock_date` has passed, set to a future date or to null to unlock the card.", json_schema_extra={'format': 'date-time'})
    policy_id: str | None = None
    transaction_amount_limit: str | float | None = Field(None, description="Max amount limit per transaction.", ge=0)
    vendor_blacklist: list[str] | None = None
    vendor_whitelist: list[str] | None = None

class PatchSpendLimitResourceBodyPermittedSpendTypes(PermissiveModel):
    """Modify permitted spend types. All fields of permitted_spend_types must be given."""
    primary_card_enabled: bool = Field(..., description="Dictates whether the user's physical card can be linked to this limit.")
    reimbursements_enabled: bool = Field(..., description="Dictates whether reimbursements can be submitted against this limit.")

class PatchSpendLimitResourceBodySpendingRestrictionsLimit(PermissiveModel):
    """Total amount limit per interval. Currently we expect the currency to be USD and the amount need to be denominated in cents."""
    amount: int = Field(..., description="the amount of money represented in the smallest denomination of the currency. For example, when the currency is USD, then the amount is expressed in cents.")
    currency_code: str | None = Field('USD', description="The type of currency, in ISO 4217 format. e.g. USD for US dollars")

class PatchSpendLimitResourceBodySpendingRestrictionsTransactionAmountLimit(PermissiveModel):
    """Max amount per transaction. Currently we expect the currency to be USD and the amount need to be denominated in cents."""
    amount: int = Field(..., description="the amount of money represented in the smallest denomination of the currency. For example, when the currency is USD, then the amount is expressed in cents.")
    currency_code: str | None = Field('USD', description="The type of currency, in ISO 4217 format. e.g. USD for US dollars")

class PatchSpendLimitResourceBodySpendingRestrictions(PermissiveModel):
    """Modify spending restrictions. If this field is passed, the entire set of new spending restrictions must be passed (i.e. the given spending restrictions will override all existing spending restrictions)."""
    allowed_categories: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = Field(None, description="List of Ramp category codes allowed for the limit.")
    allowed_vendors: list[str] | None = Field(None, description="List of merchants allowed for the limit.")
    blocked_categories: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = Field(None, description="List of Ramp category codes blocked for the limit.")
    blocked_mcc_codes: list[str] | None = None
    blocked_vendors: list[str] | None = Field(None, description="List of merchants  blocked for the limit.")
    interval: Literal["ANNUAL", "DAILY", "MONTHLY", "QUARTERLY", "TERTIARY", "TOTAL", "WEEKLY", "YEARLY"] = Field(..., description="Time interval to apply limit to.")
    is_one_time_edit: bool | None = Field(None, description="Dictates whether the spend restriction update is only applicable for the current period. Set to true for a temporary limit increase. Default is false.")
    limit: PatchSpendLimitResourceBodySpendingRestrictionsLimit = Field(..., description="Total amount limit per interval. Currently we expect the currency to be USD and the amount need to be denominated in cents.")
    lock_date: str | None = Field(None, description="Date to automatically lock the card. If lock date has passed, set to a future date or to null to unlock the card.", json_schema_extra={'format': 'date-time'})
    transaction_amount_limit: PatchSpendLimitResourceBodySpendingRestrictionsTransactionAmountLimit | None = Field(None, description="Max amount per transaction. Currently we expect the currency to be USD and the amount need to be denominated in cents.")

class PatchVendorResourceBodyAddress(PermissiveModel):
    """The address of the vendor."""
    address_line_1: str = Field(..., description="Primary address line of the vendor.")
    address_line_2: str | None = Field(None, description="Secondary address line or suite number of the vendor.")
    city: str = Field(..., description="City of the vendor address.")
    country: str | None = Field(None, description="Country of the vendor address.")
    postal_code: str = Field(..., description="Postal or ZIP code of the vendor address.")
    state: str | None = Field(None, description="The state or province. Required for US, CA, and AU. Ignored for other countries.")

class PostAccountingConnectionResourceBodySettings(PermissiveModel):
    """Optional settings for the accounting connection. Only applies to API-based connections."""
    reimbursement_sync_button_enabled: bool | None = Field(False, description="Whether the reimbursement sync button is enabled for this accounting connection. Only applies to API-based connections. Defaults to false.")
    transaction_accounting_vendor_creation_on_sync_enabled: bool | None = Field(False, description="Whether card transactions missing a mapped accounting vendor should require vendor creation before sync. Only applies to API-based connections. Defaults to false.")
    transaction_sync_button_enabled: bool | None = Field(False, description="Whether the transaction sync button is enabled for this accounting connection. Only applies to API-based connections. Defaults to false.")
    vendor_credits_enabled: bool | None = Field(False, description="Whether vendor credits are enabled for this accounting connection. Only applies to API-based connections. Defaults to false.")

class PostApplicationResourceBodyApplicant(PermissiveModel):
    """Information about the applicant."""
    email: str = Field(..., description="Email address of the applicant. Must be a business email for the business applying to Ramp.", json_schema_extra={'format': 'email'})
    first_name: str = Field(..., description="First name of the applicant.")
    last_name: str = Field(..., description="Last name of the applicant.")
    phone: str | None = Field(None, description="Phone number of the applicant in E.164 format.")

class PostApplicationResourceBodyBusinessAddress(PermissiveModel):
    """Principal place of business address."""
    apt_suite: str | None = Field(None, description="Apartment or suite number.")
    city: str | None = Field(None, description="City.")
    postal_code: str | None = Field(None, description="Postal code.")
    state: str | None = Field(None, description="Two-letter state code (e.g. CA).", min_length=2, max_length=2)
    street_address: str | None = Field(None, description="Street address.")

class PostApplicationResourceBodyBusinessIncorporation(PermissiveModel):
    """Business incorporation details."""
    date_of_incorporation: str | None = Field(None, description="Date of incorporation in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    ein_number: str | None = Field(None, description="Employer Identification Number.")
    entity_type: Literal["COOPERATIVE", "CORPORATION", "LLC", "NON_PROFIT_CORPORATION", "OTHER", "PARTNERSHIP", "SOLE_PROPRIETORSHIP"] | None = Field(None, description="Type of business entity.")
    state_of_incorporation: str | None = Field(None, description="Two-letter state code where the business is incorporated.", min_length=2, max_length=2)

class PostApplicationResourceBodyBusiness(PermissiveModel):
    """Business details."""
    address: PostApplicationResourceBodyBusinessAddress | None = Field(None, description="Principal place of business address.")
    business_description: str | None = Field(None, description="Brief description of the business.")
    business_name_dba: str | None = Field(None, description="Doing-business-as name.")
    business_name_legal: str | None = Field(None, description="Legal name of the business.")
    business_name_on_card: str | None = Field(None, description="Name to display on cards.")
    business_website: str | None = Field(None, description="Business website URL.")
    incorporation: PostApplicationResourceBodyBusinessIncorporation | None = Field(None, description="Business incorporation details.")
    phone: str | None = Field(None, description="Office phone number in E.164 format.")

class PostApplicationResourceBodyControllingOfficerAddress(PermissiveModel):
    """Residential address."""
    apt_suite: str | None = Field(None, description="Apartment or suite number.")
    city: str | None = Field(None, description="City.")
    country: str | None = Field(None, description="Two-letter country code (e.g. US).", min_length=2, max_length=2)
    postal_code: str | None = Field(None, description="Postal code.")
    state: str | None = Field(None, description="Two-letter state code (e.g. CA).", min_length=2, max_length=2)
    street_address: str | None = Field(None, description="Street address.")

class PostApplicationResourceBodyControllingOfficer(PermissiveModel):
    """The controlling officer of the business."""
    address: PostApplicationResourceBodyControllingOfficerAddress | None = Field(None, description="Residential address.")
    birth_date: str | None = Field(None, description="Date of birth in YYYY-MM-DD format.")
    email: str | None = Field(None, description="Email address.", json_schema_extra={'format': 'email'})
    first_name: str | None = Field(None, description="First name.")
    is_beneficial_owner: bool | None = Field(False, description="Whether this officer is also a beneficial owner. Defaults to false.")
    last_name: str | None = Field(None, description="Last name.")
    passport_last_4: str | None = Field(None, description="Last 4 digits of passport number.", min_length=4, max_length=4)
    phone: str | None = Field(None, description="Phone number in E.164 format.")
    ssn_last_4: str | None = Field(None, description="Last 4 digits of SSN.", min_length=4, max_length=4)
    title: str | None = Field(None, description="Job title or role.")

class PostApplicationResourceBodyFinancialDetails(PermissiveModel):
    """Financial details for underwriting."""
    estimated_monthly_ap_spend_amount: int | None = Field(None, description="Estimated monthly accounts payable spend amount in dollars.")
    estimated_monthly_spend_amount: int | None = Field(None, description="Estimated monthly card spend amount in dollars.")

class PostApplicationResourceBodyOauthAuthorizeParams(PermissiveModel):
    """OAuth authorization parameters. If provided, the user will be redirected to an OAuth consent screen after accepting the invite."""
    redirect_uri: str = Field(..., description="The URI to redirect the user to after accepting the invite.")
    state: str = Field(..., description="An opaque value used by the client to maintain state between the request and callback.", min_length=1)

class PostCardVaultCreationBodySpendingRestrictionsLimit(PermissiveModel):
    """Total amount limit per interval. Currently we expect the currency to be USD and the amount need to be denominated in cents."""
    amount: int = Field(..., description="the amount of money represented in the smallest denomination of the currency. For example, when the currency is USD, then the amount is expressed in cents.")
    currency_code: str | None = Field('USD', description="The type of currency, in ISO 4217 format. e.g. USD for US dollars")

class PostCardVaultCreationBodySpendingRestrictionsTransactionAmountLimit(PermissiveModel):
    """Max amount per transaction. Currently we expect the currency to be USD and the amount need to be denominated in cents."""
    amount: int = Field(..., description="the amount of money represented in the smallest denomination of the currency. For example, when the currency is USD, then the amount is expressed in cents.")
    currency_code: str | None = Field('USD', description="The type of currency, in ISO 4217 format. e.g. USD for US dollars")

class PostCardVaultCreationBodySpendingRestrictions(PermissiveModel):
    """Specifies the spending restrictions. If spend_program_id is passed, this field is ignored and the limit will inherit the spending restrictions of the spend program."""
    allowed_categories: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = Field(None, description="List of Ramp category codes allowed for the limit.")
    allowed_vendors: list[str] | None = Field(None, description="List of merchants allowed for the limit.")
    blocked_categories: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = Field(None, description="List of Ramp category codes blocked for the limit.")
    blocked_mcc_codes: list[str] | None = None
    blocked_vendors: list[str] | None = Field(None, description="List of merchants  blocked for the limit.")
    interval: Literal["ANNUAL", "DAILY", "MONTHLY", "QUARTERLY", "TERTIARY", "TOTAL", "WEEKLY", "YEARLY"] = Field(..., description="Time interval to apply limit to.")
    limit: PostCardVaultCreationBodySpendingRestrictionsLimit = Field(..., description="Total amount limit per interval. Currently we expect the currency to be USD and the amount need to be denominated in cents.")
    lock_date: str | None = Field(None, description="Date to automatically lock the card. If lock date has passed, set to a future date or to null to unlock the card.", json_schema_extra={'format': 'date-time'})
    transaction_amount_limit: PostCardVaultCreationBodySpendingRestrictionsTransactionAmountLimit | None = Field(None, description="Max amount per transaction. Currently we expect the currency to be USD and the amount need to be denominated in cents.")

class PostDevApiAddMatrixResultColumnBodyNativeTable(PermissiveModel):
    """The native table this result references (only users and accounting_field_options supported)"""
    accounting_field_ramp_id: str | None = Field(None, description="The accounting field's ramp_id (UUID), only set for accounting_field_options")
    table_name: Literal["accounting_field_options", "users"] = Field(..., description="The native table name for result columns: users or accounting_field_options only.")
    type_: Literal["native_table"] | None = Field('native_table', validation_alias="type", serialization_alias="type")

class PostPhysicalCardBodyFulfillmentCardPersonalizationTextNameLine1(PermissiveModel):
    value: str | None = None

class PostPhysicalCardBodyFulfillmentCardPersonalizationTextNameLine2(PermissiveModel):
    value: str | None = None

class PostPhysicalCardBodyFulfillmentCardPersonalizationText(PermissiveModel):
    name_line_1: PostPhysicalCardBodyFulfillmentCardPersonalizationTextNameLine1 | None = None
    name_line_2: PostPhysicalCardBodyFulfillmentCardPersonalizationTextNameLine2 | None = None

class PostPhysicalCardBodyFulfillmentCardPersonalization(PermissiveModel):
    text: PostPhysicalCardBodyFulfillmentCardPersonalizationText | None = None

class PostPhysicalCardBodyFulfillmentShippingRecipientAddress(PermissiveModel):
    address1: str = Field(..., min_length=1, max_length=50)
    address2: str | None = Field(None, min_length=0, max_length=50)
    city: str
    country: str
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    phone: str | None = None
    postal_code: str
    state: str | None = None

class PostPhysicalCardBodyFulfillmentShippingReturnAddress(PermissiveModel):
    address1: str = Field(..., min_length=1, max_length=50)
    address2: str | None = Field(None, min_length=0, max_length=50)
    city: str
    country: str
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    phone: str | None = None
    postal_code: str
    state: str | None = None

class PostPhysicalCardBodyFulfillmentShipping(PermissiveModel):
    method: str | None = None
    recipient_address: PostPhysicalCardBodyFulfillmentShippingRecipientAddress | None = None
    recipient_address_verification_state: Literal["NOT_VERIFIED", "OVERRIDEN", "VERIFIED"] | None = None
    return_address: PostPhysicalCardBodyFulfillmentShippingReturnAddress | None = None

class PostPhysicalCardBodyFulfillment(PermissiveModel):
    """Fulfillment details of a Ramp card. For physical cards only."""
    card_personalization: PostPhysicalCardBodyFulfillmentCardPersonalization | None = None
    cardholder_uuid: str | None = Field(None, json_schema_extra={'format': 'uuid'})
    shipping: PostPhysicalCardBodyFulfillmentShipping | None = None

class PostPhysicalCardBodySpendingRestrictions(PermissiveModel):
    """Specifies the spend restrictions on a Ramp card. One of `spending_restrictions` or `card_program_id` must be provided."""
    amount: str | float = Field(..., description="Amount limit total per interval.", ge=0)
    blocked_mcc_codes: list[str] | None = None
    card_accounting_rules: list[ApiCardAccountingRulesDataRequestBody] | None = None
    categories: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = Field(None, description="List of Ramp category codes that this card is restricted to.")
    categories_blacklist: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = None
    categories_whitelist: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = None
    currency: str | None = Field(None, description="Currency in which the amount is specified.")
    interval: Literal["ANNUAL", "DAILY", "MONTHLY", "QUARTERLY", "TERTIARY", "TOTAL", "WEEKLY", "YEARLY"] = Field(..., description="Time interval to apply limit to.")
    lock_date: str | None = Field(None, description="Date to automatically lock the card. If `lock_date` has passed, set to a future date or to null to unlock the card. Note that this is different from the actual card expiration date. This date need to conforms to ISO8601 format.", json_schema_extra={'format': 'date-time'})
    policy_id: str | None = None
    transaction_amount_limit: str | float | None = Field(None, description="Max amount limit per transaction.", ge=0)
    vendor_blacklist: list[str] | None = None
    vendor_whitelist: list[str] | None = None

class PostSpendLimitCreationBodyPermittedSpendTypes(PermissiveModel):
    """Specifies the permitted spend types."""
    primary_card_enabled: bool = Field(..., description="Dictates whether the user's physical card can be linked to this limit.")
    reimbursements_enabled: bool = Field(..., description="Dictates whether reimbursements can be submitted against this limit.")

class PostSpendLimitCreationBodySpendingRestrictionsLimit(PermissiveModel):
    """Total amount limit per interval. Currently we expect the currency to be USD and the amount need to be denominated in cents."""
    amount: int = Field(..., description="the amount of money represented in the smallest denomination of the currency. For example, when the currency is USD, then the amount is expressed in cents.")
    currency_code: str | None = Field('USD', description="The type of currency, in ISO 4217 format. e.g. USD for US dollars")

class PostSpendLimitCreationBodySpendingRestrictionsTransactionAmountLimit(PermissiveModel):
    """Max amount per transaction. Currently we expect the currency to be USD and the amount need to be denominated in cents."""
    amount: int = Field(..., description="the amount of money represented in the smallest denomination of the currency. For example, when the currency is USD, then the amount is expressed in cents.")
    currency_code: str | None = Field('USD', description="The type of currency, in ISO 4217 format. e.g. USD for US dollars")

class PostSpendLimitCreationBodySpendingRestrictions(PermissiveModel):
    """Specifies the spending restrictions. If spend_program_id is passed, this field is ignored and the limit will inherit the spending restrictions of the spend program."""
    allowed_categories: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = Field(None, description="List of Ramp category codes allowed for the limit.")
    allowed_vendors: list[str] | None = Field(None, description="List of merchants allowed for the limit.")
    blocked_categories: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = Field(None, description="List of Ramp category codes blocked for the limit.")
    blocked_mcc_codes: list[str] | None = None
    blocked_vendors: list[str] | None = Field(None, description="List of merchants  blocked for the limit.")
    interval: Literal["ANNUAL", "DAILY", "MONTHLY", "QUARTERLY", "TERTIARY", "TOTAL", "WEEKLY", "YEARLY"] = Field(..., description="Time interval to apply limit to.")
    limit: PostSpendLimitCreationBodySpendingRestrictionsLimit = Field(..., description="Total amount limit per interval. Currently we expect the currency to be USD and the amount need to be denominated in cents.")
    lock_date: str | None = Field(None, description="Date to automatically lock the card. If lock date has passed, set to a future date or to null to unlock the card.", json_schema_extra={'format': 'date-time'})
    transaction_amount_limit: PostSpendLimitCreationBodySpendingRestrictionsTransactionAmountLimit | None = Field(None, description="Max amount per transaction. Currently we expect the currency to be USD and the amount need to be denominated in cents.")

class PostSpendProgramResourceBodyIssuanceRulesAutomatic(PermissiveModel):
    """Set of rules for having spend programs issued by default to users"""
    applies_to_all: bool | None = Field(False, description="Dictates whether this rule should apply to all employees or not (if True, location_ids, department_ids, and user_custom_field_ids should be null).")
    department_ids: list[str] | None = Field(None, description="List of departments whose users are able to request or be issued this spend program.")
    location_ids: list[str] | None = Field(None, description="List of locations whose users are able to request or be issued this spend program.")
    user_custom_field_ids: list[str] | None = None

class PostSpendProgramResourceBodyIssuanceRulesRequestable(PermissiveModel):
    """Set of rules for users requesting spend programs."""
    applies_to_all: bool | None = Field(False, description="Dictates whether this rule should apply to all employees or not (if True, location_ids, department_ids, and user_custom_field_ids should be null).")
    department_ids: list[str] | None = Field(None, description="List of departments whose users are able to request or be issued this spend program.")
    location_ids: list[str] | None = Field(None, description="List of locations whose users are able to request or be issued this spend program.")
    user_custom_field_ids: list[str] | None = None

class PostSpendProgramResourceBodyIssuanceRules(PermissiveModel):
    """Spend Program Issuance Rules can be set for requests or default issuance of Limits from a program. Set whether a program is requestable or issued by default for a given set of users and their attributes (department, locations, and custom fields). If you'd like to give these permissions to all employees, you can set `applies_to_all` to `True`. Feel free to ignore this if you don't want any custom requestability or issuance logic."""
    automatic: PostSpendProgramResourceBodyIssuanceRulesAutomatic | None = Field(None, description="Set of rules for having spend programs issued by default to users")
    requestable: PostSpendProgramResourceBodyIssuanceRulesRequestable | None = Field(None, description="Set of rules for users requesting spend programs.")

class PostSpendProgramResourceBodyPermittedSpendTypes(PermissiveModel):
    """Specifies the permitted spend types for the spend program."""
    primary_card_enabled: bool = Field(..., description="Dictates whether the user's physical card can be linked to this limit.")
    reimbursements_enabled: bool = Field(..., description="Dictates whether reimbursements can be submitted against this limit.")

class PostSpendProgramResourceBodySpendingRestrictionsLimit(PermissiveModel):
    """Total amount limit per interval. Currently we expect the currency to be USD and the amount need to be denominated in cents."""
    amount: int = Field(..., description="the amount of money represented in the smallest denomination of the currency. For example, when the currency is USD, then the amount is expressed in cents.")
    currency_code: str | None = Field('USD', description="The type of currency, in ISO 4217 format. e.g. USD for US dollars")

class PostSpendProgramResourceBodySpendingRestrictionsTransactionAmountLimit(PermissiveModel):
    """Max amount per transaction. Currently we expect the currency to be USD and the amount need to be denominated in cents."""
    amount: int = Field(..., description="the amount of money represented in the smallest denomination of the currency. For example, when the currency is USD, then the amount is expressed in cents.")
    currency_code: str | None = Field('USD', description="The type of currency, in ISO 4217 format. e.g. USD for US dollars")

class PostSpendProgramResourceBodySpendingRestrictions(PermissiveModel):
    """A set of restrictions imposed on the spend program."""
    allowed_categories: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = Field(None, description="List of Ramp category codes allowed for the limit.")
    allowed_vendors: list[str] | None = Field(None, description="List of merchants allowed for the limit.")
    blocked_categories: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = Field(None, description="List of Ramp category codes blocked for the limit.")
    blocked_mcc_codes: list[str] | None = None
    blocked_vendors: list[str] | None = Field(None, description="List of merchants  blocked for the limit.")
    interval: Literal["ANNUAL", "DAILY", "MONTHLY", "QUARTERLY", "TERTIARY", "TOTAL", "WEEKLY", "YEARLY"] = Field(..., description="Time interval to apply limit to.")
    limit: PostSpendProgramResourceBodySpendingRestrictionsLimit = Field(..., description="Total amount limit per interval. Currently we expect the currency to be USD and the amount need to be denominated in cents.")
    lock_date: str | None = Field(None, description="Date to automatically lock the card. If lock date has passed, set to a future date or to null to unlock the card.", json_schema_extra={'format': 'date-time'})
    transaction_amount_limit: PostSpendProgramResourceBodySpendingRestrictionsTransactionAmountLimit | None = Field(None, description="Max amount per transaction. Currently we expect the currency to be USD and the amount need to be denominated in cents.")

class PostVendorAgreementListResourceBodyEndDateRangeEnd(PermissiveModel):
    """End date offset, always snapped to end of period"""
    offset: int = Field(..., description="Number of units to offset. Negative for past, positive for future. Example: -1 month = previous month")
    unit: Literal["day", "month", "quarter", "week", "year"] = Field(..., description="The unit of time (day, week, quarter, month, year)")

class PostVendorAgreementListResourceBodyEndDateRangeStart(PermissiveModel):
    """Start date offset, always snapped to beginning of period"""
    offset: int = Field(..., description="Number of units to offset. Negative for past, positive for future. Example: -1 month = previous month")
    unit: Literal["day", "month", "quarter", "week", "year"] = Field(..., description="The unit of time (day, week, quarter, month, year)")

class PostVendorAgreementListResourceBodyEndDateRange(PermissiveModel):
    """JSON object describing a relative end date range filter."""
    end: PostVendorAgreementListResourceBodyEndDateRangeEnd | None = Field(None, description="End date offset, always snapped to end of period")
    start: PostVendorAgreementListResourceBodyEndDateRangeStart | None = Field(None, description="Start date offset, always snapped to beginning of period")

class PostVendorAgreementListResourceBodyLastDateToTerminateRangeEnd(PermissiveModel):
    """End date offset, always snapped to end of period"""
    offset: int = Field(..., description="Number of units to offset. Negative for past, positive for future. Example: -1 month = previous month")
    unit: Literal["day", "month", "quarter", "week", "year"] = Field(..., description="The unit of time (day, week, quarter, month, year)")

class PostVendorAgreementListResourceBodyLastDateToTerminateRangeStart(PermissiveModel):
    """Start date offset, always snapped to beginning of period"""
    offset: int = Field(..., description="Number of units to offset. Negative for past, positive for future. Example: -1 month = previous month")
    unit: Literal["day", "month", "quarter", "week", "year"] = Field(..., description="The unit of time (day, week, quarter, month, year)")

class PostVendorAgreementListResourceBodyLastDateToTerminateRange(PermissiveModel):
    """JSON object describing a relative last date to terminate range filter."""
    end: PostVendorAgreementListResourceBodyLastDateToTerminateRangeEnd | None = Field(None, description="End date offset, always snapped to end of period")
    start: PostVendorAgreementListResourceBodyLastDateToTerminateRangeStart | None = Field(None, description="Start date offset, always snapped to beginning of period")

class PostVendorAgreementListResourceBodyStartDateRangeEnd(PermissiveModel):
    """End date offset, always snapped to end of period"""
    offset: int = Field(..., description="Number of units to offset. Negative for past, positive for future. Example: -1 month = previous month")
    unit: Literal["day", "month", "quarter", "week", "year"] = Field(..., description="The unit of time (day, week, quarter, month, year)")

class PostVendorAgreementListResourceBodyStartDateRangeStart(PermissiveModel):
    """Start date offset, always snapped to beginning of period"""
    offset: int = Field(..., description="Number of units to offset. Negative for past, positive for future. Example: -1 month = previous month")
    unit: Literal["day", "month", "quarter", "week", "year"] = Field(..., description="The unit of time (day, week, quarter, month, year)")

class PostVendorAgreementListResourceBodyStartDateRange(PermissiveModel):
    """JSON object describing a relative start date range filter."""
    end: PostVendorAgreementListResourceBodyStartDateRangeEnd | None = Field(None, description="End date offset, always snapped to end of period")
    start: PostVendorAgreementListResourceBodyStartDateRangeStart | None = Field(None, description="Start date offset, always snapped to beginning of period")

class PostVendorBankAccountUpdateResourceBodyAchDetails(PermissiveModel):
    """ACH payment details"""
    account_name: str | None = Field('Business Account', description="Account name")
    account_number: str = Field(..., description="ACH account number")
    account_owner_type: Literal["BUSINESS", "INDIVIDUAL"] | None = Field('BUSINESS', description="Account owner type")
    account_type: Literal["Checking", "Savings"] | None = Field('Checking', description="Account type")
    routing_number: str = Field(..., description="ACH routing number")

class PostVendorBankAccountUpdateResourceBodyWireDetails(PermissiveModel):
    """Wire payment details"""
    account_name: str | None = Field('Business Account', description="Account name")
    account_number: str = Field(..., description="Wire account number")
    routing_number: str = Field(..., description="Wire routing number")

class PostVendorListResourceBodyAddress(PermissiveModel):
    """The address of the vendor."""
    address_line_1: str = Field(..., description="Primary address line of the vendor.")
    address_line_2: str | None = Field(None, description="Secondary address line or suite number of the vendor.")
    city: str = Field(..., description="City of the vendor address.")
    country: str | None = Field(None, description="Country of the vendor address.")
    postal_code: str = Field(..., description="Postal or ZIP code of the vendor address.")
    state: str | None = Field(None, description="The state or province. Required for US, CA, and AU. Ignored for other countries.")

class PostVendorListResourceBodyBusinessVendorContacts(PermissiveModel):
    """Detailed information about the vendor contact."""
    email: str
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None

class PostVirtualCardBodySpendingRestrictions(PermissiveModel):
    """Specifies the spend restrictions on a Ramp card. One of `spending_restrictions` or `card_program_id` must be provided."""
    amount: str | float = Field(..., description="Amount limit total per interval.", ge=0)
    blocked_mcc_codes: list[str] | None = None
    card_accounting_rules: list[ApiCardAccountingRulesDataRequestBody] | None = None
    categories: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = Field(None, description="List of Ramp category codes that this card is restricted to.")
    categories_blacklist: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = None
    categories_whitelist: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = None
    currency: str | None = Field(None, description="Currency in which the amount is specified.")
    interval: Literal["ANNUAL", "DAILY", "MONTHLY", "QUARTERLY", "TERTIARY", "TOTAL", "WEEKLY", "YEARLY"] = Field(..., description="Time interval to apply limit to.")
    lock_date: str | None = Field(None, description="Date to automatically lock the card. If `lock_date` has passed, set to a future date or to null to unlock the card. Note that this is different from the actual card expiration date. This date need to conforms to ISO8601 format.", json_schema_extra={'format': 'date-time'})
    policy_id: str | None = None
    transaction_amount_limit: str | float | None = Field(None, description="Max amount limit per transaction.", ge=0)
    vendor_blacklist: list[str] | None = None
    vendor_whitelist: list[str] | None = None

class PutSpendLimitResourceBodyPermittedSpendTypes(PermissiveModel):
    """Modify permitted spend types. All fields of permitted_spend_types must be given."""
    primary_card_enabled: bool = Field(..., description="Dictates whether the user's physical card can be linked to this limit.")
    reimbursements_enabled: bool = Field(..., description="Dictates whether reimbursements can be submitted against this limit.")

class PutSpendLimitResourceBodySpendingRestrictionsLimit(PermissiveModel):
    """Total amount limit per interval. Currently we expect the currency to be USD and the amount need to be denominated in cents."""
    amount: int = Field(..., description="the amount of money represented in the smallest denomination of the currency. For example, when the currency is USD, then the amount is expressed in cents.")
    currency_code: str | None = Field('USD', description="The type of currency, in ISO 4217 format. e.g. USD for US dollars")

class PutSpendLimitResourceBodySpendingRestrictionsTransactionAmountLimit(PermissiveModel):
    """Max amount per transaction. Currently we expect the currency to be USD and the amount need to be denominated in cents."""
    amount: int = Field(..., description="the amount of money represented in the smallest denomination of the currency. For example, when the currency is USD, then the amount is expressed in cents.")
    currency_code: str | None = Field('USD', description="The type of currency, in ISO 4217 format. e.g. USD for US dollars")

class PutSpendLimitResourceBodySpendingRestrictions(PermissiveModel):
    """Modify spending restrictions. If this field is passed, the entire set of new spending restrictions must be passed (i.e. the given spending restrictions will override all existing spending restrictions)."""
    allowed_categories: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = Field(None, description="List of Ramp category codes allowed for the limit.")
    allowed_vendors: list[str] | None = Field(None, description="List of merchants allowed for the limit.")
    blocked_categories: list[Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9]] | None = Field(None, description="List of Ramp category codes blocked for the limit.")
    blocked_mcc_codes: list[str] | None = None
    blocked_vendors: list[str] | None = Field(None, description="List of merchants  blocked for the limit.")
    interval: Literal["ANNUAL", "DAILY", "MONTHLY", "QUARTERLY", "TERTIARY", "TOTAL", "WEEKLY", "YEARLY"] = Field(..., description="Time interval to apply limit to.")
    is_one_time_edit: bool | None = Field(None, description="Dictates whether the spend restriction update is only applicable for the current period. Set to true for a temporary limit increase. Default is false.")
    limit: PutSpendLimitResourceBodySpendingRestrictionsLimit = Field(..., description="Total amount limit per interval. Currently we expect the currency to be USD and the amount need to be denominated in cents.")
    lock_date: str | None = Field(None, description="Date to automatically lock the card. If lock date has passed, set to a future date or to null to unlock the card.", json_schema_extra={'format': 'date-time'})
    transaction_amount_limit: PutSpendLimitResourceBodySpendingRestrictionsTransactionAmountLimit | None = Field(None, description="Max amount per transaction. Currently we expect the currency to be USD and the amount need to be denominated in cents.")

class Receipt(PermissiveModel):
    created_at: str | None = Field(None, description="Timestamp when the receipt was created.", json_schema_extra={'format': 'date-time'})
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Unique identifier for the receipt.", json_schema_extra={'format': 'uuid'})
    receipt_url: str = Field(..., description="Pre-signed URL to download receipt image (valid for 1 hour by default).")
    transaction_id: str | None = Field(None, description="Transaction associated with this receipt.", json_schema_extra={'format': 'uuid'})
    user_id: str | None = Field(None, description="User who uploaded the receipt.", json_schema_extra={'format': 'uuid'})

class Reimbursement(PermissiveModel):
    accounting_date: str | None = Field(..., description="The date for the reimbursement for accounting purposes. If not specified, falls back to the transaction date.", json_schema_extra={'format': 'date-time'})
    accounting_field_selections: list[ApiReimbursementAccountingFieldSelection] = Field(..., description="List of accounting fields selected to code the reimbursement.")
    amount: float | None = Field(..., description="The amount that the payor pays.")
    approved_at: str | None = Field(..., description="Time at which the reimbursement is approved. Presented in ISO8601 format.", json_schema_extra={'format': 'date-time'})
    attendees: list[ApiReimbursementAttendee] = Field(..., description="List of attendees for the reimbursement.")
    created_at: str = Field(..., description="Time at which the reimbursement is created. Presented in ISO8601 format.", json_schema_extra={'format': 'date-time'})
    currency: str = Field(..., description="The currency that the payor pays with.")
    direction: Literal["BUSINESS_TO_USER", "USER_TO_BUSINESS"] = Field(..., description="The direction of the reimbursement. It could be either BUSINESS_TO_USER or USER_TO_BUSINESS.")
    distance: float | None = Field(..., description="The distance of the reimbursement in miles, for mileage reimbursements.")
    employee_id: str | None = Field(..., description="Employee ID of the person who made the reimbursement.")
    end_location: str | None = Field(..., description="Ending location of the trip, for mileage reimbursements.")
    entity_id: str | None = Field(..., description="Unique identifier of the associated business entity.", json_schema_extra={'format': 'uuid'})
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier of the reimbursement.", json_schema_extra={'format': 'uuid'})
    line_items: list[ApiReimbursementLineItem] = Field(..., description="List of line items related to the reimbursement.")
    memo: str | None = Field(..., description="Reimbursement memo")
    merchant: str | None = Field(..., description="The name of the merchant that the reimbursement is associated with.")
    merchant_id: str | None = Field(..., description="The unique identifier of the merchant. Note that this field may be empty when merchant is populated if Ramp does not recognize the merchant.", json_schema_extra={'format': 'uuid'})
    original_reimbursement_amount: CurrencyAmount | None = Field(..., description="Original reimbursement amount before the currency conversion.")
    payee_amount: CurrencyAmount | None = Field(..., description="Amount and currency received by the payee.")
    payment_batch_id: str | None = Field(..., description="The unique identifier of the reimbursement payment batch that the reimbursement is associated with.", json_schema_extra={'format': 'uuid'})
    payment_id: str | None = Field(..., description="The unique identifier of the payment batch that the reimbursement is associated with, once paid.")
    payment_processed_at: str | None = Field(..., description="Time of reimbursement payment. Presented in ISO8601 format.", json_schema_extra={'format': 'date-time'})
    receipts: list[str]
    spend_limit_id: str | None = Field(..., description="Spend limit to which the reimbursement is attributed, if it exists.", json_schema_extra={'format': 'uuid'})
    start_location: str | None = Field(..., description="Starting location of the trip, for mileage reimbursements.")
    state: Literal["APPROVED", "AWAITING_EXPORT", "AWAITING_PAYMENT", "AWAITING_PUSH_PAYMENT", "CANCELED", "DELETED", "DRAFT", "EXPORTED", "EXPORT_FAILED", "EXPORT_INITIATED", "EXPORT_MARKED_AS_FAILED", "EXPORT_SUCCESSFUL", "FAILED_REIMBURSEMENT", "INIT", "MANUALLY_REIMBURSED", "MISSING_ACH", "PENDING", "PROCESSING", "PUSH_PAYMENT_FAILED", "PUSH_PAYMENT_INITIATED", "REIMBURSED", "REIMBURSED_VIA_PUSH", "REJECTED"] = Field(..., description="current state of the reimbursement.")
    submitted_at: str | None = Field(..., description="Time when reimbursement was most recently submitted", json_schema_extra={'format': 'date-time'})
    sync_status: Literal["NOT_SYNC_READY", "SYNCED", "SYNC_READY"] = Field(..., description="Current sync status of the reimbursement.")
    synced_at: str | None = Field(..., description="Time when reimbursement has been synced. Will be None if the reimbursement is not synced.", json_schema_extra={'format': 'date-time'})
    transaction_date: str | None = Field(..., json_schema_extra={'format': 'date'})
    trip_id: str | None = Field(..., description="Trip ID associated with the reimbursement if a Trip ID is available.", json_schema_extra={'format': 'uuid'})
    type_: Literal["MILEAGE", "OUT_OF_POCKET", "PAYBACK_FULL", "PAYBACK_PARTIAL", "PER_DIEM"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the reimbursement.")
    updated_at: str | None = Field(..., description="Time at which the reimbursement was last updated. Presented in ISO8601 format.", json_schema_extra={'format': 'date-time'})
    user_email: str = Field(..., description="Email of the person who made the reimbursement.")
    user_full_name: str = Field(..., description="Full name of the person who made the reimbursement.")
    user_id: str = Field(..., description="Unique identifier of the person who made the reimbursement.", json_schema_extra={'format': 'uuid'})
    waypoints: list[str] = Field(..., description="List of intermediate stops during the trip, for mileage reimbursements.")

class RowQueryGreaterThanClauseRequestBody(PermissiveModel):
    type_: Literal["greater_than"] | None = Field('greater_than', validation_alias="type", serialization_alias="type")
    value: float | str

class RowQueryGreaterThanOrEqualClauseRequestBody(PermissiveModel):
    type_: Literal["greater_than_or_equal"] | None = Field('greater_than_or_equal', validation_alias="type", serialization_alias="type")
    value: float | str

class RowQueryIsNotClauseRequestBody(PermissiveModel):
    type_: Literal["is_not"] | None = Field('is_not', validation_alias="type", serialization_alias="type")
    values: list[str] | list[float | str] | list[bool]

class RowQueryIsNullClauseRequestBody(PermissiveModel):
    type_: Literal["is_null"] | None = Field('is_null', validation_alias="type", serialization_alias="type")

class RowQueryLessThanClauseRequestBody(PermissiveModel):
    type_: Literal["less_than"] | None = Field('less_than', validation_alias="type", serialization_alias="type")
    value: float | str

class RowQueryLessThanOrEqualClauseRequestBody(PermissiveModel):
    type_: Literal["less_than_or_equal"] | None = Field('less_than_or_equal', validation_alias="type", serialization_alias="type")
    value: float | str

class RowQueryOneOfClauseRequestBody(PermissiveModel):
    type_: Literal["one_of"] | None = Field('one_of', validation_alias="type", serialization_alias="type")
    values: list[str] | list[float | str] | list[bool]

class RowQueryFilterRequestBody(PermissiveModel):
    clause: RowQueryGreaterThanClauseRequestBody | RowQueryGreaterThanOrEqualClauseRequestBody | RowQueryIsNotClauseRequestBody | RowQueryIsNullClauseRequestBody | RowQueryLessThanClauseRequestBody | RowQueryLessThanOrEqualClauseRequestBody | RowQueryOneOfClauseRequestBody
    column_id: str
    type_: Literal["filter"] | None = Field('filter', validation_alias="type", serialization_alias="type")

class SpendLimitAccountingRulesDataRequestBody(PermissiveModel):
    field_id: str = Field(..., description="UUID of the accounting field", json_schema_extra={'format': 'uuid'})
    field_option_id: str = Field(..., description="UUID of the accounting field selection", json_schema_extra={'format': 'uuid'})

class TaxCodeOption(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The external ID of the tax code option. This is the ID in your ERP system.")
    name: str = Field(..., description="The name of the tax code option.")
    tax_rate_ids: list[str] | None = Field(None, description="A list of external tax rate IDs (remote_id values) to associate with this tax code option.")

class TaxRate(PermissiveModel):
    accounting_gl_account_id: str | None = Field(None, description="The Ramp ID (ramp_id) of the GL account associated with this tax rate. This is required if the accounting connection is API-based.", json_schema_extra={'format': 'uuid'})
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Remote/external ID of the tax rate from your ERP system.")
    name: str = Field(..., description="Name of the tax rate.")
    rate: str | float = Field(..., description="The tax rate percentage expressed as a decimal (e.g. 0.10 for 10%).", ge=0)

class Transaction(PermissiveModel):
    accounting_categories: list[ApiAccountingCategory] | None = Field(None, description="[Deprecated - use accounting_field_selections instead] Accounting categories related to the transaction.")
    accounting_date: str | None = Field(..., description="The date for the transaction for accounting purposes, in ISO8601 format. Based on the cleared date, transaction date, or a manually overridden date, depending on your accounting preferences in Ramp.", json_schema_extra={'format': 'date-time'})
    accounting_field_selections: list[ApiTransactionAccountingFieldSelection] | None = Field(None, description="List of accounting fields selected to code the transaction.")
    amount: float | None = Field(None, description="Settled amount of the transaction.")
    attendees: list[ApiTransactionAttendee] | None = Field(None, description="List of attendees for the transaction")
    card_holder: ApiTransactionCardHolder | None = Field(None, description="Information about the card holder.")
    card_id: str | None = Field(None, description="Identifier of the physical or virtual card associated with the transaction.", json_schema_extra={'format': 'uuid'})
    card_present: bool = Field(..., description="Whether the transaction was processed using a card present terminal.")
    currency_code: str | None = Field(None, description="Currency that the transaction is settled in.")
    decline_details: ApiTransactionDeclineDetails | None = Field(None, description="Details about a transaction decline.")
    disputes: list[ApiTransactionDispute] | None = Field(None, description="A list of disputes sorted in descending order by their creation time.")
    entity_id: str | None = Field(..., description="Unique identifier of business entity associated with the transaction.", json_schema_extra={'format': 'uuid'})
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'uuid'})
    limit_id: str | None = Field(None, description="Unique identifier of the spend limit associated with the transaction", json_schema_extra={'format': 'uuid'})
    line_items: list[ApiTransactionLineItem] | None = Field(None, description="List of line items related to the transaction.")
    memo: str | None = Field(None, max_length=255)
    merchant_category_code: str | None = Field(None, description="Merchant category code is a four-digit number in ISP 18245 used to classify a business by the types of goods and services it provides.")
    merchant_category_code_description: str | None = Field(None, description="Description about the merchant category code.")
    merchant_data: ApiTransactionPurchaseData | None = Field(None, description="Purchase data associated related to a transaction provided by the merchant")
    merchant_descriptor: str | None = Field(None, description="A merchant descriptor is the name that appears on a customer's bank statement when they make a purchase from that merchant.")
    merchant_id: str | None = Field(..., json_schema_extra={'format': 'uuid'})
    merchant_location: ApiMerchantLocation | None = Field(..., description="Card acceptor data such as country, city, state, and postal code if available.")
    merchant_name: str | None = None
    minor_unit_conversion_rate: int | None = Field(..., description="The conversion factor to convert from the integer amount to the actual currency value. Divide amount by this value to get the real currency amount. For USD, this is 100 (e.g., 12034 / 100 = 120.34 USD).")
    original_transaction_amount: CurrencyAmount | None = Field(..., description="the original transaction amount before the currency conversion.")
    policy_violations: list[ApiTransactionPolicyViolation] | None = Field(None, description="A list of policy violations sorted in descending order by their creation time.")
    receipts: list[str] | None = Field(None, description="Receipts listed in ascending order by their creation time, related to the transaction.")
    requires_accounting_vendor_creation_to_sync: bool | None = Field(None, description="Whether the integrator must create an accounting vendor and code it to this transaction before syncing. True when the connection has transaction_accounting_vendor_creation_on_sync_enabled=true and the transaction has no vendor accounting field selection. Omitted when transaction_accounting_vendor_creation_on_sync_enabled=false.")
    settlement_date: str | None = Field(None, description="Time when funds were moved for a transaction, in ISO8601 format.", json_schema_extra={'format': 'date-time'})
    sk_category_id: Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9] | None = Field(..., description="Ramp category code.")
    sk_category_name: str | None = Field(..., description="Ramp category name.")
    spend_program_id: str | None = Field(None, description="Unique identifier of the spend program from which this limit was issued.", json_schema_extra={'format': 'uuid'})
    state: Literal["ALL", "CLEARED", "COMPLETION", "DECLINED", "ERROR", "PENDING", "PENDING_INITIATION"] | None = Field(None, description="transaction state.")
    statement_id: str | None = Field(None, description="Statement ID associated with the transaction if one is available.", json_schema_extra={'format': 'uuid'})
    sync_status: Literal["NOT_SYNC_READY", "SYNCED", "SYNC_READY"]
    synced_at: str | None = Field(..., description="Time when transaction has been synced, in ISO8601 format. Will be None if the transaction is not synced.", json_schema_extra={'format': 'date-time'})
    trip_id: str | None = Field(..., description="Trip ID associated with the transaction if one is available.", json_schema_extra={'format': 'uuid'})
    trip_name: str | None = Field(..., description="Trip name associated with the transaction if one is available.")
    user_transaction_time: str | None = Field(None, description="Time when the transaction was created by the user, in ISO8601 format.", json_schema_extra={'format': 'date-time'})

class Transfer(PermissiveModel):
    amount: CurrencyAmount | None = Field(None, description="Amount of the transfer.")
    bank_account_id: str | None = Field(..., description="Unique identifier of the bank account used for this transfer payment.", json_schema_extra={'format': 'uuid'})
    created_at: str | None = Field(None, description="Timestamp when the transfer was created.", json_schema_extra={'format': 'date-time'})
    entity_id: str | None = Field(None, description="Business entity associated with this transfer.", json_schema_extra={'format': 'uuid'})
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Unique identifier for the transfer.", json_schema_extra={'format': 'uuid'})
    payment_id: str | None = Field(None, description="Unique payment identifier for the transfer.")
    status: Literal["ACH_CONFIRMED", "CANCELED", "COMPLETED", "ERROR", "INITIATED", "NOT_ACKED", "NOT_ENOUGH_FUNDS", "PROCESSING_BY_ODFI", "REJECTED_BY_ODFI", "RETURNED_BY_RDFI", "SUBMITTED_TO_FED", "SUBMITTED_TO_RDFI", "UNNECESSARY", "UPLOADED"] | None = Field(None, description="Status of the transfer. See [Transfers Guide](/developer-api/v1/guides/transfers) for definitions.")
    sync_status: Literal["NOT_SYNC_READY", "SYNCED", "SYNC_READY"] = Field(..., description="Current sync status of the transfer.")

class User(PermissiveModel):
    business_id: str | None = Field(..., description="Unique identifier of the company that the employee's working for.", json_schema_extra={'format': 'uuid'})
    custom_fields: list[ApiUserCustomField] = Field(..., description="A list of custom fields of the user.")
    department_id: str | None = Field(..., description="Unique identifier of the employee's department", json_schema_extra={'format': 'uuid'})
    email: str | None = Field(None, description="The employee's email address")
    employee_id: str | None = Field(..., description="An alternative identifier for an employee, coming from external systems, which can be used in place of an email.")
    entity_id: str | None = Field(..., description="Unique identifier of business entity user is associated with.", json_schema_extra={'format': 'uuid'})
    first_name: str | None = Field(None, description="First name of the employee")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Unique employee identifier", json_schema_extra={'format': 'uuid'})
    is_manager: bool = Field(..., description="Whether the employee is a manager")
    last_name: str | None = Field(None, description="Last name of the employee")
    location_id: str | None = Field(..., description="Unique identifier of the employee's location", json_schema_extra={'format': 'uuid'})
    manager_id: str | None = Field(..., description="Unique identifier of the employee's manager", json_schema_extra={'format': 'uuid'})
    phone: str | None = Field(..., description="The employee's phone number")
    role: Literal["AUDITOR", "BUSINESS_ADMIN", "BUSINESS_BOOKKEEPER", "BUSINESS_OWNER", "BUSINESS_USER", "GUEST_USER", "IT_ADMIN"] | None = Field(None, description="The employee's role")
    scheduled_deactivation_date: str | None = Field(..., description="The date when the user is scheduled to be deactivated. Presented in ISO8601 format.", json_schema_extra={'format': 'date-time'})
    status: Literal["INVITE_EXPIRED", "INVITE_PENDING", "USER_ACTIVE", "USER_INACTIVE", "USER_ONBOARDING", "USER_SUSPENDED"]

class Vendor(PermissiveModel):
    accounting_vendor_remote_id: str | None = Field(..., description="The accounting remote id of the vendor.")
    address: ApiAddressResource | None = Field(None, description="The address of the vendor.")
    billing_frequency: Literal["ANNUAL", "MONTHLY", "MULTIPLE", "NA", "OTHER", "QUARTERLY", "ROLLING", "TBD", "TWICE_A_YEAR"] | None = Field(None, description="The billing frequency for this vendor.")
    contacts: list[str] = Field(..., description="Unique identifiers of contacts associated with this vendor.")
    country: str = Field(..., description="The 2-letter country of the vendor.")
    created_at: str = Field(..., description="The date and time when this vendor was created.", json_schema_extra={'format': 'date-time'})
    default_entity_id: str | None = Field(..., description="Unique identifier of the default business entity associated with this vendor.", json_schema_extra={'format': 'uuid'})
    default_payment_method: DefaultPaymentMethodResource | None = Field(..., description="Default payment method for this vendor, including update source and policy.")
    description: str | None = Field(None, description="Description of the vendor.")
    external_vendor_id: str | None = Field(..., description="Customer-defined external identifier for the vendor. This is independent of accounting system remote IDs.")
    federal_tax_classification: Literal["C_CORPORATION", "INDIVIDUAL_SOLE_PROPRIETOR_SINGLE_MEMBER_LLC", "INTERNATIONAL", "LLC_C_CORPORATION", "LLC_PARTNERSHIP", "LLC_S_CORPORATION", "OTHER", "PARTNERSHIP", "S_CORPORATION", "TRUST_ESTATE"] | None = Field(None, description="The federal tax classification of the vendor.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Unique identifier of the vendor.", json_schema_extra={'format': 'uuid'})
    is_active: bool = Field(..., description="Whether this vendor is active.")
    is_deletable: bool = Field(..., description="Whether this vendor is deletable.")
    merchant_id: str | None = Field(None, description="The id of the card merchant.", json_schema_extra={'format': 'uuid'})
    name: str = Field(..., description="Name of the vendor.")
    name_legal: str | None = Field(None, description="Legal name of the vendor.")
    sk_category_id: Literal[1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 2, 20, 21, 23, 24, 25, 26, 27, 28, 29, 3, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 4, 40, 41, 42, 43, 44, 5, 6, 7, 8, 9] | None = Field(None, description="Ramp category code of the vendor.")
    sk_category_name: str | None = Field(None, description="The category name of the vendor.")
    state: str | None = None
    subsidiary: list[str] | None = Field(None, description="ERP subsidiary identifiers associated with this vendor. Only returned when `include_subsidiary=true`.")
    tax_address: ApiAddressResource | None = Field(None, description="The tax address of the vendor.")
    total_spend_all_time: CurrencyAmount = Field(..., description="Total spend for all time for this vendor.")
    total_spend_last_30_days: CurrencyAmount = Field(..., description="Total spend for the last 30 days for this vendor.")
    total_spend_last_365_days: CurrencyAmount = Field(..., description="Total spend for the last 365 days for this vendor.")
    total_spend_ytd: CurrencyAmount = Field(..., description="Total spend year-to-date for this vendor.")
    vendor_owner_id: str | None = Field(..., description="Unique identifier of the user which owns this vendor.", json_schema_extra={'format': 'uuid'})
    vendor_type: Literal["BUSINESS", "INDIVIDUAL"] | None = Field(None, description="The type of vendor if bill pay.")

class CustomRecordsQueryAndClauseRequestBody(PermissiveModel):
    filters: list[CustomRecordsQueryAndClauseRequestBody | CustomRecordsQueryOrClauseRequestBody | RowQueryFilterRequestBody]
    type_: Literal["and"] | None = Field('and', validation_alias="type", serialization_alias="type")

class CustomRecordsQueryOrClauseRequestBody(PermissiveModel):
    filters: list[CustomRecordsQueryAndClauseRequestBody | CustomRecordsQueryOrClauseRequestBody | RowQueryFilterRequestBody]
    type_: Literal["or"] | None = Field('or', validation_alias="type", serialization_alias="type")

class PostVendorAgreementListResourceBodyAgreementCustomRecords(PermissiveModel):
    """JSON object describing custom record filters for agreements."""
    filters: list[CustomRecordsQueryAndClauseRequestBody | CustomRecordsQueryOrClauseRequestBody | RowQueryFilterRequestBody]
    type_: Literal["and"] | None = Field('and', validation_alias="type", serialization_alias="type")


# Rebuild models to resolve forward references (required for circular refs)
AccountingVendor.model_rebuild()
ApiAccountingCategory.model_rebuild()
ApiAccountingFailedSyncRequestBody.model_rebuild()
ApiAccountingField.model_rebuild()
ApiAccountingFieldSelection.model_rebuild()
ApiAccountingFieldSelectionSource.model_rebuild()
ApiAccountingSuccessfulSyncRequestBody.model_rebuild()
ApiAccountingSyncErrorRequestBody.model_rebuild()
ApiAddressResource.model_rebuild()
ApiApplicationPersonAddressParamsRequestBody.model_rebuild()
ApiApplicationPersonParamsRequestBody.model_rebuild()
ApiBillInventoryLineItem.model_rebuild()
ApiBillLineItem.model_rebuild()
ApiBillOwner.model_rebuild()
ApiBillPayment.model_rebuild()
ApiBillTraceId.model_rebuild()
ApiBillVendor.model_rebuild()
ApiCardAccountingRulesDataRequestBody.model_rebuild()
ApiCardFulfillment.model_rebuild()
ApiCardPaymentDetailsResource.model_rebuild()
ApiCardSpendingRestrictionsDump.model_rebuild()
ApiCreateAccountingFieldParamsRequestBody.model_rebuild()
ApiCreateBankAccountPaymentParamsRequestBody.model_rebuild()
ApiCreateBillInventoryLineItemParamsRequestBody.model_rebuild()
ApiCreateBillLineItemParamsRequestBody.model_rebuild()
ApiCreateBillVendorPaymentParamsRequestBody.model_rebuild()
ApiCreateCardBillPaymentParamsRequestBody.model_rebuild()
ApiCreateManualBillPaymentParamsRequestBody.model_rebuild()
ApiItemReceiptLineItemCreateParamsRequestBody.model_rebuild()
ApiManualPaymentDetailsResource.model_rebuild()
ApiMerchantLocation.model_rebuild()
ApiPurchaseOrderLineItemCreateParamsRequestBody.model_rebuild()
ApiReimbursementAccountingCategoryInfo.model_rebuild()
ApiReimbursementAccountingFieldSelection.model_rebuild()
ApiReimbursementAttendee.model_rebuild()
ApiReimbursementLineItem.model_rebuild()
ApiTransactionAccountingCategoryInfo.model_rebuild()
ApiTransactionAccountingFieldSelection.model_rebuild()
ApiTransactionAttendee.model_rebuild()
ApiTransactionCardHolder.model_rebuild()
ApiTransactionDeclineDetails.model_rebuild()
ApiTransactionDispute.model_rebuild()
ApiTransactionLineItem.model_rebuild()
ApiTransactionPolicyViolation.model_rebuild()
ApiTransactionPurchaseAutoRental.model_rebuild()
ApiTransactionPurchaseData.model_rebuild()
ApiTransactionPurchaseFlightData.model_rebuild()
ApiTransactionPurchaseFlightSegment.model_rebuild()
ApiTransactionPurchaseLodging.model_rebuild()
ApiTransactionPurchaseReceipt.model_rebuild()
ApiTransactionPurchaseReceiptLineItem.model_rebuild()
ApiUserCustomField.model_rebuild()
ApiVendorBankAccountResource.model_rebuild()
ApiVendorPaymentDetailsResource.model_rebuild()
Bill.model_rebuild()
BillAppliedVendorCredit.model_rebuild()
Card.model_rebuild()
CardPersonalization.model_rebuild()
CardPersonalizationNameLine.model_rebuild()
CardPersonalizationText.model_rebuild()
CardShipping.model_rebuild()
CardShippingAddress.model_rebuild()
ColumnNameAndContentsRequestBody.model_rebuild()
CurrencyAmount.model_rebuild()
CustomRecordsQueryAndClauseRequestBody.model_rebuild()
CustomRecordsQueryOrClauseRequestBody.model_rebuild()
CustomRowColumnContentsByColumnNameRequestBody.model_rebuild()
CustomRowExternalKeyRequestBody.model_rebuild()
DefaultPaymentMethodAddressPolicy.model_rebuild()
DefaultPaymentMethodBankAccountPolicy.model_rebuild()
DefaultPaymentMethodCardPolicy.model_rebuild()
DefaultPaymentMethodResource.model_rebuild()
DeveloperApiMatrixColumnFilterRequestBody.model_rebuild()
DeveloperApiMatrixInputColumnDefRequestBody.model_rebuild()
DeveloperApiMatrixResultColumnDefRequestBody.model_rebuild()
DeveloperApiNativeRowIdentifierRequestBody.model_rebuild()
DeveloperApiNativeTableReferenceRequestBody.model_rebuild()
DeveloperApiNumberColumnTypeRequestBody.model_rebuild()
DeveloperApiResultNativeTableReferenceRequestBody.model_rebuild()
FieldOption.model_rebuild()
GlAccount.model_rebuild()
InventoryItemOption.model_rebuild()
Location.model_rebuild()
MatrixInputCellByNameRequestBody.model_rebuild()
MatrixResultCellByNameRequestBody.model_rebuild()
MatrixRowInputByNameRequestBody.model_rebuild()
Memo.model_rebuild()
NativeRowColumnContentsByColumnNameRequestBody.model_rebuild()
NativeRowIdentifierRequestBody.model_rebuild()
PatchAccountingConnectionDetailResourceBodySettings.model_rebuild()
PatchCardResourceBodySpendingRestrictions.model_rebuild()
PatchSpendLimitResourceBodyPermittedSpendTypes.model_rebuild()
PatchSpendLimitResourceBodySpendingRestrictions.model_rebuild()
PatchSpendLimitResourceBodySpendingRestrictionsLimit.model_rebuild()
PatchSpendLimitResourceBodySpendingRestrictionsTransactionAmountLimit.model_rebuild()
PatchVendorResourceBodyAddress.model_rebuild()
PostAccountingConnectionResourceBodySettings.model_rebuild()
PostApplicationResourceBodyApplicant.model_rebuild()
PostApplicationResourceBodyBusiness.model_rebuild()
PostApplicationResourceBodyBusinessAddress.model_rebuild()
PostApplicationResourceBodyBusinessIncorporation.model_rebuild()
PostApplicationResourceBodyControllingOfficer.model_rebuild()
PostApplicationResourceBodyControllingOfficerAddress.model_rebuild()
PostApplicationResourceBodyFinancialDetails.model_rebuild()
PostApplicationResourceBodyOauthAuthorizeParams.model_rebuild()
PostCardVaultCreationBodySpendingRestrictions.model_rebuild()
PostCardVaultCreationBodySpendingRestrictionsLimit.model_rebuild()
PostCardVaultCreationBodySpendingRestrictionsTransactionAmountLimit.model_rebuild()
PostDevApiAddMatrixResultColumnBodyNativeTable.model_rebuild()
PostPhysicalCardBodyFulfillment.model_rebuild()
PostPhysicalCardBodyFulfillmentCardPersonalization.model_rebuild()
PostPhysicalCardBodyFulfillmentCardPersonalizationText.model_rebuild()
PostPhysicalCardBodyFulfillmentCardPersonalizationTextNameLine1.model_rebuild()
PostPhysicalCardBodyFulfillmentCardPersonalizationTextNameLine2.model_rebuild()
PostPhysicalCardBodyFulfillmentShipping.model_rebuild()
PostPhysicalCardBodyFulfillmentShippingRecipientAddress.model_rebuild()
PostPhysicalCardBodyFulfillmentShippingReturnAddress.model_rebuild()
PostPhysicalCardBodySpendingRestrictions.model_rebuild()
PostSpendLimitCreationBodyPermittedSpendTypes.model_rebuild()
PostSpendLimitCreationBodySpendingRestrictions.model_rebuild()
PostSpendLimitCreationBodySpendingRestrictionsLimit.model_rebuild()
PostSpendLimitCreationBodySpendingRestrictionsTransactionAmountLimit.model_rebuild()
PostSpendProgramResourceBodyIssuanceRules.model_rebuild()
PostSpendProgramResourceBodyIssuanceRulesAutomatic.model_rebuild()
PostSpendProgramResourceBodyIssuanceRulesRequestable.model_rebuild()
PostSpendProgramResourceBodyPermittedSpendTypes.model_rebuild()
PostSpendProgramResourceBodySpendingRestrictions.model_rebuild()
PostSpendProgramResourceBodySpendingRestrictionsLimit.model_rebuild()
PostSpendProgramResourceBodySpendingRestrictionsTransactionAmountLimit.model_rebuild()
PostVendorAgreementListResourceBodyAgreementCustomRecords.model_rebuild()
PostVendorAgreementListResourceBodyEndDateRange.model_rebuild()
PostVendorAgreementListResourceBodyEndDateRangeEnd.model_rebuild()
PostVendorAgreementListResourceBodyEndDateRangeStart.model_rebuild()
PostVendorAgreementListResourceBodyLastDateToTerminateRange.model_rebuild()
PostVendorAgreementListResourceBodyLastDateToTerminateRangeEnd.model_rebuild()
PostVendorAgreementListResourceBodyLastDateToTerminateRangeStart.model_rebuild()
PostVendorAgreementListResourceBodyStartDateRange.model_rebuild()
PostVendorAgreementListResourceBodyStartDateRangeEnd.model_rebuild()
PostVendorAgreementListResourceBodyStartDateRangeStart.model_rebuild()
PostVendorBankAccountUpdateResourceBodyAchDetails.model_rebuild()
PostVendorBankAccountUpdateResourceBodyWireDetails.model_rebuild()
PostVendorListResourceBodyAddress.model_rebuild()
PostVendorListResourceBodyBusinessVendorContacts.model_rebuild()
PostVirtualCardBodySpendingRestrictions.model_rebuild()
PutSpendLimitResourceBodyPermittedSpendTypes.model_rebuild()
PutSpendLimitResourceBodySpendingRestrictions.model_rebuild()
PutSpendLimitResourceBodySpendingRestrictionsLimit.model_rebuild()
PutSpendLimitResourceBodySpendingRestrictionsTransactionAmountLimit.model_rebuild()
Receipt.model_rebuild()
Reimbursement.model_rebuild()
RowQueryFilterRequestBody.model_rebuild()
RowQueryGreaterThanClauseRequestBody.model_rebuild()
RowQueryGreaterThanOrEqualClauseRequestBody.model_rebuild()
RowQueryIsNotClauseRequestBody.model_rebuild()
RowQueryIsNullClauseRequestBody.model_rebuild()
RowQueryLessThanClauseRequestBody.model_rebuild()
RowQueryLessThanOrEqualClauseRequestBody.model_rebuild()
RowQueryOneOfClauseRequestBody.model_rebuild()
SpendLimitAccountingRulesDataRequestBody.model_rebuild()
TaxCodeOption.model_rebuild()
TaxRate.model_rebuild()
Transaction.model_rebuild()
Transfer.model_rebuild()
User.model_rebuild()
Vendor.model_rebuild()

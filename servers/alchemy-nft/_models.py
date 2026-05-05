"""
Alchemy Nft MCP Server - Pydantic Models

Generated: 2026-05-05 14:06:54 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "ComputeRarityV3Request",
    "GetCollectionMetadataV3Request",
    "GetCollectionsForOwnerV3Request",
    "GetContractMetadataBatchV3Request",
    "GetContractMetadataV3Request",
    "GetContractsForOwnerV3Request",
    "GetFloorPriceV3Request",
    "GetNftMetadataBatchV3Request",
    "GetNftMetadataV3Request",
    "GetNftSalesV3Request",
    "GetNfTsForCollectionV3Request",
    "GetNfTsForContractV3Request",
    "GetNfTsForOwnerV3Request",
    "GetNfTsRequest",
    "GetOwnersForCollectionRequest",
    "GetOwnersForContractV3Request",
    "GetOwnersForNftV3Request",
    "GetOwnersForTokenRequest",
    "IsAirdropNftV3Request",
    "IsAirdropRequest",
    "IsHolderOfCollectionRequest",
    "IsHolderOfContractV3Request",
    "IsSpamContractV3Request",
    "RefreshNftMetadataV3Request",
    "ReportSpamV3Request",
    "SearchContractMetadataV3Request",
    "SummarizeNftAttributesV3Request",
    "GetNftMetadataBatchV3BodyTokensItem",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_nfts_by_owner
class GetNfTsForOwnerV3RequestQuery(StrictModel):
    owner: str = Field(default=..., description="The wallet address to query for NFT ownership. Accepts standard hex addresses or ENS names (Ethereum Mainnet only).")
    contract_addresses: list[str] | None = Field(default=None, validation_alias="contractAddresses[]", serialization_alias="contractAddresses[]", description="Optional list of NFT contract addresses to filter results. Specify up to 45 contract addresses to narrow the response to specific collections.")
    with_metadata: bool | None = Field(default=None, validation_alias="withMetadata", serialization_alias="withMetadata", description="Include full NFT metadata in the response. Set to false to reduce payload size and improve response speed if metadata is not needed.")
    order_by: Literal["transferTime"] | None = Field(default=None, validation_alias="orderBy", serialization_alias="orderBy", description="Sort NFTs in the response by transfer time (newest first) or by default contract address and token ID. Transfer time ordering is available on major networks including Ethereum, Polygon, Arbitrum, Optimism, and Base.")
    spam_confidence_level: Literal["VERY_HIGH", "HIGH", "MEDIUM", "LOW"] | None = Field(default=None, validation_alias="spamConfidenceLevel", serialization_alias="spamConfidenceLevel", description="Filter out suspected spam NFTs based on confidence level. Higher levels (VERY_HIGH, HIGH) remove more spam but may exclude legitimate tokens. Defaults vary by network and requires a paid tier.")
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="Number of NFTs to return per page, up to a maximum of 100. Defaults to 100 if not specified.")
class GetNfTsForOwnerV3Request(StrictModel):
    """Retrieves all NFTs currently owned by a specified wallet address. Supports Ethereum, Polygon, Arbitrum, Optimism, Base, and other major networks with optional filtering, metadata inclusion, and custom ordering."""
    query: GetNfTsForOwnerV3RequestQuery

# Operation: list_nfts_for_contract
class GetNfTsForContractV3RequestQuery(StrictModel):
    contract_address: str = Field(default=..., validation_alias="contractAddress", serialization_alias="contractAddress", description="The contract address of the NFT collection. Must be a valid ERC721 or ERC1155 contract address.")
    with_metadata: bool | None = Field(default=None, validation_alias="withMetadata", serialization_alias="withMetadata", description="Whether to include full NFT metadata in the response. Set to false to reduce payload size and improve response speed if metadata is not needed.")
    start_token: str | None = Field(default=None, validation_alias="startToken", serialization_alias="startToken", description="Token ID offset for pagination, allowing you to start from a specific position or fetch multiple token ranges in parallel. Accepts hexadecimal or decimal format.")
    limit: int | None = Field(default=None, description="Maximum number of NFTs to return per request. Defaults to 100 if not specified.")
class GetNfTsForContractV3Request(StrictModel):
    """Retrieves all NFTs associated with a specific NFT contract address. Supports ERC721 and ERC1155 standards across Ethereum and multiple Layer 2 networks including Polygon, Arbitrum, Optimism, and Base."""
    query: GetNfTsForContractV3RequestQuery

# Operation: list_nfts_for_collection
class GetNfTsForCollectionV3RequestQuery(StrictModel):
    with_metadata: bool | None = Field(default=None, validation_alias="withMetadata", serialization_alias="withMetadata", description="When true, includes full NFT metadata in the response; when false, reduces payload size for faster queries. Defaults to true.")
    start_token: str | None = Field(default=None, validation_alias="startToken", serialization_alias="startToken", description="Token ID offset for pagination, specified as either a hexadecimal or decimal string. Use this to resume from a previous position or fetch multiple token ranges in parallel.")
    limit: int | None = Field(default=None, description="Maximum number of NFTs to return per request. Defaults to 100.")
    contract_address: str | None = Field(default=None, validation_alias="contractAddress", serialization_alias="contractAddress", description="String - Contract address for the NFT contract (ERC721 and ERC1155 supported).")
    collection_slug: str | None = Field(default=None, validation_alias="collectionSlug", serialization_alias="collectionSlug", description="String - OpenSea slug for the NFT collection.")
class GetNfTsForCollectionV3Request(StrictModel):
    """Retrieves all NFTs associated with a specific NFT collection across Ethereum and supported Layer 2 networks including Polygon, Arbitrum, Optimism, and Base. Supports pagination and optional metadata inclusion."""
    query: GetNfTsForCollectionV3RequestQuery | None = None

# Operation: get_nft_metadata
class GetNftMetadataV3RequestQuery(StrictModel):
    contract_address: str = Field(default=..., validation_alias="contractAddress", serialization_alias="contractAddress", description="The contract address of the NFT collection. Must be a valid ERC721 or ERC1155 contract address.")
    token_id: str = Field(default=..., validation_alias="tokenId", serialization_alias="tokenId", description="The unique identifier of the NFT token. Can be provided in either hexadecimal or decimal format.")
    token_type: str | None = Field(default=None, validation_alias="tokenType", serialization_alias="tokenType", description="The token standard type: either 'ERC721' or 'ERC1155'. Specifying this improves query performance.")
class GetNftMetadataV3Request(StrictModel):
    """Retrieve detailed metadata for a specific NFT by its token ID and contract address. Supports ERC721 and ERC1155 tokens across Ethereum and multiple Layer 2 networks including Polygon, Arbitrum, Optimism, and Base."""
    query: GetNftMetadataV3RequestQuery

# Operation: batch_retrieve_nft_metadata
class GetNftMetadataBatchV3RequestBody(StrictModel):
    tokens: list[GetNftMetadataBatchV3BodyTokensItem] = Field(default=..., description="Array of token objects to fetch metadata for, with a maximum of 100 items per request. Each token object should specify the contract address and token ID.")
class GetNftMetadataBatchV3Request(StrictModel):
    """Retrieve metadata for multiple NFT contracts in a single request. Supports up to 100 tokens across Ethereum, Polygon, Arbitrum, Optimism, Base, World Chain, and other supported networks."""
    body: GetNftMetadataBatchV3RequestBody

# Operation: get_nft_contract_metadata
class GetContractMetadataV3RequestQuery(StrictModel):
    contract_address: str = Field(default=..., validation_alias="contractAddress", serialization_alias="contractAddress", description="The blockchain address of the NFT contract. Must be a valid contract address for ERC721 or ERC1155 token standards.")
class GetContractMetadataV3Request(StrictModel):
    """Retrieve high-level metadata for an NFT contract or collection, including details about the contract itself. Supports ERC721 and ERC1155 contracts across Ethereum and multiple Layer 2 networks."""
    query: GetContractMetadataV3RequestQuery

# Operation: get_collection_metadata
class GetCollectionMetadataV3RequestQuery(StrictModel):
    collection_slug: str = Field(default=..., validation_alias="collectionSlug", serialization_alias="collectionSlug", description="The OpenSea collection slug—a URL-friendly identifier for the NFT collection (e.g., 'boredapeyachtclub').")
class GetCollectionMetadataV3Request(StrictModel):
    """Retrieve high-level metadata and contract information for an NFT collection using its OpenSea slug. Supported across Ethereum and multiple Layer 2 networks including Polygon, Arbitrum, Optimism, and Base."""
    query: GetCollectionMetadataV3RequestQuery

# Operation: batch_get_contract_metadata
class GetContractMetadataBatchV3RequestBody(StrictModel):
    contract_addresses: list[str] | None = Field(default=None, validation_alias="contractAddresses", serialization_alias="contractAddresses", description="Array of contract addresses to retrieve metadata for. Each address should be a valid Ethereum address format. If not provided, defaults to a sample set of addresses.")
class GetContractMetadataBatchV3Request(StrictModel):
    """Retrieve metadata for multiple contract addresses in a single request. Efficiently fetch contract information such as name, symbol, and decimals for a batch of addresses."""
    body: GetContractMetadataBatchV3RequestBody | None = None

# Operation: get_nft_owners
class GetOwnersForNftV3RequestQuery(StrictModel):
    contract_address: str = Field(default=..., validation_alias="contractAddress", serialization_alias="contractAddress", description="The contract address of the NFT collection. Must be a valid ERC721 or ERC1155 contract address.")
    token_id: str = Field(default=..., validation_alias="tokenId", serialization_alias="tokenId", description="The unique identifier of the token within the contract. Can be provided in either hexadecimal or decimal format.")
class GetOwnersForNftV3Request(StrictModel):
    """Retrieves the current owner(s) of a specific NFT token. Supports ERC721 and ERC1155 contracts across Ethereum, Polygon, Arbitrum, Optimism, Base, World Chain, and other supported networks."""
    query: GetOwnersForNftV3RequestQuery

# Operation: list_nft_contract_owners
class GetOwnersForContractV3RequestQuery(StrictModel):
    contract_address: str = Field(default=..., validation_alias="contractAddress", serialization_alias="contractAddress", description="The blockchain address of the NFT contract to query. Must be a valid ERC721 or ERC1155 contract address.")
    with_token_balances: bool | None = Field(default=None, validation_alias="withTokenBalances", serialization_alias="withTokenBalances", description="When enabled, includes the token balance for each token ID owned by each address. Disabled by default for faster responses.")
class GetOwnersForContractV3Request(StrictModel):
    """Retrieves all wallet addresses that own NFTs from a specific contract. Supports ERC721 and ERC1155 tokens across Ethereum and multiple Layer 2 networks including Polygon, Arbitrum, Optimism, and Base."""
    query: GetOwnersForContractV3RequestQuery

# Operation: check_spam_contract
class IsSpamContractV3RequestQuery(StrictModel):
    contract_address: str = Field(default=..., validation_alias="contractAddress", serialization_alias="contractAddress", description="The blockchain address of the NFT contract to check. Supports ERC721 and ERC1155 contract standards.")
class IsSpamContractV3Request(StrictModel):
    """Checks whether a specific NFT contract is flagged as spam by Alchemy. This helps identify potentially fraudulent or low-quality NFT collections across supported blockchain networks."""
    query: IsSpamContractV3RequestQuery

# Operation: check_nft_airdrop
class IsAirdropNftV3RequestQuery(StrictModel):
    contract_address: str = Field(default=..., validation_alias="contractAddress", serialization_alias="contractAddress", description="The contract address of the NFT collection. Supports both ERC721 and ERC1155 token standards.")
    token_id: str = Field(default=..., validation_alias="tokenId", serialization_alias="tokenId", description="The unique identifier of the token within the contract. Can be provided in either hexadecimal or decimal format.")
class IsAirdropNftV3Request(StrictModel):
    """Determines whether a specific NFT token was received as an airdrop, defined as an NFT minted to a user address in a transaction sent by a different address. Available on Ethereum mainnet and Polygon (mainnet, amoy, and mumbai)."""
    query: IsAirdropNftV3RequestQuery

# Operation: get_nft_collection_attribute_summary
class SummarizeNftAttributesV3RequestQuery(StrictModel):
    contract_address: str = Field(default=..., validation_alias="contractAddress", serialization_alias="contractAddress", description="The blockchain contract address for the NFT collection to analyze. Supports both ERC721 and ERC1155 token standards.")
class SummarizeNftAttributesV3Request(StrictModel):
    """Retrieve a summary of attribute prevalence and distribution for an NFT collection. This endpoint analyzes trait frequency across all NFTs in a contract to provide insights into attribute rarity and composition. Available on Ethereum mainnet and Polygon (mainnet and Mumbai)."""
    query: SummarizeNftAttributesV3RequestQuery

# Operation: get_nft_collection_floor_prices
class GetFloorPriceV3RequestQuery(StrictModel):
    contract_address: str = Field(default=..., validation_alias="contractAddress", serialization_alias="contractAddress", description="The contract address of the NFT collection (supports both ERC721 and ERC1155 standards). This identifies which collection's floor prices to retrieve.")
class GetFloorPriceV3Request(StrictModel):
    """Retrieves the current floor prices for an NFT collection across supported marketplaces (OpenSea and Looksrare on Ethereum mainnet). Use this to monitor pricing trends and compare floor prices across different trading platforms."""
    query: GetFloorPriceV3RequestQuery

# Operation: search_contract_metadata
class SearchContractMetadataV3RequestQuery(StrictModel):
    query: str = Field(default=..., description="The search keyword or phrase to find within contract metadata fields.")
class SearchContractMetadataV3Request(StrictModel):
    """Search for keywords across metadata of ERC-721 and ERC-1155 smart contracts. Currently available on Ethereum, Polygon, Arbitrum, Optimism, and Base networks."""
    query: SearchContractMetadataV3RequestQuery

# Operation: check_nft_holder
class IsHolderOfContractV3RequestQuery(StrictModel):
    wallet: str = Field(default=..., description="The wallet address to check for NFT holdings from the specified contract.")
    contract_address: str = Field(default=..., validation_alias="contractAddress", serialization_alias="contractAddress", description="The NFT contract address to check against. Must be a valid ERC721 or ERC1155 contract.")
class IsHolderOfContractV3Request(StrictModel):
    """Verify whether a wallet address holds any NFTs from a specific contract. Supports ERC721 and ERC1155 tokens across Ethereum and multiple Layer 2 networks including Polygon, Arbitrum, Optimism, and Base."""
    query: IsHolderOfContractV3RequestQuery

# Operation: calculate_nft_attribute_rarity
class ComputeRarityV3RequestQuery(StrictModel):
    contract_address: str = Field(default=..., validation_alias="contractAddress", serialization_alias="contractAddress", description="The contract address of the NFT collection. Supports both ERC721 and ERC1155 token standards.")
    token_id: str = Field(default=..., validation_alias="tokenId", serialization_alias="tokenId", description="The unique identifier of the NFT token within the contract. Can be provided in either hexadecimal or decimal format.")
class ComputeRarityV3Request(StrictModel):
    """Calculates the rarity score for each attribute of a specific NFT by analyzing how uncommon each attribute is within the collection. Available on Ethereum mainnet and Polygon (mainnet and Mumbai testnet)."""
    query: ComputeRarityV3RequestQuery

# Operation: list_nft_sales
class GetNftSalesV3RequestQuery(StrictModel):
    from_block: str | None = Field(default=None, validation_alias="fromBlock", serialization_alias="fromBlock", description="The starting block number for fetching NFT sales data. Accepts decimal integers, hexadecimal integers (prefixed with 0x), or 'latest'. Defaults to block 0.")
    to_block: str | None = Field(default=None, validation_alias="toBlock", serialization_alias="toBlock", description="The ending block number for fetching NFT sales data. Accepts decimal integers, hexadecimal integers (prefixed with 0x), or 'latest'. Defaults to the latest block.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results relative to the block range. Choose 'asc' for ascending order from the start block or 'desc' for descending order. Defaults to descending.")
    marketplace: Literal["seaport", "looksrare", "x2y2", "wyvern", "blur", "cryptopunks"] | None = Field(default=None, description="Filter sales by a specific NFT marketplace. Supported values are seaport, looksrare, x2y2, wyvern, blur, and cryptopunks. Omit to return sales from all supported marketplaces.")
    token_id: str | None = Field(default=None, validation_alias="tokenId", serialization_alias="tokenId", description="Filter sales to a specific NFT token ID within the collection. Omit to return sales for all token IDs in the collection.")
    taker: Literal["BUYER", "SELLER"] | None = Field(default=None, description="Filter by the participant role in the trade. Use 'BUYER' to return sales where the specified address was the buyer, or 'SELLER' for the seller role. Omit to return both buyer and seller trades.")
    limit: int | None = Field(default=None, description="Maximum number of NFT sales to return in the response. Accepts values up to 1000, which is also the default.")
class GetNftSalesV3Request(StrictModel):
    """Retrieves NFT sales transactions that have occurred through on-chain marketplaces. Supports filtering by block range, marketplace, collection, token ID, and trade participant role. Available on Ethereum (Seaport, Wyvern, X2Y2, Blur, LooksRare, Cryptopunks), Polygon (Seaport), and Optimism (Seaport) mainnets."""
    query: GetNftSalesV3RequestQuery | None = None

# Operation: list_nft_contracts_by_owner
class GetContractsForOwnerV3RequestQuery(StrictModel):
    owner: str = Field(default=..., description="The wallet address to query for NFT contracts. Accepts standard Ethereum addresses or ENS names (on Ethereum Mainnet).")
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="Number of contracts to return per page, up to a maximum of 100. Defaults to 100.")
    with_metadata: bool | None = Field(default=None, validation_alias="withMetadata", serialization_alias="withMetadata", description="Include detailed NFT metadata in the response. Disabling this reduces payload size and may improve response speed. Defaults to true.")
    order_by: Literal["transferTime"] | None = Field(default=None, validation_alias="orderBy", serialization_alias="orderBy", description="Sort contracts by transfer time (newest first) or by default contract address and token ID ordering. Transfer time ordering is supported on major networks including Ethereum, Optimism, Polygon, Base, and Arbitrum.")
    spam_confidence_level: Literal["VERY_HIGH", "HIGH", "MEDIUM", "LOW"] | None = Field(default=None, validation_alias="spamConfidenceLevel", serialization_alias="spamConfidenceLevel", description="Filter out spam contracts based on confidence level. Higher confidence levels filter more aggressively (e.g., HIGH filters both HIGH and VERY_HIGH confidence spam). Defaults vary by network: VERY_HIGH for Ethereum Mainnet, MEDIUM for Polygon. Available only on paid tier accounts.")
class GetContractsForOwnerV3Request(StrictModel):
    """Retrieves all NFT contracts owned by a specified address. Optionally returns detailed metadata and supports filtering by spam confidence level and custom ordering."""
    query: GetContractsForOwnerV3RequestQuery

# Operation: list_nft_collections_by_owner
class GetCollectionsForOwnerV3RequestQuery(StrictModel):
    owner: str = Field(default=..., description="The wallet address to query for NFT collections. Accepts standard Ethereum addresses or ENS names (on Ethereum Mainnet only).")
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="Number of collections to return per page, ranging from 1 to 100. Defaults to 100 for maximum results per request.")
    with_metadata: bool | None = Field(default=None, validation_alias="withMetadata", serialization_alias="withMetadata", description="Include full NFT metadata in the response when enabled. Disable to reduce payload size and improve response speed if metadata is not needed.")
class GetCollectionsForOwnerV3Request(StrictModel):
    """Retrieves all NFT collections owned by a specified address on Ethereum. Returns collection details with optional metadata to support portfolio analysis and collection discovery."""
    query: GetCollectionsForOwnerV3RequestQuery

# Operation: report_spam_address
class ReportSpamV3RequestQuery(StrictModel):
    address: str = Field(default=..., description="The blockchain address to report, provided as a hexadecimal string (e.g., starting with 0x).")
    is_spam: bool = Field(default=..., validation_alias="isSpam", serialization_alias="isSpam", description="Set to true to mark the address as spam, or false to remove a previous spam report.")
class ReportSpamV3Request(StrictModel):
    """Report a blockchain address as spam to help protect the network. This operation flags addresses suspected of malicious activity on supported chains including Ethereum, Polygon, Base, Arbitrum, Optimism, and others."""
    query: ReportSpamV3RequestQuery

# Operation: refresh_nft_metadata
class RefreshNftMetadataV3RequestBody(StrictModel):
    contract_address: str = Field(default=..., validation_alias="contractAddress", serialization_alias="contractAddress", description="The contract address of the NFT collection containing the token you want to refresh. Must be a valid Ethereum-format address.")
    token_id: str = Field(default=..., validation_alias="tokenId", serialization_alias="tokenId", description="The unique token ID within the specified contract that you want to refresh. Must correspond to an existing token in the contract.")
class RefreshNftMetadataV3Request(StrictModel):
    """Submits a request to refresh the cached metadata for a specific NFT token. Supported on Ethereum (Mainnet & Sepolia), Polygon (Mainnet, Mumbai & Amoy), Arbitrum One, Optimism, and Base mainnets."""
    body: RefreshNftMetadataV3RequestBody

# Operation: list_nfts
class GetNfTsRequestQuery(StrictModel):
    owner: str = Field(default=..., description="The wallet address to query for NFT ownership. Accepts standard Ethereum addresses or ENS names (on Ethereum Mainnet).")
    contract_addresses: list[str] | None = Field(default=None, validation_alias="contractAddresses[]", serialization_alias="contractAddresses[]", description="Optional list of contract addresses to filter results. Specify up to 45 contract addresses to narrow the response to specific NFT collections.")
    with_metadata: bool | None = Field(default=None, validation_alias="withMetadata", serialization_alias="withMetadata", description="Whether to include full NFT metadata in the response. Set to false to reduce payload size and improve response speed; defaults to true.")
    order_by: Literal["transferTime"] | None = Field(default=None, validation_alias="orderBy", serialization_alias="orderBy", description="How to order NFTs in the response. Use 'transferTime' to sort by most recent transfers first (supported on major networks). If unspecified, NFTs are ordered by contract address and token ID.")
    spam_confidence_level: Literal["VERY_HIGH", "HIGH", "MEDIUM", "LOW"] | None = Field(default=None, validation_alias="spamConfidenceLevel", serialization_alias="spamConfidenceLevel", description="Filter spam NFTs by confidence level. Choose from VERY_HIGH, HIGH, MEDIUM, or LOW—any spam at that level or higher will be excluded. Defaults vary by network (VERY_HIGH for Ethereum Mainnet, MEDIUM for Polygon). Available on paid tiers only.")
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="Number of NFTs to return per page, up to a maximum of 100. Defaults to 100.")
class GetNfTsRequest(StrictModel):
    """Retrieves all NFTs currently owned by a specified address, with optional filtering by contract, metadata inclusion, and spam confidence levels."""
    query: GetNfTsRequestQuery

# Operation: get_token_owners
class GetOwnersForTokenRequestQuery(StrictModel):
    contract_address: str = Field(default=..., validation_alias="contractAddress", serialization_alias="contractAddress", description="The blockchain contract address of the NFT collection. Must be a valid Ethereum address (e.g., ERC-721 or ERC-1155 contract).")
    token_id: str = Field(default=..., validation_alias="tokenId", serialization_alias="tokenId", description="The unique identifier of the token within the contract. Accepts both hexadecimal and decimal formats.")
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="Maximum number of owner records to return per page. Use this to control response size when a token has multiple owners.")
class GetOwnersForTokenRequest(StrictModel):
    """Retrieve the owner(s) of a specific NFT token by contract address and token ID. Supports pagination to handle multiple owners."""
    query: GetOwnersForTokenRequestQuery

# Operation: list_nft_collection_owners
class GetOwnersForCollectionRequestQuery(StrictModel):
    contract_address: str = Field(default=..., validation_alias="contractAddress", serialization_alias="contractAddress", description="The blockchain contract address for the NFT collection. Supports both ERC721 and ERC1155 token standards.")
    with_token_balances: bool | None = Field(default=None, validation_alias="withTokenBalances", serialization_alias="withTokenBalances", description="When enabled, includes the token balance for each token ID owned by each address. Disabled by default for faster responses.")
class GetOwnersForCollectionRequest(StrictModel):
    """Retrieves all wallet addresses that own NFTs from a specified ERC721 or ERC1155 contract, with optional token balance details per owner."""
    query: GetOwnersForCollectionRequestQuery

# Operation: check_token_airdrop
class IsAirdropRequestQuery(StrictModel):
    contract_address: str = Field(default=..., validation_alias="contractAddress", serialization_alias="contractAddress", description="The blockchain contract address for the NFT collection. Supports both ERC721 and ERC1155 token standards.")
    token_id: str = Field(default=..., validation_alias="tokenId", serialization_alias="tokenId", description="The unique identifier of the token within the contract. Can be provided in either hexadecimal or decimal format.")
class IsAirdropRequest(StrictModel):
    """Determines whether an NFT token was distributed as an airdrop by checking if it was minted to a user address in a transaction sent by a different address."""
    query: IsAirdropRequestQuery

# Operation: check_wallet_nft_collection_ownership
class IsHolderOfCollectionRequestQuery(StrictModel):
    wallet: str = Field(default=..., description="The wallet address to check for NFT ownership. Can be a standard hexadecimal address or an ENS name (Ethereum Mainnet only).")
    contract_address: str = Field(default=..., validation_alias="contractAddress", serialization_alias="contractAddress", description="The contract address of the NFT collection to check. Must be a valid ERC721 or ERC1155 contract address.")
class IsHolderOfCollectionRequest(StrictModel):
    """Verifies whether a specific wallet address holds at least one NFT from a given collection. Supports both ERC721 and ERC1155 token standards, and accepts wallet addresses in ENS format on Ethereum Mainnet."""
    query: IsHolderOfCollectionRequestQuery

# ============================================================================
# Component Models
# ============================================================================

class GetNftMetadataBatchV3BodyTokensItem(PermissiveModel):
    contract_address: str = Field(..., validation_alias="contractAddress", serialization_alias="contractAddress")
    token_id: str = Field(..., validation_alias="tokenId", serialization_alias="tokenId")
    token_type: str | None = Field(None, validation_alias="tokenType", serialization_alias="tokenType")


# Rebuild models to resolve forward references (required for circular refs)
GetNftMetadataBatchV3BodyTokensItem.model_rebuild()

"""
Polygon Api MCP Server - Pydantic Models

Generated: 2026-04-14 18:30:55 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field, RootModel

__all__ = [
    "AggregatesRequest",
    "AggregatesV1Request",
    "CryptoEmaRequest",
    "CryptoMacdRequest",
    "CryptoRsiRequest",
    "CryptoSmaRequest",
    "DeprecatedGetHistoricForexQuotesRequest",
    "DeprecatedGetHistoricStocksQuotesRequest",
    "EmaRequest",
    "ForexEmaRequest",
    "ForexMacdRequest",
    "ForexRsiRequest",
    "ForexSmaRequest",
    "GetBenzingaV1AnalystInsightsRequest",
    "GetBenzingaV1AnalystsRequest",
    "GetBenzingaV1BullsBearsSayRequest",
    "GetBenzingaV1ConsensusRatingsRequest",
    "GetBenzingaV1EarningsRequest",
    "GetBenzingaV1FirmsRequest",
    "GetBenzingaV1GuidanceRequest",
    "GetBenzingaV1RatingsRequest",
    "GetBenzingaV2NewsRequest",
    "GetConsumerSpendingEuV1MerchantAggregatesRequest",
    "GetConsumerSpendingEuV1MerchantHierarchyRequest",
    "GetCryptoAggregatesRequest",
    "GetCryptoOpenCloseRequest",
    "GetCryptoSnapshotDirectionRequest",
    "GetCryptoSnapshotTickerRequest",
    "GetEtfGlobalV1AnalyticsRequest",
    "GetEtfGlobalV1ConstituentsRequest",
    "GetEtfGlobalV1FundFlowsRequest",
    "GetEtfGlobalV1ProfilesRequest",
    "GetEtfGlobalV1TaxonomiesRequest",
    "GetEventsRequest",
    "GetFedV1InflationExpectationsRequest",
    "GetFedV1InflationRequest",
    "GetFedV1LaborMarketRequest",
    "GetFedV1TreasuryYieldsRequest",
    "GetFilingFileRequest",
    "GetFilingRequest",
    "GetForexAggregatesRequest",
    "GetForexSnapshotDirectionRequest",
    "GetForexSnapshotTickerRequest",
    "GetFuturesVXContractsRequest",
    "GetFuturesVXExchangesRequest",
    "GetFuturesVXMarketStatusRequest",
    "GetFuturesVXProductsRequest",
    "GetFuturesVXQuotesRequest",
    "GetFuturesVXSchedulesRequest",
    "GetFuturesVXSnapshotRequest",
    "GetFuturesVXTradesRequest",
    "GetGroupedCryptoAggregatesRequest",
    "GetGroupedForexAggregatesRequest",
    "GetGroupedStocksAggregatesRequest",
    "GetIndicesAggregatesRequest",
    "GetIndicesOpenCloseRequest",
    "GetOptionsAggregatesRequest",
    "GetOptionsContractRequest",
    "GetOptionsOpenCloseRequest",
    "GetPreviousCryptoAggregatesRequest",
    "GetPreviousForexAggregatesRequest",
    "GetPreviousIndicesAggregatesRequest",
    "GetPreviousOptionsAggregatesRequest",
    "GetPreviousStocksAggregatesRequest",
    "GetRelatedCompaniesRequest",
    "GetStocksAggregatesRequest",
    "GetStocksFilings10KVXSectionsRequest",
    "GetStocksFilings8KVXTextRequest",
    "GetStocksFilingsVX13FRequest",
    "GetStocksFilingsVXIndexRequest",
    "GetStocksFilingsVXRiskFactorsRequest",
    "GetStocksFinancialsV1BalanceSheetsRequest",
    "GetStocksFinancialsV1CashFlowStatementsRequest",
    "GetStocksFinancialsV1IncomeStatementsRequest",
    "GetStocksFinancialsV1RatiosRequest",
    "GetStocksOpenCloseRequest",
    "GetStocksSnapshotDirectionRequest",
    "GetStocksSnapshotTickerRequest",
    "GetStocksSnapshotTickersRequest",
    "GetStocksTaxonomiesVXRiskFactorsRequest",
    "GetStocksV1DividendsRequest",
    "GetStocksV1ShortInterestRequest",
    "GetStocksV1ShortVolumeRequest",
    "GetStocksV1SplitsRequest",
    "GetStocksVXFloatRequest",
    "GetTickerRequest",
    "GetTmxV1CorporateEventsRequest",
    "IndicesEmaRequest",
    "IndicesMacdRequest",
    "IndicesRsiRequest",
    "IndicesSmaRequest",
    "IndicesSnapshotRequest",
    "LastQuoteCurrenciesRequest",
    "LastQuoteRequest",
    "LastTradeCryptoRequest",
    "LastTradeOptionsRequest",
    "LastTradeRequest",
    "ListConditionsRequest",
    "ListDividendsRequest",
    "ListExchangesRequest",
    "ListFilingFilesRequest",
    "ListFilingsRequest",
    "ListFinancialsRequest",
    "ListIpOsRequest",
    "ListNewsRequest",
    "ListOptionsContractsRequest",
    "ListStockSplitsRequest",
    "ListTickersRequest",
    "ListTickerTypesRequest",
    "MacdRequest",
    "OptionContractRequest",
    "OptionsChainRequest",
    "OptionsEmaRequest",
    "OptionsMacdRequest",
    "OptionsRsiRequest",
    "OptionsSmaRequest",
    "QuotesFxRequest",
    "QuotesOptionsRequest",
    "QuotesRequest",
    "RealTimeCurrencyConversionRequest",
    "RsiRequest",
    "SmaRequest",
    "SnapshotsRequest",
    "TradesCryptoRequest",
    "TradesOptionsRequest",
    "TradesRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_analyst_insights
class GetBenzingaV1AnalystInsightsRequestQuery(StrictModel):
    firm_any_of: str | None = Field(default=None, validation_alias="firm.any_of", serialization_alias="firm.any_of", description="Filter results to analyst firms matching any of the specified values. Use comma-separated list for multiple firms.")
    firm_gt: str | None = Field(default=None, validation_alias="firm.gt", serialization_alias="firm.gt", description="Filter results to analyst firms lexicographically greater than the specified value.")
    firm_gte: str | None = Field(default=None, validation_alias="firm.gte", serialization_alias="firm.gte", description="Filter results to analyst firms lexicographically greater than or equal to the specified value.")
    firm_lt: str | None = Field(default=None, validation_alias="firm.lt", serialization_alias="firm.lt", description="Filter results to analyst firms lexicographically less than the specified value.")
    firm_lte: str | None = Field(default=None, validation_alias="firm.lte", serialization_alias="firm.lte", description="Filter results to analyst firms lexicographically less than or equal to the specified value.")
    rating_action_any_of: str | None = Field(default=None, validation_alias="rating_action.any_of", serialization_alias="rating_action.any_of", description="Filter results to rating actions matching any of the specified values. Use comma-separated list for multiple actions (e.g., upgrade, downgrade, initiate).")
    rating_action_gt: str | None = Field(default=None, validation_alias="rating_action.gt", serialization_alias="rating_action.gt", description="Filter results to rating actions lexicographically greater than the specified value.")
    rating_action_gte: str | None = Field(default=None, validation_alias="rating_action.gte", serialization_alias="rating_action.gte", description="Filter results to rating actions lexicographically greater than or equal to the specified value.")
    rating_action_lt: str | None = Field(default=None, validation_alias="rating_action.lt", serialization_alias="rating_action.lt", description="Filter results to rating actions lexicographically less than the specified value.")
    rating_action_lte: str | None = Field(default=None, validation_alias="rating_action.lte", serialization_alias="rating_action.lte", description="Filter results to rating actions lexicographically less than or equal to the specified value.")
    benzinga_rating_id_any_of: str | None = Field(default=None, validation_alias="benzinga_rating_id.any_of", serialization_alias="benzinga_rating_id.any_of", description="Filter results to Benzinga rating IDs matching any of the specified values. Use comma-separated list for multiple IDs.")
    benzinga_rating_id_gt: str | None = Field(default=None, validation_alias="benzinga_rating_id.gt", serialization_alias="benzinga_rating_id.gt", description="Filter results to Benzinga rating IDs numerically greater than the specified value.")
    benzinga_rating_id_gte: str | None = Field(default=None, validation_alias="benzinga_rating_id.gte", serialization_alias="benzinga_rating_id.gte", description="Filter results to Benzinga rating IDs numerically greater than or equal to the specified value.")
    benzinga_rating_id_lt: str | None = Field(default=None, validation_alias="benzinga_rating_id.lt", serialization_alias="benzinga_rating_id.lt", description="Filter results to Benzinga rating IDs numerically less than the specified value.")
    benzinga_rating_id_lte: str | None = Field(default=None, validation_alias="benzinga_rating_id.lte", serialization_alias="benzinga_rating_id.lte", description="Filter results to Benzinga rating IDs numerically less than or equal to the specified value.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 100 if not specified. Maximum allowed value is 50,000.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with sort direction appended to each column using '.asc' or '.desc'. Defaults to sorting by 'last_updated' in descending order if not specified.")
class GetBenzingaV1AnalystInsightsRequest(StrictModel):
    """Retrieve analyst insights and ratings for publicly traded companies, including recommendations and price targets from financial analysts. Filter by analyst firm, rating actions, or Benzinga rating IDs, with support for sorting and pagination."""
    query: GetBenzingaV1AnalystInsightsRequestQuery | None = None

# Operation: list_analysts
class GetBenzingaV1AnalystsRequestQuery(StrictModel):
    firm_name: str | None = Field(default=None, description="Filter results to analysts from a specific research firm or investment bank. Optional filter that narrows results to a single firm.")
    full_name: str | None = Field(default=None, description="Filter results to a specific analyst by their full name. Optional filter that narrows results to matching analysts.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Defaults to 100 if not specified. Must be between 1 and 50,000.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with sort direction specified per column using '.asc' or '.desc' suffix. Defaults to sorting by full_name in ascending order if not specified.")
class GetBenzingaV1AnalystsRequest(StrictModel):
    """Retrieve a comprehensive list of financial analysts with their performance metrics and identification details. Filter by research firm or analyst name, and customize sorting and result limits."""
    query: GetBenzingaV1AnalystsRequestQuery | None = None

# Operation: list_bulls_bears_say
class GetBenzingaV1BullsBearsSayRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response, ranging from 1 to 5000. Defaults to 100 if not specified.", ge=1, le=5001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort results by, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by ticker in descending order if not specified.")
class GetBenzingaV1BullsBearsSayRequest(StrictModel):
    """Retrieve analyst bull and bear case summaries for publicly traded companies, enabling investors to review both bullish and bearish investment arguments for informed decision-making."""
    query: GetBenzingaV1BullsBearsSayRequestQuery | None = None

# Operation: get_consensus_ratings
class GetBenzingaV1ConsensusRatingsRequestPath(StrictModel):
    ticker: str = Field(default=..., description="The stock ticker symbol for which to retrieve consensus ratings.")
class GetBenzingaV1ConsensusRatingsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return, ranging from 1 to 50,000. Defaults to 100 if not specified.", ge=1, le=50001)
class GetBenzingaV1ConsensusRatingsRequest(StrictModel):
    """Retrieve aggregated analyst consensus ratings and price targets for a stock ticker, including detailed rating breakdowns and statistical insights across multiple analysts."""
    path: GetBenzingaV1ConsensusRatingsRequestPath
    query: GetBenzingaV1ConsensusRatingsRequestQuery | None = None

# Operation: list_earnings
class GetBenzingaV1EarningsRequestQuery(StrictModel):
    date_status_any_of: str | None = Field(default=None, validation_alias="date_status.any_of", serialization_alias="date_status.any_of", description="Filter results to earnings records with a date_status matching any of the specified values. Use comma-separated values to filter by multiple statuses.")
    date_status_gt: str | None = Field(default=None, validation_alias="date_status.gt", serialization_alias="date_status.gt", description="Filter results to earnings records where date_status is strictly greater than the specified value.")
    date_status_gte: str | None = Field(default=None, validation_alias="date_status.gte", serialization_alias="date_status.gte", description="Filter results to earnings records where date_status is greater than or equal to the specified value.")
    date_status_lt: str | None = Field(default=None, validation_alias="date_status.lt", serialization_alias="date_status.lt", description="Filter results to earnings records where date_status is strictly less than the specified value.")
    date_status_lte: str | None = Field(default=None, validation_alias="date_status.lte", serialization_alias="date_status.lte", description="Filter results to earnings records where date_status is less than or equal to the specified value.")
    eps_surprise_percent_any_of: str | None = Field(default=None, validation_alias="eps_surprise_percent.any_of", serialization_alias="eps_surprise_percent.any_of", description="Filter results to earnings records with an EPS surprise percent matching any of the specified values. Use comma-separated floating-point numbers to filter by multiple surprise percentages.")
    eps_surprise_percent_gt: float | None = Field(default=None, validation_alias="eps_surprise_percent.gt", serialization_alias="eps_surprise_percent.gt", description="Filter results to earnings records where EPS surprise percent is strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    eps_surprise_percent_gte: float | None = Field(default=None, validation_alias="eps_surprise_percent.gte", serialization_alias="eps_surprise_percent.gte", description="Filter results to earnings records where EPS surprise percent is greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    eps_surprise_percent_lt: float | None = Field(default=None, validation_alias="eps_surprise_percent.lt", serialization_alias="eps_surprise_percent.lt", description="Filter results to earnings records where EPS surprise percent is strictly less than the specified value.", json_schema_extra={'format': 'double'})
    eps_surprise_percent_lte: float | None = Field(default=None, validation_alias="eps_surprise_percent.lte", serialization_alias="eps_surprise_percent.lte", description="Filter results to earnings records where EPS surprise percent is less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    revenue_surprise_percent_any_of: str | None = Field(default=None, validation_alias="revenue_surprise_percent.any_of", serialization_alias="revenue_surprise_percent.any_of", description="Filter results to earnings records with a revenue surprise percent matching any of the specified values. Use comma-separated floating-point numbers to filter by multiple surprise percentages.")
    revenue_surprise_percent_gt: float | None = Field(default=None, validation_alias="revenue_surprise_percent.gt", serialization_alias="revenue_surprise_percent.gt", description="Filter results to earnings records where revenue surprise percent is strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    revenue_surprise_percent_gte: float | None = Field(default=None, validation_alias="revenue_surprise_percent.gte", serialization_alias="revenue_surprise_percent.gte", description="Filter results to earnings records where revenue surprise percent is greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    revenue_surprise_percent_lt: float | None = Field(default=None, validation_alias="revenue_surprise_percent.lt", serialization_alias="revenue_surprise_percent.lt", description="Filter results to earnings records where revenue surprise percent is strictly less than the specified value.", json_schema_extra={'format': 'double'})
    revenue_surprise_percent_lte: float | None = Field(default=None, validation_alias="revenue_surprise_percent.lte", serialization_alias="revenue_surprise_percent.lte", description="Filter results to earnings records where revenue surprise percent is less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    limit: int | None = Field(default=None, description="Maximum number of earnings records to return in the response. Defaults to 100 if not specified; maximum allowed is 50,000.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort results by. Append '.asc' or '.desc' to each column to specify sort direction. Defaults to sorting by 'last_updated' in descending order if not specified.")
class GetBenzingaV1EarningsRequest(StrictModel):
    """Retrieve earnings data from Benzinga for publicly traded companies, including actual and estimated EPS and revenue figures with surprise calculations. Filter by date status, earnings surprises, and customize result ordering and limits."""
    query: GetBenzingaV1EarningsRequestQuery | None = None

# Operation: list_firms
class GetBenzingaV1FirmsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return in a single response. Defaults to 100 if not specified. Must be between 1 and 50,000.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort results by, with sort direction specified per column using '.asc' or '.desc' suffix. Defaults to sorting by firm name in ascending order if not specified.")
class GetBenzingaV1FirmsRequest(StrictModel):
    """Retrieve a list of financial firms from a comprehensive database of financial institutions and research firms, with support for pagination and custom sorting."""
    query: GetBenzingaV1FirmsRequestQuery | None = None

# Operation: list_guidance
class GetBenzingaV1GuidanceRequestQuery(StrictModel):
    positioning: str | None = Field(default=None, description="Filter guidance by presentation type: 'primary' for the company's emphasized figure or 'secondary' for supporting or alternate figures.")
    limit: int | None = Field(default=None, description="Maximum number of results to return, between 1 and 50,000. Defaults to 100 if not specified.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with '.asc' or '.desc' appended to each column to specify direction. Defaults to sorting by date in descending order.")
class GetBenzingaV1GuidanceRequest(StrictModel):
    """Retrieve financial guidance and earnings estimates for companies, including EPS and revenue projections across different fiscal periods."""
    query: GetBenzingaV1GuidanceRequestQuery | None = None

# Operation: list_analyst_ratings
class GetBenzingaV1RatingsRequestQuery(StrictModel):
    rating_action_any_of: str | None = Field(default=None, validation_alias="rating_action.any_of", serialization_alias="rating_action.any_of", description="Filter ratings by action type. Accepts one or more comma-separated values (e.g., 'upgrade,downgrade,initiate'). Use this to find specific types of rating changes.")
    rating_action_gt: str | None = Field(default=None, validation_alias="rating_action.gt", serialization_alias="rating_action.gt", description="Filter ratings by action type using greater-than comparison. Useful for alphabetical or numeric ordering of action types.")
    rating_action_gte: str | None = Field(default=None, validation_alias="rating_action.gte", serialization_alias="rating_action.gte", description="Filter ratings by action type using greater-than-or-equal comparison. Useful for alphabetical or numeric ordering of action types.")
    rating_action_lt: str | None = Field(default=None, validation_alias="rating_action.lt", serialization_alias="rating_action.lt", description="Filter ratings by action type using less-than comparison. Useful for alphabetical or numeric ordering of action types.")
    rating_action_lte: str | None = Field(default=None, validation_alias="rating_action.lte", serialization_alias="rating_action.lte", description="Filter ratings by action type using less-than-or-equal comparison. Useful for alphabetical or numeric ordering of action types.")
    price_target_action_any_of: str | None = Field(default=None, validation_alias="price_target_action.any_of", serialization_alias="price_target_action.any_of", description="Filter price target changes by action type. Accepts one or more comma-separated values (e.g., 'raised,lowered,initiated'). Use this to find specific types of price target adjustments.")
    price_target_action_gt: str | None = Field(default=None, validation_alias="price_target_action.gt", serialization_alias="price_target_action.gt", description="Filter price target changes by action type using greater-than comparison. Useful for alphabetical or numeric ordering of action types.")
    price_target_action_gte: str | None = Field(default=None, validation_alias="price_target_action.gte", serialization_alias="price_target_action.gte", description="Filter price target changes by action type using greater-than-or-equal comparison. Useful for alphabetical or numeric ordering of action types.")
    price_target_action_lt: str | None = Field(default=None, validation_alias="price_target_action.lt", serialization_alias="price_target_action.lt", description="Filter price target changes by action type using less-than comparison. Useful for alphabetical or numeric ordering of action types.")
    price_target_action_lte: str | None = Field(default=None, validation_alias="price_target_action.lte", serialization_alias="price_target_action.lte", description="Filter price target changes by action type using less-than-or-equal comparison. Useful for alphabetical or numeric ordering of action types.")
    benzinga_analyst_id_any_of: str | None = Field(default=None, validation_alias="benzinga_analyst_id.any_of", serialization_alias="benzinga_analyst_id.any_of", description="Filter results by analyst identifier. Accepts one or more comma-separated analyst IDs to retrieve ratings from specific analysts.")
    benzinga_analyst_id_gt: str | None = Field(default=None, validation_alias="benzinga_analyst_id.gt", serialization_alias="benzinga_analyst_id.gt", description="Filter analysts by ID using greater-than comparison. Useful for numeric filtering of analyst identifiers.")
    benzinga_analyst_id_gte: str | None = Field(default=None, validation_alias="benzinga_analyst_id.gte", serialization_alias="benzinga_analyst_id.gte", description="Filter analysts by ID using greater-than-or-equal comparison. Useful for numeric filtering of analyst identifiers.")
    benzinga_analyst_id_lt: str | None = Field(default=None, validation_alias="benzinga_analyst_id.lt", serialization_alias="benzinga_analyst_id.lt", description="Filter analysts by ID using less-than comparison. Useful for numeric filtering of analyst identifiers.")
    benzinga_analyst_id_lte: str | None = Field(default=None, validation_alias="benzinga_analyst_id.lte", serialization_alias="benzinga_analyst_id.lte", description="Filter analysts by ID using less-than-or-equal comparison. Useful for numeric filtering of analyst identifiers.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 100 if not specified. Maximum allowed value is 50,000.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with sort direction appended to each column (e.g., 'last_updated.desc,rating_action.asc'). Defaults to 'last_updated.desc' if not specified. Append '.asc' for ascending or '.desc' for descending order.")
class GetBenzingaV1RatingsRequest(StrictModel):
    """Retrieve analyst ratings and price target data from investment firms, including rating changes (upgrades, downgrades, initiations) and price target adjustments for publicly traded companies. Results can be filtered by rating action, price target action, and analyst ID, with customizable sorting and pagination."""
    query: GetBenzingaV1RatingsRequestQuery | None = None

# Operation: search_financial_news
class GetBenzingaV2NewsRequestQuery(StrictModel):
    published: str | None = Field(default=None, description="Filter articles by exact publication date. Accepts ISO 8601 timestamps, RFC 3339 format, or simple date strings (yyyy-mm-dd).")
    published_gt: str | None = Field(default=None, validation_alias="published.gt", serialization_alias="published.gt", description="Filter for articles published after this date. Accepts ISO 8601 timestamps, RFC 3339 format, or simple date strings (yyyy-mm-dd).")
    published_gte: str | None = Field(default=None, validation_alias="published.gte", serialization_alias="published.gte", description="Filter for articles published on or after this date. Accepts ISO 8601 timestamps, RFC 3339 format, or simple date strings (yyyy-mm-dd).")
    published_lt: str | None = Field(default=None, validation_alias="published.lt", serialization_alias="published.lt", description="Filter for articles published before this date. Accepts ISO 8601 timestamps, RFC 3339 format, or simple date strings (yyyy-mm-dd).")
    published_lte: str | None = Field(default=None, validation_alias="published.lte", serialization_alias="published.lte", description="Filter for articles published on or before this date. Accepts ISO 8601 timestamps, RFC 3339 format, or simple date strings (yyyy-mm-dd).")
    channels_all_of: str | None = Field(default=None, validation_alias="channels.all_of", serialization_alias="channels.all_of", description="Filter for articles that contain all specified channels. Provide multiple channels as a comma-separated list.")
    channels_any_of: str | None = Field(default=None, validation_alias="channels.any_of", serialization_alias="channels.any_of", description="Filter for articles that contain any of the specified channels. Provide multiple channels as a comma-separated list.")
    tags_all_of: str | None = Field(default=None, validation_alias="tags.all_of", serialization_alias="tags.all_of", description="Filter for articles that contain all specified tags. Provide multiple tags as a comma-separated list.")
    tags_any_of: str | None = Field(default=None, validation_alias="tags.any_of", serialization_alias="tags.any_of", description="Filter for articles that contain any of the specified tags. Provide multiple tags as a comma-separated list.")
    author_any_of: str | None = Field(default=None, validation_alias="author.any_of", serialization_alias="author.any_of", description="Filter for articles by any of the specified authors. Provide multiple authors as a comma-separated list.")
    author_gt: str | None = Field(default=None, validation_alias="author.gt", serialization_alias="author.gt", description="Filter for authors whose names come after this value alphabetically.")
    author_gte: str | None = Field(default=None, validation_alias="author.gte", serialization_alias="author.gte", description="Filter for authors whose names come after or equal to this value alphabetically.")
    author_lt: str | None = Field(default=None, validation_alias="author.lt", serialization_alias="author.lt", description="Filter for authors whose names come before this value alphabetically.")
    author_lte: str | None = Field(default=None, validation_alias="author.lte", serialization_alias="author.lte", description="Filter for authors whose names come before or equal to this value alphabetically.")
    stocks_all_of: str | None = Field(default=None, validation_alias="stocks.all_of", serialization_alias="stocks.all_of", description="Filter for articles that mention all specified stock symbols. Provide multiple symbols as a comma-separated list.")
    stocks_any_of: str | None = Field(default=None, validation_alias="stocks.any_of", serialization_alias="stocks.any_of", description="Filter for articles that mention any of the specified stock symbols. Provide multiple symbols as a comma-separated list.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 100 if not specified; maximum allowed is 50,000.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Sort results by one or more columns in ascending or descending order. Use comma-separated format with '.asc' or '.desc' suffix (e.g., 'published.desc,author.asc'). Defaults to 'published.desc' if not specified.")
class GetBenzingaV2NewsRequest(StrictModel):
    """Search and retrieve financial news articles from Benzinga's comprehensive database, with filtering by publication date, channels, tags, authors, and related stocks."""
    query: GetBenzingaV2NewsRequestQuery | None = None

# Operation: list_merchant_aggregates_eu
class GetConsumerSpendingEuV1MerchantAggregatesRequestQuery(StrictModel):
    transaction_date_gt: str | None = Field(default=None, validation_alias="transaction_date.gt", serialization_alias="transaction_date.gt", description="Filter transactions occurring after this date (exclusive). Use ISO 8601 format (yyyy-mm-dd).")
    transaction_date_gte: str | None = Field(default=None, validation_alias="transaction_date.gte", serialization_alias="transaction_date.gte", description="Filter transactions occurring on or after this date (inclusive). Use ISO 8601 format (yyyy-mm-dd).")
    transaction_date_lt: str | None = Field(default=None, validation_alias="transaction_date.lt", serialization_alias="transaction_date.lt", description="Filter transactions occurring before this date (exclusive). Use ISO 8601 format (yyyy-mm-dd).")
    transaction_date_lte: str | None = Field(default=None, validation_alias="transaction_date.lte", serialization_alias="transaction_date.lte", description="Filter transactions occurring on or before this date (inclusive). Use ISO 8601 format (yyyy-mm-dd).")
    name_any_of: str | None = Field(default=None, validation_alias="name.any_of", serialization_alias="name.any_of", description="Filter by merchant or payment processor name. Accepts multiple comma-separated values for matching any of the specified names.")
    user_country_any_of: Literal["UK", "DE", "FR", "ES", "IT", "AT", "unknown"] | None = Field(default=None, validation_alias="user_country.any_of", serialization_alias="user_country.any_of", description="Filter by consumer country. Accepts multiple comma-separated values from: UK, DE, FR, ES, IT, AT, or unknown.")
    channel_any_of: Literal["online", "offline", "bnpl"] | None = Field(default=None, validation_alias="channel.any_of", serialization_alias="channel.any_of", description="Filter by transaction channel. Accepts multiple comma-separated values: online, offline, or bnpl (buy-now-pay-later).")
    consumer_type_any_of: Literal["consumer_credit", "consumer_debit", "open_banking"] | None = Field(default=None, validation_alias="consumer_type.any_of", serialization_alias="consumer_type.any_of", description="Filter by consumer transaction type. Accepts multiple comma-separated values: consumer_credit (credit card), consumer_debit (debit card), or open_banking.")
    parent_name_any_of: str | None = Field(default=None, validation_alias="parent_name.any_of", serialization_alias="parent_name.any_of", description="Filter by parent company name. Accepts multiple comma-separated values for matching any of the specified parent entities.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Must be between 1 and 5000; defaults to 100 if not specified.", ge=1, le=5001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with .asc or .desc appended to each column name to specify direction. Defaults to transaction_date.desc if not specified.")
class GetConsumerSpendingEuV1MerchantAggregatesRequest(StrictModel):
    """Retrieve aggregated consumer spending data from European credit card and open banking panels, segmented by merchant, currency, country, and transaction channel. Data reflects daily transactions with a 7-day lag and includes user counts for custom normalization across 250+ US public companies."""
    query: GetConsumerSpendingEuV1MerchantAggregatesRequestQuery | None = None

# Operation: list_merchant_hierarchy
class GetConsumerSpendingEuV1MerchantHierarchyRequestQuery(StrictModel):
    lookup_name_any_of: str | None = Field(default=None, validation_alias="lookup_name.any_of", serialization_alias="lookup_name.any_of", description="Filter merchants by exact name match or multiple names using comma-separated values.")
    lookup_name_gt: str | None = Field(default=None, validation_alias="lookup_name.gt", serialization_alias="lookup_name.gt", description="Filter merchants by name lexicographically greater than the specified value.")
    lookup_name_gte: str | None = Field(default=None, validation_alias="lookup_name.gte", serialization_alias="lookup_name.gte", description="Filter merchants by name lexicographically greater than or equal to the specified value.")
    lookup_name_lt: str | None = Field(default=None, validation_alias="lookup_name.lt", serialization_alias="lookup_name.lt", description="Filter merchants by name lexicographically less than the specified value.")
    lookup_name_lte: str | None = Field(default=None, validation_alias="lookup_name.lte", serialization_alias="lookup_name.lte", description="Filter merchants by name lexicographically less than or equal to the specified value.")
    listing_status_any_of: Literal["public", "private"] | None = Field(default=None, validation_alias="listing_status.any_of", serialization_alias="listing_status.any_of", description="Filter by parent company listing status: 'public' for publicly traded companies or 'private' for private companies. Specify multiple values as comma-separated list.")
    active_from_gt: str | None = Field(default=None, validation_alias="active_from.gt", serialization_alias="active_from.gt", description="Filter merchants with active_from date strictly after the specified date (format: yyyy-mm-dd).")
    active_from_gte: str | None = Field(default=None, validation_alias="active_from.gte", serialization_alias="active_from.gte", description="Filter merchants with active_from date on or after the specified date (format: yyyy-mm-dd).")
    active_from_lt: str | None = Field(default=None, validation_alias="active_from.lt", serialization_alias="active_from.lt", description="Filter merchants with active_from date strictly before the specified date (format: yyyy-mm-dd).")
    active_from_lte: str | None = Field(default=None, validation_alias="active_from.lte", serialization_alias="active_from.lte", description="Filter merchants with active_from date on or before the specified date (format: yyyy-mm-dd).")
    active_to_gt: str | None = Field(default=None, validation_alias="active_to.gt", serialization_alias="active_to.gt", description="Filter merchants with active_to date strictly after the specified date (format: yyyy-mm-dd).")
    active_to_gte: str | None = Field(default=None, validation_alias="active_to.gte", serialization_alias="active_to.gte", description="Filter merchants with active_to date on or after the specified date (format: yyyy-mm-dd). Use this to find merchants active on a specific transaction date.")
    active_to_lt: str | None = Field(default=None, validation_alias="active_to.lt", serialization_alias="active_to.lt", description="Filter merchants with active_to date strictly before the specified date (format: yyyy-mm-dd).")
    active_to_lte: str | None = Field(default=None, validation_alias="active_to.lte", serialization_alias="active_to.lte", description="Filter merchants with active_to date on or before the specified date (format: yyyy-mm-dd).")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 100 if not specified; maximum allowed is 50,000.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Sort results by one or more columns in ascending or descending order using comma-separated format (e.g., 'lookup_name.asc,active_from.desc'). Defaults to 'lookup_name.asc' if not specified.")
class GetConsumerSpendingEuV1MerchantHierarchyRequest(StrictModel):
    """Retrieve merchant reference data with corporate hierarchy, ticker symbols, sectors, and industries for European consumer transactions. Use this to enrich transaction data by joining on merchant name and filtering by active date ranges to match specific transaction dates."""
    query: GetConsumerSpendingEuV1MerchantHierarchyRequestQuery | None = None

# Operation: list_etf_analytics
class GetEtfGlobalV1AnalyticsRequestQuery(StrictModel):
    risk_total_score_gt: float | None = Field(default=None, validation_alias="risk_total_score.gt", serialization_alias="risk_total_score.gt", description="Filter ETFs with total risk score greater than this value (floating point number).", json_schema_extra={'format': 'double'})
    risk_total_score_gte: float | None = Field(default=None, validation_alias="risk_total_score.gte", serialization_alias="risk_total_score.gte", description="Filter ETFs with total risk score greater than or equal to this value (floating point number).", json_schema_extra={'format': 'double'})
    risk_total_score_lt: float | None = Field(default=None, validation_alias="risk_total_score.lt", serialization_alias="risk_total_score.lt", description="Filter ETFs with total risk score less than this value (floating point number).", json_schema_extra={'format': 'double'})
    risk_total_score_lte: float | None = Field(default=None, validation_alias="risk_total_score.lte", serialization_alias="risk_total_score.lte", description="Filter ETFs with total risk score less than or equal to this value (floating point number).", json_schema_extra={'format': 'double'})
    reward_score_gt: float | None = Field(default=None, validation_alias="reward_score.gt", serialization_alias="reward_score.gt", description="Filter ETFs with reward score greater than this value (floating point number).", json_schema_extra={'format': 'double'})
    reward_score_gte: float | None = Field(default=None, validation_alias="reward_score.gte", serialization_alias="reward_score.gte", description="Filter ETFs with reward score greater than or equal to this value (floating point number).", json_schema_extra={'format': 'double'})
    reward_score_lt: float | None = Field(default=None, validation_alias="reward_score.lt", serialization_alias="reward_score.lt", description="Filter ETFs with reward score less than this value (floating point number).", json_schema_extra={'format': 'double'})
    reward_score_lte: float | None = Field(default=None, validation_alias="reward_score.lte", serialization_alias="reward_score.lte", description="Filter ETFs with reward score less than or equal to this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_total_score_gt: float | None = Field(default=None, validation_alias="quant_total_score.gt", serialization_alias="quant_total_score.gt", description="Filter ETFs with quantitative total score greater than this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_total_score_gte: float | None = Field(default=None, validation_alias="quant_total_score.gte", serialization_alias="quant_total_score.gte", description="Filter ETFs with quantitative total score greater than or equal to this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_total_score_lt: float | None = Field(default=None, validation_alias="quant_total_score.lt", serialization_alias="quant_total_score.lt", description="Filter ETFs with quantitative total score less than this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_total_score_lte: float | None = Field(default=None, validation_alias="quant_total_score.lte", serialization_alias="quant_total_score.lte", description="Filter ETFs with quantitative total score less than or equal to this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_grade_any_of: str | None = Field(default=None, validation_alias="quant_grade.any_of", serialization_alias="quant_grade.any_of", description="Filter ETFs by quantitative grade using one or more values (comma-separated list for multiple grades).")
    quant_grade_gt: str | None = Field(default=None, validation_alias="quant_grade.gt", serialization_alias="quant_grade.gt", description="Filter ETFs with quantitative grade greater than this value (alphabetically ordered).")
    quant_grade_gte: str | None = Field(default=None, validation_alias="quant_grade.gte", serialization_alias="quant_grade.gte", description="Filter ETFs with quantitative grade greater than or equal to this value (alphabetically ordered).")
    quant_grade_lt: str | None = Field(default=None, validation_alias="quant_grade.lt", serialization_alias="quant_grade.lt", description="Filter ETFs with quantitative grade less than this value (alphabetically ordered).")
    quant_grade_lte: str | None = Field(default=None, validation_alias="quant_grade.lte", serialization_alias="quant_grade.lte", description="Filter ETFs with quantitative grade less than or equal to this value (alphabetically ordered).")
    quant_composite_technical_gt: float | None = Field(default=None, validation_alias="quant_composite_technical.gt", serialization_alias="quant_composite_technical.gt", description="Filter ETFs with composite technical score greater than this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_technical_gte: float | None = Field(default=None, validation_alias="quant_composite_technical.gte", serialization_alias="quant_composite_technical.gte", description="Filter ETFs with composite technical score greater than or equal to this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_technical_lt: float | None = Field(default=None, validation_alias="quant_composite_technical.lt", serialization_alias="quant_composite_technical.lt", description="Filter ETFs with composite technical score less than this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_technical_lte: float | None = Field(default=None, validation_alias="quant_composite_technical.lte", serialization_alias="quant_composite_technical.lte", description="Filter ETFs with composite technical score less than or equal to this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_sentiment_gt: float | None = Field(default=None, validation_alias="quant_composite_sentiment.gt", serialization_alias="quant_composite_sentiment.gt", description="Filter ETFs with composite sentiment score greater than this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_sentiment_gte: float | None = Field(default=None, validation_alias="quant_composite_sentiment.gte", serialization_alias="quant_composite_sentiment.gte", description="Filter ETFs with composite sentiment score greater than or equal to this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_sentiment_lt: float | None = Field(default=None, validation_alias="quant_composite_sentiment.lt", serialization_alias="quant_composite_sentiment.lt", description="Filter ETFs with composite sentiment score less than this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_sentiment_lte: float | None = Field(default=None, validation_alias="quant_composite_sentiment.lte", serialization_alias="quant_composite_sentiment.lte", description="Filter ETFs with composite sentiment score less than or equal to this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_behavioral_gt: float | None = Field(default=None, validation_alias="quant_composite_behavioral.gt", serialization_alias="quant_composite_behavioral.gt", description="Filter ETFs with composite behavioral score greater than this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_behavioral_gte: float | None = Field(default=None, validation_alias="quant_composite_behavioral.gte", serialization_alias="quant_composite_behavioral.gte", description="Filter ETFs with composite behavioral score greater than or equal to this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_behavioral_lt: float | None = Field(default=None, validation_alias="quant_composite_behavioral.lt", serialization_alias="quant_composite_behavioral.lt", description="Filter ETFs with composite behavioral score less than this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_behavioral_lte: float | None = Field(default=None, validation_alias="quant_composite_behavioral.lte", serialization_alias="quant_composite_behavioral.lte", description="Filter ETFs with composite behavioral score less than or equal to this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_fundamental_gt: float | None = Field(default=None, validation_alias="quant_composite_fundamental.gt", serialization_alias="quant_composite_fundamental.gt", description="Filter ETFs with composite fundamental score greater than this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_fundamental_gte: float | None = Field(default=None, validation_alias="quant_composite_fundamental.gte", serialization_alias="quant_composite_fundamental.gte", description="Filter ETFs with composite fundamental score greater than or equal to this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_fundamental_lt: float | None = Field(default=None, validation_alias="quant_composite_fundamental.lt", serialization_alias="quant_composite_fundamental.lt", description="Filter ETFs with composite fundamental score less than this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_fundamental_lte: float | None = Field(default=None, validation_alias="quant_composite_fundamental.lte", serialization_alias="quant_composite_fundamental.lte", description="Filter ETFs with composite fundamental score less than or equal to this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_global_gt: float | None = Field(default=None, validation_alias="quant_composite_global.gt", serialization_alias="quant_composite_global.gt", description="Filter ETFs with composite global score greater than this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_global_gte: float | None = Field(default=None, validation_alias="quant_composite_global.gte", serialization_alias="quant_composite_global.gte", description="Filter ETFs with composite global score greater than or equal to this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_global_lt: float | None = Field(default=None, validation_alias="quant_composite_global.lt", serialization_alias="quant_composite_global.lt", description="Filter ETFs with composite global score less than this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_global_lte: float | None = Field(default=None, validation_alias="quant_composite_global.lte", serialization_alias="quant_composite_global.lte", description="Filter ETFs with composite global score less than or equal to this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_quality_gt: float | None = Field(default=None, validation_alias="quant_composite_quality.gt", serialization_alias="quant_composite_quality.gt", description="Filter ETFs with composite quality score greater than this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_quality_gte: float | None = Field(default=None, validation_alias="quant_composite_quality.gte", serialization_alias="quant_composite_quality.gte", description="Filter ETFs with composite quality score greater than or equal to this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_quality_lt: float | None = Field(default=None, validation_alias="quant_composite_quality.lt", serialization_alias="quant_composite_quality.lt", description="Filter ETFs with composite quality score less than this value (floating point number).", json_schema_extra={'format': 'double'})
    quant_composite_quality_lte: float | None = Field(default=None, validation_alias="quant_composite_quality.lte", serialization_alias="quant_composite_quality.lte", description="Filter ETFs with composite quality score less than or equal to this value (floating point number).", json_schema_extra={'format': 'double'})
    limit: int | None = Field(default=None, description="Maximum number of results to return (1 to 5000, defaults to 100 if not specified).", ge=1, le=5001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with '.asc' or '.desc' appended to each column to specify direction. Defaults to sorting by composite_ticker in ascending order.")
class GetEtfGlobalV1AnalyticsRequest(StrictModel):
    """Retrieve ETF Global analytics data with risk scores, reward metrics, and quantitative analysis across multiple dimensions. Filter and sort results by performance indicators, risk profiles, and composite grades."""
    query: GetEtfGlobalV1AnalyticsRequestQuery | None = None

# Operation: list_etf_constituents
class GetEtfGlobalV1ConstituentsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of constituent records to return per request, ranging from 1 to 5000. Defaults to 100 if not specified.", ge=1, le=5001)
    sort: str | None = Field(default=None, description="Comma-separated list of fields to sort results by, with each field suffixed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by composite_ticker in ascending order if not specified.")
class GetEtfGlobalV1ConstituentsRequest(StrictModel):
    """Retrieve detailed information about securities held within ETFs, including their weights, market values, and identifiers. Results can be paginated and sorted by any constituent field."""
    query: GetEtfGlobalV1ConstituentsRequestQuery | None = None

# Operation: list_etf_fund_flows
class GetEtfGlobalV1FundFlowsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return per request, ranging from 1 to 5000. Defaults to 100 if not specified.", ge=1, le=5001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by composite_ticker in ascending order if not specified.")
class GetEtfGlobalV1FundFlowsRequest(StrictModel):
    """Retrieve ETF Global fund flow data including share movements, net asset values, and flow metrics across ETFs. Results can be paginated and sorted by multiple columns."""
    query: GetEtfGlobalV1FundFlowsRequestQuery | None = None

# Operation: list_etf_profiles
class GetEtfGlobalV1ProfilesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of ETF profiles to return in a single response. Must be between 1 and 5000, defaults to 100 if not specified.", ge=1, le=5001)
    sort: str | None = Field(default=None, description="Comma-separated list of fields to sort results by, with each field followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by composite_ticker in ascending order if not specified.")
class GetEtfGlobalV1ProfilesRequest(StrictModel):
    """Retrieve comprehensive ETF Global industry profile data including financial metrics, operational details, and exposure information. Results can be paginated and sorted by any profile field."""
    query: GetEtfGlobalV1ProfilesRequestQuery | None = None

# Operation: list_etf_taxonomies
class GetEtfGlobalV1TaxonomiesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of taxonomy records to return in the response. Defaults to 100 if not specified. Must be between 1 and 5000.", ge=1, le=5001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort results by, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by 'composite_ticker' in ascending order if not specified.")
class GetEtfGlobalV1TaxonomiesRequest(StrictModel):
    """Retrieve ETF Global taxonomy data containing detailed classification and categorization information for ETFs, including investment strategy, methodology, and structural characteristics."""
    query: GetEtfGlobalV1TaxonomiesRequestQuery | None = None

# Operation: list_inflation_metrics
class GetFedV1InflationRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return in a single response. Accepts values from 1 to 50,000, with a default of 100 results if not specified.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort results by, with sort direction specified per column using '.asc' or '.desc' suffix. Defaults to sorting by date in ascending order if not specified.")
class GetFedV1InflationRequest(StrictModel):
    """Retrieve historical inflation and price index data, including Consumer Price Index (CPI) and Personal Consumption Expenditures (PCE) metrics. Results can be sorted and paginated for flexible data access."""
    query: GetFedV1InflationRequestQuery | None = None

# Operation: list_inflation_expectations
class GetFedV1InflationExpectationsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return in a single response, ranging from 1 to 50,000. Defaults to 100 if not specified.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by date in ascending order if not specified.")
class GetFedV1InflationExpectationsRequest(StrictModel):
    """Retrieve inflation expectations data from both market-based and economic model perspectives across multiple time horizons. Results can be paginated and sorted by any available column."""
    query: GetFedV1InflationExpectationsRequestQuery | None = None

# Operation: list_labor_market_indicators
class GetFedV1LaborMarketRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return in a single response, ranging from 1 to 50,000. Defaults to 100 if not specified.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by date in ascending order if not specified.")
class GetFedV1LaborMarketRequest(StrictModel):
    """Retrieve Federal Reserve labor market indicators including unemployment rate, labor force participation, average hourly earnings, and job openings data. Results are paginated and sortable by date or other available fields."""
    query: GetFedV1LaborMarketRequestQuery | None = None

# Operation: list_treasury_yields
class GetFedV1TreasuryYieldsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return in a single response. Accepts values from 1 to 50,000, with a default of 100 results if not specified.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort results by, with sort direction specified per column using '.asc' or '.desc' suffix. Defaults to sorting by date in ascending order if not specified.")
class GetFedV1TreasuryYieldsRequest(StrictModel):
    """Retrieve historical U.S. Treasury bond yields across various maturity periods, providing a comprehensive view of government securities interest rates from short-term to long-term instruments."""
    query: GetFedV1TreasuryYieldsRequestQuery | None = None

# Operation: get_futures_aggregates
class AggregatesV1RequestPath(StrictModel):
    ticker: str = Field(default=..., description="The futures contract identifier including base symbol and expiration month/year (e.g., GCJ5 for April 2025 gold futures).")
class AggregatesV1RequestQuery(StrictModel):
    resolution: str | None = Field(default=None, description="The candle size as a number with unit: seconds (sec), minutes (min), hours (hour), trading sessions (session), weeks (week), months (month), quarters (quarter), or years (year). Each unit has a maximum multiplier (e.g., up to 59min before switching to hours). Defaults to one trading session.")
    window_start: str | None = Field(default=None, description="Filter candles by start time using a date (YYYY-MM-DD format) or nanosecond Unix timestamp. Supports comparison operators: gte (greater than or equal), gt (greater than), lte (less than or equal), lt (less than) for range queries. When omitted, returns the most recent candles up to the specified limit.")
    limit: int | None = Field(default=None, description="Maximum number of results to return per page. Must be between 1 and 50,000, defaults to 1,000.", ge=1, le=50000)
    sort: Literal["window_start.asc", "window_start.desc"] | None = Field(default=None, description="Sort results by window_start in ascending or descending order. Defaults to descending (most recent first).")
class AggregatesV1Request(StrictModel):
    """Retrieve OHLCV aggregates (candles) for a futures contract over a specified time range. Supports flexible time windows and multiple resolution granularities from seconds to years."""
    path: AggregatesV1RequestPath
    query: AggregatesV1RequestQuery | None = None

# Operation: get_futures_aggregates_vx
class AggregatesRequestPath(StrictModel):
    ticker: str = Field(default=..., description="The futures contract identifier including base symbol and expiration month/year (e.g., GCJ5 for April 2025 gold futures).")
class AggregatesRequestQuery(StrictModel):
    resolution: str | None = Field(default=None, description="The candle interval size as a number with unit: seconds (sec), minutes (min), hours (hour), trading sessions (session), weeks (week), months (month), quarters (quarter), or years (year). Each unit has a maximum multiplier (e.g., up to 59min before switching to hours). Defaults to one trading session.")
    window_start: str | None = Field(default=None, description="Filter candles by start time using a date (YYYY-MM-DD format) or nanosecond Unix timestamp. Use comparison operators (gte, gt, lte, lt) to define ranges. When omitted, returns the most recent candles up to the specified limit.")
    limit: int | None = Field(default=None, description="Maximum number of candles to return per request, between 1 and 50,000. Defaults to 1,000 results.", ge=1, le=50000)
    sort: Literal["window_start.asc", "window_start.desc"] | None = Field(default=None, description="Sort results by window_start timestamp in ascending or descending order. Defaults to descending (most recent first).")
class AggregatesRequest(StrictModel):
    """Retrieve OHLCV candle data for a futures contract over a specified time range. Supports flexible time windows and multiple resolution granularities from seconds to years."""
    path: AggregatesRequestPath
    query: AggregatesRequestQuery | None = None

# Operation: list_futures_contracts
class GetFuturesVXContractsRequestQuery(StrictModel):
    active: bool | None = Field(default=None, description="Filter results to only include contracts that were actively tradeable on the specified date. A contract is active when its first trade date is on or before the query date and its last trade date is on or after the query date.")
    limit: int | None = Field(default=None, description="Maximum number of results to return per request, ranging from 1 to 1000. Defaults to 100 if not specified.", ge=1, le=1001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify direction. Defaults to sorting by product_code in ascending order if not specified.")
class GetFuturesVXContractsRequest(StrictModel):
    """Retrieve a paginated list of futures contracts with optional filtering by active status and custom sorting. Use this to discover all listed contracts, access complete contract specifications, or perform point-in-time lookups of contract definitions."""
    query: GetFuturesVXContractsRequestQuery | None = None

# Operation: list_futures_exchanges
class GetFuturesVXExchangesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Accepts values between 1 and 1,000, with a default of 100 if not specified.", ge=1, le=1000)
class GetFuturesVXExchangesRequest(StrictModel):
    """Retrieve a list of US futures exchanges and trading venues, including major derivatives exchanges (CME, CBOT, NYMEX, COMEX) and other futures market infrastructure for commodity, financial, and derivative contract trading."""
    query: GetFuturesVXExchangesRequestQuery | None = None

# Operation: list_futures_market_statuses
class GetFuturesVXMarketStatusRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of market status records to return in the response. Must be between 1 and 100, defaults to 10 if not specified.", ge=1, le=100)
class GetFuturesVXMarketStatusRequest(StrictModel):
    """Retrieve the current market status for futures products, including real-time operational indicators (open, pause, close) with exchange and product codes. Use this to monitor market conditions and adjust trading strategies in real-time."""
    query: GetFuturesVXMarketStatusRequestQuery | None = None

# Operation: list_futures_products
class GetFuturesVXProductsRequestQuery(StrictModel):
    name_any_of: str | None = Field(default=None, validation_alias="name.any_of", serialization_alias="name.any_of", description="Filter products by name. Accepts multiple comma-separated values to match any of the specified product names.")
    sector_any_of: Literal["asia", "base", "biofuels", "coal", "cross_rates", "crude_oil", "custom_index", "dairy", "dj_ubs_ci", "electricity", "emissions", "europe", "fertilizer", "forestry", "grains_and_oilseeds", "intl_index", "liq_nat_gas_lng", "livestock", "long_term_gov", "long_term_non_gov", "majors", "minors", "nat_gas", "nat_gas_liq_petro", "precious", "refined_products", "s_and_p_gsci", "sel_sector_index", "short_term_gov", "short_term_non_gov", "softs", "us", "us_index", "wet_bulk"] | None = Field(default=None, validation_alias="sector.any_of", serialization_alias="sector.any_of", description="Filter products by sector classification. Accepts multiple comma-separated values from predefined sectors including commodities (crude oil, natural gas, metals, grains), financials (indices, interest rates, currencies), and specialized categories (emissions, forestry, weather).")
    sub_sector_any_of: Literal["asian", "canadian", "cat", "cooling_degree_days", "ercot", "european", "gulf", "heating_degree_days", "iso_ne", "large_cap_index", "mid_cap_index", "miso", "north_american", "nyiso", "pjm", "small_cap_index", "west", "western_power"] | None = Field(default=None, validation_alias="sub_sector.any_of", serialization_alias="sub_sector.any_of", description="Filter products by sub-sector classification. Accepts multiple comma-separated values for granular categorization such as geographic regions (Asian, European, North American), grid operators (ERCOT, MISO, PJM), or index sizes (large-cap, mid-cap, small-cap).")
    asset_class_any_of: Literal["alt_investment", "commodity", "financials"] | None = Field(default=None, validation_alias="asset_class.any_of", serialization_alias="asset_class.any_of", description="Filter products by asset class. Accepts multiple comma-separated values: commodities, financials, or alternative investments.")
    asset_sub_class_any_of: Literal["agricultural", "commodity_index", "energy", "equity", "foreign_exchange", "freight", "housing", "interest_rate", "metals", "weather"] | None = Field(default=None, validation_alias="asset_sub_class.any_of", serialization_alias="asset_sub_class.any_of", description="Filter products by asset sub-class. Accepts multiple comma-separated values including agricultural, energy, metals, equity, foreign exchange, interest rates, freight, housing, commodity indices, and weather.")
    limit: int | None = Field(default=None, description="Limit the number of results returned. Must be between 1 and 50,000; defaults to 100 if not specified.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Sort results by one or more columns in ascending or descending order. Specify columns as comma-separated values with '.asc' or '.desc' suffix (e.g., 'name.asc,date.desc'). Defaults to 'date.asc' if not specified.")
class GetFuturesVXProductsRequest(StrictModel):
    """Retrieve the complete universe of supported futures products with full specifications including codes, names, exchange identifiers, classifications, settlement methods, and pricing details. Filter by product attributes or retrieve specifications for a single product to support trading system integration, risk management, and historical reconciliation."""
    query: GetFuturesVXProductsRequestQuery | None = None

# Operation: get_futures_quotes
class GetFuturesVXQuotesRequestPath(StrictModel):
    ticker: str = Field(default=..., description="The futures contract identifier combining the base symbol and expiration month/year (e.g., GCJ5 for April 2025 gold futures).")
class GetFuturesVXQuotesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of quote records to return, ranging from 1 to 50,000. Defaults to 100 if not specified.", ge=1, le=50000)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with each column suffixed by '.asc' or '.desc' to specify direction. Defaults to sorting by timestamp in descending order.")
class GetFuturesVXQuotesRequest(StrictModel):
    """Retrieve real-time quote data for a specified futures contract, including best bid/offer prices, sizes, and timestamps to analyze price dynamics and liquidity conditions."""
    path: GetFuturesVXQuotesRequestPath
    query: GetFuturesVXQuotesRequestQuery | None = None

# Operation: list_futures_schedules
class GetFuturesVXSchedulesRequestQuery(StrictModel):
    session_end_date_gt: str | None = Field(default=None, validation_alias="session_end_date.gt", serialization_alias="session_end_date.gt", description="Filter schedules to those with session end dates strictly after this date (formatted as yyyy-mm-dd). Use this to find schedules starting from a specific point in time.")
    session_end_date_gte: str | None = Field(default=None, validation_alias="session_end_date.gte", serialization_alias="session_end_date.gte", description="Filter schedules to those with session end dates on or after this date (formatted as yyyy-mm-dd). Use this to include schedules from a specific date forward.")
    session_end_date_lt: str | None = Field(default=None, validation_alias="session_end_date.lt", serialization_alias="session_end_date.lt", description="Filter schedules to those with session end dates strictly before this date (formatted as yyyy-mm-dd). Use this to find schedules up to a specific point in time.")
    session_end_date_lte: str | None = Field(default=None, validation_alias="session_end_date.lte", serialization_alias="session_end_date.lte", description="Filter schedules to those with session end dates on or before this date (formatted as yyyy-mm-dd). Use this to include schedules up through a specific date.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Defaults to 10 if not specified; maximum allowed is 1000.", ge=1, le=1001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify direction (e.g., 'product_code.asc,session_end_date.desc'). Defaults to sorting by product_code in ascending order.")
class GetFuturesVXSchedulesRequest(StrictModel):
    """Retrieve trading schedules for futures markets with session open/close times, intraday breaks, and holiday adjustments. All times are returned in UTC to support cross-system alignment for trading, execution, and operations workflows."""
    query: GetFuturesVXSchedulesRequestQuery | None = None

# Operation: list_futures_snapshots
class GetFuturesVXSnapshotRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Must be between 1 and 50,000, defaults to 100 if not specified.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify direction. Defaults to sorting by 'ticker' in ascending order if not specified.")
class GetFuturesVXSnapshotRequest(StrictModel):
    """Retrieve a snapshot of the most recent futures contract data with optional pagination and sorting capabilities."""
    query: GetFuturesVXSnapshotRequestQuery | None = None

# Operation: list_futures_trades
class GetFuturesVXTradesRequestPath(StrictModel):
    ticker: str = Field(default=..., description="The futures contract identifier, including the base symbol and contract expiration month/year (e.g., GCJ5 for April 2025 gold contract).")
class GetFuturesVXTradesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of trade records to return in the response. Defaults to 10 if not specified; maximum allowed is 49,999 records per request.", ge=1, le=50000)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify direction. Defaults to sorting by timestamp in descending order (most recent first) if not specified.")
class GetFuturesVXTradesRequest(StrictModel):
    """Retrieve tick-level trade data for a specified futures contract over a defined time range. Each record captures individual trade events with price, size, session date, and precise timestamps, enabling detailed intraday analysis, backtesting, and algorithmic strategy development."""
    path: GetFuturesVXTradesRequestPath
    query: GetFuturesVXTradesRequestQuery | None = None

# Operation: list_stock_filings_10_k_sections
class GetStocksFilings10KVXSectionsRequestQuery(StrictModel):
    section: Literal["business", "risk_factors"] | None = Field(default=None, description="Filter results by standardized section type. Valid options are 'business' (company operations and segments) or 'risk_factors' (identified business risks). Omit to retrieve all available sections.")
    limit: int | None = Field(default=None, description="Maximum number of filing sections to return in the response. Must be between 1 and 100, defaults to 10 if not specified.", ge=1, le=100)
    sort: str | None = Field(default=None, description="Sort results by one or more columns using comma-separated format, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by 'period_end' in descending order (most recent first) if not specified.")
class GetStocksFilings10KVXSectionsRequest(StrictModel):
    """Retrieve raw text content from specific sections of SEC 10-K filings. Returns standardized section excerpts from corporate annual reports, useful for extracting business descriptions, risk disclosures, and other regulatory content."""
    query: GetStocksFilings10KVXSectionsRequestQuery | None = None

# Operation: list_stocks_8k_filings_text
class GetStocksFilings8KVXTextRequestQuery(StrictModel):
    form_type_gt: str | None = Field(default=None, validation_alias="form_type.gt", serialization_alias="form_type.gt", description="Filter results to filings with form_type values greater than the specified value.")
    form_type_gte: str | None = Field(default=None, validation_alias="form_type.gte", serialization_alias="form_type.gte", description="Filter results to filings with form_type values greater than or equal to the specified value.")
    form_type_lt: str | None = Field(default=None, validation_alias="form_type.lt", serialization_alias="form_type.lt", description="Filter results to filings with form_type values less than the specified value.")
    form_type_lte: str | None = Field(default=None, validation_alias="form_type.lte", serialization_alias="form_type.lte", description="Filter results to filings with form_type values less than or equal to the specified value.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Defaults to 10 if not specified, with a maximum allowed value of 99.", ge=1, le=100)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify sort direction. Defaults to sorting by filing_date in descending order if not specified.")
class GetStocksFilings8KVXTextRequest(StrictModel):
    """Retrieve parsed text content from SEC 8-K current report filings, which disclose material corporate events such as earnings announcements, acquisitions, executive changes, and other significant developments."""
    query: GetStocksFilings8KVXTextRequestQuery | None = None

# Operation: list_13f_filings
class GetStocksFilingsVX13FRequestQuery(StrictModel):
    filer_cik: str | None = Field(default=None, description="SEC Central Index Key (CIK) of the filing entity as a 10-digit zero-padded string. Use this to retrieve all 13F filings from a specific institutional investment manager.")
    accession_number: str | None = Field(default=None, description="Unique SEC accession number for a specific filing (format: NNNNNNNNNN-YY-NNNNNN). Use this to retrieve a particular 13F filing by its unique identifier.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Must be between 1 and 1000; defaults to 100 if not specified.", ge=1, le=1001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort results by, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by filing_date in descending order (most recent first) if not specified.")
class GetStocksFilingsVX13FRequest(StrictModel):
    """Retrieve SEC Form 13F quarterly filings data showing institutional investment manager holdings. Filter by filer or accession number to access specific filings from investment managers with at least $100 million in qualifying assets under management."""
    query: GetStocksFilingsVX13FRequestQuery | None = None

# Operation: list_sec_filings
class GetStocksFilingsVXIndexRequestQuery(StrictModel):
    form_type_gt: str | None = Field(default=None, validation_alias="form_type.gt", serialization_alias="form_type.gt", description="Filter results to form types greater than the specified value (alphabetically).")
    form_type_gte: str | None = Field(default=None, validation_alias="form_type.gte", serialization_alias="form_type.gte", description="Filter results to form types greater than or equal to the specified value (alphabetically).")
    form_type_lt: str | None = Field(default=None, validation_alias="form_type.lt", serialization_alias="form_type.lt", description="Filter results to form types less than the specified value (alphabetically).")
    form_type_lte: str | None = Field(default=None, validation_alias="form_type.lte", serialization_alias="form_type.lte", description="Filter results to form types less than or equal to the specified value (alphabetically).")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 1000 if not specified. Maximum allowed value is 50000.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with each column suffixed by '.asc' or '.desc' to specify sort direction. Defaults to 'filing_date.desc' if not specified.")
class GetStocksFilingsVXIndexRequest(StrictModel):
    """Retrieve SEC EDGAR master index records for all SEC filings, including form types, filing dates, and direct links to source documents. Supports filtering by form type and customizable sorting and pagination."""
    query: GetStocksFilingsVXIndexRequestQuery | None = None

# Operation: list_risk_factors_from_stock_filings
class GetStocksFilingsVXRiskFactorsRequestQuery(StrictModel):
    filing_date_any_of: str | None = Field(default=None, validation_alias="filing_date.any_of", serialization_alias="filing_date.any_of", description="Filter results to filings with dates matching any of the specified values. Provide one or more dates as a comma-separated list.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 100 if not specified. Must be between 1 and 50,000.", ge=1, le=50000)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify direction. Defaults to sorting by filing_date in descending order.")
class GetStocksFilingsVXRiskFactorsRequest(StrictModel):
    """Retrieve risk factors disclosed in companies' 10-K SEC filings. Filter by filing date and control result size and ordering."""
    query: GetStocksFilingsVXRiskFactorsRequestQuery | None = None

# Operation: list_balance_sheets
class GetStocksFinancialsV1BalanceSheetsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Accepts values from 1 to 50,000, with a default of 100 if not specified.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by 'period_end' in ascending order if not specified.")
class GetStocksFinancialsV1BalanceSheetsRequest(StrictModel):
    """Retrieve quarterly and annual balance sheet data for public companies, showing point-in-time snapshots of assets, liabilities, and shareholders' equity at each period end."""
    query: GetStocksFinancialsV1BalanceSheetsRequestQuery | None = None

# Operation: list_cash_flow_statements
class GetStocksFinancialsV1CashFlowStatementsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return in a single response. Accepts values from 1 to 50,000, with a default of 100 if not specified.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort results by, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to 'period_end.asc' if not specified.")
class GetStocksFinancialsV1CashFlowStatementsRequest(StrictModel):
    """Retrieve quarterly, annual, and trailing twelve-month cash flow statement data for public companies, including detailed operating, investing, and financing cash flows with validated TTM calculations spanning exactly four quarters."""
    query: GetStocksFinancialsV1CashFlowStatementsRequestQuery | None = None

# Operation: list_income_statements
class GetStocksFinancialsV1IncomeStatementsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return per request, ranging from 1 to 50,000. Defaults to 100 if not specified.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort results by, with each column followed by '.asc' or '.desc' to specify ascending or descending order. Defaults to sorting by period_end in ascending order if not specified.")
class GetStocksFinancialsV1IncomeStatementsRequest(StrictModel):
    """Retrieve income statement financial data for public companies, including revenue, expenses, and net income across multiple reporting periods. Results can be paginated and sorted by various financial metrics."""
    query: GetStocksFinancialsV1IncomeStatementsRequestQuery | None = None

# Operation: list_stock_financial_ratios
class GetStocksFinancialsV1RatiosRequestQuery(StrictModel):
    price_gt: float | None = Field(default=None, validation_alias="price.gt", serialization_alias="price.gt", description="Filter for stock prices strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    price_gte: float | None = Field(default=None, validation_alias="price.gte", serialization_alias="price.gte", description="Filter for stock prices greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    price_lt: float | None = Field(default=None, validation_alias="price.lt", serialization_alias="price.lt", description="Filter for stock prices strictly less than the specified value.", json_schema_extra={'format': 'double'})
    price_lte: float | None = Field(default=None, validation_alias="price.lte", serialization_alias="price.lte", description="Filter for stock prices less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    average_volume_gt: float | None = Field(default=None, validation_alias="average_volume.gt", serialization_alias="average_volume.gt", description="Filter for average trading volume strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    average_volume_gte: float | None = Field(default=None, validation_alias="average_volume.gte", serialization_alias="average_volume.gte", description="Filter for average trading volume greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    average_volume_lt: float | None = Field(default=None, validation_alias="average_volume.lt", serialization_alias="average_volume.lt", description="Filter for average trading volume strictly less than the specified value.", json_schema_extra={'format': 'double'})
    average_volume_lte: float | None = Field(default=None, validation_alias="average_volume.lte", serialization_alias="average_volume.lte", description="Filter for average trading volume less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    market_cap_gt: float | None = Field(default=None, validation_alias="market_cap.gt", serialization_alias="market_cap.gt", description="Filter for market capitalization strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    market_cap_gte: float | None = Field(default=None, validation_alias="market_cap.gte", serialization_alias="market_cap.gte", description="Filter for market capitalization greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    market_cap_lt: float | None = Field(default=None, validation_alias="market_cap.lt", serialization_alias="market_cap.lt", description="Filter for market capitalization strictly less than the specified value.", json_schema_extra={'format': 'double'})
    market_cap_lte: float | None = Field(default=None, validation_alias="market_cap.lte", serialization_alias="market_cap.lte", description="Filter for market capitalization less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    earnings_per_share_gt: float | None = Field(default=None, validation_alias="earnings_per_share.gt", serialization_alias="earnings_per_share.gt", description="Filter for earnings per share strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    earnings_per_share_gte: float | None = Field(default=None, validation_alias="earnings_per_share.gte", serialization_alias="earnings_per_share.gte", description="Filter for earnings per share greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    earnings_per_share_lt: float | None = Field(default=None, validation_alias="earnings_per_share.lt", serialization_alias="earnings_per_share.lt", description="Filter for earnings per share strictly less than the specified value.", json_schema_extra={'format': 'double'})
    earnings_per_share_lte: float | None = Field(default=None, validation_alias="earnings_per_share.lte", serialization_alias="earnings_per_share.lte", description="Filter for earnings per share less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    price_to_earnings_gt: float | None = Field(default=None, validation_alias="price_to_earnings.gt", serialization_alias="price_to_earnings.gt", description="Filter for price-to-earnings ratio strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    price_to_earnings_gte: float | None = Field(default=None, validation_alias="price_to_earnings.gte", serialization_alias="price_to_earnings.gte", description="Filter for price-to-earnings ratio greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    price_to_earnings_lt: float | None = Field(default=None, validation_alias="price_to_earnings.lt", serialization_alias="price_to_earnings.lt", description="Filter for price-to-earnings ratio strictly less than the specified value.", json_schema_extra={'format': 'double'})
    price_to_earnings_lte: float | None = Field(default=None, validation_alias="price_to_earnings.lte", serialization_alias="price_to_earnings.lte", description="Filter for price-to-earnings ratio less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    price_to_book_gt: float | None = Field(default=None, validation_alias="price_to_book.gt", serialization_alias="price_to_book.gt", description="Filter for price-to-book ratio strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    price_to_book_gte: float | None = Field(default=None, validation_alias="price_to_book.gte", serialization_alias="price_to_book.gte", description="Filter for price-to-book ratio greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    price_to_book_lt: float | None = Field(default=None, validation_alias="price_to_book.lt", serialization_alias="price_to_book.lt", description="Filter for price-to-book ratio strictly less than the specified value.", json_schema_extra={'format': 'double'})
    price_to_book_lte: float | None = Field(default=None, validation_alias="price_to_book.lte", serialization_alias="price_to_book.lte", description="Filter for price-to-book ratio less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    price_to_sales_gt: float | None = Field(default=None, validation_alias="price_to_sales.gt", serialization_alias="price_to_sales.gt", description="Filter for price-to-sales ratio strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    price_to_sales_gte: float | None = Field(default=None, validation_alias="price_to_sales.gte", serialization_alias="price_to_sales.gte", description="Filter for price-to-sales ratio greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    price_to_sales_lt: float | None = Field(default=None, validation_alias="price_to_sales.lt", serialization_alias="price_to_sales.lt", description="Filter for price-to-sales ratio strictly less than the specified value.", json_schema_extra={'format': 'double'})
    price_to_sales_lte: float | None = Field(default=None, validation_alias="price_to_sales.lte", serialization_alias="price_to_sales.lte", description="Filter for price-to-sales ratio less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    price_to_cash_flow_gt: float | None = Field(default=None, validation_alias="price_to_cash_flow.gt", serialization_alias="price_to_cash_flow.gt", description="Filter for price-to-cash flow ratio strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    price_to_cash_flow_gte: float | None = Field(default=None, validation_alias="price_to_cash_flow.gte", serialization_alias="price_to_cash_flow.gte", description="Filter for price-to-cash flow ratio greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    price_to_cash_flow_lt: float | None = Field(default=None, validation_alias="price_to_cash_flow.lt", serialization_alias="price_to_cash_flow.lt", description="Filter for price-to-cash flow ratio strictly less than the specified value.", json_schema_extra={'format': 'double'})
    price_to_cash_flow_lte: float | None = Field(default=None, validation_alias="price_to_cash_flow.lte", serialization_alias="price_to_cash_flow.lte", description="Filter for price-to-cash flow ratio less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    price_to_free_cash_flow_gt: float | None = Field(default=None, validation_alias="price_to_free_cash_flow.gt", serialization_alias="price_to_free_cash_flow.gt", description="Filter for price-to-free cash flow ratio strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    price_to_free_cash_flow_gte: float | None = Field(default=None, validation_alias="price_to_free_cash_flow.gte", serialization_alias="price_to_free_cash_flow.gte", description="Filter for price-to-free cash flow ratio greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    price_to_free_cash_flow_lt: float | None = Field(default=None, validation_alias="price_to_free_cash_flow.lt", serialization_alias="price_to_free_cash_flow.lt", description="Filter for price-to-free cash flow ratio strictly less than the specified value.", json_schema_extra={'format': 'double'})
    price_to_free_cash_flow_lte: float | None = Field(default=None, validation_alias="price_to_free_cash_flow.lte", serialization_alias="price_to_free_cash_flow.lte", description="Filter for price-to-free cash flow ratio less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    dividend_yield_gt: float | None = Field(default=None, validation_alias="dividend_yield.gt", serialization_alias="dividend_yield.gt", description="Filter for dividend yield strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    dividend_yield_gte: float | None = Field(default=None, validation_alias="dividend_yield.gte", serialization_alias="dividend_yield.gte", description="Filter for dividend yield greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    dividend_yield_lt: float | None = Field(default=None, validation_alias="dividend_yield.lt", serialization_alias="dividend_yield.lt", description="Filter for dividend yield strictly less than the specified value.", json_schema_extra={'format': 'double'})
    dividend_yield_lte: float | None = Field(default=None, validation_alias="dividend_yield.lte", serialization_alias="dividend_yield.lte", description="Filter for dividend yield less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    return_on_assets_gt: float | None = Field(default=None, validation_alias="return_on_assets.gt", serialization_alias="return_on_assets.gt", description="Filter for return on assets (ROA) strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    return_on_assets_gte: float | None = Field(default=None, validation_alias="return_on_assets.gte", serialization_alias="return_on_assets.gte", description="Filter for return on assets (ROA) greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    return_on_assets_lt: float | None = Field(default=None, validation_alias="return_on_assets.lt", serialization_alias="return_on_assets.lt", description="Filter for return on assets (ROA) strictly less than the specified value.", json_schema_extra={'format': 'double'})
    return_on_assets_lte: float | None = Field(default=None, validation_alias="return_on_assets.lte", serialization_alias="return_on_assets.lte", description="Filter for return on assets (ROA) less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    return_on_equity_gt: float | None = Field(default=None, validation_alias="return_on_equity.gt", serialization_alias="return_on_equity.gt", description="Filter for return on equity (ROE) strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    return_on_equity_gte: float | None = Field(default=None, validation_alias="return_on_equity.gte", serialization_alias="return_on_equity.gte", description="Filter for return on equity (ROE) greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    return_on_equity_lt: float | None = Field(default=None, validation_alias="return_on_equity.lt", serialization_alias="return_on_equity.lt", description="Filter for return on equity (ROE) strictly less than the specified value.", json_schema_extra={'format': 'double'})
    return_on_equity_lte: float | None = Field(default=None, validation_alias="return_on_equity.lte", serialization_alias="return_on_equity.lte", description="Filter for return on equity (ROE) less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    debt_to_equity_gt: float | None = Field(default=None, validation_alias="debt_to_equity.gt", serialization_alias="debt_to_equity.gt", description="Filter for debt-to-equity ratio strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    debt_to_equity_gte: float | None = Field(default=None, validation_alias="debt_to_equity.gte", serialization_alias="debt_to_equity.gte", description="Filter for debt-to-equity ratio greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    debt_to_equity_lt: float | None = Field(default=None, validation_alias="debt_to_equity.lt", serialization_alias="debt_to_equity.lt", description="Filter for debt-to-equity ratio strictly less than the specified value.", json_schema_extra={'format': 'double'})
    debt_to_equity_lte: float | None = Field(default=None, validation_alias="debt_to_equity.lte", serialization_alias="debt_to_equity.lte", description="Filter for debt-to-equity ratio less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    current_gt: float | None = Field(default=None, validation_alias="current.gt", serialization_alias="current.gt", description="Filter for current ratio strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    current_gte: float | None = Field(default=None, validation_alias="current.gte", serialization_alias="current.gte", description="Filter for current ratio greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    current_lt: float | None = Field(default=None, validation_alias="current.lt", serialization_alias="current.lt", description="Filter for current ratio strictly less than the specified value.", json_schema_extra={'format': 'double'})
    current_lte: float | None = Field(default=None, validation_alias="current.lte", serialization_alias="current.lte", description="Filter for current ratio less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    quick_gt: float | None = Field(default=None, validation_alias="quick.gt", serialization_alias="quick.gt", description="Filter for quick ratio strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    quick_gte: float | None = Field(default=None, validation_alias="quick.gte", serialization_alias="quick.gte", description="Filter for quick ratio greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    quick_lt: float | None = Field(default=None, validation_alias="quick.lt", serialization_alias="quick.lt", description="Filter for quick ratio strictly less than the specified value.", json_schema_extra={'format': 'double'})
    quick_lte: float | None = Field(default=None, validation_alias="quick.lte", serialization_alias="quick.lte", description="Filter for quick ratio less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    cash_gt: float | None = Field(default=None, validation_alias="cash.gt", serialization_alias="cash.gt", description="Filter for cash ratio strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    cash_gte: float | None = Field(default=None, validation_alias="cash.gte", serialization_alias="cash.gte", description="Filter for cash ratio greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    cash_lt: float | None = Field(default=None, validation_alias="cash.lt", serialization_alias="cash.lt", description="Filter for cash ratio strictly less than the specified value.", json_schema_extra={'format': 'double'})
    cash_lte: float | None = Field(default=None, validation_alias="cash.lte", serialization_alias="cash.lte", description="Filter for cash ratio less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    ev_to_sales_gt: float | None = Field(default=None, validation_alias="ev_to_sales.gt", serialization_alias="ev_to_sales.gt", description="Filter for enterprise value-to-sales ratio strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    ev_to_sales_gte: float | None = Field(default=None, validation_alias="ev_to_sales.gte", serialization_alias="ev_to_sales.gte", description="Filter for enterprise value-to-sales ratio greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    ev_to_sales_lt: float | None = Field(default=None, validation_alias="ev_to_sales.lt", serialization_alias="ev_to_sales.lt", description="Filter for enterprise value-to-sales ratio strictly less than the specified value.", json_schema_extra={'format': 'double'})
    ev_to_sales_lte: float | None = Field(default=None, validation_alias="ev_to_sales.lte", serialization_alias="ev_to_sales.lte", description="Filter for enterprise value-to-sales ratio less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    ev_to_ebitda_gt: float | None = Field(default=None, validation_alias="ev_to_ebitda.gt", serialization_alias="ev_to_ebitda.gt", description="Filter for enterprise value-to-EBITDA ratio strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    ev_to_ebitda_gte: float | None = Field(default=None, validation_alias="ev_to_ebitda.gte", serialization_alias="ev_to_ebitda.gte", description="Filter for enterprise value-to-EBITDA ratio greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    ev_to_ebitda_lt: float | None = Field(default=None, validation_alias="ev_to_ebitda.lt", serialization_alias="ev_to_ebitda.lt", description="Filter for enterprise value-to-EBITDA ratio strictly less than the specified value.", json_schema_extra={'format': 'double'})
    ev_to_ebitda_lte: float | None = Field(default=None, validation_alias="ev_to_ebitda.lte", serialization_alias="ev_to_ebitda.lte", description="Filter for enterprise value-to-EBITDA ratio less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    enterprise_value_gt: float | None = Field(default=None, validation_alias="enterprise_value.gt", serialization_alias="enterprise_value.gt", description="Filter for enterprise value strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    enterprise_value_gte: float | None = Field(default=None, validation_alias="enterprise_value.gte", serialization_alias="enterprise_value.gte", description="Filter for enterprise value greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    enterprise_value_lt: float | None = Field(default=None, validation_alias="enterprise_value.lt", serialization_alias="enterprise_value.lt", description="Filter for enterprise value strictly less than the specified value.", json_schema_extra={'format': 'double'})
    enterprise_value_lte: float | None = Field(default=None, validation_alias="enterprise_value.lte", serialization_alias="enterprise_value.lte", description="Filter for enterprise value less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    free_cash_flow_gt: float | None = Field(default=None, validation_alias="free_cash_flow.gt", serialization_alias="free_cash_flow.gt", description="Filter for free cash flow strictly greater than the specified value.", json_schema_extra={'format': 'double'})
    free_cash_flow_gte: float | None = Field(default=None, validation_alias="free_cash_flow.gte", serialization_alias="free_cash_flow.gte", description="Filter for free cash flow greater than or equal to the specified value.", json_schema_extra={'format': 'double'})
    free_cash_flow_lt: float | None = Field(default=None, validation_alias="free_cash_flow.lt", serialization_alias="free_cash_flow.lt", description="Filter for free cash flow strictly less than the specified value.", json_schema_extra={'format': 'double'})
    free_cash_flow_lte: float | None = Field(default=None, validation_alias="free_cash_flow.lte", serialization_alias="free_cash_flow.lte", description="Filter for free cash flow less than or equal to the specified value.", json_schema_extra={'format': 'double'})
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 100 if not specified; maximum allowed is 50,000.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with each column optionally suffixed by '.asc' or '.desc' to specify sort direction. Defaults to 'ticker.asc' if not specified.")
class GetStocksFinancialsV1RatiosRequest(StrictModel):
    """Retrieve comprehensive financial ratios for public companies including valuation, profitability, liquidity, and leverage metrics. Data combines income statements, balance sheets, and cash flow statements with daily stock prices, using trailing twelve months (TTM) data for income/cash flow metrics and quarterly data for balance sheet items."""
    query: GetStocksFinancialsV1RatiosRequestQuery | None = None

# Operation: list_risk_factor_taxonomies
class GetStocksTaxonomiesVXRiskFactorsRequestQuery(StrictModel):
    taxonomy_gt: float | None = Field(default=None, validation_alias="taxonomy.gt", serialization_alias="taxonomy.gt", description="Filter taxonomies with a value strictly greater than the specified number.", json_schema_extra={'format': 'double'})
    taxonomy_gte: float | None = Field(default=None, validation_alias="taxonomy.gte", serialization_alias="taxonomy.gte", description="Filter taxonomies with a value greater than or equal to the specified number.", json_schema_extra={'format': 'double'})
    taxonomy_lt: float | None = Field(default=None, validation_alias="taxonomy.lt", serialization_alias="taxonomy.lt", description="Filter taxonomies with a value strictly less than the specified number.", json_schema_extra={'format': 'double'})
    taxonomy_lte: float | None = Field(default=None, validation_alias="taxonomy.lte", serialization_alias="taxonomy.lte", description="Filter taxonomies with a value less than or equal to the specified number.", json_schema_extra={'format': 'double'})
    primary_category_any_of: str | None = Field(default=None, validation_alias="primary_category.any_of", serialization_alias="primary_category.any_of", description="Filter to include only taxonomies whose primary category matches any of the specified values. Provide multiple values as a comma-separated list.")
    primary_category_gt: str | None = Field(default=None, validation_alias="primary_category.gt", serialization_alias="primary_category.gt", description="Filter taxonomies by primary category values strictly greater than the specified value (alphabetically for strings).")
    primary_category_gte: str | None = Field(default=None, validation_alias="primary_category.gte", serialization_alias="primary_category.gte", description="Filter taxonomies by primary category values greater than or equal to the specified value (alphabetically for strings).")
    primary_category_lt: str | None = Field(default=None, validation_alias="primary_category.lt", serialization_alias="primary_category.lt", description="Filter taxonomies by primary category values strictly less than the specified value (alphabetically for strings).")
    primary_category_lte: str | None = Field(default=None, validation_alias="primary_category.lte", serialization_alias="primary_category.lte", description="Filter taxonomies by primary category values less than or equal to the specified value (alphabetically for strings).")
    secondary_category_any_of: str | None = Field(default=None, validation_alias="secondary_category.any_of", serialization_alias="secondary_category.any_of", description="Filter to include only taxonomies whose secondary category matches any of the specified values. Provide multiple values as a comma-separated list.")
    secondary_category_gt: str | None = Field(default=None, validation_alias="secondary_category.gt", serialization_alias="secondary_category.gt", description="Filter taxonomies by secondary category values strictly greater than the specified value (alphabetically for strings).")
    secondary_category_gte: str | None = Field(default=None, validation_alias="secondary_category.gte", serialization_alias="secondary_category.gte", description="Filter taxonomies by secondary category values greater than or equal to the specified value (alphabetically for strings).")
    secondary_category_lt: str | None = Field(default=None, validation_alias="secondary_category.lt", serialization_alias="secondary_category.lt", description="Filter taxonomies by secondary category values strictly less than the specified value (alphabetically for strings).")
    secondary_category_lte: str | None = Field(default=None, validation_alias="secondary_category.lte", serialization_alias="secondary_category.lte", description="Filter taxonomies by secondary category values less than or equal to the specified value (alphabetically for strings).")
    tertiary_category_any_of: str | None = Field(default=None, validation_alias="tertiary_category.any_of", serialization_alias="tertiary_category.any_of", description="Filter to include only taxonomies whose tertiary category matches any of the specified values. Provide multiple values as a comma-separated list.")
    tertiary_category_gt: str | None = Field(default=None, validation_alias="tertiary_category.gt", serialization_alias="tertiary_category.gt", description="Filter taxonomies by tertiary category values strictly greater than the specified value (alphabetically for strings).")
    tertiary_category_gte: str | None = Field(default=None, validation_alias="tertiary_category.gte", serialization_alias="tertiary_category.gte", description="Filter taxonomies by tertiary category values greater than or equal to the specified value (alphabetically for strings).")
    tertiary_category_lt: str | None = Field(default=None, validation_alias="tertiary_category.lt", serialization_alias="tertiary_category.lt", description="Filter taxonomies by tertiary category values strictly less than the specified value (alphabetically for strings).")
    tertiary_category_lte: str | None = Field(default=None, validation_alias="tertiary_category.lte", serialization_alias="tertiary_category.lte", description="Filter taxonomies by tertiary category values less than or equal to the specified value (alphabetically for strings).")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 200 if not specified; maximum allowed is 999.", ge=1, le=1000)
    sort: str | None = Field(default=None, description="Sort results by one or more columns in ascending or descending order. Specify columns as a comma-separated list with '.asc' or '.desc' suffix (e.g., 'taxonomy.asc,primary_category.desc'). Defaults to 'taxonomy.desc' if not specified.")
class GetStocksTaxonomiesVXRiskFactorsRequest(StrictModel):
    """Retrieve the complete taxonomy of risk factor classifications used across the platform. Filter and sort by taxonomy value, primary/secondary/tertiary categories to find specific risk factor definitions."""
    query: GetStocksTaxonomiesVXRiskFactorsRequestQuery | None = None

# Operation: list_stock_dividends
class GetStocksV1DividendsRequestQuery(StrictModel):
    frequency_gt: int | None = Field(default=None, validation_alias="frequency.gt", serialization_alias="frequency.gt", description="Filter results to dividends with a frequency value greater than the specified integer.", json_schema_extra={'format': 'int64'})
    frequency_gte: int | None = Field(default=None, validation_alias="frequency.gte", serialization_alias="frequency.gte", description="Filter results to dividends with a frequency value greater than or equal to the specified integer.", json_schema_extra={'format': 'int64'})
    frequency_lt: int | None = Field(default=None, validation_alias="frequency.lt", serialization_alias="frequency.lt", description="Filter results to dividends with a frequency value less than the specified integer.", json_schema_extra={'format': 'int64'})
    frequency_lte: int | None = Field(default=None, validation_alias="frequency.lte", serialization_alias="frequency.lte", description="Filter results to dividends with a frequency value less than or equal to the specified integer.", json_schema_extra={'format': 'int64'})
    distribution_type_any_of: Literal["recurring", "special", "supplemental", "irregular", "unknown"] | None = Field(default=None, validation_alias="distribution_type.any_of", serialization_alias="distribution_type.any_of", description="Filter results to dividends matching any of the specified distribution types. Accepts comma-separated values from: recurring, special, supplemental, irregular, or unknown.")
    limit: int | None = Field(default=None, description="Maximum number of results to return per request. Defaults to 100 if not specified; maximum allowed is 5000.", ge=1, le=5001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with sort direction specified per column using '.asc' or '.desc' suffix. Defaults to sorting by ticker in ascending order if not specified.")
class GetStocksV1DividendsRequest(StrictModel):
    """Retrieve historical dividend payment records for US stocks, including split-adjusted amounts and historical adjustment factors for price normalization. Filter by dividend frequency and distribution type, with flexible sorting and pagination options."""
    query: GetStocksV1DividendsRequestQuery | None = None

# Operation: list_short_interest
class GetStocksV1ShortInterestRequestQuery(StrictModel):
    days_to_cover: float | None = Field(default=None, description="Filter results by days-to-cover ratio, calculated as short interest divided by average daily volume. Accepts decimal values to represent the estimated number of trading days needed to cover all short positions at current volume levels.", json_schema_extra={'format': 'double'})
    settlement_date: str | None = Field(default=None, description="Filter results by settlement date in YYYY-MM-DD format, typically aligned with exchange reporting schedules when short interest data becomes official.")
    avg_daily_volume: int | None = Field(default=None, description="Filter results by average daily trading volume as an integer, used to contextualize short interest levels and calculate days-to-cover metrics.", json_schema_extra={'format': 'int64'})
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Defaults to 10 if not specified; maximum allowed value is 50,000.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with each column followed by .asc or .desc to specify ascending or descending order. Defaults to sorting by ticker in ascending order if not specified.")
class GetStocksV1ShortInterestRequest(StrictModel):
    """Retrieve FINRA short interest data for securities on a specific settlement date, including metrics on short positions, trading volume, and days-to-cover calculations."""
    query: GetStocksV1ShortInterestRequestQuery | None = None

# Operation: list_short_volume_by_ticker
class GetStocksV1ShortVolumeRequestQuery(StrictModel):
    short_volume_ratio_any_of: str | None = Field(default=None, validation_alias="short_volume_ratio.any_of", serialization_alias="short_volume_ratio.any_of", description="Filter results to include only records where the short volume ratio matches any of the specified values. Provide multiple values as a comma-separated list of floating point numbers.")
    short_volume_ratio_gt: float | None = Field(default=None, validation_alias="short_volume_ratio.gt", serialization_alias="short_volume_ratio.gt", description="Filter results to include only records where the short volume ratio is strictly greater than the specified floating point value.", json_schema_extra={'format': 'double'})
    short_volume_ratio_gte: float | None = Field(default=None, validation_alias="short_volume_ratio.gte", serialization_alias="short_volume_ratio.gte", description="Filter results to include only records where the short volume ratio is greater than or equal to the specified floating point value.", json_schema_extra={'format': 'double'})
    short_volume_ratio_lt: float | None = Field(default=None, validation_alias="short_volume_ratio.lt", serialization_alias="short_volume_ratio.lt", description="Filter results to include only records where the short volume ratio is strictly less than the specified floating point value.", json_schema_extra={'format': 'double'})
    short_volume_ratio_lte: float | None = Field(default=None, validation_alias="short_volume_ratio.lte", serialization_alias="short_volume_ratio.lte", description="Filter results to include only records where the short volume ratio is less than or equal to the specified floating point value.", json_schema_extra={'format': 'double'})
    limit: int | None = Field(default=None, description="Limit the number of results returned. Defaults to 10 if not specified. Maximum allowed value is 50,000.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Sort results by one or more columns in ascending or descending order. Specify columns as a comma-separated list with '.asc' or '.desc' appended to each column name (e.g., 'ticker.asc,short_volume_ratio.desc'). Defaults to sorting by ticker in ascending order.")
class GetStocksV1ShortVolumeRequest(StrictModel):
    """Retrieve short selling volume data across stock tickers, including total trading volume, short sale metrics, and platform-specific breakdowns. Filter and sort results to analyze short selling activity."""
    query: GetStocksV1ShortVolumeRequestQuery | None = None

# Operation: list_stock_splits_historical
class GetStocksV1SplitsRequestQuery(StrictModel):
    execution_date_gt: str | None = Field(default=None, validation_alias="execution_date.gt", serialization_alias="execution_date.gt", description="Filter results to splits executed after this date (exclusive). Use ISO 8601 format: yyyy-mm-dd.")
    execution_date_gte: str | None = Field(default=None, validation_alias="execution_date.gte", serialization_alias="execution_date.gte", description="Filter results to splits executed on or after this date (inclusive). Use ISO 8601 format: yyyy-mm-dd.")
    execution_date_lt: str | None = Field(default=None, validation_alias="execution_date.lt", serialization_alias="execution_date.lt", description="Filter results to splits executed before this date (exclusive). Use ISO 8601 format: yyyy-mm-dd.")
    execution_date_lte: str | None = Field(default=None, validation_alias="execution_date.lte", serialization_alias="execution_date.lte", description="Filter results to splits executed on or before this date (inclusive). Use ISO 8601 format: yyyy-mm-dd.")
    adjustment_type_any_of: Literal["forward_split", "reverse_split", "stock_dividend"] | None = Field(default=None, validation_alias="adjustment_type.any_of", serialization_alias="adjustment_type.any_of", description="Filter results by split type. Accepts one or more values (forward_split, reverse_split, or stock_dividend) as a comma-separated list.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 100 if not specified; maximum allowed is 5000.", ge=1, le=5001)
    sort: str | None = Field(default=None, description="Sort results by one or more columns in ascending or descending order. Specify as comma-separated list with '.asc' or '.desc' suffix (e.g., 'execution_date.desc'). Defaults to 'execution_date.desc' if not specified.")
class GetStocksV1SplitsRequest(StrictModel):
    """Retrieve historical stock split and reverse split events for US equities, including adjustment factors for normalizing historical price data."""
    query: GetStocksV1SplitsRequestQuery | None = None

# Operation: list_stocks_by_float
class GetStocksVXFloatRequestQuery(StrictModel):
    free_float_percent_gt: float | None = Field(default=None, validation_alias="free_float_percent.gt", serialization_alias="free_float_percent.gt", description="Filter results to securities with free float percentage greater than this value. Accepts decimal numbers.", json_schema_extra={'format': 'double'})
    free_float_percent_gte: float | None = Field(default=None, validation_alias="free_float_percent.gte", serialization_alias="free_float_percent.gte", description="Filter results to securities with free float percentage greater than or equal to this value. Accepts decimal numbers.", json_schema_extra={'format': 'double'})
    free_float_percent_lt: float | None = Field(default=None, validation_alias="free_float_percent.lt", serialization_alias="free_float_percent.lt", description="Filter results to securities with free float percentage less than this value. Accepts decimal numbers.", json_schema_extra={'format': 'double'})
    free_float_percent_lte: float | None = Field(default=None, validation_alias="free_float_percent.lte", serialization_alias="free_float_percent.lte", description="Filter results to securities with free float percentage less than or equal to this value. Accepts decimal numbers.", json_schema_extra={'format': 'double'})
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 100 if not specified; maximum allowed is 5000.", ge=1, le=5001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with each column followed by '.asc' or '.desc' to specify direction. Defaults to sorting by ticker in ascending order.")
class GetStocksVXFloatRequest(StrictModel):
    """Retrieve free float data for US-listed securities, including the number of shares available for public trading and the percentage of total shares outstanding. Results can be filtered by free float percentage and sorted by multiple columns."""
    query: GetStocksVXFloatRequestQuery | None = None

# Operation: list_corporate_events
class GetTmxV1CorporateEventsRequestQuery(StrictModel):
    status: str | None = Field(default=None, description="Filter events by their current status. Valid statuses are: approved, canceled, confirmed, historical, pending_approval, postponed, and unconfirmed.")
    tmx_company_id: int | None = Field(default=None, description="Filter events by the TMX company identifier. Accepts a specific company ID as a 64-bit integer.", json_schema_extra={'format': 'int64'})
    tmx_company_id_gt: int | None = Field(default=None, validation_alias="tmx_company_id.gt", serialization_alias="tmx_company_id.gt", description="Filter to companies with TMX ID greater than the specified value (64-bit integer).", json_schema_extra={'format': 'int64'})
    tmx_company_id_gte: int | None = Field(default=None, validation_alias="tmx_company_id.gte", serialization_alias="tmx_company_id.gte", description="Filter to companies with TMX ID greater than or equal to the specified value (64-bit integer).", json_schema_extra={'format': 'int64'})
    tmx_company_id_lt: int | None = Field(default=None, validation_alias="tmx_company_id.lt", serialization_alias="tmx_company_id.lt", description="Filter to companies with TMX ID less than the specified value (64-bit integer).", json_schema_extra={'format': 'int64'})
    tmx_company_id_lte: int | None = Field(default=None, validation_alias="tmx_company_id.lte", serialization_alias="tmx_company_id.lte", description="Filter to companies with TMX ID less than or equal to the specified value (64-bit integer).", json_schema_extra={'format': 'int64'})
    tmx_record_id: str | None = Field(default=None, description="Filter events by the unique TMX event record identifier (alphanumeric string).")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Must be between 1 and 50,000; defaults to 100 if not specified.", ge=1, le=50001)
    sort: str | None = Field(default=None, description="Comma-separated list of columns to sort by, with '.asc' or '.desc' appended to each column to specify direction. Defaults to sorting by date in descending order if not specified.")
class GetTmxV1CorporateEventsRequest(StrictModel):
    """Retrieve corporate events and announcements for publicly traded companies, including earnings releases, conferences, dividends, and business updates from TMX. Filter by company, event status, or record ID, and customize result ordering and pagination."""
    query: GetTmxV1CorporateEventsRequestQuery | None = None

# Operation: get_currency_conversion
class RealTimeCurrencyConversionRequestPath(StrictModel):
    from_: str = Field(default=..., validation_alias="from", serialization_alias="from", description="The source currency code (e.g., AUD, USD). Use standard ISO 4217 three-letter currency codes.")
    to: str = Field(default=..., description="The target currency code (e.g., USD, CAD). Use standard ISO 4217 three-letter currency codes.")
class RealTimeCurrencyConversionRequestQuery(StrictModel):
    amount: float | None = Field(default=None, description="The amount to convert as a decimal number. Defaults to 1 if not specified.")
    precision: Literal[0, 1, 2, 3, 4] | None = Field(default=None, description="The number of decimal places for the conversion result, ranging from 0 to 4. Defaults to 2 decimal places.")
class RealTimeCurrencyConversionRequest(StrictModel):
    """Convert between two currencies using real-time market rates. Supports bidirectional conversion (e.g., USD to CAD or CAD to USD) with customizable amount and decimal precision."""
    path: RealTimeCurrencyConversionRequestPath
    query: RealTimeCurrencyConversionRequestQuery | None = None

# Operation: get_historic_forex_ticks
class DeprecatedGetHistoricForexQuotesRequestPath(StrictModel):
    from_: str = Field(default=..., validation_alias="from", serialization_alias="from", description="The source currency code (e.g., USD, AUD, EUR) in the currency pair.")
    to: str = Field(default=..., description="The target currency code (e.g., JPY, USD, GBP) in the currency pair.")
    date: str = Field(default=..., description="The date for which to retrieve historic ticks, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
class DeprecatedGetHistoricForexQuotesRequestQuery(StrictModel):
    offset: int | None = Field(default=None, description="Pagination offset for retrieving subsequent pages of results. Pass the timestamp value from the last result of the previous page to continue from that point.")
    limit: int | None = Field(default=None, description="Maximum number of ticks to return in the response. Accepts values up to 10,000.")
class DeprecatedGetHistoricForexQuotesRequest(StrictModel):
    """Retrieve historic tick data for a forex currency pair on a specific date. Use pagination parameters to navigate through large result sets."""
    path: DeprecatedGetHistoricForexQuotesRequestPath
    query: DeprecatedGetHistoricForexQuotesRequestQuery | None = None

# Operation: get_crypto_ema
class CryptoEmaRequestPath(StrictModel):
    crypto_ticker: str = Field(default=..., validation_alias="cryptoTicker", serialization_alias="cryptoTicker", description="The cryptocurrency ticker symbol (e.g., X:BTCUSD for Bitcoin in USD).")
class CryptoEmaRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for aggregating price data. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregates.")
    window: int | None = Field(default=None, description="The number of periods to include in the EMA calculation. For example, a window of 10 with daily timespan calculates a 10-day moving average. Defaults to 50 periods.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="The price type used for EMA calculation: open, high, low, or close price. Defaults to close price.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp: ascending (oldest first) or descending (newest first). Defaults to descending.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Accepts 1 to 5000 results, defaults to 10.", le=5000)
class CryptoEmaRequest(StrictModel):
    """Retrieve the exponential moving average (EMA) for a cryptocurrency ticker over a specified time range. Use this to analyze price trends and momentum across different timeframes and price types."""
    path: CryptoEmaRequestPath
    query: CryptoEmaRequestQuery | None = None

# Operation: get_forex_ema
class ForexEmaRequestPath(StrictModel):
    fx_ticker: str = Field(default=..., validation_alias="fxTicker", serialization_alias="fxTicker", description="The forex ticker symbol to analyze, formatted as a currency pair (e.g., C:EURUSD for EUR/USD).")
class ForexEmaRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for aggregating price data before EMA calculation. Options include minute, hour, day, week, month, quarter, or year. Defaults to daily aggregates.")
    adjusted: bool | None = Field(default=None, description="Whether to adjust aggregates for corporate actions like splits. When true (default), results reflect adjusted prices; set to false for unadjusted data.")
    window: int | None = Field(default=None, description="The number of periods used in the EMA calculation. For example, a window of 10 with daily timespan produces a 10-day moving average. Defaults to 50 periods.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="The price type used for EMA calculation: open, high, low, or close. Defaults to close price.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending order.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Accepts values from 1 to 5000, with a default of 10 results.", le=5000)
class ForexEmaRequest(StrictModel):
    """Calculate the exponential moving average (EMA) for a forex currency pair over a specified time range. Returns EMA values based on configurable aggregation periods and price series."""
    path: ForexEmaRequestPath
    query: ForexEmaRequestQuery | None = None

# Operation: get_exponential_moving_average
class IndicesEmaRequestPath(StrictModel):
    indices_ticker: str = Field(default=..., validation_alias="indicesTicker", serialization_alias="indicesTicker", description="The ticker symbol for the index (e.g., I:NDX for Nasdaq-100). Required to identify which index to calculate EMA for.")
class IndicesEmaRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for aggregating data before calculating EMA. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregates.")
    adjusted: bool | None = Field(default=None, description="Whether to adjust aggregates for stock splits and dividends. Set to true (default) for split-adjusted results, or false for unadjusted raw data.")
    window: int | None = Field(default=None, description="The number of periods to use in the EMA calculation. For example, a window of 10 with daily timespan produces a 10-day moving average. Defaults to 50 periods.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="Which price value to use for EMA calculation: open, high, low, or close. Defaults to close price.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending (most recent first).")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Accepts 1 to 5000 results. Defaults to 10 results.", le=5000)
class IndicesEmaRequest(StrictModel):
    """Retrieve the exponential moving average (EMA) for an indices ticker over a specified time range. Use this to analyze trend direction and momentum for index symbols like NDX."""
    path: IndicesEmaRequestPath
    query: IndicesEmaRequestQuery | None = None

# Operation: get_ema_for_options_ticker
class OptionsEmaRequestPath(StrictModel):
    options_ticker: str = Field(default=..., validation_alias="optionsTicker", serialization_alias="optionsTicker", description="The options ticker symbol to analyze, formatted as an options contract identifier (e.g., O:SPY241220P00720000).")
class OptionsEmaRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for aggregating price data before calculating EMA. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregates.")
    adjusted: bool | None = Field(default=None, description="Whether to adjust aggregates for stock splits and dividends. Set to true (default) for split-adjusted results, or false for unadjusted raw data.")
    window: int | None = Field(default=None, description="The number of periods to use in the EMA calculation. For example, a window of 10 with daily timespan produces a 10-day moving average. Defaults to 50 periods.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="The price type to use for EMA calculation: open, high, low, or close. Defaults to close price.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending (most recent first).")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Accepts values from 1 to 5000, with a default of 10 results.", le=5000)
class OptionsEmaRequest(StrictModel):
    """Calculate and retrieve the exponential moving average (EMA) for an options ticker symbol over a specified time range. Use this to analyze price trends and momentum for options contracts."""
    path: OptionsEmaRequestPath
    query: OptionsEmaRequestQuery | None = None

# Operation: get_exponential_moving_average_stock
class EmaRequestPath(StrictModel):
    stock_ticker: str = Field(default=..., validation_alias="stockTicker", serialization_alias="stockTicker", description="The stock ticker symbol to retrieve EMA data for (case-sensitive). For example, AAPL for Apple Inc.")
class EmaRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for aggregating price data before calculating the EMA. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregates.")
    adjusted: bool | None = Field(default=None, description="Whether to adjust aggregates for stock splits and dividends. When true (default), results reflect adjusted prices; set to false for unadjusted data.")
    window: int | None = Field(default=None, description="The number of periods to use in the EMA calculation. For example, a window of 10 with daily aggregates produces a 10-day moving average. Defaults to 50 periods.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="The price type used to calculate the EMA: open, high, low, or close. Defaults to using closing prices.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending order.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Accepts values from 1 to 5000, with a default of 10 results.", le=5000)
class EmaRequest(StrictModel):
    """Retrieve the exponential moving average (EMA) for a stock ticker over a specified time range. The EMA is calculated based on aggregated price data at your chosen timespan interval."""
    path: EmaRequestPath
    query: EmaRequestQuery | None = None

# Operation: get_crypto_macd
class CryptoMacdRequestPath(StrictModel):
    crypto_ticker: str = Field(default=..., validation_alias="cryptoTicker", serialization_alias="cryptoTicker", description="The cryptocurrency ticker symbol (e.g., X:BTCUSD for Bitcoin in USD).")
class CryptoMacdRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for each data point: minute, hour, day, week, month, quarter, or year. Defaults to daily aggregation.")
    short_window: int | None = Field(default=None, description="The number of periods for the short-term exponential moving average used in MACD calculation. Defaults to 12.")
    long_window: int | None = Field(default=None, description="The number of periods for the long-term exponential moving average used in MACD calculation. Defaults to 26.")
    signal_window: int | None = Field(default=None, description="The number of periods for the signal line (exponential moving average of MACD). Defaults to 9.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="The price type to use for calculations: open, high, low, or close. Defaults to close price.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp: ascending (oldest first) or descending (newest first). Defaults to descending.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 10, with a maximum of 5000.", le=5000)
class CryptoMacdRequest(StrictModel):
    """Retrieve Moving Average Convergence/Divergence (MACD) technical indicator data for a cryptocurrency ticker over a specified time range. MACD helps identify trend changes and momentum by comparing exponential moving averages."""
    path: CryptoMacdRequestPath
    query: CryptoMacdRequestQuery | None = None

# Operation: get_macd_indicator_forex
class ForexMacdRequestPath(StrictModel):
    fx_ticker: str = Field(default=..., validation_alias="fxTicker", serialization_alias="fxTicker", description="The forex ticker symbol to analyze (e.g., C:EURUSD for EUR/USD currency pair).")
class ForexMacdRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for aggregating price data: minute, hour, day, week, month, quarter, or year. Defaults to daily aggregates.")
    adjusted: bool | None = Field(default=None, description="Whether to adjust aggregates for stock splits and corporate actions. Enabled by default; set to false to use unadjusted prices.")
    short_window: int | None = Field(default=None, description="The number of periods for the short-term exponential moving average used in MACD calculation. Defaults to 12 periods.")
    long_window: int | None = Field(default=None, description="The number of periods for the long-term exponential moving average used in MACD calculation. Defaults to 26 periods.")
    signal_window: int | None = Field(default=None, description="The number of periods for calculating the MACD signal line (exponential moving average of MACD). Defaults to 9 periods.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="The price type to use for MACD calculation: open, high, low, or close. Defaults to close price.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp: ascending (oldest first) or descending (newest first). Defaults to descending.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 10; maximum allowed is 5000.", le=5000)
class ForexMacdRequest(StrictModel):
    """Retrieve Moving Average Convergence/Divergence (MACD) indicator data for a forex ticker symbol. MACD is a momentum oscillator that measures the relationship between two exponential moving averages to identify trend direction and momentum shifts."""
    path: ForexMacdRequestPath
    query: ForexMacdRequestQuery | None = None

# Operation: get_macd_for_indices
class IndicesMacdRequestPath(StrictModel):
    indices_ticker: str = Field(default=..., validation_alias="indicesTicker", serialization_alias="indicesTicker", description="The ticker symbol for the indices (e.g., I:NDX for Nasdaq-100). Required to identify which index to retrieve MACD data for.")
class IndicesMacdRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for aggregating price data before calculating MACD. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregation.")
    adjusted: bool | None = Field(default=None, description="Whether to adjust aggregated price data for stock splits and dividends. When true (default), results reflect adjusted prices; set to false for unadjusted data.")
    short_window: int | None = Field(default=None, description="The number of periods for the short-term exponential moving average used in MACD calculation. Defaults to 12 periods; lower values make the indicator more responsive to recent price changes.")
    long_window: int | None = Field(default=None, description="The number of periods for the long-term exponential moving average used in MACD calculation. Defaults to 26 periods; higher values smooth out short-term volatility.")
    signal_window: int | None = Field(default=None, description="The number of periods for calculating the MACD signal line, which is an exponential moving average of the MACD line itself. Defaults to 9 periods.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="The price series to use for MACD calculation: open, high, low, or close. Defaults to close price, which is the most common choice for technical analysis.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending order (most recent data first).")
    limit: int | None = Field(default=None, description="Maximum number of MACD data points to return. Defaults to 10 results; can be increased up to 5000 for larger datasets.", le=5000)
class IndicesMacdRequest(StrictModel):
    """Retrieve Moving Average Convergence/Divergence (MACD) indicator values for an indices ticker over a specified time range. MACD is a momentum indicator that shows the relationship between two moving averages of price."""
    path: IndicesMacdRequestPath
    query: IndicesMacdRequestQuery | None = None

# Operation: get_macd_for_options_ticker
class OptionsMacdRequestPath(StrictModel):
    options_ticker: str = Field(default=..., validation_alias="optionsTicker", serialization_alias="optionsTicker", description="The options ticker symbol to analyze, formatted as an options contract identifier (e.g., O:SPY241220P00720000).")
class OptionsMacdRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for aggregating price data before calculating MACD. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregation.")
    adjusted: bool | None = Field(default=None, description="Whether to adjust price aggregates for stock splits before calculating MACD. When true (default), results reflect split-adjusted prices; set to false for unadjusted historical prices.")
    short_window: int | None = Field(default=None, description="The number of periods for the short-term exponential moving average in the MACD calculation. Defaults to 12 periods.")
    long_window: int | None = Field(default=None, description="The number of periods for the long-term exponential moving average in the MACD calculation. Defaults to 26 periods.")
    signal_window: int | None = Field(default=None, description="The number of periods for calculating the MACD signal line (exponential moving average of MACD values). Defaults to 9 periods.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="The price type to use in MACD calculations: open, high, low, or close. Defaults to close price.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp: ascending (oldest first) or descending (newest first). Defaults to descending.")
    limit: int | None = Field(default=None, description="Maximum number of MACD data points to return. Defaults to 10; maximum allowed is 5000.", le=5000)
class OptionsMacdRequest(StrictModel):
    """Calculate and retrieve Moving Average Convergence/Divergence (MACD) indicator values for an options contract over a specified time range. MACD helps identify trend direction and momentum changes."""
    path: OptionsMacdRequestPath
    query: OptionsMacdRequestQuery | None = None

# Operation: get_macd_indicator
class MacdRequestPath(StrictModel):
    stock_ticker: str = Field(default=..., validation_alias="stockTicker", serialization_alias="stockTicker", description="The stock ticker symbol to retrieve MACD data for (case-sensitive). For example, AAPL for Apple Inc.")
class MacdRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for aggregating price data. Defaults to daily candles. Choose from minute, hour, day, week, month, quarter, or year.")
    adjusted: bool | None = Field(default=None, description="Whether to adjust aggregates for stock splits and dividends. Defaults to true for adjusted data; set to false for unadjusted prices.")
    short_window: int | None = Field(default=None, description="The number of periods for the short-term exponential moving average. Defaults to 12 periods.")
    long_window: int | None = Field(default=None, description="The number of periods for the long-term exponential moving average. Defaults to 26 periods.")
    signal_window: int | None = Field(default=None, description="The number of periods for calculating the MACD signal line (exponential moving average of MACD). Defaults to 9 periods.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="The price type to use for MACD calculation: open, high, low, or close. Defaults to close price.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 10; maximum allowed is 5000.", le=5000)
class MacdRequest(StrictModel):
    """Retrieve Moving Average Convergence/Divergence (MACD) technical indicator data for a stock ticker over a specified time range. MACD helps identify trend direction and momentum changes."""
    path: MacdRequestPath
    query: MacdRequestQuery | None = None

# Operation: get_crypto_rsi
class CryptoRsiRequestPath(StrictModel):
    crypto_ticker: str = Field(default=..., validation_alias="cryptoTicker", serialization_alias="cryptoTicker", description="The cryptocurrency ticker symbol (e.g., X:BTCUSD for Bitcoin/USD pair).")
class CryptoRsiRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for aggregating price data. Defaults to daily aggregates. Choose from minute, hour, day, week, month, quarter, or year intervals.")
    window: int | None = Field(default=None, description="The number of periods used to calculate RSI. Defaults to 14 periods. A larger window smooths the indicator over a longer timeframe.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="The price type used in RSI calculation. Defaults to closing price. Options are open, high, low, or close prices.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp. Defaults to descending (most recent first). Choose ascending for oldest-first ordering.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 10, with a maximum of 5000 results per request.", le=5000)
class CryptoRsiRequest(StrictModel):
    """Retrieve the Relative Strength Index (RSI) indicator for a cryptocurrency ticker over a specified time range. RSI measures momentum on a scale of 0-100 to identify overbought or oversold conditions."""
    path: CryptoRsiRequestPath
    query: CryptoRsiRequestQuery | None = None

# Operation: get_forex_rsi
class ForexRsiRequestPath(StrictModel):
    fx_ticker: str = Field(default=..., validation_alias="fxTicker", serialization_alias="fxTicker", description="The forex ticker symbol to analyze, formatted as a currency pair (e.g., C:EURUSD for EUR/USD).")
class ForexRsiRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for each data point in the RSI calculation. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily data.")
    adjusted: bool | None = Field(default=None, description="Whether to adjust price data for corporate actions like splits before calculating RSI. When true (default), uses adjusted prices; set to false for unadjusted prices.")
    window: int | None = Field(default=None, description="The number of periods used in the RSI calculation window. Defaults to 14 periods, which is the standard RSI lookback period.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="Which price component to use for RSI calculation: open, high, low, or close. Defaults to close price, which is the most common choice.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending (most recent first).")
    limit: int | None = Field(default=None, description="Maximum number of RSI data points to return. Defaults to 10 results; maximum allowed is 5000.", le=5000)
class ForexRsiRequest(StrictModel):
    """Calculate the Relative Strength Index (RSI) for a forex currency pair over a specified time range. RSI is a momentum oscillator that measures the magnitude of recent price changes to evaluate overbought or oversold conditions."""
    path: ForexRsiRequestPath
    query: ForexRsiRequestQuery | None = None

# Operation: get_rsi_for_indices
class IndicesRsiRequestPath(StrictModel):
    indices_ticker: str = Field(default=..., validation_alias="indicesTicker", serialization_alias="indicesTicker", description="The ticker symbol for the indices (e.g., I:NDX for Nasdaq-100). Required to identify which index to analyze.")
class IndicesRsiRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for aggregating price data before calculating RSI. Defaults to daily candles. Choose from minute, hour, day, week, month, quarter, or year.")
    adjusted: bool | None = Field(default=None, description="Whether to adjust aggregates for stock splits before calculating RSI. Defaults to true (adjusted). Set to false to use unadjusted price data.")
    window: int | None = Field(default=None, description="The number of periods used in the RSI calculation window. Defaults to 14 periods. Larger values smooth the indicator; smaller values make it more responsive.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="Which price component to use for RSI calculation: open, high, low, or close. Defaults to close price. Determines which value from each candle feeds into the RSI formula.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending (most recent first).")
    limit: int | None = Field(default=None, description="Maximum number of RSI data points to return. Defaults to 10, with a maximum of 5000 results per request.", le=5000)
class IndicesRsiRequest(StrictModel):
    """Calculate the Relative Strength Index (RSI) for an indices ticker over a specified time range. RSI is a momentum oscillator that measures the magnitude of recent price changes to evaluate overbought or oversold conditions."""
    path: IndicesRsiRequestPath
    query: IndicesRsiRequestQuery | None = None

# Operation: get_options_rsi
class OptionsRsiRequestPath(StrictModel):
    options_ticker: str = Field(default=..., validation_alias="optionsTicker", serialization_alias="optionsTicker", description="The options ticker symbol in the format O:SYMBOL (e.g., O:SPY241220P00720000 for a specific options contract).")
class OptionsRsiRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for aggregating price data before calculating RSI. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregation.")
    adjusted: bool | None = Field(default=None, description="Whether to adjust price aggregates for stock splits before calculating RSI. When true (default), results reflect split-adjusted prices; set to false for unadjusted historical prices.")
    window: int | None = Field(default=None, description="The number of periods used in the RSI calculation window. Defaults to 14 periods; larger values produce smoother, less sensitive indicators while smaller values increase sensitivity to recent price changes.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="The price series to use for RSI calculation: open, high, low, or close. Defaults to close price, which is the most common choice for technical analysis.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp. Use 'asc' for oldest-first or 'desc' for newest-first (default).")
    limit: int | None = Field(default=None, description="Maximum number of RSI data points to return. Defaults to 10; maximum allowed is 5000.", le=5000)
class OptionsRsiRequest(StrictModel):
    """Calculate the Relative Strength Index (RSI) for an options ticker symbol over a specified time range. RSI is a momentum oscillator that measures the magnitude of recent price changes to evaluate overbought or oversold conditions."""
    path: OptionsRsiRequestPath
    query: OptionsRsiRequestQuery | None = None

# Operation: get_rsi_for_stock
class RsiRequestPath(StrictModel):
    stock_ticker: str = Field(default=..., validation_alias="stockTicker", serialization_alias="stockTicker", description="The stock ticker symbol in uppercase (e.g., AAPL for Apple Inc.). This is case-sensitive.")
class RsiRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for aggregating price data before calculating RSI. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregation.")
    adjusted: bool | None = Field(default=None, description="Whether to adjust price aggregates for stock splits before calculating RSI. Defaults to true (adjusted). Set to false to use unadjusted prices.")
    window: int | None = Field(default=None, description="The number of periods used in the RSI calculation window. Defaults to 14 periods, which is the standard RSI lookback period.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="Which price type to use for RSI calculation: open, high, low, or close. Defaults to close price, which is the most common choice.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending (most recent first).")
    limit: int | None = Field(default=None, description="Maximum number of RSI data points to return. Defaults to 10, with a maximum of 5000 results per request.", le=5000)
class RsiRequest(StrictModel):
    """Calculate the Relative Strength Index (RSI) momentum indicator for a stock ticker over a specified time range. RSI measures the magnitude of recent price changes to evaluate overbought or oversold conditions."""
    path: RsiRequestPath
    query: RsiRequestQuery | None = None

# Operation: get_crypto_simple_moving_average
class CryptoSmaRequestPath(StrictModel):
    crypto_ticker: str = Field(default=..., validation_alias="cryptoTicker", serialization_alias="cryptoTicker", description="The cryptocurrency ticker symbol to analyze (e.g., X:BTCUSD for Bitcoin in USD).")
class CryptoSmaRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for aggregating price data before calculating the moving average. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregates.")
    window: int | None = Field(default=None, description="The number of periods to include in the moving average calculation. For example, a window of 10 with daily aggregates produces a 10-day moving average. Defaults to 50 periods.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="The price type used in the SMA calculation: open, high, low, or close price. Defaults to using closing prices.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp: ascending (oldest first) or descending (newest first). Defaults to descending order.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Accepts values from 1 to 5000, with a default of 10 results.", le=5000)
class CryptoSmaRequest(StrictModel):
    """Calculate the simple moving average (SMA) for a cryptocurrency ticker over a specified time range. Returns SMA values computed from historical price data aggregated at your chosen interval."""
    path: CryptoSmaRequestPath
    query: CryptoSmaRequestQuery | None = None

# Operation: get_forex_simple_moving_average
class ForexSmaRequestPath(StrictModel):
    fx_ticker: str = Field(default=..., validation_alias="fxTicker", serialization_alias="fxTicker", description="The forex ticker symbol to analyze, formatted as a currency pair (e.g., C:EURUSD for EUR/USD).")
class ForexSmaRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for aggregating price data before calculating the moving average. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregates.")
    adjusted: bool | None = Field(default=None, description="Whether to adjust aggregates for corporate actions like splits. When true (default), results reflect adjusted prices; set to false for unadjusted historical prices.")
    window: int | None = Field(default=None, description="The number of periods to include in the moving average calculation. For example, a window of 10 with daily timespan produces a 10-day moving average. Defaults to 50 periods.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="The price type used in the SMA calculation: open, high, low, or close. Defaults to close price.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending order.")
    limit: int | None = Field(default=None, description="Maximum number of SMA values to return. Accepts 1 to 5000 results, with a default of 10.", le=5000)
class ForexSmaRequest(StrictModel):
    """Calculate the simple moving average (SMA) for a forex currency pair over a specified time range. Returns SMA values based on configurable window size, price series, and time aggregation."""
    path: ForexSmaRequestPath
    query: ForexSmaRequestQuery | None = None

# Operation: get_sma_for_indices
class IndicesSmaRequestPath(StrictModel):
    indices_ticker: str = Field(default=..., validation_alias="indicesTicker", serialization_alias="indicesTicker", description="The ticker symbol for the indices instrument (e.g., I:NDX for Nasdaq-100). Required to identify which index to calculate SMA for.")
class IndicesSmaRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for aggregating data before calculating SMA. Choose from minute, hour, day, week, month, quarter, or year. Defaults to daily aggregates.")
    adjusted: bool | None = Field(default=None, description="Whether to adjust aggregates for stock splits and dividends. Set to true (default) for split-adjusted results, or false for unadjusted data.")
    window: int | None = Field(default=None, description="The number of periods to include in the moving average calculation. For example, a window of 10 with daily timespan produces a 10-day SMA. Defaults to 50 periods.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="The price type to use for SMA calculation: open, high, low, or close. Defaults to close price.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp. Use 'asc' for oldest first or 'desc' for newest first. Defaults to descending (most recent first).")
    limit: int | None = Field(default=None, description="Maximum number of SMA data points to return. Accepts 1 to 5000 results. Defaults to 10.", le=5000)
class IndicesSmaRequest(StrictModel):
    """Retrieve the simple moving average (SMA) for an indices ticker symbol over a specified time range. Use this to analyze trend direction and momentum for index instruments like the Nasdaq-100."""
    path: IndicesSmaRequestPath
    query: IndicesSmaRequestQuery | None = None

# Operation: get_sma_for_options_ticker
class OptionsSmaRequestPath(StrictModel):
    options_ticker: str = Field(default=..., validation_alias="optionsTicker", serialization_alias="optionsTicker", description="The options ticker symbol to analyze (e.g., O:SPY241220P00720000 for a specific options contract).")
class OptionsSmaRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for aggregating price data before calculating the moving average. Choose from minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregates.")
    adjusted: bool | None = Field(default=None, description="Whether to adjust aggregates for stock splits and dividends. Set to true (default) for split-adjusted results, or false for unadjusted data.")
    window: int | None = Field(default=None, description="The number of periods to include in the moving average calculation. For example, a window of 10 with daily timespan produces a 10-day moving average. Defaults to 50 periods.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="The price type used in the SMA calculation: open, high, low, or close price. Defaults to close price.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp: ascending (oldest first) or descending (newest first). Defaults to descending.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Accepts values from 1 to 5000, with a default of 10.", le=5000)
class OptionsSmaRequest(StrictModel):
    """Calculate the simple moving average (SMA) for an options ticker symbol over a specified time range. Returns SMA values based on configurable aggregation periods, price series, and window sizes."""
    path: OptionsSmaRequestPath
    query: OptionsSmaRequestQuery | None = None

# Operation: get_simple_moving_average
class SmaRequestPath(StrictModel):
    stock_ticker: str = Field(default=..., validation_alias="stockTicker", serialization_alias="stockTicker", description="The stock ticker symbol to retrieve SMA data for (case-sensitive, e.g., AAPL for Apple Inc.).")
class SmaRequestQuery(StrictModel):
    timespan: Literal["minute", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="The time interval for aggregating price data before calculating the moving average. Options include minute, hour, day, week, month, quarter, or year intervals. Defaults to daily aggregates.")
    adjusted: bool | None = Field(default=None, description="Whether to adjust aggregate prices for stock splits and dividends. When true (default), prices are adjusted; set to false to use unadjusted prices.")
    window: int | None = Field(default=None, description="The number of periods to include in the moving average calculation. For example, a window of 10 with daily aggregates produces a 10-day moving average. Defaults to 50 periods.")
    series_type: Literal["open", "high", "low", "close"] | None = Field(default=None, description="The price type to use for SMA calculation: open, high, low, or close. Defaults to using closing prices.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp: ascending (oldest first) or descending (newest first). Defaults to descending order.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 10; maximum allowed is 5000.", le=5000)
class SmaRequest(StrictModel):
    """Calculate the simple moving average (SMA) for a stock ticker over a specified time range and aggregation period. Returns SMA values ordered by timestamp to track price trends."""
    path: SmaRequestPath
    query: SmaRequestQuery | None = None

# Operation: get_last_trade_for_crypto_pair
class LastTradeCryptoRequestPath(StrictModel):
    from_: str = Field(default=..., validation_alias="from", serialization_alias="from", description="The source cryptocurrency symbol (e.g., BTC for Bitcoin). Use the standard ticker symbol for the cryptocurrency you want to trade from.")
    to: str = Field(default=..., description="The target currency or cryptocurrency symbol (e.g., USD for US Dollar). Use the standard ticker symbol for the currency you want to trade to.")
class LastTradeCryptoRequest(StrictModel):
    """Retrieve the most recent trade tick for a specified cryptocurrency pair. Returns the latest executed trade data including price and timestamp for the given from/to currency combination."""
    path: LastTradeCryptoRequestPath

# Operation: get_last_quote_for_currency_pair
class LastQuoteCurrenciesRequestPath(StrictModel):
    from_: str = Field(default=..., validation_alias="from", serialization_alias="from", description="The source currency symbol (ISO 4217 code) for the currency pair conversion, such as AUD for Australian Dollar.")
    to: str = Field(default=..., description="The target currency symbol (ISO 4217 code) to convert into, such as USD for US Dollar.")
class LastQuoteCurrenciesRequest(StrictModel):
    """Retrieve the most recent exchange rate quote for a specified forex currency pair. Returns the latest tick data for converting between two currencies."""
    path: LastQuoteCurrenciesRequestPath

# Operation: get_crypto_daily_open_close
class GetCryptoOpenCloseRequestPath(StrictModel):
    from_: str = Field(default=..., validation_alias="from", serialization_alias="from", description="The base cryptocurrency symbol of the trading pair (e.g., BTC for Bitcoin).")
    to: str = Field(default=..., description="The quote currency symbol of the trading pair (e.g., USD for US Dollar).")
    date: str = Field(default=..., description="The date for which to retrieve open/close prices, formatted as YYYY-MM-DD.", json_schema_extra={'format': 'date'})
class GetCryptoOpenCloseRequestQuery(StrictModel):
    adjusted: bool | None = Field(default=None, description="Whether to return split-adjusted prices. Defaults to true for adjusted results; set to false to retrieve unadjusted prices.")
class GetCryptoOpenCloseRequest(StrictModel):
    """Retrieve the opening and closing prices for a cryptocurrency trading pair on a specific date. Prices are adjusted for splits by default."""
    path: GetCryptoOpenCloseRequestPath
    query: GetCryptoOpenCloseRequestQuery | None = None

# Operation: get_index_open_close
class GetIndicesOpenCloseRequestPath(StrictModel):
    indices_ticker: str = Field(default=..., validation_alias="indicesTicker", serialization_alias="indicesTicker", description="The ticker symbol of the index to query, prefixed with 'I:' (e.g., I:NDX for Nasdaq-100).")
    date: str = Field(default=..., description="The date for which to retrieve open/close data, formatted as YYYY-MM-DD (e.g., 2023-03-10).")
class GetIndicesOpenCloseRequest(StrictModel):
    """Retrieve the opening, closing, and after-hours prices for an index on a specific date. Useful for analyzing daily price movements and market hours performance."""
    path: GetIndicesOpenCloseRequestPath

# Operation: get_options_daily_open_close
class GetOptionsOpenCloseRequestPath(StrictModel):
    options_ticker: str = Field(default=..., validation_alias="optionsTicker", serialization_alias="optionsTicker", description="The options contract ticker symbol in the format O:UNDERLYING[EXPIRATION][TYPE][STRIKE] (e.g., O:SPY251219C00650000 for SPY call option expiring December 19, 2025 with $650 strike).")
    date: str = Field(default=..., description="The date for which to retrieve open/close data, formatted as YYYY-MM-DD (e.g., 2023-01-09).", json_schema_extra={'format': 'date'})
class GetOptionsOpenCloseRequestQuery(StrictModel):
    adjusted: bool | None = Field(default=None, description="Whether to adjust results for stock splits. Defaults to true (adjusted); set to false to retrieve unadjusted prices.")
class GetOptionsOpenCloseRequest(StrictModel):
    """Retrieve the open, close, and after-hours prices for a specific options contract on a given date."""
    path: GetOptionsOpenCloseRequestPath
    query: GetOptionsOpenCloseRequestQuery | None = None

# Operation: get_stock_daily_open_close
class GetStocksOpenCloseRequestPath(StrictModel):
    stocks_ticker: str = Field(default=..., validation_alias="stocksTicker", serialization_alias="stocksTicker", description="The stock ticker symbol in uppercase (e.g., AAPL for Apple Inc.). Must be case-sensitive and match the official exchange listing.")
    date: str = Field(default=..., description="The date for which to retrieve pricing data, formatted as YYYY-MM-DD (e.g., 2023-01-09).", json_schema_extra={'format': 'date'})
class GetStocksOpenCloseRequestQuery(StrictModel):
    adjusted: bool | None = Field(default=None, description="Whether to adjust prices for stock splits. When true (default), prices reflect split adjustments; set to false to retrieve unadjusted historical prices.")
class GetStocksOpenCloseRequest(StrictModel):
    """Retrieve the opening, closing, and after-hours prices for a stock on a specific date. Results are adjusted for stock splits by default."""
    path: GetStocksOpenCloseRequestPath
    query: GetStocksOpenCloseRequestQuery | None = None

# Operation: list_sec_filings_reference
class ListFilingsRequestQuery(StrictModel):
    has_xbrl: bool | None = Field(default=None, description="Filter filings by XBRL instance file availability. When true, returns only filings with XBRL data; when false, returns only filings without XBRL data; when omitted, returns all filings regardless of XBRL status.")
    entities_company_data_cik: str | None = Field(default=None, validation_alias="entities.company_data.cik", serialization_alias="entities.company_data.cik", description="Filter filings by the company's Central Index Key (CIK), a unique SEC identifier.")
    entities_company_data_ticker: str | None = Field(default=None, validation_alias="entities.company_data.ticker", serialization_alias="entities.company_data.ticker", description="Filter filings by the company's stock ticker symbol.")
    entities_company_data_sic: str | None = Field(default=None, validation_alias="entities.company_data.sic", serialization_alias="entities.company_data.sic", description="Filter filings by the company's Standard Industrial Classification (SIC) code.")
    period_of_report_date_gte: str | None = Field(default=None, validation_alias="period_of_report_date.gte", serialization_alias="period_of_report_date.gte", description="Return filings with a period of report date greater than or equal to this date. Use YYYYMMDD format (e.g., 20210101 for January 1, 2021).", pattern='^[0-9]{8}$')
    period_of_report_date_gt: str | None = Field(default=None, validation_alias="period_of_report_date.gt", serialization_alias="period_of_report_date.gt", description="Return filings with a period of report date strictly greater than this date. Use YYYYMMDD format (e.g., 20210101 for January 1, 2021).", pattern='^[0-9]{8}$')
    period_of_report_date_lte: str | None = Field(default=None, validation_alias="period_of_report_date.lte", serialization_alias="period_of_report_date.lte", description="Return filings with a period of report date less than or equal to this date. Use YYYYMMDD format (e.g., 20210101 for January 1, 2021).", pattern='^[0-9]{8}$')
    period_of_report_date_lt: str | None = Field(default=None, validation_alias="period_of_report_date.lt", serialization_alias="period_of_report_date.lt", description="Return filings with a period of report date strictly less than this date. Use YYYYMMDD format (e.g., 20210101 for January 1, 2021).", pattern='^[0-9]{8}$')
    entities_company_data_name_search: str | None = Field(default=None, validation_alias="entities.company_data.name.search", serialization_alias="entities.company_data.name.search", description="Search filings by company name using text matching.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort results in ascending or descending order based on the selected sort field.")
    limit: int | None = Field(default=None, description="Maximum number of filings to return per request. Defaults to 10; maximum allowed is 1000.", ge=1, le=1000)
    sort: Literal["filing_date", "period_of_report_date"] | None = Field(default=None, description="Field to sort results by. Choose filing_date for the date the filing was submitted, or period_of_report_date for the reporting period end date. Defaults to filing_date.")
class ListFilingsRequest(StrictModel):
    """Retrieve SEC filings with flexible filtering by company identifiers, reporting dates, and XBRL availability. Results can be sorted and paginated for efficient data retrieval."""
    query: ListFilingsRequestQuery | None = None

# Operation: get_filing
class GetFilingRequestPath(StrictModel):
    filing_id: str = Field(default=..., description="The unique identifier for the SEC filing to retrieve. This ID corresponds to a specific filing record in the SEC database.")
class GetFilingRequest(StrictModel):
    """Retrieve a specific SEC filing document by its unique filing identifier. Returns detailed filing information from the Securities and Exchange Commission database."""
    path: GetFilingRequestPath

# Operation: list_filing_files
class ListFilingFilesRequestPath(StrictModel):
    filing_id: str = Field(default=..., description="The unique identifier of the SEC filing for which to retrieve associated files.")
class ListFilingFilesRequestQuery(StrictModel):
    sequence_gte: int | None = Field(default=None, validation_alias="sequence.gte", serialization_alias="sequence.gte", description="Filter results to include only files with a sequence number greater than or equal to this value. Sequence numbers range from 1 to 999.", json_schema_extra={'format': 'int64'})
    sequence_gt: int | None = Field(default=None, validation_alias="sequence.gt", serialization_alias="sequence.gt", description="Filter results to include only files with a sequence number strictly greater than this value. Sequence numbers range from 1 to 999.", json_schema_extra={'format': 'int64'})
    sequence_lte: int | None = Field(default=None, validation_alias="sequence.lte", serialization_alias="sequence.lte", description="Filter results to include only files with a sequence number less than or equal to this value. Sequence numbers range from 1 to 999.", json_schema_extra={'format': 'int64'})
    sequence_lt: int | None = Field(default=None, validation_alias="sequence.lt", serialization_alias="sequence.lt", description="Filter results to include only files with a sequence number strictly less than this value. Sequence numbers range from 1 to 999.", json_schema_extra={'format': 'int64'})
    filename_gte: str | None = Field(default=None, validation_alias="filename.gte", serialization_alias="filename.gte", description="Filter results to include only files with a filename greater than or equal to this value (lexicographic comparison).")
    filename_gt: str | None = Field(default=None, validation_alias="filename.gt", serialization_alias="filename.gt", description="Filter results to include only files with a filename strictly greater than this value (lexicographic comparison).")
    filename_lte: str | None = Field(default=None, validation_alias="filename.lte", serialization_alias="filename.lte", description="Filter results to include only files with a filename less than or equal to this value (lexicographic comparison).")
    filename_lt: str | None = Field(default=None, validation_alias="filename.lt", serialization_alias="filename.lt", description="Filter results to include only files with a filename strictly less than this value (lexicographic comparison).")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for results: 'asc' for ascending or 'desc' for descending order based on the selected sort field.")
    limit: int | None = Field(default=None, description="Maximum number of results to return per request. Defaults to 10 if not specified; maximum allowed is 1000.", ge=1, le=1000)
    sort: Literal["sequence", "filename"] | None = Field(default=None, description="Field to sort results by: 'sequence' (default) sorts by file sequence number, or 'filename' sorts alphabetically by filename.")
class ListFilingFilesRequest(StrictModel):
    """Retrieve a list of files associated with a specific SEC filing. Results can be filtered by sequence number or filename, and sorted by either field in ascending or descending order."""
    path: ListFilingFilesRequestPath
    query: ListFilingFilesRequestQuery | None = None

# Operation: get_sec_filing_file
class GetFilingFileRequestPath(StrictModel):
    filing_id: str = Field(default=..., description="The unique identifier of the SEC filing. This ID specifies which filing submission to retrieve the file from.")
    file_id: str = Field(default=..., description="The unique identifier of the specific file within the filing. This ID pinpoints the exact document or exhibit to retrieve (e.g., '1' for the first file).")
class GetFilingFileRequest(StrictModel):
    """Retrieve a specific file from an SEC filing by its filing ID and file ID. Use this to access individual documents or exhibits within a complete SEC filing submission."""
    path: GetFilingFileRequestPath

# Operation: list_related_companies
class GetRelatedCompaniesRequestPath(StrictModel):
    ticker: str = Field(default=..., description="The stock ticker symbol to find related companies for (e.g., AAPL for Apple Inc.)")
class GetRelatedCompaniesRequest(StrictModel):
    """Retrieve a list of company tickers related to a given ticker symbol, identified through analysis of news coverage and stock return patterns."""
    path: GetRelatedCompaniesRequestPath

# Operation: get_grouped_crypto_aggregates
class GetGroupedCryptoAggregatesRequestPath(StrictModel):
    date: str = Field(default=..., description="The date for which to retrieve cryptocurrency market aggregates, formatted as YYYY-MM-DD (e.g., 2025-11-03).")
class GetGroupedCryptoAggregatesRequestQuery(StrictModel):
    adjusted: bool | None = Field(default=None, description="Whether to adjust results for splits. Set to true (default) for split-adjusted prices, or false to receive unadjusted data.")
class GetGroupedCryptoAggregatesRequest(StrictModel):
    """Retrieve daily OHLC (open, high, low, close) price aggregates for the entire cryptocurrency market on a specified date. Results are adjusted for splits by default."""
    path: GetGroupedCryptoAggregatesRequestPath
    query: GetGroupedCryptoAggregatesRequestQuery | None = None

# Operation: get_grouped_forex_aggregates
class GetGroupedForexAggregatesRequestPath(StrictModel):
    date: str = Field(default=..., description="The date for which to retrieve forex market aggregates, formatted as YYYY-MM-DD (e.g., 2025-11-03).")
class GetGroupedForexAggregatesRequestQuery(StrictModel):
    adjusted: bool | None = Field(default=None, description="Whether to return split-adjusted results. Defaults to true for adjusted data; set to false to retrieve unadjusted values.")
class GetGroupedForexAggregatesRequest(StrictModel):
    """Retrieve daily OHLC (open, high, low, close) aggregated data for all forex currency pairs on a specified date. Results are adjusted for splits by default."""
    path: GetGroupedForexAggregatesRequestPath
    query: GetGroupedForexAggregatesRequestQuery | None = None

# Operation: get_grouped_stocks_aggregates
class GetGroupedStocksAggregatesRequestPath(StrictModel):
    date: str = Field(default=..., description="The date for which to retrieve market aggregates, formatted as YYYY-MM-DD (e.g., 2025-11-03).")
class GetGroupedStocksAggregatesRequestQuery(StrictModel):
    adjusted: bool | None = Field(default=None, description="Whether to return split-adjusted prices. Defaults to true; set to false to retrieve unadjusted data.")
    include_otc: bool | None = Field(default=None, description="Whether to include over-the-counter (OTC) securities in the results. Defaults to false.")
class GetGroupedStocksAggregatesRequest(StrictModel):
    """Retrieve daily OHLC (open, high, low, close) aggregate data for the entire US equities market on a specified date. Results are adjusted for splits by default."""
    path: GetGroupedStocksAggregatesRequestPath
    query: GetGroupedStocksAggregatesRequestQuery | None = None

# Operation: get_previous_crypto_aggregates
class GetPreviousCryptoAggregatesRequestPath(StrictModel):
    crypto_ticker: str = Field(default=..., validation_alias="cryptoTicker", serialization_alias="cryptoTicker", description="The ticker symbol representing the cryptocurrency pair (e.g., X:BTCUSD for Bitcoin to US Dollar).")
class GetPreviousCryptoAggregatesRequestQuery(StrictModel):
    adjusted: bool | None = Field(default=None, description="Whether to return split-adjusted results. Defaults to true for adjusted data; set to false to retrieve unadjusted historical prices.")
class GetPreviousCryptoAggregatesRequest(StrictModel):
    """Retrieve the previous trading day's OHLC (open, high, low, close) data for a specified cryptocurrency pair. Use this to analyze the prior day's price movement and market range."""
    path: GetPreviousCryptoAggregatesRequestPath
    query: GetPreviousCryptoAggregatesRequestQuery | None = None

# Operation: get_crypto_aggregates
class GetCryptoAggregatesRequestPath(StrictModel):
    crypto_ticker: str = Field(default=..., validation_alias="cryptoTicker", serialization_alias="cryptoTicker", description="The cryptocurrency pair ticker symbol (e.g., X:BTCUSD for Bitcoin/USD).")
    multiplier: int = Field(default=..., description="The multiplier for the timespan unit. Must be a positive integer that scales the timespan (e.g., multiplier=5 with timespan='minute' produces 5-minute bars).")
    timespan: Literal["second", "minute", "hour", "day", "week", "month", "quarter", "year"] = Field(default=..., description="The unit of time for each aggregate bar. Choose from: second, minute, hour, day, week, month, quarter, or year.")
    from_: str = Field(default=..., validation_alias="from", serialization_alias="from", description="The start of the time window for aggregates. Provide either a date in YYYY-MM-DD format or a millisecond Unix timestamp.")
    to: str = Field(default=..., description="The end of the time window for aggregates. Provide either a date in YYYY-MM-DD format or a millisecond Unix timestamp.")
class GetCryptoAggregatesRequestQuery(StrictModel):
    adjusted: bool | None = Field(default=None, description="Whether to adjust results for stock splits. Defaults to true (adjusted). Set to false to retrieve unadjusted data.")
    sort: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp. Use 'asc' for oldest-first or 'desc' for newest-first ordering.")
    limit: int | None = Field(default=None, description="Maximum number of base aggregates to query for creating results. Accepts values up to 50,000; defaults to 5,000 if not specified.")
class GetCryptoAggregatesRequest(StrictModel):
    """Retrieve aggregate bars (OHLCV data) for a cryptocurrency pair over a specified date range with customizable time window sizes. For example, use multiplier=5 with timespan='minute' to get 5-minute bars."""
    path: GetCryptoAggregatesRequestPath
    query: GetCryptoAggregatesRequestQuery | None = None

# Operation: get_previous_forex_close
class GetPreviousForexAggregatesRequestPath(StrictModel):
    forex_ticker: str = Field(default=..., validation_alias="forexTicker", serialization_alias="forexTicker", description="The forex ticker symbol representing a currency pair (e.g., C:EURUSD for Euro/US Dollar).")
class GetPreviousForexAggregatesRequestQuery(StrictModel):
    adjusted: bool | None = Field(default=None, description="Whether to return split-adjusted results. Defaults to true for adjusted data; set to false to retrieve unadjusted historical prices.")
class GetPreviousForexAggregatesRequest(StrictModel):
    """Retrieve the previous trading day's OHLC (open, high, low, close) data for a specified forex currency pair. Useful for analyzing recent price action and market trends."""
    path: GetPreviousForexAggregatesRequestPath
    query: GetPreviousForexAggregatesRequestQuery | None = None

# Operation: get_forex_aggregates
class GetForexAggregatesRequestPath(StrictModel):
    forex_ticker: str = Field(default=..., validation_alias="forexTicker", serialization_alias="forexTicker", description="The forex ticker symbol for the currency pair (e.g., C:EURUSD for EUR/USD).")
    multiplier: int = Field(default=..., description="The multiplier for the timespan unit. Must be a positive integer that scales the timespan (e.g., multiplier=5 with timespan='minute' returns 5-minute bars).")
    timespan: Literal["second", "minute", "hour", "day", "week", "month", "quarter", "year"] = Field(default=..., description="The unit of time for each aggregate bar. Choose from: second, minute, hour, day, week, month, quarter, or year.")
    from_: str = Field(default=..., validation_alias="from", serialization_alias="from", description="The start of the time window for aggregates. Provide either a date in YYYY-MM-DD format or a millisecond Unix timestamp.")
    to: str = Field(default=..., description="The end of the time window for aggregates. Provide either a date in YYYY-MM-DD format or a millisecond Unix timestamp.")
class GetForexAggregatesRequestQuery(StrictModel):
    adjusted: bool | None = Field(default=None, description="Whether to adjust results for stock splits. Defaults to true (adjusted). Set to false to retrieve unadjusted data.")
    sort: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp. Use 'asc' for oldest-first or 'desc' for newest-first ordering.")
    limit: int | None = Field(default=None, description="Maximum number of base aggregates to query for creating results. Accepts values up to 50,000; defaults to 5,000 if not specified.")
class GetForexAggregatesRequest(StrictModel):
    """Retrieve aggregate (OHLCV) bars for a forex currency pair over a specified date range with customizable time window sizes. For example, use multiplier=5 with timespan='minute' to get 5-minute bars."""
    path: GetForexAggregatesRequestPath
    query: GetForexAggregatesRequestQuery | None = None

# Operation: get_previous_index_aggregates
class GetPreviousIndicesAggregatesRequestPath(StrictModel):
    indices_ticker: str = Field(default=..., validation_alias="indicesTicker", serialization_alias="indicesTicker", description="The ticker symbol of the index (e.g., I:NDX for Nasdaq-100). Use the index ticker in the format specified by your data provider.")
class GetPreviousIndicesAggregatesRequest(StrictModel):
    """Retrieve the previous trading day's OHLC (open, high, low, close) aggregate data for a specified index. Useful for comparing current performance against the prior day's closing values."""
    path: GetPreviousIndicesAggregatesRequestPath

# Operation: get_indices_aggregates
class GetIndicesAggregatesRequestPath(StrictModel):
    indices_ticker: str = Field(default=..., validation_alias="indicesTicker", serialization_alias="indicesTicker", description="The ticker symbol of the index (e.g., I:NDX for Nasdaq-100).")
    multiplier: int = Field(default=..., description="The multiplier for the timespan unit. Combined with timespan to define the aggregate window size (e.g., multiplier=5 with timespan='minute' creates 5-minute bars).")
    timespan: Literal["second", "minute", "hour", "day", "week", "month", "quarter", "year"] = Field(default=..., description="The unit of time for the aggregate window. Choose from: second, minute, hour, day, week, month, quarter, or year.")
    from_: str = Field(default=..., validation_alias="from", serialization_alias="from", description="The start of the aggregate time window. Provide either a date in YYYY-MM-DD format or a millisecond Unix timestamp.")
    to: str = Field(default=..., description="The end of the aggregate time window. Provide either a date in YYYY-MM-DD format or a millisecond Unix timestamp.")
class GetIndicesAggregatesRequestQuery(StrictModel):
    sort: Literal["asc", "desc"] | None = Field(default=None, description="Sort results by timestamp in ascending order (oldest first) or descending order (newest first). Defaults to ascending if not specified.")
    limit: int | None = Field(default=None, description="Maximum number of base aggregates to query for creating results. Accepts values up to 50,000; defaults to 5,000 if not specified.")
class GetIndicesAggregatesRequest(StrictModel):
    """Retrieve aggregate (OHLCV) bars for an index over a specified date range with customizable time window sizes. For example, use multiplier=5 with timespan='minute' to get 5-minute bars."""
    path: GetIndicesAggregatesRequestPath
    query: GetIndicesAggregatesRequestQuery | None = None

# Operation: get_previous_close_for_options_contract
class GetPreviousOptionsAggregatesRequestPath(StrictModel):
    options_ticker: str = Field(default=..., validation_alias="optionsTicker", serialization_alias="optionsTicker", description="The options contract ticker symbol in the format O:{underlying}{expiration}{type}{strike} (e.g., O:SPY251219C00650000 for SPY call option expiring December 19, 2025 at $650 strike).")
class GetPreviousOptionsAggregatesRequestQuery(StrictModel):
    adjusted: bool | None = Field(default=None, description="Whether to return split-adjusted results. Defaults to true for adjusted data; set to false to retrieve unadjusted historical prices.")
class GetPreviousOptionsAggregatesRequest(StrictModel):
    """Retrieve the previous trading day's OHLC (open, high, low, close) data for a specified options contract. Results are adjusted for splits by default."""
    path: GetPreviousOptionsAggregatesRequestPath
    query: GetPreviousOptionsAggregatesRequestQuery | None = None

# Operation: get_options_aggregates
class GetOptionsAggregatesRequestPath(StrictModel):
    options_ticker: str = Field(default=..., validation_alias="optionsTicker", serialization_alias="optionsTicker", description="The options contract ticker symbol in the format O:UNDERLYING[EXPIRATION][TYPE][STRIKE] (e.g., O:SPY251219C00650000 for a SPY call option expiring December 19, 2025 with a $650 strike).")
    multiplier: int = Field(default=..., description="The multiplier for the timespan unit. Combined with timespan, this defines the bar size (e.g., multiplier=5 with timespan='minute' produces 5-minute bars). Must be a positive integer.")
    timespan: Literal["second", "minute", "hour", "day", "week", "month", "quarter", "year"] = Field(default=..., description="The unit of time for each aggregate bar. Choose from: second, minute, hour, day, week, month, quarter, or year.")
    from_: str = Field(default=..., validation_alias="from", serialization_alias="from", description="The start of the time window for aggregates. Provide either a date in YYYY-MM-DD format or a millisecond Unix timestamp.")
    to: str = Field(default=..., description="The end of the time window for aggregates. Provide either a date in YYYY-MM-DD format or a millisecond Unix timestamp. Must be after the 'from' date.")
class GetOptionsAggregatesRequestQuery(StrictModel):
    adjusted: bool | None = Field(default=None, description="Whether to adjust results for corporate actions like splits. Defaults to true (adjusted). Set to false to retrieve unadjusted data.")
    sort: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp. Use 'asc' for oldest-first or 'desc' for newest-first ordering.")
    limit: int | None = Field(default=None, description="Maximum number of base aggregates to query when constructing the result set. Accepts values up to 50,000; defaults to 5,000. Higher limits may improve accuracy for custom timespan aggregations.")
class GetOptionsAggregatesRequest(StrictModel):
    """Retrieve aggregate bars for an options contract over a specified date range in custom time window sizes. For example, with a 5-minute timespan, the API returns 5-minute OHLCV bars."""
    path: GetOptionsAggregatesRequestPath
    query: GetOptionsAggregatesRequestQuery | None = None

# Operation: get_previous_day_stock_ohlc
class GetPreviousStocksAggregatesRequestPath(StrictModel):
    stocks_ticker: str = Field(default=..., validation_alias="stocksTicker", serialization_alias="stocksTicker", description="The stock ticker symbol in uppercase (e.g., AAPL for Apple Inc.). Must be an exact, case-sensitive match.")
class GetPreviousStocksAggregatesRequestQuery(StrictModel):
    adjusted: bool | None = Field(default=None, description="Whether to adjust results for stock splits. Defaults to true; set to false to retrieve unadjusted prices.")
class GetPreviousStocksAggregatesRequest(StrictModel):
    """Retrieve the previous trading day's open, high, low, and close (OHLC) prices for a specified stock ticker. Results are adjusted for stock splits by default."""
    path: GetPreviousStocksAggregatesRequestPath
    query: GetPreviousStocksAggregatesRequestQuery | None = None

# Operation: get_stock_aggregates_by_range
class GetStocksAggregatesRequestPath(StrictModel):
    stocks_ticker: str = Field(default=..., validation_alias="stocksTicker", serialization_alias="stocksTicker", description="The stock ticker symbol in uppercase (e.g., AAPL for Apple Inc.). Must be an exact, case-sensitive match.")
    multiplier: int = Field(default=..., description="The multiplier for the timespan unit. Combined with timespan to define the bar size (e.g., multiplier=5 with timespan='minute' produces 5-minute bars). Must be a positive integer.")
    timespan: Literal["second", "minute", "hour", "day", "week", "month", "quarter", "year"] = Field(default=..., description="The unit of time for each aggregate bar. Valid options are: second, minute, hour, day, week, month, quarter, or year.")
    from_: str = Field(default=..., validation_alias="from", serialization_alias="from", description="The start of the time window for aggregates. Accepts either a date in YYYY-MM-DD format or a millisecond Unix timestamp.")
    to: str = Field(default=..., description="The end of the time window for aggregates. Accepts either a date in YYYY-MM-DD format or a millisecond Unix timestamp. Must be on or after the 'from' date.")
class GetStocksAggregatesRequestQuery(StrictModel):
    adjusted: bool | None = Field(default=None, description="Whether to adjust results for stock splits. Defaults to true (adjusted). Set to false to retrieve unadjusted data.")
    sort: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results by timestamp. Use 'asc' for ascending order (oldest first) or 'desc' for descending order (newest first).")
    limit: int | None = Field(default=None, description="Maximum number of base aggregates to query when building results. Accepts values from 1 to 50,000; defaults to 5,000 if not specified.")
class GetStocksAggregatesRequest(StrictModel):
    """Retrieve aggregate (OHLCV) bars for a stock over a specified date range with customizable time window sizes. For example, use multiplier=5 with timespan='minute' to get 5-minute bars."""
    path: GetStocksAggregatesRequestPath
    query: GetStocksAggregatesRequestQuery | None = None

# Operation: get_last_quote
class LastQuoteRequestPath(StrictModel):
    stocks_ticker: str = Field(default=..., validation_alias="stocksTicker", serialization_alias="stocksTicker", description="The stock ticker symbol in case-sensitive format (e.g., AAPL for Apple Inc.).")
class LastQuoteRequest(StrictModel):
    """Retrieve the most recent NBBO (National Best Bid and Offer) quote for a specified stock ticker symbol."""
    path: LastQuoteRequestPath

# Operation: get_last_trade_for_options_contract
class LastTradeOptionsRequestPath(StrictModel):
    options_ticker: str = Field(default=..., validation_alias="optionsTicker", serialization_alias="optionsTicker", description="The options contract ticker symbol in the format O:{underlying_symbol}{expiration_date}{contract_type}{strike_price} (e.g., O:TSLA210903C00700000 for a Tesla call option expiring September 3, 2021 with a $700 strike).")
class LastTradeOptionsRequest(StrictModel):
    """Retrieve the most recent trade execution for a specified options contract. Returns trade details including price, size, and timestamp for the latest transaction."""
    path: LastTradeOptionsRequestPath

# Operation: get_last_trade
class LastTradeRequestPath(StrictModel):
    stocks_ticker: str = Field(default=..., validation_alias="stocksTicker", serialization_alias="stocksTicker", description="The stock ticker symbol in uppercase (e.g., AAPL for Apple Inc.). Must be a valid, case-sensitive ticker symbol.")
class LastTradeRequest(StrictModel):
    """Retrieve the most recent trade execution for a specified stock ticker symbol. Returns the latest trade data including price, size, and timestamp."""
    path: LastTradeRequestPath

# Operation: list_news_for_ticker
class ListNewsRequestQuery(StrictModel):
    published_utc: str | None = Field(default=None, description="Filter results to articles published on, before, or after a specific date. Use ISO 8601 format for the date specification.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for results: ascending (oldest first) or descending (newest first). Defaults to descending when used with the sort field.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Must be between 1 and 1000 articles; defaults to 10 if not specified.", ge=1, le=1000)
    sort: Literal["published_utc"] | None = Field(default=None, description="Field to sort results by. Currently supports sorting by publication date (published_utc), which is the default ordering.")
class ListNewsRequest(StrictModel):
    """Retrieve the most recent news articles for a stock ticker symbol, including article summaries and links to original sources. Results can be filtered by publication date and sorted by recency."""
    query: ListNewsRequestQuery | None = None

# Operation: get_crypto_ticker_snapshot
class GetCryptoSnapshotTickerRequestPath(StrictModel):
    ticker: str = Field(default=..., description="The cryptocurrency ticker symbol to retrieve snapshot data for, formatted as an exchange prefix and currency pair (e.g., X:BTCUSD for Bitcoin in USD).")
class GetCryptoSnapshotTickerRequest(StrictModel):
    """Retrieve real-time and aggregate market data for a cryptocurrency ticker, including current minute and day aggregates, previous day comparison, and the latest trade and quote information. Data is refreshed as exchange data arrives and resets daily at 12am EST."""
    path: GetCryptoSnapshotTickerRequestPath

# Operation: list_crypto_gainers_or_losers
class GetCryptoSnapshotDirectionRequestPath(StrictModel):
    direction: Literal["gainers", "losers"] = Field(default=..., description="Specify whether to return top gainers or top losers. Use 'gainers' for tickers with the highest positive percentage change, or 'losers' for tickers with the highest negative percentage change since the previous day's close.")
class GetCryptoSnapshotDirectionRequest(StrictModel):
    """Retrieve the top 20 cryptocurrency gainers or losers by percentage change since the previous day's close. Snapshot data resets daily at 12am EST and populates as exchange data arrives."""
    path: GetCryptoSnapshotDirectionRequestPath

# Operation: get_forex_ticker_snapshot
class GetForexSnapshotTickerRequestPath(StrictModel):
    ticker: str = Field(default=..., description="The forex currency pair ticker symbol (e.g., C:EURUSD for Euro/US Dollar). Use the format C: prefix followed by the three-letter currency codes.")
class GetForexSnapshotTickerRequest(StrictModel):
    """Retrieve real-time forex market data for a currency pair, including current minute and day aggregates, previous day comparison, and the latest trade and quote information. Data is refreshed as exchange data arrives and resets daily at 12am EST."""
    path: GetForexSnapshotTickerRequestPath

# Operation: list_forex_gainers_or_losers
class GetForexSnapshotDirectionRequestPath(StrictModel):
    direction: Literal["gainers", "losers"] = Field(default=..., description="Specify whether to return the top gainers or top losers. Use 'gainers' for pairs with the highest positive percentage change, or 'losers' for pairs with the highest negative percentage change since the previous day's close.")
class GetForexSnapshotDirectionRequest(StrictModel):
    """Retrieve the top 20 forex currency pairs ranked by daily percentage change. Returns either the biggest gainers or losers since the previous day's close, with snapshot data refreshed daily at 12am EST."""
    path: GetForexSnapshotDirectionRequestPath

# Operation: list_stock_tickers_snapshot
class GetStocksSnapshotTickersRequestQuery(StrictModel):
    include_otc: bool | None = Field(default=None, description="Set to true to include over-the-counter (OTC) securities in the results; defaults to false to return only exchange-listed stocks.")
class GetStocksSnapshotTickersRequest(StrictModel):
    """Retrieve real-time market data snapshot for all traded stock symbols. Data is refreshed continuously from exchanges starting around 4am EST daily, with the previous day's data cleared at 3:30am EST."""
    query: GetStocksSnapshotTickersRequestQuery | None = None

# Operation: get_stock_snapshot_by_ticker
class GetStocksSnapshotTickerRequestPath(StrictModel):
    stocks_ticker: str = Field(default=..., validation_alias="stocksTicker", serialization_alias="stocksTicker", description="The stock ticker symbol in uppercase (e.g., AAPL for Apple Inc.). Must match the exact case-sensitive symbol used by the exchange.")
class GetStocksSnapshotTickerRequest(StrictModel):
    """Retrieve real-time market data snapshot for a specific stock ticker symbol. Data is refreshed as exchange data arrives, typically starting at 4am EST after the 3:30am EST daily reset."""
    path: GetStocksSnapshotTickerRequestPath

# Operation: list_stocks_by_direction
class GetStocksSnapshotDirectionRequestPath(StrictModel):
    direction: Literal["gainers", "losers"] = Field(default=..., description="Specify whether to return top gainers or top losers ranked by percentage price change since the previous close.")
class GetStocksSnapshotDirectionRequestQuery(StrictModel):
    include_otc: bool | None = Field(default=None, description="Set to true to include over-the-counter (OTC) securities in the results; defaults to false to exclude OTC securities.")
class GetStocksSnapshotDirectionRequest(StrictModel):
    """Retrieve the top 20 stocks with the highest percentage gains or losses since the previous day's close. Results include only tickers with trading volume of 10,000 or more and are updated throughout the trading day."""
    path: GetStocksSnapshotDirectionRequestPath
    query: GetStocksSnapshotDirectionRequestQuery | None = None

# Operation: get_nbbo_quotes_for_date
class DeprecatedGetHistoricStocksQuotesRequestPath(StrictModel):
    ticker: str = Field(default=..., description="The stock ticker symbol (e.g., AAPL) for which to retrieve quotes.")
    date: str = Field(default=..., description="The date for which to retrieve quotes, specified in YYYY-MM-DD format (e.g., 2020-10-14).", json_schema_extra={'format': 'date'})
class DeprecatedGetHistoricStocksQuotesRequestQuery(StrictModel):
    timestamp_limit: int | None = Field(default=None, validation_alias="timestampLimit", serialization_alias="timestampLimit", description="Optional maximum timestamp threshold; only quotes at or before this timestamp will be included in results.")
    reverse: bool | None = Field(default=None, description="Optional flag to reverse the sort order of results; when true, results are returned in descending order.")
    limit: int | None = Field(default=None, description="Optional limit on the number of quotes returned in the response, with a maximum of 50,000 and default of 5,000.")
class DeprecatedGetHistoricStocksQuotesRequest(StrictModel):
    """Retrieve National Best Bid and Offer (NBBO) quotes for a specific stock ticker on a given date. Returns intraday quote data with optional filtering and ordering."""
    path: DeprecatedGetHistoricStocksQuotesRequestPath
    query: DeprecatedGetHistoricStocksQuotesRequestQuery | None = None

# Operation: get_fx_quotes
class QuotesFxRequestPath(StrictModel):
    fx_ticker: str = Field(default=..., validation_alias="fxTicker", serialization_alias="fxTicker", description="The FX ticker symbol to retrieve quotes for, formatted as a currency pair (e.g., C:EUR-USD).")
class QuotesFxRequestQuery(StrictModel):
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results: ascending or descending. Defaults to descending order.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Must be between 1 and 50,000; defaults to 1,000.", ge=1, le=50000)
    sort: Literal["timestamp"] | None = Field(default=None, description="Field to sort results by. Currently supports sorting by timestamp only.")
class QuotesFxRequest(StrictModel):
    """Retrieve best bid-offer (BBO) quotes for a foreign exchange ticker symbol. Returns quote data sorted by timestamp in descending order by default, with configurable pagination and ordering."""
    path: QuotesFxRequestPath
    query: QuotesFxRequestQuery | None = None

# Operation: list_options_quotes
class QuotesOptionsRequestPath(StrictModel):
    options_ticker: str = Field(default=..., validation_alias="optionsTicker", serialization_alias="optionsTicker", description="The options ticker symbol to retrieve quotes for, formatted as an OCC options symbol (e.g., O:SPY241220P00720000 for a SPY put option).")
class QuotesOptionsRequestQuery(StrictModel):
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results based on the sort field. Defaults to descending order (newest first).")
    limit: int | None = Field(default=None, description="Maximum number of quote records to return in the response. Accepts values from 1 to 50,000, with a default of 1,000.", ge=1, le=50000)
    sort: Literal["timestamp"] | None = Field(default=None, description="Field to sort results by. Currently supports sorting by timestamp only.")
class QuotesOptionsRequest(StrictModel):
    """Retrieve historical quote data for an options contract ticker symbol, with configurable sorting and pagination to handle large result sets."""
    path: QuotesOptionsRequestPath
    query: QuotesOptionsRequestQuery | None = None

# Operation: get_stock_quotes
class QuotesRequestPath(StrictModel):
    stock_ticker: str = Field(default=..., validation_alias="stockTicker", serialization_alias="stockTicker", description="The stock ticker symbol to retrieve quotes for (case-sensitive). For example, AAPL for Apple Inc.")
class QuotesRequestQuery(StrictModel):
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results based on the sort field. Defaults to descending order.")
    limit: int | None = Field(default=None, description="Maximum number of quote records to return. Accepts values from 1 to 50,000, with a default of 1,000.", ge=1, le=50000)
    sort: Literal["timestamp"] | None = Field(default=None, description="Field to sort results by. Currently supports sorting by timestamp.")
class QuotesRequest(StrictModel):
    """Retrieve National Best Bid and Offer (NBBO) quotes for a stock ticker symbol. Returns quote data sorted and limited according to specified parameters."""
    path: QuotesRequestPath
    query: QuotesRequestQuery | None = None

# Operation: list_conditions
class ListConditionsRequestQuery(StrictModel):
    data_type: Literal["trade", "bbo", "nbbo"] | None = Field(default=None, description="Filter results to conditions associated with a specific data type: trade data, best bid-offer quotes, or national best bid-offer quotes.")
    id_: int | None = Field(default=None, validation_alias="id", serialization_alias="id", description="Filter results to a specific condition by its numeric identifier.")
    sip: Literal["CTA", "UTP", "OPRA"] | None = Field(default=None, description="Filter results to conditions that have a mapping for a specific SIP (Consolidated Tape Association, Unlisted Trading Privileges, or Options Price Reporting Authority).")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort results in ascending or descending order based on the selected sort field.")
    limit: int | None = Field(default=None, description="Limit the number of results returned; defaults to 10 with a maximum of 1000 results per request.", ge=1, le=1000)
    sort: Literal["asset_class", "id", "type", "name", "data_types", "legacy"] | None = Field(default=None, description="Select the field to sort by: asset class, condition ID, type, name, supported data types, or legacy status. Defaults to asset class.")
class ListConditionsRequest(StrictModel):
    """Retrieve all market conditions used by Massive, with optional filtering by data type, SIP, or condition ID. Results can be sorted and paginated for efficient data retrieval."""
    query: ListConditionsRequestQuery | None = None

# Operation: list_dividends
class ListDividendsRequestQuery(StrictModel):
    record_date: str | None = Field(default=None, description="Filter dividends by the record date (the date on which shareholders must be registered to receive the dividend). Use YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    declaration_date: str | None = Field(default=None, description="Filter dividends by the declaration date (when the dividend was officially announced). Use YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    pay_date: str | None = Field(default=None, description="Filter dividends by the payment date (when the dividend was or will be paid to shareholders). Use YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    cash_amount: float | None = Field(default=None, description="Filter dividends by the cash amount paid per share. Accepts numeric values.")
    dividend_type: Literal["CD", "SC", "LT", "ST"] | None = Field(default=None, description="Filter dividends by type: CD for regular/consistent dividends, SC for special/infrequent cash dividends, LT for long-term capital gains, or ST for short-term capital gains.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort results in ascending or descending order based on the selected sort field.")
    limit: int | None = Field(default=None, description="Limit the number of results returned. Must be between 1 and 1000, with a default of 10 results.", ge=1, le=1000)
    sort: Literal["ex_dividend_date", "pay_date", "declaration_date", "record_date", "cash_amount", "ticker"] | None = Field(default=None, description="Choose which field to sort by: ex_dividend_date (default), pay_date, declaration_date, record_date, cash_amount, or ticker symbol.")
class ListDividendsRequest(StrictModel):
    """Retrieve historical dividend payments with filtering and sorting capabilities. Query by date, amount, or dividend type to find specific dividend records across securities."""
    query: ListDividendsRequestQuery | None = None

# Operation: list_exchanges
class ListExchangesRequestQuery(StrictModel):
    locale: Literal["us", "global"] | None = Field(default=None, description="Filter results by geographic region: use 'us' for United States exchanges or 'global' for worldwide exchanges.")
class ListExchangesRequest(StrictModel):
    """Retrieve a list of all exchanges that Massive has data for, optionally filtered by geographic locale."""
    query: ListExchangesRequestQuery | None = None

# Operation: list_options_contracts
class ListOptionsContractsRequestQuery(StrictModel):
    underlying_ticker: str | None = Field(default=None, description="Filter results to contracts for a specific underlying stock ticker symbol (e.g., AAPL, TSLA).")
    contract_type: Literal["call", "put"] | None = Field(default=None, description="Filter by contract type: either call options or put options.")
    as_of: str | None = Field(default=None, description="Query contracts as they existed on a specific date using YYYY-MM-DD format. Defaults to today's date if not specified.")
    expired: bool | None = Field(default=None, description="Include expired contracts in results. By default, only active contracts are returned.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort results in ascending or descending order based on the selected sort field.")
    limit: int | None = Field(default=None, description="Maximum number of results to return, between 1 and 1000. Defaults to 10 results per request.", ge=1, le=1000)
    sort: Literal["ticker", "underlying_ticker", "expiration_date", "strike_price"] | None = Field(default=None, description="Field to sort results by: ticker symbol, underlying ticker, expiration date, or strike price. Defaults to sorting by ticker.")
class ListOptionsContractsRequest(StrictModel):
    """Retrieve historical options contracts for a given underlying asset, including both active and expired contracts. Filter by contract type, expiration date, and other criteria to find specific options trading opportunities."""
    query: ListOptionsContractsRequestQuery | None = None

# Operation: get_options_contract
class GetOptionsContractRequestPath(StrictModel):
    options_ticker: str = Field(default=..., description="The options ticker symbol identifying the contract (e.g., O:SPY251219C00650000). This follows the standard options ticker format which encodes the underlying symbol, expiration date, option type, and strike price.")
class GetOptionsContractRequestQuery(StrictModel):
    as_of: str | None = Field(default=None, description="Historical reference date for the contract data in YYYY-MM-DD format. If not provided, defaults to today's date.")
class GetOptionsContractRequest(StrictModel):
    """Retrieve detailed information about a specific options contract using its ticker symbol. Optionally specify a historical date to view the contract as it existed on that date."""
    path: GetOptionsContractRequestPath
    query: GetOptionsContractRequestQuery | None = None

# Operation: list_stock_splits
class ListStockSplitsRequestQuery(StrictModel):
    reverse_split: bool | None = Field(default=None, description="Filter results to show only reverse stock splits, where the split ratio decreases the number of shares (split_from > split_to). Omit to include all splits.")
    execution_date_gte: str | None = Field(default=None, validation_alias="execution_date.gte", serialization_alias="execution_date.gte", description="Filter splits executed on or after this date (inclusive). Use ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    execution_date_gt: str | None = Field(default=None, validation_alias="execution_date.gt", serialization_alias="execution_date.gt", description="Filter splits executed after this date (exclusive). Use ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    execution_date_lte: str | None = Field(default=None, validation_alias="execution_date.lte", serialization_alias="execution_date.lte", description="Filter splits executed on or before this date (inclusive). Use ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    execution_date_lt: str | None = Field(default=None, validation_alias="execution_date.lt", serialization_alias="execution_date.lt", description="Filter splits executed before this date (exclusive). Use ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort results in ascending or descending order based on the sort field. Defaults to ascending.")
    limit: int | None = Field(default=None, description="Maximum number of results to return per request. Must be between 1 and 1000, defaults to 10.", ge=1, le=1000)
    sort: Literal["execution_date", "ticker"] | None = Field(default=None, description="Field to sort results by: execution_date or ticker. Defaults to execution_date.")
class ListStockSplitsRequest(StrictModel):
    """Retrieve historical stock splits with details including ticker symbol, execution date, and split ratio factors. Filter by reverse splits, date range, and customize sorting and pagination."""
    query: ListStockSplitsRequestQuery | None = None

# Operation: list_tickers
class ListTickersRequestQuery(StrictModel):
    market: Literal["stocks", "crypto", "fx", "otc", "indices"] | None = Field(default=None, description="Filter results to a specific market type: stocks, crypto, forex, otc, or indices. Omit to include all markets.")
    exchange: str | None = Field(default=None, description="Filter by the asset's primary exchange using its ISO 10383 Market Identifier Code (MIC). Leave empty to query all exchanges.")
    cusip: str | None = Field(default=None, description="Filter by CUSIP code to find a specific asset. Note: CUSIP codes are accepted for filtering but are not returned in the response for legal reasons.")
    search: str | None = Field(default=None, description="Search for matching terms within ticker symbols and company names.")
    active: bool | None = Field(default=None, description="Return only actively traded tickers on the queried date. Defaults to true.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort results in ascending or descending order based on the sort field.")
    limit: int | None = Field(default=None, description="Limit the number of results returned. Must be between 1 and 1000, defaults to 100.", ge=1, le=1000)
    sort: Literal["ticker", "name", "market", "locale", "primary_exchange", "type", "currency_symbol", "currency_name", "base_currency_symbol", "base_currency_name", "cik", "composite_figi", "share_class_figi", "last_updated_utc", "delisted_utc"] | None = Field(default=None, description="Sort results by a specific field: ticker, name, market, locale, primary_exchange, type, currency details, identifiers (CIK, FIGI), or last_updated_utc. Defaults to ticker.")
class ListTickersRequest(StrictModel):
    """Query all supported ticker symbols across stocks, indices, forex, and crypto markets. Filter by market type, exchange, CUSIP, or search terms to find specific assets."""
    query: ListTickersRequestQuery | None = None

# Operation: list_ticker_types
class ListTickerTypesRequestQuery(StrictModel):
    locale: Literal["us", "global"] | None = Field(default=None, description="Filter ticker types by geographic market: use 'us' for United States market or 'global' for worldwide tickers. If omitted, returns all ticker types.")
class ListTickerTypesRequest(StrictModel):
    """Retrieve all ticker types available in the Massive database. Optionally filter results by geographic locale to see ticker types relevant to a specific market."""
    query: ListTickerTypesRequestQuery | None = None

# Operation: get_ticker_details
class GetTickerRequestPath(StrictModel):
    ticker: str = Field(default=..., description="The ticker symbol to look up, case-sensitive (e.g., AAPL for Apple Inc.). Must be a valid ticker symbol supported by the service.")
class GetTickerRequest(StrictModel):
    """Retrieve detailed information about a specific ticker symbol, including company data and market details supported by Massive."""
    path: GetTickerRequestPath

# Operation: list_snapshots
class SnapshotsRequestQuery(StrictModel):
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order direction for results: ascending or descending based on the sort field.")
    limit: int | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250 (defaults to 10).", ge=1, le=250)
    sort: Literal["ticker"] | None = Field(default=None, description="Field to sort results by; currently supports sorting by ticker symbol.")
class SnapshotsRequest(StrictModel):
    """Retrieve current snapshots for assets across all asset types, with optional sorting and pagination controls."""
    query: SnapshotsRequestQuery | None = None

# Operation: list_indices_snapshot
class IndicesSnapshotRequestQuery(StrictModel):
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for results: ascending or descending order based on the sort field.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response, ranging from 1 to 250 (defaults to 10 if not specified).", ge=1, le=250)
    sort: Literal["ticker"] | None = Field(default=None, description="Field to use for ordering results; currently supports sorting by ticker symbol.")
class IndicesSnapshotRequest(StrictModel):
    """Retrieve a snapshot of current indices data for specified tickers, with optional sorting and pagination controls."""
    query: IndicesSnapshotRequestQuery | None = None

# Operation: list_options_chain
class OptionsChainRequestPath(StrictModel):
    underlying_asset: str = Field(default=..., validation_alias="underlyingAsset", serialization_alias="underlyingAsset", description="The ticker symbol of the underlying asset (e.g., EVRI). This is the security for which you want to retrieve options contracts.")
class OptionsChainRequestQuery(StrictModel):
    contract_type: Literal["call", "put"] | None = Field(default=None, description="Filter results to only calls or puts. If omitted, both contract types are returned.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort results in ascending or descending order based on the sort field. Defaults to ascending if not specified.")
    limit: int | None = Field(default=None, description="Maximum number of results to return, between 1 and 250. Defaults to 10 if not specified.", ge=1, le=250)
    sort: Literal["ticker", "expiration_date", "strike_price"] | None = Field(default=None, description="Field to sort by: ticker symbol, expiration date, or strike price. Defaults to ticker if not specified.")
class OptionsChainRequest(StrictModel):
    """Retrieve all options contracts for a given underlying asset, with optional filtering by contract type and customizable sorting and pagination."""
    path: OptionsChainRequestPath
    query: OptionsChainRequestQuery | None = None

# Operation: get_option_contract_snapshot
class OptionContractRequestPath(StrictModel):
    underlying_asset: str = Field(default=..., validation_alias="underlyingAsset", serialization_alias="underlyingAsset", description="The ticker symbol of the underlying stock (e.g., EVRI). This identifies which equity the option contract is based on.")
    option_contract: str = Field(default=..., validation_alias="optionContract", serialization_alias="optionContract", description="The unique identifier for the specific option contract (e.g., O:EVRI260116C00015000). This format typically encodes the underlying asset, expiration date, contract type (call/put), and strike price.")
class OptionContractRequest(StrictModel):
    """Retrieve a real-time snapshot of an option contract for a given underlying stock, including current pricing and contract details."""
    path: OptionContractRequestPath

# Operation: list_crypto_trades
class TradesCryptoRequestPath(StrictModel):
    crypto_ticker: str = Field(default=..., validation_alias="cryptoTicker", serialization_alias="cryptoTicker", description="The cryptocurrency ticker symbol to retrieve trades for, formatted as an exchange prefix and currency pair (e.g., X:BTC-USD for Bitcoin in US dollars).")
class TradesCryptoRequestQuery(StrictModel):
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results: ascending (oldest first) or descending (newest first). Defaults to descending order.")
    limit: int | None = Field(default=None, description="Maximum number of trade records to return. Must be between 1 and 50,000; defaults to 1,000 if not specified.", ge=1, le=50000)
    sort: Literal["timestamp"] | None = Field(default=None, description="Field to sort results by. Currently supports sorting by timestamp only.")
class TradesCryptoRequest(StrictModel):
    """Retrieve a list of trades for a specified cryptocurrency ticker symbol, with options to sort, order, and limit results. Useful for analyzing recent trading activity and market movements."""
    path: TradesCryptoRequestPath
    query: TradesCryptoRequestQuery | None = None

# Operation: list_options_trades
class TradesOptionsRequestPath(StrictModel):
    options_ticker: str = Field(default=..., validation_alias="optionsTicker", serialization_alias="optionsTicker", description="The options ticker symbol identifying the specific contract to retrieve trades for (e.g., O:TSLA210903C00700000).")
class TradesOptionsRequestQuery(StrictModel):
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for results based on the sort field; defaults to descending order (newest first).")
    limit: int | None = Field(default=None, description="Maximum number of trade records to return, between 1 and 50,000; defaults to 1,000 if not specified.", ge=1, le=50000)
    sort: Literal["timestamp"] | None = Field(default=None, description="Field to sort results by; currently supports sorting by timestamp only.")
class TradesOptionsRequest(StrictModel):
    """Retrieve a list of trades executed for a specific options contract within an optional time range, with configurable sorting and pagination."""
    path: TradesOptionsRequestPath
    query: TradesOptionsRequestQuery | None = None

# Operation: list_trades
class TradesRequestPath(StrictModel):
    stock_ticker: str = Field(default=..., validation_alias="stockTicker", serialization_alias="stockTicker", description="The stock ticker symbol to retrieve trades for (case-sensitive). For example, AAPL for Apple Inc.")
class TradesRequestQuery(StrictModel):
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort order for results based on the sort field. Choose ascending or descending order; defaults to descending.")
    limit: int | None = Field(default=None, description="Maximum number of trade records to return. Accepts values from 1 to 50,000; defaults to 1,000 if not specified.", ge=1, le=50000)
    sort: Literal["timestamp"] | None = Field(default=None, description="Field to sort results by. Currently supports sorting by timestamp.")
class TradesRequest(StrictModel):
    """Retrieve a list of trades for a specified stock ticker within an optional time range, with configurable sorting and pagination."""
    path: TradesRequestPath
    query: TradesRequestQuery | None = None

# Operation: list_financials
class ListFinancialsRequestQuery(StrictModel):
    sic: str | None = Field(default=None, description="Filter results by Standard Industrial Classification (SIC) code to narrow results to a specific industry sector.")
    company_name_search: str | None = Field(default=None, validation_alias="company_name.search", serialization_alias="company_name.search", description="Search for companies by name using partial text matching.")
    period_of_report_date_gte: str | None = Field(default=None, validation_alias="period_of_report_date.gte", serialization_alias="period_of_report_date.gte", description="Filter to include only financial records with a period-of-report date on or after this date (inclusive). Use ISO 8601 date format.", json_schema_extra={'format': 'date'})
    period_of_report_date_gt: str | None = Field(default=None, validation_alias="period_of_report_date.gt", serialization_alias="period_of_report_date.gt", description="Filter to include only financial records with a period-of-report date strictly after this date (exclusive). Use ISO 8601 date format.", json_schema_extra={'format': 'date'})
    period_of_report_date_lte: str | None = Field(default=None, validation_alias="period_of_report_date.lte", serialization_alias="period_of_report_date.lte", description="Filter to include only financial records with a period-of-report date on or before this date (inclusive). Use ISO 8601 date format.", json_schema_extra={'format': 'date'})
    period_of_report_date_lt: str | None = Field(default=None, validation_alias="period_of_report_date.lt", serialization_alias="period_of_report_date.lt", description="Filter to include only financial records with a period-of-report date strictly before this date (exclusive). Use ISO 8601 date format.", json_schema_extra={'format': 'date'})
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort results in ascending or descending order based on the field specified in the sort parameter.")
    limit: int | None = Field(default=None, description="Maximum number of results to return per request. Defaults to 10 and cannot exceed 100.", ge=1, le=100)
    sort: Literal["filing_date", "period_of_report_date"] | None = Field(default=None, description="Field to sort results by. Choose between filing date or period-of-report date. Defaults to period-of-report date.")
class ListFinancialsRequest(StrictModel):
    """Retrieve historical financial data for stocks extracted from SEC XBRL filings. Filter by company, industry classification, reporting period, and customize result ordering and pagination."""
    query: ListFinancialsRequestQuery | None = None

# Operation: list_ipos_detailed
class ListIpOsRequestQuery(StrictModel):
    listing_date: str | None = Field(default=None, description="Filter results to a specific listing date (the first trading date for the newly listed entity). Use ISO 8601 date format.", json_schema_extra={'format': 'date'})
    ipo_status: Literal["direct_listing_process", "history", "new", "pending", "postponed", "rumor", "withdrawn"] | None = Field(default=None, description="Filter results by IPO status: new, pending, rumor, postponed, withdrawn, direct listing process, or historical.")
    order: Literal["asc", "desc"] | None = Field(default=None, description="Sort results in ascending or descending order. Defaults to descending.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Must be between 1 and 1000, defaults to 10.", ge=1, le=1000)
    sort: Literal["listing_date", "ticker", "last_updated", "security_type", "issuer_name", "currency_code", "isin", "us_code", "final_issue_price", "min_shares_offered", "max_shares_offered", "lowest_offer_price", "highest_offer_price", "total_offer_size", "shares_outstanding", "primary_exchange", "lot_size", "security_description", "ipo_status", "announced_date"] | None = Field(default=None, description="Field to sort by, such as listing date, ticker symbol, issuer name, offering price, or IPO status. Defaults to listing date.")
class ListIpOsRequest(StrictModel):
    """Retrieve a list of Initial Public Offerings with detailed information including issuer names, ticker symbols, pricing, and offering details. Filter by status (new, pending, historical, etc.) and customize sorting and pagination."""
    query: ListIpOsRequestQuery | None = None

# Operation: list_ticker_events
class GetEventsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The security identifier as a ticker symbol (case-sensitive, e.g., AAPL), CUSIP, or Composite FIGI. When using a ticker, events are returned for the entity currently represented by that ticker; use the Ticker Details endpoint to find identifiers for entities previously associated with a ticker.")
class GetEventsRequestQuery(StrictModel):
    types: str | None = Field(default=None, description="Filter results by event type using a comma-separated list. Currently supports ticker_change. Omit to return all available event types.")
class GetEventsRequest(StrictModel):
    """Retrieve a chronological timeline of corporate events for a security identified by ticker symbol, CUSIP, or Composite FIGI. Returns events for the entity currently associated with the identifier."""
    path: GetEventsRequestPath
    query: GetEventsRequestQuery | None = None

# ============================================================================
# Component Models
# ============================================================================

class ExchangeItem(PermissiveModel):
    code: str | None = Field(None, description="A unique identifier for the exchange internal to Massive.  This is not an industry code or ISO standard.")
    id_: float | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the exchange.")
    market: str | None = Field(None, description="The market data type that this exchange contains.")
    mic: str | None = Field(None, description="The Market Identification Code or MIC as defined in ISO 10383 (<a rel=\"nofollow\" target=\"_blank\" href=\"https://en.wikipedia.org/wiki/Market_Identifier_Code\">https://en.wikipedia.org/wiki/Market_Identifier_Code</a>).")
    name: str | None = Field(None, description="The name of the exchange.")
    tape: str | None = Field(None, description="The tape id of the exchange.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of exchange.\n- TRF = Trade Reporting Facility\n- exchange = Reporting exchange on the tape\n")

class Exchange(RootModel[list[ExchangeItem]]):
    pass


# Rebuild models to resolve forward references (required for circular refs)
Exchange.model_rebuild()
ExchangeItem.model_rebuild()

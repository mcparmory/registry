"""
Alpha Vantage Api MCP Server - Pydantic Models

Generated: 2026-04-06 14:30:40 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import StrictModel
from pydantic import Field

__all__ = [
    "GetQueryAdoscRequest",
    "GetQueryAdRequest",
    "GetQueryAdxRequest",
    "GetQueryAdxrRequest",
    "GetQueryAllCommoditiesRequest",
    "GetQueryAluminumRequest",
    "GetQueryAnalyticsFixedWindowRequest",
    "GetQueryAnalyticsSlidingWindowRequest",
    "GetQueryApoRequest",
    "GetQueryAroonoscRequest",
    "GetQueryAroonRequest",
    "GetQueryAtrRequest",
    "GetQueryBalanceSheetRequest",
    "GetQueryBbandsRequest",
    "GetQueryBopRequest",
    "GetQueryBrentRequest",
    "GetQueryCashFlowRequest",
    "GetQueryCciRequest",
    "GetQueryCmoRequest",
    "GetQueryCoffeeRequest",
    "GetQueryCopperRequest",
    "GetQueryCornRequest",
    "GetQueryCottonRequest",
    "GetQueryCpiRequest",
    "GetQueryCryptoIntradayRequest",
    "GetQueryCurrencyExchangeRateRequest",
    "GetQueryDemaRequest",
    "GetQueryDigitalCurrencyDailyRequest",
    "GetQueryDigitalCurrencyMonthlyRequest",
    "GetQueryDigitalCurrencyWeeklyRequest",
    "GetQueryDividendsRequest",
    "GetQueryDurablesRequest",
    "GetQueryDxRequest",
    "GetQueryEarningsCalendarRequest",
    "GetQueryEarningsCallTranscriptRequest",
    "GetQueryEarningsEstimatesRequest",
    "GetQueryEarningsRequest",
    "GetQueryEmaRequest",
    "GetQueryEtfProfileRequest",
    "GetQueryFederalFundsRateRequest",
    "GetQueryFxDailyRequest",
    "GetQueryFxIntradayRequest",
    "GetQueryFxMonthlyRequest",
    "GetQueryFxWeeklyRequest",
    "GetQueryGoldSilverHistoryRequest",
    "GetQueryGoldSilverSpotRequest",
    "GetQueryHistoricalOptionsRequest",
    "GetQueryHistoricalPutCallRatioRequest",
    "GetQueryHtDcperiodRequest",
    "GetQueryHtDcphaseRequest",
    "GetQueryHtPhasorRequest",
    "GetQueryHtSineRequest",
    "GetQueryHtTrendlineRequest",
    "GetQueryHtTrendmodeRequest",
    "GetQueryIncomeStatementRequest",
    "GetQueryIndexCatalogRequest",
    "GetQueryIndexDataRequest",
    "GetQueryInflationRequest",
    "GetQueryInsiderTransactionsRequest",
    "GetQueryInstitutionalHoldingsRequest",
    "GetQueryIpoCalendarRequest",
    "GetQueryKamaRequest",
    "GetQueryListingStatusRequest",
    "GetQueryMacdextRequest",
    "GetQueryMacdRequest",
    "GetQueryMamaRequest",
    "GetQueryMarketStatusRequest",
    "GetQueryMfiRequest",
    "GetQueryMidpointRequest",
    "GetQueryMidpriceRequest",
    "GetQueryMinusDiRequest",
    "GetQueryMinusDmRequest",
    "GetQueryMomRequest",
    "GetQueryNatrRequest",
    "GetQueryNaturalGasRequest",
    "GetQueryNewsSentimentRequest",
    "GetQueryNonfarmPayrollRequest",
    "GetQueryObvRequest",
    "GetQueryOverviewRequest",
    "GetQueryPlusDiRequest",
    "GetQueryPlusDmRequest",
    "GetQueryPpoRequest",
    "GetQueryRealGdpPerCapitaRequest",
    "GetQueryRealGdpRequest",
    "GetQueryRealtimeBulkQuotesRequest",
    "GetQueryRealtimeOptionsRequest",
    "GetQueryRealtimePutCallRatioRequest",
    "GetQueryRetailSalesRequest",
    "GetQueryRocRequest",
    "GetQueryRocrRequest",
    "GetQueryRsiRequest",
    "GetQuerySarRequest",
    "GetQuerySharesOutstandingRequest",
    "GetQuerySmaRequest",
    "GetQuerySplitsRequest",
    "GetQueryStochfRequest",
    "GetQueryStochRequest",
    "GetQueryStochrsiRequest",
    "GetQuerySugarRequest",
    "GetQuerySymbolSearchRequest",
    "GetQueryT3Request",
    "GetQueryTemaRequest",
    "GetQueryTimeSeriesDailyAdjustedRequest",
    "GetQueryTimeSeriesDailyRequest",
    "GetQueryTimeSeriesIntradayRequest",
    "GetQueryTimeSeriesMonthlyAdjustedRequest",
    "GetQueryTimeSeriesMonthlyRequest",
    "GetQueryTimeSeriesWeeklyAdjustedRequest",
    "GetQueryTimeSeriesWeeklyRequest",
    "GetQueryTopGainersLosersRequest",
    "GetQueryTrangeRequest",
    "GetQueryTreasuryYieldRequest",
    "GetQueryTrimaRequest",
    "GetQueryTrixRequest",
    "GetQueryUltoscRequest",
    "GetQueryUnemploymentRequest",
    "GetQueryVwapRequest",
    "GetQueryWheatRequest",
    "GetQueryWillrRequest",
    "GetQueryWmaRequest",
    "GetQueryWtiRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: get_intraday_time_series
class GetQueryTimeSeriesIntradayRequestQuery(StrictModel):
    function: Literal["TIME_SERIES_INTRADAY"] = Field(default=..., description="The time series function to query. Must be TIME_SERIES_INTRADAY for intraday data.")
    symbol: str = Field(default=..., description="The stock symbol or ticker of the equity to retrieve data for (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min"] = Field(default=..., description="The time interval between consecutive data points. Choose from 1-minute, 5-minute, 15-minute, 30-minute, or 60-minute intervals.")
    adjusted: bool | None = Field(default=None, description="Whether to adjust historical prices for stock splits and dividend events. Defaults to true for adjusted data.")
    extended_hours: bool | None = Field(default=None, description="Whether to include pre-market and post-market trading hours in the results. Defaults to true.")
    month: str | None = Field(default=None, description="Query a specific month of historical data in YYYY-MM format (e.g., 2009-01). Supported from January 2000 onwards.", pattern='^\\d{4}-\\d{2}$')
    outputsize: Literal["compact", "full"] | None = Field(default=None, description="Control the amount of data returned. Use 'compact' for the latest 100 data points, or 'full' for trailing 30 days of data (or the entire month if a specific month is requested). Defaults to compact.")
class GetQueryTimeSeriesIntradayRequest(StrictModel):
    """Retrieve intraday OHLCV (open, high, low, close, volume) time series data for an equity, with support for 20+ years of historical data and optional adjustment for splits and dividends."""
    query: GetQueryTimeSeriesIntradayRequestQuery

# Operation: get_daily_time_series
class GetQueryTimeSeriesDailyRequestQuery(StrictModel):
    function: Literal["TIME_SERIES_DAILY"] = Field(default=..., description="The time series data type to retrieve. Must be set to TIME_SERIES_DAILY for daily candlestick data.")
    symbol: str = Field(default=..., description="The stock symbol or ticker of the equity to retrieve data for (e.g., IBM, AAPL).")
    outputsize: Literal["compact", "full"] | None = Field(default=None, description="Controls the amount of historical data returned. Use 'compact' for the latest 100 data points (recommended for reducing response size), or 'full' for the complete 20+ year historical dataset. Full output requires a premium API key.")
class GetQueryTimeSeriesDailyRequest(StrictModel):
    """Retrieves daily OHLCV (open, high, low, close, volume) time series data for a specified equity, covering 20+ years of historical data. Choose between compact (latest 100 data points) or full historical dataset."""
    query: GetQueryTimeSeriesDailyRequestQuery

# Operation: get_daily_adjusted_time_series
class GetQueryTimeSeriesDailyAdjustedRequestQuery(StrictModel):
    function: Literal["TIME_SERIES_DAILY_ADJUSTED"] = Field(default=..., description="The time series data type to retrieve. Must be set to TIME_SERIES_DAILY_ADJUSTED for daily adjusted price and volume data.")
    symbol: str = Field(default=..., description="The stock ticker symbol of the equity to query (e.g., IBM, AAPL). Case-insensitive.")
    outputsize: Literal["compact", "full"] | None = Field(default=None, description="Controls the amount of historical data returned. Use 'compact' for the most recent 100 trading days, or 'full' for the complete 20+ year historical dataset. Defaults to compact.")
class GetQueryTimeSeriesDailyAdjustedRequest(StrictModel):
    """Retrieves daily adjusted OHLCV (open, high, low, close, volume) time series data for an equity, including split and dividend adjustments. Supports up to 20+ years of historical data with flexible output sizing."""
    query: GetQueryTimeSeriesDailyAdjustedRequestQuery

# Operation: get_weekly_time_series
class GetQueryTimeSeriesWeeklyRequestQuery(StrictModel):
    function: Literal["TIME_SERIES_WEEKLY"] = Field(default=..., description="The time series data type to retrieve. Must be set to TIME_SERIES_WEEKLY for weekly equity data.")
    symbol: str = Field(default=..., description="The stock symbol or ticker of the equity to retrieve data for (e.g., IBM, AAPL).")
class GetQueryTimeSeriesWeeklyRequest(StrictModel):
    """Retrieves weekly time series data for a specified equity, including open, high, low, close prices and trading volume for the last trading day of each week, covering 20+ years of historical data."""
    query: GetQueryTimeSeriesWeeklyRequestQuery

# Operation: get_weekly_adjusted_time_series
class GetQueryTimeSeriesWeeklyAdjustedRequestQuery(StrictModel):
    function: Literal["TIME_SERIES_WEEKLY_ADJUSTED"] = Field(default=..., description="The time series function type. Must be set to TIME_SERIES_WEEKLY_ADJUSTED to retrieve weekly adjusted historical data.")
    symbol: str = Field(default=..., description="The stock symbol or ticker of the equity to retrieve data for (e.g., IBM, AAPL). Case-insensitive.")
class GetQueryTimeSeriesWeeklyAdjustedRequest(StrictModel):
    """Retrieves weekly adjusted time series data for an equity, including open, high, low, close, adjusted close, volume, and dividend information. Covers 20+ years of historical data with the last trading day of each week as the reference point."""
    query: GetQueryTimeSeriesWeeklyAdjustedRequestQuery

# Operation: get_equity_monthly_time_series
class GetQueryTimeSeriesMonthlyRequestQuery(StrictModel):
    function: Literal["TIME_SERIES_MONTHLY"] = Field(default=..., description="The time series data type to retrieve. Must be set to TIME_SERIES_MONTHLY for monthly aggregated equity data.")
    symbol: str = Field(default=..., description="The stock symbol or ticker of the equity to retrieve data for (e.g., IBM, AAPL, MSFT).")
class GetQueryTimeSeriesMonthlyRequest(StrictModel):
    """Retrieves monthly time series data for a specified global equity, including open, high, low, close prices and trading volume for the last trading day of each month, covering 20+ years of historical data."""
    query: GetQueryTimeSeriesMonthlyRequestQuery

# Operation: get_monthly_adjusted_time_series
class GetQueryTimeSeriesMonthlyAdjustedRequestQuery(StrictModel):
    function: Literal["TIME_SERIES_MONTHLY_ADJUSTED"] = Field(default=..., description="The time series function type. Must be set to TIME_SERIES_MONTHLY_ADJUSTED to retrieve monthly adjusted data.")
    symbol: str = Field(default=..., description="The stock symbol or ticker of the equity to retrieve data for (e.g., IBM, AAPL).")
class GetQueryTimeSeriesMonthlyAdjustedRequest(StrictModel):
    """Retrieves monthly adjusted historical time series data for an equity, including split and dividend-adjusted prices, volumes, and dividends covering 20+ years of historical data."""
    query: GetQueryTimeSeriesMonthlyAdjustedRequestQuery

# Operation: get_realtime_quotes
class GetQueryRealtimeBulkQuotesRequestQuery(StrictModel):
    function: Literal["REALTIME_BULK_QUOTES"] = Field(default=..., description="The API function type; must be set to REALTIME_BULK_QUOTES to retrieve real-time quotes.")
    symbol: str = Field(default=..., description="One or more stock symbols separated by commas (e.g., MSFT,AAPL,IBM). Up to 100 symbols are accepted per request; additional symbols beyond 100 will be ignored.")
class GetQueryRealtimeBulkQuotesRequest(StrictModel):
    """Fetch real-time market quotes for multiple US-traded symbols in a single request, supporting up to 100 symbols with coverage of regular and extended trading hours."""
    query: GetQueryRealtimeBulkQuotesRequestQuery

# Operation: search_symbols
class GetQuerySymbolSearchRequestQuery(StrictModel):
    function: Literal["SYMBOL_SEARCH"] = Field(default=..., description="The search function to execute. Must be set to SYMBOL_SEARCH to perform symbol lookups.")
    keywords: str = Field(default=..., description="A text string containing one or more keywords to search for symbols. For example, company names like 'microsoft' or 'tesco'.")
class GetQuerySymbolSearchRequest(StrictModel):
    """Search for financial symbols and market information by keywords. Returns matching symbols ranked by relevance with match scores to support custom filtering logic."""
    query: GetQuerySymbolSearchRequestQuery

# Operation: check_market_status
class GetQueryMarketStatusRequestQuery(StrictModel):
    function: Literal["MARKET_STATUS"] = Field(default=..., description="The function to execute; must be set to MARKET_STATUS to retrieve global market status information.")
class GetQueryMarketStatusRequest(StrictModel):
    """Check the current open or closed status of major global trading venues across equities, forex, and cryptocurrency markets."""
    query: GetQueryMarketStatusRequestQuery

# Operation: get_index_data
class GetQueryIndexDataRequestQuery(StrictModel):
    function: Literal["INDEX_DATA"] = Field(default=..., description="The data function type to retrieve. Must be set to INDEX_DATA to fetch index time series information.")
    symbol: Literal["COMP"] = Field(default=..., description="The stock market index symbol. Must be set to COMP to retrieve NASDAQ Composite Index data.")
    interval: Literal["daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points in the returned series. Choose from daily, weekly, or monthly granularity.")
class GetQueryIndexDataRequest(StrictModel):
    """Retrieves historical OHLC (open, high, low, close) time series data for the NASDAQ Composite Index spanning decades of market data."""
    query: GetQueryIndexDataRequestQuery

# Operation: list_index_symbols
class GetQueryIndexCatalogRequestQuery(StrictModel):
    function: Literal["INDEX_CATALOG"] = Field(default=..., description="The catalog function to execute. Must be set to INDEX_CATALOG to retrieve the index symbol catalog.")
class GetQueryIndexCatalogRequest(StrictModel):
    """Retrieves a complete catalog of all supported index symbols with their full names. Use this to discover available indices for market data queries."""
    query: GetQueryIndexCatalogRequestQuery

# Operation: list_realtime_options
class GetQueryRealtimeOptionsRequestQuery(StrictModel):
    function: Literal["REALTIME_OPTIONS"] = Field(default=..., description="The data type to retrieve. Must be set to REALTIME_OPTIONS to fetch current options market data.")
    symbol: str = Field(default=..., description="The stock symbol for which to retrieve options data (e.g., IBM).")
    require_greeks: bool | None = Field(default=None, description="Include greeks (delta, gamma, vega, theta, rho) and implied volatility (IV) calculations in the response. Disabled by default for faster responses.")
    contract: str | None = Field(default=None, description="Filter results to a specific options contract by its contract ID. When omitted, returns the entire option chain for the symbol.")
    expiration: str | None = Field(default=None, description="Filter results to contracts expiring on a specific date in YYYY-MM-DD format. The date must be today or later. When omitted, returns contracts across all available expiration dates.", json_schema_extra={'format': 'date'})
class GetQueryRealtimeOptionsRequest(StrictModel):
    """Retrieve realtime US options data with full market coverage. Option chains are automatically sorted by expiration date (chronological) and then by strike price (low to high)."""
    query: GetQueryRealtimeOptionsRequestQuery

# Operation: get_realtime_put_call_ratio
class GetQueryRealtimePutCallRatioRequestQuery(StrictModel):
    function: Literal["REALTIME_PUT_CALL_RATIO"] = Field(default=..., description="The function type for this operation, which must be set to REALTIME_PUT_CALL_RATIO to retrieve realtime put-call ratio data.")
    symbol: str = Field(default=..., description="The stock ticker symbol for the equity to analyze (e.g., IBM). This identifies which company's option chain data to retrieve.")
class GetQueryRealtimePutCallRatioRequest(StrictModel):
    """Retrieves the realtime put-call ratio for a specified equity symbol, indicating market sentiment across the entire option chain and by expiration date. Lower ratios (≤0.6) suggest bullish sentiment with more call buying, while higher ratios (≥1.0) indicate bearish sentiment with more put buying."""
    query: GetQueryRealtimePutCallRatioRequestQuery

# Operation: get_historical_options
class GetQueryHistoricalOptionsRequestQuery(StrictModel):
    function: Literal["HISTORICAL_OPTIONS"] = Field(default=..., description="The data type to retrieve. Must be set to HISTORICAL_OPTIONS to fetch historical options chain data.")
    symbol: str = Field(default=..., description="The equity ticker symbol (e.g., IBM). Used to identify which stock's options data to retrieve.")
    date: str | None = Field(default=None, description="The date for which to retrieve options data in YYYY-MM-DD format. Any date from 2008-01-01 onwards is accepted. If omitted, defaults to the previous trading session.", json_schema_extra={'format': 'date'})
class GetQueryHistoricalOptionsRequest(StrictModel):
    """Retrieve historical options chain data for a given equity symbol, including implied volatility and Greeks (delta, gamma, theta, vega, rho). Data spans 15+ years and defaults to the previous trading session if no date is specified."""
    query: GetQueryHistoricalOptionsRequestQuery

# Operation: get_historical_put_call_ratio
class GetQueryHistoricalPutCallRatioRequestQuery(StrictModel):
    function: Literal["HISTORICAL_PUT_CALL_RATIO"] = Field(default=..., description="The function type for this operation. Must be set to HISTORICAL_PUT_CALL_RATIO to retrieve put-call ratio data.")
    symbol: str = Field(default=..., description="The stock ticker symbol for the equity (e.g., IBM). This identifies which company's options data to retrieve.")
    date: str | None = Field(default=None, description="The date for which to retrieve put-call ratio data in YYYY-MM-DD format. If not provided, defaults to the most recent trading session. Any date from 2008-01-01 onwards is accepted.", json_schema_extra={'format': 'date'})
class GetQueryHistoricalPutCallRatioRequest(StrictModel):
    """Retrieves historical put-call ratios for an equity symbol, indicating market sentiment through the proportion of put to call options. Ratios below 0.6 suggest bullish sentiment, while ratios above 1.0 indicate bearish sentiment."""
    query: GetQueryHistoricalPutCallRatioRequestQuery

# Operation: search_news_sentiment
class GetQueryNewsSentimentRequestQuery(StrictModel):
    function: Literal["NEWS_SENTIMENT"] = Field(default=..., description="The operation type to perform. Must be set to NEWS_SENTIMENT to retrieve news and sentiment data.")
    tickers: str | None = Field(default=None, description="Filter articles by one or more asset symbols (e.g., AAPL for stocks, CRYPTO:BTC for Bitcoin, FOREX:USD for US Dollar). Use comma-separated values to match articles mentioning multiple symbols simultaneously.")
    topics: Literal["blockchain", "earnings", "ipo", "mergers_and_acquisitions", "financial_markets", "economy_fiscal", "economy_monetary", "economy_macro", "energy_transportation", "finance", "life_sciences", "manufacturing", "real_estate", "retail_wholesale", "technology"] | None = Field(default=None, description="Filter articles by news topic category. Choose from: blockchain, earnings, ipo, mergers_and_acquisitions, financial_markets, economy_fiscal, economy_monetary, economy_macro, energy_transportation, finance, life_sciences, manufacturing, real_estate, retail_wholesale, or technology.")
    time_from: str | None = Field(default=None, description="Filter articles published on or after this date and time. Use YYYYMMDDTHHMM format (e.g., 20220410T0130 for April 10, 2022 at 1:30 AM).", json_schema_extra={'format': 'date-time'})
    time_to: str | None = Field(default=None, description="Filter articles published on or before this date and time. Use YYYYMMDDTHHMM format. If omitted, defaults to the current time.", json_schema_extra={'format': 'date-time'})
    sort: Literal["LATEST", "EARLIEST", "RELEVANCE"] | None = Field(default=None, description="Order results by LATEST (most recent first, default), EARLIEST (oldest first), or RELEVANCE (best match first).")
    limit: Literal[50, 1000] | None = Field(default=None, description="Maximum number of results to return. Choose 50 (default) or 1000.")
class GetQueryNewsSentimentRequest(StrictModel):
    """Search live and historical market news with sentiment analysis across stocks, cryptocurrencies, forex, and economic topics from global news outlets."""
    query: GetQueryNewsSentimentRequestQuery

# Operation: get_earnings_call_transcript
class GetQueryEarningsCallTranscriptRequestQuery(StrictModel):
    function: Literal["EARNINGS_CALL_TRANSCRIPT"] = Field(default=..., description="The function identifier for this operation. Must be set to EARNINGS_CALL_TRANSCRIPT to retrieve earnings call transcripts.")
    symbol: str = Field(default=..., description="The stock ticker symbol of the company (e.g., IBM). Used to identify which company's earnings call transcript to retrieve.")
    quarter: str = Field(default=..., description="The fiscal quarter in YYYYQM format (e.g., 2024Q1), where Q is followed by a digit 1-4. Any quarter from 2010Q1 onwards is supported.", pattern='^[0-9]{4}Q[1-4]$')
class GetQueryEarningsCallTranscriptRequest(StrictModel):
    """Retrieves the earnings call transcript for a specified company and fiscal quarter, with historical data spanning over 15 years and enriched with LLM-based sentiment analysis."""
    query: GetQueryEarningsCallTranscriptRequestQuery

# Operation: list_market_movers
class GetQueryTopGainersLosersRequestQuery(StrictModel):
    function: Literal["TOP_GAINERS_LOSERS"] = Field(default=..., description="The function to execute. Must be set to TOP_GAINERS_LOSERS to retrieve market mover data.")
class GetQueryTopGainersLosersRequest(StrictModel):
    """Retrieve the top 20 gainers, losers, and most actively traded stocks in the US market. Historical data is returned by default, with real-time or 15-minute delayed data available for premium members."""
    query: GetQueryTopGainersLosersRequestQuery

# Operation: list_insider_transactions
class GetQueryInsiderTransactionsRequestQuery(StrictModel):
    function: Literal["INSIDER_TRANSACTIONS"] = Field(default=..., description="The function type to invoke. Must be set to INSIDER_TRANSACTIONS to retrieve insider transaction data.")
    symbol: str = Field(default=..., description="The stock ticker symbol of the company for which to retrieve insider transactions (e.g., IBM, AAPL).")
class GetQueryInsiderTransactionsRequest(StrictModel):
    """Retrieve insider transactions (SEC Form 4 filings) for a specified company, including historical records of trades made by key stakeholders such as executives, founders, and board members."""
    query: GetQueryInsiderTransactionsRequestQuery

# Operation: get_institutional_holdings
class GetQueryInstitutionalHoldingsRequestQuery(StrictModel):
    function: Literal["INSTITUTIONAL_HOLDINGS"] = Field(default=..., description="The function type to execute; must be set to INSTITUTIONAL_HOLDINGS to retrieve institutional ownership data.")
    symbol: str = Field(default=..., description="The stock ticker symbol for the equity of interest (e.g., IBM, AAPL). Use the standard market symbol without exchange suffix.")
class GetQueryInstitutionalHoldingsRequest(StrictModel):
    """Retrieves institutional ownership and holdings data for a specified equity, showing which institutions hold shares and their ownership percentages."""
    query: GetQueryInstitutionalHoldingsRequestQuery

# Operation: calculate_analytics_fixed_window
class GetQueryAnalyticsFixedWindowRequestQuery(StrictModel):
    function: Literal["ANALYTICS_FIXED_WINDOW"] = Field(default=..., description="The analytics function to execute. Must be set to ANALYTICS_FIXED_WINDOW for this operation.")
    symbols: str = Field(default=..., validation_alias="SYMBOLS", serialization_alias="SYMBOLS", description="Comma-separated list of stock symbols to analyze. Free API keys support up to 5 symbols per request; premium keys support up to 50 symbols.")
    range_: str = Field(default=..., validation_alias="RANGE", serialization_alias="RANGE", description="The time period for analysis. Specify as 'full' for all available data, a relative range like '30day' or '6month', a single date in YYYY-MM-DD format, or a date range using start and end dates (e.g., '2023-07-01&RANGE=2023-08-31'). Also accepts YYYY-MM for a full month or YYYY-MM-DD for a single day.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "DAILY", "WEEKLY", "MONTHLY"] = Field(default=..., validation_alias="INTERVAL", serialization_alias="INTERVAL", description="The frequency of data points in the time series. Choose from minute-level intervals (1min, 5min, 15min, 30min, 60min) or daily/weekly/monthly aggregations (DAILY, WEEKLY, MONTHLY).")
    calculations: str = Field(default=..., validation_alias="CALCULATIONS", serialization_alias="CALCULATIONS", description="Comma-separated list of metrics to calculate. Available metrics include MIN, MAX, MEAN, MEDIAN, CUMULATIVE_RETURN, VARIANCE, STDDEV, MAX_DRAWDOWN, HISTOGRAM, AUTOCORRELATION, COVARIANCE, and CORRELATION. Some metrics accept optional parameters in parentheses (e.g., VARIANCE(annualized=True), HISTOGRAM(bins=20), AUTOCORRELATION(lag=2), CORRELATION(method=KENDALL)).")
    ohlc: Literal["open", "high", "low", "close"] | None = Field(default=None, validation_alias="OHLC", serialization_alias="OHLC", description="The price field to use for calculations: open, high, low, or close. Defaults to close price if not specified.")
class GetQueryAnalyticsFixedWindowRequest(StrictModel):
    """Calculate advanced analytics metrics for one or more financial symbols over a fixed time window, including statistical measures like returns, variance, drawdown, and correlation analysis."""
    query: GetQueryAnalyticsFixedWindowRequestQuery

# Operation: analyze_sliding_window_metrics
class GetQueryAnalyticsSlidingWindowRequestQuery(StrictModel):
    function: Literal["ANALYTICS_SLIDING_WINDOW"] = Field(default=..., description="The analytics function to execute. Must be set to ANALYTICS_SLIDING_WINDOW.")
    symbols: str = Field(default=..., validation_alias="SYMBOLS", serialization_alias="SYMBOLS", description="One or more stock symbols to analyze, provided as a comma-separated list. Free API keys support up to 5 symbols per request; premium keys support up to 50.")
    range_: str = Field(default=..., validation_alias="RANGE", serialization_alias="RANGE", description="The time period for the analysis. Accepts relative ranges (e.g., '2month', '10day'), specific dates in YYYY-MM-DD format, or ISO 8601 format. You can specify a start and end date by providing two RANGE parameters.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "DAILY", "WEEKLY", "MONTHLY"] = Field(default=..., validation_alias="INTERVAL", serialization_alias="INTERVAL", description="The frequency of data points in the time series. Choose from minute-level intervals (1min, 5min, 15min, 30min, 60min) for intraday analysis or daily/weekly/monthly intervals for longer-term trends.")
    ohlc: Literal["open", "high", "low", "close"] | None = Field(default=None, validation_alias="OHLC", serialization_alias="OHLC", description="The price field to use for calculations: open, high, low, or close price. Defaults to close price if not specified.")
    window_size: int = Field(default=..., validation_alias="WINDOW_SIZE", serialization_alias="WINDOW_SIZE", description="The number of data points in each sliding window. Must be at least 10, though larger windows (e.g., 20+) are recommended for more reliable statistical results.", ge=10)
    calculations: str = Field(default=..., validation_alias="CALCULATIONS", serialization_alias="CALCULATIONS", description="A comma-separated list of metrics to calculate, such as MEAN, MEDIAN, CUMULATIVE_RETURN, VARIANCE, STDDEV, COVARIANCE, or CORRELATION. Free API keys allow 1 metric per request; premium keys allow multiple. Optional parameters can be appended to metrics (e.g., STDDEV(annualized=True), CORRELATION(method=KENDALL)).")
class GetQueryAnalyticsSlidingWindowRequest(StrictModel):
    """Calculate advanced analytics metrics (mean, variance, correlation, etc.) for one or more stock symbols over sliding time windows, enabling trend analysis and statistical insights across different time intervals."""
    query: GetQueryAnalyticsSlidingWindowRequestQuery

# Operation: get_company_overview
class GetQueryOverviewRequestQuery(StrictModel):
    function: Literal["OVERVIEW"] = Field(default=..., description="The type of company data to retrieve. Must be set to OVERVIEW to fetch company information and financial metrics.")
    symbol: str = Field(default=..., description="The stock ticker symbol of the company you want to look up (e.g., IBM, AAPL).")
class GetQueryOverviewRequest(StrictModel):
    """Retrieve comprehensive company information including financial ratios and key metrics for a specified equity ticker. Data is typically updated on the same day the company reports its latest earnings and financial results."""
    query: GetQueryOverviewRequestQuery

# Operation: get_etf_profile
class GetQueryEtfProfileRequestQuery(StrictModel):
    function: Literal["ETF_PROFILE"] = Field(default=..., description="The function type to execute; must be set to ETF_PROFILE to retrieve ETF profile and holdings data.")
    symbol: str = Field(default=..., description="The ticker symbol of the ETF to retrieve profile information for (e.g., QQQ, SPY).")
class GetQueryEtfProfileRequest(StrictModel):
    """Retrieves comprehensive ETF profile data including key metrics (net assets, expense ratio, turnover) and detailed holdings information with allocation breakdown by asset types and sectors."""
    query: GetQueryEtfProfileRequestQuery

# Operation: get_dividend_history
class GetQueryDividendsRequestQuery(StrictModel):
    function: Literal["DIVIDENDS"] = Field(default=..., description="The dividend query function type. Must be set to DIVIDENDS to retrieve dividend data.")
    symbol: str = Field(default=..., description="The equity ticker symbol for which to retrieve dividend information (e.g., IBM, AAPL).")
class GetQueryDividendsRequest(StrictModel):
    """Retrieve historical and declared future dividend distributions for a specified equity ticker symbol."""
    query: GetQueryDividendsRequestQuery

# Operation: get_stock_splits
class GetQuerySplitsRequestQuery(StrictModel):
    function: Literal["SPLITS"] = Field(default=..., description="The function type to execute. Must be set to SPLITS to retrieve stock split data.")
    symbol: str = Field(default=..., description="The stock ticker symbol for which to retrieve historical split data (e.g., IBM, AAPL).")
class GetQuerySplitsRequest(StrictModel):
    """Retrieves historical stock split events for a given equity ticker symbol, including dates and split ratios."""
    query: GetQuerySplitsRequestQuery

# Operation: get_income_statement
class GetQueryIncomeStatementRequestQuery(StrictModel):
    function: Literal["INCOME_STATEMENT"] = Field(default=..., description="The financial statement type to retrieve. Must be set to INCOME_STATEMENT to fetch income statement data.")
    symbol: str = Field(default=..., description="The stock ticker symbol of the company whose income statement you want to retrieve (e.g., IBM, AAPL).")
class GetQueryIncomeStatementRequest(StrictModel):
    """Retrieve annual and quarterly income statements for a specified equity, with normalized fields mapped to GAAP and IFRS taxonomies. Data is typically updated on the same day the company reports its latest earnings."""
    query: GetQueryIncomeStatementRequestQuery

# Operation: get_balance_sheet
class GetQueryBalanceSheetRequestQuery(StrictModel):
    function: Literal["BALANCE_SHEET"] = Field(default=..., description="The balance sheet data type to retrieve. Must be set to BALANCE_SHEET.")
    symbol: str = Field(default=..., description="The stock ticker symbol of the company (e.g., IBM, AAPL). Used to identify which equity's balance sheet to retrieve.")
class GetQueryBalanceSheetRequest(StrictModel):
    """Retrieve annual and quarterly balance sheet data for a specified equity, with normalized fields mapped to GAAP and IFRS taxonomies. Data is typically updated on the same day the company reports its latest earnings and financials."""
    query: GetQueryBalanceSheetRequestQuery

# Operation: get_cash_flow_statement
class GetQueryCashFlowRequestQuery(StrictModel):
    function: Literal["CASH_FLOW"] = Field(default=..., description="The cash flow statement function type. Must be set to CASH_FLOW to retrieve cash flow data.")
    symbol: str = Field(default=..., description="The stock ticker symbol of the company for which to retrieve cash flow statements (e.g., IBM, AAPL).")
class GetQueryCashFlowRequest(StrictModel):
    """Retrieves annual and quarterly cash flow statements for a specified equity, with normalized fields mapped to GAAP and IFRS taxonomies. Data is typically updated on the same day the company reports its latest earnings and financial results."""
    query: GetQueryCashFlowRequestQuery

# Operation: get_shares_outstanding
class GetQuerySharesOutstandingRequestQuery(StrictModel):
    function: Literal["SHARES_OUTSTANDING"] = Field(default=..., description="The function identifier for this operation. Must be set to SHARES_OUTSTANDING to retrieve shares outstanding data.")
    symbol: str = Field(default=..., description="The stock ticker symbol of the company (e.g., MSFT). Use the standard market ticker symbol for the equity of interest.")
class GetQuerySharesOutstandingRequest(StrictModel):
    """Retrieves quarterly shares outstanding data for a specified equity, including both basic and diluted share counts. Data is typically updated on the same day the company reports its latest earnings and financial results."""
    query: GetQuerySharesOutstandingRequestQuery

# Operation: get_earnings
class GetQueryEarningsRequestQuery(StrictModel):
    function: Literal["EARNINGS"] = Field(default=..., description="The earnings data function type. Must be set to EARNINGS to retrieve earnings data.")
    symbol: str = Field(default=..., description="The stock ticker symbol of the company (e.g., IBM, AAPL). Used to identify which company's earnings data to retrieve.")
class GetQueryEarningsRequest(StrictModel):
    """Retrieve annual and quarterly earnings per share (EPS) data for a company, including analyst estimates and surprise metrics for quarterly periods."""
    query: GetQueryEarningsRequestQuery

# Operation: get_earnings_estimates
class GetQueryEarningsEstimatesRequestQuery(StrictModel):
    function: Literal["EARNINGS_ESTIMATES"] = Field(default=..., description="The earnings estimates function type. Must be set to EARNINGS_ESTIMATES to retrieve consensus analyst estimates.")
    symbol: str = Field(default=..., description="The stock ticker symbol for the company of interest (e.g., IBM, AAPL). Used to identify which equity's earnings estimates to retrieve.")
class GetQueryEarningsEstimatesRequest(StrictModel):
    """Retrieve consensus earnings estimates for a specified equity, including annual and quarterly EPS and revenue projections, analyst count, and revision history."""
    query: GetQueryEarningsEstimatesRequestQuery

# Operation: list_listing_status
class GetQueryListingStatusRequestQuery(StrictModel):
    function: Literal["LISTING_STATUS"] = Field(default=..., description="The function type for this operation. Must be set to LISTING_STATUS to query asset listing status.")
    date: str | None = Field(default=None, description="The date for which to retrieve listing status. Use YYYY-MM-DD format for any date from January 1, 2010 onwards. If omitted, returns data as of the latest trading day.", json_schema_extra={'format': 'date'})
    state: Literal["active", "delisted"] | None = Field(default=None, description="Filter results by asset state: active returns currently traded stocks and ETFs, while delisted returns assets that have been removed from exchanges. Defaults to active if not specified.")
class GetQueryListingStatusRequest(StrictModel):
    """Retrieve a list of active or delisted US stocks and ETFs as of a specific date or the latest trading day, enabling equity research on asset lifecycle and survivorship."""
    query: GetQueryListingStatusRequestQuery

# Operation: list_earnings_calendar
class GetQueryEarningsCalendarRequestQuery(StrictModel):
    function: Literal["EARNINGS_CALENDAR"] = Field(default=..., description="The function identifier for this operation. Must be set to EARNINGS_CALENDAR.")
    symbol: str | None = Field(default=None, description="Optional company stock symbol to filter results for a specific company. When omitted, returns earnings data for all companies.")
    horizon: Literal["3month", "6month", "12month"] | None = Field(default=None, description="Time horizon for the earnings forecast. Choose from 3 months, 6 months, or 12 months. Defaults to 3 months if not specified.")
class GetQueryEarningsCalendarRequest(StrictModel):
    """Retrieve expected earnings release dates for companies over a specified time horizon. Filter by a specific company symbol or view the full market earnings calendar."""
    query: GetQueryEarningsCalendarRequestQuery

# Operation: list_ipo_calendar
class GetQueryIpoCalendarRequestQuery(StrictModel):
    function: Literal["IPO_CALENDAR"] = Field(default=..., description="The API function to invoke. Must be set to IPO_CALENDAR to retrieve IPO calendar data.")
class GetQueryIpoCalendarRequest(StrictModel):
    """Retrieve a list of upcoming IPO events scheduled in the US market over the next 3 months."""
    query: GetQueryIpoCalendarRequestQuery

# Operation: get_exchange_rate
class GetQueryCurrencyExchangeRateRequestQuery(StrictModel):
    function: Literal["CURRENCY_EXCHANGE_RATE"] = Field(default=..., description="The function identifier for this operation; must be set to CURRENCY_EXCHANGE_RATE.")
    from_currency: str = Field(default=..., description="The source currency code (e.g., BTC for Bitcoin, USD for US Dollar). Accepts both cryptocurrency and fiat currency codes.")
    to_currency: str = Field(default=..., description="The target currency code (e.g., EUR for Euro, BTC for Bitcoin). Accepts both cryptocurrency and fiat currency codes.")
class GetQueryCurrencyExchangeRateRequest(StrictModel):
    """Retrieves the current exchange rate between two currencies, supporting both cryptocurrencies (e.g., BTC) and fiat currencies (e.g., USD, EUR)."""
    query: GetQueryCurrencyExchangeRateRequestQuery

# Operation: get_forex_intraday
class GetQueryFxIntradayRequestQuery(StrictModel):
    function: Literal["FX_INTRADAY"] = Field(default=..., description="The time series function type; must be set to FX_INTRADAY for forex intraday data.")
    from_symbol: str = Field(default=..., description="The three-letter ISO 4217 currency code for the base currency (e.g., EUR, GBP, JPY).", min_length=3, max_length=3)
    to_symbol: str = Field(default=..., description="The three-letter ISO 4217 currency code for the quote currency (e.g., USD, EUR, GBP).", min_length=3, max_length=3)
    interval: Literal["1min", "5min", "15min", "30min", "60min"] = Field(default=..., description="The time interval between consecutive data points; choose from 1-minute, 5-minute, 15-minute, 30-minute, or 60-minute intervals.")
    outputsize: Literal["compact", "full"] | None = Field(default=None, description="Controls the amount of data returned: use 'compact' for the latest 100 data points (default) or 'full' for the complete intraday time series.")
class GetQueryFxIntradayRequest(StrictModel):
    """Retrieves real-time intraday time series data (open, high, low, close prices with timestamps) for a specified forex currency pair at your chosen time interval."""
    query: GetQueryFxIntradayRequestQuery

# Operation: get_fx_daily
class GetQueryFxDailyRequestQuery(StrictModel):
    function: Literal["FX_DAILY"] = Field(default=..., description="The time series function type. Must be set to FX_DAILY for daily forex data.")
    from_symbol: str = Field(default=..., description="The base currency as a three-letter ISO 4217 code (e.g., EUR, GBP, JPY).")
    to_symbol: str = Field(default=..., description="The quote currency as a three-letter ISO 4217 code (e.g., USD, EUR, GBP).")
    outputsize: Literal["compact", "full"] | None = Field(default=None, description="Controls the amount of historical data returned. Use 'compact' for the latest 100 data points (recommended for smaller responses) or 'full' for the complete historical time series. Defaults to compact.")
class GetQueryFxDailyRequest(StrictModel):
    """Retrieve daily forex time series data (open, high, low, close prices) for a specified currency pair, updated in real-time."""
    query: GetQueryFxDailyRequestQuery

# Operation: get_forex_weekly
class GetQueryFxWeeklyRequestQuery(StrictModel):
    function: Literal["FX_WEEKLY"] = Field(default=..., description="The time series function type. Must be set to FX_WEEKLY to retrieve weekly forex data.")
    from_symbol: str = Field(default=..., description="The three-letter ISO 4217 currency code for the base currency (e.g., EUR, GBP, JPY).", min_length=3, max_length=3)
    to_symbol: str = Field(default=..., description="The three-letter ISO 4217 currency code for the quote currency (e.g., USD, EUR, GBP).", min_length=3, max_length=3)
class GetQueryFxWeeklyRequest(StrictModel):
    """Retrieves weekly OHLC (open, high, low, close) time series data for a specified forex currency pair, with real-time updates reflecting the current or partial trading week."""
    query: GetQueryFxWeeklyRequestQuery

# Operation: get_forex_monthly
class GetQueryFxMonthlyRequestQuery(StrictModel):
    function: Literal["FX_MONTHLY"] = Field(default=..., description="The time series function type. Must be set to FX_MONTHLY to retrieve monthly forex data.")
    from_symbol: str = Field(default=..., description="The base currency as a three-letter ISO 4217 code (e.g., EUR, GBP, JPY). This is the currency being converted from.")
    to_symbol: str = Field(default=..., description="The target currency as a three-letter ISO 4217 code (e.g., USD, EUR, GBP). This is the currency being converted to.")
class GetQueryFxMonthlyRequest(StrictModel):
    """Retrieves monthly time series data for a forex currency pair, including open, high, low, and close prices. Data is updated in real-time, with the latest data point representing the current or partial month."""
    query: GetQueryFxMonthlyRequestQuery

# Operation: get_crypto_intraday
class GetQueryCryptoIntradayRequestQuery(StrictModel):
    function: Literal["CRYPTO_INTRADAY"] = Field(default=..., description="The function type for this request. Must be set to CRYPTO_INTRADAY to retrieve intraday cryptocurrency time series data.")
    symbol: str = Field(default=..., description="The cryptocurrency symbol to retrieve data for (e.g., ETH for Ethereum, BTC for Bitcoin). Must be a valid cryptocurrency code from the supported list.")
    market: str = Field(default=..., description="The market currency to trade against (e.g., USD for US Dollar, EUR for Euro). Must be a valid currency code from the supported list.")
    interval: Literal["1min", "5min", "15min", "30min", "60min"] = Field(default=..., description="The time interval between consecutive data points. Choose from 1-minute, 5-minute, 15-minute, 30-minute, or 60-minute intervals.")
    outputsize: Literal["compact", "full"] | None = Field(default=None, description="Controls the amount of data returned. Use 'compact' (default) to get the latest 100 data points for faster responses, or 'full' to retrieve the complete intraday time series.")
class GetQueryCryptoIntradayRequest(StrictModel):
    """Retrieves real-time intraday price data for a cryptocurrency, including open, high, low, close prices and trading volume at specified time intervals."""
    query: GetQueryCryptoIntradayRequestQuery

# Operation: get_cryptocurrency_daily_prices
class GetQueryDigitalCurrencyDailyRequestQuery(StrictModel):
    function: Literal["DIGITAL_CURRENCY_DAILY"] = Field(default=..., description="The API function to invoke. Must be set to DIGITAL_CURRENCY_DAILY to retrieve daily cryptocurrency price history.")
    symbol: str = Field(default=..., description="The cryptocurrency symbol to query (e.g., BTC for Bitcoin). Use any valid cryptocurrency code from the supported currency list.")
    market: str = Field(default=..., description="The target market currency for price conversion (e.g., EUR for Euro). Use any valid fiat or cryptocurrency code from the supported currency list.")
class GetQueryDigitalCurrencyDailyRequest(StrictModel):
    """Retrieves daily historical price and volume data for a cryptocurrency traded against a specific fiat currency. Data is updated daily at midnight UTC and includes prices quoted in both the target market currency and USD."""
    query: GetQueryDigitalCurrencyDailyRequestQuery

# Operation: get_cryptocurrency_weekly_prices
class GetQueryDigitalCurrencyWeeklyRequestQuery(StrictModel):
    function: Literal["DIGITAL_CURRENCY_WEEKLY"] = Field(default=..., description="The API function to invoke. Must be set to DIGITAL_CURRENCY_WEEKLY to retrieve weekly cryptocurrency time series data.")
    symbol: str = Field(default=..., description="The cryptocurrency symbol to query (e.g., BTC for Bitcoin). Use any valid cryptocurrency code from the supported currency list.")
    market: str = Field(default=..., description="The target market currency for price conversion (e.g., EUR for Euro). Use any valid fiat currency code from the supported market list.")
class GetQueryDigitalCurrencyWeeklyRequest(StrictModel):
    """Retrieves weekly historical price and volume data for a cryptocurrency traded against a specified fiat currency. Data is updated daily at midnight UTC and includes prices quoted in both the target market currency and USD."""
    query: GetQueryDigitalCurrencyWeeklyRequestQuery

# Operation: get_cryptocurrency_monthly_history
class GetQueryDigitalCurrencyMonthlyRequestQuery(StrictModel):
    function: Literal["DIGITAL_CURRENCY_MONTHLY"] = Field(default=..., description="The API function to invoke. Must be set to DIGITAL_CURRENCY_MONTHLY to retrieve monthly time series data.")
    symbol: str = Field(default=..., description="The cryptocurrency symbol to query (e.g., BTC for Bitcoin). Must be a valid cryptocurrency code from the supported currency list.")
    market: str = Field(default=..., description="The target market or currency to trade against (e.g., EUR for Euro). Can be any fiat or cryptocurrency code from the supported currency list.")
class GetQueryDigitalCurrencyMonthlyRequest(StrictModel):
    """Retrieves monthly historical price and volume data for a cryptocurrency traded against a specific fiat or crypto market currency. Data is updated daily at midnight UTC and includes prices quoted in both the market currency and USD."""
    query: GetQueryDigitalCurrencyMonthlyRequestQuery

# Operation: get_spot_price
class GetQueryGoldSilverSpotRequestQuery(StrictModel):
    function: Literal["GOLD_SILVER_SPOT"] = Field(default=..., description="The API function to invoke; must be set to GOLD_SILVER_SPOT to retrieve precious metal spot prices.")
    symbol: Literal["GOLD", "XAU", "SILVER", "XAG"] = Field(default=..., description="The precious metal symbol to query: use GOLD or XAU for gold prices, or SILVER or XAG for silver prices.")
class GetQueryGoldSilverSpotRequest(StrictModel):
    """Retrieves the current live spot price for gold or silver in real-time market data."""
    query: GetQueryGoldSilverSpotRequestQuery

# Operation: get_precious_metal_history
class GetQueryGoldSilverHistoryRequestQuery(StrictModel):
    function: Literal["GOLD_SILVER_HISTORY"] = Field(default=..., description="The API function to invoke. Must be set to GOLD_SILVER_HISTORY to retrieve precious metal historical data.")
    symbol: Literal["GOLD", "XAU", "SILVER", "XAG"] = Field(default=..., description="The precious metal to query. Use GOLD or XAU for gold prices, or SILVER or XAG for silver prices.")
    interval: Literal["daily", "weekly", "monthly"] = Field(default=..., description="The time interval for historical data aggregation. Choose from daily, weekly, or monthly price snapshots.")
class GetQueryGoldSilverHistoryRequest(StrictModel):
    """Retrieves historical price data for gold or silver across multiple time horizons (daily, weekly, or monthly intervals)."""
    query: GetQueryGoldSilverHistoryRequestQuery

# Operation: get_wti_crude_oil_prices
class GetQueryWtiRequestQuery(StrictModel):
    function: Literal["WTI"] = Field(default=..., description="The data function to retrieve. Must be set to WTI to fetch West Texas Intermediate crude oil prices.")
    interval: Literal["daily", "weekly", "monthly"] | None = Field(default=None, description="The time interval for price data aggregation. Choose from daily, weekly, or monthly granularity. Defaults to monthly if not specified.")
class GetQueryWtiRequest(StrictModel):
    """Retrieves West Texas Intermediate (WTI) crude oil prices from the U.S. Energy Information Administration. Supports daily, weekly, and monthly price data sourced from FRED (Federal Reserve Bank of St. Louis)."""
    query: GetQueryWtiRequestQuery

# Operation: get_brent_crude_oil_prices
class GetQueryBrentRequestQuery(StrictModel):
    function: Literal["BRENT"] = Field(default=..., description="The data source identifier. Must be set to BRENT to retrieve Brent crude oil prices.")
    interval: Literal["daily", "weekly", "monthly"] | None = Field(default=None, description="The time interval for price data. Choose from daily, weekly, or monthly granularity. Defaults to monthly if not specified.")
class GetQueryBrentRequest(StrictModel):
    """Retrieves Brent (Europe) crude oil prices from the U.S. Energy Information Administration via FRED. Data is available in daily, weekly, or monthly intervals."""
    query: GetQueryBrentRequestQuery

# Operation: get_natural_gas_prices
class GetQueryNaturalGasRequestQuery(StrictModel):
    function: Literal["NATURAL_GAS"] = Field(default=..., description="Specifies the data type to retrieve. Must be set to NATURAL_GAS to fetch Henry Hub natural gas spot prices.")
    interval: Literal["daily", "weekly", "monthly"] | None = Field(default=None, description="Time interval for price data aggregation. Choose from daily, weekly, or monthly granularity. Defaults to monthly if not specified.")
class GetQueryNaturalGasRequest(StrictModel):
    """Retrieves Henry Hub natural gas spot prices from the U.S. Energy Information Administration. Supports daily, weekly, and monthly price data sourced from the Federal Reserve Bank of St. Louis."""
    query: GetQueryNaturalGasRequestQuery

# Operation: get_copper_prices
class GetQueryCopperRequestQuery(StrictModel):
    function: Literal["COPPER"] = Field(default=..., description="The commodity type to query. Must be set to COPPER to retrieve copper price data.")
    interval: Literal["monthly", "quarterly", "annual"] | None = Field(default=None, description="The time interval for price data aggregation. Choose from monthly (default), quarterly, or annual intervals to match your analysis needs.")
class GetQueryCopperRequest(StrictModel):
    """Retrieves global copper prices from the International Monetary Fund (IMF) via the Federal Reserve Economic Data (FRED) service, available in monthly, quarterly, or annual time intervals."""
    query: GetQueryCopperRequestQuery

# Operation: get_aluminum_prices
class GetQueryAluminumRequestQuery(StrictModel):
    function: Literal["ALUMINUM"] = Field(default=..., description="Specifies the commodity type to query. Must be set to ALUMINUM to retrieve aluminum price data.")
    interval: Literal["monthly", "quarterly", "annual"] | None = Field(default=None, description="Time interval for the price data. Accepts monthly (default), quarterly, or annual aggregations.")
class GetQueryAluminumRequest(StrictModel):
    """Retrieves global aluminum prices from the International Monetary Fund via the Federal Reserve Economic Data (FRED) service, available in monthly, quarterly, or annual time intervals."""
    query: GetQueryAluminumRequestQuery

# Operation: get_wheat_price
class GetQueryWheatRequestQuery(StrictModel):
    function: Literal["WHEAT"] = Field(default=..., description="The commodity type to query. Must be set to WHEAT for this operation.")
    interval: Literal["monthly", "quarterly", "annual"] | None = Field(default=None, description="The time interval for the price data. Choose from monthly (default), quarterly, or annual aggregations.")
class GetQueryWheatRequest(StrictModel):
    """Retrieve global wheat prices from the International Monetary Fund (IMF) via FRED. Data is available in monthly, quarterly, or annual intervals."""
    query: GetQueryWheatRequestQuery

# Operation: get_corn_prices
class GetQueryCornRequestQuery(StrictModel):
    function: Literal["CORN"] = Field(default=..., description="The commodity type to query. Must be set to CORN to retrieve corn price data.")
    interval: Literal["monthly", "quarterly", "annual"] | None = Field(default=None, description="The time interval for price data aggregation. Choose from monthly (default), quarterly, or annual intervals.")
class GetQueryCornRequest(StrictModel):
    """Retrieves global corn prices from the International Monetary Fund (IMF) via FRED (Federal Reserve Bank of St. Louis) in your choice of monthly, quarterly, or annual time intervals."""
    query: GetQueryCornRequestQuery

# Operation: get_cotton_prices
class GetQueryCottonRequestQuery(StrictModel):
    function: Literal["COTTON"] = Field(default=..., description="Specifies the commodity data to retrieve. Must be set to COTTON to fetch cotton price data.")
    interval: Literal["monthly", "quarterly", "annual"] | None = Field(default=None, description="Specifies the time interval for the price data. Choose from monthly (default), quarterly, or annual aggregations.")
class GetQueryCottonRequest(StrictModel):
    """Retrieves global cotton prices from the International Monetary Fund via the Federal Reserve Economic Data (FRED) service, available in monthly, quarterly, or annual time intervals."""
    query: GetQueryCottonRequestQuery

# Operation: get_sugar_prices
class GetQuerySugarRequestQuery(StrictModel):
    function: Literal["SUGAR"] = Field(default=..., description="The commodity type to query. Must be set to SUGAR for sugar price data.")
    interval: Literal["monthly", "quarterly", "annual"] | None = Field(default=None, description="The time interval for price data aggregation. Choose from monthly, quarterly, or annual intervals. Defaults to monthly if not specified.")
class GetQuerySugarRequest(StrictModel):
    """Retrieves global sugar prices from the International Monetary Fund (IMF) across different time horizons. Data is sourced from the Federal Reserve Bank of St. Louis FRED database."""
    query: GetQuerySugarRequestQuery

# Operation: get_coffee_prices
class GetQueryCoffeeRequestQuery(StrictModel):
    function: Literal["COFFEE"] = Field(default=..., description="Specifies the commodity type to query. Must be set to COFFEE to retrieve coffee price data.")
    interval: Literal["monthly", "quarterly", "annual"] | None = Field(default=None, description="Defines the time period aggregation for price data. Accepts monthly, quarterly, or annual intervals, with monthly as the default.")
class GetQueryCoffeeRequest(StrictModel):
    """Retrieves global coffee prices from the International Monetary Fund (IMF) across different time horizons. Data represents the global price of Other Mild Arabica coffee sourced from the Federal Reserve Bank of St. Louis."""
    query: GetQueryCoffeeRequestQuery

# Operation: get_commodity_price_index
class GetQueryAllCommoditiesRequestQuery(StrictModel):
    function: Literal["ALL_COMMODITIES"] = Field(default=..., description="Specifies the commodity dataset to retrieve. Must be set to ALL_COMMODITIES to fetch the global price index for all commodities.")
    interval: Literal["monthly", "quarterly", "annual"] | None = Field(default=None, description="Defines the time period granularity for the price index data. Accepts monthly (default), quarterly, or annual intervals.")
class GetQueryAllCommoditiesRequest(StrictModel):
    """Retrieves the global price index for all commodities across different time periods. Data is sourced from the International Monetary Fund (IMF) Global Price Index and provided by the Federal Reserve Bank of St. Louis."""
    query: GetQueryAllCommoditiesRequestQuery

# Operation: get_real_gdp
class GetQueryRealGdpRequestQuery(StrictModel):
    function: Literal["REAL_GDP"] = Field(default=..., description="The data function to retrieve; must be set to REAL_GDP to fetch Real Gross Domestic Product data.")
    interval: Literal["annual", "quarterly"] | None = Field(default=None, description="The time interval for the data; choose either annual or quarterly frequency. Defaults to annual if not specified.")
class GetQueryRealGdpRequest(StrictModel):
    """Retrieves annual or quarterly Real Gross Domestic Product data for the United States from the Federal Reserve Economic Data (FRED) database, sourced from the U.S. Bureau of Economic Analysis."""
    query: GetQueryRealGdpRequestQuery

# Operation: get_real_gdp_per_capita
class GetQueryRealGdpPerCapitaRequestQuery(StrictModel):
    function: Literal["REAL_GDP_PER_CAPITA"] = Field(default=..., description="The data function to retrieve; must be set to REAL_GDP_PER_CAPITA to fetch quarterly Real GDP per Capita metrics.")
class GetQueryRealGdpPerCapitaRequest(StrictModel):
    """Retrieves quarterly Real GDP per Capita data for the United States from the Federal Reserve Economic Data (FRED) database, sourced from the U.S. Bureau of Economic Analysis."""
    query: GetQueryRealGdpPerCapitaRequestQuery

# Operation: fetch_treasury_yield
class GetQueryTreasuryYieldRequestQuery(StrictModel):
    function: Literal["TREASURY_YIELD"] = Field(default=..., description="The data function to execute. Must be set to TREASURY_YIELD to retrieve Treasury yield data.")
    interval: Literal["daily", "weekly", "monthly"] | None = Field(default=None, description="The time interval for data points. Choose from daily, weekly, or monthly granularity. Defaults to monthly if not specified.")
    maturity: Literal["3month", "2year", "5year", "7year", "10year", "30year"] | None = Field(default=None, description="The maturity timeline of the Treasury security. Select from 3-month, 2-year, 5-year, 7-year, 10-year, or 30-year constant maturities. Defaults to 10-year if not specified.")
class GetQueryTreasuryYieldRequest(StrictModel):
    """Retrieves US Treasury yield data for a specified maturity timeline at daily, weekly, or monthly intervals. Data sourced from the Federal Reserve's official market yield on constant maturity securities."""
    query: GetQueryTreasuryYieldRequestQuery

# Operation: get_federal_funds_rate
class GetQueryFederalFundsRateRequestQuery(StrictModel):
    function: Literal["FEDERAL_FUNDS_RATE"] = Field(default=..., description="The data function to retrieve; must be set to FEDERAL_FUNDS_RATE to fetch federal funds rate data.")
    interval: Literal["daily", "weekly", "monthly"] | None = Field(default=None, description="The time interval for the data: daily for individual trading days, weekly for week-over-week rates, or monthly for month-over-month rates. Defaults to monthly if not specified.")
class GetQueryFederalFundsRateRequest(StrictModel):
    """Retrieves the current federal funds rate (interest rate) set by the United States Federal Reserve. Data is available at daily, weekly, or monthly intervals and sourced from the Federal Reserve Bank of St. Louis."""
    query: GetQueryFederalFundsRateRequestQuery

# Operation: get_cpi_data
class GetQueryCpiRequestQuery(StrictModel):
    function: Literal["CPI"] = Field(default=..., description="The data type to retrieve; must be set to CPI for Consumer Price Index data.")
    interval: Literal["monthly", "semiannual"] | None = Field(default=None, description="The reporting frequency for CPI data; choose either monthly (default) for month-over-month data or semiannual for six-month intervals.")
class GetQueryCpiRequest(StrictModel):
    """Retrieves monthly or semiannual Consumer Price Index (CPI) data for the United States, which measures inflation levels across the broader economy."""
    query: GetQueryCpiRequestQuery

# Operation: get_inflation_rates
class GetQueryInflationRequestQuery(StrictModel):
    function: Literal["INFLATION"] = Field(default=..., description="Specifies the data function to retrieve; must be set to INFLATION to fetch annual consumer price inflation rates.")
class GetQueryInflationRequest(StrictModel):
    """Retrieves annual inflation rates based on consumer prices for the United States, sourced from the Federal Reserve Economic Data (FRED) database via the World Bank."""
    query: GetQueryInflationRequestQuery

# Operation: get_retail_sales
class GetQueryRetailSalesRequestQuery(StrictModel):
    function: Literal["RETAIL_SALES"] = Field(default=..., description="The data function to retrieve; must be set to RETAIL_SALES to fetch monthly retail trade sales data.")
class GetQueryRetailSalesRequest(StrictModel):
    """Retrieves monthly Advance Retail Sales data for the United States from the U.S. Census Bureau, sourced through the Federal Reserve Economic Data (FRED) system."""
    query: GetQueryRetailSalesRequestQuery

# Operation: get_durable_goods_orders
class GetQueryDurablesRequestQuery(StrictModel):
    function: Literal["DURABLES"] = Field(default=..., description="The data function to retrieve; must be set to DURABLES to fetch durable goods orders data.")
class GetQueryDurablesRequest(StrictModel):
    """Retrieves monthly data on manufacturers' new orders for durable goods in the United States, sourced from the U.S. Census Bureau via the Federal Reserve Economic Data (FRED) database."""
    query: GetQueryDurablesRequestQuery

# Operation: get_unemployment_rate
class GetQueryUnemploymentRequestQuery(StrictModel):
    function: Literal["UNEMPLOYMENT"] = Field(default=..., description="Specifies the data function to retrieve; must be set to UNEMPLOYMENT to fetch unemployment rate data.")
class GetQueryUnemploymentRequest(StrictModel):
    """Retrieves the monthly unemployment rate for the United States, showing the percentage of unemployed individuals within the labor force. Data covers the civilian population aged 16 and older residing in the 50 states or District of Columbia."""
    query: GetQueryUnemploymentRequestQuery

# Operation: get_nonfarm_payroll
class GetQueryNonfarmPayrollRequestQuery(StrictModel):
    function: Literal["NONFARM_PAYROLL"] = Field(default=..., description="The data function to retrieve; must be set to NONFARM_PAYROLL to fetch monthly nonfarm payroll employment data.")
class GetQueryNonfarmPayrollRequest(StrictModel):
    """Retrieves monthly US nonfarm payroll employment figures from the Bureau of Labor Statistics, representing the total number of employed workers in the economy excluding farm workers, proprietors, and self-employed individuals."""
    query: GetQueryNonfarmPayrollRequestQuery

# Operation: calculate_sma
class GetQuerySmaRequestQuery(StrictModel):
    function: Literal["SMA"] = Field(default=..., description="The technical indicator function to use. Must be set to SMA for simple moving average calculations.")
    symbol: str = Field(default=..., description="The ticker symbol of the equity or currency pair (e.g., IBM, AAPL, EUR/USD).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from minute-level intervals (1, 5, 15, 30, 60 minutes) or daily/weekly/monthly aggregations.")
    time_period: int = Field(default=..., description="The number of data points used to calculate each moving average value. Must be at least 1. Larger values produce smoother averages over longer periods.", ge=1)
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations: open (opening price), close (closing price), high (highest price), or low (lowest price) for each interval.")
    month: str | None = Field(default=None, description="Optional. Retrieve SMA values for a specific month in history using YYYY-MM format (e.g., 2009-01). If omitted, calculations use the default historical data length for the selected interval.", pattern='^\\d{4}-\\d{2}$')
class GetQuerySmaRequest(StrictModel):
    """Calculates the simple moving average (SMA) for a given equity or currency pair over a specified time interval and period. Returns SMA values based on your chosen price type (open, close, high, or low)."""
    query: GetQuerySmaRequestQuery

# Operation: calculate_ema
class GetQueryEmaRequestQuery(StrictModel):
    function: Literal["EMA"] = Field(default=..., description="The technical indicator type. Must be set to EMA for exponential moving average calculations.")
    symbol: str = Field(default=..., description="The ticker symbol of the equity or currency pair to analyze (e.g., IBM, AAPL, EUR/USD).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from minute-level intervals (1, 5, 15, 30, 60 minutes) or longer periods (daily, weekly, monthly).")
    time_period: int = Field(default=..., description="The number of data points used to calculate each EMA value. Must be a positive integer of at least 1.", ge=1)
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations. Select from closing price, opening price, high price, or low price for each interval.")
    month: str | None = Field(default=None, description="Optional historical month for calculations in YYYY-MM format (e.g., 2009-01). If omitted, uses the default length of the underlying time series data.", pattern='^\\d{4}-\\d{2}$')
class GetQueryEmaRequest(StrictModel):
    """Calculates exponential moving average (EMA) values for a given equity or currency pair over a specified time interval and period."""
    query: GetQueryEmaRequestQuery

# Operation: calculate_weighted_moving_average
class GetQueryWmaRequestQuery(StrictModel):
    function: Literal["WMA"] = Field(default=..., description="The technical indicator function to apply. Must be WMA (Weighted Moving Average).")
    symbol: str = Field(default=..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL). Case-insensitive.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points in the returned series. Choose from minute-level intervals (1, 5, 15, 30, 60 minutes) or daily/weekly/monthly aggregations.")
    time_period: int = Field(default=..., description="The number of data points used to calculate each WMA value. Must be a positive integer of at least 1. Larger values produce smoother averages over longer periods.", ge=1)
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations. Select from closing price, opening price, high price, or low price for each interval.")
    month: str | None = Field(default=None, description="Optional: Retrieve historical WMA data for a specific month in YYYY-MM format (e.g., 2009-01). Omit to get the most recent data.")
class GetQueryWmaRequest(StrictModel):
    """Calculates weighted moving average (WMA) values for a given equity symbol across specified time intervals. Returns a time series of WMA data points based on your chosen price type and lookback period."""
    query: GetQueryWmaRequestQuery

# Operation: calculate_dema
class GetQueryDemaRequestQuery(StrictModel):
    function: Literal["DEMA"] = Field(default=..., description="The technical indicator type; must be set to DEMA for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol (e.g., IBM) for which to calculate the moving average.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points: 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly.")
    time_period: int = Field(default=..., description="The number of data points used in each moving average calculation; determines the sensitivity and smoothing of the DEMA values.")
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations: closing price, opening price, high price, or low price for the interval.")
    month: str | None = Field(default=None, description="Optional historical month for retrieving past DEMA values, specified in YYYY-MM format (e.g., 2009-01). Omit to get current data.")
class GetQueryDemaRequest(StrictModel):
    """Calculates the double exponential moving average (DEMA) for a given equity symbol, providing smoothed price trend analysis across various time intervals and historical periods."""
    query: GetQueryDemaRequestQuery

# Operation: calculate_tema
class GetQueryTemaRequestQuery(StrictModel):
    function: Literal["TEMA"] = Field(default=..., description="The technical indicator type; must be set to TEMA for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points, ranging from 1-minute intraday data to monthly historical data.")
    time_period: int = Field(default=..., description="The number of data points used to calculate each TEMA value; must be at least 1. Larger values produce smoother averages.", ge=1)
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations: closing price, opening price, high price, or low price for the interval.")
    month: str | None = Field(default=None, description="Optional historical month filter in YYYY-MM format to retrieve TEMA values for a specific month. If omitted, calculations use the default time series length.", pattern='^\\d{4}-\\d{2}$')
class GetQueryTemaRequest(StrictModel):
    """Calculates the Triple Exponential Moving Average (TEMA) for a given equity symbol, providing smoothed price trend analysis across various time intervals."""
    query: GetQueryTemaRequestQuery

# Operation: calculate_triangular_moving_average
class GetQueryTrimaRequestQuery(StrictModel):
    function: Literal["TRIMA"] = Field(default=..., description="The technical indicator type. Must be set to TRIMA for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from intraday intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly historical data.")
    time_period: int = Field(default=..., description="The number of data points used to calculate each TRIMA value. Must be a positive integer (minimum 1). Larger values produce smoother averages.", ge=1)
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations. Select from closing, opening, high, or low prices for each interval.")
    month: str | None = Field(default=None, description="Optional historical month to retrieve data for, specified in YYYY-MM format. If omitted, returns the most recent data based on the default time range.")
class GetQueryTrimaRequest(StrictModel):
    """Calculates the triangular moving average (TRIMA) for a given equity symbol across specified time intervals. TRIMA is a double-smoothed moving average that emphasizes mid-range price data."""
    query: GetQueryTrimaRequestQuery

# Operation: calculate_kama
class GetQueryKamaRequestQuery(StrictModel):
    function: Literal["KAMA"] = Field(default=..., description="The technical indicator type. Must be set to KAMA for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points. Choose from intraday intervals (1, 5, 15, or 30 minutes, or 1 hour) or longer periods (daily, weekly, or monthly).")
    time_period: int = Field(default=..., description="The number of periods used to calculate each KAMA value. Must be at least 1; larger values produce smoother averages.", ge=1)
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations. Select from closing, opening, high, or low prices.")
    month: str | None = Field(default=None, description="Optional historical month for the calculation in YYYY-MM format. If not specified, the indicator uses the default time series length for the selected interval.", json_schema_extra={'format': 'date'})
class GetQueryKamaRequest(StrictModel):
    """Calculates the Kaufman Adaptive Moving Average (KAMA) for a given equity symbol, providing adaptive trend-following values that adjust to market volatility and noise."""
    query: GetQueryKamaRequestQuery

# Operation: get_mama_indicator
class GetQueryMamaRequestQuery(StrictModel):
    function: Literal["MAMA"] = Field(default=..., description="The technical indicator type; must be set to MAMA for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points: 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly.")
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations: closing price, opening price, high price, or low price.")
    month: str | None = Field(default=None, description="Optional historical month for the calculation in YYYY-MM format. If omitted, uses the default length of the underlying time series data.")
    fastlimit: float | None = Field(default=None, description="Optional fast limit parameter controlling the upper bound of the adaptive moving average acceleration. Accepts positive decimal values; defaults to 0.01.")
    slowlimit: float | None = Field(default=None, description="Optional slow limit parameter controlling the lower bound of the adaptive moving average acceleration. Accepts positive decimal values; defaults to 0.01.")
class GetQueryMamaRequest(StrictModel):
    """Retrieves MESA adaptive moving average (MAMA) values for a specified equity, allowing analysis of trend direction and momentum across multiple timeframes and price types."""
    query: GetQueryMamaRequestQuery

# Operation: calculate_vwap
class GetQueryVwapRequestQuery(StrictModel):
    function: Literal["VWAP"] = Field(default=..., description="The technical indicator type; must be set to VWAP for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol (e.g., IBM) for which to calculate VWAP.")
    interval: Literal["1min", "5min", "15min", "30min", "60min"] = Field(default=..., description="The time interval between consecutive data points in the intraday series; choose from 1-minute, 5-minute, 15-minute, 30-minute, or 60-minute intervals.")
    month: str | None = Field(default=None, description="Optional historical month to retrieve VWAP data for; specify in YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data.")
class GetQueryVwapRequest(StrictModel):
    """Calculate the volume weighted average price (VWAP) for intraday time series data of a given equity, helping identify fair value and trend direction based on price and volume."""
    query: GetQueryVwapRequestQuery

# Operation: calculate_t3_moving_average
class GetQueryT3RequestQuery(StrictModel):
    function: Literal["T3"] = Field(default=..., description="The technical indicator type. Must be set to T3 for Tilson triple exponential moving average calculations.")
    symbol: str = Field(default=..., description="The equity ticker symbol (e.g., IBM, AAPL) for which to calculate the moving average.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points in the series. Choose from 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly intervals.")
    time_period: int = Field(default=..., description="The number of data points used to calculate each moving average value. Must be a positive integer of at least 1.", ge=1)
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations. Select from closing price, opening price, high price, or low price for each interval.")
    month: str | None = Field(default=None, description="Optional. Retrieve historical technical indicator data for a specific month. Specify the month in YYYY-MM format (e.g., 2009-01).")
class GetQueryT3Request(StrictModel):
    """Calculates the Tilson T3 triple exponential moving average for a given equity symbol. Returns smoothed price data based on your specified time interval and period."""
    query: GetQueryT3RequestQuery

# Operation: calculate_macd
class GetQueryMacdRequestQuery(StrictModel):
    function: Literal["MACD"] = Field(default=..., description="The technical indicator type; must be set to MACD for this operation.")
    symbol: str = Field(default=..., description="The ticker symbol of the equity or forex pair to analyze (e.g., IBM, EURUSD).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points in the time series. Choose from minute-level intervals (1, 5, 15, or 30 minutes), hourly (60 minutes), or daily/weekly/monthly aggregations.")
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use for calculations: closing price, opening price, high price, or low price for each interval.")
    month: str | None = Field(default=None, description="Optional historical month to retrieve data for, specified in YYYY-MM format. If omitted, returns the most recent data available.", json_schema_extra={'format': 'date'})
    fastperiod: int | None = Field(default=None, description="The number of periods for the fast exponential moving average. Must be a positive integer; defaults to 12 if not specified.", ge=1)
    slowperiod: int | None = Field(default=None, description="The number of periods for the slow exponential moving average. Must be a positive integer; defaults to 26 if not specified.", ge=1)
    signalperiod: int | None = Field(default=None, description="The number of periods for the signal line exponential moving average. Must be a positive integer; defaults to 9 if not specified.", ge=1)
class GetQueryMacdRequest(StrictModel):
    """Calculates Moving Average Convergence/Divergence (MACD) technical indicator values for a given equity or forex pair, returning MACD line, signal line, and histogram data across specified time intervals."""
    query: GetQueryMacdRequestQuery

# Operation: calculate_macd_extended
class GetQueryMacdextRequestQuery(StrictModel):
    function: Literal["MACDEXT"] = Field(default=..., description="The technical indicator function to execute. Must be set to MACDEXT for extended MACD calculation with configurable moving average types.")
    symbol: str = Field(default=..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL). Case-insensitive.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points. Choose from minute-level intervals (1, 5, 15, 30, 60 minutes) or daily/weekly/monthly aggregations.")
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations: closing price, opening price, high price, or low price for the interval.")
    month: str | None = Field(default=None, description="Optional historical month for backtesting in YYYY-MM format (e.g., 2009-01). If omitted, uses the most recent available data.", json_schema_extra={'format': 'date'})
    fastperiod: int | None = Field(default=None, description="The number of periods for the fast-moving average. Must be a positive integer; defaults to 12 if not specified.", ge=1)
    slowperiod: int | None = Field(default=None, description="The number of periods for the slow-moving average. Must be a positive integer; defaults to 26 if not specified.", ge=1)
    signalperiod: int | None = Field(default=None, description="The number of periods for the signal line (exponential moving average of MACD). Must be a positive integer; defaults to 9 if not specified.", ge=1)
class GetQueryMacdextRequest(StrictModel):
    """Calculate MACD (Moving Average Convergence Divergence) with customizable moving average types for technical analysis of equity price movements. Returns MACD line, signal line, and histogram values."""
    query: GetQueryMacdextRequestQuery

# Operation: get_stochastic_oscillator
class GetQueryStochRequestQuery(StrictModel):
    function: Literal["STOCH"] = Field(default=..., description="The technical indicator type. Must be set to STOCH for stochastic oscillator calculations.")
    symbol: str = Field(default=..., description="The ticker symbol of the equity or forex pair to analyze (e.g., IBM, EURUSD).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points. Choose from: 1min, 5min, 15min, 30min, 60min for intraday data, or daily, weekly, monthly for longer-term analysis.")
    month: str | None = Field(default=None, description="Optional historical month for the calculation in YYYY-MM format. If not specified, the indicator is calculated on the default time series data for the selected interval.", json_schema_extra={'format': 'date'})
    slowkperiod: int | None = Field(default=None, description="The number of periods for the slow K moving average smoothing. Must be a positive integer; defaults to 3 if not specified.", ge=1)
    slowdperiod: int | None = Field(default=None, description="The number of periods for the slow D moving average smoothing. Must be a positive integer; defaults to 3 if not specified.", ge=1)
class GetQueryStochRequest(StrictModel):
    """Retrieves stochastic oscillator (STOCH) technical indicator values for a specified equity or forex pair at a given time interval. The stochastic oscillator measures momentum by comparing closing prices to price ranges over a defined period."""
    query: GetQueryStochRequestQuery

# Operation: get_stochastic_fast_indicator
class GetQueryStochfRequestQuery(StrictModel):
    function: Literal["STOCHF"] = Field(default=..., description="The technical indicator type. Must be set to STOCHF for this operation.")
    symbol: str = Field(default=..., description="The equity ticker symbol (e.g., IBM, AAPL). Used to identify the security for which to calculate the indicator.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points. Supported intervals range from 1-minute to monthly granularity, allowing analysis across intraday and longer-term timeframes.")
    month: str | None = Field(default=None, description="Optional historical month for calculation in YYYY-MM format (e.g., 2009-01). When omitted, the indicator is calculated using the default length of the underlying time series data.")
class GetQueryStochfRequest(StrictModel):
    """Retrieves stochastic fast (STOCHF) technical indicator values for a given equity symbol. The STOCHF oscillator measures momentum by comparing closing prices to price ranges over a specified period."""
    query: GetQueryStochfRequestQuery

# Operation: calculate_rsi
class GetQueryRsiRequestQuery(StrictModel):
    function: Literal["RSI"] = Field(default=..., description="The technical indicator type. Must be set to RSI for this operation.")
    symbol: str = Field(default=..., description="The ticker symbol of the equity or forex pair to analyze (e.g., IBM, AAPL, EUR/USD).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from: 1min, 5min, 15min, 30min, 60min, daily, weekly, or monthly.")
    time_period: int = Field(default=..., description="The number of data points used to calculate each RSI value. Must be a positive integer (e.g., 10, 14, 60, 200).", ge=1)
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations. Choose from: close, open, high, or low.")
    month: str | None = Field(default=None, description="Optional historical month for which to calculate RSI values, specified in YYYY-MM format (e.g., 2009-01). If omitted, uses the default time series data.", json_schema_extra={'format': 'date'})
class GetQueryRsiRequest(StrictModel):
    """Calculates the Relative Strength Index (RSI) technical indicator for a given equity or forex pair over a specified time period and interval."""
    query: GetQueryRsiRequestQuery

# Operation: calculate_stochrsi
class GetQueryStochrsiRequestQuery(StrictModel):
    function: Literal["STOCHRSI"] = Field(default=..., description="The technical indicator type. Must be set to STOCHRSI for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points. Choose from intraday intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly historical data.")
    time_period: int = Field(default=..., description="The number of periods used to calculate each STOCHRSI value. Must be a positive integer (e.g., 10, 14, 21).")
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations. Select from closing, opening, high, or low prices.")
    month: str | None = Field(default=None, description="Optional. Retrieve STOCHRSI values for a specific month in history using YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data.")
class GetQueryStochrsiRequest(StrictModel):
    """Calculate the Stochastic Relative Strength Index (STOCHRSI) for a given equity symbol. Returns STOCHRSI values at your specified time interval and lookback period."""
    query: GetQueryStochrsiRequestQuery

# Operation: get_williams_percent_r
class GetQueryWillrRequestQuery(StrictModel):
    function: Literal["WILLR"] = Field(default=..., description="The technical indicator type. Must be set to WILLR for Williams' %R calculation.")
    symbol: str = Field(default=..., description="The equity ticker symbol (e.g., IBM, AAPL). Used to identify which security to analyze.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from minute-level intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly aggregations.")
    time_period: int = Field(default=..., description="The number of periods used in the WILLR calculation. Must be a positive integer (e.g., 60 for a 60-period lookback window).", ge=1)
    month: str | None = Field(default=None, description="Optional filter to retrieve historical WILLR values for a specific month in YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data.", json_schema_extra={'format': 'date'})
class GetQueryWillrRequest(StrictModel):
    """Retrieves Williams' %R (WILLR) momentum oscillator values for a given equity symbol. This technical indicator measures the level of the closing price relative to the highest high over a specified period, helping identify overbought and oversold conditions."""
    query: GetQueryWillrRequestQuery

# Operation: calculate_adx
class GetQueryAdxRequestQuery(StrictModel):
    function: Literal["ADX"] = Field(default=..., description="The technical indicator type; must be set to ADX for this operation.")
    symbol: str = Field(default=..., description="The ticker symbol of the equity or forex pair (e.g., IBM, EURUSD).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points: 1min, 5min, 15min, 30min, 60min for intraday data, or daily, weekly, monthly for longer-term analysis.")
    time_period: int = Field(default=..., description="The number of periods used to calculate each ADX value; must be a positive integer (e.g., 10, 14, 60, 200).", ge=1)
    month: str | None = Field(default=None, description="Optional historical month filter in YYYY-MM format (e.g., 2009-01) to retrieve ADX values for a specific month; if omitted, uses the default time series length for the selected interval.", pattern='^\\d{4}-\\d{2}$')
class GetQueryAdxRequest(StrictModel):
    """Calculates the Average Directional Movement Index (ADX) for a given equity or forex pair, returning trend strength values across your specified time interval and period."""
    query: GetQueryAdxRequestQuery

# Operation: get_adxr_values
class GetQueryAdxrRequestQuery(StrictModel):
    function: Literal["ADXR"] = Field(default=..., description="The technical indicator type; must be set to ADXR for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to retrieve ADXR values.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points, ranging from 1-minute to monthly granularity.")
    time_period: int = Field(default=..., description="The number of data points used to calculate each ADXR value; must be at least 1.", ge=1)
    month: str | None = Field(default=None, description="Optional historical month to retrieve data from, specified in YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data.")
class GetQueryAdxrRequest(StrictModel):
    """Retrieves Average Directional Movement Index Rating (ADXR) values for a specified equity, providing trend strength analysis over a chosen time interval and historical period."""
    query: GetQueryAdxrRequestQuery

# Operation: calculate_absolute_price_oscillator
class GetQueryApoRequestQuery(StrictModel):
    function: Literal["APO"] = Field(default=..., description="The technical indicator function to calculate. Must be set to APO for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol for which to calculate the APO (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points in the returned series. Choose from minute-level intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly historical data.")
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in the calculation. Select from the open, high, low, or closing price of each interval.")
    fastperiod: int | None = Field(default=None, description="The number of periods for the faster exponential moving average. Accepts any positive integer; defaults to 12 if not specified.")
    slowperiod: int | None = Field(default=None, description="The number of periods for the slower exponential moving average. Accepts any positive integer; defaults to 26 if not specified.")
    month: str | None = Field(default=None, description="Retrieve APO values for a specific month in history using YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data available.")
class GetQueryApoRequest(StrictModel):
    """Calculates the Absolute Price Oscillator (APO) technical indicator for a given equity, measuring momentum by comparing two exponential moving averages. Returns APO values at your specified time interval."""
    query: GetQueryApoRequestQuery

# Operation: calculate_ppo
class GetQueryPpoRequestQuery(StrictModel):
    function: Literal["PPO"] = Field(default=..., description="The technical indicator type. Must be set to PPO for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate the PPO.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from minute-level intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly aggregations.")
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations. Select from open, high, low, or close prices.")
    fastperiod: int | None = Field(default=None, description="The period for the fast exponential moving average. Must be a positive integer; defaults to 12 if not specified.", ge=1)
    slowperiod: int | None = Field(default=None, description="The period for the slow exponential moving average. Must be a positive integer; defaults to 26 if not specified.", ge=1)
    month: str | None = Field(default=None, description="Optional historical month to retrieve PPO values for, specified in YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data.", pattern='^\\d{4}-\\d{2}$')
class GetQueryPpoRequest(StrictModel):
    """Calculates the Percentage Price Oscillator (PPO) for an equity, a momentum indicator that measures the relationship between two exponential moving averages. Returns PPO values across a specified time interval and historical period."""
    query: GetQueryPpoRequestQuery

# Operation: calculate_momentum
class GetQueryMomRequestQuery(StrictModel):
    function: Literal["MOM"] = Field(default=..., description="The technical indicator type. Must be set to MOM for momentum calculations.")
    symbol: str = Field(default=..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from: 1min, 5min, 15min, 30min, 60min for intraday data, or daily, weekly, monthly for longer-term analysis.")
    time_period: int = Field(default=..., description="The number of data points used to calculate each momentum value. Must be a positive integer (e.g., 10, 60, 200). Larger values smooth out short-term fluctuations.", ge=1)
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations. Choose from: close, open, high, or low prices.")
    month: str | None = Field(default=None, description="Optional historical month for analysis in YYYY-MM format (e.g., 2009-01). If not specified, calculations use the default length of available time series data for the selected interval.", json_schema_extra={'format': 'date'})
class GetQueryMomRequest(StrictModel):
    """Calculates momentum (MOM) technical indicator values for a given equity symbol. Returns momentum measurements based on price changes over a specified time period and interval."""
    query: GetQueryMomRequestQuery

# Operation: get_balance_of_power
class GetQueryBopRequestQuery(StrictModel):
    function: Literal["BOP"] = Field(default=..., description="The technical indicator type. Must be set to BOP for Balance of Power calculations.")
    symbol: str = Field(default=..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate the Balance of Power indicator.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from: 1min, 5min, 15min, 30min, 60min for intraday data, or daily, weekly, monthly for longer-term analysis.")
    month: str | None = Field(default=None, description="Optional. Retrieve Balance of Power values for a specific month in history using YYYY-MM format (e.g., 2009-01). If omitted, returns data based on the default time series length for the selected interval.", json_schema_extra={'format': 'date'})
class GetQueryBopRequest(StrictModel):
    """Retrieves Balance of Power (BOP) technical indicator values for a specified equity symbol at your chosen time interval. Optionally filter results to a specific month in history."""
    query: GetQueryBopRequestQuery

# Operation: calculate_commodity_channel_index
class GetQueryCciRequestQuery(StrictModel):
    function: Literal["CCI"] = Field(default=..., description="The technical indicator type. Must be set to CCI for this operation.")
    symbol: str = Field(default=..., description="The ticker symbol of the equity or forex pair to analyze (e.g., IBM, EURUSD).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points in the returned series. Choose from minute-level intervals (1, 5, 15, or 30 minutes), hourly (60 minutes), or daily/weekly/monthly aggregations.")
    time_period: int = Field(default=..., description="The number of data points used to calculate each CCI value. Must be a positive integer of at least 1. Larger values smooth the indicator over longer periods.", ge=1)
    month: str | None = Field(default=None, description="Optional. Retrieve CCI values for a specific month in history using YYYY-MM format (e.g., 2009-01). If omitted, returns data using the default historical length.", json_schema_extra={'format': 'date'})
class GetQueryCciRequest(StrictModel):
    """Calculates the Commodity Channel Index (CCI) technical indicator for a given equity or forex pair, returning CCI values across a specified time series at your chosen interval."""
    query: GetQueryCciRequestQuery

# Operation: calculate_momentum_oscillator
class GetQueryCmoRequestQuery(StrictModel):
    function: Literal["CMO"] = Field(default=..., description="The technical indicator type; must be set to CMO for Chande Momentum Oscillator calculations.")
    symbol: str = Field(default=..., description="The stock ticker symbol for which to calculate the momentum oscillator (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points, ranging from 1-minute intraday data to monthly historical data.")
    time_period: int = Field(default=..., description="The number of data points used in each CMO calculation; must be at least 1. Larger values smooth the oscillator over longer periods.", ge=1)
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use for calculations: closing price, opening price, high price, or low price for each interval.")
    month: str | None = Field(default=None, description="Optional historical month to retrieve CMO values for a specific period in the past, specified in YYYY-MM format.")
class GetQueryCmoRequest(StrictModel):
    """Calculates the Chande Momentum Oscillator (CMO) for a given equity, providing momentum-based technical analysis values across specified time intervals and historical periods."""
    query: GetQueryCmoRequestQuery

# Operation: calculate_equity_roc
class GetQueryRocRequestQuery(StrictModel):
    function: Literal["ROC"] = Field(default=..., description="The technical indicator type. Must be set to ROC for rate of change calculations.")
    symbol: str = Field(default=..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate ROC values.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from intraday intervals (1, 5, 15, 30, or 60 minutes) or longer periods (daily, weekly, or monthly).")
    time_period: int = Field(default=..., description="The number of periods used to calculate each ROC value. Must be a positive integer (e.g., 10 means ROC is calculated over the last 10 periods).")
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations. Choose from closing price, opening price, high price, or low price for each period.")
    month: str | None = Field(default=None, description="Optional. Retrieve historical ROC values for a specific month in YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data based on the selected interval.")
class GetQueryRocRequest(StrictModel):
    """Calculates the rate of change (ROC) technical indicator for an equity, measuring the percentage change in price over a specified period. Returns ROC values at your chosen time interval."""
    query: GetQueryRocRequestQuery

# Operation: calculate_rocr
class GetQueryRocrRequestQuery(StrictModel):
    function: Literal["ROCR"] = Field(default=..., description="The technical indicator type. Must be set to ROCR for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate ROCR values.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points. Choose from intraday intervals (1min, 5min, 15min, 30min, 60min) or longer periods (daily, weekly, monthly).")
    time_period: int = Field(default=..., description="The number of periods to use in the ROCR calculation. Must be a positive integer (e.g., 10, 60, 200). Larger values smooth the indicator over longer timeframes.", ge=1)
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations: closing price, opening price, high price, or low price for each period.")
    month: str | None = Field(default=None, description="Optional. Retrieve ROCR values for a specific month in history using YYYY-MM format (e.g., 2009-01). If omitted, uses the default historical data length for the selected interval.", json_schema_extra={'format': 'date'})
class GetQueryRocrRequest(StrictModel):
    """Calculates the rate of change ratio (ROCR) technical indicator for an equity, measuring the percentage change in price over a specified period. Returns ROCR values at your chosen time interval."""
    query: GetQueryRocrRequestQuery

# Operation: calculate_aroon_indicator
class GetQueryAroonRequestQuery(StrictModel):
    function: Literal["AROON"] = Field(default=..., description="The technical indicator type; must be set to AROON for this operation.")
    symbol: str = Field(default=..., description="The ticker symbol of the equity or forex pair to analyze (e.g., IBM, EURUSD).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points, ranging from 1-minute to monthly granularity.")
    time_period: int = Field(default=..., description="The number of periods used to calculate the Aroon values; typically 14 periods is standard for this indicator.")
    month: str | None = Field(default=None, description="Optional historical month in YYYY-MM format to retrieve Aroon values for a specific month; if omitted, uses the most recent data.")
class GetQueryAroonRequest(StrictModel):
    """Calculates the Aroon technical indicator for a given equity or forex pair, returning Aroon Up and Aroon Down values to identify trend direction and strength."""
    query: GetQueryAroonRequestQuery

# Operation: calculate_aroon_oscillator
class GetQueryAroonoscRequestQuery(StrictModel):
    function: Literal["AROONOSC"] = Field(default=..., description="The technical indicator type. Must be set to AROONOSC for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points. Choose from: 1min, 5min, 15min, 30min, 60min for intraday data, or daily, weekly, monthly for longer-term analysis.")
    time_period: int = Field(default=..., description="The number of periods used to calculate the oscillator value. Must be a positive integer (e.g., 10, 25, 60). Larger values smooth the indicator over longer timeframes.", ge=1)
    month: str | None = Field(default=None, description="Optional historical month for retrieving past indicator values in YYYY-MM format (e.g., 2009-01). If omitted, uses the default data length for the selected interval.", pattern='^\\d{4}-\\d{2}$')
class GetQueryAroonoscRequest(StrictModel):
    """Calculates the Aroon oscillator (AROONOSC) technical indicator for a given equity symbol. The Aroon oscillator measures the difference between Aroon-Up and Aroon-Down, helping identify trend strength and direction changes."""
    query: GetQueryAroonoscRequestQuery

# Operation: calculate_money_flow_index
class GetQueryMfiRequestQuery(StrictModel):
    function: Literal["MFI"] = Field(default=..., description="The technical indicator type. Must be set to MFI for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from: 1min, 5min, 15min, 30min, 60min for intraday data, or daily, weekly, monthly for longer-term analysis.")
    time_period: int = Field(default=..., description="The number of data points used to calculate each MFI value. Must be a positive integer (e.g., 10, 14, 60). Larger values smooth the indicator over longer periods.", ge=1)
    month: str | None = Field(default=None, description="Optional historical month to retrieve MFI values for a specific period in the past, specified in YYYY-MM format (e.g., 2009-01). If omitted, uses the default length of the underlying time series data.")
class GetQueryMfiRequest(StrictModel):
    """Calculates the Money Flow Index (MFI) technical indicator for a given equity symbol. MFI measures buying and selling pressure by analyzing price and volume data over a specified time period and interval."""
    query: GetQueryMfiRequestQuery

# Operation: calculate_trix
class GetQueryTrixRequestQuery(StrictModel):
    function: Literal["TRIX"] = Field(default=..., description="The technical indicator type. Must be set to TRIX for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from minute-level intervals (1, 5, 15, 30, 60 minutes) or daily/weekly/monthly aggregations.")
    time_period: int = Field(default=..., description="The number of data points used to calculate each TRIX value. Must be a positive integer (e.g., 10, 60, 200). Larger values produce smoother results.", ge=1)
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations. Select from closing, opening, high, or low prices for each period.")
    month: str | None = Field(default=None, description="Optional historical month to retrieve TRIX values for a specific period in the past, specified in YYYY-MM format. If omitted, uses the default length of available time series data.", json_schema_extra={'format': 'date'})
class GetQueryTrixRequest(StrictModel):
    """Calculates the 1-day rate of change of a triple smooth exponential moving average (TRIX) for a given equity, providing momentum analysis based on the specified time interval and price series."""
    query: GetQueryTrixRequestQuery

# Operation: calculate_ultimate_oscillator
class GetQueryUltoscRequestQuery(StrictModel):
    function: Literal["ULTOSC"] = Field(default=..., description="The technical indicator function to execute. Must be set to ULTOSC for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points. Choose from intraday intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly historical data.")
    month: str | None = Field(default=None, description="Optional: Retrieve data for a specific month in history using YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data.", json_schema_extra={'format': 'date'})
    timeperiod1: int | None = Field(default=None, description="Optional: The first lookback period for the indicator calculation. Must be a positive integer; defaults to 7 if not specified.", ge=1)
    timeperiod2: int | None = Field(default=None, description="Optional: The second lookback period for the indicator calculation. Must be a positive integer; defaults to 14 if not specified.", ge=1)
    timeperiod3: int | None = Field(default=None, description="Optional: The third lookback period for the indicator calculation. Must be a positive integer; defaults to 28 if not specified.", ge=1)
class GetQueryUltoscRequest(StrictModel):
    """Calculates the Ultimate Oscillator (ULTOSC) technical indicator for a given equity symbol and time interval. The Ultimate Oscillator is a momentum indicator that combines multiple timeframes to identify overbought and oversold conditions."""
    query: GetQueryUltoscRequestQuery

# Operation: get_directional_index
class GetQueryDxRequestQuery(StrictModel):
    function: Literal["DX"] = Field(default=..., description="The technical indicator type. Must be set to DX for directional movement index calculations.")
    symbol: str = Field(default=..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points in the series. Choose from minute-level intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly aggregations.")
    time_period: int = Field(default=..., description="The number of data points used to calculate each DX value. Must be a positive integer of at least 1.", ge=1)
    month: str | None = Field(default=None, description="Optional filter to retrieve DX values for a specific month in historical data. Specify in YYYY-MM format (e.g., 2009-01 for January 2009).")
class GetQueryDxRequest(StrictModel):
    """Retrieves the Directional Movement Index (DX) technical indicator values for a specified equity symbol, time interval, and calculation period. Optionally returns historical data for a specific month."""
    query: GetQueryDxRequestQuery

# Operation: get_minus_directional_indicator
class GetQueryMinusDiRequestQuery(StrictModel):
    function: Literal["MINUS_DI"] = Field(default=..., description="The technical indicator type. Must be set to MINUS_DI for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate the indicator.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from: 1min, 5min, 15min, 30min, 60min for intraday data, or daily, weekly, monthly for longer-term data.")
    time_period: int = Field(default=..., description="The number of data points used to calculate each MINUS_DI value. Must be a positive integer (e.g., 10, 60, 200).", ge=1)
    month: str | None = Field(default=None, description="Optional. Retrieve historical indicator values for a specific month in YYYY-MM format (e.g., 2009-01). If omitted, uses the default length of the underlying time series data.", pattern='^\\d{4}-\\d{2}$')
class GetQueryMinusDiRequest(StrictModel):
    """Retrieves the Minus Directional Indicator (MINUS_DI) values for a given equity symbol, which measures downward price movement strength over a specified time period and interval."""
    query: GetQueryMinusDiRequestQuery

# Operation: get_plus_directional_indicator
class GetQueryPlusDiRequestQuery(StrictModel):
    function: Literal["PLUS_DI"] = Field(default=..., description="The technical indicator type. Must be set to PLUS_DI for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol to analyze (e.g., IBM).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly intervals.")
    time_period: int = Field(default=..., description="The number of data points used to calculate each PLUS_DI value. Must be a positive integer (e.g., 60).", ge=1)
    month: str | None = Field(default=None, description="Optional. Retrieve historical PLUS_DI values for a specific month in YYYY-MM format. If not provided, the calculation uses the default length of the underlying time series data.")
class GetQueryPlusDiRequest(StrictModel):
    """Retrieves Plus Directional Indicator (PLUS_DI) values for a given equity symbol, which measures upward price movement strength over a specified time period and interval."""
    query: GetQueryPlusDiRequestQuery

# Operation: get_minus_directional_movement
class GetQueryMinusDmRequestQuery(StrictModel):
    function: Literal["MINUS_DM"] = Field(default=..., description="The technical indicator type. Must be set to MINUS_DM for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate the indicator.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points: 1min, 5min, 15min, 30min, 60min for intraday data, or daily, weekly, monthly for longer-term analysis.")
    time_period: int = Field(default=..., description="The number of periods used in the MINUS_DM calculation. Must be a positive integer (e.g., 10, 14, 60). Larger values smooth the indicator over longer timeframes.", ge=1)
    month: str | None = Field(default=None, description="Optional historical month for the calculation in YYYY-MM format (e.g., 2009-01). If omitted, uses the default data length for the selected interval.", pattern='^\\d{4}-\\d{2}$', json_schema_extra={'format': 'date'})
class GetQueryMinusDmRequest(StrictModel):
    """Retrieves minus directional movement (MINUS_DM) technical indicator values for a specified equity, measuring downward price movement over a configurable time period and interval."""
    query: GetQueryMinusDmRequestQuery

# Operation: get_plus_directional_movement
class GetQueryPlusDmRequestQuery(StrictModel):
    function: Literal["PLUS_DM"] = Field(default=..., description="The technical indicator type. Must be set to PLUS_DM for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol (e.g., IBM, AAPL). Case-insensitive.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from minute-level intervals (1, 5, 15, 30, 60 minutes) or daily/weekly/monthly aggregations.")
    time_period: int = Field(default=..., description="The number of data points used to calculate each PLUS_DM value. Must be a positive integer of at least 1.", ge=1)
    month: str | None = Field(default=None, description="Optional historical month for retrieving technical indicators from a specific period. Specify in YYYY-MM format (e.g., 2009-01). If omitted, uses the default length of the underlying time series data.", pattern='^\\d{4}-\\d{2}$')
class GetQueryPlusDmRequest(StrictModel):
    """Retrieves Plus Directional Movement (PLUS_DM) values for a given equity symbol. PLUS_DM is a technical indicator that measures upward price movement over a specified time period."""
    query: GetQueryPlusDmRequestQuery

# Operation: calculate_bollinger_bands
class GetQueryBbandsRequestQuery(StrictModel):
    function: Literal["BBANDS"] = Field(default=..., description="The technical indicator function to execute. Must be set to BBANDS for Bollinger Bands calculation.")
    symbol: str = Field(default=..., description="The ticker symbol of the equity or forex pair to analyze (e.g., IBM, AAPL, EUR/USD).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points in the time series. Choose from intraday intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly historical data.")
    time_period: int = Field(default=..., description="The number of data points used to calculate each Bollinger Band value. Must be at least 1; typical values range from 20 to 200 depending on your analysis timeframe.", ge=1)
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use for calculations: closing price, opening price, high price, or low price of each interval.")
    month: str | None = Field(default=None, description="Optional historical month to retrieve data for, specified in YYYY-MM format. If not provided, returns the most recent data available.")
    nbdevup: int | None = Field(default=None, description="The standard deviation multiplier for the upper Bollinger Band. Must be at least 1; defaults to 2 for typical two standard deviation bands.", ge=1)
    nbdevdn: int | None = Field(default=None, description="The standard deviation multiplier for the lower Bollinger Band. Must be at least 1; defaults to 2 for typical two standard deviation bands.", ge=1)
class GetQueryBbandsRequest(StrictModel):
    """Calculates Bollinger Bands technical indicator values for a given equity or forex pair, providing upper, middle, and lower bands based on standard deviation multipliers applied to a moving average."""
    query: GetQueryBbandsRequestQuery

# Operation: calculate_midpoint
class GetQueryMidpointRequestQuery(StrictModel):
    function: Literal["MIDPOINT"] = Field(default=..., description="The technical indicator function to use. Must be set to MIDPOINT for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate midpoint values.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly intervals.")
    time_period: int = Field(default=..., description="The number of data points to use in calculating each midpoint value. Must be a positive integer (e.g., 10, 60, 200).", ge=1)
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in the calculation: closing price, opening price, highest price, or lowest price of each interval.")
    month: str | None = Field(default=None, description="Optional historical month for which to calculate midpoint values, specified in YYYY-MM format. If not provided, calculations use the default time series data.")
class GetQueryMidpointRequest(StrictModel):
    """Calculates the midpoint values (average of highest and lowest prices) for an equity over a specified period and time interval."""
    query: GetQueryMidpointRequestQuery

# Operation: calculate_midprice
class GetQueryMidpriceRequestQuery(StrictModel):
    function: Literal["MIDPRICE"] = Field(default=..., description="The technical indicator type. Must be set to MIDPRICE for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate the midpoint price.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from minute-level intervals (1, 5, 15, 30, or 60 minutes) or longer periods (daily, weekly, or monthly).")
    time_period: int = Field(default=..., description="The number of data points used to calculate each MIDPRICE value. Must be a positive integer (e.g., 10, 60, 200).", ge=1)
    month: str | None = Field(default=None, description="Optional historical month for retrieving technical indicators from a specific period in the past. Specify in YYYY-MM format (e.g., 2009-01). If omitted, uses the default time series data for the selected interval.", pattern='^\\d{4}-\\d{2}$', json_schema_extra={'format': 'date'})
class GetQueryMidpriceRequest(StrictModel):
    """Calculates the midpoint price (MIDPRICE) indicator for an equity over a specified period and time interval. MIDPRICE is computed as the average of the highest high and lowest low prices within each interval."""
    query: GetQueryMidpriceRequestQuery

# Operation: get_parabolic_sar
class GetQuerySarRequestQuery(StrictModel):
    function: Literal["SAR"] = Field(default=..., description="The technical indicator type; must be set to SAR for parabolic SAR calculations.")
    symbol: str = Field(default=..., description="The stock ticker symbol (e.g., IBM) for which to calculate the parabolic SAR.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points: 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly.")
    month: str | None = Field(default=None, description="Optional historical month filter in YYYY-MM format to retrieve SAR values for a specific month.")
    acceleration: float | None = Field(default=None, description="The acceleration factor used in SAR calculations; defaults to 0.01 and accepts positive decimal values to control how quickly the SAR adjusts to price movements.")
    maximum: float | None = Field(default=None, description="The maximum acceleration factor cap; defaults to 0.2 and accepts positive decimal values to limit the maximum rate of SAR adjustment.")
class GetQuerySarRequest(StrictModel):
    """Retrieves parabolic SAR (Stop and Reverse) technical indicator values for a given equity at specified time intervals, useful for identifying potential trend reversals and stop-loss levels."""
    query: GetQuerySarRequestQuery

# Operation: get_true_range
class GetQueryTrangeRequestQuery(StrictModel):
    function: Literal["TRANGE"] = Field(default=..., description="The technical indicator type. Must be set to TRANGE to calculate true range values.")
    symbol: str = Field(default=..., description="The stock ticker symbol (e.g., IBM, AAPL). Identifies which equity to retrieve true range data for.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points. Choose from minute-level intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly aggregations.")
    month: str | None = Field(default=None, description="Optional. Retrieve true range values for a specific month in history using YYYY-MM format (e.g., 2009-01). If omitted, returns data based on the default time series length for the selected interval.", json_schema_extra={'format': 'date'})
class GetQueryTrangeRequest(StrictModel):
    """Retrieves True Range (TRANGE) volatility values for a specified equity symbol at your chosen time interval. Optionally retrieve historical data for a specific month."""
    query: GetQueryTrangeRequestQuery

# Operation: get_atr
class GetQueryAtrRequestQuery(StrictModel):
    function: Literal["ATR"] = Field(default=..., description="The technical indicator type. Must be set to ATR for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to retrieve ATR data.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from minute-level intervals (1, 5, 15, or 30 minutes), hourly (60 minutes), or daily/weekly/monthly aggregations.")
    time_period: int = Field(default=..., description="The number of periods used to calculate each ATR value. Must be a positive integer (e.g., 14 is a common default for daily charts).", ge=1)
    month: str | None = Field(default=None, description="Optional filter to retrieve historical ATR data for a specific month in YYYY-MM format (e.g., 2009-01). Omit to get the most recent data.")
class GetQueryAtrRequest(StrictModel):
    """Retrieves Average True Range (ATR) technical indicator values for a specified equity, showing volatility measurements over a chosen time interval and period."""
    query: GetQueryAtrRequestQuery

# Operation: get_natr_values
class GetQueryNatrRequestQuery(StrictModel):
    function: Literal["NATR"] = Field(default=..., description="The technical indicator type. Must be set to NATR for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from minute-level intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly aggregations.")
    time_period: int = Field(default=..., description="The number of periods used to calculate each NATR value. Must be a positive integer (e.g., 60 for a 60-period moving average).", ge=1)
    month: str | None = Field(default=None, description="Optional historical month to retrieve data for, specified in YYYY-MM format (e.g., 2009-01 for January 2009). Omit to get the most recent data.")
class GetQueryNatrRequest(StrictModel):
    """Retrieves normalized average true range (NATR) technical indicator values for a specified equity symbol. NATR measures volatility as a percentage of the closing price, allowing for normalized comparison across different price levels."""
    query: GetQueryNatrRequestQuery

# Operation: get_chaikin_ad_line
class GetQueryAdRequestQuery(StrictModel):
    function: Literal["AD"] = Field(default=..., description="The technical indicator type. Must be set to AD for Chaikin A/D line calculations.")
    symbol: str = Field(default=..., description="The stock ticker symbol (e.g., IBM, AAPL). Identifies which equity to retrieve data for.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points in the series. Choose from minute-level intervals (1, 5, 15, or 30 minutes, or 1 hour) or daily/weekly/monthly historical data.")
    month: str | None = Field(default=None, description="Optional filter to retrieve historical data for a specific month. Use YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data.", json_schema_extra={'format': 'date'})
class GetQueryAdRequest(StrictModel):
    """Retrieves Chaikin A/D line (Accumulation/Distribution) values for a given equity, showing the relationship between price and volume to identify buying and selling pressure."""
    query: GetQueryAdRequestQuery

# Operation: get_adosc_values
class GetQueryAdoscRequestQuery(StrictModel):
    function: Literal["ADOSC"] = Field(default=..., description="The technical indicator type; must be set to ADOSC for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points: 1min, 5min, 15min, 30min, or 60min for intraday data, or daily, weekly, monthly for longer periods.")
    month: str | None = Field(default=None, description="Optional historical month in YYYY-MM format to retrieve ADOSC values for a specific month. If not provided, uses the default time series data.")
    fastperiod: int | None = Field(default=None, description="The time period for the fast exponential moving average calculation. Must be a positive integer; defaults to 3 if not specified.", ge=1)
    slowperiod: int | None = Field(default=None, description="The time period for the slow exponential moving average calculation. Must be a positive integer; defaults to 10 if not specified.", ge=1)
class GetQueryAdoscRequest(StrictModel):
    """Retrieves Chaikin A/D oscillator (ADOSC) technical indicator values for a specified equity symbol and time interval, with optional historical month selection and EMA period customization."""
    query: GetQueryAdoscRequestQuery

# Operation: get_obv
class GetQueryObvRequestQuery(StrictModel):
    function: Literal["OBV"] = Field(default=..., description="The technical indicator type to calculate. Must be set to OBV (On-Balance Volume).")
    symbol: str = Field(default=..., description="The stock ticker symbol for the equity you want to analyze (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points. Choose from: 1min, 5min, 15min, 30min, 60min for intraday data, or daily, weekly, monthly for longer-term analysis.")
    month: str | None = Field(default=None, description="Optional historical month to retrieve OBV values for a specific period in the past, specified in YYYY-MM format. If omitted, returns data based on the default time series length for the selected interval.")
class GetQueryObvRequest(StrictModel):
    """Retrieves on-balance volume (OBV) technical indicator values for a specified equity, showing cumulative volume trends across your chosen time interval."""
    query: GetQueryObvRequestQuery

# Operation: get_hilbert_trendline
class GetQueryHtTrendlineRequestQuery(StrictModel):
    function: Literal["HT_TRENDLINE"] = Field(default=..., description="The technical indicator type. Must be set to HT_TRENDLINE for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate the trendline.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points. Choose from 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly intervals.")
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations. Select from closing price, opening price, high price, or low price for the interval.")
    month: str | None = Field(default=None, description="Optional historical month to retrieve data for, specified in YYYY-MM format (e.g., 2009-01). If omitted, returns the most recent data.", json_schema_extra={'format': 'date'})
class GetQueryHtTrendlineRequest(StrictModel):
    """Retrieves Hilbert transform instantaneous trendline (HT_TRENDLINE) technical indicator values for a specified equity, helping identify trend direction and potential reversal points."""
    query: GetQueryHtTrendlineRequestQuery

# Operation: get_hilbert_sine_indicator
class GetQueryHtSineRequestQuery(StrictModel):
    function: Literal["HT_SINE"] = Field(default=..., description="The technical indicator function to calculate. Must be set to HT_SINE for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol for which to retrieve the indicator (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly intervals.")
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations. Select from closing price, opening price, high price, or low price for the interval.")
    month: str | None = Field(default=None, description="Optional historical month to retrieve data for, specified in YYYY-MM format (e.g., 2009-01 for January 2009). If omitted, returns the most recent data.")
class GetQueryHtSineRequest(StrictModel):
    """Retrieves Hilbert transform sine wave (HT_SINE) technical indicator values for a given equity symbol, useful for identifying cyclical trends and potential turning points in price movements."""
    query: GetQueryHtSineRequestQuery

# Operation: analyze_hilbert_trend_cycle
class GetQueryHtTrendmodeRequestQuery(StrictModel):
    function: Literal["HT_TRENDMODE"] = Field(default=..., description="The technical indicator function to apply. Must be set to HT_TRENDMODE for Hilbert Transform trend vs cycle analysis.")
    symbol: str = Field(default=..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL, MSFT).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points. Choose from minute-level intervals (1, 5, 15, 30, 60 minutes) or longer periods (daily, weekly, monthly).")
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations: closing price, opening price, high price, or low price for each interval.")
    month: str | None = Field(default=None, description="Optional historical month for analysis in YYYY-MM format (e.g., 2009-01). If omitted, uses the default length of available time series data.", pattern='^\\d{4}-\\d{2}$')
class GetQueryHtTrendmodeRequest(StrictModel):
    """Analyzes price data using the Hilbert Transform to identify whether the market is in a trend or cycle mode, returning mode values for the specified equity and time interval."""
    query: GetQueryHtTrendmodeRequestQuery

# Operation: get_dominant_cycle_period
class GetQueryHtDcperiodRequestQuery(StrictModel):
    function: Literal["HT_DCPERIOD"] = Field(default=..., description="The technical indicator to calculate. Must be set to HT_DCPERIOD for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol (e.g., IBM, AAPL) for which to calculate the dominant cycle period.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points. Choose from: 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly intervals.")
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations. Select from: close, open, high, or low prices.")
    month: str | None = Field(default=None, description="Optional historical month for the calculation in YYYY-MM format (e.g., 2009-01). If not specified, the calculation uses the default length of available time series data.", json_schema_extra={'format': 'date'})
class GetQueryHtDcperiodRequest(StrictModel):
    """Calculates the Hilbert transform dominant cycle period (HT_DCPERIOD) for a given equity, identifying the dominant cycle length in the price data at your specified time interval."""
    query: GetQueryHtDcperiodRequestQuery

# Operation: get_dominant_cycle_phase
class GetQueryHtDcphaseRequestQuery(StrictModel):
    function: Literal["HT_DCPHASE"] = Field(default=..., description="The technical indicator function to calculate. Must be set to HT_DCPHASE for this operation.")
    symbol: str = Field(default=..., description="The stock ticker symbol to analyze (e.g., IBM, AAPL).")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between data points. Choose from minute-level intervals (1, 5, 15, or 30 minutes, or 60 minutes) or daily/weekly/monthly historical data.")
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations. Select from open, high, low, or close prices.")
    month: str | None = Field(default=None, description="Optional historical month to retrieve data for, specified in YYYY-MM format (e.g., 2009-01 for January 2009).")
class GetQueryHtDcphaseRequest(StrictModel):
    """Retrieves the Hilbert transform dominant cycle phase indicator for a given equity symbol, helping identify the current phase position within the dominant market cycle."""
    query: GetQueryHtDcphaseRequestQuery

# Operation: get_hilbert_phasor
class GetQueryHtPhasorRequestQuery(StrictModel):
    function: Literal["HT_PHASOR"] = Field(default=..., description="The technical indicator type. Must be set to HT_PHASOR to retrieve Hilbert transform phasor components.")
    symbol: str = Field(default=..., description="The equity ticker symbol to analyze (e.g., IBM, AAPL). Case-insensitive.")
    interval: Literal["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval between consecutive data points. Choose from: 1-minute, 5-minute, 15-minute, 30-minute, 60-minute, daily, weekly, or monthly intervals.")
    series_type: Literal["close", "open", "high", "low"] = Field(default=..., description="The price type to use in calculations. Select one of: closing price, opening price, high price, or low price for each period.")
    month: str | None = Field(default=None, description="Optional historical month for the calculation in YYYY-MM format (e.g., 2009-01). If omitted, uses the default length of the underlying time series data.", json_schema_extra={'format': 'date'})
class GetQueryHtPhasorRequest(StrictModel):
    """Retrieves Hilbert transform phasor components for a given equity symbol, providing phase and amplitude information derived from the specified price series and time interval."""
    query: GetQueryHtPhasorRequestQuery

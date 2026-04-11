"""
Authentication module for Polygon API MCP server.

Generated: 2026-04-11 20:19:10 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)

This module contains:
1. Authentication class implementations (OAuth2)
2. Operation-to-auth requirements mapping (OPERATION_AUTH_MAP)
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

__all__ = [
    "APIKeyAuth",
    "OPERATION_AUTH_MAP",
]

# ============================================================================
# Authentication Classes
# ============================================================================

class APIKeyAuth:
    """
    API Key authentication for Polygon API.

    Supports header, query parameter, cookie, and path-based API key injection.
    Configure location and parameter name via constructor arguments.
    """

    def __init__(self, env_var: str = "API_KEY", location: str = "header",
                 param_name: str = "Authorization", prefix: str = ""):
        """Initialize API key authentication from environment variable.

        Args:
            env_var: Environment variable name containing the API key.
            location: Where to inject the key - 'header', 'query', 'cookie', or 'path'.
            param_name: Name of the header, query parameter, cookie, or path placeholder.
            prefix: Optional prefix before the key value (e.g., 'Bearer').
        """
        self.location = location
        self.param_name = param_name
        self.prefix = prefix
        self.api_key = os.getenv(env_var, "").strip()

        # Check for empty API key
        if not self.api_key:
            raise ValueError(
                f"{env_var} environment variable not set. "
                "Leave empty in .env to disable API Key auth."
            )

        # Detect common placeholder patterns
        placeholders = ["placeholder", "your-", "example", "change-me", "todo", "bot placeholder"]
        api_key_lower = self.api_key.lower()

        if any(p in api_key_lower for p in placeholders):
            raise ValueError(
                f"API key appears to be a placeholder ({self.api_key[:20]}...). "
                "Please set a real API key or leave empty to disable API Key auth."
            )

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for API requests."""
        if self.location != "header":
            return {}
        if self.param_name == "Authorization":
            # Use explicit prefix if set; otherwise send the key raw (no Bearer assumption —
            # apiKey schemes that happen to use the Authorization header don't imply Bearer)
            prefix = self.prefix + " " if self.prefix else ""
            return {"Authorization": f"{prefix}{self.api_key}"}
        value = f"{self.prefix} {self.api_key}" if self.prefix else self.api_key
        return {self.param_name: value}

    def get_auth_params(self) -> dict[str, str]:
        """Get authentication query parameters."""
        if self.location != "query":
            return {}
        return {self.param_name: self.api_key}

    def get_auth_cookies(self) -> dict[str, str]:
        """Get authentication cookies."""
        if self.location != "cookie":
            return {}
        return {self.param_name: self.api_key}

    def get_auth_path_params(self) -> dict[str, str]:
        """Get authentication path parameters for URL template substitution."""
        if self.location != "path":
            return {}
        return {self.param_name: self.api_key}


# ============================================================================
# Operation Auth Requirements Map
# ============================================================================

"""
Operation-to-authentication requirements mapping.

This dictionary defines which authentication schemes are required for each operation,
using OR/AND relationships (outer list = OR, inner list = AND).
"""
OPERATION_AUTH_MAP: dict[str, list[list[str]]] = {
    "list_analyst_insights": [["apiKey"]],
    "list_analysts": [["apiKey"]],
    "list_bulls_bears_say": [["apiKey"]],
    "get_consensus_ratings": [["apiKey"]],
    "list_earnings": [["apiKey"]],
    "list_firms": [["apiKey"]],
    "list_guidance": [["apiKey"]],
    "list_analyst_ratings": [["apiKey"]],
    "search_financial_news": [["apiKey"]],
    "list_merchant_aggregates_eu": [["apiKey"]],
    "list_merchant_hierarchy": [["apiKey"]],
    "list_etf_analytics": [["apiKey"]],
    "list_etf_constituents": [["apiKey"]],
    "list_etf_fund_flows": [["apiKey"]],
    "list_etf_profiles": [["apiKey"]],
    "list_etf_taxonomies": [["apiKey"]],
    "list_inflation_metrics": [["apiKey"]],
    "list_inflation_expectations": [["apiKey"]],
    "list_labor_market_indicators": [["apiKey"]],
    "list_treasury_yields": [["apiKey"]],
    "get_futures_aggregates": [["apiKey"]],
    "get_futures_aggregates_vx": [["apiKey"]],
    "list_futures_contracts": [["apiKey"]],
    "list_futures_exchanges": [["apiKey"]],
    "list_futures_market_statuses": [["apiKey"]],
    "list_futures_products": [["apiKey"]],
    "get_futures_quotes": [["apiKey"]],
    "list_futures_schedules": [["apiKey"]],
    "list_futures_snapshots": [["apiKey"]],
    "list_futures_trades": [["apiKey"]],
    "list_stock_filings_10_k_sections": [["apiKey"]],
    "list_stocks_8k_filings_text": [["apiKey"]],
    "list_13f_filings": [["apiKey"]],
    "list_sec_filings": [["apiKey"]],
    "list_risk_factors_from_stock_filings": [["apiKey"]],
    "list_balance_sheets": [["apiKey"]],
    "list_cash_flow_statements": [["apiKey"]],
    "list_income_statements": [["apiKey"]],
    "list_stock_financial_ratios": [["apiKey"]],
    "list_risk_factor_taxonomies": [["apiKey"]],
    "list_stock_dividends": [["apiKey"]],
    "list_short_interest": [["apiKey"]],
    "list_short_volume_by_ticker": [["apiKey"]],
    "list_stock_splits_historical": [["apiKey"]],
    "list_stocks_by_float": [["apiKey"]],
    "list_corporate_events": [["apiKey"]],
    "get_currency_conversion": [["apiKey"]],
    "get_historic_forex_ticks": [["apiKey"]],
    "get_crypto_ema": [["apiKey"]],
    "get_forex_ema": [["apiKey"]],
    "get_exponential_moving_average": [["apiKey"]],
    "get_ema_for_options_ticker": [["apiKey"]],
    "get_exponential_moving_average_stock": [["apiKey"]],
    "get_crypto_macd": [["apiKey"]],
    "get_macd_indicator_forex": [["apiKey"]],
    "get_macd_for_indices": [["apiKey"]],
    "get_macd_for_options_ticker": [["apiKey"]],
    "get_macd_indicator": [["apiKey"]],
    "get_crypto_rsi": [["apiKey"]],
    "get_forex_rsi": [["apiKey"]],
    "get_rsi_for_indices": [["apiKey"]],
    "get_options_rsi": [["apiKey"]],
    "get_rsi_for_stock": [["apiKey"]],
    "get_crypto_simple_moving_average": [["apiKey"]],
    "get_forex_simple_moving_average": [["apiKey"]],
    "get_sma_for_indices": [["apiKey"]],
    "get_sma_for_options_ticker": [["apiKey"]],
    "get_simple_moving_average": [["apiKey"]],
    "get_last_trade_for_crypto_pair": [["apiKey"]],
    "get_last_quote_for_currency_pair": [["apiKey"]],
    "get_market_status": [["apiKey"]],
    "list_market_holidays": [["apiKey"]],
    "get_crypto_daily_open_close": [["apiKey"]],
    "get_index_open_close": [["apiKey"]],
    "get_options_daily_open_close": [["apiKey"]],
    "get_stock_daily_open_close": [["apiKey"]],
    "list_sec_filings_reference": [["apiKey"]],
    "get_filing": [["apiKey"]],
    "list_filing_files": [["apiKey"]],
    "get_sec_filing_file": [["apiKey"]],
    "list_related_companies": [["apiKey"]],
    "get_ticker_summaries": [["apiKey"]],
    "get_grouped_crypto_aggregates": [["apiKey"]],
    "get_grouped_forex_aggregates": [["apiKey"]],
    "get_grouped_stocks_aggregates": [["apiKey"]],
    "get_previous_crypto_aggregates": [["apiKey"]],
    "get_crypto_aggregates": [["apiKey"]],
    "get_previous_forex_close": [["apiKey"]],
    "get_forex_aggregates": [["apiKey"]],
    "get_previous_index_aggregates": [["apiKey"]],
    "get_indices_aggregates": [["apiKey"]],
    "get_previous_close_for_options_contract": [["apiKey"]],
    "get_options_aggregates": [["apiKey"]],
    "get_previous_day_stock_ohlc": [["apiKey"]],
    "get_stock_aggregates_by_range": [["apiKey"]],
    "get_last_quote": [["apiKey"]],
    "get_last_trade_for_options_contract": [["apiKey"]],
    "get_last_trade": [["apiKey"]],
    "list_news_for_ticker": [["apiKey"]],
    "list_crypto_tickers_snapshot": [["apiKey"]],
    "get_crypto_ticker_snapshot": [["apiKey"]],
    "list_crypto_gainers_or_losers": [["apiKey"]],
    "get_forex_snapshot_tickers": [["apiKey"]],
    "get_forex_ticker_snapshot": [["apiKey"]],
    "list_forex_gainers_or_losers": [["apiKey"]],
    "list_stock_tickers_snapshot": [["apiKey"]],
    "get_stock_snapshot_by_ticker": [["apiKey"]],
    "list_stocks_by_direction": [["apiKey"]],
    "get_nbbo_quotes_for_date": [["apiKey"]],
    "get_fx_quotes": [["apiKey"]],
    "list_options_quotes": [["apiKey"]],
    "get_stock_quotes": [["apiKey"]],
    "list_conditions": [["apiKey"]],
    "list_dividends": [["apiKey"]],
    "list_exchanges": [["apiKey"]],
    "list_options_contracts": [["apiKey"]],
    "get_options_contract": [["apiKey"]],
    "list_stock_splits": [["apiKey"]],
    "list_tickers": [["apiKey"]],
    "list_ticker_types": [["apiKey"]],
    "get_ticker_details": [["apiKey"]],
    "list_snapshots": [["apiKey"]],
    "list_indices_snapshot": [["apiKey"]],
    "list_options_chain": [["apiKey"]],
    "get_option_contract_snapshot": [["apiKey"]],
    "list_crypto_trades": [["apiKey"]],
    "list_options_trades": [["apiKey"]],
    "list_trades": [["apiKey"]],
    "list_financials": [["apiKey"]],
    "list_ipos_detailed": [["apiKey"]],
    "list_ticker_events": [["apiKey"]]
}

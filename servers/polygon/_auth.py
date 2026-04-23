"""
Authentication module for Polygon API MCP server.

Generated: 2026-04-23 21:37:40 UTC
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
    "BearerTokenAuth",
    "OPERATION_AUTH_MAP",
]

# ============================================================================
# Authentication Classes
# ============================================================================

class BearerTokenAuth:
    """
    Bearer token authentication for Polygon API.

    Configuration:
        Provide the raw token in the environment variable.
        The authorization scheme prefix is automatically inserted.
    """

    def __init__(self, env_var: str = "BEARER_TOKEN", token_format: str = "Bearer"):
        """Initialize bearer token authentication from environment variable.

        Args:
            env_var: Environment variable name containing the bearer token.
            token_format: Authorization scheme prefix (e.g., 'Bearer').
        """
        self.token_format = token_format
        self.token = os.getenv(env_var, "").strip()

        # Check for empty token
        if not self.token:
            raise ValueError(
                f"{env_var} environment variable not set. "
                "Leave empty in .env to disable Bearer Token auth."
            )

        # Detect common placeholder patterns
        placeholders = ["placeholder", "your-", "example", "change-me", "todo", "sk_test_placeholder"]
        token_lower = self.token.lower()

        if any(p in token_lower for p in placeholders):
            raise ValueError(
                f"Bearer token appears to be a placeholder ({self.token[:20]}...). "
                "Please set a real token or leave empty to disable Bearer Token auth."
            )

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for API requests."""
        return {
            'Authorization': f'{self.token_format} {self.token}'
        }


# ============================================================================
# Operation Auth Requirements Map
# ============================================================================

"""
Operation-to-authentication requirements mapping.

This dictionary defines which authentication schemes are required for each operation,
using OR/AND relationships (outer list = OR, inner list = AND).
"""
OPERATION_AUTH_MAP: dict[str, list[list[str]]] = {
    "list_analyst_insights": [["BearerAuth"]],
    "list_analysts": [["BearerAuth"]],
    "list_bulls_bears_say": [["BearerAuth"]],
    "get_consensus_ratings": [["BearerAuth"]],
    "list_earnings": [["BearerAuth"]],
    "list_firms": [["BearerAuth"]],
    "list_guidance": [["BearerAuth"]],
    "list_analyst_ratings": [["BearerAuth"]],
    "search_financial_news": [["BearerAuth"]],
    "list_merchant_aggregates_eu": [["BearerAuth"]],
    "list_merchant_hierarchy": [["BearerAuth"]],
    "list_etf_analytics": [["BearerAuth"]],
    "list_etf_constituents": [["BearerAuth"]],
    "list_etf_fund_flows": [["BearerAuth"]],
    "list_etf_profiles": [["BearerAuth"]],
    "list_etf_taxonomies": [["BearerAuth"]],
    "list_inflation_metrics": [["BearerAuth"]],
    "list_inflation_expectations": [["BearerAuth"]],
    "list_labor_market_indicators": [["BearerAuth"]],
    "list_treasury_yields": [["BearerAuth"]],
    "get_futures_aggregates": [["BearerAuth"]],
    "get_futures_aggregates_vx": [["BearerAuth"]],
    "list_futures_contracts": [["BearerAuth"]],
    "list_futures_exchanges": [["BearerAuth"]],
    "list_futures_market_statuses": [["BearerAuth"]],
    "list_futures_products": [["BearerAuth"]],
    "get_futures_quotes": [["BearerAuth"]],
    "list_futures_schedules": [["BearerAuth"]],
    "list_futures_snapshots": [["BearerAuth"]],
    "list_futures_trades": [["BearerAuth"]],
    "list_stock_filings_10_k_sections": [["BearerAuth"]],
    "list_stocks_8k_filings_text": [["BearerAuth"]],
    "list_13f_filings": [["BearerAuth"]],
    "list_sec_filings": [["BearerAuth"]],
    "list_risk_factors_from_stock_filings": [["BearerAuth"]],
    "list_balance_sheets": [["BearerAuth"]],
    "list_cash_flow_statements": [["BearerAuth"]],
    "list_income_statements": [["BearerAuth"]],
    "list_stock_financial_ratios": [["BearerAuth"]],
    "list_risk_factor_taxonomies": [["BearerAuth"]],
    "list_stock_dividends": [["BearerAuth"]],
    "list_short_interest": [["BearerAuth"]],
    "list_short_volume_by_ticker": [["BearerAuth"]],
    "list_stock_splits_historical": [["BearerAuth"]],
    "list_stocks_by_float": [["BearerAuth"]],
    "list_corporate_events": [["BearerAuth"]],
    "get_currency_conversion": [["BearerAuth"]],
    "get_historic_forex_ticks": [["BearerAuth"]],
    "get_crypto_ema": [["BearerAuth"]],
    "get_forex_ema": [["BearerAuth"]],
    "get_exponential_moving_average": [["BearerAuth"]],
    "get_ema_for_options_ticker": [["BearerAuth"]],
    "get_exponential_moving_average_stock": [["BearerAuth"]],
    "get_crypto_macd": [["BearerAuth"]],
    "get_macd_indicator_forex": [["BearerAuth"]],
    "get_macd_for_indices": [["BearerAuth"]],
    "get_macd_for_options_ticker": [["BearerAuth"]],
    "get_macd_indicator": [["BearerAuth"]],
    "get_crypto_rsi": [["BearerAuth"]],
    "get_forex_rsi": [["BearerAuth"]],
    "get_rsi_for_indices": [["BearerAuth"]],
    "get_options_rsi": [["BearerAuth"]],
    "get_rsi_for_stock": [["BearerAuth"]],
    "get_crypto_simple_moving_average": [["BearerAuth"]],
    "get_forex_simple_moving_average": [["BearerAuth"]],
    "get_sma_for_indices": [["BearerAuth"]],
    "get_sma_for_options_ticker": [["BearerAuth"]],
    "get_simple_moving_average": [["BearerAuth"]],
    "get_last_trade_for_crypto_pair": [["BearerAuth"]],
    "get_last_quote_for_currency_pair": [["BearerAuth"]],
    "get_market_status": [["BearerAuth"]],
    "list_market_holidays": [["BearerAuth"]],
    "get_crypto_daily_open_close": [["BearerAuth"]],
    "get_index_open_close": [["BearerAuth"]],
    "get_options_daily_open_close": [["BearerAuth"]],
    "get_stock_daily_open_close": [["BearerAuth"]],
    "list_sec_filings_reference": [["BearerAuth"]],
    "get_filing": [["BearerAuth"]],
    "list_filing_files": [["BearerAuth"]],
    "get_sec_filing_file": [["BearerAuth"]],
    "list_related_companies": [["BearerAuth"]],
    "get_ticker_summaries": [["BearerAuth"]],
    "get_grouped_crypto_aggregates": [["BearerAuth"]],
    "get_grouped_forex_aggregates": [["BearerAuth"]],
    "get_grouped_stocks_aggregates": [["BearerAuth"]],
    "get_previous_crypto_aggregates": [["BearerAuth"]],
    "get_crypto_aggregates": [["BearerAuth"]],
    "get_previous_forex_close": [["BearerAuth"]],
    "get_forex_aggregates": [["BearerAuth"]],
    "get_previous_index_aggregates": [["BearerAuth"]],
    "get_indices_aggregates": [["BearerAuth"]],
    "get_previous_close_for_options_contract": [["BearerAuth"]],
    "get_options_aggregates": [["BearerAuth"]],
    "get_previous_day_stock_ohlc": [["BearerAuth"]],
    "get_stock_aggregates_by_range": [["BearerAuth"]],
    "get_last_quote": [["BearerAuth"]],
    "get_last_trade_for_options_contract": [["BearerAuth"]],
    "get_last_trade": [["BearerAuth"]],
    "list_news_for_ticker": [["BearerAuth"]],
    "list_crypto_tickers_snapshot": [["BearerAuth"]],
    "get_crypto_ticker_snapshot": [["BearerAuth"]],
    "list_crypto_gainers_or_losers": [["BearerAuth"]],
    "get_forex_snapshot_tickers": [["BearerAuth"]],
    "get_forex_ticker_snapshot": [["BearerAuth"]],
    "list_forex_gainers_or_losers": [["BearerAuth"]],
    "list_stock_tickers_snapshot": [["BearerAuth"]],
    "get_stock_snapshot_by_ticker": [["BearerAuth"]],
    "list_stocks_by_direction": [["BearerAuth"]],
    "get_nbbo_quotes_for_date": [["BearerAuth"]],
    "get_fx_quotes": [["BearerAuth"]],
    "list_options_quotes": [["BearerAuth"]],
    "get_stock_quotes": [["BearerAuth"]],
    "list_conditions": [["BearerAuth"]],
    "list_dividends": [["BearerAuth"]],
    "list_exchanges": [["BearerAuth"]],
    "list_options_contracts": [["BearerAuth"]],
    "get_options_contract": [["BearerAuth"]],
    "list_stock_splits": [["BearerAuth"]],
    "list_tickers": [["BearerAuth"]],
    "list_ticker_types": [["BearerAuth"]],
    "get_ticker_details": [["BearerAuth"]],
    "list_snapshots": [["BearerAuth"]],
    "list_indices_snapshot": [["BearerAuth"]],
    "list_options_chain": [["BearerAuth"]],
    "get_option_contract_snapshot": [["BearerAuth"]],
    "list_crypto_trades": [["BearerAuth"]],
    "list_options_trades": [["BearerAuth"]],
    "list_trades": [["BearerAuth"]],
    "list_financials": [["BearerAuth"]],
    "list_ipos_detailed": [["BearerAuth"]],
    "list_ticker_events": [["BearerAuth"]]
}

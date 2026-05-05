"""
Authentication module for Alpha Vantage MCP server.

Generated: 2026-05-05 14:10:47 UTC
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
    API Key authentication for Alpha Vantage API.

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
    "get_intraday_time_series": [["apiKey"]],
    "get_daily_time_series": [["apiKey"]],
    "get_daily_adjusted_time_series": [["apiKey"]],
    "get_weekly_time_series": [["apiKey"]],
    "get_weekly_adjusted_time_series": [["apiKey"]],
    "get_equity_monthly_time_series": [["apiKey"]],
    "get_monthly_adjusted_time_series": [["apiKey"]],
    "get_realtime_quotes": [["apiKey"]],
    "search_symbols": [["apiKey"]],
    "check_market_status": [["apiKey"]],
    "get_index_data": [["apiKey"]],
    "list_index_symbols": [["apiKey"]],
    "list_realtime_options": [["apiKey"]],
    "get_realtime_put_call_ratio": [["apiKey"]],
    "get_historical_options": [["apiKey"]],
    "get_historical_put_call_ratio": [["apiKey"]],
    "search_news_sentiment": [["apiKey"]],
    "get_earnings_call_transcript": [["apiKey"]],
    "list_market_movers": [["apiKey"]],
    "list_insider_transactions": [["apiKey"]],
    "get_institutional_holdings": [["apiKey"]],
    "calculate_analytics_fixed_window": [["apiKey"]],
    "analyze_sliding_window_metrics": [["apiKey"]],
    "get_company_overview": [["apiKey"]],
    "get_etf_profile": [["apiKey"]],
    "get_dividend_history": [["apiKey"]],
    "get_stock_splits": [["apiKey"]],
    "get_income_statement": [["apiKey"]],
    "get_balance_sheet": [["apiKey"]],
    "get_cash_flow_statement": [["apiKey"]],
    "get_shares_outstanding": [["apiKey"]],
    "get_earnings": [["apiKey"]],
    "get_earnings_estimates": [["apiKey"]],
    "list_listing_status": [["apiKey"]],
    "list_earnings_calendar": [["apiKey"]],
    "list_ipo_calendar": [["apiKey"]],
    "get_exchange_rate": [["apiKey"]],
    "get_forex_intraday": [["apiKey"]],
    "get_fx_daily": [["apiKey"]],
    "get_forex_weekly": [["apiKey"]],
    "get_forex_monthly": [["apiKey"]],
    "get_crypto_intraday": [["apiKey"]],
    "get_cryptocurrency_daily_prices": [["apiKey"]],
    "get_cryptocurrency_weekly_prices": [["apiKey"]],
    "get_cryptocurrency_monthly_history": [["apiKey"]],
    "get_spot_price": [["apiKey"]],
    "get_precious_metal_history": [["apiKey"]],
    "get_wti_crude_oil_prices": [["apiKey"]],
    "get_brent_crude_oil_prices": [["apiKey"]],
    "get_natural_gas_prices": [["apiKey"]],
    "get_copper_prices": [["apiKey"]],
    "get_aluminum_prices": [["apiKey"]],
    "get_wheat_price": [["apiKey"]],
    "get_corn_prices": [["apiKey"]],
    "get_cotton_prices": [["apiKey"]],
    "get_sugar_prices": [["apiKey"]],
    "get_coffee_prices": [["apiKey"]],
    "get_commodity_price_index": [["apiKey"]],
    "get_real_gdp": [["apiKey"]],
    "get_real_gdp_per_capita": [["apiKey"]],
    "fetch_treasury_yield": [["apiKey"]],
    "get_federal_funds_rate": [["apiKey"]],
    "get_cpi_data": [["apiKey"]],
    "get_inflation_rates": [["apiKey"]],
    "get_retail_sales": [["apiKey"]],
    "get_durable_goods_orders": [["apiKey"]],
    "get_unemployment_rate": [["apiKey"]],
    "get_nonfarm_payroll": [["apiKey"]],
    "calculate_sma": [["apiKey"]],
    "calculate_ema": [["apiKey"]],
    "calculate_weighted_moving_average": [["apiKey"]],
    "calculate_dema": [["apiKey"]],
    "calculate_tema": [["apiKey"]],
    "calculate_triangular_moving_average": [["apiKey"]],
    "calculate_kama": [["apiKey"]],
    "get_mama_indicator": [["apiKey"]],
    "calculate_vwap": [["apiKey"]],
    "calculate_t3_moving_average": [["apiKey"]],
    "calculate_macd": [["apiKey"]],
    "calculate_macd_extended": [["apiKey"]],
    "get_stochastic_oscillator": [["apiKey"]],
    "get_stochastic_fast_indicator": [["apiKey"]],
    "calculate_rsi": [["apiKey"]],
    "calculate_stochrsi": [["apiKey"]],
    "get_williams_percent_r": [["apiKey"]],
    "calculate_adx": [["apiKey"]],
    "get_adxr_values": [["apiKey"]],
    "calculate_absolute_price_oscillator": [["apiKey"]],
    "calculate_ppo": [["apiKey"]],
    "calculate_momentum": [["apiKey"]],
    "get_balance_of_power": [["apiKey"]],
    "calculate_commodity_channel_index": [["apiKey"]],
    "calculate_momentum_oscillator": [["apiKey"]],
    "calculate_equity_roc": [["apiKey"]],
    "calculate_rocr": [["apiKey"]],
    "calculate_aroon_indicator": [["apiKey"]],
    "calculate_aroon_oscillator": [["apiKey"]],
    "calculate_money_flow_index": [["apiKey"]],
    "calculate_trix": [["apiKey"]],
    "calculate_ultimate_oscillator": [["apiKey"]],
    "get_directional_index": [["apiKey"]],
    "get_minus_directional_indicator": [["apiKey"]],
    "get_plus_directional_indicator": [["apiKey"]],
    "get_minus_directional_movement": [["apiKey"]],
    "get_plus_directional_movement": [["apiKey"]],
    "calculate_bollinger_bands": [["apiKey"]],
    "calculate_midpoint": [["apiKey"]],
    "calculate_midprice": [["apiKey"]],
    "get_parabolic_sar": [["apiKey"]],
    "get_true_range": [["apiKey"]],
    "get_atr": [["apiKey"]],
    "get_natr_values": [["apiKey"]],
    "get_chaikin_ad_line": [["apiKey"]],
    "get_adosc_values": [["apiKey"]],
    "get_obv": [["apiKey"]],
    "get_hilbert_trendline": [["apiKey"]],
    "get_hilbert_sine_indicator": [["apiKey"]],
    "analyze_hilbert_trend_cycle": [["apiKey"]],
    "get_dominant_cycle_period": [["apiKey"]],
    "get_dominant_cycle_phase": [["apiKey"]],
    "get_hilbert_phasor": [["apiKey"]]
}

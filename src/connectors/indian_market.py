"""
Indian Market Connector
========================
Fetches OHLCV (Open, High, Low, Close, Volume) data for NSE/BSE
equities using yfinance as the default free data provider.

For live execution, broker-specific connectors (Angel One SmartAPI,
Dhan HQ) can be plugged in by extending this module.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def fetch_ohlcv(
    symbol: str,
    period_days: int = 60,
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Fetch historical OHLCV data for an Indian equity ticker.

    Args:
        symbol: Yahoo Finance ticker (e.g. "RELIANCE.NS", "TCS.NS").
        period_days: Number of calendar days of history to fetch.
        interval: Candle interval — "1d" (daily), "1h" (hourly), "15m", "5m".

    Returns:
        DataFrame with columns: Open, High, Low, Close, Volume, indexed by Date.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days)

    ticker = yf.Ticker(symbol)
    df = ticker.history(
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
        interval=interval,
    )

    if df.empty:
        raise ValueError(f"No OHLCV data returned for {symbol}. Check ticker symbol.")

    # Standardize column names to lowercase for consistency
    df.columns = [col.lower() for col in df.columns]

    # Keep only the essential OHLCV columns
    essential_cols = ["open", "high", "low", "close", "volume"]
    available = [c for c in essential_cols if c in df.columns]
    df = df[available].copy()

    # Drop rows with missing data
    df.dropna(inplace=True)

    return df


def get_current_price(symbol: str) -> float:
    """
    Get the latest available price for an Indian equity ticker.

    Args:
        symbol: Yahoo Finance ticker (e.g. "RELIANCE.NS").

    Returns:
        Latest close price as a float.
    """
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1d")
    if hist.empty:
        raise ValueError(f"Could not fetch current price for {symbol}.")
    return float(hist["Close"].iloc[-1])


def get_market_status() -> str:
    """
    Check if Indian equity markets are currently open.
    NSE/BSE trading hours: 9:15 AM – 3:30 PM IST (Mon–Fri).

    Returns:
        "OPEN" or "CLOSED"
    """
    from datetime import timezone

    now_utc = datetime.now(timezone.utc)
    # IST = UTC + 5:30
    ist_offset = timedelta(hours=5, minutes=30)
    now_ist = now_utc + ist_offset

    # Weekend check
    if now_ist.weekday() >= 5:  # Saturday=5, Sunday=6
        return "CLOSED"

    market_open = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now_ist.replace(hour=15, minute=30, second=0, microsecond=0)

    if market_open <= now_ist <= market_close:
        return "OPEN"
    return "CLOSED"

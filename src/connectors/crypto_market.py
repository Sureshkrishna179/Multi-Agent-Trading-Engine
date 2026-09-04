"""
Crypto Market Connector
========================
Fetches OHLCV data and current prices for cryptocurrency trading pairs
using the CCXT library, which provides a unified API across 100+ exchanges
(Binance, Delta Exchange India, Bybit, KuCoin, etc.).
"""

import ccxt
import pandas as pd
from datetime import datetime, timedelta, timezone
from src import config


def _get_exchange(exchange_name: str = "kucoin") -> ccxt.Exchange:
    """
    Initialize and return a CCXT exchange instance.

    Args:
        exchange_name: Exchange identifier (e.g. "binance", "delta", "bybit").

    Returns:
        Configured CCXT exchange object.
    """
    exchange_map = {
        "binance": ccxt.binance,
        "bybit": ccxt.bybit,
        "kucoin": ccxt.kucoin,
    }

    exchange_class = exchange_map.get(exchange_name.lower(), ccxt.binance)

    # Use API keys if available (for live execution), otherwise public-only
    api_key = ""
    api_secret = ""

    if exchange_name.lower() == "binance":
        api_key = config.BINANCE_API_KEY
        api_secret = config.BINANCE_API_SECRET

    exchange_config = {"enableRateLimit": True}
    if api_key and api_secret:
        exchange_config["apiKey"] = api_key
        exchange_config["secret"] = api_secret

    return exchange_class(exchange_config)


def fetch_ohlcv(
    symbol: str,
    exchange_name: str = "kucoin",
    timeframe: str = "1d",
    limit: int = 60,
) -> pd.DataFrame:
    """
    Fetch historical OHLCV data for a crypto trading pair.

    Args:
        symbol: Trading pair (e.g. "BTC/USDT", "ETH/USDT").
        exchange_name: Exchange to fetch from (default: "kucoin").
        timeframe: Candle interval — "1d", "4h", "1h", "15m", "5m".
        limit: Number of candles to fetch (max varies by exchange).

    Returns:
        DataFrame with columns: open, high, low, close, volume, indexed by datetime.
    """
    exchange = _get_exchange(exchange_name)

    # Fetch OHLCV candles: returns [[timestamp, O, H, L, C, V], ...]
    raw = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    if not raw:
        raise ValueError(f"No OHLCV data returned for {symbol} on {exchange_name}.")

    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)

    return df


def get_current_price(
    symbol: str,
    exchange_name: str = "kucoin",
) -> float:
    """
    Get the latest ticker price for a crypto trading pair.

    Args:
        symbol: Trading pair (e.g. "BTC/USDT").
        exchange_name: Exchange to query.

    Returns:
        Latest price as a float.
    """
    exchange = _get_exchange(exchange_name)
    ticker = exchange.fetch_ticker(symbol)
    return float(ticker["last"])


def get_market_status() -> str:
    """
    Crypto markets are 24/7 — always open.

    Returns:
        Always returns "OPEN".
    """
    return "OPEN"

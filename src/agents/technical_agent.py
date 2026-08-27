"""
Agent 1: Technical & Market Observer
======================================
Pure deterministic numerical analysis — ZERO LLM involvement.
Computes RSI, SMA, MACD, ATR, Bollinger Bands and detects
candlestick patterns from raw OHLCV data using pandas & ta library.

Output: Structured dict with indicator values, trend status, and
a normalized Technical Confidence Score (-1.0 to +1.0).
"""

import pandas as pd
import numpy as np
import ta
from src import config


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute all technical indicators on an OHLCV DataFrame.

    Adds columns: rsi, sma_20, sma_50, sma_200, macd, macd_signal,
    macd_histogram, atr, bb_upper, bb_lower, bb_middle.

    Args:
        df: DataFrame with columns [open, high, low, close, volume].

    Returns:
        DataFrame with indicator columns appended.
    """
    close = df["close"]
    high = df["high"]
    low = df["low"]

    # RSI (14-period)
    df["rsi"] = ta.momentum.RSIIndicator(
        close=close, window=config.RSI_PERIOD
    ).rsi()

    # Simple Moving Averages
    df["sma_20"] = ta.trend.SMAIndicator(
        close=close, window=config.SMA_SHORT
    ).sma_indicator()

    df["sma_50"] = ta.trend.SMAIndicator(
        close=close, window=config.SMA_MEDIUM
    ).sma_indicator()

    df["sma_200"] = ta.trend.SMAIndicator(
        close=close, window=config.SMA_LONG
    ).sma_indicator()

    # MACD (12, 26, 9)
    macd_obj = ta.trend.MACD(
        close=close,
        window_slow=config.MACD_SLOW,
        window_fast=config.MACD_FAST,
        window_sign=config.MACD_SIGNAL,
    )
    df["macd"] = macd_obj.macd()
    df["macd_signal"] = macd_obj.macd_signal()
    df["macd_histogram"] = macd_obj.macd_diff()

    # ATR (14-period)
    df["atr"] = ta.volatility.AverageTrueRange(
        high=high, low=low, close=close, window=config.ATR_PERIOD
    ).average_true_range()

    # Bollinger Bands (20-period, 2 std)
    bb_obj = ta.volatility.BollingerBands(
        close=close,
        window=config.BOLLINGER_PERIOD,
        window_dev=config.BOLLINGER_STD,
    )
    df["bb_upper"] = bb_obj.bollinger_hband()
    df["bb_middle"] = bb_obj.bollinger_mavg()
    df["bb_lower"] = bb_obj.bollinger_lband()

    return df


def detect_candlestick_patterns(df: pd.DataFrame) -> list[str]:
    """
    Detect common candlestick patterns from the last 3 candles.

    Returns:
        List of detected pattern names (e.g. ["Bullish Engulfing", "Hammer"]).
    """
    patterns = []

    if len(df) < 3:
        return patterns

    curr = df.iloc[-1]
    prev = df.iloc[-2]

    body_curr = curr["close"] - curr["open"]
    body_prev = prev["close"] - prev["open"]
    upper_wick = curr["high"] - max(curr["open"], curr["close"])
    lower_wick = min(curr["open"], curr["close"]) - curr["low"]
    body_size = abs(body_curr)

    # Doji: very small body relative to range
    candle_range = curr["high"] - curr["low"]
    if candle_range > 0 and body_size / candle_range < 0.1:
        patterns.append("Doji")

    # Hammer: small body at top, long lower wick (> 2x body)
    if body_size > 0 and lower_wick > 2 * body_size and upper_wick < body_size:
        patterns.append("Hammer")

    # Shooting Star: small body at bottom, long upper wick (> 2x body)
    if body_size > 0 and upper_wick > 2 * body_size and lower_wick < body_size:
        patterns.append("Shooting Star")

    # Bullish Engulfing: prev red, curr green, curr body engulfs prev body
    if body_prev < 0 and body_curr > 0:
        if curr["open"] <= prev["close"] and curr["close"] >= prev["open"]:
            patterns.append("Bullish Engulfing")

    # Bearish Engulfing: prev green, curr red, curr body engulfs prev body
    if body_prev > 0 and body_curr < 0:
        if curr["open"] >= prev["close"] and curr["close"] <= prev["open"]:
            patterns.append("Bearish Engulfing")

    return patterns


def detect_breakout(df: pd.DataFrame) -> dict:
    """
    Detect if the latest close has broken above or below recent SMA levels.

    Returns:
        Dict with breakout status and direction.
    """
    if len(df) < 2:
        return {"breakout": False, "direction": "NONE"}

    curr = df.iloc[-1]
    prev = df.iloc[-2]

    # Breakout above SMA 20 (price crossed from below to above)
    if pd.notna(curr.get("sma_20")) and pd.notna(prev.get("sma_20")):
        if prev["close"] < prev["sma_20"] and curr["close"] > curr["sma_20"]:
            return {"breakout": True, "direction": "BULLISH_BREAKOUT_SMA20"}
        if prev["close"] > prev["sma_20"] and curr["close"] < curr["sma_20"]:
            return {"breakout": True, "direction": "BEARISH_BREAKDOWN_SMA20"}

    return {"breakout": False, "direction": "NONE"}


def determine_trend(df: pd.DataFrame) -> str:
    """
    Determine the macro trend based on SMA alignment.

    Returns:
        "BULLISH", "BEARISH", or "SIDEWAYS".
    """
    curr = df.iloc[-1]

    sma_20 = curr.get("sma_20")
    sma_50 = curr.get("sma_50")
    price = curr["close"]

    if pd.isna(sma_20) or pd.isna(sma_50):
        return "SIDEWAYS"

    if price > sma_20 > sma_50:
        return "BULLISH"
    elif price < sma_20 < sma_50:
        return "BEARISH"
    else:
        return "SIDEWAYS"


def compute_technical_score(df: pd.DataFrame) -> float:
    """
    Calculate a normalized Technical Confidence Score from -1.0 to +1.0.
    Combines RSI, MACD, trend, and breakout signals.

    Returns:
        Score between -1.0 (strong bearish) and +1.0 (strong bullish).
    """
    score = 0.0
    curr = df.iloc[-1]

    # RSI component (-0.3 to +0.3)
    rsi = curr.get("rsi")
    if pd.notna(rsi):
        if rsi < 30:
            score += 0.2   # Oversold — potential bullish reversal
        elif rsi < 45:
            score += 0.1
        elif rsi > 70:
            score -= 0.3   # Overbought — bearish pressure
        elif rsi > 55:
            score += 0.15  # Healthy momentum

    # MACD component (-0.25 to +0.25)
    macd_hist = curr.get("macd_histogram")
    if pd.notna(macd_hist):
        if macd_hist > 0:
            score += 0.25
        else:
            score -= 0.25

    # Trend component (-0.25 to +0.25)
    trend = determine_trend(df)
    if trend == "BULLISH":
        score += 0.25
    elif trend == "BEARISH":
        score -= 0.25

    # Breakout component (-0.2 to +0.2)
    breakout = detect_breakout(df)
    if breakout["breakout"]:
        if "BULLISH" in breakout["direction"]:
            score += 0.2
        elif "BEARISH" in breakout["direction"]:
            score -= 0.2

    # Clamp to [-1.0, +1.0]
    return max(-1.0, min(1.0, round(score, 4)))


def analyze(df: pd.DataFrame, symbol: str = "") -> dict:
    """
    Full technical analysis pipeline for Agent 1.

    Args:
        df: Raw OHLCV DataFrame.
        symbol: Ticker symbol for labeling.

    Returns:
        Complete technical analysis payload (JSON-serializable dict).
    """
    # Step 1: Compute all indicators
    df = compute_indicators(df)

    # Step 2: Get the latest row for snapshot
    latest = df.iloc[-1]

    # Step 3: Build the output payload
    payload = {
        "agent": "Technical Observer (Agent 1)",
        "symbol": symbol,
        "latest_price": round(float(latest["close"]), 4),
        "indicators": {
            "rsi_14": round(float(latest["rsi"]), 2) if pd.notna(latest.get("rsi")) else None,
            "sma_20": round(float(latest["sma_20"]), 4) if pd.notna(latest.get("sma_20")) else None,
            "sma_50": round(float(latest["sma_50"]), 4) if pd.notna(latest.get("sma_50")) else None,
            "sma_200": round(float(latest["sma_200"]), 4) if pd.notna(latest.get("sma_200")) else None,
            "macd": round(float(latest["macd"]), 4) if pd.notna(latest.get("macd")) else None,
            "macd_signal": round(float(latest["macd_signal"]), 4) if pd.notna(latest.get("macd_signal")) else None,
            "macd_histogram": round(float(latest["macd_histogram"]), 4) if pd.notna(latest.get("macd_histogram")) else None,
            "atr_14": round(float(latest["atr"]), 4) if pd.notna(latest.get("atr")) else None,
            "bollinger_upper": round(float(latest["bb_upper"]), 4) if pd.notna(latest.get("bb_upper")) else None,
            "bollinger_lower": round(float(latest["bb_lower"]), 4) if pd.notna(latest.get("bb_lower")) else None,
        },
        "trend": determine_trend(df),
        "breakout": detect_breakout(df),
        "candlestick_patterns": detect_candlestick_patterns(df),
        "technical_score": compute_technical_score(df),
    }

    return payload

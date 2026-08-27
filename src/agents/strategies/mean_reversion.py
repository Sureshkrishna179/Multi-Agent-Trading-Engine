"""
Mean Reversion Strategies (#97–#101)
======================================
5 strategies for ranging/sideways markets where price snaps back to average.
"""

import pandas as pd
import numpy as np
from src.agents.strategies import BaseStrategy, MarketRegime


# ── #97: RSI Mean Reversion ───────────────────────────────────

class RSIMeanReversion(BaseStrategy):
    name = "RSI Mean Reversion"
    category = "mean_reversion"
    description = "RSI extreme in ranging market = revert to 50"
    suitable_regimes = [MarketRegime.RANGING]
    weight = 1.2

    def evaluate(self, df, sentiment_data=None):
        if "rsi" not in df.columns:
            return self._not_triggered()
        rsi = df["rsi"].iloc[-1]
        if pd.isna(rsi):
            return self._not_triggered()
        # Only in ranging markets (checked by regime classifier), extreme RSI
        if rsi < 25:
            return self._triggered("BUY", min(0.8, (25 - rsi) / 25), f"RSI={rsi:.1f} extreme oversold in range — reversion to 50 expected")
        if rsi > 75:
            return self._triggered("SELL", min(0.8, (rsi - 75) / 25), f"RSI={rsi:.1f} extreme overbought in range — reversion to 50 expected")
        return self._not_triggered()


# ── #98: Bollinger Mean Reversion ─────────────────────────────

class BollingerMeanReversion(BaseStrategy):
    name = "Bollinger Mean Reversion"
    category = "mean_reversion"
    description = "Price at outer BB in low-ADX market = revert to middle"
    suitable_regimes = [MarketRegime.RANGING]
    weight = 1.3

    def evaluate(self, df, sentiment_data=None):
        if "bb_upper" not in df.columns or "bb_lower" not in df.columns or "bb_middle" not in df.columns:
            return self._not_triggered()
        curr = df.iloc[-1]
        price = curr["close"]
        bb_u = curr["bb_upper"]
        bb_l = curr["bb_lower"]
        bb_m = curr["bb_middle"]

        if pd.isna(bb_u) or pd.isna(bb_l) or pd.isna(bb_m):
            return self._not_triggered()

        bb_range = bb_u - bb_l
        if bb_range <= 0:
            return self._not_triggered()

        # Position within bands (0 = lower, 1 = upper)
        position = (price - bb_l) / bb_range

        if position < 0.05:  # Very close to lower band
            return self._triggered("BUY", 0.7, f"Price at {position:.0%} of BB range — strong reversion to middle ({bb_m:.2f}) expected")
        if position > 0.95:  # Very close to upper band
            return self._triggered("SELL", 0.7, f"Price at {position:.0%} of BB range — reversion to middle ({bb_m:.2f}) expected")
        return self._not_triggered()


# ── #99: Z-Score Reversion ────────────────────────────────────

class ZScoreReversion(BaseStrategy):
    name = "Z-Score Reversion"
    category = "mean_reversion"
    description = "Z-score > 2 or < -2 = statistically overextended"
    suitable_regimes = [MarketRegime.RANGING, MarketRegime.VOLATILE]
    weight = 1.4

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20:
            return self._not_triggered()
        close = df["close"].iloc[-20:]
        mean = close.mean()
        std = close.std()
        if std <= 0:
            return self._not_triggered()
        z_score = (df["close"].iloc[-1] - mean) / std

        if z_score < -2:
            return self._triggered("BUY", min(0.8, abs(z_score) * 0.3), f"Z-score={z_score:.2f} — statistically oversold, reversion likely")
        if z_score > 2:
            return self._triggered("SELL", min(0.8, z_score * 0.3), f"Z-score={z_score:.2f} — statistically overbought, reversion likely")
        return self._not_triggered()


# ── #100: VWAP Mean Reversion ─────────────────────────────────

class VWAPMeanReversion(BaseStrategy):
    name = "VWAP Mean Reversion"
    category = "mean_reversion"
    description = "Price deviates far from VWAP intraday = snap back"
    suitable_regimes = [MarketRegime.RANGING, MarketRegime.VOLATILE]
    weight = 1.3

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 10 or "volume" not in df.columns:
            return self._not_triggered()
        typical = (df["high"] + df["low"] + df["close"]) / 3
        vwap = (typical * df["volume"]).cumsum() / df["volume"].cumsum()
        curr_vwap = vwap.iloc[-1]
        price = df["close"].iloc[-1]

        if pd.isna(curr_vwap) or curr_vwap <= 0:
            return self._not_triggered()

        deviation_pct = (price - curr_vwap) / curr_vwap * 100

        if deviation_pct < -3:
            return self._triggered("BUY", min(0.75, abs(deviation_pct) * 0.15), f"Price {deviation_pct:.1f}% below VWAP — reversion expected")
        if deviation_pct > 3:
            return self._triggered("SELL", min(0.75, deviation_pct * 0.15), f"Price +{deviation_pct:.1f}% above VWAP — reversion expected")
        return self._not_triggered()


# ── #101: Moving Average Reversion ────────────────────────────

class MAMeanReversion(BaseStrategy):
    name = "MA Mean Reversion"
    category = "mean_reversion"
    description = "Price > 3% from SMA 20 in ranging market = revert"
    suitable_regimes = [MarketRegime.RANGING]
    weight = 1.1

    def evaluate(self, df, sentiment_data=None):
        if "sma_20" not in df.columns:
            return self._not_triggered()
        curr = df.iloc[-1]
        price = curr["close"]
        sma = curr["sma_20"]
        if pd.isna(sma) or sma <= 0:
            return self._not_triggered()

        deviation = (price - sma) / sma * 100

        if deviation < -3:
            return self._triggered("BUY", min(0.7, abs(deviation) * 0.15), f"Price {deviation:.1f}% below SMA 20 — mean reversion buy")
        if deviation > 3:
            return self._triggered("SELL", min(0.7, deviation * 0.15), f"Price +{deviation:.1f}% above SMA 20 — mean reversion sell")
        return self._not_triggered()

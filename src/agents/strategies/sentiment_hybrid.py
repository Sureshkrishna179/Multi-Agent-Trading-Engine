"""
Sentiment & Hybrid Strategies (#102–#111)
==========================================
10 strategies combining news/macro sentiment with technical signals.
"""

import pandas as pd
import numpy as np
from src.agents.strategies import BaseStrategy, MarketRegime


# ── #102: Sentiment Momentum ─────────────────────────────────

class SentimentMomentum(BaseStrategy):
    name = "Sentiment Momentum"
    category = "sentiment"
    description = "Bullish sentiment + bullish technicals = high conviction"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.BREAKOUT]
    weight = 1.5

    def evaluate(self, df, sentiment_data=None):
        if not sentiment_data:
            return self._not_triggered()
        score = sentiment_data.get("sentiment_score", 50)
        if "rsi" not in df.columns:
            return self._not_triggered()
        rsi = df["rsi"].iloc[-1]
        sma_20 = df.get("sma_20")
        price = df["close"].iloc[-1]

        if pd.notna(rsi) and sma_20 is not None and pd.notna(sma_20.iloc[-1]):
            if score > 70 and rsi > 50 and rsi < 70 and price > sma_20.iloc[-1]:
                conf = min(0.85, score / 100 * 0.5 + 0.35)
                return self._triggered("BUY", conf, f"Sentiment={score}/100 + RSI={rsi:.0f} + above SMA20 — high conviction bullish")
        return self._not_triggered()


# ── #103: Sentiment Contrarian Panic ──────────────────────────

class SentimentContrarianPanic(BaseStrategy):
    name = "Sentiment Contrarian Panic"
    category = "sentiment"
    description = "Extreme panic + RSI oversold = bottom fishing"
    suitable_regimes = [MarketRegime.VOLATILE, MarketRegime.SHOCK, MarketRegime.TRENDING_BEARISH]
    weight = 1.8

    def evaluate(self, df, sentiment_data=None):
        if not sentiment_data:
            return self._not_triggered()
        score = sentiment_data.get("sentiment_score", 50)
        if "rsi" not in df.columns:
            return self._not_triggered()
        rsi = df["rsi"].iloc[-1]

        if pd.notna(rsi) and score < 15 and rsi < 30:
            return self._triggered("BUY", 0.75, f"Extreme panic ({score}/100) + RSI={rsi:.0f} oversold — contrarian bottom fishing")
        return self._not_triggered()


# ── #104: Sentiment Shock Override ────────────────────────────

class SentimentShockOverride(BaseStrategy):
    name = "Sentiment Shock Override"
    category = "sentiment"
    description = "Sudden sentiment drop > 30pts = force HOLD"
    suitable_regimes = [MarketRegime.SHOCK, MarketRegime.VOLATILE]
    weight = 2.0

    def evaluate(self, df, sentiment_data=None):
        if not sentiment_data:
            return self._not_triggered()
        score = sentiment_data.get("sentiment_score", 50)
        label = sentiment_data.get("sentiment_label", "NEUTRAL")

        if score < 10 or label == "EXTREME_PANIC":
            return self._triggered("HOLD", 0.95, f"SHOCK OVERRIDE — Sentiment={score}/100 ({label}). Forcing HOLD. Markets in crisis mode.")
        if score > 90 or label == "EXTREME_GREED":
            return self._triggered("HOLD", 0.9, f"GREED OVERRIDE — Sentiment={score}/100 ({label}). Forcing HOLD. Bubble risk.")
        return self._not_triggered()


# ── #105: Gap & Go Morning ────────────────────────────────────

class GapAndGo(BaseStrategy):
    name = "Gap and Go"
    category = "sentiment"
    description = "Stock gaps up > 2% at open with volume + positive news"
    suitable_regimes = [MarketRegime.BREAKOUT, MarketRegime.TRENDING_BULLISH]
    weight = 1.3

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 2:
            return self._not_triggered()
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        gap_pct = (curr["open"] - prev["close"]) / prev["close"] * 100

        sentiment_ok = True
        if sentiment_data:
            sentiment_ok = sentiment_data.get("sentiment_score", 50) > 50

        if gap_pct > 2 and curr["close"] > curr["open"] and sentiment_ok:
            return self._triggered("BUY", min(0.75, gap_pct * 0.15), f"Gap & Go — {gap_pct:.1f}% gap up with positive follow-through")
        return self._not_triggered()


# ── #106: Gap Fill Counter ────────────────────────────────────

class GapFillCounter(BaseStrategy):
    name = "Gap Fill Counter"
    category = "sentiment"
    description = "Gap up but sentiment is bearish = gap will fill"
    suitable_regimes = [MarketRegime.VOLATILE, MarketRegime.RANGING]
    weight = 1.1

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 2 or not sentiment_data:
            return self._not_triggered()
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        gap_pct = (curr["open"] - prev["close"]) / prev["close"] * 100
        score = sentiment_data.get("sentiment_score", 50)

        if gap_pct > 2 and score < 40:
            return self._triggered("SELL", 0.6, f"Gap up {gap_pct:.1f}% but sentiment bearish ({score}/100) — gap fill expected")
        if gap_pct < -2 and score > 60:
            return self._triggered("BUY", 0.6, f"Gap down {gap_pct:.1f}% but sentiment bullish ({score}/100) — gap fill expected")
        return self._not_triggered()


# ── #107: Breakout Pullback Retest ────────────────────────────

class BreakoutPullbackRetest(BaseStrategy):
    name = "Breakout Pullback Retest"
    category = "sentiment"
    description = "After breakout, pullback to retest as new support"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.BREAKOUT]
    weight = 1.5

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 25:
            return self._not_triggered()
        # Find recent breakout level (20-day high excluding last 5 bars)
        resistance = df["high"].iloc[-25:-5].max()
        # Check if price recently broke above it
        broke_above = any(df["close"].iloc[-5:-1] > resistance)
        # Now pulled back near it
        curr_price = df["close"].iloc[-1]
        near_level = abs(curr_price - resistance) / resistance < 0.015

        if broke_above and near_level and curr_price >= resistance:
            return self._triggered("BUY", 0.73, f"Pullback retest of breakout level {resistance:.2f} — new support confirmed")
        return self._not_triggered()


# ── #108: Opening Range Breakout ──────────────────────────────

class OpeningRangeBreakout(BaseStrategy):
    name = "Opening Range Breakout"
    category = "sentiment"
    description = "First 15-min H/L → breakout direction"
    suitable_regimes = [MarketRegime.BREAKOUT, MarketRegime.VOLATILE]
    weight = 1.2

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 5:
            return self._not_triggered()
        # Use first candle as proxy for opening range
        first = df.iloc[0]
        curr = df.iloc[-1]
        or_high = first["high"]
        or_low = first["low"]
        or_range = or_high - or_low

        if or_range > 0 and curr["close"] > or_high:
            return self._triggered("BUY", 0.65, f"Opening range breakout — above {or_high:.2f}")
        if or_range > 0 and curr["close"] < or_low:
            return self._triggered("SELL", 0.65, f"Opening range breakdown — below {or_low:.2f}")
        return self._not_triggered()


# ── #109: News Catalyst Momentum ──────────────────────────────

class NewsCatalystMomentum(BaseStrategy):
    name = "News Catalyst Momentum"
    category = "sentiment"
    description = "Major positive news + volume spike = ride momentum"
    suitable_regimes = [MarketRegime.BREAKOUT, MarketRegime.VOLATILE]
    weight = 1.6

    def evaluate(self, df, sentiment_data=None):
        if not sentiment_data or len(df) < 5 or "volume" not in df.columns:
            return self._not_triggered()
        score = sentiment_data.get("sentiment_score", 50)
        headlines = sentiment_data.get("headlines_analyzed", 0)
        curr = df.iloc[-1]
        avg_vol = df["volume"].iloc[-20:].mean() if len(df) >= 20 else df["volume"].mean()

        if pd.isna(avg_vol) or avg_vol <= 0:
            return self._not_triggered()

        vol_ratio = curr["volume"] / avg_vol
        price_change = (curr["close"] - curr["open"]) / curr["open"] * 100

        if score > 75 and vol_ratio > 2 and price_change > 1 and headlines > 3:
            return self._triggered("BUY", min(0.82, score / 100 * 0.5 + vol_ratio * 0.1),
                                   f"News catalyst — sentiment={score}/100, volume {vol_ratio:.1f}x, +{price_change:.1f}%")
        if score < 25 and vol_ratio > 2 and price_change < -1 and headlines > 3:
            return self._triggered("SELL", min(0.82, (100 - score) / 100 * 0.5 + vol_ratio * 0.1),
                                   f"Negative news catalyst — sentiment={score}/100, volume {vol_ratio:.1f}x, {price_change:.1f}%")
        return self._not_triggered()


# ── #110: Fear & Greed Extreme ────────────────────────────────

class FearGreedExtreme(BaseStrategy):
    name = "Fear and Greed Extreme"
    category = "sentiment"
    description = "Sentiment at extremes = contrarian position"
    suitable_regimes = [MarketRegime.VOLATILE, MarketRegime.SHOCK]
    weight = 1.4

    def evaluate(self, df, sentiment_data=None):
        if not sentiment_data:
            return self._not_triggered()
        score = sentiment_data.get("sentiment_score", 50)

        if score < 20:
            return self._triggered("BUY", min(0.7, (20 - score) / 20 * 0.7),
                                   f"Fear extreme ({score}/100) — contrarian buy opportunity")
        if score > 80:
            return self._triggered("SELL", min(0.7, (score - 80) / 20 * 0.7),
                                   f"Greed extreme ({score}/100) — contrarian sell/reduce exposure")
        return self._not_triggered()


# ── #111: Multi-Timeframe Confluence ──────────────────────────

class MultiTimeframeConfluence(BaseStrategy):
    name = "Multi-Timeframe Confluence"
    category = "sentiment"
    description = "All indicators agree = highest conviction"
    suitable_regimes = []  # All regimes
    weight = 2.0

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 50 or "rsi" not in df.columns or "sma_20" not in df.columns:
            return self._not_triggered()

        curr = df.iloc[-1]
        price = curr["close"]
        rsi = curr.get("rsi")
        sma_20 = curr.get("sma_20")
        sma_50 = curr.get("sma_50")
        macd_hist = curr.get("macd_histogram")

        if any(pd.isna(x) for x in [rsi, sma_20, sma_50, macd_hist]):
            return self._not_triggered()

        # All bullish
        bullish_count = 0
        if price > sma_20:
            bullish_count += 1
        if price > sma_50:
            bullish_count += 1
        if rsi > 50 and rsi < 70:
            bullish_count += 1
        if macd_hist > 0:
            bullish_count += 1

        sentiment_bullish = False
        if sentiment_data and sentiment_data.get("sentiment_score", 50) > 55:
            bullish_count += 1
            sentiment_bullish = True

        if bullish_count >= 4:
            return self._triggered("BUY", min(0.9, bullish_count * 0.18),
                                   f"Multi-timeframe confluence — {bullish_count}/5 factors bullish (RSI={rsi:.0f}, MACD+, above SMAs{'+ sentiment' if sentiment_bullish else ''})")

        # All bearish
        bearish_count = 0
        if price < sma_20:
            bearish_count += 1
        if price < sma_50:
            bearish_count += 1
        if rsi < 50 and rsi > 30:
            bearish_count += 1
        if macd_hist < 0:
            bearish_count += 1
        if sentiment_data and sentiment_data.get("sentiment_score", 50) < 45:
            bearish_count += 1

        if bearish_count >= 4:
            return self._triggered("SELL", min(0.9, bearish_count * 0.18),
                                   f"Multi-timeframe confluence — {bearish_count}/5 factors bearish")
        return self._not_triggered()

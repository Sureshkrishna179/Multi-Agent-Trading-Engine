"""
Candlestick Pattern Strategies (#1–#31)
=========================================
31 candlestick pattern recognition strategies.
Each detects a specific single/multi-candle formation and generates
a BUY, SELL, or HOLD signal with confidence scoring.
"""

import pandas as pd
import numpy as np
from src.agents.strategies import BaseStrategy, MarketRegime


# ── Helper Functions ────────────────────────────────────────────

def _body(candle) -> float:
    """Signed body: positive = green, negative = red."""
    return candle["close"] - candle["open"]

def _body_size(candle) -> float:
    """Absolute body size."""
    return abs(candle["close"] - candle["open"])

def _upper_wick(candle) -> float:
    return candle["high"] - max(candle["open"], candle["close"])

def _lower_wick(candle) -> float:
    return min(candle["open"], candle["close"]) - candle["low"]

def _range(candle) -> float:
    return candle["high"] - candle["low"]

def _is_green(candle) -> bool:
    return candle["close"] > candle["open"]

def _is_red(candle) -> bool:
    return candle["close"] < candle["open"]


# ── #1: Bullish Engulfing ───────────────────────────────────────

class BullishEngulfing(BaseStrategy):
    name = "Bullish Engulfing"
    category = "candlestick"
    description = "Green candle fully engulfs prior red candle"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING, MarketRegime.VOLATILE]
    weight = 1.0

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 2:
            return self._not_triggered()
        curr, prev = df.iloc[-1], df.iloc[-2]
        if _is_red(prev) and _is_green(curr):
            if curr["open"] <= prev["close"] and curr["close"] >= prev["open"]:
                conf = min(0.8, _body_size(curr) / (_range(curr) + 1e-10) * 0.9)
                return self._triggered("BUY", conf, f"Green candle engulfs prior red. Body ratio: {conf:.2f}")
        return self._not_triggered()


# ── #2: Bearish Engulfing ───────────────────────────────────────

class BearishEngulfing(BaseStrategy):
    name = "Bearish Engulfing"
    category = "candlestick"
    description = "Red candle fully engulfs prior green candle"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.RANGING, MarketRegime.VOLATILE]
    weight = 1.0

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 2:
            return self._not_triggered()
        curr, prev = df.iloc[-1], df.iloc[-2]
        if _is_green(prev) and _is_red(curr):
            if curr["open"] >= prev["close"] and curr["close"] <= prev["open"]:
                conf = min(0.8, _body_size(curr) / (_range(curr) + 1e-10) * 0.9)
                return self._triggered("SELL", conf, f"Red candle engulfs prior green. Body ratio: {conf:.2f}")
        return self._not_triggered()


# ── #3: Hammer ──────────────────────────────────────────────────

class Hammer(BaseStrategy):
    name = "Hammer"
    category = "candlestick"
    description = "Small body at top, long lower wick at support"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING]
    weight = 1.0

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 2:
            return self._not_triggered()
        curr = df.iloc[-1]
        body = _body_size(curr)
        lw = _lower_wick(curr)
        uw = _upper_wick(curr)
        if body > 0 and lw > 2 * body and uw < body:
            wick_ratio = lw / body
            return self._triggered("BUY", min(0.75, wick_ratio * 0.2), f"Hammer: lower wick {wick_ratio:.1f}x body")
        return self._not_triggered()


# ── #4: Inverted Hammer ─────────────────────────────────────────

class InvertedHammer(BaseStrategy):
    name = "Inverted Hammer"
    category = "candlestick"
    description = "Small body at bottom, long upper wick after downtrend"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING]
    weight = 0.8

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 2:
            return self._not_triggered()
        curr = df.iloc[-1]
        body = _body_size(curr)
        uw = _upper_wick(curr)
        lw = _lower_wick(curr)
        if body > 0 and uw > 2 * body and lw < body:
            return self._triggered("BUY", 0.55, f"Inverted Hammer: upper wick {uw/body:.1f}x body")
        return self._not_triggered()


# ── #5: Shooting Star ───────────────────────────────────────────

class ShootingStar(BaseStrategy):
    name = "Shooting Star"
    category = "candlestick"
    description = "Small body at bottom, long upper wick at resistance"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.RANGING]
    weight = 1.0

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 2:
            return self._not_triggered()
        curr = df.iloc[-1]
        body = _body_size(curr)
        uw = _upper_wick(curr)
        lw = _lower_wick(curr)
        if body > 0 and uw > 2 * body and lw < body:
            return self._triggered("SELL", min(0.75, uw / body * 0.2), f"Shooting Star: wick {uw/body:.1f}x body")
        return self._not_triggered()


# ── #6: Hanging Man ─────────────────────────────────────────────

class HangingMan(BaseStrategy):
    name = "Hanging Man"
    category = "candlestick"
    description = "Hammer shape at top of uptrend — exhaustion"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH]
    weight = 0.9

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 5:
            return self._not_triggered()
        curr = df.iloc[-1]
        body = _body_size(curr)
        lw = _lower_wick(curr)
        uw = _upper_wick(curr)
        # Hammer shape + uptrend context
        recent_trend = df["close"].iloc[-5:].is_monotonic_increasing
        if body > 0 and lw > 2 * body and uw < body and recent_trend:
            return self._triggered("SELL", 0.65, "Hanging Man at uptrend peak — exhaustion signal")
        return self._not_triggered()


# ── #7: Doji ────────────────────────────────────────────────────

class Doji(BaseStrategy):
    name = "Doji"
    category = "candlestick"
    description = "Body ≈ 0 — indecision"
    suitable_regimes = []  # All regimes
    weight = 0.5

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 1:
            return self._not_triggered()
        curr = df.iloc[-1]
        r = _range(curr)
        if r > 0 and _body_size(curr) / r < 0.05:
            return self._triggered("HOLD", 0.3, "Doji detected — extreme indecision, await confirmation")
        return self._not_triggered()


# ── #8: Dragonfly Doji ──────────────────────────────────────────

class DragonflyDoji(BaseStrategy):
    name = "Dragonfly Doji"
    category = "candlestick"
    description = "Doji with long lower wick — buyer rejection"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING]
    weight = 0.9

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 1:
            return self._not_triggered()
        curr = df.iloc[-1]
        r = _range(curr)
        body = _body_size(curr)
        lw = _lower_wick(curr)
        uw = _upper_wick(curr)
        if r > 0 and body / r < 0.05 and lw > r * 0.6 and uw < r * 0.1:
            return self._triggered("BUY", 0.65, "Dragonfly Doji — strong buyer rejection at lows")
        return self._not_triggered()


# ── #9: Gravestone Doji ─────────────────────────────────────────

class GravestoneDoji(BaseStrategy):
    name = "Gravestone Doji"
    category = "candlestick"
    description = "Doji with long upper wick — seller rejection"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.RANGING]
    weight = 0.9

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 1:
            return self._not_triggered()
        curr = df.iloc[-1]
        r = _range(curr)
        body = _body_size(curr)
        uw = _upper_wick(curr)
        lw = _lower_wick(curr)
        if r > 0 and body / r < 0.05 and uw > r * 0.6 and lw < r * 0.1:
            return self._triggered("SELL", 0.65, "Gravestone Doji — seller rejection at highs")
        return self._not_triggered()


# ── #10: Long-Legged Doji ───────────────────────────────────────

class LongLeggedDoji(BaseStrategy):
    name = "Long-Legged Doji"
    category = "candlestick"
    description = "Equal long wicks — extreme indecision"
    suitable_regimes = []
    weight = 0.4

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 1:
            return self._not_triggered()
        curr = df.iloc[-1]
        r = _range(curr)
        body = _body_size(curr)
        uw = _upper_wick(curr)
        lw = _lower_wick(curr)
        if r > 0 and body / r < 0.1 and uw > r * 0.3 and lw > r * 0.3:
            return self._triggered("HOLD", 0.2, "Long-Legged Doji — extreme indecision, avoid entry")
        return self._not_triggered()


# ── #11: Morning Star ───────────────────────────────────────────

class MorningStar(BaseStrategy):
    name = "Morning Star"
    category = "candlestick"
    description = "3-candle bullish reversal at bottom"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING]
    weight = 1.3

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 3:
            return self._not_triggered()
        c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
        # Big red → small body → big green
        if (_is_red(c1) and _body_size(c1) > _range(c1) * 0.4
                and _body_size(c2) < _range(c1) * 0.3
                and _is_green(c3) and _body_size(c3) > _range(c3) * 0.4
                and c3["close"] > (c1["open"] + c1["close"]) / 2):
            return self._triggered("BUY", 0.8, "Morning Star — 3-candle bullish reversal pattern")
        return self._not_triggered()


# ── #12: Evening Star ───────────────────────────────────────────

class EveningStar(BaseStrategy):
    name = "Evening Star"
    category = "candlestick"
    description = "3-candle bearish reversal at top"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.RANGING]
    weight = 1.3

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 3:
            return self._not_triggered()
        c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
        if (_is_green(c1) and _body_size(c1) > _range(c1) * 0.4
                and _body_size(c2) < _range(c1) * 0.3
                and _is_red(c3) and _body_size(c3) > _range(c3) * 0.4
                and c3["close"] < (c1["open"] + c1["close"]) / 2):
            return self._triggered("SELL", 0.8, "Evening Star — 3-candle bearish reversal pattern")
        return self._not_triggered()


# ── #13: Three White Soldiers ───────────────────────────────────

class ThreeWhiteSoldiers(BaseStrategy):
    name = "Three White Soldiers"
    category = "candlestick"
    description = "3 consecutive large green candles"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING, MarketRegime.BREAKOUT]
    weight = 1.2

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 3:
            return self._not_triggered()
        c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
        if (_is_green(c1) and _is_green(c2) and _is_green(c3)
                and c2["close"] > c1["close"] and c3["close"] > c2["close"]
                and _body_size(c1) > _range(c1) * 0.5
                and _body_size(c2) > _range(c2) * 0.5
                and _body_size(c3) > _range(c3) * 0.5):
            return self._triggered("BUY", 0.82, "Three White Soldiers — strong bullish continuation")
        return self._not_triggered()


# ── #14: Three Black Crows ──────────────────────────────────────

class ThreeBlackCrows(BaseStrategy):
    name = "Three Black Crows"
    category = "candlestick"
    description = "3 consecutive large red candles"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.RANGING, MarketRegime.BREAKOUT]
    weight = 1.2

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 3:
            return self._not_triggered()
        c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
        if (_is_red(c1) and _is_red(c2) and _is_red(c3)
                and c2["close"] < c1["close"] and c3["close"] < c2["close"]
                and _body_size(c1) > _range(c1) * 0.5
                and _body_size(c2) > _range(c2) * 0.5
                and _body_size(c3) > _range(c3) * 0.5):
            return self._triggered("SELL", 0.82, "Three Black Crows — strong bearish continuation")
        return self._not_triggered()


# ── #15: Bullish Harami ─────────────────────────────────────────

class BullishHarami(BaseStrategy):
    name = "Bullish Harami"
    category = "candlestick"
    description = "Small green inside large red — potential reversal"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING]
    weight = 0.8

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 2:
            return self._not_triggered()
        curr, prev = df.iloc[-1], df.iloc[-2]
        if (_is_red(prev) and _is_green(curr)
                and curr["open"] > prev["close"] and curr["close"] < prev["open"]
                and _body_size(curr) < _body_size(prev) * 0.5):
            return self._triggered("BUY", 0.55, "Bullish Harami — small body inside large red candle")
        return self._not_triggered()


# ── #16: Bearish Harami ─────────────────────────────────────────

class BearishHarami(BaseStrategy):
    name = "Bearish Harami"
    category = "candlestick"
    description = "Small red inside large green — potential reversal"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.RANGING]
    weight = 0.8

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 2:
            return self._not_triggered()
        curr, prev = df.iloc[-1], df.iloc[-2]
        if (_is_green(prev) and _is_red(curr)
                and curr["open"] < prev["close"] and curr["close"] > prev["open"]
                and _body_size(curr) < _body_size(prev) * 0.5):
            return self._triggered("SELL", 0.55, "Bearish Harami — small body inside large green candle")
        return self._not_triggered()


# ── #17: Piercing Line ──────────────────────────────────────────

class PiercingLine(BaseStrategy):
    name = "Piercing Line"
    category = "candlestick"
    description = "Green opens below prior close, closes above 50% of prior body"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING]
    weight = 0.9

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 2:
            return self._not_triggered()
        curr, prev = df.iloc[-1], df.iloc[-2]
        mid_prev = (prev["open"] + prev["close"]) / 2
        if (_is_red(prev) and _is_green(curr)
                and curr["open"] < prev["close"]
                and curr["close"] > mid_prev
                and curr["close"] < prev["open"]):
            return self._triggered("BUY", 0.65, "Piercing Line — closes above 50% of prior red body")
        return self._not_triggered()


# ── #18: Dark Cloud Cover ───────────────────────────────────────

class DarkCloudCover(BaseStrategy):
    name = "Dark Cloud Cover"
    category = "candlestick"
    description = "Red opens above prior close, closes below 50% of prior body"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.RANGING]
    weight = 0.9

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 2:
            return self._not_triggered()
        curr, prev = df.iloc[-1], df.iloc[-2]
        mid_prev = (prev["open"] + prev["close"]) / 2
        if (_is_green(prev) and _is_red(curr)
                and curr["open"] > prev["close"]
                and curr["close"] < mid_prev
                and curr["close"] > prev["open"]):
            return self._triggered("SELL", 0.65, "Dark Cloud Cover — closes below 50% of prior green body")
        return self._not_triggered()


# ── #19: Tweezer Top ────────────────────────────────────────────

class TweezerTop(BaseStrategy):
    name = "Tweezer Top"
    category = "candlestick"
    description = "Two candles with matching highs at resistance"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.RANGING]
    weight = 0.7

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 2:
            return self._not_triggered()
        curr, prev = df.iloc[-1], df.iloc[-2]
        high_diff = abs(curr["high"] - prev["high"])
        avg_range = (_range(curr) + _range(prev)) / 2
        if avg_range > 0 and high_diff / avg_range < 0.05 and _is_green(prev) and _is_red(curr):
            return self._triggered("SELL", 0.6, "Tweezer Top — matching highs with bearish follow-through")
        return self._not_triggered()


# ── #20: Tweezer Bottom ─────────────────────────────────────────

class TweezerBottom(BaseStrategy):
    name = "Tweezer Bottom"
    category = "candlestick"
    description = "Two candles with matching lows at support"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING]
    weight = 0.7

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 2:
            return self._not_triggered()
        curr, prev = df.iloc[-1], df.iloc[-2]
        low_diff = abs(curr["low"] - prev["low"])
        avg_range = (_range(curr) + _range(prev)) / 2
        if avg_range > 0 and low_diff / avg_range < 0.05 and _is_red(prev) and _is_green(curr):
            return self._triggered("BUY", 0.6, "Tweezer Bottom — matching lows with bullish follow-through")
        return self._not_triggered()


# ── #21: Rising Three Methods ───────────────────────────────────

class RisingThreeMethods(BaseStrategy):
    name = "Rising Three Methods"
    category = "candlestick"
    description = "Bullish continuation: big green, 3 small inside, big green"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH]
    weight = 1.1

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 5:
            return self._not_triggered()
        c1, c2, c3, c4, c5 = [df.iloc[-5+i] for i in range(5)]
        if (_is_green(c1) and _body_size(c1) > _range(c1) * 0.5
                and _is_green(c5) and _body_size(c5) > _range(c5) * 0.5
                and c5["close"] > c1["close"]
                and all(_body_size(df.iloc[-5+i]) < _body_size(c1) * 0.5 for i in [1, 2, 3])):
            return self._triggered("BUY", 0.72, "Rising Three Methods — bullish continuation pattern")
        return self._not_triggered()


# ── #22: Falling Three Methods ──────────────────────────────────

class FallingThreeMethods(BaseStrategy):
    name = "Falling Three Methods"
    category = "candlestick"
    description = "Bearish continuation: big red, 3 small inside, big red"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH]
    weight = 1.1

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 5:
            return self._not_triggered()
        c1, c2, c3, c4, c5 = [df.iloc[-5+i] for i in range(5)]
        if (_is_red(c1) and _body_size(c1) > _range(c1) * 0.5
                and _is_red(c5) and _body_size(c5) > _range(c5) * 0.5
                and c5["close"] < c1["close"]
                and all(_body_size(df.iloc[-5+i]) < _body_size(c1) * 0.5 for i in [1, 2, 3])):
            return self._triggered("SELL", 0.72, "Falling Three Methods — bearish continuation pattern")
        return self._not_triggered()


# ── #23: Bullish Marubozu ───────────────────────────────────────

class BullishMarubozu(BaseStrategy):
    name = "Bullish Marubozu"
    category = "candlestick"
    description = "Full-body green candle with no/tiny wicks"
    suitable_regimes = []
    weight = 1.0

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 1:
            return self._not_triggered()
        curr = df.iloc[-1]
        r = _range(curr)
        if r > 0 and _is_green(curr) and _body_size(curr) / r > 0.9:
            return self._triggered("BUY", 0.7, "Bullish Marubozu — maximum buyer control, no wicks")
        return self._not_triggered()


# ── #24: Bearish Marubozu ───────────────────────────────────────

class BearishMarubozu(BaseStrategy):
    name = "Bearish Marubozu"
    category = "candlestick"
    description = "Full-body red candle with no/tiny wicks"
    suitable_regimes = []
    weight = 1.0

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 1:
            return self._not_triggered()
        curr = df.iloc[-1]
        r = _range(curr)
        if r > 0 and _is_red(curr) and _body_size(curr) / r > 0.9:
            return self._triggered("SELL", 0.7, "Bearish Marubozu — maximum seller control, no wicks")
        return self._not_triggered()


# ── #25: Spinning Top ───────────────────────────────────────────

class SpinningTop(BaseStrategy):
    name = "Spinning Top"
    category = "candlestick"
    description = "Small body, equal wicks — indecision"
    suitable_regimes = []
    weight = 0.3

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 1:
            return self._not_triggered()
        curr = df.iloc[-1]
        r = _range(curr)
        body = _body_size(curr)
        uw = _upper_wick(curr)
        lw = _lower_wick(curr)
        if r > 0 and body / r < 0.3 and body / r > 0.05 and abs(uw - lw) / r < 0.2:
            return self._triggered("HOLD", 0.2, "Spinning Top — indecision, avoid entry")
        return self._not_triggered()


# ── #26: Three Inside Up ───────────────────────────────────────

class ThreeInsideUp(BaseStrategy):
    name = "Three Inside Up"
    category = "candlestick"
    description = "Bullish Harami + confirmation candle"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING]
    weight = 1.1

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 3:
            return self._not_triggered()
        c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
        # Harami + confirmation
        if (_is_red(c1) and _is_green(c2)
                and c2["open"] > c1["close"] and c2["close"] < c1["open"]
                and _body_size(c2) < _body_size(c1) * 0.5
                and _is_green(c3) and c3["close"] > c1["open"]):
            return self._triggered("BUY", 0.73, "Three Inside Up — Harami confirmed with breakout candle")
        return self._not_triggered()


# ── #27: Three Inside Down ──────────────────────────────────────

class ThreeInsideDown(BaseStrategy):
    name = "Three Inside Down"
    category = "candlestick"
    description = "Bearish Harami + confirmation candle"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.RANGING]
    weight = 1.1

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 3:
            return self._not_triggered()
        c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
        if (_is_green(c1) and _is_red(c2)
                and c2["open"] < c1["close"] and c2["close"] > c1["open"]
                and _body_size(c2) < _body_size(c1) * 0.5
                and _is_red(c3) and c3["close"] < c1["open"]):
            return self._triggered("SELL", 0.73, "Three Inside Down — Harami confirmed with breakdown candle")
        return self._not_triggered()


# ── #28: Three Outside Up ──────────────────────────────────────

class ThreeOutsideUp(BaseStrategy):
    name = "Three Outside Up"
    category = "candlestick"
    description = "Bullish Engulfing + confirmation candle"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING]
    weight = 1.2

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 3:
            return self._not_triggered()
        c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
        if (_is_red(c1) and _is_green(c2)
                and c2["open"] <= c1["close"] and c2["close"] >= c1["open"]
                and _is_green(c3) and c3["close"] > c2["close"]):
            return self._triggered("BUY", 0.78, "Three Outside Up — Engulfing confirmed with continuation")
        return self._not_triggered()


# ── #29: Three Outside Down ─────────────────────────────────────

class ThreeOutsideDown(BaseStrategy):
    name = "Three Outside Down"
    category = "candlestick"
    description = "Bearish Engulfing + confirmation candle"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.RANGING]
    weight = 1.2

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 3:
            return self._not_triggered()
        c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
        if (_is_green(c1) and _is_red(c2)
                and c2["open"] >= c1["close"] and c2["close"] <= c1["open"]
                and _is_red(c3) and c3["close"] < c2["close"]):
            return self._triggered("SELL", 0.78, "Three Outside Down — Engulfing confirmed with continuation")
        return self._not_triggered()


# ── #30: Bullish Abandoned Baby ─────────────────────────────────

class BullishAbandonedBaby(BaseStrategy):
    name = "Bullish Abandoned Baby"
    category = "candlestick"
    description = "Rare: gap-down doji followed by gap-up green"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.VOLATILE]
    weight = 1.5

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 3:
            return self._not_triggered()
        c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
        r2 = _range(c2)
        if (_is_red(c1)
                and r2 > 0 and _body_size(c2) / r2 < 0.1  # Doji
                and c2["high"] < c1["low"]  # Gap down
                and _is_green(c3) and c3["low"] > c2["high"]):  # Gap up
            return self._triggered("BUY", 0.88, "Bullish Abandoned Baby — rare high-reliability reversal")
        return self._not_triggered()


# ── #31: Bearish Abandoned Baby ─────────────────────────────────

class BearishAbandonedBaby(BaseStrategy):
    name = "Bearish Abandoned Baby"
    category = "candlestick"
    description = "Rare: gap-up doji followed by gap-down red"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.VOLATILE]
    weight = 1.5

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 3:
            return self._not_triggered()
        c1, c2, c3 = df.iloc[-3], df.iloc[-2], df.iloc[-1]
        r2 = _range(c2)
        if (_is_green(c1)
                and r2 > 0 and _body_size(c2) / r2 < 0.1  # Doji
                and c2["low"] > c1["high"]  # Gap up
                and _is_red(c3) and c3["high"] < c2["low"]):  # Gap down
            return self._triggered("SELL", 0.88, "Bearish Abandoned Baby — rare high-reliability reversal")
        return self._not_triggered()

"""
Chart Pattern Strategies (#82–#96)
====================================
15 structural price pattern strategies with measured move targets.
"""

import pandas as pd
import numpy as np
from src.agents.strategies import BaseStrategy, MarketRegime


# ── Helper: Find local highs/lows ──────────────────────────────

def _local_maxima(series: pd.Series, order: int = 5) -> pd.Series:
    """Find local maxima with given window order."""
    maxima = pd.Series(False, index=series.index)
    for i in range(order, len(series) - order):
        if series.iloc[i] == series.iloc[i - order:i + order + 1].max():
            maxima.iloc[i] = True
    return maxima

def _local_minima(series: pd.Series, order: int = 5) -> pd.Series:
    """Find local minima with given window order."""
    minima = pd.Series(False, index=series.index)
    for i in range(order, len(series) - order):
        if series.iloc[i] == series.iloc[i - order:i + order + 1].min():
            minima.iloc[i] = True
    return minima


# ── #82: Support Bounce ───────────────────────────────────────

class SupportBounce(BaseStrategy):
    name = "Support Bounce"
    category = "chart_pattern"
    description = "Price touches support level and bounces"
    suitable_regimes = [MarketRegime.RANGING, MarketRegime.TRENDING_BULLISH]
    weight = 1.3

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20:
            return self._not_triggered()
        lows = df["low"].iloc[-20:]
        support = lows.nsmallest(3).mean()
        curr = df.iloc[-1]
        threshold = support * 0.01  # 1% tolerance

        if abs(curr["low"] - support) < threshold and curr["close"] > curr["open"]:
            return self._triggered("BUY", 0.7, f"Price bounced off support at {support:.2f}")
        return self._not_triggered()


# ── #83: Resistance Rejection ─────────────────────────────────

class ResistanceRejection(BaseStrategy):
    name = "Resistance Rejection"
    category = "chart_pattern"
    description = "Price touches resistance and gets rejected"
    suitable_regimes = [MarketRegime.RANGING, MarketRegime.TRENDING_BEARISH]
    weight = 1.3

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20:
            return self._not_triggered()
        highs = df["high"].iloc[-20:]
        resistance = highs.nlargest(3).mean()
        curr = df.iloc[-1]
        threshold = resistance * 0.01

        if abs(curr["high"] - resistance) < threshold and curr["close"] < curr["open"]:
            return self._triggered("SELL", 0.7, f"Price rejected at resistance {resistance:.2f}")
        return self._not_triggered()


# ── #84: Support/Resistance Breakout ──────────────────────────

class SRBreakout(BaseStrategy):
    name = "Support/Resistance Breakout"
    category = "chart_pattern"
    description = "Price breaks through key level with volume"
    suitable_regimes = [MarketRegime.BREAKOUT, MarketRegime.RANGING]
    weight = 1.5

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 21 or "volume" not in df.columns:
            return self._not_triggered()
        highs = df["high"].iloc[-21:-1]
        lows = df["low"].iloc[-21:-1]
        resistance = highs.nlargest(3).mean()
        support = lows.nsmallest(3).mean()
        curr = df.iloc[-1]
        avg_vol = df["volume"].iloc[-21:-1].mean()
        high_vol = curr["volume"] > avg_vol * 1.3 if pd.notna(avg_vol) and avg_vol > 0 else False

        if curr["close"] > resistance and high_vol:
            return self._triggered("BUY", 0.78, f"Breakout above resistance {resistance:.2f} with volume confirmation")
        if curr["close"] < support and high_vol:
            return self._triggered("SELL", 0.78, f"Breakdown below support {support:.2f} with volume confirmation")
        return self._not_triggered()


# ── #85: Double Top ───────────────────────────────────────────

class DoubleTop(BaseStrategy):
    name = "Double Top"
    category = "chart_pattern"
    description = "Two peaks at same level + neckline break"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.RANGING]
    weight = 1.5

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 30:
            return self._not_triggered()
        highs = df["high"]
        maxima = _local_maxima(highs, order=5)
        peaks = highs[maxima].tail(2)

        if len(peaks) >= 2:
            p1, p2 = peaks.iloc[-2], peaks.iloc[-1]
            tolerance = p1 * 0.02
            if abs(p1 - p2) < tolerance:
                neckline = df["low"].iloc[peaks.index[-2]:peaks.index[-1]].min() if hasattr(peaks.index[-2], '__index__') else df["low"].iloc[-15:].min()
                if df["close"].iloc[-1] < neckline:
                    return self._triggered("SELL", 0.8, f"Double Top — peaks at ~{p1:.2f}, neckline broken at {neckline:.2f}")
        return self._not_triggered()


# ── #86: Double Bottom ────────────────────────────────────────

class DoubleBottom(BaseStrategy):
    name = "Double Bottom"
    category = "chart_pattern"
    description = "Two troughs at same level + neckline break"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING]
    weight = 1.5

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 30:
            return self._not_triggered()
        lows = df["low"]
        minima = _local_minima(lows, order=5)
        troughs = lows[minima].tail(2)

        if len(troughs) >= 2:
            t1, t2 = troughs.iloc[-2], troughs.iloc[-1]
            tolerance = t1 * 0.02
            if abs(t1 - t2) < tolerance:
                neckline = df["high"].iloc[-15:].max()
                if df["close"].iloc[-1] > neckline:
                    return self._triggered("BUY", 0.8, f"Double Bottom — troughs at ~{t1:.2f}, neckline broken at {neckline:.2f}")
        return self._not_triggered()


# ── #87: Head & Shoulders ─────────────────────────────────────

class HeadAndShoulders(BaseStrategy):
    name = "Head and Shoulders"
    category = "chart_pattern"
    description = "Classic bearish reversal pattern"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH]
    weight = 1.8

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 40:
            return self._not_triggered()
        highs = df["high"]
        maxima = _local_maxima(highs, order=5)
        peaks = highs[maxima].tail(3)

        if len(peaks) >= 3:
            ls, head, rs = peaks.iloc[-3], peaks.iloc[-2], peaks.iloc[-1]
            # Head must be highest, shoulders roughly equal
            if head > ls and head > rs and abs(ls - rs) / head < 0.03:
                neckline = df["low"].iloc[-20:].quantile(0.25)
                if df["close"].iloc[-1] < neckline:
                    return self._triggered("SELL", 0.85, f"Head & Shoulders — head={head:.2f}, shoulders=~{ls:.2f}, neckline broken")
        return self._not_triggered()


# ── #88: Inverse Head & Shoulders ─────────────────────────────

class InverseHeadAndShoulders(BaseStrategy):
    name = "Inverse Head and Shoulders"
    category = "chart_pattern"
    description = "Bullish reversal at bottom of downtrend"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH]
    weight = 1.8

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 40:
            return self._not_triggered()
        lows = df["low"]
        minima = _local_minima(lows, order=5)
        troughs = lows[minima].tail(3)

        if len(troughs) >= 3:
            ls, head, rs = troughs.iloc[-3], troughs.iloc[-2], troughs.iloc[-1]
            if head < ls and head < rs and abs(ls - rs) / (abs(head) + 1e-10) < 0.03:
                neckline = df["high"].iloc[-20:].quantile(0.75)
                if df["close"].iloc[-1] > neckline:
                    return self._triggered("BUY", 0.85, f"Inverse H&S — head={head:.2f}, neckline broken")
        return self._not_triggered()


# ── #89: Ascending Triangle ───────────────────────────────────

class AscendingTriangle(BaseStrategy):
    name = "Ascending Triangle"
    category = "chart_pattern"
    description = "Flat resistance + rising support = bullish breakout"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.RANGING]
    weight = 1.4

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20:
            return self._not_triggered()
        highs = df["high"].iloc[-20:]
        lows = df["low"].iloc[-20:]
        # Flat resistance: highs are roughly equal
        high_std = highs.std() / highs.mean() if highs.mean() > 0 else 1
        # Rising support: lows are increasing
        low_slope = np.polyfit(range(len(lows)), lows.values, 1)[0]

        if high_std < 0.015 and low_slope > 0:
            resistance = highs.mean()
            if df["close"].iloc[-1] > resistance:
                return self._triggered("BUY", 0.76, f"Ascending Triangle breakout above {resistance:.2f}")
        return self._not_triggered()


# ── #90: Descending Triangle ──────────────────────────────────

class DescendingTriangle(BaseStrategy):
    name = "Descending Triangle"
    category = "chart_pattern"
    description = "Flat support + falling resistance = bearish"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING]
    weight = 1.4

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20:
            return self._not_triggered()
        highs = df["high"].iloc[-20:]
        lows = df["low"].iloc[-20:]
        low_std = lows.std() / lows.mean() if lows.mean() > 0 else 1
        high_slope = np.polyfit(range(len(highs)), highs.values, 1)[0]

        if low_std < 0.015 and high_slope < 0:
            support = lows.mean()
            if df["close"].iloc[-1] < support:
                return self._triggered("SELL", 0.76, f"Descending Triangle breakdown below {support:.2f}")
        return self._not_triggered()


# ── #91: Symmetrical Triangle ─────────────────────────────────

class SymmetricalTriangle(BaseStrategy):
    name = "Symmetrical Triangle"
    category = "chart_pattern"
    description = "Converging trendlines — breakout either direction"
    suitable_regimes = [MarketRegime.RANGING]
    weight = 1.2

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20:
            return self._not_triggered()
        highs = df["high"].iloc[-20:]
        lows = df["low"].iloc[-20:]
        x = np.arange(len(highs))
        high_slope = np.polyfit(x, highs.values, 1)[0]
        low_slope = np.polyfit(x, lows.values, 1)[0]

        # Converging: highs falling, lows rising
        if high_slope < 0 and low_slope > 0:
            spread = highs.iloc[-1] - lows.iloc[-1]
            initial_spread = highs.iloc[0] - lows.iloc[0]
            if initial_spread > 0 and spread / initial_spread < 0.4:
                price = df["close"].iloc[-1]
                if price > highs.iloc[-1]:
                    return self._triggered("BUY", 0.7, "Symmetrical triangle bullish breakout")
                if price < lows.iloc[-1]:
                    return self._triggered("SELL", 0.7, "Symmetrical triangle bearish breakdown")
        return self._not_triggered()


# ── #92: Bull Flag ────────────────────────────────────────────

class BullFlag(BaseStrategy):
    name = "Bull Flag"
    category = "chart_pattern"
    description = "Sharp up-move → small pullback → continuation"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.BREAKOUT]
    weight = 1.4

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 15:
            return self._not_triggered()
        # Pole: strong up-move in first 5 bars
        pole_gain = (df["close"].iloc[-15] - df["close"].iloc[-20]) / df["close"].iloc[-20] * 100 if len(df) >= 20 else 0
        # Flag: small pullback in last 5-10 bars
        flag_high = df["high"].iloc[-10:-1].max()
        flag_low = df["low"].iloc[-10:-1].min()
        flag_range = (flag_high - flag_low) / flag_high * 100 if flag_high > 0 else 100

        if pole_gain > 5 and flag_range < 5:
            if df["close"].iloc[-1] > flag_high:
                return self._triggered("BUY", 0.75, f"Bull Flag breakout — pole +{pole_gain:.1f}%, flag range {flag_range:.1f}%")
        return self._not_triggered()


# ── #93: Bear Flag ────────────────────────────────────────────

class BearFlag(BaseStrategy):
    name = "Bear Flag"
    category = "chart_pattern"
    description = "Sharp down-move → small pullback → continuation"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.BREAKOUT]
    weight = 1.4

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 15:
            return self._not_triggered()
        pole_loss = (df["close"].iloc[-20] - df["close"].iloc[-15]) / df["close"].iloc[-20] * 100 if len(df) >= 20 else 0
        flag_high = df["high"].iloc[-10:-1].max()
        flag_low = df["low"].iloc[-10:-1].min()
        flag_range = (flag_high - flag_low) / flag_high * 100 if flag_high > 0 else 100

        if pole_loss > 5 and flag_range < 5:
            if df["close"].iloc[-1] < flag_low:
                return self._triggered("SELL", 0.75, f"Bear Flag breakdown — pole -{pole_loss:.1f}%, flag range {flag_range:.1f}%")
        return self._not_triggered()


# ── #94: Cup and Handle ───────────────────────────────────────

class CupAndHandle(BaseStrategy):
    name = "Cup and Handle"
    category = "chart_pattern"
    description = "Rounded bottom + small pullback → breakout"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.RANGING]
    weight = 1.6

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 40:
            return self._not_triggered()
        close = df["close"].iloc[-40:]
        mid_point = close.iloc[15:25].min()
        left_rim = close.iloc[:5].max()
        right_rim = close.iloc[-10:-5].max()
        current = df["close"].iloc[-1]

        # Cup: U-shape (mid lower than rims)
        if mid_point < left_rim * 0.95 and mid_point < right_rim * 0.95:
            # Rims roughly equal
            if abs(left_rim - right_rim) / left_rim < 0.05:
                # Handle: small pullback from right rim
                handle_low = close.iloc[-5:].min()
                if handle_low > mid_point and current > right_rim:
                    return self._triggered("BUY", 0.82, f"Cup & Handle breakout — cup depth {((left_rim - mid_point)/left_rim*100):.1f}%")
        return self._not_triggered()


# ── #95: Falling Wedge ────────────────────────────────────────

class FallingWedge(BaseStrategy):
    name = "Falling Wedge"
    category = "chart_pattern"
    description = "Converging downward lines — bullish breakout"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING]
    weight = 1.3

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20:
            return self._not_triggered()
        x = np.arange(20)
        highs = df["high"].iloc[-20:].values
        lows = df["low"].iloc[-20:].values
        high_slope = np.polyfit(x, highs, 1)[0]
        low_slope = np.polyfit(x, lows, 1)[0]

        # Both falling but converging (high slope more negative)
        if high_slope < 0 and low_slope < 0 and high_slope < low_slope:
            if df["close"].iloc[-1] > df["high"].iloc[-2]:
                return self._triggered("BUY", 0.73, "Falling Wedge bullish breakout — converging down-lines broken")
        return self._not_triggered()


# ── #96: Rising Wedge ─────────────────────────────────────────

class RisingWedge(BaseStrategy):
    name = "Rising Wedge"
    category = "chart_pattern"
    description = "Converging upward lines — bearish breakdown"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.RANGING]
    weight = 1.3

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20:
            return self._not_triggered()
        x = np.arange(20)
        highs = df["high"].iloc[-20:].values
        lows = df["low"].iloc[-20:].values
        high_slope = np.polyfit(x, highs, 1)[0]
        low_slope = np.polyfit(x, lows, 1)[0]

        # Both rising but converging (low slope more positive)
        if high_slope > 0 and low_slope > 0 and low_slope > high_slope:
            if df["close"].iloc[-1] < df["low"].iloc[-2]:
                return self._triggered("SELL", 0.73, "Rising Wedge bearish breakdown — converging up-lines broken")
        return self._not_triggered()

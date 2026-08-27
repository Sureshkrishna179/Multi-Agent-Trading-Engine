"""
Trend-Following Strategies (#32–#46)
======================================
15 strategies for riding established directional moves.
Uses moving average crossovers, SuperTrend, Ichimoku, Parabolic SAR, etc.
"""

import pandas as pd
import numpy as np
import ta
from src.agents.strategies import BaseStrategy, MarketRegime


# ── #32: SMA Crossover (9/21) ──────────────────────────────────

class SMACrossover_9_21(BaseStrategy):
    name = "SMA Crossover 9/21"
    category = "trend"
    description = "Short-term: SMA 9 crosses above/below SMA 21"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH, MarketRegime.BREAKOUT]
    weight = 1.2

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 22:
            return self._not_triggered()
        df = df.copy()
        df["sma_9"] = df["close"].rolling(9).mean()
        df["sma_21"] = df["close"].rolling(21).mean()
        curr, prev = df.iloc[-1], df.iloc[-2]
        if pd.notna(curr["sma_9"]) and pd.notna(prev["sma_9"]):
            if prev["sma_9"] <= prev["sma_21"] and curr["sma_9"] > curr["sma_21"]:
                return self._triggered("BUY", 0.7, "SMA 9 crossed above SMA 21 — bullish crossover")
            if prev["sma_9"] >= prev["sma_21"] and curr["sma_9"] < curr["sma_21"]:
                return self._triggered("SELL", 0.7, "SMA 9 crossed below SMA 21 — bearish crossover")
        return self._not_triggered()


# ── #33: EMA Crossover (9/21) ──────────────────────────────────

class EMACrossover_9_21(BaseStrategy):
    name = "EMA Crossover 9/21"
    category = "trend"
    description = "Faster than SMA crossover — better for crypto"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH, MarketRegime.BREAKOUT]
    weight = 1.3

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 22:
            return self._not_triggered()
        df = df.copy()
        df["ema_9"] = df["close"].ewm(span=9, adjust=False).mean()
        df["ema_21"] = df["close"].ewm(span=21, adjust=False).mean()
        curr, prev = df.iloc[-1], df.iloc[-2]
        if prev["ema_9"] <= prev["ema_21"] and curr["ema_9"] > curr["ema_21"]:
            return self._triggered("BUY", 0.72, "EMA 9 crossed above EMA 21 — fast bullish crossover")
        if prev["ema_9"] >= prev["ema_21"] and curr["ema_9"] < curr["ema_21"]:
            return self._triggered("SELL", 0.72, "EMA 9 crossed below EMA 21 — fast bearish crossover")
        return self._not_triggered()


# ── #34: Golden Cross (50/200) ─────────────────────────────────

class GoldenCross(BaseStrategy):
    name = "Golden Cross 50/200"
    category = "trend"
    description = "SMA 50 crosses above SMA 200 — major bullish signal"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING]
    weight = 1.8

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 201:
            return self._not_triggered()
        sma_50 = df.get("sma_50")
        sma_200 = df.get("sma_200")
        if sma_50 is None or sma_200 is None:
            return self._not_triggered()
        curr_50, prev_50 = sma_50.iloc[-1], sma_50.iloc[-2]
        curr_200, prev_200 = sma_200.iloc[-1], sma_200.iloc[-2]
        if pd.notna(curr_50) and pd.notna(curr_200) and pd.notna(prev_50) and pd.notna(prev_200):
            if prev_50 <= prev_200 and curr_50 > curr_200:
                return self._triggered("BUY", 0.85, "Golden Cross — SMA 50 crossed above SMA 200")
        return self._not_triggered()


# ── #35: Death Cross (50/200) ──────────────────────────────────

class DeathCross(BaseStrategy):
    name = "Death Cross 50/200"
    category = "trend"
    description = "SMA 50 crosses below SMA 200 — major bearish signal"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.RANGING]
    weight = 1.8

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 201:
            return self._not_triggered()
        sma_50 = df.get("sma_50")
        sma_200 = df.get("sma_200")
        if sma_50 is None or sma_200 is None:
            return self._not_triggered()
        curr_50, prev_50 = sma_50.iloc[-1], sma_50.iloc[-2]
        curr_200, prev_200 = sma_200.iloc[-1], sma_200.iloc[-2]
        if pd.notna(curr_50) and pd.notna(curr_200) and pd.notna(prev_50) and pd.notna(prev_200):
            if prev_50 >= prev_200 and curr_50 < curr_200:
                return self._triggered("SELL", 0.85, "Death Cross — SMA 50 crossed below SMA 200")
        return self._not_triggered()


# ── #36: SuperTrend ────────────────────────────────────────────

class SuperTrend(BaseStrategy):
    name = "SuperTrend"
    category = "trend"
    description = "ATR-based trend indicator — flips green/red"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH, MarketRegime.BREAKOUT]
    weight = 1.5

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 15:
            return self._not_triggered()
        df = df.copy()
        period, multiplier = 10, 3.0
        atr = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"], window=period).average_true_range()
        hl2 = (df["high"] + df["low"]) / 2
        upper = hl2 + multiplier * atr
        lower = hl2 - multiplier * atr

        supertrend = pd.Series(index=df.index, dtype=float)
        direction = pd.Series(index=df.index, dtype=int)
        supertrend.iloc[0] = upper.iloc[0]
        direction.iloc[0] = 1

        for i in range(1, len(df)):
            if df["close"].iloc[i] > upper.iloc[i - 1]:
                direction.iloc[i] = 1
            elif df["close"].iloc[i] < lower.iloc[i - 1]:
                direction.iloc[i] = -1
            else:
                direction.iloc[i] = direction.iloc[i - 1]

        curr_dir = direction.iloc[-1]
        prev_dir = direction.iloc[-2]

        if prev_dir == -1 and curr_dir == 1:
            return self._triggered("BUY", 0.78, "SuperTrend flipped bullish (green)")
        if prev_dir == 1 and curr_dir == -1:
            return self._triggered("SELL", 0.78, "SuperTrend flipped bearish (red)")
        return self._not_triggered()


# ── #37: Parabolic SAR ────────────────────────────────────────

class ParabolicSAR(BaseStrategy):
    name = "Parabolic SAR"
    category = "trend"
    description = "Dots flip from above to below price or vice versa"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH]
    weight = 1.2

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 5:
            return self._not_triggered()
        psar = ta.trend.PSARIndicator(df["high"], df["low"], df["close"])
        psar_up = psar.psar_up()
        psar_down = psar.psar_down()
        curr_up = psar_up.iloc[-1]
        prev_up = psar_up.iloc[-2]
        curr_down = psar_down.iloc[-1]
        prev_down = psar_down.iloc[-2]

        # Flip from bearish (dots above) to bullish (dots below)
        if pd.notna(curr_up) and pd.isna(prev_up):
            return self._triggered("BUY", 0.68, "Parabolic SAR flipped bullish — dots moved below price")
        if pd.notna(curr_down) and pd.isna(prev_down):
            return self._triggered("SELL", 0.68, "Parabolic SAR flipped bearish — dots moved above price")
        return self._not_triggered()


# ── #38: ADX Trend Strength ────────────────────────────────────

class ADXTrendStrength(BaseStrategy):
    name = "ADX Trend Strength"
    category = "trend"
    description = "ADX > 25 = trending, ADX rising = strengthening trend"
    suitable_regimes = []  # Filter strategy — works in all
    weight = 1.0

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20:
            return self._not_triggered()
        adx_ind = ta.trend.ADXIndicator(df["high"], df["low"], df["close"], window=14)
        adx = adx_ind.adx()
        plus_di = adx_ind.adx_pos()
        minus_di = adx_ind.adx_neg()
        curr_adx = adx.iloc[-1]
        if pd.isna(curr_adx):
            return self._not_triggered()
        curr_plus = plus_di.iloc[-1]
        curr_minus = minus_di.iloc[-1]
        if curr_adx > 25:
            if pd.notna(curr_plus) and pd.notna(curr_minus):
                if curr_plus > curr_minus:
                    return self._triggered("BUY", min(0.8, curr_adx / 100), f"ADX={curr_adx:.0f} strong bullish trend (+DI > -DI)")
                else:
                    return self._triggered("SELL", min(0.8, curr_adx / 100), f"ADX={curr_adx:.0f} strong bearish trend (-DI > +DI)")
        return self._not_triggered()


# ── #39: Ichimoku Cloud ───────────────────────────────────────

class IchimokuCloud(BaseStrategy):
    name = "Ichimoku Cloud"
    category = "trend"
    description = "Price vs cloud + Tenkan/Kijun cross"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH]
    weight = 1.5

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 52:
            return self._not_triggered()
        ich = ta.trend.IchimokuIndicator(df["high"], df["low"], window1=9, window2=26, window3=52)
        tenkan = ich.ichimoku_conversion_line()
        kijun = ich.ichimoku_base_line()
        span_a = ich.ichimoku_a()
        span_b = ich.ichimoku_b()

        price = df["close"].iloc[-1]
        t = tenkan.iloc[-1]
        k = kijun.iloc[-1]
        sa = span_a.iloc[-1]
        sb = span_b.iloc[-1]

        if any(pd.isna(x) for x in [t, k, sa, sb]):
            return self._not_triggered()

        cloud_top = max(sa, sb)
        cloud_bottom = min(sa, sb)

        # Bullish: price above cloud + Tenkan above Kijun
        if price > cloud_top and t > k:
            return self._triggered("BUY", 0.8, f"Ichimoku bullish: price above cloud, Tenkan > Kijun")
        # Bearish: price below cloud + Tenkan below Kijun
        if price < cloud_bottom and t < k:
            return self._triggered("SELL", 0.8, f"Ichimoku bearish: price below cloud, Tenkan < Kijun")
        return self._not_triggered()


# ── #40: Donchian Channel Breakout ─────────────────────────────

class DonchianBreakout(BaseStrategy):
    name = "Donchian Channel Breakout"
    category = "trend"
    description = "Price breaks 20-day high or low"
    suitable_regimes = [MarketRegime.BREAKOUT, MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH]
    weight = 1.3

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 21:
            return self._not_triggered()
        high_20 = df["high"].iloc[-21:-1].max()
        low_20 = df["low"].iloc[-21:-1].min()
        price = df["close"].iloc[-1]
        if price > high_20:
            return self._triggered("BUY", 0.75, f"Donchian breakout — price {price:.2f} > 20-day high {high_20:.2f}")
        if price < low_20:
            return self._triggered("SELL", 0.75, f"Donchian breakdown — price {price:.2f} < 20-day low {low_20:.2f}")
        return self._not_triggered()


# ── #41: Keltner Channel Trend ─────────────────────────────────

class KeltnerChannelTrend(BaseStrategy):
    name = "Keltner Channel Trend"
    category = "trend"
    description = "Price closes outside Keltner Channel — strong trend"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH, MarketRegime.BREAKOUT]
    weight = 1.2

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 21:
            return self._not_triggered()
        kc = ta.volatility.KeltnerChannel(df["high"], df["low"], df["close"], window=20, window_atr=10)
        upper = kc.keltner_channel_hband().iloc[-1]
        lower = kc.keltner_channel_lband().iloc[-1]
        price = df["close"].iloc[-1]
        if pd.notna(upper) and price > upper:
            return self._triggered("BUY", 0.7, f"Price above Keltner upper — strong bullish trend")
        if pd.notna(lower) and price < lower:
            return self._triggered("SELL", 0.7, f"Price below Keltner lower — strong bearish trend")
        return self._not_triggered()


# ── #42: Triple EMA (TEMA) ─────────────────────────────────────

class TripleEMA(BaseStrategy):
    name = "Triple EMA Crossover"
    category = "trend"
    description = "Reduced lag MA crossover"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH, MarketRegime.BREAKOUT]
    weight = 1.1

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 30:
            return self._not_triggered()
        close = df["close"]
        ema1 = close.ewm(span=10, adjust=False).mean()
        ema2 = ema1.ewm(span=10, adjust=False).mean()
        ema3 = ema2.ewm(span=10, adjust=False).mean()
        tema = 3 * ema1 - 3 * ema2 + ema3

        sma_20 = close.rolling(20).mean()
        curr_tema, prev_tema = tema.iloc[-1], tema.iloc[-2]
        curr_sma, prev_sma = sma_20.iloc[-1], sma_20.iloc[-2]

        if pd.notna(curr_tema) and pd.notna(curr_sma):
            if prev_tema <= prev_sma and curr_tema > curr_sma:
                return self._triggered("BUY", 0.68, "TEMA crossed above SMA 20 — low-lag bullish signal")
            if prev_tema >= prev_sma and curr_tema < curr_sma:
                return self._triggered("SELL", 0.68, "TEMA crossed below SMA 20 — low-lag bearish signal")
        return self._not_triggered()


# ── #43: Hull Moving Average ───────────────────────────────────

class HullMA(BaseStrategy):
    name = "Hull Moving Average"
    category = "trend"
    description = "Near-zero lag MA — catches trend changes early"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH, MarketRegime.BREAKOUT]
    weight = 1.3

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20:
            return self._not_triggered()
        close = df["close"]
        period = 16
        half = int(period / 2)
        sqrt_period = int(np.sqrt(period))
        wma_half = close.rolling(half).mean()
        wma_full = close.rolling(period).mean()
        diff = 2 * wma_half - wma_full
        hull = diff.rolling(sqrt_period).mean()

        if len(hull.dropna()) < 2:
            return self._not_triggered()

        curr, prev = hull.iloc[-1], hull.iloc[-2]
        if pd.notna(curr) and pd.notna(prev):
            if curr > prev and prev <= hull.iloc[-3] if len(hull.dropna()) > 2 and pd.notna(hull.iloc[-3]) else False:
                return self._triggered("BUY", 0.7, "Hull MA turned upward — early trend change")
            if curr < prev and prev >= hull.iloc[-3] if len(hull.dropna()) > 2 and pd.notna(hull.iloc[-3]) else False:
                return self._triggered("SELL", 0.7, "Hull MA turned downward — early trend change")
        return self._not_triggered()


# ── #44: Linear Regression Channel ─────────────────────────────

class LinearRegressionChannel(BaseStrategy):
    name = "Linear Regression Channel"
    category = "trend"
    description = "Trade in direction of regression slope"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH]
    weight = 1.0

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20:
            return self._not_triggered()
        close = df["close"].iloc[-20:].values
        x = np.arange(len(close))
        slope, intercept = np.polyfit(x, close, 1)
        r_squared = 1 - np.sum((close - (slope * x + intercept)) ** 2) / np.sum((close - np.mean(close)) ** 2)

        if r_squared > 0.7:  # Strong linear trend
            if slope > 0:
                return self._triggered("BUY", min(0.8, r_squared), f"Linear regression bullish (slope={slope:.2f}, R²={r_squared:.2f})")
            else:
                return self._triggered("SELL", min(0.8, r_squared), f"Linear regression bearish (slope={slope:.2f}, R²={r_squared:.2f})")
        return self._not_triggered()


# ── #45: Aroon Indicator ──────────────────────────────────────

class AroonIndicator(BaseStrategy):
    name = "Aroon Indicator"
    category = "trend"
    description = "Aroon Up > 70 + Down < 30 = bullish"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH]
    weight = 1.0

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 26:
            return self._not_triggered()
        aroon = ta.trend.AroonIndicator(df["close"], window=25)
        up = aroon.aroon_up().iloc[-1]
        down = aroon.aroon_down().iloc[-1]
        if pd.isna(up) or pd.isna(down):
            return self._not_triggered()
        if up > 70 and down < 30:
            return self._triggered("BUY", 0.7, f"Aroon bullish: Up={up:.0f}, Down={down:.0f}")
        if down > 70 and up < 30:
            return self._triggered("SELL", 0.7, f"Aroon bearish: Down={down:.0f}, Up={up:.0f}")
        return self._not_triggered()


# ── #46: TRIX Crossover ───────────────────────────────────────

class TRIXCrossover(BaseStrategy):
    name = "TRIX Crossover"
    category = "trend"
    description = "Triple-smoothed EMA rate of change"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH]
    weight = 1.0

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20:
            return self._not_triggered()
        trix = ta.trend.TRIXIndicator(df["close"], window=15)
        trix_val = trix.trix()
        curr = trix_val.iloc[-1]
        prev = trix_val.iloc[-2]
        if pd.notna(curr) and pd.notna(prev):
            if prev <= 0 and curr > 0:
                return self._triggered("BUY", 0.65, "TRIX crossed above zero — bullish momentum")
            if prev >= 0 and curr < 0:
                return self._triggered("SELL", 0.65, "TRIX crossed below zero — bearish momentum")
        return self._not_triggered()

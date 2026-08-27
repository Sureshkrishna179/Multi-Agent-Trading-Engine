"""
Momentum Strategies (#47–#61)
===============================
15 momentum/oscillator-based strategies.
Measures speed and strength of price moves for timing entries.
"""

import pandas as pd
import numpy as np
import ta
from src.agents.strategies import BaseStrategy, MarketRegime


# ── #47: RSI Overbought/Oversold ───────────────────────────────

class RSIOverboughtOversold(BaseStrategy):
    name = "RSI Overbought/Oversold"
    category = "momentum"
    description = "RSI < 30 oversold BUY, RSI > 70 overbought SELL"
    suitable_regimes = [MarketRegime.RANGING, MarketRegime.TRENDING_BEARISH, MarketRegime.TRENDING_BULLISH]
    weight = 1.2

    def evaluate(self, df, sentiment_data=None):
        rsi = df.get("rsi")
        if rsi is None:
            return self._not_triggered()
        val = rsi.iloc[-1]
        if pd.isna(val):
            return self._not_triggered()
        if val < 30:
            return self._triggered("BUY", min(0.8, (30 - val) / 30), f"RSI={val:.1f} oversold — bounce expected")
        if val > 70:
            return self._triggered("SELL", min(0.8, (val - 70) / 30), f"RSI={val:.1f} overbought — pullback expected")
        return self._not_triggered()


# ── #48: RSI Bullish Divergence ────────────────────────────────

class RSIBullishDivergence(BaseStrategy):
    name = "RSI Bullish Divergence"
    category = "momentum"
    description = "Price lower low but RSI higher low — hidden strength"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING]
    weight = 1.5

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 14 or "rsi" not in df.columns:
            return self._not_triggered()
        rsi = df["rsi"]
        close = df["close"]
        # Compare last 2 swing lows (simplified: compare 5-bar windows)
        if len(df) < 20:
            return self._not_triggered()
        recent_low = close.iloc[-10:].min()
        prior_low = close.iloc[-20:-10].min()
        recent_rsi_low = rsi.iloc[-10:].min()
        prior_rsi_low = rsi.iloc[-20:-10].min()

        if pd.notna(recent_rsi_low) and pd.notna(prior_rsi_low):
            if recent_low < prior_low and recent_rsi_low > prior_rsi_low:
                return self._triggered("BUY", 0.75, f"RSI bullish divergence — price lower low but RSI higher low")
        return self._not_triggered()


# ── #49: RSI Bearish Divergence ────────────────────────────────

class RSIBearishDivergence(BaseStrategy):
    name = "RSI Bearish Divergence"
    category = "momentum"
    description = "Price higher high but RSI lower high — hidden weakness"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.RANGING]
    weight = 1.5

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20 or "rsi" not in df.columns:
            return self._not_triggered()
        rsi = df["rsi"]
        close = df["close"]
        recent_high = close.iloc[-10:].max()
        prior_high = close.iloc[-20:-10].max()
        recent_rsi_high = rsi.iloc[-10:].max()
        prior_rsi_high = rsi.iloc[-20:-10].max()

        if pd.notna(recent_rsi_high) and pd.notna(prior_rsi_high):
            if recent_high > prior_high and recent_rsi_high < prior_rsi_high:
                return self._triggered("SELL", 0.75, f"RSI bearish divergence — price higher high but RSI lower high")
        return self._not_triggered()


# ── #50: MACD Crossover ───────────────────────────────────────

class MACDCrossover(BaseStrategy):
    name = "MACD Crossover"
    category = "momentum"
    description = "MACD line crosses above/below signal line"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH, MarketRegime.BREAKOUT]
    weight = 1.3

    def evaluate(self, df, sentiment_data=None):
        macd = df.get("macd")
        signal = df.get("macd_signal")
        if macd is None or signal is None:
            return self._not_triggered()
        curr_m, prev_m = macd.iloc[-1], macd.iloc[-2]
        curr_s, prev_s = signal.iloc[-1], signal.iloc[-2]
        if pd.notna(curr_m) and pd.notna(curr_s) and pd.notna(prev_m) and pd.notna(prev_s):
            if prev_m <= prev_s and curr_m > curr_s:
                return self._triggered("BUY", 0.72, "MACD crossed above signal — bullish momentum shift")
            if prev_m >= prev_s and curr_m < curr_s:
                return self._triggered("SELL", 0.72, "MACD crossed below signal — bearish momentum shift")
        return self._not_triggered()


# ── #51: MACD Bullish Divergence ───────────────────────────────

class MACDBullishDivergence(BaseStrategy):
    name = "MACD Bullish Divergence"
    category = "momentum"
    description = "Price lower low + MACD higher low"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING]
    weight = 1.5

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20 or "macd" not in df.columns:
            return self._not_triggered()
        macd = df["macd"]
        close = df["close"]
        recent_low = close.iloc[-10:].min()
        prior_low = close.iloc[-20:-10].min()
        recent_macd = macd.iloc[-10:].min()
        prior_macd = macd.iloc[-20:-10].min()
        if pd.notna(recent_macd) and pd.notna(prior_macd):
            if recent_low < prior_low and recent_macd > prior_macd:
                return self._triggered("BUY", 0.78, "MACD bullish divergence — early reversal signal")
        return self._not_triggered()


# ── #52: MACD Bearish Divergence ───────────────────────────────

class MACDBearishDivergence(BaseStrategy):
    name = "MACD Bearish Divergence"
    category = "momentum"
    description = "Price higher high + MACD lower high"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.RANGING]
    weight = 1.5

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20 or "macd" not in df.columns:
            return self._not_triggered()
        macd = df["macd"]
        close = df["close"]
        recent_high = close.iloc[-10:].max()
        prior_high = close.iloc[-20:-10].max()
        recent_macd = macd.iloc[-10:].max()
        prior_macd = macd.iloc[-20:-10].max()
        if pd.notna(recent_macd) and pd.notna(prior_macd):
            if recent_high > prior_high and recent_macd < prior_macd:
                return self._triggered("SELL", 0.78, "MACD bearish divergence — early reversal signal")
        return self._not_triggered()


# ── #53: MACD Histogram Reversal ───────────────────────────────

class MACDHistogramReversal(BaseStrategy):
    name = "MACD Histogram Reversal"
    category = "momentum"
    description = "Histogram shrinks and flips — momentum shift"
    suitable_regimes = []
    weight = 1.0

    def evaluate(self, df, sentiment_data=None):
        hist = df.get("macd_histogram")
        if hist is None or len(df) < 3:
            return self._not_triggered()
        h1, h2, h3 = hist.iloc[-3], hist.iloc[-2], hist.iloc[-1]
        if pd.notna(h1) and pd.notna(h2) and pd.notna(h3):
            # Bearish to bullish flip
            if h1 < 0 and h2 < 0 and h3 > 0:
                return self._triggered("BUY", 0.6, "MACD histogram flipped positive — momentum shift")
            if h1 > 0 and h2 > 0 and h3 < 0:
                return self._triggered("SELL", 0.6, "MACD histogram flipped negative — momentum shift")
        return self._not_triggered()


# ── #54: Stochastic Oscillator ─────────────────────────────────

class StochasticOscillator(BaseStrategy):
    name = "Stochastic Oscillator"
    category = "momentum"
    description = "%K crosses %D in overbought/oversold zones"
    suitable_regimes = [MarketRegime.RANGING, MarketRegime.TRENDING_BEARISH, MarketRegime.TRENDING_BULLISH]
    weight = 1.1

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 14:
            return self._not_triggered()
        stoch = ta.momentum.StochasticOscillator(df["high"], df["low"], df["close"], window=14, smooth_window=3)
        k = stoch.stoch()
        d = stoch.stoch_signal()
        curr_k, curr_d = k.iloc[-1], d.iloc[-1]
        prev_k, prev_d = k.iloc[-2], d.iloc[-2]
        if pd.notna(curr_k) and pd.notna(curr_d):
            if curr_k < 20 and prev_k <= prev_d and curr_k > curr_d:
                return self._triggered("BUY", 0.68, f"Stochastic bullish cross in oversold zone (%K={curr_k:.0f})")
            if curr_k > 80 and prev_k >= prev_d and curr_k < curr_d:
                return self._triggered("SELL", 0.68, f"Stochastic bearish cross in overbought zone (%K={curr_k:.0f})")
        return self._not_triggered()


# ── #55: Stochastic RSI ───────────────────────────────────────

class StochasticRSI(BaseStrategy):
    name = "Stochastic RSI"
    category = "momentum"
    description = "More sensitive than Stochastic — better for crypto"
    suitable_regimes = [MarketRegime.RANGING, MarketRegime.VOLATILE]
    weight = 1.2

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20:
            return self._not_triggered()
        stoch_rsi = ta.momentum.StochRSIIndicator(df["close"], window=14, smooth1=3, smooth2=3)
        k = stoch_rsi.stochrsi_k()
        d = stoch_rsi.stochrsi_d()
        curr_k, curr_d = k.iloc[-1], d.iloc[-1]
        if pd.notna(curr_k) and pd.notna(curr_d):
            if curr_k < 0.2 and curr_k > curr_d:
                return self._triggered("BUY", 0.65, f"StochRSI oversold cross (K={curr_k:.2f})")
            if curr_k > 0.8 and curr_k < curr_d:
                return self._triggered("SELL", 0.65, f"StochRSI overbought cross (K={curr_k:.2f})")
        return self._not_triggered()


# ── #56: Williams %R ──────────────────────────────────────────

class WilliamsR(BaseStrategy):
    name = "Williams %R"
    category = "momentum"
    description = "%R < -80 oversold BUY, %R > -20 overbought SELL"
    suitable_regimes = [MarketRegime.RANGING]
    weight = 1.0

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 14:
            return self._not_triggered()
        wr = ta.momentum.WilliamsRIndicator(df["high"], df["low"], df["close"], lbp=14)
        val = wr.williams_r().iloc[-1]
        if pd.isna(val):
            return self._not_triggered()
        if val < -80:
            return self._triggered("BUY", 0.6, f"Williams %R={val:.0f} — oversold zone")
        if val > -20:
            return self._triggered("SELL", 0.6, f"Williams %R={val:.0f} — overbought zone")
        return self._not_triggered()


# ── #57: CCI (Commodity Channel Index) ─────────────────────────

class CCIStrategy(BaseStrategy):
    name = "CCI Strategy"
    category = "momentum"
    description = "CCI > +100 bullish, CCI < -100 bearish"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH]
    weight = 1.0

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20:
            return self._not_triggered()
        cci = ta.trend.CCIIndicator(df["high"], df["low"], df["close"], window=20)
        val = cci.cci().iloc[-1]
        if pd.isna(val):
            return self._not_triggered()
        if val > 100:
            return self._triggered("BUY", min(0.75, val / 200), f"CCI={val:.0f} — strong bullish momentum")
        if val < -100:
            return self._triggered("SELL", min(0.75, abs(val) / 200), f"CCI={val:.0f} — strong bearish momentum")
        return self._not_triggered()


# ── #58: Rate of Change (ROC) ─────────────────────────────────

class RateOfChange(BaseStrategy):
    name = "Rate of Change"
    category = "momentum"
    description = "% price change over N periods"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH, MarketRegime.BREAKOUT]
    weight = 0.9

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 12:
            return self._not_triggered()
        roc = ta.momentum.ROCIndicator(df["close"], window=12)
        val = roc.roc().iloc[-1]
        if pd.isna(val):
            return self._not_triggered()
        if val > 5:
            return self._triggered("BUY", min(0.7, val / 15), f"ROC={val:.1f}% — strong upward momentum")
        if val < -5:
            return self._triggered("SELL", min(0.7, abs(val) / 15), f"ROC={val:.1f}% — strong downward momentum")
        return self._not_triggered()


# ── #59: Money Flow Index (MFI) ────────────────────────────────

class MoneyFlowIndex(BaseStrategy):
    name = "Money Flow Index"
    category = "momentum"
    description = "Volume-weighted RSI: MFI < 20 oversold, > 80 overbought"
    suitable_regimes = [MarketRegime.RANGING, MarketRegime.TRENDING_BEARISH, MarketRegime.TRENDING_BULLISH]
    weight = 1.3

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 14 or "volume" not in df.columns:
            return self._not_triggered()
        mfi = ta.volume.MFIIndicator(df["high"], df["low"], df["close"], df["volume"], window=14)
        val = mfi.money_flow_index().iloc[-1]
        if pd.isna(val):
            return self._not_triggered()
        if val < 20:
            return self._triggered("BUY", 0.7, f"MFI={val:.0f} — oversold with volume confirmation")
        if val > 80:
            return self._triggered("SELL", 0.7, f"MFI={val:.0f} — overbought with volume confirmation")
        return self._not_triggered()


# ── #60: Awesome Oscillator ───────────────────────────────────

class AwesomeOscillator(BaseStrategy):
    name = "Awesome Oscillator"
    category = "momentum"
    description = "Saucer or zero-cross momentum signal"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH]
    weight = 0.9

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 34:
            return self._not_triggered()
        ao = ta.momentum.AwesomeOscillatorIndicator(df["high"], df["low"], window1=5, window2=34)
        ao_val = ao.awesome_oscillators()
        curr, prev = ao_val.iloc[-1], ao_val.iloc[-2]
        if pd.notna(curr) and pd.notna(prev):
            if prev <= 0 and curr > 0:
                return self._triggered("BUY", 0.62, "Awesome Oscillator crossed above zero — bullish")
            if prev >= 0 and curr < 0:
                return self._triggered("SELL", 0.62, "Awesome Oscillator crossed below zero — bearish")
        return self._not_triggered()


# ── #61: TSI (True Strength Index) ─────────────────────────────

class TrueStrengthIndex(BaseStrategy):
    name = "True Strength Index"
    category = "momentum"
    description = "Double-smoothed momentum crossing signal line"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH]
    weight = 1.0

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 30:
            return self._not_triggered()
        tsi = ta.momentum.TSIIndicator(df["close"], window_slow=25, window_fast=13)
        tsi_val = tsi.tsi()
        curr, prev = tsi_val.iloc[-1], tsi_val.iloc[-2]
        if pd.notna(curr) and pd.notna(prev):
            if prev <= 0 and curr > 0:
                return self._triggered("BUY", 0.65, "TSI crossed above zero — bullish strength")
            if prev >= 0 and curr < 0:
                return self._triggered("SELL", 0.65, "TSI crossed below zero — bearish strength")
        return self._not_triggered()

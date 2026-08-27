"""
Volume-Based Strategies (#72–#81)
===================================
10 strategies that confirm moves with institutional money flow.
"""

import pandas as pd
import numpy as np
import ta
from src.agents.strategies import BaseStrategy, MarketRegime


# ── #72: Volume Spike Breakout ─────────────────────────────────

class VolumeSpikeBreakout(BaseStrategy):
    name = "Volume Spike Breakout"
    category = "volume"
    description = "Volume > 3x average + price breakout = institutional conviction"
    suitable_regimes = [MarketRegime.BREAKOUT, MarketRegime.VOLATILE]
    weight = 2.0

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 21 or "volume" not in df.columns:
            return self._not_triggered()
        curr = df.iloc[-1]
        avg_vol = df["volume"].iloc[-21:-1].mean()
        if pd.isna(avg_vol) or avg_vol <= 0:
            return self._not_triggered()
        vol_ratio = curr["volume"] / avg_vol
        if vol_ratio > 3:
            price_change = (curr["close"] - curr["open"]) / curr["open"] * 100
            if price_change > 1:
                return self._triggered("BUY", min(0.85, vol_ratio * 0.15), f"Volume spike {vol_ratio:.1f}x avg + {price_change:.1f}% up — institutional buying")
            elif price_change < -1:
                return self._triggered("SELL", min(0.85, vol_ratio * 0.15), f"Volume spike {vol_ratio:.1f}x avg + {price_change:.1f}% down — institutional selling")
        return self._not_triggered()


# ── #73: OBV Trend ────────────────────────────────────────────

class OBVTrend(BaseStrategy):
    name = "OBV Trend"
    category = "volume"
    description = "On-Balance Volume trending up while price flat = accumulation"
    suitable_regimes = [MarketRegime.RANGING, MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH]
    weight = 1.3

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20 or "volume" not in df.columns:
            return self._not_triggered()
        obv = ta.volume.OnBalanceVolumeIndicator(df["close"], df["volume"]).on_balance_volume()
        obv_sma = obv.rolling(20).mean()
        curr_obv, curr_sma = obv.iloc[-1], obv_sma.iloc[-1]
        prev_obv, prev_sma = obv.iloc[-5], obv_sma.iloc[-5]

        if pd.notna(curr_obv) and pd.notna(curr_sma):
            if curr_obv > curr_sma and curr_obv > prev_obv:
                return self._triggered("BUY", 0.65, "OBV trending above SMA — accumulation phase")
            if curr_obv < curr_sma and curr_obv < prev_obv:
                return self._triggered("SELL", 0.65, "OBV trending below SMA — distribution phase")
        return self._not_triggered()


# ── #74: OBV Divergence ───────────────────────────────────────

class OBVDivergence(BaseStrategy):
    name = "OBV Divergence"
    category = "volume"
    description = "Price falls but OBV rises = smart money buying"
    suitable_regimes = [MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING]
    weight = 1.6

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20 or "volume" not in df.columns:
            return self._not_triggered()
        obv = ta.volume.OnBalanceVolumeIndicator(df["close"], df["volume"]).on_balance_volume()
        close = df["close"]

        recent_price = close.iloc[-10:].mean()
        prior_price = close.iloc[-20:-10].mean()
        recent_obv = obv.iloc[-10:].mean()
        prior_obv = obv.iloc[-20:-10].mean()

        if pd.notna(recent_obv) and pd.notna(prior_obv):
            # Bullish divergence: price down, OBV up
            if recent_price < prior_price and recent_obv > prior_obv:
                return self._triggered("BUY", 0.72, "OBV bullish divergence — smart money accumulating while price drops")
            # Bearish divergence: price up, OBV down
            if recent_price > prior_price and recent_obv < prior_obv:
                return self._triggered("SELL", 0.72, "OBV bearish divergence — distribution while price rises")
        return self._not_triggered()


# ── #75: VWAP Cross ───────────────────────────────────────────

class VWAPCross(BaseStrategy):
    name = "VWAP Cross"
    category = "volume"
    description = "Price crosses above VWAP = bullish, below = bearish"
    suitable_regimes = []  # All
    weight = 1.4

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 5 or "volume" not in df.columns:
            return self._not_triggered()
        # Calculate VWAP
        typical = (df["high"] + df["low"] + df["close"]) / 3
        vwap = (typical * df["volume"]).cumsum() / df["volume"].cumsum()
        curr_vwap = vwap.iloc[-1]
        prev_vwap = vwap.iloc[-2]
        price = df["close"].iloc[-1]
        prev_price = df["close"].iloc[-2]

        if pd.notna(curr_vwap) and pd.notna(prev_vwap):
            if prev_price <= prev_vwap and price > curr_vwap:
                return self._triggered("BUY", 0.68, "Price crossed above VWAP — bullish intraday")
            if prev_price >= prev_vwap and price < curr_vwap:
                return self._triggered("SELL", 0.68, "Price crossed below VWAP — bearish intraday")
        return self._not_triggered()


# ── #76: VWAP Reversion ──────────────────────────────────────

class VWAPReversion(BaseStrategy):
    name = "VWAP Reversion"
    category = "volume"
    description = "Price > 2 ATR from VWAP = snap-back expected"
    suitable_regimes = [MarketRegime.RANGING, MarketRegime.VOLATILE]
    weight = 1.3

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 14 or "volume" not in df.columns or "atr" not in df.columns:
            return self._not_triggered()
        typical = (df["high"] + df["low"] + df["close"]) / 3
        vwap = (typical * df["volume"]).cumsum() / df["volume"].cumsum()
        curr_vwap = vwap.iloc[-1]
        price = df["close"].iloc[-1]
        atr = df["atr"].iloc[-1]

        if pd.notna(curr_vwap) and pd.notna(atr) and atr > 0:
            deviation = (price - curr_vwap) / atr
            if deviation > 2:
                return self._triggered("SELL", min(0.7, deviation * 0.25), f"Price {deviation:.1f}x ATR above VWAP — reversion expected")
            if deviation < -2:
                return self._triggered("BUY", min(0.7, abs(deviation) * 0.25), f"Price {abs(deviation):.1f}x ATR below VWAP — reversion expected")
        return self._not_triggered()


# ── #77: Accumulation/Distribution Line ────────────────────────

class AccDistLine(BaseStrategy):
    name = "Accumulation/Distribution"
    category = "volume"
    description = "A/D line rising = buying pressure"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH, MarketRegime.RANGING]
    weight = 1.1

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20 or "volume" not in df.columns:
            return self._not_triggered()
        ad = ta.volume.AccDistIndexIndicator(df["high"], df["low"], df["close"], df["volume"]).acc_dist_index()
        ad_sma = ad.rolling(20).mean()
        curr_ad, curr_sma = ad.iloc[-1], ad_sma.iloc[-1]

        if pd.notna(curr_ad) and pd.notna(curr_sma):
            if curr_ad > curr_sma:
                return self._triggered("BUY", 0.6, "A/D line above SMA — sustained buying pressure")
            if curr_ad < curr_sma:
                return self._triggered("SELL", 0.6, "A/D line below SMA — sustained selling pressure")
        return self._not_triggered()


# ── #78: Chaikin Money Flow ───────────────────────────────────

class ChaikinMoneyFlow(BaseStrategy):
    name = "Chaikin Money Flow"
    category = "volume"
    description = "CMF > 0 sustained = buying, CMF < 0 = selling"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH]
    weight = 1.2

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 21 or "volume" not in df.columns:
            return self._not_triggered()
        cmf = ta.volume.ChaikinMoneyFlowIndicator(df["high"], df["low"], df["close"], df["volume"], window=20)
        val = cmf.chaikin_money_flow().iloc[-1]
        if pd.notna(val):
            if val > 0.1:
                return self._triggered("BUY", min(0.7, val * 3), f"CMF={val:.2f} — sustained buying pressure")
            if val < -0.1:
                return self._triggered("SELL", min(0.7, abs(val) * 3), f"CMF={val:.2f} — sustained selling pressure")
        return self._not_triggered()


# ── #79: Force Index ──────────────────────────────────────────

class ForceIndex(BaseStrategy):
    name = "Force Index"
    category = "volume"
    description = "Price change × Volume — force behind moves"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH, MarketRegime.BREAKOUT]
    weight = 1.0

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 14 or "volume" not in df.columns:
            return self._not_triggered()
        fi = ta.volume.ForceIndexIndicator(df["close"], df["volume"], window=13)
        val = fi.force_index()
        curr, prev = val.iloc[-1], val.iloc[-2]
        if pd.notna(curr) and pd.notna(prev):
            if prev <= 0 and curr > 0:
                return self._triggered("BUY", 0.6, "Force Index crossed positive — buying force")
            if prev >= 0 and curr < 0:
                return self._triggered("SELL", 0.6, "Force Index crossed negative — selling force")
        return self._not_triggered()


# ── #80: Klinger Oscillator ───────────────────────────────────

class KlingerOscillator(BaseStrategy):
    name = "Klinger Oscillator"
    category = "volume"
    description = "Volume-based oscillator crossing signal"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH]
    weight = 1.0

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 55 or "volume" not in df.columns:
            return self._not_triggered()
        # Simplified Klinger: EMA of volume flow
        dm = ((df["high"] - df["low"]) + (df["close"] - df["open"])) * df["volume"]
        klinger = dm.ewm(span=34, adjust=False).mean() - dm.ewm(span=55, adjust=False).mean()
        signal = klinger.ewm(span=13, adjust=False).mean()
        curr_k, prev_k = klinger.iloc[-1], klinger.iloc[-2]
        curr_s, prev_s = signal.iloc[-1], signal.iloc[-2]

        if pd.notna(curr_k) and pd.notna(curr_s):
            if prev_k <= prev_s and curr_k > curr_s:
                return self._triggered("BUY", 0.62, "Klinger crossed above signal — volume-driven bullish")
            if prev_k >= prev_s and curr_k < curr_s:
                return self._triggered("SELL", 0.62, "Klinger crossed below signal — volume-driven bearish")
        return self._not_triggered()


# ── #81: Volume-Price Trend ───────────────────────────────────

class VolumePriceTrend(BaseStrategy):
    name = "Volume-Price Trend"
    category = "volume"
    description = "Cumulative volume adjusted by price change"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH]
    weight = 0.9

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20 or "volume" not in df.columns:
            return self._not_triggered()
        pct_change = df["close"].pct_change()
        vpt = (pct_change * df["volume"]).cumsum()
        vpt_sma = vpt.rolling(20).mean()
        curr_vpt = vpt.iloc[-1]
        curr_sma = vpt_sma.iloc[-1]

        if pd.notna(curr_vpt) and pd.notna(curr_sma):
            if curr_vpt > curr_sma:
                return self._triggered("BUY", 0.58, "VPT above SMA — volume confirms uptrend")
            if curr_vpt < curr_sma:
                return self._triggered("SELL", 0.58, "VPT below SMA — volume confirms downtrend")
        return self._not_triggered()

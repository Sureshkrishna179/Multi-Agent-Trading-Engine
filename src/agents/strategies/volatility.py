"""
Volatility Strategies (#62–#71)
=================================
10 strategies for profiting from volatility expansion/contraction cycles.
"""

import pandas as pd
import numpy as np
import ta
from src.agents.strategies import BaseStrategy, MarketRegime


# ── #62: Bollinger Band Squeeze ────────────────────────────────

class BollingerSqueeze(BaseStrategy):
    name = "Bollinger Band Squeeze"
    category = "volatility"
    description = "BB width narrows to minimum — explosive move imminent"
    suitable_regimes = [MarketRegime.RANGING]
    weight = 1.3

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 25 or "bb_upper" not in df.columns:
            return self._not_triggered()
        bb_w = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]
        bb_w = bb_w.dropna()
        if len(bb_w) < 20:
            return self._not_triggered()
        curr_width = bb_w.iloc[-1]
        min_width = bb_w.iloc[-20:].min()
        if curr_width <= min_width * 1.05:
            return self._triggered("HOLD", 0.6, f"BB Squeeze — width at 20-bar minimum ({curr_width:.4f}). Breakout imminent.")
        return self._not_triggered()


# ── #63: Bollinger Band Bounce ─────────────────────────────────

class BollingerBounce(BaseStrategy):
    name = "Bollinger Band Bounce"
    category = "volatility"
    description = "Price touches lower BB = BUY, upper BB = SELL (ranging)"
    suitable_regimes = [MarketRegime.RANGING]
    weight = 1.2

    def evaluate(self, df, sentiment_data=None):
        if "bb_upper" not in df.columns or "bb_lower" not in df.columns:
            return self._not_triggered()
        curr = df.iloc[-1]
        price = curr["close"]
        if pd.notna(curr["bb_lower"]) and price <= curr["bb_lower"]:
            return self._triggered("BUY", 0.65, f"Price touched lower Bollinger Band — mean reversion buy")
        if pd.notna(curr["bb_upper"]) and price >= curr["bb_upper"]:
            return self._triggered("SELL", 0.65, f"Price touched upper Bollinger Band — mean reversion sell")
        return self._not_triggered()


# ── #64: Bollinger Band Breakout ───────────────────────────────

class BollingerBreakout(BaseStrategy):
    name = "Bollinger Band Breakout"
    category = "volatility"
    description = "Price closes outside BB with volume = trend breakout"
    suitable_regimes = [MarketRegime.BREAKOUT, MarketRegime.VOLATILE]
    weight = 1.4

    def evaluate(self, df, sentiment_data=None):
        if "bb_upper" not in df.columns or "volume" not in df.columns:
            return self._not_triggered()
        curr = df.iloc[-1]
        price = curr["close"]
        avg_vol = df["volume"].iloc[-20:].mean()
        vol = curr["volume"]
        high_vol = vol > avg_vol * 1.5 if pd.notna(avg_vol) and avg_vol > 0 else False

        if pd.notna(curr["bb_upper"]) and price > curr["bb_upper"] and high_vol:
            return self._triggered("BUY", 0.75, "Price broke above upper BB with high volume — bullish breakout")
        if pd.notna(curr["bb_lower"]) and price < curr["bb_lower"] and high_vol:
            return self._triggered("SELL", 0.75, "Price broke below lower BB with high volume — bearish breakout")
        return self._not_triggered()


# ── #65: ATR Breakout ──────────────────────────────────────────

class ATRBreakout(BaseStrategy):
    name = "ATR Breakout"
    category = "volatility"
    description = "Price moves > 2x ATR from open = significant move"
    suitable_regimes = [MarketRegime.BREAKOUT, MarketRegime.VOLATILE]
    weight = 1.3

    def evaluate(self, df, sentiment_data=None):
        if "atr" not in df.columns:
            return self._not_triggered()
        curr = df.iloc[-1]
        atr = curr.get("atr")
        if pd.isna(atr) or atr <= 0:
            return self._not_triggered()
        move = curr["close"] - curr["open"]
        if abs(move) > 2 * atr:
            if move > 0:
                return self._triggered("BUY", 0.72, f"Price moved +{move:.2f} > 2x ATR ({atr:.2f}) — bullish breakout")
            else:
                return self._triggered("SELL", 0.72, f"Price moved {move:.2f} > 2x ATR ({atr:.2f}) — bearish breakout")
        return self._not_triggered()


# ── #66: ATR Trailing Stop ─────────────────────────────────────

class ATRTrailingStop(BaseStrategy):
    name = "ATR Trailing Stop"
    category = "volatility"
    description = "Dynamic trailing stop at 2x ATR for exits"
    suitable_regimes = [MarketRegime.TRENDING_BULLISH, MarketRegime.TRENDING_BEARISH]
    weight = 0.8

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 15 or "atr" not in df.columns:
            return self._not_triggered()
        curr = df.iloc[-1]
        atr = curr.get("atr")
        if pd.isna(atr):
            return self._not_triggered()
        # Check if price dropped from recent high by > 2x ATR
        recent_high = df["high"].iloc[-10:].max()
        recent_low = df["low"].iloc[-10:].min()
        price = curr["close"]
        if recent_high - price > 2 * atr:
            return self._triggered("SELL", 0.6, f"Price dropped {recent_high - price:.2f} from high > 2x ATR — trailing stop exit")
        if price - recent_low > 2 * atr:
            return self._triggered("BUY", 0.6, f"Price rallied {price - recent_low:.2f} from low > 2x ATR — trailing stop entry")
        return self._not_triggered()


# ── #67: Keltner Squeeze ──────────────────────────────────────

class KeltnerSqueeze(BaseStrategy):
    name = "Keltner Squeeze"
    category = "volatility"
    description = "BB inside Keltner Channel — coiled spring"
    suitable_regimes = [MarketRegime.RANGING]
    weight = 1.5

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 21 or "bb_upper" not in df.columns:
            return self._not_triggered()
        kc = ta.volatility.KeltnerChannel(df["high"], df["low"], df["close"], window=20, window_atr=10)
        kc_upper = kc.keltner_channel_hband().iloc[-1]
        kc_lower = kc.keltner_channel_lband().iloc[-1]
        bb_upper = df["bb_upper"].iloc[-1]
        bb_lower = df["bb_lower"].iloc[-1]

        if pd.notna(kc_upper) and pd.notna(bb_upper):
            if bb_upper < kc_upper and bb_lower > kc_lower:
                return self._triggered("HOLD", 0.7, "Keltner Squeeze — BB inside KC. Explosive breakout imminent.")
        return self._not_triggered()


# ── #68: Volatility Expansion ─────────────────────────────────

class VolatilityExpansion(BaseStrategy):
    name = "Volatility Expansion"
    category = "volatility"
    description = "ATR spikes 50%+ above average = new trend starting"
    suitable_regimes = [MarketRegime.BREAKOUT, MarketRegime.VOLATILE]
    weight = 1.2

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20 or "atr" not in df.columns:
            return self._not_triggered()
        atr = df["atr"]
        curr_atr = atr.iloc[-1]
        avg_atr = atr.iloc[-20:].mean()
        if pd.notna(curr_atr) and pd.notna(avg_atr) and avg_atr > 0:
            ratio = curr_atr / avg_atr
            if ratio > 1.5:
                price_dir = df["close"].iloc[-1] - df["close"].iloc[-2]
                signal = "BUY" if price_dir > 0 else "SELL"
                return self._triggered(signal, min(0.75, ratio * 0.3), f"ATR spike {ratio:.1f}x average — volatility expansion")
        return self._not_triggered()


# ── #69: Chaikin Volatility ───────────────────────────────────

class ChaikinVolatility(BaseStrategy):
    name = "Chaikin Volatility"
    category = "volatility"
    description = "Rate of change of ATR — acceleration"
    suitable_regimes = [MarketRegime.BREAKOUT, MarketRegime.VOLATILE]
    weight = 0.9

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20:
            return self._not_triggered()
        hl_diff = df["high"] - df["low"]
        ema_hl = hl_diff.ewm(span=10, adjust=False).mean()
        chaikin_vol = ((ema_hl - ema_hl.shift(10)) / ema_hl.shift(10) * 100)
        curr = chaikin_vol.iloc[-1]
        if pd.notna(curr):
            if curr > 25:
                return self._triggered("HOLD", 0.5, f"Chaikin Volatility={curr:.0f}% — high acceleration, caution")
        return self._not_triggered()


# ── #70: Historical Volatility Breakout ────────────────────────

class HistoricalVolBreakout(BaseStrategy):
    name = "Historical Vol Breakout"
    category = "volatility"
    description = "10-day HV drops then expands = breakout"
    suitable_regimes = [MarketRegime.RANGING, MarketRegime.BREAKOUT]
    weight = 1.1

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 25:
            return self._not_triggered()
        log_ret = np.log(df["close"] / df["close"].shift(1))
        hv_10 = log_ret.rolling(10).std() * np.sqrt(252) * 100
        hv_20 = log_ret.rolling(20).std() * np.sqrt(252) * 100
        curr_10, curr_20 = hv_10.iloc[-1], hv_20.iloc[-1]
        prev_10, prev_20 = hv_10.iloc[-2], hv_20.iloc[-2]

        if pd.notna(curr_10) and pd.notna(curr_20) and pd.notna(prev_10) and pd.notna(prev_20):
            # Was compressed (10d < 20d) and now expanding (10d > 20d)
            if prev_10 < prev_20 and curr_10 > curr_20:
                price_dir = df["close"].iloc[-1] - df["close"].iloc[-3]
                signal = "BUY" if price_dir > 0 else "SELL"
                return self._triggered(signal, 0.65, f"HV breakout — 10d vol expanded above 20d vol")
        return self._not_triggered()


# ── #71: Standard Deviation Channel ────────────────────────────

class StdDevChannel(BaseStrategy):
    name = "Std Dev Channel"
    category = "volatility"
    description = "Price > 2 std devs from mean — extreme"
    suitable_regimes = [MarketRegime.RANGING, MarketRegime.VOLATILE]
    weight = 1.0

    def evaluate(self, df, sentiment_data=None):
        if len(df) < 20:
            return self._not_triggered()
        close = df["close"].iloc[-20:]
        mean = close.mean()
        std = close.std()
        price = df["close"].iloc[-1]
        if std > 0:
            z_score = (price - mean) / std
            if z_score > 2:
                return self._triggered("SELL", min(0.75, z_score * 0.3), f"Price {z_score:.1f} std devs above mean — overextended")
            if z_score < -2:
                return self._triggered("BUY", min(0.75, abs(z_score) * 0.3), f"Price {z_score:.1f} std devs below mean — overextended")
        return self._not_triggered()

"""
Institutional Smart Money Concepts (ICT)
========================================
Advanced institutional strategies including Fair Value Gaps (FVG), 
Order Blocks (OB), and Liquidity Sweeps.

All column references use lowercase (open, high, low, close, volume)
to match the output of the market connectors.
"""

from typing import Dict, Any, Tuple
import pandas as pd
from src.agents.strategies import StrategyRegistry, BaseStrategy

class FairValueGapStrategy(BaseStrategy):
    """
    Detects Fair Value Gaps (FVG) or Imbalances.
    A Bullish FVG occurs when the low of candle 3 is higher than the high of candle 1.
    A Bearish FVG occurs when the high of candle 3 is lower than the low of candle 1.
    """
    def generate_signals(self, df: pd.DataFrame, current_price: float) -> Tuple[int, Dict[str, Any]]:
        if len(df) < 4:
            return 0, {}
            
        # We need the last 3 completed candles
        c1 = df.iloc[-4]
        c2 = df.iloc[-3]
        c3 = df.iloc[-2]
        
        # Bullish FVG
        if c3['low'] > c1['high']:
            fvg_size = c3['low'] - c1['high']
            if current_price <= c3['low'] and current_price >= c1['high']:
                return 1, {"fvg_type": "bullish_mitigation", "fvg_size": fvg_size}
                
        # Bearish FVG
        elif c3['high'] < c1['low']:
            fvg_size = c1['low'] - c3['high']
            if current_price >= c3['high'] and current_price <= c1['low']:
                return -1, {"fvg_type": "bearish_mitigation", "fvg_size": fvg_size}
                
        return 0, {}

class OrderBlockStrategy(BaseStrategy):
    """
    Detects Order Blocks (OB).
    Bullish OB: The last bearish candle before a strong bullish impulse that breaks structure.
    Bearish OB: The last bullish candle before a strong bearish impulse.
    """
    def generate_signals(self, df: pd.DataFrame, current_price: float) -> Tuple[int, Dict[str, Any]]:
        if len(df) < 10:
            return 0, {}
            
        # Lookback window for an order block
        window = df.iloc[-10:-2]
        
        # Find the lowest low in the window (potential Bullish OB location)
        lowest_idx = window['low'].idxmin()
        lowest_candle = df.loc[lowest_idx]
        
        # Check if it was a bearish candle followed by a strong impulse
        if lowest_candle['close'] < lowest_candle['open']:
            post_idx1 = df.index.get_loc(lowest_idx) + 1
            if post_idx1 + 1 < len(df):
                impulse = df.iloc[post_idx1:post_idx1+2]
                if all(c['close'] > c['open'] for _, c in impulse.iterrows()):
                    if current_price <= lowest_candle['open'] and current_price >= lowest_candle['low']:
                        return 1, {"ob_type": "bullish"}

        # Find the highest high (potential Bearish OB location)
        highest_idx = window['high'].idxmax()
        highest_candle = df.loc[highest_idx]
        
        if highest_candle['close'] > highest_candle['open']:
            post_idx1 = df.index.get_loc(highest_idx) + 1
            if post_idx1 + 1 < len(df):
                impulse = df.iloc[post_idx1:post_idx1+2]
                if all(c['close'] < c['open'] for _, c in impulse.iterrows()):
                    if current_price >= highest_candle['open'] and current_price <= highest_candle['high']:
                        return -1, {"ob_type": "bearish"}
                        
        return 0, {}

class LiquiditySweepStrategy(BaseStrategy):
    """
    Detects Liquidity Sweeps (Stop Hunts).
    Price breaks a significant high/low but immediately rejects and closes back inside the range.
    """
    def generate_signals(self, df: pd.DataFrame, current_price: float) -> Tuple[int, Dict[str, Any]]:
        if len(df) < 20:
            return 0, {}
            
        recent = df.iloc[-20:-2]
        swing_low = recent['low'].min()
        swing_high = recent['high'].max()
        
        last = df.iloc[-2]
        
        # Bearish Trap / Bullish Sweep: Price wicks below swing low but closes above it
        if last['low'] < swing_low and last['close'] > swing_low:
            return 1, {"sweep": "bullish_rejection", "level": swing_low}
            
        # Bullish Trap / Bearish Sweep: Price wicks above swing high but closes below it
        if last['high'] > swing_high and last['close'] < swing_high:
            return -1, {"sweep": "bearish_rejection", "level": swing_high}
            
        return 0, {}

"""
Institutional Smart Money Concepts (ICT)
========================================
Advanced institutional strategies including Fair Value Gaps (FVG), 
Order Blocks (OB), and Liquidity Sweeps.
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
        if len(df) < 3:
            return 0, {}
            
        # We need the last 3 completed candles
        c1 = df.iloc[-4]
        c2 = df.iloc[-3]
        c3 = df.iloc[-2]
        
        # Bullish FVG
        if c3['Low'] > c1['High']:
            # The gap is between c1['High'] and c3['Low']
            fvg_size = c3['Low'] - c1['High']
            # If current price dips into this gap (mitigation), it's a buy signal
            if current_price <= c3['Low'] and current_price >= c1['High']:
                return 1, {"fvg_type": "bullish_mitigation", "fvg_size": fvg_size}
                
        # Bearish FVG
        elif c3['High'] < c1['Low']:
            fvg_size = c1['Low'] - c3['High']
            # If current price rallies into this gap, it's a sell signal
            if current_price >= c3['High'] and current_price <= c1['Low']:
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
        lowest_idx = window['Low'].idxmin()
        lowest_candle = df.loc[lowest_idx]
        
        # Check if it was a bearish candle followed by a strong impulse
        if lowest_candle['Close'] < lowest_candle['Open']:
            # Check the next 2 candles for a strong impulsive move (large range, bullish)
            post_idx1 = df.index.get_loc(lowest_idx) + 1
            if post_idx1 + 1 < len(df):
                impulse = df.iloc[post_idx1:post_idx1+2]
                if all(c['Close'] > c['Open'] for _, c in impulse.iterrows()):
                    # Price returning to the OB zone
                    if current_price <= lowest_candle['Open'] and current_price >= lowest_candle['Low']:
                        return 1, {"ob_type": "bullish"}

        # Find the highest high (potential Bearish OB location)
        highest_idx = window['High'].idxmax()
        highest_candle = df.loc[highest_idx]
        
        if highest_candle['Close'] > highest_candle['Open']:
            post_idx1 = df.index.get_loc(highest_idx) + 1
            if post_idx1 + 1 < len(df):
                impulse = df.iloc[post_idx1:post_idx1+2]
                if all(c['Close'] < c['Open'] for _, c in impulse.iterrows()):
                    # Price returning to OB zone
                    if current_price >= highest_candle['Open'] and current_price <= highest_candle['High']:
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
        swing_low = recent['Low'].min()
        swing_high = recent['High'].max()
        
        last = df.iloc[-2]
        
        # Bearish Trap / Bullish Sweep: Price wicks below swing low but closes above it
        if last['Low'] < swing_low and last['Close'] > swing_low:
            return 1, {"sweep": "bullish_rejection", "level": swing_low}
            
        # Bullish Trap / Bearish Sweep: Price wicks above swing high but closes below it
        if last['High'] > swing_high and last['Close'] < swing_high:
            return -1, {"sweep": "bearish_rejection", "level": swing_high}
            
        return 0, {}

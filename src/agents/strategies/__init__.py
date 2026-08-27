"""
Strategy Registry — Base Classes & Auto-Discovery
====================================================
Provides the foundation for all 111 trading strategies:

- BaseStrategy: Abstract base class that every strategy inherits from.
- StrategySignal: Structured output from each strategy evaluation.
- StrategyRegistry: Singleton that auto-registers all strategy classes.
- MarketRegime: Enum for classifying current market conditions.
- classify_market_regime(): Determines if market is TRENDING, RANGING,
  BREAKOUT, VOLATILE, or SHOCK based on indicators.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import pandas as pd
import numpy as np


# ── Market Regime Classification ────────────────────────────────

class MarketRegime(Enum):
    TRENDING_BULLISH = "TRENDING_BULLISH"
    TRENDING_BEARISH = "TRENDING_BEARISH"
    RANGING = "RANGING"
    BREAKOUT = "BREAKOUT"
    VOLATILE = "VOLATILE"
    SHOCK = "SHOCK"
    UNKNOWN = "UNKNOWN"


def classify_market_regime(
    df: pd.DataFrame,
    sentiment_data: dict | None = None,
) -> MarketRegime:
    """
    Classify the current market regime based on indicators.

    Uses ADX for trend strength, Bollinger Band width for volatility,
    ATR spikes for breakout/volatile detection, and sentiment for shock.

    Args:
        df: OHLCV DataFrame with computed indicators.
        sentiment_data: Output from Agent 2 (optional).

    Returns:
        MarketRegime enum value.
    """
    curr = df.iloc[-1]

    # ── Sentiment shock check ───────────────────────────────
    if sentiment_data:
        score = sentiment_data.get("sentiment_score", 50)
        if score < 15 or score > 85:
            return MarketRegime.SHOCK

    # ── ADX-based trend detection ───────────────────────────
    adx = curr.get("adx")
    if pd.notna(adx):
        if adx > 25:
            # Strong trend — determine direction
            sma_20 = curr.get("sma_20")
            price = curr["close"]
            if pd.notna(sma_20) and price > sma_20:
                return MarketRegime.TRENDING_BULLISH
            elif pd.notna(sma_20):
                return MarketRegime.TRENDING_BEARISH
            return MarketRegime.TRENDING_BULLISH  # Default bullish if cant determine
        elif adx < 20:
            # Weak trend — ranging market
            return MarketRegime.RANGING

    # ── ATR spike detection (breakout/volatile) ─────────────
    atr = curr.get("atr")
    if pd.notna(atr) and len(df) > 14:
        avg_atr = df["atr"].rolling(14).mean().iloc[-1]
        if pd.notna(avg_atr) and avg_atr > 0:
            atr_ratio = atr / avg_atr
            if atr_ratio > 2.0:
                return MarketRegime.VOLATILE
            elif atr_ratio > 1.5:
                return MarketRegime.BREAKOUT

    # ── Bollinger Band width for ranging detection ──────────
    bb_upper = curr.get("bb_upper")
    bb_lower = curr.get("bb_lower")
    bb_middle = curr.get("bb_middle")
    if pd.notna(bb_upper) and pd.notna(bb_lower) and pd.notna(bb_middle) and bb_middle > 0:
        bb_width = (bb_upper - bb_lower) / bb_middle
        if bb_width < 0.04:  # Very tight bands = ranging/squeeze
            return MarketRegime.RANGING

    # ── Fallback: use SMA alignment ─────────────────────────
    sma_20 = curr.get("sma_20")
    sma_50 = curr.get("sma_50")
    price = curr["close"]

    if pd.notna(sma_20) and pd.notna(sma_50):
        if price > sma_20 > sma_50:
            return MarketRegime.TRENDING_BULLISH
        elif price < sma_20 < sma_50:
            return MarketRegime.TRENDING_BEARISH

    return MarketRegime.RANGING  # Default to ranging if unclear


# ── Strategy Signal Output ──────────────────────────────────────

@dataclass
class StrategySignal:
    """Structured output from a strategy evaluation."""
    triggered: bool
    signal: str  # "BUY", "SELL", "HOLD"
    confidence: float  # 0.0 to 1.0
    strategy_name: str
    category: str
    reasoning: str
    weight: float = 1.0  # Category weight for confluence scoring


# ── Base Strategy Class ─────────────────────────────────────────

class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    Every strategy must implement the `evaluate` method.
    Strategies auto-register themselves upon class creation.
    """

    name: str = "Unnamed Strategy"
    category: str = "uncategorized"
    description: str = ""
    # Which regimes this strategy works best in (empty = all regimes)
    suitable_regimes: list[MarketRegime] = []
    # Category weight for confluence scoring
    weight: float = 1.0

    def __init_subclass__(cls, **kwargs):
        """Auto-register every subclass into the global registry."""
        super().__init_subclass__(**kwargs)
        # Only register concrete strategies (those with a real name)
        if hasattr(cls, "name") and cls.name != "Unnamed Strategy":
            StrategyRegistry.register(cls)

    @abstractmethod
    def evaluate(
        self,
        df: pd.DataFrame,
        sentiment_data: dict | None = None,
    ) -> StrategySignal:
        """
        Evaluate this strategy against current market data.

        Args:
            df: OHLCV DataFrame with all computed indicators.
            sentiment_data: Output from Agent 2 (optional, for sentiment strategies).

        Returns:
            StrategySignal with triggered status, signal, confidence, and reasoning.
        """
        ...

    def _not_triggered(self, reason: str = "Conditions not met") -> StrategySignal:
        """Helper to return a non-triggered signal."""
        return StrategySignal(
            triggered=False,
            signal="HOLD",
            confidence=0.0,
            strategy_name=self.name,
            category=self.category,
            reasoning=reason,
            weight=self.weight,
        )

    def _triggered(
        self,
        signal: str,
        confidence: float,
        reasoning: str,
    ) -> StrategySignal:
        """Helper to return a triggered signal."""
        return StrategySignal(
            triggered=True,
            signal=signal,
            confidence=min(1.0, max(0.0, confidence)),
            strategy_name=self.name,
            category=self.category,
            reasoning=reasoning,
            weight=self.weight,
        )


# ── Strategy Registry (Singleton) ──────────────────────────────

class StrategyRegistry:
    """
    Global registry of all trading strategies.
    Strategies auto-register via BaseStrategy.__init_subclass__.
    """
    _strategies: dict[str, type[BaseStrategy]] = {}
    _blacklist: list[str] = []

    @classmethod
    def set_blacklist(cls, names: list[str]) -> None:
        """Set the list of currently unprofitable strategies to skip."""
        cls._blacklist = names
        
    @classmethod
    def get_blacklist(cls) -> list[str]:
        return cls._blacklist

    @classmethod
    def register(cls, strategy_class: type[BaseStrategy]) -> None:
        """Register a strategy class."""
        cls._strategies[strategy_class.name] = strategy_class

    @classmethod
    def get_all(cls) -> list[BaseStrategy]:
        """Get instances of all registered strategies, ignoring blacklisted ones."""
        return [s() for name, s in cls._strategies.items() if name not in cls._blacklist]

    @classmethod
    def get_by_category(cls, category: str) -> list[BaseStrategy]:
        """Get instances of strategies in a specific category, ignoring blacklisted ones."""
        return [s() for name, s in cls._strategies.items() if s.category == category and name not in cls._blacklist]

    @classmethod
    def get_for_regime(cls, regime: MarketRegime) -> list[BaseStrategy]:
        """Get strategies suitable for a specific market regime, ignoring blacklisted ones."""
        result = []
        for name, strategy_class in cls._strategies.items():
            if name in cls._blacklist:
                continue
            # If no suitable_regimes specified, strategy works in all regimes
            if not strategy_class.suitable_regimes or regime in strategy_class.suitable_regimes:
                result.append(strategy_class())
        return result

    @classmethod
    def count(cls) -> int:
        """Total number of registered strategies."""
        return len(cls._strategies)

    @classmethod
    def list_names(cls) -> list[str]:
        """List all registered strategy names."""
        return list(cls._strategies.keys())

    @classmethod
    def summary(cls) -> dict[str, int]:
        """Count strategies by category."""
        counts: dict[str, int] = {}
        for s in cls._strategies.values():
            counts[s.category] = counts.get(s.category, 0) + 1
        return counts

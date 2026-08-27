"""
Agent 3: Pattern & Strategy Engine (v2 — 111 Strategies)
==========================================================
Upgraded strategy engine using the modular Strategy Registry.

Pipeline:
  1. Classify Market Regime (TRENDING / RANGING / BREAKOUT / VOLATILE / SHOCK)
  2. Run ALL 111 strategies (filtered by regime suitability)
  3. Collect triggered strategies
  4. Score confluence (multiple strategies agreeing = higher confidence)
  5. Select top signal and generate trade proposal with SL/TP

Uses category weights for confluence scoring:
  candlestick=1.0x, trend=1.5x, momentum=1.3x, volatility=1.2x,
  volume=2.0x, chart_pattern=1.5x, mean_reversion=1.2x, sentiment=1.5x
"""

import pandas as pd
import ta
from src import config
from src.agents.strategies import (
    StrategyRegistry,
    StrategySignal,
    MarketRegime,
    classify_market_regime,
)

# Import all strategy modules to trigger auto-registration
from src.agents.strategies import candlestick_patterns  # noqa: F401 — 31 strategies
from src.agents.strategies import trend_following        # noqa: F401 — 15 strategies
from src.agents.strategies import momentum               # noqa: F401 — 15 strategies
from src.agents.strategies import volatility              # noqa: F401 — 10 strategies
from src.agents.strategies import volume_based            # noqa: F401 — 10 strategies
from src.agents.strategies import chart_patterns          # noqa: F401 — 15 strategies
from src.agents.strategies import mean_reversion          # noqa: F401 — 5 strategies
from src.agents.strategies import sentiment_hybrid        # noqa: F401 — 10 strategies


def _compute_extended_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute additional indicators needed by the 111 strategies
    beyond what Agent 1 already provides (ADX for regime classification).
    """
    if "adx" not in df.columns:
        try:
            adx_ind = ta.trend.ADXIndicator(df["high"], df["low"], df["close"], window=14)
            df["adx"] = adx_ind.adx()
        except Exception:
            pass
    return df


def run_all_strategies(
    df: pd.DataFrame,
    sentiment_data: dict | None = None,
    regime: MarketRegime | None = None,
) -> list[StrategySignal]:
    """
    Run all 111 registered strategies against current data.

    Args:
        df: OHLCV DataFrame with computed indicators.
        sentiment_data: Output from Agent 2.
        regime: Pre-classified market regime (if None, strategies run in all-regime mode).

    Returns:
        List of StrategySignal results from all strategies.
    """
    if regime:
        strategies = StrategyRegistry.get_for_regime(regime)
    else:
        strategies = StrategyRegistry.get_all()

    results = []
    for strategy in strategies:
        try:
            signal = strategy.evaluate(df, sentiment_data)
            results.append(signal)
        except Exception:
            # Don't let one broken strategy crash the pipeline
            continue

    return results


def score_confluence(signals: list[StrategySignal]) -> dict:
    """
    Score the confluence of triggered strategies.

    Counts how many strategies agree on BUY vs SELL,
    weighted by category weights. Higher confluence = higher confidence.

    Returns:
        Dict with buy_score, sell_score, hold_count, and details.
    """
    triggered = [s for s in signals if s.triggered]

    buy_score = 0.0
    sell_score = 0.0
    hold_count = 0
    buy_strategies = []
    sell_strategies = []
    hold_strategies = []

    for s in triggered:
        weighted = s.confidence * s.weight
        if s.signal == "BUY":
            buy_score += weighted
            buy_strategies.append(s)
        elif s.signal == "SELL":
            sell_score += weighted
            sell_strategies.append(s)
        elif s.signal == "HOLD":
            hold_count += 1
            hold_strategies.append(s)

    return {
        "buy_score": round(buy_score, 4),
        "sell_score": round(sell_score, 4),
        "hold_count": hold_count,
        "buy_count": len(buy_strategies),
        "sell_count": len(sell_strategies),
        "buy_strategies": buy_strategies,
        "sell_strategies": sell_strategies,
        "hold_strategies": hold_strategies,
        "total_triggered": len(triggered),
        "total_scanned": len(signals),
    }


def select_top_signal(confluence: dict) -> dict:
    """
    Select the final trade signal based on confluence scoring.

    Rules:
      - If any HOLD override (Sentiment Shock) with confidence > 0.9 → force HOLD
      - If buy_score > sell_score and buy_count >= 3 → BUY
      - If sell_score > buy_score and sell_count >= 3 → SELL
      - Otherwise → HOLD (capital preservation)

    Returns:
        Dict with action, confidence, strategy names, and reasoning.
    """
    # Check for high-priority HOLD overrides (e.g., Sentiment Shock)
    for h in confluence["hold_strategies"]:
        if h.confidence > 0.9:
            return {
                "action": "HOLD",
                "confidence": h.confidence,
                "strategy": h.strategy_name,
                "reasoning": h.reasoning,
                "confluence_buy": confluence["buy_count"],
                "confluence_sell": confluence["sell_count"],
            }

    buy_score = confluence["buy_score"]
    sell_score = confluence["sell_score"]
    buy_count = confluence["buy_count"]
    sell_count = confluence["sell_count"]

    # Need minimum 2 strategies agreeing for a signal
    min_confluence = 2

    if buy_score > sell_score and buy_count >= min_confluence:
        # Sort by confidence, take top strategies for reasoning
        top = sorted(confluence["buy_strategies"], key=lambda s: s.confidence * s.weight, reverse=True)
        top_names = [s.strategy_name for s in top[:5]]
        top_reasons = [s.reasoning for s in top[:3]]
        overall_conf = min(0.95, buy_score / (buy_score + sell_score + 0.01))
        return {
            "action": "BUY",
            "confidence": round(overall_conf, 4),
            "strategy": "CONFLUENCE_BUY",
            "top_strategies": top_names,
            "reasoning": f"{buy_count} strategies agree on BUY (score: {buy_score:.2f} vs SELL: {sell_score:.2f}). Top signals: {'; '.join(top_reasons)}",
            "confluence_buy": buy_count,
            "confluence_sell": sell_count,
        }

    if sell_score > buy_score and sell_count >= min_confluence:
        top = sorted(confluence["sell_strategies"], key=lambda s: s.confidence * s.weight, reverse=True)
        top_names = [s.strategy_name for s in top[:5]]
        top_reasons = [s.reasoning for s in top[:3]]
        overall_conf = min(0.95, sell_score / (buy_score + sell_score + 0.01))
        return {
            "action": "SELL",
            "confidence": round(overall_conf, 4),
            "strategy": "CONFLUENCE_SELL",
            "top_strategies": top_names,
            "reasoning": f"{sell_count} strategies agree on SELL (score: {sell_score:.2f} vs BUY: {buy_score:.2f}). Top signals: {'; '.join(top_reasons)}",
            "confluence_buy": buy_count,
            "confluence_sell": sell_count,
        }

    return {
        "action": "HOLD",
        "confidence": 0.0,
        "strategy": "CAPITAL_PRESERVATION",
        "reasoning": f"No clear confluence. BUY: {buy_count} strategies ({buy_score:.2f}), SELL: {sell_count} ({sell_score:.2f}). Waiting for stronger signal.",
        "confluence_buy": buy_count,
        "confluence_sell": sell_count,
    }


def compute_trade_levels(
    signal: dict,
    current_price: float,
    atr: float | None = None,
) -> dict:
    """
    Compute entry, stop-loss (SL), and take-profit (TP) levels.
    Uses ATR-based levels if available, else percentage-based.
    """
    action = signal.get("action", "HOLD")
    if action == "HOLD":
        return {"entry_price": None, "stop_loss": None, "take_profit": None, "risk_reward_ratio": None}

    if atr and atr > 0:
        sl_distance = atr * 1.5
        tp_distance = atr * 3.0
    else:
        sl_distance = current_price * config.DEFAULT_SL_PERCENT
        tp_distance = current_price * config.DEFAULT_TP_PERCENT

    if action == "BUY":
        sl = round(current_price - sl_distance, 4)
        tp = round(current_price + tp_distance, 4)
    elif action == "SELL":
        sl = round(current_price + sl_distance, 4)
        tp = round(current_price - tp_distance, 4)
    else:
        return {"entry_price": None, "stop_loss": None, "take_profit": None, "risk_reward_ratio": None}

    risk = abs(current_price - sl)
    reward = abs(tp - current_price)
    rr = round(reward / risk, 2) if risk > 0 else 0

    return {
        "entry_price": round(current_price, 4),
        "stop_loss": sl,
        "take_profit": tp,
        "risk_reward_ratio": rr,
    }


def analyze(
    technical_data: dict,
    sentiment_data: dict,
    current_price: float,
    df: pd.DataFrame | None = None,
) -> dict:
    """
    Full Agent 3 pipeline — 111-strategy confluence engine.

    Args:
        technical_data: Output from Agent 1 (technical_agent.analyze).
        sentiment_data: Output from Agent 2 (sentiment_agent.analyze).
        current_price: Latest market price.
        df: Full OHLCV DataFrame with indicators (for strategy evaluation).

    Returns:
        Complete trade proposal payload.
    """
    symbol = technical_data.get("symbol", "")
    atr = technical_data.get("indicators", {}).get("atr_14")

    # If df not provided, we can't run the 111-strategy engine
    # Fall back to basic signal from technical/sentiment scores
    if df is None or df.empty:
        return {
            "agent": "Strategy Engine (Agent 3)",
            "symbol": symbol,
            "current_price": round(current_price, 4),
            "action": "HOLD",
            "confidence": 0.0,
            "strategy": "NO_DATA",
            "reasoning": "No OHLCV dataframe available for strategy evaluation.",
            "entry_price": None,
            "stop_loss": None,
            "take_profit": None,
            "risk_reward_ratio": None,
        }

    # Step 1: Extend indicators (ADX for regime classification)
    df = _compute_extended_indicators(df)

    # Step 2: Classify market regime
    regime = classify_market_regime(df, sentiment_data)

    # Step 3: Run all 111 strategies
    all_signals = run_all_strategies(df, sentiment_data, regime)

    # Step 4: Score confluence
    confluence = score_confluence(all_signals)

    # Step 5: Select top signal
    top_signal = select_top_signal(confluence)

    # Step 6: Compute trade levels
    trade_levels = compute_trade_levels(top_signal, current_price, atr)

    # Step 7: Build output payload
    payload = {
        "agent": "Strategy Engine (Agent 3) — 111 Strategies",
        "symbol": symbol,
        "current_price": round(current_price, 4),
        "market_regime": regime.value,
        "strategies_registered": StrategyRegistry.count(),
        "strategies_scanned": confluence["total_scanned"],
        "strategies_triggered": confluence["total_triggered"],
        "confluence_buy": confluence["buy_count"],
        "confluence_sell": confluence["sell_count"],
        "buy_score": confluence["buy_score"],
        "sell_score": confluence["sell_score"],
        **top_signal,
        **trade_levels,
    }

    return payload

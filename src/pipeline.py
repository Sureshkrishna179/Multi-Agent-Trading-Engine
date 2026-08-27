"""
Multi-Agent Trading Bot — Core Execution Pipeline
=================================================
Runs the complete 6-agent pipeline for a single asset.
"""

from src.connectors import indian_market, crypto_market
from src.agents import technical_agent, sentiment_agent, strategy_agent, risk_executor_agent, fundamental_agent, debate_agent, ml_agent, strategy_optimizer
from src.agents.strategies import StrategyRegistry

def run_pipeline(symbol: str, market_type: str) -> dict:
    """
    Execute the full 6-agent trading pipeline for a single asset.
    """
    # ── Stage 1: Fetch Market Data ──────────────────────────────
    if market_type == "indian":
        df = indian_market.fetch_ohlcv(symbol, period_days=60)
        current_price = indian_market.get_current_price(symbol)
    else:
        df = crypto_market.fetch_ohlcv(symbol, timeframe="1d", limit=60)
        current_price = crypto_market.get_current_price(symbol)

    # ── Stage 2: Agent 1 — Technical Analysis ───────────────────
    tech_result = technical_agent.analyze(df, symbol)

    # ── Stage 3: Agent 2 — Sentiment Analysis ───────────────────
    sent_result = sentiment_agent.analyze(symbol=symbol, market_type=market_type)

    # ── Stage 3b: Agent 5 — Fundamental Analysis ────────────────
    fund_result = fundamental_agent.analyze(symbol=symbol, market_type=market_type)
    
    # ── Stage 3c: Agent 7 — ML Brain (XGBoost) ──────────────────
    ml_result = ml_agent.analyze(df, symbol)
    
    # ── Stage 3d: Agent 8 — Strategy Optimizer ──────────────────
    # This runs the historical 30-day backtest to prune bad strategies
    opt_result = strategy_optimizer.prune_strategies(df)

    # ── Stage 4: Agent 3 — Strategy Selection (Now using the Pruned Alpha 100) ──
    strat_result = strategy_agent.analyze(tech_result, sent_result, current_price, df=df)
    # Inject ML bias into strat_result if ML is highly confident
    if ml_result["confidence"] > 0.70:
        strat_result["reasoning"] += f" | ML Overwrite: Very strong {ml_result['action']} prediction."
        strat_result["action"] = ml_result["action"]
        strat_result["confidence"] = max(strat_result["confidence"], ml_result["confidence"])

    # ── Stage 5: Agent 6 — Bull vs Bear Debate ──────────────────
    debate_result = debate_agent.debate(symbol, tech_result, sent_result, strat_result, fund_result)
    
    # Override strat_result action and confidence with Judge's decision
    strat_result["action"] = debate_result.get("final_action", strat_result["action"])
    strat_result["confidence"] = debate_result.get("final_confidence", strat_result["confidence"])
    
    # ── Stage 6: Agent 4 — Risk & Execution ─────────────────────
    risk_result = risk_executor_agent.analyze(strat_result, symbol, market_type)

    return {
        "symbol": symbol,
        "market_type": market_type,
        "agent_1_technical": tech_result,
        "agent_2_sentiment": sent_result,
        "agent_5_fundamental": fund_result,
        "agent_7_ml": ml_result,
        "agent_8_optimizer": opt_result,
        "agent_3_strategy": strat_result,
        "agent_6_debate": debate_result,
        "agent_4_risk_execution": risk_result,
    }

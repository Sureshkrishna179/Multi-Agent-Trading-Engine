"""
Multi-Agent Trading Bot — Core Execution Pipeline
=================================================
Runs the complete 8-agent pipeline for a single asset.
Now includes Weighted Consensus Engine for mathematically superior decisions.
"""

from src.connectors import indian_market, crypto_market
from src.agents import technical_agent, sentiment_agent, strategy_agent, risk_executor_agent, fundamental_agent, debate_agent, ml_agent, strategy_optimizer
from src.agents.strategies import StrategyRegistry
from src.agents.agent_charter import compute_consensus

def run_pipeline(symbol: str, market_type: str) -> dict:
    """
    Execute the full 8-agent trading pipeline for a single asset.
    Uses Weighted Consensus Engine for the final decision.
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
    opt_result = strategy_optimizer.prune_strategies(df)

    # ── Stage 4: Agent 3 — Strategy Selection ───────────────────
    strat_result = strategy_agent.analyze(tech_result, sent_result, current_price, df=df)

    # ── Stage 5: Agent 6 — Bull vs Bear Debate ──────────────────
    debate_result = debate_agent.debate(symbol, tech_result, sent_result, strat_result, fund_result)

    # ── Stage 6: Weighted Consensus Engine ──────────────────────
    # All agents have spoken. Now compute the mathematically weighted consensus.
    raw_results = {
        "symbol": symbol,
        "market_type": market_type,
        "agent_1_technical": tech_result,
        "agent_2_sentiment": sent_result,
        "agent_5_fundamental": fund_result,
        "agent_7_ml": ml_result,
        "agent_8_optimizer": opt_result,
        "agent_3_strategy": strat_result,
        "agent_6_debate": debate_result,
    }
    
    consensus = compute_consensus(raw_results)
    
    # ── Stage 7: Agent 4 — Risk Guardian (Final Gatekeeper) ─────
    # Feed the CONSENSUS action (not a single agent's opinion) to the Risk Guardian.
    # The Risk Guardian has VETO power — it can reject even a unanimous BUY.
    consensus_proposal = {
        "action": consensus["consensus_action"],
        "confidence": consensus["confidence"],
        "reasoning": f"Weighted Consensus: {consensus['strength']} {consensus['consensus_action']} (Score: {consensus['consensus_score']:.2f})",
        "stop_loss": strat_result.get("stop_loss"),
        "take_profit": strat_result.get("take_profit"),
    }
    
    risk_result = risk_executor_agent.analyze(consensus_proposal, symbol, market_type)

    raw_results["consensus"] = consensus
    raw_results["agent_4_risk_execution"] = risk_result
    
    return raw_results

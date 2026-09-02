"""
Multi-Agent Trading Bot — Async DAG Execution Pipeline
======================================================
Production-grade pipeline using concurrent execution.

Architecture (Directed Acyclic Graph):
                    ┌─ Agent 1 (Technical)  ─┐
                    ├─ Agent 2 (Sentiment)   ─┤
  Fetch Data ──────>├─ Agent 5 (Fundamental) ─├──> Agent 3 (Strategy) ──> Agent 6 (Debate) ──> Consensus ──> Agent 4 (Risk)
                    ├─ Agent 7 (ML Brain)    ─┤
                    └─ Agent 8 (Optimizer)   ─┘
                         PARALLEL LAYER              SEQUENTIAL LAYER

Speed: ~3x faster than sequential execution.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.connectors import indian_market, crypto_market
from src.agents import technical_agent, sentiment_agent, strategy_agent, risk_executor_agent, fundamental_agent, debate_agent, ml_agent, strategy_optimizer
from src.agents.strategies import StrategyRegistry
from src.agents.agent_charter import compute_consensus
from src.agents.ml_monitor import log_prediction, get_model_health


def run_pipeline(symbol: str, market_type: str) -> dict:
    """
    Execute the full 8-agent trading pipeline using DAG-based parallel execution.
    
    Phase 1 (Parallel):  Agents 1, 2, 5, 7, 8 run simultaneously
    Phase 2 (Sequential): Agent 3 depends on Agent 1+2 outputs
    Phase 3 (Sequential): Agent 6 depends on Agents 1+2+3+5
    Phase 4 (Consensus):  Weighted vote across all agents
    Phase 5 (Gatekeeper): Agent 4 Risk Guardian with VETO power
    """
    pipeline_start = time.time()
    
    # ══════════════════════════════════════════════════════════════
    # PHASE 0: DATA INGESTION
    # ══════════════════════════════════════════════════════════════
    if market_type == "indian":
        df = indian_market.fetch_ohlcv(symbol, period_days=60)
        current_price = indian_market.get_current_price(symbol)
    else:
        df = crypto_market.fetch_ohlcv(symbol, timeframe="1d", limit=60)
        current_price = crypto_market.get_current_price(symbol)

    # ══════════════════════════════════════════════════════════════
    # PHASE 1: PARALLEL AGENT EXECUTION (Non-blocking DAG Layer)
    # ══════════════════════════════════════════════════════════════
    # These 5 agents are completely independent — they don't need
    # each other's outputs. Run them all at the same time.
    parallel_results = {}
    
    def _run_technical():
        return ("agent_1_technical", technical_agent.analyze(df, symbol))
    
    def _run_sentiment():
        return ("agent_2_sentiment", sentiment_agent.analyze(symbol=symbol, market_type=market_type))
    
    def _run_fundamental():
        return ("agent_5_fundamental", fundamental_agent.analyze(symbol=symbol, market_type=market_type))
    
    def _run_ml():
        return ("agent_7_ml", ml_agent.analyze(df, symbol))
    
    def _run_optimizer():
        return ("agent_8_optimizer", strategy_optimizer.prune_strategies(df))
    
    parallel_tasks = [_run_technical, _run_sentiment, _run_fundamental, _run_ml, _run_optimizer]
    
    with ThreadPoolExecutor(max_workers=5, thread_name_prefix="agent") as executor:
        futures = {executor.submit(task): task.__name__ for task in parallel_tasks}
        
        for future in as_completed(futures):
            try:
                key, result = future.result()
                parallel_results[key] = result
            except Exception as e:
                task_name = futures[future]
                print(f"   ❌ Parallel agent '{task_name}' failed: {e}")
                # Provide safe fallback so pipeline doesn't crash
                parallel_results[task_name] = _get_fallback(task_name)
    
    tech_result = parallel_results.get("agent_1_technical", {})
    sent_result = parallel_results.get("agent_2_sentiment", {})
    fund_result = parallel_results.get("agent_5_fundamental", {})
    ml_result = parallel_results.get("agent_7_ml", {})
    opt_result = parallel_results.get("agent_8_optimizer", {})

    # ══════════════════════════════════════════════════════════════
    # PHASE 2: SEQUENTIAL — Agent 3 (Strategy Selection)
    # Depends on: Agent 1 (tech) + Agent 2 (sentiment) outputs
    # ══════════════════════════════════════════════════════════════
    strat_result = strategy_agent.analyze(tech_result, sent_result, current_price, df=df)

    # ══════════════════════════════════════════════════════════════
    # PHASE 3: SEQUENTIAL — Agent 6 (Bull vs Bear Debate)
    # Depends on: Agents 1, 2, 3, 5 outputs
    # ══════════════════════════════════════════════════════════════
    debate_result = debate_agent.debate(symbol, tech_result, sent_result, strat_result, fund_result)

    # ══════════════════════════════════════════════════════════════
    # PHASE 4: WEIGHTED CONSENSUS ENGINE
    # All agents have voted. Compute the mathematical consensus.
    # ══════════════════════════════════════════════════════════════
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
    
    # ══════════════════════════════════════════════════════════════
    # PHASE 5: AGENT 4 — RISK GUARDIAN (Final Gatekeeper)
    # Has absolute VETO power over any trade.
    # ══════════════════════════════════════════════════════════════
    consensus_proposal = {
        "action": consensus["consensus_action"],
        "confidence": consensus["confidence"],
        "reasoning": f"Weighted Consensus: {consensus['strength']} {consensus['consensus_action']} (Score: {consensus['consensus_score']:.2f})",
        "stop_loss": strat_result.get("stop_loss"),
        "take_profit": strat_result.get("take_profit"),
    }
    
    risk_result = risk_executor_agent.analyze(consensus_proposal, symbol, market_type)

    # ══════════════════════════════════════════════════════════════
    # PHASE 6: MLOPS — Log prediction for drift monitoring
    # ══════════════════════════════════════════════════════════════
    ml_action = ml_result.get("action", "HOLD")
    if ml_action != "HOLD":
        log_prediction(symbol, ml_action, current_price)
    
    ml_health = get_model_health()

    pipeline_time = time.time() - pipeline_start
    
    raw_results["consensus"] = consensus
    raw_results["agent_4_risk_execution"] = risk_result
    raw_results["ml_health"] = ml_health
    raw_results["pipeline_time_seconds"] = round(pipeline_time, 2)
    
    print(f"   ⚡ Pipeline completed in {pipeline_time:.2f}s (Parallel DAG)")
    
    return raw_results


def _get_fallback(task_name: str) -> dict:
    """Safe fallback values if a parallel agent crashes."""
    fallbacks = {
        "_run_technical": {"trend": "N/A", "technical_score": 0.0},
        "_run_sentiment": {"sentiment_score": 50, "sentiment_label": "NEUTRAL"},
        "_run_fundamental": {"recommendation": "HOLD"},
        "_run_ml": {"action": "HOLD", "confidence": 0.0},
        "_run_optimizer": {"pruned": 0, "total_tested": 0, "active_alpha_strategies": 0},
    }
    return fallbacks.get(task_name, {})

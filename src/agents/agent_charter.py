"""
Agent Charter & Weighted Consensus Engine
==========================================
Inspired by the "Grok Bot with Kimi K3" autonomous agent methodology.

Each agent has a strict Charter (what it owns) and Fence Line (what it must NEVER do).
The Weighted Consensus Engine combines all agent signals into a single mathematically
weighted score for superior decision-making.

MLOps Integration: Dynamically adjusts ML Agent weight based on model health.
If model drift is detected, ML weight drops to 0% automatically.

Cost: $0 — Pure Python math, no external APIs.
"""

from src.agents.ml_monitor import get_model_health


# ─── Agent Charters ─────────────────────────────────────────────
# Each charter defines the agent's role, ownership, and hard boundaries.

CHARTERS = {
    "agent_1_technical": {
        "name": "Technical Observer",
        "owns": "Price action, indicators (RSI, MACD, Bollinger, ATR), candlestick patterns, trend detection",
        "fence": "Must NEVER consider news, sentiment, or fundamentals. Only raw price data.",
        "weight": 0.20,
    },
    "agent_2_sentiment": {
        "name": "Sentiment Analyst",
        "owns": "News RSS feeds, Reddit threads, Twitter posts, community mood scoring",
        "fence": "Must NEVER look at price charts or technical indicators. Only text-based signals.",
        "weight": 0.10,
    },
    "agent_3_strategy": {
        "name": "Strategy Selector",
        "owns": "150+ trading strategies, pattern matching, entry/exit signal generation",
        "fence": "Must NEVER override Risk Guardian. Must respect the Optimizer's blacklist.",
        "weight": 0.15,
    },
    "agent_4_risk": {
        "name": "Risk Guardian",
        "owns": "Position sizing, stop-loss enforcement, daily drawdown halt, trade approval/veto",
        "fence": "Must NEVER approve a trade without a stop-loss. Must NEVER risk more than 2% per trade.",
        "weight": 0.00,  # Risk Guardian doesn't vote — it has VETO power instead
    },
    "agent_5_fundamental": {
        "name": "Fundamental Analyst",
        "owns": "P/E ratios, market cap, revenue growth, debt-to-equity, crypto fundamentals (CoinGecko)",
        "fence": "Must NEVER consider short-term price movements. Only long-term value metrics.",
        "weight": 0.10,
    },
    "agent_6_debate": {
        "name": "Bull vs Bear Judge",
        "owns": "Synthesizing bull and bear arguments, making a final directional judgment",
        "fence": "Must NEVER ignore any agent's input. Must weigh all evidence before judging.",
        "weight": 0.10,
    },
    "agent_7_ml": {
        "name": "ML Brain (XGBoost)",
        "owns": "Feature engineering, model training, probabilistic direction prediction",
        "fence": "Must NEVER trade based on predictions alone. Must pass through Risk Guardian.",
        "weight": 0.25,  # Highest weight — data-driven mathematical prediction
    },
    "agent_8_optimizer": {
        "name": "Alpha Optimizer",
        "owns": "30-day historical backtesting, strategy win-rate calculation, blacklist management",
        "fence": "Must NEVER blacklist a strategy without testing at least 3 signals.",
        "weight": 0.10,
    },
}


# ─── Signal Conversion Helpers ──────────────────────────────────

def _action_to_signal(action: str) -> float:
    """Convert a text action to a numeric signal (-1.0 to +1.0)."""
    action = action.upper().strip()
    if action in ("BUY", "STRONG_BUY", "BULLISH"):
        return 1.0
    elif action in ("SELL", "STRONG_SELL", "BEARISH"):
        return -1.0
    else:
        return 0.0


def _score_to_signal(score: float) -> float:
    """Clamp any numeric score to [-1.0, +1.0]."""
    return max(-1.0, min(1.0, score))


# ─── Weighted Consensus Engine ──────────────────────────────────

def compute_consensus(pipeline_result: dict) -> dict:
    """
    Combines all 8 agent outputs into a single Weighted Consensus Score.
    
    Each agent contributes a signal in the range [-1.0, +1.0]:
      - Positive = Bullish
      - Negative = Bearish
      - Zero     = Neutral / No opinion
      
    The final consensus score is a weighted average of all agent signals.
    
    Returns:
        dict with consensus_score, consensus_action, confidence, and per-agent breakdown.
    """
    agent_votes = {}
    
    # ── Agent 1: Technical ──
    tech = pipeline_result.get("agent_1_technical", {})
    tech_signal = tech.get("technical_score", 0.0)
    agent_votes["agent_1_technical"] = {
        "signal": _score_to_signal(tech_signal),
        "weight": CHARTERS["agent_1_technical"]["weight"],
        "name": CHARTERS["agent_1_technical"]["name"],
        "raw_data": f"Score: {tech_signal:.2f}, Trend: {tech.get('trend', 'N/A')}",
    }
    
    # ── Agent 2: Sentiment ──
    sent = pipeline_result.get("agent_2_sentiment", {})
    sent_score = sent.get("sentiment_score", 50)
    # Normalize sentiment from 0-100 scale to -1.0 to +1.0
    sent_signal = (sent_score - 50) / 50.0
    agent_votes["agent_2_sentiment"] = {
        "signal": _score_to_signal(sent_signal),
        "weight": CHARTERS["agent_2_sentiment"]["weight"],
        "name": CHARTERS["agent_2_sentiment"]["name"],
        "raw_data": f"Score: {sent_score}/100, Label: {sent.get('sentiment_label', 'N/A')}",
    }
    
    # ── Agent 3: Strategy ──
    strat = pipeline_result.get("agent_3_strategy", {})
    strat_signal = _action_to_signal(strat.get("action", "HOLD"))
    strat_conf = strat.get("confidence", 0.5)
    agent_votes["agent_3_strategy"] = {
        "signal": strat_signal * strat_conf,
        "weight": CHARTERS["agent_3_strategy"]["weight"],
        "name": CHARTERS["agent_3_strategy"]["name"],
        "raw_data": f"Action: {strat.get('action', 'HOLD')}, Confidence: {strat_conf:.1%}",
    }
    
    # ── Agent 5: Fundamental ──
    fund = pipeline_result.get("agent_5_fundamental", {})
    fund_signal = _action_to_signal(fund.get("recommendation", "HOLD"))
    agent_votes["agent_5_fundamental"] = {
        "signal": fund_signal * 0.7,  # Fundamentals are slower-moving, dampen slightly
        "weight": CHARTERS["agent_5_fundamental"]["weight"],
        "name": CHARTERS["agent_5_fundamental"]["name"],
        "raw_data": f"Recommendation: {fund.get('recommendation', 'N/A')}",
    }
    
    # ── Agent 6: Debate Judge ──
    debate = pipeline_result.get("agent_6_debate", {})
    debate_signal = _action_to_signal(debate.get("final_action", "HOLD"))
    debate_conf = debate.get("final_confidence", 0.5)
    agent_votes["agent_6_debate"] = {
        "signal": debate_signal * debate_conf,
        "weight": CHARTERS["agent_6_debate"]["weight"],
        "name": CHARTERS["agent_6_debate"]["name"],
        "raw_data": f"Judge: {debate.get('final_action', 'HOLD')}, Confidence: {debate_conf:.1%}",
    }
    
    # ── Agent 7: ML Brain (with MLOps Drift Check) ──
    ml = pipeline_result.get("agent_7_ml", {})
    ml_signal = _action_to_signal(ml.get("action", "HOLD"))
    ml_conf = ml.get("confidence", 0.0)
    
    # MLOps: Dynamically adjust weight based on model health
    ml_health = get_model_health()
    dynamic_ml_weight = ml_health.get("ml_weight", CHARTERS["agent_7_ml"]["weight"])
    ml_status = ml_health.get("status", "HEALTHY")
    ml_accuracy = ml_health.get("accuracy_pct", "N/A")
    
    agent_votes["agent_7_ml"] = {
        "signal": ml_signal * max(ml_conf, 0.5),
        "weight": dynamic_ml_weight,  # 0% if drifted, 25% if healthy
        "name": f"ML Brain ({ml_status})",
        "raw_data": f"Action: {ml.get('action', 'HOLD')}, Bull: {ml.get('prob_bull', 0):.1%}, Bear: {ml.get('prob_bear', 0):.1%} | Health: {ml_status} ({ml_accuracy})",
    }
    
    # ── Agent 8: Optimizer ──
    opt = pipeline_result.get("agent_8_optimizer", {})
    pruned = opt.get("pruned", 0)
    total = opt.get("total_tested", 1)
    # If many strategies are pruned, it's a bearish signal (market is choppy)
    opt_signal = -0.5 if (pruned / max(total, 1)) > 0.5 else 0.3
    agent_votes["agent_8_optimizer"] = {
        "signal": opt_signal,
        "weight": CHARTERS["agent_8_optimizer"]["weight"],
        "name": CHARTERS["agent_8_optimizer"]["name"],
        "raw_data": f"Tested: {total}, Pruned: {pruned}, Active: {opt.get('active_alpha_strategies', 0)}",
    }
    
    # ── Compute Weighted Consensus ──
    total_weight = sum(v["weight"] for v in agent_votes.values())
    if total_weight == 0:
        total_weight = 1.0
        
    weighted_sum = sum(v["signal"] * v["weight"] for v in agent_votes.values())
    consensus_score = weighted_sum / total_weight
    consensus_score = max(-1.0, min(1.0, consensus_score))
    
    # Determine action from consensus score
    if consensus_score > 0.15:
        consensus_action = "BUY"
    elif consensus_score < -0.15:
        consensus_action = "SELL"
    else:
        consensus_action = "HOLD"
    
    # Confidence is the absolute value of the score
    confidence = abs(consensus_score)
    
    # Strength label
    if confidence > 0.6:
        strength = "VERY STRONG"
    elif confidence > 0.35:
        strength = "STRONG"
    elif confidence > 0.15:
        strength = "MODERATE"
    else:
        strength = "WEAK"
    
    return {
        "consensus_score": round(consensus_score, 4),
        "consensus_action": consensus_action,
        "confidence": round(confidence, 4),
        "strength": strength,
        "agent_votes": agent_votes,
    }

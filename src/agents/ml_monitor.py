"""
MLOps Model Monitor — Drift Detection & Auto-Recovery
=====================================================
Production-grade monitoring for Agent 7 (XGBoost ML Brain).

Tracks every prediction vs actual outcome. If accuracy drops below
the drift threshold, automatically zeroes out the ML agent's voting
weight to prevent garbage predictions from corrupting the consensus.

When accuracy recovers after retraining, restores the original weight.

Cost: $0 — Pure Python, no external services.
"""

import os
import json
import time
from typing import Optional

MONITOR_FILE = ".cache/ml_monitor.json"
MAX_HISTORY = 200           # Keep last 200 predictions
ROLLING_WINDOW = 100        # Compute accuracy over last 100
DRIFT_THRESHOLD = 0.52      # Below 52% → model is drifting
RECOVERY_THRESHOLD = 0.55   # Above 55% → model has recovered
DEFAULT_ML_WEIGHT = 0.25    # Normal ML voting weight (25%)


def _load_monitor() -> dict:
    """Load the monitor state from disk."""
    if os.path.exists(MONITOR_FILE):
        try:
            with open(MONITOR_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "predictions": [],
        "is_drifted": False,
        "current_accuracy": None,
        "total_predictions": 0,
        "total_correct": 0,
        "last_drift_time": None,
        "last_recovery_time": None,
    }


def _save_monitor(state: dict):
    """Save monitor state to disk."""
    os.makedirs(os.path.dirname(MONITOR_FILE), exist_ok=True)
    try:
        with open(MONITOR_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"   ⚠️ MLOps Monitor save error: {e}")


def log_prediction(symbol: str, predicted_action: str, price_at_prediction: float):
    """
    Log a new ML prediction. The actual outcome will be evaluated
    on the next scan of the same symbol.
    """
    state = _load_monitor()
    
    # Before logging new prediction, evaluate any pending predictions
    # that now have enough time elapsed (we check if price moved in the predicted direction)
    _evaluate_pending(state)
    
    prediction = {
        "symbol": symbol,
        "predicted_action": predicted_action,
        "price_at_prediction": price_at_prediction,
        "timestamp": time.time(),
        "evaluated": False,
        "correct": None,
    }
    
    state["predictions"].append(prediction)
    state["total_predictions"] += 1
    
    # Trim history to prevent unbounded growth
    if len(state["predictions"]) > MAX_HISTORY:
        state["predictions"] = state["predictions"][-MAX_HISTORY:]
    
    _save_monitor(state)


def _evaluate_pending(state: dict):
    """
    Evaluate predictions that were made in the past.
    A prediction is correct if:
      - BUY prediction → price went up (we check via subsequent predictions on same symbol)
      - SELL prediction → price went down
    
    We use a simple heuristic: compare the prediction price with the latest
    prediction price for the same symbol (if available).
    """
    # Build a map of latest prices per symbol
    latest_prices = {}
    for p in reversed(state["predictions"]):
        if p["symbol"] not in latest_prices:
            latest_prices[p["symbol"]] = p["price_at_prediction"]
    
    for pred in state["predictions"]:
        if pred["evaluated"]:
            continue
            
        # Only evaluate if we have a newer price for this symbol
        # and at least 1 hour has passed
        if time.time() - pred["timestamp"] < 3600:
            continue
            
        current_price = latest_prices.get(pred["symbol"])
        if current_price is None or current_price == pred["price_at_prediction"]:
            continue
        
        price_change = current_price - pred["price_at_prediction"]
        
        if pred["predicted_action"] == "BUY":
            pred["correct"] = price_change > 0
        elif pred["predicted_action"] == "SELL":
            pred["correct"] = price_change < 0
        else:
            pred["correct"] = False
        
        pred["evaluated"] = True
        
        if pred["correct"]:
            state["total_correct"] += 1


def get_model_health() -> dict:
    """
    Returns the current ML model health status.
    Called by the pipeline and dashboard to determine if ML should vote.
    """
    state = _load_monitor()
    
    # Evaluate any pending predictions first
    _evaluate_pending(state)
    
    # Compute rolling accuracy
    evaluated = [p for p in state["predictions"] if p["evaluated"]]
    recent = evaluated[-ROLLING_WINDOW:] if len(evaluated) >= 10 else evaluated
    
    if len(recent) < 10:
        # Not enough data to judge — keep ML active
        return {
            "status": "WARMING_UP",
            "accuracy": None,
            "predictions_evaluated": len(evaluated),
            "predictions_total": state["total_predictions"],
            "is_drifted": False,
            "ml_weight": DEFAULT_ML_WEIGHT,
            "message": f"Collecting data ({len(evaluated)}/10 evaluated so far)",
        }
    
    correct_count = sum(1 for p in recent if p["correct"])
    accuracy = correct_count / len(recent)
    
    state["current_accuracy"] = round(accuracy, 4)
    
    # ── Drift Detection ──
    was_drifted = state["is_drifted"]
    
    if accuracy < DRIFT_THRESHOLD and not was_drifted:
        # MODEL DRIFT DETECTED — Zero out voting weight
        state["is_drifted"] = True
        state["last_drift_time"] = time.time()
        print(f"   🔴 MLOps ALERT: Model drift detected! Accuracy={accuracy:.1%} < {DRIFT_THRESHOLD:.0%}. ML weight → 0%")
    
    elif accuracy >= RECOVERY_THRESHOLD and was_drifted:
        # MODEL RECOVERED — Restore voting weight
        state["is_drifted"] = False
        state["last_recovery_time"] = time.time()
        print(f"   🟢 MLOps: Model recovered! Accuracy={accuracy:.1%} > {RECOVERY_THRESHOLD:.0%}. ML weight → {DEFAULT_ML_WEIGHT:.0%}")
    
    _save_monitor(state)
    
    is_drifted = state["is_drifted"]
    ml_weight = 0.0 if is_drifted else DEFAULT_ML_WEIGHT
    
    if is_drifted:
        status = "DRIFTED"
        message = f"⚠️ Model drifted ({accuracy:.1%} accuracy). Voting weight zeroed to prevent bad signals."
    else:
        status = "HEALTHY"
        message = f"Model performing well ({accuracy:.1%} accuracy over last {len(recent)} predictions)."
    
    return {
        "status": status,
        "accuracy": round(accuracy, 4),
        "accuracy_pct": f"{accuracy:.1%}",
        "predictions_evaluated": len(evaluated),
        "predictions_total": state["total_predictions"],
        "is_drifted": is_drifted,
        "ml_weight": ml_weight,
        "message": message,
    }


def reset_monitor():
    """Reset the monitor (useful after major model changes)."""
    _save_monitor({
        "predictions": [],
        "is_drifted": False,
        "current_accuracy": None,
        "total_predictions": 0,
        "total_correct": 0,
        "last_drift_time": None,
        "last_recovery_time": None,
    })
    print("   🔄 MLOps Monitor reset.")

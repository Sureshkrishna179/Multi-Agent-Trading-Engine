"""
Live Ticker & Volatility Detector
===================================
Fast-polling price monitor that detects sudden volatility spikes.

When a symbol's price moves more than the volatility threshold within
a short window, it flags the symbol for immediate re-scanning by the
8-agent pipeline.

This is a stepping stone toward full WebSocket streaming (Phase 2).

Cost: $0 — Uses free CCXT and yfinance endpoints.
"""

import time
import json
import os
from typing import Dict, List, Optional

CACHE_FILE = ".cache/volatility_alerts.json"
VOLATILITY_THRESHOLD = 0.02  # 2% price move triggers alert
CHECK_INTERVAL = 300         # Poll every 5 minutes (300 seconds)


def _load_alerts() -> dict:
    """Load cached price snapshots and alerts."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"snapshots": {}, "alerts": [], "last_check": 0}


def _save_alerts(state: dict):
    """Save alerts state to disk."""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass


def check_volatility(symbol: str, current_price: float, market_type: str) -> Optional[dict]:
    """
    Compare current price to the last recorded snapshot.
    If price has moved more than VOLATILITY_THRESHOLD, return an alert.
    
    Args:
        symbol: The ticker symbol (e.g., "BTC/USDT" or "RELIANCE.NS")
        current_price: The current live price
        market_type: "indian" or "crypto"
    
    Returns:
        Alert dict if volatility spike detected, None otherwise.
    """
    if current_price is None or current_price <= 0:
        return None
    
    state = _load_alerts()
    snapshots = state.get("snapshots", {})
    
    previous = snapshots.get(symbol)
    alert = None
    
    if previous:
        prev_price = previous["price"]
        prev_time = previous["timestamp"]
        
        if prev_price > 0:
            pct_change = (current_price - prev_price) / prev_price
            time_elapsed = time.time() - prev_time
            
            if abs(pct_change) >= VOLATILITY_THRESHOLD:
                direction = "SPIKE_UP" if pct_change > 0 else "SPIKE_DOWN"
                alert = {
                    "symbol": symbol,
                    "market_type": market_type,
                    "direction": direction,
                    "pct_change": round(pct_change * 100, 2),
                    "prev_price": prev_price,
                    "current_price": current_price,
                    "time_elapsed_minutes": round(time_elapsed / 60, 1),
                    "timestamp": time.time(),
                    "message": f"🚨 {symbol}: {pct_change:+.2%} move detected ({direction})! "
                               f"${prev_price:.2f} → ${current_price:.2f} in {time_elapsed/60:.0f} min",
                }
                
                # Add to alert history (keep last 50)
                state["alerts"].append(alert)
                state["alerts"] = state["alerts"][-50:]
                
                print(f"   {alert['message']}")
    
    # Update snapshot
    snapshots[symbol] = {
        "price": current_price,
        "timestamp": time.time(),
        "market_type": market_type,
    }
    state["snapshots"] = snapshots
    state["last_check"] = time.time()
    
    _save_alerts(state)
    return alert


def get_recent_alerts(max_age_hours: int = 6) -> List[dict]:
    """
    Return recent volatility alerts within the specified time window.
    Used by the dashboard to display active alerts.
    """
    state = _load_alerts()
    cutoff = time.time() - (max_age_hours * 3600)
    
    recent = [a for a in state.get("alerts", []) if a.get("timestamp", 0) > cutoff]
    return recent


def get_all_snapshots() -> Dict[str, dict]:
    """Return all current price snapshots. Used for dashboard display."""
    state = _load_alerts()
    return state.get("snapshots", {})

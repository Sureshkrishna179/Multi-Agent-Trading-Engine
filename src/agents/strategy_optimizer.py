"""
Agent 8: The Alpha Optimizer (Dynamic Backtester & Caching)
=================================================
Runs a fast historical backtest of all registered strategies.
Temporarily blacklists any strategy with a win rate below 50% in the current market regime.
Caches results to disk so your local PC stays fast and cool!
"""

import os
import json
import time
import pandas as pd
from src.agents.strategies import StrategyRegistry

CACHE_DIR = ".cache"
CACHE_FILE = os.path.join(CACHE_DIR, "optimizer_cache.json")
CACHE_TTL = 12 * 3600  # 12 hours in seconds

def _load_cache() -> dict | None:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                data = json.load(f)
            if time.time() - data.get("timestamp", 0) < CACHE_TTL:
                return data
        except Exception:
            pass
    return None

def _save_cache(data: dict):
    os.makedirs(CACHE_DIR, exist_ok=True)
    data["timestamp"] = time.time()
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"   ⚠️ Could not save optimizer cache: {e}")

def prune_strategies(df: pd.DataFrame, force_retest: bool = False) -> dict:
    """
    Evaluates all registered strategies on the last 30 days of data.
    Prunes (blacklists) strategies that are failing in the current market conditions.
    Uses disk caching to keep CPU usage at 0% on repeat runs!
    """
    print(f"\n⚙️ Agent 8: Running The Alpha Optimizer...")
    
    # 1. Check Cache First
    if not force_retest:
        cached = _load_cache()
        if cached:
            print("   ⚡ Using Cached Optimizer Results (0% CPU).")
            StrategyRegistry.set_blacklist(cached.get("blacklist", []))
            return cached["result"]

    if len(df) < 40:
        print("   ⚠️ Not enough data to run historical optimizer.")
        return {"scanned": 0, "pruned": 0, "active": len(StrategyRegistry.get_all())}
        
    strategies = StrategyRegistry.get_all()
    print(f"   - Testing {len(strategies)} strategies on historical 30-day window...")
    
    win_counts = {s.name: 0 for s in strategies}
    signal_counts = {s.name: 0 for s in strategies}
    
    test_range = range(len(df) - 30, len(df) - 1)
    
    for i in test_range:
        window_df = df.iloc[:i+1]
        current_price = window_df.iloc[-1]['close']
        next_price = df.iloc[i+1]['close']
        
        actual_move = 1 if next_price > current_price else -1
        
        for strategy in strategies:
            try:
                signal, _ = strategy.generate_signals(window_df, current_price)
                if signal != 0:
                    signal_counts[strategy.name] += 1
                    if signal == actual_move:
                        win_counts[strategy.name] += 1
            except Exception:
                pass

    # Evaluate win rates and blacklist losers
    blacklist = []
    
    for s in strategies:
        total = signal_counts[s.name]
        if total > 2:
            win_rate = win_counts[s.name] / total
            if win_rate < 0.50:
                blacklist.append(s.name)
                
    # Update the Registry with the blacklist
    StrategyRegistry.set_blacklist(blacklist)
    
    result = {
        "total_tested": len(strategies),
        "pruned": len(blacklist),
        "active_alpha_strategies": len(strategies) - len(blacklist),
        "blacklist": blacklist
    }

    # Save to Cache
    _save_cache({"blacklist": blacklist, "result": result})
    
    print(f"   ✅ Optimizer Complete: Pruned {len(blacklist)} unprofitable strategies.")
    return result

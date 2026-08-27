"""
Agent 8: The Alpha Optimizer (Dynamic Backtester)
=================================================
Runs a fast historical backtest of all registered strategies.
Temporarily blacklists any strategy with a win rate below 50% in the current market regime.
"""

import pandas as pd
from src.agents.strategies import StrategyRegistry

def prune_strategies(df: pd.DataFrame) -> dict:
    """
    Evaluates all registered strategies on the last 30 days of data.
    Prunes (blacklists) strategies that are failing in the current market conditions.
    """
    print(f"\n⚙️ Agent 8: Running The Alpha Optimizer...")
    
    if len(df) < 40:
        print("   ⚠️ Not enough data to run historical optimizer.")
        return {"scanned": 0, "pruned": 0, "active": len(StrategyRegistry.get_all())}
        
    strategies = StrategyRegistry.get_all()
    print(f"   - Testing {len(strategies)} strategies on historical 30-day window...")
    
    win_counts = {s.name: 0 for s in strategies}
    signal_counts = {s.name: 0 for s in strategies}
    
    # We test on the window from index -30 to -2
    # So we can check the outcome on index+1
    test_range = range(len(df) - 30, len(df) - 1)
    
    for i in test_range:
        # The data visible up to day i
        window_df = df.iloc[:i+1]
        current_price = window_df.iloc[-1]['Close']
        next_price = df.iloc[i+1]['Close']
        
        # Did the market go UP (+1) or DOWN (-1) the next day?
        actual_move = 1 if next_price > current_price else -1
        
        for strategy in strategies:
            # We don't want the strategy checking regime on old data unless we rewrite logic,
            # so we just call generate_signals directly to test the core logic pattern.
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
        if total > 2: # Require at least 3 signals to judge
            win_rate = win_counts[s.name] / total
            if win_rate < 0.50:
                blacklist.append(s.name)
                
    # Update the Registry with the blacklist
    StrategyRegistry.set_blacklist(blacklist)
    
    print(f"   ✅ Optimizer Complete: Pruned {len(blacklist)} unprofitable strategies.")
    
    return {
        "total_tested": len(strategies),
        "pruned": len(blacklist),
        "active_alpha_strategies": len(strategies) - len(blacklist),
        "blacklist": blacklist
    }

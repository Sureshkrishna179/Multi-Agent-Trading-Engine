"""
Indian Market Trading Bot — CLI Runner
======================================
Isolated CLI execution environment for Indian Equities.
By default, screens the entire 50-stock universe in seconds and runs
the full 8-agent committee on the top breakout candidates.

Usage:
    python scripts/run_indian.py              # Screener funnel (Top 5 breakouts)
    python scripts/run_indian.py --top 10     # Top 10 breakouts
    python scripts/run_indian.py --all        # Scan all 50 stocks
"""

import sys
import argparse
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src import config
from src.screener import screen_universe
from src.pipeline import run_pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Indian Market Trading Bot")
    parser.add_argument("--top", type=int, default=5, help="Number of top screened candidates to run (default: 5)")
    parser.add_argument("--all", action="store_true", help="Scan entire 50-stock watchlist sequentially")
    args = parser.parse_args()

    print("\n" + "=" * 65)
    print("📈 INDIAN MARKET TRADING BOT (50-Stock Universe)")
    print("=" * 65)

    if args.all:
        print(f"Scanning all {len(config.INDIAN_WATCHLIST)} stocks sequentially...")
        targets = [{"symbol": s, "df": None, "latest_price": None} for s in config.INDIAN_WATCHLIST]
    else:
        print(f"Running 3-step funnel on {len(config.INDIAN_WATCHLIST)} stocks → Selecting Top {args.top} breakouts...")
        targets = screen_universe("indian", top_n=args.top)

    print(f"\n🧠 Executing 8-Agent Committee on {len(targets)} candidates:")
    for pick in targets:
        symbol = pick["symbol"]
        try:
            print(f"\nEvaluating {symbol}...")
            res = run_pipeline(symbol, "indian", df=pick.get("df"), current_price=pick.get("latest_price"))
            action = res["agent_4_risk_execution"]["risk_validation"]["action"]
            status = "APPROVED" if res["agent_4_risk_execution"]["risk_validation"]["approved"] else "VETOED"
            score = res.get("consensus", {}).get("consensus_score", 0.0)
            print(f"[{symbol}] Consensus: {score:+.2f} | Action: {action} | Risk Guardian: {status}")
        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    print("\n✅ Indian Market Scan Complete.")

"""
Indian Market Trading Bot — CLI Runner
======================================
Isolated CLI execution environment for Indian Equities.
Usage: python scripts/run_indian.py
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src import config
from src.pipeline import run_pipeline

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("📈 INDIAN MARKET TRADING BOT 📈")
    print("=" * 60)

    for symbol in config.INDIAN_WATCHLIST:
        try:
            print(f"\nEvaluating {symbol}...")
            res = run_pipeline(symbol, "indian")
            action = res["agent_4_risk_execution"]["risk_validation"]["action"]
            status = "APPROVED" if res["agent_4_risk_execution"]["risk_validation"]["approved"] else "VETOED"
            print(f"[{symbol}] Action: {action} | Status: {status}")
        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    print("\n✅ Indian Market Scan Complete.")


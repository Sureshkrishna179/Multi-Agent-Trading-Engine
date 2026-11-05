"""
24/7 Autonomous Daemon Runner
=============================
Continuous loop for production cloud deployment.
Runs:
  - Crypto Market: 24/7 continuously every 15 minutes
  - Indian Market: Monday–Friday between 09:15 AM - 03:30 PM IST every 15 minutes
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src import config
from src.pipeline import run_pipeline
from src.agents import risk_executor_agent
from src.connectors.live_ticker import check_volatility


def is_indian_market_open() -> bool:
    """Checks if current time is within NSE trading hours (9:15 AM - 3:30 PM IST, Mon-Fri)."""
    ist = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    if ist.weekday() >= 5:  # Saturday or Sunday
        return False
    start_time = ist.replace(hour=9, minute=15, second=0, microsecond=0)
    end_time = ist.replace(hour=15, minute=30, second=0, microsecond=0)
    return start_time <= ist <= end_time


def run_cycle():
    ist_now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    print(f"\n{'='*70}")
    print(f"⏰ [DAEMON CYCLE] {ist_now.strftime('%Y-%m-%d %I:%M:%S %p IST')}")
    print(f"{'='*70}")

    # 1. ── Crypto Cycle (Always Runs 24/7) ──
    print(f"\n🌐 Scanning Crypto Watchlist ({len(config.CRYPTO_WATCHLIST)} pairs)...")
    for pair in config.CRYPTO_WATCHLIST:
        try:
            res = run_pipeline(pair, "crypto")
            action = res.get("consensus", {}).get("consensus_action", "HOLD")
            score = res.get("consensus", {}).get("consensus_score", 0.0)
            approved = res.get("agent_4_risk_execution", {}).get("risk_validation", {}).get("approved", False)
            status = "✅ EXECUTED" if approved else "🛑 VETOED"
            print(f"   [{pair}] {action} (Score: {score:+.2f}) -> {status}")
        except Exception as e:
            print(f"   ❌ Error on {pair}: {e}")

    # 2. ── Indian Market Cycle (Only during NSE Market Hours) ──
    if is_indian_market_open():
        print(f"\n🇮🇳 Scanning Indian Watchlist ({len(config.INDIAN_WATCHLIST)} stocks)...")
        for stock in config.INDIAN_WATCHLIST:
            try:
                res = run_pipeline(stock, "indian")
                action = res.get("consensus", {}).get("consensus_action", "HOLD")
                score = res.get("consensus", {}).get("consensus_score", 0.0)
                approved = res.get("agent_4_risk_execution", {}).get("risk_validation", {}).get("approved", False)
                status = "✅ EXECUTED" if approved else "🛑 VETOED"
                print(f"   [{stock}] {action} (Score: {score:+.2f}) -> {status}")
            except Exception as e:
                print(f"   ❌ Error on {stock}: {e}")
    else:
        print("\n🇮🇳 Indian Market is currently CLOSED (NSE hours: 9:15 AM - 3:30 PM IST, Mon-Fri). Skipping.")

    print(f"\n💤 Sleeping for 15 minutes until next autonomous cycle...")


if __name__ == "__main__":
    print("🚀 Starting Multi-Agent 24/7 Autonomous Daemon...")
    while True:
        try:
            run_cycle()
        except KeyboardInterrupt:
            print("\n🛑 Daemon stopped by user.")
            break
        except Exception as e:
            print(f"⚠️ Unhandled error in cycle: {e}")
        time.sleep(15 * 60)  # Wait 15 minutes between scans


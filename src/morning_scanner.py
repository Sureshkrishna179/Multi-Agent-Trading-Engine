"""
Morning Pre-Market Scanner
===========================
Autonomous scanner that runs the full 8-agent pipeline across all watchlist
symbols, ranks them by Weighted Consensus Score, and saves a morning report.

Run this script at 8:45 AM IST (Indian Market) or anytime for Crypto (24/7).
Usage: python -m src.morning_scanner
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Ensure project root is on path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src import config
from src.pipeline import run_pipeline

CACHE_DIR = ".cache"
REPORT_FILE = os.path.join(CACHE_DIR, "morning_report.json")


def run_morning_scan() -> dict:
    """
    Scans all watchlist symbols across both markets.
    Returns a ranked report sorted by absolute consensus score (strongest first).
    """
    print("\n" + "=" * 60)
    print("🌅 MORNING PRE-MARKET SCANNER")
    print("=" * 60)
    
    ist_offset = timedelta(hours=5, minutes=30)
    now_ist = datetime.now(timezone.utc) + ist_offset
    print(f"   Scan Time: {now_ist.strftime('%Y-%m-%d %I:%M %p IST')}")
    
    all_results = []
    
    # ── Scan Indian Market ──
    print(f"\n🇮🇳 Scanning {len(config.INDIAN_WATCHLIST)} Indian Stocks...")
    for symbol in config.INDIAN_WATCHLIST:
        try:
            print(f"   → {symbol}...", end=" ")
            res = run_pipeline(symbol, "indian")
            consensus = res.get("consensus", {})
            risk = res.get("agent_4_risk_execution", {}).get("risk_validation", {})
            
            entry = {
                "symbol": symbol,
                "market": "indian",
                "consensus_score": consensus.get("consensus_score", 0),
                "consensus_action": consensus.get("consensus_action", "HOLD"),
                "strength": consensus.get("strength", "WEAK"),
                "confidence": consensus.get("confidence", 0),
                "risk_approved": risk.get("approved", False),
                "ml_action": res.get("agent_7_ml", {}).get("action", "HOLD"),
                "ml_confidence": res.get("agent_7_ml", {}).get("confidence", 0),
                "trend": res.get("agent_1_technical", {}).get("trend", "N/A"),
                "price": res.get("agent_1_technical", {}).get("latest_price", 0),
            }
            all_results.append(entry)
            print(f"✅ {consensus.get('consensus_action', 'HOLD')} ({consensus.get('strength', '')})")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # ── Scan Crypto Market ──
    print(f"\n₿ Scanning {len(config.CRYPTO_WATCHLIST)} Crypto Pairs...")
    for symbol in config.CRYPTO_WATCHLIST:
        try:
            print(f"   → {symbol}...", end=" ")
            res = run_pipeline(symbol, "crypto")
            consensus = res.get("consensus", {})
            risk = res.get("agent_4_risk_execution", {}).get("risk_validation", {})
            
            entry = {
                "symbol": symbol,
                "market": "crypto",
                "consensus_score": consensus.get("consensus_score", 0),
                "consensus_action": consensus.get("consensus_action", "HOLD"),
                "strength": consensus.get("strength", "WEAK"),
                "confidence": consensus.get("confidence", 0),
                "risk_approved": risk.get("approved", False),
                "ml_action": res.get("agent_7_ml", {}).get("action", "HOLD"),
                "ml_confidence": res.get("agent_7_ml", {}).get("confidence", 0),
                "trend": res.get("agent_1_technical", {}).get("trend", "N/A"),
                "price": res.get("agent_1_technical", {}).get("latest_price", 0),
            }
            all_results.append(entry)
            print(f"✅ {consensus.get('consensus_action', 'HOLD')} ({consensus.get('strength', '')})")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # ── Rank by absolute consensus score (strongest signals first) ──
    all_results.sort(key=lambda x: abs(x["consensus_score"]), reverse=True)
    
    # ── Build Report ──
    report = {
        "scan_time": now_ist.strftime("%Y-%m-%d %I:%M %p IST"),
        "timestamp": time.time(),
        "total_scanned": len(all_results),
        "top_picks": all_results[:3],  # Top 3 strongest signals
        "all_results": all_results,
        "summary": {
            "buy_signals": len([r for r in all_results if r["consensus_action"] == "BUY"]),
            "sell_signals": len([r for r in all_results if r["consensus_action"] == "SELL"]),
            "hold_signals": len([r for r in all_results if r["consensus_action"] == "HOLD"]),
        }
    }
    
    # ── Save to Cache ──
    os.makedirs(CACHE_DIR, exist_ok=True)
    try:
        with open(REPORT_FILE, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 Report saved to {REPORT_FILE}")
    except Exception as e:
        print(f"\n⚠️ Could not save report: {e}")
    
    # ── Print Summary ──
    print("\n" + "=" * 60)
    print("🏆 TOP 3 BREAKOUT PICKS")
    print("=" * 60)
    for i, pick in enumerate(report["top_picks"], 1):
        emoji = "🟢" if pick["consensus_action"] == "BUY" else "🔴" if pick["consensus_action"] == "SELL" else "⚪"
        print(f"  #{i} {emoji} {pick['symbol']} → {pick['consensus_action']} "
              f"(Score: {pick['consensus_score']:.2f}, Strength: {pick['strength']})")
    
    print(f"\n📊 Summary: {report['summary']['buy_signals']} BUY | "
          f"{report['summary']['sell_signals']} SELL | "
          f"{report['summary']['hold_signals']} HOLD")
    print("=" * 60)
    
    return report


def load_morning_report() -> dict | None:
    """Load the cached morning report if it exists and is from today."""
    if not os.path.exists(REPORT_FILE):
        return None
    try:
        with open(REPORT_FILE, "r") as f:
            report = json.load(f)
        # Check if report is from today (within last 18 hours)
        if time.time() - report.get("timestamp", 0) < 18 * 3600:
            return report
    except Exception:
        pass
    return None


if __name__ == "__main__":
    run_morning_scan()

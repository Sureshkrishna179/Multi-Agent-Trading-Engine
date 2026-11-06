"""
Morning Pre-Market Scanner
===========================
Autonomous scanner that uses the 3-step funnel screener to scan
all 50 Indian stocks and 50 crypto pairs in seconds, then runs
the full 8-agent pipeline across the top breakout candidates.

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
from src.screener import screen_universe
from src.pipeline import run_pipeline

CACHE_DIR = ".cache"
REPORT_FILE = os.path.join(CACHE_DIR, "morning_report.json")


def run_morning_scan(top_per_market: int = 5) -> dict:
    """
    Funnel Screener + 8-Agent Deep Scan across both markets.
    1. Screen all 50 Indian stocks + 50 Crypto pairs in parallel bulk.
    2. Run full 8-agent committee on top breakout candidates.
    3. Return ranked report sorted by consensus score.
    """
    print("\n" + "=" * 65)
    print("🌅 MORNING PRE-MARKET SCANNER (3-Step Funnel)")
    print("=" * 65)
    
    ist_offset = timedelta(hours=5, minutes=30)
    now_ist = datetime.now(timezone.utc) + ist_offset
    print(f"   Scan Time: {now_ist.strftime('%Y-%m-%d %I:%M %p IST')}")
    
    all_results = []
    
    # ── Step 1 & 2: Screen Indian Market ──
    print(f"\n🇮🇳 Screening {len(config.INDIAN_WATCHLIST)} Indian Stocks...")
    indian_picks = screen_universe("indian", top_n=top_per_market)
    
    print(f"\n🧠 Running 8-Agent Committee on Top {len(indian_picks)} Indian Breakouts...")
    for pick in indian_picks:
        symbol = pick["symbol"]
        try:
            print(f"   → {symbol} (Screen Score: {pick['screen_score']:.2f})...", end=" ")
            res = run_pipeline(symbol, "indian", df=pick.get("df"), current_price=pick.get("latest_price"))
            consensus = res.get("consensus", {})
            risk = res.get("agent_4_risk_execution", {}).get("risk_validation", {})
            
            entry = {
                "symbol": symbol,
                "market": "indian",
                "screen_score": pick.get("screen_score", 0),
                "volume_ratio": pick.get("volume_ratio", 1.0),
                "consensus_score": consensus.get("consensus_score", 0),
                "consensus_action": consensus.get("consensus_action", "HOLD"),
                "strength": consensus.get("strength", "WEAK"),
                "confidence": consensus.get("confidence", 0),
                "risk_approved": risk.get("approved", False),
                "ml_action": res.get("agent_7_ml", {}).get("action", "HOLD"),
                "ml_confidence": res.get("agent_7_ml", {}).get("confidence", 0),
                "trend": res.get("agent_1_technical", {}).get("trend", "N/A"),
                "price": res.get("agent_1_technical", {}).get("latest_price", pick.get("latest_price", 0)),
            }
            all_results.append(entry)
            print(f"✅ {consensus.get('consensus_action', 'HOLD')} ({consensus.get('strength', '')})")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # ── Step 1 & 2: Screen Crypto Market ──
    print(f"\n₿ Screening {len(config.CRYPTO_WATCHLIST)} Crypto Pairs...")
    crypto_picks = screen_universe("crypto", top_n=top_per_market)
    
    print(f"\n🧠 Running 8-Agent Committee on Top {len(crypto_picks)} Crypto Breakouts...")
    for pick in crypto_picks:
        symbol = pick["symbol"]
        try:
            print(f"   → {symbol} (Screen Score: {pick['screen_score']:.2f})...", end=" ")
            res = run_pipeline(symbol, "crypto", df=pick.get("df"), current_price=pick.get("latest_price"))
            consensus = res.get("consensus", {})
            risk = res.get("agent_4_risk_execution", {}).get("risk_validation", {})
            
            entry = {
                "symbol": symbol,
                "market": "crypto",
                "screen_score": pick.get("screen_score", 0),
                "volume_ratio": pick.get("volume_ratio", 1.0),
                "consensus_score": consensus.get("consensus_score", 0),
                "consensus_action": consensus.get("consensus_action", "HOLD"),
                "strength": consensus.get("strength", "WEAK"),
                "confidence": consensus.get("confidence", 0),
                "risk_approved": risk.get("approved", False),
                "ml_action": res.get("agent_7_ml", {}).get("action", "HOLD"),
                "ml_confidence": res.get("agent_7_ml", {}).get("confidence", 0),
                "trend": res.get("agent_1_technical", {}).get("trend", "N/A"),
                "price": res.get("agent_1_technical", {}).get("latest_price", pick.get("latest_price", 0)),
            }
            all_results.append(entry)
            print(f"✅ {consensus.get('consensus_action', 'HOLD')} ({consensus.get('strength', '')})")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # ── Rank by absolute consensus score ──
    all_results.sort(key=lambda x: abs(x["consensus_score"]), reverse=True)
    
    # ── Build Report ──
    report = {
        "scan_time": now_ist.strftime("%Y-%m-%d %I:%M %p IST"),
        "timestamp": time.time(),
        "total_universe_scanned": len(config.INDIAN_WATCHLIST) + len(config.CRYPTO_WATCHLIST),
        "candidates_evaluated": len(all_results),
        "top_picks": all_results[:5],
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
    print("\n" + "=" * 65)
    print("🏆 TOP 5 ALPHA PICKS")
    print("=" * 65)
    for i, pick in enumerate(report["top_picks"], 1):
        emoji = "🟢" if pick["consensus_action"] == "BUY" else "🔴" if pick["consensus_action"] == "SELL" else "⚪"
        print(f"  #{i} {emoji} {pick['symbol']:15s} [{pick['market'].upper()}] → {pick['consensus_action']} "
              f"(Score: {pick['consensus_score']:.2f}, Strength: {pick['strength']})")
    
    print(f"\n📊 Summary: {report['summary']['buy_signals']} BUY | "
          f"{report['summary']['sell_signals']} SELL | "
          f"{report['summary']['hold_signals']} HOLD")
    print("=" * 65)
    
    return report


def load_morning_report() -> dict | None:
    """Load the cached morning report if it exists and is from today."""
    if not os.path.exists(REPORT_FILE):
        return None
    try:
        with open(REPORT_FILE, "r") as f:
            report = json.load(f)
        if time.time() - report.get("timestamp", 0) < 18 * 3600:
            return report
    except Exception:
        pass
    return None


if __name__ == "__main__":
    run_morning_scan()

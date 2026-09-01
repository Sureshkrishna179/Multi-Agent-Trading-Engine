import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
from src.morning_scanner import load_morning_report

st.set_page_config(
    page_title="Multi-Agent Trading Bot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Multi-Agent Trading Bot Dashboard")

st.markdown("""
Welcome to the **Autonomous 8-Agent Trading System** with Weighted Consensus Voting.  
Each agent independently analyzes the market, then all 8 agents **vote** on the final decision.
""")

st.divider()

# ── Morning Report ──
report = load_morning_report()

if report:
    st.subheader("🌅 Morning Pre-Market Report")
    st.caption(f"Last scan: {report['scan_time']}")
    
    summary = report.get("summary", {})
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Scanned", report.get("total_scanned", 0))
    col2.metric("🟢 BUY Signals", summary.get("buy_signals", 0))
    col3.metric("🔴 SELL Signals", summary.get("sell_signals", 0))
    col4.metric("⚪ HOLD Signals", summary.get("hold_signals", 0))
    
    st.markdown("### 🏆 Top 3 Breakout Picks")
    
    top_picks = report.get("top_picks", [])
    if top_picks:
        pick_cols = st.columns(min(len(top_picks), 3))
        for i, pick in enumerate(top_picks[:3]):
            with pick_cols[i]:
                emoji = "🟢" if pick["consensus_action"] == "BUY" else "🔴" if pick["consensus_action"] == "SELL" else "⚪"
                market_flag = "🇮🇳" if pick["market"] == "indian" else "₿"
                st.metric(
                    f"#{i+1} {market_flag} {pick['symbol']}",
                    f"{emoji} {pick['consensus_action']}",
                    f"Score: {pick['consensus_score']:.2f} | {pick['strength']}"
                )
                st.caption(f"Trend: {pick['trend']} | ML: {pick['ml_action']} ({pick['ml_confidence']:.0%})")
    else:
        st.info("No picks available yet.")
    
    st.divider()
else:
    st.info("🌅 No morning report yet. The scanner runs daily before market open, or you can scan manually from the market pages.")
    st.divider()

# ── Navigation ──
st.markdown("""
### Select a market from the sidebar:
- 🇮🇳 **Indian Market** (INR Portfolio, NSE/BSE Watchlist)
- ₿ **Crypto Market** (USD Portfolio, Binance/CCXT)

---

**System Architecture:**  
8-Agent Framework → Weighted Consensus Voting → Risk Guardian Veto  
*Technical · Sentiment · Fundamentals · ML Brain · 150+ Strategies · Bull vs Bear Debate · Alpha Optimizer · Risk Guardian*
""")

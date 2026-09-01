import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import pandas as pd
from src import config
from src.pipeline import run_pipeline
from src.agents import risk_executor_agent

st.set_page_config(page_title="Indian Market Bot", page_icon="🇮🇳", layout="wide")

st.title("🇮🇳 Indian Market Trading Bot")
st.markdown("Isolated environment tracking **INR Capital** and the **NSE/BSE Watchlist**.")

# ── Portfolio Status ──
st.subheader("💼 INR Portfolio")
portfolio = risk_executor_agent.get_portfolio_status("indian")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Available Capital", f"₹{portfolio['available_capital']:,.2f}")
col2.metric("Daily PNL", f"₹{portfolio['daily_pnl']:,.2f}")
col3.metric("Open Positions", portfolio['open_positions'])
col4.metric("Total Trades", portfolio['total_trades'])

st.divider()

# ── Execution Controls ──
st.subheader("⚙️ Run 8-Agent Pipeline with Consensus Voting")

tab1, tab2 = st.tabs(["🔍 Analyze Any Custom Stock", "📋 Scan Entire Watchlist"])

with tab1:
    custom_symbol = st.text_input("Enter NSE/BSE Ticker (e.g. TATAMOTORS.NS, ADANIENT.NS, ZOMATO.NS):", value="TATAMOTORS.NS")
    if st.button("Analyze Stock", type="primary", key="btn_custom"):
        symbols_to_run = [custom_symbol.strip().upper()]
    else:
        symbols_to_run = []

with tab2:
    if st.button("Scan Full Watchlist", type="secondary", key="btn_watchlist"):
        symbols_to_run = config.INDIAN_WATCHLIST
    elif 'symbols_to_run' not in locals():
        symbols_to_run = []

if symbols_to_run:
    with st.spinner("8 Agents are analyzing and voting..."):
        for symbol in symbols_to_run:
            st.markdown(f"### Evaluating `{symbol}`")
            
            try:
                res = run_pipeline(symbol, "indian")
                
                tech = res["agent_1_technical"]
                sent = res["agent_2_sentiment"]
                fund = res["agent_5_fundamental"]
                ml = res["agent_7_ml"]
                opt = res["agent_8_optimizer"]
                strat = res["agent_3_strategy"]
                debate = res["agent_6_debate"]
                risk = res["agent_4_risk_execution"]["risk_validation"]
                consensus = res.get("consensus", {})
                
                # ── Consensus Score (Hero Metric) ──
                score = consensus.get("consensus_score", 0)
                action = consensus.get("consensus_action", "HOLD")
                strength = consensus.get("strength", "WEAK")
                
                score_emoji = "🟢" if action == "BUY" else "🔴" if action == "SELL" else "⚪"
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric(f"{score_emoji} Consensus", action, f"Score: {score:.2f}")
                c2.metric("Strength", strength)
                c3.metric("Trend", tech["trend"])
                
                if risk["approved"]:
                    c4.metric("Risk Guardian", "✅ APPROVED")
                else:
                    c4.metric("Risk Guardian", "🛑 VETOED")
                
                # ── Agent Confidence Breakdown ──
                with st.expander("📊 Agent Confidence Breakdown (How Each Agent Voted)"):
                    votes = consensus.get("agent_votes", {})
                    
                    if votes:
                        vote_data = []
                        for agent_id, vote in votes.items():
                            signal = vote["signal"]
                            weight = vote["weight"]
                            direction = "🟢 BULL" if signal > 0.05 else "🔴 BEAR" if signal < -0.05 else "⚪ NEUTRAL"
                            vote_data.append({
                                "Agent": vote["name"],
                                "Vote": direction,
                                "Signal": f"{signal:+.2f}",
                                "Weight": f"{weight:.0%}",
                                "Weighted": f"{signal * weight:+.3f}",
                                "Details": vote["raw_data"],
                            })
                        
                        df_votes = pd.DataFrame(vote_data)
                        st.dataframe(df_votes, use_container_width=True, hide_index=True)
                    
                    st.caption(f"Final Weighted Consensus: **{score:+.4f}** → **{action}** ({strength})")
                
                # ── ML & Optimizer Quick View ──
                ml_conf = f"{ml.get('confidence', 0):.1%}" if ml.get('action') != 'HOLD' else "N/A"
                st.write(f"🧠 **ML Brain**: {ml.get('action', 'HOLD')} ({ml_conf}) | "
                         f"📊 **Sentiment**: {sent.get('sentiment_score', 50)}/100 | "
                         f"⚙️ **Optimizer**: {opt.get('active_alpha_strategies', 0)} active strategies")
                
                # ── Debate Toggle ──
                with st.expander("⚖️ View Bull vs Bear Debate"):
                    st.write("**🐂 Bull Case:**", debate["bull_case"])
                    st.write("**🐻 Bear Case:**", debate["bear_case"])
                    st.write("**🏛️ Judge Decision:**", debate["judge_decision"])
                    
                # ── Risk Toggle ──
                if not risk["approved"]:
                    st.error("Veto Reasons:\n" + "\n".join([f"- {r}" for r in risk["veto_reasons"]]))
                else:
                    st.success(f"Position Sized: {risk['position_size']} shares. Risking ₹{risk['risk_amount']}.")
                    
            except Exception as e:
                st.error(f"Error processing {symbol}: {e}")
                
            st.divider()
            
    st.success("✅ Indian Watchlist Scan Complete.")

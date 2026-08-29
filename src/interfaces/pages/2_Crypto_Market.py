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

st.set_page_config(page_title="Crypto Market Bot", page_icon="₿", layout="wide")

st.title("₿ Crypto Market Trading Bot")
st.markdown("Isolated environment tracking **USD Capital** and the **Crypto Watchlist**.")

# ── Portfolio Status ──
st.subheader("💼 USD Portfolio")
portfolio = risk_executor_agent.get_portfolio_status("crypto")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Available Capital", f"${portfolio['available_capital']:,.2f}")
col2.metric("Daily PNL", f"${portfolio['daily_pnl']:,.2f}")
col3.metric("Open Positions", portfolio['open_positions'])
col4.metric("Total Trades", portfolio['total_trades'])

st.divider()

# ── Execution Controls ──
st.subheader("⚙️ Run 8-Agent Pipeline")

tab1, tab2 = st.tabs(["🔍 Analyze Any Custom Crypto", "📋 Scan Entire Watchlist"])

with tab1:
    custom_symbol = st.text_input("Enter Crypto Pair (e.g. DOGE/USDT, ADA/USDT, SOL/USDT, PEPE/USDT):", value="SOL/USDT")
    if st.button("Analyze Crypto", type="primary", key="btn_custom_crypto"):
        symbols_to_run = [custom_symbol.strip().upper()]
    else:
        symbols_to_run = []

with tab2:
    if st.button("Scan Full Watchlist", type="secondary", key="btn_watchlist_crypto"):
        symbols_to_run = config.CRYPTO_WATCHLIST
    elif 'symbols_to_run' not in locals():
        symbols_to_run = []

if symbols_to_run:
    with st.spinner("Agents are analyzing market data..."):
        for symbol in symbols_to_run:
            st.markdown(f"### Evaluating `{symbol}`")
            
            try:
                # Run the pipeline safely isolated to "crypto"
                res = run_pipeline(symbol, "crypto")
                
                tech = res["agent_1_technical"]
                sent = res["agent_2_sentiment"]
                fund = res["agent_5_fundamental"]
                ml = res["agent_7_ml"]
                opt = res["agent_8_optimizer"]
                strat = res["agent_3_strategy"]
                debate = res["agent_6_debate"]
                risk = res["agent_4_risk_execution"]["risk_validation"]
                
                # Display Summary
                st.write(f"**Alpha Optimizer**: 🧪 Tested {opt.get('total_tested',0)} | ✂️ Pruned {opt.get('pruned',0)} | ✅ Active Strategies: {opt.get('active_alpha_strategies',0)}")
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Trend", tech["trend"])
                c2.metric("Sentiment", f"{sent['sentiment_score']}/100", sent["sentiment_label"])
                
                ml_conf = f"{ml.get('confidence', 0):.1%}" if ml.get('action') != 'HOLD' else "N/A"
                c3.metric("ML Brain", ml.get('action', 'HOLD'), ml_conf)
                
                if risk["approved"]:
                    c4.metric("Action", risk["action"], "APPROVED", delta_color="normal")
                else:
                    c4.metric("Action", risk["action"], "VETOED", delta_color="inverse")
                
                # Debate Toggle
                with st.expander("⚖️ View Bull vs Bear Debate"):
                    st.write("**🐂 Bull Case:**", debate["bull_case"])
                    st.write("**🐻 Bear Case:**", debate["bear_case"])
                    st.write("**🏛️ Judge Decision:**", debate["judge_decision"])
                    
                # Risk Toggle
                if not risk["approved"]:
                    st.error("Veto Reasons:\n" + "\n".join([f"- {r}" for r in risk["veto_reasons"]]))
                else:
                    st.success(f"Position Sized: {risk['position_size']} units. Risking ${risk['risk_amount']}.")
                    
            except Exception as e:
                st.error(f"Error processing {symbol}: {e}")
                
            st.divider()
            
    st.success("✅ Crypto Watchlist Scan Complete.")

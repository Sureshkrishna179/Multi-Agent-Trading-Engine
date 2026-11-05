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
from src.connectors.live_ticker import check_volatility, get_recent_alerts
from src.interfaces.terminal_ui import (
    inject_css, render_terminal_header, render_portfolio_hero,
    render_signal_banner, render_agent_panel, render_debate,
    render_risk_box, render_vol_alert, render_stock_divider
)

st.set_page_config(page_title="Indian Market Terminal", page_icon="🇮🇳", layout="wide")
inject_css()

render_terminal_header("Indian Market Terminal", "NSE · BSE · 15 Nifty Heavyweights")

# ── Portfolio Hero ──
portfolio = risk_executor_agent.get_portfolio_status("indian")
render_portfolio_hero(
    capital=portfolio["available_capital"],
    pnl=portfolio["daily_pnl"],
    positions=portfolio["open_positions"],
    trades=portfolio["total_trades"],
    currency="₹"
)

# ── Volatility Alerts ──
alerts = get_recent_alerts(max_age_hours=6)
for a in alerts[-2:]:
    render_vol_alert(a.get("message", ""))

# ── Controls ──
tab1, tab2 = st.tabs(["  SCAN SINGLE STOCK  ", "  SCAN FULL WATCHLIST  "])

with tab1:
    col_inp, col_btn = st.columns([4, 1])
    with col_inp:
        custom_symbol = st.text_input(
            "", value="RELIANCE.NS",
            placeholder="e.g. RELIANCE.NS · TCS.NS · ZOMATO.NS",
            label_visibility="collapsed"
        )
    with col_btn:
        run_single = st.button("▶ RUN", type="primary", key="btn_custom", use_container_width=True)
    symbols_to_run = [custom_symbol.strip().upper()] if run_single else []

with tab2:
    st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#6b7280;margin-bottom:8px;">WATCHLIST · {len(config.INDIAN_WATCHLIST)} STOCKS</div>', unsafe_allow_html=True)
    # Show watchlist chips
    chip_html = " ".join([
        f'<span style="display:inline-block;padding:2px 10px;background:#111120;border:1px solid #1e1e2e;border-radius:4px;font-size:11px;color:#9ca3af;font-family:\'JetBrains Mono\',monospace;margin:2px;">{s}</span>'
        for s in config.INDIAN_WATCHLIST
    ])
    st.markdown(chip_html, unsafe_allow_html=True)
    if st.button("▶ SCAN ALL", type="primary", key="btn_watchlist", use_container_width=True):
        symbols_to_run = config.INDIAN_WATCHLIST
    elif "symbols_to_run" not in locals():
        symbols_to_run = []

# ── Pipeline Execution ──
if symbols_to_run:
    with st.spinner(""):
        for symbol in symbols_to_run:
            render_stock_divider(symbol)
            try:
                res = run_pipeline(symbol, "indian")

                tech      = res["agent_1_technical"]
                sent      = res["agent_2_sentiment"]
                debate    = res["agent_6_debate"]
                risk      = res["agent_4_risk_execution"]["risk_validation"]
                consensus = res.get("consensus", {})
                ml_health = res.get("ml_health", {})
                pipeline_time = res.get("pipeline_time_seconds", 0)

                score     = consensus.get("consensus_score", 0)
                action    = consensus.get("consensus_action", "HOLD")
                strength  = consensus.get("strength", "WEAK")
                price     = tech.get("latest_price", 0)

                # Volatility check
                vol_alert = check_volatility(symbol, price, "indian")
                if vol_alert:
                    render_vol_alert(vol_alert["message"])

                # Signal Banner
                render_signal_banner(symbol, action, score, strength, price, "₹", pipeline_time)

                # Two-column layout: agents | debate+risk
                left, right = st.columns([1, 1])

                with left:
                    render_agent_panel(consensus.get("agent_votes", {}), ml_health)

                with right:
                    render_debate(
                        debate.get("bull_case", ""),
                        debate.get("bear_case", ""),
                        debate.get("judge_decision", "")
                    )
                    render_risk_box(risk, "₹")

                # Sentiment & ML quick stats
                sent_score = sent.get("sentiment_score", 50)
                live_src = sent.get("live_sources", "?")
                total_src = sent.get("sources_polled", "?")
                blocked = ", ".join(sent.get("blocked_sources", [])) or "None"
                ml_act = res.get("agent_7_ml", {}).get("action", "HOLD")
                ml_conf = res.get("agent_7_ml", {}).get("confidence", 0)
                opt_active = res.get("agent_8_optimizer", {}).get("active_alpha_strategies", 0)

                st.markdown(f"""
                <div style="display:flex;gap:8px;font-family:'JetBrains Mono',monospace;font-size:11px;color:#4b5563;padding:4px 0 12px 0;flex-wrap:wrap;">
                    <span>📡 SENTIMENT {sent_score}/100 · {live_src}/{total_src} live sources · blocked: {blocked}</span>
                    <span style="color:#1e1e2e;">|</span>
                    <span>🧠 ML {ml_act} {ml_conf:.0%}</span>
                    <span style="color:#1e1e2e;">|</span>
                    <span>⚙️ {opt_active} active strategies</span>
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.markdown(f'<div style="color:#ef4444;font-family:\'JetBrains Mono\',monospace;font-size:12px;padding:8px 0;">✗ Error: {e}</div>', unsafe_allow_html=True)

    st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#22c55e;text-align:center;padding:16px;">✓ SCAN COMPLETE · {len(symbols_to_run)} STOCKS ANALYZED</div>', unsafe_allow_html=True)

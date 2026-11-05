"""
Terminal UI Helper — Dark Trading Terminal Theme
================================================
Shared CSS + rendering functions used by both Indian and Crypto market pages.
Inspired by the dark-terminal aesthetic of viral trading bots on X/Twitter.
"""

import streamlit as st


# ── Global Terminal CSS ──────────────────────────────────────────────────────

TERMINAL_CSS = """
<style>
/* ── Global Dark Terminal ── */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    background-color: #0a0a0f !important;
    color: #e2e8f0 !important;
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 2rem !important; max-width: 100% !important; }

/* ── Custom Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2d2d3f; border-radius: 2px; }

/* ── Terminal Header ── */
.terminal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0 6px 0;
    border-bottom: 1px solid #1e1e2e;
    margin-bottom: 16px;
}
.terminal-logo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 600;
    color: #7c3aed;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.terminal-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #22c55e;
}
.terminal-status::before { content: "● "; }

/* ── Portfolio Hero Card ── */
.pnl-hero {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a0f2e 100%);
    border: 1px solid #2d1f52;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.pnl-amount {
    font-family: 'JetBrains Mono', monospace;
    font-size: 36px;
    font-weight: 700;
    color: #fff;
    line-height: 1;
}
.pnl-amount.positive { color: #22c55e; }
.pnl-amount.negative { color: #ef4444; }
.pnl-label {
    font-size: 11px;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
    font-family: 'JetBrains Mono', monospace;
}
.pnl-sub {
    font-size: 12px;
    color: #9ca3af;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 4px;
}

/* ── Stat Pills ── */
.stat-row {
    display: flex;
    gap: 10px;
    margin-bottom: 16px;
    flex-wrap: wrap;
}
.stat-pill {
    background: #111120;
    border: 1px solid #1e1e2e;
    border-radius: 8px;
    padding: 10px 16px;
    min-width: 120px;
    flex: 1;
}
.stat-pill-label {
    font-size: 10px;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'JetBrains Mono', monospace;
}
.stat-pill-value {
    font-size: 18px;
    font-weight: 600;
    color: #e2e8f0;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 2px;
}

/* ── Signal Banner ── */
.signal-banner {
    border-radius: 10px;
    padding: 16px 20px;
    margin: 12px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border: 1px solid;
}
.signal-banner.buy {
    background: linear-gradient(135deg, #052e16 0%, #064e1e 100%);
    border-color: #16a34a;
}
.signal-banner.sell {
    background: linear-gradient(135deg, #2d0a0a 0%, #450d0d 100%);
    border-color: #dc2626;
}
.signal-banner.hold {
    background: linear-gradient(135deg, #111120 0%, #1a1a30 100%);
    border-color: #374151;
}
.signal-action {
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    letter-spacing: 3px;
}
.signal-action.buy { color: #22c55e; }
.signal-action.sell { color: #ef4444; }
.signal-action.hold { color: #9ca3af; }
.signal-score {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #6b7280;
    margin-top: 4px;
}
.signal-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 1px;
}
.signal-badge.buy { background: #16a34a22; color: #22c55e; border: 1px solid #16a34a; }
.signal-badge.sell { background: #dc262622; color: #ef4444; border: 1px solid #dc2626; }
.signal-badge.hold { background: #37415122; color: #9ca3af; border: 1px solid #374151; }

/* ── Agent Panel ── */
.agent-panel {
    background: #0d0d1a;
    border: 1px solid #1e1e2e;
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 16px;
}
.agent-panel-header {
    padding: 10px 16px;
    background: #111120;
    border-bottom: 1px solid #1e1e2e;
    font-size: 11px;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-family: 'JetBrains Mono', monospace;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.agent-row {
    display: flex;
    align-items: center;
    padding: 10px 16px;
    border-bottom: 1px solid #12121e;
    gap: 12px;
    font-family: 'JetBrains Mono', monospace;
}
.agent-row:last-child { border-bottom: none; }
.agent-row:hover { background: #111120; }
.agent-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.agent-dot.bull { background: #22c55e; box-shadow: 0 0 6px #22c55e88; }
.agent-dot.bear { background: #ef4444; box-shadow: 0 0 6px #ef444488; }
.agent-dot.neutral { background: #6b7280; }
.agent-dot.abstain { background: #374151; }
.agent-name {
    font-size: 12px;
    color: #c4c4d4;
    min-width: 150px;
    flex-shrink: 0;
}
.agent-vote {
    font-size: 11px;
    font-weight: 600;
    min-width: 70px;
}
.agent-vote.bull { color: #22c55e; }
.agent-vote.bear { color: #ef4444; }
.agent-vote.neutral { color: #6b7280; }
.agent-weight {
    font-size: 10px;
    color: #374151;
    margin-left: auto;
    padding: 2px 8px;
    background: #111120;
    border-radius: 4px;
}
.agent-detail {
    font-size: 10px;
    color: #4b5563;
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ── Debate Panel ── */
.debate-panel {
    background: #0d0d1a;
    border: 1px solid #1e1e2e;
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 16px;
}
.debate-bull {
    padding: 14px 16px;
    border-left: 3px solid #22c55e;
    background: #0a1f0e;
    margin: 0;
    font-size: 13px;
    color: #d1fae5;
    line-height: 1.6;
}
.debate-bear {
    padding: 14px 16px;
    border-left: 3px solid #ef4444;
    background: #1f0a0a;
    margin: 0;
    font-size: 13px;
    color: #fee2e2;
    line-height: 1.6;
}
.debate-judge {
    padding: 14px 16px;
    border-left: 3px solid #7c3aed;
    background: #120f1a;
    margin: 0;
    font-size: 13px;
    color: #ede9fe;
    line-height: 1.6;
}
.debate-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 6px;
    font-weight: 600;
}

/* ── Risk Box ── */
.risk-box {
    border-radius: 8px;
    padding: 14px 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    margin-bottom: 16px;
    border: 1px solid;
}
.risk-box.approved {
    background: #052e1622;
    border-color: #16a34a44;
    color: #86efac;
}
.risk-box.vetoed {
    background: #2d0a0a22;
    border-color: #dc262644;
    color: #fca5a5;
}

/* ── Volatility Alert ── */
.vol-alert {
    background: #2d1a0022;
    border: 1px solid #d9770644;
    border-radius: 8px;
    padding: 10px 16px;
    color: #fdba74;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 12px;
}

/* ── Stock Card Header ── */
.stock-header {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 20px 0 8px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.stock-header::after {
    content: "";
    flex: 1;
    height: 1px;
    background: #1e1e2e;
}

/* ── Speed Tag ── */
.speed-tag {
    display: inline-block;
    padding: 2px 10px;
    background: #111120;
    border: 1px solid #1e1e2e;
    border-radius: 4px;
    font-size: 10px;
    color: #7c3aed;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Input & Button overrides ── */
.stTextInput input {
    background: #111120 !important;
    border: 1px solid #2d2d3f !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
}
.stButton button {
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    font-size: 11px !important;
}
div[data-testid="stTab"] button {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    color: #6b7280 !important;
}
div[data-testid="stTab"] button[aria-selected="true"] {
    color: #7c3aed !important;
    border-bottom-color: #7c3aed !important;
}

/* ── Metric overrides ── */
div[data-testid="stMetric"] {
    background: #111120;
    border: 1px solid #1e1e2e;
    border-radius: 8px;
    padding: 12px 16px;
}
div[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 20px !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 10px !important;
    color: #6b7280 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

/* ── Expander overrides ── */
details {
    background: #0d0d1a !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 8px !important;
}
summary {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    color: #9ca3af !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    padding: 10px 14px !important;
}
</style>
"""


def inject_css():
    st.markdown(TERMINAL_CSS, unsafe_allow_html=True)


def render_terminal_header(title: str, subtitle: str, market: str = "PAPER"):
    st.markdown(f"""
    <div class="terminal-header">
        <div>
            <div class="terminal-logo">⬡ {title}</div>
            <div style="font-size:11px;color:#4b5563;font-family:'JetBrains Mono',monospace;margin-top:2px;">{subtitle}</div>
        </div>
        <div class="terminal-status">{market} · 8-AGENT DAG</div>
    </div>
    """, unsafe_allow_html=True)


def render_portfolio_hero(capital: float, pnl: float, positions: int, trades: int, currency: str = "₹"):
    pnl_class = "positive" if pnl >= 0 else "negative"
    pnl_sign = "+" if pnl >= 0 else ""
    st.markdown(f"""
    <div class="pnl-hero">
        <div>
            <div class="pnl-label">Available Capital</div>
            <div class="pnl-amount">{currency}{capital:,.0f}</div>
            <div class="pnl-sub">Paper Trading Mode</div>
        </div>
        <div style="text-align:center;">
            <div class="pnl-label">Daily PnL</div>
            <div class="pnl-amount {pnl_class}">{pnl_sign}{currency}{pnl:,.2f}</div>
            <div class="pnl-sub">{pnl_sign}{(pnl/max(capital,1)*100):.2f}% today</div>
        </div>
        <div style="text-align:right;">
            <div class="stat-pill" style="text-align:right;">
                <div class="pnl-label">Open Positions</div>
                <div class="pnl-amount" style="font-size:24px;">{positions}</div>
            </div>
            <div style="margin-top:8px;">
                <div class="pnl-label">Total Trades</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:600;color:#e2e8f0;">{trades}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_signal_banner(symbol: str, action: str, score: float, strength: str, price: float, currency: str = "₹", pipeline_time: float = 0):
    css_class = action.lower() if action in ("BUY", "SELL") else "hold"
    price_str = f"{currency}{price:,.2f}" if price > 0 else "N/A"
    st.markdown(f"""
    <div class="signal-banner {css_class}">
        <div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:2px;margin-bottom:4px;">
                {symbol}  ·  {price_str}
            </div>
            <div class="signal-action {css_class}">{action}</div>
            <div class="signal-score">Score {score:+.4f}  ·  Strength: {strength}</div>
        </div>
        <div style="text-align:right;">
            <div class="signal-badge {css_class}">{strength}</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#374151;margin-top:8px;">⚡ {pipeline_time}s</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_agent_panel(agent_votes: dict, ml_health: dict):
    agent_icons = {
        "agent_1_technical":  ("01", "Technical Observer"),
        "agent_2_sentiment":  ("02", "Sentiment Analyst"),
        "agent_3_strategy":   ("03", "Strategy Engine"),
        "agent_5_fundamental":("05", "Fundamental Analyst"),
        "agent_6_debate":     ("06", "Bull vs Bear Judge"),
        "agent_7_ml":         ("07", "ML Brain (XGBoost)"),
        "agent_8_optimizer":  ("08", "Alpha Optimizer"),
    }

    rows_html = ""
    for agent_id, vote in agent_votes.items():
        signal = vote.get("signal", 0)
        weight = vote.get("weight", 0)
        raw = vote.get("raw_data", "")
        name = vote.get("name", agent_id)

        if weight == 0:
            dot_class, vote_class, vote_label = "abstain", "neutral", "ABSTAIN"
        elif signal > 0.05:
            dot_class, vote_class, vote_label = "bull", "bull", "▲ BULL"
        elif signal < -0.05:
            dot_class, vote_class, vote_label = "bear", "bear", "▼ BEAR"
        else:
            dot_class, vote_class, vote_label = "neutral", "neutral", "— HOLD"

        weight_str = f"{weight:.0%}" if weight > 0 else "0% (ABSTAIN)"

        rows_html += f"""
        <div class="agent-row">
            <div class="agent-dot {dot_class}"></div>
            <div class="agent-name">{name}</div>
            <div class="agent-vote {vote_class}">{vote_label}</div>
            <div class="agent-detail">{raw[:55]}{'…' if len(raw) > 55 else ''}</div>
            <div class="agent-weight">{weight_str}</div>
        </div>"""

    ml_status = ml_health.get("status", "N/A")
    acc = ml_health.get("accuracy_pct", "—")
    st.markdown(f"""
    <div class="agent-panel">
        <div class="agent-panel-header">
            <span>Agent Voting Panel</span>
            <span style="color:#22c55e;">ML: {ml_status} · {acc}</span>
        </div>
        {rows_html}
    </div>
    """, unsafe_allow_html=True)


def render_debate(bull: str, bear: str, judge: str):
    st.markdown(f"""
    <div class="debate-panel">
        <div class="agent-panel-header"><span>⚖️ Bull vs Bear Trading Desk</span></div>
        <div class="debate-bull">
            <div class="debate-label" style="color:#22c55e;">🐂 Bull Trader</div>
            {bull or "No debate generated."}
        </div>
        <div class="debate-bear">
            <div class="debate-label" style="color:#ef4444;">🐻 Bear Trader</div>
            {bear or "No debate generated."}
        </div>
        <div class="debate-judge">
            <div class="debate-label" style="color:#a78bfa;">🏛️ Desk Manager — Final Call</div>
            {judge or "No decision."}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_risk_box(risk: dict, currency: str = "₹"):
    if risk.get("approved"):
        pos = risk.get("position_size", "N/A")
        amt = risk.get("risk_amount", 0)
        sl = risk.get("stop_loss", 0)
        tp = risk.get("take_profit", 0)
        st.markdown(f"""
        <div class="risk-box approved">
            ✅ RISK GUARDIAN — APPROVED<br>
            Position: <strong>{pos} units</strong> · Risk: <strong>{currency}{amt:.2f}</strong>
            · SL: <strong>{currency}{sl:.2f}</strong> · TP: <strong>{currency}{tp:.2f}</strong>
        </div>
        """, unsafe_allow_html=True)
    else:
        reasons = " · ".join(risk.get("veto_reasons", ["Unknown"]))
        st.markdown(f"""
        <div class="risk-box vetoed">
            🛑 RISK GUARDIAN — VETOED<br>
            {reasons}
        </div>
        """, unsafe_allow_html=True)


def render_vol_alert(msg: str):
    st.markdown(f'<div class="vol-alert">⚡ {msg}</div>', unsafe_allow_html=True)


def render_stock_divider(symbol: str):
    st.markdown(f'<div class="stock-header">{symbol}</div>', unsafe_allow_html=True)


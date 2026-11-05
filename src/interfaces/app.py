import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
from src.morning_scanner import load_morning_report
from src.interfaces.terminal_ui import inject_css, TERMINAL_CSS

st.set_page_config(
    page_title="Multi-Agent Trading Terminal",
    page_icon="⬡",
    layout="wide"
)
inject_css()

# ── Terminal Header ──
st.markdown("""
<div style="text-align:center;padding:40px 0 20px 0;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#7c3aed;letter-spacing:4px;text-transform:uppercase;margin-bottom:12px;">⬡ Multi-Agent Trading Terminal</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:36px;font-weight:700;color:#fff;line-height:1.1;">8-Agent Autonomous<br>Trading System</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#4b5563;margin-top:12px;letter-spacing:1px;">TECHNICAL · SENTIMENT · ML BRAIN · STRATEGY · FUNDAMENTAL · DEBATE · OPTIMIZER · RISK</div>
    <div style="display:inline-block;margin-top:16px;padding:4px 16px;background:#111120;border:1px solid #22c55e44;border-radius:4px;font-family:'JetBrains Mono',monospace;font-size:11px;color:#22c55e;">● PAPER TRADING · LIVE ON STREAMLIT CLOUD</div>
</div>
""", unsafe_allow_html=True)

# ── Agent Architecture Grid ──
st.markdown("""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:20px 0;">
    <div style="background:#0d0d1a;border:1px solid #1e1e2e;border-radius:10px;padding:16px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#7c3aed;letter-spacing:2px;">AGENT 01</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:600;color:#e2e8f0;margin:4px 0;">Technical</div>
        <div style="font-size:11px;color:#4b5563;">RSI · MACD · Bollinger · ATR · ADX · SMA 20/50/200</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#374151;margin-top:8px;">WEIGHT: 20%</div>
    </div>
    <div style="background:#0d0d1a;border:1px solid #1e1e2e;border-radius:10px;padding:16px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#7c3aed;letter-spacing:2px;">AGENT 02</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:600;color:#e2e8f0;margin:4px 0;">Sentiment</div>
        <div style="font-size:11px;color:#4b5563;">Moneycontrol · ET RSS · Reddit · Twitter · Fear/Greed</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#374151;margin-top:8px;">WEIGHT: 10%</div>
    </div>
    <div style="background:#0d0d1a;border:1px solid #1e1e2e;border-radius:10px;padding:16px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#7c3aed;letter-spacing:2px;">AGENT 03</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:600;color:#e2e8f0;margin:4px 0;">Strategy Engine</div>
        <div style="font-size:11px;color:#4b5563;">111 strategies · Candlestick · Trend · Momentum · Volume</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#374151;margin-top:8px;">WEIGHT: 15%</div>
    </div>
    <div style="background:#0d0d1a;border:1px solid #1e1e2e;border-radius:10px;padding:16px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#ef4444;letter-spacing:2px;">AGENT 04</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:600;color:#e2e8f0;margin:4px 0;">Risk Guardian</div>
        <div style="font-size:11px;color:#4b5563;">2% max risk · Kelly sizing · 1:2 R:R · VETO power</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#ef4444;margin-top:8px;">VETO ONLY</div>
    </div>
    <div style="background:#0d0d1a;border:1px solid #1e1e2e;border-radius:10px;padding:16px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#7c3aed;letter-spacing:2px;">AGENT 05</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:600;color:#e2e8f0;margin:4px 0;">Fundamental</div>
        <div style="font-size:11px;color:#4b5563;">P/E · D/E · Revenue growth · EPS · NSE only</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#374151;margin-top:8px;">WEIGHT: 10% (abstains on crypto)</div>
    </div>
    <div style="background:#0d0d1a;border:1px solid #1e1e2e;border-radius:10px;padding:16px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#7c3aed;letter-spacing:2px;">AGENT 06</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:600;color:#e2e8f0;margin:4px 0;">Bull/Bear Debate</div>
        <div style="font-size:11px;color:#4b5563;">Gemini 3.6 Flash · Wall Street desk persona</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#374151;margin-top:8px;">WEIGHT: 10%</div>
    </div>
    <div style="background:#0d0d1a;border:1px solid #1e1e2e;border-radius:10px;padding:16px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#7c3aed;letter-spacing:2px;">AGENT 07</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:600;color:#e2e8f0;margin:4px 0;">ML Brain</div>
        <div style="font-size:11px;color:#4b5563;">XGBoost · OHLCV features · Drift monitoring · Auto weight</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#374151;margin-top:8px;">WEIGHT: 25%</div>
    </div>
    <div style="background:#0d0d1a;border:1px solid #1e1e2e;border-radius:10px;padding:16px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#7c3aed;letter-spacing:2px;">AGENT 08</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:600;color:#e2e8f0;margin:4px 0;">Alpha Optimizer</div>
        <div style="font-size:11px;color:#4b5563;">30-day backtest · Prunes losers · 24h cache</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#374151;margin-top:8px;">WEIGHT: 10%</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Morning Report ──
report = load_morning_report()
if report:
    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#6b7280;text-transform:uppercase;letter-spacing:2px;margin:20px 0 10px 0;">🌅 Pre-Market Morning Report</div>
    """, unsafe_allow_html=True)
    summary = report.get("summary", {})
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Scanned", report.get("total_scanned", 0))
    c2.metric("🟢 BUY Signals", summary.get("buy_signals", 0))
    c3.metric("🔴 SELL Signals", summary.get("sell_signals", 0))
    c4.metric("⚪ HOLD Signals", summary.get("hold_signals", 0))

# ── CTA ──
st.markdown("""
<div style="text-align:center;margin-top:30px;padding:20px;background:#0d0d1a;border:1px solid #1e1e2e;border-radius:12px;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#6b7280;margin-bottom:8px;">SELECT A MARKET FROM THE SIDEBAR TO BEGIN</div>
    <div style="font-size:11px;color:#374151;font-family:'JetBrains Mono',monospace;">🇮🇳 Indian Market  ·  ₿ Crypto Market</div>
</div>
""", unsafe_allow_html=True)

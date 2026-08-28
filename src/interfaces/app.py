import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st

st.set_page_config(
    page_title="Multi-Agent Trading Bot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Multi-Agent Trading Bot Dashboard")

st.markdown("""
Welcome to the Dual-Interface System. 
To ensure 100% isolation of your funds and strategies, the Indian Market and Crypto Market have been completely separated.

### Please select a market from the sidebar:
- 🇮🇳 **Indian Market** (INR Portfolio, NSE/BSE Watchlist, Dhan/AngelOne APIs)
- ₿ **Crypto Market** (USD Portfolio, Binance/Delta APIs)

---
*System Architecture: 6-Agent Framework with Multi-Source Sentiment (News, Reddit, Twitter, CoinGecko).*
""")

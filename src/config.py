"""
Global Configuration — Multi-Agent Trading Bot
================================================
Centralized settings for risk parameters, capital allocation,
indicator periods, strategy thresholds, and API credentials.
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ── Execution Mode ──────────────────────────────────────────────
EXECUTION_MODE = os.getenv("EXECUTION_MODE", "PAPER")  # "PAPER" or "LIVE"


# ── Capital & Risk Parameters ───────────────────────────────────
DEFAULT_CAPITAL_INR = float(os.getenv("DEFAULT_CAPITAL_INR", 100_000))   # ₹1,00,000
DEFAULT_CAPITAL_USD = float(os.getenv("DEFAULT_CAPITAL_USD", 10_000))    # $10,000
MAX_RISK_PER_TRADE  = float(os.getenv("MAX_RISK_PER_TRADE", 0.02))      # 2% max risk
MIN_RISK_REWARD     = 2.0   # Minimum Risk-to-Reward ratio (1:2)
MAX_DAILY_DRAWDOWN  = 0.06  # 6% max daily drawdown — halt all trading


# ── Technical Indicator Periods (Agent 1) ───────────────────────
RSI_PERIOD       = 14
SMA_SHORT        = 20
SMA_MEDIUM       = 50
SMA_LONG         = 200
ATR_PERIOD       = 14
MACD_FAST        = 12
MACD_SLOW        = 26
MACD_SIGNAL      = 9
BOLLINGER_PERIOD = 20
BOLLINGER_STD    = 2


# ── Sentiment Thresholds (Agent 2) ──────────────────────────────
SENTIMENT_BULLISH_THRESHOLD = 60   # Score > 60 → Bullish
SENTIMENT_BEARISH_THRESHOLD = 40   # Score < 40 → Bearish
# Score 40–60 → Neutral

# Sentiment Source Weights (Total = 1.0)
SENTIMENT_WEIGHTS = {
    "news": 0.30,
    "reddit": 0.20,
    "twitter": 0.15,
    "stocktwits": 0.10,
    "tradingview": 0.10,
    "fear_greed": 0.10,
    "community": 0.05
}

# ── Fundamental Analysis Thresholds (Agent 5) ───────────────────
FUNDAMENTAL_PE_MAX = 30.0          # Max acceptable P/E ratio
FUNDAMENTAL_DEBT_EQUITY_MAX = 1.5  # Max acceptable D/E ratio
FUNDAMENTAL_REVENUE_GROWTH_MIN = 0.05 # Minimum 5% YoY revenue growth


# ── Strategy Playbook Thresholds (Agent 3) ──────────────────────
MOMENTUM_RSI_CEILING = 70    # RSI must be < 70 for momentum entry
REVERSION_RSI_FLOOR  = 30    # RSI must be < 30 for mean reversion entry
DEFAULT_SL_PERCENT   = 0.05  # 5% stop-loss from entry (fallback)
DEFAULT_TP_PERCENT   = 0.10  # 10% take-profit from entry (1:2 R:R)


# ── Screener Settings ──────────────────────────────────────────
SCREENER_TOP_N = 5             # Number of top picks to send to the full 8-agent pipeline
SCREENER_MIN_VOLUME_RATIO = 1.2  # Volume must be 1.2x the 20-day average to qualify
SCREENER_MIN_MOVE_PCT = 0.5    # Minimum absolute % move today to qualify


# ── API Keys ────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Angel One SmartAPI
ANGEL_API_KEY     = os.getenv("ANGEL_API_KEY", "")
ANGEL_CLIENT_ID   = os.getenv("ANGEL_CLIENT_ID", "")
ANGEL_PASSWORD    = os.getenv("ANGEL_PASSWORD", "")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET", "")

# Dhan HQ
DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN", "")
DHAN_CLIENT_ID    = os.getenv("DHAN_CLIENT_ID", "")

# Binance
BINANCE_API_KEY    = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")

# Delta Exchange India
DELTA_API_KEY    = os.getenv("DELTA_API_KEY", "")
DELTA_API_SECRET = os.getenv("DELTA_API_SECRET", "")

# Reddit API
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "TradingBot/1.0")

# Twitter API
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")


# ── Default Watchlists (50 Indian Stocks + 50 Crypto Coins) ────
INDIAN_WATCHLIST = [
    # ── Nifty 50 Core ──
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "INFY.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "BHARTIARTL.NS",
    "ITC.NS",
    "LT.NS",
    "KOTAKBANK.NS",
    "AXISBANK.NS",
    "MARUTI.NS",
    "HINDUNILVR.NS",
    "ASIANPAINT.NS",
    "BAJFINANCE.NS",
    # ── Large Cap Diversified ──
    "TATAMOTORS.NS",
    "SUNPHARMA.NS",
    "TITAN.NS",
    "ULTRACEMCO.NS",
    "WIPRO.NS",
    "HCLTECH.NS",
    "NTPC.NS",
    "POWERGRID.NS",
    "ONGC.NS",
    "COALINDIA.NS",
    # ── Banking & Financial ──
    "BAJAJFINSV.NS",
    "INDUSINDBK.NS",
    "BANKBARODA.NS",
    "PNB.NS",
    "SBILIFE.NS",
    # ── Auto & Industrial ──
    "TATASTEEL.NS",
    "JSWSTEEL.NS",
    "HINDALCO.NS",
    "M&M.NS",
    "HEROMOTOCO.NS",
    # ── IT & Tech ──
    "TECHM.NS",
    "LTIM.NS",
    "PERSISTENT.NS",
    "COFORGE.NS",
    "MPHASIS.NS",
    # ── Pharma & Healthcare ──
    "DRREDDY.NS",
    "CIPLA.NS",
    "DIVISLAB.NS",
    "APOLLOHOSP.NS",
    "MAXHEALTH.NS",
    # ── FMCG & Consumer ──
    "NESTLEIND.NS",
    "BRITANNIA.NS",
    "DABUR.NS",
    "GODREJCP.NS",
    "TATACONSUM.NS",
]

CRYPTO_WATCHLIST = [
    # ── Top 10 by Market Cap ──
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "XRP/USDT",
    "BNB/USDT",
    "ADA/USDT",
    "AVAX/USDT",
    "DOGE/USDT",
    "LINK/USDT",
    "DOT/USDT",
    # ── Layer 1 Blockchains ──
    "MATIC/USDT",
    "NEAR/USDT",
    "ATOM/USDT",
    "SUI/USDT",
    "APT/USDT",
    "SEI/USDT",
    "TIA/USDT",
    "INJ/USDT",
    "FTM/USDT",
    "ALGO/USDT",
    # ── DeFi ──
    "UNI/USDT",
    "AAVE/USDT",
    "MKR/USDT",
    "CRV/USDT",
    "SUSHI/USDT",
    "COMP/USDT",
    "SNX/USDT",
    "DYDX/USDT",
    "1INCH/USDT",
    "LDO/USDT",
    # ── AI & Compute ──
    "FET/USDT",
    "RENDER/USDT",
    "TAO/USDT",
    "ARKM/USDT",
    "AKT/USDT",
    # ── Gaming & Metaverse ──
    "IMX/USDT",
    "GALA/USDT",
    "AXS/USDT",
    "SAND/USDT",
    "MANA/USDT",
    # ── Meme Coins ──
    "SHIB/USDT",
    "PEPE/USDT",
    "WIF/USDT",
    "BONK/USDT",
    "FLOKI/USDT",
    # ── Infrastructure & Oracles ──
    "FIL/USDT",
    "AR/USDT",
    "GRT/USDT",
    "PYTH/USDT",
    "TRX/USDT",
]


# ── News Sources for Sentiment (Agent 2) ───────────────────────
NEWS_RSS_FEEDS = {
    "moneycontrol": "https://www.moneycontrol.com/rss/latestnews.xml",
    "economic_times_markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "livemint_markets": "https://www.livemint.com/rss/markets",
    "cryptopanic": "https://cryptopanic.com/news/rss/",
}

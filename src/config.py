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


# ── Default Watchlists ─────────────────────────────────────────
INDIAN_WATCHLIST = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "INFY.NS",
    "TATASTEEL.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "BHARTIARTL.NS",
    "ITC.NS",
    "WIPRO.NS",
]

CRYPTO_WATCHLIST = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "XRP/USDT",
    "BNB/USDT",
]


# ── News Sources for Sentiment (Agent 2) ───────────────────────
NEWS_RSS_FEEDS = {
    "moneycontrol": "https://www.moneycontrol.com/rss/latestnews.xml",
    "economic_times_markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "livemint_markets": "https://www.livemint.com/rss/markets",
    "cryptopanic": "https://cryptopanic.com/news/rss/",
}

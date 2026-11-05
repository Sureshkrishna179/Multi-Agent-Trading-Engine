# ⬡ Multi-Agent Autonomous Quantitative Trading Engine

An institutional-grade algorithmic trading platform for **Indian Equities (NSE/BSE)** and **Global Cryptocurrency Markets**, powered by an asynchronous **8-Agent Directed Acyclic Graph (DAG)**, Machine Learning (**XGBoost**), and Generative AI (**Google Gemini 3.6 Flash**).

---

## 🏛️ System Architecture

The engine runs a high-throughput parallel DAG pipeline completing full evaluations in **under 3 seconds**:

```
                 ┌─ Agent 01: Technical Analysis (RSI, MACD, Bollinger, ATR) ─┐
                 ├─ Agent 02: Multi-Source Sentiment (RSS, Reddit, Fear/Greed)─┤
  Data Ingestion─┼─ Agent 05: Fundamental Analysis (P/E, D/E, Revenue Growth) ─┼─> Agent 03 (111 Strategies) ─> Agent 06 (Bull/Bear Debate) ─> Consensus ─> Agent 04 (Risk Guardian VETO)
                 ├─ Agent 07: ML Brain (XGBoost Classifier + MLOps Health) ────┤
                 └─ Agent 08: Alpha Strategy Optimizer (30D Backtest Cache) ───┘
                                       PARALLEL DAG LAYER                                             SEQUENTIAL LAYER
```

### The 8 Autonomous Agents

1. **Agent 01 (Technical Observer)**: Computes RSI (14), MACD, Bollinger Bands, ATR (14), ADX, and SMA (20/50/200). Weight: **20%**
2. **Agent 02 (Sentiment Engine)**: Real-time RSS feeds (Moneycontrol, Livemint, Economic Times, CryptoPanic), Reddit, Twitter, and Fear & Greed Index. Weight: **10%**
3. **Agent 03 (Strategy Selector)**: 111 quantitative strategies across 8 categories (Candlestick, Trend, Momentum, Volatility, Volume, Chart Patterns, Mean Reversion, Sentiment-Hybrid). Weight: **15%**
4. **Agent 04 (Risk Guardian)**: **Absolute Gatekeeper with VETO power.** Enforces 2% risk limit, Kelly sizing, 1:2 R:R ratio, 6% daily drawdown halt, and dynamic ATR Stop-Loss. Weight: **VETO ONLY**
5. **Agent 05 (Fundamental Analyst)**: Evaluates P/E ratios, Debt-to-Equity, and YoY revenue growth. Explicitly abstains on crypto tickers. Weight: **10%**
6. **Agent 06 (Bull vs Bear Debate)**: Powered by **Google Gemini 3.6 Flash** adopting an aggressive Wall Street desk trader persona. Weight: **10%**
7. **Agent 07 (ML Brain)**: Supervised XGBoost classifier predicting next-bar directional movement with real-time drift detection. Weight: **25%**
8. **Agent 08 (Alpha Optimizer)**: 30-day historical backtesting of all strategies with dynamic pruning of unprofitable rules and a 24-hour cache. Weight: **10%**

---

## 📁 Repository Directory Structure

```
├── daemon.py              # 24/7 background autonomous scanner (Crypto 24/7 + NSE Market Hours)
├── Dockerfile             # Multi-stage container deployment for cloud hosting
├── docker-compose.yml     # Orchestrates Terminal (Port 8000) & Daemon services
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
│
├── frontend/              # Modern Dark Trading Terminal (React + Tailwind CSS + TradingView)
│   ├── src/
│   │   ├── components/    # HeroHUD, TradingChart, AgentPanel, DebateChamber, RiskCard, etc.
│   │   ├── App.jsx        # Main Terminal application
│   │   └── main.jsx
│   ├── dist/              # Precompiled high-speed production assets
│   ├── vite.config.js
│   └── package.json
│
├── src/
│   ├── api_server.py      # High-performance FastAPI server + WebSocket event stream (Port 8000)
│   ├── config.py          # Centralized risk parameters, indicators, and watchlists
│   ├── pipeline.py        # Asynchronous DAG parallel execution pipeline
│   ├── morning_scanner.py # Pre-market scanner & breakout ranking engine
│   ├── agents/            # The 8 autonomous agent implementations
│   │   ├── agent_charter.py       # Weighted Consensus Engine & charter definitions
│   │   ├── technical_agent.py     # Agent 1: Technical indicators
│   │   ├── sentiment_agent.py     # Agent 2: Sentiment aggregator
│   │   ├── strategy_agent.py      # Agent 3: 111-strategy confluence selector
│   │   ├── risk_executor_agent.py # Agent 4: Risk Guardian with VETO power
│   │   ├── fundamental_agent.py   # Agent 5: Fundamental analysis
│   │   ├── debate_agent.py        # Agent 6: Gemini 3.6 Flash Bull/Bear debate
│   │   ├── ml_agent.py            # Agent 7: XGBoost classifier
│   │   ├── ml_monitor.py          # MLOps drift monitor & accuracy tracker
│   │   └── strategy_optimizer.py  # Agent 8: Alpha backtesting & pruning engine
│   ├── connectors/        # Market data feeds (NSE via Yahoo Finance, Crypto via KuCoin/CCXT)
│   └── interfaces/        # Terminal UI components and Streamlit dashboard
│
└── scripts/               # Isolated CLI execution scripts
    ├── run_indian.py      # Quick CLI scan for Indian Equities
    └── run_crypto.py      # Quick CLI scan for Cryptocurrency
```

---

## 🚀 Quickstart

### 1. Local Run (FastAPI + React Terminal)
```bash
# Clone the repository
git clone https://github.com/Sureshkrishna179/Multi-Agent-Trading-Engine.git
cd Multi-Agent-Trading-Engine

# Install Python requirements
pip install -r requirements.txt

# Start the Terminal server
python src/api_server.py
```
Open **`http://localhost:8000`** in your browser.

---

### 2. 24/7 Cloud Deployment (Oracle Cloud Always-Free VM)
```bash
git clone https://github.com/Sureshkrishna179/Multi-Agent-Trading-Engine.git
cd Multi-Agent-Trading-Engine

# Set your Gemini API key
export GEMINI_API_KEY="your_api_key_here"

# Start the background daemon + web terminal
docker compose up -d
```
Visit **`http://YOUR_ORACLE_IP:8000`**.

---

## 🔒 Security
- **Zero Hardcoded Secrets**: Sensitive API credentials (`GEMINI_API_KEY`, broker tokens) are passed strictly through environment variables.
- **Capital Safeguard**: The Risk Guardian executes mandatory validation on every trade proposal; missing stop-loss prices or violations of the 2% risk ceiling trigger an instant hard veto.

/**
 * Institutional Mock Data & Telemetry
 * Provides rich, realistic data for Indian Equities (NSE/BSE) and Crypto (KuCoin/CCXT)
 * Ensures 100% visual fidelity on load, with interactive past trade synchronization.
 */

export const MOCK_WATCHLISTS = {
  indian: [
    { symbol: "RELIANCE.NS", name: "Reliance Industries", price: 2984.50, change: +1.84, market: "NSE", currency: "₹" },
    { symbol: "TCS.NS", name: "Tata Consultancy", price: 4125.00, change: -0.65, market: "NSE", currency: "₹" },
    { symbol: "HDFCBANK.NS", name: "HDFC Bank", price: 1682.30, change: +0.92, market: "NSE", currency: "₹" },
    { symbol: "INFY.NS", name: "Infosys Ltd", price: 1854.10, change: +2.15, market: "NSE", currency: "₹" },
    { symbol: "ICICIBANK.NS", name: "ICICI Bank", price: 1245.80, change: +0.45, market: "NSE", currency: "₹" }
  ],
  crypto: [
    { symbol: "BTC/USDT", name: "Bitcoin", price: 89450.00, change: +3.42, market: "CRYPTO", currency: "$" },
    { symbol: "ETH/USDT", name: "Ethereum", price: 3480.20, change: +1.15, market: "CRYPTO", currency: "$" },
    { symbol: "SOL/USDT", name: "Solana", price: 204.60, change: +6.85, market: "CRYPTO", currency: "$" },
    { symbol: "XRP/USDT", name: "Ripple", price: 2.14, change: +4.20, market: "CRYPTO", currency: "$" },
    { symbol: "BNB/USDT", name: "BNB Chain", price: 642.50, change: -0.30, market: "CRYPTO", currency: "$" }
  ]
};

export const MOCK_PORTFOLIO = {
  indian: {
    available_capital: 100000.00,
    daily_pnl: 4866.00,
    daily_pnl_pct: 4.87,
    open_positions: 2,
    total_trades: 28,
    currency: "₹"
  },
  crypto: {
    available_capital: 10000.00,
    daily_pnl: 742.50,
    daily_pnl_pct: 7.43,
    open_positions: 2,
    total_trades: 42,
    currency: "$"
  }
};

export const MOCK_TRADES = [
  {
    id: "TRD-8821",
    time: "14:15:22",
    date: "2026-11-05",
    symbol: "RELIANCE.NS",
    market: "NSE",
    side: "LONG",
    entry: 2980.50,
    exit: 3054.00,
    sl: 2920.00,
    tp: 3100.00,
    rr: "1:2.0",
    consensus_score: 0.84,
    consensus_action: "STRONG BUY",
    pnl: 4250.00,
    pnl_pct: 2.46,
    status: "EXECUTED",
    status_type: "WIN",
    risk_check: "APPROVED (Kelly 1.8%)",
    active: false,
    debate: {
      bull: "Liquidity grab below the 50 SMA completed on above-average institutional volume. Heavy RSI divergence on 15M; clearing 2,985 triggers aggressive short squeeze toward 3,100.",
      bear: "Resistance wall at 3,020 has rejected price twice this week. Macro crude volatility and rising bond yields could cap intraday upside.",
      judge: "Desk Manager Verdict: BUY WITH HIGH CONVICTION. Quantitative confluence across 18/111 strategies with XGBoost 84% directional probability. Dynamic ATR stop-loss anchored at ₹2,920 (2% risk ceiling)."
    }
  },
  {
    id: "TRD-8822",
    time: "11:42:08",
    date: "2026-11-05",
    symbol: "HDFCBANK.NS",
    market: "NSE",
    side: "LONG",
    entry: 1680.00,
    exit: 1646.40,
    sl: 1646.40,
    tp: 1747.20,
    rr: "1:2.0",
    consensus_score: 0.68,
    consensus_action: "BUY",
    pnl: -1680.00,
    pnl_pct: -2.00,
    status: "EXECUTED",
    status_type: "LOSS",
    risk_check: "APPROVED (ATR Stop Executed)",
    active: false,
    debate: {
      bull: "Private banking index seeing continuous call buildup at 1,680 strikes. Morning star formation on 1H chart suggests reversal.",
      bear: "FII net selling observed across financial heavyweights. Loan-to-deposit ratio concerns capping momentum.",
      judge: "Desk Manager Verdict: CONTROLLED LOSS. Stop-loss triggered at ₹1,646.40 precisely protecting capital. Maximum portfolio drawdown preserved."
    }
  },
  {
    id: "TRD-8823",
    time: "10:18:45",
    date: "2026-11-05",
    symbol: "TCS.NS",
    market: "NSE",
    side: "SHORT",
    entry: 4120.00,
    exit: 4037.60,
    sl: 4180.00,
    tp: 4000.00,
    rr: "1:2.0",
    consensus_score: -0.78,
    consensus_action: "STRONG SELL",
    pnl: 3296.00,
    pnl_pct: 2.00,
    status: "EXECUTED",
    status_type: "WIN",
    risk_check: "APPROVED (Bearish Confluence)",
    active: false,
    debate: {
      bull: "Long-term support at 4,100 holding strong. Dividend yield attractive for value accumulators.",
      bear: "Bearish head-and-shoulders breakdown confirmed with negative MACD histogram expansion. IT sector sentiment in extreme fear.",
      judge: "Desk Manager Verdict: SHORT POSITION APPROVED. Clear institutional distribution pattern. Take-profit target reached at ₹4,037.60."
    }
  },
  {
    id: "TRD-8824",
    time: "15:10:04",
    date: "2026-11-05",
    symbol: "INFY.NS",
    market: "NSE",
    side: "LONG",
    entry: 1850.00,
    exit: 1867.50,
    sl: 1810.00,
    tp: 1930.00,
    rr: "1:2.0",
    consensus_score: 0.72,
    consensus_action: "BUY",
    pnl: 1150.00,
    pnl_pct: 0.95,
    status: "ACTIVE",
    status_type: "OPEN",
    risk_check: "APPROVED (Position Open)",
    active: true,
    debate: {
      bull: "Breakout above 1,845 consolidation box with institutional accumulation blocks visible on order book. RSI at 58 with ample runway.",
      bear: "Upper wick rejection at 1,860 could create a mini bull trap before market close.",
      judge: "Desk Manager Verdict: ACCUMULATE LONG. Position active. Trailing ATR stop locked at ₹1,810. 1:2.0 risk-reward ratio verified."
    }
  },
  {
    id: "TRD-8825",
    time: "13:20:11",
    date: "2026-11-05",
    symbol: "ICICIBANK.NS",
    market: "NSE",
    side: "LONG",
    entry: 1245.00,
    exit: 0,
    sl: 0,
    tp: 0,
    rr: "N/A",
    consensus_score: 0.81,
    consensus_action: "STRONG BUY",
    pnl: 0,
    pnl_pct: 0,
    status: "VETOED",
    status_type: "VETO",
    risk_check: "⛔ VETOED: Missing SL from Strategy Agent",
    active: false,
    debate: {
      bull: "Superb quarterly NIM expansion, breakout to all-time highs with overwhelming institutional buy orders.",
      bear: "Extended technical metrics, risk of mean-reversion pullbacks.",
      judge: "Desk Manager & Risk Guardian Verdict: HARD VETO ENFORCED. Strategy Agent submitted signal without ATR stop-loss bounds. Trade blocked to protect capital."
    }
  },
  {
    id: "TRD-8826",
    time: "08:45:12",
    date: "2026-11-05",
    symbol: "SOL/USDT",
    market: "CRYPTO",
    side: "LONG",
    entry: 198.50,
    exit: 214.20,
    sl: 191.00,
    tp: 215.00,
    rr: "1:2.2",
    consensus_score: 0.91,
    consensus_action: "STRONG BUY",
    pnl: 1256.00,
    pnl_pct: 7.91,
    status: "EXECUTED",
    status_type: "WIN",
    risk_check: "APPROVED (KuCoin Spot)",
    active: false,
    debate: {
      bull: "DEX volumes on Solana flipped Ethereum. Massive perpetual open interest surge with negative funding indicating imminent short squeeze.",
      bear: "Overheated 4H funding rate could trigger rapid flush out of late longs.",
      judge: "Desk Manager Verdict: AGGRESSIVE BUY. 24/111 strategies triggered. XGBoost probability 88.5%. Full target hit at $214.20."
    }
  },
  {
    id: "TRD-8827",
    time: "09:12:30",
    date: "2026-11-05",
    symbol: "BTC/USDT",
    market: "CRYPTO",
    side: "LONG",
    entry: 88500.00,
    exit: 89450.00,
    sl: 86800.00,
    tp: 92000.00,
    rr: "1:2.0",
    consensus_score: 0.86,
    consensus_action: "STRONG BUY",
    pnl: 840.00,
    pnl_pct: 1.07,
    status: "ACTIVE",
    status_type: "OPEN",
    risk_check: "APPROVED (Position Open)",
    active: true,
    debate: {
      bull: "Institutional spot ETF inflows exceed $400M today. Consolidation above $88K absorption zone confirms higher low.",
      bear: "Macro CPI release in 48 hours could trigger high volatility sweep of $87,500 liquidity.",
      judge: "Desk Manager Verdict: ACTIVE LONG. Position sized conservatively via Kelly Criterion (1.5% capital). ATR stop set at $86,800."
    }
  },
  {
    id: "TRD-8828",
    time: "07:33:19",
    date: "2026-11-05",
    symbol: "ETH/USDT",
    market: "CRYPTO",
    side: "LONG",
    entry: 3450.00,
    exit: 0,
    sl: 3410.00,
    tp: 3490.00,
    rr: "1:1.0",
    consensus_score: 0.58,
    consensus_action: "BUY",
    pnl: 0,
    pnl_pct: 0,
    status: "VETOED",
    status_type: "VETO",
    risk_check: "⛔ VETOED: Risk-Reward 1:1.0 < 1:2.0 Minimum",
    active: false,
    debate: {
      bull: "Layer-2 gas consumption hitting record peaks. Staking yield steady at 3.4%.",
      bear: "ETH/BTC ratio in severe multi-month structural downtrend. Lack of institutional follow-through.",
      judge: "Desk Manager & Risk Guardian Verdict: VETO EXERCISED. Trade proposal offered only 1:1.0 R:R ($40 profit vs $40 risk). Minimum mandate is 1:2.0."
    }
  }
];

export const MOCK_COMMITTEE_DATA = {
  agent_1_technical: {
    name: "01 Technical Observer",
    score: 0.82,
    regime: "BULLISH REGIME",
    rsi: 64.2,
    macd: "+14.8",
    adx: 31.4,
    weight: 0.20,
    status: "BULL",
    details: "RSI 64.2 · Bullish MACD crossover · Price > 20/50/200 SMA"
  },
  agent_2_sentiment: {
    name: "02 Multi-Source Sentiment",
    score: 0.78,
    sentiment_index: 78,
    label: "BULLISH GREED",
    live_sources: "4/4 live",
    weight: 0.10,
    status: "BULL",
    details: "Moneycontrol + Livemint + Reddit ISB + Fear/Greed (78/100)"
  },
  agent_3_strategy: {
    name: "03 111-Strategy Confluence",
    score: 0.85,
    triggered_count: 24,
    total_strategies: 111,
    top_pattern: "Bullish Engulfing + Volume Breakout",
    weight: 0.15,
    status: "BULL",
    details: "24/111 rules triggered · Confluence score 0.85/1.0"
  },
  agent_5_fundamental: {
    name: "05 Fundamental Analyst",
    score: 0.45,
    pe_ratio: "24.2",
    de_ratio: "0.42",
    growth: "+14.8%",
    label: "FAIRLY VALUED",
    weight: 0.10,
    status: "BULL",
    details: "P/E 24.2 (Sector 28.0) · D/E 0.42 · Robust YoY Growth"
  },
  agent_7_ml: {
    name: "07 XGBoost ML Brain",
    score: 0.84,
    probability: 84.2,
    drift_status: "HEALTHY",
    accuracy: "68.4%",
    weight: 0.25,
    status: "BULL",
    details: "84.2% Upward Directional Prob · Drift 0.02 (Stable)"
  },
  agent_8_optimizer: {
    name: "08 Alpha Optimizer",
    score: 0.65,
    win_rate: "58.4%",
    pruned: 14,
    cached: true,
    weight: 0.10,
    status: "BULL",
    details: "58.4% Win Rate across 30D backtest · 0% CPU Cached"
  },
  agent_4_risk: {
    name: "04 Risk Guardian",
    status: "APPROVED",
    approved: true,
    position_size: "150 Shares",
    risk_amount: "₹1,800.00",
    stop_loss: "₹2,920.00",
    take_profit: "₹3,100.00",
    rr_ratio: "1:2.0",
    details: "Kelly 1.8% · Max 2% loss ceiling · 1:2.0 verified"
  },
  consensus: {
    score: 0.81,
    action: "STRONG BUY",
    strength: "VERY STRONG",
    confidence: "81.0%",
    latency: "1.84s"
  }
};

/**
 * Generates 60 realistic daily OHLCV candlesticks for any asset
 */
export function generateCandles(basePrice = 2900, volatility = 0.02) {
  const candles = [];
  const now = new Date();
  let currentPrice = basePrice * 0.92;

  for (let i = 60; i >= 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split("T")[0];

    const changePercent = (Math.random() - 0.47) * volatility;
    const open = currentPrice;
    const close = Math.round((open * (1 + changePercent)) * 100) / 100;
    const high = Math.round((Math.max(open, close) + Math.random() * open * 0.012) * 100) / 100;
    const low = Math.round((Math.min(open, close) - Math.random() * open * 0.012) * 100) / 100;
    const volume = Math.round(500000 + Math.random() * 1500000);

    candles.push({
      time: dateStr,
      open,
      high,
      low,
      close,
      volume
    });

    currentPrice = close;
  }

  return candles;
}


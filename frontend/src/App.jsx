import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import HeroHUD from './components/HeroHUD';
import WatchlistBar from './components/WatchlistBar';
import ZoneA_Chart from './components/ZoneA_Chart';
import ZoneB_AgentCommittee from './components/ZoneB_AgentCommittee';
import ZoneC_DebateFeed from './components/ZoneC_DebateFeed';
import ZoneD_TradeLedger from './components/ZoneD_TradeLedger';

import { 
  MOCK_WATCHLISTS, MOCK_PORTFOLIO, MOCK_TRADES, 
  MOCK_COMMITTEE_DATA, generateCandles 
} from './mockData';

const API_BASE = "http://localhost:8000";
const WS_BASE = "ws://localhost:8000/ws";

export default function App() {
  const [market, setMarket] = useState("indian"); // "indian" | "crypto"
  const [activeSymbol, setActiveSymbol] = useState("RELIANCE.NS");
  const [selectedTrade, setSelectedTrade] = useState(MOCK_TRADES[0]); // Default inspect Trade #1
  const [candles, setCandles] = useState([]);
  const [portfolio, setPortfolio] = useState(MOCK_PORTFOLIO.indian);
  const [committeeData, setCommitteeData] = useState(MOCK_COMMITTEE_DATA);
  const [activeDebate, setActiveDebate] = useState(MOCK_TRADES[0].debate);
  const [isScanning, setIsScanning] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);

  const wsRef = useRef(null);
  const currentWatchlist = market === "indian" ? MOCK_WATCHLISTS.indian : MOCK_WATCHLISTS.crypto;
  const currency = market === "indian" ? "₹" : "$";

  // Switch default symbol when market changes
  useEffect(() => {
    const list = market === "indian" ? MOCK_WATCHLISTS.indian : MOCK_WATCHLISTS.crypto;
    const firstAsset = list[0];
    setActiveSymbol(firstAsset.symbol);
    setPortfolio(market === "indian" ? MOCK_PORTFOLIO.indian : MOCK_PORTFOLIO.crypto);

    // Try fetching live portfolio from backend if running
    fetch(`${API_BASE}/api/portfolio?market=${market}`)
      .then(r => r.json())
      .then(data => {
        if (data.available_capital) {
          setPortfolio(prev => ({
            ...prev,
            available_capital: data.available_capital,
            daily_pnl: data.daily_pnl,
            open_positions: data.open_positions,
            total_trades: data.total_trades
          }));
        }
      })
      .catch(() => {});
  }, [market]);

  // Generate / Load Candlesticks for activeSymbol
  useEffect(() => {
    // Try fetching from backend /api/ohlcv
    fetch(`${API_BASE}/api/ohlcv?symbol=${encodeURIComponent(activeSymbol)}&market=${market}`)
      .then(r => r.json())
      .then(data => {
        if (data.candles && data.candles.length > 0) {
          setCandles(data.candles);
        } else {
          // Generate realistic candlesticks based on asset price
          const asset = currentWatchlist.find(a => a.symbol === activeSymbol);
          setCandles(generateCandles(asset ? asset.price : 2900));
        }
      })
      .catch(() => {
        // Instant realistic fallback
        const asset = currentWatchlist.find(a => a.symbol === activeSymbol);
        setCandles(generateCandles(asset ? asset.price : 2900));
      });
  }, [activeSymbol, market]);

  // WebSocket Connection for Real-Time Daemon Stream
  useEffect(() => {
    let reconnectTimer;
    const connectWs = () => {
      const socket = new WebSocket(WS_BASE);
      wsRef.current = socket;

      socket.onopen = () => {
        setWsConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === "SCAN_COMPLETED") {
            const data = msg.data;
            if (data.symbol === activeSymbol) {
              if (data.debate) setActiveDebate(data.debate);
            }
          }
        } catch {
          // ignore
        }
      };

      socket.onclose = () => {
        setWsConnected(false);
        reconnectTimer = setTimeout(connectWs, 5000);
      };

      socket.onerror = () => {
        socket.close();
      };
    };

    connectWs();
    return () => {
      clearTimeout(reconnectTimer);
      if (wsRef.current) wsRef.current.close();
    };
  }, [activeSymbol]);

  // Handle Trade Click from Zone D
  const handleSelectTrade = (trade) => {
    setSelectedTrade(trade);
    setActiveSymbol(trade.symbol);
    if (trade.market === "CRYPTO" && market !== "crypto") {
      setMarket("crypto");
    } else if (trade.market === "NSE" && market !== "indian") {
      setMarket("indian");
    }
    if (trade.debate) {
      setActiveDebate(trade.debate);
    }
  };

  // Clear Selected Trade
  const handleClearSelectedTrade = () => {
    setSelectedTrade(null);
  };

  // Run Manual Asset Scan
  const handleRunScan = async (symbolToScan = null) => {
    const sym = symbolToScan || activeSymbol;
    setIsScanning(true);

    try {
      const res = await fetch(`${API_BASE}/api/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol: sym, market_type: market })
      });
      const data = await res.json();
      if (data.debate) setActiveDebate(data.debate);
    } catch {
      // Keep rich mock state if offline
    } finally {
      setIsScanning(false);
    }
  };

  const activeAsset = currentWatchlist.find(a => a.symbol === activeSymbol) || currentWatchlist[0];

  return (
    <div className="min-h-screen bg-[#080810] text-[#e2e8f0] flex flex-col selection:bg-purple-900 selection:text-white">
      {/* ── TOP NAVIGATION BAR ── */}
      <Header
        market={market}
        setMarket={setMarket}
        wsConnected={wsConnected}
        mode="PAPER"
      />

      <div className="p-3 sm:p-4 max-w-[1780px] mx-auto w-full flex-1 flex flex-col space-y-3">
        {/* ── TOP HUD (Capital, PnL, Positions, 6% Drawdown Ceiling) ── */}
        <HeroHUD portfolio={portfolio} currency={currency} />

        {/* ── WATCHLIST STRIP & TICKER SEARCH ── */}
        <WatchlistBar
          watchlist={currentWatchlist.map(a => a.symbol)}
          activeSymbol={activeSymbol}
          onSelectSymbol={(sym) => {
            setActiveSymbol(sym);
            handleClearSelectedTrade();
          }}
          onScan={handleRunScan}
          isScanning={isScanning}
          market={market}
        />

        {/* ── 4-ZONE BENTO GRID (12 COLUMNS) ── */}
        <div className="flex-1 flex flex-col space-y-3">
          {/* TOP ROW: Zone A (8 Cols) + Zone B (4 Cols) */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 min-h-[460px]">
            {/* Zone A: Interactive Trade Position Chart (8 Cols) */}
            <div className="lg:col-span-8 h-full">
              <ZoneA_Chart
                candles={candles}
                activeAsset={activeAsset}
                selectedTrade={selectedTrade}
                onClearSelectedTrade={handleClearSelectedTrade}
                market={activeAsset?.market || "NSE"}
                currency={currency}
                latency="1.84s"
              />
            </div>

            {/* Zone B: The 8-Agent Committee HUD (4 Cols) */}
            <div className="lg:col-span-4 h-full">
              <ZoneB_AgentCommittee committeeData={committeeData} />
            </div>
          </div>

          {/* BOTTOM ROW: Zone C (5 Cols) + Zone D (7 Cols) */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-3 min-h-[380px]">
            {/* Zone C: Adversarial LLM Bull vs Bear & Position Chat Feed (5 Cols) */}
            <div className="lg:col-span-5 h-full">
              <ZoneC_DebateFeed
                debate={activeDebate}
                tradeContext={selectedTrade}
                fallbackMode={false}
              />
            </div>

            {/* Zone D: Ultra-Fast Past Trade & Audit Tape (7 Cols) */}
            <div className="lg:col-span-7 h-full">
              <ZoneD_TradeLedger
                trades={MOCK_TRADES}
                selectedTradeId={selectedTrade?.id}
                onSelectTrade={handleSelectTrade}
                currency={currency}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

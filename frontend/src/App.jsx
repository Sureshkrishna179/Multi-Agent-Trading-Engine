import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import HeroHUD from './components/HeroHUD';
import WatchlistBar from './components/WatchlistBar';
import TradingChart from './components/TradingChart';
import AgentPanel from './components/AgentPanel';
import DebateChamber from './components/DebateChamber';
import RiskCard from './components/RiskCard';
import TerminalLogs from './components/TerminalLogs';
import { AlertCircle, Zap } from 'lucide-react';

const API_BASE = "http://localhost:8000";
const WS_BASE = "ws://localhost:8000/ws";

export default function App() {
  const [market, setMarket] = useState("indian");
  const [watchlists, setWatchlists] = useState({ indian: [], crypto: [] });
  const [activeSymbol, setActiveSymbol] = useState("RELIANCE.NS");
  const [portfolio, setPortfolio] = useState(null);
  const [activeScan, setActiveScan] = useState(null);
  const [candles, setCandles] = useState([]);
  const [isScanning, setIsScanning] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [logs, setLogs] = useState([]);

  const wsRef = useRef(null);
  const currency = market === "indian" ? "₹" : "$";

  const addLog = (message, type = "INFO") => {
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });
    setLogs(prev => [...prev.slice(-100), { time, message, type }]);
  };

  // 1. Fetch initial Watchlists and Portfolio
  useEffect(() => {
    fetch(`${API_BASE}/api/watchlists`)
      .then(res => res.json())
      .then(data => {
        setWatchlists(data);
        if (market === "indian" && data.indian?.length) {
          setActiveSymbol(data.indian[0]);
        } else if (market === "crypto" && data.crypto?.length) {
          setActiveSymbol(data.crypto[0]);
        }
      })
      .catch(err => addLog(`Failed to fetch watchlists: ${err.message}`, "ERROR"));
  }, []);

  // Update symbol & portfolio whenever market changes
  useEffect(() => {
    const list = market === "indian" ? watchlists.indian : watchlists.crypto;
    if (list && list.length > 0) {
      setActiveSymbol(list[0]);
    }

    fetch(`${API_BASE}/api/portfolio?market=${market}`)
      .then(res => res.json())
      .then(data => setPortfolio(data))
      .catch(err => addLog(`Failed to fetch portfolio: ${err.message}`, "ERROR"));
  }, [market, watchlists]);

  // 2. Fetch Candlesticks whenever activeSymbol or market changes
  useEffect(() => {
    if (!activeSymbol) return;
    fetch(`${API_BASE}/api/ohlcv?symbol=${encodeURIComponent(activeSymbol)}&market=${market}`)
      .then(res => res.json())
      .then(data => {
        if (data.candles) {
          setCandles(data.candles);
        }
      })
      .catch(err => addLog(`Failed to load candles for ${activeSymbol}: ${err.message}`, "WARN"));
  }, [activeSymbol, market]);

  // 3. Setup WebSocket Connection with auto-reconnect
  useEffect(() => {
    let reconnectTimer;
    const connectWs = () => {
      const socket = new WebSocket(WS_BASE);
      wsRef.current = socket;

      socket.onopen = () => {
        setWsConnected(true);
        addLog("Connected to 8-Agent Backend Daemon WebSocket", "SUCCESS");
      };

      socket.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === "SCAN_STARTED") {
            addLog(`▶ Scan initiated for [${msg.symbol}] on ${msg.market.toUpperCase()}`, "INFO");
          } else if (msg.type === "SCAN_COMPLETED") {
            const data = msg.data;
            addLog(`✅ Pipeline complete for [${data.symbol}] in ${data.pipeline_time_seconds}s. Action: ${data.consensus?.action}`, "SUCCESS");
            if (data.symbol === activeSymbol) {
              setActiveScan(data);
            }
          } else if (msg.type === "SCAN_FAILED") {
            addLog(`❌ Scan failed for [${msg.symbol}]: ${msg.error}`, "ERROR");
          }
        } catch {
          // non-json message
        }
      };

      socket.onclose = () => {
        setWsConnected(false);
        addLog("WebSocket disconnected. Retrying in 4s...", "WARN");
        reconnectTimer = setTimeout(connectWs, 4000);
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

  // 4. Trigger Scan Action
  const handleScan = async (symbolToScan = null, scanAll = false) => {
    setIsScanning(true);
    const targetSymbol = symbolToScan || activeSymbol;

    if (scanAll) {
      const list = market === "indian" ? watchlists.indian : watchlists.crypto;
      addLog(`⚡ Commencing batch scan of all ${list.length} assets...`, "INFO");
      for (const sym of list) {
        try {
          setActiveSymbol(sym);
          const res = await fetch(`${API_BASE}/api/scan`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symbol: sym, market_type: market })
          });
          const data = await res.json();
          setActiveScan(data);
        } catch (e) {
          addLog(`Error batch scanning ${sym}: ${e.message}`, "ERROR");
        }
      }
      setIsScanning(false);
      return;
    }

    try {
      addLog(`Executing 8-Agent DAG Pipeline for ${targetSymbol}...`, "INFO");
      const res = await fetch(`${API_BASE}/api/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol: targetSymbol, market_type: market })
      });
      const data = await res.json();
      setActiveScan(data);
      addLog(`Scan finished. Decision: ${data.consensus?.action} (Score: ${data.consensus?.score})`, "SUCCESS");
    } catch (err) {
      addLog(`Scan execution error: ${err.message}`, "ERROR");
    } finally {
      setIsScanning(false);
    }
  };

  const currentWatchlist = market === "indian" ? watchlists.indian : watchlists.crypto;
  const consensusAction = activeScan?.consensus?.action || "HOLD";
  const consensusScore = activeScan?.consensus?.score || 0.0;
  const consensusStrength = activeScan?.consensus?.strength || "NEUTRAL";

  let bannerClass = "bg-[#111122] border-gray-700 text-gray-300";
  let actionColor = "text-gray-400";
  let badgeColor = "bg-gray-800 text-gray-300 border-gray-700";

  if (consensusAction === "BUY") {
    bannerClass = "bg-gradient-to-r from-emerald-950/60 to-[#0e1f14] border-emerald-500/50 text-emerald-100";
    actionColor = "text-emerald-400";
    badgeColor = "bg-emerald-500/20 text-emerald-400 border-emerald-500/60 shadow-[0_0_12px_#10b98144]";
  } else if (consensusAction === "SELL") {
    bannerClass = "bg-gradient-to-r from-rose-950/60 to-[#260e0e] border-rose-500/50 text-rose-100";
    actionColor = "text-rose-400";
    badgeColor = "bg-rose-500/20 text-rose-400 border-rose-500/60 shadow-[0_0_12px_#f43f5e44]";
  }

  return (
    <div className="min-h-screen bg-[#080810] text-[#e2e8f0] pb-10">
      <Header
        market={market}
        setMarket={setMarket}
        wsConnected={wsConnected}
        mode="PAPER"
      />

      <main className="max-w-7xl mx-auto px-3 sm:px-6 pt-4">
        {/* Top Hero PnL Bar */}
        <HeroHUD portfolio={portfolio} currency={currency} />

        {/* Watchlist & Search Strip */}
        <WatchlistBar
          watchlist={currentWatchlist}
          activeSymbol={activeSymbol}
          onSelectSymbol={setActiveSymbol}
          onScan={handleScan}
          isScanning={isScanning}
          market={market}
        />

        {/* Consensus Signal Banner */}
        {activeScan && (
          <div className={`rounded-xl border p-4 mb-4 flex items-center justify-between transition-all ${bannerClass}`}>
            <div>
              <div className="font-mono text-xs uppercase tracking-widest text-gray-400 mb-1 flex items-center space-x-2">
                <span>{activeScan.symbol}</span>
                <span>·</span>
                <span>{currency}{activeScan.price?.toFixed(2)}</span>
                <span>·</span>
                <span>⚡ {activeScan.pipeline_time_seconds}s DAG Latency</span>
              </div>
              <div className={`font-mono text-3xl font-extrabold tracking-wider ${actionColor}`}>
                {consensusAction}
              </div>
              <div className="font-mono text-xs text-gray-400 mt-1">
                Weighted Consensus Score: <strong className="text-white">{consensusScore > 0 ? `+${consensusScore.toFixed(4)}` : consensusScore.toFixed(4)}</strong>
              </div>
            </div>

            <div className="text-right">
              <span className={`font-mono text-xs font-bold px-3 py-1.5 rounded-lg border uppercase tracking-wider inline-block ${badgeColor}`}>
                {consensusStrength} CONVICTION
              </span>
              <div className="font-mono text-[11px] text-gray-500 mt-2">
                {activeScan.risk?.approved ? "✅ APPROVED BY GUARDIAN" : "🛑 VETOED BY GUARDIAN"}
              </div>
            </div>
          </div>
        )}

        {/* Main Grid: Candlestick Chart (Left) & 8-Agent Committee (Right) */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
          <div className="lg:col-span-2">
            <TradingChart
              candles={candles}
              symbol={activeSymbol}
              action={activeScan?.consensus?.action}
              currency={currency}
            />
          </div>

          <div className="lg:col-span-1">
            <AgentPanel
              agentVotes={activeScan?.consensus?.agent_votes}
              mlHealth={activeScan?.ml_health}
            />
          </div>
        </div>

        {/* Bull vs Bear Wall Street Debate Chamber */}
        <DebateChamber debate={activeScan?.debate} />

        {/* Risk Guardian Card */}
        <RiskCard risk={activeScan?.risk} currency={currency} />

        {/* Live Terminal Daemon Event Stream */}
        <TerminalLogs logs={logs} onClear={() => setLogs([])} />
      </main>
    </div>
  );
}


import React, { useState, useEffect } from 'react';
import { Activity, ShieldCheck, Zap, Globe, Clock } from 'lucide-react';

export default function Header({ market, setMarket, wsConnected, mode = "PAPER" }) {
  const [timeStr, setTimeStr] = useState("");

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString('en-US', { hour12: false, timeZone: 'Asia/Kolkata' }) + " IST");
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="border-b border-[#1a1a2e] bg-[#0a0a14] px-4 py-2.5 flex items-center justify-between sticky top-0 z-50">
      {/* Brand & Terminal Info */}
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2">
          <div className="w-2.5 h-2.5 rounded-full bg-purple-500 shadow-[0_0_8px_#a855f7]"></div>
          <span className="font-mono font-bold tracking-widest text-sm text-purple-400">
            ⬡ TRADING.DESK
          </span>
        </div>
        <span className="text-[#374151]">/</span>
        <span className="font-mono text-xs text-gray-400 hidden sm:inline">
          8-AGENT CONCURRENT DAG
        </span>
      </div>

      {/* Market Selector Tabs */}
      <div className="flex items-center bg-[#111120] border border-[#1e1e32] rounded-lg p-0.5">
        <button
          onClick={() => setMarket("indian")}
          className={`flex items-center space-x-1.5 px-3 py-1 rounded-md text-xs font-mono font-medium transition-all ${
            market === "indian"
              ? "bg-purple-600/30 text-purple-300 border border-purple-500/50 shadow-sm"
              : "text-gray-400 hover:text-gray-200"
          }`}
        >
          <span>🇮🇳</span>
          <span>INDIAN (NSE)</span>
        </button>
        <button
          onClick={() => setMarket("crypto")}
          className={`flex items-center space-x-1.5 px-3 py-1 rounded-md text-xs font-mono font-medium transition-all ${
            market === "crypto"
              ? "bg-purple-600/30 text-purple-300 border border-purple-500/50 shadow-sm"
              : "text-gray-400 hover:text-gray-200"
          }`}
        >
          <span>🌐</span>
          <span>CRYPTO (KUCOIN)</span>
        </button>
      </div>

      {/* Right Status Badges */}
      <div className="flex items-center space-x-3 font-mono text-xs">
        {/* Clock */}
        <div className="hidden md:flex items-center space-x-1.5 text-gray-400 bg-[#111120] px-2.5 py-1 rounded border border-[#1e1e32]">
          <Clock className="w-3.5 h-3.5 text-purple-400" />
          <span>{timeStr}</span>
        </div>

        {/* Execution Mode */}
        <div className="flex items-center space-x-1 bg-[#111120] text-emerald-400 px-2.5 py-1 rounded border border-emerald-950">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>{mode}</span>
        </div>

        {/* WebSocket Pulse */}
        <div className="flex items-center space-x-1.5 bg-[#111120] px-2.5 py-1 rounded border border-[#1e1e32]">
          <div
            className={`w-2 h-2 rounded-full ${
              wsConnected ? "bg-emerald-400 shadow-[0_0_8px_#34d399]" : "bg-rose-500"
            }`}
          />
          <span className="text-gray-400 text-[11px] hidden sm:inline">
            {wsConnected ? "LIVE" : "OFFLINE"}
          </span>
        </div>
      </div>
    </header>
  );
}


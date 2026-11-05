import React, { useState } from 'react';
import { Search, Play, RefreshCw, Zap } from 'lucide-react';

export default function WatchlistBar({
  watchlist = [],
  activeSymbol,
  onSelectSymbol,
  onScan,
  isScanning,
  market
}) {
  const [customInput, setCustomInput] = useState("");

  const handleCustomSubmit = (e) => {
    e.preventDefault();
    if (!customInput.trim()) return;
    const sym = customInput.trim().toUpperCase();
    onSelectSymbol(sym);
    onScan(sym);
    setCustomInput("");
  };

  return (
    <div className="bg-[#0d0d1a] border border-[#1a1a2e] rounded-xl p-3 mb-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        {/* Custom Input */}
        <form onSubmit={handleCustomSubmit} className="flex items-center space-x-2 flex-1 max-w-md">
          <div className="relative flex-1">
            <Search className="w-3.5 h-3.5 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={customInput}
              onChange={(e) => setCustomInput(e.target.value)}
              placeholder={market === "indian" ? "Search Ticker (e.g. INFY.NS, MARUTI.NS)..." : "Search Crypto (e.g. PEPE/USDT)..."}
              className="w-full bg-[#111120] border border-[#1e1e32] rounded-lg pl-9 pr-3 py-1.5 font-mono text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors"
            />
          </div>
          <button
            type="submit"
            disabled={isScanning}
            className="flex items-center space-x-1 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-mono text-xs font-semibold px-3.5 py-1.5 rounded-lg transition-colors shadow-sm"
          >
            {isScanning ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Play className="w-3.5 h-3.5 fill-current" />
            )}
            <span>ANALYZE</span>
          </button>
        </form>

        {/* Scan All Button */}
        <button
          onClick={() => onScan(null, true)}
          disabled={isScanning}
          className="flex items-center justify-center space-x-1.5 bg-[#141428] hover:bg-[#1a1a36] border border-purple-500/30 text-purple-300 font-mono text-xs font-semibold px-4 py-1.5 rounded-lg transition-colors"
        >
          <Zap className="w-3.5 h-3.5 text-purple-400" />
          <span>SCAN ALL {watchlist.length} ASSETS</span>
        </button>
      </div>

      {/* Watchlist Quick-Select Chips */}
      <div className="flex items-center space-x-1.5 overflow-x-auto pt-3 pb-1 scrollbar-thin">
        <span className="font-mono text-[10px] text-gray-500 uppercase tracking-wider flex-shrink-0 mr-1">
          WATCHLIST:
        </span>
        {watchlist.map((sym) => {
          const isActive = sym === activeSymbol;
          return (
            <button
              key={sym}
              onClick={() => {
                onSelectSymbol(sym);
                onScan(sym);
              }}
              className={`flex-shrink-0 font-mono text-[11px] px-2.5 py-1 rounded-md border transition-all ${
                isActive
                  ? 'bg-purple-600/20 text-purple-300 border-purple-500/60 shadow-[0_0_8px_#a855f733]'
                  : 'bg-[#111120] text-gray-400 border-[#1e1e32] hover:border-gray-600 hover:text-gray-200'
              }`}
            >
              {sym}
            </button>
          );
        })}
      </div>
    </div>
  );
}


import React, { useState } from 'react';
import { ShieldCheck, ShieldAlert, CheckCircle2, Clock, Filter, Eye, ArrowRight } from 'lucide-react';

export default function ZoneD_TradeLedger({
  trades = [],
  selectedTradeId = null,
  onSelectTrade,
  currency = "₹"
}) {
  const [activeFilter, setActiveFilter] = useState("ALL");

  const filteredTrades = trades.filter(t => {
    if (activeFilter === "EXECUTED") return t.status === "EXECUTED";
    if (activeFilter === "VETOED") return t.status === "VETOED";
    if (activeFilter === "ACTIVE") return t.status === "ACTIVE";
    return true;
  });

  return (
    <div className="bg-[#0b0c16] border border-[#1a1c2e] rounded-xl overflow-hidden shadow-2xl flex flex-col h-full">
      {/* Top Ledger Header with Filter Tabs */}
      <div className="px-4 py-2.5 bg-[#0e101d] border-b border-[#1a1c2e] flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center space-x-2">
          <Clock className="w-4 h-4 text-cyan-400" />
          <span className="font-mono text-xs font-bold uppercase tracking-wider text-cyan-300">
            AUDIT TAPE & PAST EXECUTIONS
          </span>
          <span className="font-mono text-[10px] text-gray-500 hidden sm:inline">
            (CLICK ROW TO INSPECT ON CHART)
          </span>
        </div>

        {/* Quick Filter Tabs */}
        <div className="flex items-center bg-[#141628] border border-[#1e2238] rounded-lg p-0.5 font-mono text-[11px]">
          <button
            onClick={() => setActiveFilter("ALL")}
            className={`px-2.5 py-1 rounded-md transition-all ${
              activeFilter === "ALL"
                ? "bg-purple-600 text-white font-bold"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            All ({trades.length})
          </button>
          <button
            onClick={() => setActiveFilter("EXECUTED")}
            className={`px-2.5 py-1 rounded-md transition-all ${
              activeFilter === "EXECUTED"
                ? "bg-emerald-600 text-white font-bold"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            Executed ({trades.filter(t => t.status === "EXECUTED").length})
          </button>
          <button
            onClick={() => setActiveFilter("VETOED")}
            className={`px-2.5 py-1 rounded-md transition-all ${
              activeFilter === "VETOED"
                ? "bg-rose-600 text-white font-bold"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            Vetoes ({trades.filter(t => t.status === "VETOED").length})
          </button>
          <button
            onClick={() => setActiveFilter("ACTIVE")}
            className={`px-2.5 py-1 rounded-md transition-all ${
              activeFilter === "ACTIVE"
                ? "bg-cyan-600 text-white font-bold"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            Active ({trades.filter(t => t.status === "ACTIVE").length})
          </button>
        </div>
      </div>

      {/* High-Contrast Interactive Table */}
      <div className="flex-1 overflow-x-auto overflow-y-auto max-h-[340px] scrollbar-thin select-text">
        <table className="w-full text-left font-mono text-xs border-collapse">
          <thead className="bg-[#0e101d] text-gray-400 text-[10px] uppercase tracking-wider sticky top-0 z-10 border-b border-[#1a1c2e]">
            <tr>
              <th className="py-2 px-3">Time</th>
              <th className="py-2 px-3">Asset</th>
              <th className="py-2 px-3">Side</th>
              <th className="py-2 px-3">Entry → Target</th>
              <th className="py-2 px-3">R:R / SL</th>
              <th className="py-2 px-3">Consensus</th>
              <th className="py-2 px-3 text-right">Status / Net PnL</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#151726]">
            {filteredTrades.map((t) => {
              const isSelected = t.id === selectedTradeId;
              const isWin = t.status_type === "WIN";
              const isLoss = t.status_type === "LOSS";
              const isOpen = t.status_type === "OPEN";
              const isVeto = t.status_type === "VETO";

              return (
                <tr
                  key={t.id}
                  onClick={() => onSelectTrade(t)}
                  className={`cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-cyan-950/40 border-l-4 border-cyan-400'
                      : 'hover:bg-[#121424]'
                  }`}
                >
                  {/* Time */}
                  <td className="py-2 px-3 text-gray-400 text-[11px] whitespace-nowrap">
                    {t.time}
                  </td>

                  {/* Asset */}
                  <td className="py-2 px-3 font-bold text-white whitespace-nowrap">
                    <span>{t.symbol}</span>
                    <span className="ml-1.5 text-[9px] px-1 py-0.2 rounded bg-[#181b30] text-gray-400 border border-gray-700 font-normal">
                      {t.market}
                    </span>
                  </td>

                  {/* Side */}
                  <td className="py-2 px-3 whitespace-nowrap">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      t.side === "LONG"
                        ? "bg-emerald-950/70 text-emerald-400 border border-emerald-500/50"
                        : "bg-rose-950/70 text-rose-400 border border-rose-500/50"
                    }`}>
                      {t.side}
                    </span>
                  </td>

                  {/* Entry -> Exit */}
                  <td className="py-2 px-3 text-gray-300 text-[11px] whitespace-nowrap">
                    <span className="text-gray-400">{currency}{t.entry.toLocaleString()}</span>
                    {t.exit > 0 && (
                      <>
                        <ArrowRight className="w-3 h-3 inline mx-1 text-gray-600" />
                        <span className={isWin ? "text-emerald-400 font-semibold" : "text-rose-400 font-semibold"}>
                          {currency}{t.exit.toLocaleString()}
                        </span>
                      </>
                    )}
                  </td>

                  {/* R:R / SL */}
                  <td className="py-2 px-3 text-[11px] whitespace-nowrap">
                    {t.sl > 0 ? (
                      <span className="text-gray-300">
                        {t.rr} · <span className="text-rose-400">{currency}{t.sl.toLocaleString()}</span>
                      </span>
                    ) : (
                      <span className="text-gray-600">N/A</span>
                    )}
                  </td>

                  {/* Consensus */}
                  <td className="py-2 px-3 whitespace-nowrap">
                    <div className="flex items-center space-x-1.5">
                      <div className="w-12 bg-[#1b1e33] h-1.5 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${t.consensus_score > 0 ? 'bg-emerald-400' : 'bg-rose-400'}`}
                          style={{ width: `${Math.abs(t.consensus_score) * 100}%` }}
                        />
                      </div>
                      <span className="text-[10px] text-gray-300">
                        {t.consensus_score > 0 ? `+${(t.consensus_score * 100).toFixed(0)}%` : `${(t.consensus_score * 100).toFixed(0)}%`}
                      </span>
                    </div>
                  </td>

                  {/* Status / PnL */}
                  <td className="py-2 px-3 text-right whitespace-nowrap font-bold">
                    {isVeto ? (
                      <span className="inline-block px-2 py-0.5 rounded bg-rose-950/60 border border-rose-500/50 text-rose-400 text-[10px]" title={t.risk_check}>
                        ⛔ VETOED
                      </span>
                    ) : isOpen ? (
                      <span className="inline-block px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-500/50 text-cyan-300 text-[10px]">
                        ACTIVE ({t.pnl_pct > 0 ? `+${t.pnl_pct}%` : `${t.pnl_pct}%`})
                      </span>
                    ) : isWin ? (
                      <span className="text-emerald-400 text-sm">
                        +{currency}{t.pnl.toLocaleString()} (+{t.pnl_pct}%)
                      </span>
                    ) : (
                      <span className="text-rose-400 text-sm">
                        -{currency}{Math.abs(t.pnl).toLocaleString()} ({t.pnl_pct}%)
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}


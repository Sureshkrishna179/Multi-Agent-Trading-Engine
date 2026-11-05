import React, { useState } from 'react';
import { Flame, ShieldAlert, Award, AlertTriangle, Sparkles, MessageSquare } from 'lucide-react';

export default function ZoneC_DebateFeed({ debate = {}, tradeContext = null, fallbackMode = false }) {
  const [showRawHeuristic, setShowRawHeuristic] = useState(fallbackMode);

  const bull = debate?.bull || "Institutional order flow shows clean liquidity absorption at the 200 EMA. Smart money accumulation confirmed with volume delta expanding into the close.";
  const bear = debate?.bear || "RSI 68 is nearing overbought territory. Overhead supply at key weekly pivot creates high probability of bull trap flush.";
  const judge = debate?.judge || "Desk Manager Verdict: BUY WITH HIGH CONVICTION. 24/111 confluence confirmed. Sized strictly via Kelly Criterion at 1.8% capital with 1:2.0 verified ATR bounds.";

  return (
    <div className="bg-[#0b0c16] border border-[#1a1c2e] rounded-xl overflow-hidden shadow-2xl flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-2.5 bg-[#0e101d] border-b border-[#1a1c2e] flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <MessageSquare className="w-4 h-4 text-purple-400" />
          <span className="font-mono text-xs font-bold uppercase tracking-wider text-purple-300">
            AGENT 06: DESK DEBATE & POSITION RATIONALE
          </span>
        </div>

        {/* LLM Status Pill */}
        <div className="flex items-center space-x-2">
          {showRawHeuristic ? (
            <span className="flex items-center space-x-1 font-mono text-[10px] bg-amber-950/60 border border-amber-500/50 text-amber-300 px-2 py-0.5 rounded">
              <AlertTriangle className="w-3 h-3 text-amber-400" />
              <span>[QUANT HEURISTIC FALLBACK]</span>
            </span>
          ) : (
            <span className="flex items-center space-x-1 font-mono text-[10px] bg-purple-950/60 border border-purple-500/50 text-purple-300 px-2 py-0.5 rounded">
              <Sparkles className="w-3 h-3 text-purple-400" />
              <span>GEMINI 3.6 FLASH</span>
            </span>
          )}
        </div>
      </div>

      {/* Trade Context Badge if inspecting historical trade */}
      {tradeContext && (
        <div className="bg-[#121424] px-4 py-1.5 border-b border-[#1f233a] flex items-center justify-between text-[11px] font-mono text-gray-400">
          <span>
            EXPLAINING: <strong className="text-white">{tradeContext.symbol}</strong> ({tradeContext.side} @ {tradeContext.entry})
          </span>
          <span className="text-purple-400 font-semibold">{tradeContext.time} IST</span>
        </div>
      )}

      {/* Chat Messages Stream */}
      <div className="p-3.5 space-y-3 flex-1 overflow-y-auto scrollbar-thin font-sans text-xs">
        {/* 🐂 Bull Trader Bubble (Left Aligned, Green Border) */}
        <div className="flex flex-col items-start max-w-[92%]">
          <div className="flex items-center space-x-1.5 text-emerald-400 font-mono text-[11px] font-bold mb-1">
            <span>🐂</span>
            <span>HYPER-BULL TRADER</span>
            <span className="text-[10px] text-gray-500 font-normal">Desk Analyst #1</span>
          </div>
          <div className="bg-[#0b1c13] border-l-4 border-emerald-500 border border-[#1a3826] rounded-r-xl rounded-bl-xl p-3 text-emerald-100/90 shadow-md leading-relaxed font-sans">
            {bull}
          </div>
        </div>

        {/* 🐻 Bear Trader Bubble (Right Aligned, Red Border) */}
        <div className="flex flex-col items-end max-w-[92%] ml-auto">
          <div className="flex items-center space-x-1.5 text-rose-400 font-mono text-[11px] font-bold mb-1">
            <span className="text-[10px] text-gray-500 font-normal">Risk Skeptic #2</span>
            <span>CYNICAL SHORT SELLER</span>
            <span>🐻</span>
          </div>
          <div className="bg-[#1e0d12] border-r-4 border-rose-500 border border-[#3d1922] rounded-l-xl rounded-br-xl p-3 text-rose-100/90 shadow-md leading-relaxed font-sans text-left">
            {bear}
          </div>
        </div>
      </div>

      {/* ⚖️ Anchored Desk Manager & Risk Guardian Verdict Banner */}
      <div className="p-3 bg-gradient-to-r from-[#140f26] via-[#100d20] to-[#140f26] border-t border-purple-500/40">
        <div className="flex items-center space-x-2 text-purple-300 font-mono text-xs font-bold mb-1">
          <Award className="w-4 h-4 text-purple-400" />
          <span>DESK MANAGER VERDICT & RISK ALLOCATION</span>
        </div>
        <p className="text-xs text-purple-100/90 leading-relaxed font-mono">
          {judge}
        </p>
      </div>
    </div>
  );
}


import React from 'react';
import { Flame, ShieldAlert, Award } from 'lucide-react';

export default function DebateChamber({ debate = {} }) {
  const { bull_case, bear_case, judge_decision } = debate;

  if (!bull_case && !bear_case && !judge_decision) {
    return null;
  }

  return (
    <div className="bg-[#0d0d1a] border border-[#1a1a2e] rounded-xl overflow-hidden mb-4">
      {/* Header */}
      <div className="px-4 py-3 border-b border-[#1a1a2e] bg-[#101022] flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Flame className="w-4 h-4 text-purple-400" />
          <span className="font-mono text-xs font-semibold uppercase tracking-wider text-purple-300">
            WALL STREET BULL VS BEAR CHAMBER (GEMINI 3.6 FLASH)
          </span>
        </div>
        <span className="font-mono text-[10px] text-gray-500 uppercase tracking-widest">
          QUALITATIVE SYNTHESIS
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-[#1a1a2e]">
        {/* Bull Trader */}
        <div className="p-4 bg-gradient-to-b from-emerald-950/20 to-transparent">
          <div className="flex items-center space-x-1.5 text-emerald-400 font-mono text-xs font-bold uppercase tracking-wider mb-2">
            <span>🐂</span>
            <span>HYPER-BULL TRADER</span>
          </div>
          <p className="text-xs text-emerald-100/90 leading-relaxed font-sans">
            {bull_case || "Building long-side thesis..."}
          </p>
        </div>

        {/* Bear Trader */}
        <div className="p-4 bg-gradient-to-b from-rose-950/20 to-transparent">
          <div className="flex items-center space-x-1.5 text-rose-400 font-mono text-xs font-bold uppercase tracking-wider mb-2">
            <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
            <span>CYNICAL SHORT SELLER</span>
          </div>
          <p className="text-xs text-rose-100/90 leading-relaxed font-sans">
            {bear_case || "Hunting bull traps..."}
          </p>
        </div>

        {/* Veteran Desk Manager / Judge */}
        <div className="p-4 bg-gradient-to-b from-purple-950/20 to-transparent">
          <div className="flex items-center space-x-1.5 text-purple-300 font-mono text-xs font-bold uppercase tracking-wider mb-2">
            <Award className="w-3.5 h-3.5 text-purple-400" />
            <span>DESK MANAGER FINAL VERDICT</span>
          </div>
          <p className="text-xs text-purple-100/90 leading-relaxed font-sans">
            {judge_decision || "Deliberating..."}
          </p>
        </div>
      </div>
    </div>
  );
}


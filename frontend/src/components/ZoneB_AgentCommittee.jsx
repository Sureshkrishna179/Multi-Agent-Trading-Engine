import React from 'react';
import { 
  ShieldCheck, ShieldAlert, Cpu, Sparkles, Scale, 
  Brain, Bot, Activity, CheckCircle2, AlertTriangle, Layers
} from 'lucide-react';

export default function ZoneB_AgentCommittee({ committeeData = {} }) {
  const consensus = committeeData.consensus || { score: 0.81, action: "STRONG BUY", strength: "VERY STRONG" };
  const risk = committeeData.agent_4_risk || { approved: true, status: "APPROVED", details: "Kelly 1.8% · Max 2% loss ceiling" };
  const tech = committeeData.agent_1_technical || {};
  const sent = committeeData.agent_2_sentiment || {};
  const strat = committeeData.agent_3_strategy || {};
  const fund = committeeData.agent_5_fundamental || {};
  const ml = committeeData.agent_7_ml || {};
  const opt = committeeData.agent_8_optimizer || {};

  const isApproved = risk.approved === true;
  const isBuy = consensus.action?.includes("BUY");
  const isSell = consensus.action?.includes("SELL");

  return (
    <div className="bg-[#0b0c16] border border-[#1a1c2e] rounded-xl p-3.5 shadow-2xl flex flex-col justify-between h-full space-y-3">
      {/* ── MASTER CARD: Consensus & Risk Guardian ── */}
      <div className={`rounded-xl p-3.5 border transition-all ${
        isApproved
          ? 'bg-gradient-to-br from-[#0c1f17] via-[#091510] to-[#0b0c16] border-emerald-500/50 shadow-[0_0_15px_#10b98122]'
          : 'bg-gradient-to-br from-[#260e14] via-[#1a0a0e] to-[#0b0c16] border-rose-500/50 shadow-[0_0_15px_#f43f5e22]'
      }`}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <span className="font-mono text-[10px] uppercase tracking-widest text-gray-400 font-semibold">
              WEIGHTED CONSENSUS
            </span>
          </div>
          <div className="flex items-center space-x-1.5">
            {isApproved ? (
              <span className="flex items-center space-x-1 text-emerald-400 font-mono text-[11px] font-bold bg-emerald-950/60 border border-emerald-500/60 px-2 py-0.5 rounded-full animate-pulse-bull">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>RISK APPROVED</span>
              </span>
            ) : (
              <span className="flex items-center space-x-1 text-rose-400 font-mono text-[11px] font-bold bg-rose-950/60 border border-rose-500/60 px-2 py-0.5 rounded-full animate-pulse-bear">
                <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
                <span>RISK VETOED</span>
              </span>
            )}
          </div>
        </div>

        <div className="flex items-baseline justify-between">
          <div className={`font-mono text-xl font-black tracking-wider ${
            isBuy ? 'text-emerald-400' : isSell ? 'text-rose-400' : 'text-gray-300'
          }`}>
            {consensus.action}
          </div>
          <div className="font-mono text-xs text-gray-400">
            Score: <strong className="text-white text-sm">{consensus.score > 0 ? `+${consensus.score.toFixed(2)}` : consensus.score?.toFixed(2)}</strong>
            <span className="text-gray-500 text-[10px]"> / 1.0</span>
          </div>
        </div>

        {/* Linear Consensus Bar */}
        <div className="w-full bg-[#151726] h-2 rounded-full overflow-hidden mt-2 relative">
          <div
            className={`h-full rounded-full transition-all duration-500 ${isBuy ? 'bg-emerald-400' : isSell ? 'bg-rose-500' : 'bg-gray-400'}`}
            style={{ width: `${Math.min(100, Math.max(10, Math.abs(consensus.score || 0.8) * 100))}%` }}
          />
        </div>
        <div className="flex justify-between text-[10px] font-mono text-gray-500 mt-1">
          <span>-1.0 MAX SHORT</span>
          <span className="text-purple-400 font-semibold">{consensus.strength}</span>
          <span>+1.0 MAX LONG</span>
        </div>
      </div>

      {/* ── 2x3 Grid of Agents ── */}
      <div className="grid grid-cols-2 gap-2 text-xs font-mono">
        {/* Agent 1: Technicals */}
        <div className="bg-[#0f1120] border border-[#1e2238] rounded-lg p-2.5 hover:border-cyan-500/40 transition-colors">
          <div className="flex items-center justify-between text-[10px] text-gray-400 mb-1">
            <span className="text-cyan-400 font-bold">01 TECH</span>
            <span className="text-emerald-400 font-semibold">{tech.regime || "BULLISH"}</span>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-gray-400">RSI (14)</span>
            <strong className="text-white text-sm">{tech.rsi || 64.2}</strong>
          </div>
          <div className="w-full bg-[#1b1e33] h-1.5 rounded-full overflow-hidden mt-1">
            <div className="bg-cyan-400 h-full rounded-full" style={{ width: `${tech.rsi || 64}%` }} />
          </div>
          <div className="text-[10px] text-gray-500 mt-1 flex justify-between">
            <span>MACD {tech.macd || "+14.8"}</span>
            <span>ADX {tech.adx || 31.4}</span>
          </div>
        </div>

        {/* Agent 2: Sentiment */}
        <div className="bg-[#0f1120] border border-[#1e2238] rounded-lg p-2.5 hover:border-purple-500/40 transition-colors">
          <div className="flex items-center justify-between text-[10px] text-gray-400 mb-1">
            <span className="text-purple-400 font-bold">02 SENTIMENT</span>
            <span className="text-emerald-400 font-semibold">{sent.label || "GREED"}</span>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-gray-400">Fear/Greed</span>
            <strong className="text-white text-sm">{sent.sentiment_index || 78}/100</strong>
          </div>
          <div className="w-full bg-[#1b1e33] h-1.5 rounded-full overflow-hidden mt-1">
            <div className="bg-purple-500 h-full rounded-full" style={{ width: `${sent.sentiment_index || 78}%` }} />
          </div>
          <div className="text-[10px] text-gray-500 mt-1 flex justify-between">
            <span>RSS + ISB</span>
            <span className="text-emerald-400">{sent.live_sources || "4/4 live"}</span>
          </div>
        </div>

        {/* Agent 3: Strategy Confluence */}
        <div className="bg-[#0f1120] border border-[#1e2238] rounded-lg p-2.5 hover:border-amber-500/40 transition-colors">
          <div className="flex items-center justify-between text-[10px] text-gray-400 mb-1">
            <span className="text-amber-400 font-bold">03 STRATEGIES</span>
            <span className="text-emerald-400 font-semibold">{strat.triggered_count || 24}/111</span>
          </div>
          <div className="text-white font-semibold text-xs truncate mt-0.5">
            {strat.top_pattern || "Bullish Engulfing"}
          </div>
          <div className="text-[10px] text-gray-500 mt-1">
            Confluence: <strong className="text-amber-300">{(strat.score || 0.85).toFixed(2)}</strong> / 1.0
          </div>
        </div>

        {/* Agent 5: Fundamentals */}
        <div className="bg-[#0f1120] border border-[#1e2238] rounded-lg p-2.5 hover:border-blue-500/40 transition-colors">
          <div className="flex items-center justify-between text-[10px] text-gray-400 mb-1">
            <span className="text-blue-400 font-bold">05 FUNDAMENTAL</span>
            <span className="text-cyan-400 font-semibold">{fund.label || "FAIR VALUE"}</span>
          </div>
          <div className="flex justify-between text-[11px] text-gray-300 mt-0.5">
            <span>P/E: <strong className="text-white">{fund.pe_ratio || "24.2"}</strong></span>
            <span>D/E: <strong className="text-white">{fund.de_ratio || "0.42"}</strong></span>
          </div>
          <div className="text-[10px] text-gray-500 mt-1">
            YoY Growth: <strong className="text-emerald-400">{fund.growth || "+14.8%"}</strong>
          </div>
        </div>

        {/* Agent 7: XGBoost ML Brain */}
        <div className="bg-[#0f1120] border border-[#1e2238] rounded-lg p-2.5 hover:border-emerald-500/40 transition-colors">
          <div className="flex items-center justify-between text-[10px] text-gray-400 mb-1">
            <span className="text-emerald-400 font-bold">07 ML BRAIN</span>
            <span className="text-emerald-400 font-semibold">{ml.drift_status || "HEALTHY"}</span>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-gray-400">Direction Prob</span>
            <strong className="text-white text-sm">{ml.probability || 84.2}%</strong>
          </div>
          <div className="w-full bg-[#1b1e33] h-1.5 rounded-full overflow-hidden mt-1">
            <div className="bg-emerald-400 h-full rounded-full" style={{ width: `${ml.probability || 84}%` }} />
          </div>
          <div className="text-[10px] text-gray-500 mt-1 flex justify-between">
            <span>XGBoost Acc</span>
            <span className="text-emerald-400">{ml.accuracy || "68.4%"}</span>
          </div>
        </div>

        {/* Agent 8: Alpha Optimizer */}
        <div className="bg-[#0f1120] border border-[#1e2238] rounded-lg p-2.5 hover:border-violet-500/40 transition-colors">
          <div className="flex items-center justify-between text-[10px] text-gray-400 mb-1">
            <span className="text-violet-400 font-bold">08 OPTIMIZER</span>
            <span className="text-emerald-400 font-semibold">{opt.win_rate || "58.4%"}</span>
          </div>
          <div className="text-white font-semibold text-xs mt-0.5">
            Pruned {opt.pruned || 14} Losers
          </div>
          <div className="text-[10px] text-gray-500 mt-1 flex justify-between">
            <span>30D Backtest</span>
            <span className="text-purple-400">0% CPU (Cached)</span>
          </div>
        </div>
      </div>
    </div>
  );
}


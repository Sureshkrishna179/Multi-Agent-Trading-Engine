import React from 'react';
import { Bot, Cpu, Shield, Brain, Sparkles, Scale, Gauge, HelpCircle } from 'lucide-react';

const AGENT_CONFIGS = {
  agent_1_technical: { icon: Gauge, label: "01 Technical Observer", defaultWeight: "20%" },
  agent_2_sentiment: { icon: Sparkles, label: "02 Sentiment Engine", defaultWeight: "10%" },
  agent_3_strategy: { icon: Cpu, label: "03 Strategy Selector", defaultWeight: "15%" },
  agent_4_risk: { icon: Shield, label: "04 Risk Guardian", defaultWeight: "VETO" },
  agent_5_fundamental: { icon: Scale, label: "05 Fundamental Analyst", defaultWeight: "10%" },
  agent_6_debate: { icon: HelpCircle, label: "06 Bull/Bear Judge", defaultWeight: "10%" },
  agent_7_ml: { icon: Brain, label: "07 ML Brain (XGBoost)", defaultWeight: "25%" },
  agent_8_optimizer: { icon: Bot, label: "08 Alpha Optimizer", defaultWeight: "10%" },
};

export default function AgentPanel({ agentVotes = {}, mlHealth = {} }) {
  const votesList = Object.entries(agentVotes);

  return (
    <div className="bg-[#0d0d1a] border border-[#1a1a2e] rounded-xl overflow-hidden mb-4">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[#1a1a2e] bg-[#101022]">
        <div className="flex items-center space-x-2">
          <Bot className="w-4 h-4 text-purple-400" />
          <span className="font-mono text-xs font-semibold uppercase tracking-wider text-purple-300">
            8-AGENT CONSENSUS DESK
          </span>
        </div>
        <div className="font-mono text-[11px] text-gray-400">
          HEALTH: <span className="text-emerald-400">{mlHealth?.status || "HEALTHY"}</span> ({mlHealth?.accuracy_pct || "N/A"})
        </div>
      </div>

      {/* Agents List Table */}
      <div className="divide-y divide-[#151526]">
        {votesList.length === 0 ? (
          <div className="p-6 text-center text-gray-500 font-mono text-xs">
            Run an asset scan to activate the 8 agents.
          </div>
        ) : (
          votesList.map(([agentId, vote]) => {
            const signal = vote.signal || 0;
            const weight = vote.weight || 0;
            const isAbstain = weight === 0;

            let dotColor = "bg-gray-500";
            let voteLabel = "— HOLD";
            let voteColor = "text-gray-400";

            if (isAbstain) {
              dotColor = "bg-gray-700";
              voteLabel = "✕ ABSTAIN";
              voteColor = "text-gray-500";
            } else if (signal > 0.05) {
              dotColor = "bg-emerald-400 shadow-[0_0_8px_#34d399]";
              voteLabel = "▲ BULL";
              voteColor = "text-emerald-400";
            } else if (signal < -0.05) {
              dotColor = "bg-rose-500 shadow-[0_0_8px_#f43f5e]";
              voteLabel = "▼ BEAR";
              voteColor = "text-rose-400";
            }

            const cfg = AGENT_CONFIGS[agentId] || { icon: Bot, label: vote.name, defaultWeight: "10%" };
            const Icon = cfg.icon;

            return (
              <div
                key={agentId}
                className="px-4 py-2.5 flex items-center justify-between hover:bg-[#121224] transition-colors"
              >
                {/* Left: Dot & Name */}
                <div className="flex items-center space-x-2.5 min-w-[180px]">
                  <div className={`w-2 h-2 rounded-full ${dotColor}`} />
                  <Icon className="w-3.5 h-3.5 text-gray-500" />
                  <span className="font-mono text-xs text-gray-200">
                    {vote.name || cfg.label}
                  </span>
                </div>

                {/* Vote Direction */}
                <div className={`font-mono text-xs font-semibold ${voteColor} min-w-[75px]`}>
                  {voteLabel}
                </div>

                {/* Raw Context / Metric */}
                <div className="font-mono text-[11px] text-gray-500 flex-1 truncate px-3 hidden lg:block">
                  {vote.raw_data || "No diagnostic telemetry"}
                </div>

                {/* Weight */}
                <div className="font-mono text-[10px] text-gray-400 bg-[#16162a] border border-[#23233c] px-2 py-0.5 rounded">
                  {isAbstain ? "0% (ABSTAIN)" : `${(weight * 100).toFixed(0)}% WT`}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}


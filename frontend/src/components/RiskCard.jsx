import React from 'react';
import { ShieldCheck, ShieldX, Crosshair, AlertTriangle } from 'lucide-react';

export default function RiskCard({ risk = {}, currency = "₹" }) {
  if (!risk || Object.keys(risk).length === 0) return null;

  const isApproved = risk.approved === true;
  const positionSize = risk.position_size || 0;
  const riskAmount = risk.risk_amount || 0;
  const stopLoss = risk.stop_loss || 0;
  const takeProfit = risk.take_profit || 0;
  const vetoReasons = risk.veto_reasons || [];

  return (
    <div className={`border rounded-xl p-4 mb-4 font-mono transition-all ${
      isApproved
        ? 'bg-emerald-950/20 border-emerald-500/40 text-emerald-300'
        : 'bg-rose-950/20 border-rose-500/40 text-rose-300'
    }`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          {isApproved ? (
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
          ) : (
            <ShieldX className="w-5 h-5 text-rose-400" />
          )}
          <span className="font-bold text-xs uppercase tracking-wider">
            AGENT 04: RISK GUARDIAN GATEKEEPER
          </span>
        </div>
        <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded border ${
          isApproved
            ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50'
            : 'bg-rose-500/20 text-rose-400 border-rose-500/50'
        }`}>
          {isApproved ? 'VERIFIED & APPROVED' : 'HARD VETO EXERCISED'}
        </span>
      </div>

      {isApproved ? (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs mt-3 pt-3 border-t border-emerald-900/40 text-gray-300">
          <div>
            <span className="text-gray-500 block text-[10px]">POSITION ALLOCATED</span>
            <strong className="text-emerald-400 text-sm">{positionSize} Units</strong>
          </div>
          <div>
            <span className="text-gray-500 block text-[10px]">CAPITAL AT RISK</span>
            <strong className="text-white text-sm">{currency}{riskAmount.toLocaleString(undefined, { minimumFractionDigits: 2 })}</strong>
          </div>
          <div>
            <span className="text-gray-500 block text-[10px]">DYNAMIC STOP-LOSS</span>
            <strong className="text-rose-400 text-sm">{currency}{stopLoss.toLocaleString(undefined, { minimumFractionDigits: 2 })}</strong>
          </div>
          <div>
            <span className="text-gray-500 block text-[10px]">TAKE-PROFIT (1:2 R:R)</span>
            <strong className="text-emerald-400 text-sm">{currency}{takeProfit.toLocaleString(undefined, { minimumFractionDigits: 2 })}</strong>
          </div>
        </div>
      ) : (
        <div className="mt-2 text-xs">
          <div className="flex items-center space-x-1.5 text-rose-400 font-semibold mb-1">
            <AlertTriangle className="w-4 h-4" />
            <span>VETO SAFEGUARD TRIGGERED:</span>
          </div>
          <ul className="list-disc list-inside space-y-0.5 text-rose-200/90 pl-1">
            {vetoReasons.map((reason, idx) => (
              <li key={idx}>{reason}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}


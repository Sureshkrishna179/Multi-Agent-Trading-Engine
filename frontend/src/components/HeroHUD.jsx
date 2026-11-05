import React from 'react';
import { ArrowUpRight, ArrowDownRight, Wallet, TrendingUp, Layers, CheckCircle2 } from 'lucide-react';

export default function HeroHUD({ portfolio, currency = "₹" }) {
  const capital = portfolio?.available_capital || 0;
  const pnl = portfolio?.daily_pnl || 0;
  const positions = portfolio?.open_positions || 0;
  const trades = portfolio?.total_trades || 0;
  const isPositive = pnl >= 0;
  const pnlPercent = capital > 0 ? (pnl / capital) * 100 : 0;

  return (
    <div className="bg-gradient-to-r from-[#0d0d1a] via-[#120d24] to-[#0d0d1a] border border-[#231b40] rounded-xl p-4 sm:p-5 mb-4 shadow-xl">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 items-center">
        {/* Available Capital */}
        <div>
          <div className="flex items-center space-x-1.5 text-gray-500 font-mono text-[11px] uppercase tracking-wider mb-1">
            <Wallet className="w-3.5 h-3.5 text-purple-400" />
            <span>Available Capital</span>
          </div>
          <div className="font-mono text-2xl sm:text-3xl font-bold text-white tracking-tight">
            {currency}{capital.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
          </div>
          <div className="text-[11px] text-gray-400 font-mono mt-0.5">
            Paper Trading Vault
          </div>
        </div>

        {/* Daily PnL */}
        <div>
          <div className="flex items-center space-x-1.5 text-gray-500 font-mono text-[11px] uppercase tracking-wider mb-1">
            <TrendingUp className="w-3.5 h-3.5 text-purple-400" />
            <span>Daily Net PnL</span>
          </div>
          <div className={`font-mono text-2xl sm:text-3xl font-bold tracking-tight flex items-center space-x-1 ${
            isPositive ? 'text-emerald-400' : 'text-rose-400'
          }`}>
            <span>{isPositive ? '+' : ''}{currency}{pnl.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
            {isPositive ? (
              <ArrowUpRight className="w-5 h-5 text-emerald-400 inline" />
            ) : (
              <ArrowDownRight className="w-5 h-5 text-rose-400 inline" />
            )}
          </div>
          <div className={`text-[11px] font-mono mt-0.5 ${isPositive ? 'text-emerald-500' : 'text-rose-500'}`}>
            {isPositive ? '+' : ''}{pnlPercent.toFixed(2)}% ROI Today
          </div>
        </div>

        {/* Open Positions */}
        <div>
          <div className="flex items-center space-x-1.5 text-gray-500 font-mono text-[11px] uppercase tracking-wider mb-1">
            <Layers className="w-3.5 h-3.5 text-purple-400" />
            <span>Active Positions</span>
          </div>
          <div className="font-mono text-2xl sm:text-3xl font-bold text-white tracking-tight">
            {positions}
          </div>
          <div className="text-[11px] text-gray-400 font-mono mt-0.5">
            Max 2% Risk / Position
          </div>
        </div>

        {/* Total Trades & Drawdown Bar */}
        <div>
          <div className="flex items-center space-x-1.5 text-gray-500 font-mono text-[11px] uppercase tracking-wider mb-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-purple-400" />
            <span>Total Executed</span>
          </div>
          <div className="font-mono text-2xl sm:text-3xl font-bold text-gray-200 tracking-tight">
            {trades} <span className="text-sm font-normal text-gray-500">Trades</span>
          </div>
          {/* Max Daily Drawdown Protection Meter */}
          <div className="mt-1.5">
            <div className="flex justify-between text-[10px] font-mono text-gray-400 mb-0.5">
              <span>Risk Ceiling</span>
              <span>6.0% Max DD</span>
            </div>
            <div className="w-full bg-[#1e1e30] h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-purple-500 h-full rounded-full transition-all"
                style={{ width: `${Math.min(100, (Math.abs(pnlPercent) / 6.0) * 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


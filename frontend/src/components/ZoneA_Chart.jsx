import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, LineStyle } from 'lightweight-charts';
import { BarChart3, TrendingUp, TrendingDown, Clock, ShieldCheck, Crosshair, XCircle } from 'lucide-react';

export default function ZoneA_Chart({
  candles = [],
  activeAsset,
  selectedTrade,
  onClearSelectedTrade,
  market = "NSE",
  currency = "₹",
  latency = "1.84s"
}) {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const seriesRef = useRef(null);
  const priceLinesRef = useRef([]);

  const isPositive = (activeAsset?.change || 0) >= 0;

  // Initialize TradingView Lightweight Chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#090a12' },
        textColor: '#8e96a8',
        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: '#131422' },
        horzLines: { color: '#131422' },
      },
      crosshair: {
        mode: 1,
        vertLine: { color: '#00d4ff', width: 1, style: LineStyle.Dashed },
        horzLine: { color: '#00d4ff', width: 1, style: LineStyle.Dashed },
      },
      timeScale: {
        borderColor: '#1e2235',
        timeVisible: true,
        secondsVisible: false,
      },
      rightPriceScale: {
        borderColor: '#1e2235',
        scaleMargins: {
          top: 0.1,
          bottom: 0.2,
        },
      },
      width: chartContainerRef.current.clientWidth,
      height: 380,
    });

    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    });

    chartRef.current = chart;
    seriesRef.current = candlestickSeries;

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  // Sync Candlesticks, Trade Overlay Lines (Entry, SL, TP) & Markers
  useEffect(() => {
    if (!seriesRef.current || !candles.length) return;

    // Load Candlesticks
    const formatted = candles
      .map(c => ({
        time: c.time,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      }))
      .sort((a, b) => (a.time > b.time ? 1 : -1));

    seriesRef.current.setData(formatted);

    // Clear existing price lines
    priceLinesRef.current.forEach(line => {
      try {
        seriesRef.current.removePriceLine(line);
      } catch {
        // ignore
      }
    });
    priceLinesRef.current = [];

    // If a trade is clicked/selected, draw the Entry, Stop-Loss, and Take-Profit lines!
    if (selectedTrade && selectedTrade.entry > 0) {
      // 1. Entry Line (Solid Cyan / White)
      const entryLine = seriesRef.current.createPriceLine({
        price: selectedTrade.entry,
        color: '#00d4ff',
        lineWidth: 2,
        lineStyle: LineStyle.Solid,
        axisLabelVisible: true,
        title: `ENTRY ${currency}${selectedTrade.entry.toFixed(2)}`,
      });
      priceLinesRef.current.push(entryLine);

      // 2. Dynamic ATR Stop-Loss Line (Dashed Red with SL label)
      if (selectedTrade.sl > 0) {
        const slLine = seriesRef.current.createPriceLine({
          price: selectedTrade.sl,
          color: '#ef4444',
          lineWidth: 2,
          lineStyle: LineStyle.Dashed,
          axisLabelVisible: true,
          title: `ATR SL ${currency}${selectedTrade.sl.toFixed(2)} (-2% MAX RISK)`,
        });
        priceLinesRef.current.push(slLine);
      }

      // 3. Take-Profit Target Line (Dashed Green with TP label)
      if (selectedTrade.tp > 0) {
        const tpLine = seriesRef.current.createPriceLine({
          price: selectedTrade.tp,
          color: '#22c55e',
          lineWidth: 2,
          lineStyle: LineStyle.Dashed,
          axisLabelVisible: true,
          title: `TAKE-PROFIT ${currency}${selectedTrade.tp.toFixed(2)} (${selectedTrade.rr || "1:2 R:R"})`,
        });
        priceLinesRef.current.push(tpLine);
      }

      // Add precise Trade marker
      const lastCandle = formatted[formatted.length - 1];
      seriesRef.current.setMarkers([
        {
          time: lastCandle.time,
          position: selectedTrade.side === "LONG" ? "belowBar" : "aboveBar",
          color: selectedTrade.side === "LONG" ? "#22c55e" : "#ef4444",
          shape: selectedTrade.side === "LONG" ? "arrowUp" : "arrowDown",
          text: `BOT ${selectedTrade.side} @ ${currency}${selectedTrade.entry.toFixed(2)}`,
        }
      ]);
    } else {
      // Default markers for recent signals
      const lastCandle = formatted[formatted.length - 1];
      seriesRef.current.setMarkers([
        {
          time: lastCandle.time,
          position: "belowBar",
          color: "#22c55e",
          shape: "arrowUp",
          text: "BOT BUY",
        }
      ]);
    }

    chartRef.current.timeScale().fitContent();
  }, [candles, selectedTrade, currency]);

  const latest = candles.length > 0 ? candles[candles.length - 1] : null;

  return (
    <div className="bg-[#0b0c16] border border-[#1a1c2e] rounded-xl overflow-hidden shadow-2xl flex flex-col h-full">
      {/* Top Asset & Ticker Telemetry Strip */}
      <div className="px-4 py-3 bg-[#0e101d] border-b border-[#1a1c2e] flex flex-wrap items-center justify-between gap-3">
        {/* Left: Asset Identifier */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <BarChart3 className="w-4 h-4 text-cyan-400" />
            <span className="font-mono text-base font-bold text-white tracking-wide">
              {activeAsset?.symbol || "RELIANCE.NS"}
            </span>
          </div>
          <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-[#181a2e] text-cyan-300 border border-cyan-500/30 font-semibold">
            {market}
          </span>
          <span className="text-gray-600">|</span>
          <span className="font-mono text-xs text-gray-400 hidden sm:inline">
            60-DAY OHLCV
          </span>
        </div>

        {/* Center: Live Price & 24H Delta */}
        <div className="flex items-center space-x-4 font-mono">
          <div className="text-right">
            <div className="text-lg font-bold text-white tracking-tight">
              {currency}{activeAsset?.price ? activeAsset.price.toLocaleString(undefined, { minimumFractionDigits: 2 }) : "2,984.50"}
            </div>
            <div className={`text-xs font-semibold flex items-center justify-end space-x-0.5 ${isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
              {isPositive ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
              <span>{isPositive ? '+' : ''}{(activeAsset?.change || 1.84).toFixed(2)}%</span>
            </div>
          </div>

          {/* DAG Pipeline Speed */}
          <div className="hidden md:flex items-center space-x-1.5 bg-[#141628] border border-purple-500/30 px-2.5 py-1 rounded text-purple-300 text-xs">
            <Clock className="w-3.5 h-3.5 text-purple-400" />
            <span>DAG: <strong>{latency}</strong></span>
          </div>
        </div>
      </div>

      {/* Selected Trade Inspection Banner (Active if row clicked) */}
      {selectedTrade && (
        <div className="bg-gradient-to-r from-cyan-950/40 via-[#0e1726] to-cyan-950/40 border-b border-cyan-500/40 px-4 py-2 flex items-center justify-between text-xs font-mono animate-fade-up">
          <div className="flex items-center space-x-3 text-cyan-200">
            <Crosshair className="w-4 h-4 text-cyan-400 animate-spin" />
            <span>
              AUDITING POSITION: <strong>{selectedTrade.symbol}</strong> ({selectedTrade.side}) · 
              Entry: <strong className="text-white">{currency}{selectedTrade.entry.toFixed(2)}</strong> · 
              SL: <strong className="text-rose-400">{currency}{selectedTrade.sl?.toFixed(2) || "None"}</strong> · 
              TP: <strong className="text-emerald-400">{currency}{selectedTrade.tp?.toFixed(2) || "None"}</strong>
            </span>
          </div>
          <button
            onClick={onClearSelectedTrade}
            className="flex items-center space-x-1 text-gray-400 hover:text-white bg-[#141628] px-2 py-0.5 rounded border border-gray-700 transition-colors"
          >
            <XCircle className="w-3.5 h-3.5 text-rose-400" />
            <span>RESET VIEW</span>
          </button>
        </div>
      )}

      {/* Candlestick Canvas Container */}
      <div ref={chartContainerRef} className="w-full flex-1 relative min-h-[360px]" />

      {/* OHLC Bar Footer */}
      {latest && (
        <div className="px-4 py-2 bg-[#0c0d18] border-t border-[#1a1c2e] flex items-center justify-between text-[11px] font-mono text-gray-400">
          <div className="flex space-x-4">
            <span>O: <strong className="text-gray-200">{currency}{latest.open}</strong></span>
            <span>H: <strong className="text-emerald-400">{currency}{latest.high}</strong></span>
            <span>L: <strong className="text-rose-400">{currency}{latest.low}</strong></span>
            <span>C: <strong className="text-white font-bold">{currency}{latest.close}</strong></span>
          </div>
          <div className="text-gray-500">
            VOL: <strong className="text-cyan-400">{latest.volume.toLocaleString()}</strong>
          </div>
        </div>
      )}
    </div>
  );
}


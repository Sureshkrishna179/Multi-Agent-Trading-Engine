import React, { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';
import { BarChart2 } from 'lucide-react';

export default function TradingChart({ candles = [], symbol, action, currency = "₹" }) {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const seriesRef = useRef(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Initialize Lightweight Chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#0d0d1a' },
        textColor: '#9ca3af',
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: '#151526' },
        horzLines: { color: '#151526' },
      },
      crosshair: {
        mode: 1,
        vertLine: { color: '#7c3aed', width: 1, style: 2 },
        horzLine: { color: '#7c3aed', width: 1, style: 2 },
      },
      timeScale: {
        borderColor: '#1e1e32',
        timeVisible: true,
        secondsVisible: false,
      },
      rightPriceScale: {
        borderColor: '#1e1e32',
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

    // Handle Window Resizing
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

  // Update chart data whenever candles change
  useEffect(() => {
    if (!seriesRef.current || !candles.length) return;

    // Format and sort candles by time ascending
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

    // If there is an actionable trade signal, add a TradingView visual marker to the latest candle
    if (action && (action === "BUY" || action === "SELL") && formatted.length > 0) {
      const lastCandle = formatted[formatted.length - 1];
      seriesRef.current.setMarkers([
        {
          time: lastCandle.time,
          position: action === "BUY" ? 'belowBar' : 'aboveBar',
          color: action === "BUY" ? '#22c55e' : '#ef4444',
          shape: action === "BUY" ? 'arrowUp' : 'arrowDown',
          text: `BOT ${action}`,
        },
      ]);
    } else {
      seriesRef.current.setMarkers([]);
    }

    if (chartRef.current) {
      chartRef.current.timeScale().fitContent();
    }
  }, [candles, action]);

  const latestCandle = candles.length > 0 ? candles[candles.length - 1] : null;

  return (
    <div className="bg-[#0d0d1a] border border-[#1a1a2e] rounded-xl overflow-hidden mb-4">
      {/* Chart Header Bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[#1a1a2e] bg-[#101022]">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1.5 text-purple-400 font-mono text-xs font-semibold">
            <BarChart2 className="w-4 h-4" />
            <span>{symbol || "ASSET CHART"}</span>
          </div>
          <span className="text-gray-600">|</span>
          <span className="font-mono text-xs text-gray-400">DAILY CANDLES (60D)</span>
        </div>

        {latestCandle && (
          <div className="flex items-center space-x-3 font-mono text-xs">
            <span className="text-gray-500">O: <strong className="text-gray-300">{currency}{latestCandle.open}</strong></span>
            <span className="text-gray-500">H: <strong className="text-emerald-400">{currency}{latestCandle.high}</strong></span>
            <span className="text-gray-500">L: <strong className="text-rose-400">{currency}{latestCandle.low}</strong></span>
            <span className="text-gray-500">C: <strong className="text-white font-bold">{currency}{latestCandle.close}</strong></span>
          </div>
        )}
      </div>

      {/* Candlestick Canvas Container */}
      <div ref={chartContainerRef} className="w-full relative min-h-[380px]" />
    </div>
  );
}


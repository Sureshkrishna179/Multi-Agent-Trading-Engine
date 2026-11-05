import React, { useEffect, useRef } from 'react';
import { Terminal, Trash2 } from 'lucide-react';

export default function TerminalLogs({ logs = [], onClear }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="bg-[#090912] border border-[#1a1a2e] rounded-xl overflow-hidden mb-4">
      <div className="flex items-center justify-between px-4 py-2.5 bg-[#0e0e1a] border-b border-[#1a1a2e]">
        <div className="flex items-center space-x-2">
          <Terminal className="w-3.5 h-3.5 text-purple-400" />
          <span className="font-mono text-xs font-semibold text-purple-300 uppercase tracking-wider">
            DAEMON WEBSOCKET EVENT STREAM
          </span>
        </div>
        <button
          onClick={onClear}
          className="text-gray-500 hover:text-gray-300 transition-colors"
          title="Clear logs"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>

      <div
        ref={scrollRef}
        className="p-3 max-h-48 overflow-y-auto font-mono text-[11px] leading-relaxed space-y-1 scrollbar-thin select-text bg-[#07070e]"
      >
        {logs.length === 0 ? (
          <div className="text-gray-600 italic">Listening for background events from daemon...</div>
        ) : (
          logs.map((log, index) => {
            const isError = log.type === "ERROR" || log.message?.includes("❌");
            const isSuccess = log.type === "SUCCESS" || log.message?.includes("✅");
            const isWarn = log.type === "WARN" || log.message?.includes("⚠️");

            return (
              <div key={index} className="flex items-start space-x-2">
                <span className="text-gray-600 flex-shrink-0 select-none">[{log.time || "LOG"}]</span>
                <span
                  className={
                    isError
                      ? "text-rose-400"
                      : isSuccess
                      ? "text-emerald-400"
                      : isWarn
                      ? "text-amber-400"
                      : "text-gray-400"
                  }
                >
                  {log.message}
                </span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}


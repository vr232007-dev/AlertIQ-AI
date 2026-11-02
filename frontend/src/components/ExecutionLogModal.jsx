import React from 'react';
import { X, Clock, Zap, DollarSign, Terminal, CheckCircle2, AlertOctagon, Info, AlertTriangle } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

export function ExecutionLogModal({ isOpen, onClose, execution }) {
  if (!isOpen || !execution) return null;

  const logs = execution.logs || [];
  const cost = execution.estimated_cost_usd !== undefined ? `$${Number(execution.estimated_cost_usd).toFixed(5)}` : '$0.00000';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
      <div className="bg-navy-900 border border-navy-700 rounded-xl w-full max-w-3xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-navy-800 bg-navy-850 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <Terminal className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-semibold text-white">{execution.task_name}</h3>
                <StatusBadge type="execution-status" value={execution.status} />
              </div>
              <p className="text-xs text-slate-400">
                Agent: <span className="text-slate-200 font-medium">{execution.agent_name || execution.agent_id}</span> | ID: <span className="font-mono text-cyan-300">{execution.execution_id}</span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-navy-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Telemetry Bar */}
        <div className="px-6 py-3 border-b border-navy-800 bg-navy-950 flex flex-wrap items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-1.5 text-slate-300">
            <Clock className="w-4 h-4 text-cyan-400" />
            <span>Duration: <strong className="text-white font-mono">{execution.duration_ms || 0} ms</strong></span>
          </div>

          <div className="flex items-center gap-1.5 text-slate-300">
            <Zap className="w-4 h-4 text-amber-400" />
            <span>Tokens: <strong className="text-white font-mono">{execution.tokens_total || 0}</strong> ({execution.tokens_prompt || 0} in / {execution.tokens_completion || 0} out)</span>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 text-slate-300">
              <DollarSign className="w-4 h-4 text-emerald-400" />
              <span>Est. Cost: <strong className="text-emerald-400 font-mono">{cost}</strong></span>
            </div>
            <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-navy-800 text-cyan-300 border border-navy-700">
              {execution.cost_mode || 'ESTIMATED_TELEMETRY'}
            </span>
          </div>
        </div>

        {/* Body Content */}
        <div className="p-6 overflow-y-auto space-y-5 flex-1">
          {/* Error banner if failed */}
          {execution.error_message && (
            <div className="p-3.5 rounded-lg bg-red-950/80 border border-red-500/40 text-xs text-red-200 flex items-start gap-2.5">
              <AlertOctagon className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-red-300">Execution Error</p>
                <p className="font-mono text-red-300/90 mt-0.5">{execution.error_message}</p>
              </div>
            </div>
          )}

          {/* Audit Logs Console */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-2">
              <Terminal className="w-3.5 h-3.5 text-cyan-400" />
              <span>Step-by-Step Execution Logs</span>
            </h4>
            <div className="bg-navy-950 border border-navy-800 rounded-lg p-3 font-mono text-xs space-y-2 max-h-56 overflow-y-auto">
              {logs.length === 0 ? (
                <p className="text-slate-400 text-center py-4">No log entries recorded for this task.</p>
              ) : (
                logs.map((log) => {
                  const levelColors = {
                    INFO: 'text-cyan-400',
                    WARNING: 'text-amber-400',
                    ERROR: 'text-red-400',
                    DECISION: 'text-emerald-400',
                  };
                  return (
                    <div key={log.id} className="flex items-start gap-2">
                      <span className="text-slate-400 text-[11px] shrink-0">
                        {log.timestamp ? log.timestamp.split(' ')[1] : ''}
                      </span>
                      <span className={`text-[11px] font-bold shrink-0 ${levelColors[log.level] || 'text-slate-300'}`}>
                        [{log.level}]
                      </span>
                      <span className="text-slate-200 leading-relaxed break-all">
                        {log.message}
                      </span>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Input & Output Payloads */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Input Payload</h4>
              <pre className="bg-navy-950 border border-navy-800 rounded-lg p-3 text-[11px] font-mono text-slate-300 overflow-x-auto max-h-40">
                {JSON.stringify(execution.input_payload || {}, null, 2)}
              </pre>
            </div>
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Output Result</h4>
              <pre className="bg-navy-950 border border-navy-800 rounded-lg p-3 text-[11px] font-mono text-emerald-300 overflow-x-auto max-h-40">
                {JSON.stringify(execution.output_result || {}, null, 2)}
              </pre>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-navy-800 bg-navy-850 flex items-center justify-between text-xs text-slate-400">
          <span>Started: {execution.started_at}</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-navy-700 hover:bg-navy-600 text-white font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

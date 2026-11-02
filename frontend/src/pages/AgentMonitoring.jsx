import React, { useState } from 'react';
import {
  Activity,
  Zap,
  DollarSign,
  Clock,
  CheckCircle2,
  XCircle,
  Terminal,
  Eye,
  Filter,
  Search
} from 'lucide-react';
import { StatCard } from '../components/StatCard';
import { StatusBadge } from '../components/StatusBadge';

export function AgentMonitoring({
  metrics,
  executions,
  onInspectExecution,
  onFilterChange
}) {
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  const totalExecs = metrics?.total_executions || 0;
  const successExecs = metrics?.successful_executions || 0;
  const failExecs = metrics?.failed_executions || 0;
  const waitingApproval = metrics?.waiting_approval || 0;
  const successRate = totalExecs > 0 ? Math.round((successExecs / totalExecs) * 100) : 100;
  const totalTokens = metrics?.total_tokens || 0;
  const totalCost = metrics?.total_cost_usd !== undefined ? `$${Number(metrics.total_cost_usd).toFixed(5)}` : '$0.00000';
  const avgDuration = metrics?.avg_duration_ms || 0;

  const filteredExecutions = executions.filter((item) => {
    const matchesStatus = statusFilter === 'ALL' || item.status === statusFilter;
    const matchesSearch =
      !searchTerm ||
      (item.task_name && item.task_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (item.agent_name && item.agent_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (item.execution_id && item.execution_id.toLowerCase().includes(searchTerm.toLowerCase()));
    return matchesStatus && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Telemetry Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Agent Executions"
          value={totalExecs.toLocaleString()}
          subtitle={`${successRate}% execution success rate`}
          icon={Activity}
          color="blue"
        />

        <StatCard
          title="Token Usage"
          value={totalTokens.toLocaleString()}
          subtitle="Prompt & completion tokens"
          icon={Zap}
          color="cyan"
        />

        <div className="bg-navy-900 border border-navy-700/60 rounded-xl p-5 hover:border-navy-600 transition-all shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-1.5 mb-1">
                <p className="text-xs font-medium uppercase tracking-wider text-slate-400">Estimated Cost</p>
                <span className="px-1.5 py-0.2 rounded text-[9px] font-semibold bg-navy-800 text-cyan-300 border border-navy-700">
                  ESTIMATED
                </span>
              </div>
              <h3 className="text-2xl font-bold text-emerald-400 font-mono tracking-tight">{totalCost}</h3>
              <p className="text-xs text-slate-400 mt-1">Telemetry-based inference cost</p>
            </div>
            <div className="p-2.5 rounded-lg border border-emerald-500/20 bg-emerald-500/5 text-emerald-400">
              <DollarSign className="w-5 h-5" />
            </div>
          </div>
        </div>

        <StatCard
          title="Average Latency"
          value={`${avgDuration} ms`}
          subtitle={`${failExecs} failed runs / ${waitingApproval} waiting`}
          icon={Clock}
          color={failExecs > 0 ? "orange" : "green"}
        />
      </div>

      {/* Execution History Table */}
      <div className="bg-navy-900 border border-navy-800 rounded-xl p-5 space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-white">Agent Execution Stream</h3>
            <p className="text-xs text-slate-400">Real-time task runs, status transitions, and duration metrics</p>
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            {/* Search */}
            <div className="relative flex-1 sm:w-48">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
              <input
                type="text"
                placeholder="Search tasks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-navy-950 border border-navy-700 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
              />
            </div>

            {/* Status Filter */}
            <div className="flex items-center gap-1 bg-navy-950 p-1 rounded-lg border border-navy-800 text-xs">
              {['ALL', 'SUCCESS', 'FAILED', 'WAITING_APPROVAL'].map((s) => (
                <button
                  key={s}
                  onClick={() => setStatusFilter(s)}
                  className={`px-2.5 py-1 rounded text-[11px] font-medium transition-colors ${
                    statusFilter === s
                      ? 'bg-navy-800 text-cyan-300 font-semibold'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {s === 'WAITING_APPROVAL' ? 'APPROVALS' : s}
                </button>
              ))}
            </div>
          </div>
        </div>

        {filteredExecutions.length === 0 ? (
          <div className="py-12 text-center text-xs text-slate-400 border border-dashed border-navy-800 rounded-lg">
            No agent executions found matching criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-navy-800 text-slate-400">
                  <th className="pb-2.5 font-medium">Execution ID</th>
                  <th className="pb-2.5 font-medium">Task Name</th>
                  <th className="pb-2.5 font-medium">Assigned Agent</th>
                  <th className="pb-2.5 font-medium">Status</th>
                  <th className="pb-2.5 font-medium">Latency</th>
                  <th className="pb-2.5 font-medium">Tokens</th>
                  <th className="pb-2.5 font-medium">Est. Cost</th>
                  <th className="pb-2.5 font-medium text-right">Logs</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-800/60">
                {filteredExecutions.map((row) => (
                  <tr key={row.execution_id} className="hover:bg-navy-850/60 transition-colors">
                    <td className="py-2.5 font-mono text-[11px] text-cyan-400">{row.execution_id}</td>
                    <td className="py-2.5 font-medium text-white max-w-[200px] truncate">{row.task_name}</td>
                    <td className="py-2.5 text-slate-300">{row.agent_name || row.agent_id}</td>
                    <td className="py-2.5">
                      <StatusBadge type="execution-status" value={row.status} />
                    </td>
                    <td className="py-2.5 font-mono text-slate-300">{row.duration_ms || 0} ms</td>
                    <td className="py-2.5 font-mono text-amber-300">{row.tokens_total || 0}</td>
                    <td className="py-2.5 font-mono text-emerald-400 text-[11px]">
                      ${Number(row.estimated_cost_usd || 0).toFixed(5)}
                    </td>
                    <td className="py-2.5 text-right">
                      <button
                        onClick={() => onInspectExecution(row.execution_id)}
                        className="px-2.5 py-1 rounded bg-navy-800 hover:bg-navy-700 text-cyan-300 hover:text-cyan-200 border border-navy-700 text-[11px] font-medium transition-colors"
                      >
                        View Logs
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

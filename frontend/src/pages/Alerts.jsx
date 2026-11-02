import React, { useState } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  Clock,
  CheckCircle2,
  Filter,
  Check,
  AlertTriangle
} from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';

export function Alerts({
  alerts,
  onAcknowledge,
  onResolve,
  statusFilter,
  setStatusFilter,
  severityFilter,
  setSeverityFilter
}) {
  const activeAlertsCount = alerts.filter(a => a.status === 'ACTIVE').length;

  return (
    <div className="space-y-6">
      {/* Filters Header */}
      <div className="bg-navy-900 border border-navy-800 rounded-xl p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-red-400" />
            <h3 className="text-base font-semibold text-white">Security Alerts Management</h3>
            {activeAlertsCount > 0 && (
              <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-red-500 text-white animate-pulse">
                {activeAlertsCount} Active
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Incidents generated automatically by ML model classifications and agent runtime anomalies.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Status Tabs */}
          <div className="flex items-center gap-1 bg-navy-950 p-1 rounded-lg border border-navy-800 text-xs">
            {['ALL', 'ACTIVE', 'ACKNOWLEDGED', 'RESOLVED'].map((s) => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                  statusFilter === s
                    ? 'bg-navy-800 text-cyan-300 font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {s}
              </button>
            ))}
          </div>

          {/* Severity Dropdown */}
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-navy-950 border border-navy-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="bg-navy-900 border border-navy-800 rounded-xl p-5">
        {alerts.length === 0 ? (
          <div className="py-12 text-center text-xs text-slate-400 border border-dashed border-navy-800 rounded-lg flex flex-col items-center justify-center">
            <ShieldCheck className="w-8 h-8 text-emerald-400/60 mb-2" />
            <p className="text-sm font-semibold text-slate-300">No alerts found</p>
            <p className="text-xs text-slate-400 mt-0.5">All monitored network flows and agents are operating within normal parameters.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-navy-800 text-slate-400">
                  <th className="pb-2.5 font-medium">Alert ID</th>
                  <th className="pb-2.5 font-medium">Severity</th>
                  <th className="pb-2.5 font-medium">Title & Threat Details</th>
                  <th className="pb-2.5 font-medium">Status</th>
                  <th className="pb-2.5 font-medium">Port</th>
                  <th className="pb-2.5 font-medium">Confidence</th>
                  <th className="pb-2.5 font-medium">Timestamp</th>
                  <th className="pb-2.5 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-800/60">
                {alerts.map((alert) => {
                  const isAct = alert.status === 'ACTIVE';
                  const isAck = alert.status === 'ACKNOWLEDGED';

                  return (
                    <tr key={alert.id} className="hover:bg-navy-850/60 transition-colors">
                      <td className="py-3 font-mono text-[11px] text-slate-400">#{alert.id}</td>
                      <td className="py-3">
                        <StatusBadge type="severity" value={alert.severity} />
                      </td>
                      <td className="py-3 max-w-sm">
                        <p className="font-semibold text-white">{alert.title}</p>
                        <p className="text-[11px] text-slate-400 mt-0.5 truncate" title={alert.details}>
                          {alert.details}
                        </p>
                      </td>
                      <td className="py-3">
                        <StatusBadge type="alert-status" value={alert.status} />
                      </td>
                      <td className="py-3 font-mono text-slate-200">{alert.destination_port}</td>
                      <td className="py-3 font-mono font-medium text-red-400">
                        {Math.round(alert.attack_probability * 100)}%
                      </td>
                      <td className="py-3 font-mono text-[11px] text-slate-400 whitespace-nowrap">
                        {alert.timestamp}
                      </td>
                      <td className="py-3 text-right whitespace-nowrap">
                        <div className="flex items-center justify-end gap-1.5">
                          {isAct && (
                            <button
                              onClick={() => onAcknowledge(alert.id)}
                              className="px-2.5 py-1 rounded bg-navy-800 hover:bg-amber-950/60 text-slate-300 hover:text-amber-300 border border-navy-700 hover:border-amber-500/40 text-[11px] font-medium transition-colors"
                              title="Acknowledge alert"
                            >
                              Ack
                            </button>
                          )}
                          {(isAct || isAck) && (
                            <button
                              onClick={() => onResolve(alert.id)}
                              className="px-2.5 py-1 rounded bg-navy-800 hover:bg-emerald-950/60 text-slate-300 hover:text-emerald-300 border border-navy-700 hover:border-emerald-500/40 text-[11px] font-medium transition-colors"
                              title="Mark as resolved"
                            >
                              Resolve
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

import React, { useState } from 'react';
import { History as HistoryIcon, Search, Eye, Filter } from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';

export function History({
  historyData,
  onInspectRecord,
  classFilter,
  setClassFilter,
  searchTerm,
  setSearchTerm
}) {
  const records = historyData?.records || [];
  const total = historyData?.total || 0;

  return (
    <div className="space-y-6">
      {/* Header & Filter Controls */}
      <div className="bg-navy-900 border border-navy-800 rounded-xl p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <HistoryIcon className="w-5 h-5 text-cyan-400" />
            <h3 className="text-base font-semibold text-white">Network Prediction History</h3>
            <span className="px-2 py-0.5 rounded text-xs font-mono bg-navy-800 text-slate-300 border border-navy-700">
              {total} Total Records
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Historical log of all network flows evaluated by the machine learning pipeline.
          </p>
        </div>

        <div className="flex items-center gap-2.5 w-full md:w-auto">
          {/* Search */}
          <div className="relative flex-1 md:w-56">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search port or filename..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-navy-950 border border-navy-700 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Class Filter */}
          <div className="flex items-center gap-1 bg-navy-950 p-1 rounded-lg border border-navy-800 text-xs">
            {['ALL', 'BENIGN', 'ATTACK'].map((c) => (
              <button
                key={c}
                onClick={() => setClassFilter(c)}
                className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                  classFilter === c
                    ? 'bg-navy-800 text-cyan-300 font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* History Table */}
      <div className="bg-navy-900 border border-navy-800 rounded-xl p-5">
        {records.length === 0 ? (
          <div className="py-12 text-center text-xs text-slate-400 border border-dashed border-navy-800 rounded-lg">
            No prediction records found matching filters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-navy-800 text-slate-400">
                  <th className="pb-2.5 font-medium">Record ID</th>
                  <th className="pb-2.5 font-medium">Timestamp</th>
                  <th className="pb-2.5 font-medium">Source File</th>
                  <th className="pb-2.5 font-medium">Dst Port</th>
                  <th className="pb-2.5 font-medium">Duration</th>
                  <th className="pb-2.5 font-medium">Packets</th>
                  <th className="pb-2.5 font-medium">Prediction</th>
                  <th className="pb-2.5 font-medium">Attack Prob</th>
                  <th className="pb-2.5 font-medium text-right">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-800/60">
                {records.map((row) => (
                  <tr key={row.id} className="hover:bg-navy-850/60 transition-colors">
                    <td className="py-2.5 font-mono text-[11px] text-slate-400">#{row.id}</td>
                    <td className="py-2.5 font-mono text-[11px] text-slate-400 whitespace-nowrap">
                      {row.timestamp}
                    </td>
                    <td className="py-2.5 text-slate-300 max-w-[150px] truncate" title={row.source_filename}>
                      {row.source_filename}
                    </td>
                    <td className="py-2.5 font-mono text-slate-200">{row.destination_port}</td>
                    <td className="py-2.5 font-mono text-slate-400">{Math.round(row.flow_duration)} ms</td>
                    <td className="py-2.5 font-mono text-slate-300">
                      {Math.round(row.total_fwd_packets + row.total_bwd_packets)}
                    </td>
                    <td className="py-2.5">
                      <StatusBadge type="prediction" value={row.predicted_class} />
                    </td>
                    <td className="py-2.5 font-mono text-slate-200">
                      {(row.attack_probability * 100).toFixed(1)}%
                    </td>
                    <td className="py-2.5 text-right">
                      <button
                        onClick={() => onInspectRecord(row.id)}
                        className="px-2.5 py-1 rounded bg-navy-800 hover:bg-navy-700 text-cyan-300 hover:text-cyan-200 border border-navy-700 text-[11px] font-medium transition-colors"
                      >
                        Inspect Feats
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

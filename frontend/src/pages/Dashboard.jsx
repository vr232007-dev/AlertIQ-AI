import React from 'react';
import {
  Activity,
  ShieldCheck,
  ShieldAlert,
  Bell,
  ArrowRight,
  TrendingUp,
  Cpu,
  Layers,
  Database,
  Eye
} from 'lucide-react';
import { StatCard } from '../components/StatCard';
import { StatusBadge } from '../components/StatusBadge';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

export function Dashboard({
  stats,
  systemStatus,
  onNavigate,
  onInspectRecord,
  onAcknowledgeAlert,
  onResolveAlert
}) {
  const total = stats?.total_traffic || 0;
  const benign = stats?.benign_count || 0;
  const attack = stats?.attack_count || 0;
  const activeAlerts = stats?.active_alerts || 0;
  const attackPct = stats?.attack_percentage || 0;
  const recentPredictions = stats?.recent_predictions || [];
  const recentAlerts = stats?.recent_alerts || [];

  // Chart data for Benign vs Attack
  const chartData = [
    { name: 'Benign Flows', value: benign, color: '#10b981' },
    { name: 'Malicious Attacks', value: attack, color: '#ef4444' },
  ];

  return (
    <div className="space-y-6">
      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Traffic Flows"
          value={total.toLocaleString()}
          subtitle="Analyzed flows in database"
          icon={Activity}
          color="blue"
          trend={<span>Real-time SQLite count</span>}
        />
        <StatCard
          title="Benign Traffic"
          value={benign.toLocaleString()}
          subtitle={`${total > 0 ? (100 - attackPct).toFixed(1) : 0}% of analyzed traffic`}
          icon={ShieldCheck}
          color="green"
        />
        <StatCard
          title="Detected Attacks"
          value={attack.toLocaleString()}
          subtitle={`${attackPct}% intrusion rate`}
          icon={ShieldAlert}
          color="red"
        />
        <StatCard
          title="Active Security Alerts"
          value={activeAlerts.toLocaleString()}
          subtitle="Requires analyst attention"
          icon={Bell}
          color="orange"
        />
      </div>

      {/* Charts & System Status Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Benign vs Attack Donut Chart */}
        <div className="bg-navy-900 border border-navy-800 rounded-xl p-5 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Traffic Classification Breakdown</h3>
              <p className="text-xs text-slate-400">Distribution of normal vs malicious network flows</p>
            </div>
            <span className="text-xs px-2.5 py-1 rounded bg-navy-800 text-slate-300 border border-navy-700">
              Live DB Stats
            </span>
          </div>

          {total === 0 ? (
            <div className="h-64 flex flex-col items-center justify-center text-slate-400 border border-dashed border-navy-800 rounded-lg">
              <Activity className="w-10 h-10 text-slate-400 mb-2" />
              <p className="text-sm font-medium">No traffic records in database yet</p>
              <p className="text-xs text-slate-400 mt-1">Upload a CSV or click "Quick Demo Seed" above to see live analysis.</p>
            </div>
          ) : (
            <div className="h-64 flex flex-col sm:flex-row items-center justify-center">
              <div className="w-full sm:w-1/2 h-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={chartData}
                      innerRadius={60}
                      outerRadius={85}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#0a0f1d',
                        borderColor: '#1e2c4a',
                        borderRadius: '8px',
                        color: '#f8fafc',
                        fontSize: '12px'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Legend & Stats breakdown */}
              <div className="w-full sm:w-1/2 space-y-3 px-4">
                <div className="flex items-center justify-between p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-emerald-500" />
                    <span className="text-xs font-medium text-emerald-300">Benign Traffic</span>
                  </div>
                  <span className="text-sm font-bold text-white">{benign} flows</span>
                </div>

                <div className="flex items-center justify-between p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-red-500" />
                    <span className="text-xs font-medium text-red-300">Malicious Attacks</span>
                  </div>
                  <span className="text-sm font-bold text-white">{attack} flows</span>
                </div>

                <div className="text-xs text-slate-400 text-center pt-2">
                  Total analyzed: <span className="font-semibold text-slate-200">{total}</span> records
                </div>
              </div>
            </div>
          )}
        </div>

        {/* System & Model Status Card */}
        <div className="bg-navy-900 border border-navy-800 rounded-xl p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-semibold text-white">Engine Specifications</h3>
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Real-time ML intrusion detection powered by trained Random Forest pipeline.
            </p>

            <div className="space-y-2.5 text-xs">
              <div className="flex items-center justify-between p-2 rounded bg-navy-950/60 border border-navy-800">
                <span className="text-slate-400">Dataset</span>
                <span className="font-medium text-slate-200">CIC-IDS2017</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-navy-950/60 border border-navy-800">
                <span className="text-slate-400">Features Extracted</span>
                <span className="font-mono font-semibold text-cyan-400">78 Features</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-navy-950/60 border border-navy-800">
                <span className="text-slate-400">Model Pipeline</span>
                <span className="font-medium text-slate-200">SimpleImputer + RF</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-navy-950/60 border border-navy-800">
                <span className="text-slate-400">Engine Version</span>
                <span className="font-mono text-slate-300">v{systemStatus?.model_version || '1.0.0'}</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-navy-950/60 border border-navy-800">
                <span className="text-slate-400">Backend Engine</span>
                <span className="font-medium text-emerald-400">FastAPI + SQLite</span>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-navy-800 mt-4">
            <button
              onClick={() => onNavigate('traffic')}
              className="w-full flex items-center justify-center gap-2 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium text-xs transition-all shadow-md shadow-cyan-900/20"
            >
              <span>Analyze Traffic CSV</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Recent Predictions & Active Alerts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Traffic Predictions */}
        <div className="bg-navy-900 border border-navy-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Recent Traffic Activity</h3>
              <p className="text-xs text-slate-400">Latest network flows processed</p>
            </div>
            <button
              onClick={() => onNavigate('history')}
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition-colors"
            >
              <span>View All</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          {recentPredictions.length === 0 ? (
            <div className="py-8 text-center text-xs text-slate-400 border border-dashed border-navy-800 rounded-lg">
              No recent predictions stored yet.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-navy-800 text-slate-400">
                    <th className="pb-2 font-medium">Time</th>
                    <th className="pb-2 font-medium">Dst Port</th>
                    <th className="pb-2 font-medium">Duration</th>
                    <th className="pb-2 font-medium">Classification</th>
                    <th className="pb-2 font-medium">Attack Prob</th>
                    <th className="pb-2 font-medium text-right">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-navy-800/60">
                  {recentPredictions.map((row) => (
                    <tr key={row.id} className="hover:bg-navy-850/60 transition-colors">
                      <td className="py-2.5 font-mono text-[11px] text-slate-400">
                        {row.timestamp ? row.timestamp.split(' ')[1] : '-'}
                      </td>
                      <td className="py-2.5 font-mono text-slate-200">{row.destination_port}</td>
                      <td className="py-2.5 font-mono text-slate-400">{Math.round(row.flow_duration)} ms</td>
                      <td className="py-2.5">
                        <StatusBadge type="prediction" value={row.predicted_class} />
                      </td>
                      <td className="py-2.5 font-mono font-medium text-slate-300">
                        {(row.attack_probability * 100).toFixed(1)}%
                      </td>
                      <td className="py-2.5 text-right">
                        <button
                          onClick={() => onInspectRecord(row.id)}
                          className="p-1 rounded hover:bg-navy-700 text-slate-400 hover:text-cyan-400 transition-colors"
                          title="Inspect 78 flow features"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Recent Active Alerts */}
        <div className="bg-navy-900 border border-navy-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Active Security Incidents</h3>
              <p className="text-xs text-slate-400">Intrusions detected awaiting response</p>
            </div>
            <button
              onClick={() => onNavigate('alerts')}
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition-colors"
            >
              <span>View All</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          {recentAlerts.length === 0 ? (
            <div className="py-8 text-center text-xs text-slate-400 border border-dashed border-navy-800 rounded-lg flex flex-col items-center justify-center">
              <ShieldCheck className="w-6 h-6 text-emerald-400/60 mb-1" />
              <span>No active security alerts. System normal.</span>
            </div>
          ) : (
            <div className="space-y-2.5">
              {recentAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className="p-3 rounded-lg bg-navy-950/60 border border-navy-800 flex items-center justify-between gap-3 hover:border-navy-700 transition-colors"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <StatusBadge type="severity" value={alert.severity} />
                      <span className="text-xs font-medium text-white">{alert.title}</span>
                    </div>
                    <p className="text-[11px] text-slate-400">
                      Port: <span className="font-mono text-slate-300">{alert.destination_port}</span> | Attack Confidence: <span className="font-mono text-red-400 font-semibold">{Math.round(alert.attack_probability * 100)}%</span>
                    </p>
                  </div>

                  <div className="flex items-center gap-1.5 shrink-0">
                    <button
                      onClick={() => onAcknowledgeAlert(alert.id)}
                      className="px-2 py-1 rounded bg-navy-800 hover:bg-amber-950/60 text-slate-300 hover:text-amber-300 border border-navy-700 hover:border-amber-500/40 text-[11px] font-medium transition-colors"
                    >
                      Ack
                    </button>
                    <button
                      onClick={() => onResolveAlert(alert.id)}
                      className="px-2 py-1 rounded bg-navy-800 hover:bg-emerald-950/60 text-slate-300 hover:text-emerald-300 border border-navy-700 hover:border-emerald-500/40 text-[11px] font-medium transition-colors"
                    >
                      Resolve
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

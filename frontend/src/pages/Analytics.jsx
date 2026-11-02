import React from 'react';
import { BarChart3, PieChart as PieIcon, ShieldAlert, Activity, TrendingUp } from 'lucide-react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';

export function Analytics({ analyticsData }) {
  const total = analyticsData?.total_predictions || 0;
  const benign = analyticsData?.benign_count || 0;
  const attack = analyticsData?.attack_count || 0;
  const attackPct = analyticsData?.attack_percentage || 0;
  const severityMap = analyticsData?.severity_breakdown || {};
  const topPorts = analyticsData?.top_ports || [];
  const trendData = analyticsData?.trend_data || [];

  const pieData = [
    { name: 'Benign Flows', value: benign, color: '#10b981' },
    { name: 'Attacks Detected', value: attack, color: '#ef4444' },
  ];

  const severityBarData = [
    { name: 'Critical', count: severityMap.CRITICAL || 0, fill: '#ef4444' },
    { name: 'High', count: severityMap.HIGH || 0, fill: '#f97316' },
    { name: 'Medium', count: severityMap.MEDIUM || 0, fill: '#f59e0b' },
    { name: 'Low', count: severityMap.LOW || 0, fill: '#3b82f6' },
  ];

  const portsBarData = topPorts.map(p => ({
    port: `Port ${p.port}`,
    attacks: p.attacks
  }));

  const tooltipStyle = {
    backgroundColor: '#0a0f1d',
    borderColor: '#1e2c4a',
    borderRadius: '8px',
    color: '#f8fafc',
    fontSize: '12px'
  };

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-navy-900 border border-navy-800 rounded-xl p-5">
          <p className="text-xs text-slate-400">Total Analyzed Traffic</p>
          <h3 className="text-2xl font-bold text-white mt-1">{total.toLocaleString()}</h3>
          <p className="text-xs text-slate-400 mt-1">Aggregated across all uploads</p>
        </div>

        <div className="bg-navy-900 border border-red-500/30 bg-red-500/5 rounded-xl p-5">
          <p className="text-xs text-red-400">Overall Threat Rate</p>
          <h3 className="text-2xl font-bold text-red-300 mt-1">{attackPct}%</h3>
          <p className="text-xs text-red-400/80 mt-1">{attack} total attack flows detected</p>
        </div>

        <div className="bg-navy-900 border border-emerald-500/30 bg-emerald-500/5 rounded-xl p-5">
          <p className="text-xs text-emerald-400">Benign Traffic Baseline</p>
          <h3 className="text-2xl font-bold text-emerald-300 mt-1">
            {total > 0 ? (100 - attackPct).toFixed(1) : 0}%
          </h3>
          <p className="text-xs text-emerald-400/80 mt-1">{benign} confirmed safe flows</p>
        </div>
      </div>

      {/* Row 1: Distribution & Severity Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Donut Chart */}
        <div className="bg-navy-900 border border-navy-800 rounded-xl p-5">
          <h4 className="text-sm font-semibold text-white mb-1">Traffic Distribution</h4>
          <p className="text-xs text-slate-400 mb-4">Proportion of Benign vs Malicious Network Flows</p>

          {total === 0 ? (
            <div className="h-60 flex items-center justify-center text-xs text-slate-400 border border-dashed border-navy-800 rounded-lg">
              No data available yet
            </div>
          ) : (
            <div className="h-60">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    innerRadius={65}
                    outerRadius={90}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={tooltipStyle} />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Severity Bar Chart */}
        <div className="bg-navy-900 border border-navy-800 rounded-xl p-5">
          <h4 className="text-sm font-semibold text-white mb-1">Alert Severity Breakdown</h4>
          <p className="text-xs text-slate-400 mb-4">Classification by ML confidence threshold</p>

          <div className="h-60">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={severityBarData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e2c4a" vertical={false} />
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 2: Top Targeted Ports */}
      <div className="bg-navy-900 border border-navy-800 rounded-xl p-5">
        <h4 className="text-sm font-semibold text-white mb-1">Top Targeted Destination Ports</h4>
        <p className="text-xs text-slate-400 mb-4">Most frequently targeted service ports among detected attack traffic</p>

        {portsBarData.length === 0 ? (
          <div className="h-52 flex items-center justify-center text-xs text-slate-400 border border-dashed border-navy-800 rounded-lg">
            No attack traffic recorded on target ports yet
          </div>
        ) : (
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={portsBarData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#1e2c4a" horizontal={false} />
                <XAxis type="number" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis dataKey="port" type="category" stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="attacks" fill="#06b6d4" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}

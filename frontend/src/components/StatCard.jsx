import React from 'react';

export function StatCard({ title, value, subtitle, icon: Icon, color = 'blue', trend }) {
  const colorMap = {
    blue: 'border-blue-500/20 bg-blue-500/5 text-blue-400',
    cyan: 'border-cyan-500/20 bg-cyan-500/5 text-cyan-400',
    green: 'border-emerald-500/20 bg-emerald-500/5 text-emerald-400',
    red: 'border-red-500/20 bg-red-500/5 text-red-400',
    orange: 'border-amber-500/20 bg-amber-500/5 text-amber-400',
  };

  return (
    <div className="bg-navy-900 border border-navy-700/60 rounded-xl p-5 hover:border-navy-600 transition-all shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-400 mb-1">{title}</p>
          <h3 className="text-2xl font-bold text-white tracking-tight">{value}</h3>
          {subtitle && (
            <p className="text-xs text-slate-400 mt-1">{subtitle}</p>
          )}
        </div>
        {Icon && (
          <div className={`p-2.5 rounded-lg border ${colorMap[color] || colorMap.blue}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      {trend && (
        <div className="mt-3 pt-3 border-t border-navy-800 text-xs text-slate-400 flex items-center gap-1.5">
          {trend}
        </div>
      )}
    </div>
  );
}

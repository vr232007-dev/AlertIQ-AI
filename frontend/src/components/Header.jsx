import React from 'react';
import { RefreshCw, PlayCircle, Trash2, Database } from 'lucide-react';

export function Header({
  title,
  subtitle,
  onRefresh,
  onSeedDemo,
  onResetDb,
  isRefreshing,
  isSeeding,
  isResetting
}) {
  return (
    <header className="h-16 px-6 bg-navy-900 border-b border-navy-800 flex items-center justify-between shrink-0">
      <div>
        <h2 className="text-base font-semibold text-white tracking-tight">{title}</h2>
        {subtitle && <p className="text-xs text-slate-400">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-2.5">
        {/* Seed Demo Data Button */}
        <button
          onClick={onSeedDemo}
          disabled={isSeeding}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-navy-800 hover:bg-navy-700 text-cyan-300 border border-cyan-500/30 text-xs font-medium transition-colors disabled:opacity-50"
          title="Seed realistic benign and attack flows into SQLite for live demonstration"
        >
          <PlayCircle className={`w-3.5 h-3.5 ${isSeeding ? 'animate-spin' : ''}`} />
          <span>{isSeeding ? 'Seeding...' : 'Quick Demo Seed'}</span>
        </button>

        {/* Clear Data Button */}
        <button
          onClick={onResetDb}
          disabled={isResetting}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-navy-800 hover:bg-red-950/60 text-slate-400 hover:text-red-300 border border-navy-700 hover:border-red-500/30 text-xs font-medium transition-colors disabled:opacity-50"
          title="Clear all stored predictions and alerts from SQLite"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Reset DB</span>
        </button>

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="p-2 rounded-lg bg-navy-800 hover:bg-navy-700 text-slate-300 hover:text-white border border-navy-700 text-xs transition-colors disabled:opacity-50"
          title="Refresh statistics"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-cyan-400' : ''}`} />
        </button>
      </div>
    </header>
  );
}

import React from 'react';
import {
  Activity,
  Bot,
  Terminal,
  UserCheck,
  UploadCloud,
  ShieldAlert,
  History,
  BarChart3,
  Cpu,
  Shield,
  Layers,
  Database
} from 'lucide-react';

export function Sidebar({
  currentTab,
  setCurrentTab,
  activeAlertsCount = 0,
  pendingApprovalsCount = 0,
  systemStatus
}) {
  const navItems = [
    { id: 'dashboard', label: 'SOC Dashboard', icon: Activity },
    { id: 'agents', label: 'Agent Management', icon: Bot },
    { id: 'monitoring', label: 'Agent Monitoring & Logs', icon: Terminal },
    {
      id: 'approvals',
      label: 'Human-In-The-Loop',
      icon: UserCheck,
      badge: pendingApprovalsCount > 0 ? pendingApprovalsCount : null,
      badgeColor: 'amber'
    },
    { id: 'traffic', label: 'Traffic Analysis (CSV)', icon: UploadCloud },
    {
      id: 'alerts',
      label: 'Security Alerts',
      icon: ShieldAlert,
      badge: activeAlertsCount > 0 ? activeAlertsCount : null,
      badgeColor: 'red'
    },
    { id: 'history', label: 'Prediction History', icon: History },
    { id: 'analytics', label: 'Analytics & Trends', icon: BarChart3 },
    { id: 'model', label: 'Model Specifications', icon: Cpu },
  ];

  const isOnline = systemStatus?.status === 'online';
  const isModelReady = systemStatus?.model_status === 'ready';

  return (
    <aside className="w-64 bg-navy-900 border-r border-navy-800 flex flex-col justify-between shrink-0 select-none">
      <div>
        {/* Brand Header */}
        <div className="p-5 border-b border-navy-800">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white shadow-lg shadow-cyan-500/20">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h1 className="font-bold text-base text-white tracking-tight">AlertIQ</h1>
                <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                  AI
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Intelligent SOC & Agent System</p>
            </div>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            const isAmber = item.badgeColor === 'amber';

            return (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/15 to-blue-500/10 text-cyan-300 border border-cyan-500/30 font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-navy-800/60'
                }`}
              >
                <div className="flex items-center gap-2.5 truncate">
                  <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                  <span className="truncate">{item.label}</span>
                </div>
                {item.badge && (
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                    isAmber ? 'bg-amber-500 text-black' : 'bg-red-500 text-white'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* System Status Footer */}
      <div className="p-4 border-t border-navy-800 bg-navy-950/40 text-xs">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-400' : 'bg-red-400'}`} />
              Backend API
            </span>
            <span className={`font-mono text-[11px] font-medium ${isOnline ? 'text-emerald-400' : 'text-red-400'}`}>
              {isOnline ? 'ONLINE' : 'OFFLINE'}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-slate-400 flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${isModelReady ? 'bg-cyan-400' : 'bg-amber-400'}`} />
              ML Engine (78 feats)
            </span>
            <span className={`font-mono text-[11px] font-medium ${isModelReady ? 'text-cyan-400' : 'text-amber-400'}`}>
              {isModelReady ? 'READY' : 'LOADING'}
            </span>
          </div>

          <div className="pt-2 border-t border-navy-800/80 text-[10px] text-slate-400 flex items-center justify-between">
            <span>CIC-IDS2017 Model</span>
            <span className="font-mono text-slate-300">v1.0.0</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

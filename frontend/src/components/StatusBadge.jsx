import React from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Play,
  Pause,
  XCircle,
  Activity,
  AlertOctagon
} from 'lucide-react';

export function StatusBadge({ type, value }) {
  if (type === 'prediction' || type === 'class') {
    const isAttack = value === 'ATTACK';
    return (
      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
        isAttack
          ? 'bg-red-500/10 text-red-400 border border-red-500/30'
          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
      }`}>
        {isAttack ? (
          <ShieldAlert className="w-3.5 h-3.5" />
        ) : (
          <ShieldCheck className="w-3.5 h-3.5" />
        )}
        {value}
      </span>
    );
  }

  if (type === 'severity') {
    const styles = {
      CRITICAL: 'bg-red-950/80 text-red-400 border-red-500/40',
      HIGH: 'bg-orange-950/80 text-orange-400 border-orange-500/40',
      MEDIUM: 'bg-amber-950/80 text-amber-400 border-amber-500/40',
      LOW: 'bg-blue-950/80 text-blue-400 border-blue-500/40',
    };
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded text-xs font-semibold tracking-wide border ${styles[value] || styles.LOW}`}>
        {value}
      </span>
    );
  }

  if (type === 'agent-status') {
    const isRunning = value === 'RUNNING';
    const isError = value === 'ERROR';
    const isStopped = value === 'STOPPED';

    return (
      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
        isRunning
          ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30'
          : isError
          ? 'bg-red-500/15 text-red-300 border border-red-500/30'
          : isStopped
          ? 'bg-slate-700/50 text-slate-400 border border-slate-600/30'
          : 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
      }`}>
        {isRunning && <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />}
        {isError && <AlertOctagon className="w-3 h-3 text-red-400" />}
        {isStopped && <Pause className="w-3 h-3 text-slate-400" />}
        {!isRunning && !isError && !isStopped && <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />}
        {value}
      </span>
    );
  }

  if (type === 'execution-status') {
    const isSuccess = value === 'SUCCESS';
    const isFailed = value === 'FAILED';
    const isWaiting = value === 'WAITING_APPROVAL';

    return (
      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
        isSuccess
          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
          : isFailed
          ? 'bg-red-500/10 text-red-400 border border-red-500/30'
          : isWaiting
          ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30'
          : 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
      }`}>
        {isSuccess && <CheckCircle2 className="w-3.5 h-3.5" />}
        {isFailed && <XCircle className="w-3.5 h-3.5" />}
        {isWaiting && <Clock className="w-3.5 h-3.5 animate-pulse" />}
        {value}
      </span>
    );
  }

  if (type === 'approval-status') {
    const isApproved = value === 'APPROVED';
    const isRejected = value === 'REJECTED';

    return (
      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
        isApproved
          ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
          : isRejected
          ? 'bg-red-500/15 text-red-300 border border-red-500/30'
          : 'bg-amber-500/15 text-amber-300 border border-amber-500/30'
      }`}>
        {isApproved && <CheckCircle2 className="w-3.5 h-3.5" />}
        {isRejected && <XCircle className="w-3.5 h-3.5" />}
        {!isApproved && !isRejected && <Clock className="w-3.5 h-3.5" />}
        {value}
      </span>
    );
  }

  if (type === 'alert-status') {
    const isAct = value === 'ACTIVE';
    const isAck = value === 'ACKNOWLEDGED';
    const isRes = value === 'RESOLVED';

    return (
      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${
        isAct
          ? 'bg-red-500/15 text-red-300 border border-red-500/30'
          : isAck
          ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30'
          : 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
      }`}>
        {isAct && <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-ping mr-1" />}
        {isAck && <Clock className="w-3 h-3 mr-0.5" />}
        {isRes && <CheckCircle2 className="w-3 h-3 mr-0.5" />}
        {value}
      </span>
    );
  }

  return (
    <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-800 text-slate-300">
      {value}
    </span>
  );
}

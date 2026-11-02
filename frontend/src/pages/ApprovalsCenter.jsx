import React, { useState } from 'react';
import {
  ShieldAlert,
  CheckCircle2,
  XCircle,
  Clock,
  AlertTriangle,
  UserCheck,
  FileText
} from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';

export function ApprovalsCenter({
  approvals,
  onOpenDecisionModal
}) {
  const [tab, setTab] = useState('PENDING');

  const pendingApprovals = approvals.filter(a => a.status === 'PENDING');
  const pastApprovals = approvals.filter(a => a.status !== 'PENDING');

  const displayedList = tab === 'PENDING' ? pendingApprovals : pastApprovals;

  return (
    <div className="space-y-6">
      {/* Header Info Banner */}
      <div className="bg-navy-900 border border-navy-800 rounded-xl p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <UserCheck className="w-5 h-5 text-amber-400" />
            <h3 className="text-base font-semibold text-white">Human-In-The-Loop Approval Center</h3>
            {pendingApprovals.length > 0 && (
              <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-amber-500 text-black">
                {pendingApprovals.length} Pending
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Autonomous containment actions exceeding security thresholds require human SOC analyst authorization.
          </p>
        </div>

        {/* Tab switch */}
        <div className="flex items-center gap-1 bg-navy-950 p-1 rounded-lg border border-navy-800 text-xs shrink-0">
          <button
            onClick={() => setTab('PENDING')}
            className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
              tab === 'PENDING'
                ? 'bg-navy-800 text-amber-300 font-semibold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Pending ({pendingApprovals.length})
          </button>
          <button
            onClick={() => setTab('HISTORY')}
            className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
              tab === 'HISTORY'
                ? 'bg-navy-800 text-cyan-300 font-semibold'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Decision Log ({pastApprovals.length})
          </button>
        </div>
      </div>

      {/* Approvals Cards Grid */}
      {displayedList.length === 0 ? (
        <div className="bg-navy-900 border border-dashed border-navy-800 rounded-xl p-12 text-center text-xs text-slate-400 space-y-2">
          <CheckCircle2 className="w-8 h-8 text-emerald-400/60 mx-auto" />
          <p className="text-sm font-semibold text-slate-300">
            {tab === 'PENDING' ? 'No pending approval requests' : 'No past decisions recorded'}
          </p>
          <p className="text-slate-400 max-w-sm mx-auto">
            {tab === 'PENDING'
              ? 'When an agent detects a critical intrusion and prepares containment, it will appear here.'
              : 'Decisions made by SOC analysts will be permanently logged here.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {displayedList.map((appr) => {
            const isPending = appr.status === 'PENDING';
            const isApproved = appr.status === 'APPROVED';

            return (
              <div
                key={appr.approval_id}
                className="bg-navy-900 border border-navy-800 rounded-xl p-5 hover:border-navy-700 transition-all space-y-4 shadow-sm"
              >
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <StatusBadge type="severity" value={appr.severity} />
                      <span className="font-mono text-xs font-bold text-white tracking-wide">{appr.action_type}</span>
                    </div>
                    <p className="text-[11px] text-slate-400 font-mono">
                      Target: <span className="text-slate-200">{appr.resource_target}</span>
                    </p>
                  </div>

                  <StatusBadge type="approval-status" value={appr.status} />
                </div>

                {/* Justification Box */}
                <div className="p-3 rounded-lg bg-navy-950/80 border border-navy-800 text-xs text-slate-300 leading-relaxed">
                  <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 block mb-0.5">
                    Agent Justification
                  </span>
                  {appr.reason}
                </div>

                {/* Metadata */}
                <div className="text-[11px] text-slate-400 flex items-center justify-between pt-1 border-t border-navy-800">
                  <span>Requested: {appr.requested_at}</span>
                  <span className="font-mono text-cyan-400">{appr.approval_id}</span>
                </div>

                {/* Past Decision Notes */}
                {!isPending && appr.decision_notes && (
                  <div className="p-2.5 rounded bg-navy-950 border border-navy-800 text-[11px]">
                    <span className="text-slate-400 font-semibold block mb-0.5">Analyst Note:</span>
                    <p className="text-slate-200">{appr.decision_notes}</p>
                    <span className="text-slate-400 text-[10px] block mt-1">Decided: {appr.decided_at}</span>
                  </div>
                )}

                {/* Action button if pending */}
                {isPending && (
                  <button
                    onClick={() => onOpenDecisionModal(appr)}
                    className="w-full py-2 rounded-lg bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white font-semibold text-xs transition-all shadow-md shadow-amber-950 flex items-center justify-center gap-1.5"
                  >
                    <UserCheck className="w-3.5 h-3.5" />
                    <span>Review & Authorize Action</span>
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

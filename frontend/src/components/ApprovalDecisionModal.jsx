import React, { useState } from 'react';
import { X, ShieldAlert, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

export function ApprovalDecisionModal({ isOpen, onClose, approval, onDecide }) {
  const [decision, setDecision] = useState('APPROVED');
  const [notes, setNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen || !approval) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      await onDecide(approval.approval_id, decision, notes.trim());
      setNotes('');
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to submit decision');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
      <div className="bg-navy-900 border border-navy-700 rounded-xl w-full max-w-lg shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-navy-800 bg-navy-850 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-white">Human-In-The-Loop Approval</h3>
                <StatusBadge type="severity" value={approval.severity} />
              </div>
              <p className="text-xs text-slate-400">Approval ID: <span className="font-mono text-cyan-300">{approval.approval_id}</span></p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-navy-700 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4 text-xs">
          {error && (
            <div className="p-3 rounded-lg bg-red-950/80 border border-red-500/40 text-red-300">
              {error}
            </div>
          )}

          {/* Details Box */}
          <div className="p-4 rounded-lg bg-navy-950/80 border border-navy-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Proposed Action</span>
              <span className="font-mono font-semibold text-red-400">{approval.action_type}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Target Asset / Resource</span>
              <span className="font-mono font-medium text-slate-200">{approval.resource_target}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Requesting Agent</span>
              <span className="font-medium text-cyan-300">{approval.agent_name || approval.agent_id}</span>
            </div>
            <div className="pt-2 border-t border-navy-800 text-slate-300 leading-relaxed">
              <span className="font-semibold text-slate-400 block mb-0.5">Threat Justification:</span>
              {approval.reason}
            </div>
          </div>

          {/* Decision Selection */}
          <div>
            <label className="block font-medium text-slate-300 mb-2">SOC Analyst Decision *</label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setDecision('APPROVED')}
                className={`p-3 rounded-lg border flex items-center justify-center gap-2 font-semibold transition-all ${
                  decision === 'APPROVED'
                    ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300 shadow-md shadow-emerald-950'
                    : 'bg-navy-950 border-navy-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Authorize Action</span>
              </button>

              <button
                type="button"
                onClick={() => setDecision('REJECTED')}
                className={`p-3 rounded-lg border flex items-center justify-center gap-2 font-semibold transition-all ${
                  decision === 'REJECTED'
                    ? 'bg-red-500/20 border-red-500 text-red-300 shadow-md shadow-red-950'
                    : 'bg-navy-950 border-navy-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <XCircle className="w-4 h-4 text-red-400" />
                <span>Deny / Reject</span>
              </button>
            </div>
          </div>

          {/* Decision Notes */}
          <div>
            <label className="block font-medium text-slate-300 mb-1">Analyst Decision Notes</label>
            <textarea
              rows={2}
              placeholder="e.g., Confirmed malicious brute force attack signature on Port 80; firewall isolation approved."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full bg-navy-950 border border-navy-700 rounded-lg px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Action Buttons */}
          <div className="pt-2 flex items-center justify-end gap-2.5">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-navy-800 hover:bg-navy-700 text-slate-300 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className={`px-5 py-2 rounded-lg font-semibold text-white transition-all shadow-md ${
                decision === 'APPROVED'
                  ? 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-950'
                  : 'bg-red-600 hover:bg-red-500 shadow-red-950'
              } disabled:opacity-50`}
            >
              {isSubmitting ? 'Recording...' : `Confirm ${decision === 'APPROVED' ? 'Approval' : 'Rejection'}`}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

import React, { useState } from 'react';
import { X, Bot, PlusCircle } from 'lucide-react';

export function CreateAgentModal({ isOpen, onClose, onCreateAgent }) {
  const [name, setName] = useState('');
  const [role, setRole] = useState('');
  const [modelProvider, setModelProvider] = useState('Scikit-Learn Random Forest (78-Feats)');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim() || !role.trim()) {
      setError('Please provide both Agent Name and Role.');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      await onCreateAgent({
        name: name.trim(),
        role: role.trim(),
        model_provider: modelProvider,
        description: description.trim()
      });
      setName('');
      setRole('');
      setDescription('');
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to create agent');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
      <div className="bg-navy-900 border border-navy-700 rounded-xl w-full max-w-md shadow-2xl overflow-hidden">
        <div className="px-6 py-4 border-b border-navy-800 bg-navy-850 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">Register Autonomous Agent</h3>
              <p className="text-xs text-slate-400">Add an agent to the AlertIQ multi-agent registry</p>
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

          <div>
            <label className="block font-medium text-slate-300 mb-1">Agent Name *</label>
            <input
              type="text"
              required
              placeholder="e.g., DNS Anomaly Hunter"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-navy-950 border border-navy-700 rounded-lg px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block font-medium text-slate-300 mb-1">Role / Function *</label>
            <input
              type="text"
              required
              placeholder="e.g., DNS Tunneling & DGA Threat Analyzer"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full bg-navy-950 border border-navy-700 rounded-lg px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div>
            <label className="block font-medium text-slate-300 mb-1">Model / Execution Engine</label>
            <select
              value={modelProvider}
              onChange={(e) => setModelProvider(e.target.value)}
              className="w-full bg-navy-950 border border-navy-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="Scikit-Learn Random Forest (78-Feats)">Scikit-Learn Random Forest (78-Feats)</option>
              <option value="Rule & Policy Enforcement Engine">Rule & Policy Enforcement Engine</option>
              <option value="Pandas Stream Normalizer">Pandas Stream Normalizer</option>
              <option value="NIST Compliance Auditor">NIST Compliance Auditor</option>
            </select>
          </div>

          <div>
            <label className="block font-medium text-slate-300 mb-1">Description</label>
            <textarea
              rows={3}
              placeholder="Operational responsibilities, trigger parameters, and security context..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-navy-950 border border-navy-700 rounded-lg px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

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
              className="px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium transition-all shadow-md shadow-cyan-950 disabled:opacity-50 flex items-center gap-1.5"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>{isSubmitting ? 'Registering...' : 'Register Agent'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

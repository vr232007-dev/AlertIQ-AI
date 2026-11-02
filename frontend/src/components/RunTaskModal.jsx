import React, { useState } from 'react';
import { X, Play, Loader2 } from 'lucide-react';

export function RunTaskModal({ isOpen, onClose, agent, onRunTask }) {
  const [taskName, setTaskName] = useState('');
  const [destinationPort, setDestinationPort] = useState(443);
  const [flowDuration, setFlowDuration] = useState(1500);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen || !agent) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!taskName.trim()) {
      setError('Please provide a task name.');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const payload = {
        "Destination Port": Number(destinationPort),
        "Flow Duration": Number(flowDuration),
      };
      await onRunTask(agent.agent_id, taskName.trim(), payload);
      setTaskName('');
      onClose();
    } catch (err) {
      setError(err.message || 'Task execution failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
      <div className="bg-navy-900 border border-navy-700 rounded-xl w-full max-w-md shadow-2xl overflow-hidden">
        <div className="px-6 py-4 border-b border-navy-800 bg-navy-850 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">Execute Agent Task</h3>
            <p className="text-xs text-slate-400">
              Assign task to <span className="text-cyan-400 font-medium">{agent.name}</span>
            </p>
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
            <label className="block font-medium text-slate-300 mb-1">Task Name *</label>
            <input
              type="text"
              required
              placeholder="e.g., Scan Ingress Telemetry on Port 443"
              value={taskName}
              onChange={(e) => setTaskName(e.target.value)}
              className="w-full bg-navy-950 border border-navy-700 rounded-lg px-3 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-medium text-slate-300 mb-1">Target Port</label>
              <input
                type="number"
                value={destinationPort}
                onChange={(e) => setDestinationPort(e.target.value)}
                className="w-full bg-navy-950 border border-navy-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>
            <div>
              <label className="block font-medium text-slate-300 mb-1">Flow Duration (ms)</label>
              <input
                type="number"
                value={flowDuration}
                onChange={(e) => setFlowDuration(e.target.value)}
                className="w-full bg-navy-950 border border-navy-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>
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
              {isSubmitting ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Executing...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5" />
                  <span>Run Task</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

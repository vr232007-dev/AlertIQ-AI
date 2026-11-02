import React, { useState } from 'react';
import {
  Bot,
  PlusCircle,
  Play,
  Pause,
  AlertTriangle,
  Layers,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Zap,
  Terminal,
  Activity,
  Loader2
} from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';

export function AgentManagement({
  agents,
  onOpenCreateModal,
  onOpenRunTaskModal,
  onToggleAgentStatus,
  onRunOrchestration,
  onTriggerFault,
  isOrchestrating,
  isFaulting,
  orchestrationResult
}) {
  const [selectedAgent, setSelectedAgent] = useState(null);

  return (
    <div className="space-y-6">
      {/* Top Banner: Multi-Agent Pipeline Orchestration */}
      <div className="bg-navy-900 border border-navy-800 rounded-xl p-5">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-4">
          <div>
            <div className="flex items-center gap-2">
              <Layers className="w-5 h-5 text-cyan-400" />
              <h3 className="text-base font-semibold text-white">Multi-Agent SOC Orchestration Pipeline</h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                Autonomous Workflow
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Demonstrates coordinated handoffs between agents: Ingestion $\to$ ML Classification $\to$ Containment Mitigation $\to$ Audit Ledger.
            </p>
          </div>

          <div className="flex items-center gap-2.5 shrink-0">
            {/* Run Orchestration Pipeline */}
            <button
              onClick={onRunOrchestration}
              disabled={isOrchestrating}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium text-xs transition-all shadow-md shadow-cyan-950 disabled:opacity-50"
            >
              {isOrchestrating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Orchestrating Pipeline...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  <span>Run Multi-Agent Pipeline</span>
                </>
              )}
            </button>

            {/* Trigger Fault Injection */}
            <button
              onClick={onTriggerFault}
              disabled={isFaulting}
              className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-navy-800 hover:bg-red-950/60 text-slate-300 hover:text-red-300 border border-navy-700 hover:border-red-500/40 text-xs font-medium transition-colors disabled:opacity-50"
              title="Simulates abnormal execution behavior to verify error handling and alert generation"
            >
              <AlertTriangle className={`w-4 h-4 text-red-400 ${isFaulting ? 'animate-spin' : ''}`} />
              <span>Fault Injection Test</span>
            </button>
          </div>
        </div>

        {/* Workflow Diagram: Visual Node Connections */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
          <div className="p-3.5 rounded-lg bg-navy-950/80 border border-navy-800 relative">
            <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider block mb-1">Step 1</span>
            <h4 className="text-xs font-semibold text-white">Traffic Ingestor</h4>
            <p className="text-[11px] text-slate-400 mt-0.5">Cleans & vectors 78 features</p>
          </div>

          <div className="p-3.5 rounded-lg bg-navy-950/80 border border-cyan-500/30 bg-cyan-950/10 relative">
            <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider block mb-1">Step 2</span>
            <h4 className="text-xs font-semibold text-white">ML Triage Agent</h4>
            <p className="text-[11px] text-slate-400 mt-0.5">Executes Scikit-Learn Model</p>
          </div>

          <div className="p-3.5 rounded-lg bg-navy-950/80 border border-amber-500/30 bg-amber-950/10 relative">
            <span className="text-[10px] font-bold text-amber-400 uppercase tracking-wider block mb-1">Step 3</span>
            <h4 className="text-xs font-semibold text-white">SOC Response Agent</h4>
            <p className="text-[11px] text-slate-400 mt-0.5">Triggers Human-In-The-Loop</p>
          </div>

          <div className="p-3.5 rounded-lg bg-navy-950/80 border border-navy-800 relative">
            <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider block mb-1">Step 4</span>
            <h4 className="text-xs font-semibold text-white">Compliance Auditor</h4>
            <p className="text-[11px] text-slate-400 mt-0.5">Verifies NIST SLA & Ledger</p>
          </div>
        </div>

        {/* Live Orchestration Run Result */}
        {orchestrationResult && (
          <div className="mt-4 p-4 rounded-lg bg-navy-950 border border-cyan-500/40 text-xs space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-white flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Pipeline Execution: <span className="font-mono text-cyan-300">{orchestrationResult.workflow_id}</span>
              </span>
              <span className="text-slate-400">
                Duration: <strong className="text-slate-200 font-mono">{orchestrationResult.total_duration_ms} ms</strong> | Telemetry: <strong className="text-amber-300 font-mono">{orchestrationResult.total_tokens} tokens</strong>
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-2 pt-1">
              {orchestrationResult.steps?.map((step) => (
                <div key={step.order} className="p-2.5 rounded bg-navy-900 border border-navy-800 text-[11px]">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-slate-300">{step.agent}</span>
                    <StatusBadge type="execution-status" value={step.status} />
                  </div>
                  <p className="text-slate-400 font-mono truncate">
                    {step.output?.classification || step.output?.status || 'Done'}
                  </p>
                </div>
              ))}
            </div>

            {orchestrationResult.approval_id && (
              <div className="p-2.5 rounded bg-amber-950/40 border border-amber-500/40 flex items-center justify-between text-amber-200">
                <span>Action flagged for human authorization: Containment firewall isolation requested.</span>
                <span className="font-mono font-semibold text-amber-300">Approval ID: {orchestrationResult.approval_id}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Agent Registry Header & Create Button */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-white">Registered AI Agents</h3>
          <p className="text-xs text-slate-400">View and manage autonomous agent instances, models, and operational states</p>
        </div>

        <button
          onClick={onOpenCreateModal}
          className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs transition-colors shadow-sm"
        >
          <PlusCircle className="w-3.5 h-3.5" />
          <span>Register New Agent</span>
        </button>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4">
        {agents.map((agent) => {
          const isRunning = agent.status === 'RUNNING';
          const isStopped = agent.status === 'STOPPED';

          return (
            <div
              key={agent.agent_id}
              className="bg-navy-900 border border-navy-800 rounded-xl p-5 hover:border-navy-700 transition-all space-y-4"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-navy-950 border border-navy-800 flex items-center justify-center text-cyan-400">
                    <Bot className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white tracking-tight">{agent.name}</h4>
                    <p className="text-xs text-cyan-400/90 font-medium">{agent.role}</p>
                  </div>
                </div>

                <StatusBadge type="agent-status" value={agent.status} />
              </div>

              <p className="text-xs text-slate-400 leading-relaxed min-h-[32px]">
                {agent.description || 'No description provided.'}
              </p>

              <div className="p-3 rounded-lg bg-navy-950/70 border border-navy-800 space-y-1.5 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Model Engine</span>
                  <span className="font-mono text-slate-200 text-[11px] truncate max-w-[200px]" title={agent.model_provider}>
                    {agent.model_provider}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Execution History</span>
                  <span className="text-slate-300 font-mono">
                    <strong className="text-emerald-400">{agent.successful_runs || 0}</strong> passed / <strong className="text-red-400">{agent.failed_runs || 0}</strong> failed
                  </span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-1 border-t border-navy-800">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onToggleAgentStatus(agent.agent_id, isRunning ? 'STOPPED' : 'RUNNING')}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                      isRunning
                        ? 'bg-navy-800 hover:bg-navy-700 text-amber-300 border border-navy-700'
                        : 'bg-navy-800 hover:bg-navy-700 text-emerald-300 border border-navy-700'
                    }`}
                  >
                    {isRunning ? (
                      <>
                        <Pause className="w-3.5 h-3.5" />
                        <span>Stop Agent</span>
                      </>
                    ) : (
                      <>
                        <Play className="w-3.5 h-3.5" />
                        <span>Start Agent</span>
                      </>
                    )}
                  </button>
                </div>

                <button
                  onClick={() => onOpenRunTaskModal(agent)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-300 border border-cyan-500/30 text-xs font-medium transition-colors"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>Execute Task</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

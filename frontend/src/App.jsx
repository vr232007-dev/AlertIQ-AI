import React, { useState, useEffect, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './pages/Dashboard';
import { AgentManagement } from './pages/AgentManagement';
import { AgentMonitoring } from './pages/AgentMonitoring';
import { ApprovalsCenter } from './pages/ApprovalsCenter';
import { TrafficAnalysis } from './pages/TrafficAnalysis';
import { Alerts } from './pages/Alerts';
import { History } from './pages/History';
import { Analytics } from './pages/Analytics';
import { ModelInfo } from './pages/ModelInfo';

import { FeatureModal } from './components/FeatureModal';
import { ExecutionLogModal } from './components/ExecutionLogModal';
import { CreateAgentModal } from './components/CreateAgentModal';
import { RunTaskModal } from './components/RunTaskModal';
import { ApprovalDecisionModal } from './components/ApprovalDecisionModal';

import {
  fetchSystemStatus,
  fetchModelInfo,
  fetchDashboardStats,
  fetchAlerts,
  acknowledgeAlert,
  resolveAlert,
  fetchHistory,
  fetchPredictionDetail,
  fetchAnalytics,
  resetDatabase,
  seedSampleTraffic,
  fetchAgents,
  createAgent,
  updateAgentStatus,
  executeAgentTask,
  fetchExecutions,
  fetchExecutionDetail,
  fetchApprovals,
  submitApprovalDecision,
  runMultiAgentOrchestration,
  triggerFaultInjection,
  fetchAgentMetrics
} from './api';

export function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [systemStatus, setSystemStatus] = useState(null);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [agents, setAgents] = useState([]);
  const [agentMetrics, setAgentMetrics] = useState(null);
  const [executions, setExecutions] = useState([]);
  const [approvals, setApprovals] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [historyData, setHistoryData] = useState({ total: 0, records: [] });
  const [analyticsData, setAnalyticsData] = useState(null);

  // Loading flags
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isSeeding, setIsSeeding] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [isOrchestrating, setIsOrchestrating] = useState(false);
  const [isFaulting, setIsFaulting] = useState(false);
  const [orchestrationResult, setOrchestrationResult] = useState(null);

  // Filters
  const [alertStatusFilter, setAlertStatusFilter] = useState('ALL');
  const [alertSeverityFilter, setAlertSeverityFilter] = useState('ALL');
  const [historyClassFilter, setHistoryClassFilter] = useState('ALL');
  const [historySearchTerm, setHistorySearchTerm] = useState('');

  // Modals
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [isFeatureModalOpen, setIsFeatureModalOpen] = useState(false);

  const [selectedExecution, setSelectedExecution] = useState(null);
  const [isExecutionLogModalOpen, setIsExecutionLogModalOpen] = useState(false);

  const [isCreateAgentOpen, setIsCreateAgentOpen] = useState(false);
  const [selectedAgentForTask, setSelectedAgentForTask] = useState(null);

  const [selectedApproval, setSelectedApproval] = useState(null);
  const [isApprovalModalOpen, setIsApprovalModalOpen] = useState(false);

  // Load all primary data
  const loadData = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const [statusRes, infoRes, statsRes, agentsRes, metricsRes, execsRes, apprsRes, alertsRes, histRes, analyticsRes] =
        await Promise.allSettled([
          fetchSystemStatus(),
          fetchModelInfo(),
          fetchDashboardStats(),
          fetchAgents(),
          fetchAgentMetrics(),
          fetchExecutions(),
          fetchApprovals(),
          fetchAlerts(alertStatusFilter, alertSeverityFilter),
          fetchHistory(historyClassFilter, historySearchTerm),
          fetchAnalytics()
        ]);

      if (statusRes.status === 'fulfilled') setSystemStatus(statusRes.value);
      if (infoRes.status === 'fulfilled') setModelInfo(infoRes.value);
      if (statsRes.status === 'fulfilled') setDashboardStats(statsRes.value);
      if (agentsRes.status === 'fulfilled') setAgents(agentsRes.value);
      if (metricsRes.status === 'fulfilled') setAgentMetrics(metricsRes.value);
      if (execsRes.status === 'fulfilled') setExecutions(execsRes.value);
      if (apprsRes.status === 'fulfilled') setApprovals(apprsRes.value);
      if (alertsRes.status === 'fulfilled') setAlerts(alertsRes.value?.alerts || []);
      if (histRes.status === 'fulfilled') setHistoryData(histRes.value);
      if (analyticsRes.status === 'fulfilled') setAnalyticsData(analyticsRes.value);
    } catch (err) {
      console.error('Error refreshing data:', err);
    } finally {
      setIsRefreshing(false);
    }
  }, [alertStatusFilter, alertSeverityFilter, historyClassFilter, historySearchTerm]);

  useEffect(() => {
    loadData();
    // Poll updates every 6 seconds
    const interval = setInterval(() => {
      loadData();
    }, 6000);
    return () => clearInterval(interval);
  }, [loadData]);

  // Demo Seed
  const handleSeedDemo = async () => {
    setIsSeeding(true);
    try {
      await seedSampleTraffic();
      await loadData();
    } catch (err) {
      alert(`Seed failed: ${err.message}`);
    } finally {
      setIsSeeding(false);
    }
  };

  // Reset DB
  const handleResetDb = async () => {
    if (!window.confirm('Reset all predictions, alerts, and agent telemetry in SQLite?')) return;
    setIsResetting(true);
    try {
      await resetDatabase();
      setOrchestrationResult(null);
      await loadData();
    } catch (err) {
      alert(`Reset failed: ${err.message}`);
    } finally {
      setIsResetting(false);
    }
  };

  // Inspect 78 Features for a flow
  const handleInspectRecord = async (recordId) => {
    try {
      const detail = await fetchPredictionDetail(recordId);
      setSelectedRecord(detail);
      setIsFeatureModalOpen(true);
    } catch (err) {
      alert(`Could not load record details: ${err.message}`);
    }
  };

  // Inspect Agent Execution Logs
  const handleInspectExecution = async (execId) => {
    try {
      const detail = await fetchExecutionDetail(execId);
      setSelectedExecution(detail);
      setIsExecutionLogModalOpen(true);
    } catch (err) {
      alert(`Could not load execution logs: ${err.message}`);
    }
  };

  // Agent Management Actions
  const handleCreateAgent = async (agentData) => {
    await createAgent(agentData);
    await loadData();
  };

  const handleToggleAgentStatus = async (agentId, newStatus) => {
    try {
      await updateAgentStatus(agentId, newStatus);
      await loadData();
    } catch (err) {
      alert(`Status update failed: ${err.message}`);
    }
  };

  const handleRunTask = async (agentId, taskName, payload) => {
    const res = await executeAgentTask(agentId, taskName, payload);
    await loadData();
    handleInspectExecution(res.execution_id);
  };

  // Multi-Agent Pipeline Orchestration
  const handleRunOrchestration = async () => {
    setIsOrchestrating(true);
    try {
      const result = await runMultiAgentOrchestration();
      setOrchestrationResult(result);
      await loadData();
    } catch (err) {
      alert(`Orchestration failed: ${err.message}`);
    } finally {
      setIsOrchestrating(false);
    }
  };

  // Fault Injection Failure Test
  const handleTriggerFault = async () => {
    setIsFaulting(true);
    try {
      const result = await triggerFaultInjection('agent-ml-triage', 'CORRUPTED_PAYLOAD');
      await loadData();
      alert(`Fault Injection Completed!\n\nStatus: ${result.status}\nError: ${result.error_message}\nGenerated Alert ID: #${result.generated_alert_id}`);
      handleInspectExecution(result.execution_id);
    } catch (err) {
      alert(`Fault injection failed: ${err.message}`);
    } finally {
      setIsFaulting(false);
    }
  };

  // Human-in-the-Loop Actions
  const handleOpenDecisionModal = (approval) => {
    setSelectedApproval(approval);
    setIsApprovalModalOpen(true);
  };

  const handleDecisionSubmit = async (approvalId, decision, notes) => {
    await submitApprovalDecision(approvalId, decision, notes);
    await loadData();
  };

  // Security Alert Actions
  const handleAcknowledgeAlert = async (alertId) => {
    try {
      await acknowledgeAlert(alertId);
      await loadData();
    } catch (err) {
      alert(`Could not acknowledge alert: ${err.message}`);
    }
  };

  const handleResolveAlert = async (alertId) => {
    try {
      await resolveAlert(alertId);
      await loadData();
    } catch (err) {
      alert(`Could not resolve alert: ${err.message}`);
    }
  };

  // Header Titles Map
  const tabTitles = {
    dashboard: { title: 'SOC Operational Dashboard', subtitle: 'Live telemetry, threat ratios, active alerts, and engine status' },
    agents: { title: 'AI Agent Management & Multi-Agent Orchestration', subtitle: 'Autonomous agent instances, pipeline coordination, and fault testing' },
    monitoring: { title: 'Agent Performance & Execution Telemetry', subtitle: 'Duration, token consumption, estimated inference costs, and audit logs' },
    approvals: { title: 'Human-In-The-Loop Approval Center', subtitle: 'Authorize or deny high-severity containment actions proposed by agents' },
    traffic: { title: 'Network Traffic Ingestion & Classification', subtitle: 'Upload CSV flows, validate 78 CIC-IDS2017 features, and run ML predictions' },
    alerts: { title: 'Security Alert Management', subtitle: 'Real-time incident feed, severity classification, and analyst triage' },
    history: { title: 'Prediction Ledger & History', subtitle: 'Full record of all network flows processed by the Scikit-learn model' },
    analytics: { title: 'Security Analytics & Threat Trends', subtitle: 'Multi-dimensional attack distributions, targeted ports, and timeline patterns' },
    model: { title: 'Machine Learning Model Specifications', subtitle: 'Random Forest architecture, 78 feature definitions, and pipeline details' },
  };

  const pendingApprovalsCount = approvals.filter(a => a.status === 'PENDING').length;
  const activeAlertsCount = alerts.filter(a => a.status === 'ACTIVE').length;

  return (
    <div className="flex h-screen overflow-hidden bg-navy-950 text-slate-100 font-sans">
      {/* Sidebar Navigation */}
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        activeAlertsCount={activeAlertsCount}
        pendingApprovalsCount={pendingApprovalsCount}
        systemStatus={systemStatus}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header
          title={tabTitles[currentTab]?.title || 'AlertIQ AI'}
          subtitle={tabTitles[currentTab]?.subtitle || ''}
          onRefresh={loadData}
          onSeedDemo={handleSeedDemo}
          onResetDb={handleResetDb}
          isRefreshing={isRefreshing}
          isSeeding={isSeeding}
          isResetting={isResetting}
        />

        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {currentTab === 'dashboard' && (
            <Dashboard
              stats={dashboardStats}
              systemStatus={systemStatus}
              onNavigate={setCurrentTab}
              onInspectRecord={handleInspectRecord}
              onAcknowledgeAlert={handleAcknowledgeAlert}
              onResolveAlert={handleResolveAlert}
            />
          )}

          {currentTab === 'agents' && (
            <AgentManagement
              agents={agents}
              onOpenCreateModal={() => setIsCreateAgentOpen(true)}
              onOpenRunTaskModal={(ag) => setSelectedAgentForTask(ag)}
              onToggleAgentStatus={handleToggleAgentStatus}
              onRunOrchestration={handleRunOrchestration}
              onTriggerFault={handleTriggerFault}
              isOrchestrating={isOrchestrating}
              isFaulting={isFaulting}
              orchestrationResult={orchestrationResult}
            />
          )}

          {currentTab === 'monitoring' && (
            <AgentMonitoring
              metrics={agentMetrics}
              executions={executions}
              onInspectExecution={handleInspectExecution}
            />
          )}

          {currentTab === 'approvals' && (
            <ApprovalsCenter
              approvals={approvals}
              onOpenDecisionModal={handleOpenDecisionModal}
            />
          )}

          {currentTab === 'traffic' && (
            <TrafficAnalysis
              onInspectRecord={handleInspectRecord}
              onAnalysisComplete={loadData}
            />
          )}

          {currentTab === 'alerts' && (
            <Alerts
              alerts={alerts}
              onAcknowledge={handleAcknowledgeAlert}
              onResolve={handleResolveAlert}
              statusFilter={alertStatusFilter}
              setStatusFilter={setAlertStatusFilter}
              severityFilter={alertSeverityFilter}
              setSeverityFilter={setAlertSeverityFilter}
            />
          )}

          {currentTab === 'history' && (
            <History
              historyData={historyData}
              onInspectRecord={handleInspectRecord}
              classFilter={historyClassFilter}
              setClassFilter={setHistoryClassFilter}
              searchTerm={historySearchTerm}
              setSearchTerm={setHistorySearchTerm}
            />
          )}

          {currentTab === 'analytics' && (
            <Analytics analyticsData={analyticsData} />
          )}

          {currentTab === 'model' && (
            <ModelInfo modelInfo={modelInfo} />
          )}
        </main>
      </div>

      {/* Modals */}
      <FeatureModal
        isOpen={isFeatureModalOpen}
        onClose={() => setIsFeatureModalOpen(false)}
        record={selectedRecord}
      />

      <ExecutionLogModal
        isOpen={isExecutionLogModalOpen}
        onClose={() => setIsExecutionLogModalOpen(false)}
        execution={selectedExecution}
      />

      <CreateAgentModal
        isOpen={isCreateAgentOpen}
        onClose={() => setIsCreateAgentOpen(false)}
        onCreateAgent={handleCreateAgent}
      />

      <RunTaskModal
        isOpen={!!selectedAgentForTask}
        onClose={() => setSelectedAgentForTask(null)}
        agent={selectedAgentForTask}
        onRunTask={handleRunTask}
      />

      <ApprovalDecisionModal
        isOpen={isApprovalModalOpen}
        onClose={() => setIsApprovalModalOpen(false)}
        approval={selectedApproval}
        onDecide={handleDecisionSubmit}
      />
    </div>
  );
}

export default App;

/**
 * AlertIQ AI - Frontend API Service
 * Encapsulates all RESTful communication with the FastAPI backend.
 * Uses clean, standard fetch requests easily explainable by second-year students.
 */

const API_BASE = '/api';

/**
 * Checks system health, backend state, and ML model status.
 */
export async function fetchSystemStatus() {
  const res = await fetch(`${API_BASE}/status`);
  if (!res.ok) throw new Error('Failed to fetch system status');
  return res.json();
}

/**
 * Retrieves ML model metadata and the list of 78 input features.
 */
export async function fetchModelInfo() {
  const res = await fetch(`${API_BASE}/model-info`);
  if (!res.ok) throw new Error('Failed to fetch model info');
  return res.json();
}

/**
 * Fetches dashboard summary statistics from SQLite.
 */
export async function fetchDashboardStats() {
  const res = await fetch(`${API_BASE}/dashboard/stats`);
  if (!res.ok) throw new Error('Failed to load dashboard statistics');
  return res.json();
}

/**
 * Uploads a network traffic CSV file for analysis and intrusion detection.
 */
export async function uploadTrafficCsv(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/traffic/upload`, {
    method: 'POST',
    body: formData,
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Failed to process CSV file');
  }
  return data;
}


/**
 * Uploads multiple network traffic CSV files for batch analysis.
 */
export async function uploadMultipleTrafficCsv(files) {
  const formData = new FormData();

  files.forEach((file) => {
    formData.append('files', file);
  });

  const res = await fetch(`${API_BASE}/traffic/upload-multiple`, {
    method: 'POST',
    body: formData,
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || 'Failed to process CSV files');
  }

  return data;
}

/**
 * Tests an individual flow through predict_alert().
 */
export async function predictSingleFlow(features, sourceLabel = 'manual_test') {
  const res = await fetch(`${API_BASE}/traffic/predict-single`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ features, source_label: sourceLabel }),
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Prediction failed');
  return data;
}

/**
 * Returns downloadable sample CSV URL.
 */
export function getSampleCsvUrl() {
  return `${API_BASE}/traffic/sample-csv`;
}

/**
 * Returns downloadable sample template CSV URL.
 */
export function getSampleTemplateUrl() {
  return `${API_BASE}/traffic/sample-template`;
}

/**
 * Retrieves security alerts with optional status and severity filtering.
 */
export async function fetchAlerts(status = 'ALL', severity = 'ALL', limit = 50, offset = 0) {
  const params = new URLSearchParams({ status, severity, limit, offset });
  const res = await fetch(`${API_BASE}/alerts?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch alerts');
  return res.json();
}

/**
 * Marks an alert as ACKNOWLEDGED.
 */
export async function acknowledgeAlert(alertId) {
  const res = await fetch(`${API_BASE}/alerts/${alertId}/acknowledge`, {
    method: 'PATCH',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Failed to acknowledge alert');
  return data;
}

/**
 * Marks an alert as RESOLVED.
 */
export async function resolveAlert(alertId) {
  const res = await fetch(`${API_BASE}/alerts/${alertId}/resolve`, {
    method: 'PATCH',
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Failed to resolve alert');
  return data;
}

/**
 * Fetches prediction history with pagination and search/class filters.
 */
export async function fetchHistory(filter = 'ALL', search = '', limit = 50, offset = 0) {
  const params = new URLSearchParams({ filter_class: filter, search, limit, offset });
  const res = await fetch(`${API_BASE}/history?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch prediction history');
  return res.json();
}

/**
 * Retrieves full 78-feature details for a specific prediction record.
 */
export async function fetchPredictionDetail(predictionId) {
  const res = await fetch(`${API_BASE}/history/${predictionId}`);
  if (!res.ok) throw new Error('Failed to fetch prediction details');
  return res.json();
}

/**
 * Retrieves aggregated statistics for the Analytics charts.
 */
export async function fetchAnalytics() {
  const res = await fetch(`${API_BASE}/analytics`);
  if (!res.ok) throw new Error('Failed to fetch analytics');
  return res.json();
}

/**
 * Clears database records for clean testing demonstrations.
 */
export async function resetDatabase() {
  const res = await fetch(`${API_BASE}/data/reset`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to reset database');
  return res.json();
}

/**
 * Seeds sample traffic flows for instant demo.
 */
export async function seedSampleTraffic() {
  const res = await fetch(`${API_BASE}/data/seed-sample`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to seed sample data');
  return res.json();
}

// =====================================================================
// AGENT MANAGEMENT & ORCHESTRATION APIS
// =====================================================================

/**
 * Retrieves all registered AI agents.
 */
export async function fetchAgents() {
  const res = await fetch(`${API_BASE}/agents`);
  if (!res.ok) throw new Error('Failed to fetch agents');
  return res.json();
}

/**
 * Registers a new agent.
 */
export async function createAgent(agentData) {
  const res = await fetch(`${API_BASE}/agents`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(agentData),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Failed to create agent');
  return data;
}

/**
 * Starts, stops, or changes agent status.
 */
export async function updateAgentStatus(agentId, status) {
  const res = await fetch(`${API_BASE}/agents/${agentId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Failed to update agent status');
  return data;
}

/**
 * Runs a task on an individual agent.
 */
export async function executeAgentTask(agentId, taskName, payload = null) {
  const res = await fetch(`${API_BASE}/agents/${agentId}/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task_name: taskName, payload }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Task execution failed');
  return data;
}

/**
 * Fetches recent agent executions with status filtering.
 */
export async function fetchExecutions(agentId = null, status = 'ALL', limit = 50) {
  const params = new URLSearchParams({ status, limit });
  if (agentId) params.append('agent_id', agentId);
  const res = await fetch(`${API_BASE}/executions?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch executions');
  return res.json();
}

/**
 * Retrieves full execution details and step-by-step audit logs.
 */
export async function fetchExecutionDetail(executionId) {
  const res = await fetch(`${API_BASE}/executions/${executionId}`);
  if (!res.ok) throw new Error('Failed to fetch execution logs');
  return res.json();
}

/**
 * Retrieves human-in-the-loop pending approval requests.
 */
export async function fetchApprovals(status = 'ALL', limit = 50) {
  const params = new URLSearchParams({ status, limit });
  const res = await fetch(`${API_BASE}/approvals?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch approvals');
  return res.json();
}

/**
 * Submits an approval or rejection decision.
 */
export async function submitApprovalDecision(approvalId, decision, notes = '') {
  const res = await fetch(`${API_BASE}/approvals/${approvalId}/decide`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ decision, notes }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Failed to submit decision');
  return data;
}

/**
 * Triggers the 4-agent multi-agent orchestration pipeline.
 */
export async function runMultiAgentOrchestration() {
  const res = await fetch(`${API_BASE}/orchestration/run`, { method: 'POST' });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Orchestration pipeline failed');
  return data;
}

/**
 * Triggers a fault injection scenario to test error handling & alert generation.
 */
export async function triggerFaultInjection(agentId = 'agent-ml-triage', failureType = 'CORRUPTED_PAYLOAD') {
  const res = await fetch(`${API_BASE}/orchestration/fault-injection`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ agent_id: agentId, failure_type: failureType }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Fault injection failed');
  return data;
}

/**
 * Fetches token, cost, and duration monitoring metrics.
 */
export async function fetchAgentMetrics() {
  const res = await fetch(`${API_BASE}/agent-metrics`);
  if (!res.ok) throw new Error('Failed to fetch agent metrics');
  return res.json();
}

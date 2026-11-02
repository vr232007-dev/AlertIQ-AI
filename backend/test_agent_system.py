"""
AlertIQ AI - Complete Agent AI System Test Suite
Verifies all 9 mandatory user journey steps:
1. Open dashboard & inspect system metrics
2. Create or select an agent
3. Execute an agent task
4. View execution logs
5. Trigger a failure scenario
6. Generate or display an alert
7. Submit a human approval request
8. Approve or reject it
9. Verify that the workflow reflects the decision
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.main import (
    list_registered_agents,
    register_new_agent,
    CreateAgentRequest,
    change_agent_status,
    UpdateAgentStatusRequest,
    run_agent_task,
    ExecuteTaskRequest,
    list_agent_executions,
    get_execution_logs,
    list_approvals,
    submit_approval_decision,
    ApprovalDecisionRequest,
    trigger_fault_injection,
    FaultInjectionRequest,
    trigger_orchestration_pipeline,
    get_agent_monitoring_metrics,
    list_alerts
)
from backend.database import init_db

def test_full_agent_user_journey():
    print("=" * 65)
    print("TESTING FULL HACKATHON AGENT AI USER JOURNEY")
    print("=" * 65)

    # 1. Open dashboard & inspect system metrics
    init_db()
    metrics = get_agent_monitoring_metrics()
    assert "total_executions" in metrics
    assert "cost_mode" in metrics and metrics["cost_mode"] == "ESTIMATED_TELEMETRY"
    print(f"[PASS] 1. Dashboard Metrics Loaded: {metrics['total_executions']} total runs, Cost Mode={metrics['cost_mode']}")

    # 2. Create or select an agent
    agents = list_registered_agents()
    assert len(agents) >= 4, "Default 4 agents must be seeded"
    print(f"[PASS] 2a. Default Agents Seeded: {[a['agent_id'] for a in agents]}")

    # Register a new custom agent
    new_agent_req = CreateAgentRequest(
        name="Zero-Day Hunter",
        role="Heuristic Threat Analyzer",
        model_provider="Random Forest Ensemble",
        description="Scans network flow outliers for previously unobserved zero-day attack vectors."
    )
    created_agent = register_new_agent(new_agent_req)
    assert created_agent["name"] == "Zero-Day Hunter"
    assert created_agent["status"] == "IDLE"
    print(f"[PASS] 2b. Created New Agent: ID={created_agent['agent_id']}, Role={created_agent['role']}")

    # Start the agent (update status)
    status_res = change_agent_status(created_agent["agent_id"], UpdateAgentStatusRequest(status="RUNNING"))
    assert status_res["status"] == "RUNNING"
    print(f"[PASS] 2c. Agent Started: Status={status_res['status']}")

    # 3. Execute an agent task
    sample_payload = {"Destination Port": 443, "Flow Duration": 2400}
    task_res = run_agent_task(
        agent_id="agent-ml-triage",
        req=ExecuteTaskRequest(task_name="Analyze Encrypted HTTPS Flow", payload=sample_payload)
    )
    assert task_res["status"] == "SUCCESS"
    assert "classification" in task_res["output"]
    assert task_res["tokens_total"] > 0
    assert task_res["duration_ms"] >= 0
    exec_id = task_res["execution_id"]
    print(f"[PASS] 3. Agent Task Executed: Exec ID={exec_id}, Classification={task_res['output']['classification']}, Tokens={task_res['tokens_total']}, Latency={task_res['duration_ms']}ms")

    # 4. View execution logs
    exec_detail = get_execution_logs(exec_id)
    assert len(exec_detail["logs"]) >= 2
    log_messages = [l["message"] for l in exec_detail["logs"]]
    print(f"[PASS] 4. Execution Logs Verified: {len(exec_detail['logs'])} step logs retrieved.")
    for l in exec_detail["logs"][:2]:
        print(f"      [{l['level']}] {l['message']}")

    # 5. Trigger a failure scenario
    fault_res = trigger_fault_injection(FaultInjectionRequest(
        agent_id="agent-ml-triage",
        failure_type="CORRUPTED_PAYLOAD"
    ))
    assert fault_res["status"] == "FAILED"
    assert "ValidationError" in fault_res["error_message"]
    generated_alert_id = fault_res["generated_alert_id"]
    print(f"[PASS] 5. Failure Scenario Triggered: Error='{fault_res['error_message'][:50]}...'")

    # 6. Generate or display an alert
    alerts = list_alerts(status="ACTIVE")
    alert_ids = [a["id"] for a in alerts["alerts"]]
    assert generated_alert_id in alert_ids
    matching_alert = next(a for a in alerts["alerts"] if a["id"] == generated_alert_id)
    assert matching_alert["severity"] == "CRITICAL"
    assert "Agent Execution Failure" in matching_alert["title"]
    print(f"[PASS] 6. Alert Generated for Failure: ID={generated_alert_id}, Title='{matching_alert['title']}' ({matching_alert['severity']})")

    # 7. Submit a human approval request via multi-agent orchestration
    pipeline_res = trigger_orchestration_pipeline()
    assert pipeline_res["workflow_id"].startswith("wf-")
    assert pipeline_res["status"] in ["COMPLETED_WITH_HITL_PENDING", "SUCCESS"]
    approval_id = pipeline_res["approval_id"]
    assert approval_id is not None, "Attack flow must generate an approval request for SOC response"
    print(f"[PASS] 7. Human Approval Request Submitted: Approval ID={approval_id} via Workflow {pipeline_res['workflow_id']}")

    # 8. Approve or reject it
    # First verify it is in PENDING list
    pending_approvals = list_approvals(status="PENDING")
    pending_ids = [a["approval_id"] for a in pending_approvals]
    assert approval_id in pending_ids

    # Approve the request
    decision_res = submit_approval_decision(
        approval_id=approval_id,
        req=ApprovalDecisionRequest(decision="APPROVED", notes="Approved firewall isolation following confirmed intrusion detection.")
    )
    assert decision_res["status"] == "APPROVED"
    print(f"[PASS] 8. Human Decision Recorded: {decision_res['status']} on Approval ID={approval_id}")

    # 9. Verify that the workflow reflects the decision
    updated_approvals = list_approvals(status="APPROVED")
    approved_ids = [a["approval_id"] for a in updated_approvals]
    assert approval_id in approved_ids

    # Verify underlying execution marked SUCCESS with approval notes
    appr_exec_detail = get_execution_logs(decision_res["execution_id"])
    assert appr_exec_detail["status"] == "SUCCESS"
    assert appr_exec_detail["output_result"]["approval_decision"] == "APPROVED"
    assert "Approved firewall isolation" in appr_exec_detail["output_result"]["notes"]
    print(f"[PASS] 9. Workflow State Updated: Execution {decision_res['execution_id']} reflects 'APPROVED' with analyst notes.")

    print("=" * 65)
    print("ALL 9 CORE USER JOURNEY TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    test_full_agent_user_journey()

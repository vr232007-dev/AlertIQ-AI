"""
AlertIQ AI - FastAPI Backend Server
Provides RESTful APIs for network traffic prediction, security alerts,
prediction history, analytics, and ML model information.
"""

import sys
import io
import json
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Add project root to sys.path to easily import machine_learning and backend modules
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from machine_learning.ai_engine import (
    predict_alert,
    predict_batch,
    get_model_info,
    EXPECTED_FEATURES,
    MODEL_VERSION
)
from backend.database import (
    init_db,
    save_prediction,
    save_predictions_batch,
    get_dashboard_stats,
    get_alerts,
    acknowledge_alert,
    resolve_alert,
    get_history,
    get_prediction_detail,
    get_analytics_data,
    clear_all_data,
    get_agents,
    get_agent,
    create_agent,
    update_agent_status,
    get_executions,
    get_execution_detail,
    get_approvals,
    record_approval_decision,
    get_agent_metrics
)
from backend.agent_engine import (
    execute_agent_task,
    trigger_failure_scenario,
    execute_multi_agent_pipeline
)
import pandas as pd

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database on startup
    init_db()
    yield

# Initialize FastAPI application
app = FastAPI(
    title="AlertIQ AI - Network Intrusion Detection API",
    description="Machine Learning Powered Network Intrusion Detection & Alerting System",
    version=MODEL_VERSION,
    lifespan=lifespan
)

# Enable CORS so the React frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================================
# 1. STATUS & MODEL INFORMATION ENDPOINTS
# =====================================================================

@app.get("/api/status")
def get_system_status():
    """
    Returns the real-time status of the backend API and the loaded ML model.
    """
    return {
        "status": "online",
        "backend": "FastAPI",
        "model_status": "ready",
        "model_version": MODEL_VERSION,
        "feature_count": len(EXPECTED_FEATURES)
    }


@app.get("/api/model-info")
def get_model_information():
    """
    Returns detailed metadata about the Random Forest model and its 78 features.
    """
    return get_model_info()


# =====================================================================
# 2. DASHBOARD ENDPOINT
# =====================================================================

@app.get("/api/dashboard/stats")
def get_dashboard_metrics():
    """
    Retrieves all dashboard statistics computed directly from the SQLite database.
    """
    stats = get_dashboard_stats()
    stats["model_status"] = "ready"
    stats["backend_status"] = "online"
    stats["model_version"] = MODEL_VERSION
    return stats


# =====================================================================
# 3. TRAFFIC ANALYSIS & CSV PREDICTION ENDPOINTS
# =====================================================================

@app.post("/api/traffic/upload")
def upload_traffic_csv(file: UploadFile = File(...)):
    """
    Accepts a network traffic CSV file, validates all 78 required features,
    runs the ML model prediction, and generates security alerts for ATTACK flows.
    """
    # 1. Validate file format
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload a .csv network traffic file."
        )

    try:
        # Read file contents directly from the underlying file stream
        content = file.file.read() if hasattr(file, "file") and file.file is not None else file.read()
        # Parse CSV into a pandas DataFrame
        df = pd.read_csv(io.BytesIO(content), low_memory=False)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to read CSV file: {str(e)}"
        )

    if df.empty:
        raise HTTPException(
            status_code=400,
            detail="The uploaded CSV file is empty."
        )

    # Clean whitespace from column headers
    df.columns = df.columns.str.strip()

    # If the CSV has a label or target column (e.g. from an existing dataset), drop it before validation
    for label_col in ["Label", "label", "target", "Target", "Class", "class"]:
        if label_col in df.columns:
            df = df.drop(columns=[label_col])

    # 2. Validate that all 78 features required by the trained model exist in the CSV
    missing_features = [f for f in EXPECTED_FEATURES if f not in df.columns]
    if missing_features:
        missing_preview = missing_features[:5]
        extra_count = len(missing_features) - len(missing_preview)
        msg = f"CSV validation failed: Missing {len(missing_features)} of the 78 required CIC-IDS2017 features. Missing: {', '.join(missing_preview)}"
        if extra_count > 0:
            msg += f" and {extra_count} more."
        raise HTTPException(status_code=400, detail=msg)

    # 3. Run predictions using the ML model
    try:
        predictions = predict_batch(df)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing ML model predictions: {str(e)}"
        )

    # 4. Prepare records to save in SQLite and return to frontend
    records_to_save = []
    response_items = []

    for i, pred in enumerate(predictions):
        row = df.iloc[i]

        dst_port = int(row.get("Destination Port", 0)) if pd.notnull(row.get("Destination Port")) else 0
        flow_duration = float(row.get("Flow Duration", 0.0)) if pd.notnull(row.get("Flow Duration")) else 0.0
        total_fwd = float(row.get("Total Fwd Packets", 0.0)) if pd.notnull(row.get("Total Fwd Packets")) else 0.0
        total_bwd = float(row.get("Total Backward Packets", 0.0)) if pd.notnull(row.get("Total Backward Packets")) else 0.0
        bytes_sec = float(row.get("Flow Bytes/s", 0.0)) if pd.notnull(row.get("Flow Bytes/s")) else 0.0
        pkts_sec = float(row.get("Flow Packets/s", 0.0)) if pd.notnull(row.get("Flow Packets/s")) else 0.0

        # Extract features dictionary for inspection
        features_dict = {col: (float(val) if pd.notnull(val) else 0.0) for col, val in row.items()}

        record = {
            "source_filename": file.filename,
            "predicted_class": pred["predicted_class"],
            "attack_probability": pred["attack_probability"],
            "destination_port": dst_port,
            "flow_duration": flow_duration,
            "total_fwd_packets": total_fwd,
            "total_bwd_packets": total_bwd,
            "flow_bytes_per_sec": bytes_sec,
            "flow_packets_per_sec": pkts_sec,
            "features": features_dict
        }
        records_to_save.append(record)

        # Include preview fields for the frontend response table
        response_items.append({
            "row_index": i + 1,
            "predicted_class": pred["predicted_class"],
            "attack_probability": pred["attack_probability"],
            "destination_port": dst_port,
            "flow_duration": flow_duration,
            "total_packets": int(total_fwd + total_bwd)
        })

    # 5. Save all predictions and generated alerts in the database
    batch_summary = save_predictions_batch(records_to_save)

    return {
        "filename": file.filename,
        "summary": batch_summary,
        "results": response_items[:100],  # Return first 100 rows for preview
        "has_more": len(response_items) > 100
    }


@app.post("/api/traffic/upload-multiple")
def upload_multiple_traffic_csv(files: list[UploadFile] = File(...)):
    """
    Accepts multiple CSV files and analyzes each using the existing
    Random Forest prediction and database-saving pipeline.
    """
    if not files:
        raise HTTPException(
            status_code=400,
            detail="Please select at least one CSV file."
        )

    combined_summary = {
        "total_analyzed": 0,
        "benign_count": 0,
        "attack_count": 0,
        "alerts_created": 0
    }

    combined_results = []
    successful_files = []
    failed_files = []
    global_row_index = 1

    for uploaded_file in files:
        filename = uploaded_file.filename or "unknown.csv"

        try:
            # Reuse the existing single-file analysis function.
            result = upload_traffic_csv(uploaded_file)

            successful_files.append(filename)

            # Add this file's statistics to the combined totals.
            for key in combined_summary:
                combined_summary[key] += result["summary"][key]

            # Combine the individual prediction previews.
            for row in result["results"]:
                combined_results.append({
                    **row,
                    "row_index": global_row_index,
                    "source_filename": filename,
                    "file_row_index": row["row_index"]
                })
                global_row_index += 1

        except HTTPException as error:
            failed_files.append({
                "filename": filename,
                "reason": str(error.detail)
            })

        except Exception as error:
            failed_files.append({
                "filename": filename,
                "reason": str(error)
            })

    return {
        "filenames": successful_files,
        "summary": combined_summary,
        "results": combined_results[:100],
        "has_more": len(combined_results) > 100,
        "successful_files": successful_files,
        "failed_files": failed_files
    }

class SingleFlowRequest(BaseModel):
    features: Dict[str, Any]
    source_label: Optional[str] = "single_test_flow"


@app.post("/api/traffic/predict-single")
def predict_single_flow(request: SingleFlowRequest):
    """
    Tests an individual network flow by passing its 78 features to predict_alert().
    """
    result = predict_alert(request.features)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    dst_port = int(request.features.get("Destination Port", 0))
    flow_duration = float(request.features.get("Flow Duration", 0.0))
    fwd_pkts = float(request.features.get("Total Fwd Packets", 0.0))
    bwd_pkts = float(request.features.get("Total Backward Packets", 0.0))

    pred_id = save_prediction(
        predicted_class=result["predicted_class"],
        attack_probability=result["attack_probability"],
        source_filename=request.source_label,
        destination_port=dst_port,
        flow_duration=flow_duration,
        total_fwd_packets=fwd_pkts,
        total_bwd_packets=bwd_pkts,
        features_dict=request.features
    )

    return {
        "prediction_id": pred_id,
        "predicted_class": result["predicted_class"],
        "attack_probability": result["attack_probability"],
        "model_version": result["model_version"]
    }


# =====================================================================
# 4. SAMPLE CSV DOWNLOAD ENDPOINTS
# =====================================================================

@app.get("/api/traffic/sample-csv")
def download_sample_csv():
    """
    Provides a downloadable sample CSV with 20 real network traffic records
    (a realistic mix of BENIGN and ATTACK flows) with all 78 required features.
    """
    sample_file = ROOT_DIR / "data" / "samples" / "sample_traffic.csv"
    if not sample_file.exists():
        from backend.sample_data import generate_sample_files
        generate_sample_files()

    return FileResponse(
        path=sample_file,
        filename="alertiq_sample_traffic.csv",
        media_type="text/csv"
    )


@app.get("/api/traffic/sample-template")
def download_sample_template():
    """
    Provides an empty CSV template with all 78 required column headers.
    """
    template_file = ROOT_DIR / "data" / "samples" / "sample_template.csv"
    if not template_file.exists():
        from backend.sample_data import generate_sample_files
        generate_sample_files()

    return FileResponse(
        path=template_file,
        filename="alertiq_features_template.csv",
        media_type="text/csv"
    )


# =====================================================================
# 5. SECURITY ALERTS ENDPOINTS
# =====================================================================

@app.get("/api/alerts")
def list_alerts(
    status: str = "ALL",
    severity: str = "ALL",
    limit: int = 50,
    offset: int = 0
):
    """
    Returns security alerts from the database with filtering and pagination.
    """
    return get_alerts(status=status, severity=severity, limit=limit, offset=offset)


@app.patch("/api/alerts/{alert_id}/acknowledge")
def acknowledge_security_alert(alert_id: int):
    """
    Marks an active security alert as ACKNOWLEDGED.
    """
    success = acknowledge_alert(alert_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Alert with ID {alert_id} not found or not in ACTIVE state."
        )
    return {"message": f"Alert {alert_id} successfully acknowledged.", "status": "ACKNOWLEDGED"}


@app.patch("/api/alerts/{alert_id}/resolve")
def resolve_security_alert(alert_id: int):
    """
    Marks a security alert as RESOLVED.
    """
    success = resolve_alert(alert_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Alert with ID {alert_id} not found or already resolved."
        )
    return {"message": f"Alert {alert_id} successfully resolved.", "status": "RESOLVED"}


# =====================================================================
# 6. PREDICTION HISTORY ENDPOINTS
# =====================================================================

@app.get("/api/history")
def list_prediction_history(
    filter_class: str = "ALL",
    search: str = "",
    limit: int = 50,
    offset: int = 0
):
    """
    Retrieves stored prediction history records from SQLite.
    """
    return get_history(class_filter=filter_class, search=search, limit=limit, offset=offset)


@app.get("/api/history/{prediction_id}")
def get_prediction_by_id(prediction_id: int):
    """
    Retrieves full details of a single prediction, including all 78 feature values.
    """
    detail = get_prediction_detail(prediction_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Prediction {prediction_id} not found.")
    return detail


# =====================================================================
# 7. ANALYTICS ENDPOINT
# =====================================================================

@app.get("/api/analytics")
def get_analytics():
    """
    Returns aggregated metrics for charts: class distribution, severity breakdown,
    top targeted ports, and timeline trend data.
    """
    return get_analytics_data()


# =====================================================================
# 8. DATA MANAGEMENT & DEMO HELPER ENDPOINTS
# =====================================================================

@app.post("/api/data/reset")
def reset_database():
    """
    Clears all stored predictions and alerts so a fresh demonstration can be performed.
    """
    clear_all_data()
    return {"message": "All prediction and alert records have been cleared."}


@app.post("/api/data/seed-sample")
def seed_sample_traffic():
    """
    Loads the 20 sample traffic flows from sample_traffic.csv into the database
    to quickly demonstrate dashboard, alerts, and analytics.
    """
    sample_file = ROOT_DIR / "data" / "samples" / "sample_traffic.csv"
    if not sample_file.exists():
        from backend.sample_data import generate_sample_files
        generate_sample_files()

    df = pd.read_csv(sample_file)
    predictions = predict_batch(df)

    records = []
    for i, pred in enumerate(predictions):
        row = df.iloc[i]
        dst_port = int(row.get("Destination Port", 0))
        flow_duration = float(row.get("Flow Duration", 0.0))
        total_fwd = float(row.get("Total Fwd Packets", 0.0))
        total_bwd = float(row.get("Total Backward Packets", 0.0))
        bytes_sec = float(row.get("Flow Bytes/s", 0.0))
        pkts_sec = float(row.get("Flow Packets/s", 0.0))
        features_dict = {col: float(val) for col, val in row.items()}

        records.append({
            "source_filename": "sample_traffic.csv",
            "predicted_class": pred["predicted_class"],
            "attack_probability": pred["attack_probability"],
            "destination_port": dst_port,
            "flow_duration": flow_duration,
            "total_fwd_packets": total_fwd,
            "total_bwd_packets": total_bwd,
            "flow_bytes_per_sec": bytes_sec,
            "flow_packets_per_sec": pkts_sec,
            "features": features_dict
        })

    summary = save_predictions_batch(records)
    return {
        "message": "Sample traffic records seeded successfully.",
        "summary": summary
    }


# =====================================================================
# 9. AGENT MANAGEMENT ENDPOINTS
# =====================================================================

class CreateAgentRequest(BaseModel):
    name: str
    role: str
    model_provider: Optional[str] = "Scikit-Learn Random Forest (78-Feats)"
    description: Optional[str] = ""

class UpdateAgentStatusRequest(BaseModel):
    status: str

class ExecuteTaskRequest(BaseModel):
    task_name: str
    payload: Optional[Dict[str, Any]] = None

class ApprovalDecisionRequest(BaseModel):
    decision: str
    notes: Optional[str] = ""

class FaultInjectionRequest(BaseModel):
    agent_id: Optional[str] = "agent-ml-triage"
    failure_type: Optional[str] = "CORRUPTED_PAYLOAD"


@app.get("/api/agents")
def list_registered_agents():
    """
    Returns all registered AI agents with their roles, models, and current status.
    """
    return get_agents()


@app.post("/api/agents")
def register_new_agent(req: CreateAgentRequest):
    """
    Registers a new autonomous AI agent into the SQLite registry.
    """
    if not req.name.strip() or not req.role.strip():
        raise HTTPException(status_code=400, detail="Agent name and role cannot be empty.")
    agent = create_agent(
        name=req.name.strip(),
        role=req.role.strip(),
        model_provider=req.model_provider,
        description=req.description
    )
    return agent


@app.get("/api/agents/{agent_id}")
def get_agent_by_id(agent_id: str):
    """
    Retrieves details of a specific agent.
    """
    ag = get_agent(agent_id)
    if not ag:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found.")
    return ag


@app.patch("/api/agents/{agent_id}/status")
def change_agent_status(agent_id: str, req: UpdateAgentStatusRequest):
    """
    Starts, stops, or changes the operational state of an agent.
    """
    allowed_statuses = ["IDLE", "RUNNING", "STOPPED", "ERROR"]
    clean_status = req.status.upper()
    if clean_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{req.status}'. Allowed: {', '.join(allowed_statuses)}"
        )
    update_agent_status(agent_id, clean_status)
    return {"agent_id": agent_id, "status": clean_status}


@app.post("/api/agents/{agent_id}/execute")
def run_agent_task(agent_id: str, req: ExecuteTaskRequest):
    """
    Executes a task on an individual agent and logs its step-by-step telemetry.
    """
    result = execute_agent_task(
        agent_id=agent_id,
        task_name=req.task_name,
        payload=req.payload
    )
    return result


# =====================================================================
# 10. AGENT MONITORING & EXECUTION HISTORY ENDPOINTS
# =====================================================================

@app.get("/api/executions")
def list_agent_executions(
    agent_id: Optional[str] = None,
    status: str = "ALL",
    limit: int = 50
):
    """
    Returns recent agent executions, execution duration, and success/failure states.
    """
    return get_executions(agent_id=agent_id, status=status, limit=limit)


@app.get("/api/executions/{execution_id}")
def get_execution_logs(execution_id: str):
    """
    Retrieves full execution details and step-by-step audit logs.
    """
    detail = get_execution_detail(execution_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Execution '{execution_id}' not found.")
    return detail


# =====================================================================
# 11. HUMAN-IN-THE-LOOP (HITL) APPROVAL ENDPOINTS
# =====================================================================

@app.get("/api/approvals")
def list_approvals(status: str = "ALL", limit: int = 50):
    """
    Lists pending, approved, or rejected Human-In-The-Loop actions.
    """
    return get_approvals(status=status, limit=limit)


@app.post("/api/approvals/{approval_id}/decide")
def submit_approval_decision(approval_id: str, req: ApprovalDecisionRequest):
    """
    Allows a human analyst to APPROVE or REJECT a pending high-severity agent action.
    """
    res = record_approval_decision(
        approval_id=approval_id,
        decision=req.decision,
        notes=req.notes
    )
    if not res:
        raise HTTPException(status_code=404, detail=f"Approval '{approval_id}' not found.")
    return res


# =====================================================================
# 12. MULTI-AGENT ORCHESTRATION & FAULT INJECTION ENDPOINTS
# =====================================================================

@app.post("/api/orchestration/run")
def trigger_orchestration_pipeline():
    """
    Executes the multi-agent pipeline demonstrating inter-agent coordination:
    Ingestion -> ML Triage (Scikit-Learn model) -> SOC Response (HITL) -> Audit.
    """
    return execute_multi_agent_pipeline()


@app.post("/api/orchestration/fault-injection")
def trigger_fault_injection(req: FaultInjectionRequest):
    """
    Triggers an abnormal execution fault scenario and generates an alert.
    """
    return trigger_failure_scenario(
        agent_id=req.agent_id,
        failure_type=req.failure_type
    )


@app.get("/api/agent-metrics")
def get_agent_monitoring_metrics():
    """
    Returns performance metrics: tokens, estimated cost, average duration, active agents.
    """
    return get_agent_metrics()


from fastapi.staticfiles import StaticFiles

# =====================================================================
# 13. STATIC FRONTEND SPA SERVING (For Single-Command Demonstrations)
# =====================================================================

FRONTEND_DIST = ROOT_DIR / "frontend" / "dist"
if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend_spa(full_path: str):
        # Allow /api routes to be handled by FastAPI routers
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Endpoint not found")
        file_path = FRONTEND_DIST / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")



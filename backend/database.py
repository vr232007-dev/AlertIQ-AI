"""
AlertIQ AI - Database Module
Handles SQLite connection, schema creation, and queries for predictions and alerts.
Designed to be simple, self-contained, and easily explainable for student presentations.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

# Path to the SQLite database file
DB_PATH = Path(__file__).resolve().parent / "alertiq.db"


def get_db_connection():
    """
    Creates and returns a connection to the SQLite database.
    Row factory is set to sqlite3.Row to allow dictionary-like column access.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes database tables if they do not already exist.
    Creates tables for traffic predictions and security alerts.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Predictions Table: Stores every analyzed traffic flow record
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                source_filename TEXT DEFAULT 'manual_input.csv',
                predicted_class TEXT NOT NULL,
                attack_probability REAL NOT NULL,
                destination_port INTEGER DEFAULT 0,
                flow_duration REAL DEFAULT 0,
                total_fwd_packets REAL DEFAULT 0,
                total_bwd_packets REAL DEFAULT 0,
                flow_bytes_per_sec REAL DEFAULT 0,
                flow_packets_per_sec REAL DEFAULT 0,
                features_json TEXT
            )
        """)

        # 2. Alerts Table: Stores security incidents generated for ATTACK predictions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER,
                timestamp TEXT NOT NULL,
                title TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                destination_port INTEGER DEFAULT 0,
                attack_probability REAL NOT NULL,
                details TEXT,
                acknowledged_at TEXT,
                resolved_at TEXT,
                FOREIGN KEY (prediction_id) REFERENCES predictions(id) ON DELETE CASCADE
            )
        """)

        # 3. Agents Table: Stores AI Agent definitions, roles, models, and operational state
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                model_provider TEXT DEFAULT 'Scikit-Learn Random Forest (78-Feats)',
                status TEXT DEFAULT 'IDLE',
                description TEXT,
                total_runs INTEGER DEFAULT 0,
                successful_runs INTEGER DEFAULT 0,
                failed_runs INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # 4. Agent Executions Table: Tracks task runs, token telemetry, durations, and costs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT UNIQUE NOT NULL,
                agent_id TEXT NOT NULL,
                workflow_id TEXT DEFAULT NULL,
                task_name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'RUNNING',
                started_at TEXT NOT NULL,
                completed_at TEXT,
                duration_ms INTEGER DEFAULT 0,
                tokens_prompt INTEGER DEFAULT 0,
                tokens_completion INTEGER DEFAULT 0,
                tokens_total INTEGER DEFAULT 0,
                estimated_cost_usd REAL DEFAULT 0.0,
                cost_mode TEXT DEFAULT 'ESTIMATED_TELEMETRY',
                input_payload TEXT,
                output_result TEXT,
                error_message TEXT,
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
            )
        """)

        # 5. Execution Logs Table: Step-by-step audit logs for every agent execution
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                level TEXT DEFAULT 'INFO',
                message TEXT NOT NULL,
                details TEXT,
                FOREIGN KEY (execution_id) REFERENCES agent_executions(execution_id) ON DELETE CASCADE
            )
        """)

        # 6. Human-In-The-Loop (HITL) Approvals Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS approvals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                approval_id TEXT UNIQUE NOT NULL,
                execution_id TEXT NOT NULL,
                agent_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                resource_target TEXT NOT NULL,
                reason TEXT NOT NULL,
                severity TEXT DEFAULT 'HIGH',
                status TEXT DEFAULT 'PENDING',
                requested_at TEXT NOT NULL,
                decided_at TEXT,
                decision_notes TEXT,
                FOREIGN KEY (execution_id) REFERENCES agent_executions(execution_id),
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
            )
        """)

        # Indexes for fast querying
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pred_class ON predictions(predicted_class)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pred_timestamp ON predictions(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alert_status ON alerts(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alert_timestamp ON alerts(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_exec_agent ON agent_executions(agent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_exec_status ON agent_executions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_exec ON execution_logs(execution_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_approvals_status ON approvals(status)")

        conn.commit()

    # Seed default agents if none exist
    seed_default_agents()


def save_prediction(
    predicted_class: str,
    attack_probability: float,
    source_filename: str = "manual_input.csv",
    destination_port: int = 0,
    flow_duration: float = 0.0,
    total_fwd_packets: float = 0.0,
    total_bwd_packets: float = 0.0,
    flow_bytes_per_sec: float = 0.0,
    flow_packets_per_sec: float = 0.0,
    features_dict: dict = None,
    timestamp: str = None
) -> int:
    """
    Saves a single prediction record into the SQLite database.
    If the prediction is an ATTACK, also creates an automatic security alert.
    Returns the inserted prediction ID.
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    features_json = json.dumps(features_dict) if features_dict else "{}"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions (
                timestamp, source_filename, predicted_class, attack_probability,
                destination_port, flow_duration, total_fwd_packets, total_bwd_packets,
                flow_bytes_per_sec, flow_packets_per_sec, features_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, source_filename, predicted_class, attack_probability,
            destination_port, flow_duration, total_fwd_packets, total_bwd_packets,
            flow_bytes_per_sec, flow_packets_per_sec, features_json
        ))
        prediction_id = cursor.lastrowid

        # Generate alert if classified as ATTACK
        if predicted_class == "ATTACK":
            severity = determine_severity(attack_probability)
            title = f"Intrusion Detected on Port {destination_port}"
            details = (
                f"Suspicious flow detected. Attack confidence: {round(attack_probability * 100, 1)}%. "
                f"Packets: {int(total_fwd_packets + total_bwd_packets)}, "
                f"Duration: {round(flow_duration, 2)} ms."
            )
            cursor.execute("""
                INSERT INTO alerts (
                    prediction_id, timestamp, title, severity, status,
                    destination_port, attack_probability, details
                ) VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?, ?)
            """, (
                prediction_id, timestamp, title, severity,
                destination_port, attack_probability, details
            ))

        conn.commit()
        return prediction_id


def save_predictions_batch(records: list) -> dict:
    """
    Saves a list of prediction records in a single database transaction.
    Each record must be a dict containing fields required for prediction & alert.
    Returns summary statistics: total, benign_count, attack_count, alerts_created.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    benign_count = 0
    attack_count = 0
    alerts_created = 0

    with get_db_connection() as conn:
        cursor = conn.cursor()

        for rec in records:
            pred_class = rec.get("predicted_class", "BENIGN")
            prob = rec.get("attack_probability", 0.0)
            src_file = rec.get("source_filename", "uploaded_file.csv")
            dst_port = int(rec.get("destination_port", 0))
            duration = float(rec.get("flow_duration", 0.0))
            fwd_pkts = float(rec.get("total_fwd_packets", 0.0))
            bwd_pkts = float(rec.get("total_bwd_packets", 0.0))
            bytes_sec = float(rec.get("flow_bytes_per_sec", 0.0))
            pkts_sec = float(rec.get("flow_packets_per_sec", 0.0))
            features = json.dumps(rec.get("features", {}))

            cursor.execute("""
                INSERT INTO predictions (
                    timestamp, source_filename, predicted_class, attack_probability,
                    destination_port, flow_duration, total_fwd_packets, total_bwd_packets,
                    flow_bytes_per_sec, flow_packets_per_sec, features_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, src_file, pred_class, prob,
                dst_port, duration, fwd_pkts, bwd_pkts,
                bytes_sec, pkts_sec, features
            ))
            pred_id = cursor.lastrowid

            if pred_class == "ATTACK":
                attack_count += 1
                severity = determine_severity(prob)
                title = f"Intrusion Detected on Port {dst_port}"
                details = (
                    f"Suspicious flow detected. Attack confidence: {round(prob * 100, 1)}%. "
                    f"Packets: {int(fwd_pkts + bwd_pkts)}, Duration: {round(duration, 2)} ms."
                )
                cursor.execute("""
                    INSERT INTO alerts (
                        prediction_id, timestamp, title, severity, status,
                        destination_port, attack_probability, details
                    ) VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?, ?)
                """, (
                    pred_id, timestamp, title, severity,
                    dst_port, prob, details
                ))
                alerts_created += 1
            else:
                benign_count += 1

        conn.commit()

    return {
        "total_analyzed": len(records),
        "benign_count": benign_count,
        "attack_count": attack_count,
        "alerts_created": alerts_created
    }


def determine_severity(probability: float) -> str:
    """
    Determines alert severity based on the machine learning model's confidence.
    """
    if probability >= 0.85:
        return "CRITICAL"
    elif probability >= 0.70:
        return "HIGH"
    elif probability >= 0.50:
        return "MEDIUM"
    return "LOW"


def get_dashboard_stats() -> dict:
    """
    Calculates key metrics for the main dashboard display directly from SQLite.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Total traffic flows analyzed
        cursor.execute("SELECT COUNT(*) AS total FROM predictions")
        total_traffic = cursor.fetchone()["total"]

        # Benign vs Attack count
        cursor.execute("SELECT COUNT(*) AS benign FROM predictions WHERE predicted_class = 'BENIGN'")
        benign_count = cursor.fetchone()["benign"]

        cursor.execute("SELECT COUNT(*) AS attack FROM predictions WHERE predicted_class = 'ATTACK'")
        attack_count = cursor.fetchone()["attack"]

        # Active security alerts
        cursor.execute("SELECT COUNT(*) AS active_alerts FROM alerts WHERE status = 'ACTIVE'")
        active_alerts = cursor.fetchone()["active_alerts"]

        # Calculate attack percentage
        attack_percentage = round((attack_count / total_traffic * 100), 1) if total_traffic > 0 else 0.0

        # Recent predictions (last 6 records)
        cursor.execute("""
            SELECT id, timestamp, source_filename, predicted_class,
                   attack_probability, destination_port, flow_duration
            FROM predictions
            ORDER BY id DESC
            LIMIT 6
        """)
        recent_predictions = [dict(row) for row in cursor.fetchall()]

        # Recent active alerts (last 4 records)
        cursor.execute("""
            SELECT id, timestamp, title, severity, status, destination_port, attack_probability
            FROM alerts
            WHERE status = 'ACTIVE'
            ORDER BY id DESC
            LIMIT 4
        """)
        recent_alerts = [dict(row) for row in cursor.fetchall()]

    return {
        "total_traffic": total_traffic,
        "benign_count": benign_count,
        "attack_count": attack_count,
        "active_alerts": active_alerts,
        "attack_percentage": attack_percentage,
        "recent_predictions": recent_predictions,
        "recent_alerts": recent_alerts
    }


def get_alerts(status: str = "ALL", severity: str = "ALL", limit: int = 50, offset: int = 0) -> dict:
    """
    Retrieves filtered security alerts with total count.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        conditions = []
        params = []

        if status and status.upper() != "ALL":
            conditions.append("status = ?")
            params.append(status.upper())

        if severity and severity.upper() != "ALL":
            conditions.append("severity = ?")
            params.append(severity.upper())

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        # Get total matching count
        cursor.execute(f"SELECT COUNT(*) AS total FROM alerts {where_clause}", params)
        total = cursor.fetchone()["total"]

        # Get records
        query = f"""
            SELECT id, prediction_id, timestamp, title, severity, status,
                   destination_port, attack_probability, details, acknowledged_at, resolved_at
            FROM alerts
            {where_clause}
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [limit, offset])
        alerts = [dict(row) for row in cursor.fetchall()]

    return {
        "total": total,
        "alerts": alerts
    }


def acknowledge_alert(alert_id: int) -> bool:
    """
    Marks an alert as ACKNOWLEDGED and records the current timestamp.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE alerts
            SET status = 'ACKNOWLEDGED', acknowledged_at = ?
            WHERE id = ? AND status = 'ACTIVE'
        """, (now, alert_id))
        conn.commit()
        return cursor.rowcount > 0


def resolve_alert(alert_id: int) -> bool:
    """
    Marks an alert as RESOLVED and records the current timestamp.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE alerts
            SET status = 'RESOLVED', resolved_at = ?
            WHERE id = ? AND status != 'RESOLVED'
        """, (now, alert_id))
        conn.commit()
        return cursor.rowcount > 0


def get_history(class_filter: str = "ALL", search: str = "", limit: int = 50, offset: int = 0) -> dict:
    """
    Retrieves paginated prediction history with optional filtering.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        conditions = []
        params = []

        if class_filter and class_filter.upper() != "ALL":
            conditions.append("predicted_class = ?")
            params.append(class_filter.upper())

        if search:
            conditions.append("(source_filename LIKE ? OR CAST(destination_port AS TEXT) LIKE ?)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param])

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        # Total count
        cursor.execute(f"SELECT COUNT(*) AS total FROM predictions {where_clause}", params)
        total = cursor.fetchone()["total"]

        # Fetch records
        query = f"""
            SELECT id, timestamp, source_filename, predicted_class,
                   attack_probability, destination_port, flow_duration,
                   total_fwd_packets, total_bwd_packets, flow_bytes_per_sec, flow_packets_per_sec
            FROM predictions
            {where_clause}
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [limit, offset])
        records = [dict(row) for row in cursor.fetchall()]

    return {
        "total": total,
        "records": records
    }


def get_prediction_detail(prediction_id: int) -> dict:
    """
    Returns full details of a prediction including all 78 feature values.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, source_filename, predicted_class,
                   attack_probability, destination_port, flow_duration,
                   total_fwd_packets, total_bwd_packets, flow_bytes_per_sec,
                   flow_packets_per_sec, features_json
            FROM predictions
            WHERE id = ?
        """, (prediction_id,))
        row = cursor.fetchone()

        if not row:
            return None

        result = dict(row)
        try:
            result["features"] = json.loads(result.pop("features_json") or "{}")
        except Exception:
            result["features"] = {}

        return result


def get_analytics_data() -> dict:
    """
    Computes aggregated statistics for the Analytics page:
    - Attack vs Benign distribution
    - Severity breakdown
    - Top targeted destination ports
    - Prediction timeline / trends
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Distribution
        cursor.execute("SELECT COUNT(*) AS total FROM predictions")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS benign FROM predictions WHERE predicted_class = 'BENIGN'")
        benign = cursor.fetchone()["benign"]

        cursor.execute("SELECT COUNT(*) AS attack FROM predictions WHERE predicted_class = 'ATTACK'")
        attack = cursor.fetchone()["attack"]

        # Severity breakdown
        cursor.execute("""
            SELECT severity, COUNT(*) AS count
            FROM alerts
            GROUP BY severity
        """)
        severity_breakdown = {row["severity"]: row["count"] for row in cursor.fetchall()}

        # Top targeted ports for attacks
        cursor.execute("""
            SELECT destination_port, COUNT(*) AS count
            FROM predictions
            WHERE predicted_class = 'ATTACK' AND destination_port > 0
            GROUP BY destination_port
            ORDER BY count DESC
            LIMIT 5
        """)
        top_ports = [{"port": row["destination_port"], "attacks": row["count"]} for row in cursor.fetchall()]

        # Recent batch activity (grouped by source_filename or timestamp day)
        cursor.execute("""
            SELECT SUBSTR(timestamp, 1, 10) AS date_str,
                   SUM(CASE WHEN predicted_class = 'BENIGN' THEN 1 ELSE 0 END) AS benign,
                   SUM(CASE WHEN predicted_class = 'ATTACK' THEN 1 ELSE 0 END) AS attack
            FROM predictions
            GROUP BY date_str
            ORDER BY date_str ASC
            LIMIT 14
        """)
        trend_data = [
            {"date": row["date_str"], "benign": row["benign"], "attack": row["attack"]}
            for row in cursor.fetchall()
        ]

    return {
        "total_predictions": total,
        "benign_count": benign,
        "attack_count": attack,
        "attack_percentage": round((attack / total * 100), 1) if total > 0 else 0.0,
        "severity_breakdown": {
            "CRITICAL": severity_breakdown.get("CRITICAL", 0),
            "HIGH": severity_breakdown.get("HIGH", 0),
            "MEDIUM": severity_breakdown.get("MEDIUM", 0),
            "LOW": severity_breakdown.get("LOW", 0),
        },
        "top_ports": top_ports,
        "trend_data": trend_data
    }


def clear_all_data():
    """
    Resets the database tables for clean testing and demonstration.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alerts")
        cursor.execute("DELETE FROM predictions")
        cursor.execute("DELETE FROM approvals")
        cursor.execute("DELETE FROM execution_logs")
        cursor.execute("DELETE FROM agent_executions")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('alerts', 'predictions', 'approvals', 'execution_logs', 'agent_executions')")
        cursor.execute("UPDATE agents SET status = 'IDLE', total_runs = 0, successful_runs = 0, failed_runs = 0")
        conn.commit()


# =====================================================================
# AGENT MANAGEMENT & ORCHESTRATION HELPERS
# =====================================================================

DEFAULT_AGENTS = [
    {
        "agent_id": "agent-ingest",
        "name": "Traffic Ingestion Agent",
        "role": "Telemetry Collector & Normalizer",
        "model_provider": "Pandas Stream ETL",
        "description": "Ingests network capture files, cleans headers, and prepares 78-dimensional flow tensors."
    },
    {
        "agent_id": "agent-ml-triage",
        "name": "ML Intrusion Triage Agent",
        "role": "Anomaly & Intrusion Classifier",
        "model_provider": "Scikit-Learn Random Forest (78-Features)",
        "description": "Executes trained CIC-IDS2017 machine learning pipeline to detect Benign vs Attack flows with confidence scoring."
    },
    {
        "agent_id": "agent-mitigate",
        "name": "SOC Automated Response Agent",
        "role": "Firewall & Containment Orchestrator",
        "model_provider": "Rule & Policy Enforcement",
        "description": "Formulates containment actions (blocking IP, firewall rule updates) and triggers Human-In-The-Loop approvals for high-severity threats."
    },
    {
        "agent_id": "agent-audit",
        "name": "Audit & Compliance Agent",
        "role": "Security Ledger & SLA Auditor",
        "model_provider": "Audit Verifier",
        "description": "Records non-repudiable audit logs, computes latency/token telemetry, and maintains compliance records."
    }
]


def seed_default_agents():
    """
    Seeds the four foundational SOC agents if no agents currently exist in SQLite.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM agents")
        if cursor.fetchone()["total"] == 0:
            for ag in DEFAULT_AGENTS:
                cursor.execute("""
                    INSERT INTO agents (
                        agent_id, name, role, model_provider, status, description,
                        total_runs, successful_runs, failed_runs, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, 'IDLE', ?, 0, 0, 0, ?, ?)
                """, (
                    ag["agent_id"], ag["name"], ag["role"], ag["model_provider"],
                    ag["description"], now, now
                ))
            conn.commit()


def get_agents():
    """
    Returns all registered agents.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agents ORDER BY id ASC")
        return [dict(row) for row in cursor.fetchall()]


def get_agent(agent_id: str):
    """
    Returns a single agent by its agent_id.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agents WHERE agent_id = ?", (agent_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def create_agent(name: str, role: str, model_provider: str = "Scikit-Learn Random Forest", description: str = ""):
    """
    Creates and registers a new AI Agent.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    import re
    base_id = "agent-" + re.sub(r'[^a-zA-Z0-9]', '-', name.lower()).strip('-')[:20]
    unique_id = f"{base_id}-{int(datetime.now().timestamp()) % 10000}"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agents (
                agent_id, name, role, model_provider, status, description,
                total_runs, successful_runs, failed_runs, created_at, updated_at
            ) VALUES (?, ?, ?, ?, 'IDLE', ?, 0, 0, 0, ?, ?)
        """, (unique_id, name, role, model_provider, description, now, now))
        conn.commit()
    return get_agent(unique_id)


def update_agent_status(agent_id: str, status: str):
    """
    Updates the operational status of an agent (IDLE, RUNNING, STOPPED, ERROR).
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE agents
            SET status = ?, updated_at = ?
            WHERE agent_id = ?
        """, (status, now, agent_id))
        conn.commit()


def create_execution(agent_id: str, task_name: str, input_payload: dict = None, workflow_id: str = None) -> str:
    """
    Initializes a new execution run for an agent.
    """
    import uuid
    exec_id = f"exec-{uuid.uuid4().hex[:8]}"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agent_executions (
                execution_id, agent_id, workflow_id, task_name, status,
                started_at, input_payload
            ) VALUES (?, ?, ?, ?, 'RUNNING', ?, ?)
        """, (
            exec_id, agent_id, workflow_id, task_name,
            now, json.dumps(input_payload or {})
        ))
        # Update agent status to RUNNING
        cursor.execute("""
            UPDATE agents
            SET status = 'RUNNING', total_runs = total_runs + 1, updated_at = ?
            WHERE agent_id = ?
        """, (now, agent_id))
        conn.commit()

    add_execution_log(exec_id, "INFO", f"Task '{task_name}' initialized by agent {agent_id}.")
    return exec_id


def finish_execution(
    execution_id: str,
    status: str,
    output_result: dict = None,
    error_message: str = None,
    duration_ms: int = 0,
    tokens_prompt: int = 0,
    tokens_completion: int = 0,
    cost_mode: str = "ESTIMATED_TELEMETRY"
):
    """
    Marks an execution as SUCCESS, FAILED, or WAITING_APPROVAL, updates token telemetry and cost.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tokens_total = tokens_prompt + tokens_completion
    # Standard estimation: $0.0015 per 1K prompt tokens, $0.002 per 1K completion tokens
    estimated_cost_usd = round((tokens_prompt * 0.0000015) + (tokens_completion * 0.000002), 6)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE agent_executions
            SET status = ?, completed_at = ?, duration_ms = ?,
                tokens_prompt = ?, tokens_completion = ?, tokens_total = ?,
                estimated_cost_usd = ?, cost_mode = ?,
                output_result = ?, error_message = ?
            WHERE execution_id = ?
        """, (
            status, now, duration_ms,
            tokens_prompt, tokens_completion, tokens_total,
            estimated_cost_usd, cost_mode,
            json.dumps(output_result or {}), error_message,
            execution_id
        ))

        # Retrieve agent_id
        cursor.execute("SELECT agent_id FROM agent_executions WHERE execution_id = ?", (execution_id,))
        row = cursor.fetchone()
        if row:
            ag_id = row["agent_id"]
            new_agent_status = "IDLE" if status != "FAILED" else "ERROR"
            succ_inc = 1 if status == "SUCCESS" else 0
            fail_inc = 1 if status == "FAILED" else 0

            cursor.execute("""
                UPDATE agents
                SET status = ?, successful_runs = successful_runs + ?,
                    failed_runs = failed_runs + ?, updated_at = ?
                WHERE agent_id = ?
            """, (new_agent_status, succ_inc, fail_inc, now, ag_id))

        conn.commit()

    log_level = "INFO" if status == "SUCCESS" else "ERROR" if status == "FAILED" else "WARNING"
    msg = f"Task execution completed with status: {status} in {duration_ms}ms."
    if error_message:
        msg += f" Error: {error_message}"
    add_execution_log(execution_id, log_level, msg)


def add_execution_log(execution_id: str, level: str, message: str, details: str = None):
    """
    Appends an audit log message for an agent execution.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO execution_logs (execution_id, timestamp, level, message, details)
            VALUES (?, ?, ?, ?, ?)
        """, (execution_id, now, level.upper(), message, details))
        conn.commit()


def get_executions(agent_id: str = None, status: str = None, limit: int = 50):
    """
    Returns recent agent executions with optional filters.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        conditions = []
        params = []
        if agent_id:
            conditions.append("e.agent_id = ?")
            params.append(agent_id)
        if status and status.upper() != "ALL":
            conditions.append("e.status = ?")
            params.append(status.upper())

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"""
            SELECT e.*, a.name AS agent_name, a.role AS agent_role
            FROM agent_executions e
            LEFT JOIN agents a ON e.agent_id = a.agent_id
            {where}
            ORDER BY e.id DESC
            LIMIT ?
        """
        cursor.execute(query, params + [limit])
        return [dict(row) for row in cursor.fetchall()]


def get_execution_detail(execution_id: str):
    """
    Returns full details of an execution including its step logs.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.*, a.name AS agent_name, a.role AS agent_role
            FROM agent_executions e
            LEFT JOIN agents a ON e.agent_id = a.agent_id
            WHERE e.execution_id = ?
        """, (execution_id,))
        row = cursor.fetchone()
        if not row:
            return None

        result = dict(row)
        try:
            result["input_payload"] = json.loads(result["input_payload"] or "{}")
        except Exception:
            pass
        try:
            result["output_result"] = json.loads(result["output_result"] or "{}")
        except Exception:
            pass

        # Fetch logs
        cursor.execute("""
            SELECT id, timestamp, level, message, details
            FROM execution_logs
            WHERE execution_id = ?
            ORDER BY id ASC
        """, (execution_id,))
        result["logs"] = [dict(log) for log in cursor.fetchall()]
        return result


def create_approval(execution_id: str, agent_id: str, action_type: str, resource_target: str, reason: str, severity: str = "HIGH") -> str:
    """
    Submits a pending Human-In-The-Loop approval request.
    """
    import uuid
    appr_id = f"appr-{uuid.uuid4().hex[:8]}"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO approvals (
                approval_id, execution_id, agent_id, action_type,
                resource_target, reason, severity, status, requested_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDING', ?)
        """, (appr_id, execution_id, agent_id, action_type, resource_target, reason, severity, now))
        conn.commit()

    add_execution_log(
        execution_id,
        "WARNING",
        f"Human approval required for action '{action_type}' on '{resource_target}'. Approval ID: {appr_id}"
    )
    return appr_id


def get_approvals(status: str = "ALL", limit: int = 50):
    """
    Retrieves human-in-the-loop approvals.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        conditions = []
        params = []
        if status and status.upper() != "ALL":
            conditions.append("p.status = ?")
            params.append(status.upper())

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"""
            SELECT p.*, a.name AS agent_name, e.task_name
            FROM approvals p
            LEFT JOIN agents a ON p.agent_id = a.agent_id
            LEFT JOIN agent_executions e ON p.execution_id = e.execution_id
            {where}
            ORDER BY p.id DESC
            LIMIT ?
        """
        cursor.execute(query, params + [limit])
        return [dict(row) for row in cursor.fetchall()]


def record_approval_decision(approval_id: str, decision: str, notes: str = "") -> dict:
    """
    Records an analyst's decision (APPROVED or REJECTED) on a pending action.
    """
    decision_clean = decision.upper()
    if decision_clean not in ["APPROVED", "REJECTED"]:
        raise ValueError("Decision must be either 'APPROVED' or 'REJECTED'")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM approvals WHERE approval_id = ?", (approval_id,))
        appr = cursor.fetchone()
        if not appr:
            return None

        cursor.execute("""
            UPDATE approvals
            SET status = ?, decided_at = ?, decision_notes = ?
            WHERE approval_id = ?
        """, (decision_clean, now, notes, approval_id))

        exec_id = appr["execution_id"]
        # Update execution status
        exec_status = "SUCCESS" if decision_clean == "APPROVED" else "FAILED"
        cursor.execute("""
            UPDATE agent_executions
            SET status = ?, output_result = ?
            WHERE execution_id = ?
        """, (
            exec_status,
            json.dumps({"approval_decision": decision_clean, "notes": notes, "action": appr["action_type"]}),
            exec_id
        ))

        conn.commit()

    log_level = "INFO" if decision_clean == "APPROVED" else "WARNING"
    add_execution_log(
        appr["execution_id"],
        log_level,
        f"Human-In-The-Loop decision '{decision_clean}' recorded for {appr['action_type']}. Notes: {notes or 'No notes provided'}"
    )

    return {
        "approval_id": approval_id,
        "status": decision_clean,
        "execution_id": appr["execution_id"],
        "decided_at": now
    }


def get_agent_metrics():
    """
    Aggregates agent execution metrics, costs, durations, and active statuses.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Total executions
        cursor.execute("SELECT COUNT(*) AS total FROM agent_executions")
        total_execs = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS succ FROM agent_executions WHERE status = 'SUCCESS'")
        succ_execs = cursor.fetchone()["succ"]

        cursor.execute("SELECT COUNT(*) AS fail FROM agent_executions WHERE status = 'FAILED'")
        fail_execs = cursor.fetchone()["fail"]

        cursor.execute("SELECT COUNT(*) AS wait FROM agent_executions WHERE status = 'WAITING_APPROVAL'")
        wait_execs = cursor.fetchone()["wait"]

        # Active agents
        cursor.execute("SELECT COUNT(*) AS active FROM agents WHERE status = 'RUNNING'")
        active_agents = cursor.fetchone()["active"]

        # Pending approvals
        cursor.execute("SELECT COUNT(*) AS pending_approvals FROM approvals WHERE status = 'PENDING'")
        pending_approvals = cursor.fetchone()["pending_approvals"]

        # Telemetry: total tokens & cost
        cursor.execute("""
            SELECT SUM(tokens_prompt) AS prompt,
                   SUM(tokens_completion) AS completion,
                   SUM(tokens_total) AS total_tokens,
                   SUM(estimated_cost_usd) AS total_cost,
                   AVG(duration_ms) AS avg_duration
            FROM agent_executions
        """)
        telemetry = cursor.fetchone()

        total_tokens = telemetry["total_tokens"] or 0
        total_cost = round(telemetry["total_cost"] or 0.0, 5)
        avg_duration = round(telemetry["avg_duration"] or 0.0, 1)

    return {
        "total_executions": total_execs,
        "successful_executions": succ_execs,
        "failed_executions": fail_execs,
        "waiting_approval": wait_execs,
        "active_agents": active_agents,
        "pending_approvals": pending_approvals,
        "total_tokens": total_tokens,
        "total_cost_usd": total_cost,
        "cost_mode": "ESTIMATED_TELEMETRY",
        "avg_duration_ms": avg_duration
    }


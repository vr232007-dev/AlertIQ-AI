"""
AlertIQ AI - Direct Acceptance Test Suite
Tests FastAPI endpoint functions, ML model inference, SQLite database storage,
alert generation & resolution lifecycle, and analytics calculations.
Does not require TCP sockets or external network access.
"""

import sys
import io
import json
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
from fastapi import UploadFile
from backend.main import (
    get_system_status,
    get_model_information,
    get_dashboard_metrics,
    upload_traffic_csv,
    predict_single_flow,
    SingleFlowRequest,
    list_alerts,
    acknowledge_security_alert,
    resolve_security_alert,
    list_prediction_history,
    get_prediction_by_id,
    get_analytics,
    reset_database,
    seed_sample_traffic
)
from backend.database import init_db, clear_all_data

import asyncio

def run_tests():
    print("=" * 65)
    print("ALERTIQ AI: RUNNING CORE VERIFICATION & ACCEPTANCE TESTS")
    print("=" * 65)

    # 1. Initialize Database
    init_db()
    clear_all_data()
    print("[PASS] 1. SQLite Database Initialized and Cleared")

    # 2. System Status Verification
    status = get_system_status()
    assert status["status"] == "online"
    assert status["model_status"] == "ready"
    assert status["feature_count"] == 78
    print(f"[PASS] 2. System Status Verified: Status={status['status']}, Features={status['feature_count']}")

    # 3. Model Information Verification
    model_info = get_model_information()
    assert model_info["feature_count"] == 78
    assert len(model_info["features"]) == 78
    assert "BENIGN" in model_info["classes"] and "ATTACK" in model_info["classes"]
    print(f"[PASS] 3. Model Info Verified: {model_info['model_type']} with {len(model_info['features'])} features")

    # 4. Empty State Dashboard Verification
    stats = get_dashboard_metrics()
    assert stats["total_traffic"] == 0
    assert stats["benign_count"] == 0
    assert stats["attack_count"] == 0
    assert stats["active_alerts"] == 0
    print("[PASS] 4. Dashboard Stats Correct for Empty Database State")

    # 5. Invalid CSV Upload Verification (Missing required features)
    invalid_csv_bytes = b"feature1,feature2\n1.0,2.0\n"
    invalid_upload = UploadFile(
        file=io.BytesIO(invalid_csv_bytes),
        filename="corrupted_traffic.csv"
    )
    try:
        upload_traffic_csv(invalid_upload)
        assert False, "Should have thrown HTTPException for missing features"
    except Exception as e:
        assert hasattr(e, "status_code") and e.status_code == 400
        assert "Missing" in str(e.detail)
        print(f"[PASS] 5. Invalid CSV Handled Gracefully: {e.detail[:55]}...")

    # 6. Valid CSV Upload & Batch ML Inference Verification
    sample_file = ROOT_DIR / "data" / "samples" / "sample_traffic.csv"
    assert sample_file.exists(), "sample_traffic.csv must exist"

    with open(sample_file, "rb") as f:
        content = f.read()

    upload_file = UploadFile(
        file=io.BytesIO(content),
        filename="sample_traffic.csv"
    )

    upload_result = upload_traffic_csv(upload_file)
    summary = upload_result["summary"]
    print(f"[PASS] 6. Valid CSV Processed: Total={summary['total_analyzed']}, Benign={summary['benign_count']}, Attacks={summary['attack_count']}, Alerts={summary['alerts_created']}")
    assert summary["total_analyzed"] == 20
    assert summary["benign_count"] > 0
    assert summary["attack_count"] > 0
    assert summary["alerts_created"] == summary["attack_count"]

    # 7. Dashboard Stats with Stored Records
    stats_updated = get_dashboard_metrics()
    assert stats_updated["total_traffic"] == 20
    assert stats_updated["attack_count"] == summary["attack_count"]
    assert stats_updated["benign_count"] == summary["benign_count"]
    assert len(stats_updated["recent_predictions"]) > 0
    print(f"[PASS] 7. Dashboard Stats Updated from DB: Total={stats_updated['total_traffic']}, Attack%={stats_updated['attack_percentage']}%")

    # 8. Security Alerts Generation & Filtering
    active_alerts = list_alerts(status="ACTIVE")
    assert active_alerts["total"] == summary["alerts_created"]
    first_alert = active_alerts["alerts"][0]
    alert_id = first_alert["id"]
    print(f"[PASS] 8. Security Alerts Generated: Total Active={active_alerts['total']}, Sample Alert: '{first_alert['title']}' ({first_alert['severity']})")

    # 9. Alert Acknowledgment
    ack_res = acknowledge_security_alert(alert_id)
    assert ack_res["status"] == "ACKNOWLEDGED"

    active_after_ack = list_alerts(status="ACTIVE")
    ack_alerts = list_alerts(status="ACKNOWLEDGED")
    assert any(a["id"] == alert_id for a in ack_alerts["alerts"])
    print(f"[PASS] 9. Alert Acknowledgment: Alert {alert_id} moved from ACTIVE to ACKNOWLEDGED")

    # 10. Alert Resolution
    res_res = resolve_security_alert(alert_id)
    assert res_res["status"] == "RESOLVED"

    resolved_alerts = list_alerts(status="RESOLVED")
    assert any(a["id"] == alert_id for a in resolved_alerts["alerts"])
    print(f"[PASS] 10. Alert Resolution: Alert {alert_id} moved to RESOLVED")

    # 11. Prediction History & Filtering
    history_attack = list_prediction_history(filter_class="ATTACK")
    assert all(r["predicted_class"] == "ATTACK" for r in history_attack["records"])

    history_benign = list_prediction_history(filter_class="BENIGN")
    assert all(r["predicted_class"] == "BENIGN" for r in history_benign["records"])
    print(f"[PASS] 11. Prediction History Filter Verified: {history_benign['total']} Benign, {history_attack['total']} Attack")

    # 12. Full Record Detail Retrieval (78 features)
    first_pred_id = history_attack["records"][0]["id"]
    detail = get_prediction_by_id(first_pred_id)
    assert len(detail["features"]) == 78
    print(f"[PASS] 12. Prediction Detail Verified: Record #{first_pred_id} includes all 78 feature values")

    # 13. Analytics Aggregations
    analytics = get_analytics()
    assert analytics["total_predictions"] == 20
    assert "CRITICAL" in analytics["severity_breakdown"]
    assert len(analytics["top_ports"]) > 0
    print(f"[PASS] 13. Analytics Aggregation Verified: Top Port={analytics['top_ports'][0]['port']} ({analytics['top_ports'][0]['attacks']} attacks)")

    # 14. Single Flow Prediction Endpoint
    sample_df = pd.read_csv(sample_file, nrows=1)
    single_req = SingleFlowRequest(
        features=sample_df.iloc[0].to_dict(),
        source_label="single_flow_unit_test"
    )
    single_res = predict_single_flow(single_req)
    assert single_res["predicted_class"] in ["BENIGN", "ATTACK"]
    print(f"[PASS] 14. Single Flow Prediction: Class={single_res['predicted_class']}, Prob={single_res['attack_probability']}")

    print("=" * 65)
    print("ALL 14 ACCEPTANCE VERIFICATIONS PASSED WITH 100% SUCCESS!")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()

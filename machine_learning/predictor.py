"""
Inference Engine and Alert Prioritizer for AlertIQ AI.

Loads the serialized Joblib pipeline and exposes production-ready methods
for real-time single-alert triage and high-throughput batch scoring.
Validates payloads against the AlertIQ AI shared schema before scoring.
"""

from pathlib import Path
from typing import Dict, Any, List, Union, Optional
import joblib
import pandas as pd
import numpy as np

from machine_learning.config import (
    DEFAULT_MODEL_PATH,
    PRIORITY_CLASSES
)
from machine_learning.schema import (
    SecurityAlert,
    AlertPrioritizationResult,
    validate_alert_dict,
    validate_alert_dataframe,
    FEATURE_COLUMNS
)


class AlertPrioritizer:
    """
    Production inference engine for scoring and prioritizing incoming SOC alerts.
    """

    def __init__(self, model_path: Union[str, Path] = DEFAULT_MODEL_PATH):
        """
        Loads the trained Scikit-learn pipeline from a Joblib file.

        Parameters:
            model_path (Union[str, Path]): Filesystem path to the .joblib file.

        Raises:
            FileNotFoundError: If the model file is missing at the given path.
        """
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model artifact not found at {self.model_path}. "
                "Ensure `python -m machine_learning.train` has been executed first."
            )
        self.pipeline = joblib.load(self.model_path)
        # Verify pipeline classes
        clf = self.pipeline.named_steps["classifier"]
        self.classes: List[str] = list(clf.classes_)

    def _generate_recommendation(self, priority: str, confidence: float, alert: Dict[str, Any]) -> str:
        """
        Generates contextual SOC action recommendations based on predicted priority and telemetry.

        Parameters:
            priority (str): Predicted priority label.
            confidence (float): Model prediction confidence.
            alert (Dict[str, Any]): Original alert telemetry dictionary.

        Returns:
            str: Actionable SOC Tier 1/2 playbook instruction.
        """
        asset = alert.get("destination_ip", "target host")
        zone = alert.get("network_zone", "internal")

        if priority == "Critical":
            return (
                f"[SEV-1 ESCALATION] Immediately isolate {asset} in {zone} zone. "
                f"Page on-call Incident Response commander. Model confidence: {confidence:.1%}."
            )
        elif priority == "High":
            return (
                f"[SEV-2 ACTION] Assign to Tier 2 SOC Analyst for immediate triage (<15 min SLA). "
                f"Check EDR telemetry and firewall blocks for {asset}."
            )
        elif priority == "Medium":
            return (
                f"[SEV-3 QUEUE] Enqueue for routine SOC analyst investigation within standard 4-hour window. "
                f"Correlate with adjacent endpoint activity."
            )
        else:  # Low
            return (
                "[SEV-4 INFORMATIONAL] Auto-log to SIEM repository. Suppress pager alert. "
                "No immediate human intervention required unless correlated with higher severity events."
            )

    def predict_single(
        self,
        alert_input: Union[Dict[str, Any], SecurityAlert]
    ) -> AlertPrioritizationResult:
        """
        Scores a single security alert in real time.

        Parameters:
            alert_input (Union[Dict[str, Any], SecurityAlert]): Raw alert dictionary or Pydantic model.

        Returns:
            AlertPrioritizationResult: Pydantic result containing predicted priority,
            confidence score, full class probability distribution, and playbook recommendation.
        """
        # Validate against shared schema
        if isinstance(alert_input, SecurityAlert):
            alert_dict = alert_input.model_dump()
        else:
            validated_alert = validate_alert_dict(alert_input)
            alert_dict = validated_alert.model_dump()

        alert_id = alert_dict.get("alert_id", "UNKNOWN")

        # Convert to single-row DataFrame
        df_row = pd.DataFrame([alert_dict])[FEATURE_COLUMNS]

        # Execute prediction through full Pipeline
        pred_label = self.pipeline.predict(df_row)[0]
        pred_probs = self.pipeline.predict_proba(df_row)[0]

        prob_dict = {
            cls_name: round(float(prob), 4)
            for cls_name, prob in zip(self.classes, pred_probs)
        }
        confidence = float(np.max(pred_probs))

        recommendation = self._generate_recommendation(
            priority=pred_label,
            confidence=confidence,
            alert=alert_dict
        )

        return AlertPrioritizationResult(
            alert_id=alert_id,
            predicted_priority=pred_label,
            confidence=round(confidence, 4),
            probabilities=prob_dict,
            triage_recommendation=recommendation
        )

    def predict_batch(
        self,
        alerts: Union[List[Dict[str, Any]], pd.DataFrame]
    ) -> pd.DataFrame:
        """
        Executes bulk prioritization on a collection of alerts (e.g. streaming micro-batches).

        Parameters:
            alerts (Union[List[Dict[str, Any]], pd.DataFrame]): List of alert dictionaries or DataFrame.

        Returns:
            pd.DataFrame: Augmented DataFrame containing 'predicted_priority', 'confidence',
            and individual class probabilities.
        """
        if isinstance(alerts, list):
            df = pd.DataFrame(alerts)
        else:
            df = alerts.copy()

        # Validate presence of required features
        df_features = validate_alert_dataframe(df, require_target=False)[FEATURE_COLUMNS]

        preds = self.pipeline.predict(df_features)
        probs = self.pipeline.predict_proba(df_features)

        result_df = df.copy()
        result_df["predicted_priority"] = preds
        result_df["confidence"] = np.max(probs, axis=1).round(4)

        for i, cls_name in enumerate(self.classes):
            result_df[f"prob_{cls_name.lower()}"] = probs[:, i].round(4)

        return result_df


if __name__ == "__main__":
    # Multi-scenario demonstration across all priority tiers
    sample_alerts = [
        {
            "alert_id": "ALT-DEMO-LOW",
            "timestamp": "2026-11-02T10:00:00",
            "alert_type": "Port_Scanning",
            "source_ip": "45.33.32.1",
            "destination_ip": "192.168.1.5",
            "source_port": 55000,
            "destination_port": 80,
            "protocol": "TCP",
            "network_zone": "External",
            "asset_criticality": "Low",
            "user_role": "Standard_User",
            "raw_severity": "Informational",
            "event_count": 15,
            "bytes_transferred": 120.0,
            "failed_login_attempts": 0,
            "mitre_tactic": "Discovery",
            "is_known_malicious_ip": 0,
            "is_off_hours": 0
        },
        {
            "alert_id": "ALT-DEMO-MEDIUM",
            "timestamp": "2026-11-02T10:15:00",
            "alert_type": "SQL_Injection",
            "source_ip": "62.14.22.8",
            "destination_ip": "10.0.1.20",
            "source_port": 44100,
            "destination_port": 443,
            "protocol": "HTTPS",
            "network_zone": "DMZ",
            "asset_criticality": "Medium",
            "user_role": "Standard_User",
            "raw_severity": "Medium",
            "event_count": 85,
            "bytes_transferred": 55000.0,
            "failed_login_attempts": 2,
            "mitre_tactic": "Initial_Access",
            "is_known_malicious_ip": 0,
            "is_off_hours": 1
        },
        {
            "alert_id": "ALT-DEMO-HIGH",
            "timestamp": "2026-11-02T10:30:00",
            "alert_type": "Brute_Force",
            "source_ip": "185.220.101.5",
            "destination_ip": "10.0.2.10",
            "source_port": 39120,
            "destination_port": 22,
            "protocol": "TCP",
            "network_zone": "Internal",
            "asset_criticality": "High",
            "user_role": "Service_Account",
            "raw_severity": "High",
            "event_count": 450,
            "bytes_transferred": 80000.0,
            "failed_login_attempts": 75,
            "mitre_tactic": "Credential_Access",
            "is_known_malicious_ip": 1,
            "is_off_hours": 1
        },
        {
            "alert_id": "ALT-DEMO-CRITICAL",
            "timestamp": "2026-11-02T10:45:00",
            "alert_type": "Data_Exfiltration",
            "source_ip": "10.0.4.15",
            "destination_ip": "103.25.10.4",
            "source_port": 49152,
            "destination_port": 443,
            "protocol": "HTTPS",
            "network_zone": "PCI_DSS",
            "asset_criticality": "Critical",
            "user_role": "Domain_Admin",
            "raw_severity": "High",
            "event_count": 350,
            "bytes_transferred": 85000000.0,
            "failed_login_attempts": 25,
            "mitre_tactic": "Exfiltration",
            "is_known_malicious_ip": 1,
            "is_off_hours": 1
        }
    ]

    try:
        prioritizer = AlertPrioritizer()
        print("=" * 80)
        print("          ALERT-IQ AI: REAL-TIME INFERENCE DEMONSTRATION")
        print("=" * 80)
        for alert in sample_alerts:
            res = prioritizer.predict_single(alert)
            print(f"\n[Alert ID]: {res.alert_id:<18} [Predicted Priority]: {res.predicted_priority:<10} [Confidence]: {res.confidence:.2%}")
            print(f"Probabilities:  {res.probabilities}")
            print(f"Playbook:       {res.triage_recommendation}")
        print("\n" + "=" * 80)
    except FileNotFoundError as e:
        print(f"Notice: {e}")

"""
Realistic Labelled Security Alert Dataset Generator for AlertIQ AI.

Generates synthetic, domain-accurate SOC security alerts strictly conforming to the
shared alert schema. Implements real-world SOC security heuristics and correlation
logic (asset criticality, MITRE tactics, threat intel flags, network segmentation,
user privilege level) to establish realistic ground-truth priority labels.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
import pandas as pd

from machine_learning.config import (
    DEFAULT_DATASET_PATH,
    RANDOM_STATE
)
from machine_learning.schema import (
    ALLOWED_ALERT_TYPES,
    ALLOWED_PROTOCOLS,
    ALLOWED_NETWORK_ZONES,
    ALLOWED_ASSET_CRITICALITIES,
    ALLOWED_USER_ROLES,
    ALLOWED_RAW_SEVERITIES,
    ALLOWED_MITRE_TACTICS,
    ALL_COLUMNS
)


def _generate_ip(is_internal: bool = False, rng: Optional[random.Random] = None) -> str:
    """
    Generates a realistic IPv4 address.

    Parameters:
        is_internal (bool): If True, generates an RFC 1918 private address.
                            If False, generates a routable public IP.
        rng (random.Random): Optional seeded random number generator.

    Returns:
        str: Formatted IPv4 address.
    """
    r = rng if rng is not None else random
    if is_internal:
        prefix = r.choice(["10.0", "172.16", "192.168"])
        return f"{prefix}.{r.randint(1, 254)}.{r.randint(1, 254)}"
    else:
        first_octet = r.choice([45, 62, 89, 103, 151, 185, 198, 203])
        return f"{first_octet}.{r.randint(1, 254)}.{r.randint(1, 254)}.{r.randint(1, 254)}"


def _calculate_ground_truth_priority(
    alert_type: str,
    network_zone: str,
    asset_criticality: str,
    user_role: str,
    raw_severity: str,
    event_count: int,
    bytes_transferred: float,
    failed_login_attempts: int,
    mitre_tactic: str,
    is_known_malicious_ip: int,
    is_off_hours: int,
    rng: random.Random
) -> str:
    """
    Computes a realistic SOC ground-truth priority score based on multi-factor
    security telemetry and contextual threat risk.

    Parameters:
        alert_type (str): Type of security attack/alert.
        network_zone (str): Network zone of the target host.
        asset_criticality (str): Importance of the affected asset.
        user_role (str): Identity context of the affected entity.
        raw_severity (str): Raw sensor alert severity.
        event_count (int): Volume of aggregated alert occurrences.
        bytes_transferred (float): Volume of data transferred.
        failed_login_attempts (int): Authentication failure count.
        mitre_tactic (str): Associated MITRE ATT&CK tactic.
        is_known_malicious_ip (int): Threat intel reputation flag (0 or 1).
        is_off_hours (int): Off-business hours activity flag (0 or 1).
        rng (random.Random): Seeded random number generator for realistic noise.

    Returns:
        str: Ground-truth priority ('Low', 'Medium', 'High', or 'Critical').
    """
    risk_score = 0.0

    # 1. Asset Criticality weighting (Core SOC Tier 1 triage factor)
    crit_weights = {"Low": 2.0, "Medium": 10.0, "High": 22.0, "Critical": 35.0}
    risk_score += crit_weights.get(asset_criticality, 5.0)

    # 2. Network Zone exposure & data sensitivity
    zone_weights = {
        "PCI_DSS": 28.0,
        "Cloud_VPC": 18.0,
        "Internal": 12.0,
        "DMZ": 6.0,
        "External": 3.0
    }
    risk_score += zone_weights.get(network_zone, 5.0)

    # 3. User Role / Identity privilege level
    role_weights = {
        "Domain_Admin": 28.0,
        "System": 22.0,
        "Service_Account": 12.0,
        "Contractor": 6.0,
        "Standard_User": 2.0
    }
    risk_score += role_weights.get(user_role, 2.0)

    # 4. Attack Type severity
    if alert_type in ["Data_Exfiltration", "Privilege_Escalation", "Malware_Detection"]:
        risk_score += 22.0
    elif alert_type in ["Brute_Force", "SQL_Injection", "Anomalous_Login"]:
        risk_score += 12.0
    elif alert_type in ["DDoS_Attempt", "Unauthorized_Access"]:
        risk_score += 8.0
    else:  # Port_Scanning, Phishing_Campaign
        risk_score += 3.0

    # 5. MITRE ATT&CK Tactic
    if mitre_tactic in ["Exfiltration", "Privilege_Escalation", "Lateral_Movement", "Impact"]:
        risk_score += 18.0
    elif mitre_tactic in ["Credential_Access", "Execution", "Persistence"]:
        risk_score += 10.0
    else:  # Initial_Access, Discovery, Defense_Evasion
        risk_score += 4.0

    # 6. Threat Intel Indicator
    if is_known_malicious_ip == 1:
        risk_score += 20.0

    # 7. Telemetry anomalies
    if bytes_transferred > 10_000_000:
        risk_score += 18.0
    elif bytes_transferred > 1_000_000:
        risk_score += 9.0

    if failed_login_attempts > 20:
        risk_score += 18.0
    elif failed_login_attempts > 5:
        risk_score += 8.0

    if event_count > 500:
        risk_score += 12.0
    elif event_count > 100:
        risk_score += 6.0

    # 8. Off-hours behavior
    if is_off_hours == 1:
        risk_score += 6.0

    # 9. Raw severity baseline correlation
    raw_weights = {"Informational": 0.0, "Low": 4.0, "Medium": 10.0, "High": 18.0}
    risk_score += raw_weights.get(raw_severity, 4.0)

    # 10. Realistic Real-world Noise: mimic human triage variance
    noise = rng.uniform(-6.0, 6.0)
    risk_score += noise

    # Calibrated thresholds conforming to SOC pyramid
    if risk_score >= 95.0:
        return "Critical"
    elif risk_score >= 70.0:
        return "High"
    elif risk_score >= 45.0:
        return "Medium"
    else:
        return "Low"


def generate_security_alert_dataset(
    n_samples: int = 5000,
    random_state: int = RANDOM_STATE,
    save_path: Optional[Path] = DEFAULT_DATASET_PATH
) -> pd.DataFrame:
    """
    Generates a comprehensive dataset of labelled security alerts conforming
    strictly to the AlertIQ AI shared schema.

    Parameters:
        n_samples (int): Total number of security alerts to generate (default: 5000).
        random_state (int): Seed for reproducibility.
        save_path (Optional[Path]): Destination CSV path. If None, does not write to disk.

    Returns:
        pd.DataFrame: Labelled alerts DataFrame with all schema fields and target priority.
    """
    rng = random.Random(random_state)
    np_rng = np.random.default_rng(random_state)

    # Realistic SOC frequency distributions (Alert Pyramid)
    role_choices = ["Standard_User", "Contractor", "Service_Account", "Domain_Admin", "System"]
    role_weights = [0.60, 0.15, 0.12, 0.08, 0.05]

    zone_choices = ["External", "DMZ", "Internal", "Cloud_VPC", "PCI_DSS"]
    zone_weights = [0.35, 0.25, 0.25, 0.10, 0.05]

    crit_choices = ["Low", "Medium", "High", "Critical"]
    crit_weights = [0.40, 0.35, 0.18, 0.07]

    raw_sev_choices = ["Low", "Informational", "Medium", "High"]
    raw_sev_weights = [0.35, 0.25, 0.25, 0.15]

    alert_type_choices = [
        "Port_Scanning", "Brute_Force", "Anomalous_Login", "Phishing_Campaign",
        "DDoS_Attempt", "SQL_Injection", "Unauthorized_Access",
        "Malware_Detection", "Privilege_Escalation", "Data_Exfiltration"
    ]
    alert_type_weights = [0.22, 0.18, 0.14, 0.12, 0.10, 0.08, 0.06, 0.05, 0.03, 0.02]

    records: List[Dict[str, Any]] = []
    base_time = datetime(2026, 10, 1, 0, 0, 0)
    common_dest_ports = [22, 53, 80, 443, 445, 1433, 3306, 3389, 8080, 8443]

    for idx in range(1, n_samples + 1):
        alert_id = f"ALT-2026-{idx:06d}"
        timestamp = base_time + timedelta(
            minutes=rng.randint(0, 43200),
            seconds=rng.randint(0, 59)
        )

        alert_type = rng.choices(alert_type_choices, weights=alert_type_weights, k=1)[0]
        network_zone = rng.choices(zone_choices, weights=zone_weights, k=1)[0]
        asset_criticality = rng.choices(crit_choices, weights=crit_weights, k=1)[0]
        user_role = rng.choices(role_choices, weights=role_weights, k=1)[0]
        raw_severity = rng.choices(raw_sev_choices, weights=raw_sev_weights, k=1)[0]
        mitre_tactic = rng.choice(ALLOWED_MITRE_TACTICS)
        protocol = rng.choice(ALLOWED_PROTOCOLS)

        if network_zone == "External":
            source_ip = _generate_ip(is_internal=False, rng=rng)
            dest_ip = _generate_ip(is_internal=False, rng=rng)
        else:
            source_ip = _generate_ip(is_internal=rng.random() > 0.4, rng=rng)
            dest_ip = _generate_ip(is_internal=True, rng=rng)

        source_port = rng.randint(1024, 65535)
        dest_port = rng.choice(common_dest_ports) if rng.random() > 0.3 else rng.randint(1, 65535)

        # Context-aware quantitative metrics
        if alert_type == "Brute_Force":
            failed_login_attempts = int(np_rng.integers(5, 150))
            event_count = int(failed_login_attempts + np_rng.integers(2, 40))
            bytes_transferred = float(np_rng.uniform(500, 30000))
        elif alert_type == "Data_Exfiltration":
            failed_login_attempts = int(np_rng.integers(0, 3))
            event_count = int(np_rng.integers(10, 300))
            bytes_transferred = float(np_rng.uniform(2_000_000, 120_000_000))
        elif alert_type == "DDoS_Attempt":
            failed_login_attempts = 0
            event_count = int(np_rng.integers(400, 8000))
            bytes_transferred = float(np_rng.uniform(300_000, 40_000_000))
        elif alert_type == "Port_Scanning":
            failed_login_attempts = 0
            event_count = int(np_rng.integers(15, 600))
            bytes_transferred = float(np_rng.uniform(64, 5000))
        else:
            failed_login_attempts = int(np_rng.integers(0, 8))
            event_count = int(np_rng.integers(1, 150))
            bytes_transferred = float(np_rng.uniform(200, 1_500_000))

        # Known malicious IP correlation
        intel_prob = 0.35 if alert_type in ["Data_Exfiltration", "Malware_Detection", "Privilege_Escalation"] else 0.10
        is_known_malicious_ip = 1 if rng.random() < intel_prob else 0

        # Off hours indicator (business hours: 08:00 - 18:00)
        is_off_hours = 1 if (timestamp.hour < 8 or timestamp.hour >= 18) else 0

        priority = _calculate_ground_truth_priority(
            alert_type=alert_type,
            network_zone=network_zone,
            asset_criticality=asset_criticality,
            user_role=user_role,
            raw_severity=raw_severity,
            event_count=event_count,
            bytes_transferred=bytes_transferred,
            failed_login_attempts=failed_login_attempts,
            mitre_tactic=mitre_tactic,
            is_known_malicious_ip=is_known_malicious_ip,
            is_off_hours=is_off_hours,
            rng=rng
        )

        record = {
            "alert_id": alert_id,
            "timestamp": timestamp.isoformat(),
            "alert_type": alert_type,
            "source_ip": source_ip,
            "destination_ip": dest_ip,
            "source_port": source_port,
            "destination_port": dest_port,
            "protocol": protocol,
            "network_zone": network_zone,
            "asset_criticality": asset_criticality,
            "user_role": user_role,
            "raw_severity": raw_severity,
            "event_count": event_count,
            "bytes_transferred": round(bytes_transferred, 2),
            "failed_login_attempts": failed_login_attempts,
            "mitre_tactic": mitre_tactic,
            "is_known_malicious_ip": is_known_malicious_ip,
            "is_off_hours": is_off_hours,
            "priority": priority
        }
        records.append(record)

    df = pd.DataFrame(records)
    df = df[ALL_COLUMNS]

    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(save_path, index=False)
        print(f"[AlertIQ Data Generator] Successfully generated {len(df)} records -> {save_path}")

    return df


if __name__ == "__main__":
    df = generate_security_alert_dataset(n_samples=5000, random_state=RANDOM_STATE)
    print("\nDataset Class Distribution:")
    print(df["priority"].value_counts(normalize=True).map(lambda p: f"{p:.2%}"))
    print("\nSample records:")
    print(df[["alert_id", "alert_type", "network_zone", "asset_criticality", "priority"]].head(5))

"""
AlertIQ AI - Sample Data Generator
Generates sample network traffic CSV files from the CIC-IDS2017 dataset
for testing, demonstration, and user downloads.
"""

import pandas as pd
from pathlib import Path
import sys

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from machine_learning.ai_engine import EXPECTED_FEATURES

SAMPLES_DIR = ROOT_DIR / "data" / "samples"
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

TRAINING_FILE = ROOT_DIR / "data" / "processed" / "alertiq_training.csv"


def generate_sample_files():
    """
    Creates sample CSV files:
    1. sample_traffic.csv: 20 realistic flows (10 benign, 10 attacks) with all 78 features.
    2. sample_template.csv: CSV header template with all 78 feature names.
    """
    if TRAINING_FILE.exists():
        print("Reading records from processed training dataset...")
        df = pd.read_csv(TRAINING_FILE)

        # Get 10 benign records and 10 attack records
        benign_samples = df[df["target"] == 0].head(10).drop(columns=["target"])
        attack_samples = df[df["target"] == 1].head(10).drop(columns=["target"])

        # Interleave benign and attack samples
        mixed_samples = pd.concat([benign_samples, attack_samples], ignore_index=True)
        # Ensure exact 78 features in order
        mixed_samples = mixed_samples.reindex(columns=EXPECTED_FEATURES)

        sample_traffic_file = SAMPLES_DIR / "sample_traffic.csv"
        mixed_samples.to_csv(sample_traffic_file, index=False)
        print(f"Created: {sample_traffic_file} ({len(mixed_samples)} rows)")

    # Create empty template with headers
    template_df = pd.DataFrame(columns=EXPECTED_FEATURES)
    template_file = SAMPLES_DIR / "sample_template.csv"
    template_df.to_csv(template_file, index=False)
    print(f"Created: {template_file}")


if __name__ == "__main__":
    generate_sample_files()

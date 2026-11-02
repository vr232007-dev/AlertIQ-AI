"""
Comprehensive Test Suite for AlertIQ AI Machine Learning Module.

Validates:
- Schema enforcement and validation guards
- Dataset generator conformance
- Preprocessing transformer shapes and missing value handling
- Random Forest model fitting, evaluation metrics generation
- Joblib serialization and deserialization
- Single-alert and batch inference contracts
- Non-fabricated metric mathematical consistency
"""

import unittest
from pathlib import Path
import tempfile
import numpy as np
import pandas as pd
from pydantic import ValidationError

from machine_learning.config import (
    PRIORITY_CLASSES,
    DEFAULT_RF_PARAMS
)
from machine_learning.schema import (
    SecurityAlert,
    validate_alert_dict,
    validate_alert_dataframe,
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    ALLOWED_ALERT_TYPES
)
from machine_learning.data_generator import generate_security_alert_dataset
from machine_learning.preprocessor import (
    build_preprocessor,
    split_data,
    encode_target_labels,
    decode_target_labels
)
from machine_learning.model import create_full_pipeline, AlertPriorityClassifier
from machine_learning.evaluator import compute_metrics, format_confusion_matrix
from machine_learning.train import train_and_evaluate
from machine_learning.predictor import AlertPrioritizer


class TestAlertIQMachineLearningModule(unittest.TestCase):
    """
    Unit and Integration tests for AlertIQ AI ML components.
    """

    def setUp(self):
        """Prepare sample alert fixture conforming strictly to the shared schema."""
        self.valid_alert_data = {
            "alert_id": "ALT-2026-000100",
            "timestamp": "2026-11-02T10:15:30",
            "alert_type": "Data_Exfiltration",
            "source_ip": "10.0.1.50",
            "destination_ip": "45.33.32.156",
            "source_port": 54321,
            "destination_port": 443,
            "protocol": "HTTPS",
            "network_zone": "PCI_DSS",
            "asset_criticality": "Critical",
            "user_role": "Domain_Admin",
            "raw_severity": "High",
            "event_count": 450,
            "bytes_transferred": 85000000.0,
            "failed_login_attempts": 12,
            "mitre_tactic": "Exfiltration",
            "is_known_malicious_ip": 1,
            "is_off_hours": 1,
            "priority": "Critical"
        }

    # ==========================================================================
    # 1. Schema Tests
    # ==========================================================================
    def test_schema_valid_alert(self):
        """Tests that a valid alert dictionary validates cleanly via Pydantic."""
        alert = validate_alert_dict(self.valid_alert_data)
        self.assertIsInstance(alert, SecurityAlert)
        self.assertEqual(alert.alert_id, "ALT-2026-000100")
        self.assertEqual(alert.priority, "Critical")

    def test_schema_invalid_alert_type(self):
        """Tests that unknown alert types are caught by schema validators."""
        bad_data = self.valid_alert_data.copy()
        bad_data["alert_type"] = "Unknown_Alien_Attack"
        with self.assertRaises(ValidationError):
            validate_alert_dict(bad_data)

    def test_schema_invalid_port(self):
        """Tests that out-of-range port numbers fail schema validation."""
        bad_data = self.valid_alert_data.copy()
        bad_data["destination_port"] = 999999
        with self.assertRaises(ValidationError):
            validate_alert_dict(bad_data)

    def test_schema_dataframe_missing_column(self):
        """Tests that validate_alert_dataframe rejects dataframes with missing features."""
        df = pd.DataFrame([self.valid_alert_data]).drop(columns=["network_zone"])
        with self.assertRaises(ValueError):
            validate_alert_dataframe(df)

    # ==========================================================================
    # 2. Data Generator Tests
    # ==========================================================================
    def test_data_generator_output(self):
        """Tests that synthetic dataset generator produces correct schema and types."""
        df = generate_security_alert_dataset(n_samples=100, random_state=42, save_path=None)
        self.assertEqual(len(df), 100)
        for col in FEATURE_COLUMNS:
            self.assertIn(col, df.columns)
        self.assertIn(TARGET_COLUMN, df.columns)
        # Verify all priorities are valid
        self.assertTrue(set(df[TARGET_COLUMN].unique()).issubset(set(PRIORITY_CLASSES)))

    # ==========================================================================
    # 3. Preprocessing Tests
    # ==========================================================================
    def test_preprocessor_pipeline_transformation(self):
        """Tests that ColumnTransformer transforms raw data into numeric matrices."""
        df = generate_security_alert_dataset(n_samples=50, random_state=42, save_path=None)
        X = df[FEATURE_COLUMNS]
        preproc = build_preprocessor()
        X_trans = preproc.fit_transform(X)
        self.assertEqual(X_trans.shape[0], 50)
        self.assertGreater(X_trans.shape[1], len(FEATURE_COLUMNS))
        self.assertFalse(np.isnan(X_trans).any())

    def test_target_label_encoding_roundtrip(self):
        """Tests encoding and decoding of target priority strings."""
        series = pd.Series(["Low", "Medium", "High", "Critical", "Low"])
        encoded = encode_target_labels(series)
        decoded = decode_target_labels(encoded)
        self.assertEqual(decoded, list(series))

    def test_stratified_split(self):
        """Tests that split_data creates properly stratified subsets."""
        df = generate_security_alert_dataset(n_samples=200, random_state=42, save_path=None)
        X_train, X_test, y_train, y_test = split_data(df, test_size=0.25, random_state=42)
        self.assertEqual(len(X_train), 150)
        self.assertEqual(len(X_test), 50)
        # Verify all classes present in both splits
        self.assertEqual(set(y_train.unique()), set(y_test.unique()))

    # ==========================================================================
    # 4. Evaluator Tests & Authenticity Checks
    # ==========================================================================
    def test_metrics_computation_authenticity(self):
        """Tests that compute_metrics computes genuine mathematical scores without hardcoding."""
        y_true = ["Low", "Low", "Medium", "High", "Critical"]
        y_pred = ["Low", "Medium", "Medium", "High", "Critical"]

        metrics = compute_metrics(y_true, y_pred, labels=PRIORITY_CLASSES)

        # 4 out of 5 correct = 0.8 accuracy
        self.assertAlmostEqual(metrics["accuracy"], 0.8, places=3)
        self.assertGreaterEqual(metrics["macro_precision"], 0.0)
        self.assertLessEqual(metrics["macro_precision"], 1.0)
        self.assertGreaterEqual(metrics["macro_f1"], 0.0)
        self.assertLessEqual(metrics["macro_f1"], 1.0)

        # Check confusion matrix dimensions and values
        cm = np.array(metrics["confusion_matrix"])
        self.assertEqual(cm.shape, (4, 4))
        self.assertEqual(cm.sum(), 5)

        # Formatted matrix test
        df_cm = format_confusion_matrix(cm, labels=PRIORITY_CLASSES)
        self.assertEqual(df_cm.shape, (4, 4))

    # ==========================================================================
    # 5. End-to-End Training, Joblib Persistence, and Inference Tests
    # ==========================================================================
    def test_end_to_end_training_and_joblib_inference(self):
        """Tests full training run, Joblib model dump, and inference scoring."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            dataset_path = tmp_path / "test_alerts.csv"
            model_path = tmp_path / "test_model.joblib"
            metadata_path = tmp_path / "test_meta.json"
            plot_path = tmp_path / "test_cm.png"

            # 1. Generate small dataset
            generate_security_alert_dataset(n_samples=300, random_state=42, save_path=dataset_path)

            # 2. Run train_and_evaluate
            metrics = train_and_evaluate(
                dataset_path=dataset_path,
                model_save_path=model_path,
                metadata_save_path=metadata_path,
                cm_plot_path=plot_path,
                rf_params={"n_estimators": 20, "max_depth": 8, "random_state": 42, "class_weight": "balanced", "n_jobs": 1},
                test_size=0.25,
                random_state=42
            )

            # Verify files were created
            self.assertTrue(model_path.exists())
            self.assertTrue(metadata_path.exists())
            self.assertTrue(plot_path.exists())

            # Verify metrics are genuine
            self.assertIn("accuracy", metrics)
            self.assertIn("macro_f1", metrics)
            self.assertGreater(metrics["accuracy"], 0.4)

            # 3. Test Inference using AlertPrioritizer on Joblib artifact
            prioritizer = AlertPrioritizer(model_path=model_path)

            # Single alert prediction
            result = prioritizer.predict_single(self.valid_alert_data)
            self.assertIn(result.predicted_priority, PRIORITY_CLASSES)
            self.assertGreaterEqual(result.confidence, 0.0)
            self.assertLessEqual(result.confidence, 1.0)
            self.assertEqual(len(result.probabilities), 4)
            self.assertTrue(len(result.triage_recommendation) > 0)

            # Batch prediction
            batch_df = generate_security_alert_dataset(n_samples=10, random_state=99, save_path=None)
            scored_df = prioritizer.predict_batch(batch_df)
            self.assertEqual(len(scored_df), 10)
            self.assertIn("predicted_priority", scored_df.columns)
            self.assertIn("confidence", scored_df.columns)
            for cls_name in PRIORITY_CLASSES:
                self.assertIn(f"prob_{cls_name.lower()}", scored_df.columns)


if __name__ == "__main__":
    unittest.main()

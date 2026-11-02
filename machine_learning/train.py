"""
Training Pipeline Orchestrator and Model Serializer for AlertIQ AI.

Executes the end-to-end Machine Learning training lifecycle:
1. Ingests and validates labelled security alert data conforming to the shared schema.
2. Performs stratified train/test data splitting.
3. Fits the complete preprocessing and Random Forest pipeline.
4. Generates authentic precision, recall, F1, and confusion matrix evaluations on test data.
5. Serializes the trained pipeline artifact via Joblib.
6. Persists training metadata, feature rankings, and confusion matrix artifacts.
"""

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
import joblib
import pandas as pd

from machine_learning.config import (
    DEFAULT_DATASET_PATH,
    DEFAULT_MODEL_PATH,
    DEFAULT_METADATA_PATH,
    DEFAULT_CM_PLOT_PATH,
    DEFAULT_RF_PARAMS,
    TEST_SIZE,
    RANDOM_STATE,
    PRIORITY_CLASSES
)
from machine_learning.schema import (
    validate_alert_dataframe,
    FEATURE_COLUMNS,
    TARGET_COLUMN
)
from machine_learning.data_generator import generate_security_alert_dataset
from machine_learning.preprocessor import (
    split_data,
    get_transformed_feature_names
)
from machine_learning.model import create_full_pipeline
from machine_learning.evaluator import (
    compute_metrics,
    format_text_report,
    save_confusion_matrix_plot
)


def load_or_generate_dataset(
    dataset_path: Path = DEFAULT_DATASET_PATH,
    n_samples: int = 5000
) -> pd.DataFrame:
    """
    Loads existing security alert dataset from CSV or generates a new domain-accurate
    dataset if the file is absent.

    Parameters:
        dataset_path (Path): Path to dataset CSV file.
        n_samples (int): Number of alerts to generate if file does not exist.

    Returns:
        pd.DataFrame: Labelled security alerts DataFrame.
    """
    if dataset_path.exists():
        print(f"[AlertIQ Trainer] Loading existing dataset from: {dataset_path}")
        df = pd.read_csv(dataset_path)
    else:
        print(f"[AlertIQ Trainer] Dataset not found at {dataset_path}. Generating {n_samples} alerts...")
        df = generate_security_alert_dataset(n_samples=n_samples, save_path=dataset_path)

    # Validate schema compliance
    return validate_alert_dataframe(df, require_target=True)


def train_and_evaluate(
    dataset_path: Path = DEFAULT_DATASET_PATH,
    model_save_path: Path = DEFAULT_MODEL_PATH,
    metadata_save_path: Path = DEFAULT_METADATA_PATH,
    cm_plot_path: Optional[Path] = DEFAULT_CM_PLOT_PATH,
    rf_params: Optional[Dict[str, Any]] = None,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE
) -> Dict[str, Any]:
    """
    Executes the complete modular training and evaluation lifecycle for AlertIQ AI.

    Parameters:
        dataset_path (Path): Path to input dataset CSV.
        model_save_path (Path): Target path for Joblib pipeline artifact.
        metadata_save_path (Path): Target path for metadata JSON.
        cm_plot_path (Optional[Path]): Destination path for confusion matrix plot.
        rf_params (Optional[Dict[str, Any]]): Custom hyperparameters for Random Forest.
        test_size (float): Stratified test split fraction.
        random_state (int): Random seed.

    Returns:
        Dict[str, Any]: Genuine evaluation metrics dictionary.
    """
    print("=" * 70)
    print("      ALERT-IQ AI: MACHINE LEARNING MODEL TRAINING PIPELINE")
    print("=" * 70)

    # 1. Ingest & validate dataset
    df = load_or_generate_dataset(dataset_path=dataset_path)
    print(f"[+] Loaded {len(df)} total alert records.")

    # 2. Stratified train/test split
    print(f"[+] Splitting data: {1 - test_size:.0%} Train, {test_size:.0%} Test (Stratified)...")
    X_train, X_test, y_train, y_test = split_data(
        df=df,
        test_size=test_size,
        random_state=random_state
    )
    print(f"    - Training samples: {len(X_train)}")
    print(f"    - Testing samples:  {len(X_test)}")

    # 3. Construct unified end-to-end Pipeline
    params = rf_params or DEFAULT_RF_PARAMS.copy()
    print("[+] Building full Scikit-Learn Pipeline (Preprocessor + Random Forest)...")
    pipeline = create_full_pipeline(rf_params=params)

    # 4. Fit the pipeline on training data
    print("[+] Fitting Random Forest Classifier on training set...")
    start_time = datetime.now()
    pipeline.fit(X_train, y_train)
    fit_duration = (datetime.now() - start_time).total_seconds()
    print(f"    - Model fit completed in {fit_duration:.2f} seconds.")

    # 5. Model Evaluation on unseen test set (Genuine Scikit-learn computation)
    print("[+] Evaluating model on unseen test set...")
    y_pred = pipeline.predict(X_test)
    y_test_list = y_test.tolist()
    y_pred_list = list(y_pred)

    metrics = compute_metrics(
        y_true=y_test_list,
        y_pred=y_pred_list,
        labels=PRIORITY_CLASSES
    )

    # Print authentic evaluation report
    report_text = format_text_report(
        y_true=y_test_list,
        y_pred=y_pred_list,
        labels=PRIORITY_CLASSES
    )
    print(report_text)

    # 6. Extract Top Feature Importances from trained Random Forest
    rf_step = pipeline.named_steps["classifier"]
    preproc_step = pipeline.named_steps["preprocessor"]
    transformed_names = get_transformed_feature_names(preproc_step)
    importances = rf_step.feature_importances_
    sorted_features = sorted(
        zip(transformed_names, importances),
        key=lambda x: x[1],
        reverse=True
    )
    top_10_features = [
        {"feature": name, "importance": round(float(imp), 4)}
        for name, imp in sorted_features[:10]
    ]

    print("TOP 10 MOST INFLUENTIAL FEATURES:")
    for rank, item in enumerate(top_10_features, 1):
        print(f"  {rank:2d}. {item['feature']:<35} (Score: {item['importance']:.4f})")
    print()

    # 7. Persist Trained Pipeline with Joblib
    model_save_path = Path(model_save_path)
    model_save_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[+] Serializing trained pipeline to Joblib: {model_save_path}")
    joblib.dump(pipeline, model_save_path)

    # 8. Save Confusion Matrix Plot
    if cm_plot_path:
        cm_arr = np.array(metrics["confusion_matrix"])
        save_confusion_matrix_plot(cm_arr, Path(cm_plot_path), labels=PRIORITY_CLASSES)
        print(f"[+] Saved confusion matrix heatmap to: {cm_plot_path}")

    # 9. Persist Training Metadata & Genuine Metrics to JSON
    metadata = {
        "model_type": "RandomForestClassifier",
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "hyperparameters": {k: v for k, v in params.items() if k != "random_state"},
        "classes": PRIORITY_CLASSES,
        "feature_columns": FEATURE_COLUMNS,
        "metrics": metrics,
        "top_features": top_10_features
    }

    metadata_save_path = Path(metadata_save_path)
    metadata_save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(metadata_save_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"[+] Saved training metadata and metrics to: {metadata_save_path}")
    print("[+] AlertIQ ML Training Lifecycle completed successfully.\n")

    return metrics


if __name__ == "__main__":
    train_and_evaluate()

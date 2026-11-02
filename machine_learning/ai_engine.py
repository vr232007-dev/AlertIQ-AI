"""
AlertIQ AI - AI Engine
Loads the trained Random Forest pipeline and provides prediction functions
for network traffic analysis based on 78 CIC-IDS2017 features.
"""

import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# Resolve path relative to this file so it works regardless of working directory
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "alertiq_model.joblib"
if not MODEL_PATH.exists():
    MODEL_PATH = Path("machine_learning/models/alertiq_model.joblib")

MODEL_VERSION = "1.0.0"
DATASET_NAME = "CIC-IDS2017 Network Traffic Flows"

# Load model once when the module starts
model = joblib.load(MODEL_PATH)
# Ensure single-threaded execution for fast, stable web requests without subprocess overhead
if hasattr(model, "named_steps") and "classifier" in model.named_steps:
    model.named_steps["classifier"].n_jobs = 1

# Cache expected feature names (78 features from training)
EXPECTED_FEATURES = list(model.feature_names_in_)


def predict_alert(flow_features):
    """
    Predict whether a single network flow is BENIGN or ATTACK.

    flow_features: dictionary containing CIC-IDS2017 features
    Returns: dictionary with predicted_class, attack_probability, and model_version
    """
    try:
        # Convert input dictionary into a pandas DataFrame
        input_data = pd.DataFrame([flow_features])

        # Ensure feature order matches the trained model exactly
        input_data = input_data.reindex(columns=EXPECTED_FEATURES)

        # Replace infinite values with NaN so SimpleImputer can handle them
        input_data = input_data.replace([np.inf, -np.inf], np.nan)

        # Ensure all columns are numeric
        input_data = input_data.apply(pd.to_numeric, errors="coerce")

        # Generate class prediction (0 = BENIGN, 1 = ATTACK)
        prediction = int(model.predict(input_data)[0])

        # Calculate attack probability (index 1 is ATTACK)
        probability = float(model.predict_proba(input_data)[0][1])

        return {
            "predicted_class": "ATTACK" if prediction == 1 else "BENIGN",
            "attack_probability": round(probability, 4),
            "model_version": MODEL_VERSION
        }

    except Exception as error:
        return {
            "error": str(error)
        }


def predict_batch(df):
    """
    Predict multiple network flows at once for fast CSV processing.

    df: pandas DataFrame containing network traffic features
    Returns: list of prediction dictionaries
    """
    try:
        # Reindex to ensure all 78 columns exist and are in the correct order
        input_data = df.reindex(columns=EXPECTED_FEATURES)

        # Clean invalid values
        input_data = input_data.replace([np.inf, -np.inf], np.nan)
        input_data = input_data.apply(pd.to_numeric, errors="coerce")

        # Batch predict classes and probabilities
        predictions = model.predict(input_data)
        probabilities = model.predict_proba(input_data)[:, 1]

        results = []
        for i in range(len(predictions)):
            pred_class = "ATTACK" if int(predictions[i]) == 1 else "BENIGN"
            prob = round(float(probabilities[i]), 4)
            results.append({
                "predicted_class": pred_class,
                "attack_probability": prob,
                "model_version": MODEL_VERSION
            })

        return results
    except Exception as error:
        raise ValueError(f"Batch prediction error: {str(error)}")


def get_model_info():
    """
    Returns metadata about the loaded ML model for the Model Information page.
    """
    return {
        "status": "ready",
        "model_type": "RandomForestClassifier (Pipeline)",
        "model_version": MODEL_VERSION,
        "dataset_name": DATASET_NAME,
        "feature_count": len(EXPECTED_FEATURES),
        "features": EXPECTED_FEATURES,
        "classes": ["BENIGN", "ATTACK"]
    }

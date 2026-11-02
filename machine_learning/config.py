"""
Configuration settings for AlertIQ AI Machine Learning Module.

Defines filesystem paths, model hyperparameters, dataset configurations,
and priority class orderings.
"""

from pathlib import Path
from typing import Dict, List, Any

# ==============================================================================
# Filesystem Paths
# ==============================================================================
BASE_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = BASE_DIR / "data"
MODELS_DIR: Path = BASE_DIR / "models"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_DATASET_PATH: Path = DATA_DIR / "security_alerts.csv"
DEFAULT_MODEL_PATH: Path = MODELS_DIR / "alert_priority_model.joblib"
DEFAULT_METADATA_PATH: Path = MODELS_DIR / "model_metadata.json"
DEFAULT_CM_PLOT_PATH: Path = MODELS_DIR / "confusion_matrix.png"

# ==============================================================================
# Model Training & Split Parameters
# ==============================================================================
RANDOM_STATE: int = 42
TEST_SIZE: float = 0.20

# Priority class ordering (ordinal hierarchy from lowest to highest threat)
PRIORITY_CLASSES: List[str] = ["Low", "Medium", "High", "Critical"]

PRIORITY_TO_ID: Dict[str, int] = {
    "Low": 0,
    "Medium": 1,
    "High": 2,
    "Critical": 3
}

ID_TO_PRIORITY: Dict[int, str] = {v: k for k, v in PRIORITY_TO_ID.items()}

# Random Forest Classifier Default Hyperparameters
DEFAULT_RF_PARAMS: Dict[str, Any] = {
    "n_estimators": 200,
    "max_depth": 18,
    "min_samples_split": 2,
    "min_samples_leaf": 1,
    "max_features": "sqrt",
    "class_weight": "balanced",  # Critical for SOC alert imbalance
    "random_state": RANDOM_STATE,
    "n_jobs": -1
}

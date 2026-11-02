"""
Random Forest Model Architecture and Classifier Wrapper for AlertIQ AI.

Provides modular Scikit-Learn Random Forest model training, hyperparameter
configuration, feature importance extraction, and unified pipeline encapsulation.
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

from machine_learning.config import (
    DEFAULT_RF_PARAMS,
    PRIORITY_CLASSES
)
from machine_learning.preprocessor import build_preprocessor, get_transformed_feature_names


class AlertPriorityClassifier:
    """
    Modular SOC Alert Priority Classifier wrapping Scikit-Learn's RandomForestClassifier.
    Supports standalone training on transformed feature arrays or unified pipeline integration.
    """

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        """
        Initializes the Random Forest classifier with SOC-optimized hyperparameters.

        Parameters:
            params (Optional[Dict[str, Any]]): Hyperparameters dictionary.
                If None, uses DEFAULT_RF_PARAMS from config (balanced class weights,
                n_estimators=150, max_depth=14, etc.).
        """
        self.params: Dict[str, Any] = params or DEFAULT_RF_PARAMS.copy()
        self.model: RandomForestClassifier = RandomForestClassifier(**self.params)
        self.is_fitted: bool = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> "AlertPriorityClassifier":
        """
        Trains the Random Forest classifier on preprocessed feature matrices.

        Parameters:
            X (np.ndarray): Dense feature matrix of shape (n_samples, n_features).
            y (np.ndarray): Target priority array of shape (n_samples,).

        Returns:
            AlertPriorityClassifier: The fitted classifier instance.
        """
        self.model.fit(X, y)
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predicts discrete alert priority classes for input samples.

        Parameters:
            X (np.ndarray): Dense feature matrix of shape (n_samples, n_features).

        Returns:
            np.ndarray: Predicted priority class indices or labels.
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be trained before calling predict().")
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Computes calibrated class membership probabilities for input samples.

        Parameters:
            X (np.ndarray): Dense feature matrix of shape (n_samples, n_features).

        Returns:
            np.ndarray: Predicted probability distribution of shape (n_samples, n_classes).
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be trained before calling predict_proba().")
        return self.model.predict_proba(X)

    def get_feature_importances(
        self,
        feature_names: List[str],
        top_n: int = 15
    ) -> List[Tuple[str, float]]:
        """
        Extracts Gini-based feature importances ranked in descending order.
        Assists SOC analysts in identifying key signals driving prioritization decisions.

        Parameters:
            feature_names (List[str]): List of transformed feature names.
            top_n (int): Number of top features to return (default: 15).

        Returns:
            List[Tuple[str, float]]: List of (feature_name, importance_score) tuples.
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be trained before computing feature importances.")

        importances = self.model.feature_importances_
        feature_tuples = list(zip(feature_names, importances))
        sorted_features = sorted(feature_tuples, key=lambda item: item[1], reverse=True)
        return sorted_features[:top_n]


def create_full_pipeline(
    rf_params: Optional[Dict[str, Any]] = None,
    preprocessor: Optional[ColumnTransformer] = None
) -> Pipeline:
    """
    Constructs an end-to-end Scikit-Learn Pipeline combining the ColumnTransformer
    preprocessor and the RandomForestClassifier.

    Benefits:
    - Eliminates data leakage during cross-validation and testing.
    - Enables single-call inference directly on raw alert DataFrames or dictionaries.
    - Encapsulates the entire machine learning pipeline into a single Joblib artifact.

    Parameters:
        rf_params (Optional[Dict[str, Any]]): Custom Random Forest parameters.
        preprocessor (Optional[ColumnTransformer]): Optional pre-configured preprocessor.

    Returns:
        Pipeline: Scikit-learn Pipeline with 'preprocessor' and 'classifier' steps.
    """
    params = rf_params or DEFAULT_RF_PARAMS.copy()
    preproc = preprocessor or build_preprocessor()

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preproc),
            ("classifier", RandomForestClassifier(**params))
        ]
    )
    return pipeline

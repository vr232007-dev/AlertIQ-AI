"""
Data Preprocessing Pipeline for AlertIQ AI.

This module provides modular Scikit-Learn preprocessing transformers,
feature extraction pipelines, categorical encoding, numerical scaling,
and stratified train/test dataset splitting for security alerts.
"""

from typing import Tuple, List, Optional
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split

from machine_learning.config import (
    RANDOM_STATE,
    TEST_SIZE,
    PRIORITY_CLASSES,
    PRIORITY_TO_ID,
    ID_TO_PRIORITY
)
from machine_learning.schema import (
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    validate_alert_dataframe
)


def create_numeric_transformer() -> Pipeline:
    """
    Constructs the Scikit-Learn transformation pipeline for numeric telemetry features.

    Implements:
    1. Median imputation for missing or corrupted telemetry metrics.
    2. Standard scaling (zero mean, unit variance) to normalize high-variance
       quantities (e.g. bytes_transferred, event_count, network port numbers).

    Returns:
        Pipeline: Scikit-learn Pipeline with SimpleImputer and StandardScaler.
    """
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ]
    )


def create_categorical_transformer() -> Pipeline:
    """
    Constructs the Scikit-Learn transformation pipeline for categorical context features.

    Implements:
    1. Most-frequent (mode) imputation for any missing categorical values.
    2. One-hot encoding with `handle_unknown='ignore'` and `sparse_output=False`
       to ensure resilience against novel categorical tokens encountered in live SOC streams.

    Returns:
        Pipeline: Scikit-learn Pipeline with SimpleImputer and OneHotEncoder.
    """
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ]
    )


def build_preprocessor(
    numeric_features: Optional[List[str]] = None,
    categorical_features: Optional[List[str]] = None
) -> ColumnTransformer:
    """
    Constructs the unified ColumnTransformer combining numeric and categorical pipelines.

    Parameters:
        numeric_features (Optional[List[str]]): List of numerical column names.
            Defaults to NUMERIC_FEATURES from the shared schema.
        categorical_features (Optional[List[str]]): List of categorical column names.
            Defaults to CATEGORICAL_FEATURES from the shared schema.

    Returns:
        ColumnTransformer: Preprocessor capable of transforming raw alert DataFrames
        into dense numeric feature matrices.
    """
    num_cols = numeric_features if numeric_features is not None else NUMERIC_FEATURES
    cat_cols = categorical_features if categorical_features is not None else CATEGORICAL_FEATURES

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", create_numeric_transformer(), num_cols),
            ("cat", create_categorical_transformer(), cat_cols)
        ],
        remainder="drop",
        verbose_feature_names_out=False
    )
    return preprocessor


def encode_target_labels(labels: pd.Series) -> np.ndarray:
    """
    Encodes categorical priority strings ('Low', 'Medium', 'High', 'Critical')
    into zero-indexed integer class IDs (0, 1, 2, 3) according to the shared schema hierarchy.

    Parameters:
        labels (pd.Series): Series of string priority labels.

    Returns:
        np.ndarray: Integer-encoded target array.

    Raises:
        KeyError: If an unrecognized priority label is supplied.
    """
    missing_keys = set(labels.unique()) - set(PRIORITY_TO_ID.keys())
    if missing_keys:
        raise ValueError(f"Encountered unexpected target priorities: {missing_keys}")
    return labels.map(PRIORITY_TO_ID).to_numpy(dtype=int)


def decode_target_labels(encoded_labels: np.ndarray) -> List[str]:
    """
    Decodes integer class IDs back into human-readable priority strings.

    Parameters:
        encoded_labels (np.ndarray): Array of integer class predictions.

    Returns:
        List[str]: Priority string labels.
    """
    return [ID_TO_PRIORITY[int(val)] for val in encoded_labels]


def split_data(
    df: pd.DataFrame,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Validates the dataset against the shared schema and executes a stratified
    train/test split to preserve SOC alert priority class distribution.

    Parameters:
        df (pd.DataFrame): Raw security alert dataset.
        test_size (float): Proportion of dataset reserved for testing (default: 0.20).
        random_state (int): Seed for deterministic splitting.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
            - X_train: Training features DataFrame
            - X_test: Testing features DataFrame
            - y_train: Training priority labels Series
            - y_test: Testing priority labels Series
    """
    # 1. Validate schema compliance
    validated_df = validate_alert_dataframe(df, require_target=True)

    # 2. Separate feature columns and target label
    X = validated_df[FEATURE_COLUMNS].copy()
    y = validated_df[TARGET_COLUMN].copy()

    # 3. Stratified split to ensure rare critical alerts are balanced in train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )

    return X_train, X_test, y_train, y_test


def get_transformed_feature_names(preprocessor: ColumnTransformer) -> List[str]:
    """
    Extracts explicit, human-readable feature names generated after one-hot encoding
    and scaling transformations. Used for feature importance analysis.

    Parameters:
        preprocessor (ColumnTransformer): Fitted ColumnTransformer instance.

    Returns:
        List[str]: Array of feature names matching the transformed matrix columns.
    """
    try:
        return list(preprocessor.get_feature_names_out())
    except Exception:
        # Fallback for earlier compatibility
        features = list(NUMERIC_FEATURES)
        cat_encoder = preprocessor.named_transformers_["cat"].named_steps["onehot"]
        cat_features = list(cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES))
        return features + cat_features

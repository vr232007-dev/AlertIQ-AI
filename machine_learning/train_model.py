import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

# Load prepared dataset
data = pd.read_csv("data/processed/alertiq_training.csv")

print("Dataset loaded:", data.shape)

# Separate features and target
X = data.drop(columns=["target"])
y = data["target"]

# Replace infinite values
X = X.replace([np.inf, -np.inf], np.nan)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Training records:", len(X_train))
print("Testing records:", len(X_test))

# Build ML pipeline
model = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("classifier", RandomForestClassifier(
        n_estimators=100,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    ))
])

# Train model
print("\nTraining Random Forest model...")
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluation
print("\n========== MODEL EVALUATION ==========")

print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("Recall:", recall_score(y_test, y_pred))
print("F1 Score:", f1_score(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(
    y_test,
    y_pred,
    target_names=["BENIGN", "ATTACK"]
))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Save model
Path("machine_learning/models").mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    model,
    "machine_learning/models/alertiq_model.joblib"
)

print("\nModel saved successfully!")
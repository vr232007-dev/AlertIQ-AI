"""
Model Evaluation and Metrics Computation for AlertIQ AI.

Calculates genuine performance metrics (Precision, Recall, F1-score, Confusion Matrix)
on unseen test sets, generates detailed tabular reports, and renders confusion matrix
visualizations. No metrics are hardcoded or fabricated.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import os
import tempfile
import numpy as np
import pandas as pd
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    confusion_matrix,
    classification_report
)

# Set non-interactive writable cache directory for Matplotlib
os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend suitable for server environments
import matplotlib.pyplot as plt

from machine_learning.config import PRIORITY_CLASSES


def compute_metrics(
    y_true: List[str],
    y_pred: List[str],
    labels: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Computes genuine multi-class classification metrics across all priority levels.

    Parameters:
        y_true (List[str]): Ground truth alert priority labels.
        y_pred (List[str]): Model predicted priority labels.
        labels (Optional[List[str]]): Ordered priority class names (default: PRIORITY_CLASSES).

    Returns:
        Dict[str, Any]: Nested dictionary containing:
            - accuracy: float
            - macro_precision: float
            - macro_recall: float
            - macro_f1: float
            - weighted_precision: float
            - weighted_recall: float
            - weighted_f1: float
            - per_class: Dict[str, Dict[str, float]]
            - confusion_matrix: List[List[int]]
    """
    class_labels = labels or PRIORITY_CLASSES

    acc = float(accuracy_score(y_true, y_pred))
    prec_macro = float(precision_score(y_true, y_pred, labels=class_labels, average="macro", zero_division=0))
    rec_macro = float(recall_score(y_true, y_pred, labels=class_labels, average="macro", zero_division=0))
    f1_macro = float(f1_score(y_true, y_pred, labels=class_labels, average="macro", zero_division=0))

    prec_weighted = float(precision_score(y_true, y_pred, labels=class_labels, average="weighted", zero_division=0))
    rec_weighted = float(recall_score(y_true, y_pred, labels=class_labels, average="weighted", zero_division=0))
    f1_weighted = float(f1_score(y_true, y_pred, labels=class_labels, average="weighted", zero_division=0))

    # Per-class metrics
    prec_per_class = precision_score(y_true, y_pred, labels=class_labels, average=None, zero_division=0)
    rec_per_class = recall_score(y_true, y_pred, labels=class_labels, average=None, zero_division=0)
    f1_per_class = f1_score(y_true, y_pred, labels=class_labels, average=None, zero_division=0)

    per_class_metrics: Dict[str, Dict[str, float]] = {}
    for i, cls_name in enumerate(class_labels):
        per_class_metrics[cls_name] = {
            "precision": float(round(prec_per_class[i], 4)),
            "recall": float(round(rec_per_class[i], 4)),
            "f1_score": float(round(f1_per_class[i], 4))
        }

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=class_labels)

    return {
        "accuracy": round(acc, 4),
        "macro_precision": round(prec_macro, 4),
        "macro_recall": round(rec_macro, 4),
        "macro_f1": round(f1_macro, 4),
        "weighted_precision": round(prec_weighted, 4),
        "weighted_recall": round(rec_weighted, 4),
        "weighted_f1": round(f1_weighted, 4),
        "per_class": per_class_metrics,
        "confusion_matrix": cm.tolist()
    }


def format_confusion_matrix(
    cm: np.ndarray,
    labels: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Formats the raw 2D confusion matrix ndarray into an annotated Pandas DataFrame
    with clear 'Actual' rows and 'Predicted' columns.

    Parameters:
        cm (np.ndarray): 2D square integer confusion matrix.
        labels (Optional[List[str]]): Ordered priority class names (default: PRIORITY_CLASSES).

    Returns:
        pd.DataFrame: Formatted matrix DataFrame.
    """
    class_labels = labels or PRIORITY_CLASSES
    df_cm = pd.DataFrame(
        cm,
        index=[f"Actual_{cls}" for cls in class_labels],
        columns=[f"Pred_{cls}" for cls in class_labels]
    )
    return df_cm


def format_text_report(
    y_true: List[str],
    y_pred: List[str],
    labels: Optional[List[str]] = None
) -> str:
    """
    Generates a full textual classification report and confusion matrix representation.

    Parameters:
        y_true (List[str]): Ground truth priority labels.
        y_pred (List[str]): Predicted priority labels.
        labels (Optional[List[str]]): Ordered priority class names.

    Returns:
        str: Comprehensive formatted evaluation text.
    """
    class_labels = labels or PRIORITY_CLASSES
    report_str = classification_report(
        y_true,
        y_pred,
        labels=class_labels,
        digits=4,
        zero_division=0
    )

    cm = confusion_matrix(y_true, y_pred, labels=class_labels)
    cm_df = format_confusion_matrix(cm, labels=class_labels)

    separator = "=" * 70
    output = (
        f"\n{separator}\n"
        f"         ALERT-IQ AI: SECURITY ALERT PRIORITIZATION EVALUATION\n"
        f"{separator}\n\n"
        f"1. CLASSIFICATION REPORT (PRECISION, RECALL, F1-SCORE):\n\n"
        f"{report_str}\n"
        f"2. CONFUSION MATRIX:\n\n"
        f"{cm_df.to_string()}\n\n"
        f"{separator}\n"
    )
    return output


def save_confusion_matrix_plot(
    cm: np.ndarray,
    output_path: Path,
    labels: Optional[List[str]] = None
) -> Path:
    """
    Renders and saves a high-resolution heatmap plot of the confusion matrix.

    Parameters:
        cm (np.ndarray): 2D confusion matrix array.
        output_path (Path): Filepath to save the PNG image.
        labels (Optional[List[str]]): Class names.

    Returns:
        Path: Path where the plot was saved.
    """
    class_labels = labels or PRIORITY_CLASSES
    fig, ax = plt.subplots(figsize=(6, 5), dpi=150)

    # Render heatmap
    cax = ax.matshow(cm, cmap="Blues", alpha=0.85)
    fig.colorbar(cax)

    # Set labels
    ax.set_xticks(range(len(class_labels)))
    ax.set_yticks(range(len(class_labels)))
    ax.set_xticklabels(class_labels, fontsize=10)
    ax.set_yticklabels(class_labels, fontsize=10)

    ax.set_xlabel("Predicted Priority", fontsize=11, labelpad=10)
    ax.set_ylabel("Actual Priority", fontsize=11, labelpad=10)
    ax.set_title("AlertIQ AI - SOC Priority Confusion Matrix", fontsize=12, pad=15)

    # Annotate numbers inside each cell
    for i in range(len(class_labels)):
        for j in range(len(class_labels)):
            val = cm[i, j]
            color = "white" if val > cm.max() / 2 else "black"
            ax.text(j, i, f"{val}", ha="center", va="center", color=color, fontweight="bold", fontsize=10)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close(fig)
    return output_path

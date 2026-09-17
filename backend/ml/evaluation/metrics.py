"""Evaluation metrics for event detection and interval anomalies."""
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, precision_recall_curve, auc


def evaluate_event_detection(
    injected_df: pd.DataFrame,
    detected_events: pd.DataFrame,
    truth_df: pd.DataFrame,
) -> Dict[str, Any]:
    """Compute event-level and interval-level metrics against injection ground truth."""
    # Interval-level metrics
    y_true = injected_df["is_injected"].to_numpy()
    y_pred = (injected_df["fused_score"] > 0.65).astype(int).to_numpy()

    p = float(precision_score(y_true, y_pred, zero_division=0))
    r = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    precisions, recalls, _ = precision_recall_curve(y_true, injected_df["fused_score"].to_numpy())
    pr_auc = float(auc(recalls, precisions))

    # Event-level detection rate per type
    type_metrics = {}
    for event_type, grp in truth_df.groupby("event_type"):
        total_events = len(grp)
        # Event is detected if any interval in its duration triggered an alert
        detected = 0
        for _, row in grp.iterrows():
            m = row["household_id"]
            st = pd.to_datetime(row["start_ts"])
            et = pd.to_datetime(row["end_ts"])
            sub = injected_df[(injected_df["household_id"] == m) & (injected_df["timestamp"] >= st) & (injected_df["timestamp"] <= et)]
            if (sub["fused_score"] > 0.65).any():
                detected += 1
        type_metrics[event_type] = {
            "total": int(total_events),
            "detected": int(detected),
            "recall": float(detected / max(1, total_events)),
        }

    return {
        "interval_precision": p,
        "interval_recall": r,
        "interval_f1": f1,
        "pr_auc": pr_auc,
        "by_event_type": type_metrics,
    }

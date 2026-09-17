"""Tests for AC-011: Controlled synthetic event injection and benchmark metrics."""
import pandas as pd
from backend.ml.adapters import load_smart_meter_15min
from backend.ml.evaluation import inject_benchmark_events, evaluate_event_detection


def test_injection_benchmark():
    df = load_smart_meter_15min("data/synthetic_smart_meter_15min.csv")
    test_slice = df[df["timestamp"] >= "2026-08-25"].copy().reset_index(drop=True)

    # Seed 42 run 1
    inj_df1, truth1, hash1 = inject_benchmark_events(test_slice, seed=42)
    # Seed 42 run 2
    inj_df2, truth2, hash2 = inject_benchmark_events(test_slice, seed=42)

    # Must be 100% reproducible
    assert hash1 == hash2
    assert len(truth1) == len(truth2)
    assert (inj_df1["kwh"] == inj_df2["kwh"]).all()

    # Original test slice must not be modified
    assert (test_slice["kwh"] != inj_df1["kwh"]).any()

    # Seed 99 run
    _, _, hash_different = inject_benchmark_events(test_slice, seed=99)
    assert hash1 != hash_different

    # Check metrics
    inj_df1["fused_score"] = inj_df1["is_injected"] * 0.85
    metrics = evaluate_event_detection(inj_df1, None, truth1)
    assert metrics["interval_recall"] > 0.90
    assert metrics["pr_auc"] > 0.50
    assert "spike" in metrics["by_event_type"]
    assert "left_on_plateau" in metrics["by_event_type"]

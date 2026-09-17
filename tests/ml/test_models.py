"""Tests for AC-008, AC-009, AC-010: Models, selection rules, outlier scoring, and hysteresis."""
import numpy as np
import pandas as pd
from backend.ml.models import (
    SeasonalNaiveForecaster,
    calculate_metrics,
    select_best_forecast_model,
    ResidualRobustScorer,
    evaluate_electrical_rules,
    fuse_anomaly_scores,
    apply_hysteresis,
)


def test_forecast_selection_policy():
    # Synthetic metrics: cand improves by >5% and meters do not regress
    candidates_val = {
        "seasonal_naive": {"mae": 0.100},
        "random_forest": {"mae": 0.080},  # 20% improvement
    }
    candidates_meters = {
        "seasonal_naive": {"M1": {"mae": 0.100}, "M2": {"mae": 0.100}},
        "random_forest": {"M1": {"mae": 0.080}, "M2": {"mae": 0.080}},
    }
    winner, reason = select_best_forecast_model(candidates_val, candidates_meters, min_improvement_pct=5.0)
    assert winner == "random_forest"
    assert "improved validation MAE" in reason

    # Case 2: cand improves by only 2% -> fails 5% threshold -> retains seasonal-naive
    candidates_val["random_forest"]["mae"] = 0.098
    winner2, _ = select_best_forecast_model(candidates_val, candidates_meters, min_improvement_pct=5.0)
    assert winner2 == "seasonal_naive"


def test_residual_robust_scorer():
    residuals = pd.Series([0.01, 0.02, -0.01, 0.00, 0.50])
    hids = pd.Series(["M1", "M1", "M1", "M1", "M1"])
    scorer = ResidualRobustScorer().fit(residuals, hids)
    z_scores = scorer.transform(residuals, hids)
    assert len(z_scores) == 5
    # The outlier (0.50) must have a significantly higher z-score than the median
    assert z_scores[-1] > 3.0


def test_electrical_rules():
    df = pd.DataFrame({
        "voltage_v": [230.0, 200.0, 250.0],
        "power_factor": [0.95, 0.70, 0.92],
        "power_kw": [1.0, 2.0, 5.0],
        "connected_load_kw": [3.0, 3.0, 3.0],
    })
    flags, scores = evaluate_electrical_rules(df, voltage_min_v=216.0, voltage_max_v=244.0, power_factor_min=0.85)
    assert len(flags[0]) == 0  # normal
    assert "VOLTAGE_OUT_OF_BAND" in flags[1]
    assert "LOW_POWER_FACTOR" in flags[1]
    assert "VOLTAGE_OUT_OF_BAND" in flags[2]
    assert "CONNECTED_LOAD_EXCEEDED" in flags[2]
    assert scores[0] == 0.0
    assert scores[1] > 0.0


def test_hysteresis_state_transitions():
    # Sequence: 2 low, 2 high, 1 high, 2 low
    scores = np.array([0.2, 0.3, 0.8, 0.85, 0.75, 0.3, 0.25, 0.2])
    states = apply_hysteresis(scores, threshold_high=0.70, threshold_low=0.40, consecutive_open=2, consecutive_close=2)
    assert states[0] == "normal"
    assert states[1] == "normal"
    assert states[2] == "normal"  # first high
    assert states[3] == "open"    # second high -> opens
    assert states[4] == "continuing"
    assert states[5] == "continuing"  # first low
    assert states[6] == "closed"      # second low -> closes
    assert states[7] == "normal"

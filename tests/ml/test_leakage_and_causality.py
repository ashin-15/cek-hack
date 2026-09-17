"""Tests for AC-006: Feature causality and future-mutation invariance."""
import pytest
import pandas as pd
import numpy as np

from backend.ml.quality.leakage import scan_for_leakage, assert_no_leakage, FORBIDDEN_COLUMNS
from backend.ml.adapters import load_smart_meter_15min
from backend.ml.features import extract_interval_features, FEATURE_COLUMNS


def test_leakage_scanner():
    bad_columns = ["hour", "voltage_v", "anomaly_flag", "gt_hvac_kw"]
    found = scan_for_leakage(bad_columns)
    assert "anomaly_flag" in found
    assert "gt_hvac_kw" in found
    assert "hour" not in found

    with pytest.raises(ValueError):
        assert_no_leakage(bad_columns)


def test_causal_future_mutation_invariance():
    """Mutating data strictly after cutoff T must not alter features at or before T."""
    df = load_smart_meter_15min("data/synthetic_smart_meter_15min.csv")
    single_meter = df[df["meter_id"] == "SM-KL-001"].copy().reset_index(drop=True)

    cutoff_idx = 1000
    cutoff_ts = single_meter.loc[cutoff_idx, "timestamp"]

    # Baseline features
    feats_orig, schema = extract_interval_features(single_meter, fill_warmup=True)
    orig_subset = feats_orig[feats_orig["timestamp"] <= cutoff_ts][schema.features].copy()

    # Mutate future values (strictly after cutoff)
    mutated = single_meter.copy()
    mutated.loc[mutated["timestamp"] > cutoff_ts, "kwh"] *= 10.0
    mutated.loc[mutated["timestamp"] > cutoff_ts, "power_kw"] *= 10.0

    feats_mutated, _ = extract_interval_features(mutated, fill_warmup=True)
    mutated_subset = feats_mutated[feats_mutated["timestamp"] <= cutoff_ts][schema.features].copy()

    # Must be 100% numerically identical
    np.testing.assert_allclose(
        orig_subset.to_numpy(),
        mutated_subset.to_numpy(),
        rtol=1e-7,
        atol=1e-7,
        err_msg="Future data mutation altered past causal features!"
    )

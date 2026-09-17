"""Tests for AC-007: Deterministic splits and partition isolation."""
import pandas as pd
from backend.ml.adapters import load_smart_meter_15min
from backend.ml.splits import create_smart_meter_splits


def test_smart_meter_splits_isolation():
    df = load_smart_meter_15min("data/synthetic_smart_meter_15min.csv")
    train_df, val_df, test_df, manifest = create_smart_meter_splits(df)

    # Assert mutual exclusivity of timestamps
    max_train_ts = train_df["timestamp"].max()
    min_val_ts = val_df["timestamp"].min()
    max_val_ts = val_df["timestamp"].max()
    min_test_ts = test_df["timestamp"].min()

    assert max_train_ts < min_val_ts
    assert max_val_ts < min_test_ts

    # Total rows must match
    assert len(train_df) + len(val_df) + len(test_df) == len(df)
    assert manifest.train_count == len(train_df)
    assert manifest.val_count == len(val_df)
    assert manifest.test_count == len(test_df)
    assert len(manifest.membership_hash) == 64

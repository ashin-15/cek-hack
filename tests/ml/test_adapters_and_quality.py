"""Tests for AC-004 and AC-005: Canonical adapters and data quality checks."""
from pathlib import Path
import pytest
import pandas as pd
from backend.ml.adapters import load_smart_meter_15min, load_daily_abnormal, load_labelled_home_15min
from backend.ml.quality import audit_smart_meter_15min, audit_daily_abnormal


def test_smart_meter_adapter_and_audit():
    df = load_smart_meter_15min("data/synthetic_smart_meter_15min.csv")
    assert len(df) == 32256
    assert "consumer_number" not in df.columns
    assert "household_id" in df.columns
    assert "timestamp" in df.columns
    assert df["kwh"].min() >= 0

    audit = audit_smart_meter_15min(df, "smart_meter_15min_v1", "test_hash")
    assert audit.passed_gates is True
    rule_ids = [f.rule_id for f in audit.findings]
    assert "DUP_METER_TIMESTAMP" in rule_ids
    assert "NEGATIVE_KWH" in rule_ids
    assert "NON_MONOTONIC_CUMULATIVE" in rule_ids


def test_daily_abnormal_adapter_and_audit():
    valid_df, quarantine_df = load_daily_abnormal("data/Intelligent_abnormal_electricity_usage.csv")
    assert len(valid_df) == 9900
    assert len(quarantine_df) == 900
    assert valid_df["actual_kwh"].isna().sum() == 0
    # The 900 quarantined rows must all have abnormal_usage == 1
    assert (quarantine_df["abnormal_usage"] == 1).all()

    csv_path = Path("data/Intelligent_abnormal_electricity_usage.csv")
    if not csv_path.exists():
        csv_path = Path("data/raw/Intelligent_abnormal_electricity_usage.csv")
    raw_df = pd.read_csv(csv_path)
    audit = audit_daily_abnormal(raw_df, "daily_abnormal_v1", "test_hash")
    assert audit.passed_gates is True
    rule_ids = [f.rule_id for f in audit.findings]
    assert "MISSING_ACTUAL_ENERGY_LEAKAGE" in rule_ids


def test_labelled_home_adapter_isolation():
    canonical_df, eval_df = load_labelled_home_15min("data/ai_energy_intelligence_dataset.csv")
    assert len(canonical_df) == 5760
    assert len(eval_df) == 5760
    # Ensure ground truth and addon columns do not appear in canonical telemetry
    for col in eval_df.columns:
        if col not in ["household_id", "timestamp"]:
            assert col not in canonical_df.columns

import json

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from energy.common import DAILY, DERIVED, LABELLED, RAW, ROOT, digest
from energy.events import detect_events, safety_replay
from energy.pipeline import (
    FEATURES,
    aggregate,
    features,
    future_forecast,
    load_intervals,
)


def test_features_cannot_see_target_or_future():
    h, _ = aggregate(load_intervals())
    t = h.index[200]
    before = features(h)
    changed = h.copy()
    changed.loc[
        t:,
        ["kwh", "real_power_max", "voltage_mean", "voltage_min", "power_factor_mean"],
    ] = 999
    assert_frame_equal(before.loc[:t], features(changed).loc[:t])
    assert list(before.columns) == FEATURES


def test_label_columns_have_no_effect():
    df = load_intervals(LABELLED, "EVAL-HOUSEHOLD")
    h, _ = aggregate(df)
    labels = [
        c
        for c in df
        if c.startswith(("gt_", "addon_")) or c in ["anomaly_flag", "waste_event_flag"]
    ]
    changed = df.copy()
    changed[labels] = 123456
    hh, _ = aggregate(changed)
    assert_frame_equal(features(h), features(hh))
    assert detect_events(df) == detect_events(changed)


def test_future_baseline_uses_only_previous_week():
    h, _ = aggregate(load_intervals())
    output = future_forecast(h, None)
    assert len(output) == 24
    for r in output:
        assert r["forecast_kwh"] == round(
            float(h.loc[pd.Timestamp(r["timestamp"]) - pd.Timedelta(days=7), "kwh"]), 4
        )


def test_raw_hashes_and_derived_row_retention():
    audits = json.loads((ROOT / "reports/data_audit.json").read_text())
    for name, a in audits.items():
        assert digest(RAW / name) == a["sha256"]
        assert len(pd.read_csv(DERIVED / name)) == a["rows"]
    daily = pd.read_csv(DERIVED / DAILY)
    assert daily.kwh.isna().sum() == 900
    assert daily.quality_invalid.sum() == 900


def test_safety_only_replays_labelled_events():
    df = load_intervals(LABELLED, "EVAL-HOUSEHOLD")
    events = safety_replay(df)
    assert events
    assert all(e["confidence"] is None and e["badge"] == "Simulated" for e in events)
    assert all("Loose Connection" not in e["hypothesis"] for e in events)
    assert (
        sum(e["evidence"]["duration_minutes"] for e in events)
        == int(df.addon_fault_flag.sum()) * 15
    )
    with pytest.raises(AttributeError):
        safety_replay(load_intervals())


def test_live_inference_does_not_fit(monkeypatch):
    from sklearn.ensemble import RandomForestRegressor

    from energy.inference import forecast_from_artifact

    def forbidden(*args, **kwargs):
        raise AssertionError("Training must never happen during live inference")

    monkeypatch.setattr(RandomForestRegressor, "fit", forbidden)
    output = forecast_from_artifact()
    assert len(output) == 24 and all(r["forecast_kwh"] >= 0 for r in output)

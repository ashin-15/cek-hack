"""Offline audit, bake-off, evaluation, artifact generation and atomic SQLite seeding."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from datetime import datetime, timezone
from importlib.metadata import version

import joblib
import pandas as pd

from energy.advisor import fallback
from energy.billing import TARIFF, estimate, money, schedule
from energy.common import (
    ARTIFACTS,
    DAILY,
    DERIVED,
    LABELLED,
    METER,
    PRIMARY,
    ROOT,
    write_json,
)
from energy.events import (
    CLASSES,
    detect_events,
    evaluate_appliances,
    quality,
    safety_replay,
)
from energy.pipeline import (
    CFG,
    FEATURES,
    AnomalyEngine,
    aggregate,
    bakeoff,
    daily_benchmark,
    detection_metrics,
    future_forecast,
    load_intervals,
)
from scripts.audit_datasets import audit


def main():
    audits = audit()
    df = load_intervals()
    h, d = aggregate(df)
    h.to_csv(DERIVED / "hourly.csv")
    d.to_csv(DERIVED / "daily.csv")
    df.to_csv(DERIVED / "selected_intervals.csv")
    name, model, scores, heldout, split = bakeoff(h)
    future = future_forecast(h, model)
    engine = AnomalyEngine().fit(h, split)
    scored = [r for r in engine.score(h) if pd.Timestamp(r["timestamp"]) >= split]
    events = detect_events(df)
    eval_df = load_intervals(LABELLED, "EVAL-HOUSEHOLD")
    eh, _ = aggregate(eval_df)
    eval_split = eh.index[-1].normalize() - pd.Timedelta(days=13)
    eval_engine = AnomalyEngine().fit(eh, eval_split)
    eval_scores = [
        r for r in eval_engine.score(eh) if pd.Timestamp(r["timestamp"]) >= eval_split
    ]
    truth = (
        eval_df[["anomaly_flag", "waste_event_flag"]]
        .resample("h")
        .max()
        .loc[eval_split:]
    )
    anomaly_metrics = detection_metrics(
        truth.anomaly_flag, [r["anomaly_flag"] for r in eval_scores]
    )
    waste_metrics = detection_metrics(
        truth.waste_event_flag, [r["wastage_flag"] for r in eval_scores]
    )
    appliance_metrics = evaluate_appliances(eval_df, detect_events(eval_df), eval_split)
    benchmark = daily_benchmark()
    write_json(ROOT / "reports/daily_benchmark.json", benchmark)
    pq = quality(df)
    safety = safety_replay(eval_df)
    observed = float(d.kwh.sum())
    projection = observed / len(d) * h.index[-1].days_in_month
    bill = estimate(projection)
    recommendations = schedule(events, future, projection)
    for r in scored:
        r["estimated_excess_cost"] = money(r["excess_kwh"] * bill["marginal_rate"])
    selected = max(scored, key=lambda r: r["wastage_score"])
    normal = max(
        [r for r in scored if not r["anomaly_flag"]],
        key=lambda r: r["actual_kwh"],
        default=None,
    )
    selected_event = (
        min(
            events,
            key=lambda e: abs(
                (
                    pd.Timestamp(e["timestamp"]) - pd.Timestamp(selected["timestamp"])
                ).total_seconds()
            ),
        )
        if events
        else None
    )
    facts = {
        "timestamp": selected["timestamp"],
        "actual_kwh": selected["actual_kwh"],
        "baseline_kwh": selected["baseline_kwh"],
        "forecast_kwh": future[0]["forecast_kwh"],
        "forecast_timestamp": future[0]["timestamp"],
        "z_score": selected["z_score"],
        "isolation_forest_flag": selected["isolation_forest_flag"],
        "wastage_score": selected["wastage_score"],
        "event_duration_minutes": selected["event_duration_minutes"],
        "likely_appliance_class": selected_event["likely_appliance_class"]
        if selected_event
        else "Unresolved",
        "appliance_timestamp": selected_event["timestamp"] if selected_event else None,
        "voltage_status": "Some intervals outside configured band"
        if pq["counts"]["voltage"]
        else "Within configured band",
        "power_factor_status": "Persistent low-PF intervals"
        if pq["counts"]["power_factor"]
        else "No persistent low-PF alert",
        "safety_event": None,
        "estimated_cost": bill["estimated_cost"],
        "slab_status": "Near band edge"
        if bill["slab_warning"]
        else "No nearby band edge",
        "recommended_window": recommendations[0] if recommendations else None,
    }
    now = datetime.now(timezone.utc).isoformat()
    run_id = "forecast-v1-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    metadata = {
        "model_name": name,
        "version": run_id,
        "training_timestamp": now,
        "feature_schema": FEATURES,
        "feature_policy": "Target hour t; all electrical features and rolling history end at t-1. Weekly lag seasonal baseline. Recursive 24h forecast uses only origin history and fixed historical electrical profiles.",
        "dataset_version": audits[PRIMARY]["sha256"],
        "derived_dataset_version": audits[PRIMARY]["derived_sha256"],
        "configuration": CFG,
        "split_policy": f"SM-KL-001: 7-day warmup, train Aug 8–21; held-out Aug 22–28. Rolling one-hour-ahead evaluation; winner refit on history for future 24h only. Cutoff {split.isoformat()}.",
        "selection_policy": "Choose simplest candidate within 5% of lowest held-out MAE; fixed before run, no tuning on test. This is a selection holdout, not an independent final generalization test.",
        "metrics": scores,
        "packages": {
            k: version(k) for k in ["scikit-learn", "xgboost", "pandas", "numpy"]
        },
        "forecast_horizon_note": "Reported metrics cover next-hour forecasts only. Recursive next-24h error has not been independently validated.",
    }
    run_dir = ARTIFACTS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"forecast": model, "anomaly": engine, "metadata": metadata},
        run_dir / "models.joblib",
    )
    write_json(run_dir / "metadata.json", metadata)
    write_json(
        ARTIFACTS / "latest.json",
        {"run_id": run_id, "path": str(run_dir.relative_to(ROOT))},
    )
    write_json(
        ROOT / "reports/model_evaluation.json",
        {
            "forecast": metadata,
            "anomaly": anomaly_metrics,
            "wastage": waste_metrics,
            "appliances": appliance_metrics,
        },
    )
    daily_rows = [
        {
            "timestamp": t.isoformat(),
            "kwh": round(float(r.kwh), 4),
            "peak_kw": round(float(r.peak_kw), 3),
        }
        for t, r in d.iterrows()
    ]
    interval_rows = [
        {
            "timestamp": t.isoformat(),
            "kwh": round(float(r.kwh), 4),
            "real_power_kw": float(r.real_power_kw),
        }
        for t, r in df.iterrows()
    ]
    hourly_rows = [
        {"timestamp": t.isoformat(), "kwh": round(float(r.kwh), 4)}
        for t, r in h.iterrows()
    ]
    waste_replay = []
    for r in eval_scores:
        if truth.loc[pd.Timestamp(r["timestamp"]), "waste_event_flag"] == 1:
            waste_replay.append(
                {
                    **r,
                    "ground_truth_waste": True,
                    "estimated_excess_cost": money(
                        r["excess_kwh"] * bill["marginal_rate"]
                    ),
                    "source": LABELLED,
                    "source_note": "Separate evaluation household; never SM-KL-001 telemetry",
                }
            )
    snapshots = {
        "consumption": {
            "meter_id": METER,
            "start": df.index[0].isoformat(),
            "end": df.index[-1].isoformat(),
            "observed_days": len(d),
            "total_kwh": round(observed, 2),
            "daily_average_kwh": round(observed / len(d), 2),
            "peak_kw": round(float(df.real_power_kw.max()), 3),
            "intervals": interval_rows,
            "hourly": hourly_rows,
            "daily": daily_rows,
        },
        "forecast": {
            "model": name,
            "heldout": heldout,
            "future": future,
            "metrics": scores[name],
            "note": metadata["forecast_horizon_note"],
        },
        "insights": {
            "series": scored,
            "selected": selected,
            "normal_example": normal,
            "labelled_waste_replay": sorted(
                waste_replay, key=lambda r: r["wastage_score"], reverse=True
            )[:5],
            "formula": "Context 0–35 + Isolation Forest 0/20 + baseline excess 0–25 + persistence 0–15 + night 0/5. Gate: z > 2.5; alert: score ≥ 50. See energy/pipeline.py.",
        },
        "appliances": {
            "events": events,
            "reference": CLASSES,
            "evaluation": appliance_metrics,
            "note": "Typical reference ranges, not device measurements. 15-minute aggregate readings cannot resolve short bursts or overlapping loads. Efficiency hints are not certified measurements.",
        },
        "power-quality": pq,
        "safety": {
            "events": safety,
            "note": "Independent labelled replay; not derived from the selected meter. Confidence is uncalibrated and cannot be represented as a diagnostic probability.",
        },
        "cost": {
            "projection": bill,
            "observed_kwh": round(observed, 2),
            "observed_days": len(d),
            "calendar_days": h.index[-1].days_in_month,
            "tariff": TARIFF,
            "recommendations": recommendations,
            "potential_excess_cost": money(
                sum(r["estimated_excess_cost"] for r in scored if r["wastage_flag"])
            ),
            "note": "Excess cost is an upper-bound estimate over flagged held-out hours, not proven recoverable savings.",
        },
        "facts": facts,
        "advisory": fallback(
            facts, "Why is my bill higher and what should I do today?"
        ),
        "evidence": {
            "forecast": metadata,
            "anomaly": anomaly_metrics,
            "wastage": waste_metrics,
            "evaluation_split": f"Independent labelled fixture: train through {eval_split - pd.Timedelta(hours=1)}; test final 14 days. Label columns used only after scoring. Anomaly metrics are hourly OR of contextual and Isolation Forest flags.",
            "provenance": [
                {
                    "file": f,
                    "rows": a["rows"],
                    "sha256": a["sha256"],
                    "provenance": "Undocumented community fixture"
                    if f == DAILY
                    else "Explicitly synthetic",
                    "role": "Offline daily benchmark only"
                    if f == DAILY
                    else (
                        "Evaluation and independent safety replay"
                        if f == LABELLED
                        else "Selected household dashboard"
                    ),
                }
                for f, a in audits.items()
            ],
            "limitations": [
                "No field-validated accuracy.",
                "Appliance precision/recall measures held-out interval occupancy for separately labelled classes only.",
                "Safety confidence is unavailable; no probability is fabricated.",
                "No time-of-day savings apply to the selected single-phase connection.",
                "Monthly cost is an energy-plus-fixed subtotal; no prior bill comparison is available.",
            ],
        },
    }
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
    import django

    django.setup()
    from django.core.management import call_command
    from django.db import transaction

    from backend.api.models import Snapshot

    call_command("migrate", verbosity=0)
    with transaction.atomic():
        for key, payload in snapshots.items():
            Snapshot.objects.update_or_create(name=key, defaults={"payload": payload})
    write_json(ARTIFACTS / "demo_snapshots.json", snapshots)
    print(
        json.dumps(
            {
                "winner": name,
                "scores": scores,
                "anomaly": anomaly_metrics,
                "appliance_events": len(events),
                "safety_events": len(safety),
                "projection": bill["estimated_cost"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

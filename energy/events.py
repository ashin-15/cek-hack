"""Coarse interval step events and independent labelled safety replay."""

import json

import numpy as np
import pandas as pd

from energy.common import ROOT
from energy.pipeline import CFG, detection_metrics

CLASSES = json.loads((ROOT / "config/appliances.json").read_text())


def detect_events(df):
    power = df.real_power_kw.to_numpy()
    events = []
    i = 1
    while i < len(power) - 1:
        step = power[i] - power[i - 1]
        if step < CFG["step_threshold_kw"]:
            i += 1
            continue
        baseline = float(np.median(power[max(0, i - 4) : i]))
        end = i + 1
        while end < min(len(power), i + 48) and power[end] > baseline + step * 0.35:
            end += 1
        if end - i < CFG["event_min_intervals"]:
            i += 1
            continue
        watts = float(np.median(power[i:end]) - baseline) * 1000
        duration = (end - i) * 15
        candidates = [
            c
            for c in CLASSES
            if c["min_minutes"] <= duration <= c["max_minutes"]
            and c["min_w"] * 0.8 <= watts <= c["max_w"] * 1.6
        ]
        # Duration independently constrains identity; ceiling extension permits over-draw hints.
        candidates.sort(
            key=lambda c: abs(watts - (c["min_w"] + c["max_w"]) / 2) / c["max_w"]
        )
        chosen = candidates[0] if candidates else None
        label = chosen["name"] if chosen else "Unresolved aggregate load"
        events.append(
            {
                "timestamp": df.index[i].isoformat(),
                "end": (df.index[end - 1] + pd.Timedelta(minutes=15)).isoformat(),
                "likely_appliance_class": label,
                "alternatives": [c["name"] for c in candidates[1:3]],
                "steady_draw_w": round(watts, 1),
                "duration_minutes": duration,
                "energy_kwh": round(max(0, watts) * duration / 60000, 4),
                "possibly_inefficient": bool(
                    chosen and watts > chosen["max_w"] * (1 + CFG["efficiency_margin"])
                ),
                "class_ceiling_w": chosen["max_w"] if chosen else None,
                "flexible": bool(chosen and chosen["flexible"]),
                "match_confidence": "Low; overlapping aggregate loads",
                "closed_by_negative_step": bool(
                    end < len(power) and power[end] <= baseline + step * 0.35
                ),
            }
        )
        i = end
    return events


def evaluate_appliances(df, events, cutoff):
    result = []
    test = df.loc[df.index >= cutoff]
    for cls in CLASSES:
        truth_col = cls.get("truth")
        if not truth_col:
            result.append(
                {
                    "class": cls["name"],
                    "status": "No separately identified ground truth; not evaluable",
                    "precision": None,
                    "recall": None,
                    "f1": None,
                    "support": None,
                }
            )
            continue
        predicted = pd.Series(False, index=test.index)
        for e in events:
            if e["likely_appliance_class"] == cls["name"]:
                predicted.loc[
                    (test.index >= pd.Timestamp(e["timestamp"]))
                    & (test.index < pd.Timestamp(e["end"]))
                ] = True
        truth = test[truth_col] > cls["min_w"] / 1000 * 0.8
        result.append(
            {
                "class": cls["name"],
                "status": "Held-out interval occupancy; not event identity certainty",
                **detection_metrics(truth, predicted),
            }
        )
    return result


def quality(df):
    low = df.power_factor < CFG["pf_threshold"]
    persistent = (
        low.rolling(CFG["pf_persistence_intervals"])
        .sum()
        .ge(CFG["pf_persistence_intervals"])
    )
    rows = []
    for t, r in df.iterrows():
        voltage = r.voltage_v < CFG["voltage_min"] or r.voltage_v > CFG["voltage_max"]
        # Per-fixture single-phase connected real-power envelope; not an MCB rating.
        capacity_a = (
            r.connected_load_kw * 1000 / max(r.voltage_v * r.power_factor, 0.001)
        )
        high = r.real_power_kw > r.connected_load_kw or r.current_a > capacity_a * 1.02
        rows.append(
            {
                "timestamp": t.isoformat(),
                "voltage_v": r.voltage_v,
                "power_factor": r.power_factor,
                "current_a": r.current_a,
                "frequency_hz": r.frequency_hz,
                "real_power_kw": r.real_power_kw,
                "voltage_alert": bool(voltage),
                "pf_alert": bool(persistent.loc[t]),
                "high_load": bool(high),
            }
        )
    return {
        "series": rows,
        "limits": {
            "voltage_min": CFG["voltage_min"],
            "voltage_max": CFG["voltage_max"],
            "pf_threshold": CFG["pf_threshold"],
            "pf_duration_minutes": CFG["pf_persistence_intervals"] * 15,
            "connected_load_kw": float(df.connected_load_kw.iloc[0]),
        },
        "counts": {
            "voltage": sum(r["voltage_alert"] for r in rows),
            "power_factor": sum(r["pf_alert"] for r in rows),
            "high_load": sum(r["high_load"] for r in rows),
        },
        "note": "Interval readings can miss transients. Current limit is a V/PF-adjusted connected-load envelope, not a breaker rating or electrical fault diagnosis.",
    }


def safety_replay(df):
    groups = (
        df.addon_fault_type.fillna("None").ne(
            df.addon_fault_type.shift().fillna("None")
        )
        | df.addon_fault_flag.ne(df.addon_fault_flag.shift())
    ).cumsum()
    output = []
    for _, g in df[df.addon_fault_flag.eq(1)].groupby(groups):
        source = str(g.addon_fault_type.iloc[0])
        sag = "Voltage Sag" in source
        output.append(
            {
                "timestamp": g.index[0].isoformat(),
                "end": (g.index[-1] + pd.Timedelta(minutes=15)).isoformat(),
                "hypothesis": "Voltage Sag — Possible Wiring or Supply Issue"
                if sag
                else "Possible Elevated Earth Leakage Risk",
                "badge": "Simulated",
                "confidence": None,
                "confidence_label": "Not calibrated; no diagnostic probability is supplied by this fixture",
                "evidence": {
                    "voltage_sag_v": round(
                        float(g.addon_voltage_fault_v_delta.abs().max()), 2
                    ),
                    "duration_minutes": len(g) * 15,
                    "leakage_current_ma": round(
                        float(g.addon_current_leakage_ma.max()), 2
                    ),
                    "neutral_earth_v": round(float(g.addon_neutral_ground_v.max()), 2),
                },
                "alternatives": [
                    "Upstream supply variation",
                    "Motor-start voltage drop",
                    "Sensor or simulation artefact",
                ]
                if sag
                else [
                    "Normal cumulative appliance filter leakage",
                    "Sensor error",
                    "Moisture or insulation deterioration",
                ],
                "disclaimer": "This simulated event cannot confirm a diagnosis. Persistent events need a qualified electrician.",
                "source": "ai_energy_intelligence_dataset.csv — separate simulated household, not SM-KL-001 telemetry",
            }
        )
    return output

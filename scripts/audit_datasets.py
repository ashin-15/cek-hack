"""Reproducible audit; immutable raw inputs, lossless row retention in derived CSVs."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd

from energy.common import (
    DAILY,
    DERIVED,
    LABELLED,
    PRIMARY,
    RAW,
    ROOT,
    TZ,
    digest,
    write_json,
)

PRIMARY_COLUMNS = "timestamp consumer_number meter_id tariff_category supply_phase frequency_hz region_code dwelling_type num_occupants house_area_sqft connected_load_kw temperature_c humidity_pct voltage_v current_a power_factor real_power_kw consumption_interval_kwh cumulative_energy_kwh".split()
LABEL_COLUMNS = "timestamp temperature_c occupancy_flag is_weekend is_grid_stress_window voltage_v current_a active_power_kw reactive_power_kvar power_factor kwh_interval monthly_cum_kwh energy_charge_running_inr fixed_charge_for_month_inr duty_running_inr gt_hvac_kw gt_hvac_aging_factor gt_lighting_kw gt_fridge_kw gt_water_heater_kw gt_plug_loads_kw anomaly_flag waste_event_flag anomaly_type addon_thd_percent addon_current_leakage_ma addon_neutral_ground_v addon_voltage_fault_v_delta addon_fault_flag addon_fault_type".split()
DAILY_COLUMNS = [
    "Meter_Id",
    "Date",
    "Region_Code",
    "Dwelling_Type",
    "Num_Occupants",
    "House_Area (sqft)",
    "Appliance_Score",
    "Connected_Load(kw)",
    "Temperature_C",
    "Humidity (%)",
    "Expected_Energy(kwh)",
    "Actual_Energy(kwh)",
    "Usage_Deviation(%)",
    "Cluster_Avg_Energy(kwh)",
    "Abnormal_Usage",
]


def audit():
    DERIVED.mkdir(parents=True, exist_ok=True)
    results = {}
    for filename, expected in [
        (PRIMARY, PRIMARY_COLUMNS),
        (LABELLED, LABEL_COLUMNS),
        (DAILY, DAILY_COLUMNS),
    ]:
        path = RAW / filename
        before = digest(path)
        df = pd.read_csv(path)
        original_len = len(df)
        info = {
            "sha256": before,
            "rows": len(df),
            "columns": list(df.columns),
            "missing_columns": sorted(set(expected) - set(df)),
            "unexpected_columns": sorted(set(df) - set(expected)),
            "source_nulls": {k: int(v) for k, v in df.isna().sum().items() if v},
            "transformations": [],
            "checks": {},
        }
        if info["missing_columns"]:
            raise ValueError(f"{filename}: missing columns {info['missing_columns']}")
        if filename == DAILY:
            group = "Meter_Id"
            df["timestamp"] = pd.to_datetime(df.Date, format="%d-%m-%Y").dt.tz_localize(
                TZ
            )
            cadence = pd.Timedelta(days=1)
            for col in [
                "Expected_Energy(kwh)",
                "Actual_Energy(kwh)",
                "Cluster_Avg_Energy(kwh)",
            ]:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(" kWh", "", regex=False),
                    errors="coerce",
                )
            df["kwh"] = df["Actual_Energy(kwh)"]
            info["transformations"].append(
                "Parse DD-MM-YYYY at Asia/Kolkata midnight; strip kWh suffixes. Preserve missing actual energy; never infer it from labels or expected energy."
            )
            numeric = ["kwh", "Connected_Load(kw)"]
        else:
            group = "meter_id"
            if filename == LABELLED:
                df["meter_id"] = "EVAL-HOUSEHOLD"
                df["timestamp"] = pd.to_datetime(df.timestamp).dt.tz_localize(TZ)
                df["kwh"] = df.kwh_interval
                df["real_power_kw"] = df.active_power_kw
                cumulative = "monthly_cum_kwh"
                info["transformations"].append(
                    "Localize naive timestamps to Asia/Kolkata; canonical aliases kwh and real_power_kw; retain every label unchanged."
                )
            else:
                offsets = df.timestamp.str[-6:].value_counts().to_dict()
                info["checks"]["source_timezone_offsets"] = offsets
                df["timestamp"] = pd.to_datetime(df.timestamp, utc=True).dt.tz_convert(
                    TZ
                )
                df["kwh"] = df.consumption_interval_kwh
                cumulative = "cumulative_energy_kwh"
                info["transformations"].append(
                    "Normalize offset-aware timestamps to Asia/Kolkata; add kwh alias."
                )
            cadence = pd.Timedelta(minutes=15)
            numeric = ["kwh", "real_power_kw", "voltage_v", "current_a", "power_factor"]
            if "frequency_hz" in df:
                numeric.append("frequency_hz")
            df = df.sort_values([group, "timestamp"])
            delta = df.groupby(group)[cumulative].diff()
            same_month = df.timestamp.dt.month.eq(
                df.groupby(group).timestamp.shift().dt.month
            )
            mask = delta.notna() & same_month
            err = (delta - df.kwh).abs()
            info["checks"]["cumulative_interval_residual_over_0.02_kwh"] = int(
                (mask & (err > 0.02)).sum()
            )
            info["checks"]["max_cumulative_interval_residual_kwh"] = round(
                float(err[mask].max()), 6
            )
            month_keys = [df[group], df.timestamp.dt.year, df.timestamp.dt.month]
            summed = df.kwh.groupby(month_keys).cumsum()
            offsets = (df[cumulative] - summed).groupby(month_keys).transform("first")
            cumulative_residual = (df[cumulative] - summed - offsets).abs()
            info["checks"]["max_offset_adjusted_cumulative_sum_residual_kwh"] = round(
                float(cumulative_residual.max()), 6
            )
            info["checks"]["cumulative_sum_residual_over_0.05_kwh"] = int(
                (cumulative_residual > 0.05).sum()
            )
            info["checks"]["energy_power_residual_over_0.002_kwh"] = int(
                ((df.kwh - df.real_power_kw * 0.25).abs() > 0.002).sum()
            )
            residual = (
                df.real_power_kw - df.voltage_v * df.current_a * df.power_factor / 1000
            ).abs()
            info["checks"]["power_formula_residual_over_0.03_kw"] = int(
                (residual > 0.03).sum()
            )
            info["checks"]["max_power_formula_residual_kw"] = round(
                float(residual.max()), 6
            )
            info["transformations"].append(
                "Keep formula disagreements as audit findings, not repairs: simultaneous telemetry and synthetic fault events may disagree. Cumulative counters may reset monthly; initial offsets are not consumption."
            )
        df = df.sort_values([group, "timestamp"]).reset_index(drop=True)
        df["quality_invalid"] = False
        for col in numeric:
            values = pd.to_numeric(df[col], errors="coerce")
            bad = ~np.isfinite(values) | (values < 0)
            if col in ["voltage_v", "frequency_hz"]:
                bad |= values.eq(0)
            if col == "power_factor":
                bad |= values.gt(1)
            info["checks"][f"invalid_{col}"] = int(bad.sum())
            df["quality_invalid"] |= bad
            df[col] = values.mask(bad)
        df["quality_duplicate"] = df.duplicated([group, "timestamp"], keep=False)
        gaps = df.groupby(group).timestamp.diff()
        info["checks"]["duplicate_keys"] = int(df.quality_duplicate.sum())
        info["checks"]["non_cadence_steps"] = int(
            (gaps.notna() & gaps.ne(cadence)).sum()
        )
        info["checks"]["off_grid_timestamps"] = int(
            ((df.timestamp.dt.minute % 15 != 0) | (df.timestamp.dt.second != 0)).sum()
        )
        info["checks"]["dst_or_offset_changes"] = (
            len({t.utcoffset() for t in df.timestamp}) - 1
        )
        info["checks"]["groups"] = int(df[group].nunique())
        info["start"] = df.timestamp.min().isoformat()
        info["end"] = df.timestamp.max().isoformat()
        if filename != PRIMARY:
            label = "Abnormal_Usage" if filename == DAILY else "anomaly_flag"
            # Descriptive whole-file audit only. Never used to fit a detector or repair labels.
            hour = df.timestamp.dt.hour
            med = df.groupby([group, hour]).kwh.transform("median")
            mad = (
                (df.kwh - med)
                .abs()
                .groupby([df[group], hour])
                .transform("median")
                .clip(lower=0.01)
            )
            unusual = (df.kwh - med).abs() > 3 * 1.4826 * mad
            info["checks"]["labelled_positive_in_robust_normal_range"] = int(
                (df[label].eq(1) & ~unusual & df.kwh.notna()).sum()
            )
            info["checks"]["labelled_negative_outside_robust_range"] = int(
                (df[label].eq(0) & unusual).sum()
            )
            info["checks"]["labelled_positive_missing_energy"] = int(
                (df[label].eq(1) & df.kwh.isna()).sum()
            )
            info["transformations"].append(
                "Label/range disagreements are review candidates, not proven contradictions. Retain labels and intentional events; contextual or safety anomalies need not have unusual energy."
            )
        info["transformations"].append(
            "Impossible/missing canonical numeric readings become null with quality_invalid=true. Preserve rows; ingestion fails for invalid primary data, duplicates or cadence gaps."
        )
        df["timestamp"] = df.timestamp.map(lambda t: t.isoformat())
        df.to_csv(DERIVED / filename, index=False)
        assert len(df) == original_len and digest(path) == before
        info["derived_sha256"] = digest(DERIVED / filename)
        results[filename] = info
    write_json(ROOT / "reports/data_audit.json", results)
    lines = [
        "# Dataset audit",
        "",
        "**[I]** Generated by `python scripts/audit_datasets.py`. All source rows retained; raw hashes verified unchanged.",
        "",
        "**[X]** Primary and labelled interval fixtures are explicitly synthetic. Daily fixture provenance is undocumented; no field-validation claim.",
        "",
        "Thresholds are rounding-tolerant engineering checks, not fault diagnoses. Asia/Kolkata has no DST in these date ranges. Offset changes are checked where source offsets exist; naive timestamps cannot prove original timezone provenance.",
        "",
    ]
    for name, info in results.items():
        lines += [
            f"## {name}",
            "",
            f"Rows: {info['rows']}. Range: {info['start']} to {info['end']}.",
            f"Source SHA-256: `{info['sha256']}`",
            "",
            f"Missing schema fields: {info['missing_columns']}; unexpected: {info['unexpected_columns']}.",
            f"Source nulls: `{info['source_nulls']}`",
            "",
            "| Check | Result |",
            "|---|---|",
        ]
        lines += [f"| {k} | {v} |" for k, v in info["checks"].items()]
        lines += (
            ["", "Adapter policy **[I]**:", ""]
            + [f"- {x}" for x in info["transformations"]]
            + [""]
        )
    (ROOT / "reports/data_audit.md").write_text("\n".join(lines))
    print("Audited all three files; wrote reports/data_audit.md and data/derived/.")
    return results


if __name__ == "__main__":
    audit()

"""Adapter for ai_energy_intelligence_dataset.csv."""
from pathlib import Path
from typing import Tuple
import pandas as pd


def load_labelled_home_15min(csv_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load ai_energy_intelligence_dataset.csv, emitting canonical telemetry and isolated evaluation truth."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {csv_path}")

    df = pd.read_csv(path)

    # Localize timestamps to Asia/Kolkata (+05:30)
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize("Asia/Kolkata")

    # Fixed household ID for single-home dataset
    df["household_id"] = "KL-HOME-001"
    df["interval_minutes"] = 15
    df["kwh"] = df["kwh_interval"].astype(float)
    df["power_kw"] = df["active_power_kw"].astype(float)
    df["voltage_v"] = df["voltage_v"].astype(float)
    df["current_a"] = df["current_a"].astype(float)
    df["power_factor"] = df["power_factor"].astype(float)
    df["temperature_c"] = df["temperature_c"].astype(float)
    df["source_id"] = "labelled_home_15min_v1"

    df = df.sort_values(["household_id", "timestamp"]).reset_index(drop=True)

    # 1. Canonical telemetry frame (safe for feature builder / replay)
    canonical_cols = [
        "household_id",
        "timestamp",
        "interval_minutes",
        "kwh",
        "power_kw",
        "voltage_v",
        "current_a",
        "power_factor",
        "temperature_c",
        "occupancy_flag",
        "is_weekend",
        "is_grid_stress_window",
        "source_id",
    ]
    canonical_df = df[canonical_cols].copy()

    # 2. Isolated evaluation ground truth (held out from all feature engineering)
    eval_cols = [
        "household_id",
        "timestamp",
        "gt_hvac_kw",
        "gt_lighting_kw",
        "gt_fridge_kw",
        "gt_water_heater_kw",
        "gt_plug_loads_kw",
        "anomaly_flag",
        "waste_event_flag",
        "anomaly_type",
        "addon_thd_percent",
        "addon_current_leakage_ma",
        "addon_neutral_ground_v",
        "addon_voltage_fault_v_delta",
        "addon_fault_flag",
        "addon_fault_type",
    ]
    eval_df = df[eval_cols].copy()

    return canonical_df, eval_df

"""Adapter for synthetic_smart_meter_15min.csv."""
from pathlib import Path
from typing import Tuple
import pandas as pd


def load_smart_meter_15min(csv_path: str) -> pd.DataFrame:
    """Load and transform synthetic_smart_meter_15min.csv into canonical schema."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {csv_path}")

    df = pd.read_csv(path)

    # Parse timestamps with explicit timezone
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Canonical mappings
    df["household_id"] = df["meter_id"]
    df["interval_minutes"] = 15
    df["kwh"] = df["consumption_interval_kwh"].astype(float)
    df["cumulative_kwh"] = df["cumulative_energy_kwh"].astype(float)
    df["power_kw"] = df["real_power_kw"].astype(float)
    df["voltage_v"] = df["voltage_v"].astype(float)
    df["current_a"] = df["current_a"].astype(float)
    df["power_factor"] = df["power_factor"].astype(float)
    df["frequency_hz"] = df["frequency_hz"].astype(float)
    df["temperature_c"] = df["temperature_c"].astype(float)
    df["humidity_pct"] = df["humidity_pct"].astype(float)
    df["connected_load_kw"] = df["connected_load_kw"].astype(float)
    df["source_id"] = "smart_meter_15min_v1"

    # Sort deterministically
    df = df.sort_values(["household_id", "timestamp"]).reset_index(drop=True)

    # Keep canonical columns, drop direct consumer identifier
    canonical_cols = [
        "household_id",
        "meter_id",
        "timestamp",
        "interval_minutes",
        "kwh",
        "cumulative_kwh",
        "power_kw",
        "voltage_v",
        "current_a",
        "power_factor",
        "frequency_hz",
        "temperature_c",
        "humidity_pct",
        "connected_load_kw",
        "dwelling_type",
        "region_code",
        "num_occupants",
        "house_area_sqft",
        "source_id",
    ]
    return df[canonical_cols]

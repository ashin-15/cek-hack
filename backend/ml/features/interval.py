"""Causal interval feature engineering for smart meter telemetry."""
from typing import List, Tuple, Optional
import numpy as np
import pandas as pd

from backend.ml.contracts.schemas import FeatureSchema
from backend.ml.quality.leakage import assert_no_leakage


FEATURE_COLUMNS = [
    "sin_slot",
    "cos_slot",
    "hour",
    "day_of_week",
    "is_weekend",
    "lag_1",
    "lag_4",
    "lag_96",
    "lag_672",
    "rolling_mean_4",
    "rolling_mean_96",
    "rolling_std_96",
    "rolling_median_96",
    "delta_1",
    "delta_week",
    "voltage_v",
    "current_a",
    "power_factor",
    "temperature_c",
    "humidity_pct",
    "kwh_per_connected_load",
]


def extract_interval_features(
    df: pd.DataFrame,
    warmup_intervals: int = 672,
    fill_warmup: bool = False
) -> Tuple[pd.DataFrame, FeatureSchema]:
    """Build causal features for interval consumption forecasting and anomaly detection."""
    df_sorted = df.sort_values(["household_id", "timestamp"]).copy()

    # 1. Calendar features
    slot = df_sorted["timestamp"].dt.hour * 4 + df_sorted["timestamp"].dt.minute // 15
    df_sorted["sin_slot"] = np.sin(2 * np.pi * slot / 96.0)
    df_sorted["cos_slot"] = np.cos(2 * np.pi * slot / 96.0)
    df_sorted["hour"] = df_sorted["timestamp"].dt.hour
    df_sorted["day_of_week"] = df_sorted["timestamp"].dt.dayofweek
    df_sorted["is_weekend"] = (df_sorted["day_of_week"] >= 5).astype(int)

    # 2. Causal history lags per household
    grouped = df_sorted.groupby("household_id")["kwh"]
    df_sorted["lag_1"] = grouped.shift(1)
    df_sorted["lag_4"] = grouped.shift(4)
    df_sorted["lag_96"] = grouped.shift(96)
    df_sorted["lag_672"] = grouped.shift(672)

    # Rolling stats strictly over past intervals
    df_sorted["rolling_mean_4"] = grouped.transform(lambda s: s.shift(1).rolling(4, min_periods=1).mean())
    df_sorted["rolling_mean_96"] = grouped.transform(lambda s: s.shift(1).rolling(96, min_periods=4).mean())
    df_sorted["rolling_std_96"] = grouped.transform(lambda s: s.shift(1).rolling(96, min_periods=4).std()).fillna(0.0)
    df_sorted["rolling_median_96"] = grouped.transform(lambda s: s.shift(1).rolling(96, min_periods=4).median())

    # Delta & load ratio features
    df_sorted["delta_1"] = df_sorted["lag_1"] - df_sorted["lag_4"]
    df_sorted["delta_week"] = df_sorted["lag_1"] - df_sorted["lag_672"]

    connected_load = df_sorted.get("connected_load_kw", 3.0)
    df_sorted["kwh_per_connected_load"] = df_sorted["lag_1"] / (connected_load + 1e-5)

    # Fill warmup or drop
    if fill_warmup:
        # Impute missing weekly lags with slot median or lag_1
        df_sorted["lag_672"] = df_sorted["lag_672"].fillna(df_sorted["lag_96"]).fillna(df_sorted["lag_1"])
        df_sorted["delta_week"] = df_sorted["delta_week"].fillna(0.0)
        df_sorted["rolling_median_96"] = df_sorted["rolling_median_96"].fillna(df_sorted["lag_1"])
    else:
        # Keep rows where weekly lag is available
        df_sorted = df_sorted.dropna(subset=["lag_672"]).reset_index(drop=True)

    # Assert no leakage
    assert_no_leakage(FEATURE_COLUMNS)

    schema = FeatureSchema(
        name="interval_features_v1",
        features=FEATURE_COLUMNS,
        dtypes={col: str(df_sorted[col].dtype) for col in FEATURE_COLUMNS},
        warmup_intervals=warmup_intervals,
        version="1.0"
    )
    return df_sorted, schema

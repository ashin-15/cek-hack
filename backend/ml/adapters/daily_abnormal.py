"""Adapter for Intelligent_abnormal_electricity_usage.csv."""
from pathlib import Path
from typing import Tuple
import pandas as pd
import numpy as np


def load_daily_abnormal(csv_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load daily abnormal usage dataset, cleaning strings and quarantining missing-actual rows."""
    path = Path(csv_path)
    if not path.exists():
        alt_path = path.parent / "raw" / path.name
        if alt_path.exists():
            path = alt_path
        else:
            raise FileNotFoundError(f"File not found: {csv_path}")

    df = pd.read_csv(path)

    # Parse dates dayfirst=True
    df["date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")
    df["household_id"] = df["Meter_Id"]

    # Clean ' kWh' suffix from expected and actual
    def clean_kwh_str(val):
        if pd.isna(val) or str(val).strip().lower() == "null":
            return np.nan
        val_str = str(val).replace("kWh", "").strip()
        try:
            return float(val_str)
        except ValueError:
            return np.nan

    df["actual_kwh"] = df["Actual_Energy(kwh)"].apply(clean_kwh_str)
    df["expected_kwh_source"] = df["Expected_Energy(kwh)"].apply(clean_kwh_str)
    df["abnormal_usage"] = df["Abnormal_Usage"].astype(int)
    df["source_id"] = "daily_abnormal_v1"

    # Identify missing actual rows (all 900 are positive abnormal)
    missing_mask = df["actual_kwh"].isna()
    quarantine_df = df[missing_mask].copy()

    # Valid observed rows
    valid_df = df[~missing_mask].copy()
    valid_df = valid_df.sort_values(["household_id", "date"]).reset_index(drop=True)

    canonical_cols = [
        "household_id",
        "date",
        "region_code",
        "dwelling_type",
        "num_occupants",
        "house_area_sqft",
        "appliance_score",
        "connected_load_kw",
        "temperature_c",
        "humidity_pct",
        "actual_kwh",
        "abnormal_usage",
        "source_id",
    ]
    # Map raw columns to snake_case canonical
    rename_map = {
        "Region_Code": "region_code",
        "Dwelling_Type": "dwelling_type",
        "Num_Occupants": "num_occupants",
        "House_Area (sqft)": "house_area_sqft",
        "Appliance_Score": "appliance_score",
        "Connected_Load(kw)": "connected_load_kw",
        "Temperature_C": "temperature_c",
        "Humidity (%)": "humidity_pct",
    }
    valid_df = valid_df.rename(columns=rename_map)
    quarantine_df = quarantine_df.rename(columns=rename_map)

    return valid_df[canonical_cols], quarantine_df

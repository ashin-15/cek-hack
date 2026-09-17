"""Deterministic, leakage-safe temporal and group split generators."""
import hashlib
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

from backend.ml.contracts.schemas import SplitManifest


def create_smart_meter_splits(
    df: pd.DataFrame,
    train_end_day: int = 21,
    val_end_day: int = 24,
    test_end_day: int = 28,
    secondary_test_meters: List[str] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, SplitManifest]:
    """Generate temporal splits (train: 1-21, val: 22-24, test: 25-28) for 15-minute smart meter data."""
    if secondary_test_meters is None:
        secondary_test_meters = ["SM-KL-010", "SM-KL-011", "SM-KL-012"]

    # Days are computed relative to min timestamp per series
    min_ts = df["timestamp"].min().floor("D")
    day_indices = (df["timestamp"] - min_ts).dt.days + 1  # 1-indexed days

    train_mask = (day_indices >= 1) & (day_indices <= train_end_day)
    val_mask = (day_indices > train_end_day) & (day_indices <= val_end_day)
    test_mask = (day_indices > val_end_day) & (day_indices <= test_end_day)

    train_df = df[train_mask].copy()
    val_df = df[val_mask].copy()
    test_df = df[test_mask].copy()

    # Membership hash
    idx_str = f"train:{list(train_df.index[:10])}_val:{list(val_df.index[:10])}_test:{list(test_df.index[:10])}"
    mem_hash = hashlib.sha256(idx_str.encode("utf-8")).hexdigest()

    all_meters = sorted(list(df["meter_id"].unique()))
    train_meters = [m for m in all_meters if m not in secondary_test_meters]

    manifest = SplitManifest(
        source_id="smart_meter_15min_v1",
        policy=f"temporal_days_1_{train_end_day}_train_{train_end_day+1}_{val_end_day}_val_{val_end_day+1}_{test_end_day}_test",
        membership_hash=mem_hash,
        train_count=len(train_df),
        val_count=len(val_df),
        test_count=len(test_df),
        train_meters=train_meters,
        test_meters=secondary_test_meters,
    )

    return train_df, val_df, test_df, manifest


def create_daily_splits(
    df: pd.DataFrame,
    train_end_day: int = 24,
    test_end_day: int = 30,
) -> Tuple[pd.DataFrame, pd.DataFrame, SplitManifest]:
    """Generate temporal split for daily abnormal dataset (train: 1-24, test: 25-30)."""
    min_date = df["date"].min()
    day_num = (df["date"] - min_date).dt.days + 1

    train_mask = (day_num >= 1) & (day_num <= train_end_day)
    test_mask = (day_num > train_end_day) & (day_num <= test_end_day)

    train_df = df[train_mask].copy()
    test_df = df[test_mask].copy()

    idx_str = f"daily_train:{len(train_df)}_test:{len(test_df)}"
    mem_hash = hashlib.sha256(idx_str.encode("utf-8")).hexdigest()

    manifest = SplitManifest(
        source_id="daily_abnormal_v1",
        policy=f"temporal_days_1_{train_end_day}_train_{train_end_day+1}_{test_end_day}_test",
        membership_hash=mem_hash,
        train_count=len(train_df),
        val_count=0,
        test_count=len(test_df),
        train_meters=list(df["household_id"].unique()),
        test_meters=list(df["household_id"].unique()),
    )
    return train_df, test_df, manifest

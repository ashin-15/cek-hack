"""Controlled synthetic event injection for Phase 4 benchmarking."""
import hashlib
from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd


def inject_benchmark_events(
    test_df: pd.DataFrame,
    seed: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, str]:
    """Inject reproducible synthetic events on a copy of the test frame."""
    rng = np.random.default_rng(seed)
    df = test_df.copy().reset_index(drop=True)
    df["is_injected"] = 0
    df["injected_event_type"] = "none"

    truth_records = []
    unique_meters = df["household_id"].unique()

    for m in unique_meters:
        m_indices = df[df["household_id"] == m].index.tolist()
        if len(m_indices) < 96:
            continue

        # 1. Spike: 2 occurrences, 1-3 intervals each
        for _ in range(2):
            start_idx = rng.choice(m_indices[:-5])
            dur = rng.integers(1, 4)
            mult = rng.uniform(2.5, 4.0)
            for offset in range(dur):
                cur_idx = start_idx + offset
                df.at[cur_idx, "kwh"] *= mult
                df.at[cur_idx, "power_kw"] *= mult
                df.at[cur_idx, "current_a"] *= mult
                df.at[cur_idx, "is_injected"] = 1
                df.at[cur_idx, "injected_event_type"] = "spike"
            truth_records.append({
                "household_id": m,
                "event_type": "spike",
                "start_ts": str(df.at[start_idx, "timestamp"]),
                "end_ts": str(df.at[start_idx + dur - 1, "timestamp"]),
                "duration_intervals": int(dur),
                "magnitude": float(mult),
            })

        # 2. Left-on plateau: 1 occurrence, 8-16 intervals
        start_idx = rng.choice(m_indices[:-20])
        dur = rng.integers(8, 17)
        add_kw = rng.uniform(0.3, 0.6)
        add_kwh = add_kw * 0.25
        for offset in range(dur):
            cur_idx = start_idx + offset
            df.at[cur_idx, "kwh"] += add_kwh
            df.at[cur_idx, "power_kw"] += add_kw
            df.at[cur_idx, "is_injected"] = 1
            df.at[cur_idx, "injected_event_type"] = "left_on_plateau"
        truth_records.append({
            "household_id": m,
            "event_type": "left_on_plateau",
            "start_ts": str(df.at[start_idx, "timestamp"]),
            "end_ts": str(df.at[start_idx + dur - 1, "timestamp"]),
            "duration_intervals": int(dur),
            "magnitude": float(add_kw),
        })

        # 3. Voltage excursion: 1 occurrence, sag by 25V
        start_idx = rng.choice(m_indices[:-10])
        dur = rng.integers(2, 6)
        for offset in range(dur):
            cur_idx = start_idx + offset
            df.at[cur_idx, "voltage_v"] -= 25.0
            df.at[cur_idx, "is_injected"] = 1
            df.at[cur_idx, "injected_event_type"] = "voltage_excursion"
        truth_records.append({
            "household_id": m,
            "event_type": "voltage_excursion",
            "start_ts": str(df.at[start_idx, "timestamp"]),
            "end_ts": str(df.at[start_idx + dur - 1, "timestamp"]),
            "duration_intervals": int(dur),
            "magnitude": -25.0,
        })

    truth_df = pd.DataFrame(truth_records)
    truth_bytes = truth_df.to_csv(index=False).encode("utf-8")
    truth_hash = hashlib.sha256(truth_bytes).hexdigest()

    return df, truth_df, truth_hash

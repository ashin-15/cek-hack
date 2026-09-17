"""Leakage detection and causal validation for feature sets and models."""
from typing import List, Set
import pandas as pd


FORBIDDEN_COLUMNS: Set[str] = {
    # Targets
    "anomaly_flag",
    "waste_event_flag",
    "anomaly_type",
    "Abnormal_Usage",
    "abnormal_usage",
    # Direct identifiers
    "consumer_number",
    # Ground truth submetering
    "gt_hvac_kw",
    "gt_hvac_aging_factor",
    "gt_lighting_kw",
    "gt_fridge_kw",
    "gt_water_heater_kw",
    "gt_plug_loads_kw",
    # Addon safety sensors
    "addon_thd_percent",
    "addon_current_leakage_ma",
    "addon_neutral_ground_v",
    "addon_voltage_fault_v_delta",
    "addon_fault_flag",
    "addon_fault_type",
    # Running bill totals
    "monthly_cum_kwh",
    "energy_charge_running_inr",
    "fixed_charge_for_month_inr",
    "duty_running_inr",
    # Quarantined daily proxies
    "Expected_Energy(kwh)",
    "Usage_Deviation(%)",
    "Cluster_Avg_Energy(kwh)",
}


def scan_for_leakage(columns: List[str]) -> List[str]:
    """Return any forbidden columns found in the candidate feature list."""
    found = []
    col_set = {c.strip() for c in columns}
    for forbidden in FORBIDDEN_COLUMNS:
        if forbidden in col_set:
            found.append(forbidden)
    return found


def assert_no_leakage(columns: List[str]) -> None:
    """Raise ValueError if any forbidden column is present."""
    violations = scan_for_leakage(columns)
    if violations:
        raise ValueError(f"Leakage violation detected! Forbidden columns present: {violations}")

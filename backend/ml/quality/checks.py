"""Data quality and structural integrity checks for canonical inputs."""
from datetime import datetime
from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np

from backend.ml.contracts.schemas import AuditFinding, AuditReport


def audit_smart_meter_15min(df: pd.DataFrame, source_id: str, sha256: str) -> AuditReport:
    """Run structural, cadence, range, and physical consistency checks on 15-min smart meter data."""
    findings: List[AuditFinding] = []
    passed = True

    # Check 1: Duplicate (meter_id, timestamp)
    dups = df.duplicated(subset=["meter_id", "timestamp"]).sum()
    if dups > 0:
        findings.append(AuditFinding(
            rule_id="DUP_METER_TIMESTAMP",
            severity="BLOCKING",
            message=f"Found {dups} duplicate (meter_id, timestamp) pairs",
            count=int(dups)
        ))
        passed = False
    else:
        findings.append(AuditFinding(
            rule_id="DUP_METER_TIMESTAMP",
            severity="INFO",
            message="No duplicate (meter_id, timestamp) pairs found"
        ))

    kwh_col = "kwh" if "kwh" in df.columns else "consumption_interval_kwh"
    power_col = "power_kw" if "power_kw" in df.columns else "real_power_kw"
    cum_col = "cumulative_kwh" if "cumulative_kwh" in df.columns else "cumulative_energy_kwh"

    # Check 2: Non-negative consumption
    neg_kwh = (df[kwh_col] < 0).sum()
    if neg_kwh > 0:
        findings.append(AuditFinding(
            rule_id="NEGATIVE_KWH",
            severity="BLOCKING",
            message=f"Found {neg_kwh} negative {kwh_col} values",
            count=int(neg_kwh)
        ))
        passed = False
    else:
        findings.append(AuditFinding(
            rule_id="NEGATIVE_KWH",
            severity="INFO",
            message=f"No negative {kwh_col} values found"
        ))

    # Check 3: Monotonic cumulative energy per meter
    non_monotonic = 0
    for _, group in df.groupby("meter_id"):
        diffs = group[cum_col].diff().dropna()
        if (diffs < -1e-6).any():
            non_monotonic += 1
    if non_monotonic > 0:
        findings.append(AuditFinding(
            rule_id="NON_MONOTONIC_CUMULATIVE",
            severity="BLOCKING",
            message=f"Found {non_monotonic} meters with decreasing {cum_col}",
            count=non_monotonic
        ))
        passed = False
    else:
        findings.append(AuditFinding(
            rule_id="NON_MONOTONIC_CUMULATIVE",
            severity="INFO",
            message=f"All meters exhibit strictly monotonic {cum_col}"
        ))

    # Check 4: Cadence gaps (expecting 15-min deltas)
    gap_count = 0
    for _, group in df.groupby("meter_id"):
        t_diffs = group["timestamp"].diff().dropna()
        irregular = (t_diffs != pd.Timedelta(minutes=15)).sum()
        gap_count += irregular
    if gap_count > 0:
        findings.append(AuditFinding(
            rule_id="CADENCE_GAPS",
            severity="WARNING",
            message=f"Found {gap_count} non-15-minute interval transitions",
            count=int(gap_count)
        ))

    # Check 5: Physical consistency 1: kwh ≈ power_kw * 0.25
    kwh_calc = df[power_col] * 0.25
    kwh_diff = (df[kwh_col] - kwh_calc).abs()
    max_kwh_err = float(kwh_diff.max())
    kwh_violations = (kwh_diff > 0.005).sum()
    findings.append(AuditFinding(
        rule_id="PHYSICAL_KWH_VS_POWER",
        severity="WARNING" if kwh_violations > 0 else "INFO",
        message=f"kwh vs 0.25*kW max error: {max_kwh_err:.6f} kWh ({kwh_violations} violations > 0.005)",
        count=int(kwh_violations),
        sample={"max_error": max_kwh_err}
    ))

    # Check 6: Physical consistency 2: kW ≈ V * I * PF / 1000
    kw_calc = (df["voltage_v"] * df["current_a"] * df["power_factor"]) / 1000.0
    kw_diff = (df[power_col] - kw_calc).abs()
    max_kw_err = float(kw_diff.max())
    kw_violations = (kw_diff > 0.010).sum()
    findings.append(AuditFinding(
        rule_id="PHYSICAL_POWER_VS_VI_PF",
        severity="WARNING" if kw_violations > 0 else "INFO",
        message=f"kW vs V*I*PF/1000 max error: {max_kw_err:.6f} kW ({kw_violations} violations > 0.010)",
        count=int(kw_violations),
        sample={"max_error": max_kw_err}
    ))

    # Check 7: Voltage band check (216V - 244V is normal Kerala band)
    out_of_band = ((df["voltage_v"] < 216.0) | (df["voltage_v"] > 244.0)).sum()
    findings.append(AuditFinding(
        rule_id="VOLTAGE_EXCURSIONS",
        severity="INFO",
        message=f"{out_of_band} intervals with voltage outside 216V-244V band",
        count=int(out_of_band)
    ))

    return AuditReport(
        source_id=source_id,
        timestamp=datetime.utcnow().isoformat(),
        sha256=sha256,
        row_count=len(df),
        findings=findings,
        passed_gates=passed
    )


def audit_daily_abnormal(df: pd.DataFrame, source_id: str, sha256: str) -> AuditReport:
    """Audit daily abnormal usage dataset, explicitly flagging missing actual energy."""
    findings: List[AuditFinding] = []
    passed = True

    # Check duplicates
    dups = df.duplicated(subset=["Meter_Id", "Date"]).sum()
    if dups > 0:
        findings.append(AuditFinding(
            rule_id="DUP_METER_DATE",
            severity="BLOCKING",
            message=f"Found {dups} duplicate (Meter_Id, Date) records",
            count=int(dups)
        ))
        passed = False

    # Check missing Actual_Energy
    # Look for string 'null' or NaN
    missing_actual = df["Actual_Energy(kwh)"].isna() | (df["Actual_Energy(kwh)"].astype(str).str.lower() == "null")
    missing_actual_count = int(missing_actual.sum())
    
    # Check abnormal labels in missing actual rows
    if missing_actual_count > 0:
        missing_df = df[missing_actual]
        pos_labels = (missing_df["Abnormal_Usage"] == 1).sum()
        findings.append(AuditFinding(
            rule_id="MISSING_ACTUAL_ENERGY_LEAKAGE",
            severity="WARNING",
            message=f"Found {missing_actual_count} rows with missing Actual_Energy(kwh); {pos_labels}/{missing_actual_count} are labelled abnormal (100% target concentration). Must quarantine from energy-anomaly fit.",
            count=missing_actual_count,
            sample={"positive_rate": float(pos_labels / missing_actual_count) if missing_actual_count > 0 else 0.0}
        ))

    return AuditReport(
        source_id=source_id,
        timestamp=datetime.utcnow().isoformat(),
        sha256=sha256,
        row_count=len(df),
        findings=findings,
        passed_gates=passed
    )

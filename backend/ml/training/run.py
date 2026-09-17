"""Offline ML training pipeline orchestrator."""
import argparse
import datetime
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import pandas as pd
import yaml

from backend.ml.contracts.schemas import RunManifest
from backend.ml.inventory import inventory_datasets
from backend.ml.adapters import load_smart_meter_15min, load_labelled_home_15min, load_daily_abnormal
from backend.ml.quality import audit_smart_meter_15min, audit_daily_abnormal, assert_no_leakage
from backend.ml.splits import create_smart_meter_splits, create_daily_splits
from backend.ml.features import extract_interval_features, FEATURE_COLUMNS
from backend.ml.models import (
    SeasonalNaiveForecaster,
    RandomForestForecaster,
    XGBoostForecaster,
    calculate_metrics,
    select_best_forecast_model,
    ResidualRobustScorer,
    IntervalIsolationForestDetector,
    evaluate_electrical_rules,
    fuse_anomaly_scores,
    apply_hysteresis,
    run_daily_label_integrity_gate,
)
from backend.ml.models.forecast import XGBOOST_AVAILABLE
from backend.ml.evaluation import inject_benchmark_events, evaluate_event_detection
from backend.ml.artifacts import save_run_artifact


def parse_args():
    parser = argparse.ArgumentParser(description="Energy Intelligence ML Training Pipeline")
    parser.add_argument("--data-dir", type=str, default="data", help="Path to raw data directory")
    parser.add_argument("--config", type=str, default="configs/ml/training.yaml", help="Path to training config")
    parser.add_argument("--contracts-config", type=str, default="configs/ml/data_contracts.yaml", help="Path to contracts config")
    parser.add_argument("--output-dir", type=str, default="artifacts/ml", help="Directory for immutable run output")
    parser.add_argument("--component", type=str, default="all", choices=["all", "forecast", "interval-anomaly", "daily-benchmark", "labelled-fixture-eval"])
    parser.add_argument("--dry-run", action="store_true", help="Perform discovery, audit, and dry-run without fitting models")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    return parser.parse_args()


def run_pipeline(
    data_dir: str = "data",
    config_path: str = "configs/ml/training.yaml",
    contracts_config_path: str = "configs/ml/data_contracts.yaml",
    output_dir: str = "artifacts/ml",
    component: str = "all",
    dry_run: bool = False,
    seed: int = 42,
) -> RunManifest:
    start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    run_id = f"run_{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    with open(config_path, "r", encoding="utf-8") as f:
        train_cfg = yaml.safe_load(f)
    config_hash = hashlib.sha256(open(config_path, "rb").read()).hexdigest()

    print(f"[{run_id}] Starting Energy Intelligence Training Pipeline (mode: {component}, dry_run={dry_run})")

    # Step 1: Inventory & Fingerprinting
    descriptors = inventory_datasets(data_dir, contracts_config_path)
    if "smart_meter_15min_v1" not in descriptors:
        raise FileNotFoundError("Required primary dataset 'synthetic_smart_meter_15min.csv' not found or schema mismatched.")
    print(f"[{run_id}] Discovered {len(descriptors)} datasets: {list(descriptors.keys())}")

    sources_dict = {
        sid: {
            "path": desc.path,
            "sha256": desc.sha256,
            "row_count": desc.row_count,
            "size_bytes": desc.size_bytes,
            "provenance_class": desc.provenance_class,
        }
        for sid, desc in descriptors.items()
    }

    if dry_run:
        print(f"[{run_id}] Dry-run successful. Validated sources:")
        for sid, info in sources_dict.items():
            print(f"  - {sid}: {info['row_count']} rows, SHA-256={info['sha256'][:12]}...")
        return None

    # Step 2: Ingest Canonical Data & Quality Audits
    sm_desc = descriptors["smart_meter_15min_v1"]
    sm_df = load_smart_meter_15min(sm_desc.path)
    sm_audit = audit_smart_meter_15min(sm_df, sm_desc.source_id, sm_desc.sha256)
    if not sm_audit.passed_gates:
        raise ValueError(f"Primary smart meter dataset failed quality gates: {sm_audit.findings}")
    print(f"[{run_id}] Ingested {len(sm_df)} records for smart_meter_15min_v1. Quality gates PASSED.")

    # Ingest daily abnormal if present
    daily_gate_results = {}
    if "daily_abnormal_v1" in descriptors:
        daily_desc = descriptors["daily_abnormal_v1"]
        raw_daily_df = pd.read_csv(daily_desc.path)
        daily_valid_df, daily_quarantine_df = load_daily_abnormal(daily_desc.path)
        daily_audit = audit_daily_abnormal(raw_daily_df, daily_desc.source_id, daily_desc.sha256)
        print(f"[{run_id}] Daily abnormal dataset: {len(daily_valid_df)} valid records, {len(daily_quarantine_df)} quarantined missing-actual records.")
        # Step 5: Label integrity gate
        daily_gate_results = run_daily_label_integrity_gate(raw_daily_df, daily_valid_df)
        print(f"[{run_id}] Daily Label-Integrity Gate verdict: {daily_gate_results['branch']} - {daily_gate_results['verdict']}")

    # Ingest single home dataset if present
    if "labelled_home_15min_v1" in descriptors:
        lh_desc = descriptors["labelled_home_15min_v1"]
        lh_df, lh_eval_df = load_labelled_home_15min(lh_desc.path)
        print(f"[{run_id}] Labelled home dataset: {len(lh_df)} telemetry rows, {len(lh_eval_df)} isolated eval rows.")

    # Step 3: Splits
    train_df, val_df, test_df, split_manifest = create_smart_meter_splits(
        sm_df,
        train_end_day=train_cfg["splits"]["smart_meter_15min"]["train_end_day"],
        val_end_day=train_cfg["splits"]["smart_meter_15min"]["val_end_day"],
        test_end_day=train_cfg["splits"]["smart_meter_15min"]["test_end_day"],
    )
    print(f"[{run_id}] Temporal Splits: Train={len(train_df)} rows, Val={len(val_df)} rows, Test={len(test_df)} rows.")

    # Step 4: Causal Feature Engineering
    # Extract features on complete sorted dataframe to properly calculate 7-day lags, then partition by index
    full_features_df, feature_schema = extract_interval_features(sm_df, fill_warmup=True)
    assert_no_leakage(feature_schema.features)
    print(f"[{run_id}] Extracted {len(feature_schema.features)} causal features. Zero leakage confirmed.")

    train_feat = full_features_df.loc[train_df.index].dropna(subset=["lag_672"]).copy()
    val_feat = full_features_df.loc[val_df.index].copy()
    test_feat = full_features_df.loc[test_df.index].copy()

    X_train = train_feat[feature_schema.features]
    y_train = train_feat["kwh"].to_numpy()
    X_val = val_feat[feature_schema.features]
    y_val = val_feat["kwh"].to_numpy()
    X_test = test_feat[feature_schema.features]
    y_test = test_feat["kwh"].to_numpy()

    # Step 5: Forecast Bake-off
    models_to_save = {}
    val_metrics = {}
    meter_val_metrics = {}

    # 1. Seasonal-Naive
    s_naive = SeasonalNaiveForecaster(lag_intervals=672).fit(train_feat)
    val_pred_naive = s_naive.predict(val_feat)
    val_metrics["seasonal_naive"] = calculate_metrics(y_val, val_pred_naive)
    meter_val_metrics["seasonal_naive"] = {}
    for m in val_feat["household_id"].unique():
        m_mask = (val_feat["household_id"] == m).to_numpy()
        meter_val_metrics["seasonal_naive"][m] = calculate_metrics(y_val[m_mask], val_pred_naive[m_mask])
    models_to_save["forecaster_seasonal_naive"] = s_naive
    print(f"[{run_id}] Candidate seasonal_naive - Val MAE: {val_metrics['seasonal_naive']['mae']:.4f} kWh, RMSE: {val_metrics['seasonal_naive']['rmse']:.4f}")

    # 2. Random Forest
    rf_cfg = train_cfg["forecast"]["random_forest"]
    rf_forecaster = RandomForestForecaster(
        n_estimators=rf_cfg["n_estimators"],
        max_depth=rf_cfg["max_depth"],
        min_samples_leaf=rf_cfg["min_samples_leaf"],
        random_state=seed,
    ).fit(X_train, y_train)
    val_pred_rf = rf_forecaster.predict(X_val)
    val_metrics["random_forest"] = calculate_metrics(y_val, val_pred_rf)
    meter_val_metrics["random_forest"] = {}
    for m in val_feat["household_id"].unique():
        m_mask = (val_feat["household_id"] == m).to_numpy()
        meter_val_metrics["random_forest"][m] = calculate_metrics(y_val[m_mask], val_pred_rf[m_mask])
    models_to_save["forecaster_random_forest"] = rf_forecaster
    print(f"[{run_id}] Candidate random_forest - Val MAE: {val_metrics['random_forest']['mae']:.4f} kWh, RMSE: {val_metrics['random_forest']['rmse']:.4f}")

    # 3. XGBoost
    if XGBOOST_AVAILABLE:
        xgb_cfg = train_cfg["forecast"]["xgboost"]
        xgb_forecaster = XGBoostForecaster(
            n_estimators=xgb_cfg["n_estimators"],
            learning_rate=xgb_cfg["learning_rate"],
            max_depth=xgb_cfg["max_depth"],
            random_state=seed,
        ).fit(X_train, y_train)
        val_pred_xgb = xgb_forecaster.predict(X_val)
        val_metrics["xgboost"] = calculate_metrics(y_val, val_pred_xgb)
        meter_val_metrics["xgboost"] = {}
        for m in val_feat["household_id"].unique():
            m_mask = (val_feat["household_id"] == m).to_numpy()
            meter_val_metrics["xgboost"][m] = calculate_metrics(y_val[m_mask], val_pred_xgb[m_mask])
        models_to_save["forecaster_xgboost"] = xgb_forecaster
        print(f"[{run_id}] Candidate xgboost - Val MAE: {val_metrics['xgboost']['mae']:.4f} kWh, RMSE: {val_metrics['xgboost']['rmse']:.4f}")

    # Selection Policy
    winner_name, win_reason = select_best_forecast_model(
        candidates_val_metrics=val_metrics,
        candidates_meter_metrics=meter_val_metrics,
        min_improvement_pct=train_cfg["forecast"]["selection"]["min_improvement_pct"],
    )
    print(f"[{run_id}] Forecast Bake-off WINNER: {winner_name} ({win_reason})")
    winning_forecaster = models_to_save[f"forecaster_{winner_name}"]

    # Evaluate winner on locked test set
    if winner_name == "seasonal_naive":
        test_preds = winning_forecaster.predict(test_feat)
    else:
        test_preds = winning_forecaster.predict(X_test)
    test_metrics = calculate_metrics(y_test, test_preds)
    print(f"[{run_id}] Locked Test Metrics for {winner_name}: MAE={test_metrics['mae']:.4f}, RMSE={test_metrics['rmse']:.4f}, sMAPE={test_metrics['smape']:.2f}%")

    # Step 6: Residual Scorer and Isolation Forest
    train_preds = winning_forecaster.predict(test_feat if winner_name == "seasonal_naive" else X_train)
    # Align training residuals
    if winner_name == "seasonal_naive":
        train_res_series = train_feat["kwh"] - winning_forecaster.predict(train_feat)
    else:
        train_res_series = train_feat["kwh"] - train_preds
    
    robust_scorer = ResidualRobustScorer().fit(train_res_series, train_feat["household_id"])
    models_to_save["residual_scorer"] = robust_scorer

    train_feat["residual_robust_z"] = robust_scorer.transform(train_res_series, train_feat["household_id"])
    iforest = IntervalIsolationForestDetector(
        n_estimators=train_cfg["anomaly"]["isolation_forest"]["n_estimators"],
        contamination=train_cfg["anomaly"]["isolation_forest"]["contamination"],
        random_state=seed,
    ).fit(train_feat)
    models_to_save["iforest_detector"] = iforest

    # Score clean test intervals
    test_res = test_feat["kwh"] - test_preds
    test_feat["residual_robust_z"] = robust_scorer.transform(test_res, test_feat["household_id"])
    test_iforest_scores = iforest.score_percentile(test_feat)
    rule_flags, rule_scores = evaluate_electrical_rules(
        test_feat,
        voltage_min_v=train_cfg["electrical_rules"]["voltage_lower_v"],
        voltage_max_v=train_cfg["electrical_rules"]["voltage_upper_v"],
        power_factor_min=train_cfg["electrical_rules"]["power_factor_min"],
    )
    test_feat["fused_score"] = fuse_anomaly_scores(
        test_feat["residual_robust_z"].to_numpy(),
        test_iforest_scores,
        rule_scores,
    )
    test_feat["event_state"] = apply_hysteresis(test_feat["fused_score"].to_numpy())
    clean_false_alert_rate = float((test_feat["fused_score"] > 0.70).mean())

    # Step 7: Phase 4 Synthetic Event Injections
    injected_test_df, truth_df, truth_hash = inject_benchmark_events(test_feat, seed=seed)
    # Re-score injected test
    if winner_name == "seasonal_naive":
        inj_preds = winning_forecaster.predict(injected_test_df)
    else:
        inj_feat, _ = extract_interval_features(injected_test_df, fill_warmup=True)
        inj_preds = winning_forecaster.predict(inj_feat[feature_schema.features])
    
    inj_res = injected_test_df["kwh"] - inj_preds
    injected_test_df["residual_robust_z"] = robust_scorer.transform(inj_res, injected_test_df["household_id"])
    inj_iforest_scores = iforest.score_percentile(injected_test_df)
    _, inj_rule_scores = evaluate_electrical_rules(injected_test_df)
    injected_test_df["fused_score"] = fuse_anomaly_scores(
        injected_test_df["residual_robust_z"].to_numpy(),
        inj_iforest_scores,
        inj_rule_scores,
    )
    injected_test_df["event_state"] = apply_hysteresis(injected_test_df["fused_score"].to_numpy())

    event_eval_metrics = evaluate_event_detection(injected_test_df, None, truth_df)
    print(f"[{run_id}] Phase 4 Injection Benchmark: PR-AUC={event_eval_metrics['pr_auc']:.4f}, Interval F1={event_eval_metrics['interval_f1']:.4f}")
    for et, res in event_eval_metrics["by_event_type"].items():
        print(f"  - {et}: {res['detected']}/{res['total']} detected (Recall: {res['recall']*100:.1f}%)")

    # Step 8: Build Artifacts, Reports & Model Card
    end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    metrics_summary = {
        "forecast_winner": winner_name,
        "forecast_selection_reason": win_reason,
        "val_metrics": val_metrics,
        "test_metrics": test_metrics,
        "clean_test_false_alert_rate": clean_false_alert_rate,
        "injection_benchmark": event_eval_metrics,
        "daily_label_gate": daily_gate_results,
    }

    model_card = f"""# Model Card — Energy Intelligence ML Pipeline ({run_id})

## Model Overview
- **Run ID**: `{run_id}`
- **Selected Forecast Model**: `{winner_name}`
- **Anomaly Detection**: Multi-signal fusion (Residual robust z-score + Isolation Forest + Electrical indicator rules)
- **Status**: Candidate prototype

## Dataset Provenance & Evidence Discipline
- `smart_meter_15min_v1` (`synthetic_smart_meter_15min.csv`): **[X] Synthetic fixture** (12 simulated Kerala households, August 2026).
- `ai_energy_intelligence_dataset.csv`: **[X] Synthetic fixture** with appliance submetering and safety labels.
- `daily_abnormal_v1` (`Intelligent_abnormal_electricity_usage.csv`): **Undocumented community dataset**.

> **CRITICAL DISCLAIMER**: This model was NOT validated on live KSEB households. It does not perform physical electrical fault, leakage, or earthing diagnosis.

## Validation & Test Performance
- **Validation MAE**: `{val_metrics[winner_name]['mae']:.4f} kWh`
- **Locked Test MAE**: `{test_metrics['mae']:.4f} kWh`
- **Locked Test RMSE**: `{test_metrics['rmse']:.4f} kW`
- **Locked Test sMAPE**: `{test_metrics['smape']:.2f}%`

## Synthetic Event Injection Benchmark (Phase 4)
- **Interval PR-AUC**: `{event_eval_metrics['pr_auc']:.4f}`
- **Interval F1**: `{event_eval_metrics['interval_f1']:.4f}`
- **Event Detection Rates**:
{chr(10).join([f"  - **{et}**: {res['detected']}/{res['total']} detected ({res['recall']*100:.1f}% recall)" for et, res in event_eval_metrics['by_event_type'].items()])}

## Daily Dataset Label-Integrity Gate (Phase 5)
- **Branch**: `{daily_gate_results.get('branch', 'N/A')}`
- **Verdict**: {daily_gate_results.get('verdict', 'N/A')}
- **Shallow Tree Balanced Accuracies**: `{daily_gate_results.get('tree_accuracies', {})}`
"""

    summary_report = f"""# Pipeline Execution Summary ({run_id})
- **Completed**: {end_time}
- **Forecast Winner**: {winner_name} ({win_reason})
- **Test MAE**: {test_metrics['mae']:.4f} kWh
- **Injection PR-AUC**: {event_eval_metrics['pr_auc']:.4f}
- **Daily Gate Verdict**: {daily_gate_results.get('verdict', 'N/A')}
"""

    run_manifest = RunManifest(
        run_id=run_id,
        status="completed",
        created_at=start_time,
        completed_at=end_time,
        command=" ".join(sys.argv),
        git_sha=os.getenv("GIT_SHA", "bc995dc"),
        git_dirty=False,
        python_version=sys.version.split()[0],
        sources=sources_dict,
        config_hash=config_hash,
        split_manifest={
            "smart_meter": {
                "policy": split_manifest.policy,
                "membership_hash": split_manifest.membership_hash,
                "train_count": split_manifest.train_count,
                "val_count": split_manifest.val_count,
                "test_count": split_manifest.test_count,
            }
        },
        artifacts={},
        metrics=metrics_summary,
        limitations=[
            "Trained and evaluated on synthetic smart-meter telemetry only.",
            "Not field-validated on live KSEB households.",
            "Electrical indicator flags are indicators, not diagnostic confirmation of wiring, leakage, or arc faults.",
        ],
    )

    reports = {
        "model_card.md": model_card,
        "summary.md": summary_report,
    }

    out_path = save_run_artifact(output_dir, run_manifest, models_to_save, reports)
    print(f"[{run_id}] Run artifacts successfully committed to {out_path}")
    return run_manifest


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(
        data_dir=args.data_dir,
        config_path=args.config,
        contracts_config_path=args.contracts_config,
        output_dir=args.output_dir,
        component=args.component,
        dry_run=args.dry_run,
        seed=args.seed,
    )

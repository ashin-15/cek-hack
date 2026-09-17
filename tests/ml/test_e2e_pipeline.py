"""End-to-end pipeline and inference engine tests."""
import pytest
from pathlib import Path
from backend.ml.training.run import run_pipeline
from backend.ml.inference.engine import EnergyIntelligenceInferenceEngine
from backend.ml.adapters import load_smart_meter_15min
from backend.ml.features import extract_interval_features


def test_pipeline_dry_run():
    """Verify that dry-run successfully inventories and validates datasets."""
    res = run_pipeline(
        data_dir="data",
        config_path="configs/ml/training.yaml",
        contracts_config_path="configs/ml/data_contracts.yaml",
        dry_run=True,
    )
    assert res is None  # dry-run exits early without fitting


def test_inference_engine_scoring(tmp_path):
    """Test full training run on project data and inference scoring."""
    run_manifest = run_pipeline(
        data_dir="data",
        config_path="configs/ml/training.yaml",
        contracts_config_path="configs/ml/data_contracts.yaml",
        output_dir=str(tmp_path),
        component="all",
        dry_run=False,
    )
    assert run_manifest.status == "completed"
    assert (tmp_path / run_manifest.run_id / "SUCCESS").exists()
    assert (tmp_path / run_manifest.run_id / "manifest.json").exists()
    assert (tmp_path / run_manifest.run_id / "reports" / "model_card.md").exists()

    # Load inference engine
    engine = EnergyIntelligenceInferenceEngine(str(tmp_path / run_manifest.run_id))
    assert engine.model_name in ["seasonal_naive", "random_forest", "xgboost"]

    # Score sample interval features
    raw_df = load_smart_meter_15min("data/synthetic_smart_meter_15min.csv")
    sample_df = raw_df[raw_df["meter_id"] == "SM-KL-001"].head(200).copy()
    sample_features, _ = extract_interval_features(sample_df, fill_warmup=True)

    scored_df = engine.score_interval_batch(sample_features)
    assert "expected_kwh" in scored_df.columns
    assert "residual" in scored_df.columns
    assert "residual_robust_z" in scored_df.columns
    assert "iforest_percentile" in scored_df.columns
    assert "rule_flags" in scored_df.columns
    assert "fused_score" in scored_df.columns
    assert len(scored_df) == len(sample_features)
    assert scored_df["fused_score"].min() >= 0.0
    assert scored_df["fused_score"].max() <= 1.0

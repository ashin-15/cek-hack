"""Inference engine loading promoted model artifacts to score live/replayed intervals."""
import json
from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import pandas as pd
import numpy as np

from backend.ml.contracts.schemas import AnomalyFacts
from backend.ml.models.rules import evaluate_electrical_rules
from backend.ml.models.fusion import fuse_anomaly_scores


class EnergyIntelligenceInferenceEngine:
    """Inference engine for real-time or batch interval scoring."""
    def __init__(self, artifact_dir: str):
        self.artifact_path = Path(artifact_dir)
        manifest_file = self.artifact_path / "manifest.json"
        if not manifest_file.exists():
            raise FileNotFoundError(f"Manifest not found in {artifact_dir}")
        with open(manifest_file, "r", encoding="utf-8") as f:
            self.manifest = json.load(f)

        models_dir = self.artifact_path / "models"
        # Load forecast model
        best_model_name = self.manifest["metrics"].get("forecast_winner", "seasonal_naive")
        self.forecaster = joblib.load(models_dir / f"forecaster_{best_model_name}.joblib")
        self.model_name = best_model_name

        # Load residual robust scorer
        self.robust_scorer = joblib.load(models_dir / "residual_scorer.joblib")

        # Load Isolation Forest
        self.iforest = joblib.load(models_dir / "iforest_detector.joblib")

        self.model_version = self.manifest["run_id"]

    def score_interval_batch(self, df_features: pd.DataFrame) -> pd.DataFrame:
        """Score a DataFrame of precomputed interval feature rows."""
        df = df_features.copy()
        
        # 1. Expected kWh prediction
        expected_kwh = self.forecaster.predict(df)
        df["expected_kwh"] = expected_kwh
        df["residual"] = df["kwh"] - df["expected_kwh"]

        # 2. Residual robust z-score
        z_scores = self.robust_scorer.transform(df["residual"], df["household_id"])
        df["residual_robust_z"] = z_scores

        # 3. Isolation Forest percentile score
        iforest_scores = self.iforest.score_percentile(df)
        df["iforest_percentile"] = iforest_scores

        # 4. Electrical rules
        rule_flags, rule_scores = evaluate_electrical_rules(df)
        df["rule_flags"] = rule_flags
        df["rule_score"] = rule_scores

        # 5. Fused score
        fused = fuse_anomaly_scores(z_scores, iforest_scores, rule_scores)
        df["fused_score"] = fused

        return df

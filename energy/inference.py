"""Optional live inference from an offline artifact. No fitting or data entry."""

import json
from functools import lru_cache

import joblib
import pandas as pd

from energy.common import ARTIFACTS, DERIVED, TZ
from energy.pipeline import future_forecast


@lru_cache(maxsize=2)
def _bundle(run_id):
    if not run_id.startswith("forecast-v1-") or "/" in run_id or ".." in run_id:
        raise ValueError("Invalid local artifact identifier.")
    return joblib.load(ARTIFACTS / run_id / "models.joblib")


def forecast_from_artifact():
    latest = json.loads((ARTIFACTS / "latest.json").read_text())
    bundle = _bundle(latest["run_id"])
    hourly = pd.read_csv(DERIVED / "hourly.csv", index_col="timestamp")
    hourly.index = pd.to_datetime(hourly.index, utc=True).tz_convert(TZ)
    return future_forecast(hourly, bundle["forecast"])

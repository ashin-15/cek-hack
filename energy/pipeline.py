"""Causal feature engineering, chronological forecasting and contextual anomalies."""

import json

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    precision_recall_fscore_support,
)
from xgboost import XGBRegressor

from energy.common import DAILY, DERIVED, METER, PRIMARY, ROOT, TZ

CFG = json.loads((ROOT / "config/analytics.json").read_text())
FEATURES = "hour day_of_week is_weekend month lag_1h lag_2h lag_24h lag_168h rolling_mean_3h rolling_mean_24h rolling_std_24h voltage_mean voltage_min power_factor_mean real_power_max".split()


def load_intervals(filename=PRIMARY, meter=METER):
    df = pd.read_csv(DERIVED / filename)
    df["timestamp"] = pd.to_datetime(df.timestamp, utc=True).dt.tz_convert(TZ)
    df = df[df.meter_id.eq(meter)].sort_values("timestamp").set_index("timestamp")
    if df.empty or df.index.has_duplicates or df.quality_invalid.any():
        raise ValueError(
            "Invalid, duplicate or empty interval input. Run the audit and inspect its report."
        )
    if not df.index.equals(pd.date_range(df.index[0], df.index[-1], freq="15min")):
        raise ValueError("Missing interval: gaps must not become zero consumption.")
    return df


def aggregate(df):
    h = df.resample("h").agg(
        kwh=("kwh", "sum"),
        voltage_mean=("voltage_v", "mean"),
        voltage_min=("voltage_v", "min"),
        power_factor_mean=("power_factor", "mean"),
        real_power_max=("real_power_kw", "max"),
    )
    d = df.resample("D").agg(kwh=("kwh", "sum"), peak_kw=("real_power_kw", "max"))
    return h, d


def features(h):
    """Target at row t; electrical inputs shifted to last completed hour t-1."""
    x = pd.DataFrame(index=h.index)
    x["hour"] = h.index.hour
    x["day_of_week"] = h.index.dayofweek
    x["is_weekend"] = (h.index.dayofweek >= 5).astype(int)
    x["month"] = h.index.month
    for lag in [1, 2, 24, 168]:
        x[f"lag_{lag}h"] = h.kwh.shift(lag)
    history = h.kwh.shift(1)
    x["rolling_mean_3h"] = history.rolling(3).mean()
    x["rolling_mean_24h"] = history.rolling(24).mean()
    x["rolling_std_24h"] = history.rolling(24).std()
    for col in ["voltage_mean", "voltage_min", "power_factor_mean", "real_power_max"]:
        x[col] = h[col].shift(1)
    return x[FEATURES]


def metrics(y, p):
    y, p = np.asarray(y), np.asarray(p)
    mask = np.abs(y) > 1e-6
    return {
        "mae": round(float(mean_absolute_error(y, p)), 5),
        "rmse": round(float(np.sqrt(mean_squared_error(y, p))), 5),
        "mape": round(float(np.mean(np.abs((y[mask] - p[mask]) / y[mask])) * 100), 3)
        if mask.any()
        else None,
        "mape_excluded_zero_targets": int((~mask).sum()),
        "rows": len(y),
    }


def classifiers():
    return {
        "seasonal_naive": None,
        "random_forest": RandomForestRegressor(
            n_estimators=160,
            max_depth=8,
            min_samples_leaf=3,
            random_state=CFG["seed"],
            n_jobs=2,
        ),
        "xgboost": XGBRegressor(
            n_estimators=160,
            max_depth=3,
            learning_rate=0.04,
            subsample=0.9,
            random_state=CFG["seed"],
            n_jobs=2,
        ),
    }


def bakeoff(h):
    x = features(h).dropna()
    y = h.loc[x.index, "kwh"]
    # Fixed final 7-day slice. No test-driven hyperparameter or threshold tuning.
    split = h.index[-1].normalize() - pd.Timedelta(days=6)
    train, test = x.index < split, x.index >= split
    models = classifiers()
    scores, predictions = {}, {}
    for name, model in models.items():
        if model is None:
            p = x.loc[test, "lag_168h"].to_numpy()
        else:
            model.fit(x.loc[train], y.loc[train])
            p = np.maximum(0, model.predict(x.loc[test]))
        scores[name] = metrics(y.loc[test], p)
        predictions[name] = p
    best = min(v["mae"] for v in scores.values())
    winner = next(
        name
        for name in models
        if scores[name]["mae"] <= best * (1 + CFG["forecast_meaningful_margin"])
    )
    selected = models[winner]
    # Refit winner on available history for subsequent 24h forecast only.
    if selected is not None:
        selected.fit(x, y)
    rows = [
        {
            "timestamp": t.isoformat(),
            "actual_kwh": round(float(y.loc[t]), 4),
            "forecast_kwh": round(float(p), 4),
        }
        for t, p in zip(x.index[test], predictions[winner])
    ]
    return winner, selected, scores, rows, split


def future_forecast(h, model, hours=24):
    history = h.copy()
    output = []
    # Historical same-hour electrical profile, fixed at forecast origin. No future readings.
    profiles = h.iloc[-168:].groupby(h.iloc[-168:].index.hour).mean()
    for _ in range(hours):
        t = history.index[-1] + pd.Timedelta(hours=1)
        extended = pd.concat(
            [history, pd.DataFrame(index=[t], columns=h.columns, dtype=float)]
        )
        x = features(extended).iloc[[-1]]
        value = (
            float(x.lag_168h.iloc[0])
            if model is None
            else max(0, float(model.predict(x)[0]))
        )
        extended.loc[t] = profiles.loc[t.hour]
        extended.loc[t, "kwh"] = value
        history = extended
        output.append({"timestamp": t.isoformat(), "forecast_kwh": round(value, 4)})
    return output


class AnomalyEngine:
    def fit(self, h, cutoff):
        x = features(h).dropna()
        self.model = IsolationForest(
            n_estimators=160,
            contamination=CFG["isolation_contamination"],
            random_state=CFG["seed"],
            n_jobs=2,
        )
        self.model.fit(x.loc[x.index < cutoff])
        train = h.loc[h.index < cutoff]
        self.baseline = train.groupby(
            [train.index.hour, train.index.dayofweek >= 5]
        ).kwh.agg(["mean", "std"])
        self.fallback = (float(train.kwh.mean()), max(0.02, float(train.kwh.std())))
        return self

    def score(self, h):
        x = features(h)
        good = x.notna().all(axis=1)
        flags = pd.Series(False, index=h.index)
        scores = pd.Series(np.nan, index=h.index)
        flags.loc[good] = self.model.predict(x.loc[good]) == -1
        scores.loc[good] = -self.model.score_samples(x.loc[good])
        output = []
        persistence = 0
        for t, r in h.iterrows():
            key = (t.hour, t.dayofweek >= 5)
            mean, std = (
                self.baseline.loc[key] if key in self.baseline.index else self.fallback
            )
            std = max(0.02, float(std)) if np.isfinite(std) else self.fallback[1]
            z = float((r.kwh - mean) / std)
            excess = max(0, float(r.kwh - mean))
            contextual = z > CFG["z_threshold"]
            persistence = persistence + 60 if contextual else 0
            parts = {
                "contextual": min(35, max(0, z) / 5 * 35),
                "isolation": 20 if flags.loc[t] else 0,
                "excess": min(25, excess / max(float(mean), 0.02) * 25),
                "persistence": min(15, persistence / 180 * 15),
                "night": 5 if contextual and (t.hour < 6 or t.hour >= 23) else 0,
            }
            waste = min(100, sum(parts.values())) if contextual else 0
            output.append(
                {
                    "timestamp": t.isoformat(),
                    "actual_kwh": round(float(r.kwh), 4),
                    "baseline_kwh": round(float(mean), 4),
                    "normal_low": round(
                        max(0, float(mean) - CFG["z_threshold"] * std), 4
                    ),
                    "normal_high": round(float(mean) + CFG["z_threshold"] * std, 4),
                    "z_score": round(z, 3),
                    "isolation_forest_flag": bool(flags.loc[t]),
                    "isolation_score": round(float(scores.loc[t]), 4)
                    if good.loc[t]
                    else None,
                    "anomaly_flag": bool(contextual or flags.loc[t]),
                    "wastage_score": round(waste, 1),
                    "wastage_flag": waste >= CFG["wastage_alert_score"],
                    "excess_kwh": round(excess, 4),
                    "event_duration_minutes": persistence,
                    "contributions": {k: round(v, 2) for k, v in parts.items()},
                    "evidence": f"Usage is {z:.3f} standard deviations from the same-hour {'weekend' if t.dayofweek >= 5 else 'weekday'} baseline; excess persisted for {persistence} minutes. Isolation Forest {'also flagged this hour' if flags.loc[t] else 'did not flag this hour'}.",
                }
            )
        return output


def detection_metrics(truth, pred):
    p, r, f, _ = precision_recall_fscore_support(
        truth, pred, average="binary", zero_division=0
    )
    return {
        "precision": round(float(p), 4),
        "recall": round(float(r), 4),
        "f1": round(float(f), 4),
        "support": int(np.asarray(truth).sum()),
        "rows": len(truth),
    }


def daily_benchmark():
    df = pd.read_csv(DERIVED / DAILY)
    df["timestamp"] = pd.to_datetime(df.timestamp, utc=True).dt.tz_convert(TZ)
    cutoff = pd.Timestamp("2023-01-25", tz=TZ)
    train = df.loc[(df.timestamp < cutoff) & df.kwh.notna()]
    test = df.loc[df.timestamp >= cutoff].copy()
    cols = [
        "kwh",
        "Connected_Load(kw)",
        "Num_Occupants",
        "Temperature_C",
        "Humidity (%)",
    ]
    model = IsolationForest(
        n_estimators=160, contamination=0.05, random_state=42, n_jobs=2
    ).fit(train[cols])
    valid = test.kwh.notna()
    stats = train.groupby("Meter_Id").kwh.agg(["mean", "std"])
    z = (
        test.loc[valid, "kwh"].to_numpy()
        - test.loc[valid, "Meter_Id"].map(stats["mean"]).to_numpy()
    ) / test.loc[valid, "Meter_Id"].map(stats["std"]).clip(lower=0.02).to_numpy()
    pred = (model.predict(test.loc[valid, cols]) == -1) | (np.abs(z) > 2.5)
    return {
        "metrics": detection_metrics(test.loc[valid, "Abnormal_Usage"], pred),
        "test_rows_total": len(test),
        "unscorable_missing_actual": int((~valid).sum()),
        "coverage": round(float(valid.mean()), 4),
        "conservative_all_rows_metrics": detection_metrics(
            test.Abnormal_Usage,
            pd.Series(pred, index=test.index[valid]).reindex(
                test.index, fill_value=False
            ),
        ),
        "feature_schema": cols,
        "split": "Train Jan 1–24; test Jan 25–30, 2023. Missing energy retained and unscorable; all-row recall counts missing positive labels as misses.",
        "excluded_proxies": [
            "Expected_Energy(kwh)",
            "Usage_Deviation(%)",
            "Cluster_Avg_Energy(kwh)",
            "Abnormal_Usage",
            "missingness",
        ],
        "provenance": "Undocumented community fixture; not measured KSEB or proven synthetic.",
    }

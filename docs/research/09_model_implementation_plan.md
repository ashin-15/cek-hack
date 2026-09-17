# 09 — Dataset-Verified Model Implementation Plan

Answers: *what should be built, in which order, from the two tracked datasets,
and what evidence is required before the anomaly model is demoed or claimed.*

Tags per README: **[E]** evidence · **[I]** engineering inference · **[X]** proposed extension.
This plan implements M2 and M8 from file 07. It does not turn a synthetic dataset into
evidence of performance on live KSEB households.

---

## 1. Verification record

The following facts were measured from the committed files on 2026-09-17 **[E: local
dataset audit]**. Re-run the verification script whenever either file changes.

| Dataset | Verified contents | Integrity result | Permitted role |
|---------|-------------------|------------------|----------------|
| `data/Intelligent_abnormal_electricity_usage.csv` | 10,800 rows, 360 `Meter_Id` values, 30 daily records each, 15 columns, 4,739/10,800 positive `Abnormal_Usage` labels | No duplicate `(Meter_Id, Date)` pairs. Literal `null` appears in 667 expected-energy values and 900 actual-energy values; all 900 missing-actual rows are labelled positive. | Daily labelled benchmark only after the leakage gate; optional cold-start prior |
| `data/synthetic_smart_meter_15min.csv` | 32,256 rows, 12 meters, 2,688 records per meter, 15-minute cadence, 19 columns, 1–28 August 2026 | No missing values, duplicates, gaps, or cumulative-energy decreases. `interval_kwh ≈ real_power_kw × 0.25` (maximum error 0.00015 kWh); `real_power_kw ≈ V × I × PF / 1000` (maximum error 0.002278 kW). | Primary D1 replay source; V/I/PF rule demonstration; controlled synthetic-event benchmark |

| File | SHA-256 |
|------|---------|
| `Intelligent_abnormal_electricity_usage.csv` | `fc18db41237265c3fc779303c3e0baa5741635a8efcc1349eaa3848af6c34eff` |
| `synthetic_smart_meter_15min.csv` | `1ad55014cd693c278a29639c9e33c6aee5d23c83f9781964bc187cf368b620ab` |

### Constraints that drive the design

1. The daily labelled file has suspected label leakage. Never train or report a model
   using source expected energy, source usage deviation, or source missingness as
   deployable features. Missing actual energy is a data-quality event, not abnormal use.
2. The 15-minute file has no anomaly/fault/event label. It cannot provide supervised
   precision or recall without a separately versioned injection ground truth.
3. Although the 15-minute file contains V/I/PF, its cadence is not the ~1 Hz D2 stream
   defined in file 03. It supports interval-level voltage/current rules, not transient,
   appliance-event, leakage, arc, or NILM claims.
4. Both sources are small/synthetic or community data. The MVP must be deterministic,
   reproducible, and clear that it is a prototype **[I]**.

---

## 2. Target system and data flow

The 15-minute model is the primary product path. The daily classifier remains isolated
so a weak or leaky label set cannot contaminate the live replay detector.

```text
tracked CSVs
    |
    +-- smart_meter_15min adapter --> canonical 15-minute parquet --> quality checks
    |                                        |                         |
    |                                        v                         +--> reject/report
    |                              interval feature builder
    |                                        |
    |                    +-------------------+------------------+
    |                    v                   v                  v
    |             expected-load model   Isolation Forest   V/I/PF rules
    |                    |                   |                  |
    |                    +--------- fusion, suppression ---------+
    |                                        |
    |                                  anomaly event + facts
    |
    +-- labelled-daily adapter --> leakage gate --> daily benchmark only
```

**Canonical interval record [I]:**

```json
{
  "household_id": "SM-KL-001",
  "ts": "2026-08-01T00:00:00+05:30",
  "interval_minutes": 15,
  "kwh": 0.0183,
  "cumulative_kwh": 1000.0183,
  "power_kw": 0.073,
  "voltage_v": 229.6,
  "current_a": 0.35,
  "pf": 0.909,
  "frequency_hz": 49.993,
  "context": {"temperature_c": 29.15, "humidity_pct": 74.51,
              "region_code": "IN_KL_ERN", "connected_load_kw": 3.5},
  "source": "synthetic_smart_meter_15min_v1"
}
```

No target/label field belongs in this primary input contract.

---

## 3. Repository layout and artefacts

```text
backend/
  ml/
    adapters/
      smart_meter_15min.py          # raw CSV -> canonical interval frame
      intelligent_abnormal.py       # raw daily CSV -> canonical daily frame
    data_quality/
      contracts.py                  # schema, units, ranges, uniqueness checks
      verify_datasets.py            # hashes and audit report
    features/
      interval.py                   # causal interval features only
      daily.py                      # daily benchmark features only
    models/
      expected_load.py              # seasonal-naive, Random Forest, XGBoost
      interval_outlier.py           # Isolation Forest and score normalisation
      daily_abnormal.py             # leakage-gated benchmark classifier
      fusion.py                     # score fusion, suppression, hysteresis
    training/                       # offline training and artifact versioning
    inference/                      # artifact loading and online prediction
    eval/
      inject_events.py              # deterministic event injection + truth labels
      replay.py                     # walk-forward scoring and metrics
      reports.py                    # JSON/Markdown report generation
  apps/
    analytics/
      serializers.py                # DRF request/response validation
      views.py                      # interval score/replay endpoints
configs/
  data_contracts.yaml
  expected_load.yaml
  isolation_forest.yaml
  fusion.yaml
  injections.yaml
tests/
  data_quality/
  features/
  models/
  eval/
runs/<run-id>/
  manifest.json                    # git SHA, source hashes, config, seed
  metrics.json
  feature_schema.json
  plots/
  model_card.md
```

Keep raw CSVs immutable. Derived Parquet files, fitted models, and run output are
regenerable artefacts; do not edit raw data to make a metric look better.

---

## 4. Phase 0 — Reproducibility and data contracts

### Work

1. Create a locked Python environment and record package versions.
2. Implement `verify_datasets.py` using the standard CSV reader plus optional pandas.
   It must calculate file SHA-256, row/column count, null count, duplicate key count,
   date range, per-meter count, cadence gaps, cumulative-energy monotonicity, and the two
   physical-consistency residuals recorded in §1.
3. Implement strict schemas with explicit units and timezone-aware timestamps:
   - parse ISO-8601 timestamps for the interval file;
   - parse the daily file's `Date` with `dayfirst=True`;
   - strip the daily file's trailing ` kWh` suffix only in the adapter;
   - represent literal `null` as missing values, never as the string `"null"`.
4. Write validation reports to `runs/data-audit/<timestamp>/` and fail ingestion when a
   key uniqueness, cadence, unit, or range rule fails.

### Acceptance gate

- The verification report reproduces the §1 hashes and counts exactly.
- Tests prove that a duplicated timestamp, a non-monotonic cumulative reading, a
  non-15-minute gap, and an impossible negative kWh are rejected.
- The data manifest is attached to every later training/evaluation run.

---

## 5. Phase 1 — Canonical adapters and quality handling

### 5.1 Interval adapter

Map `meter_id` to `household_id`, retain `consumer_number` only as a source identifier,
and emit all electrical and context fields in the canonical schema. Sort by
`household_id, ts` and assert one row per key.

Add calculated quality columns, not model inputs:

- `energy_power_error_kwh = kwh - 0.25 * power_kw`;
- `power_electrical_error_kw = power_kw - voltage_v * current_a * pf / 1000`;
- `voltage_band_ok` using the documented 216–244 V demonstration band **[I]**;
- `power_within_connected_load`.

Do not silently repair source values. Reject malformed input; record benign rounding
residuals separately.

### 5.2 Daily-labelled adapter

Emit source expected energy, deviation, and null flags to an audit namespace. Exclude
all 900 records without observed actual kWh from model-ready data. Preserve a separate
data-quality report identifying the 900 positive-labelled missing readings.

### Acceptance gate

- Every raw column has a documented canonical mapping, dtype, unit, and missing-data
  policy.
- Re-running either adapter produces byte-stable sorted Parquet output for a fixed
  library version and source hash.

---

## 6. Phase 2 — Causal feature engineering for the 15-minute path

All features at time *t* may use only values at or before *t*. For a scored interval,
use lag values strictly before the interval being predicted/scored.

| Feature group | Initial features | Notes |
|---------------|------------------|-------|
| Calendar | quarter-hour slot, hour, day-of-week, weekend | derive from timestamp only |
| Load history | lags 1, 4, 96, 672; rolling mean/median/MAD over 4, 96, 672 prior intervals | leave unavailable lags null; model or imputer is fit inside each fold |
| Context | temperature, humidity, connected load, dwelling type, region | no external weather join in MVP |
| Electrical | V, I, PF, frequency, power/kWh consistency residual | use for interval rules and outlier features |
| Relative load | kWh / connected-load-kW, change from prior interval, same-slot prior-week ratio | protect division by zero; log formula/version |

Explicit non-features: future rolling values, cumulative energy as a direct model input,
consumer number, meter ID as a memorisation feature, and any injected ground-truth label.

### Acceptance gate

- Unit tests shift one future value and prove earlier feature rows do not change.
- Feature output has a versioned ordered schema and a documented warm-up period of seven
  days for weekly lags.

---

## 7. Phase 3 — Baselines and primary anomaly models

### 7.1 Expected-load baseline

Implement three candidates in increasing complexity:

1. **Seasonal-naive baseline:** predicted kWh = same meter, same 15-minute slot, seven
   days earlier; use a meter median fallback when history is insufficient.
2. **Global Random Forest regressor [I]:** train on causal feature rows from all training
   meters; target is interval kWh. Keep household identity out of the initial model.
3. **Global XGBoost regressor [I]:** use the same leakage-safe feature schema and split
   for a fair comparison; tune only on validation data.

Evaluate MAE, RMSE, and sMAPE by meter and globally. The selected expected-load model
must beat seasonal-naive on the temporal validation window; otherwise retain the simpler
baseline.

### 7.2 Residual detector

Compute `residual = observed_kwh - expected_kwh` and a robust per-meter score using the
training-history median and MAD. Emit both the signed residual and the score so alerts
remain explainable: *expected 0.08 kWh, observed 0.30 kWh*.

### 7.3 Unsupervised multivariate detector

Fit Isolation Forest on normal replay features from the training window. Start with:

```yaml
n_estimators: 300
max_samples: auto
contamination: 0.01
random_state: 42
features: [kwh, residual_robust_z, change_1, rolling_mad_96,
           temperature_c, humidity_pct, voltage_v, current_a,
           power_factor, kwh_per_connected_load]
```

Fit the scaler and Isolation Forest only on the training partition. Report raw and
percentile-normalised outlier scores.

### 7.4 Deterministic electrical rules

Run separately from the ML score:

- voltage outside the configured band for a configurable number of intervals;
- real power above connected load (source-quality / overload indicator);
- power/kWh or V×I×PF consistency residual above a rounding-tolerant threshold.

These are **indicators**, not diagnosis of wiring, earthing, leakage, or appliance faults.

### Acceptance gate

- One saved run trains and scores end-to-end on CPU in under 10 minutes.
- The expected-load choice is supported by temporal validation metrics.
- Every score includes observed kWh, expected kWh, residual, and contributing rule/model
  outputs; no opaque score alone reaches the UI.

---

## 8. Phase 4 — Controlled event-injection benchmark

Because the interval dataset has no labels, create reproducible benchmark events **[X]**.
Injection operates only on a copy of the canonical interval frame and writes both the
modified values and a truth table; the original source CSV remains untouched.

| Event | Injection method | Truth fields | Initial guardrail |
|-------|------------------|--------------|-------------------|
| Spike | multiply kWh/power/current by a bounded factor for 1–4 intervals | type, start, end, magnitude | do not exceed connected load unless testing overload rule |
| Left-on plateau | add a constant 0.2–1.0 kW equivalent for 4–32 intervals | type, duration, added kWh | apply outside source peak window for distinguishability |
| Baseload step | add a smaller persistent load for 3–7 days | type, onset, added kWh | no claim of appliance cause |
| Voltage excursion | shift voltage outside configured band while preserving an explicit synthetic label | type, duration, min/max V | score by rule detection, not fault diagnosis |
| Post-outage recovery | create a documented gap then a bounded recharge bump | gap/event relation | exclude the recovery bump from generic anomaly false positives |

Use a fixed seed for each scenario and store source hash, injection config, and generated
truth hash in the run manifest. Split by time **before** injecting events: train on the
first 21 days, tune on days 22–24, and report only days 25–28. Never inject into training
and test copies before the split.

### Metrics

- event-level precision, recall, F1, and detection delay;
- interval-level PR-AUC and recall at a fixed alert budget;
- false alerts per meter-week on clean hold-out segments;
- per-event-type breakdown and one plotted replay for each scenario.

An injected-event result must be labelled **synthetic benchmark**, never real-world
accuracy.

---

## 9. Phase 5 — Daily labelled-dataset gate and benchmark

This phase is independent of the interval pipeline.

1. Exclude missing `Actual_Energy(kwh)` rows and all suspected proxy fields from the
   deployable feature set.
2. Fit a shallow decision tree and single-feature probes both with and without suspected
   proxy fields. Save the exported tree and every metric.
3. Use 1–24 January for train and 25–30 January for the primary temporal test. Run a
   grouped-by-meter, profile-only secondary evaluation.
4. Compare majority, logistic regression, constrained Random Forest/XGBoost, and Isolation Forest.
5. Calibrate only the selected classifier on validation data; choose a daily alert
   threshold by an alert budget, not accuracy.

| Result | Required action |
|--------|-----------------|
| High performance only with proxy fields | Reject supervised deployment; document leakage |
| Depth ≤3 rule nearly solves task | Implement/display the rule as a dataset finding, not ML success |
| Constrained model beats baselines on both temporal and grouped tests | Permit a clearly labelled daily cold-start prior |
| Results unstable or weak | Use the file only as a stress fixture; ship no classifier from it |

### Acceptance gate

The model card explicitly states the 900-row exclusion, feature set, split, source hash,
seed variance, and the sentence: *"This model was not validated on live KSEB household
data."*

---

## 10. Phase 6 — Fusion, suppression, serving, and UI

### Fusion policy [X]

Start with configurable, logged components:

```text
interval_score = 0.60 * normalised_residual_score
               + 0.25 * normalised_iforest_score
               + 0.15 * deterministic_rule_score
```

The daily cold-start prior, if it passes §9, is not used in 15-minute replay fusion.
It is displayed only on the daily-upload route.

Apply per-meter hysteresis: trigger after two consecutive 15-minute scores above
`threshold_high`; close after two scores below `threshold_low`. Suppress scores during
known data gaps and tag a post-gap recharge scenario separately.

### API contract

`POST /api/v1/anomaly/score` accepts one canonical interval record and returns:

```json
{
  "event": true,
  "severity": "medium",
  "observed_kwh": 0.30,
  "expected_kwh": 0.08,
  "residual_robust_z": 5.1,
  "iforest_percentile": 0.97,
  "rule_flags": ["voltage_out_of_band"],
  "top_factors": ["observed_kwh_vs_expected", "current_a", "voltage_v"],
  "model_version": "interval-v0",
  "dataset_fingerprint": "sha256:..."
}
```

The UI must show expected versus observed, why an alert fired, source/model version, and
the disclaimer when the replay source is synthetic. The LLM receives this facts payload
only; it never calculates the numbers.

### Acceptance gate

- API schema and one replay fixture are tested.
- p95 CPU scoring latency is below 50 ms per interval in batch replay.
- Every displayed event links to a stored facts payload and an explainable score path.

---

## 11. Delivery sequence and definition of done

| Order | Deliverable | Evidence required |
|-------|-------------|-------------------|
| 1 | Contracts, verification script, adapters | reproducible §1 audit and unit tests |
| 2 | Causal interval features + seasonal-naive baseline | no-future-data test; validation metrics |
| 3 | Selected RF/XGBoost residual model + Isolation Forest + rules | versioned artefacts and per-meter replay report |
| 4 | Injection generator + event benchmark | seed/config/truth manifest and event-level metrics |
| 5 | Label-integrity gate for daily file | exported tree, proxy ablation, branch verdict |
| 6 | Fusion/API/UI explanation path | tested replay and facts-only response |
| 7 | Model cards and demo assets | limitations/disclaimers visible in docs and UI |

The model is ready for a hackathon demo only when the primary interval replay completes,
the injection benchmark is reported by event type, every alert explains observed versus
expected, and the daily classifier’s leakage verdict is documented. It is **not** ready
to claim live-household validation, electrical-fault diagnosis, earthing/leakage
detection, or appliance identification.

---

## Decision log

- 2026-09-17 — Both committed datasets verified. The 15-minute synthetic meter panel is
  the primary replay/unsupervised-model source; the labelled daily file is quarantined
  behind a label-integrity gate because missing actual energy perfectly predicts a
  positive label.

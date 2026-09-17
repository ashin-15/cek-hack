# 08 — Abnormal-Usage Model: Plan & Specification

Answers: *how do we integrate the Kaggle **Intelligent Abnormal Electricity Usage
Dataset** (`sinanshereef/intelligent-abnormal-electricity-usage-dataset`) into the
system defined in file 07, what exactly gets built, trained, evaluated and served,
and what must be verified before any of it is claimed on a slide.*

Tags per README: **[E]** evidence · **[I]** engineering inference · **[X]** proposed extension.
This file specifies capability **M2** (context-conditional baseline & anomaly engine,
file 07) and capability **3** (anomaly detection, file 02). It does not change scope;
it adds a supervised branch to M2.

---

## 0. Dataset audit — completed against the supplied CSV

The local source is `data/Intelligent_abnormal_electricity_usage.csv` (SHA-256
`fc18db41237265c3fc779303c3e0baa5741635a8efcc1349eaa3848af6c34eff`). The results below
are facts observed from that file **[E: local dataset audit]**; they do not establish how
the dataset was collected or how its labels were made.

| Fact | Observed value |
|------|----------------|
| Rows / columns | 10,800 / 15; no exact duplicate rows |
| Households | 360 pseudonymous `Meter_Id` values, exactly 30 rows each |
| Time | one record per meter per day, 1–30 January 2023 (daily D1; not 15-min/1 Hz) |
| Target | `Abnormal_Usage`: 4,739 positive (43.88%) and 6,061 negative (56.12%) |
| Location fields | Kerala region codes `IN_KL_ERN`, `IN_KL_TVM`, `IN_KL_ALP` |
| Context | dwelling type, occupants, house area, appliance score, connected load, temperature and humidity |
| Energy fields | expected, actual, usage deviation, and cluster-average daily kWh |
| Electrical telemetry | no voltage, current, power, PF, outage, or appliance-level readings — it cannot support D2/D3 claims |
| Missing values | literal string `null`: 667 expected-energy rows and 900 actual-energy rows; no blank cells |

Raw `Expected_Energy(kwh)` and `Actual_Energy(kwh)` values include a trailing ` kWh`
suffix and must be parsed to numeric values. `Actual_Energy(kwh)` missingness is a
critical leakage/data-quality issue: all 900 missing-actual rows are labelled abnormal.
Missingness must therefore be handled before any model fit and must never be presented as
an energy anomaly. The file contains no licence, label definition, data-collection
method, or provenance statement; these remain unresolved.

> **Provenance warning [I].** This is a community dataset, not KSEB data and not evidence
> that the detector works on live Kerala homes. The short, complete 30-day panel,
> pseudonymous IDs, limited region/category cardinalities, and label/missingness pattern
> are consistent with generated or curated data, but do not prove it is synthetic. Treat
> it as a prototype fixture until the publisher documents collection and labelling.

### Dataset schema and usable fields

| Raw field | Type after parsing | Role / handling |
|-----------|--------------------|-----------------|
| `Meter_Id`, `Date` | ID; day-first date | group key; daily time ordering |
| `Region_Code`, `Dwelling_Type` | categorical | profile context |
| `Num_Occupants`, `House_Area (sqft)`, `Appliance_Score`, `Connected_Load(kw)` | numeric | profile context |
| `Temperature_C`, `Humidity (%)` | numeric | observed weather context |
| `Expected_Energy(kwh)`, `Actual_Energy(kwh)` | numeric after stripping ` kWh` | expected/observed daily energy; preserve source-missingness separately |
| `Usage_Deviation(%)`, `Cluster_Avg_Energy(kwh)` | numeric | diagnostic/benchmark-only until label provenance is known |
| `Abnormal_Usage` | binary integer | benchmark target |

The 30 days per meter make this a **short daily D1 panel**, not a profile-only table.
It can support a limited daily expected-vs-actual replay, but cannot train or validate
hour-of-day, night-baseload, edge/plateau, outage, voltage, or appliance-health features.

---

## 1. Role of this dataset in the system

The system already has an *unsupervised* anomaly path specified in file 05 §2:
forecast-residual scoring + Isolation Forest + change-point. That path is the **primary**
detector because it works on any household with 2–4 weeks of data and needs no labels.

This dataset gives us the one thing that path lacks: **labels**. Its two legitimate
uses, in priority order:

| Use | What it buys us | Risk |
|-----|-----------------|------|
| **U1 — Daily labelled benchmark** | Report precision / recall / PR-AUC for a *daily* prototype instead of only synthetic-injection numbers (file 06 cross-cutting limitation 2) | Label semantics and leakage may not match the product definition |
| **U2 — Daily cold-start prior** | A population-level score based on profile, weather and a modelled expected daily kWh | It is not an interval detector and must be down-weighted as personal history accrues |
| **U3 — Anomaly-type tagger** | Not available: the CSV has only the binary target, with no reason/severity/type field | Do not invent anomaly-type labels from this dataset |

**Non-uses — state these explicitly in the README so nobody drifts:**
it does **not** make the system a fault detector (file 03 stands unchanged); it does
**not** replace the residual detector; it does **not** license the claim "validated on
Kerala households".

---

## 2. Data contract & ingestion

The dataset enters through the existing adapter interface (file 04), as one more source.
No bespoke pipeline.

```
data/Intelligent_abnormal_electricity_usage.csv
        ↓  adapters/intelligent_abnormal.py
canonical frame  →  features/  →  models/
```

**Canonical labelled-record schema** (what the adapter must emit, whatever the raw columns are):

```python
# src/adapters/intelligent_abnormal.py
CANONICAL = {
    "household_id": "str",     # direct mapping from Meter_Id
    "ts":           "datetime64[ns]",  # Date, parsed day-first
    "kwh":          "float",   # Actual_Energy(kwh): observed daily kWh
    "power_w":      "float",   # optional (D2)
    "voltage_v":    "float",   # optional (D2)
    "current_a":    "float",   # optional (D2)
    "pf":           "float",   # optional (D2)
    "context":      "dict",    # region, dwelling type, occupants, area, appliance score, load, weather
    "label":        "int8",    # 1 = abnormal, 0 = normal
    "label_kind":   "str",     # 'dataset' | 'synthetic' | 'user_confirmed'
    "src":          "str",     # 'intelligent_abnormal_electricity_usage_local_v1'
}
```

Rules:

- **Never** mix `label_kind` values in a training split without recording the mix in the model card.
- The adapter writes a `dataset_fingerprint` (sha256 of the sorted raw file bytes) into
  every artefact so results are reproducible and a silent dataset update is detectable.
- Retain `expected_kwh_source`, `usage_deviation_pct`, and boolean source-missingness
  columns in the audit output. They are **not** default training features (§3).
- Version the adapter output as Parquet under
  `data/interim/intelligent_abnormal_usage_v1.parquet`.

---

## 3. Label-integrity gate (the decisive step)

File 05 guiding principle 1 **[I]**, derived from [C] **[E]**: *do not use ML to re-learn
a rule you could write.* [C]'s classifiers reached ≈100 % accuracy because they were
trained on labels produced by a deterministic algorithm — that is compression, not
learning. A Kaggle dataset titled "abnormal usage" with a binary target is a prime
candidate for exactly the same trap: labels generated by a threshold or a formula.

**The first audit has already exposed a blocker:** source `Actual_Energy(kwh)` is
missing on 900 rows and every one is positive. Exclude those rows from energy-anomaly
training/evaluation (or report them only as a separate data-quality case). Also exclude
raw `Usage_Deviation(%)`, raw source `Expected_Energy(kwh)`, and source-missingness from
the predictive feature set until the publisher documents the label-generation process:
they may be inputs to, or direct proxies for, the label. A model that uses them would not
be deployable, because the product must generate its expected kWh independently.

Run the following on the remaining 9,900 observed-energy rows before choosing a model.

```python
# scripts/label_integrity.py
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import cross_val_score

for depth in (1, 2, 3, 5):
    clf = DecisionTreeClassifier(max_depth=depth, random_state=0)
    s = cross_val_score(clf, X, y, cv=5, scoring="balanced_accuracy")
    print(depth, s.mean().round(4), s.std().round(4))

clf = DecisionTreeClassifier(max_depth=3).fit(X, y)
print(export_text(clf, feature_names=list(X.columns)))   # read the rule out loud
```

Also: single-feature AUC for every column, and a check for a monotone threshold
(`y == (feature > c)`) on each numeric column.

### Decision branches

| Finding | Interpretation | What we build |
|---------|----------------|---------------|
| **A.** depth ≤ 3 tree reaches ≥ 0.98 balanced accuracy, and the printed rule is a clean threshold | Label is **rule-derived**. Papers' trap. | Do **not** ship a classifier for it. Extract the rule, implement it as an explicit daily rule, and use the dataset only as a sanity fixture + demo data. |
| **B.** shallow trees are mediocre (< 0.9) but a full GBM reaches 0.9+ using only deployable profile, calendar, weather, lag and independently-modelled residual features | Label may carry behavioural signal. | Build the constrained daily supervised model in §5; it remains a secondary scorer. |
| **C.** performance is high only when source expected/deviation/missingness fields are included | Leakage or target reconstruction. | Reject that model and report the result; do not use the dataset as supervised evidence. |
| **D.** nothing beats ~0.6 AUC with deployable features | Labels are noise or unlearnable from these columns. | Use U1 only; retain the residual detector as the sole detector. |

**Leakage checks that run in every branch:**

- Drop any column that is a deterministic function of the label. In this CSV, treat
  source `Expected_Energy(kwh)`, `Usage_Deviation(%)`, and missingness indicators as
  suspected leakage until disproven.
- Check the label is not derivable from an ID ordering (sort by index, plot label runs).
- If a household ID exists, verify labels are not constant per household — if they are,
  the task is *household* classification, not *daily-record* classification, and the split
  must be grouped (§6).

---

## 4. Feature engineering

Two feature families; which ones exist depends on the audit.

### 4.1 Daily features available in this dataset (D1)

This dataset can share only a **daily** feature-builder subset with M2
(`src/features/daily.py`), not `features/interval.py`:

| Group | Allowed features |
|-------|------------------|
| Calendar | date, day-of-week and weekend flag; no hour-of-day or month variation exists in the 30-day panel |
| Profile | region, dwelling type, occupants, area, appliance score and connected load |
| Weather | supplied temperature and humidity; do not join a second weather source unless location/date alignment is verified |
| Personal history | prior-day and 7-day rolling actual-kWh summaries, only after sorting within `Meter_Id` and only from earlier dates |
| Baseline-relative | residual from an expected-daily-kWh model fitted on training history only; rolling-median/MAD residual where sufficient history exists |

Do **not** create hourly/calendar-sine, night-baseload, edge-count, plateau, outage,
voltage/current/PF, appliance, or 24-hour features from this CSV. They have no source
signal. The raw expected-energy and deviation fields are audit-only suspected-leakage
fields (§3), not inputs to the deployable model.

**Critical rule [I]:** the *daily residual* feature is what makes this a
context-conditional detector rather than a threshold. It must be computed with a
forecaster trained only on days strictly before the scored day (see §6 leakage discipline).

### 4.2 Profile-only fallback

If lag/residual features cannot be calculated for a scoring context, use only the profile
and weather fields above. Label the result a *population prior*, not a personal anomaly;
the CSV has no appliance inventory from which fan-equivalent or appliance-load-index
features can honestly be derived.

---

## 5. Model specification

### 5.1 Model ladder — always report all three

| Tier | Model | Purpose |
|------|-------|---------|
| **B0** | Majority class + a single-threshold rule on total kWh | Floor. If the real model doesn't clear this by a wide margin on PR-AUC, there is no story. |
| **B1** | Logistic regression on the standardised feature set | Linear reference, gives signed coefficients for the write-up |
| **M** | **LightGBM binary classifier** (`objective=binary`, `is_unbalance=True` or `scale_pos_weight`), native categorical features | Primary. Tree ensembles are the paper-supported default for electricity data — [A Table VIII] RF/XGBoost best **[E]**, [B Table 2] RF best at 12 ms inference **[E]** |
| **M-alt** | Isolation Forest / One-Class SVM trained on normals only, scored on the test set | Shows how much the labels are actually worth vs. a purely unsupervised detector. This comparison is the honest core of the evaluation. |

**On the dataset's `tensorflow` tag:** ignore it as a modelling instruction. A neural net
is not justified here — [B] measured a shallow NN *worse* than RF (RMSE 10.1 vs 8.2,
45 ms vs 12 ms) **[E]**, and [A]'s ANN also trailed RF **[E]**. If a deep model is wanted
for the report, add a 1-D CNN / LSTM only as an **[X]** ablation with the honest verdict
that it did not beat the GBM, rather than as the headline model.

### 5.2 Hyper-parameters (starting grid)

```yaml
# configs/model_abnormal_lgbm.yaml
objective: binary
metric: [average_precision, auc]
learning_rate: 0.05
num_leaves: [15, 31, 63]
min_data_in_leaf: [20, 50, 100]
feature_fraction: [0.7, 0.9, 1.0]
bagging_fraction: 0.8
bagging_freq: 1
lambda_l2: [0.0, 1.0, 5.0]
n_estimators: 2000
early_stopping_rounds: 100
scale_pos_weight: auto        # = n_neg / n_pos from the training fold only
```

Search: Optuna, 50 trials, optimising **average precision** on the validation folds — not
accuracy. With an imbalanced anomaly target, accuracy is meaningless.

### 5.3 Calibration and thresholding

The product needs a *probability* (for "how sure are we" in the UI and for the LLM facts
payload), not a raw score.

- Wrap the fitted model in `CalibratedClassifierCV(method="isotonic", cv="prefit")` on a
  held-out calibration split; report the Brier score and a reliability curve.
- Pick the operating threshold by an **alert-budget** rule, not by F1: choose τ such that
  the expected alert rate is ≤ 2 per household per week. A detector that fires daily gets
  muted by users and is worse than none (file 06 cross-cutting limitation 5).
- Expose three sensitivity presets in the UI (conservative / balanced / sensitive) mapped
  to three τ values, with the measured precision at each printed in the model card.

---

## 6. Training protocol

| Item | Spec |
|------|------|
| **Primary split** | Daily temporal hold-out: train 1–24 January and test 25–30 January for every meter. Compute all lags/residuals using only earlier dates. This is the closest replay of scoring an existing household. |
| **Secondary split** | `GroupKFold(5)` on `Meter_Id`, using only profile/weather/calendar features. It measures transfer to unseen meters, but cannot use personal-history features for a completely unseen meter. |
| **Never** | A plain random row split. It would put adjacent daily records from the same meter into train and test and inflate metrics. |
| **Imbalance** | Class weights first. SMOTE only as an ablation, applied **inside** the CV fold, never before splitting. |
| **Residual feature leakage** | The expected-daily-kWh model is fitted per fold on that fold's training window only, with a walk-forward scheme. Never substitute the CSV's raw `Expected_Energy(kwh)` or `Usage_Deviation(%)` for it. |
| **Scaling** | Not needed for LightGBM; fit the scaler inside the pipeline for B1. |
| **Seeds** | 5 seeds, report mean ± std. A single run is not a result. |
| **Tracking** | MLflow (or a plain `runs/<timestamp>/metrics.json` if time-poor); log dataset fingerprint, config, git SHA, metrics, feature importances. |
| **Data-quality exclusion** | Exclude the 900 rows with missing `Actual_Energy(kwh)` from model metrics. Report their count and label concentration separately; do not silently impute them. |

---

## 7. Evaluation

### 7.1 Metrics (report all, headline is PR-AUC)

| Metric | Why |
|--------|-----|
| **PR-AUC / average precision** | Correct headline for rare-positive detection |
| ROC-AUC | Comparability with literature |
| Precision @ alert-budget (2/household/week) | The number that actually matters to a user |
| Recall at that τ | What we miss |
| Brier score + reliability curve | Is the probability honest? |
| Confusion matrix at τ | For the slide |
| Per-household precision spread | Catches "great on average, useless for half the homes" |
| Inference latency per 1 000 rows | [B] reports 12 ms/appliance **[E]**; keep parity |

### 7.2 Three evaluation surfaces — all three go in the report

1. **Supplied-CSV daily hold-out**: temporal (1–24 January train, 25–30 January test)
   is primary; grouped-by-meter results are secondary and profile-only.
2. **Synthetic-injection benchmark** (file 07 M8): inject spikes, phantom-load steps,
   left-on plateaus, post-outage recharge bumps and ageing drift into iAWE/UCI replays;
   measure detection rate per injected event type and the false-alarm rate on clean
   stretches. This tests *our* definition of abnormal, which the Kaggle labels may not
   share.
3. **Cross-dataset transfer**: only after aggregating iAWE/UCI to compatible daily kWh
   and supplying equivalent context. Report the alert rate; do not score their raw
   intervals with this daily model. A high normal-day alert rate signals a
   dataset-specific artefact. Report it either way.

### 7.3 Required ablations

- Without weather features → shows whether [A]'s covariate finding transfers to households.
- Without the residual feature → quantifies how much the context-conditional design contributes.
- Supervised (M) vs unsupervised (M-alt) on the same test set → answers "were the labels worth it?"
- Shallow-tree (depth 3) vs full model → the §3 rule-compression check, reported as a number.

### 7.4 Explainability (non-optional — the product promises it)

Every alert must render as *expected / observed / why*. Implement with SHAP
(`TreeExplainer`, cheap on LightGBM): top-3 contributing features per flagged day,
translated into a sentence template. These templates, plus the deterministic numbers,
are what goes into the LLM facts payload — the LLM phrases, never computes
([B Discussion B] limitation 4 **[E]**, file 05 §7).

---

## 8. Integration into the running system

```
                 daily CSV replay / daily upload
                                │
                       features/daily.py
                                │
            ┌───────────────────┼────────────────────┐
            ↓                   ↓                    ↓
   expected-daily model  supervised daily      Isolation Forest
   (walk-forward)        classifier (this doc)  (daily features)
            │                   │                    │
     residual, bands       p_abnormal            outlier score
            └───────────────────┼────────────────────┘
                                ↓
                         fusion + hysteresis
                                ↓
                    anomaly event {type, severity,
                    expected, observed, top factors}
                                ↓
                 rule engine  →  facts JSON  →  LLM phrasing
                                ↓
                             dashboard / alert
```

This pipeline is for **daily replay/upload only**. It must not be wired directly to the
live MQTT/interval alert path: the CSV has no interval telemetry. The live path retains
its separately trained interval residual/Isolation Forest models; both paths may share
the event schema, not a falsely shared feature set.

**Fusion rule [X]** — deliberately simple and explainable:

```python
score = w_r * robust_z(residual) + w_s * logit(p_abnormal) + w_i * iforest_score
# w_s starts at 0.5 for a new household (cold start, use U2)
# and decays to 0.15 once >= 28 days of personal history exist;
# w_r rises correspondingly. Weights are config, logged per alert.
```

**Hysteresis:** a daily event fires only if `score > τ_high` for ≥ 2 consecutive days and
clears below `τ_low`. This is deliberately not reused for the live interval path.

**Suppression rules (deterministic, run before alerting):**
outage gaps (V = 0 / missing) are events, not anomalies; post-outage inverter recharge
bumps are tagged, not flagged (file 07 novelty 3); scheduled high-load windows the user
confirmed are whitelisted.

**Service contract:**

```http
POST /api/v1/anomaly/daily-score
{
  "household_id": "h_0021",
  "day": {"ts": "2026-01-25", "kwh": 19.89},
  "context": {"region_code": "IN_KL_TVM", "dwelling_type": "Apartment",
              "num_occupants": 3, "temperature_c": 29.5, "humidity_pct": 83.5}
}
→ 200
{
  "p_abnormal": 0.81,
  "calibrated": true,
  "expected_kwh": 0.21, "band": [0.12, 0.34],
  "anomaly_type": "daily_usage_deviation",
  "severity": "medium",
  "top_factors": [
    {"feature": "daily_residual_z", "value": 6.4, "direction": "+"},
    {"feature": "temperature_c", "value": 29.5, "direction": "+"},
    {"feature": "connected_load_kw", "value": 3.0, "direction": "+"}
  ],
  "model": {"name": "abnormal_lgbm", "version": "1.0.0",
            "dataset_fingerprint": "sha256:…", "trained_at": "2026-09-18T11:04:00Z"},
  "advice_eligible": true
}
```

Latency target: p95 < 50 ms per daily record on CPU, batch-scored for replay.
Artefacts: `models/abnormal_lgbm/1.0.0/{model.txt,calibrator.pkl,features.json,model_card.md}`.

---

## 9. Repository plan

```
src/
  adapters/intelligent_abnormal.py # local CSV → canonical daily parquet (+ fingerprint)
  features/daily.py                # dataset-specific daily replay features
  features/interval.py             # separate live D1/D2 interval path
  models/abnormal/train.py         # ladder B0/B1/M/M-alt, CV, Optuna, MLflow
  models/abnormal/calibrate.py
  models/abnormal/predict.py       # loaded by the FastAPI service
  eval/benchmark.py                # 3 surfaces + ablations → report.md
  eval/inject.py                   # synthetic event injection (M8)
  serving/api.py
scripts/
  audit_dataset.py
  label_integrity.py
configs/
  model_abnormal_lgbm.yaml
  fusion.yaml
docs/research/
  08_abnormal_usage_model_spec.md  # this file
  08a_dataset_audit.md             # produced by Step 0
  08b_model_card.md                # produced by training
```

**Model card (`08b`) must state:** dataset + fingerprint + licence, label provenance and
the §3 branch verdict, splits used, metrics with seed variance, the operating threshold
and its measured precision, known failure modes, and the sentence *"trained on a public
community dataset; not validated on live KSEB household data."*

---

## 10. Execution plan

| Phase | Work | Output | Gate |
|-------|------|--------|------|
| **P0** (complete) | Audit supplied CSV and record schema/fingerprint | 10,800-row daily D1 panel; class balance; missingness | §0 completed; provenance/licence still open |
| **P1** (1 h) | Run `label_integrity.py` after excluding missing-actual rows and suspected leakage fields | Branch verdict in `08a` | **Hard gate** — do not train before this |
| **P2** (2–3 h) | Adapter → canonical parquet; feature builder; B0/B1 baselines | Baseline PR-AUC | B0 number recorded |
| **P3** (3–4 h) | LightGBM + Optuna + grouped/temporal CV; calibration | Model artefact + metrics | Beats B0 on PR-AUC by a margin > seed std |
| **P4** (2 h) | SHAP explanations, threshold by alert budget, model card | `08b_model_card.md` | Every alert renders expected/observed/why |
| **P5** (3 h) | Synthetic-injection benchmark + cross-dataset transfer + ablations | `eval/report.md` | All three surfaces reported, including bad numbers |
| **P6** (2 h) | Daily replay endpoint, fusion with daily residual + IForest, hysteresis | `/anomaly/daily-score` | p95 < 50 ms; replay demo runs end to end |
| **P7** (1 h) | Dashboard wiring + LLM facts payload with numeric post-check | Demo path | LLM cites only numbers present in the payload |

Total ≈ 15–18 focused hours, sequencable across two people (P2–P3 modelling, P6–P7
integration in parallel once the contract in §8 is frozen).

## 11. Definition of done

1. `08a` audit and `08b` model card exist and are accurate.
2. Branch verdict from §3 is recorded, with the shallow-tree numbers that justify it.
3. PR-AUC, precision at the alert budget, and Brier reported with mean ± std over 5 seeds,
   on the specified temporal and grouped splits; missing-actual rows are reported separately.
4. Unsupervised baseline reported alongside the supervised model on the same test set.
5. Cross-dataset transfer result reported — even if it is bad.
6. Every alert in the UI shows expected, observed, and top factors.
7. No claim anywhere in the repo or deck that this model detects faults, theft, earthing,
   leakage or appliance age (file 03 stands).

## 12. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Labels are rule-derived → model is rule compression | **High** | Would invalidate the headline claim | §3 gate; if Branch A, pivot to rule extraction and say so publicly — it becomes a rigour point, not a failure |
| Dataset is synthetic/simulated without saying so | Medium | Transfer to real data fails | Generator fingerprints in the audit (rounded values, duplicate rows, impossible precision); cross-dataset transfer test |
| Missing actual kWh is perfectly associated with positives | **High** | A model could learn missingness rather than abnormal usage | Exclude those 900 rows from energy metrics; make missingness a data-quality event only |
| Source expected/deviation fields reconstruct the label | **High** | Inflated, non-deployable classifier | Exclude them from deployable features; report the leakage probe in the model card |
| Random split inflates metrics to ~0.99 | Medium | Credibility loss under questioning | Temporal and grouped splits enforced in the pipeline; B0 baseline exposes it |
| "Abnormal" in the dataset ≠ "abnormal" in our product | **High** | Users get irrelevant alerts | Keep the residual detector primary; use this as cold-start prior only (U2); evaluate on injected events too |
| Tiny dataset (< a few thousand rows) | Medium | Unstable metrics | Report seed variance and CI; prefer the simpler model when overlapping |
| Licence forbids redistribution | Low | Cannot ship data in the repo | Ship the download script, not the CSV; record licence in the model card |
| Scope creep into TensorFlow/deep models | Medium | Time lost, worse results | §5.2 — deep model is an optional ablation only |

## 13. Open questions (close in P0/P1)

1. **Answered:** 15 columns, 10,800 rows, 43.88% positive; licence remains unknown.
2. **Answered:** daily time series, 30 days × 360 meters; it is a short D1 panel.
3. **Answered:** `Meter_Id` exists; use temporal primary and grouped secondary splits.
4. **Answered:** no reason/severity/type field; U3 is out.
5. **Answered:** no V/I/PF; it cannot feed D2 voltage/safety features.
6. **Open:** real-measured versus generated/curated, and the label-generation rule.
7. **Not applicable:** it includes only a compact household profile, not the Cherukunnu variable set.

---

## Decision log

- 2026-09-17 — *Intelligent Abnormal Electricity Usage Dataset* adopted as the labelled
  source for the daily M2 prototype, with two sanctioned uses (benchmark and cold-start
  prior). It has no anomaly-type field. Any supervised classifier is a **secondary**
  scorer, never a replacement for the residual detector. The label-integrity gate (§3)
  is a hard prerequisite to training. The dataset is not KSEB data and must never be
  described as such.
- 2026-09-17 — Local CSV audit completed: 360 meters × 30 daily records in January 2023,
  no D2 telemetry and no anomaly-type label. The supplied missing actual-kWh field is
  perfectly associated with the positive class; missing rows and suspected label-proxy
  fields are excluded from deployable supervised features pending the integrity gate.

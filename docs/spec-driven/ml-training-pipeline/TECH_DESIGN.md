# Energy Intelligence ML Training Pipeline — Technical Design and Implementation Plan

Status: **Draft**
Based on PRD: 2026-09-17 draft
Owner: Project team
Approval: **Pending**

Evidence tags follow `docs/research/README.md`. Unless explicitly tagged otherwise,
the implementation design in this draft is a proposed extension **[X]**.

## Current system state

The repository currently contains documentation and three CSV files; it has no
application, Python package, test suite, dependency lock, executable data audit, or
trained artifact. **[E: repository inspection, 2026-09-17]** Existing research
documents define model intent and verified facts but are not executable. **[E]**

Observed source inventory:

| Source ID | File | Observed shape/hash | Permitted role |
|---|---|---|---|
| `smart_meter_15min_v1` | `synthetic_smart_meter_15min.csv` | 32,256 × 19; 12 meters × 2,688 intervals; SHA-256 `1ad550…ab20ab` **[E]** | Primary interval forecast/anomaly/rules/injection path |
| `labelled_home_15min_v1` | `ai_energy_intelligence_dataset.csv` | 5,760 × 30; one 60-day series; SHA-256 `25a5d1…2f576` **[E]** | Held-out anomaly/wastage/appliance evaluation and safety replay facts |
| `daily_abnormal_v1` | `Intelligent_abnormal_electricity_usage.csv` | 10,800 × 15; 360 meters × 30 days; SHA-256 `fc18db…eff` **[E]** | Leakage-gated daily benchmark/cold-start candidate only |

Hashes are recorded observations, not permanent acceptance constants. A changed hash
triggers a new source version and complete re-audit.

## Overall approach

Implement a Python package with a thin CLI and configuration-driven orchestration.
Each source passes through an explicit adapter to a task-specific canonical table.
Shared causal feature code is fit through scikit-learn-compatible pipelines. Runs use
predeclared splits, deterministic seeds, immutable output directories, and phase
completion markers. A manifest binds raw fingerprints, configuration, code revision,
environment, split membership hash, feature schema, artifacts, and metrics.

Proposed command contract **[X]**:

```bash
python -m backend.ml.training.run \
  --data-dir data \
  --config configs/ml/training.yaml \
  --output-dir artifacts/ml
```

Modes: `--dry-run`, `--component forecast|interval-anomaly|daily-benchmark|labelled-fixture-eval`,
and `--resume <run-id>`. Promotion is separate:

```bash
python -m backend.ml.training.promote --run-id <run-id>
```

## Modules and responsibilities

| Module | Responsibility | Related FRs | Owned contracts |
|---|---|---|---|
| `inventory` | Discover files, match schema signatures, hash bytes, reject ambiguity | FR-001–FR-003 | `SourceDescriptor` |
| `adapters` | Parse raw schemas into validated canonical frames | FR-004–FR-007 | Canonical interval/daily records |
| `quality` | Structural, time, range, null, formula, provenance, and leakage checks | FR-002–FR-008 | `AuditFinding`, severity policy |
| `splits` | Generate and persist immutable temporal/group assignments | FR-008–FR-009 | `SplitManifest` |
| `features` | Causal transformations and ordered feature schemas | FR-008 | `FeatureSchema` |
| `forecast` | Seasonal-naive, RF, XGBoost fitting and selection | FR-010–FR-011 | `ForecastPrediction` |
| `anomaly` | Residual/MAD, Isolation Forest, rules, fusion, hysteresis | FR-012 | `AnomalyFacts` |
| `evaluation` | Injection truth, labelled fixture evaluation, metrics, plots | FR-013–FR-015 | Metric JSON schemas |
| `daily_benchmark` | Leakage probes and conditional classifier benchmark | FR-006, FR-014 | Gate verdict |
| `artifacts` | Atomic run writes, package validation, promotion, rollback | FR-016–FR-018 | `RunManifest`, model-card schema |
| `inference` | Load promoted package, validate inputs, emit typed facts | FR-019 | Input/output schemas |
| `reporting` | Audit/model cards/summary and identifier-safe logs | FR-015, FR-020–FR-022 | Markdown + JSON reports |

## Proposed repository layout

```text
backend/
  ml/
    contracts/          # typed canonical, manifest, feature, and prediction schemas
    inventory.py
    adapters/           # one module per supported source schema
    quality/             # checks and leakage policy
    splits.py
    features/            # interval and daily causal builders
    models/              # forecast, outlier, rules, fusion, daily benchmark
    evaluation/          # injection, replay, metrics, plots
    artifacts/           # writer, validator, promotion
    inference/
    training/            # orchestration CLI and phases
configs/ml/
  data_contracts.yaml
  training.yaml
  injection.yaml
data/derived/            # ignored, reproducible canonical/split data
artifacts/ml/            # ignored model binaries; manifests/cards may be published later
tests/ml/
  unit/
  integration/
  fixtures/
```

Implementation may adjust package names to an established backend layout once one
exists, but public contracts and acceptance behavior require specification approval to
change.

## Interface contracts

### Source discovery

`SourceDescriptor` fields: `source_id`, `path`, `sha256`, `bytes`, `row_count`,
`columns`, `schema_version`, `provenance_class`, `adapter_version`. Matching uses a
required/forbidden column signature. Filenames provide diagnostics only. Duplicate
matches, zero matches for a required component, or one file matching multiple adapters
are blocking errors.

### Canonical interval record

```text
household_id: string
timestamp: datetime[Asia/Kolkata]
interval_minutes: int
kwh: float >= 0
power_kw, voltage_v, current_a, power_factor: nullable float
temperature_c, humidity_pct: nullable float
connected_load_kw: nullable float > 0
context: structured categorical fields
source_id, source_row_id: string
provenance_class: synthetic | community-undocumented
```

Ground-truth and audit-only values live in separate namespaced evaluation tables and
cannot be joined into the training feature builder.

### Training request/result

```text
TrainingRequest:
  data_dir, output_dir, config_path, components[], seed, resume_run_id?

TrainingResult:
  run_id, state, candidate_artifacts[], gate_results[], metrics_uri,
  manifest_uri, warnings[], blocking_findings[]
```

### Interval inference result

```json
{
  "household_id": "SM-KL-001",
  "timestamp": "2026-08-28T23:45:00+05:30",
  "observed_kwh": 0.30,
  "expected_kwh": 0.08,
  "forecast_model": "seasonal_naive|random_forest|xgboost",
  "residual": 0.22,
  "residual_robust_z": 5.1,
  "iforest_percentile": 0.97,
  "rule_flags": [],
  "fused_score": 0.91,
  "event_state": "open",
  "model_version": "<run-id>:interval-v1",
  "source_provenance": "synthetic"
}
```

## Dataset-specific design

### Smart-meter interval adapter

- Parse existing timezone-aware ISO timestamps and require 15-minute cadence per
  meter, unique `(meter_id, timestamp)`, monotonic cumulative energy, non-negative
  interval energy, and supported physical ranges.
- Recalculate `kwh - power_kw * 0.25` and
  `power_kw - voltage_v * current_a * power_factor / 1000`; report tolerance breaches.
- Preserve `consumer_number` only in a restricted audit mapping; never log it or use it
  as a feature.

### Labelled-home interval adapter

- Localize naive timestamps to Asia/Kolkata and require 96 records per complete day.
- Place `anomaly_flag`, `waste_event_flag`, `anomaly_type`, `gt_*`, and `addon_*` in an
  evaluation-only table.
- Exclude `monthly_cum_kwh`, running charges/duty, all ground-truth components,
  ageing factor, safety measurements/labels, and future-derived fields from forecast
  and anomaly training.
- Safety data is replayed as supplied simulated sensor evidence; it is not a predicted
  target of this ML package.

### Daily community adapter

- Parse day-first dates and strip the literal ` kWh` suffix only in the adapter.
- Preserve missingness in audit data, but exclude 900 rows missing actual energy from
  energy-anomaly fit/evaluation.
- Quarantine source expected energy, usage deviation, cluster average, and missingness
  indicators from the deployable feature set until the label rule is documented.
- Run label-integrity probes before any candidate classifier.

## Splits and leakage controls

### Primary 12-meter interval source

The four-week source is used as follows **[X]**:

- Days 1–21: fit preprocessing and models.
- Days 22–24: validation, hyperparameters, thresholds, and fusion tuning.
- Days 25–28: locked clean test and injected-event test copies.
- Report metrics per meter and globally. No test row may influence imputation,
  encoders, scalers, residual distributions, or Isolation Forest.

This primarily measures temporal generalization for known source profiles. A secondary
group holdout (meters 10–12 test, fixed before fitting) measures household transfer; it
does not replace the primary temporal result.

### Labelled single-home source

- First 42 days: optional fit/calibration only for components explicitly allowed by
  configuration.
- Next 8 days: validation/threshold selection.
- Final 10 days: locked labelled evaluation.
- Context-explained guest spikes are reported separately from waste events; they are
  not silently relabelled to improve performance.

### Daily 360-home source

- Primary: days 1–24 train/validation, days 25–30 locked temporal test.
- Secondary: deterministic group holdout by hashed meter ID with no household overlap.
- Any preprocessing is fitted independently inside each split.

### Automated leakage guard

The feature builder accepts an allowlist, not a blocklist. Tests inspect ordered schema
and lineage. A future-value mutation test changes values after a cutoff and asserts all
earlier features and predictions are unchanged.

## Feature engineering

Initial interval features **[I]**:

- Calendar: quarter-hour slot (cyclic sin/cos), hour, weekday, weekend.
- History: lags 1, 4, 96, 672; prior-only rolling median/mean/MAD/std over 4, 96, 672.
- Change/context: prior-interval delta, same-slot prior-week delta/ratio, temperature,
  humidity, connected-load-normalized kWh.
- Electrical: voltage, current, PF, frequency and formula residuals for outlier/rule
  components; inclusion in expected-load candidates is ablated and documented.
- Categoricals: dwelling and region through train-fitted unknown-safe encoding.

The first seven days are warm-up for weekly features. Missing values receive explicit
indicators only where missingness is available at inference and not label-derived.

## Model training and selection

### Expected load

Candidates share eligible rows and metrics:

1. Seasonal-naive: same interval one week ago; meter/slot median fallback.
2. Random Forest regressor with bounded search defined in configuration.
3. XGBoost regressor with bounded CPU search and early stopping on validation only.

Selection rule **[X]**: choose the least complex candidate whose global validation MAE
improves by at least 5% over seasonal-naive and does not worsen more than 25% of meters
by over 10%. If none qualifies, publish seasonal-naive. Tie within 1% favors the simpler
model. Freeze the winner and threshold configuration before one locked-test evaluation.

### Residual and Isolation Forest

Compute signed residuals and robust z-scores from training residual median/MAD per
meter and context slot, with a documented global fallback. Fit Isolation Forest only on
training features after excluding any known injected/labelled event. Start with the
configuration proposed in `docs/research/09_model_implementation_plan.md`; tune only on
validation and report sensitivity across at least three seeds.

### Fusion and event state

Keep configurable initial weights `0.60 residual + 0.25 Isolation Forest + 0.15 rule`.
Rules remain independently visible; no weighted score converts them into diagnoses.
Open an event after two consecutive scores above `threshold_high`; close after two
below `threshold_low`. Gaps suspend scoring, and post-gap recovery is tagged separately.

### Daily gate

Run majority/logistic baselines, single-feature AUCs, monotone-threshold probes, and
depth 1/2/3/5 decision trees with and without proxy fields. Then compare constrained RF
and XGBoost on deployable fields. If a shallow rule reaches >=0.98 balanced accuracy,
or performance collapses without proxies, publish the finding and no classifier. A
classifier is promotion-eligible only if it beats baselines on both temporal and group
tests and passes calibration/seed-stability checks.

## Evaluation

### Forecast metrics

MAE, RMSE, sMAPE with epsilon handling, median absolute error, and per-meter error.
MAPE may be shown only with the zero-load policy stated.

### Injected events

Deterministically create spike, left-on plateau, baseload step, voltage excursion, and
post-outage recovery scenarios in test copies. Store interval and event truth, source
hash, seed, config hash, and truth hash. Report event precision/recall/F1, interval
PR-AUC, detection delay, false alerts per meter-week on clean test, and type breakdown.

### Labelled fixture

Report anomaly and waste separately: precision, recall, F1, PR-AUC, confusion matrix,
event-level metrics, and contextual-spike false-positive behavior. Appliance class
evaluation belongs to a later bounded component unless implemented in the approved
scope; no aggregate forecast feature may use `gt_*` values.

## Artifact and manifest contract

Each run is written to a temporary sibling directory and atomically renamed only after
validation. Required files:

```text
artifacts/ml/<run-id>/
  manifest.json
  audit.json
  split_manifest.json
  feature_schema.json
  metrics.json
  model_card.md
  models/<component>/...
  reports/summary.md
  reports/plots/...
  SUCCESS | FAILED
```

`manifest.json` includes run ID/status, start/end UTC time, command, code commit and
dirty flag, Python/dependency versions, OS/CPU summary, source descriptors, config and
split hashes, seed, component artifacts/checksums, metric schema version, limitations,
and parent run when resumed. Model serialization uses joblib only for trusted local
artifacts; loading verifies checksums and compatible package versions.

## State transitions

`created → auditing → canonicalizing → splitting → training → validating → testing → candidate`

Any phase may transition to `failed`; a resumed run creates a child attempt and reuses
only checksum-verified completed outputs. `candidate → promoted → superseded`; rollback
changes the `current` pointer to a prior promoted run and does not delete artifacts.

## Concurrency, consistency, and idempotency

- One file lock per output root prevents two writers from claiming the same run ID.
- Run IDs contain UTC time plus config/source hash prefix; collisions fail.
- Phase writes are atomic; manifests are append-by-attempt and finalized once.
- Rerunning with identical inputs creates a new auditable run, not an overwrite.
- Parallel candidate fitting may be enabled, but fixed seeds and bounded thread counts
  are recorded; deterministic equivalence uses tolerance for library-level floating
  point differences.

## Privacy and security

- The pipeline requires no network access after dependencies are installed.
- CSV content is never sent to Groq or another external service.
- Logs exclude raw `consumer_number`; model inputs exclude direct source identifiers.
- Artifact loading is restricted to locally generated, checksum-verified packages.
- Paths are resolved beneath configured roots; symlink escapes and formula injection in
  generated CSV reports are rejected/escaped.

## Failures, retry, recovery, and degradation

| Failure | Behavior |
|---|---|
| Missing required source/schema | Fail affected/full run before fitting; list expected signature. |
| Unknown extra CSV | Warn and ignore by default; strict mode fails. |
| Contract/leakage error | Fail closed and retain audit evidence. |
| Candidate training failure | Mark component failed; full default run fails, explicitly selected independent components may finish with partial status. |
| XGBoost missing | Full default run fails with install guidance; no silent omission. |
| Process interruption | Retain phase outputs and failure state; resume verifies hashes before reuse. |
| Metrics below gate | Publish evaluated candidate report but do not promote component. |
| Artifact incompatible/corrupt | Backend load fails fast and may select last known compatible promoted version. |

## Performance and capacity

Current scale is 48,816 rows total. **[E]** Optimize for correctness and local CPU use,
not distributed infrastructure. Default peak memory target is <2 GB; end-to-end target
is <=10 minutes on the documented machine; inference p95 target is <50 ms/interval in
batch replay. Reports record the exact host so results remain interpretable.

## Observability

- Structured console/file logs: run/component/phase, counts, elapsed time, warnings,
  gate outcome; no consumer number.
- Metrics: rows accepted/rejected, null/range/cadence findings, split sizes, fit time,
  candidate metrics, selected model, event metrics, load/inference latency.
- No external alerting in this scope. A failed exit code and `FAILED` marker are the
  automation boundary.

## Compatibility

Support the project-locked Python version on Linux. Store versions of pandas, NumPy,
scikit-learn, XGBoost, PyArrow, and joblib. Artifacts are compatible only within the
declared environment range; incompatibility causes explicit failure, never best-effort
deserialization.

## Release and rollback

1. Execute clean audit and default run.
2. Review acceptance evidence and model cards.
3. Promote an eligible candidate by atomic local pointer update.
4. Backend loads by manifest, never by newest modification time.
5. Rollback points `current` to a prior checksum-valid promoted run.
6. Raw data and past runs remain untouched.

## Test boundaries

- Unit: parsing, contracts, time localization, lag/rolling causality, metrics, rules,
  serialization validation, path and identifier handling.
- Integration: each real source through adapter; full dry run; small deterministic fit;
  interrupted/resumed run; promote/rollback.
- Regression: observed source inventory, known audit findings, feature schema, split
  membership, seasonal-naive outputs, injected truth generation.
- Performance: full CPU training and batch inference.
- Tests do not assert a complex model must win; they assert the selection policy is
  applied honestly.

## Implementation phases

| Phase | Outcome | Key work | Exit evidence |
|---|---|---|---|
| P0 | Reproducible Python foundation | Package, locked environment, config/schema types, run ID/state, logging | Clean install; CLI help; deterministic config test |
| P1 | Inventory and audits | Source matching, hashes, quality/leakage findings, audit report | All three sources recognized; raw hashes unchanged |
| P2 | Canonical data and splits | Adapters, derived tables, timezone policy, split manifests | Contract tests; exact split counts/hashes |
| P3 | Causal features and baselines | Allowlisted features, mutation test, seasonal-naive | No-future-data proof; baseline report |
| P4 | Forecast candidates | RF/XGBoost, bounded tuning, selection rule, packaging | Comparable validation/test metrics; selected artifact |
| P5 | Interval anomaly path | Residuals, Isolation Forest, rules, fusion/hysteresis | Explainable facts for clean replay |
| P6 | Evaluation paths | Event injection and labelled-home evaluation | Truth manifests and metric reports |
| P7 | Daily integrity benchmark | Probes, ablations, baselines/candidates, gate verdict | Exported rules/probes and promotion decision |
| P8 | Artifact operations | Manifest/model card validator, inference loader, promotion/rollback/resume | End-to-end, corruption, rollback tests |
| P9 | Acceptance hardening | Runtime/latency, clean reruns, docs and limitations | Completed acceptance matrix |

Implementation must proceed in dependency order P0→P3, then P4/P7 may be independent;
P5 depends on P4, P6 depends on P3/P5, and P8/P9 integrate all outputs.

## Alternatives considered

| Alternative | Decision |
|---|---|
| Concatenate all CSVs and train one classifier | Rejected: incompatible cadence, semantics, and target availability. |
| Train only XGBoost | Rejected: no baseline discipline or simplest-winner policy. |
| Random row split | Rejected: future and household leakage. |
| Use source expected/deviation fields | Rejected for deployable daily model pending label provenance. |
| Train during Django startup/request | Rejected: slow, irreproducible, and operationally unsafe. |
| MLflow/cloud registry now | Deferred: unnecessary for hackathon scale; local immutable manifests satisfy scope. |

## Blocked technical issues

None block implementation after specification approval. Final estimator and numeric
thresholds remain evidence-driven outputs. Exact backend package alignment can be
adjusted before P0 if application scaffolding lands first, without changing contracts.

## Technical decision log

| ID | Decision | Alternatives | Rationale | Related FRs |
|---|---|---|---|---|
| TD-001 | Schema-signature discovery with configured source IDs | Filename-only; arbitrary auto-inference | Detects renames while rejecting ambiguity | FR-001–FR-002 |
| TD-002 | Allowlisted causal features and separate evaluation tables | Drop known targets late | Prevents accidental leakage by construction | FR-007–FR-009 |
| TD-003 | Frozen temporal primary plus group secondary splits | Random rows | Measures intended generalization modes | FR-009, FR-014 |
| TD-004 | Local immutable run registry and atomic promotion pointer | Overwrite `model.pkl`; cloud registry | Auditable, rollback-safe, scope-appropriate | FR-016–FR-018 |
| TD-005 | 5% global improvement plus per-meter guardrail | Highest global score wins | Makes complexity earn its place and limits household regressions | FR-011 |

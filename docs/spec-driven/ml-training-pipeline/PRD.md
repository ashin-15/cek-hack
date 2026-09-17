# Energy Intelligence ML Training Pipeline — Product Requirements

Status: **Draft**
Owner: Project team
Last updated: 2026-09-17
Approval: **Pending**

Evidence tags follow `docs/research/README.md`: **[E]** observed evidence,
**[I]** engineering inference, and **[X]** proposed extension.
Unless explicitly tagged otherwise, every normative requirement and target in this
draft is a proposed extension **[X]**.

## Problem and context

The project has three CSV datasets under `data/`, but they differ in cadence,
schema, provenance, target labels, and safe uses. **[E: local dataset audit]** A
single generic fit over concatenated rows would mix incompatible observations and
create target leakage. **[I]** The product needs a reproducible offline ML pipeline
that accepts the repository's `data/` directory, validates and fingerprints every
source, routes each known schema to its permitted model task, evaluates candidates
without future-data or household leakage, and emits deployable versioned artifacts.
**[X]**

The pipeline implements the accepted boundary in
`docs/research/10_workflow_decisions.md`: ML predicts and detects; deterministic
services calculate; the LLM only explains supplied facts. It does not implement
billing, recommendations, the web UI, or live inference serving.

## Users and stakeholders

| Actor | Need |
|---|---|
| ML developer | Run one documented command against `data/` and obtain reproducible artifacts and reports. |
| Backend developer | Load an artifact through a stable inference contract without recreating preprocessing. |
| Demo operator | Know which artifact is approved and whether a safe precomputed fallback exists. |
| Judge/reviewer | Inspect data provenance, leakage controls, splits, metrics, limitations, and evidence. |
| Product owner | Prevent synthetic/community results from being described as field validation. |

## Product goals

1. Turn the current `data/` directory into validated, task-specific training and
   evaluation inputs without modifying source CSV files. **[X]**
2. Produce an interval expected-load model and explainable anomaly outputs for the
   primary smart-meter replay path. **[X]**
3. Evaluate labelled anomaly/wastage fixtures behind explicit leakage and
   provenance gates. **[X]**
4. Make every accepted artifact reproducible from source fingerprints, code,
   configuration, split policy, and random seeds. **[I]**
5. Expose enough evidence to support the dashboard's `Model estimate`,
   `Simulated`, and provenance disclosures. **[X]**

## Success metrics

| Metric | Baseline | Target | Measurement source |
|---|---:|---:|---|
| Recognized dataset coverage | No executable pipeline | All 3 committed CSV schemas audited and routed | Run manifest and audit report |
| Raw-data mutations | Not controlled by code | 0 source-byte changes | Pre/post SHA-256 comparison |
| Reproducibility | No run contract | Same inputs/config/seed produce identical split membership and equivalent metrics within documented numeric tolerance | Two clean reruns |
| Forecast selection | No trained artifact | Frozen validation rule selects the simplest qualifying candidate, or retains seasonal-naive; the locked test is then reported once without reselection | Selection record plus per-meter/global MAE, RMSE, sMAPE |
| Synthetic event evaluation | No unified report | Event precision, recall, F1, delay, PR-AUC, and clean false-alert rate reported by event type | Injection benchmark report |
| Leakage violations | Manual review only | 0 forbidden columns in fitted feature schemas | Automated leakage tests + artifact schema |
| Artifact traceability | No artifact contract | 100% of published artifacts include source hashes, code revision, config hash, feature schema, split, seed, metrics, limitations | Model-card validator |
| CPU training runtime | Unknown | Complete default pipeline in <=10 minutes on the documented development machine, excluding optional XGBoost installation time | Timed acceptance run |
| Batch inference latency | Unknown | p95 <50 ms per interval on documented CPU batch replay | Benchmark report |

Metrics on synthetic or undocumented community data are prototype evidence only;
they are not live-household accuracy claims. **[I]**

## User flows

### UF-01 — Train the default bundle

1. The developer invokes the training command with `--data-dir data`.
2. The system inventories files, identifies supported schemas, hashes raw bytes,
   and runs quality and leakage gates.
3. The system creates canonical derived data outside the raw source files.
4. Each dataset is routed only to its approved task.
5. Candidate models are trained and compared on frozen splits.
6. The system publishes an immutable run directory with artifacts, metrics,
   model cards, and a machine-readable manifest.
7. A non-zero exit indicates a blocking contract, leakage, or acceptance failure.

### UF-02 — Train one component

The developer selects `forecast`, `interval-anomaly`, `daily-benchmark`, or
`labelled-fixture-eval`. The system still audits all files required by that component
and records skipped components and reasons.

### UF-03 — Inspect or reproduce a run

The reviewer opens the run manifest and model card, verifies the source and config
hashes, reads split and feature definitions, and reruns the recorded command.

### UF-04 — Load for inference

The backend loads a promoted artifact, checks its manifest and feature schema, and
receives a typed prediction with model/version/provenance fields. Training never
runs during application startup or an API request.

## Functional requirements

| FR ID | Requirement | Priority | Status | Notes |
|---|---|---|---|---|
| FR-001 | The offline runner shall accept a configurable directory, defaulting to repository `data/`, and inventory supported CSV files without relying on filename alone. | Must | Draft | Schema signature plus configured source ID. |
| FR-002 | The runner shall recognize the three committed schemas, record SHA-256/size/row count/column set, and reject ambiguous schema matches. | Must | Draft | Current observed hashes belong in the audit report, not hardcoded validation logic. |
| FR-003 | The pipeline shall treat source files as immutable and write canonical tables only under a configured derived-data/run location. | Must | Draft | Raw pre/post hashes must match. |
| FR-004 | Each adapter shall enforce documented field mappings, types, units, timestamps, uniqueness, cadence, missing-value rules, physical consistency checks, and provenance. | Must | Draft | Rules vary by schema. |
| FR-005 | The pipeline shall route the 12-meter 15-minute dataset to forecasting, residual/outlier detection, electrical indicator rules, and synthetic event evaluation. | Must | Draft | Primary product path. |
| FR-006 | The daily 360-home dataset shall remain isolated behind a label-integrity gate and shall never contribute suspected proxy or missingness features to deployable models. | Must | Draft | Missing actual energy is a data-quality case. |
| FR-007 | The labelled single-home 15-minute dataset shall be used for held-out anomaly/wastage/appliance evaluation and safety replay facts; target, appliance-ground-truth, ageing, safety, billing-running-total, and future-derived fields shall not enter forecast/anomaly inputs. | Must | Draft | Safety labels are not inferred from aggregate usage. |
| FR-008 | All temporal features shall be causal, with imputation, encoding, scaling, and feature selection fitted only on training partitions. | Must | Draft | Automated future-mutation test required. |
| FR-009 | Splits shall be frozen before fitting or event injection and shall prevent future-to-past and household leakage. | Must | Draft | Exact policies owned by technical design. |
| FR-010 | The forecast bake-off shall compare seasonal-naive, Random Forest, and XGBoost when available using identical eligible rows and splits. | Must | Draft | If XGBoost is unavailable, fail the full default run; component mode may explicitly skip it. |
| FR-011 | The pipeline shall select the simplest forecast candidate that satisfies the declared improvement rule; otherwise it shall retain seasonal-naive. | Must | Draft | Avoid complexity without measured benefit. |
| FR-012 | The primary anomaly output shall combine forecast residual evidence, an Isolation Forest score, and separate deterministic rule flags while preserving each component in the result. | Must | Draft | Fusion weights configurable and reported. |
| FR-013 | Synthetic event injection shall operate only on post-split copies, use fixed seeds, preserve a truth table, and never alter raw/training rows. | Must | Draft | Results labelled synthetic benchmark. |
| FR-014 | The daily labelled gate shall run proxy ablation, single-feature probes, shallow-tree rule extraction, temporal evaluation, and grouped household evaluation before any classifier can be promoted. | Must | Draft | Gate may reject ML deployment. |
| FR-015 | The pipeline shall calculate and persist task-appropriate metrics globally and by meter/event/class, including uncertainty or seed variability where applicable. | Must | Draft | No accuracy-only reporting for imbalance. |
| FR-016 | Every artifact shall package preprocessing, ordered feature schema, estimator or baseline state, thresholds, training metadata, compatibility versions, and a model card. | Must | Draft | Artifact is rejected if incomplete. |
| FR-017 | Runs shall be immutable, uniquely identified, resumable at phase boundaries, and shall never silently overwrite a prior artifact. | Must | Draft | Failed runs retain diagnostics. |
| FR-018 | Promotion shall be explicit: passing training creates a candidate; only a separate promote action updates the local `current` pointer after acceptance gates pass. | Should | Draft | Rollback selects an earlier immutable run. |
| FR-019 | The inference library shall validate feature compatibility and return observed value, expected value, residual, component scores/flags, artifact version, and dataset provenance. | Must | Draft | LLM-ready facts, not prose. |
| FR-020 | Logs and reports shall redact or avoid direct consumer identifiers while retaining pseudonymous household IDs needed for evaluation. | Must | Draft | `consumer_number` never becomes a model feature. |
| FR-021 | The pipeline shall provide deterministic dry-run/audit and component-select modes plus human-readable error messages and non-zero exit codes. | Should | Draft | Supports fast diagnosis. |
| FR-022 | Documentation shall distinguish observed dataset facts [E], engineering choices [I], and proposed behavior [X], and prohibit live-KSEB/fault-diagnosis claims. | Must | Draft | Applies to model cards and reports. |

## Business rules

1. **Dataset isolation:** incompatible cadence and semantics must not be flattened
   into one training table. **[I]**
2. **Evidence hierarchy:** raw observed fields and explicit source labels are
   reported as dataset evidence; model outputs are estimates; injected events and
   supplied synthetic labels are simulated evidence. **[I]**
3. **No label leakage:** a target or a field derived from the target, future, source
   expected value, source deviation, or ground truth cannot be a deployable input.
   **[I]**
4. **Fail closed:** missing required sources, ambiguous schemas, invalid time order,
   duplicate keys, incompatible artifacts, or leakage findings block publication.
   **[I]**
5. **Selection before test:** thresholds and hyperparameters are chosen on training
   and validation data. The locked test set is evaluated only for the final candidate.
   **[I]**
6. **No automatic diagnosis:** interval V/I/PF rules are indicators only. Aggregate
   kWh cannot establish leakage, earthing, arc, or loose-connection faults.
   **[I]**
7. **No automatic retraining:** adding a file to `data/` does not retrain production;
   a developer starts an explicit offline run. **[I]**

## Data lifecycle

`data/*.csv` (read-only) → inventory/fingerprints → audit → canonical versioned
tables → frozen split assignments → fit/tune → locked evaluation → immutable candidate
run → explicit promotion → backend load → rollback by pointer change.

Retention defaults: keep all manifests/model cards/metrics; derived tables and model
binaries are reproducible and may be pruned only by an explicit maintenance command.
Raw project CSVs are never deleted by the pipeline.

## Scope

### In scope

- Offline ingestion and audit of all three current `data/*.csv` schemas.
- Forecast candidate bake-off, residual anomaly scoring, Isolation Forest, rule
  flags, event injection, leakage-gated daily benchmark, and labelled-fixture
  evaluation.
- Versioned derived data, artifacts, manifests, reports, model cards, local
  promotion/rollback, and an inference library contract.
- Tests and benchmarks necessary to prove the above.

### Out of scope

- Django endpoints, PostgreSQL persistence, React screens, billing/tariffs,
  optimization, Groq prompting, deployment, and live KSEB integration.
- Automated scheduling/retraining, distributed training, GPU requirements, and a
  general-purpose user CSV upload feature.
- Training a definitive electrical-fault, leakage, earthing, loose-connection,
  deep-NILM, appliance-ageing, or remaining-useful-life model.

### Non-goals

- Maximizing a single leaderboard metric.
- Treating all three datasets as samples from one population.
- Claiming validation on live Kerala households.
- Reproducing label-generating rules with a complex classifier.

## Assumptions

| ID | Assumption | Risk | Validation plan | Status |
|---|---|---|---|---|
| ASM-001 | CPU-only local training is sufficient for current data volume. **[I]** | Low | Timed end-to-end run. | Proposed |
| ASM-002 | The three current schemas remain the required default bundle. **[E/X]** | Medium | Manifest version and contract tests; unknown schemas fail with guidance. | Proposed |
| ASM-003 | Asia/Kolkata is the business timezone; naive timestamps in the single-home fixture are localized, not converted. **[I]** | Medium | Timestamp/cadence tests and explicit adapter metadata. | Proposed |
| ASM-004 | XGBoost is an installable project dependency. **[I]** | Low | Environment lock and clean-install training test. | Proposed |
| ASM-005 | Exact promotion thresholds may be configured after baseline measurements, but evidence fields and no-regression rules are fixed now. **[I]** | Medium | Record thresholds in frozen config before locked-test evaluation. | Proposed |

## Open product decisions

No unresolved decision blocks this specification. The accepted workflow already fixes
the user, evidence policy, offline-training boundary, model families, and dataset roles.
Final model winners and thresholds are outputs of the frozen evaluation process, not
up-front product choices.

## Decision log

| Decision ID | Decision | Rationale | Decider/date | Impacted FRs |
|---|---|---|---|---|
| PD-001 | `data/` is an input bundle routed by schema; files are not concatenated. | Cadence, labels, and provenance are incompatible. | Existing research decision, 2026-09-17 | FR-001–FR-007 |
| PD-002 | Training is explicit and offline. | Avoid request latency, nondeterminism, and accidental retraining. | Existing accepted workflow, 2026-09-17 | FR-017–FR-019 |
| PD-003 | Primary product model is expected-load plus explainable anomaly components; the daily classifier is conditional. | Matches product data and contains label-leakage risk. | Existing research decision, 2026-09-17 | FR-010–FR-015 |
| PD-004 | Passing a training run creates a candidate, not an automatically active model. | Separates generation from acceptance and supports rollback. | Draft recommendation, pending approval | FR-018 |

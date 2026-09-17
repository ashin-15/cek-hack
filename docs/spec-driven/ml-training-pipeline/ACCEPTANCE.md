# Energy Intelligence ML Training Pipeline — Acceptance Contract

Status: **Draft**
Based on PRD/Technical Design: 2026-09-17 drafts
Approval: **Pending**

Evidence tags follow `docs/research/README.md`. All acceptance conditions in this
draft are proposed extensions **[X]**.

## Scope boundaries

### In scope

Offline dataset inventory/audit, canonicalization, leakage-safe splitting/features,
forecast and anomaly components, controlled evaluation, immutable artifacts/model
cards, promotion/rollback, and the inference library contract.

### Out of scope

Web/API/UI implementation, database/deployment, tariffs, optimization, Groq, live KSEB
data, user CSV uploads, automated retraining, and production monitoring.

### Non-goals

Field-validation claims, definitive fault diagnosis, deep NILM, appliance-ageing/RUL,
or forcing a learned model to outperform a simple baseline.

### Deferred

Cloud model registry, scheduled retraining, new arbitrary schemas, final production
deployment integration, and appliance classifier implementation beyond evaluation data
boundaries.

### Assumptions

CPU-local execution; current three-schema default bundle; Asia/Kolkata localization for
naive fixture timestamps; locked project dependencies.

### Release blockers

Any raw mutation, schema ambiguity, target/future/household leakage, missing required
artifact metadata, unlocked test-set tuning, corrupt/incompatible promoted artifact,
unexplained anomaly output, or field-validation/fault-diagnosis claim is blocking.

### Definition of done

All blocking criteria below pass on a clean checkout; evidence is stored under one
immutable run; documents and model cards state provenance and limitations; the selected
artifact can be loaded, scored, promoted, and rolled back without training in the
application path.

## Acceptance criteria

### AC-001 — Input bundle discovery is deterministic
- Related FRs: FR-001, FR-002, FR-021
- Blocking: Yes
- Scenario: The runner receives the current `data/` directory.
- Action/event: Execute dry-run twice with identical config.
- Expected result: Exactly the three supported CSV schemas are identified once each;
  descriptors and hashes match; README/non-CSV files are ignored; ordering is stable.
- Required evidence: CLI transcript, two `SourceDescriptor` JSON outputs, automated test.

### AC-002 — Ambiguous or missing sources fail closed
- Related FRs: FR-001, FR-002, FR-021
- Blocking: Yes
- Scenario: A required file is missing or a fixture ambiguously matches adapters.
- Action/event: Execute the required component/full run.
- Expected result: Fitting does not start; exit is non-zero; error names the missing or
  ambiguous schema and remediation.
- Required evidence: Integration tests and phase log.

### AC-003 — Raw training data remains byte-identical
- Related FRs: FR-003, FR-013, FR-017
- Blocking: Yes
- Scenario: Full audit, training, injection, and evaluation run.
- Action/event: Compare every raw CSV SHA-256 before and after.
- Expected result: All hashes are unchanged; every generated file is outside raw paths.
- Required evidence: Pre/post manifest and path assertion test.

### AC-004 — Source contracts and known quality findings are enforced
- Related FRs: FR-004–FR-007
- Blocking: Yes
- Scenario: Run adapters on current data and malformed fixtures.
- Action/event: Validate types, units, keys, cadence, nulls, ranges, timezones, and formula residuals.
- Expected result: Current known facts are reported; duplicates, negative kWh, invalid
  cadence, non-monotonic cumulative energy, and unparseable units are rejected; daily
  missing actual-energy rows are quarantined, not treated as energy anomalies.
- Required evidence: Audit report plus parameterized unit/integration tests.

### AC-005 — Dataset roles stay isolated
- Related FRs: FR-005–FR-007
- Blocking: Yes
- Scenario: Full default run.
- Action/event: Inspect lineage and split/feature manifests.
- Expected result: No flat cross-cadence merge exists; each source appears only in its
  permitted task/evaluation role; safety replay data never trains an aggregate detector.
- Required evidence: Lineage graph/report and schema assertions.

### AC-006 — Feature generation is causal and allowlisted
- Related FRs: FR-006–FR-009
- Blocking: Yes
- Scenario: Build features, then mutate source values strictly after a chosen cutoff.
- Action/event: Rebuild features up to the cutoff and inspect ordered schemas.
- Expected result: Earlier features are identical; no target, future-derived, source
  expected/deviation, ground-truth, running-bill, direct consumer, or prohibited field appears.
- Required evidence: Future-mutation test, leakage scanner output, feature schemas.

### AC-007 — Split membership is frozen and leakage-safe
- Related FRs: FR-009, FR-013, FR-014
- Blocking: Yes
- Scenario: Generate primary/secondary splits twice.
- Action/event: Compare membership hashes and household/time boundaries.
- Expected result: Hashes match; temporal partitions are ordered; group test households
  do not occur in fit data; injection occurs only after split on test copies.
- Required evidence: Split manifests and automated overlap tests.

### AC-008 — Forecast bake-off is fair
- Related FRs: FR-010, FR-011, FR-015
- Blocking: Yes
- Scenario: Train seasonal-naive, RF, and XGBoost candidates.
- Action/event: Compare their manifests and evaluation tables.
- Expected result: Candidates use the same eligible rows/splits/metric definitions;
  tuning uses no locked-test results; per-meter and global metrics are present.
- Required evidence: Candidate manifests, tuning log, metric report.

### AC-009 — Forecast selection policy chooses honestly
- Related FRs: FR-011
- Blocking: Yes
- Scenario: Exercise synthetic metric tables covering win, tie, global win with excessive
  meter regressions, and no-win cases; then run on project data.
- Action/event: Apply selection function.
- Expected result: Function exactly applies the 5%/per-meter/tie rules; project winner
  is justified; seasonal-naive remains valid if learned candidates do not qualify.
- Required evidence: Unit tests and selection report.

### AC-010 — Anomaly facts are explainable
- Related FRs: FR-012, FR-019
- Blocking: Yes
- Scenario: Score clean and anomalous replay intervals.
- Action/event: Inspect inference results and event transitions.
- Expected result: Every score contains observed/expected/residual, residual z,
  Isolation Forest score, independent rule flags, fused score, event state, version,
  and provenance; gaps and post-gap recovery follow policy.
- Required evidence: Golden response fixtures and replay tests.

### AC-011 — Injection benchmark is reproducible and labelled honestly
- Related FRs: FR-013, FR-015, FR-022
- Blocking: Yes
- Scenario: Generate every configured event type twice with the same seed and once with
  a different seed.
- Action/event: Compare truth hashes and run evaluation.
- Expected result: Same-seed truth is identical; different seed changes placements;
  raw/train rows remain untouched; required event/interval metrics and clean false-alert
  rate are present; report says `synthetic benchmark`.
- Required evidence: Injection/truth manifests, tests, benchmark report.

### AC-012 — Daily label-integrity gate controls promotion
- Related FRs: FR-006, FR-014, FR-015
- Blocking: Yes
- Scenario: Run daily benchmark on current source and controlled leaky fixtures.
- Action/event: Execute exclusions, proxy ablation, probes, shallow trees, temporal and group tests.
- Expected result: 900 missing-actual rows are excluded from energy-model evaluation;
  suspected proxies are absent from deployable features; rule/proxy-driven results
  cause classifier rejection; any eligible classifier has evidence from both tests.
- Required evidence: Gate JSON, exported tree/probes, ablation metrics, model card.

### AC-013 — Labelled-home evaluation preserves semantics
- Related FRs: FR-007, FR-015
- Blocking: Yes
- Scenario: Evaluate on the locked final ten days.
- Action/event: Produce anomaly, waste, and contextual-spike reports.
- Expected result: Metrics distinguish anomaly from avoidable waste; guest spikes remain
  context-explained; no safety/ageing/ground-truth field enters fitted inputs.
- Required evidence: Confusion matrices, event metrics, feature lineage test.

### AC-014 — Artifact packages are complete and tamper-evident
- Related FRs: FR-016, FR-017
- Blocking: Yes
- Scenario: Validate a successful run and then alter/remove each required artifact in fixtures.
- Action/event: Run artifact validator.
- Expected result: Valid package passes; missing metadata or checksum changes fail;
  model card includes sources, splits, features, metrics, limitations, and non-live-KSEB statement.
- Required evidence: Validator tests and complete sample manifest/model card.

### AC-015 — Runs are recoverable and never overwrite history
- Related FRs: FR-017, FR-021
- Blocking: Yes
- Scenario: Interrupt after canonicalization, resume, and launch an identical fresh run.
- Action/event: Inspect state and outputs.
- Expected result: Resume verifies and reuses only valid outputs; attempts have distinct
  IDs/history; prior run bytes remain unchanged; failure evidence is retained.
- Required evidence: Interruption/resume integration test and directory checksums.

### AC-016 — Promotion and rollback are explicit and atomic
- Related FRs: FR-018
- Blocking: Yes
- Scenario: One eligible, one ineligible, and two eligible candidate runs exist.
- Action/event: Attempt promotions, simulate interrupted pointer update, then roll back.
- Expected result: Ineligible candidate cannot be promoted; interruption leaves one
  valid pointer; rollback selects the prior checksum-valid run without deletion.
- Required evidence: Promotion/rollback tests and pointer audit log.

### AC-017 — Inference rejects incompatible inputs/artifacts
- Related FRs: FR-016, FR-019
- Blocking: Yes
- Scenario: Load valid, corrupt, version-incompatible, and feature-incompatible packages.
- Action/event: Initialize loader and score a record.
- Expected result: Valid package returns typed facts; all incompatible cases fail fast
  with actionable errors and do not silently reorder or invent features.
- Required evidence: Loader contract tests.

### AC-018 — Identifier and path protections hold
- Related FRs: FR-020
- Blocking: Yes
- Scenario: Use fixtures with consumer IDs, hostile report strings, symlinks, and traversal paths.
- Action/event: Run audit/reporting/output resolution.
- Expected result: Consumer numbers are absent from features/logs; report cells are
  escaped; writes cannot escape configured roots; symlink/traversal attempts fail.
- Required evidence: Security-focused unit/integration tests and log scan.

### AC-019 — Runtime and latency targets are measured
- Related FRs: FR-015, FR-019
- Blocking: No
- Scenario: Clean full run and batch replay on the documented development host.
- Action/event: Time execution and inference after warm-up.
- Expected result: Default target is <=10 minutes, peak memory <2 GB, p95 <50 ms per
  interval; any miss is recorded with a profile and requires an explicit waiver before
  demo promotion.
- Required evidence: Benchmark command, host metadata, time/memory/latency report.

### AC-020 — Runs are reproducible within declared tolerance
- Related FRs: FR-015–FR-017
- Blocking: Yes
- Scenario: Two clean runs with same sources/config/environment/seed.
- Action/event: Compare splits, schemas, selections, predictions, and metrics.
- Expected result: Split/feature/selection hashes match; deterministic outputs match;
  numeric outputs meet declared tolerance; source/config/code provenance is identical.
- Required evidence: Reproducibility comparison report.

### AC-021 — Offline and application boundaries are enforced
- Related FRs: FR-017–FR-019
- Blocking: Yes
- Scenario: Load/score through inference library with training functions instrumented to fail if called.
- Action/event: Initialize and score.
- Expected result: No training, tuning, raw CSV scan, or network call occurs.
- Required evidence: Boundary integration test.

### AC-022 — Evidence language is accurate
- Related FRs: FR-022
- Blocking: Yes
- Scenario: Scan generated reports/model cards and inspect representative UI-ready facts.
- Action/event: Run terminology lint and manual review.
- Expected result: Synthetic/community provenance is visible; no live-KSEB validation or
  definitive leakage/earthing/loose-connection claim appears; rule flags are indicators.
- Required evidence: Lint output and signed manual review checklist.

## Coverage map

| FR ID | AC IDs |
|---|---|
| FR-001–FR-002 | AC-001, AC-002 |
| FR-003 | AC-003 |
| FR-004 | AC-004 |
| FR-005–FR-007 | AC-004, AC-005, AC-006, AC-012, AC-013 |
| FR-008–FR-009 | AC-006, AC-007 |
| FR-010–FR-011 | AC-008, AC-009 |
| FR-012–FR-013 | AC-010, AC-011 |
| FR-014–FR-015 | AC-012, AC-013, AC-019, AC-020 |
| FR-016–FR-018 | AC-014–AC-017, AC-020 |
| FR-019 | AC-010, AC-017, AC-019, AC-021 |
| FR-020 | AC-018 |
| FR-021 | AC-001, AC-002, AC-015 |
| FR-022 | AC-011, AC-022 |

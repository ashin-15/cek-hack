# Graph Report - cek-hack  (2026-09-17)

## Corpus Check
- 57 files · ~54,123 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 491 nodes · 611 edges · 33 communities (29 shown, 4 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e67b8aad`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- research/README.md
- Energy Intelligence ML Training Pipeline — Technical Design and Implementation Plan
- Acceptance criteria
- 09 — Dataset-Verified Model Implementation Plan
- FINAL WORKFLOW — AI Household Energy Intelligence (Hackathon MVP)
- 08 — Abnormal-Usage Model: Plan & Specification
- Energy Intelligence ML Training Pipeline — Product Requirements
- extract_interval_features
- Paper [B] — AI-Enabled Smart Energy Optimization System (IJST 2026)
- inventory_datasets
- Electricity Demand Forecasting In Kerala Using Machine Learning Models
- Decision Record — Finalized MVP Workflow
- load_smart_meter_15min
- schemas.py
- test_e2e_pipeline.py
- evaluate_event_detection
- 02 — System Capabilities (Functional Scope)
- create_smart_meter_splits
- 05 — AI / ML Model Mapping per Capability
- audit_datasets.py
- Predictive_Analytics_for_Energy_Efficiency_Leverag.md
- run.py
- SDG 7 — Affordable and Clean Energy
- test_models.py
- Project Context for Agents
- Energy Intelligence ML Training Pipeline — Delivery Loop
- Household Energy Intelligence Dataset (`ai_energy_intelligence_dataset.csv`)
- cek-hack
- Data Audit and Verification Report
- promote.py
- backend/__init__.py
- backend/ml/__init__.py

## God Nodes (most connected - your core abstractions)
1. `Energy Intelligence ML Training Pipeline — Technical Design and Implementation Plan` - 25 edges
2. `Acceptance criteria` - 23 edges
3. `load_smart_meter_15min()` - 19 edges
4. `run_pipeline()` - 17 edges
5. `FINAL WORKFLOW — AI Household Energy Intelligence (Hackathon MVP)` - 17 edges
6. `Electricity Demand Forecasting In Kerala Using Machine Learning Models` - 16 edges
7. `08 — Abnormal-Usage Model: Plan & Specification` - 16 edges
8. `inventory_datasets()` - 13 edges
9. `02 — System Capabilities (Functional Scope)` - 13 edges
10. `09 — Dataset-Verified Model Implementation Plan` - 13 edges

## Surprising Connections (you probably didn't know these)
- `test_daily_abnormal_adapter_and_audit()` --calls--> `load_daily_abnormal()`  [EXTRACTED]
  tests/ml/test_adapters_and_quality.py → backend/ml/adapters/daily_abnormal.py
- `test_labelled_home_adapter_isolation()` --calls--> `load_labelled_home_15min()`  [EXTRACTED]
  tests/ml/test_adapters_and_quality.py → backend/ml/adapters/labelled_home_15min.py
- `main()` --calls--> `load_smart_meter_15min()`  [EXTRACTED]
  scripts/audit_datasets.py → backend/ml/adapters/smart_meter_15min.py
- `test_inference_engine_scoring()` --calls--> `load_smart_meter_15min()`  [EXTRACTED]
  tests/ml/test_e2e_pipeline.py → backend/ml/adapters/smart_meter_15min.py
- `test_injection_benchmark()` --calls--> `load_smart_meter_15min()`  [EXTRACTED]
  tests/ml/test_injection.py → backend/ml/adapters/smart_meter_15min.py

## Import Cycles
- None detected.

## Communities (33 total, 4 thin omitted)

### Community 0 - "research/README.md"
Cohesion: 0.04
Nodes (38): 03 — Electrical Fault & Appliance-Condition Detectability, 1. Loose electrical connections, 2. Earthing problems, 3. Leakage / abnormal current behaviour, 4. Voltage / current abnormalities, 5. Old / degrading appliances, 6. Inefficient appliances, Data tiers used in this file (+30 more)

### Community 1 - "Energy Intelligence ML Training Pipeline — Technical Design and Implementation Plan"
Cohesion: 0.05
Nodes (43): Alternatives considered, Artifact and manifest contract, Automated leakage guard, Blocked technical issues, Canonical interval record, Compatibility, Concurrency, consistency, and idempotency, Current system state (+35 more)

### Community 2 - "Acceptance criteria"
Cohesion: 0.06
Nodes (33): AC-001 — Input bundle discovery is deterministic, AC-002 — Ambiguous or missing sources fail closed, AC-003 — Raw training data remains byte-identical, AC-004 — Source contracts and known quality findings are enforced, AC-005 — Dataset roles stay isolated, AC-006 — Feature generation is causal and allowlisted, AC-007 — Split membership is frozen and leakage-safe, AC-008 — Forecast bake-off is fair (+25 more)

### Community 3 - "09 — Dataset-Verified Model Implementation Plan"
Cohesion: 0.06
Nodes (30): 09 — Dataset-Verified Model Implementation Plan, 10. Phase 6 — Fusion, suppression, serving, and UI, 11. Delivery sequence and definition of done, 1. Verification record, 2. Target system and data flow, 3. Repository layout and artefacts, 4. Phase 0 — Reproducibility and data contracts, 5.1 Interval adapter (+22 more)

### Community 4 - "FINAL WORKFLOW — AI Household Energy Intelligence (Hackathon MVP)"
Cohesion: 0.06
Nodes (31): 0. Locked decisions, 10. LLM boundaries, 11. Architecture, 12. Implementation order, 13. Demo journey, 14. Deferred until implementation, 15. Build-ready prompt, 1. Conflict resolutions (do not re-litigate) (+23 more)

### Community 5 - "08 — Abnormal-Usage Model: Plan & Specification"
Cohesion: 0.07
Nodes (27): 08 — Abnormal-Usage Model: Plan & Specification, 0. Dataset audit — completed against the supplied CSV, 10. Execution plan, 11. Definition of done, 12. Risks, 13. Open questions (close in P0/P1), 1. Role of this dataset in the system, 2. Data contract & ingestion (+19 more)

### Community 6 - "Energy Intelligence ML Training Pipeline — Product Requirements"
Cohesion: 0.10
Nodes (20): Assumptions, Business rules, Data lifecycle, Decision log, Energy Intelligence ML Training Pipeline — Product Requirements, Functional requirements, In scope, Non-goals (+12 more)

### Community 7 - "extract_interval_features"
Cohesion: 0.18
Nodes (14): FeatureSchema, extract_interval_features(), DataFrame, Causal interval feature engineering for smart meter telemetry., Build causal features for interval consumption forecasting and anomaly…, assert_no_leakage(), Leakage detection and causal validation for feature sets and models., Return any forbidden columns found in the candidate feature list. (+6 more)

### Community 8 - "Paper [B] — AI-Enabled Smart Energy Optimization System (IJST 2026)"
Cohesion: 0.11
Nodes (18): 01 — Paper Evidence Audit, Cross-paper summary, Paper [A] — Electricity Demand Forecasting in Kerala using ML (CONIT 2023), Paper [B] — AI-Enabled Smart Energy Optimization System (IJST 2026), Paper [C] — Predictive Analytics for Energy Efficiency (Energies 2024), Reusable for us, Reusable for us, Reusable for us (+10 more)

### Community 9 - "inventory_datasets"
Cohesion: 0.20
Nodes (15): SourceDescriptor, compute_file_hash_and_rows(), inventory_datasets(), match_schema_signature(), Dataset discovery, inventorying, hashing, and schema signature matching., Compute SHA-256 hash, size in bytes, row count, and header columns., Match a column list against the signatures defined in contracts., Inventory and fingerprint all supported datasets in data_dir. (+7 more)

### Community 10 - "Electricity Demand Forecasting In Kerala Using Machine Learning Models"
Cohesion: 0.11
Nodes (17): _A. Evaluation of Performance_, Electricity Demand Forecasting In Kerala Using Machine Learning Models, _<mark>A. Linear Regression</mark>_, _<mark>B. Decision Tree</mark>_, _<mark>C. Random Forest</mark>_, _<mark>D. Support Vector Machine</mark>_, _<mark>E. K-Nearest Neighbors</mark>_, _<mark>F. ANN</mark>_ (+9 more)

### Community 11 - "Decision Record — Finalized MVP Workflow"
Cohesion: 0.11
Nodes (17): AI/ML boundary, Backend, Data and AI, Data and integration decisions, Decision Record — Finalized MVP Workflow, Feature evidence tiers, Frontend, Implementation recommendations (+9 more)

### Community 12 - "load_smart_meter_15min"
Cohesion: 0.15
Nodes (12): Adapter for Intelligent_abnormal_electricity_usage.csv., load_labelled_home_15min(), DataFrame, Adapter for ai_energy_intelligence_dataset.csv., Load ai_energy_intelligence_dataset.csv, emitting canonical telemetry and…, load_smart_meter_15min(), DataFrame, Adapter for synthetic_smart_meter_15min.csv. (+4 more)

### Community 13 - "schemas.py"
Cohesion: 0.24
Nodes (12): AnomalyFacts, AuditFinding, AuditReport, Typed data contracts and schemas for the ML pipeline., RunManifest, audit_daily_abnormal(), audit_smart_meter_15min(), DataFrame (+4 more)

### Community 14 - "test_e2e_pipeline.py"
Cohesion: 0.16
Nodes (10): EnergyIntelligenceInferenceEngine, DataFrame, Inference engine loading promoted model artifacts to score live/replayed…, Inference engine for real-time or batch interval scoring., Score a DataFrame of precomputed interval feature rows., End-to-end pipeline and inference engine tests., Verify that dry-run successfully inventories and validates datasets., Test full training run on project data and inference scoring. (+2 more)

### Community 15 - "evaluate_event_detection"
Cohesion: 0.16
Nodes (11): Any, inject_benchmark_events(), DataFrame, Controlled synthetic event injection for Phase 4 benchmarking., Inject reproducible synthetic events on a copy of the test frame., evaluate_event_detection(), DataFrame, Evaluation metrics for event detection and interval anomalies. (+3 more)

### Community 16 - "02 — System Capabilities (Functional Scope)"
Cohesion: 0.15
Nodes (13): 02 — System Capabilities (Functional Scope), 10. Appliance efficiency / ageing detection (T2/T3), 11. Electrical fault detection (T2/T3, mostly needs sensors), 12. Cross-cutting, 1. Energy consumption monitoring (T1), 2. Usage pattern analysis (T1), 3. Anomaly detection (T1), 4. Energy wastage detection (T1/T2) (+5 more)

### Community 17 - "create_smart_meter_splits"
Cohesion: 0.27
Nodes (9): SplitManifest, create_daily_splits(), create_smart_meter_splits(), DataFrame, Deterministic, leakage-safe temporal and group split generators., Generate temporal splits (train: 1-21, val: 22-24, test: 25-28) for 15-minute…, Generate temporal split for daily abnormal dataset (train: 1-24, test: 25-30)., Tests for AC-007: Deterministic splits and partition isolation. (+1 more)

### Community 18 - "05 — AI / ML Model Mapping per Capability"
Cohesion: 0.18
Nodes (10): 05 — AI / ML Model Mapping per Capability, 1. Consumption forecasting, 2. Anomaly detection, 3. Appliance identification / disaggregation, 4. Appliance efficiency estimation, 5. Fault detection (see file 03 for what is physically observable), 6. Energy optimisation, 7. Personalised recommendations (+2 more)

### Community 19 - "audit_datasets.py"
Cohesion: 0.33
Nodes (6): format_audit_markdown(), format_summary_markdown(), Report generators for data audit, model cards, and benchmark summaries., Format run summary into markdown., Format multiple dataset audit reports into markdown., main()

### Community 20 - "Predictive_Analytics_for_Energy_Efficiency_Leverag.md"
Cohesion: 0.22
Nodes (8): 1. Introduction, 2. Description of the Research Problem, 3. Description of Supervised Machine Learning Implementation, 4. Results of Simulation Studies, 5. Conclusions, Abbreviations, Predictive Analytics for Energy Efficiency: Leveraging Machine Learning to Optimize Household Energy Consumption, References

### Community 21 - "run.py"
Cohesion: 0.32
Nodes (5): load_daily_abnormal(), DataFrame, Load daily abnormal usage dataset, cleaning strings and quarantining missing-…, Offline ML training pipeline orchestrator., run_pipeline()

### Community 22 - "SDG 7 — Affordable and Clean Energy"
Cohesion: 0.29
Nodes (6): AI-Based Energy Consumption Intelligence & Optimization System, Core Objective, Problem Statement, SDG 7 — Affordable and Clean Energy, The Challenge, Why This Problem Matters

### Community 24 - "Project Context for Agents"
Cohesion: 0.40
Nodes (4): Contribution rules, Evidence discipline, Project Context for Agents, Where things live

### Community 25 - "Energy Intelligence ML Training Pipeline — Delivery Loop"
Cohesion: 0.40
Nodes (4): Current Loop — LOOP-002, Energy Intelligence ML Training Pipeline — Delivery Loop, LOOP-001, Prior loops

### Community 26 - "Household Energy Intelligence Dataset (`ai_energy_intelligence_dataset.csv`)"
Cohesion: 0.50
Nodes (3): Household Energy Intelligence Dataset (`ai_energy_intelligence_dataset.csv`), Overview, Schema & Field Descriptions

### Community 27 - "cek-hack"
Cohesion: 0.50
Nodes (3): cek-hack, Getting Started, License

### Community 28 - "Data Audit and Verification Report"
Cohesion: 0.50
Nodes (3): Data Audit and Verification Report, Dataset: `daily_abnormal_v1` — PASSED, Dataset: `smart_meter_15min_v1` — PASSED

## Knowledge Gaps
- **271 isolated node(s):** `Contribution rules`, `Where things live`, `Evidence discipline`, `Getting Started`, `License` (+266 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FINAL WORKFLOW — AI Household Energy Intelligence (Hackathon MVP)` connect `FINAL WORKFLOW — AI Household Energy Intelligence (Hackathon MVP)` to `research/README.md`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `08 — Abnormal-Usage Model: Plan & Specification` connect `08 — Abnormal-Usage Model: Plan & Specification` to `research/README.md`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **What connects `Contribution rules`, `Where things live`, `Evidence discipline` to the rest of the system?**
  _271 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `research/README.md` be split into smaller, more focused modules?**
  _Cohesion score 0.043478260869565216 - nodes in this community are weakly interconnected._
- **Should `Energy Intelligence ML Training Pipeline — Technical Design and Implementation Plan` be split into smaller, more focused modules?**
  _Cohesion score 0.045454545454545456 - nodes in this community are weakly interconnected._
- **Should `Acceptance criteria` be split into smaller, more focused modules?**
  _Cohesion score 0.058823529411764705 - nodes in this community are weakly interconnected._
- **Should `09 — Dataset-Verified Model Implementation Plan` be split into smaller, more focused modules?**
  _Cohesion score 0.06451612903225806 - nodes in this community are weakly interconnected._
# Graph Report - cek-hack  (2026-09-17)

## Corpus Check
- 93 files · ~69,928 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 669 nodes · 915 edges · 54 communities (46 shown, 8 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 12 edges (avg confidence: 0.72)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b3db762e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- 03 — Electrical Fault & Appliance-Condition Detectability
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
- run_pipeline
- evaluate_event_detection
- 02 — System Capabilities (Functional Scope)
- run.py
- 05 — AI / ML Model Mapping per Capability
- train.py
- Predictive_Analytics_for_Energy_Efficiency_Leverag.md
- billing.py
- SDG 7 — Affordable and Clean Energy
- test_models.py
- Project Context for Agents
- Energy Intelligence ML Training Pipeline — Delivery Loop
- data/README.md
- Dataset audit
- promote.py
- backend/__init__.py
- backend/ml/__init__.py
- package.json
- main.jsx
- test_advisor.py
- 07 — Proposed System Scope & Novelty
- Progress and AI handoff — Paranova
- 04 — Data Collection Approaches (India / Kerala context)
- 06 — Practical Feasibility Assessment
- 12 — Local MVP implementation record
- Research Index — AI-Based Household Energy Intelligence System
- Paranova — household energy intelligence
- 0001_initial.py
- energy/__init__.py
- dev.py
- paranova-energy

## God Nodes (most connected - your core abstractions)
1. `Energy Intelligence ML Training Pipeline — Technical Design and Implementation Plan` - 25 edges
2. `Acceptance criteria` - 23 edges
3. `main()` - 18 edges
4. `load_smart_meter_15min()` - 17 edges
5. `run_pipeline()` - 17 edges
6. `FINAL WORKFLOW — AI Household Energy Intelligence (Hackathon MVP)` - 17 edges
7. `Electricity Demand Forecasting In Kerala Using Machine Learning Models` - 16 edges
8. `08 — Abnormal-Usage Model: Plan & Specification` - 16 edges
9. `02 — System Capabilities (Functional Scope)` - 13 edges
10. `09 — Dataset-Verified Model Implementation Plan` - 13 edges

## Surprising Connections (you probably didn't know these)
- `FactsProvider` --uses--> `Snapshot`  [INFERRED]
  energy/provider.py → backend/api/models.py
- `ReplayProvider` --uses--> `Snapshot`  [INFERRED]
  energy/provider.py → backend/api/models.py
- `section()` --calls--> `forecast_from_artifact()`  [EXTRACTED]
  backend/api/views.py → energy/inference.py
- `test_labelled_home_adapter_isolation()` --calls--> `load_labelled_home_15min()`  [EXTRACTED]
  tests/ml/test_adapters_and_quality.py → backend/ml/adapters/labelled_home_15min.py
- `test_inference_engine_scoring()` --calls--> `load_smart_meter_15min()`  [EXTRACTED]
  tests/ml/test_e2e_pipeline.py → backend/ml/adapters/smart_meter_15min.py

## Import Cycles
- None detected.

## Communities (54 total, 8 thin omitted)

### Community 0 - "03 — Electrical Fault & Appliance-Condition Detectability"
Cohesion: 0.18
Nodes (10): 03 — Electrical Fault & Appliance-Condition Detectability, 1. Loose electrical connections, 2. Earthing problems, 3. Leakage / abnormal current behaviour, 4. Voltage / current abnormalities, 5. Old / degrading appliances, 6. Inefficient appliances, Data tiers used in this file (+2 more)

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
Cohesion: 0.19
Nodes (14): compute_file_hash_and_rows(), inventory_datasets(), match_schema_signature(), Dataset discovery, inventorying, hashing, and schema signature matching., Compute SHA-256 hash, size in bytes, row count, and header columns., Match a column list against the signatures defined in contracts., Inventory and fingerprint all supported datasets in data_dir., Path (+6 more)

### Community 10 - "Electricity Demand Forecasting In Kerala Using Machine Learning Models"
Cohesion: 0.11
Nodes (17): _A. Evaluation of Performance_, Electricity Demand Forecasting In Kerala Using Machine Learning Models, _<mark>A. Linear Regression</mark>_, _<mark>B. Decision Tree</mark>_, _<mark>C. Random Forest</mark>_, _<mark>D. Support Vector Machine</mark>_, _<mark>E. K-Nearest Neighbors</mark>_, _<mark>F. ANN</mark>_ (+9 more)

### Community 11 - "Decision Record — Finalized MVP Workflow"
Cohesion: 0.11
Nodes (17): AI/ML boundary, Backend, Data and AI, Data and integration decisions, Decision Record — Finalized MVP Workflow, Feature evidence tiers, Frontend, Implementation recommendations (+9 more)

### Community 12 - "load_smart_meter_15min"
Cohesion: 0.13
Nodes (16): load_daily_abnormal(), DataFrame, Adapter for Intelligent_abnormal_electricity_usage.csv., Load daily abnormal usage dataset, cleaning strings and quarantining missing-…, load_labelled_home_15min(), DataFrame, Adapter for ai_energy_intelligence_dataset.csv., Load ai_energy_intelligence_dataset.csv, emitting canonical telemetry and… (+8 more)

### Community 13 - "schemas.py"
Cohesion: 0.27
Nodes (11): AnomalyFacts, AuditFinding, AuditReport, Typed data contracts and schemas for the ML pipeline., RunManifest, SourceDescriptor, audit_daily_abnormal(), audit_smart_meter_15min() (+3 more)

### Community 14 - "run_pipeline"
Cohesion: 0.17
Nodes (11): EnergyIntelligenceInferenceEngine, DataFrame, Inference engine loading promoted model artifacts to score live/replayed…, Inference engine for real-time or batch interval scoring., Score a DataFrame of precomputed interval feature rows., run_pipeline(), End-to-end pipeline and inference engine tests., Verify that dry-run successfully inventories and validates datasets. (+3 more)

### Community 15 - "evaluate_event_detection"
Cohesion: 0.13
Nodes (16): Any, inject_benchmark_events(), DataFrame, Controlled synthetic event injection for Phase 4 benchmarking., Inject reproducible synthetic events on a copy of the test frame., evaluate_event_detection(), DataFrame, Evaluation metrics for event detection and interval anomalies. (+8 more)

### Community 16 - "02 — System Capabilities (Functional Scope)"
Cohesion: 0.15
Nodes (13): 02 — System Capabilities (Functional Scope), 10. Appliance efficiency / ageing detection (T2/T3), 11. Electrical fault detection (T2/T3, mostly needs sensors), 12. Cross-cutting, 1. Energy consumption monitoring (T1), 2. Usage pattern analysis (T1), 3. Anomaly detection (T1), 4. Energy wastage detection (T1/T2) (+5 more)

### Community 17 - "run.py"
Cohesion: 0.22
Nodes (10): SplitManifest, create_daily_splits(), create_smart_meter_splits(), DataFrame, Deterministic, leakage-safe temporal and group split generators., Generate temporal splits (train: 1-21, val: 22-24, test: 25-28) for 15-minute…, Generate temporal split for daily abnormal dataset (train: 1-24, test: 25-30)., Offline ML training pipeline orchestrator. (+2 more)

### Community 18 - "05 — AI / ML Model Mapping per Capability"
Cohesion: 0.18
Nodes (10): 05 — AI / ML Model Mapping per Capability, 1. Consumption forecasting, 2. Anomaly detection, 3. Appliance identification / disaggregation, 4. Appliance efficiency estimation, 5. Fault detection (see file 03 for what is physically observable), 6. Energy optimisation, 7. Personalised recommendations (+2 more)

### Community 19 - "train.py"
Cohesion: 0.13
Nodes (32): digest(), write_json(), detect_events(), evaluate_appliances(), quality(), Coarse interval step events and independent labelled safety replay., safety_replay(), _bundle() (+24 more)

### Community 20 - "Predictive_Analytics_for_Energy_Efficiency_Leverag.md"
Cohesion: 0.22
Nodes (8): 1. Introduction, 2. Description of the Research Problem, 3. Description of Supervised Machine Learning Implementation, 4. Results of Simulation Studies, 5. Conclusions, Abbreviations, Predictive Analytics for Energy Efficiency: Leveraging Machine Learning to Optimize Household Energy Consumption, References

### Community 21 - "billing.py"
Cohesion: 0.10
Nodes (24): api_view, Snapshot, section(), band_for(), estimate(), money(), Monthly equivalent energy + fixed charges. No invented levies or ToD enrollment., schedule() (+16 more)

### Community 22 - "SDG 7 — Affordable and Clean Energy"
Cohesion: 0.29
Nodes (6): AI-Based Energy Consumption Intelligence & Optimization System, Core Objective, Problem Statement, SDG 7 — Affordable and Clean Energy, The Challenge, Why This Problem Matters

### Community 24 - "Project Context for Agents"
Cohesion: 0.40
Nodes (4): Contribution rules, Evidence discipline, Project Context for Agents, Where things live

### Community 25 - "Energy Intelligence ML Training Pipeline — Delivery Loop"
Cohesion: 0.40
Nodes (4): Current Loop — LOOP-002, Energy Intelligence ML Training Pipeline — Delivery Loop, LOOP-001, Prior loops

### Community 26 - "data/README.md"
Cohesion: 0.40
Nodes (4): Dataset roles and storage, Household Energy Intelligence Dataset (`ai_energy_intelligence_dataset.csv`), Overview, Schema & Field Descriptions

### Community 28 - "Dataset audit"
Cohesion: 0.40
Nodes (4): ai_energy_intelligence_dataset.csv, Dataset audit, Intelligent_abnormal_electricity_usage.csv, synthetic_smart_meter_15min.csv

### Community 33 - "package.json"
Cohesion: 0.06
Nodes (30): axios, dependencies, axios, lucide-react, react, react-dom, react-router-dom, recharts (+22 more)

### Community 34 - "main.jsx"
Cohesion: 0.17
Nodes (12): api, Appliances(), Ask(), Chart(), Consumption(), Cost(), date(), Evidence() (+4 more)

### Community 35 - "test_advisor.py"
Cohesion: 0.31
Nodes (9): fallback(), _narrate(), Facts-only narration. Llama selects grounded sentences; arbitrary claims fail…, statements(), validate_response(), facts(), fixture, test_safety_and_out_of_scope() (+1 more)

### Community 36 - "07 — Proposed System Scope & Novelty"
Cohesion: 0.18
Nodes (11): 07 — Proposed System Scope & Novelty, Advanced differentiating features (Tier 2 — prototype on one home / bench), AI/ML components (from file 05), Core MVP (Tier 1), Decision log, Explicitly out of scope (state on a roadmap slide), Hardware requirements, Main technical risks & mitigations (+3 more)

### Community 37 - "Progress and AI handoff — Paranova"
Cohesion: 0.18
Nodes (11): API contract reminder, Completed implementation, Critical workspace / Git state, Dataset state and roles, How the next AI should proceed, Known limitations / unfinished external verification, Last completed model run, Progress and AI handoff — Paranova (+3 more)

### Community 38 - "04 — Data Collection Approaches (India / Kerala context)"
Cohesion: 0.29
Nodes (6): 04 — Data Collection Approaches (India / Kerala context), Comparison table, Finalized hackathon data plan (see file 08), Indian-context practicalities [I], Realistic prototype data architecture, What each tier enables (recap from files 02–03)

### Community 39 - "06 — Practical Feasibility Assessment"
Cohesion: 0.29
Nodes (6): 06 — Practical Feasibility Assessment, Cross-cutting limitations, Feasibility verdict, Tier 1 — MVP / hackathon-feasible (software + project dataset replay), Tier 2 — Medium-term (needs IoT hardware fleet / additional datasets / months of data), Tier 3 — Research-level / advanced

### Community 40 - "12 — Local MVP implementation record"
Cohesion: 0.29
Nodes (7): 12 — Local MVP implementation record, Appliance and safety limits, Continuation checkpoint, Data and audit, Forecast and anomaly decisions, Local operation and verification, Tariff and narration sources

### Community 41 - "Research Index — AI-Based Household Energy Intelligence System"
Cohesion: 0.40
Nodes (5): Evidence-tag convention (used in every file), Implementation specification, Key takeaways (one paragraph), Research Index — AI-Based Household Energy Intelligence System, Source papers (in `../`)

### Community 42 - "Paranova — household energy intelligence"
Cohesion: 0.40
Nodes (5): Paranova — household energy intelligence, Repository map, Reproduce and verify, Run locally, What is included

## Knowledge Gaps
- **312 isolated node(s):** `Migration`, `name`, `version`, `private`, `type` (+307 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `write_json()` connect `train.py` to `inventory_datasets`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `FINAL WORKFLOW — AI Household Energy Intelligence (Hackathon MVP)` connect `FINAL WORKFLOW — AI Household Energy Intelligence (Hackathon MVP)` to `research/README.md`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **What connects `Migration`, `name`, `version` to the rest of the system?**
  _312 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Energy Intelligence ML Training Pipeline — Technical Design and Implementation Plan` be split into smaller, more focused modules?**
  _Cohesion score 0.045454545454545456 - nodes in this community are weakly interconnected._
- **Should `Acceptance criteria` be split into smaller, more focused modules?**
  _Cohesion score 0.058823529411764705 - nodes in this community are weakly interconnected._
- **Should `09 — Dataset-Verified Model Implementation Plan` be split into smaller, more focused modules?**
  _Cohesion score 0.06451612903225806 - nodes in this community are weakly interconnected._
- **Should `FINAL WORKFLOW — AI Household Energy Intelligence (Hackathon MVP)` be split into smaller, more focused modules?**
  _Cohesion score 0.06451612903225806 - nodes in this community are weakly interconnected._
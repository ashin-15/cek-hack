# Research Index — AI-Based Household Energy Intelligence System

This directory holds the scoping research for the hackathon project defined in
`../ai_energy_consumption_problem_statement.md`. Each file answers one scoping
question. Start with [the authoritative combined workflow](11_final-workflow-combined.md).
Earlier documents provide research and historical context; where they conflict,
file 11 controls the MVP scope.

| # | File | Question answered |
|---|------|-------------------|
| 01 | [01_paper_evidence_audit.md](01_paper_evidence_audit.md) | What do the three attached papers actually demonstrate, propose as future work, or *not* demonstrate? |
| 02 | [02_system_capabilities.md](02_system_capabilities.md) | Complete list of functions/capabilities the system should have |
| 03 | [03_electrical_fault_detectability.md](03_electrical_fault_detectability.md) | Which electrical faults / appliance conditions can be detected from consumption data alone vs. extra sensors |
| 04 | [04_data_collection_approaches.md](04_data_collection_approaches.md) | How to practically collect household data (India / Kerala focus), what each source yields, hackathon feasibility |
| 05 | [05_ai_ml_model_mapping.md](05_ai_ml_model_mapping.md) | Where AI/ML belongs; model classes per capability; paper-supported vs. proposed |
| 06 | [06_feasibility_assessment.md](06_feasibility_assessment.md) | MVP vs medium-term vs research-level; hardware, datasets, infra, ML complexity, limitations |
| 07 | [07_proposed_scope_and_novelty.md](07_proposed_scope_and_novelty.md) | Defensible project scope, differentiating/novel features, risks |
| **10** | [10_workflow_decisions.md](10_workflow_decisions.md) | Accepted MVP product, data, safety, AI, stack and demo-workflow decisions; overrides earlier recommendations where different |
| **11 — authoritative** | [11_final-workflow-combined.md](11_final-workflow-combined.md) | Master finalized combined workflow for the hackathon MVP |
| 08 | [08_abnormal_usage_model_spec.md](08_abnormal_usage_model_spec.md) | Dataset-grounded daily abnormal-usage model specification and leakage controls |
| 09 | [09_model_implementation_plan.md](09_model_implementation_plan.md) | Verified-dataset implementation plan for the interval anomaly model and daily benchmark |
| 12 | [12_mvp_implementation.md](12_mvp_implementation.md) | Implemented pipeline, evaluation policy, limitations and verification |

## Implementation specification

The draft product requirements, technical design, and measurable acceptance contract
for implementing the offline ML training pipeline are in
[`../spec-driven/ml-training-pipeline/`](../spec-driven/ml-training-pipeline/). These
documents translate the research decisions into stable `FR-*` and `AC-*` contracts;
they do not authorize production implementation until explicitly approved.

## Source papers (in `../`)

| ID | File | Short title | Level of study |
|----|------|-------------|----------------|
| **[A]** | `Electricity_Demand_Forecasting_In_Kerala_Using_Machine_Learning_Models.md` | Saji, Prakash, Krishnan — *Electricity Demand Forecasting in Kerala using ML* (CONIT 2023) | State-grid aggregate (KSEB MW), daily, 10 years |
| **[B]** | `IJST241243.md` | Singh, Pandey, Jaiswal — *AI-Enabled Smart Energy Optimization System for Consumption Forecasting and Cost Reduction* (IJST 2026) | Household, appliance inventory entered by user, monthly bill |
| **[C]** | `Predictive_Analytics_for_Energy_Efficiency_Leverag.md` | Powroźnik, Szcześniak — *Predictive Analytics for Energy Efficiency* (Energies 2024) | Single household, 13 appliances on smart sockets, 30 days, MATLAB simulation |

## Evidence-tag convention (used in every file)

Every non-trivial claim is tagged so the team never presents an idea as
"established" when it is not:

- **[E]** — *Evidence*: directly demonstrated or measured in one of the papers. Cited as `[A §III.H]`, `[B Methodology B.iii, Table 2]`, `[C Alg. 1]`, etc.
- **[I]** — *Engineering inference*: not in the papers, but follows from standard electrical engineering / ML practice or from publicly known facts (Indian meter standards, public datasets). Should be verifiable; verify before putting on a slide as fact.
- **[X]** — *Proposed extension*: our idea. Plausible, but unproven. Must be framed as a hypothesis or prototype in any pitch.

## Key takeaways (one paragraph)

None of the three papers performs anomaly detection, appliance disaggregation
(NILM), appliance-ageing detection, or electrical-fault detection. What they
*do* establish is: (1) tree ensembles (Random Forest / XGBoost) are a sound,
low-latency default for electricity regression in both aggregate [A] and
household [B] settings; (2) a slab-aware Indian billing engine plus LLM-phrased
recommendations is a working, deployed pattern [B]; (3) per-appliance data from
cheap Wi-Fi smart sockets (Tuya cloud) is a practical acquisition path, and
tiny classifiers can run the resulting decision logic [C]. Everything about
faults, earthing, leakage, or ageing in our system is therefore **[I]** or
**[X]** and must be scoped as such — see file 03.

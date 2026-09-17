# 07 — Proposed System Scope & Novelty

Answers: *a technically defensible scope — core MVP, differentiating features,
required data, AI/ML components, hardware, main risks — plus where the novelty
is.* Tags per README. This file is the decision record; update it when scope
changes.

## Positioning (one sentence)

> A context-aware energy-intelligence layer for Indian households that turns any
> available consumption data — from a bi-monthly KSEB bill to a 1 Hz sensor
> node — into *expected-vs-actual* explanations, slab-aware cost foresight, and
> guard-railed plain-language actions; with appliance-health and electrical-safety
> indicators as a hardware-backed extension.

The gap we fill is precisely what [B Discussion B] admits it cannot do
("unusual consumption", "no smart-meter/IoT real-time data") [E] and what the
problem statement calls the core objective.

## Core MVP (Tier 1)

| # | Feature | Novelty vs papers | Evidence basis |
|---|---------|-------------------|----------------|
| M1 | **Replay/manual ingestion** (audited project CSVs plus manual units/household values) behind a provider contract that can later support an authorized KSEB adapter | New: progressive path from manual values to future smart-meter data | adapter architecture [I]/[X] |
| M2 | **Context-conditional baseline & anomaly engine**: compare seasonal baseline, Random Forest and XGBoost for expected load → residual scoring + Isolation Forest/rules + anomaly-type facts; every alert states *expected / observed / why* | New: none of the papers do anomaly detection | model family [E] via [A],[B]; method [I] |
| M3 | **Wastage detectors**: phantom-load trend, left-on plateau, inactive-window usage | New | [I] |
| M4 | **Forecast + slab-cliff early warning**: quantile end-of-cycle forecast → P(crossing 250-unit KSEB telescopic→non-telescopic boundary) → daily kWh budget "gauge" | New: [B] has a static slab calculator; we make it probabilistic and forward-looking | [B B.iv] engine [E]; forecast [X] |
| M5 | **KSEB-accurate billing engine** (telescopic/non-telescopic, fixed charge, duty, fuel surcharge; JSON tariff, dated) | Reproduces [B] for Kerala | [B] [E] |
| M6 | **Inventory-based appliance split + efficiency ranking + payback** | Reproduces [B]; adds BEE-rating benchmark | [B B.ii–iii] [E]; BEE [I] |
| M7 | **Guard-railed LLM advisor** (facts-in JSON → 3–5 quantified actions; numeric post-check; templated fallback; Malayalam option) | Improves on [B]'s acknowledged LLM inconsistency | [B B.v] [E]; guardrails [I] |
| M8 | **Simulator with injectable events** used for demo and for measuring detector precision/recall | New as a first-class artefact | [X] |

## Advanced differentiating features (Tier 2 — prototype on one home / bench)

| # | Feature | Why it differentiates | Hardware |
|---|---------|----------------------|----------|
| A1 | **Appliance Health Index**: per-appliance energy-per-cycle, duty cycle, start current tracked with weather normalisation and CUSUM drift alerts (fridge, AC, geyser) | Nobody in the attached papers does ageing; strong "act before it fails" story | 2–3 smart plugs [C §2] [E] |
| A2 | **Inverter/UPS battery-health proxy**: post-outage recharge energy vs outage duration trend | Uniquely Indian; uses outage gaps that are noise for everyone else | whole-house node |
| A3 | **Electrical-safety indicators**: over/under-voltage log, over-current vs sanctioned load ([C Alg.1] threshold generalised), residual-current (leakage) monitor with leaky-appliance attribution | Cheap, real, and honestly scoped (file 03) | node + residual CT |
| A4 | **Wiring-health trend (two-point ΔV/I)** | Novel hypothesis; label as experimental | node + plug with V reporting |
| A5 | **Event-based appliance identification** on 1 Hz aggregate for 3–5 high-power appliances, with user-confirmation loop | Lightweight NILM without deep models | node ≥1 Hz |
| A6 | **Kerala grid context** ([A] replica): state demand forecast → "grid stress" nudges ("reduce / hold / increase" à la [C]) | Ties household to SDG-7 system benefit | none (public data) |

## Explicitly out of scope (state on a roadmap slide)

Loose-connection/arc detection (needs kHz waveform hardware), earthing diagnosis
(not observable from power data), full deep NILM, RL-based automated control,
utility smart-meter API (no public API), remaining-useful-life prediction.

## Novel ideas worth pitching (all [X] unless noted)

1. **"Expected vs. Unexpected" as the primary UI metaphor.** Every chart shows
   the learned expectation band; colour only what exceeds it. Directly
   implements the problem statement's "same increase may be normal or wasteful
   depending on context".
2. **Slab-cliff early warning.** KSEB's non-telescopic switch above 250 units per
   bi-month re-prices the *entire* consumption — a small overshoot can cost
   hundreds of rupees. A probabilistic forecast turned into a daily budget is
   simple, Kerala-specific and high-impact. (Verify boundary/rates against the
   current KSERC order before demo.)
3. **Outage-aware analytics.** Treat data gaps as first-class events; derive
   inverter battery health (A2), separate "post-outage recharge" from anomalies,
   and report reliability stats per household.
4. **Monsoon-aware safety.** Correlate residual-current increases with humidity/
   rain to flag damp-related insulation faults — Kerala-specific, sensor-backed.
5. **Appliance health as a maintenance nudge, not a fault alarm.** "Your fridge
   now runs 18 % longer per cycle than in August at the same room temperature —
   check the door seal / clean the condenser" is actionable without claiming
   diagnosis.
6. **Inclusive onboarding.** Bill upload or meter photo gives value on day one
   (slab position, appliance ranking, payback); the system upgrades its
   capability tier automatically as richer data arrives. Show the "capability
   ladder" in the UI.
7. **Facts-only LLM.** Publish the guardrail: the model can only cite numbers
   present in the structured input; violations fall back to templates. This is a
   concrete answer to [B]'s stated LLM limitation.
8. **Synthetic-event benchmark.** Ship the simulator + a scored benchmark for
   anomaly/ageing detectors as an open artefact — judges can see precision/recall
   rather than screenshots.

## Required data

| Purpose | Source | Tier |
|---------|--------|------|
| Forecast/pattern replay | `data/synthetic_smart_meter_15min.csv` (12 simulated meters; audit in file 09) | D1 + interval V/I/PF |
| Daily anomaly benchmark | `data/Intelligent_abnormal_electricity_usage.csv` (community fixture with unresolved provenance and suspected leakage; audit in file 08) | Daily D1 |
| Rich appliance/waste/health/safety demo | `data/ai_energy_intelligence_dataset.csv` (one simulated household) | D1 + simulated add-on channels |
| Tariff | Latest verified KSERC domestic schedule as dated JSON | — |
| Appliance benchmarks | Curated BEE star-label subset (AC, fridge, fan, geyser) | — |
| Manual input | Units and household values for bill/what-if analysis | D0 |
| External robustness (post-MVP) | iAWE, UCI, UK-DALE/REFIT | D1/D2 |

## AI/ML components (from file 05)

- Seasonal-naive baseline vs Random Forest vs XGBoost interval forecaster; select by leakage-safe held-out evaluation, then add quantile/conformal bounds (paper-supported tree families).
- Residual + Isolation Forest anomaly scorer; small tree for anomaly-type tags.
- RF inventory→kWh model ([B] replica).
- k-means day-type clustering; change-point (ruptures/CUSUM) for regime and drift.
- Event-based appliance classifier (kNN/GBM on edge features) — Tier 2.
- Rule engine for nudges/scheduling/safety thresholds ([C] pattern).
- LLM phrasing layer with guardrails ([B] pattern).

## Hardware requirements

- **Finalized MVP:** none; replay the audited synthetic project datasets.
- **Tier 2 option:** ESP32 + PZEM-004T v3 (or Shelly EM) and 2–3 Tuya/Tasmota 16 A plugs.
- **Safety add-on:** second CT wired around L+N for residual current; optional N–E voltage sensing. Electrician required for live-wire work.

## Main technical risks & mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| No live/field-validated KSEB household history | Results could be mistaken for production evidence | Badge synthetic/community data in the UI; show model versions and audit facts; never claim field validation |
| Labels are synthetic, incomplete, or suspected of leakage | Misleadingly high anomaly/fault accuracy | Apply files 08–09 leakage gates; separate injected-event metrics; preserve immutable raw files |
| Tariff mismatch with current KSERC order | Wrong ₹ figures on stage | Dated tariff JSON, one-time verification, show tariff version in UI |
| Over-claiming fault detection | Credibility/safety liability | File 03 language; "indicator, consult electrician"; descope arc/earthing |
| LLM hallucinating numbers | Trust | Facts-only guardrail + templated fallback ([B] limitation) |
| Weather API / LLM API outage during demo | Demo failure | Cache weather; offline templated recommendations |
| Replay/backend or Groq failure | Main demo breaks | Seed/precompute the main dashboard; deterministic advisory fallback; live API proof is secondary |
| Future interval smart-meter data reveals occupancy | Ethical/regulatory | Minimise retention and aggregate before cloud upload |
| Scope creep into Tier 2/3 | Nothing finished | Freeze M1–M8 first; A1–A3 only after MVP is demoable |

## Decision log

- 2026-09-17 — Scope defined per this file; papers [A],[B],[C] audited (file 01). Fault detection limited to voltage/current/leakage indicators; loose-connection and earthing detection descoped to research roadmap.

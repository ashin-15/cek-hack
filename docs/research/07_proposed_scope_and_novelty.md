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
| M1 | **Multi-source ingestion** (bill/CSV, meter-photo OCR, public-dataset replay, MQTT node, smart-plug cloud, simulator) into one canonical series | New: inclusive onboarding for non-smart-meter homes (most of Kerala) | [C §2] plug→cloud path [E]; rest [I]/[X] |
| M2 | **Context-conditional baseline & anomaly engine**: LightGBM expected-load model (hour, daytype, weather, lags) → residual scoring + Isolation Forest + anomaly-type tags; every alert states *expected / observed / why* | New: none of the papers do anomaly detection | model family [E] via [A],[B]; method [I] |
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
| Model training / demo replay | iAWE (Indian), UCI household, UK-DALE/REFIT signatures | D1/D2 |
| Weather features & forecasts | Open-Meteo (or similar) for Kerala locations | — |
| Tariff | Latest KSERC domestic schedule as JSON | — |
| Appliance benchmarks | Curated BEE star-label subset (AC, fridge, fan, geyser) | — |
| Grid context | Grid-India / POSOCO daily Kerala demand | — |
| Live demo | 1 node (whole-house or bench), 2–3 plugs | D2 |
| Onboarding demo | Sample KSEB bill PDF, meter photo | D0 |

## AI/ML components (from file 05)

- LightGBM/XGBoost interval forecaster with quantile heads (paper-supported family).
- Residual + Isolation Forest anomaly scorer; small tree for anomaly-type tags.
- RF inventory→kWh model ([B] replica).
- k-means day-type clustering; change-point (ruptures/CUSUM) for regime and drift.
- Event-based appliance classifier (kNN/GBM on edge features) — Tier 2.
- Rule engine for nudges/scheduling/safety thresholds ([C] pattern).
- LLM phrasing layer with guardrails ([B] pattern).

## Hardware requirements

- **Minimum:** none (public data + simulator + bill upload).
- **Recommended demo:** ESP32 + PZEM-004T v3 (or Shelly EM) on the mains or a bench strip; 2–3 Tuya/Tasmota 16 A plugs; Mosquitto broker on the backend host.
- **Safety add-on:** second CT wired around L+N for residual current; optional ZMPT101B for N–E voltage. Electrician for any live-wire work.

## Main technical risks & mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Insufficient real household history for learned baselines | Anomaly/forecast demos look fake | Use iAWE/UCI replay + simulator; show live node for monitoring/V/I only; be transparent |
| No labelled anomalies/ageing | Cannot report real accuracy | Synthetic-event benchmark with stated caveat |
| Tariff mismatch with current KSERC order | Wrong ₹ figures on stage | Dated tariff JSON, one-time verification, show tariff version in UI |
| Over-claiming fault detection | Credibility/safety liability | File 03 language; "indicator, consult electrician"; descope arc/earthing |
| LLM hallucinating numbers | Trust | Facts-only guardrail + templated fallback ([B] limitation) |
| Weather API / LLM API outage during demo | Demo failure | Cache weather; offline templated recommendations |
| Sensor node reliability (Wi-Fi, calibration) | Live view flaky | Pre-record a fallback stream; calibrate PZEM against a known load |
| Privacy of 1 Hz data | Ethical/regulatory | Aggregate to 1-min before upload; local-first option |
| Scope creep into Tier 2/3 | Nothing finished | Freeze M1–M8 first; A1–A3 only after MVP is demoable |

## Decision log

- 2026-09-17 — Scope defined per this file; papers [A],[B],[C] audited (file 01). Fault detection limited to voltage/current/leakage indicators; loose-connection and earthing detection descoped to research roadmap.

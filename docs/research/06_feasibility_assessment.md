# 06 — Practical Feasibility Assessment

Answers: *what is hackathon-feasible, what needs IoT hardware / more data, what is
research-level; required hardware, datasets, infrastructure, ML complexity,
deployment, limitations.* Tags per README.

## Tier 1 — MVP / hackathon-feasible (software + project dataset replay)

| Feature | Data | ML complexity | Depends on |
|---------|------|---------------|-----------|
| Ingestion adapters: project CSV replay and manual bill/unit input | D0–D1 | none | — |
| Consumption dashboard (daily/15-minute) | D1 | none | ingestion |
| Usage-pattern analysis: load shape by hour×daytype, baseload, peak windows, day clustering | D1 | low (k-means, percentiles) | ≥2 weeks data |
| Household interval forecast (24 h / 7 d): seasonal baseline vs Random Forest vs XGBoost | D1 | low–medium | audited 15-minute dataset |
| End-of-cycle kWh forecast with quantiles → **slab-crossing probability** | D1 | medium | forecast |
| KSEB slab billing engine (telescopic ≤250 units bi-monthly, non-telescopic above, fixed charge, duty, fuel surcharge) with configurable tariff JSON | D0 | none | current tariff order |
| Forecast-residual anomaly detection + Isolation Forest + anomaly-type tagging | D1 | medium | forecast |
| Wastage: phantom-load trend, left-on plateau, inactive-period usage | D1 | low | pattern module |
| Declared-inventory appliance split (RF as in [B]) + inefficient-appliance ranking vs BEE ratings + replacement payback | D0 + inventory | low | inventory UI |
| Interval-level voltage/over-current abnormality log from replayed V/I fields (not transient fault detection) | D1 telemetry | none | synthetic smart-meter replay |
| LLM recommendation layer with guardrails | derived facts | integration | Groq-hosted Llama + deterministic fallback |
| Simulator with injectable events (spike, phantom load, ageing drift, sag, outage) | — | low | — |

**Hardware:** none for the finalized replay-only MVP. ESP32/PZEM and smart plugs remain Tier 2 options, not dependencies.

**Datasets:** the three project fixtures under `data/` are authoritative for the MVP. `synthetic_smart_meter_15min.csv` and `ai_energy_intelligence_dataset.csv` are synthetic; the provenance of `Intelligent_abnormal_electricity_usage.csv` is undocumented and it must be described as a community prototype fixture, not real KSEB data. All require reproducible validation/adapters before training. iAWE, UCI, UK-DALE or REFIT may later test external robustness; they are not the main demo source. Supporting sources remain weather history/forecast, BEE star-label tables (curated subset), and the latest verified KSERC domestic tariff schedule.

**Infrastructure:** React + Vite, Recharts, Axios and React Router on Vercel; Django + Django REST Framework with pandas, NumPy, scikit-learn and XGBoost on Render or Railway; Neon PostgreSQL; Groq-hosted Llama for fact-grounded explanations. Training is an offline reproducible pipeline; Django loads versioned artifacts for inference.

**Deployment requirement:** separate frontend and backend deployments plus Neon. A seeded dashboard and deterministic recommendation fallback protect the main demo from backend cold starts or Groq failure.

**Limitations (be explicit in demo):**
- Model quality is evaluated on project fixtures; this is not field validation on live KSEB households.
- Tariff engine correct only for the configured DISCOM/year.
- Recommendations quality unvalidated (no user study) — same as [B].

## Tier 2 — Medium-term (needs IoT hardware fleet / additional datasets / months of data)

| Feature | Requirement | Why not MVP |
|---------|-------------|-------------|
| Per-appliance ageing/efficiency drift (fridge, AC, geyser, inverter battery) | Plugs or circuit CTs on target appliances; ≥ 4–8 weeks baseline per household; weather normalisation | Needs longitudinal data; validation only via synthetic drift until real failures observed |
| Event-based appliance identification on aggregate 1 Hz | Node at ≥1 Hz (ideally with reactive power); labelled events from user confirmations; transfer from iAWE/UK-DALE | Cross-house transfer is weak; needs a labelling UX and time |
| Leakage-current monitoring & leaky-appliance attribution | Residual CT (L+N) on the node; safe installation | Extra hardware + electrician; safety messaging must be conservative |
| Two-point wiring-health (ΔV under load) | Time-synchronised V from plug + node; weeks of data | Hypothesis; measurement accuracy of consumer plugs is marginal |
| Utility smart-meter integration | Data-sharing agreement or consumer-consent API from KSEB/DISCOM | No public API |
| Multi-DISCOM tariff library, ToD tariffs, solar net-metering ([B Future Work] [E]) | Tariff curation; PV data | Scope, not difficulty |
| Deferrable-load scheduling with actual control (HEMS actuation) | Smart plugs with switching; user comfort model | Safety/liability; [C §5] lists as future work [E] |
| Personalisation loop & household segmentation | Many households × months | Needs fleet data |
| Mobile app, Malayalam UI | Engineering time | Scope |

**ML complexity:** medium; mostly online statistics (CUSUM, change-point) and classic classifiers. The hard part is data and labels, not models.

## Tier 3 — Research-level / advanced

| Feature | Why research |
|---------|--------------|
| Loose-connection / series-arc detection from waveforms | Needs D4 (kHz sampling, custom front-end), labelled arc data; active PQ research area |
| Earthing-quality inference | Physically not observable from power data; needs dedicated measurement; only sensor thresholding is possible |
| Full deep NILM (seq2point, etc.) for Indian appliance mix | No large Indian labelled dataset beyond iAWE; generalisation problem |
| Remaining-useful-life prediction for appliances | Requires fleet failure histories |
| RL-based HEMS control under dynamic tariffs | [C §1] surveys; India lacks dynamic residential tariffs at scale; simulation-only |
| Federated / privacy-preserving training across homes | Infrastructure-heavy |
| Behavioural-change effectiveness studies | Requires real users over months ([C §5] future work [E]) |

## Cross-cutting limitations

1. **Cold start.** Every learned baseline needs 2–4 weeks; provide population priors (from public data, segmented by inventory) until then [I].
2. **Ground truth for anomalies/wastage/ageing does not exist**; evaluation is on synthetic injections and plausibility, and must be stated as such.
3. **Tariff volatility** — KSERC revises tariffs; engine must be data-driven (JSON), version-dated, and show the tariff date used.
4. **Weather dependence in Kerala**: humidity/monsoon drive AC/fan/dehumidifier usage and damp-related leakage; weather features are necessary, and [A §III.H] supports using dew point/humidity, not just temperature [E].
5. **Outages/voltage swings** are frequent; pipeline must be robust to gaps and must not spam alerts.
6. **Safety claims carry liability.** Any electrical-fault feature must be worded as "indicator — consult a licensed electrician", never as a diagnosis.
7. **LLM cost/latency and hallucination** — [B] measured <1.2 s and flagged inconsistency [E]; guardrails + templated fallback required.
8. **Privacy** — 1 Hz whole-house data reveals occupancy; aggregate before upload, minimise retention.

## Feasibility verdict

The problem statement's core (patterns, forecast, anomaly, wastage, actionable
insight) is **fully achievable in Tier 1 with public data plus one optional
sensor node**, and directly extends the demonstrated pieces of [A], [B], [C].
Appliance ageing and safety features are legitimate **Tier 2 differentiators**
if the team owns hardware and frames them as prototypes. Loose-connection and
earthing detection should be **explicitly descoped** to a research roadmap slide.

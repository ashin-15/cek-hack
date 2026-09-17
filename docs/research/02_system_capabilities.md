# 02 — System Capabilities (Functional Scope)

Answers: *what are all the major functions the system should have?* Each
capability lists its minimum data requirement, what the papers support, and a
tier (T1 = MVP, T2 = needs IoT hardware/extra data, T3 = research-level; tiers
are justified in file 06). Tags per README.

The problem statement (`../ai_energy_consumption_problem_statement.md`) frames the
core value as *"distinguishing normal consumption from unusual behaviour,
identifying patterns over time, and helping users understand where opportunities
for energy efficiency may exist"*. Capabilities 1–5 and 8–9 map directly onto it;
6–7 and 10–11 are extensions.

---

## 1. Energy consumption monitoring (T1)

- **Function:** Ingest and display whole-house (and, where available, circuit/appliance) consumption at the finest available resolution: monthly bill → daily kWh → 15/30-min interval → 1 s power.
- **Data needed:** at minimum a time-stamped kWh series. Real-time W, V, I, PF if an IoT node exists.
- **Papers:** [B] shows dashboards for monthly consumption and load distribution (Testing A.vi) [E]; [C] collects 1-Hz-class per-appliance power via Wi-Fi sockets (§2) [E].
- **Notes:** "Monitoring" alone is what the problem statement calls insufficient; it is the substrate, not the product.

## 2. Usage pattern analysis (T1)

- **Function:** Learn the household's typical load shape by hour-of-day × day-type × season; identify baseload (night minimum), peak windows, weekday/weekend differences, occupancy-like regimes; cluster days into "typical day types".
- **Data:** ≥ 2–4 weeks of interval data (hourly or better). Weather (temperature/humidity) improves separation of "hot-day AC" vs "behavioural" peaks — [A §III.H] shows weather covariates matter at grid level [E]; applying the same at household level is [I].
- **Papers:** [C Fig 2, 14] plots 30-day per-appliance profiles but performs no pattern analytics [E]. Everything analytic here is [I].

## 3. Anomaly detection (T1)

- **Function:** Flag intervals whose consumption deviates from the *context-conditional expectation* (time, day type, weather, recent history) — both spikes and unusual persistence (e.g. AC-level load at 3 a.m. on a cool night).
- **Data:** interval series + calendar (+ weather). Labels are typically unavailable → unsupervised / forecast-residual methods (file 05).
- **Papers:** none demonstrate it. [B Discussion B] explicitly names "unusual consumption" as something its model *cannot* catch [E] — this is the gap.
- **Key design point [I]:** an anomaly must be relative to *expected* consumption, not to a fixed threshold; otherwise every hot afternoon becomes an alert. This is the central technical requirement in the problem statement.

## 4. Energy wastage detection (T1/T2)

Wastage = consumption that is *explained* (not anomalous) but *unnecessary*. Sub-functions:

| Sub-function | Signal | Tier |
|--------------|--------|------|
| Phantom / standby load | Night-time minimum power trend; sudden step-up in baseload that persists | T1 with interval data |
| Left-on appliance | Appliance-like plateau (e.g. 1.2–1.8 kW geyser signature, 60–100 W fan/TV) continuing far beyond normal duration | T1 (whole-house heuristics) / T2 (per-appliance plug) |
| Inactive-period consumption | Load during declared/learned unoccupied windows above baseload | T1 |
| Tariff-inefficient timing | Deferrable loads (washing machine, pumping, EV/inverter charging) running in expensive ToD windows when a cheap window exists | T1 if ToD tariff applies (Kerala ToD applies only to certain consumer classes — verify current KSEB tariff order) |

- **Papers:** [C Alg. 1] provides the "reduce / hold / increase" nudge pattern driven by price + power thresholds [E]. Wastage *detection* itself is [I].

## 5. Appliance-level tracking / disaggregation (T2, partial T1)

- **Function:** Attribute whole-house consumption to appliance classes.
- **Three routes:**
  1. **Declared inventory** (user enters appliances, watts, hours) → estimated split. [B Methodology B.ii–iii] does exactly this with RF, MAPE 6.8 % at bill level [E]. T1.
  2. **Direct sub-metering** with smart plugs / CTs per circuit → exact per-device series. [C §2] [E]. T2 (hardware).
  3. **NILM** (infer appliances from the aggregate signal) → requires ≥ 1 Hz aggregate power (better with reactive power / harmonics) and labelled training data. Not in any paper; mature in the wider literature (public datasets: REDD, UK-DALE, REFIT, and the Indian **iAWE** dataset) [I]. T2/T3.
- **Honest framing:** For a hackathon, route 1 + a hybrid "declared inventory + event-based signature matching on the aggregate" is defensible [X]; full NILM is a research track.

## 6. Consumption forecasting (T1)

- **Function:** (a) Next-day / next-week interval forecast for the household; (b) end-of-billing-cycle total kWh forecast with uncertainty bands; (c) optional grid-level Kerala demand context.
- **Data:** ≥ 4–8 weeks of household history + calendar + weather forecast.
- **Papers:** [A] grid-level daily forecasting with RF/XGBoost [E]; [B] monthly kWh from declared usage [E]. Household interval forecasting with the same model families is [I].

## 7. Electricity bill / cost prediction (T1)

- **Function:** Convert forecast kWh into an expected bill using the exact DISCOM tariff (KSEB: telescopic slabs up to 250 units/bi-month, **non-telescopic** flat-rate slabs above that, fixed charge, duty, fuel surcharge — verify against the latest KSERC tariff order); show slab position, distance to next slab boundary, and **probability of crossing** by cycle end.
- **Papers:** [B Methodology B.iv, Testing A.iv] validates a slab-wise engine against real bills [E]. The probabilistic slab-crossing forecast is [X] (see file 07).

## 8. Energy optimisation (T1/T2)

- **Function:** Recommend *when* to run deferrable loads (cheap tariff window, solar surplus, below sanctioned-load ceiling) and *what* to curtail to stay under a slab boundary or a user budget.
- **Papers:** [C Alg. 1 + ml1] gives the threshold/price nudge logic [E]. Slab-budget pacing and appliance scheduling are [I]/[X]. Automated control of appliances (true HEMS actuation) is T2/T3 and listed as future work in [C §5].

## 9. Personalised AI recommendations (T1)

- **Function:** Turn structured findings (anomalies, wastage, slab risk, forecast, appliance ranking) into 3–5 quantified, plain-language actions per user, in local language if desired.
- **Papers:** [B Methodology B.v] — LLM-as-energy-auditor with structured prompt [E]; [B Discussion B] warns about inconsistency/incompleteness [E].
- **Design rule [I]:** the LLM must **phrase**, not **compute**. All numbers (kWh, ₹, %) are produced deterministically and passed in; the LLM is constrained to reference them. Recommendations are validated against a rules layer before display.

## 10. Appliance efficiency / ageing detection (T2/T3)

- **Function:** Track per-appliance energy-per-cycle, duty cycle, run-time, start-up current, and weather-normalised efficiency (e.g. AC kWh per cooling-degree-hour) over months; alert on drift.
- **Data:** per-appliance series (plug/CT) over a long baseline; appliance rated specs (BEE star label) for benchmarking.
- **Papers:** none. [B B.ii] mentions "efficiency degradation" only as motivation [E]. Entire capability is [X]. Detailed feasibility in file 03.

## 11. Electrical fault detection (T2/T3, mostly needs sensors)

- **Function (aspirational):** loose connections, earthing faults, leakage current, over/under-voltage, over-current vs sanctioned load.
- **Papers:** [C §2] only has a fixed upper power threshold [E]. Everything else is [I]/[X] and, crucially, most of it **cannot** be inferred from kWh data. File 03 covers each fault class.
- **Realistic subset for us:** voltage/current abnormality logging (if the node measures V/I), over-current vs sanctioned load, residual-current (leakage) alerting if a CT-pair or RCD-with-telemetry is fitted.

## 12. Cross-cutting

- **Data ingestion adapters:** CSV/bill upload, DISCOM portal history, IoT MQTT stream, smart-plug cloud APIs, public datasets (file 04).
- **Explainability:** every alert carries "expected X, observed Y, because Z" — required by the problem statement's "meaning behind the data".
- **Privacy/security:** [B A.v] baseline (OTP, bcrypt, HttpOnly, TLS) [E]; interval energy data is occupancy-revealing, so minimise retention and expose only aggregates externally [I].
- **Simulation / synthetic data engine:** needed to demo anomalies, faults and ageing that real short-term data will not contain (file 06/07) [X].

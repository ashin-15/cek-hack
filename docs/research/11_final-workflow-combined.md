# FINAL WORKFLOW — AI Household Energy Intelligence (Hackathon MVP)

**Version:** combined, 2026-09-17
**Supersedes:** `final-locked-workflow.md`, `final_locked_workflow_ai_household_energy_intelligence.md`, and the 2026-09-17 Decision Record.
**Scope rule:** nothing outside this file is in scope unless explicitly added. Where the three source documents disagreed, the resolution is recorded in §1 with the reason.

---

## 0. Locked decisions

| Decision | Value |
|---|---|
| Target | One Kerala household, one selected meter, shown one at a time |
| Hardware | None. Dataset replay only |
| Deployment | **Local only.** No Vercel, no Render/Railway, no Neon. SQLite file DB |
| Authentication | **None.** Dashboard opens straight onto the demo household |
| Manual user input | **One input panel only:** tariff slab values + a power-usage figure, feeding bill and what-if calculations. Nothing else is user-entered |
| Datasets | All three local files, each with a fixed role (§3) |
| Data repair | Audit + adapter layer. Raw CSVs never mutated |
| Forecasting | Bake-off: seasonal-naive baseline vs Random Forest vs XGBoost — ship the simplest model that wins on the held-out slice |
| Anomaly detection | Isolation Forest + same-hour / day-type z-score baseline |
| Wastage | Explicit rule and statistics layer. Never a label-trained classifier |
| Labels | Present in two datasets. **Evaluation only** — never a model input feature |
| Appliance inference | Aggregate step-change detection + typical Indian appliance power ranges |
| Appliance efficiency | Rated-vs-observed heuristic (>20% over class ceiling) |
| Appliance ageing / drift | **Cut.** Needs 4–8 weeks of stable per-appliance baseline |
| Power quality | Voltage, power factor, current vs configured limits — computed |
| Safety indicators | **Kept**, as labelled replay from `ai_energy_intelligence_dataset.csv` only |
| Evidence badges | Safety tab only (`Simulated` / `Model estimate`). Other tabs use plain footnotes |
| Optimization | Greedy scheduler. Never MILP, never RL, never appliance control |
| LLM | Groq narrates precomputed facts only |
| UI language | English only |
| Stack | React (Vite) + Django REST Framework + scikit-learn/XGBoost + SQLite |

---

## 1. Conflict resolutions (do not re-litigate)

| # | Conflict | Resolution | Reason |
|---|---|---|---|
| 1 | Zero manual input vs settings forms | One panel: slab values + power usage | Needed for the bill/what-if demo; too narrow to reintroduce onboarding |
| 2 | Auth vs no auth | No auth | Local single-user app; login only adds demo friction |
| 3 | Local vs cloud | Local | Removes deployment risk on demo day |
| 4 | One dataset vs three | Three, with fixed non-overlapping roles | Each answers a different question; never merged into one flat table |
| 5 | Safety excluded vs safety simulated | Kept, replay-only, badged | Signals are not derivable from aggregate telemetry, so the feature is honest only as labelled replay |
| 6 | Ageing kept vs cut | Cut | No multi-week per-appliance baseline exists |
| 7 | RF locked vs model bake-off | Bake-off, simplest winner | Prior RF evidence came from a different input schema; must be re-earned on our data |
| 8 | One household vs population view | One at a time in the UI | 360-home data is used for offline benchmarking, not as a dashboard screen |
| 9 | No labels vs labels exist | Labels exist, used for evaluation only | Prevents target leakage and inflated metrics |

---

## 2. What the system claims, and what it does not

> This is an AI-assisted household energy-intelligence prototype. It forecasts consumption, identifies unusual usage and likely appliance events, checks power quality, estimates KSEB-style cost, and suggests lower-cost usage windows from smart-meter-style telemetry. It does not diagnose electrical faults, does not control appliances, and runs on simulated data.

| Excluded | Reason |
|---|---|
| Confirmed leakage / earthing / arc diagnosis | Needs residual CT, N–E sensing, kHz waveform sampling |
| Power-theft confirmation | Needs feeder/transformer comparison |
| Appliance certainty | Aggregate disaggregation is heuristic |
| Appliance ageing | Needs a long per-appliance baseline |
| Automatic control / actuation | No hardware in scope |
| Live KSEB connection | No verified public consumer API. Show nothing that implies one |
| Field-validated accuracy | All data is simulated or of undocumented provenance |

---

## 3. Datasets and their roles

Raw files live in `data/raw/` and are **read-only**. Adapters write to `data/derived/`.

### 3.1 `synthetic_smart_meter_15min.csv` — primary

12 simulated Kerala meters, 32,256 rows, 28 days at 15-minute resolution. Explicitly synthetic.

Columns: `timestamp, consumer_number, meter_id, tariff_category, supply_phase, frequency_hz, voltage_v, current_a, power_factor, real_power_kw, consumption_interval_kwh, cumulative_energy_kwh`
Enrichment: `region_code, dwelling_type, num_occupants, house_area_sqft, connected_load_kw, temperature_c, humidity_pct`

**Role:** the live dashboard. Forecasting, anomaly detection, wastage scoring, appliance step events, power quality, cost. Demo meter: `SM-KL-001`.
It has no expected-usage column and no anomaly labels — every alert is computed.

### 3.2 `ai_energy_intelligence_dataset.csv` — ground truth and safety replay

One simulated household, 5,760 rows, 60 days at 15-minute resolution, with appliance, anomaly, wastage, ageing-factor and safety-sensor labels. Explicitly synthetic.

**Role, split in two:**
- **Evaluation:** score the appliance detector and anomaly engine against real ground truth. Labels are held out of every feature matrix.
- **Safety tab:** replay labelled safety events. This is the *only* source of safety output. Ageing-factor labels are ignored (feature cut).

### 3.3 `Intelligent_abnormal_electricity_usage.csv` — daily benchmark

360 simulated households, 10,800 daily records, January 2023, with an `Abnormal_Usage` label. Community/Kaggle fixture — **undocumented provenance.** Never call it measured KSEB data and never call it proven synthetic.

No hour/minute timestamp, no voltage, current or power factor. **Role:** offline benchmark of the daily-granularity anomaly approach only. Never rendered as a dashboard screen, never merged with 15-minute data.

### 3.4 Audit and adapter layer

Before any modelling, run `scripts/audit_datasets.py`, producing `reports/data_audit.md`.

It must check and, where needed, correct in the derived copy only:

1. Invalid or out-of-range values (negative kWh, zero voltage, PF > 1)
2. Timestamp gaps, duplicates, timezone drift, DST artefacts
3. Formula inconsistency (`cumulative_energy_kwh` vs summed intervals; `real_power_kw` vs `V × I × PF`)
4. Label contradictions (anomaly flagged on a normal-range interval, and the reverse)
5. Schema/documentation mismatches against the column lists above

Rules: preserve intentional anomaly and fault events, never delete difficult rows to improve metrics, never write back to `data/raw/`, and make every transformation reproducible from the script.

---

## 4. End-to-end workflow

```
data/raw/  (3 CSVs, read-only)
        ↓
Audit + adapters  →  reports/data_audit.md
        ↓
data/derived/  (validated, one meter selected)
        ↓
15-min / hourly / daily aggregate tables
        ↓
Feature engineering  (labels excluded)
        ↓
Forecast bake-off ──┐
Anomaly engine ─────┼──→ Wastage + power-quality rule layer
Appliance events ───┤
Tariff config ──────┘
        ↓
Cost engine + greedy scheduling
        ↓
Precomputed facts JSON  ←── labelled safety replay (separate path)
        ↓
Groq facts-only narration
        ↓
Django REST API  →  React dashboard
```

---

## 5. Pipeline

### Step 1 — Load and validate
1. Load the derived 15-minute file.
2. Parse `timestamp` as timezone-aware Kerala time (`+05:30`).
3. Filter to the selected `meter_id`.
4. Sort chronologically.
5. Assert one record per 15-minute interval, no duplicate `(meter_id, timestamp)`.
6. Coerce energy, voltage, current, frequency and PF to numeric.

### Step 2 — Aggregate tables
```
15-minute → event detection, immediate alerts, power quality
hourly    → forecasting, time-based anomaly analysis
daily     → cost, trends, monthly projection
```
Sum energy on resample. Aggregate voltage/current/frequency/PF with the mean, min or max appropriate to the indicator being displayed.

### Step 3 — Features (hourly rows)
```
hour, day_of_week, is_weekend, month
lag_1h, lag_2h, lag_24h, lag_168h
rolling_mean_3h, rolling_mean_24h, rolling_std_24h
voltage_mean, voltage_min
power_factor_mean
real_power_max
```
Chronological split only — hold out the final time slice. Never random-shuffle time-series rows. No label column, no `Abnormal_Usage`, no appliance ground truth may appear in this matrix.

---

## 6. Models and rule layer

| Capability | Method | Output |
|---|---|---|
| Forecast | Seasonal-naive vs Random Forest vs XGBoost | Next-hour / next-24h kWh |
| Multivariate anomaly | Isolation Forest | Score + flag |
| Contextual anomaly | Same-hour + same-day-type baseline | z-score, normal range |
| Wastage | Rule layer (see below) | Explainable 0–100 score |
| Appliance event | Sustained aggregate step change | Draw, duration, likely class |
| Efficiency hint | Observed steady draw vs class ceiling | Possible over-draw warning |
| Voltage quality | Outside 216–244 V (±6% of 230 V nominal) | Voltage alert |
| PF quality | Persistently below configurable threshold | PF alert |
| High load | Current/power vs `connected_load_kw` | High-load warning |
| Safety | Labelled replay, no model | Hypothesis + evidence + disclaimer |

### 6.1 Forecast bake-off

Train all three on the identical feature matrix and chronological split. Report MAE, RMSE and MAPE per model. **Ship the simplest model whose held-out error is not beaten by a meaningful margin** — if seasonal-naive is within noise of XGBoost, ship seasonal-naive and say so. Record model name, version, feature schema, dataset version, training timestamp, metrics and split policy in the artifact metadata.

Training runs offline via `scripts/train.py`. It must never execute inside a Django request or at application startup.

### 6.2 Wastage score

```
wastage score = weighted anomaly evidence
              + forecast / baseline excess
              + persistence duration
              + night-time weighting
```

Every alert exposes its contributing evidence:

> Consumption was 2.4 standard deviations above the normal 01:00 weekday baseline for 90 minutes. Prioritised because the Isolation Forest also marked it unusual.

**Never train a classifier to imitate this rule.** Doing so produces a near-100% accuracy figure that only reflects the classifier relearning the rule — a documented failure mode in the related HEMS literature. Keep the formula explicit and auditable.

### 6.3 Why greedy, not MILP or RL

- **MILP / constraint solver** — needs device runtime windows and comfort limits that only exist with manual configuration. Without them the problem reduces to "find the cheapest window", while adding a solver dependency and solve-time risk.
- **Reinforcement learning** — needs an environment, reward shaping and training episodes we do not have. Research-only at this scope.
- **Greedy** — deterministic, explainable, zero training, and correctly scoped for a system that only advises.

Keep this reasoning available; it is the most common judge question.

---

## 7. Appliance-event inference

Detect a candidate event on a sustained positive or negative step change in aggregate real power (ΔP threshold + minimum duration). Match steady draw and duration against these representative Indian household ranges. These are reference values, not measurements — the UI must say so.

| Appliance class | Typical power | Signature |
|---|---:|---|
| Refrigerator compressor | 100–250 W | Cyclic, 15–30 min, continuous low baseload |
| Ceiling fan | 50–75 W | Flat, long duration |
| LED fixture | 7–20 W | Flat, low draw |
| CFL / incandescent | 40–100 W | Flat |
| Television | 60–120 W | Evening-heavy, flat |
| Washing machine | 300–500 W, spin spikes 1000 W+ | Cyclic bursts |
| Water heater / geyser | 1,500–2,000 W | Sustained 15–30 min |
| Split AC (1–1.5 ton) | 1,200–1,800 W running | Sustained / cyclic compressor |
| Microwave | 1,000–1,500 W | Short burst |
| Kettle | 1,500–2,000 W | Very short burst, 3–5 min |
| Iron | 1,000–1,600 W | Intermittent medium burst |
| Water pump | 500–1,100 W | Short scheduled burst |
| Desktop computer | 150–300 W | Flat, variable |
| Laptop charger | 45–90 W | Flat, low |
| Mixer / grinder | 300–750 W | Very short burst |

**Efficiency flag:** raise "possibly inefficient" when a matched event's steady-state draw exceeds its class ceiling by a configurable margin, default **>20%**. Heuristic hint, not a certified measurement.

**Evaluation:** score this detector against the appliance ground truth in `ai_energy_intelligence_dataset.csv` and report precision/recall per class. The UI wording stays *likely appliance class* regardless of the score.

---

## 8. Safety indicators (replay-only)

The safety tab exists, and it is the one place where evidence badges are mandatory.

**Source:** labelled safety-sensor events in `ai_energy_intelligence_dataset.csv`. Nothing on this tab is computed from the 12-meter telemetry, because leakage current and N–E voltage are not present in and not derivable from aggregate L–N measurements.

**Wording policy — every safety card must:**
1. Head with a *likely / possible* fault hypothesis plus a confidence value.
2. Show the measured evidence (voltage sag magnitude, duration, leakage current, N–E voltage).
3. List credible alternative causes.
4. State that the system cannot confirm the diagnosis and that persistent events need a qualified electrician.
5. Carry a `Simulated` badge.

**Never** convert aggregate kWh alone into a wiring, earthing or leakage claim.

**Renaming required:** the dataset label `Possible Loose Connection / Voltage Sag` is displayed as **`Voltage Sag — Possible Wiring or Supply Issue`**. A voltage sag alone is not proof of a loose connection.

---

## 9. Cost, manual input, and recommendations

### 9.1 Tariff configuration
Bundle a dated config: `config/kseb_domestic_tariff_YYYY_MM.json`, containing telescopic slab bands, fixed charges and time-of-day rules, with a source and effective date. Never hardcode rates inside model logic. Verify against the current KSERC/KSEB tariff order before the demo.

### 9.2 Manual input panel (the only form in the app)
Accepts **slab values** and a **power-usage figure**. It feeds:
- the bill estimate and slab-cliff warning
- what-if comparison against the dataset-derived projection

It does **not** feed forecasting, anomaly detection or appliance inference. A single typed total cannot create a credible interval history, and mixing it into the models would corrupt the baselines. Label the panel as an estimator, not a data source.

### 9.3 Calculations
```
daily kWh              = sum(interval consumption)
monthly projected kWh  = daily / observed days × calendar days
monthly projected cost = tariff function(monthly projected kWh)
excess kWh             = observed kWh − forecast / baseline kWh
potential saving       = avoidable excess kWh × applicable tariff rate
slab-cliff warning     = projected kWh within N units of the next band edge
```
All billing, savings and slab logic is deterministic and unit-tested. All savings figures are labelled estimates.

### 9.4 Greedy scheduling
For each detected flexible-load-like event: estimate duration and energy, scan the next 24 hours, compare demand forecast against tariff periods, find the least-cost contiguous window of sufficient length, and recommend it with an estimated saving.

---

## 10. LLM boundaries

The backend emits a facts-only JSON sheet:
```
timestamp, actual_kwh, forecast_kwh, z_score, isolation_forest_flag,
wastage_score, event_duration_minutes, likely_appliance_class,
voltage_status, power_factor_status, safety_event (nullable),
estimated_cost, slab_status, recommended_window
```

Groq turns these into a short English explanation plus one to three recommendations.

**Prompt rules:** use only the supplied facts; preserve every number exactly; never calculate a forecast or a bill; never confirm an electrical diagnosis; quantify a saving only when the backend supplied it; distinguish observation from suggestion.

Use schema-constrained output and validate that every number cited appears in the fact sheet. **Fall back to deterministic templates** if Groq fails or validation fails — a Groq outage must not break the demo. The chatbot is read-only and answers only from precomputed facts. Select the exact Groq Llama model ID from current Groq documentation at implementation time; do not guess it.

---

## 11. Architecture

```
data/raw → audit/adapters → data/derived
   ↓
Python pipeline + scikit-learn / XGBoost  (offline, versioned artifacts)
   ↓
SQLite
   ↓
Django REST API
   ├── /consumption
   ├── /forecast
   ├── /insights
   ├── /appliances
   ├── /power-quality
   ├── /safety
   ├── /cost          (+ POST for the slab/usage estimator)
   └── /chat
   ↓
React (Vite) + Recharts + Axios + React Router
```

No endpoint accepts appliance inventory or account configuration. The replay API implements the same internal provider contract a future authorised KSEB adapter would use.

**Dashboard tabs**
1. **Consumption** — 15-min and hourly usage, actual vs forecast, daily trend
2. **Appliances** — detected step events, likely class, duration, efficiency hint
3. **Power quality** — voltage, PF, current, limit alerts
4. **Safety** — replayed labelled events, hypothesis wording, `Simulated` badge
5. **Cost** — projected kWh and cost, slab-cliff warning, manual estimator, cheaper-window suggestions
6. **Ask** — read-only facts-grounded Q&A
7. **Evidence drawer** — dataset provenance, split policy, model version, MAE/MAPE, anomaly precision/recall/F1

---

## 12. Implementation order

```
 1. Audit all three datasets; write reports/data_audit.md
 2. Build adapters; emit data/derived
 3. Load and validate one selected meter
 4. Build 15-min / hourly / daily aggregates
 5. Engineer time and rolling features (labels excluded)
 6. Build consumption and trend charts
 7. Run the forecast bake-off; ship the simplest winner
 8. Add Isolation Forest + contextual z-score baseline
 9. Implement wastage scoring and explainable alerts
10. Add appliance step detection; evaluate against ground truth
11. Add voltage / PF / current rules
12. Add safety replay tab with badges and hypothesis wording
13. Add tariff config, cost engine, slab-cliff warning, manual estimator
14. Add greedy scheduling recommendations
15. Expose facts through Django REST
16. Build React tabs, Groq narration, deterministic fallback
17. Build the evidence drawer
```

---

## 13. Demo journey

1. Open directly on the populated `SM-KL-001` dashboard — no login, no onboarding.
2. Show actual vs forecast, including one unusual-looking event that is correctly *not* flagged.
3. Replay a true wastage event: evidence, z-score, cost impact.
4. Show the end-of-cycle forecast and slab-crossing risk.
5. Show an appliance event with its likely class and efficiency hint.
6. Open the safety tab: one event, hypothesis wording, alternatives, `Simulated` badge, electrician disclaimer.
7. Enter a slab value in the estimator; show the what-if bill.
8. Ask the chat: "Why is my bill higher and what should I do today?" — the answer cites only the visible fact sheet.
9. Open the evidence drawer: provenance per dataset, split policy, model version, metrics.

**Stage reliability:** seed the demo household and precompute predictions. Cache the central advisory answer. Offer live inference and live chat as secondary proof, not as the critical path.

---

## 14. Deferred until implementation

- Exact Groq Llama model ID
- Final forecast winner after leakage-safe evaluation
- Final anomaly threshold tuning
- Exact KSERC/KSEB tariff version, verified against the current official order
- Per-dataset role confirmation after the audit (provisional roles in §3 hold until then)

---

## 15. Build-ready prompt

```
Build a single-household, local-only "AI Energy Intelligence" web app.
No hardware, no cloud deployment, no authentication.

STACK: React (Vite) + Recharts frontend, Django REST Framework backend,
SQLite, scikit-learn + XGBoost, Groq API for narration. Runs on one machine.

DATA: three CSVs in data/raw/, read-only.
 - synthetic_smart_meter_15min.csv (12 meters, 32,256 rows, 15-min V/I/PF) —
   PRIMARY, drives the dashboard. Demo meter SM-KL-001.
 - ai_energy_intelligence_dataset.csv (1 household, 5,760 rows, appliance /
   anomaly / wastage / safety labels) — evaluation ground truth AND the only
   source for the safety tab. Ignore its ageing-factor labels.
 - Intelligent_abnormal_electricity_usage.csv (360 homes, 10,800 daily rows,
   Abnormal_Usage label, undocumented provenance) — offline daily-granularity
   benchmark only. Never shown in the UI, never merged with 15-min data.

STEP 0: write scripts/audit_datasets.py producing reports/data_audit.md.
Check invalid ranges, timestamp gaps/duplicates/timezone drift, cumulative-vs-
interval and P-vs-VIcosφ formula consistency, label contradictions, and schema
mismatches. Correct only in data/derived/. Never mutate data/raw/. Never delete
rows to improve metrics. Preserve intentional anomaly and fault events.

PIPELINE:
1. Load derived data, filter to one meter_id, parse timestamps as +05:30,
   assert one record per 15-min interval.
2. Build 15-min, hourly and daily aggregate tables.
3. Features on hourly rows: hour, day_of_week, is_weekend, month,
   lag_1h/2h/24h/168h, rolling_mean_3h/24h, rolling_std_24h, voltage_mean,
   voltage_min, power_factor_mean, real_power_max. Chronological split only.
   NO label column may enter the feature matrix.
4. Forecast bake-off: seasonal-naive vs RandomForestRegressor vs XGBoost on an
   identical split. Report MAE/RMSE/MAPE. Ship the SIMPLEST model that is not
   beaten by a meaningful margin. Save a versioned artifact with metadata.
   Training runs offline in scripts/train.py, never in a Django request.
5. Isolation Forest on the feature matrix, plus a per-(hour, is_weekend)
   baseline mean/std lookup and a z-score per reading.
6. Wastage score 0-100 as an explicit auditable formula over z-score,
   Isolation Forest flag, persistence duration and night-time weighting.
   Do NOT train a classifier to reproduce this formula.
7. Appliance step detection (ΔP threshold + minimum duration) matched to a
   bundled table of typical Indian appliance wattages. Flag "possibly
   inefficient" at >20% above the class ceiling. Evaluate precision/recall
   against the appliance ground truth; keep UI wording as "likely class".
8. Power quality rules: voltage outside 216-244 V, persistently low PF,
   current/power above connected_load_kw. Computed from real columns only.
9. Safety tab: replay labelled safety events from ai_energy_intelligence_
   dataset.csv ONLY. Never infer leakage/earthing/arc from aggregate kWh.
   Each card shows a "likely/possible" hypothesis + confidence, the measured
   evidence, alternative causes, an electrician disclaimer, and a "Simulated"
   badge. Rename "Possible Loose Connection / Voltage Sag" to
   "Voltage Sag - Possible Wiring or Supply Issue".
10. Cost engine from config/kseb_domestic_tariff_YYYY_MM.json (dated, sourced).
    Daily/monthly projection, slab-cliff warning, excess cost, savings.
    Deterministic and unit-tested.
11. ONE manual input panel: slab values + a power-usage figure, feeding the
    bill estimate and what-if only. It must not feed forecasting, anomaly
    detection or appliance inference.
12. Greedy scheduler: for each deferrable-load-like event, scan the next-24h
    forecast against the tariff table, return the cheapest sufficient
    contiguous window and the estimated saving. No MILP, no RL.
13. Groq: pass ONLY the computed fact sheet. Schema-constrained output,
    validate every cited number against the sheet, fall back to deterministic
    templates on failure. The LLM never computes or decides anything.
14. Read-only chat over the same fact sheet. No device control.

API: Django REST endpoints /consumption /forecast /insights /appliances
/power-quality /safety /cost /chat. No endpoint accepts appliance inventory
or account configuration.

FRONTEND: tabs Consumption / Appliances / Power Quality / Safety / Cost /
Ask / Evidence drawer. Evidence badges appear on the Safety tab only.

DO NOT ADD: hardware integration, authentication, cloud deployment, appliance
ageing or drift detection, computed leakage/earthing/arc detection, a
multi-household dashboard, MILP or RL scheduling, or any appliance-inventory
form. If any seems necessary, stop and flag it rather than adding it.
```

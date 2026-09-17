# Decision Record — Finalized MVP Workflow

Status: **superseded** by [the combined workflow](11_final-workflow-combined.md),
2026-09-17. Retained as historical context only. Its authentication, cloud,
manual-input, ageing and safety-processing choices are not current scope. Evidence tags remain as
defined in the research index: **[E]** paper evidence, **[I]** inference, **[X]**
project extension.

## Product decisions

| Area | Final decision | Consequence |
|------|----------------|-------------|
| Primary user | Kerala households | KSEB/KSERC terminology, tariff and household context are primary. |
| Product form | Responsive web application | Desktop-first dashboard with usable mobile layout. |
| Main demo entry | Dashboard opens immediately with a populated demo household | No onboarding gate before the value demonstration. Manual inputs remain accessible from settings/input flows. |
| Authentication | Simple email/password login | Use Django authentication; do not add OTP to MVP. Demo account/session must not block the landing dashboard. |
| Control level | Advisory only | No automatic or remote appliance switching in the MVP. |
| UI language | English only | Malayalam remains future work. |
| Primary success criterion | Demo experience | Maintain technical metrics in an evidence/evaluation screen, but optimize the main journey for clarity and responsiveness. |
| Advisor interface | Dashboard insight cards plus conversational chat | Both consume the same structured fact sheet. Chat must not query raw CSV data directly. |

## Data and integration decisions

1. **Demo source:** dataset replay only; no live IoT node is required for MVP.
2. **Authoritative files:** the datasets already under `data/`:
   - `synthetic_smart_meter_15min.csv`: 12 simulated households, 32,256 rows,
     15-minute smart-meter-style V/I/PF and consumption data.
   - `Intelligent_abnormal_electricity_usage.csv`: 360 simulated households,
     10,800 daily records, including abnormal-use labels.
   - `ai_energy_intelligence_dataset.csv`: one simulated household, 5,760
     15-minute records over 60 days, including appliance ground truth, anomaly,
     waste, ageing-factor and add-on safety-sensor labels.
3. `synthetic_smart_meter_15min.csv` and `ai_energy_intelligence_dataset.csv`
   are explicitly synthetic **[X]**. `Intelligent_abnormal_electricity_usage.csv`
   is a community/Kaggle fixture with undocumented collection and label provenance;
   it must not be called measured KSEB data or proven synthetic. UI, reports and
   presentations distinguish these statuses, and no accuracy number may be
   presented as field validation on live Kerala households.
4. **Audit and repair is authorized:** preserve raw source files and intentional
   anomaly/fault events. Implement reproducible adapters that correct/represent
   invalid values, timestamp issues, formula/tariff inconsistencies, label
   contradictions and schema/documentation mismatches in derived data. Do not
   silently delete difficult rows or mutate raw CSVs to improve metrics. Maintain
   an audit report and a reproducible transformation/generator.
5. Assigning final model roles to each dataset is conditional on the audit.
   Provisional recommendation: 12-meter data for forecasting/patterns; 360-home
   daily data for population anomaly classification; richly labelled one-home
   data for appliance/wastage/safety replay. Do not merge incompatible
   granularities into one flat training table.
6. Initial user data entry is manual values (units and relevant household fields)
   based on the dataset schema. Manual totals support bill/what-if analysis; they
   do not create a credible interval history for forecasting/anomaly detection.
7. KSEB smart-meter connectivity is future integration. The MVP may show a
   disabled **“KSEB smart-meter connection — coming soon”** adapter. There is no
   verified public consumer API in the attached evidence; never imply a live
   KSEB connection. The replay API should implement the same internal provider
   contract expected of a future authorized adapter.

## Feature evidence tiers

All four requested differentiators remain in the product, but they do not have
equal evidence status:

1. **Complete MVP:** consumption monitoring, patterns, forecasting, contextual
   anomaly/wastage analysis, KSEB billing and slab-cliff warning, recommendations.
2. **Evaluated prototype:** lightweight appliance identification/NILM only where
   available appliance ground truth allows quantitative evaluation.
3. **Clearly simulated experimental modules:** appliance-health drift and safety
   indicators.
4. **Roadmap/research:** definitive loose-connection diagnosis, earthing
   diagnosis, field-validated appliance ageing, deep NILM and automatic HEMS.

### Safety wording policy

The preferred UI includes a likely fault *label*. Technical limitation: available
signals do not establish a definitive cause. Therefore the implementable policy is:

- Heading may name a **“likely/possible fault hypothesis”** and confidence.
- Always display the measured evidence (for example voltage sag magnitude,
  duration, leakage current, N–E voltage).
- Always list credible alternative causes.
- Always state that the system cannot confirm the diagnosis and persistent
  events require a qualified electrician.
- Never convert aggregate kWh alone into a wiring, earthing or leakage claim.
- Rename the current synthetic label `Possible Loose Connection / Voltage Sag`
  for user-facing output to `Voltage Sag — Possible Wiring or Supply Issue`.
  A voltage sag alone is not proof of a loose connection.

## AI/ML boundary

The accepted architecture is **ML detects and predicts; deterministic services
calculate; the LLM explains and advises**.

### Offline/training pipeline

Historical project datasets → validation/adapter transformation → preprocessing → feature
engineering → time/household-aware train/validation/test split → baseline and
candidate training → evaluation → versioned artifact and metadata.

Training must not execute inside Django API requests or application startup.
Each artifact records model name/version, feature schema, dataset version,
training timestamp, metrics and split policy.

### Online/inference pipeline

Validated request/replay event → shared preprocessing → loaded versioned model →
prediction/anomaly/appliance facts → billing and optimization services → stored
result → fact-sheet builder → Groq advisor → React dashboard/chat.

### Models

The system contains multiple bounded components, not one “AI model”:

- Forecast model: compare seasonal-naive baseline, Random Forest and XGBoost;
  retain the simplest model that wins on held-out time/households.
- Anomaly engine: forecast residuals/rules plus an evaluated detector; do not
  treat provided labels as an input feature.
- Appliance component: use ground-truth appliance fields for evaluation only;
  ensure no target leakage into model inputs.
- Optimization and KSEB billing: deterministic rules/calculation, not LLM.
- Safety: measured-signal rules/statistical model, not LLM.

## LLM role and guardrails

Groq-hosted Llama is the energy advisor/reasoning-and-explanation layer. It may:

- explain consumption, forecasts, anomalies and appliance findings;
- answer “why did my bill increase?” using computed attribution;
- generate prioritized, personalized actions;
- explain likely causes without confirming electrical diagnoses;
- convert deterministic optimization output into a daily plan.

It receives a structured fact sheet, not raw sensor data. Prompt rules require:
use only supplied facts; preserve all numbers; never calculate a forecast or
bill; never confirm an electrical diagnosis; quantify savings only when the
backend supplied the calculation; distinguish observations from suggestions.
Use schema-constrained output and validate cited numbers against the fact sheet.
Fallback to deterministic templates if Groq fails or output validation fails.

## Technology architecture

### Frontend

- React + Vite
- Recharts
- Axios
- React Router
- Deployment: Vercel

### Backend

- Django + Django REST Framework
- Python, pandas, NumPy, scikit-learn, XGBoost
- Django services/apps for households, consumption, appliances, billing,
  forecasting, anomaly detection, optimization and LLM orchestration
- Deployment: Render or Railway (choose one during deployment work)

### Data and AI

- Neon PostgreSQL
- Groq API with a Llama model; exact supported model ID must be selected from
  current Groq documentation during implementation, not guessed.
- Secrets remain server-side only.

## Recommended main demo journey

1. Open directly on a populated Kerala demo-household dashboard.
2. Show actual vs expected consumption and one context-explained event that is
   *not* incorrectly flagged.
3. Replay a true wastage event; show evidence, anomaly score and cost impact.
4. Show end-of-cycle forecast, confidence range and slab-crossing risk.
5. Show appliance attribution/health as evaluated or simulated according to its
   evidence badge.
6. Show one safety-sensor event with likely-cause wording and disclaimer.
7. Open chat: ask “Why is my bill higher and what should I do today?” The answer
   cites only the visible fact sheet.
8. Open technical-evidence drawer: show each dataset's known provenance status,
   split policy, model version and metrics.
9. Show KSEB smart-meter adapter as coming soon, not connected.

## Implementation recommendations

- Make evidence badges (`Measured`, `Model estimate`, `Simulated`, `Future
  integration`) part of the UI rather than burying caveats in slides.
- Keep billing, savings and slab calculations deterministic and unit-tested.
- Prefer a seeded demo household and precomputed predictions for reliable stage
  performance; permit live inference from the same screen as secondary proof.
- Cache or template the central advisory answer so Groq failure cannot break the
  main demo, while visibly offering live chat when available.
- Do not optimize only for an attractive dashboard: retain forecasting MAE/MAPE,
  anomaly precision/recall/F1, tariff test results and recommendation-grounding
  checks in the technical view.

## Remaining decisions deferred until implementation

- Render vs Railway for Django deployment.
- Exact Groq Llama model ID supported at implementation time.
- Final forecasting/anomaly model winners after leakage-safe evaluation.
- Final per-dataset roles after the data audit.
- Exact KSERC/KSEB tariff version after verification against the current official
  tariff order.

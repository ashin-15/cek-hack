# 12 — Local MVP implementation record

2026-09-17. **[X]** This implements file 11; it does not reopen its locked scope.
No claim below is field validation. Generated metrics are recorded in
`reports/model_evaluation.json` and visible in the evidence drawer.

## Data and audit

**[I]** Original CSVs were relocated from `data/` to `data/raw/` without changing
bytes. Audit manifests retain hashes and row counts. Adapters produce canonical
aliases, timezone-aware timestamps and quality flags in `data/derived/`; they do
not overwrite source files. Every row is retained, including missing energy and
intentional labelled events. Primary ingestion rejects missing intervals,
duplicate timestamps and invalid telemetry. Audit range/label disagreements are
review candidates, not automatic label repairs.

**[I]** The daily community fixture contains 900 missing actual-energy rows, all
positive-labelled. Missingness, expected energy, source deviation and cluster
average are excluded from the feature matrix. The independent daily benchmark
reports scorable coverage and a conservative all-row metric where missing
positive cases count as misses. The daily benchmark remains offline only; its
role/provenance is listed in the evidence drawer, with no population screen.

## Forecast and anomaly decisions

**[X]** Hourly target at time t uses strictly earlier data. Electrical features
are shifted one hour; rolling energy statistics start from `shift(1)`. This
resolves the otherwise leaky use of same-hour real power to forecast same-hour
energy. The forecast matrix has an explicit allowlist. Labels cannot enter it.

**[X]** After a seven-day lag warmup, the primary forecast trains on August 8–21
and evaluates rolling next-hour predictions on August 22–28. The seasonal-naive
prediction is the same hour one week earlier. Fixed RF/XGBoost hyperparameters
are compared on identical rows. The simplest model within 5% of the lowest MAE
wins; this engineering margin was chosen before fitting. The holdout chooses the
model and is not an additional untouched final generalization test.

**[X]** Random Forest wins the simplicity rule (MAE 0.02980 kWh, RMSE 0.04684,
MAPE 13.177%). XGBoost MAE is 0.02937; seasonal-naive MAE is 0.03205. The final
winner is refit on available history for future forecasts only. Recursive 24h
forecasting substitutes predictions for future lagged energy and fixed trailing
week same-hour profiles for unobserved electrical covariates. Its multi-step
accuracy is **not** claimed from one-hour metrics.

**[X]** Isolation Forest is fit on training features only. Same-hour/day-type
means and standard deviations are also training-only, with a 0.02 kWh standard
deviation floor. The explicit wastage score is contextual evidence (0–35), IF
flag (0 or 20), relative baseline excess (0–25), persistence (0–15), and night
weight (0 or 5). Scores are zero unless z > 2.5; alerts start at 50. No classifier
learns this rule. Configuration lives in `config/analytics.json`.

**[X]** The independent labelled household evaluates the same unsupervised
method, fitted to its own earlier history and tested on its final 14 days.
Hourly labels are the maximum of four interval labels, read only after scoring.
Current anomaly precision/recall/F1 are 0.3478 / 0.8000 / 0.4848. These weak
precision results remain visible. The selected meter has no truth labels;
its example is a computed candidate, never a “true wastage” claim. A separate
labelled waste replay appears in Ask with its own source and cost reference.

## Appliance and safety limits

**[X]** Sustained positive steps are tracked to a return toward the preceding
baseline (negative step), with at least two observed intervals and a 12-hour
cap. Power and duration jointly rank reference classes. Power matching allows
up to 1.6× the ceiling so the >20% over-draw heuristic is reachable. Overlapping
loads remain an explicit alternative; matching is low-confidence.

**[I]** Fifteen-minute sampling cannot reliably resolve 3–5 minute kettle events
or short mixer bursts. The reference table retains these classes but does not
pretend they are observable. Only refrigerator, HVAC and water-heater labels
identify a class separately. Lighting and plug-load labels are grouped and
cannot establish fixture/fan/computer identity. Precision/recall measures
held-out interval occupancy, not certified device identification. Zero recall
for a class is preserved. No ageing-factor field is used.

**[X]** No primary flexible-load event currently meets these coarse matching
rules, so scheduling shows an empty state. The greedy algorithm is implemented
and tested, including partial-hour windows and tariffs spanning midnight. It
ranks cost first, demand second. It cannot know user comfort constraints and
only suggests windows, never switches devices.

**[I]** Safety uses only the separate labelled add-on fixture. Four consecutive
labelled-event groups supply sag, residual current, neutral–earth voltage and
duration. The source has no calibrated confidence or diagnostic probability.
To avoid inventing one, cards carry `confidence: null` and “Not calibrated”,
with alternatives, the required renamed sag hypothesis, a Simulated badge and
an electrician disclaimer. This is the explicit limitation to file 11’s request
for a confidence value. No aggregate kWh or selected-meter V/I/PF produces a
safety diagnosis.

## Tariff and narration sources

**[I]** Rates were verified against the official [KSERC Gazette schedule,
5 December 2024](https://dev.erckerala.org/api/storage/orders/vnp1XnN5z47r0dCh18rj3s2e1q2utii3T8AtwUMm.pdf),
LT-I page 5 and Annexure E page 40, effective April 2025–March 2027. Configuration
includes telescopic and whole-month rates, fixed charges and conditional ToD.
The demo is single phase and has no documented ToD enrollment. Its shifting
savings must therefore be zero. The estimate is a **monthly energy-plus-fixed
subtotal**, excluding unverified levies, subsidies and concessions. It is not
an official KSEB invoice. Slab-edge warnings include the whole-month cliff.

**[I]** On implementation day the [Groq models catalogue](https://console.groq.com/docs/models)
lists `llama-3.3-70b-versatile` as enterprise access. [Groq structured-output
documentation](https://console.groq.com/docs/structured-outputs) does not list
Llama for native strict JSON-schema mode. The integration therefore uses JSON
object mode and local JSON-schema validation with enum-constrained factual
sentences. It checks every numeric token against the fact sheet. Selecting
approved observations/suggestions also prevents semantically invented claims
that numeric matching alone would not catch. The LLM never computes or
executes actions. Vendor errors, absent credentials, schema/grounding failures
and timeouts return deterministic templates. No live authenticated Groq call
has been verified; fallback and malformed-response behavior are tested.

## Local operation and verification

**[X]** SQLite stores precomputed section snapshots behind an internal provider
contract. Seeding updates them in one transaction after offline evaluation.
Each artifact directory has a unique timestamp, model/schema/configuration,
source/derived hashes, dependency versions, training time, metrics and split
policy. Startup only serves snapshots; it never runs training. The optional
`GET /forecast?live=true` reruns inference from the saved artifact without fitting;
its output uses the same forecast path as offline preparation. Chat has no
raw CSV access. Manual estimator inputs never modify snapshots or features.

**[I]** Read-only chat is the explicitly scoped question interface; the single
numerical input panel remains the cost estimator. No onboarding, configuration,
authentication, inventory, cloud, hardware or multi-household view was added.

**[X]** Verification includes tariff boundary goldens, negative/NaN validation,
what-if isolation, scheduler eligibility and duration, no-future-data feature
checks, label mutation invariance, raw hashes, row retention, replay provenance,
API status/validation, and Groq outage/hallucination fallback. Playwright covers
the full desktop flow and mobile layout with a real local API. README contains
reproduction commands. Browser screenshots are temporary validation artifacts.

## Continuation checkpoint

**[I]** The repository-root [AI handoff](../../progess.md) records the completed
implementation, verification commands, limits and current uncommitted workspace.
During handoff preparation, fetching `origin/main` revealed commit `89441a6`,
which renames file 10 to `10_workflow_decisions.md` and removes the tracked root
`env` file. Fast-forward integration stopped to protect local edits to file 10.
Reconciliation is pending; preserve the implementation and the upstream deletion.

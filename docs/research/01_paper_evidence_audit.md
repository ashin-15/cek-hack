# 01 — Paper Evidence Audit

Purpose: establish exactly what the three attached papers demonstrate, what they
defer to future work, and what they do **not** show, so downstream scoping never
over-claims. Tags: **[E]** evidence, **[I]** inference, **[X]** extension (see README).

---

## Paper [A] — Electricity Demand Forecasting in Kerala using ML (CONIT 2023)

### What is demonstrated [E]

| Item | Detail | Where |
|------|--------|-------|
| Data | ~10 years (Jan 2013 – Dec 2022) of **state-level daily demand (MW)** from KSEB, joined with weather (temperature, dew point, humidity, pressure, wind speed) from a weather website and population density | §III.H "Dataset" |
| Pre-processing | Cleaning, normalisation, train/test split. Targets appear min-max scaled (plots span 0.1–0.7; RMSE 0.054 is unit-less) | §III, Figs 2–15 |
| Models compared | LR, Decision Tree, Random Forest, SVR, KNN, XGBoost, ANN | §III.A–G |
| Result | Random Forest best: "accuracy" 82.72 %, MAE 0.038, MSE 0.002, RMSE 0.054; XGBoost essentially tied (82.11 %, same MAE/RMSE) | Table VIII, §V |
| Design insight | Weather + calendar are the chosen exogenous features; authors report "strong correlation with electricity demand" (assertion, no correlation table shown) | §III.H |

### Stated limitations / future work

The paper has no explicit future-work section. Limitations are only implicit via
the related-work critique (§II): LSTM hyper-parameter sensitivity [9], ARIMA
trouble with peaks [6], meter heterogeneity across consumers [11].

### What is NOT demonstrated (do not cite [A] for these)

- Anything at **household** granularity — the target is the whole Kerala grid.
- Sub-daily (hourly/15-min) forecasting.
- Anomaly detection, wastage detection, disaggregation, faults, recommendations.
- Feature importance / correlation analysis (asserted, not shown).
- A defined "accuracy" metric for regression (most likely R² or 1−MAPE; the paper never says). Two different values appear (82.72 % in Abstract/Table VIII vs 82.55 % in §IV.B), and the date range differs between §III.H (to Dec 2022) and §V (to Dec 2023). Treat exact figures as indicative only.

### Reusable for us

- Justifies tree-ensemble regressors with weather + calendar covariates for Kerala demand [E].
- Gives a Kerala-specific reference dataset design (features list) [E]; we can replicate with public Grid-India/KSEB daily data [I].

---

## Paper [B] — AI-Enabled Smart Energy Optimization System (IJST 2026)

### What is demonstrated [E]

| Item | Detail | Where |
|------|--------|-------|
| Input model | User **manually enters** appliance inventory: device type (one-hot, 10+ categories), rated watts, daily hours, count, seasonal multiplier | Methodology B.ii |
| Baseline formula | E = W × H × D × N / 1000 (D = 30) used as theoretical baseline; ML learns deviation from it (standby, usage variability, "efficiency degradation" cited as *motivation*, not measured) | B.ii |
| Model | Random Forest regressor (scikit-learn) on ~8,000 records of "detailed Indian household consumption data" (source not specified). RMSE 8.2 kWh, MAE 6.1 kWh, R² 0.96, 12 ms/appliance inference; vs GB 9.7 / LR 18.4 / shallow NN 10.1 | B.iii, Table 2 |
| Validation | **MAPE 6.8 %** against real DISCOM bills for test households (count not stated) | Testing Results A.i |
| Billing engine | Slab-wise progressive tariff; energy charge, fixed charge, electricity duty, fuel-adjustment charge; configurable per DISCOM; validated against actual bill breakdowns | B.iv, Testing A.iv |
| LLM advisory | Structured prompt (inventory, per-appliance kWh, bill breakdown, national-average benchmark) → Groq-hosted LLaMA-3-8B as "energy auditor" → 3–5 quantified recommendations, streamed | B.v |
| Stack / deployment | HTML/CSS/JS + Flask + PostgreSQL on Render free tier; OTP, bcrypt, HttpOnly cookies; <500 ms warm, 15–30 s cold start; 8 screens; PDF export | A.i–v, B.vi, Testing A.ii/v/vi |

### Stated limitations [E] (Discussion B)

1. Accuracy bounded by **user-entered hours/usage**; model "may overlook unexpected changes in behaviour or unusual consumption".
2. **No smart-meter or IoT real-time data** — cannot react to changing parameters.
3. Predetermined tariff tables → regional discrepancies.
4. LLM outputs may be incomplete/inconsistent; accuracy hard to guarantee.
5. Grid-only; no solar/net-metering.

### Stated future work [E] (Discussion C)

IoT/smart-meter real-time data; multi-state tariff support; mobile app; user-behaviour analysis for personalised strategy; solar + net metering.

### What is NOT demonstrated

- No time-series data at all: inputs are static declared usage; there is no
  interval consumption, so no pattern analysis, anomaly detection, or forecasting
  in the time-series sense. "Forecasting" here = predicting monthly kWh from
  declared usage.
- No appliance disaggregation from a meter signal — appliance split comes from
  what the user typed.
- No detection of efficiency degradation, ageing, or faults (the words appear
  once as a *reason* for non-linearity, never as a capability).
- No evaluation of the LLM recommendation quality (no user study, no savings measured).
- Internal inconsistency: Table 2 shows RF (8.2) beating GB (9.7), but §Testing
  A.iii says the RF "only marginally underperforms" GB by 15 %. Also "monthly"
  (Abstract) vs "daily" (B.iii) consumption target. Dataset provenance is unspecified.

### Reusable for us

- Architecture template (Flask API + Postgres + LLM-as-phraser + slab engine) is proven deployable [E].
- The **slab-crossing insight** ("small increases push users into higher slabs") is explicitly motivated [B Introduction] but implemented only as a static calculator — a forecast-driven version is open space for us [X].
- Its limitation #1/#2 is exactly the gap our IoT/time-series design fills [I].

---

## Paper [C] — Predictive Analytics for Energy Efficiency (Energies 2024)

### What is demonstrated [E]

| Item | Detail | Where |
|------|--------|-------|
| Data acquisition | 13 appliances measured with **SEM8500 6-socket Wi-Fi energy-cost meter**, data pushed to **Tuya Cloud as JSON**, **30 days** in one household | §2, Fig 1–2 |
| Decision logic | **Algorithm 1**: rule-based. If ΣP_SA ≥ P_HEMS_H → "reduce"; if ≤ P_HEMS_L → "increase"; else by price level (cheap/standard/expensive) → increase/hold/reduce | §2, Alg. 1 |
| Price signal | **Assumed** three-level daily price schedule (Fig 3), not a real tariff feed | §2 |
| ML task | 7 classifiers (fine tree, logistic regression, kernel NB, linear SVM, Gaussian SVM, boosted trees, narrow NN) trained to reproduce the Algorithm-1 message from (time, per-appliance power, power sum, price); 5-fold CV; MATLAB R2024b | §3, Tables 1–2 |
| Results | With 1 day of data: kernel NB best, others weak. With ≥3 days: fine tree, linear SVM, Gaussian SVM, narrow NN reach ≈100 % accuracy; boosted trees ~20 % precision (worst); logistic ~70 %. Fine tree chosen for speed/size | §4, Figs 4–13 |
| Case study | ml1 (fine tree) produces message timeline for a daily schedule; messages change at ~06:00, 08:00, 16:00 aligned with price and P_HEMS_H | §4, Figs 14–15 |
| Deployability argument | Model size / prediction speed / training time compared to argue small models can run on constrained HEMS or smart-meter hardware | §4 Figs 8–10, §5 |

### Stated future work [E] (§5)

Battery storage in the decision; short-term price prediction and RES generation prediction as inputs; embedding in automated HEMS; behavioural studies of consumers.

### What is NOT demonstrated

- **The ML learns a deterministic rule it was labelled by.** Near-100 % accuracy
  means the classifier reproduced Algorithm 1, not that it discovered anything
  from consumer behaviour. It is *not* evidence that ML predicts user behaviour
  or optimises cost. (The paper itself is candid this is a simulation.)
- No real dynamic tariff, no real notifications sent to users, no measured savings, no user study.
- No forecasting of consumption, no anomaly detection, no disaggregation (appliance identity is known because each is on its own socket).
- The "excessive power draw which could potentially damage the electrical installation" remark (§2) is a single fixed threshold P_HEMS_H — **not** fault detection.
- Conclusion §5 contradicts the introduction: it states the work "does not consider the optimization of energy costs on the consumer side" whereas the stated primary objective was consumer cost minimisation. Cite the paper for the *data-acquisition method* and *small-model deployability*, not for cost-saving results.

### Reusable for us

- Direct precedent for per-appliance acquisition via consumer smart sockets → cloud JSON [E]; the same class of hardware is sold in India (Tuya-based plugs) [I].
- Message-based nudging ("reduce / hold / increase") as a UX pattern for non-technical users [E].
- Total-power upper threshold as a sanctioned-load / MCB-trip early warning [E] → we can extend to sanctioned-load compliance for Indian connections [X].

---

## Cross-paper summary

| Capability | [A] | [B] | [C] | Status for us |
|------------|-----|-----|-----|---------------|
| Aggregate demand forecasting (daily, weather-driven) | **E** | – | – | Replicable |
| Household monthly kWh + bill prediction from declared inventory | – | **E** | – | Replicable |
| Slab-aware Indian billing engine | – | **E** | – | Replicable |
| LLM-phrased recommendations | – | **E** | – | Replicable (guardrails needed, [B] lim. 4) |
| Per-appliance measurement via smart sockets | – | – | **E** | Replicable (hardware) |
| Price/threshold-based consumption nudges | – | – | **E** (simulated) | Replicable |
| Interval time-series pattern analysis | – | – | partial (30-day profiles, no analytics) | **[I]** |
| Anomaly / wastage detection | – | – | – | **[I]/[X]** |
| NILM / disaggregation | – | – | – | **[I]** (well-established elsewhere, not in these papers) |
| Appliance ageing / efficiency drift | – | mentioned as motivation | – | **[X]** |
| Electrical fault detection (loose, earth, leakage) | – | – | threshold only | **[X]**, needs extra sensors — see 03 |

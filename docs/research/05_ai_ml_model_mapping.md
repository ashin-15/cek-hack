# 05 — AI / ML Model Mapping per Capability

Answers: *where should AI/ML be used, which model classes fit each capability and
why; which are supported by the papers vs. proposed extensions.* Tags per README.

## Guiding principles [I]

1. **Rules first, ML where rules fail.** [C] shows a rule (Alg. 1) can be the
   ground truth and ML merely compresses it [E] — that is a warning: do not use
   ML to re-learn a rule you can write. Use ML where the expected value is
   genuinely unknown (forecasting, baselines, anomaly scores).
2. **Tree ensembles are the default regressor.** Both [A Table VIII] and
   [B Table 2] found RF ≈ XGBoost/GBM best with millisecond inference [E].
   Use them unless a sequence model provably wins on our data.
3. **Uncertainty is a feature.** Slab-crossing and anomaly decisions need
   intervals, not point estimates → quantile/conformal methods.
4. **LLM phrases, never computes.** Per [B Discussion B] limitation 4 [E].
5. **Cold start matters.** Households have days, not years, of data. Prefer
   models that work from ~2–4 weeks and improve online.

---

## 1. Consumption forecasting

| Horizon | Model class | Why | Support |
|---------|-------------|-----|---------|
| Next 24 h / 7 d interval kWh (household) | **Gradient-boosted trees (LightGBM/XGBoost) with lag, calendar, weather features**; global model across households + household ID/embedding | Handles non-linearity, mixed features, missing values; fast; [A] and [B] show RF/XGBoost are top performers in both electricity settings | **[E]** model family via [A Table VIII], [B Table 2]; interval/household application **[I]** |
| Same, baseline | Seasonal naive (same hour last week), SARIMA/Prophet-style | Cheap benchmarks; [A §II] cites ARIMA literature and its weakness on peaks [E] | [E] as baseline |
| Same, if data volume allows | N-BEATS / Temporal Fusion Transformer / LSTM | Better on long multi-household series; [B Lit. Review] notes LSTM cost vs benefit [E]; [A §II] notes LSTM tuning burden [E] | **[X]** — only if time permits |
| End-of-billing-cycle total | **Quantile regression** (LightGBM quantile objective) or conformal prediction on top of the daily model, aggregated by Monte-Carlo sampling | Gives P(total > slab boundary) directly | **[X]** |
| Grid-level Kerala context | RF/XGBoost on daily MW + weather (replicate [A]) | Provides "state peak today" context and demand-response messaging | **[E]** |

**Features:** hour, day-of-week, holiday (Kerala/India calendar), temperature,
humidity, dew point ([A §III.H] feature list [E]), lags (1 h, 24 h, 168 h),
rolling means, outage indicator, declared inventory summary ([B B.ii] [E]).

## 2. Anomaly detection

| Approach | Model class | Why | Support |
|----------|-------------|-----|---------|
| **Forecast-residual scoring (primary)** | Residual = actual − expected (from §1 model); score via robust z (MAD) or conformal quantile bands per context | Directly encodes "abnormal relative to expectation", i.e. the problem statement's requirement; explainable ("expected 0.4 kWh, saw 1.6") | **[I]** — standard practice; none of the papers do it |
| Unsupervised density | Isolation Forest / LOF on per-interval feature vectors (P, hour, dow, temp, baseload) | Catches multivariate oddities without a forecast; cheap | **[I]** |
| Change-point detection | CUSUM, PELT (ruptures), Bayesian online change-point | Distinguishes a *regime change* (new appliance, tenant change) from a *spike*; feeds the ageing module | **[I]** |
| Sequence autoencoder | LSTM-AE / TCN-AE reconstruction error | Only with lots of data; heavier | **[X]** |
| Context labelling | Small classifier (fine tree / logistic) to tag anomaly *type*: spike, sustained, baseload step, night activity, tariff-window | Mirrors [C]'s finding that small trees suffice for discrete labelling [E] | **[I]** |

**No labels problem:** use synthetic injection (simulator) to build a labelled
validation set and report precision/recall on it; be explicit it is synthetic.

## 3. Appliance identification / disaggregation

| Route | Model class | Why | Support |
|-------|-------------|-----|---------|
| Declared inventory → consumption split | **Random Forest regressor** per appliance record (type, W, hours, count, season) → kWh | Exactly [B B.iii] (RMSE 8.2 kWh, R² 0.96, MAPE 6.8 % vs bills) | **[E]** |
| Event-based signature matching on 1 Hz aggregate | Edge detection (ΔP > threshold) → cluster (ΔP, ΔQ if available, duration, ramp) with **k-means/DBSCAN**, then **kNN / gradient-boosted classifier** to appliance class trained on public datasets (iAWE, UK-DALE) + user confirmation loop | Works for high-power, few-state appliances (geyser, AC, iron, pump, fridge compressor); interpretable | **[I]** — NILM literature; not in papers |
| Full NILM | Seq2point CNN, denoising autoencoders, FHMM | State of the art but data-hungry, poor cross-house transfer | **[X]** research track |
| Direct sub-metering | No ML; per-plug series | [C §2] [E] | **[E]** |

## 4. Appliance efficiency estimation

| Task | Model class | Why | Support |
|------|-------------|-----|---------|
| Rated vs actual efficiency | Deterministic: measured kWh per cycle / hour vs BEE-rated; ratio + confidence | No ML needed | **[I]** |
| Weather-normalised AC/fridge efficiency | **Linear/GBM regression** of daily appliance kWh on cooling-degree-hours & humidity; track model coefficient over time | Removes the largest confounder before judging drift | **[X]** |
| Drift / ageing detection | **CUSUM / Page–Hinkley on residuals** of the above; or Bayesian change-point on duty-cycle series; Kalman-smoothed trend of energy-per-cycle | Sequential detection with controllable false-alarm rate; works online | **[X]** |
| Remaining-useful-life | Survival models / degradation curves | Needs fleet failure data we do not have | **[X]** research only |

## 5. Fault detection (see file 03 for what is physically observable)

| Fault | Model class | Data | Support |
|-------|-------------|------|---------|
| Over/under-voltage, over-current vs sanctioned load | **Rules + statistics** (band, duration, frequency); no ML | D2 | [C Alg. 1] threshold [E]; rest [I] |
| Leakage current drift / step | CUSUM on I_residual; correlation of steps with appliance on-events (attributes the leaky appliance) | D3 | **[X]** |
| Wiring path resistance trend (two-point ΔV/I) | Robust linear fit of ΔV vs I per branch per week; trend test | D2 ×2 | **[X]** hypothesis |
| Series arc / loose connection | 1-D CNN or gradient-boosted classifier on HF current-waveform features | D4 | **[X]** research; hardware out of scope |
| Earthing | Not an ML problem; sensor threshold | D3 | **[I]** |

## 6. Energy optimisation

| Task | Model class | Why | Support |
|------|-------------|-----|---------|
| Nudge messages (reduce / hold / increase) | **Rule engine** (thresholds, price level, slab budget); optional tiny classifier only if rules become many | [C Alg. 1] rule and its ml1 replica [E]; ML added nothing beyond compression | **[E]** pattern; slab-budget extension **[X]** |
| Deferrable-load scheduling | **Constraint optimisation / MILP or greedy** over tariff windows, sanctioned-load ceiling, user comfort windows; inputs from forecast §1 | Deterministic, explainable, small problem size | **[I]** |
| Slab-budget pacing | Compare forecast cumulative kWh (with quantiles) vs slab boundary; recommend daily kWh budget | Turns [B]'s static slab engine into a control signal | **[X]** |
| Adaptive/learned control | Reinforcement learning (DQN/PPO) for HEMS | [C §1] reviews RL works; none needed at nudging level; data-hungry | **[X]** research |

## 7. Personalised recommendations

| Component | Model class | Why | Support |
|-----------|-------------|-----|---------|
| Insight generation (numbers) | Deterministic analytics from §1–6 | Trustworthy figures | **[I]** |
| Prioritisation | Ranking by ₹ impact × confidence × ease; optional bandit later | Simple, transparent | **[I]** |
| Phrasing | **LLM (hosted small model, e.g. LLaMA-3-8B on Groq, or local)** with structured JSON prompt of facts, persona "energy auditor", 3–5 items, quantified | [B B.v] [E] | **[E]** |
| Guardrails | Schema-constrained output; post-check every number appears in the input facts; fallback to templated text | Addresses [B Discussion B] limitation 4 [E] | **[I]** |
| Personalisation | Household segment (k-means on load-shape features) + feedback loop (accepted/dismissed) | [B Future Work] "user behaviour analysis" [E] | **[X]** |
| Language | Malayalam/Hindi output via the same LLM | Inclusion | **[X]** |

---

## Summary: paper-supported vs proposed

| Model class | Supported by papers | Our extension |
|-------------|--------------------|---------------|
| RF / XGBoost / GBM regression for kWh | [A], [B] | interval + quantile versions |
| Small tree/SVM/NB classifiers for discrete decision labels | [C] | anomaly-type labelling |
| Slab billing engine (deterministic) | [B] | probabilistic slab crossing |
| LLM recommendation phrasing | [B] | guardrails, local language |
| Forecast-residual anomaly scoring | — | primary anomaly method |
| Isolation Forest / change-point detection | — | anomaly + ageing |
| Event-based appliance signature matching | — (NILM literature) | lightweight disaggregation |
| CUSUM drift on efficiency metrics | — | appliance health |
| Residual-current analytics | — | safety add-on |
| RL / deep NILM / arc detection | — | research backlog only |

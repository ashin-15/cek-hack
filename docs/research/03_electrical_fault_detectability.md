# 03 — Electrical Fault & Appliance-Condition Detectability

Answers: *which of loose connections, earthing problems, leakage current,
voltage/current abnormalities, ageing appliances and inefficient appliances can be
detected from consumption data alone, which need extra sensors, and what
signals/features are required?*

**Bottom line first.** None of the three papers detect any electrical fault
(file 01). The only fault-adjacent element is a fixed total-power upper threshold
in [C Alg. 1] [E]. Everything below is **[I]** (standard electrical-engineering
reasoning) or **[X]** (our proposal). A standard interval smart meter reporting
kWh **cannot** diagnose loose connections, earthing defects or leakage. Do not
claim otherwise in a pitch.

## Data tiers used in this file

| Tier | What is available | Typical source (India) |
|------|-------------------|------------------------|
| **D0** | Monthly/bi-monthly kWh | KSEB bill, DISCOM portal |
| **D1** | 15/30-min interval kWh (+ maybe kVAh) | Smart-meter block-load profile via utility; daily kWh in consumer apps |
| **D2** | ~1 Hz active power, RMS V, RMS I, PF, frequency, energy | ESP32 + PZEM-004T / Shelly EM / Sonoff POW; smart-meter instantaneous DLMS objects; Tuya sockets [C §2] |
| **D3** | Residual (earth-leakage) current, neutral–earth voltage, per-circuit current | Extra CT around L+N together, N–E voltmeter, per-MCB CTs |
| **D4** | Sub-cycle waveforms (≥ 2–10 kHz sampling of V and I) | Custom ADC front-end, power-quality analyser |

---

## 1. Loose electrical connections

**Physics [I].** A loose terminal/joint adds series resistance and, under load,
produces (a) localised heating, (b) intermittent contact → micro-arcing, (c) a
load-dependent voltage drop downstream of the joint, (d) broadband high-frequency
noise and half-cycle asymmetry in the current waveform (what an AFCI/arc-fault
device looks for).

| Data tier | Detectable? | How |
|-----------|-------------|-----|
| D0/D1 | **No.** A few watts of I²R loss is invisible in kWh. | — |
| D2 (single point) | Very weak. Flicker of RMS V at the meter under constant load can hint at upstream looseness but is confounded by grid voltage variation. | Not recommended as a claim |
| D2 (two points) **[X]** | **Plausible.** If a smart plug reports its own RMS voltage while a known load runs, and the meter node reports supply voltage at the same instant, ΔV/I ≈ R_path for that branch. Trending R_path upward over weeks (with temperature normalisation) is a *wiring-health* indicator. | Needs time-aligned V readings from two devices; Tuya plugs report V but at low rate; accuracy ±1–2 V limits this to detecting *large* degradation. Prototype-able but unproven. |
| D4 | **Yes (research).** Series-arc detection from current-waveform HF content is how AFCIs work; ML on waveform features (spectral energy 1–100 kHz, shoulder width, cycle-to-cycle variance) is an active research area. | Needs custom hardware; not hackathon scope. |
| Non-electrical | Thermal camera / thermistor at the distribution board is the practical field method. | Out of scope. |

**Recommendation:** list "wiring-health trend (ΔV under load)" as an experimental
D2-two-point feature; state clearly it detects gross degradation, not incipient arcing.

## 2. Earthing problems

**Physics [I].** Earthing quality is a property of the earth electrode and the
protective-earth conductor. It is characterised by earth resistance (Ω) and shows
up under fault as neutral–earth voltage rise, touch voltage on appliance bodies,
and RCD/ELCB behaviour. Under normal load it has **no signature in L–N power flow**.

| Data tier | Detectable? |
|-----------|-------------|
| D0–D2 | **No.** Consumption data does not depend on earthing at all. |
| D3 (N–E voltage) | **Partly.** N–E RMS voltage persistently > ~2–5 V (varies by installation) suggests poor earthing or neutral problems; needs a voltage sensor between N and E — cheap (a second PZEM/ZMPT101B channel) but requires access to earth at the board. |
| D3 (earth resistance) | Only via a dedicated earth tester (fall-of-potential/clamp) — periodic manual test, not continuous. |

**Indian-context note [I].** Indian single-phase smart meters (IS 15959 / IS 16444
DLMS profile) log tamper/event classes including *neutral disturbance* and
*earth loading* (current imbalance between phase and neutral). These are
utility-side events intended for theft detection but physically correspond to
leakage/earth-return paths. They are **not** normally exposed to consumers; only
the utility HES sees them. Worth mentioning as a future integration, not as a
capability.

**Recommendation:** earthing cannot be a consumption-data feature. Offer a
"safety-sensor add-on" (N–E voltage + residual current) as a T2 hardware option
and an in-app checklist for a licensed electrician instead.

## 3. Leakage / abnormal current behaviour

**Physics [I].** Leakage means current returning via earth instead of neutral:
I_L − I_N = I_residual. Healthy household leakage is a few mA (appliance EMI
filters); insulation faults push it to tens–hundreds of mA; RCCBs trip at 30 mA
(personal protection) or 100–300 mA (fire).

| Data tier | Detectable? |
|-----------|-------------|
| D0–D2 (single CT on L only, as in PZEM/plug) | **No.** A single CT measures the L current; residual current is not observable. |
| D3 (CT around L **and** N together, or split-core on both with subtraction) | **Yes, directly.** Residual current in mA, continuous. Features: rolling mean/percentiles, step changes correlated with appliance on-events (identifies *which* appliance leaks), slow upward drift (insulation degradation), rain/humidity correlation (Kerala monsoon damp faults). |
| Smart meter event log (utility side) | Partially: *earth loading / current imbalance* tamper events [I], not consumer-accessible. |

**Recommendation:** residual-current monitoring is the **one electrical-safety
feature that is cheap, real, and gives clean ML features** (a second CT + the
same ADC). Position it as the "safety" differentiator if hardware is in scope.

## 4. Voltage / current abnormalities

| Abnormality | Signal | Tier | Detectable? |
|-------------|--------|------|-------------|
| Over/under-voltage (India nominal 230 V, tolerance roughly ±6 % → ~216–244 V; rural Kerala routinely sees 190–260 V) | RMS V outside band; duration; time-of-day pattern (evening sag) | D2 | **Yes.** Simple rules + statistics; useful for appliance-protection advice (voltage stabiliser recommendation, warranty risk). |
| Voltage sag/flicker on appliance start | Short RMS dips coincident with motor start (compressor, pump) | D2 at ≥1 Hz (better 10 Hz) | Partly; sag *magnitude* growing over time is also an ageing/wiring cue. |
| Over-current vs sanctioned/connected load | Total kW vs sanctioned load (KSEB connected-load basis) | D1/D2 | **Yes.** [C Alg. 1] upper threshold P_HEMS_H [E]; extend to Indian sanctioned load and MCB rating [X]. |
| Poor power factor | PF from D2; high reactive share indicates motor/inverter loads | D2 | Yes; informational for domestic (no PF penalty for LT domestic in Kerala, but kVAh data exists in smart meters). |
| Frequency deviation | Grid-wide; informational only | D2 | Yes, but not household-actionable. |
| Neutral break / phase issues (3-phase homes) | Per-phase V imbalance | D2 ×3 | Yes with 3-phase node. |
| Outage detection & duration | Data gap + V = 0 | D1/D2 | Yes; also cleans anomaly detection (gaps ≠ zero usage). |

## 5. Old / degrading appliances

**Principle [I].** Ageing shows up as *drift in a per-appliance efficiency metric*
under normalised conditions. Requires per-appliance (or reliably disaggregated)
data and a baseline of weeks–months, plus context normalisation (ambient
temperature, usage).

| Appliance | Degradation mechanism | Measurable feature (D2 per appliance) | Normalisation |
|-----------|----------------------|----------------------------------------|---------------|
| Refrigerator | Worn compressor, door-seal leak, refrigerant loss, dirty condenser | Compressor duty cycle ↑, on-time per cycle ↑, kWh/day ↑, start-up current ↑ | Ambient temperature; door-opening proxy (daytime vs 2–5 a.m. cycles) |
| Air conditioner | Refrigerant loss, dirty filter/coil, compressor wear | kWh per cooling-degree-hour ↑; time to reach set-point ↑ (if thermostat cycles visible); run fraction ↑ | Outdoor temp/humidity (Kerala: humidity matters); set-point |
| Water heater (geyser) | Scale on element, thermostat drift | Heating duration per use ↑; energy per heating event ↑ | Inlet water temp (seasonal), volume drawn |
| Ceiling fan / pump motor | Bearing wear, capacitor degradation | Power at same speed setting ↑; start-up current ↑; PF ↓ | Speed setting; for pumps, head/flow |
| Inverter/UPS battery (very common in Indian homes) **[X]** | Battery capacity loss, sulphation | Charging energy after each outage ↑ relative to outage duration; float current ↑; more frequent charge cycles | Outage duration (from data gaps) — a distinctly Indian feature |
| LED/CFL lighting, TV, set-top box | Minor; mostly standby creep | Baseload contribution | — |

| Data tier | Detectable? |
|-----------|-------------|
| D0 | Only extreme: multi-month kWh creep with no behavioural explanation — ambiguous. |
| D1 (whole-house interval) | **Weak but real for the fridge only [X]:** at 2–5 a.m. the aggregate is ≈ baseload + fridge cycling; the periodic component's duty cycle/amplitude is extractable by autocorrelation and can be trended. Other appliances are confounded. |
| D2 per appliance (plug/CT) | **Yes** with a ≥ 4–8-week baseline; change-point/drift detection on the features above. |
| Labels | There is no public labelled "ageing" dataset for Indian appliances; validation would rely on simulation, accelerated proxies (dirty filter experiment), or manufacturer spec vs measured. |

**Honest framing:** "appliance health trend" is an [X] feature. Demo it with a
synthetic drift injected into a real plug series and validate the detector's
sensitivity/false-alarm trade-off; do not claim field validation.

## 6. Inefficient appliances

Distinct from ageing: an appliance that is *working as designed* but is a poor
design or badly used.

| Method | Data | Feasibility |
|--------|------|-------------|
| Rated vs measured power (nameplate vs plug reading) | Declared inventory [B B.ii] + D2 plug | T1/T2; simple. |
| Benchmark vs BEE star-rating table (e.g. 5-star 1.5-ton AC ISEER vs measured kWh/h) | Public BEE datasets [I] + D2 | T1 (with inventory) / T2 (measured). |
| Share-of-bill ranking and payback calculator for replacement (₹ saved/yr vs price) | [B B.v] ranks appliances and recommends upgrades via LLM [E]; deterministic payback maths [I] | T1. |
| Behavioural inefficiency (AC set-point too low, geyser left on) | Pattern analysis (file 02 §4) | T1/T2. |

## Summary matrix

| Target | From kWh/interval data alone | With D2 node (V, I, P, PF @1 Hz) | Extra sensors needed | Papers |
|--------|------------------------------|----------------------------------|----------------------|--------|
| Loose connections | No | Gross only, two-point ΔV **[X]** | HF waveform (D4) or thermal | none |
| Earthing problems | No | No | N–E voltage, earth tester (D3) | none |
| Leakage current | No | No (single CT) | Residual CT (D3) — **cheap, recommended** | none |
| Voltage abnormalities | No | **Yes** | — | none |
| Over-current / sanctioned load | Coarse (interval peak) | **Yes** | — | [C Alg.1] threshold [E] |
| Appliance ageing | Fridge-only heuristic **[X]** | **Yes per-appliance**, long baseline **[X]** | plugs/CTs | [B] motivation only |
| Inefficient appliances | With declared inventory **[E via B]** | Better | — | [B] |

## Features to compute (for file 05)

- Per interval: P_mean, P_max, P_min, V_rms mean/min/max, I_rms, PF, ΔP events (edge count, magnitude histogram), I_residual mean/max (if D3).
- Per appliance-cycle (D2 plug): on-duration, off-duration, energy per cycle, peak start current, steady-state power, ramp shape.
- Daily: baseload (5th percentile of night power), kWh, peak kW, cooling-degree-hours, outage count/duration.
- Drift statistics: rolling median, CUSUM, Page–Hinkley statistic on each per-appliance efficiency metric.

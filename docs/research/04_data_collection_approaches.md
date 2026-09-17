# 04 — Data Collection Approaches (India / Kerala context)

Answers: *how can the system practically collect data from households; what does
each approach provide; what is realistic for a prototype?* Tags per README.
Data tiers D0–D4 are defined in file 03.

## Comparison table

| Approach | Data provided | Resolution | Cost / effort | Indian availability | Paper precedent | Hackathon verdict |
|----------|---------------|-----------|---------------|---------------------|-----------------|-------------------|
| **1. Utility bills / DISCOM portal history** | kWh per billing cycle (KSEB: bi-monthly for most domestic), slab, amount, connected load | D0 | Zero hardware; manual entry, PDF parse, or portal scrape (ToS risk) | Universal | [B] validates against DISCOM bills [E] | **Yes** — onboarding baseline & bill validation |
| **2. Existing smart meters (utility-owned)** | Meter stores block-load profile (15/30-min kWh, kVAh, avg V, avg I), daily energy, instantaneous V/I/PF, event logs (over/under-voltage, current imbalance/earth loading, neutral disturbance, magnet) per IS 15959 DLMS profile | D1 (+ D2 snapshots) | Consumer sees only what the utility app exposes (usually daily/monthly kWh, prepaid balance) | RDSS rollout underway nationally; Kerala penetration low so far — **verify current KSEB status** | [B] lists smart-meter integration as future work [E] | Only via **CSV export / manual upload** of whatever the utility app shows. No consumer API assumption. |
| **3. Smart-meter APIs** | Programmatic access to (2) | D1 | Requires utility partnership / HES access | No public consumer-facing API for KSEB known; some DISCOMs expose data inside their own apps only | none | **No** — design an adapter interface, mock it |
| **4. Smart-meter local port (optical/IR, DLMS/COSEM)** | Same objects as (2) read locally | D1/D2 | Optical probe + DLMS client (e.g. Gurux); many objects need utility-issued authentication keys | Meters have the port; keys not available to consumers | none | **No** for hackathon; note as research |
| **5. Whole-house IoT energy node** (ESP32 + PZEM-004T v3 / SCT-013 CT + ADC; or off-the-shelf Shelly EM, Sonoff POW Elite) | RMS V, RMS I, active P, energy, PF, frequency at ~1 Hz; CT clamp non-invasively on the main incomer | D2 | ₹1,000–3,000 DIY; ~₹3,000–6,000 off-the-shelf; needs distribution-board access, ideally installed by an electrician | Parts widely sold in India | [C §2] uses the plug-based equivalent [E] | **Yes (1 demo unit)** — richest signal per rupee |
| **6. Smart plugs (Tuya / Tasmota / Sonoff S31 / Shelly Plug)** | Per-appliance P, V, I, energy; state on/off; typically 1–60 s reporting | D2 per appliance | ₹700–1,500 each; 16 A variants needed for AC/geyser (Indian 16 A sockets) | Widely available (Wipro, Qubo, Tata Power EZ, generic Tuya) | [C §2] — SEM8500 6-socket → Tuya Cloud JSON [E] | **Yes (2–4 plugs)** — fridge, AC/geyser, TV/entertainment, washing machine |
| **7. Circuit-level monitoring** (CT per MCB, e.g. Emporia Vue-style, or multi-channel ADC) | Per-circuit P/I: lights, sockets, AC, kitchen, geyser | D2 per circuit | ₹4,000–10,000; electrician install; Indian homes typically have 4–8 circuits | Imported or DIY | none | **Optional** — good middle ground between 5 and 8; skip for hackathon unless team has EE capacity |
| **8. Appliance-level sensors** (manufacturer cloud: smart ACs, inverters, smart geysers) | Set-point, mode, compressor state, sometimes energy | Varies | Free if appliance is smart; vendor APIs inconsistent | Growing (Voltas, LG, Daikin apps; Luminous inverter apps) | [C §2] mentions SA manufacturer apps [E] | **No** (integration churn) |
| **9. NILM on aggregate** | Inferred per-appliance series from (5) | D2 → virtual per-appliance | Software only; needs ≥1 Hz data and training data | Public datasets exist incl. Indian **iAWE** | none | **Partial** — event-based signature matching for 3–5 high-power appliances [X]; not full NILM |
| **10. Safety add-on sensors** (residual CT around L+N, N–E voltmeter) | Leakage mA, N–E V | D3 | +₹500–1,500 on node 5 | DIY | none | **Optional demo** if pitching safety |
| **11. Manual meter photo / OCR** | Daily cumulative kWh from a phone photo of the meter | D0 → daily | Zero hardware; OCR reliability varies | Universal — critical for the majority of Kerala homes without smart meters | none | **Yes** [X] — inclusive onboarding path |
| **12. Public datasets** | Real interval / per-appliance series for training and demo | D1/D2 | Free | Indian: iAWE (Delhi, 73 days, 1 Hz aggregate + appliance); global: UCI household (1-min, 4 yrs, 3 sub-meters), UK-DALE, REFIT, REDD, AMPds, London Low Carbon (5,567 homes, 30-min), Pecan Street (licence). Grid: Grid-India/POSOCO daily state demand for Kerala | [A] built its own KSEB dataset [E] | **Yes** — primary source for models |

## What each tier enables (recap from files 02–03)

- **D0 (bills only):** slab position, bill prediction, inventory-based appliance split [B], inefficient-appliance ranking, coarse year-over-year drift. No anomalies, no patterns.
- **D1 (interval kWh):** pattern analysis, forecasting, anomaly & wastage detection, slab-crossing probability, fridge-only ageing heuristic. This is the *minimum* for the problem statement's core objective.
- **D2 (1 Hz V/I/P/PF):** all of D1 plus voltage abnormality, over-current, event-based appliance identification, per-appliance ageing (with plugs), inverter-battery health proxy.
- **D3:** leakage and earthing indicators.
- **D4:** arc/loose-connection research.

## Realistic prototype data architecture

```
                 ┌──────────────┐
  Bill PDF/CSV ─▶│              │
  Meter photo  ─▶│  Ingestion   │──▶ canonical timeseries store
  Utility CSV  ─▶│  adapters    │    (household_id, ts, kWh|W, V, I, PF, src)
  ESP32/MQTT   ─▶│              │
  Tuya/plug API─▶│              │
  Simulator    ─▶│              │
                 └──────────────┘
```

- One canonical schema; every source is an adapter. The smart-meter API adapter
  exists as an interface with a mock so the architecture is honest about future
  utility integration [I].
- **Simulator adapter** is first-class: it replays public datasets (iAWE/UCI)
  with Indian appliance schedules and can inject anomalies, phantom loads,
  ageing drift, voltage sags and outages — the only way to demo T2/T3 features
  in a hackathon [X].

## Indian-context practicalities [I]

- Most Kerala domestic connections are single-phase, 230 V, sanctioned load
  commonly 1–5 kW (3-phase above). A single CT + voltage tap covers the whole
  house.
- Distribution boards are usually accessible but live-wire work should be done
  by an electrician; the CT clamp is non-invasive, the voltage tap is not.
- Frequent short outages and wide voltage swings are normal; the pipeline must
  treat gaps as *outage*, not zero consumption, and must not flag every
  voltage excursion.
- Inverter/UPS units are ubiquitous; their charging appears as a post-outage
  load bump — a confounder for anomaly detection and a feature for battery
  health [X].
- Privacy: 1 Hz whole-house data reveals occupancy. Store raw D2 locally or
  aggregate to 1-min before cloud upload; publish only derived features.

## Recommended hackathon data plan

1. **Primary:** iAWE + UCI household datasets, re-timestamped and tariff-mapped to KSEB, driving all ML.
2. **Secondary:** one ESP32 + PZEM-004T whole-house node on a team member's home (or a lab bench with a kettle/fan/heater) for a live-data demo; 2–3 Tuya plugs for per-appliance view (mirrors [C]).
3. **Tertiary:** bill upload/photo path to show inclusive onboarding.
4. **Simulator** for anomalies, ageing, and voltage/outage events.

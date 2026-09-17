# Dataset roles and storage

Raw CSVs live in `data/raw/` and are immutable inputs. Audit/adapters write to
`data/derived/`. See `reports/data_audit.md` for hashes, checks and transformations.

- `synthetic_smart_meter_15min.csv`: explicitly synthetic; selected-meter dashboard.
- `ai_energy_intelligence_dataset.csv`: explicitly synthetic; evaluation and separate safety replay.
- `Intelligent_abnormal_electricity_usage.csv`: undocumented community provenance; offline daily benchmark only, never a dashboard or merged interval source.

The current scope is [the combined workflow](../docs/research/11_final-workflow-combined.md).
The schema below documents source columns, not promises of product features or diagnosis.

# Household Energy Intelligence Dataset (`ai_energy_intelligence_dataset.csv`)

## Overview

- **File**: `data/raw/ai_energy_intelligence_dataset.csv`
- **Rows**: 5,760 records (60 days at 15-minute intervals: `2026-03-01 00:00:00` to `2026-04-29 23:45:00`)
- **Granularity**: 15 minutes (96 intervals per day)
- **Role in Project**: Appliance/anomaly evaluation and independent labelled safety replay only. Labels never enter a feature matrix. Ageing labels are ignored.
- **Evidence Tag**: **[X]** synthetic fixture created for testing baseline models, anomaly detection, slab tariff warnings, and electrical safety monitoring under Kerala household conditions.

## Schema & Field Descriptions

| Column | Unit / Type | Description |
|---|---|---|
| `timestamp` | ISO datetime string | 15-minute timestamp (`YYYY-MM-DD HH:MM:SS`) |
| `temperature_c` | °C (float) | Ambient temperature context |
| `occupancy_flag` | 0 / 1 (int) | Household occupancy indicator |
| `is_weekend` | 0 / 1 (int) | Weekend indicator |
| `is_grid_stress_window` | 0 / 1 (int) | Grid peak stress window indicator (evening peak hours) |
| `voltage_v` | Volts (float) | Root-mean-square mains voltage |
| `current_a` | Amperes (float) | Total household current |
| `active_power_kw` | kW (float) | Total household active power |
| `reactive_power_kvar` | kVAR (float) | Total household reactive power |
| `power_factor` | float (0.0–1.0) | Household power factor |
| `kwh_interval` | kWh (float) | Energy consumed in the 15-minute window |
| `monthly_cum_kwh` | kWh (float) | Cumulative energy consumption for the billing month |
| `energy_charge_running_inr` | INR (float) | Running telescopic/slab energy charge under KSEB tariff |
| `fixed_charge_for_month_inr`| INR (int) | Fixed charge tier under KSEB schedule |
| `duty_running_inr` | INR (float) | Electricity duty running total (10% of energy charge) |
| `gt_hvac_kw` | kW (float) | Ground-truth HVAC active power |
| `gt_hvac_aging_factor` | float (1.0+) | HVAC degradation multiplier (compressor wear / efficiency loss) |
| `gt_lighting_kw` | kW (float) | Ground-truth lighting load |
| `gt_fridge_kw` | kW (float) | Ground-truth refrigerator load |
| `gt_water_heater_kw` | kW (float) | Ground-truth geyser/water heater load |
| `gt_plug_loads_kw` | kW (float) | Ground-truth plug and standby loads |
| `anomaly_flag` | 0 / 1 (int) | Flag indicating any operational anomaly |
| `waste_event_flag` | 0 / 1 (int) | Flag indicating true avoidable energy waste |
| `anomaly_type` | string | Classification (`Normal`, `Weekend Guest Spike (context-explained)`, `Phantom Standby Load`, `Unnecessary Night HVAC`) |
| `addon_thd_percent` | % (float) | Total Harmonic Distortion (hardware add-on telemetry) |
| `addon_current_leakage_ma` | mA (float) | Earth leakage current (Tier 2 safety sensor) |
| `addon_neutral_ground_v` | Volts (float) | Neutral-to-ground voltage (earthing / wiring health) |
| `addon_voltage_fault_v_delta`| Volts (float) | Sudden voltage sag indicating potential loose connection |
| `addon_fault_flag` | 0 / 1 (int) | Safety fault event indicator |
| `addon_fault_type` | string / null | Safety fault label (`Elevated Earth Leakage Risk`, `Possible Loose Connection / Voltage Sag`) |

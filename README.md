# Paranova — household energy intelligence

A local, single-household energy dashboard built with React/Vite, Django REST,
SQLite and offline scikit-learn/XGBoost analytics. Opens directly on the synthetic
`SM-KL-001` replay. No login, hardware or cloud deployment.

The authoritative scope is [the combined workflow](docs/research/11_final-workflow-combined.md).
Implementation choices and limits are in [the implementation record](docs/research/12_mvp_implementation.md).
For an AI continuation checkpoint, read [progess.md](progess.md).

## Run locally

Requires Python 3.12, [uv](https://docs.astral.sh/uv/), and Node.js 22.12+.

```bash
uv sync --locked
npm ci --prefix frontend
.venv/bin/python scripts/train.py
.venv/bin/python scripts/dev.py
```

Open **http://127.0.0.1:5173**. The API listens on `127.0.0.1:8000`.
The initial offline preparation audits all three datasets, trains/evaluates models,
writes artifacts, migrates SQLite and seeds all dashboard facts. It is explicit:
application startup and requests never train models. “Re-run saved model” runs
optional live inference from the versioned artifact, with the cached forecast
remaining available. Ctrl+C stops both servers.

Alternatively, run the servers in separate terminals:

```bash
.venv/bin/python manage.py runserver 127.0.0.1:8000 --noreload
npm run dev --prefix frontend
```

The app needs no network after setup. Groq narration is optional: copy
`.env.example` to `.env`, add a server-side key, restart Django, then select
“Try live Groq narration” in Ask. It calls `openai/gpt-oss-120b`, a model
generally available on Groq's catalogue (the `llama-3.3-70b-versatile` model
this was originally built against requires enterprise account access). Missing
access, outages and invalid responses all fall back to deterministic
explanations. No secrets reach Vite or the browser. Live Groq was exercised
with an authorized account.

## Reproduce and verify

```bash
.venv/bin/python scripts/audit_datasets.py
.venv/bin/python scripts/train.py
.venv/bin/python -m pytest -q
.venv/bin/python manage.py check
npm run build --prefix frontend
# With both local servers running and Chromium installed:
npm run test:e2e --prefix frontend
```

Browser tests use `/usr/bin/chromium` by default; set `CHROMIUM_PATH` for another
installation. They cover desktop/mobile navigation, charts, estimator, safety,
chat and the evidence drawer.

## What is included

- Consumption at 15-minute, hourly and daily resolutions; chronological forecast
  bake-off, next-hour backtest and recursive next-24-hour outlook.
- Isolation Forest and contextual z-scores, explicit wastage evidence and scores.
- Coarse appliance step matching, over-draw hints and per-class evaluation.
- Computed voltage/PF/load checks; separately labelled safety-sensor replay.
- Dated KSERC tariff configuration, monthly energy-plus-fixed estimate, editable
  rate/usage what-if panel, slab-edge warning and tested greedy scheduler.
- Facts-only Q&A with cached deterministic answers and optional Groq selection
  of approved factual sentences; visible model/data evidence.

The cost estimate **excludes duty, taxes, fuel surcharge, meter rent and special
concessions**. The single-phase demo has no time-of-day rate difference. Its
current coarse event detector finds no eligible flexible events, so the app
shows an honest empty scheduling state. It does not invent savings.

Safety is **not** computed from the selected meter. It replays four labelled
events from a separate synthetic household. No diagnostic probability is
available; confidence is explicitly uncalibrated. Appliance scores are limited
and visible; none of these results establish field accuracy.

## Repository map

| Path | Purpose |
|---|---|
| `data/raw/` | Three original CSVs, relocated byte-for-byte; never modified by scripts |
| `data/derived/` | Reproducible adapters and selected-meter aggregates (generated) |
| `scripts/audit_datasets.py` | Range, schema, cadence, formula and label audit |
| `scripts/train.py` | Offline modelling, evaluation and atomic SQLite seed |
| `energy/` | Analytics, billing, scheduler, safety replay and narration services |
| `backend/` | Read-only DRF API plus estimator and chat POST endpoints |
| `frontend/` | React dashboard and browser tests |
| `config/` | Tariff, appliance references and explicit rule thresholds |
| `reports/` | Audit and evaluation outputs |
| `artifacts/` | Timestamped model bundles, metadata and cached demo facts (generated) |
| `energy.sqlite3` | Local snapshot database (generated) |

GET `/consumption`, `/forecast`, `/insights`, `/appliances`, `/power-quality`,
`/safety`, `/cost`, `/chat`, `/facts`, `/evidence` (also available under `/api/`).
POST `/cost` accepts only `{usage_kwh, slab_rates}` (five telescopic rates followed
by five whole-month rates); POST `/chat` accepts `{question, live?}`. The estimator
never changes stored facts. No inventory or account configuration endpoint exists.

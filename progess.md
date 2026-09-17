# Progress and AI handoff — Paranova

Last updated: 2026-09-17 (Asia/Kolkata).
Filename intentionally follows the user's request: `progess.md`.

## Start here

The user explicitly requested implementation of the **full local MVP**, then
requested this handoff for another AI. The implementation is built and tested;
**do not restart or scaffold it again**. No implementation command is currently
waiting to finish. Remaining limitations and the Git synchronization issue below
must not be mistaken for verified capabilities.

Read in this order:

1. [AGENTS.md](AGENTS.md) — contribution rules and evidence discipline.
2. [Authoritative workflow](docs/research/11_final-workflow-combined.md) — locked scope.
3. [Implementation record](docs/research/12_mvp_implementation.md) — durable decisions and limitations.
4. [README.md](README.md) — setup, execution and verification commands.
5. This file — handoff checkpoint and workspace state.

**[X]** Product/model capabilities are prototypes. **[I]** Engineering assumptions
and limitations are documented in file 12. Do not claim field-validated results
or treat simulated labels as actual household fault diagnoses.

## Critical workspace / Git state

- Branch: `main`; remote: `https://github.com/ashin-15/cek-hack.git`.
- **The implementation is uncommitted and has not been pushed.** Many new
  directories are untracked. Preserve them; inspect `git status --short` before
  any checkout, reset, cleaning, stashing or merge.
- The initial implementation started after a successful pull at `98a704a`.
- During this handoff, a fresh fetch found `origin/main` advanced to `89441a6`.
  The attempted fast-forward **aborted** because it would overwrite local
  `docs/research/10_finalized_workflow_decisions.md`. The local branch was not
  merged or rebased. Reconcile local and remote changes before subsequent
  implementation work; do not discard the local MVP to satisfy the pull rule.
- Inspection of `HEAD..origin/main` shows the upstream commit renames
  `docs/research/10_finalized_workflow_decisions.md` to
  `docs/research/10_workflow_decisions.md` (unchanged contents), and deletes the
  tracked root `env` file. Preserve the upstream rename/deletion when reconciling;
  carry over the local superseded notice and update links accordingly.
- Local Git config enables pull-with-rebase, which rejects this dirty worktree.
  `git -c pull.rebase=false pull --ff-only` fetched successfully but encountered
  the overwrite protection above. Do not repeatedly retry without resolving it.
- `git status` also shows deletion of the tracked root file `env`. This deletion
  was noticed during implementation but was **not intentionally performed by
  this agent**. The newly fetched upstream commit also deletes this file. It was
  left untouched; do not restore, publish or print possible secrets automatically. `.env.example` is the new safe configuration template.
- The three old `data/*.csv` paths appear deleted because they were moved into
  `data/raw/`. The new files were verified byte-for-byte against the originals
  in `HEAD` using `git show`; this is relocation, not loss or data editing.

## Completed implementation

| Area | Completed work / primary files |
|---|---|
| Authoritative docs | Corrected `AGENTS.md` and research-index pointers; marked file 10 superseded; added file 12 and updated README/data documentation |
| Environment | Python 3.12, `pyproject.toml`, `uv.lock`, `.venv`; frontend package/lock files. NumPy constrained below 2.4 for pandas compatibility |
| Audit / adapters | `scripts/audit_datasets.py`: schema, numeric ranges, timezone/cadence/duplicates, electrical/cumulative formulas, label-range review; writes reports and derived copies without mutating raw input |
| Aggregates / features | `energy/pipeline.py`: selected SM-KL-001 intervals, hourly/daily aggregates, explicit feature allowlist, causal lags/rolling statistics and shifted electrical features |
| Forecasts | Seasonal-naive/RF/XGBoost bake-off, chronological holdout, simplest-within-5%-MAE rule, saved model, next-hour backtest and recursive next-24h forecast |
| Anomaly / wastage | Training-only Isolation Forest and same-hour/day-type baselines; explicit auditable score and evidence; independent labelled evaluation and offline daily benchmark |
| Appliances | `energy/events.py` plus `config/appliances.json`: sustained aggregate steps, likely classes/alternatives, >20% over-draw hint, per-class evaluation |
| Power quality | Interval voltage, persistent low PF, connected-load/current-envelope checks; no inferred electrical fault diagnosis |
| Safety | Four labelled event groups from the separate synthetic safety fixture; renamed sag hypothesis, sensor evidence, alternatives, Simulated badge and electrician disclaimer |
| Billing | `energy/billing.py`, dated KSERC tariff JSON: telescopic and whole-month rates, fixed charges, projection, band-edge warning, isolated rate/usage what-if estimator |
| Scheduling | Tested greedy contiguous-window search with conditional ToD eligibility, fractional-hour duration and forecast-demand tie-break; advisory only |
| Narration / chat | `energy/advisor.py`: cached deterministic explanations, optional Groq Llama, JSON/schema/numeric grounding checks, fail-safe templates |
| API / SQLite | `backend/`, migrations, `energy/provider.py`: precomputed snapshots; offline atomic seeding; no authentication, inventory or account configuration |
| Optional live inference | `energy/inference.py`; GET `/forecast?live=true` loads the saved artifact and predicts without fitting; dashboard “Re-run saved model” button |
| React UI | `frontend/src/main.jsx`, `styles.css`: Consumption, Appliances, Power quality, Safety, Cost & savings, Ask, and an evidence drawer; responsive desktop/mobile layout |
| Tests / launch | `tests/`, `frontend/tests/`, `scripts/dev.py`; explicit offline preparation, then local API/frontend servers |

## Dataset state and roles

**[I]** All raw content is unchanged. Generated files can be reproduced.

- `data/raw/synthetic_smart_meter_15min.csv`: 32,256 rows, 12 explicitly synthetic
  meters, 28 days. Only `SM-KL-001` drives the main household dashboard.
- `data/raw/ai_energy_intelligence_dataset.csv`: 5,760 rows, one separate
  explicitly synthetic household. Appliance/anomaly evaluation and safety
  replay only. Labels do not enter feature matrices; ageing is ignored.
- `data/raw/Intelligent_abnormal_electricity_usage.csv`: 10,800 daily records,
  360 households; provenance undocumented. Offline daily benchmark only.
  All 900 missing actual-energy rows are positive-labelled. Retain these rows,
  report unscorable coverage, and never use missingness/expected energy/source
  deviation/labels as predictive shortcuts.

Audit outputs: `reports/data_audit.md` and `reports/data_audit.json`.
Generated `data/derived/`, `artifacts/`, and `energy.sqlite3` are ignored by Git.
They exist in this workspace but must be regenerated in a fresh checkout.

## Last completed model run

Artifact pointer: `artifacts/latest.json`.
Checkpoint run ID: `forecast-v1-20260917T090808225021Z`.
Use the pointer rather than hardcoding this ID if training is rerun.

**[X]** Forecast evaluation on 168 held-out hourly rows:

| Model | MAE (kWh) | RMSE (kWh) | MAPE |
|---|---:|---:|---:|
| Seasonal-naive | 0.03205 | 0.06080 | 14.143% |
| **Random Forest — selected** | **0.02980** | **0.04684** | **13.177%** |
| XGBoost | 0.02937 | 0.04653 | 13.297% |

- Seven-day feature warmup; primary training August 8–21, test August 22–28.
- Random Forest is the simpler candidate within the predefined 5% margin of
  XGBoost. This holdout selects the winner; it is not an additional untouched
  generalization test. Future-only forecasts use the winner refit on history.
- One-hour metrics do not validate the recursive 24-hour forecast.
- Independent labelled-fixture anomaly precision/recall/F1:
  **0.3478 / 0.8000 / 0.4848**, 20 positive hours in 336 test hours.
- Rule-based wastage precision/recall/F1: **1.0 / 1.0 / 1.0**, only 10 labelled
  positive hours in that same synthetic holdout. This narrow fixture result
  is not field accuracy and does not justify training a label-mimicking model.
- Appliance detector finds 92 candidates and two possible over-draw hints in
  the selected primary history. Separate evaluation has limited performance,
  including zero water-heater precision/recall. Keep the results visible.
- Current monthly energy-plus-fixed projection: **₹1,017.88**.

Detailed results: `reports/model_evaluation.json`, `reports/daily_benchmark.json`,
and the versioned artifact metadata. Regenerated reports supersede these numbers.

## Known limitations / unfinished external verification

1. **Live Groq has not been tested with an authorized account.** The integration
   uses `llama-3.3-70b-versatile`, listed as enterprise access in official docs
   checked during implementation. Optional server-side `GROQ_API_KEY` goes in
   `.env`; no key is required for the working deterministic demo.
2. **Llama native strict JSON-schema output is not supported in the checked
   Groq docs.** Integration uses JSON object mode and local schema validation
   over exact approved sentences, plus numeric checks. Do not describe this as
   vendor-enforced strict structured output or unrestricted free-form narration.
3. **Safety confidence is uncalibrated.** Cards intentionally use `null` /
   “Not calibrated” instead of inventing a probability. This is an explicitly
   documented limitation of the workflow's request for a confidence value.
4. **There are no eligible flexible events in the selected primary replay.**
   The scheduler is implemented/tested, but the UI honestly shows an empty state.
   The single-phase demo also has no established ToD enrollment, so shifting
   alone cannot claim savings. Do not fabricate candidates or change datasets
   merely to make the screen look populated.
5. **Billing is a subtotal estimate**, excluding duty, taxes, fuel surcharges,
   meter rent, subsidies and concessions. Tariff JSON uses the official KSERC
   schedule effective April 2025–March 2027, checked on implementation day.
6. **Appliance inference is coarse.** Fifteen-minute data cannot reliably resolve
   short kettle/mixer events or overlapping loads. Only separately labelled
   classes can be evaluated. Efficiency hints are not certified measurements.
7. **Low anomaly precision is real in this evaluation.** The primary meter has
   no truth labels. Its alert is a computed candidate; the “true waste” example
   appears separately in Ask from the labelled evaluation household.
8. **No prior bill is supplied.** Chat must not invent an explanation of an
   established bill increase. The fallback explicitly explains this limitation.
9. Vite production build passes but reports a bundle-size warning (~738 kB JS
   before gzip). Code splitting is a possible follow-up, not a functional blocker.
10. **Git synchronization remains unresolved**, as described above. No commit,
    push, deployment or merge was performed by this agent.

## Verification already completed

Last implementation verification (before this documentation-only handoff):

- `python scripts/train.py`: completed audit, bake-off/evaluation, unique
  artifact generation, migrations and SQLite seeding.
- `.venv/bin/python -m pytest -q`: **39 passed**, no warning summary after the
  NumPy compatibility correction.
- `.venv/bin/python manage.py check`: no issues.
- `npm run build --prefix frontend`: passed; bundle-size advisory only.
- `npm run test:e2e --prefix frontend`: **2 passed**, real Chromium with the
  local backend. Covers desktop journey, mobile layout, live saved-model
  inference, estimator, safety, chat fallback and evidence drawer.
- Ruff import/undefined-name checks and `git diff --check`: passed.
- All three relocated raw CSVs matched their original tracked bytes exactly.
- Desktop and mobile screenshots were visually inspected. Temporary files:
  `/tmp/paranova-desktop.png`, `/tmp/paranova-mobile.png` (may not persist).

No need to repeat training/tests solely to read this handoff. Rerun appropriate
checks after changing behavior, dependencies, data adapters or model code.

## Run / resume commands

From the project root:

```bash
# Fresh checkout / missing dependencies:
uv sync --locked
npm ci --prefix frontend

# Explicit offline preparation when generated files are absent or stale:
.venv/bin/python scripts/train.py

# Start both local servers, without training:
.venv/bin/python scripts/dev.py
```

UI: `http://127.0.0.1:5173`; API: `http://127.0.0.1:8000`.
Servers were left running after implementation, but **check current reachability
and port occupancy before starting duplicates**. Agent tool sessions are not a
persistent process-management contract. Django was started with `--noreload`;
restart it after backend changes.

```bash
.venv/bin/python -m pytest -q
.venv/bin/python manage.py check
.venv/bin/ruff check energy backend scripts tests manage.py --select F,I
npm run build --prefix frontend
# Requires both servers and Chromium:
npm run test:e2e --prefix frontend
```

Browser config defaults to `/usr/bin/chromium`; override `CHROMIUM_PATH` if
needed. In this restricted workspace, network installs, Git writes, binding
Django and launching Chromium needed tool permission escalation. A writable
uv cache was supplied as `UV_CACHE_DIR=/tmp/paranova-uv`; npm used
`--cache /tmp/paranova-npm`. Respect sandbox approvals instead of bypassing them.

## API contract reminder

GET (also available under `/api/`): `/consumption`, `/forecast`, `/insights`,
`/appliances`, `/power-quality`, `/safety`, `/cost`, `/chat`, `/facts`, `/evidence`.

- `/forecast?live=true`: optional saved-model inference; never training.
- POST `/cost`: `{ "usage_kwh": number, "slab_rates": [10 rates] }`.
  Five telescopic rates, then five whole-month rates; no persisted mutation.
- POST `/chat`: `{ "question": "...", "live": false }`; maximum 500 characters.
- No endpoint accepts an appliance inventory, account config or device control.

## How the next AI should proceed

1. Inspect the existing implementation, local modifications and remote changes;
   reconcile the blocked pull while preserving user work.
2. Continue the user's next requested change. The original build is already
   implemented; the items above are limitations, not permission to expand scope.
3. If live Groq is requested, use authorized server-side credentials, verify
   account model access and keep fallback behavior intact.
4. Keep durable decisions in `docs/` and update this file when a new checkpoint
   is reached. Maintain honest metric/provenance wording and raw-data integrity.
5. Do not introduce auth, cloud services, hardware, ageing, a population UI,
   MILP/RL, appliance control or inferred electrical diagnoses.

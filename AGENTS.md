# Project Context for Agents

The `docs/` directory is the project's primary source of truth for its problem
statement, research, decisions, and domain context. Read the relevant documents
before planning or making changes so your work stays aligned with the project.

## Contribution rules

1. Before starting new work or adding changes, pull the latest changes from the
   shared branch. Do not forget this step; project context and decisions may
   have been updated in `docs/`.
2. When new ideas, decisions, assumptions, research, or other durable project
   context emerge, add or update the appropriate file in `docs/` as part of the
   same change.
3. Keep documentation accurate and current. Treat undocumented, transient chat
   context as non-authoritative until it has been recorded in `docs/`.

## Where things live

- `docs/ai_energy_consumption_problem_statement.md` — the hackathon problem statement.
- `docs/*.md` (paper titles) — the three source research papers, referenced as
  [A] Kerala demand forecasting, [B] IJST Smart Energy Optimizer, [C] Energies HEMS.
- `docs/research/README.md` — complete research index. The finalized product,
  architecture, data and demo decisions are in
  `docs/research/11_final-workflow-combined.md`, which overrides earlier scope
  and implementation recommendations. File 07 provides historical scope and
  novelty context; file 01 says what the papers do and do not prove.

## Evidence discipline

Tag claims in docs as **[E]** (demonstrated in a paper, cite section), **[I]**
(engineering inference), or **[X]** (our proposed, unproven extension). Never
present [I]/[X] items as established. In particular: standard smart-meter kWh data
cannot diagnose loose connections, earthing or leakage faults (see
`docs/research/03_electrical_fault_detectability.md`).

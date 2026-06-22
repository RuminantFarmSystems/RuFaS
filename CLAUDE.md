# CLAUDE.md

Guidance for Claude Code (claude.ai/code) working in this repository.

## Project

**RuFaS** (Ruminant Farm Systems) — whole-dairy-farm biophysical simulation
model in Python. Simulates a dairy farm day-by-day across animal, field/soil/crop,
manure, and feed-storage subsystems, plus an Economics/Energy/Emissions (EEE)
layer, then aggregates outputs and generates reports/graphics.

This checkout is the **MyForageSystem (MSF)** fork. Working branch: `dev-msf`
(upstream integration branch is `dev`).

## Layered CLAUDE.md (load-on-demand)

Subsystem conventions live next to their code and load only when Claude reads
files there — keep this root file repository-wide, push specifics down:

- `RUFAS/CLAUDE.md` — top-level managers (input/output/task/report) + engine
- `RUFAS/biophysical/CLAUDE.md` — biophysical domain overview
- `RUFAS/biophysical/animal/CLAUDE.md` — animal subsystem
- `RUFAS/biophysical/field/CLAUDE.md` — field / soil / crop subsystem
- `RUFAS/EEE/CLAUDE.md` — Economics, Energy, Emissions
- `RUFAS/data_structures/CLAUDE.md` — inter-subsystem connection objects
- `tests/CLAUDE.md` — pytest conventions

Cross-cutting path-scoped rules live in `.claude/rules/` and load when a
matching file enters context (e.g. `protected-inputs.md`).

## Tooling

- **Python**: `>= 3.12, < 3.14` (CI pins 3.12).
- **Install (editable + dev tools)**: `pip install -e ".[dev]"`.
- **Formatter**: Black — `target-version py312`, **line-length 120**. CI
  auto-formats changed `.py` files and commits the result; match it locally.
- **Linter**: Flake8 — `max-line-length 120`, `max-complexity 10`,
  `ignore = E203, W503` (see `.flake8`).
- **Types**: mypy **strict** (`disallow_untyped_defs`, `strict = True`,
  `disallow_any_generics`, …). Every function needs full type annotations.
- **Tests**: pytest `>=9.0.3` + `pytest-mock`, `pytest-lazy-fixtures`
  (`from pytest_lazy_fixtures import lf`), `freezegun`.
- **Coverage**: `coverage` via `.github/.coveragerc`.
- **Docs**: Sphinx (`pip install -e ".[build_docs]"`, build under `docs/`).

## Common commands

| Task                    | Command                                                        |
| ----------------------- | -------------------------------------------------------------- |
| Run the model (example) | `python main.py -p input/task_manager_metadata.json`           |
| Run, no graphics        | `python main.py -g`                                            |
| All tests               | `pytest`                                                       |
| One test file           | `pytest tests/test_simulation_engine.py`                       |
| One test                | `pytest tests/test_units.py::test_name`                        |
| Coverage report         | `coverage run --rcfile=.github/.coveragerc && coverage report`|
| Format                  | `black .`                                                      |
| Lint                    | `flake8 .`                                                     |
| Type check              | `python -m mypy .`                                             |

`main.py` flags: `-p` metadata path, `-o` output dir, `-l` logs dir,
`-v {errors,warnings,logs,credits,none}`, `-c` clear output (caution),
`-g` no graphics, `-s` suppress log files. See `main.py:parse_gnu_args`.

## Architecture

Entry point `main.py` → `TaskManager.start(...)`. A run is driven by a
metadata JSON (`input/task_manager_metadata.json`) that lists tasks; each task
points at config/data JSON under `input/data/`.

Top-level flow (`RUFAS/`):

- **`task_manager.py`** — orchestrates one or more simulation tasks.
- **`input_manager.py`** — parses & resolves the input JSON tree (deep, with a
  configurable depth limit) into in-memory structures.
- **`simulation_engine.py`** — the day-by-day loop driving subsystems.
- **`output_manager.py`** — log/data pools, verbosity (`LogVerbosity`), dumps.
- **`report_generator.py` / `graph_generator.py`** — reports & graphics.
- **`data_validator.py`** — large validation layer over inputs.
- Support: `rufas_time.py`, `units.py`, `weather.py`, `general_constants.py`,
  `user_constants.py`, `current_day_conditions.py`, `util.py`.

Domain packages:

- **`RUFAS/biophysical/`** — `animal/`, `field/`, `manure/`, `feed_storage/`.
- **`RUFAS/EEE/`** — emissions, energy, tractor / implements (economics layer).
- **`RUFAS/data_structures/`** — typed connection objects that move material
  (manure, feed, nutrients) between subsystems.

Non-Python: **`DataCollectionApp/`** is a separate static JS/HTML web app
(input authoring) — not part of the Python model; ignore it for model work.

## Conventions

These mirror the RuFaS wiki — see
[Code review](https://github.com/RuminantFarmSystems/RuFaS/wiki/Code-review),
[How to write a design doc](https://github.com/RuminantFarmSystems/RuFaS/wiki/How-to-write-a-design-doc%3F),
[Branching Strategy](https://github.com/RuminantFarmSystems/RuFaS/wiki/Branching-Strategy-in-RuFaS).

- **Full type hints everywhere** — mypy strict will reject untyped defs.
- **NumPy-style docstrings** on every modified/added function (+ a unit test).
- **Line length 120**, Black-formatted. Don't hand-format against Black.
- **Keep cyclomatic complexity ≤ 10** (flake8 `max-complexity`). Refactor
  rather than suppress. Apply DRY / SOLID; keep functions small.
- **Comments are discouraged** — clean code should explain *what* it does; only a
  comment explaining *why* an approach was chosen is acceptable.
- **Tests mirror `RUFAS/`** under `tests/` (`test_<module>.py`, `test_<pkg>/`),
  and must cover **normal operation, edge cases, and invalid inputs**. See
  `tests/CLAUDE.md` (unit + E2E). For the E2E workflow use the
  `rufas-e2e-testing` skill.
- **Design-doc-driven for large work** — a change ≈ 1 engineer-month or more needs
  a design doc agreed before coding. Use the `rufas-design-doc` skill.

## Branching & PRs

Upstream flow: feature branch → `dev` → `test` → `main`. **This fork integrates on
`dev-msf`** (its `dev`); CI runs there. PR rules (from the Code-review wiki):

- Keep PRs **≤ ~200 lines** where possible (larger = "large", needs design review).
- PR description follows **what / why / how** (concise) + a **Test Plan**; link the
  GitHub issue; no temp/unused files; rebase before review.
- **Two reviews** required (ideally one SME + one software engineer) + all CI green
  before merge; the author merges and deletes the branch.

## Gotchas

- **`changelog.md` is mandatory on every PR** — CI fails the PR if it is not
  updated. Add an entry describing the change.
- **Protected input files** — a set of `input/.../example_*.json` (and
  `no_*.json`) fixtures are CI-protected; changing them fails the build. Full
  list + rule in `.claude/rules/protected-inputs.md`. Don't edit them.
- **mypy ratchet** — CI compares the error count against `dev` and **fails if
  your branch adds errors**. Don't introduce new mypy errors; reduce where you can.
- **CI target branch is `dev`** (push/PR). This fork works on `dev-msf`.
- **Coverage omits `__init__.py`** and defensive branches (see `.coveragerc`).
- **Large modules**: `output_manager.py` (~127 KB), `data_validator.py` (~99 KB),
  `input_manager.py` (~80 KB). Prefer targeted reads / a Python LSP over full reads.

## Code intelligence

The `pyright-lsp@claude-plugins-official` plugin is enabled for this repo
(`.claude/settings.json` → `enabledPlugins`). Use the **LSP tool** for symbol
lookups (`documentSymbol`, `workspaceSymbol`, `goToDefinition`,
`findReferences`, call hierarchy) instead of scanning the large modules.

Requires the `pyright`/`pyright-langserver` binary on your machine
(`npm i -g pyright` or via your package manager).

> **mypy remains the CI source of truth** for types (strict mode, error ratchet
> vs `dev`). Pyright diagnostics surfaced in-editor are for navigation/quick
> feedback and may differ from mypy — don't treat a pyright warning as a CI
> gate, and don't "fix" code solely to satisfy pyright if mypy is happy.

## graphify (dependency graph)

This repo has a graphify knowledge graph of the model code (`RUFAS/` + `main.py`)
at `graphify-out/`. Only `GRAPH_REPORT.md` is committed; `graph.json`/`graph.html`
are gitignored and rebuilt on demand. Scope is set by `.graphifyignore`.

Rules:

- **Before answering architecture / "how does X relate to Y" questions**, read
  `graphify-out/GRAPH_REPORT.md` for god nodes (e.g. `OutputManager`,
  `GeneralConstants`, `RufasTime`, `InputManager`) and community structure.
- For cross-module questions prefer the graph over grep:
  `graphify query "<question>"`, `graphify path "<A>" "<B>"`,
  `graphify explain "<symbol>"` (traverses EXTRACTED + INFERRED edges).
- **After modifying code in `RUFAS/`**, refresh the AST graph (free, no API):
  `GRAPHIFY_NO_TIPS=1 graphify update .` (append `|| true` in scripts — graphify
  prints a buggy "tips" line that exits non-zero *after* writing the graph).
- CI auto-updates `GRAPH_REPORT.md` on push (`.github/workflows/update-graphify.yml`).
  Requires `uv tool install graphifyy` locally to run graphify yourself.
- Optional semantic pass (richer edges, **uses API tokens**): `/graphify` in a
  Claude Code session. Fine for this public repo; skip if you want zero cost.

## Dev workflow (skills + slash commands)

Agent dev-workflow skills are vendored under `.claude/skills/` (self-sufficient).
Use them directly: `superpowers:test-driven-development`,
`systematic-debugging`, `writing-plans`, `requesting-code-review`,
`verification-before-completion`, `using-git-worktrees`, etc.

Two planning tracks, both ending in a per-task TDD implementation via `/apply-plan`:

- **Lightweight (PLAN file)**: `/diagnose` → `PLAN_<slug>.md` → `/challenge-plan`
  (counter-validates via a fresh-context subagent; auto-cycles `/refine-plan` +
  re-challenge) → `/apply-plan`.
- **Spec-driven (OpenSpec)**: `/opsx:propose` → `/challenge-plan openspec:<name>`
  → `/apply-plan openspec:<name>` → `/opsx:archive` after merge. OpenSpec is
  scaffolded under `openspec/` (CLI `@fission-ai/openspec`; `openspec list`,
  `openspec validate`).

`/apply-plan` runs each task RED→GREEN→REFACTOR with a spec + quality double
review, enforces the RuFaS gates (mypy strict, flake8 ≤ 10, pytest, Black 120,
changelog, protected inputs), and opens a PR into `dev-msf` via `gh`. The
`code-reviewer` agent (`.claude/agents/`) gives a Python/scientific-integrity
review on demand. `/graphify` queries the dependency graph; `/sync-claude-md`
audits the layered `CLAUDE.md` files against the code.

## Beef Module Reference Documents

All NRC 2016 beef module reference data lives in `docs/beef_module/`:
- `NRC2016_Beef_Requirements_Calculator_Inventory_Final.xlsx` — NRC 2016 equations,
  coefficients, breed multipliers, Box 12-1 benchmark (MP = 691 g/d)
- `NRC2016_BeefCattle_FeedLibrary_Complete.xlsx` — Feed compositions
  (Table 18-1), Feed IDs 301–305
- `RuFaS_Feedlot_Implementation_Plan.docx` — 8-step implementation plan

Cow-calf system reference data lives in `docs/beef_module/cow_calf/`:

- `RuFaS_CowCalf_Integration_Plan.md` — 11-step implementation plan with NRC 2016 equation
  references (Chapters 6/11/12/13/19), lessons from PR #32 feedlot module, and named scope
  boundaries
- `README.md` — scope boundaries, known simplifications, and future-PR candidates

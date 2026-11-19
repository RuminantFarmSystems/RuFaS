---
paths:
  - "input/data/**"
  - "input/metadata/**"
---

# Protected input JSON files — do not edit

Scope: **only** `example_*.json` / `no_*.json` under `input/data/**` and
`input/metadata/**`. This rule says **nothing** about `tests/` — test files are
yours to create and edit freely (see `tests/CLAUDE.md`).

The CI workflow `.github/workflows/combined_format_lint_test_mypy.yml`
(step **Check for Unauthorized Changes**) **fails the build** if any of a fixed
set of example input files is modified. These are reference scenarios
(`example_*`, `no_*`) that downstream tests and users depend on.

## Rule

- **Never edit** the protected `example_*.json` / `no_*.json` input files under
  `input/data/**` and `input/metadata/**`.
- To test a new scenario, create a **new** JSON file with a different name and
  point your task metadata at it — do not repurpose a protected example.
- If a protected file genuinely must change, surface it to the user first; it
  needs maintainer sign-off and will otherwise block the PR.

## Protected paths (from CI)

Metadata: `example_freestall_dairy_metadata.json`, `example_open_lot_metadata.json`,
`example_no_animal_metadata.json`.

Tasks: `example_freestall_task.json`, `example_open_lot_task.json`,
`example_no_animal_task.json`.

Data (`input/data/**`): the `example_*` / `no_*` files under `animal/`,
`config/`, `crop/`, `EEE/` (`default_costs.json`, `default_emissions.json`),
`feed/`, `feed_management/`, `fertilizer_schedule/`, `field/`,
`manure_schedule/`, `manure/`, `soil/`, `tillage_schedule/`.

See the CI `paths_to_protect` array for the authoritative, exact list.

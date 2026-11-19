# Upstream sync notes — November 2026

Quick guide for developers working on this fork after the sync of `dev-msf` with
RuminantFarmSystems/RuFaS `dev` (`9af6eca23`, 2026-11-05). Previous sync: June 2026 (PR #29).
The fork is now **0 commits behind upstream**; 2515 upstream commits came in.

Everything below is "what changed that you will bump into". Details of each upstream change
are in `changelog_WIP.md` (search the PR number).

---

## 1. Conventions that changed — read this first

| Before | Now | Why |
|---|---|---|
| Add your PR entry to `changelog.md` | Add it to **`changelog_WIP.md`** under `### Next Version Updates` | CI now fails a PR that does not touch `changelog_WIP.md`. `changelog.md` only holds released versions. |
| Properties files in `input/metadata/properties/` | **`RUFAS/input/metadata/properties/`** (`default.json`, `tasks_properties.json`, `commodity_properties.json`) | Upstream packages them with the library (#3142). Paths are hardcoded in `RUFAS/input_manager.py`. |
| `GeneralConstants.MJ_CH4_TO_G_CH4` / `KCAL_TO_MJ` | `G_CH4_TO_MJ_CH4` / `MCAL_TO_MJ` (same values) | Pure renames. |
| `random_seed` in config input files | Removed (#3070) | Seed comes from the task. |
| `Weather.mean_annual_temperature` | `Weather.long_term_average_annual_temperature` | Rename. |

Fork docs that still mention the old conventions (`CLAUDE.md`, `AGENTS.md`,
`.claude/commands/*`, `docs/_src/_wiki/Input-Manager.rst`, `onboarding.rst`) are a pending
follow-up.

## 2. Animal module — new upstream behaviour you must know

- **Removal model rewritten (#3241).** Per-lactation culling is gone. Cows now roll daily
  against annual, parity-indexed death and acute-sale probabilities
  (`Animal.assess_and_schedule_removal`, `RemovalRiskParityGroup`). Input block
  `from_literature.culling` is now `annual_death_prob`, `parity_death_dist`,
  `annual_sale_prob`, `parity_sale_dist`. `determine_future_death_date` no longer exists.
- **Youngstock mortality (#3003).** New required inputs
  `management_decisions.calf_mortality_rate` and `heifer_mortality_rate`;
  `Animal._setup_calf_mortality()` / `_setup_heifer_mortality()` schedule deaths at birth.
- **Calf retention policy (#3078).** `HerdManager.calf_retention_policy`
  (`CalfRetentionPolicy`) decides at birth whether a dairy calf is sold or kept
  (`calf_retention_method`: `rate` or `count`). It sells male calves at birth.
  **Fork rule: `BEEF_CALF` newborns bypass it** (guard in `HerdManager`); do not remove that
  guard or the cow-calf weaning numbers collapse.
- **Genetics submodule (#2734, #2966, #3257).** New required input blocks: `genetics`
  (TBV / environment variances and correlations), `farm_level.repro.selective_repro_strategy`,
  `ranking_method`, `genetic_selection_index_weights`, and `semen_allocation_proportions`
  under `repro.heifers` and `repro.cows`. Newborn dicts (`NewBornCalfValuesTypedDict`) now
  require `sex: Sex` and `bred_from_semen: SemenType | None`.
- **`Animal.daily_routines(time, population_ranking_indexes)`** — second argument is new
  (pass `None` in unit tests).
- **Ration DMI control (#3248).** `RationManager.set_intake_options`, `IntakeOption`
  (`predict_DMI`, `set_DMI`, `set_DMI_per_X`), `resolve_target_dmi(animal_combination, pen)`.
  `get_user_defined_ration` now takes a target DMI (float), not `NutritionRequirements`.
  The fork's beef rations (`feedlot_*`, `beef_*`, `beef_stocker_*`) coexist with it;
  turning the stocker limit-feed cap into an `IntakeOption` member is still open.
- **`HerdManager` new attributes**: `daily_herd_reproduction_statistics`,
  `calf_retention_policy`, `herd_statistics.heiferIII_to_cow_transitions`, heifer ADG by pen
  (#3047), high-priority herd outputs (#3329). Tests that build `HerdManager` or `Animal`
  with `__new__` must set every new attribute themselves.
- New `Breed.BOD` (`Beef_On_Dairy`) next to the fork's beef breeds.
- `SimulationEngine.simulate()` is now split into `_post_simulation_processing`,
  `_post_simulation_reporting`, `_post_simulation_logging`. The fork's
  `report_undelivered_crops` (field curing) runs in `_post_simulation_reporting`.

## 3. Crop, soil, feed, manure — upstream additions

- `harvest_efficiency` is now a crop-configuration input on `CropData` (#3163), with a new
  `pasture` crop configuration. `CropManagement.manage_harvest` returns `HarvestedCrop | None`.
  The fork's `weather` parameter (field curing, `wilt_days`) is still required.
- Manure carbon flows into the soil carbon pools (#3229); `daily_spread` block in manure
  schedules (#2623, #3168); `tractor_size` field input (#3132).
- Feed input structure reorganized (#2971); initial storage inventory
  (`FeedManager.stock_initial_storage_inventory`).
- New simulation types: `animals_only` (#3002), `feed_only` (#3183), `manure_only` (#3217).
- Mineralization residue factor re-implemented (#3150), urine N minimums (#2994), farm-grown
  feed emissions unit fix (#2907/#3288).

## 4. Tooling and testing

- `pyproject.toml`: version `1.0.5`, `deepdiff>=9.1.0`, `black>=26.5.1`, console script
  `rufas = RUFAS.main:main`. The fork's pytest markers (`unit`, `component`, `integration`,
  `regression`, `validation`, `nrc2016`, `smoke`, `slow`) are kept.
- E2E testing gained must-change (#3182), accepted-range (#3290), multi-seed averaging (#3295)
  and an `animals_only` scenario (#3136). Run: `python main.py -p
  input/metadata/end_to_end_testing_tm_metadata.json`. Known: the Animal domain reports the
  fork's four `AnimalType.BEEF_*_deaths` output variables as "added" (zero on dairy herds);
  all other values match upstream.
- `OutputManager` adds `simulation_day` to info maps automatically (#2931) — do not add it
  yourself.
- Cross-validation: many new Animal rules (#2935) and `is_not_null` / `is_in` operators;
  nulled input blobs no longer silently load defaults (#3098).
- mypy: ~1160 pre-existing errors upstream. Judge a change by diffing error sets against the
  base branch, not by the total.

## 5. What the fork still owns (unchanged by the sync)

- Beef module: feedlot, cow-calf, stocker/backgrounding, BeefGEM scenarios, NRC 2016
  calculators (`RUFAS/biophysical/animal/*beef*`, `docs/beef_module/`).
- Silage pre-harvest field curing (`wilt_days`, `swath_density`, crops in transit in
  `FeedManager`).
- `TaskManager.start()` does not run the Python-version / dependency checks and reads the
  version with `importlib.metadata` (library use by `rufas-api` / `msf-rufas`).
- CI runs on `dev-msf`; Dependabot targets `dev-msf`.

## 6. Open follow-ups

1. `changelog_WIP.md` entry for the sync PR.
2. Refresh fork docs listed in section 1.
3. E2E: refresh expected results for the `BEEF_*_deaths` variables (or exclude them from the
   Animal filter) and consider a beef E2E input set.
4. Decide whether the stocker limit-feed cap becomes an `IntakeOption` member.

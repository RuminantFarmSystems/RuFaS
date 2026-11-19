# RUFAS/biophysical/animal/ — animal subsystem

Models the dairy herd plus the beef modules (feedlot, cow-calf,
stocker/backgrounding). Entry/orchestration:

- `herd_manager.py` — owns the herd's daily step and state.
- `herd_factory.py` — builds the herd from parsed inputs.
- `pen.py` — pen-level grouping; `animal.py` — individual animal model.
- `animal_config.py`, `animal_grouping_scenarios.py` — configuration.
- `animal_module_reporter.py` — subsystem reporting hooks.
- Constants: `animal_constants.py`, `animal_module_constants.py`.

## Biological sub-packages

- `digestive_system/` — intake & digestion.
- `nutrients/` — nutrient pools/requirements (incl. beef NRC calculators).
- `ration/` — feed ration formulation/allocation.
- `growth/` — body growth.
- `milk/` — milk production.
- `reproduction/` — breeding/gestation cycle.
- `animal_health/` — health states.
- `animal_genetics/` — genetic parameters.
- `bedding/` — bedding use (feeds into manure).
- `data_types/` — animal-specific typed structures.

## Beef modules — extension rules

When adding or extending a beef animal type (feedlot / cow-calf / stocker
family), follow the sibling module exactly:

- **Register in BOTH dispatch dicts** in `animal.py`
  (`initialize_animal_methods` and
  `ANIMAL_TYPE_TO_LIFE_STAGE_UPDATE_METHOD_MAP`) and use early-return
  properties on `AnimalType` (`is_feedlot`-style) for behavioral shunts —
  never an `if/elif` chain on the animal type.
- **Extend existing structures, never add parallel ones** (repo-wide rule,
  see `RUFAS/CLAUDE.md`) — here that means: new cohorts go INTO the
  `animal_groups` list of `HerdManager._process_daily_herd_updates`, not
  into a second loop after it; new rations/constraints follow the existing
  registration lists in `ration_manager.py` / `ration_optimizer.py`.
- **Input schema keys mirror the nearest sibling block** (repo-wide rule,
  see `RUFAS/CLAUDE.md`) — here: herd counts are `num_<type>` (see
  `_initialize_feedlot_herd`: `num_steers`, `num_heifers`, `entry_weight`),
  never `n_*`.
- **Config parsing = merge-then-validate**: merge user config with class
  defaults FIRST, then validate the merged dict — the canonical pair is
  `AnimalConfig._merge_beef_defaults` +
  `DataValidator.validate_beef_cow_calf_config`. A validator that only
  checks keys present in the raw dict misses omissions.
- **Validation lives in `DataValidator` and the requirements calculators**
  — do not re-validate inside `Animal._initialize_*` methods (no sibling
  does).
- **Requirements calculators** (`nutrients/`): inputs dataclass +
  `_validate_inputs` covering EVERY float field (finite + domain), plus
  cross-guards rejecting the other calculators' animal types. Shared NRC
  helpers live in `BeefNRCRequirementsCalculator` — do not copy the
  sbw/eqsbw/empty-amino-acids boilerplate into a new calculator; extract a
  shared helper instead.
- **Reporter layering**: per-animal reporting goes through
  `AnimalModuleReporter`, called from `HerdManager` — never from
  `animal.py` (lower layer). Reuse the sibling's `MeasurementUnits` for the
  same quantity (e.g. FCR).
- **KNOWN LIMIT — feedlot daily loop is dormant**:
  `HerdManager.feedlot_animals` is not iterated daily (see the TODO near
  `_feedlot_life_stage_update` in `animal.py`). Any transition INTO feedlot
  is currently a simulation dead-end — state this as a scope boundary in
  `docs/beef_module/<module>/README.md` and in the changelog entry.

## Notes

- Inputs come from `input/data/animal/*.json` plus
  `input/data/animal_genetics/` and `input/data/animal_health/` (validated in
  `RUFAS/data_validator.py`). Several are CI-protected — see
  `.claude/rules/protected-inputs.md`.
- Feed arrives via the feed_storage→animal connection; manure/bedding leave via
  the animal→manure connection (`RUFAS/data_structures/`).
- Tests mirror this tree under `tests/test_biophysical/test_animal/`.
- Beef reference data (NRC 2016 workbooks, scope boundaries) lives in
  `docs/beef_module/`.

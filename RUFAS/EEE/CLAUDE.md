# RUFAS/EEE/ — Economics, Energy, Emissions

Cross-cutting layer that estimates energy use, emissions, and (economic) costs
from the physical model's activity.

- `EEE_manager.py` — orchestrates the EEE estimates for a run.
- `energy.py` — `EnergyEstimator` (e.g. diesel consumption from field ops).
- `emissions.py` — emissions estimates.
- `tractor.py` / `tractor_implement.py` — `Tractor` / `TractorImplement`
  machinery models for field-operation energy.

## Notes

- Driven by field-operation events (`FieldOperationEvent`, `TillageImplement`,
  `TractorSize`) defined in `RUFAS/data_structures/tillage_implements.py`.
- Defaults come from `input/data/EEE/default_costs.json` and
  `default_emissions.json` — both **CI-protected** (`.claude/rules/protected-inputs.md`).
- Tests in `tests/test_EEE/` with shared fixtures in
  `tests/test_EEE/fixtures.py`; they construct real `InputManager()` /
  `OutputManager()` and patch estimator methods with `pytest-mock`.

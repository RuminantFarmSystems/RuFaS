# RUFAS/biophysical/field/ — field / soil / crop subsystem

Models cropland: soil biogeochemistry, crop growth, and field operations.

- `manager/` — field subsystem manager (daily step + state).
- `field/` — field entity & field-operation logic.
- `crop/` — crop growth and rotations.
- `soil/` — soil model, split by nutrient cycle:
  - `carbon_cycling/`
  - `nitrogen_cycling/`
  - `phosphorus_cycling/`

## Notes

- Inputs: `input/data/field/`, `input/data/crop/`,
  `input/data/crop_configurations/` (crop config presets, e.g.
  `default_crop_configs.json` / `no_crop_configs.json`), `input/data/soil/`,
  `input/data/fertilizer_schedule/`, `input/data/tillage_schedule/`,
  `input/data/manure_schedule/`. Many are CI-protected — see
  `.claude/rules/protected-inputs.md`.
- Harvested material leaves through the crop_soil→feed_storage connection;
  manure applications enter through the manure→crop_soil connection
  (`RUFAS/data_structures/`).
- Field operations (tillage, etc.) feed the EEE layer via
  `FieldOperationEvent` / `TillageImplement` in
  `RUFAS/data_structures/tillage_implements.py`.
- Tests mirror this tree under `tests/test_biophysical/test_crop_soil_field/`.

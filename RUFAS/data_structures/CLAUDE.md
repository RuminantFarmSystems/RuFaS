# RUFAS/data_structures/ — inter-subsystem connections

Typed objects that move material and events **between** biophysical subsystems,
so domains stay decoupled. Use these instead of passing raw dicts across
subsystem boundaries.

## Connection objects (directional)

- `crop_soil_to_feed_storage_connection.py` — harvest → storage.
- `feed_storage_to_animal_connection.py` — feed → herd.
- `animal_to_manure_connection.py` — excretion/bedding → manure.
- `manure_to_crop_soil_connection.py` — manure application → field.
- `field_manure_supplier.py` — supplies field-bound manure.

## Domain types

- `manure_types.py`, `manure_nutrients.py`, `manure_supplement_methods.py` —
  manure composition/handling.
- `tillage_implements.py` — `FieldOperationEvent`, `TillageImplement`,
  `TractorSize` (consumed by `RUFAS/EEE/`).
- `events.py` — event structures used across the simulation.

## Notes

- These are plain typed data carriers — keep behaviour in the owning subsystem's
  manager, not here.
- Tests: `tests/test_data_structures/`.

# RUFAS/biophysical/ — biophysical model

The physical farm model, driven day-by-day by `RUFAS/simulation_engine.py`.
Four domains, each a manager-led subsystem:

- `animal/` — herd, pens, digestion, growth, milk, reproduction, health,
  rations, bedding. Largest subsystem (~24k LOC). Own `CLAUDE.md`.
- `field/` — fields, soil (C/N/P cycling), crops, field operations. (~22k LOC).
  Own `CLAUDE.md`.
- `manure/` — manure handling, storage, separators, digesters, processors,
  nutrient tracking (`manure_manager.py`, `manure_nutrient_manager.py`). Own
  `CLAUDE.md`.
- `feed_storage/` — silage, hay, baleage, grain, purchased feed; `feed_manager.py`
  + `storage.py` base. `feed_storage_enum.py` enumerates storage types. Own
  `CLAUDE.md`.

## Pattern

Each domain exposes a **`*_manager.py`** that owns the subsystem's daily step
and holds its state. Material crosses domains through typed objects in
`RUFAS/data_structures/` (e.g. field→feed_storage, feed_storage→animal,
animal→manure, manure→crop_soil) — don't pass raw dicts between subsystems.

Constants live in dedicated `*_constants.py` modules per domain. Never inline
a numeric literal in a formula — **including bounds/clamps** like
`max(x, 0.95)`: name it. Give EVERY constant a docstring UNDER the assignment
stating its unit and provenance: a bibliographic source for scientific values
(canonical style: `ACTIVATION_ENERGY` in `manure/manure_constants.py`), or an
explicit statement that it is a numerical/implementation guard (e.g.
"numerical guard against a near-zero denominator, not an NRC threshold" —
`BEEF_DMI_MIN_NE_CONCENTRATION`). **NEVER invent or approximate a citation to
satisfy this rule** — an honest "no source, here's why it exists" is
compliant; a fabricated reference is not. A constant without documented
provenance blocks review. If a formula clamps or bounds a value, say so in
the function's docstring (`Notes`) and cover the clamped branch with a test.

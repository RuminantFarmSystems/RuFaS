# RUFAS/biophysical/manure/ — manure subsystem

Handles manure from excretion/bedding through storage, treatment, and
land-application supply.

- `manure_manager.py` — owns the manure subsystem's daily step + state.
- `manure_nutrient_manager.py` — tracks N/P and other nutrients through manure.
- `processor.py` / `processor_enum.py` — manure processing units & their types.
- `manure_constants.py` — subsystem constants.

## Treatment sub-packages

- `separator/` — solid–liquid separation.
- `digester/` — anaerobic digestion.
- `handler/` — handling/transfer logic.
- `storage/` — manure storage structures.

## Flow

Receives material via the **animal→manure** connection
(`RUFAS/data_structures/animal_to_manure_connection.py`) and supplies field
application via **manure→crop_soil** + `field_manure_supplier.py`. Manure
composition types live in `RUFAS/data_structures/manure_*.py`.

Field operations involving manure feed the EEE energy/emissions layer.

Tests: `tests/test_biophysical/test_manure/`.

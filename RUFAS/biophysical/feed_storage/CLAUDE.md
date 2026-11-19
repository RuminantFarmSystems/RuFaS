# RUFAS/biophysical/feed_storage/ — feed storage subsystem

Stores harvested and purchased feed, models degradation/loss, and serves feed
to the herd.

- `feed_manager.py` — owns the feed-storage daily step + inventory.
- `storage.py` — base storage abstraction.
- `feed_storage_enum.py` — storage-type enumeration.
- Concrete stores: `silage.py`, `hay.py`, `baleage.py`, `grain.py`,
  `purchased_feed_storage.py`.

## Flow

Filled from harvest via the **crop_soil→feed_storage** connection
(`RUFAS/data_structures/crop_soil_to_feed_storage_connection.py`) and drains to
the herd via the **feed_storage→animal** connection. Feed planning /
degradation cadence is driven from `RUFAS/simulation_engine.py`
(`_execute_feed_planning`, `_is_time_to_process_feed_degradations`).

Tests: `tests/test_biophysical/test_feed_storage/`.

## Equation tag format (MSF convention)

Scientific equations implemented in this module are tagged with a structured
identifier used in docstrings and the IFSM/RuFaS flowcharts:

```
[<Subsystem>.<Module>.<#>]
```

| Segment | Meaning | Values in use |
|---|---|---|
| Subsystem | Top-level domain | `FS` = Feed Storage |
| Module | Storage type or function group | `SIL` = Silage · `NUT` = Nutrient recalculation · `HAY` = Hay · `BAL` = Baleage · `GRN` = Grain |
| `#` | Sequential equation number within the module | 1, 2, 3 … |

**Examples:** `FS.SIL.1` (alfalfa fermentation DM loss), `FS.NUT.1` (nutrient
passive concentration), `FS.SIL.4` (DM loss to effluent).

Reference the tag in the function's NumPy docstring `Notes` section and link
it to the corresponding IFSM equation number where applicable.

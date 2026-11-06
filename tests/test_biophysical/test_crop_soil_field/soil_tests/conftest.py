"""Shared fixtures for the soil tests.

Several soil tests monkey-patch ``LayerData`` class methods via direct
class-attribute assignment (e.g. ``LayerData.determine_soil_nutrient_concentration
= MagicMock()``) without restoring them. Under pytest < 8 the collection order
happened to run the victim tests (which call the real methods) before the
polluting ones, so the leak was invisible. pytest >= 8 changed collection
ordering, exposing the leak: tests such as
``test_layer_data.py::test_calculate_phosphorus_sorption_parameter`` then receive
the leaked ``MagicMock`` instead of the real method.

The autouse fixture below snapshots and restores ``LayerData``'s class state
around every soil test, keeping such monkey-patches test-local without having to
rewrite each call site. New leaks of the same kind are neutralised automatically.
"""

from typing import Iterator

import pytest

from RUFAS.biophysical.field.soil.layer_data import LayerData


@pytest.fixture(autouse=True)
def _isolate_layer_data_class_state() -> Iterator[None]:
    """Restore ``LayerData``'s class attributes after each test."""
    snapshot = dict(vars(LayerData))
    yield
    # Remove attributes added during the test.
    for name in list(vars(LayerData)):
        if name not in snapshot:
            delattr(LayerData, name)
    # Restore attributes that were replaced (e.g. monkey-patched methods).
    for name, value in snapshot.items():
        if vars(LayerData).get(name) is not value:
            try:
                setattr(LayerData, name, value)
            except (AttributeError, TypeError):
                pass

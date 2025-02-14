import pytest

from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover


def test_storage_init_error() -> None:
    """Test that Storage cannot be initialized because it does not fully implement the abstract base class."""

    with pytest.raises(TypeError):
        Storage(
            name="test storage",
            is_housing_emissions_calculator=False,
            cover=StorageCover.NO_COVER,
            storage_time_period=100,
        )

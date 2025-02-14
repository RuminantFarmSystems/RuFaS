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


# TODO: Test when a Storage child is implemented, either #2103, 2104, or 2105
def test_storage_init() -> None:
    """Test that a Storage instance is instantiated properly."""
    pass


# TODO: Test when a Storage child is implemented, either #2103, 2104, or 2105
def test_receive_manure() -> None:
    """Test that the receive_manure method in Storage works correctly."""
    pass

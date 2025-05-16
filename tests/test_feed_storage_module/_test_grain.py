import pytest

from RUFAS.data_structures.crop_soil_to_feed_storage_connection import CropCategory
from RUFAS.routines.feed_storage.grain import Grain


@pytest.fixture
def grain() -> Grain:
    """
    Pytest fixture to create a Grain instance for testing.

    Returns
    -------
    Grain
        An instance of the Grain class.
    """
    return Grain()


def test_acceptable_crops(grain: Grain):
    assert grain.acceptable_crops == [
        CropCategory.CORN,
        CropCategory.SMALL_GRAIN,
        CropCategory.SOY,
    ]

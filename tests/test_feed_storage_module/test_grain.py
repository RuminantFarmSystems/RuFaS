import pytest
from RUFAS.routines.feed_storage.grain import Grain
from RUFAS.routines.feed_storage.enums import CropCategory


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

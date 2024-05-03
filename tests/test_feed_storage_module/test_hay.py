import pytest
from RUFAS.routines.feed_storage.hay import Hay
from RUFAS.routines.feed_storage.enums import CropCategory


@pytest.fixture
def hay() -> Hay:
    """
    Pytest fixture to create a Hay instance for testing.

    Returns
    -------
    Hay
        An instance of the Hay class.
    """
    return Hay()


def test_acceptable_crops(hay: Hay):
    assert hay.acceptable_crops == [
        CropCategory.ALFALFA,
        CropCategory.GRASS,
        CropCategory.SMALL_GRAIN,
    ]

import pytest
from RUFAS.routines.feed_storage.baleage import Baleage
from RUFAS.routines.feed_storage.enums import CropCategory


@pytest.fixture
def baleage() -> Baleage:
    """
    Pytest fixture to create a Baleage instance for testing.

    Returns
    -------
    Baleage
        An instance of the Baleage class.
    """
    return Baleage()


def test_acceptable_crops(baleage: Baleage):
    assert baleage.acceptable_crops == [
        CropCategory.ALFALFA,
        CropCategory.GRASS,
        CropCategory.SMALL_GRAIN,
    ]

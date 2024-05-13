import pytest
from RUFAS.routines.feed_storage.sileage import Sileage, Bunker, Pile, Bag
from RUFAS.routines.feed_storage.enums import CropCategory


@pytest.fixture
def sileage() -> Sileage:
    return Sileage()


def test_acceptable_crops(sileage: Sileage):
    assert sileage.acceptable_crops == [
        CropCategory.ALFALFA,
        CropCategory.CORN,
        CropCategory.GRASS,
        CropCategory.SMALL_GRAIN,
    ]


@pytest.fixture
def bunker() -> Bunker:
    return Bunker()


@pytest.fixture
def pile() -> Pile:
    return Pile()


@pytest.fixture
def bag() -> Bag:
    return Bag()

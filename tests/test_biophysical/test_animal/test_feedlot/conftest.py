import pytest
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


@pytest.fixture(scope="module")
def all_animal_types() -> list[AnimalType]:
    """All AnimalType enum members."""
    return list(AnimalType)


@pytest.fixture(scope="module")
def feedlot_types() -> list[AnimalType]:
    """Only the feedlot AnimalType members."""
    return [AnimalType.FEEDLOT_STEER, AnimalType.FEEDLOT_HEIFER]


@pytest.fixture(scope="module")
def dairy_types() -> list[AnimalType]:
    """All non-feedlot AnimalType members."""
    return [
        AnimalType.CALF,
        AnimalType.HEIFER_I,
        AnimalType.HEIFER_II,
        AnimalType.HEIFER_III,
        AnimalType.DRY_COW,
        AnimalType.LAC_COW,
    ]

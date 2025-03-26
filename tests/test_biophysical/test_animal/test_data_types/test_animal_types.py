from typing import Generator
import pytest

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


@pytest.fixture(scope="module")
def all_animal_types() -> Generator[list[AnimalType], None, None]:
    """Fixture providing all AnimalType enum members"""
    yield list(AnimalType)


@pytest.mark.parametrize("heifer_type", [AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III])
def test_is_heifer_true(heifer_type: AnimalType) -> None:
    """Test that heifer types return True for is_heifer"""
    assert heifer_type.is_heifer is True
    assert heifer_type.is_cow is False


@pytest.mark.parametrize("cow_type", [AnimalType.DRY_COW, AnimalType.LAC_COW])
def test_is_cow_true(cow_type: AnimalType) -> None:
    """Test that cow types return True for is_cow"""
    assert cow_type.is_cow is True
    assert cow_type.is_heifer is False


@pytest.mark.parametrize("non_heifer_non_cow", [AnimalType.CALF])
def test_is_heifer_is_cow_false(non_heifer_non_cow: AnimalType) -> None:
    """Test that a non-heifer, non-cow type returns False for both properties"""
    assert non_heifer_non_cow.is_heifer is False
    assert non_heifer_non_cow.is_cow is False


def test_all_animal_types_have_expected_properties(all_animal_types: list[AnimalType]) -> None:
    """Ensure all AnimalType members return expected boolean values"""
    heifer_types = {AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III}
    cow_types = {AnimalType.DRY_COW, AnimalType.LAC_COW}

    for animal in all_animal_types:
        expected_is_heifer = animal in heifer_types
        expected_is_cow = animal in cow_types

        assert animal.is_heifer == expected_is_heifer, f"Unexpected is_heifer value for {animal}"
        assert animal.is_cow == expected_is_cow, f"Unexpected is_cow value for {animal}"

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_grouping_scenarios import AnimalGroupingScenario
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


def test_find_animal_combination_matches_enum_mapping(mocker: MockerFixture) -> None:
    """
    For each scenario, and for each animal_type listed in its value mapping,
    find_animal_combination should return the corresponding AnimalCombination.
    This exercises:
      * the Enum __init__ that builds _animal_combination_by_animal_type
      * get_animal_type
      * find_animal_combination
    """
    for scenario in (
        AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW,
        AnimalGroupingScenario.CALF__GROWING_AND_CLOSE_UP__LACCOW,
    ):
        for animal_combination, animal_types in scenario.value.items():
            for animal_type in animal_types:
                animal = mocker.Mock(spec=Animal)
                animal.animal_type = animal_type

                result = scenario.find_animal_combination(animal)

                assert result == animal_combination


@pytest.mark.parametrize(
    "method_name, expected_type",
    [
        ("_get_calf_type", AnimalType.CALF),
        ("_get_heiferI_type", AnimalType.HEIFER_I),
        ("_get_heiferII_type", AnimalType.HEIFER_II),
        ("_get_heiferIII_type", AnimalType.HEIFER_III),
    ],
)
def test_youngstock_get_type_helpers_return_expected_animal_type(
    mocker: MockerFixture,
    method_name: str,
    expected_type: AnimalType,
) -> None:
    """
    Directly exercise the simple *_type helper methods to ensure they return the
    correct AnimalType. The passed Animal instance is not used, but we provide
    a spec'd mock for safety.
    """
    scenario = AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW
    animal = mocker.Mock(spec=Animal)

    method = getattr(scenario, method_name)
    result = method(animal)

    assert result == expected_type


@pytest.mark.parametrize(
    "scenario, is_lactating, expected_type",
    [
        (
            AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW,
            True,
            AnimalType.LAC_COW,
        ),
        (
            AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW,
            False,
            AnimalType.DRY_COW,
        ),
        (
            AnimalGroupingScenario.CALF__GROWING_AND_CLOSE_UP__LACCOW,
            True,
            AnimalType.LAC_COW,
        ),
        (
            AnimalGroupingScenario.CALF__GROWING_AND_CLOSE_UP__LACCOW,
            False,
            AnimalType.DRY_COW,
        ),
    ],
)
def test_get_cow_type_uses_is_lactating_and_scenario(
    mocker: MockerFixture,
    scenario: AnimalGroupingScenario,
    is_lactating: bool,
    expected_type: AnimalType,
) -> None:
    """
    _get_cow_type should map to LAC_COW or DRY_COW based on is_lactating,
    for both grouping scenarios.
    """
    cow = mocker.Mock(spec=Animal)
    cow.is_lactating = is_lactating

    result = scenario._get_cow_type(cow)

    assert result == expected_type


def test_get_animal_type_returns_animal_attribute(mocker: MockerFixture) -> None:
    """
    get_animal_type should simply return animal.animal_type.
    """
    scenario = AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW
    animal = mocker.Mock(spec=Animal)
    animal.animal_type = AnimalType.CALF

    result = scenario.get_animal_type(animal)

    assert result == AnimalType.CALF

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.enums import AnimalCombination
from RUFAS.general_constants import GeneralConstants

from tests.test_biophysical.test_animal.test_herd_manager.pytest_fixtures import (
    config_json, animal_json, manure_management_json, feed_json, mock_get_data_side_effect,
    mock_herd, herd_manager
)

assert config_json is not None
assert animal_json is not None
assert manure_management_json is not None
assert feed_json is not None
assert mock_get_data_side_effect is not None
assert mock_herd is not None
assert herd_manager is not None


def test_animals_by_type(
        herd_manager: HerdManager, mock_herd: dict[str, list[Animal]]
) -> None:
    """Unit test for HerdManager.animals_by_type property"""
    expected_animals_by_type: dict[AnimalType, list[Animal]] = {
        AnimalType.CALF: mock_herd["calves"],
        AnimalType.HEIFER_I: mock_herd["heiferIs"],
        AnimalType.HEIFER_II: mock_herd["heiferIIs"],
        AnimalType.HEIFER_III: mock_herd["heiferIIIs"],
        AnimalType.DRY_COW: mock_herd["dry_cows"],
        AnimalType.LAC_COW: mock_herd["lac_cows"],
    }
    actual = herd_manager.animals_by_type

    assert actual == expected_animals_by_type


def test_animals_by_combination(
        herd_manager: HerdManager, mock_herd: dict[str, list[Animal]]
) -> None:
    """Unit test for HerdManager.animals_by_combination property"""
    expected_animals_by_combination: dict[AnimalCombination, list[Animal]] = {
        AnimalCombination.CALF: mock_herd["calves"],
        AnimalCombination.GROWING: mock_herd["heiferIs"] + mock_herd["heiferIIs"],
        AnimalCombination.CLOSE_UP: mock_herd["heiferIIIs"] + mock_herd["dry_cows"],
        AnimalCombination.LAC_COW: mock_herd["lac_cows"],
    }
    actual = herd_manager.animals_by_combination

    assert actual == expected_animals_by_combination


def test_pens_by_animal_combination(
        herd_manager: HerdManager
) -> None:
    """Unit test for HerdManager.pens_by_animal_combination property"""
    expected_pens_by_combination: dict[AnimalCombination, list[Pen]] = {
        AnimalCombination.CALF: [],
        AnimalCombination.GROWING: [],
        AnimalCombination.CLOSE_UP: [],
        AnimalCombination.LAC_COW: [],
    }
    for pen in herd_manager.all_pens:
        expected_pens_by_combination[pen.animal_combination].append(pen)

    actual = herd_manager.pens_by_animal_combination

    assert actual == expected_pens_by_combination


def test_phosphorus_concentration_by_animal_class(
        herd_manager: HerdManager, mock_herd: dict[str, list[Animal]]
) -> None:
    """Unit test for HerdManager.phosphorus_concentration_by_animal_class property"""
    expected_phosphorus_concentration_by_animal_class: dict[AnimalType, float] = {
        AnimalType.CALF: 0.0,
        AnimalType.HEIFER_I: 0.0,
        AnimalType.HEIFER_II: 0.0,
        AnimalType.HEIFER_III: 0.0,
        AnimalType.DRY_COW: 0.0,
        AnimalType.LAC_COW: 0.0,
    }
    animals_by_type_mapping: dict[AnimalType, list[Animal]] = {
        AnimalType.CALF: mock_herd["calves"],
        AnimalType.HEIFER_I: mock_herd["heiferIs"],
        AnimalType.HEIFER_II: mock_herd["heiferIIs"],
        AnimalType.HEIFER_III: mock_herd["heiferIIIs"],
        AnimalType.DRY_COW: mock_herd["dry_cows"],
        AnimalType.LAC_COW: mock_herd["lac_cows"],
    }

    for animal_type in [AnimalType.CALF, AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III,
                        AnimalType.LAC_COW, AnimalType.DRY_COW]:
        animals = animals_by_type_mapping[animal_type]
        total_phosphorus = sum([animal.nutrients.total_phosphorus_in_animal * GeneralConstants.GRAMS_TO_KG
                                for animal in animals])
        total_body_weight = sum([animal.body_weight for animal in animals])
        expected_phosphorus_concentration_by_animal_class[animal_type] = (
            total_phosphorus / total_body_weight if total_body_weight > 0 else 0.0
        )

    actual = herd_manager.phosphorus_concentration_by_animal_class

    assert actual == expected_phosphorus_concentration_by_animal_class

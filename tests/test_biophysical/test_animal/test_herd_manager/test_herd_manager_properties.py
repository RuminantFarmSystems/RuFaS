from unittest.mock import MagicMock
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.general_constants import GeneralConstants

from tests.test_biophysical.test_animal.test_herd_manager.pytest_fixtures import (
    config_json,
    animal_json,
    feed_json,
    mock_get_data_side_effect,
    mock_herd,
    herd_manager,
)

assert config_json is not None
assert animal_json is not None
assert feed_json is not None
assert mock_get_data_side_effect is not None
assert mock_herd is not None
assert herd_manager is not None


def test_animals_by_type(herd_manager: HerdManager, mock_herd: dict[str, list[Animal]]) -> None:
    """Unit test for HerdManager.animals_by_type property"""
    expected_animals_by_type: dict[AnimalType, list[Animal]] = {
        AnimalType.CALF: mock_herd["calves"],
        AnimalType.HEIFER_I: mock_herd["heiferIs"],
        AnimalType.HEIFER_II: mock_herd["heiferIIs"],
        AnimalType.HEIFER_III: mock_herd["heiferIIIs"],
        AnimalType.DRY_COW: mock_herd["dry_cows"],
        AnimalType.LAC_COW: mock_herd["lac_cows"],
        AnimalType.FEEDLOT_STEER: herd_manager.feedlot_animals,
        AnimalType.FEEDLOT_HEIFER: herd_manager.feedlot_animals,
        AnimalType.BEEF_COW: herd_manager.beef_cows,
        AnimalType.BEEF_HEIFER_REPLACEMENT: herd_manager.beef_replacement_heifers,
        AnimalType.BEEF_CALF: herd_manager.beef_calves,
        AnimalType.BEEF_BULL: herd_manager.beef_bulls,
    }
    actual = herd_manager.animals_by_type

    assert actual == expected_animals_by_type


def test_animals_by_combination(herd_manager: HerdManager, mock_herd: dict[str, list[Animal]]) -> None:
    """Unit test for HerdManager.animals_by_combination property"""
    expected_animals_by_combination: dict[AnimalCombination, list[Animal]] = {
        AnimalCombination.CALF: mock_herd["calves"],
        AnimalCombination.GROWING: mock_herd["heiferIs"] + mock_herd["heiferIIs"],
        AnimalCombination.CLOSE_UP: mock_herd["heiferIIIs"] + mock_herd["dry_cows"],
        AnimalCombination.LAC_COW: mock_herd["lac_cows"],
    }
    actual = herd_manager.animals_by_combination

    assert actual == expected_animals_by_combination


def test_pens_by_animal_combination(herd_manager: HerdManager) -> None:
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
        AnimalType.FEEDLOT_STEER: 0.0,
        AnimalType.FEEDLOT_HEIFER: 0.0,
        AnimalType.BEEF_COW: 0.0,
        AnimalType.BEEF_HEIFER_REPLACEMENT: 0.0,
        AnimalType.BEEF_CALF: 0.0,
        AnimalType.BEEF_BULL: 0.0,
    }
    animals_by_type_mapping: dict[AnimalType, list[Animal]] = {
        AnimalType.CALF: mock_herd["calves"],
        AnimalType.HEIFER_I: mock_herd["heiferIs"],
        AnimalType.HEIFER_II: mock_herd["heiferIIs"],
        AnimalType.HEIFER_III: mock_herd["heiferIIIs"],
        AnimalType.DRY_COW: mock_herd["dry_cows"],
        AnimalType.LAC_COW: mock_herd["lac_cows"],
        AnimalType.FEEDLOT_STEER: [],
        AnimalType.FEEDLOT_HEIFER: [],
        AnimalType.BEEF_COW: herd_manager.beef_cows,
        AnimalType.BEEF_HEIFER_REPLACEMENT: herd_manager.beef_replacement_heifers,
        AnimalType.BEEF_CALF: herd_manager.beef_calves,
        AnimalType.BEEF_BULL: herd_manager.beef_bulls,
    }

    for animal_type, animals in animals_by_type_mapping.items():
        total_phosphorus = sum(
            [animal.nutrients.total_phosphorus_in_animal * GeneralConstants.GRAMS_TO_KG for animal in animals]
        )
        total_body_weight = sum([animal.body_weight for animal in animals])
        expected_phosphorus_concentration_by_animal_class[animal_type] = (
            total_phosphorus / total_body_weight if total_body_weight > 0 else 0.0
        )

    actual = herd_manager.phosphorus_concentration_by_animal_class

    assert actual == expected_phosphorus_concentration_by_animal_class


def test_heiferII_events_by_id_returns_expected_mapping(herd_manager: HerdManager) -> None:
    """heiferII_events_by_id should map 'HEIFER_II_<id>' -> events for each HeiferII."""
    expected = {f"{heiferII.animal_type.name}_{heiferII.id}": heiferII.events for heiferII in herd_manager.heiferIIs}

    result = herd_manager.heiferII_events_by_id

    assert result == expected


def test_heiferII_events_by_id_empty_when_no_heiferIIs(herd_manager: HerdManager) -> None:
    """heiferII_events_by_id should return an empty dict when there are no HeiferII animals."""
    herd_manager.heiferIIs = []

    result = herd_manager.heiferII_events_by_id

    assert result == {}


def test_cow_events_by_id_returns_expected_mapping(herd_manager: HerdManager) -> None:
    """cow_events_by_id should map 'COWTYPE_<id>' -> events for each cow."""

    expected = {f"{cow.animal_type.name}_{cow.id}": cow.events for cow in herd_manager.cows}

    result = herd_manager.cow_events_by_id

    assert result == expected


def test_cow_events_by_id_empty_when_no_cows(herd_manager: HerdManager) -> None:
    """cow_events_by_id should return an empty dict when herd_manager.cows is empty."""

    herd_manager.cows = []

    result = herd_manager.cow_events_by_id

    assert result == {}


def test_average_305_day_milk_yield_by_lactation_group(herd_manager: HerdManager) -> None:
    """Correctly returns average 305-day milk yield values for L1, L2, and L3+ cohorts."""
    herd_manager.cows = []

    cow1 = MagicMock()
    cow1.reproduction.calves = 1
    cow1.milk_production.milk_305_day_yield = 9000

    cow2 = MagicMock()
    cow2.reproduction.calves = 1
    cow2.milk_production.milk_305_day_yield = 7000

    cow3 = MagicMock()
    cow3.reproduction.calves = 2
    cow3.milk_production.milk_305_day_yield = 8500

    cow4 = MagicMock()
    cow4.reproduction.calves = 3
    cow4.milk_production.milk_305_day_yield = 10000

    cow5 = MagicMock()
    cow5.reproduction.calves = 4
    cow5.milk_production.milk_305_day_yield = 11000

    herd_manager.cows.extend([cow1, cow2, cow3, cow4, cow5])

    assert herd_manager.average_l1_305_day_milk_yield == 8000
    assert herd_manager.average_l2_305_day_milk_yield == 8500
    assert herd_manager.average_l3_plus_305_day_milk_yield == 10500

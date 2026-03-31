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
    }
    animals_by_type_mapping: dict[AnimalType, list[Animal]] = {
        AnimalType.CALF: mock_herd["calves"],
        AnimalType.HEIFER_I: mock_herd["heiferIs"],
        AnimalType.HEIFER_II: mock_herd["heiferIIs"],
        AnimalType.HEIFER_III: mock_herd["heiferIIIs"],
        AnimalType.DRY_COW: mock_herd["dry_cows"],
        AnimalType.LAC_COW: mock_herd["lac_cows"],
    }

    for animal_type in [
        AnimalType.CALF,
        AnimalType.HEIFER_I,
        AnimalType.HEIFER_II,
        AnimalType.HEIFER_III,
        AnimalType.LAC_COW,
        AnimalType.DRY_COW,
    ]:
        animals = animals_by_type_mapping[animal_type]
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


def test_average_herd_305_days_milk_production_all_zero_or_not_milking(
    herd_manager: HerdManager,
) -> None:
    """If no milking cows with positive 305-day production, return 0.0."""
    herd_manager.cows = []

    for i in range(3):
        cow = MagicMock()
        cow.is_milking = False
        cow.milk_production.current_lactation_305_day_milk_produced = 0
        herd_manager.cows.append(cow)

    assert herd_manager.average_herd_305_days_milk_production == 0.0


def test_average_herd_305_days_milk_production_single_cow(
    herd_manager: HerdManager,
) -> None:
    """Correctly returns single cow's positive 305-day milk production."""

    herd_manager.cows = []

    cow = MagicMock()
    cow.is_milking = True
    cow.milk_production.current_lactation_305_day_milk_produced = 9000
    herd_manager.cows.append(cow)

    assert herd_manager.average_herd_305_days_milk_production == 9000


def test_average_herd_305_days_milk_production_multiple_cows(
    herd_manager: HerdManager,
) -> None:
    """Correct average for multiple milking cows with positive 305-day production."""

    herd_manager.cows = []

    cow1 = MagicMock()
    cow1.is_milking = True
    cow1.milk_production.current_lactation_305_day_milk_produced = 10000

    cow2 = MagicMock()
    cow2.is_milking = True
    cow2.milk_production.current_lactation_305_day_milk_produced = 8000

    cow3 = MagicMock()
    cow3.is_milking = False
    cow3.milk_production.current_lactation_305_day_milk_produced = 5000

    herd_manager.cows.extend([cow1, cow2, cow3])

    expected_avg = (10000 + 8000) / 2

    assert herd_manager.average_herd_305_days_milk_production == expected_avg


def test_average_herd_305_days_milk_production_milking_but_production_nonpositive(
    herd_manager: HerdManager,
) -> None:
    """Milking cows with ≤0 production should be excluded; if all excluded → 0.0."""

    herd_manager.cows = []

    for prod in [0, -2000, 0]:
        cow = MagicMock()
        cow.is_milking = True
        cow.milk_production.current_lactation_305_day_milk_produced = prod
        herd_manager.cows.append(cow)

    assert herd_manager.average_herd_305_days_milk_production == 0.0

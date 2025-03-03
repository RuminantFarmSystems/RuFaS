from datetime import datetime
from typing import Any
from unittest.mock import call, MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.biophysical.feed.feed import Feed
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.feed_storage_to_animal_connection import TotalInventory
from RUFAS.enums import AnimalCombination
from tests.test_biophysical.test_animal.test_herd_manager.pytest_fixtures import (
    config_json, animal_json, manure_management_json, feed_json, mock_get_data_side_effect,
    mock_herd_manager, mock_herd, herd_manager
)

assert config_json is not None
assert animal_json is not None
assert manure_management_json is not None
assert feed_json is not None
assert mock_get_data_side_effect is not None
assert herd_manager is not None
assert mock_herd is not None


def test_initialize_pens(
    animal_json: dict[str, Any],
    manure_management_json: dict[str, Any],
    mock_get_data_side_effect: list[Any],
    mocker: MockerFixture,
) -> None:
    herd_manager, _ = mock_herd_manager(
        calves=[],
        heiferIs=[],
        heiferIIs=[],
        heiferIIIs=[],
        cows=[],
        replacement=[],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect,
    )
    herd_manager.all_pens = []

    herd_manager.initialize_pens(
        all_pen_data=animal_json["pen_information"],
        manure_management_scenarios=manure_management_json["manure_management_scenarios"],
    )

    expected_pen_configs = [
        {
            "pen_id": pen_config["id"],
            "pen_name": pen_config["pen_name"],
            "vertical_dist_to_milking_parlor": pen_config["vertical_dist_to_milking_parlor"],
            "horizontal_dist_to_milking_parlor": pen_config["horizontal_dist_to_milking_parlor"],
            "number_of_stalls": pen_config["number_of_stalls"],
            "housing_type": pen_config["housing_type"],
            "pen_type": pen_config["pen_type"],
            "max_stocking_density": pen_config["max_stocking_density"],
            "animal_combination": pen_config["animal_combination"],
            "bedding_type": manure_management_json["manure_management_scenarios"][
                pen_config["manure_management_scenario_id"]
            ]["bedding_type"],
            "manure_handling": manure_management_json["manure_management_scenarios"][
                pen_config["manure_management_scenario_id"]
            ]["manure_handler"],
            "manure_separator": manure_management_json["manure_management_scenarios"][
                pen_config["manure_management_scenario_id"]
            ]["manure_separator"],
            "manure_separator_after_digestion": manure_management_json["manure_management_scenarios"][
                pen_config["manure_management_scenario_id"]
            ]["manure_separator_after_digestion"],
            "manure_storage": manure_management_json["manure_management_scenarios"][
                pen_config["manure_management_scenario_id"]
            ]["manure_treatment"],
        }
        for pen_config in animal_json["pen_information"]
    ]

    for pen_num in range(len(herd_manager.all_pens)):
        pen = herd_manager.all_pens[pen_num]
        assert pen.id == expected_pen_configs[pen_num]["pen_id"]
        assert pen.pen_name == expected_pen_configs[pen_num]["pen_name"]
        assert pen.vertical_dist_to_parlor == expected_pen_configs[pen_num]["vertical_dist_to_milking_parlor"]
        assert pen.horizontal_dist_to_parlor == expected_pen_configs[pen_num]["horizontal_dist_to_milking_parlor"]
        assert pen.num_stalls == expected_pen_configs[pen_num]["number_of_stalls"]
        assert pen.housing_type == expected_pen_configs[pen_num]["housing_type"]
        assert pen.pen_type == expected_pen_configs[pen_num]["pen_type"]
        assert pen.max_stocking_density == expected_pen_configs[pen_num]["max_stocking_density"]
        assert pen.animal_combination.name == expected_pen_configs[pen_num]["animal_combination"]
        assert pen.bedding_type == expected_pen_configs[pen_num]["bedding_type"]
        assert pen.manure_handling == expected_pen_configs[pen_num]["manure_handling"]
        assert pen.manure_separator == expected_pen_configs[pen_num]["manure_separator"]
        assert pen.manure_separator_after_digestion == expected_pen_configs[pen_num]["manure_separator_after_digestion"]
        assert pen.manure_storage == expected_pen_configs[pen_num]["manure_storage"]


def test_allocate_animals_to_pens(
    herd_manager: HerdManager, mocker: MockerFixture, mock_herd: dict[str, list[Animal]]
) -> None:
    mock_allocate_animals_to_pens_helper = mocker.patch.object(herd_manager, "_allocate_animals_to_pens_helper")
    mock_fully_update_animal_to_pen_id_map = mocker.patch.object(herd_manager, "fully_update_animal_to_pen_id_map")

    herd_manager.allocate_animals_to_pens()

    assert mock_allocate_animals_to_pens_helper.call_args_list == [
        call(mock_herd["calves"], herd_manager.pens_by_animal_combination[AnimalCombination.CALF]),
        call(
            mock_herd["heiferIs"] + mock_herd["heiferIIs"],
            herd_manager.pens_by_animal_combination[AnimalCombination.GROWING],
        ),
        call(
            mock_herd["heiferIIIs"] + mock_herd["dry_cows"],
            herd_manager.pens_by_animal_combination[AnimalCombination.CLOSE_UP],
        ),
        call(mock_herd["lac_cows"], herd_manager.pens_by_animal_combination[AnimalCombination.LAC_COW]),
    ]
    mock_fully_update_animal_to_pen_id_map.assert_called_once()


def test_remove_animal_from_pen_and_id_map(
    herd_manager: HerdManager, mocker: MockerFixture, mock_herd: dict[str, list[Animal]]
) -> None:
    animals = (
        mock_herd["calves"]
        + mock_herd["heiferIs"]
        + mock_herd["heiferIIs"]
        + mock_herd["heiferIIIs"]
        + mock_herd["dry_cows"]
        + mock_herd["lac_cows"]
    )
    herd_manager.animal_to_pen_id_map = {
        animal.id: herd_manager.pens_by_animal_combination[
            herd_manager.ANIMAL_GROUPING_SCENARIO.find_animal_combination(animal)
        ][0].id
        for animal in animals
    }

    mock_pen_remove_animals_by_ids = mocker.patch("RUFAS.biophysical.animal.pen.Pen.remove_animals_by_ids")

    for animal in animals:
        herd_manager._remove_animal_from_pen_and_id_map(animal)
        mock_pen_remove_animals_by_ids.assert_called_with([animal.id])

    assert herd_manager.animal_to_pen_id_map == {}


def test_add_animal_to_pen_and_id_map(
    herd_manager: HerdManager, mocker: MockerFixture, mock_herd: dict[str, list[Animal]]
) -> None:
    mock_current_day_conditions = MagicMock(auto_spec=CurrentDayConditions)
    animals = (
        mock_herd["calves"]
        + mock_herd["heiferIs"]
        + mock_herd["heiferIIs"]
        + mock_herd["heiferIIIs"]
        + mock_herd["dry_cows"]
        + mock_herd["lac_cows"]
    )
    herd_manager.animal_to_pen_id_map = {}

    mock_pen_update_animals = mocker.patch("RUFAS.biophysical.animal.pen.Pen.update_animals")

    mock_feed = mocker.MagicMock(auto_spec=Feed)
    for animal in animals:
        herd_manager._add_animal_to_pen_and_id_map(
            animal, mock_feed, mock_current_day_conditions, TotalInventory({}, datetime.today().date())
        )
        mock_pen_update_animals.assert_called_with(
            [animal],
            herd_manager.ANIMAL_GROUPING_SCENARIO.find_animal_combination(animal),
            mock_feed,
        )

    assert herd_manager.animal_to_pen_id_map == {
        animal.id: herd_manager.pens_by_animal_combination[
            herd_manager.ANIMAL_GROUPING_SCENARIO.find_animal_combination(animal)
        ][0].id
        for animal in animals
    }


def test_create_additional_pens(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    expected_num_new_pens = {
        AnimalCombination.CALF: 2,
        AnimalCombination.GROWING: 2,
        AnimalCombination.CLOSE_UP: 0,
        AnimalCombination.LAC_COW: 6,
    }
    expected_num_stalls_per_additional_pen = {
        AnimalCombination.CALF: 3,
        AnimalCombination.GROWING: 3,
        AnimalCombination.CLOSE_UP: 0,
        AnimalCombination.LAC_COW: 8,
    }
    animal_space_shortage_map = {
        AnimalCombination.CALF: 2,
        AnimalCombination.GROWING: 2,
        AnimalCombination.CLOSE_UP: 0,
        AnimalCombination.LAC_COW: 6,
    }

    mock_calculate_max_animal_spaces_per_pen = mocker.patch.object(
        herd_manager, "_calculate_max_animal_spaces_per_pen", side_effect=[1, 1, 1, 1]
    )

    for animal_combination, pens in herd_manager.pens_by_animal_combination.items():
        reference_pen = pens[0]
        expected_new_pens: list[Pen] = []
        num_new_pens = expected_num_new_pens[animal_combination]
        animal_space_shortage = animal_space_shortage_map[animal_combination]
        for i in range(num_new_pens):
            new_pen_id = reference_pen.id + i
            expected_new_pens.append(
                Pen(
                    pen_id=new_pen_id,
                    pen_name=str(new_pen_id),
                    vertical_dist_to_milking_parlor=reference_pen.vertical_dist_to_parlor,
                    horizontal_dist_to_milking_parlor=reference_pen.horizontal_dist_to_parlor,
                    number_of_stalls=expected_num_stalls_per_additional_pen[animal_combination],
                    housing_type=reference_pen.housing_type,
                    bedding_type=reference_pen.bedding_type,
                    pen_type=reference_pen.pen_type,
                    manure_handling=reference_pen.manure_handling,
                    manure_separator=reference_pen.manure_separator,
                    manure_separator_after_digestion=reference_pen.manure_separator_after_digestion,
                    manure_storage=reference_pen.manure_storage,
                    animal_combination=animal_combination,
                    max_stocking_density=reference_pen.max_stocking_density,
                )
            )
        result: list[Pen] = herd_manager._create_additional_pens(
            pens=pens, animal_combination=animal_combination, start_pen_id=reference_pen.id,
            animal_space_shortage=animal_space_shortage
        )

        if expected_num_new_pens[animal_combination] > 0:
            mock_calculate_max_animal_spaces_per_pen.assert_called_with(
                num_stalls=expected_num_stalls_per_additional_pen[animal_combination],
                max_stocking_density=reference_pen.max_stocking_density,
            )

        for j in range(len(result)):
            result_pen: Pen = result[j]
            expected_pen: Pen = expected_new_pens[j] if j < len(expected_new_pens) else MagicMock(auto_spec=Pen)
            assert result_pen.id == expected_pen.id
            assert result_pen.pen_name == expected_pen.pen_name
            assert result_pen.vertical_dist_to_parlor == expected_pen.vertical_dist_to_parlor
            assert result_pen.horizontal_dist_to_parlor == expected_pen.horizontal_dist_to_parlor
            assert result_pen.num_stalls == expected_pen.num_stalls
            assert result_pen.housing_type == expected_pen.housing_type
            assert result_pen.bedding_type == expected_pen.bedding_type
            assert result_pen.pen_type == expected_pen.pen_type
            assert result_pen.manure_handling == expected_pen.manure_handling
            assert result_pen.manure_separator == expected_pen.manure_separator
            assert result_pen.manure_separator_after_digestion == expected_pen.manure_separator_after_digestion
            assert result_pen.manure_storage == expected_pen.manure_storage
            assert result_pen.animal_combination == animal_combination
            assert result_pen.max_stocking_density == expected_pen.max_stocking_density


@pytest.mark.parametrize(
    "num_stalls, max_stocking_density, expected, raise_value_error",
    [
        (100, 1.2, 120, False),
        (7, 1.2, 8, False),
        (0, 1.1, 0, False),
        (100, 0, 0, False),
        (-1, 1.2, None, True),
        (100, -1, None, True),
    ],
)
def test_calculate_max_animal_spaces_per_pen(
    num_stalls: int,
    max_stocking_density: float,
    expected: int | None,
    raise_value_error: bool,
    herd_manager: HerdManager
) -> None:
    if raise_value_error:
        with pytest.raises(ValueError):
            herd_manager._calculate_max_animal_spaces_per_pen(num_stalls, max_stocking_density)
    else:
        result = herd_manager._calculate_max_animal_spaces_per_pen(num_stalls, max_stocking_density)
        assert result == expected


@pytest.mark.parametrize(
    "num_animals,num_stalls,max_stocking_density,expected",
    [
        # 1. Exact Match Capacity
        (10, [10], [1.0], 0),
        # 2. Insufficient Capacity
        (10, [10], [0.5], 5),
        # 3. Multiple Pens, Exact Match
        (10, [5, 5], [1.0, 1.0], 0),
        # 4. Multiple Pens, Surplus Capacity
        (10, [10, 10], [1.0, 1.0], -10),
        # 5. Mixed Densities and Multiple Pens
        (15, [5, 10], [1.0, 1.5], -5),
        # 6. Multiple Pens, Large Exact Match
        (50, [10, 20, 10], [1.0, 1.0, 2.0], 0),
        # 7. Large Shortage
        (100, [10, 20, 30], [1.0, 1.0, 1.0], 40),
        # 8. No Pens Provided
        (10, [], [], 10),
    ],
)
def test_calculate_animal_space_shortage(
    num_animals: int,
    num_stalls: list[int],
    max_stocking_density: list[float],
    expected: int | None,
    herd_manager: HerdManager,
    mocker: MockerFixture
) -> None:

    mock_pens: list[Pen] = []
    for n in range(len(num_stalls)):
        dummy_pen = mocker.MagicMock(auto_spec=Pen)
        dummy_pen.num_stalls = num_stalls[n]
        dummy_pen.max_stocking_density = max_stocking_density[n]
        mock_pens.append(dummy_pen)

    result = herd_manager._calculate_animal_space_shortage(num_animals=num_animals, pens=mock_pens)

    assert result == expected


@pytest.mark.parametrize(
    "num_animals, num_spaces, expected, raise_value_error",
    [
        # Valid scenarios
        (0, 10, 0.0, False),  # No animals, positive spaces
        (10, 5, 2.0, False),  # More animals than spaces => density > 1
        (5, 10, 0.5, False),  # Fewer animals than spaces => density < 1
        (10, 10, 1.0, False),  # Equal animals and spaces => density = 1
        (100, 20, 5.0, False),  # Large numbers
        (1, 1, 1.0, False),  # Minimal positive values
        (50, 100, 0.5, False),  # Ratio less than 1 but valid
        # Error scenarios
        (-1, 10, None, True),  # Negative animals
        (10, 0, None, True),  # Zero spaces
        (10, -5, None, True),  # Negative spaces
    ],
)
def test_calculate_density(
    num_animals: int,
    num_spaces: int,
    expected: float,
    raise_value_error: bool,
    herd_manager: HerdManager
) -> None:
    if raise_value_error:
        with pytest.raises(ValueError):
            herd_manager._calculate_density(num_animals, num_spaces)
    else:
        result = herd_manager._calculate_density(num_animals, num_spaces)
        assert result == expected


def test_gather_pen_history(
        herd_manager: HerdManager, mock_herd: dict[str, list[Animal]], mocker: MockerFixture
) -> None:
    animals = (
        mock_herd["calves"]
        + mock_herd["heiferIs"]
        + mock_herd["heiferIIs"]
        + mock_herd["heiferIIIs"]
        + mock_herd["dry_cows"]
        + mock_herd["lac_cows"]
    )
    herd_manager.animal_to_pen_id_map = {
        animal.id: herd_manager.pens_by_animal_combination[
            herd_manager.ANIMAL_GROUPING_SCENARIO.find_animal_combination(animal)
        ][0].id
        for animal in animals
    }
    mock_update_pen_history_by_animal_id = {
        animal.id: mocker.patch.object(animal, "update_pen_history") for animal in animals
    }

    for animals in [
        herd_manager.calves,
        herd_manager.heiferIs,
        herd_manager.heiferIIs,
        herd_manager.heiferIIIs,
        herd_manager.cows,
    ]:
        herd_manager._gather_pen_history(animals, simulation_day=10)
        for animal in animals:
            mock_update_pen_history_by_animal_id[animal.id].assert_called_once()


def test_record_pen_history(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    mock_gather_pen_history = mocker.patch.object(herd_manager, "_gather_pen_history")

    herd_manager.record_pen_history(simulation_day=10)

    assert mock_gather_pen_history.call_args_list == [
        call(herd_manager.calves, 10),
        call(herd_manager.heiferIs, 10),
        call(herd_manager.heiferIIs, 10),
        call(herd_manager.heiferIIIs, 10),
        call(herd_manager.cows, 10),
    ]


def test_clear_pens(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    mock_clear_pen = mocker.patch("RUFAS.biophysical.animal.pen.Pen.clear")

    herd_manager.clear_pens()
    assert mock_clear_pen.call_args_list == [call() for _ in range(len(herd_manager.all_pens))]

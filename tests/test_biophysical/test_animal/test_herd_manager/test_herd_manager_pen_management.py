from datetime import datetime
from typing import Any
from unittest.mock import call, MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID, TotalInventory, Feed
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.rufas_time import RufasTime
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
from tests.test_biophysical.test_animal.test_herd_manager.pytest_fixtures import (
    config_json,
    animal_json,
    feed_json,
    mock_get_data_side_effect,
    mock_herd_manager,
    mock_herd,
    herd_manager,
    mock_pen,
    mock_animal,
)

assert config_json is not None
assert animal_json is not None
assert feed_json is not None
assert mock_get_data_side_effect is not None
assert herd_manager is not None
assert mock_herd is not None


def test_initialize_pens(
    animal_json: dict[str, Any],
    mock_get_data_side_effect: list[Any],
    mocker: MockerFixture,
) -> None:
    """Unit test for initialize_pens()"""
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


def test_allocate_animals_to_pens(
    herd_manager: HerdManager, mocker: MockerFixture, mock_herd: dict[str, list[Animal]]
) -> None:
    """Unit test for allocate_animals_to_pens()"""
    mock_allocate_animals_to_pens_helper = mocker.patch.object(herd_manager, "_allocate_animals_to_pens_helper")
    mock_fully_update_animal_to_pen_id_map = mocker.patch.object(herd_manager, "fully_update_animal_to_pen_id_map")
    mock_time = mocker.MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 15

    herd_manager.allocate_animals_to_pens(mock_time.simulation_day)

    assert mock_allocate_animals_to_pens_helper.call_args_list == [
        call(
            mock_herd["calves"],
            herd_manager.pens_by_animal_combination[AnimalCombination.CALF],
        ),
        call(
            mock_herd["heiferIs"] + mock_herd["heiferIIs"],
            herd_manager.pens_by_animal_combination[AnimalCombination.GROWING],
        ),
        call(
            mock_herd["heiferIIIs"] + mock_herd["dry_cows"],
            herd_manager.pens_by_animal_combination[AnimalCombination.CLOSE_UP],
        ),
        call(
            mock_herd["lac_cows"],
            herd_manager.pens_by_animal_combination[AnimalCombination.LAC_COW],
        ),
    ]
    mock_fully_update_animal_to_pen_id_map.assert_called_once()


@pytest.mark.parametrize(
    "num_animals, max_spaces_in_pens, expected_num_animals_in_pens",
    [
        (90, [50, 30, 20], [45, 27, 18]),
        (70, [50, 30, 20], [35, 21, 14]),
        (47, [50, 30, 20], [22, 15, 10]),
        # No animals at all
        (0, [10, 10, 10], [0, 0, 0]),
        # Single pen with enough space
        (15, [20], [15]),
        # Single pen with exact space
        (10, [10], [10]),
        # Smaller number of animals than total spaces
        (30, [50, 10], [25, 5]),
        # Exactly full scenario
        (60, [20, 20, 20], [20, 20, 20]),
        # A scenario with fractional pen limits
        (25, [10, 10, 10], [9, 9, 7]),
        # Scenario with overstocking
        (100, [45, 25, 15], [52, 30, 18]),
    ],
)
def test_plan_animal_allocation(
    num_animals: int,
    max_spaces_in_pens: list[int],
    expected_num_animals_in_pens: list[int],
    herd_manager: HerdManager,
) -> None:
    """Unit test for _plan_animal_allocation()"""
    result = herd_manager._plan_animal_allocation(num_animals, max_spaces_in_pens)
    assert result == expected_num_animals_in_pens


@pytest.mark.parametrize(
    "allocation_plan, total_animals_to_allocate, total_number_of_pens, animal_type_to_allocate, value_error_expected",
    [
        ([35, 21, 14], 70, 3, AnimalType.CALF, False),
        ([35, 21, 14], 70, 2, AnimalType.CALF, True),
        ([35, 21, 14], 70, 4, AnimalType.CALF, True),
        ([0, 0, 0], 0, 0, AnimalType.LAC_COW, True),
        ([10], 10, 1, AnimalType.HEIFER_II, False),
        ([5, 5], 9, 2, AnimalType.HEIFER_III, True),
        ([5, 5], 11, 2, AnimalType.HEIFER_III, True),
        ([2, 3, 5], 10, 3, AnimalType.DRY_COW, False),
        ([0, 0, 5], 5, 3, AnimalType.DRY_COW, False),
    ],
)
def test_execute_allocation_plan(
    allocation_plan: list[int],
    total_animals_to_allocate: int,
    total_number_of_pens: int,
    animal_type_to_allocate: AnimalType,
    value_error_expected: bool,
    herd_manager: HerdManager,
) -> None:
    """Unit test for _execute_allocation_plan()"""
    animals: list[Animal] = []
    pens: list[Pen] = []
    if total_animals_to_allocate > 0:
        animals = [mock_animal(animal_type_to_allocate, id=i) for i in range(total_animals_to_allocate)]
        pens = [
            mock_pen(
                pen_id=i, animal_combination=herd_manager.ANIMAL_GROUPING_SCENARIO.find_animal_combination(animals[0])
            )
            for i in range(total_number_of_pens)
        ]

    if value_error_expected:
        with pytest.raises(ValueError):
            herd_manager._execute_allocation_plan(allocation_plan, animals, pens)
    else:
        expected_animals_in_pen_by_id: dict[int, dict[int, Animal]] = {}
        current_i = 0
        for i, pen in enumerate(pens):
            next_i = current_i + allocation_plan[i]
            expected_animals_in_pen_by_id[pen.id] = {animal.id: animal for animal in animals[current_i:next_i]}
            current_i = next_i

        herd_manager._execute_allocation_plan(allocation_plan, animals, pens)
        for pen in pens:
            assert pen.animals_in_pen == expected_animals_in_pen_by_id[pen.id]


def test_remove_animal_from_pen_and_id_map(
    herd_manager: HerdManager, mocker: MockerFixture, mock_herd: dict[str, list[Animal]]
) -> None:
    """Unit test for animal_to_pen_id_map()"""
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
    """Unit test for _add_animal_to_pen_and_id_map()"""
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

    mock_feed = MagicMock(auto_spec=Feed)
    for animal in animals:
        herd_manager._add_animal_to_pen_and_id_map(
            animal, mock_feed, mock_current_day_conditions, TotalInventory({}, datetime.today().date()), 15
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


def test_add_animal_to_pen_and_id_map_with_empty_pen(
    herd_manager: HerdManager, mocker: MockerFixture, mock_herd: dict[str, list[Animal]]
) -> None:
    """Unit test for _add_animal_to_pen_and_id_map() when adding to an empty pen"""
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

    mock_feed = MagicMock(auto_spec=Feed)
    total_inventory = TotalInventory({}, datetime.today().date())

    for animal in animals:
        herd_manager.animal_to_pen_id_map = {}
        animal_combination = herd_manager.ANIMAL_GROUPING_SCENARIO.find_animal_combination(animal)
        pen_with_min_stocking_density = min(
            herd_manager.pens_by_animal_combination[animal_combination],
            key=lambda p: p.current_stocking_density,
        )
        pen_with_min_stocking_density.clear()

        mock_pen_insert_animal_into_animals_in_pen_map = mocker.patch.object(
            pen_with_min_stocking_density, "insert_single_animal_into_animals_in_pen_map"
        )
        mock_pen_set_animal_nutritional_requirements = mocker.patch.object(
            pen_with_min_stocking_density, "set_animal_nutritional_requirements"
        )
        mock_reformulate_ration_single_pen = mocker.patch.object(herd_manager, "_reformulate_ration_single_pen")

        mock_udr_key = mocker.MagicMock()
        mocker.patch.object(RationManager, "get_user_defined_ration_feeds", return_value=mock_udr_key)

        mock_pen_avail_feeds = mocker.MagicMock()
        mocker.patch.object(herd_manager, "_find_pen_available_feeds", return_value=mock_pen_avail_feeds)

        herd_manager._add_animal_to_pen_and_id_map(animal, mock_feed, mock_current_day_conditions, total_inventory, 15)

        mock_pen_insert_animal_into_animals_in_pen_map.assert_called_with(animal)
        mock_pen_set_animal_nutritional_requirements.assert_called_with(
            temperature=mock_current_day_conditions.mean_air_temperature, available_feeds=mock_feed
        )
        mock_reformulate_ration_single_pen.assert_called_with(
            pen=pen_with_min_stocking_density,
            pen_available_feeds=mock_pen_avail_feeds,
            current_temperature=mock_current_day_conditions.mean_air_temperature,
            total_inventory=total_inventory,
            simulation_day=15,
        )
        assert animal.id in herd_manager.animal_to_pen_id_map
        assert herd_manager.animal_to_pen_id_map[animal.id] == pen_with_min_stocking_density.id


def test_add_animal_to_pen_and_id_map_uses_default_ration_feeds_when_not_user_defined(
    herd_manager: HerdManager, mocker: MockerFixture, mock_herd: dict[str, list[Animal]]
) -> None:
    """When ration is not user-defined, _add_animal_to_pen_and_id_map should use RationManager.ration_feeds."""
    mock_current_day_conditions = MagicMock(auto_spec=CurrentDayConditions)
    animal = mock_herd["calves"][0]

    herd_manager.animal_to_pen_id_map = {}
    herd_manager.is_ration_defined_by_user = False
    mock_feed = MagicMock(auto_spec=Feed)
    available_feeds: list[Feed] = [mock_feed]
    total_inventory = TotalInventory({}, datetime.today().date())

    animal_combination = herd_manager.ANIMAL_GROUPING_SCENARIO.find_animal_combination(animal)
    pen_with_min_stocking_density: Pen = min(
        herd_manager.pens_by_animal_combination[animal_combination],
        key=lambda p: p.current_stocking_density,
    )
    pen_with_min_stocking_density.clear()

    mocker.patch.object(pen_with_min_stocking_density, "insert_single_animal_into_animals_in_pen_map")
    mocker.patch.object(pen_with_min_stocking_density, "set_animal_nutritional_requirements")
    mock_reformulate_ration_single_pen = mocker.patch.object(herd_manager, "_reformulate_ration_single_pen")

    mock_ration_feeds = mocker.MagicMock(name="ration_feeds")
    mocker.patch.object(RationManager, "ration_feeds", mock_ration_feeds, create=True)

    mock_pen_avail_feeds = mocker.MagicMock()
    mock_find_pen_available_feeds = mocker.patch.object(
        herd_manager, "_find_pen_available_feeds", return_value=mock_pen_avail_feeds
    )

    herd_manager._add_animal_to_pen_and_id_map(
        animal=animal,
        available_feeds=available_feeds,
        current_day_conditions=mock_current_day_conditions,
        total_inventory=total_inventory,
        simulation_day=15,
    )

    mock_find_pen_available_feeds.assert_called_once_with(available_feeds, mock_ration_feeds)

    mock_reformulate_ration_single_pen.assert_called_once_with(
        pen=pen_with_min_stocking_density,
        pen_available_feeds=mock_pen_avail_feeds,
        current_temperature=mock_current_day_conditions.mean_air_temperature,
        total_inventory=total_inventory,
        simulation_day=15,
    )

    assert herd_manager.animal_to_pen_id_map[animal.id] == pen_with_min_stocking_density.id


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
    herd_manager: HerdManager,
) -> None:
    """Unit test for _calculate_max_animal_spaces_per_pen()"""
    if raise_value_error:
        with pytest.raises(ValueError):
            herd_manager._calculate_max_animal_spaces_per_pen(num_stalls, max_stocking_density)
    else:
        result = herd_manager._calculate_max_animal_spaces_per_pen(num_stalls, max_stocking_density)
        assert result == expected


@pytest.mark.parametrize(
    "number_of_animals, animal_type, number_of_pens, animal_combination",
    [
        (100, AnimalType.CALF, 3, AnimalCombination.CALF),
        (100, AnimalType.HEIFER_I, 3, AnimalCombination.GROWING),
        (100, AnimalType.HEIFER_II, 5, AnimalCombination.GROWING),
        (10, AnimalType.HEIFER_III, 1, AnimalCombination.CLOSE_UP),
        (100, AnimalType.DRY_COW, 3, AnimalCombination.CLOSE_UP),
        (100, AnimalType.LAC_COW, 3, AnimalCombination.LAC_COW),
    ],
)
def test_allocate_animals_to_pens_helper(
    number_of_animals: int,
    animal_type: AnimalType,
    number_of_pens: int,
    animal_combination: AnimalCombination,
    herd_manager: HerdManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for _allocate_animals_to_pens_helper()"""
    dummy_allocation_plan = [2, 3, 3]

    mock_plan_animal_allocation = mocker.patch.object(
        herd_manager, "_plan_animal_allocation", return_value=dummy_allocation_plan
    )
    mock_execute_allocation_plan = mocker.patch.object(herd_manager, "_execute_allocation_plan")
    mock_calculate_max_animal_spaces_per_pen = mocker.patch.object(
        herd_manager, "_calculate_max_animal_spaces_per_pen", return_value=10
    )

    dummy_animals = [mock_animal(animal_type=animal_type) for _ in range(number_of_animals)]
    dummy_pens = [mock_pen(pen_id=i, animal_combination=animal_combination) for i in range(number_of_pens)]

    herd_manager._allocate_animals_to_pens_helper(dummy_animals, dummy_pens)

    assert mock_calculate_max_animal_spaces_per_pen.call_count == number_of_pens
    mock_plan_animal_allocation.assert_called_once_with(
        num_animals=number_of_animals,
        max_spaces_in_pens=[10] * number_of_pens,
    )
    mock_execute_allocation_plan.assert_called_once_with(
        allocation_plan=dummy_allocation_plan, animals=dummy_animals, animal_pens=dummy_pens
    )


def test_fully_update_animal_to_pen_id_map(
    herd_manager: HerdManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for fully_update_animal_to_pen_id_map()"""
    expected_animal_to_pen_id_map = {
        0: 0,
        1: 0,
        2: 0,
        3: 1,
        4: 1,
        5: 1,
        6: 1,
        7: 1,
        8: 1,
        9: 2,
        10: 2,
        11: 2,
        12: 2,
        13: 2,
        14: 2,
        15: 2,
        16: 3,
        17: 3,
        18: 3,
    }
    mock_time = mocker.MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 15

    herd_manager.animal_to_pen_id_map = {}
    herd_manager.fully_update_animal_to_pen_id_map(mock_time.simulation_day)

    assert herd_manager.animal_to_pen_id_map == expected_animal_to_pen_id_map


def test_fully_update_animal_to_pen_id_map_warns_if_pen_is_overstocked(
    herd_manager: HerdManager,
    mocker: MockerFixture,
) -> None:
    """Test that a warning is logged if a pen is overstocked during animal-to-pen ID map update."""
    mock_time = mocker.MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 15

    mock_add_warning = mocker.patch.object(herd_manager.om, "add_warning")

    overstocked_pen = mocker.MagicMock()
    overstocked_pen.id = 99
    overstocked_pen.animals_in_pen = [100, 101]
    overstocked_pen.current_stocking_density = 2.5
    overstocked_pen.max_stocking_density = 2.0
    overstocked_pen.num_stalls = 1

    normal_pen = mocker.MagicMock()
    normal_pen.id = 88
    normal_pen.animals_in_pen = [200]
    normal_pen.current_stocking_density = 1.0
    normal_pen.max_stocking_density = 2.0

    herd_manager.all_pens = [overstocked_pen, normal_pen]
    herd_manager.animal_to_pen_id_map = {}

    mocker.patch.object(herd_manager, "_calculate_max_animal_spaces_per_pen", return_value=2)

    herd_manager.fully_update_animal_to_pen_id_map(mock_time.simulation_day)

    assert herd_manager.animal_to_pen_id_map == {
        100: 99,
        101: 99,
        200: 88,
    }

    mock_add_warning.assert_called_once()
    args, kwargs = mock_add_warning.call_args
    assert "overstocked" in args[0].lower()
    assert "Pen 99" in args[1]
    assert kwargs["info_map"]["function"] == "fully_update_animal_to_pen_id_map"
    assert kwargs["info_map"]["simulation_day"] == 15


@pytest.mark.parametrize(
    "all_feed_ids, user_defined_ids, expected_ids",
    [
        # 1. Single match
        ([1, 2], [1], [1]),
        # 2. No matches
        ([1, 2], [3], []),
        # 3. Multiple matches (order should be preserved from all_available_feeds)
        ([1, 2, 3], [3, 1], [1, 3]),
        # 4. Both lists empty
        ([], [], []),
        # 5. user_defined_ids empty → always returns []
        ([1], [], []),
    ],
)
def test_find_pen_available_feeds(
    all_feed_ids: list[int],
    user_defined_ids: list[int],
    expected_ids: list[int],
    herd_manager: HerdManager,
    mocker: MockerFixture,
) -> None:
    """Tests for _find_pen_available_feeds filtering behavior."""
    all_available_feeds = []
    for feed_id in all_feed_ids:
        feed = mocker.MagicMock(spec=Feed)
        feed.rufas_id = RUFAS_ID(feed_id)
        all_available_feeds.append(feed)

    user_defined_ration_feed_ids = [RUFAS_ID(feed_id) for feed_id in user_defined_ids]

    result = herd_manager._find_pen_available_feeds(
        all_available_feeds=all_available_feeds,
        user_defined_ration_feed_ids=user_defined_ration_feed_ids,
    )

    assert [feed.rufas_id for feed in result] == expected_ids


def test_gather_pen_history(
    herd_manager: HerdManager, mock_herd: dict[str, list[Animal]], mocker: MockerFixture
) -> None:
    """Unit test for _gather_pen_history()"""
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
    """Unit test for record_pen_history()"""
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
    """Unit test for clear_pens()"""
    mock_clear_pen = mocker.patch("RUFAS.biophysical.animal.pen.Pen.clear")

    herd_manager.clear_pens()
    assert mock_clear_pen.call_args_list == [call() for _ in range(len(herd_manager.all_pens))]

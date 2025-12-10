from datetime import datetime
from random import shuffle, randint
from typing import Any
from unittest.mock import call, MagicMock, PropertyMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.bedding.bedding import Bedding
from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus, Breed
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_population import AnimalPopulation
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import NewBornCalfValuesTypedDict
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput
from RUFAS.biophysical.animal.data_types.reproduction import HerdReproductionStatistics
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.feed_storage_to_animal_connection import Feed, TotalInventory
from RUFAS.rufas_time import RufasTime
from RUFAS.weather import Weather

from tests.test_biophysical.test_animal.test_herd_manager.pytest_fixtures import (
    config_json,
    animal_json,
    feed_json,
    mock_get_data_side_effect,
    mock_herd,
    mock_animal,
    herd_manager,
    mock_herd_manager,
)

assert config_json is not None
assert animal_json is not None
assert feed_json is not None
assert mock_get_data_side_effect is not None
assert herd_manager is not None
assert mock_herd is not None


def test_reset_daily_statistics(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    """Unit test for _reset_daily_statistics()"""
    mock_reset_daily_stats = mocker.patch.object(herd_manager.herd_statistics, "reset_daily_stats")
    mock_reset_parity = mocker.patch.object(herd_manager.herd_statistics, "reset_parity")
    mock_reset_cull_reason_stats = mocker.patch.object(herd_manager.herd_statistics, "reset_cull_reason_stats")

    herd_manager._reset_daily_statistics()

    mock_reset_daily_stats.assert_called_once_with()
    mock_reset_parity.assert_called_once_with()
    mock_reset_cull_reason_stats.assert_called_once_with()


def test_update_sold_animal_statistics(
    herd_manager: HerdManager, mock_herd: dict[str, list[Animal]], mocker: MockerFixture
) -> None:
    """Unit test for _update_sold_animal_statistics()"""
    mock_update_sold_and_died_cows = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._update_sold_and_died_cow_statistics"
    )
    mock_update_sold_heiferIIs = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._update_sold_heiferII_statistics"
    )
    mock_update_sold_newborn_calves = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._update_sold_newborn_calf_statistics"
    )

    sold_newborn_calves = mock_herd["calves"]
    sold_heiferIIs = mock_herd["heiferIIs"]
    sold_and_died_cows = mock_herd["lac_cows"]

    herd_manager._update_sold_animal_statistics(
        sold_newborn_calves=sold_newborn_calves, sold_heiferIIs=sold_heiferIIs, sold_and_died_cows=sold_and_died_cows
    )

    mock_update_sold_newborn_calves.assert_called_once_with(sold_newborn_calves)
    mock_update_sold_heiferIIs.assert_called_once_with(sold_heiferIIs)
    mock_update_sold_and_died_cows.assert_called_once_with(sold_and_died_cows)


@pytest.mark.parametrize(
    "animal_type, number_of_animals, newborn_calves_expected, "
    "expected_number_of_graduated_animals, expected_number_of_sold_animals, "
    "expected_number_of_sold_newborn_calves, expected_number_of_newborn_calves",
    [
        (AnimalType.CALF, 10, False, 3, 0, 0, 0),
        (AnimalType.CALF, 10, False, 10, 0, 0, 0),
        (AnimalType.CALF, 10, False, 0, 0, 0, 0),
        (AnimalType.HEIFER_I, 10, False, 3, 0, 0, 0),
        (AnimalType.HEIFER_I, 10, False, 10, 0, 0, 0),
        (AnimalType.HEIFER_I, 10, False, 0, 0, 0, 0),
        (AnimalType.HEIFER_II, 10, False, 3, 1, 0, 0),
        (AnimalType.HEIFER_II, 10, False, 9, 1, 0, 0),
        (AnimalType.HEIFER_II, 10, False, 10, 0, 0, 0),
        (AnimalType.HEIFER_II, 10, False, 0, 0, 0, 0),
        (AnimalType.HEIFER_II, 10, False, 0, 10, 0, 0),
        (AnimalType.HEIFER_III, 10, False, 0, 0, 0, 0),
        (AnimalType.HEIFER_III, 10, True, 3, 0, 2, 1),
        (AnimalType.HEIFER_III, 10, True, 10, 0, 8, 2),
        (AnimalType.HEIFER_III, 10, True, 8, 0, 8, 0),
        (AnimalType.HEIFER_III, 10, True, 8, 0, 0, 8),
        (AnimalType.LAC_COW, 10, False, 3, 1, 0, 0),
        (AnimalType.LAC_COW, 10, False, 2, 0, 0, 0),
        (AnimalType.LAC_COW, 10, False, 0, 2, 0, 0),
        (AnimalType.LAC_COW, 10, False, 0, 0, 0, 0),
        (AnimalType.DRY_COW, 10, True, 3, 1, 3, 0),
        (AnimalType.DRY_COW, 10, True, 3, 1, 2, 1),
        (AnimalType.DRY_COW, 10, False, 0, 1, 0, 0),
        (AnimalType.DRY_COW, 10, False, 0, 0, 0, 0),
        (AnimalType.DRY_COW, 10, True, 10, 0, 8, 2),
        (AnimalType.DRY_COW, 10, True, 10, 0, 10, 0),
    ],
)
def test_perform_daily_routines_for_animals(
    animal_type: AnimalType,
    number_of_animals: int,
    newborn_calves_expected: bool,
    expected_number_of_graduated_animals: int,
    expected_number_of_sold_animals: int,
    expected_number_of_sold_newborn_calves: int,
    expected_number_of_newborn_calves: int,
    herd_manager: HerdManager,
    mock_herd: dict[str, list[Animal]],
    mocker: MockerFixture,
) -> None:
    """Unit test for _perform_daily_routines_for_animals()"""
    (
        expected_graduated_animals,
        expected_sold_animals,
        expected_sold_newborn_calves,
        expected_newborn_calves,
    ) = ([], [], [], [])
    animals = [mock_animal(animal_type) for _ in range(number_of_animals)]
    for _ in range(expected_number_of_graduated_animals):
        animal = animals.pop(0)
        if animal_type in [AnimalType.HEIFER_III, AnimalType.DRY_COW] and newborn_calves_expected:
            mocker.patch.object(
                animal,
                "daily_routines",
                return_value=DailyRoutinesOutput(
                    animal_status=AnimalStatus.LIFE_STAGE_CHANGED,
                    newborn_calf_config=NewBornCalfValuesTypedDict(
                        breed=Breed.HO.name,
                        animal_type=AnimalType.CALF.value,
                        birth_date="",
                        days_born=0,
                        birth_weight=10.1,
                        initial_phosphorus=10.0,
                        net_merit=18.8,
                    ),
                    herd_reproduction_statistics=HerdReproductionStatistics(),
                ),
            )
        else:
            mocker.patch.object(
                animal,
                "daily_routines",
                return_value=DailyRoutinesOutput(
                    animal_status=AnimalStatus.LIFE_STAGE_CHANGED,
                    herd_reproduction_statistics=HerdReproductionStatistics(),
                ),
            )
        expected_graduated_animals.append(animal)
    for _ in range(expected_number_of_sold_animals):
        animal = animals.pop(0)
        mocker.patch.object(
            animal,
            "daily_routines",
            return_value=DailyRoutinesOutput(
                animal_status=AnimalStatus.SOLD, herd_reproduction_statistics=HerdReproductionStatistics()
            ),
        )
        expected_sold_animals.append(animal)
    for animal in animals:
        mocker.patch.object(
            animal,
            "daily_routines",
            return_value=DailyRoutinesOutput(
                animal_status=AnimalStatus.REMAIN, herd_reproduction_statistics=HerdReproductionStatistics()
            ),
        )

    animals = animals + expected_graduated_animals + expected_sold_animals
    shuffle(animals)

    create_newborn_calf_side_effect = []
    if newborn_calves_expected:
        expected_sold_newborn_calves = [
            mock_animal(AnimalType.CALF, sold=True) for _ in range(expected_number_of_sold_newborn_calves)
        ]
        expected_newborn_calves = [
            mock_animal(AnimalType.CALF, sold=False) for _ in range(expected_number_of_newborn_calves)
        ]
        create_newborn_calf_side_effect = expected_sold_newborn_calves + expected_newborn_calves
        shuffle(create_newborn_calf_side_effect)
    mock_create_newborn_calf = mocker.patch.object(
        herd_manager, "_create_newborn_calf", side_effect=create_newborn_calf_side_effect
    )

    mock_time = MagicMock(auto_spec=RufasTime)
    (
        actual_graduated_animals,
        actual_sold_animal,
        actual_stillborn_newborn_calves,
        actual_newborn_calves,
        actual_sold_newborn_calves,
    ) = herd_manager._perform_daily_routines_for_animals(mock_time, animals)

    assert set(actual_graduated_animals) == set(expected_graduated_animals)
    assert set(actual_sold_animal) == set(expected_sold_animals)
    assert set(actual_sold_newborn_calves) == set(expected_sold_newborn_calves)
    assert set(actual_newborn_calves) == set(expected_newborn_calves)
    assert len(actual_graduated_animals) == len(expected_graduated_animals)
    assert len(actual_sold_animal) == len(expected_sold_animals)
    assert len(actual_newborn_calves) == len(expected_newborn_calves)
    assert len(actual_sold_newborn_calves) == len(expected_sold_newborn_calves)
    if newborn_calves_expected:
        assert (
            mock_create_newborn_calf.call_count
            == expected_number_of_newborn_calves + expected_number_of_sold_newborn_calves
        )
    else:
        mock_create_newborn_calf.assert_not_called()


def test_perform_daily_routines_counts_deaths_and_handles_stillborn_newborns(
    herd_manager: HerdManager,
    mocker: MockerFixture,
) -> None:
    """Covers:
    - animal_status == DEAD increments herd_statistics.animals_deaths_by_stage
    - DEAD also adds the animal to sold_animals
    - newborn_calf.stillborn goes into stillborn_newborn_calves
    """
    dead_animal = MagicMock(spec=Animal)
    dead_animal.animal_type = AnimalType.LAC_COW

    dead_output = DailyRoutinesOutput(
        animal_status=AnimalStatus.DEAD,
        newborn_calf_config=None,
        herd_reproduction_statistics=HerdReproductionStatistics(),
    )
    mocker.patch.object(dead_animal, "daily_routines", return_value=dead_output)

    calving_animal = MagicMock(spec=Animal)
    calving_animal.animal_type = AnimalType.DRY_COW

    newborn_config: NewBornCalfValuesTypedDict = {
        "breed": Breed.HO.name,
        "animal_type": AnimalType.CALF.value,
        "birth_date": "",
        "days_born": 0,
        "birth_weight": 10.1,
        "initial_phosphorus": 10.0,
        "net_merit": 18.8,
    }

    calving_output = DailyRoutinesOutput(
        animal_status=AnimalStatus.LIFE_STAGE_CHANGED,
        newborn_calf_config=newborn_config,
        herd_reproduction_statistics=HerdReproductionStatistics(),
    )
    mocker.patch.object(calving_animal, "daily_routines", return_value=calving_output)

    stillborn_calf = MagicMock(spec=Animal)
    stillborn_calf.stillborn = True
    stillborn_calf.sold = False

    mock_create_newborn_calf = mocker.patch.object(
        herd_manager,
        "_create_newborn_calf",
        return_value=stillborn_calf,
    )

    before_deaths = herd_manager.herd_statistics.animals_deaths_by_stage[AnimalType.LAC_COW]

    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = 0

    (
        graduated_animals,
        sold_animals,
        stillborn_newborn_calves,
        newborn_calves,
        sold_newborn_calves,
    ) = herd_manager._perform_daily_routines_for_animals(
        time=mock_time,
        animals=[dead_animal, calving_animal],
    )

    assert herd_manager.herd_statistics.animals_deaths_by_stage[AnimalType.LAC_COW] == before_deaths + 1
    assert sold_animals == [dead_animal]
    assert graduated_animals == [calving_animal]
    mock_create_newborn_calf.assert_called_once()
    assert stillborn_newborn_calves == [stillborn_calf]
    assert newborn_calves == []
    assert sold_newborn_calves == []


def test_update_herd_structure(
    herd_manager: HerdManager, mock_herd: dict[str, list[Animal]], mocker: MockerFixture
) -> None:
    """Unit test for the _update_herd_structure() method."""
    mock_available_feeds: list[Feed] = [MagicMock(auto_spec=Feed)]
    mock_current_day_conditions, mock_total_inventory = (
        MagicMock(auto_spec=CurrentDayConditions),
        MagicMock(auto_spec=TotalInventory),
    )

    newborn_calves, graduated_animals, removed_animals, newly_added_animals = (
        mock_herd["calves"],
        mock_herd["heiferIs"],
        mock_herd["heiferIIs"],
        mock_herd["replacement"],
    )

    mock_handle_graduated_animals = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._handle_graduated_animals"
    )
    mock_handle_newly_added_animals = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._handle_newly_added_animals"
    )
    mock_remove_animal_from_pen_and_id_map = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._remove_animal_from_pen_and_id_map"
    )

    herd_manager._update_herd_structure(
        graduated_animals=graduated_animals,
        newborn_calves=newborn_calves,
        removed_animals=removed_animals,
        newly_added_animals=newly_added_animals,
        available_feeds=mock_available_feeds,
        current_day_conditions=mock_current_day_conditions,
        total_inventory=mock_total_inventory,
        simulation_day=15,
    )

    mock_handle_graduated_animals.assert_called_once_with(
        graduated_animals, mock_available_feeds, mock_current_day_conditions, mock_total_inventory, 15
    )
    assert mock_handle_newly_added_animals.call_args_list == [
        call(newborn_calves, mock_available_feeds, mock_current_day_conditions, mock_total_inventory, 15),
        call(newly_added_animals, mock_available_feeds, mock_current_day_conditions, mock_total_inventory, 15),
    ]
    assert mock_remove_animal_from_pen_and_id_map.call_args_list == [call(animal) for animal in removed_animals]


def test_daily_routines(herd_manager: HerdManager, mock_herd: dict[str, list[Animal]], mocker: MockerFixture) -> None:
    """Unit test for daily_routines()"""
    mock_feed = MagicMock(auto_spec=Feed)
    mock_weather = MagicMock(auto_spec=Weather)
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 15
    mock_total_inventory = MagicMock(auto_spec=TotalInventory)

    mocker.patch.object(HerdManager, "average_herd_305_days_milk_production", new_callable=PropertyMock)

    graduated_calves, graduated_heiferIs, graduated_heiferIIs, graduated_heiferIIIs, graduated_cows = (
        mock_herd["heiferIs"],
        mock_herd["heiferIIs"],
        mock_herd["heiferIIIs"],
        mock_herd["lac_cows"],
        mock_herd["dry_cows"],
    )
    sold_calves, sold_heiferIs, sold_heiferIIs, sold_heiferIIIs, sold_and_died_cows = (
        [mock_animal(AnimalType.CALF, sold=True) for _ in range(2)],
        [mock_animal(AnimalType.HEIFER_I, sold=True) for _ in range(2)],
        [mock_animal(AnimalType.HEIFER_II, sold=True) for _ in range(2)],
        [mock_animal(AnimalType.HEIFER_III, sold=True) for _ in range(2)],
        [mock_animal(AnimalType.LAC_COW, sold=True) for _ in range(2)],
    )
    heiferIII_newborn_calves, heiferIII_sold_newborn_calves, cow_newborn_calves, cow_sold_newborn_calves = (
        [mock_animal(AnimalType.CALF, sold=False) for _ in range(2)],
        [mock_animal(AnimalType.CALF, sold=True) for _ in range(2)],
        [mock_animal(AnimalType.CALF, sold=False) for _ in range(2)],
        [mock_animal(AnimalType.CALF, sold=True) for _ in range(2)],
    )
    sold_oversupply_heiferIIIs = [mock_animal(AnimalType.HEIFER_III, sold=True) for _ in range(5)]
    bought_replacement_heiferIIIs = [mock_animal(AnimalType.HEIFER_III, sold=False) for _ in range(5)]

    graduated_animals = (
        graduated_calves + graduated_heiferIs + graduated_heiferIIs + graduated_heiferIIIs + graduated_cows
    )
    newborn_calves = heiferIII_newborn_calves + cow_newborn_calves
    removed_animals = (
        sold_calves + sold_heiferIs + sold_heiferIIs + sold_heiferIIIs + sold_and_died_cows + sold_oversupply_heiferIIIs
    )

    mock_perform_daily_routines_for_animals_side_effect: list[
        tuple[list[Animal], list[Animal], list[Animal], list[Animal], list[Animal]]
    ] = [
        (graduated_calves, sold_calves, [], [], []),
        (graduated_heiferIs, sold_heiferIs, [], [], []),
        (graduated_heiferIIs, sold_heiferIIs, [], [], []),
        (graduated_heiferIIIs, sold_heiferIIIs, heiferIII_sold_newborn_calves, heiferIII_newborn_calves, []),
        (graduated_cows, sold_and_died_cows, cow_sold_newborn_calves, cow_newborn_calves, []),
    ]

    mock_reset_daily_statistics = mocker.patch.object(herd_manager, "_reset_daily_statistics")
    mock_perform_daily_routines_for_animals = mocker.patch.object(
        herd_manager,
        "_perform_daily_routines_for_animals",
        side_effect=mock_perform_daily_routines_for_animals_side_effect,
    )
    mock_update_sold_animal_statistics = mocker.patch.object(herd_manager, "_update_sold_animal_statistics")
    mock_check_if_heifers_need_to_be_sold = mocker.patch.object(
        herd_manager, "_check_if_heifers_need_to_be_sold", return_value=sold_oversupply_heiferIIIs
    )
    mock_check_if_replacement_heifers_needed = mocker.patch.object(
        herd_manager, "_check_if_replacement_heifers_needed", return_value=bought_replacement_heiferIIIs
    )
    mock_update_herd_structure = mocker.patch.object(herd_manager, "_update_herd_structure")
    mock_record_pen_history = mocker.patch.object(herd_manager, "record_pen_history")
    mock_update_herd_statistics = mocker.patch.object(herd_manager, "update_herd_statistics")
    mock_report_manure_streams = mocker.patch(
        "RUFAS.biophysical.animal.animal_module_reporter.AnimalModuleReporter.report_manure_streams"
    )
    mock_report_manure_excretions = mocker.patch(
        "RUFAS.biophysical.animal.animal_module_reporter.AnimalModuleReporter.report_manure_excretions"
    )
    mock_report_milk = mocker.patch("RUFAS.biophysical.animal.animal_module_reporter.AnimalModuleReporter.report_milk")
    mock_report_305d_milk = mocker.patch(
        "RUFAS.biophysical.animal.animal_module_reporter.AnimalModuleReporter.report_305d_milk"
    )
    mock_report_ration = mocker.patch.object(herd_manager, "_report_ration")

    for pen in herd_manager.all_pens:
        pen.manure_streams = [
            {
                "stream_name": "single_general_stream",
                "stream_proportion": 1.0,
                "first_processor": "mock_processor",
                "bedding_name": "mock_bedding",
            }
        ]
        pen.beddings = {"mock_bedding": MagicMock(auto_spec=Bedding)}

    herd_manager.daily_routines([mock_feed], mock_time, mock_weather, mock_total_inventory)

    mock_reset_daily_statistics.assert_called_once_with()
    assert mock_perform_daily_routines_for_animals.call_count == 5
    assert mock_perform_daily_routines_for_animals.call_args_list == [
        call(mock_time, herd_manager.calves),
        call(mock_time, herd_manager.heiferIs),
        call(mock_time, herd_manager.heiferIIs),
        call(mock_time, herd_manager.heiferIIIs),
        call(mock_time, herd_manager.cows),
    ]
    mock_update_sold_animal_statistics.assert_called_once_with(
        sold_newborn_calves=[], sold_heiferIIs=sold_heiferIIs, sold_and_died_cows=sold_and_died_cows
    )
    mock_check_if_heifers_need_to_be_sold.assert_called_once_with(simulation_day=mock_time.simulation_day)
    mock_check_if_replacement_heifers_needed.assert_called_once_with(time=mock_time)
    mock_update_herd_structure.assert_called_once_with(
        graduated_animals=graduated_animals,
        newborn_calves=newborn_calves,
        newly_added_animals=bought_replacement_heiferIIIs,
        removed_animals=removed_animals,
        available_feeds=[mock_feed],
        current_day_conditions=mock_weather.get_current_day_conditions(),
        total_inventory=mock_total_inventory,
        simulation_day=15,
    )
    mock_record_pen_history.assert_called_once_with(mock_time.simulation_day)
    mock_update_herd_statistics.assert_called_once_with()
    mock_report_manure_streams.assert_called_once()
    mock_report_manure_excretions.assert_called_once()
    mock_report_milk.assert_called_once()
    mock_report_305d_milk.assert_called_once()
    mock_report_ration.assert_called_once()


@pytest.mark.parametrize(
    "is_newborn_calf_sold, is_newborn_calf_stillborn", [(False, False), (True, False), (False, True)]
)
def test_create_newborn_calf(
    is_newborn_calf_sold: bool, is_newborn_calf_stillborn: bool, herd_manager: HerdManager, mocker: MockerFixture
) -> None:
    """Unit test for _create_newborn_calf()"""
    AnimalPopulation.set_current_max_animal_id(0)
    newborn_calf_config = NewBornCalfValuesTypedDict(
        breed=Breed.HO.name,
        animal_type=AnimalType.CALF.value,
        birth_date="",
        days_born=0,
        birth_weight=10.1,
        initial_phosphorus=10.0,
        net_merit=18.8,
    )
    animal = mock_animal(animal_type=AnimalType.CALF, sold=is_newborn_calf_sold, stillborn=is_newborn_calf_stillborn)
    animal.events = MagicMock(auto_spec=AnimalEvents)
    animal.events.add_event = MagicMock()

    mock_animal_init = mocker.patch("RUFAS.biophysical.animal.herd_manager.Animal", return_value=animal)

    herd_manager._create_newborn_calf(newborn_calf_config, 0)

    expected_newborn_calf_config = newborn_calf_config.copy()
    expected_newborn_calf_config["id"] = AnimalPopulation.current_animal_id
    mock_animal_init.assert_called_once_with(args=expected_newborn_calf_config, simulation_day=0)

    if not (is_newborn_calf_stillborn or is_newborn_calf_sold):
        animal.events.add_event.assert_called_once()


def test_check_if_heifers_need_to_be_sold(
    mock_get_data_side_effect: list[Any], mocker: MockerFixture, mock_herd: dict[str, list[Animal]]
) -> None:
    """Unit test for _check_if_heifers_need_to_be_sold()"""
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"] * 25,
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect,
    )
    herd_manager.herd_statistics.heiferIII_num, herd_manager.herd_statistics.cow_num = (
        len(herd_manager.heiferIIIs),
        len(herd_manager.cows),
    )

    result = herd_manager._check_if_heifers_need_to_be_sold(simulation_day=0)

    expected_sold_heiferIIIs = mock_herd["heiferIIIs"][::-1][:3]
    expected_sold_heiferIIIs_info = [
        {
            "id": removed_heiferIII.id,
            "animal_type": removed_heiferIII.animal_type.value,
            "sold_at_day": removed_heiferIII.sold_at_day,
            "body_weight": removed_heiferIII.body_weight,
            "cull_reason": "NA",
            "days_in_milk": "NA",
            "parity": "NA",
        }
        for removed_heiferIII in expected_sold_heiferIIIs[:3]
    ]
    assert result == expected_sold_heiferIIIs
    assert herd_manager.herd_statistics.sold_heiferIIIs_info == expected_sold_heiferIIIs_info
    assert herd_manager.herd_statistics.heiferIII_num == 97
    assert herd_manager.herd_statistics.sold_heiferIII_oversupply_num == 3


def test_check_if_replacement_heifers_needed(
    mock_get_data_side_effect: list[Any], mocker: MockerFixture, mock_herd: dict[str, list[Animal]]
) -> None:
    """Unit test for _check_if_replacement_heifers_needed()"""
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"] * 23,
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"] * 2,
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect,
    )
    herd_manager.herd_statistics.heiferIII_num, herd_manager.herd_statistics.cow_num = (
        len(herd_manager.heiferIIIs),
        len(herd_manager.cows),
    )
    herd_manager.herd_statistics.bought_heifer_num = 0

    for replacement in herd_manager.replacement_market:
        replacement.days_born = 10

    mocker.patch(
        "RUFAS.biophysical.animal.animal_genetics.animal_genetics.AnimalGenetics."
        "assign_net_merit_value_to_animals_entering_herd",
        return_vale=8.8,
    )

    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 100
    mock_time.current_date = datetime.today()

    result = herd_manager._check_if_replacement_heifers_needed(mock_time)

    expected_bought_animals = mock_herd["replacement"] * 2

    assert result == expected_bought_animals
    assert herd_manager.herd_statistics.bought_heifer_num == 2


@pytest.mark.parametrize(
    "animal_type_to_remove",
    [
        AnimalType.CALF,
        AnimalType.HEIFER_I,
        AnimalType.HEIFER_II,
        AnimalType.HEIFER_III,
        AnimalType.LAC_COW,
        AnimalType.DRY_COW,
    ],
)
def test_remove_animal_from_current_array(
    animal_type_to_remove: AnimalType,
    mock_herd: dict[str, list[Animal]],
    mocker: MockerFixture,
    mock_get_data_side_effect: list[Any],
) -> None:
    """Unit test for _remove_animal_from_current_array()"""
    herd_manager, _ = mock_herd_manager(
        calves=(mock_herd["calves"]),
        heiferIs=(mock_herd["heiferIs"]),
        heiferIIs=(mock_herd["heiferIIs"]),
        heiferIIIs=(mock_herd["heiferIIIs"]),
        cows=(mock_herd["dry_cows"] + mock_herd["lac_cows"]),
        replacement=(mock_herd["replacement"]),
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect,
    )

    animals_by_animal_type = {
        AnimalType.CALF: mock_herd["calves"],
        AnimalType.HEIFER_I: mock_herd["heiferIs"],
        AnimalType.HEIFER_II: mock_herd["heiferIIs"],
        AnimalType.HEIFER_III: mock_herd["heiferIIIs"],
        AnimalType.LAC_COW: mock_herd["lac_cows"],
        AnimalType.DRY_COW: mock_herd["dry_cows"],
    }
    herd_manager_array_by_animal_type = {
        AnimalType.CALF: "calves",
        AnimalType.HEIFER_I: "heiferIs",
        AnimalType.HEIFER_II: "heiferIIs",
        AnimalType.HEIFER_III: "heiferIIIs",
        AnimalType.LAC_COW: "cows",
        AnimalType.DRY_COW: "cows",
    }

    animals_to_remove = animals_by_animal_type[animal_type_to_remove]
    animal_to_remove = animals_to_remove[randint(0, len(animals_to_remove) - 1)]

    herd_manager._remove_animal_from_current_array(animal_to_remove)

    animals_by_animal_type[animal_type_to_remove].remove(animal_to_remove)

    assert animal_to_remove not in getattr(herd_manager, herd_manager_array_by_animal_type[animal_type_to_remove])
    assert herd_manager.calves == mock_herd["calves"]
    assert herd_manager.heiferIs == mock_herd["heiferIs"]
    assert herd_manager.heiferIIs == mock_herd["heiferIIs"]
    assert herd_manager.heiferIIIs == mock_herd["heiferIIIs"]
    assert herd_manager.cows == mock_herd["dry_cows"] + mock_herd["lac_cows"]


@pytest.mark.parametrize(
    "animal_type_to_add",
    [
        AnimalType.CALF,
        AnimalType.HEIFER_I,
        AnimalType.HEIFER_II,
        AnimalType.HEIFER_III,
        AnimalType.LAC_COW,
        AnimalType.DRY_COW,
    ],
)
def test_add_animal_to_new_array(
    animal_type_to_add: AnimalType,
    herd_manager: HerdManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for _add_animal_to_new_array()"""
    animal_to_add = mock_animal(animal_type=animal_type_to_add)
    herd_manager_array_by_animal_type = {
        AnimalType.CALF: "calves",
        AnimalType.HEIFER_I: "heiferIs",
        AnimalType.HEIFER_II: "heiferIIs",
        AnimalType.HEIFER_III: "heiferIIIs",
        AnimalType.LAC_COW: "cows",
        AnimalType.DRY_COW: "cows",
    }
    other_array_names = set(
        [name for animal_type, name in herd_manager_array_by_animal_type.items() if animal_type != animal_type_to_add]
    )
    if animal_type_to_add.is_cow:
        other_array_names.remove("cows")

    herd_manager._add_animal_to_new_array(animal_to_add)

    assert animal_to_add in getattr(herd_manager, herd_manager_array_by_animal_type[animal_type_to_add])
    for other_array_name in other_array_names:
        assert animal_to_add not in getattr(herd_manager, other_array_name)


def test_update_animal_array(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    """Unit test for _update_animal_array()"""
    mock_remove_animal_from_current_array = mocker.patch.object(herd_manager, "_remove_animal_from_current_array")
    mock_add_animal_to_new_array = mocker.patch.object(herd_manager, "_add_animal_to_new_array")

    animal_to_update = mock_animal(animal_type=AnimalType.CALF)

    herd_manager._update_animal_array(animal_to_update)

    mock_remove_animal_from_current_array.assert_called_once_with(animal_to_update)
    mock_add_animal_to_new_array.assert_called_once_with(animal_to_update)


def test_handle_graduated_animals(
    herd_manager: HerdManager, mocker: MockerFixture, mock_herd: dict[str, list[Animal]]
) -> None:
    """Unit test for _handle_graduated_animals()"""
    mock_remove_animal_from_pen_and_id_map = mocker.patch.object(herd_manager, "_remove_animal_from_pen_and_id_map")
    mock_update_animal_array = mocker.patch.object(herd_manager, "_update_animal_array")
    mock_add_animal_to_pen_and_id_map = mocker.patch.object(herd_manager, "_add_animal_to_pen_and_id_map")

    graduated_animals = [
        mock_animal(animal_type=AnimalType.HEIFER_I),
        mock_animal(animal_type=AnimalType.HEIFER_II),
        mock_animal(animal_type=AnimalType.HEIFER_III),
        mock_animal(animal_type=AnimalType.LAC_COW),
    ]
    mock_feed = MagicMock(auto_spec=Feed)
    mock_current_day_conditions = MagicMock(auto_spec=CurrentDayConditions)
    mock_total_inventory = MagicMock(auto_spec=TotalInventory)

    herd_manager._handle_graduated_animals(
        graduated_animals, [mock_feed], mock_current_day_conditions, mock_total_inventory, 15
    )

    assert mock_remove_animal_from_pen_and_id_map.call_args_list == [call(animal) for animal in graduated_animals]
    assert mock_update_animal_array.call_args_list == [call(animal) for animal in graduated_animals]
    assert mock_add_animal_to_pen_and_id_map.call_args_list == [
        call(animal, [mock_feed], mock_current_day_conditions, mock_total_inventory, 15) for animal in graduated_animals
    ]


def test_handle_newly_added_animals(
    herd_manager: HerdManager, mocker: MockerFixture, mock_herd: dict[str, list[Animal]]
) -> None:
    """Unit test for _handle_newly_added_animals()"""
    mock_add_animal_to_pen_and_id_map = mocker.patch.object(herd_manager, "_add_animal_to_pen_and_id_map")

    new_animals = [
        mock_animal(animal_type=AnimalType.HEIFER_I),
        mock_animal(animal_type=AnimalType.HEIFER_II),
        mock_animal(animal_type=AnimalType.HEIFER_III),
        mock_animal(animal_type=AnimalType.LAC_COW),
    ]
    mock_feed = MagicMock(auto_spec=Feed)
    mock_current_day_conditions = MagicMock(auto_spec=CurrentDayConditions)
    mock_total_inventory = MagicMock(auto_spec=TotalInventory)

    herd_manager._handle_newly_added_animals(
        new_animals, [mock_feed], mock_current_day_conditions, mock_total_inventory, 15
    )

    assert mock_add_animal_to_pen_and_id_map.call_args_list == [
        call(animal, [mock_feed], mock_current_day_conditions, mock_total_inventory, 15) for animal in new_animals
    ]

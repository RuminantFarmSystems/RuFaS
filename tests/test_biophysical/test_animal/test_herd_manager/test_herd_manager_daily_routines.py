from datetime import datetime
from random import shuffle, randint
from typing import Any, cast
from unittest.mock import call, MagicMock, PropertyMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_genetics.animal_genetics import Genetics
from RUFAS.biophysical.animal.bedding.bedding import Bedding
from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus, Breed
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_population import AnimalPopulation
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import NewBornCalfValuesTypedDict
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput
from RUFAS.biophysical.animal.data_types.daily_herd_updates import DailyHerdUpdates
from RUFAS.biophysical.animal.data_types.animal_manure_excretions import AnimalManureExcretions
from RUFAS.biophysical.animal.data_types.reproduction import HerdReproductionStatistics
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.data_structures.feed_storage_to_animal_connection import Feed
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
    dead_animal.days_born = 888

    dead_output = DailyRoutinesOutput(
        animal_status=AnimalStatus.DEAD,
        newborn_calf_config=None,
        herd_reproduction_statistics=HerdReproductionStatistics(),
    )
    mocker.patch.object(dead_animal, "daily_routines", return_value=dead_output)

    calving_animal = MagicMock(spec=Animal)
    calving_animal.animal_type = AnimalType.DRY_COW
    calving_animal.days_born = 576
    calving_animal.genetics = MagicMock(spec=Genetics)
    mocker.patch.object(calving_animal.genetics, "recalculate_values_at_lactation_start")

    newborn_config: NewBornCalfValuesTypedDict = {
        "breed": Breed.HO.name,
        "animal_type": AnimalType.CALF.value,
        "birth_date": "",
        "days_born": 0,
        "birth_weight": 10.1,
        "initial_phosphorus": 10.0,
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
    mock_time.current_date = datetime(2023, 1, 1)

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
    mock_current_day_conditions = MagicMock(auto_spec=CurrentDayConditions)

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
        simulation_day=15,
    )

    mock_handle_graduated_animals.assert_called_once_with(
        graduated_animals, mock_available_feeds, mock_current_day_conditions, 15
    )
    assert mock_handle_newly_added_animals.call_args_list == [
        call(newborn_calves, mock_available_feeds, mock_current_day_conditions, 15),
        call(newly_added_animals, mock_available_feeds, mock_current_day_conditions, 15),
    ]
    assert mock_remove_animal_from_pen_and_id_map.call_args_list == [call(animal) for animal in removed_animals]


def test_collect_daily_herd_updates(
    herd_manager: HerdManager, mock_herd: dict[str, list[Animal]], mocker: MockerFixture
) -> None:
    """Unit test for _collect_daily_herd_updates()."""
    mock_time = MagicMock(auto_spec=RufasTime)

    graduated_calves = mock_herd["calves"][:1]
    sold_calves = [mock_animal(AnimalType.CALF, sold=True)]
    ignored_calf_stillborns = [mock_animal(AnimalType.CALF, stillborn=True)]
    ignored_calf_newborns = [mock_animal(AnimalType.CALF)]
    ignored_calf_sold_newborns = [mock_animal(AnimalType.CALF, sold=True)]

    graduated_heiferIs = mock_herd["heiferIs"][:1]
    sold_heiferIs = [mock_animal(AnimalType.HEIFER_I, sold=True)]
    graduated_heiferIIs = mock_herd["heiferIIs"][:1]
    sold_heiferIIs = [mock_animal(AnimalType.HEIFER_II, sold=True)]

    graduated_heiferIIIs = mock_herd["heiferIIIs"][:1]
    sold_heiferIIIs = [mock_animal(AnimalType.HEIFER_III, sold=True)]
    heiferIII_stillborns = [mock_animal(AnimalType.CALF, stillborn=True)]
    heiferIII_newborns = [mock_animal(AnimalType.CALF)]
    heiferIII_sold_newborns = [mock_animal(AnimalType.CALF, sold=True)]

    graduated_cows = mock_herd["lac_cows"][:1]
    sold_and_died_cows = [mock_animal(AnimalType.LAC_COW, sold=True)]
    cow_stillborns = [mock_animal(AnimalType.CALF, stillborn=True)]
    cow_newborns = [mock_animal(AnimalType.CALF)]
    cow_sold_newborns = [mock_animal(AnimalType.CALF, sold=True)]

    mock_perform_daily_routines_for_animals = mocker.patch.object(
        herd_manager,
        "_perform_daily_routines_for_animals",
        side_effect=[
            (graduated_calves, sold_calves, ignored_calf_stillborns, ignored_calf_newborns, ignored_calf_sold_newborns),
            (graduated_heiferIs, sold_heiferIs, [], [], []),
            (graduated_heiferIIs, sold_heiferIIs, [], [], []),
            (
                graduated_heiferIIIs,
                sold_heiferIIIs,
                heiferIII_stillborns,
                heiferIII_newborns,
                heiferIII_sold_newborns,
            ),
            (graduated_cows, sold_and_died_cows, cow_stillborns, cow_newborns, cow_sold_newborns),
        ],
    )

    actual_daily_herd_updates = herd_manager._process_daily_herd_updates(mock_time)

    assert mock_perform_daily_routines_for_animals.call_args_list == [
        call(mock_time, herd_manager.calves),
        call(mock_time, herd_manager.heiferIs),
        call(mock_time, herd_manager.heiferIIs),
        call(mock_time, herd_manager.heiferIIIs),
        call(mock_time, herd_manager.cows),
    ]
    assert isinstance(actual_daily_herd_updates, DailyHerdUpdates)
    assert actual_daily_herd_updates.graduated_animals == (
        graduated_calves + graduated_heiferIs + graduated_heiferIIs + graduated_heiferIIIs + graduated_cows
    )
    assert (
        actual_daily_herd_updates.removed_animals
        == sold_calves + sold_heiferIs + sold_heiferIIs + sold_heiferIIIs + sold_and_died_cows
    )
    assert actual_daily_herd_updates.newborn_calves == heiferIII_newborns + cow_newborns
    assert actual_daily_herd_updates.sold_newborn_calves == heiferIII_sold_newborns + cow_sold_newborns
    assert actual_daily_herd_updates.stillborn_newborn_calves == heiferIII_stillborns + cow_stillborns
    assert actual_daily_herd_updates.sold_heiferIIs == sold_heiferIIs
    assert actual_daily_herd_updates.sold_and_died_cows == sold_and_died_cows


@pytest.mark.parametrize("simulation_day, expect_adjustment", [(14, False), (15, True)])
def test_apply_daily_herd_structure_updates(
    simulation_day: int,
    expect_adjustment: bool,
    herd_manager: HerdManager,
    mock_herd: dict[str, list[Animal]],
    mocker: MockerFixture,
) -> None:
    """Unit test for _apply_daily_herd_structure_updates()."""
    graduated_animals = mock_herd["heiferIs"]
    newborn_calves = mock_herd["calves"]
    removed_animals = [mock_animal(AnimalType.LAC_COW, sold=True)]
    sold_oversupply_cows = [mock_animal(AnimalType.LAC_COW, sold=True)]
    replacement_heifers = [mock_animal(AnimalType.HEIFER_III)]
    mock_available_feeds: list[Feed] = [MagicMock(auto_spec=Feed)]
    mock_current_day_conditions = MagicMock(auto_spec=CurrentDayConditions)
    mock_weather = MagicMock(auto_spec=Weather)
    mock_weather.get_current_day_conditions.return_value = mock_current_day_conditions
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = simulation_day
    herd_manager.adjustment_period = 15

    mock_check_if_cows_need_to_be_sold = mocker.patch.object(
        herd_manager, "_check_if_cows_need_to_be_sold", return_value=sold_oversupply_cows
    )
    mock_update_sold_and_died_cow_statistics = mocker.patch.object(herd_manager, "_update_sold_and_died_cow_statistics")
    mock_check_if_replacement_heifers_needed = mocker.patch.object(
        herd_manager, "_check_if_replacement_heifers_needed", return_value=replacement_heifers
    )
    mock_update_herd_structure = mocker.patch.object(herd_manager, "_update_herd_structure")

    herd_manager._apply_daily_herd_structure_updates(
        graduated_animals=graduated_animals,
        newborn_calves=newborn_calves,
        removed_animals=removed_animals,
        available_feeds=mock_available_feeds,
        time=mock_time,
        weather=mock_weather,
    )

    if expect_adjustment:
        mock_check_if_cows_need_to_be_sold.assert_called_once_with(
            simulation_day=simulation_day, removed_animal=removed_animals
        )
        mock_update_sold_and_died_cow_statistics.assert_called_once_with(removed_animals)
        mock_check_if_replacement_heifers_needed.assert_called_once_with(time=mock_time)
        expected_removed_animals = removed_animals
        expected_newly_added_animals = replacement_heifers
    else:
        mock_check_if_cows_need_to_be_sold.assert_not_called()
        mock_update_sold_and_died_cow_statistics.assert_not_called()
        mock_check_if_replacement_heifers_needed.assert_not_called()
        expected_removed_animals = removed_animals
        expected_newly_added_animals = []

    mock_update_herd_structure.assert_called_once_with(
        graduated_animals=graduated_animals,
        newborn_calves=newborn_calves,
        newly_added_animals=expected_newly_added_animals,
        removed_animals=expected_removed_animals,
        available_feeds=mock_available_feeds,
        current_day_conditions=mock_current_day_conditions,
        simulation_day=simulation_day,
    )


def test_collect_manure_outputs_by_pen(herd_manager: HerdManager) -> None:
    """Unit test for _collect_manure_outputs_by_pen()."""
    first_pen, second_pen = MagicMock(), MagicMock()
    first_pen.id = 1
    first_pen.animal_combination.name = "CALF"
    first_pen.total_manure_excretion = MagicMock()
    first_pen.total_enteric_methane = 1.5
    first_pen.get_manure_streams.return_value = {"first_stream": MagicMock()}
    second_pen.id = 2
    second_pen.animal_combination.name = "LAC_COW"
    second_pen.total_manure_excretion = MagicMock()
    second_pen.total_enteric_methane = 2.5
    second_pen.get_manure_streams.return_value = {"second_stream": MagicMock()}
    herd_manager.all_pens = [first_pen, second_pen]

    herd_manager_output, animal_manure_excretions_by_pen, enteric_methane_emission_by_pen = (
        herd_manager._collect_manure_outputs_by_pen()
    )

    assert herd_manager_output == {
        "first_stream": first_pen.get_manure_streams.return_value["first_stream"],
        "second_stream": second_pen.get_manure_streams.return_value["second_stream"],
    }
    assert animal_manure_excretions_by_pen == {
        "CALF_PEN_1": first_pen.total_manure_excretion,
        "LAC_COW_PEN_2": second_pen.total_manure_excretion,
    }
    assert enteric_methane_emission_by_pen == {"CALF_PEN_1": 1.5, "LAC_COW_PEN_2": 2.5}


def test_warn_when_lactating_cows_have_no_milk(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    """Unit test for _warn_when_lactating_cows_have_no_milk()."""
    no_milk_cow = MagicMock()
    no_milk_cow.milk_production.daily_milk_produced = 0
    no_milk_cow.is_milking = True
    no_milk_cow.days_in_milk = 2
    milking_cow = MagicMock()
    milking_cow.milk_production.daily_milk_produced = 10
    milking_cow.is_milking = True
    milking_cow.days_in_milk = 2
    first_day_cow = MagicMock()
    first_day_cow.milk_production.daily_milk_produced = 0
    first_day_cow.is_milking = True
    first_day_cow.days_in_milk = 1
    herd_manager.cows = [no_milk_cow, milking_cow, first_day_cow]
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 15
    mock_add_warning = mocker.patch.object(herd_manager.om, "add_warning")

    herd_manager._warn_when_lactating_cows_have_no_milk(mock_time)

    mock_add_warning.assert_called_once_with(
        "Warning: Lactating cows with no production.",
        "There are 1 lactating cows with no milking production on simulation day 15.",
        info_map={
            "class": herd_manager.__class__.__name__,
            "function": herd_manager.execute_daily_routines.__name__,
            "simulation_day": 15,
        },
    )


def test_report_daily_routine_outputs(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    """Unit test for _report_daily_routine_outputs()."""
    herd_manager_output = {"stream": ManureStream.make_empty_manure_stream()}
    animal_manure_excretions_by_pen = {"CALF_PEN_1": AnimalManureExcretions()}
    enteric_methane_emission_by_pen = {"CALF_PEN_1": 1.0}
    mocker.patch.object(HerdManager, "average_herd_305_days_milk_production", new_callable=PropertyMock)
    mock_report_enteric_methane_emission = mocker.patch(
        "RUFAS.biophysical.animal.animal_module_reporter.AnimalModuleReporter.report_enteric_methane_emission"
    )
    mock_report_daily_animal_population = mocker.patch(
        "RUFAS.biophysical.animal.animal_module_reporter.AnimalModuleReporter.report_daily_animal_population"
    )
    mock_report_herd_statistics_data = mocker.patch(
        "RUFAS.biophysical.animal.animal_module_reporter.AnimalModuleReporter.report_herd_statistics_data"
    )
    mock_report_manure_excretions = mocker.patch(
        "RUFAS.biophysical.animal.animal_module_reporter.AnimalModuleReporter.report_manure_excretions"
    )
    mock_report_manure_streams = mocker.patch(
        "RUFAS.biophysical.animal.animal_module_reporter.AnimalModuleReporter.report_manure_streams"
    )
    mock_report_milk = mocker.patch("RUFAS.biophysical.animal.animal_module_reporter.AnimalModuleReporter.report_milk")
    mock_report_305d_milk = mocker.patch(
        "RUFAS.biophysical.animal.animal_module_reporter.AnimalModuleReporter.report_305d_milk"
    )
    mock_report_ration = mocker.patch.object(herd_manager, "_report_ration")
    mock_calculate_and_report_average_genetics = mocker.patch.object(
        herd_manager, "_calculate_and_report_average_genetics"
    )

    herd_manager._report_daily_routine_outputs(
        herd_manager_output, animal_manure_excretions_by_pen, enteric_methane_emission_by_pen, simulation_day=15
    )

    mock_report_enteric_methane_emission.assert_called_once_with(enteric_methane_emission_by_pen)
    mock_report_daily_animal_population.assert_called_once_with(herd_manager.herd_statistics, 15)
    mock_report_herd_statistics_data.assert_called_once_with(herd_manager.herd_statistics, 15)
    mock_report_manure_excretions.assert_called_once_with(animal_manure_excretions_by_pen, 15)
    mock_report_manure_streams.assert_called_once_with(herd_manager_output, 15)
    mock_report_milk.assert_called_once_with(herd_manager.daily_milk_report, 15)
    mock_report_305d_milk.assert_called_once()
    mock_report_ration.assert_called_once_with(15)
    mock_calculate_and_report_average_genetics.assert_called_once_with(15)


def test_daily_routines(herd_manager: HerdManager, mock_herd: dict[str, list[Animal]], mocker: MockerFixture) -> None:
    """Unit test for daily_routines()"""
    mock_feed = MagicMock(auto_spec=Feed)
    mock_weather = MagicMock(auto_spec=Weather)
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 15

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
    mock_check_if_cows_need_to_be_sold = mocker.patch.object(
        herd_manager, "_check_if_cows_need_to_be_sold", return_value=sold_oversupply_heiferIIIs
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

    herd_manager.execute_daily_routines([mock_feed], mock_time, mock_weather)

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
    assert mock_check_if_cows_need_to_be_sold.call_count == 0
    assert mock_check_if_replacement_heifers_needed.call_count == 0
    assert mock_update_herd_structure.call_count == 1
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
        dam_tbv_fat=10.0,
        dam_tbv_protein=10.0,
    )
    animal = mock_animal(animal_type=AnimalType.CALF, sold=is_newborn_calf_sold, stillborn=is_newborn_calf_stillborn)
    animal.events = MagicMock(auto_spec=AnimalEvents)
    animal.events.add_event = MagicMock()

    mock_animal_init = mocker.patch("RUFAS.biophysical.animal.herd_manager.Animal", return_value=animal)

    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 100
    mock_time.current_date = datetime.today()

    herd_manager._create_newborn_calf(newborn_calf_config, mock_time)

    expected_newborn_calf_config = newborn_calf_config.copy()
    expected_newborn_calf_config["id"] = AnimalPopulation.current_animal_id
    mock_animal_init.assert_called_once_with(args=expected_newborn_calf_config, time=mock_time)

    if not (is_newborn_calf_stillborn or is_newborn_calf_sold):
        animal.events.add_event.assert_called_once()


def _create_sortable_mock_cow(
    id_val: int, is_dnb: bool, daily_milk: float, days_in_milk: int, days_in_pregnancy: int
) -> Animal:
    """Helper to create a mock cow with specific sorting attributes."""
    cow = MagicMock(spec=Animal)
    cow.id = id_val
    cow.animal_type = AnimalType.LAC_COW
    cow.body_weight = 600.0
    cow.sold_at_day = None

    cow.reproduction = MagicMock()
    cow.reproduction.do_not_breed = is_dnb
    cow.reproduction.calves = 1

    cow.milk_production = MagicMock()
    cow.milk_production.daily_milk_produced = daily_milk

    cow.days_in_milk = days_in_milk
    cow.days_in_pregnancy = days_in_pregnancy
    return cast(Animal, cow)


def test_check_if_cows_need_to_be_sold_comprehensive(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    """
    Unit test for _check_if_cows_need_to_be_sold().

    Verifies:
    1. All eligible cows are ranked only by lowest milk production.
    2. Cows with DIM <= 60 are protected (skipped).
    3. Cows with days in pregnancy >= 180 are protected (skipped).
    4. Error is logged if herd is too large but no cows are eligible.
    5. Statistics are updated correctly based on source code logic.
    """
    HERD_TARGET = 10
    SELLING_THRESHOLD = 10
    SIMULATION_DAY = 100

    herd_manager.herd_statistics.herd_num = HERD_TARGET
    herd_manager.selling_threshold = SELLING_THRESHOLD
    herd_manager.herd_statistics.cow_num = 15
    herd_manager.herd_statistics.sold_cow_oversupply_num = 0
    herd_manager.herd_statistics.sold_cow_num = 0
    herd_manager.herd_statistics.cow_herd_exit_num = 10

    cow_dnb_low_milk = _create_sortable_mock_cow(1, True, 10.0, 100, 50)
    cow_dnb_high_milk = _create_sortable_mock_cow(2, True, 50.0, 100, 60)
    cow_normal_low_milk = _create_sortable_mock_cow(3, False, 20.0, 100, 70)
    cow_normal_high_milk = _create_sortable_mock_cow(4, False, 40.0, 100, 80)
    cow_protected_low_dim = _create_sortable_mock_cow(5, False, 5.0, 10, 0)
    cow_protected_high_preg = _create_sortable_mock_cow(6, False, 1.0, 200, 180)

    fillers = []
    for i in range(10):
        fillers.append(_create_sortable_mock_cow(10 + i, False, 100.0, 200, 20))

    fillers[0].milk_production.daily_milk_produced = 90.0

    all_cows = [
        cow_dnb_low_milk,
        cow_dnb_high_milk,
        cow_normal_low_milk,
        cow_normal_high_milk,
        cow_protected_low_dim,
        cow_protected_high_preg,
    ] + fillers

    herd_manager.cows = all_cows

    mock_om_add_error = mocker.patch.object(herd_manager.om, "add_error")

    removed_cows = herd_manager._check_if_cows_need_to_be_sold(SIMULATION_DAY, [])

    assert len(removed_cows) == 6
    assert len(herd_manager.cows) == 10

    assert removed_cows[0] == cow_dnb_low_milk
    assert removed_cows[1] == cow_normal_low_milk
    assert removed_cows[2] == cow_normal_high_milk
    assert removed_cows[3] == cow_dnb_high_milk
    assert removed_cows[4] == fillers[0]

    assert cow_protected_low_dim in herd_manager.cows
    assert cow_protected_high_preg in herd_manager.cows

    herd_manager.herd_statistics.herd_num = 1
    herd_manager.selling_threshold = 1.0

    cow_prot_1 = _create_sortable_mock_cow(99, False, 100.0, 10, 0)
    cow_prot_2 = _create_sortable_mock_cow(98, False, 100.0, 10, 0)
    herd_manager.cows = [cow_prot_1, cow_prot_2]

    stuck_result = herd_manager._check_if_cows_need_to_be_sold(SIMULATION_DAY, [])

    assert len(stuck_result) == 0
    mock_om_add_error.assert_called_once()


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

    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 100
    mock_time.current_date = datetime.today()
    AnimalConfig.average_phenotype["fat_kg"] = {mock_time.current_date.year: 10.0}
    AnimalConfig.average_phenotype["protein_kg"] = {mock_time.current_date.year: 10.0}

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

    herd_manager._handle_graduated_animals(graduated_animals, [mock_feed], mock_current_day_conditions, 15)

    assert mock_remove_animal_from_pen_and_id_map.call_args_list == [call(animal) for animal in graduated_animals]
    assert mock_update_animal_array.call_args_list == [call(animal) for animal in graduated_animals]
    assert mock_add_animal_to_pen_and_id_map.call_args_list == [
        call(animal, [mock_feed], mock_current_day_conditions, 15) for animal in graduated_animals
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

    herd_manager._handle_newly_added_animals(new_animals, [mock_feed], mock_current_day_conditions, 15)

    assert mock_add_animal_to_pen_and_id_map.call_args_list == [
        call(animal, [mock_feed], mock_current_day_conditions, 15) for animal in new_animals
    ]


def test_update_genetic_values_at_lactation_start_disabled(herd_manager: HerdManager) -> None:
    """simulate_genetics=False → early return, recalculate never called."""
    AnimalConfig.simulate_genetics = False
    animal = mock_animal(AnimalType.LAC_COW)
    animal.genetics = MagicMock(spec=Genetics)
    mock_time = MagicMock(auto_spec=RufasTime)

    herd_manager._update_genetic_values_at_lactation_start(animal, mock_time)

    animal.genetics.recalculate_values_at_lactation_start.assert_not_called()


def test_update_genetic_values_at_lactation_start_enabled(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    """simulate_genetics=True → recalculate_values_at_lactation_start called with group TBV means."""
    AnimalConfig.simulate_genetics = True

    cow = mock_animal(AnimalType.LAC_COW, days_born=730)
    cow.genetics = MagicMock(spec=Genetics)
    cow.calves = 2

    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.current_date = datetime(2022, 6, 1)

    mocker.patch.object(Genetics, "calculate_average_tbv", return_value=(15.0, 25.0))

    herd_manager._update_genetic_values_at_lactation_start(cow, mock_time)

    cow.genetics.recalculate_values_at_lactation_start.assert_called_once_with(
        birth_year=2020,
        animal_type=cow.animal_type,
        parity=cow.calves,
        group_specific_TBV_fat_mean=15.0,
        group_specific_TBV_protein_mean=25.0,
    )


def test_calculate_and_report_average_genetics_disabled(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    """simulate_genetics=False → early return, no reporting."""
    AnimalConfig.simulate_genetics = False
    mocker.patch.object(
        herd_manager.__class__,
        "_calculate_and_report_average_genetics",
        wraps=herd_manager._calculate_and_report_average_genetics,
    )
    mock_genetics_avg = mocker.patch.object(Genetics, "calculate_average_genetic_values")
    mock_reporter = mocker.patch("RUFAS.biophysical.animal.herd_manager.AnimalModuleReporter")

    herd_manager._calculate_and_report_average_genetics(simulation_day=10)

    mock_genetics_avg.assert_not_called()
    mock_reporter.report_average_genetics.assert_not_called()


def test_calculate_and_report_average_genetics_enabled(
    herd_manager: HerdManager, mock_herd: dict[str, list[Animal]], mocker: MockerFixture
) -> None:
    """simulate_genetics=True → average genetics computed and reported for all 6 groups."""
    AnimalConfig.simulate_genetics = True

    herd_manager.calves = mock_herd["calves"]
    herd_manager.heiferIs = mock_herd["heiferIs"]
    herd_manager.heiferIIs = mock_herd["heiferIIs"]
    herd_manager.heiferIIIs = mock_herd["heiferIIIs"]
    herd_manager.cows = mock_herd["lac_cows"] + mock_herd["dry_cows"]

    for animal in (
        herd_manager.calves
        + herd_manager.heiferIs
        + herd_manager.heiferIIs
        + herd_manager.heiferIIIs
        + herd_manager.cows
    ):
        animal.genetics = MagicMock(spec=Genetics)

    fake_avg = {"TBV_fat": 1.0, "TBV_protein": 2.0}
    mocker.patch.object(Genetics, "calculate_average_genetic_values", return_value=fake_avg)
    mock_report = mocker.patch("RUFAS.biophysical.animal.herd_manager.AnimalModuleReporter.report_average_genetics")

    herd_manager._calculate_and_report_average_genetics(simulation_day=10)

    assert mock_report.call_count == 6
    reported_groups = {c.args[1] for c in mock_report.call_args_list}
    assert reported_groups == {"herd", "calves", "heiferI", "heiferII", "heiferIII", "cow"}


def test_create_newborn_calf_genetics_enabled(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    """simulate_genetics=True → calculate_ebv_and_ranking_index called on newborn."""
    AnimalConfig.simulate_genetics = True
    AnimalPopulation.set_current_max_animal_id(0)

    newborn_calf_config = NewBornCalfValuesTypedDict(
        breed=Breed.HO.name,
        animal_type=AnimalType.CALF.value,
        birth_date="",
        days_born=0,
        birth_weight=10.0,
        initial_phosphorus=10.0,
        dam_tbv_fat=5.0,
        dam_tbv_protein=3.0,
    )

    calf = mock_animal(animal_type=AnimalType.CALF, sold=False, stillborn=False)
    calf.genetics = MagicMock(spec=Genetics)
    calf.calves = 0
    calf.events = MagicMock(auto_spec=AnimalEvents)

    mocker.patch("RUFAS.biophysical.animal.herd_manager.Animal", return_value=calf)
    mocker.patch.object(Genetics, "calculate_average_tbv", return_value=(8.0, 16.0))
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 1
    mock_time.current_date = datetime.today()

    herd_manager._create_newborn_calf(newborn_calf_config, mock_time)

    calf.genetics.calculate_ebv_and_ranking_index.assert_called_once_with(calf.animal_type, 8.0, 16.0, calf.calves)


def test_create_newborn_calf_genetics_disabled(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    """simulate_genetics=False → calculate_ebv_and_ranking_index NOT called."""
    AnimalConfig.simulate_genetics = False
    AnimalPopulation.set_current_max_animal_id(0)

    newborn_calf_config = NewBornCalfValuesTypedDict(
        breed=Breed.HO.name,
        animal_type=AnimalType.CALF.value,
        birth_date="",
        days_born=0,
        birth_weight=10.0,
        initial_phosphorus=10.0,
    )

    calf = mock_animal(animal_type=AnimalType.CALF, sold=False, stillborn=False)
    calf.genetics = None
    calf.events = MagicMock(auto_spec=AnimalEvents)

    mocker.patch("RUFAS.biophysical.animal.herd_manager.Animal", return_value=calf)
    mock_calculate_avg_tbv = mocker.patch.object(Genetics, "calculate_average_tbv")
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 1
    mock_time.current_date = datetime.today()

    herd_manager._create_newborn_calf(newborn_calf_config, mock_time)

    mock_calculate_avg_tbv.assert_not_called()


def test_update_replacement_animal_genetics(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    """Replacement genetics re-initialised using heiferIII TBV mean, EBV recalculated."""
    AnimalConfig.simulate_genetics = True
    AnimalConfig.average_phenotype["fat_kg"] = {2020: 10.0}
    AnimalConfig.average_phenotype["protein_kg"] = {2020: 20.0}

    replacement = mock_animal(AnimalType.HEIFER_III, days_born=730)
    replacement.calves = 0

    herd_manager.heiferIIIs = [mock_animal(AnimalType.HEIFER_III, id=i) for i in range(3)]
    for a in herd_manager.heiferIIIs:
        a.genetics = MagicMock(spec=Genetics)

    mock_genetics_instance = MagicMock(spec=Genetics)
    mock_genetics_cls = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.Genetics", return_value=mock_genetics_instance
    )
    mock_genetics_cls.calculate_average_tbv.return_value = (5.0, 10.0)

    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.current_date = datetime(2022, 6, 1)

    herd_manager._update_replacement_animal_genetics(replacement, mock_time)

    mock_genetics_cls.assert_called_once_with(
        birth_year=2020,
        animal_type=replacement.animal_type,
    )
    assert replacement.genetics == mock_genetics_instance
    mock_genetics_instance.calculate_ebv_and_ranking_index.assert_called_once_with(
        replacement.animal_type, 5.0, 10.0, replacement.calves
    )

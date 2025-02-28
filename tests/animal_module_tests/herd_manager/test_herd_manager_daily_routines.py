import copy
from datetime import datetime
from typing import Any
from unittest import mock
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus, Breed
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_population import AnimalPopulation
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import NewBornCalfValuesTypedDict
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.feed_storage_to_animal_connection import Feed, TotalInventory
from RUFAS.enums import AnimalCombination
from RUFAS.time import Time
from RUFAS.weather import Weather

from tests.animal_module_tests.herd_manager.pytest_fixtures import (
    config_json, animal_json, manure_management_json, feed_json, mock_get_data_side_effect,
    mock_herd, mock_animal, mock_pen, herd_manager, mock_herd_manager
)

assert config_json
assert animal_json
assert manure_management_json
assert feed_json
assert mock_get_data_side_effect

def test_daily_routines(
    herd_manager: HerdManager, mock_herd: dict[str, list[Animal]], mocker: MockerFixture
) -> None:
    herd_manager.all_pens = [
        mock_pen(AnimalCombination.CALF, mocker),
        mock_pen(AnimalCombination.GROWING, mocker),
        mock_pen(AnimalCombination.CLOSE_UP, mocker),
        mock_pen(AnimalCombination.LAC_COW, mocker),
    ]

    mock_feed = mocker.MagicMock(auto_spec=Feed)
    mock_weather = mocker.MagicMock(auto_spec=Weather)
    mock_time = mocker.MagicMock(auto_spec=Time)

    mock_animal_daily_routines_side_effect = [
        DailyRoutinesOutput(animal_status=AnimalStatus.REMAIN, newborn_calf_config=None),
        DailyRoutinesOutput(animal_status=AnimalStatus.LIFE_STAGE_CHANGED, newborn_calf_config=None),
        DailyRoutinesOutput(animal_status=AnimalStatus.SOLD, newborn_calf_config=None),
        DailyRoutinesOutput(animal_status=AnimalStatus.REMAIN, newborn_calf_config=None),
        DailyRoutinesOutput(animal_status=AnimalStatus.LIFE_STAGE_CHANGED, newborn_calf_config=None),
        DailyRoutinesOutput(animal_status=AnimalStatus.SOLD, newborn_calf_config=None),
        DailyRoutinesOutput(animal_status=AnimalStatus.REMAIN, newborn_calf_config=None),
        DailyRoutinesOutput(animal_status=AnimalStatus.LIFE_STAGE_CHANGED, newborn_calf_config=None),
        DailyRoutinesOutput(animal_status=AnimalStatus.SOLD, newborn_calf_config=None),
        DailyRoutinesOutput(animal_status=AnimalStatus.REMAIN, newborn_calf_config=None),
        DailyRoutinesOutput(
            animal_status=AnimalStatus.LIFE_STAGE_CHANGED,
            newborn_calf_config=NewBornCalfValuesTypedDict(
                breed=Breed.HO.name,
                animal_type=AnimalType.CALF.value,
                birth_date="",
                days_born=0,
                birth_weight=10.1,
                initial_phosphorus=10.0,
                net_merit=18.8
            )
        ),
        DailyRoutinesOutput(
            animal_status=AnimalStatus.LIFE_STAGE_CHANGED,
            newborn_calf_config=NewBornCalfValuesTypedDict(
                breed=Breed.HO.name,
                animal_type=AnimalType.CALF.value,
                birth_date="",
                days_born=0,
                birth_weight=10.1,
                initial_phosphorus=10.0,
                net_merit=18.8
            )
        ),
        DailyRoutinesOutput(animal_status=AnimalStatus.SOLD, newborn_calf_config=None),
        DailyRoutinesOutput(animal_status=AnimalStatus.REMAIN, newborn_calf_config=None),
        DailyRoutinesOutput(animal_status=AnimalStatus.REMAIN, newborn_calf_config=None),
        DailyRoutinesOutput(animal_status=AnimalStatus.REMAIN, newborn_calf_config=None),
        DailyRoutinesOutput(
            animal_status=AnimalStatus.LIFE_STAGE_CHANGED,
            newborn_calf_config=NewBornCalfValuesTypedDict(
                breed=Breed.HO.name,
                animal_type=AnimalType.CALF.value,
                birth_date="",
                days_born=0,
                birth_weight=10.1,
                initial_phosphorus=10.0,
                net_merit=18.8
            )
        ),
        DailyRoutinesOutput(
            animal_status=AnimalStatus.LIFE_STAGE_CHANGED,
            newborn_calf_config=NewBornCalfValuesTypedDict(
                breed=Breed.HO.name,
                animal_type=AnimalType.CALF.value,
                birth_date="",
                days_born=0,
                birth_weight=10.1,
                initial_phosphorus=10.0,
                net_merit=18.8
            )
        ),
        DailyRoutinesOutput(animal_status=AnimalStatus.SOLD, newborn_calf_config=None),
    ]
    mock_create_newborn_calf_side_effect = [
        mock_animal(
            animal_type=AnimalType.CALF,
            mocker=mocker,
            sold=False,
        ),
        mock_animal(
            animal_type=AnimalType.CALF,
            mocker=mocker,
            sold=True,
        ),
        mock_animal(
            animal_type=AnimalType.CALF,
            mocker=mocker,
            sold=False,
        ),
        mock_animal(
            animal_type=AnimalType.CALF,
            mocker=mocker,
            sold=True,
        ),
    ]
    mock_create_newborn_calf = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._create_newborn_calf",
        side_effect=copy.deepcopy(mock_create_newborn_calf_side_effect),
    )

    animals = (
        mock_herd["calves"]
        + mock_herd["heiferIs"]
        + mock_herd["heiferIIs"]
        + mock_herd["heiferIIIs"]
        + mock_herd["dry_cows"]
        + mock_herd["lac_cows"]
    )
    graduated_animals: list[Animal] = []
    newborn_calves: list[Animal] = []
    removed_animals: list[Animal] = []

    sold_heiferIIs: list[Animal] = []
    sold_and_died_cows: list[Animal] = []
    sold_newborn_calves: list[Animal] = []
    for animal in animals:
        return_value = mock_animal_daily_routines_side_effect.pop(0)
        animal.daily_routines = mocker.MagicMock(return_value=return_value)
        if return_value.animal_status in [AnimalStatus.DEAD, AnimalStatus.SOLD]:
            removed_animals.append(animal)
            if animal.animal_type == AnimalType.HEIFER_II:
                sold_heiferIIs.append(animal)
            elif animal.animal_type.is_cow:
                sold_and_died_cows.append(animal)
        elif return_value.animal_status == AnimalStatus.LIFE_STAGE_CHANGED:
            graduated_animals.append(animal)
            if return_value.newborn_calf_config is not None and (
                    animal.animal_type == AnimalType.HEIFER_III or animal.animal_type.is_cow
            ):
                newborn_calf = mock_create_newborn_calf_side_effect.pop(0)
                if newborn_calf.sold:
                    sold_newborn_calves.append(newborn_calf)
                else:
                    newborn_calves.append(newborn_calf)


    mock_update_sold_and_died_cows = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._update_sold_and_died_cow_statistics"
    )
    mock_update_sold_heiferIIs = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._update_sold_heiferII_statistics"
    )
    mock_update_sold_newborn_calves = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._update_sold_newborn_calf_statistics"
    )
    mock_check_if_heifers_need_to_be_sold = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._check_if_heifers_need_to_be_sold", return_value=[]
    )
    mock_check_if_replacement_heifers_needed = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager._check_if_replacement_heifers_needed"
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
    mock_record_pen_history = mocker.patch("RUFAS.biophysical.animal.herd_manager.HerdManager.record_pen_history")
    mock_update_herd_statistics = mocker.patch(
        "RUFAS.biophysical.animal.herd_manager.HerdManager.update_herd_statistics"
    )
    mock_report_animal_module_manure = mocker.patch(
        "RUFAS.biophysical.animal.animal_module_reporter.AnimalModuleReporter.report_animal_module_manure"
    )
    mock_report_daily_reports = mocker.patch(
        "RUFAS.biophysical.animal.animal_module_reporter.AnimalModuleReporter.report_daily_reports"
    )

    mock_total_inventory = mock.MagicMock(auto_spec=TotalInventory)

    herd_manager.daily_routines(mock_feed, mock_time, mock_weather, mock_total_inventory)

    assert mock_create_newborn_calf.call_count == 4
    mock_update_sold_and_died_cows.assert_called_once_with(sold_and_died_cows)
    mock_update_sold_heiferIIs.assert_called_once_with(sold_heiferIIs)
    mock_update_sold_newborn_calves.assert_called_once_with(sold_newborn_calves)
    mock_check_if_heifers_need_to_be_sold.assert_called_once()
    mock_check_if_replacement_heifers_needed.assert_called_once()
    mock_handle_graduated_animals.assert_called_once_with(
        graduated_animals, mock_feed, mock_weather.get_current_day_conditions(), mock_total_inventory
    )
    assert mock_handle_newly_added_animals.call_count == 2
    assert mock_remove_animal_from_pen_and_id_map.call_args_list == [call(animal) for animal in removed_animals]
    mock_record_pen_history.assert_called_once()
    mock_update_herd_statistics.assert_called_once()
    mock_report_animal_module_manure.assert_called_once()
    mock_report_daily_reports.assert_called_once()


@pytest.mark.parametrize(
    "is_newborn_calf_sold", [True, False]
)
def test_create_newborn_calf(is_newborn_calf_sold: bool, herd_manager: HerdManager, mocker: MockerFixture) -> None:
    AnimalPopulation.set_current_max_animal_id(0)
    newborn_calf_config = NewBornCalfValuesTypedDict(
        breed=Breed.HO.name,
        animal_type=AnimalType.CALF.value,
        birth_date="",
        days_born=0,
        birth_weight=10.1,
        initial_phosphorus=10.0,
        net_merit=18.8
    )
    animal = mock_animal(animal_type=AnimalType.CALF, mocker=mocker, sold=is_newborn_calf_sold)
    animal.events = mock.MagicMock(auto_spec=AnimalEvents)
    animal.events.add_event = mock.MagicMock()

    mock_animal_init = mocker.patch("RUFAS.biophysical.animal.herd_manager.Animal", return_value=animal)

    herd_manager._create_newborn_calf(newborn_calf_config, 0)

    expected_newborn_calf_config = newborn_calf_config.copy()
    expected_newborn_calf_config["id"] = AnimalPopulation.current_animal_id
    mock_animal_init.assert_called_once_with(args=expected_newborn_calf_config, simulation_day=0)

    if not is_newborn_calf_sold:
        animal.events.add_event.assert_called_once_with(animal.days_born, 0, animal_constants.ENTER_HERD)


def test_check_if_heifers_need_to_be_sold(
    mock_get_data_side_effect: list[Any], mocker: MockerFixture, mock_herd: dict[str, list[Animal]]
) -> None:
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
            "animal_type": removed_heiferIII.animal_type,
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
        return_vale=8.8
    )

    mock_time = mocker.MagicMock(auto_spec=Time)
    mock_time.simulation_day = 100
    mock_time.current_date = datetime.today()

    result = herd_manager._check_if_replacement_heifers_needed(mock_time)

    expected_bought_animals = mock_herd["replacement"] * 2

    assert result == expected_bought_animals
    assert herd_manager.herd_statistics.bought_heifer_num == 2


def test_handle_graduated_animals(
    herd_manager: HerdManager, mocker: MockerFixture, mock_herd: dict[str, list[Animal]]
) -> None:
    mock_remove_animal_from_pen_and_id_map = mocker.patch.object(herd_manager, "_remove_animal_from_pen_and_id_map")
    mock_update_animal_array = mocker.patch.object(herd_manager, "_update_animal_array")
    mock_add_animal_to_pen_and_id_map = mocker.patch.object(herd_manager, "_add_animal_to_pen_and_id_map")

    graduated_animals = [
        mock_animal(animal_type=AnimalType.HEIFER_I, mocker=mocker),
        mock_animal(animal_type=AnimalType.HEIFER_II, mocker=mocker),
        mock_animal(animal_type=AnimalType.HEIFER_III, mocker=mocker),
        mock_animal(animal_type=AnimalType.LAC_COW, mocker=mocker),
    ]
    mock_feed = mocker.MagicMock(auto_spec=Feed)
    mock_current_day_conditions = mocker.MagicMock(auto_spec=CurrentDayConditions)
    mock_total_inventory = mocker.MagicMock(auto_spec=TotalInventory)

    herd_manager._handle_graduated_animals(
        graduated_animals, [mock_feed], mock_current_day_conditions, mock_total_inventory
    )

    assert mock_remove_animal_from_pen_and_id_map.call_args_list == [
        call(animal) for animal in graduated_animals
    ]
    assert mock_update_animal_array.call_args_list == [
        call(animal) for animal in graduated_animals
    ]
    assert mock_add_animal_to_pen_and_id_map.call_args_list == [
        call(
            animal, [mock_feed], mock_current_day_conditions, mock_total_inventory
        ) for animal in graduated_animals
    ]


def test_handle_newly_added_animals(
    herd_manager: HerdManager, mocker: MockerFixture, mock_herd: dict[str, list[Animal]]
) -> None:
    mock_add_animal_to_pen_and_id_map = mocker.patch.object(herd_manager, "_add_animal_to_pen_and_id_map")

    new_animals = [
        mock_animal(animal_type=AnimalType.HEIFER_I, mocker=mocker),
        mock_animal(animal_type=AnimalType.HEIFER_II, mocker=mocker),
        mock_animal(animal_type=AnimalType.HEIFER_III, mocker=mocker),
        mock_animal(animal_type=AnimalType.LAC_COW, mocker=mocker),
    ]
    mock_feed = mocker.MagicMock(auto_spec=Feed)
    mock_current_day_conditions = mocker.MagicMock(auto_spec=CurrentDayConditions)
    mock_total_inventory = mocker.MagicMock(auto_spec=TotalInventory)

    herd_manager._handle_newly_added_animals(
        new_animals, [mock_feed], mock_current_day_conditions, mock_total_inventory
    )

    assert mock_add_animal_to_pen_and_id_map.call_args_list == [
        call(animal, [mock_feed], mock_current_day_conditions, mock_total_inventory) for animal in new_animals
    ]

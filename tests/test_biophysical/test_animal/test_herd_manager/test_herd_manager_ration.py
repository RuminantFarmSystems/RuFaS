from datetime import datetime, date, timedelta
from random import randint
from typing import Any
from unittest.mock import MagicMock, call

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.biophysical.animal.ration.calf_ration_manager import WHOLE_MILK_ID, CalfMilkType
from RUFAS.biophysical.animal.ration.user_defined_ration_manager import UserDefinedRationManager
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    Feed,
    TotalInventory,
    IdealFeeds,
    RUFAS_ID,
    RequestedFeed,
    AdvancePurchaseAllowance,
)
from RUFAS.enums import AnimalCombination
from RUFAS.rufas_time import RufasTime
from RUFAS.weather import Weather
from tests.test_biophysical.test_animal.test_herd_manager.pytest_fixtures import (
    config_json,
    animal_json,
    feed_json,
    mock_get_data_side_effect,
    mock_herd_manager,
    mock_herd,
    herd_manager,
)

assert config_json is not None
assert animal_json is not None
assert feed_json is not None
assert mock_get_data_side_effect is not None
assert mock_herd is not None
assert herd_manager is not None


def mock_available_feeds() -> list[Feed]:
    return [MagicMock(auto_spec=Feed)]


@pytest.mark.parametrize(
    "simulation_day, formulation_interval, expected",
    [
        # simulation_day == 0 scenario
        (0, 10, True),  # day=0 -> True regardless of interval
        # formulation_interval == 1 scenario
        (5, 1, True),  # interval=1 -> True for any simulation_day
        (10, 1, True),
        # simulation_day % formulation_interval == 1 scenario
        (7, 3, True),  # 7 % 3 = 1 -> True
        (1, 10, True),  # 1 % 10 = 1 -> True
        # None of the conditions met (should return False)
        (2, 2, False),  # 2 % 2 = 0, interval=2 != 1, day=2 !=0
        (10, 5, False),  # 10 % 5 = 0, interval=5 != 1, day=10 !=0
        (3, 4, False),  # 3 % 4 = 3, not 1; interval=4 != 1; day=3 !=0
    ],
)
def test_end_ration_interval(
    simulation_day: int,
    formulation_interval: int,
    expected: bool,
    mock_get_data_side_effect: list[Any],
    mocker: MockerFixture,
    mock_herd: dict[str, list[Animal]],
) -> None:
    """Unit test for end_ration_interval()."""
    herd_manager, _ = mock_herd_manager(
        calves=mock_herd["calves"],
        heiferIs=mock_herd["heiferIs"],
        heiferIIs=mock_herd["heiferIIs"],
        heiferIIIs=mock_herd["heiferIIIs"],
        cows=mock_herd["dry_cows"] + mock_herd["lac_cows"],
        replacement=mock_herd["replacement"],
        mocker=mocker,
        mock_get_data_side_effect=mock_get_data_side_effect,
    )
    herd_manager.formulation_interval = formulation_interval

    result = herd_manager.end_ration_interval(simulation_day=simulation_day)

    assert result == expected


@pytest.mark.parametrize("WHOLE_MILK_ID_in_calf_ration", [True, False])
def test_set_milk_type_in_calf_ration_manager(
    WHOLE_MILK_ID_in_calf_ration: bool, herd_manager: HerdManager, mocker: MockerFixture
) -> None:
    """Unit test for set_milk_type_in_calf_ration_manager()."""
    calf_ration = {WHOLE_MILK_ID: 0.0} if WHOLE_MILK_ID_in_calf_ration else {}
    UserDefinedRationManager.user_defined_rations = {AnimalCombination.CALF: calf_ration}

    expected_milk_type = CalfMilkType.WHOLE if WHOLE_MILK_ID_in_calf_ration else CalfMilkType.REPLACER
    info_map = {
        "class": herd_manager.__class__.__name__,
        "function": herd_manager.set_milk_type_in_calf_ration_manager.__name__,
        "milk_type": expected_milk_type.value,
        "calf_ration": calf_ration,
    }

    mock_set_milk_type = mocker.patch(
        "RUFAS.biophysical.animal.ration.calf_ration_manager.CalfRationManager.set_milk_type"
    )
    mock_om_add_log = mocker.patch.object(herd_manager.om, "add_log")

    herd_manager.set_milk_type_in_calf_ration_manager()

    mock_set_milk_type.assert_called_once_with(expected_milk_type)
    mock_om_add_log.assert_called_once_with(
        "Milk type set for calf ration",
        f"Calf requirements routines will assume 100% of calves' milk intake is {expected_milk_type.value}",
        info_map,
    )


def test_initialize_nutrient_requirements(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    """Unit test for initialize_nutrient_requirements()."""
    mock_weather, mock_time, mock_available_fees = (
        MagicMock(auto_spec=Weather),
        MagicMock(auto_spec=RufasTime),
        mock_available_feeds(),
    )

    mock_pen_set_animal_nutritional_requirements_methods = []
    for pen in herd_manager.all_pens:
        mock_pen_set_animal_nutritional_requirements_methods.append(
            mocker.patch.object(pen, "set_animal_nutritional_requirements")
        )

    herd_manager.initialize_nutrient_requirements(mock_weather, mock_time, mock_available_fees)

    for mock_function_call in mock_pen_set_animal_nutritional_requirements_methods:
        mock_function_call.assert_called_once()


def test_update_all_max_daily_feeds(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    """Unit test for end_ration_interval()."""
    dummy_rufas_ids = list(range(randint(0, 50)))
    dummy_next_harvest_dates = {rufas_id: datetime.today().date() for rufas_id in dummy_rufas_ids}
    mock_total_inventory, mock_time = MagicMock(auto_spec=TotalInventory), MagicMock(auto_spec=RufasTime)

    mock_update_single_max_daily_feed = mocker.patch.object(herd_manager, "_update_single_max_daily_feed")

    result = herd_manager.update_all_max_daily_feeds(mock_total_inventory, dummy_next_harvest_dates, mock_time)

    assert result == IdealFeeds({})
    expected_update_single_max_daily_feed_call_args_list = [
        call(rufas_id, harvest_date, mock_total_inventory, mock_time)
        for rufas_id, harvest_date in dummy_next_harvest_dates.items()
    ]
    assert mock_update_single_max_daily_feed.call_args_list == expected_update_single_max_daily_feed_call_args_list


def test_update_all_max_daily_feeds_not_simulate_animals(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    """Unit test for end_ration_interval()."""
    herd_manager.simulate_animals = False
    dummy_rufas_ids = list(range(randint(0, 50)))
    dummy_next_harvest_dates = {rufas_id: datetime.today().date() for rufas_id in dummy_rufas_ids}
    mock_total_inventory, mock_time = MagicMock(auto_spec=TotalInventory), MagicMock(auto_spec=RufasTime)

    mock_update_single_max_daily_feed = mocker.patch.object(herd_manager, "_update_single_max_daily_feed")

    result = herd_manager.update_all_max_daily_feeds(mock_total_inventory, dummy_next_harvest_dates, mock_time)

    assert result == IdealFeeds({})
    mock_update_single_max_daily_feed.assert_not_called()


@pytest.mark.parametrize(
    "rufas_id, current_date, next_harvest_date, available_amount, expected_max_daily_amount",
    [
        (123, datetime.today(), datetime.today().date() + timedelta(days=5), 10.8, 0.11368421052631579),
        (108, datetime.today(), datetime.today().date() + timedelta(days=45), 23.3, 0.027251461988304096),
        (88, datetime.today(), datetime.today().date() + timedelta(days=1085), 1237, 0.06000485083676935),
        (65, datetime.today(), datetime.today().date() + timedelta(days=10), 24.88, 0.13094736842105265),
        (48, datetime.today(), datetime.today().date() + timedelta(days=2), 97324, 2561.157894736842),
    ],
)
def test_update_single_max_daily_feed(
    rufas_id: RUFAS_ID,
    current_date: datetime,
    next_harvest_date: date,
    available_amount: float,
    expected_max_daily_amount: float,
    herd_manager: HerdManager,
) -> None:
    """Unit test for _update_single_max_daily_feed()."""
    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.current_date = current_date

    mock_total_inventory = MagicMock(auto_spec=TotalInventory)
    mock_total_inventory.available_feeds = {rufas_id: available_amount}

    herd_manager._update_single_max_daily_feed(rufas_id, next_harvest_date, mock_total_inventory, mock_time)

    assert herd_manager._max_daily_feeds[rufas_id] == pytest.approx(expected_max_daily_amount)


def test_formulate_rations(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    """Unit test for formulate_rations()."""
    available_feeds, current_temperature, ration_interval_length, mock_total_inventory = (
        mock_available_feeds(),
        30,
        30,
        MagicMock(auto_spec=TotalInventory),
    )
    mock_time = mocker.MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 15

    mock_clear_pens = mocker.patch.object(herd_manager, "clear_pens")
    mock_allocate_animals_to_pens = mocker.patch.object(herd_manager, "allocate_animals_to_pens")
    mock_reformulate_ration_single_pen = mocker.patch.object(herd_manager, "_reformulate_ration_single_pen")

    mock_pen_get_requested_feed = [
        mocker.patch.object(pen, "get_requested_feed", return_value=RequestedFeed({})) for pen in herd_manager.all_pens
    ]

    result = herd_manager.formulate_rations(
        available_feeds, current_temperature, ration_interval_length, mock_total_inventory, mock_time.simulation_day
    )

    assert result == RequestedFeed({})

    mock_clear_pens.assert_called_once_with()
    mock_allocate_animals_to_pens.assert_called_once_with(mock_time.simulation_day)

    expected_reformulate_ration_single_pen_call_args_list = [
        call(pen, available_feeds, current_temperature, mock_total_inventory) for pen in herd_manager.all_pens
    ]
    assert mock_reformulate_ration_single_pen.call_args_list == expected_reformulate_ration_single_pen_call_args_list

    for mock_method in mock_pen_get_requested_feed:
        mock_method.assert_called_once_with(ration_interval_length)


def test_formulate_rations_not_simulate_animals(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    """Unit test for formulate_rations()."""
    herd_manager.simulate_animals = False
    available_feeds, current_temperature, ration_interval_length, mock_total_inventory = (
        mock_available_feeds(),
        30,
        30,
        MagicMock(auto_spec=TotalInventory),
    )

    mock_clear_pens = mocker.patch.object(herd_manager, "clear_pens")
    mock_allocate_animals_to_pens = mocker.patch.object(herd_manager, "allocate_animals_to_pens")
    mock_reformulate_ration_single_pen = mocker.patch.object(herd_manager, "_reformulate_ration_single_pen")
    mock_time = mocker.MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 15

    mock_pen_get_requested_feed = [
        mocker.patch.object(pen, "get_requested_feed", return_value=RequestedFeed({})) for pen in herd_manager.all_pens
    ]

    result = herd_manager.formulate_rations(
        available_feeds, current_temperature, ration_interval_length, mock_total_inventory, mock_time.simulation_day
    )

    assert result == RequestedFeed({})

    mock_clear_pens.assert_not_called()
    mock_allocate_animals_to_pens.assert_not_called()
    mock_reformulate_ration_single_pen.assert_not_called()

    for mock_method in mock_pen_get_requested_feed:
        mock_method.assert_not_called()


def test_formulate_rations_empty_pen(herd_manager: HerdManager, mocker: MockerFixture) -> None:
    """Unit test for formulate_rations()."""
    mocker.patch.object(Pen, "is_populated", new_callable=mocker.PropertyMock, return_value=False)

    available_feeds, current_temperature, ration_interval_length, mock_total_inventory = (
        mock_available_feeds(),
        30,
        30,
        MagicMock(auto_spec=TotalInventory),
    )

    mock_clear_pens = mocker.patch.object(herd_manager, "clear_pens")
    mock_allocate_animals_to_pens = mocker.patch.object(herd_manager, "allocate_animals_to_pens")
    mock_reformulate_ration_single_pen = mocker.patch.object(herd_manager, "_reformulate_ration_single_pen")
    mock_time = mocker.MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 15

    mock_pen_get_requested_feed = [
        mocker.patch.object(pen, "get_requested_feed", return_value=RequestedFeed({})) for pen in herd_manager.all_pens
    ]

    result = herd_manager.formulate_rations(
        available_feeds, current_temperature, ration_interval_length, mock_total_inventory, mock_time.simulation_day
    )

    assert result == RequestedFeed({})

    mock_clear_pens.assert_called_once_with()
    mock_allocate_animals_to_pens.assert_called_once_with(mock_time.simulation_day)

    mock_reformulate_ration_single_pen.assert_not_called()

    for mock_method in mock_pen_get_requested_feed:
        mock_method.assert_not_called()
    for pen in herd_manager.all_pens:
        assert pen.ration == {}


@pytest.mark.parametrize("use_user_defined_ration", [True, False])
def test_reformulate_ration_single_pen(
    use_user_defined_ration: bool, herd_manager: HerdManager, mocker: MockerFixture
) -> None:
    """Unit test for _reformulate_ration_single_pen()."""
    mock_pen, available_feeds, current_temperature, mock_total_inventory = (
        MagicMock(auto_spec=Pen),
        mock_available_feeds(),
        30,
        MagicMock(auto_spec=TotalInventory),
    )
    mock_use_user_defined_ration = mocker.patch.object(mock_pen, "use_user_defined_ration")
    mock_formulate_optimized_ration = mocker.patch.object(mock_pen, "formulate_optimized_ration")

    herd_manager.is_ration_defined_by_user = use_user_defined_ration
    herd_manager._max_daily_feeds = {}
    herd_manager.advance_purchase_allowance = MagicMock(auto_spec=AdvancePurchaseAllowance)
    herd_manager._reformulate_ration_single_pen(mock_pen, available_feeds, current_temperature, mock_total_inventory)

    if use_user_defined_ration:
        mock_use_user_defined_ration.assert_called_once_with(available_feeds, current_temperature)
        mock_formulate_optimized_ration.assert_not_called()
    else:
        mock_use_user_defined_ration.assert_not_called()
        mock_formulate_optimized_ration.assert_called_once_with(
            available_feeds,
            herd_manager._max_daily_feeds,
            herd_manager.advance_purchase_allowance,
            mock_total_inventory,
        )

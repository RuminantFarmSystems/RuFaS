from datetime import datetime, date, timedelta
from random import randint
from typing import Any
from unittest.mock import MagicMock, call

from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionSupply
import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.biophysical.animal.ration.calf_ration_manager import WHOLE_MILK_ID, CalfMilkType
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    Feed,
    TotalInventory,
    IdealFeeds,
    RUFAS_ID,
    RequestedFeed,
    AdvancePurchaseAllowance,
)
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
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


@pytest.mark.parametrize(
    "is_ration_defined_by_user, WHOLE_MILK_ID_in_calf_ration",
    [
        (True, True),  # uses user_defined_rations, contains WHOLE_MILK_ID
        (True, False),  # uses user_defined_rations, does NOT contain WHOLE_MILK_ID
        (False, True),  # uses ration_feeds, contains WHOLE_MILK_ID (hits the else branch)
        (False, False),  # uses ration_feeds, does NOT contain WHOLE_MILK_ID (else branch)
    ],
)
def test_set_milk_type_in_calf_ration_manager(
    is_ration_defined_by_user: bool,
    WHOLE_MILK_ID_in_calf_ration: bool,
    herd_manager: HerdManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for set_milk_type_in_calf_ration_manager()."""
    herd_manager.is_ration_defined_by_user = is_ration_defined_by_user

    if is_ration_defined_by_user:
        calf_ration = {WHOLE_MILK_ID: 0.0} if WHOLE_MILK_ID_in_calf_ration else {}
        calf_feeds = list(calf_ration.keys())
        RationManager.user_defined_rations = {AnimalCombination.CALF: calf_ration}
        RationManager.ration_feeds = {AnimalCombination.CALF: []}
    else:
        calf_feeds = [WHOLE_MILK_ID] if WHOLE_MILK_ID_in_calf_ration else []
        RationManager.ration_feeds = {AnimalCombination.CALF: calf_feeds}
        RationManager.user_defined_rations = {AnimalCombination.CALF: {}}

    expected_milk_type = CalfMilkType.WHOLE if WHOLE_MILK_ID_in_calf_ration else CalfMilkType.REPLACER

    expected_info_map = {
        "class": herd_manager.__class__.__name__,
        "function": herd_manager.set_milk_type_in_calf_ration_manager.__name__,
        "milk_type": expected_milk_type.value,
        "calf_feeds": calf_feeds,
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
        expected_info_map,
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


@pytest.mark.parametrize("is_ration_defined_by_user", [True, False])
def test_formulate_rations(
    is_ration_defined_by_user: bool,
    herd_manager: HerdManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for formulate_rations() when animals are simulated and pens may be populated."""
    available_feeds, current_temperature, ration_interval_length, mock_total_inventory = (
        mock_available_feeds(),
        30,
        30,
        MagicMock(auto_spec=TotalInventory),
    )
    mock_time = mocker.MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 15

    herd_manager.simulate_animals = True
    herd_manager.is_ration_defined_by_user = is_ration_defined_by_user

    mock_clear_pens = mocker.patch.object(herd_manager, "clear_pens")
    mock_allocate_animals_to_pens = mocker.patch.object(herd_manager, "allocate_animals_to_pens")
    mock_reformulate_ration_single_pen = mocker.patch.object(herd_manager, "_reformulate_ration_single_pen")

    mock_pen_get_requested_feed = [
        mocker.patch.object(pen, "get_requested_feed", return_value=RequestedFeed({})) for pen in herd_manager.all_pens
    ]

    mock_ration_feed_ids = mocker.sentinel.ration_feed_ids

    if is_ration_defined_by_user:
        mock_get_user_defined = mocker.patch.object(
            RationManager, "get_user_defined_ration_feeds", return_value=mock_ration_feed_ids
        )
        mock_get_default = mocker.patch.object(RationManager, "get_ration_feeds")
    else:
        mock_get_user_defined = mocker.patch.object(RationManager, "get_user_defined_ration_feeds")
        mock_get_default = mocker.patch.object(RationManager, "get_ration_feeds", return_value=mock_ration_feed_ids)

    mocker.patch.object(herd_manager, "_find_pen_available_feeds", return_value=available_feeds)

    result = herd_manager.formulate_rations(
        available_feeds,
        current_temperature,
        ration_interval_length,
        mock_total_inventory,
        mock_time.simulation_day,
    )

    assert result == RequestedFeed({})

    mock_clear_pens.assert_called_once_with()
    mock_allocate_animals_to_pens.assert_called_once_with(mock_time.simulation_day)

    expected_reformulate_ration_single_pen_call_args_list = [
        call(pen, available_feeds, current_temperature, mock_total_inventory, 15) for pen in herd_manager.all_pens
    ]
    assert mock_reformulate_ration_single_pen.call_args_list == expected_reformulate_ration_single_pen_call_args_list

    for mock_method in mock_pen_get_requested_feed:
        mock_method.assert_called_once_with(ration_interval_length)

    if is_ration_defined_by_user:
        assert mock_get_user_defined.call_count == len(herd_manager.all_pens)
        mock_get_default.assert_not_called()
    else:
        assert mock_get_default.call_count == len(herd_manager.all_pens)
        mock_get_user_defined.assert_not_called()


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
    mock_formulate_optimized_ration = mocker.patch.object(mock_pen, "formulate_optimized_ration")

    herd_manager.is_ration_defined_by_user = use_user_defined_ration
    herd_manager._max_daily_feeds = {}
    herd_manager.advance_purchase_allowance = MagicMock(auto_spec=AdvancePurchaseAllowance)
    herd_manager._reformulate_ration_single_pen(
        mock_pen, available_feeds, current_temperature, mock_total_inventory, 15
    )

    if use_user_defined_ration:
        mock_formulate_optimized_ration.assert_called_once_with(
            True,
            available_feeds,
            current_temperature,
            herd_manager._max_daily_feeds,
            herd_manager.advance_purchase_allowance,
            mock_total_inventory,
            15,
        )
    else:
        mock_formulate_optimized_ration.assert_called_once_with(
            False,
            available_feeds,
            current_temperature,
            herd_manager._max_daily_feeds,
            herd_manager.advance_purchase_allowance,
            mock_total_inventory,
            15,
        )


def test_report_ration_reports_per_pen_and_herd_total(mocker: MockerFixture) -> None:
    """_report_ration should report each pen's totals and the aggregated herd ration."""
    simulation_day = 7

    herd_manager = mocker.MagicMock(spec=HerdManager)

    pen1 = mocker.MagicMock()
    pen1.id = 1
    pen1.animal_combination = mocker.MagicMock()
    pen1.animal_combination.name = "CALF"
    pen1.animals_in_pen = ["a1", "a2", "a3"]
    pen1.total_pen_ration = {
        "corn_silage": 10.0,
        "alfalfa_hay": 5.0,
    }

    pen2 = mocker.MagicMock()
    pen2.id = 2
    pen2.animal_combination = mocker.MagicMock()
    pen2.animal_combination.name = "COW"
    pen2.animals_in_pen = ["b1", "b2"]
    pen2.total_pen_ration = {
        "corn_silage": 20.0,
        "grass_hay": 3.0,
    }

    herd_manager.all_pens = [pen1, pen2]

    mock_report_pen_total = mocker.patch.object(AnimalModuleReporter, "report_daily_pen_total")
    mock_report_ration_per_pen = mocker.patch.object(AnimalModuleReporter, "report_daily_ration_per_pen")
    mock_report_herd_total = mocker.patch.object(AnimalModuleReporter, "report_daily_herd_total_ration")

    HerdManager._report_ration(herd_manager, simulation_day)

    assert mock_report_pen_total.call_args_list == [
        mocker.call(str(pen1.id), pen1.animal_combination.name, len(pen1.animals_in_pen), simulation_day),
        mocker.call(str(pen2.id), pen2.animal_combination.name, len(pen2.animals_in_pen), simulation_day),
    ]

    assert mock_report_ration_per_pen.call_args_list == [
        mocker.call(str(pen1.id), pen1.animal_combination.name, pen1.total_pen_ration, simulation_day),
        mocker.call(str(pen2.id), pen2.animal_combination.name, pen2.total_pen_ration, simulation_day),
    ]

    expected_herd_total_ration = {
        "corn_silage": 10.0 + 20.0,
        "alfalfa_hay": 5.0,
        "grass_hay": 3.0,
    }

    mock_report_herd_total.assert_called_once_with(expected_herd_total_ration, simulation_day)


def test_report_ration_interval_data(
    herd_manager: HerdManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for report_ration_interval_data() using mocked NutritionSupply."""

    simulation_day = 42
    pen_unpopulated = mocker.MagicMock(auto_spec=Pen)
    pen_unpopulated.is_populated = False

    pen_calf = mocker.MagicMock(auto_spec=Pen)
    pen_calf.is_populated = True
    pen_calf.animal_combination = AnimalCombination.CALF
    pen_calf.id = 1
    pen_calf.ration = {"feed1": 1.0}
    pen_calf.animals_in_pen = {"a": object(), "b": object()}

    calf_supply = mocker.MagicMock(auto_spec=NutritionSupply)
    calf_supply.dry_matter = 10.0
    calf_supply.metabolizable_energy = 20.0
    pen_calf.average_nutrition_supply = calf_supply

    pen_lac_cow = mocker.MagicMock(auto_spec=Pen)
    pen_lac_cow.is_populated = True
    pen_lac_cow.animal_combination = AnimalCombination.LAC_COW
    pen_lac_cow.id = 2
    pen_lac_cow.ration = {"feed2": 2.0}
    pen_lac_cow.animals_in_pen = {"c": object()}

    lac_cow_supply = mocker.MagicMock(auto_spec=NutritionSupply)
    lac_cow_supply.dry_matter = 15.0
    lac_cow_supply.metabolizable_energy = 25.0
    pen_lac_cow.average_nutrition_supply = lac_cow_supply

    pen_lac_cow.average_nutrition_requirements = mocker.sentinel.requirements
    pen_lac_cow.average_body_weight = 650.0
    pen_lac_cow.average_milk_production_reduction = 0.1
    pen_lac_cow.average_nutrition_evaluation = mocker.sentinel.evaluation

    herd_manager.all_pens = [pen_unpopulated, pen_calf, pen_lac_cow]

    mock_report_ration_per_animal = mocker.patch.object(AnimalModuleReporter, "report_ration_per_animal")
    mock_report_nutrient_amounts = mocker.patch.object(AnimalModuleReporter, "report_nutrient_amounts")
    mock_report_me_diet = mocker.patch.object(AnimalModuleReporter, "report_me_diet")
    mock_report_avg_reqs = mocker.patch.object(AnimalModuleReporter, "report_average_nutrient_requirements")
    mock_report_avg_eval = mocker.patch.object(AnimalModuleReporter, "report_average_nutrient_evaluation_results")

    herd_manager.report_ration_interval_data(simulation_day)

    calf_base_name = f"{AnimalCombination.CALF.name}_PEN_{pen_calf.id}"
    lac_cow_base_name = f"{AnimalCombination.LAC_COW.name}_PEN_{pen_lac_cow.id}"

    assert mock_report_ration_per_animal.call_args_list == [
        mocker.call(
            calf_base_name,
            pen_calf.ration,
            calf_supply.dry_matter,
            len(pen_calf.animals_in_pen),
            simulation_day,
        ),
        mocker.call(
            lac_cow_base_name,
            pen_lac_cow.ration,
            lac_cow_supply.dry_matter,
            len(pen_lac_cow.animals_in_pen),
            simulation_day,
        ),
    ]

    assert mock_report_nutrient_amounts.call_args_list == [
        mocker.call(
            calf_base_name,
            calf_supply,
            len(pen_calf.animals_in_pen),
            simulation_day,
        ),
        mocker.call(
            lac_cow_base_name,
            lac_cow_supply,
            len(pen_lac_cow.animals_in_pen),
            simulation_day,
        ),
    ]

    assert mock_report_me_diet.call_args_list == [
        mocker.call(
            calf_base_name,
            calf_supply.metabolizable_energy,
            len(pen_calf.animals_in_pen),
            simulation_day,
        ),
        mocker.call(
            lac_cow_base_name,
            lac_cow_supply.metabolizable_energy,
            len(pen_lac_cow.animals_in_pen),
            simulation_day,
        ),
    ]

    mock_report_avg_reqs.assert_called_once_with(
        lac_cow_base_name,
        pen_lac_cow.average_nutrition_requirements,
        pen_lac_cow.average_body_weight,
        pen_lac_cow.average_milk_production_reduction,
        len(pen_lac_cow.animals_in_pen),
        simulation_day,
    )

    mock_report_avg_eval.assert_called_once_with(
        lac_cow_base_name,
        pen_lac_cow.average_nutrition_evaluation,
        simulation_day,
    )


def test_reformulate_ration_single_pen_lac_cow_zero_milk_updates_animals(
    herd_manager: HerdManager,
    mocker: MockerFixture,
) -> None:
    """If LAC_COW with zero milk, all animals get daily_milking_update_without_history before ration formulation."""
    pen = mocker.MagicMock(auto_spec=Pen)
    pen.animal_combination = AnimalCombination.LAC_COW
    pen.average_milk_production = 0.0

    animal1 = mocker.MagicMock()
    animal2 = mocker.MagicMock()
    pen.animals_in_pen = {"a1": animal1, "a2": animal2}

    pen_available_feeds = mock_available_feeds()
    current_temperature = 30.0
    total_inventory = mocker.MagicMock(auto_spec=TotalInventory)
    simulation_day = 15

    herd_manager.is_ration_defined_by_user = True
    herd_manager._max_daily_feeds = {}
    herd_manager.advance_purchase_allowance = mocker.MagicMock(auto_spec=AdvancePurchaseAllowance)

    mock_formulate_optimized_ration = mocker.patch.object(pen, "formulate_optimized_ration")

    herd_manager._reformulate_ration_single_pen(
        pen,
        pen_available_feeds,
        current_temperature,
        total_inventory,
        simulation_day,
    )

    animal1.daily_milking_update_without_history.assert_called_once_with()
    animal2.daily_milking_update_without_history.assert_called_once_with()

    mock_formulate_optimized_ration.assert_called_once_with(
        herd_manager.is_ration_defined_by_user,
        pen_available_feeds,
        current_temperature,
        herd_manager._max_daily_feeds,
        herd_manager.advance_purchase_allowance,
        total_inventory,
        simulation_day,
    )


@pytest.mark.parametrize("is_ration_defined_by_user", [True, False])
def test_reformulate_ration_single_pen_calf_branch(
    is_ration_defined_by_user: bool,
    herd_manager: HerdManager,
    mocker: MockerFixture,
) -> None:
    """
    For CALF pens, use_user_defined_ration is always called.
    If rations are not user-defined, user_defined_rations[CALF] is created from available feeds.
    """
    pen = mocker.MagicMock(auto_spec=Pen)
    pen.animal_combination = AnimalCombination.CALF

    pen_available_feeds = mock_available_feeds()
    current_temperature = 30.0
    total_inventory = mocker.MagicMock(auto_spec=TotalInventory)
    simulation_day = 15

    herd_manager.is_ration_defined_by_user = is_ration_defined_by_user
    herd_manager._max_daily_feeds = {}
    herd_manager.advance_purchase_allowance = mocker.MagicMock(auto_spec=AdvancePurchaseAllowance)

    mock_use_user_defined_ration = mocker.patch.object(pen, "use_user_defined_ration")
    mock_formulate_optimized_ration = mocker.patch.object(pen, "formulate_optimized_ration")

    if is_ration_defined_by_user:
        RationManager.user_defined_rations = {AnimalCombination.CALF: {1: 1.0}}
    else:
        RationManager.user_defined_rations = {}

    herd_manager._reformulate_ration_single_pen(
        pen,
        pen_available_feeds,
        current_temperature,
        total_inventory,
        simulation_day,
    )

    mock_formulate_optimized_ration.assert_not_called()

    mock_use_user_defined_ration.assert_called_once_with(pen_available_feeds, current_temperature)

    if not is_ration_defined_by_user:
        ration_fraction = 100 / len(pen_available_feeds)
        expected_ration = {feed.rufas_id: ration_fraction for feed in pen_available_feeds}
        assert RationManager.user_defined_rations == {AnimalCombination.CALF: expected_ration}
    else:
        assert RationManager.user_defined_rations == {AnimalCombination.CALF: {1: 1.0}}

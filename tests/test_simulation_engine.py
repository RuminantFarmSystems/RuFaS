from datetime import datetime, timedelta

from RUFAS.EEE.emissions import EmissionsEstimator
import pytest
from unittest.mock import MagicMock, call

from pytest_mock import MockerFixture

from RUFAS.EEE.EEE_manager import EEEManager
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.biophysical.feed_storage.feed_manager import FeedManager
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.data_structures.events import ManureEvent
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    TotalInventory,
    IdealFeeds,
    RequestedFeed,
    NutrientStandard,
)
from RUFAS.data_structures.manure_supplement_methods import ManureSupplementMethod
from RUFAS.data_structures.manure_to_crop_soil_connection import (
    ManureEventNutrientRequestResults,
    NutrientRequestResults,
    ManureEventNutrientRequest,
)
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import (
    HarvestedCrop,
)
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.field.field.field import Field
from RUFAS.biophysical.field.field.manure_application import ManureApplication
from RUFAS.biophysical.field.manager.field_manager import FieldManager
from RUFAS.biophysical.manure.manure_manager import ManureManager
from RUFAS.simulation_engine import SimulationEngine
from RUFAS.rufas_time import RufasTime
from RUFAS.weather import Weather


@pytest.fixture
def simulation_engine(mocker: MockerFixture) -> SimulationEngine:
    mocker.patch("RUFAS.simulation_engine.RufasTime")
    mocker.patch("RUFAS.simulation_engine.SimulationEngine._initialize_simulation")

    simulation_engine = SimulationEngine()

    simulation_engine.herd_manager = MagicMock(auto_spec=HerdManager)
    simulation_engine.manure_manager = MagicMock(auto_spec=ManureManager)
    simulation_engine.field_manager = MagicMock(auto_spec=FieldManager)
    simulation_engine.feed_manager = MagicMock(auto_spec=FeedManager)
    simulation_engine.emissions_estimator = MagicMock(auto_spec=EmissionsEstimator)

    return simulation_engine


def test_simulation_engine_init(mocker: MockerFixture) -> None:
    """
    Unit test for the __init__ method in the SimulationEngine class.
    """

    # Arrange
    mock_initialize_simulation = mocker.patch.object(SimulationEngine, "_initialize_simulation")
    mock_time = mocker.MagicMock(auto_spec=RufasTime)
    mocker.patch("RUFAS.simulation_engine.RufasTime", return_value=mock_time)

    # Act
    simulation_engine = SimulationEngine()

    # Assert
    mock_initialize_simulation.assert_called_once()
    assert simulation_engine.time == mock_time


@pytest.mark.parametrize("start_time, end_time", [(100, 200), (300, 400)])
def test_simulate(
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
    start_time: int,
    end_time: int,
) -> None:
    """
    Unit test for function simulate() in file RUFAS/simulation_engine.py
    """
    # Arrange
    mocker.patch("RUFAS.simulation_engine.timer.time", side_effect=[start_time, end_time])
    mock_estimate_emissions = mocker.patch.object(EEEManager, "estimate_all")
    mock_run_simulation_main_loop = mocker.patch.object(simulation_engine, "_run_simulation_main_loop")
    mock_report_end_of_simulation = mocker.patch(
        "RUFAS.biophysical.animal.animal_module_reporter.AnimalModuleReporter" ".report_end_of_simulation"
    )
    mocker.patch("RUFAS.output_manager.OutputManager.add_variable")
    mock_om_add_log = mocker.patch("RUFAS.output_manager.OutputManager.add_log")

    mock_time = MagicMock(auto_spec=RufasTime)
    mock_time.simulation_day = 100
    simulation_engine.time = mock_time

    info_map = {
        "class": simulation_engine.__class__.__name__,
        "function": simulation_engine.simulate.__name__,
    }
    expected_simulation_time = end_time - start_time
    expected_log_message = f"Total simulation time is: {expected_simulation_time}"

    # Act
    simulation_engine.simulate()

    # Assert
    mock_run_simulation_main_loop.assert_called_once()
    assert mock_om_add_log.call_args_list == [
        call("Simulation complete", "Simulation Completed.", info_map),
        call("total_simulation_time", expected_log_message, info_map),
    ]
    mock_report_end_of_simulation.assert_called_once_with(
        simulation_engine.herd_manager.herd_statistics,
        simulation_engine.herd_manager.herd_reproduction_statistics,
        simulation_engine.time,
        simulation_engine.herd_manager.heiferII_events_by_id,
        simulation_engine.herd_manager.cow_events_by_id,
    )

    mock_estimate_emissions.assert_called_once()


@pytest.mark.parametrize(
    "is_time_to_recalculate_max_daily_feeds, is_time_to_reformulate_ration," "is_ok_to_feed_animals",
    [
        (True, True, True),
        (True, True, False),
        (True, False, True),
        (True, False, False),
        (False, True, True),
        (False, True, False),
        (False, False, True),
        (False, False, False),
    ],
)
def test_daily_simulation(
    is_time_to_recalculate_max_daily_feeds: bool,
    is_time_to_reformulate_ration: bool,
    is_ok_to_feed_animals: bool,
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for function _daily_simulation in file RUFAS/simulation_engine.py
    """
    # Arrange
    simulation_engine.simulate_animals = True
    simulation_engine.time = (mock_time := MagicMock(auto_spec=RufasTime))
    simulation_engine.weather = (mock_weather := MagicMock(auto_spec=Weather))
    mock_weather_get_current_day_conditions = mocker.patch.object(
        mock_weather,
        "get_current_day_conditions",
        return_value=(mock_current_day_conditions := MagicMock(auto_spec=CurrentDayConditions)),
    )
    simulation_engine.time.current_date = datetime.today()
    simulation_engine.time.simulation_day = 15
    simulation_engine.next_max_daily_feed_recalculation = (
        simulation_engine.time.current_date
        if is_time_to_recalculate_max_daily_feeds
        else simulation_engine.time.current_date + timedelta(days=1)
    )
    simulation_engine.max_daily_feed_recalculation_interval = timedelta(days=round(365 / 4))
    simulation_engine.next_ration_reformulation = (
        simulation_engine.time.current_date.date()
        if is_time_to_reformulate_ration
        else (simulation_engine.time.current_date + timedelta(days=1)).date()
    )

    simulation_engine.feed_manager.crop_to_rufas_id = {"crop_1": 1, "crop_2": 2, "crop_3": 3, "crop_4": 4}

    mock_generate_daily_manure_applications = mocker.patch.object(
        simulation_engine,
        "generate_daily_manure_applications",
        return_value=(mock_manure_applications := [MagicMock(auto_spec=ManureApplication)]),
    )
    mock_formulate_ration = mocker.patch.object(simulation_engine, "_formulate_ration")
    mock_advance_time = mocker.patch.object(simulation_engine, "_advance_time")

    crop_1, crop_2 = MagicMock(auto_spec=HarvestedCrop), MagicMock(auto_spec=HarvestedCrop)
    crop_1.config_name, crop_2.config_name = "crop_1", "crop_2"
    mock_field_daily_update_routine = mocker.patch.object(
        simulation_engine.field_manager,
        "daily_update_routine",
        return_value=(mock_harvested_crops := [crop_1, crop_2]),
    )
    expected_harvested_crops_config_names = [[harvest_crop.config_name] for harvest_crop in mock_harvested_crops]
    mock_field_receive_crop = mocker.patch.object(simulation_engine.feed_manager, "receive_crop")
    mock_field_get_next_harvest_dates = mocker.patch.object(
        simulation_engine.field_manager,
        "get_next_harvest_dates",
        side_effect=lambda crop_config_name: {crop_config_name[0]: datetime.today().date()},
    )

    mock_feed_get_total_inventory = mocker.patch.object(
        simulation_engine.feed_manager,
        "get_total_projected_inventory",
        return_value=(mock_total_inventory := MagicMock(auto_spec=TotalInventory)),
    )
    mock_feed_translate_crop_config_name_to_rufas_id = mocker.patch.object(
        simulation_engine.feed_manager,
        "translate_crop_config_name_to_rufas_id",
        return_value=(
            mock_next_harvest_dates_with_rufas_ids := {1: datetime.today().date(), 2: datetime.today().date()}
        ),
    )
    mock_feed_manage_planning_cycle_purchases = mocker.patch.object(
        simulation_engine.feed_manager, "manage_planning_cycle_purchases"
    )
    mock_feed_manage_daily_feed_request = mocker.patch.object(
        simulation_engine.feed_manager,
        "manage_daily_feed_request",
        return_value=(is_ok_to_feed_animals, {"purchased": {}}),
    )

    mock_herd_update_all_max_daily_feeds = mocker.patch.object(
        simulation_engine.herd_manager,
        "update_all_max_daily_feeds",
        return_value=(mock_ideal_feeds_to_purchase := MagicMock(auto_spec=IdealFeeds)),
    )
    mock_herd_collect_daily_feed_request = mocker.patch.object(
        simulation_engine.herd_manager,
        "collect_daily_feed_request",
        return_value=(mock_requested_feed := MagicMock(auto_spec=RequestedFeed)),
    )
    mock_herd_daily_routines = mocker.patch.object(
        simulation_engine.herd_manager,
        "daily_routines",
        return_value=(
            mock_manure_streams := {
                "stream_1": MagicMock(auto_spec=ManureStream),
                "stream_2": MagicMock(auto_spec=ManureStream),
            }
        ),
    )

    mock_manure_daily_update = mocker.patch.object(simulation_engine.manure_manager, "run_daily_update")

    mock_om_add_warning = mocker.patch("RUFAS.output_manager.OutputManager.add_warning")
    mock_record_time = mocker.patch.object(mock_time, "record_time")
    mock_record_weather = mocker.patch.object(mock_weather, "record_weather")
    mocker.patch.object(simulation_engine.feed_manager, "report_feed_storage_levels")
    mocker.patch.object(simulation_engine.feed_manager, "report_cumulative_purchased_feeds")
    mock_calc_emissions = mocker.patch.object(
        simulation_engine.emissions_estimator, "calculate_purchased_feed_emissions"
    )
    mock_report_cumulative_purchased_feeds = mocker.patch.object(
        simulation_engine.feed_manager, "report_cumulative_purchased_feeds"
    )
    mock_report_feed_storage_levels = mocker.patch.object(simulation_engine.feed_manager, "report_feed_storage_levels")

    # Act
    simulation_engine._daily_simulation()

    # Assert
    mock_generate_daily_manure_applications.assert_called_once_with()
    mock_weather_get_current_day_conditions.assert_called_once_with(mock_time)
    mock_field_daily_update_routine.assert_called_once_with(mock_weather, mock_time, mock_manure_applications)
    assert mock_field_receive_crop.call_args_list == [
        call(harvested_crop, simulation_engine.time.simulation_day) for harvested_crop in mock_harvested_crops
    ]

    not_harvested_feeds_config_names = [
        config_name
        for config_name in simulation_engine.feed_manager.crop_to_rufas_id.keys()
        if config_name not in [harvested_crop[0] for harvested_crop in expected_harvested_crops_config_names]
    ]
    if is_time_to_recalculate_max_daily_feeds:
        expected_harvested_crops_config_names.append(not_harvested_feeds_config_names)
    assert mock_field_get_next_harvest_dates.call_args_list == [
        call(names) for names in expected_harvested_crops_config_names
    ]

    assert (
        mock_feed_get_total_inventory.call_args_list
        == [call(mock_time.current_date.date(), mock_weather, mock_time)] * 2
    )
    mock_feed_translate_crop_config_name_to_rufas_id.assert_called_once()
    mock_herd_update_all_max_daily_feeds.assert_called_once_with(
        mock_total_inventory, mock_next_harvest_dates_with_rufas_ids, mock_time
    )
    mock_feed_manage_planning_cycle_purchases.assert_called_once_with(mock_ideal_feeds_to_purchase, mock_time)

    expected_formulate_ration_call_args = []
    if is_time_to_reformulate_ration:
        expected_formulate_ration_call_args.append(call())
    if not is_ok_to_feed_animals:
        expected_formulate_ration_call_args.append(call())
        mock_om_add_warning.assert_called_once_with(
            "Value: not enough feed for the herd",
            "Reformulating ration for all pens",
            {"class": simulation_engine.__class__.__name__, "function": simulation_engine._daily_simulation.__name__},
        )
    assert mock_formulate_ration.call_args_list == expected_formulate_ration_call_args

    mock_herd_collect_daily_feed_request.assert_called_once_with()
    mock_feed_manage_daily_feed_request.assert_called_once_with(mock_requested_feed, mock_time)
    mock_herd_daily_routines.assert_called_once_with(
        simulation_engine.feed_manager.available_feeds, mock_time, mock_weather, mock_total_inventory
    )
    mock_manure_daily_update.assert_called_once_with(mock_manure_streams, mock_time, mock_current_day_conditions)
    mock_record_time.assert_called_once_with()
    mock_record_weather.assert_called_once_with(mock_time)
    mock_advance_time.assert_called_once_with()
    mock_report_feed_storage_levels.assert_called_once_with(
        simulation_engine.time.simulation_day, "daily_storage_levels"
    )
    mock_report_cumulative_purchased_feeds.assert_called_once_with(simulation_engine.time.simulation_day)
    mock_calc_emissions.assert_called_once_with({})


@pytest.mark.parametrize(
    "ration_formulation_interval_length, number_of_pens",
    [
        (30, 4),
        (30, 10),
        (50, 7),
    ],
)
def test_formulate_ration(
    ration_formulation_interval_length: int,
    number_of_pens: int,
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for function _formulate_ration() in file RUFAS/simulation_engine.py
    """
    simulation_engine.time = (mock_time := MagicMock(auto_spec=RufasTime))
    simulation_engine.weather = (mock_weather := MagicMock(auto_spec=Weather))
    simulation_engine.herd_manager.all_pens = [MagicMock(auto_spec=Pen) for _ in range(number_of_pens)]

    mock_time.current_date = datetime.today()
    simulation_engine.ration_formulation_interval_length = timedelta(days=ration_formulation_interval_length)
    expected_next_ration_formulation_date = (
        datetime.today() + timedelta(days=ration_formulation_interval_length)
    ).date()

    mock_feed_process_degradations = mocker.patch.object(simulation_engine.feed_manager, "process_degradations")
    mock_feed_get_total_inventory = mocker.patch.object(
        simulation_engine.feed_manager,
        "get_total_projected_inventory",
        return_value=(mock_total_inventory := MagicMock(auto_spec=TotalInventory)),
    )
    mock_weather_get_current_day_conditions = mocker.patch.object(
        mock_weather,
        "get_current_day_conditions",
        return_value=(mock_current_day_conditions := MagicMock(auto_spec=CurrentDayConditions)),
    )
    mock_herd_formulate_rations = mocker.patch.object(
        simulation_engine.herd_manager,
        "formulate_rations",
        return_value=(mock_requested_feed := MagicMock(auto_spec=RequestedFeed)),
    )
    mock_feed_manage_ration_interval_purchases = mocker.patch.object(
        simulation_engine.feed_manager, "manage_ration_interval_purchases"
    )
    mock_report_ration_interval_data = mocker.patch.object(
        simulation_engine.herd_manager, "report_ration_interval_data"
    )

    simulation_engine._formulate_ration()

    mock_feed_process_degradations.assert_called_once_with(mock_weather, mock_time)
    assert simulation_engine.next_ration_reformulation == expected_next_ration_formulation_date
    mock_feed_get_total_inventory.assert_called_once_with(
        simulation_engine.next_ration_reformulation, mock_weather, mock_time
    )
    mock_weather_get_current_day_conditions.assert_called_once_with(time=mock_time)
    mock_herd_formulate_rations.assert_called_once_with(
        simulation_engine.feed_manager.available_feeds,
        mock_current_day_conditions.mean_air_temperature,
        ration_formulation_interval_length,
        mock_total_inventory,
        simulation_engine.time.simulation_day,
    )
    mock_feed_manage_ration_interval_purchases.assert_called_once_with(mock_requested_feed, mock_time)
    mock_report_ration_interval_data.assert_called_once()


def test_generate_daily_manure_applications(simulation_engine: SimulationEngine, mocker: MockerFixture) -> None:
    """Unit test for generate_daily_manure_applications in SimulationEngine."""
    simulation_engine.time = (mock_time := MagicMock(auto_spec=RufasTime))
    simulation_engine.simulate_animals = True

    field_1, field_2 = MagicMock(auto_spec=Field), MagicMock(auto_spec=Field)
    field_1.field_data.name, field_2.field_data.name = "Field 1", "Field 2"
    simulation_engine.field_manager.fields = [field_1, field_2]

    manure_event_request_1, manure_event_request_2 = (
        MagicMock(auto_spec=ManureEventNutrientRequest),
        MagicMock(auto_spec=ManureEventNutrientRequest),
    )
    manure_event_request_1.field_name, manure_event_request_2.field_name = "Field 1", "Field 2"
    manure_event_request_1.event, manure_event_request_2.event = (
        (mock_event_1 := MagicMock(auto_spec=ManureEvent)),
        (mock_event_2 := MagicMock(auto_spec=ManureEvent)),
    )
    manure_event_request_1.manure_supplement_method, manure_event_request_2.manure_supplement_method = (
        ManureSupplementMethod.NONE,
        ManureSupplementMethod.NONE,
    )
    manure_event_request_1.nutrient_request, manure_event_request_2.nutrient_request = (
        (mock_nutrient_request_result := MagicMock(auto_spec=NutrientRequestResults)),
        None,
    )

    mock_check_manure_schedules = mocker.patch.object(
        simulation_engine.field_manager,
        "check_manure_schedules",
        side_effect=[[manure_event_request_1], [manure_event_request_2]],
    )
    mock_request_nutrients = mocker.patch.object(
        simulation_engine.manure_manager, "request_nutrients", return_value=mock_nutrient_request_result
    )

    result = simulation_engine.generate_daily_manure_applications()

    assert result == [
        ManureEventNutrientRequestResults("Field 1", mock_event_1, mock_nutrient_request_result),
        ManureEventNutrientRequestResults("Field 2", mock_event_2, None),
    ]
    mock_check_manure_schedules.assert_any_call(field_1, mock_time)
    mock_check_manure_schedules.assert_any_call(field_2, mock_time)
    mock_request_nutrients.assert_called_once()


def test_initialize_simulation(mocker: MockerFixture) -> None:
    """
    Unit test for function _initialize_simulation in file RUFAS/simulation_engine.py
    """
    # Arrange
    mocker.patch.object(SimulationEngine, "__init__", return_value=None)
    simulation_engine = SimulationEngine()

    simulation_engine.time = (mock_time := MagicMock(auto_spec=RufasTime))
    mock_time.current_date = datetime.today()

    mock_input_manager = MagicMock(auto_spec=InputManager)
    mock_output_manager = MagicMock(auto_spec=OutputManager)
    simulation_engine.im, simulation_engine.om = mock_input_manager, mock_output_manager

    mock_weather_data = {"dummy": "weather data"}
    mock_config_nutrient_standard = "NASEM"
    mock_feed_config = {"dummy": "feed config"}
    mock_feed_storage_configs = {"dummy": "storage configs"}
    mock_feed_storage_instances = {"dummy": "storage instances"}
    mock_ration_interval_length = 30
    mock_is_ration_defined_by_user = True
    mock_simulate_animals = True

    mock_im_get_data = mocker.patch.object(
        mock_input_manager,
        "get_data",
        side_effect=[
            mock_weather_data,
            mock_config_nutrient_standard,
            mock_feed_config,
            mock_feed_storage_configs,
            mock_feed_storage_instances,
            mock_simulate_animals,
            mock_ration_interval_length,
            mock_is_ration_defined_by_user,
            4,
        ],
    )

    mock_weather = MagicMock(auto_spec=Weather)
    mock_weather_init = mocker.patch("RUFAS.simulation_engine.Weather", return_value=mock_weather)

    mock_field_manager = MagicMock(auto_spec=FieldManager)
    mock_field_manager_init = mocker.patch("RUFAS.simulation_engine.FieldManager", return_value=mock_field_manager)

    mock_nutrient_standard = MagicMock(auto_spec=NutrientStandard)
    mock_nutrient_standard_init = mocker.patch(
        "RUFAS.simulation_engine.NutrientStandard", return_value=mock_nutrient_standard
    )

    mock_feed_manager = MagicMock(auto_spec=FeedManager)
    mock_feed_manager_init = mocker.patch("RUFAS.simulation_engine.FeedManager", return_value=mock_feed_manager)

    mock_herd_manager = MagicMock(auto_spec=HerdManager)
    mock_herd_manager_init = mocker.patch("RUFAS.simulation_engine.HerdManager", return_value=mock_herd_manager)

    mock_manure_manager = MagicMock(auto_spec=ManureManager)
    mock_manure_manager_init = mocker.patch("RUFAS.simulation_engine.ManureManager", return_value=mock_manure_manager)

    mock_emissions_estimator = MagicMock(auto_spec=EmissionsEstimator)
    mock_emissions_estimator_init = mocker.patch(
        "RUFAS.simulation_engine.EmissionsEstimator", return_value=mock_emissions_estimator
    )

    # Act
    simulation_engine._initialize_simulation()

    # Assert
    assert mock_im_get_data.call_args_list == [
        call("weather"),
        call("config.nutrient_standard"),
        call("feed"),
        call("feed_storage_configurations"),
        call("feed_storage_instances"),
        call("config.simulate_animals"),
        call("animal.ration.formulation_interval"),
        call("animal.ration.user_input"),
        call("feed.max_daily_feed_recalculations_per_year"),
    ]

    assert simulation_engine.om.time == mock_time
    mock_weather_init.assert_called_once_with(mock_weather_data, mock_time)
    assert simulation_engine.weather == mock_weather
    assert simulation_engine.simulate_animals == mock_simulate_animals

    mock_field_manager_init.assert_called_once_with()
    assert simulation_engine.field_manager == mock_field_manager
    mock_emissions_estimator_init.assert_called_once_with()
    assert simulation_engine.emissions_estimator == mock_emissions_estimator
    mock_nutrient_standard_init.assert_called_once_with(mock_config_nutrient_standard)
    mock_feed_manager_init.assert_called_once_with(
        mock_feed_config, mock_nutrient_standard, mock_feed_storage_configs, mock_feed_storage_instances
    )
    assert simulation_engine.feed_manager == mock_feed_manager

    assert simulation_engine.ration_formulation_interval_length == timedelta(days=mock_ration_interval_length)
    assert simulation_engine.next_ration_reformulation == mock_time.current_date.date()
    assert simulation_engine.is_ration_defined_by_user == mock_is_ration_defined_by_user
    assert simulation_engine.max_daily_feed_recalculation_interval == timedelta(days=round(365 / 4))
    assert simulation_engine.next_max_daily_feed_recalculation == mock_time.current_date + timedelta(
        days=round(365 / 4)
    )

    mock_herd_manager_init.assert_called_once_with(
        mock_weather, mock_time, is_ration_defined_by_user=True, available_feeds=mock_feed_manager.available_feeds
    )
    assert simulation_engine.herd_manager == mock_herd_manager

    mock_manure_manager_init.assert_called_once_with(
        mock_weather.intercept_mean_temp, mock_weather.phase_shift, mock_weather.amplitude
    )
    assert simulation_engine.manure_manager == mock_manure_manager


@pytest.mark.parametrize(
    "year_start_day, year_end_day, expected_day_count",
    [
        # Simulate 1 year end
        (0, 0, 1),
        # Simulate 2 years end
        (2, 3, 2),
        # Simulate 4 years end
        (362, 365, 4),
    ],
)
def test_annual_simulation(
    year_start_day: int,
    year_end_day: int,
    expected_day_count: int,
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for function _annual_simulation in file RUFAS/simulation_engine.py
    """

    # Arrange
    mock_daily_simulation = mocker.patch.object(simulation_engine, "_daily_simulation")
    mock_run_post_annual_routines = mocker.patch.object(simulation_engine, "_run_post_annual_routines")

    simulation_engine.time = (mock_time := MagicMock(auto_spec=RufasTime))
    mock_time.year_start_day = year_start_day
    mock_time.year_end_day = year_end_day

    # Act
    simulation_engine._annual_simulation()

    # Assert
    assert mock_daily_simulation.call_count == expected_day_count
    assert mock_daily_simulation.call_args_list == [call()] * expected_day_count
    mock_run_post_annual_routines.assert_called_once()


def test_annual_reset(simulation_engine: SimulationEngine, mocker: MockerFixture) -> None:
    """
    Unit test for function annual_reset() in file RUFAS/simulation_engine.py
    """
    mock_field_annual_update_routine = mocker.patch.object(simulation_engine.field_manager, "annual_update_routine")

    simulation_engine.annual_reset()

    mock_field_annual_update_routine.assert_called_once_with()


def test_annual_mass_balance(simulation_engine: SimulationEngine) -> None:
    """
    Unit test for function annual_mass_balance() in file RUFAS/simulation_engine.py
    """
    simulation_engine.annual_mass_balance(MagicMock(auto_spec=RufasTime))


def test_run_post_annual_routines(simulation_engine: SimulationEngine, mocker: MockerFixture) -> None:
    """
    Unit test for function _run_post_annual_routines in file RUFAS/simulation_engine.py
    """

    # Arrange
    simulation_engine.time = (mock_time := MagicMock(auto_spec=RufasTime))

    mock_annual_mass_balance = mocker.patch.object(simulation_engine, "annual_mass_balance")
    mock_annual_reset = mocker.patch.object(simulation_engine, "annual_reset")

    # Act
    simulation_engine._run_post_annual_routines()

    # Assert
    mock_annual_mass_balance.assert_called_once_with(mock_time)
    mock_annual_reset.assert_called_once_with()


def test_advance_time(simulation_engine: SimulationEngine, mocker: MockerFixture) -> None:
    """
    Unit test for function _advance_time in file RUFAS/simulation_engine.py
    """

    # Arrange
    simulation_engine.time = (mock_time := MagicMock(auto_spec=RufasTime))
    mock_time_advance = mocker.patch.object(mock_time, "advance")

    # Act
    simulation_engine._advance_time()

    # Assert
    mock_time_advance.assert_called_once_with()


@pytest.mark.parametrize(
    "expected_iterations",
    [
        # Simulate a loop that runs once
        1,
        # Simulate a loop that runs twice
        2,
        # Simulate a loop that runs three times
        3,
    ],
)
def test_run_simulation_main_loop(
    expected_iterations: int, simulation_engine: SimulationEngine, mocker: MockerFixture
) -> None:
    """
    Unit test for function _run_simulation_main_loop in file RUFAS/simulation_engine.py
    """

    # Arrange
    simulation_engine.time = (mock_time := MagicMock(auto_spec=RufasTime))
    mock_time.simulation_length_years = expected_iterations

    mock_annual_simulation = mocker.patch.object(simulation_engine, "_annual_simulation")

    # Act
    simulation_engine._run_simulation_main_loop()

    # Assert
    assert mock_annual_simulation.call_count == expected_iterations
    assert mock_annual_simulation.call_args_list == [call()] * expected_iterations

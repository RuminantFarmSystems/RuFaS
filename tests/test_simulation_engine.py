from datetime import date, datetime, timedelta

from RUFAS.EEE.emissions import EmissionsEstimator
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
import pytest
from unittest.mock import MagicMock, PropertyMock, call

from pytest_mock import MockerFixture

from RUFAS.EEE.EEE_manager import EEEManager
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.biophysical.feed_storage.feed_manager import FeedManager
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.events import ManureEvent
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    Feed,
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
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.field.field.field import Field
from RUFAS.biophysical.field.manager.field_manager import FieldManager
from RUFAS.biophysical.manure.manure_manager import ManureManager
from RUFAS.simulation_engine import DEFAULT_FEED_DEGRADATIONS_PROCESSING_INTERVAL, SimulationEngine, SimulationType
from RUFAS.rufas_time import RufasTime
from RUFAS.weather import Weather


def test_simulation_type_enum_values() -> None:
    """Unit test for SimulationType enum values."""
    assert SimulationType.FULL_FARM.value == "full_farm"
    assert SimulationType.FIELD_AND_FEED.value == "field_and_feed"
    assert SimulationType.FIELD_ONLY.value == "field_only"
    assert SimulationType.ANIMALS_ONLY.value == "animals_only"


@pytest.mark.parametrize(
    "simulation_type, expected_result",
    [
        (SimulationType.FULL_FARM, True),
        (SimulationType.FIELD_AND_FEED, False),
        (SimulationType.FIELD_ONLY, False),
        (SimulationType.ANIMALS_ONLY, True),
    ],
)
def test_simulate_animals(
    simulation_type: SimulationType,
    expected_result: bool,
) -> None:
    """Unit test for SimulationType.simulate_animals property."""
    assert simulation_type.simulate_animals is expected_result


def test_animal_simulation_types() -> None:
    """Unit test for SimulationType._animal_simulation_types."""
    assert SimulationType._animal_simulation_types() == {SimulationType.FULL_FARM, SimulationType.ANIMALS_ONLY}


def test_field_simulation_types() -> None:
    """Unit test for SimulationType._fields_simulation_types."""
    assert SimulationType._fields_simulation_types() == {
        SimulationType.FULL_FARM,
        SimulationType.FIELD_AND_FEED,
        SimulationType.FIELD_ONLY,
    }


def test_manure_simulation_types() -> None:
    """Unit test for SimulationType._manure_simulation_types."""
    assert SimulationType._manure_simulation_types() == {SimulationType.FULL_FARM}


def test_feed_simulation_types() -> None:
    """Unit test for SimulationType._feed_simulation_types."""
    assert SimulationType._feed_simulation_types() == {
        SimulationType.FULL_FARM,
        SimulationType.FIELD_AND_FEED,
    }


@pytest.mark.parametrize("simulation_type", list(SimulationType))
def test_get_simulation_type_valid(simulation_type: SimulationType) -> None:
    """Unit test for SimulationType.get_simulation_type with valid values."""
    assert SimulationType.get_simulation_type(simulation_type.value) is simulation_type


def test_get_simulation_type_invalid() -> None:
    """Unit test for SimulationType.get_simulation_type with an invalid value."""
    invalid_simulation_type = "not_a_real_simulation"
    valid_simulation_types = ", ".join(simulation_type.value for simulation_type in SimulationType)

    with pytest.raises(
        ValueError,
        match=(f"Unknown simulation type: {invalid_simulation_type}. " f"Expected one of: {valid_simulation_types}."),
    ):
        SimulationType.get_simulation_type(invalid_simulation_type)


@pytest.fixture
def simulation_engine(mocker: MockerFixture) -> SimulationEngine:
    mocker.patch("RUFAS.simulation_engine.RufasTime")
    mocker.patch("RUFAS.simulation_engine.SimulationEngine._setup_simulation_modules")
    mock_simulation_type = SimulationType("full_farm")

    simulation_engine = SimulationEngine(mock_simulation_type)

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
    mock_setup_simulation_modules = mocker.patch.object(SimulationEngine, "_setup_simulation_modules")
    mock_time = mocker.MagicMock(auto_spec=RufasTime)
    mocker.patch("RUFAS.simulation_engine.RufasTime", return_value=mock_time)
    mock_simulation_type = SimulationType("full_farm")

    # Act
    simulation_engine = SimulationEngine(mock_simulation_type)

    # Assert
    mock_setup_simulation_modules.assert_called_once()
    assert simulation_engine.time == mock_time


@pytest.mark.parametrize("start_time, end_time", [(100, 200), (300, 400)])
def test_simulate(
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
    start_time: int,
    end_time: int,
) -> None:
    """
    Unit test for function simulate() in simulation_engine.py
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
        simulation_engine.herd_manager.animal_genetic_history_by_id,
    )

    mock_estimate_emissions.assert_called_once()


def test_execute_full_farm_daily_simulation(
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for function _execute_full_farm_daily_simulation in file
    RUFAS/simulation_engine.py
    """
    # Arrange
    daily_harvested_crops = [{"crop": "corn"}]
    harvest_schedule = {"day_1": ["corn silage"]}
    daily_manure_data = {"manure": "data"}
    daily_purchased_feeds_fed = {"feed_1": 12.5}

    mock_execute_daily_field_operations = mocker.patch.object(
        simulation_engine,
        "_execute_daily_field_operations",
        return_value=daily_harvested_crops,
    )
    mock_receive_daily_harvested_crops = mocker.patch.object(
        simulation_engine,
        "_receive_daily_harvested_crops",
    )
    mock_build_harvest_schedule = mocker.patch.object(
        simulation_engine,
        "_build_harvest_schedule",
        return_value=harvest_schedule,
    )
    mock_execute_feed_planning = mocker.patch.object(
        simulation_engine,
        "_execute_feed_planning",
    )
    mock_execute_ration_planning = mocker.patch.object(
        simulation_engine,
        "_execute_ration_planning",
    )
    mock_execute_daily_animal_operations = mocker.patch.object(
        simulation_engine,
        "_execute_daily_animal_operations",
        return_value=(daily_manure_data, daily_purchased_feeds_fed),
    )
    mock_execute_daily_manure_operations = mocker.patch.object(
        simulation_engine,
        "_execute_daily_manure_operations",
    )
    mock_report_daily_records = mocker.patch.object(
        simulation_engine,
        "_report_daily_records",
    )
    mock_advance_time = mocker.patch.object(
        simulation_engine,
        "_advance_time",
    )

    # Act
    simulation_engine._execute_full_farm_daily_simulation()

    # Assert
    mock_execute_daily_field_operations.assert_called_once_with()
    mock_receive_daily_harvested_crops.assert_called_once_with(daily_harvested_crops)
    mock_build_harvest_schedule.assert_called_once_with(daily_harvested_crops)
    mock_execute_feed_planning.assert_called_once_with(harvest_schedule)
    mock_execute_ration_planning.assert_called_once_with()
    mock_execute_daily_animal_operations.assert_called_once_with()
    mock_execute_daily_manure_operations.assert_called_once_with(daily_manure_data)
    mock_report_daily_records.assert_called_once_with(daily_purchased_feeds_fed)
    mock_advance_time.assert_called_once_with()


def test_execute_field_and_feed_daily_simulation(
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for function _execute_field_and_feed_daily_simulation in file
    RUFAS/simulation_engine.py
    """
    # Arrange
    daily_harvested_crops = [{"crop": "corn"}]
    harvest_schedule = {"day_1": ["corn silage"]}

    parent = MagicMock()

    parent.attach_mock(
        mocker.patch.object(
            simulation_engine,
            "_execute_daily_field_operations",
            return_value=daily_harvested_crops,
        ),
        "execute_daily_field_operations",
    )
    parent.attach_mock(
        mocker.patch.object(
            simulation_engine,
            "_receive_daily_harvested_crops",
        ),
        "receive_daily_harvested_crops",
    )
    parent.attach_mock(
        mocker.patch.object(
            simulation_engine,
            "_build_harvest_schedule",
            return_value=harvest_schedule,
        ),
        "build_harvest_schedule",
    )
    parent.attach_mock(
        mocker.patch.object(simulation_engine, "_execute_feed_planning"),
        "execute_feed_planning",
    )
    parent.attach_mock(
        mocker.patch.object(simulation_engine, "_report_daily_records"),
        "report_daily_records",
    )
    parent.attach_mock(
        mocker.patch.object(simulation_engine, "_advance_time"),
        "advance_time",
    )

    mock_execute_ration_planning = mocker.patch.object(
        simulation_engine,
        "_execute_ration_planning",
    )
    mock_execute_daily_animal_operations = mocker.patch.object(
        simulation_engine,
        "_execute_daily_animal_operations",
    )
    mock_execute_daily_manure_operations = mocker.patch.object(
        simulation_engine,
        "_execute_daily_manure_operations",
    )

    # Act
    simulation_engine._execute_field_and_feed_daily_simulation()

    # Assert
    assert parent.mock_calls == [
        call.execute_daily_field_operations(),
        call.receive_daily_harvested_crops(daily_harvested_crops),
        call.build_harvest_schedule(daily_harvested_crops),
        call.execute_feed_planning(harvest_schedule),
        call.report_daily_records(),
        call.advance_time(),
    ]

    mock_execute_ration_planning.assert_not_called()
    mock_execute_daily_animal_operations.assert_not_called()
    mock_execute_daily_manure_operations.assert_not_called()


def test_execute_animals_only_daily_simulation(
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for function _execute_animals_only_daily_simulation in file
    RUFAS/simulation_engine.py
    """
    # Arrange
    daily_manure_data = {"manure": "data"}
    daily_purchased_feeds_fed = {"feed_1": 12.5}
    mock_execute_ration_planning = mocker.patch.object(
        simulation_engine,
        "_execute_ration_planning",
    )
    mock_execute_daily_animal_operations = mocker.patch.object(
        simulation_engine,
        "_execute_daily_animal_operations",
        return_value=(daily_manure_data, daily_purchased_feeds_fed),
    )
    mock_report_daily_records = mocker.patch.object(
        simulation_engine,
        "_report_daily_records",
    )
    mock_advance_time = mocker.patch.object(
        simulation_engine,
        "_advance_time",
    )

    # Act
    simulation_engine._execute_animals_only_daily_simulation()

    # Assert
    mock_execute_ration_planning.assert_called_once_with()
    mock_execute_daily_animal_operations.assert_called_once_with()
    mock_report_daily_records.assert_called_once_with(daily_purchased_feeds_fed)
    mock_advance_time.assert_called_once_with()


def test_execute_daily_field_operations(
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for function _execute_daily_field_operations in file
    RUFAS/simulation_engine.py
    """
    # Arrange
    manure_applications = [MagicMock(), MagicMock()]
    harvested_crops = [MagicMock(), MagicMock()]

    mock_generate_daily_manure_applications = mocker.patch.object(
        simulation_engine,
        "_generate_daily_manure_applications",
        return_value=manure_applications,
    )

    simulation_engine.weather = MagicMock()
    simulation_engine.time = MagicMock()

    simulation_engine.field_manager = MagicMock()
    simulation_engine.field_manager.daily_update_routine.return_value = harvested_crops

    # Act
    result = simulation_engine._execute_daily_field_operations()

    # Assert
    mock_generate_daily_manure_applications.assert_called_once_with()
    simulation_engine.field_manager.daily_update_routine.assert_called_once_with(
        simulation_engine.weather,
        simulation_engine.time,
        manure_applications,
    )
    assert result == harvested_crops


def test_execute_daily_field_operations_no_harvested_crops(
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for function _execute_daily_field_operations with no harvested crops
    in simulation_engine.py
    """
    # Arrange
    manure_applications = [MagicMock()]
    harvested_crops: list[HarvestedCrop] = []

    mock_generate_daily_manure_applications = mocker.patch.object(
        simulation_engine,
        "_generate_daily_manure_applications",
        return_value=manure_applications,
    )

    simulation_engine.weather = MagicMock()
    simulation_engine.time = MagicMock()
    simulation_engine.time.simulation_day = 123

    simulation_engine.field_manager = MagicMock()
    simulation_engine.field_manager.daily_update_routine.return_value = harvested_crops

    simulation_engine.feed_manager = MagicMock()

    # Act
    result = simulation_engine._execute_daily_field_operations()

    # Assert
    mock_generate_daily_manure_applications.assert_called_once_with()
    simulation_engine.field_manager.daily_update_routine.assert_called_once_with(
        simulation_engine.weather,
        simulation_engine.time,
        manure_applications,
    )
    simulation_engine.feed_manager.receive_crop.assert_not_called()
    assert result == harvested_crops


def test_execute_field_only_simulation(
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for function _execute_field_only_simulation
    in file RUFAS/simulation_engine.py
    """
    parent = MagicMock()

    parent.attach_mock(
        mocker.patch.object(simulation_engine, "_execute_daily_field_operations"),
        "execute_daily_field_operations",
    )
    parent.attach_mock(
        mocker.patch.object(simulation_engine, "_report_daily_records"),
        "report_daily_records",
    )
    parent.attach_mock(
        mocker.patch.object(simulation_engine, "_advance_time"),
        "advance_time",
    )

    simulation_engine._execute_field_only_simulation()

    assert parent.mock_calls == [
        call.execute_daily_field_operations(),
        call.report_daily_records(),
        call.advance_time(),
    ]


def test_build_harvest_schedule_no_feed_recalculation(
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for function _build_harvest_schedule when feed planning recalculation
    is not needed in simulation_engine.py
    """
    # Arrange
    harvested_crop_1 = MagicMock()
    harvested_crop_1.config_name = "corn_silage"

    harvested_crop_2 = MagicMock()
    harvested_crop_2.config_name = "alfalfa"

    harvested_crops: list[HarvestedCrop] = [harvested_crop_1, harvested_crop_2]

    expected_schedule = {
        "corn_silage": datetime(2026, 6, 1).date(),
        "alfalfa": datetime(2026, 6, 15).date(),
    }

    mocker.patch.object(
        SimulationEngine,
        "_should_recalculate_feed_planning",
        new_callable=mocker.PropertyMock,
        return_value=False,
    )

    mock_get_next_harvest_dates = mocker.patch.object(
        simulation_engine.field_manager,
        "get_next_harvest_dates",
        return_value=expected_schedule,
    )

    # Act
    result = simulation_engine._build_harvest_schedule(harvested_crops)

    # Assert
    mock_get_next_harvest_dates.assert_called_once()
    called_crop_names = mock_get_next_harvest_dates.call_args.args[0]
    assert set(called_crop_names) == {"corn_silage", "alfalfa"}
    assert result == expected_schedule


@pytest.mark.parametrize(
    "offset_days, expected",
    [
        (0, True),
        (1, False),
    ],
)
def test_should_recalculate_feed_planning(
    simulation_engine: SimulationEngine,
    offset_days: int,
    expected: bool,
) -> None:
    """
    Unit test for property _should_recalculate_feed_planning
    in simulation_engine.py
    """
    # Arrange
    current_date = datetime(2026, 3, 11)

    simulation_engine.time.current_date = current_date
    simulation_engine.next_max_daily_feed_recalculation = current_date + timedelta(days=offset_days)

    # Act / Assert
    assert simulation_engine._should_recalculate_feed_planning is expected


def test_execute_feed_planning_empty_schedule(
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for function _execute_feed_planning with empty harvest schedule
    in simulation_engine.py
    """
    # Arrange
    mock_get_total_projected_inventory = mocker.patch.object(
        simulation_engine.feed_manager,
        "get_total_projected_inventory",
    )
    mock_translate_crop_config_name_to_rufas_id = mocker.patch.object(
        simulation_engine.feed_manager,
        "translate_crop_config_name_to_rufas_id",
    )
    mock_update_all_max_daily_feeds = mocker.patch.object(
        simulation_engine.herd_manager,
        "update_all_max_daily_feeds",
    )
    mock_manage_planning_cycle_purchases = mocker.patch.object(
        simulation_engine.feed_manager,
        "manage_planning_cycle_purchases",
    )

    # Act
    simulation_engine._execute_feed_planning({})

    # Assert
    mock_get_total_projected_inventory.assert_not_called()
    mock_translate_crop_config_name_to_rufas_id.assert_not_called()
    mock_update_all_max_daily_feeds.assert_not_called()
    mock_manage_planning_cycle_purchases.assert_not_called()


def test_execute_feed_planning(
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for function _execute_feed_planning in simulation_engine.py
    """
    # Arrange
    harvest_schedule: dict[str, date | None] = {"corn_silage": None}

    projected_inventory = {1: 100}
    harvest_dates_with_ids = {12: None}
    ideal_feeds = IdealFeeds({1: 50})
    simulation_day = 123

    simulation_engine.simulate_animals = True
    simulation_engine.time.current_date = datetime(2026, 3, 11)
    mocker.patch.object(simulation_engine.time, "simulation_day", simulation_day, create=True)
    simulation_engine.weather = MagicMock()

    mocker.patch.object(
        type(simulation_engine),
        "_is_time_to_process_feed_degradations",
        new_callable=PropertyMock,
        return_value=False,
    )

    mock_get_total_projected_inventory = mocker.patch.object(
        simulation_engine.feed_manager,
        "get_total_projected_inventory",
        return_value=projected_inventory,
    )
    mock_translate_crop_config_name_to_rufas_id = mocker.patch.object(
        simulation_engine.feed_manager,
        "translate_crop_config_name_to_rufas_id",
        return_value=harvest_dates_with_ids,
    )
    mock_update_all_max_daily_feeds = mocker.patch.object(
        simulation_engine,
        "_update_all_max_daily_feeds",
        return_value=ideal_feeds,
    )
    mock_manage_planning_cycle_purchases = mocker.patch.object(
        simulation_engine.feed_manager,
        "manage_planning_cycle_purchases",
    )
    mock_report_feed_storage_levels = mocker.patch.object(
        simulation_engine.feed_manager,
        "report_feed_storage_levels",
    )
    mock_report_cumulative_purchased_feeds = mocker.patch.object(
        simulation_engine.feed_manager,
        "report_cumulative_purchased_feeds",
    )
    mock_process_degradations = mocker.patch.object(
        simulation_engine.feed_manager,
        "process_degradations",
    )

    # Act
    simulation_engine._execute_feed_planning(harvest_schedule)

    # Assert
    mock_get_total_projected_inventory.assert_called_once_with(
        simulation_engine.time.current_date.date(),
        simulation_engine.weather,
        simulation_engine.time,
    )
    mock_translate_crop_config_name_to_rufas_id.assert_called_once_with(harvest_schedule)
    mock_update_all_max_daily_feeds.assert_called_once_with(
        projected_inventory,
        harvest_dates_with_ids,
    )
    mock_manage_planning_cycle_purchases.assert_called_once_with(
        ideal_feeds,
        simulation_engine.time,
    )
    mock_report_feed_storage_levels.assert_called_once_with(
        simulation_day,
        "daily_storage_levels",
    )
    mock_report_cumulative_purchased_feeds.assert_called_once_with(simulation_day)
    mock_process_degradations.assert_not_called()


def test_build_harvest_schedule(
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for function _build_harvest_schedule in file
    RUFAS/simulation_engine.py
    """
    # Arrange
    harvested_crop_1 = MagicMock()
    harvested_crop_1.config_name = "corn_silage"

    harvested_crop_2 = MagicMock()
    harvested_crop_2.config_name = "alfalfa"

    harvested_crop_3 = MagicMock()
    harvested_crop_3.config_name = "corn_silage"

    harvested_crops: list[HarvestedCrop] = [
        harvested_crop_1,
        harvested_crop_2,
        harvested_crop_3,
    ]

    expected_schedule = {
        "corn_silage": datetime(2026, 6, 1).date(),
        "alfalfa": datetime(2026, 6, 15).date(),
    }

    mock_get_next_harvest_dates = mocker.patch.object(
        simulation_engine.field_manager,
        "get_next_harvest_dates",
        return_value=expected_schedule,
    )

    # Act
    result = simulation_engine._build_harvest_schedule(harvested_crops)

    # Assert
    mock_get_next_harvest_dates.assert_called_once()
    called_crop_names = mock_get_next_harvest_dates.call_args.args[0]
    assert set(called_crop_names) == {"corn_silage", "alfalfa"}
    assert result == expected_schedule


@pytest.mark.parametrize(
    "is_time_to_reformulate, expected_call_count, expected_next_reformulation",
    [
        (True, 1, datetime(2026, 4, 10).date()),
    ],
)
def test_execute_ration_planning(
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
    is_time_to_reformulate: bool,
    expected_call_count: int,
    expected_next_reformulation: date,
) -> None:
    """
    Unit test for function _execute_ration_planning in simulation_engine.py
    """
    # Arrange
    mocker.patch.object(
        SimulationEngine,
        "_is_time_to_reformulate_ration",
        new_callable=PropertyMock,
        return_value=is_time_to_reformulate,
    )

    simulation_engine.time.current_date = datetime(2026, 3, 11)
    simulation_engine.ration_formulation_interval_length = timedelta(days=30)
    simulation_engine.next_ration_reformulation = datetime(2026, 3, 11).date()

    mock_formulate_ration = mocker.patch.object(
        simulation_engine,
        "_formulate_ration",
    )

    # Act
    simulation_engine._execute_ration_planning()

    # Assert
    assert mock_formulate_ration.call_count == expected_call_count
    assert simulation_engine.next_ration_reformulation == expected_next_reformulation


@pytest.mark.parametrize(
    "current_date, next_reformulation, expected",
    [
        (date(2026, 3, 11), date(2026, 3, 11), True),
        (date(2026, 3, 12), date(2026, 3, 11), True),
        (date(2026, 3, 10), date(2026, 3, 11), False),
    ],
)
def test_is_time_to_reformulate_ration(
    simulation_engine: SimulationEngine,
    current_date: date,
    next_reformulation: date,
    expected: bool,
) -> None:
    """
    Unit test for property _is_time_to_reformulate_ration
    in simulation_engine.py
    """
    # Arrange
    simulation_engine.time.current_date = datetime.combine(current_date, datetime.min.time())
    simulation_engine.next_ration_reformulation = next_reformulation

    # Act / Assert
    assert simulation_engine._is_time_to_reformulate_ration is expected


@pytest.mark.parametrize(
    "is_ok_to_feed_animals, expected_purchased_feeds, expect_warning, expect_formulate_ration",
    [
        (
            True,
            {101: 25.0, 202: 10.5},
            False,
            False,
        ),
        (
            False,
            {101: 25.0, 202: 10.5},
            True,
            True,
        ),
    ],
)
def test_execute_daily_animal_operations(
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
    is_ok_to_feed_animals: bool,
    expected_purchased_feeds: dict[int, float],
    expect_warning: bool,
    expect_formulate_ration: bool
) -> None:
    """
    Unit test for function _execute_daily_animal_operations in simulation_engine.py
    """
    # Arrange
    simulation_engine.simulate_feed = True
    simulation_engine.time = MagicMock()
    simulation_engine.weather = MagicMock()
    simulation_engine.om = MagicMock()

    requested_feed = MagicMock()
    daily_feeds_fed = MagicMock()
    daily_feeds_fed.purchased = expected_purchased_feeds

    all_manure_data = {"pen_1": MagicMock(), "pen_2": MagicMock()}
    available_feeds: list[Feed] = [MagicMock(rufas_id=12), MagicMock(rufas_id=7)]
    simulation_engine.available_feeds = available_feeds

    mock_collect_daily_feed_request = mocker.patch.object(
        simulation_engine.herd_manager,
        "collect_daily_feed_request",
        return_value=requested_feed,
    )
    mock_manage_daily_feed_request = mocker.patch.object(
        simulation_engine.feed_manager,
        "manage_daily_feed_request",
        return_value=(is_ok_to_feed_animals, daily_feeds_fed),
    )
    mock_formulate_ration = mocker.patch.object(
        simulation_engine,
        "_formulate_ration",
    )
    mock_daily_routines = mocker.patch.object(
        simulation_engine.herd_manager,
        "execute_daily_routines",
        return_value=all_manure_data,
    )

    call_tracker = MagicMock()
    call_tracker.attach_mock(mock_daily_routines, "execute_daily_routines")
    call_tracker.attach_mock(mock_collect_daily_feed_request, "collect_daily_feed_request")
    call_tracker.attach_mock(mock_manage_daily_feed_request, "manage_daily_feed_request")
    call_tracker.attach_mock(simulation_engine.om.add_warning, "add_warning")
    call_tracker.attach_mock(mock_formulate_ration, "formulate_ration")

    # Act
    result_manure_data, result_purchased_feeds = simulation_engine._execute_daily_animal_operations()

    # Assert
    expected_calls = [
        call.execute_daily_routines(
            available_feeds,
            simulation_engine.time,
            simulation_engine.weather,
        ),
        call.collect_daily_feed_request(),
        call.manage_daily_feed_request(
            requested_feed,
            simulation_engine.time,
        ),
    ]

    if expect_warning:
        expected_calls.extend(
            [
                call.add_warning(
                    "Value: not enough feed for the herd",
                    "Reformulating ration for all pens",
                    {
                        "class": "SimulationEngine",
                        "function": "_execute_daily_animal_operations",
                    },
                ),
                call.formulate_ration(),
            ]
        )

    if expect_formulate_ration: 
        mock_formulate_ration.assert_called_once_with()
    else:
        mock_formulate_ration.assert_not_called()

    assert call_tracker.mock_calls == expected_calls
    assert result_manure_data == all_manure_data
    assert result_purchased_feeds == expected_purchased_feeds


@pytest.mark.parametrize(
    "daily_manure_data, should_call_update",
    [
        ({"pen_1": MagicMock(spec=ManureStream)}, True),
        (None, False),
    ],
)
def test_execute_daily_manure_operations(
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
    daily_manure_data: dict[str, ManureStream] | None,
    should_call_update: bool,
) -> None:
    """
    Unit test for function _execute_daily_manure_operations
    in simulation_engine.py
    """
    # Arrange
    simulation_engine.time = MagicMock()
    simulation_engine.weather = MagicMock()

    current_day_conditions = MagicMock()

    mock_get_current_day_conditions = mocker.patch.object(
        simulation_engine.weather,
        "get_current_day_conditions",
        return_value=current_day_conditions,
    )

    mock_run_daily_update = mocker.patch.object(
        simulation_engine.manure_manager,
        "run_daily_update",
    )

    # Act
    simulation_engine._execute_daily_manure_operations(daily_manure_data)

    # Assert
    if should_call_update:
        mock_get_current_day_conditions.assert_called_once_with(simulation_engine.time)
        mock_run_daily_update.assert_called_once_with(
            daily_manure_data,
            simulation_engine.time,
            current_day_conditions,
        )
    else:
        mock_get_current_day_conditions.assert_not_called()
        mock_run_daily_update.assert_not_called()


@pytest.mark.parametrize(
    "daily_purchased_feeds_fed, expect_emissions_call",
    [
        ({101: 25.0, 202: 10.5}, True),
        (None, False),
    ],
)
def test_report_daily_records(
    simulation_engine: SimulationEngine,
    mocker: MockerFixture,
    daily_purchased_feeds_fed: dict[int, float] | None,
    expect_emissions_call: bool,
) -> None:
    """
    Unit test for function _report_daily_records in simulation_engine.py
    """
    # Arrange
    mock_weather = MagicMock(auto_spec=Weather)
    simulation_engine.weather = mock_weather
    mock_calculate_purchased_feed_emissions = mocker.patch.object(
        simulation_engine.emissions_estimator,
        "calculate_purchased_feed_emissions",
    )

    mock_record_time = mocker.patch.object(
        simulation_engine.time,
        "record_time",
    )

    mock_record_weather = mocker.patch.object(
        simulation_engine.weather,
        "record_weather",
    )

    # Act
    simulation_engine._report_daily_records(daily_purchased_feeds_fed)

    # Assert
    if expect_emissions_call:
        mock_calculate_purchased_feed_emissions.assert_called_once_with(daily_purchased_feeds_fed)
    else:
        mock_calculate_purchased_feed_emissions.assert_not_called()

    mock_record_time.assert_called_once_with()
    mock_record_weather.assert_called_once_with(simulation_engine.time)


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
    Unit test for function _formulate_ration() in simulation_engine.py
    """
    # Arrange
    simulation_engine.simulate_feed = True
    simulation_engine.time = (mock_time := MagicMock(auto_spec=RufasTime))
    simulation_engine.weather = (mock_weather := MagicMock(auto_spec=Weather))
    simulation_engine.herd_manager.all_pens = [MagicMock(auto_spec=Pen) for _ in range(number_of_pens)]
    simulation_engine.available_feeds = [MagicMock(), MagicMock()]

    mock_time.simulation_day = 123

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
        simulation_engine.feed_manager,
        "manage_ration_interval_purchases",
    )
    mock_report_feed_manager_balance = mocker.patch.object(
        simulation_engine.feed_manager,
        "report_feed_manager_balance",
    )
    mock_report_ration_interval_data = mocker.patch.object(
        simulation_engine.herd_manager,
        "report_ration_interval_data",
    )

    simulation_engine.ration_formulation_interval_length = timedelta(days=ration_formulation_interval_length)

    # Act
    simulation_engine._formulate_ration()

    # Assert
    mock_weather_get_current_day_conditions.assert_called_once_with(time=mock_time)
    mock_herd_formulate_rations.assert_called_once_with(
        simulation_engine.available_feeds,
        mock_current_day_conditions.mean_air_temperature,
        ration_formulation_interval_length,
        mock_time.simulation_day,
    )
    mock_feed_manage_ration_interval_purchases.assert_called_once_with(mock_requested_feed, mock_time)
    mock_report_feed_manager_balance.assert_called_once_with(mock_time.simulation_day)
    mock_report_ration_interval_data.assert_called_once_with(mock_time.simulation_day)


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

    result = simulation_engine._generate_daily_manure_applications()

    assert result == [
        ManureEventNutrientRequestResults("Field 1", mock_event_1, mock_nutrient_request_result),
        ManureEventNutrientRequestResults("Field 2", mock_event_2, None),
    ]
    mock_check_manure_schedules.assert_any_call(field_1, mock_time)
    mock_check_manure_schedules.assert_any_call(field_2, mock_time)
    mock_request_nutrients.assert_called_once()


def test_setup_simulation_modules(mocker: MockerFixture) -> None:
    """
    Unit test for function _setup_simulation_modules in simulation_engine.py
    """
    # Arrange
    mocker.patch.object(SimulationEngine, "__init__", return_value=None)
    simulation_engine = SimulationEngine(SimulationType.FULL_FARM)

    simulation_engine.time = (mock_time := MagicMock(autospec=RufasTime))
    mock_time.current_date = datetime.today()

    mock_input_manager = MagicMock(autospec=InputManager)
    mock_output_manager = MagicMock(autospec=OutputManager)
    simulation_engine.im = mock_input_manager
    simulation_engine.om = mock_output_manager

    simulation_engine.simulate_fields = True
    simulation_engine.simulate_feed = True
    simulation_engine.simulate_animals = True
    simulation_engine.simulate_manure = True

    mock_max_daily_feed_recalculations_per_year = 4
    mock_weather_data = {"dummy": "weather data"}
    mock_feed_config = {
        "dummy": "feed config",
        "ration_formulation_parameters": {
            "max_daily_feed_recalculations_per_year": mock_max_daily_feed_recalculations_per_year,
        },
    }
    mock_config_nutrient_standard = "NASEM"
    mock_feed_storage_configs = {"dummy": "storage configs"}
    mock_feed_storage_instances = {"dummy": "storage instances"}

    mock_ration_interval_length = 30
    mock_is_ration_defined_by_user = True
    mock_ration_config = {
        "formulation_interval": mock_ration_interval_length,
        "user_input": mock_is_ration_defined_by_user,
    }

    mock_im_get_data = mocker.patch.object(
        mock_input_manager,
        "get_data",
        side_effect=[
            mock_weather_data,
            mock_feed_config,
            mock_config_nutrient_standard,
            mock_feed_storage_configs,
            mock_feed_storage_instances,
            mock_ration_config,
        ],
    )

    mock_weather = MagicMock(autospec=Weather)
    mock_weather_init = mocker.patch(
        "RUFAS.simulation_engine.Weather",
        return_value=mock_weather,
    )

    mock_field_manager = MagicMock(autospec=FieldManager)
    mock_field_manager_init = mocker.patch(
        "RUFAS.simulation_engine.FieldManager",
        return_value=mock_field_manager,
    )

    mock_nutrient_standard = MagicMock(autospec=NutrientStandard)
    mock_nutrient_standard_init = mocker.patch(
        "RUFAS.simulation_engine.NutrientStandard",
        return_value=mock_nutrient_standard,
    )

    mock_available_feeds = [MagicMock(rufas_id=12), MagicMock(rufas_id=7)]
    mock_setup_available_feeds = mocker.patch(
        "RUFAS.simulation_engine.AvailableFeedsBuilder.setup_available_feeds",
        return_value=mock_available_feeds,
    )

    mock_feed_manager = MagicMock(autospec=FeedManager)
    mock_feed_manager_init = mocker.patch(
        "RUFAS.simulation_engine.FeedManager",
        return_value=mock_feed_manager,
    )

    mock_herd_manager = MagicMock(autospec=HerdManager)
    mock_herd_manager_init = mocker.patch(
        "RUFAS.simulation_engine.HerdManager",
        return_value=mock_herd_manager,
    )

    mock_manure_manager = MagicMock(autospec=ManureManager)
    mock_manure_manager_init = mocker.patch(
        "RUFAS.simulation_engine.ManureManager",
        return_value=mock_manure_manager,
    )

    mock_emissions_estimator = MagicMock(autospec=EmissionsEstimator)
    mock_emissions_estimator_init = mocker.patch(
        "RUFAS.simulation_engine.EmissionsEstimator",
        return_value=mock_emissions_estimator,
    )

    # Act
    simulation_engine._setup_simulation_modules()

    # Assert
    assert mock_im_get_data.call_args_list == [
        call("weather"),
        call("feed"),
        call("config.nutrient_standard"),
        call("feed_storage_configurations"),
        call("feed_storage_instances"),
        call("animal.ration"),
    ]

    assert simulation_engine.om.time == mock_time

    mock_weather_init.assert_called_once_with(mock_weather_data, mock_time)
    assert simulation_engine.weather == mock_weather

    mock_emissions_estimator_init.assert_called_once_with()
    assert simulation_engine.emissions_estimator == mock_emissions_estimator

    mock_field_manager_init.assert_called_once_with()
    assert simulation_engine.field_manager == mock_field_manager

    mock_nutrient_standard_init.assert_called_once_with(mock_config_nutrient_standard)
    mock_setup_available_feeds.assert_called_once_with(
        mock_feed_config,
        mock_nutrient_standard,
    )
    assert simulation_engine.available_feeds == mock_available_feeds

    mock_feed_manager_init.assert_called_once_with(
        mock_feed_config,
        mock_available_feeds,
        mock_feed_storage_configs,
        mock_feed_storage_instances,
    )
    assert simulation_engine.feed_manager == mock_feed_manager

    expected_interval = timedelta(days=round(365 / mock_max_daily_feed_recalculations_per_year))
    assert simulation_engine.max_daily_feed_recalculation_interval == expected_interval
    assert simulation_engine.next_max_daily_feed_recalculation == mock_time.current_date + expected_interval
    assert simulation_engine.feed_degradations_interval_length == timedelta(
        days=DEFAULT_FEED_DEGRADATIONS_PROCESSING_INTERVAL
    )
    assert simulation_engine.next_degradations_processing == mock_time.current_date.date()

    assert simulation_engine.ration_formulation_interval_length == timedelta(days=mock_ration_interval_length)
    assert simulation_engine.next_ration_reformulation == mock_time.current_date.date()
    assert simulation_engine.is_ration_defined_by_user == mock_is_ration_defined_by_user

    mock_herd_manager_init.assert_called_once_with(
        mock_weather,
        mock_time,
        is_ration_defined_by_user=mock_is_ration_defined_by_user,
        available_feeds=mock_available_feeds,
    )
    assert simulation_engine.herd_manager == mock_herd_manager

    mock_manure_manager_init.assert_called_once_with(
        mock_weather.intercept_mean_temp,
        mock_weather.phase_shift,
        mock_weather.amplitude,
    )
    assert simulation_engine.manure_manager == mock_manure_manager

    mock_emissions_estimator.check_available_purchased_feed_data.assert_called_once_with([12, 7])


@pytest.mark.parametrize(
    "year_start_day, year_end_day, expected_day_count",
    [
        (0, 0, 1),
        (2, 3, 2),
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
    Unit test for function _annual_simulation in simulation_engine.py
    """
    # Arrange
    mock_daily_simulation = mocker.MagicMock(name="daily_simulation")
    mock_run_post_annual_routines = mocker.patch.object(simulation_engine, "_run_post_annual_routines")

    simulation_engine.time = (mock_time := MagicMock(autospec=RufasTime))
    mock_time.year_start_day = year_start_day
    mock_time.year_end_day = year_end_day

    simulation_engine._simulation_type_to_daily_simulation_function = {
        SimulationType("full_farm"): mock_daily_simulation,
        SimulationType("field_and_feed"): mocker.MagicMock(name="no_animals_daily_simulation"),
    }

    # Act
    simulation_engine._annual_simulation()

    # Assert
    assert mock_daily_simulation.call_count == expected_day_count
    assert mock_daily_simulation.call_args_list == [call()] * expected_day_count
    mock_run_post_annual_routines.assert_called_once_with()


def test_annual_reset(simulation_engine: SimulationEngine, mocker: MockerFixture) -> None:
    """
    Unit test for function annual_reset() in simulation_engine.py
    """
    mock_field_annual_update_routine = mocker.patch.object(simulation_engine.field_manager, "annual_update_routine")

    simulation_engine.annual_reset()

    mock_field_annual_update_routine.assert_called_once_with()


def test_annual_mass_balance(simulation_engine: SimulationEngine) -> None:
    """
    Unit test for function annual_mass_balance() in simulation_engine.py
    """
    simulation_engine.annual_mass_balance(MagicMock(auto_spec=RufasTime))


def test_run_post_annual_routines(simulation_engine: SimulationEngine, mocker: MockerFixture) -> None:
    """
    Unit test for function _run_post_annual_routines in simulation_engine.py
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
    Unit test for function _advance_time in simulation_engine.py
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
    Unit test for function _run_simulation_main_loop in simulation_engine.py
    """

    # Arrange
    simulation_engine.time = (mock_time := MagicMock(auto_spec=RufasTime))
    mock_time.simulation_length_years = expected_iterations

    mock_annual_simulation = mocker.patch.object(simulation_engine, "_annual_simulation")

    # Act
    simulation_engine._run_simulation_main_loop()

    # Assert
    assert mock_annual_simulation.call_count == expected_iterations

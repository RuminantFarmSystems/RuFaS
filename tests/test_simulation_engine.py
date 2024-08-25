import pytest
from mock.mock import MagicMock
from pytest_mock import MockerFixture

from RUFAS.routines import Feed
from RUFAS.routines.EEE.EEE_manager import EEEManager
from RUFAS.simulation_engine import SimulationEngine
from RUFAS.data_structures.pen_manure_data import PenManureData
from RUFAS.time import Time


def test_simulation_engine_init(mocker: MockerFixture) -> None:
    """
    Unit test for the __init__ method in the SimulationEngine class.
    """

    # Arrange
    mock_initialize_simulation = mocker.patch.object(SimulationEngine, "_initialize_simulation")
    mock_time = mocker.MagicMock()
    mocker.patch("RUFAS.simulation_engine.Time", return_value=mock_time)

    # Act
    simulation_engine = SimulationEngine()

    # Assert
    mock_initialize_simulation.assert_called_once()
    assert simulation_engine.time == mock_time


@pytest.mark.parametrize("start_time, end_time", [(100, 200), (300, 400)])
def test_simulate(mocker: MockerFixture, start_time: int, end_time: int) -> None:
    """
    Unit test for function simulate in file RUFAS/simulation_engine.py
    """

    # Arrange
    patch_for_output_manager = mocker.patch("RUFAS.simulation_engine.om")
    patch_for_output_manager.get_error_and_warning_counts.return_value = (1, 2)
    mocker.patch("RUFAS.simulation_engine.timer.time", side_effect=[start_time, end_time])
    mocker.patch.object(SimulationEngine, "__init__", return_value=None)
    simulation_engine = SimulationEngine()
    simulation_engine.time = mocker.MagicMock()
    simulation_engine.time.simulation_day = 100
    simulation_engine.feed = mocker.MagicMock()

    simulation_engine.animal_manager = mocker.MagicMock()
    simulation_engine.animal_manager.heiferIIs = mocker.MagicMock()
    simulation_engine.animal_manager.cows = mocker.MagicMock()

    simulation_engine.manure_manager = mocker.MagicMock()
    simulation_engine.field_manager = mocker.MagicMock()
    simulation_engine.feed_manager = mocker.MagicMock()
    mock_estimate_emissions = mocker.patch.object(EEEManager, "estimate_all")
    patch_for_run_simulation_main_loop = mocker.patch.object(
        simulation_engine, "_run_simulation_main_loop", return_value=None
    )
    patch_for_animal_module_reporter = mocker.patch(
        "RUFAS.simulation_engine.routines.animal"
        ".animal_module_reporter.AnimalModuleReporter"
        ".report_end_of_simulation"
    )

    info_map = {
        "class": simulation_engine.__class__.__name__,
        "function": simulation_engine.simulate.__name__,
    }
    expected_simulation_time = end_time - start_time
    expected_log_message = f"Total simulation time is: {expected_simulation_time}"

    # Act
    simulation_engine.simulate()

    # Assert
    patch_for_run_simulation_main_loop.assert_called_once()
    expected_simulation_time = end_time - start_time
    expected_log_message = f"Total simulation time is: {expected_simulation_time}"
    patch_for_output_manager.add_log.assert_called_with("total_simulation_time", expected_log_message, info_map)
    patch_for_animal_module_reporter.assert_called_once_with(
        simulation_engine.animal_manager.life_cycle_manager,
        simulation_engine.time,
        simulation_engine.animal_manager.heiferIIs,
        simulation_engine.animal_manager.cows,
    )
    simulation_engine.feed_manager.query_available_feeds.assert_called_once()
    mock_estimate_emissions.assert_called_once()


def test_daily_simulation(mocker: MockerFixture) -> None:
    """
    Unit test for function _daily_simulation in file RUFAS/simulation_engine.py
    """

    # Arrange
    mocker.patch.object(SimulationEngine, "__init__", return_value=None)
    simulation_engine = SimulationEngine()
    simulation_engine.day_counter = 100
    simulation_engine.feed = mocker.MagicMock()
    simulation_engine.animal_manager = mocker.MagicMock()
    simulation_engine.animal_manager.simulation_day = expected_animal_manager_sim_day = 10
    simulation_engine.manure_manager = mocker.MagicMock()
    simulation_engine.field_manager = mocker.MagicMock()
    simulation_engine.weather = mocker.MagicMock()
    simulation_engine.time = mocker.MagicMock()
    simulation_engine.animal_manager.all_pens = mocker.MagicMock()
    mock_pen_manure_data = [mocker.MagicMock(autospec=PenManureData)]
    mocker.patch.object(simulation_engine.animal_manager, "collect_pen_manure_data", return_value=mock_pen_manure_data)

    patch_for_daily_feed_routine = mocker.patch("RUFAS.simulation_engine.routines.daily_feed_routine")
    patch_for_advance_time = mocker.patch.object(simulation_engine, "_advance_time")

    # Act
    simulation_engine._daily_simulation()

    # Assert
    simulation_engine.animal_manager.daily_updates.assert_called_once_with(
        simulation_engine.feed,
        simulation_engine.weather,
        simulation_engine.time,
    )
    simulation_engine.manure_manager.daily_update.assert_called_once_with(
        mock_pen_manure_data, expected_animal_manager_sim_day
    )
    simulation_engine.field_manager.daily_update_routine.assert_called_once_with(
        simulation_engine.weather, simulation_engine.time
    )
    patch_for_daily_feed_routine.assert_called_once_with(
        simulation_engine.feed,
        simulation_engine.field_manager,
        simulation_engine.animal_manager,
    )
    simulation_engine.time.record_time.assert_called_once()
    simulation_engine.weather.record_weather.assert_called_once_with(simulation_engine.time)
    patch_for_advance_time.assert_called_once()


def test_initialize_simulation(mocker: MockerFixture) -> None:
    """
    Unit test for function _initialize_simulation in file RUFAS/simulation_engine.py
    """

    # Arrange
    mocker.patch.object(SimulationEngine, "__init__", return_value=None)
    simulation_engine = SimulationEngine()

    simulation_engine.im = mocker.MagicMock()
    simulation_engine.im.get_data = MagicMock(side_effect=[{}, {}, {"manure_management_scenarios": {}}, {}])

    mock_weather = mocker.MagicMock()
    patch_for_weather = mocker.patch("RUFAS.simulation_engine.Weather", return_value=mock_weather)

    mock_time = mocker.MagicMock()
    simulation_engine.time = mock_time

    mock_feed = mocker.MagicMock()
    patch_for_feed = mocker.patch("RUFAS.simulation_engine.Feed", return_value=mock_feed)

    mock_animal_manager = mocker.MagicMock()
    mock_animal_manager.all_pens = mocker.MagicMock()
    mock_pen_manure_data = [mocker.MagicMock(autospec=PenManureData)]
    mocker.patch.object(mock_animal_manager, "collect_pen_manure_data", return_value=mock_pen_manure_data)
    patch_for_animal_manager = mocker.patch("RUFAS.simulation_engine.AnimalManager", return_value=mock_animal_manager)

    mock_manure_manager = mocker.MagicMock()
    patch_for_manure_manager = mocker.patch("RUFAS.simulation_engine.ManureManager", return_value=mock_manure_manager)

    mock_field_manager = mocker.MagicMock()
    patch_for_field_manager = mocker.patch("RUFAS.simulation_engine.FieldManager", return_value=mock_field_manager)

    mock_feed_manager = mocker.MagicMock()
    patch_for_feed_manager = mocker.patch("RUFAS.simulation_engine.FeedManager", return_value=mock_feed_manager)

    # Act
    simulation_engine._initialize_simulation()

    # Assert
    simulation_engine.im.get_data.assert_has_calls(
        [
            mocker.call("weather"),
            mocker.call("feed"),
            mocker.call("manure_management"),
            mocker.call("animal"),
        ]
    )

    patch_for_weather.assert_called_once_with({}, mock_time)
    patch_for_feed.assert_called_once_with({})
    patch_for_animal_manager.assert_called_once_with(
        {"manure_management_scenarios": {}}, mock_feed, mock_weather, mock_time
    )
    patch_for_manure_manager.assert_called_once_with(
        mock_pen_manure_data, mock_weather, mock_time, {"manure_management_scenarios": {}}
    )
    patch_for_field_manager.assert_called_once_with(manure_manager=mock_manure_manager, feed_manager=mock_feed_manager)
    patch_for_feed_manager.assert_called_once()


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
    mocker: MockerFixture, year_start_day: int, year_end_day: int, expected_day_count: int
) -> None:
    """
    Unit test for function _annual_simulation in file RUFAS/simulation_engine.py
    """

    # Arrange
    mocker.patch.object(SimulationEngine, "__init__", return_value=None)
    simulation_engine = SimulationEngine()

    patch_for_run_pre_annual_routines = mocker.patch.object(simulation_engine, "_run_pre_annual_routines")
    patch_for_run_post_annual_routines = mocker.patch.object(simulation_engine, "_run_post_annual_routines")
    patch_for_daily_simulation = mocker.patch.object(simulation_engine, "_daily_simulation")

    simulation_engine.time = mocker.MagicMock()
    simulation_engine.time.year_start_day = year_start_day
    simulation_engine.time.year_end_day = year_end_day

    # Act
    simulation_engine._annual_simulation()

    # Assert
    patch_for_run_pre_annual_routines.assert_called_once()
    assert patch_for_daily_simulation.call_count == expected_day_count
    patch_for_run_post_annual_routines.assert_called_once()


def test_run_post_annual_routines(mocker: MockerFixture) -> None:
    """
    Unit test for function _run_post_annual_routines in file RUFAS/simulation_engine.py
    """

    # Arrange
    mock_time = mocker.MagicMock(auto_spec=Time)

    mocker.patch.object(SimulationEngine, "__init__", return_value=None)
    simulation_engine = SimulationEngine()
    simulation_engine.annual_mass_balance = MagicMock()
    simulation_engine.annual_reset = MagicMock()
    simulation_engine.time = mock_time

    # Act
    simulation_engine._run_post_annual_routines()

    # Assert
    simulation_engine.annual_mass_balance.assert_called_once_with(simulation_engine.time)
    simulation_engine.annual_reset.assert_called_once()


def test_run_pre_annual_routines(mocker: MockerFixture) -> None:
    """
    Unit test for function _run_pre_annual_routines in file RUFAS/simulation_engine.py
    """

    # Arrange
    mocker.patch.object(SimulationEngine, "__init__", return_value=None)
    simulation_engine = SimulationEngine()
    simulation_engine.feed = MagicMock(auto_spec=Feed)

    patch_for_annual_feed_routine = mocker.patch("RUFAS.simulation_engine.routines.annual_feed_routine")

    # Act
    simulation_engine._run_pre_annual_routines()

    # Assert
    patch_for_annual_feed_routine.assert_called_once_with(simulation_engine.feed)


@pytest.mark.parametrize(
    "initial_simulation_day, time_str_return_value, expected_simulation_day",
    [
        (0, "1", 1),
        (10, "11", 11),
        (365, "366", 366),
    ],
)
def test_advance_time(
    mocker: MockerFixture,
    initial_simulation_day: int,
    time_str_return_value,
    expected_simulation_day: int,
) -> None:
    """
    Unit test for function _advance_time in file RUFAS/simulation_engine.py
    """

    # Arrange
    mocker.patch.object(SimulationEngine, "__init__", return_value=None)
    simulation_engine = SimulationEngine()
    mock_time = mocker.MagicMock()
    mock_time.simulation_day = initial_simulation_day + 1
    simulation_engine.time = mock_time
    simulation_engine.animal_manager = mocker.MagicMock()
    simulation_engine.animal_manager.simulation_day = initial_simulation_day

    # Act
    simulation_engine._advance_time()

    # Assert
    simulation_engine.time.advance.assert_called_once()
    assert simulation_engine.animal_manager.simulation_day == expected_simulation_day


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
def test_run_simulation_main_loop(mocker: MockerFixture, expected_iterations: int) -> None:
    """
    Unit test for function _run_simulation_main_loop in file RUFAS/simulation_engine.py
    """

    # Arrange
    mocker.patch.object(SimulationEngine, "__init__", return_value=None)
    simulation_engine = SimulationEngine()

    simulation_engine.time = mocker.MagicMock()
    simulation_engine.time.simulation_length_years = expected_iterations

    patch_for_annual_simulation = mocker.patch.object(simulation_engine, "_annual_simulation")

    # Act
    simulation_engine._run_simulation_main_loop()

    # Assert
    assert patch_for_annual_simulation.call_count == expected_iterations

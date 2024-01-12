import pytest
from pytest_mock import MockerFixture

from RUFAS.simulation_engine import SimulationEngine


def test_simulation_engine_init(mocker: MockerFixture) -> None:
    """
    Unit test for the __init__ method in the SimulationEngine class.
    """

    # Arrange
    mock_initialize_simulation = mocker.patch.object(
        SimulationEngine, "_initialize_simulation"
    )

    # Act
    _ = SimulationEngine()

    # Assert
    mock_initialize_simulation.assert_called_once()


@pytest.mark.parametrize("start_time, end_time", [(100, 200), (300, 400)])
def test_simulate(mocker: MockerFixture, start_time: int, end_time: int) -> None:
    """
    Unit test for function simulate in file RUFAS/simulation_engine.py
    """

    # Arrange
    patch_for_output_manager = mocker.patch("RUFAS.simulation_engine.om")
    mocker.patch(
        "RUFAS.simulation_engine.timer.time", side_effect=[start_time, end_time]
    )
    patch_for_sys_stdout_write = mocker.patch(
        "RUFAS.simulation_engine.sys.stdout.write"
    )
    mocker.patch.object(SimulationEngine, "__init__", return_value=None)
    simulation_engine = SimulationEngine()
    simulation_engine.day_counter = 100
    simulation_engine.state = mocker.MagicMock()
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

    # Act
    simulation_engine.simulate()

    # Assert
    patch_for_run_simulation_main_loop.assert_called_once()
    patch_for_sys_stdout_write.assert_called_once_with("\nSimulation Successful\n\n")
    expected_simulation_time = end_time - start_time
    expected_log_message = f"Total simulation time is: {expected_simulation_time}"
    patch_for_output_manager.add_log.assert_called_with(
        "total_simulation_time", expected_log_message, info_map
    )
    patch_for_animal_module_reporter.assert_called_once_with(
        simulation_engine.state.animal_manager, 100
    )


def test_daily_simulation(mocker: MockerFixture) -> None:
    """
    Unit test for function _daily_simulation in file RUFAS/simulation_engine.py
    """

    # Arrange
    mocker.patch.object(SimulationEngine, "__init__", return_value=None)
    simulation_engine = SimulationEngine()
    simulation_engine.day_counter = 100
    simulation_engine.state = mocker.MagicMock()
    simulation_engine.weather = mocker.MagicMock()
    simulation_engine.time = mocker.MagicMock()

    patch_for_simulate_daily_manure_manager = mocker.patch(
        "RUFAS.simulation_engine.simulate_daily_manure_manager"
    )
    patch_for_daily_feed_routine = mocker.patch(
        "RUFAS.simulation_engine.routines.daily_feed_routine"
    )
    patch_for_advance_time = mocker.patch.object(simulation_engine, "_advance_time")

    # Act
    simulation_engine._daily_simulation()

    # Assert
    simulation_engine.state.animal_manager.daily_updates.assert_called_once_with(
        simulation_engine.state.feed, simulation_engine.weather, simulation_engine.time
    )
    patch_for_simulate_daily_manure_manager.assert_called_once_with(
        simulation_engine.state.manure_manager, simulation_engine.state.animal_manager
    )
    simulation_engine.state.field_manager.daily_update_routine.assert_called_once_with(
        simulation_engine.weather, simulation_engine.time
    )
    patch_for_daily_feed_routine.assert_called_once_with(
        simulation_engine.state.feed,
        simulation_engine.state.field_manager,
        simulation_engine.state.animal_manager,
    )
    simulation_engine.time.record_time.assert_called_once()
    simulation_engine.weather.record_weather.assert_called_once_with(
        simulation_engine.time
    )
    patch_for_advance_time.assert_called_once()


def test_initialize_simulation(mocker: MockerFixture) -> None:
    """
    Unit test for function _initialize_simulation in file RUFAS/simulation_engine.py
    """

    # Arrange
    mocker.patch.object(SimulationEngine, "__init__", return_value=None)
    simulation_engine = SimulationEngine()

    config_data = {"set_seed": True, "seed": 42}
    patch_for_get_data = mocker.patch(
        "RUFAS.simulation_engine.im.get_data", side_effect=[config_data, {}]
    )

    mock_config = mocker.MagicMock(**config_data)
    patch_for_config = mocker.patch(
        "RUFAS.simulation_engine.Config", return_value=mock_config
    )

    mock_weather = mocker.MagicMock()
    patch_for_weather = mocker.patch(
        "RUFAS.simulation_engine.Weather", return_value=mock_weather
    )

    mock_time = mocker.MagicMock()
    patch_for_time = mocker.patch(
        "RUFAS.simulation_engine.Time", return_value=mock_time
    )

    mock_feed_manager = mocker.MagicMock()
    patch_for_feed_manager = mocker.patch(
        "RUFAS.simulation_engine.FeedManager", return_value=mock_feed_manager
    )

    mock_state = mocker.MagicMock()
    patch_for_state = mocker.patch(
        "RUFAS.simulation_engine.State", return_value=mock_state
    )

    patch_for_random_seed = mocker.patch("RUFAS.simulation_engine.random.seed")
    patch_for_numpy_seed = mocker.patch("RUFAS.simulation_engine.numpy.random.seed")

    # Act
    simulation_engine._initialize_simulation()

    # Assert
    patch_for_get_data.assert_has_calls([mocker.call("config"), mocker.call("weather")])
    patch_for_random_seed.assert_called_once_with(42)
    patch_for_numpy_seed.assert_called_once_with(42)

    patch_for_config.assert_called_once_with(config_data)
    patch_for_weather.assert_called_once_with({}, mock_config)
    patch_for_time.assert_called_once_with(mock_config)
    patch_for_feed_manager.assert_called_once()
    patch_for_state.assert_called_once_with(mock_config, mock_weather, mock_time, mock_feed_manager)


@pytest.mark.parametrize(
    "day, update_interval, expected_output, should_write",
    [
        # Day is a multiple of update_interval, should write first char
        (0, 50, "-", True),
        # Day is a multiple of update_interval, should write second char
        (50, 50, "\\", True),
        # Day is a multiple of update_interval, should write third char
        (100, 50, "|", True),
        # Day is a multiple of update_interval, should write fourth char
        (150, 50, "/", True),
        # Day is not a multiple of update_interval, should not write
        (51, 50, "", False),
    ],
)
def test_visualize_sim_progress(
    mocker: MockerFixture,
    day: int,
    update_interval: int,
    expected_output: str,
    should_write: bool,
) -> None:
    """
    Unit test for function _visualize_sim_progress in file RUFAS/simulation_engine.py
    """

    # Arrange
    mock_stdout = mocker.patch("RUFAS.simulation_engine.sys.stdout")

    # Act
    SimulationEngine._visualize_sim_progress(day, update_interval)

    # Assert
    if should_write:
        mock_stdout.write.assert_called_with(expected_output)
    else:
        mock_stdout.write.assert_not_called()


@pytest.mark.parametrize(
    "end_year_side_effect, expected_day_count",
    [
        # Simulate 1 year end
        ([False, True], 1),
        # Simulate 2 years end
        ([False, False, True], 2),
        # Simulate 4 years end
        ([False] * 4 + [True], 4),
    ],
)
def test_annual_simulation(
    mocker: MockerFixture, end_year_side_effect: list, expected_day_count: int
) -> None:
    """
    Unit test for function _annual_simulation in file RUFAS/simulation_engine.py
    """

    # Arrange
    mocker.patch.object(SimulationEngine, "__init__", return_value=None)
    simulation_engine = SimulationEngine()

    patch_for_run_pre_annual_routines = mocker.patch.object(
        simulation_engine, "_run_pre_annual_routines"
    )
    patch_for_run_post_annual_routines = mocker.patch.object(
        simulation_engine, "_run_post_annual_routines"
    )
    patch_for_daily_simulation = mocker.patch.object(
        simulation_engine, "_daily_simulation"
    )
    patch_for_visualize_sim_progress = mocker.patch.object(
        simulation_engine, "_visualize_sim_progress"
    )

    simulation_engine.time = mocker.MagicMock()
    simulation_engine.time.end_year.side_effect = end_year_side_effect

    # Act
    simulation_engine._annual_simulation()

    # Assert
    patch_for_run_pre_annual_routines.assert_called_once()
    assert patch_for_visualize_sim_progress.call_count == expected_day_count
    assert patch_for_daily_simulation.call_count == expected_day_count
    patch_for_run_post_annual_routines.assert_called_once()


def test_run_post_annual_routines(mocker: MockerFixture) -> None:
    """
    Unit test for function _run_post_annual_routines in file RUFAS/simulation_engine.py
    """

    # Arrange
    mocker.patch.object(SimulationEngine, "__init__", return_value=None)
    simulation_engine = SimulationEngine()

    simulation_engine.state = mocker.MagicMock()
    simulation_engine.time = mocker.MagicMock()

    # Act
    simulation_engine._run_post_annual_routines()

    # Assert
    simulation_engine.state.annual_mass_balance.assert_called_once_with(
        simulation_engine.time
    )
    simulation_engine.state.annual_reset.assert_called_once()
    simulation_engine.time.advance.assert_called_once()


def test_run_pre_annual_routines(mocker: MockerFixture) -> None:
    """
    Unit test for function _run_pre_annual_routines in file RUFAS/simulation_engine.py
    """

    # Arrange
    mocker.patch.object(SimulationEngine, "__init__", return_value=None)
    simulation_engine = SimulationEngine()

    simulation_engine.state = mocker.MagicMock()

    patch_for_annual_feed_routine = mocker.patch(
        "RUFAS.simulation_engine.routines.annual_feed_routine"
    )

    # Act
    simulation_engine._run_pre_annual_routines()

    # Assert
    patch_for_annual_feed_routine.assert_called_once_with(simulation_engine.state.feed)


@pytest.mark.parametrize(
    "print_day, initial_simulation_day, to_str_return_value, expected_simulation_day",
    [
        (True, 0, "Day 1", 1),
        (False, 0, "Day 1", 1),
        (True, 10, "Day 11", 11),
        (False, 10, "Day 11", 11),
        (True, 365, "Day 366", 366),
        (False, 365, "Day 366", 366),
    ],
)
def test_advance_time(
    mocker: MockerFixture,
    print_day: bool,
    initial_simulation_day: int,
    to_str_return_value: str,
    expected_simulation_day: int,
) -> None:
    """
    Unit test for function _advance_time in file RUFAS/simulation_engine.py
    """

    # Arrange
    mocker.patch.object(SimulationEngine, "__init__", return_value=None)
    simulation_engine = SimulationEngine()

    simulation_engine.time = mocker.MagicMock()
    simulation_engine.time.to_str.return_value = to_str_return_value
    simulation_engine.state = mocker.MagicMock()
    simulation_engine.state.animal_manager.simulation_day = initial_simulation_day
    patch_for_add_log = mocker.patch("RUFAS.simulation_engine.om.add_log")

    # Act
    simulation_engine._advance_time(print_day)

    # Assert
    simulation_engine.time.advance.assert_called_once()
    assert (
        simulation_engine.state.animal_manager.simulation_day == expected_simulation_day
    )

    if print_day:
        expected_log_message = f"simulating day: {to_str_return_value}"
        expected_info_map = {
            "class": "SimulationEngine",
            "function": "_advance_time",
            "print_day": print_day,
        }
        patch_for_add_log.assert_called_once_with(
            "simulation_day", expected_log_message, expected_info_map
        )
    else:
        patch_for_add_log.assert_not_called()


@pytest.mark.parametrize(
    "end_simulation_side_effect, expected_iterations",
    [
        # Simulate a loop that runs once
        ([False, True], 1),
        # Simulate a loop that runs twice
        ([False, False, True], 2),
        # Simulate a loop that runs three times
        ([False, False, False, True], 3),
    ],
)
def test_run_simulation_main_loop(
    mocker: MockerFixture, end_simulation_side_effect: list, expected_iterations: int
) -> None:
    """
    Unit test for function _run_simulation_main_loop in file RUFAS/simulation_engine.py
    """

    # Arrange
    mocker.patch.object(SimulationEngine, "__init__", return_value=None)
    simulation_engine = SimulationEngine()

    simulation_engine.time = mocker.MagicMock()
    simulation_engine.time.end_simulation.side_effect = end_simulation_side_effect

    patch_for_annual_simulation = mocker.patch.object(
        simulation_engine, "_annual_simulation"
    )

    # Act
    simulation_engine._run_simulation_main_loop()

    # Assert
    assert patch_for_annual_simulation.call_count == expected_iterations

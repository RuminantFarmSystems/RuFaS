import pytest
from mock.mock import MagicMock, call
from pytest import approx
from pytest_mock.plugin import MockerFixture

from RUFAS.general_constants import GeneralConstants
from RUFAS.simulation_engine import SimulationEngine
from RUFAS.util import Utility


def test_annual_reset():
    """Unit test for function annual_reset in classes"""
    pass


def test_annual_mass_balance():
    """Unit test for function annual_mass_balance in classes"""
    pass


def test_calc_sim_length():
    """Unit test for function calc_sim_length in classes"""
    pass


def test_to_str():
    """Unit test for function to_str in classes"""
    pass


def test_advance():
    """Unit test for function advance in classes"""
    pass


def test_end_year():
    """Unit test for function end_year in classes"""
    pass


def test_end_simulation():
    """Unit test for function end_simulation in classes"""
    pass


def test_general_constants() -> None:
    """Tests the general constants in file general_constants.py."""
    constants = GeneralConstants
    assert constants.GRAMS_TO_KG == approx(0.001)
    assert constants.LITERS_TO_CUBIC_METERS == approx(0.001)
    assert constants.KG_TO_CUBIC_METERS == approx(0.001)
    assert constants.DAYS_PER_YEAR == 365
    assert constants.SECONDS_PER_DAY == 86400
    assert constants.WATER_DENSITY_KG_PER_LITER == approx(0.997)
    assert constants.WATER_DENSITY_KG_PER_M3 == approx(0.997 * 0.001)


def test_is_leap_year():
    """Unit test for function is_leap_year in classes"""
    pass


@pytest.fixture
def patch_simulation_engine(mocker: MockerFixture) -> SimulationEngine:
    """Returns a mocked SimulationEngine"""
    mocker.patch("RUFAS.simulation_engine.SimulationEngine._initialize_simulation")

    sim_eng = SimulationEngine()
    sim_eng.config = MagicMock()
    sim_eng.weather = MagicMock()
    sim_eng.time = MagicMock()
    sim_eng.state = MagicMock()

    return sim_eng


def test_init_simulation_engine(
    patch_simulation_engine: SimulationEngine, mocker: MockerFixture
) -> None:
    """Unit test for function __init__ in file RUFAS/simulation_engine.py"""
    assert patch_simulation_engine.config is not None
    assert patch_simulation_engine.weather is not None
    assert patch_simulation_engine.time is not None
    assert patch_simulation_engine.state is not None
    patch_simulation_engine._initialize_simulation.assert_called_once()


def test_simulate(
    patch_simulation_engine: SimulationEngine, mocker: MockerFixture
) -> None:
    """Unit test for function simulate in file RUFAS/simulation_engine.py"""
    patch_for_run_simulation_main_loop = mocker.patch(
        "RUFAS.simulation_engine.SimulationEngine._run_simulation_main_loop"
    )
    sim_eng = patch_simulation_engine
    sim_eng.simulate()
    patch_for_run_simulation_main_loop.assert_called_once()


def test_run_simulation_main_loop(patch_simulation_engine: SimulationEngine) -> None:
    """Unit test for function simulate in file RUFAS/simulation_engine.py"""
    sim_eng = patch_simulation_engine
    sim_eng.time.end_simulation = MagicMock(side_effect=[False, True])
    sim_eng._annual_simulation = MagicMock()
    sim_eng._run_simulation_main_loop()
    sim_eng.time.end_simulation.assert_has_calls([call(), call()])
    sim_eng._annual_simulation.assert_called_once()


def test_daily_simulation(
    patch_simulation_engine: SimulationEngine, mocker: MockerFixture
) -> None:
    """Unit test for function _daily_simulation in file RUFAS/simulation_engine.py"""
    mocker.patch("RUFAS.routines.daily_feed_routine")
    mocker.patch("RUFAS.simulation_engine.SimulationEngine._advance_time")
    patch_simulation_engine._daily_simulation()
    for mocked in mocker._patches_and_mocks:
        assert mocked[1].call_count == 1
    patch_simulation_engine.state.field_manager.daily_update_routine.assert_called_once()
    patch_simulation_engine.time.record_time.assert_called_once()
    patch_simulation_engine.weather.record_weather.assert_called_once()


def test_advance_time(
    patch_simulation_engine: SimulationEngine, mocker: MockerFixture
) -> None:
    """Unit test for function _advance_time in file RUFAS/simulation_engine.py"""
    mocker.patch("RUFAS.time.Time.to_str")
    mocker.patch("RUFAS.time.Time.advance")
    patch_simulation_engine.state.animal_manager.simulation_day = 1
    patch_simulation_engine._advance_time(False)
    patch_simulation_engine._advance_time(True)
    assert patch_simulation_engine.time.advance.call_count == 2
    assert patch_simulation_engine.time.to_str.call_count == 1
    assert patch_simulation_engine.state.animal_manager.simulation_day == 3


def test_input_prompt():
    """Unit test for function input_prompt in file user_prompt.py"""
    pass


class DummyClass:
    def __init__(self, value: int) -> None:
        self.value = value


class DummyNestedClass:
    def __init__(self, value: int) -> None:
        self.value = DummyClass(value)


@pytest.mark.parametrize(
    "input_obj, depth, max_depth, expected_output",
    [
        (42, 0, 1, 42),
        (3.14, 0, 1, 3.14),
        ("test", 0, 1, "test"),
        (True, 0, 1, True),
        (False, 0, 1, False),
        (None, 0, 1, None),
        ([], 0, 1, []),
        ((), 0, 1, ()),
        ({}, 0, 1, {}),
        (set(), 0, 1, []),
        ([1, "test", True], 0, 1, [1, "test", True]),
        ((1, "test", True), 0, 1, (1, "test", True)),
        ({1, 2, 3}, 0, 1, [1, 2, 3]),
        ({"a": 1, "b": 2}, 0, 1, {"a": 1, "b": 2}),
        ({"a": [1, 2, 3], "b": {"c": 4}}, 0, 3, {"a": [1, 2, 3], "b": {"c": 4}}),
        (["a", (1, 2), {"b": 3}], 0, 2, ["a", (1, 2), {"b": 3}]),
        ([1, [2, [3, 4], 5], 6], 0, 2, [1, [2, "[3, 4]", 5], 6]),
        ({"a": {"b": {"c": 42}}}, 0, 2, {"a": {"b": {"c": 42}}}),
        (DummyClass(42), 0, 1, {"value": 42}),
        (DummyNestedClass(42), 0, 2, {"value": {"value": 42}}),
        ({"a": {"b": DummyClass(42)}}, 0, 3, {"a": {"b": {"value": 42}}}),
        (
            [42, "test", 3.14, True, None, [1, 2, 3], {"a": 1}],
            0,
            2,
            [42, "test", 3.14, True, None, [1, 2, 3], {"a": 1}],
        ),
    ],
)
def test_make_serializable_recursive(
    input_obj: object,
    depth: int,
    max_depth: int,
    expected_output: object,
    mocker: MockerFixture,
) -> None:
    """Unit test for function _make_serializable() in file util.py"""
    # Arrange
    _ = mocker.patch.object(Utility, "_get_str", side_effect=lambda x: str(x))

    # Act
    result = Utility._make_serializable(input_obj, depth, max_depth)

    # Assert
    assert result == expected_output

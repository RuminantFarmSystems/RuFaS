"""
RUFAS: Ruminant Farm Systems Model
File name: test_misc.py
Description: Implements test cases
Author(s): Pooya Hekmati, sh2235@cornell.edu
"""

import pytest
from mock.mock import MagicMock
from pytest import approx, raises
from pytest_mock.plugin import MockerFixture

from RUFAS.simulation_engine import SimulationEngine
from RUFAS.util import Utility


def test_annual_reset():
    """Unit test for function annual_reset in file classes.py"""
    pass


def test_annual_mass_balance():
    """Unit test for function annual_mass_balance in file classes.py"""
    pass


def test_calc_sim_length():
    """Unit test for function calc_sim_length in file classes.py"""
    pass


def test_to_str():
    """Unit test for function to_str in file classes.py"""
    pass


def test_advance():
    """Unit test for function advance in file classes.py"""
    pass


def test_end_year():
    """Unit test for function end_year in file classes.py"""
    pass


def test_end_simulation():
    """Unit test for function end_simulation in file classes.py"""
    pass


def test_is_leap_year():
    """Unit test for function is_leap_year in file classes.py"""
    pass


@pytest.fixture
def patch_simulation_engine(mocker: MockerFixture) -> SimulationEngine:
    """Returns a mocked SimulationEngine"""
    mocker.patch(
            'RUFAS.simulation_engine.SimulationEngine._initialize_simulation')

    sim_eng = SimulationEngine('dummy_path')
    sim_eng.config = MagicMock()
    sim_eng.weather = MagicMock()
    sim_eng.time = MagicMock()
    sim_eng.state = MagicMock()
    sim_eng.output = MagicMock()

    return sim_eng


def test_init_simulation_engine(patch_simulation_engine: SimulationEngine) -> None:
    """Unit test for function __init__ in file RUFAS/simulation_engine.py"""
    patch_simulation_engine._initialize_simulation.assert_called_once_with(
            'dummy_path')


def test_simulate(patch_simulation_engine: SimulationEngine, mocker: MockerFixture) -> None:
    """Unit test for function simulate in file RUFAS/simulation_engine.py"""
    mocker.patch(
            'RUFAS.simulation_engine.SimulationEngine._run_simulation_main_loop')
    mocker.patch(
            'RUFAS.simulation_engine.SimulationEngine._show_final_messages')
    sim_eng = patch_simulation_engine
    sim_eng.simulate()
    sim_eng._run_simulation_main_loop.assert_called_once()
    sim_eng.output.finalize.assert_called_once_with(
            sim_eng.state, sim_eng.weather, sim_eng.time)
    sim_eng._show_final_messages.assert_called_once()


def test_show_final_messages(
        patch_simulation_engine: SimulationEngine, mocker: MockerFixture) -> None:
    """Unit test for function _show_final_messages in file RUFAS/simulation_engine.py"""
    mocker.patch('sys.stdout.write')
    patch_simulation_engine._show_final_messages(1, 1)
    assert mocker._mocks[1].call_count == 3


def test_daily_simulation(
        patch_simulation_engine: SimulationEngine, mocker: MockerFixture) -> None:
    """Unit test for function _daily_simulation in file RUFAS/simulation_engine.py"""
    mocker.patch('RUFAS.routines.daily_animal_routine')
    mocker.patch('RUFAS.routines.daily_manure_storage_routine')
    mocker.patch('RUFAS.routines.daily_fields_routine')
    mocker.patch('RUFAS.routines.daily_feed_routine')
    mocker.patch('RUFAS.simulation_engine.SimulationEngine._advance_time')
    patch_simulation_engine._daily_simulation()
    assert patch_simulation_engine.output.daily_update.call_count == 1
    for mocked in mocker._mocks:
        assert mocked.call_count == 1


def test_advance_time(
        patch_simulation_engine: SimulationEngine, mocker: MockerFixture) -> None:
    """Unit test for function _advance_time in file RUFAS/simulation_engine.py"""
    mocker.patch('RUFAS.classes.Time.to_str')
    mocker.patch('RUFAS.classes.Time.advance')
    patch_simulation_engine.state.animal_management.simulation_day = 1
    patch_simulation_engine._advance_time(False)
    patch_simulation_engine._advance_time(True)
    assert patch_simulation_engine.time.advance.call_count == 2
    assert patch_simulation_engine.time.to_str.call_count == 1
    assert patch_simulation_engine.state.animal_management.simulation_day == 3


def test_input_prompt():
    """Unit test for function input_prompt in file user_prompt.py"""
    pass


def test_query():
    """Unit test for function query in file util.py"""
    pass


def test_get_base_dir():
    """Unit test for function get_base_dir in file util.py"""
    pass


def test_read_json_file():
    """Unit test for function read_json_file in file util.py"""
    pass


def test_LP_solve():
    """Unit test for function LP_solve in file util.py"""
    pass


def test_create_LP_problem():
    """Unit test for function create_LP_problem in file util.py"""
    pass


def test_is_correct_structure():
    """Unit test for function is_correct_structure in file util.py"""
    pass


def test_generate_LP_vars():
    """Unit test for function generate_LP_vars in file util.py"""
    pass


def test_add_LP_constraints():
    """Unit test for function add_LP_constraints in file util.py"""
    pass


def test_solve_with_fastest_solver():
    """Unit test for function solve_with_fastest_solver in file util.py"""
    pass


def test_organize_results():
    """Unit test for function organize_results in file util.py"""
    pass


def test_LP_print():
    """Unit test for function LP_print in file util.py"""
    pass


def test_calc_average() -> None:
    """Unit test for function calc_average in file util.py"""
    # Normal case
    result = Utility.calc_average(num_values=9, cur_avg=5, new_value=6)
    actual_new_num_values, actual_new_avg = result
    assert actual_new_num_values == 10
    assert actual_new_avg == approx(5.1)  # (9 * 5 + 6) / 10

    # Given a count of 0 and an average value of 0.0,
    # the function should return whatever the new value is.
    result = Utility.calc_average(num_values=0, cur_avg=0.0, new_value=6.0)
    actual_new_num_values, actual_new_avg = result
    assert actual_new_num_values == 1
    assert actual_new_avg == approx(6.0)


def test_remove_items_from_list_by_indices() -> None:
    """Unit test for function remove_items_from_list_by_indices in file util.py"""
    # Given an empty list and an empty list of removal indices,
    # the function should do nothing.
    arr = []
    del_idx = []
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert len(arr) == 0

    # Given a non-empty list and an empty list of removal indices,
    # the function should do nothing.
    arr = [0, 1, 2]
    del_idx = []
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert arr == [0, 1, 2]

    # Given a list of size 1 and the removal index of 0,
    # the function should return an empty list.
    arr = [0]
    del_idx = [0]
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert len(arr) == 0

    # Given a list of size 2 and one valid removal index,
    # the function should return a correct list of size 1.
    arr = [10, 20]
    del_idx = [0]
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert arr == [20]

    arr = [10, 20]
    del_idx = [1]
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert arr == [10]

    # Given a list of size 3 and a list of 2 removal indices,
    # the function should return a correct list of size 1.
    arr = [10, 20, 30]
    del_idx = [0, 1]
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert arr == [30]

    arr = [10, 20, 30]
    del_idx = [1, 2]
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert arr == [10]

    arr = [10, 20, 30]
    del_idx = [0, 2]
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert arr == [20]

    # Given an empty list and a non-empty list of removal indices,
    # the function should raise IndexError.
    arr = []
    del_idx = [0]
    with raises(IndexError):
        Utility.remove_items_from_list_by_indices(arr, del_idx)


def test_percent_calculator() -> None:
    """Unit test for function percent_calculator in file util.py"""
    # Normal case
    # Given any random non-zero denominator,
    # the function should return correct percentages.
    pc = Utility.percent_calculator(denominator=20)
    assert pc(0) == approx(0.0)
    assert pc(20) == approx(100.0)
    assert pc(8) == approx(40.0)  # e.g., 8/20 = 40%
    assert pc(-8) == approx(-40.0)
    assert pc(24) == approx(120.0)

    # Given a denominator of 100,
    # the function should return the numerator as percentage.
    pc = Utility.percent_calculator(denominator=100)
    assert pc(0.0) == approx(0.0)
    assert pc(12.3) == approx(12.3)
    assert pc(100.0) == approx(100.0)

    # Given a 0 denominator, the function should raise a ZeroDivisionError.
    pc = Utility.percent_calculator(denominator=0)
    with raises(ZeroDivisionError):
        pc(1.0)

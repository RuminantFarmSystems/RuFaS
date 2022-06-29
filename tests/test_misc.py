"""
RUFAS: Ruminant Farm Systems Model
File name: test_misc.py
Description: Implements test cases
Author(s): Pooya Hekmati, sh2235@cornell.edu
"""

import mock
from mock.mock import MagicMock
from pytest_mock.plugin import MockerFixture
import pytest
from RUFAS.simulation_engine import SimulationEngine


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

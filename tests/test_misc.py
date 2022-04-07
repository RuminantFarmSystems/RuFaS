"""
RUFAS: Ruminant Farm Systems Model
File name: test_misc.py
Description: Implements test cases
Author(s): Pooya Hekmati, sh2235@cornell.edu
"""

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


def init_simulation_engine(mocker):
    mocker.patch('SimulationEngine._initialize_simulation', return_value=None)
    print(mocker)
    sim_eng = SimulationEngine('dummy_path')
    import pdb;pdb.set_trace()
    assert 1==0


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

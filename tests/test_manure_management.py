"""
RUFAS: Ruminant Farm Systems Model
File name: old_manure_management.py
Description: Implements test cases
Author(s): Sadman Chowdhury, skc86@cornell.edu
"""
from typing import List

from pytest import approx

from RUFAS.routines.manure_management.gas_emissions.gas_emissions import GasEmissions
from RUFAS.simulation_engine import SimulationEngine


def assert_two_lists_equal(expected_items: List, result_items: List) -> None:
    """Checks equality of two lists element-wise.

    Args:
        expected_items: list of expected results.
        result_items: list of results to be tested.

    Returns:
        None

    """
    assert len(expected_items) == len(result_items)
    for expected, result in zip(expected_items, result_items):
        assert expected == approx(result)


def test_convert_temp_C_to_K():
    """Unit test for function convert_temp_C_to_K in file gas_emissions.py"""
    temps_in_C = [-273.15, 0, 100]
    expected_temps = [0, 273.15, 373.15]
    result_temps = [GasEmissions.convert_temp_C_to_K(
        temp) for temp in temps_in_C]
    assert_two_lists_equal(expected_temps, result_temps)


def test_calc_modified_hours():
    """Unit test for function calc_modified_hours in file gas_emissions.py"""
    hours = [15, 14, 5, 4]
    expected_hours = [0.2857129, 0.3999013, -0.3999013, -0.2857141]
    result_hours = [GasEmissions.calc_modified_hours(hour) for hour in hours]
    assert_two_lists_equal(expected_hours, result_hours)


def test_calc_Kh():
    """Unit test for function calc_Kh in file gas_emissions.py"""
    temp_in_k = 200
    value_to_test = GasEmissions.calc_Kh(temp_in_k)
    assert value_to_test == 501187.2336272715


def test_calc_Ka():
    """Unit test for function calc_Ka in file gas_emissions.py"""
    temp_in_k = 200
    ph = 10
    value_to_test = GasEmissions.calc_Ka(temp_in_k, ph)
    assert value_to_test == 5492.361063180863


def test_calc_Q():
    """Unit test for function calc_Q in file gas_emissions.py"""
    temp_in_k = 200
    ph = 10
    value_to_test = GasEmissions.calc_Q(temp_in_k, 10)
    assert value_to_test == 2752701247.3377566


def test_calc_ruc():
    """Unit test for function calc_ruc in file gas_emissions.py"""
    pass


def test_calc_vmax():
    """Unit test for function calc_vmax in file gas_emissions.py"""
    pass


def test_calc_Kmc():
    """Unit test for function calc_Kmc in file gas_emissions.py"""
    pass


def test_calc_henry_constant():
    """Unit test for function calc_henry_constant in file gas_emissions.py"""
    T = 250
    value_to_test = GasEmissions.calc_henry_constant(T)
    assert value_to_test == 126726.5385349147


def test_calc_air_friction_velocity():
    """Unit test for function calc_air_friction_velocity in file 
    gas_emissions.py"""
    pass


def test_calc_mass_transfer_coefficient_liquid():
    """Unit test for function calc_mass_transfer_coefficient_liquid in file 
    gas_emissions.py"""
    pass


def test_calc_resistance_to_mass_transfer():
    """Unit test for function calc_resistance_to_mass_transfer in file 
    gas_emissions.py"""
    pass


def test_calc_overall_mass_transfer_coefficient():
    """Unit test for function calc_vmax in file gas_emissions.py"""
    pass


def test_calc_concentration_of_ammonia_in_manure():
    """Unit test for function calc_concentration_of_ammonia_in_manure in file gas_emissions.py"""
    pass


def test_calc_E_N20_manure():
    """Unit test for function calc_E_N20_manure in file gas_emissions.py"""
    pass

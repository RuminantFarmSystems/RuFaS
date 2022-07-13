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
    result = 501187.2336272715
    assert value_to_test == result


def test_calc_Ka():
    """Unit test for function calc_Ka in file gas_emissions.py"""
    temp_in_k = 200
    ph = 10
    value_to_test = GasEmissions.calc_Ka(temp_in_k, ph)
    result = 5492.361063180863
    assert value_to_test == result


def test_calc_Q():
    """Unit test for function calc_Q in file gas_emissions.py"""
    temp_in_k = 200
    ph = 10
    value_to_test = GasEmissions.calc_Q(temp_in_k, 10)
    result = 2752701247.3377566
    assert value_to_test == result


def test_calc_ruc():
    """Unit test for function calc_ruc in file gas_emissions.py"""
    temp_in_k = -6463
    #kmc = 841709169.5924
    # 10642073358.417162
    cu = 1
    value_to_test = GasEmissions.calc_ruc(temp_in_k, cu)
    result = 12.643409066016016
    assert value_to_test == result


def test_calc_vmax():
    """Unit test for function calc_vmax in file gas_emissions.py"""
    temp_in_k = -6463
    value_to_test = GasEmissions.calc_vmax(temp_in_k)
    result = 10642073358.417162
    assert value_to_test == result


def test_calc_Kmc():
    """Unit test for function calc_Kmc in file gas_emissions.py"""
    temp_in_k = -5914
    value_to_test = GasEmissions.calc_kmc(temp_in_k)
    result = 916332804.3735441
    assert value_to_test == result


def test_calc_henry_constant():
    """Unit test for function calc_henry_constant in file gas_emissions.py"""
    T = 250
    value_to_test = GasEmissions.calc_henry_constant(T)
    result = 126726.53853495147
    assert value_to_test == result


def test_calc_air_friction_velocity():
    """Unit test for function calc_air_friction_velocity in file
    gas_emissions.py"""
    Va = 1
    value_to_test = GasEmissions.calc_air_friction_velocity(Va)
    result = 0.02
    assert value_to_test == result


def test_calc_mass_transfer_coefficient_gaseous():
    """Unit test for function calc_mass_transfer_coefficient_gaseous in file
   gas_emissions.py"""
    U = 1
    SC = 2
    value_to_test = GasEmissions.calc_mass_transfer_coefficient_gaseous(U, SC)
    result = 0.030037008951454235
    assert value_to_test == result


def test_calc_mass_transfer_coefficient_liquid():
    """Unit test for function calc_mass_transfer_coefficient_liquid in file 
    gas_emissions.py"""
    T = 100
    value_to_test = GasEmissions.calc_mass_transfer_coefficient_liquid(T)
    result = 0.0001417
    assert value_to_test == result


def test_calc_resistance_to_mass_transfer():
    """Unit test for function calc_resistance_to_mass_transfer in file 
    gas_emissions.py"""
    Rs = 3.456
    Rc = 6.544
    value_to_test = GasEmissions.calc_resistance_to_mass_transfer(Rs, Rc)
    result = 10.0
    assert value_to_test == result


def test_calc_overall_mass_transfer_coefficient():
    """Unit test for function calc_vmax in file gas_emissions.py"""
    H = 1
    Kg = 2
    Kl = 3
    Rm = 4
    value_to_test = GasEmissions.calc_overall_mass_transfer_coefficient(
        H, Kg, Kl, Rm)
    result = 0.20689655172413796
    assert value_to_test == result


def test_calc_concentration_of_ammonia_in_manure():
    """Unit test for function calc_concentration_of_ammonia_in_manure in file gas_emissions.py"""
    F = 10
    C_tan = 3
    value_to_test = GasEmissions.calc_concentration_of_ammonia_in_manure(
        F, C_tan)
    result = 30
    assert value_to_test == result


def test_calc_E_N20_manure():
    """Unit test for function calc_E_N20_manure in file gas_emissions.py"""
    EF_n20 = 1000
    A_storage = 1000
    value_to_test = GasEmissions.calc_E_N20_manure(EF_n20, A_storage)
    result = 1000
    assert value_to_test == result


def test_calc_ammonia_flux():
    """Unit test for function calc_ammonia_flux in file gas_emissions.py"""
    K = 1
    Cm = 2
    H = 3
    Ca = 4
    value_to_test = GasEmissions.calc_ammonia_flux(K, Cm, H, Ca)
    result = -36000
    assert value_to_test == result

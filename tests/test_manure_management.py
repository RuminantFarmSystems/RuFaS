"""
RUFAS: Ruminant Farm Systems Model
File name: old_manure_management.py
Description: Implements test cases
Author(s): Sadman Chowdhury, skc86@cornell.edu
"""
from typing import List

from pytest import approx

from RUFAS.routines.manure_management.gas_emissions.gas_emissions import GasEmissions
from RUFAS.routines.manure_management.misc.constants import ManureManagementConstants
from RUFAS.routines.manure_management.misc.manure import Manure
from RUFAS.simulation_engine import SimulationEngine


# --------------------------- Test misc module

def test_manure_init() -> None:
    """Unit test for function __init__ in file manure.py"""

    # Given no arguments, a new Manure object should have all attributes
    # initially set to 0.
    manure = Manure()
    assert manure.U == approx(0.0)
    assert manure.TAN_s == approx(0.0)
    assert manure.MN == approx(0.0)
    assert manure.Mkg == approx(0.0)
    assert manure.TSd == approx(0.0)
    assert manure.VSd == approx(0.0)
    assert manure.VSnd == approx(0.0)
    assert manure.WIP_frac == approx(0.0)
    assert manure.WOP_frac == approx(0.0)
    assert manure.p_excrt_manure == approx(0.0)
    assert manure.p_frac == approx(0.0)
    assert manure.K_manure == approx(0.0)
    assert manure.CH4_manure == approx(0.0)

    # Given some arguments, a new Manure object should either set the corresponding
    # attributes to the given values or do some calculations.
    manure = Manure(
            # The following attributes should be modified.
            U=1.0,
            TAN_s=1.0,
            MN=1.0,
            VSd=1.0,
            VSnd=1.0,
            p_excrt_manure=1.0,
            K_manure=1.0,

            # The following attributes should stay the same.
            # Only pick two as an example.
            Mkg=10.0,
            CH4_manure=10.0
    )
    constants = ManureManagementConstants
    assert manure.U == approx(constants.UREA_MOLAR_MASS)
    assert manure.TAN_s == approx(constants.TAN_MOLAR_MASS)
    assert manure.MN == approx(constants.GRAMS_TO_KG)
    assert manure.VSd == approx(constants.GRAMS_TO_KG)
    assert manure.VSnd == approx(constants.GRAMS_TO_KG)
    assert manure.p_excrt_manure == approx(constants.GRAMS_TO_KG)
    assert manure.K_manure == approx(constants.GRAMS_TO_KG)

    assert manure.Mkg == approx(10.0)
    assert manure.CH4_manure == approx(10.0)

    # Attributes that are not set to anything should be set to the default value of 0.
    assert manure.TSd == approx(0.0)
    assert manure.WIP_frac == approx(0.0)
    assert manure.WOP_frac == approx(0.0)
    assert manure.p_frac == approx(0.0)


# --------------------------- Test manure handlers module

# --------------------------- Test reception pits module

# --------------------------- Test manure separators module

# --------------------------- Test treatments module

# --------------------------- Test gas emissions module


# --------------------------- Test gas_emissions module

def assert_two_lists_equal(expected_items: List, result_items: List) -> None:
    """
    Checks equality of two lists element-wise.

    Parameters
    ----------
    expected_items: list of expected results.
    result_items: list of results to be tested.

    Returns
    -------
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
    # kmc = 841709169.5924
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
    value_to_test = GasEmissions.calc_Kmc(temp_in_k)
    result = 916332804.3735441
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
    value_to_test = GasEmissions.calc_conc_of_NH3_in_manure(
            F, C_tan)
    result = 30
    assert value_to_test == result


def test_calc_E_N20_manure():
    """Unit test for function calc_E_N20_manure in file gas_emissions.py"""
    pass


def test_calc_ammonia_flux():
    """Unit test for function calc_ammonia_flux in file gas_emissions.py"""
    K = 1
    Cm = 2
    H = 3
    Ca = 4
    value_to_test = GasEmissions.calc_NH3_flux(K, Cm, H, Ca)
    result = -36000
    assert value_to_test == result

# --------------------------- Test helpers module

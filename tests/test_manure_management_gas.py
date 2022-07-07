"""
RUFAS: Ruminant Farm Systems Model
File name: test_manure_management.py
Description: Implements test cases
Author(s): Sadman Chowdhury, skc86@cornell.edu
"""

import pytest
from RUFAS.routines.manure_management import gas_emissions
import RUFAS.routines.manure_management.gas_emissions


def test_calc_Kh():
    """Unit test for function calc_Kh in file gas_emissions.py"""
    temp_in_k = 30
    value_to_test = gas_emissions.gas_emissions.GasEmissions.calc_Kh(temp_in_k)
    assert value_to_test == 0

    pass


def test_calc_Ka():
    """Unit test for function calc_Ka in file gas_emissions.py"""
    pass


def test_calc_Q():
    """Unit test for function calc_Q in file gas_emissions.py"""
    pass


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
    pass


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


def test_convert_temp_C_to_K():
    """Unit test for function calc_vmax in file gas_emissions.py"""
    pass

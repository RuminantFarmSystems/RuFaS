"""
RUFAS: Ruminant Farm Systems Model
File name: test_leaf_area_index.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

from RUFAS.routines.field.crop.crop_types.base_crop import BaseCrop
from RUFAS.routines.field.soil.soil import Soil
from RUFAS.classes import Weather, Time
from RUFAS.routines.field.crop.growth_constraints import *

from unittest.mock import MagicMock
import pytest

from math import exp

def mock_crop(bio_P_opt = 150.0, bio_P = 90.0, bio_N_opt = 120.0,bio_N = 72.0,\
                water_act_up = 33.2):
    """
    Description:
        Creates a BaseCrop class mocking object for use as input for functions. It is initialized with the
        arguments provided; arguments are dynamic and can be changed/added to as needed.

    Args:
        bio_P_opt (float): BaseCrop attribute, optimal mass of phosphorus stored in plant material (kg P/ha)
        bio_P (float): BaseCrop attribute, actual mass of phosphorus stored in plant material (kg P/ha
        bio_N_opt (float): BaseCrop attribute, optimal mass of nitrogen stored in plant material (kg P/ha)
        bio_N (float): BaseCrop attribute, actual mass of nitrogen stored in plant material (kg P/ha)
        water_act_up (float): BaseCrop attribute, tottal plant water uptake on a given day (mm H20)

    Returns:
        BaseCrop class mocking object
    """
    mcrop = MagicMock(BaseCrop)

    mcrop.bio_P_opt = bio_P_opt
    mcrop.bio_P = bio_P
    mcrop.bio_N_opt = bio_N_opt
    mcrop.bio_N = bio_N
    mcrop.water_act_up = water_act_up

    return mcrop

def mock_soil(trans_max = 42.7):
    """
    Description:
        Creates a Soil class mocking object for use as input for functions. It is initialized with the
        arguments provided; arguments are dynamic and can be changed/added to as needed.

    Args:
        trans_max (float): Soil attribute, maximum plant transpiration on a given day (mm H20)

    Returns:
        Soil class mocking object
    """
    msoil = MagicMock(Soil)

    msoil.trans_max = trans_max

    return msoil

def mock_weather():
    """
    Description:
        Creates a Weather class mocking object for use as input for functions. It is initialized with the
        arguments provided; arguments are dynamic and can be changed/added to as needed.

    Args:

    Returns:
        Weather class mocking object
    """
    pass

def mock_time():
    """
    Description:
        Creates a Time class mocking object for use as input for functions. It is initialized with the
        arguments provided; arguments are dynamic and can be changed/added to as needed.

    Args:

    Returns:
        Time class mocking object
    """
    pass


#calc_phi_P()
def test_calc_phi_P_correctly_calculates_phi_P_for_non_zero_optimal_P():
    crop = mock_crop()

    assert pytest.approx(calc_phi_P(crop)) == max(0,200 * ((90.0/150.0) - 0.5))

def test_calc_phi_P_correctly_calculates_phi_P_for_zero_optimal_P():
    crop = mock_crop(bio_P_opt = 0)

    assert pytest.approx(calc_phi_P(crop)) == 300

#calc_p_stress()...assumes calc_phi_P() works properly
def test_calc_p_sress_correctly_calculates_phos_stress_for_non_zero_optimal_P():
    crop = mock_crop()

    phi_P = calc_phi_P(crop)
    p_stress = 1 - phi_P / (phi_P + exp(3.535 - 0.02597 * phi_P))

    assert pytest.approx(calc_p_stress(crop)) == min(0.99,p_stress)

def test_calc_p_sress_correctly_calculates_phos_stress_for_zero_optimal_P():
    crop = mock_crop(bio_P_opt= 0.0)

    assert pytest.approx(calc_p_stress(crop)) == 0

#calc_phi_N()
def test_calc_phi_N_correctly_calculates_phi_N_non_zero_optimal_N():
    crop = mock_crop()

    assert pytest.approx(calc_phi_N(crop)) == max(0,200 * ((72.0/120.0) - 0.5))

def test_calc_phi_N_correctly_calculates_phi_N_zero_optimal_N():
    crop = mock_crop(bio_N_opt = 0)

    assert pytest.approx(calc_phi_N(crop)) == 300

#calc_n_stress()...assumes calc_phi_N() works properly
def test_calc_n_sress_correctly_calculates_nitrogen_stress_for_non_zero_optimal_N():
    crop = mock_crop()

    phi_N = calc_phi_N(crop)
    n_stress = 1 - phi_N / (phi_N + exp(3.535 - 0.02597 * phi_N))

    assert pytest.approx(calc_p_stress(crop)) == min(0.99,n_stress)

def test_calc_n_sress_correctly_calculates_nitrogen_stress_for_zero_optimal_N():
    crop = mock_crop(bio_N_opt= 0.0)

    assert pytest.approx(calc_n_stress(crop)) == 0

#calc_t_stress()

#calc_w_stress()
def test_w_stress_correctly_calculates_w_stress_larger_water_act_up():
    crop = mock_crop(water_act_up= 62.3)
    soil = mock_soil()
    
    assert pytest.approx(calc_w_stress(soil,crop)) == 0

def test_w_stress_correctly_calculates_w_stress_smaller_water_act_up():
    crop = mock_crop()
    soil = mock_soil()

    assert pytest.approx(calc_w_stress(soil,crop)) == min(0.99,1.0 - (33.2 / 42.7))

def test_w_stress_correctly_calculates_w_stress_trans_max_zero():
    crop = mock_crop()
    soil = mock_soil(trans_max=0)

    assert pytest.approx(calc_w_stress(soil,crop)) == 0

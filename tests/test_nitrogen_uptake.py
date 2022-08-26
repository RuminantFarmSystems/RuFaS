"""
RUFAS: Ruminant Farm Systems Model
File name: test_nitrogen_uptake.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

from RUFAS.routines.field.crop.nitrogen_uptake import *
from RUFAS.routines.field.crop.nitrogen_fixation import calc_N_fixation
from RUFAS.routines.field.crop.crop_types.base_crop import BaseCrop
from RUFAS.routines.field.soil.soil import *

from unittest.mock import MagicMock
import pytest

from math import log, exp

def mock_crop(z_root = 800, N_up = 1.4, beta_n = 10.0 ):
    """
    Description: 
        Creates a BaseCrop class mocking object for use as input for functions. It is initialized with the
        arguments provided; arguments are dynamic and can be changed/added to as needed.

    Args:
        z_root (float)
        N_up (float)
        beta_n (float)

    Return:
        a BaseCrop mocking object instantiated with the provided arguments 
    """
    mcrop = MagicMock(BaseCrop)

    mcrop.z_root = z_root
    mcrop.N_up = N_up
    mcrop.beta_n = beta_n

    return mcrop

def mock_soil():
    """
    Description: 
        Creates a Soil class mocking object for use as input for functions. It is initialized with the
        arguments provided; arguments are dynamic and can be changed/added to as needed.

    Args:

    Return:
        a Soil mocking object instantiated with the provided arguments 
    """


#the following tests are for the calc_N_up_z() function in nitrogen_uptake.py
def test_calc_N_up_z_calculates_correct_uptake_value():
    """
    Description:
        unittest for calc_N_up_z in outines/field/crop/nitrogen_uptake.py. Tests that the 
        function  outputs the correct uptake value from the surface to the specified depth, z,
        when the BaseCrop attribute z_root is non-zero.
    """
    crop = mock_crop()
    z = 850.0

    term1 = 1.4 / (1 - exp(-1 * 10))
    term2 = 1 - exp(-1 * 10 * z / 800)

    assert pytest.approx(calc_N_up_z(crop,z)) == term1 * term2

def test_calc_N_up_z_returns_zero_for_z_root_zero_value():
    """
    Description:
        unittest for calc_N_up_z in outines/field/crop/nitrogen_uptake.py. Tests that the 
        function  outputs zero when the BaseCrop attribute z_root is zero.
    """

    crop = mock_crop(z_root = 0)
    z = 850.0

    assert pytest.approx(calc_N_up_z(crop,z)) == 0


        
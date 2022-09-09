"""
RUFAS: Ruminant Farm Systems Model
File name: test_nitrogen_uptake.py
Description: Implements tests for nitrogen_uptake.py
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

from RUFAS.routines.field.crop.nitrogen_uptake import *
from RUFAS.routines.field.crop.nitrogen_fixation import calc_N_fixation
from RUFAS.routines.field.crop.crop_types.base_crop import BaseCrop
from RUFAS.routines.field.soil.soil import *

from unittest.mock import MagicMock
import pytest

from math import log, exp

def mock_crop(z_root = 800, N_up = 1.4, beta_n = 10.0, bio_N = 0.7, N_act_up = 29.6 \
    , fix_nitrogen = True, fr_PHU = 0.5, pot_N_up_each_layer = [21.1]):
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
    mcrop.bio_N = bio_N
    mcrop.N_act_up = 29.6
    mcrop.fix_nitrogen = fix_nitrogen
    mcrop.fr_PHU = fr_PHU
    mcrop.pot_N_up_each_layer = pot_N_up_each_layer

    return mcrop

def mock_soil_layer(NO3 = 12.7,soil_water = 3.1,fc_water = 2.7,bottom_depth = 893.8):
    mlayer = MagicMock(Soil.SoilLayer)

    mlayer.NO3 = NO3
    mlayer.soil_water = soil_water
    mlayer.fc_water = fc_water 
    mlayer.bottom_depth = bottom_depth
    
    
    return mlayer

def mock_soil(soil_layers = [mock_soil_layer()]):
    msoil = MagicMock(Soil)

    msoil.soil_layers = soil_layers
    
    return msoil

#calc_bio_N()...assumes dependencies work properly
def test_calc_bio_N_correctly_calculates_and_sets_bio_N():
    crop = mock_crop()
    soil = mock_soil()
    
    calc_bio_N(soil,crop)
    N_fix = calc_N_fixation(soil,crop)

    assert pytest.approx(crop.bio_N) == 0.7 + 29.6 + N_fix


#the following tests are for the calc_N_up_z() function in nitrogen_uptake.py
def test_calc_N_up_z_calculates_correct_uptake_value():
    """
    Description:
        unittest for calc_N_up_z in outines/field/crop/nitrogen_uptake.py. Tests that the 
        function outputs the correct uptake value from the surface to the specified depth, z,
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
        function outputs zero when the BaseCrop attribute z_root is zero.
    """

    crop = mock_crop(z_root = 0)
    z = 850.0

    assert pytest.approx(calc_N_up_z(crop,z)) == 0




        
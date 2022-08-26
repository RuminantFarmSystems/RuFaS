"""
RUFAS: Ruminant Farm Systems Model
File name: test_soil_temp.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

from RUFAS.routines.field.crop.root_development import *
from RUFAS.routines.field.crop.crop_types.base_crop import BaseCrop

from unittest.mock import MagicMock
import pytest


def mock_crop_type(fr_PHU = 0.45,z_root = 800 , z_root_max = 1800):
    mcrop = MagicMock(BaseCrop)

    mcrop.fr_PHU = fr_PHU
    mcrop.z_root = z_root
    mcrop.z_root_max = z_root_max
    
    return mcrop


#the following tests are for the calc_daily_root_biomass() function

#test 1 is to simulate an instance where fr_root is > 0
def test_calc_daily_root_biomass_correctly_calculates_root_biomass():
    crop = mock_crop_type()
    calc_daily_root_biomass(crop)

    assert pytest.approx(crop.fr_root) == 0.4 - 0.2 * 0.45

#test 2 is to simulate instance where fr_root is <= 0
def test_calc_daily_root_biomass_correctly_calculates_root_biomass_zero():
    crop = mock_crop_type(fr_PHU = 2)
    calc_daily_root_biomass(crop)

    assert pytest.approx(crop.fr_root) == 0


#the following test is for the calc_z_root()



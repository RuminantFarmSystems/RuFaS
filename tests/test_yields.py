"""
RUFAS: Ruminant Farm Systems Model
File name: test_yields.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
           Clay Morrow, morrowcj@outlook.com
"""


from RUFAS.routines.field.crop.crop_types import base_crop
from RUFAS.routines.field.crop.yields import * 
from unittest.mock import MagicMock
import pytest

from math import exp


def mock_crop(HU = 0.1, PHU = 8.8, LAI = 2.3, yld = 3.0, P = 0.5, N = 0.7, bmass = 3.2 \
    ,fr_PHU = 1.3, HI_opt = 2.1):
    """
    Description:
        Creates a mock object of the BaseCrop class to be used for unittesting the functions
        in the yields.py file. 

    Args:
        (float) HU: crop attribute accumulated_HU
        (float) PHU: crop attribute PHU
        (float) LAI: crop attribute LAI_actual
        (float) yld: crop attribute yield_actual
        (float) P: crop attribute bio_P
        (float) N: crop attribute bio_N
        (float) bmass: crop attribute biomass_actual

    Return:
        returns the BaseCrop mock object set with the proper attribute values
    """
    
    mcrop = MagicMock(base_crop.BaseCrop)
    mcrop.accumulated_HU = HU
    mcrop.PHU = PHU
    mcrop.LAI_actual = LAI
    mcrop.yield_actual = yld
    mcrop.bio_P = P
    mcrop.bio_N = N
    mcrop.biomass_actual = bmass
    mcrop.fr_PHU = fr_PHU
    mcrop.HI_opt = HI_opt

    return mcrop

#The following tests are for the cut() function in yields.py
def test_cut_correctly_sets_accumulated_HU():
    crop = mock_crop()
    cut(crop,0.33)
    assert pytest.approx(crop.accumulated_HU) == 0.1 * (1 - .33)

def test_cut_correctly_sets_fr_PHU():
    crop = mock_crop()
    cut(crop,0.33)
    assert pytest.approx(crop.fr_PHU) == (0.1 * (1 - .33)) / 8.8

def test_cut_correctly_sets_LAI_actual():
    crop = mock_crop()
    cut(crop,0.33)
    assert pytest.approx(crop.LAI_actual) == 2.3 * (1 - .33) 

def test_cut_correctly_sets_fr_LAI_max_to_zero():
    crop = mock_crop()
    cut(crop,0.33)
    assert pytest.approx(crop.fr_LAI_max) == 0.0

def test_cut_correctly_sets_biomass_actual():
    crop = mock_crop()
    cut(crop,0.33)
    assert pytest.approx(crop.biomass_actual) == 3.2 - 3.0

def test_cut_correctly_sets_bio_P():
    crop = mock_crop()
    cut(crop,0.33)
    assert pytest.approx(crop.bio_P) == 0.5 * (1 - 0.33)

def test_cut_correctly_sets_bio_N():
    crop = mock_crop()
    cut(crop,0.33)
    assert pytest.approx(crop.bio_N) == 0.7 * (1 - 0.33)

def test_cut_correctly_sets_ET_annual_to_zero():
    crop = mock_crop()
    cut(crop,0.33)
    assert pytest.approx(crop.ET_annual) == 0

def test_cut_correctly_sets_all():
    crop = mock_crop()
    cut(crop,0.33)
    test_list = [
        pytest.approx(crop.accumulated_HU) == 0.1 * (1 - .33),
        pytest.approx(crop.fr_PHU) == (0.1 * (1 - .33)) / 8.8,
        pytest.approx(crop.LAI_actual) == 2.3 * (1 - .33),
        pytest.approx(crop.fr_LAI_max) == 0.0,
        pytest.approx(crop.biomass_actual) == 3.2 - 3.0,
        pytest.approx(crop.bio_P) == 0.5 * (1 - 0.33),
        pytest.approx(crop.bio_N) == 0.7 * (1 - 0.33),
        pytest.approx(crop.ET_annual) == 0
    ]

    assert all(test_list)


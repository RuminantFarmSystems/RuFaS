"""
RUFAS: Ruminant Farm Systems Model
File name: test_biomass.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

from RUFAS.routines.field.crop.crop_types import base_crop
from RUFAS.routines.field.crop.leaf_area_index import * 
from unittest.mock import MagicMock
import pytest

from math import exp, log, sqrt


def mock_crop(fr_PHU_1 = 0.15, fr_LAI_1 = 0.01,fr_PHU_2 = 0.50, fr_LAI_2 = 0.95 \
    ,fr_LAI_max = 0.95, fr_PHU = 0.75, LAI_actual = 4.3, LAI_max = 7.0, prev_fr_LAI_max = .87 ,\
        fr_PHU_sen = 0.90, gamma_reg = .7):
    """
    Description:
        creates the mock BaseCrop instance that will be used as
        the basis of the leaf_area_index.py unittests. The appropriate
        attributes of the instance will be instantiated in this function, 
        passed in as arguments
    """
    mcrop = MagicMock(base_crop.BaseCrop)
    mcrop.fr_PHU_1 = fr_PHU_1
    mcrop.fr_LAI_1 = fr_LAI_1
    mcrop.fr_PHU_2 = fr_PHU_2
    mcrop.fr_LAI_2 = fr_LAI_2
    mcrop.fr_LAI_max = fr_LAI_max
    mcrop.fr_PHU = fr_PHU
    mcrop.LAI_actual = LAI_actual
    mcrop.LAI_max = LAI_max
    mcrop.prev_fr_LAI_max = prev_fr_LAI_max
    mcrop.fr_PHU_sen = fr_PHU_sen
    mcrop.gamma_reg = gamma_reg
    return mcrop

#for testing L1, assume L2 is correct
def test_calculate_shape_coefficients_correctly_calculates_L1():
    crop = mock_crop()
    L1, L2 = calculate_shape_coefficients(crop)
    #L2 = (log((0.15/0.01) - 0.15) - log((0.50/0.95) - 0.50)) / (0.50 - 0.15)
    assert pytest.approx(L1) == log((0.15/0.01) - 0.15) + (L2 * 0.15)

#testing L2 individually
def test_calculate_shape_coefficients_correctly_calculates_L2():
    crop = mock_crop()
    L1 , L2 = calculate_shape_coefficients(crop)

    assert pytest.approx(L2) == (log((0.15/0.01) - 0.15) - log((0.50/0.95) - 0.50)) / (0.50 - 0.15)

def test_calculate_shape_coefficients_correctly_calculates_L1_and_L2():
    crop = mock_crop()
    L1 , L2 = calculate_shape_coefficients(crop)
    tests = [ 
        pytest.approx(L1) == log((0.15/0.01) - 0.15) + (L2 * 0.15),
        pytest.approx(L2) == (log((0.15/0.01) - 0.15) - log((0.50/0.95) - 0.50)) / (0.50 - 0.15)
    ]
    assert all(tests)

#the following tests are for the calc_fr_LAI_max() function
#assumes that L1 and L2 (output of shape coefficient function) are correct
def test_calc_fr_LAI_max_correctly_sets_prev_fr_LAI_max():
    crop = mock_crop()
    L1,L2 = calculate_shape_coefficients(crop)
    calc_fr_LAI_max(crop, L1,L2)

    assert pytest.approx(crop.prev_fr_LAI_max) == 0.95

def test_calc_fr_LAI_max_correctly_sets_fr_LAI_max():
    crop = mock_crop()
    L1,L2 = calculate_shape_coefficients(crop)
    calc_fr_LAI_max(crop, L1,L2)
    
    assert pytest.approx(crop.fr_LAI_max) == 0.75 / (0.75 + exp(L1 - (L2 * 0.75)))

def test_calc_fr_LAI_max_all_correct():
    crop = mock_crop()
    L1,L2 = calculate_shape_coefficients(crop)
    calc_fr_LAI_max(crop, L1,L2)

    tests = [ 
        pytest.approx(crop.prev_fr_LAI_max) == 0.95,
        pytest.approx(crop.fr_LAI_max) == 0.75 / (0.75 + exp(L1 - (L2 * 0.75)))
    ]
    assert all(tests)

#the following tests are for the calculate_d_LAI_actual() function:
def test_calculate_d_LAI_actual_correctly_calculates_change_in_LAI_actual():
    crop = mock_crop()
    
    assert pytest.approx(calculate_d_LAI_actual(crop,.55)) == 0.55 * sqrt(0.7)



#the following tests are for the calculate_LAI_actual() function
#there are 2 cases:when fr_PHU <= fr_PHU_sen and when fr_PHU > fr_PHU_sen
#assume calculate_d_LAI_actual works properly and is correct

#case 1: fr_PHU <= fr_PHU_sen
def test_calculate_LAI_actual_sets_LAI_actual_correctly():
    crop = mock_crop()
    calculate_LAI_actual(crop)

    #first need to calculate d_LAI_actual
    d_LAI_max = (.95 - .87) * 7.0 * (1- exp(5* (4.3-7.0)))
    d_LAI_actual = calculate_d_LAI_actual(crop,d_LAI_max)

    assert pytest.approx(crop.LAI_actual) == max(4.3 + d_LAI_actual,0)

#case 2: fr_PHU > fr_PHU_sen
    crop = mock_crop(fr_PHU = .9, fr_PHU_sen =.7)
    calculate_LAI_actual(crop)

    #first need to calculate d_LAI_actual
    d_LAI_max = (.95 - .87) * 7.0 * (1- exp(5* (4.3-7.0)))
    d_LAI_actual = calculate_d_LAI_actual(crop,d_LAI_max)

    assert pytest.approx(crop.LAI_actual) == max((4.3 * (1-.9)/(1-.7)), 0)






    




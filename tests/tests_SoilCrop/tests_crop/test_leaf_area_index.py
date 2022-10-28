"""
RUFAS: Ruminant Farm Systems Model
File name: test_leaf_area_index.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

from RUFAS.routines.field.crop.crop_types import base_crop
from RUFAS.routines.field.crop.leaf_area_index import *
from tests.tests_SoilCrop.mock_classes import *
from unittest.mock import MagicMock
import pytest

from math import exp, log, sqrt


#TODO: add exception raising conditions to original function in leaf_area_index.py
#to ensure no div by 0 and input for logs is valid

@pytest.mark.parametrize(("fr_PHU_1","fr_LAI_1","fr_PHU_2","fr_LAI_2"),[
    (.15, .01, .50, .95),
    (.45, .08, .39,.70), 
    (1.0, 0.47, .95, 0.5)
])
def test_calculate_shape_coefficients(fr_PHU_1: float, fr_LAI_1: float, fr_PHU_2: float, fr_LAI_2: float) -> None:
    """
    Description:
        Unit test for calculate_shape_coefficients() in routines/field/crop/leaf_area_index.py
    """

    crop = mock_crop(fr_PHU_1 = fr_PHU_1, fr_LAI_1 = fr_LAI_1, fr_PHU_2 = fr_PHU_2, fr_LAI_2 = fr_LAI_2)

    #L2 expected
    L2_part1 = (fr_PHU_1 / fr_LAI_1) - fr_PHU_1
    L2_part2 = (fr_PHU_2 / fr_LAI_2) - fr_PHU_2

    L2 = (log(L2_part1) - log(L2_part2)) / (fr_PHU_2 - fr_PHU_1)

    #L1 expected, uses L2 in its calculation
    L1 = log((fr_PHU_1 / fr_LAI_1) - fr_PHU_1) + (L2 * fr_PHU_1)

    #assertion
    assert pytest.approx(calculate_shape_coefficients(crop)) == [L1,L2]



@pytest.mark.parametrize(("fr_PHU_1","fr_LAI_1","fr_PHU_2","fr_LAI_2","fr_LAI_max","fr_PHU","prev_fr_LAI_max"),[
    (.15, .01, .50, .95, .95, .75, .87),
    (.45, .08, .39,.70, .62, .81, .64), 
    (1.0, 0.47, .95, 0.5, .20, .41, .41)
])
def test_calc_fr_LAI_max(fr_PHU_1, fr_LAI_1, fr_PHU_2, fr_LAI_2, fr_LAI_max, fr_PHU, prev_fr_LAI_max) -> None:
    """Ensures that prev_fr_LAI_max and fr_LAI_max are calculated correctly in calc_fr_LAI_max"""

    crop = mock_crop(fr_PHU_1 = fr_PHU_1, fr_LAI_1 = fr_LAI_1, fr_PHU_2 = fr_PHU_2, fr_LAI_2 = fr_LAI_2, \
        fr_LAI_max = fr_LAI_max,fr_PHU = fr_PHU,prev_fr_LAI_max = prev_fr_LAI_max)

    #get L1,L2
    L1,L2 = calculate_shape_coefficients(crop)

    #expected
    previous_fr_max = fr_LAI_max

    exponent = exp(L1 - (L2 * fr_PHU))
    LAI_max = fr_PHU / (fr_PHU + exponent)

    #assert function output/result is same as expected result
    calc_fr_LAI_max(crop,L1,L2)
    PREV = crop.prev_fr_LAI_max
    MAX = crop.fr_LAI_max

    assert pytest.approx([PREV,MAX]) == [previous_fr_max,LAI_max]



@pytest.mark.parametrize(("d_LAI_max","gamma_reg"),[
    (.55,.7), #arbitrary
    (0,0), #zeroes
    (1,1), #ones
    #(-1,-1), #negative vals
    (.8,.1) #arbitrary
])
def test_calculuate_d_LAI_actual(d_LAI_max, gamma_reg):
    """ensures that change in LAI actual (d_LAI_actual) is calculated correctly"""

    crop = mock_crop(gamma_reg = gamma_reg)

    #expected value [C.8.A.5]
    d_actual = d_LAI_max * sqrt(gamma_reg)

    #assert actual result is same as expected
    assert pytest.approx(calculate_d_LAI_actual(crop,d_LAI_max)) == d_actual



@pytest.mark.parametrize(("LAI_actual","LAI_max","fr_LAI_max","prev_fr_LAI_max","fr_PHU","fr_PHU_sen","gamma_reg"),
[(4.3, 7.0, .95, .87, .9, .7,.1), #fr_PHU > fr_PHU_sen
 (1 ,1, 1, 1, 1, 1, 1), #all ones
 (3.7, 5.6, .76, .59, .48, .63, .25), #fr_PHU < fr_PHU_sen
 (3.7, 5.6, .76, .59, .63, .63, .25) #fr_PHU = fr_PHU_sen
])
def test_calculate_LAI_actual(LAI_actual, LAI_max, fr_LAI_max, prev_fr_LAI_max, fr_PHU, fr_PHU_sen, gamma_reg):
    '''ensures that LAI_actual is correctly calculated in calculate_LAI_actual()'''
    
    crop = mock_crop(LAI_actual = LAI_actual, LAI_max = LAI_max,fr_LAI_max = fr_LAI_max, 
    prev_fr_LAI_max = prev_fr_LAI_max,fr_PHU = fr_PHU, fr_PHU_sen = fr_PHU_sen, gamma_reg = gamma_reg)

    #expected value [C.8.A.5/6]
    delta_LAI_max = (fr_LAI_max - prev_fr_LAI_max) * LAI_max * (1 - exp(5 * (LAI_actual - LAI_max)))
    delta_LAI_actual =  calculate_d_LAI_actual(crop, delta_LAI_max)

    if fr_PHU <= fr_PHU_sen:
        LAI_actual = max(LAI_actual + delta_LAI_actual, 0)
    else:
        LAI_actual = max(LAI_actual * ((1-fr_PHU) / (1- fr_PHU_sen)) , 0)


    #check that actual val is same as expected
    calculate_LAI_actual(crop)
    assert pytest.approx(crop.LAI_actual) == LAI_actual

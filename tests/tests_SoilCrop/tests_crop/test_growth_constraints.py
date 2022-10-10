"""
RUFAS: Ruminant Farm Systems Model
File name: test_growth_constraints.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

from RUFAS.routines.field.crop.crop_types.base_crop import BaseCrop
from RUFAS.routines.field.soil.soil import Soil
from RUFAS.classes import Weather, Time
from RUFAS.routines.field.crop.growth_constraints import *
from tests.tests_SoilCrop.mock_classes import *

from unittest.mock import MagicMock
import pytest

from math import exp


@pytest.mark.parametrize(("bio_P", "bio_P_opt"),[
    (90,130),  #arbitrary values
    (0, 0), #all zeroes
    (1, 1), #all ones
    (-1, 140), #bio_P negative
    (78, -1), #bio_P_opt negative
    (82, 0), #bio_P_opt zero
    (81,200)
])
def test_calc_phi_P(bio_P,bio_P_opt):
    """ 
    Description:
        Unit test for calc_phi_P in routines/field/crop/growth_constraints.py. Makes
        use of the pytest parametrization to conduct many test cases at once.
    """
    crop = mock_crop(bio_P = bio_P, bio_P_opt = bio_P_opt)

    #
    if bio_P_opt == 0:
        phi_P = 300
    else:
        phi_P = max(0, 200 * ((bio_P / bio_P_opt) - 0.5))
    
    assert pytest.approx(calc_phi_P(crop)) == phi_P



@pytest.mark.parametrize(("bio_P", "bio_P_opt"),[
    (81, 200), #arbitrary
    (0, 0), #zeroes
    (1, 1), #ones
    (-1, 250), #negaitve bio_P
    (80, -1), #negative bio_P_opt
    (90,0), #bio_P_opt = 0 to induce if statement
])
def test_calc_p_stress(bio_P, bio_P_opt):
    """ 
    Description:
        Unit test for calc_P_stress in routines/field/crop/growth_constraints.py. Makes
        use of the pytest parametrization to conduct many test cases at once. Any functions used as a
        dependency are assumed to be correct (i.e previously tested before implementation of this test function)
    """
    
    crop = mock_crop(bio_P = bio_P, bio_P_opt = bio_P_opt)

    if bio_P_opt == 0:
        p_stress = 0
    else:
        phi_p = calc_phi_P(crop)
        print(phi_p)
        p_stress = min(0.99, 1 - (phi_p / (phi_p + exp(3.535 - (0.02597* phi_p)))))
    
    assert pytest.approx(calc_p_stress(crop)) == p_stress


@pytest.mark.parametrize(("bio_N", "bio_N_opt"),[
    (90,130),  #arbitrary values
    (0, 0), #all zeroes
    (1, 1), #all ones
    (-1, 140), #bio_N negative
    (78, -1), #bio_N_opt negative
    (82, 0), #bio_N_opt zero
    (81,200)
])
def test_calc_phi_N(bio_N,bio_N_opt):
    """ 
    Description:
        Unit test for calc_phi_N in routines/field/crop/growth_constraints.py. Makes
        use of the pytest parametrization to conduct many test cases at once.
    """
    crop = mock_crop(bio_N = bio_N, bio_N_opt = bio_N_opt)

    #
    if bio_N_opt == 0:
        phi_N = 300
    else:
        phi_N = max(0, 200 * ((bio_N / bio_N_opt) - 0.5))
    
    assert pytest.approx(calc_phi_N(crop)) == phi_N


@pytest.mark.parametrize(("bio_N", "bio_N_opt"),[
    (81, 200), #arbitrary
    (0, 0), #zeroes
    (1, 1), #ones
    (-1, 250), #negaitve bio_P
    (80, -1), #negative bio_P_opt
    (90,0), #bio_P_opt = 0 to induce if statement
])
def test_calc_n_stress(bio_N, bio_N_opt):
    """ 
    Description:
        Unit test for calc_P_stress in routines/field/crop/growth_constraints.py. Makes
        use of the pytest parametrization to conduct many test cases at once. Any functions used as a
        dependency are assumed to be correct (i.e previously tested before implementation of this test function)
    """
    
    crop = mock_crop(bio_N = bio_N, bio_N_opt = bio_N_opt)

    if bio_N_opt == 0:
        N_stress = 0
    else:
        phi_N = calc_phi_N(crop)
        print(phi_N)
        N_stress = min(0.99, 1 - (phi_N / (phi_N + exp(3.535 - (0.02597* phi_N)))))
    
    assert pytest.approx(calc_n_stress(crop)) == N_stress

@pytest.mark.parametrize(("water_act_up","trans_max"),[
    (20,40), #arbitrary int
    (0,0), #zeroes
    (1,1), #ones
    (-1,-1), #negative
    (26.8,34.1), #arbitrary floats
])
def test_calc_w_stress(water_act_up, trans_max):
    """
    Description:
        Unit test for calc_w_stress() in routines/field/crop/growth_constraints.py.
        Makes use of pytest parametrization to conduct many tests at once.
    """
    crop = mock_crop(water_act_up = water_act_up)
    soil = mock_soil(trans_max = trans_max)

    if trans_max == 0:
        w_stress = 0
    else:
        w_stress = 1.0 - (water_act_up / trans_max)
    if w_stress < 0:
        w_stress = 0
    else:
        w_stress = min(0.99, w_stress)

    assert pytest.approx(calc_w_stress(soil,crop)) == w_stress



# @pytest.mark.parametrize((),[])
# def test_calc_t_stress():
#     """
#     Description:
#         Tests calc_t_stress in routines/field/crop/growth_constraints.py.    
#     """
#     crop = mock_crop()
#     time = mock_time()
#     weather = mock_weather()




#     assert pytest.approx(calc_t_stress(crop,weather,time)) == True





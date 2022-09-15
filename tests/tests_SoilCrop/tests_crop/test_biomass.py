"""
RUFAS: Ruminant Farm Systems Model
File name: test_biomass.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

import pytest
from math import exp

from RUFAS.routines.field.crop.biomass import *
from tests.tests_SoilCrop.mock_classes import mock_crop

@pytest.mark.parametrize("h_day,k_l,lai_act", [
    (1, 1, 1),
    (0, 0, 0),
    (1, 0, 1),
    (.2, -.38, 0.75),
    (.2, .38, 0.75)
])
def test_intercept_radiation(h_day, k_l, lai_act):
    """
    Description: test calculation of solar radiation intercepted for photosynthesis

    Args:
        h_day: solar radiation on the current day
        k_l: light extinction coefficient
        lai_act: actual LAI
    """

    h_photo = 0.5 * h_day * (1 - exp(-k_l * lai_act))
    result = intercept_radiation(h_day, k_l, lai_act)
    assert result == h_photo

@pytest.mark.parametrize("h_day,lai_act", [
    (-1, 1),
    (1, -1),
    (-1, -1)
])
def test_intercept_radiation_error(h_day, lai_act):
    """
    Description: test that `intercept_radiation()` raises exceptions when appropriate
    Args:
        h_day: solar radiation on the current day
        lai_act: actual LAI
    """

    with pytest.raises(Exception):
        intercept_radiation(h_day, 0.8, lai_act)

@pytest.mark.parametrize("rad,eff,expected",[
    (0, 0, 0),
    (1000, 0.33, 330),
    (1961.67, 0.217, 1961.67 * 0.217)
])
def test_limit_growth(rad, eff, expected):
    """
    Description: test that `limit_growth()` matches expectations

    Args:
        rad: incoming light radiation
        eff: light use efficiency
        expected: expected output
    """

    assert limit_growth(rad, eff) == expected

@pytest.mark.parametrize("rad,eff", [
    (-1000, 0.33),
    (1000, -0.33),
    (-1000, -0.33)
])
def test_limit_growth_errors(rad, eff):
    """
    Description: test that `limit_growth()` raises errors if negative values are given

    Args:
        rad: incoming light radiation
        eff: light use efficiency
    """

    with pytest.raises(Exception):
        limit_growth(rad, eff)

@pytest.mark.parametrize("start,g,rad,eff", [
    (0, 0.2, 1000, 1),
    (1, 0, 1000, 1),
    (1, 0.2, 0, 1),
    (0, 0, 0, 0),
    (137.2, 0.37, 10379, 0.872),
])
def test_update_biomass(start, g, rad, eff):
    """
    Description: test that `update_biomass()` properly updates attributes

    Args:
        start: starting size of the plant
        g: growth factor of the plant
        rad: total incoming solar radiation
        eff: light use efficiency of the plant
    """
    mc = mock_crop(biomass_actual=start, gamma_reg=g, d_biomass_max=0, d_biomass_actual=0, prev_biomass_actual=0, RUE=eff)
    update_biomass(mc, light=rad)

    check_limit = limit_growth(rad, eff)
    check_grow = grow_biomass(start, g, check_limit)

    assert [mc.d_biomass_max, mc.d_biomass_actual, mc.prev_biomass_actual, mc.biomass_actual] == \
           [check_limit, check_grow["accumulated biomass"], start, check_grow["end"]]

# ## OLD TESTS ----
# # the following tests are for the calc_bio_AG() function
# def test_calc_bio_AG_sets_bio_AG_correctly():
#     """
#     Description:
#         Unittest for calc_bio_AG() in routines/field/crop/biomass.py. Checks that the
#         BaseCrop attribute bio_AG is correctly set
#     """
#
#     crop = mock_crop()
#     calc_bio_AG(crop)
#
#     assert pytest.approx(crop.bio_AG) == (1 - .38) * 4.6
#
#
# # the following tests are for the calc_gamma_wu() function
# def test_calc_gamma_wu_sets_ET_annual_correctly_ET_max_nonzero():
#     """
#     Description:
#         Unittest for calc_gamma_wu in routines/field/crop/biomass.py. Checks that the
#         Soil attribute ET_max_annual is correctly set when it is initially a non-zero value.
#
#     """
#     crop = mock_crop()
#     soil = mock_soil()
#     calc_gamma_wu(soil, crop)
#
#     assert pytest.approx(soil.ET_annual) == 2.1 + 1.3
#
#
# def test_calc_gamma_wu_sets_gamma_wu_correctly_ET_max_nonzero():
#     """
#     Description:
#         Unittest for calc_gamma_wu in routines/field/crop/biomass.py. Checks that the
#         Soil attribute gamma_wu is correctly set when soil.ET_max_annual is initially a non-zero value.
#
#     """
#
#     crop = mock_crop()
#     soil = mock_soil()
#     calc_gamma_wu(soil, crop)
#
#     assert pytest.approx(crop.gamma_wu) == 100 * ((2.1 + 1.3) / 1.5)
#
#
# def test_calc_gamma_wu_sets_all_correctly_ET_max_nonzero():
#     """
#     Description:
#         Blanket test to check that all values set in calc_gamma_wu() are set appropriately
#         when soil.ET_max_annual is initially a non-zero value.
#
#     """
#     crop = mock_crop()
#     soil = mock_soil()
#     calc_gamma_wu(soil, crop)
#
#     test_list = [
#         pytest.approx(soil.ET_annual) == 2.1 + 1.3,
#         pytest.approx(crop.gamma_wu) == 100 * ((2.1 + 1.3) / 1.5)
#     ]
#
#     assert all(test_list)
#
#
# def test_calc_gamma_wu_returns_zero_with_ET_max_as_zero():
#     """
#     Description:
#         Unittest for calc_gamma_wu() in routines/field/crop/biomass.py. Checks that
#         the function returns 0 if the Soil attribute ET_max_annual is initially set to zero.
#     """
#     crop = mock_crop()
#     soil = mock_soil(ET_max_annual=0.0)
#
#     assert pytest.approx(calc_gamma_wu(soil, crop)) == 0

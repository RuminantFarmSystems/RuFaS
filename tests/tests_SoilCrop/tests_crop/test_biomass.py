"""
RUFAS: Ruminant Farm Systems Model
File name: test_biomass.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

import pytest

from RUFAS.routines.field.crop.biomass import *
from tests.tests_SoilCrop.mock_classes import mock_crop, mock_soil


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


@pytest.mark.parametrize("rad,eff,expected", [
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


@pytest.mark.parametrize("start,g,rad,ext,eff", [
    (0, 0.2, 1000, 0.33, 1),  # no initial size
    (1, 0, 1000, 0.33, 1),  # no growth
    (1, 0.2, 0, 0.33, 1),  # no light
    (1, 0.2, 1000, 0, 1),  # no light extinction
    (1, 0.2, 1000, 1, 1),  # total light extinction
    (0, 0, 0, 0, 0),  # all zero
    (137.2, 0.37, 10379, 0.375, 0.872)  # arbitrary case
])
def test_update_biomass(start, g, rad, ext, eff, lai):
    """
    Description: test that `update_biomass()` properly updates attributes

    Args:
        start: starting size of the plant
        g: growth factor of the plant
        rad: total incoming solar radiation
        ext: light extinction coefficient
        eff: light use efficiency of the plant
        lai: actual leaf area index
    """
    mc = mock_crop(biomass_actual=start, gamma_reg=g, d_biomass_max=0, d_biomass_actual=0, prev_biomass_actual=0,
                   RUE=eff, kl=ext, LAI_actual=lai)
    # expected values
    incpt_light = intercept_radiation(rad, ext, lai)
    check_limit = limit_growth(incpt_light, eff)
    check_grow = grow_biomass(start, g, check_limit)
    # execute function
    update_biomass(mc, light=incpt_light)

    assert [mc.d_biomass_max, mc.d_biomass_actual, mc.prev_biomass_actual, mc.biomass_actual] == \
           [check_limit, check_grow["accumulated biomass"], start, check_grow["end"]]


@pytest.mark.parametrize("fr,bm", [
    (0.5, 1),  # half biomass in roots
    (0.5, 50),  # increase biomass
    (0, 1),  # no roots
    (1, 1),  # all roots
    (-0.5, 1),  # negative roots?
    (0.297, 132.1) # arbitrary
])
def test_calc_bio_AG(fr, bm):
    """
    Description: Test `calc_bio_AG()`

    Args:
        fr: fraction of biomass in roots
        bm: actual plant biomass
    """
    assert calc_bio_AG(fr, bm) == (1-fr)*bm


@pytest.mark.parameterize("fr,bm", [
    (0.5, 1),  # half biomass in roots
    (0.5, 50),  # increase biomass
    (0, 1),  # no roots
    (1, 1),  # all roots
    (-0.5, 1),  # negative roots?
    (0.297, 132.1)  # arbitrary
])
def test_update_bio_AG(fr, bm):
    """
    Description: Test `update_bio_AG()`

    Args:
        fr: fraction of biomass in roots
        bm: actual plant biomass
    """
    mc = mock_crop(fr_root=fr, biomass_actual=bm, bio_AG=0)
    update_bio_AG(mc)
    assert mc.bio_AG == calc_bio_AG(fr, bm)


@pytest.mark.parametrize("evap,trans", [
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 0),
    (-1, 0),
    (0, -1),
    (-1, -1),
    (0.32, 1.357)
])
def test_calc_evapotrans(evap, trans):
    """
    Description: Test `calc_evapotrans()`

    Args:
        evap: evaporation
        trans: transpiration
    """
    assert calc_evapotrans(evap, trans) == evap+trans


@pytest.mark.parametrize("evap,trans,evap_max,start_et", [
    (1, 1, 1, 1),  # all 1
    (0, 1, 1, 1),  # no evap
    (1, 0, 1, 1),  # no trans
    (1, 1, 0, 1),  # max = 0
    (1, 1, 1, 0),  # start = 0
    (0, 0, 0, 0),  # all 0
    (0.48, 0.33, 1.33, 1.05),  # arbitrary values
    (0.48, 0.33, 0, 1.05)  # arbitrary & max = 0
])
def test_update_evapotrans(evap, trans, evap_max, start_et):
    """
    Description: Test `update_evapotrans()`

    Args:
        evap: evaporation
        trans: transpiration
    """
    ms = mock_soil(evap_annual=evap, trans_annual=trans, ET_max_annual=evap_max,
                   ET_annual=start_et)
    update_evapotrans(ms)

    if evap_max != 0:  # conditional assertion
        assert ms.ET_annual == evap + trans
    else:
        assert ms.ET_annual == start_et


@pytest.mark.parametrize("et,et_max", [
    (1, 1),
    (0, 0),
    (0, 1),
    (1, 0),
    (0.38, 0),
    (0, 0.29),
    (0.38, 0.29)
])
def test_calc_water_def(et, et_max):
    """
    Description:

    Args:
        et: evapotranspiration
        et_max: maximum evapotranspiration
    """
    if et_max != 0:
        assert calc_water_def(et, et_max) == 100 * (et / et_max)
    else:
        assert calc_water_def(et, et_max) == 0

def test_update_all():
    assert False  # TODO: I don't yet know how to properly mock the radiation object

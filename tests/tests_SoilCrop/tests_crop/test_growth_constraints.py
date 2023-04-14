"""
RUFAS: Ruminant Farm Systems Model
File name: test_growth_constraints.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

from RUFAS.routines.field.crop.growth_constraints import *
from tests.tests_SoilCrop.mock_classes import *

import pytest
from math import exp


@pytest.mark.parametrize(("opt", "phi"), [
    (1, 1),  # both 1
    (0, 0),  # both 0
    (1, 0),  # phi 0
    (0, 1),  # opt 0
    (-1, 1),  # negative opt
    (93.8, 200),  # arbitrary
    (93.8, 100),  # smaller phi
    (93.8, .1),  # very small phi
    (93.8, 300),  # max (?) phi
])
def test_calc_nutrient_stress(opt, phi):
    """ensure that stress is correctly calculated with calc_nutrient_stress()"""
    if opt == 0:
        stress = 0
    else:
        stress = 1 - (phi / (phi + exp(3.535 - (0.02597 * phi))))

    if stress > 1:
        stress = 1

    assert calc_nutrient_stress(optimal=opt, stress_factor=phi) == stress


@pytest.mark.parametrize(("act", "opt"), [
    (0, 0),  # all 1
    (1, 1),  # all 0
    (1, 0),  # both 0
    (0, 1),  # 0 nitrogen
    (-1, 1),  # negative nitrogen
    (1, -1),  # negative optimal
    (90.3, 130.1),  # arbitrary act < opt
    (78.1, 32.55),  # negative act > opt
    (200.3, 200.3),  # arbitrary act = opt
    (190.53, 190.54),  # almost equal
])
def test_calc_nutrient_stress_scaling_factor(act, opt):
    """ensure that nitrogen scaling factor is correctly calculated by calc_nitrogen_stress_scaling_factor()."""
    if opt == 0:
        phi = 100
    else:
        phi = max(0., (200 * ((act / opt) - 0.5)))

    assert calc_nutrient_stress_scaling_factor(stored=act, optimal=opt) == phi


@pytest.mark.parametrize(("uptake", "trans"), [
    (20, 40),  # arbitrary int
    (0, 0),  # zeroes
    (1, 1),  # ones
    (-1, -1),  # negative
    (26.8, 34.1),  # arbitrary floats
    (32.55, 18.2)  # trans < uptake
])
def test_calc_water_stress(uptake, trans):
    """ensure water stress is correctly calculated with calc_water_stress()"""
    if trans == 0:
        w_stress = 0
    else:
        w_stress = 1.0 - (uptake / trans)

    if w_stress < 0:
        w_stress = 0
    elif w_stress > 1:
        w_stress = 1

    assert calc_water_stress(uptake, trans) == w_stress


@pytest.mark.parametrize("air,mini,opt", [
    (1, 1, 1),  # all 1 (A)
    (1, 0, 0),  # air 1 (D)
    (0, 1, 0),  # min 1 (A)
    (0, 0, 1),  # opt 1 (A)
    (0, 0, 0),  # all 0 (A)
    (0.5, 0, 1),  # min < air < opt (B)
    (1, 0, 1),  # min < air = opt (B)
    (1.5, 0, 1),  # opt < air < 2*opt - min (C)
    (2, 0, 1),  # opt < air = 2*opt - min (C)
    (3, 0, 1),  # opt < air > 2*opt - min (D)
    (5.6, 12.2, 25.5),  # arbitrary (A)
    (15.8, 12.2, 25.5),  # arbitrary (B)
    (36.7, 12.2, 25.5),  # arbitrary (C)
    (39.9, 12.2, 25.5),  # arbitrary (D)
])
def test_calc_temperature_stress(air, mini, opt):
    """ensure temperature stress is correctly calculated with calc_temperature_stress()"""
    top = -0.1054*((opt - air)**2)
    dbl = (2*opt) - mini

    expect = None
    if air <= mini:  # A
        expect = 1
    if mini < air <= opt:  # B
        expect = 1 - exp(top / ((air - mini) ** 2))
    if opt < air <= dbl:  # C
        expect = 1 - exp(top / ((dbl - mini) ** 2))
    if air > dbl:  # D
        expect = 1

    assert calc_temperature_stress(air_temp=air, min_temp=mini, optimal_temp=opt) == expect


@pytest.mark.parametrize("w,t,n,p", [
    (1, 1, 1, 1),  # all 1
    (.8, .7, .6, .5),  # water limited
    (.8, .82, .6, .5),  # temperature limited
    (.8, .7, .9, .5),  # nitrogen limited
    (.8, .7, .6, 0.93),  # phosphorus limited
    (0, 0, 0, 0),  # no limits
])
def test_calc_growth_factor(w, t, n, p):
    limiting_factor = max(w, t, n, p)
    expect = 1 - limiting_factor
    assert calc_growth_factor(water_stress=w, temperature_stress=t, nitrogen_stress=n, phosphorus_stress=p) == expect


@pytest.mark.parametrize("water_up,trans,temp,min_temp,opt_temp,nitro,opt_nitro,phos,opt_phos", [
    (100, 50, 25.3, 10.8, 26.0, 83.33, 112.18, 20.10, 30.65)
])
def test_update_growth_factor(water_up, trans, temp, min_temp, opt_temp, nitro, opt_nitro, phos, opt_phos):
    mc = mock_crop(water_act_up=water_up, T_base_min=min_temp, T_opt=opt_temp, bio_N=nitro, bio_N_opt=opt_nitro,
                   bio_P=phos, bio_P_opt=opt_phos)
    ms = mock_soil(trans_max=trans)
    # TODO This does NOT test that weather values are accessed properly. Accessing weather attributes should be a func
    mw = mock_weather(T_avg=[[temp]])
    mt = mock_time(day=0, year=0)

    update_growth_factor(crop=mc, soil=ms, weather=mw, time=mt)

    w_stress = calc_water_stress(water_up, trans)
    t_stress = calc_temperature_stress(temp, min_temp, opt_temp)
    n_stress = calc_nutrient_stress(opt_nitro, calc_nutrient_stress_scaling_factor(nitro, opt_nitro))
    p_stress = calc_nutrient_stress(opt_phos, calc_nutrient_stress_scaling_factor(phos, opt_phos))
    expect = calc_growth_factor(w_stress, t_stress, n_stress, p_stress)

    assert mc.gamma_reg == expect

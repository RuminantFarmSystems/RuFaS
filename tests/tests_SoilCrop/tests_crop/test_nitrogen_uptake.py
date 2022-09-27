"""
RUFAS: Ruminant Farm Systems Model
File name: test_nitrogen_uptake.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

import pytest
from RUFAS.routines.field.crop.nitrogen_uptake import *
from tests.tests_SoilCrop.mock_classes import mock_crop


@pytest.mark.parametrize("heat,nfrac,n3,n1", [
    (1, .5, .25, .75),  # max heat
    (0.8, .5, .25, 1),  # max n3
    (0.32, .5, .25, .75),  # arbitrary
])
def test_calc_shape_log(heat, nfrac, n3, n1):
    """Description: check that calc_shape_log() calculates correct output"""
    observe = calc_shape_log(heat_frac=heat, nfrac_x=nfrac, nfrac_3=n3, nfrac_1=n1)
    bottom = 1 - ((nfrac - n3) / (n1 - n3))
    inside = (heat / bottom) - heat
    expect = log(inside)
    assert observe == expect


@pytest.mark.parametrize("heat,nfrac,n3,n1", [
    (0, .5, .25, .75),  # no heat
    (0.8, 0, .25, .75),  # n3 = 0
    (0.8, 0.76, .25, .75),  # nfrac > n1
    (0.8, 0.75, .25, .75),  # nfrac = n1
    (0.8, .5, .25, 0.24),  # n1 < n3
    (0.8, 1.2, .25, .25),  # out of bounds
    (0.8, 1.2, -.25, .25),  # out of bounds
    (0.6, 0.3, 0.31, 0.8),  # log(-y): nfrac < n3
    (0.6, 0.3, 0.3, 0.8),  # nfrac = n3
    (0.8, 0.3, 0.31, 0.8),  # log(-y)
    (1, 0.3, 0.31, 0.8),  # log(-y)
    # (1, 0.3, 0.29, 0.8),  # no error
])
def test_error_calc_shape_log(heat, nfrac, n3, n1):
    """Description: check that calc_shape_log() throws erros when appropriate"""
    with pytest.raises(Exception):
        calc_shape_log(heat_frac=heat, nfrac_x=nfrac, nfrac_3=n3, nfrac_1=n1)


@pytest.mark.parametrize("hh,hf,n1,n2,nn,n3", [
    (0.8, 1, 0.9, 0.6, 0.3, 0.25),
    (0.8, 0.81, 0.9, 0.6, 0.3, 0.25),  # small difference in heat units
    (0.8, 1, 0.9, 0.6, 0.25000001, 0.25),  # small difference in nfrac_near and nfrac_3
    (0.633, 0.691, 0.530, 0.101, 0.057, 0.013),  # arbitrary
])
def test_calc_nshape2(hh, hf, n1, n2, nn, n3):
    """Description: check that the shape parameters are correctly calculated by calc_nshapes"""
    observe = calc_shape_parameters(heatfrac_half=hh, heatfrac_full=hf, nfrac_1=n1, nfrac_2=n2, nfrac_near=nn, nfrac_3=n3)
    expect_2 = (calc_shape_log(hh, n2, n3, n1) - calc_shape_log(hf, nn, n3, n1)) / (hf - hh)
    expect_1 = calc_shape_log(hh, n2, n3, n1) + (expect_2 * hh)
    assert observe == [expect_1, expect_2]


@pytest.mark.parametrize("p,n1,n3,shape1,shape2", [
    (0.2, 0.8, 0.5, 0.1, 0.5),  # shape1 < shape2
    (0.2, 0.8, 0.5, 0.5, 0.1),  # shape1 > shape2
    (0.2, 0.8, 0.5, -0.5, 0.1),  # negative shape 1
    (0.2, 0.8, 0.5, 0.5, -0.1),  # negative shape 2
    (0.2, 0.8, 0.5, -0.5, -0.1),  # both negative
    (0.789, 0.587, 0.501, 0.138, 0.920),  # arbitrary
])
def test_calc_nfrac(p, n1, n3, shape1, shape2):
    observe = calc_nitrogen_fraction(phu_frac=p, nfrac_1=n1, nfrac_3=n3, shape1=shape1, shape2=shape2)
    expect = (n1 - n3) * (1 - (p / (p + exp(shape1 + shape2*p)))) + n3
    assert observe == expect


@pytest.mark.parametrize("heatfrac,n1,n2,n3star,n3,phu_half,phu_full,bmass", [
    (0.6, 0.8, 0.6, 0.3, 0.25, 0.5, 1, 1),  # start
    (0.6, 0.8, 0.6, 0.3, 0.01, 0.5, 1, 1),  # small n3star - n3
    (0.8, 0.8, 0.6, 0.3, 0.01, 0.5, 1, 1),  # heatfrac = n1
    (1.0, 0.8, 0.6, 0.3, 0.01, 0.5, 1, 1),  # heatfrac > n1
    (0.6, 0.8, 0.6, 0.3, 0.01, 0.5, 0.55, 1),  # reduced phu_full
    (0.6, 0.8, 0.6, 0.3, 0.01, 0.8, 1, 1),  # increased phu_half
    (0.6, 0.8, 0.6, 0.3, 0.01, 0.8, 1, 0.5),  # fractional bmass
    (0.6, 0.8, 0.6, 0.3, 0.01, 0.8, 1, 0),  # no bmass
    (0.782, 0.533, 0.440, 0.331, 0.002, 0.975, 0.987, 1357.94),  # arbitrary
])
def test_update_nfrac(heatfrac, n1, n2, n3star, n3, phu_half, phu_full, bmass):
    """test that nitrogen fraction is properly updated by update_nfrac()"""
    if bmass == 0:
        expect = 0
    else:
        shapes = calc_shape_parameters(heatfrac_half=phu_half, heatfrac_full=phu_full, nfrac_1=n1, nfrac_2=n2,
                                       nfrac_near=n3star, nfrac_3=n3)
        expect = calc_nitrogen_fraction(phu_frac=heatfrac, nfrac_1=n1, nfrac_3=n3, shape1=shapes[0], shape2=shapes[1])

    mc = mock_crop(biomass_actual=bmass, prev_biomass_actual=bmass, fr_PHU_50=phu_half, fr_PHU_100=phu_full,
                   fr_PHU=heatfrac, prev_fr_PHU=heatfrac, fr_n1=n1, fr_n2=n2, fr_n3ish=n3star, fr_n3=n3)
    update_nitrogen_fraction(mc)
    observe = mc.fr_N

    assert observe == expect


@pytest.mark.parametrize("nf,bm", [
    (1, 1),
    (1, 0),
    (0, 1),
    (0, 0),
    (.25, .3),
    (.10, .257)
])
def test_calc_optimial_nitrogen(nf, bm):
    """test that optimal nitrogen is correctly calculated by calc_optimal_nitrogen()"""
    assert calc_optimal_nitrogen(nf, bm) == nf*bm


@pytest.mark.parametrize("nstart,nf,bm", [
    (0, 1, 1),  # no starting N
    (0.5, 1, 1),  # some N
    (1, 1, 1),  # N=1
    (237.3, .18, 1192.112)  # arbitrary
])
def test_calc_optimial_nitrogen(nstart, nf, bm):
    """test that a plant's optimal nitrogen is correctly updated by update_optimal_nitrogen()"""
    mc = mock_crop(biomass_actual=bm, fr_N=nf, bio_N_opt=nstart)
    update_optimal_nitrogen(mc)
    assert mc.bio_N_opt == nstart + (nf*bm)


@pytest.mark.parametrize("opt,prev,mat,growth", [
    (1, 1, 1, 1),  # all 1
    (0, 1, 1, 1),  # optimal N = 0
    (1, 0, 1, 1),  # previous N = 0
    (1, 1, 0, 1),  # mature N fraction = 0
    (1, 1, 1, 0),  # maximum growth = 0
    (0, 0, 0, 0),  # all 0
    (189.4, 105.01, 0.355, 233.59),  # arbitrary (first route) min(84, 331)
    (189.4, 105.01, 0.355, 23.359),  # arbitrary (second route) min(84, 33.1)
])
def test_calc_max_nitrogen_uptake(opt, prev, mat, growth):
    """test that potential nitrogen uptake is correctly calculated by calc_max_nitrogen_uptake()"""
    expect = min(opt - prev, 4*mat*growth)
    observe = calc_nitrogen_demand(demand=opt, nitrogen_start=prev, mature_nfrac=mat, max_growth=growth)
    assert expect == observe


@pytest.mark.parametrize("opt_n,prev_n,mat_nfrac,grow_max", [
    (1, 1, 1, 1),  # all 1
    (0, 1, 1, 1),  # optimal N = 0
    (1, 0, 1, 1),  # previous N = 0
    (1, 1, 0, 1),  # mature N fraction = 0
    (1, 1, 1, 0),  # maximum growth = 0
    (0, 0, 0, 0),  # all 0
    (189.4, 105.01, 0.355, 233.59),  # arbitrary (first route) min(84, 331)
    (189.4, 105.01, 0.355, 23.359),  # arbitrary (second route) min(84, 33.1)
    (189.4, 189.4, 0.355, 23.359),  # opt_n = prev_n
])
def test_update_max_nitrogen_uptake(opt_n, prev_n, mat_nfrac, grow_max):
    """check that potential nitrogen uptake is correctly updated for a plant by update_max_nitrogen_uptake()"""
    mc = mock_crop(bio_N_opt=opt_n, prev_bio_N=prev_n, fr_n3=mat_nfrac, d_biomass_max=grow_max, N_up=0)
    update_nitrogen_demand(mc)
    if opt_n - prev_n < 0:
        expect = 0
    else:
        expect = calc_nitrogen_demand(opt_n, prev_n, mat_nfrac, grow_max)
    assert mc.N_up == expect


@pytest.mark.parametrize("d,z,r,b", [
    (1, 1, 1, 1),  # all 1
    (0, 1, 1, 1),  # no demand
    (1, 0, 1, 1),  # surface only
    (1, 1, 0, 1),  # no root depth
    (1, 1, 1, -1),  # negative distribution coefficient
    (98.63, 20.2, 32.28, 0.38),  # arbitrary
    (98.63, 20.2, 32.28, 1.21),  # coefficient > 1
    (98.63, 20.2, 32.28, -0.38),  # coefficient < 0
    (98.63, 20.2, 12.28, 0.38),  # depth > root depth
])
def test_calc_surface_nitrogen_uptake(d, z, r, b):
    """check that nitrogen uptake is correctly calculated by calc_surface_nitrogen_uptake()"""
    observe = calc_nitrogen_uptake_to_depth(demand=d, depth=z, root_depth=r, ndistro=b)
    if r <= 0:
        expect = 0
    else:
        expect = (d / (1 - exp(-b))) * (1 - exp(-b * (z / r)))
    assert observe == expect

@pytest.mark.parametrize("d,z,r,b", [
    (1, 1, 1, 0),  # no coefficient (error)
    (0, 0, 0, 0),  # all 0
    (0.3, 0.28, 0.11, 0)
])
def test_error_surface_nitrogen_uptake(d, z, r, b):
    """"check that errors are appropriately thrown for calc_surface_nitrogen_uptake()"""
    with pytest.raises(Exception):
        calc_nitrogen_uptake_to_depth(demand=d, depth=z, root_depth=r, ndistro=b)


@pytest.mark.parametrize("bounds,d,r,b", [
    ([0.25, 0.50, 0.75, 1.00], 1, 1, 1),  # four layers
    ([0.25, 0.50, 0.75, 1.00], 0.5, 1, 1),  # reduced demand
    ([0.25, 0.50, 0.75, 1.00], 1, 0.5, 1),  # reduced root depth
    ([0.25, 0.50, 0.75, 1.00], 1, 1.5, 1),  # increased root depth
    ([0.25, 0.50, 0.75, 1.00], 1, 1, 0.5),  # reduced distribution
    ([0.2, 0.40, 0.6, 0.8, 1.0], 1, 1, 1),  # five layers
    ([1/3, 2/3, 1], 1, 1, 1),  # three layers
    ([0.991, 3.7, 3.89, 12.01, 15], 338.97, 12.88, 0.395),  # arbitrary (roots in 5th)
    ([0.991, 3.7, 3.89, 12.01, 15], 338.97, 4.33, 0.395),  # arbitrary (roots in 4th)
    ([0.991, 3.7, 3.89, 12.01, 15], 338.97, 1.25, 0.395),  # arbitrary (roots in 2nd)
])
def test_calc_layer_nitrogen_potential(bounds, d, r, b):
    """test that potential nitrogen uptake is calculated correctly for each soil layer with calc_layer_nitrogen_potential()"""
    layer_nitrogen = []  # empty list to fill
    upper_nitrogen = 0  # nitrogen in the top boundary (soil surface) is 0
    for i in range(len(bounds)):
        lower_nitrogen = calc_nitrogen_uptake_to_depth(demand=d, depth=bounds[i],
                                                       root_depth=r, ndistro=b)
        layer_nitrogen.append(lower_nitrogen - upper_nitrogen)
        upper_nitrogen = lower_nitrogen
    expect = layer_nitrogen
    observe = calc_layer_nitrogen_potential(boundaries=bounds, demand=d, root_depth=r, ndistro=b)
    assert expect == observe

def test_N_uptake():
    assert False

def test_calc_N_up_each_layer():
    assert False

def calc_bio_N():
    assert False

def test_update_all():
    assert False
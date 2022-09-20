"""
RUFAS: Ruminant Farm Systems Model
File name: test_nitrogen_uptake.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

import pytest
from RUFAS.routines.field.crop.nitrogen_uptake import *

@pytest.mark.parametrize("heat,nfrac,n3,n1",[
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

@pytest.mark.parametrize("heat,nfrac,n3,n1",[
    (0, .5, .25, .75),  # no heat
    (0.8, 0, .25, .75),  # n3 = 0
    (0.8, 0.76, .25, .75),  # nfrac > n1
    (0.8, 0.75, .25, .75),  # nfrac = n1
    (0.8, .5, .25, 0.24),  # n1 < n3
    (0.8, 1.2, .25, .25),  # out of bounds
    (0.8, 1.2, -.25, .25),  # out of bounds
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
    observe = calc_nshapes(heatfrac_half=hh, heatfrac_full=hf, nfrac_1=n1, nfrac_2=n2, nfrac_near=nn, nfrac_3=n3)
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
    observe = calc_nfrac(phu_frac=p, nfrac_1=n1, nfrac_3=n3, shape1=shape1, shape2=shape2)
    expect = (n1 - n3) * (1 - (p / (p + exp(shape1 + shape2*p)))) + n3
    assert observe == expect

def test_update_nfrac():
    assert False
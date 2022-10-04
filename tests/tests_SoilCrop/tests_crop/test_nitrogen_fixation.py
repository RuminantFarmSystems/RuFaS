import pytest
from RUFAS.routines.field.crop.nitrogen_fixation import *


@pytest.mark.parametrize("depth,bounds,expect", [
    (0.2, [0.25, 0.5, 0.75, 1.0], 0),  # first layer
    (0.3, [0.25, 0.5, 0.75, 1.0], 1),  # second layer
    (0.6, [0.25, 0.5, 0.75, 1.0], 2),  # third layer
    (0.8, [0.25, 0.5, 0.75, 1.0], 3),  # fourth layer
    (2, [0.25, 0.5, 0.75, 1.0], 3),  # deeper than deepest layer
    (0, [0.25, 0.5, 0.75, 1.0], None),  # no roots
    (-0.5, [0.25, 0.5, 0.75, 1.0], None),  # negative roots (invalid)
])
def test_get_root_accessible_layer(depth, bounds, expect):
    assert get_deepest_root_accessible_layer(root_depth=depth, layer_bounds=bounds) == expect


@pytest.mark.parametrize("hf,exp", [
    (0, 0),  # first piece
    (0.15, 0),  # first boundary
    (0.2, (6.67 * 0.2) - 1),  # second piece
    (0.3, (6.67 * 0.3) - 1),  # second boundary
    (0.4, 1),  # third part
    (0.55, 1),  # third boundary
    (0.7, 3.75 - (5 * 0.7)),  # forth part
    (0.75, 3.75 - (5 * 0.75)),  # forth boundary
    (1, 0),  # beyond forth boundary
    (-1, 0),  # less than 0
])
def test_calc_growth_stage_factor(hf, exp):
    assert calc_growth_stage_factor(heatfrac=hf) == exp


@pytest.mark.parametrize("nitrates,expect", [
    (0, 1),  # zero
    (50.5, 1),  # first piece
    (100, 1),  # first boundary
    (150.5, 1.5 - (0.0005 * 150.5)),  # second piece
    (300, 1.5 - (0.0005 * 300)),  # second boundary
    (350, 0),  # third piece
    (-100, 1),  # negative
])
def test_calc_nitrate_factor(nitrates, expect):
    assert calc_nitrate_factor(accessible_nitrates=nitrates) == expect


@pytest.mark.parametrize("acc,cap", [
    (0.8, 1),  # 80% capacity
    (0.2, 1),  # 20% capacity
    (80, 100),  # whole numbers
    (100, 100),  # 100% capacity
    (120, 100),  # > 100% capacity
    (0, 100),  # no water
    (137.59, 157.33)  # arbitrary
])
def test_calc_soil_water_factor(acc, cap):
    obs = calc_soil_water_factor(accessible_water=acc, at_capacity_water=cap)
    assert obs == acc / (0.85 * cap)


@pytest.mark.parametrize("d,g,w,n", [
    (1, 1, 1, 1),  # all 1
    (0, 1, 1, 1),  # zero growth factor
    (1, 0, 1, 1),  # zero water factor
    (1, 1, 0, 1),  # zero nitrate factor
    (1, 1, 1, 0),  # zero water factor
    (0, 0, 0, 0),  # all zero
    (38.9, 0.5, 0.6, 0.7),  # arbitrary
    (38.9, 0.5, 0.6, 0.55),  # n < w
    (38.9, 0.5, 1.5, 1.1),  # n > 1, w > 1
])
def test_calc_fixed_nitrogen(d, g, w, n):
    expect = d * g * min(w, n, 1)
    if expect < d:
        expect = d
    assert calc_fixed_nitrogen(d, g, w, n) == expect

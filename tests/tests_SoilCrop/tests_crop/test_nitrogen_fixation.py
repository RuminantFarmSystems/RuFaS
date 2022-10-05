import pytest
from RUFAS.routines.field.crop.nitrogen_fixation import *
from tests.tests_SoilCrop.mock_classes import mock_soil, mock_soil_layer, mock_crop


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
    assert obs == acc / 0.85 * cap


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


@pytest.mark.parametrize("depth, bounds, nitrates, water, field_caps", [
    (1, [0.3, 0.5, 1], [0.2, 0.5, 0.3], [0.5, 0.3, 0.2], [1, 1, 1]),    # all layers accessible
    (0.4, [0.3, 0.5, 1], [0.2, 0.5, 0.3], [0.5, 0.3, 0.2], [1, 1, 1]),  # second layer accessible
    (1.5, [0.3, 0.5, 1], [0.2, 0.5, 0.3], [0.5, 0.3, 0.2], [1, 1, 1]),  # deeper than all layers
    (20.25, [15.32, 22.70, 31.09], [22.1, 5.96, 13.0], [10.5, 15.17, 8.90], [12.0, 19.9, 8.8]),  # arbitrary
])
def test_get_accessible_soil_resources(depth, bounds, nitrates, water, field_caps):
    # observed
    ms = mock_soil(soil_layers=[])
    for b, n, w, c in zip(bounds, nitrates, water, field_caps):
        ml = mock_soil_layer(bottom_depth=b, NO3=n, soil_water=w, fc_water=c)
        ms.soil_layers.append(ml)
    observe = get_accessible_soil_resources(soil=ms, root_depth=depth)
    observe = list(observe.values())
    # expected
    deepest = get_deepest_root_accessible_layer(root_depth=depth, layer_bounds=bounds)
    accessible_water = 0
    capacity = 0
    accessible_nitrates = 0
    for layer in ms.soil_layers[slice(deepest)]:
        accessible_water += layer.soil_water
        capacity += layer.fc_water
        accessible_nitrates += layer.NO3
    expect = [deepest, accessible_water, capacity, accessible_nitrates]
    # check equivalence
    assert observe == expect


@pytest.mark.parametrize("cdepth,cheatfrac,cuptakes,sbounds,swater,scapacity,snitrate", [
    (1, .5, [.5, .25, .05], [0.3, 0.6, 1], [.5, .6, .8], [1, 1, 1], [0.3, 0.5, 0.25]),  # all layers accessible
    (0.4, .5, [.5, .25, .05], [0.3, 0.6, 1], [.5, .6, .8], [1, 1, 1], [0.3, 0.5, 0.25]),  # second layer accessible
    (1.5, .5, [.5, .25, .05], [0.3, 0.6, 1], [.5, .6, .8], [1, 1, 1], [0.3, 0.5, 0.25]),  # deeper than layers
    (1, .5, [.5, .25, .05], [0.3, 0.6, 1], [.5, .6, .8], [.6, .6, 1.2], [0.3, 0.5, 0.25]),  # altered capacity
    (37.9, 0.83, [15.3, 5.9, 0.99], [22.9, 37.0, 45.3], [83.2, 15.9, 8.8], [79.0, 16.0, 10.3], [15.3, 6.3, 0.05]),  # aribtrary
])
def test_fix_nitrogen(cdepth, cheatfrac, cuptakes, sbounds, swater, scapacity, snitrate):
    # observe
    msoil = mock_soil(soil_layers=[])
    for boundary, water, capacity, nitrate in zip(sbounds, swater, scapacity, snitrate):
        mlayer = mock_soil_layer(bottom_depth=boundary, soil_water=water, fc_water=capacity, NO3=nitrate)
        msoil.soil_layers.append(mlayer)
    mcrop = mock_crop(z_root=cdepth, fr_PHU=cheatfrac, pot_N_up_each_layer=cuptakes)
    fix_nitrogen(crop=mcrop, soil=msoil)
    # expect
    accessible_resources = get_accessible_soil_resources(soil=msoil, root_depth=cdepth)
    deepest_layer=accessible_resources["deepest layer"]
    accessible_layers = [layer for layer in msoil.soil_layers[slice(deepest_layer)]]
    demand = calc_N_demand(crop_type=mcrop, accessible_layers=accessible_layers)
    growth_factor = calc_growth_stage_factor(heatfrac=cheatfrac)
    water_factor = calc_soil_water_factor(accessible_water=accessible_resources["water"],
                                          at_capacity_water=accessible_resources["water capacity"])
    nitrate_factor = calc_nitrate_factor(accessible_nitrates=accessible_resources["nitrates"])
    fixed_nitrogen = calc_fixed_nitrogen(demand, growth_factor, water_factor, nitrate_factor)
    # assertion
    assert fixed_nitrogen == mcrop.N_fix


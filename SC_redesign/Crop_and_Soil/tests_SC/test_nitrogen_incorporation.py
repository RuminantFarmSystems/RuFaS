import pytest

from SC_redesign.Crop_and_Soil.crop.nitrogen_incorporation import *
from pytest_mock import MockerFixture
from unittest.mock import MagicMock


# --- static function tests ----
@pytest.mark.parametrize("halfheat,heatfrac,emerge,half,near,mature", [
    (0.5, 1.0, 0.8, 0.6, 0.3, 0.2),  # start
    (0.99, 1.0, 0.8, 0.6, 0.3, 0.2),  # half_heat close to mature heat
    (0.01, 1.0, 0.8, 0.6, 0.3, 0.2),  # small half_heat
    (0.5, 1.0, 0.8, 0.6, 0.20001, 0.2),  # near very close to mature
    (0.286, 0.54, 0.522, 0.4, 0.1, 0.08),  # arbitrary
    # Above tests are copied from old subroutine tests
    (0.8, 1, 0.9, 0.6, 0.3, 0.25),
    (0.8, 0.81, 0.9, 0.6, 0.3, 0.25),  # small difference in heat units
    (0.8, 1, 0.9, 0.6, 0.25000001, 0.25),  # small difference in nfrac_near and nfrac_3
    (0.633, 0.691, 0.530, 0.101, 0.057, 0.013),  # arbitrary
])
def test_determine_nitrogen_shape_parameters(halfheat, heatfrac, emerge, half, near, mature):
    """check that the shape parameters are correctly calculated by determine_nshapes()"""
    observe = NitrogenIncorporation.determine_nitrogen_shape_parameters(halfheat, heatfrac, emerge, half, near, mature)
    expect_2 = (NitrogenIncorporation.determine_shape_log(halfheat, half, mature, emerge) -
                NitrogenIncorporation.determine_shape_log(heatfrac, near, mature, emerge)) / (heatfrac - halfheat)
    expect_1 = NitrogenIncorporation.determine_shape_log(halfheat, half, mature, emerge) + (expect_2 * halfheat)
    assert observe == [expect_1, expect_2]


@pytest.mark.parametrize("heatfrac,current,mature,emergence", [
    (1, .5, .25, .75),  # max_evapotranspiration heatfrac
    (0.8, .5, .25, 1),  # max_evapotranspiration mature nfrac
    (0.32, .5, .25, .75),  # arbitrary
])
def test_determine_shape_log(heatfrac, current, mature, emergence):
    """check that determine_shape_log() calculates correct output"""
    observe = NitrogenIncorporation.determine_shape_log(heatfrac, current, mature, emergence)
    bottom = 1 - ((current - mature) / (emergence - mature))
    inside = (heatfrac / bottom) - heatfrac
    expect = log(inside)
    assert observe == expect


@pytest.mark.parametrize("heatfrac,current,mature,emergence", [
    (0, .5, .25, .75),  # no heatfrac
    (0.8, 0, .25, .75),  # mature nfrac = 0
    (0.8, 0.76, .25, .75),  # nfrac > emergence
    (0.8, 0.75, .25, .75),  # nfrac = emergence
    (0.8, .5, .25, 0.24),  # emergence < mature
    (0.8, 1.2, .25, .25),  # out of bounds
    (0.8, 1.2, -.25, .25),  # out of bounds
    (0.6, 0.3, 0.31, 0.8),  # log(-y): nfrac < mature
    (0.6, 0.3, 0.3, 0.8),  # nfrac = mature
    (0.8, 0.3, 0.31, 0.8),  # log(-y)
    (1, 0.3, 0.31, 0.8),  # log(-y)
    # (1, 0.3, 0.29, 0.8),  # no error
])
def test_error_determine_shape_log(heatfrac, current, mature, emergence):
    """check that determine_shape_log() throws errors when appropriate"""
    with pytest.raises(Exception):
        NitrogenIncorporation.determine_shape_log(heatfrac, current, mature, emergence)


@pytest.mark.parametrize("heatfrac,emerge,mature,shape1,shape2", [
    (0.2, 0.8, 0.5, 0.1, 0.5),  # shape1 < shape2
    (0.2, 0.8, 0.5, 0.5, 0.1),  # shape1 > shape2
    (0.2, 0.8, 0.5, -0.5, 0.1),  # negative shape 1
    (0.2, 0.8, 0.5, 0.5, -0.1),  # negative shape 2
    (0.2, 0.8, 0.5, -0.5, -0.1),  # both negative
    (0.789, 0.587, 0.501, 0.138, 0.920),  # arbitrary
])
def test_determine_optimal_nitrogen_fraction(heatfrac, emerge, mature, shape1, shape2):
    """ensure that nitrogen fraction is correctly calculated by determine_optimal_nitrogen_fraction()"""
    observe = NitrogenIncorporation.determine_optimal_nitrogen_fraction(heatfrac, emerge, mature, shape1, shape2)
    expect = (emerge - mature) * (1 - (heatfrac / (heatfrac + exp(shape1 + shape2 * heatfrac)))) + mature
    assert observe == expect


@pytest.mark.parametrize("nfrac,biomass", [
    (1, 1),
    (1, 0),
    (0, 1),
    (0, 0),
    (.25, .3),
    (.10, .257)
])
def test_determine_optimal_nitrogen(nfrac, biomass):
    """test that optimal nitrogen is correctly calculated by determine_optimal_nitrogen()"""
    assert NitrogenIncorporation.determine_optimal_nitrogen(nfrac, biomass) == nfrac * biomass


@pytest.mark.parametrize("optimal,previous,mature,max_growth", [
    (1, 1, 1, 1),  # all 1
    (0, 1, 1, 1),  # optimal N = 0
    (1, 0, 1, 1),  # previous N = 0
    (1, 1, 0, 1),  # mature N fraction = 0
    (1, 1, 1, 0),  # maximum growth = 0
    (0, 0, 0, 0),  # all 0
    (189.4, 105.01, 0.355, 233.59),  # arbitrary (first route) min(84, 331)
    (189.4, 105.01, 0.355, 23.359),  # arbitrary (second route) min(84, 33.1)
])
def test_determine_potential_nitrogen_uptake(optimal, previous, mature, max_growth):
    """test that potential nitrogen uptake is correctly calculated by determine_max_nitrogen_uptake()"""
    expect = min(optimal - previous, 4 * mature * max_growth)
    observe = NitrogenIncorporation.determine_potential_nitrogen_uptake(optimal, previous, mature, max_growth)
    assert expect == observe


@pytest.mark.parametrize("root,depths,expect", [
    (1.5, [0, 1, 2, 3], 3),  # roots access layer 3
    (2.7, [0, 1, 2, 3], 4),  # 4th layer
    (3.8, [0, 1, 2, 3], 4),  # beyond max_evapotranspiration depth
    (83.33, [10.4, 18.20, 63.7, 100, 1937.8], 4)  # arbitrary
])
def test_determine_deepest_accessible_layer(root, depths, expect):
    assert NitrogenIncorporation.determine_deepest_accessible_layer(root, depths) == expect


@pytest.mark.parametrize("root,depths", [
    (-1, [0, 1, 2, 3]),  # root < 0
    (0, [0, 1, 2, 3]),  # root = 0
])
def test_error_determine_deepest_accessible_layer(root, depths):
    with pytest.raises(ValueError):
        NitrogenIncorporation.determine_deepest_accessible_layer(root, depths)


@pytest.mark.parametrize("bounds,demand,root_depth,ndistro", [
    ([0.25, 0.50, 0.75, 1.00], 1, 1, 1),  # four layers
    ([0.25, 0.50, 0.75, 1.00], 0.5, 1, 1),  # reduced demand
    ([0.25, 0.50, 0.75, 1.00], 1, 0.5, 1),  # reduced root depth
    ([0.25, 0.50, 0.75, 1.00], 1, 1.5, 1),  # increased root depth
    ([0.25, 0.50, 0.75, 1.00], 1, 1, 0.5),  # reduced distribution
    ([0.2, 0.40, 0.6, 0.8, 1.0], 1, 1, 1),  # five layers
    ([1 / 3, 2 / 3, 1], 1, 1, 1),  # three layers
    ([0.991, 3.7, 3.89, 12.01, 15], 338.97, 12.88, 0.395),  # arbitrary (roots in 5th)
    ([0.991, 3.7, 3.89, 12.01, 15], 338.97, 4.33, 0.395),  # arbitrary (roots in 4th)
    ([0.991, 3.7, 3.89, 12.01, 15], 338.97, 1.25, 0.395),  # arbitrary (roots in 2nd)
])
def test_determine_layer_nitrogen_uptake_potential(bounds, demand, root_depth, ndistro):
    """
    ensure potential nitrogen uptake is calculated correctly for each soil layer with
    determine_layer_nitrogen_potential()
    """
    layer_nitrogen = []  # empty list to fill
    upper_nitrogen = 0  # nitrogen in the top boundary (soil surface) is 0
    for i in range(len(bounds)):
        lower_nitrogen = NitrogenIncorporation.determine_nitrogen_uptake_to_depth(demand, bounds[i], root_depth,
                                                                                  ndistro)
        layer_nitrogen.append(lower_nitrogen - upper_nitrogen)
        upper_nitrogen = lower_nitrogen
    expect = layer_nitrogen
    observe = NitrogenIncorporation.determine_layer_nitrogen_uptake_potential(bounds, demand, root_depth, ndistro)
    assert expect == observe


@pytest.mark.parametrize("bounds,demand,root_depth,ndistro", [
    ([1, 0], 1, 1, 1),
    ([1, .5, 3], 1, 1, 1),
    ([1, 2, 3, 2.9], 1, 1, 1),
    ([100, 100.1, 100.01], 1, 1, 1),
    ([0.5, 0.4, 0.3], 0.53, .9, 0.11),
    ([1, 2, 3, 3], 1, 1, 1),  # ascending with redundant layer
    ([1, 1, 1, 1], 1, 1, 1),  # redundant layers
    ([3, 2, 1, 1], 1, 1, 1),  # descending with redundant layer
])
def test_error_determine_layer_nitrogen_uptake_potential(bounds, demand, root_depth, ndistro):
    """check that determine_layer_nitrogen_potential throws an error when soil boundaries are not properly ordered"""
    with pytest.raises(Exception):
        NitrogenIncorporation.determine_layer_nitrogen_uptake_potential(bounds, demand, root_depth, ndistro)


@pytest.mark.parametrize("demand,depth,root_depth,ndistro", [
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
def test_determine_nitrogen_uptake_to_depth(demand, depth, root_depth, ndistro):
    """check that nitrogen uptake is correctly calculated by determine_surface_nitrogen_uptake()"""
    observe = NitrogenIncorporation.determine_nitrogen_uptake_to_depth(demand, depth, root_depth, ndistro)
    if root_depth <= 0:
        expect = 0
    else:
        expect = (demand / (1 - exp(-ndistro))) * (1 - exp(-ndistro * (depth / root_depth)))
    assert observe == expect


@pytest.mark.parametrize("demand,depth,root_depth,ndistro", [
    (1, 1, 1, 0),  # no coefficient (error)
    (0, 0, 0, 0),  # all 0
    (0.3, 0.28, 0.11, 0)
])
def test_error_determine_nitrogen_uptake_to_depth(demand, depth, root_depth, ndistro):
    """"check that errors are appropriately thrown for determine_surface_nitrogen_uptake()"""
    with pytest.raises(Exception):
        NitrogenIncorporation.determine_nitrogen_uptake_to_depth(demand, depth, root_depth, ndistro)


@pytest.mark.parametrize("pots,avails", [
    ([0.5, 0.25, 0.05], [0.3, 0.2, 0.01]),
    ([0.5, 0.25, 0.05], [0.6, 0.3, 0.06]),  # abundant nitrates
    ([0.5, 0.25, 0.05], [0, 0, 0]),  # no nitrates
    ([0.5, 0.25, 0.05, .01], [0.3, 0.2, 0.01, 0.01]),  # 4 layers
    ([0.5, 0.25, 0.05], [0.5, 0.25, 0.05]),  # exactly met demands
    ([112.3, 50.44, 17, 12.99], [50.33, 15.10, 8.05, 6.66]),  # arbitrary
])
def test_determine_layer_nitrogen_demands(pots, avails):
    """test that nitrogen demand is correctly calculated for each layer by determine_layer_nitrogen_demand()"""
    observe = NitrogenIncorporation.determine_layer_nitrogen_demands(pots, avails)
    # starting values
    no3_sum = 0
    up_sum = 0
    demand_list = []
    # loop over layers
    for pot_up, no3 in zip(pots, avails):
        demand = up_sum - no3_sum  # difference between potential and available
        demand = max(demand, 0)  # constrain to zero
        demand_list.append(demand)
        up_sum += pot_up
        no3_sum += no3
    assert demand_list == pytest.approx(observe, rel=0.00001)


@pytest.mark.parametrize("demand,potential,nitrate", [
    ([1, 1, 1], [0.5, 0.5, 0.5], [0.3, 0.3, 0.3]),  # use nitrate
    ([1, 1, 1], [0.5, 0.5, 0.5], [0.6, 0.6, 0.6]),  # use nitrogen
    ([1, 1, 1], [0.5, 0.5, 0.5], [0.6, 0.3, 0.6]),  # use nitrogen, then nitrate, then nitrogen
    ([1, 1, 1], [0.5, 0.5, 0.5], [0.6, 0.3, 0.6]),  # increased demand
    ([0.01, 0.01, 0.01], [0.5, 0.5, 0.5], [0.6, 0.3, 0.6]),  # decreased demand
    ([25, 8.33, 2.05, 12.99, 0.5], [22.5, 15.98, 2.22, 35.4, 0.001], [15.5, 20.99, 8, 5.5, 0.1])  # arbitrary
])
def test_determine_layer_nitrogen_uptake(demand, potential, nitrate):
    """test that actual nitrogen uptake from each layer is properly calculated by determine_layer_nitrogen_uptake()"""
    observe = NitrogenIncorporation.determine_layer_nitrogen_uptake(demand, potential, nitrate)
    expect = []
    for d, p, n in zip(demand, potential, nitrate):
        uptake = min(p + d, n)
        expect.append(uptake)
    assert observe == expect


@pytest.mark.parametrize("reqs,srcs", [
    ([0, 0], [1, 1]),  # no requests
    ([0.5, 0], [1, 1]),  # request from first layer
    ([0, 0.5], [1, 1]),  # request from second layer
    ([0.5, 0.5], [1, 1]),  # request from both
    ([18.66, 33.74], [20.30, 19.93])  # arbitrary
])
def test_determine_layer_extracted_resource(reqs, srcs):
    """ensure that extracted nitrogen is correctly calculated for each layer"""
    draws = []
    for i in range(len(reqs)):
        draws.append(NitrogenIncorporation.determine_extracted_resource(reqs[i], srcs[i]))
    assert draws == NitrogenIncorporation.determine_layer_extracted_resource(reqs, srcs)


@pytest.mark.parametrize("requested,available", [
    (0, 1),  # no request
    (0.5, 1),  # request < avaialble
    (1, 1),  # request = available
    (1.5, 1),  # request > available
    (85.93, 232.7)  # arbitrary
])
def test_determine_extracted_resource(requested, available):
    """ensure that extracted resource is correctly calculated by determine_extracted_resource()"""
    if available < 0:
        drawn = 0
    elif requested > available:
        drawn = available
    else:
        drawn = requested
    assert drawn == NitrogenIncorporation.determine_extracted_resource(requested, available)


@pytest.mark.parametrize("nitrates,expect", [
    (0, 1),  # A
    (13.2, 1),  # arbitrary A
    (100, 1),  # A edge
    (100.1, 1.5 - 5e-4 * 100.1),  # B
    (200, 1.5 - 5e-4 * 200),  # B
    (300, 1.5 - 5e-4 * 300),  # B
    (300.1, 0),  # C
    (450, 0)  # C
])
def test_determine_nitrate_factor(nitrates, expect):
    assert NitrogenIncorporation.determine_nitrate_factor(nitrates) == expect


@pytest.mark.parametrize("heatfrac,expect", [
    (-1.0, 0.0),  # piece A
    (0.00, 0.0),
    (0.05, 0.0),
    (0.15, 0.0),
    (0.22, 6.67 * 0.22 - 1),  # piece B
    (0.30, 6.67 * 0.30 - 1),
    (0.43, 1.0),  # piece C
    (0.55, 1.0),
    (0.67, 3.75 - 5 * 0.67),  # piece D
    (0.75, 3.75 - 5 * 0.75),
    (0.76, 0.0),  # piece E
    (1.39, 0.0)
])
def test_determine_fixation_stage_factor(heatfrac, expect):
    assert NitrogenIncorporation.determine_fixation_stage_factor(heatfrac) == expect


@pytest.mark.parametrize("demand,stage,water,nitrate,expect", [
    (0, 1, 1, 1, 0),  # no demand
    (1, 1, 1, 1, 1),  # all 1
    (1, 1, 0.2, 0.5, 0.2),  # water min
    (1, 1, 0.6, 0.5, 0.5),  # nitrate min
    (1, 0.5, 0.6, 0.5, 0.5 * 0.5),  # reduced stage
    (0.3, 0.5, 0.6, 0.5, 0.3 * 0.5 * 0.5)  # reduced demand
])
def test_determine_fixed_nitrogen(demand, stage, water, nitrate, expect):
    """check that nitrogen values are calculated as expected with determine_fixed_nitrogen()"""
    assert NitrogenIncorporation.determine_fixed_nitrogen(demand, stage, water, nitrate) == expect


@pytest.mark.parametrize("demand,stage,water,nitrate", [
    (1, -1, 1, 1),  # neg stage
    (1, 1, -1, 1),  # neg water
    (1, 1, 1, -1),  # neg nitrate
    (1, 1.2, 1, 1),  # stage > 1
    (1, 1, 2, 1),  # water > 1
    (1, 1, 1, 100)  # nitrate > 1
])
def test_error_determine_fixed_nitrogen(demand, stage, water, nitrate):
    with pytest.raises(ValueError):
        NitrogenIncorporation.determine_fixed_nitrogen(demand, stage, water, nitrate)


@pytest.mark.parametrize("prev,new,fix", [
    (1, 1, 1),  # all 1
    (1, 1, 0),  # no fixation
    (1, 0, 1),  # no new nitrogen
    (0, 1, 1),  # no previous nitrogen
    (0, 0, 0),  # all 0
    (50.39, 10.55, 3.05)  # arbitrary
])
def test_determine_stored_nitrogen(prev, new, fix):
    """test the stored nitrogen is properly calculated by determine_stored_nitrogen()"""
    observe = NitrogenIncorporation.determine_stored_nitrogen(new, prev, fix)
    assert observe == prev + new + fix


# ---- initialization functions (reusable) ----
def init_incorp(**kwargs):
    """helper function to create GrowthConstraint instance, with specified attributes"""
    incorp = NitrogenIncorporation()
    for key, val in kwargs.items():
        setattr(incorp, key, val)
    return incorp


# ---- member function tests ----
@pytest.mark.parametrize("old,new", [
    (None, 1),  # no start
    (0, 1),  # start = 0
    (1, 2),  # start = 0
    (2, 1),  # start > new
    (133.26, 149.4)  # arbitrary
])
def test_shift_nitrogen_time(old, new):
    incorp = init_incorp(previous_nitrogen=old, nitrogen=new)
    incorp.shift_nitrogen_time()
    assert incorp.previous_nitrogen == new


@pytest.mark.parametrize("root_depth,depths,expect", [
    (1.5, [0, 1, 2, 3], [4, 1]),
    (2.6, [0, 1, 2, 3], [4, 0]),
    (0.3, [0, 0.5, 1, 2, 3], [5, 3]),
    (28.4, [18.2, 21.6, 100.4], [3, 0])
])
def test_find_deepest_accessible_soil_layer(root_depth, depths, expect):
    """ensure that layers are partitioned correctly by determine_deepest_accessible_soil_layer"""
    crop = init_incorp(root_depth=root_depth)
    crop.find_deepest_accessible_soil_layer(depths)
    assert crop.total_soil_layers == expect[0]
    assert crop.accessible_soil_layers == NitrogenIncorporation.determine_deepest_accessible_layer(root_depth, depths)
    assert crop.inaccessible_soil_layers == expect[1]


@pytest.mark.parametrize("deepest,layers", [
    (1, [1, 2, 3, 4]),  # one layer
    (2, [1, 2, 3, 4]),  # two layers
    (3, [1, 2, 3, 4]),  # three layers
    (4, [1, 2, 3, 4]),  # four layers
    (2, [22.5, 80.6, 100.0, 199.9]),  # arbitrary list
])
def test_access_layers(deepest, layers):
    """check that soil layers are accessed correctly with access_layers()"""
    crop = init_incorp(accessible_soil_layers=deepest)
    assert crop.access_layers(layers) == layers[slice(deepest)]


@pytest.mark.parametrize("missed,uptakes,expect", [
    (-1, [0.25, 0.5, 1], [0.25, 0.5, 1]),  # negative missed layers
    (0, [0.25, 0.5, 1], [0.25, 0.5, 1]),  # no missed layers
    (1, [0.25, 0.5, 1], [0.25, 0.5, 1, 0]),  # one missed layer
    (2, [0.25, 0.5, 1], [0.25, 0.5, 1, 0, 0]),  # 2 missed layers
    (3, [12.5, 8.3, 22.2, 7.8], [12.5, 8.3, 22.2, 7.8, 0, 0, 0]),  # arbitrary, 3 missed
])
def test_extend_nitrate_uptakes_to_full_profile(missed, uptakes, expect):
    """check that the correct number of zeros are padded to uptakes by extend_nitrate_uptakes_to_full_profile()"""
    crop = init_incorp(inaccessible_soil_layers=missed, actual_nitrogen_uptakes=uptakes)
    crop.extend_nitrate_uptakes_to_full_profile()
    assert crop.actual_nitrogen_uptakes == expect


@pytest.mark.parametrize("uptakes,nitrates", [
    ([1], [1]),  # start
    ([1], [0]),  # no nitrates
    ([0], [1]),  # no uptakes
    ([0.5], [1]),  # uptakes < nitrates
    ([1.2], [1]),  # uptakes > nitrates
    ([37.9, 40.2, 18.3], [100.5, 83.3, 30.7]),  # arbitrary - abundant nitrates
    ([87.36, 86.40, 30.33], [82.4, 83.0, 29.9]),  # nitrates limited
    ([57.33, 32.20, 0], [40.2, 99.0, 30.7]),  # no uptake from last layer
])
def test_extract_nitrogen_from_soil_layers(uptakes, nitrates):
    nitrates_copy = nitrates.copy()

    incorp = init_incorp(actual_nitrogen_uptakes=uptakes)
    incorp.extract_nitrogen_from_soil_layers(nitrates)

    remaining = []
    for i in range(len(uptakes)):
        remaining.append(max(nitrates_copy[i] - uptakes[i], 0))
    # print(nitrates_copy)
    # print(remaining)
    assert nitrates == remaining


@pytest.mark.parametrize("uptakes", [
    [1],  # one layer
    [1, 1, 1, 1],  # four layers
    [81.2, 0],  # arbitrary with zero
    [15.3, 18.2, 4, 20.33]
])
def test_tally_total_nitrogen_uptake(uptakes):
    """check that total nitrogen is correctly calculated by tally_total_nitrogen_uptake()"""
    crop = init_incorp(actual_nitrogen_uptakes=uptakes)

    crop.tally_total_nitrogen_uptake()
    assert crop.total_nitrogen_uptake == sum(uptakes)


@pytest.mark.parametrize("fixer,nitrates,water", [
    (True, 100, 0.5),  # fixer with nitrates
    (True, 0, 0.5),  # fixer without nitrates
    (False, 100, 0.5),  # non-fixer with nitrates
    (False, 0, 0.5),  # non-fixer without nitrates
])
def test_try_fixation(fixer, nitrates, water, mocker: MockerFixture):
    """check that try_fixation calls its sub-functions if fixation occurs"""
    patch_update_fixation_attributes = mocker.patch(
        "SC_redesign.Crop_and_Soil.crop.nitrogen_incorporation.NitrogenIncorporation.update_fixation_attributes")
    patch_fix_nitrogen = mocker.patch(
        "SC_redesign.Crop_and_Soil.crop.nitrogen_incorporation.NitrogenIncorporation.fix_nitrogen")
    crop = init_incorp(is_nitrogen_fixer=fixer)
    crop.try_fixation(nitrates, water)
    if fixer:
        patch_update_fixation_attributes.assert_called_once()
        patch_fix_nitrogen.assert_called_once()
    else:
        patch_update_fixation_attributes.assert_not_called()
        patch_fix_nitrogen.assert_not_called()
        assert crop.fixed_nitrogen == 0


def test_update_fixation_attributes(mocker: MockerFixture):
    """"check that update_nitrate_attributes calls both its sub-functions"""
    patch_determine_nitrate_factor = mocker.patch(
        "SC_redesign.Crop_and_Soil.crop.nitrogen_incorporation.NitrogenIncorporation.determine_nitrate_factor")
    patch_determine_determine_fixation_stage_factor = mocker.patch(
        "SC_redesign.Crop_and_Soil.crop.nitrogen_incorporation.NitrogenIncorporation.determine_fixation_stage_factor")
    crop = init_incorp()
    crop.update_fixation_attributes(100)
    patch_determine_nitrate_factor.assert_called_once()
    patch_determine_determine_fixation_stage_factor.assert_called_once()


@pytest.mark.parametrize("uptake,demand,water,fixfact,nitrate", [
    (0, 10, 0.5, 0.25, 0.3),  # unmet demand, water > nitrate > fix
    (10, 10, 0.5, 0.25, 0.3),  # no unmet demand, water > nitrate > fix
    (5, 10, 0.2, 0.25, 0.3),  # unmet demand, water < fix < nitrate
    (5, 10, 0.2, 0.25, 0.22),  # unmet demand, water < nitrate < fix
    (73.4, 112.5, 0.83, 0.11, 0.44),  # arbitrary
])
def test_fix_nitrogen(uptake, demand, water, fixfact, nitrate):
    """check that fixed nitrogen is properly calculated by fix_nitrogen()"""
    crop = init_incorp(potential_nitrogen_uptake=demand, total_nitrogen_uptake=uptake, fixation_stage_factor=fixfact,
                       nitrate_factor=nitrate)
    crop.fix_nitrogen(water)
    if (demand - uptake) > 0:
        assert crop.fixed_nitrogen == NitrogenIncorporation.determine_fixed_nitrogen(demand - uptake, fixfact, water,
                                                                                     nitrate)
    else:
        assert crop.fixed_nitrogen == 0


@pytest.mark.parametrize("depths,nitrates", [
    ([.5, 1, 10, 20], [0.5, 0.8, 5, 10])
])
def test_uptake_nitrogen(depths, nitrates):
    # initialize crop and run method
    crop = init_incorp(potential_nitrogen_uptake=17.5, root_depth=35.0, nitrogen_distro_param=0.32)

    # Mock functions
    crop.find_deepest_accessible_soil_layer = MagicMock(return_value=None)
    crop.access_layers = MagicMock(return_value=[1, 2, 3])
    NitrogenIncorporation.determine_layer_nitrogen_uptake_potential = MagicMock(return_value=[3.25, 6.33, 7.10])
    NitrogenIncorporation.determine_layer_nitrogen_demands = MagicMock(return_value=[12, 15, 17])
    NitrogenIncorporation.determine_layer_nitrogen_uptake = MagicMock(return_value=[8.9, 9.9, 13.12])
    NitrogenIncorporation.determine_layer_extracted_resource = MagicMock(return_value=[5.0, 4.0, 2.0])
    crop.extend_nitrate_uptakes_to_full_profile = MagicMock()
    crop.extract_nitrogen_from_soil_layers = MagicMock()
    crop.tally_total_nitrogen_uptake = MagicMock()

    # run function
    crop.uptake_nitrogen(nitrates, depths)

    # check assertions
    crop.find_deepest_accessible_soil_layer.assert_called_once_with(depths)
    NitrogenIncorporation.determine_layer_nitrogen_uptake_potential.assert_called_once_with([1, 2, 3],
                                                                                            17.5, 35.0, 0.32)
    assert crop.layer_nitrogen_potentials == [3.25, 6.33, 7.10]
    NitrogenIncorporation.determine_layer_nitrogen_demands.assert_called_once_with([3.25, 6.33, 7.10], [1, 2, 3])
    assert crop.unmet_nitrogen_demands == [12, 15, 17]
    NitrogenIncorporation.determine_layer_nitrogen_uptake.assert_called_once_with([12, 15, 17], [3.25, 6.33, 7.10],
                                                                                  [1, 2, 3])
    assert crop.nitrogen_requests == [8.9, 9.9, 13.12]
    NitrogenIncorporation.determine_layer_extracted_resource.assert_called_once_with([8.9, 9.9, 13.12], [1, 2, 3])
    assert crop.actual_nitrogen_uptakes == [5.0, 4.0, 2.0]
    crop.extend_nitrate_uptakes_to_full_profile.assert_called_once()
    crop.extract_nitrogen_from_soil_layers.assert_called_once()
    crop.tally_total_nitrogen_uptake.assert_called_once()


@pytest.mark.parametrize("nitrates,depths,water_factor,gate", [
    ([.5, .3, .2], [1, 2, 5], .692, True),
    ([.5, .3, .2], [1, 2, 5], .692, False)
])
def test_incorporate_nitrogen(nitrates, depths, water_factor, gate):
    # initialize object
    crop = init_incorp(heat_fraction=0.38, half_mature_heat_fraction=.54, mature_heat_fraction=0.99,
                       emergence_nitrogen_fraction=0.71, half_mature_nitrogen_fraction=0.68,
                       near_mature_nitrogen_fraction=0.62, mature_nitrogen_fraction=0.60,
                       biomass=122.8, previous_nitrogen=0, biomass_growth_max=999)

    # mock intermediate functions
    crop.shift_nitrogen_time = MagicMock(return_value=None)
    crop.determine_nitrogen_shape_parameters = MagicMock(return_value=[1.2, 0.8])
    crop.determine_optimal_nitrogen_fraction = MagicMock(return_value=0.75)
    if gate:
        crop.determine_optimal_nitrogen = MagicMock(return_value=-268)
    else:
        crop.determine_optimal_nitrogen = MagicMock(return_value=268)
    crop.determine_potential_nitrogen_uptake = MagicMock(return_value=123.1)
    crop.uptake_nitrogen = MagicMock(return_value=None)  # TODO - don't know how to mock attribute updates
    crop.access_layers = MagicMock(return_value=[5, 10, 15.3])
    crop.try_fixation = MagicMock(return_value=None)
    NitrogenIncorporation.determine_stored_nitrogen = MagicMock(return_value=99.3)

    # run method
    crop.incorporate_nitrogen(nitrates, depths, water_factor)

    # assertions
    crop.shift_nitrogen_time.assert_called_once()
    crop.determine_nitrogen_shape_parameters.assert_called_once_with(0.54, 0.99, 0.71, 0.68, 0.62, 0.60)
    assert crop._nitrogen_shapes == [1.2, 0.8]
    crop.determine_optimal_nitrogen_fraction.assert_called_once_with(0.38, 0.71, 0.60, 1.2, 0.8)
    assert crop.optimal_nitrogen_fraction == 0.75
    if gate:
        crop.determine_optimal_nitrogen.assert_called_once_with(0.75, 122.8)
        assert crop.optimal_nitrogen == -268
        crop.determine_potential_nitrogen_uptake.assert_not_called()
        assert crop.potential_nitrogen_uptake == 0
    else:
        assert crop.optimal_nitrogen == 268
        crop.determine_potential_nitrogen_uptake.assert_called_once_with(268, 0, 0.60, 999)
        assert crop.potential_nitrogen_uptake == 123.1
    crop.uptake_nitrogen.assert_called_once_with(nitrates, depths)
    crop.try_fixation.assert_called_once_with(5+10+15.3, water_factor)
    NitrogenIncorporation.determine_stored_nitrogen.assert_called_once()  # should be called_once_with() w/ attr mocked
    assert crop.nitrogen == 99.3

import pytest

from SC_redesign.Crop_and_Soil.crop.nitrogen_incorporation import *
from pytest_mock import MockerFixture


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
    ensure potential nitrogen uptake is calculated correctly for each soil layer with determine_layer_nitrogen_potential()
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
def test_incorporate_nitrogen():
    assert False


def test_uptake_nitrogen():
    assert False


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
    print(nitrates_copy)
    print(remaining)

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

## ---- OLD ----

# TODO: will be incorporated into incorporate_nitrogen() integration test
# @pytest.mark.parametrize("half_heat,mat_heat,emerge,half,near,mature", [
#     (0.5, 1.0, 0.8, 0.6, 0.3, 0.2),  # start
#     (0.99, 1.0, 0.8, 0.6, 0.3, 0.2),  # half_heat close to mature heat
#     (0.01, 1.0, 0.8, 0.6, 0.3, 0.2),  # small half_heat
#     (0.5, 1.0, 0.8, 0.6, 0.20001, 0.2),  # near very close to mature
#     (0.286, 0.54, 0.522, 0.4, 0.1, 0.08),  # arbitrary
# ])
# def test_determine_nitrogen_shape_parameters(half_heat, mat_heat, emerge, half, near, mature):
#     incorp = init_incorp(half_mature_heat_fraction=half_heat, mature_heat_fraction=mat_heat,
#                          emergence_nitrogen_fraction=emerge, half_mature_nitrogen_fraction=half,
#                          near_mature_nitrogen_fraction=near, mature_nitrogen_fraction=mature)
#     incorp.determine_nitrogen_shape_parameters()
#     assert incorp.shapes_nitrogen_uptake == NitrogenIncorporation.determine_nitrogen_shape_parameters(half_heat,
#                                                                                                       mat_heat,
#                                                                                                       emerge, half,
#                                                                                                       near, mature)

# TODO: will be incorporated into incorporate_nitrogen() integration test
# @pytest.mark.parametrize("heatfrac,emerge,mature,s1,s2", [
#     (0.6, 0.8, 0.25, 1, 1),  # start
#     (0.6, 0.8, 0.25, 0.5, 1),  # reduced s1
#     (0.6, 0.8, 0.25, 1, 0.2),  # reduced s2
#     (0.6, 0.8, 0.25, 0.5, 0.2),  # both shapes reduced
#     (0.6, 0.6, 0.25, 1, 1),  # heatfrac = emergence nfrac
#     (0.6, 0.5, 0.25, 1, 1),  # heafrac < emergence nfrac
#     (0.6, 0.25, 0.25, 1, 1),  # emergence nfrac = mature
#     (0.6, 0.2, 0.25, 1, 1),  # emergence nfrac < mature
#     (0.512, 0.73, 0.59, 0.83, 0.33)  # arbitrary
# ])
# def test_determine_optimal_nitrogen_fraction(heatfrac, emerge, mature, s1, s2):
#     """test that nitrogen fraction is properly updated by determine_optimal_nitrogen_fraction()"""
#     incorp = init_incorp(heat_fraction=heatfrac, emergence_nitrogen_fraction=emerge,
#                          mature_nitrogen_fraction=mature, shapes_nitrogen_uptake=[s1, s2])
#     incorp.determine_optimal_nitrogen_fraction()
#     assert incorp.optimal_nitrogen_fraction == calc_optimal_nitrogen_fraction(heatfrac, emerge, mature, s1, s2)

# TODO: will be incorporated into incorporate_nitrogen() integration test
# @pytest.mark.parametrize("nfrac, biomass", [
#     (1, 1),  # all 1
#     (1, 0),  # no biomass
#     (0, 1),  # no nitrogen
#     (0, 0),  # neither
#     (.18, 1192.112),  # arbitrary
#     (.83, 526.7),  # arbitrary
# ])
# def test_determine_optimal_nitrogen(nfrac, biomass):
#     """test that a plant's optimal nitrogen is correctly updated by update_optimal_nitrogen()"""
#     incorp = init_incorp(biomass=biomass, optimal_nitrogen_fraction=nfrac)
#     incorp.determine_optimal_nitrogen()
#     assert incorp.optimal_nitrogen == calc_mass_from_fraction(nfrac, biomass)

# TODO: will be incorporated into incorporate_nitrogen() integration test
# @pytest.mark.parametrize("opt_n,prev_n,mat_nfrac,grow_max", [
#     (1, 1, 1, 1),  # all 1
#     (0, 1, 1, 1),  # optimal N = 0
#     (1, 0, 1, 1),  # previous N = 0
#     (1, 1, 0, 1),  # mature N fraction = 0
#     (1, 1, 1, 0),  # maximum growth = 0
#     (0, 0, 0, 0),  # all 0
#     (189.4, 105.01, 0.355, 233.59),  # arbitrary (first route) min(84, 331)
#     (189.4, 105.01, 0.355, 23.359),  # arbitrary (second route) min(84, 33.1)
#     (189.4, 189.4, 0.355, 23.359),  # opt_n = prev_n
# ])
# def test_determine_potential_nitrogen_uptake(opt_n, prev_n, mat_nfrac, grow_max):
#     """check that potential nitrogen uptake is correctly updated for a plant by update_max_nitrogen_uptake()"""
#     incorp = init_incorp(optimal_nitrogen=opt_n, previous_nitrogen=prev_n,
#                          mature_nitrogen_fraction=mat_nfrac, biomass_growth_max=grow_max)
#     incorp.determine_potential_nitrogen_uptake()
#     if opt_n - prev_n < 0:
#         expect = 0
#     else:
#         expect = calc_potential_nitrogen_uptake(opt_n, prev_n, mat_nfrac, grow_max)
#     assert incorp.potential_nitrogen_uptake == expect

# TODO: will be incorporated into uptake_nitrogen() integration test
# @pytest.mark.parametrize("bounds,desire,depth,ndistro", [
#     ([.25, .5, .75, 1], 100, 0.7, 1),  # start: roots in 3rd layer
#     ([.25, .5, .75, 1], 100, 0.4, 1),  # roots in 2nd layer
#     ([.25, .5, .75, 1], 100, 0.5, 1),  # roots at 2nd boundary
#     ([.25, .5, .75, 1], 100, 0.7, 0.4),  # reduced distro parameter
#     ([.25, .5, .75, 1], 80, 0.7, 1),  # reduced desire
#     ([1/3, 2/3, 1], 100, 0.7, 1),  # reduced layers
#     ([15.3, 16.9, 30.30, 102.0], 862.5, 22.4, 0.833),  # arbitrary
# ])
# def test_stratify_potential_nitrogen_uptake(bounds, desire, depth, ndistro):
#     incorp = init_incorp(potential_nitrogen_uptake=desire, root_depth=depth, nitrogen_distro_param=ndistro)
#     incorp.stratify_potential_nitrogen_uptake(bounds)
#     assert incorp.layer_nitrogen_potentials == calc_layer_nitrogen_uptake_potential(bounds, desire, depth, ndistro)

# TODO: will be incorporated into uptake_nitrogen() integration test
# @pytest.mark.parametrize("potentials, nitrates", [
#     ([0.8], [1]),  # start, 1 layer
#     ([1], [1]),  # potential = nitrates
#     ([1], [0]),  # no nitrate
#     ([0.8, 0.5, 0.2], [1, 0.5, 0.1]),  # differential availability
#     ([33.65, 20.2, 12], [22.0, 30.1, 7.9]),  # arbitrary
# ])
# def test_stratify_nitrogen_demand(potentials, nitrates):
#     incorp = init_incorp(layer_nitrogen_potentials=potentials)
#     incorp.stratify_unmet_nitrogen_demand(nitrates)
#     assert incorp.unmet_nitrogen_demands == calc_layer_nitrogen_demands(potentials, nitrates)


# TODO: will be incorporated into uptake_nitrogen() integration test
# @pytest.mark.parametrize("demands,potentials,nitrates", [
#     ([0.5, 0.5], [1, 1], [0.5, 0.3]),  # start
#     ([0.5, 1.2], [1, 1], [0.5, 0.3]),  # demand > potential
#     ([0.5, 0.5], [.8, 1], [0.5, 0.3]),  # reduced potential
#     ([0.5, 0.5], [1, 1], [2, 2]),  # abundant nitrates
#     ([0.5, 0.5], [1, 1], [0.1, 0.1]),  # scarce nitrates
#     ([75.3, 30.66, 12.9], [100, 50.5, 8.33], [80.5, 10.44, 12.7]),  # arbitrary
# ])
# def test_stratify_nitrogen_uptake_requests(demands, potentials, nitrates):
#     incorp = init_incorp(unmet_nitrogen_demands=demands, layer_nitrogen_potentials=potentials)
#     incorp.stratify_nitrogen_uptake_requests(nitrates)
#     assert incorp.nitrogen_requests == calc_layer_nitrogen_uptake(demands, potentials, nitrates)

# TODO: will be incorporated into uptake_nitrogen() integration test
# @pytest.mark.parametrize("requests,nitrates", [
#     ([1], [1]),  # start
#     ([1], [0]),  # no nitrates
#     ([0], [1]),  # no requests
#     ([0.5], [1]),  # requests < nitrates
#     ([1.2], [1]),  # requests > nitrates
#     ([37.9, 40.2, 18.3], [100.5, 83.3, 30.7]),  # arbitrary - abundant nitrates
#     ([87.36, 86.40, 30.33], [82.4, 83.0, 29.9]),  # nitrates limited
# ])
# def test_determine_actual_nitrogen_uptakes(requests, nitrates):
#     incorp = init_incorp(nitrogen_requests=requests)
#     incorp.determine_actual_nitrogen_uptake(nitrates)
#     expect = NitrogenIncorporation.determine_layer_extracted_resource(requests, nitrates)
#     assert incorp.actual_nitrogen_uptakes == expect

# TODO: will be incorporated into update_fixation_attributes() test
# @pytest.mark.parametrize("nitrates", [0, 0.5, 100, -1])
# def test_determine_nitrate_factor(nitrates):
#     """check that nitrate factor is set properly by determine_nitrate_factor"""
#     crop = init_incorp()
#     crop.determine_nitrate_factor(nitrates)
#     assert crop.nitrate_factor == calc_nitrate_factor(nitrates)

# TODO: will be incorporated into update_fixation_attributes() test
# @pytest.mark.parametrize("heatfrac", [0, 0.5, 1, -1])
# def test_determine_fixation_stage_factor(heatfrac):
#     """check that fixation stage factor is properly set by determine_fixation_stage_factor()"""
#     crop = init_incorp(heat_fraction=heatfrac)
#     crop.determine_fixation_stage_factor()
#     assert crop.fixation_stage_factor == calc_fixation_stage_factor(heatfrac)

# TODO: will be incorporated into incorporate_nitrogen() integration test
# @pytest.mark.parametrize("up,nitro,fix", [
#     (10, 0, 0),  # up, no start or fixed
#     (0, 0, 10),  # fixation, no start or up
#     (10, 0, 10),  # no start
#     (0, 10, 10),  # no up
#     (10, 10, 0),  # no fixation
#     (10, 10, 10),  # up + fixation
#     (26.7, 15.4, 3.39),  # arbirary
# ])
# def test_store_obtained_nitrogen(up, nitro, fix):
#     """check that nitrogen is properly stored in the plant with store_obtained_nitrogen()"""
#     crop = init_incorp(total_nitrogen_uptake=up, nitrogen=nitro, fixed_nitrogen=fix)
#     crop.store_obtained_nitrogen()
#     assert crop.nitrogen == calc_stored_nitrogen(up, nitro, fix)

# TODO: Integration tests needed
# def test_uptake_nitrogen():
#     """integration test for uptake_nitrogen()"""
#     raise Exception("need to write an integration test for uptake_nitrogen")
#
# def test_incorporate_nitrogen():
#     """integration test for incorporate_nitrogen()"""
#     raise Exception("need to write an integration test for incorporate_nitrogen")

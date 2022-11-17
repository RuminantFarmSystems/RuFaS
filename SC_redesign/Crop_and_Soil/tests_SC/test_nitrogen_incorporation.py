import pytest
from SC_redesign.Crop_and_Soil.crop.nitrogen_incorporation import *


# --- helper function tests ----
@pytest.mark.parametrize("heat_fraction,current,mature,emergence", [
    (1, .5, .25, .75),  # max heat_fraction
    (0.8, .5, .25, 1),  # max mature nfrac
    (0.32, .5, .25, .75),  # arbitrary
])
def test_calc_shape_log(heatfrac, current, mature, emergence):
    """check that calc_shape_log() calculates correct output"""
    observe = calc_shape_log(heatfrac, current, mature, emergence)
    bottom = 1 - ((current - mature) / (emergence - mature))
    inside = (heatfrac / bottom) - heatfrac
    expect = log(inside)
    assert observe == expect


@pytest.mark.parametrize("heat_fraction,current,mature,emergence", [
    (0, .5, .25, .75),  # no heat_fraction
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
def test_error_calc_shape_log(heatfrac, current, mature, emergence):
    """check that calc_shape_log() throws errors when appropriate"""
    with pytest.raises(Exception):
        calc_shape_log(heatfrac, current, mature, emergence)


@pytest.mark.parametrize("halfheat,heat_fraction,emerge,half,near,mature", [
    (0.8, 1, 0.9, 0.6, 0.3, 0.25),
    (0.8, 0.81, 0.9, 0.6, 0.3, 0.25),  # small difference in heat units
    (0.8, 1, 0.9, 0.6, 0.25000001, 0.25),  # small difference in nfrac_near and nfrac_3
    (0.633, 0.691, 0.530, 0.101, 0.057, 0.013),  # arbitrary
])
def test_calc_shape_parameters(halfheat, heatfrac, emerge, half, near, mature):
    """check that the shape parameters are correctly calculated by calc_nshapes()"""
    observe = calc_shape_parameters(halfheat, heatfrac, emerge, half, near, mature)
    expect_2 = (calc_shape_log(halfheat, half, mature, emerge) -
                calc_shape_log(heatfrac, near, mature, emerge)) / (heatfrac - halfheat)
    expect_1 = calc_shape_log(halfheat, half, mature, emerge) + (expect_2 * halfheat)
    assert observe == [expect_1, expect_2]


@pytest.mark.parametrize("heat_fraction,emerge,mature,shape1,shape2", [
    (0.2, 0.8, 0.5, 0.1, 0.5),  # shape1 < shape2
    (0.2, 0.8, 0.5, 0.5, 0.1),  # shape1 > shape2
    (0.2, 0.8, 0.5, -0.5, 0.1),  # negative shape 1
    (0.2, 0.8, 0.5, 0.5, -0.1),  # negative shape 2
    (0.2, 0.8, 0.5, -0.5, -0.1),  # both negative
    (0.789, 0.587, 0.501, 0.138, 0.920),  # arbitrary
])
def test_calc_nitrogen_fraction(heatfrac, emerge, mature, shape1, shape2):
    """ensure that nitrogen fraction is correctly calculated by calc_optimal_nitrogen_fraction()"""
    observe = calc_optimal_nitrogen_fraction(heatfrac, emerge, mature, shape1, shape2)
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
def test_calc_mass_from_fraction(nfrac, biomass):
    """test that optimal nitrogen is correctly calculated by calc_optimal_nitrogen()"""
    assert calc_mass_from_fraction(nfrac, biomass) == nfrac * biomass


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
def test_calc_potential_nitrogen_uptake(optimal, previous, mature, max_growth):
    """test that potential nitrogen uptake is correctly calculated by calc_max_nitrogen_uptake()"""
    expect = min(optimal - previous, 4 * mature * max_growth)
    observe = calc_potential_nitrogen_uptake(optimal, previous, mature, max_growth)
    assert expect == observe


@pytest.mark.parametrize("demand,depth,root_depth,nitrogen_distribution_parameter", [
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
def test_calc_nitrogen_uptake_to_depth(demand, depth, root_depth, ndistro):
    """check that nitrogen uptake is correctly calculated by calc_surface_nitrogen_uptake()"""
    observe = calc_nitrogen_uptake_to_depth(demand, depth, root_depth, ndistro)
    if root_depth <= 0:
        expect = 0
    else:
        expect = (demand / (1 - exp(-ndistro))) * (1 - exp(-ndistro * (depth / root_depth)))
    assert observe == expect


@pytest.mark.parametrize("demand,depth,root_depth,nitrogen_distribution_parameter", [
    (1, 1, 1, 0),  # no coefficient (error)
    (0, 0, 0, 0),  # all 0
    (0.3, 0.28, 0.11, 0)
])
def test_error_calc_nitrogen_uptake_to_depth(demand, depth, root_depth, ndistro):
    """"check that errors are appropriately thrown for calc_surface_nitrogen_uptake()"""
    with pytest.raises(Exception):
        calc_nitrogen_uptake_to_depth(demand, depth, root_depth, ndistro)


@pytest.mark.parametrize("bounds,demand,root_depth,nitrogen_distribution_parameter", [
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
def test_calc_layer_nitrogen_uptake_potential(bounds, demand, root_depth, ndistro):
    """
    ensure potential nitrogen uptake is calculated correctly for each soil layer with calc_layer_nitrogen_potential()
    """
    layer_nitrogen = []  # empty list to fill
    upper_nitrogen = 0  # nitrogen in the top boundary (soil surface) is 0
    for i in range(len(bounds)):
        lower_nitrogen = calc_nitrogen_uptake_to_depth(demand, bounds[i], root_depth, ndistro)
        layer_nitrogen.append(lower_nitrogen - upper_nitrogen)
        upper_nitrogen = lower_nitrogen
    expect = layer_nitrogen
    observe = calc_layer_nitrogen_uptake_potential(bounds, demand, root_depth, ndistro)
    assert expect == observe


@pytest.mark.parametrize("bounds,demand,root_depth,nitrogen_distribution_parameter", [
    ([1, 0], 1, 1, 1),
    ([1, .5, 3], 1, 1, 1),
    ([1, 2, 3, 2.9], 1, 1, 1),
    ([100, 100.1, 100.01], 1, 1, 1),
    ([0.5, 0.4, 0.3], 0.53, .9, 0.11),
    ([1, 2, 3, 3], 1, 1, 1),  # ascending with redundant layer
    ([1, 1, 1, 1], 1, 1, 1),  # redundant layers
    ([3, 2, 1, 1], 1, 1, 1),  # descending with redundant layer
])
def test_error_calc_layer_nitrogen_uptake_potential(bounds, demand, root_depth, ndistro):
    """check that calc_layer_nitrogen_potential throws an error when soil boundaries are not properly ordered"""
    with pytest.raises(Exception):
        calc_layer_nitrogen_uptake_potential(bounds, demand, root_depth, ndistro)


@pytest.mark.parametrize("pots,avails", [
    ([0.5, 0.25, 0.05], [0.3, 0.2, 0.01]),
    ([0.5, 0.25, 0.05], [0.6, 0.3, 0.06]),  # abundant nitrates
    ([0.5, 0.25, 0.05], [0, 0, 0]),  # no nitrates
    ([0.5, 0.25, 0.05, .01], [0.3, 0.2, 0.01, 0.01]),  # 4 layers
    ([0.5, 0.25, 0.05], [0.5, 0.25, 0.05]),  # exactly met demands
    ([112.3, 50.44, 17, 12.99], [50.33, 15.10, 8.05, 6.66]),  # arbitrary
])
def test_calc_layer_nitrogen_demands(pots, avails):
    """test that nitrogen demand is correctly calculated for each layer by calc_layer_nitrogen_demand()"""
    observe = calc_layer_nitrogen_demands(pots, avails)
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
def test_calc_layer_nitrogen_uptake(demand, potential, nitrate):
    """test that actual nitrogen uptake from each layer is properly calculated by calc_layer_nitrogen_uptake()"""
    observe = calc_layer_nitrogen_uptake(demand, potential, nitrate)
    expect = []
    for d, p, n in zip(demand, potential, nitrate):
        uptake = min(p + d, n)
        expect.append(uptake)
    assert observe == expect


@pytest.mark.parametrize("requested,available", [
    (0, 1),  # no request
    (0.5, 1),  # request < avaialble
    (1, 1),  # request = available
    (1.5, 1),  # request > available
    (85.93, 232.7)  # arbitrary
])
def test_calc_extracted_resource(requested, available):
    """ensure that extracted resource is correctly calculated by calc_extracted_resource()"""
    if available < 0:
        drawn = 0
    elif requested > available:
        drawn = available
    else:
        drawn = requested
    assert drawn == calc_extracted_resource(requested, available)


@pytest.mark.parametrize("reqs,srcs", [
    ([0, 0], [1, 1]),  # no requests
    ([0.5, 0], [1, 1]),  # request from first layer
    ([0, 0.5], [1, 1]),  # request from second layer
    ([0.5, 0.5], [1, 1]),  # request from both
    ([18.66, 33.74], [20.30, 19.93])  # arbitrary
])
def test_calc_layer_extracted_resource(reqs, srcs):
    """ensure that extracted nitrogen is correctly calculated for each layer"""
    draws = []
    for i in range(len(reqs)):
        draws.append(calc_extracted_resource(reqs[i], srcs[i]))
    assert draws == calc_layer_extracted_resource(reqs, srcs)


@pytest.mark.parametrize("prev,new,fix", [
    (1, 1, 1),  # all 1
    (1, 1, 0),  # no fixation
    (1, 0, 1),  # no new nitrogen
    (0, 1, 1),  # no previous nitrogen
    (0, 0, 0),  # all 0
    (50.39, 10.55, 3.05)  # arbitrary
])
def calc_stored_nitrogen(prev, new, fix):
    """test the stored nitrogen is properly calculated by calc_stored_nitrogen()"""
    observe = calc_stored_nitrogen(new, prev, fix)
    assert observe == prev + new + fix


@pytest.mark.parametrize("heat_fraction,expect", [
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
def test_calc_fixation_stage_factor(heatfrac, expect):
    assert calc_fixation_stage_factor(heatfrac) == expect


def test_calc_fixed_nitrogen(demand, stage, water, nitrate):
    assert False


def test_calc_nitrate_factor(nitrates):
    assert False

def test_calc_soil_water_factor(available, capacity):
    assert False


def test_calc_deepest_accessible_layer(depth, bounds):
    assert False

# ---- initialization functions (reusable) ----
def init_nu(**kwargs):
    """helper function to create GrowthConstraint instance, with specified attributes"""
    nu = NitrogenIncorporation()
    for key, val in kwargs.items():
        setattr(nu, key, val)
    return nu


def init_soil(**kwargs):
    """helper function to create GrowthConstraint instance, with specified attributes"""
    soil = Soil()
    for key, val in kwargs.items():
        setattr(soil, key, val)
    return soil

# ---- member function tests ----
@pytest.mark.parametrize("heat_fraction,emerge,mature,s1,s2", [
    (0.6, 0.8, 0.25, 1, 1),  # start
    (0.6, 0.8, 0.25, 0.5, 1),  # reduced s1
    (0.6, 0.8, 0.25, 1, 0.2),  # reduced s2
    (0.6, 0.8, 0.25, 0.5, 0.2),  # both shapes reduced
    (0.6, 0.6, 0.25, 1, 1),  # heat_fraction = emergence nfrac
    (0.6, 0.5, 0.25, 1, 1),  # heafrac < emergence nfrac
    (0.6, 0.25, 0.25, 1, 1),  # emergence nfrac = mature
    (0.6, 0.2, 0.25, 1, 1),  # emergence nfrac < mature
    (0.512, 0.73, 0.59, 0.83, 0.33)  # arbitrary
])
def test_determine_nitrogen_fraction(heatfrac, emerge, mature, s1, s2):
    """test that nitrogen fraction is properly updated by update_nitrogen_fraction()"""
    nu = init_nu(heat_fraction=heatfrac, emergence_nfrac=emerge, mature_nfrac=mature, shapes_nitrogen_uptake=[s1, s2])
    nu.determine_optimal_nitrogen_fraction()
    assert nu.optimal_nitrogen_fraction == calc_optimal_nitrogen_fraction(heatfrac, emerge, mature, s1, s2)


@pytest.mark.parametrize("half_heat,mat_heat,emerge,half,near,mature", [
    (0.5, 1.0, 0.8, 0.6, 0.3, 0.2),  # start
    (0.99, 1.0, 0.8, 0.6, 0.3, 0.2),  # half_heat close to mature heat
    (0.01, 1.0, 0.8, 0.6, 0.3, 0.2),  # small half_heat
    (0.5, 1.0, 0.8, 0.6, 0.20001, 0.2),  # near very close to mature
    (0.286, 0.54, 0.522, 0.4, 0.1, 0.08),  # arbitrary
])
def test_determine_nfrac_shape_parameters(half_heat, mat_heat, emerge, half, near, mature):
    nu = init_nu(half_mature_heatfrac=half_heat, mature_heatfrac=mat_heat, emergence_nfrac=emerge,
                 half_mature_nfrac=half, near_mature_nfrac=near, mature_nfrac=mature)
    nu.determine_nitrogen_shape_parameters()
    assert nu.shapes_nitrogen_uptake == calc_shape_parameters(half_heat, mat_heat, emerge, half, near, mature)


@pytest.mark.parametrize("nfrac, biomass", [
    (1, 1),  # all 1
    (1, 0),  # no biomass
    (0, 1),  # no nitrogen
    (0, 0),  # neither
    (.18, 1192.112),  # arbitrary
    (.83, 526.7),  # arbitrary
])
def test_determine_optimal_nitrogen(nfrac, biomass):
    """test that a plant's optimal nitrogen is correctly updated by update_optimal_nitrogen()"""
    nu = init_nu(biomass=biomass, optimal_nitrogen_fraction=nfrac)
    nu.determine_optimal_nitrogen()
    assert nu.optimal_nitrogen == calc_mass_from_fraction(nfrac, biomass)


# @pytest.mark.parametrize("nitrogen", [0, 0.2, 0.5, 1, 237.32])
# def test_shift_nitrogen_time(nitrogen):
#     nu = init_nu(nitrogen=nitrogen)
#     nu.shift_nitrogen_time()
#     assert nu.previous_nitrogen == nitrogen


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
def test_determine_potential_nitrogen_uptake(opt_n, prev_n, mat_nfrac, grow_max):
    """check that potential nitrogen uptake is correctly updated for a plant by update_max_nitrogen_uptake()"""
    nu = init_nu(optimal_nitrogen=opt_n, previous_nitrogen=prev_n, mature_nfrac=mat_nfrac, biomass_growth_max=grow_max)
    nu.determine_potential_nitrogen_uptake()
    if opt_n - prev_n < 0:
        expect = 0
    else:
        expect = calc_potential_nitrogen_uptake(opt_n, prev_n, mat_nfrac, grow_max)
    assert nu.potential_nitrogen_uptake == expect


@pytest.mark.parametrize("bounds,desire,depth,nitrogen_distribution_parameter", [
    ([.25, .5, .75, 1], 100, 0.7, 1),  # start: roots in 3rd layer
    ([.25, .5, .75, 1], 100, 0.4, 1),  # roots in 2nd layer
    ([.25, .5, .75, 1], 100, 0.5, 1),  # roots at 2nd boundary
    ([.25, .5, .75, 1], 100, 0.7, 0.4),  # reduced distro parameter
    ([.25, .5, .75, 1], 80, 0.7, 1),  # reduced desire
    ([1/3, 2/3, 1], 100, 0.7, 1),  # reduced layers
    ([15.3, 16.9, 30.30, 102.0], 862.5, 22.4, 0.833),  # arbitrary
])
def test_stratify_potential_nitrogen_uptake(bounds, desire, depth, ndistro):
    nu = init_nu(potential_nitrogen_uptake=desire, root_depth=depth, nitrogen_distro_param=ndistro)
    nu.stratify_potential_nitrogen_uptake(bounds)
    assert nu.layer_nitrogen_potentials == calc_layer_nitrogen_uptake_potential(bounds, desire, depth, ndistro)

@pytest.mark.parametrize("potentials, nitrates", [
    ([0.8], [1]),  # start, 1 layer
    ([1], [1]),  # potential = nitrates
    ([1], [0]),  # no nitrate
    ([0.8, 0.5, 0.2], [1, 0.5, 0.1]),  # differential availability
    ([33.65, 20.2, 12], [22.0, 30.1, 7.9]),  # arbitrary
])
def test_stratify_nitrogen_demand(potentials, nitrates):
    nu = init_nu(layer_nitrogen_potentials=potentials)
    nu.stratify_unmet_nitrogen_demand(nitrates)
    assert nu.unmet_nitrogen_demands == calc_layer_nitrogen_demands(potentials, nitrates)


@pytest.mark.parametrize("demands,potentials,nitrates", [
    ([0.5, 0.5], [1, 1], [0.5, 0.3]),  # start
    ([0.5, 1.2], [1, 1], [0.5, 0.3]),  # demand > potential
    ([0.5, 0.5], [.8, 1], [0.5, 0.3]),  # reduced potential
    ([0.5, 0.5], [1, 1], [2, 2]),  # abundant nitrates
    ([0.5, 0.5], [1, 1], [0.1, 0.1]),  # scarce nitrates
    ([75.3, 30.66, 12.9], [100, 50.5, 8.33], [80.5, 10.44, 12.7]),  # arbitrary
])
def test_stratify_nitrogen_uptake(demands, potentials, nitrates):
    nu = init_nu(layer_nitrogen_demands=demands, layer_nitrogen_potentials=potentials)
    nu.stratify_nitrogen_uptake_requests(nitrates)
    assert nu.nitrogen_requests == calc_layer_nitrogen_uptake(demands, potentials, nitrates)


@pytest.mark.parametrize("uptakes,nitrates", [
    ([1], [1]),  # start
    ([1], [0]),  # no nitrates
    ([0], [1]),  # no uptakes
    ([0.5], [1]),  # uptakes < nitrates
    ([1.2], [1]),  # uptakes > nitrates
    ([37.9, 40.2, 18.3], [100.5, 83.3, 30.7]),  # arbitrary - abundant nitrates
    ([87.36, 86.40, 30.33], [82.4, 83.0, 29.9]),  # nitrates limited
])
def test_reassess_nitrogen_availability(uptakes, nitrates):
    nu = init_nu(layer_nitrogen_uptakes=uptakes)
    nu.determine_actual_nitrogen_uptakes(nitrates)
    expect = calc_layer_extracted_resource(uptakes, nitrates)
    assert [nu.nitrogen_requests, nu.total_nitrogen_uptake] == [expect, sum(expect)]


@pytest.mark.parametrize("uptakes,nitrates", [
    ([1], [1]),  # start
    ([1], [0]),  # no nitrates
    ([0], [1]),  # no uptakes
    ([0.5], [1]),  # uptakes < nitrates
    ([1.2], [1]),  # uptakes > nitrates
    ([37.9, 40.2, 18.3], [100.5, 83.3, 30.7]),  # arbitrary - abundant nitrates
    ([87.36, 86.40, 30.33], [82.4, 83.0, 29.9]),  # nitrates limited
])
def test_extract_nitrogen_from_soil(uptakes, nitrates):
    nu = init_nu(layer_nitrogen_uptakes=uptakes, total_nitrogen_uptake=sum(uptakes), nitrogen=100)
    soil = init_soil(nitrates=nitrates)
    nu.extract_nitrogen_from_soil(soil)

    total_uptake = sum(uptakes)
    remaining = []
    for i in range(len(uptakes)):
        remaining.append(nitrates[i] - uptakes[i])

    assert soil.extracted_nitrates == nu.nitrogen_requests
    assert soil.total_extracted_nitrogen == nu.total_nitrogen_uptake == total_uptake
    assert soil.nitrates == remaining
    assert nu.nitrogen == 100 + total_uptake


def test_incorporate_nitrogen():
    assert False

def test_store_nitrogen_biomass():
    assert False

def test_uptake_nitrogen():
    assert False

def test_try_fixation():
    assert False

def test_fix_nitrogen(water, nitrate):
    assert False

def test_determine_deepest_accessible_soil_layer(depths):
    assert False

def test_access_layers(full):
    assert False


# ---- integration tests ----

## ---- OLD

#

#
#

#
#
# @pytest.mark.parametrize("uptake_potential,root_depth,nitrogen_distribution_parameter,layer_depths,total_accessible_nitrates", [
#     (1, 1, 0.5, [0.25, 0.5, 0.75, 1.0], [0.5, 0.25, 0.04, 0.01]),  # roots = max depth, even layers, unit sums
#     (1.5, 1, 0.5, [0.25, 0.5, 0.75, 1.0], [0.5, 0.25, 0.04, 0.01]),  # increased demand
#     (0.05, 1, 0.5, [0.25, 0.5, 0.75, 1.0], [0.5, 0.25, 0.04, 0.01]),  # decreased demand
#     (0, 1, 0.5, [0.25, 0.5, 0.75, 1.0], [0.5, 0.25, 0.04, 0.01]),  # no demand
#     (1, 1.5, 0.5, [0.25, 0.5, 0.75, 1.0], [0.5, 0.25, 0.04, 0.01]),  # increased root depth
#     (1, 0.5, 0.5, [0.25, 0.5, 0.75, 1.0], [0.5, 0.25, 0.04, 0.01]),  # decreased root depth
#     (1, 0, 0.5, [0.25, 0.5, 0.75, 1.0], [0.5, 0.25, 0.04, 0.01]),  # no roots
#     (1, 1, 1, [0.25, 0.5, 0.75, 1.0], [0.5, 0.25, 0.04, 0.01]),  # nitrogen_distribution_parameter = 1
#     (1, 1, -1, [0.25, 0.5, 0.75, 1.0], [0.5, 0.25, 0.04, 0.01]),  # nitrogen_distribution_parameter < 0
#     (1, 1, 0.5, [0.25, 0.5, 0.75, 1.0], [1, 0.75, 0.5, 0.25]),  # increased nitrates
#     (1, 1, 1, [0.25, 0.5, 0.75, 1.0], [0.25, 0.05, 0.01, 0.001]),  # decreased nitrates
#     (1, 1, 1, [0.25, 0.5, 0.75, 1.0], [0, 0, 0, 0]),  # no nitrates
#     (1, 1, 1, [0.25, 0.5, 0.75, 1.0, 1.2], [0.5, 0.25, 0.04, 0.01, 0.005]),  # extra soil layer
#     (332.33, 50.08, 0.298, [20.22, 31.85, 33.01, 40.12], [20, 5.51, 1.01, 10.01]),  # arbitrary
#     (1050, 85, 0.66, [37.1, 71.97, 90.33, 113.9], [309, 453.2, 1007.3, 500.22]),  # arbitrary 2
# ])
# def test_uptake_nitrogen(uptake_potential, root_depth, nitrogen_distribution_parameter, layer_depths, total_accessible_nitrates):
#     """integration test for the uptake_nitrogen() function, which updates class attributes with many functions"""
#     # observed
#     ms = mock_soil(soil_layers=[])
#     for depth, nitrate in zip(layer_depths, total_accessible_nitrates):
#         ml = mock_soil_layer(bottom_depth=depth, NO3=nitrate, N_uptake=0)
#         ms.soil_layers.append(ml)
#     mc = mock_crop(N_up=uptake_potential, z_root=root_depth, beta_n=nitrogen_distribution_parameter, N_act_up=0)
#     uptake_nitrogen(mc, ms)
#     observe_soil_uptakes = [layer.N_uptake for layer in ms.soil_layers]
#     observe_soil_nitrates = [layer.NO3 for layer in ms.soil_layers]
#     # expected
#     expect_potentials = calc_layer_nitrogen_potential(boundaries=layer_depths, demand=uptake_potential,
#                                                       root_depth=root_depth, nitrogen_distribution_parameter=nitrogen_distribution_parameter)
#     expect_demands = calc_layer_nitrogen_demand(uptake_potentials=expect_potentials,
#                                                 nitrate_availabilities=total_accessible_nitrates)
#     expect_uptakes = calc_layer_nitrogen_uptake(layer_demand=expect_demands, layer_potential=expect_potentials,
#                                                 layer_nitrate=total_accessible_nitrates)
#     expect_nitrates = [nitrate - uptake for nitrate, uptake in zip(total_accessible_nitrates, expect_uptakes)]
#     # collect results
#     observe = [mc.pot_N_up_each_layer, mc.act_N_up_each_layer, mc.N_act_up, observe_soil_uptakes, observe_soil_nitrates]
#     expect = [expect_potentials, expect_uptakes, sum(expect_uptakes), expect_uptakes, expect_nitrates]
#     # assertion
#     assert observe == expect
#
#
# @pytest.mark.parametrize("total_uptake,nitrogen_start,fixed", [
#     (1, 0, 0),  # uptake only
#     (0, 0, 1),  # fixation only
#     (1, 0, 1),  # uptake and fixation
#     (1, 1, 1),  # start with some N
#     (0, 0, 0),  # no change
#     (0, 1, 0),  # no change - start with some N
#     (23.59, 12.5, 1.033),  # arbitrary
#     (19.79, 22.08, 0.051),  # arbitrary
# ])
# def test_store_nitrogen(total_uptake, nitrogen_start, fixed):
#     """test that stored nitrogen is properly updated by store_nitrogen()"""
#     mc = mock_crop(N_act_up=total_uptake, bio_N=nitrogen_start, N_fix=fixed)
#     store_obtained_nitrogen(mc)
#     expect = calc_stored_nitrogen(uptake=total_uptake, previous=nitrogen_start, fixed=fixed)
#     assert mc.bio_N == expect
#
#
# # TODO: need to add more test cases for this integration test
# @pytest.mark.parametrize("hf,hf50,hf100,phf,"
#                          "nf1,nf2,nfn,nf3,"
#                          "bm,nmo,ns,mg,"
#                          "rd,nds,nfx,fix,"
#                          "sbs,sns,sw,scw", [
#                              (0.7, 0.5, 1.0, 0.75,  # case 1 (no fixation)
#                               0.8, 0.6, 0.3, 0.2,
#                               100, 10, 50, 20,
#                               1, 0.5, 0, False,
#                               [0.3, 0.6, 1], [0.2, 0.1, 0.01], [.9, .5, .8], [1, 1, 1]),
#                              (0.7, 0.5, 1.0, 0.75,  # case 1 (with fixation)
#                               0.8, 0.6, 0.3, 0.2,
#                               100, 10, 50, 20,
#                               1, 0.5, 0, True,
#                               [0.3, 0.6, 1], [0.2, 0.1, 0.01], [.9, .5, .8], [1, 1, 1]),
#                          ])
# def test_update_nitrogen(hf, hf50, hf100, phf, nf1, nf2, nfn, nf3, bm, nmo, ns, mg, rd, nds, nfx, fix,
#                          sbs, sns, sw, scw):
#     """integration test for update_nitrogen()"""
#     # observe
#     mc = mock_crop(fr_PHU_50=hf50, fr_PHU_100=hf100, fr_n1=nf1, fr_n2=nf2, fr_n3ish=nfn, fr_n3=nf3,
#                    prev_fr_PHU=phf, bio_N_opt=nmo, bio_N=ns, d_biomass_max=mg, z_root=rd, beta_n=nds,
#                    biomass_actual=bm, fr_PHU=hf, N_fix=nfx, is_nitrogen_fixer=fix)
#     ms = mock_soil(soil_layers=[])
#     for depth, nitrate, water, cap_water in zip(sbs, sns, sw, scw):
#         ml = mock_soil_layer(bottom_depth=depth, NO3=nitrate, N_uptake=0, soil_water=water, fc_water=cap_water)
#         ms.soil_layers.append(ml)
#     reallocate_nitrogen(mc, ms)
#     observe_layer_leftovers = [layer.NO3 for layer in ms.soil_layers]
#     observe_layer_uptakes = [layer.N_uptake for layer in ms.soil_layers]
#     # expect
#     # update_nitrogen_fraction()
#     nshapes = calc_shape_parameters(heatfrac_half=hf50, heatfrac_full=hf100, nfrac_1=nf1, nfrac_2=nf2, nfrac_near=nfn,
#                                     nfrac_3=nf3)
#     nfrac = calc_optimal_nitrogen_fraction(phu_frac=phf, nfrac_1=nf1, nfrac_3=nf3, shape1=nshapes[0], shape2=nshapes[1])
#     # update_optimal_nitrogen()
#     optimal_nitrogen = calc_optimal_nitrogen(nfrac=nfrac, biomass=bm)
#     # update_potential_nitrogen_uptake()
#     if optimal_nitrogen - ns < 0:
#         potential_uptake = 0
#     else:
#         potential_uptake = calc_potential_nitrogen_uptake(demand=optimal_nitrogen, nitrogen_start=ns, mature_nitrogen_fraction=nf3,
#                                                           max_growth=mg)
#         # uptake_nitrogen()
#     layer_potentials = calc_layer_nitrogen_potential(boundaries=sbs, demand=potential_uptake, root_depth=rd,
#                                                      nitrogen_distribution_parameter=nds)
#     layer_demands = calc_layer_nitrogen_demand(uptake_potentials=layer_potentials, nitrate_availabilities=sns)
#     layer_uptakes = calc_layer_nitrogen_uptake(layer_demand=layer_demands, layer_potential=layer_potentials,
#                                                layer_nitrate=sns)
#     layer_leftovers = [available - uptake for available, uptake in zip(sns, layer_uptakes)]
#     total_uptake = sum(layer_uptakes)
#     # fix_nitrogen()
#     if fix:
#         accessible_resources = get_accessible_soil_resources(ms, rd)
#         deepest_layer = accessible_resources["deepest layer"]
#         accessible_soil_layers = [layer for layer in ms.soil_layers[slice(deepest_layer)]]
#         demand = calc_N_demand(crop_type=mc, accessible_soil_layers=accessible_soil_layers)
#         growth_factor = calc_growth_stage_factor(heat_fraction=phf)
#         water_factor = calc_soil_water_factor(accessible_water=accessible_resources["water"],
#                                               at_capacity_water=accessible_resources["water capacity"])
#         nitrate_factor = calc_nitrate_factor(total_accessible_nitrates=accessible_resources["nitrates"])
#         nitrogen_fixed = calc_fixed_nitrogen(demand, growth_factor, water_factor, nitrate_factor)
#     else:
#         nitrogen_fixed = 0
#
#     # store_obtained_nitrogen()
#     nitrogen_biomass = calc_stored_nitrogen(uptake=total_uptake, previous=ns, fixed=nitrogen_fixed)
#
#     # make assertions (the full test fails on first failed assumption)
#     assert mc.fr_N == nfrac
#     assert mc.optimal_nitrogen == optimal_nitrogen
#     assert mc.N_up == potential_uptake
#     assert mc.pot_N_up_each_layer == layer_potentials
#     assert mc.act_N_up_each_layer == layer_uptakes
#     assert observe_layer_uptakes == layer_uptakes
#     assert observe_layer_leftovers == layer_leftovers
#     assert mc.N_act_up == total_uptake
#     assert mc.bio_N == nitrogen_biomass
#     if fix:
#         assert mc.N_fix == nitrogen_fixed

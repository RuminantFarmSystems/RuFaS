"""
RUFAS: Ruminant Farm Systems Model
File name: test_nitrogen_uptake.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

import pytest
from RUFAS.routines.field.crop.nitrogen_uptake import *
from tests.tests_SoilCrop.mock_classes import mock_crop, mock_soil, mock_soil_layer


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
def test_calc_optimal_nitrogen(nf, bm):
    """test that optimal nitrogen is correctly calculated by calc_optimal_nitrogen()"""
    assert calc_optimal_nitrogen(nf, bm) == nf*bm


@pytest.mark.parametrize("nstart,nf,bm", [
    (0, 1, 1),  # no starting N
    (0.5, 1, 1),  # some N
    (1, 1, 1),  # N=1
    (237.3, .18, 1192.112)  # arbitrary
])
def test_update_optimal_nitrogen(nstart, nf, bm):
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
def test_calc_potential_nitrogen_uptake(opt, prev, mat, growth):
    """test that potential nitrogen uptake is correctly calculated by calc_max_nitrogen_uptake()"""
    expect = min(opt - prev, 4*mat*growth)
    observe = calc_potential_nitrogen_uptake(demand=opt, nitrogen_start=prev, mature_nfrac=mat, max_growth=growth)
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
def test_update_potential_nitrogen_uptake(opt_n, prev_n, mat_nfrac, grow_max):
    """check that potential nitrogen uptake is correctly updated for a plant by update_max_nitrogen_uptake()"""
    mc = mock_crop(bio_N_opt=opt_n, prev_bio_N=prev_n, fr_n3=mat_nfrac, d_biomass_max=grow_max, N_up=0)
    update_potential_nitrogen_uptake(mc)
    if opt_n - prev_n < 0:
        expect = 0
    else:
        expect = calc_potential_nitrogen_uptake(opt_n, prev_n, mat_nfrac, grow_max)
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
def test_nitrogen_uptake_to_depth(d, z, r, b):
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
def test_error_nitrogen_uptake_to_depth(d, z, r, b):
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

@pytest.mark.parametrize("bounds,d,r,b", [
    ([1, 0], 1, 1, 1),
    ([1, .5, 3], 1, 1, 1),
    ([1, 2, 3, 2.9], 1, 1, 1),
    ([100, 100.1, 100.01], 1, 1, 1),
    ([0.5, 0.4, 0.3], 0.53, .9, 0.11),
    ([1, 2, 3, 3], 1, 1, 1),  # ascending with redundant layer
    ([1, 1, 1, 1], 1, 1, 1),  # redundant layers
    ([3, 2, 1, 1], 1, 1, 1),  # descending with redundant layer
])
def test_error_calc_layer_nitrogen_potential(bounds, d, r, b):
    """check that calc_layer_nitrogen_potential throws an error when soil boundaries are not properly ordered"""
    with pytest.raises(Exception):
        calc_layer_nitrogen_potential(bounds, d, r, b)

@pytest.mark.parametrize("pots,avails", [
    ([0.5, 0.25, 0.05], [0.3, 0.2, 0.01]),
    ([0.5, 0.25, 0.05], [0.6, 0.3, 0.06]),  # abundant nitrates
    ([0.5, 0.25, 0.05], [0, 0, 0]),  # no nitrates
    ([0.5, 0.25, 0.05, .01], [0.3, 0.2, 0.01, 0.01]),  # 4 layers
    ([0.5, 0.25, 0.05], [0.5, 0.25, 0.05]),  # exactly met demands
    ([112.3, 50.44, 17, 12.99], [50.33, 15.10, 8.05, 6.66]),  # arbitrary
])
def test_calc_layer_nitrogen_demand(pots, avails):
    """test that nitrogen demand is correctly calculated for each layer by calc_layer_nitrogen_demand()"""
    observe = calc_layer_nitrogen_demand(uptake_potentials=pots, nitrate_availabilities=avails)

    # # test structure adapted from old version of code
    # # TODO: this test code (and therefore, the old function code) gives something other than expected
    # #   I need to triple-check this with the pseudocode.
    # cumulative_uptake_potential = 0
    # cumulative_nitrates = 0
    # nitrogen_demand = 0  # a layer's demand starts at 0
    # layer_demand = []
    # actual_uptake = []
    # for potential, available in zip(pots, avails):
    #     nitrogen_uptake = min((potential + nitrogen_demand), available)
    #     actual_uptake.append(nitrogen_uptake)
    #     cumulative_uptake_potential += potential
    #     cumulative_nitrates += available
    #     demand = max(cumulative_uptake_potential - cumulative_nitrates, 0)
    #     layer_demand.append(demand)
    #     nitrogen_demand = demand
    # expect = layer_demand
    # assert expect == observe

    # new version (based on my interpretation of psuedocode) - this version works
    # starting values
    no3_sum = 0
    up_sum = 0
    demand_list = []
    for pot_up, no3 in zip(pots, avails):  # loop over layers
        # demand = previous up_sum - previous no3_sum:
        demand = up_sum - no3_sum  # difference between potential and available
        demand = max(demand, 0) # constrain to zero
        demand_list.append(demand)

        # add to totals for next loop
        up_sum += pot_up
        no3_sum += no3
    assert demand_list == pytest.approx(observe, rel=0.00001)
    raise Exception("This function is the likely culprit for significantly reduced yields... (no, it's something else)")

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
    observe = calc_layer_nitrogen_uptake(layer_demand=demand, layer_potential=potential, layer_nitrate=nitrate)
    expect = []
    for d, p, n in zip(demand, potential, nitrate):
        uptake = min(p + d, n)
        expect.append(uptake)
    assert observe == expect

@pytest.mark.parametrize("prev,new,fix", [
    (1, 1, 1),  # all 1
    (1, 1, 0),  # no fixation
    (1, 0, 1),  # no new nitrogen
    (0, 1, 1),  # no previous nitrogen
    (0, 0, 0),  # all 0
    (50.39, 10.55, 3.05)  # arbitrary
])
def calc_stored_nitogen(prev, new, fix):
    """test the stored nitrogen is properly calculated by calc_stored_nitrogen()"""
    observe = calc_stored_nitrogen(uptake=new, previous=prev, fixed=fix)
    assert observe == prev + new + fix

@pytest.mark.parametrize("uptake_potential,root_depth,ndistro,layer_depths,layer_nitrates", [
    (1, 1, 0.5, [0.25, 0.5, 0.75, 1.0], [0.5, 0.25, 0.04, 0.01]),  # roots = max depth, even layers, unit sums
    (1.5, 1, 0.5, [0.25, 0.5, 0.75, 1.0], [0.5, 0.25, 0.04, 0.01]),  # increased demand
    (0.05, 1, 0.5, [0.25, 0.5, 0.75, 1.0], [0.5, 0.25, 0.04, 0.01]),  # decreased demand
    (0, 1, 0.5, [0.25, 0.5, 0.75, 1.0], [0.5, 0.25, 0.04, 0.01]),  # no demand
    (1, 1.5, 0.5, [0.25, 0.5, 0.75, 1.0], [0.5, 0.25, 0.04, 0.01]),  # increased root depth
    (1, 0.5, 0.5, [0.25, 0.5, 0.75, 1.0], [0.5, 0.25, 0.04, 0.01]),  # decreased root depth
    (1, 0, 0.5, [0.25, 0.5, 0.75, 1.0], [0.5, 0.25, 0.04, 0.01]),  # no roots
    (1, 1, 1, [0.25, 0.5, 0.75, 1.0], [0.5, 0.25, 0.04, 0.01]),  # ndistro = 1
    (1, 1, -1, [0.25, 0.5, 0.75, 1.0], [0.5, 0.25, 0.04, 0.01]),  # ndistro < 0
    (1, 1, 0.5, [0.25, 0.5, 0.75, 1.0], [1, 0.75, 0.5, 0.25]),  # increased nitrates
    (1, 1, 1, [0.25, 0.5, 0.75, 1.0], [0.25, 0.05, 0.01, 0.001]),  # decreased nitrates
    (1, 1, 1, [0.25, 0.5, 0.75, 1.0], [0, 0, 0, 0]),  # no nitrates
    (1, 1, 1, [0.25, 0.5, 0.75, 1.0, 1.2], [0.5, 0.25, 0.04, 0.01, 0.005]),  # extra soil layer
    (332.33, 50.08, 0.298, [20.22, 31.85, 33.01, 40.12], [20, 5.51, 1.01, 10.01]),  # arbitrary
    (1050, 85, 0.66, [37.1, 71.97, 90.33, 113.9], [309, 453.2, 1007.3, 500.22]),  # arbitrary 2
])
def test_uptake_nitrogen(uptake_potential, root_depth, ndistro, layer_depths, layer_nitrates):
    """integration test for the uptake_nitrogen() function, which updates class attributes with many functions"""
    # observed
    ms = mock_soil(soil_layers=[])
    for depth, nitrate in zip(layer_depths, layer_nitrates):
        ml = mock_soil_layer(bottom_depth=depth, NO3=nitrate, N_uptake=0)
        ms.soil_layers.append(ml)
    mc = mock_crop(N_up=uptake_potential, z_root=root_depth, beta_n=ndistro, N_act_up=0)
    uptake_nitrogen(mc, ms)
    observe_soil_uptakes = [layer.N_uptake for layer in ms.soil_layers]
    observe_soil_nitrates = [layer.NO3 for layer in ms.soil_layers]
    # expected
    expect_potentials = calc_layer_nitrogen_potential(boundaries=layer_depths, demand=uptake_potential,
                                                      root_depth=root_depth, ndistro=ndistro)
    expect_demands = calc_layer_nitrogen_demand(uptake_potentials=expect_potentials,
                                                nitrate_availabilities=layer_nitrates)
    expect_uptakes = calc_layer_nitrogen_uptake(layer_demand=expect_demands, layer_potential=expect_potentials,
                                                layer_nitrate=layer_nitrates)
    expect_nitrates = [nitrate - uptake for nitrate, uptake in zip(layer_nitrates, expect_uptakes)]
    # collect results
    observe = [mc.pot_N_up_each_layer, mc.act_N_up_each_layer, mc.N_act_up, observe_soil_uptakes, observe_soil_nitrates]
    expect = [expect_potentials, expect_uptakes, sum(expect_uptakes), expect_uptakes, expect_nitrates]
    # assertion
    assert observe == expect

@pytest.mark.parametrize("total_uptake,nitrogen_start,fixed", [
    (1, 0, 0),  # uptake only
    (0, 0, 1),  # fixation only
    (1, 0, 1),  # uptake and fixation
    (1, 1, 1),  # start with some N
    (0, 0, 0),  # no change
    (0, 1, 0),  # no change - start with some N
    (23.59, 12.5, 1.033),  # arbitrary
    (19.79, 22.08, 0.051),  # arbitrary
])
def test_update_stored_nitrogen(total_uptake, nitrogen_start, fixed):
    """test that stored nitrogen is properly updated by update_stored_nitrogen()"""
    mc = mock_crop(N_act_up=total_uptake, bio_N=nitrogen_start, N_fix=fixed)
    update_stored_nitrogen(mc)
    expect = calc_stored_nitrogen(uptake=total_uptake, previous=nitrogen_start, fixed=fixed)
    assert mc.bio_N == expect

def test_fix_nitrogen():
    motivational_message = "fix_nitrogen() needs to be changed once nitrogen_fixation.py" +\
                           "(calc_N_fixation()) has been refactored and tested - Clay"
    raise Exception(motivational_message)


def test_update_nitrogen():
    raise Exception("I still need to write an integration test for update_nitrogen() - Clay")
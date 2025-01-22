from math import log, exp

import pytest
from pytest_mock import MockerFixture

from RUFAS.output_manager import OutputManager
from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.crop.nutrient_uptake import NutrientUptake


@pytest.mark.parametrize(
    "halfheat,heatfrac,emerge,half,near,mature,should_fail",
    [
        (0.5, 1.0, 0.8, 0.6, 0.3, 0.2, False),  # start
        (0.99, 1.0, 0.8, 0.6, 0.3, 0.2, False),  # half_heat close to mature heat
        (0.01, 1.0, 0.8, 0.6, 0.3, 0.2, False),  # small half_heat
        (0.5, 1.0, 0.8, 0.6, 0.20001, 0.2, False),  # near very close to mature
        (0.286, 0.54, 0.522, 0.4, 0.1, 0.08, False),  # arbitrary
        (0.8, 1, 0.9, 0.6, 0.3, 0.25, False),
        (0.8, 0.81, 0.9, 0.6, 0.3, 0.25, False),  # small difference in heat units
        (
            0.8,
            1,
            0.9,
            0.6,
            0.25000001,
            0.25,
            False,
        ),  # small difference in nfrac_near and nfrac_3
        (0.633, 0.691, 0.530, 0.101, 0.057, 0.013, False),  # arbitrary
        (0.5, 0.5, 0.530, 0.101, 0.057, 0.013, True),
    ],
)
def test_determine_nutrient_shape_parameters(
    halfheat: float,
    heatfrac: float,
    emerge: float,
    half: float,
    near: float,
    mature: float,
    should_fail: bool,
    mocker: MockerFixture,
) -> None:
    """Check that the shape parameters are correctly calculated by determine_nshapes() and that errors were raised
    correctly."""
    om = OutputManager()
    mock_add = mocker.patch.object(om, "add_error")
    if should_fail:
        try:
            NutrientUptake.determine_nutrient_shape_parameters(halfheat, heatfrac, emerge, half, mature)
        except ValueError as e:
            assert str(e) == "half_mature_heat_fraction must not equal mature_heat_fraction"
            mock_add.assert_called_once()
    else:
        expected_near = mature + 0.00001
        observe = NutrientUptake.determine_nutrient_shape_parameters(halfheat, heatfrac, emerge, half, mature)
        expect_2 = (
            NutrientUptake._determine_shape_log(halfheat, half, mature, emerge)
            - NutrientUptake._determine_shape_log(heatfrac, expected_near, mature, emerge)
        ) / (heatfrac - halfheat)
        expect_1 = NutrientUptake._determine_shape_log(halfheat, half, mature, emerge) + (expect_2 * halfheat)
        assert observe == [expect_1, expect_2]


@pytest.mark.parametrize(
    "heatfrac,current,mature,emergence",
    [
        (1, 0.5, 0.25, 0.75),  # max_evapotranspiration heatfrac
        (0.8, 0.5, 0.25, 1),  # max_evapotranspiration mature nfrac
        (0.32, 0.5, 0.25, 0.75),  # arbitrary
    ],
)
def test_determine_shape_log(heatfrac: float, current: float, mature: float, emergence: float) -> None:
    """Check that determine_shape_log() calculates correct output."""
    observe = NutrientUptake._determine_shape_log(heatfrac, current, mature, emergence)
    bottom = 1 - ((current - mature) / (emergence - mature))
    inside = (heatfrac / bottom) - heatfrac
    expect = log(inside)
    assert observe == expect


@pytest.mark.parametrize(
    "heatfrac,current,mature,emergence",
    [
        (0, 0.5, 0.25, 0.75),  # no heatfrac
        (0.8, 0, 0.25, 0.75),  # mature nfrac = 0
        (0.8, 0.76, 0.25, 0.75),  # nfrac > emergence
        (0.8, 0.75, 0.25, 0.75),  # nfrac = emergence
        (0.8, 0.5, 0.25, 0.24),  # emergence < mature
        (0.8, 1.2, 0.25, 0.25),  # out of bounds
        (0.8, 1.2, -0.25, 0.25),  # out of bounds
        (0.6, 0.3, 0.31, 0.8),  # log(-y): nfrac < mature
        (0.6, 0.3, 0.3, 0.8),  # nfrac = mature
        (0.8, 0.3, 0.31, 0.8),  # log(-y)
        (1, 0.3, 0.31, 0.8),  # log(-y)
    ],
)
def test_error_determine_shape_log(
    heatfrac: float, current: float, mature: float, emergence: float, mocker: MockerFixture
) -> None:
    """Check that determine_shape_log() throws errors when appropriate."""
    om = OutputManager()
    mock_add = mocker.patch.object(om, "add_error")
    with pytest.raises(Exception):
        NutrientUptake._determine_shape_log(heatfrac, current, mature, emergence)
    mock_add.assert_called_once()


@pytest.mark.parametrize(
    "heatfrac,emerge,mature,shape1,shape2",
    [
        (0.2, 0.8, 0.5, 0.1, 0.5),  # shape1 < shape2
        (0.2, 0.8, 0.5, 0.5, 0.1),  # shape1 > shape2
        (0.2, 0.8, 0.5, -0.5, 0.1),  # negative shape 1
        (0.2, 0.8, 0.5, 0.5, -0.1),  # negative shape 2
        (0.2, 0.8, 0.5, -0.5, -0.1),  # both negative
        (0.789, 0.587, 0.501, 0.138, 0.920),  # arbitrary
    ],
)
def test_determine_optimal_nutrient_fraction(
    heatfrac: float, emerge: float, mature: float, shape1: float, shape2: float
) -> None:
    """Ensure that nutrient fraction is correctly calculated by determine_optimal_nutrient_fraction()."""
    observe = NutrientUptake.determine_optimal_nutrient_fraction(heatfrac, emerge, mature, shape1, shape2)
    expect = (emerge - mature) * (1 - (heatfrac / (heatfrac + exp(shape1 - shape2 * heatfrac)))) + mature
    assert observe == expect


@pytest.mark.parametrize("nfrac,biomass", [(1, 1), (1, 0), (0, 1), (0, 0), (0.25, 0.3), (0.10, 0.257)])
def test_determine_optimal_nutrient(nfrac: float, biomass: float) -> None:
    """Test that optimal nutrient is correctly calculated by determine_optimal_nutrient()."""
    assert NutrientUptake.determine_optimal_nutrient(nfrac, biomass) == nfrac * biomass


@pytest.mark.parametrize(
    "optimal,previous,mature,max_growth",
    [
        (1, 1, 1, 1),  # all 1
        (0, 1, 1, 1),  # optimal N = 0
        (1, 0, 1, 1),  # previous N = 0
        (1, 1, 0, 1),  # mature N fraction = 0
        (1, 1, 1, 0),  # maximum growth = 0
        (0, 0, 0, 0),  # all 0
        (189.4, 105.01, 0.355, 233.59),  # arbitrary (first route) min(84, 331)
        (189.4, 105.01, 0.355, 23.359),  # arbitrary (second route) min(84, 33.1)
    ],
)
def test_determine_potential_nutrient_uptake(optimal: float, previous: float, mature: float, max_growth: float) -> None:
    """Test that potential nutrient uptake is correctly calculated by determine_potential_nutrient_uptake()."""
    expect = min(optimal - previous, 4 * mature * max_growth)
    observe = NutrientUptake.determine_potential_nutrient_uptake(optimal, previous, mature, max_growth)
    assert expect == observe


@pytest.mark.parametrize(
    "root,depths,expect",
    [
        (1.5, [0, 1, 2, 3], 3),  # roots access layer 3
        (2.7, [0, 1, 2, 3], 4),  # 4th layer
        (3.8, [0, 1, 2, 3], 4),  # beyond max_evapotranspiration depth
        (83.33, [10.4, 18.20, 63.7, 100, 1937.8], 4),  # arbitrary
    ],
)
def test_determine_deepest_accessible_layer(root: float, depths: list[float], expect: float) -> None:
    """Test that the deepest soil layer that is accessible to roots
    is correctly calculated by _determine_deepest_accessible_layer()."""
    assert NutrientUptake._determine_deepest_accessible_layer(root, depths) == expect


@pytest.mark.parametrize("root,depths", [(-1, [0, 1, 2, 3])])  # root < 0
def test_error_determine_deepest_accessible_layer(root: float, depths: list[float], mocker: MockerFixture) -> None:
    """Check that the errors were raised for specific cases."""
    om = OutputManager()
    mock_add = mocker.patch.object(om, "add_error")
    with pytest.raises(ValueError):
        NutrientUptake._determine_deepest_accessible_layer(root, depths)
    mock_add.assert_called_once()


@pytest.mark.parametrize(
    "bounds,demand,root_depth,ndistro",
    [
        ([0.25, 0.50, 0.75, 1.00], 1, 1, 1),  # four layers
        ([0.25, 0.50, 0.75, 1.00], 0.5, 1, 1),  # reduced demand
        ([0.25, 0.50, 0.75, 1.00], 1, 0.5, 1),  # reduced root depth
        ([0.25, 0.50, 0.75, 1.00], 1, 1.5, 1),  # increased root depth
        ([0.25, 0.50, 0.75, 1.00], 1, 1, 0.5),  # reduced distribution
        ([0.2, 0.40, 0.6, 0.8, 1.0], 1, 1, 1),  # five layers
        ([1 / 3, 2 / 3, 1], 1, 1, 1),  # three layers
        (
            [0.991, 3.7, 3.89, 12.01, 15],
            338.97,
            12.88,
            0.395,
        ),  # arbitrary (roots in 5th)
        (
            [0.991, 3.7, 3.89, 12.01, 15],
            338.97,
            4.33,
            0.395,
        ),  # arbitrary (roots in 4th)
        (
            [0.991, 3.7, 3.89, 12.01, 15],
            338.97,
            1.25,
            0.395,
        ),  # arbitrary (roots in 2nd)
    ],
)
def test_determine_layer_nutrient_uptake_potential(
    bounds: list[float], demand: float, root_depth: float, ndistro: float
) -> None:
    """
    Ensure potential nutrient uptake is calculated correctly for each soil layer with
    determine_layer_nutrient_potential().
    """
    layer_nitrogen = []  # empty list to fill
    upper_nitrogen = 0  # nitrogen in the top boundary (soil surface) is 0
    for i in range(len(bounds)):
        lower_nitrogen = NutrientUptake._determine_nutrient_uptake_to_depth(demand, bounds[i], root_depth, ndistro)
        layer_nitrogen.append(lower_nitrogen - upper_nitrogen)
        upper_nitrogen = lower_nitrogen
    expect = layer_nitrogen
    observe = NutrientUptake.determine_layer_nutrient_uptake_potential(bounds, demand, root_depth, ndistro)
    assert expect == observe


@pytest.mark.parametrize(
    "bounds,demand,root_depth,ndistro",
    [
        ([1, 0], 1, 1, 1),
        ([1, 0.5, 3], 1, 1, 1),
        ([1, 2, 3, 2.9], 1, 1, 1),
        ([100, 100.1, 100.01], 1, 1, 1),
        ([0.5, 0.4, 0.3], 0.53, 0.9, 0.11),
        ([1, 2, 3, 3], 1, 1, 1),  # ascending with redundant layer
        ([1, 1, 1, 1], 1, 1, 1),  # redundant layers
        ([3, 2, 1, 1], 1, 1, 1),  # descending with redundant layer
    ],
)
def test_error_determine_layer_nutrient_uptake_potential(
    bounds: list[float], demand: float, root_depth: float, ndistro: float, mocker: MockerFixture
) -> None:
    """Check that determine_layer_nutrient_potential throws an error when soil boundaries are not properly ordered."""
    om = OutputManager()
    mock_add = mocker.patch.object(om, "add_error")
    with pytest.raises(Exception):
        NutrientUptake.determine_layer_nutrient_uptake_potential(bounds, demand, root_depth, ndistro)
    mock_add.assert_called_once()


@pytest.mark.parametrize(
    "demand,depth,root_depth,ndistro",
    [
        (1, 1, 1, 1),  # all 1
        (0, 1, 1, 1),  # no demand
        (1, 0, 1, 1),  # surface only
        (1, 1, 0, 1),  # no root depth
        (1, 1, 1, -1),  # negative distribution coefficient
        (98.63, 20.2, 32.28, 0.38),  # arbitrary
        (98.63, 20.2, 32.28, 1.21),  # coefficient > 1
        (98.63, 20.2, 32.28, -0.38),  # coefficient < 0
        (98.63, 20.2, 12.28, 0.38),  # depth > root depth
    ],
)
def test_determine_nutrient_uptake_to_depth(demand: float, depth: float, root_depth: float, ndistro: float) -> None:
    """Check that nutrient uptake is correctly calculated by determine_surface_nutrient_uptake()."""
    observe = NutrientUptake._determine_nutrient_uptake_to_depth(demand, depth, root_depth, ndistro)
    if root_depth <= 0:
        expect = 0
    else:
        expect = (demand / (1 - exp(-ndistro))) * (1 - exp(-ndistro * (depth / root_depth)))
    assert observe == expect


@pytest.mark.parametrize(
    "demand,depth,root_depth,ndistro",
    [
        (1, 1, 1, 0),  # no coefficient (error)
        (0, 0, 0, 0),  # all 0
        (0.3, 0.28, 0.11, 0),
    ],
)
def test_error_determine_nutrient_uptake_to_depth(
    demand: float, depth: float, root_depth: float, ndistro: float, mocker: MockerFixture
) -> None:
    """Check that errors are appropriately thrown for determine_surface_nitrogen_uptake()."""
    om = OutputManager()
    mock_add = mocker.patch.object(om, "add_error")
    with pytest.raises(Exception):
        NutrientUptake._determine_nutrient_uptake_to_depth(demand, depth, root_depth, ndistro)
    mock_add.assert_called_once()


@pytest.mark.parametrize(
    "pots,avails",
    [
        ([0.5, 0.25, 0.05], [0.3, 0.2, 0.01]),
        ([0.5, 0.25, 0.05], [0.6, 0.3, 0.06]),  # abundant nitrates
        ([0.5, 0.25, 0.05], [0, 0, 0]),  # no nitrates
        ([0.5, 0.25, 0.05, 0.01], [0.3, 0.2, 0.01, 0.01]),  # 4 layers
        ([0.5, 0.25, 0.05], [0.5, 0.25, 0.05]),  # exactly met demands
        ([112.3, 50.44, 17, 12.99], [50.33, 15.10, 8.05, 6.66]),  # arbitrary
    ],
)
def test_determine_layer_nutrient_demands(pots: list[float], avails: list[float]) -> None:
    """Test that nutrient demand is correctly calculated for each layer by determine_layer_nitrogen_demand()."""
    observe = NutrientUptake.determine_layer_nutrient_demands(pots, avails)
    no3_sum = 0
    up_sum = 0
    demand_list = []
    for pot_up, no3 in zip(pots, avails):
        demand = up_sum - no3_sum
        demand = max(demand, 0)
        demand_list.append(demand)
        up_sum += pot_up
        no3_sum += no3
    assert demand_list == pytest.approx(observe, rel=0.00001)


@pytest.mark.parametrize(
    "demand,potential,nitrate",
    [
        ([1, 1, 1], [0.5, 0.5, 0.5], [0.3, 0.3, 0.3]),
        ([1, 1, 1], [0.5, 0.5, 0.5], [0.6, 0.6, 0.6]),
        (
            [1, 1, 1],
            [0.5, 0.5, 0.5],
            [0.6, 0.3, 0.6],
        ),
        ([1, 1, 1], [0.5, 0.5, 0.5], [0.6, 0.3, 0.6]),
        ([0.01, 0.01, 0.01], [0.5, 0.5, 0.5], [0.6, 0.3, 0.6]),
        (
            [25, 8.33, 2.05, 12.99, 0.5],
            [22.5, 15.98, 2.22, 35.4, 0.001],
            [15.5, 20.99, 8, 5.5, 0.1],
        ),
    ],
)
def test_determine_layer_nutrient_uptake(demand: list[float], potential: list[float], nitrate: list[float]) -> None:
    """Test that actual nutrient uptake from each layer is properly calculated by determine_layer_nitrogen_uptake()."""
    observe = NutrientUptake.determine_layer_nutrient_uptake(demand, potential, nitrate)
    expect = []
    for d, p, n in zip(demand, potential, nitrate):
        uptake = min(p + d, n)
        expect.append(uptake)
    assert observe == expect


@pytest.mark.parametrize(
    "reqs,srcs",
    [
        ([0, 0], [1, 1]),  # no requests
        ([0.5, 0], [1, 1]),  # request from first layer
        ([0, 0.5], [1, 1]),  # request from second layer
        ([0.5, 0.5], [1, 1]),  # request from both
        ([18.66, 33.74], [20.30, 19.93]),  # arbitrary
    ],
)
def test_determine_layer_extracted_resource(reqs: list[float], srcs: list[float]) -> None:
    """Ensure that extracted nutrient is correctly calculated for each layer."""
    draws = []
    for i in range(len(reqs)):
        draws.append(NutrientUptake._determine_extracted_resource(reqs[i], srcs[i]))
    assert draws == NutrientUptake.determine_layer_extracted_resource(reqs, srcs)


@pytest.mark.parametrize(
    "requested,available",
    [
        (0, 1),  # no request
        (0.5, 1),  # request < avaialble
        (1, 1),  # request = available
        (1.5, 1),  # request > available
        (85.93, 232.7),  # arbitrary
    ],
)
def test_determine_extracted_resource(requested: float, available: float) -> None:
    """Ensure that extracted resource is correctly calculated by determine_extracted_resource()."""
    if available < 0:
        drawn = 0
    elif requested > available:
        drawn = available
    else:
        drawn = requested
    assert drawn == NutrientUptake._determine_extracted_resource(requested, available)


@pytest.mark.parametrize(
    "prev,new,fix",
    [
        (1, 1, 1),
        (1, 1, 0),
        (1, 0, 1),
        (0, 1, 1),
        (0, 0, 0),
        (50.39, 10.55, 3.05),
    ],
)
def test_determine_stored_nutrient(prev: float, new: float, fix: float) -> None:
    """Test the stored nutrient is properly calculated by determine_stored_nutrient()."""
    observe = NutrientUptake.determine_stored_nutrient(new, prev, fix)
    assert observe == prev + new + fix


@pytest.mark.parametrize(
    "root_depth,depths,expect",
    [
        (1.5, [0, 1, 2, 3], [4, 1]),
        (2.6, [0, 1, 2, 3], [4, 0]),
        (0.3, [0, 0.5, 1, 2, 3], [5, 3]),
        (28.4, [18.2, 21.6, 100.4], [3, 0]),
    ],
)
def test_find_deepest_accessible_soil_layer(root_depth: float, depths: list[float], expect: list[float]) -> None:
    """Ensure that layers are partitioned correctly by determine_deepest_accessible_soil_layer."""
    data = CropData(root_depth=root_depth)
    incorp = NutrientUptake(data)
    incorp.find_deepest_accessible_soil_layer(depths)
    assert data.total_soil_layers == expect[0]
    assert data.accessible_soil_layers == NutrientUptake._determine_deepest_accessible_layer(root_depth, depths)
    assert data.inaccessible_soil_layers == expect[1]


@pytest.mark.parametrize(
    "deepest,layers",
    [
        (1, [1, 2, 3, 4]),  # one layer
        (2, [1, 2, 3, 4]),  # two layers
        (3, [1, 2, 3, 4]),  # three layers
        (4, [1, 2, 3, 4]),  # four layers
        (2, [22.5, 80.6, 100.0, 199.9]),  # arbitrary list
    ],
)
def test_access_layers(deepest: int, layers: list[float]) -> None:
    """Check that soil layers are accessed correctly with access_layers()."""
    data = CropData(accessible_soil_layers=deepest)
    incorp = NutrientUptake(data)
    assert incorp.access_layers(layers) == layers[slice(deepest)]


@pytest.mark.parametrize(
    "missed,uptakes,expect",
    [
        (-1, [0.25, 0.5, 1], [0.25, 0.5, 1]),  # negative missed layers
        (0, [0.25, 0.5, 1], [0.25, 0.5, 1]),  # no missed layers
        (1, [0.25, 0.5, 1], [0.25, 0.5, 1, 0]),  # one missed layer
        (2, [0.25, 0.5, 1], [0.25, 0.5, 1, 0, 0]),  # 2 missed layers
        (
            3,
            [12.5, 8.3, 22.2, 7.8],
            [12.5, 8.3, 22.2, 7.8, 0, 0, 0],
        ),  # arbitrary, 3 missed
    ],
)
def test_extend_nutrient_uptakes_to_full_profile(missed: int, uptakes: list[float], expect: list[float]) -> None:
    """Check that the correct number of zeros are padded to uptakes by extend_nutrient_uptakes_to_full_profile()."""
    data = CropData(inaccessible_soil_layers=missed)
    incorp = NutrientUptake(data)
    incorp.extend_nutrient_uptakes_to_full_profile(uptakes)
    assert uptakes == expect


@pytest.mark.parametrize(
    "uptakes,nutrients",
    [
        ([1], [1]),  # start
        ([1], [0]),
        ([0], [1]),  # no uptakes
        ([0.5], [1]),
        ([1.2], [1]),
        ([37.9, 40.2, 18.3], [100.5, 83.3, 30.7]),  # arbitrary - abundant nitrates
        ([87.36, 86.40, 30.33], [82.4, 83.0, 29.9]),
        ([57.33, 32.20, 0], [40.2, 99.0, 30.7]),  # no uptake from last layer
    ],
)
def test_extract_nutrient_from_soil_layers(uptakes: list[float], nutrients: list[float]) -> None:
    """
    Check the nutrient is correctly extracted from soil layers with the function extract_nutrient_from_soil_layers().
    """
    nitrates_copy = nutrients.copy()

    data = CropData()
    incorp = NutrientUptake(data)
    incorp.extract_nutrient_from_soil_layers(nutrients, uptakes)

    remaining = []
    for i in range(len(uptakes)):
        remaining.append(max(nitrates_copy[i] - uptakes[i], 0))
    assert nutrients == remaining


@pytest.mark.parametrize(
    "uptakes",
    [
        [1],  # one layer
        [1, 1, 1, 1],  # four layers
        [81.2, 0],  # arbitrary with zero
        [15.3, 18.2, 4, 20.33],
    ],
)
def test_tally_total_nitrogen_uptake(uptakes: list[float]) -> None:
    """Check that total nutrient is correctly calculated by tally_total_nutrient_uptake()."""
    data = CropData()
    incorp = NutrientUptake(data)
    result = incorp.tally_total_nutrient_uptake(uptakes)
    assert result == sum(uptakes)

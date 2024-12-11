from math import exp, log
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from pytest_mock import MockerFixture

from RUFAS.output_manager import OutputManager
from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.crop.nitrogen_incorporation import NitrogenIncorporation
from RUFAS.routines.field.soil.soil_data import SoilData


@pytest.fixture
def mock_add(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(OutputManager, "add_error")


# --- static function tests ----
@pytest.mark.parametrize(
    "halfheat,heatfrac,emerge,half,near,mature,should_fail",
    [
        (0.5, 1.0, 0.8, 0.6, 0.3, 0.2, False),  # start
        (0.99, 1.0, 0.8, 0.6, 0.3, 0.2, False),  # half_heat close to mature heat
        (0.01, 1.0, 0.8, 0.6, 0.3, 0.2, False),  # small half_heat
        (0.5, 1.0, 0.8, 0.6, 0.20001, 0.2, False),  # near very close to mature
        (0.286, 0.54, 0.522, 0.4, 0.1, 0.08, False),  # arbitrary
        # Above tests are copied from old subroutine tests
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
def test_determine_nitrogen_shape_parameters(
    halfheat: float,
    heatfrac: float,
    emerge: float,
    half: float,
    near: float,
    mature: float,
    should_fail: bool,
    mock_add: MagicMock,
) -> None:
    """check that the shape parameters are correctly calculated by determine_nshapes() and that errors were raised
    correctly"""
    OutputManager()
    if should_fail:
        try:
            NitrogenIncorporation.determine_nutrient_shape_parameters(halfheat, heatfrac, emerge, half, mature)
        except ValueError as e:
            assert str(e) == "half_mature_heat_fraction must not equal mature_heat_fraction"
            mock_add.assert_called_once()
    else:
        expected_near = mature + 0.00001
        observe = NitrogenIncorporation.determine_nutrient_shape_parameters(halfheat, heatfrac, emerge, half, mature)
        expect_2 = (
            NitrogenIncorporation._determine_shape_log(halfheat, half, mature, emerge)
            - NitrogenIncorporation._determine_shape_log(heatfrac, expected_near, mature, emerge)
        ) / (heatfrac - halfheat)
        expect_1 = NitrogenIncorporation._determine_shape_log(halfheat, half, mature, emerge) + (expect_2 * halfheat)
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
    """check that determine_shape_log() calculates correct output"""
    observe = NitrogenIncorporation._determine_shape_log(heatfrac, current, mature, emergence)
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
        # (1, 0.3, 0.29, 0.8),  # no error
    ],
)
def test_error_determine_shape_log(
    heatfrac: float, current: float, mature: float, emergence: float, mock_add: MagicMock
) -> None:
    """check that determine_shape_log() throws errors when appropriate"""
    OutputManager()
    with pytest.raises(Exception):
        NitrogenIncorporation._determine_shape_log(heatfrac, current, mature, emergence)
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
def test_determine_optimal_nitrogen_fraction(
    heatfrac: float, emerge: float, mature: float, shape1: float, shape2: float
) -> None:
    """Ensure that nitrogen fraction is correctly calculated by determine_optimal_nitrogen_fraction()."""
    observe = NitrogenIncorporation.determine_optimal_nutrient_fraction(heatfrac, emerge, mature, shape1, shape2)
    expect = (emerge - mature) * (1 - (heatfrac / (heatfrac + exp(shape1 - shape2 * heatfrac)))) + mature
    assert observe == expect


@pytest.mark.parametrize("nfrac,biomass", [(1, 1), (1, 0), (0, 1), (0, 0), (0.25, 0.3), (0.10, 0.257)])
def test_determine_optimal_nitrogen(nfrac: float, biomass: float) -> None:
    """test that optimal nitrogen is correctly calculated by determine_optimal_nitrogen()"""
    assert NitrogenIncorporation.determine_optimal_nutrient(nfrac, biomass) == nfrac * biomass


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
def test_determine_potential_nitrogen_uptake(optimal: float, previous: float, mature: float, max_growth: float) -> None:
    """test that potential nitrogen uptake is correctly calculated by determine_max_nitrogen_uptake()"""
    expect = min(optimal - previous, 4 * mature * max_growth)
    observe = NitrogenIncorporation.determine_potential_nutrient_uptake(optimal, previous, mature, max_growth)
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
def test_determine_deepest_accessible_layer(root: float, depths: float, expect: float) -> None:
    assert NitrogenIncorporation.determine_deepest_accessible_layer(root, depths) == expect


@pytest.mark.parametrize("root,depths", [(-1, [0, 1, 2, 3])])  # root < 0
def test_error_determine_deepest_accessible_layer(root: float, depths: float, mock_add: MagicMock) -> None:
    OutputManager()
    with pytest.raises(ValueError):
        NitrogenIncorporation.determine_deepest_accessible_layer(root, depths)
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
def test_determine_layer_nitrogen_uptake_potential(
    bounds: float, demand: float, root_depth: float, ndistro: float
) -> None:
    """
    ensure potential nitrogen uptake is calculated correctly for each soil layer with
    determine_layer_nitrogen_potential()
    """
    layer_nitrogen = []  # empty list to fill
    upper_nitrogen = 0  # nitrogen in the top boundary (soil surface) is 0
    for i in range(len(bounds)):
        lower_nitrogen = NitrogenIncorporation._determine_nitrogen_uptake_to_depth(
            demand, bounds[i], root_depth, ndistro
        )
        layer_nitrogen.append(lower_nitrogen - upper_nitrogen)
        upper_nitrogen = lower_nitrogen
    expect = layer_nitrogen
    observe = NitrogenIncorporation.determine_layer_nutrient_uptake_potential(bounds, demand, root_depth, ndistro)
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
def test_error_determine_layer_nitrogen_uptake_potential(
    bounds: float, demand: float, root_depth: float, ndistro: float, mock_add: MagicMock
) -> None:
    """check that determine_layer_nitrogen_potential throws an error when soil boundaries are not properly ordered"""
    OutputManager()
    with pytest.raises(Exception):
        NitrogenIncorporation.determine_layer_nutrient_uptake_potential(bounds, demand, root_depth, ndistro)
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
def test_determine_nitrogen_uptake_to_depth(demand: float, depth: float, root_depth: float, ndistro: float) -> None:
    """check that nitrogen uptake is correctly calculated by determine_surface_nitrogen_uptake()"""
    observe = NitrogenIncorporation._determine_nitrogen_uptake_to_depth(demand, depth, root_depth, ndistro)
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
def test_error_determine_nitrogen_uptake_to_depth(
    demand: float, depth: float, root_depth: float, ndistro: float, mock_add: MagicMock
) -> None:
    """ "check that errors are appropriately thrown for determine_surface_nitrogen_uptake()"""
    OutputManager()
    with pytest.raises(Exception):
        NitrogenIncorporation._determine_nitrogen_uptake_to_depth(demand, depth, root_depth, ndistro)
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
def test_determine_layer_nitrogen_demands(pots: list[float], avails: list[float]) -> None:
    """test that nitrogen demand is correctly calculated for each layer by determine_layer_nitrogen_demand()"""
    observe = NitrogenIncorporation.determine_layer_nutrient_demands(pots, avails)
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


@pytest.mark.parametrize(
    "demand,potential,nitrate",
    [
        ([1, 1, 1], [0.5, 0.5, 0.5], [0.3, 0.3, 0.3]),  # use nitrate
        ([1, 1, 1], [0.5, 0.5, 0.5], [0.6, 0.6, 0.6]),  # use nitrogen
        (
            [1, 1, 1],
            [0.5, 0.5, 0.5],
            [0.6, 0.3, 0.6],
        ),  # use nitrogen, then nitrate, then nitrogen
        ([1, 1, 1], [0.5, 0.5, 0.5], [0.6, 0.3, 0.6]),  # increased demand
        ([0.01, 0.01, 0.01], [0.5, 0.5, 0.5], [0.6, 0.3, 0.6]),  # decreased demand
        (
            [25, 8.33, 2.05, 12.99, 0.5],
            [22.5, 15.98, 2.22, 35.4, 0.001],
            [15.5, 20.99, 8, 5.5, 0.1],
        ),  # arbitrary
    ],
)
def test_determine_layer_nitrogen_uptake(demand: list[float], potential: list[float], nitrate: list[float]) -> None:
    """test that actual nitrogen uptake from each layer is properly calculated by determine_layer_nitrogen_uptake()"""
    observe = NitrogenIncorporation.determine_layer_nutrient_uptake(demand, potential, nitrate)
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
    """ensure that extracted nitrogen is correctly calculated for each layer"""
    draws = []
    for i in range(len(reqs)):
        draws.append(NitrogenIncorporation._determine_extracted_resource(reqs[i], srcs[i]))
    assert draws == NitrogenIncorporation.determine_layer_extracted_resource(reqs, srcs)


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
    """ensure that extracted resource is correctly calculated by determine_extracted_resource()"""
    if available < 0:
        drawn = 0
    elif requested > available:
        drawn = available
    else:
        drawn = requested
    assert drawn == NitrogenIncorporation._determine_extracted_resource(requested, available)


@pytest.mark.parametrize(
    "nitrates,expect",
    [
        (0, 1),  # A
        (13.2, 1),  # arbitrary A
        (100, 1),  # A edge
        (100.1, 1.5 - 5e-3 * 100.1),  # B
        (200, 1.5 - 5e-3 * 200),  # B
        (300, 1.5 - 5e-3 * 300),  # B
        (300.1, 0),  # C
        (450, 0),  # C
    ],
)
def test_determine_nitrate_factor(nitrates: float, expect: float) -> None:
    assert NitrogenIncorporation._determine_nitrate_factor(nitrates) == expect


@pytest.mark.parametrize(
    "heatfrac,expect",
    [
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
        (1.39, 0.0),
    ],
)
def test_determine_fixation_stage_factor(heatfrac: float, expect: float) -> None:
    assert NitrogenIncorporation._determine_fixation_stage_factor(heatfrac) == expect


@pytest.mark.parametrize(
    "demand,stage,water,nitrate,expect",
    [
        (0, 1, 1, 1, 0),  # no demand
        (1, 1, 1, 1, 1),  # all 1
        (1, 1, 0.2, 0.5, 0.2),  # water min
        (1, 1, 0.6, 0.5, 0.5),  # nitrate min
        (1, 0.5, 0.6, 0.5, 0.5 * 0.5),  # reduced stage
        (0.3, 0.5, 0.6, 0.5, 0.3 * 0.5 * 0.5),  # reduced demand
    ],
)
def test_determine_fixed_nitrogen(demand: float, stage: float, water: float, nitrate: float, expect: float) -> None:
    """check that nitrogen values are calculated as expected with determine_fixed_nitrogen()"""
    assert NitrogenIncorporation._determine_fixed_nitrogen(demand, stage, water, nitrate) == expect


@pytest.mark.parametrize(
    "demand,stage,water,nitrate",
    [
        (1, -1, 1, 1),  # neg stage
        (1, 1, -1, 1),  # neg water
        (1, 1, 1, -1),  # neg nitrate
        (1, 1.2, 1, 1),  # stage > 1
        (1, 1, 2, 1),  # water > 1
        (1, 1, 1, 100),  # nitrate > 1
    ],
)
def test_error_determine_fixed_nitrogen(
    demand: float, stage: float, water: float, nitrate: float, mock_add: MagicMock
) -> None:
    OutputManager()
    with pytest.raises(ValueError):
        NitrogenIncorporation._determine_fixed_nitrogen(demand, stage, water, nitrate)
    mock_add.assert_called_once()


@pytest.mark.parametrize(
    "prev,new,fix",
    [
        (1, 1, 1),  # all 1
        (1, 1, 0),  # no fixation
        (1, 0, 1),  # no new nitrogen
        (0, 1, 1),  # no previous nitrogen
        (0, 0, 0),  # all 0
        (50.39, 10.55, 3.05),  # arbitrary
    ],
)
def test_determine_stored_nitrogen(prev: float, new: float, fix: float) -> None:
    """test the stored nitrogen is properly calculated by determine_stored_nitrogen()"""
    observe = NitrogenIncorporation.determine_stored_nutrient(new, prev, fix)
    assert observe == prev + new + fix


# ---- member function tests ----
@pytest.mark.parametrize(
    "old,new",
    [
        (None, 1),  # no start
        (0, 1),  # start = 0
        (1, 2),  # start = 0
        (2, 1),  # start > new
        (133.26, 149.4),  # arbitrary
    ],
)
def test_shift_nitrogen_time(old: float, new: float) -> None:
    data = CropData(nitrogen=new)
    incorp = NitrogenIncorporation(data, previous_nitrogen=old)
    incorp.shift_nitrogen_time()
    assert incorp.previous_nitrogen == new


@pytest.mark.parametrize(
    "root_depth,depths,expect",
    [
        (1.5, [0, 1, 2, 3], [4, 1]),
        (2.6, [0, 1, 2, 3], [4, 0]),
        (0.3, [0, 0.5, 1, 2, 3], [5, 3]),
        (28.4, [18.2, 21.6, 100.4], [3, 0]),
    ],
)
def test_find_deepest_accessible_soil_layer(root_depth: float, depths: float, expect: float) -> None:
    """ensure that layers are partitioned correctly by determine_deepest_accessible_soil_layer"""
    data = CropData(root_depth=root_depth)
    incorp = NitrogenIncorporation(data)
    incorp.find_deepest_accessible_soil_layer(depths)
    assert data.total_soil_layers == expect[0]
    assert data.accessible_soil_layers == NitrogenIncorporation.determine_deepest_accessible_layer(root_depth, depths)
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
def test_access_layers(deepest: float, layers: list[float]) -> None:
    """check that soil layers are accessed correctly with access_layers()"""
    data = CropData(accessible_soil_layers=deepest)
    incorp = NitrogenIncorporation(data)
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
def test_extend_nitrate_uptakes_to_full_profile(missed: float, uptakes: list[float], expect: list[float]) -> None:
    """check that the correct number of zeros are padded to uptakes by extend_nitrate_uptakes_to_full_profile()"""
    data = CropData(inaccessible_soil_layers=missed)
    incorp = NitrogenIncorporation(data, actual_nitrogen_uptakes=uptakes)
    incorp.extend_nitrate_uptakes_to_full_profile()
    assert incorp.actual_nitrogen_uptakes == expect


@pytest.mark.parametrize(
    "uptakes,nitrates",
    [
        ([1], [1]),  # start
        ([1], [0]),  # no nitrates
        ([0], [1]),  # no uptakes
        ([0.5], [1]),  # uptakes < nitrates
        ([1.2], [1]),  # uptakes > nitrates
        ([37.9, 40.2, 18.3], [100.5, 83.3, 30.7]),  # arbitrary - abundant nitrates
        ([87.36, 86.40, 30.33], [82.4, 83.0, 29.9]),  # nitrates limited
        ([57.33, 32.20, 0], [40.2, 99.0, 30.7]),  # no uptake from last layer
    ],
)
def test_extract_nitrogen_from_soil_layers(uptakes: list[float], nitrates: list[float]) -> None:
    nitrates_copy = nitrates.copy()

    data = CropData()
    incorp = NitrogenIncorporation(data, actual_nitrogen_uptakes=uptakes)
    incorp.extract_nitrogen_from_soil_layers(nitrates)

    remaining = []
    for i in range(len(uptakes)):
        remaining.append(max(nitrates_copy[i] - uptakes[i], 0))
    assert nitrates == remaining


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
    """check that total nitrogen is correctly calculated by tally_total_nitrogen_uptake()"""
    data = CropData()
    incorp = NitrogenIncorporation(data, actual_nitrogen_uptakes=uptakes)
    incorp.tally_total_nitrogen_uptake()
    assert incorp.total_nitrogen_uptake == sum(uptakes)


@pytest.mark.parametrize(
    "fixer,nitrates,water",
    [
        (True, 100, 0.5),  # fixer with nitrates
        (True, 0, 0.5),  # fixer without nitrates
        (False, 100, 0.5),  # non-fixer with nitrates
        (False, 0, 0.5),  # non-fixer without nitrates
    ],
)
def test_try_fixation(fixer: bool, nitrates: float, water: float, mocker: MockerFixture) -> None:
    """check that try_fixation calls its sub-functions if fixation occurs"""
    patch_update_fixation_attributes = mocker.patch(
        "RUFAS.routines.field.crop.nitrogen_incorporation.NitrogenIncorporation.update_fixation_attributes"
    )
    patch_fix_nitrogen = mocker.patch(
        "RUFAS.routines.field.crop.nitrogen_incorporation.NitrogenIncorporation.fix_nitrogen"
    )
    data = CropData(is_nitrogen_fixer=fixer)
    incorp = NitrogenIncorporation(data)
    incorp.try_fixation(nitrates, water)
    if fixer:
        patch_update_fixation_attributes.assert_called_once()
        patch_fix_nitrogen.assert_called_once()
    else:
        patch_update_fixation_attributes.assert_not_called()
        patch_fix_nitrogen.assert_not_called()
        assert incorp.fixed_nitrogen == 0


def test_update_fixation_attributes(mocker: MockerFixture) -> None:
    """ "check that update_nitrate_attributes calls both its sub-functions"""
    patch_determine_nitrate_factor = mocker.patch(
        "RUFAS.routines.field.crop.nitrogen_incorporation.NitrogenIncorporation._determine_nitrate_factor"
    )
    patch_determine_determine_fixation_stage_factor = mocker.patch(
        "RUFAS.routines.field.crop.nitrogen_incorporation.NitrogenIncorporation._determine_fixation_stage_factor"
    )
    incorp = NitrogenIncorporation()
    incorp.update_fixation_attributes(100)
    patch_determine_nitrate_factor.assert_called_once()
    patch_determine_determine_fixation_stage_factor.assert_called_once()


@pytest.mark.parametrize(
    "uptake,demand,water,fixfact,nitrate",
    [
        (0, 10, 0.5, 0.25, 0.3),  # unmet demand, water > nitrate > fix
        (10, 10, 0.5, 0.25, 0.3),  # no unmet demand, water > nitrate > fix
        (5, 10, 0.2, 0.25, 0.3),  # unmet demand, water < fix < nitrate
        (5, 10, 0.2, 0.25, 0.22),  # unmet demand, water < nitrate < fix
        (73.4, 112.5, 0.83, 0.11, 0.44),  # arbitrary
    ],
)
def test_fix_nitrogen(uptake: float, demand: float, water: float, fixfact: float, nitrate: float) -> None:
    """check that fixed nitrogen is properly calculated by fix_nitrogen()"""
    data = CropData()
    incorp = NitrogenIncorporation(
        data,
        potential_nitrogen_uptake=demand,
        total_nitrogen_uptake=uptake,
        fixation_stage_factor=fixfact,
        nitrate_factor=nitrate,
    )
    incorp.fix_nitrogen(water)
    if (demand - uptake) > 0:
        assert incorp.fixed_nitrogen == NitrogenIncorporation._determine_fixed_nitrogen(
            demand - uptake, fixfact, water, nitrate
        )
    else:
        assert incorp.fixed_nitrogen == 0


@pytest.mark.parametrize("depths,nitrates", [([0.5, 1, 10, 20], [0.5, 0.8, 5, 10])])
def test_uptake_nitrogen(depths: list[float], nitrates: list[float]) -> None:
    # initialize crop and run method
    data = CropData(root_depth=35.0)
    incorp = NitrogenIncorporation(data, potential_nitrogen_uptake=17.5, nitrogen_distro_param=0.32)

    # Mock functions
    incorp.find_deepest_accessible_soil_layer = MagicMock(return_value=None)
    incorp.access_layers = MagicMock(return_value=[1, 2, 3])
    incorp.determine_layer_nutrient_uptake_potential = MagicMock(return_value=[3.25, 6.33, 7.10])
    incorp.determine_layer_nutrient_demands = MagicMock(return_value=[12, 15, 17])
    incorp.determine_layer_nutrient_uptake = MagicMock(return_value=[8.9, 9.9, 13.12])
    incorp.determine_layer_extracted_resource = MagicMock(return_value=[5.0, 4.0, 2.0])
    incorp.extend_nitrate_uptakes_to_full_profile = MagicMock()
    incorp.extract_nitrogen_from_soil_layers = MagicMock()
    incorp.tally_total_nitrogen_uptake = MagicMock()

    # run function
    incorp.uptake_nitrogen(nitrates, depths)

    # check assertions
    incorp.find_deepest_accessible_soil_layer.assert_called_once_with(depths)
    incorp.determine_layer_nutrient_uptake_potential.assert_called_once_with([1, 2, 3], 17.5, 35.0, 0.32)
    assert incorp.layer_nitrogen_potentials == [3.25, 6.33, 7.10]
    incorp.determine_layer_nutrient_demands.assert_called_once_with([3.25, 6.33, 7.10], [1, 2, 3])
    assert incorp.unmet_nitrogen_demands == [12, 15, 17]
    incorp.determine_layer_nutrient_uptake.assert_called_once_with([12, 15, 17], [3.25, 6.33, 7.10], [1, 2, 3])
    assert incorp.nitrogen_requests == [8.9, 9.9, 13.12]
    incorp.determine_layer_extracted_resource.assert_called_once_with([8.9, 9.9, 13.12], [1, 2, 3])
    assert incorp.actual_nitrogen_uptakes == [5.0, 4.0, 2.0]
    incorp.extend_nitrate_uptakes_to_full_profile.assert_called_once()
    incorp.extract_nitrogen_from_soil_layers.assert_called_once()
    incorp.tally_total_nitrogen_uptake.assert_called_once()


@pytest.mark.parametrize(
    "nitrates,depths,water_factor,gate",
    [
        ([0.5, 0.3, 0.2], [1, 2, 5], 0.692, True),
        ([0.5, 0.3, 0.2], [1, 2, 5], 0.692, False),
    ],
)
def test_incorporate_nitrogen(nitrates: list[float], depths: list[float], water_factor: float, gate: bool) -> None:
    """Tests that nitrogen uptake and fixation is performed correctly."""
    # initialize object
    data = CropData(
        half_mature_heat_fraction=0.54,
        mature_heat_fraction=0.99,
        biomass=122.8,
        biomass_growth_max=999,
        emergence_nitrogen_fraction=0.71,
        half_mature_nitrogen_fraction=0.68,
        mature_nitrogen_fraction=0.60,
    )
    with (
        patch(
            "RUFAS.routines.field.soil.soil_data.SoilData.soil_water_factor",
            new_callable=PropertyMock,
            return_value=water_factor,
        ),
        patch.object(CropData, "heat_fraction", new_callable=PropertyMock, return_value=0.38),
    ):
        soil = SoilData(field_size=1.3)
        del soil.soil_layers[3]  # delete 4th layer
        top_depths = [0] + depths[:2]
        soil.set_vectorized_layer_attribute("top_depth", top_depths)
        soil.set_vectorized_layer_attribute("bottom_depth", depths)
        soil.set_vectorized_layer_attribute("nitrate", nitrates)
        incorp = NitrogenIncorporation(
            data,
            previous_nitrogen=0,
        )
        # mock intermediate functions
        incorp.shift_nitrogen_time = MagicMock(return_value=None)
        incorp.determine_nutrient_shape_parameters = MagicMock(return_value=[1.2, 0.8])
        incorp.determine_optimal_nutrient_fraction = MagicMock(return_value=0.75)
        if gate:
            incorp.determine_optimal_nutrient = MagicMock(return_value=-268)
        else:
            incorp.determine_optimal_nutrient = MagicMock(return_value=268)
        incorp.determine_potential_nutrient_uptake = MagicMock(return_value=123.1)
        incorp.uptake_nitrogen = MagicMock(return_value=None)
        incorp.access_layers = MagicMock(return_value=[5, 10, 15.3])
        incorp.try_fixation = MagicMock(return_value=None)
        NitrogenIncorporation.determine_stored_nutrient = MagicMock(return_value=99.3)

        # run method
        incorp.incorporate_nitrogen(soil)

        # assertions
        incorp.shift_nitrogen_time.assert_called_once()
        incorp.determine_nutrient_shape_parameters.assert_called_once_with(0.54, 0.99, 0.71, 0.68, 0.60)
        assert incorp.nitrogen_shapes == [1.2, 0.8]
        incorp.determine_optimal_nutrient_fraction.assert_called_once_with(0.38, 0.71, 0.60, 1.2, 0.8)
        assert data.optimal_nitrogen_fraction == 0.75
        if gate:
            incorp.determine_optimal_nutrient.assert_called_once_with(0.75, 122.8)
            assert data.optimal_nitrogen == -268
            incorp.determine_potential_nutrient_uptake.assert_not_called()
            assert incorp.potential_nitrogen_uptake == 0
        else:
            assert data.optimal_nitrogen == 268
            incorp.determine_potential_nutrient_uptake.assert_called_once_with(268, 0, 0.60, 999)
            assert incorp.potential_nitrogen_uptake == 123.1
        incorp.try_fixation.assert_called_once_with(5 + 10 + 15.3, water_factor)
        NitrogenIncorporation.determine_stored_nutrient.assert_called_once()  # should called_once_with() w/attr mocked
        assert data.nitrogen == 99.3

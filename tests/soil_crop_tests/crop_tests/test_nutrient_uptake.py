from math import log, exp

import pytest
from pytest_mock import MockerFixture

from RUFAS.output_manager import OutputManager
from RUFAS.routines.field.crop.nutrient_uptake import NutrientUptake


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
    """check that the shape parameters are correctly calculated by determine_nshapes() and that errors were raised
    correctly"""
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
    """check that determine_shape_log() calculates correct output"""
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
    """check that determine_shape_log() throws errors when appropriate"""
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
    """test that optimal nutrient is correctly calculated by determine_optimal_nutrient()"""
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
    """test that potential nutrient uptake is correctly calculated by determine_potential_nutrient_uptake()"""
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
    """test that the deepest soil layer that is accessible to roots
     is correctly calculated by _determine_deepest_accessible_layer()"""
    assert NutrientUptake._determine_deepest_accessible_layer(root, depths) == expect


@pytest.mark.parametrize("root,depths", [(-1, [0, 1, 2, 3])])  # root < 0
def test_error_determine_deepest_accessible_layer(root: float, depths: list[float], mocker: MockerFixture) -> None:
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
    ensure potential nutrient uptake is calculated correctly for each soil layer with
    determine_layer_nutrient_potential()
    """
    layer_nitrogen = []  # empty list to fill
    upper_nitrogen = 0  # nitrogen in the top boundary (soil surface) is 0
    for i in range(len(bounds)):
        lower_nitrogen = NutrientUptake._determine_nutrient_uptake_to_depth(
            demand, bounds[i], root_depth, ndistro
        )
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
    """check that determine_layer_nutrient_potential throws an error when soil boundaries are not properly ordered"""
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
    """check that nutrient uptake is correctly calculated by determine_surface_nutrient_uptake()"""
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
    """ "check that errors are appropriately thrown for determine_surface_nitrogen_uptake()"""
    om = OutputManager()
    mock_add = mocker.patch.object(om, "add_error")
    with pytest.raises(Exception):
        NutrientUptake._determine_nutrient_uptake_to_depth(demand, depth, root_depth, ndistro)
    mock_add.assert_called_once()

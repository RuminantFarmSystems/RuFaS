from math import exp

import pytest

from RUFAS.routines.field.crop.biomass_allocation import BiomassAllocation
from RUFAS.routines.field.crop.crop_data import CropData

from tests.soil_crop_tests.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


@pytest.fixture
def mock_crop_data() -> CropData:
    return CropData(**SAMPLE_CROP_CONFIGURATION)


# ---- helper function tests ----
@pytest.mark.parametrize(
    "rad,ext,lai",
    [(1, 1, 1), (0, 0, 0), (1, 0, 1), (0.2, -0.38, 0.75), (0.2, 0.38, 0.75)],
)
def test_calc_intercepted_radiation(rad: float, ext: float, lai: float) -> None:
    """ensure that intercepted radiation is correctly calculated by calc_intercepted_radiation()"""
    h_photo = 0.5 * rad * (1 - exp(-ext * lai))
    result = BiomassAllocation._intercept_radiation(rad, ext, lai)
    assert result == h_photo


@pytest.mark.parametrize(
    "rad,eff,expected",
    [
        (0, 0, 0),
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 0),
        (1, 1, 1),
        (1000, 0.33, 330),  # arbitrary
        (1961.67, 0.217, 1961.67 * 0.217),
        (18.5, 22.19, 18.5 * 22.19),  # rad < eff
    ],
)
def test_calc_max_accumulation(rad: float, eff: float, expected: float) -> None:
    """test that maximum biomass accumulation is properly calculated with calc_max_accumulation()"""
    assert BiomassAllocation._determine_max_accumulation(rad, eff) == expected


@pytest.mark.parametrize(
    "factor,max_growth",
    [(1, 0), (0, 1), (1, 1), (0.8, 103.84), (1.2, 103.84), (1.2, 873.2)],
)
def test_calc_biomass_accumulation(factor: float, max_growth: float) -> None:
    """ensure that biomass growth is correctly calculated by calc_biomass_accumulation()"""
    assert BiomassAllocation._determine_accumulated_biomass(factor, max_growth) == max_growth * factor


@pytest.mark.parametrize(
    "frac,bmass",
    [
        (1, 0),
        (0, 1),
        (0, 0),
        (1, 1),
        (1.00, 836.2),  # arbitrary: frac = 1
        (0.46, 836.2),  # arbitrary: frac < 1
        (1.27, 836.2),  # arbitrary: frac > 1
        (-1, 836.2),  # arbitrary: frac < 0
        (0.59, 529.33),  # arbitrary 2
    ],
)
def test_calc_above_ground_biomass(frac: float, bmass: float) -> None:
    """ensure that above ground biomass is correctly calculated"""
    expect = bmass * (1 - frac)
    assert BiomassAllocation._determine_above_ground_biomass(frac, bmass) == expect


@pytest.mark.parametrize(
    "frac,bmass",
    [
        (1, 0),
        (0, 1),
        (0, 0),
        (1, 1),
        (1.00, 836.2),  # arbitrary: frac = 1
        (0.46, 836.2),  # arbitrary: frac < 1
        (1.27, 836.2),  # arbitrary: frac > 1
        (-1, 836.2),  # arbitrary: frac < 0
        (0.59, 529.33),  # arbitrary 2
    ],
)
def test_calc_below_ground_biomass(frac: float, bmass: float) -> None:
    """ensure that below ground biomass is correctly calculated"""
    assert BiomassAllocation._determine_below_ground_biomass(frac, bmass) == bmass * frac


# ---- member function tests ----
@pytest.mark.parametrize(
    "light,ext,conv,gfact,rfrac",
    [
        (1000, 0.7, 20, 1, 1 / 3),  # start
        (1000, 0.7, 20, 1, 0.66),  # increased root proportion
        (1000, 0.7, 20, 0.83, 0.33),  # restricted growth
        (1000, 0.7, 16.3, 1, 0.33),  # reduced energy conversion
        (1000, 0.8, 20, 1, 0.33),  # greater light extinction
        (824.6, 0.7, 20, 1, 0.33),  # lower incoming light
        (2372.55, 0.29, 15.17, 0.663, 0.205),  # arbitrary
    ],
)
def test_allocate_biomass(
    mock_crop_data: CropData, light: float, ext: float, conv: float, gfact: float, rfrac: float
) -> None:
    """Integration check to check that biomass gets allocated correctly."""
    mock_crop_data.leaf_area_index = 1.87
    mock_crop_data.growth_factor = gfact
    mock_crop_data.root_fraction = rfrac
    mock_crop_data.biomass = 89.0
    mock_crop_data.light_use_efficiency = conv
    bioal = BiomassAllocation(mock_crop_data, light_extinction=ext)

    bioal.allocate_biomass(light)

    # photosynthesize
    energy = BiomassAllocation._intercept_radiation(light, ext, lai=1.87)
    max_growth = BiomassAllocation._determine_max_accumulation(energy, conv)
    growth = BiomassAllocation._determine_accumulated_biomass(gfact, max_growth)
    mass = 89.0 + growth
    # TODO: test photosynthesize() and partition_biomass() separately? Issue #2514.
    # partition_biomass
    green = BiomassAllocation._determine_above_ground_biomass(rfrac, mass)
    root = BiomassAllocation._determine_below_ground_biomass(rfrac, mass)

    assert bioal.usable_light == energy
    assert mock_crop_data.biomass_growth_max == max_growth
    assert bioal.previous_biomass == 89.0
    assert bioal.biomass_growth == growth
    assert mock_crop_data.biomass == mass
    assert mock_crop_data.above_ground_biomass == green
    assert mock_crop_data.root_biomass == root

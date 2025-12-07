from math import exp

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.field.crop.biomass_allocation import BiomassAllocation
from RUFAS.biophysical.field.crop.crop_data import CropData

from tests.test_biophysical.test_crop_soil_field.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


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
def test_allocate_biomass(mock_crop_data: CropData, mocker: MockerFixture) -> None:
    """Integration check to check that biomass gets allocated correctly."""
    biomass_allocation = BiomassAllocation(mock_crop_data)
    mock_photosynthesize = mocker.patch.object(biomass_allocation, "photosynthesize")
    mock_partition_biomass = mocker.patch.object(biomass_allocation, "partition_biomass")

    biomass_allocation.allocate_biomass((dummy_light := 89.0))

    mock_photosynthesize.assert_called_once_with(dummy_light)
    mock_partition_biomass.assert_called_once_with()


@pytest.mark.parametrize(
    "light, light_extinction, light_use_efficiency, growth_factor, starting_biomass, expected_usable_light,"
    "expected_biomass_growth_max, expected_previous_biomass, expected_biomass_growth, expected_final_biomass",
    [
        # start
        (1000, 0.7, 20, 1, 89.0, 364.9549943019595, 7299.09988603919, 89.0, 7299.09988603919, 7388.09988603919),
        # restricted growth
        (1000, 0.7, 20, 0.83, 89.0, 364.9549943019595, 7299.09988603919, 89.0, 6058.252905412527, 6147.252905412527),
        # reduced energy conversion
        (1000, 0.7, 16.3, 1, 89.0, 364.9549943019595, 5948.766407121941, 89.0, 5948.766407121941, 6037.766407121941),
        # greater light extinction
        (1000, 0.8, 20, 1, 89.0, 387.98776589362916, 7759.755317872583, 89.0, 7759.755317872583, 7848.755317872583),
        # lower incoming light
        (824.6, 0.7, 20, 1, 89.0, 300.9418883013958, 6018.837766027917, 89.0, 6018.837766027917, 6107.837766027917),
        # arbitrary
        (
            2372.55,
            0.29,
            15.17,
            0.663,
            89.0,
            496.563479099514,
            7532.867977939627,
            89.0,
            4994.291469373973,
            5083.291469373973,
        ),
    ],
)
def test_photosynthesize(
    mock_crop_data: CropData,
    light: float,
    light_extinction: float,
    light_use_efficiency: float,
    growth_factor: float,
    starting_biomass: float,
    expected_usable_light: float,
    expected_biomass_growth_max: float,
    expected_previous_biomass: float,
    expected_biomass_growth: float,
    expected_final_biomass: float,
) -> None:
    mock_crop_data.leaf_area_index = 1.87
    mock_crop_data.growth_factor = growth_factor
    mock_crop_data.biomass = starting_biomass
    mock_crop_data.light_use_efficiency = light_use_efficiency
    biomass_allocation = BiomassAllocation(mock_crop_data, light_extinction=light_extinction)

    biomass_allocation.allocate_biomass(light)

    assert biomass_allocation.usable_light == pytest.approx(expected_usable_light)
    assert biomass_allocation.data.biomass_growth_max == pytest.approx(expected_biomass_growth_max)
    assert biomass_allocation.previous_biomass == pytest.approx(expected_previous_biomass)
    assert biomass_allocation.biomass_growth == pytest.approx(expected_biomass_growth)
    assert biomass_allocation.data.biomass == pytest.approx(expected_final_biomass)


@pytest.mark.parametrize(
    "bio_mass, root_fraction, expected_above_ground_biomass, expected_root_biomass",
    [
        (89.0, 1 / 3, 59.33333333333334, 29.666666666666664),
        (89.0, 0.66, 30.259999999999998, 58.74),
        (89.0, 0.33, 59.629999999999995, 29.37),
        (89.0, 0.205, 70.75500000000001, 18.244999999999997),
    ],
)
def test_partition_biomass(
    bio_mass: float,
    root_fraction: float,
    expected_above_ground_biomass: float,
    expected_root_biomass: float,
    mock_crop_data: CropData,
) -> None:
    mock_crop_data.biomass = bio_mass
    mock_crop_data.root_fraction = root_fraction
    biomass_allocation = BiomassAllocation(mock_crop_data)

    biomass_allocation.partition_biomass()

    assert biomass_allocation.data.above_ground_biomass == pytest.approx(expected_above_ground_biomass)
    assert biomass_allocation.data.root_biomass == pytest.approx(expected_root_biomass)

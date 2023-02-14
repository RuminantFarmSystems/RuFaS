import pytest
from math import exp, log, atan, sin
from unittest.mock import MagicMock

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.soil.soil_erosion import SoilErosion


# --- Static method tests ---
@pytest.mark.parametrize("sand,silt", [
    (15, 65),
    (0, 0),
    (17, 60),
    (9, 80),
    (12.339485, 61.1938549),
    (23.4958769, 58.1093485),
])
def test_determine_coarse_sand_factor(sand, silt):
    """tests _determine_coarse_sand_factor() in soil_erosion.py"""
    observe = SoilErosion._determine_coarse_sand_factor(sand, silt)
    expect_exp_term = exp((-0.256) * sand * (1 - (silt / 100)))
    expect = 0.2 + 0.3 * expect_exp_term
    # print(str(observe))
    assert observe == expect


@pytest.mark.parametrize("silt,clay", [
    (65, 20),
    (66.23948, 20.4958),
    (78.129348, 10.93845),
    (57.129485, 30.19485),
    (83.49482, 13.390458),
])
def test_determine_clay_silt_ratio_factor(silt, clay):
    """tests _determine_clay_silt_ratio_factor() in soil_erosion.py"""
    observe = SoilErosion._determine_clay_silt_ratio_factor(silt, clay)
    expect = silt / (clay + silt)
    expect = expect ** 0.3
    # print(str(observe))
    assert observe == expect


@pytest.mark.parametrize("silt,clay", [
    (0, 0),
])
def test_error_clay_silt_ratio_factor(silt, clay):
    """tests that _determine_clay_silt_ratio_factor() in soil_erosion.py correctly raises an error when invalid input is
        given"""
    with pytest.raises(Exception):
        SoilErosion._determine_clay_silt_ratio_factor(silt, clay)


@pytest.mark.parametrize("carbon", [
    0.012,
    0,
    0.039124,
    0.0019485,
    0.029684,
    0.01395986,
])
def test_determine_carbon_content_factor(carbon):
    """tests _determine_carbon_content_factor() in soil_erosion.py"""
    observe = SoilErosion._determine_carbon_content_factor(carbon)
    expect_bottom_term = carbon + exp(3.72 - 2.95 * carbon)
    expect = 1 - ((0.25 * carbon) / expect_bottom_term)
    # print(str(observe))
    assert observe == expect


@pytest.mark.parametrize("sand", [
    15,
    0,
    23.5869348,
    35.1938403,
    76.193850,
    80.10039458,
    12.9498602,
    8.1019843912,
    4.1938402,
])
def test_determine_high_sand_factor(sand):
    """tests _determine_high_sand_factor() in soil_erosion.py"""
    observe = SoilErosion._determine_high_sand_factor(sand)
    top_term = 0.7 * (1 - (sand / 100))
    first_bottom_term = (1 - (sand / 100))
    second_bottom_term = exp(-5.51 + 22.9 * first_bottom_term)
    expect = 1 - (top_term / (first_bottom_term + second_bottom_term))
    # print(str(observe))
    assert observe == expect


@pytest.mark.parametrize("sand,silt,clay,carbon", [
    (15, 65, 22.5, 0.012),
    (14.2938495, 68.29285945, 15.1918492, 0.02395923),
    (10.4829458, 78.19128491, 17.1828402, 0.0300195829),
    (30.104958, 50.1918749, 25.1143534, 0.0123923984),
    (50, 30.1948591, 19.8939582, 0.01139495),
])
def test_determine_soil_erodibility_factor(sand, silt, clay, carbon):
    """tests _determine_soil_erodibility_factor() in soil_erosion.py"""

    # Mock helper methods
    SoilErosion._determine_coarse_sand_factor = MagicMock(return_value=0.28)
    SoilErosion._determine_clay_silt_ratio_factor = MagicMock(return_value=0.93)
    SoilErosion._determine_carbon_content_factor = MagicMock(return_value=0.99)
    SoilErosion._determine_high_sand_factor = MagicMock(return_value=0.95)

    # Run method
    observe = SoilErosion._determine_soil_erodibility_factor(sand, silt, clay, carbon)

    # Check everything
    SoilErosion._determine_coarse_sand_factor.assert_called_once()
    SoilErosion._determine_clay_silt_ratio_factor.assert_called_once()
    SoilErosion._determine_carbon_content_factor.assert_called_once()
    SoilErosion._determine_high_sand_factor.assert_called_once()
    assert observe == (0.28 * 0.93 * 0.99 * 0.95)


@pytest.mark.parametrize("min_cover,residue", [
    (0.2, 800),
    (0.001, 500),
    (0.003, 80),
    (0.01, 0),
    (0.05, 928.948569),
])
def test_determine_cover_management_factor(min_cover, residue):
    """tests _determine_cover_management_factor() in soil_erosion.py"""
    observe = SoilErosion._determine_cover_management_factor(min_cover, residue)
    expect = exp((log(0.8) - log(min_cover)) * exp(-0.00115 * residue) + log(min_cover))
    assert observe == expect


@pytest.mark.parametrize("min_cover,residue", [
    (0, 0)
])
def test_error_determine_cover_management_factor(min_cover, residue):
    """tests that _determine_cover_management_factor() correctly raises error for invalid inputs"""
    with pytest.raises(Exception):
        SoilErosion._determine_cover_management_factor(min_cover, residue)


@pytest.mark.parametrize("average_slope", [
    0.02,
    0,
    0.001,
    0.05,
    0.084595829,
    0.12593,
])
def test_determine_exponential_term(average_slope):
    """tests _determine_exponential_term() in soil_erosion.py"""
    observe = SoilErosion._determine_exponential_term(average_slope)
    exp_term = exp(-35.835 * average_slope)
    expect = 0.6 * (1 - exp_term)
    assert observe == expect


@pytest.mark.parametrize("length, avg_slope", [
    (3, 0.02),
    (0, 0),
    (16, 0.11),
    (19, 0.19),
    (1, 0.28),
    (8.194894, 0.089493),
])
def test_determine_topographic_factor(length, avg_slope):
    """tests _determine_topographic_factor() in soil_erosion.py"""

    # Mock helper function
    SoilErosion._determine_exponential_term = MagicMock(return_value=0.45)

    # Run method
    observe = SoilErosion._determine_topographic_factor(length, avg_slope)

    # Calculate expected return value
    expect = ((length / 22.1) ** 0.45) * (65.41 * (sin(atan(avg_slope)) ** 2) + 4.56 * sin(atan(avg_slope)) + 0.065)

    # Check everything
    SoilErosion._determine_exponential_term.assert_called_with(avg_slope)
    assert observe == expect


@pytest.mark.parametrize("percent_rock", [
    0,
    0.5,
    0.02194,
    0.019493,
    0.0492184949,
    0.10495492330,
])
def test_determine_coarse_fragment_factor(percent_rock):
    """tests _determine_coarse_fragment_factor() in soil_erosion.py"""
    observe = SoilErosion._determine_coarse_fragment_factor(percent_rock)
    expect = exp((-0.053) * percent_rock)
    assert observe == expect


@pytest.mark.parametrize("surface_runoff,peak_runoff_rate,field_area,erodibility_factor,cover_factor,practice_factor,"
                         "topographic_factor,fragment_factor", [
                             (10, 0.15, 1, 0.98, 0.79, 1, 0.88, 0.93),
                             (34.59648, 0.2139485, 3.2294823, 0.99, 0.784248, 0.109401, 0.728394, 0.6569382),
                             (18.91918429, 0.09184013, 0.8391984, 0.8729485473, 0.8192847, 0.7348924, 0.89717392,
                              0.459683)
                         ])
def test_determine_sediment_yield(surface_runoff, peak_runoff_rate, field_area, erodibility_factor, cover_factor,
                                  practice_factor, topographic_factor, fragment_factor):
    """tests _determine_sediment_yield() in soil_erosion.py"""
    observe = SoilErosion._determine_sediment_yield(surface_runoff, peak_runoff_rate, field_area, erodibility_factor,
                                                    cover_factor, practice_factor, topographic_factor, fragment_factor)
    expect = (11.8 * ((surface_runoff * peak_runoff_rate * field_area) ** 0.56) * erodibility_factor * cover_factor *
              practice_factor * topographic_factor * fragment_factor)
    assert observe == expect


# --- Integration tests ---
@pytest.mark.parametrize("min_cover_factor,residue", [
    (0.2, 800),
    (0.001, 500),
    (0.003, 80),
    (0.01, 0),
    (0.05, 928.948569),
])
def test_erode(min_cover_factor, residue):
    """tests that erode() properly calls methods and stores values"""

    # Initialize objects
    data = SoilData(accumulated_runoff=13, peak_runoff_rate=0.11)
    incorp = SoilErosion(data)

    # Mock helper function
    incorp._determine_soil_erodibility_factor = MagicMock(return_value=0.95)
    incorp._determine_cover_management_factor = MagicMock(return_value=0.95)
    incorp._determine_support_practice_factor = MagicMock(return_value=0.95)
    incorp._determine_topographic_factor = MagicMock(return_value=0.95)
    incorp._determine_coarse_fragment_factor = MagicMock(return_value=0.95)
    incorp._determine_sediment_yield = MagicMock(return_value=0.05)

    # Run method
    incorp.erode(min_cover_factor, residue)

    # Check everything
    incorp._determine_soil_erodibility_factor.assert_called_once()
    incorp._determine_cover_management_factor.assert_called_once()
    incorp._determine_support_practice_factor.assert_called_once()
    incorp._determine_topographic_factor.assert_called_once()
    incorp._determine_coarse_fragment_factor.assert_called_once()
    incorp._determine_sediment_yield.assert_called_once()
    assert incorp.data.eroded_sediment == 0.05

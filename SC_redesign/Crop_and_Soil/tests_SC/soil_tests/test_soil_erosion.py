import pytest
from math import exp
from unittest.mock import MagicMock

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

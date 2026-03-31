from math import atan, exp, log, sin
from unittest.mock import MagicMock, patch

import pytest

from RUFAS.general_constants import GeneralConstants
from RUFAS.biophysical.field.soil.soil_data import SoilData
from RUFAS.biophysical.field.soil.soil_erosion import SoilErosion


# --- Static method tests ---
@pytest.mark.parametrize(
    "sand,silt",
    [
        (0.15, 0.65),
        (0, 0),
        (0.17, 0.60),
        (0.09, 0.80),
        (0.12339485, 0.611938549),
        (0.234958769, 0.581093485),
    ],
)
def test_determine_coarse_sand_factor(sand: float, silt: float) -> None:
    """Tests _determine_coarse_sand_factor() in soil_erosion.py"""
    observe = SoilErosion._determine_coarse_sand_factor(sand, silt)
    expect_exp_term = exp((-0.256) * sand * 100 * (1 - (silt)))
    expect = 0.2 + 0.3 * expect_exp_term
    assert observe == expect


@pytest.mark.parametrize(
    "silt,clay",
    [
        (65, 20),
        (66.23948, 20.4958),
        (78.129348, 10.93845),
        (57.129485, 30.19485),
        (83.49482, 13.390458),
    ],
)
def test_determine_clay_silt_ratio_factor(silt: float, clay: float) -> None:
    """Tests _determine_clay_silt_ratio_factor() in soil_erosion.py"""
    observe = SoilErosion._determine_clay_silt_ratio_factor(silt, clay)
    expect = silt / (clay + silt)
    expect = expect**0.3
    assert observe == expect


def test_determine_clay_silt_ratio_factor_zero() -> None:
    """Tests the case when silt and clay are zero."""
    observed = SoilErosion._determine_clay_silt_ratio_factor(0, 0)
    assert observed == 1


@pytest.mark.parametrize(
    "carbon",
    [
        0.012,
        0,
        0.039124,
        0.0019485,
        0.029684,
        0.01395986,
    ],
)
def test_determine_carbon_content_factor(carbon: float) -> None:
    """Tests _determine_carbon_content_factor() in soil_erosion.py"""
    observe = SoilErosion._determine_carbon_content_factor(carbon)
    expect_bottom_term = carbon * GeneralConstants.FRACTION_TO_PERCENTAGE + exp(
        3.72 - 2.95 * carbon * GeneralConstants.FRACTION_TO_PERCENTAGE
    )
    expect = 1 - ((0.25 * carbon * GeneralConstants.FRACTION_TO_PERCENTAGE) / expect_bottom_term)
    assert observe == expect


@pytest.mark.parametrize(
    "sand",
    [
        0.15,
        0,
        0.235869348,
        0.351938403,
        0.76193850,
        0.8010039458,
        0.129498602,
        0.81019843912,
        0.41938402,
    ],
)
def test_determine_high_sand_factor(sand: float) -> None:
    """Tests _determine_high_sand_factor() in soil_erosion.py"""
    observe = SoilErosion._determine_high_sand_factor(sand)
    top_term = 0.7 * (1 - (sand))
    first_bottom_term = 1 - (sand)
    second_bottom_term = exp(-5.51 + 22.9 * first_bottom_term)
    expect = 1 - (top_term / (first_bottom_term + second_bottom_term))
    assert observe == expect


@pytest.mark.parametrize(
    "sand,silt,clay,carbon",
    [
        (15, 65, 22.5, 0.012),
        (14.2938495, 68.29285945, 15.1918492, 0.02395923),
        (10.4829458, 78.19128491, 17.1828402, 0.0300195829),
        (30.104958, 50.1918749, 25.1143534, 0.0123923984),
        (50, 30.1948591, 19.8939582, 0.01139495),
    ],
)
def test_determine_soil_erodibility_factor(sand: float, silt: float, clay: float, carbon: float) -> None:
    """Tests _determine_soil_erodibility_factor() in soil_erosion.py"""

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


@pytest.mark.parametrize(
    "min_cover,residue",
    [
        (0.2, 800),
        (0.001, 500),
        (0.003, 80),
        (0.01, 0),
        (0.05, 928.948569),
    ],
)
def test_determine_cover_management_factor(min_cover: float, residue: float) -> None:
    """Tests _determine_cover_management_factor() in soil_erosion.py"""
    observe = SoilErosion._determine_cover_management_factor(min_cover, residue)
    expect = exp((log(0.8) - log(min_cover)) * exp(-0.00115 * residue) + log(min_cover))
    assert observe == expect


@pytest.mark.parametrize("min_cover,residue", [(0, 0)])
def test_error_determine_cover_management_factor(min_cover: float, residue: float) -> None:
    """Tests that _determine_cover_management_factor() correctly raises error for invalid inputs"""
    with pytest.raises(Exception):
        SoilErosion._determine_cover_management_factor(min_cover, residue)


@pytest.mark.parametrize(
    "average_slope",
    [
        0.02,
        0,
        0.001,
        0.05,
        0.084595829,
        0.12593,
    ],
)
def test_determine_exponential_term(average_slope: float) -> None:
    """Tests _determine_exponential_term() in soil_erosion.py"""
    observe = SoilErosion._determine_exponential_term(average_slope)
    exp_term = exp(-35.835 * average_slope)
    expect = 0.6 * (1 - exp_term)
    assert observe == expect


@pytest.mark.parametrize(
    "length, avg_slope",
    [
        (3, 0.02),
        (0, 0),
        (16, 0.11),
        (19, 0.19),
        (1, 0.28),
        (8.194894, 0.089493),
    ],
)
def test_determine_topographic_factor(length: float, avg_slope: float) -> None:
    """Tests _determine_topographic_factor() in soil_erosion.py"""

    # Mock helper function
    SoilErosion._determine_exponential_term = MagicMock(return_value=0.45)

    # Run method
    observe = SoilErosion._determine_topographic_factor(length, avg_slope)

    # Calculate expected return value
    expect = ((length / 22.1) ** 0.45) * (65.41 * (sin(atan(avg_slope)) ** 2) + 4.56 * sin(atan(avg_slope)) + 0.065)

    # Check everything
    SoilErosion._determine_exponential_term.assert_called_with(avg_slope)
    assert observe == expect


@pytest.mark.parametrize(
    "rock_fraction",
    [
        0,
        0.005,
        0.002194,
        0.0019493,
        0.00492184949,
        0.010495492330,
    ],
)
def test_determine_coarse_fragment_factor(rock_fraction: float) -> None:
    """Tests _determine_coarse_fragment_factor() in soil_erosion.py"""
    observe = SoilErosion._determine_coarse_fragment_factor(rock_fraction)
    expect = exp((-0.053) * rock_fraction * 100)
    assert observe == expect


@pytest.mark.parametrize(
    "runoff,rainfall,length,manning,average,area,expected",
    [
        (4.3, 10.33, 58.9, 0.33, 34.5, 1.4, 0.00252778),
        (3.66, 7.2, 78.4, 0.58, 28.9, 2.7, 0.004875),
        (0.0, 0.0, 45.1, 0.488, 38.4, 0.9, 0.0),
    ],
)
def test_determine_peak_runoff_rate(
    runoff: float,
    rainfall: float,
    length: float,
    manning: float,
    average: float,
    area: float,
    expected: float,
) -> None:
    """Tests that the peak runoff rate is determined correctly."""
    with patch.multiple(
        "RUFAS.biophysical.field.soil.soil_erosion.SoilErosion",
        _determine_runoff_coefficient=MagicMock(return_value=0.5),
        _determine_rainfall_intensity=MagicMock(return_value=1.3),
    ):
        actual = SoilErosion._determine_peak_runoff_rate(runoff, rainfall, length, manning, average, area)
        assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "runoff,rainfall,expected",
    [(10.3, 12.1, 0.85123967), (5.5, 11.0, 0.5), (3.0, 9.0, 0.333333333)],
)
def test_determine_runoff_coefficient(runoff: float, rainfall: float, expected: float) -> None:
    """Tests that the correct runoff coefficient is calculated."""
    actual = SoilErosion._determine_runoff_coefficient(runoff, rainfall)
    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "rainfall,length,manning,average,expected",
    [(3.0, 60.0, 0.33, 18.2, 0.8), (11.2, 71.22, 0.441, 24.55, 2.98666667)],
)
def test_determine_rainfall_intensity(
    rainfall: float, length: float, manning: float, average: float, expected: float
) -> None:
    """Tests that the rainfall intensity is calculated accurately."""
    with patch.multiple(
        "RUFAS.biophysical.field.soil.soil_erosion.SoilErosion",
        _determine_time_of_concentration=MagicMock(return_value=1.5),
        _determine_half_hour_rainfall_fraction=MagicMock(return_value=0.3),
        _determine_fraction_rainfall_during_time_of_concentration=MagicMock(return_value=0.4),
    ):
        actual = SoilErosion._determine_rainfall_intensity(rainfall, length, manning, average)

        assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "slope,manning,average_slope",
    [(60.0, 0.4, 33.55), (15.66, 0.8, 14.5), (45.1, 0.4451, 20.22)],
)
def test_determine_time_of_concentration(slope: float, manning: float, average_slope: float) -> None:
    """Tests that the time of concentration is determined correctly."""
    expected = ((slope**0.6) * (manning**0.6)) / (18 * (average_slope**0.3))
    actual = SoilErosion._determine_time_of_concentration(slope, manning, average_slope)
    assert actual == expected


@pytest.mark.parametrize("rainfall", [1.1, 10.66, 0.0, 4.8])
def test_determine_half_hour_rainfall_fraction(rainfall: float) -> None:
    """Tests that the maximum half-hour rainfall fraction is calculated correctly."""
    expected = (0.02083 + (1 - exp(-125 / (rainfall + 5)))) / 2
    actual = SoilErosion._determine_half_hour_rainfall_fraction(rainfall)
    assert actual == expected


@pytest.mark.parametrize("concentration,rainfall_frac", [(3.5, 0.03), (1.44, 0.334), (8.67, 0.67)])
def test_fraction_rainfall_during_time_of_concentration(concentration: float, rainfall_frac: float) -> None:
    """Tests that the fraction of rainfall that fell during the time of concentration is calculated correctly."""
    expected = 1 - exp(2 * concentration * log(1 - rainfall_frac))
    actual = SoilErosion._determine_fraction_rainfall_during_time_of_concentration(concentration, rainfall_frac)
    assert actual == expected


@pytest.mark.parametrize(
    "surface_runoff,peak_runoff_rate,field_area,erodibility_factor,cover_factor,practice_factor,"
    "topographic_factor,fragment_factor",
    [
        (10, 0.15, 1, 0.98, 0.79, 1, 0.88, 0.93),
        (34.59648, 0.2139485, 3.2294823, 0.99, 0.784248, 0.109401, 0.728394, 0.6569382),
        (
            18.91918429,
            0.09184013,
            0.8391984,
            0.8729485473,
            0.8192847,
            0.7348924,
            0.89717392,
            0.459683,
        ),
    ],
)
def test_determine_sediment_yield(
    surface_runoff: float,
    peak_runoff_rate: float,
    field_area: float,
    erodibility_factor: float,
    cover_factor: float,
    practice_factor: float,
    topographic_factor: float,
    fragment_factor: float,
) -> None:
    """Tests _determine_sediment_yield() in soil_erosion.py"""
    observe = SoilErosion._determine_sediment_yield(
        surface_runoff,
        peak_runoff_rate,
        field_area,
        erodibility_factor,
        cover_factor,
        practice_factor,
        topographic_factor,
        fragment_factor,
    )
    expect = (
        11.8
        * ((surface_runoff * peak_runoff_rate * field_area) ** 0.56)
        * erodibility_factor
        * cover_factor
        * practice_factor
        * topographic_factor
        * fragment_factor
    )
    assert observe == expect


@pytest.mark.parametrize(
    "sediment_yield,snow_content",
    [
        (0.015, 1),
        (0.03, 3),
        (0.029385473, 2.49381),
        (0.108481, 6.193943),
    ],
)
def test_determine_adjusted_sediment_yield(sediment_yield: float, snow_content: float) -> float:
    """Tests _determine_adjusted_sediment_yield() in soil_erosion.py"""
    observe = SoilErosion._determine_adjusted_sediment_yield(sediment_yield, snow_content)
    expect = sediment_yield / exp(3 * snow_content / 25.4)
    assert observe == expect


# --- Integration tests ---
@pytest.mark.parametrize(
    "field_size,min_cover_factor,residue,rainfall,accumulated_runoff,should_fail",
    [
        (1, 0.2, 800, 10.2, 13, False),
        (3, 0.001, 500, 3.6, 13, False),
        (4.69, 0.003, 80, 6.77, 13, False),
        (0.891, 0.01, 0, 0.0, 13, False),
        (0.956, 0.05, 928.948569, 15.9, 13, False),
        (1, 0.2, 800, 10.2, None, True),
    ],
)
def test_erode(
    field_size: float,
    min_cover_factor: float,
    residue: float,
    rainfall: float,
    should_fail: bool,
    accumulated_runoff: float,
) -> None:
    """Tests that erode() properly calls methods and stores values"""

    # Initialize objects
    data = SoilData(accumulated_runoff=accumulated_runoff, field_size=1.33)
    incorp = SoilErosion(data)

    # Mock helper function
    incorp._determine_soil_erodibility_factor = MagicMock(return_value=0.87)
    incorp._determine_cover_management_factor = MagicMock(return_value=0.95)
    incorp._determine_support_practice_factor = MagicMock(return_value=0.98)
    incorp._determine_topographic_factor = MagicMock(return_value=0.79)
    incorp._determine_coarse_fragment_factor = MagicMock(return_value=0.91)
    incorp._determine_peak_runoff_rate = MagicMock(return_value=0.15)
    incorp._determine_sediment_yield = MagicMock(return_value=0.05)
    incorp._determine_adjusted_sediment_yield = MagicMock(return_value=0.0498)
    if should_fail:
        with pytest.raises(TypeError) as e:
            incorp.erode(field_size, min_cover_factor, residue, rainfall)
            assert str(e) == "SoilData accumulated_runoff cannot be NoneType"
    else:
        # Run method
        incorp.erode(field_size, min_cover_factor, residue, rainfall)

        # Check everything
        incorp._determine_soil_erodibility_factor.assert_called_once()
        incorp._determine_cover_management_factor.assert_called_once()
        incorp._determine_support_practice_factor.assert_called_once()
        incorp._determine_topographic_factor.assert_called_once()
        incorp._determine_coarse_fragment_factor.assert_called_once()
        incorp._determine_peak_runoff_rate.assert_called_once()
        incorp._determine_sediment_yield.assert_called_once()
        incorp._determine_adjusted_sediment_yield.assert_called_once()
        assert incorp.data.eroded_sediment == 0.0498
        assert incorp.data.annual_eroded_sediment_total == 0.0498
        assert incorp.data.surface_runoff_volume == incorp.data.accumulated_runoff / field_size
        assert incorp.data.annual_surface_runoff_total == incorp.data.accumulated_runoff / field_size


def test_determine_support_practice_factor() -> None:
    """Test that the support factor is returned correctly"""
    data = SoilData(accumulated_runoff=13, field_size=1.33)
    erosion = SoilErosion(data, field_size=0.65)
    assert erosion._determine_support_practice_factor() == 1

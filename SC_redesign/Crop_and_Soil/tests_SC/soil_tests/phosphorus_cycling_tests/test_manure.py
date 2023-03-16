import pytest
from math import exp, sqrt

from SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.manure import Manure


# --- Static Method tests ---
@pytest.mark.parametrize("avg_air_temp", [
    10,
    33,
    0,
    -14,
    18.34580983290,
])
def test_determine_temperature_factor(avg_air_temp: float) -> None:
    """Tests that the temperature factor is correctly calculated and bounded."""
    observe = Manure._determine_temperature_factor(avg_air_temp)
    expect = min(1, max(0, (2 * 32 ** 2 * avg_air_temp ** 2 - avg_air_temp ** 4) / 32 ** 4))
    assert observe == expect


@pytest.mark.parametrize("temp_factor", [
    0.0,
    1.0,
    0.4,
    0.8884959312,
])
def test_determine_dry_matter_decomposition_rate(temp_factor: float) -> None:
    """Tests that the dry matter decomposition rate is calculated correctly for a given day."""
    observe = Manure._determine_dry_matter_decomposition_rate(temp_factor)
    expect = 0.003 * temp_factor ** 0.5
    assert observe == expect


@pytest.mark.parametrize("moisture,temp_factor,area,is_dung", [
    [0.4, 0.3, 1, False],
    [0.8, 0.1, 3.18, True],
    [0.2, 0.187, 2.854, False],
    [0.552, 0.87, 0.875, True],
])
def test_determine_dry_manure_matter_assimilation(moisture: float, temp_factor: float, area: float,
                                                  is_dung: bool) -> None:
    """Tests that the correct amount of manure dry matter is assimilated into the soil on a given day is calculated
        correctly.
    """
    observe = Manure._determine_dry_manure_matter_assimilation(moisture, temp_factor, area, is_dung)
    if is_dung:
        expect = (30 * exp(3.5 * sqrt(moisture)) * (temp_factor ** 0.1) * area)
    else:
        expect = (30 * exp(2.5 * moisture)) * temp_factor * area
    assert observe == expect


@pytest.mark.parametrize("rate,temp,moisture", [
    (0.01, 0.83, 0.67),
    (0.1, 0.78, 0.85),
    (0.0025, 0.43, 0.77),
    (0.01, 0.66, 0.66),
])
def test_determine_mineralization_rate(rate: float, temp: float, moisture: float) -> float:
    """Tests that the correct rate of mineralization is determined for a specific pool of phosphorus on a given day."""
    observe = Manure._determine_mineralization_rate(rate, temp, moisture)
    if temp <= moisture:
        expect = rate * temp
    else:
        expect = rate * moisture
    assert observe == expect


@pytest.mark.parametrize("rain,moisture,current_mass,original_mass,temp_factor", [
    (0.8, 0.7, 35, 80, 0.7),            # Moisture decreases
    (0.2, 0.0, 45, 150, 0.95),          # Moisture decreases
    (1.0, 0.4, 22, 87, 0.684),          # No moisture change
    (3.99, 0.81, 76, 100, 0.182),       # No moisture change
    (4.0, 0.44, 28.47, 50, 0.12),       # No moisture change
    (5.6, 0.78, 35.673, 60, 0.081),     # Moisture increases
    (7.8, .087, 97, 140, 0.345),        # Moisture increases
])
def test_determine_moisture_change(rain: float, moisture: float, current_mass: float, original_mass: float,
                                   temp_factor: float) -> None:
    """Tests that the correct change in the moisture factor of an application of manure is calculated on a given day."""
    observe = Manure._determine_moisture_change(rain, moisture, current_mass, original_mass, temp_factor)
    if rain < 1:
        expect = -1 * (-0.05 * (current_mass / original_mass) + 0.075) * temp_factor
    elif 1.0 <= rain <= 4.0:
        expect = 0
    else:
        expect = (-0.3 * moisture) + 0.27
    assert observe == expect


@pytest.mark.parametrize("rain,manure_mass,manure_coverage", [
    (13, 300, 3),
    (5, 30, 1.8),
    (3.881993, 86.24832, 2.3948),
])
def test_determine_rain_manure_dry_matter_ratio(rain: float, manure_mass: float, manure_coverage: float) -> float:
    """Tests that the ratio of rain to manure is calculated correctly."""
    observe = Manure._determine_rain_manure_dry_matter_ratio(rain, manure_mass, manure_coverage)
    expect = rain / manure_mass * manure_coverage * 10_000
    assert observe == expect


@pytest.mark.parametrize("rain,runoff", [
    (13, 0),
    (11, 3),
    (10, 10),
])
def test_determine_phosphorus_dissolved_factor(rain: float, runoff: float) -> None:
    """Tests that the adjusted ratio of rainfall to runoff is calculated correctly"""
    observe = Manure._determine_phosphorus_dissolved_factor(rain, runoff)
    expect = (runoff / rain) ** 0.225
    assert observe == expect

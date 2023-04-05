import pytest
from math import exp, sqrt
from unittest.mock import patch, MagicMock, PropertyMock

from SC_redesign.Crop_and_Soil.crop_and_soil_constants import HECTARES_TO_SQUARE_MILLIMETERS, \
    CUBIC_MILLIMETERS_TO_LITERS, MILLIGRAMS_TO_KILOGRAMS
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
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


@pytest.mark.parametrize("manure,rain_manure_ratio,is_cow", [
    (300, 1300, True),
    (255, 1234, False),
])
def test_determine_water_extractable_inorganic_phosphorus_leached(manure: float, rain_manure_ratio: float,
                                                                  is_cow: bool) -> None:
    """Tests that the correct mass of water extractable inorganic phosphorus leached is calculated."""
    observe = Manure._determine_water_extractable_inorganic_phosphorus_leached(manure, rain_manure_ratio, is_cow)
    if is_cow:
        expect = min(1.0, (1.2 * rain_manure_ratio) / (rain_manure_ratio + 73.1)) * manure
    else:
        expect = min(1.0, (2.2 * rain_manure_ratio) / (rain_manure_ratio + 300.1)) * manure
    expect = max(0, expect)
    assert observe == expect


@pytest.mark.parametrize("manure,rain_manure_ratio,is_cow", [
    (300, 1300, True),
    (255, 1234, False),
])
def test_determine_water_extractable_organic_phosphorus_leached(manure: float, rain_manure_ratio: float,
                                                                is_cow: bool) -> None:
    """Tests that the correct mass of water extractable organic phosphorus leached is calculated."""
    Manure._determine_water_extractable_inorganic_phosphorus_leached = MagicMock(return_value=50)
    observe = Manure._determine_water_extractable_organic_phosphorus_leached(manure, rain_manure_ratio, is_cow)
    expect = 50 / 0.6
    Manure._determine_water_extractable_inorganic_phosphorus_leached.assert_called_once_with(manure, rain_manure_ratio,
                                                                                             is_cow)
    assert observe == expect


@pytest.mark.parametrize("rain,runoff", [
    (13, 0),
    (11, 3),
    (10, 10),
])
def test_determine_phosphorus_distribution_factor(rain: float, runoff: float) -> None:
    """Tests that the adjusted ratio of rainfall to runoff is calculated correctly."""
    observe = Manure._determine_phosphorus_distribution_factor(rain, runoff)
    expect = (runoff / rain) ** 0.225
    assert observe == expect


@pytest.mark.parametrize("manure,rain,field_size,distribution_factor", [
    (23, 11, 3.1, 0.8743),
    (58.67143, 7.183, 0.981, 0.69982),
    (147.1892, 4.867, 1.875, 0.1984),
    (87.92734, 6.839, 2.385, 1.0),
    (101.29482, 9.29583, 3.4918, 0.0),
])
def test_determine_water_extractable_phosphorus_runoff_concentration(manure: float, rain: float, field_size: float,
                                                                     distribution_factor: float) -> None:
    """Tests that the concentration of water extractable phosphorus in runoff is calculated correctly based on manure
        leached, amount of rainfall, area of the field, and the ratio of runoff to rainfall."""
    observe = Manure._determine_water_extractable_phosphorus_runoff_concentration(manure, rain, field_size,
                                                                                  distribution_factor)
    expect = manure / rain * (1 / field_size) * 100 * distribution_factor
    assert pytest.approx(observe) == expect


# --- Helper method tests ---
@pytest.mark.parametrize("amount_phosphorus,field_size", [
    (100, 3.1),
    (25.6, 2),
    (66.23, 1.88),
])
def test_add_infiltrated_phosphorus_to_soil(amount_phosphorus: float, field_size: float) -> None:
    """Test that methods are called correctly on correct layers of soil profile."""
    data = SoilData()
    incorp = Manure(data)
    with patch("SC_redesign.Crop_and_Soil.soil.layer_data.LayerData.add_to_labile_phosphorus",
               new_callable=PropertyMock) as mocked_add_to_labile_phosphorus:
        incorp._add_infiltrated_phosphorus_to_soil(amount_phosphorus, field_size)
        assert mocked_add_to_labile_phosphorus.call_count == 2


@pytest.mark.parametrize("rain,runoff,area,manure_mass,field_coverage,phosphorus_mass,organic", [
    (11, 3, 1.8, 800, 0.7, 120, True),
    (14, 1.8, 3.1, 950, 0.91, 133, False),
    (9.1, 2.7, 2.2, 993, 0.88, 86, True),
    (10.11, 4.1, 2.8, 1234, 0.9655, 200, False),
    (14, 13, 2.0, 20, 0.12, 1.4, False),
    (9.8, 9.1, 2, 36, 0.28, 2.1, True),
    (6.2, 0.0, 2.3, 500, 0.65, 80, False),
])
def test_leach_phosphorus_to_runoff(rain: float, runoff: float, area: float, manure_mass: float, field_coverage: float,
                                    phosphorus_mass: float, organic: bool) -> None:
    """Test that leaching phosphorus calls all the correct functions and calculates the masses of phosphorus lost
        correctly."""
    Manure._determine_rain_manure_dry_matter_ratio = MagicMock(return_value=0.4)
    Manure._determine_phosphorus_distribution_factor = MagicMock(return_value=1.2)
    Manure._determine_water_extractable_organic_phosphorus_leached = MagicMock(return_value=25)
    Manure._determine_water_extractable_inorganic_phosphorus_leached = MagicMock(return_value=25)
    Manure._determine_water_extractable_phosphorus_runoff_concentration = MagicMock(return_value=5)

    observed = Manure._leach_phosphorus_to_runoff(rain, runoff, area, manure_mass, field_coverage, phosphorus_mass,
                                                  organic)
    runoff_in_liters = runoff * area * HECTARES_TO_SQUARE_MILLIMETERS * CUBIC_MILLIMETERS_TO_LITERS
    expected_water_extractable_phosphorus_leached = min(25, phosphorus_mass)
    expected_runoff_phosphorus_in_kg = 5 * runoff_in_liters * MILLIGRAMS_TO_KILOGRAMS
    expected_infiltrated_phosphorus = max(0, expected_water_extractable_phosphorus_leached
                                          - expected_runoff_phosphorus_in_kg)

    Manure._determine_rain_manure_dry_matter_ratio.assert_called_once_with(rain, manure_mass, field_coverage)
    Manure._determine_phosphorus_distribution_factor.assert_called_once_with(rain, runoff)
    if organic:
        Manure._determine_water_extractable_organic_phosphorus_leached.assert_called_once_with(phosphorus_mass, 0.4,
                                                                                               True)
        Manure._determine_water_extractable_inorganic_phosphorus_leached.assert_not_called()
    else:
        Manure._determine_water_extractable_organic_phosphorus_leached.assert_not_called()
        Manure._determine_water_extractable_inorganic_phosphorus_leached.assert_called_once_with(phosphorus_mass, 0.4,
                                                                                                 True)
    Manure._determine_water_extractable_phosphorus_runoff_concentration.assert_called_once_with(
        expected_water_extractable_phosphorus_leached, rain, area, 1.2)
    assert observed["new_phosphorus_pool_amount"] == (phosphorus_mass - expected_water_extractable_phosphorus_leached)
    assert observed["infiltrated_phosphorus"] == expected_infiltrated_phosphorus
    assert observed["runoff_phosphorus"] == expected_runoff_phosphorus_in_kg

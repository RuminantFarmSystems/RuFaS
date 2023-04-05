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


@pytest.mark.parametrize("rain,runoff,area,machine,organic", [
    (11, 3, 1.8, True, True),           # Machine-applied organic manure
    (14, 1.8, 3.1, True, False),        # Machine-applied inorganic manure
    (9.1, 2.7, 2.2, False, True),       # Grazer-applied organic manure
    (10.11, 4.1, 2.8, False, False),    # Grazer-applied inorganic manure
])
def test_leach_phosphorus_to_runoff(rain: float, runoff: float, area: float, machine: bool, organic: bool) -> None:
    """Test that leaching phosphorus calls all the correct functions and sets right attributes to right values."""
    machine_organic = machine and organic
    machine_inorganic = machine and not organic
    grazer_organic = not machine and organic

    data = SoilData(machine_manure_dry_mass=800,
                    machine_manure_field_coverage=0.8,
                    machine_water_extractable_organic_phosphorus=100,
                    machine_water_extractable_inorganic_phosphorus=200,
                    grazing_manure_dry_mass=900,
                    grazing_manure_field_coverage=0.9,
                    grazing_water_extractable_organic_phosphorus=120,
                    grazing_water_extractable_inorganic_phosphorus=220)
    incorp = Manure(data)

    incorp._determine_rain_manure_dry_matter_ratio = MagicMock(return_value=0.4)
    incorp._determine_distribution_factor = MagicMock(return_value=1.1)
    incorp._determine_phosphorus_distribution_factor = MagicMock(return_value=1.2)
    incorp._determine_water_extractable_organic_phosphorus_leached = MagicMock(return_value=25)
    incorp._determine_water_extractable_inorganic_phosphorus_leached = MagicMock(return_value=25)
    incorp._determine_water_extractable_phosphorus_runoff_concentration = MagicMock(return_value=5)
    incorp._add_infiltrated_phosphorus_to_soil = MagicMock()

    incorp._leach_phosphorus_to_runoff(rain, runoff, area, machine, organic)
    runoff_in_liters = runoff * area * HECTARES_TO_SQUARE_MILLIMETERS * CUBIC_MILLIMETERS_TO_LITERS
    expected_runoff_phosphorus_in_kg = 5 * runoff_in_liters * MILLIGRAMS_TO_KILOGRAMS
    expected_infiltrated_phosphorus = max(0, 25 - expected_runoff_phosphorus_in_kg)

    if machine:
        incorp._determine_rain_manure_dry_matter_ratio.assert_called_once_with(rain, 800, 0.8)
    else:
        incorp._determine_rain_manure_dry_matter_ratio.assert_called_once_with(rain, 900, 0.9)
    incorp._determine_phosphorus_distribution_factor.assert_called_once_with(rain, runoff)
    if machine_organic:
        incorp._determine_water_extractable_organic_phosphorus_leached.assert_called_once_with(100, 0.4, True)
        assert incorp._determine_water_extractable_inorganic_phosphorus_leached.call_count == 0
        assert incorp.data.machine_water_extractable_organic_phosphorus == 75
        assert incorp.data.annual_runoff_machine_manure_organic_phosphorus == expected_runoff_phosphorus_in_kg
    elif machine_inorganic:
        incorp._determine_water_extractable_inorganic_phosphorus_leached.assert_called_once_with(200, 0.4, True)
        assert incorp._determine_water_extractable_organic_phosphorus_leached.call_count == 0
        assert incorp.data.machine_water_extractable_inorganic_phosphorus == 175
        assert incorp.data.annual_runoff_machine_manure_inorganic_phosphorus == expected_runoff_phosphorus_in_kg
    elif grazer_organic:
        incorp._determine_water_extractable_organic_phosphorus_leached.assert_called_once_with(120, 0.4, True)
        assert incorp._determine_water_extractable_inorganic_phosphorus_leached.call_count == 0
        assert incorp.data.grazing_water_extractable_organic_phosphorus == 95
        assert incorp.data.annual_runoff_grazing_manure_organic_phosphorus == expected_runoff_phosphorus_in_kg
    else:
        incorp._determine_water_extractable_inorganic_phosphorus_leached.assert_called_once_with(220, 0.4, True)
        assert incorp._determine_water_extractable_organic_phosphorus_leached.call_count == 0
        assert incorp.data.grazing_water_extractable_inorganic_phosphorus == 195
        assert incorp.data.annual_runoff_grazing_manure_inorganic_phosphorus == expected_runoff_phosphorus_in_kg
    incorp._determine_water_extractable_phosphorus_runoff_concentration.assert_called_once_with(25, rain, area, 1.2)
    incorp._add_infiltrated_phosphorus_to_soil.assert_called_once_with(expected_infiltrated_phosphorus, area)

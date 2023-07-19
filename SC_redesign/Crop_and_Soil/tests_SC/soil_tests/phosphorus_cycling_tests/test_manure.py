import pytest
from math import exp, sqrt
from unittest.mock import patch, call, MagicMock, PropertyMock

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


@pytest.mark.parametrize("rain,moisture,current_mass,original_mass,temp_factor", [
    (0.8, 0.7, 35, 80, 0.7),  # Moisture decreases
    (0.2, 0.0, 45, 150, 0.95),  # Moisture decreases
    (1.0, 0.4, 22, 87, 0.684),  # No moisture change
    (3.99, 0.81, 76, 100, 0.182),  # No moisture change
    (4.0, 0.44, 28.47, 50, 0.12),  # No moisture change
    (5.6, 0.78, 35.673, 60, 0.081),  # Moisture increases
    (7.8, .087, 97, 140, 0.345),  # Moisture increases
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


@pytest.mark.parametrize("rain,runoff,area,manure_mass,field_coverage,phosphorus_mass,organic", [
    (11, 3, 1.8, 800, 0.7, 120, True),
    (14, 1.8, 3.1, 950, 0.91, 133, False),
    (9.1, 2.7, 2.2, 993, 0.88, 86, True),
    (10.11, 4.1, 2.8, 1234, 0.9655, 200, False),
    (14, 13, 2.0, 20, 0.12, 1.4, False),
    (9.8, 9.1, 2, 36, 0.28, 2.1, True),
    (6.2, 0.0, 2.3, 500, 0.65, 80, False),
])
def test_determine_phosphorus_leached_from_surface(rain: float, runoff: float, area: float, manure_mass: float,
                                                   field_coverage: float, phosphorus_mass: float,
                                                   organic: bool) -> None:
    """Test that subroutines are called correctly and that leached phosphorus amounts are calculated correctly."""
    Manure._determine_rain_manure_dry_matter_ratio = MagicMock(return_value=0.4)
    Manure._determine_phosphorus_distribution_factor = MagicMock(return_value=1.2)
    Manure._determine_water_extractable_organic_phosphorus_leached = MagicMock(return_value=25.0)
    Manure._determine_water_extractable_inorganic_phosphorus_leached = MagicMock(return_value=25.0)
    Manure._determine_water_extractable_phosphorus_runoff_concentration = MagicMock(return_value=5)

    observed = Manure._determine_phosphorus_leached_from_surface(rain, runoff, area, manure_mass, field_coverage,
                                                                 phosphorus_mass, organic)
    runoff_in_liters = runoff * area * HECTARES_TO_SQUARE_MILLIMETERS * CUBIC_MILLIMETERS_TO_LITERS
    expected_covered_area = area * field_coverage
    expected_water_extractable_phosphorus_leached = min(25.0, phosphorus_mass)
    expected_runoff_phosphorus_in_kg = 5 * runoff_in_liters * MILLIGRAMS_TO_KILOGRAMS
    expected_infiltrated_phosphorus = max(0, expected_water_extractable_phosphorus_leached
                                          - expected_runoff_phosphorus_in_kg)

    Manure._determine_rain_manure_dry_matter_ratio.assert_called_once_with(rain, manure_mass, expected_covered_area)
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


@pytest.mark.parametrize("phosphorus,rate,temp_factor,moisture_factor", [
    (25, 0.1, 0.33, 0.55),
    (33, 0.01, 0.65, 0.78),
    (21, 0.0025, 0.3423, 0.7768),
    (0, 0.01, 0.012, 0.23),
    (23, 0.0025, -0.13, 0.332),
    (41, 0.1, -0.19, 0.0),
])
def test_determine_mineralized_surface_phosphorus(phosphorus: float, rate: float, temp_factor: float,
                                                  moisture_factor: float) -> None:
    """Tests that the correct amount of mineralized phosphorus is calculated."""
    observed = Manure._determine_mineralized_surface_phosphorus(phosphorus, rate, temp_factor, moisture_factor)
    expected = min(phosphorus, max(0.0, phosphorus * rate * min(temp_factor, moisture_factor)))
    assert observed == expected


@pytest.mark.parametrize("ratio,phosphorus", [
    (0.88, 26),
    (0.212, 12.13),
    (0.0, 30.21),
    (0.441, 0.0),
    (0.0, 0.0),
])
def test_determine_assimilated_phosphorus_amount(ratio: float, phosphorus: float) -> None:
    """Tests that the correct amount of phosphorus assimilated into the soil is calculated."""
    observed = Manure._determine_assimilated_phosphorus_amount(ratio, phosphorus)
    expected = max(0.0, ratio * phosphorus)
    expected = min(phosphorus, expected)
    assert observed == expected


# --- Helper method tests ---
@pytest.mark.parametrize("amount_phosphorus,field_size", [
    (100, 3.1),
    (25.6, 2),
    (66.23, 1.88),
])
def test_add_infiltrated_phosphorus_to_soil(amount_phosphorus: float, field_size: float) -> None:
    """Test that methods are called correctly on correct layers of soil profile."""
    data = SoilData(field_size=field_size)
    incorp = Manure(data)
    with patch("SC_redesign.Crop_and_Soil.soil.layer_data.LayerData.add_to_labile_phosphorus",
               new_callable=PropertyMock) as mocked_add_to_labile_phosphorus:
        incorp._add_infiltrated_phosphorus_to_soil(amount_phosphorus, field_size)
        assert mocked_add_to_labile_phosphorus.call_count == 2


@pytest.mark.parametrize("rain,runoff,area", [
    (13, 4, 1.8),
    (12, 1.8, 2.1),
    (14, 12.2, 3.4),
    (4.2, 0, 2.4),
])
def test_leach_and_update_phosphorus_pools(rain: float, runoff: float, area: float) -> None:
    """Tests that the update subroutine for phosphorus pools in Manure correctly calls methods and sets attributes."""
    data = SoilData(machine_manure_dry_mass=1000, machine_manure_field_coverage=0.86, field_size=area,
                    machine_water_extractable_inorganic_phosphorus=200, machine_water_extractable_organic_phosphorus=90,
                    grazing_manure_dry_mass=800, grazing_manure_field_coverage=0.78,
                    grazing_water_extractable_inorganic_phosphorus=125, grazing_water_extractable_organic_phosphorus=70)
    incorp = Manure(data)

    incorp._determine_phosphorus_leached_from_surface = MagicMock(return_value={
        "new_phosphorus_pool_amount": 30,
        "infiltrated_phosphorus": 25,
        "runoff_phosphorus": 20,
    })
    incorp._add_infiltrated_phosphorus_to_soil = MagicMock()

    incorp._leach_and_update_phosphorus_pools(rain, runoff, area)

    leached_calls = [call(rain, runoff, area, 1000, 0.86, 90, True), call(rain, runoff, area, 1000, 0.86, 200, False),
                     call(rain, runoff, area, 800, 0.78, 70, True), call(rain, runoff, area, 800, 0.78, 125, False)]
    incorp._determine_phosphorus_leached_from_surface.assert_has_calls(leached_calls)
    infiltrated_calls = [call(25, area), call(25, area), call(25, area), call(25, area)]
    incorp._add_infiltrated_phosphorus_to_soil.assert_has_calls(infiltrated_calls)
    assert incorp.data.machine_water_extractable_organic_phosphorus == 30
    assert incorp.data.machine_water_extractable_inorganic_phosphorus == 30
    assert incorp.data.annual_runoff_machine_manure_organic_phosphorus == 20
    assert incorp.data.annual_runoff_machine_manure_inorganic_phosphorus == 20
    assert incorp.data.grazing_water_extractable_organic_phosphorus == 30
    assert incorp.data.grazing_water_extractable_inorganic_phosphorus == 30
    assert incorp.data.annual_runoff_grazing_manure_organic_phosphorus == 20
    assert incorp.data.annual_runoff_grazing_manure_inorganic_phosphorus == 20


@pytest.mark.parametrize("rain,temp_factor", [
    (10, 0.35),
    (4, 0.4413),
    (16, 0.121),
])
def test_adjust_manure_moisture_factor(rain: float, temp_factor: float) -> None:
    """Tests that the manure moisture factors of the different pools are correctly updated."""
    # Case 1: calculated moisture factor is negative
    with patch("SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.manure.Manure._determine_moisture_change",
               new_callable=MagicMock, return_value=-1.0) as mocked_determine_moisture_change:
        data1 = SoilData(machine_manure_dry_mass=1000, machine_manure_field_coverage=0.86,
                         machine_manure_moisture_factor=0.5, machine_manure_applied_mass=1100,
                         grazing_manure_dry_mass=800, grazing_manure_field_coverage=0.76,
                         grazing_manure_moisture_factor=0.6, grazing_manure_applied_mass=900,
                         field_size=1.1)
        incorp1 = Manure(data1)

        incorp1._adjust_manure_moisture_factor(rain, temp_factor)

        moisture_change_calls = [call(rain, 0.5, 1000, 1100, temp_factor), call(rain, 0.6, 800, 900, temp_factor)]
        mocked_determine_moisture_change.assert_has_calls(moisture_change_calls)
        assert incorp1.data.machine_manure_moisture_factor == 0.0
        assert incorp1.data.grazing_manure_moisture_factor == 0.0

    # Case 2: calculated moisture factor is greater than upper bound
    with patch("SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.manure.Manure._determine_moisture_change",
               new_callable=MagicMock, return_value=1.0) as mocked_determine_moisture_change:
        data2 = SoilData(machine_manure_dry_mass=1000, machine_manure_field_coverage=0.86,
                         machine_manure_moisture_factor=0.5, machine_manure_applied_mass=1100,
                         grazing_manure_dry_mass=800, grazing_manure_field_coverage=0.76,
                         grazing_manure_moisture_factor=0.6, grazing_manure_applied_mass=900, field_size=1.1)
        incorp2 = Manure(data2)

        incorp2._adjust_manure_moisture_factor(rain, temp_factor)

        moisture_change_calls = [call(rain, 0.5, 1000, 1100, temp_factor), call(rain, 0.6, 800, 900, temp_factor)]
        mocked_determine_moisture_change.assert_has_calls(moisture_change_calls)
        assert incorp2.data.machine_manure_moisture_factor == 0.9
        assert incorp2.data.grazing_manure_moisture_factor == 0.9

    # Case 3: calculated moisture factor is not reset due to being out of bounds
    with patch("SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.manure.Manure._determine_moisture_change",
               new_callable=MagicMock, return_value=0.1) as mocked_determine_moisture_change:
        data3 = SoilData(machine_manure_dry_mass=1000, machine_manure_field_coverage=0.86,
                         machine_manure_moisture_factor=0.5, machine_manure_applied_mass=1100,
                         grazing_manure_dry_mass=800, grazing_manure_field_coverage=0.76,
                         grazing_manure_moisture_factor=0.6, grazing_manure_applied_mass=900, field_size=1.1)
        incorp3 = Manure(data3)

        incorp3._adjust_manure_moisture_factor(rain, temp_factor)

        moisture_change_calls = [call(rain, 0.5, 1000, 1100, temp_factor), call(rain, 0.6, 800, 900, temp_factor)]
        mocked_determine_moisture_change.assert_has_calls(moisture_change_calls)
        assert incorp3.data.machine_manure_moisture_factor == 0.6
        assert incorp3.data.grazing_manure_moisture_factor == 0.7


@pytest.mark.parametrize("temp_factor,machine_mass,machine_coverage,grazing_mass,grazing_field", [
    (0.45, 800, 0.85, 500, 0.44),
    (0.66, 900, 0.92, 450, 0.38),
    (0.12, 43, 0.07, 88, 0.11),
    (0.33, 3, 0.02, 120, 0.33),
])
def test_determine_decomposed_surface_manure(temp_factor: float, machine_mass: float, machine_coverage: float,
                                             grazing_mass: float, grazing_field: float) -> None:
    """Tests that the correct changes in mass and field coverage of machine and grazer applied manure are calculated."""
    data = SoilData(machine_manure_dry_mass=800, machine_manure_field_coverage=0.85, grazing_manure_dry_mass=500,
                    grazing_manure_field_coverage=0.44, field_size=1.1)
    incorp = Manure(data)

    incorp._determine_dry_matter_decomposition_rate = MagicMock(return_value=0.5)

    observed = incorp._determine_decomposed_surface_manure(temp_factor)

    expected_machine_mass_decomp = min(max(0.0, incorp.data.machine_manure_dry_mass * 0.5),
                                       incorp.data.machine_manure_dry_mass)
    expected_machine_coverage_decomp = min(max(0.0, expected_machine_mass_decomp / incorp.data.machine_manure_dry_mass *
                                               incorp.data.machine_manure_field_coverage),
                                           incorp.data.machine_manure_field_coverage)
    expected_grazing_mass_decomp = min(max(0.0, incorp.data.grazing_manure_dry_mass * 0.5),
                                       incorp.data.grazing_manure_dry_mass)
    expected_grazing_coverage_decomp = min(max(0.0, expected_grazing_mass_decomp / incorp.data.grazing_manure_dry_mass *
                                               incorp.data.grazing_manure_field_coverage),
                                           incorp.data.grazing_manure_field_coverage)

    incorp._determine_dry_matter_decomposition_rate.assert_called_once_with(temp_factor)
    assert observed["decomposed_machine_manure_mass_change"] == expected_machine_mass_decomp
    assert observed["decomposed_machine_manure_coverage_change"] == expected_machine_coverage_decomp
    assert observed["decomposed_grazing_manure_mass_change"] == expected_grazing_mass_decomp
    assert observed["decomposed_grazing_manure_coverage_change"] == expected_grazing_coverage_decomp


@pytest.mark.parametrize("temp_factor,area", [
    (0.44, 1.89),
    (0.3223, 2.45),
    (0.661, 1.23),
])
def test_determine_assimilated_surface_manure(temp_factor: float, area: float) -> None:
    """Tests that correct decrease in manure and field coverage due to assimilation are calculated."""
    # Case 1: no manure in the pools
    data1 = SoilData(field_size=1.1)
    incorp1 = Manure(data1)
    incorp1._determine_dry_manure_matter_assimilation = MagicMock()

    observed1 = incorp1._determine_assimilated_surface_manure(temp_factor, area)
    expected1 = {"assimilated_machine_manure": 0, "machine_manure_coverage": 0, "assimilated_grazing_manure": 0,
                 "grazing_manure_coverage": 0}

    incorp1._determine_dry_manure_matter_assimilation.assert_not_called()
    assert observed1 == expected1

    # Case 2: manure in pools, not fully assimilated
    data2 = SoilData(machine_manure_dry_mass=100, machine_manure_field_coverage=0.55,
                     machine_manure_moisture_factor=0.77, grazing_manure_dry_mass=80,
                     grazing_manure_field_coverage=0.4, grazing_manure_moisture_factor=0.83, field_size=1.1)
    incorp2 = Manure(data2)
    incorp2._determine_dry_manure_matter_assimilation = MagicMock(return_value=25)

    observed2 = incorp2._determine_assimilated_surface_manure(temp_factor, area)
    expected_machine_cover_area2 = area * 0.55
    expected_grazing_cover_area2 = area * 0.4
    expected_machine_coverage2 = min(0.55, max(25 / 100 * 0.55, 0.0))
    expected_grazing_coverage2 = min(0.4, max(25 / 80 * 0.4, 0.0))
    expected2 = {"assimilated_machine_manure": 25, "machine_manure_coverage": expected_machine_coverage2,
                 "assimilated_grazing_manure": 25, "grazing_manure_coverage": expected_grazing_coverage2}
    expected_assimilation_calls2 = [call(0.77, temp_factor, expected_machine_cover_area2, False),
                                    call(0.83, temp_factor, expected_grazing_cover_area2, True)]

    incorp2._determine_dry_manure_matter_assimilation.assert_has_calls(expected_assimilation_calls2)
    assert observed2 == expected2

    # Case 3: manure in pools, all of it should be assimilated
    data3 = SoilData(machine_manure_dry_mass=75, machine_manure_field_coverage=0.88,
                     machine_manure_moisture_factor=0.80, grazing_manure_dry_mass=95,
                     grazing_manure_field_coverage=0.85, grazing_manure_moisture_factor=0.79, field_size=1.1)
    incorp3 = Manure(data3)
    incorp3._determine_dry_manure_matter_assimilation = MagicMock(return_value=120)

    observed3 = incorp3._determine_assimilated_surface_manure(temp_factor, area)
    expected_machine_cover_area3 = area * 0.88
    expected_grazing_cover_area3 = area * 0.85
    expected_machine_coverage3 = 0.88
    expected_grazing_coverage3 = 0.85
    expected3 = {"assimilated_machine_manure": 75, "machine_manure_coverage": expected_machine_coverage3,
                 "assimilated_grazing_manure": 95, "grazing_manure_coverage": expected_grazing_coverage3}
    expected_assimilation_calls3 = [call(0.80, temp_factor,  expected_machine_cover_area3, False),
                                    call(0.79, temp_factor, expected_grazing_cover_area3, True)]

    incorp3._determine_dry_manure_matter_assimilation.assert_has_calls(expected_assimilation_calls3)
    assert observed3 == expected3


@pytest.mark.parametrize("rain,runoff,area,mean_temp", [
    (12, 1.8, 2.1, 14),
    (14, 12.2, 3.4, 9),
    (0, 0, 2.4, 28),
])
def test_daily_manure_update(rain: float, runoff: float, area: float, mean_temp: float) -> None:
    """Tests that the main manure update method correctly calls all subroutines."""
    # Case 1: manure pools are empty
    data1 = SoilData(field_size=area)
    incorp1 = Manure(data1)

    incorp1._leach_and_update_phosphorus_pools = MagicMock()
    incorp1._determine_temperature_factor = MagicMock(return_value=0.32)
    incorp1._adjust_manure_moisture_factor = MagicMock()
    incorp1._determine_decomposed_surface_manure = MagicMock(return_value={
        "decomposed_machine_manure_mass_change": 0,
        "decomposed_machine_manure_coverage_change": 0.0,
        "decomposed_grazing_manure_mass_change": 0,
        "decomposed_grazing_manure_coverage_change": 0.0})
    incorp1._determine_mineralized_surface_phosphorus = MagicMock(return_value=0)
    incorp1._determine_assimilated_surface_manure = MagicMock(return_value={
        "assimilated_machine_manure": 0,
        "machine_manure_coverage": 0.0,
        "assimilated_grazing_manure": 0,
        "grazing_manure_coverage": 0.0})
    incorp1._determine_assimilated_phosphorus_amount = MagicMock(return_value=0)
    incorp1._add_infiltrated_phosphorus_to_soil = MagicMock()

    incorp1.daily_manure_update(rain, runoff, area, mean_temp)

    if rain > 0.0:
        incorp1._leach_and_update_phosphorus_pools.assert_called_once_with(rain, runoff, area)
    else:
        incorp1._leach_and_update_phosphorus_pools.assert_not_called()
    incorp1._determine_temperature_factor.assert_called_once_with(mean_temp)
    if rain < 1.0 or rain > 4.0:
        incorp1._adjust_manure_moisture_factor.assert_called_once_with(rain, 0.32)
    else:
        incorp1._adjust_manure_moisture_factor.assert_not_called()
    incorp1._determine_decomposed_surface_manure.assert_called_once_with(0.32)
    assert incorp1._determine_mineralized_surface_phosphorus.call_count == 6
    incorp1._determine_assimilated_surface_manure.assert_called_once_with(0.32, area)
    assert incorp1._determine_assimilated_phosphorus_amount.call_count == 8
    assert incorp1.data.machine_manure_dry_mass == 0
    assert incorp1.data.machine_manure_field_coverage == 0.0
    assert incorp1.data.machine_stable_organic_phosphorus == 0
    assert incorp1.data.machine_stable_inorganic_phosphorus == 0
    assert incorp1.data.machine_water_extractable_organic_phosphorus == 0
    assert incorp1.data.machine_water_extractable_inorganic_phosphorus == 0
    assert incorp1.data.grazing_manure_dry_mass == 0
    assert pytest.approx(incorp1.data.grazing_manure_field_coverage) == 0.0
    assert incorp1.data.grazing_stable_organic_phosphorus == 0
    assert incorp1.data.grazing_stable_inorganic_phosphorus == 0
    assert incorp1.data.grazing_water_extractable_organic_phosphorus == 0
    assert incorp1.data.grazing_water_extractable_inorganic_phosphorus == 0
    incorp1._add_infiltrated_phosphorus_to_soil.assert_called_once_with(0, area)

    # Case 2: sum of amounts decomposed and assimilated are less than what is on the field
    data2 = SoilData(machine_manure_dry_mass=300, machine_manure_field_coverage=0.91, field_size=area,
                     machine_manure_moisture_factor=0.74, machine_stable_organic_phosphorus=20,
                     machine_stable_inorganic_phosphorus=21, machine_water_extractable_organic_phosphorus=22,
                     machine_water_extractable_inorganic_phosphorus=23, grazing_manure_dry_mass=200,
                     grazing_manure_field_coverage=0.83, grazing_manure_moisture_factor=0.66,
                     grazing_stable_organic_phosphorus=10, grazing_stable_inorganic_phosphorus=11,
                     grazing_water_extractable_organic_phosphorus=12, grazing_water_extractable_inorganic_phosphorus=13)
    incorp2 = Manure(data2)

    incorp2._leach_and_update_phosphorus_pools = MagicMock()
    incorp2._determine_temperature_factor = MagicMock(return_value=0.35)
    incorp2._adjust_manure_moisture_factor = MagicMock()
    incorp2._determine_decomposed_surface_manure = MagicMock(return_value={
        "decomposed_machine_manure_mass_change": 100,
        "decomposed_machine_manure_coverage_change": 0.22,
        "decomposed_grazing_manure_mass_change": 80,
        "decomposed_grazing_manure_coverage_change": 0.18})
    incorp2._determine_mineralized_surface_phosphorus = MagicMock(return_value=3)
    incorp2._determine_assimilated_surface_manure = MagicMock(return_value={
        "assimilated_machine_manure": 50,
        "machine_manure_coverage": 0.15,
        "assimilated_grazing_manure": 30,
        "grazing_manure_coverage": 0.08})
    incorp2._determine_assimilated_phosphorus_amount = MagicMock(return_value=2)
    incorp2._add_infiltrated_phosphorus_to_soil = MagicMock()

    incorp2.daily_manure_update(rain, runoff, area, mean_temp)

    if rain > 0.0:
        incorp2._leach_and_update_phosphorus_pools.assert_called_once_with(rain, runoff, area)
    else:
        incorp2._leach_and_update_phosphorus_pools.assert_not_called()
    incorp2._determine_temperature_factor.assert_called_once_with(mean_temp)
    if rain < 1.0 or rain > 4.0:
        incorp2._adjust_manure_moisture_factor.assert_called_once_with(rain, 0.35)
    else:
        incorp2._adjust_manure_moisture_factor.assert_not_called()
    incorp2._determine_decomposed_surface_manure.assert_called_once_with(0.35)
    assert incorp2._determine_mineralized_surface_phosphorus.call_count == 6
    incorp2._determine_assimilated_surface_manure.assert_called_once_with(0.35, area)
    assert incorp2._determine_assimilated_phosphorus_amount.call_count == 8
    assert incorp2.data.machine_manure_dry_mass == 150
    assert incorp2.data.machine_manure_field_coverage == 0.54
    assert incorp2.data.machine_stable_organic_phosphorus == 15
    assert incorp2.data.machine_stable_inorganic_phosphorus == 16
    assert incorp2.data.machine_water_extractable_organic_phosphorus == 17 + 0.75
    assert incorp2.data.machine_water_extractable_inorganic_phosphorus == 21 + 8.25
    assert incorp2.data.grazing_manure_dry_mass == 90
    assert pytest.approx(incorp2.data.grazing_manure_field_coverage) == 0.57
    assert incorp2.data.grazing_stable_organic_phosphorus == 5
    assert incorp2.data.grazing_stable_inorganic_phosphorus == 6
    assert incorp2.data.grazing_water_extractable_organic_phosphorus == 7 + 0.75
    assert incorp2.data.grazing_water_extractable_inorganic_phosphorus == 11 + 8.25
    incorp2._add_infiltrated_phosphorus_to_soil.assert_called_once_with(16, area)

    # Case 3: more manure/phosphorus is decomposed and assimilated than there is on the field.
    data3 = SoilData(machine_manure_dry_mass=50, machine_manure_field_coverage=0.19, field_size=area,
                     machine_manure_moisture_factor=0.35, machine_stable_organic_phosphorus=2.0,
                     machine_stable_inorganic_phosphorus=2.1, machine_water_extractable_organic_phosphorus=2.2,
                     machine_water_extractable_inorganic_phosphorus=2.3, grazing_manure_dry_mass=38,
                     grazing_manure_field_coverage=0.12, grazing_manure_moisture_factor=0.59,
                     grazing_stable_organic_phosphorus=1.0, grazing_stable_inorganic_phosphorus=1.1,
                     grazing_water_extractable_organic_phosphorus=1.2,
                     grazing_water_extractable_inorganic_phosphorus=1.3)
    incorp3 = Manure(data3)

    incorp3._leach_and_update_phosphorus_pools = MagicMock()
    incorp3._determine_temperature_factor = MagicMock(return_value=0.37)
    incorp3._adjust_manure_moisture_factor = MagicMock()
    incorp3._determine_decomposed_surface_manure = MagicMock(return_value={
        "decomposed_machine_manure_mass_change": 35,
        "decomposed_machine_manure_coverage_change": 0.11,
        "decomposed_grazing_manure_mass_change": 20,
        "decomposed_grazing_manure_coverage_change": 0.9})
    incorp3._determine_mineralized_surface_phosphorus = MagicMock(return_value=2)
    incorp3._determine_assimilated_surface_manure = MagicMock(return_value={
        "assimilated_machine_manure": 25,
        "machine_manure_coverage": 0.10,
        "assimilated_grazing_manure": 23,
        "grazing_manure_coverage": 0.05})
    incorp3._determine_assimilated_phosphorus_amount = MagicMock(return_value=3)
    incorp3._add_infiltrated_phosphorus_to_soil = MagicMock()

    incorp3.daily_manure_update(rain, runoff, area, mean_temp)

    if rain > 0.0:
        incorp3._leach_and_update_phosphorus_pools.assert_called_once_with(rain, runoff, area)
    else:
        incorp3._leach_and_update_phosphorus_pools.assert_not_called()
    incorp3._determine_temperature_factor.assert_called_once_with(mean_temp)
    if rain < 1.0 or rain > 4.0:
        incorp3._adjust_manure_moisture_factor.assert_called_once_with(rain, 0.37)
    else:
        incorp3._adjust_manure_moisture_factor.assert_not_called()
    incorp3._determine_decomposed_surface_manure.assert_called_once_with(0.37)
    assert incorp3._determine_mineralized_surface_phosphorus.call_count == 6
    incorp3._determine_assimilated_surface_manure.assert_called_once_with(0.37, area)
    assert incorp3._determine_assimilated_phosphorus_amount.call_count == 8
    assert incorp3.data.machine_manure_dry_mass == 0
    assert incorp3.data.machine_manure_field_coverage == 0.0
    assert incorp3.data.machine_stable_organic_phosphorus == 0
    assert incorp3.data.machine_stable_inorganic_phosphorus == 0
    assert incorp3.data.machine_water_extractable_organic_phosphorus == 0.5
    assert incorp3.data.machine_water_extractable_inorganic_phosphorus == 2 + 2 + 1.5
    assert incorp3.data.grazing_manure_dry_mass == 0
    assert pytest.approx(incorp3.data.grazing_manure_field_coverage) == 0.0
    assert incorp3.data.grazing_stable_organic_phosphorus == 0
    assert incorp3.data.grazing_stable_inorganic_phosphorus == 0
    assert incorp3.data.grazing_water_extractable_organic_phosphorus == 0.5
    assert incorp3.data.grazing_water_extractable_inorganic_phosphorus == 2 + 2 + 1.5
    incorp3._add_infiltrated_phosphorus_to_soil.assert_called_once_with(24, area)

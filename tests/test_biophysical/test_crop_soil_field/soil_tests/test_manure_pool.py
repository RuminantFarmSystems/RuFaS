from math import exp, sqrt
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from RUFAS.general_constants import GeneralConstants
from RUFAS.biophysical.field.soil.manure_pool import ManurePool
from RUFAS.biophysical.field.soil.phosphorus_cycling.manure import Manure
from RUFAS.biophysical.field.soil.soil_data import SoilData


def test_equal() -> None:
    pool1 = ManurePool()
    pool2 = ManurePool()
    assert pool2 == pool1


def test_manure_pool_attribute_not_equal() -> None:
    pool1 = ManurePool()
    pool2 = ManurePool(manure_dry_mass=521)
    assert not pool1 == pool2


def test_instance_not_equal() -> None:
    pool1 = ManurePool()
    observed = pool1 == 3
    assert not observed


@pytest.mark.parametrize(
    "avg_air_temp",
    [
        10,
        33,
        0,
        -14,
        18.34580983290,
    ],
)
def test_determine_temperature_factor(avg_air_temp: float) -> None:
    """Tests that the temperature factor is correctly calculated and bounded."""
    observe = ManurePool._determine_temperature_factor(avg_air_temp)
    expect = min(1, max(0, (2 * 32**2 * avg_air_temp**2 - avg_air_temp**4) / 32**4))
    assert observe == expect


@pytest.mark.parametrize(
    "temp_factor",
    [
        0.0,
        1.0,
        0.4,
        0.8884959312,
    ],
)
def test_determine_dry_matter_decomposition_rate(temp_factor: float) -> None:
    """Tests that the dry matter decomposition rate is calculated correctly for a given day."""
    observe = ManurePool._determine_dry_matter_decomposition_rate(temp_factor)
    expect = 0.003 * temp_factor**0.5
    assert observe == expect


@pytest.mark.parametrize(
    "moisture,temp_factor,area,is_dung",
    [
        [0.4, 0.3, 1, False],
        [0.8, 0.1, 3.18, True],
        [0.2, 0.187, 2.854, False],
        [0.552, 0.87, 0.875, True],
    ],
)
def test_determine_dry_manure_matter_assimilation(
    moisture: float, temp_factor: float, area: float, is_dung: bool
) -> None:
    """Tests that the correct amount of manure dry matter is assimilated into the soil on a given day is calculated
    correctly.
    """
    observe = ManurePool._determine_dry_manure_matter_assimilation(moisture, temp_factor, area, is_dung)
    if is_dung:
        expect = 30 * exp(3.5 * sqrt(moisture)) * (temp_factor**0.1) * area
    else:
        expect = (30 * exp(2.5 * moisture)) * temp_factor * area
    assert observe == expect


@pytest.mark.parametrize(
    "rain,moisture,current_mass,original_mass,temp_factor",
    [
        (0.8, 0.7, 35, 80, 0.7),  # Moisture decreases
        (0.2, 0.0, 45, 150, 0.95),  # Moisture decreases
        (1.0, 0.4, 22, 87, 0.684),  # No moisture change
        (3.99, 0.81, 76, 100, 0.182),  # No moisture change
        (4.0, 0.44, 28.47, 50, 0.12),  # No moisture change
        (5.6, 0.78, 35.673, 60, 0.081),  # Moisture increases
        (7.8, 0.087, 97, 140, 0.345),  # Moisture increases
    ],
)
def test_determine_moisture_change(
    rain: float,
    moisture: float,
    current_mass: float,
    original_mass: float,
    temp_factor: float,
) -> None:
    """Tests that the correct change in the moisture factor of an application of manure is calculated on a given day."""
    observe = ManurePool._determine_moisture_change(rain, moisture, current_mass, original_mass, temp_factor)
    if rain < 1:
        expect = -1 * (-0.05 * (current_mass / original_mass) + 0.075) * temp_factor
    elif 1.0 <= rain <= 4.0:
        expect = 0
    else:
        expect = (-0.3 * moisture) + 0.27
    assert observe == expect


@pytest.mark.parametrize(
    "rain,manure_mass,manure_coverage",
    [
        (13, 300, 3),
        (5, 30, 1.8),
        (3.881993, 86.24832, 2.3948),
    ],
)
def test_determine_rain_manure_dry_matter_ratio(rain: float, manure_mass: float, manure_coverage: float) -> float:
    """Tests that the ratio of rain to manure is calculated correctly."""
    observe = ManurePool._determine_rain_manure_dry_matter_ratio(rain, manure_mass, manure_coverage)
    expect = rain / manure_mass * manure_coverage * 10_000
    assert observe == expect


@pytest.mark.parametrize(
    "manure,rain_manure_ratio,is_cow, organic_phosphorus",
    [
        (300, 1300, True, False),
        (255, 1234, False, False),
        (300, 1300, True, True),
        (255, 1234, False, True),
    ],
)
def test_determine_water_extractable_phosphorus_leached(
    manure: float, rain_manure_ratio: float, is_cow: bool, organic_phosphorus: bool
) -> None:
    """Tests that the correct mass of water extractable inorganic phosphorus leached is calculated."""
    observe = ManurePool._determine_water_extractable_phosphorus_leached(
        manure, rain_manure_ratio, is_cow, organic_phosphorus
    )

    if is_cow:
        expect = min(1.0, (1.2 * rain_manure_ratio) / (rain_manure_ratio + 73.1)) * manure
    else:
        expect = min(1.0, (2.2 * rain_manure_ratio) / (rain_manure_ratio + 300.1)) * manure
    expect = max(0.0, expect) / 0.6 if organic_phosphorus else max(0.0, expect)
    assert observe == expect


@pytest.mark.parametrize(
    "rain,runoff",
    [
        (13, 0),
        (11, 3),
        (10, 10),
    ],
)
def test_determine_phosphorus_distribution_factor(rain: float, runoff: float) -> None:
    """Tests that the adjusted ratio of rainfall to runoff is calculated correctly."""
    observe = ManurePool._determine_phosphorus_distribution_factor(rain, runoff)
    expect = (runoff / rain) ** 0.225
    assert observe == expect


@pytest.mark.parametrize(
    "manure,rain,field_size,distribution_factor",
    [
        (23, 11, 3.1, 0.8743),
        (58.67143, 7.183, 0.981, 0.69982),
        (147.1892, 4.867, 1.875, 0.1984),
        (87.92734, 6.839, 2.385, 1.0),
        (101.29482, 9.29583, 3.4918, 0.0),
    ],
)
def test_determine_water_extractable_phosphorus_runoff_concentration(
    manure: float, rain: float, field_size: float, distribution_factor: float
) -> None:
    """Tests that the concentration of water extractable phosphorus in runoff is calculated correctly based on manure
    leached, amount of rainfall, area of the field, and the ratio of runoff to rainfall.
    """
    observe = ManurePool._determine_water_extractable_phosphorus_runoff_concentration(
        manure, rain, field_size, distribution_factor
    )
    expect = manure / rain * (1 / field_size) * 100 * distribution_factor
    assert pytest.approx(observe) == expect


@pytest.mark.parametrize(
    "rain,runoff,area,manure_mass,field_coverage,phosphorus_mass,organic",
    [
        (11, 3, 1.8, 800, 0.7, 120, True),
        (14, 1.8, 3.1, 950, 0.91, 133, False),
        (9.1, 2.7, 2.2, 993, 0.88, 86, True),
        (10.11, 4.1, 2.8, 1234, 0.9655, 200, False),
        (14, 13, 2.0, 20, 0.12, 1.4, False),
        (9.8, 9.1, 2, 36, 0.28, 2.1, True),
        (6.2, 0.0, 2.3, 500, 0.65, 80, False),
    ],
)
def test_determine_phosphorus_leached_from_surface(
    rain: float,
    runoff: float,
    area: float,
    manure_mass: float,
    field_coverage: float,
    phosphorus_mass: float,
    organic: bool,
    mocker: MockerFixture,
) -> None:
    """Test that subroutines are called correctly and that leached phosphorus amounts are calculated correctly."""
    mock_rain_ratio = mocker.patch.object(ManurePool, "_determine_rain_manure_dry_matter_ratio", return_value=0.4)
    mock_phosphorus_distribution_factor = mocker.patch.object(
        ManurePool, "_determine_phosphorus_distribution_factor", return_value=1.2
    )
    mock_water_extractable_phosphorus_leached = mocker.patch.object(
        ManurePool, "_determine_water_extractable_phosphorus_leached", return_value=25.0
    )

    mock_runoff_concentration = mocker.patch.object(
        ManurePool, "_determine_water_extractable_phosphorus_runoff_concentration", return_value=5
    )

    observed = ManurePool._determine_phosphorus_leached_from_surface(
        rain, runoff, area, manure_mass, field_coverage, phosphorus_mass, organic
    )
    runoff_in_liters = (
        runoff * area * GeneralConstants.HECTARES_TO_SQUARE_MILLIMETERS * GeneralConstants.CUBIC_MILLIMETERS_TO_LITERS
    )
    expected_covered_area = area * field_coverage
    expected_water_extractable_phosphorus_leached = min(25.0, phosphorus_mass)
    expected_runoff_phosphorus_in_kg = 5 * runoff_in_liters * GeneralConstants.MILLIGRAMS_TO_KG
    expected_infiltrated_phosphorus = max(
        0,
        expected_water_extractable_phosphorus_leached - expected_runoff_phosphorus_in_kg,
    )

    mock_rain_ratio.assert_called_once_with(rain, manure_mass, expected_covered_area)
    mock_phosphorus_distribution_factor.assert_called_once_with(rain, runoff)
    if organic:
        mock_water_extractable_phosphorus_leached.assert_called_once_with(phosphorus_mass, 0.4, True, True)
    else:
        mock_water_extractable_phosphorus_leached.assert_called_once_with(phosphorus_mass, 0.4, True, False)
    mock_runoff_concentration.assert_called_once_with(expected_water_extractable_phosphorus_leached, rain, area, 1.2)
    assert observed["new_phosphorus_pool_amount"] == (phosphorus_mass - expected_water_extractable_phosphorus_leached)
    assert observed["infiltrated_phosphorus"] == expected_infiltrated_phosphorus
    assert observed["runoff_phosphorus"] == expected_runoff_phosphorus_in_kg


@pytest.mark.parametrize(
    "phosphorus,rate,temp_factor,moisture_factor",
    [
        (25, 0.1, 0.33, 0.55),
        (33, 0.01, 0.65, 0.78),
        (21, 0.0025, 0.3423, 0.7768),
        (0, 0.01, 0.012, 0.23),
        (23, 0.0025, -0.13, 0.332),
        (41, 0.1, -0.19, 0.0),
    ],
)
def test_determine_mineralized_surface_phosphorus(
    phosphorus: float, rate: float, temp_factor: float, moisture_factor: float
) -> None:
    """Tests that the correct amount of mineralized phosphorus is calculated."""
    observed = ManurePool.determine_mineralized_surface_phosphorus(phosphorus, rate, temp_factor, moisture_factor)
    expected = min(phosphorus, max(0.0, phosphorus * rate * min(temp_factor, moisture_factor)))
    assert observed == expected


@pytest.mark.parametrize(
    "ratio,phosphorus",
    [
        (0.88, 26),
        (0.212, 12.13),
        (0.0, 30.21),
        (0.441, 0.0),
        (0.0, 0.0),
    ],
)
def test_determine_assimilated_phosphorus_amount(ratio: float, phosphorus: float) -> None:
    """Tests that the correct amount of phosphorus assimilated into the soil is calculated."""
    observed = ManurePool.determine_assimilated_phosphorus_amount(ratio, phosphorus)
    expected = max(0.0, ratio * phosphorus)
    expected = min(phosphorus, expected)
    assert observed == expected


@pytest.mark.parametrize(
    "amount_phosphorus,field_size",
    [
        (100, 3.1),
        (25.6, 2),
        (66.23, 1.88),
    ],
)
def test_add_infiltrated_phosphorus_to_soil(amount_phosphorus: float, field_size: float, mocker: MockerFixture) -> None:
    """Test that methods are called correctly on correct layers of soil profile."""
    data = SoilData(field_size=field_size)
    incorp = Manure(data)
    mock_add = mocker.patch("RUFAS.biophysical.field.soil.layer_data.LayerData.add_to_labile_phosphorus")
    incorp._add_infiltrated_phosphorus_to_soil(amount_phosphorus, field_size)
    assert mock_add.call_count == 2


@pytest.mark.parametrize(
    "rain,runoff,area",
    [
        (13, 4, 1.8),
        (12, 1.8, 2.1),
        (14, 12.2, 3.4),
        (4.2, 0, 2.4),
    ],
)
def test_leach_and_update_phosphorus_pools(rain: float, runoff: float, area: float, mocker: MockerFixture) -> None:
    """Tests that the update subroutine for phosphorus pools in Manure correctly calls methods and sets attributes."""
    data = SoilData(
        machine_manure=ManurePool(
            manure_dry_mass=1000,
            manure_field_coverage=0.86,
            water_extractable_inorganic_phosphorus=200,
            water_extractable_organic_phosphorus=90,
        ),
        grazing_manure=ManurePool(
            manure_dry_mass=800,
            manure_field_coverage=0.78,
            water_extractable_inorganic_phosphorus=125,
            water_extractable_organic_phosphorus=70,
        ),
        field_size=area,
    )
    incorp = Manure(data)

    mock_leached_from_surface = mocker.patch.object(
        ManurePool,
        "_determine_phosphorus_leached_from_surface",
        return_value={
            "new_phosphorus_pool_amount": 30,
            "infiltrated_phosphorus": 25,
            "runoff_phosphorus": 20,
        },
    )
    mock_add_pool = mocker.patch.object(incorp, "_add_infiltrated_phosphorus_to_soil")

    incorp._leach_and_update_phosphorus_pools(rain, runoff, area)

    leached_calls = [
        call(rain, runoff, area, 1000, 0.86, 90, True),
        call(rain, runoff, area, 1000, 0.86, 200, False),
        call(rain, runoff, area, 800, 0.78, 70, True),
        call(rain, runoff, area, 800, 0.78, 125, False),
    ]

    mock_leached_from_surface.assert_has_calls(leached_calls)
    infiltrated_calls = [call(25, area), call(25, area), call(25, area), call(25, area)]
    mock_add_pool.assert_has_calls(infiltrated_calls)
    assert incorp.data.machine_manure.water_extractable_organic_phosphorus == 30
    assert incorp.data.machine_manure.water_extractable_inorganic_phosphorus == 30
    assert incorp.data.machine_manure.organic_phosphorus_runoff == 20
    assert incorp.data.machine_manure.inorganic_phosphorus_runoff == 20
    assert incorp.data.machine_manure.annual_runoff_manure_organic_phosphorus == 20
    assert incorp.data.machine_manure.annual_runoff_manure_inorganic_phosphorus == 20
    assert incorp.data.grazing_manure.water_extractable_organic_phosphorus == 30
    assert incorp.data.grazing_manure.water_extractable_inorganic_phosphorus == 30
    assert incorp.data.grazing_manure.organic_phosphorus_runoff == 20
    assert incorp.data.grazing_manure.inorganic_phosphorus_runoff == 20
    assert incorp.data.grazing_manure.annual_runoff_manure_organic_phosphorus == 20
    assert incorp.data.grazing_manure.annual_runoff_manure_inorganic_phosphorus == 20


@pytest.mark.parametrize(
    "rain,temp_factor,manure_dry_mass,no_calc",
    [
        (10, 0.35, 0, True),
        (4, 0.4413, 500, False),
        (16, 0.121, -20, True),
    ],
)
def test_adjust_manure_moisture_factor(
    rain: float, temp_factor: float, manure_dry_mass: float, no_calc: bool, mocker: MockerFixture
) -> None:
    """Tests that the manure moisture factors of the different pools are correctly updated."""
    mocked_determine_moisture_change = mocker.patch.object(ManurePool, "_determine_moisture_change", return_value=0.1)
    incorp1 = ManurePool(
        manure_moisture_factor=0.5, manure_dry_mass=manure_dry_mass, manure_applied_mass=2.2, manure_field_coverage=69
    )

    incorp1.adjust_manure_moisture_factor(rain, temp_factor)

    moisture_change_calls = [call(rain, 0.5, 500, 2.2, temp_factor)]
    if no_calc:
        mocked_determine_moisture_change.assert_not_called()
        assert incorp1.manure_moisture_factor == 0.5
    else:
        mocked_determine_moisture_change.assert_has_calls(moisture_change_calls)
        assert incorp1.manure_moisture_factor == 0.6


@pytest.mark.parametrize(
    "temp_factor,manure_dry_mass,manure_field_coverage,expected",
    [
        (0.45, 800, 0.85, (400.0, 0.425)),
        (0.66, 900, 0.92, (450.0, 0.46)),
        (0.12, 43, 0.07, (21.5, 0.035)),
        (0.33, 3, 0.02, (1.5, 0.01)),
    ],
)
def test_determine_decomposed_surface_manure(
    temp_factor: float,
    manure_dry_mass: float,
    manure_field_coverage: float,
    expected: tuple[float, float],
    mocker: MockerFixture,
) -> None:
    """Tests that the correct changes in mass and field coverage of machine and grazer applied manure are calculated."""
    incorp = ManurePool(manure_dry_mass=manure_dry_mass, manure_field_coverage=manure_field_coverage)
    mock_decomp_rate = mocker.patch.object(incorp, "_determine_dry_matter_decomposition_rate", return_value=0.5)

    observed = incorp.determine_decomposed_surface_manure(temp_factor)

    mock_decomp_rate.assert_called_once_with(temp_factor)
    assert observed == expected


@pytest.mark.parametrize(
    "temp_factor,area,manure_dry_mass,no_calc,expected",
    [(0.44, 1.89, 0, True, (0, 0)), (0.3223, 2.45, 500, False, (20, 0.02)), (0.661, 1.23, 500, False, (20, 0.02))],
)
def test_determine_assimilated_surface_manure(
    temp_factor: float,
    area: float,
    manure_dry_mass: float,
    no_calc: bool,
    expected: tuple[float, float],
    mocker: MockerFixture,
) -> None:
    """Tests that correct decrease in manure and field coverage due to assimilation are calculated."""
    pool = ManurePool(manure_dry_mass=manure_dry_mass, manure_field_coverage=0.5, manure_moisture_factor=0.4)
    if no_calc:
        observed = pool.determine_assimilated_surface_manure(temp_factor, area)
        assert observed == (0, 0)
    else:
        mocked_determine_dry_manure_matter_assimilation = mocker.patch.object(
            pool, "_determine_dry_manure_matter_assimilation", return_value=20
        )
        observed = pool.determine_assimilated_surface_manure(temp_factor, area)

        mocked_determine_dry_manure_matter_assimilation.assert_called_once_with(0.4, temp_factor, 0.5 * area, False)

        assert observed == expected


@pytest.mark.parametrize(
    "rain,area,mean_temp",
    [
        (12, 2.1, 14),
        (0, 3.4, 9),
        (3, 2.4, 28),
    ],
)
def test_daily_manure_update(rain: float, area: float, mean_temp: float, mocker: MockerFixture) -> None:
    """Tests that the main manure update method correctly calls all subroutines."""
    pool = ManurePool(stable_organic_phosphorus=4)

    mock_determine_temperature_factor = mocker.patch.object(pool, "_determine_temperature_factor", return_value=0.1)
    mock_determine_decomposed_surface_manure = mocker.patch.object(
        pool, "determine_decomposed_surface_manure", return_value=(0, 0)
    )
    mock_determine_mineralized_surface_phosphorus = mocker.patch.object(
        pool, "determine_mineralized_surface_phosphorus", return_value=4
    )
    mock_adjust_manure_moisture_factor = mocker.patch.object(pool, "adjust_manure_moisture_factor", return_value=0.2)
    mock_determine_assimilated_surface_manure = mocker.patch.object(
        pool, "determine_assimilated_surface_manure", return_value=(0, 0)
    )
    mock_determine_assimilated_phosphorus_amount = mocker.patch.object(
        pool, "determine_assimilated_phosphorus_amount", return_value=4
    )

    mineralized_surface_phosphorus_calls = [
        call(4, 0.01, 0.1, 0),
        call(0, 0.0025, 0.1, 0),
        call(0, 0.1, 0.1, 0),
    ]

    assimilated_phosphorus_amount_calls = [call(0, 0), call(0, 0), call(0, 0)]

    observed = pool.daily_manure_update(rain, area, mean_temp)
    if rain < 1 or rain > 4:
        mock_adjust_manure_moisture_factor.assert_called_once_with(rain, 0.1)
    mock_determine_temperature_factor.assert_called_once_with(mean_temp)
    mock_determine_decomposed_surface_manure.assert_called_once_with(0.1)
    assert mock_determine_mineralized_surface_phosphorus.call_count == 3
    mock_determine_mineralized_surface_phosphorus.assert_has_calls(mineralized_surface_phosphorus_calls)
    mock_determine_assimilated_surface_manure.assert_called_once_with(0.1, area)
    assert mock_determine_assimilated_phosphorus_amount.call_count == 4
    mock_determine_assimilated_phosphorus_amount.assert_has_calls(assimilated_phosphorus_amount_calls)
    assert pool.manure_dry_mass == 0
    assert pool.manure_field_coverage == 0
    assert pool.stable_organic_phosphorus == 0
    assert pool.stable_inorganic_phosphorus == 0
    assert pool.water_extractable_organic_phosphorus == 1
    assert pool.water_extractable_inorganic_phosphorus == 11
    assert pool.annual_decomposed_manure == 12

    assert observed == 16


@pytest.mark.parametrize(
    "rain,area,mean_temp",
    [
        (12, 2.1, 14),
        (0, 3.4, 9),
        (3, 2.4, 28),
    ],
)
def test_daily_manure_update_with_dry_mass(rain: float, area: float, mean_temp: float, mocker: MockerFixture) -> None:
    """Tests that the main manure update method correctly calls all subroutines when manure dry mass is not 0."""
    pool = ManurePool(manure_dry_mass=100)

    mock_determine_temperature_factor = mocker.patch.object(pool, "_determine_temperature_factor", return_value=0.1)
    mock_determine_decomposed_surface_manure = mocker.patch.object(
        pool, "determine_decomposed_surface_manure", return_value=(0, 0)
    )
    mock_determine_mineralized_surface_phosphorus = mocker.patch.object(
        pool, "determine_mineralized_surface_phosphorus", return_value=4
    )
    mock_adjust_manure_moisture_factor = mocker.patch.object(pool, "adjust_manure_moisture_factor", return_value=0.2)
    mock_determine_assimilated_surface_manure = mocker.patch.object(
        pool, "determine_assimilated_surface_manure", return_value=(0, 0)
    )
    mock_determine_assimilated_phosphorus_amount = mocker.patch.object(
        pool, "determine_assimilated_phosphorus_amount", return_value=4
    )

    mineralized_surface_phosphorus_calls = [
        call(0, 0.01, 0.1, 0),
        call(0, 0.0025, 0.1, 0),
        call(0, 0.1, 0.1, 0),
    ]

    assimilated_phosphorus_amount_calls = [call(0, 0), call(0, 0), call(0, 0)]

    observed = pool.daily_manure_update(rain, area, mean_temp)
    if rain < 1 or rain > 4:
        mock_adjust_manure_moisture_factor.assert_called_once_with(rain, 0.1)
    mock_determine_temperature_factor.assert_called_once_with(mean_temp)
    mock_determine_decomposed_surface_manure.assert_called_once_with(0.1)
    assert mock_determine_mineralized_surface_phosphorus.call_count == 3
    mock_determine_mineralized_surface_phosphorus.assert_has_calls(mineralized_surface_phosphorus_calls)
    mock_determine_assimilated_surface_manure.assert_called_once_with(0.1, area)
    assert mock_determine_assimilated_phosphorus_amount.call_count == 4
    mock_determine_assimilated_phosphorus_amount.assert_has_calls(assimilated_phosphorus_amount_calls)
    assert pool.manure_dry_mass == 100
    assert pool.manure_field_coverage == 0
    assert pool.stable_organic_phosphorus == 0
    assert pool.stable_inorganic_phosphorus == 0
    assert pool.water_extractable_organic_phosphorus == 1
    assert pool.water_extractable_inorganic_phosphorus == 11

    assert observed == 16


def test_runoff_reset() -> None:
    """Test that the runoffs were being reset correctly."""
    pool = ManurePool(organic_phosphorus_runoff=250, inorganic_phosphorus_runoff=77)
    pool.runoff_reset()
    assert pool.organic_phosphorus_runoff == 0
    assert pool.inorganic_phosphorus_runoff == 0


@pytest.mark.parametrize(
    "manure_dry_mass,manure_field_coverage,expected",
    [
        (12, 2.1, True),
        (0, 3.4, False),
        (3, 0, False),
    ],
)
def test_determine_phosphorus_leach(manure_dry_mass: float, manure_field_coverage: float, expected: bool) -> None:
    """Tests that the phosphorus leaching run status is being correctly determined."""
    pool = ManurePool(manure_dry_mass=manure_dry_mass, manure_field_coverage=manure_field_coverage)
    observed = pool.determine_phosphorus_leach()
    assert observed == expected

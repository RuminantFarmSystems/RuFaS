from math import exp
from unittest.mock import MagicMock, PropertyMock, call, patch

import pytest

from RUFAS.biophysical.field.soil.nitrogen_cycling.nitrification_volatilization import NitrificationVolatilization
from RUFAS.biophysical.field.soil.soil_data import SoilData


# --- Static method tests ---
@pytest.mark.parametrize(
    "temp,expected",
    [(20, 0.615), (31.493, 1.0), (14.334, 0.382_694), (5.0193, 0.000_791_3)],
)
def test_calculate_nitrification_volatilization_temp_factor(temp: float, expected: float) -> None:
    """Tests that the temperature factor used by the nitrification volatilization module is calculated correctly."""
    observed = NitrificationVolatilization._calculate_nitrification_volatilization_temp_factor(temp)
    assert pytest.approx(observed) == expected


@pytest.mark.parametrize(
    "water,wilting,field",
    [
        (3.55, 1.85, 6.559),
        (0.0, 1.22, 4.55712),
        (1.33, 2.22, 5.7781),
        (7.55, 2.314, 6.0133),
    ],
)
def test_calculate_nitrification_soil_water_factor(water: float, wilting: float, field: float) -> None:
    """Tests that the water factor for nitrification is calculated correctly."""
    observed = NitrificationVolatilization._calculate_nitrification_soil_water_factor(water, wilting, field)
    if water < 0.25 * field - 0.75 * wilting:
        expected = (water - wilting) / (0.25 * (field - wilting))
    else:
        expected = 1.0
    assert observed == expected


@pytest.mark.parametrize(
    "depth",
    [
        12,
        33.5,
        94,
        120.394,
    ],
)
def test_calculate_volatilization_depth_factor(depth: float) -> None:
    """Tests that the volatilization depth factor is calculated correctly."""
    observed = NitrificationVolatilization._calculate_volatilization_depth_factor(depth)
    expected = 1 - depth / (depth + exp(4.706 - 0.0305 * depth))
    assert observed == expected


@pytest.mark.parametrize(
    "temp_factor,water_factor",
    [(0.9982, 0.7767), (0.6779, 0.88657), (0.144, 0.2295), (0.3059, 0.2259)],
)
def test_calculate_nitrification_regulator(temp_factor: float, water_factor: float) -> None:
    """Tests that the nitrification factor is calculated correctly."""
    observed = NitrificationVolatilization._calculate_nitrification_regulator(temp_factor, water_factor)
    expected = temp_factor * water_factor
    assert observed == expected


@pytest.mark.parametrize(
    "temp_factor,depth_factor,exchange_factor",
    [(0.7795, 0.4495, 0.15), (0.11439, 0.9938, 0.1245), (0.8858, 0.6675, 0.22395)],
)
def test_calculate_volatilization_regulator(temp_factor: float, depth_factor: float, exchange_factor: float) -> None:
    """Tests that the volatilization factor is calculated correctly."""
    observed = NitrificationVolatilization._calculate_volatilization_regulator(
        temp_factor, depth_factor, exchange_factor
    )
    expected = temp_factor * depth_factor * exchange_factor
    assert observed == expected


@pytest.mark.parametrize(
    "ammonium,nitrification,volatilization",
    [(30.12, 0.56, 0.056), (21.45, 0.8895, 0.1123), (40.595, 0.411894, 0.0857)],
)
def test_calculate_total_ammonium_lost(ammonium: float, nitrification: float, volatilization: float) -> None:
    """Tests that the amount of ammonium lost to nitrification and volatilization is calculated correctly."""
    observed = NitrificationVolatilization._calculate_total_ammonium_lost(ammonium, nitrification, volatilization)
    expected = ammonium * (1 - exp(-1 * nitrification - volatilization))
    assert observed == expected


@pytest.mark.parametrize("regulator", [0.05, 0.11234, 0.781, 0.8894, 0.4459])
def test_calculate_ammonium_loss_fraction(regulator: float) -> None:
    """Tests that the fraction of ammonium lost to a given process is calculated correctly."""
    observed = NitrificationVolatilization._calculate_ammonium_loss_fraction(regulator)
    expected = 1 - exp(-1 * regulator)
    assert observed == expected


@pytest.mark.parametrize(
    "ammonium_lost,actual,other",
    [(12.44, 0.33, 0.132), (33.4495, 0.465, 0.33184), (22.592, 0.2815, 0.44568)],
)
def test_calculate_ammonium_lost_to_process(ammonium_lost: float, actual: float, other: float) -> None:
    """Tests that the amount of ammonium lost to a specific process is calculated correctly."""
    observed = NitrificationVolatilization._calculate_ammonium_lost_to_process(ammonium_lost, actual, other)
    expected = ammonium_lost * actual / (actual + other)
    assert pytest.approx(observed) == expected


# --- Main routine test ---
def test_do_daily_nitrification_and_volatilization() -> None:
    """Tests that the main routine of NitrificationVolatilization correctly calculates and updates attributes."""
    with patch.multiple(
        "RUFAS.biophysical.field.soil.layer_data.LayerData",
        wilting_point_content=PropertyMock(return_value=2.33),
        field_capacity_content=PropertyMock(return_value=5.77),
        depth_of_layer_center=PropertyMock(return_value=57.89),
        nutrient_cycling_water_factor=PropertyMock(return_value=0.75),
    ):
        data = SoilData(field_size=1.8)
        incorp = NitrificationVolatilization(data)
        incorp.data.set_vectorized_layer_attribute("temperature", [18, 4, 18, 18])
        incorp.data.set_vectorized_layer_attribute("water_content", [3.67, 3.67, 3.67, 3.67])
        incorp.data.set_vectorized_layer_attribute(
            "ammonium_volatilization_cation_exchange_factor", [0.18, 0.18, 0.18, 0.18]
        )
        incorp.data.set_vectorized_layer_attribute("ammonium_content", [25, 25, 25, 25])
        incorp.data.set_vectorized_layer_attribute("nitrate_content", [25, 25, 25, 25])

        incorp._calculate_nitrification_volatilization_temp_factor = MagicMock(return_value=0.8)
        incorp._calculate_nitrification_soil_water_factor = MagicMock(return_value=0.75)
        incorp._calculate_volatilization_depth_factor = MagicMock(return_value=0.46)
        incorp._calculate_nitrification_regulator = MagicMock(return_value=0.55)
        incorp._calculate_volatilization_regulator = MagicMock(return_value=0.08)
        incorp._calculate_ammonium_loss_fraction = MagicMock(return_value=0.35)
        incorp._calculate_total_ammonium_lost = MagicMock(return_value=6.5)
        incorp._calculate_ammonium_lost_to_process = MagicMock(return_value=3.25)

        incorp.do_daily_nitrification_and_volatilization()

        temp_factor_calls = [call(18)] * 3
        incorp._calculate_nitrification_volatilization_temp_factor.assert_has_calls(temp_factor_calls)
        depth_factor_calls = [call(57.89)] * 3
        incorp._calculate_volatilization_depth_factor.assert_has_calls(depth_factor_calls)
        nitrification_regulator_calls = [call(0.8, 0.75)] * 3
        incorp._calculate_nitrification_regulator.assert_has_calls(nitrification_regulator_calls)
        volatilization_regulator_calls = [call(0.8, 0.46, 0.18)] * 3
        incorp._calculate_volatilization_regulator.assert_has_calls(volatilization_regulator_calls)
        ammonium_loss_frac_calls = [call(0.55), call(0.08)] * 3
        incorp._calculate_ammonium_loss_fraction.assert_has_calls(ammonium_loss_frac_calls)
        total_ammonium_lost_calls = [call(25, 0.55, 0.08)] * 3
        incorp._calculate_total_ammonium_lost.assert_has_calls(total_ammonium_lost_calls)
        ammonium_lost_calls = [call(6.5, 0.35, 0.35)] * 6
        incorp._calculate_ammonium_lost_to_process.assert_has_calls(ammonium_lost_calls)

        assert incorp.data.soil_layers[0].ammonium_content == 18.5
        assert incorp.data.soil_layers[0].nitrate_content == 28.25
        assert incorp.data.soil_layers[0].ammonia_emissions == 3.25
        assert incorp.data.soil_layers[0].annual_ammonia_emissions_total == 3.25

        assert incorp.data.soil_layers[1].ammonium_content == 25
        assert incorp.data.soil_layers[1].nitrate_content == 25
        assert incorp.data.soil_layers[1].annual_ammonia_emissions_total == 0

        for layer in incorp.data.soil_layers[2:]:
            assert layer.ammonium_content == 18.5
            assert layer.nitrate_content == 28.25
            assert layer.ammonia_emissions == 3.25
            assert layer.annual_ammonia_emissions_total == 3.25

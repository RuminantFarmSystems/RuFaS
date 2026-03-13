from math import exp, log
from unittest.mock import MagicMock

import pytest

from RUFAS.biophysical.field.soil.soil_data import SoilData
from RUFAS.biophysical.field.soil.soil_temp import SoilTemp


@pytest.mark.parametrize(
    "bulk_density",
    [
        0,
        1.89,
        1.23223,
        1.5321,
        1.4013,
    ],
)
def test_determine_maximum_damping_depth(bulk_density: float) -> None:
    """tests _determine_maximum_damping_depth() in soil_temp.py"""
    observe = SoilTemp._determine_maximum_damping_depth(bulk_density)
    expect = 1000 + ((2500 * bulk_density) / (bulk_density + (686 * exp(-5.63 * bulk_density))))
    assert observe == expect


@pytest.mark.parametrize(
    "water_content,density,bottom_depth",
    [
        (21.456, 1.78, 2000),
        (24.534, 1.8694, 2130),
        (50.67, 2.0194, 1924),
        (45.8395, 1.543, 1874),
    ],
)
def test_determine_scaling_factor(water_content: float, density: float, bottom_depth: int) -> None:
    """tests _determine_scaling_factor() in soil_temp.py"""
    observe = SoilTemp._determine_scaling_factor(water_content, density, bottom_depth)
    bottom_term = (0.356 - (0.144 * density)) * bottom_depth
    expect = water_content / bottom_term
    assert observe == expect


@pytest.mark.parametrize(
    "max_damping_depth,scaling_factor",
    [
        (1000, 0.189),
        (3000, 0.3942),
        (2457, 0.23423),
        (2958, 0.3058),
    ],
)
def test_determine_damping_depth(max_damping_depth: int, scaling_factor: float) -> None:
    """tests _determine_damping_depth() in soil_temp.py"""
    observe = SoilTemp._determine_damping_depth(max_damping_depth, scaling_factor)
    expect = max_damping_depth * exp(log(500 / max_damping_depth) * ((1 - scaling_factor) / (1 + scaling_factor)) ** 2)
    assert observe == expect


@pytest.mark.parametrize(
    "center_depth,damping_depth",
    [
        (14, 2198.9583),
        (80, 2003.95),
        (158, 1894.596),
        (365, 2304.786),
        (904, 1569.852323),
        (1784, 1995.38547),
        (2104, 2058.5853),
        (2594.4859, 2394.5857),
    ],
)
def test_determine_depth_factor(center_depth, damping_depth):
    """tests _determine_depth_factor() in soil_temp.py"""
    observe = SoilTemp._determine_depth_factor(center_depth, damping_depth)
    expect = (center_depth / damping_depth) / (
        (center_depth / damping_depth) + exp(-0.867 - (2.078 * (center_depth / damping_depth)))
    )
    assert observe == expect


@pytest.mark.parametrize(
    "radiation,albedo",
    [
        (102.3, 0.16),
        (0, 0),
        (303.564, 0.18),
        (78.9837, 0.199),
        (586, 0.2354),
        (238.384, 0.3885),
    ],
)
def test_determine_radiation_factor(radiation, albedo):
    """tests _determine_radiation_factor() in soil_temp.py"""
    observe = SoilTemp._determine_radiation_factor(radiation, albedo)
    expect_top = radiation * (1 - albedo) - 14
    expect = expect_top / 20
    assert observe == expect


@pytest.mark.parametrize(
    "radiation,avg_temp,min_temp,max_temp",
    [
        (20, 21, 18, 23),
        (18.93845, 23.985, 28, 16),
        (12.9983, 26.848, 30, 23),
        (35.69458, 22.3847, 24, 17),
        (41.3932, 16.93845, 19, 10),
    ],
)
def test_determine_bare_soil_surface_temp(radiation, avg_temp, min_temp, max_temp):
    """tests _determine_bare_soil_surface_temp() in soil_tests.py"""
    observed = SoilTemp._determine_bare_soil_surface_temp(radiation, avg_temp, min_temp, max_temp)
    expect = avg_temp + radiation * ((max_temp - min_temp) / 2)
    assert observed == expect


@pytest.mark.parametrize(
    "plant_cover,snow_cover",
    [
        (137.93, 13.95),
        (102.495, 18.9585),
        (0, 0),
        (32.495, 56.94385),
        (203.0459, 34.958),
    ],
)
def test_determine_cover_weighting_factor(plant_cover, snow_cover):
    observe = SoilTemp._determine_cover_weighting_factor(plant_cover, snow_cover)
    plant_factor = plant_cover / (plant_cover + exp(7.563 - (0.001297 * plant_cover)))
    snow_factor = snow_cover / (snow_cover + exp(6.055 - (0.3002 * snow_cover)))
    expect = max(plant_factor, snow_factor)
    assert observe == expect


@pytest.mark.parametrize(
    "cover_factor,previous_top_layer_temp,bare_surface_temp",
    [
        (0, 0, 0),
        (0.5, 12, 15),
        (0.88, 23, 28),
        (0.11, -3, -1),
        (0.42495, 17.8547, 20.4857),
    ],
)
def test_determine_soil_surface_temp(cover_factor, previous_top_layer_temp, bare_surface_temp):
    observe = SoilTemp._determine_soil_surface_temp(cover_factor, previous_top_layer_temp, bare_surface_temp)
    expect = (cover_factor * previous_top_layer_temp) + ((1 - cover_factor) * bare_surface_temp)
    assert observe == expect


@pytest.mark.parametrize(
    "lag,prev_soil_temp,depth_factor,avg_annual_air_temp,soil_surface_temp",
    [
        (0.8, 15, 0.5, 19, 16),
        (0.78, -2, 0.18, 21, -4),
        (0.80198, 12, 0.89, 22.9485, 20.3847),
        (0.892, 17, 0.0989, 21.99843, 19.98332),
        (0.677534, 13.9683, 0.892, 19.33854, 15.10393),
    ],
)
def test_determine_average_soil_temperature(lag, prev_soil_temp, depth_factor, avg_annual_air_temp, soil_surface_temp):
    """tests _determine_average_soil_temperature() in soil_tests.py"""
    observe = SoilTemp._determine_average_soil_temperature(
        lag, prev_soil_temp, depth_factor, avg_annual_air_temp, soil_surface_temp
    )
    expect = (lag * prev_soil_temp) + (
        (1 - lag) * ((depth_factor * (avg_annual_air_temp - soil_surface_temp)) + soil_surface_temp)
    )
    assert observe == expect


# ---- Integration tests ----
@pytest.mark.parametrize(
    "radiation,avg_temp,min_temp,max_temp,plant_cover,snow_cover,avg_annual_temp",
    [
        (100.596, 20.6958, 16.395, 23.59568, 80.938, 2.3948, 9),
        (0, 0, 0, 0, 0, 0, 0),  # apocalypse
        (300, 28, 26, 31, 1200, 0, 12),
        (170, 24, 20, 30, 400, 3, 8.95),
    ],
)
def test_daily_soil_temperature_update(
    radiation: float,
    avg_temp: float,
    min_temp: float,
    max_temp: float,
    plant_cover: float,
    snow_cover: float,
    avg_annual_temp: float,
) -> None:
    """Tests that daily_soil_update() in soil_temp.py correctly uses and updates all functions."""
    # Initialize objects
    data = SoilData(field_size=1.0)
    incorp = SoilTemp(data)

    # Mock helper functions
    incorp._determine_maximum_damping_depth = MagicMock(return_value=1000)
    incorp._determine_scaling_factor = MagicMock(return_value=0.35)
    incorp._determine_damping_depth = MagicMock(return_value=1995)
    incorp._determine_radiation_factor = MagicMock(return_value=0.5)
    incorp._determine_bare_soil_surface_temp = MagicMock(return_value=20)
    incorp._determine_cover_weighting_factor = MagicMock(return_value=0.5)
    incorp._determine_soil_surface_temp = MagicMock(return_value=18.5)
    incorp._determine_depth_factor = MagicMock(return_value=0.5)
    incorp._determine_average_soil_temperature = MagicMock(return_value=14)

    # Record expected previous day temperature values
    expect_prev_temps = []
    for layer in incorp.data.soil_layers:
        expect_prev_temps.append(layer.temperature)

    # Run method
    incorp.daily_soil_temperature_update(
        radiation,
        avg_temp,
        min_temp,
        max_temp,
        plant_cover,
        snow_cover,
        avg_annual_temp,
    )

    # Check everything
    incorp._determine_maximum_damping_depth.assert_called_with(incorp.data.profile_bulk_density)
    incorp._determine_scaling_factor.assert_called_with(
        incorp.data.profile_soil_water_content,
        incorp.data.profile_bulk_density,
        incorp.data.soil_layers[-1].bottom_depth,
    )
    incorp._determine_damping_depth.assert_called_with(1000, 0.35)
    incorp._determine_radiation_factor.assert_called_with(radiation, incorp.data.albedo)
    incorp._determine_bare_soil_surface_temp.assert_called_with(0.5, avg_temp, min_temp, max_temp)
    incorp._determine_cover_weighting_factor.assert_called_with(plant_cover, snow_cover)
    incorp._determine_soil_surface_temp.assert_called_with(0.5, incorp.data.soil_layers[0].previous_day_temperature, 20)

    assert incorp._determine_depth_factor.call_count == len(data.soil_layers)
    assert incorp._determine_average_soil_temperature.call_count == len(data.soil_layers)
    for layer_index in range(len(incorp.data.soil_layers)):
        assert 14 == incorp.data.soil_layers[layer_index].temperature
        assert expect_prev_temps[layer_index] == incorp.data.soil_layers[layer_index].previous_day_temperature

    # Run method a second time for expanded code coverage
    incorp.daily_soil_temperature_update(
        radiation,
        avg_temp,
        min_temp,
        max_temp,
        plant_cover,
        snow_cover,
        avg_annual_temp,
    )

    # Re-check everything
    incorp._determine_maximum_damping_depth.assert_called_with(incorp.data.profile_bulk_density)
    incorp._determine_scaling_factor.assert_called_with(
        incorp.data.profile_soil_water_content,
        incorp.data.profile_bulk_density,
        incorp.data.soil_layers[-1].bottom_depth,
    )
    incorp._determine_damping_depth.assert_called_with(1000, 0.35)
    incorp._determine_radiation_factor.assert_called_with(radiation, incorp.data.albedo)
    incorp._determine_bare_soil_surface_temp.assert_called_with(0.5, avg_temp, min_temp, max_temp)
    incorp._determine_cover_weighting_factor.assert_called_with(plant_cover, snow_cover)
    incorp._determine_soil_surface_temp.assert_called_with(0.5, expect_prev_temps[0], 20)
    assert incorp._determine_depth_factor.call_count == len(data.soil_layers) * 2
    assert incorp._determine_average_soil_temperature.call_count == len(data.soil_layers) * 2
    for layer in incorp.data.soil_layers:
        assert 14 == layer.temperature
        assert 14 == layer.previous_day_temperature

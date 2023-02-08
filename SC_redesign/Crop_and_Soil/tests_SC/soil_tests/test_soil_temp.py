import pytest

from SC_redesign.Crop_and_Soil.soil.soil_temp import *


# --- Static function tests ---
@pytest.mark.parametrize("bulk_density", [
    0,
    1.89,
    1.23223,
    1.5321,
    1.4013,
])
def test_determine_maximum_damping_depth(bulk_density):
    """tests _determine_maximum_damping_depth() in soil_temp.py"""
    observe = SoilTemp._determine_maximum_damping_depth(bulk_density)
    expect = 1000 + ((2500 * bulk_density) / (bulk_density + (686 * exp(-5.63 * bulk_density))))
    # print(observe)
    assert observe == expect


@pytest.mark.parametrize("water_content,density,bottom_depth", [
    (21.456, 1.78, 2000),
    (24.534, 1.8694, 2130),
    (50.67, 2.0194, 1924),
    (45.8395, 1.543, 1874),
])
def test_determine_scaling_factor(water_content, density, bottom_depth):
    """tests _determine_scaling_factor() in soil_temp.py"""
    observe = SoilTemp._determine_scaling_factor(water_content, density, bottom_depth)
    bottom_term = (0.356 - (0.144 * density)) * bottom_depth
    expect = water_content / bottom_term
    # print(observe)
    assert observe == expect


@pytest.mark.parametrize("max_damping_depth,scaling_factor", [
    (1000, 0.189),
    (3000, 0.3942),
    (2457, 0.23423),
    (2958, 0.3058),
])
def test_determine_damping_depth(max_damping_depth, scaling_factor):
    """tests _determine_damping_depth() in soil_temp.py"""
    observe = SoilTemp._determine_damping_depth(max_damping_depth, scaling_factor)
    expect = max_damping_depth * exp(log(500 / max_damping_depth) * ((1 - scaling_factor) / (1 + scaling_factor))**2)
    # print(observe)
    assert observe == expect


@pytest.mark.parametrize("center_depth,damping_depth", [
    (14, 2198.9583),
    (80, 2003.95),
    (158, 1894.596),
    (365, 2304.786),
    (904, 1569.852323),
    (1784, 1995.38547),
    (2104, 2058.5853),
    (2594.4859, 2394.5857),
])
def test_determine_depth_factor(center_depth, damping_depth):
    """tests _determine_depth_factor() in soil_temp.py"""
    observe = SoilTemp._determine_depth_factor(center_depth, damping_depth)
    expect = (center_depth / damping_depth) / ((center_depth / damping_depth) + exp(-0.867 - (2.078 * (center_depth /
                                                                                                       damping_depth))))
    # print(observe)
    assert observe == expect


@pytest.mark.parametrize("radiation,albedo", [
    (102.3, 0.16),
    (0, 0),
    (303.564, 0.18),
    (78.9837, 0.199),
    (586, 0.2354),
    (238.384, 0.3885),
])
def test_determine_radiation_factor(radiation, albedo):
    """tests _determine_radiation_factor() in soil_temp.py"""
    observe = SoilTemp._determine_radiation_factor(radiation, albedo)
    expect_top = radiation * (1 - albedo) - 14
    expect = expect_top / 20
    # print(observe)
    assert observe == expect


@pytest.mark.parametrize("radiation,avg_temp,min_temp,max_temp", [
    (20, 21, 18, 23),
    (18.93845, 23.985, 28, 16),
    (12.9983, 26.848, 30, 23),
    (35.69458, 22.3847, 24, 17),
    (41.3932, 16.93845, 19, 10),
])
def test_determine_bare_soil_surface_temp(radiation, avg_temp, min_temp, max_temp):
    """tests _determine_bare_soil_surface_temp() in soil_tests.py"""
    observed = SoilTemp._determine_bare_soil_surface_temp(radiation, avg_temp, min_temp, max_temp)
    expect = avg_temp + radiation * ((max_temp - min_temp) / 2)
    assert observed == expect


@pytest.mark.parametrize("plant_cover,snow_cover", [
    (137.93, 13.95),
    (102.495, 18.9585),
    (0, 0),
    (32.495, 56.94385),
    (203.0459, 34.958),
])
def test_determine_cover_weighting_factor(plant_cover, snow_cover):
    observe = SoilTemp._determine_cover_weighting_factor(plant_cover, snow_cover)
    plant_factor = plant_cover / (plant_cover + exp(7.563 - (0.001297 * plant_cover)))
    snow_factor = snow_cover / (snow_cover + exp(6.055 - (0.3002 * snow_cover)))
    expect = max(plant_factor, snow_factor)
    print(observe)
    assert observe == expect


@pytest.mark.parametrize("cover_factor,previous_top_layer_temp,bare_surface_temp", [
    (0, 0, 0),
    (0.5, 12, 15),
    (0.88, 23, 28),
    (0.11, -3, -1),
    (0.42495, 17.8547, 20.4857),
])
def test_determine_soil_surface_temp(cover_factor, previous_top_layer_temp, bare_surface_temp):
    observe = SoilTemp._determine_soil_surface_temp(cover_factor, previous_top_layer_temp, bare_surface_temp)
    expect = (cover_factor * previous_top_layer_temp) + ((1 - cover_factor) * bare_surface_temp)
    assert observe == expect

import pytest
from math import log, floor
from unittest.mock import MagicMock

from SC_redesign.Crop_and_Soil.soil.infiltration import *


# --- static function tests ---
@pytest.mark.parametrize("curve_num_2", [
    10,
    40,
    60,
    77,
    81,
    95,
])
def test_determine_curve_number_1(curve_num_2):
    """test _determine_curve_number_1() in infiltration.py"""
    observe = Infiltration._determine_first_moisture_condition_parameter(curve_num_2)
    expect = curve_num_2 - \
             ((20 * (100 - curve_num_2)) / (100 - curve_num_2 + exp(2.533 - (0.0636 * (100 - curve_num_2)))))
    assert expect == observe


@pytest.mark.parametrize("curve_num_2", [
    10,
    40,
    60,
    77,
    81,
    95,
])
def test_determine_curve_number_3(curve_num_2):
    """test _determine_curve_number_3() in infiltration.py"""
    observe = Infiltration._determine_third_moisture_condition_parameter(curve_num_2)
    expect = curve_num_2 * exp(0.00673 * (100 - curve_num_2))
    assert expect == observe


@pytest.mark.parametrize("curve_num", [
    10,
    20,
    40,
    56,
    78,
    99,
])
def test_determine_max_retention_parameter(curve_num):
    """test _determine_retention_parameter() in infiltration.py"""
    observe = Infiltration._determine_retention_parameter_for_moisture_condition(curve_num)
    expect = (1000 / curve_num) - 10
    expect = expect * 25.4
    assert expect == observe


@pytest.mark.parametrize("field_capacity,saturation,max_retention_param,curve_3_retention_param", [
    (0.8, 1.4, 380, 250),
    (1.1, 2.8, 459.84, 345.134),
    (0.2, 0.83, 138.9, 100.3),
    (0.74, 0.965, 608.783, 435.678),
])
def test_determine_second_shape_coefficient(field_capacity, saturation, max_retention_param, curve_3_retention_param):
    """test _determine_second_shape_coefficient() in infiltration.py"""
    top_first_term = log((field_capacity / (1 - (curve_3_retention_param * (max_retention_param ** (-1))))) -
                         field_capacity)
    top_second_term = log((saturation / (1 - (2.54 * (max_retention_param ** (-1))))) - saturation)
    expect = (top_first_term - top_second_term) / (saturation - field_capacity)
    observe = Infiltration._determine_second_shape_coefficient(field_capacity, saturation, max_retention_param,
                                                               curve_3_retention_param)
    assert pytest.approx(observe) == expect


@pytest.mark.parametrize("field_capacity,max_retention_param,curve_3_retention_param,second_shape_coeff", [
    (0.8, 400, 210, 21.44),
    (0.9, 506, 453, 29.889),
    (0.4, 254, 167, 12.343),
    (1.5, 607.34, 587.4345, 37.891),
])
def test_determine_first_shape_coefficient(field_capacity, max_retention_param, curve_3_retention_param,
                                           second_shape_coeff):
    """test _determine_first_shape_coefficient() in infiltration.py"""
    observe = Infiltration._determine_first_shape_coefficient(field_capacity, max_retention_param,
                                                              curve_3_retention_param, second_shape_coeff)
    expect = log((field_capacity / (1 - (curve_3_retention_param / max_retention_param))) - field_capacity) + \
             (second_shape_coeff * field_capacity)
    assert expect == observe


@pytest.mark.parametrize("water_content,max_retention_param,first_shape_coefficient,second_shape_coefficient", [
    (0.4, 400, 26.834, 24.586),
    (0.85, 450, 29.596, 28.495),
    (0.61, 502, 30.502, 27.8586),
    (0, 104, 15.678, 12.395),
])
def test_determine_retention_parameter(water_content, max_retention_param, first_shape_coefficient,
                                       second_shape_coefficient):
    """test _determine_retention_parameter() in infiltration.py"""
    observe = Infiltration._determine_retention_parameter(water_content, max_retention_param, first_shape_coefficient,
                                                          second_shape_coefficient)
    expect_quotient = water_content / (water_content + exp(first_shape_coefficient - (second_shape_coefficient *
                                                                                      water_content)))
    expect = max_retention_param * (1 - expect_quotient)
    assert observe == expect


@pytest.mark.parametrize("max_retention_param,retention_param", [
    (400, 388),
    (406.596, 391.9495),
    (201.495, 198.596),
    (306.295, 294.96),
])
def test_determine_frozen_retention_parameter(max_retention_param, retention_param):
    """test _determine_frozen_retention_param() in infiltration.py"""
    observe = Infiltration._determine_frozen_retention_parameter(max_retention_param, retention_param)
    expect = max_retention_param * (1 - exp(-0.000862 * retention_param))
    assert expect == observe


@pytest.mark.parametrize("slope_frac,curve_2,curve_3", [
    (0.01, 40.0, 38),
    (0.15, 51.3, 45.6),
    (0.114, 49.8, 45.9),
    (0.09, 31.5, 29.5),
    (0.123, 67.4, 58.7),
])
def test_determine_curve_2_adjusted(slope_frac, curve_2, curve_3):
    observe = Infiltration._determine_second_moisture_condition_adjusted(slope_frac, curve_2, curve_3)
    expect = (((curve_3 - curve_2) / 3) * (1 - (2 * exp(-13.86 * slope_frac)))) + curve_2
    assert expect == observe


@pytest.mark.parametrize("rainfall,retention_param", [
    (1.3, 12.5),
    (8.3, 56.939),
    (4.3, 20.118),
    (0, 0),
    (12.6, 40.95),
])
def test_determine_runoff(rainfall, retention_param):
    """test _determine_excess_rainfall() in infiltration.py"""
    observe = Infiltration._determine_accumulated_runoff(rainfall, retention_param)
    if rainfall <= (0.2 * retention_param):
        assert 0 == observe
    else:
        expect_top = (rainfall - 0.2 * retention_param) ** 2
        expect_bottom = rainfall + (0.8 * retention_param)
        assert (expect_top / expect_bottom) == observe


@pytest.mark.parametrize(
    "prev_retention_param,potential_evapotranspiration,max_retention_param,rainfall,runoff,coefficient",
    [
        (12.4, 1.6, 16.8, 1.3, 0.4, 0.83),  # all arbitrary coefficients
        (14.8, 2.4, 20.1, 1.8, 1.1, 0.72),
        (8.93, 1.02, 12.19, 0.3, 0.05, 0.91),
    ])
def test_determine_updated_retention_parameter(prev_retention_param, potential_evapotranspiration, max_retention_param,
                                               rainfall, runoff, coefficient):
    """test _determine_updated_retention_parameter() in infiltration.py"""
    observe = Infiltration._determine_updated_retention_parameter(prev_retention_param, potential_evapotranspiration,
                                                                  max_retention_param, rainfall, runoff, coefficient)
    expect = prev_retention_param + (potential_evapotranspiration * exp(((-1) * coefficient * prev_retention_param) /
                                                                        max_retention_param)) - rainfall + runoff
    assert pytest.approx(observe) == expect


@pytest.mark.parametrize("retention_param", [
    25,
    9.54,
    1.23,
    15.395,
])
def test_determine_moisture_condition_parameter(retention_param):
    """test _determine_moisture_condition_parameter() in infiltration.py"""
    observe = Infiltration._determine_moisture_condition_parameter(retention_param)
    expect_bottom = retention_param + 254
    expect = 25400 / expect_bottom
    assert expect == observe


# --- Integration tests ----
@pytest.mark.parametrize("second_moisture_parameter,rainfall,is_top_frozen,coefficient", [
    (40, 1.4, False, 0.91),
    (59, 3.5, True, 0.4858),
    (14, 2.5, False, 0.694),
    (36, 0.3, False, 0.58392),
    (96, 4.697, False, 0.5938),
    (76, 2.45, False, 0.9694),
])
def test_infiltrate(second_moisture_parameter, rainfall, is_top_frozen, coefficient):
    """test that infiltrate() correctly stores all values in SoilData object and calls all the methods it should"""
    # initialize objects
    if is_top_frozen:
        data = SoilData(potential_evapotranspiration=1.5, average_subbasin_slope=0.07, previous_retention_parameter=27,
                        soil_layers=[LayerData(top_depth=0, bottom_depth=10, temperature=-1)])
    else:
        data = SoilData(potential_evapotranspiration=1.5, average_subbasin_slope=0.07, previous_retention_parameter=27,
                        soil_layers=[LayerData(top_depth=0, bottom_depth=10, temperature=14)])
    incorp = Infiltration(data)
    assert incorp.data.potential_evapotranspiration == 1.5
    assert incorp.data.average_subbasin_slope == 0.07
    assert incorp.data.previous_retention_parameter == 27

    # mock helper functions
    incorp._determine_third_moisture_condition_parameter = MagicMock(return_value=25)
    incorp._determine_second_moisture_condition_adjusted = MagicMock(return_value=40)
    incorp._determine_first_moisture_condition_parameter = MagicMock(return_value=15)
    incorp._determine_retention_parameter_for_moisture_condition = MagicMock(return_value=300)
    incorp._determine_second_shape_coefficient = MagicMock(return_value=0.8)
    incorp._determine_first_shape_coefficient = MagicMock(return_value=0.85)
    incorp._determine_retention_parameter = MagicMock(return_value=23)
    incorp._determine_frozen_retention_parameter = MagicMock(return_value=20)
    incorp._determine_updated_retention_parameter = MagicMock(return_value=21.34)
    incorp._determine_accumulated_runoff = MagicMock(return_value=0.95)
    incorp._determine_moisture_condition_parameter = MagicMock(return_value=50)

    # run main method
    incorp.infiltrate(second_moisture_parameter, rainfall, coefficient)

    # assertions
    assert incorp._determine_third_moisture_condition_parameter.call_count == 2
    assert incorp._determine_second_moisture_condition_adjusted.call_count == 1
    assert incorp._determine_first_moisture_condition_parameter.call_count == 1
    assert incorp._determine_retention_parameter_for_moisture_condition.call_count == 2
    assert incorp._determine_second_shape_coefficient.call_count == 1
    assert incorp._determine_first_shape_coefficient.call_count == 1
    assert incorp._determine_retention_parameter.call_count == 1
    if is_top_frozen:
        assert incorp._determine_frozen_retention_parameter.call_count == 1
    else:
        assert incorp._determine_frozen_retention_parameter.call_count == 0
    assert incorp._determine_accumulated_runoff.call_count == 1
    assert incorp._determine_updated_retention_parameter.call_count == 1
    assert incorp._determine_moisture_condition_parameter.call_count == 1
    assert incorp.data.previous_retention_parameter == 21.34
    assert incorp.data.moisture_condition_parameter == 50
    assert incorp.data.accumulated_runoff == 0.95

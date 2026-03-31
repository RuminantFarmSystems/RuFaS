from math import exp, log
from unittest.mock import MagicMock, call, patch

import pytest

from RUFAS.biophysical.field.soil.infiltration import Infiltration
from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.soil_data import SoilData


# --- static function tests ---
@pytest.mark.parametrize(
    "curve_num_2",
    [
        10,
        40,
        60,
        77,
        81,
        95,
    ],
)
def test_determine_curve_number_1(curve_num_2):
    """test _determine_curve_number_1() in infiltration.py"""
    observe = Infiltration._determine_first_moisture_condition_parameter(curve_num_2)
    expect = curve_num_2 - (
        (20 * (100 - curve_num_2)) / (100 - curve_num_2 + exp(2.533 - (0.0636 * (100 - curve_num_2))))
    )
    assert expect == observe


@pytest.mark.parametrize(
    "curve_num_2",
    [
        10,
        40,
        60,
        77,
        81,
        95,
    ],
)
def test_determine_curve_number_3(curve_num_2):
    """test _determine_curve_number_3() in infiltration.py"""
    observe = Infiltration._determine_third_moisture_condition_parameter(curve_num_2)
    expect = curve_num_2 * exp(0.00673 * (100 - curve_num_2))
    assert expect == observe


@pytest.mark.parametrize(
    "curve_num",
    [
        10,
        20,
        40,
        56,
        78,
        99,
    ],
)
def test_determine_max_retention_parameter(curve_num):
    """test _determine_retention_parameter() in infiltration.py"""
    observe = Infiltration._determine_retention_parameter_for_moisture_condition(curve_num)
    expect = (1000 / curve_num) - 10
    expect = expect * 25.4
    assert expect == observe


@pytest.mark.parametrize(
    "field_capacity,saturation,max_retention_param,curve_3_retention_param",
    [
        (0.8, 1.4, 380, 250),
        (1.1, 2.8, 459.84, 345.134),
        (0.2, 0.83, 138.9, 100.3),
        (0.74, 0.965, 608.783, 435.678),
    ],
)
def test_determine_second_shape_coefficient(field_capacity, saturation, max_retention_param, curve_3_retention_param):
    """test _determine_second_shape_coefficient() in infiltration.py"""
    top_first_term = log(
        (field_capacity / (1 - (curve_3_retention_param * (max_retention_param ** (-1))))) - field_capacity
    )
    top_second_term = log((saturation / (1 - (2.54 * (max_retention_param ** (-1))))) - saturation)
    expect = (top_first_term - top_second_term) / (saturation - field_capacity)
    observe = Infiltration._determine_second_shape_coefficient(
        field_capacity, saturation, max_retention_param, curve_3_retention_param
    )
    assert pytest.approx(observe) == expect


@pytest.mark.parametrize(
    "field_capacity,max_retention_param,curve_3_retention_param,second_shape_coeff",
    [
        (0.8, 400, 210, 21.44),
        (0.9, 506, 453, 29.889),
        (0.4, 254, 167, 12.343),
        (1.5, 607.34, 587.4345, 37.891),
    ],
)
def test_determine_first_shape_coefficient(
    field_capacity, max_retention_param, curve_3_retention_param, second_shape_coeff
):
    """test _determine_first_shape_coefficient() in infiltration.py"""
    observe = Infiltration._determine_first_shape_coefficient(
        field_capacity, max_retention_param, curve_3_retention_param, second_shape_coeff
    )
    expect = log((field_capacity / (1 - (curve_3_retention_param / max_retention_param))) - field_capacity) + (
        second_shape_coeff * field_capacity
    )
    assert expect == observe


@pytest.mark.parametrize(
    "water_content,max_retention_param,first_shape_coefficient,second_shape_coefficient",
    [
        (0.4, 400, 26.834, 24.586),
        (0.85, 450, 29.596, 28.495),
        (0.61, 502, 30.502, 27.8586),
        (0, 104, 15.678, 12.395),
    ],
)
def test_determine_retention_parameter(
    water_content,
    max_retention_param,
    first_shape_coefficient,
    second_shape_coefficient,
):
    """test _determine_retention_parameter() in infiltration.py"""
    observe = Infiltration._determine_retention_parameter(
        water_content,
        max_retention_param,
        first_shape_coefficient,
        second_shape_coefficient,
    )
    expect_quotient = water_content / (
        water_content + exp(first_shape_coefficient - (second_shape_coefficient * water_content))
    )
    expect = max_retention_param * (1 - expect_quotient)
    assert observe == expect


@pytest.mark.parametrize(
    "max_retention_param,retention_param",
    [
        (400, 388),
        (406.596, 391.9495),
        (201.495, 198.596),
        (306.295, 294.96),
    ],
)
def test_determine_frozen_retention_parameter(max_retention_param, retention_param):
    """test _determine_frozen_retention_param() in infiltration.py"""
    observe = Infiltration._determine_frozen_retention_parameter(max_retention_param, retention_param)
    expect = max_retention_param * (1 - exp(-0.000862 * retention_param))
    assert expect == observe


@pytest.mark.parametrize(
    "rainfall,retention_param",
    [
        (1.3, 12.5),
        (8.3, 56.939),
        (4.3, 20.118),
        (0, 0),
        (12.6, 40.95),
    ],
)
def test_determine_runoff(rainfall, retention_param):
    """test _determine_excess_rainfall() in infiltration.py"""
    observe = Infiltration._determine_accumulated_runoff(rainfall, retention_param)
    if rainfall <= (0.2 * retention_param):
        assert 0 == observe
    else:
        expect_top = (rainfall - 0.2 * retention_param) ** 2
        expect_bottom = rainfall + (0.8 * retention_param)
        assert (expect_top / expect_bottom) == observe


# --- Integration tests ----
@pytest.mark.parametrize(
    "rainfall,is_top_frozen,expected_runoff,expected_infiltration,expected_total_runoff",
    [
        (1.4, False, 1.4, 0.0, 2.7),
        (3.5, True, 3.0, 0.5, 4.3),
        (20.0, False, 3.0, 17.0, 4.3),
        (0.0, False, 0.0, 0.0, 1.3),
    ],
)
def test_infiltrate(
    rainfall: float,
    is_top_frozen: bool,
    expected_runoff: float,
    expected_infiltration: float,
    expected_total_runoff: float,
) -> None:
    """Test that infiltrate() correctly stores all values in SoilData object and calls all the methods it should."""
    surface_layer = MagicMock(LayerData)
    if is_top_frozen:
        setattr(surface_layer, "temperature", -1.0)
    else:
        setattr(surface_layer, "temperature", 15.0)
    setattr(surface_layer, "acceptable_percolation_amount", 1.0)
    setattr(surface_layer, "water_content", 8.0)
    data = MagicMock(SoilData)
    setattr(data, "soil_layers", [surface_layer])
    setattr(data, "second_moisture_condition_parameter", 85.0)
    setattr(data, "profile_saturation", 200.0)
    setattr(data, "profile_field_capacity", 125.0)
    setattr(data, "profile_soil_water_content", 115.0)
    setattr(data, "accumulated_runoff", 1.1)
    setattr(data, "infiltrated_water", 1.2)
    setattr(data, "annual_runoff_total", 1.3)
    incorp = Infiltration(data)

    with (
        patch(
            "RUFAS.biophysical.field.soil.infiltration.Infiltration._determine_third_moisture_condition_parameter",
            return_value=90,
        ) as third_curve_num,
        patch(
            "RUFAS.biophysical.field.soil.infiltration.Infiltration._determine_first_moisture_condition_parameter",
            return_value=10,
        ) as first_curve_num,
        patch(
            "RUFAS.biophysical.field.soil.infiltration.Infiltration."
            "_determine_retention_parameter_for_moisture_condition",
            return_value=0.5,
        ) as moisture_param,
        patch(
            "RUFAS.biophysical.field.soil.infiltration.Infiltration._determine_second_shape_coefficient",
            return_value=1.1,
        ) as second_shape,
        patch(
            "RUFAS.biophysical.field.soil.infiltration.Infiltration._determine_first_shape_coefficient",
            return_value=1.2,
        ) as first_shape,
        patch(
            "RUFAS.biophysical.field.soil.infiltration.Infiltration._determine_retention_parameter",
            return_value=0.6,
        ) as retention_param,
        patch(
            "RUFAS.biophysical.field.soil.infiltration.Infiltration._determine_frozen_retention_parameter",
            return_value=0.6,
        ) as frozen_retention_param,
        patch(
            "RUFAS.biophysical.field.soil.infiltration.Infiltration._determine_accumulated_runoff",
            return_value=3.0,
        ) as runoff,
    ):
        incorp.infiltrate(rainfall)

        third_curve_num.assert_called_once_with(85.0)
        first_curve_num.assert_called_once_with(85.0)
        retention_param_for_moisture_calls = [call(10), call(90)]
        moisture_param.assert_has_calls(retention_param_for_moisture_calls)
        second_shape.assert_called_once_with(125.0, 200.0, 0.5, 0.5)
        first_shape.assert_called_once_with(125.0, 0.5, 0.5, 1.1)
        retention_param.assert_called_once_with(115.0, 0.5, 1.2, 1.1)
        if is_top_frozen:
            frozen_retention_param.assert_called_once_with(0.5, 0.6)
        else:
            frozen_retention_param.assert_not_called()
        runoff.assert_called_once_with(rainfall, 0.6)

        assert incorp.data.accumulated_runoff == expected_runoff
        assert incorp.data.infiltrated_water == expected_infiltration
        assert incorp.data.annual_runoff_total == expected_total_runoff

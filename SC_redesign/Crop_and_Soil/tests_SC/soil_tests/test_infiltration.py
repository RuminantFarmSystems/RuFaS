import pytest

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
    observe = Infiltration._determine_curve_number_1(curve_num_2)
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
    observe = Infiltration._determine_curve_number_3(curve_num_2)
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
def test_determine_retention_parameter(curve_num):
    """test _determine_retention_parameter() in infiltration.py"""
    observe = Infiltration._determine_max_retention_parameter(curve_num)
    expect = (1000 / curve_num) - 10
    expect = expect * 25.4
    assert expect == observe


@pytest.mark.parametrize("rainfall, retention_param", [
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

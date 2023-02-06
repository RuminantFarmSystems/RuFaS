import pytest
from math import exp

from SC_redesign.Crop_and_Soil.soil.percolation import *


# --- Static function tests ---
@pytest.mark.parametrize("saturation,field_capacity,hydraulic_conductivity", [
    (4.3, 3.4, 9),
    (6.2, 5.4, 15.2),
    (100, 85, 10.014385),
    (3.456, 3.01443, 8.76849),
    (5.013, 4.104, 5.6097),
    (6.78, 4.56, 8.9607),
])
def test_determine_percolation_travel_time(saturation, field_capacity, hydraulic_conductivity):
    """tests _determine_percolation_travel_time() in percolation.py"""
    observe = Percolation._determine_percolation_travel_time(saturation, field_capacity, hydraulic_conductivity)
    expect = (saturation / hydraulic_conductivity) - (field_capacity / hydraulic_conductivity)
    assert pytest.approx(observe) == expect


@pytest.mark.parametrize("saturation,field_capacity,hydraulic_conductivity", [
    (4.3, 3.6, 0),
    (4.5, 4.1, -1.32),
])
def test_error_determine_percolation_travel_time(saturation, field_capacity, hydraulic_conductivity):
    """test that _determine_percolation_travel_time() correctly raises errors when invalid input is passed"""
    with pytest.raises(Exception):
        Percolation._determine_percolation_travel_time(saturation, field_capacity, hydraulic_conductivity)


@pytest.mark.parametrize("drainable_water,time_step,travel_time", [
    (30, 12, 0.25),
    (20, 8, 0.345),
    (22.45, 9.75, 0.28948),
    (46, 10.33, 0.31004),
    (48, 19.5, 0.28485),
])
def test_determine_percolation_to_next_layer(drainable_water, time_step, travel_time):
    """tests _determine_percolation_to_next_layer() in percolation.py"""
    observe = Percolation._determine_percolation_to_next_layer(drainable_water, time_step, travel_time)
    expect = 1 - exp((-1 * time_step) / travel_time)
    expect *= drainable_water
    assert observe == expect


@pytest.mark.parametrize("water_content,field_capacity_content,saturated_capacity_content", [
    (0.98, 0.83, 1.13),
    (0.68, 0.74, 0.99),
    (0.34, 0.68, 1.34),
    (1.21, 1.13, 1.21),
    (0.89, 0.78, 1.02),
])
def test_determine_if_percolation_allowed(water_content, field_capacity_content, saturated_capacity_content):
    observe = Percolation._determine_if_percolation_allowed(water_content, field_capacity_content,
                                                            saturated_capacity_content)
    if water_content > (field_capacity_content + (0.5 * (saturated_capacity_content - field_capacity_content))):
        assert True == observe
    else:
        assert False == observe

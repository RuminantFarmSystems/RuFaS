import pytest
from unittest.mock import MagicMock, patch

from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData
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


@pytest.mark.parametrize("water_content,field_capacity_content,saturated_capacity_content,high_seasonal_water_table", [
    (0.98, 0.83, 1.13, True),
    (0.68, 0.74, 0.99, True),
    (0.34, 0.68, 1.34, False),
    (1.21, 1.13, 1.21, True),
    (0.89, 0.78, 1.02, False),
])
def test_determine_if_percolation_allowed(water_content, field_capacity_content, saturated_capacity_content,
                                          high_seasonal_water_table):
    """tests _determine_if_percolation_allowed() in percolation.py"""
    observe = Percolation._determine_if_percolation_allowed(water_content, field_capacity_content,
                                                            saturated_capacity_content, high_seasonal_water_table)
    if not high_seasonal_water_table:
        assert True == observe
    elif (water_content > (field_capacity_content + (0.5 * (saturated_capacity_content - field_capacity_content)))) and \
            high_seasonal_water_table:
        assert True == observe
    else:
        assert False == observe


# --- Integration tests ----
@pytest.mark.parametrize("upper,lower", [
    (LayerData(top_depth=0, bottom_depth=15), LayerData(top_depth=15, bottom_depth=39)),
    (LayerData(top_depth=39, bottom_depth=83), LayerData(top_depth=83, bottom_depth=143)),
    (LayerData(top_depth=143, bottom_depth=567), LayerData(top_depth=567, bottom_depth=634)),
])
def test_percolate_between_layers(upper, lower):
    travel_time = Percolation._determine_percolation_travel_time(upper.saturation_content, upper.field_capacity_content,
                                                                 upper.saturated_hydraulic_conductivity)
    percolation_amount = Percolation._determine_percolation_to_next_layer(upper.excess_water_available, 24, travel_time)

    if upper.excess_water_available <= 0:
        expect = 0
    elif lower.acceptable_percolation_amount < percolation_amount:
        expect = lower.acceptable_percolation_amount
    else:
        expect = percolation_amount

    observe = Percolation._percolate_between_layers(24, upper, lower)

    # Assertions
    assert observe == expect

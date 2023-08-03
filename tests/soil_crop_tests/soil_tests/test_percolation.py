from typing import List

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from RUFAS.routines.field.soil.percolation import Percolation
from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.routines.field.soil.layer_data import LayerData
from math import exp


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
        assert observe is True
    elif (water_content > (field_capacity_content + (0.5 * (saturated_capacity_content - field_capacity_content)))) \
            and high_seasonal_water_table:
        assert observe is True
    else:
        assert observe is False


@pytest.mark.parametrize("time_step,excess_water_available,amount_to_percolate,acceptable_percolation_amount,expected",
                         [
                             (30, 3, 10, 5, 5),
                             (30, 3, 3, 10, 3),
                             (30, -5, 10, 5, 0)
                         ])
def test_percolate_between_layers(time_step: float, excess_water_available: float, amount_to_percolate: float,
                                  acceptable_percolation_amount: float, expected: float) -> None:
    """this function tests _percolate_between_layers() in Percolation.py"""
    upper_data = LayerData(top_depth=0, bottom_depth=20, field_size=1.33)
    lower_data = LayerData(top_depth=20, bottom_depth=87, saturation_point_water_concentration=0.1, field_size=1.33)
    with patch('RUFAS.routines.field.soil.layer_data.LayerData.excess_water_available', new_callable=PropertyMock,
               return_value=excess_water_available), \
         patch('RUFAS.routines.field.soil.layer_data.LayerData.acceptable_percolation_amount',
               new_callable=PropertyMock, return_value=acceptable_percolation_amount):

        Percolation._determine_percolation_travel_time = MagicMock()
        Percolation._determine_percolation_to_next_layer = MagicMock(return_value=amount_to_percolate)
        result = Percolation._percolate_between_layers(time_step, upper_data, lower_data)
        if excess_water_available <= 0:
            assert result == expected
        else:
            assert Percolation._determine_percolation_travel_time.call_count == 1
            assert Percolation._determine_percolation_to_next_layer.call_count == 1
            assert result == expected


# --- Integration tests ----
@pytest.mark.parametrize("can_percolate, expected", [
    (True, [4.7, 4.75, 21, 0.3]),
    (False, [5.0, 4.75, 21, 0])
])
def test_percolate(can_percolate: bool, expected: List[float]):
    """tests the main routine of percolation.py (percolate()) and check that it updates all values correctly"""
    # Initialize objects
    layers = [LayerData(top_depth=0, bottom_depth=39, field_size=1.33),
              LayerData(top_depth=39, bottom_depth=87, field_size=1.33),
              LayerData(top_depth=87, bottom_depth=217, field_size=1.33)]
    # Set soil water content of layers so that water actually percolates
    layers[0].water_content = 17
    layers[1].water_content = 21
    layers[2].water_content = 40
    data = SoilData(field_size=1.33, soil_layers=layers,
                    vadose_zone_layer=LayerData(top_depth=100000, bottom_depth=200000,
                                                soil_water_concentration=0, field_size=1.33))

    # Mock intermediate functions
    Percolation._determine_if_percolation_allowed = MagicMock(return_value=can_percolate)
    Percolation._determine_percolation_travel_time = MagicMock(return_value=0.245)
    Percolation._determine_percolation_to_next_layer = MagicMock(return_value=0.5)
    Percolation._percolate_between_layers = MagicMock(return_value=0.3)
    incorp = Percolation(data)
    # Record expected final values for soil water content in each layer and vadose zone
    # Top layer should lose 0.3 mm of water
    # Second layer gains then loses 0.3 mm of water
    # Third layer gains then loses 0.3 mm of water
    # Vadose zone starts empty, then gains 0.3 mm of water

    # Run function
    incorp.percolate(True)
    # Collect results
    observe = [incorp.data.soil_layers[0].water_content, incorp.data.soil_layers[1].water_content,
               incorp.data.soil_layers[2].water_content, incorp.data.vadose_zone_layer.water_content]
    # Assertions
    if can_percolate:
        assert observe == expected
        assert Percolation._determine_if_percolation_allowed.call_count == len(data.soil_layers)
        assert Percolation._percolate_between_layers.call_count == len(data.soil_layers)
        for layer in incorp.data.soil_layers:
            assert layer.percolated_water == 0.3
    else:
        assert observe == expected

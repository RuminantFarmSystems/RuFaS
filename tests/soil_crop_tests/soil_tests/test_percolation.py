from typing import List

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from RUFAS.routines.field.soil.percolation import Percolation
from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.routines.field.soil.layer_data import LayerData
from math import exp, inf


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
@pytest.mark.parametrize("infiltration,water_contents,acceptable_percolation_amounts,percolated_water,"
                         "expected_water_contents", [
                             (10.0, [5.0, 5.0, 5.0, 5.0], [3.0] * 4, [7.0, 4.0, 1.0, 0.0], [8.0, 8.0, 8.0, 6.0, 0.0]),
                             (4.0, [5.0, 5.0, 5.0, 5.0], [3.0] * 4, [1.0, 0.0, 0.0, 0.0], [8.0, 6.0, 5.0, 5.0, 0.0]),
                             (8.5, [6.0, 12.4, 19.3, 18.0], [1.3, 2.4, 5.0, 4.7], [7.2, 4.8, 0.0, 0.0],
                              [7.3, 14.8, 24.1, 18.0, 0.0]),
                             (20.0, [5.0, 5.0, 5.0, 5.0], [3.0] * 4, [17.0, 14.0, 11.0, 8.0],
                              [8.0, 8.0, 8.0, 8.0, 8.0]),
                             (20.0, [8.0, 8.0, 8.0, 8.0], [0.0] * 4, [20.0] * 4, [8.0, 8.0, 8.0, 8.0, 20.0])
                         ])
def test_percolate_excess_water(infiltration: float, water_contents: list[float],
                                acceptable_percolation_amounts: list[float], percolated_water: list[float],
                                expected_water_contents: list[float]) -> None:
    """Tests that extreme levels of infiltration are handled correctly."""
    layers = []
    for index in range(4):
        new_layer = LayerData(top_depth=0, bottom_depth=100, field_size=3.0)
        new_layer.water_content = water_contents[index]
        layers.append(new_layer)
    vadose_zone = MagicMock(LayerData)
    vadose_zone.acceptable_percolation_amount = inf
    vadose_zone.water_content = 0.0
    soil_data = MagicMock(SoilData)
    soil_data.soil_layers = layers
    soil_data.vadose_zone_layer = vadose_zone
    soil_data.infiltrated_water = infiltration
    percolation = Percolation(soil_data)
    with patch("RUFAS.routines.field.soil.layer_data.LayerData.acceptable_percolation_amount",
               new_callable=PropertyMock, side_effect=acceptable_percolation_amounts):
        percolation._percolate_excess_water()

    for index, layer in enumerate(percolation.data.soil_layers):
        assert pytest.approx(layer.water_content) == expected_water_contents[index]
        assert pytest.approx(layer.percolated_water) == percolated_water[index]
    assert percolation.data.vadose_zone_layer.water_content == expected_water_contents[-1]


@pytest.fixture
def mock_soil_data() -> SoilData:
    field_size = 1.33
    soil_layers = [
        LayerData(top_depth=0, bottom_depth=20, field_size=field_size),
        LayerData(top_depth=20, bottom_depth=200, field_size=field_size),
        LayerData(top_depth=200, bottom_depth=3500, field_size=field_size)
    ]
    soil_data = SoilData(field_size=1.33, soil_layers=soil_layers)
    soil_data.set_vectorized_layer_attribute("water_content", [10.0, 50.0, 100.0])
    return soil_data


@pytest.mark.parametrize("can_percolate,seasonal_high_water_table,infiltration,excessive_infiltration,expected", [
    (True, True, 0.0, False, [7.0, 50.0, 100.0, 3.0]),
    (False, False, 0.0, False, [10.0, 50.0, 100.0, 0.0]),
    (True, False, 1.0, False, [8.0, 50.0, 100.0, 3.0]),
    (True, False, 10.0, True, [10.0, 50.0, 100.0])
])
def test_percolate(can_percolate: bool, seasonal_high_water_table: bool, infiltration: float,
                   excessive_infiltration: bool, expected: List[float], mock_soil_data: SoilData) -> None:
    """Tests the main routine of percolation.py and check that it updates all values correctly."""
    mock_soil_data.infiltrated_water = infiltration
    incorp = Percolation(mock_soil_data)

    with patch("RUFAS.routines.field.soil.percolation.Percolation._determine_if_percolation_allowed",
               return_value=can_percolate) as percolation_allowed, \
            patch("RUFAS.routines.field.soil.percolation.Percolation._percolate_between_layers", return_value=3.0) as \
            percolate_between_layers, \
            patch.object(LayerData, "acceptable_percolation_amount", new_callable=PropertyMock, return_value=1.0), \
            patch.object(Percolation, "_percolate_excess_water", new_callable=MagicMock) as percolate_excess:
        incorp.percolate(seasonal_high_water_table)

    if excessive_infiltration:
        percolate_excess.assert_called_once()
        assert percolation_allowed.call_count == 0
        assert percolate_between_layers.call_count == 0
        assert mock_soil_data.get_vectorized_layer_attribute("water_content") == [10.0, 50.0, 100.0]
        assert mock_soil_data.vadose_zone_layer.water_content == 0.0
        assert mock_soil_data.get_vectorized_layer_attribute("percolated_water") == [0.0] * 3
    else:
        percolate_excess.assert_not_called()
        assert percolation_allowed.call_count == 3
        actual_percolation = mock_soil_data.get_vectorized_layer_attribute("percolated_water")
        if can_percolate:
            assert percolate_between_layers.call_count == 3
            assert actual_percolation == [3.0, 3.0, 3.0]
        else:
            percolate_between_layers.assert_not_called()
            assert actual_percolation == [0.0, 0.0, 0.0]

        actual_profile_contents = mock_soil_data.get_vectorized_layer_attribute("water_content")
        assert actual_profile_contents == expected[:-1]
        actual_vadose_content = mock_soil_data.vadose_zone_layer.water_content
        assert actual_vadose_content == expected[-1]

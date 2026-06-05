from math import exp
from typing import List
from unittest.mock import MagicMock, patch

import pytest

from RUFAS.biophysical.field.soil.evaporation import Evaporation
from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.soil_data import SoilData


@pytest.mark.parametrize(
    "max_soil_water_evap,depth",
    [
        (1.1, 0),
        (0, 0),
        (2.3, 4),
        (2.7, 6.3),
        (5.3256, 19),
    ],
)
def test_determine_depth_evaporative_demand(max_soil_water_evap, depth):
    observe = Evaporation._determine_depth_evaporative_demand(max_soil_water_evap, depth)
    expect = depth / (depth + exp(2.374 - (0.00713 * depth)))
    expect *= max_soil_water_evap
    assert observe == expect


@pytest.mark.parametrize(
    "max_soil_water_evap,top_depth,bottom_depth,compensation",
    [
        (1.2, 0, 3, 1),  # defaults
        (0.9, 4, 9, 0.78),  # default water contents, different esco
        (
            1.1,
            2,
            8,
            1.8,
        ),
        (1.5, 4, 12, 1),
        (2.1, 0, 15, 2.3),
    ],
)
def test_determine_layer_evaporative_demand(max_soil_water_evap, top_depth, bottom_depth, compensation):
    observe = Evaporation._determine_layer_evaporative_demand(
        max_soil_water_evap, top_depth, bottom_depth, compensation
    )
    expect_top_demand = Evaporation._determine_depth_evaporative_demand(max_soil_water_evap, top_depth)
    expect_bottom_demand = Evaporation._determine_depth_evaporative_demand(max_soil_water_evap, bottom_depth)
    assert (expect_bottom_demand - (expect_top_demand * compensation)) == observe


@pytest.mark.parametrize(
    "max_soil_water_evap,top_depth,bottom_depth,compensation",
    [
        (1, None, 2, 1),
        (1, -1.2, 4, 1),
        (1, 3, 2, 1),
        (1, 1, None, 1),
    ],
)
def test_determine_layer_evaporative_demand_error(max_soil_water_evap, top_depth, bottom_depth, compensation):
    with pytest.raises(Exception):
        Evaporation._determine_layer_evaporative_demand(max_soil_water_evap, top_depth, bottom_depth, compensation)


@pytest.mark.parametrize(
    "evap_demand,soil_water,field_water,wilting_water",
    [
        (0.3, 1.3, 1.5, 0.2),
        (0.8, 1.8, 1.6, 0.9),
        (1.4, 1.1, 2, 1),
        (1.1, 2.3, 2.5, 0.3),
    ],
)
def test_determine_evaporative_demand_reduced(evap_demand, soil_water, field_water, wilting_water):
    observe = Evaporation._determine_evaporative_demand_reduced(evap_demand, soil_water, field_water, wilting_water)
    if soil_water < field_water:
        expect = evap_demand * exp((2.5 * (soil_water - field_water)) / (field_water - wilting_water))
    else:
        expect = evap_demand
    assert expect == observe


@pytest.mark.parametrize(
    "reduced_evap_demand,soil_water,wilting_water",
    [
        (0.2, 1.3, 0.2),
        (0.5, 1.8, 0.9),
        (1.8, 1.1, 1),
        (1.1, 2.3, 0.3),
    ],
)
def test_determine_amount_water_removed(reduced_evap_demand, soil_water, wilting_water):
    observe = Evaporation._determine_amount_water_removed(reduced_evap_demand, soil_water, wilting_water)
    expect = min(reduced_evap_demand, 0.8 * (soil_water - wilting_water))
    assert expect == observe


@pytest.mark.parametrize(
    "max_evaporation,expected_evaporation,expected_loop_iterations,expected_water_contents,"
    "expected_water_evaporated",
    [
        (10, 2.8, 4, [0.8, 0.8, 0.8, 0.8], [0.7, 0.7, 0.7, 0.7]),
        (5.5, 2.8, 4, [0.8, 0.8, 0.8, 0.8], [0.7, 0.7, 0.7, 0.7]),
        (2.2, 2.2, 4, [0.8, 0.8, 0.8, 1.4], [0.7, 0.7, 0.7, 0.1]),
        (1.5, 1.5, 3, [0.8, 0.8, 1.4, 1.5], [0.7, 0.7, 0.1, 0.0]),
        (0, 0, 1, [1.5, 1.5, 1.5, 1.5], [0.0, 0.0, 0.0, 0.0]),
    ],
)
def test_evaporate(
    max_evaporation: float,
    expected_evaporation: float,
    expected_loop_iterations: int,
    expected_water_contents: List[float],
    expected_water_evaporated: List[float],
) -> None:
    """Tests that `evaporate()` evaporates the correct amount of water from the soil profile, and stores that amount
    properly"""
    data = SoilData(
        field_size=1.33,
        soil_layers=[
            LayerData(top_depth=0, bottom_depth=20, field_size=1.33),
            LayerData(top_depth=20, bottom_depth=50, field_size=1.33),
            LayerData(top_depth=50, bottom_depth=80, field_size=1.33),
            LayerData(top_depth=80, bottom_depth=200, field_size=1.33),
        ],
    )
    incorp = Evaporation(data)
    incorp.data.set_vectorized_layer_attribute("water_content", [1.5] * 4)
    incorp.data.set_vectorized_layer_attribute("soil_evaporation_compensation_coefficient", [0.9] * 4)
    incorp.data.set_vectorized_layer_attribute("evaporated_water_content", [1.1] * 4)

    path_str = "RUFAS.biophysical.field.soil.evaporation.Evaporation"
    with (
        patch(
            f"{path_str}._determine_layer_evaporative_demand",
            new_callable=MagicMock,
            return_value=0.8,
        ) as demand,
        patch(
            f"{path_str}._determine_evaporative_demand_reduced",
            new_callable=MagicMock,
            return_value=0.6,
        ) as reduced,
        patch(
            f"{path_str}._determine_amount_water_removed",
            new_callable=MagicMock,
            return_value=0.7,
        ) as removed,
    ):
        incorp.evaporate(max_evaporation)
        actual_water_contents = incorp.data.get_vectorized_layer_attribute("water_content")
        actual_water_evaporated = incorp.data.get_vectorized_layer_attribute("evaporated_water_content")

        assert demand.call_count == expected_loop_iterations
        assert reduced.call_count == expected_loop_iterations
        assert removed.call_count == expected_loop_iterations
        assert pytest.approx(actual_water_contents) == expected_water_contents
        assert pytest.approx(actual_water_evaporated) == expected_water_evaporated
        assert pytest.approx(incorp.data.water_evaporated) == expected_evaporation
        assert pytest.approx(incorp.data.annual_soil_evaporation_total) == expected_evaporation

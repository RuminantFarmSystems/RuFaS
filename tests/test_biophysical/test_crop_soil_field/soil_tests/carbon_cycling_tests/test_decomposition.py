import math
from unittest.mock import MagicMock

import pytest

from RUFAS.biophysical.field.soil.carbon_cycling.decomposition import Decomposition
from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.soil_data import SoilData


@pytest.mark.parametrize(
    "layer_temp",
    [
        -40.33,
        -20.1,
        0.0,
        70,  # lower values
        150,  # higher values
        88.8,  # arbitrary
    ],
)
def test_calc_temp_factor(
    layer_temp,
    x_inflection: float = 15.4,
    y_inflection: float = 11.75,
    point_distance: float = 29.7,
    inflection_slope=0.03,
    normalizer=20.80546,
):
    """ensures that temperature effect was calculated according to the formula in "pseudocode_soil" S.6.A.1"""
    expect = max(
        0.0,
        (
            y_inflection
            + (point_distance / math.pi) * math.atan(math.pi * inflection_slope * (layer_temp - x_inflection))
        )
        / normalizer,
    )
    assert Decomposition._calc_temp_factor(layer_temp) == expect


@pytest.mark.parametrize(
    "water_factor",
    [
        15,  # lower values
        13,  # higher values
        16.6,  # arbitrary
        0.0,
        1.333,
        4.8,
    ],
)
def test_calc_moisture_factor(
    water_factor,
    a_term: float = 0.55,
    b_term: float = 1.7,
    c_term: float = -0.007,
    first_exponent=6.648115,
    second_exponent=3.22,
) -> None:
    """ensures that moisture effect was calculated according to the formula in "pseudocode_soil" S.6.A.2"""
    expected_base_1 = (water_factor - b_term) / (a_term - b_term)
    expected_base_2 = (water_factor - c_term) / (a_term - c_term)

    if expected_base_1 < 0.0:
        expected_term_1 = (-1) * ((-1 * expected_base_1) ** first_exponent)
    else:
        expected_term_1 = expected_base_1**first_exponent
    if expected_base_2 < 0.0:
        expected_term_2 = (-1) * ((-1 * expected_base_2) ** second_exponent)
    else:
        expected_term_2 = expected_base_2**second_exponent
    expected = expected_term_1 * expected_term_2

    if expected < 0.0:
        expected = 0.0

    assert Decomposition._calc_moisture_factor(water_factor) == expected


@pytest.mark.parametrize(
    "temp_average, layers",
    [
        (
            70,
            [
                LayerData(
                    top_depth=0,
                    bottom_depth=40,
                    soil_water_concentration=1.8,
                    field_capacity_water_concentration=1.6,
                    wilting_point_water_concentration=0.9,
                    field_size=1.33,
                ),
                LayerData(
                    top_depth=40,
                    bottom_depth=120,
                    soil_water_concentration=0.9,
                    field_size=1.33,
                    field_capacity_water_concentration=1.2,
                    wilting_point_water_concentration=0.8,
                ),
                LayerData(
                    top_depth=120,
                    bottom_depth=200,
                    soil_water_concentration=0.8,
                    field_size=1.33,
                    field_capacity_water_concentration=0.8,
                    wilting_point_water_concentration=0.3,
                ),
            ],
        ),  # lower values
        (
            150,
            [
                LayerData(
                    top_depth=0,
                    bottom_depth=30,
                    soil_water_concentration=2.8,
                    field_capacity_water_concentration=2.3,
                    wilting_point_water_concentration=1.8,
                    field_size=1.33,
                ),
                LayerData(
                    top_depth=30,
                    bottom_depth=150,
                    soil_water_concentration=1.9,
                    field_size=1.33,
                    field_capacity_water_concentration=1.8,
                    wilting_point_water_concentration=0.8,
                ),
                LayerData(
                    top_depth=150,
                    bottom_depth=220,
                    soil_water_concentration=0.8,
                    field_size=1.33,
                    field_capacity_water_concentration=1,
                    wilting_point_water_concentration=0.2,
                ),
            ],
        ),  # higher values
        (
            88.8,
            [
                LayerData(
                    top_depth=0,
                    bottom_depth=80,
                    soil_water_concentration=2.3,
                    field_size=1.33,
                    field_capacity_water_concentration=2.9,
                    wilting_point_water_concentration=1.8,
                ),
                LayerData(
                    top_depth=80,
                    bottom_depth=200,
                    soil_water_concentration=1.4,
                    field_size=1.33,
                    field_capacity_water_concentration=1.8,
                    wilting_point_water_concentration=0.8,
                ),
                LayerData(
                    top_depth=200,
                    bottom_depth=220,
                    soil_water_concentration=0.8,
                    field_size=1.33,
                    field_capacity_water_concentration=1,
                    wilting_point_water_concentration=0.6,
                ),
            ],
        ),  # arbitrary
    ],
)
def test_decompose(temp_average: int | float, layers: list[LayerData]) -> None:
    """ensures that all SoilData attributes were correctly updated"""
    data = SoilData(field_size=1.33, soil_layers=layers)
    decomp = Decomposition(data)
    Decomposition._calc_moisture_factor = MagicMock(return_value=1.89)
    Decomposition._calc_temp_factor = MagicMock(return_value=3.99)

    # calls function
    decomp.decompose()

    # making sure functions were called properly
    assert Decomposition._calc_temp_factor.call_count == len(layers)
    assert Decomposition._calc_moisture_factor.call_count == len(layers)

    for layer in data.soil_layers:
        assert layer.decomposition_moisture_effect == 1.89
        assert layer.decomposition_temperature_effect == 3.99

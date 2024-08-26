import pytest
from math import exp
from unittest.mock import patch, MagicMock, PropertyMock, call

from RUFAS.routines.field.soil.nitrogen_cycling.denitrification import Denitrification
from RUFAS.routines.field.soil.soil_data import SoilData


@pytest.mark.parametrize(
    "nitrates,denitrification_rate,temp_factor,carbon_proportion",
    [
        (78, 1.4, 0.88, 0.60),
        (104.55, 0.33, 0.233, 0.4455),
        (22.12, 0.0, 0.5561, 0.71223),
        (204.445, 3.0, 0.781, 0.22334),
        (0.0, 2.55, 0.1554, 0.39112),
    ],
)
def test_calculate_denitrification_amount(
    nitrates: float,
    denitrification_rate: float,
    temp_factor: float,
    carbon_proportion: float,
) -> None:
    """Tests that the amount of nitrified nitrates is calculated correctly."""
    actual = Denitrification._calculate_denitrification_amount(
        nitrates, denitrification_rate, temp_factor, carbon_proportion
    )
    expected_denitrification_factor = max(
        min(1 - exp(-1 * denitrification_rate * temp_factor * carbon_proportion * 100), 1.0), 0.0
    )
    expected = nitrates * expected_denitrification_factor
    assert actual == expected


def test_denitrify() -> None:
    """
    Tests that the main routine correctly gets the amount of nitrates nitrified and removes it from the nitrate pool.

    Notes
    -----
    This test achieves full code coverage by creating a soil profile in which the top (first), third, and fourth layers
    should have nitrate removed by denitrification, while the second layer should not. This is done by setting the
    `denitrification_threshold_water_content` attribute of the top, third, and fourth layers to be below the mocked
    `nutrient_cycling_water_factor`, and above for the second.

    """
    with patch.multiple(
        "RUFAS.routines.field.soil.layer_data.LayerData",
        nutrient_cycling_water_factor=PropertyMock(return_value=0.91),
        nutrient_cycling_temp_factor=PropertyMock(return_value=0.89),
    ):
        data = SoilData(field_size=1.8)
        incorp = Denitrification(data)
        incorp.data.set_vectorized_layer_attribute("nitrate_content", [35] * 4)
        incorp.data.set_vectorized_layer_attribute("denitrification_threshold_water_content", [0.5, 1.3, 0.5, 0.5])
        incorp.data.set_vectorized_layer_attribute("denitrification_rate_coefficient", [1.5] * 4)
        incorp.data.set_vectorized_layer_attribute("soil_overall_carbon_fraction", [0.65] * 4)
        incorp.data.set_vectorized_layer_attribute("nitrous_oxide_emissions", [0.11] * 4)
        incorp._calculate_denitrification_amount = MagicMock(return_value=15)

        incorp.denitrify()

        nitrification_amount_calls = [call(35, 1.5, 0.89, 0.65)] * 3
        incorp._calculate_denitrification_amount.assert_has_calls(nitrification_amount_calls)
        for index in [0, 2, 3]:
            assert incorp.data.soil_layers[index].nitrate_content == 20
            assert incorp.data.soil_layers[index].nitrous_oxide_emissions == 15
            assert incorp.data.soil_layers[index].annual_nitrous_oxide_emissions_total == 15
        assert incorp.data.soil_layers[1].nitrate_content == 35
        assert incorp.data.soil_layers[1].nitrous_oxide_emissions == 0.0
        assert incorp.data.soil_layers[1].annual_nitrous_oxide_emissions_total == 0

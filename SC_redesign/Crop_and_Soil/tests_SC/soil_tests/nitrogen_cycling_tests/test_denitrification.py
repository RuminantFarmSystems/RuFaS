import pytest
from math import exp
from unittest.mock import patch, MagicMock, PropertyMock, call

from SC_redesign.Crop_and_Soil.soil.nitrogen_cycling.denitrification import Denitrification
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData


# --- Static method test ---
@pytest.mark.parametrize("nitrates,denitrification_rate,temp_factor,percent_carbon", [
    (78, 1.4, 0.88, 60),
    (104.55, 0.33, 0.233, 44.55),
    (22.12, 0.0, 0.5561, 71.223),
    (204.445, 3.0, 0.781, 22.334),
    (0.0, 2.55, 0.1554, 39.112)
])
def test_calculate_nitrification_amount(nitrates: float, denitrification_rate: float, temp_factor: float,
                                        percent_carbon: float) -> None:
    """Tests that the amount of nitrified nitrates is calculated correctly."""
    observed = Denitrification._calculate_nitrification_amount(nitrates, denitrification_rate, temp_factor,
                                                               percent_carbon)
    expected_nitrification_factor = max(min(1 - exp(-1 * denitrification_rate * temp_factor * percent_carbon), 1.0),
                                        0.0)
    expected = nitrates * expected_nitrification_factor
    assert observed == expected


# --- Test main routine ---
def test_do_denitrification() -> None:
    """Tests that the main routine correctly gets the amount of nitrates nitrified and removes it from the nitrate
        pool."""
    with patch.multiple("SC_redesign.Crop_and_Soil.soil.layer_data.LayerData",
                        nutrient_cycling_water_factor=PropertyMock(return_value=0.91),
                        nutrient_cycling_temp_factor=PropertyMock(return_value=0.89)):
        data = SoilData(field_size=1.8)
        incorp = Denitrification(data)
        incorp.data.set_vectorized_layer_attribute("nitrate_content", [35] * 4)
        incorp.data.set_vectorized_layer_attribute("denitrification_threshold_water_content", [0.5, 1.3, 0.5, 0.5])
        incorp.data.set_vectorized_layer_attribute("denitrification_rate_coefficient", [1.5] * 4)
        incorp.data.set_vectorized_layer_attribute("soil_overall_carbon_fraction", [0.65] * 4)
        incorp._calculate_nitrification_amount = MagicMock(return_value=15)

        incorp.do_denitrification()

        nitrification_amount_calls = [call(35, 1.5, 0.89, 65)] * 3
        incorp._calculate_nitrification_amount.assert_has_calls(nitrification_amount_calls)
        for index in [0, 2, 3]:
            assert incorp.data.soil_layers[index].nitrate_content == 20
            assert incorp.data.soil_layers[index].annual_denitrified_nitrogen_total == 15
        assert incorp.data.soil_layers[1].nitrate_content == 35
        assert incorp.data.soil_layers[1].annual_denitrified_nitrogen_total == 0

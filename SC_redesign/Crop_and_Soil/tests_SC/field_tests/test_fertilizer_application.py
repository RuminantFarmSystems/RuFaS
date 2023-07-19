import pytest
from typing import List
from unittest.mock import MagicMock

from SC_redesign.Crop_and_Soil.field.fertilizer_application import FertilizerApplication


@pytest.mark.parametrize("phosphorus,fertilizer,inorganic_nitrogen_frac,ammonium_frac,organic_nitrogen_frac,expected", [
    (15, 90, 0.15, 0.44, 0.09, [7.56, 5.94, 4.05]),
    (22.1, 144, 0.33, 0.2, 0.06, [38.016, 9.504, 4.32]),
    (0, 0, 0, 0, 0, [0, 0, 0])
])
def test_apply_fertilizer(phosphorus: float, fertilizer: float, inorganic_nitrogen_frac: float, ammonium_frac: float,
                          organic_nitrogen_frac: float, expected: List[float]) -> None:
    """Tests that fertilizer is applied correctly."""
    field_size = 1.7
    fert_app = FertilizerApplication(field_size=field_size)
    fert_app.soil.data.soil_layers[0].nitrate_content = 0
    fert_app.soil.data.soil_layers[0].ammonium_content = 0
    fert_app.soil.data.soil_layers[0].fresh_organic_nitrogen_content = 0
    fert_app.soil.data.soil_layers[0].active_organic_nitrogen_content = 0

    fert_app.soil.phosphorus_cycling.fertilizer.add_fertilizer_phosphorus = MagicMock()

    fert_app.apply_fertilizer(phosphorus, fertilizer, inorganic_nitrogen_frac, ammonium_frac, organic_nitrogen_frac,
                              field_size)

    fert_app.soil.phosphorus_cycling.fertilizer.add_fertilizer_phosphorus.assert_called_once_with(phosphorus)
    assert pytest.approx(fert_app.soil.data.soil_layers[0].nitrate_content) == expected[0] / field_size
    assert pytest.approx(fert_app.soil.data.soil_layers[0].ammonium_content) == expected[1] / field_size
    assert pytest.approx(fert_app.soil.data.soil_layers[0].fresh_organic_nitrogen_content) == expected[2] / field_size
    assert pytest.approx(fert_app.soil.data.soil_layers[0].active_organic_nitrogen_content) == expected[2] / field_size

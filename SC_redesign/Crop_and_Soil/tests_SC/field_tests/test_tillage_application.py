import pytest
from unittest.mock import MagicMock
from typing import List

from SC_redesign.Crop_and_Soil.field.field_data import FieldData
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.field.tillage_application import TillageApplication


@pytest.mark.parametrize("data,attr_name,attr_value,incorp_frac,expected_remaining,expected_removed", [
    (SoilData(field_size=1.5), "machine_water_extractable_inorganic_phosphorus", 23, 0.35, 14.95, 8.05),
    (FieldData(), "current_residue", 45, 0.22, 35.1, 9.9),
    (SoilData(field_size=0.43), "available_phosphorus_pool", 13.55, 0.49, 6.9105, 6.6395)
])
def test_remove_amount_incorporated(data: object, attr_name: str, attr_value: float, incorp_frac: float,
                                    expected_remaining: float, expected_removed: float) -> None:
    """Tests that correct amount is removed and returned from the specified pool."""
    setattr(data, attr_name, attr_value)

    actual_removed = TillageApplication._remove_amount_incorporated(data, attr_name, incorp_frac)
    actual_remaining = getattr(data, attr_name)

    assert pytest.approx(actual_removed) == expected_removed
    assert pytest.approx(actual_remaining) == expected_remaining


@pytest.mark.parametrize("layers,field_size,pool_values,pool_name,till_depth,mix_frac,expected", [
    ([LayerData(field_size=1.3, top_depth=0, bottom_depth=20), LayerData(field_size=1.3, top_depth=20, bottom_depth=60),
      LayerData(field_size=1.3, top_depth=60, bottom_depth=180)], 1.3, [40, 50, 20], "nitrate_content", 120, 0.3,
     [33, 45, 32]),
    ([LayerData(field_size=1.4, top_depth=0, bottom_depth=20),
      LayerData(field_size=1.4, top_depth=20, bottom_depth=50)], 1.4, [30, 10], "active_inorganic_phosphorus_content",
     50, 0.25, [26.5, 13.5]),
    ([LayerData(field_size=2.1, top_depth=0, bottom_depth=20), LayerData(field_size=2.1, top_depth=20, bottom_depth=50),
      LayerData(field_size=2.1, top_depth=50, bottom_depth=110), LayerData(field_size=2.1, top_depth=110,
                                                                           bottom_depth=500)],
     2.1, [30, 10, 3, 2], "nitrate_content", 50, 0.25, [26.5, 13.5, 3, 2]),
    ([LayerData(field_size=1, top_depth=0, bottom_depth=20)], 1.0, [20], "fresh_organic_nitrogen_content", 20, 0.4,
     [20])
])
def test_mix_soil_layers(layers: List[LayerData], field_size: float, pool_values: List[float], pool_name: str,
                         till_depth: float, mix_frac: float, expected: List[float]) -> None:
    """Tests that stuff is correctly redistributed between different pools in the soil layer."""
    soil_data = SoilData(field_size=field_size, soil_layers=layers)
    soil_data.set_vectorized_layer_attribute(pool_name, pool_values)
    field_data = FieldData(field_size=field_size)
    tillage_app = TillageApplication(field_data, soil_data)
    print(tillage_app.soil_data.get_vectorized_layer_attribute(pool_name))

    tillage_app._mix_soil_layers(pool_name, till_depth, mix_frac)

    actual = tillage_app.soil_data.get_vectorized_layer_attribute(pool_name)
    print(actual)
    assert actual == expected

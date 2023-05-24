import pytest
from unittest.mock import MagicMock

from SC_redesign.Crop_and_Soil.field.field_data import FieldData
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


@pytest.mark.parametrize("data,surface_attr_name,incorp_frac,soil_attr_name,soil_attr_value", [
    (FieldData(), "current_residue", 0.33, "plant_root_residue", 13),
    (SoilData(field_size=1.0), "recalcitrant_phosphorus_pool", 0.44, "labile" 15)
])
def test_till_surface_pool_into_top_layer(data: object, surface_attr_name: str, incorp_frac: float, soil_attr_name: str,
                                          soil_attr_value: float) -> None:
    """Tests that pools in top layer of soil are correctly added to."""
    till_app = TillageApplication()
    setattr(till_app.soil_data.soil_layers[0], soil_attr_name, soil_attr_value)

    till_app._remove_amount_incorporate = MagicMock(return_value=3)
    expected_amount_in_soil = 3 + soil_attr_value

    till_app._till_surface_pool_into_top_layer(data, surface_attr_name, incorp_frac, soil_attr_name)
    actual_amount_in_soil = pytest.approx(getattr(till_app.soil_data.soil_layers[0], soil_attr_name))

    till_app._remove_amount_incorporate.assert_called_once_with(data, surface_attr_name, incorp_frac)
    assert actual_amount_in_soil == expected_amount_in_soil

from unittest.mock import MagicMock, patch, PropertyMock

import pytest
from pytest import approx

from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData


@pytest.mark.parametrize("soil_water_content,field_capacity_content,wilting_point_content,saturation_content,expected",
                         [
                             (0.3, 0.6, 0.8, 0.3, 2.5),
                             (0.6, 0.5, 0.8, 0.3, 1.5)
                         ])
def test_water_factor(soil_water_content: float, field_capacity_content: float, wilting_point_content: float,
                      saturation_content: float, expected: float) -> None:
    """Tests that water factor was calculated correctly"""
    with patch('SC_redesign.Crop_and_Soil.soil.layer_data.LayerData.soil_water_content',
               new_callable=PropertyMock, return_value=soil_water_content), \
         patch('SC_redesign.Crop_and_Soil.soil.layer_data.LayerData.field_capacity_content',
               new_callable=PropertyMock, return_value=field_capacity_content), \
         patch('SC_redesign.Crop_and_Soil.soil.layer_data.LayerData.wilting_point_content',
               new_callable=PropertyMock, return_value=wilting_point_content), \
         patch('SC_redesign.Crop_and_Soil.soil.layer_data.LayerData.saturation_content',
               new_callable=PropertyMock, return_value=saturation_content):
        layer = LayerData(top_depth=15, bottom_depth=32, field_size=35)
        actual = layer.water_factor
        assert expected == approx(actual)

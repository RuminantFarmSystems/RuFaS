from unittest.mock import patch, PropertyMock

import pytest
from pytest import approx

from RUFAS.routines.field.soil.layer_data import LayerData


@pytest.mark.parametrize("water_content,field_capacity_content,wilting_point_content,saturation_content,expected",
                         [
                             (0.3, 0.6, 0.8, 0.3, 2.5),
                             (0.6, 0.5, 0.8, 0.3, 1.5)
                         ])
def test_water_factor(water_content: float, field_capacity_content: float, wilting_point_content: float,
                      saturation_content: float, expected: float) -> None:
    """Tests that water factor was calculated correctly"""
    with patch('RUFAS.routines.field.soil.layer_data.LayerData.field_capacity_content',
               new_callable=PropertyMock, return_value=field_capacity_content), \
         patch('RUFAS.routines.field.soil.layer_data.LayerData.wilting_point_content',
               new_callable=PropertyMock, return_value=wilting_point_content), \
         patch('RUFAS.routines.field.soil.layer_data.LayerData.saturation_content',
               new_callable=PropertyMock, return_value=saturation_content):
        layer = LayerData(top_depth=15, bottom_depth=32, field_size=35)
        layer.water_content = water_content
        actual = layer.water_factor
        assert expected == approx(actual)

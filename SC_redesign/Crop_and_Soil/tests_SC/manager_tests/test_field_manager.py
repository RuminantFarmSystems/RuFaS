from SC_redesign.Crop_and_Soil.manager.field_manager import FieldManager
from SC_redesign.Crop_and_Soil.field.field_data import FieldData
from SC_redesign.Crop_and_Soil.field.field import Field
from RUFAS.classes import Time
import pytest
from typing import List, Any
from RUFAS.output_manager import OutputManager
from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather
from unittest.mock import MagicMock


@pytest.mark.parametrize("fields", [
    [Field(field_data=FieldData(name="field1")), Field(field_data=FieldData(name="field2")),
     Field(field_data=FieldData(name="field3"))],
    []
])
def test_daily_update_routine(fields: Field):
    mocked_time = MagicMock(Time)
    mocked_weather = MagicMock(CurrentWeather)
    setattr(mocked_time, "calendar_year", 1998)
    setattr(mocked_time, "day", 5)
    Field.manage_field = MagicMock()
    fm = FieldManager(fields=fields)
    fm.daily_update_routine(current_weather=mocked_weather, time=mocked_time)
    assert Field.manage_field.call_count == len(fields)

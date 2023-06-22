from SC_redesign.Crop_and_Soil.manager.field_manager import FieldManager
from SC_redesign.Crop_and_Soil.field.field_data import FieldData
from SC_redesign.Crop_and_Soil.field.field import Field
from RUFAS.classes import Time, Weather
import pytest
from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather
from unittest.mock import MagicMock
from typing import List


@pytest.mark.parametrize("fields", [
    [Field(field_data=FieldData(name="field1")), Field(field_data=FieldData(name="field2")),
     Field(field_data=FieldData(name="field3"))],
    []
])
def test_daily_update_routine(fields: List[Field]) -> None:
    mocked_time = MagicMock(Time)
    mocked_weather = MagicMock(Weather)
    setattr(mocked_time, "calendar_year", 1998)
    setattr(mocked_time, "day", 5)
    setattr(mocked_weather, "radiation", 3)
    setattr(mocked_weather, "T_min", 3)
    setattr(mocked_weather, "T_avg", 3)
    setattr(mocked_weather, "T_max", 3)
    setattr(mocked_weather, "T_avg_annual", 3)
    setattr(mocked_weather, "rainfall", 3)
    fm = FieldManager()
    fm.fields = fields
    for field in fields:
        field.manage_field = MagicMock()
    fm.om.send_daily_variables = MagicMock()
    fm.daily_update_routine(weather=mocked_weather, time=mocked_time)
    for field in fields:
        assert field.manage_field.call_count == 1
    assert fm.om.send_daily_variables.call_count == 1


@pytest.mark.parametrize("fields", [
    [Field(field_data=FieldData(name="field1")), Field(field_data=FieldData(name="field2")),
     Field(field_data=FieldData(name="field3"))],
    []
])
def test_annual_update_routine(fields: Field):
    mocked_time = MagicMock(Time)
    mocked_weather = MagicMock(CurrentWeather)
    setattr(mocked_time, "calendar_year", 1998)
    setattr(mocked_time, "day", 5)
    for field in fields:
        field.perform_annual_reset = MagicMock()
    fm = FieldManager()
    fm.fields = fields
    fm.om.send_annual_variables = MagicMock()
    fm.annual_update_routine()
    for field in fields:
        assert field.perform_annual_reset.call_count == 1
    assert fm.om.send_annual_variables.call_count == 1


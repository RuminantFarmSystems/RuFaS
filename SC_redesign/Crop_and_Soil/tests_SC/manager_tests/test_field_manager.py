from SC_redesign.Crop_and_Soil.manager.field_manager import FieldManager
from SC_redesign.Crop_and_Soil.field.field_data import FieldData
from SC_redesign.Crop_and_Soil.field.field import Field
from RUFAS.classes import Time
import pytest
from typing import List, Dict
from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather
from unittest.mock import MagicMock


@pytest.mark.parametrize("fields", [
    [Field(field_data=FieldData(name="field1")), Field(field_data=FieldData(name="field2")),
     Field(field_data=FieldData(name="field3"))],
    []
])
def test_daily_update_routine(fields: List[Field]) -> None:
    mocked_time = MagicMock(Time)
    mocked_weather = MagicMock(CurrentWeather)
    setattr(mocked_time, "calendar_year", 1998)
    setattr(mocked_time, "day", 5)
    fm = FieldManager([])
    fm.fields = fields
    for field in fields:
        field.manage_field = MagicMock()
    fm.om.send_daily_variables = MagicMock()
    fm.daily_update_routine(current_weather=mocked_weather, time=mocked_time)
    for field in fields:
        assert field.manage_field.call_count == 1
    assert fm.om.send_daily_variables.call_count == 1


@pytest.mark.parametrize("fields", [
    [Field(field_data=FieldData(name="field1")), Field(field_data=FieldData(name="field2")),
     Field(field_data=FieldData(name="field3"))],
    []
])
def test_annual_update_routine(fields: List[Field]):
    mocked_time = MagicMock(Time)
    mocked_weather = MagicMock(CurrentWeather)
    setattr(mocked_time, "calendar_year", 1998)
    setattr(mocked_time, "day", 5)
    for field in fields:
        field.perform_annual_reset = MagicMock()
    fm = FieldManager([])
    fm.fields = fields
    fm.om.send_annual_variables = MagicMock()
    fm.annual_update_routine()
    for field in fields:
        assert field.perform_annual_reset.call_count == 1
    assert fm.om.send_annual_variables.call_count == 1


@pytest.mark.parametrize("field_name,config", [
    ("test_1", {
        "fertilizer": {
            "mixes": {
                "0_0_60": {
                    "N": 0.0,
                    "P": 0.0,
                    "K": 0.6
                },
                "6_10_20": {
                    "N": 0.0672511,
                    "P": 0.112085,
                    "K": 0.22417
                },
                "5_4_27": {
                    "N": 0.0560426,
                    "P": 0.0493175,
                    "K": 0.2790919
                },
                "5_6_40": {
                    "N": 0.0560426,
                    "P": 0.06904443,
                    "K": 0.39
                },
                "82_0_0": {
                    "N": 0.82,
                    "P": 0.0,
                    "K": 0.0
                }
            },
            "rotation_years": [],
            "repeat": 0,
            "mix": ["6_10_20", "6_10_20", "5_4_27", "5_6_40", "5_6_40", "5_6_40", "5_6_40"],
            "year": [1993, 1996, 2001, 2005, 2009, 2013, 2017],
            "day": [103, 103, 103, 103, 103, 103, 103],
            "N_mass": [6.72511, 6.72511, 5.60426, 5.60426, 5.6, 5.60426, 5.60426],
            "P_mass": [11.2085, 11.2085, 4.93175, 6.904443, 6.72511, 6.904443, 6.904443],
            "K_mass": [22.417, 22.417, 27.90919, 39.072871, 39.072871, 39.072871, 39.072871],
            "depth": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "surface_percent": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        },
        "manure": {
            "rotation_years": [],
            "repeat": 0,
            "year": [1990, 1992, 1993, 1996, 1997, 2000, 2001, 2004, 2005, 2008, 2009, 2012, 2013, 2016, 2017],
            "day": [113, 335, 311, 311, 310, 315, 316, 316, 314, 310, 327, 304, 324, 280, 318],
            "N_mass": [266, 266, 201, 207, 230, 279, 214, 244, 320, 169, 355, 163, 245, 66, 275],
            "P_mass": [70, 70, 45, 36, 37, 50, 31, 48, 53, 20, 60, 29, 43, 30, 54],
            "K_mass": [188, 188, 211, 164, 183, 198, 112, 156, 227, 167, 270, 128, 192, 86, 178],
            "cover_percent": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
            "depth": [150.0, 150.0, 150.0, 150.0, 150.0, 150.0, 150.0, 150.0, 150.0, 150.0, 150.0, 150.0, 150.0, 150.0,
                      150.0],
            "surface_percent": [0.80, 0.80, 0.80, 0.80, 0.80, 0.80, 0.80, 0.80, 0.80, 0.80, 0.80, 0.80, 0.80, 0.80,
                                0.80]
        },
        "tillage": {
            "rotation_years": [],
            "repeat": 0,
            "year": [1989, 1989, 1992, 1993, 1993, 1993, 1994, 1997, 1997, 1997, 1998, 2000, 2001, 2001, 2001, 2001,
                     2002, 2004, 2005, 2005, 2006, 2008, 2009, 2009, 2010, 2010, 2012, 2013, 2013, 2014, 2016, 2017,
                     2018, 2018],
            "day": [305, 306, 335, 120, 121, 313, 108, 100, 114, 324, 98, 316, 114, 136, 142, 317, 175, 321, 118, 318,
                    95, 315, 121, 327, 83, 88, 321, 126, 339, 112, 280, 125, 117, 120],
            "percent_incorporated": [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3,
                                     0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3,
                                     0.3, 0.3],
            "percent_mixed": [0.3, 0.55, 0.3, 0.85, 0.55, 0.3, 0.55, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.1, 0.25, 0.3, 0.3,
                              0.3, 0.3, 0.3, 0.55, 0.55, 0.3, 0.3, 0.55, 0.3, 0.55, 0.3, 0.55, 0.3, 0.3, 0.3, 0.3, 0.3],
            "depth": [150, 75, 150, 100, 75, 150, 75, 150, 100, 150, 100, 150, 100, 5, 25, 150, 100, 150, 100, 150, 75,
                      150, 100, 100, 150, 100, 150, 100, 150, 100, 100, 100, 100, 100]
        }
    })
])
def test_setup_management(field_name: str, config: Dict) -> None:
    """Tests that farm management practices are correctly set up for simulations."""
    mixes, fert_sched, manure_sched, till_sched = FieldManager._setup_management(field_name, config)
    assert mixes == config.get("fertilizer").get("mixes")
    assert fert_sched.years == config.get("fertilizer").get("year")
    assert manure_sched.days == config.get("manure").get("day")
    assert till_sched.tillage_depths == config.get("tillage").get("depth")

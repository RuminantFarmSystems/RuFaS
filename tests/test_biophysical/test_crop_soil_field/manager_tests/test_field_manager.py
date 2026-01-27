from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List
from unittest.mock import MagicMock, call, patch

import mock
import pytest
from pytest_mock.plugin import MockerFixture

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
from RUFAS.data_structures.events import FertilizerEvent, ManureEvent, TillageEvent, PlantingEvent, HarvestEvent
from RUFAS.data_structures.manure_supplement_methods import ManureSupplementMethod
from RUFAS.data_structures.manure_to_crop_soil_connection import (
    ManureEventNutrientRequest,
    ManureEventNutrientRequestResults,
)
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.field.crop.crop_data_factory import CropDataFactory
from RUFAS.biophysical.field.field.field import Field
from RUFAS.biophysical.field.field.field_data import FieldData
from RUFAS.biophysical.field.manager.crop_schedule import CropSchedule
from RUFAS.biophysical.field.manager.fertilizer_schedule import FertilizerSchedule
from RUFAS.biophysical.field.manager.field_manager import FieldManager
from RUFAS.biophysical.field.manager.manure_schedule import ManureSchedule
from RUFAS.biophysical.field.manager.tillage_schedule import TillageSchedule
from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.soil import Soil
from RUFAS.biophysical.field.soil.soil_data import SoilData
from RUFAS.data_structures.manure_types import ManureType
from RUFAS.rufas_time import RufasTime
from RUFAS.weather import Weather

im = InputManager()
om = OutputManager()


@pytest.fixture
def mock_input_manager(mocker: MockerFixture) -> InputManager:
    """Returns an uninitialized InputManager object"""
    return InputManager()


@pytest.fixture
def input_manager_original_method_states(
    mock_input_manager: InputManager,
) -> Dict[str, Callable]:
    """Fixture to store original methods of InputManager"""
    return {
        "get_data": mock_input_manager.get_data,
    }


@pytest.mark.parametrize("field_blob_names", [[], ["field_1", "field_2", "field_3"]])
def test_field_manager_init(mocker: MockerFixture, field_blob_names: list[str]) -> None:
    """Tests that FieldManager init method runs correctly."""
    available_crop_configs = ["alfalfa", "corn", "oats"]
    expected_field_setup_calls = [call(field_name, available_crop_configs) for field_name in field_blob_names]
    data_keys_by_properties = mocker.patch(
        "RUFAS.input_manager.InputManager.get_data_keys_by_properties", return_value=field_blob_names
    )
    field_setup = mocker.patch(
        "RUFAS.biophysical.field.manager.field_manager.FieldManager._setup_field", return_value=MagicMock(Field)
    )
    crop_config_setup = mocker.patch.object(CropDataFactory, "setup_crop_configurations", return_value=None)
    available_crop_configs = mocker.patch.object(
        CropDataFactory, "get_available_crop_configurations", return_value=available_crop_configs
    )
    add_warning = mocker.patch.object(om, "add_warning")

    field_manager = FieldManager()

    crop_config_setup.assert_called_once()
    available_crop_configs.assert_called_once()
    assert len(field_manager.fields) == len(field_blob_names)
    assert len(field_manager.output_gatherer.fields) == len(field_blob_names)
    data_keys_by_properties.assert_called_once()
    if len(field_blob_names) > 0:
        field_setup.assert_has_calls(expected_field_setup_calls)
        add_warning.assert_not_called()
    else:
        field_setup.assert_not_called()
        add_warning.assert_called_once()


@pytest.fixture
def mock_weather(mocker: MockerFixture) -> Weather:
    """Fixture for Weather object."""
    mocker.patch("RUFAS.weather.Weather.__init__", return_value=None)

    mock_time = MagicMock(RufasTime)

    mock_weather = Weather({}, mock_time)
    return mock_weather


@pytest.mark.parametrize(
    "fields, expected_harvests_count, manure_applications",
    [
        (
            [
                Field(
                    field_data=FieldData(name="field1"),
                ),
                Field(
                    field_data=FieldData(name="field2"),
                ),
                Field(
                    field_data=FieldData(name="field3"),
                ),
            ],
            6,
            [
                MagicMock(spec=ManureEventNutrientRequestResults),
                MagicMock(spec=ManureEventNutrientRequestResults),
                MagicMock(spec=ManureEventNutrientRequestResults),
            ],
        ),
        ([], 0, {}),
    ],
)
def test_daily_update_routine(
    manure_applications: dict[str, List[ManureEventNutrientRequestResults]],
    mock_weather: Weather,
    mocker: MockerFixture,
    fields: list[Field],
    expected_harvests_count: int,
) -> None:
    """Tests that the daily routines and its methods are called and updated correctly."""
    mocked_time = MagicMock(RufasTime)
    setattr(mocked_time, "year", 1)
    setattr(mocked_time, "calendar_year", 1998)
    setattr(mocked_time, "year", 1998)
    setattr(mocked_time, "day", 5)
    mocked_time.current_date = datetime(1998, 1, 1) + timedelta(days=5 - 1)

    get_conditions = mocker.patch.object(
        mock_weather, "get_current_day_conditions", return_value=MagicMock(CurrentDayConditions)
    )
    mocker.patch.object(CropDataFactory, "setup_crop_configurations", return_value=None)
    mocker.patch.object(CropDataFactory, "get_available_crop_configurations", return_value=["alfalfa", "corn", "oats"])
    with patch("RUFAS.input_manager.InputManager.get_data_keys_by_properties", return_value=[]):
        fm = FieldManager()
        mock_add_var = mocker.patch.object(fm.om, "add_variable")

        fm.fields = fields
        for field in fields:
            mocker.patch.object(
                field,
                "manage_field",
                return_value=[
                    HarvestedCrop(
                        config_name="test_crop",
                        field_name="test_field",
                        harvest_time=mocked_time,
                        storage_time=mocked_time,
                        dry_matter_mass=10.0,
                        dry_matter_percentage=0.85,
                        dry_matter_digestibility=0.65,
                        crude_protein_percent=0.12,
                        non_protein_nitrogen=0.02,
                        starch=0.30,
                        adf=0.15,
                        ndf=0.35,
                        lignin=0.05,
                        sugar=0.10,
                        ash=0.08,
                        recorded_days=set(),
                    ),
                    HarvestedCrop(
                        config_name="test_crop_2",
                        field_name="test_field",
                        harvest_time=mocked_time,
                        storage_time=mocked_time,
                        dry_matter_mass=10.0,
                        dry_matter_percentage=0.85,
                        dry_matter_digestibility=0.65,
                        crude_protein_percent=0.12,
                        non_protein_nitrogen=0.02,
                        starch=0.30,
                        adf=0.15,
                        ndf=0.35,
                        lignin=0.05,
                        sugar=0.10,
                        ash=0.08,
                        recorded_days=set(),
                    ),
                ],
            )
        fm.output_gatherer.send_daily_variables = MagicMock()
        actual = fm.daily_update_routine(
            weather=mock_weather, time=mocked_time, manure_applications=manure_applications
        )

        for field in fields:
            assert field.manage_field.call_count == 1
        assert get_conditions.call_count == len(fields)
        assert fm.output_gatherer.send_daily_variables.call_count == 1
        assert mock_add_var.call_count == len(fields)
        assert len(actual) == expected_harvests_count


@pytest.mark.parametrize(
    "fields",
    [
        [
            Field(
                field_data=FieldData(name="field1"),
            ),
            Field(
                field_data=FieldData(name="field2"),
            ),
            Field(
                field_data=FieldData(name="field3"),
            ),
        ],
        [],
    ],
)
def test_annual_update_routine(mocker: MockerFixture, fields: List[Field]) -> None:
    """Tests that the annual routines and it's methods were called and updated correctly"""
    mocker.patch.object(CropDataFactory, "setup_crop_configurations", return_value=None)
    mocker.patch.object(CropDataFactory, "get_available_crop_configurations", return_value=["alfalfa", "corn", "oats"])
    for field in fields:
        field.perform_annual_reset = MagicMock()
    with patch("RUFAS.input_manager.InputManager.get_data_keys_by_properties", return_value=[]):
        fm = FieldManager()
        fm.fields = fields
        fm.output_gatherer.send_annual_variables = MagicMock()

        fm.annual_update_routine()

        for field in fields:
            assert field.perform_annual_reset.call_count == 1
        assert fm.output_gatherer.send_annual_variables.call_count == 1


@pytest.mark.parametrize(
    "fertilizer_schedule_data,expected_available_mixes,expected_schedule",
    [
        (
            {
                "available_fertilizer_mixes": [
                    {"name": "0_0_60", "N": 0.0, "P": 0.0, "K": 0.6, "ammonium_fraction": 0.0},
                    {"name": "6_10_20", "N": 0.0672511, "P": 0.112085, "K": 0.22417, "ammonium_fraction": 0.0},
                    {"name": "5_4_27", "N": 0.0560426, "P": 0.0493175, "K": 0.2790919, "ammonium_fraction": 0.0},
                    {"name": "5_6_40", "N": 0.0560426, "P": 0.06904443, "K": 0.39, "ammonium_fraction": 0.5},
                    {"name": "82_0_0", "N": 0.82, "P": 0.0, "K": 0.0, "ammonium_fraction": 1.0},
                ],
                "mix_names": [
                    "6_10_20",
                    "6_10_20",
                    "5_4_27",
                    "5_6_40",
                    "5_6_40",
                    "5_6_40",
                    "5_6_40",
                ],
                "years": [1993, 1996, 2001, 2005, 2009, 2013, 2017],
                "days": [103, 103, 103, 103, 103, 103, 103],
                "nitrogen_masses": [
                    6.72511,
                    6.72511,
                    5.60426,
                    5.60426,
                    5.6,
                    5.60426,
                    5.60426,
                ],
                "phosphorus_masses": [
                    11.2085,
                    11.2085,
                    4.93175,
                    6.904443,
                    6.72511,
                    6.904443,
                    6.904443,
                ],
                "potassium_masses": [
                    22.417,
                    22.417,
                    27.90919,
                    39.072871,
                    39.072871,
                    39.072871,
                    39.072871,
                ],
                "application_depths": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                "surface_remainder_fractions": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                "pattern_repeat": 0,
                "pattern_skip": 0,
            },
            {
                "0_0_60": {"N": 0.0, "P": 0.0, "K": 0.6, "ammonium_fraction": 0.0},
                "6_10_20": {"N": 0.0672511, "P": 0.112085, "K": 0.22417, "ammonium_fraction": 0.0},
                "5_4_27": {"N": 0.0560426, "P": 0.0493175, "K": 0.2790919, "ammonium_fraction": 0.0},
                "5_6_40": {"N": 0.0560426, "P": 0.06904443, "K": 0.39, "ammonium_fraction": 0.5},
                "82_0_0": {"N": 0.82, "P": 0.0, "K": 0.0, "ammonium_fraction": 1.0},
            },
            FertilizerSchedule(
                name="fertilizer_schedule",
                mix_names=[
                    "6_10_20",
                    "6_10_20",
                    "5_4_27",
                    "5_6_40",
                    "5_6_40",
                    "5_6_40",
                    "5_6_40",
                ],
                years=[1993, 1996, 2001, 2005, 2009, 2013, 2017],
                days=[103, 103, 103, 103, 103, 103, 103],
                nitrogen_masses=[
                    6.72511,
                    6.72511,
                    5.60426,
                    5.60426,
                    5.6,
                    5.60426,
                    5.60426,
                ],
                phosphorus_masses=[
                    11.2085,
                    11.2085,
                    4.93175,
                    6.904443,
                    6.72511,
                    6.904443,
                    6.904443,
                ],
                potassium_masses=[
                    22.417,
                    22.417,
                    27.90919,
                    39.072871,
                    39.072871,
                    39.072871,
                    39.072871,
                ],
                application_depths=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                surface_remainder_fractions=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                pattern_repeat=0,
                pattern_skip=0,
            ),
        ),
        (
            {
                "available_fertilizer_mixes": [
                    {"name": "barnyard_fert", "N": 0.4, "P": 0.2, "K": 0.1, "ammonium_fraction": 0.3}
                ],
                "mix_names": ["barnyard_fert"],
                "years": [2010],
                "days": [200],
                "nitrogen_masses": [1000],
                "phosphorus_masses": [5],
                "potassium_masses": [400],
                "application_depths": [0.0],
                "surface_remainder_fractions": [1.0],
                "pattern_repeat": 0,
                "pattern_skip": 0,
            },
            {"barnyard_fert": {"N": 0.4, "P": 0.2, "K": 0.1, "ammonium_fraction": 0.3}},
            FertilizerSchedule(
                name="fertilizer_schedule",
                mix_names=["barnyard_fert"],
                years=[2010],
                days=[200],
                nitrogen_masses=[1000],
                phosphorus_masses=[5],
                potassium_masses=[400.0],
                application_depths=[0.0],
                surface_remainder_fractions=[1.0],
                pattern_repeat=0,
                pattern_skip=0,
            ),
        ),
    ],
)
def test_setup_fertilizer_schedule(
    fertilizer_schedule_data: dict[str, list[dict[str, Any]]],
    expected_available_mixes: dict[str, dict[str, float]],
    expected_schedule: FertilizerSchedule,
    mock_input_manager: InputManager,
    input_manager_original_method_states: dict[str, Callable],
) -> None:
    """Tests that fertilizer schedules and available fertilizer mixes are correctly setup."""
    mock_input_manager.get_data = mock.MagicMock(return_value=fertilizer_schedule_data)
    expected_events = expected_schedule.generate_fertilizer_events()

    actual_available_mixes, actual_events = FieldManager._setup_fertilizer_events("test_fert_schedule")
    assert actual_available_mixes == expected_available_mixes
    assert actual_events == expected_events
    mock_input_manager.get_data.assert_called_once_with("test_fert_schedule")

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]


def test_setup_fertilizer_schedule_no_data(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    """Test when no fertilizer schedule input."""
    mocker.patch.object(mock_input_manager, "get_data", return_value=None)

    with pytest.raises(ValueError):
        FieldManager._setup_fertilizer_events("test_fert_schedule")


@pytest.mark.parametrize(
    "manure_schedule_data,expected_manure_schedule",
    [
        (
            {
                "supplement_manure_nutrient_deficiencies": [
                    "none",
                    "none",
                    "none",
                    "none",
                    "none",
                    "none",
                    "none",
                    "none",
                    "none",
                    "none",
                    "none",
                    "none",
                    "none",
                    "none",
                    "none",
                ],
                "years": [
                    1990,
                    1992,
                    1993,
                    1996,
                    1997,
                    2000,
                    2001,
                    2004,
                    2005,
                    2008,
                    2009,
                    2012,
                    2013,
                    2016,
                    2017,
                ],
                "days": [
                    113,
                    335,
                    311,
                    311,
                    310,
                    315,
                    316,
                    316,
                    314,
                    310,
                    327,
                    304,
                    324,
                    280,
                    318,
                ],
                "nitrogen_masses": [
                    266,
                    266,
                    201,
                    207,
                    230,
                    279,
                    214,
                    244,
                    320,
                    169,
                    355,
                    163,
                    245,
                    66,
                    275,
                ],
                "phosphorus_masses": [
                    70,
                    70,
                    45,
                    36,
                    37,
                    50,
                    31,
                    48,
                    53,
                    20,
                    60,
                    29,
                    43,
                    30,
                    54,
                ],
                "potassium_masses": [
                    188,
                    188,
                    211,
                    164,
                    183,
                    198,
                    112,
                    156,
                    227,
                    167,
                    270,
                    128,
                    192,
                    86,
                    178,
                ],
                "manure_types": [
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                ],
                "coverage_fractions": [
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                ],
                "application_depths": [
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                ],
                "surface_remainder_fractions": [
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                ],
                "pattern_repeat": 0,
                "pattern_skip": 0,
            },
            ManureSchedule(
                name="manure_schedule",
                years=[
                    1990,
                    1992,
                    1993,
                    1996,
                    1997,
                    2000,
                    2001,
                    2004,
                    2005,
                    2008,
                    2009,
                    2012,
                    2013,
                    2016,
                    2017,
                ],
                days=[
                    113,
                    335,
                    311,
                    311,
                    310,
                    315,
                    316,
                    316,
                    314,
                    310,
                    327,
                    304,
                    324,
                    280,
                    318,
                ],
                nitrogen_masses=[
                    266,
                    266,
                    201,
                    207,
                    230,
                    279,
                    214,
                    244,
                    320,
                    169,
                    355,
                    163,
                    245,
                    66,
                    275,
                ],
                phosphorus_masses=[
                    70,
                    70,
                    45,
                    36,
                    37,
                    50,
                    31,
                    48,
                    53,
                    20,
                    60,
                    29,
                    43,
                    30,
                    54,
                ],
                manure_types=[
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                ],
                manure_supplement_methods=[
                    ManureSupplementMethod.NONE,
                    ManureSupplementMethod.NONE,
                    ManureSupplementMethod.NONE,
                    ManureSupplementMethod.NONE,
                    ManureSupplementMethod.NONE,
                    ManureSupplementMethod.NONE,
                    ManureSupplementMethod.NONE,
                    ManureSupplementMethod.NONE,
                    ManureSupplementMethod.NONE,
                    ManureSupplementMethod.NONE,
                    ManureSupplementMethod.NONE,
                    ManureSupplementMethod.NONE,
                    ManureSupplementMethod.NONE,
                    ManureSupplementMethod.NONE,
                    ManureSupplementMethod.NONE,
                ],
                field_coverages=[
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                    0.1,
                ],
                application_depths=[
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                    150.0,
                ],
                surface_remainder_fractions=[
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                    0.80,
                ],
                pattern_repeat=0,
                pattern_skip=0,
            ),
        ),
        (
            {
                "supplement_manure_nutrient_deficiencies": [
                    "none",
                    "none",
                    "none",
                    "none",
                    "none",
                    "none",
                    "none",
                    "none",
                    "none",
                ],
                "years": [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016],
                "days": [200, 200, 200, 200, 200, 200, 200, 200, 200],
                "nitrogen_masses": [
                    1000,
                    1000,
                    1000,
                    1000,
                    1000,
                    1000,
                    1000,
                    1000,
                    1000,
                ],
                "phosphorus_masses": [500, 500, 500, 500, 500, 500, 500, 500, 500],
                "manure_types": [
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                    ManureType.LIQUID,
                ],
                "potassium_masses": [0.0],
                "coverage_fractions": [
                    0.95,
                    0.95,
                    0.95,
                    0.95,
                    0.95,
                    0.95,
                    0.95,
                    0.95,
                    0.95,
                ],
                "application_depths": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                "surface_remainder_fractions": [
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                    1.0,
                ],
                "pattern_repeat": 0,
                "pattern_skip": 0,
            },
            ManureSchedule(
                name="manure_schedule",
                years=[2008],
                days=[200],
                nitrogen_masses=[1000],
                phosphorus_masses=[500],
                manure_types=[ManureType.LIQUID],
                manure_supplement_methods=[ManureSupplementMethod.NONE],
                field_coverages=[0.95],
                application_depths=[0.0],
                surface_remainder_fractions=[1.0],
                pattern_repeat=8,
                pattern_skip=0,
            ),
        ),
    ],
)
def test_setup_manure_schedule(
    manure_schedule_data: dict[str, list[int] | list[ManureType] | list[float] | int],
    expected_manure_schedule: ManureSchedule,
    mock_input_manager: InputManager,
    input_manager_original_method_states: dict[str, Callable],
) -> None:
    """Tests that ManureSchedules are correctly initialized with data from the InputManager."""
    mock_input_manager.get_data = mock.MagicMock(return_value=manure_schedule_data)
    expected_manure_events = expected_manure_schedule.generate_manure_events()
    actual_manure_events = FieldManager._setup_manure_events("test_manure_schedule")
    assert actual_manure_events == expected_manure_events
    mock_input_manager.get_data.assert_called_once_with("test_manure_schedule")

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]


def test_setup_manure_schedule_no_data(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    """Test when no manure schedule input."""
    mocker.patch.object(mock_input_manager, "get_data", return_value=None)

    with pytest.raises(ValueError):
        FieldManager._setup_manure_events("test_manure_schedule")


@pytest.mark.parametrize(
    "tillage_schedule_data,expected_tillage_schedule",
    [
        (
            {
                "pattern_repeat": 0,
                "pattern_skip": 0,
                "years": [
                    1989,
                    1989,
                    1992,
                    1993,
                    1993,
                    1993,
                    1994,
                    1997,
                    1997,
                    1997,
                    1998,
                    2000,
                    2001,
                    2001,
                    2001,
                    2001,
                    2002,
                    2004,
                    2005,
                    2005,
                    2006,
                    2008,
                    2009,
                    2009,
                    2010,
                    2010,
                    2012,
                    2013,
                    2013,
                    2014,
                    2016,
                    2017,
                    2018,
                    2018,
                ],
                "days": [
                    305,
                    306,
                    335,
                    120,
                    121,
                    313,
                    108,
                    100,
                    114,
                    324,
                    98,
                    316,
                    114,
                    136,
                    142,
                    317,
                    175,
                    321,
                    118,
                    318,
                    95,
                    315,
                    121,
                    327,
                    83,
                    88,
                    321,
                    126,
                    339,
                    112,
                    280,
                    125,
                    117,
                    120,
                ],
                "incorporation_fractions": [
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                ],
                "mixing_fractions": [
                    0.3,
                    0.55,
                    0.3,
                    0.85,
                    0.55,
                    0.3,
                    0.55,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.1,
                    0.25,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.55,
                    0.55,
                    0.3,
                    0.3,
                    0.55,
                    0.3,
                    0.55,
                    0.3,
                    0.55,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                ],
                "tillage_depths": [
                    150,
                    75,
                    150,
                    100,
                    75,
                    150,
                    75,
                    150,
                    100,
                    150,
                    100,
                    150,
                    100,
                    5,
                    25,
                    150,
                    100,
                    150,
                    100,
                    150,
                    75,
                    150,
                    100,
                    100,
                    150,
                    100,
                    150,
                    100,
                    150,
                    100,
                    100,
                    100,
                    100,
                    100,
                ],
                "implements": ["subsoiler"],
            },
            TillageSchedule(
                name="tillage_schedule",
                years=[
                    1989,
                    1989,
                    1992,
                    1993,
                    1993,
                    1993,
                    1994,
                    1997,
                    1997,
                    1997,
                    1998,
                    2000,
                    2001,
                    2001,
                    2001,
                    2001,
                    2002,
                    2004,
                    2005,
                    2005,
                    2006,
                    2008,
                    2009,
                    2009,
                    2010,
                    2010,
                    2012,
                    2013,
                    2013,
                    2014,
                    2016,
                    2017,
                    2018,
                    2018,
                ],
                days=[
                    305,
                    306,
                    335,
                    120,
                    121,
                    313,
                    108,
                    100,
                    114,
                    324,
                    98,
                    316,
                    114,
                    136,
                    142,
                    317,
                    175,
                    321,
                    118,
                    318,
                    95,
                    315,
                    121,
                    327,
                    83,
                    88,
                    321,
                    126,
                    339,
                    112,
                    280,
                    125,
                    117,
                    120,
                ],
                incorporation_fractions=[
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                ],
                mixing_fractions=[
                    0.3,
                    0.55,
                    0.3,
                    0.85,
                    0.55,
                    0.3,
                    0.55,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.1,
                    0.25,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.55,
                    0.55,
                    0.3,
                    0.3,
                    0.55,
                    0.3,
                    0.55,
                    0.3,
                    0.55,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                ],
                tillage_depths=[
                    150,
                    75,
                    150,
                    100,
                    75,
                    150,
                    75,
                    150,
                    100,
                    150,
                    100,
                    150,
                    100,
                    5,
                    25,
                    150,
                    100,
                    150,
                    100,
                    150,
                    75,
                    150,
                    100,
                    100,
                    150,
                    100,
                    150,
                    100,
                    150,
                    100,
                    100,
                    100,
                    100,
                    100,
                ],
                implements=["subsoiler"],
            ),
        ),
        (
            {
                "years": [2014],
                "days": [322],
                "incorporation_fractions": [0.95],
                "mixing_fractions": [0.95],
                "tillage_depths": [150],
                "implements": ["cultivator"],
                "pattern_repeat": 0,
                "pattern_skip": 0,
            },
            TillageSchedule(
                name="tillage_schedule",
                years=[2014],
                days=[322],
                incorporation_fractions=[0.95],
                mixing_fractions=[0.95],
                tillage_depths=[150],
                implements=["cultivator"],
                pattern_skip=0,
                pattern_repeat=0,
            ),
        ),
    ],
)
def test_setup_tillage_schedule(
    tillage_schedule_data: dict[str, int | list[int] | list[float] | list[str]],
    expected_tillage_schedule: TillageSchedule,
    mock_input_manager: InputManager,
    input_manager_original_method_states: dict[str, Callable],
) -> None:
    """Tests that TillageSchedules are correctly initialized with data from the InputManager."""
    mock_input_manager.get_data = mock.MagicMock(return_value=tillage_schedule_data)
    expected_tillage_events = expected_tillage_schedule.generate_tillage_events()

    actual_tillage_events = FieldManager._setup_tillage_events("test_tillage_schedule")
    assert actual_tillage_events == expected_tillage_events
    mock_input_manager.get_data.assert_called_once_with("test_tillage_schedule")

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]


def test_setup_tillage_schedule_no_data(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    """Test when no tillage input data available."""
    mocker.patch.object(mock_input_manager, "get_data", return_value=None)

    with pytest.raises(ValueError):
        FieldManager._setup_tillage_events("test_tillage_schedule")


@pytest.mark.parametrize(
    "crop_schedule_config,expected",
    [
        (
            [
                {
                    "crop_species": "corn",
                    "planting_years": [2009],
                    "pattern_repeat": 1,
                    "planting_skip": 0,
                    "harvesting_skip": 0,
                    "planting_days": [121],
                    "harvest_years": [2009],
                    "harvest_days": [319],
                    "harvest_operations": ["harvest_kill"],
                    "harvest_type": "scheduled",
                }
            ],
            [
                CropSchedule(
                    name="crop_schedule_0",
                    crop_reference="corn",
                    planting_years=[2009],
                    planting_days=[121],
                    harvest_years=[2009],
                    harvest_days=[319],
                    harvest_operations=["harvest_kill"],
                    use_heat_scheduling=False,
                    pattern_repeat=1,
                )
            ],
        ),
        (
            [
                {
                    "crop_species": "corn",
                    "planting_years": [2010],
                    "pattern_repeat": 0,
                    "planting_skip": 1,
                    "harvesting_skip": 1,
                    "planting_days": [121],
                    "harvest_years": [2010],
                    "harvest_days": [319],
                    "harvest_operations": ["harvest_kill"],
                    "harvest_type": "optimal",
                    "planting_order": "1st",
                    "extracted": True,
                },
                {
                    "crop_species": "corn",
                    "planting_years": [2011],
                    "pattern_repeat": 0,
                    "planting_skip": 3,
                    "harvesting_skip": 1,
                    "planting_days": [121],
                    "harvest_years": [2011],
                    "harvest_days": [319],
                    "harvest_operations": ["harvest_kill"],
                    "harvest_type": "scheduled",
                    "planting_order": "1st",
                    "extracted": True,
                },
                {
                    "crop_species": "corn",
                    "planting_years": [2012],
                    "pattern_repeat": 0,
                    "planting_skip": 1,
                    "harvesting_skip": 2,
                    "planting_days": [121],
                    "harvest_years": [2012],
                    "harvest_days": [319],
                    "harvest_operations": ["harvest_kill"],
                    "harvest_type": "optimal",
                    "planting_order": "1st",
                    "extracted": True,
                },
                {
                    "crop_species": "corn",
                    "planting_years": [2013],
                    "pattern_repeat": 0,
                    "planting_skip": 1,
                    "harvesting_skip": 1,
                    "planting_days": [121],
                    "harvest_years": [2013],
                    "harvest_days": [319],
                    "harvest_operations": ["harvest_kill"],
                    "harvest_type": "scheduled",
                    "planting_order": "1st",
                    "extracted": True,
                },
            ],
            [
                CropSchedule(
                    name="crop_schedule_0",
                    crop_reference="corn",
                    planting_years=[2010],
                    planting_days=[121],
                    harvest_years=[2010],
                    harvest_days=[319],
                    harvest_operations=["harvest_kill"],
                    use_heat_scheduling=True,
                    pattern_repeat=0,
                ),
                CropSchedule(
                    name="crop_schedule_1",
                    crop_reference="corn",
                    planting_years=[2011],
                    planting_days=[121],
                    harvest_years=[2011],
                    harvest_days=[319],
                    harvest_operations=["harvest_kill"],
                    use_heat_scheduling=False,
                    pattern_repeat=0,
                ),
                CropSchedule(
                    name="crop_schedule_2",
                    crop_reference="corn",
                    planting_years=[2012],
                    planting_days=[121],
                    harvest_years=[2012],
                    harvest_days=[319],
                    harvest_operations=["harvest_kill"],
                    use_heat_scheduling=True,
                    pattern_repeat=0,
                ),
                CropSchedule(
                    name="crop_schedule_3",
                    crop_reference="corn",
                    planting_years=[2013],
                    planting_days=[121],
                    harvest_years=[2013],
                    harvest_days=[319],
                    harvest_operations=["harvest_kill"],
                    use_heat_scheduling=False,
                    pattern_repeat=0,
                ),
            ],
        ),
    ],
)
def test_crop_schedule_setup(
    crop_schedule_config: list[dict[str, Any]],
    expected: List[CropSchedule],
    mock_input_manager: InputManager,
    input_manager_original_method_states: dict[str, Callable],
) -> None:
    """Tests that crop schedules are created correctly from the crop schedule configuration passed to it."""
    mock_input_manager.get_data = mock.MagicMock(return_value=crop_schedule_config)
    crop_configs = ["alfalfa", "corn", "oats"]

    actual = FieldManager._setup_crop_schedules("test_crop_schedule", crop_configs)

    for index in range(len(expected)):
        assert actual[index].generate_planting_events() == expected[index].generate_planting_events()
        assert actual[index].generate_harvest_events() == expected[index].generate_harvest_events()
    mock_input_manager.get_data.assert_called_once_with("test_crop_schedule.crop_schedules")

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]


def test_setup_crop_schedule_schedule_no_data(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    """Test when no crop schedule input data available."""
    mocker.patch.object(mock_input_manager, "get_data", return_value=None)
    crop_configs = ["alfalfa", "corn", "oats"]

    with pytest.raises(ValueError):
        FieldManager._setup_crop_schedules("test_crop_schedule", crop_configs)


def test_crop_schedule_setup_error(mocker: MockerFixture, mock_input_manager: InputManager) -> None:
    """Test that crop schedule setup fails correctly when a config is not available."""
    crop_rotations = [
        {
            "crop_species": "corn",
            "planting_years": [2010],
            "pattern_repeat": 0,
            "planting_skip": 1,
            "harvesting_skip": 1,
            "planting_days": [121],
            "harvest_years": [2010],
            "harvest_days": [319],
            "harvest_operations": ["harvest_kill"],
            "harvest_type": "optimal",
            "extracted": True,
        }
    ]
    mocker.patch.object(mock_input_manager, "get_data", return_value=crop_rotations)

    with pytest.raises(ValueError):
        FieldManager._setup_crop_schedules("crop_schedule_error", ["alfalfa"])


@pytest.mark.parametrize(
    "field_size,top,residue,config,expected",
    [
        (
            1.3,
            0.0,
            0.0,
            {
                "bottom_depth": 279.4,
                "soil_water_concentration": 0.3,
                "wilting_point_water_concentration": 0.23,
                "field_capacity_water_concentration": 0.29,
                "saturation_point_water_concentration": 0.58,
                "saturated_hydraulic_conductivity": 9.17,
                "pH": 9.9,
                "initial_temperature": 15.77575,
                "bulk_density": 1.34,
                "organic_carbon_fraction": 0.012,
                "clay_fraction": 0.2195,
                "silt_fraction": 0.6342,
                "sand_fraction": 0.1463,
                "rock_fraction": 0.0,
                "initial_labile_inorganic_phosphorus_concentration": 2.7,
                "initial_fresh_organic_phosphorus_concentration": 0.0,
                "initial_soil_nitrate_concentration": 1,
                "initial_soil_ammonium_concentration": 1,
                "humus_mineralization_rate_factor": 0.0003,
                "ammonium_volatilization_cation_exchange_factor": 0.15,
                "denitrification_rate_coefficient": 1.4,
                "denitrification_threshold_water_content": 1.1,
                "residue_fresh_organic_mineralization_rate": 0.05,
                "OM_percent": 0.04,
            },
            LayerData(
                field_size=1.3,
                top_depth=0.0,
                bottom_depth=279.4,
                wilting_point_water_concentration=0.23,
                field_capacity_water_concentration=0.29,
                saturation_point_water_concentration=0.58,
                saturated_hydraulic_conductivity=9.17,
                pH=9.9,
                clay_fraction=0.2195,
                temperature=15.77575,
                bulk_density=1.34,
                organic_carbon_fraction=0.012,
                initial_soil_ammonium_concentration=1.0,
                initial_soil_nitrate_concentration=1.0,
                initial_labile_inorganic_phosphorus_concentration=2.7,
                ammonium_volatilization_cation_exchange_factor=0.15,
                soil_water_concentration=0.3,
                sand_fraction=0.1463,
                silt_fraction=0.6342,
                rock_fraction=0.0,
                residue=0.0,
            ),
        ),
        (
            2.2,
            279.4,
            0.0,
            {
                "bottom_depth": 1041.4,
                "soil_water_concentration": 0.3,
                "wilting_point_water_concentration": 0.163,
                "field_capacity_water_concentration": 0.306,
                "saturation_point_water_concentration": 0.5,
                "saturated_hydraulic_conductivity": 9.17,
                "pH": 6.5,
                "initial_temperature": 14.50797297,
                "bulk_density": 1.42,
                "organic_carbon_fraction": 0.012,
                "clay_fraction": 0.2727,
                "silt_fraction": 0.5909,
                "sand_fraction": 0.1364,
                "rock_fraction": 0.0,
                "initial_labile_inorganic_phosphorus_concentration": 2.7,
                "initial_fresh_organic_phosphorus_concentration": 0.0,
                "initial_soil_nitrate_concentration": 1,
                "initial_soil_ammonium_concentration": 1,
                "humus_mineralization_rate_factor": 0.0003,
                "ammonium_volatilization_cation_exchange_factor": 0.15,
                "denitrification_rate_coefficient": 1.4,
                "denitrification_threshold_water_content": 1.1,
                "residue_fresh_organic_mineralization_rate": 0.05,
                "OM_percent": 0.006,
            },
            LayerData(
                field_size=2.2,
                top_depth=279.4,
                bottom_depth=1041.4,
                wilting_point_water_concentration=0.163,
                field_capacity_water_concentration=0.306,
                saturation_point_water_concentration=0.5,
                saturated_hydraulic_conductivity=9.17,
                pH=6.5,
                clay_fraction=0.2727,
                temperature=14.50797297,
                bulk_density=1.42,
                organic_carbon_fraction=0.012,
                initial_soil_ammonium_concentration=1,
                initial_soil_nitrate_concentration=1,
                initial_labile_inorganic_phosphorus_concentration=2.7,
                ammonium_volatilization_cation_exchange_factor=0.15,
                soil_water_concentration=0.3,
                sand_fraction=0.1364,
                silt_fraction=0.5909,
                rock_fraction=0.0,
                residue=0.0,
            ),
        ),
    ],
)
def test_setup_soil_layer(
    field_size: float, top: float, residue: float, config: dict[str, float | int], expected: LayerData
) -> None:
    """Tests that LayerData instances are configured correctly with a given specification."""
    actual = FieldManager._setup_soil_layer(field_size, top, residue, config)
    assert actual == expected


@pytest.mark.parametrize(
    "config",
    [
        {},
        {
            "wilting_point": 0.1,
            "field_capacity": 0.29,
            "saturation": 0.58,
            "K_sat": 20.0,
            "clay": 22.5,
            "initial_temperature": 0.0,
            "bulk_density": 1.34,
            "org_C_percent": 0.012,
            "NH4": 1,
            "labile_P": 23.7,
            "active_mineral_rate": 0.0003,
            "volatile_exchange_factor": 0.15,
            "soil_water_percent": 0.3,
            "OM_percent": 0.019,
        },
    ],
)
def test_setup_soil_layer_error(config: dict[str, float | int]) -> None:
    """Tests that errors are thrown correctly when not enough information is provided to create one."""
    with pytest.raises(ValueError) as e:
        FieldManager._setup_soil_layer(1.0, 0.0, 0.0, config)
    assert str(e.value) == "Bottom depth is required for each soil layer."


@pytest.mark.parametrize(
    "soil_configuration",
    [
        {
            "second_moisture_condition_parameter": 85.00,
            "average_subbasin_slope": 0.02,
            "slope_length": 3,
            "manning_roughness_coefficient": 0.4,
            "support_practice_factor": 0.8,
            "albedo": 0.16,
            "soil_evaporation_compensation_coefficient": 0.95,
            "initial_residue": 0,
            "humus_mineralization_rate_factor": 0.0003,
            "denitrification_rate_coefficient": 0.01,
            "denitrification_threshold_water_content": 1.3,
            "residue_fresh_organic_mineralization_rate": 0.05,
            "soil_layers": [
                {
                    "bottom_depth": 279.4,
                    "soil_water_concentration": 0.3,
                    "wilting_point_water_concentration": 0.23,
                    "field_capacity_water_concentration": 0.29,
                    "saturation_point_water_concentration": 0.58,
                    "saturated_hydraulic_conductivity": 9.17,
                    "initial_temperature": 15.77575,
                    "bulk_density": 1.34,
                    "organic_carbon_fraction": 0.012,
                    "clay_fraction": 0.2195,
                    "silt_fraction": 0.6342,
                    "sand_fraction": 0.1463,
                    "rock_fraction": 0.0,
                    "initial_labile_inorganic_phosphorus_concentration": 2.7,
                    "initial_fresh_organic_phosphorus_concentration": 0.0,
                    "initial_soil_nitrate_concentration": 1,
                    "initial_soil_ammonium_concentration": 1,
                    "humus_mineralization_rate_factor": 0.0003,
                    "ammonium_volatilization_cation_exchange_factor": 0.15,
                    "denitrification_rate_coefficient": 1.4,
                    "denitrification_threshold_water_content": 1.1,
                    "residue_fresh_organic_mineralization_rate": 0.05,
                    "OM_percent": 0.04,
                },
                {
                    "bottom_depth": 1041.4,
                    "soil_water_concentration": 0.3,
                    "wilting_point_water_concentration": 0.163,
                    "field_capacity_water_concentration": 0.306,
                    "saturation_point_water_concentration": 0.5,
                    "saturated_hydraulic_conductivity": 9.17,
                    "initial_temperature": 14.50797297,
                    "bulk_density": 1.42,
                    "organic_carbon_fraction": 0.012,
                    "clay_fraction": 0.2727,
                    "silt_fraction": 0.5909,
                    "sand_fraction": 0.1364,
                    "rock_fraction": 0.0,
                    "initial_labile_inorganic_phosphorus_concentration": 2.7,
                    "initial_fresh_organic_phosphorus_concentration": 0.0,
                    "initial_soil_nitrate_concentration": 1,
                    "initial_soil_ammonium_concentration": 1,
                    "humus_mineralization_rate_factor": 0.0003,
                    "ammonium_volatilization_cation_exchange_factor": 0.15,
                    "denitrification_rate_coefficient": 1.4,
                    "denitrification_threshold_water_content": 1.1,
                    "residue_fresh_organic_mineralization_rate": 0.05,
                    "OM_percent": 0.006,
                },
                {
                    "bottom_depth": 1168.4,
                    "soil_water_concentration": 0.3,
                    "wilting_point_water_concentration": 0.151,
                    "field_capacity_water_concentration": 0.298,
                    "saturation_point_water_concentration": 0.5,
                    "saturated_hydraulic_conductivity": 23.29,
                    "initial_temperature": 13.38623,
                    "bulk_density": 1.6,
                    "organic_carbon_fraction": 0.012,
                    "clay_fraction": 0.2233,
                    "silt_fraction": 0.6311,
                    "sand_fraction": 0.1456,
                    "rock_fraction": 0.0,
                    "initial_labile_inorganic_phosphorus_concentration": 2.7,
                    "initial_fresh_organic_phosphorus_concentration": 0.0,
                    "initial_soil_nitrate_concentration": 1,
                    "initial_soil_ammonium_concentration": 1,
                    "humus_mineralization_rate_factor": 0.0003,
                    "ammonium_volatilization_cation_exchange_factor": 0.15,
                    "denitrification_rate_coefficient": 1.4,
                    "denitrification_threshold_water_content": 1.1,
                    "residue_fresh_organic_mineralization_rate": 0.05,
                    "OM_percent": 0.0025,
                },
                {
                    "bottom_depth": 2006.6,
                    "soil_water_concentration": 0.3,
                    "wilting_point_water_concentration": 0.132,
                    "field_capacity_water_concentration": 0.211,
                    "saturation_point_water_concentration": 0.5,
                    "saturated_hydraulic_conductivity": 23.29,
                    "initial_temperature": 13.38623,
                    "bulk_density": 1.5,
                    "organic_carbon_fraction": 0.012,
                    "clay_fraction": 0.1304,
                    "silt_fraction": 0.7066,
                    "sand_fraction": 0.1630,
                    "rock_fraction": 0.0,
                    "initial_labile_inorganic_phosphorus_concentration": 2.7,
                    "initial_fresh_organic_phosphorus_concentration": 0.0,
                    "initial_soil_nitrate_concentration": 1,
                    "initial_soil_ammonium_concentration": 1,
                    "humus_mineralization_rate_factor": 0.0003,
                    "ammonium_volatilization_cation_exchange_factor": 0.15,
                    "denitrification_rate_coefficient": 1.4,
                    "denitrification_threshold_water_content": 1.1,
                    "residue_fresh_organic_mineralization_rate": 0.05,
                    "OM_percent": 0.0025,
                },
            ],
        },
        {
            "second_moisture_condition_parameter": 85.00,
            "average_subbasin_slope": 0.02,
            "slope_length": 3,
            "manning_roughness_coefficient": 0.4,
            "support_practice_factor": 0.08,
            "albedo": 0.16,
            "soil_evaporation_compensation_coefficient": 0.95,
            "initial_residue": 0,
            "humus_mineralization_rate_factor": 0.0003,
            "denitrification_rate_coefficient": 0.01,
            "denitrification_threshold_water_content": 1.3,
            "residue_fresh_organic_mineralization_rate": 0.05,
            "soil_layers": [
                {
                    "bottom_depth": 150,
                    "soil_water_concentration": 0.3,
                    "wilting_point_water_concentration": 0.1,
                    "field_capacity_water_concentration": 0.30,
                    "saturation_point_water_concentration": 0.5,
                    "saturated_hydraulic_conductivity": 20,
                    "initial_temperature": 15.77575,
                    "bulk_density": 1.3,
                    "organic_carbon_fraction": 0.012,
                    "clay_fraction": 0.20,
                    "silt_fraction": 0.65,
                    "sand_fraction": 0.15,
                    "rock_fraction": 0.0,
                    "initial_labile_inorganic_phosphorus_concentration": 23.7,
                    "initial_soil_nitrate_concentration": 0.0,
                    "initial_soil_ammonium_concentration": 1,
                    "humus_mineralization_rate_factor": 0.0003,
                    "ammonium_volatilization_cation_exchange_factor": 0.15,
                    "denitrification_rate_coefficient": 1.4,
                    "denitrification_threshold_water_content": 1.1,
                    "residue_fresh_organic_mineralization_rate": 0.05,
                    "OM_percent": 0.019,
                },
                {
                    "bottom_depth": 300,
                    "soil_water_concentration": 0.3,
                    "wilting_point_water_concentration": 0.1,
                    "field_capacity_water_concentration": 0.3,
                    "saturation_point_water_concentration": 0.5,
                    "saturated_hydraulic_conductivity": 20,
                    "initial_temperature": 14.50797297,
                    "bulk_density": 1.3,
                    "organic_carbon_fraction": 0.012,
                    "clay_fraction": 0.20,
                    "silt_fraction": 0.65,
                    "sand_fraction": 0.15,
                    "rock_fraction": 0.0,
                    "initial_labile_inorganic_phosphorus_concentration": 10,
                    "initial_soil_nitrate_concentration": 0.0,
                    "initial_soil_ammonium_concentration": 1,
                    "humus_mineralization_rate_factor": 0.0003,
                    "ammonium_volatilization_cation_exchange_factor": 0.15,
                    "denitrification_rate_coefficient": 1.4,
                    "denitrification_threshold_water_content": 1.1,
                    "residue_fresh_organic_mineralization_rate": 0.05,
                    "OM_percent": 0.019,
                },
                {
                    "bottom_depth": 450,
                    "soil_water_concentration": 0.3,
                    "wilting_point_water_concentration": 0.1,
                    "field_capacity_water_concentration": 0.30,
                    "saturation_point_water_concentration": 0.5,
                    "saturated_hydraulic_conductivity": 20,
                    "initial_temperature": 13.38623,
                    "bulk_density": 1.3,
                    "organic_carbon_fraction": 0.012,
                    "clay_fraction": 0.20,
                    "silt_fraction": 0.65,
                    "sand_fraction": 0.15,
                    "rock_fraction": 0.0,
                    "initial_labile_inorganic_phosphorus_concentration": 10,
                    "initial_soil_nitrate_concentration": 0.0,
                    "initial_soil_ammonium_concentration": 1,
                    "humus_mineralization_rate_factor": 0.0003,
                    "ammonium_volatilization_cation_exchange_factor": 0.15,
                    "denitrification_rate_coefficient": 1.4,
                    "denitrification_threshold_water_content": 1.1,
                    "residue_fresh_organic_mineralization_rate": 0.05,
                    "OM_percent": 0.019,
                },
            ],
        },
    ],
)
def test_setup_soil(
    soil_configuration: dict[str, float | int | list[dict[str, Any]]],
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Tests that Soil profiles are setup correctly with data from the InputManager."""
    mock_input_manager.get_data = mock.MagicMock(return_value=soil_configuration)
    actual_soil = FieldManager._setup_soil("test_soil_setup", 1.0)
    assert actual_soil.data.second_moisture_condition_parameter == soil_configuration.get(
        "second_moisture_condition_parameter"
    )
    assert actual_soil.data.average_subbasin_slope == soil_configuration.get("average_subbasin_slope")
    assert actual_soil.data.slope_length == soil_configuration.get("slope_length")
    assert actual_soil.data.manning == soil_configuration.get("manning_roughness_coefficient")
    assert actual_soil.data.albedo == soil_configuration.get("albedo")
    assert actual_soil.data.denitrification_threshold_water_content == soil_configuration.get(
        "denitrification_threshold_water_content"
    )
    assert len(actual_soil.data.soil_layers) == len(soil_configuration.get("soil_layers")) + 1
    mock_input_manager.get_data.assert_called_once_with("test_soil_setup")

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]


@pytest.mark.parametrize(
    "soil_configuration,error_message",
    [
        (
            {
                "second_moisture_condition_parameter": 85.00,
                "average_subbasin_slope": 0.02,
                "slope_length": 3,
                "manning_roughness_coefficient": 0.4,
                "support_practice_factor": 0.08,
                "albedo": 0.16,
                "soil_evaporation_compensation_coefficient": 0.95,
                "initial_residue": 0,
            },
            "Configuration for soil layers must be provided.",
        ),
        (
            {
                "second_moisture_condition_parameter": 85.00,
                "average_subbasin_slope": 0.02,
                "slope_length": 3,
                "manning_roughness_coefficient": 0.4,
                "support_practice_factor": 0.08,
                "albedo": 0.16,
                "soil_evaporation_compensation_coefficient": 0.95,
                "initial_residue": 0,
                "soil_layers": None,
            },
            "Configuration for soil layers must be provided.",
        ),
    ],
)
def test_setup_soil_error(
    soil_configuration: dict[str, float | int] | dict[str, float | int | None],
    error_message: str,
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Any],
) -> None:
    """Tests that errors are raised correctly when invalid soil configurations are passed."""
    mock_input_manager.get_data = mock.MagicMock(return_value=soil_configuration)

    with pytest.raises(ValueError) as e:
        FieldManager._setup_soil("soil_config", 1.3)
    assert str(e.value) == error_message

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]


@pytest.mark.parametrize(
    "field_name,field_config",
    [
        (
            "field_1",
            {
                "soil_specification": "soil",
                "crop_specification": "crop",
                "fertilizer_management_specification": "fertilizer_schedule",
                "manure_management_specification": "manure_schedule",
                "tillage_management_specification": "tillage_schedule",
                "field_size": 1.0,
                "absolute_latitude": 43.304346,
                "longitude": None,
                "minimum_daylength": 9.0,
                "seasonal_high_water_table": False,
                "watering_amount_in_liters": 0.0,
                "watering_interval": 0,
                "supplement_manure_nutrient_deficiencies": True,
                "simulate_water_stress": True,
                "simulate_temp_stress": False,
                "simulate_nitrogen_stress": True,
                "simulate_phosphorus_stress": False,
            },
        ),
        (
            "field_2",
            {
                "soil_specification": "soil",
                "crop_specification": "crop",
                "fertilizer_management_specification": "fertilizer_schedule_1",
                "manure_management_specification": "manure_schedule_1",
                "tillage_management_specification": "tillage_schedule_1",
                "field_size": 1.0,
                "absolute_latitude": 43.5,
                "longitude": -89.4,
                "minimum_daylength": 9.0,
                "seasonal_high_water_table": False,
                "watering_amount_in_liters": 500.0,
                "watering_interval": 3,
                "supplement_manure_nutrient_deficiencies": False,
                "simulate_water_stress": True,
                "simulate_temp_stress": False,
                "simulate_nitrogen_stress": True,
                "simulate_phosphorus_stress": False,
            },
        ),
    ],
)
def test_setup_field(
    field_name: str,
    field_config: dict[str, str | float | bool | int | None] | dict[str, str | float | bool | int],
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
    mocker: MockerFixture,
) -> None:
    """Tests that a Field instance is correctly initialized with a given input configuration."""
    mock_fertilizer_events = [MagicMock(FertilizerEvent)]
    mock_manure_events = [MagicMock(ManureEvent)]
    mock_tillage_events = [MagicMock(TillageEvent)]
    mock_planting_events = [MagicMock(PlantingEvent)]
    mock_harvest_events = [MagicMock(HarvestEvent)]

    dummy_available_fertilizer_mixes = {"A": {"N": 0.0, "P": 1.1, "K": 2.2, "ammonium_fraction": 0.0}}
    crop_configs = ["alfalfa", "corn", "oats"]

    mocked_soil_profile = MagicMock(Soil)
    mocked_soil_data = MagicMock(SoilData)
    mocked_soil_profile.data = mocked_soil_data

    mock_input_manager.get_data = mock.MagicMock(return_value=field_config)

    mock_setup_soil_data = mocker.patch(
        "RUFAS.biophysical.field.manager.field_manager.FieldManager._setup_soil", return_value=mocked_soil_profile
    )
    mock_setup_fertilizer_events = mocker.patch(
        "RUFAS.biophysical.field.manager.field_manager.FieldManager._setup_fertilizer_events",
        return_value=(dummy_available_fertilizer_mixes, mock_fertilizer_events),
    )
    mock_setup_manure_events = mocker.patch(
        "RUFAS.biophysical.field.manager.field_manager.FieldManager._setup_manure_events",
        return_value=mock_manure_events,
    )
    mock_setup_tillage_events = mocker.patch(
        "RUFAS.biophysical.field.manager.field_manager.FieldManager._setup_tillage_events",
        return_value=mock_tillage_events,
    )
    mock_setup_crop_data = mocker.patch(
        "RUFAS.biophysical.field.manager.field_manager.FieldManager._setup_crop_events",
        return_value=(mock_planting_events, mock_harvest_events),
    )

    new_field = FieldManager._setup_field(field_name, crop_configs)

    assert new_field.field_data.name == field_name
    assert new_field.field_data.field_size == field_config.get("field_size")
    assert new_field.field_data.absolute_latitude == field_config.get("absolute_latitude")
    assert new_field.field_data.longitude == field_config.get("longitude")
    assert new_field.field_data.minimum_daylength == field_config.get("minimum_daylength")
    assert new_field.field_data.watering_amount_in_liters == field_config.get("watering_amount_in_liters")
    assert new_field.field_data.watering_interval == field_config.get("watering_interval")
    assert new_field.field_data.simulate_water_stress == field_config.get("simulate_water_stress")
    assert new_field.field_data.simulate_temp_stress == field_config.get("simulate_temp_stress")
    assert new_field.field_data.simulate_nitrogen_stress == field_config.get("simulate_nitrogen_stress")
    assert new_field.field_data.simulate_phosphorus_stress == field_config.get("simulate_phosphorus_stress")

    assert new_field.soil == mocked_soil_profile
    assert new_field.available_fertilizer_mixes == {
        "A": {"N": 0.0, "P": 1.1, "K": 2.2, "ammonium_fraction": 0.0},
        "100_0_0": {"N": 1.0, "P": 0.0, "K": 0.0, "ammonium_fraction": 0.0},
        "26_4_24": {"N": 0.26, "P": 0.04, "K": 0.24, "ammonium_fraction": 0.0},
    }

    mock_input_manager.get_data.assert_called_once_with(field_name)
    mock_setup_fertilizer_events.assert_called_once_with(field_config.get("fertilizer_management_specification"))
    mock_setup_manure_events.assert_called_once_with(field_config.get("manure_management_specification"))
    mock_setup_tillage_events.assert_called_once_with(field_config.get("tillage_management_specification"))
    mock_setup_crop_data.assert_called_once_with(field_config.get("crop_specification"), crop_configs)
    mock_setup_soil_data.assert_called_once_with(
        soil_configuration=field_config.get("soil_specification"), field_size=field_config.get("field_size")
    )

    mock_input_manager.get_data = input_manager_original_method_states["get_data"]


@pytest.mark.parametrize(
    "field_name,field_config",
    [
        (
            "field_1",
            {
                "soil_specification": "soil",
                "crop_specification": "crop",
                "fertilizer_management_specification": "fertilizer_schedule",
                "manure_management_specification": "manure_schedule",
                "tillage_management_specification": "tillage_schedule",
                "field_size": 1.0,
                "absolute_latitude": 43.304346,
                "longitude": None,
                "minimum_daylength": 9.0,
                "seasonal_high_water_table": False,
                "watering_amount_in_liters": 0.0,
                "watering_interval": 0,
                "supplement_manure_nutrient_deficiencies": True,
                "simulate_water_stress": True,
                "simulate_temp_stress": False,
                "simulate_nitrogen_stress": True,
                "simulate_phosphorus_stress": False,
            },
        ),
        (
            "field_2",
            {
                "soil_specification": "soil",
                "crop_specification": "crop",
                "fertilizer_management_specification": "fertilizer_schedule_1",
                "manure_management_specification": "manure_schedule_1",
                "tillage_management_specification": "tillage_schedule_1",
                "field_size": 1.0,
                "absolute_latitude": 43.5,
                "longitude": -89.4,
                "minimum_daylength": 9.0,
                "seasonal_high_water_table": False,
                "watering_amount_in_liters": 500.0,
                "watering_interval": 3,
                "supplement_manure_nutrient_deficiencies": False,
                "simulate_water_stress": True,
                "simulate_temp_stress": False,
                "simulate_nitrogen_stress": True,
                "simulate_phosphorus_stress": False,
            },
        ),
    ],
)
def test_setup_field_data(
    field_name: str, field_config: dict[str, str | float | bool | int | None] | dict[str, str | float | bool | int]
) -> None:
    result = FieldManager._setup_field_data(field_name, field_config)
    assert result.name == field_name
    assert result.field_size == field_config.get("field_size")
    assert result.absolute_latitude == field_config.get("absolute_latitude")
    assert result.longitude == field_config.get("longitude")
    assert result.minimum_daylength == field_config.get("minimum_daylength")
    assert result.seasonal_high_water_table == field_config.get("seasonal_high_water_table")
    assert result.watering_amount_in_liters == field_config.get("watering_amount_in_liters")
    assert result.watering_interval == field_config.get("watering_interval")
    assert result.simulate_water_stress == field_config.get("simulate_water_stress")
    assert result.simulate_temp_stress == field_config.get("simulate_temp_stress")
    assert result.simulate_nitrogen_stress == field_config.get("simulate_nitrogen_stress")
    assert result.simulate_phosphorus_stress == field_config.get("simulate_phosphorus_stress")


def test_setup_crop_date(mocker: MockerFixture) -> None:
    dummy_crop_schedule = MagicMock(CropSchedule)
    dummy_planting_events = [MagicMock(PlantingEvent), MagicMock(PlantingEvent)]
    dummy_harvest_events = [MagicMock(HarvestEvent), MagicMock(HarvestEvent)]

    crop_configs = ["alfalfa", "corn", "oats"]
    mocker.patch.object(CropDataFactory, "setup_crop_configurations", return_value=None)
    mocker.patch.object(CropDataFactory, "get_available_crop_configurations", return_value=crop_configs)
    mock_generate_planting_events = mocker.patch.object(
        dummy_crop_schedule, "generate_planting_events", return_value=dummy_planting_events
    )
    mock_generate_harvest_events = mocker.patch.object(
        dummy_crop_schedule, "generate_harvest_events", return_value=dummy_harvest_events
    )
    mock_setup_crop_schedule = mocker.patch(
        "RUFAS.biophysical.field.manager.field_manager.FieldManager._setup_crop_schedules",
        return_value=[dummy_crop_schedule],
    )

    result_planting, result_harvest = FieldManager._setup_crop_events("crop_rotation_config", crop_configs)

    assert result_planting == dummy_planting_events
    assert result_harvest == dummy_harvest_events

    mock_setup_crop_schedule.assert_called_once_with("crop_rotation_config", crop_configs)
    mock_generate_planting_events.assert_called_once()
    mock_generate_harvest_events.assert_called_once()


def test_check_manure_schedules(mocker: MockerFixture) -> None:
    """Tests that check_manure_schedules calls _check_manure_application_schedule and returns the correct results."""
    # Arrange
    field = MagicMock(Field)
    time = MagicMock(RufasTime)
    expected_manure_requests = [
        ManureEventNutrientRequest(
            field_name="field1",
            event=MagicMock(),
            nutrient_request=MagicMock(),
        ),
        ManureEventNutrientRequest(
            field_name="field2",
            event=MagicMock(),
            nutrient_request=MagicMock(),
        ),
    ]
    field.check_manure_application_schedule.return_value = expected_manure_requests
    mocker.patch.object(CropDataFactory, "setup_crop_configurations", return_value=None)
    mocker.patch.object(CropDataFactory, "get_available_crop_configurations", return_value=["alfalfa", "corn", "oats"])
    field_manager = FieldManager()

    # Act
    manure_requests = field_manager.check_manure_schedules(field, time)

    # Assert
    field.check_manure_application_schedule.assert_called_once_with(time)
    assert manure_requests == expected_manure_requests
